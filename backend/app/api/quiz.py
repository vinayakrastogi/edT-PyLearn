import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.content_repository.base import ContentRepository
from app.content_repository.loader import get_content_repo
from app.core.deps import get_db, get_current_user, get_tz_offset
from app.core.ratelimit import limit_quiz_submits
from app.models.user import User
from app.models.progress import QuizAttempt
from app.schemas.quiz import QuizResponse, QuizSubmitRequest, QuizSubmitResponse, QuizAttemptRecord
from app.services import gamification
from app.services.grading import grade_quiz

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.get("/{module_id}", response_model=QuizResponse)
async def get_quiz(
    module_id: str,
    repo: ContentRepository = Depends(get_content_repo),
    _: User = Depends(get_current_user),
):
    return await repo.get_quiz(module_id)


@router.post("/{module_id}/submit", response_model=QuizSubmitResponse)
async def submit_quiz(
    module_id: str,
    payload: QuizSubmitRequest,
    repo: ContentRepository = Depends(get_content_repo),
    db: Session = Depends(get_db),
    current_user: User = Depends(limit_quiz_submits),
    tz_offset: int = Depends(get_tz_offset),
):
    user_id = current_user.id

    # Validate before anything is saved: only the module's own id is accepted. A case-insensitive
    # filesystem would also resolve another spelling, and that must not fill the progress tables
    # (the badge statistics would count every spelling as another module).
    detail = await repo.get_module(module_id)
    if detail.id != module_id:
        raise HTTPException(status_code=404, detail=f"Module '{module_id}' not found")
    quiz_file_path = repo._module_path(module_id) / "quiz.json"  # type: ignore[attr-defined]
    if not quiz_file_path.exists():
        raise HTTPException(status_code=404, detail=f"Module '{module_id}' has no quiz")

    # Load full quiz with answers (from content file)
    with open(quiz_file_path) as f:
        quiz_data = json.load(f)

    quiz_id = quiz_data.get("id", f"{module_id}-quiz")
    questions = quiz_data.get("questions", [])

    result = grade_quiz(questions, payload.answers)

    # Persist attempt
    attempt = QuizAttempt(
        user_id=user_id,
        module_id=module_id,
        quiz_id=quiz_id,
        answers=payload.answers,
        score=result["score"],
        max_score=result["max_score"],
        per_question_results=result["per_question_results"],
    )
    db.add(attempt)
    db.commit()

    # Rewards are best effort: the graded result and the saved attempt must never depend on gamification.
    rewards = None
    try:
        rewards = gamification.record_quiz_attempt(
            db, current_user, module_id, attempt.id, result["percentage"], detail=detail, tz_offset=tz_offset,
        )
    except Exception:
        logger.exception("Gamification failed for a quiz submit (user=%s, module=%s)", user_id, module_id)
        db.rollback()

    return QuizSubmitResponse(**result, rewards=rewards)


@router.get("/{module_id}/attempts", response_model=List[QuizAttemptRecord])
def get_quiz_attempts(
    module_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempts = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.module_id == module_id,
        )
        .order_by(QuizAttempt.attempted_at.desc())
        .all()
    )
    return [
        QuizAttemptRecord(
            id=a.id,
            quiz_id=a.quiz_id,
            score=a.score,
            max_score=a.max_score,
            percentage=round(a.score / a.max_score * 100, 1) if a.max_score else 0,
            per_question_results=a.per_question_results,
            attempted_at=a.attempted_at,
        )
        for a in attempts
    ]

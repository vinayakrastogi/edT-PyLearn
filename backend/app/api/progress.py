import logging
from collections import defaultdict
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.content_repository.base import ContentRepository
from app.content_repository.loader import get_content_repo
from app.core.deps import get_db, get_current_user, get_tz_offset
from app.models.user import User
from app.models.progress import LessonProgress, QuizAttempt, CodeSubmission, SubmissionStatus
from app.schemas.module import ModuleDetail
from app.schemas.progress import LessonViewRequest, LessonProgressRecord, ModuleProgressSummary, DashboardResponse, TrackAccessRequest, ConceptMastery
from app.services import gamification

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/progress", tags=["progress"])


def _module_summary(db: Session, user_id: int, module_id: str, detail: ModuleDetail) -> ModuleProgressSummary:
    """One learner's progress through one module (shared by the dashboard and GET /{module_id})."""
    total_docs = len(detail.docs)
    total_problems = len(detail.problems)

    viewed_docs = [
        lesson_id
        for (lesson_id,) in db.query(LessonProgress.lesson_id).filter(
            LessonProgress.user_id == user_id,
            LessonProgress.module_id == module_id,
            LessonProgress.is_complete.is_(True),
        )
    ]
    docs_read = len(viewed_docs)

    quiz_attempts_rows = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.module_id == module_id,
        )
        .all()
    )
    quiz_attempts = len(quiz_attempts_rows)
    best_quiz_score: Optional[float] = None
    if quiz_attempts_rows:
        best = max(quiz_attempts_rows, key=lambda a: a.score / a.max_score if a.max_score else 0)
        best_quiz_score = round(best.score / best.max_score * 100, 1) if best.max_score else 0

    # Plain DISTINCT (not PostgreSQL's DISTINCT ON): same rows, ordered by problem id, and it also runs on SQLite.
    passed_problems = [
        problem_id
        for (problem_id,) in db.query(CodeSubmission.problem_id)
        .filter(
            CodeSubmission.user_id == user_id,
            CodeSubmission.module_id == module_id,
            CodeSubmission.status == SubmissionStatus.PASS,
        )
        .distinct()
        .order_by(CodeSubmission.problem_id)
    ]
    problems_solved = len(passed_problems)

    total = total_docs + total_problems + (1 if detail.quiz_id else 0)
    done = docs_read + problems_solved + (1 if best_quiz_score is not None and best_quiz_score == 100 else 0)
    completion = round((done / total * 100) if total else 0, 1)

    return ModuleProgressSummary(
        module_id=module_id,
        total_docs=total_docs,
        docs_read=docs_read,
        quiz_attempts=quiz_attempts,
        best_quiz_score=best_quiz_score,
        total_problems=total_problems,
        problems_solved=problems_solved,
        completion_percentage=completion,
        viewed_docs=viewed_docs,
        passed_problems=passed_problems,
    )


def _live_streak(db: Session, user: User, tz_offset: int) -> int:
    """
    The learner's current streak. The gamification service owns it and already reports a lapsed
    streak as 0 (a streak kept alive by a banked freeze still counts). A gamification failure must
    not break the dashboard, so it falls back to 0 rather than showing a possibly dead streak.
    """
    user_id = user.id
    try:
        return gamification.get_summary(db, user, tz_offset=tz_offset).streak.count
    except Exception:
        logger.exception("Gamification failed to read the streak (user=%s)", user_id)
        db.rollback()
        return 0


@router.post("/track-access")
def track_access(
    payload: TrackAccessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only remembers where the learner was: streaks are owned by the gamification service and are
    # driven by real learning activity, not by page views.
    current_user.last_accessed_path = payload.path
    current_user.last_accessed_title = payload.title
    db.commit()
    return {"status": "ok"}


@router.post("/lesson-view", response_model=LessonProgressRecord)
async def mark_lesson_viewed(
    payload: LessonViewRequest,
    repo: ContentRepository = Depends(get_content_repo),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tz_offset: int = Depends(get_tz_offset),
):
    user_id = current_user.id

    # Only real lessons can be recorded: made-up ids must neither fill the progress tables nor earn XP.
    # An unknown module is a 404 (a malformed module id a 400) straight from the repository. Another
    # spelling of a module id (a case-insensitive filesystem still resolves it) is not a module either.
    detail = await repo.get_module(payload.module_id)
    if detail.id != payload.module_id or not any(doc.id == payload.lesson_id for doc in detail.docs):
        raise HTTPException(
            status_code=404,
            detail=f"Lesson '{payload.lesson_id}' not found in module '{payload.module_id}'",
        )

    progress = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.user_id == user_id,
            LessonProgress.module_id == payload.module_id,
            LessonProgress.lesson_id == payload.lesson_id,
        )
        .first()
    )
    if progress is None:
        progress = LessonProgress(
            user_id=user_id,
            module_id=payload.module_id,
            lesson_id=payload.lesson_id,
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    # Read the row now: the gamification service commits (which expires it) or rolls back below.
    lesson_id, viewed_at, is_complete = progress.lesson_id, progress.viewed_at, progress.is_complete

    # Every view counts as streak activity, re-reads included; the XP ledger pays a lesson only once.
    # Rewards are best effort: the saved progress must never depend on gamification.
    rewards = None
    try:
        rewards = gamification.record_lesson_read(
            db, current_user, payload.module_id, payload.lesson_id, detail=detail, tz_offset=tz_offset,
        )
    except Exception:
        logger.exception(
            "Gamification failed for a lesson view (user=%s, module=%s, lesson=%s)",
            user_id, payload.module_id, payload.lesson_id,
        )
        db.rollback()

    return LessonProgressRecord(lesson_id=lesson_id, viewed_at=viewed_at, is_complete=is_complete, rewards=rewards)


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    repo: ContentRepository = Depends(get_content_repo),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tz_offset: int = Depends(get_tz_offset),
):
    modules = await repo.list_modules()
    summaries = []
    details: Dict[str, ModuleDetail] = {}
    for mod in modules:
        try:
            detail = await repo.get_module(mod.id)
        except Exception as e:
            # Skip modules that can't be loaded (missing files, corrupt data, etc.)
            logger.warning("Could not load module %s: %s", mod.id, e)
            continue
        details[mod.id] = detail
        summaries.append(_module_summary(db, current_user.id, mod.id, detail))

    # Concept Mastery Aggregation
    mastery_counts = defaultdict(lambda: {"correct": 0, "total": 0})

    # 1. Quizzes
    all_quizzes = db.query(QuizAttempt).filter(QuizAttempt.user_id == current_user.id).all()
    for att in all_quizzes:
        for qr in att.per_question_results:
            for concept in qr.get("concepts", []):
                mastery_counts[concept]["total"] += 1
                if qr.get("correct"):
                    mastery_counts[concept]["correct"] += 1

    # 2. Coding Problems
    all_subs = db.query(CodeSubmission).filter(CodeSubmission.user_id == current_user.id).all()
    for sub in all_subs:
        detail = details.get(sub.module_id)  # loaded above: no need to read the module again per submission
        if detail is None: continue
        prob = next((p for p in detail.problems if p.get("id") == sub.problem_id), None)
        if not prob: continue

        for concept in prob.get("concepts", []):
            mastery_counts[concept]["total"] += 1
            if sub.status == SubmissionStatus.PASS:
                mastery_counts[concept]["correct"] += 1

    mastery_stats = []
    for concept, counts in mastery_counts.items():
        if counts["total"] > 0:
            percentage = round(counts["correct"] / counts["total"] * 100, 1)
            mastery_stats.append(ConceptMastery(
                concept=concept,
                correct=counts["correct"],
                total=counts["total"],
                percentage=percentage
            ))

    mastery_stats.sort(key=lambda x: x.percentage, reverse=True)

    return DashboardResponse(
        modules=summaries,
        streak_count=_live_streak(db, current_user, tz_offset),
        mastery_stats=mastery_stats
    )


@router.get("/{module_id}", response_model=ModuleProgressSummary)
async def module_progress(
    module_id: str,
    repo: ContentRepository = Depends(get_content_repo),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    detail = await repo.get_module(module_id)
    return _module_summary(db, current_user.id, module_id, detail)

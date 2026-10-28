import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.content_repository.base import ContentRepository
from app.content_repository.loader import get_content_repo
from app.core.deps import get_db, get_current_user, get_tz_offset
from app.core.ratelimit import limit_code_submits
from app.models.user import User
from app.models.progress import CodeSubmission, SubmissionStatus
from app.schemas.problem import ProblemDetail, CodeSubmitRequest, CodeSubmitResponse, SubmissionRecord
from app.services import gamification
from app.services.grading import grade_submission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/problems", tags=["problems"])


@router.get("/{module_id}/{problem_id}", response_model=ProblemDetail)
async def get_problem(
    module_id: str,
    problem_id: str,
    repo: ContentRepository = Depends(get_content_repo),
    _: User = Depends(get_current_user),
):
    return await repo.get_problem(module_id, problem_id)


@router.post("/{module_id}/{problem_id}/submit", response_model=CodeSubmitResponse)
async def submit_code(
    module_id: str,
    problem_id: str,
    payload: CodeSubmitRequest,
    repo: ContentRepository = Depends(get_content_repo),
    db: Session = Depends(get_db),
    current_user: User = Depends(limit_code_submits),
    tz_offset: int = Depends(get_tz_offset),
):
    user_id = current_user.id

    # Validate before grading or saving anything: the module and problem ids must be spelled exactly
    # as the content spells them (a case-insensitive filesystem would resolve other spellings too,
    # and each spelling would then count as another problem in the badge statistics).
    detail = await repo.get_module(module_id)
    if detail.id != module_id or not any(isinstance(p, dict) and p.get("id") == problem_id for p in detail.problems):
        raise HTTPException(status_code=404, detail=f"Problem '{problem_id}' not found in module '{module_id}'")
    problem = await repo.get_problem(module_id, problem_id)

    all_tests = await repo.get_hidden_tests(module_id, problem_id)
    grading = await run_in_threadpool(grade_submission, payload.code, all_tests)

    # Earlier submissions of this problem, counted before the new one is saved: 0 means this is the
    # learner's very first try (that is what the first-try bonus rewards).
    prior_submissions = (
        db.query(func.count(CodeSubmission.id))
        .filter(
            CodeSubmission.user_id == user_id,
            CodeSubmission.module_id == module_id,
            CodeSubmission.problem_id == problem_id,
        )
        .scalar()
    ) or 0

    submission = CodeSubmission(
        user_id=user_id,
        module_id=module_id,
        problem_id=problem_id,
        code=payload.code,
        status=SubmissionStatus(grading["status"]),
        test_results=grading["test_results"],
        stdout=grading["stdout"],
        stderr=grading["stderr"],
    )
    db.add(submission)
    db.commit()

    # Rewards are best effort: grading and the saved submission must never depend on gamification.
    rewards = None
    try:
        rewards = gamification.record_problem_submission(
            db, current_user, module_id, problem_id,
            difficulty=problem.difficulty,
            passed=grading["status"] == SubmissionStatus.PASS.value,
            prior_submissions=prior_submissions,
            detail=detail,
            tz_offset=tz_offset,
        )
    except Exception:
        logger.exception(
            "Gamification failed for a code submit (user=%s, module=%s, problem=%s)",
            user_id, module_id, problem_id,
        )
        db.rollback()

    return CodeSubmitResponse(**grading, rewards=rewards)


@router.get("/{module_id}/{problem_id}/submissions", response_model=List[SubmissionRecord])
def get_submissions(
    module_id: str,
    problem_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    submissions = (
        db.query(CodeSubmission)
        .filter(
            CodeSubmission.user_id == current_user.id,
            CodeSubmission.module_id == module_id,
            CodeSubmission.problem_id == problem_id,
        )
        .order_by(CodeSubmission.submitted_at.desc())
        .limit(20)
        .all()
    )
    return submissions

import time
from collections import defaultdict, deque
from typing import Deque, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User
from app.services.execution import run_python_code

router = APIRouter(prefix="/api/run", tags=["run"])

_recent_runs: Dict[int, Deque[float]] = defaultdict(deque)


class RunRequest(BaseModel):
    code: str = Field(max_length=20_000)
    stdin: str = Field(default="", max_length=2_000)


class RunResponse(BaseModel):
    stdout: str
    stderr: str
    timed_out: bool
    images: List[str] = []


def _enforce_rate_limit(user_id: int) -> None:
    now = time.monotonic()
    window = _recent_runs[user_id]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= settings.RUN_RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Slow down a little - too many runs this minute.")
    window.append(now)


@router.post("", response_model=RunResponse)
def run_code(payload: RunRequest, user: User = Depends(get_current_user)):
    """Run a snippet from a lesson or the playground. Not graded, not stored."""
    _enforce_rate_limit(user.id)
    result = run_python_code(payload.code, stdin_input=payload.stdin)
    return RunResponse(
        stdout=result.stdout,
        stderr=result.stderr,
        timed_out=result.timed_out,
        images=result.images,
    )

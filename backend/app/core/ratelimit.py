"""
A tiny in-memory sliding-window rate limiter, one window per (limiter, learner).

It is per process, which is enough to stop a script hammering the grading endpoints from one
account; it is not a substitute for a gateway limit.
"""
import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict

from fastapi import Depends, HTTPException

from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User

_WINDOW_SECONDS = 60.0
_windows: Dict[str, Dict[int, Deque[float]]] = defaultdict(lambda: defaultdict(deque))


def reset_rate_limits() -> None:
    """Forget every window (tests)."""
    _windows.clear()


def rate_limited(name: str, limit_getter: Callable[[], int], message: str):
    """A FastAPI dependency that raises 429 once the learner has made `limit` calls in the last minute."""

    def dependency(user: User = Depends(get_current_user)) -> User:
        now = time.monotonic()
        window = _windows[name][user.id]
        while window and now - window[0] > _WINDOW_SECONDS:
            window.popleft()
        if len(window) >= limit_getter():
            raise HTTPException(status_code=429, detail=message)
        window.append(now)
        return user

    return dependency


limit_quiz_submits = rate_limited(
    "quiz-submit",
    lambda: settings.QUIZ_SUBMIT_RATE_LIMIT_PER_MINUTE,
    "Slow down a little - too many quiz submissions this minute.",
)
limit_code_submits = rate_limited(
    "code-submit",
    lambda: settings.CODE_SUBMIT_RATE_LIMIT_PER_MINUTE,
    "Slow down a little - too many code submissions this minute.",
)

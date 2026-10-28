"""Public Python code-runner API: no login, one shared API key. Meant for demos on a trusted network."""
import time
import hmac
from collections import defaultdict, deque
from pathlib import Path
from typing import Deque, Dict, List

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.execution import run_python_code

router = APIRouter(tags=["public-run"])

_recent: Dict[str, Deque[float]] = defaultdict(deque)


class PublicRunRequest(BaseModel):
    code: str = Field(max_length=20_000, examples=["print(sum(range(10)))"])
    stdin: str = Field(default="", max_length=2_000)


class PublicRunResponse(BaseModel):
    stdout: str
    stderr: str
    timed_out: bool
    images: List[str] = []


@router.post("/api/public/run", response_model=PublicRunResponse, summary="Run Python code")
def public_run(payload: PublicRunRequest, request: Request, x_api_key: str = Header(default="")):
    """Run a Python snippet in the sandbox and return stdout, stderr and any matplotlib images (base64 PNG).

    Send your key in the `X-API-Key` header.
    """
    if not settings.PUBLIC_API_ENABLED:
        raise HTTPException(status_code=404, detail="Public runner is disabled.")
    if not settings.PUBLIC_API_KEY or not hmac.compare_digest(x_api_key.encode(), settings.PUBLIC_API_KEY.encode()):
        raise HTTPException(status_code=401, detail="Missing or wrong X-API-Key header.")
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = _recent[client]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= settings.RUN_RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Too many runs this minute.")
    window.append(now)
    r = run_python_code(payload.code, stdin_input=payload.stdin)
    return PublicRunResponse(stdout=r.stdout, stderr=r.stderr, timed_out=r.timed_out, images=r.images)


@router.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def demo_page():
    if not settings.PUBLIC_API_ENABLED:
        raise HTTPException(status_code=404, detail="Public runner is disabled.")
    return (Path(__file__).parent / "public_demo.html").read_text()

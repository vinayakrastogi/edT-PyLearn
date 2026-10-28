"""Run from the repository root on a Docker host: uvicorn runner.app:app --port 8010."""
import hmac
import os
from threading import BoundedSemaphore

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.container_sandbox import ContainerUnavailable, execute_in_container

KEY = os.environ.get("SANDBOX_RUNNER_KEY", "")
if len(KEY) < 32:
    raise RuntimeError("Set SANDBOX_RUNNER_KEY to a random secret of at least 32 characters.")
IMAGE = os.environ.get("SANDBOX_DOCKER_IMAGE", "pylearn-sandbox:latest")
LIMIT = int(os.environ.get("SANDBOX_MAX_CONCURRENT", "2"))
if not 1 <= LIMIT <= 8:
    raise RuntimeError("SANDBOX_MAX_CONCURRENT must be between 1 and 8.")
slots = BoundedSemaphore(LIMIT)
app = FastAPI(title="PyLearn isolated runner", docs_url=None, redoc_url=None, openapi_url=None)


def require_key(x_runner_key: str = Header(default="")):
    if not hmac.compare_digest(x_runner_key.encode(), KEY.encode()):
        raise HTTPException(401, "Invalid runner key.")


class Job(BaseModel):
    code: str = Field(max_length=40_000)
    stdin: str = Field(default="", max_length=2_000)
    timeout: int = Field(default=5, ge=1, le=30)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/execute", dependencies=[Depends(require_key)])
def execute(job: Job):
    if not slots.acquire(blocking=False):
        raise HTTPException(503, "Runner is busy. Retry shortly.")
    try:
        return execute_in_container(job.code, job.stdin, image=IMAGE, timeout=job.timeout)
    except ContainerUnavailable:
        raise HTTPException(503, "The isolated runner is unavailable.") from None
    finally:
        slots.release()

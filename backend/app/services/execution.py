import base64
import binascii
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, List
from threading import BoundedSemaphore

import httpx

from app.core.config import settings
from .container_sandbox import ContainerUnavailable, MAX_RESPONSE_BYTES, execute_in_container

MAX_OUTPUT_CHARS = 20_000
MAX_IMAGES = 3
MAX_IMAGE_BYTES = 400_000
_slots = BoundedSemaphore(settings.SANDBOX_MAX_CONCURRENT)


class SandboxUnavailable(Exception):
    """Infrastructure failures must not become failed graded submissions."""


def _remote_execution(code, stdin):
    try:
        with httpx.stream(
            "POST", settings.SANDBOX_RUNNER_URL.rstrip("/") + "/execute",
            headers={"X-Runner-Key": settings.SANDBOX_RUNNER_KEY, "ngrok-skip-browser-warning": "1"},
            json={"code": code, "stdin": stdin, "timeout": settings.SANDBOX_TIMEOUT_SECONDS},
            timeout=settings.SANDBOX_TIMEOUT_SECONDS + 15, follow_redirects=False, trust_env=False,
        ) as response:
            response.raise_for_status()
            body = bytearray()
            for chunk in response.iter_bytes():
                body.extend(chunk)
                if len(body) > MAX_RESPONSE_BYTES:
                    raise ValueError("Runner response is too large")
        return json.loads(body)
    except (httpx.HTTPError, ValueError, RecursionError):
        raise SandboxUnavailable("The isolated Python runner is unavailable. Please retry shortly.") from None


def _execution_result(data):
    try:
        if (not isinstance(data, dict) or not isinstance(data["stdout"], str)
                or not isinstance(data["stderr"], str) or type(data["error"]) is not bool
                or type(data["timed_out"]) is not bool or not isinstance(data.get("images", []), list)):
            raise ValueError
        images = []
        for value in data.get("images", [])[:MAX_IMAGES]:
            prefix = "data:image/png;base64,"
            if (not isinstance(value, str) or not value.startswith(prefix)
                    or len(value) > MAX_IMAGE_BYTES * 4 // 3 + len(prefix) + 4):
                raise ValueError
            raw = base64.b64decode(value[len(prefix):], validate=True)
            if len(raw) > MAX_IMAGE_BYTES or not raw.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError
            images.append(value)
        return ExecutionResult(_clip(data["stdout"]), _clip(data["stderr"]),
                               data["timed_out"], data["error"], images)
    except (KeyError, TypeError, ValueError, binascii.Error):
        raise SandboxUnavailable("The isolated Python runner returned an invalid response.") from None


class ExecutionResult:
    def __init__(self, stdout: str, stderr: str, timed_out: bool, error: bool, images: List[str] | None = None):
        self.stdout = stdout
        self.stderr = stderr
        self.timed_out = timed_out
        self.error = error
        self.images = images or []


def _clip(text: str) -> str:
    if len(text) > MAX_OUTPUT_CHARS:
        return text[:MAX_OUTPUT_CHARS] + "\n... output truncated ..."
    return text


def _limit_resources(timeout: int):
    """Applied in the child process before exec (POSIX only). Best-effort hardening."""
    def apply():
        try:
            import resource
        except ImportError:  # Windows
            return
        limits = [
            (resource.RLIMIT_CPU, timeout + 1),
            (resource.RLIMIT_FSIZE, 2 * 1024 * 1024),  # max file the program may write
            (resource.RLIMIT_CORE, 0),
        ]
        # RLIMIT_AS is not enforced on macOS; harmless to try elsewhere.
        if sys.platform.startswith("linux"):
            limits.append((resource.RLIMIT_AS, 768 * 1024 * 1024))
        for res, value in limits:
            try:
                resource.setrlimit(res, (value, value))
            except (ValueError, OSError):
                pass
    return apply


def _clean_env(tmpdir: str) -> dict:
    """Nothing from the server's environment (API keys, DB URL, ...) reaches learner code."""
    return {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": tmpdir,
        "TMPDIR": tmpdir,
        "MPLCONFIGDIR": tmpdir,
        "MPLBACKEND": "Agg",
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "LANG": "C.UTF-8",
    }


def _collect_images(tmpdir: str) -> List[str]:
    images: List[str] = []
    for png in sorted(Path(tmpdir).glob("*.png"))[:MAX_IMAGES]:
        if png.is_symlink() or not png.is_file() or png.stat().st_size > MAX_IMAGE_BYTES:
            continue
        data = png.read_bytes()
        if len(data) <= MAX_IMAGE_BYTES:
            images.append("data:image/png;base64," + base64.b64encode(data).decode())
    return images


def run_python_code(code: str, stdin_input: str = "") -> ExecutionResult:
    if settings.SANDBOX_MODE == "disabled":
        raise SandboxUnavailable("Python execution is disabled until an isolated runner is configured.")
    if settings.ENVIRONMENT == "production" and settings.SANDBOX_MODE == "local":
        raise SandboxUnavailable("Local Python execution is disabled in production.")
    if not _slots.acquire(blocking=False):
        raise SandboxUnavailable("Python execution is busy. Please retry shortly.")
    try:
        if settings.SANDBOX_MODE == "remote":
            return _execution_result(_remote_execution(code, stdin_input))
        if settings.SANDBOX_MODE == "docker":
            try:
                data = execute_in_container(code, stdin_input, image=settings.SANDBOX_DOCKER_IMAGE,
                                            timeout=settings.SANDBOX_TIMEOUT_SECONDS)
            except ContainerUnavailable as exc:
                raise SandboxUnavailable(str(exc)) from None
            return _execution_result(data)
        if settings.SANDBOX_MODE != "local":
            raise SandboxUnavailable("Python execution is not configured.")
        return _run_local(code, stdin_input)
    finally:
        _slots.release()


def _run_local(code: str, stdin_input: str = "") -> ExecutionResult:
    """
    Execute learner code in a throw-away directory with a timeout.

    SANDBOX_MODE=local  -> subprocess in isolated mode (-I), scrubbed env, rlimits.
                           Good for development; NOT a security boundary.
    Docker and remote execution are dispatched before this development-only path.
    """
    timeout = settings.SANDBOX_TIMEOUT_SECONDS
    tmpdir = tempfile.mkdtemp(prefix="pylearn-")
    try:
        Path(tmpdir, "solution.py").write_text(code, encoding="utf-8")

        cmd = [sys.executable, "-I", "solution.py"]
        kwargs = {"env": _clean_env(tmpdir), "preexec_fn": _limit_resources(timeout)}

        result = subprocess.run(
            cmd,
            input=stdin_input,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tmpdir,
            **kwargs,
        )
        return ExecutionResult(
            stdout=_clip(result.stdout),
            stderr=_clip(result.stderr),
            timed_out=False,
            error=(result.returncode != 0),
            images=_collect_images(tmpdir),
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(stdout="", stderr="", timed_out=True, error=False)
    except Exception as e:  # noqa: BLE001 - surface any launcher failure as an execution error
        return ExecutionResult(stdout="", stderr=str(e), timed_out=False, error=True)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _first_function_name(user_code: str) -> str | None:
    for line in user_code.splitlines():
        stripped = line.strip()
        if stripped.startswith("def ") and not line.startswith((" ", "\t")):
            return stripped[4:].split("(")[0].strip()
    return None


def build_test_harness(user_code: str, test_input: Any, expected: str) -> str:
    """
    Function problems: define the learner's function, call it with the test input and
    print the result. The first top-level `def` is the function under test.
    Falls back to running the code as-is when no function is defined.
    """
    fn_name = _first_function_name(user_code)
    if fn_name:
        return (
            user_code
            + "\n\n# --- test harness ---\n"
            + f"_input = {repr(test_input)}\n"
            + "if isinstance(_input, list):\n"
            + f"    _result = {fn_name}(*_input)\n"
            + "else:\n"
            + f"    _result = {fn_name}(_input)\n"
            + "print(_result, end='')\n"
        )
    return user_code

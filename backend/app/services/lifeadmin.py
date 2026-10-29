"""HTTP-only adapter: no LifeAdmin imports, files or database access."""
from asyncio import sleep, timeout
import logging
from uuid import UUID

import httpx
from fastapi import HTTPException
from pydantic import TypeAdapter, ValidationError

from app.core.config import settings
from app.schemas.notes import LessonNote

logger = logging.getLogger(__name__)

# Render's free API may return gateway errors while it wakes. These waits and
# every HTTP attempt share LIFEADMIN_TIMEOUT_SECONDS as one overall deadline.
_RETRY_DELAYS = (0, 2, 4, 8, 12, 16, 16)


def _temporary_gateway(response: httpx.Response) -> bool:
    if response.status_code in (502, 504):
        return True
    # A JSON 503 is LifeAdmin's configuration error, not a hosting startup page.
    return response.status_code == 503 and "json" not in response.headers.get("content-type", "").lower()


async def request_lifeadmin(method: str, path: str, *, params=None, data=None):
    if not settings.LIFEADMIN_API_KEY:
        raise HTTPException(503, "Lesson notes are not configured. Set LIFEADMIN_API_URL and LIFEADMIN_API_KEY on the server.")
    try:
        async with timeout(settings.LIFEADMIN_TIMEOUT_SECONDS), httpx.AsyncClient(
            base_url=settings.LIFEADMIN_API_URL.rstrip("/"),
            timeout=settings.LIFEADMIN_TIMEOUT_SECONDS,
            headers={
                "X-API-Key": settings.LIFEADMIN_API_KEY,
                "ngrok-skip-browser-warning": "1",
            },
            follow_redirects=False,
            trust_env=False,
        ) as client:
            for attempt, delay in enumerate(_RETRY_DELAYS, start=1):
                if delay:
                    await sleep(delay)
                # Keep the original POST request_id: LifeAdmin deduplicates a
                # save even if it committed before a gateway lost the response.
                response = await client.request(method, path, params=params, json=data)
                if not _temporary_gateway(response):
                    break
                logger.warning("LifeAdmin gateway status %s on attempt %s", response.status_code, attempt)
    except (httpx.TimeoutException, TimeoutError):
        raise HTTPException(504, "LifeAdmin took too long to respond. Retry with the same note.") from None
    except httpx.RequestError:
        raise HTTPException(503, "Cannot reach LifeAdmin. Check that its API is running and the server address is correct.") from None
    if _temporary_gateway(response):
        raise HTTPException(503, "LifeAdmin is starting or temporarily unavailable. Try saving again shortly.")
    if response.status_code == 404:
        raise HTTPException(404, "Note not found.")
    if response.status_code == 409:
        raise HTTPException(409, "Create a LifeAdmin account using the same email as your PyLearn account, then retry.")
    if response.status_code in (401, 403, 503):
        raise HTTPException(503, "LifeAdmin is unavailable or its API key is not configured correctly.")
    if not response.is_success:
        raise HTTPException(502, "LifeAdmin could not process the request.")
    if method == "DELETE":
        return None
    try:
        adapter = TypeAdapter(list[LessonNote] if method == "GET" else LessonNote)
        return adapter.validate_python(response.json())
    except (ValueError, ValidationError):
        raise HTTPException(502, "LifeAdmin returned an invalid response.") from None


def owner_id(user_id: int) -> str:
    return f"{settings.LIFEADMIN_CLIENT_ID}:{user_id}"


async def list_notes(user_id: int, resource_id: str, owner_email: str):
    return await request_lifeadmin("GET", "/api/v1/notes", params={
        "owner_id": owner_id(user_id), "owner_email": owner_email, "resource_id": resource_id,
    })


async def create_note(user_id: int, resource_id: str, title: str, content: str, request_id: UUID, owner_email: str):
    return await request_lifeadmin("POST", "/api/v1/notes", data={
        "owner_id": owner_id(user_id), "owner_email": owner_email, "resource_id": resource_id,
        "title": title[:200], "content": content, "request_id": str(request_id),
    })


async def delete_note(user_id: int, note_id: UUID, owner_email: str):
    await request_lifeadmin("DELETE", f"/api/v1/notes/{note_id}",
                            params={"owner_id": owner_id(user_id), "owner_email": owner_email})

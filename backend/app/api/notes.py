from uuid import UUID

from fastapi import APIRouter, Depends, Response

from app.content_repository.base import ContentRepository
from app.content_repository.loader import get_content_repo
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.notes import LessonNote, LessonNoteCreate, LessonNotes
from app.services import lifeadmin

router = APIRouter(prefix="/api/notes", tags=["lesson-notes"])


@router.get("/{module_id}/{doc_id}", response_model=LessonNotes)
async def list_notes(module_id: str, doc_id: str, user: User = Depends(get_current_user),
                     repo: ContentRepository = Depends(get_content_repo)):
    await repo.get_doc(module_id, doc_id)
    return {"notes": await lifeadmin.list_notes(user.id, f"{module_id}/{doc_id}", user.email)}


@router.post("/{module_id}/{doc_id}", response_model=LessonNote, status_code=201)
async def create_note(module_id: str, doc_id: str, payload: LessonNoteCreate,
                      user: User = Depends(get_current_user),
                      repo: ContentRepository = Depends(get_content_repo)):
    doc = await repo.get_doc(module_id, doc_id)
    return await lifeadmin.create_note(user.id, f"{module_id}/{doc_id}", doc.title,
                                       payload.content, payload.request_id, user.email)


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: UUID, user: User = Depends(get_current_user)):
    await lifeadmin.delete_note(user.id, note_id, user.email)
    return Response(status_code=204)

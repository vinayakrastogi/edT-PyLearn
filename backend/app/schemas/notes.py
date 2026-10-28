from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LessonNoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    content: str = Field(min_length=1, max_length=20_000)
    request_id: UUID


class LessonNote(BaseModel):
    id: UUID
    title: str
    content: str
    resource_id: str
    created_at: str


class LessonNotes(BaseModel):
    notes: list[LessonNote]

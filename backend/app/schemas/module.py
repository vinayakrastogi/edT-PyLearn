from pydantic import BaseModel
from typing import List, Optional

# Module and badge icons are kebab-case icon keys (see ICONS in frontend/src/lib/icons.tsx), never emoji.
DEFAULT_MODULE_ICON = "book-open"


class DocMeta(BaseModel):
    id: str
    title: str
    order: int
    concepts: List[str] = []


class DocPage(BaseModel):
    id: str
    title: str
    order: int
    concepts: List[str] = []
    content_md: str  # raw markdown; the client renders it (no server-side HTML, so no XSS surface)
    read_minutes: int = 1


class ModuleMeta(BaseModel):
    id: str
    title: str
    description: str
    order: int
    icon: str = DEFAULT_MODULE_ICON  # kebab-case key from frontend/src/lib/icons.tsx ICONS
    doc_count: int = 0
    problem_count: int = 0
    is_generative: bool = False


class ModuleDetail(BaseModel):
    id: str
    title: str
    description: str
    order: int
    icon: str
    docs: List[DocMeta]
    quiz_id: Optional[str] = None
    problems: List[dict] = []
    is_generative: bool = False

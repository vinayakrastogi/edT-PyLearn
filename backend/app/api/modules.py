from fastapi import APIRouter, Depends, HTTPException
import shutil
from typing import List

from app.core.deps import require_faculty
from app.models.user import User
from app.content_repository.loader import get_content_repo
from app.content_repository.base import ContentRepository
from app.schemas.module import ModuleMeta, ModuleDetail, DocPage

router = APIRouter(prefix="/api/modules", tags=["modules"])


@router.get("", response_model=List[ModuleMeta])
async def list_modules(repo: ContentRepository = Depends(get_content_repo)):
    return await repo.list_modules()


@router.get("/{module_id}", response_model=ModuleDetail)
async def get_module(module_id: str, repo: ContentRepository = Depends(get_content_repo)):
    return await repo.get_module(module_id)


@router.get("/{module_id}/docs/{doc_id}", response_model=DocPage)
async def get_doc(
    module_id: str,
    doc_id: str,
    repo: ContentRepository = Depends(get_content_repo),
):
    return await repo.get_doc(module_id, doc_id)

@router.delete("/{module_id}")
async def delete_module(
    module_id: str,
    repo: ContentRepository = Depends(get_content_repo),
    _: User = Depends(require_faculty),
):
    if not module_id.startswith("generated-"):
        raise HTTPException(status_code=403, detail="Only AI-generated modules can be deleted.")

    module_dir = repo._module_path(module_id)  # type: ignore[attr-defined]  # validates the id too
    shutil.rmtree(module_dir)
    return {"deleted": module_id}

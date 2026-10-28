from app.content_repository.base import ContentRepository
from app.content_repository.file_repo import FileSystemContentRepository
from app.core.config import settings

_repo: ContentRepository | None = None


def get_content_repo() -> ContentRepository:
    """
    Factory — returns the configured ContentRepository singleton.
    To swap to a different backend (e.g. Azure Blob), change only here.
    """
    global _repo
    if _repo is None:
        _repo = FileSystemContentRepository(settings.CONTENT_DIR)
    return _repo

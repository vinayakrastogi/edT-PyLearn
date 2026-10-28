from abc import ABC, abstractmethod
from typing import List

from app.schemas.module import ModuleMeta, ModuleDetail, DocPage
from app.schemas.quiz import QuizResponse
from app.schemas.problem import ProblemDetail


class ContentRepository(ABC):
    """
    Abstract interface for reading module content.

    Implementations:
    - FileSystemContentRepository: reads from /content directory (current)
    - AzureBlobContentRepository: future, same interface

    Swapping the implementation requires only changing the factory in loader.py,
    not any API route or service code.
    """

    @abstractmethod
    async def list_modules(self) -> List[ModuleMeta]:
        """Return metadata for all modules (no content body)."""
        ...

    @abstractmethod
    async def get_module(self, module_id: str) -> ModuleDetail:
        """Return module detail including doc list and problem list."""
        ...

    @abstractmethod
    async def get_doc(self, module_id: str, doc_id: str) -> DocPage:
        """Return a single doc page with rendered HTML."""
        ...

    @abstractmethod
    async def get_quiz(self, module_id: str) -> QuizResponse:
        """Return quiz questions — correct answers stripped."""
        ...

    @abstractmethod
    async def get_problem(self, module_id: str, problem_id: str) -> ProblemDetail:
        """Return problem detail — hidden tests NOT included."""
        ...

    @abstractmethod
    async def get_hidden_tests(self, module_id: str, problem_id: str) -> List[dict]:
        """Return ALL test cases including hidden — server-side only, never sent to client."""
        ...

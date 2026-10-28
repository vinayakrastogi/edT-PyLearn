import json
import re
from pathlib import Path
from typing import List

import frontmatter
from fastapi import HTTPException

from app.content_repository.base import ContentRepository
from app.schemas.module import DEFAULT_MODULE_ICON, ModuleMeta, ModuleDetail, DocPage, DocMeta
from app.schemas.quiz import QuizResponse
from app.schemas.problem import ProblemDetail

import yaml


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_HIDDEN_QUESTION_KEYS = ("correct", "correct_answer", "explanation")


def _check_id(value: str, what: str = "id") -> str:
    """Reject anything that could escape the content directory (../, slashes, etc.)."""
    if not _SAFE_ID.match(value or ""):
        raise HTTPException(status_code=400, detail=f"Invalid {what}")
    return value


class FileSystemContentRepository(ContentRepository):
    """
    Reads module content from the local /content directory.

    Content layout:
    content/
      {module_id}/
        module.yaml
        docs/
          {order}-{slug}.md       (YAML frontmatter: id, title, order, concepts)
        quiz.json
        problems/
          {problem_id}.json
    """

    def __init__(self, content_dir: str):
        self.content_dir = Path(content_dir).resolve()

    def _module_path(self, module_id: str) -> Path:
        p = self.content_dir / _check_id(module_id, "module id")
        if not p.exists():
            raise HTTPException(status_code=404, detail=f"Module '{module_id}' not found")
        return p

    async def list_modules(self) -> List[ModuleMeta]:
        modules = []
        if not self.content_dir.exists():
            return modules
        for entry in sorted(self.content_dir.iterdir()):
            if not entry.is_dir():
                continue
            meta_file = entry / "module.yaml"
            if not meta_file.exists():
                continue
            with open(meta_file) as f:
                data = yaml.safe_load(f)
            doc_count = len(list((entry / "docs").glob("*.md"))) if (entry / "docs").exists() else 0
            problems_dir = entry / "problems"
            problem_count = len(list(problems_dir.glob("*.json"))) if problems_dir.exists() else 0
            modules.append(ModuleMeta(
                id=data["id"],
                title=data["title"],
                description=data.get("description", ""),
                order=data.get("order", 0),
                icon=data.get("icon", DEFAULT_MODULE_ICON),
                doc_count=doc_count,
                problem_count=problem_count,
                is_generative=data.get("is_generative", False),
            ))
        return sorted(modules, key=lambda m: m.order)

    async def get_module(self, module_id: str) -> ModuleDetail:
        path = self._module_path(module_id)
        meta_file = path / "module.yaml"
        with open(meta_file) as f:
            data = yaml.safe_load(f)

        # Docs
        docs: List[DocMeta] = []
        docs_dir = path / "docs"
        if docs_dir.exists():
            for md_file in sorted(docs_dir.glob("*.md")):
                post = frontmatter.load(str(md_file))
                docs.append(DocMeta(
                    id=post.metadata.get("id", md_file.stem),
                    title=post.metadata.get("title", md_file.stem),
                    order=post.metadata.get("order", 0),
                    concepts=post.metadata.get("concepts", []),
                ))
        docs = sorted(docs, key=lambda d: d.order)

        # Problems
        problems = []
        problems_dir = path / "problems"
        if problems_dir.exists():
            for pf in sorted(problems_dir.glob("*.json")):
                with open(pf) as f:
                    pd = json.load(f)
                problems.append({"id": pd["id"], "title": pd["title"], "concepts": pd.get("concepts", [])})

        # Quiz
        quiz_id = None
        if (path / "quiz.json").exists():
            with open(path / "quiz.json") as f:
                qdata = json.load(f)
            quiz_id = qdata.get("id", f"{module_id}-quiz")

        return ModuleDetail(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            order=data.get("order", 0),
            icon=data.get("icon", DEFAULT_MODULE_ICON),
            docs=docs,
            quiz_id=quiz_id,
            problems=problems,
            is_generative=data.get("is_generative", False),
        )

    async def get_doc(self, module_id: str, doc_id: str) -> DocPage:
        path = self._module_path(module_id)
        docs_dir = path / "docs"
        # Find file where frontmatter id matches
        target = None
        for md_file in docs_dir.glob("*.md"):
            post = frontmatter.load(str(md_file))
            if post.metadata.get("id") == doc_id:
                target = post
                break
        if target is None:
            raise HTTPException(status_code=404, detail=f"Doc '{doc_id}' not found in module '{module_id}'")

        words = len(target.content.split())
        return DocPage(
            id=doc_id,
            title=target.metadata.get("title", doc_id),
            order=target.metadata.get("order", 0),
            concepts=target.metadata.get("concepts", []),
            content_md=target.content,
            read_minutes=max(1, round(words / 200)),
        )

    async def get_quiz(self, module_id: str) -> QuizResponse:
        path = self._module_path(module_id)
        quiz_file = path / "quiz.json"
        if not quiz_file.exists():
            raise HTTPException(status_code=404, detail=f"No quiz found for module '{module_id}'")
        with open(quiz_file) as f:
            data = json.load(f)

        # Strip correct answers before returning
        questions_safe = []
        for q in data.get("questions", []):
            q_copy = {k: v for k, v in q.items() if k not in _HIDDEN_QUESTION_KEYS}
            questions_safe.append(q_copy)

        return QuizResponse(
            id=data.get("id", f"{module_id}-quiz"),
            module_id=module_id,
            title=data.get("title", "Quiz"),
            questions=questions_safe,
        )

    async def get_problem(self, module_id: str, problem_id: str) -> ProblemDetail:
        path = self._module_path(module_id)
        pfile = path / "problems" / f"{_check_id(problem_id, 'problem id')}.json"
        if not pfile.exists():
            raise HTTPException(status_code=404, detail=f"Problem '{problem_id}' not found")
        with open(pfile) as f:
            data = json.load(f)
        return ProblemDetail(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            starter_code=data.get("starter_code", ""),
            concepts=data.get("concepts", []),
            visible_tests=data.get("visible_tests", []),
            type=data.get("type", "function"),
            difficulty=data.get("difficulty", "easy"),
            hints=data.get("hints", []),
        )

    async def get_hidden_tests(self, module_id: str, problem_id: str) -> List[dict]:
        path = self._module_path(module_id)
        pfile = path / "problems" / f"{_check_id(problem_id, 'problem id')}.json"
        if not pfile.exists():
            raise HTTPException(status_code=404, detail=f"Problem '{problem_id}' not found")
        with open(pfile) as f:
            data = json.load(f)
        # Return all tests (visible + hidden)
        visible = data.get("visible_tests", [])
        hidden = data.get("hidden_tests", [])
        return [{"is_hidden": False, **t} for t in visible] + [{"is_hidden": True, **t} for t in hidden]

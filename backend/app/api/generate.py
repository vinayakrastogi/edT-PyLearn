import os
import json
import logging
import uuid
import re
from pathlib import Path
import ipaddress
import socket
from typing import Any
from urllib.parse import urlparse

import yaml
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from pypdf import PdfReader
from groq import Groq
from app.core.config import settings
from app.core.deps import require_faculty
from app.core.text import delete_pictographs_deep, strip_pictographs, strip_pictographs_deep
from app.services.grading import grade_submission

logger = logging.getLogger(__name__)

# Every generation route spends AI credits and writes to disk: faculty only.
router = APIRouter(prefix="/api/generate", tags=["generate"], dependencies=[Depends(require_faculty)])

_SAFE_SLUG = re.compile(r"[^a-zA-Z0-9_-]")

# Every AI-generated module gets this icon key (see ICONS in frontend/src/lib/icons.tsx). The model is
# never asked for an icon, so it can never hand us an emoji.
GENERATED_MODULE_ICON = "sparkles"

# Problem fields that the grader runs or compares character for character: the code and the whole
# test cases (input / stdin / driver / expected). Emoji in them are deleted without tidying any
# space, so a string literal in the solution and the output it prints lose exactly the same
# characters. Every other field (title, description, concepts, hints) is prose and is tidied.
_PROBLEM_CODE_FIELDS = frozenset({"starter_code", "solution_code", "visible_tests", "hidden_tests"})


def _slug(value: str, fallback: str) -> str:
    return _SAFE_SLUG.sub("", value or "")[:80] or fallback


def _solution_passes(problem: dict) -> bool:
    """True when the problem's own solution passes all of its own tests (or there is nothing to run)."""
    solution = problem.get("solution_code")
    tests = [*(problem.get("visible_tests") or []), *(problem.get("hidden_tests") or [])]
    if not isinstance(solution, str) or not solution.strip() or not tests:
        return True
    if not all(isinstance(t, dict) for t in tests):
        return False
    return grade_submission(solution, tests)["status"] == "PASS"


def _clean_problem(content: dict) -> dict | None:
    """Strip emoji from one generated problem.

    Returns None when the emoji sat in the code or tests and removing them broke the problem, i.e.
    its solution no longer passes its tests (say the code builds the symbol with chr() while the
    expected output spells it out). A problem whose code and tests had no emoji is never run here.
    """
    clean, code_changed = {}, False
    for key, value in content.items():
        if key in _PROBLEM_CODE_FIELDS:
            clean[key] = delete_pictographs_deep(value)
            code_changed = code_changed or clean[key] != value
        else:
            clean[key] = strip_pictographs_deep(value)
    if code_changed and not _solution_passes(clean):
        logger.warning("Dropped generated problem %r: removing emoji from its code broke its tests", clean.get("id"))
        return None
    return clean


def _clean_problems(problems: Any) -> list:
    """_clean_problem over the model's problem list ({filename, content} items); broken ones are dropped."""
    if not isinstance(problems, list):
        return []
    cleaned = []
    for item in problems:
        if not isinstance(item, dict) or not isinstance(item.get("content"), dict):
            continue
        content = _clean_problem(item["content"])
        if content is not None:
            cleaned.append({**strip_pictographs_deep({k: v for k, v in item.items() if k != "content"}), "content": content})
    return cleaned


def _assert_public_url(url: str) -> None:
    """Block SSRF: only http(s) URLs that resolve to public addresses."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise HTTPException(status_code=400, detail="Only http(s) URLs are allowed")
    try:
        infos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="Could not resolve that URL")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise HTTPException(status_code=400, detail="That URL points to a private address")


class ModuleInput(BaseModel):
    id: str
    title: str
    description: str
    order: int
    icon: str = GENERATED_MODULE_ICON  # ignored: generated modules always get GENERATED_MODULE_ICON

class DocInput(BaseModel):
    filename: str
    id: str
    title: str
    order: int
    concepts: list[str]
    content: str

class TopicRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)


class UrlRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2000)


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=60000)


class SaveLocalRequest(BaseModel):
    module: ModuleInput
    docs: list[DocInput]
    quiz_json: dict
    problems: list[dict]

@router.post("/from-pdf")
async def generate_from_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        reader = PdfReader(file.file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")

    if not text.strip():
        raise HTTPException(status_code=400, detail="PDF contains no extractable text.")

    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured on backend.")

    client = Groq(api_key=api_key)
    return generate_with_ai(client, text, context="PDF text")


@router.post("/save-local")
async def save_local(payload: SaveLocalRequest):
    content_dir = Path(settings.CONTENT_DIR).resolve()

    raw_id = _slug(payload.module.id.lower(), uuid.uuid4().hex[:6])
    module_id = raw_id if raw_id.startswith("generated-") else f"generated-{raw_id}"

    module_dir = content_dir / module_id
    if module_dir.exists():
        raise HTTPException(status_code=400, detail="A module with this ID already exists.")

    module_dir.mkdir(parents=True)

    # yaml.safe_dump guarantees valid YAML even if the AI puts quotes/colons in a title
    (module_dir / "module.yaml").write_text(yaml.safe_dump({
        "id": module_id,
        "title": strip_pictographs(payload.module.title),
        "description": strip_pictographs(payload.module.description),
        "order": payload.module.order,
        "icon": GENERATED_MODULE_ICON,
    }, allow_unicode=True, sort_keys=False))

    docs_dir = module_dir / "docs"
    docs_dir.mkdir()
    for n, doc in enumerate(payload.docs, start=1):
        doc_id = _slug(doc.id, f"lesson-{n}")
        meta = yaml.safe_dump(
            {"id": doc_id, "title": strip_pictographs(doc.title), "order": doc.order,
             "concepts": strip_pictographs_deep(doc.concepts)},
            allow_unicode=True, sort_keys=False,
        )
        filename = _slug(Path(doc.filename).stem, doc_id) + ".md"
        (docs_dir / filename).write_text(f"---\n{meta}---\n\n{strip_pictographs(doc.content)}\n")

    with open(module_dir / "quiz.json", "w") as f:
        json.dump(strip_pictographs_deep(payload.quiz_json), f, indent=2)

    probs_dir = module_dir / "problems"
    probs_dir.mkdir()
    skipped_problems = []
    for n, prob in enumerate(payload.problems, start=1):
        raw_content = prob.get("content")
        if not isinstance(raw_content, dict):
            skipped_problems.append(f"problem-{n}")
            continue
        # May run the solution (only when emoji had to come out of its code), so off the event loop.
        prob_content = await run_in_threadpool(_clean_problem, raw_content)
        if prob_content is None:
            skipped_problems.append(_slug(str(raw_content.get("id", "")), f"problem-{n}"))
            continue
        prob_id = _slug(str(prob_content.get("id", "")), f"problem-{n}")
        prob_content["id"] = prob_id
        with open(probs_dir / f"{prob_id}.json", "w") as f:
            json.dump(prob_content, f, indent=2)

    return {"status": "success", "module_id": module_id, "skipped_problems": skipped_problems}


# Helper function for AI generation
def generate_with_ai(client: Groq, source_text: str, context: str = "content") -> dict:
    prompt = f"""
    You are an expert curriculum designer and senior software engineer. Based on the following {context}, generate a highly detailed, comprehensive, and interactive learning module.
    
    CRITICAL INSTRUCTIONS TO PREVENT SHORT/LAZY GENERATION:
    1. Lessons (docs): You MUST generate at least 3-4 separate lessons. Each lesson's content MUST be extremely detailed (at least 500-800 words), complete with explanations, code examples, and bolded terms. Do NOT write short 2-line summaries.
    2. Quiz (quiz_json): You MUST generate at least 4-5 multiple choice questions. The 'correct_answer' field MUST be the integer index (0, 1, 2, or 3) of the correct option in the options array.
    3. Coding Problems (problems): You MUST generate at least 1-2 coding problems. Provide a detailed description, meaningful starter code, and the full solution code.
    4. Plain text only: do NOT use emoji or pictographic symbols (check marks, stars, arrows drawn as symbols) anywhere, including headings, lists, code and printed output.
    
    Return the output STRICTLY as a raw JSON object (do not wrap in markdown ```json) matching this exact schema:
    {{
      "module": {{
        "id": "string (lowercase, dashes only)",
        "title": "string",
        "description": "string",
        "order": 1
      }},
      "docs": [
        {{
          "filename": "string (e.g. '01-intro.md')", 
          "id": "string",
          "title": "string",
          "order": 1,
          "concepts": ["string"],
          "content": "string (LONG, DETAILED raw markdown content ONLY, do NOT include frontmatter. MUST contain code examples.)"
        }}
      ],
      "quiz_json": {{
         "id": "string",
         "title": "string",
         "questions": [
           {{"id": "string", "type": "mcq", "question": "string", "options": ["string", "string", "string", "string"], "correct_answer": 0, "concepts": ["string"]}}
         ]
      }},
      "problems": [
        {{"filename": "string (e.g. '01-prob.json')", "content": {{"id": "str", "title": "str", "description": "str (detailed)", "starter_code": "str", "concepts": ["str"], "visible_tests": [{{"input": "str", "expected": "str"}}], "hidden_tests": [{{"input": "str", "expected": "str"}}], "solution_code": "str"}}}}
      ]
    }}

    Text to process:
    {source_text[:30000]}
    """
    
    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        raw_text = response.choices[0].message.content
        if raw_text.startswith("```json"):
            raw_text = raw_text.strip()[7:-3]
        
        data = json.loads(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")
    return _clean_generated(data)


def _clean_generated(data: dict) -> dict:
    """Strip emoji from whatever the model wrote and give the module our own icon key.

    Problems are cleaned field by field (see _clean_problem) so their solutions keep passing their tests.
    """
    if not isinstance(data, dict):
        raise HTTPException(status_code=500, detail="AI Generation failed: the model did not return a JSON object")
    has_problems = "problems" in data
    problems = data.get("problems")
    data = strip_pictographs_deep({k: v for k, v in data.items() if k != "problems"})
    if has_problems:
        data["problems"] = _clean_problems(problems)
    if isinstance(data.get("module"), dict):
        data["module"]["icon"] = GENERATED_MODULE_ICON
    return data


@router.post("/from-topic")
async def generate_from_topic(payload: TopicRequest):
    """Generate module from topic name/description"""
    topic = payload.topic
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured on backend.")
    
    if not topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    client = Groq(api_key=api_key)
    
    # Create a rich prompt for topic-based generation
    enhanced_prompt = f"""
    Create a comprehensive Python learning module about: {topic}
    
    Include:
    - Clear explanations suitable for learners
    - Practical code examples and use cases
    - Best practices and common pitfalls
    - Hands-on coding exercises
    """
    
    return generate_with_ai(client, enhanced_prompt, context="topic")


@router.post("/from-url")
async def generate_from_url(payload: UrlRequest):
    """Generate module from URL (scraping)"""
    url = payload.url
    import requests
    from bs4 import BeautifulSoup
    
    # Reject bad input first, so an unsafe URL is a 400 whether or not the AI key is configured.
    if not url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty")

    _assert_public_url(url)

    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured on backend.")

    try:
        # Scrape the URL (redirects disabled: a redirect could bounce to an internal host)
        response = requests.get(url, timeout=10, allow_redirects=False, headers={'User-Agent': 'PyLearn/1.0'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No content extracted from URL")
        
        client = Groq(api_key=api_key)
        return generate_with_ai(client, text, context="web page")
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")


@router.post("/from-text")
async def generate_from_text(payload: TextRequest):
    """Generate module from pasted text/markdown"""
    text = payload.text
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured on backend.")
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    client = Groq(api_key=api_key)
    return generate_with_ai(client, text, context="text content")

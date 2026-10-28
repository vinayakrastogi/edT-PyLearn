"""
Badge and module icons are kebab-case keys that the frontend turns into SVG icons (ICONS in
frontend/src/lib/icons.tsx). An unknown key would silently fall back to a book, so every key the
backend can send must exist in that map.
"""
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from fastapi.testclient import TestClient

from app.api.generate import GENERATED_MODULE_ICON, _clean_generated
from app.core.config import settings
from app.core.deps import get_current_user
from app.core.text import delete_pictographs, strip_pictographs, strip_pictographs_deep
from app.main import app
from app.schemas.module import DEFAULT_MODULE_ICON
from app.services.gamification_rules import BADGES
from app.services.grading import grade_submission
from tests.test_no_emoji import PROSE_RE

ROOT = Path(__file__).resolve().parents[2]
ICONS_FILE = ROOT / "frontend" / "src" / "lib" / "icons.tsx"
CONTENT_DIR = ROOT / "content"

_ICONS_BLOCK = re.compile(r"^(?:export\s+)?const ICONS\b[^=]*=\s*\{(?P<body>.*?)\n\}", re.DOTALL | re.MULTILINE)
_ICON_KEY = re.compile(r"^\s*'?(?P<key>[a-z0-9-]+)'?\s*:", re.MULTILINE)
_KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Test strings with emoji in them, built from code points so this file passes the emoji check.
PARTY, SNAKE, CHECK, STAR, VS16 = chr(0x1F389), chr(0x1F40D), chr(0x2713), chr(0x2B50), chr(0xFE0F)
ARROW = chr(0x2192)


def icon_keys() -> set:
    match = _ICONS_BLOCK.search(ICONS_FILE.read_text(encoding="utf-8"))
    assert match, f"could not find `const ICONS = {{...}}` in {ICONS_FILE}"
    return {m.group("key") for m in _ICON_KEY.finditer(match.group("body"))}


def module_yamls() -> list:
    return sorted(CONTENT_DIR.glob("*/module.yaml"))


def test_the_icons_map_can_be_read():
    keys = icon_keys()
    assert len(keys) >= 20
    assert all(_KEBAB.match(k) for k in keys), sorted(keys)
    assert DEFAULT_MODULE_ICON in keys and GENERATED_MODULE_ICON in keys


def test_every_badge_icon_is_a_known_icon_key():
    keys = icon_keys()
    unknown = {b.id: b.icon for b in BADGES if b.icon not in keys}
    assert not unknown, f"badge icons missing from ICONS in {ICONS_FILE.name}: {unknown}"


def test_every_module_icon_is_a_known_icon_key():
    keys = icon_keys()
    files = module_yamls()
    assert len(files) >= 11  # the ten core modules + the generative one
    unknown = {}
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        icon = data.get("icon", DEFAULT_MODULE_ICON)
        if icon not in keys:
            unknown[path.parent.name] = icon
    assert not unknown, f"module.yaml icons missing from ICONS in {ICONS_FILE.name}: {unknown}"


# --------------------------------------------------------------------------------------
# AI-generated content never carries emoji
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, clean",
    [
        (f"## {SNAKE} Intro", "## Intro"),
        (f"Great job! {PARTY}", "Great job!"),
        (f"Great job! {PARTY}\nNext line", "Great job!\nNext line"),
        (f"a {STAR}{VS16} b", "a b"),
        (f"print('{CHECK} done')", "print('done')"),
        (f"Input {ARROW} Process", f"Input {ARROW} Process"),  # plain arrows are fine in prose
        ("    indented = True\n", "    indented = True\n"),  # code indentation is untouched
        ("", ""),
    ],
)
def test_strip_pictographs(raw, clean):
    assert strip_pictographs(raw) == clean


def test_strip_pictographs_deep_cleans_nested_values_only():
    data = {"title": f"Loops {PARTY}", "options": [f"{CHECK} yes", "no"], "correct_answer": 0}
    assert strip_pictographs_deep(data) == {"title": "Loops", "options": ["yes", "no"], "correct_answer": 0}


def test_generated_output_gets_the_sparkles_icon_and_no_emoji():
    data = _clean_generated({"module": {"title": f"{SNAKE} Snakes", "icon": SNAKE}, "docs": [{"content": f"Hi {PARTY}"}]})
    assert data["module"] == {"title": "Snakes", "icon": GENERATED_MODULE_ICON}
    assert data["docs"][0]["content"] == "Hi"


def _save_local(tmp_path, monkeypatch, payload: dict):
    monkeypatch.setattr(settings, "CONTENT_DIR", str(tmp_path))
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=2, role="faculty", email="f@example.com", full_name="Fac"
    )
    try:
        return TestClient(app).post("/api/generate/save-local", json=payload)
    finally:
        app.dependency_overrides.clear()


def test_save_local_writes_an_icon_key_and_strips_emoji(tmp_path, monkeypatch):
    r = _save_local(tmp_path, monkeypatch, {
        "module": {"id": "emoji-test", "title": f"{SNAKE} Snakes", "description": f"Fun {PARTY}", "order": 1, "icon": SNAKE},
        "docs": [{"filename": "01-intro.md", "id": "intro", "title": f"{STAR} Intro", "order": 1,
                  "concepts": [f"{CHECK} basics"], "content": f"# Hello {PARTY}\n\nprint('{CHECK} ok')"}],
        "quiz_json": {"id": "q", "title": "Quiz", "questions": [{"id": "q1", "question": f"Ready? {PARTY}"}]},
        "problems": [{"filename": "01.json", "content": {"id": "p1", "title": f"{STAR} Sum", "solution_code": "print(1)"}}],
    })
    assert r.status_code == 200, r.text
    folder = tmp_path / r.json()["module_id"]

    meta = yaml.safe_load((folder / "module.yaml").read_text(encoding="utf-8"))
    assert meta["icon"] == GENERATED_MODULE_ICON
    assert (meta["title"], meta["description"]) == ("Snakes", "Fun")

    saved = "\n".join(
        p.read_text(encoding="utf-8") for p in sorted(folder.rglob("*")) if p.is_file()
    )
    for ch in (SNAKE, PARTY, CHECK, STAR):
        assert ch not in saved
    assert "# Hello\n\nprint('ok')" in (folder / "docs" / "01-intro.md").read_text(encoding="utf-8")
    assert json.loads((folder / "problems" / "p1.json").read_text(encoding="utf-8"))["title"] == "Sum"


# A program whose printed output carries the emoji from a string literal. Tidying the space around
# the emoji differently in the code and in the expected output used to break it.
STARS_PROBLEM = {
    "id": "stars", "title": f"{STAR} Stars", "description": f"Print a star on each line {PARTY}",
    "type": "program", "concepts": [f"{CHECK} loops"], "hints": [f"Use range {STAR}"],
    "starter_code": f"# print('{STAR}', i)\n",
    "solution_code": f"for i in range(3):\n    print('{STAR}', i)\n",
    "visible_tests": [{"stdin": "", "expected": f"{STAR} 0\n{STAR} 1\n{STAR} 2"}],
    "hidden_tests": [{"stdin": "", "expected": f"{STAR} 0\n{STAR} 1\n{STAR} 2\n"}],
}
# A function problem with emoji on both sides of the value it returns.
CHEER_PROBLEM = {
    "id": "cheer", "title": "Cheer", "description": "Cheer a friend on.",
    "solution_code": f"def cheer(name):\n    return '{CHECK} ' + name + '! {PARTY}'\n",
    "visible_tests": [{"input": "Ada", "expected": f"{CHECK} Ada! {PARTY}"}],
    "hidden_tests": [{"input": ["Bo"], "expected": f"{CHECK} Bo! {PARTY}"}],
}
# The code builds the symbol with chr(), so only the expected output loses it: removal breaks this one.
BUILT_PROBLEM = {
    "id": "built", "title": "Built star", "description": "Print a star.", "type": "program",
    "solution_code": "print(chr(0x2B50) + ' ok')\n",
    "visible_tests": [{"stdin": "", "expected": f"{STAR} ok"}],
}


@pytest.mark.parametrize(
    "raw, clean",
    [
        (f"print('{STAR}', i)", "print('', i)"),
        (f"{STAR} 0\n{STAR} 1", " 0\n 1"),  # the same leading space the code above prints
        (f"x = 'a {STAR}{VS16} b'  ", "x = 'a  b'  "),
        ("    indented = True\n", "    indented = True\n"),
        ("", ""),
    ],
)
def test_delete_pictographs_touches_no_space(raw, clean):
    assert delete_pictographs(raw) == clean


def _all_tests(problem: dict) -> list:
    """The tests the grader runs for a saved problem (as the file repository combines them)."""
    return [*problem.get("visible_tests", []), *problem.get("hidden_tests", [])]


def test_generated_problems_keep_passing_their_own_tests_once_emoji_are_gone():
    data = _clean_generated({"problems": [
        {"filename": f"01-stars{STAR}.json", "content": STARS_PROBLEM},
        {"filename": "02-cheer.json", "content": CHEER_PROBLEM},
        {"filename": "03-built.json", "content": BUILT_PROBLEM},
    ]})
    problems = data["problems"]
    assert [p["content"]["id"] for p in problems] == ["stars", "cheer"]  # the broken one is dropped
    assert problems[0]["filename"] == "01-stars.json"
    for item in problems:
        assert grade_submission(item["content"]["solution_code"], _all_tests(item["content"]))["status"] == "PASS"


def test_save_local_problems_still_pass_their_own_tests(tmp_path, monkeypatch):
    # The originals pass, so any failure below comes from the clean-up.
    for problem in (STARS_PROBLEM, CHEER_PROBLEM):
        assert grade_submission(problem["solution_code"], _all_tests(problem))["status"] == "PASS"

    r = _save_local(tmp_path, monkeypatch, {
        "module": {"id": "emoji-code", "title": "Stars", "description": "Stars", "order": 1},
        "docs": [],
        "quiz_json": {"id": "q", "title": "Quiz", "questions": []},
        "problems": [{"filename": f"{n}.json", "content": p} for n, p in enumerate((STARS_PROBLEM, CHEER_PROBLEM, BUILT_PROBLEM))],
    })
    assert r.status_code == 200, r.text
    assert r.json()["skipped_problems"] == ["built"]
    folder = tmp_path / r.json()["module_id"] / "problems"
    assert sorted(p.name for p in folder.iterdir()) == ["cheer.json", "stars.json"]

    for name in ("stars", "cheer"):
        text = (folder / f"{name}.json").read_text(encoding="utf-8")
        assert not PROSE_RE.search(text), text
        saved = json.loads(text)
        assert grade_submission(saved["solution_code"], _all_tests(saved))["status"] == "PASS", name

    stars = json.loads((folder / "stars.json").read_text(encoding="utf-8"))
    # Prose is tidied; code only loses the symbol itself.
    assert (stars["title"], stars["description"], stars["concepts"], stars["hints"]) == (
        "Stars", "Print a star on each line", ["loops"], ["Use range"],
    )
    assert stars["solution_code"] == "for i in range(3):\n    print('', i)\n"
    assert stars["starter_code"] == "# print('', i)\n"

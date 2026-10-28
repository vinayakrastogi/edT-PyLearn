"""
Content validator: run it after writing or editing any module.

    python -m tools.check_content                 # all modules
    python -m tools.check_content module-1-...    # one module

Lesson conventions it enforces
  ```python            runnable example. If it is followed by an ```output block,
  ```output            the real stdout must match that block exactly (trailing spaces ignored).
  ```python-try        editable "Try it yourself" example (must run without error).
  Flags go on the fence line, e.g.  ```python stdin="Asha|7"  or  ```python expect-error
    no-run             never executed (network, GUI, ...).
    stdin="a|b"        feeds "a\\nb" to input() calls ("|" separates lines).
    expect-error       must fail; last traceback line must equal the last line of the
                       following ```output block.
"""
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

import frontmatter
import yaml

from app.services.execution import run_python_code
from app.services.grading import grade_submission

CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"
MIN_LESSONS = 7
MIN_LESSON_WORDS = 450
MIN_QUIZ_QUESTIONS = 20
REQUIRED_HEADINGS = ("## Common Mistakes", "## Try It Yourself", "## Recap")

FENCE = re.compile(
    r"^```(?P<lang>[\w-]+)(?P<meta>[^\n]*)\n(?P<body>.*?)^```",
    re.DOTALL | re.MULTILINE,
)


@dataclass
class Block:
    lang: str
    body: str
    comments: str
    start: int
    end: int


def parse_blocks(text: str) -> List[Block]:
    return [Block(m["lang"], m["body"], m["meta"], m.start(), m.end()) for m in FENCE.finditer(text)]


def _norm(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.strip().splitlines())


def check_lesson(path: Path) -> List[str]:
    errors: List[str] = []
    name = f"{path.parent.parent.name}/{path.name}"
    post = frontmatter.load(str(path))
    for key in ("id", "title", "order", "concepts"):
        if key not in post.metadata:
            errors.append(f"{name}: frontmatter missing '{key}'")
    if not post.metadata.get("concepts"):
        errors.append(f"{name}: needs at least one concept")

    body = post.content
    words = len(body.split())
    if words < MIN_LESSON_WORDS:
        errors.append(f"{name}: only {words} words (min {MIN_LESSON_WORDS})")
    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            errors.append(f"{name}: missing section '{heading}'")

    blocks = parse_blocks(body)
    if sum(1 for b in blocks if b.lang == "python") < 3:
        errors.append(f"{name}: needs at least 3 python examples")

    for i, block in enumerate(blocks):
        if block.lang not in ("python", "python-try"):
            continue
        if "no-run" in block.comments:
            continue
        line_no = body[: block.start].count("\n") + 1
        where = f"{name} (block at line ~{line_no})"
        stdin = ""
        m = re.search(r'stdin="([^"]*)"', block.comments)
        if m:
            stdin = m.group(1).replace("|", "\n") + "\n"
        elif "input(" in block.body:
            errors.append(f"{where}: uses input() but its fence has no stdin=... or no-run")
            continue

        result = run_python_code(block.body, stdin_input=stdin)
        expect_error = "expect-error" in block.comments
        nxt = blocks[i + 1] if i + 1 < len(blocks) else None
        has_output = (
            nxt is not None
            and nxt.lang == "output"
            and body[block.end : nxt.start].strip() == ""
        )

        if result.timed_out:
            errors.append(f"{where}: timed out")
            continue
        if expect_error:
            if not result.error:
                errors.append(f"{where}: expected an error but it ran fine")
            elif has_output:
                got = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ""
                got = re.sub(r"\. Did you mean:.*$", "", got)  # suggestion text varies by Python version
                want = nxt.body.strip().splitlines()[-1] if nxt.body.strip() else ""
                if not (got == want or got.startswith(want.rstrip(")"))):  # tolerate extra detail added by newer Pythons
                    errors.append(f"{where}: error line mismatch\n    shown:  {want}\n    actual: {got}")
            continue
        if result.error:
            errors.append(f"{where}: raised an error:\n    " + (result.stderr.strip().splitlines() or ["?"])[-1])
            continue
        if has_output and _norm(result.stdout) != _norm(nxt.body):
            errors.append(
                f"{where}: output mismatch\n--- shown ---\n{_norm(nxt.body)}\n--- actual ---\n{_norm(result.stdout)}"
            )
    return errors


def check_quiz(module_dir: Path, lesson_concepts: set) -> List[str]:
    errors: List[str] = []
    qfile = module_dir / "quiz.json"
    if not qfile.exists():
        return [f"{module_dir.name}: quiz.json missing"]
    data = json.loads(qfile.read_text())
    questions = data.get("questions", [])
    if len(questions) < MIN_QUIZ_QUESTIONS:
        errors.append(f"{module_dir.name}: quiz has {len(questions)} questions (min {MIN_QUIZ_QUESTIONS})")
    seen = set()
    for q in questions:
        qid = q.get("id", "?")
        where = f"{module_dir.name} quiz {qid}"
        if qid in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(qid)
        if not q.get("explanation"):
            errors.append(f"{where}: missing explanation")
        if q.get("type") == "mcq":
            opts = q.get("options", [])
            if len(opts) < 3 or not isinstance(q.get("correct_answer"), int) or not 0 <= q["correct_answer"] < len(opts):
                errors.append(f"{where}: bad options/correct_answer")
            if len(set(opts)) != len(opts):
                errors.append(f"{where}: duplicate options")
        elif q.get("type") == "true_false":
            if not isinstance(q.get("correct_answer"), bool):
                errors.append(f"{where}: correct_answer must be true/false")
        else:
            errors.append(f"{where}: unknown type {q.get('type')}")
        if not q.get("concepts"):
            errors.append(f"{where}: no concepts")
        for c in q.get("concepts", []):
            if c not in lesson_concepts:
                errors.append(f"{where}: concept '{c}' is not taught by any lesson in this module")
    return errors


def check_problems(module_dir: Path) -> List[str]:
    errors: List[str] = []
    pdir = module_dir / "problems"
    if not pdir.exists():
        return [f"{module_dir.name}: no problems folder"]
    for pf in sorted(pdir.glob("*.json")):
        data = json.loads(pf.read_text())
        where = f"{module_dir.name}/problems/{pf.name}"
        if data.get("id") != pf.stem:
            errors.append(f"{where}: id '{data.get('id')}' does not match filename")
        if not data.get("solution_code"):
            errors.append(f"{where}: no solution_code")
            continue
        tests = [{"is_hidden": False, **t} for t in data.get("visible_tests", [])] + [
            {"is_hidden": True, **t} for t in data.get("hidden_tests", [])
        ]
        if not tests:
            errors.append(f"{where}: no tests")
            continue
        res = grade_submission(data["solution_code"], tests)
        if res["status"] != "PASS":
            bad = [t for t in res["test_results"] if not t["passed"]]
            errors.append(f"{where}: reference solution fails {len(bad)}/{res['total_count']} tests ({res['stderr'].strip()[-120:]})")
        starter = data.get("starter_code", "")
        if starter and data["solution_code"].strip() == starter.strip():
            errors.append(f"{where}: starter_code equals the solution")
    return errors


def check_module(module_dir: Path) -> List[str]:
    errors: List[str] = []
    meta_file = module_dir / "module.yaml"
    if not meta_file.exists():
        return [f"{module_dir.name}: module.yaml missing"]
    meta = yaml.safe_load(meta_file.read_text())
    if meta.get("id") != module_dir.name:
        errors.append(f"{module_dir.name}: module.yaml id '{meta.get('id')}' != folder name")
    if meta.get("is_generative"):
        return errors

    lessons = sorted((module_dir / "docs").glob("*.md")) if (module_dir / "docs").exists() else []
    if len(lessons) < MIN_LESSONS:
        errors.append(f"{module_dir.name}: {len(lessons)} lessons (min {MIN_LESSONS})")

    concepts: set = set()
    orders: List[int] = []
    ids: List[str] = []
    for lf in lessons:
        errors += check_lesson(lf)
        meta_l = frontmatter.load(str(lf)).metadata
        concepts.update(meta_l.get("concepts", []))
        orders.append(meta_l.get("order"))
        ids.append(meta_l.get("id"))
    if orders != list(range(1, len(lessons) + 1)):
        errors.append(f"{module_dir.name}: lesson order values must be 1..{len(lessons)}, got {orders}")
    if len(set(ids)) != len(ids):
        errors.append(f"{module_dir.name}: duplicate lesson ids")

    errors += check_quiz(module_dir, concepts)
    errors += check_problems(module_dir)
    return errors


def main(argv: List[str]) -> int:
    targets = [CONTENT_DIR / a for a in argv] if argv else sorted(
        d for d in CONTENT_DIR.iterdir() if d.is_dir() and (d / "module.yaml").exists()
    )
    total = 0
    for d in targets:
        errs = check_module(d)
        status = "OK " if not errs else "FAIL"
        print(f"[{status}] {d.name}")
        for e in errs:
            print("   -", e)
        total += len(errs)
    print(f"\n{total} problem(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

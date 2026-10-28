"""
Author coding problems in Python; expected outputs are computed by running the reference
solution, so a problem can never ship with a wrong answer key.

    from tools.problem_builder import build

    build("module-1-introduction-to-python", [
        dict(id="area", title="Rectangle Area", kind="function", concepts=["operators"],
             description="...", starter="def area(w, h):\\n    pass\\n",
             solution="def area(w, h):\\n    return w * h\\n",
             visible=[[3, 4]], hidden=[[10, 2], [0, 5]]),
    ])

kind="function": tests are argument lists (a bare value is a single argument); the function's
                 return value is printed and compared.
kind="program":  tests are stdin strings; the whole program's stdout is compared.
kind="driver":   tests are driver scripts appended after the learner's code (for classes,
                 files, anything stateful); the driver's stdout is compared.
Test items may be (value, hint) tuples in "visible" to add a label shown to learners.
"""
import json
from pathlib import Path
from typing import List

from app.services.execution import build_test_harness, run_python_code

CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"


def _run(kind: str, solution: str, test):
    if kind == "driver":
        res = run_python_code(solution + "\n\n# --- driver ---\n" + test + "\n")
    elif kind == "program":
        res = run_python_code(solution, stdin_input=test)
    else:
        res = run_python_code(build_test_harness(solution, test, ""))
    if res.error or res.timed_out:
        raise RuntimeError(f"Reference solution crashed on {test!r}:\n{res.stderr}")
    out = res.stdout
    return out.strip() if kind == "function" else "\n".join(l.rstrip() for l in out.strip().splitlines())


def _make_test(kind: str, solution: str, test) -> dict:
    expected = _run(kind, solution, test)
    if kind == "driver":
        return {"driver": test, "expected": expected}
    if kind == "program":
        return {"stdin": test, "expected": expected}
    return {"input": test, "expected": expected}


def build(module_id: str, problems: List[dict]) -> None:
    out_dir = CONTENT_DIR / module_id / "problems"
    out_dir.mkdir(parents=True, exist_ok=True)
    for n, p in enumerate(problems, start=1):
        kind = p.get("kind", "function")
        pid = f"{n:02d}-{p['id']}"
        data = {
            "id": pid,
            "title": p["title"],
            "type": kind,
            "difficulty": p.get("difficulty", "easy"),
            "description": p["description"].strip(),
            "starter_code": p["starter"],
            "concepts": p["concepts"],
            "visible_tests": [_make_test(kind, p["solution"], t) for t in p["visible"]],
            "hidden_tests": [_make_test(kind, p["solution"], t) for t in p.get("hidden", [])],
            "hints": p.get("hints", []),
            "solution_code": p["solution"],
        }
        (out_dir / f"{pid}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"  wrote {pid} ({len(data['visible_tests'])}+{len(data['hidden_tests'])} tests)")

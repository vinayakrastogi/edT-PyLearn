"""
Recompute every `expected` value in a module's problems by running its reference
solution, so stored answers can never drift from the code.

    python -m tools.regen_expected module-1-introduction-to-python [--write]

Without --write it only reports what would change. Problems whose reference solution
crashes are listed so they can be rewritten by hand.
"""
import json
import sys
from pathlib import Path

from app.services.execution import build_test_harness, run_python_code

CONTENT_DIR = Path(__file__).resolve().parents[2] / "content"


def actual_output(solution: str, test: dict):
    if "driver" in test:
        res = run_python_code(solution + "\n\n" + test["driver"] + "\n")
        return None if (res.error or res.timed_out) else "\n".join(l.rstrip() for l in res.stdout.strip().splitlines())
    if "stdin" in test:
        res = run_python_code(solution, stdin_input=str(test["stdin"]))
        return None if (res.error or res.timed_out) else "\n".join(l.rstrip() for l in res.stdout.strip().splitlines())
    res = run_python_code(build_test_harness(solution, test.get("input"), ""))
    return None if (res.error or res.timed_out) else res.stdout.strip()


def main(argv):
    write = "--write" in argv
    for name in [a for a in argv if not a.startswith("--")]:
        for pf in sorted((CONTENT_DIR / name / "problems").glob("*.json")):
            data = json.loads(pf.read_text())
            changed, broken = 0, 0
            for key in ("visible_tests", "hidden_tests"):
                for t in data.get(key, []):
                    got = actual_output(data["solution_code"], t)
                    if got is None:
                        broken += 1
                    elif got != str(t.get("expected", "")).strip():
                        changed += 1
                        t["expected"] = got
            flag = "BROKEN " if broken else ("updated" if changed else "ok     ")
            print(f"{flag} {name}/{pf.name} (changed={changed}, crashed={broken})")
            if write and changed and not broken:
                pf.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])

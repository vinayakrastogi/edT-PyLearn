"""Check lesson files only (faster than the full validator):  python -m tools.lint_lessons module-2-... [more]"""
import sys
from pathlib import Path
from tools.check_content import CONTENT_DIR, check_lesson

bad = 0
for m in sys.argv[1:]:
    for f in sorted((CONTENT_DIR / m / "docs").glob("*.md")):
        errs = check_lesson(f)
        bad += len(errs)
        print(("OK   " if not errs else "FAIL ") + f.name)
        for e in errs:
            print("   -", e)
sys.exit(1 if bad else 0)

"""
Fill placeholder output blocks with real program output (then read them to make sure
they show what the lesson intends!).

    python -m tools.fill_outputs path/to/lesson.md

An ```output block whose body is just `?` is replaced by the real stdout of the python
block above it (or the last traceback line for `expect-error` blocks).
"""
import re
import sys
from pathlib import Path

from app.services.execution import run_python_code
from tools.check_content import parse_blocks


def fill(path: Path) -> int:
    text = path.read_text()
    blocks = parse_blocks(text)
    out, cursor, filled = [], 0, 0
    for i, b in enumerate(blocks):
        nxt = blocks[i + 1] if i + 1 < len(blocks) else None
        if b.lang in ("python", "python-try") and nxt and nxt.lang == "output" and nxt.body.strip() == "?":
            m = re.search(r'stdin="([^"]*)"', b.comments)
            res = run_python_code(b.body, stdin_input=(m.group(1).replace("|", "\n") + "\n") if m else "")
            if "expect-error" in b.comments:
                actual = (res.stderr.strip().splitlines() or [""])[-1]
                actual = re.sub(r"\. Did you mean:.*$", "", actual)
            else:
                actual = "\n".join(l.rstrip() for l in res.stdout.rstrip("\n").splitlines())
            out.append(text[cursor:nxt.start])
            out.append(f"```output\n{actual}\n```")
            cursor = nxt.end
            filled += 1
    out.append(text[cursor:])
    if filled:
        path.write_text("".join(out))
    return filled


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(p, "filled", fill(Path(p)))

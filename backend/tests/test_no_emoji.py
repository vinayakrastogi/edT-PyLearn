"""
The project uses SVG icons (lucide-react + our own logo), never emoji. This test keeps it that way.

Run `python tests/test_no_emoji.py` from backend/ to list every offending character with its location.

Two strictness levels:
  * code (frontend/src, backend/app, backend/tests, backend/tools, frontend/index.html,
    frontend/public, submission/ scripts): no emoji, no pictographic symbols (check marks, stars,
    play triangles...) and no arrow characters either; the UI draws those with icons.
  * prose (lesson content, Markdown docs and the Word documents in submission/): no emoji or
    pictographic symbols, but plain typographic arrows such as "Input -> Process" written with
    U+2192 are allowed.
"""
import html
import re
import sys
import zipfile
from pathlib import Path
from typing import Iterator, List, Tuple

ROOT = Path(__file__).resolve().parents[2]


def _span(lo: int, hi: int) -> str:
    return f"{chr(lo)}-{chr(hi)}"


# Built from code points, so this file does not trip its own check.
_PICTOGRAPHIC = "".join(
    [
        _span(0x1F000, 0x1FAFF),  # emoji, pictographs, symbols & pictographs extended
        _span(0x2600, 0x27BF),  # misc symbols + dingbats (check marks, stars, warning signs)
        _span(0x2B00, 0x2BFF),  # misc symbols and arrows (stars, big arrows)
        _span(0x2300, 0x23FF),  # misc technical (stopwatch, hourglass)
        _span(0x25A0, 0x25FF),  # geometric shapes (play triangles, diamonds)
        "".join(map(chr, (0xFE0E, 0xFE0F, 0x200D, 0x20E3))),  # variation selectors, zero width joiner, keycap
        "".join(map(chr, (0x2122, 0x2139, 0x24C2, 0x3030, 0x303D, 0x3297, 0x3299))),  # letterlike / enclosed emoji
    ]
)
_ARROWS = _span(0x2190, 0x21FF)

CODE_RE = re.compile(f"[{_PICTOGRAPHIC}{_ARROWS}]")
PROSE_RE = re.compile(f"[{_PICTOGRAPHIC}]")

SKIP_DIRS = {"node_modules", "venv", ".venv", "__pycache__", "dist", ".git", ".pytest_cache"}
CODE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".py", ".html", ".css", ".svg", ".json", ".yaml", ".yml", ".md", ".txt"}
PROSE_EXTS = {".md", ".yaml", ".yml", ".json", ".txt"}

CODE_TARGETS = [
    ROOT / "frontend" / "src",
    ROOT / "frontend" / "public",
    ROOT / "frontend" / "index.html",
    ROOT / "backend" / "app",
    ROOT / "backend" / "tests",
    ROOT / "backend" / "tools",
    ROOT / "submission",  # make.js builds the submission document
]
PROSE_TARGETS = [ROOT / "content"] + sorted(ROOT.glob("*.md")) + sorted((ROOT / "submission").glob("*.docx"))

_DOCX_PARAGRAPH_END = re.compile(r"</w:p>")
_XML_TAG = re.compile(r"<[^>]+>")


def _read_text(path: Path) -> str:
    """The file's text; for a Word document, the text of its parts with one paragraph per line."""
    if path.suffix != ".docx":
        return path.read_text(encoding="utf-8")
    try:
        with zipfile.ZipFile(path) as docx:
            parts = [docx.read(n).decode("utf-8") for n in docx.namelist() if n.startswith("word/") and n.endswith(".xml")]
    except (zipfile.BadZipFile, KeyError) as exc:
        raise OSError(f"{path} is not a readable Word document") from exc
    return "\n".join(html.unescape(_XML_TAG.sub("", _DOCX_PARAGRAPH_END.sub("\n", xml))) for xml in parts)


def _files(target: Path, exts: set) -> Iterator[Path]:
    if target.is_file():
        yield target
        return
    if not target.exists():
        return
    for path in sorted(target.rglob("*")):
        if path.is_file() and path.suffix in exts and not (set(path.relative_to(ROOT).parts) & SKIP_DIRS):
            yield path


def find_offenders() -> List[Tuple[str, int, str, str]]:
    found = []
    for targets, exts, pattern in ((CODE_TARGETS, CODE_EXTS, CODE_RE), (PROSE_TARGETS, PROSE_EXTS, PROSE_RE)):
        for target in targets:
            for path in _files(target, exts):
                try:
                    text = _read_text(path)
                except (UnicodeDecodeError, OSError):
                    continue
                for lineno, line in enumerate(text.splitlines(), 1):
                    for m in pattern.finditer(line):
                        found.append((str(path.relative_to(ROOT)), lineno, f"U+{ord(m.group()):04X}", line.strip()[:120]))
    return found


def test_no_emoji_anywhere():
    offenders = find_offenders()
    report = "\n".join(f"{f}:{n} {cp}  {line}" for f, n, cp, line in offenders[:60])
    assert not offenders, f"{len(offenders)} emoji/pictographic characters found (use lucide icons instead):\n{report}"


if __name__ == "__main__":
    rows = find_offenders()
    for f, n, cp, line in rows:
        print(f"{f}:{n} {cp}  {line}")
    print(f"{len(rows)} offending characters")
    sys.exit(1 if rows else 0)

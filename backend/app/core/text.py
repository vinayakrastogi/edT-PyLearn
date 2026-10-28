"""
Text clean-up for content we did not write ourselves (AI-generated lessons, quizzes and problems).

PyLearn draws every symbol with SVG icons, so emoji and pictographic characters never belong in
saved content. The character ranges match the prose rules in tests/test_no_emoji.py: emoji,
pictographs, dingbats, misc technical and geometric shapes are removed; plain typographic arrows
are kept.
"""
import re
from typing import Any, Callable


def _span(lo: int, hi: int) -> str:
    return f"{chr(lo)}-{chr(hi)}"


# Built from code points, so this file does not trip the emoji check itself.
_PICTOGRAPHIC = "".join(
    [
        _span(0x1F000, 0x1FAFF),  # emoji, pictographs, symbols & pictographs extended
        _span(0x2600, 0x27BF),  # misc symbols + dingbats
        _span(0x2B00, 0x2BFF),  # misc symbols and arrows (stars, big arrows)
        _span(0x2300, 0x23FF),  # misc technical (stopwatch, hourglass)
        _span(0x25A0, 0x25FF),  # geometric shapes
        "".join(map(chr, (0xFE0E, 0xFE0F, 0x200D, 0x20E3))),  # variation selectors, zero width joiner, keycap
        "".join(map(chr, (0x2122, 0x2139, 0x24C2, 0x3030, 0x303D, 0x3297, 0x3299))),  # letterlike / enclosed emoji
    ]
)
_RUN = f"[{_PICTOGRAPHIC}]+"

# "Well done! <emoji>" at the end of a line: drop the emoji and the spaces before it.
_AT_LINE_END = re.compile(f"[ \t]*{_RUN}[ \t]*$", re.MULTILINE)
# "<emoji> Intro" or "a <emoji> b": drop the emoji and one space after it, so no double space is left.
_ANYWHERE = re.compile(f"{_RUN}[ \t]?")
# The characters alone, for delete_pictographs.
_ONLY = re.compile(_RUN)


def strip_pictographs(text: str) -> str:
    """Remove emoji and pictographic symbols from prose, tidying the space each one leaves behind."""
    if not text:
        return text
    return _ANYWHERE.sub("", _AT_LINE_END.sub("", text))


def delete_pictographs(text: str) -> str:
    """Remove emoji and pictographic symbols and nothing else: no space is touched.

    For code and program input/output. A string literal in a solution and the output it prints lose
    exactly the same characters, so the two stay in step (strip_pictographs would tidy the space
    around them differently in each).
    """
    if not text:
        return text
    return _ONLY.sub("", text)


def _map_strings(value: Any, clean: Callable[[str], str]) -> Any:
    if isinstance(value, str):
        return clean(value)
    if isinstance(value, list):
        return [_map_strings(v, clean) for v in value]
    if isinstance(value, dict):
        return {k: _map_strings(v, clean) for k, v in value.items()}
    return value


def strip_pictographs_deep(value: Any) -> Any:
    """strip_pictographs applied to every string value inside nested dicts and lists."""
    return _map_strings(value, strip_pictographs)


def delete_pictographs_deep(value: Any) -> Any:
    """delete_pictographs applied to every string value inside nested dicts and lists."""
    return _map_strings(value, delete_pictographs)

"""Utilities for reading LSP-like params used by handlers and tests."""

from typing import Any, Optional, Tuple


def get_attr(params: Any, name: str, default: Any = None) -> Any:
    if params is None:
        return default
    if isinstance(params, dict):
        return params.get(name, default)
    return getattr(params, name, default)


def get_position(params: Any) -> Tuple[int, int]:
    position = get_attr(params, "position", {})
    if isinstance(position, dict):
        return int(position.get("line", 0)), int(position.get("character", 0))
    return int(get_attr(position, "line", 0)), int(get_attr(position, "character", 0))


def get_text(params: Any) -> Optional[str]:
    text = get_attr(params, "text")
    if text is not None:
        return str(text)

    text_document = get_attr(params, "text_document")
    text = get_attr(text_document, "text")
    if text is not None:
        return str(text)

    return None


def word_at_position(text: str, line_number: int, character: int) -> str:
    lines = text.splitlines()
    if line_number < 0 or line_number >= len(lines):
        return ""

    line = lines[line_number]
    character = max(0, min(character, len(line)))
    start = character
    while start > 0 and not line[start - 1].isspace():
        start -= 1
    end = character
    while end < len(line) and not line[end].isspace():
        end += 1
    return line[start:end].strip(",{}")


def strip_inline_comment(line: str) -> str:
    return line.split("!", 1)[0].strip()

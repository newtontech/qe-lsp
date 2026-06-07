"""Hover handler."""

from typing import Any, Optional

from lsprotocol import types

from qe_lsp.constants import QE_HOVER_DOCS
from qe_lsp.text import get_position, get_text, word_at_position


def hover(params: Any) -> Optional[types.Hover]:
    text = get_text(params)
    if not text:
        return None

    line_number, character = get_position(params)
    keyword = word_at_position(text, line_number, character).upper()
    if keyword not in QE_HOVER_DOCS:
        return None

    return types.Hover(
        contents=types.MarkupContent(
            kind=types.MarkupKind.Markdown,
            value=f"**{keyword}**\n\n{QE_HOVER_DOCS[keyword]}",
        )
    )

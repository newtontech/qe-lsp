"""Hover handler."""

from typing import Any, Optional

from lsprotocol import types

from qe_lsp.features.navigation import get_hover
from qe_lsp.text import get_position, get_text


def hover(params: Any) -> Optional[types.Hover]:
    """Handle a textDocument/hover request.

    Returns hover documentation for the symbol under the cursor, including
    section-level docs and per-namelist parameter descriptions.
    """
    text = get_text(params)
    if not text:
        return None

    line_number, character = get_position(params)
    return get_hover(text, line_number, character)

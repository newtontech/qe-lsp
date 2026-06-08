"""Definition handler for textDocument/definition requests."""

from typing import Any, Optional

from lsprotocol import types

from qe_lsp.features.navigation import get_definition
from qe_lsp.text import get_position, get_text


def definition(params: Any) -> Optional[types.Location]:
    """Handle a textDocument/definition request.

    Returns the location where the symbol under the cursor is defined.
    """
    text = get_text(params)
    if not text:
        return None

    line_number, character = get_position(params)
    uri = _get_uri(params)

    return get_definition(text, line_number, character, uri)


def _get_uri(params: Any) -> str:
    """Extract the document URI from LSP params."""
    text_document = getattr(params, "text_document", None)
    if text_document is None:
        return ""
    return getattr(text_document, "uri", "")

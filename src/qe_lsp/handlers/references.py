"""References handler for textDocument/references requests."""

from typing import Any, List

from lsprotocol import types

from qe_lsp.features.navigation import get_references
from qe_lsp.text import get_position, get_text


def references(params: Any) -> List[types.Location]:
    """Handle a textDocument/references request.

    Returns all locations where the symbol under the cursor is referenced.
    """
    text = get_text(params)
    if not text:
        return []

    line_number, character = get_position(params)
    uri = _get_uri(params)
    include_declaration = _include_declaration(params)

    return get_references(text, line_number, character, uri, include_declaration)


def _get_uri(params: Any) -> str:
    """Extract the document URI from LSP params."""
    text_document = getattr(params, "text_document", None)
    if text_document is None:
        return ""
    return getattr(text_document, "uri", "")


def _include_declaration(params: Any) -> bool:
    """Extract includeDeclaration from ReferenceContext."""
    context = getattr(params, "context", None)
    if context is None:
        return True
    return getattr(context, "include_declaration", True)

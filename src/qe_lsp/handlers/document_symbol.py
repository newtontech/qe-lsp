"""Document symbol handler for textDocument/documentSymbol requests."""

from typing import Any, List

from lsprotocol import types

from qe_lsp.features.navigation import get_document_symbols
from qe_lsp.text import get_text


def document_symbol(params: Any) -> List[types.DocumentSymbol]:
    """Handle a textDocument/documentSymbol request.

    Returns a hierarchical list of symbols in the document.
    """
    text = get_text(params)
    if not text:
        return []

    return get_document_symbols(text)

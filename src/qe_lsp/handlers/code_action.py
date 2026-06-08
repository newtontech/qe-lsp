"""Code action handler for textDocument/codeAction requests."""

from typing import Any

from lsprotocol.types import CodeAction, CodeActionParams

from qe_lsp.features.code_actions import CodeActionProvider

_provider = CodeActionProvider()


def code_action(params: Any) -> list[CodeAction]:
    """Handle a textDocument/codeAction request.

    Parameters
    ----------
    params:
        LSP CodeActionParams (or a compatible dict-like object).
    """
    # Extract diagnostics from the params
    diagnostics = getattr(params, "diagnostics", []) or []

    # Try to get the document text from the params
    text_document = getattr(params, "text_document", None)
    if text_document is None:
        return []

    uri = getattr(text_document, "uri", "")

    # The handler is called after the server stores the document text
    # in lsp_server.documents.  When invoked outside of the server
    # context (e.g. in unit tests), fall back to an empty string.
    try:
        from qe_lsp.server import server as _server

        source = _server.documents.get(uri, "")  # type: ignore[attr-defined]
    except (ImportError, AttributeError):
        source = ""

    return _provider.get_code_actions(source, diagnostics)

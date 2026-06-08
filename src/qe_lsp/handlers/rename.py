"""LSP handlers for ``textDocument/prepareRename`` and ``textDocument/rename``."""

from __future__ import annotations

from typing import Any, Optional

from lsprotocol.types import (
    Position,
    Range,
    WorkspaceEdit,
)

from qe_lsp.features.rename import RenameProvider
from qe_lsp.text import get_attr, get_text

_provider = RenameProvider()


def prepare_rename(params: Any) -> Optional[Range]:
    """Handle ``textDocument/prepareRename``.

    Returns the ``Range`` of the renamable symbol at the cursor, or
    ``None`` if the position cannot be renamed.
    """
    text = _get_document_text(params)
    if text is None:
        return None

    line, character = _get_position(params)
    return _provider.prepare_rename(text, line, character)


def rename(params: Any) -> Optional[WorkspaceEdit]:
    """Handle ``textDocument/rename``.

    Returns a ``WorkspaceEdit`` that applies the rename across the
    document, or ``None`` if the target cannot be renamed.
    """
    text = _get_document_text(params)
    if text is None:
        return None

    line, character = _get_position(params)

    position = get_attr(params, "position", {})
    new_name = get_attr(position, "new_name", "") if isinstance(position, dict) else ""
    if not new_name:
        # Try alternate param layouts used by some LSP clients.
        new_name = get_attr(params, "new_name", "")

    uri = _get_uri(params)
    return _provider.rename(text, uri, line, character, new_name)


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------


def _get_position(params: Any) -> tuple[int, int]:
    position = get_attr(params, "position", {})
    if isinstance(position, dict):
        return int(position.get("line", 0)), int(position.get("character", 0))
    return int(get_attr(position, "line", 0)), int(get_attr(position, "character", 0))


def _get_document_text(params: Any) -> Optional[str]:
    text = get_text(params)
    if text is not None:
        return text

    # Fall back to the server's document cache when available.
    uri = _get_uri(params)
    if uri:
        try:
            from qe_lsp.server import server as _server

            return _server.documents.get(uri, None)  # type: ignore[attr-defined]
        except (ImportError, AttributeError):
            pass

    return None


def _get_uri(params: Any) -> str:
    text_document = get_attr(params, "text_document", None)
    if text_document is None:
        text_document = get_attr(params, "textDocument", None)
    if text_document is None:
        return ""
    return get_attr(text_document, "uri", "")

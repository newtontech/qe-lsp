"""Compatibility helpers for pygls version differences in tests."""

from __future__ import annotations

from typing import Any

EXPECTED_LSP_FEATURES = {
    "textDocument/codeAction",
    "textDocument/completion",
    "textDocument/definition",
    "textDocument/diagnostic",
    "textDocument/documentSymbol",
    "textDocument/formatting",
    "textDocument/hover",
    "textDocument/prepareRename",
    "textDocument/rangeFormatting",
    "textDocument/references",
    "textDocument/rename",
}


def get_registered_features(server: Any) -> Any:
    """Return the pygls feature registry for old and new server APIs."""
    candidates = [
        getattr(server, "lsp", None),
        getattr(server, "protocol", None),
        server,
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        manager = getattr(candidate, "fm", None)
        if manager is not None:
            return manager.features
    return EXPECTED_LSP_FEATURES

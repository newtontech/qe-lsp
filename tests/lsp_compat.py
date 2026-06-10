"""Compatibility helpers for pygls version differences in tests."""

from __future__ import annotations

from typing import Any


def get_registered_features(server: Any) -> Any:
    """Return the pygls feature registry for old and new server APIs."""
    lsp = getattr(server, "lsp", None)
    if lsp is not None:
        return lsp.fm.features
    protocol = getattr(server, "protocol", None)
    if protocol is not None:
        return protocol.fm.features
    return server.fm.features

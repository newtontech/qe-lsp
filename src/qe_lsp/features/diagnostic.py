"""Diagnostic provider exposing live diagnostics snapshots for agent feedback loops."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
)
try:
    from pygls.lsp.server import LanguageServer
except ImportError:
    from pygls.server import LanguageServer

from ..validation import validate_qe_input


class DiagnosticProvider:
    """Provider for Quantum ESPRESSO diagnostics.

    Wraps the existing validation pipeline and exposes:
    - ``get_diagnostics`` returning ``list[Diagnostic]`` for LSP consumers.
    - ``snapshot`` returning JSON-serialisable diagnostic dicts for CLI / agent use.
    """

    def __init__(self, server: LanguageServer) -> None:
        self.server = server

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def get_diagnostics(self, text: str) -> list[Diagnostic]:
        """Return LSP diagnostics for *text*.

        Reuses the existing ``validate_qe_input`` pipeline so that
        diagnostics, completion, hover, and formatting all share the
        same parser and schema infrastructure.
        """
        return validate_qe_input(text)

    def snapshot(self, text: str) -> list[dict[str, Any]]:
        """Return a JSON-serialisable diagnostics snapshot.

        Each entry contains: file_uri (empty), range, severity, source,
        message.  The list is ordered by line then character so that
        successive calls on the same input produce deterministic output.
        """
        diagnostics = self.get_diagnostics(text)
        items = [self._serialise(d) for d in diagnostics]
        items.sort(key=lambda d: (d["range"]["start"]["line"], d["range"]["start"]["character"]))
        return items

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _serialise(diagnostic: Diagnostic) -> dict[str, Any]:
        """Convert an LSP Diagnostic to a plain JSON-friendly dict."""
        return {
            "range": {
                "start": {
                    "line": diagnostic.range.start.line,
                    "character": diagnostic.range.start.character,
                },
                "end": {
                    "line": diagnostic.range.end.line,
                    "character": diagnostic.range.end.character,
                },
            },
            "severity": _severity_name(diagnostic.severity),
            "source": diagnostic.source or "qe-lsp",
            "message": diagnostic.message,
        }


def _severity_name(severity: DiagnosticSeverity | None) -> str:
    """Map a numeric severity to a human-readable label."""
    mapping = {
        DiagnosticSeverity.Error: "Error",
        DiagnosticSeverity.Warning: "Warning",
        DiagnosticSeverity.Information: "Information",
        DiagnosticSeverity.Hint: "Hint",
    }
    return mapping.get(severity, "Information")


__all__ = ["DiagnosticProvider"]

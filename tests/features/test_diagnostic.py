"""Tests for the DiagnosticProvider live diagnostics snapshot."""

import json
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pygls.lsp.server import LanguageServer
else:
    try:
        from pygls.lsp.server import LanguageServer
    except ImportError:
        from pygls.server import LanguageServer

from qe_lsp.features.diagnostic import DiagnosticProvider


@pytest.fixture
def provider() -> DiagnosticProvider:
    """Create a DiagnosticProvider backed by a minimal LanguageServer."""
    server = LanguageServer("test-qe-lsp", "0.1.0")
    return DiagnosticProvider(server)


# ------------------------------------------------------------------
# get_diagnostics
# ------------------------------------------------------------------


class TestGetDiagnostics:
    """Tests for DiagnosticProvider.get_diagnostics."""

    def test_empty_input_returns_empty(self, provider: DiagnosticProvider) -> None:
        diagnostics = provider.get_diagnostics("")
        assert diagnostics == []

    def test_valid_input_returns_empty(self, provider: DiagnosticProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n"
        assert provider.get_diagnostics(text) == []

    def test_unclosed_namelist_is_error(self, provider: DiagnosticProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n"
        diagnostics = provider.get_diagnostics(text)
        assert len(diagnostics) == 1
        assert diagnostics[0].severity is not None
        # DiagnosticSeverity.Error == 1
        assert diagnostics[0].severity.value == 1
        assert "Unclosed" in diagnostics[0].message

    def test_warning_severity(self, provider: DiagnosticProvider) -> None:
        text = "&SYSTEM\nibrav = 1\nA = 7.5\n/\n"
        diagnostics = provider.get_diagnostics(text)
        assert len(diagnostics) == 1
        # DiagnosticSeverity.Warning == 2
        assert diagnostics[0].severity is not None
        assert diagnostics[0].severity.value == 2
        assert "ignored when ibrav is not 0" in diagnostics[0].message

    def test_ibrav_zero_without_cell_parameters(self, provider: DiagnosticProvider) -> None:
        text = "&SYSTEM\nibrav = 0\n/\n"
        diagnostics = provider.get_diagnostics(text)
        assert len(diagnostics) == 1
        assert "CELL_PARAMETERS" in diagnostics[0].message

    def test_duplicate_parameter(self, provider: DiagnosticProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\ncalculation = 'nscf'\n/\n"
        diagnostics = provider.get_diagnostics(text)
        assert len(diagnostics) == 1
        assert "Duplicate" in diagnostics[0].message

    def test_source_is_qe_lsp(self, provider: DiagnosticProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n"
        diagnostics = provider.get_diagnostics(text)
        assert diagnostics[0].source == "qe-lsp"


# ------------------------------------------------------------------
# snapshot (JSON-serialisable)
# ------------------------------------------------------------------


class TestSnapshot:
    """Tests for DiagnosticProvider.snapshot."""

    def test_empty_input_snapshot(self, provider: DiagnosticProvider) -> None:
        assert provider.snapshot("") == []

    def test_valid_input_snapshot(self, provider: DiagnosticProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n"
        assert provider.snapshot(text) == []

    def test_snapshot_is_json_serialisable(self, provider: DiagnosticProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n"
        items = provider.snapshot(text)
        serialised = json.dumps(items)
        assert isinstance(serialised, str)
        round_tripped = json.loads(serialised)
        assert round_tripped == items

    def test_snapshot_contains_expected_keys(self, provider: DiagnosticProvider) -> None:
        text = "&SYSTEM\nibrav = 0\n/\n"
        items = provider.snapshot(text)
        assert len(items) == 1
        item = items[0]
        assert "range" in item
        assert "severity" in item
        assert "source" in item
        assert "message" in item
        assert "start" in item["range"]
        assert "end" in item["range"]

    def test_snapshot_severity_is_string(self, provider: DiagnosticProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n"
        items = provider.snapshot(text)
        assert items[0]["severity"] == "Error"

    def test_snapshot_deterministic_ordering(self, provider: DiagnosticProvider) -> None:
        """Two calls with the same text must produce the same output."""
        text = "&SYSTEM\nibrav = 0\n/\n&CONTROL\ncalculation = 'scf'\n"
        first = provider.snapshot(text)
        second = provider.snapshot(text)
        assert first == second

    def test_snapshot_warning_severity_is_string(self, provider: DiagnosticProvider) -> None:
        text = "&SYSTEM\nibrav = 1\nA = 7.5\n/\n"
        items = provider.snapshot(text)
        assert items[0]["severity"] == "Warning"

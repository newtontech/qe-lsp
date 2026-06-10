from lsprotocol import types
from qe_lsp import __version__
from qe_lsp.constants import QE_KEYWORDS
from qe_lsp.handlers.completion import completion
from qe_lsp.handlers.diagnostic import diagnostic
from qe_lsp.handlers.hover import hover
from qe_lsp.server import create_server, server
from tests.lsp_compat import get_registered_features


class Params:
    def __init__(self, text, line=0, character=0):
        self.text = text
        self.position = {"line": line, "character": character}


def test_import():
    """Test that the package exposes its version."""
    assert __version__ == "0.1.0"


def test_completion_returns_qe_keywords():
    """Completion should expose common Quantum ESPRESSO input sections."""
    items = completion(None)

    labels = {item.label for item in items}
    assert set(QE_KEYWORDS).issubset(labels)
    assert "&CONTROL" in labels
    assert "&SYSTEM" in labels
    assert "ATOMIC_POSITIONS" in labels
    assert "K_POINTS" in labels
    assert all(item.kind == types.CompletionItemKind.Keyword for item in items)
    assert all(item.detail == "Quantum ESPRESSO input keyword" for item in items)


def test_hover_returns_markdown_documentation_for_position():
    """Hover should return documentation for the symbol under the cursor."""
    result = hover(Params("&SYSTEM\n/", character=3))

    assert isinstance(result, types.Hover)
    assert isinstance(result.contents, types.MarkupContent)
    assert result.contents.kind == types.MarkupKind.Markdown
    assert "&SYSTEM" in result.contents.value
    assert "System definition" in result.contents.value


def test_hover_returns_none_for_unknown_content():
    """Hover should not show misleading documentation for unknown content."""
    assert hover(Params("unknown_keyword", character=4)) is None


def test_diagnostic_returns_empty_for_valid_input():
    """A minimal closed namelist should not produce diagnostics."""
    assert diagnostic(Params("&CONTROL\n/\n")) == []


def test_diagnostic_allows_inline_comments_after_namelist_end():
    """Comments after '/' should not hide a valid namelist terminator."""
    assert diagnostic(Params("&CONTROL\n/ ! done\n")) == []


def test_diagnostic_reports_unclosed_namelist():
    """An unclosed namelist should produce a diagnostic."""
    diagnostics = diagnostic(Params("&CONTROL\ncalculation = 'scf'\n"))

    assert len(diagnostics) == 1
    assert diagnostics[0].severity == types.DiagnosticSeverity.Error
    assert "Unclosed namelist" in diagnostics[0].message
    assert diagnostics[0].range.start.line == 0


def test_diagnostic_reports_ibrav_zero_without_cell_parameters():
    """ibrav = 0 requires an explicit CELL_PARAMETERS card."""
    diagnostics = diagnostic(Params("&SYSTEM\nibrav = 0\n/\n"))

    assert len(diagnostics) == 1
    assert diagnostics[0].severity == types.DiagnosticSeverity.Error
    assert "CELL_PARAMETERS" in diagnostics[0].message


def test_diagnostic_warns_when_lattice_constants_ignored():
    """A, B, C, and cos* are ignored when ibrav is not zero."""
    diagnostics = diagnostic(Params("&SYSTEM\nibrav = 1\nA = 7.5\n/\n"))

    assert len(diagnostics) == 1
    assert diagnostics[0].severity == types.DiagnosticSeverity.Warning
    assert "ignored when ibrav is not 0" in diagnostics[0].message


def test_diagnostic_warns_about_low_ecutrho_ratio():
    """ecutrho should normally be at least 4x ecutwfc."""
    diagnostics = diagnostic(Params("&SYSTEM\necutwfc = 60\necutrho = 120\n/\n"))

    assert len(diagnostics) == 1
    assert diagnostics[0].severity == types.DiagnosticSeverity.Warning
    assert "at least 4x ecutwfc" in diagnostics[0].message


def test_diagnostic_reports_pseudopotential_element_mismatch():
    """The pseudo filename should match the declared element."""
    diagnostics = diagnostic(Params("ATOMIC_SPECIES\nO 15.999 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"))

    assert len(diagnostics) == 1
    assert diagnostics[0].severity == types.DiagnosticSeverity.Error
    assert "does not appear to match element O" in diagnostics[0].message


def test_diagnostic_reports_atomic_positions_without_species():
    """All positioned atoms need a matching ATOMIC_SPECIES entry."""
    diagnostics = diagnostic(
        Params(
            "ATOMIC_SPECIES\nO 15.999 O.pbe.UPF\n" "ATOMIC_POSITIONS {crystal}\nSi 0.0 0.0 0.0\n"
        )
    )

    assert len(diagnostics) == 1
    assert diagnostics[0].severity == types.DiagnosticSeverity.Error
    assert "missing from ATOMIC_SPECIES" in diagnostics[0].message


def test_diagnostic_warns_about_gamma_offsets():
    """Gamma-only K_POINTS must not include non-zero offsets."""
    diagnostics = diagnostic(Params("K_POINTS {gamma}\n1 1 1 0 0 1\n"))

    assert len(diagnostics) == 1
    assert diagnostics[0].severity == types.DiagnosticSeverity.Warning
    assert "non-zero offset" in diagnostics[0].message


def test_server_registers_lsp_features():
    """Handlers should be registered with pygls, not only callable directly."""
    features = get_registered_features(server)

    assert "textDocument/completion" in features
    assert "textDocument/hover" in features
    assert "textDocument/diagnostic" in features


def test_create_server_uses_configured_version():
    """Server creation should use the package version source of truth."""
    created = create_server()

    assert created.name == "qe-lsp"
    assert created.version == __version__

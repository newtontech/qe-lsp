"""Basic tests for qe-lsp."""

from qe_lsp import __version__
from qe_lsp.server import QE_KEYWORDS, completion, diagnostic, hover, server
from lsprotocol import types


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


def test_server_registers_lsp_features():
    """Handlers should be registered with pygls, not only callable directly."""
    features = server.protocol.fm.features

    assert "textDocument/completion" in features
    assert "textDocument/hover" in features
    assert "textDocument/diagnostic" in features

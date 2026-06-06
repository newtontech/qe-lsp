"""
Basic tests for qe-lsp.
"""

from qe_lsp import __version__
from qe_lsp.server import QE_KEYWORDS, completion, diagnostic, hover


def test_import():
    """Test that the package exposes its version."""
    assert __version__ == "0.1.0"


def test_completion_returns_qe_keywords():
    """Completion should expose common Quantum ESPRESSO input sections."""
    items = completion(None)

    labels = {item["label"] for item in items}
    assert set(QE_KEYWORDS).issubset(labels)
    assert "&CONTROL" in labels
    assert "ATOMIC_POSITIONS" in labels


def test_hover_returns_markdown_documentation():
    """Hover should return a markdown payload for known QE content."""
    result = hover(None)

    assert result["contents"]["kind"] == "markdown"
    assert "&CONTROL" in result["contents"]["value"]
    assert "Quantum ESPRESSO" in result["contents"]["value"]


def test_diagnostic_is_currently_empty():
    """Diagnostic handler currently returns an empty list."""
    assert diagnostic(None) == []

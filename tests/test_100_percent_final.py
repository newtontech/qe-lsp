"""Tests to reach 100% code coverage."""

import pytest
from unittest.mock import MagicMock, patch
from lsprotocol.types import (
    HoverParams,
    Position,
    TextDocumentIdentifier,
)

from qe_lsp.parser import QEParser, QELexer, Token, TokenType


class TestFinalParserCoverage:
    """Tests for parser 100% coverage."""

    def test_lexer_handle_right_paren(self):
        """Test lexer handles ) character."""
        lexer = QELexer("a(b)")
        tokens = lexer.tokenize()
        assert tokens[-1].type == TokenType.EOF

    def test_parser_namelist_line_end(self):
        """Test parser namelist line_end assignment."""
        text = """&control
calculation = 'scf'
/"""
        parser = QEParser(text)
        result = parser.parse()
        assert "control" in result.namelists
        assert result.namelists["control"].line_end > 0


class TestFinalServerCoverage:
    """Tests for server 100% coverage."""

    def test_get_namelist_at_position_ampersand_end(self):
        """Test _get_namelist_at_position with &end closure."""
        from qe_lsp.server import _get_namelist_at_position
        
        doc = MagicMock()
        doc.source = "&control\ncalc='scf'\n&end\nafter"
        
        position = MagicMock()
        position.line = 3
        
        result = _get_namelist_at_position(doc, position)
        assert result is None


class TestInitCoverage:
    """Tests for __init__ 100% coverage."""

    def test_getattr_raises_attribute_error(self):
        """Test __getattr__ raises AttributeError for invalid attribute."""
        import qe_lsp
        
        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp.nonexistent_attr_12345
        
        assert "nonexistent_attr_12345" in str(exc_info.value)

"""Complete coverage tests for remaining uncovered lines."""

import pytest
from unittest.mock import MagicMock, patch


class TestInitCompleteCoverage:
    """Complete coverage for __init__.py - lines 35-37."""

    def test_getattr_raises_error(self):
        """Test __getattr__ raises AttributeError with correct message."""
        import qe_lsp

        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp.this_does_not_exist

        assert "module 'qe_lsp' has no attribute" in str(exc_info.value)
        assert "this_does_not_exist" in str(exc_info.value)


class TestParserCompleteCoverage:
    """Complete coverage for parser.py remaining lines."""

    def test_parser_error_with_token(self):
        """Test parser error with specific token."""
        from qe_lsp.parser import QEParser, Token, TokenType

        parser = QEParser("&control\n/")
        parser.tokens = [
            Token(TokenType.NAMELIST_START, "control", 1, 1),
            Token(TokenType.NEWLINE, "\n", 1, 9),
            Token(TokenType.NAMELIST_END, "/", 2, 1),
            Token(TokenType.EOF, "", 2, 2),
        ]

        # Error with a specific token
        error_token = Token(TokenType.PARAMETER, "test", 5, 10)
        parser.error("Test error", error_token)

        assert len(parser.errors) == 1
        assert parser.errors[0]["line"] == 5
        assert parser.errors[0]["column"] == 10

    def test_parse_card_data_with_only_newlines(self):
        """Test parse_card_data with only newlines."""
        from qe_lsp.parser import QEParser, Token, TokenType

        parser = QEParser("")
        parser.tokens = [
            Token(TokenType.NEWLINE, "\n", 1, 1),
            Token(TokenType.NEWLINE, "\n", 2, 1),
            Token(TokenType.EOF, "", 3, 1),
        ]
        parser.pos = 0

        result = parser.parse_card_data("TEST")
        assert result == []

    def test_parse_namelist_with_missing_value(self):
        """Test parsing namelist with parameter missing value."""
        from qe_lsp.parser import QEParser

        # Parameter without =
        text = """&control
calculation
/"""
        parser = QEParser(text)
        result = parser.parse()

        assert "control" in result.namelists
        # The parameter should be present even without value
        assert "calculation" in result.namelists["control"].parameters

    def test_parse_card_without_options(self):
        """Test parsing card without options."""
        from qe_lsp.parser import QEParser

        text = """ATOMIC_SPECIES
C 12.0 C.upf"""
        parser = QEParser(text)
        result = parser.parse()

        assert "ATOMIC_SPECIES" in result.cards
        # No options provided
        assert result.cards["ATOMIC_SPECIES"].options is None

    def test_parse_with_unknown_token_types(self):
        """Test parse with unknown/unsupported token types."""
        from qe_lsp.parser import QEParser

        # Input with special characters that might create unexpected tokens
        text = """$comment
ATOMIC_SPECIES
C 12.0 C.upf"""
        parser = QEParser(text)
        result = parser.parse()

        # Should parse without crashing
        assert "ATOMIC_SPECIES" in result.cards


class TestServerCompleteCoverage:
    """Complete coverage for server.py remaining lines."""

    def test_get_namelist_at_position_with_empty_name(self):
        """Test _get_namelist_at_position with empty namelist name."""
        from qe_lsp.server import _get_namelist_at_position
        from unittest.mock import MagicMock

        doc = MagicMock()
        doc.source = "&\ncalculation = 'scf'\n/"

        pos = MagicMock()
        pos.line = 1
        pos.character = 5

        result = _get_namelist_at_position(doc, pos)
        # Should handle empty namelist name gracefully
        assert result is None or result == ""

    def test_hover_with_unrecognized_card(self):
        """Test hover handler with unrecognized card."""
        from qe_lsp.server import hover
        from unittest.mock import MagicMock, patch

        params = MagicMock()
        params.text_document.uri = "file:///test.in"
        params.position.line = 0
        params.position.character = 0

        with patch('qe_lsp.server._get_server') as mock_get_server:
            mock_doc = MagicMock()
            mock_doc.source = "UNKNOWN_CARD"
            mock_server = MagicMock()
            mock_server.workspace.get_text_document.return_value = mock_doc
            mock_get_server.return_value = mock_server

            with patch('qe_lsp.server._get_word_at_position', return_value=("UNKNOWN_CARD", None)):
                with patch('qe_lsp.server._get_namelist_at_position', return_value=None):
                    result = hover(params)
                    # Should return None for unrecognized card
                    assert result is None

    def test_document_symbol_with_empty_namelist(self):
        """Test document_symbol with namelist that has no children."""
        from qe_lsp.server import document_symbol
        from unittest.mock import MagicMock, patch

        params = MagicMock()
        params.text_document.uri = "file:///test.in"

        with patch('qe_lsp.server._get_server') as mock_get_server:
            mock_doc = MagicMock()
            mock_doc.source = "&control\n/"
            mock_server = MagicMock()
            mock_server.workspace.get_text_document.return_value = mock_doc
            mock_get_server.return_value = mock_server

            result = document_symbol(params)
            # Should return symbols even for empty namelist
            assert isinstance(result, list)


class TestEdgeCases:
    """Edge case tests for complete coverage."""

    def test_get_word_at_position_empty_line(self):
        """Test get_word_at_position on empty line."""
        from qe_lsp.parser import get_word_at_position

        result = get_word_at_position("line1\n\nline3", 1, 0)
        assert result[0] is None

    def test_get_word_at_position_beyond_column(self):
        """Test get_word_at_position beyond line length."""
        from qe_lsp.parser import get_word_at_position

        result = get_word_at_position("short", 0, 100)
        assert result[0] is None

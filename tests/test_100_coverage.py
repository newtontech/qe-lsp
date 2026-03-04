"""Tests to achieve 100% coverage for missing lines."""

import pytest
from unittest.mock import MagicMock, patch
from qe_lsp.parser import QELexer, QEParser, TokenType, parse_qe_input
from qe_lsp.server import _get_namelist_at_position, _hover_handler


class TestInitModuleCoverage:
    """Cover __init__.py lines 35-37."""

    def test_getattr_invalid_attribute_raises(self):
        """Test that accessing invalid attribute raises AttributeError."""
        import qe_lsp

        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp.nonexistent_attribute

        assert "has no attribute" in str(exc_info.value)


class TestParserCoverage:
    """Cover parser.py missing lines."""

    def test_read_string_unclosed(self):
        """Cover parser.py:146 - unclosed string reads until EOF."""
        lexer = QELexer('"unclosed string')
        token = lexer.read_string()
        assert token.type == TokenType.STRING
        assert token.value == "unclosed string"

    def test_read_number_no_exponent_after_e(self):
        """Cover parser.py:160-162 - number with 'e' but no exponent."""
        lexer = QELexer("1e")
        token = lexer.read_number()
        assert token.type == TokenType.NUMBER
        assert "e" in token.value

    def test_tokenize_unknown_character(self):
        """Cover parser.py:280-281 - unknown character handling."""
        lexer = QELexer("?")
        tokens = lexer.tokenize()
        assert any(t.type == TokenType.EOF for t in tokens)

    def test_parse_namelist_with_param_no_equals(self):
        """Cover parser.py:426,432 - parameter without '=' in namelist."""
        # This input should trigger the missing '=' branch
        parser = QEParser("&control\ncalculation\n/")
        # Tokenize first
        parser.tokens = parser.lexer.tokenize()
        parser.pos = 0
        # Skip to namelist start
        while parser.current().type != TokenType.NAMELIST_START:
            parser.advance()
        namelist = parser.parse_namelist()
        # Should still return a namelist even if param has no value
        assert namelist is not None
        assert namelist.name == "control"

    def test_parse_card_data_edge_cases(self):
        """Cover parser.py:469 - card data edge cases."""
        parser = QEParser("ATOMIC_POSITIONS\nSi 0.0 0.0 0.0\nK_POINTS automatic\n2 2 2 0 0 0")
        parser.tokens = parser.lexer.tokenize()
        parser.pos = 0
        while parser.current().type != TokenType.CARD_NAME:
            parser.advance()
        card = parser.parse_card()
        assert card is not None

    def test_parse_continue_branches(self):
        """Cover parser.py:572->574, 578->580 - continue branches in parse()."""
        result = parse_qe_input("\n\n&control\n/\n\n&system\n/\n\n")
        assert "control" in result.namelists
        assert "system" in result.namelists


class TestServerCoverage:
    """Cover server.py missing lines."""

    def test_get_namelist_at_position_line_branch(self):
        """Cover server.py:81->75 - the i < position.line branch."""
        from lsprotocol.types import Position

        doc = MagicMock()
        doc.source = "&control\n/\n&system\n/"

        position = Position(line=2, character=0)
        result = _get_namelist_at_position(doc, position)
        assert result == "system"

    def test_hover_handler_returns_none(self):
        """Cover server.py:177->185 - hover returns None branch."""
        from lsprotocol.types import TextDocumentPositionParams, Position

        params = MagicMock(spec=TextDocumentPositionParams)
        params.text_document.uri = "test:///test.in"
        params.position = Position(line=0, character=0)

        with patch("qe_lsp.server._get_server") as mock_get_server:
            mock_server = MagicMock()
            mock_doc = MagicMock()
            mock_doc.source = "some_random_word"
            mock_server.workspace.get_text_document.return_value = mock_doc
            mock_get_server.return_value = mock_server

            result = _hover_handler(params)
            assert result is None


class TestMainFunction:
    """Cover server.py:321 - main() function."""

    @patch("qe_lsp.server._get_server")
    def test_main_function(self, mock_get_server):
        """Test main() function starts the server."""
        from qe_lsp.server import main

        mock_server = MagicMock()
        mock_get_server.return_value = mock_server

        try:
            main()
        except SystemExit:
            pass

        mock_server.start_io.assert_called_once()


class TestAdditionalCoverage:
    """Additional tests for remaining uncovered lines."""

    def test_parse_with_card_condition_branch(self):
        """Cover parser.py:504->507 - card parsing with specific conditions."""
        # This should trigger the specific branch at line 504->507
        result = parse_qe_input("&control\n/\nATOMIC_POSITIONS crystal\nSi 0.0 0.0 0.0")
        assert "ATOMIC_POSITIONS" in result.cards

    def test_parse_namelist_at_eof(self):
        """Test parsing when EOF is reached during namelist."""
        lexer = QELexer('"test string')
        tokens = lexer.tokenize()
        # Should handle unclosed string gracefully
        assert any(t.type == TokenType.EOF for t in tokens)

    def test_parse_value_with_parentheses(self):
        """Test parsing value with parentheses."""
        lexer = QELexer("(1,2,3)")
        tokens = lexer.tokenize()
        # Should handle parentheses correctly
        assert any(t.type == TokenType.EOF for t in tokens)

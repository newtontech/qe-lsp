"""Final coverage tests for missing lines."""

import pytest
from unittest.mock import MagicMock, patch

from qe_lsp.parser import (
    QELexer,
    QEParser,
    TokenType,
    parse_qe_input,
)
from qe_lsp.server import (
    _get_namelist_at_position,
    _hover_handler,
    main,
)


class TestLexerMissingLines:
    """Test lexer lines 158, 171 (unclosed string, unknown char)."""

    def test_unclosed_string_eof(self):
        """Test unclosed string reaching EOF (line 158)."""
        lexer = QELexer("'unclosed string")
        token = lexer.read_string()
        assert token.type == TokenType.STRING
        assert token.value == "unclosed string"

    def test_unknown_character_skip(self):
        """Test unknown character being skipped in tokenize (line 171)."""
        lexer = QELexer("&control\n@#\n/")
        tokens = lexer.tokenize()
        assert tokens[-1].type == TokenType.EOF


class TestParserMissingLines:
    """Test parser missing lines."""

    def test_parse_value_error_fallback(self):
        """Test parse_value ValueError fallback."""
        parser = QEParser("invalid_number")
        parser.tokens = [MagicMock(type=TokenType.NUMBER, value="not_a_number", line=1, column=1)]
        parser.pos = 0
        result = parser.parse_value()
        assert result == "not_a_number"

    def test_parse_namelist_comment_handling(self):
        """Test COMMENT handling in parse_namelist."""
        text = """&control
! this is a comment
calculation = 'scf'
/"""
        result = parse_qe_input(text)
        assert "control" in result.namelists


class TestServerMissingLines:
    """Test server missing lines."""

    def test_get_namelist_at_position_ampersand_end(self):
        """Test &end handling."""
        doc = MagicMock()
        doc.source = "&control\n&end\ncalc = 'scf'"
        result = _get_namelist_at_position(doc, MagicMock(line=2, character=0))
        assert result is None

    @patch("qe_lsp.server._get_server")
    def test_hover_namelist_name(self, mock_get_server):
        """Test hover on namelist name."""
        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(
            source="&control\ncalculation = 'scf'\n/"
        )
        mock_get_server.return_value = srv

        from lsprotocol.types import HoverParams, Position, TextDocumentIdentifier

        params = HoverParams(
            text_document=TextDocumentIdentifier(uri="file:///test.in"),
            position=Position(line=0, character=2),
        )

        result = _hover_handler(params)
        assert result is not None

    @patch("qe_lsp.server._get_server")
    def test_main_function(self, mock_get_server):
        """Test main function."""
        mock_srv = MagicMock()
        mock_get_server.return_value = mock_srv
        main()
        mock_srv.start_io.assert_called_once()


class TestInitMissingLines:
    """Test __init__.py missing lines."""

    def test_getattr_else_branch(self):
        """Test __getattr__ else branch raising AttributeError."""
        import qe_lsp

        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp.nonexistent_attribute

        assert "nonexistent_attribute" in str(exc_info.value)

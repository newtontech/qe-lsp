"""Additional tests to achieve 100% coverage."""

import pytest
from unittest.mock import MagicMock, patch


def test_init_getattr_server():
    """Test __getattr__ for server lazy import."""
    import qe_lsp
    # This should trigger the lazy import
    srv = qe_lsp.server
    assert srv is not None


def test_init_getattr_main():
    """Test __getattr__ for main lazy import."""
    import qe_lsp
    # This should trigger the lazy import
    main_func = qe_lsp.main
    assert main_func is not None


def test_init_getattr_invalid():
    """Test __getattr__ for invalid attribute."""
    import qe_lsp
    with pytest.raises(AttributeError):
        _ = qe_lsp.nonexistent_attribute


class TestParserEdgeCases:
    """Test edge cases in parser."""

    def test_parser_error_with_token(self):
        """Test parser error with specific token."""
        from qe_lsp.parser import QEParser

        parser = QEParser("&control\n")
        parser.tokens = []
        parser.pos = 0
        # Create a mock token
        mock_token = MagicMock()
        mock_token.line = 5
        mock_token.column = 10
        parser.error("test error", mock_token)
        assert len(parser.errors) == 1
        assert parser.errors[0]["line"] == 5
        assert parser.errors[0]["column"] == 10

    def test_parse_namelist_without_equals(self):
        """Test parsing namelist with parameter without equals sign."""
        from qe_lsp.parser import QEParser, Token, TokenType

        # Create a parser with a namelist that has a parameter without value
        text = "&control\ncalculation\n/"
        parser = QEParser(text)
        parser.tokens = [
            Token(TokenType.NAMELIST_START, "control", 1, 1),
            Token(TokenType.NEWLINE, "\n", 1, 9),
            Token(TokenType.PARAMETER, "calculation", 2, 1),
            Token(TokenType.NEWLINE, "\n", 2, 12),
            Token(TokenType.NAMELIST_END, "/", 3, 1),
            Token(TokenType.EOF, "", 3, 2),
        ]
        parser.pos = 0
        namelist = parser.parse_namelist()
        assert namelist is not None
        assert "calculation" in namelist.parameters

    def test_parse_card_data_with_comment(self):
        """Test parsing card data with comment."""
        from qe_lsp.parser import QEParser, Token, TokenType

        parser = QEParser("")
        parser.tokens = [
            Token(TokenType.PARAMETER, "Si", 1, 1),
            Token(TokenType.COMMENT, "! comment", 1, 5),
            Token(TokenType.EOF, "", 1, 15),
        ]
        parser.pos = 0
        data = parser.parse_card_data("ATOMIC_SPECIES")
        assert data == [["Si"]]

    def test_parse_card_with_comment_after_options(self):
        """Test parsing card with comment after options."""
        from qe_lsp.parser import QEParser, Token, TokenType

        parser = QEParser("")
        parser.tokens = [
            Token(TokenType.CARD_NAME, "ATOMIC_POSITIONS", 1, 1),
            Token(TokenType.PARAMETER, "crystal", 1, 18),
            Token(TokenType.COMMENT, "! comment", 1, 26),
            Token(TokenType.NEWLINE, "\n", 1, 35),
            Token(TokenType.EOF, "", 2, 1),
        ]
        parser.pos = 0
        card = parser.parse_card()
        assert card is not None
        assert card.options == "crystal"

    def test_parse_value_with_unknown_token(self):
        """Test parse_value with unknown token type."""
        from qe_lsp.parser import QEParser, Token, TokenType

        parser = QEParser("")
        parser.tokens = [
            Token(TokenType.NEWLINE, "\n", 1, 1),
            Token(TokenType.EOF, "", 1, 2),
        ]
        parser.pos = 0
        value = parser.parse_value()
        assert value is None


class TestLexerEdgeCases:
    """Test edge cases in lexer."""

    def test_skip_comment_not_comment(self):
        """Test skip_comment when not at comment."""
        from qe_lsp.parser import QELexer

        lexer = QELexer("not a comment")
        # peek() is not '!', so skip_comment should do nothing
        lexer.skip_comment()
        assert lexer.pos == 0

    def test_read_boolean_dot_only(self):
        """Test reading identifier starting with dot that's not a boolean."""
        from qe_lsp.parser import QELexer, TokenType

        lexer = QELexer(".notbool")
        token = lexer.read_identifier()
        assert token.type == TokenType.PARAMETER
        assert token.value == ".notbool"


class TestServerEdgeCases:
    """Test edge cases in server."""

    def test_get_namelist_at_position_empty_namelist(self):
        """Test getting namelist when name part is empty."""
        from qe_lsp.server import _get_namelist_at_position

        doc = MagicMock()
        doc.source = "&\ncalculation = 'scf'\n/"
        pos = MagicMock(line=1, character=0)
        result = _get_namelist_at_position(doc, pos)
        # Empty namelist name should result in None
        assert result is None

    def test_hover_no_card_doc(self):
        """Test hover when card doc is not found."""
        from qe_lsp.server import hover

        with patch("qe_lsp.server._get_server") as mock_get_server:
            srv = MagicMock()
            srv.workspace.get_text_document.return_value = MagicMock(
                source="UNKNOWN_CARD"
            )
            mock_get_server.return_value = srv

            params = MagicMock()
            params.text_document.uri = "test://test.in"
            params.position = MagicMock(line=0, character=0)

            result = hover(params)
            # Should return None for unknown card
            assert result is None

    def test_completion_with_no_matches(self):
        """Test completion when no matches found."""
        from qe_lsp.server import completion

        with patch("qe_lsp.server._get_server") as mock_get_server:
            srv = MagicMock()
            srv.workspace.get_text_document.return_value = MagicMock(
                source="xyz123nonexistent"
            )
            mock_get_server.return_value = srv

            params = MagicMock()
            params.text_document.uri = "test://test.in"
            params.position = MagicMock(line=0, character=10)

            result = completion(params)
            # Should return empty completion list
            assert result is not None
            assert len(result.items) == 0


class TestDocsModule:
    """Test docs module edge cases."""

    def test_doc_formatter_param_not_found(self):
        """Test format_parameter_doc when param not found."""
        from qe_lsp.docs import DocFormatter

        result = DocFormatter.format_parameter_doc("nonexistent", "control")
        assert result is None

    def test_doc_formatter_card_not_found(self):
        """Test format_card_doc when card not found."""
        from qe_lsp.docs import DocFormatter

        result = DocFormatter.format_card_doc("UNKNOWN_CARD")
        assert result is None


class TestDataModuleEdgeCases:
    """Test data module edge cases."""

    def test_format_param_hover_with_all_fields(self):
        """Test format_param_hover with all possible fields."""
        from qe_lsp.data import format_param_hover

        param_doc = {
            "description": "Test parameter",
            "type": "real",
            "required": True,
            "default": 1.0,
            "values": ["1.0", "2.0", "3.0"],
        }
        result = format_param_hover(param_doc)
        assert "Test parameter" in result
        assert "real" in result
        assert "Required" in result
        assert "1.0" in result
        assert "Possible values" in result

    def test_format_param_hover_minimal(self):
        """Test format_param_hover with minimal fields."""
        from qe_lsp.data import format_param_hover

        param_doc = {"description": "Test parameter"}
        result = format_param_hover(param_doc)
        assert result == "Test parameter"

    def test_format_card_hover_with_example(self):
        """Test format_card_hover with example field."""
        from qe_lsp.data import format_card_hover

        card_doc = {
            "description": "Test card",
            "format": "FORMAT",
            "example": "EXAMPLE",
            "required_when": "always",
        }
        result = format_card_hover(card_doc)
        assert "Test card" in result
        assert "FORMAT" in result
        assert "EXAMPLE" in result
        assert "always" in result

    def test_get_param_doc_not_found(self):
        """Test get_param_doc when not found."""
        from qe_lsp.data import get_param_doc

        result = get_param_doc("nonexistent", "nonexistent")
        assert result is None

    def test_get_card_doc_not_found(self):
        """Test get_card_doc when not found."""
        from qe_lsp.data import get_card_doc

        result = get_card_doc("UNKNOWN")
        assert result is None

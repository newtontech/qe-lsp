"""Extra tests for higher coverage."""

import pytest
from unittest.mock import MagicMock, patch


class TestInitGetattr:
    """Test __init__.__getattr__ branches."""

    def test_getattr_else_branch(self):
        """Test __getattr__ with unknown name raises AttributeError."""
        import qe_lsp

        with pytest.raises(AttributeError):
            qe_lsp.__getattr__("nonexistent_module_name")


class TestDataFormatBranches:
    """Test data.py format function branches."""

    def test_format_param_without_type(self):
        """Test format_param_hover without type field (373->376)."""
        from qe_lsp.data import format_param_hover

        result = format_param_hover({"description": "test"})
        assert "test" in result
        assert "**Type:**" not in result

    def test_format_card_without_format(self):
        """Test format_card_hover without format field (403->406)."""
        from qe_lsp.data import format_card_hover

        result = format_card_hover({"description": "test"})
        assert "test" in result
        assert "**Format:**" not in result


class TestParserEdgeCases:
    """Test parser edge cases."""

    def test_lexer_unclosed_string(self):
        """Test lexer with unclosed string (146->exit)."""
        from qe_lsp.parser import QELexer, TokenType

        lexer = QELexer("'unclosed")
        token = lexer.read_string()
        assert token.type == TokenType.STRING
        assert token.value == "unclosed"

    def test_lexer_unclosed_paren(self):
        """Test lexer with unclosed parenthesis (280-281)."""
        from qe_lsp.parser import QELexer

        lexer = QELexer("test(unclosed")
        tokens = lexer.tokenize()
        assert len(tokens) > 0

    def test_lexer_standalone_close_paren(self):
        """Test lexer with standalone close paren (288->290)."""
        from qe_lsp.parser import QELexer

        lexer = QELexer(")")
        tokens = lexer.tokenize()
        assert len(tokens) > 0

    def test_parser_card_data_stops_at_namelist(self):
        """Test card data stops at namelist (382-383)."""
        from qe_lsp.parser import QEParser

        text = "ATOMIC_SPECIES\nSi 28 Si.upf\n&control\n/"
        parser = QEParser(text)
        result = parser.parse()
        assert "ATOMIC_SPECIES" in result.cards


class TestServerBranches:
    """Test server.py branches."""

    def test_server_init(self):
        """Test server initialization (38->43)."""
        from qe_lsp.server import _get_server
        import qe_lsp.server as server_mod

        server_mod._server_instance = None
        srv = _get_server()
        assert srv is not None

    def test_namelist_detection_ampersand_end(self):
        """Test namelist detection with &end (80->74)."""
        from qe_lsp.server import _get_namelist_at_position
        from lsprotocol.types import Position

        mock_doc = MagicMock()
        mock_doc.source = "&control\nx=1\n&end\n"
        pos = Position(line=3, character=0)  # After &end
        result = _get_namelist_at_position(mock_doc, pos)
        # After &end, should be None
        assert result is None

    def test_completion_in_namelist(self):
        """Test completion inside namelist (157->164)."""
        from qe_lsp.server import completion
        from lsprotocol.types import CompletionParams, Position

        mock_doc = MagicMock()
        mock_doc.source = "&control\n  calc"

        mock_workspace = MagicMock()
        mock_workspace.get_text_document.return_value = mock_doc

        with patch("qe_lsp.server._get_server") as mock_get_server:
            mock_server = MagicMock()
            mock_server.workspace = mock_workspace
            mock_get_server.return_value = mock_server

            params = CompletionParams(
                text_document=MagicMock(uri="file:///test.in"),
                position=Position(line=1, character=6),
            )
            result = completion(params)
            assert result is not None

    def test_hover_on_namelist_name(self):
        """Test hover on namelist name (176->184)."""
        from qe_lsp.server import hover
        from lsprotocol.types import TextDocumentPositionParams, Position

        mock_doc = MagicMock()
        mock_doc.source = "ions"

        mock_workspace = MagicMock()
        mock_workspace.get_text_document.return_value = mock_doc

        with patch("qe_lsp.server._get_server") as mock_get_server:
            mock_server = MagicMock()
            mock_server.workspace = mock_workspace
            mock_get_server.return_value = mock_server

            params = TextDocumentPositionParams(
                text_document=MagicMock(uri="file:///test.in"),
                position=Position(line=0, character=0),
            )
            result = hover(params)
            assert result is not None

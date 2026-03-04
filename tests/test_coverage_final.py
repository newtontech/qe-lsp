"""Tests for achieving 100% code coverage."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


class TestInitCoverage:
    """Test coverage for __init__.py edge cases."""

    def test_getattr_invalid_attribute(self):
        """Test __getattr__ raises AttributeError for invalid attribute."""
        import qe_lsp

        with pytest.raises(AttributeError, match="module 'qe_lsp' has no attribute"):
            _ = qe_lsp.nonexistent_attribute

    def test_getattr_server(self):
        """Test lazy loading of server attribute."""
        import qe_lsp

        # This should trigger the lazy import
        server = qe_lsp.server
        assert server is not None

    def test_getattr_main(self):
        """Test lazy loading of main function."""
        import qe_lsp

        main_func = qe_lsp.main
        assert callable(main_func)


class TestParserCoverage:
    """Test coverage for parser.py edge cases."""

    def test_lexer_peek_empty_string(self):
        """Test lexer peek with empty string."""
        from qe_lsp.parser import QELexer

        lexer = QELexer("")
        # Peek beyond end of text should return empty string
        assert lexer.peek(100) == ""

    def test_parser_parse_value_empty(self):
        """Test parse_value when no value is present."""
        from qe_lsp.parser import QEParser

        parser = QEParser("&control\n/")
        parser.tokens = parser.lexer.tokenize()
        # Position at EOF
        parser.pos = len(parser.tokens) - 1
        result = parser.parse_value()
        assert result is None

    def test_parser_unrecognized_card_data(self):
        """Test parsing card data with unrecognized tokens."""
        from qe_lsp.parser import QEParser

        # Card with unusual content
        text = """ATOMIC_SPECIES
C 12.0 C.pbe-n-kjpaw_psl.1.0.0.UPF
&unknown"""
        parser = QEParser(text)
        result = parser.parse()
        assert "ATOMIC_SPECIES" in result.cards

    def test_parse_card_with_special_chars(self):
        """Test parsing card with special characters in data."""
        from qe_lsp.parser import QEParser

        text = """ATOMIC_POSITIONS crystal
C 0.0 0.0 0.0
O 0.5 0.5 0.5 ! comment"""
        parser = QEParser(text)
        result = parser.parse()
        assert "ATOMIC_POSITIONS" in result.cards
        assert len(result.cards["ATOMIC_POSITIONS"].data) == 2

    def test_namelist_with_array_params(self):
        """Test parsing namelist with array parameters like celldm(1)."""
        from qe_lsp.parser import QEParser

        text = """
&system
ibrav = 1
celldm(1) = 10.0
/"""
        parser = QEParser(text)
        result = parser.parse()
        assert "system" in result.namelists

    def test_parser_empty_namelist_name(self):
        """Test parsing namelist with empty name edge case."""
        from qe_lsp.parser import QEParser, Token, TokenType

        parser = QEParser("&system\n/")
        parser.tokens = [
            Token(TokenType.NAMELIST_START, "system", 1, 1),
            Token(TokenType.NEWLINE, "\n", 1, 8),
            Token(TokenType.NAMELIST_END, "/", 2, 1),
            Token(TokenType.EOF, "", 2, 2),
        ]
        parser.pos = 0
        result = parser.parse_namelist()
        assert result is not None
        assert result.name == "system"

    def test_parse_namelist_with_param_no_value(self):
        """Test parsing namelist with parameter missing value."""
        from qe_lsp.parser import QEParser

        text = """
&control
calculation
/"""
        parser = QEParser(text)
        result = parser.parse()
        assert "control" in result.namelists

    def test_get_word_at_position_edge_cases(self):
        """Test get_word_at_position with edge cases."""
        from qe_lsp.parser import get_word_at_position

        # Empty text
        result = get_word_at_position("", 0, 0)
        assert result[0] is None

        # Position beyond text
        result = get_word_at_position("test", 10, 10)
        assert result[0] is None

        # End of line
        result = get_word_at_position("test word", 0, 9)
        assert result[0] is None


class TestServerCoverage:
    """Test coverage for server.py edge cases."""

    def test_get_namelist_at_position_after_end(self):
        """Test _get_namelist_at_position after namelist end."""
        from qe_lsp.server import _get_namelist_at_position
        from unittest.mock import MagicMock

        doc = MagicMock()
        doc.source = """&control
calculation = 'scf'
/
&system
ibrav = 1
/
"""

        # Position inside &system namelist
        pos = MagicMock()
        pos.line = 4  # Line with ibrav = 1
        pos.character = 2

        result = _get_namelist_at_position(doc, pos)
        assert result == "system"

    def test_get_namelist_at_position_with_ampersand_end(self):
        """Test _get_namelist_at_position with &end terminator."""
        from qe_lsp.server import _get_namelist_at_position
        from unittest.mock import MagicMock

        doc = MagicMock()
        doc.source = """&control
calculation = 'scf'
&end
ATOMIC_SPECIES
"""

        # Position after &end
        pos = MagicMock()
        pos.line = 4
        pos.character = 0

        result = _get_namelist_at_position(doc, pos)
        assert result is None

    def test_hover_with_unknown_card(self):
        """Test hover handler with unknown card."""
        from qe_lsp.server import hover
        from unittest.mock import MagicMock

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

            result = hover(params)
            assert result is None

    def test_document_symbol_empty_file(self):
        """Test document symbol handler with empty file."""
        from qe_lsp.server import document_symbol
        from unittest.mock import MagicMock, patch

        params = MagicMock()
        params.text_document.uri = "file:///test.in"

        with patch('qe_lsp.server._get_server') as mock_get_server:
            mock_doc = MagicMock()
            mock_doc.source = ""
            mock_server = MagicMock()
            mock_server.workspace.get_text_document.return_value = mock_doc
            mock_get_server.return_value = mock_server

            result = document_symbol(params)
            assert result == []

    def test_completion_returns_items(self):
        """Test completion handler returns completion items."""
        from qe_lsp.server import completion
        from unittest.mock import MagicMock, patch

        params = MagicMock()
        params.text_document.uri = "file:///test.in"
        params.position.line = 1
        params.position.character = 2

        with patch('qe_lsp.server._get_server') as mock_get_server:
            mock_doc = MagicMock()
            # Ensure the line at position 1 has enough characters
            mock_doc.source = "&control\nibr\n/"
            mock_server = MagicMock()
            mock_server.workspace.get_text_document.return_value = mock_doc
            mock_get_server.return_value = mock_server

            result = completion(params)
            assert result is not None
            # Should return completion items
            assert isinstance(result.items, list)

    def test_main_function(self):
        """Test the main function starts server."""
        from qe_lsp.server import main
        from unittest.mock import MagicMock, patch

        with patch('qe_lsp.server._get_server') as mock_get_server:
            mock_server = MagicMock()
            mock_get_server.return_value = mock_server

            main()
            mock_server.start_io.assert_called_once()


class TestDataCoverage:
    """Test coverage for data.py edge cases."""

    def test_get_param_doc_invalid_namelist(self):
        """Test get_param_doc with invalid namelist."""
        from qe_lsp.data import get_param_doc

        result = get_param_doc("invalid_namelist", "some_param")
        assert result is None

    def test_get_card_doc_invalid_card(self):
        """Test get_card_doc with invalid card."""
        from qe_lsp.data import get_card_doc

        result = get_card_doc("INVALID_CARD")
        assert result is None

    def test_format_param_hover_without_optional_fields(self):
        """Test format_param_hover with minimal parameter doc."""
        from qe_lsp.data import format_param_hover

        param_doc = {"description": "Test param"}
        result = format_param_hover(param_doc)
        assert "Test param" in result
        assert "Type:" not in result

    def test_format_card_hover_without_optional_fields(self):
        """Test format_card_hover with minimal card doc."""
        from qe_lsp.data import format_card_hover

        card_doc = {"description": "Test card"}
        result = format_card_hover(card_doc)
        assert "Test card" in result
        assert "Format:" not in result

    def test_get_parameter_doc_legacy(self):
        """Test legacy get_parameter_doc function."""
        from qe_lsp.data import get_parameter_doc

        result = get_parameter_doc("control", "calculation")
        assert result is not None
        assert "scf" in result.lower()

        result = get_parameter_doc("invalid", "param")
        assert result is None


class TestDocsCoverage:
    """Test coverage for docs.py edge cases."""

    def test_doc_formatter_format_parameter_doc_not_found(self):
        """Test DocFormatter with non-existent parameter."""
        from qe_lsp.docs import DocFormatter

        result = DocFormatter.format_parameter_doc("nonexistent", "control")
        assert result is None

    def test_doc_formatter_format_card_doc_not_found(self):
        """Test DocFormatter with non-existent card."""
        from qe_lsp.docs import DocFormatter

        result = DocFormatter.format_card_doc("NONEXISTENT")
        assert result is None

    def test_get_formatted_parameter_doc_not_found(self):
        """Test get_formatted_parameter_doc with non-existent parameter."""
        from qe_lsp.docs import get_formatted_parameter_doc

        result = get_formatted_parameter_doc("nonexistent", "control")
        assert result is None

    def test_get_formatted_card_doc_not_found(self):
        """Test get_formatted_card_doc with non-existent card."""
        from qe_lsp.docs import get_formatted_card_doc

        result = get_formatted_card_doc("NONEXISTENT")
        assert result is None


class TestParserAdditionalCoverage:
    """Additional tests for parser coverage."""

    def test_lexer_error(self):
        """Test lexer error handling."""
        from qe_lsp.parser import QELexer

        lexer = QELexer("test")
        # Test error method exists
        try:
            lexer.error("test error")
        except SyntaxError as e:
            assert "test error" in str(e)

    def test_parser_error(self):
        """Test parser error handling."""
        from qe_lsp.parser import QEParser

        parser = QEParser("test")
        parser.error("test error message")
        assert len(parser.errors) > 0
        assert "test error message" in parser.errors[0]["message"]

    def test_parse_card_data_with_comment(self):
        """Test parsing card data with comments."""
        from qe_lsp.parser import QEParser

        text = """ATOMIC_SPECIES
C 12.0 C.upf ! this is a comment
H 1.0 H.upf"""
        parser = QEParser(text)
        result = parser.parse()
        assert "ATOMIC_SPECIES" in result.cards

    def test_parse_card_with_options(self):
        """Test parsing card with options."""
        from qe_lsp.parser import QEParser

        text = """ATOMIC_POSITIONS crystal
C 0.0 0.0 0.0"""
        parser = QEParser(text)
        result = parser.parse()
        assert "ATOMIC_POSITIONS" in result.cards
        assert result.cards["ATOMIC_POSITIONS"].options == "crystal"

    def test_parse_unknown_token(self):
        """Test parsing with unknown tokens."""
        from qe_lsp.parser import QEParser

        # Input with unusual characters
        text = "\u0026control\n@#$\n/"
        parser = QEParser(text)
        result = parser.parse()
        assert "control" in result.namelists

    def test_read_identifier_with_empty_namelist(self):
        """Test reading identifier with empty namelist name."""
        from qe_lsp.parser import QELexer

        # Just & with nothing after
        lexer = QELexer("&\n/")
        tokens = lexer.tokenize()
        # Should handle gracefully
        assert any(t.type.name == "PARAMETER" for t in tokens)


class TestServerAdditionalCoverage:
    """Additional tests for server coverage."""

    def test_get_namelist_at_position_in_control(self):
        """Test _get_namelist_at_position inside control namelist."""
        from qe_lsp.server import _get_namelist_at_position
        from unittest.mock import MagicMock

        doc = MagicMock()
        doc.source = """&control
calculation = 'scf'
&end
"""

        # Position inside control namelist
        pos = MagicMock()
        pos.line = 1
        pos.character = 5

        result = _get_namelist_at_position(doc, pos)
        assert result == "control"

        """Test that all expected imports are available."""
        import qe_lsp

        # Test all public API elements are available
        assert hasattr(qe_lsp, 'parse_qe_input')
        assert hasattr(qe_lsp, 'get_param_doc')
        assert hasattr(qe_lsp, 'get_namelist_params')
        assert hasattr(qe_lsp, 'get_card_names')
        assert hasattr(qe_lsp, 'get_card_doc')
        assert hasattr(qe_lsp, 'QEInputFile')
        assert hasattr(qe_lsp, 'Namelist')
        assert hasattr(qe_lsp, 'Card')

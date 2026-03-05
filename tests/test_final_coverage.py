"""Final coverage tests for 100% code coverage."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


class TestParserFinalCoverage:
    """Final parser coverage tests."""

    def test_lexer_empty_after_ampersand_with_space(self):
        """Test lexer with & followed by space (line 158)."""
        from qe_lsp.parser import QELexer, TokenType

        lexer = QELexer("& ")
        token = lexer.read_identifier()
        # When there's just '&' followed by space, it becomes a PARAMETER
        assert token.type == TokenType.PARAMETER

    def test_lexer_read_identifier_t_f_values(self):
        """Test lexer reading 't' and 'f' as booleans (line 171)."""
        from qe_lsp.parser import QELexer, TokenType

        # Test 't' as standalone boolean
        lexer = QELexer("t")
        token = lexer.read_identifier()
        assert token.type == TokenType.BOOLEAN
        assert token.value == "t"

        # Test 'f' as standalone boolean
        lexer = QELexer("f")
        token = lexer.read_identifier()
        assert token.type == TokenType.BOOLEAN
        assert token.value == "f"

    def test_lexer_peek_offset(self):
        """Test lexer peek with offset."""
        from qe_lsp.parser import QELexer

        lexer = QELexer("abc")
        assert lexer.peek(0) == "a"
        assert lexer.peek(1) == "b"
        assert lexer.peek(2) == "c"
        assert lexer.peek(3) == ""  # Beyond end

    def test_lexer_skip_comment_not_bang(self):
        """Test skip_comment when no bang."""
        from qe_lsp.parser import QELexer

        lexer = QELexer("not_a_comment")
        initial_pos = lexer.pos
        lexer.skip_comment()  # Should not advance since no '!'
        assert lexer.pos == initial_pos

    def test_parser_card_data_with_namelist_following(self):
        """Test card data parsing when namelist follows (lines 382-383)."""
        from qe_lsp.parser import QEParser

        text = """ATOMIC_SPECIES
Si 28.085 Si.upf
&control
/
"""
        parser = QEParser(text)
        result = parser.parse()
        assert "ATOMIC_SPECIES" in result.cards
        assert "control" in result.namelists

    def test_parser_error_with_value_none(self):
        """Test parser error when value is None (lines 431-434)."""
        from qe_lsp.parser import QEParser

        # This input should trigger the error path
        text = """&control
    calculation =
/
"""
        parser = QEParser(text)
        result = parser.parse()
        # Should have an error about expected value
        assert len(result.errors) > 0

    def test_parser_unknown_tokens_skip(self):
        """Test parser skipping unknown tokens (lines 457-458)."""
        from qe_lsp.parser import QEParser

        # Use characters that don't match any token type
        text = "@#$%^&*()[]{}"
        parser = QEParser(text)
        result = parser.parse()
        # Should parse without crashing, just skip unknown tokens
        assert isinstance(result.namelists, dict)

    def test_parser_validate_missing_control_and_system(self):
        """Test validation when both control and system are missing (lines 469, 470->477)."""
        from qe_lsp.parser import QEParser

        text = """&electrons
/
"""
        parser = QEParser(text)
        result = parser.parse()
        errors = [e for e in result.errors if "Missing required namelist" in e["message"]]
        assert len(errors) >= 1
        assert any("control" in e["message"] for e in errors)

    def test_parser_validate_missing_required_params(self):
        """Test validation of required parameters (lines 479->482, 504->507)."""
        from qe_lsp.parser import QEParser

        # control without required params
        text = """&control
/
"""
        parser = QEParser(text)
        result = parser.parse()
        # Should have errors for missing required params
        errors = [e for e in result.errors if "Missing required parameter" in e["message"]]
        assert len(errors) >= 1


class TestServerFinalCoverage:
    """Final server coverage tests."""

    def test_get_word_at_position_line_out_of_range(self):
        """Test _get_word_at_position when line is out of range (line 50)."""
        from qe_lsp.server import _get_word_at_position
        from lsprotocol.types import Position, Range

        mock_doc = MagicMock()
        mock_doc.source = "short\nfile"

        pos = Position(line=10, character=0)  # Line beyond file
        result = _get_word_at_position(mock_doc, pos)
        assert result == ("", Range(pos, pos))

    def test_hover_on_unknown_word(self):
        """Test hover returns None for unknown word."""
        from qe_lsp.server import hover
        from lsprotocol.types import TextDocumentPositionParams, Position

        mock_doc = MagicMock()
        mock_doc.source = "unknownword"

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
            # Should return None for unknown words
            assert result is None

    def test_diagnostic_with_warnings(self):
        """Test diagnostic handler with warning-level errors."""
        from qe_lsp.server import diagnostic

        mock_doc = MagicMock()
        mock_doc.source = """&control
    calculation = 'scf'
    prefix = 'test'
    outdir = './'
/
"""

        mock_workspace = MagicMock()
        mock_workspace.get_text_document.return_value = mock_doc

        with patch("qe_lsp.server._get_server") as mock_get_server:
            mock_server = MagicMock()
            mock_server.workspace = mock_workspace
            mock_get_server.return_value = mock_server

            params = MagicMock()
            params.text_document.uri = "file:///test.in"
            result = diagnostic(params)
            # Should return list of diagnostics
            assert isinstance(result, list)


class TestInitFinalCoverage:
    """Final __init__.py coverage tests."""

    def test_getattr_invalid_attribute(self):
        """Test __getattr__ with invalid attribute (lines 35-37)."""
        import qe_lsp

        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp.nonexistent_invalid_attribute

        assert "has no attribute" in str(exc_info.value)
        assert "nonexistent_invalid_attribute" in str(exc_info.value)


class TestDataFinalCoverage:
    """Final data.py coverage tests."""

    def test_format_param_hover_with_required_no_default(self):
        """Test format_param_hover with required but no default."""
        from qe_lsp.data import format_param_hover

        param_doc = {"description": "Test parameter", "type": "string", "required": True}
        result = format_param_hover(param_doc)
        assert "**Type:**" in result
        assert "⚠️ **Required parameter**" in result
        assert "**Default:**" not in result

    def test_format_param_hover_with_values_no_default(self):
        """Test format_param_hover with values but no default."""
        from qe_lsp.data import format_param_hover

        param_doc = {
            "description": "Test parameter",
            "type": "string",
            "values": ["'opt1'", "'opt2'"],
        }
        result = format_param_hover(param_doc)
        assert "**Possible values:**" in result

    def test_format_card_hover_with_all_fields(self):
        """Test format_card_hover with all optional fields."""
        from qe_lsp.data import format_card_hover

        card_doc = {
            "description": "Test card",
            "format": "format_spec",
            "example": "example_spec",
            "required_when": "always",
        }
        result = format_card_hover(card_doc)
        assert "Test card" in result
        assert "format_spec" in result
        assert "example_spec" in result
        assert "always" in result


class TestDocsFinalCoverage:
    """Final docs.py coverage tests."""

    def test_doc_formatter_format_card_doc_none(self):
        """Test DocFormatter.format_card_doc returns None for unknown card."""
        from qe_lsp.docs import DocFormatter

        result = DocFormatter.format_card_doc("NONEXISTENT_CARD")
        assert result is None

    def test_doc_formatter_format_parameter_doc_none(self):
        """Test DocFormatter.format_parameter_doc returns None for unknown param."""
        from qe_lsp.docs import DocFormatter

        result = DocFormatter.format_parameter_doc("nonexistent", "control")
        assert result is None


class TestParserEdgeCasesAdvanced:
    """Advanced edge case tests for parser."""

    def test_lexer_tokenize_with_mixed_content(self):
        """Test lexer with complex mixed content."""
        from qe_lsp.parser import QELexer, TokenType

        text = """&control
    calculation = 'scf'
    prefix = "test"
    flag = .true.
/
ATOMIC_SPECIES
Si 28.085 Si.upf
"""
        lexer = QELexer(text)
        tokens = lexer.tokenize()

        # Should have various token types
        types = [t.type for t in tokens]
        assert TokenType.NAMELIST_START in types
        assert TokenType.NAMELIST_END in types
        assert TokenType.CARD_NAME in types
        assert TokenType.STRING in types
        assert TokenType.BOOLEAN in types

    def test_parser_parse_value_invalid(self):
        """Test parse_value with invalid token type."""
        from qe_lsp.parser import QEParser, TokenType

        parser = QEParser("")
        # Manually set up to have a comment as current token
        parser.tokens = [MagicMock(type=TokenType.COMMENT, value="! comment", line=1, column=1)]
        parser.pos = 0

        result = parser.parse_value()
        assert result is None

    def test_parser_parse_card_no_start(self):
        """Test parse_card when not at card start."""
        from qe_lsp.parser import QEParser, TokenType

        parser = QEParser("")
        # Set up to not be at a CARD_NAME token
        parser.tokens = [MagicMock(type=TokenType.PARAMETER, value="param", line=1, column=1)]
        parser.pos = 0

        result = parser.parse_card()
        assert result is None

    def test_parser_parse_namelist_no_start(self):
        """Test parse_namelist when not at namelist start."""
        from qe_lsp.parser import QEParser, TokenType

        parser = QEParser("")
        # Set up to not be at a NAMELIST_START token
        parser.tokens = [MagicMock(type=TokenType.PARAMETER, value="param", line=1, column=1)]
        parser.pos = 0

        result = parser.parse_namelist()
        assert result is None

    def test_parser_error_method(self):
        """Test parser error method."""
        from qe_lsp.parser import QEParser, TokenType

        parser = QEParser("")
        token = MagicMock(type=TokenType.PARAMETER, value="test", line=5, column=10)
        parser.error("Test error", token)

        assert len(parser.errors) == 1
        assert parser.errors[0]["message"] == "Test error"
        assert parser.errors[0]["line"] == 5
        assert parser.errors[0]["column"] == 10

    def test_parser_expect_wrong_type(self):
        """Test expect method with wrong token type."""
        from qe_lsp.parser import QEParser, TokenType

        parser = QEParser("")
        parser.tokens = [MagicMock(type=TokenType.PARAMETER, value="param", line=1, column=1)]
        parser.pos = 0

        result = parser.expect(TokenType.NAMELIST_START)
        assert result is None

    def test_parser_advance_at_end(self):
        """Test advance when at end of tokens."""
        from qe_lsp.parser import QEParser, TokenType

        parser = QEParser("")
        parser.tokens = [MagicMock(type=TokenType.EOF, value="", line=1, column=1)]
        parser.pos = 0

        result = parser.advance()
        # Should return current token and not advance beyond
        assert result.type == TokenType.EOF
        assert parser.pos == 0  # Should not advance past EOF

    def test_get_word_at_position_various_cases(self):
        """Test get_word_at_position with various cases."""
        from qe_lsp.parser import get_word_at_position

        text = "hello world\nsecond line"

        # First word
        word, start, end = get_word_at_position(text, 0, 0)
        assert word == "hello"

        # Second word
        word, start, end = get_word_at_position(text, 0, 6)
        assert word == "world"

        # Position in middle of word
        word, start, end = get_word_at_position(text, 0, 2)
        assert word == "hello"

        # Out of range line
        word, start, end = get_word_at_position(text, 10, 0)
        assert word is None

        # Out of range column
        word, start, end = get_word_at_position(text, 0, 100)
        assert word is None


class TestIntegrationFinal:
    """Final integration tests."""

    def test_full_parse_example_file(self):
        """Test parsing a complete example file."""
        from qe_lsp.parser import parse_qe_input

        text = """&control
    calculation = 'scf'
    prefix = 'silicon'
    pseudo_dir = './'
    outdir = './tmp/'
    tstress = .true.
    tprnfor = .true.
/

&system
    ibrav = 2
    celldm(1) = 10.20
    nat = 2
    ntyp = 1
    ecutwfc = 30.0
/

&electrons
    conv_thr = 1.0d-8
/

ATOMIC_SPECIES
 Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS alat
 Si   0.000000000   0.000000000   0.000000000
 Si   0.250000000   0.250000000   0.250000000

K_POINTS automatic
 6 6 6 0 0 0
"""
        result = parse_qe_input(text)

        assert "control" in result.namelists
        assert "system" in result.namelists
        assert "electrons" in result.namelists
        assert "ATOMIC_SPECIES" in result.cards
        assert "ATOMIC_POSITIONS" in result.cards
        assert "K_POINTS" in result.cards

    def test_all_namelists_have_params(self):
        """Test that all namelists return params."""
        from qe_lsp.parser import get_namelist_params

        namelists = ["control", "system", "electrons", "ions", "cell"]
        for nl in namelists:
            params = get_namelist_params(nl)
            assert isinstance(params, list)
            assert len(params) > 0

        # Unknown namelist returns empty list
        assert get_namelist_params("unknown") == []

    def test_all_cards_returned(self):
        """Test that get_card_names returns cards."""
        from qe_lsp.parser import get_card_names

        cards = get_card_names()
        assert isinstance(cards, list)
        assert len(cards) > 0
        assert "ATOMIC_SPECIES" in cards
        assert "ATOMIC_POSITIONS" in cards
        assert "ATOMIC_K_POINTS" not in cards or "K_POINTS" in cards

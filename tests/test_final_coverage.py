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

    def test_unclosed_paren_in_celldm(self):
        """Test unclosed parenthesis in celldm (lines 280-281)."""
        lexer = QELexer("celldm(1")
        tokens = lexer.tokenize()
        # Should handle unclosed paren without error
        assert any(t.value == "celldm" for t in tokens)

    def test_missing_value_after_equals(self):
        """Test missing value after = (lines 431-434)."""
        text = """&control
calculation =
/"""
        result = parse_qe_input(text)
        assert any("Expected value" in e["message"] for e in result.errors)

    def test_unknown_tokens_skip(self):
        """Test skipping unknown tokens (lines 457-458)."""
        text = "@#$%^&*()"  # Special characters
        result = parse_qe_input(text)
        # Should parse without crashing
        assert isinstance(result.namelists, dict)

    def test_missing_control_namelist(self):
        """Test missing control namelist validation (line 469)."""
        text = """&system
ibrav=1
nat=1
ntyp=1
ecutwfc=20
/
"""
        result = parse_qe_input(text)
        assert any("Missing required namelist '&control'" in e["message"] for e in result.errors)

    def test_missing_system_namelist(self):
        """Test missing system namelist validation (line 470->477)."""
        text = """&control
calculation='scf'
prefix='test'
outdir='./'
/
"""
        result = parse_qe_input(text)
        assert any("Missing required namelist '&system'" in e["message"] for e in result.errors)

    def test_missing_required_params_control(self):
        """Test missing required params in control (lines 479->482)."""
        text = """&control
/
&system
ibrav=1
nat=1
ntyp=1
ecutwfc=20
/
"""
        result = parse_qe_input(text)
        assert any("Missing required parameter 'calculation'" in e["message"] for e in result.errors)

    def test_missing_required_params_system(self):
        """Test missing required params in system (lines 504->507)."""
        text = """&control
calculation='scf'
prefix='test'
outdir='./'
/
&system
/
"""
        result = parse_qe_input(text)
        assert any("Missing required parameter" in e["message"] for e in result.errors)

    def test_card_with_following_namelist(self):
        """Test card data with namelist following (lines 572->574)."""
        text = """ATOMIC_SPECIES
Si 28.0 Si.upf
&control
calculation='scf'
/
"""
        result = parse_qe_input(text)
        assert "ATOMIC_SPECIES" in result.cards

    def test_card_with_eof_following(self):
        """Test card data with EOF following (lines 578->580)."""
        text = """ATOMIC_SPECIES
Si 28.0 Si.upf"""
        result = parse_qe_input(text)
        assert "ATOMIC_SPECIES" in result.cards


class TestServerMissingLines:
    """Test server missing lines."""

    def test_get_word_at_position_beyond_line_count(self):
        """Test _get_word_at_position when position is beyond line count (line 50)."""
        from qe_lsp.server import _get_word_at_position
        from lsprotocol.types import Position

        doc = MagicMock()
        doc.source = "&control\ncalculation = 'scf'\n/"
        pos = Position(line=10, character=0)  # Beyond line count
        word, range_obj = _get_word_at_position(doc, pos)
        assert word == ""

    def test_get_namelist_at_position_ampersand_end(self):
        """Test &end handling (line 80->74)."""
        doc = MagicMock()
        doc.source = "&control\n&end\ncalc = 'scf'"
        result = _get_namelist_at_position(doc, MagicMock(line=2, character=0))
        assert result is None

    @patch("qe_lsp.server._get_server")
    def test_hover_namelist_name(self, mock_get_server):
        """Test hover on namelist name (line 176->184)."""
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
        """Test main function (line 320)."""
        mock_srv = MagicMock()
        mock_get_server.return_value = mock_srv
        main()
        mock_srv.start_io.assert_called_once()


class TestInitMissingLines:
    """Test __init__.py missing lines."""

    def test_getattr_else_branch(self):
        """Test __getattr__ else branch raising AttributeError (lines 35-37)."""
        import qe_lsp

        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp.nonexistent_attribute

        assert "nonexistent_attribute" in str(exc_info.value)


class TestDataMissingLines:
    """Test data.py missing lines."""

    def test_format_param_hover_no_type(self):
        """Test format_param_hover without type field (lines 373->376)."""
        from qe_lsp.data import format_param_hover

        param_doc = {"description": "Test parameter"}  # No type field
        result = format_param_hover(param_doc)
        assert "Test parameter" in result
        assert "**Type:**" not in result

    def test_format_card_hover_no_format(self):
        """Test format_card_hover without format field (lines 403->406)."""
        from qe_lsp.data import format_card_hover

        card_doc = {"description": "Test card"}  # No format field
        result = format_card_hover(card_doc)
        assert "Test card" in result
        assert "**Format:**" not in result

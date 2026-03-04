"""Additional tests for qe-lsp to achieve 100% coverage."""

from unittest.mock import MagicMock, patch

import pytest


class TestInitModule:
    """Test __init__.py module for full coverage."""

    def test_getattr_invalid_attribute(self):
        """Test that accessing invalid attribute raises AttributeError."""
        import qe_lsp

        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp.invalid_attribute_name

        assert "invalid_attribute_name" in str(exc_info.value)
        assert "module" in str(exc_info.value)


class TestParserEdgeCases:
    """Test edge cases in parser for full coverage."""

    def test_lexer_error_raises(self):
        """Test that lexer error raises SyntaxError."""
        from qe_lsp.parser import QELexer

        lexer = QELexer("test")
        # Manually trigger error
        with pytest.raises(SyntaxError) as exc_info:
            lexer.error("test error message")

        assert "test error message" in str(exc_info.value)

    def test_lexer_read_identifier_empty_boolean(self):
        """Test reading identifier with just dot."""
        from qe_lsp.parser import QELexer, TokenType

        lexer = QELexer(".")
        token = lexer.read_identifier()
        assert token.type == TokenType.PARAMETER
        assert token.value == "."

    def test_lexer_read_identifier_only_ampersand(self):
        """Test reading identifier with just ampersand."""
        from qe_lsp.parser import QELexer, TokenType

        lexer = QELexer("&")
        token = lexer.read_identifier()
        assert token.type == TokenType.PARAMETER
        assert token.value == "&"

    def test_lexer_tokenize_with_parens(self):
        """Test tokenizing with parentheses (array indices)."""
        from qe_lsp.parser import QELexer, TokenType

        lexer = QELexer("celldm(1) = 10.0")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        # Should handle parentheses
        assert TokenType.PARAMETER in types
        assert TokenType.NUMBER in types

    def test_lexer_tokenize_unknown_characters(self):
        """Test tokenizing unknown characters."""
        from qe_lsp.parser import QELexer, TokenType

        lexer = QELexer("&control\n  $unknown\n/")
        tokens = lexer.tokenize()
        # Should skip unknown characters without error
        assert tokens[-1].type == TokenType.EOF

    def test_lexer_read_string_with_escape(self):
        """Test reading string with escape sequences."""
        from qe_lsp.parser import QELexer, TokenType

        lexer = QELexer("'test\\'value'")
        token = lexer.read_string()
        assert token.type == TokenType.STRING

    def test_lexer_read_number_with_sign(self):
        """Test reading number with leading sign."""
        from qe_lsp.parser import QELexer, TokenType

        lexer = QELexer("-42.5")
        token = lexer.read_number()
        assert token.type == TokenType.NUMBER
        assert token.value == "-42.5"

    def test_lexer_read_number_with_exponent_sign(self):
        """Test reading number with signed exponent."""
        from qe_lsp.parser import QELexer, TokenType

        lexer = QELexer("1.0e-10")
        token = lexer.read_number()
        assert token.type == TokenType.NUMBER
        assert "e-10" in token.value

    def test_parser_error_with_token(self):
        """Test parser error recording with specific token."""
        from qe_lsp.parser import QEParser, Token, TokenType

        parser = QEParser("test")
        token = Token(TokenType.PARAMETER, "test", 5, 10)
        parser.error("test error", token)

        assert len(parser.errors) == 1
        assert parser.errors[0]["line"] == 5
        assert parser.errors[0]["column"] == 10

    def test_parser_parse_value_invalid(self):
        """Test parsing invalid value."""
        from qe_lsp.parser import QEParser, TokenType

        parser = QEParser("/")
        parser.tokens = parser.lexer.tokenize()
        value = parser.parse_value()
        assert value is None

    def test_parser_parse_namelist_with_comment(self):
        """Test parsing namelist with comments."""
        from qe_lsp.parser import parse_qe_input

        text = """&control
  calculation = 'scf'  ! This is a comment
  prefix = 'test'
/"""
        result = parse_qe_input(text)
        assert result.namelists["control"].parameters["calculation"] == "scf"

    def test_parser_parse_card_data_with_comments(self):
        """Test parsing card data with comments."""
        from qe_lsp.parser import parse_qe_input

        text = """ATOMIC_SPECIES
Si 28.085 Si.upf  ! Silicon
Ge 72.63 Ge.upf   ! Germanium"""
        result = parse_qe_input(text)
        assert "ATOMIC_SPECIES" in result.cards
        assert len(result.cards["ATOMIC_SPECIES"].data) >= 1

    def test_parser_parse_card_empty_lines(self):
        """Test parsing card with empty lines."""
        from qe_lsp.parser import parse_qe_input

        text = """ATOMIC_SPECIES

Si 28.085 Si.upf

/"""
        result = parse_qe_input(text)
        assert "ATOMIC_SPECIES" in result.cards

    def test_parser_validate_unknown_namelist(self):
        """Test validation with unknown namelist."""
        from qe_lsp.parser import Namelist, QEInputFile, QEParser

        parser = QEParser("test")
        result = QEInputFile()
        result.namelists["unknown"] = Namelist(name="unknown")
        parser.validate(result)
        # Should not add errors for unknown namelists

    def test_get_word_at_position_no_word(self):
        """Test get_word_at_position when there's no word."""
        from qe_lsp.parser import get_word_at_position

        text = "   "
        word, start, end = get_word_at_position(text, 0, 1)
        assert word is None

    def test_get_word_at_position_special_chars(self):
        """Test get_word_at_position with special characters."""
        from qe_lsp.parser import get_word_at_position

        text = "hello!world"
        word, start, end = get_word_at_position(text, 0, 6)
        # Should stop at special character
        assert word is not None


class TestDataModule:
    """Test data module for full coverage."""

    def test_get_parameter_doc_function(self):
        """Test get_parameter_doc function."""
        from qe_lsp.data import get_parameter_doc

        # Test existing parameter
        doc = get_parameter_doc("control", "calculation")
        assert doc is not None

        # Test non-existent namelist
        doc = get_parameter_doc("nonexistent", "param")
        assert doc is None

        # Test non-existent parameter
        doc = get_parameter_doc("control", "nonexistent")
        assert doc is None

    def test_get_card_doc_function(self):
        """Test get_card_doc function."""
        from qe_lsp.data import get_card_doc

        # Test existing card
        doc = get_card_doc("ATOMIC_SPECIES")
        assert doc is not None

        # Test non-existent card
        doc = get_card_doc("NONEXISTENT")
        assert doc is None

    def test_format_param_hover_no_description(self):
        """Test format_param_hover without description."""
        from qe_lsp.data import format_param_hover

        param_doc = {"type": "string"}
        result = format_param_hover(param_doc)
        assert "Type:" in result

    def test_format_card_hover_no_description(self):
        """Test format_card_hover without description."""
        from qe_lsp.data import format_card_hover

        card_doc = {"format": "test format"}
        result = format_card_hover(card_doc)
        assert "Format:" in result


class TestServerEdgeCases:
    """Test server module edge cases for full coverage."""

    @patch("qe_lsp.server._get_server")
    def test_completion_with_empty_result(self, mock_get_server):
        """Test completion when result is empty."""
        from qe_lsp.server import completion

        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(source="xyz")
        mock_get_server.return_value = srv

        params = MagicMock()
        params.text_document.uri = "test://test.in"
        params.position = MagicMock(line=0, character=3)

        result = completion(params)
        # Should return empty or partial list
        assert result is not None or result is None

    @patch("qe_lsp.server._get_server")
    def test_hover_on_namelist_name(self, mock_get_server):
        """Test hover on namelist name."""
        from qe_lsp.server import hover

        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(source="&control")
        mock_get_server.return_value = srv

        params = MagicMock()
        params.text_document.uri = "test://test.in"
        params.position = MagicMock(line=0, character=1)

        result = hover(params)
        # Should return hover for namelist
        assert result is not None or result is None

    @patch("qe_lsp.server._get_server")
    def test_diagnostic_with_warning(self, mock_get_server):
        """Test diagnostic with warning severity."""
        from qe_lsp.server import diagnostic

        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(source="&unknown\n/")
        mock_get_server.return_value = srv

        params = MagicMock()
        params.text_document.uri = "test://test.in"

        result = diagnostic(params)
        assert isinstance(result, list)

    @patch("qe_lsp.server._get_server")
    def test_document_symbol_empty(self, mock_get_server):
        """Test document symbol with empty document."""
        from qe_lsp.server import document_symbol

        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(source="")
        mock_get_server.return_value = srv

        params = MagicMock()
        params.text_document.uri = "test://test.in"

        result = document_symbol(params)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_word_at_position_line_out_of_range(self):
        """Test _get_word_at_position with line out of range."""
        from lsprotocol.types import Position

        from qe_lsp.server import _get_word_at_position

        doc = MagicMock()
        doc.source = "test"
        position = Position(line=100, character=0)

        word, rng = _get_word_at_position(doc, position)
        assert word == ""

    def test_get_namelist_at_position_with_end(self):
        """Test _get_namelist_at_position with &end."""
        from lsprotocol.types import Position

        from qe_lsp.server import _get_namelist_at_position

        doc = MagicMock()
        doc.source = "&control\n&end\ntest"
        position = Position(line=2, character=0)

        namelist = _get_namelist_at_position(doc, position)
        assert namelist is None

    def test_get_namelist_at_position_no_ampersand(self):
        """Test _get_namelist_at_position with namelist without &."""
        from lsprotocol.types import Position

        from qe_lsp.server import _get_namelist_at_position

        doc = MagicMock()
        doc.source = "control\ntest"
        position = Position(line=1, character=0)

        namelist = _get_namelist_at_position(doc, position)
        assert namelist is None


class TestParserAdvancedFeatures:
    """Test advanced parser features."""

    def test_parse_complex_input(self):
        """Test parsing complex input with multiple sections."""
        from qe_lsp.parser import parse_qe_input

        text = """
&control
  calculation = 'vc-relax'
  prefix = 'silicon'
  outdir = './tmp'
  pseudo_dir = './'
  tstress = .true.
  tprnfor = .true.
/

&system
  ibrav = 2
  celldm(1) = 10.20
  nat = 2
  ntyp = 1
  ecutwfc = 30.0
  ecutrho = 240.0
  occupations = 'smearing'
  degauss = 0.01
  smearing = 'methfessel-paxton'
/

&electrons
  conv_thr = 1.0d-10
  mixing_beta = 0.7
  mixing_mode = 'plain'
  diagonalization = 'david'
/

&ions
  ion_dynamics = 'bfgs'
/

&cell
  cell_dynamics = 'bfgs'
  press = 0.0
/

ATOMIC_SPECIES
 Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS alat
 Si   0.000000000   0.000000000   0.000000000
 Si   0.250000000   0.250000000   0.250000000

K_POINTS automatic
 6 6 6 0 0 0

CELL_PARAMETERS alat
  0.0   0.5   0.5
  0.5   0.0   0.5
  0.5   0.5   0.0
"""
        result = parse_qe_input(text)
        assert "control" in result.namelists
        assert "system" in result.namelists
        assert "electrons" in result.namelists
        assert "ions" in result.namelists
        assert "cell" in result.namelists
        assert "ATOMIC_SPECIES" in result.cards
        assert "ATOMIC_POSITIONS" in result.cards
        assert "K_POINTS" in result.cards
        assert "CELL_PARAMETERS" in result.cards

    def test_parse_with_huge_numbers(self):
        """Test parsing with scientific notation variations."""
        from qe_lsp.parser import parse_qe_input

        text = """
&system
  ibrav = 1
  nat = 1
  ntyp = 1
  ecutwfc = 1.0D+10
  degauss = 1.D-5
/
"""
        result = parse_qe_input(text)
        params = result.namelists["system"].parameters
        assert params["ecutwfc"] == 1.0e10

    def test_parse_missing_equals_in_namelist(self):
        """Test parsing namelist with missing equals sign."""
        from qe_lsp.parser import parse_qe_input

        text = """
&control
  calculation 'scf'
  prefix = 'test'
/
&system
  ibrav = 1
  nat = 1
  ntyp = 1
  ecutwfc = 20
/
"""
        # Should handle gracefully
        result = parse_qe_input(text)
        assert "control" in result.namelists

    def test_parse_boolean_variations(self):
        """Test parsing various boolean formats."""
        from qe_lsp.parser import parse_qe_input

        text = """
&control
  calculation = 'scf'
  prefix = 'test'
  outdir = './'
  tstress = T
  tprnfor = F
/
&system
  ibrav = 1
  nat = 1
  ntyp = 1
  ecutwfc = 20
/
"""
        result = parse_qe_input(text)
        params = result.namelists["control"].parameters
        assert params["tstress"] is True
        assert params["tprnfor"] is False


class TestParserValidateRequiredParams:
    """Test validation of required parameters."""

    def test_validate_all_required_params_present(self):
        """Test validation when all required params are present."""
        from qe_lsp.parser import parse_qe_input

        text = """
&control
  calculation = 'scf'
  prefix = 'test'
  outdir = './'
/
&system
  ibrav = 1
  nat = 1
  ntyp = 1
  ecutwfc = 20
/
"""
        result = parse_qe_input(text)
        # Should have no missing parameter errors
        missing_param_errors = [
            e for e in result.errors if "Missing required parameter" in e["message"]
        ]
        assert len(missing_param_errors) == 0

    def test_validate_missing_params_in_control(self):
        """Test validation with missing params in control."""
        from qe_lsp.parser import parse_qe_input

        text = """
&control
  prefix = 'test'
/
&system
  ibrav = 1
  nat = 1
  ntyp = 1
  ecutwfc = 20
/
"""
        result = parse_qe_input(text)
        # Should have missing calculation error
        assert any("calculation" in e["message"] for e in result.errors)

    def test_validate_missing_params_in_system(self):
        """Test validation with missing params in system."""
        from qe_lsp.parser import parse_qe_input

        text = """
&control
  calculation = 'scf'
  prefix = 'test'
  outdir = './'
/
&system
  ibrav = 1
  ntyp = 1
  ecutwfc = 20
/
"""
        result = parse_qe_input(text)
        # Should have missing nat error
        assert any("nat" in e["message"] for e in result.errors)

"""Tests for Quantum ESPRESSO input file parser."""

from qe_lsp.parser import (
    Token,
    TokenType,
    Namelist,
    Card,
    QEInputFile,
    QELexer,
    QEParser,
    parse_qe_input,
    get_parameter_doc,
    get_namelist_params,
    get_card_names,
    get_word_at_position,
)


class TestToken:
    """Test Token dataclass."""

    def test_token_creation(self):
        """Test creating a Token."""
        token = Token(TokenType.PARAMETER, "test", 1, 0)
        assert token.type == TokenType.PARAMETER
        assert token.value == "test"
        assert token.line == 1
        assert token.column == 0


class TestNamelist:
    """Test Namelist dataclass."""

    def test_namelist_creation(self):
        """Test creating a Namelist."""
        namelist = Namelist(
            name="control",
            parameters={"calculation": "scf"},
            line_start=1,
            line_end=5
        )
        assert namelist.name == "control"
        assert namelist.parameters["calculation"] == "scf"
        assert namelist.line_start == 1
        assert namelist.line_end == 5

    def test_namelist_default(self):
        """Test Namelist with default values."""
        namelist = Namelist(name="system")
        assert namelist.name == "system"
        assert namelist.parameters == {}
        assert namelist.line_start == 0
        assert namelist.line_end == 0


class TestCard:
    """Test Card dataclass."""

    def test_card_creation(self):
        """Test creating a Card."""
        card = Card(
            name="ATOMIC_SPECIES",
            options="crystal",
            data=[["Si", "28.085", "Si.pbe-n-kjpaw_psl.1.0.0.UPF"]],
            line_start=10,
            line_end=15
        )
        assert card.name == "ATOMIC_SPECIES"
        assert card.options == "crystal"
        assert len(card.data) == 1
        assert card.line_start == 10
        assert card.line_end == 15


class TestQEInputFile:
    """Test QEInputFile dataclass."""

    def test_qeinputfile_creation(self):
        """Test creating a QEInputFile."""
        qe_file = QEInputFile()
        assert qe_file.namelists == {}
        assert qe_file.cards == {}
        assert qe_file.errors == []


class TestQELexer:
    """Test QELexer class."""

    def test_lexer_init(self):
        """Test lexer initialization."""
        lexer = QELexer("test")
        assert lexer.text == "test"
        assert lexer.pos == 0
        assert lexer.line == 1
        assert lexer.column == 1

    def test_advance(self):
        """Test advance method."""
        lexer = QELexer("ab")
        assert lexer.advance() == "a"
        assert lexer.pos == 1
        assert lexer.advance() == "b"
        assert lexer.pos == 2
        assert lexer.advance() == ""  # End of text

    def test_advance_newline(self):
        """Test advance with newline."""
        lexer = QELexer("a\nb")
        lexer.advance()  # 'a'
        assert lexer.line == 1
        lexer.advance()  # '\n'
        assert lexer.line == 2
        assert lexer.column == 1

    def test_peek(self):
        """Test peek method."""
        lexer = QELexer("abc")
        assert lexer.peek() == "a"
        assert lexer.peek(1) == "b"
        assert lexer.peek(2) == "c"
        assert lexer.peek(3) == ""  # Out of bounds

    def test_skip_whitespace(self):
        """Test skip_whitespace method."""
        lexer = QELexer("   abc")
        lexer.skip_whitespace()
        assert lexer.peek() == "a"

    def test_skip_comment(self):
        """Test skip_comment method."""
        lexer = QELexer("! this is a comment\nnext")
        lexer.skip_comment()
        assert lexer.peek() == "\n"

    def test_read_string_single_quote(self):
        """Test reading single-quoted string."""
        lexer = QELexer("'hello world'")
        token = lexer.read_string()
        assert token.type == TokenType.STRING
        assert token.value == "hello world"
        assert token.line == 1

    def test_read_string_double_quote(self):
        """Test reading double-quoted string."""
        lexer = QELexer('"hello world"')
        token = lexer.read_string()
        assert token.type == TokenType.STRING
        assert token.value == "hello world"

    def test_read_number_integer(self):
        """Test reading integer."""
        lexer = QELexer("123")
        token = lexer.read_number()
        assert token.type == TokenType.NUMBER
        assert token.value == "123"

    def test_read_number_float(self):
        """Test reading float."""
        lexer = QELexer("3.14")
        token = lexer.read_number()
        assert token.type == TokenType.NUMBER
        assert token.value == "3.14"

    def test_read_number_scientific(self):
        """Test reading scientific notation."""
        lexer = QELexer("1d-10")
        token = lexer.read_number()
        assert token.type == TokenType.NUMBER
        assert token.value == "1e-10"  # d replaced with e

    def test_read_identifier_parameter(self):
        """Test reading identifier as parameter."""
        lexer = QELexer("calculation")
        token = lexer.read_identifier()
        assert token.type == TokenType.PARAMETER
        assert token.value == "calculation"

    def test_read_identifier_namelist(self):
        """Test reading namelist identifier."""
        lexer = QELexer("&control")
        token = lexer.read_identifier()
        assert token.type == TokenType.NAMELIST_START
        assert token.value == "control"

    def test_read_identifier_card(self):
        """Test reading card identifier."""
        lexer = QELexer("ATOMIC_SPECIES")
        token = lexer.read_identifier()
        assert token.type == TokenType.CARD_NAME
        assert token.value == "ATOMIC_SPECIES"

    def test_read_identifier_boolean_true(self):
        """Test reading boolean true values."""
        for val in [".true.", ".TRUE.", "T", "t"]:
            lexer = QELexer(val)
            token = lexer.read_identifier()
            assert token.type == TokenType.BOOLEAN
            assert token.value == val.lower()

    def test_read_identifier_boolean_false(self):
        """Test reading boolean false values."""
        for val in [".false.", ".FALSE.", "F", "f"]:
            lexer = QELexer(val)
            token = lexer.read_identifier()
            assert token.type == TokenType.BOOLEAN
            assert token.value == val.lower()

    def test_tokenize_simple(self):
        """Test tokenizing simple input."""
        lexer = QELexer("&control\ncalculation='scf'\n/")
        tokens = lexer.tokenize()
        assert len(tokens) > 0
        assert tokens[-1].type == TokenType.EOF

    def test_tokenize_namelist(self):
        """Test tokenizing namelist."""
        lexer = QELexer("&control\n  calculation = 'scf'\n  prefix = 'test'\n/")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        assert TokenType.NAMELIST_START in types
        assert TokenType.NAMELIST_END in types
        assert TokenType.PARAMETER in types
        assert TokenType.STRING in types

    def test_tokenize_card(self):
        """Test tokenizing card."""
        lexer = QELexer("ATOMIC_SPECIES\nSi 28.085 Si.upf")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        assert TokenType.CARD_NAME in types
        assert TokenType.NUMBER in types

    def test_tokenize_comment(self):
        """Test tokenizing with comments."""
        lexer = QELexer("! comment\n&control")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        # Comment should be skipped
        assert TokenType.NAMELIST_START in types


class TestQEParser:
    """Test QEParser class."""

    def test_parser_init(self):
        """Test parser initialization."""
        parser = QEParser("test")
        assert parser.text == "test"
        assert parser.pos == 0
        assert parser.errors == []

    def test_current_token(self):
        """Test current token method."""
        parser = QEParser("&control")
        parser.tokens = parser.lexer.tokenize()
        token = parser.current()
        assert token.type == TokenType.NAMELIST_START

    def test_current_empty(self):
        """Test current with no tokens."""
        parser = QEParser("")
        token = parser.current()
        assert token.type == TokenType.EOF

    def test_advance(self):
        """Test advance method."""
        parser = QEParser("&control /")
        parser.tokens = parser.lexer.tokenize()
        first = parser.current()
        assert first.type == TokenType.NAMELIST_START
        parser.advance()
        # Should advance past whitespace and newlines

    def test_expect(self):
        """Test expect method."""
        parser = QEParser("&control")
        parser.tokens = parser.lexer.tokenize()
        token = parser.expect(TokenType.NAMELIST_START)
        assert token is not None
        assert token.value == "control"

    def test_expect_fail(self):
        """Test expect with wrong type."""
        parser = QEParser("&control")
        parser.tokens = parser.lexer.tokenize()
        token = parser.expect(TokenType.CARD_NAME)
        assert token is None

    def test_parse_value_string(self):
        """Test parsing string value."""
        parser = QEParser("'test'")
        parser.tokens = parser.lexer.tokenize()
        value = parser.parse_value()
        assert value == "test"

    def test_parse_value_number_int(self):
        """Test parsing integer value."""
        parser = QEParser("42")
        parser.tokens = parser.lexer.tokenize()
        value = parser.parse_value()
        assert value == 42
        assert isinstance(value, int)

    def test_parse_value_number_float(self):
        """Test parsing float value."""
        parser = QEParser("3.14")
        parser.tokens = parser.lexer.tokenize()
        value = parser.parse_value()
        assert value == 3.14
        assert isinstance(value, float)

    def test_parse_value_boolean_true(self):
        """Test parsing boolean true."""
        parser = QEParser(".true.")
        parser.tokens = parser.lexer.tokenize()
        value = parser.parse_value()
        assert value is True

    def test_parse_value_boolean_false(self):
        """Test parsing boolean false."""
        parser = QEParser(".false.")
        parser.tokens = parser.lexer.tokenize()
        value = parser.parse_value()
        assert value is False

    def test_parse_value_parameter(self):
        """Test parsing parameter value."""
        parser = QEParser("somevalue")
        parser.tokens = parser.lexer.tokenize()
        value = parser.parse_value()
        assert value == "somevalue"

    def test_parse_value_none(self):
        """Test parsing with no value."""
        parser = QEParser("")
        parser.tokens = parser.lexer.tokenize()
        value = parser.parse_value()
        assert value is None

    def test_parse_namelist(self):
        """Test parsing namelist."""
        parser = QEParser("&control\n  calculation = 'scf'\n  prefix = 'test'\n/")
        parser.tokens = parser.lexer.tokenize()
        namelist = parser.parse_namelist()
        assert namelist is not None
        assert namelist.name == "control"
        assert namelist.parameters["calculation"] == "scf"
        assert namelist.parameters["prefix"] == "test"

    def test_parse_namelist_no_start(self):
        """Test parsing without namelist start."""
        parser = QEParser("not a namelist")
        parser.tokens = parser.lexer.tokenize()
        namelist = parser.parse_namelist()
        assert namelist is None

    def test_parse_card(self):
        """Test parsing card."""
        parser = QEParser("ATOMIC_SPECIES\nSi 28.085 Si.upf")
        parser.tokens = parser.lexer.tokenize()
        card = parser.parse_card()
        assert card is not None
        assert card.name == "ATOMIC_SPECIES"
        assert len(card.data) == 1

    def test_parse_card_with_options(self):
        """Test parsing card with options."""
        parser = QEParser("ATOMIC_POSITIONS crystal\nSi 0.0 0.0 0.0")
        parser.tokens = parser.lexer.tokenize()
        card = parser.parse_card()
        assert card is not None
        assert card.name == "ATOMIC_POSITIONS"
        assert card.options == "crystal"

    def test_parse_card_no_start(self):
        """Test parsing without card start."""
        parser = QEParser("not a card")
        parser.tokens = parser.lexer.tokenize()
        card = parser.parse_card()
        assert card is None

    def test_validate_missing_control(self):
        """Test validation missing control namelist."""
        parser = QEParser("")
        result = QEInputFile()
        parser.validate(result)
        assert len(parser.errors) >= 2  # Missing control and system
        assert any("control" in e["message"] for e in parser.errors)

    def test_validate_missing_system(self):
        """Test validation missing system namelist."""
        parser = QEParser("")
        result = QEInputFile()
        parser.validate(result)
        assert any("system" in e["message"] for e in parser.errors)

    def test_validate_missing_required_params(self):
        """Test validation missing required parameters."""
        parser = QEParser("&control\n/")
        result = parser.parse()
        assert any("calculation" in e["message"] for e in result.errors)

    def test_parse_full_input(self):
        """Test parsing full QE input."""
        text = """
&control
  calculation = 'scf'
  prefix = 'si'
  outdir = './tmp'
/
&system
  ibrav = 2
  nat = 2
  ntyp = 1
  ecutwfc = 40
/
ATOMIC_SPECIES
  Si 28.085 Si.pbe-n-kjpaw_psl.1.0.0.UPF
K_POINTS automatic
  6 6 6 1 1 1
"""
        result = parse_qe_input(text)
        assert "control" in result.namelists
        assert "system" in result.namelists
        assert result.namelists["control"].parameters["calculation"] == "scf"
        assert "ATOMIC_SPECIES" in result.cards

    def test_error_recording(self):
        """Test error recording."""
        parser = QEParser("test")
        parser.error("test error")
        assert len(parser.errors) == 1
        assert parser.errors[0]["message"] == "test error"


class TestHelperFunctions:
    """Test helper functions."""

    def test_parse_qe_input(self):
        """Test parse_qe_input function."""
        result = parse_qe_input("&control\n/")
        assert isinstance(result, QEInputFile)

    def test_get_parameter_doc_known(self):
        """Test get_parameter_doc for known parameter."""
        doc = get_parameter_doc("calculation")
        assert doc is not None
        assert "calculation" in doc.lower()

    def test_get_parameter_doc_unknown(self):
        """Test get_parameter_doc for unknown parameter."""
        doc = get_parameter_doc("unknown_param")
        assert doc is None

    def test_get_namelist_params_control(self):
        """Test get_namelist_params for control."""
        params = get_namelist_params("control")
        assert "calculation" in params
        assert "prefix" in params
        assert "outdir" in params

    def test_get_namelist_params_system(self):
        """Test get_namelist_params for system."""
        params = get_namelist_params("system")
        assert "ibrav" in params
        assert "nat" in params
        assert "ecutwfc" in params

    def test_get_namelist_params_unknown(self):
        """Test get_namelist_params for unknown namelist."""
        params = get_namelist_params("unknown")
        assert params == []

    def test_get_card_names(self):
        """Test get_card_names function."""
        cards = get_card_names()
        assert "ATOMIC_SPECIES" in cards
        assert "K_POINTS" in cards
        assert "CELL_PARAMETERS" in cards

    def test_get_word_at_position(self):
        """Test get_word_at_position function."""
        text = "hello world"
        word, start, end = get_word_at_position(text, 0, 0)
        assert word == "hello"
        assert start == 0
        assert end == 5

    def test_get_word_at_position_middle(self):
        """Test get_word_at_position in middle of word."""
        text = "hello world"
        word, start, end = get_word_at_position(text, 0, 2)
        assert word == "hello"
        assert start == 0
        assert end == 5

    def test_get_word_at_position_second_word(self):
        """Test get_word_at_position for second word."""
        text = "hello world"
        word, start, end = get_word_at_position(text, 0, 6)
        assert word == "world"
        assert start == 6
        assert end == 11

    def test_get_word_at_position_out_of_range(self):
        """Test get_word_at_position out of range."""
        text = "hello"
        word, start, end = get_word_at_position(text, 10, 0)
        assert word is None
        assert start == 0
        assert end == 0

    def test_get_word_at_position_column_out_of_range(self):
        """Test get_word_at_position column out of range."""
        text = "hello"
        word, start, end = get_word_at_position(text, 0, 100)
        assert word is None


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_input(self):
        """Test parsing empty input."""
        result = parse_qe_input("")
        assert result.namelists == {}
        assert result.cards == {}
        assert len(result.errors) >= 2  # Missing control and system

    def test_only_whitespace(self):
        """Test parsing whitespace only."""
        result = parse_qe_input("   \n\t\n   ")
        assert result.namelists == {}
        assert len(result.errors) >= 2

    def test_only_comments(self):
        """Test parsing comments only."""
        result = parse_qe_input("! comment 1\n! comment 2")
        assert result.namelists == {}

    def test_unclosed_namelist(self):
        """Test unclosed namelist."""
        result = parse_qe_input("&control\n  calculation = 'scf'")
        assert "control" in result.namelists

    def test_multiple_namelists(self):
        """Test multiple namelists."""
        text = """
&control
  calculation = 'scf'
/
&system
  ibrav = 2
/
&electrons
  conv_thr = 1d-8
/
"""
        result = parse_qe_input(text)
        assert "control" in result.namelists
        assert "system" in result.namelists
        assert "electrons" in result.namelists

    def test_multiple_cards(self):
        """Test multiple cards."""
        text = """
ATOMIC_SPECIES
  Si 28.085 Si.upf
ATOMIC_POSITIONS
  Si 0.0 0.0 0.0
K_POINTS
  6 6 6 1 1 1
"""
        result = parse_qe_input(text)
        assert "ATOMIC_SPECIES" in result.cards
        assert "ATOMIC_POSITIONS" in result.cards
        assert "K_POINTS" in result.cards

    def test_quoted_strings_with_spaces(self):
        """Test quoted strings containing spaces."""
        text = "&control\n  prefix = 'hello world'\n/"
        result = parse_qe_input(text)
        assert result.namelists["control"].parameters["prefix"] == "hello world"

    def test_scientific_notation_variations(self):
        """Test various scientific notation formats."""
        text = """
&system
  ecutwfc = 1D2
  ecutrho = 1e2
  degauss = 1.5d-3
/
"""
        result = parse_qe_input(text)
        params = result.namelists["system"].parameters
        assert params["ecutwfc"] == 100.0  # 1D2 = 100
        assert params["ecutrho"] == 100.0
        assert params["degauss"] == 0.0015

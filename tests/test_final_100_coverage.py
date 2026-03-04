"""Final tests to achieve 100% code coverage."""

import pytest
from unittest.mock import MagicMock, patch
from lsprotocol.types import (
    CompletionParams,
    DocumentSymbolParams,
    HoverParams,
    Position,
    TextDocumentIdentifier,
)

from qe_lsp.parser import (
    QEInputFile,
    QEParser,
    QELexer,
    Token,
    TokenType,
    parse_qe_input,
)


class TestFinalCoverage:
    """Final tests for 100% coverage."""

    def test_init_getattr_invalid(self):
        """Test __getattr__ raises AttributeError for invalid name."""
        import qe_lsp
        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp.invalid_attribute_xyz
        assert "invalid_attribute_xyz" in str(exc_info.value)

    def test_init_getattr_server(self):
        """Test __getattr__ returns server."""
        import qe_lsp
        server = qe_lsp.server
        assert server is not None

    def test_init_getattr_main(self):
        """Test __getattr__ returns main."""
        import qe_lsp
        main_func = qe_lsp.main
        assert callable(main_func)

    def test_parser_lexer_read_identifier_boolean_dot_true(self):
        """Test lexer handles .true. boolean."""
        lexer = QELexer("&control\nflag = .true.\n/")
        tokens = lexer.tokenize()
        bool_tokens = [t for t in tokens if t.type == TokenType.BOOLEAN]
        assert len(bool_tokens) >= 1
        assert ".true." in [t.value for t in bool_tokens]

    def test_parser_lexer_read_identifier_boolean_dot_false(self):
        """Test lexer handles .false. boolean."""
        lexer = QELexer("&control\nflag = .false.\n/")
        tokens = lexer.tokenize()
        bool_tokens = [t for t in tokens if t.type == TokenType.BOOLEAN]
        assert len(bool_tokens) >= 1
        assert ".false." in [t.value for t in bool_tokens]

    def test_parser_validate_required_params(self):
        """Test validation catches missing required parameters."""
        text = """&control
/
&system
/"""
        parser = QEParser(text)
        result = parser.parse()
        assert len(result.errors) > 0
        error_messages = [e["message"] for e in result.errors]
        assert any("Missing required" in msg for msg in error_messages)

    def test_server_main(self):
        """Test main function starts server."""
        from qe_lsp.server import main, _get_server
        
        with patch.object(_get_server(), 'start_io') as mock_start:
            main()
            mock_start.assert_called_once()

    def test_parser_validate_missing_system(self):
        """Test validation catches missing &system."""
        text = """&control
calculation = 'scf'
prefix = 'test'
outdir = './tmp'
/"""
        parser = QEParser(text)
        result = parser.parse()
        error_messages = [e["message"] for e in result.errors]
        assert any("&system" in msg for msg in error_messages)

    def test_parser_validate_missing_control(self):
        """Test validation catches missing &control."""
        text = """&system
ibrav = 1
nat = 1
ntyp = 1
ecutwfc = 30
/"""
        parser = QEParser(text)
        result = parser.parse()
        error_messages = [e["message"] for e in result.errors]
        assert any("&control" in msg for msg in error_messages)

    def test_parser_error_without_token(self):
        """Test parser error method without token."""
        parser = QEParser("")
        parser.tokens = [Token(TokenType.EOF, "", 1, 1)]
        parser.pos = 0
        parser.error("Test error")
        assert len(parser.errors) == 1

    def test_server_get_namelist_with_end(self):
        """Test _get_namelist_at_position with &end."""
        from qe_lsp.server import _get_namelist_at_position
        
        doc = MagicMock()
        doc.source = "&control\ncalc='scf'\n&end\nafter"
        
        position = MagicMock()
        position.line = 3
        
        result = _get_namelist_at_position(doc, position)
        assert result is None

    def test_parser_lexer_empty_namelist_name(self):
        """Test lexer with empty namelist name after &."""
        lexer = QELexer("&\n/")
        tokens = lexer.tokenize()
        assert tokens[-1].type == TokenType.EOF

    def test_parser_main_loop_skip_unknown(self):
        """Test parser main loop skips unknown tokens."""
        text = """&control
calculation = 'scf'
prefix = 'test'
outdir = './tmp'
/
&system
ibrav = 1
nat = 1
ntyp = 1
ecutwfc = 30
/
UNKNOWN_TOKEN"""
        parser = QEParser(text)
        result = parser.parse()
        assert "control" in result.namelists
        assert "system" in result.namelists

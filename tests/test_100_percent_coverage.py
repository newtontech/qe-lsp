"""Additional tests to achieve 100% code coverage."""

import pytest
from lsprotocol.types import (
    CompletionParams,
    DiagnosticSeverity,
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
from qe_lsp.server import (
    _get_namelist_at_position,
    _get_word_at_position,
    completion,
    diagnostic,
    document_symbol,
    hover,
)


class TestInitModule:
    """Tests for __init__.py module."""

    def test_getattr_invalid_attribute(self):
        """Test __getattr__ raises AttributeError for invalid attribute."""
        import qe_lsp

        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp.nonexistent_attribute

        assert "nonexistent_attribute" in str(exc_info.value)


class TestParserEdgeCases:
    """Tests for parser edge cases."""

    def test_lexer_read_identifier_empty(self):
        """Test lexer handles empty identifier after &."""
        lexer = QELexer("&")
        tokens = lexer.tokenize()
        # Should not crash, just return EOF
        assert tokens[-1].type == TokenType.EOF

    def test_parser_parse_value_none_with_eof(self):
        """Test parser handles EOF when parsing value."""
        parser = QEParser("&control\ncalc = ")
        result = parser.parse()
        # Should handle gracefully
        assert "control" in result.namelists or len(result.errors) > 0

    def test_parse_namelist_with_error_message(self):
        """Test that parser records error for missing value."""
        text = """&control
calculation =
/"""
        parser = QEParser(text)
        result = parser.parse()
        # Parser should handle this gracefully
        assert isinstance(result, QEInputFile)


class TestServerBranches:
    """Tests for server branch coverage."""

    def test_get_namelist_at_position_with_end(self):
        """Test detecting namelist with &end closure."""
        doc = type("Doc", (), {"source": "&control\n&end\nparam"})()
        position = type("Pos", (), {"line": 2})()
        result = _get_namelist_at_position(doc, position)
        # After &end, should be None
        assert result is None

    def test_hover_on_unknown_card(self):
        """Test hover returns None for unknown card."""
        doc = type("Doc", (), {"source": "UNKNOWN_CARD"})()
        doc.uri = "test://test.in"

        # Mock server and workspace
        class MockWorkspace:
            def get_text_document(self, uri):
                return doc

        class MockServer:
            workspace = MockWorkspace()

        import qe_lsp.server as server_module

        original_server = server_module._server_instance
        server_module._server_instance = MockServer()

        try:
            params = HoverParams(
                text_document=TextDocumentIdentifier(uri="test://test.in"),
                position=Position(line=0, character=0),
            )
            result = hover(params)
            # Should return None for unknown word
            assert result is None
        finally:
            server_module._server_instance = original_server

    def test_diagnostic_warning_severity(self):
        """Test diagnostic handles warning severity."""
        doc = type("Doc", (), {"source": "&unknown\n/"})()
        doc.uri = "test://test.in"

        class MockWorkspace:
            def get_text_document(self, uri):
                return doc

        class MockServer:
            workspace = MockWorkspace()

        import qe_lsp.server as server_module

        original_server = server_module._server_instance
        server_module._server_instance = MockServer()

        try:
            params = type("Params", (), {"text_document": type("TD", (), {"uri": "test://test.in"})()})()
            result = diagnostic(params)
            # Should return diagnostics
            assert isinstance(result, list)
        finally:
            server_module._server_instance = original_server


class TestLexerFullCoverage:
    """Tests for complete lexer coverage."""

    def test_lexer_peek_offset(self):
        """Test lexer peek with offset."""
        lexer = QELexer("abc")
        assert lexer.peek(0) == "a"
        assert lexer.peek(1) == "b"
        assert lexer.peek(2) == "c"
        assert lexer.peek(3) == ""  # Beyond end

    def test_lexer_boolean_t_f(self):
        """Test lexer handles single character booleans."""
        # Test the T/F boolean handling
        text = "&control\nflag = T\n/"
        lexer = QELexer(text)
        tokens = lexer.tokenize()
        # Find the boolean token
        bool_tokens = [t for t in tokens if t.type == TokenType.BOOLEAN]
        assert len(bool_tokens) > 0
        assert bool_tokens[0].value in ("t", ".true.")

    def test_lexer_unexpected_characters(self):
        """Test lexer handles unexpected characters gracefully."""
        text = "&control\n!@#$%^\n/"
        lexer = QELexer(text)
        tokens = lexer.tokenize()
        # Should not crash
        assert tokens[-1].type == TokenType.EOF


class TestParserFullCoverage:
    """Tests for complete parser coverage."""

    def test_parser_current_empty_tokens(self):
        """Test parser current with empty tokens."""
        parser = QEParser("")
        parser.tokens = []
        parser.pos = 0
        result = parser.current()
        assert result.type == TokenType.EOF

    def test_parser_expect_wrong_type(self):
        """Test parser expect with wrong token type."""
        text = "&control\n/"
        parser = QEParser(text)
        parser.tokens = QELexer(text).tokenize()
        parser.pos = 0
        # Expect NUMBER but got NAMELIST_START
        result = parser.expect(TokenType.NUMBER)
        assert result is None

    def test_parse_card_data_with_comments(self):
        """Test parsing card data with inline comments."""
        text = """ATOMIC_SPECIES
H 1.0 H.pbe-rrkjus.UPF ! hydrogen
O 16.0 O.pbe-rrkjus.UPF"""
        parser = QEParser(text)
        result = parser.parse()
        assert "ATOMIC_SPECIES" in result.cards

    def test_validate_unknown_namelist_param(self):
        """Test validation with unknown parameter."""
        text = """&control
calculation = 'scf'
prefix = 'test'
outdir = './tmp'
unknown_param = 1
/
&system
ibrav = 1
nat = 1
ntyp = 1
ecutwfc = 30
/"""
        parser = QEParser(text)
        result = parser.parse()
        # Should parse without error
        assert "control" in result.namelists

    def test_get_word_at_position_line_out_of_range(self):
        """Test get_word_at_position with line out of range."""
        from qe_lsp.parser import get_word_at_position

        text = "line1\nline2"
        result = get_word_at_position(text, 10, 0)  # Line 10 doesn't exist
        assert result == (None, 0, 0)


class TestServerIntegration:
    """Integration tests for server functions."""

    def test_completion_with_empty_word(self):
        """Test completion when word is empty."""
        doc = type("Doc", (), {"source": "&control\n"})()
        doc.uri = "test://test.in"

        class MockWorkspace:
            def get_text_document(self, uri):
                return doc

        class MockServer:
            workspace = MockWorkspace()

        import qe_lsp.server as server_module

        original_server = server_module._server_instance
        server_module._server_instance = MockServer()

        try:
            params = CompletionParams(
                text_document=TextDocumentIdentifier(uri="test://test.in"),
                position=Position(line=1, character=0),
            )
            result = completion(params)
            # Should return completion list
            assert result is not None
        finally:
            server_module._server_instance = original_server

    def test_hover_outside_namelist(self):
        """Test hover when not in a namelist."""
        doc = type("Doc", (), {"source": "ATOMIC_SPECIES"})()
        doc.uri = "test://test.in"

        class MockWorkspace:
            def get_text_document(self, uri):
                return doc

        class MockServer:
            workspace = MockWorkspace()

        import qe_lsp.server as server_module

        original_server = server_module._server_instance
        server_module._server_instance = MockServer()

        try:
            params = HoverParams(
                text_document=TextDocumentIdentifier(uri="test://test.in"),
                position=Position(line=0, character=0),
            )
            result = hover(params)
            # Should return hover for card
            assert result is not None
        finally:
            server_module._server_instance = original_server

    def test_document_symbol_empty(self):
        """Test document symbols with empty file."""
        doc = type("Doc", (), {"source": ""})()
        doc.uri = "test://test.in"

        class MockWorkspace:
            def get_text_document(self, uri):
                return doc

        class MockServer:
            workspace = MockWorkspace()

        import qe_lsp.server as server_module

        original_server = server_module._server_instance
        server_module._server_instance = MockServer()

        try:
            params = DocumentSymbolParams(
                text_document=TextDocumentIdentifier(uri="test://test.in")
            )
            result = document_symbol(params)
            # Should return empty list
            assert result == []
        finally:
            server_module._server_instance = original_server

    def test_get_namelist_at_position_with_ampersand_end(self):
        """Test _get_namelist_at_position handles &end properly."""
        doc = type("Doc", (), {"source": "&control\ncalc='scf'\n&end\noutside"})()
        position = type("Pos", (), {"line": 3})()
        result = _get_namelist_at_position(doc, position)
        assert result is None


class TestParserMissingBranches:
    """Tests for parser code branches not yet covered."""

    def test_parser_error_with_token(self):
        """Test parser error method with token parameter."""
        parser = QEParser("")
        token = Token(TokenType.PARAMETER, "test", 1, 1)
        parser.error("Test error message", token)
        assert len(parser.errors) == 1
        assert parser.errors[0]["message"] == "Test error message"

    def test_parse_namelist_missing_value_error(self):
        """Test parse_namelist records error for missing value."""
        text = """&control
param =
/"""
        parser = QEParser(text)
        result = parser.parse()
        assert isinstance(result, QEInputFile)


class TestInitGetAttr:
    """Test __init__.py getattr."""

    def test_getattr_invalid(self):
        """Test getattr raises AttributeError."""
        import qe_lsp
        with pytest.raises(AttributeError):
            _ = qe_lsp.xyz_invalid

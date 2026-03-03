"""Tests for Quantum ESPRESSO LSP server."""

from unittest.mock import MagicMock, patch

from qe_lsp.server import (
    _get_word_at_position,
    _get_namelist_at_position,
    completion,
    hover,
    diagnostic,
    document_symbol,
    main,
    _get_server_for_testing,
)


class TestHelperFunctions:
    """Test helper functions."""

    def test_get_word_at_position(self):
        """Test getting word at position."""
        doc = MagicMock()
        doc.source = "ecutwfc = 60"
        word, rng = _get_word_at_position(doc, MagicMock(line=0, character=0))
        assert word == "ecutwfc"

    def test_get_word_at_position_middle(self):
        """Test getting word from middle of word."""
        doc = MagicMock()
        doc.source = "ecutwfc = 60"
        word, rng = _get_word_at_position(doc, MagicMock(line=0, character=3))
        assert word == "ecutwfc"

    def test_get_word_at_position_empty(self):
        """Test getting word from empty line."""
        doc = MagicMock()
        doc.source = "\\n"
        word, rng = _get_word_at_position(doc, MagicMock(line=0, character=0))
        assert word == ""

    def test_get_namelist_at_position(self):
        """Test getting namelist at position."""
        doc = MagicMock()
        doc.source = """&control
calculation = 'scf'
/"""
        namelist = _get_namelist_at_position(doc, MagicMock(line=1, character=0))
        assert namelist == "control"

    def test_get_namelist_at_position_outside(self):
        """Test getting namelist when outside."""
        doc = MagicMock()
        doc.source = """&control
/
calculation = 'scf'"""
        namelist = _get_namelist_at_position(doc, MagicMock(line=2, character=0))
        assert namelist is None


class TestQEServer:
    """Test QE LSP server."""

    def test_server_exists(self):
        """Test server instance exists."""
        srv = _get_server_for_testing()
        assert srv is not None
        assert srv.name == "qe-lsp"
        assert srv.version == "0.1.0"


class TestCompletion:
    """Test completion feature."""

    @patch('qe_lsp.server._get_server')
    def test_completion_in_namelist(self, mock_get_server):
        """Test completion inside namelist."""
        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(
            source="""&control
calc
/"""
        )
        mock_get_server.return_value = srv

        params = MagicMock()
        params.text_document.uri = "test://test.in"
        params.position = MagicMock(line=1, character=4)

        result = completion(params)
        assert result is not None

    @patch('qe_lsp.server._get_server')
    def test_completion_outside_namelist(self, mock_get_server):
        """Test completion outside namelist."""
        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(
            source="con"
        )
        mock_get_server.return_value = srv

        params = MagicMock()
        params.text_document.uri = "test://test.in"
        params.position = MagicMock(line=0, character=3)

        result = completion(params)
        assert result is not None


class TestHover:
    """Test hover feature."""

    @patch('qe_lsp.server._get_server')
    def test_hover_on_parameter(self, mock_get_server):
        """Test hover on parameter."""
        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(
            source="""&control
calculation = 'scf'
/"""
        )
        mock_get_server.return_value = srv

        params = MagicMock()
        params.text_document.uri = "test://test.in"
        params.position = MagicMock(line=1, character=0)

        result = hover(params)
        # Hover should work even without doc (returns None)
        assert result is None or hasattr(result, 'contents')

    @patch('qe_lsp.server._get_server')
    def test_hover_empty_word(self, mock_get_server):
        """Test hover with empty word."""
        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(
            source="\\n"
        )
        mock_get_server.return_value = srv

        params = MagicMock()
        params.text_document.uri = "test://test.in"
        params.position = MagicMock(line=0, character=0)

        result = hover(params)
        assert result is None


class TestDiagnostic:
    """Test diagnostic feature."""

    @patch('qe_lsp.server._get_server')
    def test_diagnostic_valid_input(self, mock_get_server):
        """Test diagnostic with valid input."""
        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(
            source="""&control
/
&system
ibrav = 1
nat = 1
ntyp = 1
ecutwfc = 30
/
&electrons
/"""
        )
        mock_get_server.return_value = srv

        params = MagicMock()
        params.text_document.uri = "test://test.in"

        result = diagnostic(params)
        assert isinstance(result, list)

    @patch('qe_lsp.server._get_server')
    def test_diagnostic_missing_namelist(self, mock_get_server):
        """Test diagnostic with missing namelist."""
        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(
            source="&control\\n/"
        )
        mock_get_server.return_value = srv

        params = MagicMock()
        params.text_document.uri = "test://test.in"

        result = diagnostic(params)
        # Should have errors (missing system namelist)
        assert len(result) > 0


class TestDocumentSymbol:
    """Test document symbol feature."""

    @patch('qe_lsp.server._get_server')
    def test_document_symbol(self, mock_get_server):
        """Test document symbol extraction."""
        srv = MagicMock()
        srv.workspace.get_text_document.return_value = MagicMock(
            source="""&control
calculation = 'scf'
/
&system
ibrav = 1
/
&electrons
/"""
        )
        mock_get_server.return_value = srv

        params = MagicMock()
        params.text_document.uri = "test://test.in"

        result = document_symbol(params)
        assert isinstance(result, list)
        # Should have symbols for namelists
        assert len(result) >= 3


class TestMain:
    """Test main entry point."""

    @patch('qe_lsp.server._get_server')
    def test_main(self, mock_get_server):
        """Test main function."""
        mock_server = MagicMock()
        mock_get_server.return_value = mock_server

        main()
        mock_get_server.assert_called_once()
        mock_server.start_io.assert_called_once()

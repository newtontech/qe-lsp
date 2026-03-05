"""Additional tests to reach 100% coverage."""

import pytest
from unittest.mock import MagicMock, patch


class TestInitFinalCoverage:
    """Tests for __init__.py final coverage."""

    def test_getattr_invalid_attribute(self):
        """Test that accessing invalid attribute raises AttributeError (lines 35-37)."""
        import qe_lsp

        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp.nonexistent_attribute

        assert "qe_lsp" in str(exc_info.value)
        assert "nonexistent_attribute" in str(exc_info.value)


class TestDataFinalCoverage:
    """Tests for data.py final coverage."""

    def test_format_param_hover_no_type_branch(self):
        """Test format_param_hover when type is not present (branch 373->376)."""
        from qe_lsp.data import format_param_hover

        param_doc = {
            "description": "Test description",
            "default": 100,
        }
        result = format_param_hover(param_doc)

        assert "Test description" in result
        assert "**Type:**" not in result
        assert "**Default:**" in result


class TestParserFinalCoverage:
    """Tests for parser.py final coverage."""

    def test_parse_card_with_data_then_eof(self):
        """Test parse_card_data ending with EOF."""
        from qe_lsp.parser import parse_qe_input

        text = """ATOMIC_SPECIES
  Si  28.0  Si.UPF"""
        result = parse_qe_input(text)

        assert "ATOMIC_SPECIES" in result.cards
        assert len(result.cards["ATOMIC_SPECIES"].data) == 1


class TestServerFinalCoverage:
    """Tests for server.py final coverage."""

    def test_main_function(self):
        """Test main function."""
        from qe_lsp.server import main

        with patch("qe_lsp.server._get_server") as mock_get_server:
            mock_server = MagicMock()
            mock_get_server.return_value = mock_server

            main()

            mock_server.start_io.assert_called_once()

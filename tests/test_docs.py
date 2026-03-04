"""Tests for docs module."""

import pytest

from qe_lsp.docs import (
    DocFormatter,
    get_formatted_card_doc,
    get_formatted_namelist_doc,
    get_formatted_parameter_doc,
)


class TestDocFormatter:
    """Test DocFormatter class."""

    def test_format_parameter_doc_valid(self):
        """Test formatting a valid parameter."""
        result = DocFormatter.format_parameter_doc("calculation", "control")
        assert result is not None
        assert "calculation" in result
        assert "control" in result

    def test_format_parameter_doc_invalid(self):
        """Test formatting an invalid parameter."""
        result = DocFormatter.format_parameter_doc("nonexistent", "control")
        assert result is None

    def test_format_parameter_doc_invalid_namelist(self):
        """Test formatting with invalid namelist."""
        result = DocFormatter.format_parameter_doc("calculation", "nonexistent")
        assert result is None

    def test_format_card_doc_valid(self):
        """Test formatting a valid card."""
        result = DocFormatter.format_card_doc("ATOMIC_SPECIES")
        assert result is not None
        assert "ATOMIC_SPECIES" in result

    def test_format_card_doc_invalid(self):
        """Test formatting an invalid card."""
        result = DocFormatter.format_card_doc("NONEXISTENT")
        assert result is None

    def test_format_namelist_doc(self):
        """Test formatting namelist documentation."""
        result = DocFormatter.format_namelist_doc("control")
        assert "control" in result
        assert "namelist" in result


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_formatted_parameter_doc(self):
        """Test get_formatted_parameter_doc function."""
        result = get_formatted_parameter_doc("calculation", "control")
        assert result is not None
        assert "calculation" in result

    def test_get_formatted_card_doc(self):
        """Test get_formatted_card_doc function."""
        result = get_formatted_card_doc("ATOMIC_SPECIES")
        assert result is not None
        assert "ATOMIC_SPECIES" in result

    def test_get_formatted_namelist_doc(self):
        """Test get_formatted_namelist_doc function."""
        result = get_formatted_namelist_doc("system")
        assert "system" in result
        assert "namelist" in result

"""Additional tests to achieve 100% coverage."""

import pytest


class TestInitCoverage:
    """Tests for __init__.py coverage."""

    def test_getattr_invalid_attribute_error_message(self):
        """Test that AttributeError includes the attribute name."""
        import qe_lsp

        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp.invalid_attr_xyz
        assert "invalid_attr_xyz" in str(exc_info.value)

    def test_getattr_another_invalid_attr(self):
        """Test another invalid attribute to cover line 35-37."""
        import qe_lsp

        with pytest.raises(AttributeError) as exc_info:
            _ = qe_lsp._private_attr_abc
        assert "_private_attr_abc" in str(exc_info.value)

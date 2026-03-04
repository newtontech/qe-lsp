"""Basic tests for qe-lsp."""

import pytest


def test_package_imports():
    """Test that the package can be imported."""
    import qe_lsp

    assert qe_lsp.__version__ == "0.1.0"


def test_version():
    """Test version."""
    from qe_lsp import __version__

    assert __version__ == "0.1.0"


def test_all_exports():
    """Test that all expected exports are available."""
    import qe_lsp

    assert "parse" in qe_lsp.__all__
    assert "QEParser" in qe_lsp.__all__
    assert "QEInputFile" in qe_lsp.__all__
    assert "QEInput" in qe_lsp.__all__
    assert "Namelist" in qe_lsp.__all__
    assert "Card" in qe_lsp.__all__
    assert "get_parameter_doc" in qe_lsp.__all__
    assert "get_card_doc" in qe_lsp.__all__
    assert "server" in qe_lsp.__all__
    assert "main" in qe_lsp.__all__


def test_parser_exports():
    """Test that parser can be imported."""
    from qe_lsp import QEParser, parse

    assert QEParser is not None
    assert parse is not None


def test_docs_exports():
    """Test that documentation can be imported."""
    from qe_lsp import get_parameter_doc, get_card_doc

    assert get_parameter_doc is not None
    assert get_card_doc is not None


def test_parse_function():
    """Test that parse function works."""
    from qe_lsp import parse

    result = parse("&control\n/")
    assert result is not None
    assert "control" in result.namelists


def test_import_server():
    """Test that server can be imported."""
    from qe_lsp import server, main

    assert server is not None
    assert main is not None


def test_getattr_invalid():
    """Test that accessing invalid attribute raises AttributeError."""
    import qe_lsp

    with pytest.raises(AttributeError):
        _ = qe_lsp.nonexistent_attribute


def test_main_lazy_import():
    """Test lazy import of main function."""
    import qe_lsp

    main_fn = qe_lsp.main
    assert main_fn is not None
    assert callable(main_fn)

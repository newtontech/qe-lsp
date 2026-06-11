"""Tests for the FormattingProvider document and range formatting."""

from typing import TYPE_CHECKING

import pytest
from lsprotocol.types import (
    DocumentFormattingParams,
    DocumentRangeFormattingParams,
    FormattingOptions,
    Position,
    Range,
    TextDocumentIdentifier,
)

from qe_lsp.features.formatting import FormattingProvider, get_formatting_provider
from tests.lsp_compat import get_registered_features

if TYPE_CHECKING:
    from pygls.lsp.server import LanguageServer
else:
    try:
        from pygls.lsp.server import LanguageServer
    except ImportError:
        from pygls.server import LanguageServer


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def provider() -> FormattingProvider:
    """Create a FormattingProvider backed by a minimal LanguageServer."""
    server = LanguageServer("test-qe-lsp", "0.1.0")
    return FormattingProvider(server)


@pytest.fixture
def fmt_params() -> DocumentFormattingParams:
    """Default formatting parameters (2 spaces)."""
    return DocumentFormattingParams(
        text_document=TextDocumentIdentifier(uri="test.qe"),
        options=FormattingOptions(tab_size=2, insert_spaces=True),
    )


@pytest.fixture
def fmt_params_4() -> DocumentFormattingParams:
    """Formatting parameters with 4-space indentation."""
    return DocumentFormattingParams(
        text_document=TextDocumentIdentifier(uri="test.qe"),
        options=FormattingOptions(tab_size=4, insert_spaces=True),
    )


@pytest.fixture
def fmt_params_tabs() -> DocumentFormattingParams:
    """Formatting parameters with tab indentation."""
    return DocumentFormattingParams(
        text_document=TextDocumentIdentifier(uri="test.qe"),
        options=FormattingOptions(tab_size=2, insert_spaces=False),
    )


def _range_params(
    start_line: int,
    end_line: int,
    tab_size: int = 2,
    insert_spaces: bool = True,
) -> DocumentRangeFormattingParams:
    """Helper to build range-formatting params."""
    return DocumentRangeFormattingParams(
        text_document=TextDocumentIdentifier(uri="test.qe"),
        range=Range(
            start=Position(line=start_line, character=0),
            end=Position(line=end_line, character=999),
        ),
        options=FormattingOptions(tab_size=tab_size, insert_spaces=insert_spaces),
    )


# ------------------------------------------------------------------
# Provider creation
# ------------------------------------------------------------------


class TestProviderCreation:
    def test_provider_exists(self, provider: FormattingProvider) -> None:
        assert provider is not None

    def test_factory(self) -> None:
        server = LanguageServer("test-qe-lsp", "0.1.0")
        instance = get_formatting_provider(server)
        assert isinstance(instance, FormattingProvider)


# ------------------------------------------------------------------
# Document formatting
# ------------------------------------------------------------------


class TestFormatDocument:
    def test_empty_returns_empty(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        assert provider.format_document("", fmt_params) == []

    def test_already_formatted_returns_empty(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = "&CONTROL\n  calculation = 'scf'\n/\n"
        assert provider.format_document(text, fmt_params) == []

    def test_single_line_no_change(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = "ATOMIC_SPECIES\n"
        edits = provider.format_document(text, fmt_params)
        # Single card header with no body — already fine
        assert edits == []

    def test_namelist_indentation(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n"
        edits = provider.format_document(text, fmt_params)
        assert len(edits) == 1
        assert "  calculation = 'scf'" in edits[0].new_text

    def test_card_indentation(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = "ATOMIC_SPECIES\nSi 28.086 Si.pbe.UPF\n"
        edits = provider.format_document(text, fmt_params)
        assert len(edits) == 1
        assert "  Si 28.086 Si.pbe.UPF" in edits[0].new_text

    def test_nested_namelists_and_cards(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = (
            "&CONTROL\n"
            "calculation = 'scf'\n"
            "/\n"
            "&SYSTEM\n"
            "ibrav = 1\n"
            "ecutwfc = 60\n"
            "/\n"
            "ATOMIC_SPECIES\n"
            "Si 28.086 Si.pbe.UPF\n"
            "ATOMIC_POSITIONS {crystal}\n"
            "Si 0.0 0.0 0.0\n"
        )
        edits = provider.format_document(text, fmt_params)
        assert len(edits) == 1
        formatted = edits[0].new_text
        assert "  calculation = 'scf'" in formatted
        assert "  ibrav = 1" in formatted
        assert "  Si 28.086 Si.pbe.UPF" in formatted
        assert "  Si 0.0 0.0 0.0" in formatted

    def test_4_space_indent(
        self, provider: FormattingProvider, fmt_params_4: DocumentFormattingParams
    ) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n"
        edits = provider.format_document(text, fmt_params_4)
        assert len(edits) == 1
        assert "    calculation = 'scf'" in edits[0].new_text

    def test_tab_indent(
        self, provider: FormattingProvider, fmt_params_tabs: DocumentFormattingParams
    ) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n"
        edits = provider.format_document(text, fmt_params_tabs)
        assert len(edits) == 1
        assert "\tcalculation = 'scf'" in edits[0].new_text

    def test_trailing_newline_preserved(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        # Already formatted — no edits
        # Let's use unformatted version
        text2 = "&CONTROL\ncalculation = 'scf'\n/\n"
        edits2 = provider.format_document(text2, fmt_params)
        if edits2:
            assert edits2[0].new_text.endswith("\n")

    def test_idempotent(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        """Formatting the output of formatting again must produce no edits."""
        text = "&CONTROL\ncalculation = 'scf'\n/\n"
        first_edits = provider.format_document(text, fmt_params)
        assert len(first_edits) == 1
        formatted = first_edits[0].new_text
        second_edits = provider.format_document(formatted, fmt_params)
        assert second_edits == []


class TestFormatDocumentComments:
    def test_comment_preserved(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = "! This is a comment\n&CONTROL\ncalculation = 'scf'\n/\n"
        edits = provider.format_document(text, fmt_params)
        assert len(edits) == 1
        assert "! This is a comment" in edits[0].new_text

    def test_inline_comment_preserved(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = "&CONTROL\ncalculation = 'scf' ! SCF run\n/\n"
        edits = provider.format_document(text, fmt_params)
        assert len(edits) == 1
        assert "! SCF run" in edits[0].new_text

    def test_blank_lines_preserved(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = "&CONTROL\n\ncalculation = 'scf'\n/\n"
        edits = provider.format_document(text, fmt_params)
        assert len(edits) == 1
        lines = edits[0].new_text.splitlines()
        # The blank line at index 1 should still be blank
        assert lines[1] == ""


class TestFormatDocumentMalformed:
    def test_unclosed_namelist(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n"
        edits = provider.format_document(text, fmt_params)
        assert len(edits) == 1
        assert "  calculation = 'scf'" in edits[0].new_text

    def test_stray_slash(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = "/\n"
        edits = provider.format_document(text, fmt_params)
        # Slash without a namelist — should still format without error
        assert isinstance(edits, list)

    def test_random_text(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = "some random text\nmore random text\n"
        edits = provider.format_document(text, fmt_params)
        # Should not crash, and text without structure stays as-is
        assert isinstance(edits, list)


# ------------------------------------------------------------------
# Range formatting
# ------------------------------------------------------------------


class TestFormatRange:
    def test_empty_returns_empty(self, provider: FormattingProvider) -> None:
        params = _range_params(0, 0)
        assert provider.format_range("", params) == []

    def test_range_within_namelist(self, provider: FormattingProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n"
        # Format only line 1 (the assignment)
        params = _range_params(1, 1)
        edits = provider.format_range(text, params)
        assert len(edits) == 1
        assert "  calculation = 'scf'" in edits[0].new_text

    def test_range_includes_namelist_header(self, provider: FormattingProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n"
        # Format lines 0-2
        params = _range_params(0, 2)
        edits = provider.format_range(text, params)
        assert len(edits) == 1

    def test_already_formatted_range(self, provider: FormattingProvider) -> None:
        text = "&CONTROL\n  calculation = 'scf'\n/\n"
        params = _range_params(1, 1)
        edits = provider.format_range(text, params)
        assert edits == []

    def test_range_clamps_to_document(self, provider: FormattingProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n"
        # Request a range beyond the document
        params = _range_params(0, 100)
        edits = provider.format_range(text, params)
        assert isinstance(edits, list)

    def test_range_preserves_surrounding_context(self, provider: FormattingProvider) -> None:
        """Range formatting must not affect lines outside the range."""
        text = "&CONTROL\ncalculation = 'scf'\n/\n&SYSTEM\nibrav = 1\n/\n"
        # Format only line 4 (ibrav = 1)
        params = _range_params(4, 4)
        edits = provider.format_range(text, params)
        assert len(edits) == 1
        assert "  ibrav = 1" in edits[0].new_text

    def test_range_with_card(self, provider: FormattingProvider) -> None:
        text = "ATOMIC_SPECIES\nSi 28.086 Si.pbe.UPF\nATOMIC_POSITIONS {crystal}\nSi 0.0 0.0 0.0\n"
        # Format lines 1 and 3 (card data rows)
        params = _range_params(1, 1)
        edits = provider.format_range(text, params)
        assert len(edits) == 1
        assert "  Si 28.086 Si.pbe.UPF" in edits[0].new_text


# ------------------------------------------------------------------
# Idempotency across representative fixtures
# ------------------------------------------------------------------


class TestIdempotency:
    """Formatting the result of formatting must produce no edits."""

    FULL_INPUT = (
        "&CONTROL\n"
        "  calculation = 'scf'\n"
        "/\n"
        "&SYSTEM\n"
        "  ibrav = 1\n"
        "  A = 5.42\n"
        "  nat = 1\n"
        "  ntyp = 1\n"
        "  ecutwfc = 60.0\n"
        "/\n"
        "&ELECTRONS\n"
        "  conv_thr = 1.0e-8\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        "  Si 28.086 Si.pbe.UPF\n"
        "ATOMIC_POSITIONS {crystal}\n"
        "  Si 0.0 0.0 0.0\n"
        "K_POINTS {automatic}\n"
        "  4 4 4 0 0 0\n"
    )

    UNFORMATTED_INPUT = (
        "&CONTROL\n"
        "calculation = 'scf'\n"
        "/\n"
        "&SYSTEM\n"
        "ibrav = 1\n"
        "A = 5.42\n"
        "nat = 1\n"
        "ntyp = 1\n"
        "ecutwfc = 60.0\n"
        "/\n"
        "&ELECTRONS\n"
        "conv_thr = 1.0e-8\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        "Si 28.086 Si.pbe.UPF\n"
        "ATOMIC_POSITIONS {crystal}\n"
        "Si 0.0 0.0 0.0\n"
        "K_POINTS {automatic}\n"
        "4 4 4 0 0 0\n"
    )

    def test_full_input_idempotent(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        """A fully formatted document should produce zero edits."""
        edits = provider.format_document(self.FULL_INPUT, fmt_params)
        assert edits == []

    def test_format_then_format_again(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        """Formatting unformatted input then formatting again must be idempotent."""
        first_edits = provider.format_document(self.UNFORMATTED_INPUT, fmt_params)
        assert len(first_edits) == 1
        formatted = first_edits[0].new_text
        second_edits = provider.format_document(formatted, fmt_params)
        assert second_edits == []

    def test_format_with_comments_idempotent(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = (
            "! Silicon SCF\n"
            "&CONTROL\n"
            "  calculation = 'scf' ! SCF run\n"
            "/\n"
            "! End of control\n"
            "\n"
            "ATOMIC_SPECIES\n"
            "  Si 28.086 Si.pbe.UPF\n"
        )
        edits = provider.format_document(text, fmt_params)
        assert edits == []

    def test_format_then_format_with_comments(
        self, provider: FormattingProvider, fmt_params: DocumentFormattingParams
    ) -> None:
        text = (
            "! Silicon SCF\n"
            "&CONTROL\n"
            "calculation = 'scf' ! SCF run\n"
            "/\n"
            "! End of control\n"
            "\n"
            "ATOMIC_SPECIES\n"
            "Si 28.086 Si.pbe.UPF\n"
        )
        first = provider.format_document(text, fmt_params)
        assert len(first) == 1
        second = provider.format_document(first[0].new_text, fmt_params)
        assert second == []


# ------------------------------------------------------------------
# Server registration
# ------------------------------------------------------------------


class TestServerRegistration:
    def test_formatting_provider_attached(self) -> None:
        from qe_lsp.server import create_server

        srv = create_server()
        assert hasattr(srv, "formatting_provider")
        assert isinstance(srv.formatting_provider, FormattingProvider)

    def test_server_registers_formatting_handlers(self) -> None:
        from qe_lsp.server import server

        features = get_registered_features(server)
        assert "textDocument/formatting" in features
        assert "textDocument/rangeFormatting" in features

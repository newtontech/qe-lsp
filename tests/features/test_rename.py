"""Tests for the RenameProvider (textDocument/prepareRename + textDocument/rename)."""

import pytest

from lsprotocol.types import Position, Range, TextEdit

from qe_lsp.features.rename import RenameProvider


@pytest.fixture
def provider() -> RenameProvider:
    return RenameProvider()


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _make_text(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------
# prepareRename — namelist parameters
# ------------------------------------------------------------------


class TestPrepareRenameParameters:
    """prepareRename returns the range of a renamable namelist parameter."""

    def test_prepare_rename_parameter_in_control(self, provider: RenameProvider) -> None:
        text = _make_text([
            "&CONTROL",
            "  calculation = 'scf'",
            "/",
        ])
        result = provider.prepare_rename(text, line=1, character=4)
        assert result is not None
        assert result.start.line == 1
        assert result.end.line == 1
        # The name "calculation" starts at column 2 (after indent)
        assert result.start.character == 2
        assert result.end.character == 2 + len("calculation")

    def test_prepare_rename_ecutwfc(self, provider: RenameProvider) -> None:
        text = _make_text([
            "&SYSTEM",
            "  ecutwfc = 60.0",
            "/",
        ])
        result = provider.prepare_rename(text, line=1, character=6)
        assert result is not None
        assert result.start.character == 2
        assert result.end.character == 2 + len("ecutwfc")

    def test_prepare_rename_array_parameter(self, provider: RenameProvider) -> None:
        text = _make_text([
            "&SYSTEM",
            "  celldm(1) = 10.0",
            "/",
        ])
        result = provider.prepare_rename(text, line=1, character=5)
        assert result is not None
        # Should cover the full "celldm(1)" token
        assert result.start.character == 2
        assert result.end.character == 2 + len("celldm(1)")


# ------------------------------------------------------------------
# prepareRename — element symbols
# ------------------------------------------------------------------


class TestPrepareRenameElementSymbols:
    """prepareRename returns the range of element symbols in card rows."""

    def test_prepare_rename_species_symbol(self, provider: RenameProvider) -> None:
        text = _make_text([
            "ATOMIC_SPECIES",
            "Si 28.086 Si.pbe.UPF",
        ])
        result = provider.prepare_rename(text, line=1, character=1)
        assert result is not None
        assert result.start.line == 1
        assert result.start.character == 0
        assert result.end.character == 2

    def test_prepare_rename_position_symbol(self, provider: RenameProvider) -> None:
        text = _make_text([
            "ATOMIC_POSITIONS {crystal}",
            "Si 0.0 0.0 0.0",
        ])
        result = provider.prepare_rename(text, line=1, character=0)
        assert result is not None
        assert result.start.character == 0
        assert result.end.character == 2


# ------------------------------------------------------------------
# prepareRename — rejection cases
# ------------------------------------------------------------------


class TestPrepareRenameRejection:
    """prepareRename returns None for targets that cannot be renamed."""

    @pytest.mark.parametrize(
        "text,line,character",
        [
            ("&CONTROL\ncalculation = 'scf'\n/\n", 0, 1),  # namelist header
            ("&SYSTEM\necutwfc = 60\n/\n", 0, 1),  # namelist header
        ],
    )
    def test_reject_namelist_header(
        self,
        provider: RenameProvider,
        text: str,
        line: int,
        character: int,
    ) -> None:
        assert provider.prepare_rename(text, line, character) is None

    def test_reject_card_header(self, provider: RenameProvider) -> None:
        text = _make_text([
            "ATOMIC_SPECIES",
            "Si 28.086 Si.pbe.UPF",
        ])
        assert provider.prepare_rename(text, line=0, character=3) is None

    def test_reject_empty_word(self, provider: RenameProvider) -> None:
        text = _make_text(["", "  ", ""])
        assert provider.prepare_rename(text, line=1, character=1) is None

    def test_reject_out_of_bounds_line(self, provider: RenameProvider) -> None:
        text = "calculation = 'scf'\n"
        assert provider.prepare_rename(text, line=99, character=0) is None

    def test_reject_card_value_not_symbol(self, provider: RenameProvider) -> None:
        """Clicking on the mass value in ATOMIC_SPECIES should not match."""
        text = _make_text([
            "ATOMIC_SPECIES",
            "Si 28.086 Si.pbe.UPF",
        ])
        # character 4 is in the middle of "28.086"
        result = provider.prepare_rename(text, line=1, character=5)
        assert result is None


# ------------------------------------------------------------------
# rename — namelist parameters (same file)
# ------------------------------------------------------------------


class TestRenameNamelistParameters:
    """rename produces workspace edits for all occurrences of a parameter."""

    def test_rename_single_occurrence(self, provider: RenameProvider) -> None:
        text = _make_text([
            "&SYSTEM",
            "  ecutwfc = 60.0",
            "/",
        ])
        result = provider.rename(text, "file:///test.in", line=1, character=4, new_name="cutoff")
        assert result is not None
        changes = result.changes
        assert "file:///test.in" in changes
        edits = changes["file:///test.in"]
        assert len(edits) == 1
        assert edits[0].new_text == "cutoff"
        assert edits[0].range.start.line == 1

    def test_rename_duplicate_parameter(self, provider: RenameProvider) -> None:
        """Both the primary and duplicate assignment should be renamed."""
        text = _make_text([
            "&SYSTEM",
            "  ecutwfc = 60.0",
            "  ecutwfc = 80.0",
            "/",
        ])
        result = provider.rename(text, "file:///test.in", line=2, character=4, new_name="cutoff")
        assert result is not None
        edits = result.changes["file:///test.in"]
        assert len(edits) == 2
        names = {e.new_text for e in edits}
        assert names == {"cutoff"}

    def test_rename_parameter_in_correct_namelist_only(
        self,
        provider: RenameProvider,
    ) -> None:
        """A parameter name appearing in different namelists should only
        rename within the triggered namelist."""
        text = _make_text([
            "&CONTROL",
            "  title = 'test'",
            "/",
            "&SYSTEM",
            "  nat = 1",
            "/",
        ])
        # Triggering on "title" in &CONTROL
        result = provider.rename(text, "file:///test.in", line=1, character=4, new_name="job_title")
        assert result is not None
        edits = result.changes["file:///test.in"]
        assert len(edits) == 1
        assert edits[0].range.start.line == 1

    def test_rename_returns_none_for_invalid_new_name(
        self,
        provider: RenameProvider,
    ) -> None:
        text = _make_text([
            "&SYSTEM",
            "  ecutwfc = 60.0",
            "/",
        ])
        assert provider.rename(text, "file:///test.in", line=1, character=4, new_name="") is None
        assert provider.rename(text, "file:///test.in", line=1, character=4, new_name="123bad") is None

    def test_rename_returns_none_for_unsupported_target(
        self,
        provider: RenameProvider,
    ) -> None:
        text = _make_text([
            "&CONTROL",
            "  calculation = 'scf'",
            "/",
        ])
        # Clicking on the namelist header should not produce edits
        assert provider.rename(text, "file:///test.in", line=0, character=1, new_name="NEW") is None


# ------------------------------------------------------------------
# rename — element symbols
# ------------------------------------------------------------------


class TestRenameElementSymbols:
    """rename produces workspace edits for element symbols across cards."""

    def test_rename_species_and_positions(self, provider: RenameProvider) -> None:
        text = _make_text([
            "ATOMIC_SPECIES",
            "Si 28.086 Si.pbe.UPF",
            "ATOMIC_POSITIONS {crystal}",
            "Si 0.0 0.0 0.0",
            "O 0.5 0.5 0.5",
        ])
        result = provider.rename(text, "file:///test.in", line=1, character=0, new_name="Ge")
        assert result is not None
        edits = result.changes["file:///test.in"]
        # Si appears in ATOMIC_SPECIES line 1 and ATOMIC_POSITIONS line 3
        si_lines = [e.range.start.line for e in edits if e.new_text == "Ge"]
        assert 1 in si_lines
        assert 3 in si_lines
        # O should not be renamed
        assert not any(e.range.start.line == 4 for e in edits)

    def test_rename_position_symbol(self, provider: RenameProvider) -> None:
        text = _make_text([
            "ATOMIC_SPECIES",
            "O 15.999 O.pbe.UPF",
            "ATOMIC_POSITIONS {crystal}",
            "O 0.0 0.0 0.0",
            "O 0.5 0.5 0.5",
        ])
        result = provider.rename(text, "file:///test.in", line=3, character=0, new_name="S")
        assert result is not None
        edits = result.changes["file:///test.in"]
        o_lines = sorted(e.range.start.line for e in edits)
        assert o_lines == [1, 3, 4]

    def test_rename_symbol_no_match_outside_cards(self, provider: RenameProvider) -> None:
        """Only symbols in ATOMIC_SPECIES and ATOMIC_POSITIONS are renamed."""
        text = _make_text([
            "ATOMIC_SPECIES",
            "Si 28.086 Si.pbe.UPF",
        ])
        result = provider.rename(text, "file:///test.in", line=0, character=3, new_name="Ge")
        # "ATOMIC_SPECIES" header is not an element symbol
        assert result is None


# ------------------------------------------------------------------
# rename — rejection and edge cases
# ------------------------------------------------------------------


class TestRenameRejection:
    """rename refuses keywords, sections, unresolved symbols, and invalid names."""

    def test_reject_namelist_header(self, provider: RenameProvider) -> None:
        text = _make_text(["&CONTROL", "  calculation = 'scf'", "/"])
        assert provider.rename(text, "file:///test.in", line=0, character=1, new_name="X") is None

    def test_reject_card_header(self, provider: RenameProvider) -> None:
        text = _make_text(["ATOMIC_SPECIES", "Si 28.086 Si.pbe.UPF"])
        assert provider.rename(text, "file:///test.in", line=0, character=3, new_name="X") is None

    def test_reject_out_of_bounds(self, provider: RenameProvider) -> None:
        text = "ecutwfc = 60\n"
        assert provider.rename(text, "file:///test.in", line=99, character=0, new_name="X") is None

    def test_reject_empty_new_name(self, provider: RenameProvider) -> None:
        text = _make_text(["&SYSTEM", "  ecutwfc = 60.0", "/"])
        assert provider.rename(text, "file:///test.in", line=1, character=4, new_name="") is None

    def test_reject_numeric_new_name(self, provider: RenameProvider) -> None:
        text = _make_text(["&SYSTEM", "  ecutwfc = 60.0", "/"])
        assert provider.rename(text, "file:///test.in", line=1, character=4, new_name="123") is None

    def test_reject_special_chars_in_new_name(self, provider: RenameProvider) -> None:
        text = _make_text(["&SYSTEM", "  ecutwfc = 60.0", "/"])
        assert provider.rename(text, "file:///test.in", line=1, character=4, new_name="bad-name") is None


# ------------------------------------------------------------------
# Handler-level integration
# ------------------------------------------------------------------


class TestRenameHandler:
    """Test the handler module functions directly."""

    def test_handler_rename_via_params(self) -> None:
        from qe_lsp.handlers.rename import rename as rename_handler

        text = _make_text([
            "&SYSTEM",
            "  ecutwfc = 60.0",
            "/",
        ])

        class Params:
            def __init__(self, text: str, line: int, character: int, new_name: str) -> None:
                self.text = text
                self.position = {"line": line, "character": character, "new_name": new_name}
                self.text_document = type("TD", (), {"uri": "file:///test.in"})()

        result = rename_handler(Params(text, line=1, character=4, new_name="cutoff"))
        assert result is not None
        edits = result.changes["file:///test.in"]
        assert len(edits) == 1
        assert edits[0].new_text == "cutoff"

    def test_handler_prepare_rename_via_params(self) -> None:
        from qe_lsp.handlers.rename import prepare_rename as prepare_rename_handler

        text = _make_text([
            "&SYSTEM",
            "  ecutwfc = 60.0",
            "/",
        ])

        class Params:
            def __init__(self, text: str, line: int, character: int) -> None:
                self.text = text
                self.position = {"line": line, "character": character}
                self.text_document = type("TD", (), {"uri": "file:///test.in"})()

        result = prepare_rename_handler(Params(text, line=1, character=4))
        assert result is not None
        assert result.start.line == 1

    def test_handler_returns_none_for_empty_text(self) -> None:
        from qe_lsp.handlers.rename import rename as rename_handler

        class Params:
            text = None
            position = {"line": 0, "character": 0, "new_name": "X"}
            text_document = type("TD", (), {"uri": "file:///test.in"})()

        assert rename_handler(Params()) is None

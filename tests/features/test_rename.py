"""Tests for rename features: prepareRename, rename for QE variables and symbols."""

from lsprotocol import types

from qe_lsp.features.rename import RenameProvider, _namelist_for_line, _word_at
from qe_lsp.handlers.rename import prepare_rename, rename

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_INPUT = """\
&CONTROL
  calculation = 'scf'
  title = 'test'
/
&SYSTEM
  ibrav = 1
  celldm(1) = 7.5
  nat = 2
  ntyp = 1
  ecutwfc = 60
  ecutrho = 480
/
&ELECTRONS
  conv_thr = 1d-8
  mixing_beta = 0.7
/
ATOMIC_SPECIES
Si 28.086 Si.pbe.UPF
ATOMIC_POSITIONS {crystal}
Si 0.0 0.0 0.0
Si 0.25 0.25 0.25
K_POINTS {automatic}
4 4 4 0 0 0
"""
# Line index:
#  0: &CONTROL
#  1:   calculation = 'scf'
#  2:   title = 'test'
#  3: /
#  4: &SYSTEM
#  5:   ibrav = 1
#  6:   celldm(1) = 7.5
#  7:   nat = 2
#  8:   ntyp = 1
#  9:   ecutwfc = 60
# 10:   ecutrho = 480
# 11: /
# 12: &ELECTRONS
# 13:   conv_thr = 1d-8
# 14:   mixing_beta = 0.7
# 15: /
# 16: ATOMIC_SPECIES
# 17: Si 28.086 Si.pbe.UPF
# 18: ATOMIC_POSITIONS {crystal}
# 19: Si 0.0 0.0 0.0
# 20: Si 0.25 0.25 0.25
# 21: K_POINTS {automatic}
# 22: 4 4 4 0 0 0

DUPLICATE_PARAM_INPUT = """\
&CONTROL
  calculation = 'scf'
  calculation = 'nscf'
/
"""
# Line index:
#  0: &CONTROL
#  1:   calculation = 'scf'
#  2:   calculation = 'nscf'
#  3: /

MULTI_ELEMENT_INPUT = """\
&CONTROL
  calculation = 'scf'
/
&SYSTEM
  ibrav = 1
  nat = 4
  ntyp = 2
  ecutwfc = 60
/
ATOMIC_SPECIES
Si 28.086 Si.pbe.UPF
O 15.999 O.pbe.UPF
ATOMIC_POSITIONS {crystal}
Si 0.0 0.0 0.0
Si 0.25 0.25 0.25
O 0.5 0.5 0.5
O 0.75 0.75 0.75
"""
# Line index:
#  0: &CONTROL
#  1:   calculation = 'scf'
#  2: /
#  3: &SYSTEM
#  4:   ibrav = 1
#  5:   nat = 4
#  6:   ntyp = 2
#  7:   ecutwfc = 60
#  8: /
#  9: ATOMIC_SPECIES
# 10: Si 28.086 Si.pbe.UPF
# 11: O 15.999 O.pbe.UPF
# 12: ATOMIC_POSITIONS {crystal}
# 13: Si 0.0 0.0 0.0
# 14: Si 0.25 0.25 0.25
# 15: O 0.5 0.5 0.5
# 16: O 0.75 0.75 0.75

URI = "file:///test.in"


class Params:
    """Minimal LSP-params stand-in for handler tests."""

    def __init__(
        self,
        text: str,
        line: int = 0,
        character: int = 0,
        uri: str = URI,
        new_name: str = "",
    ):
        self.text = text
        self.position = {"line": line, "character": character, "new_name": new_name}
        self.text_document = type("TD", (), {"uri": uri})()
        self.new_name = new_name


_provider = RenameProvider()


def _edits(result: types.WorkspaceEdit, uri: str = URI) -> list[types.TextEdit]:
    assert result.changes is not None
    return list(result.changes[uri])


def _changes(result: types.WorkspaceEdit):
    assert result.changes is not None
    return result.changes


# ===========================================================================
# _word_at helper
# ===========================================================================


class TestWordAt:
    def test_simple_word(self) -> None:
        text = "  ecutwfc = 60\n"
        assert _word_at(text, 0, 2) == "ecutwfc"

    def test_word_with_array_index(self) -> None:
        text = "  celldm(1) = 7.5\n"
        assert _word_at(text, 0, 2) == "celldm(1)"

    def test_empty_line(self) -> None:
        assert _word_at("\n\n", 0, 0) == ""

    def test_out_of_range_line(self) -> None:
        assert _word_at("hello", 5, 0) == ""

    def test_out_of_range_char(self) -> None:
        assert _word_at("hi", 0, 100) == ""


# ===========================================================================
# _namelist_for_line helper
# ===========================================================================


class TestNamelistForLine:
    def test_line_in_control(self) -> None:
        assert _namelist_for_line(SAMPLE_INPUT, 1) == "&CONTROL"

    def test_line_in_system(self) -> None:
        assert _namelist_for_line(SAMPLE_INPUT, 5) == "&SYSTEM"

    def test_line_in_electrons(self) -> None:
        assert _namelist_for_line(SAMPLE_INPUT, 13) == "&ELECTRONS"

    def test_line_outside_namelist(self) -> None:
        assert _namelist_for_line(SAMPLE_INPUT, 16) is None

    def test_line_after_close(self) -> None:
        assert _namelist_for_line(SAMPLE_INPUT, 3) is None


# ===========================================================================
# prepareRename
# ===========================================================================


class TestPrepareRename:
    """prepareRename should return a Range for renamable symbols and None
    for structural keywords and unsupported positions."""

    # -- Renamable targets ---------------------------------------------------

    def test_prepare_rename_parameter(self) -> None:
        """Namelist parameter (ecutwfc at line 9, char 2) is renamable."""
        result = _provider.prepare_rename(SAMPLE_INPUT, 9, 2)
        assert result is not None
        assert isinstance(result, types.Range)
        assert result.start.line == 9
        assert result.start.character == 2
        assert result.end.character > 2

    def test_prepare_rename_calculation(self) -> None:
        """calculation at line 1 is a renamable parameter."""
        result = _provider.prepare_rename(SAMPLE_INPUT, 1, 2)
        assert result is not None
        assert result.start.line == 1

    def test_prepare_rename_celldm(self) -> None:
        """celldm(1) at line 6 is renamable."""
        result = _provider.prepare_rename(SAMPLE_INPUT, 6, 2)
        assert result is not None
        assert result.start.line == 6

    def test_prepare_rename_element_symbol_species(self) -> None:
        """Si in ATOMIC_SPECIES at line 17 is renamable."""
        result = _provider.prepare_rename(SAMPLE_INPUT, 17, 0)
        assert result is not None
        assert result.start.line == 17
        assert result.start.character == 0
        assert result.end.character == 2  # len("Si")

    def test_prepare_rename_element_symbol_positions(self) -> None:
        """Si in ATOMIC_POSITIONS at line 19 is renamable."""
        result = _provider.prepare_rename(SAMPLE_INPUT, 19, 0)
        assert result is not None
        assert result.start.line == 19

    # -- Rejected targets ----------------------------------------------------

    def test_prepare_rename_rejects_namelist_header(self) -> None:
        """Namelist headers (&CONTROL) are not renamable."""
        assert _provider.prepare_rename(SAMPLE_INPUT, 0, 2) is None

    def test_prepare_rename_rejects_card_header(self) -> None:
        """Card headers (ATOMIC_SPECIES) are not renamable."""
        assert _provider.prepare_rename(SAMPLE_INPUT, 16, 2) is None

    def test_prepare_rename_rejects_slash(self) -> None:
        """Namelist terminator '/' is not renamable."""
        assert _provider.prepare_rename(SAMPLE_INPUT, 3, 0) is None

    def test_prepare_rename_rejects_blank(self) -> None:
        """Blank line cannot be renamed."""
        assert _provider.prepare_rename("", 0, 0) is None

    def test_prepare_rename_rejects_out_of_range(self) -> None:
        """Out-of-range line returns None."""
        assert _provider.prepare_rename("hello", 10, 0) is None


# ===========================================================================
# rename — namelist parameters (same file)
# ===========================================================================


class TestRenameNamelistParameter:
    """Rename should update all occurrences of a namelist parameter within
    the same namelist block."""

    def test_rename_ecutwfc(self) -> None:
        """Rename ecutwfc -> kinetic_cutoff produces one edit in &SYSTEM."""
        result = _provider.rename(SAMPLE_INPUT, URI, 9, 2, "kinetic_cutoff")
        assert result is not None
        assert isinstance(result, types.WorkspaceEdit)
        edits = _edits(result)
        assert len(edits) == 1
        assert edits[0].new_text == "kinetic_cutoff"
        assert edits[0].range.start.line == 9

    def test_rename_calculation(self) -> None:
        """Rename calculation -> calc_type in &CONTROL."""
        result = _provider.rename(SAMPLE_INPUT, URI, 1, 2, "calc_type")
        assert result is not None
        edits = _edits(result)
        assert len(edits) == 1
        assert edits[0].new_text == "calc_type"
        assert edits[0].range.start.line == 1

    def test_rename_celldm(self) -> None:
        """Rename celldm(1) -> lattice_a produces one edit."""
        result = _provider.rename(SAMPLE_INPUT, URI, 6, 2, "lattice_a")
        assert result is not None
        edits = _edits(result)
        assert len(edits) == 1
        assert edits[0].new_text == "lattice_a"
        assert edits[0].range.start.line == 6

    def test_rename_duplicate_parameter(self) -> None:
        """Rename of a duplicated parameter edits both occurrences."""
        result = _provider.rename(DUPLICATE_PARAM_INPUT, URI, 1, 2, "calc_type")
        assert result is not None
        edits = _edits(result)
        assert len(edits) == 2
        edit_lines = {e.range.start.line for e in edits}
        assert edit_lines == {1, 2}
        assert all(e.new_text == "calc_type" for e in edits)

    def test_rename_on_duplicate_line(self) -> None:
        """Triggering rename on the duplicate line itself still works."""
        result = _provider.rename(DUPLICATE_PARAM_INPUT, URI, 2, 2, "calc_type")
        assert result is not None
        edits = _edits(result)
        assert len(edits) == 2

    def test_rename_preserves_uri(self) -> None:
        """The returned WorkspaceEdit should reference the original URI."""
        custom_uri = "file:///custom/path.in"
        result = _provider.rename(SAMPLE_INPUT, custom_uri, 9, 2, "new_name")
        assert result is not None
        assert custom_uri in _changes(result)


# ===========================================================================
# rename — element symbols (cross-card same file)
# ===========================================================================


class TestRenameElementSymbol:
    """Rename should update element symbols across ATOMIC_SPECIES and
    ATOMIC_POSITIONS cards."""

    def test_rename_si_symbol(self) -> None:
        """Renaming Si -> Ge edits all Si rows in both cards."""
        result = _provider.rename(SAMPLE_INPUT, URI, 17, 0, "Ge")
        assert result is not None
        edits = _edits(result)
        # Si appears once in ATOMIC_SPECIES (line 17) and twice in
        # ATOMIC_POSITIONS (lines 19, 20).
        assert len(edits) == 3
        edit_lines = {e.range.start.line for e in edits}
        assert edit_lines == {17, 19, 20}
        assert all(e.new_text == "Ge" for e in edits)

    def test_rename_si_from_positions(self) -> None:
        """Triggering rename from ATOMIC_POSITIONS still edits species too."""
        result = _provider.rename(SAMPLE_INPUT, URI, 19, 0, "Ge")
        assert result is not None
        edits = _edits(result)
        assert len(edits) == 3

    def test_rename_multi_element_selective(self) -> None:
        """Renaming only Si leaves O untouched in MULTI_ELEMENT_INPUT."""
        result = _provider.rename(MULTI_ELEMENT_INPUT, URI, 10, 0, "Ge")
        assert result is not None
        edits = _edits(result)
        # Si at lines 10 (species), 13, 14 (positions) -> 3 edits
        assert len(edits) == 3
        edit_lines = {e.range.start.line for e in edits}
        assert 11 not in edit_lines  # O species row unchanged
        assert 15 not in edit_lines  # O positions unchanged
        assert 16 not in edit_lines  # O positions unchanged

    def test_rename_o_symbol(self) -> None:
        """Renaming O -> N in MULTI_ELEMENT_INPUT edits 3 rows."""
        result = _provider.rename(MULTI_ELEMENT_INPUT, URI, 11, 0, "N")
        assert result is not None
        edits = _edits(result)
        # O at lines 11 (species), 15, 16 (positions)
        assert len(edits) == 3
        edit_lines = {e.range.start.line for e in edits}
        assert edit_lines == {11, 15, 16}


# ===========================================================================
# rename — rejection cases
# ===========================================================================


class TestRenameRejection:
    """Rename should reject unsupported or ambiguous targets."""

    def test_reject_namelist_header(self) -> None:
        """Cannot rename &CONTROL."""
        result = _provider.rename(SAMPLE_INPUT, URI, 0, 2, "NewControl")
        assert result is None

    def test_reject_card_header(self) -> None:
        """Cannot rename ATOMIC_SPECIES."""
        result = _provider.rename(SAMPLE_INPUT, URI, 16, 2, "NEW_SPECIES")
        assert result is None

    def test_reject_empty_new_name(self) -> None:
        """Empty new_name is rejected."""
        result = _provider.rename(SAMPLE_INPUT, URI, 9, 2, "")
        assert result is None

    def test_reject_invalid_new_name(self) -> None:
        """New name starting with a digit is rejected."""
        result = _provider.rename(SAMPLE_INPUT, URI, 9, 2, "1bad")
        assert result is None

    def test_reject_new_name_with_spaces(self) -> None:
        """New name with spaces is rejected."""
        result = _provider.rename(SAMPLE_INPUT, URI, 9, 2, "has space")
        assert result is None

    def test_reject_unresolved_position(self) -> None:
        """A position that does not fall on any known symbol returns None."""
        result = _provider.rename(SAMPLE_INPUT, URI, 22, 2, "something")
        # Line 22 is "4 4 4 0 0 0" — not a namelist parameter or element symbol.
        assert result is None

    def test_reject_blank_text(self) -> None:
        """Empty document text yields None."""
        result = _provider.rename("", URI, 0, 0, "x")
        assert result is None

    def test_reject_out_of_range_line(self) -> None:
        """Negative or out-of-range line yields None."""
        result = _provider.rename(SAMPLE_INPUT, URI, -1, 0, "x")
        assert result is None

    def test_reject_slash_line(self) -> None:
        """Slash '/' terminator is not a renamable target."""
        result = _provider.rename(SAMPLE_INPUT, URI, 3, 0, "x")
        assert result is None

    def test_reject_k_points_data(self) -> None:
        """K_POINTS data rows (numbers) are not renamable."""
        result = _provider.rename(SAMPLE_INPUT, URI, 22, 0, "Fe")
        assert result is None


# ===========================================================================
# Handler-level tests
# ===========================================================================


class TestRenameHandler:
    """Handler-level integration for prepare_rename and rename."""

    def test_handler_prepare_rename(self) -> None:
        """prepare_rename handler returns a Range for a valid parameter."""
        params = Params(SAMPLE_INPUT, line=9, character=2)
        result = prepare_rename(params)
        assert result is not None
        assert isinstance(result, types.Range)

    def test_handler_rename(self) -> None:
        """rename handler returns a WorkspaceEdit for a valid rename."""
        params = Params(SAMPLE_INPUT, line=9, character=2, new_name="kinetic_cutoff")
        result = rename(params)
        assert result is not None
        assert isinstance(result, types.WorkspaceEdit)
        assert URI in _changes(result)
        assert _edits(result)[0].new_text == "kinetic_cutoff"

    def test_handler_prepare_rename_rejects(self) -> None:
        """prepare_rename handler returns None for a namelist header."""
        params = Params(SAMPLE_INPUT, line=0, character=2)
        assert prepare_rename(params) is None

    def test_handler_rename_rejects(self) -> None:
        """rename handler returns None for an unresolvable position."""
        params = Params(SAMPLE_INPUT, line=22, character=2, new_name="x")
        assert rename(params) is None

    def test_handler_rename_rejects_invalid_name(self) -> None:
        """rename handler returns None for an invalid new name."""
        params = Params(SAMPLE_INPUT, line=9, character=2, new_name="1bad")
        assert rename(params) is None

    def test_handler_rename_empty_text(self) -> None:
        """rename handler returns None for empty text."""
        params = Params("", line=0, character=0, new_name="x")
        assert rename(params) is None

    def test_handler_prepare_rename_empty_text(self) -> None:
        """prepare_rename handler returns None for empty text."""
        params = Params("", line=0, character=0)
        assert prepare_rename(params) is None


# ===========================================================================
# Server registration
# ===========================================================================


class TestRenameServerRegistration:
    def test_server_registers_prepare_rename(self) -> None:
        from qe_lsp.server import server

        features = server.lsp.fm.features
        assert "textDocument/prepareRename" in features

    def test_server_registers_rename(self) -> None:
        from qe_lsp.server import server

        features = server.lsp.fm.features
        assert "textDocument/rename" in features


# ===========================================================================
# Edge cases
# ===========================================================================


class TestRenameEdgeCases:
    def test_valid_new_name_with_underscore(self) -> None:
        """Underscore-prefixed new name is accepted."""
        result = _provider.rename(SAMPLE_INPUT, URI, 9, 2, "_ecutwfc")
        assert result is not None

    def test_valid_new_name_all_uppercase(self) -> None:
        """All-uppercase new name is accepted."""
        result = _provider.rename(SAMPLE_INPUT, URI, 9, 2, "ECUTWFC")
        assert result is not None

    def test_parameter_value_not_renamed(self) -> None:
        """Rename should only edit the parameter name, not its value."""
        result = _provider.rename(SAMPLE_INPUT, URI, 1, 2, "calc_type")
        assert result is not None
        edits = _edits(result)
        # Only one edit for the name itself (line 1, starting at char 2).
        assert len(edits) == 1
        edit = edits[0]
        assert edit.range.start.character == 2
        assert edit.range.end.character == 2 + len("calculation")

    def test_different_namelist_same_param_name_not_renamed(self) -> None:
        """A parameter in one namelist should NOT rename a parameter with
        the same name in a different namelist."""
        text = "&CONTROL\n" "  title = 'ctrl'\n" "/\n" "&SYSTEM\n" "  ecutwfc = 60\n" "/\n"
        # Rename ecutwfc in &SYSTEM — should only edit line 4.
        result = _provider.rename(text, URI, 4, 2, "cutoff")
        assert result is not None
        edits = _edits(result)
        assert len(edits) == 1
        assert edits[0].range.start.line == 4

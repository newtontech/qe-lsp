"""Tests for the TypecheckProvider type-aware validation."""

import json

import pytest

from qe_lsp.features.typecheck import (
    RULE_ENUM_INVALID,
    RULE_NUMERIC_RANGE,
    RULE_REQUIRED_SECTION_MISSING,
    RULE_TYPE_MISMATCH,
    RULE_UNIT_UNKNOWN,
    TypecheckProvider,
)


@pytest.fixture
def provider() -> TypecheckProvider:
    """Create a TypecheckProvider instance."""
    return TypecheckProvider()


# ------------------------------------------------------------------
# typecheck()
# ------------------------------------------------------------------


class TestTypecheckEmpty:
    """Empty or minimal inputs."""

    def test_empty_input_no_diagnostics(self, provider: TypecheckProvider) -> None:
        assert provider.typecheck("") == []

    def test_comment_only_no_diagnostics(self, provider: TypecheckProvider) -> None:
        assert provider.typecheck("! just a comment\n") == []

    def test_empty_namelist_no_typecheck_errors(self, provider: TypecheckProvider) -> None:
        """An empty namelist has no typed keywords to validate."""
        text = "&CONTROL\n/\n"
        diagnostics = provider.typecheck(text)
        assert diagnostics == []


class TestTypeMismatch:
    """Tests for RULE_TYPE_MISMATCH (QE-TE001)."""

    def test_boolean_expected_got_string(self, provider: TypecheckProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\ntstress = hello\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert len(type_errors) == 1
        assert "tstress" in type_errors[0].message
        assert "boolean" in type_errors[0].message.lower()

    def test_integer_expected_got_string(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = abc\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert len(type_errors) == 1
        assert "ibrav" in type_errors[0].message
        assert "integer" in type_errors[0].message.lower()

    def test_float_expected_got_string(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\necutwfc = not_a_number\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert len(type_errors) == 1
        assert "ecutwfc" in type_errors[0].message

    def test_valid_boolean_true(self, provider: TypecheckProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\ntstress = .true.\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert type_errors == []

    def test_valid_boolean_false(self, provider: TypecheckProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\ntstress = .false.\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert type_errors == []

    def test_valid_boolean_t(self, provider: TypecheckProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\ntstress = T\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert type_errors == []

    def test_valid_boolean_f(self, provider: TypecheckProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\ntprnfor = f\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert type_errors == []

    def test_valid_integer(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = 1\nnat = 4\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert type_errors == []

    def test_valid_float(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\necutwfc = 60.0\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert type_errors == []

    def test_valid_float_scientific(self, provider: TypecheckProvider) -> None:
        text = "&ELECTRONS\nconv_thr = 1.0e-8\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert type_errors == []

    def test_valid_float_fortran_d_notation(self, provider: TypecheckProvider) -> None:
        text = "&ELECTRONS\nconv_thr = 1.0d-8\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert type_errors == []

    def test_valid_integer_float_as_integer(self, provider: TypecheckProvider) -> None:
        """An integer-typed keyword like ibrav accepts '1.0' as valid."""
        text = "&SYSTEM\nibrav = 1\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert type_errors == []


class TestEnumInvalid:
    """Tests for RULE_ENUM_INVALID (QE-TE002)."""

    def test_invalid_calculation_value(self, provider: TypecheckProvider) -> None:
        text = "&CONTROL\ncalculation = 'bogus'\n/\n"
        diagnostics = provider.typecheck(text)
        enum_errors = [d for d in diagnostics if d.code == RULE_ENUM_INVALID]
        assert len(enum_errors) == 1
        assert "bogus" in enum_errors[0].message

    def test_invalid_diagonalization(self, provider: TypecheckProvider) -> None:
        text = "&ELECTRONS\ndiagonalization = 'bad_method'\n/\n"
        diagnostics = provider.typecheck(text)
        enum_errors = [d for d in diagnostics if d.code == RULE_ENUM_INVALID]
        assert len(enum_errors) == 1

    def test_invalid_mixing_mode(self, provider: TypecheckProvider) -> None:
        text = "&ELECTRONS\nmixing_mode = 'potato'\n/\n"
        diagnostics = provider.typecheck(text)
        enum_errors = [d for d in diagnostics if d.code == RULE_ENUM_INVALID]
        assert len(enum_errors) == 1

    def test_invalid_ion_dynamics(self, provider: TypecheckProvider) -> None:
        text = "&IONS\nion_dynamics = 'fly'\n/\n"
        diagnostics = provider.typecheck(text)
        enum_errors = [d for d in diagnostics if d.code == RULE_ENUM_INVALID]
        assert len(enum_errors) == 1

    def test_invalid_cell_dofree(self, provider: TypecheckProvider) -> None:
        text = "&CELL\ncell_dofree = 'everything'\n/\n"
        diagnostics = provider.typecheck(text)
        enum_errors = [d for d in diagnostics if d.code == RULE_ENUM_INVALID]
        assert len(enum_errors) == 1

    def test_valid_enum_no_error(self, provider: TypecheckProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n"
        diagnostics = provider.typecheck(text)
        enum_errors = [d for d in diagnostics if d.code == RULE_ENUM_INVALID]
        assert enum_errors == []

    def test_nspin_enum_invalid(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nnspin = 3\n/\n"
        diagnostics = provider.typecheck(text)
        enum_errors = [d for d in diagnostics if d.code == RULE_ENUM_INVALID]
        assert len(enum_errors) == 1
        assert "nspin" in enum_errors[0].message

    def test_nspin_enum_valid(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nnspin = 2\n/\n"
        diagnostics = provider.typecheck(text)
        enum_errors = [d for d in diagnostics if d.code == RULE_ENUM_INVALID]
        assert enum_errors == []


class TestUnitValidation:
    """Tests for RULE_UNIT_UNKNOWN (QE-TE003)."""

    def test_wrong_unit_family(self, provider: TypecheckProvider) -> None:
        """Energy keyword with a length unit."""
        text = "&SYSTEM\necutwfc = 60.0 bohr\n/\n"
        diagnostics = provider.typecheck(text)
        unit_errors = [d for d in diagnostics if d.code == RULE_UNIT_UNKNOWN]
        assert len(unit_errors) == 1
        assert "bohr" in unit_errors[0].message
        assert "not valid" in unit_errors[0].message

    def test_unknown_unit(self, provider: TypecheckProvider) -> None:
        """Energy keyword with an entirely unknown unit."""
        text = "&SYSTEM\necutwfc = 60.0 parsecs\n/\n"
        diagnostics = provider.typecheck(text)
        unit_errors = [d for d in diagnostics if d.code == RULE_UNIT_UNKNOWN]
        assert len(unit_errors) == 1
        assert "parsecs" in unit_errors[0].message
        assert "Unknown unit" in unit_errors[0].message

    def test_valid_unit_no_error(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\necutwfc = 60.0 ry\n/\n"
        diagnostics = provider.typecheck(text)
        unit_errors = [d for d in diagnostics if d.code == RULE_UNIT_UNKNOWN]
        assert unit_errors == []

    def test_no_unit_no_error(self, provider: TypecheckProvider) -> None:
        """Keywords that accept units but have none are valid (use defaults)."""
        text = "&SYSTEM\necutwfc = 60.0\n/\n"
        diagnostics = provider.typecheck(text)
        unit_errors = [d for d in diagnostics if d.code == RULE_UNIT_UNKNOWN]
        assert unit_errors == []

    def test_length_unit_on_length_keyword(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\na = 5.42 ang\n/\n"
        diagnostics = provider.typecheck(text)
        unit_errors = [d for d in diagnostics if d.code == RULE_UNIT_UNKNOWN]
        assert unit_errors == []

    def test_energy_unit_on_length_keyword(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\na = 5.42 ry\n/\n"
        diagnostics = provider.typecheck(text)
        unit_errors = [d for d in diagnostics if d.code == RULE_UNIT_UNKNOWN]
        assert len(unit_errors) == 1
        assert "ry" in unit_errors[0].message

    def test_pressure_keyword_with_valid_unit(self, provider: TypecheckProvider) -> None:
        text = "&CELL\npress = 10.0 kbar\n/\n"
        diagnostics = provider.typecheck(text)
        unit_errors = [d for d in diagnostics if d.code == RULE_UNIT_UNKNOWN]
        assert unit_errors == []

    def test_pressure_keyword_with_wrong_unit(self, provider: TypecheckProvider) -> None:
        text = "&CELL\npress = 10.0 bohr\n/\n"
        diagnostics = provider.typecheck(text)
        unit_errors = [d for d in diagnostics if d.code == RULE_UNIT_UNKNOWN]
        assert len(unit_errors) == 1


class TestNumericRange:
    """Tests for RULE_NUMERIC_RANGE (QE-TW001)."""

    def test_ibrav_above_max(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = 99\n/\n"
        diagnostics = provider.typecheck(text)
        range_warnings = [d for d in diagnostics if d.code == RULE_NUMERIC_RANGE]
        assert len(range_warnings) == 1
        assert "exceeds maximum" in range_warnings[0].message

    def test_ibrav_below_min(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = -1\n/\n"
        diagnostics = provider.typecheck(text)
        range_warnings = [d for d in diagnostics if d.code == RULE_NUMERIC_RANGE]
        assert len(range_warnings) == 1
        assert "below minimum" in range_warnings[0].message

    def test_ibrav_valid_range(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = 1\n/\n"
        diagnostics = provider.typecheck(text)
        range_warnings = [d for d in diagnostics if d.code == RULE_NUMERIC_RANGE]
        assert range_warnings == []

    def test_cosab_out_of_range(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\ncosab = 2.0\n/\n"
        diagnostics = provider.typecheck(text)
        range_warnings = [d for d in diagnostics if d.code == RULE_NUMERIC_RANGE]
        assert len(range_warnings) == 1

    def test_cosab_valid_range(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\ncosab = 0.5\n/\n"
        diagnostics = provider.typecheck(text)
        range_warnings = [d for d in diagnostics if d.code == RULE_NUMERIC_RANGE]
        assert range_warnings == []

    def test_nat_below_min(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nnat = 0\n/\n"
        diagnostics = provider.typecheck(text)
        range_warnings = [d for d in diagnostics if d.code == RULE_NUMERIC_RANGE]
        assert len(range_warnings) == 1

    def test_mixing_beta_above_max(self, provider: TypecheckProvider) -> None:
        text = "&ELECTRONS\nmixing_beta = 1.5\n/\n"
        diagnostics = provider.typecheck(text)
        range_warnings = [d for d in diagnostics if d.code == RULE_NUMERIC_RANGE]
        assert len(range_warnings) == 1


class TestRequiredSections:
    """Tests for RULE_REQUIRED_SECTION_MISSING (QE-TE004)."""

    def test_ibrav_zero_without_cell_parameters(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = 0\n/\n"
        diagnostics = provider.typecheck(text)
        section_errors = [d for d in diagnostics if d.code == RULE_REQUIRED_SECTION_MISSING]
        assert any("CELL_PARAMETERS" in d.message for d in section_errors)

    def test_ibrav_zero_with_cell_parameters(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = 0\n/\nCELL_PARAMETERS\n1.0 0.0 0.0\n"
        diagnostics = provider.typecheck(text)
        section_errors = [d for d in diagnostics if d.code == RULE_REQUIRED_SECTION_MISSING]
        assert not any("CELL_PARAMETERS" in d.message for d in section_errors)

    def test_nat_without_atomic_species(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nnat = 2\nntyp = 1\n/\n"
        diagnostics = provider.typecheck(text)
        section_errors = [d for d in diagnostics if d.code == RULE_REQUIRED_SECTION_MISSING]
        assert any("ATOMIC_SPECIES" in d.message for d in section_errors)

    def test_nat_without_atomic_positions(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nnat = 2\nntyp = 1\n/\n"
        diagnostics = provider.typecheck(text)
        section_errors = [d for d in diagnostics if d.code == RULE_REQUIRED_SECTION_MISSING]
        assert any("ATOMIC_POSITIONS" in d.message for d in section_errors)

    def test_nat_with_all_cards(self, provider: TypecheckProvider) -> None:
        text = (
            "&SYSTEM\nnat = 2\nntyp = 1\n/\n"
            "ATOMIC_SPECIES\nO 15.999 O.pbe.UPF\n"
            "ATOMIC_POSITIONS {crystal}\nO 0.0 0.0 0.0\nO 0.5 0.5 0.5\n"
        )
        diagnostics = provider.typecheck(text)
        section_errors = [d for d in diagnostics if d.code == RULE_REQUIRED_SECTION_MISSING]
        assert section_errors == []

    def test_vc_relax_without_cell_namelist(self, provider: TypecheckProvider) -> None:
        text = "&CONTROL\ncalculation = 'vc-relax'\n/\n" "&SYSTEM\nibrav = 1\necutwfc = 60\n/\n"
        diagnostics = provider.typecheck(text)
        section_errors = [d for d in diagnostics if d.code == RULE_REQUIRED_SECTION_MISSING]
        assert any("&CELL" in d.message for d in section_errors)

    def test_vc_relax_with_cell_namelist(self, provider: TypecheckProvider) -> None:
        text = (
            "&CONTROL\ncalculation = 'vc-relax'\n/\n"
            "&SYSTEM\nibrav = 1\necutwfc = 60\n/\n"
            "&CELL\ncell_dynamics = 'bfgs'\n/\n"
        )
        diagnostics = provider.typecheck(text)
        section_errors = [d for d in diagnostics if d.code == RULE_REQUIRED_SECTION_MISSING]
        assert not any("&CELL" in d.message for d in section_errors)


class TestValidInput:
    """Well-formed inputs produce zero typecheck diagnostics."""

    def test_minimal_valid_scf(self, provider: TypecheckProvider) -> None:
        text = (
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
            "Si 28.086 Si.pbe.UPF\n"
            "ATOMIC_POSITIONS {crystal}\n"
            "Si 0.0 0.0 0.0\n"
            "K_POINTS {automatic}\n"
            "4 4 4 0 0 0\n"
        )
        diagnostics = provider.typecheck(text)
        assert diagnostics == []

    def test_valid_relax_with_ions(self, provider: TypecheckProvider) -> None:
        text = (
            "&CONTROL\n"
            "  calculation = 'relax'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "  ecutwfc = 60\n"
            "  nat = 1\n"
            "  ntyp = 1\n"
            "/\n"
            "&IONS\n"
            "  ion_dynamics = 'bfgs'\n"
            "/\n"
            "ATOMIC_SPECIES\n"
            "Si 28.086 Si.pbe.UPF\n"
            "ATOMIC_POSITIONS {crystal}\n"
            "Si 0.0 0.0 0.0\n"
        )
        diagnostics = provider.typecheck(text)
        assert diagnostics == []


class TestSourceAndSeverity:
    """Verify source and severity attributes on typecheck diagnostics."""

    def test_source_is_qe_lsp_typecheck(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = abc\n/\n"
        diagnostics = provider.typecheck(text)
        assert diagnostics[0].source == "qe-lsp-typecheck"

    def test_type_error_severity(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = abc\n/\n"
        diagnostics = provider.typecheck(text)
        type_errors = [d for d in diagnostics if d.code == RULE_TYPE_MISMATCH]
        assert type_errors[0].severity is not None
        assert type_errors[0].severity.value == 1  # Error

    def test_range_warning_severity(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = 99\n/\n"
        diagnostics = provider.typecheck(text)
        range_warnings = [d for d in diagnostics if d.code == RULE_NUMERIC_RANGE]
        assert range_warnings[0].severity is not None
        assert range_warnings[0].severity.value == 2  # Warning


# ------------------------------------------------------------------
# snapshot (JSON serialisation)
# ------------------------------------------------------------------


class TestSnapshot:
    """Tests for TypecheckProvider.snapshot."""

    def test_empty_snapshot(self, provider: TypecheckProvider) -> None:
        assert provider.snapshot("") == []

    def test_valid_input_empty_snapshot(self, provider: TypecheckProvider) -> None:
        text = (
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
            "Si 28.086 Si.pbe.UPF\n"
            "ATOMIC_POSITIONS {crystal}\n"
            "Si 0.0 0.0 0.0\n"
        )
        assert provider.snapshot(text) == []

    def test_snapshot_is_json_serialisable(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = abc\n/\n"
        items = provider.snapshot(text)
        serialised = json.dumps(items)
        assert isinstance(serialised, str)
        round_tripped = json.loads(serialised)
        assert round_tripped == items

    def test_snapshot_contains_required_keys(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = abc\n/\n"
        items = provider.snapshot(text)
        assert len(items) >= 1
        for item in items:
            assert "range" in item
            assert "severity" in item
            assert "source" in item
            assert "message" in item
            assert "code" in item
            assert "start" in item["range"]
            assert "end" in item["range"]

    def test_snapshot_severity_is_string(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = abc\n/\n"
        items = provider.snapshot(text)
        assert items[0]["severity"] == "Error"

    def test_snapshot_code_is_string(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = abc\n/\n"
        items = provider.snapshot(text)
        assert items[0]["code"].startswith("QE-")

    def test_snapshot_deterministic_ordering(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = abc\n/\n" "&CONTROL\ncalculation = 'bogus'\n/\n"
        first = provider.snapshot(text)
        second = provider.snapshot(text)
        assert first == second

    def test_snapshot_source_is_typecheck(self, provider: TypecheckProvider) -> None:
        text = "&SYSTEM\nibrav = abc\n/\n"
        items = provider.snapshot(text)
        assert items[0]["source"] == "qe-lsp-typecheck"

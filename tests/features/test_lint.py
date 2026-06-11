"""Tests for the LintProvider schema-aware static checks."""

import json

import pytest

from qe_lsp.features.lint import (
    LintProvider,
    RULE_BAD_CALCULATION,
    RULE_CONV_THR_LOOSE,
    RULE_DEPRECATED_KEYWORD,
    RULE_ECUTRHO_INCONSISTENT,
    RULE_INCONSISTENT_SETTINGS,
    RULE_INVALID_KEYWORD_VALUE,
    RULE_MISSING_ATOMIC_POSITIONS,
    RULE_MISSING_ATOMIC_SPECIES,
    RULE_MISSING_CONTROL,
    RULE_MISSING_CONTROL_CALC,
    RULE_MISSING_REQUIRED_SECTION,
    RULE_MISSING_SYSTEM_ECUTWFC,
    RULE_OCCUPATIONS_DEGAUSS_MISMATCH,
    RULE_ORPHAN_PARAMETER,
    RULE_UNKNOWN_KEYWORD,
    RULE_UNKNOWN_NAMELIST,
)


@pytest.fixture
def provider() -> LintProvider:
    """Create a LintProvider instance."""
    return LintProvider()


# ------------------------------------------------------------------
# lint()
# ------------------------------------------------------------------


class TestLintEmpty:
    """Empty or minimal inputs."""

    def test_empty_input_no_diagnostics(self, provider: LintProvider) -> None:
        assert provider.lint("") == []

    def test_comment_only_no_diagnostics(self, provider: LintProvider) -> None:
        assert provider.lint("! just a comment\n") == []

    def test_empty_namelist_reports_missing_required(self, provider: LintProvider) -> None:
        """An empty &CONTROL is treated as missing; &SYSTEM is also missing."""
        text = "&CONTROL\n/\n"
        diagnostics = provider.lint(text)
        codes = [d.code for d in diagnostics]
        assert RULE_MISSING_REQUIRED_SECTION in codes

    def test_minimal_valid_input_no_errors(self, provider: LintProvider) -> None:
        """A well-formed minimal input produces zero errors."""
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
        diagnostics = provider.lint(text)
        assert diagnostics == []


class TestLintWarnings:
    """Warning-level diagnostics."""

    def test_unknown_keyword_warning(self, provider: LintProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\ntypo_param = 42\n/\n"
        diagnostics = provider.lint(text)
        unknowns = [d for d in diagnostics if d.code == RULE_UNKNOWN_KEYWORD]
        assert len(unknowns) == 1
        assert "typo_param" in unknowns[0].message
        assert unknowns[0].severity is not None
        assert unknowns[0].severity.value == 2  # Warning

    def test_deprecated_keyword_warning(self, provider: LintProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\nnstep = 100\n/\n"
        diagnostics = provider.lint(text)
        deprecated = [d for d in diagnostics if d.code == RULE_DEPRECATED_KEYWORD]
        assert len(deprecated) == 1
        assert "nstep" in deprecated[0].message

    def test_orphan_parameter_warning(self, provider: LintProvider) -> None:
        text = "foo = 42\n&CONTROL\ncalculation = 'scf'\n/\n"
        diagnostics = provider.lint(text)
        orphans = [d for d in diagnostics if d.code == RULE_ORPHAN_PARAMETER]
        assert len(orphans) == 1
        assert "foo" in orphans[0].message

    def test_orphan_parameter_after_namelist_close(self, provider: LintProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\nbar = 99\n"
        diagnostics = provider.lint(text)
        orphans = [d for d in diagnostics if d.code == RULE_ORPHAN_PARAMETER]
        assert len(orphans) == 1
        assert "bar" in orphans[0].message

    def test_relax_without_ions(self, provider: LintProvider) -> None:
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
        )
        diagnostics = provider.lint(text)
        inconsistencies = [d for d in diagnostics if d.code == RULE_INCONSISTENT_SETTINGS]
        assert any("&IONS" in d.message for d in inconsistencies)

    def test_nscf_without_nbnd(self, provider: LintProvider) -> None:
        text = (
            "&CONTROL\n"
            "  calculation = 'nscf'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "  ecutwfc = 60\n"
            "  nat = 1\n"
            "  ntyp = 1\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        inconsistencies = [d for d in diagnostics if d.code == RULE_INCONSISTENT_SETTINGS]
        assert any("nbnd" in d.message for d in inconsistencies)


class TestLintErrors:
    """Error-level diagnostics."""

    def test_unknown_namelist(self, provider: LintProvider) -> None:
        text = "&FOOBAR\nx = 1\n/\n"
        diagnostics = provider.lint(text)
        unknowns = [d for d in diagnostics if d.code == RULE_UNKNOWN_NAMELIST]
        assert len(unknowns) == 1
        assert "FOOBAR" in unknowns[0].message
        assert unknowns[0].severity is not None
        assert unknowns[0].severity.value == 1  # Error

    def test_invalid_calculation_value(self, provider: LintProvider) -> None:
        text = "&CONTROL\ncalculation = 'bogus'\n/\n"
        diagnostics = provider.lint(text)
        bad_calc = [d for d in diagnostics if d.code == RULE_BAD_CALCULATION]
        assert len(bad_calc) == 1
        assert "bogus" in bad_calc[0].message
        assert bad_calc[0].severity is not None
        assert bad_calc[0].severity.value == 1  # Error

    def test_valid_calculation_values_no_error(self, provider: LintProvider) -> None:
        """All known valid calculation values should NOT trigger RULE_BAD_CALCULATION."""
        for calc in ("scf", "nscf", "bands", "relax", "md", "vc-relax", "vc-md", "cp", "vc-cp"):
            text = f"&CONTROL\ncalculation = '{calc}'\n/\n"
            diagnostics = provider.lint(text)
            bad_calc = [d for d in diagnostics if d.code == RULE_BAD_CALCULATION]
            assert bad_calc == [], f"calculation='{calc}' should be valid"

    def test_missing_calculation_no_bad_calculation_error(self, provider: LintProvider) -> None:
        """Missing 'calculation' keyword is covered by RULE_MISSING_CONTROL_CALC,
        not by RULE_BAD_CALCULATION."""
        text = "&CONTROL\noutdir = './tmp'\n/\n"
        diagnostics = provider.lint(text)
        bad_calc = [d for d in diagnostics if d.code == RULE_BAD_CALCULATION]
        assert bad_calc == []

    def test_invalid_diagonalization_value(self, provider: LintProvider) -> None:
        text = "&ELECTRONS\ndiagonalization = 'invalid_method'\n/\n"
        diagnostics = provider.lint(text)
        invalids = [d for d in diagnostics if d.code == RULE_INVALID_KEYWORD_VALUE]
        assert len(invalids) == 1

    def test_invalid_mixing_mode(self, provider: LintProvider) -> None:
        text = "&ELECTRONS\nmixing_mode = 'potato'\n/\n"
        diagnostics = provider.lint(text)
        invalids = [d for d in diagnostics if d.code == RULE_INVALID_KEYWORD_VALUE]
        assert len(invalids) == 1

    def test_missing_control_calculation(self, provider: LintProvider) -> None:
        text = "&CONTROL\noutdir = './tmp'\n/\n"
        diagnostics = provider.lint(text)
        codes = [d.code for d in diagnostics]
        assert RULE_MISSING_CONTROL_CALC in codes

    def test_rule_missing_control_namelist(self, provider: LintProvider) -> None:
        """RULE qe.input.missing_control: error when &CONTROL namelist is absent."""
        text = "&SYSTEM\n  ibrav = 2,\n/\n"
        diagnostics = provider.lint(text)
        missing = [d for d in diagnostics if d.code == RULE_MISSING_CONTROL]
        assert len(missing) == 1
        assert "CONTROL" in missing[0].message
        assert missing[0].severity is not None
        assert missing[0].severity.value == 1  # Error

    def test_missing_control_with_only_electrons(self, provider: LintProvider) -> None:
        """Even &ELECTRONS alone should trigger missing &CONTROL."""
        text = "&ELECTRONS\nconv_thr = 1e-8\n/\n"
        diagnostics = provider.lint(text)
        missing = [d for d in diagnostics if d.code == RULE_MISSING_CONTROL]
        assert len(missing) == 1

    def test_control_present_no_missing_control_error(self, provider: LintProvider) -> None:
        """When &CONTROL exists, RULE_MISSING_CONTROL should NOT fire."""
        text = "&CONTROL\ncalculation = 'scf'\n/\n"
        diagnostics = provider.lint(text)
        missing = [d for d in diagnostics if d.code == RULE_MISSING_CONTROL]
        assert missing == []

    def test_missing_system_ecutwfc(self, provider: LintProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n&SYSTEM\nibrav = 1\n/\n"
        diagnostics = provider.lint(text)
        codes = [d.code for d in diagnostics]
        assert RULE_MISSING_SYSTEM_ECUTWFC in codes

    def test_vc_relax_without_cell_namelist(self, provider: LintProvider) -> None:
        text = "&CONTROL\n  calculation = 'vc-relax'\n/\n&SYSTEM\n  ibrav = 1\n  ecutwfc = 60\n/\n"
        diagnostics = provider.lint(text)
        errors = [d for d in diagnostics if d.code == RULE_INCONSISTENT_SETTINGS]
        assert any("&CELL" in d.message for d in errors)

    def test_missing_atomic_species(self, provider: LintProvider) -> None:
        text = (
            "&CONTROL\ncalculation = 'scf'\n/\n"
            "&SYSTEM\nibrav = 1\necutwfc = 60\nnat = 2\nntyp = 1\n/\n"
        )
        diagnostics = provider.lint(text)
        codes = [d.code for d in diagnostics]
        assert RULE_MISSING_ATOMIC_SPECIES in codes

    def test_missing_atomic_positions(self, provider: LintProvider) -> None:
        text = (
            "&CONTROL\ncalculation = 'scf'\n/\n"
            "&SYSTEM\nibrav = 1\necutwfc = 60\nnat = 2\nntyp = 1\n/\n"
        )
        diagnostics = provider.lint(text)
        codes = [d.code for d in diagnostics]
        assert RULE_MISSING_ATOMIC_POSITIONS in codes


class TestConvThrLoose:
    """RULE qe.scf.conv_thr_loose (QE-W010): warn when conv_thr > 1e-4."""

    def test_loose_conv_thr_triggers_warning(self, provider: LintProvider) -> None:
        text = "&ELECTRONS\n  conv_thr = 1e-3\n/\n"
        diagnostics = provider.lint(text)
        loose = [d for d in diagnostics if d.code == RULE_CONV_THR_LOOSE]
        assert len(loose) == 1
        assert "conv_thr" in loose[0].message
        assert loose[0].severity is not None
        assert loose[0].severity.value == 2  # Warning

    def test_tight_conv_thr_no_warning(self, provider: LintProvider) -> None:
        text = "&ELECTRONS\n  conv_thr = 1e-8\n/\n"
        diagnostics = provider.lint(text)
        loose = [d for d in diagnostics if d.code == RULE_CONV_THR_LOOSE]
        assert loose == []

    def test_exact_threshold_no_warning(self, provider: LintProvider) -> None:
        """conv_thr = 1e-4 exactly should NOT trigger the warning."""
        text = "&ELECTRONS\n  conv_thr = 1e-4\n/\n"
        diagnostics = provider.lint(text)
        loose = [d for d in diagnostics if d.code == RULE_CONV_THR_LOOSE]
        assert loose == []

    def test_no_conv_thr_no_warning(self, provider: LintProvider) -> None:
        text = "&ELECTRONS\n  mixing_beta = 0.7\n/\n"
        diagnostics = provider.lint(text)
        loose = [d for d in diagnostics if d.code == RULE_CONV_THR_LOOSE]
        assert loose == []

    def test_very_loose_conv_thr(self, provider: LintProvider) -> None:
        """conv_thr = 0.1 is clearly too loose."""
        text = "&ELECTRONS\n  conv_thr = 0.1\n/\n"
        diagnostics = provider.lint(text)
        loose = [d for d in diagnostics if d.code == RULE_CONV_THR_LOOSE]
        assert len(loose) == 1
        assert "0.1" in loose[0].message

    def test_snapshot_includes_conv_thr_warning(self, provider: LintProvider) -> None:
        text = "&ELECTRONS\n  conv_thr = 1e-3\n/\n"
        items = provider.snapshot(text)
        loose_items = [i for i in items if i["code"] == RULE_CONV_THR_LOOSE]
        assert len(loose_items) == 1
        assert loose_items[0]["severity"] == "Warning"


class TestEcutrhoInconsistent:
    """RULE qe.cutoff.ecutrho_inconsistent (QE-W011): warn when ecutrho is
    outside the 4x-16x ecutwfc range."""

    def test_ecutrho_too_low_triggers_warning(self, provider: LintProvider) -> None:
        """ecutrho = 2*ecutwfc is below the 4x minimum."""
        text = (
            "&CONTROL\n"
            "  calculation = 'scf'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "  ecutwfc = 60.0\n"
            "  ecutrho = 120.0\n"
            "  nat = 1\n"
            "  ntyp = 1\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_ECUTRHO_INCONSISTENT]
        assert len(warnings) == 1
        assert "ecutrho" in warnings[0].message
        assert warnings[0].severity is not None
        assert warnings[0].severity.value == 2  # Warning

    def test_ecutrho_too_high_triggers_warning(self, provider: LintProvider) -> None:
        """ecutrho = 20*ecutwfc is above the 16x maximum."""
        text = (
            "&CONTROL\n"
            "  calculation = 'scf'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "  ecutwfc = 60.0\n"
            "  ecutrho = 1200.0\n"
            "  nat = 1\n"
            "  ntyp = 1\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_ECUTRHO_INCONSISTENT]
        assert len(warnings) == 1

    def test_ecutrho_4x_ecutwfc_no_warning(self, provider: LintProvider) -> None:
        """ecutrho = 4*ecutwfc is the lower bound and should NOT warn."""
        text = (
            "&CONTROL\n"
            "  calculation = 'scf'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "  ecutwfc = 60.0\n"
            "  ecutrho = 240.0\n"
            "  nat = 1\n"
            "  ntyp = 1\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_ECUTRHO_INCONSISTENT]
        assert warnings == []

    def test_ecutrho_16x_ecutwfc_no_warning(self, provider: LintProvider) -> None:
        """ecutrho = 16*ecutwfc is the upper bound and should NOT warn."""
        text = (
            "&CONTROL\n"
            "  calculation = 'scf'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "  ecutwfc = 60.0\n"
            "  ecutrho = 960.0\n"
            "  nat = 1\n"
            "  ntyp = 1\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_ECUTRHO_INCONSISTENT]
        assert warnings == []

    def test_ecutrho_8x_ecutwfc_no_warning(self, provider: LintProvider) -> None:
        """ecutrho = 8*ecutwfc is a typical valid ratio."""
        text = (
            "&CONTROL\n"
            "  calculation = 'scf'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "  ecutwfc = 60.0\n"
            "  ecutrho = 480.0\n"
            "  nat = 1\n"
            "  ntyp = 1\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_ECUTRHO_INCONSISTENT]
        assert warnings == []

    def test_no_ecutrho_no_warning(self, provider: LintProvider) -> None:
        """Missing ecutrho should NOT trigger the check."""
        text = (
            "&CONTROL\n"
            "  calculation = 'scf'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "  ecutwfc = 60.0\n"
            "  nat = 1\n"
            "  ntyp = 1\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_ECUTRHO_INCONSISTENT]
        assert warnings == []

    def test_no_ecutwfc_no_warning(self, provider: LintProvider) -> None:
        """Missing ecutwfc should NOT trigger the check."""
        text = (
            "&CONTROL\n"
            "  calculation = 'scf'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "  ecutrho = 480.0\n"
            "  nat = 1\n"
            "  ntyp = 1\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_ECUTRHO_INCONSISTENT]
        assert warnings == []

    def test_snapshot_includes_ecutrho_warning(self, provider: LintProvider) -> None:
        text = (
            "&CONTROL\n"
            "  calculation = 'scf'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "  ecutwfc = 60.0\n"
            "  ecutrho = 120.0\n"
            "  nat = 1\n"
            "  ntyp = 1\n"
            "/\n"
        )
        items = provider.snapshot(text)
        warnings = [i for i in items if i["code"] == RULE_ECUTRHO_INCONSISTENT]
        assert len(warnings) == 1
        assert warnings[0]["severity"] == "Warning"


class TestLintSourceAndCode:
    """Verify source and code attributes on lint diagnostics."""

    def test_source_is_qe_lsp_lint(self, provider: LintProvider) -> None:
        text = "&FOOBAR\nx = 1\n/\n"
        diagnostics = provider.lint(text)
        assert diagnostics[0].source == "qe-lsp-lint"

    def test_code_is_set(self, provider: LintProvider) -> None:
        text = "&FOOBAR\nx = 1\n/\n"
        diagnostics = provider.lint(text)
        assert diagnostics[0].code is not None
        assert isinstance(diagnostics[0].code, str)
        assert diagnostics[0].code.startswith("QE-")

    def test_valid_enum_values_no_error(self, provider: LintProvider) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n&ELECTRONS\nmixing_mode = 'plain'\n/\n"
        diagnostics = provider.lint(text)
        invalids = [d for d in diagnostics if d.code == RULE_INVALID_KEYWORD_VALUE]
        assert invalids == []


# ------------------------------------------------------------------
# snapshot (JSON serialisation)
# ------------------------------------------------------------------


class TestSnapshot:
    """Tests for LintProvider.snapshot."""

    def test_empty_snapshot(self, provider: LintProvider) -> None:
        assert provider.snapshot("") == []

    def test_valid_input_empty_snapshot(self, provider: LintProvider) -> None:
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

    def test_snapshot_is_json_serialisable(self, provider: LintProvider) -> None:
        text = "&FOOBAR\nx = 1\n/\n"
        items = provider.snapshot(text)
        serialised = json.dumps(items)
        assert isinstance(serialised, str)
        round_tripped = json.loads(serialised)
        assert round_tripped == items

    def test_snapshot_contains_required_keys(self, provider: LintProvider) -> None:
        text = "&FOOBAR\nx = 1\n/\n"
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

    def test_snapshot_severity_is_string(self, provider: LintProvider) -> None:
        text = "&FOOBAR\nx = 1\n/\n"
        items = provider.snapshot(text)
        error_items = [i for i in items if i["code"] == RULE_UNKNOWN_NAMELIST]
        assert len(error_items) >= 1
        assert error_items[0]["severity"] == "Error"

    def test_snapshot_code_is_string(self, provider: LintProvider) -> None:
        text = "&FOOBAR\nx = 1\n/\n"
        items = provider.snapshot(text)
        error_items = [i for i in items if i["code"] == RULE_UNKNOWN_NAMELIST]
        assert error_items[0]["code"].startswith("QE-")

    def test_snapshot_deterministic_ordering(self, provider: LintProvider) -> None:
        text = "&FOOBAR\nx = 1\n/\n&CONTROL\ncalculation = 'bogus'\n/\n"
        first = provider.snapshot(text)
        second = provider.snapshot(text)
        assert first == second

    def test_snapshot_warning_severity(self, provider: LintProvider) -> None:
        text = "orphan_param = 42\n&CONTROL\ncalculation = 'scf'\n/\n"
        items = provider.snapshot(text)
        orphan_items = [i for i in items if i["code"] == RULE_ORPHAN_PARAMETER]
        assert len(orphan_items) >= 1
        assert orphan_items[0]["severity"] == "Warning"


class TestOccupationsDegaussMismatch:
    """RULE qe.smearing.occupations_degauss_mismatch (QE-W012): warn when
    occupations='smearing' but degauss is missing or out of range."""

    def test_missing_degauss_triggers_warning(self, provider: LintProvider) -> None:
        text = (
            "&SYSTEM\n"
            "  occupations = 'smearing'\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_OCCUPATIONS_DEGAUSS_MISMATCH]
        assert len(warnings) == 1
        assert "degauss is not set" in warnings[0].message
        assert warnings[0].severity is not None
        assert warnings[0].severity.value == 2  # Warning

    def test_degauss_too_small_triggers_warning(self, provider: LintProvider) -> None:
        text = (
            "&SYSTEM\n"
            "  occupations = 'smearing'\n"
            "  degauss = 0.0001\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_OCCUPATIONS_DEGAUSS_MISMATCH]
        assert len(warnings) == 1
        assert "too small" in warnings[0].message

    def test_degauss_too_large_triggers_warning(self, provider: LintProvider) -> None:
        text = (
            "&SYSTEM\n"
            "  occupations = 'smearing'\n"
            "  degauss = 0.2\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_OCCUPATIONS_DEGAUSS_MISMATCH]
        assert len(warnings) == 1
        assert "too large" in warnings[0].message

    def test_valid_degauss_no_warning(self, provider: LintProvider) -> None:
        text = (
            "&SYSTEM\n"
            "  occupations = 'smearing'\n"
            "  degauss = 0.01\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_OCCUPATIONS_DEGAUSS_MISMATCH]
        assert warnings == []

    def test_degauss_at_lower_bound_no_warning(self, provider: LintProvider) -> None:
        """degauss = 0.001 exactly should NOT trigger the warning."""
        text = (
            "&SYSTEM\n"
            "  occupations = 'smearing'\n"
            "  degauss = 0.001\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_OCCUPATIONS_DEGAUSS_MISMATCH]
        assert warnings == []

    def test_degauss_at_upper_bound_no_warning(self, provider: LintProvider) -> None:
        """degauss = 0.1 exactly should NOT trigger the warning."""
        text = (
            "&SYSTEM\n"
            "  occupations = 'smearing'\n"
            "  degauss = 0.1\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_OCCUPATIONS_DEGAUSS_MISMATCH]
        assert warnings == []

    def test_fixed_occupations_no_warning(self, provider: LintProvider) -> None:
        """occupations = 'fixed' should not trigger degauss checks."""
        text = (
            "&SYSTEM\n"
            "  occupations = 'fixed'\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_OCCUPATIONS_DEGAUSS_MISMATCH]
        assert warnings == []

    def test_no_occupations_no_warning(self, provider: LintProvider) -> None:
        """No occupations keyword at all should not trigger the check."""
        text = (
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "/\n"
        )
        diagnostics = provider.lint(text)
        warnings = [d for d in diagnostics if d.code == RULE_OCCUPATIONS_DEGAUSS_MISMATCH]
        assert warnings == []

    def test_snapshot_includes_degauss_warning(self, provider: LintProvider) -> None:
        text = (
            "&SYSTEM\n"
            "  occupations = 'smearing'\n"
            "/\n"
        )
        items = provider.snapshot(text)
        degauss_items = [i for i in items if i["code"] == RULE_OCCUPATIONS_DEGAUSS_MISMATCH]
        assert len(degauss_items) == 1
        assert degauss_items[0]["severity"] == "Warning"

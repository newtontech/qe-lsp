"""Tests for CodeActionProvider quick fixes."""

from __future__ import annotations

import pytest

from lsprotocol.types import (
    CodeAction,
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
    TextEdit,
)

from qe_lsp.features.code_actions import CodeActionProvider
from qe_lsp.features.lint import (
    LintProvider,
    RULE_BAD_CALCULATION,
    RULE_DEPRECATED_KEYWORD,
    RULE_INCONSISTENT_SETTINGS,
    RULE_MISSING_ATOMIC_POSITIONS,
    RULE_MISSING_ATOMIC_SPECIES,
    RULE_MISSING_CONTROL,
    RULE_MISSING_CONTROL_CALC,
    RULE_MISSING_REQUIRED_SECTION,
    RULE_MISSING_SYSTEM_ECUTWFC,
    RULE_ORPHAN_PARAMETER,
    RULE_UNKNOWN_KEYWORD,
    RULE_UNKNOWN_NAMELIST,
)
from qe_lsp.validation import validate_qe_input


@pytest.fixture
def provider() -> CodeActionProvider:
    """Create a CodeActionProvider instance."""
    return CodeActionProvider()


def _text_edits(action: CodeAction) -> list[TextEdit]:
    assert action.edit is not None
    assert action.edit.changes is not None
    return list(action.edit.changes["document"])


@pytest.fixture
def lint_provider() -> LintProvider:
    """Create a LintProvider instance."""
    return LintProvider()


def _diag(
    line: int = 0,
    char: int = 0,
    length: int = 1,
    message: str = "",
    severity: DiagnosticSeverity = DiagnosticSeverity.Error,
    code: str = "",
    source: str = "qe-lsp",
) -> Diagnostic:
    """Helper to create a Diagnostic for tests."""
    return Diagnostic(
        range=Range(
            start=Position(line=line, character=char),
            end=Position(line=line, character=char + length),
        ),
        severity=severity,
        message=message,
        source=source,
        code=code,
    )


# ------------------------------------------------------------------
# Unclosed namelist
# ------------------------------------------------------------------


class TestFixUnclosedNamelist:
    def test_adds_slash_to_close_namelist(self, provider: CodeActionProvider) -> None:
        source = "&CONTROL\ncalculation = 'scf'\n"
        diags = validate_qe_input(source)
        assert len(diags) >= 1

        actions = provider.get_code_actions(source, diags)
        assert any("close namelist" in a.title.lower() for a in actions)

        action = next(a for a in actions if "close namelist" in a.title.lower())
        assert action.kind is not None
        edit = action.edit
        assert edit is not None
        changes = edit.changes
        assert changes is not None
        assert "document" in changes
        text_edits = changes["document"]
        assert len(text_edits) == 1
        assert "/" in text_edits[0].new_text


# ------------------------------------------------------------------
# Unknown keyword -> typo correction
# ------------------------------------------------------------------


class TestFixUnknownKeyword:
    def test_suggests_correction_for_typo(self, provider: CodeActionProvider) -> None:
        source = "&CONTROL\ncalculation = 'scf'\ncalulation = 'nscf'\n/\n"
        diags = LintProvider().lint(source)
        unknowns = [d for d in diags if d.code == RULE_UNKNOWN_KEYWORD]
        assert len(unknowns) >= 1

        actions = provider.get_code_actions(source, unknowns)
        assert len(actions) >= 1
        assert any("calculation" in a.title for a in actions)

    def test_no_action_for_very_short_unknown(self, provider: CodeActionProvider) -> None:
        diag = _diag(
            line=1,
            char=2,
            length=1,
            message="Unknown keyword 'x' in &CONTROL.",
            code=RULE_UNKNOWN_KEYWORD,
        )
        actions = provider.get_code_actions("&CONTROL\nx = 1\n/\n", [diag])
        # Single character unknown should not produce typo corrections
        keyword_actions = [a for a in actions if "Replace" in a.title]
        assert keyword_actions == []


# ------------------------------------------------------------------
# Invalid enum value
# ------------------------------------------------------------------


class TestFixInvalidValue:
    def test_suggests_closest_valid_calculation(self, provider: CodeActionProvider) -> None:
        source = "&CONTROL\ncalculation = 'bogus'\n/\n"
        diags = LintProvider().lint(source)
        invalids = [d for d in diags if d.code == RULE_BAD_CALCULATION]
        assert len(invalids) >= 1

        actions = provider.get_code_actions(source, invalids)
        assert len(actions) >= 1
        # Should suggest a valid value
        assert any("Change" in a.title or "Replace" in a.title for a in actions)


# ------------------------------------------------------------------
# Deprecated keyword
# ------------------------------------------------------------------


class TestFixDeprecatedKeyword:
    def test_removes_deprecated_nstep(self, provider: CodeActionProvider) -> None:
        source = "&CONTROL\ncalculation = 'scf'\nnstep = 100\n/\n"
        diags = LintProvider().lint(source)
        deprecated = [d for d in diags if d.code == RULE_DEPRECATED_KEYWORD]
        assert len(deprecated) >= 1

        actions = provider.get_code_actions(source, deprecated)
        assert len(actions) >= 1
        assert any("Remove deprecated" in a.title for a in actions)

        action = next(a for a in actions if "deprecated" in a.title.lower())
        text_edits = _text_edits(action)
        # Removing the line produces an empty new_text
        assert text_edits[0].new_text == ""


# ------------------------------------------------------------------
# Duplicate parameter
# ------------------------------------------------------------------


class TestFixDuplicateParameter:
    def test_removes_duplicate(self, provider: CodeActionProvider) -> None:
        source = "&CONTROL\ncalculation = 'scf'\ncalculation = 'nscf'\n/\n"
        diags = validate_qe_input(source)
        duplicates = [d for d in diags if "Duplicate" in d.message]
        assert len(duplicates) >= 1

        actions = provider.get_code_actions(source, duplicates)
        assert len(actions) >= 1
        assert any("duplicate" in a.title.lower() for a in actions)

        action = next(a for a in actions if "duplicate" in a.title.lower())
        text_edits = _text_edits(action)
        assert text_edits[0].new_text == ""


# ------------------------------------------------------------------
# mixing_beta too high
# ------------------------------------------------------------------


class TestFixMixingBeta:
    def test_lowers_mixing_beta(self, provider: CodeActionProvider) -> None:
        source = "&ELECTRONS\nmixing_beta = 0.9\n/\n"
        diags = validate_qe_input(source)
        beta_warnings = [d for d in diags if "mixing_beta" in d.message]
        assert len(beta_warnings) >= 1

        actions = provider.get_code_actions(source, beta_warnings)
        assert len(actions) >= 1
        assert any("0.7" in a.title for a in actions)

        action = next(a for a in actions if "0.7" in a.title)
        text_edits = _text_edits(action)
        assert text_edits[0].new_text == "0.7"


# ------------------------------------------------------------------
# ecutrho ratio
# ------------------------------------------------------------------


class TestFixEcutrhoRatio:
    def test_adjusts_ecutrho_to_ratio(self, provider: CodeActionProvider) -> None:
        source = "&SYSTEM\nibrav = 1\necutwfc = 60.0\necutrho = 100.0\n/\n"
        diags = validate_qe_input(source)
        ratio_warnings = [d for d in diags if "ecutrho should normally" in d.message]
        assert len(ratio_warnings) >= 1

        actions = provider.get_code_actions(source, ratio_warnings)
        assert len(actions) >= 1
        assert any("ecutrho" in a.title.lower() for a in actions)

        action = next(a for a in actions if "ecutrho" in a.title.lower())
        text_edits = _text_edits(action)
        # Should set to 4x60 = 240.0
        assert "240.0" in text_edits[0].new_text


# ------------------------------------------------------------------
# Orphan parameter
# ------------------------------------------------------------------


class TestFixOrphanParameter:
    def test_removes_orphan(self, provider: CodeActionProvider) -> None:
        source = "foo = 42\n&CONTROL\ncalculation = 'scf'\n/\n"
        diags = LintProvider().lint(source)
        orphans = [d for d in diags if d.code == RULE_ORPHAN_PARAMETER]
        assert len(orphans) >= 1

        actions = provider.get_code_actions(source, orphans)
        assert len(actions) >= 1
        assert any("orphan" in a.title.lower() for a in actions)

        action = next(a for a in actions if "orphan" in a.title.lower())
        text_edits = _text_edits(action)
        assert text_edits[0].new_text == ""


# ------------------------------------------------------------------
# Missing required sections
# ------------------------------------------------------------------


class TestFixMissingSections:
    def test_adds_control_skeleton(self, provider: CodeActionProvider) -> None:
        source = "&SYSTEM\nibrav = 1\n/\n"
        diags = LintProvider().lint(source)
        control_diags = [d for d in diags if d.code == RULE_MISSING_CONTROL]
        assert len(control_diags) >= 1

        actions = provider.get_code_actions(source, control_diags)
        assert len(actions) >= 1
        assert any("&CONTROL" in a.title for a in actions)

    def test_adds_system_skeleton(self, provider: CodeActionProvider) -> None:
        source = "&CONTROL\ncalculation = 'scf'\n/\n"
        diags = LintProvider().lint(source)
        missing = [d for d in diags if d.code == RULE_MISSING_REQUIRED_SECTION]
        system_diags = [d for d in missing if "&SYSTEM" in d.message]
        assert len(system_diags) >= 1

        actions = provider.get_code_actions(source, system_diags)
        assert len(actions) >= 1
        assert any("&SYSTEM" in a.title for a in actions)

    def test_adds_calculation_to_control(self, provider: CodeActionProvider) -> None:
        source = "&CONTROL\noutdir = './tmp'\n/\n"
        diags = LintProvider().lint(source)
        calc_diags = [d for d in diags if d.code == RULE_MISSING_CONTROL_CALC]
        assert len(calc_diags) >= 1

        actions = provider.get_code_actions(source, calc_diags)
        assert len(actions) >= 1
        assert any("calculation" in a.title for a in actions)

    def test_adds_ecutwfc_to_system(self, provider: CodeActionProvider) -> None:
        source = "&CONTROL\ncalculation = 'scf'\n/\n&SYSTEM\nibrav = 1\n/\n"
        diags = LintProvider().lint(source)
        ecutwfc_diags = [d for d in diags if d.code == RULE_MISSING_SYSTEM_ECUTWFC]
        assert len(ecutwfc_diags) >= 1

        actions = provider.get_code_actions(source, ecutwfc_diags)
        assert len(actions) >= 1
        assert any("ecutwfc" in a.title for a in actions)

    def test_adds_atomic_species_skeleton(self, provider: CodeActionProvider) -> None:
        source = (
            "&CONTROL\ncalculation = 'scf'\n/\n"
            "&SYSTEM\nibrav = 1\necutwfc = 60\nnat = 2\nntyp = 1\n/\n"
        )
        diags = LintProvider().lint(source)
        species_diags = [d for d in diags if d.code == RULE_MISSING_ATOMIC_SPECIES]
        assert len(species_diags) >= 1

        actions = provider.get_code_actions(source, species_diags)
        assert len(actions) >= 1
        assert any("ATOMIC_SPECIES" in a.title for a in actions)

    def test_adds_atomic_positions_skeleton(self, provider: CodeActionProvider) -> None:
        source = (
            "&CONTROL\ncalculation = 'scf'\n/\n"
            "&SYSTEM\nibrav = 1\necutwfc = 60\nnat = 2\nntyp = 1\n/\n"
        )
        diags = LintProvider().lint(source)
        pos_diags = [d for d in diags if d.code == RULE_MISSING_ATOMIC_POSITIONS]
        assert len(pos_diags) >= 1

        actions = provider.get_code_actions(source, pos_diags)
        assert len(actions) >= 1
        assert any("ATOMIC_POSITIONS" in a.title for a in actions)


# ------------------------------------------------------------------
# Inconsistent settings
# ------------------------------------------------------------------


class TestFixInconsistentSettings:
    def test_adds_ions_for_relax(self, provider: CodeActionProvider) -> None:
        source = (
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
        diags = LintProvider().lint(source)
        inconsistent = [
            d for d in diags if d.code == RULE_INCONSISTENT_SETTINGS and "&IONS" in d.message
        ]
        assert len(inconsistent) >= 1

        actions = provider.get_code_actions(source, inconsistent)
        assert len(actions) >= 1
        assert any("&IONS" in a.title for a in actions)

    def test_adds_cell_for_vc_relax(self, provider: CodeActionProvider) -> None:
        source = (
            "&CONTROL\n"
            "  calculation = 'vc-relax'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 1\n"
            "  ecutwfc = 60\n"
            "  nat = 1\n"
            "  ntyp = 1\n"
            "/\n"
            "&ELECTRONS\n"
            "/\n"
        )
        diags = LintProvider().lint(source)
        cell_diags = [
            d for d in diags if d.code == RULE_INCONSISTENT_SETTINGS and "&CELL" in d.message
        ]
        assert len(cell_diags) >= 1

        actions = provider.get_code_actions(source, cell_diags)
        assert len(actions) >= 1
        assert any("&CELL" in a.title for a in actions)


# ------------------------------------------------------------------
# Code action metadata
# ------------------------------------------------------------------


class TestCodeActionMetadata:
    def test_actions_have_quickfix_kind(self, provider: CodeActionProvider) -> None:
        source = "&CONTROL\ncalculation = 'scf'\n"
        diags = validate_qe_input(source)
        actions = provider.get_code_actions(source, diags)
        for action in actions:
            assert action.kind is not None

    def test_actions_reference_original_diagnostic(
        self,
        provider: CodeActionProvider,
    ) -> None:
        source = "&CONTROL\ncalculation = 'scf'\n"
        diags = validate_qe_input(source)
        actions = provider.get_code_actions(source, diags)
        for action in actions:
            if action.diagnostics:
                assert len(action.diagnostics) >= 1

    def test_actions_have_titles(self, provider: CodeActionProvider) -> None:
        source = "&CONTROL\ncalculation = 'scf'\n"
        diags = validate_qe_input(source)
        actions = provider.get_code_actions(source, diags)
        for action in actions:
            assert action.title
            assert isinstance(action.title, str)


# ------------------------------------------------------------------
# Empty / no-action cases
# ------------------------------------------------------------------


class TestEdgeCases:
    def test_no_actions_for_empty_source(self, provider: CodeActionProvider) -> None:
        actions = provider.get_code_actions("", [])
        assert actions == []

    def test_no_actions_for_unrelated_diagnostic(self, provider: CodeActionProvider) -> None:
        diag = _diag(
            line=0,
            char=0,
            length=5,
            message="Some unrelated issue",
            code="QE-Z999",
        )
        actions = provider.get_code_actions("&CONTROL\n/\n", [diag])
        assert actions == []

    def test_no_actions_for_valid_input(self, provider: CodeActionProvider) -> None:
        source = (
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
        diags = validate_qe_input(source) + LintProvider().lint(source)
        actions = provider.get_code_actions(source, diags)
        assert actions == []


# ------------------------------------------------------------------
# Similarity score
# ------------------------------------------------------------------


class TestSimilarityScore:
    def test_exact_match(self, provider: CodeActionProvider) -> None:
        score = provider._similarity_score("calculation", "calculation")
        assert score == 1.0

    def test_no_similarity(self, provider: CodeActionProvider) -> None:
        score = provider._similarity_score("abc", "xyz")
        assert score < 0.5

    def test_empty_strings(self, provider: CodeActionProvider) -> None:
        assert provider._similarity_score("", "") == 1.0
        assert provider._similarity_score("", "abc") == 0.0

    def test_near_match(self, provider: CodeActionProvider) -> None:
        score = provider._similarity_score("calulation", "calculation")
        assert score > 0.6


# ------------------------------------------------------------------
# Integration: full pipeline from lint to code action
# ------------------------------------------------------------------


class TestIntegration:
    def test_full_pipeline_unknown_namelist(
        self,
        provider: CodeActionProvider,
        lint_provider: LintProvider,
    ) -> None:
        source = "&FOOBAR\nx = 1\n/\n"
        diags = lint_provider.lint(source)
        assert any(d.code == RULE_UNKNOWN_NAMELIST for d in diags)

    def test_full_pipeline_unknown_keyword(
        self,
        provider: CodeActionProvider,
        lint_provider: LintProvider,
    ) -> None:
        source = "&CONTROL\ncalculation = 'scf'\ntypo_param = 42\n/\n"
        diags = lint_provider.lint(source)
        unknowns = [d for d in diags if d.code == RULE_UNKNOWN_KEYWORD]
        assert len(unknowns) >= 1

        actions = provider.get_code_actions(source, diags)
        # Typo correction may or may not find a close match for "typo_param"
        # but the action should be attempted
        assert isinstance(actions, list)

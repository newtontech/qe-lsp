"""Tests using real-world QE .in example fixtures.

Validates parse/diagnostic stability, completion, hover, formatting,
navigation, rename, and code actions against representative QE inputs
covering all calculation types and common invalid patterns.
"""

from pathlib import Path

import pytest

from qe_lsp.parser import parse_qe_input, declared_species
from qe_lsp.validation import validate_qe_input
from qe_lsp.features.diagnostic import DiagnosticProvider
from qe_lsp.features.lint import LintProvider
from qe_lsp.features.typecheck import TypecheckProvider
from qe_lsp.features.formatting import FormattingProvider
from qe_lsp.features.code_actions import CodeActionProvider
from qe_lsp.features.navigation import (
    build_symbol_index,
    get_hover,
    get_definition,
    get_references,
    get_document_symbols,
)

try:
    from pygls.lsp.server import LanguageServer as PyglsLanguageServer
except ImportError:
    from pygls.server import LanguageServer as PyglsLanguageServer  # type: ignore[attr-defined,no-redef]

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_fixture(name: str) -> str:
    path = FIXTURES_DIR / name
    assert path.exists(), f"Fixture {name} not found at {path}"
    return path.read_text()


def _make_server():
    return PyglsLanguageServer("test-qe-lsp", "0.1.0")


# ---------------------------------------------------------------------------
# Fixture parametrisation
# ---------------------------------------------------------------------------

VALID_FIXTURES = [
    "silicon_scf.in",
    "aluminum_relax.in",
    "sio2_vc_relax.in",
    "silicon_bands.in",
    "fe_spin.in",
]


@pytest.fixture(params=VALID_FIXTURES, ids=VALID_FIXTURES)
def valid_fixture(request) -> str:
    return _read_fixture(request.param)


# ===================================================================
# 1. Parse stability
# ===================================================================


class TestParseStability:
    """Parsing valid .in files should succeed without errors."""

    @pytest.mark.parametrize("fixture_name", VALID_FIXTURES, ids=VALID_FIXTURES)
    def test_parse_does_not_raise(self, fixture_name: str) -> None:
        text = _read_fixture(fixture_name)
        parsed = parse_qe_input(text)
        assert parsed is not None
        assert isinstance(parsed.namelists, dict)
        assert isinstance(parsed.cards, dict)
        # No unclosed namelists in valid fixtures
        assert parsed.unclosed_namelist is None

    @pytest.mark.parametrize("fixture_name", VALID_FIXTURES, ids=VALID_FIXTURES)
    def test_parse_roundtrip_stability(self, fixture_name: str) -> None:
        """Parsing twice must produce identical results."""
        text = _read_fixture(fixture_name)
        first = parse_qe_input(text)
        second = parse_qe_input(text)
        assert set(first.namelists.keys()) == set(second.namelists.keys())
        assert set(first.cards.keys()) == set(second.cards.keys())
        assert set(first.namelist_lines.keys()) == set(second.namelist_lines.keys())

    def test_silicon_scf_has_expected_structure(self) -> None:
        text = _read_fixture("silicon_scf.in")
        parsed = parse_qe_input(text)
        assert "&CONTROL" in parsed.namelists
        assert "&SYSTEM" in parsed.namelists
        assert "&ELECTRONS" in parsed.namelists
        assert "ATOMIC_SPECIES" in parsed.cards
        assert "ATOMIC_POSITIONS" in parsed.cards
        assert "K_POINTS" in parsed.cards

    def test_aluminum_relax_has_ions(self) -> None:
        text = _read_fixture("aluminum_relax.in")
        parsed = parse_qe_input(text)
        assert "&IONS" in parsed.namelists
        ions = parsed.namelists["&IONS"]
        assert "ion_dynamics" in ions

    def test_sio2_vc_relax_has_cell(self) -> None:
        text = _read_fixture("sio2_vc_relax.in")
        parsed = parse_qe_input(text)
        assert "&CELL" in parsed.namelists
        assert "CELL_PARAMETERS" in parsed.cards

    def test_bands_has_kpoints_tpiba(self) -> None:
        text = _read_fixture("silicon_bands.in")
        parsed = parse_qe_input(text)
        assert "K_POINTS" in parsed.cards
        assert "nbnd" in parsed.namelists.get("&SYSTEM", {})

    def test_fe_spin_has_nspin(self) -> None:
        text = _read_fixture("fe_spin.in")
        parsed = parse_qe_input(text)
        system = parsed.namelists.get("&SYSTEM", {})
        assert "nspin" in system
        assert "starting_magnetization(1)" in system

    def test_declared_species_silicon(self) -> None:
        text = _read_fixture("silicon_scf.in")
        parsed = parse_qe_input(text)
        assert declared_species(parsed) == {"Si"}

    def test_declared_species_sio2(self) -> None:
        text = _read_fixture("sio2_vc_relax.in")
        parsed = parse_qe_input(text)
        assert declared_species(parsed) == {"Si", "O"}


# ===================================================================
# 2. Diagnostic stability — valid fixtures should have zero errors
# ===================================================================


class TestDiagnosticStability:
    """Valid QE .in files should produce minimal diagnostics."""

    @pytest.mark.parametrize("fixture_name", VALID_FIXTURES, ids=VALID_FIXTURES)
    def test_validation_no_errors(self, fixture_name: str) -> None:
        text = _read_fixture(fixture_name)
        diagnostics = validate_qe_input(text)
        errors = [d for d in diagnostics if d.severity is not None and d.severity.value == 1]
        assert errors == [], f"Unexpected errors in {fixture_name}: {[d.message for d in errors]}"

    @pytest.mark.parametrize("fixture_name", VALID_FIXTURES, ids=VALID_FIXTURES)
    def test_lint_no_errors(self, fixture_name: str) -> None:
        text = _read_fixture(fixture_name)
        lint = LintProvider()
        diagnostics = lint.lint(text)
        errors = [d for d in diagnostics if d.severity is not None and d.severity.value == 1]
        assert (
            errors == []
        ), f"Unexpected lint errors in {fixture_name}: {[d.message for d in errors]}"

    @pytest.mark.parametrize("fixture_name", VALID_FIXTURES, ids=VALID_FIXTURES)
    def test_typecheck_no_errors(self, fixture_name: str) -> None:
        text = _read_fixture(fixture_name)
        tc = TypecheckProvider()
        diagnostics = tc.typecheck(text)
        errors = [d for d in diagnostics if d.severity is not None and d.severity.value == 1]
        assert (
            errors == []
        ), f"Unexpected typecheck errors in {fixture_name}: {[d.message for d in errors]}"

    def test_diagnostic_snapshot_deterministic(self) -> None:
        """Two diagnostic runs must produce identical results."""
        text = _read_fixture("silicon_scf.in")
        server = _make_server()
        provider = DiagnosticProvider(server)
        snap1 = provider.snapshot(text)
        snap2 = provider.snapshot(text)
        assert snap1 == snap2

    def test_lint_snapshot_deterministic(self) -> None:
        text = _read_fixture("silicon_scf.in")
        lint = LintProvider()
        snap1 = lint.snapshot(text)
        snap2 = lint.snapshot(text)
        assert snap1 == snap2


# ===================================================================
# 3. Formatting stability
# ===================================================================


class TestFormattingStability:
    """Formatting valid fixtures must be idempotent."""

    @pytest.mark.parametrize("fixture_name", VALID_FIXTURES, ids=VALID_FIXTURES)
    def test_format_idempotent(self, fixture_name: str) -> None:
        from lsprotocol.types import (
            DocumentFormattingParams,
            FormattingOptions,
            TextDocumentIdentifier,
        )

        text = _read_fixture(fixture_name)
        server = _make_server()
        fmt = FormattingProvider(server)
        params = DocumentFormattingParams(
            text_document=TextDocumentIdentifier(uri=f"file:///{fixture_name}"),
            options=FormattingOptions(tab_size=2, insert_spaces=True),
        )
        # First format
        edits1 = fmt.format_document(text, params)
        if not edits1:
            # Already formatted
            return
        formatted = edits1[0].new_text
        # Second format must produce no edits
        edits2 = fmt.format_document(formatted, params)
        assert edits2 == [], f"Formatting not idempotent for {fixture_name}"

    @pytest.mark.parametrize("fixture_name", VALID_FIXTURES, ids=VALID_FIXTURES)
    def test_format_preserves_comments(self, fixture_name: str) -> None:
        from lsprotocol.types import (
            DocumentFormattingParams,
            FormattingOptions,
            TextDocumentIdentifier,
        )

        text = _read_fixture(fixture_name)
        server = _make_server()
        fmt = FormattingProvider(server)
        params = DocumentFormattingParams(
            text_document=TextDocumentIdentifier(uri=f"file:///{fixture_name}"),
            options=FormattingOptions(tab_size=2, insert_spaces=True),
        )
        edits = fmt.format_document(text, params)
        formatted = edits[0].new_text if edits else text
        # Comments (lines starting with !) should be preserved
        for original_line in text.splitlines():
            stripped = original_line.strip()
            if stripped.startswith("!"):
                assert stripped in formatted, f"Comment lost: {stripped}"


# ===================================================================
# 4. Navigation on real fixtures
# ===================================================================


class TestNavigationOnFixtures:
    """Symbol index, hover, definition, references on real .in files."""

    def test_symbol_index_silicon_scf(self) -> None:
        text = _read_fixture("silicon_scf.in")
        index = build_symbol_index(text)
        assert index.lookup("&CONTROL")
        assert index.lookup("&SYSTEM")
        assert index.lookup("&ELECTRONS")
        assert index.lookup("ecutwfc")
        assert index.lookup("ATOMIC_SPECIES")
        assert index.lookup("ATOMIC_POSITIONS")
        assert index.lookup("K_POINTS")

    def test_hover_on_all_namelists(self) -> None:
        text = _read_fixture("silicon_scf.in")
        for nl in ["&CONTROL", "&SYSTEM", "&ELECTRONS"]:
            index = build_symbol_index(text)
            syms = index.lookup(nl)
            assert syms, f"Missing symbol for {nl}"
            result = get_hover(text, syms[0].line, syms[0].character)
            assert result is not None, f"No hover for {nl}"

    def test_hover_on_keywords(self) -> None:
        text = _read_fixture("silicon_scf.in")
        for kw in ["calculation", "ecutwfc", "mixing_beta", "conv_thr"]:
            index = build_symbol_index(text)
            syms = index.lookup(kw)
            assert syms, f"Missing symbol for {kw}"
            result = get_hover(text, syms[0].line, syms[0].character)
            assert result is not None, f"No hover for {kw}"

    def test_definition_on_all_cards(self) -> None:
        text = _read_fixture("silicon_scf.in")
        for card in ["ATOMIC_SPECIES", "ATOMIC_POSITIONS", "K_POINTS"]:
            index = build_symbol_index(text)
            syms = index.lookup(card)
            assert syms, f"Missing symbol for {card}"
            result = get_definition(text, syms[0].line, syms[0].character, "file:///test.in")
            assert result is not None, f"No definition for {card}"

    def test_references_for_ecutwfc(self) -> None:
        text = _read_fixture("silicon_scf.in")
        index = build_symbol_index(text)
        syms = index.lookup("ecutwfc")
        assert len(syms) >= 1
        refs = get_references(text, syms[0].line, syms[0].character, "file:///test.in")
        assert len(refs) >= 1

    def test_document_symbols_multi_namelist(self) -> None:
        text = _read_fixture("sio2_vc_relax.in")
        symbols = get_document_symbols(text)
        names = [s.name for s in symbols]
        assert "&CONTROL" in names
        assert "&SYSTEM" in names
        assert "&IONS" in names
        assert "&CELL" in names
        assert "ATOMIC_SPECIES" in names
        assert "ATOMIC_POSITIONS" in names
        assert "CELL_PARAMETERS" in names

    def test_symbol_index_bands(self) -> None:
        text = _read_fixture("silicon_bands.in")
        index = build_symbol_index(text)
        assert index.lookup("nbnd")
        assert index.lookup("K_POINTS")


# ===================================================================
# 5. Common invalid cases
# ===================================================================


class TestCommonInvalidCases:
    """Tests for typical user errors in QE inputs."""

    def _all_diagnostics(self, text: str) -> list:
        """Collect diagnostics from all providers."""
        diags = validate_qe_input(text)
        diags.extend(LintProvider().lint(text))
        diags.extend(TypecheckProvider().typecheck(text))
        return diags

    # --- Namelist errors ---

    def test_unclosed_control(self) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n"
        diags = self._all_diagnostics(text)
        assert any("Unclosed" in d.message for d in diags)

    def test_unclosed_system(self) -> None:
        text = "&SYSTEM\nibrav = 1\necutwfc = 60\n"
        diags = self._all_diagnostics(text)
        assert any("Unclosed" in d.message for d in diags)

    def test_unknown_namelist(self) -> None:
        text = "&PHONON\nfildyn = 'dyn'\n/\n"
        diags = self._all_diagnostics(text)
        assert any("Unknown namelist" in d.message for d in diags)

    def test_lowercase_namelist_is_accepted(self) -> None:
        """QE namelists are case-insensitive; &control is treated as &CONTROL."""
        text = "&control\ncalculation = 'scf'\n/\n"
        diags = LintProvider().lint(text)
        # No unknown namelist errors; the parser normalises to uppercase
        unknown = [d for d in diags if "Unknown namelist" in d.message]
        assert unknown == []

    # --- Parameter errors ---

    def test_duplicate_calculation(self) -> None:
        text = "&CONTROL\ncalculation = 'scf'\ncalculation = 'relax'\n/\n"
        diags = validate_qe_input(text)
        assert any("Duplicate parameter" in d.message for d in diags)

    def test_invalid_calculation_value(self) -> None:
        text = "&CONTROL\ncalculation = 'optimize'\n/\n"
        diags = LintProvider().lint(text)
        assert any("Invalid value" in d.message and "calculation" in d.message for d in diags)

    def test_unknown_keyword_in_control(self) -> None:
        text = "&CONTROL\ncalculation = 'scf'\nbad_keyword = 42\n/\n"
        diags = LintProvider().lint(text)
        assert any("Unknown keyword" in d.message for d in diags)

    def test_wrong_type_boolean(self) -> None:
        text = "&CONTROL\ncalculation = 'scf'\ntstress = yes\n/\n"
        diags = TypecheckProvider().typecheck(text)
        assert any("boolean" in d.message.lower() for d in diags)

    def test_wrong_type_integer(self) -> None:
        text = "&SYSTEM\nibrav = 'fcc'\n/\n"
        diags = TypecheckProvider().typecheck(text)
        assert any("integer" in d.message.lower() for d in diags)

    def test_wrong_type_float(self) -> None:
        text = "&SYSTEM\necutwfc = 'high'\n/\n"
        diags = TypecheckProvider().typecheck(text)
        assert any("numeric" in d.message.lower() for d in diags)

    def test_ibrav_out_of_range(self) -> None:
        text = "&SYSTEM\nibrav = 15\n/\n"
        diags = TypecheckProvider().typecheck(text)
        assert any("exceeds maximum" in d.message for d in diags)

    def test_ibrav_negative(self) -> None:
        text = "&SYSTEM\nibrav = -2\n/\n"
        diags = TypecheckProvider().typecheck(text)
        assert any("below minimum" in d.message for d in diags)

    # --- Structural errors ---

    def test_ibrav_zero_no_cell_parameters(self) -> None:
        text = (
            "&CONTROL\ncalculation = 'scf'\n/\n"
            "&SYSTEM\nibrav = 0\nnat = 1\nntyp = 1\necutwfc = 60\n/\n"
        )
        diags = self._all_diagnostics(text)
        assert any("CELL_PARAMETERS" in d.message for d in diags)

    def test_vc_relax_no_cell_namelist(self) -> None:
        text = (
            "&CONTROL\ncalculation = 'vc-relax'\n/\n"
            "&SYSTEM\nibrav = 1\necutwfc = 60\nnat = 1\nntyp = 1\n/\n"
            "&ELECTRONS\n/\n"
        )
        diags = self._all_diagnostics(text)
        assert any("&CELL" in d.message for d in diags)

    def test_relax_no_ions(self) -> None:
        text = (
            "&CONTROL\ncalculation = 'relax'\n/\n"
            "&SYSTEM\nibrav = 1\necutwfc = 60\nnat = 1\nntyp = 1\n/\n"
        )
        diags = LintProvider().lint(text)
        assert any("&IONS" in d.message for d in diags)

    def test_missing_ecutwfc_without_nat(self) -> None:
        """When both ecutwfc and nat are missing from &SYSTEM, report ecutwfc."""
        text = "&CONTROL\ncalculation = 'scf'\n/\n" "&SYSTEM\nibrav = 1\n/\n"
        diags = LintProvider().lint(text)
        assert any("ecutwfc" in d.message for d in diags)

    def test_nat_without_atomic_species(self) -> None:
        text = (
            "&CONTROL\ncalculation = 'scf'\n/\n"
            "&SYSTEM\nibrav = 1\necutwfc = 60\nnat = 2\nntyp = 1\n/\n"
        )
        diags = LintProvider().lint(text)
        assert any("ATOMIC_SPECIES" in d.message for d in diags)

    def test_nat_without_atomic_positions(self) -> None:
        text = (
            "&CONTROL\ncalculation = 'scf'\n/\n"
            "&SYSTEM\nibrav = 1\necutwfc = 60\nnat = 2\nntyp = 1\n/\n"
        )
        diags = LintProvider().lint(text)
        assert any("ATOMIC_POSITIONS" in d.message for d in diags)

    # --- Pseudopotential errors ---

    def test_pseudo_element_mismatch(self) -> None:
        text = "ATOMIC_SPECIES\nO 15.999 Si.pbe.UPF\n"
        diags = validate_qe_input(text)
        assert any("does not appear to match" in d.message for d in diags)

    def test_mixed_functional_families(self) -> None:
        text = "ATOMIC_SPECIES\nSi 28.086 Si.pbe.UPF\nO 15.999 O.lda.UPF\n"
        diags = validate_qe_input(text)
        assert any("Mixed pseudopotential" in d.message for d in diags)

    # --- Atomic positions errors ---

    def test_atom_not_in_species(self) -> None:
        text = (
            "ATOMIC_SPECIES\nSi 28.086 Si.pbe.UPF\n" "ATOMIC_POSITIONS {crystal}\nO 0.0 0.0 0.0\n"
        )
        diags = validate_qe_input(text)
        assert any("missing from ATOMIC_SPECIES" in d.message for d in diags)

    def test_crystal_coords_out_of_bounds(self) -> None:
        text = (
            "ATOMIC_SPECIES\nSi 28.086 Si.pbe.UPF\n" "ATOMIC_POSITIONS {crystal}\nSi 1.5 0.0 0.0\n"
        )
        diags = validate_qe_input(text)
        assert any("between 0 and 1" in d.message for d in diags)

    # --- K_POINTS errors ---

    def test_gamma_with_offset(self) -> None:
        text = "K_POINTS {gamma}\n4 4 4 0 0 1\n"
        diags = validate_qe_input(text)
        assert any("non-zero offset" in d.message for d in diags)

    def test_coarse_k_grid(self) -> None:
        text = "K_POINTS {automatic}\n2 2 2 0 0 0\n"
        diags = validate_qe_input(text)
        assert any("very coarse" in d.message for d in diags)

    # --- Ecutrho/ecnutwfc ratio ---

    def test_ecutrho_too_low(self) -> None:
        text = "&SYSTEM\necutwfc = 60\necutrho = 120\n/\n"
        diags = validate_qe_input(text)
        assert any("at least 4x ecutwfc" in d.message for d in diags)

    def test_ecutrho_too_low_paw(self) -> None:
        text = "&SYSTEM\necutwfc = 60\necutrho = 300\n/\n" "ATOMIC_SPECIES\nO 15.999 O.paw.UPF\n"
        diags = validate_qe_input(text)
        assert any("at least 8x ecutwfc" in d.message for d in diags)

    def test_ecutrho_ok(self) -> None:
        text = "&SYSTEM\necutwfc = 60\necutrho = 240\n/\n"
        diags = validate_qe_input(text)
        ratio_warnings = [d for d in diags if "ecutrho should normally" in d.message]
        assert ratio_warnings == []

    # --- Mixing beta ---

    def test_high_mixing_beta(self) -> None:
        text = "&ELECTRONS\nmixing_beta = 0.9\n/\n"
        diags = validate_qe_input(text)
        assert any("mixing_beta above 0.7" in d.message for d in diags)

    def test_ok_mixing_beta(self) -> None:
        text = "&ELECTRONS\nmixing_beta = 0.5\n/\n"
        diags = validate_qe_input(text)
        beta_warnings = [d for d in diags if "mixing_beta" in d.message]
        assert beta_warnings == []

    # --- Orphan parameters ---

    def test_orphan_parameter_before_namelist(self) -> None:
        text = "foo = 42\n&CONTROL\ncalculation = 'scf'\n/\n"
        diags = LintProvider().lint(text)
        assert any("outside any namelist" in d.message for d in diags)

    def test_orphan_parameter_after_namelist(self) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\nbar = 99\n"
        diags = LintProvider().lint(text)
        assert any("outside any namelist" in d.message for d in diags)

    # --- nspin without magnetization ---

    def test_nspin_without_magnetization(self) -> None:
        text = (
            "&CONTROL\ncalculation = 'scf'\n/\n" "&SYSTEM\nibrav = 1\nnspin = 2\necutwfc = 60\n/\n"
        )
        diags = LintProvider().lint(text)
        assert any("nspin > 1" in d.message for d in diags)

    # --- Deprecated keywords ---

    def test_deprecated_nstep(self) -> None:
        text = "&CONTROL\ncalculation = 'scf'\nnstep = 100\n/\n"
        diags = LintProvider().lint(text)
        assert any("Deprecated" in d.message and "nstep" in d.message for d in diags)


# ===================================================================
# 6. Code actions on real fixtures (invalid cases)
# ===================================================================


class TestCodeActionsOnInvalid:
    """Code actions should provide quick fixes for common errors."""

    def test_fix_unclosed_namelist(self) -> None:
        source = "&CONTROL\ncalculation = 'scf'\n"
        diags = validate_qe_input(source)
        provider = CodeActionProvider()
        actions = provider.get_code_actions(source, diags)
        assert any("close namelist" in a.title.lower() for a in actions)

    def test_fix_unknown_keyword_typo(self) -> None:
        source = "&CONTROL\ncalculation = 'scf'\ncalulation = 'nscf'\n/\n"
        diags = LintProvider().lint(source)
        unknowns = [d for d in diags if "Unknown keyword" in d.message]
        provider = CodeActionProvider()
        actions = provider.get_code_actions(source, unknowns)
        assert any("calculation" in a.title for a in actions)

    def test_fix_invalid_calculation_value(self) -> None:
        source = "&CONTROL\ncalculation = 'bogus'\n/\n"
        diags = LintProvider().lint(source)
        invalids = [d for d in diags if "Invalid value" in d.message]
        provider = CodeActionProvider()
        actions = provider.get_code_actions(source, invalids)
        assert len(actions) >= 1

    def test_fix_deprecated_keyword(self) -> None:
        source = "&CONTROL\ncalculation = 'scf'\nnstep = 100\n/\n"
        diags = LintProvider().lint(source)
        deprecated = [d for d in diags if "Deprecated" in d.message]
        provider = CodeActionProvider()
        actions = provider.get_code_actions(source, deprecated)
        assert any("Remove deprecated" in a.title for a in actions)

    def test_fix_duplicate_parameter(self) -> None:
        source = "&CONTROL\ncalculation = 'scf'\ncalculation = 'nscf'\n/\n"
        diags = validate_qe_input(source)
        duplicates = [d for d in diags if "Duplicate" in d.message]
        provider = CodeActionProvider()
        actions = provider.get_code_actions(source, duplicates)
        assert any("duplicate" in a.title.lower() for a in actions)

    def test_fix_missing_control_calculation(self) -> None:
        source = "&CONTROL\noutdir = './tmp'\n/\n"
        diags = LintProvider().lint(source)
        calc_diags = [d for d in diags if "calculation" in d.message and "Missing" in d.message]
        provider = CodeActionProvider()
        actions = provider.get_code_actions(source, calc_diags)
        assert any("calculation" in a.title for a in actions)

    def test_fix_missing_system_ecutwfc(self) -> None:
        source = "&CONTROL\ncalculation = 'scf'\n/\n&SYSTEM\nibrav = 1\n/\n"
        diags = LintProvider().lint(source)
        ecutwfc_diags = [d for d in diags if "ecutwfc" in d.message]
        provider = CodeActionProvider()
        actions = provider.get_code_actions(source, ecutwfc_diags)
        assert any("ecutwfc" in a.title for a in actions)

    def test_no_actions_for_valid_input(self) -> None:
        text = _read_fixture("silicon_scf.in")
        diags = (
            validate_qe_input(text)
            + LintProvider().lint(text)
            + TypecheckProvider().typecheck(text)
        )
        provider = CodeActionProvider()
        actions = provider.get_code_actions(text, diags)
        assert actions == []


# ===================================================================
# 7. Completion on fixtures
# ===================================================================


class TestCompletionOnFixtures:
    """Verify completion returns QE keywords."""

    def test_completion_returns_all_keywords(self) -> None:
        from qe_lsp.handlers.completion import completion
        from qe_lsp.constants import QE_KEYWORDS

        items = completion(None)
        labels = {item.label for item in items}
        for kw in QE_KEYWORDS:
            assert kw in labels, f"Missing completion: {kw}"

    def test_completion_items_are_keywords(self) -> None:
        from lsprotocol import types as lsp_types
        from qe_lsp.handlers.completion import completion

        items = completion(None)
        for item in items:
            assert item.kind == lsp_types.CompletionItemKind.Keyword


# ===================================================================
# 8. Full pipeline integration on each fixture
# ===================================================================


class TestFullPipeline:
    """End-to-end pipeline: parse → diagnostics → lint → typecheck → format → nav."""

    @pytest.mark.parametrize("fixture_name", VALID_FIXTURES, ids=VALID_FIXTURES)
    def test_full_pipeline(self, fixture_name: str) -> None:
        """Run all providers on each fixture without errors."""
        text = _read_fixture(fixture_name)

        # Parse
        parsed = parse_qe_input(text)
        assert parsed is not None

        # Validation
        validate_qe_input(text)

        # Lint
        LintProvider().lint(text)

        # Typecheck
        TypecheckProvider().typecheck(text)

        # Formatting
        from lsprotocol.types import (
            DocumentFormattingParams,
            FormattingOptions,
            TextDocumentIdentifier,
        )

        server = _make_server()
        fmt = FormattingProvider(server)
        params = DocumentFormattingParams(
            text_document=TextDocumentIdentifier(uri=f"file:///{fixture_name}"),
            options=FormattingOptions(tab_size=2, insert_spaces=True),
        )
        fmt.format_document(text, params)

        # Navigation
        index = build_symbol_index(text)
        for nl in parsed.namelists:
            syms = index.lookup(nl)
            if syms:
                get_hover(text, syms[0].line, syms[0].character)
                get_definition(text, syms[0].line, syms[0].character, "file:///test.in")
                get_references(text, syms[0].line, syms[0].character, "file:///test.in")

        get_document_symbols(text)

        # Code actions
        diags = (
            validate_qe_input(text)
            + LintProvider().lint(text)
            + TypecheckProvider().typecheck(text)
        )
        CodeActionProvider().get_code_actions(text, diags)

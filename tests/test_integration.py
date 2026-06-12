"""Integration tests covering server lifecycle, regression harness,
and edge cases that cross provider boundaries.
"""

import json
from pathlib import Path

import pytest

try:
    from pygls.lsp.server import LanguageServer as PyglsLanguageServer
except ImportError:
    from pygls.server import LanguageServer as PyglsLanguageServer  # type: ignore[attr-defined,no-redef]

from qe_lsp.parser import parse_qe_input, declared_species, normalize_value, parse_number
from qe_lsp.text import strip_inline_comment, word_at_position
from qe_lsp.validation import validate_qe_input
from qe_lsp.features.diagnostic import DiagnosticProvider
from qe_lsp.features.lint import LintProvider
from qe_lsp.features.typecheck import TypecheckProvider
from qe_lsp.features.regression import RegressionHarness, GoldenFixture
from qe_lsp.features.test_runner import TestRunnerProvider, TestRunnerConfig, parse_solver_output
from qe_lsp.features.agent_api import AgentAPIProvider
from tests.lsp_compat import get_registered_features

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text()


def _make_server():
    return PyglsLanguageServer("test-qe-lsp", "0.1.0")


# ===================================================================
# Parser edge cases
# ===================================================================


class TestParserEdgeCases:
    """Parser robustness for unusual but valid inputs."""

    def test_fortran_d_notation(self) -> None:
        """Fortran double-precision notation (1.0d-8) should be parseable."""
        val = parse_number("1.0d-8")
        assert val is not None
        assert abs(val - 1.0e-8) < 1e-15

    def test_fortran_e_notation(self) -> None:
        val = parse_number("1.0e-8")
        assert val is not None
        assert abs(val - 1.0e-8) < 1e-15

    def test_integer_value(self) -> None:
        val = parse_number("42")
        assert val == 42.0

    def test_normalize_value_strips_quotes(self) -> None:
        assert normalize_value("'scf'") == "scf"
        assert normalize_value('"scf"') == "scf"

    def test_normalize_value_lowercases(self) -> None:
        assert normalize_value("SCF") == "scf"

    def test_empty_input(self) -> None:
        parsed = parse_qe_input("")
        assert parsed.namelists == {}
        assert parsed.cards == {}
        assert parsed.unclosed_namelist is None
        assert parsed.duplicate_parameters == []

    def test_comment_only_input(self) -> None:
        parsed = parse_qe_input("! Just a comment\n! Another line\n")
        assert parsed.namelists == {}
        assert parsed.cards == {}

    def test_inline_comments_stripped(self) -> None:
        text = "&CONTROL\ncalculation = 'scf' ! self-consistent\n/\n"
        parsed = parse_qe_input(text)
        assert "calculation" in parsed.namelists.get("&CONTROL", {})

    def test_empty_namelist(self) -> None:
        text = "&CONTROL\n/\n"
        parsed = parse_qe_input(text)
        assert "&CONTROL" in parsed.namelists
        assert parsed.namelists["&CONTROL"] == {}

    def test_multiple_namelists(self) -> None:
        text = "&CONTROL\ncalculation = 'scf'\n/\n&SYSTEM\nibrav = 1\n/\n"
        parsed = parse_qe_input(text)
        assert "&CONTROL" in parsed.namelists
        assert "&SYSTEM" in parsed.namelists

    def test_all_five_namelists(self) -> None:
        text = (
            "&CONTROL\ncalculation = 'vc-relax'\n/\n"
            "&SYSTEM\nibrav = 1\necutwfc = 60\nnat = 1\nntyp = 1\n/\n"
            "&ELECTRONS\n/\n"
            "&IONS\nion_dynamics = 'bfgs'\n/\n"
            "&CELL\ncell_dynamics = 'bfgs'\n/\n"
        )
        parsed = parse_qe_input(text)
        assert set(parsed.namelists.keys()) == {
            "&CONTROL",
            "&SYSTEM",
            "&ELECTRONS",
            "&IONS",
            "&CELL",
        }

    def test_card_with_options(self) -> None:
        text = "ATOMIC_POSITIONS {crystal}\nSi 0.0 0.0 0.0\n"
        parsed = parse_qe_input(text)
        assert "ATOMIC_POSITIONS" in parsed.cards
        assert "CRYSTAL" in parsed.card_headers.get("ATOMIC_POSITIONS", "")

    def test_k_points_automatic(self) -> None:
        text = "K_POINTS {automatic}\n4 4 4 0 0 0\n"
        parsed = parse_qe_input(text)
        assert "K_POINTS" in parsed.cards
        rows = parsed.cards["K_POINTS"]
        assert len(rows) == 1

    def test_k_points_gamma(self) -> None:
        text = "K_POINTS {gamma}\n"
        parsed = parse_qe_input(text)
        assert "K_POINTS" in parsed.cards

    def test_cell_parameters(self) -> None:
        text = "CELL_PARAMETERS {angstrom}\n1.0 0.0 0.0\n0.0 1.0 0.0\n0.0 0.0 1.0\n"
        parsed = parse_qe_input(text)
        assert "CELL_PARAMETERS" in parsed.cards
        assert len(parsed.cards["CELL_PARAMETERS"]) == 3

    def test_declared_species_empty(self) -> None:
        parsed = parse_qe_input("&CONTROL\n/\n")
        assert declared_species(parsed) == set()

    def test_parameter_with_array_index(self) -> None:
        text = "&SYSTEM\nstarting_magnetization(1) = 0.6\n/\n"
        parsed = parse_qe_input(text)
        assert "starting_magnetization(1)" in parsed.namelists.get("&SYSTEM", {})

    def test_celldm_with_index(self) -> None:
        text = "&SYSTEM\ncelldm(1) = 10.26\ncelldm(2) = 1.0\n/\n"
        parsed = parse_qe_input(text)
        system = parsed.namelists.get("&SYSTEM", {})
        assert "celldm(1)" in system
        assert "celldm(2)" in system


# ===================================================================
# Text utilities
# ===================================================================


class TestTextUtilities:
    def test_strip_inline_comment(self) -> None:
        assert strip_inline_comment("  x = 1 ! comment") == "x = 1"

    def test_strip_inline_comment_no_comment(self) -> None:
        assert strip_inline_comment("  x = 1") == "x = 1"

    def test_strip_inline_comment_only_comment(self) -> None:
        assert strip_inline_comment("! comment") == ""

    def test_word_at_position(self) -> None:
        text = "  ecutwfc = 60"
        assert word_at_position(text, 0, 2) == "ecutwfc"

    def test_word_at_position_after_equals(self) -> None:
        text = "ecutwfc = 60"
        # character 10 is at '60'
        assert word_at_position(text, 0, 10) == "60"

    def test_word_at_position_out_of_range(self) -> None:
        assert word_at_position("hello", 5, 0) == ""

    def test_word_at_position_empty_text(self) -> None:
        assert word_at_position("", 0, 0) == ""


# ===================================================================
# Regression harness with real fixtures
# ===================================================================


class TestRegressionHarnessWithFixtures:
    """Load real .in files into the regression harness and validate."""

    def test_add_silicon_scf_as_fixture(self) -> None:
        text = _read_fixture("silicon_scf.in")
        harness = RegressionHarness()
        harness.add_fixture(
            GoldenFixture(
                name="silicon_scf",
                input_source=text,
                expected_diagnostics=[],
            )
        )
        result = harness.run_fixture("silicon_scf")
        assert result.passed

    def test_snapshot_silicon_scf(self) -> None:
        text = _read_fixture("silicon_scf.in")
        diagnostics = validate_qe_input(text)
        harness = RegressionHarness()
        snapshot = harness.snapshot_fixture("silicon_scf", text, diagnostics)
        data = json.loads(snapshot)
        assert data["name"] == "silicon_scf"
        assert data["expected_diagnostics"] == []

    def test_add_all_valid_fixtures(self) -> None:
        harness = RegressionHarness()
        for name in [
            "silicon_scf.in",
            "aluminum_relax.in",
            "sio2_vc_relax.in",
            "silicon_bands.in",
            "fe_spin.in",
        ]:
            text = _read_fixture(name)
            harness.add_fixture(
                GoldenFixture(
                    name=name,
                    input_source=text,
                    expected_diagnostics=[],
                )
            )
        assert harness.fixture_count == 5
        results = harness.run_all()
        assert all(r.passed for r in results)


# ===================================================================
# Server lifecycle
# ===================================================================


class TestServerLifecycle:
    """Test server creation and document management."""

    def test_create_server(self) -> None:
        from qe_lsp.server import create_server

        srv = create_server()
        assert srv.name == "qe-lsp"
        assert hasattr(srv, "diagnostic_provider")
        assert hasattr(srv, "lint_provider")
        assert hasattr(srv, "typecheck_provider")
        assert hasattr(srv, "code_action_provider")
        assert hasattr(srv, "formatting_provider")
        assert hasattr(srv, "documents")

    def test_server_features_registered(self) -> None:
        from qe_lsp.server import server

        features = get_registered_features(server)
        expected = [
            "textDocument/completion",
            "textDocument/hover",
            "textDocument/definition",
            "textDocument/references",
            "textDocument/documentSymbol",
            "textDocument/diagnostic",
            "textDocument/codeAction",
            "textDocument/prepareRename",
            "textDocument/rename",
            "textDocument/formatting",
            "textDocument/rangeFormatting",
        ]
        for feat in expected:
            assert feat in features, f"Missing feature: {feat}"


# ===================================================================
# Diagnostic provider snapshot consistency
# ===================================================================


class TestDiagnosticSnapshotConsistency:
    """Verify that diagnostic snapshots are deterministic and complete."""

    def test_snapshot_keys_on_invalid_input(self) -> None:
        server = _make_server()
        provider = DiagnosticProvider(server)
        text = "&CONTROL\ncalculation = 'bogus'\n/\n"
        snap = provider.snapshot(text)
        for item in snap:
            assert "range" in item
            assert "severity" in item
            assert "source" in item
            assert "message" in item

    def test_lint_snapshot_on_unknown_namelist(self) -> None:
        lint = LintProvider()
        text = "&FOOBAR\nx = 1\n/\n"
        snap = lint.snapshot(text)
        assert len(snap) >= 1
        for item in snap:
            assert "code" in item
            assert item["code"].startswith("QE-")

    def test_typecheck_snapshot_on_bad_type(self) -> None:
        tc = TypecheckProvider()
        text = "&SYSTEM\nibrav = abc\n/\n"
        snap = tc.snapshot(text)
        assert len(snap) >= 1
        for item in snap:
            assert "code" in item
            assert item["code"].startswith("QE-")


# ===================================================================
# Agent API with real fixtures
# ===================================================================


class TestAgentAPIWithFixtures:
    def test_snapshot_silicon_scf(self) -> None:
        text = _read_fixture("silicon_scf.in")
        api = AgentAPIProvider()
        snap = api.get_snapshot(text, uri="file:///silicon_scf.in")
        assert snap.uri == "file:///silicon_scf.in"
        assert snap.metadata["language"] == "quantum-espresso"
        assert snap.metadata["provider"] == "qe_lsp"
        assert snap.metadata["feature_count"]["outline_items"] > 0

    def test_outline_json(self) -> None:
        text = _read_fixture("aluminum_relax.in")
        api = AgentAPIProvider()
        outline_json = api.get_outline_json(text, uri="file:///aluminum_relax.in")
        data = json.loads(outline_json)
        assert "outline" in data
        assert len(data["outline"]) > 0

    def test_diagnostics_json(self) -> None:
        text = _read_fixture("silicon_scf.in")
        api = AgentAPIProvider()
        diags_json = api.get_diagnostics_json(text, uri="file:///silicon_scf.in")
        data = json.loads(diags_json)
        assert data["count"] == 0


# ===================================================================
# Test runner provider
# ===================================================================


class TestTestRunnerProviderIntegration:
    def test_parse_output_from_real_error(self) -> None:
        output = "     from line  10 : calculation type not implemented\n% error in calculation\n"
        result = parse_solver_output(output)
        assert not result.success

    def test_disabled_provider(self) -> None:
        provider = TestRunnerProvider()
        diags = provider.run_validation("test")
        assert len(diags) >= 1
        assert diags[0].code == "QE9000"

    def test_config_validation(self) -> None:
        config = TestRunnerConfig(enabled=True, executable="")
        errors = config.validate()
        assert len(errors) >= 1


# ===================================================================
# Cross-provider: all providers agree on valid input
# ===================================================================


class TestCrossProviderAgreement:
    """All diagnostic providers should agree that valid fixtures have no errors."""

    @pytest.mark.parametrize(
        "fixture_name",
        [
            "silicon_scf.in",
            "aluminum_relax.in",
            "sio2_vc_relax.in",
            "silicon_bands.in",
            "fe_spin.in",
        ],
        ids=["silicon_scf", "aluminum_relax", "sio2_vc_relax", "silicon_bands", "fe_spin"],
    )
    def test_all_providers_no_errors(self, fixture_name: str) -> None:
        text = _read_fixture(fixture_name)
        validation_diags = validate_qe_input(text)
        lint_diags = LintProvider().lint(text)
        typecheck_diags = TypecheckProvider().typecheck(text)

        all_diags = validation_diags + lint_diags + typecheck_diags
        errors = [d for d in all_diags if d.severity is not None and d.severity.value == 1]
        assert (
            errors == []
        ), f"Unexpected errors in {fixture_name}: {[(d.source, d.message) for d in errors]}"

"""Tests for the QE test-runner / dry-run bridge."""

import json
from pathlib import Path

from lsprotocol.types import DiagnosticSeverity
from qe_lsp.features.test_runner import (
    RULE_SCF_NOT_CONVERGED,
    TestRunnerConfig,
    TestRunnerProvider,
    parse_log,
    parse_solver_output,
    solver_output_to_diagnostics,
    SolverOutput,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "rules"


class TestTestRunnerConfig:
    def test_default_disabled(self):
        assert not TestRunnerConfig().enabled

    def test_validate_missing_executable(self):
        errors = TestRunnerConfig(enabled=True, executable="").validate()
        assert len(errors) == 1

    def test_validate_ok(self):
        assert len(TestRunnerConfig(executable="pw.x", enabled=True).validate()) == 0


class TestParseSolverOutput:
    def test_empty(self):
        assert parse_solver_output("").success

    def test_error(self):
        r = parse_solver_output("% error: bad input\n")
        assert not r.success
        assert len(r.errors) == 1

    def test_warning(self):
        r = parse_solver_output("warning: deprecated\n")
        assert r.success
        assert len(r.warnings) == 1

    def test_from_line(self):
        r = parse_solver_output("from line 5: unknown keyword\n")
        assert not r.success
        assert r.errors[0]["line"] == 4


class TestDiagnostics:
    def test_error_diagnostic(self):
        diags = solver_output_to_diagnostics(
            SolverOutput(errors=[{"message": "err", "line": 1, "source": "t"}])
        )
        assert diags[0].severity == DiagnosticSeverity.Error
        assert diags[0].code == "QE9001"

    def test_warning_diagnostic(self):
        diags = solver_output_to_diagnostics(
            SolverOutput(warnings=[{"message": "warn", "line": 0, "source": "t"}])
        )
        assert diags[0].severity == DiagnosticSeverity.Warning
        assert diags[0].code == "QE9002"


class TestProvider:
    def test_disabled(self):
        diags = TestRunnerProvider().run_validation("test")
        assert diags[0].severity == DiagnosticSeverity.Information

    def test_no_exec(self):
        diags = TestRunnerProvider(TestRunnerConfig(executable="", enabled=True)).run_validation(
            "t"
        )
        assert diags[0].severity == DiagnosticSeverity.Warning

    def test_missing_exec(self):
        diags = TestRunnerProvider(
            TestRunnerConfig(executable="/no/such/bin", enabled=True)
        ).run_validation("t")
        assert diags[0].severity == DiagnosticSeverity.Error

    def test_captured(self):
        diags = TestRunnerProvider().run_with_captured_output("% error: bad\n")
        assert len(diags) == 1

    def test_captured_clean(self):
        assert len(TestRunnerProvider().run_with_captured_output("ok\n")) == 0

    def test_snapshot(self):
        s = json.loads(
            TestRunnerProvider(TestRunnerConfig(executable="pw.x", enabled=True)).snapshot_config()
        )
        assert s["enabled"]
        assert s["executable"] == "pw.x"


class TestParseLogSCFNotConverged:
    """RULE qe.log.scf_not_converged (QE-E014): error on SCF non-convergence log."""

    def test_scf_not_converged_uppercase(self) -> None:
        """Standard QE output: 'SCF convergence NOT achieved'."""
        log = (
            "     Program PWSCF v.7.2 starts on 12Jun2024\n"
            "\n"
            "     SCF convergence NOT achieved after 100 iterations\n"
        )
        diags = parse_log(log)
        assert len(diags) == 1
        assert diags[0].code == RULE_SCF_NOT_CONVERGED
        assert diags[0].severity == DiagnosticSeverity.Error
        assert diags[0].source == "qe-log-parser"
        assert "SCF convergence NOT achieved" in diags[0].message
        # The error should be on line 2 (0-indexed)
        assert diags[0].range.start.line == 2

    def test_convergence_not_achieved_lowercase(self) -> None:
        """Variant: 'convergence not achieved' in lowercase."""
        log = "convergence not achieved\n"
        diags = parse_log(log)
        assert len(diags) == 1
        assert diags[0].code == RULE_SCF_NOT_CONVERGED

    def test_convergence_not_achieved_mixed_case(self) -> None:
        """Variant: mixed case 'convergence NOT achieved'."""
        log = "     convergence NOT achieved after 200 iterations\n"
        diags = parse_log(log)
        assert len(diags) == 1
        assert diags[0].code == RULE_SCF_NOT_CONVERGED

    def test_scf_convergence_is_not_achieved(self) -> None:
        """Variant: 'convergence is not achieved'."""
        log = "SCF convergence is not achieved\n"
        diags = parse_log(log)
        assert len(diags) == 1
        assert diags[0].code == RULE_SCF_NOT_CONVERGED

    def test_converged_log_no_error(self) -> None:
        """Normal convergence output should NOT trigger the rule."""
        log = (
            "     iteration #  1    energy = -100.5\n"
            "     iteration #  2    energy = -100.6\n"
            "     convergence has been achieved\n"
            "     !    total energy              =    -100.60000000 Ry\n"
        )
        diags = parse_log(log)
        scf_errors = [d for d in diags if d.code == RULE_SCF_NOT_CONVERGED]
        assert scf_errors == []

    def test_empty_log_no_error(self) -> None:
        """Empty log output should produce no diagnostics."""
        diags = parse_log("")
        assert diags == []

    def test_multiple_failures(self) -> None:
        """Multiple SCF failure lines produce multiple diagnostics."""
        log = (
            "SCF convergence NOT achieved after 100 iterations\n"
            "some intermediate output\n"
            "convergence not achieved\n"
        )
        diags = parse_log(log)
        assert len(diags) == 2
        assert diags[0].range.start.line == 0
        assert diags[1].range.start.line == 2

    def test_clean_log_no_error(self) -> None:
        """A successful SCF run log should not trigger."""
        log = (
            "     Program PWSCF v.7.2 starts today\n"
            "     Self-consistent Calculation\n"
            "     iteration #  1:  e = -100.0 Ry\n"
            "     iteration #  2:  e = -100.5 Ry\n"
            "     convergence achieved\n"
            "     End of self-consistent calculation\n"
            "     !    total energy = -100.500000 Ry\n"
        )
        diags = parse_log(log)
        scf_errors = [d for d in diags if d.code == RULE_SCF_NOT_CONVERGED]
        assert scf_errors == []

    def test_golden_fixture_exists_and_matches(self) -> None:
        """Verify the golden fixture file exists and its contents align."""
        fixture_path = FIXTURES_DIR / "log_scf_not_converged.json"
        assert fixture_path.exists(), f"Missing fixture: {fixture_path}"
        data = json.loads(fixture_path.read_text())
        assert data["rule_id"] == "qe.log.scf_not_converged"
        assert data["diagnostic_code"] == RULE_SCF_NOT_CONVERGED
        assert data["severity"] == "error"
        assert "SCF convergence" in data["message_pattern"]

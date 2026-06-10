"""Tests for the QE test-runner / dry-run bridge."""

import json
from lsprotocol.types import DiagnosticSeverity
from qe_lsp.features.test_runner import (
    TestRunnerConfig,
    TestRunnerProvider,
    parse_solver_output,
    solver_output_to_diagnostics,
    SolverOutput,
)


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

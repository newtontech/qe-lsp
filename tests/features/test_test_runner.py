"""Tests for the QE test-runner / dry-run bridge."""

import json
from pathlib import Path

import pytest

from lsprotocol.types import DiagnosticSeverity
from qe_lsp.features.test_runner import (
    RULE_BAND_STRUCTURE_ERROR,
    RULE_ERROR_IN_ROUTINE,
    RULE_MAX_CPU_TIME,
    RULE_PHONON_ERROR,
    RULE_QE_WARNING,
    RULE_SCF_NOT_CONVERGED,
    RULE_SEGMENTATION_FAULT,
    TestRunnerConfig,
    TestRunnerProvider,
    parse_log,
    parse_qe_output,
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


class TestParseLogErrorInRoutine:
    """RULE qe.log.error_in_routine (QE-E015): generic QE error in routine."""

    def test_error_in_routine_basic(self) -> None:
        """Standard 'Error in routine' line."""
        log = "     Error in routine pwscf (某某): some error description\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_ERROR_IN_ROUTINE]
        assert len(errors) == 1
        assert errors[0].severity == DiagnosticSeverity.Error
        assert errors[0].source == "qe-log-parser"
        assert "pwscf" in errors[0].message

    def test_error_in_routine_no_parens(self) -> None:
        """Error in routine without parenthetical detail."""
        log = "Error in routine c_phagsi: problems computing eigenvectors\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_ERROR_IN_ROUTINE]
        assert len(errors) == 1
        assert "c_phagsi" in errors[0].message

    def test_error_in_routine_with_detail(self) -> None:
        """Error in routine with colon-separated detail."""
        log = "Error in routine punch_plot (WRITE): error writing to file\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_ERROR_IN_ROUTINE]
        assert len(errors) == 1
        assert "punch_plot" in errors[0].message

    def test_no_false_positive(self) -> None:
        """Normal output should not trigger."""
        log = "     routine pwscf finished successfully\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_ERROR_IN_ROUTINE]
        assert errors == []

    def test_line_number_correct(self) -> None:
        """Error on third line gets line number 2."""
        log = "line 0\nline 1\nError in routine pwscf: bad\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_ERROR_IN_ROUTINE]
        assert len(errors) == 1
        assert errors[0].range.start.line == 2


class TestParseLogQEWarning:
    """RULE qe.log.warning (QE-E016): QE WARNING lines."""

    def test_warning_basic(self) -> None:
        """Standard WARNING: line."""
        log = "WARNING: degenerate or nearly degenerate eigenvalues found\n"
        diags = parse_log(log)
        warnings = [d for d in diags if d.code == RULE_QE_WARNING]
        assert len(warnings) == 1
        assert warnings[0].severity == DiagnosticSeverity.Warning
        assert warnings[0].source == "qe-log-parser"
        assert "degenerate" in warnings[0].message

    def test_warning_mixed_case(self) -> None:
        """Mixed-case warning should still match."""
        log = "Warning: something went wrong\n"
        diags = parse_log(log)
        warnings = [d for d in diags if d.code == RULE_QE_WARNING]
        assert len(warnings) == 1

    def test_no_false_positive(self) -> None:
        """Normal output without WARNING: should not trigger."""
        log = "     calculation finished without issues\n"
        diags = parse_log(log)
        warnings = [d for d in diags if d.code == RULE_QE_WARNING]
        assert warnings == []

    def test_multiple_warnings(self) -> None:
        """Multiple WARNING lines produce multiple diagnostics."""
        log = (
            "WARNING: first warning\n"
            "some output\n"
            "WARNING: second warning\n"
        )
        diags = parse_log(log)
        warnings = [d for d in diags if d.code == RULE_QE_WARNING]
        assert len(warnings) == 2
        assert warnings[0].range.start.line == 0
        assert warnings[1].range.start.line == 2


class TestParseLogSegfault:
    """RULE qe.log.seg_fault (QE-E017): Segmentation fault."""

    def test_segfault(self) -> None:
        log = "Segmentation fault\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_SEGMENTATION_FAULT]
        assert len(errors) == 1
        assert errors[0].severity == DiagnosticSeverity.Error
        assert "Segmentation fault" in errors[0].message

    def test_segfault_in_context(self) -> None:
        log = (
            "Program PWSCF v.7.2 starts\n"
            "some computation\n"
            "Segmentation fault (core dumped)\n"
        )
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_SEGMENTATION_FAULT]
        assert len(errors) == 1
        assert errors[0].range.start.line == 2

    def test_no_false_positive(self) -> None:
        log = "     computation completed successfully\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_SEGMENTATION_FAULT]
        assert errors == []


class TestParseLogMaxCPUTime:
    """RULE qe.log.max_cpu_time (QE-E018): Maximum CPU time exceeded."""

    def test_max_cpu_time(self) -> None:
        log = "Maximum CPU time exceeded\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_MAX_CPU_TIME]
        assert len(errors) == 1
        assert errors[0].severity == DiagnosticSeverity.Error

    def test_max_cpu_time_with_detail(self) -> None:
        log = (
            "     WARNING: Maximum CPU time exceeded in scf cycle\n"
        )
        diags = parse_log(log)
        max_cpu = [d for d in diags if d.code == RULE_MAX_CPU_TIME]
        assert len(max_cpu) == 1

    def test_no_false_positive(self) -> None:
        log = "     CPU time: 12.5 seconds\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_MAX_CPU_TIME]
        assert errors == []


class TestParseLogBandStructureError:
    """RULE qe.log.band_structure_error (QE-E019): band structure errors."""

    def test_band_structure_error(self) -> None:
        log = "band structure calculation error\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_BAND_STRUCTURE_ERROR]
        assert len(errors) == 1
        assert errors[0].severity == DiagnosticSeverity.Error

    def test_bands_fail(self) -> None:
        log = "     bands error during interpolation\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_BAND_STRUCTURE_ERROR]
        assert len(errors) == 1

    def test_band_structure_fail(self) -> None:
        log = "band structure calculation fail\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_BAND_STRUCTURE_ERROR]
        assert len(errors) == 1

    def test_no_false_positive(self) -> None:
        log = "     band structure computed successfully\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_BAND_STRUCTURE_ERROR]
        assert errors == []


class TestParseLogPhononError:
    """RULE qe.log.phonon_error (QE-E020): phonon calculation errors."""

    def test_phonon_error(self) -> None:
        log = "phonon calculation error\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_PHONON_ERROR]
        assert len(errors) == 1
        assert errors[0].severity == DiagnosticSeverity.Error

    def test_ph_error(self) -> None:
        log = "     ph calculation error in q-point\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_PHONON_ERROR]
        assert len(errors) == 1

    def test_lambda_error(self) -> None:
        log = "lambda calculation error\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_PHONON_ERROR]
        assert len(errors) == 1

    def test_phonon_fail(self) -> None:
        log = "phonon calculation fail\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_PHONON_ERROR]
        assert len(errors) == 1

    def test_no_false_positive(self) -> None:
        log = "     phonon frequencies computed successfully\n"
        diags = parse_log(log)
        errors = [d for d in diags if d.code == RULE_PHONON_ERROR]
        assert errors == []


class TestParseLogMixed:
    """Multiple error types in the same log produce multiple diagnostics."""

    def test_mixed_errors(self) -> None:
        log = (
            "WARNING: something suspicious\n"
            "SCF convergence NOT achieved after 100 iterations\n"
            "Error in routine pwscf: bad input\n"
            "Segmentation fault\n"
        )
        diags = parse_log(log)
        codes = [d.code for d in diags]
        assert RULE_QE_WARNING in codes
        assert RULE_SCF_NOT_CONVERGED in codes
        assert RULE_ERROR_IN_ROUTINE in codes
        assert RULE_SEGMENTATION_FAULT in codes
        assert len(diags) == 4


class TestParseQEOutput:
    """Tests for parse_qe_output file-based function."""

    def test_reads_file_and_parses(self, tmp_path: Path) -> None:
        """parse_qe_output reads a file and returns diagnostics."""
        log_file = tmp_path / "pw.out"
        log_file.write_text("SCF convergence NOT achieved after 50 iterations\n")
        diags = parse_qe_output(log_file)
        assert len(diags) == 1
        assert diags[0].code == RULE_SCF_NOT_CONVERGED

    def test_clean_file_no_diagnostics(self, tmp_path: Path) -> None:
        """Clean output produces no diagnostics."""
        log_file = tmp_path / "pw.out"
        log_file.write_text("     Program PWSCF v.7.2 starts\n     convergence achieved\n")
        diags = parse_qe_output(log_file)
        assert diags == []

    def test_file_not_found(self) -> None:
        """Raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            parse_qe_output(Path("/no/such/file.out"))

    def test_multi_pattern_file(self, tmp_path: Path) -> None:
        """File with multiple errors produces multiple diagnostics."""
        log_file = tmp_path / "pw.out"
        log_file.write_text(
            "WARNING: something\n"
            "Error in routine pwscf: bad\n"
            "Segmentation fault\n"
        )
        diags = parse_qe_output(log_file)
        assert len(diags) == 3

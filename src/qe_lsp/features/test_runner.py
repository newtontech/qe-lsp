"""Optional test-runner / dry-run bridge for Quantum ESPRESSO.

Provides an opt-in command that runs QE validation or dry-run checks
when the binary is configured, and maps solver output back into LSP
diagnostics.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from lsprotocol.types import Diagnostic, DiagnosticSeverity, Position, Range


@dataclass
class TestRunnerConfig:
    """Configuration for the QE test runner."""

    executable: str = ""
    timeout: float = 30.0
    enabled: bool = False

    def validate(self) -> List[str]:
        errors: List[str] = []
        if self.enabled and not self.executable:
            errors.append("QE executable path is not configured")
        if self.timeout <= 0:
            errors.append("Timeout must be positive")
        return errors


@dataclass
class SolverOutput:
    success: bool = True
    raw_output: str = ""
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)


_ERROR_PATTERNS = [
    (re.compile(r"%\s*error[^:]*:\s*(.+?)(?:\n|$)", re.MULTILINE), "error"),
    (re.compile(r"warning\s*:\s*(.+?)(?:\n|$)", re.MULTILINE), "warning"),
    (re.compile(r"from line\s+(\d+)\s*:\s*(.+?)(?:\n|$)", re.MULTILINE), "error"),
]

_LINE_NUM_RE = re.compile(r"line\s+(\d+)", re.IGNORECASE)


def parse_solver_output(raw: str) -> SolverOutput:
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    for pattern, severity in _ERROR_PATTERNS:
        for match in pattern.finditer(raw):
            groups = match.groups()
            message = groups[-1].strip() if groups else match.group(0).strip()
            line_num = 0
            if len(groups) >= 2:
                try:
                    line_num = int(groups[0]) - 1
                except (ValueError, IndexError):
                    pass
            line_match = _LINE_NUM_RE.search(message)
            if line_match and line_num == 0:
                line_num = int(line_match.group(1)) - 1
            entry = {"message": message, "line": line_num, "source": "qe-test-runner"}
            (errors if severity == "error" else warnings).append(entry)
    return SolverOutput(success=len(errors) == 0, raw_output=raw, errors=errors, warnings=warnings)


def solver_output_to_diagnostics(output: SolverOutput) -> List[Diagnostic]:
    diagnostics: List[Diagnostic] = []
    for err in output.errors:
        diagnostics.append(
            Diagnostic(
                range=Range(
                    start=Position(line=err["line"], character=0),
                    end=Position(line=err["line"], character=999),
                ),
                message=err["message"],
                severity=DiagnosticSeverity.Error,
                source="qe-test-runner",
                code="QE9001",
            )
        )
    for warn in output.warnings:
        diagnostics.append(
            Diagnostic(
                range=Range(
                    start=Position(line=warn["line"], character=0),
                    end=Position(line=warn["line"], character=999),
                ),
                message=warn["message"],
                severity=DiagnosticSeverity.Warning,
                source="qe-test-runner",
                code="QE9002",
            )
        )
    return diagnostics


class TestRunnerProvider:
    def __init__(self, config: Optional[TestRunnerConfig] = None) -> None:
        self._config = config or TestRunnerConfig()

    @property
    def config(self) -> TestRunnerConfig:
        return self._config

    @config.setter
    def config(self, value: TestRunnerConfig) -> None:
        self._config = value

    def validate_config(self) -> List[str]:
        return self._config.validate()

    def run_validation(self, source: str) -> List[Diagnostic]:
        if not self._config.enabled:
            return [
                Diagnostic(
                    range=Range(start=Position(0, 0), end=Position(0, 0)),
                    message="QE test runner is not enabled. Configure the executable path to enable.",
                    severity=DiagnosticSeverity.Information,
                    source="qe-test-runner",
                    code="QE9000",
                )
            ]
        if not self._config.executable:
            return [
                Diagnostic(
                    range=Range(start=Position(0, 0), end=Position(0, 0)),
                    message="QE executable path is not configured.",
                    severity=DiagnosticSeverity.Warning,
                    source="qe-test-runner",
                    code="QE9000",
                )
            ]
        import shutil

        if not shutil.which(self._config.executable):
            return [
                Diagnostic(
                    range=Range(start=Position(0, 0), end=Position(0, 0)),
                    message=f"QE executable not found: {self._config.executable}",
                    severity=DiagnosticSeverity.Error,
                    source="qe-test-runner",
                    code="QE9000",
                )
            ]
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".in", delete=False) as f:
                f.write(source)
                temp_path = f.name
            result = subprocess.run(
                [self._config.executable, "-input", temp_path],
                capture_output=True,
                text=True,
                timeout=self._config.timeout,
            )
            raw_output = result.stdout + "\n" + result.stderr
            output = parse_solver_output(raw_output)
            return solver_output_to_diagnostics(output)
        except subprocess.TimeoutExpired:
            return [
                Diagnostic(
                    range=Range(start=Position(0, 0), end=Position(0, 0)),
                    message=f"QE validation timed out after {self._config.timeout}s.",
                    severity=DiagnosticSeverity.Warning,
                    source="qe-test-runner",
                    code="QE9003",
                )
            ]
        except FileNotFoundError:
            return [
                Diagnostic(
                    range=Range(start=Position(0, 0), end=Position(0, 0)),
                    message=f"QE executable not found: {self._config.executable}",
                    severity=DiagnosticSeverity.Error,
                    source="qe-test-runner",
                    code="QE9000",
                )
            ]
        finally:
            try:
                Path(temp_path).unlink()
            except (NameError, FileNotFoundError):
                pass

    def run_with_captured_output(self, captured_output: str) -> List[Diagnostic]:
        output = parse_solver_output(captured_output)
        return solver_output_to_diagnostics(output)

    def snapshot_config(self) -> str:
        return json.dumps(
            {
                "enabled": self._config.enabled,
                "executable": self._config.executable or "(not configured)",
                "timeout": self._config.timeout,
            },
            indent=2,
        )

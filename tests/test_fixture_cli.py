"""Tests for agent CLI against fixtures with stable DiagnosticEnvelope/v1 JSON."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"
INVALID_DIR = FIXTURES_DIR / "invalid"
LOGS_DIR = FIXTURES_DIR / "logs"


def run_tool(args: list[str], timeout: int = 30) -> dict[str, Any]:
    """Run the qe-lsp-tool and return the JSON output."""
    cmd = [sys.executable, "-m", "qe_lsp.tool"] + args
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, cwd=str(FIXTURES_DIR)
    )
    if result.returncode not in (0, 1):  # 0 = ok, 1 = blocking diagnostics
        pytest.fail(f"Tool failed with code {result.returncode}: {result.stderr}")
    return cast("dict[str, Any]", json.loads(result.stdout))


class TestValidFixtures:
    """Valid fixtures should have no blocking diagnostics."""

    def test_valid_scf_no_blocking(self) -> None:
        payload = run_tool(["check", str(VALID_DIR / "scf_valid.in")])
        assert payload["ok"] is True
        assert payload["summary"]["blocking"] == 0
        assert payload["software"] == "qe"

    def test_valid_relax_no_blocking(self) -> None:
        payload = run_tool(["check", str(VALID_DIR / "relax_valid.in")])
        assert payload["ok"] is True
        assert payload["summary"]["blocking"] == 0

    def test_valid_silicon_scf_no_blocking(self) -> None:
        payload = run_tool(["check", str(VALID_DIR / "silicon_scf_valid.in")])
        assert payload["ok"] is True
        assert payload["summary"]["blocking"] == 0


class TestInvalidFixtures:
    """Invalid fixtures should have blocking diagnostics."""

    def test_missing_cell_parameters_blocking(self) -> None:
        payload = run_tool(["check", str(INVALID_DIR / "missing_cell_parameters.in")])
        assert payload["ok"] is False
        assert payload["summary"]["blocking"] > 0
        assert any(d["code"] == "QE-TE004" for d in payload["diagnostics"])

    def test_low_ecutrho_ratio_warning(self) -> None:
        payload = run_tool(["check", str(INVALID_DIR / "low_ecutrho_ratio.in")])
        # This should be a warning, not blocking
        assert payload["summary"]["warnings"] > 0
        assert any("4x to 16x" in d["message"] for d in payload["diagnostics"])

    def test_unclosed_namelist_blocking(self) -> None:
        payload = run_tool(["check", str(INVALID_DIR / "unclosed_namelist.in")])
        assert payload["ok"] is False
        assert payload["summary"]["blocking"] > 0

    def test_pseudo_element_mismatch_blocking(self) -> None:
        payload = run_tool(["check", str(INVALID_DIR / "pseudo_element_mismatch.in")])
        assert payload["ok"] is False
        assert payload["summary"]["blocking"] > 0

    def test_atomic_positions_without_species_blocking(self) -> None:
        payload = run_tool(["check", str(INVALID_DIR / "atomic_positions_without_species.in")])
        assert payload["ok"] is False
        assert payload["summary"]["blocking"] > 0

    def test_gamma_nonzero_offset_warning(self) -> None:
        payload = run_tool(["check", str(INVALID_DIR / "gamma_nonzero_offset.in")])
        assert payload["summary"]["warnings"] > 0


class TestLogFixtures:
    """Log fixtures should be parseable (logs are not parsed by check)."""

    def test_logs_directory_exists(self) -> None:
        assert LOGS_DIR.exists()
        assert len(list(LOGS_DIR.glob("*.log"))) >= 1


class TestDiagnosticEnvelopeSchema:
    """All diagnostics should match DiagnosticEnvelope/v1."""

    def test_envelope_fields_on_valid(self) -> None:
        payload = run_tool(["check", str(VALID_DIR / "scf_valid.in")])
        assert "diagnostic_engine" in payload
        assert "ok" in payload
        assert "diagnostics" in payload
        assert "summary" in payload
        assert "blocking" in payload["summary"]
        assert "errors" in payload["summary"]
        assert "warnings" in payload["summary"]

    def test_diagnostic_fields(self) -> None:
        payload = run_tool(["check", str(INVALID_DIR / "missing_cell_parameters.in")])
        for diag in payload["diagnostics"]:
            assert "code" in diag
            assert "severity" in diag
            assert "category" in diag
            assert "confidence" in diag
            assert "source" in diag
            assert "range" in diag
            assert "software" in diag
            assert "path" in diag
            assert "message" in diag
            assert "blocking" in diag
            assert "diagnostic_engine" in diag


class TestAgentCLI:
    """Test other agent CLI operations."""

    def test_capabilities(self) -> None:
        payload = run_tool(["capabilities"])
        assert payload["software"] == "qe"
        assert "diagnostics" in payload["capabilities"]
        assert "fix-placeholder" in payload["capabilities"]

    def test_context(self) -> None:
        payload = run_tool(
            ["context", str(VALID_DIR / "scf_valid.in"), "--line", "2", "--character", "5"]
        )
        assert "context" in payload
        assert "position" in payload

    def test_complete(self) -> None:
        payload = run_tool(
            ["complete", str(VALID_DIR / "scf_valid.in"), "--line", "2", "--character", "5"]
        )
        assert "items" in payload
        assert isinstance(payload["items"], list)

    def test_hover(self) -> None:
        payload = run_tool(
            ["hover", str(VALID_DIR / "scf_valid.in"), "--line", "2", "--character", "5"]
        )
        assert "contents" in payload or payload.get("status") == "unavailable"

    def test_symbols(self) -> None:
        payload = run_tool(["symbols", str(VALID_DIR / "scf_valid.in")])
        assert "items" in payload
        assert isinstance(payload["items"], list)

    def test_fix(self) -> None:
        payload = run_tool(
            [
                "fix",
                str(INVALID_DIR / "missing_cell_parameters.in"),
                "--line",
                "5",
                "--character",
                "5",
            ]
        )
        assert "actions" in payload
        assert isinstance(payload["actions"], list)


class TestPreflightFixtures:
    """Test preflight fixtures with intent.json."""

    def test_preflight_valid(self) -> None:
        payload = run_tool(["check", str(FIXTURES_DIR / "preflight" / "valid_pw" / "pw.in")])
        assert payload["ok"] is True

    def test_preflight_invalid(self) -> None:
        payload = run_tool(["check", str(FIXTURES_DIR / "preflight" / "ntyp_mismatch" / "pw.in")])
        # ntyp_mismatch produces a warning about mixed pseudopotential families
        assert payload["summary"]["warnings"] > 0

"""Focused tests for the OpenQC v1 docstring-wiki-raw traceability report contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = REPO_ROOT / "reports" / "docstring-wiki-raw-traceability.json"
CHECKER_SCRIPT = REPO_ROOT / "scripts" / "generate-traceability-report.py"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def report() -> dict:
    """Load the generated traceability report."""
    if not REPORT_PATH.exists():
        pytest.skip(
            f"Report not found at {REPORT_PATH}; run scripts/generate-traceability-report.py first"
        )
    with open(REPORT_PATH, encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


# ---------------------------------------------------------------------------
# Schema contract tests
# ---------------------------------------------------------------------------


class TestOpenQCTraceabilityV1Schema:
    """Verify the report satisfies the openqc.lsp.traceability.v1 contract."""

    def test_schema_version(self, report: dict) -> None:
        assert report["schemaVersion"] == "openqc.lsp.traceability.v1"

    def test_top_level_fields_present(self, report: dict) -> None:
        required = [
            "schemaVersion",
            "serverId",
            "repository",
            "languageId",
            "generatedAt",
            "summary",
            "docstrings",
            "wikiSources",
            "ruleIds",
            "sourceUrls",
            "rawManifest",
        ]
        for field in required:
            assert field in report, f"Missing required top-level field: {field}"

    def test_server_id(self, report: dict) -> None:
        assert isinstance(report["serverId"], str)
        assert len(report["serverId"]) > 0

    def test_repository(self, report: dict) -> None:
        assert isinstance(report["repository"], str)
        assert "qe-lsp" in report["repository"]

    def test_language_id(self, report: dict) -> None:
        assert report["languageId"] == "qe"

    def test_generated_at_format(self, report: dict) -> None:
        from datetime import datetime

        dt = datetime.fromisoformat(report["generatedAt"])
        assert dt.tzinfo is not None  # must be timezone-aware

    def test_summary_structure(self, report: dict) -> None:
        s = report["summary"]
        assert "docstringsTotal" in s
        assert "docstringsLinked" in s
        assert "brokenWikiLinks" in s
        assert "wikiSourcesWithoutRaw" in s
        assert "rawManifestFailures" in s
        assert s["docstringsLinked"] == s["docstringsTotal"]
        assert s["brokenWikiLinks"] == 0
        assert s["wikiSourcesWithoutRaw"] == 0
        assert s["rawManifestFailures"] == 0


# ---------------------------------------------------------------------------
# Docstrings contract
# ---------------------------------------------------------------------------


class TestDocstrings:
    """Verify docstrings[] entries."""

    def test_docstrings_is_list(self, report: dict) -> None:
        assert isinstance(report["docstrings"], list)
        assert len(report["docstrings"]) > 0

    def test_docstring_entry_fields(self, report: dict) -> None:
        for entry in report["docstrings"]:
            assert isinstance(entry, dict)
            assert "path" in entry
            assert "wikiPath" in entry
            assert "symbol" in entry
            # All must be non-empty strings
            assert isinstance(entry["path"], str) and len(entry["path"]) > 0
            assert isinstance(entry["wikiPath"], str) and len(entry["wikiPath"]) > 0
            assert isinstance(entry["symbol"], str) and len(entry["symbol"]) > 0
            # wikiPath must start with wiki/
            assert entry["wikiPath"].startswith("wiki/")
            # path must be a repo-relative path
            assert not entry["path"].startswith("/")

    def test_docstring_paths_exist(self, report: dict) -> None:
        for entry in report["docstrings"]:
            full_path = REPO_ROOT / entry["path"]
            assert full_path.exists(), f"Source file not found: {entry['path']}"

    def test_docstring_wiki_paths_exist(self, report: dict) -> None:
        for entry in report["docstrings"]:
            full_path = REPO_ROOT / entry["wikiPath"]
            assert full_path.exists(), f"Wiki page not found: {entry['wikiPath']}"


# ---------------------------------------------------------------------------
# Wiki sources contract
# ---------------------------------------------------------------------------


class TestWikiSources:
    """Verify wikiSources[] entries."""

    def test_wiki_sources_is_list(self, report: dict) -> None:
        assert isinstance(report["wikiSources"], list)
        assert len(report["wikiSources"]) > 0

    def test_wiki_source_entry_fields(self, report: dict) -> None:
        for entry in report["wikiSources"]:
            assert isinstance(entry, dict)
            assert "wikiPath" in entry
            assert "rawPath" in entry
            assert "sourceUrl" in entry
            # wikiPath and rawPath must be non-empty
            assert isinstance(entry["wikiPath"], str) and len(entry["wikiPath"]) > 0
            assert isinstance(entry["rawPath"], str) and len(entry["rawPath"]) > 0
            # sourceUrl is a string (may be empty)
            assert isinstance(entry["sourceUrl"], str)
            # wikiPath must start with wiki/
            assert entry["wikiPath"].startswith("wiki/")
            # rawPath must be a repo-relative path
            assert "raw/assets/" in entry["rawPath"]

    def test_wiki_source_wiki_paths_exist(self, report: dict) -> None:
        for entry in report["wikiSources"]:
            full_path = REPO_ROOT / entry["wikiPath"]
            assert full_path.exists(), f"Wiki page not found: {entry['wikiPath']}"

    def test_wiki_source_raw_paths_exist(self, report: dict) -> None:
        for entry in report["wikiSources"]:
            full_path = REPO_ROOT / entry["rawPath"]
            assert full_path.exists(), f"Raw asset not found: {entry['rawPath']}"


# ---------------------------------------------------------------------------
# Rule IDs contract
# ---------------------------------------------------------------------------


class TestRuleIds:
    """Verify ruleIds[] entries."""

    def test_rule_ids_is_list(self, report: dict) -> None:
        assert isinstance(report["ruleIds"], list)
        assert len(report["ruleIds"]) > 0

    def test_rule_id_entry_fields(self, report: dict) -> None:
        for entry in report["ruleIds"]:
            assert isinstance(entry, dict)
            assert "code" in entry
            assert "sourcePath" in entry
            assert isinstance(entry["code"], str) and len(entry["code"]) > 0
            assert isinstance(entry["sourcePath"], str) and len(entry["sourcePath"]) > 0
            # Code must match the OpenQC <BACKEND>-<FILE_ROLE>-<CATEGORY>-NNN pattern.
            import re

            assert re.match(
                r"^QE-INPUT-(ERROR|WARNING|INFO)-\d{3}$", entry["code"]
            ), f"Rule code {entry['code']} does not match OpenQC rule ID format"

    def test_rule_id_source_paths_exist(self, report: dict) -> None:
        for entry in report["ruleIds"]:
            full_path = REPO_ROOT / entry["sourcePath"]
            assert full_path.exists(), f"Source file not found: {entry['sourcePath']}"

    def test_rule_ids_from_lint_are_present(self, report: dict) -> None:
        """Verify at least the core lint rules from lint.py are represented."""
        codes = {r["code"] for r in report["ruleIds"]}
        expected_core = {
            "QE-INPUT-ERROR-001",
            "QE-INPUT-ERROR-002",
            "QE-INPUT-ERROR-003",
            "QE-INPUT-WARNING-001",
            "QE-INPUT-WARNING-002",
            "QE-INPUT-WARNING-003",
            "QE-INPUT-ERROR-004",
            "QE-INPUT-ERROR-005",
            "QE-INPUT-ERROR-006",
            "QE-INPUT-ERROR-007",
            "QE-INPUT-WARNING-004",
            "QE-INPUT-ERROR-008",
            "QE-INPUT-ERROR-009",
            "QE-INPUT-WARNING-010",
            "QE-INPUT-WARNING-011",
            "QE-INPUT-WARNING-012",
            "QE-INPUT-ERROR-013",
        }
        missing = expected_core - codes
        assert not missing, f"Missing expected rule codes: {missing}"


# ---------------------------------------------------------------------------
# Source URLs contract
# ---------------------------------------------------------------------------


class TestSourceUrls:
    """Verify sourceUrls[] entries."""

    def test_source_urls_is_list(self, report: dict) -> None:
        assert isinstance(report["sourceUrls"], list)
        assert len(report["sourceUrls"]) > 0

    def test_source_url_entry_fields(self, report: dict) -> None:
        for entry in report["sourceUrls"]:
            assert isinstance(entry, dict)
            assert "rawPath" in entry
            assert "url" in entry
            assert isinstance(entry["rawPath"], str)
            assert isinstance(entry["url"], str) and len(entry["url"]) > 0
            # URL must start with http:// or https://
            assert entry["url"].startswith("http")

    def test_source_url_has_upstream_urls(self, report: dict) -> None:
        """Must include at least the core QE upstream URLs."""
        all_urls = {e["url"] for e in report["sourceUrls"]}
        assert any(
            "quantum-espresso.org" in u for u in all_urls
        ), "Missing quantum-espresso.org URLs"


# ---------------------------------------------------------------------------
# Raw manifest contract
# ---------------------------------------------------------------------------


class TestRawManifest:
    """Verify rawManifest entries."""

    def test_raw_manifest_is_object(self, report: dict) -> None:
        assert isinstance(report["rawManifest"], dict)
        assert len(report["rawManifest"]) > 0

    def test_raw_manifest_entries_are_valid(self, report: dict) -> None:
        manifest = report["rawManifest"]
        assert isinstance(manifest["path"], str) and len(manifest["path"]) > 0
        assert isinstance(manifest["ok"], bool)
        assert manifest["path"].startswith("raw/assets/")

    def test_raw_manifest_paths_exist(self, report: dict) -> None:
        full_path = REPO_ROOT / report["rawManifest"]["path"]
        assert full_path.exists(), f"Raw manifest not found: {report['rawManifest']['path']}"

    def test_all_raw_assets_ok(self, report: dict) -> None:
        """No raw asset should be flagged as failing."""
        assert report["rawManifest"]["ok"] is True


# ---------------------------------------------------------------------------
# Regeneration smoke test
# ---------------------------------------------------------------------------


class TestRegeneration:
    """Verify the checker script can regenerate the report."""

    def test_checker_script_exists(self) -> None:
        assert CHECKER_SCRIPT.exists(), f"Checker script not found: {CHECKER_SCRIPT}"

    def test_checker_script_runs(self) -> None:
        """Run the checker script and confirm it exits 0."""
        import subprocess

        result = subprocess.run(
            [sys.executable, str(CHECKER_SCRIPT)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert (
            result.returncode == 0
        ), f"Checker script failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        assert REPORT_PATH.exists()


# ---------------------------------------------------------------------------
# Consistency / cross-reference tests
# ---------------------------------------------------------------------------


class TestConsistency:
    """Cross-reference checks between report sections."""

    def test_rule_ids_at_lint_module(self, report: dict) -> None:
        """Lint.py should be one of the sources for rule IDs."""
        lint_sources = [r for r in report["ruleIds"] if "lint.py" in r["sourcePath"]]
        assert len(lint_sources) > 0, "No rule IDs from lint.py"

    def test_docstring_wiki_paths_in_wiki_sources(self, report: dict) -> None:
        """Docstring wiki paths should also appear in wikiSources."""
        docstring_wikis = {e["wikiPath"] for e in report["docstrings"]}
        wiki_source_wikis = {e["wikiPath"] for e in report["wikiSources"]}
        # At least some overlap is expected
        overlap = docstring_wikis & wiki_source_wikis
        assert len(overlap) > 0, "No wiki path appears in both docstrings and wikiSources"

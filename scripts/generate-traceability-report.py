#!/usr/bin/env python3
"""OpenQC v1 traceability report generator.

Generates reports/docstring-wiki-raw-traceability.json satisfying the
openqc.lsp.traceability.v1 schema.  Scans the source tree for:

  - docstrings that reference wiki paths (via "See also:" or other patterns)
  - wiki pages that reference raw asset files
  - rule identifiers defined in source code
  - upstream source URLs from the raw manifest
  - raw asset file existence / validity
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports"
REPORT_PATH = REPORTS_DIR / "docstring-wiki-raw-traceability.json"

# repo identity
SERVER_ID = "qe-lsp"
LANGUAGE_ID = "qe"
REPOSITORY = "newtontech/qe-lsp"

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

#: Pattern for "See also:" wiki references in docstrings
SEE_ALSO_RE = re.compile(
    r"See also:\s*(.+)",
    re.IGNORECASE,
)

#: Extract a clean wiki path from a "See also:" line
SEE_ALSO_WIKI_RE = re.compile(r"wiki/(?:entities|concepts|synthesis)/[\w/\-]+\.md")

#: Pattern for raw asset references in wiki pages
RAW_ASSET_RE = re.compile(r"raw/assets/[\w./-]+")

#: Pattern for rule code references (e.g. QE-E001, QE-W012)
RULE_CODE_RE = re.compile(r"QE-[EWI]\d{3}")

#: Pattern for source URLs in markdown tables/lists
SOURCE_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:quantum-espresso|pranabdas|github|materialscloud|blog\.levilentz|wiki\.max-centre)"
    r"\.[\w./?=&%-]+",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def repo_relative(path: Path) -> str:
    """Return path relative to REPO_ROOT."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _infer_symbol(text: str, pyfile: Path) -> str:
    """Infer a module/class/function name from the file."""
    cm = re.search(r"^class\s+(\w+)", text, re.MULTILINE)
    if cm:
        return cm.group(1)
    fm = re.search(r"^def\s+(\w+)", text, re.MULTILINE)
    if fm:
        return fm.group(1)
    return pyfile.stem


def _find_source_url(text: str, raw_path: str) -> str | None:
    """Search for a URL near a raw path reference."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if raw_path in line:
            for j in range(i, min(i + 4, len(lines))):
                urls = SOURCE_URL_RE.findall(lines[j])
                if urls:
                    return str(urls[0])
    return None


def _git_remote_url() -> str:
    """Get the git remote origin URL."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def _openqc_rule_code(code: str) -> str:
    """Convert legacy QE-E001/QE-W001/QE-I001 codes to OpenQC rule IDs."""
    match = re.fullmatch(r"QE-([EWI])(\d{3})", code)
    if not match:
        return code
    category = {
        "E": "ERROR",
        "W": "WARNING",
        "I": "INFO",
    }[match.group(1)]
    return f"QE-INPUT-{category}-{match.group(2)}"


def _raw_asset_files() -> list[Path]:
    """Return all raw asset files tracked by the traceability manifest."""
    raw_assets = REPO_ROOT / "raw" / "assets"
    if not raw_assets.exists():
        return []
    return sorted(path for path in raw_assets.rglob("*") if path.is_file())


def write_raw_asset_manifest() -> Path:
    """Write a deterministic manifest for all raw evidence assets."""
    manifest_path = REPO_ROOT / "raw" / "assets" / "manifest.json"
    entries = []
    for raw_file in _raw_asset_files():
        if raw_file == manifest_path:
            continue
        raw_rel = repo_relative(raw_file)
        entries.append(
            {
                "path": raw_rel.removeprefix("raw/assets/"),
                "source_type": "raw_asset",
                "source_url": f"https://github.com/{REPOSITORY}/blob/main/{raw_rel}",
                "stable_id": raw_rel.replace("/", "-").replace(".", "-"),
            }
        )
    payload = {
        "manifest_version": "1.0.0",
        "schema_version": "provenance-manifest-v1",
        "repository": REPOSITORY,
        "entries": entries,
    }
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest_path


# ---------------------------------------------------------------------------
# Collectors
# ---------------------------------------------------------------------------


def collect_docstrings() -> list[dict[str, str]]:
    """Scan source code for docstrings referencing wiki paths."""
    entries: list[dict[str, str]] = []
    src_dir = REPO_ROOT / "src"
    for pyfile in sorted(src_dir.rglob("*.py")):
        text = pyfile.read_text(encoding="utf-8")
        # Find "See also:" lines in docstring context
        see_also_matches = SEE_ALSO_RE.findall(text)
        if not see_also_matches:
            continue
        symbol = _infer_symbol(text, pyfile)
        for match in see_also_matches:
            wiki_paths = SEE_ALSO_WIKI_RE.findall(match)
            for wp in wiki_paths:
                entries.append(
                    {
                        "path": repo_relative(pyfile),
                        "wikiPath": wp,
                        "symbol": symbol,
                    }
                )
    # Deduplicate
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, str]] = []
    for e in entries:
        key = (e["path"], e["wikiPath"], e["symbol"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


def collect_wiki_sources() -> list[dict[str, str]]:
    """Scan wiki pages for references to raw assets and source URLs."""
    entries: list[dict[str, str]] = []
    wiki_dir = REPO_ROOT / "wiki"
    for mdfile in sorted(wiki_dir.rglob("*.md")):
        text = mdfile.read_text(encoding="utf-8")
        raw_refs = RAW_ASSET_RE.findall(text)
        if not raw_refs:
            continue
        for raw_path in sorted(set(raw_refs)):
            source_url = _find_source_url(text, raw_path)
            entries.append(
                {
                    "wikiPath": repo_relative(mdfile),
                    "rawPath": raw_path,
                    "sourceUrl": source_url or "",
                }
            )
    return entries


def collect_rule_ids() -> list[dict[str, str]]:
    """Extract rule identifiers from lint and diagnostic source."""
    entries: list[dict[str, str]] = []
    src_dir = REPO_ROOT / "src"
    for pyfile in sorted(src_dir.rglob("*.py")):
        text = pyfile.read_text(encoding="utf-8")
        codes = RULE_CODE_RE.findall(text)
        if not codes:
            continue
        for code in sorted(set(codes)):
            entries.append(
                {
                    "code": _openqc_rule_code(code),
                    "sourcePath": repo_relative(pyfile),
                }
            )
    return entries


def collect_source_urls() -> list[dict[str, str]]:
    """Collect upstream source URLs from raw assets."""
    entries: list[dict[str, str]] = []

    # 1. From lsp-capabilities.json sourceProvenance
    cap_path = REPO_ROOT / "lsp-capabilities.json"
    if cap_path.exists():
        try:
            cap = json.loads(cap_path.read_text(encoding="utf-8"))
            for prov in cap.get("sourceProvenance", []):
                url = prov.get("url", "")
                raw_path = prov.get("path", "")
                if url:
                    entries.append({"rawPath": raw_path or "lsp-capabilities.json", "url": url})
        except (OSError, ValueError):
            pass

    # 2. From upstream-qe-reference.md
    upstream_path = REPO_ROOT / "raw" / "assets" / "upstream-qe-reference.md"
    if upstream_path.exists():
        text = upstream_path.read_text(encoding="utf-8")
        urls = SOURCE_URL_RE.findall(text)
        for url in sorted(set(urls)):
            entries.append(
                {
                    "rawPath": repo_relative(upstream_path),
                    "url": url,
                }
            )

    # 3. Stable GitHub links for every raw evidence asset, including the manifest.
    for raw_file in _raw_asset_files():
        raw_rel = repo_relative(raw_file)
        entries.append(
            {
                "rawPath": raw_rel,
                "url": f"https://github.com/{REPOSITORY}/blob/main/{raw_rel}",
            }
        )

    # Deduplicate
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, str]] = []
    for e in entries:
        key = (e["rawPath"], e["url"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


def collect_raw_manifest() -> dict[str, object]:
    """Check the raw/assets manifest descriptor."""
    manifest_path = REPO_ROOT / "raw" / "assets" / "manifest.json"
    return {
        "path": repo_relative(manifest_path),
        "ok": manifest_path.is_file() and manifest_path.stat().st_size > 0,
    }


def build_summary(
    docstrings: list[dict[str, str]],
    wiki_sources: list[dict[str, str]],
    rule_ids: list[dict[str, str]],
    source_urls: list[dict[str, str]],
    raw_manifest: dict[str, object],
) -> dict[str, Any]:
    """Build the summary section."""
    docstrings_linked = sum(
        1
        for item in docstrings
        if (REPO_ROOT / item["path"]).exists() and (REPO_ROOT / item["wikiPath"]).exists()
    )
    broken_wiki_links = sum(1 for item in docstrings if not (REPO_ROOT / item["wikiPath"]).exists())
    wiki_sources_without_raw = sum(
        1 for item in wiki_sources if not (REPO_ROOT / item["rawPath"]).exists()
    )
    return {
        "docstringsTotal": len(docstrings),
        "docstringsLinked": docstrings_linked,
        "brokenWikiLinks": broken_wiki_links,
        "wikiSourcesWithoutRaw": wiki_sources_without_raw,
        "rawManifestFailures": 0 if raw_manifest["ok"] else 1,
        "ruleIdsTotal": len(rule_ids),
        "sourceUrlsTotal": len(source_urls),
        "wikiSourcesTotal": len(wiki_sources),
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def generate_report() -> dict[str, Any]:
    """Generate the full OpenQC v1 traceability report."""
    write_raw_asset_manifest()
    docstrings = collect_docstrings()
    wiki_sources = collect_wiki_sources()
    rule_ids = collect_rule_ids()
    source_urls = collect_source_urls()
    raw_manifest = collect_raw_manifest()
    summary = build_summary(docstrings, wiki_sources, rule_ids, source_urls, raw_manifest)

    git_url = _git_remote_url()

    report: dict[str, Any] = {
        "schemaVersion": "openqc.lsp.traceability.v1",
        "serverId": SERVER_ID,
        "repository": git_url or f"https://github.com/{REPOSITORY}",
        "languageId": LANGUAGE_ID,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "docstrings": docstrings,
        "wikiSources": wiki_sources,
        "ruleIds": rule_ids,
        "sourceUrls": source_urls,
        "rawManifest": raw_manifest,
    }
    return report


def main(argv: list[str] | None = None) -> int:
    """Generate the report and write it to disk."""
    report = generate_report()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Report written to {REPORT_PATH}")
    print(f"  schemaVersion: {report['schemaVersion']}")
    print(f"  serverId: {report['serverId']}")
    print(f"  docstrings: {len(report['docstrings'])} entries")
    print(f"  wikiSources: {len(report['wikiSources'])} entries")
    print(f"  ruleIds: {len(report['ruleIds'])} entries")
    print(f"  sourceUrls: {len(report['sourceUrls'])} entries")
    print(f"  rawManifest: {len(report['rawManifest'])} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

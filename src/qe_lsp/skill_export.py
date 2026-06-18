"""Export the bundled pluggable skill specification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SKILL_SPEC_JSON = (
    '{"schema":"scientific-lsp-skill/v1","name":"qe","software":"qe","display_nam'
    'e":"Quantum ESPRESSO","description":"Quantum ESPRESSO input preflight for pw'
    '.x and related input files.","package":{"name":"qe-lsp","install":"pip insta'
    'll qe-lsp"},"entrypoints":{"server":"qe-lsp","tool":"qe-lsp-tool"},"file_pat'
    'terns":["*.in","*.pw.in","*.relax.in","*.vc-relax.in","*.scf.in","*.nscf.in"'
    ',"*.bands.in","*.ph.in","*.dos.in"],"operations":["capabilities","check","co'
    'ntext","complete","hover","symbols","fix"],"diagnostic_contract":"Diagnostic'
    'Envelope/v1","blocking_policy":{"mode":"warning-only","description":"Use --f'
    'ail-on-blocking when generated inputs must be launch-ready."},"source_proven'
    'ance":[{"kind":"official_docs","label":"Quantum ESPRESSO input descriptions"'
    ',"url":"https://www.quantum-espresso.org/documentation/input-data-descriptio'
    'n/"}]}'
)

SKILL_SPEC: dict[str, Any] = json.loads(SKILL_SPEC_JSON)

SKILL_MD_LINES = [
    '---',
    'name: qe',
    (
        'description: "Quantum ESPRESSO input preflight for pw.x and related input fi'
        'les."'
    ),
    '---',
    '',
    '# Quantum ESPRESSO LSP Skill',
    '',
    (
        'Use this skill when preparing, repairing, or reviewing Quantum ESPRESSO inpu'
        't files before a run. It provides an installable language server and an agen'
        't-facing CLI that reports machine-readable diagnostics.'
    ),
    '',
    '## Scope',
    '',
    (
        '- Input patterns: *.in, *.pw.in, *.relax.in, *.vc-relax.in, *.scf.in, *.nscf'
        '.in, *.bands.in, *.ph.in, *.dos.in'
    ),
    '- Server command: `qe-lsp`',
    '- Agent CLI: `qe-lsp-tool`',
    '- Diagnostic contract: `DiagnosticEnvelope/v1`',
    '',
    '## Installing the checker',
    '',
    '```bash',
    'pip install qe-lsp',
    '```',
    '',
    (
        'This installs the `qe-lsp` language server and the `qe-lsp-tool` agent CLI f'
        'rom the `qe-lsp` Python package.'
    ),
    '',
    '## Useful inspection commands',
    '',
    '```bash',
    'qe-lsp-tool capabilities',
    'qe-lsp-tool skill-spec --format json',
    'qe-lsp-tool skill-export --output ./skill',
    'qe-lsp-tool check <input-file-or-dir> --format json',
    'qe-lsp-tool context <input-file-or-dir> --line 0 --character 0 --format json',
    'qe-lsp-tool hover <input-file-or-dir> --line 0 --character 0 --format json',
    (
        'qe-lsp-tool complete <input-file-or-dir> --line 0 --character 0 --format jso'
        'n'
    ),
    'qe-lsp-tool symbols <input-file-or-dir> --format json',
    'qe-lsp-tool fix <input-file-or-dir> --line 0 --character 0 --format json',
    '```',
    '',
    (
        '`fix` is advisory and must be treated as a preview. Do not blindly apply a r'
        "epair without preserving the user's scientific intent."
    ),
    '',
    '## Validation gate',
    '',
    'Before saying generated inputs are ready, run:',
    '',
    '```bash',
    'qe-lsp-tool check <input-file-or-dir> --format json --fail-on-blocking',
    '```',
    '',
    (
        'Report `commands`, `files_checked`, `tool_available`, `diagnostics`, `blocki'
        'ng_findings`, `readiness`, and `reason`.'
    ),
    '',
    '## Repair rules',
    '',
    '1. Validate first and identify the smallest blocking issue.',
    '2. Fix syntax or schema errors with minimal edits.',
    (
        '3. Preserve scientific settings unless the user explicitly asks to redesign '
        'them.'
    ),
    '4. Re-run the checker after every edit.',
    (
        '5. Separate syntax, schema, semantic, and runtime-log diagnostics in the fin'
        'al report.'
    ),
]
SKILL_MD = "\n".join(SKILL_MD_LINES) + "\n"

REFERENCES_README_LINES = [
    '# Quantum ESPRESSO LSP Skill References',
    '',
    (
        'This directory is reserved for small examples, rule notes, and templates tha'
        't are safe to ship with the Python package. Keep large manuals and generated'
        ' indexes in the LSP package proper, not in the pluggable skill artifact.'
    ),
]
REFERENCES_README = "\n".join(REFERENCES_README_LINES) + "\n"


def _yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if (
        not text
        or any(ch in text for ch in ":#[]{},&*?")
        or text[0] in "-!@`"
        or text.endswith(" ")
        or "\n" in text
    ):
        return json.dumps(text, ensure_ascii=False)
    return text


def _to_yaml(value: object, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}{key}:")
                lines.append(_to_yaml(item, indent + 2))
            else:
                lines.append(f"{pad}{key}: {_yaml_scalar(item)}")
        return "\n".join(lines)
    if isinstance(value, list):
        if not value:
            return f"{pad}[]"
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(_to_yaml(item, indent + 2))
            else:
                lines.append(f"{pad}- {_yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{pad}{_yaml_scalar(value)}"


def skill_spec_text(output_format: str = "json") -> str:
    if output_format == "json":
        return json.dumps(SKILL_SPEC, indent=2, sort_keys=True, ensure_ascii=False)
    if output_format == "yaml":
        return _to_yaml(SKILL_SPEC) + "\n"
    raise ValueError(f"unsupported skill spec format: {output_format}")


def export_skill(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    references_dir = output_dir / "references"
    references_dir.mkdir(exist_ok=True)
    (output_dir / "skill.yaml").write_text(skill_spec_text("yaml"), encoding="utf-8")
    (output_dir / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
    (references_dir / "README.md").write_text(REFERENCES_README, encoding="utf-8")
    return {
        "ok": True,
        "schema": SKILL_SPEC["schema"],
        "name": SKILL_SPEC["name"],
        "output_dir": str(output_dir),
        "files": [
            str(output_dir / "skill.yaml"),
            str(output_dir / "SKILL.md"),
            str(references_dir / "README.md"),
        ],
    }

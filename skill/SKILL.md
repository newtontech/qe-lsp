---
name: qe
description: "Quantum ESPRESSO input preflight for pw.x and related input files."
---

# Quantum ESPRESSO LSP Skill

Use this skill when preparing, repairing, or reviewing Quantum ESPRESSO input files before a run. It provides an installable language server and an agent-facing CLI that reports machine-readable diagnostics.

## Scope

- Input patterns: *.in, *.pw.in, *.relax.in, *.vc-relax.in, *.scf.in, *.nscf.in, *.bands.in, *.ph.in, *.dos.in
- Server command: `qe-lsp`
- Agent CLI: `qe-lsp-tool`
- Diagnostic contract: `DiagnosticEnvelope/v1`

## Installing the checker

```bash
pip install qe-lsp
```

This installs the `qe-lsp` language server and the `qe-lsp-tool` agent CLI from the `qe-lsp` Python package.

## Useful inspection commands

```bash
qe-lsp-tool capabilities
qe-lsp-tool skill-spec --format json
qe-lsp-tool skill-export --output ./skill
qe-lsp-tool check <input-file-or-dir> --format json
qe-lsp-tool context <input-file-or-dir> --line 0 --character 0 --format json
qe-lsp-tool hover <input-file-or-dir> --line 0 --character 0 --format json
qe-lsp-tool complete <input-file-or-dir> --line 0 --character 0 --format json
qe-lsp-tool symbols <input-file-or-dir> --format json
qe-lsp-tool fix <input-file-or-dir> --line 0 --character 0 --format json
```

`fix` is advisory and must be treated as a preview. Do not blindly apply a repair without preserving the user's scientific intent.

## Validation gate

Before saying generated inputs are ready, run:

```bash
qe-lsp-tool check <input-file-or-dir> --format json --fail-on-blocking
```

Report `commands`, `files_checked`, `tool_available`, `diagnostics`, `blocking_findings`, `readiness`, and `reason`.

## Repair rules

1. Validate first and identify the smallest blocking issue.
2. Fix syntax or schema errors with minimal edits.
3. Preserve scientific settings unless the user explicitly asks to redesign them.
4. Re-run the checker after every edit.
5. Separate syntax, schema, semantic, and runtime-log diagnostics in the final report.

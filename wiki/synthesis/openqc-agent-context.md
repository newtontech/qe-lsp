# OpenQC Agent Context

OpenQC consumes `qe-lsp-tool` and `lsp-capabilities.json` to assemble diagnostics, hover, completion, symbols, examples, next-token guidance, and repair-plan hints for `qe` documents.

## LSP Capability Surface

| Capability | Operation | Source Evidence |
|------------|-----------|-----------------|
| Completion | `complete` | Namelist/card keywords from [completion.py](../../raw/assets/constants.py); see [Quick Reference](./quick-reference.md) |
| Hover | `hover` | Parameter docs from [hover.py](../../src/qe_lsp/handlers/hover.py); namelist refs in [control-namelist-reference.md](./control-namelist-reference.md) |
| Diagnostics | `check` | Validation from [validation.py](../../raw/assets/validation.py), lint from [lint.py](../../src/qe_lsp/features/lint.py); [Diagnostic Engine](../concepts/diagnostic-engine-v1.md) |
| Symbols | `symbols` | Namelist/card outline from document symbol handler |
| Fix Preview | `fix` | Code actions from validation and lint rules |
| Navigation | `definition` | Go-to-definition for namelists and cards |
| Blocking Gate | `check` | Warning-only by default (`blockingPolicy.mode: warning-only` in `lsp-capabilities.json`) |

## Source Provenance

The LSP draws domain knowledge from these upstream sources (recorded in `lsp-capabilities.json` → `sourceProvenance`):

- **QE input descriptions**: https://www.quantum-espresso.org/documentation/input-data-description/
- **pw.x reference**: https://www.quantum-espresso.org/Doc/INPUT_PW.html
- **ph.x reference**: https://www.quantum-espresso.org/Doc/INPUT_PH.html
- **DOS tutorial**: https://pranabdas.github.io/espresso/hands-on/dos/
- **Pseudopotential libraries**: https://www.quantum-espresso.org/pseudopotentials/
- **Upstream manifest**: [raw/assets/upstream-qe-reference.md](../../raw/assets/upstream-qe-reference.md)

## Diagnostic Engine

Diagnostics follow `DiagnosticEnvelope/v1` (see `diagnostics/diagnostic-engine-v1.schema.json`). Default blocking policy is `warning-only`.

## Example Inputs

- **Silicon SCF**: [raw/assets/silicon_scf.in](../../raw/assets/silicon_scf.in) — basic SCF calculation
- **CO relax (official test suite)**: [raw/assets/example-carbonyl-relax.in](../../raw/assets/example-carbonyl-relax.in) — geometry optimization
- **Annotated examples**: [raw/assets/qe-examples.md](../../raw/assets/qe-examples.md) — SCF, NSCF, bands, relax, MD, phonon

## 参考来源 (Sources)

- `src/qe_lsp/tool.py`: agent CLI and capability manifest loader
- `raw/assets/DIAGNOSTIC_ENGINE_V1.md`: diagnostic contract
- [LSP Server Architecture](../concepts/lsp-server-architecture.md): server design

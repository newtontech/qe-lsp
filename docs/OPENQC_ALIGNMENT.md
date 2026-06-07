# OpenQC Alignment

`qe-lsp` is the standalone Quantum ESPRESSO language server. `newtontech/OpenQC-VSCode` should expose the same language behavior in VS Code.

## Keep aligned

- File extension handling for `.in`, `.pw.in`, `.relax.in`, `.vc-relax.in`, `.scf.in`, `.nscf.in`, `.bands.in`, `.ph.in`, and `.dos.in`.
- Diagnostics for namelists, cards, keywords, and common invalid values.
- Completion and hover vocabulary for QE input sections.
- Minimal parser fixtures used for smoke tests.

## Release check

Before a public OpenQC release, smoke test one valid and one invalid QE input against this server and the extension.

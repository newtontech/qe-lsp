# Qe lsp

Language Server Protocol implementation for qe quantum chemistry software.

## Features

- Syntax highlighting
- Auto-completion
- Diagnostics
- Hover documentation

## Installation

```bash
pip install qe-lsp
```

## Usage

```bash
qe-lsp
```

## OpenQC Alignment

This repository is part of the newtontech computational chemistry LSP family. `newtontech/OpenQC-VSCode` is the VS Code-facing integration layer for this server.

When changing diagnostics, completions, hover text, file detection, or parser fixtures, also update or open an alignment issue in `OpenQC-VSCode` so the extension behavior stays consistent with `qe-lsp`.

## Development

```bash
git clone https://github.com/newtontech/qe-lsp.git
cd qe-lsp
pip install -e ".[dev]"
```

## License

MIT

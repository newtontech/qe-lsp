# Quantum ESPRESSO LSP

Language Server Protocol implementation for Quantum ESPRESSO quantum chemistry software.

## Features

- **Auto-completion** for QE namelists, keywords, and cards
- **Diagnostics** with error and warning detection
- **Hover documentation** for QE keywords and namelists
- Support for `.in`, `.pw.in`, `.relax.in`, `.vc-relax.in`, `.scf.in`, `.nscf.in`, `.bands.in`, `.ph.in`, and `.dos.in` input files
- Namelist parsing and validation
- Card validation (ATOMIC_SPECIES, ATOMIC_POSITIONS, K_POINTS, CELL_PARAMETERS)
- Pseudopotential and element validation
- Lattice parameter checking

## Installation

```bash
pip install qe-lsp
```

## Usage

Start the language server:

```bash
qe-lsp
```

### Editor Integration

This package provides the language server executable. To use it in an editor,
connect an LSP client to the `qe-lsp` command and register QE input files
with appropriate extensions. The repository does not currently ship a
VS Code extension or TextMate grammar.

Syntax highlighting depends on your editor or extension setup.

## OpenQC Alignment

This repository is part of the newtontech computational chemistry LSP family. `newtontech/OpenQC-VSCode` is the VS Code-facing integration layer for this server.

When changing diagnostics, completions, hover text, file detection, or parser fixtures, also update or open an alignment issue in `OpenQC-VSCode` so the extension behavior stays consistent with `qe-lsp`.

### Supported File Extensions

- `.in` - Generic Quantum ESPRESSO input file
- `.pw.in` - PWscf input file
- `.relax.in` - Geometry relaxation input file
- `.vc-relax.in` - Variable-cell relaxation input file
- `.scf.in` - Self-consistent field calculation input file
- `.nscf.in` - Non-self-consistent field calculation input file
- `.bands.in` - Band structure calculation input file
- `.ph.in` - Phonon calculation input file
- `.dos.in` - Density of states calculation input file

## Development

```bash
git clone https://github.com/newtontech/qe-lsp.git
cd qe-lsp
pip install -e ".[dev]"
```

### Running Tests

```bash
pip install -e ".[dev]"
python -m pytest
```

If your local Python environment is not set up yet, you can reproduce the Python
suite without modifying the project environment:

```bash
uv run --with pytest --with pytest-cov python -m pytest
```

### Release verification

Releases are published from `v*` tag pushes by `.github/workflows/release.yml`.
The workflow checks that the tag, Python package, `VERSION`, and OpenQC
capability manifest agree, then builds the distributions and installs the wheel
into a new virtual environment. The isolated smoke verifies `qe-lsp --help`,
installed version metadata, the agent JSON CLI, and valid, invalid, and
runtime-log fixtures before the OIDC-enabled `pypi` environment can publish.
No long-lived PyPI token is used.

Maintainers can exercise the same artifact smoke before creating a tag:

```bash
python -m pip install build
python -m build
python scripts/verify_release.py --tag v0.1.1
python scripts/smoke_test_wheel.py --wheel dist/qe_lsp-0.1.1-py3-none-any.whl
```

### Code Quality

```bash
black src/ tests/
ruff check src/ tests/
mypy src/ tests/
pre-commit run --all-files
```

See `docs/pr-review-workflow.md` for the merge/modify/hold PR review process
and the parallel Codex subagent review lanes.

## Supported Namelists

### CONTROL Namelist
Controls the execution of the program, including calculation type, convergence criteria, and I/O settings.

### SYSTEM Namelist
Defines the physical system, including crystal structure, atomic positions, basis sets, and pseudopotentials.

### ELECTRONS Namelist
Controls electronic structure calculations, including convergence thresholds and mixing parameters.

### IONS Namelist
Controls ionic relaxation and molecular dynamics.

### CELL Namelist
Controls variable-cell relaxation and cell dynamics.

## Supported Cards

### ATOMIC_SPECIES
Specifies element symbols, masses, and pseudopotential files for each atomic species.

### ATOMIC_POSITIONS
Lists atomic positions in crystal, angstrom, or bohr coordinates.

### K_POINTS
Defines the k-point mesh for Brillouin zone integration.

### CELL_PARAMETERS
Specifies explicit cell vectors when ibrav=0 (free crystal structure).

## Example Input File

```
&CONTROL
  calculation = 'scf'
  restart_mode = 'from_scratch'
  pseudo_dir = './pseudo/'
  outdir = './tmp/'
/

&SYSTEM
  ibrav = 2
  celldm(1) = 10.0
  nat = 2
  ntyp = 1
  ecutwfc = 30.0
/

&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
/

ATOMIC_SPECIES
Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS crystal
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25

K_POINTS automatic
8 8 8 0 0 0
```

## License

MIT

## Changelog

See [LICENSE](LICENSE) for the license text and [CHANGELOG.md](CHANGELOG.md)
for version history.

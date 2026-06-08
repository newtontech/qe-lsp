# Changelog

All notable changes to qe-lsp will be documented in this file.

## [0.1.0] - 2025-01-XX

### Added
- Initial LSP server implementation for Quantum ESPRESSO
- Auto-completion for QE namelists and keywords
- Hover documentation for QE keywords
- Diagnostic support for common errors
- Support for .in, .pw.in, .relax.in, .vc-relax.in, .scf.in, .nscf.in, .bands.in, .ph.in, and .dos.in files
- Namelist parsing and validation
- Card validation (ATOMIC_SPECIES, ATOMIC_POSITIONS, K_POINTS, CELL_PARAMETERS)
- Pseudopotential and element validation
- Lattice parameter checking
- Basic test suite with 92% coverage
- CI/CD pipeline with multi-version Python testing

## [Unreleased]

### Planned
- Code formatting for QE inputs
- Quick fixes for common errors
- Enhanced validation for specific calculation types

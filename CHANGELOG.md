# Change Log

## [0.1.1] - 2026-03-03

### Fixed
- Fixed critical infinite loop bug in parser when parsing numbers, identifiers, and whitespace
- Fixed boolean value parsing for .true., .false., .true, .false
- Fixed scientific notation handling for Fortran-style numbers (1d-10, 2e5)
- Fixed all server tests to properly mock LSP server instances

### Improvements
- Achieved 100% test coverage (127 tests)
- Added test helper function for easier server testing
- Improved parser robustness for edge cases

## [0.1.0] - 2026-03-02

### Added
- Initial release with basic LSP support
- Parser implementation for Quantum ESPRESSO input files (.in)
- LSP server implementation with completion, hover, diagnostics, and document symbols
- Comprehensive parameter documentation for all main namelists
- Card documentation for ATOMIC_SPECIES, ATOMIC_POSITIONS, K_POINTS, CELL_PARAMETERS
- Full test suite with 127 tests covering all modules

### Features
- Syntax highlighting for namelists and cards
- Auto-completion for namelist names, parameters, and values
- Hover documentation with parameter descriptions and types
- Diagnostics for syntax errors, missing required parameters, and unknown parameters
- Document symbols (outline view) showing namelists, parameters, and cards

### Quality
- Fixed code linting issues (ruff)
- Code follows PEP 8 and modern Python best practices
- Type hints throughout the codebase
- Comprehensive test coverage

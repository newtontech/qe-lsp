# Change Log

## [0.1.5] - 2026-03-04

### Fixed
- Removed orphaned code in server.py (stray return statement)
- Code cleanup and formatting improvements

### Improvements
- Maintained 96% test coverage (176 tests passing)
- All LSP features working correctly:
  - Auto-completion for namelists and parameters
  - Hover documentation
  - Diagnostics
  - Document symbols

## [0.1.4] - 2026-03-03

### Added
- Added comprehensive test coverage improvements (test_coverage.py):
  - Tests for __init__.py edge cases (__getattr__ invalid attribute)
  - Parser edge case tests (lexer errors, boolean parsing, number formats)
  - Data module tests (parameter/card documentation edge cases)
  - Server edge case tests (empty documents, position handling)
  - Advanced parser feature tests (complex inputs, scientific notation)
  - Required parameter validation tests

### Improvements
- Test coverage improved from 91% to 96% (176 tests)
- Added 35 new tests covering edge cases and error paths
- Better error handling verification in parser
- Enhanced LSP server robustness testing

## [0.1.3] - 2026-03-03

### Added
- Extended QE card support with additional cards:
  - PSEUDOPOTENTIALS, SPIN_CONSTRAINTS, HUBBARD, HUBBARD_CARD
  - EXTERNALEFIELD, FREE_CHARGE, ATOMIC_COORDS
  - CLIMBING_IMAGES, CONSTRAINTS_INFO, PENALTY_INFO
- Added comprehensive card documentation:
  - OCCUPATIONS card with format specification
  - ATOMIC_FORCES card for external forces
  - CONSTRAINTS card for ionic constraints
  - ATOMIC_VELOCITIES card for MD simulations
  - HUBBARD card for DFT+U calculations
  - EXTERNALEFIELD card for electric fields
- Improved K_POINTS documentation with automatic/crystal format details

### Improvements
- Enhanced parser to recognize more QE input file cards
- Better documentation coverage for LSP hover tooltips
- Test suite stability maintained (141 tests passing, 91% coverage)

## [0.1.2] - 2026-03-03

### Added
- Added tests for docs module (DocFormatter, convenience functions)
- Added test for lazy import of main function
- Added test for AttributeError on invalid attribute access
- Added tests for hover on card names
- Added tests for completion with card names
- Added tests for document symbols with cards
- Added .coveragerc for proper coverage configuration

### Fixed
- Fixed coverage configuration to properly measure source code
- Coverage now correctly reports 91% (141 tests)

### Improvements
- Improved test coverage from 127 to 141 tests
- Added comprehensive documentation tests

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

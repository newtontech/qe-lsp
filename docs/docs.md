# QE-LSP Documentation

## Overview

QE-LSP is a Language Server Protocol implementation for Quantum ESPRESSO input files. It provides
syntax highlighting, auto-completion, diagnostics, and hover documentation for Quantum ESPRESSO
calculations.

## Architecture

### Components

- `server.py` - Main LSP server with feature registration
- `parser.py` - Quantum ESPRESSO input parser
- `validation.py` - Diagnostic checks for QE inputs
- `handlers/` - LSP feature handlers (completion, hover, diagnostics)
- `constants.py` - QE keywords and documentation strings

### Parser Design

The parser processes Quantum ESPRESSO input files incrementally:
1. Detects namelists (blocks starting with `&NAME` and ending with `/`)
2. Extracts card sections (ATOMIC_SPECIES, ATOMIC_POSITIONS, K_POINTS, CELL_PARAMETERS)
3. Parses parameter assignments with `name = value` syntax
4. Tracks duplicate parameters and unclosed namelists

### Validation Strategy

Validation checks are organized by severity:
- **Errors**: Syntax errors, unclosed namelists, missing required cards
- **Warnings**: Invalid values, inconsistent parameters, pseudopotential issues

Common validation checks:
- Unclosed namelists
- Missing cell parameters when ibrav=0
- Lattice constants being ignored for ibrav≠0
- Low ecutrho/ecutwfc ratio
- Pseudopotential element mismatches
- Missing species in ATOMIC_POSITIONS
- Invalid gamma-only k-point offsets

## Development Guidelines

### Adding New Diagnostics

1. Add the diagnostic check in `validation.py`
2. Add test cases in `tests/test_basic.py` or `tests/test_validation_accuracy.py`
3. Update `OPENQC_ALIGNMENT.md` if the diagnostic affects extension behavior

### Adding New Keywords

1. Add keywords to `QE_KEYWORDS` list in `constants.py`
2. Add hover documentation to `QE_HOVER_DOCS`
3. Add completion tests in `tests/test_basic.py`

### Code Quality Standards

- Maintain >80% test coverage (current: 92%)
- Use type hints for all public functions
- Run `pre-commit run --all-files` before committing
- Ensure all tests pass with `pytest`

## Testing

### Test Structure

- `test_basic.py` - Basic LSP functionality tests
- `test_validation_accuracy.py` - Validation accuracy regression tests

### Running Tests

```bash
# Full test suite
pytest

# With coverage
pytest --cov

# Specific test file
pytest tests/test_basic.py
```

## CI/CD

The project uses GitHub Actions for continuous integration:
- Tests on Python 3.9, 3.10, 3.11, 3.12
- Code quality checks (black, ruff, mypy, pre-commit)
- Package building verification

## Future Enhancements

Potential features for future versions:
- Code formatting for QE inputs
- Quick fixes for common errors
- Advanced validation for specific calculation types
- Integration with QE documentation
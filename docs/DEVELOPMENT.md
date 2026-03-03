# Development Guide

This guide provides detailed information for developers who want to contribute to QE-LSP.

## Architecture Overview

QE-LSP consists of three main components:

1. **Parser** (`src/qe_lsp/parser.py`)
   - Parses Quantum ESPRESSO input files
   - Tracks positions for LSP features
   - Validates structure and required parameters

2. **Data** (`src/qe_lsp/data.py`)
   - Parameter documentation
   - Valid values and defaults
   - Formatting functions for hover

3. **Server** (`src/qe_lsp/server.py`)
   - LSP protocol implementation
   - Handles editor requests
   - Manages diagnostics

4. **Docs** (`src/qe_lsp/docs.py`)
   - Documentation formatting utilities
   - Hover text generation

## Parser Architecture

### AST Classes

The parser builds an Abstract Syntax Tree (AST) with these classes:

- `Token` - Lexical token with type, value, position
- `TokenType` - Enum of token types
- `Namelist` - Collection of parameters
- `Card` - Card with data lines
- `QEInputFile` - Complete parsed file

### Parsing Flow

```
Input String
    ↓
Tokenize (Lexer)
    ↓
Parse tokens into AST
    ↓
Validate required parameters
    ↓
Return QEInputFile
```

## LSP Features Implementation

### Hover

1. Get word at cursor position
2. Check if inside namelist
3. Look up parameter documentation
4. Return markdown-formatted hover

### Completion

Three contexts:

1. **Namelist/Card level** - Suggest namelists and cards
2. **Parameter level** - Suggest parameters for current namelist
3. **Value level** - Suggest valid values for parameter

### Diagnostics

Two types:

1. **Errors** - Invalid syntax, unknown namelists/cards, missing required params
2. **Warnings** - Unknown parameters

### Document Symbols

Returns hierarchical symbols:

```
&control (Namespace)
├── calculation (Property)
├── prefix (Property)
└── ...
ATOMIC_SPECIES (Array)
```

## Testing Strategy

### Test Organization

- `test_parser.py` - Parser unit tests (core functionality)
- `test_data.py` - Data module tests (parameter documentation)
- `test_server.py` - LSP server tests (mock-based)
- `test_docs.py` - Documentation formatting tests
- `test_basic.py` - Basic import and export tests
- `test_coverage.py` - Edge case and error handling tests

### Coverage Requirements

**95% code coverage** is required. Use `# pragma: no cover` sparingly for:

- `__repr__` methods
- Abstract method stubs
- Unreachable code
- LSP server initialization edge cases

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/qe_lsp --cov-report=term-missing

# Run specific test file
pytest tests/test_parser.py -v

# Run with verbose output
pytest -v --tb=short
```

### Test Fixtures

Common test data is in `conftest.py`:

- `sample_qe_input` - Full example
- `minimal_qe_input` - Minimal valid input
- `invalid_qe_input` - Contains errors
- `empty_qe_input` - Edge case
- `comment_only_input` - Edge case

### Writing Tests

Follow these patterns:

```python
def test_feature_description(self):
    """Test that feature does X."""
    # Arrange
    input_data = "..."
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected
```

## Adding New Features

### Adding a New LSP Feature

1. Add handler function in `server.py`:

```python
def _new_feature_handler(params: NewFeatureParams) -> Result:
    """Handle new feature request."""
    srv = _get_server()
    doc = srv.workspace.get_text_document(params.text_document.uri)
    # ... implementation
    return result

# Register in _setup_features
srv.feature("textDocument/newFeature")(_new_feature_handler)
```

2. Add tests in `test_server.py`

3. Update documentation

### Adding New Parameters

1. Edit `src/qe_lsp/data.py`
2. Add to appropriate namelist dictionary
3. Include:
   - `description` - Human-readable description
   - `type` - Parameter type
   - `default` - Default value (if any)
   - `values` - Valid options for enums
   - `required` - Whether parameter is required

4. Add test in `test_data.py`

## Debugging

### Enable Verbose Logging

Set environment variable:

```bash
export PYGLS_DEBUG=1
qe-lsp
```

### Test Against Real Input

Create a test file:

```python
from qe_lsp.parser import parse_qe_input

with open("test.in") as f:
    result = parse_qe_input(f.read())

for name, namelist in result.namelists.items():
    print(f"Namelist: {name}")
    for param_name, value in namelist.parameters.items():
        print(f"  {param_name} = {value}")
```

## Release Process

1. Update version in `src/qe_lsp/__init__.py`
2. Update CHANGELOG.md
3. Run full test suite: `pytest`
4. Check coverage: `pytest --cov=src/qe_lsp`
5. Create git tag
6. Build and publish to PyPI

## Current Statistics

- **Tests**: 176 tests passing
- **Coverage**: 96% (551 statements, 15 missed)
- **Modules**: 5 Python modules
- **Supported Namelists**: 5 (control, system, electrons, ions, cell)
- **Supported Cards**: 15+

## Common Issues

### Import Errors

Make sure to install in editable mode:

```bash
pip install -e ".[dev]"
```

### Type Errors

Run mypy to check types:

```bash
mypy src
```

### Test Failures

Run with verbose output:

```bash
pytest -v --tb=short
```

## Code Style

- Line length: 100 characters
- Use black for formatting
- Use isort for import sorting
- Add type hints to all functions
- Write docstrings for all public functions

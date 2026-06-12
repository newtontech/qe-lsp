"""Quantum ESPRESSO validation checks that produce LSP diagnostics."""


from lsprotocol import types

from .parser import (
    Parameter,
)


def _range_for(line: int, character: int, length: int = 1) -> types.Range:
    return types.Range(
        start=types.Position(line=line, character=character),
        end=types.Position(line=line, character=character + max(1, length)),
    )


def _diagnostic(
    line: int,
    character: int,
    message: str,
    severity: types.DiagnosticSeverity,
    length: int = 1,
) -> types.Diagnostic:
    return types.Diagnostic(
        range=_range_for(line, character, length),
        severity=severity,
        message=message,
        source="qe-lsp",
    )


def _parameter_diagnostic(
    parameter: Parameter,
    message: str,
    severity: types.DiagnosticSeverity,
) -> types.Diagnostic:
    return _diagnostic(
        parameter.line,
        parameter.character,
        message,
        severity,
        len(parameter.name),
    )

"""Quantum ESPRESSO validation checks that produce LSP diagnostics."""

from typing import List

from lsprotocol import types

from .parser import (
    Parameter,
    declared_species,
    normalize_value,
    parse_number,
    parse_qe_input,
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


def validate_qe_input(text: str) -> List[types.Diagnostic]:
    parsed = parse_qe_input(text)
    diagnostics: List[types.Diagnostic] = []

    if parsed.unclosed_namelist is not None:
        diagnostics.append(
            _parameter_diagnostic(
                parsed.unclosed_namelist,
                f"Unclosed namelist {parsed.unclosed_namelist.name}; expected '/'.",
                types.DiagnosticSeverity.Error,
            )
        )

    for parameter in parsed.duplicate_parameters:
        diagnostics.append(
            _parameter_diagnostic(
                parameter,
                f"Duplicate parameter {parameter.name}.",
                types.DiagnosticSeverity.Error,
            )
        )

    system = parsed.namelists.get("&SYSTEM", {})
    ibrav = system.get("ibrav")
    if ibrav is not None:
        ibrav_value = normalize_value(ibrav.value)
        if ibrav_value == "0" and "CELL_PARAMETERS" not in parsed.cards:
            diagnostics.append(
                _parameter_diagnostic(
                    ibrav,
                    "ibrav = 0 requires an explicit CELL_PARAMETERS card.",
                    types.DiagnosticSeverity.Error,
                )
            )
        if ibrav_value != "0":
            for lattice_name in ("a", "b", "c", "cosab", "cosac", "cosbc"):
                lattice_parameter = system.get(lattice_name)
                if lattice_parameter is not None:
                    diagnostics.append(
                        _parameter_diagnostic(
                            lattice_parameter,
                            f"{lattice_name} is ignored when ibrav is not 0.",
                            types.DiagnosticSeverity.Warning,
                        )
                    )

    ecutwfc = system.get("ecutwfc")
    ecutrho = system.get("ecutrho")
    if ecutwfc is not None and ecutrho is not None:
        wfc_value = parse_number(ecutwfc.value)
        rho_value = parse_number(ecutrho.value)
        required_ratio = 8 if _uses_paw_pseudopotential(parsed) else 4
        if (
            wfc_value is not None
            and rho_value is not None
            and rho_value < required_ratio * wfc_value
        ):
            diagnostics.append(
                _parameter_diagnostic(
                    ecutrho,
                    f"ecutrho should normally be at least {required_ratio}x ecutwfc.",
                    types.DiagnosticSeverity.Warning,
                )
            )

    electrons = parsed.namelists.get("&ELECTRONS", {})
    mixing_beta = electrons.get("mixing_beta")
    if mixing_beta is not None:
        mixing_value = parse_number(mixing_beta.value)
        if mixing_value is not None and mixing_value > 0.7:
            diagnostics.append(
                _parameter_diagnostic(
                    mixing_beta,
                    "mixing_beta above 0.7 may make large systems hard to converge.",
                    types.DiagnosticSeverity.Warning,
                )
            )

    diagnostics.extend(_validate_pseudopotentials(text))
    diagnostics.extend(_validate_atomic_positions(text))
    diagnostics.extend(_validate_k_points(text))
    return diagnostics


def _validate_pseudopotentials(text: str) -> List[types.Diagnostic]:
    parsed = parse_qe_input(text)
    diagnostics: List[types.Diagnostic] = []
    functionals = set()

    for row in parsed.cards.get("ATOMIC_SPECIES", []):
        if len(row.values) < 2:
            continue
        pseudo_file = row.values[1]
        pseudo_prefix = pseudo_file.split(".", 1)[0].lower()
        parts = pseudo_file.lower().split(".")
        if len(parts) > 1:
            functionals.add(parts[1])
        if pseudo_prefix != row.symbol.lower():
            diagnostics.append(
                _diagnostic(
                    row.line,
                    0,
                    f"Pseudopotential {pseudo_file} does not appear to match element {row.symbol}.",
                    types.DiagnosticSeverity.Error,
                    len(row.symbol),
                )
            )

    if len(functionals) > 1:
        first_row = parsed.cards.get("ATOMIC_SPECIES", [])[0]
        diagnostics.append(
            _diagnostic(
                first_row.line,
                0,
                "Mixed pseudopotential functional families may be inconsistent.",
                types.DiagnosticSeverity.Warning,
                len(first_row.symbol),
            )
        )

    return diagnostics


def _validate_atomic_positions(text: str) -> List[types.Diagnostic]:
    parsed = parse_qe_input(text)
    species = declared_species(parsed)
    diagnostics: List[types.Diagnostic] = []
    header = parsed.card_headers.get("ATOMIC_POSITIONS", "")

    for row in parsed.cards.get("ATOMIC_POSITIONS", []):
        if row.symbol not in species:
            diagnostics.append(
                _diagnostic(
                    row.line,
                    0,
                    f"Element {row.symbol} is missing from ATOMIC_SPECIES.",
                    types.DiagnosticSeverity.Error,
                    len(row.symbol),
                )
            )
        if "CRYSTAL" in header:
            coordinates = [parse_number(value) for value in row.values[:3]]
            if any(
                value is not None and (value < 0 or value > 1) for value in coordinates
            ):
                diagnostics.append(
                    _diagnostic(
                        row.line,
                        0,
                        "Crystal coordinates should normally be between 0 and 1.",
                        types.DiagnosticSeverity.Warning,
                        len(row.symbol),
                    )
                )

    return diagnostics


def _validate_k_points(text: str) -> List[types.Diagnostic]:
    parsed = parse_qe_input(text)
    diagnostics: List[types.Diagnostic] = []
    header = parsed.card_headers.get("K_POINTS", "")

    rows = parsed.cards.get("K_POINTS", [])

    if "GAMMA" not in header:
        if "AUTOMATIC" in header and rows:
            row = rows[0]
            grid = [parse_number(value) for value in [row.symbol] + row.values[:2]]
            if any(value is not None and value < 3 for value in grid):
                diagnostics.append(
                    _diagnostic(
                        row.line,
                        0,
                        "K_POINTS automatic grid is very coarse for production calculations.",
                        types.DiagnosticSeverity.Warning,
                        len(row.symbol),
                    )
                )
        return diagnostics

    if not rows:
        return diagnostics

    row = rows[0]
    values = row.values
    offsets = values[2:5] if len(values) >= 5 else []
    if any(value != "0" for value in offsets):
        diagnostics.append(
            _diagnostic(
                row.line,
                0,
                "K_POINTS {gamma} should not include a non-zero offset.",
                types.DiagnosticSeverity.Warning,
                len(row.symbol),
            )
        )

    return diagnostics


def _uses_paw_pseudopotential(parsed) -> bool:
    for row in parsed.cards.get("ATOMIC_SPECIES", []):
        if len(row.values) >= 2 and "paw" in row.values[1].lower():
            return True
    return False

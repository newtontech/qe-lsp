"""Type-aware validation for Quantum ESPRESSO keyword values.

Validates scalar types (string, integer, float, boolean), enum values,
physical units, and required-section constraints.  Produces LSP diagnostics
with source ``qe-lsp-typecheck`` so that consumers can distinguish these
from structural lint and parser diagnostics.

The schema metadata lives in ``KEYWORD_SCHEMA`` which is designed to be
incrementally extended as coverage grows without breaking existing checks.
"""

from __future__ import annotations

from typing import Any

from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
)

from ..parser import Parameter, normalize_value, parse_number, parse_qe_input
from ..text import strip_inline_comment

# ------------------------------------------------------------------
# Rule codes  (QE-TExxx = typecheck error, QE-TWxxx = typecheck warning)
# ------------------------------------------------------------------

RULE_TYPE_MISMATCH = "QE-TE001"
RULE_ENUM_INVALID = "QE-TE002"
RULE_UNIT_UNKNOWN = "QE-TE003"
RULE_REQUIRED_SECTION_MISSING = "QE-TE004"
RULE_NUMERIC_RANGE = "QE-TW001"

# ------------------------------------------------------------------
# Value-type enumeration
# ------------------------------------------------------------------

TYPE_INTEGER = "integer"
TYPE_FLOAT = "float"
TYPE_STRING = "string"
TYPE_BOOLEAN = "boolean"
TYPE_PATH = "path"

# ------------------------------------------------------------------
# Unit families
# ------------------------------------------------------------------

ENERGY_UNITS = frozenset({"ry", "ha", "ev", "kry", "kha", "kev"})
LENGTH_UNITS = frozenset({"bohr", "ang", "angstrom", "alat", "crystal"})
TIME_UNITS = frozenset({"s", "ps", "fs", "ry"})
MASS_UNITS = frozenset({"amu", "ry"})
PRESSURE_UNITS = frozenset({"kbar", "gpa", "ry"})

ALL_KNOWN_UNITS = ENERGY_UNITS | LENGTH_UNITS | TIME_UNITS | MASS_UNITS | PRESSURE_UNITS

# ------------------------------------------------------------------
# Keyword schema
# ------------------------------------------------------------------

#: Each entry maps a keyword to a dict with optional keys:
#:   ``type``  - expected value type (one of TYPE_* constants)
#:   ``enum``  - frozenset of valid lower-case string values
#:   ``units`` - frozenset of valid unit families (e.g. ENERGY_UNITS)
#:   ``min``   - numeric minimum (inclusive) for range checks
#:   ``max``   - numeric maximum (inclusive) for range checks
KEYWORD_SCHEMA: dict[str, dict[str, Any]] = {
    # &CONTROL
    "calculation": {
        "type": TYPE_STRING,
        "enum": frozenset(
            {
                "scf",
                "nscf",
                "bands",
                "relax",
                "md",
                "vc-relax",
                "vc-md",
            }
        ),
    },
    "title": {"type": TYPE_STRING},
    "verbosity": {"type": TYPE_STRING, "enum": frozenset({"high", "low", "default", "xml"})},
    "restart_mode": {
        "type": TYPE_STRING,
        "enum": frozenset({"from_scratch", "restart"}),
    },
    "wf_collect": {"type": TYPE_BOOLEAN},
    "nstep": {"type": TYPE_INTEGER, "min": 0},
    "iprint": {"type": TYPE_INTEGER, "min": 0},
    "tstress": {"type": TYPE_BOOLEAN},
    "tprnfor": {"type": TYPE_BOOLEAN},
    "dt": {"type": TYPE_FLOAT, "min": 0},
    "outdir": {"type": TYPE_PATH},
    "wfcdir": {"type": TYPE_PATH},
    "prefix": {"type": TYPE_STRING},
    "max_seconds": {"type": TYPE_FLOAT, "min": 0},
    "etot_conv_thr": {"type": TYPE_FLOAT, "min": 0},
    "forc_conv_thr": {"type": TYPE_FLOAT, "min": 0},
    "disk_io": {
        "type": TYPE_STRING,
        "enum": frozenset({"low", "medium", "high", "none"}),
    },
    "pseudo_dir": {"type": TYPE_PATH},
    "tefield": {"type": TYPE_BOOLEAN},
    "dipfield": {"type": TYPE_BOOLEAN},
    "lelfield": {"type": TYPE_BOOLEAN},
    "nberrycyc": {"type": TYPE_INTEGER, "min": 0},
    "lorbm": {"type": TYPE_BOOLEAN},
    "lberry": {"type": TYPE_BOOLEAN},
    "gdir": {"type": TYPE_INTEGER, "min": 1, "max": 3},
    "nppstr": {"type": TYPE_INTEGER, "min": 0},
    "lfcpopt": {"type": TYPE_BOOLEAN},
    "gate": {"type": TYPE_BOOLEAN},
    "plane_axis": {"type": TYPE_INTEGER, "min": 1, "max": 3},
    # &SYSTEM
    "ibrav": {"type": TYPE_INTEGER, "min": 0, "max": 14},
    "a": {"type": TYPE_FLOAT, "min": 0, "units": LENGTH_UNITS},
    "b": {"type": TYPE_FLOAT, "min": 0, "units": LENGTH_UNITS},
    "c": {"type": TYPE_FLOAT, "min": 0, "units": LENGTH_UNITS},
    "cosab": {"type": TYPE_FLOAT, "min": -1.0, "max": 1.0},
    "cosac": {"type": TYPE_FLOAT, "min": -1.0, "max": 1.0},
    "cosbc": {"type": TYPE_FLOAT, "min": -1.0, "max": 1.0},
    "nat": {"type": TYPE_INTEGER, "min": 1},
    "ntyp": {"type": TYPE_INTEGER, "min": 1},
    "nbnd": {"type": TYPE_INTEGER, "min": 1},
    "tot_charge": {"type": TYPE_FLOAT},
    "tot_magnetization": {"type": TYPE_FLOAT, "min": 0},
    "ecutwfc": {"type": TYPE_FLOAT, "min": 0, "units": ENERGY_UNITS},
    "ecutrho": {"type": TYPE_FLOAT, "min": 0, "units": ENERGY_UNITS},
    "occupations": {
        "type": TYPE_STRING,
        "enum": frozenset(
            {
                "smearing",
                "tetrahedra",
                "tetrahedra_lin",
                "tetrahedra_opt",
                "fixed",
                "from_input",
            }
        ),
    },
    "degauss": {"type": TYPE_FLOAT, "min": 0, "units": ENERGY_UNITS},
    "smearing": {
        "type": TYPE_STRING,
        "enum": frozenset(
            {
                "gaussian",
                "methfessel-paxton",
                "mp",
                "mv",
                "fermi-dirac",
                "fd",
            }
        ),
    },
    "nspin": {"type": TYPE_INTEGER, "enum": frozenset({"1", "2", "4"})},
    "starting_magnetization": {"type": TYPE_FLOAT, "min": -1.0, "max": 1.0},
    "nosym": {"type": TYPE_BOOLEAN},
    "nosym_evc": {"type": TYPE_BOOLEAN},
    "noinv": {"type": TYPE_BOOLEAN},
    "no_t_rev": {"type": TYPE_BOOLEAN},
    "force_symmorphic": {"type": TYPE_BOOLEAN},
    "use_all_frac": {"type": TYPE_BOOLEAN},
    "noncolin": {"type": TYPE_BOOLEAN},
    "lspinorb": {"type": TYPE_BOOLEAN},
    "lda_plus_u": {"type": TYPE_BOOLEAN},
    "lda_plus_u_kind": {"type": TYPE_INTEGER, "min": 0, "max": 1},
    # &ELECTRONS
    "conv_thr": {"type": TYPE_FLOAT, "min": 0},
    "niter": {"type": TYPE_INTEGER, "min": 1},
    "electron_maxstep": {"type": TYPE_INTEGER, "min": 0},
    "scf_must_converge": {"type": TYPE_BOOLEAN},
    "diagonalization": {
        "type": TYPE_STRING,
        "enum": frozenset(
            {
                "david",
                "cg",
                "ppcg",
                "paro",
                "rmm-davidson",
                "rmm-paro",
            }
        ),
    },
    "mixing_mode": {
        "type": TYPE_STRING,
        "enum": frozenset({"plain", "tf", "local-tf"}),
    },
    "mixing_beta": {"type": TYPE_FLOAT, "min": 0.0, "max": 1.0},
    "mixing_ndim": {"type": TYPE_INTEGER, "min": 1},
    "mixing_gg0": {"type": TYPE_FLOAT, "min": 0},
    "diago_thr_init": {"type": TYPE_FLOAT, "min": 0},
    "diago_cg_maxiter": {"type": TYPE_INTEGER, "min": 1},
    "diago_david_ndim": {"type": TYPE_INTEGER, "min": 1},
    "diago_full_acc": {"type": TYPE_BOOLEAN},
    "startingpot": {"type": TYPE_STRING, "enum": frozenset({"atomic", "file"})},
    "startingwfc": {
        "type": TYPE_STRING,
        "enum": frozenset({"atomic", "atomic+random", "random", "file"}),
    },
    "real_space": {"type": TYPE_BOOLEAN},
    "tqr": {"type": TYPE_BOOLEAN},
    "efield": {"type": TYPE_FLOAT},
    # &IONS
    "ion_dynamics": {
        "type": TYPE_STRING,
        "enum": frozenset({"none", "bfgs", "damp", "verlet", "langevin", "beeman"}),
    },
    "ion_positions": {"type": TYPE_STRING, "enum": frozenset({"default", "from_input"})},
    "pot_extrapolation": {
        "type": TYPE_STRING,
        "enum": frozenset(
            {
                "none",
                "atomic",
                "first_order",
                "second_order",
            }
        ),
    },
    "wfc_extrapolation": {
        "type": TYPE_STRING,
        "enum": frozenset(
            {
                "none",
                "atomic",
                "first_order",
                "second_order",
            }
        ),
    },
    "remove_rigid_rot": {"type": TYPE_BOOLEAN},
    "bfgs_ndim": {"type": TYPE_INTEGER, "min": 1},
    "bfgs_w1": {"type": TYPE_FLOAT},
    "bfgs_w2": {"type": TYPE_FLOAT},
    "trust_radius_max": {"type": TYPE_FLOAT, "min": 0},
    "trust_radius_min": {"type": TYPE_FLOAT, "min": 0},
    "trust_radius_init": {"type": TYPE_FLOAT, "min": 0},
    "upscale": {"type": TYPE_FLOAT, "min": 0},
    "ion_nstepe": {"type": TYPE_INTEGER, "min": 0},
    # &CELL
    "cell_dynamics": {
        "type": TYPE_STRING,
        "enum": frozenset({"none", "sd", "damp-pr", "damp-w", "bfgs", "pr", "w"}),
    },
    "press": {"type": TYPE_FLOAT, "min": 0, "units": PRESSURE_UNITS},
    "wmass": {"type": TYPE_FLOAT, "min": 0},
    "cell_factor": {"type": TYPE_FLOAT, "min": 0},
    "press_conv_thr": {"type": TYPE_FLOAT, "min": 0},
    "cell_dofree": {
        "type": TYPE_STRING,
        "enum": frozenset(
            {
                "all",
                "x",
                "y",
                "z",
                "xy",
                "xz",
                "yz",
                "xyz",
                "shape",
                "volume",
                "2dxy",
                "2dshape",
            }
        ),
    },
    "isotropic": {"type": TYPE_BOOLEAN},
    "fix_volume": {"type": TYPE_BOOLEAN},
    "fix_area": {"type": TYPE_BOOLEAN},
}

# ------------------------------------------------------------------
# Boolean parsing
# ------------------------------------------------------------------

_TRUE_VALUES = frozenset({".true.", "true", "t", ".t."})
_FALSE_VALUES = frozenset({".false.", "false", "f", ".f."})


def _is_boolean(value: str) -> bool:
    """Return True if *value* is a valid QE boolean literal."""
    normalized = normalize_value(value)
    return normalized in _TRUE_VALUES or normalized in _FALSE_VALUES


def _is_integer(value: str) -> bool:
    """Return True if *value* can be parsed as an integer."""
    normalized = normalize_value(value).replace("d", "e")
    try:
        float_val = float(normalized)
        return float_val == int(float_val)
    except (ValueError, OverflowError):
        return False


def _is_float(value: str) -> bool:
    """Return True if *value* can be parsed as a float."""
    normalized = normalize_value(value).replace("d", "e")
    try:
        float(normalized)
        return True
    except (ValueError, OverflowError):
        return False


def _make_diagnostic(
    param: Parameter,
    message: str,
    severity: DiagnosticSeverity,
    code: str,
    length: int | None = None,
) -> Diagnostic:
    """Create a Diagnostic anchored to *param*."""
    span = length if length is not None else len(param.name)
    return Diagnostic(
        range=Range(
            start=Position(line=param.line, character=param.character),
            end=Position(line=param.line, character=param.character + max(1, span)),
        ),
        severity=severity,
        message=message,
        source="qe-lsp-typecheck",
        code=code,
    )


def _extract_unit_from_line(
    lines: list[str],
    param: Parameter,
) -> str | None:
    """Extract a unit suffix from the raw line containing *param*.

    QE values can be ``60.0 ry`` where the parser only captures ``60.0``.
    This method looks at the full line after the ``=`` to find a trailing
    alphabetic unit token.
    """
    if param.line >= len(lines):
        return None
    raw_line = strip_inline_comment(lines[param.line])
    eq_pos = raw_line.find("=")
    if eq_pos < 0:
        return None
    rhs = raw_line[eq_pos + 1 :].strip()
    # Strip surrounding quotes from the first token
    rhs = rhs.strip("'\"")
    parts = rhs.split()
    if len(parts) < 2:
        return None
    # The unit is the last token if it is purely alphabetic
    candidate = parts[-1]
    if candidate.isalpha():
        return candidate.lower()
    return None


# ------------------------------------------------------------------
# Typecheck provider
# ------------------------------------------------------------------


class TypecheckProvider:
    """Type-aware validation for Quantum ESPRESSO input values.

    Checks:
    - Scalar value types (string, integer, float, boolean, path)
    - Enum values against known allowed sets
    - Physical unit suffixes
    - Numeric range constraints
    - Required-section presence when specific keywords are used
    """

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def typecheck(self, text: str) -> list[Diagnostic]:
        """Run all typecheck rules on *text* and return diagnostics."""
        parsed = parse_qe_input(text)
        diagnostics: list[Diagnostic] = []

        self._check_keyword_types(parsed, diagnostics)
        self._check_enum_values(parsed, diagnostics)
        self._check_units(parsed, text, diagnostics)
        self._check_numeric_ranges(parsed, diagnostics)
        self._check_required_sections(parsed, diagnostics)

        return diagnostics

    def snapshot(self, text: str) -> list[dict[str, Any]]:
        """Return a JSON-serialisable snapshot of typecheck diagnostics."""
        diagnostics = self.typecheck(text)
        items = [_serialise(d) for d in diagnostics]
        items.sort(key=lambda d: (d["range"]["start"]["line"], d["range"]["start"]["character"]))
        return items

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _check_keyword_types(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Validate that keyword values match their expected scalar type."""
        for _namelist_name, params in parsed.namelists.items():
            for _param_name, param in params.items():
                schema = KEYWORD_SCHEMA.get(_param_name)
                if schema is None:
                    continue
                expected_type = schema.get("type")
                if expected_type is None:
                    continue
                self._validate_type(param, expected_type, diagnostics)

    def _validate_type(
        self,
        param: Parameter,
        expected_type: str,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Check a single parameter value against its expected type."""
        raw_value = param.value.strip().strip("'\"")

        if expected_type == TYPE_BOOLEAN:
            if not _is_boolean(param.value):
                diagnostics.append(
                    _make_diagnostic(
                        param,
                        f"Expected boolean for '{param.name}', got '{raw_value}'. "
                        f"Use .true. or .false.",
                        DiagnosticSeverity.Error,
                        RULE_TYPE_MISMATCH,
                    )
                )

        elif expected_type == TYPE_INTEGER:
            if not _is_integer(param.value):
                diagnostics.append(
                    _make_diagnostic(
                        param,
                        f"Expected integer for '{param.name}', got '{raw_value}'.",
                        DiagnosticSeverity.Error,
                        RULE_TYPE_MISMATCH,
                    )
                )

        elif expected_type == TYPE_FLOAT:
            if not _is_float(param.value):
                diagnostics.append(
                    _make_diagnostic(
                        param,
                        f"Expected numeric value for '{param.name}', got '{raw_value}'.",
                        DiagnosticSeverity.Error,
                        RULE_TYPE_MISMATCH,
                    )
                )

        elif expected_type == TYPE_STRING:
            # Strings in QE are always valid; enum validation is separate.
            pass

        elif expected_type == TYPE_PATH:
            if not raw_value:
                diagnostics.append(
                    _make_diagnostic(
                        param,
                        f"Expected file path for '{param.name}', got empty value.",
                        DiagnosticSeverity.Error,
                        RULE_TYPE_MISMATCH,
                    )
                )

    def _check_enum_values(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Validate enum-like keywords against their allowed value sets."""
        for _namelist_name, params in parsed.namelists.items():
            for _param_name, param in params.items():
                schema = KEYWORD_SCHEMA.get(_param_name)
                if schema is None:
                    continue
                valid_values = schema.get("enum")
                if valid_values is None:
                    continue
                normalized = normalize_value(param.value)
                if normalized not in valid_values:
                    raw_display = param.value.strip().strip("'\"")
                    valid_str = ", ".join(sorted(valid_values))
                    diagnostics.append(
                        _make_diagnostic(
                            param,
                            f"Invalid value '{raw_display}' for '{_param_name}'. "
                            f"Valid: {valid_str}.",
                            DiagnosticSeverity.Error,
                            RULE_ENUM_INVALID,
                        )
                    )

    def _check_units(
        self,
        parsed: Any,
        text: str,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Validate unit suffixes on keywords that accept physical units.

        The parser captures only the first token after ``=`` as the value,
        so unit suffixes are extracted from the raw line text instead.
        """
        lines = text.splitlines()
        for _namelist_name, params in parsed.namelists.items():
            for _param_name, param in params.items():
                schema = KEYWORD_SCHEMA.get(_param_name)
                if schema is None:
                    continue
                allowed_units = schema.get("units")
                if allowed_units is None:
                    continue

                unit = _extract_unit_from_line(lines, param)
                if unit is None:
                    continue

                if unit not in allowed_units:
                    valid_str = ", ".join(sorted(allowed_units))
                    if unit in ALL_KNOWN_UNITS:
                        diagnostics.append(
                            _make_diagnostic(
                                param,
                                f"Unit '{unit}' is not valid for '{_param_name}'. "
                                f"Expected one of: {valid_str}.",
                                DiagnosticSeverity.Error,
                                RULE_UNIT_UNKNOWN,
                            )
                        )
                    else:
                        diagnostics.append(
                            _make_diagnostic(
                                param,
                                f"Unknown unit '{unit}' for '{_param_name}'. "
                                f"Known units: {valid_str}.",
                                DiagnosticSeverity.Error,
                                RULE_UNIT_UNKNOWN,
                            )
                        )

    def _check_numeric_ranges(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Check numeric values against min/max range constraints."""
        for _namelist_name, params in parsed.namelists.items():
            for _param_name, param in params.items():
                schema = KEYWORD_SCHEMA.get(_param_name)
                if schema is None:
                    continue
                min_val = schema.get("min")
                max_val = schema.get("max")
                if min_val is None and max_val is None:
                    continue

                numeric_value = parse_number(param.value)
                if numeric_value is None:
                    continue

                if min_val is not None and numeric_value < min_val:
                    diagnostics.append(
                        _make_diagnostic(
                            param,
                            f"Value {numeric_value} for '{_param_name}' is below "
                            f"minimum {min_val}.",
                            DiagnosticSeverity.Warning,
                            RULE_NUMERIC_RANGE,
                        )
                    )
                if max_val is not None and numeric_value > max_val:
                    diagnostics.append(
                        _make_diagnostic(
                            param,
                            f"Value {numeric_value} for '{_param_name}' exceeds "
                            f"maximum {max_val}.",
                            DiagnosticSeverity.Warning,
                            RULE_NUMERIC_RANGE,
                        )
                    )

    def _check_required_sections(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Check that required sections are present when trigger keywords exist."""
        system = parsed.namelists.get("&SYSTEM", {})
        control = parsed.namelists.get("&CONTROL", {})

        # Check ibrav = 0 requires CELL_PARAMETERS
        ibrav = system.get("ibrav")
        if ibrav is not None:
            ibrav_val = normalize_value(ibrav.value)
            if ibrav_val == "0" and "CELL_PARAMETERS" not in parsed.cards:
                diagnostics.append(
                    _make_diagnostic(
                        ibrav,
                        "ibrav = 0 requires an explicit CELL_PARAMETERS card.",
                        DiagnosticSeverity.Error,
                        RULE_REQUIRED_SECTION_MISSING,
                    )
                )

        # Check nat requires ATOMIC_SPECIES and ATOMIC_POSITIONS
        nat = system.get("nat")
        if nat is not None:
            nat_val = normalize_value(nat.value)
            try:
                nat_int = int(float(nat_val))
                if nat_int > 0:
                    if "ATOMIC_SPECIES" not in parsed.cards:
                        diagnostics.append(
                            _make_diagnostic(
                                nat,
                                "nat is set but ATOMIC_SPECIES card is missing.",
                                DiagnosticSeverity.Error,
                                RULE_REQUIRED_SECTION_MISSING,
                            )
                        )
                    if "ATOMIC_POSITIONS" not in parsed.cards:
                        diagnostics.append(
                            _make_diagnostic(
                                nat,
                                "nat is set but ATOMIC_POSITIONS card is missing.",
                                DiagnosticSeverity.Error,
                                RULE_REQUIRED_SECTION_MISSING,
                            )
                        )
            except (ValueError, OverflowError):
                pass

        # Check vc-relax / vc-md require &CELL
        calc = control.get("calculation")
        if calc is not None:
            calc_val = normalize_value(calc.value)
            if calc_val in ("vc-relax", "vc-md") and "&CELL" not in parsed.namelists:
                diagnostics.append(
                    _make_diagnostic(
                        calc,
                        f"calculation = '{calc_val}' requires the &CELL namelist.",
                        DiagnosticSeverity.Error,
                        RULE_REQUIRED_SECTION_MISSING,
                    )
                )


# ------------------------------------------------------------------
# Serialisation helper
# ------------------------------------------------------------------

_SEVERITY_LABELS: dict[int, str] = {
    DiagnosticSeverity.Error: "Error",
    DiagnosticSeverity.Warning: "Warning",
    DiagnosticSeverity.Information: "Information",
    DiagnosticSeverity.Hint: "Hint",
}


def _serialise(diagnostic: Diagnostic) -> dict[str, Any]:
    """Convert a typecheck Diagnostic to a JSON-friendly dict."""
    severity_value = (
        diagnostic.severity if diagnostic.severity is not None else DiagnosticSeverity.Error
    )
    return {
        "range": {
            "start": {
                "line": diagnostic.range.start.line,
                "character": diagnostic.range.start.character,
            },
            "end": {
                "line": diagnostic.range.end.line,
                "character": diagnostic.range.end.character,
            },
        },
        "severity": _SEVERITY_LABELS.get(severity_value, "Information"),
        "source": diagnostic.source or "qe-lsp-typecheck",
        "code": str(diagnostic.code) if diagnostic.code is not None else None,
        "message": diagnostic.message,
    }


__all__ = ["TypecheckProvider"]

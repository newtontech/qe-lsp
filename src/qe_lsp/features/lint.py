"""Schema-aware static lint rules for Quantum ESPRESSO input files.

Produces LSP diagnostics with stable rule codes so that automated coding
agents and CI pipelines can filter and act on specific categories of
findings.  All checks are deterministic, offline, and based on the
shared parser / keyword infrastructure.
"""

from __future__ import annotations

from typing import Any

from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
)

from ..parser import normalize_value, parse_number, parse_qe_input

# ------------------------------------------------------------------
# Rule codes  (QE-Exxx = error, QE-Wxxx = warning, QE-Ixxx = info)
# ------------------------------------------------------------------

RULE_MISSING_REQUIRED_SECTION = "QE-E001"
RULE_UNKNOWN_NAMELIST = "QE-E002"
RULE_UNKNOWN_KEYWORD = "QE-W001"
RULE_INVALID_KEYWORD_VALUE = "QE-E003"
RULE_DEPRECATED_KEYWORD = "QE-W002"
RULE_INCONSISTENT_SETTINGS = "QE-W003"
RULE_MISSING_CONTROL_CALC = "QE-E004"
RULE_MISSING_SYSTEM_ECUTWFC = "QE-E005"
RULE_MISSING_ATOMIC_SPECIES = "QE-E006"
RULE_MISSING_ATOMIC_POSITIONS = "QE-E007"
RULE_ORPHAN_PARAMETER = "QE-W004"
RULE_MISSING_CONTROL = "QE-E008"
RULE_BAD_CALCULATION = "QE-E009"
RULE_CONV_THR_LOOSE = "QE-W010"
RULE_ECUTRHO_INCONSISTENT = "QE-W011"
RULE_OCCUPATIONS_DEGAUSS_MISMATCH = "QE-W012"

# ------------------------------------------------------------------
# Schema data
# ------------------------------------------------------------------

VALID_NAMELISTS = frozenset(
    {
        "&CONTROL",
        "&SYSTEM",
        "&ELECTRONS",
        "&IONS",
        "&CELL",
    }
)

#: Mapping of namelist -> set of recognised parameter names.
#: This is intentionally a *subset* of the full QE grammar — it covers
#: the most common keywords and is the set we lint against.  Unknown
#: keywords outside this set trigger QE-W001.
KNOWN_PARAMETERS: dict[str, frozenset[str]] = {
    "&CONTROL": frozenset(
        {
            "calculation",
            "title",
            "verbosity",
            "restart_mode",
            "wf_collect",
            "nstep",
            "iprint",
            "tstress",
            "tprnfor",
            "dt",
            "outdir",
            "wfcdir",
            "prefix",
            "lkpoint_dir",
            "max_seconds",
            "etot_conv_thr",
            "forc_conv_thr",
            "disk_io",
            "pseudo_dir",
            "tefield",
            "dipfield",
            "lelfield",
            "nberrycyc",
            "lorbm",
            "lberry",
            "gdir",
            "nppstr",
            "lfcpopt",
            "gate",
            "plane_axis",
        }
    ),
    "&SYSTEM": frozenset(
        {
            "ibrav",
            "a",
            "b",
            "c",
            "cosab",
            "cosac",
            "cosbc",
            "celldm",
            "celldm(1)",
            "celldm(2)",
            "celldm(3)",
            "celldm(4)",
            "celldm(5)",
            "celldm(6)",
            "nat",
            "ntyp",
            "nbnd",
            "tot_charge",
            "tot_magnetization",
            "ecutwfc",
            "ecutrho",
            "occupations",
            "degauss",
            "smearing",
            "nspin",
            "starting_magnetization",
            "nosym",
            "nosym_evc",
            "noinv",
            "no_t_rev",
            "force_symmorphic",
            "use_all_frac",
            "noncolin",
            "lspinorb",
            "lda_plus_u",
            "lda_plus_u_kind",
            "hubbard_u",
            "hubbard_alpha",
            "hubbard_j",
            "starting_ns_eigenvalue",
            "u_projection_type",
            "edir",
            "emaxpos",
            "eopreg",
            "eamp",
            "angle1",
            "angle2",
            "report",
            "lxdm",
            "exx_fraction",
            "ec_fixed",
            "screening_parameter",
            "gcscu",
            "gcscu2",
            "gcscu3",
        }
    ),
    "&ELECTRONS": frozenset(
        {
            "conv_thr",
            "niter",
            "electron_maxstep",
            "scf_must_converge",
            "adaptively",
            "diagonalization",
            "mixing_mode",
            "mixing_beta",
            "mixing_ndim",
            "mixing_gg0",
            "tq_smoothing",
            "tbeta_smoothing",
            "diago_thr_init",
            "diago_cg_maxiter",
            "diago_david_ndim",
            "diago_rmm_ndim",
            "diago_rmm_conv",
            "diago_full_acc",
            "efield",
            "efield_cart",
            "efield_phase",
            "startingpot",
            "startingwfc",
            "tqr",
            "real_space",
        }
    ),
    "&IONS": frozenset(
        {
            "ion_dynamics",
            "ion_positions",
            "pot_extrapolation",
            "wfc_extrapolation",
            "remove_rigid_rot",
            "bfgs_ndim",
            "bfgs_w1",
            "bfgs_w2",
            "trust_radius_max",
            "trust_radius_min",
            "trust_radius_init",
            "upscale",
            "ion_nstepe",
        }
    ),
    "&CELL": frozenset(
        {
            "cell_dynamics",
            "press",
            "wmass",
            "cell_factor",
            "press_conv_thr",
            "cell_dofree",
            "isotropic",
            "fix_volume",
            "fix_area",
            "taup",
            "taub",
        }
    ),
}

#: Keywords that are deprecated or have recommended replacements.
DEPRECATED_KEYWORDS: dict[str, str] = {
    "lkpoint_dir": "Use outdir for k-point directory handling.",
    "nstep": "Use electron_maxstep in &ELECTRONS for SCF iteration limits.",
}

#: Enum-like value sets for specific keywords.
VALID_CALCULATIONS = frozenset(
    {
        "scf",
        "nscf",
        "bands",
        "relax",
        "md",
        "vc-relax",
        "vc-md",
        "cp",
        "vc-cp",
    }
)
VALID_DIAGALIZATIONS = frozenset(
    {
        "david",
        "cg",
        "ppcg",
        "paro",
        "rmm-davidson",
        "rmm-paro",
    }
)
VALID_MIXING_MODES = frozenset(
    {
        "plain",
        "tf",
        "local-tf",
    }
)
VALID_SMEARING = frozenset(
    {
        "gaussian",
        "methfessel-paxton",
        "mp",
        "mv",
        "fermi-dirac",
        "fd",
    }
)
VALID_OCCUPATIONS = frozenset(
    {
        "smearing",
        "tetrahedra",
        "tetrahedra_lin",
        "tetrahedra_opt",
        "fixed",
        "from_input",
    }
)
VALID_ION_DYNAMICS = frozenset(
    {
        "none",
        "bfgs",
        "damp",
        "verlet",
        "langevin",
        "beeman",
    }
)
VALID_CELL_DYNAMICS = frozenset(
    {
        "none",
        "sd",
        "damp-pr",
        "damp-w",
        "bfgs",
        "pr",
        "w",
    }
)
VALID_CELL_DOFREE = frozenset(
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
)

#: Keyword -> (valid values, rule code for invalid value)
VALUE_CONSTRAINTS: dict[str, tuple[frozenset[str], str]] = {
    "calculation": (VALID_CALCULATIONS, RULE_BAD_CALCULATION),
    "diagonalization": (VALID_DIAGALIZATIONS, RULE_INVALID_KEYWORD_VALUE),
    "mixing_mode": (VALID_MIXING_MODES, RULE_INVALID_KEYWORD_VALUE),
    "smearing": (VALID_SMEARING, RULE_INVALID_KEYWORD_VALUE),
    "occupations": (VALID_OCCUPATIONS, RULE_INVALID_KEYWORD_VALUE),
    "ion_dynamics": (VALID_ION_DYNAMICS, RULE_INVALID_KEYWORD_VALUE),
    "cell_dynamics": (VALID_CELL_DYNAMICS, RULE_INVALID_KEYWORD_VALUE),
    "cell_dofree": (VALID_CELL_DOFREE, RULE_INVALID_KEYWORD_VALUE),
}


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    return value.strip().strip("'\"")


# ------------------------------------------------------------------
# Lint provider
# ------------------------------------------------------------------


class LintProvider:
    """Schema-aware static lint for Quantum ESPRESSO inputs.

    Checks:
    - Missing required sections / parameters
    - Unknown namelists
    - Unknown keywords
    - Invalid keyword values
    - Deprecated keywords
    - Inconsistent settings
    - Orphan parameters outside any namelist
    """

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def lint(self, text: str) -> list[Diagnostic]:
        """Run all lint checks on *text* and return diagnostics."""
        parsed = parse_qe_input(text)
        diagnostics: list[Diagnostic] = []

        self._check_missing_control(parsed, diagnostics)
        self._check_required_sections(parsed, text, diagnostics)
        self._check_unknown_namelists(parsed, diagnostics)
        self._check_unknown_keywords(parsed, diagnostics)
        self._check_invalid_values(parsed, diagnostics)
        self._check_deprecated_keywords(parsed, diagnostics)
        self._check_inconsistent_settings(parsed, diagnostics)
        self._check_conv_thr_loose(parsed, diagnostics)
        self._check_ecutrho_inconsistent(parsed, diagnostics)
        self._check_occupations_degauss_mismatch(parsed, diagnostics)
        self._check_orphan_parameters(parsed, text, diagnostics)

        return diagnostics

    def snapshot(self, text: str) -> list[dict[str, Any]]:
        """Return a JSON-serialisable snapshot of lint diagnostics.

        Each entry includes range, severity, source, message, and rule
        code.  Sorted deterministically by (line, character).
        """
        diagnostics = self.lint(text)
        items = [_serialise(d) for d in diagnostics]
        items.sort(key=lambda d: (d["range"]["start"]["line"], d["range"]["start"]["character"]))
        return items

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _check_missing_control(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Emit QE-E008 when &CONTROL namelist is absent."""
        if not parsed.namelists:
            return
        if "&CONTROL" not in parsed.namelists:
            diagnostics.append(
                self._make(
                    line=0,
                    char=0,
                    length=0,
                    message="Missing required namelist &CONTROL.",
                    severity=DiagnosticSeverity.Error,
                    code=RULE_MISSING_CONTROL,
                )
            )

    def _check_required_sections(
        self,
        parsed: Any,
        text: str,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Report missing required namelists and cards."""
        namelists = parsed.namelists

        if not namelists:
            return

        control = namelists.get("&CONTROL", {})
        if control and "calculation" not in control:
            diagnostics.append(
                self._make(
                    line=0,
                    char=0,
                    length=0,
                    message="Missing required parameter 'calculation' in &CONTROL.",
                    severity=DiagnosticSeverity.Error,
                    code=RULE_MISSING_CONTROL_CALC,
                )
            )

        system = namelists.get("&SYSTEM", {})
        if not system:
            diagnostics.append(
                self._make(
                    line=0,
                    char=0,
                    length=0,
                    message="Missing required namelist &SYSTEM.",
                    severity=DiagnosticSeverity.Error,
                    code=RULE_MISSING_REQUIRED_SECTION,
                )
            )
        elif "ecutwfc" not in system and "nat" not in system:
            diagnostics.append(
                self._make(
                    line=0,
                    char=0,
                    length=0,
                    message="Missing required parameter 'ecutwfc' in &SYSTEM.",
                    severity=DiagnosticSeverity.Error,
                    code=RULE_MISSING_SYSTEM_ECUTWFC,
                )
            )

        has_species = "ATOMIC_SPECIES" in parsed.cards
        has_positions = "ATOMIC_POSITIONS" in parsed.cards
        if system and "nat" in system:
            if not has_species:
                diagnostics.append(
                    self._make(
                        line=0,
                        char=0,
                        length=0,
                        message="Missing required card ATOMIC_SPECIES (nat is set).",
                        severity=DiagnosticSeverity.Error,
                        code=RULE_MISSING_ATOMIC_SPECIES,
                    )
                )
            if not has_positions:
                diagnostics.append(
                    self._make(
                        line=0,
                        char=0,
                        length=0,
                        message="Missing required card ATOMIC_POSITIONS (nat is set).",
                        severity=DiagnosticSeverity.Error,
                        code=RULE_MISSING_ATOMIC_POSITIONS,
                    )
                )

    def _check_unknown_namelists(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Flag namelists outside the QE grammar."""
        for name, line_num in parsed.namelist_lines.items():
            if name not in VALID_NAMELISTS:
                diagnostics.append(
                    self._make(
                        line=line_num,
                        char=0,
                        length=len(name),
                        message=f"Unknown namelist {name}.",
                        severity=DiagnosticSeverity.Error,
                        code=RULE_UNKNOWN_NAMELIST,
                    )
                )

    def _check_unknown_keywords(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Warn about parameters not in the known schema for each namelist."""
        for namelist_name, params in parsed.namelists.items():
            known = KNOWN_PARAMETERS.get(namelist_name)
            if known is None:
                continue
            for param_name, param in params.items():
                if param_name not in known:
                    diagnostics.append(
                        self._make(
                            line=param.line,
                            char=param.character,
                            length=len(param_name),
                            message=f"Unknown keyword '{param_name}' in {namelist_name}.",
                            severity=DiagnosticSeverity.Warning,
                            code=RULE_UNKNOWN_KEYWORD,
                        )
                    )

    def _check_invalid_values(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Check enum-like keyword values against known valid sets."""
        for namelist_name, params in parsed.namelists.items():
            for param_name, param in params.items():
                constraint = VALUE_CONSTRAINTS.get(param_name)
                if constraint is None:
                    continue
                valid_values, rule_code = constraint
                raw_value = normalize_value(param.value)
                if raw_value not in valid_values:
                    raw_display = _strip_quotes(param.value)
                    valid_str = ", ".join(sorted(valid_values))
                    msg = f"Invalid value '{raw_display}' for '{param_name}'. Valid: {valid_str}."
                    diagnostics.append(
                        self._make(
                            line=param.line,
                            char=param.character,
                            length=len(param_name),
                            message=msg,
                            severity=DiagnosticSeverity.Error,
                            code=rule_code,
                        )
                    )

    def _check_deprecated_keywords(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Flag deprecated keywords with recommended replacements."""
        for namelist_name, params in parsed.namelists.items():
            for param_name, param in params.items():
                hint = DEPRECATED_KEYWORDS.get(param_name)
                if hint is not None:
                    diagnostics.append(
                        self._make(
                            line=param.line,
                            char=param.character,
                            length=len(param_name),
                            message=f"Deprecated keyword '{param_name}'. {hint}",
                            severity=DiagnosticSeverity.Warning,
                            code=RULE_DEPRECATED_KEYWORD,
                        )
                    )

    def _check_inconsistent_settings(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Detect semantically inconsistent parameter combinations."""
        control = parsed.namelists.get("&CONTROL", {})
        system = parsed.namelists.get("&SYSTEM", {})
        ions = parsed.namelists.get("&IONS", {})
        cell = parsed.namelists.get("&CELL", {})

        calc_param = control.get("calculation")
        if calc_param is None:
            return

        calc = normalize_value(calc_param.value)

        if calc in ("relax", "vc-relax") and not ions:
            diagnostics.append(
                self._make(
                    line=0,
                    char=0,
                    length=0,
                    message=f"&IONS namelist is recommended for calculation='{calc}'.",
                    severity=DiagnosticSeverity.Warning,
                    code=RULE_INCONSISTENT_SETTINGS,
                )
            )

        if calc in ("vc-relax", "vc-md") and not cell:
            diagnostics.append(
                self._make(
                    line=0,
                    char=0,
                    length=0,
                    message=f"&CELL namelist is required for calculation='{calc}'.",
                    severity=DiagnosticSeverity.Error,
                    code=RULE_INCONSISTENT_SETTINGS,
                )
            )

        nspin_param = system.get("nspin")
        if nspin_param is not None:
            nspin_val = parse_number(nspin_param.value)
            if nspin_val is not None and nspin_val > 1:
                has_mag = "starting_magnetization" in system
                has_nc_val = False
                noncolin_param = system.get("noncolin")
                if noncolin_param is not None:
                    has_nc_val = normalize_value(noncolin_param.value) in (
                        ".true.",
                        "true",
                        "t",
                    )
                if not has_mag and not has_nc_val:
                    diagnostics.append(
                        self._make(
                            line=nspin_param.line,
                            char=nspin_param.character,
                            length=len("nspin"),
                            message=(
                                "nspin > 1 but no starting_magnetization or "
                                "noncolin = .true. set in &SYSTEM."
                            ),
                            severity=DiagnosticSeverity.Warning,
                            code=RULE_INCONSISTENT_SETTINGS,
                        )
                    )

        if calc in ("nscf", "bands"):
            if "nbnd" not in system:
                diagnostics.append(
                    self._make(
                        line=0,
                        char=0,
                        length=0,
                        message=(
                            f"calculation='{calc}' usually requires explicit nbnd in &SYSTEM."
                        ),
                        severity=DiagnosticSeverity.Warning,
                        code=RULE_INCONSISTENT_SETTINGS,
                    )
                )

    def _check_conv_thr_loose(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Emit QE-W010 when conv_thr in &ELECTRONS is set above 1e-4."""
        electrons = parsed.namelists.get("&ELECTRONS", {})
        param = electrons.get("conv_thr")
        if param is None:
            return
        value = parse_number(param.value)
        if value is not None and value > 1e-4:
            diagnostics.append(
                self._make(
                    line=param.line,
                    char=param.character,
                    length=len("conv_thr"),
                    message=(
                        f"conv_thr = {value} is too loose. "
                        "Consider tightening to <= 1e-4 for reliable SCF convergence."
                    ),
                    severity=DiagnosticSeverity.Warning,
                    code=RULE_CONV_THR_LOOSE,
                )
            )

    def _check_ecutrho_inconsistent(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Emit QE-W011 when ecutrho is outside the 4x-16x range of ecutwfc."""
        system = parsed.namelists.get("&SYSTEM", {})
        ecutwfc_param = system.get("ecutwfc")
        ecutrho_param = system.get("ecutrho")
        if ecutwfc_param is None or ecutrho_param is None:
            return

        ecutwfc_val = parse_number(ecutwfc_param.value)
        ecutrho_val = parse_number(ecutrho_param.value)
        if ecutwfc_val is None or ecutrho_val is None or ecutwfc_val <= 0:
            return

        ratio = ecutrho_val / ecutwfc_val
        if ratio < 4 or ratio > 16:
            diagnostics.append(
                self._make(
                    line=ecutrho_param.line,
                    char=ecutrho_param.character,
                    length=len("ecutrho"),
                    message=(
                        f"ecutrho = {ecutrho_val} is inconsistent with ecutwfc = {ecutwfc_val} "
                        f"(ratio = {ratio:.1f}x). Expected range: 4x to 16x ecutwfc."
                    ),
                    severity=DiagnosticSeverity.Warning,
                    code=RULE_ECUTRHO_INCONSISTENT,
                )
            )

    def _check_occupations_degauss_mismatch(
        self,
        parsed: Any,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Emit QE-W012 when occupations='smearing' but degauss is missing or out of range."""
        system = parsed.namelists.get("&SYSTEM", {})
        occ_param = system.get("occupations")
        if occ_param is None:
            return

        occ_value = normalize_value(occ_param.value)
        if occ_value != "smearing":
            return

        degauss_param = system.get("degauss")
        if degauss_param is None:
            diagnostics.append(
                self._make(
                    line=occ_param.line,
                    char=occ_param.character,
                    length=len("occupations"),
                    message=(
                        "occupations = 'smearing' requires degauss in &SYSTEM, "
                        "but degauss is not set."
                    ),
                    severity=DiagnosticSeverity.Warning,
                    code=RULE_OCCUPATIONS_DEGAUSS_MISMATCH,
                )
            )
            return

        degauss_val = parse_number(degauss_param.value)
        if degauss_val is None:
            return

        if degauss_val < 0.001:
            diagnostics.append(
                self._make(
                    line=degauss_param.line,
                    char=degauss_param.character,
                    length=len("degauss"),
                    message=(
                        f"degauss = {degauss_val} is too small (< 0.001 Ry). "
                        "Consider using a value >= 0.001 Ry for stable smearing."
                    ),
                    severity=DiagnosticSeverity.Warning,
                    code=RULE_OCCUPATIONS_DEGAUSS_MISMATCH,
                )
            )
        elif degauss_val > 0.1:
            diagnostics.append(
                self._make(
                    line=degauss_param.line,
                    char=degauss_param.character,
                    length=len("degauss"),
                    message=(
                        f"degauss = {degauss_val} is too large (> 0.1 Ry). "
                        "Consider using a value <= 0.1 Ry to avoid over-smearing."
                    ),
                    severity=DiagnosticSeverity.Warning,
                    code=RULE_OCCUPATIONS_DEGAUSS_MISMATCH,
                )
            )

    def _check_orphan_parameters(
        self,
        parsed: Any,
        text: str,
        diagnostics: list[Diagnostic],
    ) -> None:
        """Detect assignments outside any namelist block."""
        from ..parser import ASSIGNMENT_RE
        from ..text import strip_inline_comment

        in_namelist = False
        for line_number, raw_line in enumerate(text.splitlines()):
            line = strip_inline_comment(raw_line)
            if not line:
                continue
            if line.startswith("&"):
                in_namelist = True
                continue
            if line.startswith("/"):
                in_namelist = False
                continue
            if not in_namelist:
                for match in ASSIGNMENT_RE.finditer(line):
                    name = match.group(1)
                    diagnostics.append(
                        self._make(
                            line=line_number,
                            char=match.start(1),
                            length=len(name),
                            message=f"Parameter '{name}' is outside any namelist.",
                            severity=DiagnosticSeverity.Warning,
                            code=RULE_ORPHAN_PARAMETER,
                        )
                    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make(
        line: int,
        char: int,
        length: int,
        message: str,
        severity: DiagnosticSeverity,
        code: str,
    ) -> Diagnostic:
        return Diagnostic(
            range=Range(
                start=Position(line=line, character=char),
                end=Position(line=line, character=char + max(1, length)),
            ),
            severity=severity,
            message=message,
            source="qe-lsp-lint",
            code=code,
        )


# ------------------------------------------------------------------
# Serialisation helpers
# ------------------------------------------------------------------

_SEVERITY_LABELS: dict[int, str] = {
    DiagnosticSeverity.Error: "Error",
    DiagnosticSeverity.Warning: "Warning",
    DiagnosticSeverity.Information: "Information",
    DiagnosticSeverity.Hint: "Hint",
}


def _serialise(diagnostic: Diagnostic) -> dict[str, Any]:
    """Convert a lint Diagnostic to a JSON-friendly dict."""
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
        "source": diagnostic.source or "qe-lsp-lint",
        "code": str(diagnostic.code) if diagnostic.code is not None else None,
        "message": diagnostic.message,
    }


__all__ = ["LintProvider"]

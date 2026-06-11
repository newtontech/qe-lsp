"""Machine-readable code-intelligence API for AI coding agents."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from lsprotocol.types import Diagnostic


@dataclass
class AgentAPISnapshot:
    uri: str = ""
    version: Optional[int] = None
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)
    outline: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "uri": self.uri,
                "version": self.version,
                "diagnostics": self.diagnostics,
                "outline": self.outline,
                "metadata": self.metadata,
            },
            indent=2,
        )


def _diag_to_dict(d: Diagnostic) -> Dict[str, Any]:
    return {
        "line": d.range.start.line,
        "character": d.range.start.character,
        "severity": d.severity,
        "message": d.message,
        "code": d.code,
        "source": d.source,
    }


def describe_domain_language() -> Dict[str, Any]:
    """Return a machine-readable description of the Quantum ESPRESSO input language.

    The description includes supported namelists, common keywords with types
    and short descriptions, recognised cards, and file extensions.  Agent
    tools can call this at startup to bootstrap their understanding of the
    QE domain.
    """
    return {
        "language": "quantum-espresso",
        "namelists": {
            "CONTROL": {
                "description": "General calculation control parameters.",
                "keywords": {
                    "calculation": {
                        "type": "string",
                        "enum": [
                            "scf",
                            "nscf",
                            "bands",
                            "relax",
                            "md",
                            "vc-relax",
                            "vc-md",
                        ],
                        "description": "Type of calculation to perform.",
                    },
                    "prefix": {
                        "type": "string",
                        "description": "Prefix for output file names.",
                    },
                    "outdir": {
                        "type": "string",
                        "description": "Directory for temporary and output files.",
                    },
                    "pseudo_dir": {
                        "type": "string",
                        "description": "Directory containing pseudopotential files.",
                    },
                    "ibrav": {
                        "type": "integer",
                        "enum": list(range(0, 15)),
                        "description": "Bravais-lattice index (0 = free).",
                    },
                    "restart_mode": {
                        "type": "string",
                        "enum": ["from_scratch", "restart"],
                        "description": "Whether to restart from previous run.",
                    },
                    "tprnfor": {
                        "type": "logical",
                        "description": "Calculate forces.",
                    },
                    "tstress": {
                        "type": "logical",
                        "description": "Calculate stress tensor.",
                    },
                    "dt": {
                        "type": "float",
                        "description": "Time step for molecular dynamics (Ry*au).",
                    },
                    "max_seconds": {
                        "type": "float",
                        "description": "Wall-time limit in seconds.",
                    },
                    "etot_conv_thr": {
                        "type": "float",
                        "description": "Convergence threshold on total energy (Ry).",
                    },
                    "forc_conv_thr": {
                        "type": "float",
                        "description": "Convergence threshold on forces (Ry/au).",
                    },
                },
            },
            "SYSTEM": {
                "description": "System-specific parameters.",
                "keywords": {
                    "celldm": {
                        "type": "float[6]",
                        "description": "Lattice parameters (celldm(1)-celldm(6)).",
                    },
                    "nat": {
                        "type": "integer",
                        "description": "Number of atoms in the unit cell.",
                    },
                    "ntyp": {
                        "type": "integer",
                        "description": "Number of atom types.",
                    },
                    "ecutwfc": {
                        "type": "float",
                        "description": "Kinetic-energy cutoff for wavefunctions (Ry).",
                    },
                    "ecutrho": {
                        "type": "float",
                        "description": "Kinetic-energy cutoff for charge density (Ry).",
                    },
                    "occupations": {
                        "type": "string",
                        "enum": ["smearing", "tetrahedra", "fixed", "from_input"],
                        "description": "Occupation method.",
                    },
                    "degauss": {
                        "type": "float",
                        "description": "Smearing width (Ry).",
                    },
                    "smearing": {
                        "type": "string",
                        "enum": [
                            "gaussian",
                            "methfessel-paxton",
                            "marzari-vanderbilt",
                            "fd",
                        ],
                        "description": "Smearing type.",
                    },
                    "nspin": {
                        "type": "integer",
                        "enum": [1, 2, 4],
                        "description": "Spin polarization (1=non-magnetic, 2=LSDA, 4=non-collinear).",
                    },
                    "noncolin": {
                        "type": "logical",
                        "description": "Non-collinear magnetism.",
                    },
                },
            },
            "ELECTRONS": {
                "description": "Electronic-structure convergence parameters.",
                "keywords": {
                    "conv_thr": {
                        "type": "float",
                        "description": "Convergence threshold for SCF (Ry).",
                    },
                    "electron_maxstep": {
                        "type": "integer",
                        "description": "Maximum number of SCF iterations.",
                    },
                    "mixing_beta": {
                        "type": "float",
                        "description": "Mixing factor for self-consistency.",
                    },
                    "mixing_mode": {
                        "type": "string",
                        "enum": ["plain", "TF", "local-TF"],
                        "description": "Charge-density mixing mode.",
                    },
                    "diagonalization": {
                        "type": "string",
                        "enum": ["david", "cg", "ppcg", "paro"],
                        "description": "Eigenvalue solver.",
                    },
                    "scf_must_converge": {
                        "type": "logical",
                        "description": "Abort if SCF does not converge.",
                    },
                    "startingwfc": {
                        "type": "string",
                        "enum": ["random", "atomic", "atomic+random", "file"],
                        "description": "Initial wavefunction guess.",
                    },
                    "startingcharge": {
                        "type": "string",
                        "enum": ["atomic", "file"],
                        "description": "Initial charge-density guess.",
                    },
                },
            },
            "IONS": {
                "description": "Ionic-motion parameters (relax / md).",
                "keywords": {
                    "ion_dynamics": {
                        "type": "string",
                        "enum": ["bfgs", "damp", "verlet", "langevin", "beeman"],
                        "description": "Ionic dynamics algorithm.",
                    },
                    "ion_positions": {
                        "type": "string",
                        "enum": ["default", "from_input"],
                        "description": "Source of initial ionic positions.",
                    },
                    "pot_extrapolation": {
                        "type": "string",
                        "enum": ["none", "atomic", "first_order", "second_order"],
                        "description": "Potential extrapolation method.",
                    },
                    "bfgs_ndim": {
                        "type": "integer",
                        "description": "BFGS history dimension.",
                    },
                    "trust_radius_max": {
                        "type": "float",
                        "description": "Maximum trust radius (au).",
                    },
                    "trust_radius_min": {
                        "type": "float",
                        "description": "Minimum trust radius (au).",
                    },
                },
            },
            "CELL": {
                "description": "Cell-motion parameters (vc-relax / vc-md).",
                "keywords": {
                    "cell_dynamics": {
                        "type": "string",
                        "enum": ["none", "sd", "damp-pr", "bfgs", "pr", "w"],
                        "description": "Cell dynamics algorithm.",
                    },
                    "press": {
                        "type": "float",
                        "description": "Target pressure (kbar).",
                    },
                    "press_conv_thr": {
                        "type": "float",
                        "description": "Convergence threshold on pressure (kbar).",
                    },
                    "cell_factor": {
                        "type": "float",
                        "description": "Scaling factor for cell moves.",
                    },
                    "fix_volume": {
                        "type": "logical",
                        "description": "Keep cell volume fixed during relaxation.",
                    },
                    "fix_area": {
                        "type": "logical",
                        "description": "Keep cell area fixed (2D calculations).",
                    },
                },
            },
        },
        "cards": {
            "ATOMIC_SPECIES": {
                "description": "Defines atom types and pseudopotentials.",
                "syntax": "<type> <mass> <pseudo_file>",
            },
            "ATOMIC_POSITIONS": {
                "description": "Coordinates of atoms in the unit cell.",
                "options": ["alat", "bohr", "crystal", "angstrom", "crystal_sg"],
            },
            "K_POINTS": {
                "description": "Brillouin-zone sampling.",
                "options": [
                    "tpiba",
                    "automatic",
                    "crystal",
                    "gamma",
                    "tpiba_b",
                    "crystal_b",
                ],
            },
            "CELL_PARAMETERS": {
                "description": "Lattice vectors (when ibrav=0).",
                "options": ["alat", "bohr", "angstrom"],
            },
            "ATOMIC_FORCES": {
                "description": "External forces on atoms (for constrained optimisation).",
                "syntax": "<index> <fx> <fy> <fz>",
            },
            "CONSTRAINTS": {
                "description": "Geometric constraints on atoms.",
            },
            "OCCUPATIONS": {
                "description": "Manual occupation numbers (when occupations='from_input').",
            },
        },
        "file_types": {
            ".in": "Primary Quantum ESPRESSO input file.",
            ".pw": "PWscf input file alias.",
            ".q2r": "q2r.x input (phonon interpolation).",
            ".matdyn": "matdyn.x input (phonon dispersion).",
            ".ph": "ph.x input (phonon calculation).",
            ".pp": "pp.x input (post-processing).",
            ".bands": "bands.x input (band structure).",
            ".dos": "dos.x input (density of states).",
            ".projwfc": "projwfc.x input (projected DOS).",
        },
    }


def lookup_namelist(name: str) -> Optional[Dict[str, Any]]:
    """Return schema for a QE namelist by name.

    Returns a dict with:
      - name: the namelist name (uppercased)
      - description: short description of the namelist
      - keywords: dict mapping keyword name to its schema (type, description,
        default_value, valid_values, required)
    Returns None if the namelist is not found.
    """
    domain = describe_domain_language()
    nl = domain["namelists"].get(name.upper())
    if nl is None:
        return None
    keywords: Dict[str, Any] = {}
    for kw_name, kw_schema in nl["keywords"].items():
        keywords[kw_name] = {
            "type": kw_schema.get("type"),
            "description": kw_schema.get("description", ""),
            "default_value": kw_schema.get("default_value"),
            "valid_values": kw_schema.get("enum"),
            "required": kw_schema.get("required", False),
        }
    return {
        "name": name.upper(),
        "description": nl.get("description", ""),
        "keywords": keywords,
    }


def lookup_keyword(namelist: str, keyword: str) -> Optional[Dict[str, Any]]:
    """Return schema for a specific keyword within a namelist.

    Returns a dict with:
      - namelist: parent namelist name
      - name: keyword name
      - type: value type (string, integer, float, logical, etc.)
      - description: short description
      - default_value: default value if known, else None
      - valid_values: list of valid values for enum types, else None
      - required: whether this keyword is required
    Returns None if the namelist or keyword is not found.
    """
    domain = describe_domain_language()
    nl = domain["namelists"].get(namelist.upper())
    if nl is None:
        return None
    kw_schema = nl["keywords"].get(keyword)
    if kw_schema is None:
        return None
    return {
        "namelist": namelist.upper(),
        "name": keyword,
        "type": kw_schema.get("type"),
        "description": kw_schema.get("description", ""),
        "default_value": kw_schema.get("default_value"),
        "valid_values": kw_schema.get("enum"),
        "required": kw_schema.get("required", False),
    }


class AgentAPIProvider:
    def __init__(self) -> None:
        pass

    def get_snapshot(
        self,
        source: str,
        uri: str = "",
        version: Optional[int] = None,
        diagnostics: Optional[List[Diagnostic]] = None,
    ) -> AgentAPISnapshot:
        diag_dicts = [_diag_to_dict(d) for d in (diagnostics or [])]
        outline = self._build_outline(source)
        return AgentAPISnapshot(
            uri=uri,
            version=version,
            diagnostics=diag_dicts,
            outline=outline,
            metadata={
                "language": "quantum-espresso",
                "provider": "qe_lsp",
                "feature_count": {"diagnostics": len(diag_dicts), "outline_items": len(outline)},
            },
        )

    def _build_outline(self, source: str) -> List[Dict[str, Any]]:
        outline: List[Dict[str, Any]] = []
        lines = source.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("!") and not stripped.startswith("#"):
                outline.append({"line": i, "text": stripped[:80], "type": "content"})
        return outline

    def get_diagnostics_json(
        self, source: str, uri: str = "", diagnostics: Optional[List[Diagnostic]] = None
    ) -> str:
        snap = self.get_snapshot(source, uri, diagnostics=diagnostics)
        return json.dumps(
            {"uri": snap.uri, "diagnostics": snap.diagnostics, "count": len(snap.diagnostics)},
            indent=2,
        )

    def get_outline_json(self, source: str, uri: str = "") -> str:
        snap = self.get_snapshot(source, uri)
        return json.dumps({"uri": snap.uri, "outline": snap.outline}, indent=2)


# ---------------------------------------------------------------------------
# Minimal examples and next-token guidance for AI-assisted authoring
# ---------------------------------------------------------------------------

_EXAMPLES: List[Dict[str, str]] = [
    {
        "name": "scf",
        "description": "Self-consistent field calculation for total energy.",
        "calculation_type": "scf",
        "input_text": (
            "&CONTROL\n"
            "  calculation = 'scf'\n"
            "  prefix = 'si'\n"
            "  outdir = './out'\n"
            "  pseudo_dir = './pseudo'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 2\n"
            "  celldm(1) = 10.2\n"
            "  nat = 2\n"
            "  ntyp = 1\n"
            "  ecutwfc = 30.0\n"
            "/\n"
            "&ELECTRONS\n"
            "  conv_thr = 1.0d-8\n"
            "/\n"
            "ATOMIC_SPECIES\n"
            "  Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
            "ATOMIC_POSITIONS crystal\n"
            "  Si 0.00 0.00 0.00\n"
            "  Si 0.25 0.25 0.25\n"
            "K_POINTS automatic\n"
            "  8 8 8 0 0 0\n"
        ),
    },
    {
        "name": "nscf",
        "description": "Non-self-consistent field calculation for band structure or DOS.",
        "calculation_type": "nscf",
        "input_text": (
            "&CONTROL\n"
            "  calculation = 'nscf'\n"
            "  prefix = 'si'\n"
            "  outdir = './out'\n"
            "  pseudo_dir = './pseudo'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 2\n"
            "  celldm(1) = 10.2\n"
            "  nat = 2\n"
            "  ntyp = 1\n"
            "  ecutwfc = 30.0\n"
            "  nbnd = 12\n"
            "/\n"
            "&ELECTRONS\n"
            "  conv_thr = 1.0d-8\n"
            "/\n"
            "ATOMIC_SPECIES\n"
            "  Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
            "ATOMIC_POSITIONS crystal\n"
            "  Si 0.00 0.00 0.00\n"
            "  Si 0.25 0.25 0.25\n"
            "K_POINTS automatic\n"
            "  12 12 12 0 0 0\n"
        ),
    },
    {
        "name": "relax",
        "description": "Structural relaxation with fixed cell.",
        "calculation_type": "relax",
        "input_text": (
            "&CONTROL\n"
            "  calculation = 'relax'\n"
            "  prefix = 'si'\n"
            "  outdir = './out'\n"
            "  pseudo_dir = './pseudo'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 2\n"
            "  celldm(1) = 10.2\n"
            "  nat = 2\n"
            "  ntyp = 1\n"
            "  ecutwfc = 30.0\n"
            "/\n"
            "&ELECTRONS\n"
            "  conv_thr = 1.0d-8\n"
            "/\n"
            "&IONS\n"
            "  ion_dynamics = 'bfgs'\n"
            "/\n"
            "ATOMIC_SPECIES\n"
            "  Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
            "ATOMIC_POSITIONS crystal\n"
            "  Si 0.00 0.00 0.00\n"
            "  Si 0.25 0.25 0.25\n"
            "K_POINTS automatic\n"
            "  8 8 8 0 0 0\n"
        ),
    },
    {
        "name": "vc-relax",
        "description": "Variable-cell relaxation: optimise both ionic positions and cell shape.",
        "calculation_type": "vc-relax",
        "input_text": (
            "&CONTROL\n"
            "  calculation = 'vc-relax'\n"
            "  prefix = 'si'\n"
            "  outdir = './out'\n"
            "  pseudo_dir = './pseudo'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 2\n"
            "  celldm(1) = 10.2\n"
            "  nat = 2\n"
            "  ntyp = 1\n"
            "  ecutwfc = 30.0\n"
            "/\n"
            "&ELECTRONS\n"
            "  conv_thr = 1.0d-8\n"
            "/\n"
            "&IONS\n"
            "  ion_dynamics = 'bfgs'\n"
            "/\n"
            "&CELL\n"
            "  cell_dynamics = 'bfgs'\n"
            "  press = 0.0\n"
            "  press_conv_thr = 0.1\n"
            "/\n"
            "ATOMIC_SPECIES\n"
            "  Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
            "ATOMIC_POSITIONS crystal\n"
            "  Si 0.00 0.00 0.00\n"
            "  Si 0.25 0.25 0.25\n"
            "K_POINTS automatic\n"
            "  8 8 8 0 0 0\n"
        ),
    },
    {
        "name": "md",
        "description": "Molecular dynamics simulation.",
        "calculation_type": "md",
        "input_text": (
            "&CONTROL\n"
            "  calculation = 'md'\n"
            "  prefix = 'si'\n"
            "  outdir = './out'\n"
            "  pseudo_dir = './pseudo'\n"
            "  dt = 20.0\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 2\n"
            "  celldm(1) = 10.2\n"
            "  nat = 2\n"
            "  ntyp = 1\n"
            "  ecutwfc = 30.0\n"
            "/\n"
            "&ELECTRONS\n"
            "  conv_thr = 1.0d-8\n"
            "/\n"
            "&IONS\n"
            "  ion_dynamics = 'verlet'\n"
            "/\n"
            "ATOMIC_SPECIES\n"
            "  Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
            "ATOMIC_POSITIONS crystal\n"
            "  Si 0.00 0.00 0.00\n"
            "  Si 0.25 0.25 0.25\n"
            "K_POINTS automatic\n"
            "  4 4 4 0 0 0\n"
        ),
    },
    {
        "name": "phonon",
        "description": "Phonon calculation using ph.x (requires prior scf run).",
        "calculation_type": "phonon",
        "input_text": (
            "phonon of Si\n"
            "&INPUTPH\n"
            "  prefix = 'si'\n"
            "  outdir = './out'\n"
            "  fildyn = 'si.dyn'\n"
            "  tr2_ph = 1.0d-14\n"
            "  amass(1) = 28.086\n"
            "/\n"
            "0.0 0.0 0.0\n"
        ),
    },
    {
        "name": "bands",
        "description": "Band-structure calculation (nscf on a path, then bands.x post-processing).",
        "calculation_type": "bands",
        "input_text": (
            "&CONTROL\n"
            "  calculation = 'bands'\n"
            "  prefix = 'si'\n"
            "  outdir = './out'\n"
            "  pseudo_dir = './pseudo'\n"
            "/\n"
            "&SYSTEM\n"
            "  ibrav = 2\n"
            "  celldm(1) = 10.2\n"
            "  nat = 2\n"
            "  ntyp = 1\n"
            "  ecutwfc = 30.0\n"
            "  nbnd = 12\n"
            "/\n"
            "&ELECTRONS\n"
            "  conv_thr = 1.0d-8\n"
            "/\n"
            "ATOMIC_SPECIES\n"
            "  Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
            "ATOMIC_POSITIONS crystal\n"
            "  Si 0.00 0.00 0.00\n"
            "  Si 0.25 0.25 0.25\n"
            "K_POINTS crystal\n"
            "5\n"
            "  0.500  0.500  0.500  20  L\n"
            "  0.000  0.000  0.000  20  Gamma\n"
            "  0.500  0.000  0.500  20  X\n"
            "  0.375  0.375  0.750  20  U\n"
            "  0.000  0.000  0.000   1  Gamma\n"
        ),
    },
    {
        "name": "dos",
        "description": "Density of states using dos.x (requires prior nscf run).",
        "calculation_type": "dos",
        "input_text": (
            "&DOS\n"
            "  prefix = 'si'\n"
            "  outdir = './out'\n"
            "  fildos = 'si.dos'\n"
            "  Emin = -10.0\n"
            "  Emax = 20.0\n"
            "  DeltaE = 0.01\n"
            "/\n"
        ),
    },
]

_EXAMPLES_INDEX: Dict[str, Dict[str, str]] = {ex["calculation_type"]: ex for ex in _EXAMPLES}

# Token-suggestion rules: each rule has a regex pattern and a list of
# suggestion dicts.  The last line of the context is matched against each
# pattern; matching rules contribute their suggestions.
_TOKEN_RULES: List[Dict[str, Any]] = [
    {
        "trigger": "namelist_start",
        "pattern": r"&(?:CONTROL|SYSTEM|ELECTRONS|IONS|CELL|INPUTPH|DOS)\s*$",
        "suggestions": [
            {
                "text": "\n  ",
                "type": "indent",
                "description": "Indented newline for keyword assignment",
            },
        ],
    },
    {
        "trigger": "after_control_calculation",
        "pattern": r"calculation\s*=\s*['\"]",
        "suggestions": [
            {"text": "scf'  ", "type": "value", "description": "Self-consistent field calculation"},
            {"text": "nscf'  ", "type": "value", "description": "Non-self-consistent field calculation"},
            {"text": "relax'  ", "type": "value", "description": "Ionic relaxation (fixed cell)"},
            {"text": "vc-relax'  ", "type": "value", "description": "Variable-cell relaxation"},
            {"text": "md'  ", "type": "value", "description": "Molecular dynamics"},
            {"text": "bands'  ", "type": "value", "description": "Band-structure calculation"},
        ],
    },
    {
        "trigger": "namelist_end",
        "pattern": r"/\s*$",
        "suggestions": [
            {
                "text": "ATOMIC_SPECIES\n",
                "type": "card",
                "description": "Define atom types and pseudopotentials",
            },
            {
                "text": "ATOMIC_POSITIONS crystal\n",
                "type": "card",
                "description": "Atomic coordinates in crystal units",
            },
            {
                "text": "K_POINTS automatic\n",
                "type": "card",
                "description": "Automatic uniform k-point grid",
            },
            {
                "text": "CELL_PARAMETERS\n",
                "type": "card",
                "description": "Lattice vectors (when ibrav=0)",
            },
            {
                "text": "ATOMIC_FORCES\n",
                "type": "card",
                "description": "External forces on atoms",
            },
        ],
    },
    {
        "trigger": "atomic_species_header",
        "pattern": r"ATOMIC_SPECIES\s*$",
        "suggestions": [
            {
                "text": "  <label> <mass> <pseudo_file>\n",
                "type": "placeholder",
                "description": "One line per atom type: label, mass, pseudopotential file",
            },
        ],
    },
    {
        "trigger": "atomic_positions_header",
        "pattern": r"ATOMIC_POSITIONS\s+(?:alat|bohr|crystal|angstrom|crystal_sg)\s*$",
        "suggestions": [
            {
                "text": "  <label> <x> <y> <z>\n",
                "type": "placeholder",
                "description": "One line per atom: label and three coordinates",
            },
        ],
    },
    {
        "trigger": "k_points_automatic",
        "pattern": r"K_POINTS\s+(?:automatic|tpiba|crystal|gamma)\s*$",
        "suggestions": [
            {
                "text": "  <nk1> <nk2> <nk3> <dk1> <dk2> <dk3>\n",
                "type": "placeholder",
                "description": "Grid dimensions and offsets for k-point sampling",
            },
        ],
    },
    {
        "trigger": "control_keywords",
        "pattern": r"&CONTROL\s*",
        "suggestions": [
            {"text": "calculation = ", "type": "keyword", "description": "Type of calculation to perform"},
            {"text": "prefix = ", "type": "keyword", "description": "Prefix for output file names"},
            {"text": "outdir = ", "type": "keyword", "description": "Directory for temporary and output files"},
            {
                "text": "pseudo_dir = ",
                "type": "keyword",
                "description": "Directory containing pseudopotential files",
            },
            {"text": "ibrav = ", "type": "keyword", "description": "Bravais-lattice index (0 = free)"},
            {"text": "tprnfor = ", "type": "keyword", "description": "Calculate forces"},
            {"text": "tstress = ", "type": "keyword", "description": "Calculate stress tensor"},
            {"text": "dt = ", "type": "keyword", "description": "Time step for MD (Ry*au)"},
        ],
    },
    {
        "trigger": "system_keywords",
        "pattern": r"&SYSTEM\s*",
        "suggestions": [
            {"text": "nat = ", "type": "keyword", "description": "Number of atoms in the unit cell"},
            {"text": "ntyp = ", "type": "keyword", "description": "Number of atom types"},
            {
                "text": "ecutwfc = ",
                "type": "keyword",
                "description": "Kinetic-energy cutoff for wavefunctions (Ry)",
            },
            {
                "text": "ecutrho = ",
                "type": "keyword",
                "description": "Kinetic-energy cutoff for charge density (Ry)",
            },
            {"text": "ibrav = ", "type": "keyword", "description": "Bravais-lattice index"},
            {"text": "occupations = ", "type": "keyword", "description": "Occupation method"},
        ],
    },
    {
        "trigger": "electrons_keywords",
        "pattern": r"&ELECTRONS\s*",
        "suggestions": [
            {"text": "conv_thr = ", "type": "keyword", "description": "Convergence threshold for SCF (Ry)"},
            {
                "text": "electron_maxstep = ",
                "type": "keyword",
                "description": "Maximum number of SCF iterations",
            },
            {
                "text": "mixing_beta = ",
                "type": "keyword",
                "description": "Mixing factor for self-consistency",
            },
            {"text": "diagonalization = ", "type": "keyword", "description": "Eigenvalue solver"},
        ],
    },
    {
        "trigger": "ions_keywords",
        "pattern": r"&IONS\s*",
        "suggestions": [
            {"text": "ion_dynamics = ", "type": "keyword", "description": "Ionic dynamics algorithm"},
            {
                "text": "ion_positions = ",
                "type": "keyword",
                "description": "Source of initial ionic positions",
            },
        ],
    },
    {
        "trigger": "cell_keywords",
        "pattern": r"&CELL\s*",
        "suggestions": [
            {"text": "cell_dynamics = ", "type": "keyword", "description": "Cell dynamics algorithm"},
            {"text": "press = ", "type": "keyword", "description": "Target pressure (kbar)"},
            {
                "text": "press_conv_thr = ",
                "type": "keyword",
                "description": "Convergence threshold on pressure (kbar)",
            },
        ],
    },
]


def get_examples(calculation_type: str = "") -> List[Dict[str, str]]:
    """Return minimal example QE input snippets for common calculation types.

    Parameters
    ----------
    calculation_type:
        If provided, return only the example matching this calculation type
        (e.g. ``"scf"``, ``"vc-relax"``).  If empty, return all examples.

    Returns
    -------
    list of dict
        Each dict has keys ``name``, ``description``, ``calculation_type``,
        and ``input_text``.
    """
    if calculation_type:
        match = _EXAMPLES_INDEX.get(calculation_type)
        if match is None:
            return []
        return [dict(match)]
    return [dict(ex) for ex in _EXAMPLES]


def next_token_suggestions(context: str, prefix: str = "") -> List[Dict[str, str]]:
    """Suggest next tokens based on partial QE input context.

    The function examines the tail of *context* and, optionally, a *prefix*
    string that the user has already started typing.  It returns a list of
    suggestion dicts, each with ``text``, ``type``, and ``description``.

    Parameters
    ----------
    context:
        The full QE input text typed so far.
    prefix:
        Additional characters the cursor is positioned after (for inline
        completion).

    Returns
    -------
    list of dict
        Suggested tokens.  Each entry contains ``text``, ``type``, and
        ``description``.
    """
    import re

    if not context and not prefix:
        return [
            {"text": "&CONTROL\n", "type": "namelist", "description": "Start a CONTROL namelist block"},
            {"text": "&INPUTPH\n", "type": "namelist", "description": "Start a ph.x phonon input"},
            {"text": "&DOS\n", "type": "namelist", "description": "Start a dos.x input"},
        ]

    lines = context.rstrip().splitlines()
    if not lines:
        return [
            {"text": "&CONTROL\n", "type": "namelist", "description": "Start a CONTROL namelist block"},
        ]

    last_line = lines[-1].rstrip()

    # Check rules from most specific to least specific.
    results: List[Dict[str, str]] = []

    for rule in _TOKEN_RULES:
        if re.search(rule["pattern"], last_line):
            for suggestion in rule["suggestions"]:
                results.append(
                    {
                        "text": suggestion["text"],
                        "type": suggestion["type"],
                        "description": suggestion["description"],
                    }
                )

    # If no rule matched, offer a generic suggestion to close the current namelist.
    if not results:
        results.append(
            {
                "text": "/\n",
                "type": "namelist_end",
                "description": "Close the current namelist",
            }
        )

    # Filter by prefix if provided.
    if prefix:
        results = [r for r in results if r["text"].startswith(prefix)]

    return results


# ---------------------------------------------------------------------------
# Rule manifest – machine-readable catalogue of all diagnostic rules
# ---------------------------------------------------------------------------

_RULE_DEFINITIONS: List[Dict[str, str]] = [
    {
        "code": "QE-E001",
        "rule_id": "qe.input.missing_required_section",
        "severity": "error",
        "description": "Missing required namelist or card section.",
    },
    {
        "code": "QE-E002",
        "rule_id": "qe.input.unknown_namelist",
        "severity": "error",
        "description": "Unknown namelist outside the QE grammar.",
    },
    {
        "code": "QE-W001",
        "rule_id": "qe.input.unknown_keyword",
        "severity": "warning",
        "description": "Unknown keyword not in the known schema for a namelist.",
    },
    {
        "code": "QE-E003",
        "rule_id": "qe.input.invalid_keyword_value",
        "severity": "error",
        "description": "Invalid value for a keyword with constrained enum values.",
    },
    {
        "code": "QE-W002",
        "rule_id": "qe.input.deprecated_keyword",
        "severity": "warning",
        "description": "Deprecated keyword with a recommended replacement.",
    },
    {
        "code": "QE-W003",
        "rule_id": "qe.input.inconsistent_settings",
        "severity": "warning",
        "description": "Semantically inconsistent parameter combination.",
    },
    {
        "code": "QE-E004",
        "rule_id": "qe.input.missing_control_calculation",
        "severity": "error",
        "description": "Missing required parameter 'calculation' in &CONTROL.",
    },
    {
        "code": "QE-E005",
        "rule_id": "qe.input.missing_system_ecutwfc",
        "severity": "error",
        "description": "Missing required parameter 'ecutwfc' in &SYSTEM.",
    },
    {
        "code": "QE-E006",
        "rule_id": "qe.input.missing_atomic_species",
        "severity": "error",
        "description": "Missing required card ATOMIC_SPECIES when nat is set.",
    },
    {
        "code": "QE-E007",
        "rule_id": "qe.input.missing_atomic_positions",
        "severity": "error",
        "description": "Missing required card ATOMIC_POSITIONS when nat is set.",
    },
    {
        "code": "QE-W004",
        "rule_id": "qe.input.orphan_parameter",
        "severity": "warning",
        "description": "Parameter assignment outside any namelist block.",
    },
    {
        "code": "QE-E008",
        "rule_id": "qe.input.missing_control",
        "severity": "error",
        "description": "Missing required namelist &CONTROL.",
    },
    {
        "code": "QE-E009",
        "rule_id": "qe.input.bad_calculation",
        "severity": "error",
        "description": "Invalid value for the 'calculation' keyword.",
    },
    {
        "code": "QE-W010",
        "rule_id": "qe.scf.conv_thr_loose",
        "severity": "warning",
        "description": "conv_thr is too loose (> 1e-4) for reliable SCF convergence.",
    },
    {
        "code": "QE-W011",
        "rule_id": "qe.cutoff.ecutrho_inconsistent",
        "severity": "warning",
        "description": "ecutrho is outside the 4x-16x range of ecutwfc.",
    },
    {
        "code": "QE-W012",
        "rule_id": "qe.smearing.occupations_degauss_mismatch",
        "severity": "warning",
        "description": "occupations='smearing' but degauss is missing or out of range.",
    },
    {
        "code": "QE-E013",
        "rule_id": "qe.kpoints.invalid_card",
        "severity": "error",
        "description": "Invalid K_POINTS card type specifier.",
    },
    {
        "code": "QE-E014",
        "rule_id": "qe.log.scf_not_converged",
        "severity": "error",
        "description": "SCF convergence was not achieved in the QE output log.",
    },
    {
        "code": "QE-E015",
        "rule_id": "qe.log.error_in_routine",
        "severity": "error",
        "description": "Error reported in a QE routine in the output log.",
    },
    {
        "code": "QE-E016",
        "rule_id": "qe.log.warning",
        "severity": "error",
        "description": "Warning-level issue detected in QE output log.",
    },
    {
        "code": "QE-E017",
        "rule_id": "qe.log.segmentation_fault",
        "severity": "error",
        "description": "Segmentation fault detected in QE output.",
    },
    {
        "code": "QE-E018",
        "rule_id": "qe.log.max_cpu_time",
        "severity": "error",
        "description": "Maximum CPU time exceeded in QE output.",
    },
    {
        "code": "QE-E019",
        "rule_id": "qe.log.band_structure_error",
        "severity": "error",
        "description": "Band structure calculation error in QE output.",
    },
    {
        "code": "QE-E020",
        "rule_id": "qe.log.phonon_error",
        "severity": "error",
        "description": "Phonon calculation error in QE output.",
    },
    {
        "code": "QE-TE001",
        "rule_id": "qe.typecheck.type_mismatch",
        "severity": "error",
        "description": "Value type does not match the expected type for the keyword.",
    },
    {
        "code": "QE-TE002",
        "rule_id": "qe.typecheck.enum_invalid",
        "severity": "error",
        "description": "Value is not in the allowed enum set for the keyword.",
    },
    {
        "code": "QE-TE003",
        "rule_id": "qe.typecheck.unit_unknown",
        "severity": "warning",
        "description": "Unknown unit specified for a physical quantity.",
    },
    {
        "code": "QE-TE004",
        "rule_id": "qe.typecheck.required_section_missing",
        "severity": "error",
        "description": "A required section is missing based on the calculation type.",
    },
    {
        "code": "QE-TW001",
        "rule_id": "qe.typecheck.numeric_range",
        "severity": "warning",
        "description": "Numeric value is outside the recommended range.",
    },
]


def get_rule_manifest() -> List[Dict[str, str]]:
    """Return a machine-readable catalogue of all diagnostic rules.

    Each entry contains:
      - code: the stable diagnostic code (e.g. ``"QE-E001"``)
      - rule_id: a dot-separated human identifier (e.g. ``"qe.input.missing_control"``)
      - severity: ``"error"`` or ``"warning"``
      - description: short summary of what the rule detects

    Returns a fresh copy on every call so callers can safely mutate.
    """
    return [dict(entry) for entry in _RULE_DEFINITIONS]


# ---------------------------------------------------------------------------
# OpenQC smoke test – integration verification
# ---------------------------------------------------------------------------

# Minimal test inputs paired with the diagnostic code they must trigger.
_SMOKE_PROBES: List[Dict[str, str]] = [
    {
        "name": "missing_control",
        "input": "&SYSTEM\n  ibrav = 2\n/\n",
        "expected_code": "QE-E008",
    },
    {
        "name": "bad_calculation",
        "input": "&CONTROL\n  calculation = 'invalid'\n/\n",
        "expected_code": "QE-E009",
    },
    {
        "name": "conv_thr_loose",
        "input": "&ELECTRONS\n  conv_thr = 1e-3\n/\n",
        "expected_code": "QE-W010",
    },
    {
        "name": "ecutrho_inconsistent",
        "input": (
            "&CONTROL\n  calculation = 'scf'\n/\n"
            "&SYSTEM\n  ibrav = 1\n  ecutwfc = 60.0\n  ecutrho = 120.0\n"
            "  nat = 1\n  ntyp = 1\n/\n"
        ),
        "expected_code": "QE-W011",
    },
    {
        "name": "occupations_degauss_mismatch",
        "input": "&SYSTEM\n  occupations = 'smearing'\n/\n",
        "expected_code": "QE-W012",
    },
    {
        "name": "invalid_kpoints_card",
        "input": "K_POINTS {bogus}\n4 4 4 0 0 0\n",
        "expected_code": "QE-E013",
    },
]


def openqc_smoke() -> Dict[str, Any]:
    """Run a lightweight integration smoke test for OpenQC consumers.

    Verifies that the following integration points are functional:

    1. **Rule manifest export** -- ``get_rule_manifest()`` returns a non-empty
       list of rule definitions.
    2. **Diagnostic engine** -- the lint provider produces diagnostics for
       malformed inputs.
    3. **Agent API** -- ``AgentAPIProvider`` can build snapshots from source
       text.
    4. **Fixture probes** -- each of the built-in smoke probes triggers the
       expected diagnostic code, confirming end-to-end rule wiring.

    Returns
    -------
    dict
        A result dict with keys:
        - ``status``: ``"pass"`` or ``"fail"``
        - ``manifest_rule_count``: number of rules in the manifest
        - ``diagnostic_engine_ok``: whether the lint provider runs
        - ``agent_api_ok``: whether the AgentAPIProvider runs
        - ``probe_results``: list of per-probe pass/fail dicts
        - ``errors``: list of error messages (empty on full pass)
    """
    from ..features.lint import LintProvider

    errors: List[str] = []
    result: Dict[str, Any] = {
        "status": "pass",
        "manifest_rule_count": 0,
        "diagnostic_engine_ok": False,
        "agent_api_ok": False,
        "probe_results": [],
        "errors": [],
    }

    # 1. Rule manifest export
    manifest = get_rule_manifest()
    result["manifest_rule_count"] = len(manifest)
    if len(manifest) == 0:
        errors.append("Rule manifest is empty.")

    # 2. Diagnostic engine responds to test inputs
    try:
        provider = LintProvider()
        provider.lint("&CONTROL\ncalculation = 'scf'\n/\n")
        result["diagnostic_engine_ok"] = True
    except Exception as exc:
        errors.append(f"Diagnostic engine error: {exc}")

    # 3. Agent API is reachable
    try:
        api = AgentAPIProvider()
        snap = api.get_snapshot("&CONTROL\ncalculation = 'scf'\n/\n")
        result["agent_api_ok"] = snap.metadata.get("language") == "quantum-espresso"
        if not result["agent_api_ok"]:
            errors.append("Agent API metadata language mismatch.")
    except Exception as exc:
        errors.append(f"Agent API error: {exc}")

    # 4. Each smoke probe triggers the expected diagnostic code
    lint_provider = LintProvider()
    for probe in _SMOKE_PROBES:
        probe_result: Dict[str, Any] = {
            "name": probe["name"],
            "expected_code": probe["expected_code"],
            "found": False,
            "status": "fail",
        }
        try:
            diags = lint_provider.lint(probe["input"])
            codes = [str(d.code) for d in diags if d.code is not None]
            probe_result["actual_codes"] = codes
            if probe["expected_code"] in codes:
                probe_result["found"] = True
                probe_result["status"] = "pass"
            else:
                errors.append(
                    f"Probe '{probe['name']}': expected code "
                    f"{probe['expected_code']}, got {codes}"
                )
        except Exception as exc:
            errors.append(f"Probe '{probe['name']}' raised: {exc}")
            probe_result["error"] = str(exc)
        result["probe_results"].append(probe_result)

    if errors:
        result["status"] = "fail"
    result["errors"] = errors

    return result

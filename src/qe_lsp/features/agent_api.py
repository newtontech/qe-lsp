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

"""Quantum ESPRESSO parameter documentation and data.

This module contains documentation for QE parameters used in hover
tooltips and completion items.
"""

from __future__ import annotations

from typing import Any

# CONTROL namelist parameters
CONTROL_PARAMS: dict[str, dict[str, Any]] = {
    "calculation": {
        "description": "Type of calculation to perform.",
        "type": "string",
        "required": True,
        "values": ["'scf'", "'nscf'", "'bands'", "'relax'", "'md'", "'vc-relax'", "'vc-md'"],
    },
    "title": {
        "description": "Title of the calculation for documentation purposes.",
        "type": "string",
    },
    "verbosity": {
        "description": "Level of output verbosity.",
        "type": "string",
        "values": ["'low'", "'medium'", "'high'"],
    },
    "restart_mode": {
        "description": "How to start the calculation.",
        "type": "string",
        "values": ["'from_scratch'", "'restart'"],
    },
    "nstep": {
        "description": "Maximum number of ionic steps.",
        "type": "integer",
        "default": 1,
    },
    "tstress": {
        "description": "Calculate stress tensor.",
        "type": "boolean",
    },
    "tprnfor": {
        "description": "Print forces.",
        "type": "boolean",
    },
    "dt": {
        "description": "Time step for molecular dynamics (in Rydberg atomic units).",
        "type": "real",
    },
    "outdir": {
        "description": "Directory for temporary output files.",
        "type": "string",
    },
    "prefix": {
        "description": "Prefix for output files.",
        "type": "string",
    },
    "pseudo_dir": {
        "description": "Directory containing pseudopotential files.",
        "type": "string",
    },
    "etot_conv_thr": {
        "description": "Energy convergence threshold (in Ry).",
        "type": "real",
    },
    "forc_conv_thr": {
        "description": "Force convergence threshold (in Ry/Bohr).",
        "type": "real",
    },
    "disk_io": {
        "description": "Level of disk I/O.",
        "type": "string",
        "values": ["'high'", "'medium'", "'low'", "'none'"],
    },
}

# SYSTEM namelist parameters
SYSTEM_PARAMS: dict[str, dict[str, Any]] = {
    "ibrav": {
        "description": "Bravais lattice index (0-14).",
        "type": "integer",
        "required": True,
        "values": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"],
    },
    "nat": {
        "description": "Number of atoms in the unit cell.",
        "type": "integer",
        "required": True,
    },
    "ntyp": {
        "description": "Number of types of atoms.",
        "type": "integer",
        "required": True,
    },
    "nbnd": {
        "description": "Number of electronic bands to calculate.",
        "type": "integer",
    },
    "ecutwfc": {
        "description": "Kinetic energy cutoff for wavefunctions (in Ry).",
        "type": "real",
        "required": True,
    },
    "ecutrho": {
        "description": "Kinetic energy cutoff for charge density (in Ry).",
        "type": "real",
    },
    "tot_charge": {
        "description": "Total charge of the system.",
        "type": "real",
        "default": 0,
    },
    "tot_magnetization": {
        "description": "Total magnetization of the system.",
        "type": "real",
    },
    "occupations": {
        "description": "Occupation distribution.",
        "type": "string",
        "values": ["'smearing'", "'tetrahedra'", "'fixed'"],
    },
    "smearing": {
        "description": "Smearing method for metals.",
        "type": "string",
        "values": ["'gaussian'", "'methfessel-paxton'"],
    },
    "degauss": {
        "description": "Smearing width (in Ry).",
        "type": "real",
    },
    "nspin": {
        "description": "Spin polarization (1, 2, or 4).",
        "type": "integer",
        "values": ["1", "2", "4"],
    },
    "noncolin": {
        "description": "Perform non-collinear calculation.",
        "type": "boolean",
    },
    "lspinorb": {
        "description": "Include spin-orbit coupling.",
        "type": "boolean",
    },
}

# ELECTRONS namelist parameters
ELECTRONS_PARAMS: dict[str, dict[str, Any]] = {
    "electron_maxstep": {
        "description": "Maximum number of SCF iterations.",
        "type": "integer",
        "default": 100,
    },
    "scf_must_converge": {
        "description": "Stop if SCF does not converge.",
        "type": "boolean",
    },
    "conv_thr": {
        "description": "SCF convergence threshold (in Ry).",
        "type": "real",
        "default": 1e-6,
    },
    "mixing_mode": {
        "description": "Charge mixing method.",
        "type": "string",
        "values": ["'plain'", "'TF'", "'local-TF'"],
    },
    "mixing_beta": {
        "description": "Mixing factor.",
        "type": "real",
        "default": 0.7,
    },
    "mixing_ndim": {
        "description": "Number of iterations used in mixing.",
        "type": "integer",
        "default": 8,
    },
    "diagonalization": {
        "description": "Diagonalization method.",
        "type": "string",
        "values": ["'david'", "'cg'"],
    },
    "startingpot": {
        "description": "Initial potential.",
        "type": "string",
        "values": ["'atomic'", "'file'"],
    },
    "startingwfc": {
        "description": "Initial wavefunctions.",
        "type": "string",
        "values": ["'atomic'", "'atomic+random'", "'file'", "'random'"],
    },
}

# IONS namelist parameters
IONS_PARAMS: dict[str, dict[str, Any]] = {
    "ion_dynamics": {
        "description": "Ion dynamics algorithm.",
        "type": "string",
        "values": ["'bfgs'", "'damp'", "'verlet'"],
    },
    "ion_temperature": {
        "description": "Temperature control method.",
        "type": "string",
    },
    "tempw": {
        "description": "Ionic temperature (in Kelvin).",
        "type": "real",
    },
    "tolp": {
        "description": "Convergence threshold for ionic minimization.",
        "type": "real",
    },
    "delta_t": {
        "description": "Time step for ionic dynamics.",
        "type": "real",
    },
    "nraise": {
        "description": "Raise temperature every nraise steps.",
        "type": "integer",
    },
    "trust_radius_max": {
        "description": "Maximum trust radius for BFGS.",
        "type": "real",
    },
    "trust_radius_min": {
        "description": "Minimum trust radius for BFGS.",
        "type": "real",
    },
    "bfgs_ndim": {
        "description": "Dimension of BFGS space.",
        "type": "integer",
    },
}

# CELL namelist parameters
CELL_PARAMS: dict[str, dict[str, Any]] = {
    "cell_dynamics": {
        "description": "Cell dynamics algorithm.",
        "type": "string",
        "values": ["'none'", "'sd'", "'bfgs'"],
    },
    "press": {
        "description": "Target pressure (in KBar).",
        "type": "real",
        "default": 0.0,
    },
    "wmass": {
        "description": "Fictitious cell mass (in atomic units).",
        "type": "real",
    },
    "cell_factor": {
        "description": "Factor for unit cell scaling.",
        "type": "real",
    },
    "press_conv_thr": {
        "description": "Pressure convergence threshold (in KBar).",
        "type": "real",
    },
}

# Combined ALL_PARAMS
ALL_PARAMS: dict[str, dict[str, dict[str, Any]]] = {
    "control": CONTROL_PARAMS,
    "system": SYSTEM_PARAMS,
    "electrons": ELECTRONS_PARAMS,
    "ions": IONS_PARAMS,
    "cell": CELL_PARAMS,
}

# Namelist suggestions (parameter names for each namelist)
NAMELIST_SUGGESTIONS: dict[str, list[str]] = {
    "control": list(CONTROL_PARAMS.keys()),
    "system": list(SYSTEM_PARAMS.keys()),
    "electrons": list(ELECTRONS_PARAMS.keys()),
    "ions": list(IONS_PARAMS.keys()),
    "cell": list(CELL_PARAMS.keys()),
}

# Card documentation
CARD_DOCS: dict[str, dict[str, str]] = {
    "ATOMIC_SPECIES": {
        "description": "Defines atomic species and pseudopotentials.",
        "format": """ATOMIC_SPECIES
  label  mass  pseudo_file""",
    },
    "ATOMIC_POSITIONS": {
        "description": "Defines atomic positions in the unit cell.",
        "format": """ATOMIC_POSITIONS { alat | bohr | angstrom | crystal }
  label  x  y  z  [if_pos(1) if_pos(2) if_pos(3)]""",
    },
    "K_POINTS": {
        "description": "Defines the k-point grid.",
        "format": """K_POINTS { automatic | gamma | crystal }""",
    },
    "CELL_PARAMETERS": {
        "description": "Defines the unit cell vectors.",
        "format": """CELL_PARAMETERS { alat | bohr | angstrom }
  v1(1) v1(2) v1(3)
  v2(1) v2(2) v2(3)
  v3(1) v3(2) v3(3)""",
    },
}


def get_param_doc(namelist: str, param: str) -> dict[str, Any] | None:
    """Get documentation for a parameter.

    Args:
        namelist: The namelist name (e.g., 'control', 'system')
        param: The parameter name

    Returns:
        Parameter documentation dict or None if not found
    """
    return ALL_PARAMS.get(namelist.lower(), {}).get(param.lower())


def get_card_doc(card: str) -> dict[str, str] | None:
    """Get documentation for a card.

    Args:
        card: The card name (e.g., 'ATOMIC_SPECIES')

    Returns:
        Card documentation dict or None if not found
    """
    return CARD_DOCS.get(card.upper())


def format_param_hover(param_doc: dict[str, Any]) -> str:
    """Format parameter documentation for hover tooltip.

    Args:
        param_doc: Parameter documentation dictionary

    Returns:
        Formatted markdown string
    """
    lines = []

    if "description" in param_doc:
        lines.append(param_doc["description"])

    if "type" in param_doc:
        lines.append(f"\n**Type:** `{param_doc['type']}`")

    if param_doc.get("required"):
        lines.append("\n⚠️ **Required parameter**")

    if "default" in param_doc:
        lines.append(f"\n**Default:** `{param_doc['default']}`")

    if "values" in param_doc:
        values_str = ", ".join(param_doc["values"])
        lines.append(f"\n**Possible values:** {values_str}")

    return "\n".join(lines)


def format_card_hover(card_doc: dict[str, str]) -> str:
    """Format card documentation for hover tooltip.

    Args:
        card_doc: Card documentation dictionary

    Returns:
        Formatted markdown string
    """
    lines = []

    if "description" in card_doc:
        lines.append(card_doc["description"])

    if "format" in card_doc:
        lines.append(f"\n**Format:**\n```\n{card_doc['format']}\n```")

    if "example" in card_doc:
        lines.append(f"\n**Example:**\n```\n{card_doc['example']}\n```")

    if "required_when" in card_doc:
        lines.append(f"\n**Required when:** {card_doc['required_when']}")

    return "\n".join(lines)


# Legacy compatibility - PARAMETER_DOCS for simple string-based access
PARAMETER_DOCS: dict[str, dict[str, str]] = {
    "control": {
        "calculation": """Type of calculation to perform.

Values:
  - 'scf': Self-consistent field (default)
  - 'nscf': Non-self-consistent field
  - 'bands': Band structure calculation
  - 'relax': Geometry relaxation
  - 'md': Molecular dynamics
  - 'vc-relax': Variable-cell relaxation
  - 'vc-md': Variable-cell molecular dynamics""",
        "title": "Title of the calculation for documentation purposes.",
        "verbosity": "Level of output verbosity (low, medium, high).",
        "restart_mode": "How to start the calculation (from_scratch, restart).",
        "nstep": "Maximum number of ionic steps (default: 1).",
        "tstress": "Calculate stress tensor (.true. or .false.).",
        "tprnfor": "Print forces (.true. or .false.).",
        "dt": "Time step for molecular dynamics (in Rydberg atomic units).",
        "outdir": "Directory for temporary output files.",
        "prefix": "Prefix for output files.",
        "pseudo_dir": "Directory containing pseudopotential files.",
        "etot_conv_thr": "Energy convergence threshold (in Ry).",
        "forc_conv_thr": "Force convergence threshold (in Ry/Bohr).",
        "disk_io": "Level of disk I/O (high, medium, low, none).",
    },
    "system": {
        "ibrav": "Bravais lattice index (0-14).",
        "nat": "Number of atoms in the unit cell.",
        "ntyp": "Number of types of atoms.",
        "nbnd": "Number of electronic bands to calculate.",
        "ecutwfc": "Kinetic energy cutoff for wavefunctions (in Ry).",
        "ecutrho": "Kinetic energy cutoff for charge density (in Ry).",
        "tot_charge": "Total charge of the system (default: 0).",
        "tot_magnetization": "Total magnetization of the system.",
        "occupations": "Occupation distribution (smearing, tetrahedra, fixed).",
        "smearing": "Smearing method for metals (gaussian, methfessel-paxton).",
        "degauss": "Smearing width (in Ry).",
        "nspin": "Spin polarization (1, 2, or 4).",
        "noncolin": "Perform non-collinear calculation (.true. or .false.).",
        "lspinorb": "Include spin-orbit coupling (.true. or .false.).",
    },
    "electrons": {
        "electron_maxstep": "Maximum number of SCF iterations (default: 100).",
        "scf_must_converge": "Stop if SCF does not converge (.true. or .false.).",
        "conv_thr": "SCF convergence threshold (in Ry).",
        "mixing_mode": "Charge mixing method (plain, TF, local-TF).",
        "mixing_beta": "Mixing factor (default: 0.7).",
        "mixing_ndim": "Number of iterations used in mixing (default: 8).",
        "diagonalization": "Diagonalization method (david, cg).",
        "startingpot": "Initial potential (atomic, file).",
        "startingwfc": "Initial wavefunctions (atomic, atomic+random, file, random).",
    },
    "ions": {
        "ion_dynamics": "Ion dynamics algorithm (bfgs, damp, verlet).",
        "ion_temperature": "Temperature control method.",
        "tempw": "Ionic temperature (in Kelvin).",
        "tolp": "Convergence threshold for ionic minimization.",
        "delta_t": "Time step for ionic dynamics.",
        "nraise": "Raise temperature every nraise steps.",
    },
    "cell": {
        "cell_dynamics": "Cell dynamics algorithm (none, sd, bfgs).",
        "press": "Target pressure (in KBar).",
        "wmass": "Fictitious cell mass (in atomic units).",
        "cell_factor": "Factor for unit cell scaling.",
        "press_conv_thr": "Pressure convergence threshold (in KBar).",
    },
}


def get_parameter_doc(namelist: str, param: str) -> str | None:
    """Get documentation for a parameter (legacy string version).

    Args:
        namelist: The namelist name (e.g., 'control', 'system')
        param: The parameter name

    Returns:
        Documentation string or None if not found
    """
    return PARAMETER_DOCS.get(namelist.lower(), {}).get(param.lower())

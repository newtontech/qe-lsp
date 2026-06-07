"""Shared constants for qe-lsp."""

SERVER_NAME = "qe-lsp"

QE_KEYWORDS = [
    "&CONTROL",
    "&SYSTEM",
    "&ELECTRONS",
    "&IONS",
    "&CELL",
    "ATOMIC_SPECIES",
    "ATOMIC_POSITIONS",
    "K_POINTS",
    "CELL_PARAMETERS",
]

QE_HOVER_DOCS = {
    "&CONTROL": "Calculation control namelist for Quantum ESPRESSO inputs.",
    "&SYSTEM": "System definition namelist, including cell, atoms, cutoffs, and occupations.",
    "&ELECTRONS": "Electronic minimization namelist for convergence and mixing settings.",
    "ATOMIC_SPECIES": "Card listing element symbols, masses, and pseudopotential files.",
    "ATOMIC_POSITIONS": "Card listing atom coordinates in crystal, angstrom, or bohr units.",
    "K_POINTS": "Card describing the reciprocal-space sampling grid.",
    "CELL_PARAMETERS": "Card providing explicit cell vectors when ibrav is 0.",
}

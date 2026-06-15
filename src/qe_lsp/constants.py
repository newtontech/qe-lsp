"""
Shared constants for qe-lsp.

See also: wiki/entities/quantum-espresso-namelist.md, wiki/entities/card.md, wiki/synthesis/control-namelist-reference.md
"""

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

QE_NAMELISTS = {"&CONTROL", "&SYSTEM", "&ELECTRONS", "&IONS", "&CELL"}

QE_CARDS = {"ATOMIC_SPECIES", "ATOMIC_POSITIONS", "K_POINTS", "CELL_PARAMETERS"}

QE_HOVER_DOCS = {
    "&CONTROL": "Calculation control namelist for Quantum ESPRESSO inputs.",
    "&SYSTEM": "System definition namelist, including cell, atoms, cutoffs, and occupations.",
    "&ELECTRONS": "Electronic minimization namelist for convergence and mixing settings.",
    "&IONS": "Ion dynamics namelist for relax and md calculations.",
    "&CELL": "Cell dynamics namelist for variable-cell calculations (vc-relax, vc-md).",
    "ATOMIC_SPECIES": "Card listing element symbols, masses, and pseudopotential files.",
    "ATOMIC_POSITIONS": "Card listing atom coordinates in crystal, angstrom, or bohr units.",
    "K_POINTS": "Card describing the reciprocal-space sampling grid.",
    "CELL_PARAMETERS": "Card providing explicit cell vectors when ibrav is 0.",
}

# Per-namelist keyword documentation for hover.
QE_PARAM_DOCS: dict[str, dict[str, str]] = {
    "&CONTROL": {
        "calculation": "Type of calculation: 'scf', 'nscf', 'bands', 'relax', 'md', 'vc-relax', 'vc-md'.",
        "title": "Job title used in output files.",
        "prefix": "Prefix for temporary and output files.",
        "outdir": "Directory for temporary and output files.",
        "wf_collect": "Collect wavefunctions at the end of the run (true/false).",
        "disk_io": "Disk I/O level: 'high', 'medium', 'low', 'none'.",
        "tprnfor": "Calculate forces (true/false).",
        "tstress": "Calculate stress (true/false).",
        "dt": "Time step for molecular dynamics (in Rydberg atomic units).",
        "nstep": "Number of ionic steps. Default: 1 for scf, 50 for relax/md.",
        "iprint": "Print info every N steps in md runs.",
        "isave": "Save restart file every N steps.",
    },
    "&SYSTEM": {
        "ibrav": "Bravais-lattice index. 0 = free, 1-14 = standard lattices.",
        "celldm": "Lattice parameters (celldm(1) = alat in Bohr). Used when ibrav > 0.",
        "a": "Lattice constant in Angstrom (alternative to celldm(1)).",
        "b": "Lattice constant b (used in some ibrav values).",
        "c": "Lattice constant c (used in some ibrav values).",
        "cosab": "Cosine of angle between a and b vectors.",
        "cosac": "Cosine of angle between a and c vectors.",
        "cosbc": "Cosine of angle between b and c vectors.",
        "nat": "Number of atoms in the cell.",
        "ntyp": "Number of atom types.",
        "nbnd": "Number of electronic bands.",
        "tot_charge": "Total charge of the system.",
        "tot_magnetization": "Fixed total magnetization for spin-polarized calculations.",
        "ecutwfc": "Kinetic energy cutoff for wavefunctions in Ry.",
        "ecutrho": "Kinetic energy cutoff for charge density and potential in Ry.",
        "occupations": "Occupation method: 'smearing', 'tetrahedra', 'fixed'.",
        "degauss": "Gaussian spreading (Ry) for smearing.",
        "smearing": "Smearing type: 'gaussian', 'methfessel-paxton', 'marzari-vanderbilt', 'fermi-dirac'.",
        "nspin": "Spin polarization: 1 = no spin, 2 = spin-polarized, 4 = noncollinear.",
        "input_dft": "Override the DFT functional from pseudopotentials.",
        "exx_fraction": "Fraction of exact exchange for hybrid functionals.",
    },
    "&ELECTRONS": {
        "conv_thr": "Convergence threshold for self-consistency (Ry).",
        "electron_maxstep": "Maximum number of SCF iterations.",
        "mixing_beta": "Mixing factor for charge-density mixing (0 < beta <= 1).",
        "mixing_mode": "Mixing mode: 'plain', 'TF', 'local-TF'.",
        "diagonalization": "Diagonalization method: 'david', 'cg', 'ppcg', 'paro', 'rmm-davidson'.",
        "diago_cg_maxiter": "Max iterations for CG diagonalization.",
        "diago_david_ndim": "Number of Davidson iterations.",
        "scf_must_converge": "Abort if SCF does not converge (true/false).",
        "startingwfc": "Starting wavefunctions: 'random', 'atomic', 'atomic+random', 'file'.",
        "startingpot": "Starting potential: 'atomic', 'file'.",
        "tqr": "Use tail-assisted quick recircularization (true/false).",
    },
    "&IONS": {
        "ion_dynamics": "Ion dynamics: 'none', 'bfgs', 'damp', 'verlet', 'langevin', 'beeman'.",
        "ion_positions": "Read ion positions from input or restart: 'default', 'from_input'.",
        "pot_extrapolation": "Potential extrapolation scheme between ionic steps.",
        "wfc_extrapolation": "Wavefunction extrapolation scheme between ionic steps.",
        "remove_rigid_rot": "Remove rigid-body rotation in MD (true/false).",
        "bfgs_ndim": "Number of old forces used in BFGS Hessian.",
        "trust_radius_max": "Maximum trust radius for BFGS (Bohr).",
        "trust_radius_min": "Minimum trust radius for BFGS (Bohr).",
        "trust_radius_ini": "Initial trust radius for BFGS (Bohr).",
    },
    "&CELL": {
        "cell_dynamics": "Cell dynamics: 'none', 'sd', 'damp-pr', 'damp-w', 'bfgs', 'pr'.",
        "press": "Target external pressure (kbar).",
        "press_conv_thr": "Convergence threshold on pressure (kbar).",
        "cell_dofree": "Degrees of freedom for cell relaxation: 'all', 'x', 'y', 'z', 'xy', 'xz', 'yz', 'xyz', 'shape', 'volume', '2Dxy', '2Dshape'.",
        "cell_factor": "Factor used to build the supercell for stress calculation.",
        "wmass": "Fictitious cell mass for variable-cell dynamics.",
    },
}

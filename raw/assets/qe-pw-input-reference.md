> Source: https://www.quantum-espresso.org/Doc/INPUT_PW.html
> Additional: https://www.quantum-espresso.org/Doc/user_guide_PDF/pw_user_guide.pdf

# pw.x Input Reference — Namelists, Cards, and Parameters

## Overview

`pw.x` is the core plane-wave self-consistent field (PWscf) code in Quantum ESPRESSO. Its input file uses a Fortran-style format with **namelists** (`&NAME ... /`) and **cards** (free-format data blocks). All quantities are in **Rydberg atomic units** unless otherwise specified. Charge is "number" charge (not multiplied by e); potentials are in energy units.

**Important:** Use only plain ASCII text files. Tabs, CRLF, or other strange characters cause trouble.

## Input File Structure

```
&CONTROL
  ...
/
&SYSTEM
  ...
/
&ELECTRONS
  ...
/
[ &IONS
  ...
/ ]
[ &CELL
  ...
/ ]
[ &FCP
  ...
/ ]
[ &RISM
  ...
/ ]
ATOMIC_SPECIES
...
ATOMIC_POSITIONS
...
K_POINTS
...
[ CELL_PARAMETERS
  ... ]
[ CONSTRAINTS
  ... ]
[ OCCUPATIONS
  ... ]
[ ATOMIC_VELOCITIES
  ... ]
[ ATOMIC_FORCES
  ... ]
[ SOLVENTS
  ... ]
[ HUBBARD
  ... ]
```

Namelists must appear in the order given above. Cards must also appear in the specified order. Namelists and cards may be missing if not needed.

---

## Namelist: &CONTROL

General calculation settings.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `calculation` | CHARACTER | 'scf' | Type of calculation: 'scf', 'nscf', 'bands', 'relax', 'md', 'vc-relax', 'vc-md' |
| `title` | CHARACTER | ' ' | Descriptive title |
| `verbosity` | CHARACTER | 'low' | Output verbosity: 'debug', 'high', 'medium', 'low', 'default', 'minimal' |
| `restart_mode` | CHARACTER | 'from_scratch' | 'from_scratch' or 'restart' |
| `wf_collect` | LOGICAL | .false. | Collect wavefunctions into a single file |
| `nstep` | INTEGER | 1 (scf/nscf/bands), 50 (md/relax) | Number of molecular-dynamics or structural optimization steps |
| `iprint` | INTEGER | 100000 | Band energies are printed every iprint iterations |
| `tstress` | LOGICAL | .false. | Calculate stress |
| `tprnfor` | LOGICAL | .false. | Print forces |
| `dt` | REAL | 20.0 (CP), 1.0 (PW) | Time step for molecular dynamics (in Rydberg atomic units) |
| `outdir` | CHARACTER | './' | Directory for input/output/temporary data |
| `wfcdir` | CHARACTER | same as outdir | Directory for large wavefunction files |
| `prefix` | CHARACTER | 'pwscf' | Prepended to input/output filenames |
| `lkpoint_dir` | LOGICAL | .false. | Use k-point-specific directories |
| `max_seconds` | REAL | 1e7 (no limit) | Wall-clock time limit in seconds |
| `etot_conv_thr` | REAL | 1e-4 Ry | Convergence threshold on total energy (for vc-relax) |
| `forc_conv_thr` | REAL | 1e-3 Ry/bohr | Convergence threshold on forces (for relax/vc-relax) |
| `disk_io` | CHARACTER | 'low' | I/O behavior: 'high', 'medium', 'low', 'minimal', 'none' |
| `pseudo_dir` | CHARACTER | $ESPRESSO_PSEUDO or './' | Directory containing pseudopotential files |
| `tefield` | LOGICAL | .false. | Add a sawtooth electric field |
| `dipfield` | LOGICAL | .false. | Add dipole correction |
| `lelfield` | LOGICAL | .false. | Add homogeneous electric field |
| `lberry` | LOGICAL | .false. | Berry phase calculation |
| `gate` | LOGICAL | .false. | Gate field calculation |
| `twochem` | LOGICAL | .false. | Two-chemical-potential calculation |
| `lfcp` | LOGICAL | .false. | Constant-potential calculation |
| `trism` | LOGICAL | .false. | 3D-RISM calculation |

---

## Namelist: &SYSTEM

System-specific variables defining the physical system.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ibrav` | INTEGER | 0 | Bravais lattice index (0-14). 0 = free (requires CELL_PARAMETERS card) |
| `celldm(i)` (i=1..6) | REAL | 0.0 | Lattice parameters: celldm(1)=alat (bohr), celldm(2-6)=b/a, c/a, cos(ab), cos(ac), cos(bc) |
| `A`, `B`, `C` | REAL | 0.0 | Lattice parameters in Angstrom (alternative to celldm) |
| `cosAB`, `cosAC`, `cosBC` | REAL | 0.0 | Cosines of lattice angles (alternative to celldm) |
| `nat` | INTEGER | — | Number of atoms in the unit cell |
| `ntyp` | INTEGER | — | Number of atom types |
| `nbnd` | INTEGER | calculated | Number of electronic states (bands) |
| `nbnd_cond` | INTEGER | 0 | Number of conduction bands for two-chemical potential |
| `tot_charge` | REAL | 0.0 | Total charge of the system |
| `tot_magnetization` | REAL | -1.0 | Total magnetization (for spin-polarized calculations) |
| `ecutwfc` | REAL | — | Kinetic energy cutoff for wavefunctions (Ry) |
| `ecutrho` | REAL | 4*ecutwfc | Kinetic energy cutoff for charge density and potential (Ry). Typically 4x ecutwfc for norm-conserving PP, 8-12x for ultrasoft/PAW |
| `ecutfock` | REAL | 0.0 | Cutoff for exact exchange (EXX) |
| `nosym` | LOGICAL | .false. | Do not use symmetry |
| `nosym_evc` | LOGICAL | .false. | Do not use symmetry to fold k-points |
| `noinv` | LOGICAL | .false. | Do not use inversion symmetry |
| `no_t_rev` | LOGICAL | .false. | Do not use time-reversal symmetry |
| `force_symmorphic` | LOGICAL | .false. | Forbid non-symmorphic symmetries |
| `occupations` | CHARACTER | 'smearing' | 'smearing', 'tetrahedra', 'tetrahedra_lin', 'tetrahedra_opt', 'from_input', 'fixed' |
| `degauss` | REAL | 0.0 Ry | Gaussian broadening width (used with smearing) |
| `smearing` | CHARACTER | 'gaussian' | Smearing method: 'gaussian', 'methfessel-paxton', 'marzari-vanderbilt', 'fermi-dirac' |
| `nspin` | INTEGER | 1 | 1 = non-spin-polarized, 2 = LSDA, 4 = noncollinear |
| `noncolin` | LOGICAL | .false. | Noncollinear magnetism |
| `lspinorb` | LOGICAL | .false. | Spin-orbit coupling |
| `input_dft` | CHARACTER | ' ' | Override the DFT functional read from pseudopotentials |
| `exx_fraction` | REAL | 0.0 | Fraction of exact exchange for hybrid functionals |
| `lda_plus_u` | LOGICAL | .false. | Enable DFT+U |
| `Hubbard_U(i)` (i=1,ntyp) | REAL | 0.0 | Hubbard U parameter per atom type (Ry) |
| `Hubbard_beta(i)` (i=1,ntyp) | REAL | 0.0 | Hubbard beta parameter (Ry) |
| `vdw_corr` | CHARACTER | 'none' | van der Waals correction: 'grimme-d2', 'grimme-d3', 'ts-vdw', 'xdm', 'dft-d3', 'rVV10' |
| `london` | LOGICAL | .false. | (Deprecated) Use Grimme D2 correction |
| `assume_isolated` | CHARACTER | 'none' | Isolation method: 'none', 'm-t', 'martyna-tuckerman', '2d', 'esm', 'dc' |

### ibrav Values (Bravais Lattice Index)

| ibrav | Description |
|-------|-------------|
| 0 | Free lattice (CELL_PARAMETERS card required) |
| 1 | Simple cubic (P) |
| 2 | Face-centered cubic (F) |
| 3 | Body-centered cubic (I) |
| -3 | Body-centered cubic (alternative) |
| 4 | Hexagonal (P) |
| 5 | Trigonal with hexagonal axis (R) |
| -5 | Trigonal with rhombohedral axis (R) |
| 6 | Tetragonal (P) |
| 7 | Tetragonal (I) |
| 8 | Orthorhombic (P) |
| 9 | Orthorhombic base-centered (C) |
| 10 | Orthorhombic face-centered (F) |
| 11 | Orthorhombic body-centered (I) |
| 12 | Monoclinic (P) |
| -12 | Monoclinic base-centered (C) |
| 13 | Monoclinic base-centered (A) |
| 14 | Triclinic (P) |

---

## Namelist: &ELECTRONS

Electronic convergence parameters for SCF.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `electron_maxstep` | INTEGER | 100 | Maximum number of SCF iterations |
| `exx_maxstep` | INTEGER | 100 | Maximum number of EXX iterations |
| `scf_must_converge` | LOGICAL | .true. | If .false., continue even if SCF doesn't converge |
| `conv_thr` | REAL | 1e-6 Ry | Energy convergence threshold for SCF |
| `adaptive_thr` | LOGICAL | .false. | Adaptive convergence threshold |
| `mixing_mode` | CHARACTER | 'plain' | Charge mixing: 'plain', 'TF', 'local-TF' |
| `mixing_beta` | REAL | 0.7 | Mixing factor for charge density (0.1-0.8 typical) |
| `mixing_ndim` | INTEGER | 8 | Number of iterations used in mixing |
| `mixing_fixed_ns` | INTEGER | 0 | Number of fixed iterations before mixing |
| `diagonalization` | CHARACTER | 'david' | 'david' (Davidson) or 'cg' (conjugate-gradient) or 'rmm-davidson' or 'paro' or 'mrgr' |
| `diago_thr_init` | REAL | 0.0 | Initial diagonalization threshold |
| `diago_cg_maxiter` | INTEGER | 20 | Max iterations for CG diagonalization |
| `diago_david_ndim` | INTEGER | 4 | Dimensional subspace for Davidson |
| `startingpot` | CHARACTER | 'atomic' | Starting potential: 'atomic', 'file', 'random' |
| `startingwfc` | CHARACTER | 'random' | Starting wavefunctions: 'random', 'atomic', 'atomic+random', 'file' |
| `tqr` | LOGICAL | .false. | Use two-quarter-grid integration |
| `real_space` | LOGICAL | .false. | Use real-space interpolation for localized orbitals |

---

## Namelist: &IONS

Ionic dynamics (used for 'relax', 'md', 'vc-relax', 'vc-md' calculations).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ion_positions` | CHARACTER | 'default' | 'default' or 'from_input' |
| `ion_dynamics` | CHARACTER | — | 'bfgs', 'sd', 'damp', 'verlet', 'langevin', 'bfgs', 'langevin-smc' |
| `ion_velocities` | CHARACTER | 'default' | 'default', 'from_input', 'random' |
| `pot_extrapolation` | CHARACTER | 'atomic' | 'none', 'atomic', 'first_order', 'second_order' |
| `wfc_extrapolation` | CHARACTER | 'none' | 'none', 'first_order', 'second_order' |
| `remove_rigid_rot` | LOGICAL | .false. | Remove rigid-body rotation from trajectory |
| `ion_temperature` | CHARACTER | 'not_controlled' | 'rescaling', 'rescale-v', 'rescale-T', 'berendsen', 'andersen', 'langevin', 'not_controlled' |
| `tempw` | REAL | 300.0 K | Target temperature |
| `refold_pos` | LOGICAL | .false. | Refold atoms into the unit cell after relaxation |
| `bfgs_ndim` | INTEGER | 1 | Number of old forces used in BFGS |
| `trust_radius_max` | REAL | 0.8 bohr | Maximum trust radius for BFGS |
| `trust_radius_min` | REAL | 1e-3 bohr | Minimum trust radius for BFGS |

---

## Namelist: &CELL

Cell dynamics (used for 'vc-relax', 'vc-md' calculations).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cell_dynamics` | CHARACTER | — | 'none', 'sd', 'damp-pr', 'damp-w', 'bfgs', 'pr', 'w', 'berendsen' |
| `press` | REAL | 0.0 kbar | Target pressure |
| `wmass` | REAL | calculated | Fictitious cell mass |
| `cell_factor` | REAL | 0.0 | Scaling factor for cell |
| `press_conv_thr` | REAL | 0.5 kbar | Convergence threshold on pressure |
| `cell_dofree` | CHARACTER | 'all' | Degrees of freedom: 'all', 'x', 'y', 'z', 'xy', 'xz', 'yz', 'xyz', 'shape', 'volume', '2Dxy', '2Dshape' |

---

## Card: ATOMIC_SPECIES

Defines atom types and their pseudopotentials.

**Format:**
```
ATOMIC_SPECIES
X  Mass_X  PseudoPot_X
```

Where:
- `X` = atom label (case-insensitive, max 3 characters)
- `Mass_X` = atomic mass in atomic mass units (amu)
- `PseudoPot_X` = pseudopotential filename

**Example:**
```
ATOMIC_SPECIES
Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF
O   15.999   O.pbe-n-rrkjus_psl.1.0.0.UPF
```

---

## Card: ATOMIC_POSITIONS

Specifies atomic positions.

**Format:**
```
ATOMIC_POSITIONS {units}
X  x  y  z  [if_pos(1)  if_pos(2)  if_pos(3)]
...
```

Units options:
- `(alat)` — in units of the lattice parameter `alat` (default)
- `(bohr)` — in Bohr
- `(angstrom)` / `(crystal)` — in Angstrom / fractional coordinates
- `(crystal_sg)` — fractional coordinates for space-group notation

`if_pos(i)` flags: 1 = allow relaxation along this direction, 0 = fix (default: all 1).

**Example:**
```
ATOMIC_POSITIONS (angstrom)
Si  0.00  0.00  0.00
Si  1.36  1.36  1.36
```

---

## Card: K_POINTS

Defines k-point mesh for Brillouin zone sampling.

**Format options:**

### Automatic mesh
```
K_POINTS {automatic}
nk1  nk2  nk3  sk1  sk2  sk3
```

### Gamma-only
```
K_POINTS {gamma}
```

### Automatic (tetrahedra)
```
K_POINTS {automatic}
nk1  nk2  nk3  0  0  0
```

### Manual list
```
K_POINTS {crystal}
nks
xk_x  xk_y  xk_z  wk
...
```

Where:
- `nk1, nk2, nk3` = Monkhorst-Pack grid dimensions
- `sk1, sk2, sk3` = offsets (0 = no offset, 1 = half-grid offset)
- `nks` = number of k-points
- `wk` = k-point weight

**Example:**
```
K_POINTS {automatic}
4 4 4  0 0 0
```

---

## Card: CELL_PARAMETERS

Explicit cell vectors (required when `ibrav = 0`).

**Format:**
```
CELL_PARAMETERS {units}
v1(1)  v1(2)  v1(3)
v2(1)  v2(2)  v2(3)
v3(1)  v3(2)  v3(3)
```

Units: `(alat)` (default), `(bohr)`, `(angstrom)`.

**Example:**
```
CELL_PARAMETERS {angstrom}
5.43  0.00  0.00
0.00  5.43  0.00
0.00  0.00  5.43
```

---

## Card: CONSTRAINTS

Optional card for constrained dynamics.

**Format:**
```
CONSTRAINTS
nconstr  constr_tol
constr_type  constr(1) .. constr(4)  constr_target
...
```

---

## Card: OCCUPATIONS

Optional card for explicit occupation numbers.

**Format:**
```
OCCUPATIONS
f_inp1(1)  f_inp1(2)  ... f_inp1(nbnd)
...  (for spin 2 if needed)
```

---

## Card: ATOMIC_VELOCITIES

Initial velocities for MD simulations.

**Format:**
```
ATOMIC_VELOCITIES
V  vx  vy  vz
...
```

---

## Card: ATOMIC_FORCES

Optional initial forces on atoms.

**Format:**
```
ATOMIC_FORCES
X  fx  fy  fz
...
```

---

## Card: HUBBARD

Hubbard parameters for DFT+U with site-specific values.

**Format (Hubbard I):**
```
HUBBARD
label(1)-manifold(1)  u_val(1)
...
```

---

## Calculation Types

| Value | Description | Namelists Required |
|-------|-------------|-------------------|
| `'scf'` | Self-consistent field calculation | &CONTROL, &SYSTEM, &ELECTRONS |
| `'nscf'` | Non-self-consistent (read potential, compute eigenvalues) | &CONTROL, &SYSTEM, &ELECTRONS |
| `'bands'` | Band structure along k-path | &CONTROL, &SYSTEM, &ELECTRONS |
| `'relax'` | Structural optimization (fixed cell) | + &IONS |
| `'md'` | Molecular dynamics (fixed cell) | + &IONS |
| `'vc-relax'` | Variable-cell structural optimization | + &IONS, &CELL |
| `'vc-md'` | Variable-cell molecular dynamics | + &IONS, &CELL |

---

## Common Parameter Guidelines

### Energy Cutoffs
- **ecutwfc**: Controls basis set quality. Typical values: 20-80 Ry for norm-conserving PP, 25-50 Ry for ultrasoft PP.
- **ecutrho**: Must be >= 4*ecutwfc for norm-conserving, typically 8-12x for ultrasoft/PAW.

### SCF Convergence
- **conv_thr**: Typically 1e-6 to 1e-8 Ry for production calculations.
- **mixing_beta**: 0.3-0.7 for insulators, 0.1-0.3 for metals. Smaller values are more stable but slower.

### K-point Mesh
- SCF: uniform grid (e.g., 4x4x4 to 12x12x12 depending on system)
- NSCF/DOS: denser grid (e.g., 8x8x8 to 24x24x24)
- Bands: path along high-symmetry lines

### Units Reference
- Length: Bohr (1 Bohr = 0.529177 Angstrom)
- Energy: Rydberg (1 Ry = 13.6057 eV)
- Mass: atomic mass units (amu)
- Time: atomic time units (1 atu = 2.4189e-17 s)

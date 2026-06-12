> Source: https://www.quantum-espresso.org/documentation/input-data-description/
> Additional: https://www.quantum-espresso.org/Doc/INPUT_CP.html, https://www.quantum-espresso.org/Doc/INPUT_PH.html, https://www.quantum-espresso.org/Doc/INPUT_PP.html, https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html

# Quantum ESPRESSO Programs Reference — Input File Formats

## Overview

Quantum ESPRESSO (QE) is a suite of codes for electronic structure calculations. Each program has its own input file format, typically consisting of Fortran-style namelists and data cards. This document covers the major executables.

---

## Complete Program List

### PWscf (Plane-Wave Self-Consistent Field)
- **pw.x** — Core DFT calculation (SCF, NSCF, bands, relax, MD, vc-relax)
- **hp.x** — Hubbard U parameters from linear response
- **bgw2pw.x** / **pw2bgw.x** — BerkeleyGW interface
- **pwcond.x** — Ballistic conductance
- **pprism.x** — 3D-RISM post-processing
- **oscdft_et.x** — Constrained DFT

### PHonon (Phonon Calculations)
- **ph.x** — Phonon frequencies and eigenvectors via DFPT
- **dynmat.x** — Dynamical matrix post-processing
- **matdyn.x** — Interpolated phonon dispersion
- **q2r.x** — Force constants from dynamical matrices
- **d3hess.x** — Third-order force constants
- **postahc.x** — Electron self-energy from electron-phonon

### CP (Car-Parrinello)
- **cp.x** — Car-Parrinello molecular dynamics
- **cppp.x** — CP post-processing

### TurboTDDFT
- **turbo_lanczos.x** — Lanczos-based TDDFT
- **turbo_spectrum.x** — Spectrum calculation
- **turbo_davidson.x** — Davidson-based TDDFT

### TurboMAGNON
- **turbo_magnon.x** — Magnon dispersion

### TurboEELS
- **turbo_eels.x** — Electron energy-loss spectroscopy

### XSpectra
- **xspectra.x** — X-ray absorption spectra

### Atomic
- **ld1.x** — Atomic pseudopotential generation

### KCW
- **kcw.x** — Koopmans-compliant functionals

### PWneb
- **neb.x** — Nudged elastic band (NEB) method

### QEHeat
- **all_currents.x** — Transport coefficients

### Post-Processing (PP)
- **pp.x** — General data extraction and plotting
- **dos.x** — Density of states
- **bands.x** — Band structure post-processing
- **band_interpolation.x** — Band interpolation
- **projwfc.x** — Projected DOS / wavefunction projections
- **molecularpdos.x** — Molecular-projected DOS
- **ppp.x** — Polarization via Berry phase
- **ppacf.x** — Atomic correlation functions
- **pw2wannier90.x** — Wannier90 interface

---

## ph.x — Phonon Input Format

Phonon calculations via density functional perturbation theory (DFPT).

### Input Structure
```
title_line
&INPUTPH
  ...
/
[xq(1) xq(2) xq(3)]       # if ldisp != .true. and qplot != .true.
[ nqs                       # if qplot == .true.
  xq1  xq2  xq3  nq
  ... ]
[ atom(1) atom(2) ... ]    # if nat_todo specified
```

### Key Parameters (&INPUTPH)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `amass(i)` | REAL | from PP | Atomic mass (amu) per type |
| `outdir` | CHARACTER | './' | Must match pw.x |
| `prefix` | CHARACTER | 'pwscf' | Must match pw.x |
| `niter_ph` | INTEGER | 100 | Max SCF iterations for phonon |
| `tr2_ph` | REAL | 1e-12 | Self-consistency threshold |
| `alpha_mix(niter)` | REAL | 0.7 | Mixing factor per iteration |
| `nmix_ph` | INTEGER | 4 | Number of mixing iterations |
| `fildyn` | CHARACTER | 'matdyn' | Output file for dynamical matrix |
| `fildrho` | CHARACTER | ' ' | Output file for charge density response |
| `fildvscf` | CHARACTER | ' ' | Output file for potential variation |
| `epsil` | LOGICAL | .false. | Calculate dielectric constant (q=0, insulator) |
| `trans` | LOGICAL | .true. | Calculate phonons |
| `lraman` | LOGICAL | .false. | Calculate Raman coefficients |
| `ldisp` | LOGICAL | .false. | Grid of q-points for dispersion |
| `nq1, nq2, nq3` | INTEGER | 0,0,0 | Monkhorst-Pack grid for q-points |
| `nk1, nk2, nk3` | INTEGER | 0,0,0 | Override k-point grid for phonon |
| `recover` | LOGICAL | .false. | Restart from interrupted run |
| `qplot` | LOGICAL | .false. | Read list of q-points |
| `electron_phonon` | CHARACTER | ' ' | 'simple', 'interpolated', 'lambda_tetra', 'gamma_tetra', 'epa', 'ahc' |
| `start_irr` / `last_irr` | INTEGER | 1 / 3*nat | Compute subset of irreducible representations |
| `start_q` / `last_q` | INTEGER | 1 / nqs | Compute subset of q-points |
| `nat_todo` | INTEGER | 0 | Displace only subset of atoms |
| `asr` | LOGICAL | .false. | Apply acoustic sum rule |

### Output
- Dynamical matrices: `outdir/_ph0/prefix.phsave/dynmat.#iq.#irr.xml`
- Displacement patterns: `outdir/_ph0/prefix.phsave/patterns.#iq.xml`

---

## cp.x — Car-Parrinello MD Input Format

Car-Parrinello ab initio molecular dynamics. All quantities in **Hartree atomic units**.

### Input Structure
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
&IONS
  ...
/
&CELL
  ...
/
[ &PRESS_AI
  ... / ]
[ &WANNIER
  ... / ]
ATOMIC_SPECIES
...
ATOMIC_POSITIONS
...
K_POINTS
...
[ CELL_PARAMETERS
  ... ]
```

### Key Differences from pw.x

| Feature | pw.x | cp.x |
|---------|------|------|
| SCF approach | Direct diagonalization/mixing | Car-Parrinello fictitious dynamics |
| Units | Rydberg atomic units | Hartree atomic units |
| Time step | dt (Ry units) | dt (Hartree units) |
| Electron dynamics | SCF iterations | Fictitious dynamics via `electron_dynamics` |
| Orthogonalization | Built-in diagonalization | Configurable (Gram-Schmidt, etc.) |

### Key cp.x Parameters

#### &ELECTRONS (cp.x-specific)
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `electron_dynamics` | CHARACTER | — | 'sd' (steepest descent), 'dm' (damped), 'verlet', 'none' |
| `emass` | REAL | — | Fictitious electron mass |
| `emass_cutoff` | REAL | 2.5 | Cutoff for fictitious electron mass |
| `orthogonalization` | CHARACTER | 'gram-schmidt' | 'gram-schmidt', 'ortho-cholesky' |
| `electron_damping` | REAL | 0.0 | Damping for electron dynamics |

#### &IONS (cp.x-specific)
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ion_dynamics` | CHARACTER | — | 'sd', 'verlet', 'damp', 'none' |
| `ion_damping` | REAL | 0.0 | Damping for ionic dynamics |
| `ion_temperature` | CHARACTER | 'not_controlled' | Temperature control |
| `ion_nstepe` | INTEGER | 1 | Electronic steps per ionic step |

---

## pp.x — Post-Processing Input Format

General-purpose data extraction from pw.x or cp.x results.

### Input Structure
```
&INPUTPP
  ...
/
&PLOT
  ... /
```

### Key &INPUTPP Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prefix` | CHARACTER | required | Must match pw.x |
| `outdir` | CHARACTER | './' | Must match pw.x |
| `filplot` | CHARACTER | 'tmp.pp' | Temporary output file |
| `plot_num` | INTEGER | -1 | Quantity to extract (see below) |
| `spin_component` | INTEGER | 0 | Spin selection (0=total, 1=up, 2=down) |
| `kpoint` | INTEGER | — | K-point selection (for plot_num=7) |
| `kband` | INTEGER | — | Band selection (for plot_num=7) |
| `emin`, `emax` | REAL | — | Energy range for LDOS/ILDOS (eV) |

### plot_num Values

| Value | Quantity |
|-------|----------|
| 0 | Electron (pseudo-)charge density |
| 1 | Total potential (V_bare + V_H + V_xc) |
| 2 | Local ionic potential (V_bare) |
| 3 | Local density of states at specific energy |
| 4 | Local density of electronic entropy |
| 5 | STM images (Tersoff-Hamann) |
| 6 | Spin polarization (rho_up - rho_down) |
| 7 | |psi|^2 for selected wavefunctions |
| 8 | Electron localization function (ELF) |
| 9 | Charge density minus atomic density |
| 10 | Integrated LDOS (emin to emax) |
| 11 | V_bare + V_H potential |
| 12 | Sawtooth electric field potential |
| 13 | Noncollinear magnetization |
| 17 | All-electron valence charge (PAW only) |
| 19 | Reduced density gradient |
| 22 | Kinetic energy density |

### Key &PLOT Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `nfile` | INTEGER | Number of data files |
| `filepp(i)` | CHARACTER | Input data file(s) |
| `weight(i)` | REAL | Linear combination weights |
| `iflag` | INTEGER | 0=spherical avg, 1=1D, 2=2D, 3=3D, 4=polar |
| `output_format` | INTEGER | 0=gnuplot, 3=XCRYSDEN, 5=XCRYSDEN 3D, 6=Gaussian cube |
| `fileout` | CHARACTER | Output plot file |
| `interpolation` | CHARACTER | 'fourier' (default) or 'bspline' |

---

## dos.x — Density of States Input Format

Calculates total density of states from pw.x output.

### Input Structure
```
&DOS
  prefix = '...',
  outdir = '...',
  fildos = 'dos.dat',
  Emin = ...,
  Emax = ...,
  DeltaE = ...
/
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prefix` | CHARACTER | 'pwscf' | Must match pw.x |
| `outdir` | CHARACTER | './' | Must match pw.x |
| `fildos` | CHARACTER | 'dos.dat' | Output file name |
| `Emin` | REAL | band minimum | Minimum energy (eV) |
| `Emax` | REAL | band maximum | Maximum energy (eV) |
| `DeltaE` | REAL | 0.01 | Energy grid step (eV) |

### Output Format
Two columns: energy (eV) and DOS (states/eV).

---

## bands.x — Band Structure Post-Processing

Extracts and reformats band structure from pw.x bands calculation.

### Input Structure
```
&BANDS
  prefix = '...',
  outdir = '...',
  filband = 'bands.dat',
  ...
/
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prefix` | CHARACTER | 'pwscf' | Must match pw.x |
| `outdir` | CHARACTER | './' | Must match pw.x |
| `filband` | CHARACTER | 'bands.dat' | Output band data file |
| `lsym` | LOGICAL | .true. | Symmetrize bands |

### Workflow
1. Run `pw.x` with `calculation = 'scf'` (compute ground state)
2. Run `pw.x` with `calculation = 'bands'` (compute eigenvalues along k-path)
3. Run `bands.x` to extract and plot band data

---

## projwfc.x — Projected DOS Input Format

Projects wavefunctions onto orthogonalized atomic orbitals and calculates projected DOS.

### Input Structure
```
&PROJWFC
  prefix = '...',
  outdir = '...',
  ...
/
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prefix` | CHARACTER | 'pwscf' | Must match pw.x |
| `outdir` | CHARACTER | './' | Must match pw.x |
| `ngauss` | INTEGER | 0 | Broadening type: 0=Simple Gaussian, 1=Methfessel-Paxton, -1=Marzari-Vanderbilt, -99=Fermi-Dirac |
| `degauss` | REAL | 0.0 | Gaussian broadening (Ry) |
| `Emin`, `Emax` | REAL | band extrema | Energy range (eV) |
| `DeltaE` | REAL | — | Energy grid step (eV) |
| `filpdos` | CHARACTER | prefix | Output file prefix for PDOS |
| `filproj` | CHARACTER | stdout | Output file for projections |
| `lsym` | LOGICAL | .true. | Symmetrize projections |
| `kresolveddos` | LOGICAL | .false. | Compute k-resolved DOS |

### Output Files
- `{filpdos}.pdos_tot` — Total DOS and sum of projected DOS
- `{filpdos}.pdos_atm#N(X)_wfc#M(l)` — Per-atom projected DOS
- `{filpdos}.pdos_atm#N(X)_wfc#M(l_j)` — With spin-orbit coupling

---

## matdyn.x — Phonon Dispersion Interpolation

Interpolates phonon frequencies from a coarse q-grid to arbitrary q-points.

### Input Structure
```
&INPUT
  asr = '',
  amass(1) = ...,
  flfrc = '...',
  flfrq = '...',
  q_in_band_form = .true.,
  ...
/
nqs
q1  q2  q3  nq
...
```

### Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `asr` | CHARACTER | Acoustic sum rule: 'no', 'simple', 'crystal', 'one-dim', 'zero-dim' |
| `flfrc` | CHARACTER | Input force constants file (from q2r.x) |
| `flfrq` | CHARACTER | Output phonon frequencies file |
| `q_in_band_form` | LOGICAL | Interpolate between listed q-points |
| `dos` | LOGICAL | Compute phonon DOS |
| `nk1, nk2, nk3` | INTEGER | Grid for phonon DOS |

---

## q2r.x — Force Constants

Transforms dynamical matrices to real-space force constants.

### Input Structure
```
&INPUT
  fildyn = '...',
  zasr = '',
  loto_2d = .false.
/
```

---

## dynmat.x — Dynamical Matrix Utilities

Post-processes dynamical matrices.

### Input Structure
```
&INPUT
  fildyn = '...',
  asr = '',
  ...
/
```

---

## Common Workflow Patterns

### Phonon Calculation
```
1. pw.x (scf)  →  ground state
2. ph.x        →  dynamical matrices on q-grid
3. q2r.x       →  real-space force constants
4. matdyn.x    →  phonon dispersion / DOS
```

### Band Structure
```
1. pw.x (scf)      →  ground state
2. pw.x (bands)    →  eigenvalues along k-path
3. bands.x         →  extract band data
```

### DOS and Projected DOS
```
1. pw.x (scf)      →  ground state
2. pw.x (nscf)     →  eigenvalues on dense k-grid
3. dos.x           →  total DOS
4. projwfc.x       →  projected DOS
```

### Charge Density / Potential Plotting
```
1. pw.x (scf)      →  ground state
2. pp.x            →  extract quantity + plot
```

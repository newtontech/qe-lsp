> Source: https://www.quantum-espresso.org/Doc/INPUT_PW.html
> Additional: https://pranabdas.github.io/espresso/hands-on/dos/, https://mattermodeling.stackexchange.com/questions/11814/, https://wiki.max-centre.eu/index.php/Non_self-consistent_calculations, https://www.paradim.org/sites/default/files/2019-05/QE-Input_and_Convergence_Parameters.pdf

# Quantum ESPRESSO Example Input Files

## Overview

This document provides annotated example input files for the most common Quantum ESPRESSO calculation types. Each example uses silicon (Si, diamond structure, FCC) as the model system.

---

## 1. Self-Consistent Field (SCF) Calculation

The fundamental calculation: obtains the ground-state charge density and total energy.

```fortran
&CONTROL
  calculation = 'scf'
  prefix = 'silicon'
  outdir = './tmp/'
  pseudo_dir = './pseudo/'
  etot_conv_thr = 1.0d-6
  forc_conv_thr = 1.0d-3
  tstress = .true.
  tprnfor = .true.
/

&SYSTEM
  ibrav = 2
  celldm(1) = 10.26        ! lattice parameter in Bohr (Si: 5.43 Angstrom)
  nat = 2
  ntyp = 1
  ecutwfc = 30.0           ! kinetic energy cutoff for wavefunctions (Ry)
  ecutrho = 240.0          ! kinetic energy cutoff for charge density (Ry)
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 0.01           ! smearing width (Ry)
/

&ELECTRONS
  conv_thr = 1.0d-8        ! SCF convergence threshold (Ry)
  mixing_beta = 0.7
  electron_maxstep = 100
/

ATOMIC_SPECIES
  Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
  Si  0.00  0.00  0.00
  Si  0.25  0.25  0.25

K_POINTS {automatic}
  8 8 8  0 0 0
```

### Key Notes
- `ibrav = 2` for FCC lattice; `celldm(1)` is the side length in Bohr
- For ultrasoft PP: `ecutrho = 8 * ecutwfc` (or larger)
- For norm-conserving PP: `ecutrho = 4 * ecutwfc`
- `occupations = 'smearing'` is required for metals; for insulators `fixed` or `smearing` both work

---

## 2. Non-Self-Consistent Field (NSCF) Calculation

Reads the ground-state potential from a prior SCF run and computes eigenvalues on a denser k-grid. Used for DOS and other post-processing.

```fortran
&CONTROL
  calculation = 'nscf'
  prefix = 'silicon'
  outdir = './tmp/'
  pseudo_dir = './pseudo/'
/

&SYSTEM
  ibrav = 2
  celldm(1) = 10.26
  nat = 2
  ntyp = 1
  ecutwfc = 30.0
  ecutrho = 240.0
  nbnd = 12                ! more bands than occupied states for DOS
  occupations = 'tetrahedra'
  nosym = .true.           ! avoid generating extra k-points
/

&ELECTRONS
  conv_thr = 1.0d-8
/

ATOMIC_SPECIES
  Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
  Si  0.00  0.00  0.00
  Si  0.25  0.25  0.25

K_POINTS {automatic}
  12 12 12  0 0 0
```

### Key Notes
- `prefix` and `outdir` must match the SCF calculation
- `occupations = 'tetrahedra'` is recommended for DOS (more accurate integration)
- `nbnd` should include unoccupied bands (check SCF output for number of Kohn-Sham states)
- `nosym = .true.` prevents symmetry from generating additional k-points
- K-grid is typically denser than SCF (e.g., 12x12x12 vs 8x8x8)

---

## 3. Band Structure Calculation

Computes eigenvalues along high-symmetry k-path. Requires SCF first.

### Step 1: SCF (same as above)

### Step 2: Bands calculation
```fortran
&CONTROL
  calculation = 'bands'
  prefix = 'silicon'
  outdir = './tmp/'
  pseudo_dir = './pseudo/'
/

&SYSTEM
  ibrav = 2
  celldm(1) = 10.26
  nat = 2
  ntyp = 1
  ecutwfc = 30.0
  ecutrho = 240.0
  nbnd = 12
/

&ELECTRONS
  conv_thr = 1.0d-8
/

ATOMIC_SPECIES
  Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
  Si  0.00  0.00  0.00
  Si  0.25  0.25  0.25

K_POINTS {crystal}
5                          ! number of k-points along path
  0.500  0.500  0.500  10  ! L point
  0.000  0.000  0.000  10  ! Gamma point
  0.500  0.000  0.500  10  ! X point
  0.375  0.375  0.750  10  ! K point (approximate)
  0.000  0.000  0.000   1  ! Gamma point (return)
```

### Step 3: Post-process with bands.x
```fortran
&BANDS
  prefix = 'silicon'
  outdir = './tmp/'
  filband = 'si_bands.dat'
/
```

### Key Notes
- Use `{crystal}` coordinates for k-points
- The weight column specifies the number of interpolation points between consecutive k-points
- Common high-symmetry points for FCC: Gamma (0,0,0), X (0.5,0,0.5), L (0.5,0.5,0.5), W (0.5,0.25,0.75), K (0.375,0.375,0.75)

---

## 4. DOS Calculation (using dos.x)

Complete workflow for density of states.

### Step 1: SCF (see above)

### Step 2: NSCF with dense k-grid (see NSCF example above)

### Step 3: DOS with dos.x
```fortran
&DOS
  prefix = 'silicon'
  outdir = './tmp/'
  fildos = 'si_dos.dat'
  Emin = -10.0
  Emax = 20.0
/
```

### Step 4 (optional): Projected DOS with projwfc.x
```fortran
&PROJWFC
  prefix = 'silicon'
  outdir = './tmp/'
  filpdos = 'si_pdos'
  Emin = -10.0
  Emax = 20.0
  DeltaE = 0.01
/
```

### Output Files
- `si_dos.dat` — Energy (eV) vs DOS (states/eV)
- `si_pdos.pdos_tot` — Total projected DOS
- `si_pdos.pdos_atm#1(Si)_wfc#1(s)` — Si s-projected DOS
- `si_pdos.pdos_atm#1(Si)_wfc#2(p)` — Si p-projected DOS

---

## 5. Structural Relaxation (relax)

Optimizes atomic positions at fixed cell shape.

```fortran
&CONTROL
  calculation = 'relax'
  prefix = 'silicon'
  outdir = './tmp/'
  pseudo_dir = './pseudo/'
  etot_conv_thr = 1.0d-5
  forc_conv_thr = 1.0d-4
  nstep = 100
/

&SYSTEM
  ibrav = 2
  celldm(1) = 10.26
  nat = 2
  ntyp = 1
  ecutwfc = 30.0
  ecutrho = 240.0
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 0.01
/

&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
/

&IONS
  ion_dynamics = 'bfgs'
/

ATOMIC_SPECIES
  Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
  Si  0.00  0.00  0.00
  Si  0.25  0.25  0.25

K_POINTS {automatic}
  8 8 8  0 0 0
```

### Key Notes
- `&IONS` namelist is required for relax/md calculations
- `ion_dynamics = 'bfgs'` is most efficient for insulators
- `ion_dynamics = 'damp'` is often more robust for metals
- `refold_pos = .true.` can be added to &IONS to refold atoms into the unit cell

---

## 6. Variable-Cell Relaxation (vc-relax)

Optimizes both atomic positions and cell shape/volume.

```fortran
&CONTROL
  calculation = 'vc-relax'
  prefix = 'silicon'
  outdir = './tmp/'
  pseudo_dir = './pseudo/'
  etot_conv_thr = 1.0d-5
  forc_conv_thr = 1.0d-4
  nstep = 100
/

&SYSTEM
  ibrav = 2
  celldm(1) = 10.5         ! initial guess (slightly off)
  nat = 2
  ntyp = 1
  ecutwfc = 30.0
  ecutrho = 240.0
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 0.01
/

&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
/

&IONS
  ion_dynamics = 'bfgs'
/

&CELL
  cell_dynamics = 'bfgs'
  press = 0.0              ! target pressure in kbar
  press_conv_thr = 0.5     ! pressure convergence (kbar)
  cell_dofree = 'all'
/

ATOMIC_SPECIES
  Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
  Si  0.00  0.00  0.00
  Si  0.25  0.25  0.25

K_POINTS {automatic}
  8 8 8  0 0 0
```

### Key Notes
- `&CELL` namelist is required
- `cell_dynamics = 'bfgs'` is recommended
- `cell_dofree` controls which cell degrees of freedom are optimized
- `cell_factor` (default: 2.0 for vc-relax) controls the cell scaling
- For 2D materials: `cell_dofree = '2Dxy'` or `'2Dshape'`

---

## 7. Molecular Dynamics (md)

Born-Oppenheimer molecular dynamics at fixed cell.

```fortran
&CONTROL
  calculation = 'md'
  prefix = 'silicon'
  outdir = './tmp/'
  pseudo_dir = './pseudo/'
  dt = 20.0                ! time step in Rydberg atomic units (~0.48 fs)
  nstep = 1000
/

&SYSTEM
  ibrav = 2
  celldm(1) = 10.26
  nat = 2
  ntyp = 1
  ecutwfc = 30.0
  ecutrho = 240.0
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 0.01
/

&ELECTRONS
  conv_thr = 1.0d-6
  mixing_beta = 0.7
/

&IONS
  ion_dynamics = 'verlet'
  ion_temperature = 'rescaling'
  tempw = 300.0            ! target temperature (K)
/

ATOMIC_SPECIES
  Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
  Si  0.00  0.00  0.00
  Si  0.25  0.25  0.25

K_POINTS {automatic}
  4 4 4  0 0 0
```

### Key Notes
- `dt` is in Rydberg atomic units: 1 Ry au = 4.8378e-17 s (so dt=20 ~ 0.97 fs)
- Common thermostats: 'rescaling', 'berendsen', 'andersen', 'langevin'
- For NPT: use `calculation = 'vc-md'` with `&CELL`
- Typical dt: 1-50 au (0.02-2.4 fs) depending on system

---

## 8. Phonon Calculation (ph.x)

Computes phonon frequencies via DFPT.

### Step 1: SCF (see above)
Make sure `tstress = .true.` and `tprnfor = .true.` in &CONTROL.

### Step 2: ph.x calculation
```fortran
Phonon for Silicon
&INPUTPH
  prefix = 'silicon'
  outdir = './tmp/'
  fildyn = 'si.dyn'
  tr2_ph = 1.0d-14
  ldisp = .true.
  nq1 = 4
  nq2 = 4
  nq3 = 4
  trans = .true.
  epsil = .true.
/
```

### For single q-point
```fortran
Phonon at Gamma
&INPUTPH
  prefix = 'silicon'
  outdir = './tmp/'
  fildyn = 'si.dyn0'
  tr2_ph = 1.0d-14
  trans = .true.
  epsil = .true.
/
0.0 0.0 0.0
```

### Step 3: Post-process
```fortran
! q2r.x — generate force constants
&INPUT
  fildyn = 'si.dyn'
  zasr = 'crystal'
/

! matdyn.x — phonon dispersion
&INPUT
  asr = 'crystal'
  flfrc = 'si.fc'
  flfrq = 'si.freq'
  q_in_band_form = .true.
/
5
  0.500  0.500  0.500  20  ! L
  0.000  0.000  0.000  20  ! Gamma
  0.500  0.000  0.500  20  ! X
  0.375  0.375  0.750  20  ! K
  0.000  0.000  0.000   1  ! Gamma
```

---

## 9. Spin-Polarized Calculation

For magnetic systems.

```fortran
&CONTROL
  calculation = 'scf'
  prefix = 'iron'
  outdir = './tmp/'
  pseudo_dir = './pseudo/'
/

&SYSTEM
  ibrav = 1
  celldm(1) = 5.42         ! BCC Fe in Bohr
  nat = 1
  ntyp = 1
  ecutwfc = 40.0
  ecutrho = 320.0
  nspin = 2                ! spin-polarized
  occupations = 'smearing'
  smearing = 'marzari-vanderbilt'
  degauss = 0.01
  starting_magnetization(1) = 0.6   ! initial magnetic moment
/

&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.3        ! smaller for metals
/

ATOMIC_SPECIES
  Fe  55.845  Fe.pbe-spn-kjpaw_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
  Fe  0.0  0.0  0.0

K_POINTS {automatic}
  12 12 12  0 0 0
```

### Key Notes
- `nspin = 2` for collinear spin-polarized (LSDA)
- `starting_magnetization(i)` provides initial guess for each atom type
- Use smaller `mixing_beta` (0.1-0.3) for metals

---

## 10. Free-Format Cell (ibrav = 0)

When the Bravais lattice does not match a standard type.

```fortran
&CONTROL
  calculation = 'scf'
  prefix = 'sio2'
  outdir = './tmp/'
  pseudo_dir = './pseudo/'
/

&SYSTEM
  ibrav = 0                ! free format
  nat = 9
  ntyp = 2
  ecutwfc = 50.0
  ecutrho = 400.0
/

&ELECTRONS
  conv_thr = 1.0d-8
/

ATOMIC_SPECIES
  Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF
  O   15.999   O.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
  Si  0.000  0.000  0.000
  Si  0.500  0.500  0.000
  O   0.250  0.250  0.000
  O   0.750  0.750  0.000
  O   0.000  0.500  0.250
  O   0.000  0.500  0.750
  O   0.500  0.000  0.250
  O   0.500  0.000  0.750
  O   0.250  0.000  0.000

K_POINTS {automatic}
  4 4 4  0 0 0

CELL_PARAMETERS {angstrom}
  4.913  0.000  0.000
  0.000  4.913  0.000
  0.000  0.000  5.405
```

### Key Notes
- `ibrav = 0` requires the CELL_PARAMETERS card
- `celldm` and A/B/C parameters are ignored when ibrav=0
- CELL_PARAMETERS unit options: `{alat}`, `{bohr}`, `{angstrom}`

---

## Calculation Workflow Summary

| Workflow | Step 1 | Step 2 | Step 3 | Step 4 |
|----------|--------|--------|--------|--------|
| Energy only | pw.x (scf) | | | |
| Band structure | pw.x (scf) | pw.x (bands) | bands.x | |
| Total DOS | pw.x (scf) | pw.x (nscf) | dos.x | |
| Projected DOS | pw.x (scf) | pw.x (nscf) | projwfc.x | |
| Relaxation | pw.x (relax) | | | |
| Cell+relax | pw.x (vc-relax) | pw.x (scf) | ... | |
| Phonons | pw.x (scf) | ph.x | q2r.x | matdyn.x |
| MD | pw.x (md) | | | |
| Spin-polarized | pw.x (scf, nspin=2) | | | |

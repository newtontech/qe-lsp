> Source: https://www.quantum-espresso.org/Doc/pw_user_guide/node9.html
> Additional: https://blog.levilentz.com/parse-quantum-espresso-output-file/, https://ase-lib.org/_modules/ase/io/espresso.html

# Quantum ESPRESSO Output File Format Reference

## Overview

Quantum ESPRESSO produces several types of output:
1. **Standard output** (stdout) — Human-readable text with calculation details
2. **Data files** — Binary/XML files in `outdir/prefix.save/`
3. **Post-processing files** — Text files from dos.x, bands.x, projwfc.x, etc.

This document covers the structure and format of each output type, with guidance for parsing.

---

## 1. Standard Output (pw.x stdout)

The text output of pw.x is the primary human-readable output. Key sections appear in order:

### 1.1 Header

```
     Program PWSCF v.7.3.1 starts on 13Jun2024 at 10:30:00

     This program is part of the open-source Quantum ESPRESSO suite
```

Contains:
- Program version
- Start date/time
- Number of MPI processes and OpenMP threads

### 1.2 Input Echo

The entire input file is echoed to output.

### 1.3 General Information

```
     lattice parameter (alat)  =       10.2600  a.u.
     unit-cell volume          =      270.26465 (a.u.)^3
     number of atoms/cell      =            2
     number of atomic types    =            1
     number of Kohn-Sham states=            8
     kinetic-energy cutoff     =       30.0000  Ry
     charge density cutoff     =      240.0000  Ry
     convergence threshold     :       1.0E-08
     mixing beta               :       0.7000
     number of iterations used :       8  plain mixing
     Exchange-correlation      :  PBE ( 1 1 1 1 0 0)
```

Extractable fields:
| Field | Marker string | Units |
|-------|--------------|-------|
| Version | `Program PWSCF` | — |
| Lattice parameter | `lattice parameter (alat)` | Bohr |
| Cell volume | `unit-cell volume` | Bohr^3 |
| Number of atoms | `number of atoms/cell` | — |
| Atom types | `number of atomic types` | — |
| Bands | `number of Kohn-Sham states` | — |
| ecutwfc | `kinetic-energy cutoff` | Ry |
| ecutrho | `charge density cutoff` | Ry |
| conv_thr | `convergence threshold` | Ry |
| mixing_beta | `mixing beta` | — |
| XC functional | `Exchange-correlation` | — |
| Electrons | `number of electrons` | — |

### 1.4 Lattice Vectors

```
     cart. coord. in units of alat
       a(1) = (   0.500000   0.000000   0.500000 )
       a(2) = (   0.000000   0.500000   0.500000 )
       a(3) = (   0.500000   0.000000  -0.500000 )
```

### 1.5 K-Points

```
     number of k points=    8
     cart. coord. in units 2pi/alat
       k(    1) = (   0.0000000   0.0000000   0.0000000), wk =  0.0312500
       ...
```

### 1.6 Atomic Positions

```
     site n.     atom                  positions (alat units)
         1           Si  tau(   1) = (   0.0000000   0.0000000   0.0000000 )
         2           Si  tau(   2) = (   2.5650000   2.5650000   2.5650000 )
```

### 1.7 SCF Iteration

Each SCF step produces:
```
     iteration #  1     ecut=    30.00Ry     rms=  3.21E+00
     ...
     iteration # 12     ecut=    30.00Ry     rms=  8.34E-09

     end of bfgs converged iteration   ... total energy =   -15.84920123 Ry
```

Key marker: the `!` before total energy indicates the final converged value:
```
!    total energy              =    -15.84920123 Ry
```

### 1.8 Eigenvalues

After SCF convergence:
```
     k = 0.0000 0.0000 0.0000 (    1 PWs)   bands (ev):

    -6.6424   5.6475   5.6475   5.6475   6.2836   6.2836   6.2836   8.4931
```

Format: 8 eigenvalues per line, in eV.

### 1.9 Total Energy Components

```
     The total energy is the sum of the following terms:

     one-electron contribution =   -31.69884537 Ry
     hartree contribution      =     17.91737450 Ry
     xc contribution           =    -7.36525842 Ry
     ewald contribution        =    -0.27135703 Ry

!    total energy              =    -15.84920123 Ry

     Harris-Foulkes estimate   =    -15.84920123 Ry
     estimated scf accuracy    <     8.344E-09 Ry

     The total energy is  -15.84920123 Ry
```

### 1.10 Forces

```
     Forces acting on atoms (Ry/au):

     atom   1 type  1   force =     0.00000000   0.00000000   0.00000000
     atom   2 type  1   force =     0.00000000   0.00000000   0.00000000

     Total force =     0.000000     Total SCF correction =     0.000000
```

### 1.11 Stress Tensor

```
     total   stress  (Ry/bohr**3)                   (kbar)     P=       0.03
   -0.00000026   0.00000000   0.00000000        -0.04      0.00      0.00
    0.00000000  -0.00000026   0.00000000         0.00     -0.04      0.00
    0.00000000   0.00000000  -0.00000026         0.00      0.00     -0.04
```

### 1.12 Band Gap

```
     highest occupied, lowest unoccupied level (ev):     6.2836    6.2974
```

### 1.13 Fermi Energy

```
     the Fermi energy is    6.6424 ev
```

### 1.14 Final Coordinates (relax/vc-relax)

```
     Begin final coordinates

     CELL_PARAMETERS (alat= 10.25882)
       0.500000000   0.000000000   0.500000000
       0.000000000   0.500000000   0.500000000
       0.500000000   0.000000000  -0.500000000

     ATOMIC_POSITIONS (crystal)
       Si   0.000000000   0.000000000   0.000000000
       Si   0.250000000   0.250000000   0.250000000
     End final coordinates
```

---

## 2. Data Files (outdir/prefix.save/)

After an SCF calculation, QE writes binary/XML data to `outdir/prefix.save/`:

### Key Files

| File | Description |
|------|-------------|
| `charge-density.dat` | Self-consistent charge density |
| `data-file.xml` | XML metadata (cell, atoms, k-points, etc.) |
| `evc.dat` / `wfc.dat` | Wavefunctions |
| `paw*.dat` | PAW-specific data (if PAW) |
| `spin-polarization.dat` | Magnetization density (if nspin=2) |

### data-file.xml Structure

Contains structured XML with:
- Cell vectors and parameters
- Atomic species and positions
- K-points and weights
- Band structure metadata
- Symmetry operations
- Simulation parameters

### Wavefunction Files
- Format: unformatted Fortran binary
- Location: `outdir/prefix.save/K00001/evc01.dat` etc. (one per k-point pool)
- Can be read by pp.x, projwfc.x, and other post-processing tools

---

## 3. Post-Processing Output Formats

### 3.1 dos.x Output (fildos)

Plain text, two columns:
```
  E (eV)    DOS (states/eV)
  -9.000    0.000
  -8.990    0.001
  ...
```

### 3.2 bands.x Output (filband)

Plain text with band eigenvalues:
```
  &plot nbnd=12, nks=50
  0.500  0.500  0.500    ! k-point
  -5.234   3.456   ...   ! eigenvalues for this k-point (eV)
  ...
```

Can be read by plotting tools or converted to plottable format.

### 3.3 projwfc.x Output (filpdos)

Multiple files:
- `{filpdos}.pdos_tot`: E, DOS(E), PDOS(E)
- `{filpdos}.pdos_atm#N(X)_wfc#M(l)`: E, LDOS(E), PDOS_1(E), ..., PDOS_2l+1(E)

For spin-polarized:
- Columns double: DOSup, DOSdw, PDOSup, PDOSdw

### 3.4 pp.x Output

Depends on `output_format`:
- Format 0: gnuplot-compatible 1D data
- Format 3: XCRYSDEN 2D/3D format
- Format 5: XCRYSDEN 3D (entire FFT grid)
- Format 6: Gaussian cube file (readable by VESTA, VMD, etc.)

### 3.5 Phonon Output

**Dynamical matrices** (from ph.x):
- Binary format in `outdir/_ph0/prefix.phsave/dynmat.#iq.#irr.xml`
- XML format for recoverability

**Force constants** (from q2r.x):
- Real-space interatomic force constants
- Text format

**Phonon frequencies** (from matdyn.x):
```
       q =  0.0000  0.0000  0.0000
  omega(  1) =       -0.000001 [THz] =       -0.000003 [cm-1]
  omega(  2) =       -0.000001 [THz] =       -0.000003 [cm-1]
  omega(  3) =        0.000001 [THz] =        0.000003 [cm-1]
  omega(  4) =       15.634703 [THz] =      521.483667 [cm-1]
  ...
```

---

## 4. Parsing Strategies

### 4.1 Key Markers for Text Parsing

| Data | Marker | Extraction |
|------|--------|-----------|
| Final energy | `!    total energy` | `!` at line start means final converged value |
| SCF energy | `total energy =` (no `!`) | Intermediate SCF energy |
| Fermi level | `the Fermi energy is` | Value in eV |
| Band gap | `highest occupied, lowest unoccupied` | Two values in eV |
| Cell volume | `unit-cell volume` | Bohr^3 (multiply by 0.148185 for Angstrom^3) |
| Forces | `Forces acting on atoms` | Block of nat lines, Ry/au |
| Stress | `total   stress` | 3x3 tensor |
| Converged SCF | `convergence has been achieved` | Boolean |
| New cell volume | `new unit-cell volume` | After vc-relax |
| Final coordinates | `Begin final coordinates` | Block until `End final coordinates` |

### 4.2 Unit Conversion

| From | To | Factor |
|------|-----|--------|
| Bohr | Angstrom | 0.529177 |
| Ry | eV | 13.6057 |
| Ry/bohr | eV/Angstrom | 25.7112 |
| Ry/bohr^3 | kbar | 4107.87 |
| Bohr^3 | Angstrom^3 | 0.148185 |
| Ry*atu | fs | 0.02419 |

### 4.3 XML Output Parsing

For programmatic access, the XML data files are more reliable than text parsing:
- `data-file.xml` contains all simulation metadata
- Phonon dynamical matrices are in XML format
- Use standard XML parsers (Python lxml, etc.)

### 4.4 Libraries for Parsing QE Output

| Library | Language | URL |
|---------|----------|-----|
| ASE | Python | https://ase-lib.org/ (ase.io.espresso) |
| AiiDA | Python | https://www.aiida.net/ |
| NOMAD parser | Python | https://github.com/nomad-coe/nomad-parser-quantum-espresso |
| qe-tools | Python | https://github.com/aiidateam/qe-tools |
| pwtools | Python | https://github.com/elcorto/pwtools |

---

## 5. Common Output Sections by Calculation Type

### SCF
Header -> Input echo -> General info -> Lattice -> K-points -> SCF iterations -> Energy -> Forces (if tprnfor) -> Stress (if tstress)

### NSCF
Same as SCF but eigenvalues are printed for all k-points with band energies.

### Bands
Header -> Input echo -> General info -> Eigenvalues along k-path

### Relax
Header -> Input echo -> SCF -> Forces -> BFGS step -> SCF -> Forces -> ... -> Converged -> Final coordinates

### vc-relax
Similar to relax but with CELL_PARAMETERS update at each step. Final output includes optimized cell.

### MD
Each MD step produces SCF + forces + positions. Trajectory data may be written to file.

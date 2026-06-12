> Source: https://www.quantum-espresso.org/pseudopotentials/
> Additional: https://pseudopotentials.quantum-espresso.org/, https://www.scm.com/doc/QuantumEspresso/pseudopotentials.html, https://github.com/dalcorso/pslibrary

# Quantum ESPRESSO Pseudopotential Formats and Libraries

## Overview

Quantum ESPRESSO (QE) uses **pseudopotentials (PPs)** to replace the strong electron-ion interaction with an effective potential acting on valence electrons only. QE supports multiple PP types and uses a unified format (UPF) for all of them.

---

## 1. Pseudopotential Types

### 1.1 Norm-Conserving (NC)
- Most general compatibility (all calculation types)
- Required for: meta-GGA functionals, Gamma-only phonon, Raman, anharmonic force constants
- Higher energy cutoff typically needed
- Kleinman-Bylander separable form

### 1.2 Ultrasoft (US)
- Softer (lower energy cutoff) than NC
- Not compatible with some advanced features
- More efficient for large systems
- ecutrho typically 8-12x ecutwfc

### 1.3 Projector Augmented Wave (PAW)
- Similar efficiency to ultrasoft
- Most accurate for many properties
- All-electron reconstruction available
- Not yet supported by CP code
- Requires PAW-specific data in PP file

### Compatibility Matrix

| Feature | NC | US | PAW |
|---------|----|----|-----|
| Standard SCF/NSCF/bands | Yes | Yes | Yes |
| Meta-GGA functionals | Yes | No | No |
| Gamma-only phonon | Yes | No | Yes |
| Raman/3rd-order | Yes | No | No |
| CP (Car-Parrinello) | Yes | Yes | No |
| PAW reconstruction | No | No | Yes |
| Noncollinear magnetism | Yes | Yes | Yes |
| Spin-orbit coupling | Yes | Yes | Yes |

---

## 2. File Formats

### 2.1 UPF (Unified Pseudopotential Format)

The **native and recommended format** for QE. Current version: **UPF v2**.

All PP types (NC, US, PAW) are stored in UPF format. UPF files have the extension `.upf` and are XML-structured.

**Structure of a UPF file:**
```xml
<UPF version="2.0.1">
  <PP_INFO>
    ... (generation info, references)
  </PP_INFO>
  <PP_HEADER
    generated="..."
    author="..."
    date="..."
    comment="..."
    element="Si"
    pseudo_type="NC"
    relativistic="scalar"
    is_ultrasoft="False"
    is_paw="False"
    is_coulomb="False"
    paw_as_gipaw="False"
    core_correction="True"
    functional="PBE"
    z_valence="4.00"
    total_psenergy="..."
    wfc_cutoff="..."
    rho_cutoff="..."
    l_max="2"
    l_max_rho="..."
    l_local="-1"
    mesh_size="..."
    number_of_wfc="3"
    number_of_proj="3"
  />
  <PP_MESH>
    <PP_R type="real" size="..." columns="4">
      ... (radial grid)
    </PP_R>
    <PP_RAB type="real" size="..." columns="4">
      ... (radial grid derivative)
    </PP_RAB>
  </PP_MESH>
  <PP_LOCAL type="real" size="..." columns="4">
    ... (local potential)
  </PP_LOCAL>
  <PP_NONLOCAL>
    <PP_BETA ... >
      ... (nonlocal projectors)
    </PP_BETA>
    <PP_DIJ ... >
      ... (D_ij coefficients)
    </PP_DIJ>
  </PP_NONLOCAL>
  <PP_PSWFC>
    <PP_CHI ... >
      ... (pseudo wavefunctions)
    </PP_CHI>
  </PP_PSWFC>
  <PP_RHOATOM type="real" size="..." columns="4">
    ... (atomic charge density)
  </PP_RHOATOM>
</UPF>
```

### 2.2 Legacy Formats

QE still accepts several older formats:

| Format | Extension | Notes |
|--------|-----------|-------|
| NC pseudopotential | `.psp`, `.psp8` | ABINIT NC format |
| US pseudopotential | `.vdb` | Vanderbilt US format |
| PAW dataset | `.paw` | PAW format |
| RRKJ format | `.rrkj` | Rappe-Rabe-Kaxiras-Joannopoulos |
| HGH | `.hgh` | Hartwigsen-Goedecker-Hutter |
| FHI | `.fhi` | FHI (Fritz-Haber-Institut) |

Conversion utilities are available in the `upftools/` directory of the QE distribution.

### 2.3 Format Conversion Tools

Located in `upftools/` of the QE source:

| Tool | Purpose |
|------|---------|
| `upf2upf2.x` | Convert UPF v1 to UPF v2 |
| `vdw_kernel_table.x` | Generate van der Waals kernel table |
| Various scripts | Convert from other formats to UPF |

---

## 3. PP Libraries and Sources

### 3.1 SSSP (Standard Solid State Pseudopotentials)

**Recommended default choice.**

- URL: https://www.materialscloud.org/discover/sssp/table/efficiency
- Curated by THEOS (EPFL) and MARVEL
- Available in two versions:
  - **SSSP Efficiency** — Optimized for speed
  - **SSSP Precision** — Optimized for accuracy
- All elements, verified against all-electron calculations
- Available in PBE and PBEsol flavors
- PAW and NC variants

### 3.2 PSlibrary

- URL: https://github.com/dalcorso/pslibrary
- Author: Paolo Dal Corso
- Ultrasoft and PAW pseudopotentials
- Scalar-relativistic and fully-relativistic versions
- PBE, PBEsol, and other functionals
- Naming convention: `{element}.{functional}-{type}-{author}_psl.{version}.UPF`

### 3.3 GBRV (Garrity-Bennett-Rabe-Vanderbilt)

- URL: https://www.physics.rutgers.edu/gbrv/
- Ultrasoft pseudopotentials
- Optimized for high-throughput DFT
- PBE functional
- Available for QE, ABINIT, JDFTx

### 3.4 SG15

- Norm-conserving and PAW pseudopotentials
- Optimized for high accuracy
- Multiple exchange-correlation functionals

### 3.5 PseudoDojo

- URL: http://www.pseudo-dojo.org/
- NC and PAW pseudopotentials
- Stringent accuracy verification
- ONCV (Optimized Norm-Conserving Vanderbilt) format

### 3.6 Official QE Tables

- URL: https://pseudopotentials.quantum-espresso.org/legacy_tables
- Legacy PP tables (some kept for reference)
- Named by element and generation method

---

## 4. Choosing and Using Pseudopotentials

### 4.1 Selection Criteria

1. **XC functional match**: PP must be generated with the same functional you plan to use (e.g., PBE PP for PBE calculation)
2. **PP type compatibility**: Ensure the PP type (NC/US/PAW) is compatible with your calculation type
3. **Valence configuration**: Check that the PP includes all relevant valence electrons (e.g., semicore states for transition metals)
4. **Energy cutoff**: Different PPs require different cutoffs; check documentation
5. **Testing**: Always test PPs on simple systems before production calculations

### 4.2 File Naming Conventions

Common patterns in PP filenames:

```
Si.pbe-n-rrkjus_psl.1.0.0.UPF
│  │   │  │      │   └── version
│  │   │  │      └── PSlibrary identifier
│  │   │  └── PP method (rrkjus = RRKJ ultrasoft)
│  │   └── type (n = norm-conserving, us = ultrasoft)
│  └── XC functional (pbe)
└── Element
```

```
Si_ONCV_PBE-1.2.upf
│  │    │   └── version
│  │    └── XC functional
│  └── Method (ONCV)
└── Element
```

### 4.3 pseudo_dir Configuration

Specify where QE looks for PP files:

1. In input file: `pseudo_dir = '/path/to/pseudopotentials/'`
2. Environment variable: `export ESPRESSO_PSEUDO=/path/to/pseudopotentials/`
3. Default: current directory

### 4.4 ATOMIC_SPECIES Card

Reference the PP file in the input:
```
ATOMIC_SPECIES
Si  28.0855  Si.pbe-n-rrkjus_psl.1.0.0.UPF
```

The mass is in atomic mass units (amu). The PP file must be in `pseudo_dir`.

---

## 5. Generating Custom Pseudopotentials

If no suitable PP is available, use **ld1.x** (included in QE distribution):

### ld1.x Input Structure
```
&INPUT
  zed = 14.0,          ! atomic number
  relativistic = 1,    ! 0=nonrel, 1=scalar, 2=full
  config = '[Ne] 3s2 3p2',
  dft = 'PBE',
  iswitch = 3,         ! generation mode
  ...
/
```

This is an advanced topic requiring expertise in atomic structure calculations.

---

## 6. Validation and Testing

### 6.1 Essential Checks

- **Ghost states**: Verify no ghost states in the PP (check PP documentation)
- **Cutoff convergence**: Converge total energy with respect to ecutwfc
- **Comparison**: Compare lattice constants, bulk modulus, band gaps against known values
- **Transferability**: Test on different chemical environments

### 6.2 Delta Factor

The "delta factor" measures the PP accuracy against all-electron reference calculations. Lower delta = better agreement. Available in the SSSP and PseudoDojo databases.

---

## 7. Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `error #1: file not found` | PP file not in pseudo_dir | Check path and filename |
| `incorrect PP type` | Using US PP with incompatible feature | Switch to NC PP |
| `Ghost states detected` | Poor PP generation | Use a different PP library |
| `SCF not converging` | Incompatible PP or too hard PP | Try softer PP or increase ecutwfc |
| `Wrong results` | XC mismatch | Ensure PP functional matches calculation |
| `PAW not supported` | Using PAW with CP | Switch to NC/US for CP |

---

## 8. Quick Reference

### Recommended PP Libraries by Use Case

| Use Case | Recommended Library | PP Type |
|----------|-------------------|---------|
| General DFT (PBE) | SSSP Efficiency | PAW/US |
| High accuracy | SSSP Precision | PAW/NC |
| Phonons (DFPT) | SSSP or PSlibrary | NC or PAW |
| Meta-GGA | PseudoDojo or SG15 | NC |
| Raman | PSlibrary | NC |
| High throughput | GBRV | US |
| Car-Parrinello MD | PSlibrary | NC or US |

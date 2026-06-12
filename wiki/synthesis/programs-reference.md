# QE Programs Reference / QE 程序参考

## Source / 来源
- `raw/assets/qe-programs-reference.md` - Complete programs reference

## Program Categories / 程序类别

### Core DFT / 核心 DFT
| Program | Purpose / 用途 | Input Namelists |
|---------|---------------|----------------|
| `pw.x` | Plane-wave SCF/NSCF/bands/relax/MD | &CONTROL, &SYSTEM, &ELECTRONS, [&IONS], [&CELL] |
| `cp.x` | Car-Parrinello MD (Hartree units) | &CONTROL, &SYSTEM, &ELECTRONS, &IONS, [&CELL] |

### Phonons / 声子
| Program | Purpose / 用途 |
|---------|---------------|
| `ph.x` | Phonons via DFPT |
| `q2r.x` | Dynamical matrices → force constants |
| `matdyn.x` | Interpolated phonon dispersion |
| `dynmat.x` | Dynamical matrix post-processing |

### Post-Processing / 后处理
| Program | Purpose / 用途 | Input Namelist |
|---------|---------------|---------------|
| `pp.x` | Extract charge/potential data | &INPUTPP, &PLOT |
| `dos.x` | Total density of states | &DOS |
| `bands.x` | Band structure extraction | &BANDS |
| `projwfc.x` | Projected DOS | &PROJWFC |
| `molecularpdos.x` | Molecular PDOS | — |
| `ppp.x` | Polarization (Berry phase) | — |
| `pw2wannier90.x` | Wannier90 interface | — |

### Other / 其他
| Program | Purpose / 用途 |
|---------|---------------|
| `neb.x` | Nudged elastic band |
| `turbo_lanczos.x` | TDDFT (Lanczos) |
| `turbo_davidson.x` | TDDFT (Davidson) |
| `xspectra.x` | X-ray absorption |
| `ld1.x` | Pseudopotential generation |
| `hp.x` | Hubbard U parameters |
| `kcw.x` | Koopmans-compliant functionals |

## Common Conventions / 通用约定

### prefix and outdir
All programs that depend on pw.x output must use the same `prefix` and `outdir`:
- `prefix` — Prepended to all data filenames (default: 'pwscf')
- `outdir` — Directory containing data files (default: './')

所有依赖 pw.x 输出的程序必须使用相同的 `prefix` 和 `outdir`。

### Units / 单位
- pw.x: Rydberg atomic units (energy: Ry, length: Bohr)
- cp.x: Hartree atomic units (energy: Ha, length: Bohr)
- Post-processing output: Typically eV for energies

## Workflow Diagrams / 工作流图

### Standard DFT Workflow
```
pw.x (scf) ──→ pw.x (nscf) ──→ dos.x
     │              │
     │              └──→ projwfc.x
     │
     ├──→ pw.x (bands) ──→ bands.x
     │
     ├──→ pw.x (relax)
     │
     ├──→ pw.x (vc-relax)
     │
     └──→ ph.x ──→ q2r.x ──→ matdyn.x
```

## Related Pages / 相关页面

- [ph.x Phonon](../entities/ph-x-phonon.md)
- [Post-Processing Programs](../entities/post-processing-programs.md)
- [Band Structure and DOS Workflow](../concepts/band-structure-dos-workflow.md)
- [Phonon Calculation Workflow](../concepts/phonon-calculation.md)

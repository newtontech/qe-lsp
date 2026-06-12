# QE Examples Reference / QE 示例参考

## Source / 来源
- `raw/assets/qe-examples.md` - Complete example input files
- `raw/assets/silicon_scf.in` - Silicon SCF fixture
- `raw/assets/silicon_bands.in` - Silicon bands fixture
- `raw/assets/aluminum_relax.in` - Aluminum relax fixture
- `raw/assets/sio2_vc_relax.in` - SiO2 vc-relax fixture
- `raw/assets/fe_spin.in` - Iron spin-polarized fixture

## Example Input Files / 示例输入文件

The project contains reference input files for all major calculation types:

项目包含所有主要计算类型的参考输入文件：

| File | Calculation | System |
|------|-----------|--------|
| `silicon_scf.in` | SCF | Si (diamond, ibrav=2) |
| `silicon_bands.in` | Bands | Si (diamond) |
| `aluminum_relax.in` | Relax | Al (FCC) |
| `sio2_vc_relax.in` | vc-relax | SiO2 (ibrav=0) |
| `fe_spin.in` | SCF (spin) | Fe (BCC, nspin=2) |

## Calculation Type Summary / 计算类型总结

### SCF (Self-Consistent Field)
- Namelists: &CONTROL, &SYSTEM, &ELECTRONS
- Purpose: Ground-state charge density and total energy
- Key parameters: ecutwfc, ecutrho, conv_thr, mixing_beta

### NSCF (Non-Self-Consistent Field)
- Namelists: &CONTROL, &SYSTEM, &ELECTRONS
- Purpose: Eigenvalues on dense k-grid (for DOS)
- Key: `calculation = 'nscf'`, `occupations = 'tetrahedra'`

### Bands (Band Structure)
- Namelists: &CONTROL, &SYSTEM, &ELECTRONS
- Purpose: Eigenvalues along high-symmetry k-path
- Key: `calculation = 'bands'`, k-path in K_POINTS

### Relax (Structural Optimization)
- Namelists: &CONTROL, &SYSTEM, &ELECTRONS, &IONS
- Purpose: Optimize atomic positions (fixed cell)
- Key: `ion_dynamics = 'bfgs'`, forc_conv_thr

### vc-relax (Variable-Cell Relaxation)
- Namelists: &CONTROL, &SYSTEM, &ELECTRONS, &IONS, &CELL
- Purpose: Optimize positions and cell
- Key: `cell_dynamics = 'bfgs'`, press, cell_dofree

### MD (Molecular Dynamics)
- Namelists: &CONTROL, &SYSTEM, &ELECTRONS, &IONS
- Purpose: Born-Oppenheimer MD
- Key: `ion_dynamics = 'verlet'`, dt, ion_temperature

### Phonon (via ph.x)
- Separate program: ph.x
- Purpose: Phonon frequencies via DFPT
- Key: ldisp, nq1/nq2/nq3, fildyn

### Spin-Polarized
- Same as SCF but with `nspin = 2`
- Key: `starting_magnetization(i)`, smaller mixing_beta

## Key Parameter Defaults / 关键参数默认值

| Parameter | Insulator | Metal |
|-----------|-----------|-------|
| ecutwfc | 30-60 Ry | 30-60 Ry |
| ecutrho | 4x (NC), 8-12x (US/PAW) | same |
| mixing_beta | 0.5-0.7 | 0.1-0.3 |
| conv_thr | 1e-6 to 1e-8 | 1e-6 to 1e-8 |
| K-grid | 4-8 | 8-16 |
| smearing | N/A | Gaussian or MV, 0.01-0.03 Ry |

## Related Pages / 相关页面

- [Input File Format](input-file-format.md)
- [Quick Reference](quick-reference.md)
- [Programs Reference](programs-reference.md)

# ph.x Phonon Input / ph.x 声子输入

## Source / 来源
- `raw/assets/qe-programs-reference.md` - Program reference documentation
- `raw/assets/qe-examples.md` - Example input files

## Definition / 定义

`ph.x` computes phonon frequencies and eigenvectors using Density Functional Perturbation Theory (DFPT). It reads the ground-state data produced by a prior `pw.x` SCF calculation.

`ph.x` 使用密度泛函微扰理论 (DFPT) 计算声子频率和本征矢量。它读取先前 `pw.x` SCF 计算产生的基态数据。

## Input Structure / 输入结构

```
title_line
&INPUTPH
  prefix = '...',
  outdir = '...',
  ...
/
[xq(1) xq(2) xq(3)]   ! single q-point (if ldisp != .true.)
```

## Key Parameters / 关键参数

| Parameter | Type | Default | Description / 描述 |
|-----------|------|---------|-------------------|
| `prefix` | CHARACTER | 'pwscf' | Must match pw.x prefix |
| `outdir` | CHARACTER | './' | Must match pw.x outdir |
| `tr2_ph` | REAL | 1e-12 | Self-consistency threshold |
| `fildyn` | CHARACTER | 'matdyn' | Output dynamical matrix file |
| `ldisp` | LOGICAL | .false. | Grid of q-points for dispersion |
| `nq1,nq2,nq3` | INTEGER | 0,0,0 | q-point grid dimensions |
| `epsil` | LOGICAL | .false. | Compute dielectric constant |
| `trans` | LOGICAL | .true. | Compute phonons |
| `lraman` | LOGICAL | .false. | Compute Raman coefficients |
| `electron_phonon` | CHARACTER | ' ' | Electron-phonon coupling mode |

## Output Files / 输出文件

| File | Location | Description |
|------|----------|-------------|
| Dynamical matrices | `outdir/_ph0/prefix.phsave/dynmat.#iq.#irr.xml` | Per q-point and irrep |
| Displacement patterns | `outdir/_ph0/prefix.phsave/patterns.#iq.xml` | Atomic displacement patterns |

## Phonon Workflow / 声子工作流

```
1. pw.x (scf)    → ground state charge density
2. ph.x          → dynamical matrices on q-grid
3. q2r.x         → real-space force constants
4. matdyn.x      → phonon dispersion / DOS
```

## Related Entities / 相关实体

- [Calculation Type](calculation-type.md)
- [Pseudopotential](pseudopotential.md)
- [K-points](k-points.md)

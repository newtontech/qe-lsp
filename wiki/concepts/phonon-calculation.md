# Phonon Calculation Workflow / 声子计算工作流

## Source / 来源
- `raw/assets/qe-programs-reference.md` - Program reference
- `raw/assets/qe-examples.md` - Example phonon input

## Overview / 概述

Phonon calculations in Quantum ESPRESSO use Density Functional Perturbation Theory (DFPT) via `ph.x` to compute vibrational properties: phonon frequencies, eigenvectors, dielectric constants, and electron-phonon coupling.

Quantum ESPRESSO 中的声子计算使用 `ph.x` 通过密度泛函微扰理论 (DFPT) 计算振动性质：声子频率、本征矢量、介电常数和电子-声子耦合。

## Workflow Steps / 工作流步骤

### Step 1: SCF Ground State / 自洽基态
```
pw.x < pw.scf.in > pw.scf.out
```
Requirements:
- `tstress = .true.` and `tprnfor = .true.` in &CONTROL
- Converged SCF with tight threshold

### Step 2: Phonon Calculation / 声子计算
```
ph.x < ph.in > ph.out
```

Two modes:
- **Single q-point**: Specify `xq(1) xq(2) xq(3)` after namelist
- **Grid (dispersion)**: Set `ldisp = .true.` with `nq1 nq2 nq3`

### Step 3: Force Constants / 力常数
```
q2r.x < q2r.in > q2r.out
```
Converts dynamical matrices to real-space force constants.

### Step 4: Interpolation / 插值
```
matdyn.x < matdyn.in > matdyn.out
```
Interpolates phonon frequencies along arbitrary q-paths.

## Key ph.x Parameters / 关键 ph.x 参数

| Parameter | Description / 描述 |
|-----------|-------------------|
| `ldisp` | Grid of q-points for full dispersion |
| `nq1,nq2,nq3` | Monkhorst-Pack grid for q-points |
| `epsil` | Compute dielectric constant at q=0 |
| `trans` | Compute phonon modes |
| `lraman` | Compute Raman coefficients |
| `fildyn` | Dynamical matrix output file |
| `electron_phonon` | Electron-phonon coupling calculation |

## Acoustic Sum Rule / 声学求和规则

Applied via `asr` parameter in q2r.x and matdyn.x:
- `'crystal'` — Crystal acoustic sum rule
- `'simple'` — Simple sum rule
- `'one-dim'` — For 1D systems
- `'zero-dim'` — For molecules

## Related Concepts / 相关概念

- [SCF Convergence](scf-convergence.md)
- [ph.x Phonon](../entities/ph-x-phonon.md)
- [Post-Processing Programs](../entities/post-processing-programs.md)

# Band Structure and DOS Workflow / 能带结构和态密度工作流

## Source / 来源
- `raw/assets/qe-examples.md` - Example input files
- `raw/assets/qe-programs-reference.md` - Program reference

## Overview / 概述

Band structure and density of states (DOS) calculations are among the most common post-SCF analyses. Both require a converged SCF ground state as a starting point.

能带结构和态密度 (DOS) 计算是最常见的 SCF 后分析之一。两者都需要收敛的 SCF 基态作为起点。

## Band Structure Workflow / 能带结构工作流

### Step 1: SCF / 自洽计算
Standard SCF with appropriate k-grid and convergence.

### Step 2: Bands Calculation / 能带计算
```
pw.x < pw.bands.in > pw.bands.out
```
- Set `calculation = 'bands'`
- Define k-path in K_POINTS card with `{crystal}` coordinates
- Weight column = number of interpolation points between consecutive k-points

### Step 3: Extract with bands.x / 使用 bands.x 提取
```
bands.x < bands.in > bands.out
```

## Common High-Symmetry Points / 常见高对称点

| Structure | Points |
|-----------|--------|
| FCC | Gamma (0,0,0), X (0.5,0,0.5), L (0.5,0.5,0.5), W (0.5,0.25,0.75) |
| BCC | Gamma, H, N, P |
| HCP | Gamma, M, K, A, L |
| Simple cubic | Gamma, X, R, M |

## DOS Workflow / 态密度工作流

### Step 1: SCF / 自洽计算
Standard SCF calculation.

### Step 2: NSCF on Dense Grid / 稠密网格上的非自洽计算
```
pw.x < pw.nscf.in > pw.nscf.out
```
- Set `calculation = 'nscf'`
- Use `occupations = 'tetrahedra'` (more accurate integration)
- Dense k-grid (12x12x12 or higher)
- Set `nosym = .true.` to prevent extra k-point generation
- Specify `nbnd` to include unoccupied bands

### Step 3: Total DOS / 总态密度
```
dos.x < dos.in > dos.out
```

### Step 4 (optional): Projected DOS / 投影态密度
```
projwfc.x < projwfc.in > projwfc.out
```

## projwfc.x Broadening Options / projwfc.x 展宽选项

| ngauss | Method / 方法 |
|--------|-------------|
| 0 | Simple Gaussian (default) |
| 1 | Methfessel-Paxton order 1 |
| -1 | Marzari-Vanderbilt "cold smearing" |
| -99 | Fermi-Dirac function |

## Important Rules / 重要规则

1. **Same prefix and outdir**: NSCF/bands must use the same `prefix` and `outdir` as SCF
   NSCF/bands 必须使用与 SCF 相同的 prefix 和 outdir
2. **Denser k-grid**: NSCF requires a denser k-grid than SCF
   NSCF 需要比 SCF 更密的 k 网格
3. **Tetrahedron method**: Use `occupations = 'tetrahedra'` for DOS (not smearing)
   对于 DOS 使用 `occupations = 'tetrahedra'`（不是展宽）
4. **Sufficient bands**: Set `nbnd` high enough for unoccupied states
   设置足够高的 `nbnd` 以包含非占据态

## Related Concepts / 相关概念

- [SCF Convergence](scf-convergence.md)
- [K-points](../entities/k-points.md)
- [Post-Processing Programs](../entities/post-processing-programs.md)

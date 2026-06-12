# Post-Processing Programs / 后处理程序

## Source / 来源
- `raw/assets/qe-programs-reference.md` - Program reference documentation
- `raw/assets/qe-examples.md` - Example input files

## Definition / 定义

Quantum ESPRESSO provides several post-processing tools that extract and visualize data from pw.x and cp.x output. These programs share common conventions for `prefix` and `outdir`.

Quantum ESPRESSO 提供了多个后处理工具，用于从 pw.x 和 cp.x 输出中提取和可视化数据。这些程序共享 `prefix` 和 `outdir` 的通用约定。

## Programs / 程序列表

### pp.x — General Post-Processing

Extracts charge densities, potentials, and other quantities from pw.x output.

从 pw.x 输出中提取电荷密度、势和其他量。

**Key parameters** (&INPUTPP):
| Parameter | Description |
|-----------|-------------|
| `plot_num` | Quantity to extract (0-25) |
| `filplot` | Output file for extracted data |

**Common plot_num values**:
- 0: Charge density
- 1: Total potential
- 5: STM images
- 7: |psi|^2 for selected states
- 17: All-electron charge (PAW)

### dos.x — Density of States

Computes total DOS from NSCF eigenvalues.

从 NSCF 本征值计算总态密度。

**Input format**:
```
&DOS
  prefix = '...', outdir = '...', fildos = 'dos.dat'
  Emin = ..., Emax = ..., DeltaE = ...
/
```

### bands.x — Band Structure Post-Processing

Extracts band eigenvalues from a bands calculation for plotting.

从能带计算中提取本征值用于绘图。

**Input format**:
```
&BANDS
  prefix = '...', outdir = '...', filband = 'bands.dat'
/
```

### projwfc.x — Projected DOS

Projects wavefunctions onto atomic orbitals and computes projected DOS.

将波函数投影到原子轨道并计算投影态密度。

**Key parameters** (&PROJWFC):
| Parameter | Description |
|-----------|-------------|
| `ngauss` | Broadening type (0=Gaussian, 1=MP, -1=MV, -99=FD) |
| `degauss` | Broadening width (Ry) |
| `filpdos` | Output file prefix |

**Output files**:
- `{filpdos}.pdos_tot` — Total projected DOS
- `{filpdos}.pdos_atm#N(X)_wfc#M(l)` — Per-atom, per-orbital PDOS

### matdyn.x — Phonon Dispersion

Interpolates phonon frequencies from force constants.

从力常数插值声子频率。

### q2r.x — Force Constants

Transforms dynamical matrices to real-space force constants.

将动力学矩阵转换为实空间力常数。

## Common Workflow Patterns / 常见工作流模式

### DOS / 态密度
```
pw.x (scf) → pw.x (nscf) → dos.x
                             projwfc.x
```

### Band Structure / 能带结构
```
pw.x (scf) → pw.x (bands) → bands.x
```

### Phonon Dispersion / 声子色散
```
pw.x (scf) → ph.x → q2r.x → matdyn.x
```

### Charge Density Plot / 电荷密度绘图
```
pw.x (scf) → pp.x
```

## Related Entities / 相关实体

- [Calculation Type](calculation-type.md)
- [Pseudopotential](pseudopotential.md)
- [ph.x Phonon](ph-x-phonon.md)

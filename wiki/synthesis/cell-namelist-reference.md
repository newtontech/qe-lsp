# CELL Namelist Reference / CELL 名称列表参考

## Source Sources / 来源
- `raw/assets/constants.py` - `QE_PARAM_DOCS["&CELL"]`

## Purpose / 目的

Controls variable-cell relaxation and cell dynamics for optimizing crystal structure under pressure or finding equilibrium lattice parameters.

控制变晶胞弛豫和晶胞动力学，用于在压力下优化晶体结构或寻找平衡晶格参数。

## When Required / 何时需要

Required for calculation types:
- `vc-relax` - Variable-cell relaxation
- `vc-md` - Variable-cell molecular dynamics

Not required for:
- `scf`, `nscf`, `bands`, `relax`, `md`, `ph`

## Parameters / 参数

### Cell Dynamics / 晶胞动力学

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `cell_dynamics` | string | Cell dynamics algorithm | 晶胞动力学算法 |
| `press` | real | Target external pressure (kbar) | 目标外压力 |
| `press_conv_thr` | real | Pressure convergence threshold (kbar) | 压力收敛阈值 |
| `cell_dofree` | string | Degrees of freedom for relaxation | 弛豫自由度 |

### Variable-Cell MD / 变晶胞 MD

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `cell_factor` | real | Supercell factor for stress calculation | 应力计算的超胞因子 |
| `wmass` | real | Fictitious cell mass | 虚构晶胞质量 |

## Parameter Details / 参数详情

### cell_dynamics / 晶胞动力学算法

Values: `'none'`, `'sd'`, `'damp-pr'`, `'damp-w'`, `'bfgs'`, `'pr'`

- `'bfgs'`: BFGS quasi-Newton method (recommended)
- `'pr'`: Presnel-conjugate gradient
- `'sd'`: Steepest descent
- `'damp-pr'`: Damped PR
- `'damp-w'`: Damped with wavefunction extrapolation
- `'none'`: No cell optimization

**Default**: `'bfgs'` for `vc-relax`

### press / 目标压力

Target external pressure in kilobar.

千巴单位的目标外压力。

**Typical values**:
- `0.0`: Ambient pressure (default)
- `10.0`: High pressure
- `-1.0`: Negative pressure (tension)

### press_conv_thr / 压力收敛阈值

Convergence threshold on pressure (kbar).

压力收敛阈值 (kbar)。

Default: `0.5` kbar

Tighten for more precise pressure convergence.

### cell_dofree / 弛豫自由度

Specifies which cell parameters can change during relaxation.

指定弛豫期间哪些晶胞参数可以变化。

Values:
- `'all'`: All cell parameters (default)
- `'x'`, `'y'`, `'z'`: Only specified axis length
- `'xy'`, `'xz'`, `'yz'`: Only specified plane
- `'xyz'`: Only cell shape (fixed volume)
- `'shape'`: Cell angles only
- `'volume'`: Volume only
- `'2Dxy'`: 2D system (xy plane free)
- `'2Dshape'`: 2D shape relaxation

### cell_factor / 超胞因子

Factor used to build supercell for stress calculation.

用于构建应力计算超胞的因子。

Higher values give more accurate stress but cost more.

Default: Depends on system size

### wmass / 虚构晶胞质量

Fictitious cell mass for variable-cell dynamics (in atomic units).

变晶胞动力学的虚构晶胞质量（原子单位）。

Only relevant for `vc-md` calculations.

Default: Automatically calculated

## Examples / 示例

### Standard VC-Relax / 标准变晶胞弛豫

```
&CELL
  cell_dynamics = 'bfgs'
  press = 0.0
  cell_dofree = 'all'
/
```

### Fixed Volume / 固定体积

```
&CELL
  cell_dynamics = 'bfgs'
  press = 0.0
  cell_dofree = 'shape'    ! Volume fixed, shape can change
/
```

### 2D System / 二维系统

```
&CELL
  cell_dynamics = 'bfgs'
  press = 0.0
  cell_dofree = '2Dxy'     ! Free xy plane, fixed z
/
```

### Under Pressure / 加压

```
&CELL
  cell_dynamics = 'bfgs'
  press = 10.0             ! 10 kbar pressure
  press_conv_thr = 0.1
/
```

### VC-MD / 变晶胞分子动力学

```
&CELL
  cell_dynamics = 'damp-w'
  press = 0.0
  wmass = 20.0
/
```

## Related Entities / 相关实体

- [Calculation Type](calculation-type.md)
- [IONS Namelist](ions-namelist-reference.md)
- [CELL_PARAMETERS Card](cell-parameters-card.md)
- [ibrav Parameter](ibrav-parameter.md)

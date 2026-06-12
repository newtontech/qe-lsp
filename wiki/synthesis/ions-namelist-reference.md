# IONS Namelist Reference / IONS 名称列表参考

## Source Sources / 来源
- `raw/assets/constants.py` - `QE_PARAM_DOCS["&IONS"]`

## Purpose / 目的

Controls ionic relaxation and molecular dynamics for geometry optimization and ionic motion.

控制几何优化和离子运动的离子弛豫和分子动力学。

## When Required / 何时需要

Required for calculation types:
- `relax` - Ionic relaxation only
- `md` - Molecular dynamics
- `vc-relax` - Variable-cell relaxation
- `vc-md` - Variable-cell MD

Not required for:
- `scf`, `nscf`, `bands`, `ph`

## Parameters / 参数

### Ion Dynamics / 离子动力学

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `ion_dynamics` | string | Ion dynamics algorithm | 离子动力学算法 |
| `ion_positions` | string | Position source | 位置来源 |

### Extrapolation / 外推

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `pot_extrapolation` | string | Potential extrapolation | 势外推 |
| `wfc_extrapolation` | string | Wavefunction extrapolation | 波函数外推 |

### BFGS Settings / BFGS 设置

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `bfgs_ndim` | integer | BFGS history length | BFGS 历史长度 |
| `trust_radius_max` | real | Maximum trust radius (Bohr) | 最大信任半径 |
| `trust_radius_min` | real | Minimum trust radius (Bohr) | 最小信任半径 |
| `trust_radius_ini` | real | Initial trust radius (Bohr) | 初始信任半径 |

### Advanced / 高级

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `remove_rigid_rot` | logical | Remove rigid rotation | 移除刚体旋转 |

## Parameter Details / 参数详情

### ion_dynamics / 离子动力学算法

Values: `'none'`, `'bfgs'`, `'damp'`, `'verlet'`, `'langevin'`, `'beeman'`

- `'bfgs'`: BFGS quasi-Newton method (recommended for relaxation)
- `'damp'`: Damped molecular dynamics
- `'verlet'`: Verlet algorithm (for MD)
- `'langevin'`: Langevin dynamics (thermostat)
- `'beeman'`: Beeman algorithm (for MD)
- `'none'`: No ion movement

**Default**:
- `'bfgs'` for `relax`
- `'verlet'` for `md`

### ion_positions / 离子位置

Values: `'default'`, `'from_input'`

- `'default'`: Read from restart file if available
- `'from_input'`: Always read from input file

### pot_extrapolation / 势外推

Potential extrapolation scheme between ionic steps.

离子步之间的势外推方案。

Common values: `'atomic'`, `'order_1'`, `'order_2'`, `'order_3'`

### wfc_extrapolation / 波函数外推

Wavefunction extrapolation scheme between ionic steps.

离子步之间的波函数外推方案。

Common values: `'none'`, `'atomic'`, `'order_1'`, `'order_2'`, `'order_3'`

### BFGS Trust Radius / BFGS 信任半径

Controls step size in BFGS optimization.

控制 BFGS 优化中的步长。

- `trust_radius_max`: Maximum step size (default: 0.5 Bohr)
- `trust_radius_min`: Minimum step size (default: 0.01 Bohr)
- `trust_radius_ini`: Initial step size (default: 0.2 Bohr)

### bfgs_ndim / BFGS 历史维度

Number of old forces used in BFGS Hessian approximation.

BFGS Hessian 近似中使用的旧力数量。

Default: 1

Higher values use more memory but may converge faster.

## Examples / 示例

### Standard Relaxation / 标准弛豫

```
&IONS
  ion_dynamics = 'bfgs'
/
```

### Damped Dynamics / 阻尼动力学

```
&IONS
  ion_dynamics = 'damp'
  pot_extrapolation = 'order_2'
  wfc_extrapolation = 'order_1'
/
```

### Custom BFGS / 自定义 BFGS

```
&IONS
  ion_dynamics = 'bfgs'
  bfgs_ndim = 3
  trust_radius_max = 1.0
  trust_radius_min = 0.05
/
```

### From Input Positions / 从输入位置

```
&IONS
  ion_dynamics = 'bfgs'
  ion_positions = 'from_input'
/
```

## Related Entities / 相关实体

- [Calculation Type](calculation-type.md)
- [CELL Namelist](cell-namelist-reference.md)
- [ATOMIC_POSITIONS Card](atomic-positions-card.md)

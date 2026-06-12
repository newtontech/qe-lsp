# ELECTRONS Namelist Reference / ELECTRONS 名称列表参考

## Source Sources / 来源
- `raw/assets/constants.py` - `QE_PARAM_DOCS["&ELECTRONS"]`

## Purpose / 目的

Controls electronic structure calculation: convergence thresholds, mixing parameters, and diagonalization methods.

控制电子结构计算：收敛阈值、混合参数和对角化方法。

## Parameters / 参数

### Convergence / 收敛

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `conv_thr` | real | SCF convergence threshold (Ry) | SCF 收敛阈值 |
| `electron_maxstep` | integer | Maximum SCF iterations | 最大 SCF 迭代次数 |

### Mixing / 混合

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `mixing_beta` | real | Charge density mixing factor | 电荷密度混合因子 |
| `mixing_mode` | string | Mixing scheme | 混合方案 |

### Diagonalization / 对角化

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `diagonalization` | string | Diagonalization method | 对角化方法 |
| `diago_cg_maxiter` | integer | Max CG iterations | 最大 CG 迭代次数 |
| `diago_david_ndim` | integer | Davidson iterations | Davidson 迭代次数 |

### Starting Point / 起始点

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `startingwfc` | string | Starting wavefunctions | 起始波函数 |
| `startingpot` | string | Starting potential | 起始势 |

### Advanced / 高级

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `scf_must_converge` | logical | Abort if not converged | 若不收敛则中止 |
| `tqr` | logical | Tail-assisted quick recircularization | 尾辅助快速再循环 |

## Parameter Details / 参数详情

### conv_thr / 收敛阈值

Convergence threshold for self-consistency.

自洽收敛阈值。

**Typical values**:
- `1.0d-8`: Strict convergence
- `1.0d-6`: Standard convergence
- `1.0d-4`: Quick test

Default: `1.0d-6`

### mixing_beta / 混合因子

Charge density mixing factor. Valid range: 0 < β ≤ 1.

电荷密度混合因子。有效范围：0 < β ≤ 1。

**Validation**: Warning when > 0.7 (may cause convergence issues)

**Recommended**:
- `0.7`: Default for most systems
- `0.3-0.5`: For metals or difficult convergence
- `0.1-0.3`: For very difficult cases

### mixing_mode / 混合方案

Values: `'plain'`, `'TF'`, `'local-TF'`

- `'plain'`: Plain Broyden mixing (default)
- `'TF'`: Thomas-Fermi mixing (recommended for metals)
- `'local-TF'`: Local Thomas-Fermi mixing

### diagonalization / 对角化方法

Values: `'david'`, `'cg'`, `'ppcg'`, `'paro'`, `'rmm-davidson'`

- `'david'`: Davidson method (default, good for large systems)
- `'cg'`: Conjugate gradient
- `'ppcg'`: Preconditioned CG
- `'rmm-davidson'`: Residual minimization + Davidson

### electron_maxstep / 最大 SCF 步数

Maximum number of SCF iterations.

SCF 迭代的最大次数。

Default: 100

Increase for difficult convergence.

### startingwfc / 起始波函数

Values: `'random'`, `'atomic'`, `'atomic+random'`, `'file'`

- `'random'`: Random starting wavefunctions
- `'atomic'`: Superposition of atomic wavefunctions
- `'atomic+random'`: Atomic with small random component
- `'file'`: Read from previous calculation

### startingpot / 起始势

Values: `'atomic'`, `'file'`

- `'atomic'`: Superposition of atomic potentials
- `'file'`: Read from previous calculation

### scf_must_converge / 必须收敛

When `.true.`, calculation aborts if SCF doesn't converge.

设置为 `.true.` 时，若 SCF 不收敛则计算中止。

Default: `.true.`

## Examples / 示例

### Standard SCF / 标准 SCF

```
&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
  electron_maxstep = 100
/
```

### Metallic System / 金属系统

```
&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.3          ! Lower mixing
  mixing_mode = 'TF'         ! Thomas-Fermi
  electron_maxstep = 200
/
```

### From Previous Calculation / 从先前计算

```
&ELECTRONS
  conv_thr = 1.0d-8
  startingwfc = 'file'
  startingpot = 'file'
/
```

## Related Entities / 相关实体

- [SCF Convergence](scf-convergence.md)
- [mixing_beta Parameter](mixing-beta.md)
- [conv_thr Parameter](conv-thr.md)

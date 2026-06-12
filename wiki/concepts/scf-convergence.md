# SCF Convergence / 自洽场收敛

## Source Sources / 来源
- `raw/assets/constants.py` - ELECTRONS namelist parameters
- `raw/assets/validation.py` - convergence-related validation

## Definition / 定义

Self-consistent field (SCF) convergence is achieved when the electron density (or total energy) stops changing between iterations within a specified threshold.

自洽场 (SCF) 收敛是指当电子密度（或总能量）在迭代之间的变化停止在指定阈值内时达到的状态。

## Convergence Control Parameters / 收敛控制参数

Located in `&ELECTRONS` namelist:

| Parameter | Purpose | Chinese Description |
|-----------|---------|-------------------|
| `conv_thr` | Convergence threshold (Ry) | 收敛阈值 |
| `electron_maxstep` | Maximum SCF iterations | 最大 SCF 迭代次数 |
| `mixing_beta` | Charge density mixing factor | 电荷密度混合因子 |
| `mixing_mode` | Mixing scheme | 混合方案 |
| `scf_must_converge` | Abort if not converged | 若不收敛则中止 |

## conv_thr / 收敛阈值

The target convergence threshold for SCF cycle.

SCF 循环的目标收敛阈值。

**Typical values**:
- `1.0d-6` to `1.0d-8` for production calculations
- `1.0d-4` for quick tests

**Example**:
```
&ELECTRONS
  conv_thr = 1.0d-8    ! Strict convergence
/
```

## Convergence Strategies / 收敛策略

### For Insulators / 绝缘体

```
&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
  electron_maxstep = 100
/
```

### For Metals / 金属

```
&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.3          ! Lower mixing
  mixing_mode = 'TF'          ! Thomas-Fermi
  smearing = 'methfessel-paxton'
  degauss = 0.02
/
```

### For Large Systems / 大系统

```
&ELECTRONS
  conv_thr = 1.0d-6           ! Looser threshold
  mixing_beta = 0.5
  electron_maxstep = 200
/
```

## Troubleshooting Convergence / 收敛故障排除

### SCF Does Not Converge / SCF 不收敛

1. **Lower mixing_beta**: Reduce from 0.7 to 0.3-0.5
2. **Change mixing_mode**: Try `'TF'` or `'local-TF'`
3. **Increase electron_maxstep**: Allow more iterations
4. **Use smearing**: For metals, add smearing
5. **Check cutoffs**: Ensure ecutwfc is sufficient

### Oscillating Behavior / 振荡行为

**Symptoms**: Energy oscillates between values

**Solutions**:
- Reduce mixing_beta
- Change mixing_mode to 'TF'
- For metals, adjust smearing parameters

## scf_must_converge / 必须收敛

When `true`, the calculation aborts if SCF doesn't converge.

设置为 `true` 时，如果 SCF 不收敛则计算中止。

**Example**:
```
&ELECTRONS
  scf_must_converge = .true.
  electron_maxstep = 100
/
```

## Related Entities / 相关实体

- [ELECTRONS Namelist](electrons-namelist.md)
- [mixing_beta Parameter](mixing-beta.md)
- [conv_thr Parameter](conv-thr.md)
- [Smearing](smearing.md)

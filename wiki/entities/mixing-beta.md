# mixing_beta Parameter / 混合参数

## Source Sources / 来源
- `raw/assets/validation.py` - mixing_beta validation
- `raw/assets/constants.py` - ELECTRONS namelist documentation

## Definition / 定义

`mixing_beta` in the `&ELECTRONS` namelist controls the charge density mixing factor for self-consistent field convergence. It determines how much of the new density is mixed with the old density in each SCF iteration.

`&ELECTRONS` 名称列表中的 `mixing_beta` 控制自洽场收敛的电荷密度混合因子。它决定每次 SCF 迭代中新密度与旧密度的混合比例。

## Range / 范围

Valid range: `0 < mixing_beta ≤ 1`

Valid values typically: `0.1` to `0.9`

## Validation Rules / 验证规则

### High mixing_beta Warning / 高混合警告

**Severity**: Warning

**Message**: "mixing_beta above 0.7 may make large systems hard to converge."

When `mixing_beta > 0.7`, a warning is issued because too aggressive mixing can cause oscillations and convergence failures in large systems.

## Convergence Behavior / 收敛行为

| mixing_beta | Behavior | Chinese Description |
|-------------|----------|-------------------|
| Low (0.1-0.3) | Slow but stable | 慢但稳定 |
| Medium (0.3-0.7) | Balanced | 平衡 |
| High (0.7-0.9) | Fast but risky | 快但风险 |

## Example / 示例

```
&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7    ! Standard value
/
```

For difficult systems:
```
&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.3    ! Lower for stability
  mixing_mode = 'TF'   ! Use Thomas-Fermi mixing
/
```

## Related Parameters / 相关参数

| Parameter | Purpose | Chinese Description |
|-----------|---------|-------------------|
| `mixing_mode` | Mixing scheme | 混合方案 |
| `conv_thr` | SCF convergence threshold | SCF 收敛阈值 |
| `electron_maxstep` | Max SCF iterations | 最大 SCF 迭代次数 |

## mixing_mode Options / mixing_mode 选项

- `plain` - Plain Broyden mixing
- `TF` - Thomas-Fermi mixing (recommended for metals)
- `local-TF` - Local Thomas-Fermi mixing

## Best Practices / 最佳实践

1. **Start with 0.7**: Default value works for most systems
2. **Reduce for metals**: Use lower values (0.1-0.3) for metallic systems
3. **Adjust based on convergence**: Increase if SCF converges slowly, decrease if unstable
4. **Use with mixing_mode**: Combine with TF mixing for difficult cases

## Related Entities / 相关实体

- [ELECTRONS Namelist](electrons-namelist.md)
- [SCF Convergence](scf-convergence.md)
- [conv_thr Parameter](conv-thr.md)

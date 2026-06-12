# K-Points / K 点

## Source Sources / 来源
- `raw/assets/validation.py` - `_validate_k_points()` function
- `raw/assets/silicon_scf.in` - K_POINTS example

## Definition / 定义

K-points are sampling points in the Brillouin zone used to integrate electronic properties over reciprocal space.

K 点是布里渊区中的采样点，用于在倒空间积分电子性质。

## K_POINTS Card Format / K_POINTS 卡片格式

```
K_POINTS [option]
[data based on option]
```

## Options / 选项

| Option | Chinese Description | Data Format |
|--------|-------------------|------------|
| `automatic` | 自动网格 | `nk1 nk2 nk3 0 0 0` |
| `gamma` | Γ 点 | `1` (just gamma) or `nk1 nk2 nk3 0 0 0` |
| `crystal` | 晶体坐标 | List of k-points and weights |
| `tpiba` | 2π/a 单位 | List of k-points and weights |
| `automatic` | Monkhorst-Pack | `nk1 nk2 nk3 k1 k2 k3` |

## Automatic Grid / 自动网格

```
K_POINTS {automatic}
8 8 8 0 0 0
```

Format: `nk1 nk2 nk3 k1 k2 k3`
- `nk1, nk2, nk3`: Grid divisions
- `k1, k2, k3`: Shifts (usually 0 0 0)

### Coarse Grid Warning / 粗网格警告

**Severity**: Warning

**Message**: "K_POINTS automatic grid is very coarse for production calculations."

Triggered when any grid dimension < 3.

## Gamma-Only / 仅 Gamma 点

```
K_POINTS {gamma}
```

### Gamma Offset Warning / Gamma 偏移警告

**Severity**: Warning

**Message**: "K_POINTS {gamma} should not include a non-zero offset."

When using `{gamma}` option with non-zero shifts, a warning is issued because gamma-only calculations should not include offsets.

## Explicit K-Points / 显式 K 点

```
K_POINTS {crystal}
6
0.00 0.00 0.00 1.00
0.50 0.00 0.00 1.00
0.00 0.50 0.00 1.00
...
```

Format: Number of k-points, then rows of `kx ky kz weight`

## Validation Rules / 验证规则

1. **Coarse grid**: Warning for dimensions < 3 in automatic mode
2. **Gamma offset**: Warning for non-zero offsets with `{gamma}` option
3. **Missing card**: Error if K_POINTS is required for calculation type

## Best Practices / 最佳实践

1. **SCF**: Use automatic grid with reasonable density (e.g., 6×6×6 for bulk)
2. **NSCF/Bands**: Use specific path for band structure
3. **Convergence**: Test k-point convergence for production calculations
4. **Gamma**: Use for large supercells where Γ-point sampling is sufficient

## Related Entities / 相关实体

- [Card](card.md)
- [Bravais Lattice](bravais-lattice.md)
- [Calculation Type](calculation-type.md)

# ibrav Parameter / ibrav 参数

## Source Sources / 来源
- `raw/assets/validation.py` - ibrav validation logic
- `raw/assets/constants.py` - SYSTEM namelist documentation

## Definition / 定义

`ibrav` is the Bravais lattice index in the `&SYSTEM` namelist that specifies the crystal structure type. Values 0-14 correspond to different lattice symmetries.

`ibrav` 是 `&SYSTEM` 名称列表中的布拉维晶格索引，指定晶体结构类型。值 0-14 对应不同的晶格对称性。

## Values / 取值

| Value | Lattice Type | Chinese Description |
|-------|-------------|-------------------|
| 0 | Free crystal | 自由晶体 |
| 1 | Simple cubic | 简单立方 |
| 2 | Face-centered cubic | 面心立方 |
| 3 | Body-centered cubic | 体心立方 |
| 4 | Hexagonal | 六方 |
| 5 | Trigonal (rhombohedral) | 三角 (菱面) |
| -5 | Trigonal (hexagonal axes) | 三角 (六角轴) |
| 6 | Tetragonal (P) | 四方 (P) |
| 7 | Tetragonal (I) | 四方 (I) |
| 8 | Orthorhombic (P) | 正交 (P) |
| 9 | Orthorhombic (base-centered) | 正交 (底心) |
| 10 | Orthorhombic (face-centered) | 正交 (面心) |
| 11 | Orthorhombic (body-centered) | 正交 (体心) |
| 12 | Monoclinic (P) | 单斜 (P) |
| -12 | Monoclinic (base-centered) | 单斜 (底心) |
| 13 | Monoclinic (unique axis c) | 单斜 (唯一轴 c) |
| 14 | Triclinic | 三斜 |

## Lattice Parameters / 晶格参数

When `ibrav > 0`, use `celldm()` array:
- `celldm(1)` - Lattice constant a (in Bohr)
- `celldm(2-6)` - Dimensionless ratios

When `ibrav = 0`, must specify `CELL_PARAMETERS` card explicitly.

## Validation Rules / 验证规则

### ibrav = 0 / 自由晶体

**Error**: Missing `CELL_PARAMETERS` card

When `ibrav = 0`, the crystal structure is defined by explicit cell vectors in `CELL_PARAMETERS`. This card is required.

### ibrav ≠ 0 / 非自由晶体

**Warning**: Lattice parameters ignored

When `ibrav ≠ 0`, parameters `a`, `b`, `c`, `cosab`, `cosac`, `cosbc` are ignored because the lattice is defined by `celldm()` instead.

## Example / 示例

```
&SYSTEM
  ibrav = 2              ! Face-centered cubic
  celldm(1) = 10.26      ! Lattice constant in Bohr
  nat = 2
  ntyp = 1
  ecutwfc = 30.0
/
```

## Related Entities / 相关实体

- [SYSTEM Namelist](system-namelist.md)
- [CELL_PARAMETERS Card](cell-parameters-card.md)
- [Bravais Lattice](bravais-lattice.md)
- [celldm Parameter](celldm-parameter.md)

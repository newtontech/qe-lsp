# Bravais Lattice / 布拉维晶格

## Source Sources / 来源
- `raw/assets/constants.py` - ibrav parameter documentation
- `raw/assets/validation.py` - Lattice validation logic

## Purpose / 目的

Bravais lattices represent the 14 unique 3D crystal structures that can fill space without gaps. The `ibrav` parameter selects which lattice type to use.

布拉维晶格代表 14 种独特的可以无间隙填充空间的 3D 晶体结构。`ibrav` 参数选择要使用的晶格类型。

## 14 Bravais Lattices / 14 种布拉维晶格

### Cubic System / 立方晶系 (3)

| ibrav | Name | Chinese | Constraints |
|-------|------|---------|-------------|
| 1 | Simple cubic | 简单立方 | a=b=c, α=β=γ=90° |
| 2 | Face-centered cubic | 面心立方 | a=b=c, α=β=γ=90° |
| 3 | Body-centered cubic | 体心立方 | a=b=c, α=β=γ=90° |

### Tetragonal System / 四方晶系 (2)

| ibrav | Name | Chinese | Constraints |
|-------|------|---------|-------------|
| 6 | Tetragonal P | 四方 P | a=b≠c, α=β=γ=90° |
| 7 | Tetragonal I | 四方 I | a=b≠c, α=β=γ=90° |

### Orthorhombic System / 正交晶系 (4)

| ibrav | Name | Chinese | Constraints |
|-------|------|---------|-------------|
| 8 | Orthorhombic P | 正交 P | a≠b≠c, α=β=γ=90° |
| 9 | Orthorhombic base-centered | 正交底心 | a≠b≠c, α=β=γ=90° |
| 10 | Orthorhombic face-centered | 正交面心 | a≠b≠c, α=β=γ=90° |
| 11 | Orthorhombic body-centered | 正交体心 | a≠b≠c, α=β=γ=90° |

### Hexagonal System / 六方晶系 (1)

| ibrav | Name | Chinese | Constraints |
|-------|------|---------|-------------|
| 4 | Hexagonal | 六方 | a=b≠c, α=β=90°, γ=120° |

### Trigonal System / 三角晶系 (2)

| ibrav | Name | Chinese | Constraints |
|-------|------|---------|-------------|
| 5 | Trigonal (rhombohedral) | 三角 (菱面) | a=b=c, α=β=γ≠90° |
| -5 | Trigonal (hexagonal axes) | 三角 (六角轴) | a=b≠c, α=β=90°, γ=120° |

### Monoclinic System / 单斜晶系 (2)

| ibrav | Name | Chinese | Constraints |
|-------|------|---------|-------------|
| 12 | Monoclinic P | 单斜 P | a≠b≠c, α=γ=90°≠β |
| -12 | Monoclinic base-centered | 单斜底心 | a≠b≠c, α=γ=90°≠β |

### Triclinic System / 三斜晶系 (1)

| ibrav | Name | Chinese | Constraints |
|-------|------|---------|-------------|
| 14 | Triclinic | 三斜 | a≠b≠c, α≠β≠γ≠90° |

### Free Crystal / 自由晶体 (1)

| ibrav | Name | Chinese | Constraints |
|-------|------|---------|-------------|
| 0 | Free crystal | 自由晶体 | Arbitrary cell vectors |

## Lattice Parameters / 晶格参数

For `ibrav > 0`, parameters are defined by `celldm()` array:

对于 `ibrav > 0`，参数由 `celldm()` 数组定义：

- `celldm(1)` - Lattice constant a (Bohr)
- `celldm(2)` - Ratio b/a
- `celldm(3)` - Ratio c/a
- `celldm(4)` - cos(α)
- `celldm(5)` - cos(β)
- `celldm(6)` - cos(γ)

For `ibrav = 0`, use `CELL_PARAMETERS` card instead.

## Examples / 示例

### Silicon Diamond (FCC) / 硅金刚石 (面心立方)

```
&SYSTEM
  ibrav = 2              ! FCC
  celldm(1) = 10.26      ! a = 10.26 Bohr
  nat = 2
  ntyp = 1
/
```

### Graphene-like (Hexagonal) / 类石墨烯 (六方)

```
&SYSTEM
  ibrav = 4              ! Hexagonal
  celldm(1) = 4.65       ! a
  celldm(3) = 1.5        ! c/a (for layered system)
/
```

### Arbitrary Crystal (Free) / 任意晶体 (自由)

```
&SYSTEM
  ibrav = 0              ! Free crystal
  nat = 9
  ntyp = 2
/
CELL_PARAMETERS {angstrom}
4.913 0.0 0.0
0.0 4.913 0.0
0.0 0.0 5.405
```

## Symmetry Constraints / 对称性约束

Higher symmetry lattices (lower `ibrav` for non-zero values) have constraints:
- Fewer independent parameters needed
- Faster calculations
- May not match experimental data exactly

Lower symmetry (higher `ibrav` values, especially ibrav=0):
- More parameters
- More flexibility
- Slower calculations

## Related Entities / 相关实体

- [ibrav Parameter](ibrav-parameter.md)
- [celldm Parameter](celldm-parameter.md)
- [CELL_PARAMETERS Card](cell-parameters-card.md)

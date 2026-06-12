# celldm Parameter / celldm 参数

## Source Sources / 来源
- `raw/assets/constants.py` - SYSTEM namelist documentation
- `raw/assets/silicon_scf.in` - celldm example

## Purpose / 目的

The `celldm()` array defines lattice parameters for the crystal structure when `ibrav > 0`.

当 `ibrav > 0` 时，`celldm()` 数组定义晶体结构的晶格参数。

## When Used / 何时使用

- **Used** when `ibrav > 0` (standard Bravais lattices)
  `ibrav > 0`（标准布拉维晶格）时使用
- **Ignored** when `ibrav = 0` (use CELL_PARAMETERS instead)
  `ibrav = 0` 时忽略（改用 CELL_PARAMETERS）

## Array Elements / 数组元素

| Element | Description | Chinese Description | Default |
|---------|-------------|-------------------|---------|
| `celldm(1)` | Lattice constant a (in Bohr) | 晶格常数 a (玻尔) | Required |
| `celldm(2)` | b/a ratio | b/a 比率 | 1.0 |
| `celldm(3)` | c/a ratio | c/a 比率 | 1.0 |
| `celldm(4)` | cos(α) | cos(α) | Species-dependent |
| `celldm(5)` | cos(β) | cos(β) | Species-dependent |
| `celldm(6)` | cos(γ) | cos(γ) | Species-dependent |

## Unit / 单位

`celldm(1)` is specified in **Bohr** (atomic units).

`celldm(1)` 以**玻尔**（原子单位）指定。

Conversion: 1 Bohr = 0.529177 Å

## Examples / 示例

### Cubic (ibrav=1,2,3) / 立方

```
&SYSTEM
  ibrav = 2              ! FCC
  celldm(1) = 10.26      ! a = 10.26 Bohr (~5.43 Å)
/
```

Only `celldm(1)` is needed for cubic systems.

### Tetragonal (ibrav=6,7) / 四方

```
&SYSTEM
  ibrav = 6              ! Tetragonal P
  celldm(1) = 10.26      ! a
  celldm(2) = 1.0        ! b/a = 1.0
  celldm(3) = 1.5        ! c/a = 1.5
/
```

### Orthorhombic (ibrav=8) / 正交

```
&SYSTEM
  ibrav = 8              ! Orthorhombic P
  celldm(1) = 10.26      ! a
  celldm(2) = 1.2        ! b/a
  celldm(3) = 1.5        ! c/a
/
```

### Hexagonal (ibrav=4) / 六方

```
&SYSTEM
  ibrav = 4              ! Hexagonal
  celldm(1) = 9.0        ! a
  celldm(3) = 1.63       ! c/a
/
```

Default `celldm(2)` and `celldm(4)` are set automatically for hexagonal.

### Triclinic (ibrav=14) / 三斜

```
&SYSTEM
  ibrav = 14             ! Triclinic
  celldm(1) = 10.0       ! a
  celldm(2) = 1.1        ! b/a
  celldm(3) = 1.2        ! c/a
  celldm(4) = 0.1        ! cos(α)
  celldm(5) = 0.2        ! cos(β)
  celldm(6) = 0.3        ! cos(γ)
/
```

## Alternative: a, b, c Parameters / 替代方案：a, b, c 参数

As an alternative to `celldm(1)`, you can use `a` (in Angstrom):

除了 `celldm(1)`，您可以使用 `a`（埃）：

```
&SYSTEM
  ibrav = 2
  a = 5.43              ! Angstrom instead of Bohr
/
```

Note: Mixing `celldm(1)` and `a` is not recommended.

## Default Values / 默认值

When not specified:
- `celldm(2-3)`: 1.0 (for cubic systems)
- `celldm(4-6)`: Depends on crystal system

## Relation to CELL_PARAMETERS / 与 CELL_PARAMETERS 的关系

| ibrav | Use celldm | Use CELL_PARAMETERS |
|-------|------------|-------------------|
| 0 | No | Yes |
| 1-14 | Yes | No |

When `ibrav = 0`, all `celldm` values are ignored and `CELL_PARAMETERS` card is required.

## Related Entities / 相关实体

- [ibrav Parameter](ibrav-parameter.md)
- [CELL_PARAMETERS Card](cell-parameters-card.md)
- [Bravais Lattice](bravais-lattice.md)

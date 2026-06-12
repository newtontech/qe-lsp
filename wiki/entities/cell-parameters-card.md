# CELL_PARAMETERS Card / 晶胞参数卡片

## Source Sources / 来源
- `raw/assets/validation.py` - ibrav=0 validation
- `raw/assets/sio2_vc_relax.in` - CELL_PARAMETERS example

## Purpose / 目的

Specifies explicit cell vectors when `ibrav = 0` (free crystal structure).

当 `ibrav = 0`（自由晶体结构）时指定显式晶胞矢量。

## When Required / 何时需要

**Required** when `ibrav = 0`

**Ignored** when `ibrav ≠ 0`

## Syntax / 语法

```
CELL_PARAMETERS [unit]
a1_x a1_y a1_z
a2_x a2_y a2_z
a3_x a3_y a3_z
```

Each row represents one lattice vector.

## Units / 单位

| Unit | Chinese Description | Example |
|------|-------------------|---------|
| `angstrom` | 埃 (Å) | 5.43 0.0 0.0 |
| `bohr` | 玻尔 | 10.26 0.0 0.0 |
| `(alat)` | 晶格常数单位 | 1.0 0.0 0.0 |

Default: `alat` (if not specified)

## Cell Vectors / 晶胞矢量

The three rows define the three lattice vectors **a**, **b**, **c**:

三行定义三个晶格矢量 **a**, **b**, **c**：

```
CELL_PARAMETERS {angstrom}
a1_x a1_y a1_z    ! a vector
a2_x a2_y a2_z    ! b vector
a3_x a3_y a3_z    ! c vector
```

## Validation Rules / 验证规则

### Missing Card / 缺少卡片

**Severity**: Error

**Message**: "ibrav = 0 requires an explicit CELL_PARAMETERS card."

When `ibrav = 0` and no `CELL_PARAMETERS` card is present.

## Example / 示例

### Orthorhombic Cell / 正交晶胞

```
&SYSTEM
  ibrav = 0
  nat = 2
  ntyp = 1
/
CELL_PARAMETERS {angstrom}
4.913 0.0 0.0    ! a vector
0.0 4.913 0.0    ! b vector
0.0 0.0 5.405    ! c vector
```

### Triclinic Cell / 三斜晶胞

```
CELL_PARAMETERS {angstrom}
5.0 0.1 0.2
0.1 5.5 0.3
0.2 0.3 6.0
```

### Bohr Units / 玻尔单位

```
CELL_PARAMETERS {bohr}
10.26 0.0 0.0
0.0 10.26 0.0
0.0 0.0 10.26
```

### Alat Units / 晶格常数单位

```
&SYSTEM
  ibrav = 0
  celldm(1) = 10.26    ! Reference length
/
CELL_PARAMETERS    ! Default is alat
1.0 0.0 0.0
0.0 1.0 0.0
0.0 0.0 1.0
```

## Relation to ibrav / 与 ibrav 的关系

| ibrav Value | CELL_PARAMETERS Required? | Chinese Description |
|-------------|--------------------------|-------------------|
| 0 | Yes | 需要 |
| 1-14 | No | 不需要 (ignored) |

When `ibrav ≠ 0`, the lattice is defined by `celldm()` parameters instead, and any `CELL_PARAMETERS` card is ignored.

## Volume Calculation / 体积计算

The cell volume is calculated as the scalar triple product:

晶胞体积计算为标量三重积：

```
V = a · (b × c)
```

This volume is used for:
- Energy normalization
- Pressure calculations
- Density calculations

## With VC-Relax / 与变晶胞弛豫

When using `calculation = 'vc-relax'`, the cell vectors in `CELL_PARAMETERS` are optimized along with atomic positions.

使用 `calculation = 'vc-relax'` 时，`CELL_PARAMETERS` 中的晶胞矢量与原子位置一起优化。

## Related Entities / 相关实体

- [ibrav Parameter](ibrav-parameter.md)
- [CELL Namelist](cell-namelist-reference.md)
- [celldm Parameter](celldm-parameter.md)
- [Card](card.md)

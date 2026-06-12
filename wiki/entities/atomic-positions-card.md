# ATOMIC_POSITIONS Card / 原子位置卡片

## Source Sources / 来源
- `raw/assets/validation.py` - `_validate_atomic_positions()` function
- `raw/assets/silicon_scf.in` - ATOMIC_POSITIONS example

## Purpose / 目的

Specifies the coordinates of atoms in the crystal structure.

指定晶体结构中原子的坐标。

## Syntax / 语法

```
ATOMIC_POSITIONS [unit]
Symbol1 x y z [if_pos]
Symbol2 x y z [if_pos]
...
```

## Units / 单位

| Unit | Chinese Description | Coordinate Range |
|------|-------------------|-----------------|
| `crystal` | 晶体坐标 | 0-1 (fractional) |
| `angstrom` | 埃 | Any (absolute) |
| `bohr` | 玻尔 | Any (absolute) |
| `(alat)` | Lattice constant units | Any (fractional) |

Default: `alat` if not specified

## Optional Constraints / 可选约束

`if_pos` values control which coordinates are fixed during relaxation:

`if_pos` 值控制弛豫期间哪些坐标固定：

| Value | Description | Chinese Description |
|-------|-------------|-------------------|
| 0 | Fixed | 固定 |
| 1 | Free to move | 可移动 |
| 2, 3, ... | Alternative behavior | 替代行为 |

Example: `Si 0.0 0.0 0.0 0 0 1` fixes x and y, allows z to relax.

## Validation Rules / 验证规则

### Missing Species / 缺少种类

**Severity**: Error

**Message**: "Element {symbol} is missing from ATOMIC_SPECIES."

When an element symbol in ATOMIC_POSITIONS is not declared in ATOMIC_SPECIES.

### Crystal Coordinates Range / 晶体坐标范围

**Severity**: Warning

**Message**: "Crystal coordinates should normally be between 0 and 1."

When coordinates are outside [0,1] for crystal units, a warning is issued because unusual values may indicate errors.

Note: Values outside [0,1] are sometimes valid (e.g., atoms at boundaries).

## Example / 示例

### Crystal Coordinates / 晶体坐标

```
ATOMIC_POSITIONS {crystal}
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25
```

### Angstrom Coordinates / 埃坐标

```
ATOMIC_POSITIONS {angstrom}
Si 0.00 0.00 0.00
Si 1.36 1.36 1.36
```

### With Constraints / 带约束

```
ATOMIC_POSITIONS {crystal}
Si 0.0 0.0 0.0 0 0 1    ! Fixed x,y, free z
Si 0.5 0.5 0.0 1 1 1    ! Free to move
```

### Different Species / 不同种类

```
ATOMIC_SPECIES
Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF
O 15.999 O.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
Si 0.0 0.0 0.0
O 0.3 0.3 0.25
```

## Order Independence / 顺序无关

The order of atoms in ATOMIC_POSITIONS does not need to match the order in ATOMIC_SPECIES.

ATOMIC_POSITIONS 中原子的顺序不需要与 ATOMIC_SPECIES 中的顺序匹配。

## Related Entities / 相关实体

- [ATOMIC_SPECIES Card](atomic-species-card.md)
- [Card](card.md)
- [IONS Namelist](ions-namelist-reference.md)

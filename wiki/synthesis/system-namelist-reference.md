# SYSTEM Namelist Reference / SYSTEM 名称列表参考

## Source Sources / 来源
- `raw/assets/constants.py` - `QE_PARAM_DOCS["&SYSTEM"]`

## Purpose / 目的

Defines the physical system: crystal structure, atomic positions, basis sets, and pseudopotentials.

定义物理系统：晶体结构、原子位置、基组和赝势。

## Parameters / 参数

### Crystal Structure / 晶体结构

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `ibrav` | integer | Bravais lattice index (0-14) | 布拉维晶格索引 |
| `celldm(1)` | real | Lattice constant a (Bohr) | 晶格常数 a |
| `celldm(2-6)` | real | Dimensionless lattice ratios | 无量纲晶格比率 |
| `a`, `b`, `c` | real | Lattice constants (Å) | 晶格常数 |
| `cosab`, `cosac`, `cosbc` | real | Cosines of lattice angles | 晶格角余弦 |

### Atomic System / 原子系统

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `nat` | integer | Number of atoms | 原子数 |
| `ntyp` | integer | Number of atom types | 原子类型数 |

### Electronic Structure / 电子结构

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `nbnd` | integer | Number of bands | 能带数 |
| `ecutwfc` | real | Wavefunction cutoff (Ry) | 波函数截断 |
| `ecutrho` | real | Charge density cutoff (Ry) | 电荷密度截断 |
| `tot_charge` | real | Total charge | 总电荷 |
| `tot_magnetization` | real | Total magnetization | 总磁化强度 |
| `nspin` | integer | Spin polarization | 自旋极化 |

### Occupations / 占据

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `occupations` | string | Occupation method | 占据方法 |
| `smearing` | string | Smearing type | 展宽类型 |
| `degauss` | real | Smearing width (Ry) | 展宽宽度 |

### DFT Functional / DFT 泛函

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `input_dft` | string | Override XC functional | 覆盖 XC 泛函 |
| `exx_fraction` | real | Exact exchange fraction | 精确交换比例 |

## Parameter Details / 参数详情

### ibrav / 布拉维晶格索引

| Value | Lattice | Description |
|-------|---------|-------------|
| 0 | Free | Requires CELL_PARAMETERS |
| 1 | Simple cubic | 简单立方 |
| 2 | FCC | 面心立方 |
| 3 | BCC | 体心立方 |
| 4 | Hexagonal | 六方 |
| 5 | Trigonal | 三角 (菱面) |

See [ibrav Parameter](ibrav-parameter.md) for full list.

### celldm Array / celldm 数组

When `ibrav > 0`, use `celldm(1)` for lattice constant in Bohr.

- `celldm(1) = a` (Bohr)
- `celldm(2) = b/a`
- `celldm(3) = c/a`
- `celldm(4) = cos(α)`
- `celldm(5) = cos(β)`
- `celldm(6) = cos(γ)`

### ecutwfc / 波函数截断

Kinetic energy cutoff for wavefunctions in Rydberg.

里德堡单位的波函数动能截断。

Typical: 20-100 Ry (depends on system and pseudopotential)

### ecutrho / 电荷密度截断

Kinetic energy cutoff for charge density and potential.

电荷密度和势的动能截断。

**Requirements**:
- PAW: `ecutrho ≥ 8 * ecutwfc`
- Ultrasoft: `ecutrho ≥ 4 * ecutwfc`
- NCPP: `ecutrho ≥ 4 * ecutwfc`

### nspin / 自旋极化

| Value | Description | Chinese Description |
|-------|-------------|-------------------|
| 1 | No spin polarization | 无自旋极化 |
| 2 | Spin-polarized | 自旋极化 |
| 4 | Non-collinear | 非共线 |

### occupations / 占据方法

Values: `'fixed'`, `'smearing'`, `'tetrahedra'`

- `'fixed'`: Fixed occupations (insulators)
- `'smearing'`: Smearing for metals
- `'tetrahedra'`: Tetrahedron method

### smearing / 展宽类型

Values: `'gaussian'`, `'methfessel-paxton'`, `'marzari-vanderbilt'`, `'fermi-dirac'`

## Example / 示例

### FCC Silicon / 面心立方硅

```
&SYSTEM
  ibrav = 2              ! FCC
  celldm(1) = 10.26      ! a = 10.26 Bohr
  nat = 2
  ntyp = 1
  ecutwfc = 30.0
  ecutrho = 240.0
/
```

### Free Crystal / 自由晶体

```
&SYSTEM
  ibrav = 0              ! Free crystal
  nat = 9
  ntyp = 2
  ecutwfc = 60.0
  ecutrho = 480.0
/
CELL_PARAMETERS {angstrom}
4.913 0.0 0.0
0.0 4.913 0.0
0.0 0.0 5.405
```

## Related Entities / 相关实体

- [ibrav Parameter](ibrav-parameter.md)
- [ecutwfc & ecutrho](ecutwfc-ecutrho.md)
- [CELL_PARAMETERS Card](cell-parameters-card.md)

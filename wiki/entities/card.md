# Card / 卡片

## Source Sources / 来源
- `raw/assets/constants.py` - QE_CARDS, QE_HOVER_DOCS
- `raw/assets/parser.py` - Card parsing logic

## Definition / 定义

Cards are data sections in Quantum ESPRESSO input that specify structured information like atomic species, positions, k-points, and cell parameters. Unlike namelists, cards are not Fortran-style blocks.

Card 是 Quantum ESPRESSO 输入中用于指定结构化信息的数据部分，如原子种类、位置、k 点和晶胞参数。与名称列表不同，卡片不是 Fortran 风格的块。

## Supported Cards / 支持的卡片

| Card | Purpose | Chinese Description |
|------|---------|-------------------|
| `ATOMIC_SPECIES` | Element symbols, masses, pseudopotentials | 元素符号、质量、赝势 |
| `ATOMIC_POSITIONS` | Atomic coordinates | 原子坐标 |
| `K_POINTS` | Brillouin zone sampling | 布里渊区采样 |
| `CELL_PARAMETERS` | Explicit cell vectors | 显式晶胞矢量 |

## Syntax / 语法

Cards appear as a header line followed by data rows:

```
CARD_NAME [options]
data_row_1
data_row_2
```

## ATOMIC_SPECIES / 原子种类

Specifies element symbols, atomic masses, and pseudopotential files:

```
ATOMIC_SPECIES
Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF
O 15.999 O.pbe-n-rrkjus_psl.1.0.0.UPF
```

Each row: `symbol mass pseudo_file`

## ATOMIC_POSITIONS / 原子位置

Lists atomic coordinates with optional unit specification:

```
ATOMIC_POSITIONS {crystal}
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25
```

Units: `crystal`, `angstrom`, `bohr`

## K_POINTS / K 点

Defines k-point mesh for Brillouin zone integration:

```
K_POINTS {automatic}
8 8 8 0 0 0
```

Options: `automatic`, `gamma`, `crystal`, `tpiba`, etc.

## CELL_PARAMETERS / 晶胞参数

Specifies cell vectors when `ibrav=0`:

```
CELL_PARAMETERS {angstrom}
4.913 0.0 0.0
0.0 4.913 0.0
0.0 0.0 5.405
```

Units: `angstrom`, `bohr`

## Validation Rules / 验证规则

- **Missing species in ATOMIC_POSITIONS**: Error when element not in ATOMIC_SPECIES
- **Crystal coordinates range**: Warning when coordinates outside [0,1]
- **Pseudopotential mismatch**: Error when pseudo file doesn't match element symbol

## Related Entities / 相关实体

- [Namelist](quantum-espresso-namelist.md)
- [Pseudopotential](pseudopotential.md)
- [Bravais Lattice](bravais-lattice.md)
- [K-points](k-points.md)

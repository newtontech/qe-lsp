# Input File Format / 输入文件格式

## Source Sources / 来源
- `raw/assets/parser.py` - Input parsing logic
- `raw/assets/silicon_scf.in` - Example input file

## File Structure / 文件结构

Quantum ESPRESSO input files have a specific structure with namelists and cards:

Quantum ESPRESSO 输入文件具有特定的结构，包含名称列表和卡片：

```
! Comments start with !

&NAMELIST1
  parameter1 = value1
  parameter2 = value2
/

&NAMELIST2
  parameter3 = value3
/

CARD_NAME1 [options]
data_row_1
data_row_2

CARD_NAME2 [options]
data_row_1
```

## Components / 组件

### Comments / 注释

Lines starting with `!` are comments.

以 `!` 开头的行是注释。

Example: `! Silicon SCF calculation`

### Namelists / 名称列表

Blocks starting with `&NAME` and ending with `/`.

以 `&NAME` 开始、`/` 结束的块。

```
&CONTROL
  calculation = 'scf'
/
```

### Cards / 卡片

Data sections that appear after namelists.

出现在名称列表之后的数据部分。

```
ATOMIC_SPECIES
Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF
```

## Order of Sections / 部分顺序

Typical order in input files:

输入文件中的典型顺序：

1. Comments (optional)
2. `&CONTROL` namelist
3. `&SYSTEM` namelist
4. `&ELECTRONS` namelist
5. `&IONS` namelist (if needed)
6. `&CELL` namelist (if needed)
7. `ATOMIC_SPECIES` card
8. `ATOMIC_POSITIONS` card
9. `K_POINTS` card
10. `CELL_PARAMETERS` card (if `ibrav=0`)

## Value Formats / 值格式

| Type | Format | Examples |
|------|--------|----------|
| String | `'value'` or `"value"` | `'scf'`, `"from_scratch"` |
| Integer | `number` | `2`, `100` |
| Real | `number` or `number`d`exponent` | `30.0`, `1.0d-8` |
| Logical | `.true.` or `.false.` | `.true.`, `.false.` |
| Array | `name(index)` | `celldm(1)`, `nat` |

## Inline Comments / 行内注释

Inline comments are stripped by the parser:

解析器会剥离行内注释：

```
calculation = 'scf'   ! This is a comment
```

Parsed as: `calculation = 'scf'`

解析为：`calculation = 'scf'`

## Case Sensitivity / 大小写敏感

- Namelist names: Case-insensitive (but conventionally uppercase)
  名称列表名称：不区分大小写（但通常为大写）
- Parameter names: Case-insensitive
  参数名称：不区分大小写
- String values: Case-sensitive
  字符串值：区分大小写
- Card names: Case-insensitive
  卡片名称：不区分大小写

## Complete Example / 完整示例

```
! Silicon SCF calculation
&CONTROL
  calculation = 'scf'
  restart_mode = 'from_scratch'
  pseudo_dir = './pseudo/'
  outdir = './tmp/'
/

&SYSTEM
  ibrav = 2
  celldm(1) = 10.26
  nat = 2
  ntyp = 1
  ecutwfc = 30.0
  ecutrho = 240.0
/

&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
/

ATOMIC_SPECIES
Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25

K_POINTS {automatic}
8 8 8 0 0 0
```

## File Extensions / 文件扩展名

| Extension | Calculation Type | Chinese Description |
|-----------|----------------|-------------------|
| `.in` | Generic | 通用 |
| `.scf.in` | SCF | 自洽场 |
| `.relax.in` | Relaxation | 弛豫 |
| `.vc-relax.in` | Variable-cell relaxation | 变晶胞弛豫 |
| `.bands.in` | Band structure | 能带结构 |
| `.nscf.in` | Non-SCF | 非自洽 |
| `.ph.in` | Phonon | 声子 |
| `.dos.in` | Density of states | 态密度 |

## Related Entities / 相关实体

- [Namelist](quantum-espresso-namelist.md)
- [Card](card.md)
- [Calculation Type](calculation-type.md)

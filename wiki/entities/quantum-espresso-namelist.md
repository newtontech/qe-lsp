# Namelist / 名称列表

## Source Sources / 来源
- `raw/assets/constants.py` - QE_KEYWORDS, QE_NAMELISTS
- `raw/assets/parser.py` - Namelist parsing logic

## Definition / 定义

A namelist is a Fortran-style input block in Quantum ESPRESSO that groups related parameters for a specific aspect of the calculation. Namelists start with `&NAME` and end with `/`.

NameList 是 Quantum ESPRESSO 中用于归组相关参数的 Fortran 风格输入块。名称列表以 `&NAME` 开始，以 `/` 结束。

## Syntax / 语法

```
&NAMELIST_NAME
  parameter1 = value1
  parameter2 = value2
/
```

## Supported Namelists / 支持的名称列表

| Namelist | Purpose | Chinese Description |
|----------|---------|-------------------|
| `&CONTROL` | Calculation execution control | 计算执行控制 |
| `&SYSTEM` | Physical system definition | 物理系统定义 |
| `&ELECTRONS` | Electronic structure control | 电子结构控制 |
| `&IONS` | Ionic relaxation dynamics | 离子弛豫动力学 |
| `&CELL` | Variable-cell relaxation | 变晶胞弛豫 |

## Parsing Behavior / 解析行为

The parser detects namelists by lines starting with `&`. When a namelist is opened, all subsequent parameter assignments (`name = value`) are attributed to that namelist until a closing `/` is encountered.

解析器通过以 `&` 开头的行检测名称列表。当打开名称列表时，所有后续参数赋值（`name = value`）都被归因于该名称列表，直到遇到结束符 `/`。

## Validation Rules / 验证规则

- **Unclosed namelist**: Error - Missing `/` at end
- **Duplicate parameters**: Error - Same parameter assigned twice

## Related Entities / 相关实体

- [Parameter Assignment](parameter-assignment.md)
- [Card](card.md)
- [Calculation Type](calculation-type.md)

# Parameter Assignment / 参数赋值

## Source Sources / 来源
- `raw/assets/parser.py` - ASSIGNMENT_RE pattern
- `raw/assets/constants.py` - Parameter documentation

## Purpose / 目的

Parameter assignments set values for namelist parameters in Quantum ESPRESSO input files.

参数赋值为 Quantum ESPRESSO 输入文件中的名称列表参数设置值。

## Syntax / 语法

```
parameter_name = value
```

## Assignment Pattern / 赋值模式

The parser recognizes this pattern:

解析器识别此模式：

```
([A-Za-z_][A-Za-z0-9_]*(?:\(\d+\))?)\s*=\s*('[^']*'|\"[^\"]*\"|[^\s,]+)
```

## Value Types / 值类型

### Strings / 字符串

Must be quoted with single or double quotes:

必须用单引号或双引号引起来：

```
calculation = 'scf'
restart_mode = "from_scratch"
```

### Integers / 整数

```
nat = 2
ntyp = 1
nstep = 50
```

### Real Numbers / 实数

Standard or Fortran D notation:

标准或 Fortran D 表示法：

```
ecutwfc = 30.0
conv_thr = 1.0d-8    ! Same as 1.0e-8
dt = 20.0
```

### Logicals / 逻辑值

Fortran-style:

Fortran 风格：

```
tprnfor = .true.
wf_collect = .false.
```

### Arrays / 数组

Indexed notation:

索引表示法：

```
celldm(1) = 10.26
celldm(2) = 1.0
```

## Case Sensitivity / 大小写敏感

- **Parameter names**: Case-insensitive
  参数名称：不区分大小写
- **String values**: Case-sensitive
  字符串值：区分大小写
- **Logical values**: Case-insensitive (`.true.`, `.TRUE.`, `.True.` all valid)
  逻辑值：不区分大小写

## Inline Comments / 行内注释

Comments after values are stripped by the parser:

值后的注释会被解析器剥离：

```
calculation = 'scf'   ! This comment is ignored
```

Parsed as: `calculation = 'scf'`

解析为：`calculation = 'scf'`

## Duplicate Detection / 重复检测

The parser detects duplicate parameter assignments within a namelist:

解析器检测名称列表中的重复参数赋值：

```
&SYSTEM
  ibrav = 2
  ibrav = 0    ! Error: Duplicate parameter
/
```

**Severity**: Error

**Message**: "Duplicate parameter ibrav."

## Array Indexing / 数组索引

Fortran-style 1-based indexing:

Fortran 风格的从 1 开始的索引：

```
celldm(1)    ! First element
celldm(2)    ! Second element
```

## Whitespace / 空白

Whitespace around `=` is optional:

`=` 周围的空格是可选的：

```
calculation='scf'        ! Valid
calculation = 'scf'      ! Valid
calculation  =  'scf'   ! Valid
```

## Validation / 验证

After parsing, parameters are validated for:

解析后，参数将进行以下验证：

- **Type correctness**: Value matches parameter type
  类型正确性：值与参数类型匹配
- **Value range**: Value within valid range
  值范围：值在有效范围内
- **Cross-parameter consistency**: Parameters consistent with each other
  参数间一致性：参数彼此一致

## Example / 示例

```
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
  electron_maxstep = 100
/
```

## Related Entities / 相关实体

- [Namelist](quantum-espresso-namelist.md)
- [Input File Format](input-file-format.md)
- [Validation](validation.md)

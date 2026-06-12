# ATOMIC_SPECIES Card / 原子种类卡片

## Source Sources / 来源
- `raw/assets/validation.py` - `_validate_pseudopotentials()` function
- `raw/assets/parser.py` - ATOMIC_SPECIES parsing

## Purpose / 目的

Declares the atomic species in the system, including element symbols, atomic masses, and pseudopotential files.

声明系统中的原子种类，包括元素符号、原子质量和赝势文件。

## Syntax / 语法

```
ATOMIC_SPECIES
Symbol Mass Pseudopotential_File
...
```

## Format / 格式

Each row contains three space-separated values:

每行包含三个空格分隔的值：

1. **Symbol** - Element symbol (e.g., Si, O, Fe)
   元素符号
2. **Mass** - Atomic mass in atomic mass units (e.g., 28.086)
   原子质量（原子质量单位）
3. **Pseudopotential_File** - Path to .UPF pseudopotential file
   赝势文件路径

## Example / 示例

```
ATOMIC_SPECIES
Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF
O 15.999 O.pbe-n-rrkjus_psl.1.0.0.UPF
Fe 55.845 Fe.pbe-n-rrkjus_psl.1.0.0.UPF
```

## Pseudopotential File Naming / 赝势文件命名

Standard format: `Element.XC-Type.Version.UPF`

标准格式：`Element.XC-Type.Version.UPF`

- **Element**: Must match row symbol
  元素：必须与行符号匹配
- **XC**: Exchange-correlation functional (pbe, lda, etc.)
  交换关联泛函
- **Type**: Pseudopotential type (paw, rrkjus, etc.)
  赝势类型
- **Version**: Version number
  版本号

## Validation Rules / 验证规则

### Element Mismatch / 元素不匹配

**Severity**: Error

**Message**: "Pseudopotential {file} does not appear to match element {symbol}."

When the pseudopotential filename doesn't start with the element symbol.

当赝势文件名不以元素符号开头时触发。

**Example of error**:
```
ATOMIC_SPECIES
Si 28.086 Fe.pbe-n-rrkjus_psl.1.0.0.UPF    ! Error: Fe ≠ Si
```

### Mixed Functionals / 混合泛函

**Severity**: Warning

**Message**: "Mixed pseudopotential functional families may be inconsistent."

When pseudopotentials from different XC functional families are mixed.

当混合来自不同 XC 泛函族的赝势时触发。

**Example**:
```
ATOMIC_SPECIES
Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF    ! PBE
O 15.999 O.lda-n-rrkjus_psl.1.0.0.UPF     ! LDA - Mixed!
```

## Reference by ATOMIC_POSITIONS / 被 ATOMIC_POSITIONS 引用

All element symbols used in `ATOMIC_POSITIONS` must be declared in `ATOMIC_SPECIES`.

`ATOMIC_POSITIONS` 中使用的所有元素符号必须在 `ATOMIC_SPECIES` 中声明。

```
ATOMIC_SPECIES
Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF
O 15.999 O.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
Si 0.0 0.0 0.0      ! Valid - declared above
O 0.3 0.3 0.25      ! Valid - declared above
C 0.5 0.5 0.5       ! Error - C not declared
```

## Pseudopotential Directories / 赝势目录

The `pseudo_dir` parameter in `&CONTROL` specifies where to look for pseudopotential files:

`&CONTROL` 中的 `pseudo_dir` 参数指定查找赝势文件的位置：

```
&CONTROL
  pseudo_dir = './pseudo/'
/
```

## Best Practices / 最佳实践

1. **Consistent functionals**: Use same XC functional for all species
   一致的泛函：所有种类使用相同的 XC 泛函
2. **Mass accuracy**: Use accurate atomic masses
   准确的质量：使用准确的原子质量
3. **File existence**: Ensure .UPF files exist in `pseudo_dir`
   文件存在：确保 .UPF 文件存在于 `pseudo_dir` 中

## Related Entities / 相关实体

- [Pseudopotential](pseudopotential.md)
- [ATOMIC_POSITIONS Card](atomic-positions-card.md)
- [CONTROL Namelist](control-namelist-reference.md)

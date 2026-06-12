# ecutwfc & ecutrho Parameters / 能量截断参数

## Source Sources / 来源
- `raw/assets/validation.py` - Cutoff ratio validation
- `raw/assets/constants.py` - SYSTEM namelist documentation

## Definition / 定义

`ecutwfc` is the kinetic energy cutoff for wavefunctions, and `ecutrho` is the cutoff for charge density and potential. Both are specified in Rydberg (Ry).

`ecutwfc` 是波函数的动能截断，`ecutrho` 是电荷密度和势的截断。两者均以里德堡 (Ry) 为单位。

## Location / 位置

Both parameters are in the `&SYSTEM` namelist.

两者参数位于 `&SYSTEM` 名称列表中。

## Required Ratio / 要求的比率

The relationship between cutoffs depends on pseudopotential type:

截断之间的关系取决于赝势类型：

| Pseudopotential Type | Minimum Ratio | Chinese Description |
|---------------------|---------------|-------------------|
| PAW (Projector Augmented Wave) | 8:1 | 投影缀加平面波 |
| Ultrasoft/NCPP | 4:1 | 超软/模守恒 |

## Validation Rules / 验证规则

### Low Ratio Warning / 低比率警告

**Severity**: Warning

**Message**: "ecutrho should normally be at least {ratio}x ecutwfc."

When `ecutrho < ratio * ecutwfc`, a warning is issued because the charge density grid may be too coarse to accurately represent the wavefunctions.

## Pseudopotential Detection / 赝势检测

The validator automatically detects PAW pseudopotentials by checking for "paw" in the pseudopotential filename (case-insensitive).

验证器通过检查赝势文件名中的 "paw"（不区分大小写）自动检测 PAW 赝势。

## Example / 示例

```
&SYSTEM
  ibrav = 2
  celldm(1) = 10.26
  nat = 2
  ntyp = 1
  ecutwfc = 30.0      ! Wavefunction cutoff
  ecutrho = 240.0     ! Charge density cutoff (8x for PAW, 4x otherwise)
/
```

## Best Practices / 最佳实践

1. **PAW calculations**: Use `ecutrho ≥ 8 * ecutwfc`
2. **Ultrasoft/NCPP**: Use `ecutrho ≥ 4 * ecutwfc`
3. **Convergence testing**: Always test convergence with respect to both cutoffs

## Related Entities / 相关实体

- [SYSTEM Namelist](system-namelist.md)
- [Pseudopotential](pseudopotential.md)
- [ATOMIC_SPECIES Card](atomic-species-card.md)

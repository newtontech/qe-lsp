# Pseudopotential / 赝势

## Source Sources / 来源
- `raw/assets/validation.py` - `_validate_pseudopotentials()` function
- `raw/assets/parser.py` - ATOMIC_SPECIES parsing

## Definition / 定义

Pseudopotentials are effective potentials that replace core electrons in DFT calculations, allowing simulation of valence electrons with fewer plane waves.

赝势是 DFT 计算中替代核心电子的有效势，允许使用较少的平面波模拟价电子。

## ATOMIC_SPECIES Format / ATOMIC_SPECIES 格式

```
ATOMIC_SPECIES
Symbol Mass Pseudopotential_File
```

**Example**:
```
ATOMIC_SPECIES
Si 28.086 Si.pbe-n-rrkjus_psl.1.0.0.UPF
O 15.999 O.pbe-n-rrkjus_psl.1.0.0.UPF
```

## Naming Convention / 命名约定

Pseudopotential files typically follow this pattern:
```
Element.Exchange-Correlation.Type.Version.UPF
```

**Components**:
- Element symbol (e.g., `Si`, `O`)
- XC functional (e.g., `pbe`, `lda`, `blyp`)
- Type (e.g., `n-rrkjus`, `rrkjus`, `paw`)
- Version (e.g., `1.0.0`)

## Pseudopotential Types / 赝势类型

| Type | Chinese Description | Cutoff Ratio |
|------|-------------------|-------------|
| NCPP (Norm-Conserving) | 模守恒赝势 | 4x |
| Ultrasoft | 超软赝势 | 4x |
| PAW (Projector Augmented Wave) | 投影缀加平面波 | 8x |

## Validation Rules / 验证规则

### Element Mismatch / 元素不匹配

**Severity**: Error

**Message**: "Pseudopotential {file} does not appear to match element {symbol}."

When the pseudopotential filename prefix doesn't match the element symbol in ATOMIC_SPECIES.

Example: `Si 28.086 Fe.pbe-n-rrkjus.UPF` triggers error because `Fe` ≠ `Si`.

### Mixed Functionals / 混合泛函

**Severity**: Warning

**Message**: "Mixed pseudopotential functional families may be inconsistent."

When ATOMIC_SPECIES contains pseudopotentials from different XC functional families (e.g., mixing PBE and LDA).

## Common Functional Families / 常见泛函族

| Functional | Chinese | Abbreviation |
|------------|---------|-------------|
| Perdew-Burke-Ernzerhof | PBE 泛函 | pbe |
| Local Density Approximation | 局域密度近似 | lda |
| BLYP | BLYP 泛函 | blyp |
| PBEsol | PBEsol 泛函 | pbesol |

## UPF Format / UPF 格式

Quantum ESPRESSO uses UPF (Unified Pseudopotential Format) files with `.UPF` extension.

Quantum ESPRESSO 使用扩展名为 `.UPF` 的 UPF (统一赝势格式) 文件。

## Related Entities / 相关实体

- [ATOMIC_SPECIES Card](atomic-species-card.md)
- [ecutwfc & ecutrho](ecutwfc-ecutrho.md)
- [ATOMIC_POSITIONS Card](atomic-positions-card.md)

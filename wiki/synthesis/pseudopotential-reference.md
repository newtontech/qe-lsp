# Pseudopotential Reference / 赝势参考

## Source / 来源
- `raw/assets/qe-pseudopotentials.md` - Pseudopotential documentation

## PP Types and Compatibility / 赝势类型与兼容性

| Type / 类型 | Cutoff Ratio / 截断比 | Limitations / 限制 |
|-------------|---------------------|-------------------|
| Norm-Conserving (NC) | ecutrho = 4x ecutwfc | Most compatible; required for meta-GGA, Raman |
| Ultrasoft (US) | ecutrho = 8-12x ecutwfc | Softer; not for meta-GGA or Raman |
| PAW | ecutrho = 8-12x ecutwfc | Most accurate; not for CP code |

## UPF Format / UPF 格式

QE uses the Unified Pseudopotential Format (UPF v2) as its native format. UPF files are XML-structured.

QE 使用统一赝势格式 (UPF v2) 作为其原生格式。UPF 文件是 XML 结构的。

Key sections in a UPF file:
- `PP_HEADER` — Element, type, functional, valence, cutoffs
- `PP_MESH` — Radial grid
- `PP_LOCAL` — Local potential
- `PP_NONLOCAL` — Projectors and D_ij
- `PP_PSWFC` — Pseudo wavefunctions
- `PP_RHOATOM` — Atomic charge density

## PP Libraries / 赝势库

| Library | Type | URL | Notes |
|---------|------|-----|-------|
| **SSSP** | PAW/US/NC | materialscloud.org/discover/sssp | Recommended default |
| **PSlibrary** | US/PAW | github.com/dalcorso/pslibrary | Multiple functionals |
| **GBRV** | US | physics.rutgers.edu/gbrv | High-throughput |
| **SG15** | NC/PAW | — | High accuracy |
| **PseudoDojo** | NC/PAW | pseudo-dojo.org | Stringent verification |

## File Naming Convention / 文件命名约定

```
Element.Functional-Type_Author.Version.UPF
```

Example: `Si.pbe-n-rrkjus_psl.1.0.0.UPF`
- `Si` — Element
- `pbe` — PBE functional
- `n` — Norm-conserving
- `rrkjus` — RRKJ method
- `psl` — PSlibrary
- `1.0.0` — Version

## Validation Rules / 验证规则

1. Element symbol must match PP filename prefix
   元素符号必须与 PP 文件名前缀匹配
2. All PPs should use the same XC functional family
   所有 PP 应使用相同的 XC 泛函族
3. Always test PPs on simple systems first
   始终先在简单系统上测试 PP

## Related Pages / 相关页面

- [Pseudopotential Entity](../entities/pseudopotential.md)
- [ecutwfc & ecutrho](../entities/ecutwfc-ecutrho.md)
- [ATOMIC_SPECIES Card](../entities/atomic-species-card.md)

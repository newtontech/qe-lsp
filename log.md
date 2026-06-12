# Change Log / 变更日志

This log tracks all changes to the QE-LSP LLM Wiki.

此日志跟踪 QE-LSP LLM 维基的所有更改。

## 2025-06-12 / 2025年6月12日

### Initial Wiki Creation / 初始维基创建

Created the LLM Wiki structure for QE-LSP with 25 wiki pages covering:

为 QE-LSP 创建了 LLM 维基结构，包含 25 个维基页面：

#### Entity Pages (9) / 实体页面

1. [quantum-espresso-namelist.md](wiki/entities/quantum-espresso-namelist.md) - Namelist definition and types
2. [card.md](wiki/entities/card.md) - Card types and syntax
3. [ibrav-parameter.md](wiki/entities/ibrav-parameter.md) - Bravais lattice index
4. [ecutwfc-ecutrho.md](wiki/entities/ecutwfc-ecutrho.md) - Energy cutoff parameters
5. [calculation-type.md](wiki/entities/calculation-type.md) - All calculation types
6. [pseudopotential.md](wiki/entities/pseudopotential.md) - Pseudopotential concepts
7. [k-points.md](wiki/entities/k-points.md) - K-point mesh options
8. [mixing-beta.md](wiki/entities/mixing-beta.md) - SCF mixing parameter
9. [parameter-assignment.md](wiki/entities/parameter-assignment.md) - Assignment syntax

#### Card-Specific Entities (4) / 卡片特定实体

10. [atomic-species-card.md](wiki/entities/atomic-species-card.md) - ATOMIC_SPECIES card
11. [atomic-positions-card.md](wiki/entities/atomic-positions-card.md) - ATOMIC_POSITIONS card
12. [cell-parameters-card.md](wiki/entities/cell-parameters-card.md) - CELL_PARAMETERS card
13. [celldm-parameter.md](wiki/entities/celldm-parameter.md) - celldm array

#### Concept Pages (5) / 概念页面

14. [scf-convergence.md](wiki/concepts/scf-convergence.md) - Self-consistent field convergence
15. [diagnostic-severity.md](wiki/concepts/diagnostic-severity.md) - Error levels and policy
16. [lsp-server-architecture.md](wiki/concepts/lsp-server-architecture.md) - Server design
17. [bravais-lattice.md](wiki/concepts/bravais-lattice.md) - 14 lattice types
18. [diagnostic-engine.md](wiki/concepts/diagnostic-engine.md) - Validation system

#### Synthesis Pages (6) / 综合页面

19. [control-namelist-reference.md](wiki/synthesis/control-namelist-reference.md) - CONTROL parameters
20. [system-namelist-reference.md](wiki/synthesis/system-namelist-reference.md) - SYSTEM parameters
21. [electrons-namelist-reference.md](wiki/synthesis/electrons-namelist-reference.md) - ELECTRONS parameters
22. [ions-namelist-reference.md](wiki/synthesis/ions-namelist-reference.md) - IONS parameters
23. [cell-namelist-reference.md](wiki/synthesis/cell-namelist-reference.md) - CELL parameters
24. [input-file-format.md](wiki/synthesis/input-file-format.md) - File structure guide
25. [quick-reference.md](wiki/synthesis/quick-reference.md) - Common parameters

#### Navigation (2) / 导航

26. [index.md](index.md) - Main navigation hub
27. [log.md](log.md) - This file

#### Source Evidence / 源证据

Copied to `raw/assets/`:
- README.md, CHANGELOG.md
- Documentation files (DIAGNOSTIC_ENGINE_V1.md, docs.md, etc.)
- Source extracts (constants.py, parser.py, validation.py)
- Test fixtures (silicon_scf.in, sio2_vc_relax.in, etc.)

### Wiki Statistics / 维基统计

- **Total wiki pages**: 27
- **Entity pages**: 13
- **Concept pages**: 5
- **Synthesis pages**: 6
- **Source evidence files**: 13
- **Languages**: Bilingual (Chinese/English)

### Coverage / 覆盖范围

- ✅ 5 namelists (CONTROL, SYSTEM, ELECTRONS, IONS, CELL)
- ✅ 4 cards (ATOMIC_SPECIES, ATOMIC_POSITIONS, K_POINTS, CELL_PARAMETERS)
- ✅ 15 ibrav values (all Bravais lattices)
- ✅ 8 calculation types
- ✅ 30+ parameters with documentation
- ✅ LSP server architecture
- ✅ Diagnostic engine specification
- ✅ Validation rules and examples

---

## Future Updates / 未来更新

Potential additions for future versions:

未来版本的潜在补充：

- Smearing parameters and methods
- Conjugate gradient diagonalization options
- Molecular dynamics specific parameters
- Phonon calculation details
- Band structure workflow
- DOS calculation workflow
- More validation rule examples
- Troubleshooting guide
- Performance optimization tips

---

## Template for New Entries / 新条目模板

```markdown
## YYYY-MM-DD

### Description / 描述

Brief description of changes.

更改的简要描述。

#### Added / 新增
- [page-name.md](wiki/path/page.md) - Description

#### Modified / 修改
- [page-name.md](wiki/path/page.md) - Changes made

#### Deleted / 删除
- [page-name.md](wiki/path/page.md) - Reason for deletion
```

# Change Log / 变更日志

This log tracks all changes to the QE-LSP LLM Wiki.

此日志跟踪 QE-LSP LLM 维基的所有更改。

## 2026-06-13 / 2026年6月13日

### Documentation Collection Expansion / 文档收集扩展

Expanded the wiki with comprehensive upstream Quantum ESPRESSO documentation collected from official sources.

从官方来源收集的上游 Quantum ESPRESSO 文档扩展了维基。

#### Raw Documentation (5 new files) / 原始文档（5 个新文件）

1. [qe-pw-input-reference.md](raw/assets/qe-pw-input-reference.md) - Complete pw.x input reference: all namelists, cards, parameters, calculation types, ibrav values
2. [qe-programs-reference.md](raw/assets/qe-programs-reference.md) - All QE program input formats: ph.x, cp.x, pp.x, dos.x, bands.x, projwfc.x, matdyn.x, q2r.x, etc.
3. [qe-examples.md](raw/assets/qe-examples.md) - Annotated example input files for SCF, NSCF, bands, relax, vc-relax, MD, phonon, spin-polarized, ibrav=0
4. [qe-output-format.md](raw/assets/qe-output-format.md) - QE output file format, stdout parsing markers, data files, post-processing output, unit conversions
5. [qe-pseudopotentials.md](raw/assets/qe-pseudopotentials.md) - PP types (NC/US/PAW), UPF format, PP libraries (SSSP, PSlibrary, GBRV, SG15, PseudoDojo), validation

#### Entity Pages (2 new) / 实体页面（2 个新增）

6. [ph-x-phonon.md](wiki/entities/ph-x-phonon.md) - ph.x phonon input format and workflow
7. [post-processing-programs.md](wiki/entities/post-processing-programs.md) - pp.x, dos.x, bands.x, projwfc.x, matdyn.x, q2r.x

#### Concept Pages (3 new) / 概念页面（3 个新增）

8. [qe-output-parsing.md](wiki/concepts/qe-output-parsing.md) - Output format, key markers, unit conversions, parsing libraries
9. [phonon-calculation.md](wiki/concepts/phonon-calculation.md) - DFPT phonon workflow: pw.x → ph.x → q2r.x → matdyn.x
10. [band-structure-dos-workflow.md](wiki/concepts/band-structure-dos-workflow.md) - Band structure and DOS workflows, high-symmetry points

#### Synthesis Pages (3 new) / 综合页面（3 个新增）

11. [programs-reference.md](wiki/synthesis/programs-reference.md) - All QE programs with categories and workflow diagrams
12. [pseudopotential-reference.md](wiki/synthesis/pseudopotential-reference.md) - PP types, libraries, naming conventions, validation
13. [examples-reference.md](wiki/synthesis/examples-reference.md) - Calculation type examples, parameter defaults

#### Updated / 更新

14. [index.md](index.md) - Added navigation for all new pages, expanded domain coverage
15. [log.md](log.md) - This update

### Wiki Statistics / 维基统计

- **Total wiki pages**: 36 (was 27)
- **Entity pages**: 15
- **Concept pages**: 8
- **Synthesis pages**: 9
- **Source evidence files**: 18
- **Languages**: Bilingual (Chinese/English)

### Sources / 来源

Documentation collected from:
- https://www.quantum-espresso.org/Doc/INPUT_PW.html
- https://www.quantum-espresso.org/Doc/INPUT_CP.html
- https://www.quantum-espresso.org/Doc/INPUT_PH.html
- https://www.quantum-espresso.org/Doc/INPUT_PP.html
- https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html
- https://www.quantum-espresso.org/documentation/input-data-description/
- https://www.quantum-espresso.org/pseudopotentials/
- https://pranabdas.github.io/espresso/hands-on/dos/
- https://blog.levilentz.com/parse-quantum-espresso-output-file/

---

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

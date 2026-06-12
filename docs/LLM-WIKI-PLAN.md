# LLM Wiki Plan for QE-LSP / QE-LSP LLM 维基计划

## Overview / 概述

This document outlines the LLM Wiki structure created for the QE-LSP project, following the Karpathy-style wiki pattern.

本文档概述了为 QE-LSP 项目创建的 LLM 维基结构，遵循 Karpathy 风格的维基模式。

## Wiki Structure / 维基结构

```
qe-lsp/
├── raw/
│   └── assets/              # Source evidence files
│       ├── README.md         # Project overview
│       ├── CHANGELOG.md      # Version history
│       ├── DIAGNOSTIC_ENGINE_V1.md  # Diagnostic contract
│       ├── docs.md           # Development guidelines
│       ├── *.py              # Source extracts
│       └── *.in              # QE input fixtures
│
├── wiki/
│   ├── entities/             # QE-specific domain entities
│   │   ├── quantum-espresso-namelist.md
│   │   ├── card.md
│   │   ├── ibrav-parameter.md
│   │   ├── ecutwfc-ecutrho.md
│   │   ├── calculation-type.md
│   │   ├── pseudopotential.md
│   │   ├── k-points.md
│   │   ├── mixing-beta.md
│   │   ├── parameter-assignment.md
│   │   ├── atomic-species-card.md
│   │   ├── atomic-positions-card.md
│   │   ├── cell-parameters-card.md
│   │   └── celldm-parameter.md
│   │
│   ├── concepts/             # Cross-cutting concepts
│   │   ├── scf-convergence.md
│   │   ├── diagnostic-severity.md
│   │   ├── lsp-server-architecture.md
│   │   ├── bravais-lattice.md
│   │   └── diagnostic-engine.md
│   │
│   └── synthesis/            # Reference materials
│       ├── control-namelist-reference.md
│       ├── system-namelist-reference.md
│       ├── electrons-namelist-reference.md
│       ├── ions-namelist-reference.md
│       ├── cell-namelist-reference.md
│       ├── input-file-format.md
│       └── quick-reference.md
│
├── index.md                  # Navigation hub
└── log.md                    # Change log
```

## Content Coverage / 内容覆盖

### Entities (13 pages) / 实体 (13 页)

QE-specific domain concepts:

QE 特定领域概念：

1. **Namelist** - Fortran-style input blocks
2. **Card** - Data sections (ATOMIC_SPECIES, etc.)
3. **ibrav** - Bravais lattice index (0-14)
4. **ecutwfc/ecutrho** - Energy cutoffs with ratio validation
5. **Calculation types** - scf, nscf, bands, relax, vc-relax, md, vc-md, ph
6. **Pseudopotential** - PAW, ultrasoft, NCPP with validation
7. **K-points** - Automatic, gamma, crystal options
8. **mixing_beta** - SCF mixing parameter with warnings
9. **Parameter assignment** - Syntax for name=value
10. **ATOMIC_SPECIES card** - Element declaration
11. **ATOMIC_POSITIONS card** - Coordinate specification
12. **CELL_PARAMETERS card** - Explicit cell vectors
13. **celldm** - Lattice parameter array

### Concepts (5 pages) / 概念 (5 页)

Cross-cutting ideas:

跨领域概念：

1. **SCF convergence** - Self-consistent field strategies
2. **Diagnostic severity** - Error, warning, information, hint
3. **LSP architecture** - Server, parser, validation, handlers
4. **Bravais lattice** - 14 crystal systems
5. **Diagnostic engine** - Validation categories and rules

### Synthesis (7 pages) / 综合 (7 页)

Reference materials:

参考资料：

1. **CONTROL reference** - All CONTROL parameters
2. **SYSTEM reference** - All SYSTEM parameters
3. **ELECTRONS reference** - All ELECTRONS parameters
4. **IONS reference** - All IONS parameters
5. **CELL reference** - All CELL parameters
6. **Input format** - File structure guide
7. **Quick reference** - Common parameters

## Source Evidence / 源证据

Files copied to `raw/assets/`:

复制到 `raw/assets/` 的文件：

### Documentation / 文档
- README.md - Project overview
- CHANGELOG.md - Version history
- DIAGNOSTIC_ENGINE_V1.md - Diagnostic contract
- docs.md - Development guidelines
- OPENQC_ALIGNMENT.md - Extension alignment
- pr-review-workflow.md - Review process
- agent-verification-loop.md - Agent workflow

### Source Code / 源代码
- constants.py - Keywords and documentation
- parser.py - Input parsing logic
- validation.py - Diagnostic rules

### Fixtures / 装置
- silicon_scf.in - Basic SCF example
- sio2_vc_relax.in - Variable-cell example
- aluminum_relax.in - Relaxation example
- fe_spin.in - Spin-polarized example
- silicon_bands.in - Band structure example

## Bilingual Format / 双语格式

All wiki pages use:
- Chinese headings (中文标题)
- English terms (英文术语)
- Bilingual descriptions (双语描述)

Example:
```markdown
# Namelist / 名称列表

## Definition / 定义
A namelist is... / 名称列表是...
```

## Navigation / 导航

The `index.md` file provides:
- Overview of wiki structure
- Quick navigation links
- Domain coverage summary
- Maintenance notes

## Change Tracking / 变更跟踪

The `log.md` file records:
- Creation date and initial content
- Statistics (page counts, coverage)
- Future update ideas
- Template for new entries

## QE Domain Coverage / QE 领域覆盖

The wiki covers:

维基涵盖：

- **5 namelists** - Complete coverage
- **4 cards** - Complete coverage
- **15 ibrav values** - All Bravais lattices
- **8 calculation types** - All major types
- **30+ parameters** - Key parameters with docs
- **LSP architecture** - Server design and features
- **Validation rules** - All diagnostic categories

## Next Steps / 下一步

1. ✅ Create directory structure
2. ✅ Copy source evidence
3. ✅ Create entity pages (13)
4. ✅ Create concept pages (5)
5. ✅ Create synthesis pages (7)
6. ✅ Create index.md and log.md
7. ✅ Git commit and PR
8. ✅ Closeout pass (issue #87): upstream manifest, example input, LSP provenance, wiki lint

## Closeout Status (issue #87)

- [x] Upstream QE documentation link manifest (`raw/assets/upstream-qe-reference.md`)
- [x] Official test-suite example input (`raw/assets/example-carbonyl-relax.in`)
- [x] Cross-references in `index.md` (OpenQC agent context, upstream manifest)
- [x] Lightweight wiki lint (`scripts/wiki-lint.sh`)
- [x] LSP source provenance in `lsp-capabilities.json` (expanded 1→6 entries)
- [x] OpenQC agent context grounding (`wiki/synthesis/openqc-agent-context.md`)

## Git Workflow / Git 工作流

```bash
git add raw/ wiki/ index.md log.md
git commit -m "feat: add LLM Wiki knowledge base (raw/ + wiki/ + index.md + log.md)"
git push
gh pr create --title "feat: add LLM Wiki knowledge base" \
              --body "Adds Karpathy-style LLM Wiki with raw/ + wiki/ structure for Quantum ESPRESSO domain knowledge"
gh pr merge --squash --auto
```

## Version / 版本

- **Created**: 2025-06-12
- **QE-LSP Version**: 0.1.0
- **Wiki Pages**: 27
- **Source Files**: 13

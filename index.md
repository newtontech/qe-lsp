# QE-LSP LLM Wiki / QE-LSP LLM 维基

## 概述 / Overview

This is a Karpathy-style LLM-maintained wiki for Quantum ESPRESSO LSP domain knowledge. The wiki synthesizes information from source code, documentation, and real-world QE input files into a structured knowledge base.

这是 Quantum ESPRESSO LSP 领域知识的 Karpathy 风格 LLM 维护的维基。该维基将来自源代码、文档和真实 QE 输入文件的信息综合成结构化知识库。

## Wiki Structure / 维基结构

```
raw/          # Source evidence files
└── assets/   # Copied docs, source extracts, fixtures

wiki/         # Synthesized knowledge
├── entities/ # QE-specific concepts (namelists, cards, parameters)
├── concepts/ # Cross-cutting ideas (diagnostics, architecture)
└── synthesis/ # Reference materials (API docs, guides)

index.md      # This file - navigation hub
log.md        # Change log
```

## Quick Navigation / 快速导航

### 核心概念 / Core Concepts

- [Namelist / 名称列表](wiki/entities/quantum-espresso-namelist.md) - Fortran-style input blocks
- [Card / 卡片](wiki/entities/card.md) - Data sections for structures
- [Calculation Type / 计算类型](wiki/entities/calculation-type.md) - SCF, relax, vc-relax, etc.

### 参数参考 / Parameter Reference

- [CONTROL Namelist](wiki/synthesis/control-namelist-reference.md)
- [SYSTEM Namelist](wiki/synthesis/system-namelist-reference.md)
- [ELECTRONS Namelist](wiki/synthesis/electrons-namelist-reference.md)
- [IONS Namelist](wiki/synthesis/ions-namelist-reference.md)
- [CELL Namelist](wiki/synthesis/cell-namelist-reference.md)

### 关键实体 / Key Entities

- [ibrav Parameter](wiki/entities/ibrav-parameter.md) - Bravais lattice index
- [ecutwfc & ecutrho](wiki/entities/ecutwfc-ecutrho.md) - Energy cutoffs
- [mixing_beta](wiki/entities/mixing-beta.md) - SCF mixing parameter
- [Pseudopotential](wiki/entities/pseudopotential.md) - Effective potentials

### 卡片详解 / Card Details

- [ATOMIC_SPECIES](wiki/entities/atomic-species-card.md) - Element and pseudo declaration
- [ATOMIC_POSITIONS](wiki/entities/atomic-positions-card.md) - Atomic coordinates
- [K_POINTS](wiki/entities/k-points.md) - Brillouin zone sampling
- [CELL_PARAMETERS](wiki/entities/cell-parameters-card.md) - Explicit cell vectors

### 架构与诊断 / Architecture & Diagnostics

- [LSP Server Architecture](wiki/concepts/lsp-server-architecture.md) - Server design
- [Diagnostic Engine](wiki/concepts/diagnostic-engine.md) - Validation system
- [Diagnostic Severity](wiki/concepts/diagnostic-severity.md) - Error levels

### 概念深化 / Concepts

- [SCF Convergence](wiki/concepts/scf-convergence.md) - Self-consistent field
- [Bravais Lattice](wiki/concepts/bravais-lattice.md) - Crystal structures
- [Parameter Assignment](wiki/entities/parameter-assignment.md) - Value syntax

### 综合参考 / Synthesis

- [Input File Format](wiki/synthesis/input-file-format.md) - File structure guide
- [Quick Reference](wiki/synthesis/quick-reference.md) - Common parameters

## Domain Coverage / 领域覆盖

This wiki covers:

此维基涵盖：

- **5 Namelists** - CONTROL, SYSTEM, ELECTRONS, IONS, CELL
- **4 Cards** - ATOMIC_SPECIES, ATOMIC_POSITIONS, K_POINTS, CELL_PARAMETERS
- **15+ ibrav values** - All Bravais lattices
- **8 Calculation types** - scf, nscf, bands, relax, md, vc-relax, vc-md, ph
- **30+ Parameters** - Key QE input parameters with validation rules
- **LSP Architecture** - Server design, diagnostic engine, agent CLI

## Maintenance / 维护

This wiki is designed to be maintained by LLM agents:

此维基设计为由 LLM 代理维护：

1. Source evidence in `raw/assets/` provides grounding
   `raw/assets/` 中的源证据提供基础
2. Wiki pages in `wiki/` synthesize knowledge
   `wiki/` 中的维基页面综合知识
3. `log.md` tracks all changes
   `log.md` 跟踪所有更改
4. Bilingual format (Chinese headings, English terms)
   双语格式（中文标题，英文术语）

## QE-LSP Project / QE-LSP 项目

- **Repository**: https://github.com/newtontech/qe-lsp
- **Purpose**: Language Server Protocol implementation for Quantum ESPRESSO
- **Language Server**: Quantum ESPRESSO input files (.in, .scf.in, etc.)
- **Features**: Auto-completion, diagnostics, hover documentation
- **Test Coverage**: 92%

## Version / 版本

- **Wiki Created**: 2025-06-12
- **QE-LSP Version**: 0.1.0
- **Source Commit**: Main branch

## See Also / 另见

- [QE-LSP README](raw/assets/README.md) - Project overview
- [QE-LSP Documentation](raw/assets/docs.md) - Development guidelines
- [Diagnostic Engine V1](raw/assets/DIAGNOSTIC_ENGINE_V1.md) - Diagnostic contract

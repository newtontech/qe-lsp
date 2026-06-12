# QE Output Parsing / QE 输出解析

## Source / 来源
- `raw/assets/qe-output-format.md` - Output format documentation

## Overview / 概述

Quantum ESPRESSO produces several types of output that can be parsed programmatically. Understanding the output format is essential for automated analysis, LSP features, and data extraction.

Quantum ESPRESSO 产生多种可编程解析的输出。理解输出格式对于自动化分析、LSP 功能和数据提取至关重要。

## Output Types / 输出类型

### 1. Standard Output (stdout) / 标准输出
Human-readable text produced by all QE programs. Key sections appear in a fixed order.

所有 QE 程序产生的可读文本。关键部分按固定顺序出现。

### 2. Data Files / 数据文件
Binary/XML files written to `outdir/prefix.save/`.

写入 `outdir/prefix.save/` 的二进制/XML 文件。

### 3. Post-Processing Files / 后处理文件
Plain-text files from dos.x, bands.x, projwfc.x, etc.

来自 dos.x、bands.x、projwfc.x 等的纯文本文件。

## Key Markers in stdout / 标准输出中的关键标记

### Energy / 能量
- `!    total energy` — Final converged energy (Ry). The `!` marks the final value.
- `total energy =` — Intermediate SCF energy (no `!`)
- `highest occupied, lowest unoccupied level (ev)` — Band gap info
- `the Fermi energy is` — Fermi level in eV

### Structure / 结构
- `lattice parameter (alat)` — In Bohr
- `unit-cell volume` — In Bohr^3
- `number of atoms/cell` — Integer
- `new unit-cell volume` — After vc-relax

### SCF / 自洽
- `convergence has been achieved` — Boolean
- `iteration #N` — SCF iteration step
- `rms` — Root mean square of change

### Forces & Stress / 力和应力
- `Forces acting on atoms (Ry/au)` — Block of nat lines
- `total   stress  (Ry/bohr**3)` — 3x3 tensor

### Final Coordinates / 最终坐标
- `Begin final coordinates` — Start block
- `CELL_PARAMETERS` — Optimized cell
- `ATOMIC_POSITIONS` — Optimized positions
- `End final coordinates` — End block

## Unit Conversions / 单位转换

| From | To | Factor |
|------|-----|--------|
| Bohr | Angstrom | 0.529177 |
| Ry | eV | 13.6057 |
| Ry/bohr | eV/Angstrom | 25.7112 |
| Ry/bohr^3 | kbar | 4107.87 |
| Bohr^3 | Angstrom^3 | 0.148185 |

## Data Files in outdir/prefix.save/ / 输出目录中的数据文件

| File | Description / 描述 |
|------|-------------------|
| `data-file.xml` | XML metadata (cell, atoms, k-points) |
| `charge-density.dat` | Self-consistent charge density |
| `evc.dat` / `wfc.dat` | Wavefunctions |
| `paw*.dat` | PAW-specific data |

## Parsing Libraries / 解析库

| Library | Language | URL |
|---------|----------|-----|
| ASE | Python | ase-lib.org |
| AiiDA | Python | aiida.net |
| NOMAD parser | Python | github.com/nomad-coe/nomad-parser-quantum-espresso |
| qe-tools | Python | github.com/aiidateam/qe-tools |

## LSP Relevance / LSP 相关性

For the QE-LSP project, output parsing informs:
- Diagnostic messages about convergence
- Hover documentation for output markers
- Code actions for common output issues

对于 QE-LSP 项目，输出解析有助于：
- 关于收敛的诊断消息
- 输出标记的悬停文档
- 常见输出问题的代码操作

## Related Concepts / 相关概念

- [SCF Convergence](scf-convergence.md)
- [Diagnostic Engine](diagnostic-engine.md)
- [Post-Processing Programs](../entities/post-processing-programs.md)

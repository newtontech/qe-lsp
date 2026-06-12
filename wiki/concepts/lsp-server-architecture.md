# LSP Server Architecture / LSP 服务器架构

## Source Sources / 来源
- `raw/assets/docs.md` - Architecture documentation
- `raw/assets/README.md` - Server overview

## Overview / 概述

QE-LSP implements the Language Server Protocol (LSP) to provide IDE features for Quantum ESPRESSO input files. The server is built with `pygls` and follows a provider-based architecture.

QE-LSP 实现语言服务器协议 (LSP) 为 Quantum ESPRESSO 输入文件提供 IDE 功能。服务器使用 `pygls` 构建，遵循基于提供者的架构。

## Core Components / 核心组件

### Server / 服务器

`server.py` - Main LSP server with feature registration

`server.py` - 具有功能注册的主 LSP 服务器

- Registers feature providers
- Handles LSP lifecycle
- Dispatches requests to providers

### Parser / 解析器

`parser.py` - Quantum ESPRESSO input parser

`parser.py` - Quantum ESPRESSO 输入解析器

- Parses namelists and cards
- Extracts parameter assignments
- Tracks duplicates and errors

### Validation / 验证

`validation.py` - Diagnostic checks for QE inputs

`validation.py` - QE 输入的诊断检查

- Syntax validation
- Schema validation
- Cross-field consistency checks

### Constants / 常量

`constants.py` - QE keywords and documentation

`constants.py` - QE 关键字和文档

- Keyword lists
- Hover documentation
- Parameter descriptions

### Handlers / 处理器

`handlers/` - LSP feature handlers

`handlers/` - LSP 功能处理器

- `completion.py` - Auto-completion
- `hover.py` - Hover documentation
- `diagnostic.py` - Diagnostics
- `code_action.py` - Code actions
- `definition.py` - Go to definition
- `references.py` - Find references
- `rename.py` - Symbol renaming

### Features / 功能

`features/` - Extended LSP features

`features/` - 扩展 LSP 功能

- `diagnostic.py` - Diagnostic provider
- `formatting.py` - Code formatting
- `typecheck.py` - Type checking
- `navigation.py` - Symbol navigation
- `code_actions.py` - Quick fixes
- `lint.py` - Linting
- `test_runner.py` - Test execution

## Parser Design / 解析器设计

The parser processes input files incrementally:

解析器增量处理输入文件：

1. Detect namelists (`&NAME` ... `/`)
   检测名称列表
2. Extract card sections
   提取卡片部分
3. Parse parameter assignments (`name = value`)
   解析参数赋值
4. Track duplicates and errors
   跟踪重复项和错误

## Validation Strategy / 验证策略

Validation checks are organized by severity:

验证检查按严重程度组织：

### Errors / 错误
- Syntax errors
- Unclosed namelists
- Missing required cards
- Duplicate parameters

### Warnings / 警告
- Invalid values
- Inconsistent parameters
- Pseudopotential issues
- Configuration problems

## Agent CLI / 代理 CLI

The server provides an agent-facing CLI for structured output:

服务器提供面向代理的 CLI 用于结构化输出：

```bash
qe-lsp-tool check path/to/input --format json
qe-lsp-tool context path/to/input --format json
qe-lsp-tool complete path/to/input --format json
qe-lsp-tool hover path/to/input --format json
qe-lsp-tool symbols path/to/input --format json
qe-lsp-tool fix path/to/input --format json
```

## Rich Diagnostic Shape / 富诊断形状

All agent-facing diagnostics include:

所有面向代理的诊断包括：

```json
{
  "code": "STABLE_CODE",
  "severity": "error",
  "category": "syntax",
  "confidence": 1.0,
  "source": "qe-lsp",
  "software": "qe",
  "file_type": "input",
  "blocking": true
}
```

## OpenQC Alignment / OpenQC 对齐

QE-LSP is designed to align with `newtontech/OpenQC-VSCode` extension:

QE-LSP 设计为与 `newtontech/OpenQC-VSCode` 扩展对齐：

- Same file extension handling
- Same diagnostic behavior
- Same completion vocabulary
- Consistent validation rules

## Related Entities / 相关实体

- [Diagnostic Severity](diagnostic-severity.md)
- [Diagnostic Engine](diagnostic-engine.md)
- [LSP Protocol](lsp-protocol.md)

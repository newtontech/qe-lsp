# Diagnostic Engine / 诊断引擎

## Source Sources / 来源
- `raw/assets/DIAGNOSTIC_ENGINE_V1.md` - Full engine documentation
- `raw/assets/validation.py` - Diagnostic implementation

## Purpose / 目的

The Diagnostic Engine provides structured, machine-readable diagnostics for Quantum ESPRESSO input files. It follows the shared newtontech Scientific LSP diagnostics contract.

诊断引擎为 Quantum ESPRESSO 输入文件提供结构化的、机器可读的诊断。它遵循共享的 newtontech 科学 LSP 诊断约定。

## Severity Policy / 严重程度策略

| Severity | Description | Chinese Description | Blocking |
|----------|-------------|-------------------|----------|
| `error` | High-confidence issue that upstream runtime will likely reject | 高置信度问题，上游运行时可能拒绝 | Yes |
| `warning` | High-risk or suspicious input that may be intentional | 高风险或可疑输入，可能是有意为之 | No |
| `information` | Style or documentation facts | 风格或文档事实 | No |
| `hint` | Optional optimization suggestions | 可选优化建议 | No |

## Categories / 类别

| Category | Description | Chinese Description |
|----------|-------------|-------------------|
| `syntax` | Syntax errors | 语法错误 |
| `schema` | Structural validation | 结构验证 |
| `type/value` | Invalid values | 无效值 |
| `cross-file reference` | File reference issues | 文件引用问题 |
| `semantic consistency` | Logical consistency | 逻辑一致性 |
| `preflight/runtime-risk` | Runtime warnings | 运行时警告 |
| `style/deprecation` | Style issues | 样式问题 |

## Rich Diagnostic Shape / 富诊断形状

Every agent-facing diagnostic must include:

每个面向代理的诊断必须包括：

```json
{
  "code": "STABLE_CODE",
  "severity": "error",
  "category": "syntax",
  "confidence": 1.0,
  "source": "qe-lsp",
  "range": {
    "start": {"line": 0, "character": 0},
    "end": {"line": 0, "character": 1}
  },
  "software": "qe",
  "file_type": "input",
  "path": "input",
  "expected": null,
  "actual": null,
  "manual_ref": null,
  "fix_hints": [],
  "blocking": true
}
```

## Diagnostic Types / 诊断类型

### Syntax Errors / 语法错误

- **Unclosed namelist**: Missing `/` at end
  未关闭的名称列表：末尾缺少 `/`
- **Duplicate parameters**: Same parameter assigned twice
  重复参数：同一参数赋值两次

### Schema Errors / 模式错误

- **Missing CELL_PARAMETERS**: Required when `ibrav=0`
  缺少 CELL_PARAMETERS：`ibrav=0` 时必需
- **Missing species in ATOMIC_POSITIONS**: Element not declared
  ATOMIC_POSITIONS 中缺少种类：未声明元素

### Type/Value Warnings / 类型/值警告

- **Ignored lattice parameters**: `a`, `b`, `c` ignored when `ibrav≠0`
  忽略的晶格参数：`ibrav≠0` 时忽略 `a`, `b`, `c`
- **Low cutoff ratio**: `ecutrho` too small relative to `ecutwfc`
  低截断比率：`ecutrho` 相对于 `ecutwfc` 太小
- **High mixing_beta**: May cause convergence issues
  高 mixing_beta：可能导致收敛问题

### Semantic Warnings / 语义警告

- **Pseudopotential mismatch**: Filename doesn't match element
  赝势不匹配：文件名与元素不匹配
- **Mixed functionals**: Different XC families in same calculation
  混合泛函：同一计算中使用不同 XC 族
- **Coarse k-point grid**: Grid dimensions < 3
  粗 k 点网格：网格维度 < 3

## Agent CLI / 代理 CLI

```bash
qe-lsp-tool check path/to/input --format json
qe-lsp-tool context path/to/input --format json
qe-lsp-tool complete path/to/input --format json
qe-lsp-tool hover path/to/input --format json
qe-lsp-tool symbols path/to/input --format json
qe-lsp-tool fix path/to/input --format json
```

## Provider Model / 提供者模型

The diagnostic engine uses a provider model inspired by python-lsp-server:

诊断引擎使用受 python-lsp-server 启发的提供者模型：

- **Editor-facing LSP**: Native LSP diagnostics for VS Code, etc.
  面向编辑器的 LSP：VS Code 等的原生 LSP 诊断
- **Agent-facing API**: Deterministic JSON for check/repair/recheck loops
  面向代理的 API：用于检查/修复/重新检查循环的确定性 JSON

## Related Entities / 相关实体

- [Diagnostic Severity](diagnostic-severity.md)
- [LSP Server Architecture](lsp-server-architecture.md)
- [Validation](validation.md)

# Diagnostic Severity / 诊断严重程度

## Source Sources / 来源
- `raw/assets/DIAGNOSTIC_ENGINE_V1.md` - Severity policy documentation
- `raw/assets/validation.py` - Diagnostic severity examples

## Definition / 定义

Diagnostic severity indicates how seriously an issue should be treated. QE-LSP follows the shared newtontech Scientific LSP diagnostics contract.

诊断严重程度指示问题应如何严肃对待。QE-LSP 遵循共享的 newtontech 科学 LSP 诊断约定。

## Severity Levels / 严重程度级别

| Severity | Description | Chinese Description | Blocking |
|----------|-------------|-------------------|----------|
| `error` | High-confidence issue that upstream runtime will likely reject | 高置信度问题，上游运行时可能拒绝 | Yes |
| `warning` | High-risk or suspicious input that may be intentional | 高风险或可疑输入，可能是有意为之 | No |
| `information` | Style or documentation facts | 风格或文档事实 | No |
| `hint` | Optional optimization suggestions | 可选优化建议 | No |

## Error Examples / 错误示例

### Unclosed Namelist / 未关闭的名称列表

```
&CONTROL
  calculation = 'scf'
  ! Missing closing /
```

**Severity**: Error
**Reason**: Invalid syntax that QE will reject

### Duplicate Parameter / 重复参数

```
&SYSTEM
  ibrav = 2
  ibrav = 0    ! Duplicate
/
```

**Severity**: Error
**Reason**: Ambiguous input

### Missing CELL_PARAMETERS / 缺少 CELL_PARAMETERS

When `ibrav = 0` without `CELL_PARAMETERS` card.

**Severity**: Error
**Reason**: Incomplete specification

## Warning Examples / 警告示例

### Ignored Lattice Parameters / 忽略的晶格参数

```
&SYSTEM
  ibrav = 2
  a = 5.43    ! Ignored when ibrav ≠ 0
/
```

**Severity**: Warning
**Reason**: Parameter has no effect but syntax is valid

### Low Cutoff Ratio / 低截断比率

```
&SYSTEM
  ecutwfc = 30.0
  ecutrho = 60.0    ! Should be 4x or 8x ecutwfc
/
```

**Severity**: Warning
**Reason**: May produce inaccurate results but won't crash

### High mixing_beta / 高 mixing_beta

```
&ELECTRONS
  mixing_beta = 0.9    ! May cause convergence issues
/
```

**Severity**: Warning
**Reason**: Risky but sometimes intentional

## Diagnostic Categories / 诊断类别

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

All agent-facing diagnostics include:

```json
{
  "code": "STABLE_CODE",
  "severity": "error",
  "category": "syntax",
  "confidence": 1.0,
  "source": "qe-lsp",
  "software": "qe",
  "blocking": true
}
```

## Related Entities / 相关实体

- [Validation](validation.md)
- [Diagnostic Engine](diagnostic-engine.md)
- [LSP Protocol](lsp-protocol.md)

# Quick Reference / 快速参考

## Source Sources / 来源
- `raw/assets/README.md` - Feature overview
- `raw/assets/constants.py` - All keywords and docs

## Installation / 安装

```bash
pip install qe-lsp
```

## Start Server / 启动服务器

```bash
qe-lsp
```

## Supported File Extensions / 支持的文件扩展名

| Extension | Description | Chinese Description |
|-----------|-------------|-------------------|
| `.in` | Generic QE input | 通用 QE 输入 |
| `.pw.in` | PWscf input | PWscf 输入 |
| `.scf.in` | SCF calculation | SCF 计算 |
| `.nscf.in` | Non-SCF calculation | 非 SCF 计算 |
| `.relax.in` | Ionic relaxation | 离子弛豫 |
| `.vc-relax.in` | Variable-cell relaxation | 变晶胞弛豫 |
| `.bands.in` | Band structure | 能带结构 |
| `.ph.in` | Phonon calculation | 声子计算 |
| `.dos.in` | Density of states | 态密度 |

## Namelists / 名称列表

| Namelist | Purpose | Required For |
|----------|---------|-------------|
| `&CONTROL` | Execution control | All calculations |
| `&SYSTEM` | System definition | All calculations |
| `&ELECTRONS` | Electronic structure | All calculations |
| `&IONS` | Ionic dynamics | relax, md, vc-relax, vc-md |
| `&CELL` | Cell dynamics | vc-relax, vc-md |

## Cards / 卡片

| Card | Purpose | Required When |
|------|---------|--------------|
| `ATOMIC_SPECIES` | Element and pseudopotential | Always |
| `ATOMIC_POSITIONS` | Atomic coordinates | Always |
| `K_POINTS` | k-point mesh | Always |
| `CELL_PARAMETERS` | Cell vectors | `ibrav=0` |

## Calculation Types / 计算类型

| Type | Description | Required Namelists |
|------|-------------|------------------|
| `scf` | Self-consistent field | CONTROL, SYSTEM, ELECTRONS |
| `nscf` | Non-self-consistent | CONTROL, SYSTEM, ELECTRONS |
| `bands` | Band structure | CONTROL, SYSTEM, ELECTRONS |
| `relax` | Ionic relaxation | CONTROL, SYSTEM, ELECTRONS, IONS |
| `vc-relax` | Variable-cell | All namelists |
| `md` | Molecular dynamics | CONTROL, SYSTEM, ELECTRONS, IONS |

## Common Parameters / 常用参数

### CONTROL / 控制

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| `calculation` | Calculation type | `'scf'`, `'relax'` |
| `pseudo_dir` | Pseudo directory | `'./pseudo/'` |
| `outdir` | Output directory | `'./tmp/'` |

### SYSTEM / 系统

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| `ibrav` | Bravais lattice | 0, 1-14 |
| `ecutwfc` | Cutoff (Ry) | 20-100 |
| `ecutrho` | Density cutoff | 4× or 8× ecutwfc |
| `nat` | Number of atoms | Integer |
| `ntyp` | Number of types | Integer |

### ELECTRONS / 电子

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| `conv_thr` | Convergence | 1.0d-8 |
| `mixing_beta` | Mixing factor | 0.7 |
| `electron_maxstep` | Max iterations | 100 |

## Minimal SCF Input / 最小 SCF 输入

```
&CONTROL
  calculation = 'scf'
/

&SYSTEM
  ibrav = 2
  celldm(1) = 10.0
  nat = 1
  ntyp = 1
  ecutwfc = 30.0
/

&ELECTRONS
/

ATOMIC_SPECIES
H 1.008 H.pbe-n-rrkjus.UPF

ATOMIC_POSITIONS {crystal}
H 0.0 0.0 0.0

K_POINTS {gamma}
```

## Agent CLI / 代理 CLI

```bash
# Check diagnostics
qe-lsp-tool check input.in --format json

# Get completion
qe-lsp-tool complete input.in --format json

# Get hover docs
qe-lsp-tool hover input.in --format json

# Get symbols
qe-lsp-tool symbols input.in --format json
```

## Related Entities / 相关实体

- [Input File Format](input-file-format.md)
- [Calculation Type](calculation-type.md)
- [LSP Server Architecture](lsp-server-architecture.md)

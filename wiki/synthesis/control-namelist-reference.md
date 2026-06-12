# CONTROL Namelist Reference / CONTROL 名称列表参考

## Source Sources / 来源
- `raw/assets/constants.py` - `QE_PARAM_DOCS["&CONTROL"]`

## Purpose / 目的

Controls the execution of Quantum ESPRESSO programs, including calculation type, convergence criteria, and I/O settings.

控制 Quantum ESPRESSO 程序的执行，包括计算类型、收敛标准和 I/O 设置。

## Parameters / 参数

### Core Calculation Parameters / 核心计算参数

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `calculation` | string | Calculation type | 计算类型 |
| `restart_mode` | string | Restart behavior | 重启行为 |
| `title` | string | Job title | 作业标题 |
| `prefix` | string | File prefix | 文件前缀 |

### I/O Parameters / I/O 参数

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `outdir` | string | Output directory | 输出目录 |
| `pseudo_dir` | string | Pseudopotential directory | 赝势目录 |
| `wf_collect` | logical | Collect wavefunctions | 收集波函数 |
| `disk_io` | string | Disk I/O level | 磁盘 I/O 级别 |

### Molecular Dynamics Parameters / 分子动力学参数

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `dt` | real | Time step (Ry a.u.) | 时间步长 |
| `nstep` | integer | Number of ionic steps | 离子步数 |
| `iprint` | integer | Print interval | 打印间隔 |
| `isave` | integer | Save interval | 保存间隔 |

### Force/Stress Parameters / 力/应力参数

| Parameter | Type | Description | Chinese Description |
|-----------|------|-------------|-------------------|
| `tprnfor` | logical | Calculate forces | 计算力 |
| `tstress` | logical | Calculate stress | 计算应力 |

## Parameter Details / 参数详情

### calculation / 计算类型

Values: `'scf'`, `'nscf'`, `'bands'`, `'relax'`, `'md'`, `'vc-relax'`, `'vc-md'`, `'ph'`

Default: `'scf'`

### restart_mode / 重启模式

Values: `'from_scratch'`, `'restart'`

Default: `'from_scratch'`

### outdir / 输出目录

Directory for temporary files (wavefunction, charge density, etc.)

临时文件目录（波函数、电荷密度等）

Example: `outdir = './tmp/'`

### pseudo_dir / 赝势目录

Directory containing pseudopotential `.UPF` files.

包含赝势 `.UPF` 文件的目录。

Example: `pseudo_dir = './pseudo/'`

### wf_collect / 收集波函数

When `true`, collects wavefunctions at end of run.

设置为 `true` 时，在运行结束时收集波函数。

Default: `.false.`

### dt / 时间步长

Time step for molecular dynamics in Rydberg atomic units.

里德堡原子单位中的分子动力学时间步长。

Typical: 1-20 Ry a.u.

### nstep / 离子步数

Number of ionic steps for `relax` and `md` calculations.

`relax` 和 `md` 计算的离子步数。

Default: 1 for `scf`, 50 for `relax`/`md`

## Example / 示例

```
&CONTROL
  calculation = 'scf'
  restart_mode = 'from_scratch'
  pseudo_dir = './pseudo/'
  outdir = './tmp/'
  title = 'Silicon SCF calculation'
  prefix = 'si'
/
```

## Related Entities / 相关实体

- [Calculation Type](calculation-type.md)
- [SYSTEM Namelist](system-namelist-reference.md)
- [ELECTRONS Namelist](electrons-namelist-reference.md)

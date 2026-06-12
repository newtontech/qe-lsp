# Calculation Type / 计算类型

## Source Sources / 来源
- `raw/assets/constants.py` - CONTROL namelist documentation
- `raw/assets/silicon_scf.in` - SCF example
- `raw/assets/sio2_vc_relax.in` - vc-relax example

## Definition / 定义

The `calculation` parameter in the `&CONTROL` namelist specifies the type of Quantum ESPRESSO calculation to perform. It determines which namelists are required and what physics is computed.

`&CONTROL` 名称列表中的 `calculation` 参数指定要执行的 Quantum ESPRESSO 计算类型。它决定了需要哪些名称列表以及计算哪些物理量。

## Supported Calculation Types / 支持的计算类型

| Type | Description | Required Namelists | Chinese Description |
|------|-------------|------------------|-------------------|
| `scf` | Self-consistent field | CONTROL, SYSTEM, ELECTRONS | 自洽场 |
| `nscf` | Non-self-consistent field | CONTROL, SYSTEM, ELECTRONS | 非自洽场 |
| `bands` | Band structure | CONTROL, SYSTEM, ELECTRONS | 能带结构 |
| `relax` | Ionic relaxation | CONTROL, SYSTEM, ELECTRONS, IONS | 离子弛豫 |
| `vc-relax` | Variable-cell relaxation | CONTROL, SYSTEM, ELECTRONS, IONS, CELL | 变晶胞弛豫 |
| `md` | Molecular dynamics | CONTROL, SYSTEM, ELECTRONS, IONS | 分子动力学 |
| `vc-md` | Variable-cell MD | CONTROL, SYSTEM, ELECTRONS, IONS, CELL | 变晶胞分子动力学 |
| `ph` | Phonon calculation | CONTROL, SYSTEM, ELECTRONS | 声子计算 |

## SCF Calculation / 自洽场计算

The most common calculation type. Solves Kohn-Sham equations self-consistently.

最常见的计算类型。自洽求解 Kohn-Sham 方程。

**Example**:
```
&CONTROL
  calculation = 'scf'
  restart_mode = 'from_scratch'
/
```

**Typical use**: Ground-state energy, forces, stress

## NSCF Calculation / 非自洽场计算

Computes band structure, DOS, or other properties using a fixed potential from a previous SCF.

使用之前 SCF 的固定势计算能带结构、DOS 或其他性质。

**Typical use**: Band structures, DOS plotting

## Relax Calculation / 弛豫计算

Optimizes atomic positions to find local energy minimum.

优化原子位置以找到局部能量极小值。

**Required namelists**: `&IONS`

**Typical use**: Geometry optimization, finding equilibrium structure

## VC-Relax Calculation / 变晶胞弛豫

Optimizes both atomic positions and cell parameters simultaneously.

同时优化原子位置和晶胞参数。

**Required namelists**: `&IONS`, `&CELL`

**Typical use**: Equilibrium crystal structure under pressure

## MD Calculation / 分子动力学

Simulates ionic motion using forces computed at each timestep.

使用每个时间步计算的力模拟离子运动。

**Required namelists**: `&IONS`

**Key parameters**: `dt` (timestep), `nstep` (number of steps)

## File Extensions / 文件扩展名

Common practice uses file extensions to indicate calculation type:
- `.scf.in` - SCF calculation
- `.relax.in` - Relaxation calculation
- `.vc-relax.in` - Variable-cell relaxation
- `.bands.in` - Band structure calculation
- `.nscf.in` - Non-SCF calculation
- `.ph.in` - Phonon calculation
- `.dos.in` - Density of states

## Related Entities / 相关实体

- [CONTROL Namelist](control-namelist.md)
- [IONS Namelist](ions-namelist.md)
- [CELL Namelist](cell-namelist.md)
- [ELECTRONS Namelist](electrons-namelist.md)

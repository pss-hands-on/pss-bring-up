# Lab 1: Core structure

```{button-link} slides/index.html
:color: primary
:outline:

Slides for this lab
```

You will describe a small operation model in PSS, generate it in four flavors
with `pssc`, and drive it from three environments (C, SystemVerilog and
Python), and see that all three program the device identically.

:::{card} Objectives
- Describe an operation model in PSS: a **component tree** holding **state**,
  an **initialization** function, and **operations**, **exports** and
  **imports**
- Generate it with `pssc` for SystemVerilog, C, C++ and Python
- Integrate it into a C, a SystemVerilog and a Python environment
- Add an operation and change a signature, and follow the change through every
  generated flavor
:::

**Before you start:** complete the {site}`setup <setup.html>` once, so that
`pssc`, `verilator` and `python3` are on your `PATH`.

**Time:** about 45 minutes.

## The device

A block with two timer channels at a `0x100` stride. Each channel has three
registers:

| Offset | Register | Fields |
|---|---|---|
| `0x0` | CTRL | bit 0 `EN`, bit 1 `IRQ_EN` |
| `0x4` | LOAD | reload value |
| `0x8` | STATUS | bit 0 `DONE` (write 1 to clear) |

![The timer block and its operation model](../../diagrams/lab1_model.svg)

In this lab the model uses raw register offsets. Lab 2 replaces them with a
register model generated from SystemRDL.

```{toctree}
:maxdepth: 2

walkthrough
exercises
reference
```

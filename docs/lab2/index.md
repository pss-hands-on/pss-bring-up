# Lab 2: Registers and memory

```{button-link} slides/index.html
:color: primary
:outline:

Slides for this lab
```

Lab 1 wrote `write32(make_handle_from_handle(base, 0x8), 1)`: an offset and a
bit position typed by hand. In this lab the register map comes from its
SystemRDL description, as a PSS register model, and the operation model's
programming sequences are written against it.

:::{card} Objectives
- Generate a PSS register package from SystemRDL with `peakrdl pss`
- Bind a register model to addresses at initialization
- Write programming sequences with whole-register writes, field writes
  (read-modify-write) and write-1-to-clear registers
- Change the register spec, and follow the change into every generated flavor
  without editing any PSS
:::

**Before you start:** finish {site}`Lab 1 <lab1/index.html>`. The tools are the
same, plus `peakrdl` with the peakrdl-pss plugin, which {site}`setup
<setup.html>` already installed.

**Time:** about 45 minutes.

## Why a register model?

With raw offsets:

- **Offsets** are restated by hand, and a wrong one fails silently.
- **Field positions and masks** are restated by hand.
- **Access rules** (read-only, write-1-to-clear) are invisible.
- Every consumer (RTL, UVM RAL, firmware headers) has its own copy.

PSS 3.x has a **register model** in `addr_reg_pkg`. Generate it from the same
source as everything else.

## The device

The same two-channel timer as Lab 1, now with a block ID register and a
COUNT register per channel, described in `rdl/timer.rdl`. The full register
map is on the {doc}`registers` page.

```{toctree}
:maxdepth: 2

registers
walkthrough
exercises
reference
```

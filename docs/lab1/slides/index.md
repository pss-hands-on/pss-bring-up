---
revealjs_slide:
  data-transition: none
---

# Lab 1: Core structure

:::{revealjs-section}
:data-background-color: "#1a365d"
:::

`labs/lab1`

# Lab 1 goals

- Describe an operation model in PSS:
  - a **component tree** holding **state**
  - an **initialization** function
  - **operations**, **exports** and **imports**
- Generate it with `pssc` in four flavors
- Integrate it into three environments: **C**, **SystemVerilog**, **Python**
- See that all three drive the device **identically**

# The device and the model

![](../../../diagrams/lab1_model.svg)

Two timer channels, raw register offsets for now (Lab 2 fixes that).

# PSS: imports (`pss/plat_pkg.pss`)

```{literalinclude} ../../../labs/lab1/pss/plat_pkg.pss
:language: pss
```

- `import target function` declares a **platform service**. The model only names it.
- Memory access (`read32`/`write32`) is an implicit import, from `addr_reg_pkg`.
- Each generator turns imports into the language's *"you implement this"* form:
  a method on `soc_c_imp_if` (SV), an `extern` prototype (C), a method on a `Protocol` (Py)

# PSS: a leaf component (`pss/timer_c.pss`)

:::{revealjs-section}
:data-state: small
:::

```{literalinclude} ../../../labs/lab1/pss/timer_c.pss
:language: pss
:start-at: component timer_c
```

# PSS: the root (`pss/soc_c.pss`)

```{literalinclude} ../../../labs/lab1/pss/soc_c.pss
:language: pss
:start-at: component soc_c
```

- The **root** is chosen on the command line (`--root soc_c`)
- **Exports** select the root functions the environment can call. Sub-component
  functions remain reachable in C/C++/Py.

# Generating output

![](../../../diagrams/pssc_flow.svg)

```console
$ pssc compile pss/plat_pkg.pss pss/timer_c.pss pss/soc_c.pss \
       -t op-model-c --root soc_c -o gen/c \
       --link-style direct --mem-access functions --lifecycle static
```

# Available output flavors

| `-t` | Output | Useful options |
|---|---|---|
| `op-model-sv` | package with `*_imp_if`, `*_ctxt_if`, `*_root` | `--package NAME` |
| `op-model-c` | `<prefix>.h/.c`, private `<prefix>_regs.h` | `--prefix`, `--link-style`, `--mem-access`, `--lifecycle static`, `--addr-bits 32`, `--yield import` |
| `op-model-cpp` | `<ns>.hpp`, header-only | `--namespace`, `--dispatch {virtual,template}` |
| `op-model-py` | `<module>.py` + `pssc_rt.py` | `--py-await {sync,async}` |
| *(all)* | | `--emit-manifest FILE` (JSON: ops, signatures, register offsets), `--no-comments` |

`pssc targets` lists them all. Each target also tells the model what it can do
via `target_cfg_pkg` (e.g. `HAVE_EVENT_WAIT`).

# PSS → SystemVerilog

::::{grid} 2
:::{grid-item}
```{literalinclude} ../../../labs/lab1/pss/timer_c.pss
:language: pss
:start-at: target function bool is_done()
:lines: 1-11
:dedent: 4
```
:::
:::{grid-item}
```{literalinclude} ../../../labs/lab1/gen/sv/timer_c.svh
:language: systemverilog
:start-at: virtual task is_done
:end-before: endclass
:dedent: 4
```
:::
::::

Return values become an `output` **first argument**, since operations are
tasks. Address arithmetic is folded: `base + 8`.

# PSS → C and Python

::::{grid} 2
:::{grid-item}
```{literalinclude} ../../../labs/lab1/gen/c/soc.c
:language: c
:start-at: uint8_t timer_is_done
:end-before: /* --- soc_c --- */
```
:::
:::{grid-item}
```{literalinclude} ../../../labs/lab1/gen/py/soc.py
:language: python
:start-at: class Timer
:end-before: class Soc
```
:::
::::

Comments in the PSS source are carried into every output (`--no-comments` to
drop them).

# What happens at run time

![](../../../diagrams/lab1_sequence.svg)

# Environment integration

::::{grid} 2
:::{grid-item}
**SystemVerilog** (`env/sv/tb.sv`)
- class `implements soc_c_imp_if`
- `soc_c_root#(T)::create(imp, base)`
- `write32`/`read32` may consume time

**C** (`env/c/main.c`)
- define `pssc_mem_read32/write32`
- define `plat_delay_us`
- `static soc_c soc; soc_init(&soc, base);`
:::
:::{grid-item}
**Python** (`env/py/run.py`)
- any object with `read32`, `write32`, `plat_delay_us` (a `Protocol`, so no
  inheritance needed)
- `Soc(env, base)`

**All three** use a ~40-line *fake timer* behind the import API, so the lab
runs on a laptop.
:::
::::

# Lab 1: run it

```console
$ cd labs/lab1
$ make run          # gen + run C, SV (Verilator), Python
```

```{literalinclude} ../../_build/generated/lab1/run-py.txt
:language: text
```

**Same output from all three environments.** Same model, same bus traffic.

# Lab 1 exercises

1. **Observe.** `make gen`, then find each PSS element in `gen/sv`, `gen/c`,
   `gen/cpp`, `gen/py`: state, `initialize`, `delay_ticks`, `plat_delay_us`,
   `tmr[2]`
2. **Add an operation.** Give `timer_c` a `stop()` (EN=0, clear DONE); add and
   export `soc_c::cancel(int t)`. Regenerate: where did `cancel` appear in each
   flavor?
3. **Change a signature.** Give `wait_done` a `max_polls` budget and make it
   return `bool`; make `delay_ticks` return it. Update the three harnesses to
   report a timeout and call `cancel()`

Step-by-step instructions are in the guide. Solution: `labs/lab1/solution`,
run with `make run SOL=1`.

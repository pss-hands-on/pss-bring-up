---
revealjs_slide:
  data-transition: none
---

# Lab 2: Registers and memory

:::{revealjs-section}
:data-background-color: "#1a365d"
:::

`labs/lab2`

# Why a register model?

Lab 1 wrote `write32(make_handle_from_handle(base, 0x8), 1)`.

- **Offsets** are restated by hand, and wrong ones fail silently
- **Field positions and masks** are restated by hand
- **Access rules** (read-only, W1C) are invisible
- Every consumer (RTL, UVM RAL, firmware headers) has its own copy

PSS 3.x has a **register model** in `addr_reg_pkg`. Generate it from the same
source as everything else.

# Creating register models

![](../../../diagrams/reg_flow.svg)

```console
$ peakrdl pss rdl/timer.rdl --pad-tail -o pss/timer_regs_pkg.pss
```

# The register spec (`rdl/timer.rdl`)

:::{revealjs-section}
:data-state: small
:::

```{literalinclude} ../../../labs/lab2/rdl/timer.rdl
:language: systemrdl
```

# PSS register-model anatomy

![](../../../diagrams/reg_anatomy.svg)

# Generated register package (excerpt)

:::{revealjs-section}
:data-state: small
:::

```{literalinclude} ../../../labs/lab2/pss/timer_regs_pkg.pss
:language: pss
:start-at: struct timer_ch_regs__status_s
:end-before: struct timer_ch_regs__count_s
:dedent: 4
```

```{literalinclude} ../../../labs/lab2/pss/timer_regs_pkg.pss
:language: pss
:start-at: pure component timer_ch_regs_c
:end-before: pure component timer_regs_c
:dedent: 4
```

`onwrite = woclr` has no PSS equivalent: peakrdl-pss warns (`PSS-W101`) and
keeps it as a comment.

# Register and memory access functions

| Call | On | Bus effect |
|---|---|---|
| `read()` / `write(v)` | `reg_c<R>` | one access; value is the packed struct `R` |
| `read_val()` / `write_val(raw)` | `reg_c<R>` | one access; raw `bit[N]` |
| `write_field("en", 1)` | `reg_c<R>` | **read-modify-write** of one field |
| `write_masked(mask, v)` | `reg_c<R>` | **read-modify-write** |
| `set_handle(h)` | `reg_group_c` | none: binds the bank to an address (init only) |
| `get_offset_of_instance[_array]` | `reg_group_c` | none: folded to a constant by pssc |
| `read32(h)` / `write32(h, v)`, `8/16/64` | `addr_handle_t` | raw memory access (Lab 1) |
| `make_handle_from_handle(h, off)` | `addr_handle_t` | none: address arithmetic |

The field name in `write_field` is **resolved at compile time**, so a typo is
an error rather than a wrong bit.

# Binding registers to addresses

![](../../../diagrams/address_binding.svg)

# The programming sequence (`pss/timer_ch_c.pss`)

:::{revealjs-section}
:data-state: small
:::

```{literalinclude} ../../../labs/lab2/pss/timer_ch_c.pss
:language: pss
:start-at: // Program the channel.
:end-before: // Stop the count.
:dedent: 4
```

# The step table, generated

`/// Step:` comments in the PSS → sphinx-pss generates the programming-guide
table:

```{eval-rst}
.. pss:steps:: timer_c::one_shot
   :numbering: outline
```

# Register-operation details

![](../../../diagrams/rmw.svg)

# Register-operation pitfalls

- **Field writes read first.** `write_field`/`write_masked` are a
  read-modify-write (PSS 3.1 §21.14.1). On a register with clear-on-read bits,
  that read **is** a side effect.
- **W1C registers.** Write the clear value with `write_val`. Don't RMW a W1C
  register, or you'll clear bits you didn't mean to.
- **Whole vs. field writes.** Build a struct and `write()` once when
  configuring. Use `write_field()` to flip one bit of live state.
- **Reserved bits.** Use `--pad-tail` so every struct spans the full register
  width. Otherwise C gets a `uint8_t raw` for a 32-bit register.
- **Device-specific semantics** (W1C, RC, sticky) aren't in the PSS type.
  Document them in the operation, where the next reader will look.

# What it generates

::::{grid} 2
:::{grid-item}
```{literalinclude} ../../../labs/lab2/gen/sv/timer_ch_c.svh
:language: systemverilog
:start-at: virtual task start();
:end-before: /** Stop the count. */
:dedent: 4
```
:::
:::{grid-item}
```{literalinclude} ../../../labs/lab2/gen/c/timer.c
:language: c
:start-at: void timer_ch_start
:end-before: /* Stop the count. */
```
:::
::::

# Lab 2: run it

```console
$ cd labs/lab2
$ make regs        # SystemRDL -> pss/timer_regs_pkg.pss (checked in)
$ make run
```

![](../../../diagrams/lab2_trace.svg)

# Lab 2 exercises

1. **Change the register spec.** Add an `ovf` bit to `STATUS` in
   `rdl/timer.rdl` (bit 2, W1C: "expired again while DONE was set").
   `make regs gen` and find `ovf` in every flavor. You edited no PSS.
2. **Write a programming sequence.** Add `timer_ch_c::ack()` (read STATUS,
   clear DONE|OVF, return `ovf`) and `timer_c::periodic(int c, bit[32] ticks,
   int n)` → number of missed expiries. Export it.
3. **Explain the trace.** Run `periodic(1, 20, 3)` and `periodic(1, 4, 2)`.
   Why does the second miss expiries? Which bus accesses come from
   `write_field`?

Step-by-step instructions are in the guide. Solution: `labs/lab2/solution`,
run with `make run SOL=1`.

# Wrap-up

- An **operation model** is PSS's device knowledge, separated from scenarios
- **Four parts:** export API, import API, initialization, state
- **`pssc`** turns one model into SV, C, C++ and Python, each idiomatic for
  its users
- **Register models** come from the register spec (SystemRDL → `peakrdl
  pss`), not from hand-typed offsets
- Payoff today: **every team runs the same programming sequence**. Payoff
  later: PSS tests reuse the same functions.

# The register model

The register map has one source: `rdl/timer.rdl`. This page renders it with
sphinx-peakrdl, then follows it through `peakrdl pss` into the PSS register
package the operation model uses.

## The SystemRDL source

```{literalinclude} ../../labs/lab2/rdl/timer.rdl
:language: systemrdl
:caption: rdl/timer.rdl
```

- The block is an `addrmap` with an ID register and two channels.
- Each channel is a `regfile` instance, `ch[2]`, at `0x100` with a `0x100`
  stride. The model never states these offsets again.
- `STATUS.DONE` is `onwrite = woclr`: write 1 to clear.

## The register map

Rendered from the RDL above. Browse the same map interactively in the
{rdl:html-ref}`register browser <timer_regs>`.

```{eval-rst}
.. rdl:docnode:: timer_regs
   :no-wrap-section:
```

### One channel

```{eval-rst}
.. rdl:doctree:: timer_regs.ch[0]
```

## From SystemRDL to PSS

![SystemRDL → peakrdl pss → PSS register package → pssc](../../diagrams/reg_flow.svg)

```console
$ make regs
peakrdl pss rdl/timer.rdl --pad-tail -o pss/timer_regs_pkg.pss
```

The generated `pss/timer_regs_pkg.pss` is checked in, so you can skip this
step until Exercise 1. `--pad-tail` adds a reserved field to every register
narrower than 32 bits, so every struct spans the full register width.

### The generated package

![Anatomy of a PSS register model](../../diagrams/reg_anatomy.svg)

For each register, the package has a **packed struct** of its fields and a
**register component** (`reg_c<struct, access, width>`). For each `regfile`
or `addrmap`, it has a **register group** (`reg_group_c`) that holds the
registers and knows their offsets. Here is the channel's STATUS register and
the group:

```{literalinclude} ../../labs/lab2/pss/timer_regs_pkg.pss
:language: pss
:caption: pss/timer_regs_pkg.pss (excerpt)
:start-at: struct timer_ch_regs__status_s
:end-before: struct timer_ch_regs__count_s
:dedent: 4
```

```{literalinclude} ../../labs/lab2/pss/timer_regs_pkg.pss
:language: pss
:start-at: pure component timer_ch_regs_c
:end-before: pure component timer_regs_c
:dedent: 4
```

`onwrite = woclr` has no PSS equivalent: peakrdl-pss warns (`PSS-W101`) and
keeps it as a comment. The {doc}`reference` page has the whole package,
documented by sphinx-pss.

## Register and memory access functions

| Call | On | Bus effect |
|---|---|---|
| `read()` / `write(v)` | `reg_c<R>` | one access; the value is the packed struct `R` |
| `read_val()` / `write_val(raw)` | `reg_c<R>` | one access; a raw `bit[N]` |
| `write_field("en", 1)` | `reg_c<R>` | **read-modify-write** of one field |
| `write_masked(mask, v)` | `reg_c<R>` | **read-modify-write** |
| `set_handle(h)` | `reg_group_c` | none: binds the bank to an address (initialization only) |
| `get_offset_of_instance[_array]` | `reg_group_c` | none: folded to a constant by pssc |
| `read32(h)` / `write32(h, v)`, and 8/16/64 | `addr_handle_t` | raw memory access (Lab 1) |
| `make_handle_from_handle(h, off)` | `addr_handle_t` | none: address arithmetic |

The field name in `write_field` is **resolved at compile time**, so a typo is
an error rather than a wrong bit.

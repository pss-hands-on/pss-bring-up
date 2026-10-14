# Walkthrough

Work through these steps in order. All paths are relative to `labs/lab2`.

## Step 1: Look around

```console
$ cd labs/lab2
$ make help
```

Compared with Lab 1, there is one new target, `make regs`, and two new
directories: `rdl/`, the register spec, and the generated
`pss/timer_regs_pkg.pss`. Read {doc}`registers` first if you have not.

## Step 2: Bind the register model to addresses

![Binding register groups to addresses at initialization](../../diagrams/address_binding.svg)

The root holds the block's register group and one operation component per
channel:

```{literalinclude} ../../labs/lab2/pss/timer_c.pss
:language: pss
:caption: pss/timer_c.pss
:start-at: component timer_c
:end-before: // Is the expected block at this address?
```

- `regs.set_handle(base)` binds the whole register file to the block's base
  address. It generates no bus access.
- `get_offset_of_instance_array("ch", i)` is the channel's offset **from the
  RDL**: `0x100 + i*0x100`. pssc folds it to a constant, so nothing is looked
  up at run time, and nothing is restated by hand.

Each channel binds its own bank:

```{literalinclude} ../../labs/lab2/pss/timer_ch_c.pss
:language: pss
:caption: pss/timer_ch_c.pss
:start-at: component timer_ch_c
:end-before: // Program the channel.
```

## Step 3: Read the programming sequences

A *programming sequence* is the ordered set of register accesses that makes
the device do one thing. The two that program the channel:

```{literalinclude} ../../labs/lab2/pss/timer_ch_c.pss
:language: pss
:start-at: // Program the channel.
:end-before: // Stop the count.
:dedent: 4
```

The `/// Step:` comments mark the steps of each sequence. sphinx-pss reads
them and generates the step table, the way a vendor programming guide lists a
procedure, so the guide and the code can't drift apart:

```{eval-rst}
.. pss:steps:: timer_ch_c::configure

.. pss:steps:: timer_ch_c::start
```

The root's `one_shot` calls them. Its table nests each callee's steps under
the step that calls it:

```{eval-rst}
.. pss:steps:: timer_c::one_shot
   :numbering: outline
```

### Three kinds of register write

![Whole-register write, field write, write-1-to-clear](../../diagrams/rmw.svg)

Whole-register write
: `configure` builds a `timer_ch_regs__ctrl_s` value and writes it **once**
  with `regs.ctrl.write(ctrl)`. Use this when programming a register from
  scratch.

Field write
: `start` sets one bit of live state with `regs.ctrl.write_field("en", 1)`.
  That is a **read-modify-write**: a read of CTRL, then a write (PSS 3.1
  §21.14.1). The rest of CTRL is preserved.

Write-1-to-clear
: `start` clears DONE with `regs.status.write_val(1)`. **Don't**
  read-modify-write a W1C register: the read returns the bits that are set,
  and writing them back clears all of them.

:::{warning}
**Field writes read first.** On a register with clear-on-read bits, that read
*is* a side effect. Device-specific semantics like W1C, RC and sticky bits are
not part of the PSS type, so document them in the operation, where the next
reader will look (as `start` does).
:::

## Step 4: Generate, and see what the register model becomes

```console
$ make gen
```

::::{tab-set}

:::{tab-item} SystemVerilog
```{literalinclude} ../../labs/lab2/gen/sv/timer_ch_c.svh
:language: systemverilog
:caption: gen/sv/timer_ch_c.svh
:start-at: virtual task start();
:end-before: /** Stop the count. */
:dedent: 4
```

`reg_c` is parameterized by the packed struct. The field name is resolved at
generation time, to a constant (`TIMER_CH_REGS__CTRL_en`).
:::

:::{tab-item} C
```{literalinclude} ../../labs/lab2/gen/c/timer.c
:language: c
:caption: gen/c/timer.c
:start-at: void timer_ch_start
:end-before: /* Stop the count. */
```

```{literalinclude} ../../labs/lab2/gen/c/timer_regs.h
:language: c
:caption: gen/c/timer_regs.h (the private register header)
:start-at: typedef union { uint32_t raw; struct {
:end-at: timer_ch_regs__ctrl_s;
```

Registers become bitfield unions, and `write_field` becomes a masked write.
:::

::::

The `/// Step:` comments come through too, so the generated code reads like
the step table.

## Step 5: Run it

```console
$ make run
```

Every harness's fake device prints each access by register name:

::::{tab-set}

:::{tab-item} C
```{literalinclude} ../_build/generated/lab2/run-c.txt
:language: text
```
:::

:::{tab-item} SystemVerilog
```{literalinclude} ../_build/generated/lab2/run-sv.txt
:language: text
```
:::

:::{tab-item} Python
```{literalinclude} ../_build/generated/lab2/run-py.txt
:language: text
```
:::

::::

![The bus trace of one_shot](../../diagrams/lab2_trace.svg)

Match the trace to the step table above:

1. `probe()` reads ID and checks for `0x7A11`.
2. **Program the channel**: LOAD, then CTRL with EN=0.
3. **Start the count**: STATUS = 1 clears DONE; then CTRL is *read* and
   written back with EN set. That read is the read-modify-write of
   `write_field`.
4. **Wait for expiry**: STATUS is polled until DONE (bit 0) is set.

Next: {doc}`exercises`.

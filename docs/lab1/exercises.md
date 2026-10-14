# Exercises

Three exercises, each building on the last. Work in `labs/lab1`. Each
solution is in `labs/lab1/solution/`; run it with `make run SOL=1`, and open
the dropdowns below only after you have tried.

## Exercise 1: Observe

Run `make gen`, then find each PSS element in `gen/sv`, `gen/c`, `gen/cpp`
and `gen/py`:

| PSS element | Look for |
|---|---|
| state (`id`, `base`) | a class field, a struct member, an attribute |
| `initialize` | where it is called from, in each flavor |
| `delay_ticks` | the export: what the environment calls |
| `plat_delay_us` | the import: what the environment supplies |
| `tmr[2]` | how the instance array is represented |

:::{dropdown} Where to look
:icon: light-bulb

- **SystemVerilog**: `soc_c_ctxt_if.svh` (export), `soc_c_imp_if.svh`
  (import), `timer_c.svh` and `soc_c.svh` (state and operations),
  `soc_c_root.svh` (the factory that calls `initialize`).
- **C**: `soc.h` (the state structs, the export and import prototypes),
  `soc.c` (`soc_init`, which constructs and initializes the tree).
- **C++**: `soc.hpp`: `soc_import_if` (import), `soc_c_if` (export).
- **Python**: `soc.py`: `SocImportApi` (a `Protocol`), `Timer`, `Soc`.

In C the array is a fixed-size member (`timer_c tmr[2]`) with an accessor
`soc_tmr(self, i)`; in Python it is a list behind `tmr_at(i)`.
:::

## Exercise 2: Add an operation

Give `timer_c` a `stop()` operation, and give the root an exported
`cancel(int t)` that calls it.

::::{card}
**Steps**

1. In `pss/timer_c.pss`, add `target function void stop()`. It writes CTRL
   with `EN=0`, then clears DONE (write `1` to STATUS).
2. In `pss/soc_c.pss`, add `target function void cancel(int t)`, which calls
   `tmr[t].stop()`.
3. Export it: `export target function cancel;`.
4. `make gen`. Where did `cancel` appear in each flavor?
::::

You will call `cancel` from the harnesses in Exercise 3.

:::{dropdown} Solution
:icon: check-circle

```{literalinclude} ../_build/generated/lab1/diff/pss/timer_c.pss.diff
:language: diff
:caption: pss/timer_c.pss (includes Exercise 3's change to wait_done)
```

```{literalinclude} ../_build/generated/lab1/diff/pss/soc_c.pss.diff
:language: diff
:caption: pss/soc_c.pss (includes Exercise 3's change to delay_ticks)
```
:::

## Exercise 3: Change a signature

Give `wait_done` a polling budget, so a timer that never expires cannot hang
the caller.

::::{card}
**Steps**

1. Change `timer_c::wait_done` to `bool wait_done(int poll_us, int
   max_polls)`. It returns `false` if DONE was not seen after `max_polls`
   polls, and `true` otherwise.
2. Change `soc_c::delay_ticks` to `bool delay_ticks(int t, bit[32] ticks, int
   max_polls)`, returning `wait_done`'s result.
3. `make gen`. Then update the three harnesses to:
   - call `delay_ticks(1, 35, 10)` and report `done` or `TIMEOUT`;
   - call `delay_ticks(0, 1000, 5)`, which times out, and then call
     `cancel(0)`.
4. `make run`.
::::

:::{tip}
Look at how each flavor returns the new `bool`. In C and Python it is a
return value. In SystemVerilog, operations are tasks, so the result is an
`output` **first argument**: `soc.delay_ticks(ok, 1, 35, 10)`.
:::

:::::{dropdown} Solution: the harnesses
:icon: check-circle

::::{tab-set}

:::{tab-item} C
```{literalinclude} ../_build/generated/lab1/diff/env/c/main.c.diff
:language: diff
```
:::

:::{tab-item} SystemVerilog
```{literalinclude} ../_build/generated/lab1/diff/env/sv/tb.sv.diff
:language: diff
```
:::

:::{tab-item} Python
```{literalinclude} ../_build/generated/lab1/diff/env/py/run.py.diff
:language: diff
```
:::

::::
:::::

### Expected output

With the exercises done, `make run SOL=1` (or your own `make run`) prints,
for each environment:

```{literalinclude} ../_build/generated/lab1/run-py-solution.txt
:language: text
```

The second call times out after 5 polls, and `cancel(0)` stops the channel:
EN=0, then DONE cleared.

Next: {site}`Lab 2 <lab2/index.html>`, where the raw offsets are replaced by a
register model.

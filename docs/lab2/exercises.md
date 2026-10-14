# Exercises

Work in `labs/lab2`. The solution is in `labs/lab2/solution/`; run it with
`make run SOL=1`, and open the dropdowns only after you have tried.

## Exercise 1: Change the register spec

Add an `OVF` bit to STATUS: bit 2, write-1-to-clear, set when the channel
expires again while DONE is still set.

::::{card}
**Steps**

1. In `rdl/timer.rdl`, add the field to the `status` register:

   ```systemrdl
   field { sw = rw; hw = w; onwrite = woclr; desc = "Missed expiry"; } ovf[2:2] = 0;
   ```

2. Regenerate the PSS register package, then the operation model:

   ```console
   $ make regs gen
   ```

3. Find `ovf` in `pss/timer_regs_pkg.pss`, and in every generated flavor:
   `gen/sv`, `gen/c/timer_regs.h`, `gen/cpp`, `gen/py`.
::::

**You edited no PSS.** The spec change reached four languages through two
generators.

:::{dropdown} Solution
:icon: check-circle

```{literalinclude} ../_build/generated/lab2/diff/rdl/timer.rdl.diff
:language: diff
```

```{literalinclude} ../_build/generated/lab2/diff/pss/timer_regs_pkg.pss.diff
:language: diff
:caption: the regenerated PSS register package
```
:::

## Exercise 2: Write a programming sequence

Use `OVF` to run a channel periodically and count the expiries the software
missed.

::::{card}
**Steps**

1. In `pss/timer_ch_c.pss`, add `bool ack()`: read STATUS, clear DONE and OVF
   (both W1C, so write the value `0x5`), and return whether OVF was set.
2. In `pss/timer_c.pss`, add `int periodic(int c, bit[32] ticks, int n)`:
   configure channel `c` for periodic mode, start it, then `n` times wait for
   an expiry and `ack()` it. Stop the channel and return the number of missed
   expiries.
3. Mark the steps of `periodic` with `/// Step:` comments.
4. Export `periodic`, and call `periodic(1, 20, 3)` and `periodic(1, 4, 2)`
   from each harness.
5. The fake devices need to model OVF too: each must set it when an expiry
   happens while DONE is set, and clear it on a write of bit 2.
::::

:::{tip}
`ack()` must read STATUS **before** clearing it, and must not use
`write_field`: a read-modify-write of STATUS would write back every W1C bit
that is set.
:::

:::{dropdown} Solution: the model
:icon: check-circle

```{literalinclude} ../_build/generated/lab2/diff/pss/timer_ch_c.pss.diff
:language: diff
```

```{literalinclude} ../_build/generated/lab2/diff/pss/timer_c.pss.diff
:language: diff
```

The `/// Step:` comments in `periodic` give it a step table like
{pss:func}`one_shot's <timer_c::one_shot>` on the {doc}`walkthrough` page.
:::

:::::{dropdown} Solution: the harnesses
:icon: check-circle

::::{tab-set}

:::{tab-item} C
```{literalinclude} ../_build/generated/lab2/diff/env/c/main.c.diff
:language: diff
```
:::

:::{tab-item} SystemVerilog
```{literalinclude} ../_build/generated/lab2/diff/env/sv/tb.sv.diff
:language: diff
```
:::

:::{tab-item} Python
```{literalinclude} ../_build/generated/lab2/diff/env/py/run.py.diff
:language: diff
```
:::

::::
:::::

## Exercise 3: Explain the trace

Run the solution:

```console
$ make run-py SOL=1
```

```{literalinclude} ../_build/generated/lab2/run-py-solution.txt
:language: text
:start-at: periodic(1, 20, 3)
```

1. Why does `periodic(1, 4, 2)` miss expiries, when `periodic(1, 20, 3)`
   misses none?
2. Which bus accesses come from `write_field`, and how can you tell?

:::{dropdown} Answers
:icon: check-circle

1. `wait_done` polls every 10 µs. With a reload of 20, the channel expires
   once per two polls, so each expiry is acknowledged before the next. With a
   reload of 4, it expires twice or more between polls; the second expiry
   finds DONE still set, which sets OVF. `ack()` sees OVF and counts a miss.
2. A `write_field` is a **read of CTRL immediately followed by a write of
   CTRL**: in `start` (EN=1) and in `stop` (EN=0). Whole-register writes
   (`configure`) and the W1C writes to STATUS have no read before them.
:::

That is the end of the labs. Back to the {site}`overview <index.html>`.

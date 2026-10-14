---
revealjs_slide:
  data-transition: none
---

# PSS Operation Models

:::{revealjs-section}
:data-state: title
:::

**Hands-on: one device model → SystemVerilog, C, C++, Python**

Matthew Ballance

# Agenda

1. **Intro: what and why.** Integration, drift, and how far PSS gets us today
2. **Operation-model anatomy.** What an operation model has to provide, and how it maps to SV and C
3. **Lab 1: Core structure.** Component tree, initialization, export and import functions; generate and integrate
4. **Lab 2: Registers and memory.** Register models from SystemRDL; programming sequences

# Intro: what and why

:::{revealjs-section}
:data-background-color: "#1a365d"
:::

Integration and the need for consistent content

# Challenge 1: integration needs content

![](../../../diagrams/integration_challenge.svg)

:::{revealjs-notes}
Systems are composed of many design blocks: processor core, interconnect, comm
controller. Each needs complex programming to configure and operate,
individually and in aggregate. This is most apparent on integration teams: SoC,
emulation, firmware, post-silicon.
:::

# Challenge 2: drift

![](../../../diagrams/drift.svg)

:::{revealjs-notes}
One team tests one way, another differently. One small configuration or
programming difference makes the device behave very differently. A major cause
of integration headaches.
:::

# Bottom line

We need **consistent device-programming content**, delivered in **several
languages and methodologies**.

| Team | Language | What it needs |
|---|---|---|
| SoC DV | SystemVerilog / UVM | time-consuming tasks, sequencer-driven bus access |
| Emulation | C on the core, SV on the host | small footprint, fast |
| Firmware | C, bare-metal | no heap, no scheduler, `volatile` MMIO |
| Post-silicon | C / Python | scripting, lab debug, real hardware |

Same device knowledge, four different delivery requirements.

# PSS: the visible solution for portable *tests*

![](../../../diagrams/pss_test_portability.svg)

:::{revealjs-notes}
A PSS test description goes through a generator and comes out as a test in one
of many languages. Each action bubble carries randomization AND register
programming.
:::

# Two key pieces in every action

![](../../../diagrams/two_pieces.svg)

**Scenario / decision** and **realization** (device driver, device utility).

# PSS elements, briefly

![](../../../diagrams/pss_elements.svg)

# What is a *test*?

- **Limited parameterization.** A seed and a few knobs, not an API
- **Autonomous.** Exercises the design within the given parameters and checks as it goes
- **Clear pass/fail**

A test is one *consumer* of device knowledge, and not the most common one.

# PSS adoption: requirements vs. reality

![](../../../diagrams/adoption_gap.svg)

# Taking PSS beyond test reuse

**Separate realization from scenario.** At this point it's a simple separation:

![](../../../diagrams/scenario_split.svg)

# The operation model

The component functions now form a **device-programming API** we can generate:

![](../../../diagrams/op_model_fanout.svg)

PSS scenarios still call the same functions directly.

# Bottom line

- PSS gives us a **single source of truth** for device content that can target any language
- Operation models pay off **immediately**, without waiting for anyone to write PSS tests
- More PSS content available → **easier PSS adoption** for test scenarios later

# Getting technical: operation-model anatomy

:::{revealjs-section}
:data-background-color: "#1a365d"
:::

# Key requirements

![](../../../diagrams/anatomy.svg)

# Four things an operation model must provide

| Requirement | Purpose | In PSS |
|---|---|---|
| **Export API** | the environment calls in: perform an operation, notify an event | `export target function f;` on the root |
| **Import API** | the model calls out: memory access, platform services | `read32`/`write32`, `import target function` |
| **Initialization** | bind state: base addresses, ids | `solve function void initialize(...)` |
| **State** | per-instance data the operations read | component fields, register-group handles |

Everything else (scheduling, bus protocol, logging, test intent) stays in the
**environment**.

# SystemVerilog mapping

![](../../../diagrams/sv_mapping.svg)

# SystemVerilog: what you write

```systemverilog
class my_imp implements soc_c_imp_if;          // IMPORT: you implement
  virtual task write32(addr_handle_t addr, bit [31:0] data);
    /* start a bus sequence, or call a uvm_reg backdoor ... */
  endtask
  virtual task read32(addr_handle_t addr, output bit [31:0] data); ... endtask
  virtual task plat_delay_us(input int us);  #(us * 1us);  endtask
endclass

initial begin
  my_imp        imp = new();
  soc_c_ctxt_if soc = soc_c_root#(my_imp)::create(imp, 64'h4000_0000);  // FACTORY
  soc.delay_ticks(1, 35);                                                // EXPORT
end
```

- Operations are **tasks**, so they may consume time
- One `create()` per device instance; the returned handle holds the state

# C mapping

![](../../../diagrams/c_mapping.svg)

# C: what you write

```c
#include "soc.h"

/* IMPORT: memory seam (--mem-access functions) */
uint32_t pssc_mem_read32 (pssc_addr_t a)             { return *(volatile uint32_t *)a; }
void     pssc_mem_write32(pssc_addr_t a, uint32_t d) { *(volatile uint32_t *)a = d; }

/* IMPORT: the model's own imports */
void plat_delay_us(int us) { busy_wait_us(us); }

static soc_c soc;                       /* STATE: --lifecycle static, no malloc */

int main(void) {
    soc_init(&soc, 0x40000000u);        /* INIT */
    soc_delay_ticks(&soc, 1, 35);       /* EXPORT: <prefix>_<function>(self, ...) */
}
```

Python (`op-model-py`) and C++ (`op-model-cpp`) follow the same shape: an
import **protocol/interface**, a root **class**, and `create()` or a constructor.

# Next: the labs

- **Lab 1: Core structure.** Describe an operation model; generate four
  flavors; drive it from C, SystemVerilog and Python
- **Lab 2: Registers and memory.** Generate the register model from SystemRDL;
  write programming sequences against it

Setup and step-by-step instructions are in the guide.

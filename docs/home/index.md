# PSS bring-up

**Separate realization from scenario.** One PSS *operation model* holds a
device's programming knowledge once, and `pssc` generates it as an idiomatic
library for every team that has to drive the device: SystemVerilog for SoC DV,
C for firmware and emulation, C++, and Python for post-silicon.

The material is a short talk and two hands-on labs. Each section has a slide
deck and a step-by-step guide.

::::{grid} 1 1 3 3
:gutter: 3

:::{grid-item-card} Intro: what and why
:link: why
:link-type: doc

Integration, drift, how far PSS gets us today, and what an operation model
has to provide.
+++
{bdg-primary-line}`talk` {bdg-secondary-line}`~30 min`
:::

:::{grid-item-card} Lab 1: Core structure
:link: lab1/index.html

Component tree, initialization, export and import functions. Generate four
flavors and drive them from C, SystemVerilog and Python.
+++
{bdg-success-line}`lab` {bdg-secondary-line}`~45 min`
:::

:::{grid-item-card} Lab 2: Registers and memory
:link: lab2/index.html

Generate the register model from SystemRDL, then write programming
sequences against it.
+++
{bdg-success-line}`lab` {bdg-secondary-line}`~45 min`
:::

::::

```{button-link} slides/index.html
:color: primary
:outline:

Open the intro slides
```

## Before the labs

Everything runs on a laptop: each lab puts a small fake device behind the
model's import API, so no simulator license or hardware is needed. Follow
{doc}`setup` once, then start with Lab 1.

```{toctree}
:maxdepth: 2
:hidden:

why
anatomy
setup
```

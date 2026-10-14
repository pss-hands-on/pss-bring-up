# pss-bring-up

Separate realization from scenario: one PSS **operation model** generates the
device bring-up API for SystemVerilog, C, C++ and Python.

Every team that touches a device (SoC DV, emulation, firmware, post-silicon)
needs the same programming sequences in a different language, and each team's
copy drifts. A PSS operation model holds that device knowledge once, as
component functions with an export API, an import API, initialization and
state. `pssc` turns it into an idiomatic library for each consumer. PSS tests
can call the same functions later, so the model pays off before anyone writes a
PSS test.

This repo has a short positioning talk and two hands-on labs.

| | |
|---|---|
| `slides.md` | the talk (Marp) |
| `pptx/` | PowerPoint build of the same slides, with native, editable diagrams |
| `diagrams/` | diagram sources (`make_diagrams.py`) and the generated SVGs |
| `labs/lab1` | core structure: component tree, initialization, export/import functions |
| `labs/lab2` | registers and memory: SystemRDL → PSS register model, programming sequences |
| `docs/outline.md` | the talk outline |

## Setup

```bash
uvx ivpm update        # fetch the tools into packages/
direnv allow           # put them on PATH (pssc, peakrdl, verilator, python)
```

The `use` dep-set (the default) fetches Verilator from edapack, and pssc, its
libraries and peakrdl-pss **from source**: the labs need operation-model fixes
that are not on PyPI yet. You also need `gcc`. `ivpm update -d dev` adds the
PSS and SystemRDL agent skills.

## Labs

```bash
cd labs/lab1
make help
make run          # generate, then run the C, SystemVerilog and Python harnesses
make run SOL=1    # the exercise solution
```

Each environment puts a ~40-line fake device behind the model's import API, so
everything runs on a laptop, and all three print the same bus trace. See
[`labs/README.md`](labs/README.md).

## Slides

```bash
npx @marp-team/marp-cli slides.md          # HTML; --pdf or --pptx also work
cd pptx && npm install && npm run build    # the editable PowerPoint version
```

`npm run build` regenerates the diagrams first. Set `APPLY_THEME` to an
`apply_theme.js` to restyle the PowerPoint master; without it the deck builds
unthemed.

## Related

- [pss-registers-up](https://github.com/pss-hands-on/pss-registers-up): PSS
  modeling on a register-programmed device (Wishbone DMA, UVM testbench)
- [pssc](https://github.com/psstools/pssc): the PSS compiler and its
  `op-model-*` targets

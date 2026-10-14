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

This repo has a short positioning talk and two hands-on labs, published as a
docs site at **<https://dvkit.org/pss-hands-on/pss-bring-up/>**: an intro and
setup, then a section per lab with its slides and step-by-step instructions.

| | |
|---|---|
| `labs/lab1` | core structure: component tree, initialization, export/import functions |
| `labs/lab2` | registers and memory: SystemRDL → PSS register model, programming sequences |
| `docs/` | the site: one Sphinx project per section (`home`, `lab1`, `lab2`), each with a guide and a reveal.js deck in `slides/` |
| `diagrams/` | diagram sources (`make_diagrams.py`) and the generated SVGs |
| `pptx/` | PowerPoint build of the decks, with native, editable diagrams |

## Setup

```bash
uvx ivpm update        # fetch the tools into packages/
direnv allow           # put them on PATH (pssc, peakrdl, verilator, python)
```

The `use` dep-set (the default) fetches Verilator from edapack, and pssc, its
libraries and peakrdl-pss **from source**: the labs need operation-model fixes
that are not on PyPI yet, so you also need `gcc`/`g++`, `cmake`, a Java
runtime (pssparser's build runs ANTLR) and the Python headers (`python3-dev`). `ivpm update -d docs` adds Sphinx and its extensions; `-d dev` adds the PSS and SystemRDL agent skills
too.

## Labs

```bash
cd labs/lab1
make help
make run          # generate, then run the C, SystemVerilog and Python harnesses
make run SOL=1    # the exercise solution
```

Each environment puts a ~40-line fake device behind the model's import API, so
everything runs on a laptop, and all three print the same bus trace. The
step-by-step instructions are on the docs site; see also
[`labs/README.md`](labs/README.md).

## Docs

```bash
uvx ivpm update -d docs
direnv exec . docs/build.sh          # -> docs/_build/site/index.html
```

Each section's `conf.py` runs its lab (`make run`, with and without `SOL=1`)
before Sphinx reads a page: the reference pages document the *generated* code,
and the walkthroughs include the harnesses' real output. A lab that stops
working fails the docs build, and the build fails on any warning.

The Sphinx extensions, one per language on the pages:

| Extension | Domain | Used for |
|---|---|---|
| [sphinx-pss](https://github.com/psstools/sphinx-pss) | `pss` | autodoc of each lab's model; `pss:steps` tables from `/// Step:` comments |
| [sphinx-systemverilog](https://github.com/fvutils/sphinx-systemverilog) | `sv` | autodoc of the SystemVerilog API that pssc generates |
| [sphinx-peakrdl](https://github.com/SystemRDL/sphinx-peakrdl) | `rdl` | Lab 2's register map, and the PeakRDL register browser |
| pygments-pss, pygments-systemrdl | | highlighting, in the guide and on the slides |
| [sphinx-revealjs](https://github.com/attakei/sphinx-revealjs) | | the decks |

`ci/docs.sh` is the CI build: bootstrap, `docs/build.sh`, then checks that the
site is complete and every cross-section link resolves. Only the Forgejo
workflow publishes; dvkit.org picks up its `docs-pss-hands-on-pss-bring-up`
artifact.

The PowerPoint version: `cd pptx && npm install && npm run build`. Set
`APPLY_THEME` to an `apply_theme.js` to restyle the master; without it the deck
builds unthemed.

## Related

- [pss-registers-up](https://github.com/pss-hands-on/pss-registers-up): PSS
  modeling on a register-programmed device (Wishbone DMA, UVM testbench)
- [pssc](https://github.com/psstools/pssc): the PSS compiler and its
  `op-model-*` targets

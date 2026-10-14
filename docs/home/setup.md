# Setup

Do this once, before Lab 1. It takes a few minutes, most of it downloading.

## What you need

- Linux (or WSL), with `git`, `make`, `gcc`/`g++`, `cmake`, a Java
  runtime and the Python headers. pssc's libraries are built from source: two are C++ extensions,
  and pssparser runs ANTLR (Java) to generate its parser. On Ubuntu:
  `sudo apt install build-essential cmake default-jre-headless python3-dev`
- Python 3.12 or newer, and [`uv`](https://docs.astral.sh/uv/) (for `uvx`)
- [`direnv`](https://direnv.net/), hooked into your shell

Everything else comes from the repository's `ivpm.yaml`:

| Tool | Used for | From |
|---|---|---|
| `pssc` | generating the operation models | source (psstools/pssc), with pssparser and the zuspec libraries |
| `peakrdl` + peakrdl-pss | SystemRDL → PSS register package (Lab 2) | `peakrdl` from PyPI, the plugin from source |
| `verilator` ≥ 5 | running the SystemVerilog harnesses | edapack prebuilt release |
| `python3` | the Python harnesses | a venv in `packages/python` |

:::{note}
`pssc` and peakrdl-pss come from source because the labs need fixes that are
not in their PyPI releases yet.
:::

## Fetch the tools

```console
$ git clone https://github.com/pss-hands-on/pss-bring-up.git
$ cd pss-bring-up
$ uvx ivpm update
$ direnv allow
```

`ivpm update` fetches everything into `packages/` and writes
`packages/packages.envrc`. The repository's `.envrc` sources it, so once you
`direnv allow`, the tools are on your `PATH` whenever you are inside the
repository.

## Check it

```console
$ pssc --version
$ peakrdl --help | grep pss
$ verilator --version
```

You should see a `pssc` version, a `pss` subcommand for `peakrdl`, and
Verilator 5.x. Then run Lab 1's starting point:

```console
$ make -C labs/lab1 run
```

All three harnesses (C, SystemVerilog, Python) print the same bus trace. The
Python one looks like this:

```{literalinclude} ../_build/generated/lab1/run-py.txt
:language: text
```

If that works, you are ready for Lab 1.

## Lab layout

Every lab has the same shape:

```text
labs/labN/
  Makefile      make help lists the targets; add SOL=1 for the solution
  pss/          the operation model: the deliverable
  env/c/        C harness:      pssc_mem_read32/write32 + plat_delay_us, fake device
  env/sv/       SV harness:     class implementing <root>_imp_if, create(), fake device
  env/py/       Python harness: object with read32/write32/plat_delay_us
  rdl/          (Lab 2) SystemRDL source of the register model
  solution/     the same tree with the exercises done
  gen/, build/  generated output (not checked in)
```

## Troubleshooting

`make: pssc: No such file or directory`
: The environment is not loaded. Run `direnv allow` in the repository root,
  or prefix commands with `direnv exec .`.

`call to 'ExprAttribute' has no lowering in the C target`
: You are running a PyPI `pssc` rather than the source build. Check
  `which pssc`: it should be under `packages/python/bin`.

Using a different pssc source tree
: `make ... PSSC_SRC=~/projects/psstools/pssc`.

### Known pssc quirks

These are pssc issues the labs work around (as of 2026-10-14):

- `op-model-c` with `--mem-access functions` **and the default
  `--link-style mmio`** still lowers raw `read32`/`write32` to a pointer
  dereference, so a host harness segfaults. The labs pass `--link-style direct
  --mem-access functions`.
- `--link-style vtable --mem-access ...` is a user error, but it is reported
  as an internal error with a traceback (exit 2).
- Register structs narrower than the register give a C union with a
  `uint8_t raw`. The labs use `peakrdl pss --pad-tail` to avoid this.
- Hex literals in PSS come out decimal in SV and C (`0x7A11` → `31249`). This
  is cosmetic.

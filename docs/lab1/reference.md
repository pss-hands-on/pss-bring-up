# Reference

Generated from the lab's sources, so it always matches them: the PSS model
by sphinx-pss from `labs/lab1/pss/`, and the SystemVerilog API by
sphinx-systemverilog from what `pssc` generates in `labs/lab1/gen/sv/`. Doc
comments in the PSS are carried through `pssc` into the generated
SystemVerilog, which is why the two halves of this page say the same things.

## The PSS model

### Imports

```{eval-rst}
.. autopsspackage:: plat_pkg
```

### Root component

```{eval-rst}
.. autopsscomponent:: soc_c
```

### Timer channel

```{eval-rst}
.. autopsscomponent:: timer_c
```

## The generated SystemVerilog API

What an SV environment sees, from `gen/sv/soc_c_pkg.sv`.

### What you call: the export API

```{eval-rst}
.. autosvclass:: soc_c_pkg::soc_c_ctxt_if
   :members:
   :undoc-members:
```

### What you implement: the import API

```{eval-rst}
.. autosvclass:: soc_c_pkg::soc_c_imp_if
   :members:
   :undoc-members:
   :show-inheritance:
```

The memory accesses are inherited from `pss_mem_if`, in the runtime package
`pssc_reg_pkg`:

```{eval-rst}
.. autosvclass:: pssc_reg_pkg::pss_mem_if
   :members:
   :undoc-members:
```

### The factory

```{eval-rst}
.. autosvclass:: soc_c_pkg::soc_c_root
   :members: create
```

# Lab 1: core structure. See ../_shared/common.py.
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "_shared"))
import common  # noqa: E402

common.configure(globals(), "lab1", tags)  # noqa: F821 -- `tags` is Sphinx's
common.prepare_lab("lab1")
lab = common.lab_paths("lab1")

# The model as the lab hands it out (not solution/), in pssc's order.
pss_source_files = [str(lab["pss"] / f)
                    for f in ("plat_pkg.pss", "timer_c.pss", "soc_c.pss")]
# The generated SystemVerilog package: what an SV environment sees.
sv_build_units = [str(lab["gen"] / "sv" / f)
                  for f in ("pssc_reg_pkg.sv", "soc_c_pkg.sv")]
sv_include_dirs = [str(lab["gen"] / "sv")]


def setup(app):
    common.setup_app(app)

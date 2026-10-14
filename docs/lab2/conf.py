# Lab 2: registers and memory. See ../_shared/common.py.
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "_shared"))
import common  # noqa: E402

common.configure(globals(), "lab2", tags)  # noqa: F821 -- `tags` is Sphinx's
common.prepare_lab("lab2")
lab = common.lab_paths("lab2")

# The model as the lab hands it out (not solution/), in pssc's order.
pss_source_files = [str(lab["pss"] / f)
                    for f in ("timer_regs_pkg.pss", "plat_pkg.pss",
                              "timer_types_pkg.pss", "timer_ch_c.pss",
                              "timer_c.pss")]
# The generated SystemVerilog package: what an SV environment sees.
sv_build_units = [str(lab["gen"] / "sv" / f)
                  for f in ("pssc_reg_pkg.sv", "timer_c_pkg.sv")]
sv_include_dirs = [str(lab["gen"] / "sv")]
# The register spec, rendered by sphinx-peakrdl (rdl domain + PeakRDL-html).
extensions.append("sphinx_peakrdl")  # noqa: F821 -- set by configure()
# MyST asks every domain for `any` references; this one cannot answer.
suppress_warnings.append("myst.domains")  # noqa: F821
peakrdl_input_files = [str(lab["rdl"] / "timer.rdl")]
peakrdl_html_title = "Timer registers"


def setup(app):
    common.setup_app(app)

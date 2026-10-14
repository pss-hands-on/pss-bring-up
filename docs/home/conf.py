# The site root: landing page, intro, setup. See ../_shared/common.py.
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "_shared"))
import common  # noqa: E402

common.configure(globals(), "home", tags)  # noqa: F821 -- `tags` is Sphinx's
# setup.md shows the output of Lab 1's starting point.
common.prepare_lab("lab1")


def setup(app):
    common.setup_app(app)

"""Configuration shared by the three Sphinx projects that make up the site.

The site is three projects, not one, because sphinx-pss and
sphinx-systemverilog each parse ONE build unit per project, and the labs
collide inside a single one: both define ``plat_pkg`` and ``timer_c``, and a
lab's ``solution/`` tree redefines everything in it. So each section is its
own project, and ``docs/build.sh`` assembles them:

    /              docs/home    the landing page, the intro and setup
    /slides/       docs/home/slides    the intro deck (reveal.js)
    /lab1/         docs/lab1    ...and so on per lab
    /lab1/slides/  docs/lab1/slides

Each project's ``conf.py`` is a few lines that call :func:`configure`. The
guide is the ``html`` builder over the project directory; the deck is the
``revealjs`` builder over its ``slides/`` subdirectory with the same conf.py
(``-c``) and ``-t slides``.
"""

from __future__ import annotations

import pathlib
import subprocess

DOCS = pathlib.Path(__file__).resolve().parents[1]
REPO = DOCS.parent
LABS = REPO / "labs"
DIAGRAMS = REPO / "diagrams"
# Captured `make run` output, written by prepare_lab() and included by pages.
GENERATED = DOCS / "_build" / "generated"

# The sections of the site, in reading order: (directory, title, site path).
SECTIONS = [
    ("home", "Overview", ""),
    ("lab1", "Lab 1: Core structure", "lab1/"),
    ("lab2", "Lab 2: Registers and memory", "lab2/"),
]


def prepare_lab(lab: str) -> None:
    """Generate a lab's operation model and capture its runs, for the docs.

    The reference pages document the GENERATED SystemVerilog API and the
    walkthroughs show the harnesses' real output, so both have to exist before
    Sphinx reads a page. Running the lab here, rather than checking its output
    in, means a docs build fails when a lab stops working.

    Writes ``GENERATED/<lab>/run-<env>[-solution].txt`` for env in c, sv, py.
    """
    out = GENERATED / lab
    out.mkdir(parents=True, exist_ok=True)
    # All four flavors: the pages show gen/cpp too, which no run-* target makes.
    _make(lab, "gen")
    for sol, suffix in (("0", ""), ("1", "-solution")):
        for env in ("c", "sv", "py"):
            stdout = _make(lab, f"run-{env}", f"SOL={sol}")
            (out / f"run-{env}{suffix}.txt").write_text(_run_transcript(stdout))
    _solution_diffs(lab, out / "diff")


def _solution_diffs(lab: str, out: pathlib.Path) -> None:
    """``diff/<path>.diff``: each solution file against the lab's start file.

    Not literalinclude's ``:diff:``, whose headers are the absolute paths of
    the machine that built the docs -- and the site is public. These are
    labelled the way the attendee sees the files.
    """
    import difflib

    root = LABS / lab
    for sol in sorted((root / "solution").rglob("*")):
        rel = sol.relative_to(root / "solution")
        start = root / rel
        if not sol.is_file() or not start.is_file() or rel.parts[0] in ("gen", "build"):
            continue
        a, b = start.read_text().splitlines(True), sol.read_text().splitlines(True)
        if a == b:
            continue
        dest = out / f"{rel}.diff"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("".join(difflib.unified_diff(
            a, b, f"{rel}", f"solution/{rel}")))


def _make(lab: str, *args: str) -> str:
    """Run ``make -C labs/<lab> ARGS``; its stdout, or an error naming the command."""
    proc = subprocess.run(["make", "-s", "-C", str(LABS / lab), *args],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"`make -C labs/{lab} {' '.join(args)}` failed "
            f"(exit {proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
    return proc.stdout


def _run_transcript(stdout: str) -> str:
    """Keep the harness's own output; drop build chatter and Verilator's report."""
    keep = []
    for line in stdout.splitlines():
        if line.startswith(("- ", "gen/", "solution/gen/")) or "Verilator" in line:
            continue
        keep.append(line)
    return "\n".join(keep) + "\n"


def configure(ns: dict, section: str, tags) -> None:
    """Fill a project's conf.py namespace ``ns``."""
    slides = tags.has("slides")
    site_up = "" if section == "home" else "../"

    ns.update(
        project="PSS bring-up",
        author="Matthew Ballance",
        copyright="2026, Matthew Ballance",
        html_title="PSS bring-up",
        extensions=[
            "myst_parser",
            "sphinx_design",
            "sphinx_copybutton",
            "sphinx_revealjs",
            "sphinx_pss",
            "sphinx_systemverilog",
            # sphinx_peakrdl is added by lab2/conf.py only: its `rdl` domain
            # is asked to resolve every MyST link, and fails in a project
            # with no register model loaded.
        ],
        myst_enable_extensions=["colon_fence", "attrs_block", "attrs_inline",
                                "deflist", "fieldlist"],
        myst_heading_anchors=3,
        root_doc="index",
        templates_path=[str(DOCS / "_shared" / "_templates")],
        html_static_path=[str(DOCS / "_shared" / "_static")],
        html_css_files=["site.css"],
        html_theme="furo",
        html_theme_options={
            "light_css_variables": {
                "color-brand-primary": "#1a365d",
                "color-brand-content": "#2b6cb0",
            },
            "dark_css_variables": {
                "color-brand-primary": "#90cdf4",
                "color-brand-content": "#90cdf4",
            },
            "source_repository": "https://github.com/pss-hands-on/pss-bring-up/",
            "source_branch": "main",
            "source_directory": f"docs/{section}/",
        },
        html_sidebars={
            "**": [
                "sidebar/brand.html",
                "sidebar/search.html",
                "site-nav.html",
                "sidebar/scroll-start.html",
                "sidebar/navigation.html",
                "sidebar/scroll-end.html",
            ],
        },
        html_context={
            "site_up": site_up,
            "site_sections": SECTIONS,
            "site_section": section,
        },
        # Every doc block and generated listing in the labs is short enough to
        # read whole, so the copy button strips only shell prompts.
        copybutton_prompt_text=r"\$ ",
        copybutton_prompt_is_regexp=True,
        # Build units for the domain extensions. Empty for `home`; a lab's
        # conf.py sets its own after configure().
        pss_doc_style="native",
        # No undoc-members: it lists every function parameter as an entry.
        # The labs document each operation instead.
        pss_default_options={"members": True, "member-order": "source"},
        pss_diagrams="graphviz",
        sv_doc_style="auto",
        # The labs' `export target function`s are instance functions, which
        # pssparser reports as an extension to PSS 20.4.2. pssc requires it;
        # the warning is correct and says nothing a reader can act on.
        suppress_warnings=["pss.parser"],
        # Reveal.js decks.
        revealjs_style_theme="white",
        # Slide URLs by section id (#/lab-1-goals), so guide pages can link
        # to a slide and the link survives slides being added before it.
        revealjs_use_section_ids=True,
        # sphinx.ext.graphviz (loaded by sphinx-pss) links graphviz.css, but
        # the revealjs builder replaces html_static_path with this list.
        revealjs_static_path=[str(DOCS / "_shared" / "_static"),
                              _sphinx_static("graphviz")],
        # pygments.css: the HTML builder links it itself; a deck has to ask.
        revealjs_css_files=["pygments.css", "deck.css"],
        revealjs_script_conf={
            "hash": True,
            "slideNumber": "c/t",
            "width": 1280,
            "height": 760,
            "margin": 0.04,
            "center": False,
        },
        revealjs_script_plugins=[
            {"name": "RevealNotes", "src": "revealjs/plugin/notes/notes.js"},
        ],
        exclude_patterns=["_build"] + ([] if slides else ["slides/**"]),
    )
    if slides:
        # The revealjs theme names no Pygments style, so its pygments.css has
        # no token colours. (The guide keeps furo's own light/dark pair.)
        ns["pygments_style"] = "friendly"


def _sphinx_static(name: str) -> str:
    import sphinx

    return str(pathlib.Path(sphinx.__file__).parent / "templates" / name)


def setup_app(app) -> None:
    """Shared ``setup()``: Pygments, not highlight.js, for code on slides.

    sphinx-revealjs hands every code block to reveal.js's highlight.js, which
    has no grammar for PSS or SystemRDL. Sphinx's own Pygments path has both
    (pygments-pss, pygments-systemrdl), so the decks use that, the same
    highlighter as the guide pages.
    """
    from sphinx.writers.html5 import HTML5Translator
    from sphinx_revealjs.writers import RevealjsSlideTranslator

    class PygmentsSlideTranslator(RevealjsSlideTranslator):
        def visit_literal_block(self, node):
            return HTML5Translator.visit_literal_block(self, node)

    app.set_translator("revealjs", PygmentsSlideTranslator, override=True)
    app.add_role("site", site_role)


def site_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """``{site}`Title <lab2/exercises.html>``` -- a link to another section.

    The sections are separate Sphinx projects, so neither a toctree nor a
    MyST link can reach across them. The target is a path from the SITE root;
    the role makes it relative to the current page, and checks that the page
    exists in its project, so a typo fails the build instead of shipping a
    dead link.
    """
    from docutils import nodes
    from docutils.utils import unescape
    from sphinx.util.nodes import split_explicit_title

    _, title, target = split_explicit_title(unescape(text))
    first, _, rest = target.partition("/")
    labs = {d for d, _, p in SECTIONS if p}
    project, page = (first, rest) if first in labs else ("home", target)
    page = page.split("#", 1)[0] or "index.html"
    if page.startswith("slides/"):
        source = DOCS / project / "slides" / "index.md"
    else:
        source = DOCS / project / (page.removesuffix(".html") + ".md")
    if not source.is_file():
        msg = inliner.reporter.error(
            f"site: {target!r} has no source ({source.relative_to(DOCS)})",
            line=lineno)
        return [inliner.problematic(rawtext, rawtext, msg)], [msg]
    env = inliner.document.settings.env
    up = "../" * env.docname.count("/") + env.config.html_context["site_up"]
    return [nodes.reference(rawtext, title, refuri=up + target)], []


def lab_paths(lab: str) -> dict:
    """Absolute paths a lab's conf.py hands to the domain extensions."""
    root = LABS / lab
    return {"root": root, "pss": root / "pss", "gen": root / "gen",
            "rdl": root / "rdl"}

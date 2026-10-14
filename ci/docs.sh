#!/usr/bin/env bash
#****************************************************************************
#* ci/docs.sh -- build the docs site and check it, on either forge.
#*
#* Both workflow files (.github/workflows/docs.yml, .forgejo/workflows/docs.yml)
#* call this and nothing else to do the work, so what "the docs build" IS lives
#* in one place. It runs unchanged on a laptop, which is how it gets debugged.
#*
#*   1. bootstrap -- ivpm and uv into a venv, then `ivpm update -d docs`
#*   2. build     -- docs/build.sh: three Sphinx projects, each a guide and a
#*                   deck, with -W. Each project runs its lab, so a lab that
#*                   stops working fails the docs.
#*   3. check     -- the site is complete. Sphinx exits 0 on a build that
#*                   produced almost nothing, and on Forgejo this output is
#*                   PUBLISHED with no review gate in front of main, so these
#*                   checks are what stands in its place.
#*
#* Environment:
#*   DOCS_OUT     where the site is built (default: docs/_build/site)
#*   IVPM_CACHE   ivpm's package cache (default: ~/.cache/ivpm, the path the
#*                workflows cache between runs)
#*   CI_CACHE_DAYS     prune cache entries not linked for this many days (14)
#*   CI_SKIP_BOOTSTRAP=1   use packages/ as it is
#****************************************************************************
set -u -o pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

out="${DOCS_OUT:-$root/docs/_build/site}"
export IVPM_CACHE="${IVPM_CACHE:-$HOME/.cache/ivpm}"
mkdir -p "$IVPM_CACHE"

group()    { echo "::group::$*"; }
endgroup() { echo "::endgroup::"; }
fail()     { echo "::error::$*"; exit 1; }

# ---- 1. bootstrap ----------------------------------------------------------
if [ "${CI_SKIP_BOOTSTRAP:-0}" != "1" ]; then
    group "bootstrap: ivpm update -d docs"
    # direnv: packages/packages.envrc is written for it (source_env,
    # PATH_add), so the environment a developer gets from `direnv allow` is
    # the one CI gets too. cmake, java, python3-dev: pssc's source dep-set builds two
    # C++ extensions, dv-solve and pssparser, with cmake, and pssparser runs
    # ANTLR (a jar) to generate its parser. The runner image has neither.
    missing=""
    # dot (graphviz): the docs draw inheritance diagrams of the generated SV.
    for tool in direnv cmake java dot; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            case "$tool" in
            java) tool=default-jre-headless ;;
            dot)  tool=graphviz ;;
            esac
            missing="$missing $tool"
        fi
    done
    # ...and pssparser's extension compiles against Python.h.
    python3 -c 'import os, sysconfig, sys; sys.exit(not os.path.exists(os.path.join(sysconfig.get_path("include"), "Python.h")))' \
        || missing="$missing python3-dev"
    if [ -n "$missing" ]; then
        sudo=""
        [ "$(id -u)" = "0" ] || sudo="sudo"
        $sudo apt-get update -qq && $sudo apt-get install -y -qq $missing >/dev/null \
            || fail "could not install:$missing"
    fi
    # uv, and --py-uv: with pip, ivpm builds pssparser in an isolated build
    # environment that cannot see the .pxd files of debug-mgr and ciostream,
    # which it cimports, and Cython fails. uv is also what a laptop with
    # `uvx ivpm` uses, so CI installs the way the setup page does.
    python3 -m venv .ci-venv \
        && .ci-venv/bin/pip install -q --upgrade pip ivpm uv \
        || fail "could not install ivpm and uv"
    export PATH="$root/.ci-venv/bin:$PATH"
    # -a: clone git URLs as written (HTTPS). A runner has no ssh identity.
    ivpm update -a --py-uv -d docs || fail "ivpm update -d docs failed"
    ivpm cache clean --days "${CI_CACHE_DAYS:-14}" \
        || echo "::warning::ivpm cache clean failed; the cache is unchanged"
    direnv allow . || exit 1
    endgroup
fi

# ---- 2. build ---------------------------------------------------------------
group "docs/build.sh"
direnv exec . docs/build.sh "$out" || fail "docs build failed"
endgroup

# ---- 3. check ---------------------------------------------------------------
group "check the site"
for page in index.html why.html anatomy.html setup.html slides/index.html \
            lab1/index.html lab1/walkthrough.html lab1/exercises.html \
            lab1/reference.html lab1/slides/index.html \
            lab2/index.html lab2/registers.html lab2/walkthrough.html \
            lab2/exercises.html lab2/reference.html lab2/slides/index.html \
            lab2/peakrdl-html/index.html ; do
    test -s "$out/$page" || fail "$page missing from the site"
done
n=$(find "$out" -name '*.html' | wc -l)
echo "html files: $n"
[ "$n" -ge 30 ] || fail "only $n html files; the site is incomplete"

# The parts that can come out EMPTY while the build still succeeds: generated
# by the domain extensions from the labs, so check them by content.
grep -q 'soc_c_ctxt_if' "$out/lab1/reference.html" \
    || fail "lab1 reference: no generated SystemVerilog API (sphinx-systemverilog)"
grep -q 'delay_ticks' "$out/lab1/reference.html" \
    || fail "lab1 reference: no PSS model (sphinx-pss)"
grep -q 'pss-steps' "$out/lab2/walkthrough.html" \
    || fail "lab2 walkthrough: no step tables (sphinx-pss)"
grep -q 'timer_regs.ch' "$out/lab2/registers.html" \
    || fail "lab2 registers: no register map (sphinx-peakrdl)"
grep -q 'done after' "$out/lab1/walkthrough.html" \
    || fail "lab1 walkthrough: no captured run output"

# Every relative link and image in the site resolves. The sections are
# separate Sphinx projects linked by hand, which Sphinx does not check.
python3 - "$out" <<'PY' || exit 1
import pathlib, re, sys, urllib.parse
site = pathlib.Path(sys.argv[1])
bad = []
for page in site.rglob("*.html"):
    if "peakrdl-html" in page.parts or "_sv_source" in page.parts:
        continue
    for url in re.findall(r'(?:href|src)="([^"#?]+)', page.read_text(errors="ignore")):
        if re.match(r"^[a-z][a-z0-9+.-]*:", url) or url.startswith("//"):
            continue
        target = (page.parent / urllib.parse.unquote(url)).resolve()
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            bad.append(f"{page.relative_to(site)} -> {url}")
if bad:
    print("::error::broken links:\n  " + "\n  ".join(sorted(set(bad))))
    sys.exit(1)
print("OK: every relative link resolves")
PY

# The site is public: nothing may name the machine that built it. Match paths
# INTO the checkout, not the bare root: on a runner that is /w, a substring of
# half the site.
esc=$(printf '%s' "$root" | sed 's/[.[\*^$/]/\\&/g')
if grep -rIlE -- "$esc/(labs|docs|packages|diagrams|ci)/" "$out" ; then
    fail "the files above contain paths into the build machine's checkout ($root)"
fi
echo "OK: no build-machine paths in the site"
endgroup

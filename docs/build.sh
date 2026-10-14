#!/usr/bin/env bash
#****************************************************************************
#* docs/build.sh -- build the whole site: three Sphinx projects, each with a
#* guide (html) and a deck (revealjs), assembled into one tree.
#*
#*   docs/build.sh [OUT]          default OUT: docs/_build/site
#*
#*   OUT/              docs/home            OUT/slides/       docs/home/slides
#*   OUT/lab1/         docs/lab1            OUT/lab1/slides/  docs/lab1/slides
#*   OUT/lab2/         docs/lab2            OUT/lab2/slides/  docs/lab2/slides
#*
#* Why three projects, and not one: see docs/_shared/common.py. The sections
#* link to each other with relative hrefs that Sphinx does not check, so build
#* the site with this script rather than one sphinx-build: a lone project
#* deploys a site whose cross-section links are dead.
#*
#* Each project's conf.py runs its lab (`make run`, with and without SOL=1),
#* so this needs the lab tools on PATH: run it under `direnv exec .`.
#*
#* SPHINXOPTS is passed to every sphinx-build (default: -W --keep-going, so
#* any warning fails the build).
#****************************************************************************
set -eu -o pipefail

docs="$(cd "$(dirname "$0")" && pwd)"
out="${1:-$docs/_build/site}"
opts="${SPHINXOPTS:--W --keep-going}"
doctrees="$docs/_build/doctrees"

# Sphinx does not track the PSS, SV and RDL sources the domain extensions
# read, so a cached doctree would keep documenting a stale model.
rm -rf "$out" "$doctrees"
for section in home lab1 lab2; do
    if [ "$section" = home ]; then dest="$out"; else dest="$out/$section"; fi
    echo "== $section: guide -> ${dest#$docs/}"
    sphinx-build -q $opts -b html -d "$doctrees/$section" \
        "$docs/$section" "$dest"
    echo "== $section: slides -> ${dest#$docs/}/slides"
    sphinx-build -q $opts -b revealjs -t slides -d "$doctrees/$section-slides" \
        -c "$docs/$section" "$docs/$section/slides" "$dest/slides"
done
echo "site: $out"

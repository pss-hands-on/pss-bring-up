#!/bin/sh
# Regenerate SVGs and (optionally) PNG previews into $1.
cd "$(dirname "$0")" && python3 make_diagrams.py >/dev/null
[ -n "$1" ] && for f in *.svg; do inkscape "$f" --export-type=png --export-filename="$1/${f%.svg}.png" 2>/dev/null; done
true

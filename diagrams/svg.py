"""Tiny drawing helpers shared by the diagram scripts (make_diagrams.py).

Every call does two things: it appends SVG markup (for slides.md), and it
records a primitive in `self.prims` (for the PowerPoint build, which turns
each primitive into a native, editable shape). A `box` is recorded as one
primitive -- a shape with its text inside -- so it stays one object to edit.
"""
import json
import os
from xml.sax.saxutils import escape

SANS = "Helvetica, Arial, sans-serif"
MONO = "DejaVu Sans Mono, Menlo, Consolas, monospace"

# (stroke, fill, text) per role
PAL = {
    "pss":  ("#2b6cb0", "#ebf4ff", "#1a365d"),
    "sv":   ("#6b46c1", "#f3efff", "#44337a"),
    "c":    ("#2f855a", "#e6f6ec", "#1c4532"),
    "cpp":  ("#2c7a7b", "#e6fffa", "#1d4044"),
    "py":   ("#b7791f", "#fff8e6", "#744210"),
    "env":  ("#4a5568", "#f1f3f5", "#1a202c"),
    "hw":   ("#9c4221", "#fff1e8", "#652b19"),
    "warn": ("#c53030", "#fff5f5", "#742a2a"),
    "note": ("#718096", "#ffffff", "#2d3748"),
    "tool": ("#1a202c", "#2d3748", "#ffffff"),
}
INK = "#2d3748"
MUTED = "#718096"
MARKER_COLOR = {"ah": INK, "ahr": "#c53030", "ahm": MUTED}


#: every diagram saved in this run, by file stem -- see dump()
REGISTRY = {}


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.items, self.prims = w, h, [], []
        self._quiet = 0     # >0 while a box draws its parts: record nothing

    def add(self, s):
        self.items.append(s)

    def rec(self, **p):
        if not self._quiet:
            self.prims.append(p)

    def save(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{self.w}" '
                f'height="{self.h}" viewBox="0 0 {self.w} {self.h}">\n'
                '<defs>\n'
                f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>\n'
                f'<marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#c53030"/></marker>\n'
                f'<marker id="ahm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker>\n'
                '</defs>\n'
                f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>\n')
        with open(path, "w") as f:
            f.write(head + "\n".join(self.items) + "\n</svg>\n")
        REGISTRY[os.path.splitext(os.path.basename(path))[0]] = self

    def to_dict(self):
        return {"w": self.w, "h": self.h, "prims": self.prims}

    # --- primitives ---------------------------------------------------
    def text(self, x, y, s, size=16, color=INK, anchor="start", weight="normal",
             font=SANS, italic=False):
        self.rec(t="text", x=x, y=y, s=s, size=size, color=color, anchor=anchor,
                 bold=weight == "bold", mono=font == MONO, italic=italic)
        st = ' font-style="italic"' if italic else ""
        if font == MONO:
            s = s.replace(" ", "\u00a0")   # keep indentation in every renderer
        self.add(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
                 f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}"{st}>'
                 f'{escape(s)}</text>')

    def rect(self, x, y, w, h, role="pss", rx=10, dashed=False, sw=2, fill=None):
        stroke, f, _ = PAL[role]
        self.rec(t="rect", x=x, y=y, w=w, h=h, stroke=stroke, fill=fill or f, rx=rx,
                 dashed=dashed, sw=sw)
        d = ' stroke-dasharray="7 5"' if dashed else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                 f'fill="{fill or f}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def box(self, x, y, w, h, title=None, lines=(), role="pss", mono=True,
            size=15, title_size=17, dashed=False, center=False, lh=None):
        stroke, fill, tc = PAL[role]
        lh = lh or int(size * 1.4)
        self.rec(t="box", x=x, y=y, w=w, h=h, stroke=stroke, fill=fill, color=tc,
                 title=title, lines=list(lines), mono=mono, size=size,
                 title_size=title_size, dashed=dashed, center=center, lh=lh)
        self._quiet += 1
        self.rect(x, y, w, h, role, dashed=dashed)
        if center and not lines:
            self.text(x + w / 2, y + h / 2 + title_size * 0.35, title, title_size,
                      tc, "middle", "bold")
            self._quiet -= 1
            return
        cy = y + title_size + 10
        if title:
            self.text(x + w / 2 if center else x + 12, cy, title, title_size, tc,
                      "middle" if center else "start", "bold")
            cy += lh + 2
        for ln in lines:
            self.text(x + w / 2 if center else x + 14, cy, ln, size, tc,
                      "middle" if center else "start",
                      font=MONO if mono else SANS)
            cy += lh
        self._quiet -= 1

    def line(self, x1, y1, x2, y2, color=INK, sw=2, dashed=False, arrow=True,
             marker="ah", both=False, opacity=1.0):
        self.rec(t="line", x1=x1, y1=y1, x2=x2, y2=y2, color=color, sw=sw,
                 dashed=dashed, arrow=arrow, both=both, opacity=opacity)
        d = ' stroke-dasharray="6 5"' if dashed else ""
        m = f' marker-end="url(#{marker})"' if arrow else ""
        if both:
            m += f' marker-start="url(#{marker})"'
        o = f' stroke-opacity="{opacity}"' if opacity < 1 else ""
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
                 f'stroke-width="{sw}"{d}{m}{o}/>')

    def path(self, d, color=INK, sw=2, dashed=False, arrow=True, marker="ah"):
        self.rec(t="path", d=d, color=color, sw=sw, dashed=dashed, arrow=arrow)
        da = ' stroke-dasharray="6 5"' if dashed else ""
        m = f' marker-end="url(#{marker})"' if arrow else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da}{m}/>')

    def label(self, x, y, s, size=14, color=MUTED, anchor="middle", bg=True,
              weight="normal", font=SANS):
        self.rec(t="text", x=x, y=y, s=s, size=size, color=color, anchor=anchor,
                 bold=weight == "bold", mono=font == MONO, italic=False, bg=bg)
        self._quiet += 1
        if bg:
            cw = 0.6 if font == MONO else 0.53
            w = len(s) * size * cw + 10
            x0 = x - w / 2 if anchor == "middle" else (x - w + 5 if anchor == "end" else x - 5)
            self.add(f'<rect x="{x0}" y="{y - size}" width="{w}" height="{size + 7}" '
                     f'rx="4" fill="#ffffff" opacity="0.92"/>')
        self.text(x, y, s, size, color, anchor, weight, font=font)
        self._quiet -= 1


def dump(path):
    """Write every saved diagram's primitives as JSON for the PowerPoint build."""
    with open(path, "w") as f:
        json.dump({k: v.to_dict() for k, v in REGISTRY.items()}, f, indent=1)

// Builds pss-operation-models.pptx: the PowerPoint twin of the reveal.js decks.
//
// Diagrams are NOT pictures: ../diagrams/make_diagrams.py writes every
// diagram's primitives to ../diagrams/diagrams.json, and drawDiagram() below
// turns each one into a native shape (a box with its text inside, a line
// with an arrowhead, a text box), so they can be edited in PowerPoint.
//
//   cd pptx && npm install            # pptxgenjs, once
//   npm run build    # = make_diagrams.py, then NODE_PATH=./node_modules node build_deck.js
//
// Slide text follows the reveal.js decks (docs/{home,lab1,lab2}/slides/index.md);
// when one changes, change the other.
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
// The theme step is optional: point APPLY_THEME at an apply_theme.js
// (pptx skill) to restyle the master; without it the deck builds unthemed.
const applyTheme = process.env.APPLY_THEME
  ? require(process.env.APPLY_THEME).applyTheme
  : async () => {};

const OUT = path.join(__dirname, "pss-operation-models.pptx");
const DIAGRAMS = JSON.parse(fs.readFileSync(
  path.join(__dirname, "..", "diagrams", "diagrams.json"), "utf8"));

const THEME = {
  name: "PSS operation models",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1A202C", lt1: "FFFFFF", dk2: "1A365D", lt2: "F1F3F5",
    accent1: "2B6CB0", // PSS blue
    accent2: "9C4221", // device / realization
    accent3: "6B46C1", // SystemVerilog
    accent4: "718096", // muted ink
    accent5: "EBF4FF", // PSS tint
    accent6: "E2E8F0", // rules
    hlink: "2B6CB0", folHlink: "6B46C1",
  },
};
const HEX = THEME.colors;
const MONO = "Courier New";       // safe-list monospace: same width in PowerPoint and in QA
const DIAG_SANS = "Arial";        // metric-compatible with the SVGs' Helvetica

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.title = "PSS Operation Models: Hands-On";
pres.author = "Matthew Ballance";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333, M = 0.6, TOP = 1.4, BOTTOM = 6.85;

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.0, w: 12, h: 1.5,
        fontSize: 48, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 3.7, w: 12, h: 1.8,
        fontSize: 22, color: C.background2, valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "DIVIDER",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.6, w: 12, h: 1.3,
        fontSize: 44, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 4.05, w: 12, h: 0.8,
        fontSize: 20, color: C.accent5, valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  margin: [0.5, M, 0.6, M],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.9,
        fontSize: 32, bold: true, color: C.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "PSS operation models · hands-on",
        options: { x: M, y: 7.0, w: 6, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } },
  ],
  slideNumber: { x: W - M - 0.6, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: C.accent4, align: "right" },
});

// ---------- text helpers ----------
// Inline markdown -> runs: **bold**, *italic*, `code`.
function runs(str, base) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/g;
  let last = 0, m;
  const push = (text, o) => { if (text) out.push({ text, options: Object.assign({}, base, o) }); };
  while ((m = re.exec(str))) {
    push(str.slice(last, m.index), {});
    const tok = m[0];
    if (tok.startsWith("**")) push(tok.slice(2, -2), { bold: true });
    else if (tok.startsWith("`")) push(tok.slice(1, -1), { fontFace: MONO, color: HEX.accent2 });
    else push(tok.slice(1, -1), { italic: true });
    last = m.index + tok.length;
  }
  push(str.slice(last), {});
  return out;
}
// A paragraph list. Items: "text" or [level, "text"]; `numbered` for 1. 2. 3.
function para(items, o = {}) {
  const res = [];
  items.forEach((it, i) => {
    const [lvl, str] = Array.isArray(it) ? it : [0, it];
    const rs = runs(str, {});
    rs.forEach((r, j) => {
      // Paragraph options go on the first run, in a fresh object (pptxgenjs mutates
      // options in place). pptxgenjs also writes a bullet-less pPr before each later
      // run; dedupeParagraphProps() removes those after the build.
      const bullet = o.plain ? false : (o.numbered && lvl === 0 ? { type: "number" } : { indent: 18 });
      if (j === 0) Object.assign(r.options, { bullet, indentLevel: lvl, paraSpaceAfter: o.space ?? 8 });
      if (j === rs.length - 1 && i < items.length - 1) r.options.breakLine = true;
    });
    res.push(...rs);
  });
  return res;
}
// Courier New is wider than Calibri: set inline code a size smaller than its text.
function sizeCode(rs, size) {
  rs.forEach((r) => { if (r.options && r.options.fontFace === MONO && !r.options.fontSize)
    r.options.fontSize = Math.round(size * 0.86 * 2) / 2; });
  return rs;
}
function txt(s, content, o) {
  const opts = Object.assign({ isTextBox: true, fontSize: 18, color: C.text1, margin: 0, valign: "top" }, o);
  s.addText(sizeCode(typeof content === "string" ? runs(content, {}) : content, opts.fontSize), opts);
}
// A code block: monospace on a tinted card, sized to its line count.
function code(s, str, o) {
  const lines = str.replace(/\n$/, "").split("\n");
  const size = o.size || 14;
  const h = o.h || lines.length * size * 1.22 / 72 + 0.3;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: o.x, y: o.y, w: o.w, h, rectRadius: 0.06,
    fill: { color: C.background2 }, line: { color: C.accent6, width: 0.75 },
    objectName: (o.name || "code") + " card" });
  s.addText(lines.map((l, i) => ({ text: l, options: { breakLine: i < lines.length - 1 } })), {
    isTextBox: true, x: o.x + 0.15, y: o.y + 0.12, w: o.w - 0.3, h: h - 0.24,
    fontFace: MONO, fontSize: size, color: C.text1, margin: 0, valign: "top",
    lineSpacing: size * 1.22, objectName: o.name || "code" });
  return h;
}
function table(s, rows, o) {
  const fs_ = o.size || 15;
  const data = rows.map((r, ri) => r.map((cell) => ({
    text: sizeCode(runs(cell, {}), fs_),
    options: ri === 0 ? { bold: true, fill: { color: HEX.accent5 }, color: HEX.dk2 } : {},
  })));
  s.addTable(data, { x: o.x, y: o.y, w: o.w, colW: o.colW, fontSize: fs_, color: HEX.dk1,
    fontFace: THEME.bodyFontFace, border: { type: "solid", pt: 0.75, color: HEX.accent6 },
    margin: [4, 6, 4, 6], valign: "middle", objectName: o.name || "table" });
}

// ---------- diagrams as native shapes ----------
const hex = (c) => c.replace("#", "").toUpperCase();
const estW = (s, size, mono) => s.length * size * (mono ? 0.6 : 0.56);

// Merge consecutive text primitives that form one block (same x, font, size,
// regular line pitch) so a code listing is one text box, not one per line.
function mergeTexts(prims) {
  const out = [];
  for (const p of prims) {
    const prev = out[out.length - 1];
    if (p.t === "text" && !p.bg && prev && prev.t === "block" && !prev.bg &&
        p.x === prev.x && p.anchor === prev.anchor && p.mono === prev.mono &&
        p.size === prev.size && p.bold === prev.bold && p.italic === prev.italic) {
      const dy = p.y - prev.lastY;
      if (dy > p.size && dy < 2.5 * p.size && (prev.pitch === null || Math.abs(dy - prev.pitch) < 0.5)) {
        prev.pitch = dy; prev.lastY = p.y; prev.lines.push({ s: p.s, color: p.color });
        continue;
      }
    }
    if (p.t === "text") {
      out.push(Object.assign({}, p, { t: "block", lines: [{ s: p.s, color: p.color }], pitch: null, lastY: p.y }));
    } else out.push(p);
  }
  return out;
}

function parsePath(d) {
  const tok = d.match(/[MLCZ]|-?\d+(\.\d+)?/g);
  const segs = []; let i = 0, cmd = null;
  const num = () => parseFloat(tok[i++]);
  while (i < tok.length) {
    if (/[MLCZ]/.test(tok[i])) cmd = tok[i++];
    if (cmd === "M") segs.push({ k: "M", x: num(), y: num() });
    else if (cmd === "L") segs.push({ k: "L", x: num(), y: num() });
    else if (cmd === "C") segs.push({ k: "C", x1: num(), y1: num(), x2: num(), y2: num(), x: num(), y: num() });
    else if (cmd === "Z") { segs.push({ k: "Z" }); }
  }
  return segs;
}

function drawDiagram(s, name, region) {
  const d = DIAGRAMS[name];
  if (!d) throw new Error("no diagram " + name);
  const k = Math.min(region.w / d.w, region.h / d.h);          // inches per px
  const ox = region.x + (region.w - d.w * k) / 2, oy = region.y;
  const X = (v) => ox + v * k, Y = (v) => oy + v * k, L = (v) => v * k, PT = (v) => v * k * 72;
  let n = 0;
  const nm = (what) => `${name} ${what} ${++n}`;

  for (const p of mergeTexts(d.prims)) {
    if (p.t === "rect") {
      const rounded = p.rx > 0;
      s.addShape(rounded ? pres.shapes.ROUNDED_RECTANGLE : pres.shapes.RECTANGLE, Object.assign(
        { x: X(p.x), y: Y(p.y), w: L(p.w), h: L(p.h), objectName: nm("shape"),
          line: { color: hex(p.stroke), width: PT(p.sw), dashType: p.dashed ? "dash" : "solid" },
          fill: p.fill === "none" ? { type: "none" } : { color: hex(p.fill) } },
        rounded ? { rectRadius: Math.min(L(p.rx), L(Math.min(p.w, p.h)) / 2) } : {}));
    } else if (p.t === "box") {
      const S = PT(p.lh);
      const tr = [];
      if (p.title) tr.push({ text: p.title, options: { bold: true, fontSize: PT(p.title_size),
        fontFace: DIAG_SANS, color: hex(p.color), lineSpacing: S, breakLine: p.lines.length > 0 } });
      p.lines.forEach((ln, i) => tr.push({ text: ln, options: {
        fontSize: PT(p.size), fontFace: p.mono ? MONO : DIAG_SANS, color: hex(p.color),
        lineSpacing: S, breakLine: i < p.lines.length - 1 } }));
      const centerOnly = p.center && p.lines.length === 0;
      const topInset = Math.max(2, p.title_size + 10 - 0.8 * p.lh);
      s.addText(tr.length ? tr : "", {
        shape: pres.shapes.ROUNDED_RECTANGLE, x: X(p.x), y: Y(p.y), w: L(p.w), h: L(p.h),
        rectRadius: L(10), fill: { color: hex(p.fill) },
        line: { color: hex(p.stroke), width: PT(2), dashType: p.dashed ? "dash" : "solid" },
        align: p.center ? "center" : "left", valign: centerOnly ? "middle" : "top",
        margin: centerOnly ? 0 : [PT(13), PT(8), PT(4), PT(topInset)],
        objectName: nm("box") });
    } else if (p.t === "line") {
      const x = Math.min(p.x1, p.x2), y = Math.min(p.y1, p.y2);
      s.addShape(pres.shapes.LINE, { x: X(x), y: Y(y), w: L(Math.abs(p.x2 - p.x1)), h: L(Math.abs(p.y2 - p.y1)),
        flipH: p.x2 < p.x1, flipV: p.y2 < p.y1, objectName: nm("line"),
        line: Object.assign({ color: hex(p.color), width: PT(p.sw), dashType: p.dashed ? "dash" : "solid" },
          p.opacity < 1 ? { transparency: Math.round((1 - p.opacity) * 100) } : {},
          p.arrow ? { endArrowType: "triangle" } : {}, p.both ? { beginArrowType: "triangle" } : {}) });
    } else if (p.t === "path") {
      const segs = parsePath(p.d);
      const xs = [], ys = [];
      segs.forEach((g) => { ["x", "x1", "x2"].forEach((a) => g[a] !== undefined && xs.push(g[a]));
                            ["y", "y1", "y2"].forEach((a) => g[a] !== undefined && ys.push(g[a])); });
      const x0 = Math.min(...xs), y0 = Math.min(...ys);
      const w = Math.max(...xs) - x0 || 1, h = Math.max(...ys) - y0 || 1;
      const points = segs.filter((g) => g.k !== "Z").map((g) => g.k === "C"
        ? { x: L(g.x - x0), y: L(g.y - y0), curve: { type: "cubic", x1: L(g.x1 - x0), y1: L(g.y1 - y0), x2: L(g.x2 - x0), y2: L(g.y2 - y0) } }
        : Object.assign({ x: L(g.x - x0), y: L(g.y - y0) }, g.k === "M" ? { moveTo: true } : {}));
      s.addShape(pres.shapes.CUSTOM_GEOMETRY, { x: X(x0), y: Y(y0), w: L(w), h: L(h), points,
        fill: { type: "none" }, objectName: nm("connector"),
        line: Object.assign({ color: hex(p.color), width: PT(p.sw), dashType: p.dashed ? "dash" : "solid" },
          p.arrow ? { endArrowType: "triangle" } : {}) });
    } else if (p.t === "block") {
      const pitch = p.pitch || p.size * 1.2;
      const wpx = Math.max(...p.lines.map((l) => estW(l.s, p.size, p.mono))) * 1.12 + 6;
      const x = p.anchor === "middle" ? p.x - wpx / 2 : p.anchor === "end" ? p.x - wpx : p.x;
      const hpx = pitch * p.lines.length + 2;
      s.addText(p.lines.map((l, i) => ({ text: l.s, options: { color: hex(l.color),
          breakLine: i < p.lines.length - 1 } })), {
        isTextBox: true, x: X(x), y: Y(p.y - 0.8 * pitch), w: L(wpx), h: L(hpx),
        fontFace: p.mono ? MONO : DIAG_SANS, fontSize: PT(p.size), bold: p.bold, italic: p.italic,
        lineSpacing: PT(pitch), margin: 0, valign: "top", wrap: false,
        align: p.anchor === "middle" ? "center" : p.anchor === "end" ? "right" : "left",
        fill: p.bg ? { color: "FFFFFF" } : undefined, objectName: nm("text") });
    }
  }
  return oy + d.h * k;   // bottom edge, for placing a caption under it
}

// ---------- slide helpers ----------
let section = null;
function sect(title) { section = title; pres.addSection({ title }); }
function content(title, notes) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(sizeCode(runs(title, {}), 32), { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function divider(title, sub) {
  const s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (sub) s.addText(sizeCode(runs(sub, {}), 20).map((r) =>
    Object.assign(r, { options: Object.assign(r.options, { color: HEX.accent5 }) })), { placeholder: "body" });
  return s;
}
// A slide that is a diagram, optionally with a caption under it.
function diagramSlide(title, name, o = {}) {
  const s = content(title, o.notes);
  let y = TOP;
  if (o.lead) { txt(s, o.lead, { x: M, y, w: W - 2 * M, h: 0.45 }); y += 0.55; }
  const capH = o.caption ? 0.6 : 0;
  const bottom = drawDiagram(s, name, { x: M, y, w: W - 2 * M, h: (o.maxH || BOTTOM - y - capH) });
  if (o.caption) txt(s, o.caption, { x: M, y: bottom + 0.15, w: W - 2 * M, h: 0.5 });
  return s;
}
const twoCol = (W - 2 * M - 0.4) / 2;

// =====================================================================
// Title + agenda
// =====================================================================
sect("Intro");
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: section });
  s.addText("PSS Operation Models", { placeholder: "title" });
  s.addText([
    { text: "Hands-on: one device model → SystemVerilog, C, C++, Python", options: { breakLine: true } },
    { text: "Matthew Ballance", options: { fontSize: 16 } },
  ], { placeholder: "body" });
  s.addNotes("Diagrams are native shapes generated from diagrams/make_diagrams.py. Labs: labs/lab1, labs/lab2 (see labs/README.md).");
}
{
  const s = content("Agenda");
  const items = [
    ["1", "Intro: what and why", "Integration, drift, and how far PSS gets us today"],
    ["2", "Operation-model anatomy", "What an operation model has to provide, and how it maps to SV and C"],
    ["3", "Lab 1: Core structure", "Component tree, initialization, export and import functions; generate and integrate"],
    ["4", "Lab 2: Registers and memory", "Register models from SystemRDL; programming sequences"],
  ];
  items.forEach(([n, t, d], i) => {
    const y = TOP + 0.1 + i * 1.3;
    s.addShape(pres.shapes.OVAL, { x: M, y, w: 0.8, h: 0.8, fill: { color: C.accent1 },
      line: { color: C.accent1 }, objectName: "agenda dot " + n });
    s.addText(n, { isTextBox: true, x: M, y, w: 0.8, h: 0.8, fontSize: 24, bold: true,
      color: C.background1, align: "center", valign: "middle", margin: 0, objectName: "agenda num " + n });
    txt(s, t, { x: M + 1.1, y: y + 0.02, w: 10.5, h: 0.42, fontSize: 22, bold: true, color: C.text2 });
    txt(s, d, { x: M + 1.1, y: y + 0.45, w: 10.5, h: 0.4, fontSize: 16, color: C.accent4 });
  });
}

// =====================================================================
// Intro
// =====================================================================
divider("Intro: what and why", "Integration and the need for consistent content");

diagramSlide("Challenge 1: integration needs content", "integration_challenge", {
  notes: "Systems are composed of many design blocks: processor core, interconnect, comm controller. Each needs complex programming to configure and operate, individually and in aggregate. Most apparent on integration teams: SoC, emulation, firmware, post-silicon." });

diagramSlide("Challenge 2: drift", "drift", {
  notes: "One team tests one way, another differently. One small config/programming difference causes the device to behave very differently. Major cause of integration headaches." });

{
  const s = content("Bottom line: one device, four delivery requirements");
  txt(s, "We need **consistent device-programming content**, delivered in **several languages and methodologies**.",
    { x: M, y: TOP, w: W - 2 * M, h: 0.5 });
  table(s, [
    ["Team", "Language", "What it needs"],
    ["SoC DV", "SystemVerilog / UVM", "time-consuming tasks, sequencer-driven bus access"],
    ["Emulation", "C on the core, SV on the host", "small footprint, fast"],
    ["Firmware", "C, bare-metal", "no heap, no scheduler, `volatile` MMIO"],
    ["Post-silicon", "C / Python", "scripting, lab debug, real hardware"],
  ], { x: M, y: TOP + 0.8, w: W - 2 * M, colW: [2.3, 3.6, 6.23], size: 17 });
  txt(s, "*Same device knowledge, four different delivery requirements.*",
    { x: M, y: 5.3, w: W - 2 * M, h: 0.5, color: C.accent4 });
}

diagramSlide("PSS: the visible solution for portable *tests*", "pss_test_portability", {
  notes: "PSS test description -> generator -> test implemented in one of many languages. Each action bubble carries randomization AND register programming." });

diagramSlide("Two key pieces in every action", "two_pieces", {
  caption: "**Scenario / decision** and **realization** (device driver, device utility)." });

diagramSlide("PSS elements, briefly", "pss_elements");

{
  const s = content("What is a *test*?");
  const cards = [
    ["Limited parameterization", "A seed and a few knobs, not an API"],
    ["Autonomous", "Exercises the design within the given parameters and checks as it goes"],
    ["Clear pass/fail", "One verdict at the end"],
  ];
  const cw = (W - 2 * M - 0.6) / 3;
  cards.forEach(([h, b], i) => {
    const x = M + i * (cw + 0.3);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: TOP + 0.2, w: cw, h: 2.4, rectRadius: 0.08,
      fill: { color: C.accent5 }, line: { color: C.accent5 }, objectName: "test trait " + i });
    txt(s, h, { x: x + 0.3, y: TOP + 0.5, w: cw - 0.6, h: 0.5, fontSize: 22, bold: true, color: C.text2 });
    txt(s, b, { x: x + 0.3, y: TOP + 1.15, w: cw - 0.6, h: 1.2, fontSize: 17 });
  });
  txt(s, "A test is one *consumer* of device knowledge, and not the most common one.",
    { x: M, y: 4.6, w: W - 2 * M, h: 0.6, fontSize: 22, bold: true, color: C.accent2 });
}

diagramSlide("PSS adoption: requirements vs. reality", "adoption_gap");

diagramSlide("Taking PSS beyond test reuse", "scenario_split", {
  lead: "**Separate realization from scenario.** At this point it's a simple separation:" });

diagramSlide("The operation model", "op_model_fanout", {
  lead: "The component functions now form a **device-programming API** we can generate:",
  caption: "PSS scenarios still call the same functions directly." });

{
  const s = content("Bottom line");
  const pts = [
    ["Single source of truth", "PSS gives us device content that can target any language"],
    ["Pays off immediately", "Operation models don't wait for anyone to write PSS tests"],
    ["Easier PSS adoption", "More PSS content available → test scenarios become cheaper later"],
  ];
  pts.forEach(([h, b], i) => {
    const y = TOP + 0.2 + i * 1.6;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: W - 2 * M, h: 1.3, rectRadius: 0.08,
      fill: { color: i === 1 ? C.accent5 : C.background2 }, line: { color: C.background2 }, objectName: "point " + i });
    txt(s, h, { x: M + 0.35, y: y + 0.2, w: 11, h: 0.45, fontSize: 22, bold: true, color: C.text2 });
    txt(s, b, { x: M + 0.35, y: y + 0.7, w: 11, h: 0.45, fontSize: 18 });
  });
}

// =====================================================================
// Anatomy
// =====================================================================
sect("Anatomy");
divider("Getting technical: operation-model anatomy");

diagramSlide("Key requirements", "anatomy");

{
  const s = content("Four things an operation model must provide");
  table(s, [
    ["Requirement", "Purpose", "In PSS"],
    ["**Export API**", "the environment calls in: perform an operation, notify an event", "`export target function f;` on the root"],
    ["**Import API**", "the model calls out: memory access, platform services", "`read32`/`write32`, `import target function`"],
    ["**Initialization**", "bind state: base addresses, ids", "`solve function void initialize(...)`"],
    ["**State**", "per-instance data the operations read", "component fields, register-group handles"],
  ], { x: M, y: TOP + 0.1, w: W - 2 * M, colW: [2.3, 5.0, 4.83], size: 17 });
  txt(s, "Everything else (scheduling, bus protocol, logging, test intent) stays in the **environment**.",
    { x: M, y: 5.2, w: W - 2 * M, h: 0.5 });
}

diagramSlide("SystemVerilog mapping", "sv_mapping");

{
  const s = content("SystemVerilog: what you write");
  const h = code(s, `class my_imp implements soc_c_imp_if;          // IMPORT: you implement
  virtual task write32(addr_handle_t addr, bit [31:0] data);
    /* start a bus sequence, or call a uvm_reg backdoor ... */
  endtask
  virtual task read32(addr_handle_t addr, output bit [31:0] data); ... endtask
  virtual task plat_delay_us(input int us);  #(us * 1us);  endtask
endclass

initial begin
  my_imp        imp = new();
  soc_c_ctxt_if soc = soc_c_root#(my_imp)::create(imp, 64'h4000_0000);  // FACTORY
  soc.delay_ticks(1, 35);                                                // EXPORT
end`, { x: M, y: TOP, w: W - 2 * M, size: 15, name: "sv usage" });
  txt(s, para(["Operations are **tasks**, so they may consume time",
               "One `create()` per device instance; the returned handle holds the state"]),
    { x: M, y: TOP + h + 0.3, w: W - 2 * M, h: 1.0 });
}

diagramSlide("C mapping", "c_mapping");

{
  const s = content("C: what you write");
  const h = code(s, `#include "soc.h"

/* IMPORT: memory seam (--mem-access functions) */
uint32_t pssc_mem_read32 (pssc_addr_t a)             { return *(volatile uint32_t *)a; }
void     pssc_mem_write32(pssc_addr_t a, uint32_t d) { *(volatile uint32_t *)a = d; }

/* IMPORT: the model's own imports */
void plat_delay_us(int us) { busy_wait_us(us); }

static soc_c soc;                       /* STATE: --lifecycle static, no malloc */

int main(void) {
    soc_init(&soc, 0x40000000u);        /* INIT */
    soc_delay_ticks(&soc, 1, 35);       /* EXPORT: <prefix>_<function>(self, ...) */
}`, { x: M, y: TOP, w: W - 2 * M, size: 15, name: "c usage" });
  txt(s, "Python (`op-model-py`) and C++ (`op-model-cpp`) follow the same shape: an import **protocol/interface**, a root **class**, and `create()` or a constructor.",
    { x: M, y: TOP + h + 0.3, w: W - 2 * M, h: 0.8 });
}

// =====================================================================
// Lab 1
// =====================================================================
sect("Lab 1");
divider("Lab 1: Core structure", "`labs/lab1`");

{
  const s = content("Lab 1 goals");
  txt(s, para([
    "Describe an operation model in PSS:",
    [1, "a **component tree** holding **state**"],
    [1, "an **initialization** function"],
    [1, "**operations**, **exports** and **imports**"],
    "Generate it with `pssc` in four flavors",
    "Integrate it into three environments: **C**, **SystemVerilog**, **Python**",
    "See that all three drive the device **identically**",
  ]), { x: M, y: TOP, w: 6.6, h: 4.8, fontSize: 20 });
  // the three environments as a visual
  [["C", "2F855A", "E6F6EC"], ["SystemVerilog", "6B46C1", "F3EFFF"], ["Python", "B7791F", "FFF8E6"]].forEach(([t, st, f], i) => {
    s.addText(t, { shape: pres.shapes.ROUNDED_RECTANGLE, x: 8.4, y: TOP + 0.4 + i * 1.3, w: 3.9, h: 1.0,
      rectRadius: 0.08, fill: { color: f }, line: { color: st, width: 1.5 }, fontSize: 20, bold: true,
      color: st, align: "center", valign: "middle", objectName: "env " + t });
  });
  txt(s, "same model · same bus traffic", { x: 8.4, y: TOP + 4.3, w: 3.9, h: 0.4, fontSize: 15,
    italic: true, color: C.accent4, align: "center" });
}

diagramSlide("The device and the model", "lab1_model", {
  caption: "Two timer channels, raw register offsets for now (Lab 2 fixes that)." });

{
  const s = content("PSS: imports (`pss/plat_pkg.pss`)");
  const h = code(s, `// What the operation model needs FROM its environment.
// The environment (UVM test, firmware, Python harness) implements these.
package plat_pkg {
    // Wait for (at least) 'us' microseconds of device time.
    import target function void plat_delay_us(int us);
}`, { x: M, y: TOP, w: W - 2 * M, size: 15, name: "plat_pkg" });
  txt(s, para([
    "`import target function` declares a **platform service**. The model only names it.",
    "Memory access (`read32`/`write32`) is an implicit import, from `addr_reg_pkg`.",
    "Each generator turns imports into the language's *\"you implement this\"* form:",
    [1, "SV: a method on `soc_c_imp_if`"], [1, "C: an `extern` prototype"], [1, "Py: a method on a `Protocol`"],
  ]), { x: M, y: TOP + h + 0.3, w: W - 2 * M, h: 3.0 });
}

{
  const s = content("PSS: a leaf component (`pss/timer_c.pss`)");
  code(s, `component timer_c {
    // --- State: set once at initialization, read by every operation
    int            id;
    addr_handle_t  base;

    // --- Initialization: bind this instance to its address window
    solve function void initialize(int i, addr_handle_t b) {
        id   = i;
        base = b;
    }

    // --- Operations
    target function void start(bit[32] ticks) {
        write32(make_handle_from_handle(base, 0x8), 1);     // clear DONE
        write32(make_handle_from_handle(base, 0x4), ticks); // LOAD
        write32(make_handle_from_handle(base, 0x0), 1);     // EN
    }
    target function bool is_done() {
        bit[32] sts = read32(make_handle_from_handle(base, 0x8));
        return (sts & 1) != 0;
    }
    target function void wait_done(int poll_us) {
        while (!is_done()) { plat_delay_us(poll_us); }
    }
}`, { x: M, y: TOP - 0.1, w: 8.9, size: 12.5, name: "timer_c" });
  const notes = [["State", "fields every operation reads"], ["Initialization", "`solve function`: binds state once"],
                 ["Operations", "`target function`: touch the device"]];
  notes.forEach(([t, d], i) => {
    const y = TOP + 0.2 + i * 1.6;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.8, y, w: 2.93, h: 1.3, rectRadius: 0.08,
      fill: { color: C.accent5 }, line: { color: C.accent5 }, objectName: "callout " + t });
    txt(s, t, { x: 10.0, y: y + 0.15, w: 2.6, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
    txt(s, d, { x: 10.0, y: y + 0.58, w: 2.6, h: 0.65, fontSize: 14 });
  });
}

{
  const s = content("PSS: the root (`pss/soc_c.pss`)");
  const h = code(s, `component soc_c {
    timer_c  tmr[2];

    solve function void initialize(addr_handle_t base) {
        foreach (tmr[i]) {
            tmr[i].initialize(i, make_handle_from_handle(base, i * 0x100));
        }
    }

    // A composite operation: start a timer and block until it expires.
    target function void delay_ticks(int t, bit[32] ticks) {
        tmr[t].start(ticks);
        tmr[t].wait_done(10);
    }

    // The API the environment sees.
    export target function delay_ticks;
}`, { x: M, y: TOP - 0.1, w: W - 2 * M, size: 13, name: "soc_c" });
  txt(s, para([
    "The **root** is chosen on the command line (`--root soc_c`)",
    "**Exports** select the root functions the environment can call. Sub-component functions remain reachable in C/C++/Py.",
  ]), { x: M, y: TOP - 0.1 + h + 0.2, w: W - 2 * M, h: 1.0, fontSize: 17 });
}

{
  const s = content("Generating output");
  const bottom = drawDiagram(s, "pssc_flow", { x: M, y: TOP - 0.1, w: W - 2 * M, h: 4.1 });
  code(s, `pssc compile pss/plat_pkg.pss pss/timer_c.pss pss/soc_c.pss \\
     -t op-model-c --root soc_c -o gen/c \\
     --link-style direct --mem-access functions --lifecycle static`,
    { x: M, y: bottom + 0.2, w: W - 2 * M, size: 15, name: "pssc command" });
}

{
  const s = content("Available output flavors");
  table(s, [
    ["`-t`", "Output", "Useful options"],
    ["`op-model-sv`", "package with `*_imp_if`, `*_ctxt_if`, `*_root`", "`--package NAME`"],
    ["`op-model-c`", "`<prefix>.h/.c`, private `<prefix>_regs.h`", "`--prefix`, `--link-style`, `--mem-access`, `--lifecycle static`, `--addr-bits 32`, `--yield import`"],
    ["`op-model-cpp`", "`<ns>.hpp`, header-only", "`--namespace`, `--dispatch {virtual,template}`"],
    ["`op-model-py`", "`<module>.py` + `pssc_rt.py`", "`--py-await {sync,async}`"],
    ["*(all)*", "", "`--emit-manifest FILE` (JSON: ops, signatures, register offsets), `--no-comments`"],
  ], { x: M, y: TOP, w: W - 2 * M, colW: [2.2, 4.4, 5.53], size: 15 });
  txt(s, "`pssc targets` lists them all. Each target also tells the model what it can do via `target_cfg_pkg` (e.g. `HAVE_EVENT_WAIT`).",
    { x: M, y: 5.75, w: W - 2 * M, h: 0.8, fontSize: 17 });
}

{
  const s = content("PSS → SystemVerilog");
  const y = TOP;
  const h1 = code(s, `target function bool is_done() {
    bit[32] sts = read32(
        make_handle_from_handle(base, 0x8));
    return (sts & 1) != 0;
}

target function void wait_done(int poll_us) {
    while (!is_done()) {
        plat_delay_us(poll_us);
    }
}`, { x: M, y, w: twoCol, size: 13, name: "pss is_done", h: 4.3 });
  code(s, `virtual task is_done(output bit status);
  bit [31:0] sts;
  pss_imp.read32((base + 8), sts);
  status = (sts & 1) != 0;
  return;
endtask

virtual task wait_done(input int poll_us);
  bit pssc_tmp_0;
  forever begin
    is_done(pssc_tmp_0);
    if (!(!(pssc_tmp_0))) break;
    pss_imp.plat_delay_us(poll_us);
  end
endtask`, { x: M + twoCol + 0.4, y, w: twoCol, size: 13, name: "sv is_done", h: 4.3 });
  txt(s, "Return values become an `output` **first argument**, since operations are tasks. Address arithmetic is folded: `base + 8`.",
    { x: M, y: y + h1 + 0.25, w: W - 2 * M, h: 0.8, fontSize: 17 });
}

{
  const s = content("PSS → C and Python");
  const y = TOP;
  code(s, `uint8_t timer_is_done(timer_c *_self) {
    uint32_t sts = pssc_r32(pssc_bus(_self),
                            (_self->base + 8));
    return (sts & 1) != 0;
}

void timer_wait_done(timer_c *_self,
                     int poll_us) {
    while (!(timer_is_done(_self))) {
        plat_delay_us(poll_us);
    }
}`, { x: M, y, w: twoCol, size: 13, name: "c is_done", h: 4.3 });
  code(s, `class Timer(object):
    def __init__(self, imports: SocImportApi, i, b):
        self._imports = imports
        self.id = i
        self.base = b

    def is_done(self):
        sts = self._imports.read32((self.base + 8))
        return (sts & 1) != 0

    def wait_done(self, poll_us):
        while not (self.is_done()):
            self._imports.plat_delay_us(poll_us)`, { x: M + twoCol + 0.4, y, w: twoCol, size: 13, name: "py is_done", h: 4.3 });
  txt(s, "Comments in the PSS source are carried into every output (`--no-comments` to drop them).",
    { x: M, y: y + 4.55, w: W - 2 * M, h: 0.5, fontSize: 17 });
}

diagramSlide("What happens at run time", "lab1_sequence");

{
  const s = content("Environment integration");
  const envs = [
    ["SystemVerilog", "env/sv/tb.sv", "6B46C1", "F3EFFF", ["class `implements soc_c_imp_if`", "`soc_c_root#(T)::create(imp, base)`", "`write32`/`read32` may consume time"]],
    ["C", "env/c/main.c", "2F855A", "E6F6EC", ["define `pssc_mem_read32/write32`", "define `plat_delay_us`", "`static soc_c soc;` `soc_init(&soc, base);`"]],
    ["Python", "env/py/run.py", "B7791F", "FFF8E6", ["any object with `read32`, `write32`, `plat_delay_us`", "a `Protocol`: no inheritance needed", "`Soc(env, base)`"]],
  ];
  const cw = (W - 2 * M - 0.6) / 3;
  envs.forEach(([t, f, st, fill, items], i) => {
    const x = M + i * (cw + 0.3);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: TOP, w: cw, h: 3.9, rectRadius: 0.08,
      fill: { color: fill }, line: { color: st, width: 1.5 }, objectName: "env card " + t });
    txt(s, t, { x: x + 0.25, y: TOP + 0.2, w: cw - 0.5, h: 0.45, fontSize: 22, bold: true, color: st });
    txt(s, runs("`" + f + "`", {}), { x: x + 0.25, y: TOP + 0.7, w: cw - 0.5, h: 0.35, fontSize: 14 });
    txt(s, para(items), { x: x + 0.25, y: TOP + 1.25, w: cw - 0.5, h: 2.5, fontSize: 16 });
  });
  txt(s, "**All three** use a ~40-line *fake timer* behind the import API, so the lab runs on a laptop.",
    { x: M, y: TOP + 4.25, w: W - 2 * M, h: 0.6 });
}

{
  const s = content("Lab 1: run it");
  const h = code(s, `cd labs/lab1
make run                                      # gen + run C, SV (Verilator), Python
make run PSSC_SRC=~/projects/psstools/pssc    # against a pssc source tree`,
    { x: M, y: TOP, w: W - 2 * M, size: 15, name: "run cmds" });
  const h2 = code(s, `delay_ticks(1, 35)
  [bus] write32 0x40000108 = 0x1
  [bus] write32 0x40000104 = 0x23
  [bus] write32 0x40000100 = 0x1
done after 4 polls`, { x: M, y: TOP + h + 0.3, w: 7.5, size: 15, name: "run output" });
  s.addText([{ text: "×3", options: { fontSize: 54, bold: true, color: C.accent1, breakLine: true } },
             { text: "identical output from C, SV and Python", options: { fontSize: 17, color: C.text1 } }],
    { isTextBox: true, x: 8.6, y: TOP + h + 0.3, w: 4.1, h: h2, margin: 0, valign: "middle", objectName: "same output" });
  txt(s, "**Same model, same bus traffic.**", { x: M, y: TOP + h + h2 + 0.55, w: W - 2 * M, h: 0.5 });
}

{
  const s = content("Lab 1 exercises");
  txt(s, para([
    "**Observe.** `make gen`, then find each PSS element in `gen/sv`, `gen/c`, `gen/cpp`, `gen/py`: state, `initialize`, `delay_ticks`, `plat_delay_us`, `tmr[2]`",
    "**Add an operation.** Give `timer_c` a `stop()` (EN=0, clear DONE); add and export `soc_c::cancel(int t)`. Regenerate: where did `cancel` appear in each flavor?",
    "**Change a signature.** Give `wait_done` a `max_polls` budget and make it return `bool`; make `delay_ticks` return it. Update the three harnesses to report a timeout and call `cancel()`",
  ], { numbered: true, space: 14 }), { x: M, y: TOP, w: W - 2 * M, h: 4.2, fontSize: 19 });
  txt(s, "Solution: `labs/lab1/solution`, run with `make run SOL=1`.",
    { x: M, y: 5.9, w: W - 2 * M, h: 0.5, color: C.accent4 });
}

// =====================================================================
// Lab 2
// =====================================================================
sect("Lab 2");
divider("Lab 2: Registers and memory", "`labs/lab2`");

{
  const s = content("Why a register model?");
  txt(s, "Lab 1 wrote `write32(make_handle_from_handle(base, 0x8), 1)`.",
    { x: M, y: TOP, w: W - 2 * M, h: 0.5 });
  const probs = [
    ["Offsets", "restated by hand; wrong ones fail silently"],
    ["Fields & masks", "positions and masks restated by hand"],
    ["Access rules", "read-only, W1C: invisible in the code"],
    ["Copies", "RTL, UVM RAL, firmware headers each keep their own"],
  ];
  const cw = (W - 2 * M - 0.9) / 4;
  probs.forEach(([h, b], i) => {
    const x = M + i * (cw + 0.3);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: TOP + 0.75, w: cw, h: 2.0, rectRadius: 0.08,
      fill: { color: "FFF5F5" }, line: { color: "FFF5F5" }, objectName: "problem " + i });
    txt(s, h, { x: x + 0.25, y: TOP + 0.95, w: cw - 0.5, h: 0.45, fontSize: 19, bold: true, color: "C53030" });
    txt(s, b, { x: x + 0.25, y: TOP + 1.5, w: cw - 0.5, h: 1.1, fontSize: 15 });
  });
  txt(s, "PSS 3.x has a **register model** in `addr_reg_pkg`. Generate it from the same source as everything else.",
    { x: M, y: TOP + 3.2, w: W - 2 * M, h: 0.8, fontSize: 20 });
}

{
  const s = content("Creating register models");
  const bottom = drawDiagram(s, "reg_flow", { x: M, y: TOP - 0.1, w: W - 2 * M, h: 4.4 });
  code(s, "peakrdl pss rdl/timer.rdl --pad-tail -o pss/timer_regs_pkg.pss",
    { x: M, y: bottom + 0.2, w: W - 2 * M, size: 15, name: "peakrdl command" });
}

diagramSlide("PSS register-model anatomy", "reg_anatomy");

{
  const s = content("Generated register package (excerpt)");
  const h = code(s, `package timer_regs_pkg {
    import addr_reg_pkg::*;

    struct timer_ch_regs__status_s : packed_s<LITTLE_ENDIAN> {
        bit done;       // [0] sw=rw hw=w reset=0x0 dropped: onwrite=woclr
        bit busy;       // [1] sw=r hw=w reset=0x0
        bit[30] rsvd_2; // [31:2] reserved
    }
    pure component timer_ch_regs__status_c : reg_c<timer_ch_regs__status_s, READWRITE, 32> {}

    pure component timer_ch_regs_c : reg_group_c {
        timer_ch_regs__ctrl_c   ctrl;
        timer_ch_regs__load_c   load;
        timer_ch_regs__status_c status;
        timer_ch_regs__count_c  count;

        pure function bit[64] get_offset_of_instance(string name) {
            match (name) { ["ctrl"]: return 0x0;  ["load"]: return 0x4;  /* ... */ }
        }
    }
}`, { x: M, y: TOP - 0.1, w: W - 2 * M, size: 12.5, name: "regs pkg" });
  txt(s, "`onwrite = woclr` has no PSS equivalent: peakrdl-pss warns (`PSS-W101`) and keeps it as a comment.",
    { x: M, y: TOP - 0.1 + h + 0.15, w: W - 2 * M, h: 0.5, fontSize: 16 });
}

{
  const s = content("Register and memory access functions");
  table(s, [
    ["Call", "On", "Bus effect"],
    ["`read()` / `write(v)`", "`reg_c<R>`", "one access; value is the packed struct `R`"],
    ["`read_val()` / `write_val(raw)`", "`reg_c<R>`", "one access; raw `bit[N]`"],
    ["`write_field(\"en\", 1)`", "`reg_c<R>`", "**read-modify-write** of one field"],
    ["`write_masked(mask, v)`", "`reg_c<R>`", "**read-modify-write**"],
    ["`set_handle(h)`", "`reg_group_c`", "none: binds the bank to an address (init only)"],
    ["`get_offset_of_instance[_array]`", "`reg_group_c`", "none: folded to a constant by pssc"],
    ["`read32(h)` / `write32(h, v)`, 8/16/64", "`addr_handle_t`", "raw memory access (Lab 1)"],
    ["`make_handle_from_handle(h, off)`", "`addr_handle_t`", "none: address arithmetic"],
  ], { x: M, y: TOP - 0.1, w: W - 2 * M, colW: [4.6, 2.2, 5.33], size: 14 });
  txt(s, "The field name in `write_field` is **resolved at compile time**, so a typo is an error rather than a wrong bit.",
    { x: M, y: 6.25, w: W - 2 * M, h: 0.5, fontSize: 16 });
}

diagramSlide("Binding registers to addresses", "address_binding");

{
  const s = content("The programming sequence (`pss/timer_ch_c.pss`)");
  code(s, `component timer_ch_c {
    int              id;
    timer_ch_regs_c  regs;      // this channel's register bank

    solve function void initialize(int i, addr_handle_t bank) {
        id = i;
        regs.set_handle(bank);
    }

    target function void configure(timer_cfg_s cfg) {
        timer_ch_regs__ctrl_s ctrl;
        timer_ch_regs__load_s load;
        load.value = cfg.ticks;
        regs.load.write(load);
        ctrl.en = 0;  ctrl.irq_en = cfg.irq_en;            // build the value,
        ctrl.mode = cfg.periodic;  ctrl.prescale = cfg.prescale;
        regs.ctrl.write(ctrl);                              // then write it once
    }

    target function void start() {
        regs.status.write_val(1);         // DONE is write-1-to-clear
        regs.ctrl.write_field("en", 1);   // read-modify-write of one field
    }

    target function bool is_done() {
        timer_ch_regs__status_s sts = regs.status.read();
        return sts.done == 1;
    }
}`, { x: M, y: TOP - 0.15, w: W - 2 * M, size: 11.5, name: "timer_ch_c" });
}

diagramSlide("Register-operation details", "rmw");

{
  const s = content("Register-operation pitfalls");
  const items = [
    ["Field writes read first", "`write_field`/`write_masked` are a read-modify-write (PSS 3.1 §21.14.1). On a register with clear-on-read bits, that read **is** a side effect."],
    ["W1C registers", "Write the clear value with `write_val`. Don't RMW a W1C register, or you'll clear bits you didn't mean to."],
    ["Whole vs. field writes", "Build a struct and `write()` once when configuring. Use `write_field()` to flip one bit of live state."],
    ["Reserved bits", "Use `--pad-tail` so every struct spans the full register width. Otherwise C gets a `uint8_t raw` for a 32-bit register."],
    ["Device semantics", "W1C, RC and sticky bits aren't in the PSS type. Document them in the operation, where the next reader will look."],
  ];
  items.forEach(([h, b], i) => {
    const y = TOP - 0.1 + i * 1.07;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: W - 2 * M, h: 0.92, rectRadius: 0.06,
      fill: { color: i === 0 ? "FFF5F5" : C.background2 }, line: { color: i === 0 ? "FFF5F5" : C.background2 },
      objectName: "pitfall " + i });
    txt(s, h, { x: M + 0.25, y: y + 0.12, w: 3.0, h: 0.7, fontSize: 18, bold: true,
      color: i === 0 ? "C53030" : C.text2, valign: "middle" });
    txt(s, b, { x: M + 3.4, y: y + 0.08, w: W - 2 * M - 3.6, h: 0.78, fontSize: 15, valign: "middle" });
  });
}

{
  const s = content("What it generates");
  code(s, `// SV: reg_c parameterized by the packed struct
class timer_ch_regs_c;
  reg_c #(timer_ch_regs__ctrl_s)   ctrl;
  reg_c #(timer_ch_regs__load_s)   load;
  reg_c #(timer_ch_regs__status_s) status;
  reg_c #(timer_ch_regs__count_s,
          READONLY)                count;
  ...
endclass

virtual task start();
  regs.status.write_val(1);
  regs.ctrl.write_field(
      TIMER_CH_REGS__CTRL_en, 1);
endtask`, { x: M, y: TOP, w: twoCol, size: 13, name: "sv regs", h: 4.8 });
  code(s, `/* C: bitfield unions, private header */
typedef union { uint32_t raw; struct {
    uint32_t en       :  1;
    uint32_t irq_en   :  1;
    uint32_t mode     :  1;
    uint32_t rsvd_3   :  1;
    uint32_t prescale :  4;
    uint32_t rsvd_8   : 24;
}; } timer_ch_regs__ctrl_s;

void timer_ch_start(timer_ch_c *_self) {
    timer_ch_regs_status_write_val(_self, 1);
    timer_ch_regs_ctrl_write_masked(
        _self, 1, 1);
}`, { x: M + twoCol + 0.4, y: TOP, w: twoCol, size: 13, name: "c regs", h: 4.8 });
}

{
  const s = content("Lab 2: run it");
  const h = code(s, `cd labs/lab2
make regs     # SystemRDL -> pss/timer_regs_pkg.pss (checked in; needs peakrdl-pss)
make run`, { x: M, y: TOP - 0.1, w: W - 2 * M, size: 14, name: "run cmds" });
  drawDiagram(s, "lab2_trace", { x: M, y: TOP - 0.1 + h + 0.2, w: W - 2 * M, h: BOTTOM - (TOP + h + 0.1) });
}

{
  const s = content("Lab 2 exercises");
  txt(s, para([
    "**Change the register spec.** Add an `ovf` bit to `STATUS` in `rdl/timer.rdl` (bit 2, W1C: \"expired again while DONE was set\"). `make regs gen` and find `ovf` in every flavor. You edited no PSS.",
    "**Write a programming sequence.** Add `timer_ch_c::ack()` (read STATUS, clear DONE|OVF, return `ovf`) and `timer_c::periodic(int c, bit[32] ticks, int n)` → number of missed expiries. Export it.",
    "**Explain the trace.** Run `periodic(1, 20, 3)` and `periodic(1, 4, 2)`. Why does the second miss expiries? Which bus accesses come from `write_field`?",
  ], { numbered: true, space: 14 }), { x: M, y: TOP, w: W - 2 * M, h: 4.4, fontSize: 19 });
  txt(s, "Solution: `labs/lab2/solution`, run with `make run SOL=1`.",
    { x: M, y: 5.9, w: W - 2 * M, h: 0.5, color: C.accent4 });
}

// =====================================================================
// Wrap-up
// =====================================================================
sect("Wrap-up");
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: section });
  s.addText("Wrap-up", { placeholder: "title" });
  s.addText(para([
    "An **operation model** is PSS's device knowledge, separated from scenarios",
    "**Four parts:** export API, import API, initialization, state",
    "**pssc** turns one model into SV, C, C++ and Python, each idiomatic for its users",
    "**Register models** come from the register spec (SystemRDL → `peakrdl pss`)",
    "Today: **every team runs the same programming sequence**. Later: PSS tests reuse the same functions.",
  ], { space: 6 }).map((r) => (r.options.fontFace === MONO ? Object.assign(r, { options: Object.assign(r.options, { color: HEX.accent5, fontSize: 16 }) }) : r)),
  { placeholder: "body", fontSize: 18 });
}

// pptxgenjs writes an <a:pPr> before every run of a multi-run paragraph; the
// schema allows one, first. Keep the first and drop the rest.
async function dedupeParagraphProps(file) {
  const JSZip = require("jszip");
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const PPR = /<a:pPr\b[^>]*\/>|<a:pPr\b[^>]*>.*?<\/a:pPr>/g;
  let fixed = 0;
  for (const name of Object.keys(zip.files).filter((n) => /^ppt\/slides\/slide\d+\.xml$/.test(n))) {
    const xml = await zip.file(name).async("string");
    const out = xml.replace(/<a:p>.*?<\/a:p>/gs, (para) => {
      let seen = 0;
      return para.replace(PPR, (m) => (seen++ === 0 ? m : (fixed++, "")));
    });
    zip.file(name, out);
  }
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
  return fixed;
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  const n = await dedupeParagraphProps(OUT);
  console.log("wrote", OUT, `(${n} duplicate paragraph props removed)`);
})();

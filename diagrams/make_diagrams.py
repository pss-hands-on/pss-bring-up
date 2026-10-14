"""Generate the slide diagrams as SVG.  Run:  python3 make_diagrams.py

Each function writes one <name>.svg next to this script. The slides
(../slides.md) reference them by name.
"""
import os
from svg import Svg, INK, MUTED, MONO, SANS, PAL, dump

HERE = os.path.dirname(os.path.abspath(__file__))


def out(name):
    return os.path.join(HERE, name + ".svg")


# =====================================================================
# Intro
# =====================================================================

def integration_challenge():
    s = Svg(1200, 520)
    # SoC
    s.rect(640, 30, 530, 460, "hw", rx=16)
    s.text(905, 64, "SoC", 22, PAL["hw"][2], "middle", "bold")
    blocks = [("CPU core", 670, 90), ("Interconnect", 920, 90),
              ("DMA", 670, 200), ("Comm ctrl (UART/SPI)", 920, 200),
              ("Timer", 670, 310), ("Memory ctrl", 920, 310)]
    for name, x, y in blocks:
        s.box(x, y, 220, 80, name, role="hw", center=True, title_size=16)
    s.text(905, 440, "each block: complex to configure and operate,", 15,
           PAL["hw"][2], "middle", italic=True)
    s.text(905, 462, "alone and in combination", 15, PAL["hw"][2], "middle",
           italic=True)
    teams = [("SoC DV", "SystemVerilog / UVM", "sv"),
             ("Emulation", "C on core  +  SV", "cpp"),
             ("Firmware", "C, bare-metal", "c"),
             ("Post-silicon", "C / Python, lab", "py")]
    for i, (t, sub, role) in enumerate(teams):
        y = 40 + i * 115
        s.box(30, y, 300, 90, t, [sub], role=role, mono=False, size=15)
        s.line(330, y + 45, 636, 120 + i * 90, color=PAL[role][0])
    s.label(485, 25, "every team programs every block", 15, INK, weight="bold",
            bg=False)
    s.save(out("integration_challenge"))


def drift():
    s = Svg(1200, 520)
    s.box(840, 170, 300, 170, "DMA", [], role="hw", center=True, title_size=26)
    s.text(990, 290, "one device", 16, PAL["hw"][2], "middle", italic=True)
    seqs = [
        ("SoC DV", "sv", ["CSR.en  = 1", "SZ      = 64", "poll CSR.done"], None),
        ("Emulation", "cpp", ["SZ      = 64", "CSR.en  = 1", "poll CSR.done"], "order"),
        ("Firmware", "c", ["CSR     = 0x1  // prio=0!", "SZ      = 64", "wait IRQ"], "prio lost"),
        ("Post-silicon", "py", ["SZ      = 0x40", "CSR.en  = 1", "sleep(1ms)"], "no completion check"),
    ]
    for i, (t, role, lines, diff) in enumerate(seqs):
        y = 15 + i * 125
        s.box(30, y, 400, 110, t, lines, role=role, size=15, lh=22)
        s.line(430, y + 55, 836, 200 + i * 37, color=PAL[role][0])
        if diff:
            s.label(600, y + 50 + (i - 1.5) * 20, "≠ " + diff, 14, "#c53030",
                    weight="bold")
    s.text(990, 380, "4 teams → 4 sequences", 18, "#c53030", "middle", "bold")
    s.text(990, 405, "→ 4 different behaviors", 18, "#c53030", "middle", "bold")
    s.text(990, 450, "“Works in sim, fails on the board”", 16, MUTED,
           "middle", italic=True)
    s.save(out("drift"))


def pss_test_portability():
    s = Svg(1200, 470)
    # PSS scenario panel
    s.rect(20, 20, 560, 430, "pss", rx=16)
    s.text(300, 52, "PSS test description", 20, PAL["pss"][2], "middle", "bold")

    def bubble(x, y, name, rand, regs):
        s.rect(x, y, 230, 120, "note", rx=40)
        s.text(x + 115, y + 28, name, 17, INK, "middle", "bold", font=MONO)
        s.line(x + 20, y + 40, x + 210, y + 40, color="#cbd5e0", sw=1, arrow=False)
        s.text(x + 115, y + 64, rand, 14, "#2b6cb0", "middle", font=MONO)
        s.line(x + 20, y + 78, x + 210, y + 78, color="#cbd5e0", sw=1, dashed=True, arrow=False)
        s.text(x + 115, y + 102, regs, 14, "#9c4221", "middle", font=MONO)

    bubble(185, 75, "dma_xfer_a", "rand size, chan", "CSR, SZ, SRC, DST")
    bubble(45, 290, "uart_tx_a", "rand baud, len", "LCR, DLL, THR")
    bubble(325, 290, "tmr_wait_a", "rand ticks", "LOAD, CTRL, STS")
    s.line(270, 195, 170, 286)
    s.line(330, 195, 430, 286)
    s.text(300, 440, "decisions (random)  +  register programming", 14, MUTED, "middle",
           italic=True)
    # generator
    s.box(640, 190, 170, 80, "generator", role="tool", center=True, title_size=18)
    s.line(580, 230, 636, 230)
    outs = [("SV / UVM test", "sv"), ("C test on the core", "c"),
            ("C test in the lab", "py"), ("…", "env")]
    for i, (t, role) in enumerate(outs):
        y = 40 + i * 105
        s.box(880, y, 290, 80, t, role=role, center=True, title_size=17)
        s.line(810, 230, 876, y + 40, color=PAL[role][0])
    s.save(out("pss_test_portability"))


def two_pieces():
    s = Svg(1200, 380)
    s.rect(20, 20, 1160, 340, "note", rx=16)
    s.text(600, 56, "One action, two very different jobs", 20, INK, "middle", "bold")
    s.box(60, 90, 500, 240, "Scenario  (decide)", [
        "• what to do, in what order",
        "• random choices under constraints",
        "• resources, data flow, scheduling",
        "",
        "test-specific; changes per test",
    ], role="pss", mono=False, size=17, lh=30)
    s.box(640, 90, 500, 240, "Realization  (do)", [
        "• how to make the device do it",
        "• register/memory programming",
        "• waiting for completion, errors",
        "",
        "device-specific; same for everyone",
    ], role="hw", mono=False, size=17, lh=30)
    s.line(560, 210, 636, 210)
    s.label(598, 200, "calls", 14, MUTED, bg=False)
    s.save(out("two_pieces"))


def pss_elements():
    s = Svg(1200, 430)
    cols = [
        ("Component tree", "structure", "pss", [
            "component pss_top {",
            "  dma_c   dma;",
            "  uart_c  uart[2];",
            "  timer_c tmr;",
            "}",
        ]),
        ("Actions", "scenario: flow + choices", "pss", [
            "action dma_xfer_a {",
            "  input  buf_s src;",
            "  output buf_s dst;",
            "  lock   chan_r ch;",
            "  rand bit[16] size;",
            "}",
        ]),
        ("Procedural code", "realization", "hw", [
            "exec body {",
            "  comp.regs.sz.write_val(size);",
            "  comp.regs.csr",
            "      .write_field(\"en\", 1);",
            "  plat_wait_irq();",
            "}",
        ]),
    ]
    notes = [["provides structure: instances,", "resources, register banks"],
             ["data-flow + resource relationships;", "make the random choices"],
             ["carries out decisions: calls", "functions, touches registers"]]
    for i, (t, sub, role, code) in enumerate(cols):
        x = 20 + i * 395
        s.box(x, 20, 370, 390, None, role=role)
        s.text(x + 185, 56, t, 20, PAL[role][2], "middle", "bold")
        s.text(x + 185, 80, sub, 15, PAL[role][2], "middle", italic=True)
        for j, ln in enumerate(code):
            s.text(x + 20, 125 + j * 26, ln, 15, INK, font=MONO)
        s.line(x + 20, 300, x + 350, 300, color=PAL[role][0], sw=1, arrow=False, opacity=0.4)
        for j, ln in enumerate(notes[i]):
            s.text(x + 20, 330 + j * 24, ln, 15, PAL[role][2])
    s.save(out("pss_elements"))


def adoption_gap():
    s = Svg(1200, 400)
    s.text(600, 34, "Who needs device-programming content?", 20, INK, "middle", "bold")
    segs = [("PSS tests", 230, "pss"), ("UVM sequences", 210, "sv"),
            ("firmware / drivers", 260, "c"), ("emulation bring-up", 200, "cpp"),
            ("lab scripts", 200, "py")]
    x = 40
    for t, w, role in segs:
        s.rect(x, 60, w, 80, role, rx=6)
        s.text(x + w / 2, 107, t, 16, PAL[role][2], "middle", "bold")
        x += w + 4
    # brace over PSS tests
    s.path("M40,160 L40,175 L270,175 L270,160", color="#2b6cb0", arrow=False)
    s.text(155, 200, "where PSS adoption", 15, "#2b6cb0", "middle", "bold")
    s.text(155, 220, "usually stops", 15, "#2b6cb0", "middle", "bold")
    s.path("M274,160 L274,175 L1150,175 L1150,160", color="#c53030", arrow=False)
    s.text(712, 200, "need the same device knowledge — but aren’t “tests”", 15,
           "#c53030", "middle", "bold")
    rows = [("Adopting PSS for tests requires…", [
                "PSS as the test-description language",
                "PSS content for every device a test touches",
                "…and actually writing tests"], "pss", 40),
            ("…but in practice", [
                "mission-mode firmware exercises the design — not a test",
                "teams can’t (yet) write full tests in PSS",
                "PSS doesn’t exist for every device"], "warn", 610)]
    for t, lines, role, x0 in rows:
        s.box(x0, 245, 550, 140, t, ["• " + ln for ln in lines], role=role,
              mono=False, size=15, lh=26)
    s.save(out("adoption_gap"))


def scenario_split():
    s = Svg(1200, 470)
    s.text(270, 32, "Before: one action does both", 18, INK, "middle", "bold")
    s.text(870, 32, "After: realization moves to the component", 18, INK, "middle", "bold")
    before = [
        "action xfer_a {",
        "  rand bit[16] size;",
        "  constraint size in [1..4096];",
        "  exec body {",
        "    comp.regs.sz.write_val(size);",
        "    comp.regs.csr",
        "      .write_field(\"en\", 1);",
        "    while (!done) { ... }",
        "  }",
        "}",
    ]
    s.box(20, 50, 500, 330, None, role="pss")
    for j, ln in enumerate(before):
        color = "#9c4221" if 4 <= j <= 7 else INK
        s.text(40, 85 + j * 28, ln, 16, color, font=MONO)
    s.rect(30, 177, 480, 118, "hw", rx=6, dashed=True, fill="none")
    s.line(540, 250, 610, 250, sw=3)
    after_a = [
        "action xfer_a {",
        "  rand bit[16] size;",
        "  constraint size in [1..4096];",
        "  exec body {",
        "    comp.transfer(size);",
        "  }",
        "}",
    ]
    s.box(630, 50, 550, 210, None, role="pss")
    s.text(1170, 72, "scenario", 14, PAL["pss"][0], "end", italic=True)
    for j, ln in enumerate(after_a):
        s.text(650, 85 + j * 25, ln, 16, INK, font=MONO)
    after_c = [
        "component dma_c {",
        "  target function void transfer(bit[16] sz) {",
        "    regs.sz.write_val(sz);",
        "    regs.csr.write_field(\"en\", 1);",
        "    while (!done) { ... }",
        "  }",
        "}",
    ]
    s.box(630, 280, 550, 180, None, role="hw")
    s.text(1170, 302, "realization → operation model", 14, PAL["hw"][0], "end",
           italic=True)
    for j, ln in enumerate(after_c):
        s.text(650, 315 + j * 22, ln, 15, INK, font=MONO)
    s.path("M840,196 C900,230 900,250 860,312", color=PAL["hw"][0])
    s.label(925, 245, "calls", 14, PAL["hw"][0], bg=False)
    s.save(out("scenario_split"))


def op_model_fanout():
    s = Svg(1200, 470)
    s.box(20, 150, 340, 170, "PSS operation model", [
        "component tree",
        "+ functions (operations)",
        "+ register model",
    ], role="pss", mono=False, size=16, lh=26, title_size=19)
    s.box(420, 195, 140, 80, "pssc", role="tool", center=True, title_size=20)
    s.line(360, 235, 416, 235, sw=3)
    outs = [("SystemVerilog classes", "UVM sequences, tests", "sv"),
            ("C functions", "firmware, emulation, post-si", "c"),
            ("C++ classes", "host models, SystemC", "cpp"),
            ("Python module", "lab scripts, cocotb", "py")]
    for i, (t, sub, role) in enumerate(outs):
        y = 15 + i * 100
        s.box(640, y, 330, 80, t, [sub], role=role, mono=False, size=15)
        s.line(560, 235, 636, y + 40, color=PAL[role][0])
    s.box(640, 420 - 10, 330, 50, "PSS scenarios — call it directly", role="pss",
          center=True, title_size=15, dashed=True)
    s.path("M190,320 C190,440 400,435 636,435", color=PAL["pss"][0], dashed=True)
    s.text(1000, 175, "one source", 17, INK, "start", "bold")
    s.text(1000, 200, "of truth for", 17, INK, "start", "bold")
    s.text(1000, 225, "“how to drive", 17, INK, "start", "bold")
    s.text(1000, 250, "this device”", 17, INK, "start", "bold")
    s.save(out("op_model_fanout"))


# =====================================================================
# Operation-model anatomy
# =====================================================================

def anatomy():
    s = Svg(1200, 520)
    s.rect(15, 15, 1170, 490, "env", rx=18, dashed=True)
    s.text(40, 48, "Environment  (UVM test · firmware · Python script)", 18,
           PAL["env"][2], weight="bold")
    # model
    s.rect(380, 90, 440, 330, "pss", rx=16)
    s.text(600, 124, "Operation-model instance", 20, PAL["pss"][2], "middle", "bold")
    s.box(410, 145, 380, 70, "State", ["base addresses, ids, config"],
          role="note", mono=False, size=15)
    s.box(410, 228, 380, 70, "Initialization", ["initialize(base) — bind state"],
          role="note", mono=False, size=15)
    s.box(410, 311, 380, 90, "Operations", ["functions on the component tree,",
          "registers, polling loops"], role="note", mono=False, size=15)
    # left: factory + export
    s.box(40, 110, 270, 90, "Factory / ctor", ["create + initialize", "returns the API handle"],
          role="sv", mono=False, size=15)
    s.line(310, 160, 406, 262, color=PAL["sv"][0], sw=3)
    s.box(40, 280, 270, 110, "Export API", ["perform an operation", "notify an event (IRQ)"],
          role="sv", mono=False, size=15)
    s.line(310, 335, 406, 355, color=PAL["sv"][0], sw=3)
    s.label(175, 420, "env \u2192 model", 14, PAL["sv"][0], weight="bold")
    # right: import
    s.box(890, 110, 270, 110, "Import API", ["memory: read32 / write32", "platform: delay, yield, msg"],
          role="c", mono=False, size=15)
    s.line(794, 355, 886, 175, color=PAL["c"][0], sw=3)
    s.label(850, 225, "model → env", 14, PAL["c"][0], weight="bold")
    s.box(890, 270, 270, 90, "Your implementation", ["bus agent / pointer /", "fake device"],
          role="env", mono=False, size=15)
    s.line(1025, 220, 1025, 266, color=PAL["env"][0])
    s.text(600, 460, "The model holds device knowledge; the environment holds everything else.",
           16, INK, "middle", italic=True)
    s.save(out("anatomy"))


def sv_mapping():
    s = Svg(1200, 500)

    def cls(x, y, w, h, kind, name, members, role):
        s.rect(x, y, w, h, role, rx=6)
        s.text(x + w / 2, y + 22, kind, 13, PAL[role][2], "middle", italic=True)
        s.text(x + w / 2, y + 44, name, 17, PAL[role][2], "middle", "bold", font=MONO)
        s.line(x, y + 56, x + w, y + 56, color=PAL[role][0], sw=1, arrow=False)
        for j, m in enumerate(members):
            s.text(x + 12, y + 80 + j * 22, m, 14, INK, font=MONO)

    cls(30, 30, 360, 140, "interface class — EXPORT API", "soc_c_ctxt_if",
        ["task delay_ticks(int t,", "                 bit[31:0] ticks);"], "sv")
    cls(810, 30, 360, 140, "interface class — IMPORT API", "soc_c_imp_if",
        ["extends pss_mem_if  // read32/write32..", "task plat_delay_us(int us);"], "c")
    cls(380, 250, 440, 160, "factory + root context", "soc_c_root #(Timp)",
        ["static function soc_c_ctxt_if", "  create(Timp imp, addr_handle_t base);",
         "protected soc_c pss_root;  // the STATE", "protected Timp  pss_imp;"], "pss")
    cls(880, 300, 290, 110, "your class", "my_imp", ["implements soc_c_imp_if"], "env")
    cls(30, 300, 290, 110, "generated component", "soc_c", ["timer_c tmr[2];", "task delay_ticks(...)"], "note")
    # relationships
    s.path("M520,250 L300,172", color=PAL["sv"][0], dashed=True)
    s.label(400, 225, "implements", 13, PAL["sv"][0])
    s.path("M680,250 L900,172", color=PAL["c"][0], dashed=True)
    s.label(800, 225, "implements", 13, PAL["c"][0])
    s.line(1025, 300, 1025, 174, color=PAL["env"][0], dashed=True)
    s.label(1025, 245, "implements", 13, PAL["env"][0])
    s.line(380, 355, 324, 355, color=MUTED)
    s.label(352, 345, "owns", 13, MUTED, bg=False)
    s.line(820, 355, 876, 355, color=MUTED)
    s.label(848, 345, "calls", 13, MUTED, bg=False)
    s.text(600, 460, "create() builds the tree, runs initialize(), returns the export handle.",
           16, INK, "middle", italic=True)
    s.text(600, 485, "The handle IS the state — one per device instance.", 16, INK, "middle",
           italic=True)
    s.save(out("sv_mapping"))


def c_mapping():
    s = Svg(1200, 440)
    s.box(30, 30, 520, 180, "State: complete struct types", [
        "typedef struct timer_c {",
        "    int         id;",
        "    pssc_addr_t base;",
        "} timer_c;",
        "typedef struct soc_c { timer_c tmr[2]; } soc_c;",
    ], role="pss", size=14, lh=24)
    s.box(30, 240, 520, 180, "Export API + lifecycle", [
        "void soc_init(soc_c *_self, pssc_addr_t base);",
        "void soc_delay_ticks(soc_c *_self, int t,",
        "                     uint32_t ticks);",
        "void timer_start(timer_c *_self, uint32_t ticks);",
        "   →  <prefix>_<function>(self, ...)",
    ], role="sv", size=14, lh=24)
    s.box(650, 30, 520, 130, "Import API: model imports", [
        "/* named exactly as the model names them */",
        "void plat_delay_us(int us);",
        "/* + pssc_message() if the model reports */",
    ], role="c", size=14, lh=26)
    s.box(650, 190, 520, 230, "Import API: memory seam (pick one)", [
        "--mem-access pointer    *(volatile u32*)a",
        "--mem-access functions  pssc_mem_read32(a)",
        "--link-style vtable     bus->read32(ctx,a)",
        "",
        "--lifecycle static      no malloc",
        "--addr-bits 32          narrower handles",
    ], role="c", size=14, lh=26)
    s.save(out("c_mapping"))


# =====================================================================
# Lab 1
# =====================================================================

def lab1_model():
    s = Svg(1200, 500)
    # device memory map
    s.rect(900, 30, 270, 440, "hw", rx=10)
    s.text(1035, 60, "Device @ 0x4000_0000", 16, PAL["hw"][2], "middle", "bold")
    for k, (off, nm) in enumerate([("+0x000", "timer 0"), ("+0x100", "timer 1")]):
        y = 85 + k * 190
        s.rect(920, y, 230, 170, "note", rx=6)
        s.text(935, y + 26, f"{off}  {nm}", 15, INK, weight="bold", font=MONO)
        for j, r in enumerate(["0x0 CTRL   EN, IRQ_EN", "0x4 LOAD", "0x8 STATUS DONE (W1C)"]):
            s.text(935, y + 60 + j * 32, r, 13, INK, font=MONO)
    # component tree
    s.box(30, 30, 380, 190, "soc_c  (root)", [
        "timer_c tmr[2];",
        "",
        "initialize(base)",
        "delay_ticks(t, ticks)   export",
    ], role="pss", size=15, lh=26)
    s.box(30, 270, 380, 200, "timer_c", [
        "int id;  addr_handle_t base;",
        "",
        "initialize(i, b)",
        "start(ticks)",
        "is_done() -> bool",
        "wait_done(poll_us)",
    ], role="pss", size=15, lh=24)
    s.line(220, 220, 220, 266)
    s.label(220, 248, "tmr[0], tmr[1]", 13, MUTED, font=MONO)
    s.box(490, 360, 330, 110, "plat_pkg", ["import target function", "  void plat_delay_us(int us);"],
          role="c", size=14, lh=24)
    s.line(410, 440, 486, 420, color=PAL["c"][0])
    s.label(448, 455, "calls", 13, PAL["c"][0], bg=False)
    s.line(410, 330, 916, 160, color=PAL["hw"][0], dashed=True)
    s.label(660, 238, "write32 / read32 (base + off)", 13, PAL["hw"][0], font=MONO)
    s.line(410, 110, 916, 110, color=PAL["hw"][0], dashed=True)
    s.label(660, 104, "initialize: base + i*0x100", 13, PAL["hw"][0], font=MONO)
    s.save(out("lab1_model"))


def pssc_flow():
    s = Svg(1200, 470)
    s.box(20, 140, 260, 180, "PSS sources", [
        "plat_pkg.pss",
        "timer_c.pss",
        "soc_c.pss",
        "(dependency order!)",
    ], role="pss", size=15, lh=26)
    s.rect(330, 175, 270, 110, "tool", rx=10)
    s.text(465, 210, "pssc compile", 19, "#ffffff", "middle", "bold", font=MONO)
    s.text(465, 238, "--root soc_c", 15, "#e2e8f0", "middle", font=MONO)
    s.text(465, 262, "-t op-model-<flavor>", 15, "#e2e8f0", "middle", font=MONO)
    s.line(280, 230, 326, 230, sw=3)
    outs = [("op-model-sv", "soc_c_pkg.sv (+ .svh)", "pssc_reg_pkg.sv", "sv"),
            ("op-model-c", "soc.h  soc.c  soc_regs.h", "pssc_mem*.h  pssc_env.h", "c"),
            ("op-model-cpp", "soc.hpp", "pssc_reg.hpp  pssc_env.hpp", "cpp"),
            ("op-model-py", "soc.py", "pssc_rt.py", "py")]
    for i, (t, f1, f2, role) in enumerate(outs):
        y = 15 + i * 112
        s.box(680, y, 490, 96, None, role=role)
        s.text(695, y + 28, t, 17, PAL[role][2], weight="bold", font=MONO)
        s.text(695, y + 56, f1, 15, INK, font=MONO)
        s.text(695, y + 80, f2 + "   (runtime core)", 14, MUTED, font=MONO)
        s.line(600, 230, 676, y + 48, color=PAL[role][0])
    s.save(out("pssc_flow"))


def lab1_sequence():
    s = Svg(1200, 560)
    cols = [("test code", 110, "env"), ("soc_c", 380, "pss"), ("tmr[1]", 620, "pss"),
            ("environment (imports)", 960, "c")]
    for name, x, role in cols:
        w = 220 if len(name) > 10 else 150
        s.box(x - w / 2, 15, w, 44, name, role=role, center=True, title_size=16)
        s.line(x, 59, x, 545, color="#cbd5e0", dashed=True, arrow=False)

    def msg(x1, x2, y, t, color=INK, dashed=False):
        s.line(x1, y, x2, y, color=color, dashed=dashed)
        s.label((x1 + x2) / 2, y - 7, t, 14, color, font=MONO)

    msg(110, 380, 95, "delay_ticks(1, 35)")
    msg(380, 620, 135, "start(35)")
    for j, t in enumerate(["write32(+0x108, 1)", "write32(+0x104, 35)", "write32(+0x100, 1)"]):
        msg(620, 960, 175 + j * 36, t, PAL["c"][0])
    msg(380, 620, 300, "wait_done(10)")
    # loop frame
    s.rect(560, 320, 560, 160, "note", rx=4, dashed=True, fill="none")
    s.text(572, 340, "loop  while !is_done()", 14, MUTED, weight="bold", font=MONO)
    msg(620, 960, 375, "read32(+0x108)", PAL["c"][0])
    msg(960, 620, 410, "DONE = 0", MUTED, dashed=True)
    msg(620, 960, 455, "plat_delay_us(10)", PAL["c"][0])
    msg(960, 620, 510, "DONE = 1  → return", MUTED, dashed=True)
    msg(380, 110, 535, "return", MUTED, dashed=True)
    s.save(out("lab1_sequence"))


# =====================================================================
# Lab 2
# =====================================================================

def reg_flow():
    s = Svg(1200, 470)
    s.box(20, 160, 200, 140, "timer.rdl", ["SystemRDL", "(or IP-XACT →", " RDL, Rubix…)"],
          role="hw", mono=False, size=15)
    s.rect(270, 190, 230, 80, "tool", rx=10)
    s.text(385, 223, "peakrdl pss", 18, "#ffffff", "middle", "bold", font=MONO)
    s.text(385, 250, "--pad-tail", 14, "#e2e8f0", "middle", font=MONO)
    s.line(220, 230, 266, 230, sw=3)
    s.box(550, 120, 300, 220, "timer_regs_pkg.pss", [
        "struct ..._s : packed_s<>",
        "  (field layout)",
        "component ..._c : reg_c<>",
        "  (one register)",
        "component ..._c : reg_group_c",
        "  (bank + offsets)",
    ], role="pss", size=14, lh=24)
    s.line(500, 230, 546, 230, sw=3)
    s.box(900, 30, 280, 90, "imported by", ["timer_ch_c.pss", "timer_c.pss"], role="pss", size=14)
    s.line(850, 180, 896, 80)
    s.box(900, 170, 280, 120, "pssc  →", ["SV: reg_c #(struct)", "C:  bitfield unions", "Py: _RegValue classes"],
          role="tool", size=14)
    s.rect(900, 170, 280, 120, "tool")
    s.text(915, 197, "pssc →", 17, "#ffffff", weight="bold")
    for j, t in enumerate(["SV: reg_c #(struct)", "C:  bitfield unions", "Py: _RegValue classes"]):
        s.text(915, 225 + j * 22, t, 14, "#e2e8f0", font=MONO)
    s.line(850, 230, 896, 230, sw=3)
    s.box(900, 330, 280, 120, "same RDL also feeds", ["RTL (peakrdl-regblock)", "UVM RAL (peakrdl-uvm)",
          "docs (peakrdl-html)"], role="note", mono=False, size=14, lh=24)
    s.path("M120,300 C120,420 600,420 896,400", color=MUTED, dashed=True, marker="ahm")
    s.label(500, 400, "one register spec, many consumers", 14, MUTED)
    s.save(out("reg_flow"))


def reg_anatomy():
    s = Svg(1200, 520)
    # bit field diagram
    s.text(30, 36, "struct timer_ch_regs__ctrl_s : packed_s<LITTLE_ENDIAN>", 16, INK,
           weight="bold", font=MONO)
    fields = [("rsvd_8", 31, 8, 420, "note"), ("prescale", 7, 4, 220, "pss"),
              ("rsvd", 3, 3, 90, "note"), ("mode", 2, 2, 110, "pss"),
              ("irq_en", 1, 1, 110, "pss"), ("en", 0, 0, 110, "pss")]
    x = 30
    for nm, hi, lo, w, role in fields:
        s.rect(x, 52, w, 56, role, rx=0, sw=1.5)
        s.text(x + w / 2, 86, nm, 15, PAL[role][2], "middle", "bold", font=MONO)
        s.text(x + 4, 126, str(hi), 12, MUTED, font=MONO)
        if hi != lo:
            s.text(x + w - 4, 126, str(lo), 12, MUTED, "end", font=MONO)
        x += w
    s.text(x + 10, 86, "← field layout", 14, MUTED, italic=True)
    # reg_c
    s.box(30, 160, 540, 150, "pure component timer_ch_regs__ctrl_c", [
        "  : reg_c<timer_ch_regs__ctrl_s, READWRITE, 32> {}",
        "",
        "read()  write(v)  write_masked(m, v)",
        "read_val()  write_val(raw)  write_field(\"en\", 1)",
    ], role="pss", size=14, lh=24, title_size=15)
    s.text(580, 200, "← one register:", 14, MUTED, italic=True)
    s.text(580, 220, "   value type + access + width", 14, MUTED, italic=True)
    # reg_group
    s.box(30, 340, 540, 160, "pure component timer_ch_regs_c : reg_group_c", [
        "timer_ch_regs__ctrl_c   ctrl;     // @0x0",
        "timer_ch_regs__load_c   load;     // @0x4",
        "timer_ch_regs__status_c status;   // @0x8",
        "timer_ch_regs__count_c  count;    // @0xC",
        "get_offset_of_instance(\"load\") → 0x4",
    ], role="pss", size=14, lh=23, title_size=15)
    s.text(580, 380, "← a bank: registers + offsets", 14, MUTED, italic=True)
    # usage
    s.box(820, 160, 350, 340, "In the operation model", [
        "component timer_ch_c {",
        "  timer_ch_regs_c regs;",
        "",
        "  init: regs.set_handle(h);",
        "",
        "  regs.load.write_val(t);",
        "  sts = regs.status.read();",
        "  if (sts.done == 1) ...",
        "  regs.ctrl",
        "    .write_field(\"en\", 1);",
        "}",
    ], role="hw", size=14, lh=25, title_size=16)
    s.save(out("reg_anatomy"))


def address_binding():
    s = Svg(1200, 480)
    # memory map
    s.rect(830, 20, 340, 440, "hw", rx=10)
    s.text(1000, 50, "address map", 16, PAL["hw"][2], "middle", "bold")
    rows = [("0x4000_0000", "ID", 70), ("0x4000_0100", "ch[0]  CTRL LOAD STATUS COUNT", 160),
            ("0x4000_0200", "ch[1]  CTRL LOAD STATUS COUNT", 300)]
    for a, t, y in rows:
        h = 60 if t == "ID" else 120
        s.rect(850, y, 300, h, "note", rx=4)
        s.text(860, y + 22, a, 14, PAL["hw"][2], weight="bold", font=MONO)
        parts = t.split("  ")
        s.text(860, y + 46, parts[0], 14, INK, font=MONO)
        if len(parts) > 1:
            s.text(860, y + 72, parts[1], 13, MUTED, font=MONO)
    code = [
        "solve function void initialize(addr_handle_t base) {",
        "    regs.set_handle(base);",
        "    foreach (ch[i]) {",
        "        ch[i].initialize(i,",
        "            make_handle_from_handle(base,",
        "                regs.get_offset_of_instance_array(\"ch\", i)));",
        "    }",
        "}",
    ]
    s.box(20, 20, 760, 270, "timer_c::initialize", [], role="pss")
    for j, ln in enumerate(code):
        s.text(40, 80 + j * 26, ln, 15, INK, font=MONO)
    s.line(780, 100, 846, 100, color=PAL["hw"][0])
    s.line(780, 205, 846, 220, color=PAL["hw"][0])
    s.line(780, 215, 846, 360, color=PAL["hw"][0])
    s.box(20, 320, 760, 140, "Why per-channel components?", [
        "• each channel binds its own bank → operations are index-free",
        "• offsets come from the generated group → stated once, in the RDL",
        "• pssc folds the offset to a constant: base + 0x100 + 0x100*i",
    ], role="note", mono=False, size=16, lh=28)
    s.save(out("address_binding"))


def rmw():
    s = Svg(1200, 470)
    s.text(30, 34, "What reaches the bus", 20, INK, weight="bold")
    rows = [
        ("regs.load.write(v)", [("W", "LOAD = v")], "whole register, one write"),
        ("regs.load.write_val(0x19)", [("W", "LOAD = 0x19")], "raw value, one write"),
        ("regs.status.read()", [("R", "STATUS")], "one read → struct"),
        ("regs.ctrl.write_field(\"en\", 1)", [("R", "CTRL"), ("W", "CTRL | en")],
         "read-modify-write (LRM §21.14.1)"),
        ("regs.ctrl.write_masked(m, v)", [("R", "CTRL"), ("W", "(cur&~m)|(v&m)")],
         "read-modify-write"),
    ]
    for i, (call, ops, note) in enumerate(rows):
        y = 60 + i * 72
        s.text(30, y + 32, call, 16, INK, font=MONO)
        x = 470
        for k, (rw, t) in enumerate(ops):
            role = "c" if rw == "R" else "sv"
            s.rect(x, y + 8, 200, 38, role, rx=6)
            s.text(x + 12, y + 33, rw, 16, PAL[role][0], weight="bold", font=MONO)
            s.text(x + 34, y + 33, t, 14, INK, font=MONO)
            if k == 0 and len(ops) > 1:
                s.line(x + 200, y + 27, x + 226, y + 27)
            x += 230
        s.text(940, y + 32, note, 14, MUTED, italic=True)
    s.box(30, 425 - 10, 1140, 50, None, role="warn")
    s.text(50, 446, "A field write still READS the register. If a read has side effects "
           "(clear-on-read), that matters.", 15, PAL["warn"][2], weight="bold")
    s.save(out("rmw"))


def lab2_trace():
    s = Svg(1200, 430)
    s.text(30, 32, "one_shot(0, 25) — identical in C, SystemVerilog and Python", 18, INK,
           weight="bold")
    trace = [
        ("W", "ch0.LOAD   = 0x19", "configure: load.write()", "sv"),
        ("W", "ch0.CTRL   = 0x00", "configure: ctrl.write() (EN=0)", "sv"),
        ("W", "ch0.STATUS = 0x01", "start: clear DONE (W1C)", "sv"),
        ("R", "ch0.CTRL   -> 0x00", "start: write_field(\"en\",1) — read…", "c"),
        ("W", "ch0.CTRL   = 0x01", "…modify, write", "sv"),
        ("R", "ch0.STATUS -> 0x02", "wait_done: BUSY", "c"),
        ("R", "ch0.STATUS -> 0x02", "  (plat_delay_us between polls)", "c"),
        ("R", "ch0.STATUS -> 0x02", "", "c"),
        ("R", "ch0.STATUS -> 0x01", "DONE → return", "c"),
    ]
    for i, (rw, t, note, role) in enumerate(trace):
        y = 50 + i * 40
        s.rect(30, y, 460, 32, role, rx=4, sw=1.5)
        s.text(44, y + 22, rw, 15, PAL[role][0], weight="bold", font=MONO)
        s.text(70, y + 22, t, 15, INK, font=MONO)
        if note:
            s.text(510, y + 22, note, 15, MUTED, italic=True)
    s.save(out("lab2_trace"))


ALL = [integration_challenge, drift, pss_test_portability, two_pieces, pss_elements,
       adoption_gap, scenario_split, op_model_fanout, anatomy, sv_mapping, c_mapping,
       lab1_model, pssc_flow, lab1_sequence, reg_flow, reg_anatomy, address_binding,
       rmw, lab2_trace]

if __name__ == "__main__":
    for f in ALL:
        f()
        print("wrote", f.__name__ + ".svg")
    dump(os.path.join(HERE, "diagrams.json"))   # primitives for ../pptx/build_deck.js
    print("wrote diagrams.json")

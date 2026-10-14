"""Lab 2 -- Python environment for the timer operation model."""
from timer import Timer

BASE = 0x4000_0000
REG = {0x0: "CTRL", 0x4: "LOAD", 0x8: "STATUS", 0xC: "COUNT"}


class FakeTimer:
    """Register-accurate fake: ID, and per channel CTRL/LOAD/STATUS/COUNT."""

    def __init__(self):
        self.ch = [dict(ctrl=0, load=0, done=0, count=0) for _ in range(2)]
        self.polls = 0

    def _decode(self, addr):
        off = addr - BASE
        return (None, "ID") if off < 0x100 else ((off >> 8) - 1, REG[off & 0xFF])

    def write32(self, addr, data):
        c, r = self._decode(addr)
        print(f"  [bus] W ch{c}.{r:<6} = {data:#010x}")
        ch = self.ch[c]
        if r == "CTRL":
            if data & 1 and not ch["ctrl"] & 1:
                ch["count"] = ch["load"]           # rising EN loads COUNT
            ch["ctrl"] = data
        elif r == "LOAD":
            ch["load"] = data
        elif r == "STATUS" and data & 1:
            ch["done"] = 0                         # write-1-to-clear

    def read32(self, addr):
        c, r = self._decode(addr)
        if c is None:
            v = 0x0001_7A11
        else:
            ch = self.ch[c]
            v = {"CTRL": ch["ctrl"], "LOAD": ch["load"],
                 "STATUS": ch["done"] | ((ch["ctrl"] & 1) << 1),
                 "COUNT": ch["count"]}[r]
        print(f"  [bus] R {'ID' if c is None else f'ch{c}.{r}':<10} -> {v:#010x}")
        return v

    def plat_delay_us(self, us):
        self.polls += 1
        for ch in self.ch:
            if ch["ctrl"] & 1:
                ch["count"] = max(ch["count"] - us, 0)
                if ch["count"] == 0:
                    ch["done"] = 1
                    if ch["ctrl"] & 4:
                        ch["count"] = ch["load"]   # periodic
                    else:
                        ch["ctrl"] &= ~1           # one-shot


env = FakeTimer()
tmr = Timer(env, BASE)

print("probe()")
assert tmr.probe(), "no timer at BASE"

print("one_shot(0, 25)")
tmr.one_shot(0, 25)
print(f"done after {env.polls} polls")

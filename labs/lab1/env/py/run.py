"""Lab 1 -- Python environment for the soc_c operation model.

The generated `Soc` takes ONE object that supplies everything the model
imports: memory access (read32/write32) and the model's own imports
(plat_delay_us). It is a Protocol -- nothing needs to inherit anything.
"""
from soc import Soc

BASE = 0x4000_0000


class FakeSoc:
    """Two fake timers at BASE + n*0x100, driven by plat_delay_us()."""

    def __init__(self):
        self.tmr = [dict(en=0, load=0, done=0, elapsed=0) for _ in range(2)]
        self.polls = 0

    def _decode(self, addr):
        off = addr - BASE
        return self.tmr[off >> 8], off & 0xff

    # --- memory access ---
    def write32(self, addr, data):
        print(f"  [bus] write32 {addr:#010x} = {data:#x}")
        t, reg = self._decode(addr)
        if reg == 0x0:
            t["en"], t["elapsed"] = data & 1, 0
        elif reg == 0x4:
            t["load"] = data
        elif reg == 0x8 and data & 1:
            t["done"] = 0

    def read32(self, addr):
        t, reg = self._decode(addr)
        return t["done"] if reg == 0x8 else 0

    # --- the model's import ---
    def plat_delay_us(self, us):
        self.polls += 1
        for t in self.tmr:
            if t["en"]:
                t["elapsed"] += us
                if t["elapsed"] >= t["load"]:
                    t["done"], t["en"] = 1, 0


env = FakeSoc()
soc = Soc(env, BASE)

print("delay_ticks(1, 35)")
soc.delay_ticks(1, 35)
print(f"done after {env.polls} polls")

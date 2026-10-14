/* Lab 1 -- C environment for the soc_c operation model.
 *
 * The environment supplies two things the generated code imports:
 *   1. memory access   -- pssc_mem_read32/write32 (--mem-access functions)
 *   2. model imports   -- plat_delay_us()
 * Here both drive a tiny fake timer, so the harness runs on a laptop.
 * On silicon, (1) is a pointer dereference and (2) is a busy-wait.
 */
#include <stdio.h>
#include "soc.h"

/* ---- A fake device: two timers at BASE + n*0x100 ---------------------- */
#define BASE 0x40000000u
static struct { uint32_t en, load, done, elapsed; } tmr[2];
static unsigned n_polls;

static int decode(pssc_addr_t a, unsigned *reg) {
    unsigned off = (unsigned)(a - BASE);
    *reg = off & 0xff;
    return (int)(off >> 8);
}

void pssc_mem_write32(pssc_addr_t a, uint32_t d) {
    unsigned reg; int t = decode(a, &reg);
    printf("  [bus] write32 0x%08llx = 0x%x\n", (unsigned long long)a, d);
    switch (reg) {
    case 0x0: tmr[t].en = d & 1; tmr[t].elapsed = 0; break;
    case 0x4: tmr[t].load = d; break;
    case 0x8: if (d & 1) tmr[t].done = 0; break;
    }
}
uint32_t pssc_mem_read32(pssc_addr_t a) {
    unsigned reg; int t = decode(a, &reg);
    return (reg == 0x8) ? tmr[t].done : 0;
}
/* Unused widths still need a definition: the seam declares them all. */
void     pssc_mem_write8 (pssc_addr_t a, uint8_t  d) { (void)a; (void)d; }
uint8_t  pssc_mem_read8  (pssc_addr_t a) { (void)a; return 0; }
void     pssc_mem_write16(pssc_addr_t a, uint16_t d) { (void)a; (void)d; }
uint16_t pssc_mem_read16 (pssc_addr_t a) { (void)a; return 0; }
void     pssc_mem_write64(pssc_addr_t a, uint64_t d) { (void)a; (void)d; }
uint64_t pssc_mem_read64 (pssc_addr_t a) { (void)a; return 0; }

/* ---- The model's import: advance device time -------------------------- */
void plat_delay_us(int us) {
    n_polls++;
    for (int t = 0; t < 2; t++) {
        if (!tmr[t].en) continue;
        tmr[t].elapsed += (uint32_t)us;
        if (tmr[t].elapsed >= tmr[t].load) { tmr[t].done = 1; tmr[t].en = 0; }
    }
}

void pssc_message(const char *fmt, ...) { (void)fmt; }

/* ---- The test: use the operation model -------------------------------- */
static soc_c soc;           /* --lifecycle static: no malloc */

int main(void) {
    soc_init(&soc, BASE);

    printf("delay_ticks(1, 35, 10)\n");
    printf("  -> %s\n", soc_delay_ticks(&soc, 1, 35, 10) ? "done" : "TIMEOUT");

    printf("delay_ticks(0, 1000, 5)\n");
    if (!soc_delay_ticks(&soc, 0, 1000, 5)) {
        printf("  -> TIMEOUT; cancel(0)\n");
        soc_cancel(&soc, 0);
    }
    printf("%u polls total\n", n_polls);
    return 0;
}

/* Lab 2 -- C environment for the timer operation model.
 *
 * Same seams as Lab 1: memory access + plat_delay_us(). The fake device is
 * now register-accurate: ID, and per channel CTRL / LOAD / STATUS / COUNT.
 */
#include <stdio.h>
#include "timer.h"

#define BASE 0x40000000u

/* ---- Fake device ------------------------------------------------------ */
static struct { uint32_t ctrl, load, done, count; } ch[2];
static unsigned n_polls;

static const char *reg_name(unsigned off) {
    static const char *n[] = { "CTRL", "LOAD", "STATUS", "COUNT" };
    return off < 0x100 ? "ID" : n[(off & 0xff) >> 2];
}

void pssc_mem_write32(pssc_addr_t a, uint32_t d) {
    unsigned off = (unsigned)(a - BASE), c = (off >> 8) - 1;
    printf("  [bus] W ch%u.%-6s = 0x%08x\n", c, reg_name(off), d);
    switch (off & 0xff) {
    case 0x0:   /* CTRL: rising EN loads COUNT */
        if ((d & 1) && !(ch[c].ctrl & 1)) ch[c].count = ch[c].load;
        ch[c].ctrl = d; break;
    case 0x4: ch[c].load = d; break;
    case 0x8: if (d & 1) ch[c].done = 0; break;   /* write-1-to-clear */
    }
}

uint32_t pssc_mem_read32(pssc_addr_t a) {
    unsigned off = (unsigned)(a - BASE), c = (off >> 8) - 1;
    uint32_t v = 0;
    if (off < 0x100)            v = 0x00017A11;   /* ID: rev 1, id 0x7A11 */
    else switch (off & 0xff) {
    case 0x0: v = ch[c].ctrl; break;
    case 0x4: v = ch[c].load; break;
    case 0x8: v = ch[c].done | ((ch[c].ctrl & 1) << 1); break;
    case 0xC: v = ch[c].count; break;
    }
    if (off < 0x100) printf("  [bus] R ID         -> 0x%08x\n", v);
    else             printf("  [bus] R ch%u.%-6s -> 0x%08x\n", c, reg_name(off), v);
    return v;
}
void     pssc_mem_write8 (pssc_addr_t a, uint8_t  d) { (void)a; (void)d; }
uint8_t  pssc_mem_read8  (pssc_addr_t a) { (void)a; return 0; }
void     pssc_mem_write16(pssc_addr_t a, uint16_t d) { (void)a; (void)d; }
uint16_t pssc_mem_read16 (pssc_addr_t a) { (void)a; return 0; }
void     pssc_mem_write64(pssc_addr_t a, uint64_t d) { (void)a; (void)d; }
uint64_t pssc_mem_read64 (pssc_addr_t a) { (void)a; return 0; }

/* Device time: each microsecond is one tick (prescale ignored). */
void plat_delay_us(int us) {
    n_polls++;
    for (int c = 0; c < 2; c++) {
        if (!(ch[c].ctrl & 1)) continue;
        ch[c].count = (ch[c].count > (uint32_t)us) ? ch[c].count - us : 0;
        if (ch[c].count == 0) {
            ch[c].done = 1;
            if (ch[c].ctrl & 4) ch[c].count = ch[c].load;   /* periodic */
            else                ch[c].ctrl &= ~1u;          /* one-shot */
        }
    }
}

void pssc_message(const char *fmt, ...) { (void)fmt; }

/* ---- The test --------------------------------------------------------- */
static timer_c tmr;

int main(void) {
    timer_init(&tmr, BASE);

    printf("probe()\n");
    if (!timer_probe(&tmr)) { printf("no timer at 0x%x\n", BASE); return 1; }

    printf("one_shot(0, 25)\n");
    timer_one_shot(&tmr, 0, 25);
    printf("done after %u polls\n", n_polls);
    return 0;
}

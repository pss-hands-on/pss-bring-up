// Lab 1 -- SystemVerilog environment for the soc_c operation model.
//
// The generated package gives you:
//   soc_c_imp_if   -- interface class: what YOU implement (memory + imports)
//   soc_c_ctxt_if  -- interface class: the operations YOU call
//   soc_c_root     -- factory: create(imp, base) returns a soc_c_ctxt_if
// In a UVM env, the imp class would start sequences on a register adapter;
// here it drives a fake timer directly.
import pssc_reg_pkg::*;
import soc_c_pkg::*;

class fake_soc_imp implements soc_c_imp_if;
  localparam bit [63:0] BASE = 64'h4000_0000;
  bit        en[2], done[2];
  bit [31:0] load[2], elapsed[2];
  int        polls;

  // --- memory access (pss_mem_if) ---
  virtual task write32(addr_handle_t addr, bit [31:0] data);
    int t = int'((addr - BASE) >> 8);
    $display("  [bus] write32 0x%08h = 0x%0h", addr, data);
    case ((addr - BASE) & 'hff)
      'h0: begin en[t] = data[0]; elapsed[t] = 0; end
      'h4: load[t] = data;
      'h8: if (data[0]) done[t] = 0;
    endcase
    #1ns;   // a bus transaction takes time
  endtask
  virtual task read32(addr_handle_t addr, output bit [31:0] data);
    int t = int'((addr - BASE) >> 8);
    data = (((addr - BASE) & 'hff) == 'h8) ? 32'(done[t]) : 0;
    #1ns;
  endtask
  virtual task write8 (addr_handle_t addr, bit [7:0]  data); endtask
  virtual task read8  (addr_handle_t addr, output bit [7:0]  data); data = 0; endtask
  virtual task write16(addr_handle_t addr, bit [15:0] data); endtask
  virtual task read16 (addr_handle_t addr, output bit [15:0] data); data = 0; endtask
  virtual task write64(addr_handle_t addr, bit [63:0] data); endtask
  virtual task read64 (addr_handle_t addr, output bit [63:0] data); data = 0; endtask

  // --- the model's import ---
  virtual task plat_delay_us(input int us);
    polls++;
    #(us * 1us);
    foreach (en[t]) if (en[t]) begin
      elapsed[t] += us;
      if (elapsed[t] >= load[t]) begin done[t] = 1; en[t] = 0; end
    end
  endtask
endclass

module tb;
  initial begin
    fake_soc_imp  imp = new();
    soc_c_ctxt_if soc = soc_c_root#(fake_soc_imp)::create(imp, 64'h4000_0000);

    $display("delay_ticks(1, 35)");
    soc.delay_ticks(1, 35);
    $display("done after %0d polls at %0t", imp.polls, $time);
    $finish;
  end
endmodule

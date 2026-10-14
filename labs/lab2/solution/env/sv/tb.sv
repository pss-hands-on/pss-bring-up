// Lab 2 -- SystemVerilog environment for the timer operation model.
//
// In a UVM environment, write32/read32 would run a uvm_reg_bus_op through
// the agent's sequencer (or a uvm_mem backdoor); plat_delay_us would wait
// on the clocking block. The model doesn't care which.
import pssc_reg_pkg::*;
import timer_c_pkg::*;

class fake_timer_imp implements timer_c_imp_if;
  localparam bit [63:0] BASE = 64'h4000_0000;
  bit [31:0] ctrl[2], load[2], count[2];
  bit        done[2], ovf[2];
  int        polls;

  function string name(bit [63:0] addr);
    string r[4] = '{"CTRL", "LOAD", "STATUS", "COUNT"};
    int off = int'(addr - BASE);
    if (off < 'h100) return "ID        ";
    return $sformatf("ch%0d.%-6s", (off >> 8) - 1, r[(off & 'hff) >> 2]);
  endfunction

  virtual task write32(addr_handle_t addr, bit [31:0] data);
    int off = int'(addr - BASE), c = (off >> 8) - 1;
    $display("  [bus] W %s = 0x%08h", name(addr), data);
    case (off & 'hff)
      'h0: begin if (data[0] && !ctrl[c][0]) count[c] = load[c]; ctrl[c] = data; end
      'h4: load[c] = data;
      'h8: begin if (data[0]) done[c] = 0; if (data[2]) ovf[c] = 0; end
    endcase
    #10ns;
  endtask

  virtual task read32(addr_handle_t addr, output bit [31:0] data);
    int off = int'(addr - BASE), c = (off >> 8) - 1;
    if (off < 'h100) data = 32'h0001_7A11;
    else case (off & 'hff)
      'h0: data = ctrl[c];
      'h4: data = load[c];
      'h8: data = {29'b0, ovf[c], ctrl[c][0], done[c]};
      'hC: data = count[c];
    endcase
    $display("  [bus] R %s -> 0x%08h", name(addr), data);
    #10ns;
  endtask

  virtual task write8 (addr_handle_t addr, bit [7:0]  data); endtask
  virtual task read8  (addr_handle_t addr, output bit [7:0]  data); data = 0; endtask
  virtual task write16(addr_handle_t addr, bit [15:0] data); endtask
  virtual task read16 (addr_handle_t addr, output bit [15:0] data); data = 0; endtask
  virtual task write64(addr_handle_t addr, bit [63:0] data); endtask
  virtual task read64 (addr_handle_t addr, output bit [63:0] data); data = 0; endtask

  virtual task plat_delay_us(input int us);
    polls++;
    #(us * 1us);
    repeat (us) foreach (ctrl[c]) if (ctrl[c][0]) begin
      count[c]--;
      if (count[c] == 0) begin
        if (done[c]) ovf[c] = 1;              // missed one
        done[c] = 1;
        if (ctrl[c][2]) count[c] = load[c];   // periodic
        else            ctrl[c][0] = 0;       // one-shot
      end
    end
  endtask
endclass

module tb;
  initial begin
    fake_timer_imp imp = new();
    timer_c_ctxt_if tmr = timer_c_root#(fake_timer_imp)::create(imp, 64'h4000_0000);
    bit ok;
    int missed;

    $timeformat(-6, 2, " us", 0);
    $display("probe()");
    tmr.probe(ok);
    if (!ok) $fatal(1, "no timer at BASE");

    $display("one_shot(0, 25)");
    tmr.one_shot(0, 25);

    $display("periodic(1, 20, 3)");
    tmr.periodic(missed, 1, 20, 3);
    $display("  -> missed %0d", missed);

    $display("periodic(1, 4, 2)   -- expires faster than we poll");
    tmr.periodic(missed, 1, 4, 2);
    $display("  -> missed %0d", missed);
    $finish;
  end
endmodule

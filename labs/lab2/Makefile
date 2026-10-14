# Lab 2 -- Registers and memory. `make help` lists the steps.
include ../common/pssc.mk

# `make run SOL=1` builds the exercise solution instead of the starting point.
ifeq ($(SOL),1)
D = solution/
endif

# peakrdl with the peakrdl-pss plugin installed (`pip install peakrdl-pss`)
PEAKRDL ?= peakrdl

REGS = $(D)pss/timer_regs_pkg.pss
SRCS = $(REGS) $(D)pss/plat_pkg.pss $(D)pss/timer_types_pkg.pss \
       $(D)pss/timer_ch_c.pss $(D)pss/timer_c.pss
ROOT = timer_c

help:
	@echo "make regs      -- SystemRDL -> PSS register package ($(REGS))"
	@echo "make gen       -- generate all four flavors into $(D)gen/<flavor>/"
	@echo "make run-c     -- build + run the C host harness"
	@echo "make run-sv    -- build + run the SystemVerilog harness (Verilator)"
	@echo "make run-py    -- run the Python harness"
	@echo "make run       -- all three"
	@echo "make clean"
	@echo "Add SOL=1 to any target to use the solution."

regs: $(REGS)
$(REGS): $(D)rdl/timer.rdl
	$(PEAKRDL) pss $< --pad-tail -o $@

gen: gen-sv gen-c gen-cpp gen-py

gen-sv: $(SRCS)
	$(PSSC) compile $(SRCS) -t op-model-sv  --root $(ROOT) -o $(D)gen/sv
gen-c: $(SRCS)
	$(PSSC) compile $(SRCS) -t op-model-c   --root $(ROOT) -o $(D)gen/c \
	    --link-style direct --mem-access functions --lifecycle static
gen-cpp: $(SRCS)
	$(PSSC) compile $(SRCS) -t op-model-cpp --root $(ROOT) -o $(D)gen/cpp
gen-py: $(SRCS)
	$(PSSC) compile $(SRCS) -t op-model-py  --root $(ROOT) -o $(D)gen/py

run-c: gen-c
	mkdir -p $(D)build
	$(CC) $(CFLAGS) -I$(D)gen/c -o $(D)build/c_harness $(D)env/c/main.c $(D)gen/c/timer.c
	./$(D)build/c_harness

run-sv: gen-sv
	mkdir -p $(D)build
	$(VERILATOR) --binary --timing -Wno-fatal -I$(D)gen/sv --Mdir $(D)build/sv \
	    $(D)gen/sv/pssc_reg_pkg.sv $(D)gen/sv/timer_c_pkg.sv $(D)env/sv/tb.sv --top-module tb \
	    > $(D)build/sv.log 2>&1 || (cat $(D)build/sv.log; false)
	./$(D)build/sv/Vtb

run-py: gen-py
	PYTHONPATH=$(D)gen/py $(PYTHON) $(D)env/py/run.py

run: run-c run-sv run-py

clean:
	rm -rf gen build solution/gen solution/build

.PHONY: help regs gen gen-sv gen-c gen-cpp gen-py run-c run-sv run-py run clean

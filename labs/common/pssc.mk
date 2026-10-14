# Shared make settings for the labs.
#
# PSSC is the pssc command. With pssc installed (`pip install pssc`) the
# default works; against a source checkout, point it at the tree:
#   make PSSC_SRC=~/projects/psstools/pssc
ifneq ($(PSSC_SRC),)
PSSC ?= env PYTHONPATH=$(PSSC_SRC)/src $(PSSC_SRC)/packages/python/bin/python -m pssc
else
PSSC ?= pssc
endif

CC        ?= gcc
CFLAGS    ?= -std=c99 -Wall -Wextra -O1
VERILATOR ?= verilator
PYTHON    ?= python3

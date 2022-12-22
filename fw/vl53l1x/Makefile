# Location of top-level MicroPython directory
MPY_DIR = ../micropython

# Name of module
MOD = vl53l1x

# Source files (.c or .py)
SRC = vl53l1x.c VL53L1X_api.c vl53l1_platform.c vl53l1x.py

# Architecture to build for (x86, x64, armv6m, armv7m, xtensa, xtensawin)
ARCH = xtensawin
MICROPY_FLOAT_IMPL = none
CFLAGS += -DMICROPY_DEBUG_VERBOSE

# Include to get the rules for compiling and linking the module
include $(MPY_DIR)/py/dynruntime.mk

.PHONY: compiledb
compiledb:
	compiledb make clean all

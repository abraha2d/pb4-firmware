#!/usr/bin/env bash

set -e
set -o pipefail

scripts/01_build_fw.sh

FACTORY_OFFSET=$(gen_esp32part.py build/partition-table.bin | grep '^factory,' | cut -d, -f4)
esptool.py --baud 2000000 write_flash --flash_mode qout 0x1000 build/bootloader.bin 0x8000 build/partition-table.bin "$FACTORY_OFFSET" build/micropython.bin

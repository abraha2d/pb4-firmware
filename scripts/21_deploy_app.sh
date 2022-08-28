#!/usr/bin/env bash

set -e
set -o pipefail

scripts/12_pack_app.sh

VFS_OFFSET=$(gen_esp32part.py build/partition-table.bin | grep vfs | cut -d, -f4)
esptool.py --baud 2000000 write_flash --flash_mode qout "$VFS_OFFSET" build/app.bin

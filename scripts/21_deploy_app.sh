#!/usr/bin/env bash

set -e
set -o pipefail

scripts/12_pack_app.sh

VFS_OFFSET=$(gen_esp32part.py build/partition-table.bin | grep vfs | cut -d, -f4 | xargs)
esptool.py --baud 1000000 write_flash "$VFS_OFFSET" build/app.bin

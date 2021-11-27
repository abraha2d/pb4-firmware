#!/usr/bin/env bash

set -e
set -o pipefail

scripts/02_pack.sh

VFS_OFFSET=$(grep vfs partitions.csv | cut -d, -f4 | xargs)
esptool.py --baud 2000000 write_flash "$VFS_OFFSET" build/app.bin

#!/usr/bin/env bash

set -e
set -o pipefail

VFS_OFFSET=$(grep factory partitions.csv | cut -d, -f4 | xargs)
esptool.py --baud 2000000 write_flash "$VFS_OFFSET" build/fw.bin

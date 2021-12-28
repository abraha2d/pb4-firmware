#!/usr/bin/env bash

set -e
set -o pipefail

# TODO: Build firmware if necessary

FACTORY_OFFSET=$(grep factory partitions.csv | cut -d, -f4 | xargs)
esptool.py --baud 2000000 write_flash "$FACTORY_OFFSET" build/fw.bin

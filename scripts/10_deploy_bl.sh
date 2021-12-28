#!/usr/bin/env bash

set -e
set -o pipefail

# TODO: Build bootloader if necessary

esptool.py --baud 2000000 write_flash 0x1000 build/bl.bin

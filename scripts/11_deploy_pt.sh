#!/usr/bin/env bash

set -e
set -o pipefail

gen_esp32part.py --flash-size 16MB partitions.csv build/pt.bin

esptool.py --baud 2000000 write_flash 0x8000 build/pt.bin

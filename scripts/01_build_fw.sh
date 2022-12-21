#!/usr/bin/env bash

set -e
set -o pipefail

export BOARD="${BOARD:-PB4}"
FW_SRC="${FW_SRC:-fw/micropython/ports/esp32}"

cp -a config/* "$FW_SRC"

make -C "$FW_SRC" submodules all

mkdir -p build/
cp -a "$FW_SRC/build-$BOARD/bootloader/bootloader.bin" build/
cp -a "$FW_SRC/build-$BOARD/partition_table/partition-table.bin" build/
cp -a "$FW_SRC/build-$BOARD/micropython.bin" build/

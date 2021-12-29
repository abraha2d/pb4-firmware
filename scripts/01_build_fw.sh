#!/usr/bin/env bash

set -e
set -o pipefail

export BOARD="${BOARD:-POTTYBOX_4}"
FW_SRC="${FW_SRC:?required!}"

cp -a config/* "$FW_SRC"

make -C "$FW_SRC" all

cp -a "$FW_SRC/build-$BOARD/bootloader/bootloader.bin" build/
cp -a "$FW_SRC/build-$BOARD/partition_table/partition-table.bin" build/
cp -a "$FW_SRC/build-$BOARD/micropython.bin" build/

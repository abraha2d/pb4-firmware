#!/usr/bin/env bash

set -e
set -o pipefail

export BOARD="${BOARD:-PB4}"
FW_SRC="${FW_SRC:-fw/micropython/ports/esp32}"

cp -a config/* "$FW_SRC"

make -C "$FW_SRC" clean

#!/usr/bin/env bash

set -e
set -o pipefail

VFS_EXTRA=94754
VFS_ALIGN=0x10000

scripts/11_stage_app.sh

mkdir -p build
rm -rf build/app.bin

APP_SIZE=$(du -bd0 staging | xargs | cut -d' ' -f1)
VFS_SIZE=$((((APP_SIZE + VFS_EXTRA) / VFS_ALIGN + 1) * VFS_ALIGN))

mklittlefs -c staging -s "$VFS_SIZE" -- build/app.bin >/dev/null

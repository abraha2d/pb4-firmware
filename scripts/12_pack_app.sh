#!/usr/bin/env bash

set -e
set -o pipefail

VFS_SIZE=$(gen_esp32part.py build/partition-table.bin | grep '^vfs,' | cut -d, -f5)
VFS_SIZE=${VFS_SIZE//M/*1024K}
VFS_SIZE=${VFS_SIZE//K/*1024}
VFS_SIZE=$((VFS_SIZE))

scripts/11_stage_app.sh

mkdir -p build/
rm -rf build/app.bin

mklittlefs -c staging -s "$VFS_SIZE" -- build/app.bin >/dev/null

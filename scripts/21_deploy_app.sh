#!/usr/bin/env bash

set -e
set -o pipefail

scripts/13_pack_app.sh

VFS_OFFSET=$(gen_esp32part.py build/partition-table.bin | grep '^vfs,' | cut -d, -f4)

APP_0_OFFSET=$(gen_esp32part.py build/partition-table.bin | grep 'app_0,' | cut -d, -f4)
APP_0_SIZE=$(gen_esp32part.py build/partition-table.bin | grep '^app_0,' | cut -d, -f5)
APP_0_SIZE=${APP_0_SIZE//M/*1024K}
APP_0_SIZE=${APP_0_SIZE//K/*1024}
APP_0_SIZE=$((APP_0_SIZE))

APP_1_OFFSET=$(gen_esp32part.py build/partition-table.bin | grep '^app_1,' | cut -d, -f4)
APP_1_SIZE=$(gen_esp32part.py build/partition-table.bin | grep '^app_1,' | cut -d, -f5)
APP_1_SIZE=${APP_1_SIZE//M/*1024K}
APP_1_SIZE=${APP_1_SIZE//K/*1024}
APP_1_SIZE=$((APP_1_SIZE))

esptool.py --baud 2000000 write_flash --flash_mode qout "$VFS_OFFSET" build/app.bin
[ -n "$APP_0_OFFSET" ] && esptool.py --baud 2000000 erase_region "$APP_0_OFFSET" "$APP_0_SIZE"
[ -n "$APP_1_OFFSET" ] && esptool.py --baud 2000000 erase_region "$APP_1_OFFSET" "$APP_1_SIZE"

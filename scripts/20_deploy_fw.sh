#!/usr/bin/env bash

set -e
set -o pipefail

scripts/01_build_fw.sh

FACTORY_OFFSET=$(gen_esp32part.py build/partition-table.bin | grep '^factory,' | cut -d, -f4)

OTA_0_OFFSET=$(gen_esp32part.py build/partition-table.bin | grep '^ota_0,' | cut -d, -f4)
OTA_0_SIZE=$(gen_esp32part.py build/partition-table.bin | grep '^ota_0,' | cut -d, -f5)
OTA_0_SIZE=${OTA_0_SIZE//M/*1024K}
OTA_0_SIZE=${OTA_0_SIZE//K/*1024}
OTA_0_SIZE=$((OTA_0_SIZE))

OTA_1_OFFSET=$(gen_esp32part.py build/partition-table.bin | grep '^ota_1,' | cut -d, -f4)
OTA_1_SIZE=$(gen_esp32part.py build/partition-table.bin | grep '^ota_1,' | cut -d, -f5)
OTA_1_SIZE=${OTA_1_SIZE//M/*1024K}
OTA_1_SIZE=${OTA_1_SIZE//K/*1024}
OTA_1_SIZE=$((OTA_1_SIZE))

esptool.py --baud 2000000 write_flash --flash_mode qout 0x1000 build/bootloader.bin 0x8000 build/partition-table.bin "$FACTORY_OFFSET" build/micropython.bin
[ -n "$OTA_0_OFFSET" ] && esptool.py --baud 2000000 erase_region "$OTA_0_OFFSET" "$OTA_0_SIZE"
[ -n "$OTA_1_OFFSET" ] && esptool.py --baud 2000000 erase_region "$OTA_1_OFFSET" "$OTA_1_SIZE"

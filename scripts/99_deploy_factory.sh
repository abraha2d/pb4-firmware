#!/usr/bin/env bash

set -e
set -o pipefail

scripts/01_build_fw.sh
scripts/13_pack_app.sh

esptool.py erase_flash
scripts/20_deploy_fw.sh
scripts/21_deploy_app.sh

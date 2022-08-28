#!/usr/bin/env bash

set -e
set -o pipefail

esptool.py erase_flash
scripts/20_deploy_fw.sh
scripts/21_deploy_app.sh

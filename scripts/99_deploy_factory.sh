#!/usr/bin/env bash

set -e
set -o pipefail

scripts/20_deploy_fw.sh
scripts/21_deploy_app.sh

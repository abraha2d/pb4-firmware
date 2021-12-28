#!/usr/bin/env bash

set -e
set -o pipefail

scripts/10_deploy_bl.sh
scripts/11_deploy_pt.sh
scripts/12_deploy_fw.sh
scripts/13_deploy_app.sh

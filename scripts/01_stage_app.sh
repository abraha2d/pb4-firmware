#!/usr/bin/env bash

set -e
set -o pipefail

scripts/00_build_ui.sh

mkdir -p staging
rm -rf staging/*

cd src
find -- * -type f -iregex ".*\.\(py\|html\|css\|js\)" -print0 | xargs -0 cp --parents -t ../staging

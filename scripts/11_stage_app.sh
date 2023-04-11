#!/usr/bin/env bash

set -e
set -o pipefail

mkdir -p staging/
rm -rf staging/*

scripts/10_build_ui.sh
(cd src && find -- * -type f -iregex ".*\.\(py\|html\|css\|js\)" -print0 | xargs -0 cp --parents -t ../staging/)

echo "NAME = '$(basename "$(git remote get-url origin)" .git)'" >>staging/version.py
echo "VERSION = '$(git describe --always --dirty)'" >>staging/version.py

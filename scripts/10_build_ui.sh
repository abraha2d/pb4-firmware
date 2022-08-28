#!/usr/bin/env bash

set -e
set -o pipefail

cd ui
yarn

VERSION_FILE=$(yarn --silent build_path)/VERSION
if [ -f "$VERSION_FILE" ]; then
  VERSION=$(<"$VERSION_FILE")
fi

APPVER=$(yarn --silent appver)

[ "$APPVER" == "$VERSION" ] || yarn build

echo "$APPVER" > "$VERSION_FILE"

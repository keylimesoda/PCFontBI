#!/usr/bin/env sh
set -eu
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/fonts/PCFontBI"
mkdir -p "$DEST"
cp fonts/PCFontBI-*.ttf "$DEST/"
if command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f "$DEST"
fi
printf 'Installed PCFontBI to %s\n' "$DEST"

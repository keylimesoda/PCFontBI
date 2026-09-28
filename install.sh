#!/usr/bin/env sh
set -eu
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/fonts/PCFontBI"
mkdir -p "$DEST"
cp fonts/PCFontBI-*.ttf "$DEST/"
cp fonts/PCFontBI-Symbols.ttc "$DEST/"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/fontconfig/conf.d"
mkdir -p "$CONFIG_DIR"
cp config/60-PCFontBI-symbols.conf "$CONFIG_DIR/60-PCFontBI-symbols.conf"
if command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f "$DEST"
fi
printf 'Installed PCFontBI and its symbol companion to %s\n' "$DEST"

#!/usr/bin/env sh
set -eu
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/fonts/ibm-vga8x16-tui"
mkdir -p "$DEST"
cp fonts/*.ttf "$DEST/"
if command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f "$DEST"
fi
printf 'Installed IBM VGA 8x16 TUI to %s\n' "$DEST"

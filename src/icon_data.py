"""Original pixel icons plus the independently licensed companion repertoire."""
import gzip,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ICONS=json.loads((ROOT/'design/icons.json').read_text())
ICON_ROWS={int(cp,16):bytes.fromhex(icon['rows']) for icon in ICONS.values() for cp in icon['mappings'].values()}
SYMBOL_SOURCE=json.loads(gzip.decompress((ROOT/'upstream/nerd-fonts/pixel-symbols.json.gz').read_bytes()))
SYMBOL_ROWS={int(cp,16):bytes.fromhex(rows) for cp,rows in SYMBOL_SOURCE['glyphs'].items()}

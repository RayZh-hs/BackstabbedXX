#!/usr/bin/env python3
"""Disable station boundary returns and install reversible carriage links.

Before installing, flush and stop all writers and take a verified full-world
backup with the map-creator helper. --output prepares a ZIP without installation.
"""

import argparse
import json
from pathlib import Path
import tempfile
import zipfile

from subway_station_carriages import TRANSLATIONS, links, patch_datapack


ROOT = Path(__file__).resolve().parent.parent
WORLD = ROOT / '.minecraft/saves/Backstabbed ++! by NorbMinecraft and Bagel Buddies'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Prepare the datapack without changing the world or assets')
    args = parser.parse_args()
    source = WORLD / 'datapacks/mcm.zip'
    with zipfile.ZipFile(source) as archive:
        files = {info.filename: archive.read(info) for info in archive.infolist()}
    patch_datapack(files)
    output = args.output or source
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.zip', delete=False) as stream:
        temporary = Path(stream.name)
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name, content in files.items():
                archive.writestr(name, content)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    if not args.output:
        for language, changes in TRANSLATIONS.items():
            path = ROOT / f'.minecraft/resourcepacks/backstabbed-resource/assets/subway_station/lang/{language}.json'
            values = json.loads(path.read_text())
            values.pop('subway_station.boundary', None)
            values.update(changes)
            path.write_text(json.dumps(values, ensure_ascii=False, indent=2) + '\n')
    manifest = ROOT / 'docs/arenas/subway_station_carriages.json'
    manifest.write_text(json.dumps(list(links()), indent=2, ensure_ascii=False) + '\n')
    print(f'Prepared {output}: 40 carriage links, automatic boundary returns disabled')


if __name__ == '__main__':
    main()

"""KLUT-27 containment: one build-sized cuboid with a 30-block face margin."""
import json
from pathlib import Path

MARGIN = 30

def boxes_for_build(bounds, offset=36864):
    # Bounds identify occupied block coordinates. Include the positive face of
    # the last block before expanding, so both sides have exactly 30 blocks.
    return [{axis: {'min': bounds['min'][i] + shift - MARGIN,
                   'max': bounds['max'][i] + 1 + shift + MARGIN}
             for i, (axis, shift) in enumerate(zip('xyz', (offset, 0, offset)))}]

def current_boxes():
    manifest = Path(__file__).resolve().parents[1] / 'docs/arenas/klut27.json'
    return boxes_for_build(json.loads(manifest.read_text(encoding='utf-8'))['source_visible_bounds'])

def predicate(boxes):
    return {'condition': 'minecraft:any_of', 'terms': [
        {'condition': 'minecraft:location_check', 'predicate': {
            'dimension': 'minecraft:overworld', 'position': box}} for box in boxes]}

if __name__ == '__main__':
    import datetime, hashlib, zipfile
    from sync_klut27_standalone import ROOT, TARGETS, zip_bytes
    key = 'data/klut27/predicate/arena.json'
    boxes = current_boxes()
    body = (json.dumps(predicate(boxes), separators=(',', ':')) + '\n').encode()
    folder = ROOT / '.minecraft/backups/klut27-cuboid-boundary' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder.mkdir(parents=True)
    snapshots = []
    for index, world in enumerate(TARGETS):
        path = world / 'datapacks/mcm.zip'; original = path.read_bytes()
        backup = folder / f'{index}-mcm.zip'; backup.write_bytes(original)
        assert backup.read_bytes() == original
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            files = {name: z.read(name) for name in z.namelist()}
        files[key] = body
        snapshots.append((path, original, zip_bytes(files)))
    # Check neither file changed during preparation (e.g. an external editor).
    for path, original, _ in snapshots: assert path.read_bytes() == original, path
    for path, _, updated in snapshots: path.write_bytes(updated)
    manifest_path = ROOT / 'docs/arenas/klut27.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest.update(containment_boxes=boxes, containment_margin=MARGIN,
                    containment_shape='cuboid', play_area='Entire build bounding box including the lower antenna, expanded 30 blocks from all six block-volume faces. Existing waiting/active elimination rules remain.')
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Updated bounds:', boxes)
    print('Datapack backups:', folder)

"""Append-only Lost Vale prefabs. Coordinates are world offsets within a chunk.

Rows comprise (name, floor shape or None, floor frames, props). Props are
(x, y, z, shape, frame); x and y must be odd. Append rows to PREFABS.
Packed rows live with their immutable IDs and content in lv_manifest.json.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import struct

# Pin the writer to this sibling; compiler imports can preload another copy.
_flex_spec = importlib.util.spec_from_file_location(
    '_lv_globs_flex', Path(__file__).with_name('u8_flex.py'))
_flex_module = importlib.util.module_from_spec(_flex_spec)
_flex_spec.loader.exec_module(_flex_module)
FlexArchive = _flex_module.FlexArchive

ROOT = Path(__file__).resolve().parents[3]
RETAIL = ROOT / 'shared/data/u8-install/STATIC/GLOB.FLX'
if RETAIL.with_suffix('.FLX.bak').exists():
    RETAIL = RETAIL.with_suffix('.FLX.bak')
OUTPUT = ROOT / 'shared/build/GLOB.FLX'
MANIFEST = ROOT / 'shared/build/lv_manifest.json'
FIRST = 3072

# Six layouts per family, kept in this order forever. All art already ships.
LAYOUTS = (
    ((159, 223), (255, 255), (319, 319)),
    ((95, 319), (191, 351), (223, 255)),
    ((351, 159), (383, 255), (287, 223)),
    ((191, 127), (255, 191), (159, 223)),
    ((287, 351), (383, 383), (351, 287)),
    ((127, 191), (223, 223), (191, 319)),
)
# name, floor, frames, prop (shape, frame) sequence. Frame selection for
# floors is seeded by row and cell, so adding rows preserves earlier bytes.
FAMILIES = (
    ('earth_brush', 4, (30, 31, 32, 33), ((321, 0), (322, 1), (465, 0))),
    ('earth_wood', 4, (30, 31, 32, 33), ((75, 0), (56, 0), (322, 0))),
    ('earth_debris', 4, (30, 31, 32, 33), ((465, 0), (465, 2), (322, 1))),
    ('mixed_earth', 301, tuple(range(7)), ((465, 0), (322, 0), (465, 2))),
    ('cloud_gold', 874, (0, 2, 3, 4), ()),
    ('cloud_columns', 874, (0, 2, 3, 4), ((875, 0), (875, 0))),
    ('cloud_edge', 874, (0, 2, 3, 4), ()),
    ('gold', 876, (0, 1), ()),
    ('flagstone', 35, (0,), ((465, 0), (465, 1))),
    ('yard', 4, (30, 31, 32, 33), ((149, 0), (649, 2), (322, 0))),
)
PREFABS = tuple((f'{name}_{k}', floor, frames,
                 tuple((*xy, 0, shape, frame) for xy, (shape, frame)
                       in zip(LAYOUTS[k], props)))
                for name, floor, frames, props in FAMILIES for k in range(6))

# Appended after the first wave's packed rows by the manifest allocator.
# Authored silhouettes: an oak shoulder, an open glade, an edge thicket,
# and a smaller grove with deadwood. All bases stay on the ground. Separate
# collision boxes let mushrooms and roots sit beside trunks at their feet.
PREFABS += tuple((f'grass_wood_{k}', 3, (26, 27, 28), props)
    for k, props in enumerate((
        ((287,319,0,199,0), (511,223,0,75,4), (95,447,0,152,2),
         (511,511,0,57,0), (287,383,0,65,6), (479,319,0,65,7),
         (127,511,0,434,0), (383,287,0,434,2), (191,383,0,414,0)),
        ((223,255,0,75,4), (511,479,0,75,1), (127,479,0,152,0),
         (479,191,0,57,2), (287,319,0,65,7), (191,447,0,65,6),
         (287,127,0,434,1), (479,255,0,434,3), (223,511,0,414,0)),
        ((511,383,0,199,0), (223,223,0,75,0), (383,479,0,152,3),
         (223,447,0,57,1), (511,479,0,65,6), (447,479,0,65,7),
         (191,511,0,434,2), (383,95,0,434,0), (319,511,0,414,0)),
        ((383,255,0,75,4), (255,511,0,75,3), (95,159,0,152,4),
         (479,511,0,57,3), (447,319,0,65,7), (319,319,0,65,6),
         (159,255,0,434,3), (511,319,0,434,1), (127,223,0,414,0)),
    )))
# Paint-only banks. They overlay existing grass, whose top is z=48.
# Local x=255 is the west bank's east edge; x=385 is the east bank's
# westmost 128-unit column. No grass or water is emitted by these rows.
PREFABS += tuple((f'moat_{side}_{k}', None, (),
                 tuple(p for j, y in enumerate((127, 255, 383, 511))
                       for p in ((x, y, 40, 903, (6, 8, 9, 10)[(k+j)%4]),
                                 (x if side == 'west' else x+32,
                                  y, 8, 904, (k+j)%7))))
                for side, x in (('west', 255), ('east', 385))
                for k in range(4))

PREFABS += tuple((f'fallen_drum_{k}', 874, (0, 2, 3, 4),
                 ((x, y, 0, 905, 0), (x-64, y+64, 0, 910, 6+k%3)))
                 for k, (x, y) in enumerate(((255,255),(319,191),(191,319),(351,287))))

# Retail 455's rock-to-earth corner, world offsets and oriented edge frames.
MIXED_TILES = ((127,511,301,0), (127,383,301,1), (255,511,301,1),
               (255,383,301,0), (383,511,386,1), (383,383,386,0),
               (127,255,386,6), (255,255,386,7), (383,255,386,11),
               (511,511,4,31), (511,127,4,31), (383,127,4,32),
               (127,127,4,33), (255,127,386,24), (511,383,386,24),
               (511,255,4,32))


def authored(row):
    name, floor, frames, props = row
    k = int(name.rsplit('_', 1)[1])
    tiles = []
    if floor is None:
        return list(props)
    for x in (127, 255, 383, 511):
        for y in (127, 255, 383, 511):
            rng = random.Random(f'{name}:{x}:{y}')
            shape, frame = floor, rng.choice(frames)
            if name.startswith('cloud_gold') and x + y > 600 + 32 * k:
                shape, frame = 876, rng.randrange(2)
            if name.startswith('cloud_edge') and x + y > 700 + 32 * k:
                shape, frame = 351, 0
            # Flat earth interiors surrounded by rock; no directional edge
            # frame is rotated or guessed. Corners can be appended as rows.
            if name.startswith('mixed_earth') and x <= 255 and y <= 255:
                shape, frame = 4, rng.choice((30, 31, 32, 33))
            tiles.append((x, y, 0, shape, frame))
    if name.startswith('mixed_earth'):
        tiles = [(x,y,0,shape,random.Random(f'{name}:{x}:{y}').choice(frames)
                  if shape == 301 else frame) for x,y,shape,frame in MIXED_TILES]
    if name.startswith('earth_wood'):
        props = ((255,255,0,75,0), (447,447,0,56,k), (383,127,0,322,k%5))
    if name.startswith('yard'):
        props = ((159,159,0,149,0), (447,351,0,649,2), (255,447,0,322,k%5))
    return tiles + list(props)


def encode(items):
    if len(items) > 65535:
        raise ValueError('glob item count exceeds uint16')
    out = bytearray(struct.pack('<H', len(items)))
    for x, y, z, shape, frame in items:
        if not (0 <= x <= 511 and 0 <= y <= 511 and x % 2 and y % 2):
            raise ValueError(f'glob coordinates must be odd within chunk: {(x, y)}')
        out.extend(struct.pack('<BBBHB', x // 2, y // 2, z, shape, frame))
    return bytes(out)


def registry(path=MANIFEST):
    return json.loads(Path(path).read_text())


_PACKED_CACHE = {}  # resolved manifest path -> (file bytes, parsed document)


def register_packed(items, path=MANIFEST):
    """Persist a content-addressed row before its egg can be emitted.

    Build_all_maps rebuilds GLOB.FLX after builders and before validation.
    The manifest is source data: each appended row must travel with its map.

    Rows are content-addressed, so on a rebuild nearly every call finds its
    row present. The parsed manifest is reused while the file's bytes are
    exactly what was last parsed or written here; any other writer changes
    the bytes and forces a fresh parse. (Map 10's pack made 1,593 calls,
    each re-parsing the whole manifest: 66 s, 2026-11-10.)
    """
    items = [tuple(i) for i in items]
    payload = encode(items)
    name = 'packed_' + hashlib.sha256(payload).hexdigest()
    key = str(Path(path).resolve())
    data = Path(path).read_bytes()
    cached = _PACKED_CACHE.get(key)
    doc = cached[1] if cached and cached[0] == data else json.loads(data)
    _PACKED_CACHE[key] = (data, doc)
    pins = doc.setdefault('globs', {})
    if name in pins:
        if pins[name]['items'] != [list(i) for i in items]:
            raise ValueError(f'content changed for {name}')
        return pins[name]['id']
    number = max([FIRST - 1] + [p['id'] for p in pins.values()]) + 1
    if number > 65535:
        raise ValueError('glob quality exhausted')
    # Lists, as a re-parse would give, so the cached document compares the
    # same way; JSON serialises lists and tuples identically.
    pins[name] = dict(id=number, items=[list(i) for i in items])
    out = (json.dumps(doc, indent=2) + '\n').encode()
    Path(path).write_bytes(out)
    _PACKED_CACHE[key] = (out, doc)
    return number


def build(retail=RETAIL, output=OUTPUT, manifest=MANIFEST):
    base = FlexArchive(retail)
    if base.count != FIRST:
        raise ValueError(f'expected {FIRST} retail slots, found {base.count}')
    doc = registry(manifest)
    pins = doc.setdefault('globs', {})
    for row in PREFABS:
        name = row[0]
        payload = encode(authored(row))
        digest = hashlib.sha256(payload).hexdigest()
        n = pins[name]['id'] if name in pins else max([FIRST - 1] + [p['id'] for p in pins.values()]) + 1
        expected = dict(id=n, sha256=digest)
        if name in pins and pins[name] != expected:
            raise ValueError(f'authored glob pin changed: {name}')
        pins[name] = expected
    ids = [p['id'] for p in pins.values()]
    if len(ids) > 65536 - FIRST:
        raise ValueError('glob quality exhausted')
    if len(set(ids)) != len(ids) or sorted(ids) != list(range(FIRST, FIRST + len(ids))):
        raise ValueError('glob IDs must be unique and contiguous from 3072')
    entries = [base.get_object(i) for i in range(FIRST)] + [None] * len(ids)
    for row in PREFABS:
        entries[pins[row[0]]['id']] = encode(authored(row))
    for name, pin in pins.items():
        if name.startswith('packed_'):
            payload = encode(pin['items'])
            if name != 'packed_' + hashlib.sha256(payload).hexdigest():
                raise ValueError(f'packed glob content changed: {name}')
            entries[pin['id']] = payload
    staged = Path(str(output) + '.staging')
    try:
        FlexArchive.write(staged, entries, header=base._data[:128])
        check = FlexArchive(staged)
        if check.count != len(entries) or any(check[i] != entries[i] for i in range(len(entries))):
            raise ValueError('glob round trip failed')
    except Exception:
        if staged.exists():
            os.replace(staged, str(output) + '.failed')
        raise
    Path(manifest).write_text(json.dumps(doc, indent=2) + '\n')
    os.replace(staged, output)
    print(f'GLOB.FLX: {FIRST} retail slots preserved, {len(ids)} LV slots appended')


if __name__ == '__main__':
    build()

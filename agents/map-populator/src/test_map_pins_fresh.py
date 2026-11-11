#!/usr/bin/env python3
"""
test_map_pins_fresh.py — map_pins.json cannot go stale silently.

map_pins.json (docs/reviews/2026-09-14-map-cleanup-plan.md section 2) is a
DERIVED inventory: derive_map_pins.py reads it out of the built FIXED.DAT,
lv_manifest.json and the compiled usecode. Nothing stops it drifting out of
sync with a later build by hand — it was found stale on 2026-09-30, still
recording the FIXED.DAT sha256 prefix bf233644 (EggEndgame at its pre-move
position, one Map 18 EggCrackHint missing) two commits after 4f981fe and
5620f0e moved those eggs and rebuilt FIXED.DAT to f92973ee.

This test re-derives the pin inventory twice and fails if the committed
map_pins.json disagrees with either in any field but the `generated` date
stamp, which is expected to move every regeneration and carries no
information about correctness:

  * from the CURRENTLY BUILT FIXED.DAT (the same call derive_map_pins.py's
    main() makes) — the bytes that ship;
  * from the map builders' in-memory output (derive_map_pins.build
    ('builders')) — so a builder edit that moves a pinned item fails here
    at once, before anyone rebuilds FIXED.DAT.

    python3 agents/map-populator/src/test_map_pins_fresh.py

Plain script: exit 0 on pass, 1 on fail.
"""

import json
import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
PINS = os.path.join(SRC_DIR, 'map_pins.json')

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


print('=' * 70)
print('map_pins.json freshness — re-derived against the BUILT FIXED.DAT')

if not os.path.exists(FIXED):
    print('  shared/build/FIXED.DAT absent — run tools/build_artifacts.sh')
    sys.exit(1)

if not os.path.exists(PINS):
    print('  map_pins.json absent — run '
          'agents/map-populator/src/derive_map_pins.py')
    sys.exit(1)

import derive_map_pins          # noqa: E402

fresh, notes = derive_map_pins.build()
with open(PINS) as fh:
    committed = json.load(fh)

check('committed fixed_sha256_prefix matches the built FIXED.DAT',
      committed.get('fixed_sha256_prefix') == fresh['fixed_sha256_prefix'],
      f"committed {committed.get('fixed_sha256_prefix')!r} != built "
      f"{fresh['fixed_sha256_prefix']!r} — FIXED.DAT was rebuilt since "
      f"map_pins.json was last regenerated")


def row_key(r):
    return (r['shape'], r['frame'], r['quality'], r['npcnum'],
            r['x'], r['y'], r['z'])


# Every field but the date stamp has to agree, or the inventory is
# describing a different map than the one that ships (FIXED.DAT) or the
# one the builders now produce.
for label, derived in (
        ('the built FIXED.DAT', fresh),
        ("the builders' in-memory output",
         derive_map_pins.build('builders')[0])):
    stale = committed.get('maps') != derived['maps']
    check(f'every pinned row (map, shape, frame, quality, npcnum, position, '
          f'class, kind, why, reads) matches {label}',
          not stale,
          f'map_pins.json disagrees with {label} — rebuild if a builder '
          f'changed, then regenerate with '
          f'`python3 agents/map-populator/src/derive_map_pins.py` and commit '
          f'the diff')
    if not stale:
        continue
    for mapnum in sorted(set(committed.get('maps', {})) |
                         set(derived['maps']), key=int):
        old = committed.get('maps', {}).get(mapnum, [])
        new = derived['maps'].get(mapnum, [])
        if old == new:
            continue
        print(f'    map {mapnum}: committed {len(old)} row(s), '
              f'derived {len(new)} row(s)')
        old_k = {row_key(r) for r in old}
        new_k = {row_key(r) for r in new}
        for k in sorted(old_k - new_k):
            print(f'      - shape {k[0]} frame {k[1]} q {k[2]} npc {k[3]} '
                  f'at ({k[4]}, {k[5]}, {k[6]})')
        for k in sorted(new_k - old_k):
            print(f'      + shape {k[0]} frame {k[1]} q {k[2]} npc {k[3]} '
                  f'at ({k[4]}, {k[5]}, {k[6]})')

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

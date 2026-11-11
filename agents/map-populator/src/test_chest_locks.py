#!/usr/bin/env python3
"""
test_chest_locks.py — every locked chest we place has a lock its key fits.

A locked chest (shape 618, or its east-facing twin 673) is not locked by its
own quality. KEYRING (class 0x4F, byte-identical to retail) handles a key
used on one at 004F:0445: it looks inside the chest for a TRAP (shape 756)
with quality/256 == 1 and opens the chest only for a key whose quality
equals that trap's low byte. With no such TRAP it opens for ANY key, the key
blank included. Hrodny's chest shipped that way until 2026-10-08
(docs/playtest-2026-10-08-intrinsics.md, C4; the rule is written up in
docs/research/2026-10-08-u8-intrinsic-table.md).

So, for every locked chest the builders put in FIXED.DAT:
  1. a contained TRAP with quality/256 == 1 follows it (same container
     depth, before the next top-level record), and
  2. a key (shape 82) whose quality is that trap's low byte exists: placed
     on some map, or, for a lock in SCRIPT_KEYS, spawned by the usecode
     named there. A script-keyed lock must have NO placed key, so the
     errand that hands it out can't be skipped.

Retail locked chests live in NONFIXED, not FIXED, so the base FIXED.DAT has
none; the test still skips any chest the pristine base already carries.
"""

import os
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(os.path.dirname(SRC)))
sys.path.insert(0, SRC)

from u8_map import MapArchive                               # noqa: E402
from lv_shapes import SHAPE_CHEST_LOCKED, SHAPE_KEY, SHAPE_TRAP  # noqa: E402

BUILT = os.path.join(BASE, 'shared', 'build', 'FIXED.DAT')
PRISTINE = os.path.join(BASE, 'shared', 'data', 'u8-install', 'STATIC',
                        'FIXED.DAT.bak')
LOCKED_CHESTS = (SHAPE_CHEST_LOCKED, 673)
CONTAINER_DEPTH_LIMIT = 64   # contained records carry x = depth (< 64)
# Locks whose only key is handed out by usecode. Hrodny's chest: her
# 'How can I open the temple?' pops a bag holding a q20 key (1994 design;
# test_uc_dialogue 'HRODNY key errand'). The spare q20 key the map used to
# place in the village was removed 2026-10-11 (Douglas).
SCRIPT_KEYS = {20: "HRODNY.UNK 'How can I open the temple?' bag"}

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def contents(items, k):
    """Records directly inside the top-level container at index k."""
    out = []
    for it in items[k + 1:]:
        if it.x >= CONTAINER_DEPTH_LIMIT:
            break
        if it.x == 1:
            out.append(it)
    return out


print('=' * 66)
print('Locked chests: each has a TRAP lock and a key that fits it')
print('=' * 66)

if not os.path.exists(BUILT):
    print(f'  SKIP  {BUILT} not built (run tools/build_artifacts.sh)')
    sys.exit(0)

built = MapArchive(BUILT)
base_chests = set()
if os.path.exists(PRISTINE):
    base = MapArchive(PRISTINE)
    for m in base.non_empty_maps():
        for it in base.get_map_items(m):
            if it.shape in LOCKED_CHESTS:
                base_chests.add((m, it.x, it.y, it.z))

key_qualities = set()
chests = []
for m in built.non_empty_maps():
    items = built.get_map_items(m)
    for k, it in enumerate(items):
        if it.shape == SHAPE_KEY:
            key_qualities.add(it.quality)
        if (it.shape in LOCKED_CHESTS and it.x >= CONTAINER_DEPTH_LIMIT
                and (m, it.x, it.y, it.z) not in base_chests):
            chests.append((m, it, contents(items, k)))

check('the builders place at least one locked chest', bool(chests),
      'Hrodny\'s chest (build_map_10.py) is missing')

for m, chest, inside in chests:
    where = f'map {m} chest at ({chest.x}, {chest.y}, {chest.z})'
    locks = [t for t in inside
             if t.shape == SHAPE_TRAP and t.quality // 256 == 1]
    check(f'{where} contains a TRAP lock (shape {SHAPE_TRAP}, '
          f'quality 0x1xx)', len(locks) == 1,
          f'found {len(locks)}; without one KEYRING opens it for any key')
    for t in locks:
        keyid = t.quality & 0xFF
        if keyid in SCRIPT_KEYS:
            check(f'{where}: no placed key has quality {keyid} (the key '
                  f'comes only from {SCRIPT_KEYS[keyid]})',
                  keyid not in key_qualities,
                  f'placed key qualities: {sorted(key_qualities)}')
            continue
        check(f'{where}: a placed key has quality {keyid}',
              keyid in key_qualities,
              f'placed key qualities: {sorted(key_qualities)}')

print()
print(f'{passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

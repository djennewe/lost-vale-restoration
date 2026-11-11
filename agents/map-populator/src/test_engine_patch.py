#!/usr/bin/env python3
"""
test_engine_patch.py — guards the one engine-side invariant the map data
depends on: EGGS ARE NEVER PROMOTED TO ACTORS.

WHY THIS TEST EXISTS (2026-07-28, found by an in-engine run, not by a test).
The patched `Map::loadFixedFormatObjects` promotes FIXED.DAT items whose
npcNum is 100-116 into real Actors so their dialogue dispatches via
npcNum + 1024. An EGG has no npcNum: that byte holds its hatch ranges
(`Egg::getXRange` = high nibble, `getYRange` = low nibble, x32), so a
perfectly ordinary +/-192 range reads as "npcNum 102" and the promotion
turned the egg into an Actor — which is not an Egg object and therefore can
never hatch. Two of Map 18's event eggs were silently dead this way:

    EggCrackHint   (quality 306, class 1457) @ (2864,6048)
    EggAOCeremony  (quality 296, class 1447) @ (3072,8320)  <- quest step 17

Both carry a 0x66 range, so both landed in actor slot 102 — one clobbering
the other's position — and slot 102 is also Sigrid, a real NPC on Map 10.
`Item::callUsecodeEvent` had always excluded egg families from npcNum
dispatch for exactly this reason; the load-time promotion had not.

The map data is NOT at fault and is not changed: 0x66 is a legitimate hatch
range. The invariant lives in the engine patch, so that is what this test
pins — plus the inventory of eggs that depend on it, so the next person sees
immediately what breaks if the exclusion is dropped.
"""

import os
import re
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_map import MapArchive  # noqa: E402
from lv_shapes import NPCNUM_BANDS  # noqa: E402

PATCH = os.path.join(BASE_DIR, 'tools', 'scummvm-patches',
                     '0001-lost-vale-engine.patch')
FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')

# The maps the promotion is restricted to, and the egg shapes whose npcNum
# byte is range data rather than an NPC number.
LV_MAPS = (9, 10, 11, 13, 17, 18)
EGG_SHAPES = {2, 73, 500, 508}

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
print('Engine patch: eggs are never promoted to Actors')

patch = open(PATCH).read()
added = '\n'.join(ln[1:] for ln in patch.splitlines() if ln.startswith('+'))

check('the tracked engine patch exists and touches map.cpp',
      'world/map.cpp' in patch)

# 1. The promotion still exists and still uses the documented window.
window = re.search(r'npcNum >= (\d+) && npcNum <= (\d+)', added)
check('promotion window is still present in the patch', window is not None)
if window:
    lo, hi = int(window.group(1)), int(window.group(2))
    band = next((k for k in NPCNUM_BANDS if k == (lo, hi)), None)
    check(f'window {lo}-{hi} matches the NPCNUM_BANDS entry in lv_shapes.py',
          band is not None, f'bands={sorted(NPCNUM_BANDS)}')

# 2. The exclusion itself — the whole point of this file.
for fam in ('SF_GLOBEGG', 'SF_UNKEGG', 'SF_MONSTEREGG', 'SF_TELEPORTEGG'):
    check(f'promotion excludes {fam}', fam in added)
check('the exclusion is wired into the promotion condition (!lvIsEgg)',
      re.search(r'if \(GAME_IS_U8 .{0,200}?!lvIsEgg', added, re.S) is not None,
      'the families may be computed but not actually tested')

# 3. The eggs that depend on it, straight from the built map. This is the
#    blast radius: every one of these goes silently dead if the exclusion is
#    removed, and each is an event trigger with no other way to fire.
print()
print('  Eggs on LV maps whose hatch range lands in the promotion window:')
if not os.path.exists(FIXED):
    print('  (shared/build/FIXED.DAT absent — run tools/build_artifacts.sh)')
    check('FIXED.DAT present for the dependency inventory', False,
          'build artifacts first')
else:
    m = MapArchive(FIXED)
    at_risk = []
    for mp in LV_MAPS:
        for i in m.get_map_items(mp):
            if i.shape in EGG_SHAPES and lo <= i.npcnum <= hi:
                at_risk.append((mp, i.shape, i.quality, i.npcnum, i.x, i.y))
    for mp, shape, q, npc, x, y in at_risk:
        print(f'    map {mp:>2}  shape {shape:>3}  quality {q:>4} '
              f'(class {q + 0x47F})  range byte {npc:#04x}  @ ({x},{y})')
    if not at_risk:
        print('    (none right now — the exclusion is still required, because'
              ' any future 0x64-0x74 range would land here)')
    # Assert rather than merely report: these are the two the in-engine run
    # caught, and a regression would show up as them going missing from the
    # map OR the exclusion going missing from the patch (checked above).
    check('the two Map 18 event eggs still carry their 1994-style ranges',
          sorted((q, npc) for _m, _s, q, npc, _x, _y in at_risk)
          == [(296, 0x66), (306, 0x66)],
          str(at_risk))

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

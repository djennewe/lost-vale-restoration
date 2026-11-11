#!/usr/bin/env python3
"""
test_endgame_hatch_box.py — EggEndgame hatches on the Map 10 arrival pad
from Map 18 (teleport target 210), and never from the return trigger 211.

Map 10's EggEndgame (shape 73, quality 299 -> class 1450, lv-new/ENDGAME.UNK)
was moved on 2026-09-29 (commit 5620f0e) to sit on teleport TARGET egg 210 —
the pad every return from Map 18 lands on — so the restoration finale cannot
be walked around (docs/playtest-2026-09-29-endgame-egg-pad.md). That is only
true if the engine's own hatch test passes for an Avatar standing where a
teleport puts him, and fails everywhere teleporter 211 (the active trigger
back into Map 18) would fire, so standing at the return trigger does not
retrigger the finale.

The arithmetic is the engine's, not a closed box. EggHatcherProcess::run
(world/egg_hatcher_process.cpp), with the egg at (ex, ey, ez), its ranges
xr = (npcNum >> 4) & 0xF, yr = npcNum & 0xF (Egg::getXRange/getYRange), and
the Avatar's reference point (px, py, pz) and footpad (axs, ays):

    x1 = ex - 32*xr   x2 = ex + 32*xr   (same for y)
    hatch iff  x1 <= px  and  px - axs < x2
          and  y1 <= py  and  py - ays < y2
          and  ez - 48 < pz <= ez + 48

The footpad is half-open like every U8 box ((px - axs, px]), so the set of
reference points that hatch an egg is [x1, x2 + axs) on x — wider on the
far side by the body's own size. MainActor::teleport puts the Avatar's
reference point exactly on the target egg's location (main_actor.cpp,
`Actor::teleport(mapNum, pt.x, pt.y, pt.z)` after findDestination).

The Avatar may come back from Map 18 at either size (Tiny Tar wears off on
the way, or does not), so both bodies are checked: shape 1 (footpad 2x2 =
64x64) and the Tiny Tar body TypeTinytar resolves to (867 since
2026-10-08, footpad 1x1 = 32x32), read from TYPEFLAG.

Both sources are checked: the map builders' in-memory output (so a builder
edit fails here before any rebuild) and, when present, the BUILT FIXED.DAT
(what ships, per .claude/rules/map-geometry.md "test the built artifact").

    python3 agents/map-populator/src/test_endgame_hatch_box.py

Plain script: exit 0 on pass, 1 on fail.
"""

import contextlib
import io
import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)
sys.path.append(os.path.join(BASE_DIR, 'agents', 'usecode-compiler', 'src'))

from u8_map import MapArchive, MapItem          # noqa: E402
from parse_typeflag import load_typeflag        # noqa: E402
from u8c_symbols import TYPE_SHAPES             # noqa: E402

FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
TYPEFLAG = os.path.join(BASE_DIR, 'shared', 'build', 'TYPEFLAG.DAT')
MAP_10 = 10
EGGENDGAME_QUALITY = 299
TELEPORT_TARGET_ID = 210       # the arrival pad from Map 18
TELEPORT_TRIGGER_ID = 211      # the active trigger back into Map 18
RANGE_MUL = 32                 # egg_hatcher_process.cpp: GAME_IS_U8 ? 32 : 64
Z_RANGE = 48                   # egg_hatcher_process.cpp: z_range
TINY = TYPE_SHAPES['TypeTinytar']
AVATAR_SHAPES = {'full-size (shape 1)': 1, f'Tiny Tar (shape {TINY})': TINY}

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def hatch_span(egg, axs, ays):
    """Half-open reference-point spans [lo, hi) on x and y, and the
    (lo, hi] z span, over which the engine hatches `egg` for a body whose
    footpad is axs x ays."""
    xr = (egg.npcnum >> 4) & 0xF
    yr = egg.npcnum & 0xF
    x1, x2 = egg.x - RANGE_MUL * xr, egg.x + RANGE_MUL * xr
    y1, y2 = egg.y - RANGE_MUL * yr, egg.y + RANGE_MUL * yr
    return ((x1, x2 + axs), (y1, y2 + ays),
            (egg.z - Z_RANGE, egg.z + Z_RANGE))


def hatches(egg, px, py, pz, axs, ays):
    """EggHatcherProcess::run's test, verbatim."""
    xr = (egg.npcnum >> 4) & 0xF
    yr = egg.npcnum & 0xF
    x1, x2 = egg.x - RANGE_MUL * xr, egg.x + RANGE_MUL * xr
    y1, y2 = egg.y - RANGE_MUL * yr, egg.y + RANGE_MUL * yr
    return (x1 <= px and px - axs < x2 and y1 <= py and py - ays < y2 and
            egg.z - Z_RANGE < pz <= egg.z + Z_RANGE)


def spans_meet(a, b):
    """Two hatch regions share a reference point (x, y half-open [lo, hi),
    z half-open (lo, hi])."""
    (ax, ay, az), (bx, by, bz) = a, b
    return (max(ax[0], bx[0]) < min(ax[1], bx[1]) and
            max(ay[0], by[0]) < min(ay[1], by[1]) and
            max(az[0], bz[0]) < min(az[1], bz[1]))


def builder_items():
    from build_map_10 import build_map_10
    with contextlib.redirect_stdout(io.StringIO()):
        built = build_map_10()
    # Through the record codec, so the fields are exactly what ships.
    return [MapItem.from_bytes(it.to_bytes()) for it in built]


tf_path = TYPEFLAG if os.path.exists(TYPEFLAG) else None
shapes = load_typeflag(tf_path)
bodies = {name: (shapes[s].footpad_x * 32, shapes[s].footpad_y * 32)
          for name, s in AVATAR_SHAPES.items()}

sources = [("builders' in-memory output", builder_items())]
if os.path.exists(FIXED):
    sources.append(('built FIXED.DAT', MapArchive(FIXED).get_map_items(MAP_10)))
else:
    print('  (shared/build/FIXED.DAT absent — builder output only)')

for label, items in sources:
    print('=' * 70)
    print(f'EggEndgame vs the Map 10 <-> Map 18 teleport pair — {label}')

    eggs = [i for i in items
            if i.shape == 73 and i.quality == EGGENDGAME_QUALITY]
    targets = [i for i in items
               if i.is_teleport_target and i.quality == TELEPORT_TARGET_ID]
    triggers = [i for i in items
                if i.is_teleporter and (i.quality & 0xFF) == TELEPORT_TRIGGER_ID]

    check(f'exactly one EggEndgame (quality {EGGENDGAME_QUALITY}) on Map 10',
          len(eggs) == 1, f'found {len(eggs)}')
    check(f'exactly one teleport TARGET egg {TELEPORT_TARGET_ID} on Map 10',
          len(targets) == 1, f'found {len(targets)}')
    check(f'exactly one teleporter (trigger) egg {TELEPORT_TRIGGER_ID}',
          len(triggers) == 1, f'found {len(triggers)}')
    if not (eggs and targets and triggers):
        continue
    egg, target, trigger = eggs[0], targets[0], triggers[0]

    check('EggEndgame has a non-zero hatch range (npcNum != 0)',
          egg.npcnum != 0, f'npcNum=0x{egg.npcnum:02X}')
    print(f'  EggEndgame  ({egg.x},{egg.y},{egg.z}) npcNum=0x{egg.npcnum:02X}')
    print(f'  target {TELEPORT_TARGET_ID}  ({target.x},{target.y},{target.z})')
    print(f'  trigger {TELEPORT_TRIGGER_ID} ({trigger.x},{trigger.y},'
          f'{trigger.z}) npcNum=0x{trigger.npcnum:02X}')

    for name, (axs, ays) in bodies.items():
        check(f'{name} landing on target {TELEPORT_TARGET_ID} hatches '
              f'EggEndgame',
              hatches(egg, target.x, target.y, target.z, axs, ays),
              f'arrival point ({target.x},{target.y},{target.z}) fails the '
              f'engine test for a {axs}x{ays} body — the finale could be '
              f'walked around')
        span_e = hatch_span(egg, axs, ays)
        span_t = hatch_span(trigger, axs, ays)
        print(f'    {name}: EggEndgame hatches for x [{span_e[0][0]},'
              f'{span_e[0][1]}) y [{span_e[1][0]},{span_e[1][1]}); trigger '
              f'{TELEPORT_TRIGGER_ID} for x [{span_t[0][0]},{span_t[0][1]}) '
              f'y [{span_t[1][0]},{span_t[1][1]})')
        check(f'{name}: no position hatches both EggEndgame and trigger '
              f'{TELEPORT_TRIGGER_ID}',
              not spans_meet(span_e, span_t),
              'the regions meet — standing at the return trigger would '
              'also hatch the finale egg')
        check(f'{name}: the arrival point on target {TELEPORT_TARGET_ID} '
              f'does not hatch trigger {TELEPORT_TRIGGER_ID} (the pad is '
              f'not inside the return trigger)',
              not hatches(trigger, target.x, target.y, target.z, axs, ays))

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

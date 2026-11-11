#!/usr/bin/env python3
"""
test_sanctum_clearance.py — the crack-to-altar route through Map 18's Inner
Sanctum, checked with the engine's own box arithmetic.

WHY THIS FILE EXISTS (2026-09-13). Placing the three Zealan gods (shape 860)
did two things to the tightest room in the game at once: it deleted nine
rock-spire props that had been standing as blockers, and it gave the gods a
192-unit footpad where the donor shape's was 96. Net effect on the route was
not obvious from either change alone, and nothing covered it:

  - `test_crack_geometry.py` reads the patched TYPEFLAG, so it covers the
    APERTURE IN THE NORTH WALL and nothing south of it.
  - `test_route_reach.py` is FIXED.DAT-only by its own docstring. It never
    loads a footpad, so a shape that grew to four times its floor area is
    invisible to it. A green estate implied a coverage that did not exist.

The room has been rebuilt twice since. 2026-09-14: a flagstone hall with a
processional way and a two-tier dais. 2026-10-17: the 1994 screenshot
screen04 — a cave shrine behind the crack, the gods on their retail plinths
(37 frames 10/13, top z 16) on the 1994 triangle, the altar on the bare
floor, no dais (build_map_18.SCREEN04). What this file guards now is what
that layout could break: the gods' boxes (the 1994 64x64 bases, footpad
2x2x7) at their pins, the entry lane from the crack, the altar and the
ceremony egg on the floor with screen04's Avatar inside the egg's box, and
no furniture in the lane.

Same instrument as `test_crack_geometry`: `Box::overlaps` verbatim over the
BUILT FIXED.DAT with globs expanded, so it tests what ships.
"""

import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_map import MapArchive                      # noqa: E402
sys.path.insert(0, os.path.join(BASE_DIR, 'agents', 'usecode-compiler', 'src'))
from map_preview import GlobReader, expand_globs   # noqa: E402
from parse_typeflag import load_typeflag           # noqa: E402

FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
TYPEFLAG = os.path.join(BASE_DIR, 'shared', 'build', 'TYPEFLAG.DAT')

SI_SOLID = 0x02
BODY_TINY = 32          # shape 867 — the shrunken Avatar, who is who enters
BODY_FULL = 64          # shape 1   — the normal Avatar

GODS_SHAPE = 860
GODS_FOOTPAD = (2, 2, 7)
GOD_Z = 16              # on the plinth top
# screen04's triangle (vignettes/screen04.json placement.pin_moves).
GOD_POS = [(2783, 8031), (3039, 7903), (3039, 8415)]
PLINTH_SHAPE = 37       # retail plinth, frame 10 at z 0 and 13 at z 8

# The entry lane: from the crack (x 2817..2879 on y=6143) south through the
# antechamber, probed just inside the wall and either side of its middle.
LANE_ROWS = [6300, 6655, 6784]
LANE_LO, LANE_HI = 2700, 2880
LANE_END = 6783

ALTAR = (3127, 8175, 0)
CEREMONY_EGG_QUALITY = 296   # EggAOCeremony
AVATAR_SPOT = (3256, 8152)   # where screen04 shows the Avatar at the altar
NO_DAIS = (113, 70)          # the 2026-09-14 way and dais tiles

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def overlaps(a, b):
    """ultima8/misc/box.h Box::overlaps, verbatim. Half-open boxes (x-xd, x];
    every comparison is <=, so an exact fit is a MISS."""
    ax, ay, az, axd, ayd, azd = a
    bx, by, bz, bxd, byd, bzd = b
    if ax <= bx - bxd or bx <= ax - axd:
        return False
    if ay <= by - byd or by <= ay - ayd:
        return False
    if az + azd <= bz or bz + bzd <= az:
        return False
    return True


print('=' * 70)
print('Inner Sanctum clearance — the gods against the crack-to-altar route')

if not os.path.exists(FIXED) or not os.path.exists(TYPEFLAG):
    print('  shared/build artifacts absent — run tools/build_artifacts.sh')
    sys.exit(1)

shapes = load_typeflag(TYPEFLAG)
items = expand_globs(MapArchive(FIXED).get_map_items(18), GlobReader())

blockers = []
for it in items:
    si = shapes[it.shape]
    xd, yd, zd = si.footpad_x * 32, si.footpad_y * 32, si.footpad_z * 8
    if not (si.flags0 & SI_SOLID) or zd <= 0:
        continue
    blockers.append((it.x, it.y, it.z, xd, yd, zd, it.shape))


def runs_free(bs, y, body, lo, hi, step=4):
    """Contiguous x runs where a body-sized box at (x, y) hits nothing."""
    free = [x for x in range(lo, hi, step)
            if not any(overlaps((x, y, 0, body, body, 32), b[:6]) for b in bs)]
    out, start, prev = [], None, None
    for x in free:
        if start is None:
            start = x
        elif x - prev > step:
            out.append((start, prev))
            start = x
        prev = x
    if start is not None:
        out.append((start, prev))
    return out


# ── 0. The two shape tables agree about the gods ─────────────────────────
# The map builders' SHAPE_* constants and u8c_symbols' TYPE_SHAPES are
# separate tables that already disagree in places (.claude/rules/shape-ids.md).
# They must not disagree here: build_map_18 places SHAPE_GOD_CRYSTAL, and
# AOSCENE/TEMPLENT free whatever TypeZealanGod resolves to. If those drift,
# the ceremony silently frees nothing — a foreach over a shape that is not on
# the map matches zero items and reports no error.
try:
    from lv_shapes import SHAPE_GOD_CRYSTAL          # noqa: E402
    from u8c_symbols import TYPE_SHAPES              # noqa: E402
    check('TypeZealanGod and SHAPE_GOD_CRYSTAL name the same shape',
          TYPE_SHAPES.get('TypeZealanGod') == SHAPE_GOD_CRYSTAL == GODS_SHAPE,
          f"TYPE_SHAPES={TYPE_SHAPES.get('TypeZealanGod')} "
          f"SHAPE_GOD_CRYSTAL={SHAPE_GOD_CRYSTAL} — the ceremony would free "
          f"nothing, silently")
except ImportError as e:
    check('both shape tables are importable', False, str(e))


# ── 1. The gods are solid, at the footpad the injector authored ──────────
si = shapes[GODS_SHAPE]
check('shape 860 is SI_SOLID', bool(si.flags0 & SI_SOLID),
      'a god you can walk through is not an obstacle at all')
check(f'shape 860 carries the authored {GODS_FOOTPAD} footpad (the 1994 '
      f'64x64 base, Timyra\'s 56 tall)',
      (si.footpad_x, si.footpad_y, si.footpad_z) == GODS_FOOTPAD,
      f'got {si.footpad_x}x{si.footpad_y}x{si.footpad_z} — donor 443 is '
      f'3x3x3, so this reads as the TYPEFLAG patch having been dropped')

gods = [b for b in blockers if b[6] == GODS_SHAPE]
check('all three gods are in the built FIXED.DAT as solid boxes',
      len(gods) == 3, f'{len(gods)} found')
check("the gods stand on screen04's triangle",
      sorted((b[0], b[1]) for b in gods) == sorted(GOD_POS),
      f'{sorted((b[0], b[1]) for b in gods)}')
plinths = [b for b in blockers if b[6] == PLINTH_SHAPE]
check('each god stands on a plinth top (z 16): a two-tile retail plinth at '
      'z 0 and 8 under her box',
      all(b[2] == GOD_Z for b in gods) and all(
          sum(1 for p in plinths if p[2] in (0, 8) and p[2] + p[5] <= GOD_Z
              and overlaps((g[0], g[1], p[2], g[3], g[4], p[5]), p[:6])) == 2
          for g in gods),
      f'{[(b[0], b[1], b[2]) for b in gods]}')

# Positive check: the box actually obstructs. Everything else below only
# shows the gods are NOT in the way, which an unpatched TYPEFLAG also passes.
check('a body pressed into a god is refused',
      all(any(overlaps((gx - 16, gy - 16, GOD_Z, BODY_FULL, BODY_FULL, 32),
                       b[:6]) for b in gods)
          for gx, gy in GOD_POS))

# ── 2. The entry lane from the crack is open ─────────────────────────────
for y in LANE_ROWS:
    r = runs_free(blockers, y, BODY_TINY, LANE_LO, LANE_HI)
    widest = max((hi - lo for lo, hi in r), default=0)
    check(f'the shrunken Avatar has a lane south at y={y}',
          bool(r), 'the sanctum is sealed against the player who can enter')
    check(f'...with real margin at y={y}, not an exact fit',
          widest >= 32, f'widest run is {widest} units')

# ── 2a. No dais: the altar stands on the floor ───────────────────────────
dais = [b for b in blockers if b[6] in NO_DAIS and b[1] > 6144]
check('the sanctum has no dais or processional way (screen04 shows bare '
      'floor round the altar)', not dais, f'{[(b[6], b[0], b[1]) for b in dais[:4]]}')
altar = [b for b in blockers if b[6] == 550]
check("the altar stands on the floor at screen04's spot",
      len(altar) == 1 and tuple(altar[0][:3]) == ALTAR,
      f'{[(a[0], a[1], a[2]) for a in altar]}')

# ── 2c. The ceremony egg hatches for an Avatar beside the altar ──────────
# The egg is not solid, so it is not in `blockers`; find it in the items.
eggs = [it for it in items if it.shape == 73
        and it.quality == CEREMONY_EGG_QUALITY]
check('exactly one EggAOCeremony on the map', len(eggs) == 1, f'{len(eggs)}')
if eggs:
    e = eggs[0]
    ex, ey, ez = e.x, e.y, e.z
    check('the ceremony egg is on the floor with the altar', ez == ALTAR[2],
          f'egg z={ez}')
    # EggHatcherProcess::run hatches when the Avatar is inside the egg's
    # x/y range AND `egg.z - 48 < avatar.z <= egg.z + 48`.
    EGG_Z_RANGE = 48
    check('...inside the hatcher\'s z window for an Avatar on the floor',
          ez - EGG_Z_RANGE < 0 <= ez + EGG_Z_RANGE,
          f'egg z={ez}: window ({ez - EGG_Z_RANGE}, {ez + EGG_Z_RANGE}]')
    rx, ry = 32 * (e.npcnum & 0xF), 32 * (e.npcnum >> 4)
    check("...and its range box holds screen04's Avatar, beside the altar",
          ex - rx <= AVATAR_SPOT[0] <= ex + rx
          and ey - ry <= AVATAR_SPOT[1] <= ey + ry,
          f'egg at ({ex},{ey}) npcnum={e.npcnum:#x}')

# ── 3. Nothing solid stands in the entry lane ────────────────────────────
# The lane is x 2700..2880 from the crack line down to y 6783; the only
# solid things allowed to touch it are the wall line itself (y <= 6175). A
# rubble pile, a bone heap or a wall piece drifting into it is the
# regression a future dressing pass could plausibly cause.
lane = (LANE_HI, LANE_END, 0, LANE_HI - LANE_LO, LANE_END - 6144, 40)
intruders = [b for b in blockers if b[1] > 6200 and overlaps(lane, b[:6])]
check('nothing solid stands in the entry lane', not intruders,
      f'{[(b[6], b[0], b[1]) for b in intruders[:6]]}')

print()
print('=' * 70)
if failed:
    print(f'FAILED: {passed} passed, {failed} failed')
    sys.exit(1)
print(f'OK: {passed} passed, 0 failed')

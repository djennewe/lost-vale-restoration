#!/usr/bin/env python3
"""
test_harpie_corpses.py — a dead lane harpie never seals Map 13's climb.

WHY (docs/playtest-2026-10-18-armed-harpie-pair.md finding 2,
docs/playtest-2026-10-24-harpies-one-at-a-time.md finding 2). A dead
harpie stays where it fell, solid, at its full TYPEFLAG box: shape 873
carries the torax 120's row, footpad (4,4,4) and SI_SOLID, so the box is
128 x 128 x 32. That is retail behaviour, not an LV defect:

  * Actor::die / dieU8 (actor.cpp:1299-1412) sets ACT_DEAD and FLG_BROKEN,
    plays the death animation and leaves the actor in the world. Nothing in
    it changes the shape, the flags or the box.
  * CurrentMap::getPositionInfo (current_map.cpp:710-793) and sweepTest
    block on SI_SOLID alone. No dead-actor or FLG_BROKEN exemption exists,
    so a retail torax's body blocks exactly as ours does.
  * No usecode runs at a U8 death: receiveHitU8 calls die() directly, and
    no retail ANIM.DAT frame carries AFF_USECODE (0x4000, the flag
    behind calledFromAnim), whatever the action or shape. Every retail
    monster class (TORAX 120, TROLL, GHOUL, DEMON, GHOST, SKELETON, ...)
    has look() alone, and none disposes of its body.
  * The body goes when it leaves the fast area (item.cpp:2000, the
    FLG_FAST_ONLY destroy), as playtest 10-24 finding 4 saw.

So a body straight ahead stops a held walk, as any solid does. The mover
retries a refused step only one heading right and left
(U8AvatarMoverProcess::step), and while the Avatar's box lies wholly
within the body's x span both retries hit it. That is 10-24's stall,
cleared by a sidestep. What the map must not do is let one body close the
way. This test holds that against the BUILT FIXED.DAT and TYPEFLAG.DAT.

LANES. The leg's harpies (build_map_13.HARPIE_FIRST, HARPIE_LANE and
HARPIE_TOP) hatch one at a time, so one body lies on the leg at a time
unless the player leads a later harpie back to an earlier one. A body is
laid at every position any of them can walk to from its egg on the
climb's north leg (y LEG_Y), on a CORPSE_STRIDE lattice, at the level it
stands on there. Then exact_reach floods the Avatar from the three lanes
160 south of the body to the three lanes 224 north of it. Every body must
leave the leg open. The three lanes are 384 wide
(build_map_13.CLIMB_WIDE), so one 128-wide body always leaves at least
128. Two bodies abreast could leave three gaps of about 43, which is why
the pair that hatched together (10-18 finding 2) could close it.

The summit is not covered here, by decision: one summit harpie's body in
the neck between screen01's boulder and the plateau's east edge, or in the
column below it, can close the walk to teleporter 209 until it leaves the
fast area, and walking back down the climb clears it. Douglas accepted
that on 2026-10-30, because any ground that widens the neck draws over
screen01's window (build_map_13, THE HARPIES).

    python3 agents/map-populator/src/test_harpie_corpses.py [FIXED.DAT]

Plain script: exit 0 on pass, 1 on fail.
"""

import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC_DIR)

import avatar_mover as am                                  # noqa: E402
from u8_map import MapArchive, MapItem                     # noqa: E402
from map_preview import GlobReader                         # noqa: E402
from parse_typeflag import load_typeflag                   # noqa: E402
from exact_reach import ExactReach, DEFAULT_TYPEFLAG       # noqa: E402
from lv_shapes import SHAPE_MON_HARPIE                     # noqa: E402
import lv_map13_tiers as T                                 # noqa: E402
from build_map_13 import (HARPIE_FIRST, HARPIE_FIRST_Z, HARPIE_LANE,  # noqa: E402
                          HARPIE_LANE_Z, HARPIE_TOP, CLIMB_Z_TOP, TILE,
                          climb_z)

CORPSE_STRIDE = 32           # body positions tried, world units
# The north leg's three lanes (x 4863-5247), as Avatar max-corner x at
# each lane's centre, and the leg's straight run between its bend at
# y 7935 and the turn west at y 1663: bodies to y 2111, whose probe ends
# 224 on, in the row south of the turn's bend square (y 1408-1791).
LANE_X = (4959, 5087, 5215)
LEG_ROI = (4500, 1700, 5700, 7900)
LEG_Y = (2111, 7600)
SEED_DY, TARGET_DY = 160, 224

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')
    return cond


def expand(items, roi):
    """Glob eggs expanded once, keeping every item whose box can reach
    within 256 of `roi` (a max corner up to 512 beyond its far side)."""
    gr = GlobReader()
    x0, y0, x1, y1 = roi
    out = []
    for it in items:
        subs = (gr.glob_to_items(it.quality, it.x, it.y, it.z & 0xFF)
                if it.is_glob_egg else [it])
        out.extend(s for s in subs
                   if x0 - 256 <= s.x <= x1 + 512 and
                   y0 - 256 <= s.y <= y1 + 512)
    return out


def body(it):
    return MapItem(x=it[0], y=it[1], z=it[2], shape=SHAPE_MON_HARPIE)


def harpie_spots(items, shapes, roi, eggs):
    """Every position (max corner, on the stride) a harpie walks to from
    `eggs`, with the level it stands on: where its body can fall."""
    si = shapes[SHAPE_MON_HARPIE]
    hb = (si.footpad_x * 32, si.footpad_y * 32, si.footpad_z * 8)
    er = ExactReach(items, shapes, roi, body=hb)
    reach, seeded = er.flood(eggs)
    spots = []
    for level, r in reach.items():
        for i, j in zip(*r.nonzero()):
            x, y = er.x_of(i), er.y_of(j)
            if (x + 1) % CORPSE_STRIDE == 0 and (y + 1) % CORPSE_STRIDE == 0:
                spots.append((x, y, level))
    return sorted(spots), len(seeded) == len(eggs)


def leg_z(y):
    return climb_z(T.corner(y // TILE))


def leg_open(items, shapes, extra, cy):
    roi = (4600, cy - 400, 5500, cy + 350)
    er = ExactReach(items + extra, shapes, roi)
    sy, ty = cy + SEED_DY, cy - TARGET_DY
    reach, seeded = er.flood([(x, sy, leg_z(sy)) for x in LANE_X])
    return bool(seeded) and any(
        er.reached_near(reach, x, ty, leg_z(ty), ring=24) for x in LANE_X)


def lanes(items, shapes):
    print('=' * 70)
    print('Map 13: one leg harpie\'s body anywhere it can fall on the north '
          'leg leaves the leg open')
    near = expand(items, LEG_ROI)
    eggs = [(*HARPIE_FIRST, HARPIE_FIRST_Z), (*HARPIE_LANE, HARPIE_LANE_Z),
            (*HARPIE_TOP, CLIMB_Z_TOP)]
    spots, ok = harpie_spots(near, shapes, LEG_ROI, eggs)
    check(f'the leg\'s eggs {eggs} each stand a harpie', ok)
    spots = [s for s in spots if LEG_Y[0] <= s[1] <= LEG_Y[1]]
    seals, probes = [], []
    for s in spots:
        if not leg_open(near, shapes, [body(s)], s[1]):
            (seals if leg_open(near, shapes, [], s[1]) else probes).append(s)
    check('with no body, the leg is open at every probe a body closed',
          not probes,
          f'{len(probes)} probes fail with no body, e.g. {probes[:4]}')
    check(f'none of {len(spots)} bodies closes the leg', spots and not seals,
          f'{len(seals)} close it, e.g. {seals[:4]}' if seals else
          'no body positions found')


def main():
    fixed = sys.argv[1] if len(sys.argv) > 1 else am.DEFAULT_FIXED
    for path in (fixed, DEFAULT_TYPEFLAG):
        if not os.path.exists(path):
            print(f'  {path} absent — run tools/build_artifacts.sh')
            return 1
    items = list(MapArchive(fixed).get_map_items(13))
    shapes = load_typeflag(DEFAULT_TYPEFLAG)
    lanes(items, shapes)
    print()
    print('=' * 70)
    print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, '
          f'{failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())

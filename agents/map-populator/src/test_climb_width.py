#!/usr/bin/env python3
"""
test_climb_width.py — Map 13's climb leaves a walking Avatar room to
stray, from its foot to the summit.

WHY (docs/playtest-2026-10-11-full-run-part6.md finding 2). The climb was
one 128-unit tile wide from the warning zone to the end of the narrow
ledge. The engine stands an actor only while his bottom centre is over
land (exact_reach.mask: `midx = x - bxd/2`), so his centre had exactly
the tile's 128 units to wander in. In-engine a walking Avatar dropped to
z 0 six times in one climb, at x 4005-4081 y 7176-7679 (z 24-40, round
the bones on the ledge) and at the switchback's bends (4295,5388,z66) and
(4396,5474,z76). The mover retries every refused step one heading right
or left (U8AvatarMoverProcess::step), so a slide at a riser, a bend or the
bones moves him sideways, and on one tile that soon takes his centre past
the edge. The climb is now three tiles wide (build_map_13.CLIMB_WIDE).

1. MARGIN. exact_reach over the BUILT FIXED.DAT, every standable position
   of each level shaved by EROSION lattice cells (8 units each) wherever
   the ground at that level and the levels a step away (within 8) ends in
   a drop. Positions a solid blocks count as ground: a wall or a boulder
   is an edge he cannot step off.
   Shaving the union, not each level, keeps the risers: the row at z and
   the row at z+4 meet, and eroding each alone would cut every seam. The
   foot of the climb must still reach the summit, so every position on the
   route has EROSION * 8 = 64 units — a body width — of standing ground on
   either side. One tile leaves 120 positions across; the shave takes 128.
2. HOLDS. avatar_mover.hold, the engine's held-input movement, along every
   leg of build_map_13.CLIMB_WAYPOINTS: from one tile into the leg, the
   body on the centre line and 16 units either side, facing along the
   leg, every walking mode (mouse or keyboard, either step parity) must
   reach the leg's far end with no fall on the way and with the body's
   centre over a climb cell (climb_cells) at every position it passes on
   the raised climb (between the valley at its foot and the summit).
3. RUNNING HOLDS (2026-10-11, docs/playtest-2026-10-11-fix7.md finding 1).
   The same for a mouse run, mid-stride and from a standstill. A run
   drifted right of its heading on every uphill leg, off the lane onto the
   ledge faces' tops and on the east leg down to z 0: its 56- and 64-unit
   frames are swept, the sweep meets the next tile's top 4 higher, and the
   mover retries one heading right first. Before build_map_13's run curbs
   the lower N, E and upper N legs failed here, ending at (4244,8652,16),
   (4856,5976,56) and (4312,2792,100); the playtest's runs ended at
   (4148,8108,24), (4577,5950,52) and (4272,2764,100).
   On the lower N leg 8 of 16 standing mouse runs stepped off its
   uncurbed lowest stretch, e.g. at (4272,9408,4), before 2026-10-11's
   curbs on both lane edges (FIXED 09bde917).
   KEYBOARD RUNS (Shift+Up, docs/playtest-2026-10-11-fix9.md C1): the
   same, the mover stepping the Avatar's own facing, so a refused step's
   slide turns him for good. In-engine 4 of 5 left the lower N leg, east
   and west, and ended at z 0. Its holds include the playtest's start
   (4064,10000) (LEG_STARTS). On FIXED 09bde917 all 16 lower N holds
   failed (west off the edge at (3860,8412,20), east off the lowest
   stretch at (4270,9586,4)), and 4 E and 6 upper N holds went off the
   uncurbed left edge, e.g. (4844,5532,56) and (3864,3336,96).
4. FOOT (docs/playtest-2026-10-11-fix7.md finding 2). Holds N in every
   mode from pad 207's row, x 4096 +/- 112, and from the playtest's start
   (4050,10958) must pass the ruined wall at the climb's foot. Its gap was
   one tile (3967,4095] beside a pad at x 4096; a run slid along the east
   stub and wedged at (4239,10816). Before the gap was widened to the
   climb's three lanes, 76 of 256 holds failed.
5. PAST THE BENDS (docs/playtest-2026-10-11-fix9.md C1 bends). Every
   hold along a leg that ends at a bend, carried on in the leg's heading
   for PAST_SECONDS beyond its end, every mode, runs also from a
   standstill, must not fall and must keep the body's centre over the
   climb. In-engine E held past the E->N bend went off its east side 3 of
   3, and W held past the W->N bend off its west side 3 of 4. On FIXED
   09bde917 all four legs failed: 36, 29, 28 and 36 holds, e.g. off the
   W->N bend's west side at (3864,5200,76).

    python3 agents/map-populator/src/test_climb_width.py [FIXED.DAT]

Plain script: exit 0 on pass, 1 on fail.
"""

import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC_DIR)

import avatar_mover as am                         # noqa: E402
from u8_map import MapArchive                     # noqa: E402
from parse_typeflag import load_typeflag          # noqa: E402
from exact_reach import ExactReach, DEFAULT_TYPEFLAG  # noqa: E402
from build_map_13 import (climb_tiles, climb_cells, CLIMB_WAYPOINTS,  # noqa: E402
                          TILE, CLIMB_Z_TOP, lanes_at, spur_ground,
                          summit_cells)

ROI = (1500, 0, 6700, 12300)       # Map 13's climb with a margin
EROSION = 8                        # lattice cells: 64 units, a body width
NEAR_Z = 8                         # a walking step changes z by 0, 4 or 8
OFFSETS = (-16, 0, 16)             # across the leg, from the centre line
SPEED = 300                        # units a second, under a walk's ~450
PAST_SECONDS = 3                   # a hold carried on beyond a bend
# Starts beyond each leg's own, by leg index: the fix9 playtest's keyboard
# runs up the lower N leg set off from (4064,10000).
LEG_STARTS = {0: [(4064, 10000, 4)]}

# ((mouse, run, firststep), standing) per kind of hold. Walking: every mode
# either way from mid-stride. Running: mid-stride and from a standstill
# (the first animation then a walk, as when the player sets off).
WALKS = [(m, False) for m in am.MODES if not m[1]]
RUNS = [(m, s) for m in am.MODES if m[1] for s in (False, True)]
MOUSE_RUNS = [(m, s) for (m, s) in RUNS if m[0]]
KEY_RUNS = [(m, s) for (m, s) in RUNS if not m[0]]

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


class MarginReach(ExactReach):
    """ExactReach whose standable set keeps EROSION cells of ground at its
    own and the neighbouring levels on every side."""

    def __init__(self, *a, erosion, **kw):
        super().__init__(*a, **kw)
        self.erosion = erosion
        self._margin = {}

    def mask(self, level):
        if level in self._margin:
            return self._margin[level]
        own = ExactReach.mask(self, level)
        # Ground is where he stands or cannot go: a wall or a boulder is an
        # edge he cannot step off, so only a drop is shaved.
        ground = own | self.blocked(level)
        for other in self.levels:
            if other != level and abs(other - level) <= NEAR_Z:
                ground |= ExactReach.mask(self, other)
        for _ in range(self.erosion):
            e = ground.copy()
            e[1:, :] &= ground[:-1, :]
            e[:-1, :] &= ground[1:, :]
            e[:, 1:] &= ground[:, :-1]
            e[:, :-1] &= ground[:, 1:]
            ground = e
        self._margin[level] = own & ground
        return self._margin[level]


def legs():
    """(first tile index, last tile index, heading) per waypoint leg."""
    out, k = [], 0
    for (ax, ay), (bx, by) in zip(CLIMB_WAYPOINTS, CLIMB_WAYPOINTS[1:]):
        n = (abs(bx - ax) + abs(by - ay)) // TILE
        h = ('N' if by < ay else 'S') if by != ay else \
            ('E' if bx > ax else 'W')
        out.append((k, k + n, h))
        k += n
    return out


def margin(items, tiles):
    print('=' * 70)
    print(f'Map 13: foot to summit with {EROSION * 8} units of ground either '
          f'side of the body')
    er = MarginReach(items, load_typeflag(DEFAULT_TYPEFLAG), ROI,
                     erosion=EROSION)
    fx, fy, fz = tiles[1]                  # the first tile up off the valley
    reach, seeded = er.flood([(fx - 32, fy - 32, fz)])
    check(f'the climb\'s foot ({fx - 32},{fy - 32},z{fz}) keeps its margin',
          bool(seeded))
    reached = {}
    for k, (x, y, z) in enumerate(tiles):
        reached[k] = er.reached_near(reach, x - 32, y - 32, z, ring=32)
    lost = [k for k in sorted(reached) if k and not reached[k]]
    first = tiles[lost[0]] if lost else None
    check(f'every path tile up to the plateau edge (z{CLIMB_Z_TOP}) is '
          f'reached', not lost,
          f'{len(lost)} of {len(tiles)} unreached, the first ({first[0]},'
          f'{first[1]},z{first[2]})' if lost else '')


def holds(items, tiles, what, modes, past=False):
    """Every hold in `modes` along every leg must reach the leg's end with
    no fall and the body's centre over a climb cell. `past`: the legs that
    end at a bend only, each hold carried on PAST_SECONDS beyond the end
    and judged over its whole trail."""
    print('=' * 70)
    print(f'Map 13: held {what} input along every leg of the climb'
          f'{", carried past its bend" if past else ""}')
    world = am.World(items, am.load_shapes(), ROI)
    anims = am.load_anims()
    cells = climb_cells()
    # The climb's one side opening (build_map_13.CLIMB_SPURS, 2026-10-17)
    # leads onto screen14's skull ring path: a hold that turns in there is
    # on walkable, curbed ground, not off the climb.
    side = {(TILE * cx + TILE - 1, TILE * cy + TILE - 1): z
            for (cx, cy), z in spur_ground().items()}
    cells = {**side, **cells}
    # The raised climb, between its two open ends: the valley at its foot
    # (south of the first tile above z 0) and the summit plateau
    # (build_map_13.summit_cells: since 2026-10-17 the climb enters it at
    # its north-east corner, so no y bounds it, as SUMMIT_Y1 did). A
    # keyboard run turned back at a bend follows the lanes out of either
    # end.
    foot_y = next(y for (_, y, z) in tiles if z > 0)
    summit = set(summit_cells())

    def raised(p):
        return p[1] - 32 <= foot_y and \
            ((p[0] - 32) // TILE, (p[1] - 32) // TILE) not in summit

    def off_climb(p):
        # The cell (cx - 128, cx] under the body's centre (x - 32, y - 32),
        # and the body no lower than a step below its tile.
        # The cell's max corner on the climb's own lattice (the tiles sit
        # on 127 mod 128 since 2026-10-17, on 0 mod 128 before).
        ox, oy = CLIMB_WAYPOINTS[0][0] % TILE, CLIMB_WAYPOINTS[0][1] % TILE
        c = (-(-(p[0] - 32 - ox) // TILE) * TILE + ox,
             -(-(p[1] - 32 - oy) // TILE) * TILE + oy)
        return raised(p) and (c not in cells or p[2] < cells[c] - NEAR_Z)

    all_legs = legs()
    for li, (k0, k1, h) in enumerate(all_legs):
        if past and (li + 1 == len(all_legs) or all_legs[li + 1][2] == h):
            continue                              # no bend at its end
        x0, y0, z0 = tiles[k0]
        x1, y1, _ = tiles[k1]
        # The Avatar's position is his box's max corner, so a body centred
        # on a tile (x - 128, x] stands at x - 32.
        ux, uy = am.xf(am.DIRS[h]), am.yf(am.DIRS[h])
        ex, ey = x1 - 32, y1 - 32                 # centred on the last tile

        def done(p):                              # past the far end's centre
            return (p[0] - ex) * ux + (p[1] - ey) * uy >= 0

        seconds = (abs(x1 - x0) + abs(y1 - y0) + 2 * TILE) / SPEED + 2 + \
            (PAST_SECONDS if past else 0)
        wide = 2 * lanes_at(tiles[k0 + 1][1]) + 1
        starts = [(x0 - 32 + ux * TILE + off * (ux == 0),
                   y0 - 32 + uy * TILE + off * (uy == 0), z0)
                  for off in OFFSETS] + LEG_STARTS.get(li, [])
        bad = []
        for start in starts:
            for mode, standing in modes:
                falls = []
                out, _k, pos, _s, trail = am.hold(
                    world, anims, start, h, *mode, {}, seconds,
                    standing=standing, falls=falls)
                end = next((i for i, p in enumerate(trail) if done(p)),
                           None)
                span = trail if past or end is None else trail[:end]
                fell = [f for f in falls if f[0] in span and raised(f[0])]
                off = next((p for p in span if off_climb(p)), None)
                why = []
                if out == 'falls' and (past or end is None):
                    why.append(f'falls to his death at {pos}')
                if fell:
                    (fx, fy, fz), land = fell[0]
                    why.append(f'falls {fz} -> {land} at ({fx},{fy})')
                if off:
                    why.append(f'leaves the climb at {off}')
                if end is None:
                    why.append(f'{out} at {pos} short of the end')
                if why:
                    bad.append(f'from {start} {am.mode_name(*mode)}'
                               f'{" standing" if standing else ""}: '
                               + ', '.join(why) + f' (ends {out} at {pos})')
        n = len(starts) * len(modes)
        check(f'leg {h} ({x0},{y0},z{z0}) -> ({x1},{y1}), {wide} '
              f'tile{"s" * (wide > 1)} wide: {n} {what} holds reach its end'
              f'{f" and {PAST_SECONDS} s past" if past else ""} without a '
              f'fall, on the climb', not bad,
              f'{len(bad)} holds: ' + '; '.join(bad[:3]))


# 4. FOOT (2026-10-11, docs/playtest-2026-10-11-fix7.md finding 2). A run N
# off the arrival line wedged at (4239,10816) on the east stub of the ruined
# wall at the climb's foot: its gap was one tile, x (3967,4095], and pad
# 207 stands at x 4096, so a body straight north of the pad overlapped the
# stub by a unit. A mouse run there slid east along the stub's face into
# the corner (the model stops at (4240,10824)). From pad 207's row, the pad
# and 112 either side in 16s, and from the playtest's start, a hold N in
# every mode, mid-stride and from a standstill, must reach the climb's foot.
FOOT_PAD = 207
FOOT_SPREAD = 112
FOOT_STARTS = ((4050, 10958, 0),)       # the playtest's run N


def foot(items):
    print('=' * 70)
    print(f'Map 13: held input north from pad {FOOT_PAD} through the ruined '
          f'wall to the climb\'s foot')
    world = am.World(items, am.load_shapes(), ROI)
    anims = am.load_anims()
    pad, = [it for it in items if it.is_teleport_target
            and it.quality & 0xFF == FOOT_PAD]
    boxes = {it.quality & 0xFF: am.hatch_box(it) for it in items
             if it.is_teleporter}
    goal = CLIMB_WAYPOINTS[0][1]
    starts = [(x, pad.y, pad.z & 0xFF) for x in
              range(pad.x - FOOT_SPREAD, pad.x + FOOT_SPREAD + 1, 16)]
    starts += list(FOOT_STARTS)
    seconds = (pad.y - goal) / SPEED + 2
    bad = []
    for start in starts:
        for mode in am.MODES:
            for standing in (False, True):
                out, k, pos, _s, trail = am.hold(
                    world, anims, start, 'N', *mode, boxes, seconds,
                    standing=standing)
                if not any(p[1] <= goal for p in trail):
                    bad.append(f'from {start} {am.mode_name(*mode)}'
                               f'{" standing" if standing else ""}: {out}'
                               f'{f" {k}" if k else ""} at {pos}')
    check(f'{len(starts) * len(am.MODES) * 2} holds N from pad {FOOT_PAD}\'s '
          f'row (x {pad.x}+/-{FOOT_SPREAD}) and {FOOT_STARTS[0][:2]} reach '
          f'the climb\'s foot (y {goal})', not bad,
          f'{len(bad)} holds: ' + '; '.join(bad[:3]))



def main():
    fixed = sys.argv[1] if len(sys.argv) > 1 else am.DEFAULT_FIXED
    for path in (fixed, am.DEFAULT_ANIM, DEFAULT_TYPEFLAG):
        if not os.path.exists(path):
            print(f'  {path} absent — run tools/build_artifacts.sh')
            return 1
    items = list(MapArchive(fixed).get_map_items(13))
    tiles = climb_tiles()
    margin(items, tiles)
    holds(items, tiles, 'walking', WALKS)
    holds(items, tiles, 'mouse running', MOUSE_RUNS)
    holds(items, tiles, 'keyboard running', KEY_RUNS)
    holds(items, tiles, 'walking or running', WALKS + RUNS, past=True)
    foot(items)
    print()
    print('=' * 70)
    print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, '
          f'{failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())

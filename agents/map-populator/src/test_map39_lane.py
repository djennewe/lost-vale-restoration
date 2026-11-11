#!/usr/bin/env python3
"""
test_map39_lane.py: a player who does not cheat can WALK from Tenebrae to
the Lord British egg, judged with the ENGINE'S box arithmetic on the BUILT
FIXED.DAT, with every trigger box treated as a wall.

WHY (2026-10-09). docs/playtest-2026-10-09-full-run-1-18.md finding 1: the
only walking route from the city to the egg's field went through the anchor
box of the east gate's teleport egg to Map 40, so a walker reaching it was
teleported away; quest step 1's primary trigger could not be walked to.
Every test that existed walked from the egg outwards and stopped at the
field's edges; none asked whether the field could be reached at all.
build_map_39's lane (TENEBRAE_LANE_*) opens a tunnel through the gate wall.

The model is exact_reach.ExactReach (getPositionInfo and Box::overlaps
verbatim; a walk step changes z by 0, +-4 or +-8 and by nothing else), with
three things taken away from it:

  1. EVERY TRIGGER BOX. EggHatcherProcess::run (egg_hatcher_process.cpp:
     68-85) hatches an egg when the Avatar's reference point satisfies
     x1 <= x < x2 + 64, y1 <= y < y2 + 64 (x1/x2 = egg x -/+ 32*range, the
     64 the footpad) and egg z - 48 < z <= egg z + 48. Every egg on the map
     except the goal and the inert arrival pads (a frame-1 teleport egg's
     hatch does nothing) has that box removed from the walkable set: a
     teleport out, a monster spawn and a usecode egg all end the walk.
  2. WATER, plus a margin: a SEA tile is SOLID, so exact_reach would stand
     a body on it, and the engine drowns him (pathfind.DryMixin's lesson).
  3. SEAMS. The walkable set is eroded by EROSION lattice cells (8 units
     each) on every side before the flood, so a corridor survives only if it
     is at least about 64 + 2*8*EROSION units clear. That is the aperture
     rule (.claude/rules/map-geometry.md): a body width plus margin, never an
     exact fit.

Seeds: the arrival pad Map 40's east-gate teleporter (id 0) lands on, and
the city point the 10-09 report routed from. Goal: a reached position inside
the Lord British egg's own hatch box. Then two pins: with the lane's tunnel
masked there is NO path (the lane is what opened it, and the city is
otherwise sealed), and the route is printed as waypoints for a verifier.
"""

import os
import sys
from collections import deque

import numpy as np

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_map import MapArchive                           # noqa: E402
from map_preview import GlobReader, expand_globs        # noqa: E402
from parse_typeflag import load_typeflag                # noqa: E402
from exact_reach import (ExactReach, AVATAR_BODY, SI_SEA,  # noqa: E402
                         Z_SEARCH_OFFSETS_U8)
import build_map_39 as b39                              # noqa: E402

FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
TYPEFLAG = os.path.join(BASE_DIR, 'shared', 'build', 'TYPEFLAG.DAT')

MAP = 39
ROI = (10500, 13000, 22200, 21500)    # the city, the gate wall and the field
CITY = (18562, 14406, 48)             # the 10-09 report's city point
ARRIVAL_ID = 0                        # Map 40's east gate -> Map 39
EGG = (b39.TENEBRAE_EGG_X, b39.TENEBRAE_EGG_Y, b39.TENEBRAE_EGG_Z)
EGG_RANGE = ((b39.LB_EGG_NPCNUM >> 4) & 0xF, b39.LB_EGG_NPCNUM & 0xF)
WATER_MARGIN = 64                     # one body width of shore kept dry
EROSION = 3                           # lattice cells shaved off every edge
RANGE_MUL = 32                        # egg_hatcher_process.cpp, U8
Z_RANGE = 48
FOOTPAD = AVATAR_BODY[0]              # the 64 in "x - axs < x2"

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def hatch_box(x, y, z, npcnum):
    """Reference-point box [x0, x1) x [y0, y1), (z0, z1] the hatcher fires in."""
    xr, yr = (npcnum >> 4) & 0xF, npcnum & 0xF
    return (x - RANGE_MUL * xr, x + RANGE_MUL * xr + FOOTPAD,
            y - RANGE_MUL * yr, y + RANGE_MUL * yr + FOOTPAD,
            z - Z_RANGE, z + Z_RANGE)


class LaneReach(ExactReach):
    """ExactReach minus trigger boxes, water (with a margin) and seams."""

    def __init__(self, items, shapes, roi, forbid, seas, erosion, **kw):
        super().__init__(items, shapes, roi, **kw)
        self.forbid = list(forbid)
        self.seas = seas
        self.erosion = erosion
        self._lane = {}
        self.xs = self.X0 + np.arange(self.NX) * self.step
        self.ys = self.Y0 + np.arange(self.NY) * self.step

    def mask(self, level):
        if level in self._lane:
            return self._lane[level]
        m = super().mask(level).copy()
        for (x0, x1, y0, y1, z0, z1) in self.forbid:
            if z0 < level <= z1:
                m[np.ix_((self.xs >= x0) & (self.xs < x1),
                         (self.ys >= y0) & (self.ys < y1))] = False
        bx, by, _ = self.body
        w = WATER_MARGIN
        for (sx, sy, top, sxd, syd) in self.seas:
            if level - 8 <= top <= level + 8:
                i0, i1 = self._kx(sx - sxd - w, sx + bx + w)
                j0, j1 = self._ky(sy - syd - w, sy + by + w)
                if i0 <= i1 and j0 <= j1:
                    m[i0:i1 + 1, j0:j1 + 1] = False
        for _ in range(self.erosion):
            e = m.copy()
            e[1:, :] &= m[:-1, :]
            e[:-1, :] &= m[1:, :]
            e[:, 1:] &= m[:, :-1]
            e[:, :-1] &= m[:, 1:]
            m = e
        self._lane[level] = m
        return m

    def in_box(self, box):
        x0, x1, y0, y1, _z0, _z1 = box
        return np.ix_((self.xs >= x0) & (self.xs < x1),
                      (self.ys >= y0) & (self.ys < y1))


def reaches_egg(er, reach):
    box = hatch_box(*EGG, b39.LB_EGG_NPCNUM)
    sel = er.in_box(box)
    return [L for L, r in reach.items() if box[4] < L <= box[5] and r[sel].any()]


def route(er, seeds, box):
    """BFS with parents over the same lattice and z table, from the seeds to
    the first position inside the box. Returns (lattice path, waypoints)."""
    deltas = [d for d in Z_SEARCH_OFFSETS_U8 if abs(d) <= er.step_z]
    levels = set(er.levels)
    masks = {L: er.mask(L) for L in er.levels}
    x0, x1, y0, y1, z0, z1 = box
    prev, q = {}, deque()
    for s in seeds:
        prev[s] = None
        q.append(s)
    while q:
        cur = q.popleft()
        i, j, L = cur
        if x0 <= er.x_of(i) < x1 and y0 <= er.y_of(j) < y1 and z0 < L <= z1:
            path = []
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            path.reverse()
            return ([(er.x_of(i), er.y_of(j), L) for (i, j, L) in path],
                     waypoints(er, masks, path))
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if not (0 <= ni < er.NX and 0 <= nj < er.NY):
                continue
            for d in deltas:
                nL = L + d
                if nL in levels and masks[nL][ni, nj] and (ni, nj, nL) not in prev:
                    prev[(ni, nj, nL)] = cur
                    q.append((ni, nj, nL))
    return None


def waypoints(er, masks, path):
    """Pull the lattice path straight: from each waypoint, go to the farthest
    later path position whose straight segment stays on standable positions
    of one level (sampled every lattice step, on the eroded mask, so a leg
    keeps the same margin the flood demanded). A walker chases these one at
    a time."""
    def clear(a, b):
        (ia, ja, La), (ib, jb, Lb) = a, b
        if La != Lb:
            return False
        n = max(abs(ib - ia), abs(jb - ja))
        return all(masks[La][round(ia + (ib - ia) * t / n),
                             round(ja + (jb - ja) * t / n)]
                   for t in range(n + 1))
    out, a = [path[0]], 0
    while a < len(path) - 1:
        b = a + 1
        while b + 1 < len(path) and clear(path[a], path[b + 1]):
            b += 1
        out.append(path[b])
        a = b
    return [(er.x_of(i), er.y_of(j), L) for (i, j, L) in out]


print('=' * 70)
print('Map 39: walking from Tenebrae to the Lord British egg, triggers masked')

if not os.path.exists(FIXED) or not os.path.exists(TYPEFLAG):
    print('  shared/build artifacts absent: run tools/build_artifacts.sh')
    sys.exit(1)

shapes = load_typeflag(TYPEFLAG)
arch = MapArchive(FIXED)
raw = arch.get_map_items(MAP)
gr = GlobReader()

# Every hidden flat retains its exact support box and has visible underpaint.
roof_pieces = [i for i in b39.GlobReader().glob_to_items(
    b39.TENEBRAE_LANE_GLOB[3], *b39.TENEBRAE_LANE_GLOB[:3])
    if i.shape in (35, 564) and i.z == 136]
keys = {(i.x, i.y, i.z, i.shape, i.frame) for i in raw}
roof_errors = []
for roof in roof_pieces:
    large = roof.shape == 564
    solid, backdrop = (499, 895) if large else (763, 894)
    expected = {(roof.x, roof.y, roof.z, solid, 0),
                (roof.x - 4 * roof.z, roof.y - 4 * roof.z, 0, backdrop, 0)}
    old, new = shapes[roof.shape], shapes[solid]
    if not expected <= keys or (old.footpad_x, old.footpad_y, old.footpad_z) != (
            new.footpad_x, new.footpad_y, new.footpad_z):
        roof_errors.append((roof.x, roof.y, roof.shape))
    if shapes[backdrop].flags0 & 0x0E:
        roof_errors.append(('physical backdrop', backdrop))
check('each tunnel roof retains its support footprint and projected underpaint',
      len(roof_pieces) == 8 and not roof_errors, str(roof_errors))

backstops = {(x, 19967, 88, 497, 0) for x in (16127, 16255)}
backstops.update((16255, y, z, 498, 0)
                 for y in (19743, 19871, 19967) for z in (48, 88))
check('the hidden near wall keeps its 136-unit top and continuous east flank',
      backstops <= keys and shapes[497].footpad_z * 8 + 88 == 136
      and shapes[498].footpad_z * 8 + 88 == 136)

# The arrival pad: Map 40's teleporter to this map with id 0, and the
# frame-1 egg on this map that answers it.
tele = [e for e in arch.get_map_items(40)
        if e.is_teleporter and e.mapnum == MAP and e.quality - 256 == ARRIVAL_ID]
pads = [e for e in raw if e.is_teleport_target and e.quality == ARRIVAL_ID]
check('Map 40 carries the east-gate teleporter to Map 39 (id 0)', len(tele) == 1,
      f'{len(tele)} found')
check('Map 39 carries its arrival pad', len(pads) == 1, f'{len(pads)} found')
arrival = (pads[0].x, pads[0].y, pads[0].z & 0xFF) if pads else None

# Every egg the hatcher can fire, except the goal and the inert pads.
forbid = []
for e in raw:
    if e.x < 64 or e.shape >= len(shapes) or e.is_glob_egg:
        continue
    fam = shapes[e.shape].family_name or ''
    if 'EGG' not in fam or e.is_teleport_target:
        continue
    if (e.x, e.y, e.z & 0xFF) == EGG:
        continue
    forbid.append(hatch_box(e.x, e.y, e.z & 0xFF, e.npcnum))
east_gate = [e for e in raw if e.is_teleporter and e.mapnum == 40
             and (e.x, e.y) == (19600, 14072)]
check('the east gate trigger the 10-09 report names is on the map and masked',
      len(east_gate) == 1 and hatch_box(19600, 14072, 48, 0x94) in forbid,
      f'{east_gate}')

seas = []
for it in expand_globs(raw, gr):
    if it.x < 64 or it.shape >= len(shapes):
        continue
    si = shapes[it.shape]
    if si.flags0 & SI_SEA:
        seas.append((it.x, it.y, (it.z & 0xFF) + si.footpad_z * 8,
                     si.footpad_x * 32, si.footpad_y * 32))

er = LaneReach(raw, shapes, ROI, forbid, seas, EROSION, glob_reader=gr, step=8)
seeds_xyz = [s for s in (arrival, CITY) if s]
reach, seeded = er.flood(seeds_xyz)
check('both seeds stand on the city plateau (z 48)',
      len(seeded) == 2 and all(s[3] == 48 for s in seeded), f'{seeded}')
hit = reaches_egg(er, reach)
check('a walked path reaches the Lord British egg\'s hatch box from the city, '
      'every other trigger box masked, water kept %d clear, seams eroded '
      'by %d cells' % (WATER_MARGIN, EROSION), bool(hit), 'NO PATH')

# The lane is load-bearing: mask the tunnel and the city is sealed again.
tx0, tx1 = b39.TENEBRAE_LANE_FLOOR[0][0] - 127, b39.TENEBRAE_LANE_FLOOR[0][0]
tunnel = (tx0, tx1 + AVATAR_BODY[0], 19584, 19968 + AVATAR_BODY[1], -1, 255)
sealed = LaneReach(raw, shapes, ROI, forbid + [tunnel], seas, EROSION,
                   glob_reader=gr, step=8)
r2, _ = sealed.flood(seeds_xyz)
check('with the lane\'s tunnel masked there is no walked path (the city is '
      'otherwise sealed by its walls and teleport gates)',
      not reaches_egg(sealed, r2), 'another route exists: re-survey the lane')

if hit and arrival:
    # The route a verifier walks: from the arrival pad, where a player coming
    # from Map 40 through the east gate lands.
    i, j = er.index_of(arrival[0], arrival[1])
    pts, wps = route(er, [(i, j, seeded[0][3])],
                     hatch_box(*EGG, b39.LB_EGG_NPCNUM)) or ([], [])
    check('the route walks through the tunnel', any(
        tx0 < x <= tx1 and 19584 <= y <= 19968 for (x, y, _z) in pts),
        f'{wps}')
    if wps:
        print(f'  route from the arrival pad ({len(wps)} waypoints, the last '
              f'inside the hatch box):')
        for k in range(0, len(wps), 6):
            print('    ' + ' -> '.join(f'({x},{y},{z})'
                                       for (x, y, z) in wps[k:k + 6]))

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

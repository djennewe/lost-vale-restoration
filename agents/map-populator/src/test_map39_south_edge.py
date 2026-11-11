#!/usr/bin/env python3
"""
test_map39_south_edge.py: Tenebrae's grass edge, checked with the ENGINE'S
box arithmetic on the BUILT FIXED.DAT.

WHY (2026-10-03). The Lord British scene draws the player south across the
retail grass field, whose south edge (y=20479) drops 48 units into void.
The first fix (b356e42) put two oaks at x (16863, 17439] on a 6,400-unit
edge, and its message said "stops the drop". A player 100 units east or
west reached the identical drop. Nothing tested the claim.

Three instruments, all on the expanded built map:

  1. STRAIGHT SWEEPS. For every integer x along the south edge, can a
     64x40 body walk due south from the grass into the void band without
     overlapping a solid (`Box::overlaps`, half-open, verbatim)? The same
     sweeps run east along the field's east face, south along the avenue
     stub, and east along the stub's east edge. No x, y may leak.

  2. THE FLOOD. exact_reach.ExactReach floods every standing position the
     body can reach from the egg (void plates left out, so void is void).
     Any reached position with an unblocked neighbour that has nothing to
     stand on is an exposure. The only exposures allowed are the pinned
     open edges (build_map_39.TENEBRAE_OPEN_EDGES). Since 2026-10-09 the
     flood also walks the lane's tunnel through the gate wall, and the city
     beyond it inside the window. It cannot see a gap in the tunnel's side
     walls, though: "ground" here is any support top in xy, and the roof
     plates over the hollow count. Section 4 does see one (dropping one
     wall course failed it with 9 near-lane exits, 2026-10-09);
     test_map39_lane.py proves the lane itself.

  3. THE CLIMB AND THE BURIAL. No solid with a top in [56, 128) stands within
     one body width of an oak (a rung for climb72 on jump), and no oak box
     overlaps another solid.

Plus the stale-frame rule: no void cell within view of the field stays
unplated (south of y=20479 or east of x=20991).
"""

import os
import sys

import numpy as np

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_map import MapArchive                           # noqa: E402
from map_preview import GlobReader, expand_globs        # noqa: E402
from parse_typeflag import load_typeflag                # noqa: E402
from exact_reach import ExactReach, AVATAR_BODY         # noqa: E402
import lv_furnish as lf                                 # noqa: E402

FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
TYPEFLAG = os.path.join(BASE_DIR, 'shared', 'build', 'TYPEFLAG.DAT')

SI_SOLID = 0x02
SI_SEA = 0x04
SI_LAND = 0x08

OAK = 199
EGG = (17150, 19700, 48)          # the lane the Lord British egg stands on
BX, BY, BZ = AVATAR_BODY          # 64 x 64 x 40
GROUND = 48                       # the grass's own height
CLIMB = 72                        # Animation::climb72, the jump's reach

# Field extent, read from the built map (see build_map_39's docstring).
SOUTH_EDGE_Y = 20479              # last grass row's max y
EAST_FACE_X = 20479               # field's east face below the avenue stub
STUB_SOUTH_Y = 19967              # avenue stub's south edge (x 20480..20991)
STUB_EAST_X = 20991               # avenue stub's east edge
FIELD_NORTH_Y = 19480             # exposure scope: body anchor y >= this

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
    """ultima8/misc/box.h Box::overlaps, verbatim (see test_crack_geometry):
    boxes are half-open (x-xd, x], so an exact fit is a miss."""
    ax, ay, az, axd, ayd, azd = a
    bx, by, bz, bxd, byd, bzd = b
    if ax <= bx - bxd or bx <= ax - axd:
        return False
    if ay <= by - byd or by <= ay - ayd:
        return False
    if az + azd <= bz or bz + bzd <= az:
        return False
    return True


def blocks_any(intervals, lo, hi):
    """True when some closed integer interval meets [lo, hi]: a straight
    walk from lo to hi is stopped if any position along it is blocked."""
    return any(a <= hi and b >= lo for a, b in intervals)


print('=' * 70)
print("Tenebrae's grass edge: engine box arithmetic on the built FIXED.DAT")

if not os.path.exists(FIXED) or not os.path.exists(TYPEFLAG):
    print('  shared/build artifacts absent: run tools/build_artifacts.sh')
    sys.exit(1)

shapes = load_typeflag(TYPEFLAG)
raw = MapArchive(FIXED).get_map_items(39)
items = expand_globs(raw, GlobReader())


def box_of(it):
    si = shapes[it.shape]
    return (it.x, it.y, it.z, si.footpad_x * 32, si.footpad_y * 32,
            si.footpad_z * 8)


# Every SOLID with height: what Box::overlaps can block a body with.
solids = []
for it in items:
    si = shapes[it.shape]
    b = box_of(it)
    if (si.flags0 & SI_SOLID) and b[3] > 0 and b[4] > 0 and b[5] > 0 \
            and it.shape != lf.VOID_PLATE:
        solids.append((it, b))
body_solids = [b for (_, b) in solids
               if b[2] < GROUND + BZ and b[2] + b[5] > GROUND]
# The edge's own oaks: shape 199 at the grass height, along the field and
# the avenue's east edge. (Retail places others elsewhere on the map, at
# other heights.)
oaks = [(it, b) for (it, b) in solids
        if it.shape == OAK and it.z == GROUND and it.y >= 17900
        and it.x >= 14000]
check('the map carries the edge oaks', len(oaks) >= 40,
      f'{len(oaks)} oaks')


# ---------------------------------------------------------------------------
# 1. Straight sweeps
# ---------------------------------------------------------------------------
# A body at anchor (x, y) occupies (x-64, x] x (y-64, y]. For a fixed x, the
# anchor ys a solid blocks are y in (by-byd, by+64), integer: by-byd+1 ..
# by+63. A leak is an x where the blocked union leaves a gap on the way from
# the grass to the first anchor with the body fully past the edge.

def blocked_y(x):
    out = []
    for (bx, by, bz, bxd, byd, bzd) in body_solids:
        if bx - bxd < x < bx + BX:
            out.append((by - byd + 1, by + BY - 1))
    return out


def blocked_x(y):
    out = []
    for (bx, by, bz, bxd, byd, bzd) in body_solids:
        if by - byd < y < by + BY:
            out.append((bx - bxd + 1, bx + BX - 1))
    return out


def sweep_south(x_lo, x_hi, y_from, y_to):
    """x anchors in [x_lo, x_hi] whose due-south walk y_from..y_to is free."""
    return [x for x in range(x_lo, x_hi + 1)
            if not blocks_any(blocked_y(x), y_from, y_to)]


def sweep_east(y_lo, y_hi, x_from, x_to):
    return [y for y in range(y_lo, y_hi + 1)
            if not blocks_any(blocked_x(y), x_from, x_to)]


def spans(vals):
    if not vals:
        return []
    out, s, p = [], vals[0], vals[0]
    for v in vals[1:]:
        if v == p + 1:
            p = v
        else:
            out.append((s, p))
            s = p = v
    out.append((s, p))
    return out


print('\nStraight sweeps (a 64x40 body walking out of the grass)')
# Anchors whose centre (x-32) is on grass: 14112..20511. Body fully past the
# south edge: its min y (y-64) >= 20479 -> y >= 20543.
# Start 200 north of the edge, where the lane is plain grass.
south = sweep_south(14112, 20511, SOUTH_EDGE_Y - 200, SOUTH_EDGE_Y + BY + 1)
check('south edge: no x lets a body walk due south into the void band',
      not south, f'{len(south)} leaking x in {spans(south)[:6]}')
# East face: x anchors past 20543 are fully beyond; sweep y along the face.
east = sweep_east(STUB_SOUTH_Y + 40, SOUTH_EDGE_Y + 20,
                  EAST_FACE_X - 200, EAST_FACE_X + BX + 1)
check('east face: no y lets a body walk due east into the void',
      not east, f'{len(east)} leaking y in {spans(east)[:6]}')
stub_s = sweep_south(EAST_FACE_X + 1, STUB_EAST_X + 40,
                     STUB_SOUTH_Y - 200, STUB_SOUTH_Y + BY + 1)
check('avenue stub south edge: no x lets a body walk due south into the void',
      not stub_s, f'{len(stub_s)} leaking x in {spans(stub_s)[:6]}')
stub_e = sweep_east(FIELD_NORTH_Y, STUB_SOUTH_Y,
                    STUB_EAST_X - 200, STUB_EAST_X + BX + 1)
check('avenue stub east edge: no y (>= %d) lets a body walk due east into '
      'the void' % FIELD_NORTH_Y, not stub_e,
      f'{len(stub_e)} leaking y in {spans(stub_e)[:6]}')

def sweep_north(x_lo, x_hi, y_from, y_to):
    """x anchors whose due-north walk from y_from (south) to y_to is free."""
    return [x for x in range(x_lo, x_hi + 1)
            if not blocks_any(blocked_y(x), y_to, y_from)]


# The platform's north end: centre on the last grass tile (x 14080..14335).
plat_n = sweep_north(14112, 14367, 19600, 19327)
check('platform north end: no x lets a body walk due north into the void',
      not plat_n, f'{len(plat_n)} leaking x in {spans(plat_n)[:6]}')

# Sanity: the instrument sees an oak exactly as the engine does. A body
# whose max x equals the oak's open low edge is an exact fit (a miss); one
# unit further in overlaps.
_ob = oaks[0][1]
_edge = _ob[0] - _ob[3]
_mid = _ob[1] - _ob[4] // 2
check('instrument: a body touching an oak face misses, one unit in hits',
      not overlaps((_edge, _mid, GROUND, BX, BY, BZ), _ob)
      and overlaps((_edge + 1, _mid, GROUND, BX, BY, BZ), _ob))

# ---------------------------------------------------------------------------
# 2. The flood
# ---------------------------------------------------------------------------
print('\nFlood from the egg lane (ExactReach, void plates removed)')
flat = [i for i in raw if i.shape != lf.VOID_PLATE]
roi = (12800, 19000, 21600, 21400)
er = ExactReach(flat, shapes, roi, step=8)
reach, seeded = er.flood([EGG])
check('the egg lane is standable', bool(seeded), 'seed not on a surface')

# Cover for the exposure test: what a body centre can be over without
# falling. Water is not floor but it is not void (it paints, and the gate
# moat is retail), so SI_SEA counts as "something there".
under = list(er.supports)
for it in expand_globs(flat, GlobReader()):
    si = shapes[it.shape]
    if si.flags0 & SI_SEA:
        under.append((it.x, it.y, 0, si.footpad_x * 32, si.footpad_y * 32))


def _bucket(boxes, key_xy):
    """Index boxes by 256-unit cell of their max corner, for point lookups."""
    idx = {}
    for bx_ in boxes:
        x, y, xd, yd = key_xy(bx_)
        for gx in range((x - xd) // 256, x // 256 + 1):
            for gy in range((y - yd) // 256, y // 256 + 1):
                idx.setdefault((gx, gy), []).append(bx_)
    return idx


_under_idx = _bucket(under, lambda s_: (s_[0], s_[1], s_[3], s_[4]))
_block_idx = _bucket(er.blockers, lambda k: (k[0], k[1], k[3], k[4]))


def has_ground(cx, cy):
    return any(sx - sxd < cx <= sx and sy - syd < cy <= sy
               for (sx, sy, _top, sxd, syd)
               in _under_idx.get((cx // 256, cy // 256), ()))


def blocked_at(x, y, z):
    b = (x, y, z, BX, BY, BZ)
    seen = set()
    for gx in range((x - BX) // 256, x // 256 + 1):
        for gy in range((y - BY) // 256, y // 256 + 1):
            for k in _block_idx.get((gx, gy), ()):
                if id(k) not in seen:
                    seen.add(id(k))
                    if overlaps(b, k):
                        return True
    return False


exposed = []
for L in er.levels:
    r = reach[L]
    if not r.any():
        continue
    for i, j in np.argwhere(r):
        x, y = er.x_of(i), er.y_of(j)
        for dx, dy in ((8, 0), (-8, 0), (0, 8), (0, -8)):
            nx, ny = x + dx, y + dy
            if not (roi[0] < nx < roi[2] and roi[1] < ny < roi[3]):
                continue
            if not has_ground(nx - BX // 2, ny - BY // 2) \
                    and not blocked_at(nx, ny, L):
                exposed.append((L, x, y))
                break

in_scope = [e for e in exposed if e[2] >= FIELD_NORTH_Y]
check('flood: no reachable position steps into void south of y=%d'
      % FIELD_NORTH_Y, not in_scope,
      f'{len(in_scope)} exposed, e.g. {in_scope[:3]}')
north = [e for e in exposed if e[2] < FIELD_NORTH_Y]
# What is left must be the pinned open edge: the avenue's east edge, body
# anchor x >= 21023, and nothing else.
stray = [e for e in north if e[1] < STUB_EAST_X + 24]
check('flood: what stays open is exactly the pinned avenue east edge',
      not stray, f'stray exposures {stray[:3]}')
print(f'  ({len(exposed)} exposed positions in all; {len(north)} north of '
      f'y={FIELD_NORTH_Y} on the avenue east edge, retail and open)')

# ---------------------------------------------------------------------------
# 3. Climb and burial
# ---------------------------------------------------------------------------
print('\nClimb rule and burial')
rungs = []
buried = []
_course_bottoms = {(b[0], b[1], b[2]) for (_, b) in solids}
for (oit, ob) in oaks:
    if oit.z != GROUND:
        continue
    # grown by one body width in x and y
    grown = (ob[0] + BX, ob[1] + BY, ob[2], ob[3] + 2 * BX, ob[4] + 2 * BY,
             ob[5])
    for (it, b) in solids:
        if it is oit:
            continue
        if it.shape != OAK and overlaps(ob, b):
            buried.append((oit.x, oit.y, it.shape, it.x, it.y, it.z))
        top = b[2] + b[5]
        # A course with another course laid on it has no standable top.
        if (b[0], b[1], top) in _course_bottoms:
            continue
        near = not (grown[0] <= b[0] - b[3] or b[0] <= grown[0] - grown[3]
                    or grown[1] <= b[1] - b[4] or b[1] <= grown[1] - grown[4])
        if it.shape != OAK and near and GROUND + 8 <= top < ob[2] + ob[5]:
            rungs.append((oit.x, oit.y, it.shape, it.x, it.y, top))
check('no oak is buried in a non-oak solid (oaks overlap each other on purpose)', not buried, f'{buried[:3]}')
check('no solid with a top in [56, 128) within a body width of an oak '
      '(no rung for climb72 on jump)', not rungs, f'{rungs[:3]}')
# The fence panels are 40 tall, so a rung unless standing on top is
# impossible. Every body position that rests on a panel's top (z=88) must
# overlap some other solid, here the roof slab.
fences = [(it, b) for (it, b) in solids if it.shape in (62, 130)
          and 19360 <= it.y <= 19423 and 14000 <= it.x <= 14400]
check('the platform north end has its two fence panels and the west one',
      len(fences) == 3, f'{len(fences)} panels')
standable = []
for (fit, fb) in fences:
    top = fb[2] + fb[5]
    others = [b for (it, b) in solids if it is not fit
              and abs(b[0] - fb[0]) < 600 and abs(b[1] - fb[1]) < 600]
    for bx in range(fb[0] - fb[3] + 1, fb[0] + BX):
        for by in range(fb[1] - fb[4] + 1, fb[1] + BY):
            body = (bx, by, top, BX, BY, BZ)
            if any(overlaps(body, o) for o in others):
                continue
            # getPositionInfo: supported needs LAND within 8 under the
            # body's bottom centre; a panel is SOLID only.
            mx, my = bx - BX // 2, by - BY // 2
            if any(lx - lxd < mx <= lx and ly - lyd < my <= ly
                   and top - 8 <= lt <= top
                   for (lx, ly, lt, lxd, lyd) in er.lands):
                standable.append((fit.x, bx, by))
check('no body can stand on a fence panel (a roof slab overhead, or no land '
      'under it)',
      not standable, f'{len(standable)} standing positions, e.g. {standable[:2]}')
check('every oak stands 80 tall from the grass (above climb72)',
      all(b[5] > CLIMB for (_, b) in oaks), 'a short blocker is a rung')
check('every item placed at the edge sits on the 4-unit z lattice',
      all(it.z % 4 == 0 for (it, _) in oaks))

# ---------------------------------------------------------------------------
# 4. Falls (found in ScummVM 2026-10-03, docs/playtest-2026-10-03-batch-merge.md)
# ---------------------------------------------------------------------------
# Sections 1 and 2 walk the grass and stop at an edge. The engine does not:
# a body stepped past an edge falls until it meets a top, and at z<=0 it is
# supported anywhere (current_map.cpp:773), so a fall that reaches z=0 puts
# the player on a floor that runs under the whole map, to the band under
# the apparition. The verifier walked that way twice. This flood seeds on
# the lane over the whole map, follows walks (0, +-4, +-8) and falls onto
# any real surface or solid top, and counts every position whose next step
# falls clear to z=0 (water excepted: the pool drowns, finding 3).
print('\nFalls to z=0 (whole map, falls followed)')
xs_ = [i.x for i in flat if i.x >= 64]
ys_ = [i.y for i in flat if i.y >= 64]
er2 = ExactReach(flat, shapes, (min(xs_) - 512, min(ys_) - 512,
                                max(xs_) + 512, max(ys_) + 512), step=8)
levels = [L for L in er2.levels if L > 0]


def _box_mask(boxes, keep):
    m = np.zeros((er2.NX, er2.NY), dtype=bool)
    for (bx_, by_, bz_, bxd_, byd_, bzd_) in boxes:
        if not keep(bz_, bzd_):
            continue
        i0, i1 = er2._kx(bx_ - bxd_, bx_ + BX)
        j0, j1 = er2._ky(by_ - byd_, by_ + BY)
        if i0 <= i1 and j0 <= j1:
            m[i0:i1 + 1, j0:j1 + 1] = True
    return m


def blocked_mask(L):
    return _box_mask(er2.blockers, lambda bz_, bzd_: not (
        bz_ >= L + BZ or bz_ + bzd_ <= L))


sea = np.zeros((er2.NX, er2.NY), dtype=bool)
for it in expand_globs(flat, GlobReader()):
    si = shapes[it.shape]
    if si.flags0 & SI_SEA:
        i0, i1 = er2._kx(it.x - si.footpad_x * 32 + BX // 2, it.x + BX // 2 + 1)
        j0, j1 = er2._ky(it.y - si.footpad_y * 32 + BY // 2, it.y + BY // 2 + 1)
        if i0 <= i1 and j0 <= j1:
            sea[i0:i1 + 1, j0:j1 + 1] = True

masks = {L: er2.mask(L) for L in levels}
blks = {L: blocked_mask(L) for L in levels}
# A solid under the edge with a top below L (not zero-height grass at L
# itself) stops a fall from L on its top.
under = {L: _box_mask(er2.blockers, lambda bz_, bzd_, L=L: bzd_ > 0
                      and 0 < bz_ + bzd_ < L) for L in levels}


def nbrs(r):
    n = np.zeros_like(r)
    n[1:, :] |= r[:-1, :]
    n[:-1, :] |= r[1:, :]
    n[:, 1:] |= r[:, :-1]
    n[:, :-1] |= r[:, 1:]
    return n


reach2 = {L: np.zeros((er2.NX, er2.NY), dtype=bool) for L in levels}
_i, _j = er2.index_of(EGG[0], EGG[1])
reach2[GROUND][_i, _j] = True
steps = {L: [L2 for L2 in levels if abs(L2 - L) in (4, 8)] for L in levels}
dirty = {GROUND}
while dirty:
    L = max(dirty)          # high levels first: falls only go down
    dirty.discard(L)
    r = reach2[L] = er2._propagate_both(masks[L], reach2[L])
    nb = nbrs(r)
    for L2 in steps[L]:
        add = nb & masks[L2] & ~reach2[L2]
        if add.any():
            reach2[L2] |= add
            dirty.add(L2)
    # falls: off the surface with nothing to step onto, onto the highest
    # surface below
    edge = nb & ~masks[L] & ~blks[L]
    for L2 in steps[L]:
        edge &= ~masks[L2]
    for L2 in sorted((l for l in levels if l < L - 8), reverse=True):
        if not edge.any():
            break
        add = edge & masks[L2] & ~reach2[L2]
        if add.any():
            reach2[L2] |= add
            dirty.add(L2)
        edge &= ~masks[L2]

void_exits = []
for L in levels:
    r = reach2[L]
    if not r.any():
        continue
    cand = nbrs(r) & ~masks[L] & ~blks[L] & ~sea & ~under[L]
    for L2 in levels:
        if L2 < L or 0 < L2 - L <= 8:
            cand &= ~masks[L2]
    for i, j in np.argwhere(cand):
        void_exits.append((L, er2.x_of(i), er2.y_of(j)))


def near_lane(e):
    # the field and the harbour south of the gate wall line, and the avenue
    # east of x=20400 from y=18200 (the void plates' accept window)
    return (e[1] >= 12800 and e[2] >= 19400) or (e[1] >= 20400 and e[2] >= 18200)


near = [e for e in void_exits if near_lane(e)]
check('falls: no position near the lane steps off into a clear fall to z=0',
      not near, f'{len(near)}, e.g. {near[:3]}')
# The rest are retail Tenebrae's own drops (build_map_39.TENEBRAE_OPEN_EDGES).
# Their count is pinned so a new drop anywhere on the plateau is noticed.
RETAIL_VOID_EXITS = 7709
check('falls: the retail drops elsewhere on the plateau number exactly %d'
      % RETAIL_VOID_EXITS, len(void_exits) == RETAIL_VOID_EXITS,
      f'{len(void_exits)}')

# ---------------------------------------------------------------------------
# 5. Stale frames
# ---------------------------------------------------------------------------
print('\nStale frames')
real = [i for i in items if i.shape != lf.VOID_PLATE]
floors = lf.floor_cells(real, shapes, eggs_as_chunks=False)
field = {c for c in floors
         if 14080 <= c[0] <= STUB_EAST_X + 128
         and 19583 <= c[1] <= SOUTH_EDGE_Y + 127}
view = lf.cells_within_view(field)
cover = lf.floor_cells(items, shapes, eggs_as_chunks=False, painted=True)
left = sorted(c for c in view - cover
              if c[1] > SOUTH_EDGE_Y or c[0] > STUB_EAST_X)
check('void_in_view south of y=%d and east of x=%d is 0'
      % (SOUTH_EDGE_Y, STUB_EAST_X), not left,
      f'{len(left)} cells, e.g. {left[:4]}')

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

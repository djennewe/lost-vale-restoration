#!/usr/bin/env python3
"""
exact_reach.py — reachability judged with the ENGINE'S OWN box arithmetic.

WHY THIS EXISTS (2026-07-31). `map_walkability.WalkGrid` rasterises the map
to 32-unit cells and calls a cell blocked only when a blocker covers the
cell CENTRE. That is the right instrument for "is there a route from A to
B" and the wrong one for anything that turns on a single body width:

  * it shipped the Tiny Tar crack SEALED (b95de7a) — the raster lost the
    last world unit of a filler and walked a 1-cell body through a 31-unit
    gap the engine refuses;
  * and it points the other way too. `flood(body_cells=2)` demands all four
    cells of a 2x2 body be free, so a corridor that is 64 units wide but
    NOT aligned to the 32-unit cell grid reads as impassable when the
    engine would walk it. That over-restriction is what raised the two
    2026-07-30 reachability suspicions (Map 10's Sacred Circle, Map 17's
    shield halves) that this module exists to settle.

So this module does not rasterise footprints at all. It reimplements
`CurrentMap::getPositionInfo` (ultima8/world/current_map.cpp) and
`Box::overlaps` / `Box::overlapsXY` / `Box::isBelow` (ultima8/misc/box.h)
exactly, and floods over a lattice of world positions at a configurable
step (default 8 units, offset so positions land on the same `x % 32 == 31`
alignment every map item uses).

The engine rules reproduced here, verbatim from getPositionInfo:

    blocked   an item with (its flags & mover flags & (SOLID|DAMAGING))
              whose box OVERLAPS the mover box. The Avatar is shape 1,
              flags 0x22 = SOLID|BAG, so in practice: SOLID items only.
    supported supportz == target.z exactly, where supportz is the highest
              (item.z + item.zd) <= target.z over items overlapping the
              mover in XY with flags & (SOLID|LAND|ROOF). Equivalently:
              some such item's TOP is exactly the standing z.
    land      landz + 8 >= target.z, where landz is the highest top over
              (LAND|ROOF) items whose box isBelow the mover's BOTTOM
              CENTRE (x - xd/2, y - yd/2). A point test, not a box test.
    z <= 0    is supported unconditionally.

Vertical movement follows AnimationTracker::step: when a step lands
invalid or unsupported the engine runs scanForValidPosition, which probes
candidate z offsets from a FIXED TABLE, not a range:

    static const int SEARCH_OFFSETS_U8[] = {0, -4, 4, -8, 8};
    (current_map.cpp; Crusader's table also has +/-1, 2, 3 — U8's does not)

so a lattice step may change level by 0, +/-4 or +/-8 and by NOTHING ELSE.
Reading that table as "anything up to 8" is what let the 2026-07-31 Cloud
Cliffs rebuild ship with 1- and 2-unit risers that this model certified and
the engine refused (F10, 2026-08-17). `step_z` now caps which entries of
the table are offered, it does not define a continuous range.

WHAT THIS MODEL STILL DOES NOT DO. It sees FIXED.DAT only — NPCs, doors
and everything else in NONFIXED.DAT/NPCDATA are invisible (the palace
door lesson, HANDOFF F2). It checks positions, not the swept volume
between them, so a blocker thinner than the lattice step could sit between
two valid positions unnoticed; keep the step at or below 8 for verdicts
that matter. And a lattice is still a lattice: "reachable" means a chain of
valid standing positions exists, not that the engine's pathfinder finds it.

TWO DELIBERATE DEVIATIONS FROM THE ENGINE, both found in the 2026-07-31
self-audit, both biasing the same way — this model is stricter than the
engine, so treat UNREACHED as "no walking route over real geometry", never
as "the engine refuses":

  1. AT z <= 0 THE ENGINE SUPPORTS ANYTHING. getPositionInfo ends with
     `if (target._z <= 0) info.supported = true;` (current_map.cpp:773),
     so any unblocked position at ground zero is valid-and-supported even
     over NOTHING — the engine will walk the Avatar across a floorless
     void at z=0 (it renders as blackness). This model requires a real
     surface at every z, because "you can technically traverse the void"
     is not a verdict worth shipping on: the project's own blackness rule
     (2026-07-02) already treats it as broken.
  2. WALKING ONLY — THE JUMP BUTTON IS NOT MODELED. On jump,
     u8_avatar_mover_process.cpp auto-tries Animation::climb72 down to
     climb16, so the engine can CLIMB obstacles up to 72 units tall when
     the anim finds a standable top. A barrier this model calls sealed is
     a *walking* seal; if it is <= 72 tall with clear headroom, a player
     pressing jump at it may simply climb over. Check barrier heights
     before trusting a seal (see test_route_reach's caveat).

EDGES (2026-10-10). The flood only ever enters SUPPORTED positions, so on
its own it cannot see a walk off a ledge: a step the engine takes onto
nothing and then falls from. `walk_off()` follows those steps — where the
actor lands, whether the fall hurts (80) or kills (104), and the walk on
from wherever it survives. test_map_edges uses it; read its docstring
before trusting a "no lethal drop". It found Map 13's summit hanging off
the map's north edge (playtest 2026-10-10 finding 4), which this module
could not see while it skipped every item at x or y < 64 as "contained".
Contained records are now known by FLG_CONTAINED, as the engine knows them.

HURT BY USECODE (2026-10-10). Some floors burn without SI_DAMAGING: the
retail lava, shape 409, is LAND|SOLID and its damage is its class's
gotHit (event 6, CLRLAVA @0199:0080). `hurt_shapes` makes such items
keep-out zones — a body that so much as TOUCHES one (sweepTest's
intervals are closed, current_map.cpp:1093-1123) is refused — grown by
`hurt_margin` world units on every side, so a flood can ask for a route
that keeps that much daylight from the lava.

CLI:
    exact_reach.py --map 17 --seed 4608,9984,0 --target 4259,7199,0
    exact_reach.py --map 10 --seed 12800,2560,0 --target 20480,16896,0 \
        --roi 10240,1024,22528,18944 --step 8
"""

import argparse
import os
import sys
from collections import deque

import numpy as np

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_map import MapArchive                       # noqa: E402
from map_preview import GlobReader, expand_globs     # noqa: E402
from parse_typeflag import load_typeflag             # noqa: E402

DEFAULT_FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
DEFAULT_TYPEFLAG = os.path.join(BASE_DIR, 'shared', 'build', 'TYPEFLAG.DAT')

# ShapeInfo flag bits (gfx/shape_info.h). flags0 is byte 0 of TYPEFLAG;
# SI_ROOF lives in the low nibble of byte 1, which parse_typeflag exposes
# as .flags1.
SI_SOLID = 0x02
SI_SEA = 0x04
SI_LAND = 0x08
SI_DAMAGING = 0x40
SI_ROOF_F1 = 0x04

FLG_CONTAINED = 0x0008
FLG_INVISIBLE = 0x0010
FLG_EQUIPPED = 0x0200
FLG_FLIPPED = 0x0020

# CurrentMap::addItem refuses any location outside [0, MAP_NUM_CHUNKS *
# _mapChunkSize) = [0, 64 * 512) on either axis (current_map.cpp:246): an
# actor that walks there leaves the chunk lists.
MAP_EXTENT = 64 * 512

# GravityProcess::actorFallStoppedU8 (gravity_process.cpp): a fall of 80 or
# more hurts, (h - 72) / 4 hit points; a fall of 104 or more kills.
FALL_HURTS = 80
FALL_LETHAL = 104

# Mover footpads, world units. Shape 1 is (2,2,5); shape 867 — the Tiny
# Tar Avatar — is (1,1,4).
AVATAR_BODY = (64, 64, 40)
TINY_BODY = (32, 32, 32)

# AnimationTracker::step -> scanForValidPosition probes exactly these z
# offsets in U8 (current_map.cpp SEARCH_OFFSETS_U8). A walking actor cannot
# change z by any other amount — see the module docstring.
Z_SEARCH_OFFSETS_U8 = (0, -4, 4, -8, 8)
DEFAULT_STEP_Z = 8
# One lattice step. 8 is the finest alignment any map item uses.
DEFAULT_STEP = 8

# Shapes that hurt by usecode, not by SI_DAMAGING, so TYPEFLAG cannot see
# them. 409 is the Plane of Fire's lava (Map 44 lays 11,195 tiles of it).
# Its class CLRLAVA's gotHit (EUSECODE class 0x0199, event 6) runs
# whenever an actor's move sweeps into contact with a tile — standing on
# it is `_touchingFloor`, item.cpp:1178. Frames <= 32 burn: receiveHit,
# 2-4 fire damage (type 0x80), then again after a 30-tick wait for as
# long as he has not moved (0199:00DC-01DA).
# Frames > 32 are the deep lava: the Avatar is put in stasis, sunk, and
# killed outright with damage = his hp; any other hitter is destroyed.
# (Disassembly: 0199:00AC getFrame <= 32, 0199:01B6 receiveHit, 0199:0259
# the death branch.) playtest-2026-10-10-full-run-part5 finding 1 is a
# death on it.
#
# The rest come from a survey of every shape placed on an LV map whose
# gotHit reaches Item::receiveHit (test_route_reach's gothit_hurts, which
# fails on a new one):
#   267 CAMPFIRE  2-5 fire damage to an NPC hitter (010B:0127 receiveHit).
#   318 FIREPIT   on a coin flip, not while cooling down: a die roll
#                 (0581:1A96) through METHOD 057C:0080, receiveHit. Build 7
#                 lost 2 hp to one on Map 11 (playtest-2026-10-11-build7 L1).
#   794 FIRESHRO  a quality-0 fire shroom touched by a live NPC explodes
#                 (057C:0676, receiveHit on what stands near). Retail Map 8
#                 places 274 of them, all quality 0.
#   216 LIGHT     a lightning strike: an NPC that overlaps it (216:0123
#                 Item::overlaps) gets a quake or a LightningBolt, and the
#                 Avatar a 255-point hit through METHOD 057C:0080
#                 (216:01C7). Screen09 places one (frame 10) on its shelf.
#   438 WATER4    the waterfall's foam. Its gotHit is CLRWATER's, a spawn
#                 of WATER 056E:0080, which drowns a hitter that isOn it
#                 (item.cpp Item::isOn: footprints overlap, its top at his
#                 z). The foam is 8 deep, so its top is the lake banks'
#                 height and a body on the bank beside it is on it.
#   400 FIREFELD  an NPC that overlaps a fire field of frame <= 9 takes a
#                 die roll's fire (0581:1A96) unless a shape-703 item lies
#                 within 64 of it (0190:0115 area search), receiveHit at
#                 0190:0173. First on an LV map with Map 11's screen05
#                 torture pocket (2026-10-17): two at frame 0.
# 216, 438 and 400 are SI_DAMAGING in retail TYPEFLAG (0x41, 0x47), as are
# 318 and 267; 409 and 794 are not. The engine reads SI_DAMAGING only as a
# blocker flag (current_map.cpp blockmask); the hurt is the class's.
# CLRWATER (347) also reaches receiveHit but drowns only what stands ON
# the water (056E:00A2 isOn); its top is 0, under every bank, and the
# lake rails keep walkers off it: it is not listed.
HURT_SHAPES_U8 = (216, 267, 318, 400, 409, 438, 794)


class ExactReach:
    """Engine-faithful standability + flood over a lattice of positions.

    Positions are MAX corners, the same convention map items use: a body
    of width B at x occupies the half-open span (x - B, x].
    """

    def __init__(self, items, shapes, roi, body=AVATAR_BODY,
                 step=DEFAULT_STEP, step_z=DEFAULT_STEP_Z,
                 glob_reader=None, mover_flags=SI_SOLID,
                 hurt_shapes=(), hurt_margin=0):
        self.shapes = shapes
        self.roi = roi
        self.body = body
        self.step = step
        self.step_z = step_z
        self.mover_flags = mover_flags
        self.hurt_margin = hurt_margin
        hurt_shapes = frozenset(hurt_shapes)

        bxd, byd, bzd = body
        x0r, y0r, x1r, y1r = roi

        # Lattice: positions x = X0 + k*step, aligned so that x % 32 == 31
        # when step divides 32 — the alignment every map item sits on.
        self.X0 = (x0r // step) * step + (step - 1)
        self.Y0 = (y0r // step) * step + (step - 1)
        self.NX = max(1, (x1r - self.X0) // step + 1)
        self.NY = max(1, (y1r - self.Y0) // step + 1)

        expanded = []
        gr = glob_reader
        for it in items:
            if it.is_glob_egg:
                if gr is None:
                    gr = GlobReader()
                    self._gr = gr
                expanded.extend(gr.glob_to_items(
                    it.quality, it.x, it.y, it.z & 0xFF))
            else:
                expanded.append(it)

        # Boxes that matter, clipped to the ROI grown by one body width so
        # a blocker just outside still blocks positions just inside.
        self.blockers = []   # (x, y, z, xd, yd, zd)
        self.supports = []   # (x, y, top, xd, yd)
        self.lands = []      # (x, y, top, xd, yd)
        self.hurts = []      # (x, y, z, xd, yd, zd), hurt_shapes items
        for it in expanded:
            # A contained record has no world position: its x is the
            # container DEPTH and its y the gump slot (u8_map.contained_-
            # item). The engine knows it by FLG_CONTAINED, and so do we. A
            # coordinate test here (x < 64 or y < 64) dropped Map 13's
            # whole summit edge row — 70 items at y=0 — so a flood could
            # neither stand on it nor see the walk off it (playtest
            # 2026-10-10 finding 4).
            if it.flags & (FLG_CONTAINED | FLG_EQUIPPED):
                continue
            if it.shape < 0 or it.shape >= len(shapes):
                continue
            si = shapes[it.shape]
            xd, yd = si.footpad_x * 32, si.footpad_y * 32
            if it.flags & FLG_FLIPPED:
                xd, yd = yd, xd
            zd = si.footpad_z * 8
            if it.shape in hurt_shapes:
                self.hurts.append((it.x, it.y, it.z & 0xFF, xd, yd, zd))
            # A zero-HEIGHT box is still support and still land — the U8
            # floor tile (shape 35) is footpad (4,4,0), so its top is its
            # own z. Only a zero-AREA footprint is nothing at all. Such a
            # box can never block: Box::overlaps needs _z + _zd > o._z.
            if xd <= 0 or yd <= 0:
                continue
            if it.x - xd >= x1r + bxd or it.x <= x0r - bxd:
                continue
            if it.y - yd >= y1r + byd or it.y <= y0r - byd:
                continue
            z = it.z & 0xFF
            is_solid = bool(si.flags0 & SI_SOLID)
            is_land = bool(si.flags0 & SI_LAND)
            is_roof = bool(si.flags1 & SI_ROOF_F1)
            is_dmg = bool(si.flags0 & SI_DAMAGING)
            if (si.flags0 & SI_SOLID or is_dmg) and \
               ((si.flags0 & mover_flags) & (SI_SOLID | SI_DAMAGING)):
                self.blockers.append((it.x, it.y, z, xd, yd, zd))
            if is_solid or is_land or is_roof:
                self.supports.append((it.x, it.y, z + zd, xd, yd))
            if is_land or is_roof:
                self.lands.append((it.x, it.y, z + zd, xd, yd))

        self.levels = sorted({s[2] for s in self.supports})
        self._mask = {}
        self._blocked = {}
        self._near = None

    # -- lattice index helpers ------------------------------------------

    def _kx(self, lo_excl, hi_excl):
        """lattice x indices k with lo_excl < X0 + k*step < hi_excl."""
        s, X0 = self.step, self.X0
        kmin = (lo_excl - X0) // s + 1
        kmax = -((-(hi_excl - X0)) // s) - 1
        return max(0, kmin), min(self.NX - 1, kmax)

    def _ky(self, lo_excl, hi_excl):
        s, Y0 = self.step, self.Y0
        kmin = (lo_excl - Y0) // s + 1
        kmax = -((-(hi_excl - Y0)) // s) - 1
        return max(0, kmin), min(self.NY - 1, kmax)

    def x_of(self, i):
        return self.X0 + i * self.step

    def y_of(self, j):
        return self.Y0 + j * self.step

    def index_of(self, x, y):
        """Nearest lattice index to a world point."""
        i = int(round((x - self.X0) / self.step))
        j = int(round((y - self.Y0) / self.step))
        return min(max(i, 0), self.NX - 1), min(max(j, 0), self.NY - 1)

    # -- per-level masks -------------------------------------------------

    def mask(self, level):
        """Bool array [NX, NY]: can the body stand here at this level?"""
        if level in self._mask:
            return self._mask[level]
        bxd, byd, bzd = self.body

        sup = np.zeros((self.NX, self.NY), dtype=bool)
        for (sx, sy, top, sxd, syd) in self.supports:
            if top != level:
                continue
            i0, i1 = self._kx(sx - sxd, sx + bxd)
            j0, j1 = self._ky(sy - syd, sy + byd)
            if i0 <= i1 and j0 <= j1:
                sup[i0:i1 + 1, j0:j1 + 1] = True

        # landz + 8 >= z, and isBelow means top <= z: a LAND/ROOF top in
        # [z-8, z] under the mover's bottom centre.
        lnd = np.zeros((self.NX, self.NY), dtype=bool)
        for (lx, ly, top, lxd, lyd) in self.lands:
            if not (level - 8 <= top <= level):
                continue
            # midx = x - bxd/2 must lie in (lx - lxd, lx]
            i0, i1 = self._kx(lx - lxd + bxd // 2, lx + bxd // 2 + 1)
            j0, j1 = self._ky(ly - lyd + byd // 2, ly + byd // 2 + 1)
            if i0 <= i1 and j0 <= j1:
                lnd[i0:i1 + 1, j0:j1 + 1] = True
        blk = self.blocked(level)

        if level <= 0:
            # The ENGINE would accept ~blk alone here (z<=0 is supported
            # unconditionally, current_map.cpp:773) — deliberately stricter:
            # a real surface is required, see deviation 1 in the docstring.
            ok = ~blk & (sup | lnd)
        else:
            ok = sup & lnd & ~blk
        self._mask[level] = ok
        return ok

    def blocked(self, level):
        """Bool array [NX, NY]: does a blocker overlap the body standing at
        this level? (Box::overlaps; any z, a lattice level or not.) With
        `hurt_shapes`, also: does the body touch one, `hurt_margin` grown —
        closed intervals, as sweepTest's contact test is."""
        if level in self._blocked:
            return self._blocked[level]
        bxd, byd, bzd = self.body
        blk = np.zeros((self.NX, self.NY), dtype=bool)
        for (bx, by, bz, bxd_, byd_, bzd_) in self.blockers:
            if bz >= level + bzd or bz + bzd_ <= level:
                continue
            i0, i1 = self._kx(bx - bxd_, bx + bxd)
            j0, j1 = self._ky(by - byd_, by + byd)
            if i0 <= i1 and j0 <= j1:
                blk[i0:i1 + 1, j0:j1 + 1] = True
        m = self.hurt_margin
        for (hx, hy, hz, hxd, hyd, hzd) in self.hurts:
            if hz > level + bzd or hz + hzd < level:
                continue
            i0, i1 = self._kx(hx - hxd - m - 1, hx + bxd + m + 1)
            j0, j1 = self._ky(hy - hyd - m - 1, hy + byd + m + 1)
            if i0 <= i1 and j0 <= j1:
                blk[i0:i1 + 1, j0:j1 + 1] = True
        self._blocked[level] = blk
        return blk

    # -- flood -----------------------------------------------------------

    @staticmethod
    def _propagate(mask, reach):
        """Propagate `reach` along axis 1 inside contiguous runs of `mask`.
        Run-labelled so a whole row moves in one vectorised pass."""
        if not reach.any():
            return reach
        starts = mask.copy()
        starts[:, 1:] &= ~mask[:, :-1]
        ids = np.cumsum(starts.ravel()).reshape(mask.shape)
        sel = reach & mask
        hit = np.bincount(ids[sel].ravel(), minlength=int(ids.max()) + 1) > 0
        return mask & hit[ids]

    def _propagate_both(self, mask, reach):
        """Flood `reach` through `mask` in-plane, to a fixpoint. One pass of
        each axis is NOT enough — a corridor that turns needs one pass per
        turn — so alternate until nothing more is picked up."""
        maskT = np.ascontiguousarray(mask.T)
        n = -1
        while True:
            reach = self._propagate(mask, reach)
            rt = self._propagate(maskT, np.ascontiguousarray(reach.T))
            reach = np.ascontiguousarray(rt.T)
            total = int(reach.sum())
            if total == n:
                return reach
            n = total

    def flood(self, seeds):
        """seeds: [(x, y, z)] world points. Returns {level: bool array}.

        A seed snaps to the nearest lattice position and to the nearest
        standable level within step_z of its z."""
        reach = {L: np.zeros((self.NX, self.NY), dtype=bool)
                 for L in self.levels}
        seeded = []
        for (sx, sy, sz) in seeds:
            i, j = self.index_of(sx, sy)
            best = None
            for L in self.levels:
                if abs(L - sz) > max(self.step_z, 8):
                    continue
                if self.mask(L)[i, j] and (best is None or
                                           abs(L - sz) < abs(best - sz)):
                    best = L
            if best is None:
                continue
            reach[best][i, j] = True
            seeded.append((sx, sy, sz, best))
        if not seeded:
            return reach, seeded
        return self._grow(reach, {L for L in self.levels if reach[L].any()}), \
            seeded

    def _grow(self, reach, dirty):
        """Flood `reach` in place to a fixpoint from the levels in `dirty`."""
        if self._near is None:
            # Level pairs a single lattice step can move between. Maps with
            # a real climb have ~90 levels, so precompute rather than
            # rescan. The set of legal deltas is the engine's offset TABLE
            # clipped by step_z, not the range 1..step_z: a 1-unit riser is
            # as impassable as a 9-unit one (see the module docstring).
            deltas = {d for d in Z_SEARCH_OFFSETS_U8
                      if d != 0 and abs(d) <= self.step_z}
            self._near = {L: [L2 for L2 in self.levels if (L2 - L) in deltas]
                          for L in self.levels}
        near = self._near

        # Worklist over levels. Popping a level floods it in-plane, then
        # spreads to every level a single step can reach; any level that
        # gains ground goes back on the list. Terminates because reach only
        # ever grows and is bounded by the masks.
        dirty = set(dirty)
        while dirty:
            L = dirty.pop()
            r = self._propagate_both(self.mask(L), reach[L])
            reach[L] = r
            if not near[L] or not r.any():
                continue
            spread = r.copy()
            spread[1:, :] |= r[:-1, :]
            spread[:-1, :] |= r[1:, :]
            spread[:, 1:] |= r[:, :-1]
            spread[:, :-1] |= r[:, 1:]
            for L2 in near[L]:
                add = spread & self.mask(L2) & ~reach[L2]
                if add.any():
                    reach[L2] |= add
                    dirty.add(L2)
        return reach

    def shortest_path(self, reach, a, b):
        """Deterministic BFS within a flood, endpoints matched at ring 96.

        In-plane edges are cardinal; level changes also allow a stationary
        XY, matching _grow. Equal-length choices sort by world (x, y, z).
        An unreachable endpoint or disconnected pair raises ValueError.
        """
        start = self.reached_near(reach, *a, ring=96)
        end = self.reached_near(reach, *b, ring=96)
        if start is None or end is None:
            raise ValueError(f"unreached leg endpoint: {a} -> {b}")
        def node(p):
            i, j = self.index_of(*p[:2])
            return i, j, p[2]
        start, end = node(start), node(end)
        queue = deque([start])
        previous = {start: None}
        levels = {z: [v for v in sorted(reach)
                      if v-z in Z_SEARCH_OFFSETS_U8 and abs(v-z) <= self.step_z]
                  for z in reach}
        while queue:
            here = queue.popleft()
            if here == end:
                path = []
                while here is not None:
                    i, j, z = here
                    path.append((self.x_of(i), self.y_of(j), z))
                    here = previous[here]
                return path[::-1]
            i, j, z = here
            neighbours = []
            for di, dj in ((-1, 0), (0, -1), (0, 0), (0, 1), (1, 0)):
                ii, jj = i+di, j+dj
                if not (0 <= ii < self.NX and 0 <= jj < self.NY):
                    continue
                for zz in levels[z]:
                    n = (ii, jj, zz)
                    if n not in previous and reach[zz][ii, jj]:
                        neighbours.append(n)
            for n in sorted(neighbours):
                previous[n] = here
                queue.append(n)
        raise ValueError(f"disconnected leg: {a} -> {b}")

    # -- edges -----------------------------------------------------------

    def _engine_stands(self, z):
        """Where the ENGINE takes a step at z as valid and supported: the
        flood's mask, except at z <= 0, where getPositionInfo supports
        anything unblocked (deviation 1 in the docstring cuts the other way
        here — this asks where a walk ends, not where it should go)."""
        return ~self.blocked(z) if z <= 0 else self.mask(z)

    def _dilate8(self, r):
        nb = np.zeros_like(r)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di or dj:
                    nb[max(di, 0):self.NX + min(di, 0),
                       max(dj, 0):self.NY + min(dj, 0)] |= \
                        r[max(-di, 0):self.NX + min(-di, 0),
                          max(-dj, 0):self.NY + min(-dj, 0)]
        return nb

    def walk_off(self, reach):
        """Follow every walk off the edge of a flood. Returns a dict:

          reach    the flood extended by every drop a walk survives
          falls    [(x, y, from_z, land_z)], each drop of FALL_HURTS or more
          teeter   [(x, y, z)], resting on an edge with no land beneath
          void     [(x, y, z)], landed at z <= 0 on no surface
          off_map  [(x, y, z)], any of the above outside [0, MAP_EXTENT)

        The flood alone cannot see an edge: it only enters positions the
        engine calls supported. But AnimationTracker::step, when a step
        lands unsupported, runs scanForValidPosition over the z offsets
        {0, -4, 4, -8, 8}, and a valid but UNSUPPORTED hit is taken anyway
        (`foundunsupported`, current_map.cpp); the tracker then sets
        `_unsupported` and the actor falls. The step is refused only when
        every offset is blocked. So each lattice neighbour (8-connected) of
        the flood that is valid at some offset and supported at none is a
        step off an edge. The actor drops onto the highest SOLID|LAND|ROOF
        top under its body (GravityProcess sweeps down into anything with
        those flags), or to z = 0, which the engine supports over nothing.

        A drop lands one of three ways. On a supported position, it seeds
        the flood again (a ledge the walk could not climb back up). On a
        top that its body overlaps but whose land is not under its centre
        (getPositionInfo's `landz + 8 >= z`), it TEETERS: gravity cannot
        move it, and each further step is the same scan again — this is
        how the Avatar walked 128 units out over Map 13's summit row before
        it fell (playtest 2026-10-10 finding 4). At z <= 0 on no surface it
        is in the void, which test_map_edges' footprint check owns. A drop
        of FALL_LETHAL or more ends the walk.

        Momentum is not modeled: every fall is straight down at the first
        unsupported lattice position.
        """
        bxd, byd, _ = self.body
        sup = np.array([s[:5] for s in self.supports], dtype=np.int64) \
            if self.supports else np.zeros((0, 5), dtype=np.int64)
        reach = {L: r.copy() for L, r in reach.items()}
        falls, void, teeter = [], [], []
        done = set()
        queue = deque()

        def first(i, j, z, pred):
            for d in Z_SEARCH_OFFSETS_U8:
                if pred(z + d)[i, j]:
                    return z + d
            return None

        def unblocked(z):
            return ~self.blocked(z)

        def step_offs(new):
            for L, r in new.items():
                if not r.any():
                    continue
                stand = np.zeros_like(r)
                valid = np.zeros_like(r)
                for d in Z_SEARCH_OFFSETS_U8:
                    stand |= self._engine_stands(L + d)
                    valid |= unblocked(L + d)
                for i, j in np.argwhere(self._dilate8(r) & valid & ~stand):
                    queue.append((int(i), int(j), L))

        def settle(i, j, z, fresh):
            """The actor is supported at (i, j, z): is that the flood's?"""
            if z in reach and self.mask(z)[i, j]:
                if not reach[z][i, j]:
                    fresh.setdefault(z, []).append((i, j))
                return True
            if z <= 0:
                void.append((self.x_of(i), self.y_of(j), z))
                return True
            return False

        step_offs(reach)
        while True:
            fresh = {}
            while queue:
                i, j, z = queue.popleft()
                if (i, j, z) in done:
                    continue
                done.add((i, j, z))
                z0 = first(i, j, z, unblocked)
                x, y = self.x_of(i), self.y_of(j)
                under = ((sup[:, 0] - sup[:, 3] < x) & (x - bxd < sup[:, 0]) &
                         (sup[:, 1] - sup[:, 4] < y) & (y - byd < sup[:, 1]) &
                         (sup[:, 2] <= z0))
                land = max(int(sup[under, 2].max()) if under.any() else 0, 0)
                if z0 - land >= FALL_HURTS:
                    falls.append((x, y, z0, land))
                    if z0 - land >= FALL_LETHAL:
                        continue
                if settle(i, j, land, fresh):
                    continue
                teeter.append((x, y, land))
                for i2 in range(max(i - 1, 0), min(i + 2, self.NX)):
                    for j2 in range(max(j - 1, 0), min(j + 2, self.NY)):
                        if (i2, j2) == (i, j):
                            continue
                        s = first(i2, j2, land, self._engine_stands)
                        if s is not None:
                            settle(i2, j2, s, fresh)
                        elif first(i2, j2, land, unblocked) is not None:
                            queue.append((i2, j2, land))
            if not fresh:
                break
            before = {L: r.copy() for L, r in reach.items()}
            for L, pts in fresh.items():
                for i, j in pts:
                    reach[L][i, j] = True
            self._grow(reach, set(fresh))
            step_offs({L: reach[L] & ~before[L] for L in reach})

        def outside(x, y):
            return not (0 <= x < MAP_EXTENT and 0 <= y < MAP_EXTENT)

        xs = self.X0 + np.arange(self.NX) * self.step
        ys = self.Y0 + np.arange(self.NY) * self.step
        bad = ((xs < 0) | (xs >= MAP_EXTENT))[:, None] | \
              ((ys < 0) | (ys >= MAP_EXTENT))[None, :]
        off = [(self.x_of(int(i)), self.y_of(int(j)), L)
               for L, r in reach.items() for i, j in np.argwhere(r & bad)]
        off += [p for p in teeter + void if outside(p[0], p[1])]
        off += [(x, y, z) for (x, y, z, _) in falls if outside(x, y)]
        falls.sort(key=lambda f: (f[3] - f[2], f[1], f[0]))
        return {'reach': reach, 'falls': falls, 'teeter': teeter,
                'void': void, 'off_map': sorted(set(off))}

    # -- queries ---------------------------------------------------------

    def standable_levels(self, x, y):
        i, j = self.index_of(x, y)
        return [L for L in self.levels if self.mask(L)[i, j]]

    def reached_near(self, reach, x, y, z, ring=96):
        """Did the flood reach a standing position within `ring` units of
        (x, y), at a level within step_z of z? Items you must walk up to
        are SOLID themselves, so their own cell is never standable."""
        i0, i1 = self._kx(x - ring, x + ring + 1)
        j0, j1 = self._ky(y - ring, y + ring + 1)
        if i0 > i1 or j0 > j1:
            return None
        for L in self.levels:
            if abs(L - z) > max(self.step_z, 24):
                continue
            sub = reach[L][i0:i1 + 1, j0:j1 + 1]
            if sub.any():
                ii, jj = np.argwhere(sub)[0]
                return (self.x_of(i0 + ii), self.y_of(j0 + jj), L)
        return None

    def summary(self, reach):
        tot = sum(int(r.sum()) for r in reach.values())
        walk = sum(int(self.mask(L).sum()) for L in self.levels)
        return tot, walk


# ===========================================================================


def load_map(mapnum, fixed=DEFAULT_FIXED, typeflag=DEFAULT_TYPEFLAG):
    shapes = load_typeflag(typeflag)
    items = MapArchive(fixed).get_map_items(mapnum)
    return items, shapes


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--map', type=int, required=True)
    ap.add_argument('--seed', action='append', required=True,
                    help='x,y,z world position to flood from (repeatable)')
    ap.add_argument('--target', action='append', default=[],
                    help='x,y,z[,label] to test reachability of')
    ap.add_argument('--roi', help='x0,y0,x1,y1 (default: map extent)')
    ap.add_argument('--step', type=int, default=DEFAULT_STEP)
    ap.add_argument('--step-z', type=int, default=DEFAULT_STEP_Z)
    ap.add_argument('--ring', type=int, default=96)
    ap.add_argument('--tiny', action='store_true',
                    help='model the shrunken Avatar (shape 867) instead')
    ap.add_argument('--fixed', default=DEFAULT_FIXED)
    args = ap.parse_args()

    items, shapes = load_map(args.map, args.fixed)
    if not items:
        print(f'no items for map {args.map}')
        return 1

    if args.roi:
        roi = tuple(int(v) for v in args.roi.split(','))
    else:
        placed = [i for i in items if not i.flags & (FLG_CONTAINED |
                                                    FLG_EQUIPPED)]
        xs = [i.x for i in placed]
        ys = [i.y for i in placed]
        roi = (min(xs) - 64, min(ys) - 64, max(xs) + 64, max(ys) + 64)

    body = TINY_BODY if args.tiny else AVATAR_BODY
    er = ExactReach(items, shapes, roi, body=body, step=args.step,
                    step_z=args.step_z)
    print(f'map {args.map}  roi {roi}  lattice {er.NX}x{er.NY} @ {args.step}'
          f'  body {body}  levels {er.levels[:12]}'
          f'{"..." if len(er.levels) > 12 else ""}')

    seeds = [tuple(int(v) for v in s.split(',')) for s in args.seed]
    reach, seeded = er.flood(seeds)
    for (sx, sy, sz) in seeds:
        got = [s for s in seeded if s[:3] == (sx, sy, sz)]
        if got:
            print(f'  seed ({sx},{sy},{sz}): standing at level {got[0][3]}')
        else:
            lv = er.standable_levels(sx, sy)
            print(f'  seed ({sx},{sy},{sz}): NOT STANDABLE '
                  f'(levels here: {lv})')
    tot, walk = er.summary(reach)
    print(f'  reached {tot} of {walk} standable lattice positions')

    rc = 0
    for t in args.target:
        parts = t.split(',')
        tx, ty, tz = (int(v) for v in parts[:3])
        label = parts[3] if len(parts) > 3 else f'({tx},{ty},{tz})'
        hit = er.reached_near(reach, tx, ty, tz, ring=args.ring)
        if hit:
            print(f'  REACHED  {label}: stand at {hit}')
        else:
            print(f'  UNREACHED {label} within {args.ring} units')
            rc = 1
    return rc


if __name__ == '__main__':
    sys.exit(main())

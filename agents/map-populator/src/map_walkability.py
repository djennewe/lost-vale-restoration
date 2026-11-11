#!/usr/bin/env python3
"""
map_walkability.py — Headless walkability/reachability validator.

Catches the class of map-truth bugs that static per-item checks cannot:
floor globs that are SEA water (tester drowned), empty floor globs
(void), quest items floating in gaps between platform tiles, rooms with
no doorway between them, and "plug" items that do not actually cover the
doorway they seal. This is a REPORTING tool: it never modifies builders
or FIXED.DAT.

Engine geometry (verified against scummvm-lv, 2026-07-04)
---------------------------------------------------------
- An item's origin is its MAX corner. It occupies the box
      (x - xd, x]  ×  (y - yd, y]  ×  [z, z + zd)
  where (xd, yd, zd) = TYPEFLAG footpad × (32, 32, 8).
  Source: ShapeInfo::getFootpadWorld() in
  scummvm-lv/engines/ultima/ultima8/gfx/shape_info.h — `z = _z * 8`,
  x/y `* 32`, with x/y SWAPPED when the item carries FLG_FLIPPED
  (0x0020) in its FIXED.DAT flags word (item.h).
- TYPEFLAG flags0 bits: 0x01 FIXED, 0x02 SOLID, 0x04 SEA, 0x08 LAND,
  0x10 OCCL. Nibble layout verified against TypeFlags::load() in
  gfx/type_flags.cpp — parse_typeflag.py decodes identically.
- z is stored UNSIGNED on disk: Map::loadFixedFormatObjects() does
  `readByte()` (0..255). u8_map.MapItem parses it signed, so all z pass
  through engine_z() (& 0xFF) here. A builder's z=-2 is engine z=254.
- Glob eggs expand per GlobEgg::enterFastArea(): x/y offsets ×2 +1
  within the egg's 512-chunk, z added directly. glob_catalog.GlobReader
  replicates this exactly.
- The avatar is shape 1: footpad (2,2,5) → a 64×64×40 world box.

Walkability model (v1)
----------------------
The world is sampled on a CELL(=32)-unit grid at cell centers. Per cell:
- Every LAND/SEA item covering the center contributes a candidate
  surface at top = z + zd (flat footpad_z==0 floors: top == z).
  Equal-top ties go to the LATER item in map order (draws on top).
- A SOLID item with zd > 16 is a blocker. Standing at surface level s,
  the cell is BLOCKED if a blocker's [z, z+zd) intersects
  (s + STEP_Z, s + AVATAR_ZD] — i.e. it pokes into the avatar's body
  above step height. (A blocker whose top is at or below s+STEP_Z is
  steppable; one starting at or above s+AVATAR_ZD is ceiling.)
- Cell status at a level: WALKABLE (LAND top, not blocked), SEA (top
  surface is a SEA item), BLOCKED, or VOID (no surface at all).
Flood fill moves between 4-adjacent cells when the destination has a
non-SEA, unblocked surface within STEP_Z(=24) z of the current level;
visited state is (cell, level) so multi-story cells work.

Caveats (v1, by design): the fill is single-cell — passages narrower
than the avatar's 64-unit width (2 cells) may be reported reachable
that the engine would reject; diagonal moves are not modelled.

Usage
-----
    python3 map_walkability.py                    # all suites (11, 39, 8, 10)
    python3 map_walkability.py --maps 11          # one suite
    python3 map_walkability.py --fixed path/to/FIXED.DAT

Exit code 0 only if every assertion passes. Designed so
build_all_maps.py can later call run_all() — NOT wired into the gate.
"""

import os
import sys
import json
import argparse
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from u8_map import MapArchive, MapItem
from parse_typeflag import load_typeflag
from glob_catalog import GlobReader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
DEFAULT_FIXED = os.path.join(BASE_DIR, "shared", "build", "FIXED.DAT")

# --- Engine constants (see module docstring for sources) -------------------
CELL = 32            # grid resolution, world units
STEP_Z = 24          # max step up/down between adjacent cells
AVATAR_ZD = 40       # avatar shape 1: footpad_z 5 × 8

# Mover widths in CELLs, for WalkGrid.flood(body_cells=...). The engine
# checks a full footpad Box in canExistAt(), so a passage narrower than the
# mover is impassable however walkable its floor is. This is what makes the
# Tiny Tar crack work (DD-005): the Avatar is shape 1, footpad (2,2,5) =
# 64x64, and the shrunken Avatar is shape 867, footpad (1,1,4) = 32x32, so
# a 32-unit aperture passes one and blocks the other.
BODY_AVATAR = 2      # 64x64 — normal Avatar
BODY_TINY = 1        # 32x32 — after drinking Tiny Tar
BLOCKER_MIN_ZD = 16  # SOLID items must have zd > this to block a cell
RING = 64            # interaction ring around solid targets (2 cells)
FLG_FLIPPED = 0x0020

FLAG_SOLID = 0x02
FLAG_SEA = 0x04
FLAG_LAND = 0x08

# Egg shapes are data carriers, not physical geometry (footpads (1,1,1)
# in TYPEFLAG are meaningless): glob egg 2 (expanded separately),
# UnkEgg 73, monster egg 500, teleport egg 508.
EGG_SHAPES = {2, 73, 500, 508}

WALKABLE, SEA, VOID, BLOCKED = "WALKABLE", "SEA", "VOID", "BLOCKED"
LAND_KIND = "LAND"   # kind tag used in surface records


def engine_z(z):
    """FIXED.DAT z as the engine reads it: an unsigned byte."""
    return z & 0xFF


class WalkGrid:
    """Rasterized surfaces + blockers over a region of interest."""

    def __init__(self, items, roi, shapes, glob_reader=None,
                 exclude=None):
        """items: MapItems (glob eggs still folded); roi: (x0,y0,x1,y1)
        world rect; shapes: parse_typeflag ShapeInfo list; exclude:
        optional predicate(item) -> True to drop an item (used for the
        boulder-removal counterfactual)."""
        self.roi = roi
        self.shapes = shapes
        self._surf = {}    # (ci,cj) -> [(top, kind, order, item)]
        self._block = {}   # (ci,cj) -> [(z0, z1, item)]
        self._levels = {}  # (ci,cj) -> collapsed level list (lazy)

        expanded = []
        gr = glob_reader
        for it in items:
            if exclude is not None and exclude(it):
                continue
            if it.is_glob_egg:
                if gr is None:
                    gr = GlobReader()
                expanded.extend(gr.glob_to_items(
                    it.quality, it.x, it.y, engine_z(it.z)))
            else:
                expanded.append(it)
        self.items = expanded

        for order, it in enumerate(expanded):
            self._rasterize(order, it)

    # -- geometry ----------------------------------------------------------

    def footpad_world(self, item):
        """(xd, yd, zd) world units, honoring FLG_FLIPPED."""
        if item.shape < 0 or item.shape >= len(self.shapes):
            return 0, 0, 0
        si = self.shapes[item.shape]
        xd, yd = si.footpad_x * 32, si.footpad_y * 32
        if item.flags & FLG_FLIPPED:
            xd, yd = yd, xd
        return xd, yd, si.footpad_z * 8

    @staticmethod
    def cell_of(x, y):
        return x // CELL, y // CELL

    @staticmethod
    def _cell_range(hi, d):
        """Cells whose CENTER (32i+16) lies in the world span (hi-d, hi]."""
        if d <= 0:
            return range(0)
        i_min = (hi - d - CELL // 2) // CELL + 1
        i_max = (hi - CELL // 2) // CELL
        return range(i_min, i_max + 1)

    def _rasterize(self, order, it):
        # Contained items store container depth in x; the off-map staging
        # margin also lives below 64 (same heuristic as map_validate).
        if it.x < 64 or it.y < 64:
            return
        if it.shape in EGG_SHAPES:
            return
        if it.shape < 0 or it.shape >= len(self.shapes):
            return
        si = self.shapes[it.shape]
        flags = si.flags0
        is_land = bool(flags & FLAG_LAND)
        is_sea = bool(flags & FLAG_SEA)
        is_solid = bool(flags & FLAG_SOLID)
        if not (is_land or is_sea or is_solid):
            return

        xd, yd, zd = self.footpad_world(it)
        if xd <= 0 or yd <= 0:
            return  # zero-area footpad: no collision, no support
        x0r, y0r, x1r, y1r = self.roi
        if it.x - xd >= x1r or it.x <= x0r or it.y - yd >= y1r or it.y <= y0r:
            return

        z = engine_z(it.z)
        surf = (z + zd, SEA if is_sea else LAND_KIND, order, it) \
            if (is_land or is_sea) else None
        blk = (z, z + zd, it) if (is_solid and zd > BLOCKER_MIN_ZD) else None
        if surf is None and blk is None:
            return

        for ci in self._cell_range(it.x, xd):
            for cj in self._cell_range(it.y, yd):
                key = (ci, cj)
                if surf is not None:
                    self._surf.setdefault(key, []).append(surf)
                if blk is not None:
                    self._block.setdefault(key, []).append(blk)

    # -- per-cell levels -----------------------------------------------------

    def levels(self, ci, cj):
        """Collapsed surface levels for a cell, ascending by top:
        [{level, kind, item, blocked, blocker}]. Equal tops collapse to
        the latest item in map order (later items draw on top)."""
        key = (ci, cj)
        if key in self._levels:
            return self._levels[key]
        out = []
        surfs = self._surf.get(key)
        if surfs:
            by_top = {}
            for top, kind, order, it in surfs:
                prev = by_top.get(top)
                if prev is None or order > prev[1]:
                    by_top[top] = (kind, order, it)
            blocks = self._block.get(key, ())
            for top in sorted(by_top):
                kind, _order, it = by_top[top]
                blocked_by = None
                for z0, z1, bit in blocks:
                    if z0 < top + AVATAR_ZD and z1 > top + STEP_Z:
                        blocked_by = bit
                        break
                out.append({"level": top, "kind": kind, "item": it,
                            "blocked": blocked_by is not None,
                            "blocker": blocked_by})
        self._levels[key] = out
        return out

    def status_at(self, x, y, z_ref, ignore=None):
        """(status, level_rec) for the cell containing (x,y), judged at
        the surface level nearest z_ref (at or below z_ref + STEP_Z).
        ignore: item to exclude from blocking (a solid target item does
        not block its own placement check)."""
        ci, cj = self.cell_of(x, y)
        lvls = self.levels(ci, cj)
        if not lvls:
            return VOID, None
        cands = [l for l in lvls if l["level"] <= z_ref + STEP_Z]
        if not cands:
            return VOID, None
        rec = max(cands, key=lambda l: l["level"])
        if rec["kind"] == SEA:
            return SEA, rec
        blocked = rec["blocked"]
        if blocked and ignore is not None:
            blocked = any(
                z0 < rec["level"] + AVATAR_ZD and z1 > rec["level"] + STEP_Z
                and bit is not ignore
                for z0, z1, bit in self._block.get((ci, cj), ()))
        if blocked:
            return BLOCKED, rec
        return WALKABLE, rec

    # -- flood fill ----------------------------------------------------------

    def _body_fits(self, ci, cj, lv, body_cells):
        """Can a body_cells x body_cells mover stand with its MAX corner in
        cell (ci,cj) at level lv? Item positions are the max corner (see
        u8_map.wall_run_x), so the body covers cells
        (ci-body+1..ci, cj-body+1..cj). Every one of them must offer a
        walkable surface within STEP_Z of lv.

        body_cells=1 reproduces the historical point-mover behaviour; the
        Avatar is really 64x64 = 2 cells, and the shrunken Avatar 32x32 =
        1 cell, which is the entire basis of the Tiny Tar crack (DD-005).
        """
        if body_cells <= 1:
            return True
        for bi in range(ci - body_cells + 1, ci + 1):
            for bj in range(cj - body_cells + 1, cj + 1):
                if bi == ci and bj == cj:
                    continue
                ok = False
                for rec in self.levels(bi, bj):
                    if rec["kind"] == SEA or rec["blocked"]:
                        continue
                    if abs(rec["level"] - lv) <= STEP_Z:
                        ok = True
                        break
                if not ok:
                    return False
        return True

    def flood(self, seeds, body_cells=1, blocked_cells=frozenset()):
        """Multi-level BFS. seeds: [(x, y, z)]. Returns
        {(ci,cj): set(levels reached)}. Unseated seeds are skipped (the
        caller should verify seeds with status_at first).

        body_cells: width of the mover in 32-unit cells. Default 1 keeps
        every historical caller's behaviour (a point mover). Pass
        BODY_AVATAR (2) to model the real 64x64 Avatar box the engine
        checks in canExistAt(), or BODY_TINY (1) for the shrunken form.

        blocked_cells: (ci, cj) cells the flood must not enter, for the
        one thing the raster cannot judge — a one-body-width aperture
        (see .claude/rules/map-geometry.md). The caller decides with exact
        box arithmetic whether the engine refuses it, then seals it here
        and asks the raster the question it is good at: is there any
        OTHER way through.
        """
        x0r, y0r, x1r, y1r = self.roi
        ci_lo, cj_lo = x0r // CELL, y0r // CELL
        ci_hi, cj_hi = x1r // CELL, y1r // CELL

        reached = {}
        q = deque()
        for (sx, sy, sz) in seeds:
            ci, cj = self.cell_of(sx, sy)
            if (ci, cj) in blocked_cells:
                continue
            best = None
            for rec in self.levels(ci, cj):
                if rec["kind"] == SEA or rec["blocked"]:
                    continue
                d = abs(rec["level"] - sz)
                if d <= 2 * STEP_Z and (best is None or d < best[1]):
                    best = (rec["level"], d)
            if best is None:
                continue
            lv = best[0]
            if not self._body_fits(ci, cj, lv, body_cells):
                continue
            if lv not in reached.setdefault((ci, cj), set()):
                reached[(ci, cj)].add(lv)
                q.append((ci, cj, lv))

        while q:
            ci, cj, lv = q.popleft()
            for ni, nj in ((ci + 1, cj), (ci - 1, cj),
                           (ci, cj + 1), (ci, cj - 1)):
                if not (ci_lo <= ni <= ci_hi and cj_lo <= nj <= cj_hi):
                    continue
                if (ni, nj) in blocked_cells:
                    continue
                for rec in self.levels(ni, nj):
                    if rec["kind"] == SEA or rec["blocked"]:
                        continue
                    nl = rec["level"]
                    if abs(nl - lv) > STEP_Z:
                        continue
                    if not self._body_fits(ni, nj, nl, body_cells):
                        continue
                    seen = reached.setdefault((ni, nj), set())
                    if nl not in seen:
                        seen.add(nl)
                        q.append((ni, nj, nl))
        return reached

    def reached_near(self, reached, item, level, ring=RING):
        """True if the flood reached a cell within `ring` world units of
        the item's footprint box, at a level within STEP_Z of `level`."""
        xd, yd, _zd = self.footpad_world(item)
        xd, yd = max(xd, CELL), max(yd, CELL)
        for ci in self._cell_range(item.x + ring, xd + 2 * ring):
            for cj in self._cell_range(item.y + ring, yd + 2 * ring):
                for lv in reached.get((ci, cj), ()):
                    if abs(lv - level) <= STEP_Z:
                        return True
        return False


# ===========================================================================
# Support checks for placed things (talismans, eggs, apparitions...)
# ===========================================================================

def check_support(grid, item, label, results, want_reach=None,
                  reach_label=""):
    """PASS/FAIL: the item stands on walkable, non-SEA ground (support
    surface within STEP_Z below its z, not floating, not water, and the
    standing spot is not inside another blocker). If want_reach is a
    flood result, also require the item be reachable (its own cell or
    the RING around it)."""
    z = engine_z(item.z)
    status, rec = grid.status_at(item.x, item.y, z, ignore=item)
    pos = f"({item.x},{item.y},{z})"
    if rec is None:
        results.fail(f"{label} {pos}: NO support surface under it — "
                     f"floating in a void / missing terrain")
        return None
    lvl = rec["level"]
    sup = f"shape {rec['item'].shape} top z={lvl}"
    if status == SEA:
        results.fail(f"{label} {pos}: stands on WATER ({sup}, SEA) — "
                     f"drowning hazard")
        return None
    if z - lvl > STEP_Z:
        results.fail(f"{label} {pos}: FLOATING {z - lvl} units above its "
                     f"support ({sup})")
        return lvl
    if status == BLOCKED:
        blk = rec["blocker"]
        results.fail(f"{label} {pos}: standing spot is blocked by solid "
                     f"shape {blk.shape} at ({blk.x},{blk.y},{engine_z(blk.z)})")
        return lvl

    if want_reach is not None:
        if grid.reached_near(want_reach, item, lvl):
            results.ok(f"{label} {pos}: on walkable ground ({sup}), "
                       f"reachable {reach_label}")
        else:
            results.fail(f"{label} {pos}: on walkable ground ({sup}) but "
                         f"NOT reachable {reach_label}")
    else:
        results.ok(f"{label} {pos}: on walkable ground ({sup})")
    return lvl


# ===========================================================================
# Exact interval math for the Map 11 doorway plug (assertion d)
# ===========================================================================

def doorway_coverage(boulders, shapes, door_lo, door_hi, wall_y_lo, wall_y_hi,
                     floor_top):
    """Boulder plugs must cover the doorway x-span (door_lo, door_hi]
    across the wall band y (wall_y_lo, wall_y_hi] at avatar-blocking z.
    Returns (uncovered [(lo, hi]], notes [str], corrected [(x, y)])."""
    notes = []
    covered = []
    for b in boulders:
        si = shapes[b.shape]
        xd, yd, zd = si.footpad_x * 32, si.footpad_y * 32, si.footpad_z * 8
        z = engine_z(b.z)
        x_int = (max(door_lo, b.x - xd), min(door_hi, b.x))
        spans_wall = (b.y >= wall_y_hi and b.y - yd <= wall_y_lo)
        blocks_z = (z <= floor_top + STEP_Z and z + zd >= floor_top + AVATAR_ZD)
        where = f"({b.x},{b.y},{z}) box x({b.x - xd},{b.x}] y({b.y - yd},{b.y}] z[{z},{z + zd})"
        if not spans_wall:
            notes.append(f"boulder {where}: does NOT span the wall band "
                         f"y({wall_y_lo},{wall_y_hi}]")
        if not blocks_z:
            notes.append(f"boulder {where}: z-band does not block the avatar "
                         f"above floor top {floor_top}")
        if x_int[0] < x_int[1] and spans_wall and blocks_z:
            covered.append(x_int)
        if b.x > door_hi or b.x - xd >= door_hi or x_int[0] >= x_int[1]:
            notes.append(f"boulder {where}: lies partly/fully OUTSIDE the "
                         f"doorway ({door_lo},{door_hi}]")

    covered.sort()
    uncovered = []
    cur = door_lo
    for lo, hi in covered:
        if lo > cur:
            uncovered.append((cur, lo))
        cur = max(cur, hi)
    if cur < door_hi:
        uncovered.append((cur, door_hi))

    # Corrected origins: tile 128-wide boxes east from door_lo. Max-corner
    # origin o covers (o-128, o].
    corrected = []
    o = door_lo + 128
    while o <= door_hi:
        corrected.append(o)
        o += 128
    return uncovered, notes, corrected


# ===========================================================================
# Results collector (map_validate-style report)
# ===========================================================================

class Results:
    def __init__(self, title):
        self.title = title
        self.lines = []
        self.n_pass = 0
        self.n_fail = 0

    def ok(self, msg):
        self.n_pass += 1
        self.lines.append(f"  [PASS] {msg}")

    def fail(self, msg):
        self.n_fail += 1
        self.lines.append(f"  [FAIL] {msg}")

    def info(self, msg):
        self.lines.append(f"  [info] {msg}")

    def render(self):
        head = f"{self.title}: {self.n_pass} pass, {self.n_fail} fail"
        return "\n".join([head] + self.lines)


def _spans_from_cells(cells):
    """Merge sorted (cell_index, open?) pairs into world spans
    [(x_lo, x_hi)] over the open runs."""
    spans = []
    run = None
    for ci, open_ in cells:
        if open_:
            if run is None:
                run = [ci, ci]
            else:
                run[1] = ci
        elif run is not None:
            spans.append(run)
            run = None
    if run is not None:
        spans.append(run)
    return [(a * CELL, b * CELL + CELL) for a, b in spans]


# ===========================================================================
# Map 11 suite — Elemental Dungeon
# ===========================================================================

# Doorway carved through the Four Pillars chamber south wall (segment
# i=10 skipped at origin x=8704; wall shape 26 footpad (4,1,6) = 128×32
# → the missing segment leaves (8448, 8704] open) and the aligned pad
# north-wall skip. Wall band across both wall lines (y=22527 chamber,
# y=22528 pad, yd=32): y (22495, 22528].
M11_DOOR_LO, M11_DOOR_HI = 8448, 8704
M11_WALL_Y_LO, M11_WALL_Y_HI = 22496, 22528
M11_FLOOR_TOP = 0            # glob 42 = 16× shape 242 (4,4,0) at z 0
M11_BOUNDARY_ROW_Y = 22512   # cell-center row crossing both wall lines
M11_PAD_X = (8192, 9215)

M11_SEEDS = {
    # teleport DEST 202 (arrival from Map 9) + the wiring.md verification
    # teleports (shared/docs/wiring.md "Verification plan").
    "entry(dest202)": (9728, 1536, 0),
    "hub": (9728, 5632, 0),
    "earth": (3584, 3584, 0),
    "air": (16896, 3584, 0),
    "fire": (3584, 16896, 2),     # z=2 stone walkway over the lava floor
    "water": (10240, 16896, 0),
    "chamber": (8192, 20992, 0),
    "pad(dest205)": (8291, 22639, 0),   # pad 204: the NW corner since
                                        # 2026-10-10 (arrival corridors)
}

M11_TRIGGER_204 = (8960, 23296, 1)      # moved 2026-07-04 onto a marked
                                        # slab in the pad room's SE corner


def run_map11(archive, shapes, gr):
    res = Results("Map 11 (Elemental Dungeon)")
    items = archive.get_map_items(11)
    if not items:
        res.fail("no items for map 11 in FIXED.DAT")
        return res
    roi = (768, 768, 20736, 23808)

    grid = WalkGrid(items, roi, shapes, glob_reader=gr)

    # --- seed validity + per-seed floods -------------------------------
    floods = {}
    for name, (sx, sy, sz) in M11_SEEDS.items():
        st, rec = grid.status_at(sx, sy, sz)
        if st == WALKABLE:
            res.info(f"seed {name} ({sx},{sy},{sz}): ok at level "
                     f"{rec['level']}")
        else:
            why = "" if rec is None else (
                f" (level {rec['level']}, shape {rec['item'].shape})")
            res.fail(f"seed {name} ({sx},{sy},{sz}): {st}{why}")
        floods[name] = grid.flood([(sx, sy, sz)])

    # --- seed-to-seed connectivity (island structure) -------------------
    names = list(M11_SEEDS)
    for i, a in enumerate(names):
        linked = []
        for b in names:
            if b == a:
                continue
            bx, by, bz = M11_SEEDS[b]
            cell = grid.cell_of(bx, by)
            if any(abs(lv - bz) <= 2 * STEP_Z
                   for lv in floods[a].get(cell, ())):
                linked.append(b)
        res.info(f"connectivity: {a} -> " +
                 (", ".join(linked) if linked else "(nothing)"))

    # --- section reachability: the four elemental sections must be
    # reachable from the entry-hall seed (via the hub and corridors) ----
    entry_flood = floods["entry(dest202)"]
    for sect in ("earth", "air", "fire", "water"):
        bx, by, bz = M11_SEEDS[sect]
        cell = grid.cell_of(bx, by)
        if any(abs(lv - bz) <= 2 * STEP_Z
               for lv in entry_flood.get(cell, ())):
            res.ok(f"section reachability: entry(dest202) reaches the "
                   f"{sect} seed ({bx},{by},{bz})")
        else:
            res.fail(f"section reachability: entry(dest202) CANNOT reach "
                     f"the {sect} seed ({bx},{by},{bz})")

    union = {}
    for f in floods.values():
        for cell, lvls in f.items():
            union.setdefault(cell, set()).update(lvls)

    # --- (a) talismans / receptacles / pillars ---------------------------
    # Shapes from the builder: the art track made them custom art (pillars
    # 865, receptacles 866). Until 2026-10-07 this still looked for 721 and
    # 307, found none, and so never checked their support or reach.
    import build_map_11 as b11
    talis = [it for it in items if it.shape == 596]
    recept = [it for it in items
              if it.shape == b11.SHAPE_RECEPTACLE
              and it.npcnum == b11.RECEPTACLE_NPCNUM]
    pillars = [it for it in items
               if it.shape == b11.SHAPE_PILLAR and 201 <= it.quality <= 204]
    if len(talis) != 4:
        res.fail(f"expected 4 talismans (shape 596), found {len(talis)}")
    if len(recept) != 4:
        res.fail(f"expected 4 receptacles (shape {b11.SHAPE_RECEPTACLE} npc "
                 f"{b11.RECEPTACLE_NPCNUM}), found {len(recept)}")
    if len(pillars) != 4:
        res.fail(f"expected 4 quest pillars (shape {b11.SHAPE_PILLAR} "
                 f"q201-204), found {len(pillars)}")

    elem = {101: "Earth", 102: "Air", 103: "Fire", 104: "Water",
            201: "Earth", 202: "Air", 203: "Fire", 204: "Water"}
    for it in talis:
        check_support(grid, it, f"talisman[{elem.get(it.quality, it.quality)}]",
                      res, want_reach=union, reach_label="from a seed")
    for it in recept:
        check_support(grid, it, f"receptacle[{elem.get(it.quality, it.quality)}]",
                      res, want_reach=union, reach_label="from a seed")
    for it in pillars:
        check_support(grid, it, f"pillar[{elem.get(it.quality, it.quality)}]",
                      res, want_reach=union, reach_label="from a seed")

    # --- plug boulders: support (informational placement sanity) --------
    plugs = [it for it in items if it.shape == 66 and it.quality == 299]
    for it in plugs:
        check_support(grid, it, "plug boulder", res)

    # --- teleporter pad trigger ------------------------------------------
    tx, ty, tz = M11_TRIGGER_204
    trig = [it for it in items if it.is_teleport_target
            and it.quality == 204]
    if not trig:
        res.fail("teleport TRIGGER 204 not found on map 11")
    else:
        t = trig[0]
        st, rec = grid.status_at(t.x, t.y, engine_z(t.z))
        if st == WALKABLE:
            reach = grid.reached_near(floods["pad(dest205)"], t,
                                      rec["level"])
            if reach:
                res.ok(f"teleport TRIGGER 204 ({t.x},{t.y},{engine_z(t.z)}): "
                       f"walkable, reachable from pad seed")
            else:
                res.fail(f"teleport TRIGGER 204 ({t.x},{t.y}): walkable "
                         f"but NOT reachable from pad seed")
        else:
            res.fail(f"teleport TRIGGER 204 ({t.x},{t.y}): {st}")

    # --- (b) with plugs PRESENT: chamber must NOT reach the pad ----------
    ch_flood = floods["chamber"]
    t_cell = grid.cell_of(tx, ty)
    leaked = any(abs(lv - tz) <= 2 * STEP_Z
                 for lv in ch_flood.get(t_cell, ()))
    if leaked:
        res.fail("plug-present isolation: path EXISTS from pillar chamber "
                 "to the teleporter pad (sealing boulders do not seal)")
    else:
        res.ok("plug-present isolation: no path from pillar chamber to "
               "teleporter pad")

    # Where does the boundary leak? Walk the wall row.
    row_j = M11_BOUNDARY_ROW_Y // CELL
    cells = []
    for ci in range(M11_PAD_X[0] // CELL, M11_PAD_X[1] // CELL + 1):
        recs = grid.levels(ci, row_j)
        open_ = any(r["kind"] == LAND_KIND and not r["blocked"]
                    and abs(r["level"] - M11_FLOOR_TOP) <= STEP_Z
                    for r in recs)
        cells.append((ci, open_))
    spans = _spans_from_cells(cells)
    if spans:
        span_s = ", ".join(f"x {a}..{b}" for a, b in spans)
        res.info(f"chamber/pad boundary (y≈{M11_BOUNDARY_ROW_Y}) open "
                 f"spans at floor level: {span_s}")
        non_door = [s for s in spans
                    if s[1] <= M11_DOOR_LO or s[0] >= M11_DOOR_HI]
        if non_door:
            res.info("NOTE: correcting the plug origins alone will NOT "
                     "seal the room — the boundary is also open OUTSIDE "
                     "the doorway at " +
                     ", ".join(f"x {a}..{b}" for a, b in non_door) +
                     " (wall-segment spacing gaps, see wall survey)")

    # --- systemic wall-spacing survey -------------------------------------
    # The builders place cave wall segments every 256 units, but shape 26
    # has footpad (4,1,6) = 128 wide and shape 32 (1,4,6) = 128 deep; the
    # base game tiles these shapes every 128 (verified against base
    # FIXED.DAT map 8 wall rows). Count joints between consecutive
    # segments in each wall run that leave a collision gap.
    for wshape, along_x in ((26, True), (32, False)):
        runs = {}
        for it in items:
            if it.shape != wshape or it.x < 64 or it.y < 64:
                continue
            key = (it.y, engine_z(it.z)) if along_x else (it.x, engine_z(it.z))
            runs.setdefault(key, []).append(it.x if along_x else it.y)
        pad = shapes[wshape].footpad_x * 32 if along_x \
            else shapes[wshape].footpad_y * 32
        joints = gaps = 0
        for key, vs in runs.items():
            vs = sorted(vs)
            for a, b in zip(vs, vs[1:]):
                if b - a <= 2 * pad:   # same run (256 spacing or tighter)
                    joints += 1
                    if b - a > pad:
                        gaps += 1
        if joints:
            res.info(f"wall survey shape {wshape}: {gaps}/{joints} "
                     f"segment joints leave a collision gap (builder "
                     f"spacing 256 vs footpad {pad}; base game tiles "
                     f"this shape every {pad})")

    # --- (c) with plugs REMOVED: path MUST exist --------------------------
    grid_open = WalkGrid(items, roi, shapes, glob_reader=gr,
                         exclude=lambda it: it.shape == 66
                         and it.quality == 299)
    ch_x, ch_y, ch_z = M11_SEEDS["chamber"]
    open_flood = grid_open.flood([(ch_x, ch_y, ch_z)])
    t_reach = any(abs(lv - tz) <= 2 * STEP_Z
                  for lv in open_flood.get(t_cell, ()))
    if t_reach:
        res.ok("plug-removed connectivity: chamber reaches the teleporter "
               "pad through the carved doorway")
    else:
        res.fail("plug-removed connectivity: chamber still CANNOT reach "
                 "the teleporter pad with boulders removed")

    # --- (d) exact doorway coverage + corrected origins -------------------
    uncovered, notes, corrected = doorway_coverage(
        plugs, shapes, M11_DOOR_LO, M11_DOOR_HI,
        M11_WALL_Y_LO, M11_WALL_Y_HI, M11_FLOOR_TOP)
    for n in notes:
        res.info(n)
    if uncovered:
        u = ", ".join(f"({a},{b}]" for a, b in uncovered)
        res.fail(f"doorway ({M11_DOOR_LO},{M11_DOOR_HI}] not sealed by the "
                 f"plug boulders — uncovered sub-span(s): {u}")
        fix = ", ".join(f"({x},{M11_WALL_Y_HI})" for x in corrected)
        res.info(f"corrected plug origins (128×128 boulders, max-corner, "
                 f"y={M11_WALL_Y_HI}, z=0): {fix}")
    else:
        res.ok(f"doorway ({M11_DOOR_LO},{M11_DOOR_HI}] fully covered by "
               f"plug boulders")

    # --- informational: byte-wrapped z hazards in ROI ---------------------
    wrapped = [it for it in grid.items
               if engine_z(it.z) >= 200 and it.x >= 64 and it.y >= 64
               and it.shape < len(shapes)
               and (shapes[it.shape].flags0 & (FLAG_SEA | FLAG_LAND))]
    if wrapped:
        from collections import Counter
        c = Counter(it.shape for it in wrapped)
        res.info(f"z byte-wrap suspects (LAND/SEA items at engine z>=200, "
                 f"builder negative z): {sum(c.values())} items, by shape "
                 f"{dict(c)} — e.g. "
                 + ", ".join(f"({it.x},{it.y},{engine_z(it.z)})"
                             for it in wrapped[:3]))
    return res


# ===========================================================================
# Maps 39 / 8 — LORDBRIT quest step 1 regression
# ===========================================================================

def _lb_site(res, archive, shapes, gr, mapnum, roi, egg_xy_z, app_xy_z):
    items = archive.get_map_items(mapnum)
    if not items:
        res.fail(f"no items for map {mapnum} in FIXED.DAT")
        return
    grid = WalkGrid(items, roi, shapes, glob_reader=gr)

    ex, ey, ez = egg_xy_z
    ax, ay, az = app_xy_z

    eggs = [it for it in items if it.shape == 73
            and abs(it.x - ex) <= 4 and abs(it.y - ey) <= 4]
    apps = [it for it in items if it.shape == 411
            and abs(it.x - ax) <= 4 and abs(it.y - ay) <= 4]
    if not eggs:
        res.fail(f"LB egg (shape 73) not found near ({ex},{ey})")
    if not apps:
        res.fail(f"LB apparition (shape 411) not found near ({ax},{ay})")

    st, rec = grid.status_at(ex, ey, ez)
    if st == WALKABLE:
        res.ok(f"LB egg ({ex},{ey},{ez}): on walkable ground (shape "
               f"{rec['item'].shape} top z={rec['level']})")
    else:
        why = "" if rec is None else (
            f" (surface shape {rec['item'].shape} top z={rec['level']})")
        res.fail(f"LB egg ({ex},{ey},{ez}): {st}{why}")

    flood = grid.flood([(ex, ey, ez)])
    if apps:
        check_support(grid, apps[0], "LB apparition", res,
                      want_reach=flood, reach_label="from the egg")
    else:
        st2, rec2 = grid.status_at(ax, ay, az)
        msg = f"LB apparition point ({ax},{ay},{az}): {st2}"
        (res.ok if st2 == WALKABLE else res.fail)(msg)

    # Hatch box: the egg triggers over ±128 units (npcnum 0x44).
    # Classify every cell: SEA cells are drowning hazards (hard FAIL,
    # the Tenebrae moat bug), VOID cells are missing terrain (FAIL),
    # blocked cells are legitimate scenery (the apparition itself is a
    # 96×96×48 solid) and only reported.
    total = walk = void = sea = 0
    blockers = {}
    for ci in grid._cell_range(ex + 128, 256):
        for cj in grid._cell_range(ey + 128, 256):
            total += 1
            recs = [r for r in grid.levels(ci, cj)
                    if abs(r["level"] - ez) <= STEP_Z]
            if not recs:
                void += 1
                continue
            top = max(recs, key=lambda r: r["level"])
            if top["kind"] == SEA:
                sea += 1
            elif top["blocked"]:
                b = top["blocker"]
                blockers[b.shape] = blockers.get(b.shape, 0) + 1
            else:
                walk += 1
    detail = f"{walk}/{total} walkable at z≈{ez}"
    if blockers:
        detail += ", blocked by " + ", ".join(
            f"{n}× shape {s}" for s, n in sorted(blockers.items()))
    if void:
        detail += f", {void} VOID"
    if sea:
        detail += f", {sea} SEA"
    if sea or void:
        res.fail(f"LB egg hatch box (±128): {detail}")
    else:
        res.ok(f"LB egg hatch box (±128): {detail}")


def run_map39(archive, shapes, gr):
    res = Results("Map 39 (Tenebrae gate — LORDBRIT primary)")
    # Grass approach lane: shape-3 tiles (17023-17279, 19583-20095) z=48.
    _lb_site(res, archive, shapes, gr, 39,
             roi=(16512, 19072, 17792, 20608),
             egg_xy_z=(17150, 19700, 48),
             app_xy_z=(17150, 19850, 48))
    return res


def run_map8(archive, shapes, gr):
    import build_map_08 as b8
    res = Results("Map 8 (Mythran approach — LORDBRIT backstop)")
    _lb_site(res, archive, shapes, gr, 8,
             roi=(1536, 1536, 3072, 3072),
             egg_xy_z=(b8.LB_BACKSTOP_EGG_X, b8.LB_BACKSTOP_EGG_Y,
                       b8.LB_BACKSTOP_EGG_Z),
             app_xy_z=(b8.LB_BACKSTOP_APPARITION_X,
                       b8.LB_BACKSTOP_APPARITION_Y,
                       b8.LB_BACKSTOP_APPARITION_Z))
    return res


# ===========================================================================
# Map 10 — quest steps 7-8: Passage stone, PLNTST egg, Ragnar's bag drop
# ===========================================================================

# All three sites are fixed by the quest wiring, not free map choices:
#  - the island stone must equal TypeBushKey (u8c_symbols) and be takeable;
#  - the PLNTST egg (quality 283 = pinned EGGPLANTTEST 1434 - 0x47F) must
#    sit within 100 world units of the Test Plant or its hatch scene finds
#    no plant to destroy (PLNTST.UNK `within 100 ... of referent`);
#  - Ragnar's bag pops at the 1994-hardcoded (16447,25727,64)
#    (RAGNAR.UNK:837) — the map must supply standing ground within STEP_Z
#    below z=64 there, reachable from the Temple Approach.

MAP10_STONE_XY = (13888, 18368)      # build_map_10 island deck placement
MAP10_SHORE_SEED = (13824, 20800, 0)  # south lakeshore, solid land
MAP10_EGG_QUALITY = 283
from lv_shapes import SHAPE_SPECIAL_ROOT, SHAPE_TEST_PLANT  # noqa: E402
MAP10_PLANT_SHAPE = SHAPE_TEST_PLANT  # TypeShortmushroom (PLNTST's target), 871
MAP10_BAG_DROP = (16447, 25727, 64)   # RAGNAR.UNK:837, exact
MAP10_APPROACH_SEED = (16447, 24448, 0)  # Temple Approach interior
MAP10_ROOT_XY = (21376, 16640)        # special root by the Sacred Circle stones
MAP10_ROOT_SEED = (20480, 16896, 0)   # Sacred Circle centre, barren ground
MAP10_ROOT_SHAPE = SHAPE_SPECIAL_ROOT  # TypeWeedz, 869, frame 0

# EGGSHADES ceremony (quest steps 14-15, wired 2026-07-27). Coordinates
# mirror lv-patched/SHADES.UNK (teleport-ins + send-homes) and
# build_map_10.build_sacred_circle() (the trigger egg).
MAP10_SHADES_EGG_XY = (20480, 17152)
MAP10_SHADES_SCENE_COORDS = [
    ("egg / avatar mark", 20480, 17152),
    ("Atli teleport-in",    20224, 17216),
    ("Thordis teleport-in", 20672, 17312),
    ("Ezrekal teleport-in", 20480, 17472),
]
MAP10_SHADES_HOME_COORDS = [
    ("Atli",    19200, 6400),    # Gunnar-village hut (npcnum 107 placement)
    ("Thordis", 6144, 6656),     # Hoskuld-village spot (npcnum 106)
    ("Ezrekal", 12800, 12544),   # her dwelling (npcnum 116)
]

# Passage Test grounds (quest step 8). The PLNTST egg + Test Plant were
# relocated to the vale's SW corner so the hatch scene lands on real
# terrain instead of void. These mirror build_map_10.build_test_grounds()
# and TESTPLAN.UNK; the plateau walk surface is z=64.
MAP10_GROUNDS_Z = 64
MAP10_EGG_XY = (12800, 29440)         # relocated PLNTST egg
MAP10_PLANT_XY = (12800, 29408)       # relocated Test Plant
MAP10_GROUNDS_ROI = (12160, 29056, 13440, 30272)   # the z=64 plateau + margin
MAP10_LINK_ROI = (11264, 20480, 14336, 30208)      # Moriens -> corridor -> grounds
# Every absolute coordinate the TESTPLAN/PLNTST scene touches (all z=64):
MAP10_SCENE_COORDS = [
    ("avatar teleport", 13055, 30079),
    ("NPC teleport",    12927, 29823),
    ("pop1 wind", 12777, 29801), ("pop1 plant", 12767, 29791),
    ("pop2 wind", 12873, 29737), ("pop2 plant", 12863, 29727),
    ("pop3 wind", 12745, 29673), ("pop3 plant", 12735, 29663),
    ("pop4 wind", 12649, 29705), ("pop4 plant", 12639, 29695),
    ("pop5 wind", 12777, 29577), ("pop5 plant", 12767, 29567),
]


def run_map10(archive, shapes, gr):
    res = Results("Map 10 (quest items — steps 7-8 stone/egg/bag drop)")
    items = archive.get_map_items(10)
    if not items:
        res.fail("no items for map 10 in FIXED.DAT")
        return res

    # --- a) Passage stone: pickable shape, on the deck, reachable -------
    roi = (12800, 17900, 14800, 21100)
    grid = WalkGrid(items, roi, shapes, glob_reader=gr)
    sx, sy = MAP10_STONE_XY
    stones = [it for it in items if it.shape == 798
              and abs(it.x - sx) <= 192 and abs(it.y - sy) <= 192]
    if not stones:
        res.fail(f"Passage stone (shape 798) not found near ({sx},{sy})")
    else:
        st = stones[0]
        if st.frame != 0:
            res.fail(f"Passage stone frame={st.frame} — PLNTST's foreach "
                     f"filters frame=0; the stone would never match")
        else:
            res.ok("Passage stone frame=0 (matches PLNTST's foreach filter)")
        if shapes[st.shape].flags0 & 0x01:  # SI_FIXED
            res.fail("Passage stone shape is SI_FIXED — not pickable")
        seedst, _ = grid.status_at(*MAP10_SHORE_SEED)
        if seedst != WALKABLE:
            res.fail(f"south shore seed {MAP10_SHORE_SEED}: {seedst}")
        flood = grid.flood([MAP10_SHORE_SEED])
        check_support(grid, st, "Passage stone", res,
                      want_reach=flood, reach_label="from the south shore")
        # causeway spot check — mid-lake slab must be LAND above the water
        mst, mrec = grid.status_at(13800, 19500, 8)
        if mst == WALKABLE and mrec["level"] == 8:
            res.ok("causeway mid-point (13800,19500): slab at z=8 over "
                   "the water")
        else:
            res.fail(f"causeway mid-point (13800,19500): {mst} "
                     f"(level {mrec['level'] if mrec else None}) — "
                     f"crossing broken")

    # --- b) PLNTST trigger egg: placed, in range of the plant ------------
    # Relocated 2026-07-05 to the SW Passage Test grounds (z=64 plateau).
    roi = MAP10_GROUNDS_ROI
    grid = WalkGrid(items, roi, shapes, glob_reader=gr)
    eggs = [it for it in items if it.shape == 73
            and it.quality == MAP10_EGG_QUALITY]
    if len(eggs) != 1:
        res.fail(f"expected exactly 1 PLNTST egg (shape 73 quality "
                 f"{MAP10_EGG_QUALITY}), found {len(eggs)}")
    else:
        egg = eggs[0]
        if egg.npcnum != 0x44:
            res.fail(f"PLNTST egg npcnum=0x{egg.npcnum:02X} — want 0x44 "
                     f"(4x4 hatch box, DD-007a)")
        else:
            res.ok("PLNTST egg quality 283 npcnum 0x44 (DD-007a)")
        ez = engine_z(egg.z)
        st, rec = grid.status_at(egg.x, egg.y, ez)
        if st == WALKABLE:
            res.ok(f"PLNTST egg ({egg.x},{egg.y},{ez}): on walkable "
                   f"ground (shape {rec['item'].shape} top z={rec['level']})")
        else:
            res.fail(f"PLNTST egg ({egg.x},{egg.y},{ez}): {st}")
        plants = [it for it in items if it.shape == MAP10_PLANT_SHAPE
                  and it.frame == 0
                  and max(abs(it.x - egg.x), abs(it.y - egg.y)) <= 96]
        if plants:
            p = plants[0]
            d = max(abs(p.x - egg.x), abs(p.y - egg.y))
            res.ok(f"Test Plant (shape {MAP10_PLANT_SHAPE} frame 0) {d} "
                   f"units from the egg — inside PLNTST's 100-unit hatch "
                   f"search")
        else:
            res.fail(f"no Test Plant (shape {MAP10_PLANT_SHAPE} frame 0) "
                     f"within 96 units of the PLNTST egg — hatch would "
                     f"consume the stone and destroy nothing")
        # hatch box scan, LB-style: SEA/VOID in the ±128 box are failures
        total = walk = void = sea = 0
        blockers = {}
        for ci in grid._cell_range(egg.x + 128, 256):
            for cj in grid._cell_range(egg.y + 128, 256):
                total += 1
                recs = [r for r in grid.levels(ci, cj)
                        if abs(r["level"] - ez) <= STEP_Z]
                if not recs:
                    void += 1
                    continue
                top = max(recs, key=lambda r: r["level"])
                if top["kind"] == SEA:
                    sea += 1
                elif top["blocked"]:
                    b = top["blocker"]
                    blockers[b.shape] = blockers.get(b.shape, 0) + 1
                else:
                    walk += 1
        detail = f"{walk}/{total} walkable at z≈{ez}"
        if blockers:
            detail += ", blocked by " + ", ".join(
                f"{n}× shape {s}" for s, n in sorted(blockers.items()))
        if void:
            detail += f", {void} VOID"
        if sea:
            detail += f", {sea} SEA"
        if sea or void:
            res.fail(f"PLNTST egg hatch box (±128): {detail}")
        else:
            res.ok(f"PLNTST egg hatch box (±128): {detail}")

    # --- c) Ragnar's bag drop: ground within a step below z=64 ----------
    roi = (15900, 24200, 17500, 26300)
    grid = WalkGrid(items, roi, shapes, glob_reader=gr)
    bx, by, bz = MAP10_BAG_DROP
    st, rec = grid.status_at(bx, by, bz)
    if rec is None:
        res.fail(f"Ragnar bag drop ({bx},{by},{bz}): VOID — the bag pops "
                 f"into nothing (RAGNAR.UNK:837 is hardcoded; the map "
                 f"must supply ground here)")
    elif st != WALKABLE:
        res.fail(f"Ragnar bag drop ({bx},{by},{bz}): {st} (surface shape "
                 f"{rec['item'].shape} top z={rec['level']})")
    elif bz - rec["level"] > STEP_Z:
        res.fail(f"Ragnar bag drop ({bx},{by},{bz}): bag would float "
                 f"{bz - rec['level']} units above the surface (shape "
                 f"{rec['item'].shape} top z={rec['level']})")
    else:
        res.ok(f"Ragnar bag drop ({bx},{by},{bz}): lands {bz - rec['level']} "
               f"units above shape {rec['item'].shape} top z={rec['level']} "
               f"(within one step — takeable where it rests)")
        seedst, _ = grid.status_at(*MAP10_APPROACH_SEED)
        if seedst != WALKABLE:
            res.fail(f"approach seed {MAP10_APPROACH_SEED}: {seedst}")
        flood = grid.flood([MAP10_APPROACH_SEED])
        drop_cell = grid.cell_of(bx, by)
        lvls = flood.get(drop_cell, ())
        if any(abs(lv - rec["level"]) <= STEP_Z for lv in lvls):
            res.ok(f"bag drop cell reachable from the Temple Approach "
                   f"(flood reaches levels {sorted(lvls)})")
        else:
            near = [lv for c, ls in flood.items()
                    if max(abs(c[0] - drop_cell[0]),
                           abs(c[1] - drop_cell[1])) <= 2 for lv in ls]
            if any(abs(lv - rec["level"]) <= STEP_Z for lv in near):
                res.ok("bag drop reachable (flood reaches an adjacent "
                       "cell at crown level)")
            else:
                res.fail(f"bag drop NOT reachable from the Temple "
                         f"Approach (drop cell levels reached: "
                         f"{sorted(lvls)})")

    # --- d) Passage Test grounds: scene coords walkable @64, reachable ---
    # The hatch scene teleports/pops items to hard 1994 coordinates that
    # used to be void. Every one must now stand on the z=64 plateau, and
    # the plateau must be reachable on foot from the existing walkable net
    # (the south lakeshore, via Moriens Ruins + the ramped corridor).
    Z = MAP10_GROUNDS_Z
    grid = WalkGrid(items, MAP10_LINK_ROI, shapes, glob_reader=gr)

    for label, cx, cy in MAP10_SCENE_COORDS:
        st, rec = grid.status_at(cx, cy, Z)
        if st == WALKABLE and rec is not None and abs(rec["level"] - Z) <= STEP_Z:
            res.ok(f"TESTPLAN {label} ({cx},{cy},{Z}): walkable "
                   f"(shape {rec['item'].shape} top z={rec['level']})")
        else:
            lvl = None if rec is None else rec["level"]
            res.fail(f"TESTPLAN {label} ({cx},{cy},{Z}): {st} (top z={lvl}) "
                     f"— scene item lands in void/blocked")

    # The Test Plant is SOLID since 2026-10-11 (shape 871, a (3,3,4) box),
    # so its own point is blocked by itself; it is checked with
    # check_support after the flood below, as the root is.
    for lbl, (tx, ty) in (("PLNTST egg", MAP10_EGG_XY),):
        st, rec = grid.status_at(tx, ty, Z)
        if st == WALKABLE and rec is not None and rec["level"] == Z:
            res.ok(f"{lbl} site ({tx},{ty},{Z}): on the z=64 plateau floor")
        else:
            res.fail(f"{lbl} site ({tx},{ty},{Z}): {st} "
                     f"(top z={None if rec is None else rec['level']})")

    seedst, _ = grid.status_at(*MAP10_SHORE_SEED)
    if seedst != WALKABLE:
        res.fail(f"grounds link: south-shore seed {MAP10_SHORE_SEED}: {seedst}")
    flood = grid.flood([MAP10_SHORE_SEED])
    for lbl, tx, ty in (("PLNTST egg approach", *MAP10_EGG_XY),
                        ("avatar wake point", *MAP10_SCENE_COORDS[0][1:])):
        cell = grid.cell_of(tx, ty)
        lvls = flood.get(cell, ())
        if any(abs(lv - Z) <= STEP_Z for lv in lvls):
            res.ok(f"grounds reachable on foot: south shore -> {lbl} "
                   f"({tx},{ty}) at z={Z}")
        else:
            res.fail(f"grounds NOT reachable on foot: south shore cannot "
                     f"reach {lbl} ({tx},{ty}) at z={Z} "
                     f"(levels reached at that cell: {sorted(lvls)})")
    tplants = [it for it in items if it.shape == MAP10_PLANT_SHAPE
               and it.quality == 10 and (it.x, it.y) == MAP10_PLANT_XY]
    if len(tplants) != 1:
        res.fail(f"expected one Test Plant (shape {MAP10_PLANT_SHAPE} q10) "
                 f"at {MAP10_PLANT_XY}, found {len(tplants)}")
    else:
        check_support(grid, tplants[0], "Test Plant", res, want_reach=flood,
                      reach_label="from the south shore")
    # --- e) Special root (steps 9-10): pickable, frame 9, on reachable
    # ground by the Sacred Circle standing stones -------------------------
    roi = (19000, 15600, 22500, 18300)
    grid = WalkGrid(items, roi, shapes, glob_reader=gr)
    rx, ry = MAP10_ROOT_XY
    roots = [it for it in items if it.shape == MAP10_ROOT_SHAPE
             and abs(it.x - rx) <= 192 and abs(it.y - ry) <= 192]
    if not roots:
        res.fail(f"special root (shape {MAP10_ROOT_SHAPE}) not found near "
                 f"({rx},{ry}) — Ezrekal's root quest has no root to find")
    else:
        rt = roots[0]
        if rt.frame != 0:
            res.fail(f"special root frame={rt.frame} — Ezrekal's foreach "
                     f"filters (type = TypeWeedz) and (frame = 0); it would "
                     f"never match")
        else:
            res.ok("special root frame=0 (matches Ezrekal's foreach filter)")
        if shapes[rt.shape].flags0 & 0x01:  # SI_FIXED
            res.fail(f"special root shape {rt.shape} is SI_FIXED — cannot be "
                     f"picked up, so it can never reach the Avatar's "
                     f"container for Ezrekal's `within container Avatar`")
        else:
            res.ok(f"special root shape {rt.shape} not SI_FIXED (carryable)")
        seedst, _ = grid.status_at(*MAP10_ROOT_SEED)
        if seedst != WALKABLE:
            res.fail(f"Sacred Circle seed {MAP10_ROOT_SEED}: {seedst}")
        flood = grid.flood([MAP10_ROOT_SEED])
        check_support(grid, rt, "special root", res,
                      want_reach=flood, reach_label="from the Sacred Circle")

    # --- f) EGGSHADES ceremony (steps 14-15): trigger egg wired, every
    # scene coordinate walkable at the Sacred Circle -----------------------
    # The 2026-07-27 wiring: egg quality 294 (-> class 1445 EggShades),
    # npcnum 0x88 = +/-256 hatch box, and lv-patched/SHADES.UNK retargets
    # the six 1994 teleports to these coordinates. This is the scene with
    # the only avatarPoisoned cure, so a stranded elder = unwinnable game.
    eggs294 = [it for it in items if it.shape == 73 and it.quality == 294]
    if len(eggs294) != 1:
        res.fail(f"expected exactly one EggShades egg (shape 73 q294) on "
                 f"Map 10, found {len(eggs294)}")
    else:
        se = eggs294[0]
        if (se.x, se.y) != MAP10_SHADES_EGG_XY:
            res.fail(f"EggShades egg at ({se.x},{se.y}), expected "
                     f"{MAP10_SHADES_EGG_XY}")
        else:
            res.ok(f"EggShades egg at {MAP10_SHADES_EGG_XY} q294")
        if se.npcnum != 0x88:
            res.fail(f"EggShades egg npcnum=0x{se.npcnum:02X}, expected "
                     f"0x88 (+/-256 hatch box)")
        else:
            res.ok("EggShades hatch box npcnum=0x88 (+/-256)")
    # Same grid/ROI as the special-root section: the whole ceremony plays
    # inside it. All in-scene points must be walkable AND flood-reachable
    # from the circle centre (the avatar pathfinds to the egg; the elders
    # teleport in and later walk out).
    for lbl, cx, cy in MAP10_SHADES_SCENE_COORDS:
        st, why = grid.status_at(cx, cy, 0)
        levels = flood.get(grid.cell_of(cx, cy), set())
        if st != WALKABLE:
            res.fail(f"SHADES {lbl} ({cx},{cy}) z=0: {st} ({why})")
        elif not any(lv <= STEP_Z for lv in levels):
            res.fail(f"SHADES {lbl} ({cx},{cy}) z=0 walkable but NOT "
                     f"reachable from the Sacred Circle centre "
                     f"(levels reached: {sorted(levels)})")
        else:
            res.ok(f"SHADES {lbl} ({cx},{cy}) walkable + reachable")
    # Send-home destinations, each on its own local grid. The exact cell
    # may be occupied by the NPC's own placement, so the check is: the
    # home cell OR a 64-unit neighbour is walkable (the NPC lands and can
    # step off; a fully blocked neighbourhood strands a quest NPC).
    for who, hx, hy in MAP10_SHADES_HOME_COORDS:
        hroi = (hx - 512, hy - 512, hx + 512, hy + 512)
        hgrid = WalkGrid(items, hroi, shapes, glob_reader=gr)
        cands = [(hx, hy), (hx - 64, hy), (hx + 64, hy),
                 (hx, hy - 64), (hx, hy + 64)]
        good = [c for c in cands if hgrid.status_at(c[0], c[1], 0)[0]
                == WALKABLE]
        if good:
            res.ok(f"SHADES {who} home ({hx},{hy}): landing area walkable "
                   f"({len(good)}/5 cells)")
        else:
            res.fail(f"SHADES {who} home ({hx},{hy}): no walkable cell in "
                     f"the landing area — send-home strands the NPC")

    return res


# ===========================================================================

SUITES = {11: run_map11, 39: run_map39, 8: run_map8, 10: run_map10}
# 18 is registered after run_map18 is defined, further down.


LV_MAPS_WITH_TELEPORTS = (8, 9, 10, 11, 13, 17, 18, 39)
LV_TELEPORT_ID_RANGE = range(200, 214)
MIN_DEST_TRIGGER_SEPARATION = 384


def run_teleport_spacing(archive):
    """Every LV teleport DEST must sit >= MIN_DEST_TRIGGER_SEPARATION
    units from every teleport TRIGGER on the same map — found in-game
    2026-07-04 when three steps into the Vale returned the tester to the
    pillar chamber (Map 10's trigger 205 sat 512 units dead north of dest
    204, on the walking line). (The names here are the pre-771d5c7 ones:
    `dests` are the frame-0 triggers, `triggers` the frame-1 pads.)

    Distance is necessary, not sufficient. Triggers are not point traps:
    npcNum is the hatch range (+/-384 or +/-416 in x on most LV triggers;
    Map 8's 212 is +/-32 since 2026-10-10), and a teleport keeps the
    Avatar's heading, so a held key walks him off the pad along it. Map
    10's pad 212 sat 512 from trigger 213 and still bounced
    (docs/playtest-2026-10-10-mover.md finding 2). The heading check is
    test_route_reach.arrival_corridors, which replays the engine's mover
    (avatar_mover.py) from every pad."""
    res = Results("LV teleport dest/trigger spacing")
    for m in LV_MAPS_WITH_TELEPORTS:
        items = archive.get_map_items(m)
        dests, triggers = [], []
        for it in items:
            if it.shape != MapItem.SHAPE_TELEPORT_EGG:
                continue
            if it.frame == 0 and (it.quality - 256) in LV_TELEPORT_ID_RANGE:
                dests.append(it)
            elif it.frame == 1 and it.quality in LV_TELEPORT_ID_RANGE:
                triggers.append(it)
        for d in dests:
            for t in triggers:
                dist = ((d.x - t.x) ** 2 + (d.y - t.y) ** 2) ** 0.5
                label = (f"map {m}: dest {d.quality - 256} ({d.x},{d.y}) "
                         f"vs trigger {t.quality} ({t.x},{t.y}): "
                         f"{dist:.0f} units")
                if dist >= MIN_DEST_TRIGGER_SEPARATION:
                    res.ok(label)
                else:
                    res.fail(label + f" — closer than "
                             f"{MIN_DEST_TRIGGER_SEPARATION}, bounce risk")
    return res


MAP18_ARRIVAL = (3072, 1792, 0)      # teleport DEST 210, from Map 10
MAP18_ALTAR = (3072, 8192)           # the altar / EggAOCeremony
MAP18_CRACK_CELLS = (88, 89)         # x[2816,2880) — the open cells
# WIDENED 2026-07-28. This used to be (89,) — "the ONE open cell" — and that
# design was impassable in the engine: the raster below quantises to 32-unit
# cells and marks a cell blocked only when a blocker covers its CENTRE, so
# the west filler's last unit (2848) vanished and cell 89 read as fully free
# when the engine had only 31 units of clear span for a 32-unit body. The
# cell model CANNOT adjudicate a one-body-width aperture; the authority is
# test_crack_geometry.py, which reimplements Box::overlaps exactly. The two
# checks below are kept for what the raster IS good at — which cells are
# open, and whether the floods reach — and no longer claim to prove the
# mechanic on their own.
MAP18_CRACK_ROW = 191                # y[6112,6144) — the sanctum boundary


def run_map18(archive, shapes, gr):
    """Map 18: the Tiny Tar crack must seal the temple against a full-size
    Avatar and open it to a shrunken one (DD-005).

    This is the load-bearing assertion of the whole temple-entry design, and
    it cannot be checked by eye: the difference between a working crack and a
    decorative one is 32 world units, and the map's walls come partly from
    glob 80 (which ships its own south wall and doorway per chunk) rather
    than from the builder. So it is proved by flooding the map twice at the
    two real body widths the engine checks in canExistAt().
    """
    res = Results("Map 18 (Ancient Temple — the Tiny Tar crack, DD-005)")
    items = archive.get_map_items(18)
    if not items:
        res.fail("no items for map 18 in FIXED.DAT")
        return res
    roi = (1024, 512, 5120, 8704)
    grid = WalkGrid(items, roi, shapes, glob_reader=gr)

    st, _rec = grid.status_at(*MAP18_ARRIVAL)
    if st != WALKABLE:
        res.fail(f"arrival pad (DEST 210) {MAP18_ARRIVAL}: {st}")
        return res
    res.ok(f"arrival pad {MAP18_ARRIVAL} walkable")

    altar_cell = grid.cell_of(*MAP18_ALTAR)

    # The crack itself is 63 units of clear span, and this raster reads it
    # as two free cells = 64. Until 2026-09-14 the full-size flood was
    # stopped anyway, by accident: the sanctum beyond the crack was a
    # lattice of glob-80 wall stubs, and the god standing 5 units east of
    # the crack's lane pinched the 2-cell body off. The room is open now,
    # so the raster body walked through the crack to the altar and this
    # check failed while test_crack_geometry.py said sealed — which is the
    # exact disagreement .claude/rules/map-geometry.md describes. So: the
    # aperture is adjudicated HERE with Box::overlaps over the expanded
    # items, the same way that test does it; if the engine refuses the
    # full-size body there, those cells are sealed for the full-size flood
    # and the raster answers the question it can — is there any other way.
    line_items = []
    for it in items:
        if it.shape == MapItem.SHAPE_GLOB_EGG:
            line_items.extend(gr.glob_to_items(it.quality, it.x, it.y, it.z))
        else:
            line_items.append(it)
    crack_y = MAP18_CRACK_ROW * CELL + CELL - 1              # 6143
    blockers = []
    for it in line_items:
        si = shapes[it.shape]
        xd, yd, zd = si.footpad_x * 32, si.footpad_y * 32, si.footpad_z * 8
        if (si.flags0 & 0x02) and zd > 0 and abs(it.y - crack_y) <= 64 \
                and 2400 <= it.x <= 3500:
            blockers.append((it.x, it.y, it.z, xd, yd, zd))

    def _overlaps(a, b):        # ultima8/misc/box.h Box::overlaps, verbatim
        ax, ay, az, axd, ayd, azd = a
        bx, by, bz, bxd, byd, bzd = b
        if ax <= bx - bxd or bx <= ax - axd:
            return False
        if ay <= by - byd or by <= ay - ayd:
            return False
        if az + azd <= bz or bz + bzd <= az:
            return False
        return True

    full_fits = [x for x in range(2700, 3100)
                 if not any(_overlaps((x, crack_y, 0, 64, 64, 32), b)
                            for b in blockers)]
    crack_cells = frozenset((ci, MAP18_CRACK_ROW) for ci in MAP18_CRACK_CELLS)
    if full_fits:
        res.fail(f"the crack admits a FULL-SIZE body by box arithmetic "
                 f"({len(full_fits)} positions, [{full_fits[0]}.."
                 f"{full_fits[-1]}]) — the temple is not sealed")
        big = grid.flood([MAP18_ARRIVAL], body_cells=BODY_AVATAR)
    else:
        res.ok("the crack refuses a full-size body (0 positions, exact box "
               "arithmetic) — sealing its cells for the full-size flood")
        big = grid.flood([MAP18_ARRIVAL], body_cells=BODY_AVATAR,
                         blocked_cells=crack_cells)
    small = grid.flood([MAP18_ARRIVAL], body_cells=BODY_TINY)

    if altar_cell in big:
        res.fail("a FULL-SIZE Avatar can reach the altar by some route "
                 "other than the crack — the temple is not sealed, so Tiny "
                 "Tar is pointless and steps 17-18 are free")
    else:
        res.ok(f"full-size Avatar CANNOT reach the altar "
               f"({len(big)} cells, stops north of the sanctum wall)")

    if altar_cell not in small:
        res.fail("a SHRUNKEN Avatar cannot reach the altar either — the "
                 "temple is unenterable and the quest is dead")
    else:
        res.ok(f"shrunken Avatar CAN reach the altar ({len(small)} cells)")

    # Which cells are open. NOTE this no longer proves the mechanic: two
    # open cells is 63 units of clear span, not 64, and only the exact box
    # arithmetic in test_crack_geometry.py can tell those apart. What this
    # loop still catches is a cell going open or closed unintentionally.
    for ci in range(MAP18_CRACK_CELLS[0] - 3, MAP18_CRACK_CELLS[0] + 4):
        x = ci * CELL + 1
        st, _ = grid.status_at(x, MAP18_CRACK_ROW * CELL + 8, 0)
        want_open = ci in MAP18_CRACK_CELLS
        if want_open and st != WALKABLE:
            res.fail(f"crack cell {ci} x[{ci*CELL},{ci*CELL+CELL}) is {st} — "
                     f"the aperture is closed")
        elif not want_open and st == WALKABLE:
            res.fail(f"cell {ci} x[{ci*CELL},{ci*CELL+CELL}) beside the crack "
                     f"is WALKABLE — the aperture has grown; re-run "
                     f"test_crack_geometry.py, the Avatar may now fit")
    res.ok(f"aperture spans exactly the expected cells {MAP18_CRACK_CELLS} "
           f"(clear span 63 units — the width itself is adjudicated by "
           f"test_crack_geometry.py, not by this raster)")

    # The things the ceremony needs, on the far side.
    for label, (ax, ay) in (("altar", MAP18_ALTAR),):
        cand = [it for it in items
                if abs(it.x - ax) <= 192 and abs(it.y - ay) <= 192
                and shapes[it.shape].flags0 & 0x02]
        if cand:
            res.ok(f"{label} present at ({ax},{ay})")
        else:
            res.fail(f"{label} missing near ({ax},{ay})")
    return res


MAP9_ARRIVAL = (13696, 14208, 0)     # pad 201, in from Map 8 (hall, 2026-10-10)
MAP9_EXIT = (14336, 16760)           # TRIGGER 202, on to Map 11


def run_map9(archive, shapes, gr):
    """Map 9 must stay walkable end to end at AVATAR width.

    Added 2026-07-30 because its absence let a wall change seal the map
    silently. Map 9 is three zones stacked north-south, and zone 2's south
    wall sits exactly on the zone-2/zone-3 boundary — it is the only way to
    the Elemental Dungeon teleporter. Before the picket-fence sweep that
    wall was 50% hole and the porosity WAS the doorway; making it solid cut
    the map in half, and every existing check still passed (134 PASS)
    because nothing flooded this map.

    Deliberately flooded at BODY_AVATAR, not the default point mover: the
    failure being guarded is a route too narrow for a 64x64 body, which a
    point flood cannot see.
    """
    res = Results("Map 9 (Galjeron's Chamber — end-to-end route)")
    items = archive.get_map_items(9)
    if not items:
        res.fail("no items for map 9 in FIXED.DAT")
        return res
    xs = [i.x for i in items]
    ys = [i.y for i in items]
    roi = (min(xs) - 256, min(ys) - 256, max(xs) + 256, max(ys) + 256)
    grid = WalkGrid(items, roi, shapes, glob_reader=gr)

    st, _rec = grid.status_at(*MAP9_ARRIVAL)
    if st != WALKABLE:
        res.fail(f"arrival pad (DEST 200) {MAP9_ARRIVAL}: {st}")
        return res
    res.ok(f"arrival pad {MAP9_ARRIVAL} walkable")

    fl = grid.flood([MAP9_ARRIVAL], body_cells=BODY_AVATAR)
    if grid.cell_of(*MAP9_EXIT) in fl:
        res.ok(f"exit TRIGGER 202 {MAP9_EXIT} reachable at Avatar width "
               f"({len(fl)} cells)")
    else:
        res.fail(f"exit TRIGGER 202 {MAP9_EXIT} NOT reachable from the "
                 f"arrival pad at Avatar width — Map 9 is a dead end and the "
                 f"Elemental Dungeon is cut off ({len(fl)} cells reached)")
    return res


def run_event_eggs(archive, shapes, gr):
    """Every LV event egg (shape 73, quality >= 200) must be dispatchable
    and standable-on, on whatever map it sits.

    This is a cross-map suite rather than a per-map one because the failure
    mode it guards is uniform and has now bitten FOUR times: the quality
    field being written as a LABEL rather than as the class selector it is
    (`class = quality + 0x47F`). Map 10's "SHADES trigger" carried
    quality 2 (-> MONEGG), Map 17's obelisk carried 3 (-> BARENTRY), and
    Map 18 carried 4 and 5, which addressed the base game's TORAN EXECUTION
    cutscene and an unrelated Tenebrae scene INSIDE the Zealan temple. All
    four are fixed; this suite makes a fifth impossible to ship.

    Checks per egg:
      1. quality resolves to a class that is actually PINNED in the
         manifest (a typo now fails the build instead of silently running
         base-game Pagan code);
      2. npcNum is non-zero — it packs the hatch box (x range = high
         nibble, y range = low nibble), and 0x00 means zero range, which
         is why neither Map 18 egg was ever observed firing;
      3. the egg stands on real supported ground, so the player can
         physically walk into its box.
    """
    res = Results("LV event eggs (dispatch + hatch box + standable)")
    manifest_path = os.path.join(BASE_DIR, "shared", "build",
                                 "lv_manifest.json")
    try:
        with open(manifest_path) as fh:
            pinned = {v: k for k, v in json.load(fh)["classes"].items()}
    except (OSError, ValueError, KeyError):
        res.fail(f"could not read class pins from {manifest_path}")
        return res

    found = 0
    for m in sorted(archive.non_empty_maps()):
        items = archive.get_map_items(m)
        eggs = [i for i in items
                if i.shape == 73 and i.quality >= 200]
        if not eggs:
            continue
        for e in eggs:
            found += 1
            cid = e.quality + 0x47F
            name = pinned.get(cid)
            where = f"map {m} ({e.x},{e.y},{e.z}) q={e.quality}"
            if name is None:
                res.fail(f"{where}: dispatches class {cid}, which is NOT a "
                         f"pinned LV class — quality was probably written "
                         f"as a label, not a class selector")
                continue
            res.ok(f"{where} -> class {cid} {name}")
            if e.npcnum == 0:
                res.fail(f"{where} ({name}): npcNum 0x00 = ZERO hatch "
                         f"range; the egg can never be walked into")
            else:
                xr, yr = (e.npcnum >> 4) & 0xF, e.npcnum & 0xF
                res.ok(f"{where} ({name}): hatch box +/-{xr * 32}x"
                       f"{yr * 32} (npcNum 0x{e.npcnum:02X})")
            roi = (e.x - 768, e.y - 768, e.x + 768, e.y + 768)
            grid = WalkGrid(items, roi, shapes, glob_reader=gr)
            check_support(grid, e, f"{name} egg", res)
    if not found:
        res.fail("no LV event eggs found at all — expected several")
    return res


SUITES[9] = run_map9
SUITES[18] = run_map18


def run_all(fixed_path=DEFAULT_FIXED, map_nums=(11, 39, 8, 10, 18, 9)):
    """Run the declared suites. Returns (report_text, all_passed)."""
    archive = MapArchive(fixed_path)
    shapes = load_typeflag()
    gr = GlobReader()

    blocks = []
    total_pass = total_fail = 0
    for m in map_nums:
        r = SUITES[m](archive, shapes, gr)
        blocks.append(r.render())
        total_pass += r.n_pass
        total_fail += r.n_fail
    spacing = run_teleport_spacing(archive)
    blocks.append(spacing.render())
    total_pass += spacing.n_pass
    total_fail += spacing.n_fail
    eggs = run_event_eggs(archive, shapes, gr)
    blocks.append(eggs.render())
    total_pass += eggs.n_pass
    total_fail += eggs.n_fail
    blocks.append(f"\nTotal: {total_pass} PASS, {total_fail} FAIL")
    return "\n\n".join(blocks), total_fail == 0


def main():
    ap = argparse.ArgumentParser(
        description="Headless walkability/reachability validator")
    ap.add_argument("--fixed", default=DEFAULT_FIXED,
                    help=f"Path to FIXED.DAT (default: {DEFAULT_FIXED})")
    ap.add_argument("--maps", default="11,39,8,10,18,9",
                    help="Comma-separated suite maps (of 11, 39, 8, 10, 18, 9)")
    args = ap.parse_args()

    if not os.path.exists(args.fixed):
        print(f"ERROR: FIXED.DAT not found at {args.fixed}")
        sys.exit(1)

    map_nums = [int(m) for m in args.maps.split(",") if m.strip()]
    for m in map_nums:
        if m not in SUITES:
            print(f"ERROR: no walkability suite for map {m} "
                  f"(have: {sorted(SUITES)})")
            sys.exit(1)

    print(f"Walkability validation: {args.fixed}")
    print(f"Cell {CELL}, step {STEP_Z}, avatar height {AVATAR_ZD}\n")
    report, ok = run_all(args.fixed, map_nums)
    print(report)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

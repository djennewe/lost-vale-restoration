#!/usr/bin/env python3
"""
village_layout.py — APPROACH 3: PROCEDURAL LAYOUT.

Auto-arranges prefab buildings into a believable Lost Vale village without any
hand-placement. A "PlotMap" style engine: it places prefab footprints on plots
subject to spatial constraints (no overlap, minimum gap, stay in bounds), then
connects each building to a central plaza/well with path tiles and fills the
ground with terrain glob eggs.

The engine is prefab-agnostic. It consumes any object implementing the shared
Stampable protocol (duck-typed):

    name: str
    footprint: (w, h)       # bounding-box size in world units
    tags: list[str]
    origin_z: int
    def stamp(self, dest_x, dest_y, z_base=0) -> list[MapItem]:
        # items positioned with the structure's min corner at (dest_x, dest_y)

The real prefab modules are built in parallel and not available here yet, so a
few inline stub prefabs (StubHut / StubLonghouse / StubHall + StubWell /
StubCampfire props) are included purely for the self-test render.

Public API:
    VillageSpec                              — layout description (dataclass)
    generate_village(spec, prefabs, props=None, seed=None) -> list[MapItem]
    plan_layout(spec, prefabs, seed=None)    -> (list[Placement], shortfall)
    check_overlaps(placements)               -> int   (0 after a good layout)

Self-test:
    cd agents/map-populator/src && python3 village_layout.py
"""

import math
import os
import random
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from u8_map import MapItem, generate_terrain_grid

# Floor/diamond tile size in world units. A U8 land tile sprite is a 62x32
# isometric diamond whose footprint is 128x128 world units, so prefab footprints
# and path runs step on this grid.
TILE = 128


# ===========================================================================
# Spec + placement record
# ===========================================================================

@dataclass
class VillageSpec:
    """Describes one procedural village.

    center        : (x, y) world coords of the plaza / well.
    bounds        : (half_w, half_h) — village occupies center +/- these.
    target_buildings : how many prefabs to place.
    style         : "cluster" (ring around a central plaza) or
                    "road" (buildings line a path axis).
    ground_glob   : glob index used to tile the ground (generate_terrain_grid).
    ground_z      : the village's terrain height (H7). Every structure is
                    stamped with this as its z_base, and the ground tiles are
                    laid at it. Default 0, which is where Map 10's terrain
                    globs (40/43/55) put their walkable surface. This used to
                    be each prefab's own origin_z, which is a SOURCE datum,
                    not a destination height — see the stamp sites below.
    seed          : RNG seed — placement is fully deterministic.
    require_tags  : if set, prefer prefabs carrying any of these tags.
    min_gap       : minimum clear gap (world units) between footprints.
    ring_radius   : cluster ring radius (defaults to ~55% of min bound).
    road_axis     : "x" or "y" — main axis for the "road" style.
    road_offset   : perpendicular distance from the road centerline to a
                    building's near edge.
    path_shape    : floor-tile shape used for paths (None disables shape paths).
    path_frame    : frame for path_shape tiles.
    path_glob     : alternative coarse path made of glob eggs (None = unused).
    chunk_size    : terrain chunk size for ground fill (engine constant 512).
    """
    center: Tuple[int, int]
    bounds: Tuple[int, int] = (1792, 1792)
    target_buildings: int = 6
    style: str = "cluster"
    ground_glob: int = 43
    ground_z: int = 0
    seed: int = 1234
    require_tags: Optional[List[str]] = None
    min_gap: int = 96
    ring_radius: Optional[int] = None
    road_axis: str = "x"
    road_offset: int = 384
    path_shape: Optional[int] = 3
    path_frame: int = 0
    path_glob: Optional[int] = None
    chunk_size: int = 512
    grid_snap: Optional[int] = None   # snap placements to this grid (e.g. 512
                                      # for glob buildings, which the engine
                                      # snaps to their 512-unit chunk anyway)


@dataclass
class Placement:
    """A prefab committed to a spot. Min corner of footprint at (x, y)."""
    prefab: object
    x: int
    y: int

    @property
    def w(self) -> int:
        return self.prefab.footprint[0]

    @property
    def h(self) -> int:
        return self.prefab.footprint[1]

    @property
    def box(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)


# ===========================================================================
# Geometry helpers
# ===========================================================================

def _rects_overlap(a, b, gap=0) -> bool:
    """True if rect a and b (x, y, w, h) come within `gap` of each other.

    gap=0 is a strict geometric overlap (shared edges do NOT count). gap>0
    additionally rejects boxes that sit closer than `gap` apart.
    """
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return (ax - gap < bx + bw and bx - gap < ax + aw and
            ay - gap < by + bh and by - gap < ay + ah)


def check_overlaps(placements: List[Placement]) -> int:
    """Count unordered pairs of placements whose footprints truly overlap.

    Should be 0 after a successful layout (the placer guarantees a min_gap >= 0).
    """
    count = 0
    for i in range(len(placements)):
        for j in range(i + 1, len(placements)):
            if _rects_overlap(placements[i].box, placements[j].box, gap=0):
                count += 1
    return count


def _snap(v, g):
    """Round v to the nearest multiple of grid g."""
    return int(round(v / g) * g)


def _clamp_box(x, y, w, h, cx, cy, bw, bh):
    """Clamp a w*h box so it stays inside the village rect, or None if it can't."""
    minx, miny = cx - bw, cy - bh
    maxx, maxy = cx + bw, cy + bh
    if w > (maxx - minx) or h > (maxy - miny):
        return None
    x = min(max(x, minx), maxx - w)
    y = min(max(y, miny), maxy - h)
    return int(x), int(y)


def _front_anchor(p: Placement, target: Tuple[int, int]) -> Tuple[int, int]:
    """Point on a building's footprint boundary nearest to `target`.

    Used as the spot a path leaves the building from (its "front").
    """
    tx, ty = target
    ax = min(max(tx, p.x), p.x + p.w)
    ay = min(max(ty, p.y), p.y + p.h)
    return int(ax), int(ay)


def _pick_prefab(prefabs, rng, require_tags):
    """Pick a prefab, preferring those that carry any required tag."""
    pool = prefabs
    if require_tags:
        tagged = [p for p in prefabs
                  if any(t in getattr(p, "tags", []) for t in require_tags)]
        if tagged:
            pool = tagged
    return rng.choice(pool)


# ===========================================================================
# Placement strategies
# ===========================================================================

MAX_TRIES_PER_BUILDING = 40


def _place_cluster(spec, prefabs, rng, placed):
    """Ring the buildings around the central plaza, facing inward."""
    cx, cy = spec.center
    bw, bh = spec.bounds
    ring = spec.ring_radius or int(min(bw, bh) * 0.55)
    n = spec.target_buildings

    for i in range(n):
        base_angle = 2 * math.pi * i / max(1, n)
        committed = False
        for _ in range(MAX_TRIES_PER_BUILDING):
            prefab = _pick_prefab(prefabs, rng, spec.require_tags)
            w, h = prefab.footprint
            angle = base_angle + rng.uniform(-0.35, 0.35)
            rad = ring * rng.uniform(0.82, 1.18)
            bxc = cx + rad * math.cos(angle)
            byc = cy + rad * math.sin(angle)
            clamped = _clamp_box(bxc - w / 2, byc - h / 2, w, h, cx, cy, bw, bh)
            if clamped is None:
                continue
            x, y = clamped
            if spec.grid_snap:
                x, y = _snap(x, spec.grid_snap), _snap(y, spec.grid_snap)
            if any(_rects_overlap((x, y, w, h), q.box, spec.min_gap)
                   for q in placed):
                continue
            placed.append(Placement(prefab, x, y))
            committed = True
            break
        if not committed:
            # Could not seat this slot without overlap; stop trying this index.
            continue
    return placed


def _place_road(spec, prefabs, rng, placed):
    """Line the buildings along a road axis with small perpendicular jitter."""
    cx, cy = spec.center
    bw, bh = spec.bounds
    axis_x = spec.road_axis == "x"
    along_half = bw if axis_x else bh
    n = spec.target_buildings

    # March a cursor along the road, alternating sides each step.
    margin = 256
    cursor = -along_half + margin
    placed_count = 0
    guard = 0
    while placed_count < n and cursor < along_half - margin and guard < n * 6:
        guard += 1
        committed = False
        for _ in range(MAX_TRIES_PER_BUILDING):
            prefab = _pick_prefab(prefabs, rng, spec.require_tags)
            w, h = prefab.footprint
            along_size = w if axis_x else h
            perp_size = h if axis_x else w
            side = 1 if placed_count % 2 == 0 else -1
            along = cursor + rng.uniform(-48, 48)
            # near edge sits road_offset from centerline -> box offset further out
            perp = side * (spec.road_offset + perp_size / 2) + rng.uniform(-32, 32)
            if axis_x:
                bxc, byc = cx + along, cy + perp
            else:
                bxc, byc = cx + perp, cy + along
            clamped = _clamp_box(bxc - w / 2, byc - h / 2, w, h, cx, cy, bw, bh)
            if clamped is None:
                continue
            x, y = clamped
            if spec.grid_snap:
                x, y = _snap(x, spec.grid_snap), _snap(y, spec.grid_snap)
            if any(_rects_overlap((x, y, w, h), q.box, spec.min_gap)
                   for q in placed):
                continue
            placed.append(Placement(prefab, x, y))
            placed_count += 1
            committed = True
            # advance cursor by roughly one building footprint along the axis
            cursor += along_size // 2 + spec.min_gap
            break
        if not committed:
            cursor += TILE  # nudge along and retry
    return placed


def plan_layout(spec: VillageSpec, prefabs, seed: Optional[int] = None):
    """Decide where buildings go. Deterministic for a given (spec.seed, prefabs).

    Returns (placements, shortfall) where shortfall = requested - placed.
    """
    if not prefabs:
        return [], spec.target_buildings
    rng = random.Random(spec.seed if seed is None else seed)
    placed: List[Placement] = []
    if spec.style == "road":
        _place_road(spec, prefabs, rng, placed)
    else:
        _place_cluster(spec, prefabs, rng, placed)
    shortfall = spec.target_buildings - len(placed)
    return placed, shortfall


# ===========================================================================
# Paths, plaza, ground, props
# ===========================================================================

def _path_item(spec, x, y):
    if spec.path_glob is not None:
        return MapItem.glob_egg(int(x), int(y), 0, spec.path_glob)
    return MapItem.placed_item(int(x), int(y), 0, spec.path_shape, spec.path_frame)


def _path_enabled(spec):
    return spec.path_glob is not None or spec.path_shape is not None


def _path_step(spec):
    return spec.chunk_size if spec.path_glob is not None else TILE


def _run(a, b, fixed, horizontal, step, emit):
    lo, hi = (a, b) if a <= b else (b, a)
    t = lo
    while t <= hi:
        emit(t, fixed) if horizontal else emit(fixed, t)
        t += step
    # guarantee the endpoint tile exists
    emit(hi, fixed) if horizontal else emit(fixed, hi)


def _l_path(x0, y0, x1, y1, step, emit):
    """L-shaped run: horizontal leg at y0, then vertical leg at x1."""
    _run(x0, x1, y0, True, step, emit)
    _run(y0, y1, x1, False, step, emit)


def _build_paths(spec, placements):
    """Connect every building's front to the plaza (cluster) or road (road)."""
    if not _path_enabled(spec):
        return []
    cx, cy = spec.center
    step = _path_step(spec)
    items: List[MapItem] = []
    emit = lambda x, y: items.append(_path_item(spec, x, y))
    axis_x = spec.road_axis == "x"

    if spec.style == "road":
        # Main road strip across the village along the chosen axis.
        bw, bh = spec.bounds
        if axis_x:
            _run(cx - bw, cx + bw, cy, True, step, emit)
        else:
            _run(cy - bh, cy + bh, cx, False, step, emit)
        # Spur from each building straight to the centerline.
        for p in placements:
            pcx, pcy = p.center
            target = (pcx, cy) if axis_x else (cx, pcy)
            ax, ay = _front_anchor(p, target)
            _l_path(ax, ay, target[0], target[1], step, emit)
    else:
        # Radial path from each building front into the plaza.
        for p in placements:
            ax, ay = _front_anchor(p, (cx, cy))
            _l_path(ax, ay, cx, cy, step, emit)

    return items


def _build_plaza(spec):
    """A small patch of path tiles at the village center (the plaza floor)."""
    if not _path_enabled(spec):
        return []
    cx, cy = spec.center
    step = _path_step(spec)
    span = 1 if spec.path_glob is not None else 2  # tiles each side of center
    items = []
    for ix in range(-span, span + 1):
        for iy in range(-span, span + 1):
            items.append(_path_item(spec, cx + ix * step, cy + iy * step))
    return items


def _build_ground(spec):
    """Tile the whole village rect with terrain glob eggs."""
    cx, cy = spec.center
    bw, bh = spec.bounds
    cs = spec.chunk_size
    x_start = cx - bw
    y_start = cy - bh
    x_chunks = max(1, math.ceil((2 * bw) / cs))
    y_chunks = max(1, math.ceil((2 * bh) / cs))
    grid = generate_terrain_grid(x_start, y_start, x_chunks, y_chunks,
                                 spec.ground_glob, cs)
    # generate_terrain_grid hardcodes egg z=0 (all base terrain is ground
    # level). Lift the whole grid to the village's datum so the ground and
    # the structures stamped onto it agree (H7).
    if spec.ground_z:
        for egg in grid:
            egg.z = spec.ground_z
    return grid


def _scatter_props(spec, props, placements, rng):
    """Place a 'well'-tagged prop at the plaza and scatter the rest near buildings."""
    if not props:
        return []
    cx, cy = spec.center
    items: List[MapItem] = []

    well = next((p for p in props if "well" in getattr(p, "tags", [])), None)
    others = [p for p in props if p is not well]

    if well is not None:
        w, h = well.footprint
        items.extend(well.stamp(cx - w // 2, cy - h // 2, spec.ground_z))

    if others and placements:
        n = min(len(placements), max(2, len(placements) // 2))
        targets = rng.sample(placements, n)
        for p in targets:
            prop = rng.choice(others)
            w, h = prop.footprint
            # drop it just outside a footprint corner, toward the plaza
            sx = -1 if p.center[0] > cx else 1
            sy = -1 if p.center[1] > cy else 1
            px = p.x + (p.w if sx > 0 else -w) - sx * 32
            py = p.y + (p.h if sy > 0 else -h) - sy * 32
            items.extend(prop.stamp(int(px), int(py), spec.ground_z))
    return items


# ===========================================================================
# Top-level assembly
# ===========================================================================

def generate_village(spec: VillageSpec, prefabs, props=None,
                     seed: Optional[int] = None) -> List[MapItem]:
    """Generate a complete village as a flat list[MapItem].

    Order (back-to-front friendly, though the renderer/engine re-sorts):
    ground -> plaza -> paths -> buildings -> props.
    Deterministic for a fixed (spec.seed, prefabs, props).
    """
    if seed is not None:
        spec.seed = seed
    rng = random.Random(spec.seed)
    # Advance the SAME rng used by plan_layout so prop scatter is downstream of
    # placement and stays reproducible.
    placements: List[Placement] = []
    if prefabs:
        if spec.style == "road":
            _place_road(spec, prefabs, rng, placements)
        else:
            _place_cluster(spec, prefabs, rng, placements)

    items: List[MapItem] = []
    items.extend(_build_ground(spec))
    items.extend(_build_plaza(spec))
    items.extend(_build_paths(spec, placements))
    for p in placements:
        # H7: z_base is the DESTINATION terrain height, not the prefab's own
        # origin_z. Passing origin_z made every relocation a no-op — a
        # BuildingPrefab kept its source z (a Map 37 prefab, origin_z=64,
        # would float 64 above ground here) and a GlobPrefab stacked its
        # datum on the egg. Both now ground on the village's own terrain.
        items.extend(p.prefab.stamp(p.x, p.y, spec.ground_z))
    items.extend(_scatter_props(spec, props or [], placements, rng))
    return items


# ===========================================================================
# Inline stub prefabs (self-test only; real prefabs come from sibling modules)
# ===========================================================================

class _StubBuilding:
    """A minimal Stampable: floor tiles + perimeter walls + door + roof.

    Renders as a recognizable little hut so the layout can be eyeballed.
    """

    def __init__(self, name, footprint, tags, roof_frame=2):
        self.name = name
        self.footprint = footprint
        self.tags = list(tags)
        self.origin_z = 0
        self.roof_frame = roof_frame

    def stamp(self, dest_x, dest_y, z_base=0):
        w, h = self.footprint
        wt = max(1, round(w / TILE))
        ht = max(1, round(h / TILE))
        items = []
        # Floor.
        for ix in range(wt):
            for iy in range(ht):
                items.append(MapItem.placed_item(
                    dest_x + ix * TILE, dest_y + iy * TILE, z_base, 3, 0))
        # Back walls (north + west edges).
        for ix in range(wt):
            items.append(MapItem.placed_item(
                dest_x + ix * TILE, dest_y, z_base, 145, 0))
        for iy in range(ht):
            items.append(MapItem.placed_item(
                dest_x, dest_y + iy * TILE, z_base, 145, 1))
        # Front (east) wall with a door at the south corner.
        for iy in range(ht):
            shape = 68 if iy == ht - 1 else 148
            items.append(MapItem.placed_item(
                dest_x + wt * TILE, dest_y + iy * TILE, z_base, shape, 0))
        # Roof, lifted to sit on top of the ~60px-tall walls.
        for ix in range(wt):
            for iy in range(ht):
                items.append(MapItem.placed_item(
                    dest_x + ix * TILE, dest_y + iy * TILE,
                    z_base + 30, 412, self.roof_frame))
        return items


def StubHut():
    return _StubBuilding("hut", (256, 256), ["hut", "home"], roof_frame=2)


def StubLonghouse():
    return _StubBuilding("longhouse", (384, 256), ["hut", "longhouse"],
                         roof_frame=5)


def StubHall():
    return _StubBuilding("hall", (384, 320), ["hall", "civic"], roof_frame=8)


class StubWell:
    """A plaza well: a water tile ringed by four short posts."""
    name = "well"
    footprint = (192, 192)
    tags = ["prop", "well"]
    origin_z = 0

    def stamp(self, dest_x, dest_y, z_base=0):
        items = [MapItem.placed_item(dest_x + 96, dest_y + 96, z_base, 347, 0)]
        for ox, oy in [(0, 0), (192, 0), (0, 192), (192, 192)]:
            items.append(MapItem.placed_item(
                dest_x + ox, dest_y + oy, z_base, 721, 0))
        return items


class StubCampfire:
    """A small prop: a single flame/torch shape."""
    name = "campfire"
    footprint = (64, 64)
    tags = ["prop", "campfire"]
    origin_z = 0

    def stamp(self, dest_x, dest_y, z_base=0):
        return [MapItem.placed_item(dest_x + 32, dest_y + 32, z_base, 295, 0)]


# ===========================================================================
# Self-test
# ===========================================================================

def _selftest():
    from iso_render import IsoRenderer

    prefabs = [StubHut(), StubLonghouse(), StubHall()]
    props = [StubWell(), StubCampfire()]
    renderer = IsoRenderer()
    results = []

    configs = [
        ("cluster", VillageSpec(
            center=(8192, 8192), bounds=(1792, 1792), target_buildings=7,
            style="cluster", ground_glob=43, seed=20260620,
            require_tags=["hut"], min_gap=128)),
        ("road", VillageSpec(
            center=(8192, 8192), bounds=(2304, 1280), target_buildings=6,
            style="road", road_axis="x", road_offset=320, ground_glob=43,
            seed=77, min_gap=128)),
    ]

    ok = True
    for style, spec in configs:
        items = generate_village(spec, prefabs, props)
        placements, shortfall = plan_layout(spec, prefabs)
        overlaps = check_overlaps(placements)
        if overlaps != 0:
            ok = False

        xs = [it.x for it in items]
        ys = [it.y for it in items]
        bounds = (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, 0, 0)

        out = f"/tmp/village_{style}.png"
        renderer.render(items, scale=2).save(out)
        results.append((style, spec, len(placements), shortfall, overlaps,
                        len(items), bounds, out))

    print("=" * 64)
    print("village_layout.py self-test")
    print("=" * 64)
    for (style, spec, placed, shortfall, overlaps, n_items,
         bounds, out) in results:
        print(f"\n[{style}]")
        print(f"  buildings placed/requested : {placed}/{spec.target_buildings}"
              f"  (shortfall {shortfall})")
        print(f"  total map items            : {n_items}")
        print(f"  footprint overlaps         : {overlaps}")
        print(f"  world bounds (minx,miny,maxx,maxy): {bounds}")
        print(f"  render                     : {out}")
        assert overlaps == 0, f"{style}: expected 0 overlaps, got {overlaps}"

    print("\nAll overlap assertions passed (0 overlaps each).")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_selftest())

"""
lv_landscape.py — the outdoor kit: cliff rims, worn tracks, and the 128-grid
they sit on. Lifted out of the Map 10 landscape pass (2026-09-15, cleanup
plan section 3) the way lv_furnish.py was lifted out of the temple.

What a cliff is, in this projection (Map 8, the Plateau, is the reference:
177 × 26 and 160 × 32 on a 128 stride, stacked in 48-unit courses, with
125 rock-top tiles one course above every run):

  * a run of 26 (long in x) along an east-west line, or 32 (long in y)
    along a north-south line, one piece per 128 units — 256 spacing is a
    50% hole, the picket-fence defect every LV map shipped with;
  * courses stacked at z = 0, 48, 96 … — one course reads as a wall, two
    as a cliff, and the courses rise with any terrain they flank;
  * a crest of 125 one course above the top, laid OUTSIDE the ground it
    rims, so the top reads as rock going back and nothing hangs over the
    walkable strip below it (a crest laid inward is a 96-high roof over
    three cells of ground, and the Avatar vanishes under it);
  * a 29 post in each convex corner, where two runs would leave a 32×32
    notch open.

Every tile here goes on the glob floor's own 128-grid (max corners ≡ 127
mod 128 — lv_furnish.floor_grid explains the -1), so nothing straddles two
floor tiles.
"""

from u8_map import MapItem
from lv_shapes import (
    SHAPE_CAVE_WALL_E, SHAPE_CAVE_WALL_S, SHAPE_CLIFF_TOP, SHAPE_CLIFF_CORNER,
    SHAPE_TRACK_COBBLE, SHAPE_BLOCKER_X, SHAPE_BLOCKER_Y,
)

CHUNK = 512
TILE = 128
# A zero-height tile laid over a glob floor is sorted by the flat rules
# (sort_item.cpp:145-181), and position never enters them before the flags
# do: an SI_DRAW flat "always gets drawn first" — under the floor — and so
# does an SI_OCCL one. The glob floors are SI_OCCL, so an overlay drawn on
# top must be a flat with NEITHER flag: 6, 71, 425, 783 (lv_shapes). 301
# and 386 carry SI_DRAW and vanished under the moss in-engine (2026-09-15).

SHAPE_CLIFF_X = SHAPE_CAVE_WALL_E     # 26: 4x1x6, a run along an east-west line
SHAPE_CLIFF_Y = SHAPE_CAVE_WALL_S     # 32: 1x4x6, a run along a north-south line
CLIFF_COURSE = 48
CLIFF_FRAMES = (0, 1, 2, 3, 4, 5, 6)  # 26/32: 7-8 are black, 26 f13 red, f14 capped
CREST_FRAMES = (0, 1, 2, 3, 4, 5, 6)  # 125: plain grey rock tops
TRACK_FRAMES = (2, 4, 6, 9, 11, 13, 15, 17, 19)    # 425: the brown-earth frames


def grid(v):
    """Snap a world coordinate to the glob floor's tile grid (max corner
    ≡ 127 mod 128), rounding down."""
    return (v // TILE) * TILE + TILE - 1


def _course_tops(top):
    z = 0
    while z < top:
        yield z
        z += CLIFF_COURSE


def crest_z(top):
    """The z the crest sits at over courses stacked while z < top."""
    z = 0
    while z < top:
        z += CLIFF_COURSE
    return z


def _flush_tops(base):
    """Courses that END at `base`: z = base - 48, base - 96 … >= 0. A face
    whose top is the ground it rims, so it hides nothing behind it."""
    return list(range(base - CLIFF_COURSE, -1, -CLIFF_COURSE))[::-1]


def _barrier_tops(base):
    """Two invisible courses on a flush face: 96 above the ground, more
    than the jump's climb72 reaches, and none of it ever drawn."""
    return [base, base + CLIFF_COURSE]


def cliff_run_x(items, x0, x1, y, top, phase=0, frames=CLIFF_FRAMES,
                zs=None, shape=SHAPE_CLIFF_X):
    """Courses of 26 covering x in (x0, x1] at max-corner y, from z=0 while
    z < top (or at exactly `zs`). The +y face of the run looks south."""
    for z in (zs if zs is not None else _course_tops(top)):
        for i, x in enumerate(range(x0 + TILE, x1 + 1, TILE)):
            items.append(MapItem.placed_item(
                x=x, y=y, z=z, shape=shape,
                frame=frames[(i + z // CLIFF_COURSE + phase) % len(frames)]))


def cliff_run_y(items, y0, y1, x, top, phase=0, frames=CLIFF_FRAMES,
                zs=None, shape=SHAPE_CLIFF_Y):
    """Courses of 32 covering y in (y0, y1] at max-corner x. The +x face of
    the run looks east."""
    for z in (zs if zs is not None else _course_tops(top)):
        for i, y in enumerate(range(y0 + TILE, y1 + 1, TILE)):
            items.append(MapItem.placed_item(
                x=x, y=y, z=z, shape=shape,
                frame=frames[(i + z // CLIFF_COURSE + phase) % len(frames)]))


def cliff_corner(items, x, y, top, zs=None):
    for z in (zs if zs is not None else _course_tops(top)):
        items.append(MapItem.placed_item(
            x=x, y=y, z=z, shape=SHAPE_CLIFF_CORNER,
            frame=CLIFF_FRAMES[(z // CLIFF_COURSE) % len(CLIFF_FRAMES)]))


def crest_tile(x, y, z):
    return MapItem.placed_item(
        x=x, y=y, z=z, shape=SHAPE_CLIFF_TOP,
        frame=CREST_FRAMES[(x // TILE + y // TILE) % len(CREST_FRAMES)])


def rim(chunks, courses=2, crest=True, flush=frozenset()):
    """Close a terrain footprint with cliffs.

    `chunks` is {(cx, cy): base_z} — every 512-unit chunk that has ground,
    with the z its ground sits at. Chunk (cx, cy) covers (512cx, 512cx+512]
    × (512cy, 512cy+512] in max-corner terms. Along every chunk edge whose
    neighbour is missing, `courses` courses of cliff are stacked from z=0
    to base_z + courses*48, placed in the void just beyond the edge so no
    walkable ground is lost and no flood ever meets them; convex corners
    get a post; the crest goes one course up, one tile beyond the wall.
    Missing neighbours INSIDE the footprint are rimmed too, so fill holes
    with ground unless a black pit is what you want.

    `flush` names edges, (cx, cy, 'south') or (cx, cy, 'east'), that must
    not stand above their ground. The camera looks from the south-east, so
    a south or east rim is drawn in FRONT of the ground it closes, and a
    face h units above that ground hides everything within about 8h of it
    in x+y: the vale's 96-high rim hides a body anywhere within ~770. On a
    flush edge the visible courses end at the ground (_flush_tops: the
    face drops away from the walker's feet, as a plateau's should) and two
    courses of retail's invisible wall stand on it (_barrier_tops), so it
    still cannot be walked or jumped off. No crest. A corner touching a
    flush edge gets the flush post; the 32x32 notch above it is out of a
    64-wide body's reach between the two barriers."""
    items = []
    crest_at = {}
    for (cx, cy), base in chunks.items():
        X0, Y0 = cx * CHUNK, cy * CHUNK
        top = base + courses * CLIFF_COURSE
        zc = crest_z(top)
        west = (cx - 1, cy) not in chunks
        east = (cx + 1, cy) not in chunks
        north = (cx, cy - 1) not in chunks
        south = (cx, cy + 1) not in chunks
        flat = {s for s in ('west', 'east', 'north', 'south')
                if (cx, cy, s) in flush}
        face = _flush_tops(base)
        bar = _barrier_tops(base)
        phase = cx * 3 + cy
        for side, on, run, a0, at, ph in (
                ('west', west, cliff_run_y, Y0, X0, phase),
                ('east', east, cliff_run_y, Y0, X0 + CHUNK + 32, phase + 2),
                ('north', north, cliff_run_x, X0, Y0, phase + 4),
                ('south', south, cliff_run_x, X0, Y0 + CHUNK + 32, phase + 6)):
            if not on:
                continue
            if side not in flat:
                run(items, a0, a0 + CHUNK, at, top, ph)
                continue
            run(items, a0, a0 + CHUNK, at, top, ph, zs=face)
            run(items, a0, a0 + CHUNK, at, top, frames=(0,), zs=bar,
                shape=SHAPE_BLOCKER_Y if run is cliff_run_y
                else SHAPE_BLOCKER_X)
        for a, b, x, y, sides in (
                (west, north, X0, Y0, {'west', 'north'}),
                (east, north, X0 + CHUNK + 32, Y0, {'east', 'north'}),
                (west, south, X0, Y0 + CHUNK + 32, {'west', 'south'}),
                (east, south, X0 + CHUNK + 32, Y0 + CHUNK + 32,
                 {'east', 'south'})):
            if a and b:
                cliff_corner(items, x, y, top,
                             zs=face if sides & flat else None)
        if not crest:
            continue
        xs = [X0 + TILE * k for k in range(1, 5)]
        ys = [Y0 + TILE * k for k in range(1, 5)]
        tiles = []
        if west and 'west' not in flat:
            tiles += [(X0, y) for y in ys]
        if east and 'east' not in flat:
            tiles += [(X0 + CHUNK + TILE, y) for y in ys]
        if north and 'north' not in flat:
            tiles += [(x, Y0) for x in xs]
        if south and 'south' not in flat:
            tiles += [(x, Y0 + CHUNK + TILE) for x in xs]
        for a, b, x, y, sides in (
                (west, north, X0, Y0, {'west', 'north'}),
                (east, north, X0 + CHUNK + TILE, Y0, {'east', 'north'}),
                (west, south, X0, Y0 + CHUNK + TILE, {'west', 'south'}),
                (east, south, X0 + CHUNK + TILE, Y0 + CHUNK + TILE,
                 {'east', 'south'})):
            if a and b and not sides & flat:
                tiles.append((x, y))
        for x, y in tiles:
            # a tile shared by two chunks' edges takes the higher crest
            crest_at[(x, y)] = max(crest_at.get((x, y), 0), zc)
    for (x, y), z in sorted(crest_at.items()):
        items.append(crest_tile(x, y, z))
    return items


def track(items, points, shape=SHAPE_TRACK_COBBLE, frames=TRACK_FRAMES, z=0,
          width=1):
    """A worn track: one tile per 128 units along the polyline `points`,
    snapped to the floor grid, diagonals as a staircase. `width` 2 lays a
    second lane beside the first (east of a north-south leg, south of an
    east-west one). Tiles are LAND with no height, so a track changes
    nothing a flood sees; it must still lie on ground, and the caller's
    build-time check proves that."""
    pts = [(grid(x), grid(y)) for x, y in points]
    cells = []
    seen = set()

    def put(x, y):
        if (x, y) not in seen:
            seen.add((x, y))
            cells.append((x, y))

    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay
        n = max(abs(dx), abs(dy)) // TILE
        for i in range(n + 1):
            t = i / n if n else 0.0
            x = ax + int(round(dx * t / TILE)) * TILE
            y = ay + int(round(dy * t / TILE)) * TILE
            put(x, y)
            if width > 1:
                if abs(dy) >= abs(dx):
                    put(x + TILE, y)
                else:
                    put(x, y + TILE)
    for x, y in cells:
        items.append(MapItem.placed_item(
            x=x, y=y, z=z, shape=shape,
            frame=frames[(x // TILE * 7 + y // TILE * 3) % len(frames)]))
    return cells


def tile_run(items, xs, ys, z, shape, frames):
    """Plain tiles over the columns `xs` × rows `ys` (max corners), frame
    by position so a rebuild is byte-identical. Over a glob floor at the
    floor's own z, `shape` must be one of the overlay flats (see the note
    at the top)."""
    for x in xs:
        for y in ys:
            items.append(MapItem.placed_item(
                x=x, y=y, z=z, shape=shape,
                frame=frames[(x // TILE * 5 + y // TILE * 3) % len(frames)]))


def span(a, b):
    """The floor-grid max corners of the tiles covering [a, b): for a chunk
    (a = 512c, b = a + 512) that is 512c+127 … 512c+511."""
    return list(range(grid(a), grid(b - 1) + 1, TILE))

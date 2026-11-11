#!/usr/bin/env python3
"""
lv_furnish.py — the furnishing kit the Lost Vale interiors are built from.

Lifted out of build_map_18.py on 2026-09-15 (cleanup plan Phase 0,
docs/reviews/2026-09-14-map-cleanup-plan.md §4) so the other builders
import it rather than copy it. Everything here was chosen off contact
sheets of what the base game's own interiors place and verified in-engine
on Map 18; agents/map-populator/docs/map-18-ancient-temple.md is the record.

The pieces:

  floor_grid(origin, k)           the 128-grid a glob floor's tiles land on
  raised_platform(xs, ys, z, …)   one tier of raised tiles with the edge
                                  faces this projection shows
  column(x, y, z=0)               plinth + plain shaft + crowned shaft
  accent_reliefs(items, lines)    carved-face frames on the visible wall
                                  faces, every fourth piece

and the constants the builders share: the flagstone glob, the platform
frames, the stone-wall pair and its plain/relief frames.

Two projection facts drive all of it. Screen x is (x - y)/4 and screen y
is (x + y)/8, so of any box only its +x face (screen lower-right) and +y
face (screen lower-left) can be seen; a room shows the inside face of its
north wall (a line of constant y, its +y face looking south into the room)
and of its west wall (constant x, +x face), and shows its east and south
walls their backs. And item positions are max corners with half-open
boxes — an item at (x, y) occupies (x - xd, x] × (y - yd, y] — which is
why a 128-unit tile at x occupies x-127..x and why the doorway runs in the
builders start on an odd coordinate.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from u8_map import MapItem                                   # noqa: E402
from lv_shapes import (                                      # noqa: E402
    SHAPE_SHADOW_PLATE,
    SHAPE_CAVE_BACKDROP_SMALL,
    SHAPE_CAVE_BACKDROP_LARGE,
    SHAPE_PLATFORM_FLAGSTONE,
    SHAPE_PAVING_RAISED,
    SHAPE_COLUMN_STONE,
    SHAPE_STONE_WALL_NS,
    SHAPE_GLOB_WALL_PIECE,
)

# ---------------------------------------------------------------------------
# Floors
# ---------------------------------------------------------------------------
# GLOB.FLX index (not a U8SHAPES.FLX shape id): sixteen shape-35 flagstones
# per chunk, frames 2/3, and nothing else. Glob 80 is the same floor with
# four wall pieces baked along the chunk's south edge — tiling it stamped
# the lattice Map 18 had until 2026-09-14. Floors come from this one and
# every wall is placed on purpose.
GLOB_FLAGSTONE_FLOOR = 65


def floor_grid(origin, k):
    """The k-th 128-grid line of a glob floor whose chunk origin (a multiple
    of 512) is `origin`. GlobEgg::enterFastArea lands a chunk's tiles at
    (egg & ~0x1FF) + 2*gx + 1, so for an egg at origin+511 the tiles' max
    corners sit on origin - 1 + 128k (measured 2026-09-14: x ≡ 1023, y ≡
    6143 mod 128 for the sanctum at (1024, 6144)). Anything laid over a
    floor goes on the same grid so no tile straddles two of the floor's."""
    return origin - 1 + 128 * k


# ---------------------------------------------------------------------------
# Raised platforms
# ---------------------------------------------------------------------------
# SHAPE_PLATFORM_FLAGSTONE (113) is the base game's raised-flagstone
# platform tile, 8 high, in the same stone as the shape-35 floor; its six
# frames carry the edge faces. A platform needs face frames on its east
# column and south row and a corner frame where they meet; every other
# tile's faces are hidden behind the tile in front of it, so the interior
# frame is only a texture choice.
PLAT_FRAME_INNER = 0        # interior / west column / north row
PLAT_FRAME_S = 0            # south row: +y face showing
PLAT_FRAME_E = 3            # east column: +x face showing
PLAT_FRAME_SE = 1           # south-east corner: both faces
TIER = 8                    # one platform tile is one step; STEP_Z is 24

FLAGSTONE_FRAMES = (PLAT_FRAME_INNER, PLAT_FRAME_S, PLAT_FRAME_E, PLAT_FRAME_SE)
# SHAPE_PAVING_RAISED (70) is the same kind of kit in a paler, rougher
# stone: frames 3/4/5 are the +y face, the +x face and the corner (frames
# 0-2 are its dark set). Map 18 tops its dais with it so the top tier reads
# as a different slab from the flagstone ring under it.
PAVING_FRAMES = (3, 3, 4, 5)


def raised_platform(xs, ys, z, shape=SHAPE_PLATFORM_FLAGSTONE,
                    frames=FLAGSTONE_FRAMES):
    """One tier of raised tiles over the tile columns `xs` and rows `ys`
    (both ascending, item max-corner coords), faces on the east and south
    edges. `frames` is (inner, south, east, south-east corner). Stack tiers
    at z, z + TIER, … — each is one 8-unit step, and a stack of three tops
    out at 24, the most a walking Avatar steps up."""
    inner, south_f, east_f, corner = frames
    items = []
    for x in xs:
        for y in ys:
            east, south = x == xs[-1], y == ys[-1]
            frame = (corner if east and south else
                     east_f if east else
                     south_f if south else inner)
            items.append(MapItem.placed_item(x=x, y=y, z=z, shape=shape,
                                             frame=frame))
    return items


# ---------------------------------------------------------------------------
# Columns
# ---------------------------------------------------------------------------
def column(x, y, z=0):
    """A temple column at max-corner (x, y) standing on a surface whose top
    is `z`: a raised-flagstone plinth with both faces showing, a plain shaft
    (249 frame 13, base and no capital) and the crowned shaft (frame 12) on
    top — 88 tall on a 128-unit foot. A single 40-tall column read
    in-engine as a fence post (2026-09-14); frames 0-5 are the outdoor set
    with grass at the foot. The plinth is centred under the shaft."""
    return [
        MapItem.placed_item(x=x + 48, y=y + 48, z=z,
                            shape=SHAPE_PLATFORM_FLAGSTONE, frame=PLAT_FRAME_SE),
        MapItem.placed_item(x=x, y=y, z=z + TIER, shape=SHAPE_COLUMN_STONE,
                            frame=13),
        MapItem.placed_item(x=x, y=y, z=z + TIER + 40,
                            shape=SHAPE_COLUMN_STONE, frame=12),
    ]


# ---------------------------------------------------------------------------
# Walls
# ---------------------------------------------------------------------------
# The base game's own stone-wall pair — 10 long in y (north-south runs,
# wall_run_y), 15 long in x (east-west runs, wall_run_x; the same piece
# glob 80 baked). 489/492, which every LV map used for walls until
# 2026-09-14, are wall ORNAMENTS (gargoyle caps, carved corners, barred
# windows) and read in-engine as rows of wall tops stacked on each other.
# Frame 1 is the plain course in both; the face reliefs are 10 f5 / 15 f0.
WALL_NS = SHAPE_STONE_WALL_NS
WALL_EW = SHAPE_GLOB_WALL_PIECE
WALL_PLAIN = 1
WALL_RELIEF = {WALL_NS: 5, WALL_EW: 0}


def accent_reliefs(items, lines, z=0, every=4, phase=2):
    """Set a carved face into every `every`-th ground-course piece of the
    walls whose inside face this projection shows.

    `lines` names them: ('y', 6143) is an east-west wall on that y whose
    +y face looks into the room south of it (a north wall); ('x', 1024) is
    a north-south wall on that x whose +x face looks into the room east of
    it (a west wall). East and south walls show the room their backs and
    are not listed. Only pieces at course `z` with the plain frame change.
    Deterministic by position, so a rebuild is byte-identical."""
    north = {c for axis, c in lines if axis == 'y'}
    west = {c for axis, c in lines if axis == 'x'}
    for it in items:
        if it.z != z or it.frame != WALL_PLAIN:
            continue
        if it.shape == WALL_EW and it.y in north and (it.x // 128) % every == phase:
            it.frame = WALL_RELIEF[WALL_EW]
        elif it.shape == WALL_NS and it.x in west and (it.y // 128) % every == phase:
            it.frame = WALL_RELIEF[WALL_NS]
    return items


# ---------------------------------------------------------------------------
# The void floor (2026-09-16)
# ---------------------------------------------------------------------------
# `Ultima8Engine::paint()` fills the frame black only when `_highRes` is set
# (ultima8.cpp:711, the `usehighres` config key). Without it, wherever no
# item paints — the void beyond a map's terrain — the previous frame's pixels
# stay on screen. Every LV map is a set of zones standing in void, and from
# the edge of any zone the view reaches 1,280 units past it on the x-y
# diagonal and 1,600 on x+y at the 640x400 canvas (half that at 320x200), so
# a player at a wall sees stale frames beyond it. Found on Map 17's cloud
# islands (docs/playtest-2026-09-15-cloud-tiles.md, finding 1).
#
# The fix is a floor: a pure-black 256-unit plate (shape 564 frame 2, the
# plate Map 8 flanks its paving with) under every 128-cell that is void and
# within view of a floor cell. The plate is SI_DRAW, which sorts UNDER every
# real floor at the same z (.claude/rules/map-geometry.md), so blocks may
# overlap real floors freely — the plate shows only where nothing else
# paints. `test_map_hygiene.py` counts the uncovered cells per map and
# ratchets them.
VIEW_RX = 1280 + 128        # |Δ(x - y)| the 640x400 canvas shows, plus a cell
VIEW_RY = 1600 + 256        # |Δ(x + y)|, plus the tallest tile
CELL = 128
VOID_PLATE = SHAPE_SHADOW_PLATE
VOID_PLATE_FRAME = 2        # the fully opaque black frame (4226 px of index 0)
VOID_PLATE_SPAN = 256       # its 8x8 footpad


def _cell(x, y):
    """The 128-grid cell (max corner, ≡ 127 mod 128) containing world (x, y)."""
    return ((x // CELL) * CELL + CELL - 1, (y // CELL) * CELL + CELL - 1)


SI_SEA, SI_LAND = 0x04, 0x08


BACKDROP_SHAPES = {SHAPE_CAVE_BACKDROP_SMALL, SHAPE_CAVE_BACKDROP_LARGE}


def floor_cells(items, shapes, eggs_as_chunks=True, painted=False):
    """The set of 128-cells that carry a floor: every placed LAND item of
    height 0 or 1 tile across its footpad — or, with `painted`, every LAND
    or SEA one and the decorative cave backdrops: water paints too, and what matters for the void is what
    paints, while what matters for the view is where a player stands. With
    `eggs_as_chunks`, for a list where globs are still eggs, every glob
    egg's sixteen (a floor glob covers its 512 chunk); a list with globs
    expanded passes False and counts the real tiles. `shapes` is the
    parsed TYPEFLAG (parse_typeflag.load_typeflag on the BUILT file)."""
    want = (SI_LAND | SI_SEA) if painted else SI_LAND
    cells = set()
    for it in items:
        if it.shape == MapItem.SHAPE_GLOB_EGG:
            if not eggs_as_chunks:
                continue
            ox, oy = it.x & ~0x1FF, it.y & ~0x1FF
            for k in range(4):
                for j in range(4):
                    cells.add((ox + CELL - 1 + CELL * k, oy + CELL - 1 + CELL * j))
            continue
        si = shapes[it.shape]
        paints = si.flags0 & want or (painted and it.shape in BACKDROP_SHAPES)
        if not paints or si.footpad_z > 1:       # a flat
            continue
        fx, fy = si.footpad_x * 32, si.footpad_y * 32
        for cx in range(it.x - fx + CELL, it.x + 1, CELL):
            for cy in range(it.y - fy + CELL, it.y + 1, CELL):
                cells.add(_cell(cx, cy))
    return cells


def cells_within_view(floors):
    """Every cell within the canvas's view of some floor cell, floors
    included: the dilation of `floors` by the view window in the rotated
    (x - y, x + y) frame."""
    seen = set(floors)
    r = max(VIEW_RX, VIEW_RY) // CELL + 1
    offsets = [(i, j) for i in range(-r, r + 1) for j in range(-r, r + 1)
               if abs(i - j) * CELL <= VIEW_RX and abs(i + j) * CELL <= VIEW_RY]
    # Only boundary cells (a missing 8-neighbour) need dilating: a void cell
    # within an interior cell's window lies within the window of the boundary
    # cell where the straight line to it leaves the floor, whose |Δ(x-y)| and
    # |Δ(x+y)| are both smaller. Map 10 has 26,000 floor cells; ~3,000 border.
    edge = [(cx, cy) for cx, cy in floors
            if any((cx + CELL * i, cy + CELL * j) not in floors
                   for i in (-1, 0, 1) for j in (-1, 0, 1) if i or j)]
    for cx, cy in edge:
        for i, j in offsets:
            x, y = cx + CELL * i, cy + CELL * j
            if x >= CELL - 1 and y >= CELL - 1:
                seen.add((x, y))
    return seen


def void_cells(items, shapes):
    """Cells within view of a REAL floor that nothing paints: what a player
    can see of the void. `items` must have its globs EXPANDED (the real
    tiles). The seed is the floors a player can stand on — the black plates
    are excluded from it, or the cover would breed its own outer ring
    forever — and the cover is everything that paints: land, water (Map
    10's lake is glob 55, sixteen SI_SEA tiles), and the plates."""
    real = [it for it in items if it.shape != VOID_PLATE]
    floors = floor_cells(real, shapes, eggs_as_chunks=False)
    cover = floor_cells(items, shapes, eggs_as_chunks=False, painted=True)
    return cells_within_view(floors) - cover


def void_floor(items, shapes=None):
    """Black plates under every void cell within view. One 256-unit plate
    per 2x2 block that holds at least one such cell; overlap with real floor
    is harmless (SI_DRAW sorts under it). Returns the plate items."""
    if shapes is None:
        from parse_typeflag import load_typeflag
        shapes = load_typeflag(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', '..', '..',
            'shared', 'build', 'TYPEFLAG.DAT'))
    # Expand the globs for real, as test_map_hygiene does: a chunk is not
    # always sixteen floor tiles (the lake glob is water, a cliff glob is
    # walls), and the count must be the same one the ratchet sees.
    from map_preview import GlobReader, expand_globs
    expanded = expand_globs(items, GlobReader())
    blocks = set()
    for cx, cy in void_cells(expanded, shapes):
        blocks.add(((cx // VOID_PLATE_SPAN) * VOID_PLATE_SPAN + VOID_PLATE_SPAN - 1,
                    (cy // VOID_PLATE_SPAN) * VOID_PLATE_SPAN + VOID_PLATE_SPAN - 1))
    return [MapItem.placed_item(x=bx, y=by, z=0, shape=VOID_PLATE,
                                frame=VOID_PLATE_FRAME)
            for bx, by in sorted(blocks)]

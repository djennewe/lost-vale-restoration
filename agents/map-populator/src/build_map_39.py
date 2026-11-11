#!/usr/bin/env python3
"""
build_map_39.py — Map 39 (Tenebrae) modification: quest step 1 trigger,
the Lord British message scene (shared/docs/wiring.md "Quest step 1:
LORDBRIT").

THE SITE — Tenebrae city-gate chokepoint (identified 2026-07-03,
RELOCATED same day after an in-game death):
Map 39 is Tenebrae's core (confirmed independently by two prior agents:
map-populator/docs/base-game-maps.md's "high container count suggests a
city/town map (likely Tenebrae)" note, and building_prefab.py's harder
citation — "Source maps surveyed: 39 (Tenebrae core — richest), 41
(Tenebrae), 40 (Tenebrae hub)").

PLACEMENT POST-MORTEM (2026-07-03): the first placement put the pair at
(17050,19100..19196,z=8) — INSIDE the gate's water channel. The "walled
courtyard" between the double wall lines (y≈19007 and y≈19455) is a moat:
its shape-347 frame-16 plates are WATER (the same 347 water frames the
validator's blackness rule exists for), the channel floor is cut down to
z=-120, and the "pure black floor" was read as a cosmetic issue and paved
over instead of recognized as water. A tester teleported there and
drowned without taking a step. Item/glob scans cannot see base-map
walkable ground reliably; the correction below comes from glob-expanded
data (shape-3 grass tiles, frames 26-28, in a 128-unit grid at
(17023-17279, 19583-20095), all at z=48) — the solid grass approach lane
in front of the SOUTH side of the gate, which matches the tester's
screenshot (grass on the near side of the arch, water beyond).

The pair now sits on that grass lane at z=48: anyone walking the lane to
or from the south gate crosses the egg's hatch box. No paving slab is
needed — the ground is real grass, not black-rendering water.

Debug teleport: MainActor::teleport 39 17150 20000 48
(lands on the grass lane south of the gate; walk toward the gate — screen
upper-right — to cross the hatch box and trigger the scene)

WHAT WE ADD:
  - 1x shape-73 UnkEgg (invisible trigger), quality = pinned EggLBScene
    class id (1455) - 0x47F = 304, npcnum = 0x44 (4x4 hatch range —
    DD-007a convention, VERIFIED IN-GAME 2026-07-03 by the DD-007 spike).
    Sits IN the archway gap so any route through the gate crosses its
    +/-128 unit hatch box.
  - 1x SHAPE_ROCK_SLAB_GROUND paving tile (z=1) under the apparition, so
    it doesn't read as floating in the courtyard's black shadow floor.
  - 1x shape-411 apparition item (frame 0, NO npcnum — a plain item
    placement, not npcnum-dispatched), ~3 tiles (96 units) further into
    the courtyard from the egg, clear line of sight through the open gate
    (nothing but pavement between them).

Both live quest-step-1 placements (this map + the build_map_08.py
backstop) rely on `lbStarted` to make duplicate eggs harmless — the first
one the Avatar reaches fires the scene once; any other placement (and any
save that already visited one) is inert forever after.

THE LANE FROM THE CITY (2026-10-09, docs/playtest-2026-10-09-full-run-1-18.md
finding 1). Until this date nobody could walk here. The "gate" above is not a
gate a citizen walks through: this field and the avenue east of it lie OUTSIDE
Tenebrae's walls, and every retail way out of the city is a teleport egg. The
survey, all on the built map with exact_reach's box arithmetic and the egg
hatcher's anchor boxes (egg_hatcher_process.cpp:68-85) masked:
  - the east wall (x 19456..19967) is two faces with a hollow between; the
    only way through it is the east gate passage (y 13952..14207), and the
    teleport egg to Map 40 at (19600,14072), range 0x94, covers it whole
    (anchor box x 19312..19951, y 13944..14263). That was the only route,
    and it ends on Map 40;
  - the main south gate (x 16896..17407) opens north onto the canal: a
    floorless strip, then water (347 at z 0) under a covered passage, with
    retail 565 plates at z 80..88 inside the arch (y 19296..19423) that
    block a body at z 48. The 498 rail (x 16384..16415) fences the city off
    from the canal basin;
  - the gate wall west of it (x 14976..16863, y 19456..19967) is a hollow
    block: north face, an empty interior floored only to y 19743, south face.
    Its three "doorways" (x 15008/15520/16032 ..+191) are blind niches whose
    back wall (y 19584..19615) is solid at z 48..88.
The two flood regions come closest (448 units, 4-connected) through those
niches and across the east wall. The lane takes the east niche, nearest the
egg: a 128-wide tunnel through the block (TENEBRAE_LANE_*), its floor two
pale slabs, its sides walled to the roof, and three retail bottom courses cut
from glob 742 (one back wall, two south face), the documented deviation in
BASE_ITEM_REMOVALS. No LV item stood in the block; the one LV obstruction on
the far side, the rock scatter's westmost rock, closed the field's mouth into
the gate lane from the west and was moved east. Phase 4 replaces it with TENEBRAE_LAWN_CLUMPS.
test_map39_lane.py asserts the walk from the Map 40 arrival pad (19130,14070)
and the city reaches the egg's own hatch box with every other trigger box
masked, and that masking the tunnel seals the city again.

THE SOUTH EDGE (found 2026-09-26, docs/playtest-2026-09-26-lamps-plaques-lb.md
Finding 3; re-measured 2026-10-03 against the glob-expanded BUILT FIXED.DAT
after review found the first treeline covered 576 units of a 6,400-unit edge):
the grass the egg/apparition stand on is real retail Tenebrae terrain, not
something we laid. Base-game shape-3 grass tiles (128-unit grid, z=48) run
from the retail wall line (every retail solid there ends at y=19967) south to
y=20479, and nothing exists south of that until an unrelated cluster at
y=21535+. Retail never needed a floor there because nothing routed a player
this far; the LB quest egg does, since its apparition (150 units south of the
egg) draws the Avatar onward, and a player who keeps walking drops 48 units
to the map's z=0 floor, in the black void the edge was never dressed for.

What a 64x40 body can actually reach, measured with exact_reach.ExactReach
(engine box arithmetic) from the egg with the void plates left out:
  - the south edge, body anchor x 14119..20503 at y 20511 (the grass edge is
    y=20479; the body's centre must leave grass before it falls);
  - the east face of the field, x=20479, body anchor y 20007..20511;
  - the avenue stub south of the field's NE corner: its south edge y=19967
    (anchor x 20519..21015) and its east edge x=20991 (anchor x 21023).
  - the retail platform's north end, x 14080..14335 at y=19327, where the
    platform meets nothing (closed by two fence panels under its roof slab).
West of x=14079 the platform drops 40 onto the gate pool's own stone rim
(retail shape 126, z 0..8).

THE FALLS (found in ScummVM 2026-10-03, docs/playtest-2026-10-03-batch-merge.md
C1). The walking flood above stops at an edge; the engine does not. A body
past an edge falls to the first top below it, and at z<=0 getPositionInfo
supports it anywhere (current_map.cpp:773), so z=0 is one floor under the
whole map. The verifier reached the black band under the apparition twice
that way: off the rim's south end (the platform drop, then an 8-unit step
down), and off the avenue's east edge. The lane is part of Tenebrae's whole
z=48 plateau, which has thousands of such drops; Douglas chose (2026-10-03)
to close the ones near the lane and pin the rest. Closed here:
  - the avenue's east edge from the stub north to y=17922 (six oaks,
    TENEBRAE_TREELINE_AVENUE);
  - the gate wall's three doorways and the main gate, whose 32-unit strip at
    y 19455..19487 has no floor (pale slabs, TENEBRAE_GATE_THRESHOLDS);
  - the harbour's two open ends, with wall courses copied from retail's own
    gate wall (TENEBRAE_HARBOUR_NORTH and _SOUTH);
  - the platform's north-west corner (TENEBRAE_PLATFORM_WEST_FENCE);
  - and, because the end walls turned a blocked step into a side step into
    the pool, a railing along the quay's water edge (TENEBRAE_QUAY_RAILING).
The platform's drop onto the rim stays: the harbour is now closed at both
ends, the pool is water, and a body on the rim can jump the 40 back up.

The south fix is one authored FOREST EDGE: 34 SHAPE_OAK_TREE (199, 288x288x80, the
only tall tree retail places, placed across maps 3/4/6/41) in
clumps and singles. Spacing is hand-set (trunk gaps vary, never a ruler) with
every neighbouring pair overlapping by at least 24 units in x and sitting
0..61 units apart in y, so the union is one connected blob and no x admits a
64-unit body between trunks; the base line wanders in y between 20386 and
20479. An L-shaped return runs up the east face and along the avenue stub.
Walk-through bushes (SHAPE_BUSH, FIX only, never solid) break up the row's
north face.

Why oaks alone: 80 units clears the engine's climb72 on jump from a z=48
lane (a solid top of 72 or less is a rung; 80 is not), so one course is
enough and nothing stacks. The edge is closed by oaks; bushes remain non-solid. Phase 4 replaces
the old spire scatter with bushes and keeps its garden fence and fungus clear
of the trees.
test_map39_south_edge.py asserts no solid with a top in [56, 128) within one
body width of any oak, and that no oak is buried in a solid.

Trees at the west end stand on the retail platform's 94 tiles (z 40..48,
solid), so those oaks rest exactly on a solid's top face, the geometry
map-geometry.md warns about for small carryables. It is a large static prop on
a plinth, the same stacking retail uses for its walls, but an in-engine look
for "Cycle in paint dependency graph" lines is still owed.

void_floor() then plates every void cell the barrier leaves in view south and
east of the field, computed from a LOCAL window of real base-Tenebrae context
so the fix does not re-patch retail Tenebrae's unrelated edges. It runs last.
"""

import sys
import os
import random
sys.path.insert(0, os.path.dirname(__file__))

from u8_map import MapItem, MapArchive
from base_input import pristine_base
from lv_dressing import Site, GRASS_FOREST
from parse_typeflag import load_typeflag
from lv_furnish import void_floor
from map_preview import GlobReader
from lv_shapes import (
    SHAPE_LB_EGG,
    SHAPE_LB_APPARITION,
    SHAPE_ROCK_SLAB_GROUND,
    SHAPE_OAK_TREE,
    SHAPE_BUSH,
    SHAPE_FENCE_X,
    SHAPE_FENCE_Y,
    SHAPE_SLAB_PALE,
    SHAPE_GLOB_WALL_PIECE,
    SHAPE_WALL_CAP_X,
    SHAPE_WALL_STUB_X,
    SHAPE_STONE_WALL_NS,
    SHAPE_STONE_WALL_NS_SHORT,
    SHAPE_WALL_CAP_Y,
    SHAPE_WALL_CAP_Y_SHORT,
    SHAPE_BLOCKER_X,
    SHAPE_BLOCKER_Y,
    SHAPE_CAVE_BACKDROP_SMALL,
    SHAPE_CAVE_BACKDROP_LARGE,
    SHAPE_WATER_SURFACE_SMALL,
)

# quality = pinned EggLBScene class id (shared/build/lv_manifest.json) - 0x47F
#         = 1455 - 1151 = 304
# EggLBScene::hatch() (agents/usecode-compiler/src/lv-new/LBSCENE.UNK) spawns
# TypeLordBritish::use(), which plays the full LB message scene.
LB_EGG_QUALITY = 304

# npcNum packs the hatch trigger box: x range = high nibble, y range = low
# nibble (Egg::getXRange/getYRange). 0x44 = 4x4 -> +/-128 unit box centered
# on the egg (same convention as the DD-007 spike in build_shape_gallery.py).
LB_EGG_NPCNUM = 0x44

# --- Tenebrae gate placement -------------------------------------------
# Grass approach lane south of the gate. Ground truth (glob-expanded scan
# 2026-07-03): shape-3 grass tiles, 128-unit grid, (17023-17279 x
# 19583-20095), all z=48. The gate arch is the wall line at y=19455; the
# moat channel (water, z-cut to -120) is NORTH of it — never place there.
TENEBRAE_EGG_X = 17150
TENEBRAE_EGG_Y = 19700
TENEBRAE_EGG_Z = 48

TENEBRAE_APPARITION_X = 17150
TENEBRAE_APPARITION_Y = 19850   # ~150 units farther from the gate, so the
                                 # ghost is visible ahead as the player
                                 # walks the lane; well inside the foreach
                                 # range (1024) of the egg.
TENEBRAE_APPARITION_Z = 48

# --- The field's south and east edges (found 2026-09-26, closed 2026-10-03)
# See the module docstring for the measured extent. Every number below is a
# hand-set world position; test_map39_south_edge.py checks the built result
# with the engine's box arithmetic, so a mistake here fails there.
TENEBRAE_EDGE_Z = 48          # the grass's own height, on the 4-unit lattice

# The south row, west to east. These are the collision anchors before the
# phase 4 southward offsets. The two oaks at x=17151 and 17439 are the
# 2026-10-01 pair, kept as members of the row. Neighbours overlap by 24..142
# units in x; y wanders between 20386 and 20479 (the grass edge).
TENEBRAE_TREELINE_SOUTH = (
    (14380, 20462), (14611, 20479), (14809, 20412), (15056, 20470),
    (15207, 20386), (15451, 20479), (15677, 20452), (15930, 20479),
    (16119, 20394), (16358, 20474), (16573, 20421), (16721, 20479),
    (16957, 20444), (17151, 20479), (17439, 20479), (17680, 20452),
    (17886, 20468), (18143, 20409), (18314, 20471), (18563, 20479),
    (18795, 20391), (19009, 20479), (19270, 20463), (19458, 20479),
    (19702, 20398), (19928, 20474), (20181, 20479), (20330, 20452),
    (20476, 20470),
)

# The retail platform's north end (x 14080..14335) also drops into void, at
# y=19327. A roof slab (shape 113, z 88..96) covers exactly that platform, so
# an oak is the wrong blocker there (its box would touch the slab and hand
# the climb rule a rung, top 96, 32 below the canopy). Two wooden fence
# panels (SHAPE_FENCE_X, 128x32x40, top 88) fit between the platform's top
# face (z 48) and the slab's underside (z 88): a body walking is stopped, and
# a body that jumps cannot stand on the top, because standing at z=88 would
# put it inside the slab. (x, y, frame)
TENEBRAE_NORTH_FENCE = (
    (14207, 19360, 0),
    (14335, 19360, 2),
)

# The return up the east face of the field (x=20479), the concave corner,
# and the avenue stub's south and east edges; each oak overlaps the one
# before it.
TENEBRAE_TREELINE_EAST = (
    (20452, 20232), (20479, 19990),    # east face, then the concave corner
    (20726, 19975), (20975, 19955),    # south edge of the avenue stub
    (21000, 19700),                    # its east edge, up to the field's
                                       # northern tile row (y 19455)
)

# Walk-through undergrowth on the row's north face: (x, y, frame). SHAPE_BUSH
# is FIX only, so it never blocks, never supports, and is never a rung.
TENEBRAE_BUSHES = (
    (14680, 20108, 0), (14744, 20140, 2), (14826, 20120, 1),
    (14796, 20087, 3),
    (15544, 20120, 3), (15620, 20156, 0), (15688, 20134, 3),
    (15736, 20089, 1),
    (18028, 20084, 0), (18096, 20122, 3), (18180, 20104, 2),
    (18132, 20083, 1),
    (19300, 20082, 2), (19372, 20002, 0), (19454, 19984, 3),
    (19396, 20064, 1),
    (20600, 20180, 1), (20676, 20226, 3), (20738, 20192, 0),
)

# The avenue's east edge (x=20991) north of the stub, up to y=17922: the
# drop there is 48 units onto z=0, and the engine supports ANY position at
# z<=0 (current_map.cpp:773), so a player who stepped off walked the black
# floor south to the band under the apparition (verified in ScummVM
# 2026-10-03, docs/playtest-2026-10-03-batch-merge.md C1). Each oak's box
# ends at or past x=20960, so a body cannot get its centre past x=20991,
# and each overlaps the next in y. (x, y)
TENEBRAE_TREELINE_AVENUE = (
    (20990, 19440), (20972, 19195), (21000, 18950),
    (20981, 18700), (20994, 18452), (20978, 18210),
)

# The gate wall's three doorways and the main gate leave a 32-unit strip,
# y 19455..19487, with no floor at z=48 between the city's grass and the
# field's. A body whose bottom centre is over it has no land under it and
# falls to z=0 (retail FIXED and the new-game NONFIXED place nothing there).
# A pale slab (no SI_DRAW, no SI_OCCL, so it overlays the grass) spans each
# doorway; two per doorway, because one 128 tile leaves a strip of the
# 192-unit opening a body can still centre over. (x, y)
# (2026-10-09: the three doorways are blind niches in a hollow block and the
# main gate opens onto the canal, so none of these joined the city to the
# field; the east pair, (16159..16223, 19519), now floors the mouth of the
# lane's tunnel, TENEBRAE_LANE_*.)
TENEBRAE_GATE_THRESHOLDS = (
    (15135, 19519), (15199, 19519),
    (15647, 19519), (15711, 19519),
    (16159, 19519), (16223, 19519),
    (17023, 19519), (17151, 19519), (17279, 19519), (17407, 19519),
)

# The harbour (gate pool x 13695..13951, its stone rims at z 0..8) runs from
# the gate wall south to y=20479 and is open at both ends: the platform drops
# 40 onto its east rim, and the rim walked off either end onto z=0. Two walls
# close it, built from the courses retail uses for the gate wall at x
# 13567..13823 (footing 670, two 15 courses, lintel 670, top 15), top z=136,
# out of climb72 reach from the platform (48) and the rim (8). The north wall
# fills the opening under the existing top course (x 13887..14079), and stops
# at z=88 where the retail roof slab 113 begins. (shape, frame, x, y, z)
#
# The z=48 course is shape 15 frame 0, not retail's frame 2. Frames 2 and 3
# are frames 0 and 1 with grass tufts painted along the base: right where
# retail's gate wall stands on the z=48 lawn, but here that course sits 40
# above the rim and the black band, and its tufts drew a green line across
# the middle of both walls (docs/playtest-2026-10-04-batch-retest.md C1f,
# finding 8). Frame 0 is the same large-block masonry without them.
TENEBRAE_HARBOUR_NORTH = (
    (SHAPE_WALL_STUB_X, 0, 13951, 19455, 8),
    (SHAPE_WALL_STUB_X, 0, 13951, 19455, 48),
    (SHAPE_WALL_CAP_X, 0, 14079, 19455, 0),
    (SHAPE_GLOB_WALL_PIECE, 1, 14079, 19455, 8),
    (SHAPE_GLOB_WALL_PIECE, 0, 14079, 19455, 48),
)
TENEBRAE_HARBOUR_SOUTH = tuple(
    piece
    for k, x in enumerate((13695, 13823, 13951, 14079))
    for piece in (
        (SHAPE_WALL_CAP_X, 0, x, 20511, 0),
        (SHAPE_GLOB_WALL_PIECE, 1, x, 20511, 8),
        (SHAPE_GLOB_WALL_PIECE, 0, x, 20511, 48),
        (SHAPE_WALL_CAP_X, 0, x, 20511, 88),
        (SHAPE_GLOB_WALL_PIECE, (1, 0, 1, 0)[k], x, 20511, 96),
    )
)

# A railing along the east rim's water edge, y 19455..20479. Walking into
# either harbour wall, the Avatar mover answers a blocked step with a side
# step (u8_avatar_mover_process.cpp:663-695), and on a 128-wide quay the
# side step to the west lands in the pool: in ScummVM he drowned twice
# walking north into the north wall (docs/playtest-2026-10-04-batch-retest.md
# C1d). Panels long in y (SHAPE_FENCE_Y, 32x128x40) on the rim's west 32
# units leave 96 to walk, and are SOLID only, so nothing stands on one.
# (x, y, frame)
TENEBRAE_QUAY_RAILING = tuple(
    (13983, 19583 + 128 * k, (1, 2, 3, 2, 1, 3, 2, 1)[k]) for k in range(8)
)

# The platform's north-west corner (94 at x 14079..14207, y 19327..19455)
# has void to its west, under the retail roof slab: the verifier's Avatar slid
# past the north fence's west end there. A fence panel long in y closes it;
# the slab at z=88 sits directly on its top, so nothing can stand there.
TENEBRAE_PLATFORM_WEST_FENCE = (14079, 19423, 1)

# --- The walking lane from the city (2026-10-09) --------------------------
# docs/playtest-2026-10-09-full-run-1-18.md finding 1: with the east gate's
# teleport box masked, nothing walks from the city to this field. The field
# and the avenue lie OUTSIDE Tenebrae's walls, and every retail way out is a
# teleport egg; the gate wall between the city and the field (y 19456..19967)
# is a hollow block whose three "doorways" are blind niches. The module
# docstring has the whole survey. The lane makes the east niche (x 16032..
# 16223) a real passage: a 128-wide tunnel through the block, built the way
# retail builds its own gate passages (the east gate is a 512-unit tunnel
# under the same z=136 roof plates).
#
# The three wall pieces in the way are inside GLOB 742, so, as on Map 8
# (build_map_08.BASE_ITEM_REMOVALS), the glob egg goes and its other items
# are re-placed by lane_glob_replacement(). THIS IS A DELIBERATE DEVIATION
# FROM RETAIL GEOMETRY: three bottom courses (z 48..88) of the wall are cut.
# The lintel and upper courses over each cut stay, so each opening keeps a
# lintel across it.
TENEBRAE_LANE_GLOB = (16383, 19967, 48, 742)        # (x, y, z, glob index)
TENEBRAE_LANE_CUT = (                                # (x, y, z, shape, frame)
    (16223, 19615, 48, SHAPE_GLOB_WALL_PIECE, 1),    # the niche's blind back
    (16127, 19967, 48, SHAPE_GLOB_WALL_PIECE, 3),    # the south face, x 16000..
    (16255, 19967, 48, SHAPE_GLOB_WALL_PIECE, 3),    # the south face, ..16255
)
# build_all_maps.py filters these raw base items out of Map 39 before adding
# ours: (x, y, z, shape), the same key build_map_08 uses.
BASE_ITEM_REMOVALS = {TENEBRAE_LANE_GLOB[:3] + (MapItem.SHAPE_GLOB_EGG,)}

# The tunnel's clear width is x 16096..16223 (128: a 64-unit body plus 64),
# from the niche (y 19584) to the field (y 19968). Retail floors the block
# only to y 19743, so two pale slabs (the doorway thresholds' paving) carry
# it to the field; SHAPE_SLAB_PALE is a flat with neither SI_DRAW nor
# SI_OCCL. (x, y), z = TENEBRAE_EDGE_Z.
TENEBRAE_LANE_FLOOR = ((16223, 19871), (16223, 19967))

# The hollow either side of the tunnel has no floor, and z=0 under it is a
# sealed box, so both sides are walled full height to the roof plates (z 136)
# the way retail walls a north-south run: a 10/8 course (48..88), a lintel
# (88..96), a 10/8 course (96..136). Nothing is a rung: every top up to 136
# has a course on it, and 136 is 88 above the floor, out of climb72. The east
# wall's upper course starts at y 19648, under retail's own 12 at 19616..
# 19647. (shape, frame, x, y, z)
TENEBRAE_LANE_WALLS = tuple(
    piece
    for wx in (16095, 16255)                         # west, east (max x)
    for piece in (
        (SHAPE_STONE_WALL_NS, 1, wx, 19743, 48),
        (SHAPE_STONE_WALL_NS, 1, wx, 19871, 48),
        (SHAPE_STONE_WALL_NS_SHORT, 0, wx, 19967, 48),
        (SHAPE_WALL_CAP_Y, 0, wx, 19743, 88),
        (SHAPE_WALL_CAP_Y_SHORT, 0, wx, 19839, 88),
        (SHAPE_WALL_CAP_Y_SHORT, 0, wx, 19935, 88),
        ((SHAPE_STONE_WALL_NS, 1, wx, 19743, 96) if wx == 16095 else
         (SHAPE_STONE_WALL_NS_SHORT, 0, wx, 19743, 96)),
        (SHAPE_STONE_WALL_NS_SHORT, 0, wx, 19839, 96),
        (SHAPE_STONE_WALL_NS_SHORT, 0, wx, 19935, 96),
    )
)
# The south cut is x 16000..16255, wider than the tunnel. West of the west
# wall it would leave a pocket exactly 64 wide (x 16000..16063) from the
# field into the hollow; half-open boxes let a body through an exact fit, so
# a stub (64x32x40, under the retail lintel) restores that much of the face.
TENEBRAE_LANE_STUB = (16063, 19967, 0)               # (x, y, frame), z = 48

# Edges of the city that are NOT closed, and why. Every one is a retail drop
# off Tenebrae's z=48 plateau that no retail route used and the Lord British
# scene does not route a player to; test_map39_south_edge.py pins how many
# there are and where, so a new drop near the lane fails the estate.
#   - the avenue's east edge north of y=17922 (retail, map-long);
#   - the city's other borders and interior drops, all north of the gate
#     wall or west of x=13700.
TENEBRAE_OPEN_EDGES = (
    'avenue east edge x=20991, y < 17922 (retail, map-long)',
    'city borders and interior drops north of the gate wall (retail)',
)

# The rock-spire scatter: (x, y, frame), varied frames so nothing repeats in
# a row, kept CLEAR of every tree, not tucked against them.
#
# Correction (2026-10-01, caught in verification before this shipped): an
# earlier draft placed these touching the trunks, reasoning shape 66's
# missing SI_LAND made it unusable as a climb step. That is wrong:
# exact_reach.py's getPositionInfo model supports standing on SOLID alone,
# and a climb-reach check found a real two-hop chain through the touching
# placement (lane 48 to rock top 88 to tree top 128, each hop inside
# climb72). Adjacency is what matters, so these sit 181+ units north of every
# tree's near edge and clear of the retail wall structure (x up to 16895,
# y up to 19967).
#
# Moved (2026-10-09): the first rock stood at (17060, 19950), where it and
# its neighbours closed the field's mouth into the gate lane from the west,
# the side the city lane now arrives from: 37 units from the wall face, 32
# between rocks, every gap narrower than a body. It now stands east of the
# row, 133 units clear of the last rock, so the walk from the tunnel runs
# straight up to the apparition.
# Four former spire sites become irregular three-bush islands. The second
# sits south of its old anchor to keep the apparition's clear box open.
TENEBRAE_LAWN_CLUMPS = (
    (17770, 19872, 2), (17834, 19910, 0), (17898, 19889, 3),
    (17184, 20088, 1), (17256, 20096, 3), (17310, 20073, 0),
    (17366, 19930, 0), (17430, 19966, 2), (17394, 20012, 1),
    (17520, 19986, 3), (17592, 20026, 1), (17658, 20002, 2),
)

# An abandoned timber garden boundary: the bed curves around its east
# end, then thins into mushrooms toward the wood.
# Every anchor is authored here and retains its explicit coordinates.
WALL_GARDEN = (
    (SHAPE_FENCE_X, 7, 18508, 19820),
    (SHAPE_FENCE_Y, 7, 18380, 19820),
    (434, 2, 18328, 19884), (434, 0, 18398, 19936),
    (434, 3, 18576, 19932), (434, 1, 18648, 19888),
    (434, 0, 18712, 19944), (434, 2, 18764, 20002),
    (65, 1, 19070, 19920), (65, 3, 19160, 19960),
    (465, 2, 18470, 19992), (465, 7, 18506, 20018),
    (465, 11, 18554, 19996),
)


# Four unequal triangular copses beyond the barrier give the edge depth.
# Their branches overlap in the image; their collision boxes stay separate.
SOUTH_WOOD_COPSES = (
    (14880, 20930), (15206, 21014), (15032, 21350),
    (16168, 20912), (16520, 21010), (16332, 21340),
    (18040, 20886), (18390, 21002), (18200, 21316),
    (19620, 20910), (19958, 21038), (19780, 21374),
)


def dress_lane(items):
    """Validate dressing against the complete retail map and retain its prefix."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    path = pristine_base(os.path.join(root, 'shared/data/u8-install/STATIC/FIXED.DAT'),
                         what='FIXED.DAT base (map 39 dressing)')
    retail = [i for i in MapArchive(path).get_map_items(39)
              if (i.x, i.y, i.z, i.shape) not in BASE_ITEM_REMOVALS]
    assert len(retail) == 4623
    shapes = load_typeflag(os.path.join(root, 'shared/build/TYPEFLAG.DAT'))
    site = Site(39, retail + items, shapes, seed=3904)
    inherited = {id(i) for i in site.items}
    site.set_piece('The swallowed garden fence', [
        MapItem.placed_item(x, y, TENEBRAE_EDGE_Z, shape, frame)
        for shape, frame, x, y in WALL_GARDEN])
    site.set_piece('Lawn thickets', [
        MapItem.placed_item(x, y, TENEBRAE_EDGE_Z, SHAPE_BUSH, frame)
        for x, y, frame in TENEBRAE_BUSHES + TENEBRAE_LAWN_CLUMPS])
    # The shared guard currently rejects five forest family members for
    # internal solid overlap or top faces. An empty batch retains plain grass.
    site.swap_chunks(plain=1, family=GRASS_FOREST, share=.5,
                     where=(12900, 20479, 22900, 22400))
    site.set_piece('South wood copses', [
        MapItem.placed_item(x, y, TENEBRAE_EDGE_Z, SHAPE_OAK_TREE, 0)
        for x, y in SOUTH_WOOD_COPSES])
    # Protect inherited geometry from packing, including the clipped harbour
    # strips. pack() still records every new piece for built-map auditing.
    site.protected_raw.update(inherited)
    return site.pack()[len(retail):]


# How far around the site to pull real base-Tenebrae context from, for the
# void_floor() view computation below. void_floor()'s own view dilation
# (.claude/rules/map-geometry.md: ~1280-1600 units each way) treats
# whatever real floor falls OUTSIDE this window as void too, since a window edge
# looks exactly like a map edge to that algorithm, so the window is padded
# well past the view radius in every direction; ACCEPT_X/ACCEPT_Y below
# then keeps only the plates actually near the barrier, discarding the
# false "void" the padded window's own far edges generate. That keeps the
# fix scoped to this one defect rather than re-patching retail Tenebrae's
# unrelated edges elsewhere on a 256x256-chunk city map.
_CONTEXT_X = (12800, 21500)
_CONTEXT_Y = (15800, 24200)

# The only region a void plate is accepted from: the band south of the south
# edge, plus the void east of the avenue stub down to the corner. A plate is
# black and sorts under every real floor, so a generous window costs nothing
# visible; the window only keeps the padded context's own far edges from
# adding plates under unrelated retail Tenebrae.
_ACCEPT_SOUTH_X = (12900, 22900)
_ACCEPT_SOUTH_Y = (20479, 22400)
_ACCEPT_EAST_X = (20400, 22900)
_ACCEPT_EAST_Y = (18200, 22400)


def _accepted(p):
    return ((_ACCEPT_SOUTH_X[0] <= p.x <= _ACCEPT_SOUTH_X[1]
             and _ACCEPT_SOUTH_Y[0] <= p.y <= _ACCEPT_SOUTH_Y[1])
            or (_ACCEPT_EAST_X[0] <= p.x <= _ACCEPT_EAST_X[1]
                and _ACCEPT_EAST_Y[0] <= p.y <= _ACCEPT_EAST_Y[1]))


def _base_map_39_context():
    """Real (pristine) base-game Map 39 items near the gate/lane, for
    void_floor()'s view computation only, never returned as part of the
    additions (build_all_maps.py already owns adding the real base map).
    Glob eggs are left unexpanded; void_floor() expands them itself, same
    as every from-scratch builder's own void_floor(items) call."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    base_fixed = os.path.join(base_dir, "shared", "data", "u8-install",
                              "STATIC", "FIXED.DAT")
    base_path = pristine_base(base_fixed, what='FIXED.DAT base (map 39 context)')
    all_items = MapArchive(base_path).get_map_items(39)
    return [it for it in all_items
            if _CONTEXT_X[0] <= it.x <= _CONTEXT_X[1]
            and _CONTEXT_Y[0] <= it.y <= _CONTEXT_Y[1]
            and (it.x, it.y, it.z, it.shape) not in BASE_ITEM_REMOVALS]


def lane_surface(item):
    """Retain collision exactly and paint the tunnel ceiling below actors.

    Roof plates retain their solid support at the original height.
    The remaining wall and trim surfaces retain their retail records.
    """
    if item.shape in (564, 35) and item.z == 136:
        large = item.shape == 564
        return [MapItem.placed_item(
                    x=item.x, y=item.y, z=item.z,
                    shape=499 if large else 763, frame=0),
                MapItem.placed_item(
                    x=item.x - 4 * item.z, y=item.y - 4 * item.z, z=0,
                    shape=SHAPE_CAVE_BACKDROP_LARGE if large else SHAPE_CAVE_BACKDROP_SMALL, frame=0)]
    return [item]


def lane_glob_replacement():
    """Glob 742's items at the east niche, minus TENEBRAE_LANE_CUT, as plain
    FIXED items (a glob is all-or-nothing; build_map_08 does the same).
    Expanded from the player's own GLOB.FLX rather than copied into this
    file; the cut must match exactly, so a different glob fails here."""
    gx, gy, gz, index = TENEBRAE_LANE_GLOB
    glob = GlobReader().glob_to_items(index, gx, gy, gz)
    cut = set(TENEBRAE_LANE_CUT)
    found = {(it.x, it.y, it.z, it.shape, it.frame) for it in glob} & cut
    if found != cut:
        raise RuntimeError(
            f'glob {index} at ({gx},{gy},{gz}) does not carry the lane cut: '
            f'missing {sorted(cut - found)}')
    return [piece for it in glob
            if (it.x, it.y, it.z, it.shape, it.frame) not in cut
            for piece in lane_surface(MapItem.placed_item(
                x=it.x, y=it.y, z=it.z, shape=it.shape, frame=it.frame))]


def lane_additions():
    """The tunnel through the gate wall: the re-placed glob, its floor, its
    two side walls and the stub that closes the south cut's west pocket."""
    items = lane_glob_replacement()
    for (fx, fy) in TENEBRAE_LANE_FLOOR:
        items.append(MapItem.placed_item(
            x=fx, y=fy, z=TENEBRAE_EDGE_Z, shape=SHAPE_SLAB_PALE, frame=0))
    for (shp, fr, wx, wy, wz) in TENEBRAE_LANE_WALLS:
        items.append(MapItem.placed_item(x=wx, y=wy, z=wz, shape=shp, frame=fr))
    sx, sy, sfr = TENEBRAE_LANE_STUB
    items.append(MapItem.placed_item(
        x=sx, y=sy, z=TENEBRAE_EDGE_Z, shape=SHAPE_WALL_STUB_X, frame=sfr))
    # Merge the lintel's 8 units and the upper course's 40 into one
    # 48-unit editor wall. Its top stays 136, preserving climb clearance.
    south_x = (16127, 16255)
    visible = []
    for it in items:
        south = (it.y == 19967 and it.x in south_x
                 and (it.shape, it.z) in ((15, 96), (670, 88)))
        east = (it.x == 16255 and 19616 <= it.y <= 19967
                and it.shape in (8, 10, 692, 726))
        if south:
            if it.shape == 15:
                visible.append(MapItem.placed_item(
                    x=it.x, y=it.y, z=88, shape=SHAPE_BLOCKER_X))
                # Two overlapping diamonds cover the wall's tall face.
                for offset in (0, 64):
                    visible.append(MapItem.placed_item(
                        x=it.x - 4 * it.z - offset,
                        y=it.y - 4 * it.z - offset,
                        z=0, shape=SHAPE_CAVE_BACKDROP_LARGE, frame=0))
        elif not east:
            visible.append(it)
    # The short final piece overlaps the preceding run by 32 units. The
    # original east wall and the south face already occupy that union.
    for y in (19743, 19871, 19967):
        for z in (48, 88):
            visible.append(MapItem.placed_item(x=16255, y=y, z=z, shape=SHAPE_BLOCKER_Y))
    return visible


def tenebrae_skirt(plates):
    """Continue Tenebrae grass beyond the closed oak line and the channel.

    Full grass chunks cost one egg each. The two harbour columns use the
    glob's individual tiles so grass stays clear of the lower water and quay.
    """
    chunks = sorted({(p.x // 512, p.y // 512) for p in plates})
    items = []
    globs = GlobReader()
    for cx, cy in chunks:
        x, y = cx * 512 + 511, cy * 512 + 511
        if cx in (26, 27) and cy >= 40:
            items.extend(i for i in globs.glob_to_items(1, x, y, TENEBRAE_EDGE_Z)
                         if i.x < 13568 or i.x > 14079)
        else:
            items.append(MapItem.glob_egg(x, y, TENEBRAE_EDGE_Z, 1))
    # The channel continues below the closed south wall at retail water z.
    # The stone strip paints its bank without supplying a standing level.
    for y in range(20639, _ACCEPT_SOUTH_Y[1], 128):
        for x in (13695, 13823, 13951):
            items.append(MapItem.placed_item(
                x=x, y=y, z=0, shape=SHAPE_WATER_SURFACE_SMALL, frame=16))
        items.append(MapItem.placed_item(
            x=14079, y=y, z=0, shape=SHAPE_CAVE_BACKDROP_SMALL, frame=0))
    for x in (13695, 13823, 13951, 14079):
        items.append(MapItem.placed_item(
            x=x, y=20511, z=0, shape=SHAPE_CAVE_BACKDROP_SMALL, frame=0))
    return items


def build_map_39_additions():
    """Return list of MapItem additions for Map 39 (Tenebrae)."""
    items = []

    # 1. The trigger egg, in the middle of the grass approach lane. Its
    #    +/-128 hatch box (npcnum 0x44) spans the lane width in front of
    #    the south gate.
    items.append(MapItem(
        x=TENEBRAE_EGG_X, y=TENEBRAE_EGG_Y, z=TENEBRAE_EGG_Z,
        shape=SHAPE_LB_EGG, frame=0,
        quality=LB_EGG_QUALITY, npcnum=LB_EGG_NPCNUM
    ))

    # 2. The apparition — plain item placement, NO npcnum (avoid npcnum
    #    dispatch; shape 411's TYPEFLAG family is SF_CONTAINER, so an
    #    npcnum here would risk accidental engine behavior on top of the
    #    sprite already being a placeholder). Stands on real grass (z=48
    #    ground) — no paving slab needed.
    items.append(MapItem.placed_item(
        x=TENEBRAE_APPARITION_X, y=TENEBRAE_APPARITION_Y, z=TENEBRAE_APPARITION_Z,
        shape=SHAPE_LB_APPARITION, frame=0, quality=0
    ))

    # 3. The forest edge: oaks along the south edge, returning up the east
    #    face and along the avenue stub (module docstring, TENEBRAE_TREELINE_*).
    #    All at z=48; the grass under them is zd=0 and never blocks. Closes
    #    the 48-unit drop into void found 2026-09-26.
    for (tx, ty) in TENEBRAE_TREELINE_SOUTH + TENEBRAE_TREELINE_EAST:
        items.append(MapItem.placed_item(
            x=tx, y=(max(ty, 20479 - random.Random(f"39:oak:{tx}").randrange(94))
                      if (tx, ty) in TENEBRAE_TREELINE_SOUTH else ty),
            z=TENEBRAE_EDGE_Z, shape=SHAPE_OAK_TREE, frame=0
        ))

    # 3b. The platform's north end: two fence panels under the roof slab,
    #     and one along its north-west corner's west face.
    for (fx, fy, ffr) in TENEBRAE_NORTH_FENCE:
        items.append(MapItem.placed_item(
            x=fx, y=fy, z=TENEBRAE_EDGE_Z, shape=SHAPE_FENCE_X, frame=ffr
        ))
    wx, wy, wfr = TENEBRAE_PLATFORM_WEST_FENCE
    items.append(MapItem.placed_item(
        x=wx, y=wy, z=TENEBRAE_EDGE_Z, shape=SHAPE_FENCE_Y, frame=wfr
    ))

    # 3c. The avenue's east edge, north of the stub.
    for (tx, ty) in TENEBRAE_TREELINE_AVENUE:
        items.append(MapItem.placed_item(
            x=tx, y=ty, z=TENEBRAE_EDGE_Z, shape=SHAPE_OAK_TREE, frame=0
        ))

    # 3d. Thresholds in the gate wall's doorways.
    for (sx, sy) in TENEBRAE_GATE_THRESHOLDS:
        items.append(MapItem.placed_item(
            x=sx, y=sy, z=TENEBRAE_EDGE_Z, shape=SHAPE_SLAB_PALE, frame=0
        ))

    # 3e. The harbour's two end walls, and the railing on its east quay.
    for (shp, fr, hx, hy, hz) in TENEBRAE_HARBOUR_NORTH + TENEBRAE_HARBOUR_SOUTH:
        items.append(MapItem.placed_item(
            x=hx, y=hy, z=hz, shape=shp, frame=fr
        ))
    for (rx, ry, rfr) in TENEBRAE_QUAY_RAILING:
        items.append(MapItem.placed_item(
            x=rx, y=ry, z=8, shape=SHAPE_FENCE_Y, frame=rfr
        ))

    # 3f. The lane from the city: the tunnel through the east niche.
    items.extend(lane_additions())

    # Infer the visible skirt from the original accepted void coverage.
    # Retain the scoped cover calculation after adding grass and channel paint.
    base = _base_map_39_context()
    initial = [p for p in void_floor(base + items) if _accepted(p)]
    items.extend(tenebrae_skirt(initial))
    items = dress_lane(items)
    items.extend(p for p in void_floor(base + items) if _accepted(p))

    return items


# --- TEST-ONLY: new-game start area (Map 3) ------------------------------
# Avatar's new-game spawn (read directly from the retail
# SAVEGAME/U8SAVE.000 ITEMCACH.DAT NPC slot 1 — see scan_npc_slots.py for
# the offset table): shape=1 frame=185 at (14527, 5887, 8) on MAP 3.
# Default OFF — never ships in a release build (fires the post-mid-game
# hook at minute one of a fresh game). Enable with the module constant
# below or `--lb-test-egg` on build_all_maps.py.
LB_TEST_EGG_AT_START = False

LB_TEST_EGG_X = 14527
LB_TEST_EGG_Y = 5987   # 100 units south of the Avatar's exact spawn point
                        # (14527,5887) so it doesn't share the Avatar's own
                        # starting tile.
LB_TEST_EGG_Z = 8

LB_TEST_APPARITION_X = 14527
LB_TEST_APPARITION_Y = 6083   # ~96 units further south of the test egg
LB_TEST_APPARITION_Z = 8


def build_map_03_test_additions():
    """TEST-ONLY: same egg+apparition pair at the new-game start area
    (Map 3), for quick fresh-game verification runs. Only called by
    build_all_maps.py when LB_TEST_EGG_AT_START is True or --lb-test-egg
    is passed on the command line — never in a normal build."""
    items = []

    items.append(MapItem(
        x=LB_TEST_EGG_X, y=LB_TEST_EGG_Y, z=LB_TEST_EGG_Z,
        shape=SHAPE_LB_EGG, frame=0,
        quality=LB_EGG_QUALITY, npcnum=LB_EGG_NPCNUM
    ))
    items.append(MapItem.placed_item(
        x=LB_TEST_APPARITION_X, y=LB_TEST_APPARITION_Y, z=1,
        shape=SHAPE_ROCK_SLAB_GROUND, frame=0, quality=0
    ))
    items.append(MapItem.placed_item(
        x=LB_TEST_APPARITION_X, y=LB_TEST_APPARITION_Y, z=LB_TEST_APPARITION_Z,
        shape=SHAPE_LB_APPARITION, frame=0, quality=0
    ))

    return items


if __name__ == '__main__':
    items = build_map_39_additions()
    print(f"Map 39 (Tenebrae) additions: {len(items)} items")
    for item in items:
        print(f"  {item}")

    print()
    print(f"Map 3 TEST additions (LB_TEST_EGG_AT_START={LB_TEST_EGG_AT_START}):")
    test_items = build_map_03_test_additions()
    for item in test_items:
        print(f"  {item}")

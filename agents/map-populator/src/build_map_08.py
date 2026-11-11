#!/usr/bin/env python3
"""
build_map_08.py — Map 8 Plateau modification: THE Lost Vale Double Doors.

Restores the famous sealed doors in the Bonecrusher-cave doorway at
(20191..20703, 2751) — the retail game's "doors that cannot be opened"
(Ultima Codex) — as functional locked doors, and stages the LV entry
around them.

THE SITE (all base-game, verified against retail FIXED.DAT 2026-07-02):
  - Two blank shape-619 monoliths (256x96 featureless black slabs, no
    usecode, nothing behind) fill a 512-unit doorway at y=2751, z=0 —
    these ARE the famous sealed doors. Removed via BASE_ITEM_REMOVALS.
  - A paved rock-slab walk (shape 301) approaches from the south through
    a colonnade of tall stalagmite pillars (shape 394) — the retail game
    already dressed the approach.
  - The whole area is a roofed cave (ceiling plates at z=96) with black
    shadow-floor plates (564 frame 2) flanking the paving.

WHAT WE ADD (docstring corrected 2026-07-31 — an earlier draft here
claimed we place four door leaves and flanking rock spires; we place
NEITHER. The two shape-342 leaves are RETAIL items seeded from
U8SAVE.000 — see DOOR_LOCK_ID below, "we just cut the key"):
  - Key (82, "key blank") + chest (78, "chest") on the paved approach.
  - Teleport trigger 200 -> Map 9 hidden in the black interior pocket
    behind the doors; dests 201/212 in the niche west of the doorway and
    the return to Map 10 (id 212, an EggValeReturn usecode egg that
    teleports only once the Vale is open) on a pale slab in the open
    south-east of the bone chamber (+ paving slab at 200).
  - The LORDBRIT backstop egg + apparition pair on the Mythran approach.

HOW THE DOORS OPEN (the full recipe lives in
docs/map-08-plateau-entry.md): double-click the KEY -> target cursor ->
click the leaf. A locked leaf's own use()/look barks "Locked Door" at
the top viewport edge. A wandering base-game ghost (shape 411, solid)
can transiently block the doorway -- the leaf barks "blocked" until it
moves; retail-correct, not fixable from FIXED.DAT.

Debug teleport: MainActor::teleport 8 20430 3250 0
(outer bone chamber, at the wall gap facing the doors)

Site history — earlier failed placements, all superseded by finding the
REAL retail doorway:
  1. (2560,1536,8)    — Mythran-house cluster, wrong area entirely.
  2. (14540,8000,48)  — top of a corridor wall ridge (z=48 is wall top).
  3. corridor x=14591 — real floor, but its own east wall hides the whole
                        interior from the fixed SE camera.
  4. (15680,7720)     — invented "roofed pocket" site; worked, but the
                        authentic sealed doorway at (20447,2751) is where
                        the 1994 design put the doors.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from u8_map import MapItem
from lv_shapes import (
    SHAPE_KEY,
    SHAPE_CHEST,
    SHAPE_ROCK_SLAB_GROUND,
    SHAPE_CAVE_BACKDROP_SMALL,
    SHAPE_CAVE_BACKDROP_LARGE,
    SHAPE_SLAB_PALE,
    SHAPE_LB_EGG,
    SHAPE_LB_APPARITION,
    SHAPE_PLACEHOLDER_INVISIBLE_EGG,
)
from build_map_39 import LB_EGG_QUALITY, LB_EGG_NPCNUM


# Lock ID 99 = the REAL retail doors' lock (see below).
#
# THE DEFINITIVE DOOR FINDING (2026-07-02, via live engine dump): the
# famous sealed Lost Vale doors are DYNAMIC items seeded from the
# new-game template SAVEGAME/U8SAVE.000 (NOT in FIXED.DAT, NOT in any
# glob — which is why every static scan missed them):
#   shape 342 frame 0, quality 0x663, at (20351,3071)  west leaf
#   shape 342 frame 1, quality 0x463, at (20479,3071)  east leaf
# Quality encoding: low byte = lock ID (0x63 = 99), 0x400 = LOCKED,
# 0x100 = open, 0x200 = unknown (west leaf only). They are unopenable in
# retail simply because NO quality-99 key exists in the shipped game —
# but the shipped keyring usecode whitelists shape 342, so a q=99 key
# unlocks them with zero code changes. WE DO NOT PLACE ANY DOORS: the
# real ones have been there since 1994. We just cut the key.
DOOR_LOCK_ID = 99

# ---------------------------------------------------------------------------
# The retail sealed-door slabs to REMOVE (exact raw FIXED.DAT items).
# build_all_maps.py filters these out of the base map before adding ours.
# ---------------------------------------------------------------------------
# (empty — the 619 monoliths at y=2751 are the dark interior backdrop
# behind the real doors; earlier builds wrongly removed them)
BASE_ITEM_REMOVALS = {
    # --- 2026-09-01: THE CAVE SEAM WALL (glob egg 933) ---------------------
    # This is a DELIBERATE DEVIATION FROM RETAIL GEOMETRY. Read
    # docs/playtest-2026-09-01-stock-bindings-climb.md before changing it.
    #
    # Map 8's south cave is two disjoint z=56 regions. The one the cave
    # ascent reaches is a pocket of 4,864 standing positions, bounded by the
    # z=8 corridor face north, a 56-unit drop south, and — east, 96 units
    # away — a wall. Past that wall is the 61,373-position shelf that
    # carries the electric gateway, the cave mouth and the whole route on
    # to Mythran.
    #
    # Nothing crosses those 96 units. Standing jump falls short; running
    # jump slides along the face; hop.py cannot resolve a target; a manual
    # both-button targeted chord only turns the Avatar; all four walking
    # directions are refused. And the 48-unit faces from the trench onto
    # the shelf refuse the climb scan at every facing and standoff tried
    # (2026-09-01, and F1 before it). Every session that has crossed this
    # cave crossed it with `MainActor::teleport`.
    #
    # The blocker is ONE item: shape 32 frame 1, footpad 32x128x48, at
    # (29695, 24447, 56), spanning x (29663,29695] y (24319,24447]
    # z [56,104). It is a segment of a north-south wall column, and it is
    # inside GLOB 933 — so it cannot be filtered by coordinate. The glob
    # egg is removed here and its other 20 items are re-placed verbatim by
    # `seam_glob_replacement()`, which is the same "remove the base item,
    # put ours back" pattern the sealed-doors work established.
    #
    # Deleting that one segment opens a 128-unit doorway and joins the two
    # regions: the pocket goes 4,864 -> 66,336 positions and reaches
    # cp3j-past-gate at (30815, 24520, 56).
    (29695, 24575, 56, 2),

    # --- 2026-09-01: THE SECOND SEAM (glob egg 936) -----------------------
    # Same story, one chamber further south. The joined shelf stopped dead
    # at y=26367 — walked from cp3n, the Avatar reaches (30407, 26366, 56)
    # and wedges, and the east side is walled too ((31355, 25154, 56)).
    # F3 puts the cave mouth at y~29100, so the shelf did not reach it.
    #
    # The barrier is an east-west wall run at y=26399. Dropping ONE item —
    # shape 26 frame 7, footpad 128x32x48, at (30463, 26399, 56) — opens a
    # 128-unit doorway and takes the shelf from 66,336 to 221,491 standing
    # positions, reaching the cave mouth. `seam2_glob_replacement()` puts
    # the glob's other 36 items back verbatim.
    (30719, 26623, 56, 2),
}

# The 20 items of glob 933 minus the seam wall segment. Re-placed as plain
# FIXED items because the glob is all-or-nothing. Verbatim from
# GlobReader.glob_to_items(933, 29695, 24575, 56) — do not "tidy" them.
SEAM_GLOB_ITEMS = [
    # (x, y, z, shape, frame)
    (29695, 24159, 104, 31, 1),
    (29695, 24191,  56, 32, 2),
    (29695, 24319,  56, 32, 3),
    (29695, 24415, 104, 32, 6),
    (29695, 24575, 104, 31, 1),
    (29695, 24479, 104, 30, 1),
    (29695, 24191, 152, 498, 0),
    (29695, 24575, 152, 498, 0),
    # (29695, 24447, 56, 32, 1)  <-- THE SEAM WALL, deliberately omitted
    (29695, 24575,  56, 32, 0),
    (29695, 24223, 104, 30, 1),
    (29695, 24287, 104, 30, 0),
    (29439, 24575,  56, 564, 2),
    (29439, 24319,  56, 564, 2),
    (29695, 24319, 152, 564, 5),
    (29695, 24575, 152, 564, 6),
    (29695, 24447, 152, 498, 0),
    (29695, 24319, 152, 498, 0),
    (29439, 24575, 152, 564, 2),
    (29439, 24319, 152, 564, 2),
    (29695, 24575,  56, 564, 2),
]


def seam_glob_replacement():
    """Glob 933's items, minus the one wall segment that seals the cave."""
    return [MapItem.placed_item(x=x, y=y, z=z, shape=shape, frame=frame)
            for (x, y, z, shape, frame) in SEAM_GLOB_ITEMS]


# Glob 936, verbatim from GlobReader.glob_to_items(936, 30719, 26623, 56),
# minus the wall segment at (30463, 26399, 56) — the second doorway.
SEAM2_GLOB_ITEMS = [
    (30719, 26527, 152, 334, 0),
    (30591, 26527, 152, 334, 0),
    (30335, 26623, 152, 334, 0),
    (30719, 26623, 152, 334, 0),
    (30623, 26399,  56,  32, 7),
    (30463, 26399, 104,  26, 8),
    (30591, 26399, 104,  26, 8),
    (30623, 26399, 104,  32, 8),
    (30623, 26271, 104,  29, 6),
    (30335, 26399,  56,  29, 6),
    (30623, 26271,  56,  29, 6),
    (30335, 26271, 104,  29, 7),
    (30335, 26367, 104,  31, 4),
    (30335, 26399, 104,  29, 6),
    (30591, 26623, 152, 334, 0),
    (30463, 26623, 152, 334, 0),
    (30463, 26527, 152, 334, 0),
    (30591, 26527, 152, 334, 0),
    (30719, 26271, 104,  27, 3),
    (30719, 26271, 152, 497, 0),
    (30623, 26399, 152, 498, 0),
    (30303, 26271, 104,  27, 3),
    (30335, 26367, 152, 334, 26),
    (30335, 26495, 152, 334, 0),
    (30591, 26399, 152, 497, 0),
    (30463, 26399, 152, 497, 0),
    (30335, 26271, 152, 497, 0),
    (30335, 26399, 152, 498, 0),
    (30463, 26623,  56, 564, 2),
    (30719, 26623,  56, 564, 2),
    (30591, 26399,  56,  26, 7),
    (30463, 26367,  56, 564, 2),
    (30719, 26367,  56, 564, 2),
    (30303, 26239,  56,  27, 2),
    (30335, 26367,  56,  32, 7),
    # (30463, 26399, 56, 26, 7)  <-- THE SECOND SEAM WALL, omitted
    (30719, 26271,  56,  27, 3),
]


def seam2_glob_replacement():
    """Glob 936's items, minus the wall segment at (30463, 26399, 56)."""
    return [MapItem.placed_item(x=x, y=y, z=z, shape=shape, frame=frame)
            for (x, y, z, shape, frame) in SEAM2_GLOB_ITEMS]

# VQ-003, VQ-004, and VQ-008: these retail chunks became reachable
# through the two authorised seam cuts. The 32-unit exact-reach flood from (29311,24415,56)
# reaches 304 cells in pristine retail and 15,740 after the cuts. Only the
# black surfaces intersecting the added component are listed below; the
# pocket keeps its art outside the first doorway's threshold footprint;
# the trench and other retail routes keep their own art.
# Coordinates are expanded GLOB.FLX records, including their half-open boxes.
LV_SHELF_GLOBS = (
    (31743, 24063, 937),
    (32255, 24063, 1757),
    (31743, 24575, 938),
    (32255, 24575, 1757),
    (31743, 25087, 937),
    (32255, 25087, 1757),
    (31743, 25599, 938),
    (32255, 25599, 1757),
    (31743, 26111, 937),
    (32255, 26111, 1757),
    (29695, 26623, 936),
    (30207, 26623, 935),
    (31231, 26623, 935),
    (31743, 26623, 394),
    (32255, 26623, 1757),
    (29695, 27135, 931),
    (30207, 27135, 1757),
    (30719, 27135, 1757),
    (31231, 27135, 1757),
    (31743, 27135, 1757),
    (32255, 27135, 1757),
    (30207, 27647, 937),
    (30719, 27647, 1757),
    (31231, 27647, 1757),
    (31743, 27647, 1757),
    (32255, 27647, 1757),
    (30207, 28159, 938),
    (30719, 28159, 1757),
    (31231, 28159, 1757),
    (28159, 28671, 936),
    (28671, 28671, 935),
    (29183, 28671, 772),
    (30207, 28671, 937),
    (30719, 28671, 1757),
    (31231, 28671, 1757),
    (30719, 29183, 1757),
    (31231, 29183, 1757),
    (30719, 29695, 1757),
    (31231, 29695, 1757),
    (30719, 30207, 1757),
    (31231, 30207, 1757),
    (30719, 30719, 1757),
    (31231, 30719, 1757),
)
BASE_ITEM_REMOVALS.update((x, y, 56, 2) for x, y, _ in LV_SHELF_GLOBS)

# Floor and ceiling coordinates are separate: a black ceiling is never
# painted into a floor. Ceiling support and collision use retail's
# invisible, zero-height equivalents (499: 256 square, 763: 128 square).
# Shape 499 preserves SOLID support; its missing LAND affects only the
# unreachable ceiling tops. Editor floor 761 has damaging SCREAMER usecode.
LV_SHELF_FLOORS = frozenset((
    (31487, 23807), (31743, 23807), (31999, 23807), (32255, 23807),
    (31487, 24063), (31743, 24063), (31999, 24063), (32255, 24063),
    (31519, 24191),
    (31743, 24319), (31999, 24319), (32255, 24319),
    (29695, 24575), (31743, 24575), (31999, 24575), (32255, 24575),
    (31487, 24831), (31743, 24831), (31999, 24831), (32255, 24831),
    (31487, 25087), (31743, 25087), (31999, 25087), (32255, 25087),
    (31519, 25215),
    (31743, 25343), (31999, 25343), (32255, 25343),
    (31743, 25599), (31999, 25599), (32255, 25599),
    (31487, 25855), (31743, 25855), (31999, 25855), (32255, 25855),
    (31487, 26111), (31743, 26111), (31999, 26111), (32255, 26111),
    (29439, 26367), (29695, 26367), (29951, 26367), (30207, 26367), (30463, 26367),
    (30719, 26367), (30975, 26367), (31231, 26367), (31487, 26367), (31743, 26367),
    (31999, 26367), (32255, 26367),
    (29439, 26623), (29695, 26623), (29951, 26623), (30207, 26623), (30463, 26623),
    (30719, 26623), (30975, 26623), (31231, 26623), (31487, 26623), (31743, 26623),
    (31999, 26623), (32255, 26623),
    (29439, 26879), (29695, 26879), (29951, 26879), (30207, 26879), (30463, 26879),
    (30719, 26879), (30975, 26879), (31231, 26879), (31487, 26879), (31743, 26879),
    (31999, 26879), (32255, 26879),
    (29695, 27135), (29951, 27135), (30207, 27135), (30463, 27135), (30719, 27135),
    (30975, 27135), (31231, 27135), (31487, 27135), (31743, 27135), (31999, 27135),
    (32255, 27135),
    (29951, 27391), (30207, 27391), (30463, 27391), (30719, 27391), (30975, 27391),
    (31231, 27391), (31487, 27391), (31743, 27391), (31999, 27391), (32255, 27391),
    (29951, 27647), (30207, 27647), (30463, 27647), (30719, 27647), (30975, 27647),
    (31231, 27647), (31487, 27647), (31743, 27647), (31999, 27647), (32255, 27647),
    (29983, 27775),
    (30207, 27903), (30463, 27903), (30719, 27903), (30975, 27903), (31231, 27903),
    (30207, 28159), (30463, 28159), (30719, 28159), (30975, 28159), (31231, 28159),
    (27903, 28415), (28159, 28415), (28415, 28415), (28671, 28415), (28927, 28415),
    (29951, 28415), (30207, 28415), (30463, 28415), (30719, 28415), (30975, 28415),
    (31231, 28415),
    (29951, 28671), (30207, 28671), (30463, 28671), (30719, 28671), (30975, 28671), (31231, 28671),
    (30463, 28927), (30719, 28927), (30975, 28927), (31231, 28927),
    (30463, 29183), (30719, 29183), (30975, 29183), (31231, 29183),
    (30463, 29439), (30719, 29439), (30975, 29439), (31231, 29439),
    (30463, 29695), (30719, 29695), (30975, 29695), (31231, 29695),
    (30463, 29951), (30719, 29951), (30975, 29951), (31231, 29951),
    (30463, 30207), (30719, 30207), (30975, 30207), (31231, 30207),
    (30463, 30463), (30719, 30463), (30975, 30463), (31231, 30463),
    (30463, 30719), (30719, 30719), (30975, 30719), (31231, 30719),
))
LV_SHELF_CEILINGS = frozenset((
    (31519, 23679, 152),
    (31743, 23775, 144),
    (31519, 23807, 152),
    (31519, 23935, 152),
    (31743, 24031, 144),
    (31519, 24063, 152),
    (31519, 24191, 152), (31647, 24191, 152), (31743, 24191, 152),
    (31647, 24319, 152), (31743, 24319, 152),
    (31647, 24447, 152), (31743, 24447, 152),
    (29695, 24575, 152), (31519, 24575, 152), (31647, 24575, 152), (31743, 24575, 152),
    (31519, 24703, 152),
    (31743, 24799, 144),
    (31519, 24831, 152),
    (31519, 24959, 152),
    (31743, 25055, 144),
    (31519, 25087, 152),
    (31519, 25215, 152), (31647, 25215, 152), (31743, 25215, 152),
    (31647, 25343, 152), (31743, 25343, 152),
    (31647, 25471, 152), (31743, 25471, 152),
    (31519, 25599, 152), (31647, 25599, 152), (31743, 25599, 152),
    (31519, 25727, 152),
    (31743, 25823, 144),
    (31519, 25855, 152),
    (31519, 25983, 152),
    (31743, 26079, 144),
    (31519, 26111, 152),
    (31519, 26239, 152),
    (29311, 26367, 152), (29951, 26367, 152), (30079, 26367, 152), (30207, 26367, 152),
    (30335, 26367, 152), (30975, 26367, 152), (31103, 26367, 152), (31231, 26367, 152),
    (31711, 26367, 152),
    (29823, 26399, 152), (29951, 26399, 152), (30079, 26399, 152), (30207, 26399, 152),
    (30847, 26399, 152), (30975, 26399, 152), (31103, 26399, 152), (31231, 26399, 152),
    (31359, 26399, 152),
    (29311, 26495, 152), (30335, 26495, 152),
    (29439, 26527, 152), (29567, 26527, 152), (29695, 26527, 152), (30463, 26527, 152),
    (30591, 26527, 152), (30719, 26527, 152), (31359, 26527, 152),
    (29919, 26623, 144), (30175, 26623, 144), (30943, 26623, 144), (31199, 26623, 144),
    (29311, 26623, 152), (29439, 26623, 152), (29567, 26623, 152), (29695, 26623, 152),
    (30335, 26623, 152), (30463, 26623, 152), (30591, 26623, 152), (30719, 26623, 152),
    (31359, 26623, 152), (31615, 26623, 152), (31711, 26623, 152),
    (29439, 26879, 152), (29695, 26879, 152),
    (29695, 27135, 152),
    (29983, 27263, 152),
    (30207, 27359, 144),
    (29983, 27391, 152),
    (29983, 27519, 152),
    (30207, 27615, 144),
    (29983, 27647, 152),
    (29983, 27775, 152), (30111, 27775, 152), (30207, 27775, 152),
    (30111, 27903, 152), (30207, 27903, 152),
    (30111, 28031, 152), (30207, 28031, 152),
    (29983, 28159, 152), (30111, 28159, 152), (30207, 28159, 152),
    (29983, 28287, 152),
    (30207, 28383, 144),
    (29087, 28415, 152), (29983, 28415, 152),
    (29983, 28543, 152),
    (30207, 28639, 144),
    (29983, 28671, 152),
))


def shelf_backdrop(item):
    """Preserve a surface's projected paint without adding physical support."""
    # Moving both axes by -4*z preserves (x-y)/4 and (x+y)/8-z,
    # including irregular frame edges. Avatar and shelf sort above z0.
    return MapItem.placed_item(
        x=item.x - 4 * item.z, y=item.y - 4 * item.z, z=0,
        shape=(SHAPE_CAVE_BACKDROP_LARGE if item.shape == 564
               else SHAPE_CAVE_BACKDROP_SMALL), frame=item.frame)


def drawn_shelf_surfaces(items):
    """Draw the LV-exposed floor at the existing floor height."""
    import random

    out = []
    # The upper courses beside the second cut paint over its approach.
    # Matching invisible walls preserve every collision box and barrier height;
    # the lower retail rock courses supply the doorway jambs.
    # The first lintel remains: hiding it enlarges the dark slit while the
    # raised retail shelf still masks the threshold at m08-07.
    upper_walls = {
        (30463, 26399, 104, 26): 497,
        (30591, 26399, 104, 26): 497,
        (30623, 26399, 104, 32): 498,
    }
    for item in items:
        if (item.x, item.y, item.z, item.shape) == (30335, 26367, 56, 32):
            # The upper jamb looked detached above its black lower course.
            # The textured frame joins the two without changing the box.
            item = MapItem.placed_item(x=item.x, y=item.y, z=item.z,
                                       shape=item.shape, frame=0)
        invisible = upper_walls.get((item.x, item.y, item.z, item.shape))
        if invisible is not None:
            out.append(MapItem.placed_item(
                x=item.x, y=item.y, z=item.z, shape=invisible, frame=0))
        elif (item.z == 56 and (item.x, item.y) in LV_SHELF_FLOORS
                and (item.shape == 334
                     or (item.shape, item.frame) == (564, 2))):
            # The rock tiles leave the black plate's irregular border clear.
            out.append(shelf_backdrop(item))
            # 301 and 564 are both LAND|SOLID|DRAW, with zero height.
            # Four 128-square rocks replace one 256-square black plate.
            offsets = (0, 128) if item.shape == 564 else (0,)
            for dx in offsets:
                for dy in offsets:
                    out.append(MapItem.placed_item(
                        x=item.x-dx, y=item.y-dy, z=56,
                        shape=SHAPE_ROCK_SLAB_GROUND,
                        frame=random.Random(
                            f'8:shelf:{item.x-dx}:{item.y-dy}').randrange(4)))
        elif ((item.x, item.y, item.z) in LV_SHELF_CEILINGS
              and item.shape in (334, 564)):
            out.append(MapItem.placed_item(
                x=item.x, y=item.y, z=item.z,
                shape=499 if item.shape == 564 else 763, frame=0))
            # Low-resolution play retains every pixel that no item paints.
            out.append(shelf_backdrop(item))
        else:
            out.append(item)
    return out


def first_seam_aperture_backdrops():
    """Repaint the removed wall's air gap above the existing threshold."""
    # These black decorative plates cover the old wall sprite in projection.
    # The physical floor, lintel, and raised retail shelf retain their records.
    return [MapItem.placed_item(x=x, y=y, z=0,
                               shape=SHAPE_CAVE_BACKDROP_LARGE, frame=2)
            for x, y in ((29423, 24111), (29295, 23983))]


def route_backdrops(items):
    """Paint the void seen from the LV shelf and the approved retail stops."""
    from pathlib import Path
    from base_input import pristine_base
    from lv_furnish import cells_within_view, floor_cells
    from map_preview import GlobReader, expand_globs
    from parse_typeflag import load_typeflag
    from u8_map import MapArchive

    root = Path(__file__).resolve().parents[3]
    shapes = load_typeflag(str(root / 'shared/build/TYPEFLAG.DAT'))
    retail = MapArchive(pristine_base(str(
        root / 'shared/data/u8-install/STATIC/FIXED.DAT'))).get_map_items(8)
    retained = [i for i in retail
                if (i.x, i.y, i.z, i.shape) not in BASE_ITEM_REMOVALS]
    expanded = expand_globs(retained + items, GlobReader())
    cover = floor_cells(expanded, shapes, eggs_as_chunks=False, painted=True)
    # A 256-square seed covers each replaced shelf plate. These seeds
    # describe the view envelope only and are never emitted as LAND.
    seeds = [MapItem.placed_item(x=x, y=y, z=56, shape=564, frame=2)
             for x, y in sorted(LV_SHELF_FLOORS)]
    shelf = floor_cells(seeds, shapes, eggs_as_chunks=False, painted=True)
    # All four LV route witnesses receive the cave's dark surround.
    # Decorative backings repaint the view without adding support.
    route = {(29151, 30303), (20319, 3247), (20031, 3423), (21199, 3855)}
    route = {(x // 128 * 128 + 127, y // 128 * 128 + 127)
             for x, y in route}
    plates = set()
    for cells, z in ((shelf, 56), (route, 0)):
        for x, y in cells_within_view(cells) - cover:
            if x > 32767 or y > 32767:
                continue
            bx, by = x // 256 * 256 + 255, y // 256 * 256 + 255
            plates.add((bx - 4*z, by - 4*z))
    # Retained retail ceilings cut isolated skirt fragments into these
    # first-seam views. Keep their accepted darkness until the aperture
    # has a complete treatment; the remaining shelf receives the skirt.
    views = []
    for x, y, z in ((29745, 23677, 0), (29279, 23967, 56)):
        sx, sy = (x-y)//4 - 320, (x+y)//8 - z - 220
        views.append((sx, sy, sx+640, sy+400))
    out = []
    for x, y in sorted(plates):
        sx, sy = (x-y)//4, (x+y)//8
        if any(sx-63 < r and sx+63 > l and sy-63 < b and sy+1 > t
               for l, t, r, b in views):
            continue
        # Decorative black repaints low-resolution frames without adding
        # support beneath the shelf or exposing disconnected paving.
        out.append(MapItem.placed_item(x=x, y=y, z=0,
                   shape=SHAPE_CAVE_BACKDROP_LARGE, frame=2))
    return out


def shelf_glob_replacements():
    """Keep each selected retail chunk verbatim except its exposed black."""
    from map_preview import GlobReader

    gr = GlobReader()
    return drawn_shelf_surfaces([
        item for x, y, glob in LV_SHELF_GLOBS
        for item in gr.glob_to_items(glob, x, y, 56)])


# Chest in the OUTER bone chamber (y 3150-3900), the only reliably
# visible ground per the engine's own map dump (GameMapGump::dumpMap,
# 2026-07-02) — WITH THE KEY INSIDE IT, as the 1994 design specifies
# ("The key is found in a nearby chest"). FIXED-format containment
# (decoded from ScummVM map.cpp loadFixedFormatObjects): every
# SF_CONTAINER item opens a container context; immediately following
# records with x == container depth (1) are loaded INTO it (y/z/flags
# copied from a real base-game contained item: the desk-book on this
# same map, x=1 y=8221 z=0 flags=0x2408). Any later record with a real
# x coordinate pops the context.
# VISIBILITY RULES learned the hard way:
#  - The corridor strip y 2751-3071 in front of the doors renders BEHIND
#    the cave's south wall sprites (wall row at y=3071 has larger x+y, so
#    it draws after and covers anything standing in the strip — that is
#    where the avatar kept disappearing).
#  - The z=96 ceiling plates carry no SI_ROOF flag (never auto-hidden);
#    their wall-top row at y=3103 visually shadows y 3039-3167.
#  => interactive items live at y >= 3180, in the open bone field, near
#     the wall GAP at x 20287-20543 where the paved path passes through.
# Key is SW of the chest in world coords (= in front on screen) so the
# chest sprite can never overdraw it.
# NOTE reach rule (engine, 2026-07-02): double-click 'use' requires the
# avatar within 128 units AND a clear line-sweep — solid clutter (the
# mushroom clusters at the cliff foot) blocks canReach and flashes the
# red X. Loot therefore sits ~130 units out in the open bone field.
CHEST_X = 20436   # moved 64 west 2026-07-31: at 20500 the chest sat 16
CHEST_Y = 3340    # units INSIDE trigger 212's hatch box (x 20484..21316 —
                  # approaching it from the south teleported you to Map 10,
                  # demonstrated in the retest). Now 48 clear of the box on
                  # the far side (and since 2026-10-10 the box is about 500
                  # south of it, see TELE_213_TRIGGER_X).
                  # y 3370 -> 3340 after build 7: its box, x (20340,20436]
                  # y (3306,3370] z [0,16), overlapped the retail skeleton
                  # (358, U8SAVE's NONFIXED) at (20447,3487,0), box x
                  # (20383,20447] y (3359,3487], and the Avatar walking the
                  # doorway column at x 20383 closed the paint cycle
                  # 358 -> 1 -> 78 between them (12 engine lines,
                  # playtest-2026-10-11-build7 finding 3; test_paint_cycles).
                  # Now 19 units north of the skeleton.

# Teleport trigger -> Map 9, in the black interior pocket BEHIND the doors
# (base 564 floor at (20351,2719) spans x 20223-20479, y 2591-2847).
# Unreachable until the doors are unlocked and opened.
TELE_200_TRIGGER_X = 20415
TELE_200_TRIGGER_Y = 2783   # deepened 2026-07-04 (was 2980): 190 units
                            # from return-dest 201 meant re-approaching
                            # the doors after a Map 9 round trip bounced
                            # you straight back (map_walkability teleport
                            # spacing rule). It keeps it behind the
                            # doors on the same base-564 floor span
                            # (y 2591-2847), >=384 from dests 201 and 212.
                            # 2783, not 2786 (2026-10-10): the hatch box
                            # (npcNum 0xC9, +/-288 in y) reaches a body
                            # whose max corner is below y + 288 + 64. At
                            # 2786 that was 3138, and 3135 is where a body
                            # stands flush south of the y=3071 door line,
                            # the closed leaves or the wall niche west of
                            # the west jamb: three units of it were inside
                            # the box. y + 352 = 3135 stops the box at the
                            # door line, so only the open doorway reaches it.
TELE_200_TRIGGER_Z = 0

# Teleport destination for returns from Map 9 (ID 201) — in the niche west
# of the doorway's west jamb, on the bone pile at z 8.
#   2026-10-10 (d665e3c): (20415,3170) -> (20160,3420,0), off the doorway's
#     straight north line.
#   2026-10-10 (later): -> the niche. (20160,3420,0) stood at z 0 INSIDE
#     retail bone piles (tops 8 and 16; arrival_footing), and its north line
#     was only safe by luck: the engine's mover slides a refused step 45
#     degrees and a keyboard hold then faces the slide, and 16 units east
#     a held key wall-followed into trigger 212 (test_route_reach.
#     arrival_corridors, now on avatar_mover.py). In the niche, north,
#     north-east and north-west are all wall or jamb, so every held input
#     stops where it lands — this is where his northbound runs from the
#     old pad ended in-engine, (20156,3140,8) (playtest 10-10-gateways).
#     The niche is x 20095..20159, y 3135..3191 at z 8; every spot in it
#     passes, so the pad keeps 16 units of margin each way.
TELE_201_DEST_X = 20111
TELE_201_DEST_Y = 3175
TELE_201_DEST_Z = 8

# Teleport destination for arrivals from Lost Vale (Map 10 side sends ID
# 212) — in the same niche, 32 east of the other pad.
#   2026-10-10 (d665e3c): (20260,3260) -> (20192,3300,0).
#   2026-10-10 (later): -> the niche. At (20192,3300,0) a northbound hold
#     met the west jamb, slid NE into the open doorway and hatched 201 to
#     Map 9, 9 holds of 9 in-engine; a NW hold slid into a pocket of bone
#     piles at (20140,3280,0), inside them at z 0, and refused all 8
#     headings (playtest 10-10-gateways G1 and finding 2). He arrives from
#     Map 10's court heading N, NE or NW, and in the niche all three stop.
TELE_212_DEST_X = 20143
TELE_212_DEST_Y = 3175
TELE_212_DEST_Z = 8

# Teleport trigger for going to Lost Vale directly (ID 212, the RETURN to
# the Vale), on the chamber's east wall.
#   Its hatch box is npcNum-ranged: x +/-32 * (npcNum >> 4), y +/-32 *
#   (npcNum & 0xF), the body's max corner in [x - xr, x + xr + 64) by
#   [y - yr, y + yr + 64). It was 0xD4 (x +/-416, y +/-128: npcNum was the
#   teleport id) at (20900,3300), which covered the chamber's whole
#   north-east quarter from x 20484, and a push north at the doors from x
#   20450 slid NE along the leaves into it, to Map 10, doors open or closed
#   (playtest 10-10-gateways finding 3).
#   2026-10-10: the egg moves onto the floor against the east wall and its
#   x range drops to 32 (0x14), so the box is the strip x 21215..21247 for
#   y 3200..3519, with its slab at z=1 (21247,3455).
#   2026-10-10 (later): that strip was unusable (playtest 10-10-maps3 G4,
#   findings 3-4). Glob 938's east wall and z=96 roof stand in front of
#   everything east of about x 20860, so the Avatar was not drawn there
#   (100% covered, item_sorter.overdrawn) and neither was the slab: a blind
#   walk into black. And the slab was a riser: 301 is SOLID and zero
#   height at z=1, scanForValidPosition has no +1 offset, so every walk
#   onto it ended unsupported at z 4 and he got on only by falling back
#   down (avatar_mover `falls`). Now the egg is on open floor in the bone
#   field, x +/-32 and y +/-32 (0x11): the box is the body's max corner in
#   x [20543,20671), y [3871,3999), every spot of it on the floor at z 0
#   and 0% covered, and its marker is a FLUSH pale slab (71, a flat with
#   neither SI_DRAW nor SI_OCCL, so it draws over the SI_DRAW 301 floor;
#   0% covered) on x (20511,20639] y (3839,3967]: a walk across it, mouse
#   or keyboard, fires it with no riser (test_route_reach.deliberate_use).
#   It is off the niche's south-east line: of 256 four-second holds from
#   the two pads (8 headings, every input, doors open and closed) only 10
#   keyboard W/SW wall-follows reach it, none sooner than 1.3 s, and no
#   arrival heading (N/NE/NW) does (arrival_corridors). The doorway column
#   x (20223,20479] ends 32 west of the slab and 64 west of the box's x
#   range, so a walk straight north to the doors inside it never fires.
#   2026-10-11: GATED ON QUEST STATE. The bone field is also the first-visit
#   way in from the spitter corridor, and a mouse run E 3.54 s then N 2.5 s
#   from the corridor's safe pocket (18164,5020) crossed this slab and
#   landed a fresh player on Map 10 with steps 3 and 4 undone
#   (docs/playtest-2026-10-11-replay-leg2.md finding 1). A route to the
#   doors that never crosses the slab cannot be promised: the corridor
#   opens onto the whole chamber floor, and the slab is the return route's
#   only marked spot. So the egg is no longer an engine TeleportEgg (whose
#   hatch is unconditional) but EggValeReturn (lv-new/VALERTRN.UNK), which
#   calls teleportToEgg(10, 212) only once allColumnsDestroyed is set:
#   the flag that opens Map 11's way to 205, the only way into the Vale.
#   Same spot, same npcnum 0x11, so the same hatch box and slab.
#   quality 308 = pinned EGGVALERETURN 1459 - 0x47F (shared/build/
#   lv_manifest.json); test_route_reach.first_visit_approach replays the
#   way in, and test_uc_vale_return.py runs the class both ways.
TELE_213_TRIGGER_X = 20575
TELE_213_TRIGGER_Y = 3903
TELE_213_TRIGGER_Z = 0
TELE_213_TRIGGER_RANGE = 0x11
TELE_213_SLAB_X = 20639   # slab x (20511,20639] y (3839,3967], z 0: the
TELE_213_SLAB_Y = 3967    # body's footprint over it is the hatch box
VALE_RETURN_EGG_QUALITY = 308

# --- Quest step 1 BACKSTOP (shared/docs/wiring.md "Quest step 1: LORDBRIT") --
# Ordering backstop, not the primary: nobody reaches Mythran without
# lbDone (the `lbStarted` global makes a second egg harmless — first one
# the Avatar reaches fires the scene once, this one then sits inert
# forever). Placed on the plateau approach southeast of Mythran's house
# (Mythran's own position is ~(1503,1791) — see the item cluster at the
# top of this file's region scan; his house/porch furniture occupies
# roughly x 1503-2400, y 1791-2050). (2200,2230) is on the open path just
# past that cluster, still well within his house's immediate grounds —
# every route to Mythran (from the plateau entrance OR straight off the
# double doors path) funnels past this point.
LB_BACKSTOP_EGG_X = 2200
LB_BACKSTOP_EGG_Y = 2230
LB_BACKSTOP_EGG_Z = 8

# The apparition stands between the hearth and the dining table, 22 units
# north of the egg. Until 2026-10-07 it stood at (2200, 2326) — "on the open
# path" by the comment above, but that is the ground-floor room of the
# house (fireplace 277 at y 2079, upper floor 164 at z 40), and its box
# x(2104,2200] y(2230,2326] z[8,56) swallowed retail's dining table (263,
# z[0,16)) and the four cups on it (182 at z 16, from U8SAVE.000's
# NONFIXED.DAT, so no builder places them). ItemSorter cannot order boxes
# nested like that: 3,533 `Cycle in paint dependency graph 182 -> 411`
# lines while it stood unclaimed (docs/playtest-2026-10-04-lb-detour.md
# finding 3). Here the box x(2104,2200] y(2112,2208] clears the fireplace
# (y <= 2079) and the table (y > 2212), and its slab y(2080,2208] does too.
# It still pierces the upper floor (z[40,48)) as before: a 48-tall figure
# fits nowhere under that 40-unit ceiling, the nearest spot clear of
# everything is about 430 units away, and LBSCENE.UNK's cleanup only
# reaches 256 from the egg. The engine culls that floor (zlimit = roof z)
# whenever the Avatar is in the room.
LB_BACKSTOP_APPARITION_X = 2200
LB_BACKSTOP_APPARITION_Y = 2208
LB_BACKSTOP_APPARITION_Z = 8


def build_map_08_additions():
    """Return list of MapItem additions for Map 8."""
    items = []

    # 2. The chest (shape 78, "chest", closed) ...
    items.append(MapItem.placed_item(
        x=CHEST_X, y=CHEST_Y, z=0,
        shape=SHAPE_CHEST, frame=0, quality=0
    ))
    # 3. ...with the Key to the Double Doors INSIDE it (containment
    #    record: x=1 = container depth; y/z/flags mimic the base game's
    #    desk-book contained item on this map). quality 99 = the real
    #    doors' lock ID.
    items.append(MapItem(
        x=1, y=8221, z=0,
        shape=SHAPE_KEY, frame=0, flags=0x2408, quality=DOOR_LOCK_ID
    ))

    # 4. Teleport TRIGGER (ID 200) — behind the doors -> Map 9. The
    #    deepened spot sits on the black 564 shadow plate, so it rides a
    #    z=1 paving slab (the door-site precedent) — visible, not void.
    items.append(MapItem.placed_item(
        x=TELE_200_TRIGGER_X, y=TELE_200_TRIGGER_Y, z=1,
        shape=SHAPE_ROCK_SLAB_GROUND, frame=3, quality=0
    ))
    # SWAPPED 2026-07-31: the 07-25 relocation comments were written under
    # the pre-771d5c7 inverted helper names, so the ACTIVE trigger had been
    # built on the quest egress line (the playtest C1 bounce class). Ids and
    # roles unchanged; positions exchanged. See build_map_13's base pair.
    # The slab-marked alcove spot now holds the ACTIVE trigger to Map 9;
    # returns from Map 9 land south of the doors and, since 2026-10-10,
    # off the doorway's line too (see TELE_201_DEST), so neither walking
    # back out nor arriving with the key still held ping-pongs through the
    # doorway box.
    items.append(MapItem.teleport_target(
        x=TELE_201_DEST_X, y=TELE_201_DEST_Y, z=TELE_201_DEST_Z,
        teleport_id=200
    ))

    # 5. The active trigger to Map 9, on the slab behind the doors (ID 201)
    items.append(MapItem.teleporter(
        x=TELE_200_TRIGGER_X, y=TELE_200_TRIGGER_Y, z=1,
        teleport_id=201, dest_npc=201, dest_map=9
    ))

    # 6. Teleport DEST for ID 212 (Avatar arrives from Lost Vale -> Map 8)
    # SWAPPED 2026-07-31: the 07-25 relocation comments were written under
    # the pre-771d5c7 inverted helper names, so the ACTIVE trigger had been
    # built on the quest egress line (the playtest C1 bounce class). Ids and
    # roles unchanged; positions exchanged. See build_map_13's base pair.
    items.append(MapItem.teleport_target(
        x=TELE_212_DEST_X, y=TELE_212_DEST_Y, z=TELE_212_DEST_Z,
        teleport_id=213
    ))

    # 7. The return to Lost Vale (ID 212, Map 8 -> Map 10's pad 212) + its
    #    pale slab, flush with the floor (see TELE_213_TRIGGER_X: z=1 made
    #    it a riser). A usecode egg, not a TeleportEgg: it teleports only
    #    once the Vale is open (VALE_RETURN_EGG_QUALITY).
    # Frame 9, not 0: VQ-091 (the phase 4 Map 8 report, request 1); the
    # route test's DELIBERATE[212] expects it.
    items.append(MapItem.placed_item(
        x=TELE_213_SLAB_X, y=TELE_213_SLAB_Y, z=0,
        shape=SHAPE_SLAB_PALE, frame=9, quality=0
    ))
    items.append(MapItem(
        x=TELE_213_TRIGGER_X, y=TELE_213_TRIGGER_Y, z=TELE_213_TRIGGER_Z,
        shape=SHAPE_PLACEHOLDER_INVISIBLE_EGG, frame=0,
        quality=VALE_RETURN_EGG_QUALITY, npcnum=TELE_213_TRIGGER_RANGE
    ))

    # 8. Quest step 1 BACKSTOP — same egg+apparition pair as the Tenebrae
    #    primary (build_map_39.py), on the Mythran approach. `lbStarted`
    #    makes this harmless if the Tenebrae egg already fired.
    items.append(MapItem(
        x=LB_BACKSTOP_EGG_X, y=LB_BACKSTOP_EGG_Y, z=LB_BACKSTOP_EGG_Z,
        shape=SHAPE_LB_EGG, frame=0,
        quality=LB_EGG_QUALITY, npcnum=LB_EGG_NPCNUM
    ))
    items.append(MapItem.placed_item(
        x=LB_BACKSTOP_APPARITION_X, y=LB_BACKSTOP_APPARITION_Y,
        z=LB_BACKSTOP_APPARITION_Z,
        shape=SHAPE_LB_APPARITION, frame=0, quality=0
    ))

    # 9. Glob 933 re-placed without its seam wall segment — the cave
    #    doorway. See BASE_ITEM_REMOVALS for why.
    items.extend(drawn_shelf_surfaces(seam_glob_replacement()))
    items.extend(drawn_shelf_surfaces(seam2_glob_replacement()))
    items.extend(shelf_glob_replacements())
    items.extend(route_backdrops(items))
    items.extend(first_seam_aperture_backdrops())

    return dress_lv_additions(items)


def dress_lv_additions(items):
    """Validate the authored LV pockets against the complete retained cave."""
    from pathlib import Path
    from base_input import pristine_base
    from lv_dressing import Site
    from parse_typeflag import load_typeflag
    from u8_map import MapArchive

    root = Path(__file__).resolve().parents[3]
    retail = MapArchive(pristine_base(str(
        root / 'shared/data/u8-install/STATIC/FIXED.DAT'))).get_map_items(8)
    retained = [i for i in retail
                if (i.x, i.y, i.z, i.shape) not in BASE_ITEM_REMOVALS]
    shapes = load_typeflag(str(root / 'shared/build/TYPEFLAG.DAT'))
    site = Site(8, retained + items, shapes, seed=408)
    # Retail and the seam replacements must survive as individual records.
    # Dressing on even coordinates stays loose and needs no new prefab.
    site.protected_raw = {id(i) for i in site.items}
    # A broken fairy ring fills a shelf recess. Its open mouth faces the
    # lane, and its taller caps frame a clear centre at camera scale.
    site.set_piece('the hollow fairy ring', [
        MapItem.placed_item(30912, 27136, 56, 65, 0),
        MapItem.placed_item(31104, 27008, 56, 65, 2),
        MapItem.placed_item(31328, 27040, 56, 65, 0),
        MapItem.placed_item(31424, 27200, 56, 65, 1),
        MapItem.placed_item(31424, 27424, 56, 65, 2),
        MapItem.placed_item(31264, 27552, 56, 65, 0),
        MapItem.placed_item(31040, 27520, 56, 65, 1),
        MapItem.placed_item(30912, 27360, 56, 65, 2),
        MapItem.placed_item(31008, 27040, 56, 465, 3),
        MapItem.placed_item(31200, 27008, 56, 465, 7),
        MapItem.placed_item(31456, 27312, 56, 465, 12),
        MapItem.placed_item(31360, 27552, 56, 465, 5),
        MapItem.placed_item(30976, 27456, 56, 465, 14),
        MapItem.placed_item(31168, 27296, 56, 465, 0),
        MapItem.placed_item(31232, 27328, 56, 465, 10),
        MapItem.placed_item(31200, 27232, 56, 465, 6),
    ])
    # Packed supplies and a rolled bed flank a stone fire circle. The
    # dropped torch points toward the doors; the return lane stays clear.
    site.set_piece('the vigil camp', [
        MapItem.placed_item(20224, 3584, 0, 149, 0),
        MapItem.placed_item(20256, 3744, 0, 534, 0),
        MapItem.placed_item(20128, 3776, 0, 568, 0),
        MapItem.placed_item(20352, 3664, 0, 267, 0),
        MapItem.placed_item(20288, 3632, 0, 465, 3),
        MapItem.placed_item(20320, 3600, 0, 465, 7),
        MapItem.placed_item(20384, 3600, 0, 465, 12),
        MapItem.placed_item(20416, 3664, 0, 465, 1),
        MapItem.placed_item(20384, 3728, 0, 465, 9),
        MapItem.placed_item(20320, 3728, 0, 465, 4),
        MapItem.placed_item(20288, 3696, 0, 465, 10),
    ])
    # Four smaller pockets follow individual shelf recesses. Coordinates
    # describe each composition; no stride, scatter, or floor substitution.
    for name, pieces in (
        ('west shelf gravel', (
            (30240, 27360, 465, 4), (30304, 27424, 465, 10),
            (30400, 27392, 465, 2), (30336, 27520, 465, 1),
            (30432, 27584, 465, 13), (30272, 27552, 465, 8))),
        ('east shelf fungus', (
            (31616, 26592, 65, 2), (31680, 26656, 65, 0),
            (31584, 26720, 465, 9), (31744, 26784, 465, 15),
            (31680, 26848, 465, 1), (31552, 26816, 465, 6))),
        ('south shelf gravel fan', (
            (30720, 29152, 465, 11), (30816, 29184, 465, 5),
            (30912, 29248, 65, 1), (30752, 29280, 465, 0),
            (30848, 29376, 465, 14), (31008, 29344, 465, 7))),
        ('lower shelf seep', (
            (30912, 30272, 65, 0), (31136, 30240, 65, 2),
            (31136, 30304, 465, 12), (30848, 30400, 465, 3),
            (31072, 30464, 465, 16), (31168, 30400, 465, 10))),
    ):
        site.set_piece(name, [MapItem.placed_item(x, y, 56, shape, frame)
                              for x, y, shape, frame in pieces])
    return site.pack()[len(retained):]


if __name__ == '__main__':
    items = build_map_08_additions()
    print(f"Map 8 additions: {len(items)} items")
    for item in items:
        print(f"  {item}")

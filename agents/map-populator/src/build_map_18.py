#!/usr/bin/env python3
"""
build_map_18.py — Map 18: Ancient Temple / Shrine of the Ancient Ones

End-game interior map where the Zealan gods are freed.

Layout: ~12x15 chunks (6,144x7,680 world units)

Zones:
  Temple Exterior:   (2048-4096, 512-2560)     4x4 chunks
  Outer Hall:        (1536-4608, 2560-4608)     6x4 chunks
  Transition Hall:   (2048-4096, 4608-6144)     4x3 chunks
  Inner Sanctum:     (1024-5120, 6144-9344)     a cave behind the crack,
                     screen04's shrine stamped in it (2026-10-17)
"""

import sys
import os
import random
sys.path.insert(0, os.path.dirname(__file__))

from u8_map import MapItem, generate_terrain_grid, wall_run_x, wall_run_y
from lv_monster_eggs import monster_group
import lv_cave_vignette as cave_vignette
import lv_dressing
from glob_catalog import GlobReader
from item_sorter import ItemSorter
from parse_typeflag import load_typeflag
from lv_furnish import (
    GLOB_FLAGSTONE_FLOOR, column, accent_reliefs,
    WALL_NS, WALL_EW, WALL_PLAIN,
)
from lv_shapes import (
    SHAPE_LARGE_GATE,
    SHAPE_GOD_CRYSTAL,
    SHAPE_ALTAR_STONE,
    SHAPE_MON_TEMPLE_GUARD,
    SHAPE_SKULL_LOOSE,
    SHAPE_PLACEHOLDER_INVISIBLE_EGG,
    NPCNUM_MONSKUL,
    SHAPE_TAPESTRY_ON_X_WALL,
    SHAPE_TAPESTRY_ON_Y_WALL,
    SHAPE_WALL_LAMP_ON_X_WALL,
    SHAPE_WALL_LAMP_ON_Y_WALL,
    SHAPE_URN,
    SHAPE_BENCH_NS,
    SHAPE_GLOB_WALL_PIECE,
    SHAPE_GRAVEL,
    SHAPE_RUBBLE_PILE,
    SHAPE_RUBBLE_SMALL,
    SHAPE_BLOCKER_X,
    SHAPE_BLOCKER_Y,
    SHAPE_SACRED_SHIELD_1994,
    SHAPE_STRIPED_PROP_1994,
    SHAPE_CAVE_BACKDROP_SMALL,
    SHAPE_CAVE_BACKDROP_LARGE,
    SHAPE_SANCTUM_BACKDROP,
)


from lv_art_props import CAVE_BACKDROP_CLIPS

# === SHAPE CONSTANTS ===
GLOB_TEMPLE_FLOOR = 80      # GLOB.FLX index (not a U8SHAPES.FLX shape id).
                             # NOT A FLOOR TILE: 16 shape-35 flagstones PLUS
                             # four wall pieces (shape 15 x2, 47 x2, all 40
                             # tall) baked along the chunk's south edge with
                             # a 128-unit doorway between them. Tiled, that
                             # stamps a lattice of low walls every 512 units
                             # of y — the "grid of low walls" the 2026-09-13
                             # clearance test measured and the 2026-09-14
                             # in-engine render showed for what it is. No
                             # zone tiles it since 2026-09-14; kept as the
                             # record of what the lattice was.
# The furnishing kit — raised platforms, columns, the stone-wall pair and
# the relief accents — lives in lv_furnish.py since 2026-09-15 (cleanup plan
# Phase 0); it was authored here and Map 18 is its record.
GLOB_SANCTUM_FLOOR = GLOB_FLAGSTONE_FLOOR

# === THE BREACH (2026-09-26) ===
# The crack becomes a full-size doorway once `templeOpen` is set. Without
# it the sanctum had no exit at full size: leaving took a second Tiny Tar,
# and a player who carried one in was sealed with the gods
# (docs/playtest-2026-09-26-steps-15-18.md, finding 2). The 1994 dialogue
# wants it open too: "I have opened your temple!" sends Ezrekal to fetch
# Atli and Thordis, full-size, to meet the Avatar there (EZREKAL.UNK:2048).
#
# These six wall records carry BREACH_QUALITY, and EggTempleEntry and
# EggCrackHint destroy exactly them (getQ, the COLPUZZL idiom). Fixed items
# are re-read from FIXED.DAT on every map switch, so the wall reseals when
# the player leaves Map 18; each arrival reopens it through EggCrackHint's
# second egg, far up the hall and out of view of the wall.
#
# Removed, the ground course is clear over x 2688..2879 (192 units, 129
# positions for the 64-wide body, 2751..2879) and the courses above over
# 2688..2943, so the doorway is 120 tall with no lintel to fit under. The
# ground piece at 3007 (box 2880..3007) stays, a full 40-unit course whose
# west half stands under open air. Quality 307 is used
# by no other Map 18 record; test_crack_geometry.py checks both states.
BREACH_QUALITY = 307
BREACH_Y = 6143
BREACH_PIECES = {          # (x, z, shape): the ends of their boxes
    (2815, 0, SHAPE_GLOB_WALL_PIECE), (2816, 0, 47),
    (2815, 40, SHAPE_GLOB_WALL_PIECE), (2943, 40, SHAPE_GLOB_WALL_PIECE),
    (2815, 80, SHAPE_GLOB_WALL_PIECE), (2943, 80, SHAPE_GLOB_WALL_PIECE),
}



def tag_breach(items):
    """Give the six breach records BREACH_QUALITY. Raises if any is
    missing or doubled, so a wall rebuild cannot drop the tag silently."""
    found = {}
    for it in items:
        key = (it.x, it.z, it.shape)
        if it.y == BREACH_Y and key in BREACH_PIECES:
            if key in found:
                raise ValueError(f'breach piece {key} placed twice')
            it.quality = BREACH_QUALITY
            found[key] = it
    missing = BREACH_PIECES - set(found)
    if missing:
        raise ValueError(f'breach pieces not built: {sorted(missing)}')
    return items


def build_breach_rubble():
    """Floor debris for the breach (2026-09-30, reshaped 2026-10-03). Without
    it the opened wall is a clean 192x120 rectangle with straight jambs and
    no rubble (docs/playtest-2026-09-26-sanctum-breach/ D7, D10, E2b), and
    it reads as a cut doorway. The sanctum-side rubble is also the cue that
    shows the player where the crack is: it is visible over the wall from
    the hall from y 5620 (docs/playtest-2026-10-01-breach-rubble.md).

    Every item here sits on the SANCTUM side (y >= 6144), which is correct
    in both states: a temple wall that is about to give way already has
    fallen stone at its foot, breach or not, so nothing needs to appear or
    vanish with templeOpen. (tag_breach() only tags the six records whose
    (x, z, shape) key is in BREACH_PIECES; none of these match, so they are
    untouched by the sweep in either direction.)

    Two kinds of item, two different safety arguments:

    - The gravel (SHAPE_GRAVEL) is a zd=0 flat. Box::overlaps requires
      az + azd > bz, which a zero-height box fails by construction, so it
      can never overlap anything at all. It is SI_DRAW / SI_OCCL free
      (neither flag), unlike 301/300/299, so it draws above the sanctum
      floor instead of vanishing under it (.claude/rules/map-geometry.md).
      The 128x128 tiles are staggered by 32-96 units with mixed frames and
      thin out away from the wall, so the spill has a ragged edge and a
      tail instead of one square mat.

    - The rubble (524 piles, 96 wide, and 526 chips, 64 wide) has real
      height and so DOES count as a blocker. Each box sits with its north
      y edge at or south of the wall line (y - depth >= 6143), which keeps
      it out of test_crack_geometry's aperture check regardless of x, and
      wholly outside x 2700..2880, the lane test_sanctum_clearance polices.
      The layout is deliberately lopsided: the west side has one pile and
      one chip, the east a pile and two chips. Both margins are re-checked
      by those two tests against the built FIXED.DAT.
    """
    items = []
    # (x, y, frame): x = 32k-1 and y = 32k-1 like the floor grid.
    for (gx, gy, fr) in (
            (2751, 6271, 1), (2879, 6271, 4), (2975, 6271, 7),
            (2815, 6335, 10), (2687, 6335, 13), (3039, 6367, 3),
            (2847, 6431, 17), (2943, 6463, 22), (2783, 6495, 25)):
        items.append(MapItem.placed_item(x=gx, y=gy, z=0,
                                         shape=SHAPE_GRAVEL, frame=fr))
    for (rx, ry, shape, fr) in (
            (2655, 6303, SHAPE_RUBBLE_PILE, 2),
            (3071, 6271, SHAPE_RUBBLE_PILE, 3),
            (2543, 6239, SHAPE_RUBBLE_SMALL, 7),
            (2975, 6231, SHAPE_RUBBLE_SMALL, 6),
            (3135, 6399, SHAPE_RUBBLE_SMALL, 8)):
        items.append(MapItem.placed_item(x=rx, y=ry, z=0, shape=shape,
                                         frame=fr))
    return items


# Every zone boundary that glob 80 used to wall is an explicit run of its
# own wall piece now, with one 256-unit doorway on the temple's centre line
# (x 2944..3199) where the circulation goes through. `wall_run_x` leaves a
# segment open if it overlaps the gap at all, and the pieces land on
# x = start + 128k, so a run started on an odd boundary (…2047, 1535) has
# segment edges at 2943 and 3199 and the doorway comes out exactly 256.
DOORWAY = (2943, 3199)

# The wall faces this projection shows, for accent_reliefs(): the north
# lines (their +y face looks into the room below them) and the west walls.
RELIEF_LINES = [('y', 512), ('y', 2559), ('y', 2591), ('y', 4607),
                ('y', 6143), ('x', 1536), ('x', 2048)]

SHAPE_ALTAR = SHAPE_ALTAR_STONE  # 550, engine name "altar" — a real carved stone altar
                             # block. Was SHAPE_PLACEHOLDER_GENERIC_PILLAR (721), which
                             # is the base-game CHIMNEY: the endgame ceremony centerpiece,
                             # the one object AOSCENE.UNK narrates the Avatar placing the
                             # artifact upon, rendered as a squat brick chimney and printed
                             # "chimney" when clicked (2026-07-19 art audit). Safe to swap
                             # map-side: no LV usecode declares a TypeStatue/TypePedestals
                             # typeclass, and the only foreach over TypeStatue (721) is
                             # PLNTST.UNK's, which is scoped "within 100 cells of referent"
                             # on Map 10 and so can never see a Map 18 item.

# Quality values
QUALITY_GOD_FELICITAR = 301
QUALITY_GOD_DOLORAS = 302
QUALITY_GOD_TIMYRA = 303
QUALITY_ALTAR = 310


def build_temple_exterior():
    """Temple Exterior — the entrance court: gate, teleport eggs."""
    items = []
    x0, y0 = 2048, 512

    # Floor (4x4 chunks). REBUILT 2026-09-14 with the other three zones:
    # GLOB_SANCTUM_FLOOR, the flagstones without glob 80's baked wall row.
    # The zone's south line is placed explicitly below.
    items.extend(generate_terrain_grid(x0, y0, 4, 4, GLOB_SANCTUM_FLOOR))

    # Grand entrance walls. REBUILT SOLID 2026-07-27 (DD-005): these were
    # eight posts of the north-south piece every 256 units — and that
    # shape is 32x128, long in Y, so an east-west run of it covered 32 of
    # every 256 units. See u8_map.wall_run_x/_y for the full write-up.
    # East-west runs use WALL_EW (128x32), north-south runs WALL_NS
    # (32x128), both at the 128 stride the base game itself uses. Those
    # were 492/489 until 2026-09-14 — see the WALL_* block above.
    #
    # Until 2026-09-14 only the north wall and the two sides were built
    # here: GLOB_TEMPLE_FLOOR's baked row walled every chunk's south edge
    # with a 128-unit doorway per chunk, and that was the circulation. It
    # was also the lattice. The south line is now an explicit run of the
    # same wall piece with one 256-unit doorway on the centre line into
    # the Outer Hall — double-walling a glob row here once sealed the
    # player in, so the floor has to be the wall-less glob for this to be
    # right.
    items.extend(wall_run_x(x0, x0 + 2048, y0, WALL_EW, frame=WALL_PLAIN))
    items.extend(wall_run_y(y0, y0 + 2048, x0, WALL_NS, frame=WALL_PLAIN))
    items.extend(wall_run_y(y0, y0 + 2048, x0 + 2047, WALL_NS,
                            frame=WALL_PLAIN))
    items.extend(wall_run_x(x0 - 1, x0 + 2047, y0 + 2047, SHAPE_GLOB_WALL_PIECE,
                            frame=WALL_PLAIN, gaps=[DOORWAY]))

    # The temple gate — set into the north wall's face, centred on the
    # axis (it stood 128 units out on the floor). Quality 180 is a lock id
    # with the LOCKED bit clear: it opens on a double-click onto solid
    # wall, which is what it did before too.
    items.append(MapItem.placed_item(
        x=x0 + 1088, y=y0 + 128, z=0,
        shape=SHAPE_LARGE_GATE, frame=0, quality=180  # temple gate
    ))

    # Colonnade — three pairs down the court, 512 either side of the axis
    # the teleport eggs sit on.
    for cy in (y0 + 512, y0 + 1024, y0 + 1536):
        for cx in (x0 + 512, x0 + 1536):
            items.extend(column(cx, cy))

    # Banners and lamps on the north wall's face, either side of the gate,
    # and an urn in each corner.
    for tx, fr in ((x0 + 832, 0), (x0 + 1344, 0)):
        items.append(MapItem.placed_item(
            x=tx, y=y0 + 1, z=0, shape=SHAPE_TAPESTRY_ON_Y_WALL, frame=fr))
    for tx in (x0 + 640, x0 + 1536):
        items.append(MapItem.placed_item(
            x=tx, y=y0 + 32, z=16, shape=SHAPE_WALL_LAMP_ON_Y_WALL, frame=0))
    for ux, uy in ((x0 + 64, y0 + 128), (x0 + 1984, y0 + 128),
                   (x0 + 64, y0 + 1984), (x0 + 1984, y0 + 1984)):
        items.append(MapItem.placed_item(x=ux, y=uy, z=0, shape=SHAPE_URN,
                                         frame=0))

    # Teleport TRIGGER (ID 210) -> Map 10. Keep this north of the
    # south-wall footprint; the old y0+1536/y0+1792 pair could land the
    # Avatar in the wall/roof collision area and put the return trigger on
    # the inward path.
    # SWAPPED 2026-07-31: the 07-25 relocation comments were written under
    # the pre-771d5c7 inverted helper names, so the ACTIVE trigger had been
    # built on the quest egress line (the playtest C1 bounce class). Ids and
    # roles unchanged; positions exchanged. See build_map_13's base pair.
    items.append(MapItem.teleporter(
        x=x0 + 1024, y=y0 + 896, z=0,
        teleport_id=210, dest_npc=210, dest_map=10
    ))

    # Teleport ARRIVAL PAD (ID 211) — arrival from Map 10, reached by
    # walking in toward the temple entrance rather than deeper into the
    # map. Moved 2026-07-04 (was y0+1024, 256 units from trigger 210 —
    # pad bounce risk per the map_walkability spacing rule).
    items.append(MapItem.teleport_target(
        x=x0 + 1024, y=y0 + 1280, z=0,
        teleport_id=211
    ))

    # Gone 2026-09-14: two rock slabs at z=4 flanking the pad, sixteen
    # floating roof squares at z=24 (one 128-unit tile per chunk), four
    # wall reliefs standing loose on the floor.

    return items


def build_outer_hall():
    """Outer Hall — the great hall: colonnade, guardian, pews."""
    items = []
    x0, y0 = 1536, 2560

    # Floor (6x4 chunks) — GLOB_SANCTUM_FLOOR since 2026-09-14; see the
    # Exterior. The lines this zone owns are placed below.
    items.extend(generate_terrain_grid(x0, y0, 6, 4, GLOB_SANCTUM_FLOOR))

    # Walls — REBUILT SOLID 2026-07-27 (DD-005), and again 2026-09-14. The
    # Outer Hall is WIDER than the zones on either side (x0=1536 vs 2048),
    # so besides its sides it needs: north SHOULDERS either side of the
    # Exterior's south line (which is that zone's to build, x 2048..4095),
    # and its whole south line, with the doorway into the Transition Hall
    # on the centre line. Before today the south line was glob 80's baked
    # row, whose six per-chunk doorways included two — x 1727..1855 and
    # 4287..4415 — that opened onto nothing: the Transition Hall is only
    # x 2048..4095, and the void south of a floor edge is walkable
    # (current_map.cpp:773, the 2026-07-31 sanctum exit). Sealed now.
    items.extend(wall_run_y(y0, y0 + 2048, x0, WALL_NS, frame=WALL_PLAIN))
    items.extend(wall_run_y(y0, y0 + 2048, x0 + 3071, WALL_NS,
                            frame=WALL_PLAIN))
    items.extend(wall_run_x(x0, x0 + 512, y0 + 31, WALL_EW, frame=WALL_PLAIN))
    items.extend(wall_run_x(x0 + 2560, x0 + 3072, y0 + 31, WALL_EW,
                            frame=WALL_PLAIN))
    items.extend(wall_run_x(x0 - 1, x0 + 3071, y0 + 2047, SHAPE_GLOB_WALL_PIECE,
                            frame=WALL_PLAIN, gaps=[DOORWAY]))

    # Close the square between the shoulder and the exterior's south wall.
    # The 32-unit stub stays within the existing wall corner.
    items.append(MapItem.placed_item(2079, 2591, 0, 47, WALL_PLAIN))

    # Colonnade — two rows of four, 640 in from each side wall, the nave
    # between them.
    for cy in (y0 + 384, y0 + 896, y0 + 1408, y0 + 1920):
        for cx in (x0 + 640, x0 + 2432):
            shafts = column(cx, cy)
            items.extend(shafts[:2] if (cx, cy) in ((2176, 3456), (3968, 4480)) else shafts)

    # The temple guardian, a golem (214: 150-175 hp, 15-25 a blow, immune
    # to blades), in the east aisle behind the colonnade, 1,360 units off
    # the nave's line from the north doorway to the south one: beyond the
    # 768 at which a combat-activity monster picks a target. A MONEGG
    # trigger (lv_monster_eggs) just inside the north doorway, x (2943,
    # 3199], hatches it. Until 2026-10-11 it stood mid-nave with no
    # trigger and never hatched.
    items.extend(monster_group(
        1, trigger=(x0 + 1536, y0 + 192, 0), box=(8, 2),
        eggs=[(x0 + 2816, y0 + 1024, 0, SHAPE_MON_TEMPLE_GUARD)]))

    # Pews — two long benches down each side aisle, between the columns
    # and the wall. 8 tall, so they are stepped over, never a wall.
    for by in (y0 + 768, y0 + 1408):
        for bx in (x0 + 160, x0 + 2688):
            items.append(MapItem.placed_item(x=bx, y=by, z=0,
                                             shape=SHAPE_BENCH_NS, frame=0))

    # Tapestries: two on the Exterior's line (its sanctum-side face is
    # y=2560) either side of the doorway, one on each shoulder, two down
    # the west wall. Lamps between them; an urn in each corner.
    for tx, fr in ((x0 + 1024, 0), (x0 + 2048, 2)):
        items.append(MapItem.placed_item(
            x=tx, y=y0, z=0, shape=SHAPE_TAPESTRY_ON_Y_WALL, frame=fr))
    for tx, fr in ((x0 + 256, 2), (x0 + 2816, 2)):
        items.append(MapItem.placed_item(
            x=tx, y=y0 + 32, z=0, shape=SHAPE_TAPESTRY_ON_Y_WALL, frame=fr))
    for ty, fr in ((y0 + 640, 0), (y0 + 1408, 2)):
        items.append(MapItem.placed_item(
            x=x0 + 1, y=ty, z=0, shape=SHAPE_TAPESTRY_ON_X_WALL, frame=fr))
    for tx in (x0 + 768, x0 + 2304):
        items.append(MapItem.placed_item(
            x=tx, y=y0 + 32, z=16, shape=SHAPE_WALL_LAMP_ON_Y_WALL, frame=0))
    items.append(MapItem.placed_item(
        x=x0 + 32, y=y0 + 1024, z=16, shape=SHAPE_WALL_LAMP_ON_X_WALL, frame=0))
    for ux, uy in ((x0 + 64, y0 + 96), (x0 + 3008, y0 + 96),
                   (x0 + 64, y0 + 1984), (x0 + 3008, y0 + 1984)):
        items.append(MapItem.placed_item(x=ux, y=uy, z=0, shape=SHAPE_URN,
                                         frame=0))

    # Gone 2026-09-14: four stools carrying quality 9 and a comment calling
    # them inscriptions, five loose wall reliefs, twenty-four floating roof
    # squares at z=32, two chests.

    return items


def build_transition_hall():
    """Transition Hall — narrowing passage with Tiny Tar entry."""
    items = []
    x0, y0 = 2048, 4608

    # Floor (4x3 chunks) — GLOB_SANCTUM_FLOOR since 2026-09-14; see the
    # Exterior. The crack line below is now wholly this function's.
    items.extend(generate_terrain_grid(x0, y0, 4, 3, GLOB_SANCTUM_FLOOR))

    # Walls — REBUILT SOLID 2026-07-27 (DD-005). The north line is the
    # Outer Hall's (its south run, doorway on the centre line); east and
    # west are sealed here, and the sanctum-gate hardening stacks two more
    # courses on them.
    items.extend(wall_run_y(y0, y0 + 1536, x0, WALL_NS, frame=WALL_PLAIN))
    items.extend(wall_run_y(y0, y0 + 1536, x0 + 2047, WALL_NS,
                            frame=WALL_PLAIN))

    # ══ THE TINY TAR CRACK (DD-005) ══════════════════════════════════════
    # THIS is the temple's real gate, and the whole reason quest steps 17-18
    # exist. The south wall of the Transition Hall IS the Inner Sanctum
    # boundary (y0+1535 = 6143, the sanctum starts at 6144), and it is the
    # ONLY way through: the hall's east and west walls are sealed above, and
    # at these y values there is no terrain at all outside x 2048-4096, so
    # there is nothing to walk around through.
    #
    # The aperture is 63 world units of CLEAR SPAN — x 2817..2879 inclusive.
    # That width is the entire mechanic:
    #
    #     normal Avatar   shape 1   footpad (2,2,5) = 64x64  -> needs 64 free
    #                                                           units, has 63
    #                                                           -> CANNOT fit
    #     shrunken Avatar shape 867 footpad (1,1,4) = 32x32  -> 32 valid x
    #                                                           positions
    #
    # WHY 63 AND NOT 32 (fixed 2026-07-28, and this is the important note in
    # this file). The aperture used to be "one 32-unit cell", closed on the
    # west by a 96-wide filler at x=2848. In the ENGINE that is 31 units of
    # clear span, not 32, and the crack was IMPASSABLE EVEN SHRUNKEN — the
    # whole DD-005 entry route was sealed. Item boxes are half-open:
    # `Box::contains` is `px > _x - _xd && px <= _x`, so the filler at
    # x=2848 occupies 2753..2848 INCLUSIVE and the glob piece east of it
    # occupies 2880..2943. Clear span 2849..2879 = 31. A 32-wide footpad
    # needs 32 consecutive free units, and `Box::overlaps` is strict, so
    # there was no valid x at all.
    #
    # It shipped because the proof was rasterised, not exact:
    # map_walkability quantises to 32-unit cells and marks a cell blocked
    # only when a blocker's span covers the CELL CENTRE, so the filler's
    # last unit (2848, the first unit of cell 89) vanished and the cell read
    # as fully free. The flood then walked a 1-cell body through a gap the
    # engine refuses. `test_crack_geometry.py` now checks this aperture with
    # the engine's own box arithmetic instead; a one-body-width aperture
    # must never again be proven by the cell flood alone.
    #
    # 63 is chosen so BOTH halves have margin: the full-size Avatar is
    # refused by a whole unit of x on every alignment, and the shrunken one
    # has 32 valid positions rather than a single exact fit that the walk
    # code would have to hit dead-on.
    #
    # Until 2026-09-14 the wall on this line was mostly glob 80's: each
    # chunk of GLOB_TEMPLE_FLOOR brought wall pieces along its south edge
    # with a 128-unit doorway at relative x 191-319, so the line carried
    # stone across x 2047-4095 with four holes — [2239,2367] [2751,2879]
    # [3263,3391] [3775,3903] — three of which were filled and the fourth
    # made the crack. The floor is the wall-less glob now and the line is
    # built here in the same pieces, to the same numbers:
    #
    #   pieces (128 wide) from 2047 to 2815; a 64-unit stub whose box is
    #   2753..2816; nothing to 2879; pieces from 2879 to 4031; a stub for
    #   the last 64 to the east wall.
    #
    # Clear span 2817..2879, as before. The stub is what makes it 63 and
    # not 64: the piece west of it already ends at 2815, so the stub's
    # only job is to own unit 2816. It keeps the opening reading as one
    # missing block of masonry.
    #
    # It is deliberately NOT on the map's centre line. A ruined temple has a
    # crack where the masonry failed, not a neat hole above the altar.
    GLOB_WALL_PIECE = SHAPE_GLOB_WALL_PIECE   # 128x32x40 wall segment
    GLOB_WALL_STUB = 47           # the same set's 64x32x40 segment
    CRACK_FILL_X = 2816           # 64-unit stub ends here; clear span 2817..2879
    CRACK_LINE_Y = y0 + 1535      # 6143: the sanctum starts at 6144
    items.extend(wall_run_x(x0 - 1, CRACK_FILL_X - 1, CRACK_LINE_Y,
                            GLOB_WALL_PIECE, frame=WALL_PLAIN))
    items.append(MapItem.placed_item(x=CRACK_FILL_X, y=CRACK_LINE_Y, z=0,
                                     shape=GLOB_WALL_STUB, frame=0))
    items.extend(wall_run_x(2879, x0 + 1983, CRACK_LINE_Y, GLOB_WALL_PIECE,
                            frame=WALL_PLAIN))
    items.append(MapItem.placed_item(x=x0 + 2047, y=CRACK_LINE_Y, z=0,
                                     shape=GLOB_WALL_STUB, frame=0))

    # EGGCRACKHINT — the "far too narrow" bark, on the HALL side of the
    # crack. quality 306 -> class 1457 (lv-new/CRACKHNT.UNK). npcnum 0x66 =
    # +/-192, so it fires as the player comes down the hall toward the wall.
    #
    # It has to be a SEPARATE egg from EggTempleEntry on the far side, not
    # one egg spanning the wall: in U8 Egg::hatch() early-returns on
    # _hatched and Egg::unhatch() is a Crusader-only no-op, so an egg fires
    # at most once per fast-area load. A single egg would spend itself on
    # the hint at full size and never set templeOpen on the way back
    # through shrunken.
    items.append(MapItem(
        x=2864, y=y0 + 1440, z=0,
        shape=SHAPE_PLACEHOLDER_INVISIBLE_EGG, frame=0,
        quality=306, npcnum=0x66  # EggCrackHint 1457
    ))

    # A SECOND EggCrackHint, at the hall's north doorway (2026-09-26). It
    # reopens the breach (see BREACH_QUALITY) on every arrival once
    # `templeOpen` is set, 1,300 units up the hall, so the wall is already
    # open when it comes into view. CRACKHNT reads its own y to tell the
    # two apart: this one never barks the hint. npcnum 0x88 = +/-256, the
    # doorway's width and more.
    items.append(MapItem(
        x=x0 + 1024, y=y0 + 192, z=0,
        shape=SHAPE_PLACEHOLDER_INVISIBLE_EGG, frame=0,
        quality=306, npcnum=0x88  # EggCrackHint 1457, the breach re-opener
    ))

    # FINDABILITY (2026-10-03): the cue for the gap is the rubble on the
    # sanctum side (build_breach_rubble), which shows over the wall from
    # y 5620 on the hall approach. A flat plate on the hall floor right
    # under the wall was tried and removed: it sat 96-223 units north of
    # the 120-tall wall, which hides it from the camera
    # (docs/playtest-2026-10-01-breach-rubble.md). The hall gets one low
    # rock instead, further north where it can be seen. At y 5887 (224 north
    # of the wall's face, y 6111) the wall still hid it in ScummVM; a 16-tall
    # rock needs about 416 units (docs/playtest-2026-10-03-batch-merge.md
    # D1), and at 480 its base met the wall's top edge on screen and read
    # as lying on the parapet (docs/playtest-2026-10-04-batch-retest.md
    # finding 7), so it sits at 5503, 608 north, east of the approach line.
    items.append(MapItem.placed_item(
        x=2975, y=5503, z=0, shape=SHAPE_RUBBLE_SMALL, frame=6))

    # REMOVED 2026-07-27 with the crack: a SHAPE_DOOR_S (69) at
    # (3072, 5888) carrying quality 190 and commented "tiny door". It was
    # neither tiny nor a gate — quality 190 encodes lock id 190 with the
    # 0x400 LOCKED bit CLEAR, so it was an ordinary closed-but-unlocked
    # door that any full-size Avatar opened with a double-click, sitting in
    # the middle of the hall rather than on the sanctum boundary. The real
    # aperture above replaces it.

    # REMOVED 2026-07-27 (egg-queue pass). There was a shape-73 UnkEgg here
    # commented "POTION trigger", carrying quality=4. Quality is not a label:
    # UnkEgg dispatch is class = quality + 0x47F, so quality 4 addressed class
    # 1155 — the base game's TORAN EXECUTION CUTSCENE from Tenebrae ("Toran,
    # you have been accused of blasphemy against our Lady Mordea and sentenced
    # to death", 6,038 bytes) — playing inside the Zealan Ancient Temple.
    # Same authoring error as the Map 10 "SHADES trigger" egg (quality 2 ->
    # MONEGG, fixed earlier today) and the altar egg below.
    #
    # Not re-pointed at anything: Tiny Tar is a DRUNK potion, not an egg
    # scene. TypePotion::use() (POTION.UNK) branches on the item's frame and
    # is already dispatched by npcnum 229 -> class 1253 (see build_map_10.py).
    # A trigger egg was never the mechanism, so this placement simply goes.
    #
    # The Tiny Entry itself stays. What it still needs is a drinkable frame-8
    # potion, which no placed item is yet: shape 766 has only 8 frames (0-7),
    # so frame 8 has no art. That belongs with the temple-opening work, which
    # is blocked on `templeOpen` having no writer anywhere in the corpus.

    # The narrowing. Two stations of stone walls jutting in from the sides
    # (were two wooden hut-wall stubs, 145, standing alone mid-floor), a
    # column at each inner end: the passage closes from 2048 wide to 1280
    # to 1024 on the way to the crack. One course, so their tops are
    # standable; nothing they touch is under 120 tall, so they lead
    # nowhere. Both stations stay north of EggCrackHint's box (y 5856+).
    for jy, jut in ((y0 + 768, 384), (y0 + 1152, 512)):
        items.extend(wall_run_x(x0, x0 + jut, jy, WALL_EW, frame=WALL_PLAIN))
        items.extend(wall_run_x(x0 + 2048 - jut, x0 + 2048, jy,
                                WALL_EW, frame=WALL_PLAIN))
        items.extend(column(x0 + jut + 64, jy))
        items.extend(column(x0 + 2048 - jut - 32, jy))

    # Tapestries either side of the doorway on the Outer Hall's line (its
    # face is y=4608) and one on the west wall; lamps on both.
    for tx, fr in ((x0 + 768, 2), (x0 + 1376, 0)):
        items.append(MapItem.placed_item(
            x=tx, y=y0, z=0, shape=SHAPE_TAPESTRY_ON_Y_WALL, frame=fr))
    items.append(MapItem.placed_item(
        x=x0 + 1, y=y0 + 256, z=0, shape=SHAPE_TAPESTRY_ON_X_WALL, frame=0))
    for tx in (x0 + 384, x0 + 1664):
        items.append(MapItem.placed_item(
            x=tx, y=y0 + 32, z=16, shape=SHAPE_WALL_LAMP_ON_Y_WALL, frame=0))
    for ly in (y0 + 512, y0 + 1344):
        items.append(MapItem.placed_item(
            x=x0 + 32, y=ly, z=16, shape=SHAPE_WALL_LAMP_ON_X_WALL, frame=0))

    # Gone 2026-09-14: twelve floating rubble-ceiling squares at z=20 —
    # below head height — and two loose wall reliefs.

    return items


# ══ THE INNER SANCTUM: screen04's cave shrine (2026-10-17) ══════════════
#
# The 1994 screenshot screen04 is the ceremony: three gods in amber on
# their plinths, the altar with the Shield on it, the Avatar beside it, on
# a cave floor (301) between craggy rock (the 26-32 cave-wall family).
# Under the screenshot rule the sanctum is that place: the reconstruction
# (agents/map-populator/src/vignettes/screen04.json) is stamped verbatim at
# its origin, and the cave around it is extrapolated in the same style.
# The temple's masonry ends at the crack line: the breach opens from the
# Transition Hall into a natural cave the temple was built against.
#
# What went with the 2026-09-14 room: the two-tier dais (the shot's altar
# stands on the floor), the processional way, the candelabra, rune
# columns, cushions, candles, colonnade, tapestries, lamps and urns, the
# flagstone globs, and the temple walls on the west, east and south
# lines. The skull 331 moves off the shot's frame.
SCREEN04 = 'screen04'

# 1994-only art in the vignette -> the shapes the art track built for it.
SCREEN04_ART = {
    2010: (SHAPE_GOD_CRYSTAL, 0),      # Felicitar sealed, 860 frame 0
    2011: (SHAPE_GOD_CRYSTAL, 1),      # Doloras sealed, 860 frame 1
    2012: (SHAPE_GOD_CRYSTAL, 2),      # Timyra sealed, 860 frame 2
    2013: SHAPE_SACRED_SHIELD_1994,    # the Shield on the altar (dropped)
    2014: SHAPE_STRIPED_PROP_1994,     # the striped prop on Felicitar's plinth
}

# The gods and the altar are the vignette's own items; their qualities are
# map-side bookkeeping (nothing in the usecode reads them) and identify the
# god, so they follow the frame. Positions are screen04's, the pin moves its
# placement block lists.
GODS = {   # frame: (x, y, z, quality)
    0: (2783, 8031, 16, QUALITY_GOD_FELICITAR),   # west, hunched
    1: (3039, 7903, 16, QUALITY_GOD_DOLORAS),     # north-east, kneeling
    2: (3039, 8415, 16, QUALITY_GOD_TIMYRA),      # south, standing
}
ALTAR_POS = (3127, 8175, 0)

# THE SHIELD IS NOT PLACED. The shot shows the ceremony moment, with the
# restored Shield already on the altar; in the game the player carries it
# in, and AOSCENE.UNK's shield.pop(3111, 8167, 16) puts it on exactly the
# vignette's spot (altar + (-16, -8, +16)). A map copy would be a second,
# free Shield on the altar from the start.
SCREEN04_LEFT_OUT = [(SHAPE_SACRED_SHIELD_1994, 0, 3111, 8167, 16)]

# EGGAOCEREMONY (quest step 17, freeing the Ancient Ones). Quality 296 ->
# class 1447 (lv-new/AOSCENE.UNK, manifest-pinned); npcnum 0x66 = a +/-192
# hatch box, so it fires as the player reaches the altar, not on entering
# the cave. Floor level since the dais went (EggHatcherProcess's z window is
# +/-48 either way); x, y unchanged, and screen04's Avatar, at
# (3256, 8152, 0) beside the altar, stands inside the box.
#
# AOSCENE checks godsFree (replay guard), templeOpen, shieldFixed, then the
# restored Shield in the Avatar's pack; it sets godsFree, which EggEndgame
# reads.
CEREMONY_EGG = (3072, 8320, 0)

# The priestess's skull (TypeMonskul, npcnum 228 -> class 1252): look()
# barks "Strange skull", use() reads her letter to Odion, Apathas and Amoras.
# A lore placement, not a 1994 one (no quest reads it). It lay on the altar
# until 2026-10-17, which put it on open floor in screen04's frame; it now
# lies at the foot of the cave's west wall south-west of the gods, off the
# frame. Shape 331 is the loose carryable skull, not 641/663 (SI_FIXED).
SKULL_POS = (2496, 8448, 0)

# THE CAVE, on the 128 grid (lv_cave_vignette.Cave): '.' floor, '#' rock.
# Columns are x // 128 from 8 (x 1024), rows y // 128 from 48 (y 6144, the
# first unit south of the crack line). Inside the shot's window the shot
# decides; the mask is the cave round it:
#   rows 48-55  the antechamber behind the breach (x 2304..3455), where the
#               breach rubble lies and EggTempleEntry waits;
#   rows 56-58  two passages round the rock the shot shows at its top
#               (x 2688..2975, its south face on y 7551). The west passage
#               is a cell narrower than the antechamber so that its wall
#               and the shrine's (x 2303) are separate runs: a run any of
#               whose pieces would paint into the window goes invisible
#               whole (Cave._face), and one long run lost them all;
#   rows 59-71  the shrine: the shot's floor and its west wall on x 2303,
#               with the floor run out past the frame on every side (the
#               south edge is y 9215: the old temple wall on y 8703 painted
#               12,769 px into the frame).
# Rock north or west of floor gets cave wall, two 48-unit courses; rock
# south or east of it the invisible wall, so the floor ends at black there,
# as the 1994 caves do. Nothing generated paints into the window.
SANCTUM_CELL0 = (8, 48)
SANCTUM_MASK = [
    # 8       16      24      32     39
    '###########.......##############',   # 48  y 6144
    '###########.......##############',   # 49
    '##########.........#############',   # 50
    '##########.........#############',   # 51
    '##########.........#############',   # 52
    '##########.........#############',   # 53
    '##########..........############',   # 54
    '##########..........############',   # 55
    '###########..###.....###########',   # 56
    '###########..###.....###########',   # 57
    '###########..###.....###########',   # 58
    '##########............##########',   # 59  y 7552
    '##########............##########',   # 60
    '##########............##########',   # 61
    '##########............##########',   # 62
    '##########............##########',   # 63
    '##########............##########',   # 64
    '##########...........###########',   # 65
    '##########...........###########',   # 66
    '###########..........###########',   # 67
    '###########.........############',   # 68
    '############.......#############',   # 69
    '############......##############',   # 70
    '#############....###############',   # 71  y 9088..9215
    '################################',   # 72
]
SANCTUM_BOX = (1024, 6144, 5120, 9344)      # x0, y0, x1, y1 of the mask


def sanctum_island(shot):
    """Cap the enclosed rock between the passages without entering screen04."""
    items = []
    # The cave closure leaves rock tops black. This isolated 3x3 island
    # needs a textured crest. Recess the north and north-east lip to the
    # floor so Tiny Tar stays visible on the approach and both fork turns.
    # Shape 6 is flat gravel without SI_DRAW, so it paints over the black
    # backing at z 0. The 96-unit invisible shell stays in place.
    heights = ((0, 0, 0), (0, 0, 0), (48, 56, 72))
    for cy, row in enumerate(heights, 56):
        for cx, z in enumerate(row, 21):
            # Recess the north and east flats clear of screen04's bounds. Their
            # zero-height boxes leave the approach's floor level intact.
            dy = -64 if cy == 56 and cx < 23 else 0
            if (cx, cy) == (23, 57):
                dy = -8
            items.append(MapItem.placed_item(
                cx * 128 + 127, cy * 128 + 127 + dy, z,
                SHAPE_GRAVEL if z == 0 else cave_vignette.ROCK_FLOOR,
                0 if z == 0 else (cx + 3 * cy) % 7))

    # The closure hides a whole face run when any piece enters the shot.
    # Keep the visible face behind the fork. The upper course closes the
    # triangular seam below the 72-unit cap; the post backs its south tip.
    # These faces stay inside the shell and outside screen04's window.
    items.append(MapItem.placed_item(3071, 7423, 0, 30, 0))
    items.append(MapItem.placed_item(3071, 7487, 0, 30, 0))
    items.append(MapItem.placed_item(3071, 7487, 24, 30, 0))
    items.append(MapItem.placed_item(3071, 7503, 0, 29, 0))
    if any(shot.paints_window(it) for it in items):
        # The low west lip extends behind the shot's own rock face. Its
        # sprite bounds reach the window, so check the final painted pixels.
        p = cave_vignette.built_painter()
        base = [cave_vignette._d(it) for it in shot.items]
        before = p.paint(base, shot.csx, shot.csy, shot.W, shot.H)[0]
        after = p.paint(base + [cave_vignette._d(it) for it in items],
                        shot.csx, shot.csy, shot.W, shot.H)[0]
        if (before != after).any():
            raise ValueError('sanctum island changes screen04 pixels')
    return items


def build_inner_sanctum(items):
    """Return `items` with the Inner Sanctum built: screen04 stamped, its
    gods and altar tagged, the ceremony egg and the skull placed, and the
    cave closed round the shot (lv_cave_vignette)."""
    shot = cave_vignette.Shot(SCREEN04, art_map=SCREEN04_ART)
    items, shot = cave_vignette.stamp(items, shot, 18)
    items = shot.drop(items, SCREEN04_LEFT_OUT)

    for it in items:
        if it.shape == SHAPE_GOD_CRYSTAL and it.frame in GODS and \
                (it.x, it.y, it.z) == GODS[it.frame][:3]:
            it.quality = GODS[it.frame][3]
        elif it.shape == SHAPE_ALTAR and (it.x, it.y, it.z) == ALTAR_POS:
            it.quality = QUALITY_ALTAR
    tagged = [it for it in items if it.quality in
              (QUALITY_GOD_FELICITAR, QUALITY_GOD_DOLORAS, QUALITY_GOD_TIMYRA,
               QUALITY_ALTAR) and it.shape in (SHAPE_GOD_CRYSTAL, SHAPE_ALTAR)]
    if len(tagged) != 4:
        raise ValueError(f'screen04: expected three gods and the altar at '
                         f'their pins, tagged {len(tagged)}')

    items.append(MapItem(
        x=CEREMONY_EGG[0], y=CEREMONY_EGG[1], z=CEREMONY_EGG[2],
        shape=SHAPE_PLACEHOLDER_INVISIBLE_EGG, frame=0,
        quality=296, npcnum=0x66  # EggAOCeremony 1447
    ))

    # The temple's own pieces stay as built. The hall's side walls end on
    # y=6144 (their last piece's box is y 6017..6144), the mask's first row,
    # and the closure would drop them as rock-cell clutter: the hall's
    # corners then opened onto the void (test_map_edges, 2026-10-17).
    def temple_side(it):
        return it.y <= SANCTUM_BOX[1] and not it.is_glob_egg
    temple = [it for it in items if temple_side(it)]
    items = [it for it in items if not temple_side(it)]
    cave = cave_vignette.Cave(shot, SANCTUM_CELL0, SANCTUM_MASK, salt=18,
                              jag=True)
    items = cave.build(items, 18) + temple
    items = cave.underlay(items)
    # After the closure, which rebuilds every generated item in its box from
    # the mask: the skull and the outline would be dropped as rock-cell
    # clutter otherwise.
    items.append(MapItem(
        x=SKULL_POS[0], y=SKULL_POS[1], z=SKULL_POS[2],
        shape=SHAPE_SKULL_LOOSE, frame=0, npcnum=NPCNUM_MONSKUL
    ))
    items.extend(sanctum_outline())
    return items


def sanctum_outline():
    """The old sanctum rectangle's outline in retail's invisible wall
    (497/498, SI_EDITOR: solid, never drawn), three 48-unit courses, 144
    tall: the shoulders y=6175 (x 1024..2048 and 4096..5120), x=1024,
    x=5119 and the south line y=9343. See build_sanctum_gate_hardening."""
    items = []
    x0, y0, x1, y1 = SANCTUM_BOX
    for z in (0, 48, 96):
        for xa, xb in ((x0, 2048), (4096, x1)):            # shoulders
            for x in range(xa + 127, xb, 128):
                items.append(MapItem.placed_item(x, 6175, z,
                                                 SHAPE_BLOCKER_X, 0))
        for x in range(x0 + 127, x1, 128):                 # south
            items.append(MapItem.placed_item(x, y1 - 1, z,
                                             SHAPE_BLOCKER_X, 0))
        for y in range(y0 + 127, y1, 128):                 # west, east
            items.append(MapItem.placed_item(x0 + 31, y, z,
                                             SHAPE_BLOCKER_Y, 0))
            items.append(MapItem.placed_item(x1 - 1, y, z,
                                             SHAPE_BLOCKER_Y, 0))
    return items


def build_temple_entry_egg():
    """EGGTEMPLEENTRY — the `templeOpen` writer (DD-005), and the piece the
    1994 team never wrote. Placed immediately SOUTH of the Tiny Tar crack,
    on the sanctum side: the only way to stand here is to have squeezed
    through, so the egg does not gate anything, it just records the fact
    for the six NPCs whose dialogue waits on the flag.

    quality 305 -> class 1456 (lv-new/TEMPLENT.UNK, manifest-pinned).
    npcnum 0x84 = x +/-256, y +/-128. The y range is wide enough that
    dropping out of the crack crosses it, tight enough that it cannot fire
    from the hall side of the wall (the crack itself is at x 2848-2879,
    y 6112-6143). The x range was +/-128 until the breach (2026-09-26):
    a full-size player walking in through the doorway at x 2688..2943
    must cross it too, because it re-applies the freed gods' frames.
    Not 0x64 (+/-192): range bytes 100-116 fall in the engine's Actor
    promotion window, which test_engine_patch pins to two known eggs."""
    return [MapItem(
        x=2864, y=6144 + 96, z=0,
        shape=SHAPE_PLACEHOLDER_INVISIBLE_EGG, frame=0,
        quality=305, npcnum=0x84  # EggTempleEntry 1456
    )]


def build_sanctum_gate_hardening():
    """Make the Inner Sanctum's boundary hold against JUMPING and against
    the z=0 void walk — the two bypasses the 2026-07-31 playtest proved.

    THE GATE WAS BROKEN THREE WAYS (docs/playtest-2026-07-31-gates-climb-
    corridors.md, test A):

      1. CLIMB. The engine auto-tries Animation::climb72..climb16 on jump
         (u8_avatar_mover_process.cpp), and every wall on the sanctum
         boundary was ONE course = 40 tall with a bare standable top. The
         full-size Avatar climbed the crack wall on the first jump at
         (2576,6108) and again at (2976,6108), walked into the sanctum,
         and `templeOpen` went 0→1 with no potion and no shrink.
      2. WALL-TOP WALKWAYS. The Transition Hall's own side walls (40 tall,
         continuous) meet the boundary corner, so any climbable 40-top is
         an elevated path onto any other 40-top it touches.
      3. THE VOID. The engine supports any unblocked position at z<=0
         (current_map.cpp:773), so the void outside a map is WALKABLE; the
         playtest Avatar left the sanctum through a south doorway into it
         at (2815,9189).

    The west side and keyed breach pier retain three masonry courses.
    The east side and remaining crack line keep their ground course, with
    invisible 48-tall blockers at z 40 and 88. Their top at 136 exceeds
    the adjacent relief top at 46 and the 72-unit climb. The crack
    aperture itself is untouched: its clear span is x 2817..2879 at
    z 0..40, and the courses above it start at z=40, which the 32-tall
    shrunken Avatar passes under with 8 units of headroom — verified by
    test_crack_geometry.py and test_route_reach.py.

    Since 2026-10-17 the sanctum is a cave (screen04), closed by its own
    shell, and the rest of the old rectangle is rock. Its outline, the
    shoulders y=6175 (x 1024..2048 and 4096..5120), x=1024, x=5119 and
    the south line y=9343, is held by retail's invisible wall (497/498,
    SI_EDITOR, never drawn) three 48-unit courses high, 144: whatever the
    cave does inside it, nothing walks or climbs out into the void, and no
    temple masonry stands in the cave's black.
    """
    items = []
    for z in (40, 80):
        # The west wall faces away from the hall and keeps its masonry.
        items.extend(wall_run_y(4608, 6144, 2048, WALL_NS,
                                frame=WALL_PLAIN, z=z))
        # The six keyed breach records retain their shape, frame, and box.
        for x, bz, shape in sorted(BREACH_PIECES):
            if bz == z:
                items.append(MapItem.placed_item(x, BREACH_Y, z, shape,
                                                 WALL_PLAIN))
    for z in (40, 88):
        for x in range(2175, 4096, 128):
            if x not in (2815, 2943):
                items.append(MapItem.placed_item(x, BREACH_Y, z,
                                                 SHAPE_BLOCKER_X, 0))
        items.extend(wall_run_y(4608, 6144, 4095, SHAPE_BLOCKER_Y,
                                frame=0, z=z))
    return items


def sanctum_backfill(shot):
    """Paint rock crests and their backing outside screen04's window."""
    cave = cave_vignette.Cave(shot, SANCTUM_CELL0, SANCTUM_MASK,
                              salt=18, jag=True)
    items = []
    floor_cells = {k for k in cave.cells if cave.floor128(k)}
    for cx, cy in sorted(cave.cells - floor_cells):
        # Preserve the recessed island lip that keeps the fork visible.
        if 21 <= cx <= 23 and 56 <= cy <= 58:
            continue
        if not any((cx + dx, cy + dy) in floor_cells
                   for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))):
            continue
        top = MapItem.placed_item(cx * 128 + 127, cy * 128 + 127, 48,
                                  cave_vignette.ROCK_FLOOR,
                                  (cx + 3 * cy) % 7)
        if not shot.paints_window(top, p=cave_vignette.built_painter()):
            items.append(top)
        else:
            backing = MapItem.placed_item(cx * 128 + 127,
                                          cy * 128 + 127, 0,
                                          SHAPE_CAVE_BACKDROP_SMALL,
                                          (cx + 3 * cy) % 29)
            if not shot.paints_window(backing, p=cave_vignette.built_painter()):
                items.append(backing)
    return items


def west_passage_backdrop(items):
    """Preserve the west island's collision and its screen04 projection."""
    out = []
    found = 0
    for it in items:
        if (it.shape, it.x, it.y, it.z) == (566, 2943, 7551, 48):
            # Two overlapping invisible strips have the original 192x32
            # union, at the original height. The decorative clone keeps
            # 566's box dimensions; its shifted anchor compensates the
            # new position so its pixels remain on the original view ray.
            out.extend(MapItem.placed_item(x, it.y, it.z, 497, 0)
                       for x in (2879, 2943))
            out.append(MapItem.placed_item(2623, 7231, 0,
                                           SHAPE_SANCTUM_BACKDROP, it.frame))
            found += 1
        elif (it.shape == 301 and it.y == 7551
              and (it.x, it.z) in ((2815, 48), (2943, 56), (3071, 72))):
            # These inaccessible caps have no visible screen04 pixels.
            # Retain each 128x128 support box with retail's editor plate.
            it.shape, it.frame = 763, 0
            out.append(it)
        else:
            out.append(it)
    if found != 1:
        raise ValueError(f'west sanctum passage: expected one 566, got {found}')
    return out




def mountain_back():
    """Two cliff courses and one continuous crest behind the forecourt."""
    cliffs = []
    # The masonry stands 64 units in front of the mountain face.
    for x in range(2175, 4096, 128):
        for z in (0, 48):
            cliffs.append(MapItem.placed_item(
                x, 448, z, 26, random.Random(f"18:north:{x}:{z}").randrange(7)))
        cliffs.append(MapItem.placed_item(
            x, 448, 96, 125, random.Random(f"18:north-crest:{x}").randrange(7)))
    for y in range(639, 2560, 128):
        for z in (0, 48):
            cliffs.append(MapItem.placed_item(
                1984, y, z, 32, random.Random(f"18:west:{y}:{z}").randrange(7)))
        cliffs.append(MapItem.placed_item(
            1984, y, 96, 125, random.Random(f"18:west-crest:{y}").randrange(7)))
    for z in (0, 48):
        cliffs.extend((MapItem.placed_item(2047, 448, z, 28, 0),
                       MapItem.placed_item(1984, 511, z, 30, 0),
                       MapItem.placed_item(1984, 448, z, 29, 0)))
    cliffs.append(MapItem.placed_item(1984, 448, 96, 125, 12))

    return cliffs


def north_void_backing():
    """Paint the off-map north view without negative FIXED coordinates.

    Offsets of 1008 in x, 1009 in y, and 252 in z preserve the
    negative-y screen position under the engine's truncating division.
    These zero-height black plates cover y=-1024..-1; normal void coverage
    handles the positive map. Keeping them after coverage avoids counting
    their translated footprints as coverage of the positive ground.
    """
    return [MapItem.placed_item(x + 1008, y + 1009, 252, 564, 2)
            for x in range(255, 6144, 256) for y in (-1, -257, -513, -769)]

def dressed_floors(items):
    """Cold stone borders frame each nave; rough paving marks the forecourt."""
    globs = GlobReader()
    out = []
    for it in items:
        if it.is_glob_egg and it.quality == cave_vignette.GLOB_ROCK_FLOOR:
            out.extend(globs.glob_to_items(it.quality, it.x, it.y, it.z))
            continue
        if not it.is_glob_egg or it.quality != GLOB_FLAGSTONE_FLOOR:
            out.append(it)
            continue
        for tile in globs.glob_to_items(it.quality, it.x, it.y, it.z):
            x, y = tile.x, tile.y
            if y < 2560:
                # A broad flagstone approach connects the pad and the gate.
                tile.shape = 35 if 2816 <= x <= 3327 else 71
            elif y < 4608:
                tile.shape = 71 if x < 1792 or x >= 4352 or y < 2816 or y >= 4352 else 35
            else:
                tile.shape = 71 if x < 2304 or x >= 3840 or y < 4864 else 35
            tile.frame = random.Random(f"18:paving:{x}:{y}").choice((0, 1) if tile.shape == 35 else (0, 1, 2))
            out.append(tile)
    shot_windows = lv_dressing.shot_windows(18)
    sorter = ItemSorter()
    gravel_rows = {
        48: (19, 25), 49: (19, 25), 50: (18, 26), 51: (18, 26), 52: (18, 26),
        53: (18, 26), 54: (18, 27), 55: (18, 27),
        65: (18, 20), 66: (19, 21),
        67: (19, 22), 68: (20, 26), 69: (20, 26), 70: (21, 26), 71: (22, 25),
    }
    for tile in out:
        cx, cy = tile.x // 128, tile.y // 128
        span = gravel_rows.get(cy)
        if (tile.shape == 301 and tile.z == 0 and span and span[0] <= cx <= span[1]
                and not lv_dressing.paints_window(tile, sorter, shot_windows)):
            tile.shape, tile.frame = 6, random.Random(f"18:gravel:{cx}:{cy}:grain50").randrange(3)
        elif tile.shape == 301 and tile.z == 0 and not lv_dressing.paints_window(tile, sorter, shot_windows):
            tile.frame = random.Random(f"18:cave-floor:{cx}:{cy}").randrange(7)
    return out


def dress_temple(items):
    """Four authored focal groups with protected footprints."""
    site = lv_dressing.Site(18, dressed_floors(items), load_typeflag(), seed=4018)
    pieces = {
        'gate wardens': [
            (2783, 895, 0, 38, 0), (3423, 895, 0, 38, 1),
        ],
        'broken votive screen': [
            (2527, 3007, 0, 38, 2), (2719, 3039, 0, 38, 3),
            (2623, 2959, 0, SHAPE_URN, 0),
            (2591, 3135, 0, 465, 8), (2687, 3167, 0, 465, 2),
        ],
        'fallen arch': [
            (3487, 5343, 0, 46, 0), (3584, 5439, 0, 47, 0),
            (3455, 5471, 0, 465, 3), (3551, 5535, 0, 465, 12),
        ],
        'priestess memorial': [
            (2591, 8671, 0, 38, 2), (2527, 8799, 0, 465, 4),
            (2623, 8735, 0, 465, 13),
        ],
    }
    # Debris follows the drain, bench feet, and the failing arch in uneven fans.
    debris = {
        'gate wardens': (
            (2239, 959, 3), (2303, 1023, 8), (2175, 1087, 12), (2271, 1151, 1),
            (3871, 1119, 5), (3935, 1215, 11), (3807, 1279, 2), (3903, 1311, 15),
            (2335, 2207, 7), (2239, 2271, 4), (2303, 2367, 13), (2431, 2303, 9)),
        'broken votive screen': (
            (1887, 3263, 4), (1983, 3295, 10), (1919, 3391, 1), (2047, 3455, 14),
            (4351, 2815, 8), (4447, 2879, 12), (4383, 2975, 3), (4511, 3007, 6),
            (2495, 4287, 2), (2559, 4351, 13), (2463, 4415, 7), (2591, 4479, 16)),
        'fallen arch': (
            (2303, 4959, 8), (2399, 4991, 2), (2271, 5087, 15), (2399, 5183, 3),
            (3743, 4927, 9), (3839, 5023, 4), (3679, 5087, 12), (3807, 5215, 6)),
    }
    for name, rows in debris.items():
        pieces[name].extend((x, y, 0, 465, frame) for x, y, frame in rows)
    pieces['fallen arch'].extend((
        (3103, 5471, 0, 526, 7), (3039, 5599, 0, 526, 2),
        (3167, 5663, 0, 526, 8)))
    for name, rows in pieces.items():
        site.set_piece(name, [MapItem.placed_item(*row) for row in rows])
    site.set_piece('west-wall fungus', [MapItem.placed_item(*row) for row in (
        (2431, 6783, 0, 65, 0), (2527, 6879, 0, 65, 1),
        (2399, 6943, 0, 65, 0), (2527, 7039, 0, 65, 1),
        (2431, 7103, 0, 65, 0))])
    site.set_piece('fallen breach masonry', [MapItem.placed_item(*row) for row in (
        (3263, 6655, 0, 46, 0), (3328, 6719, 0, 47, 0),
        (3295, 6815, 0, 465, 6), (3391, 6879, 0, 465, 11),
        (3327, 6975, 0, 465, 1))])
    return site.pack()

def build_map_18():
    """Build complete Map 18 item list."""
    items = []
    items.extend(build_temple_exterior())
    items.extend(build_outer_hall())
    items.extend(build_transition_hall())
    items.extend(build_temple_entry_egg())
    items.extend(build_sanctum_gate_hardening())
    items.extend(build_breach_rubble())
    items = accent_reliefs(items, RELIEF_LINES)
    # After the reliefs, which rewrite wall frames: the tag goes on the
    # records that ship.
    items = tag_breach(items)
    items = build_inner_sanctum(items)
    # The inaccessible crest must not count as ground for void coverage:
    # its raised tiles would suppress the black backing below its faces,
    # leaving 160 unpainted pixels when the frame is not cleared.
    shot = cave_vignette.Shot(SCREEN04, art_map=SCREEN04_ART)
    items.extend(mountain_back())
    ground = items.copy()
    items.extend(sanctum_island(
        cave_vignette.Shot(SCREEN04, art_map=SCREEN04_ART)))
    # The void floor: black plates under every void cell within view of a
    # floor — the engine never clears the frame without `usehighres`
    # (.claude/rules/map-geometry.md). Last, after every walkable floor.
    # The cave's loose 301 is SI_DRAW like the 564 plate, so inside
    # the sanctum box this is lv_cave_vignette's cover, which swaps a plate
    # over such a tile for cell-sized black tiles; outside it, plates only.
    cover = cave_vignette.void_cover(ground, within=SANCTUM_BOX)
    shot = cave_vignette.Shot(SCREEN04, art_map=SCREEN04_ART)
    tops = sanctum_backfill(shot)
    # Retain the original backing under the raised rock, then close the
    # extra view cells seeded by its new LAND tops.
    cover.extend(cave_vignette.void_cover(ground + cover + tops,
                                         within=SANCTUM_BOX))
    items.extend(cover)
    items.extend(tops)
    # D3: the black backing defines the mountain beyond the rooms.
    items = west_passage_backdrop(items)
    # Repaint the former caps beneath the actor. Binary masks exclude
    # screen04 while the editor plates retain every original support box.
    items.extend(MapItem.placed_item(*clip['at'], 0,
                                     SHAPE_CAVE_BACKDROP_LARGE, 7 + n)
                 for n, clip in enumerate(CAVE_BACKDROP_CLIPS)
                 if clip['map'] == 18)
    items.extend(north_void_backing())
    return dress_temple(items)


if __name__ == '__main__':
    items = build_map_18()
    globs = sum(1 for i in items if i.is_glob_egg)
    teles = sum(1 for i in items if i.is_teleport_egg)
    mons = sum(1 for i in items if i.is_monster_egg)
    print(f"Map 18: {len(items)} items")
    print(f"  Glob eggs: {globs}")
    print(f"  Teleport eggs: {teles}")
    print(f"  Monster eggs: {mons}")
    print(f"  Other items: {len(items) - globs - teles - mons}")

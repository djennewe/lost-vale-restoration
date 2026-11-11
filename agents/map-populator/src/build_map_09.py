#!/usr/bin/env python3
"""
build_map_09.py — Map 9: Beyond Double Doors / Galjeron's Chamber

Small interior map connecting Bonecrusher's Cave (Map 8) to the Elemental
Dungeon (Map 11). The player's first step into the expansion.

Layout: 8x8 chunks (4096x4096 world units)
  - Guardian chamber (north): the 1994 screen10 tomb dais, closed into a
            cave (GUARDIAN_MASK) with a north-west passage to trigger 200
            (2026-10-17; it replaced zone 1, the straight throat)
  - Zone 2: Main chamber (4x4 chunks) — Galjeron's body, journal, the lair
  - Zone 3: Deeper passage (2x3 chunks) — cave giving way to worked stone,
            on to Map 11

REBUILT 2026-09-15 (cleanup plan, docs/reviews/2026-09-14-map-cleanup-plan.md
§3): the three zones had one ceiling tile per 512-unit chunk (26 floating
squares), six wall reliefs standing loose on the floor, two rock slabs
floating at z=4 as "carved walls", and a north shoulder open to the void.
Now: no ceilings (see the note above cave_run_x), the cavern's walls two courses tall with a lintel over each
opening, the lair dressed as a lair, and the last stretch of the deeper
passage built in the Zealan masons' stone (10/15 with carved faces, two
columns) so the Elemental Dungeon is announced before the teleporter.
Every pinned object — four teleport eggs, the body, the journal, the pack,
the sword, the guardian egg — is where it was.
"""

import sys
import os
import random
from pathlib import Path
import lv_dressing
from parse_typeflag import load_typeflag
sys.path.insert(0, os.path.dirname(__file__))

from u8_map import MapItem, generate_terrain_grid, wall_run_x, wall_run_y
from lv_monster_eggs import monster_group
from lv_furnish import column, accent_reliefs, WALL_NS, WALL_EW, WALL_PLAIN
import lv_cave_vignette as cave_vignette
from lv_shapes import (
    SHAPE_CLIFF_TOP,
    SHAPE_BLOCKER_X,
    SHAPE_BLOCKER_Y,
    SHAPE_CAVE_WALL_E,
    SHAPE_CAVE_WALL_S,
    SHAPE_BOOK_CLOSED,
    SHAPE_BACKPACK,
    SHAPE_LONGSWORD,
    SHAPE_BONES_A,
    SHAPE_BONES_B,
    SHAPE_NPC_GUARD_ARMORED,
    SHAPE_MON_LAIR_GUARDIAN,
    SHAPE_BOULDER_PILE,
)


# === CONSTANTS ===

# Map origin — place content in the center of the map space
MAP_X_START = 12288  # chunk 24
MAP_Y_START = 12288  # chunk 24

# Glob indices for terrain
# 2026-10-17: 397 (16x shape 301, retail's grey cave rock, f0-6), the floor
# every 1994 interior shot shows, screen10 here pixel for pixel. Was 45, a
# shape-242 cobble with moss.
GLOB_CAVE_FLOOR = cave_vignette.GLOB_ROCK_FLOOR

# The cave wall pair: 26 long in x (east-west runs), 32 long in y
# (north-south runs), 48 tall, both with a set of rock-texture frames.
# Runs cycle through the first four so a wall is not one tile repeated.
CAVE_FRAMES = (0, 1, 2, 3)
CAVE_COURSE = 48          # one course of 26/32


def cave_run_x(x0, x1, y, z=0, gaps=()):
    items = wall_run_x(x0, x1, y, SHAPE_CAVE_WALL_E, frame=0, z=z, gaps=gaps)
    for i, it in enumerate(items):
        it.frame = CAVE_FRAMES[i % len(CAVE_FRAMES)]
    return items


def cave_run_y(y0, y1, x, z=0, gaps=()):
    items = wall_run_y(y0, y1, x, SHAPE_CAVE_WALL_S, frame=0, z=z, gaps=gaps)
    for i, it in enumerate(items):
        it.frame = CAVE_FRAMES[(i + 2) % len(CAVE_FRAMES)]
    return items


# NO CEILINGS. A continuous SHAPE_CAVE_CEILING_B (37) roof at z=48 was tried
# over the two passages on 2026-09-15: in-engine the tiles over the far end
# of the passage kept drawing while the Avatar stood inside it (findRoof
# hides only the tiles about him), so the roof read as a pale slab lying on
# the walls, and 34 draws as a red tiled roof. Bonecrusher's cave next door
# has no ceiling at all — rock walls against the black — and that is the
# idiom this map follows now. (Before that: one tile per chunk, 26 squares.)


def build_guardian_chamber():
    """The guardian chamber, north of the hall: the 1994 screen10 (a
    tomb-kit dais with claw statues, ghouls, a body on the altar) placed by
    place_screen10 below, and the two Map 8 gateway eggs.

    Until 2026-10-17 this was zone 1, a straight 1024-wide throat with
    the return trigger at its north end. The shot's window covers that
    throat, so the throat's floor, walls and dressing are gone: the
    chamber's floor and rock are the shot plus GUARDIAN_MASK."""
    items = []
    # Teleport TRIGGER (ID 200) — back to Map 8 (Plateau double doors).
    # MOVED 2026-10-17 from (14336, 12416), the north end of the old
    # throat: that spot is now the strip between the dais and the
    # chamber's north wall, and its hatch box (npcNum 0xC8, +/-384 x
    # +/-256) covered the dais's back half — anyone walking round the
    # altar went home. It stands now at the head of the passage that
    # leaves the chamber north-west (the floor screen10 shows at its top
    # left, behind the wall), so the box holds that passage and nothing
    # of the chamber: x 13375..13887 (+64), y 11775..12351 (+64).
    # SWAPPED 2026-07-31: the 07-25 relocation comments were written under
    # the pre-771d5c7 inverted helper names, so the ACTIVE trigger had been
    # built on the quest egress line (the playtest C1 bounce class). Ids and
    # roles unchanged; positions exchanged. See build_map_13's base pair.
    items.append(MapItem.teleporter(
        x=TRIGGER_200[0], y=TRIGGER_200[1], z=0,
        teleport_id=200, dest_npc=200, dest_map=8
    ))

    # ARRIVAL pad (ID 201) — where Map 8's trigger 201 delivers. Out of
    # the throat since 2026-10-10 (was (x0+512, y0+512), 64 units south of
    # trigger 200's hatch box): Map 8's trigger is walked into heading
    # north, through the doors, and the Avatar arrives still walking
    # north. With the key held he walked straight back into that box and
    # on to Map 8 — the arrival-corridor bounce
    # (test_route_reach.arrival_corridors). Here, in the hall, his
    # northbound line ends on the rock between the hall and the guardian
    # chamber (GUARDIAN_MASK row 103), and the quest line leaves south
    # down the hall.
    items.append(MapItem.teleport_target(
        x=MAP_X_START + 1408, y=MAP_Y_START + 1920, z=0,
        teleport_id=201
    ))
    return items


# ── screen10, the guardian dais (2026-10-17) ─────────────────────────────
# docs/research/2026-10-16-screenshot-reconstruction.md; the vignette is
# vignettes/screen10.json, origin (12928, 11520).
#
# THE DAIS TOP IS z 56, from the tomb kit's own heights: the east face is
# three relief panels 246/247/249 (40 tall) on x 14432..14463, y
# 12544..12799, and the arcade slabs 240 (16 tall) sit on panels, so the
# top is 40 + 16. The reconstruction solved every piece for the pixels at
# z 0/24/48; an item at (x, y, z) draws exactly where (x+4h, y+4h, z+h)
# does (lv_cave_vignette.relift), so each piece the shot shows on the
# dais goes up onto it with not one pixel moved: the three slabs to z 40
# on the panel line, the altar block 206 and the arms and blood on it to
# the top, the blood runs 421/457 onto the east and south faces, and the
# three top steps 107/101/100 down to the floor in front of the south
# face. The Avatar the shot shows on the dais stands at (14360, 12792,
# 56). The rest of the dais's volume and the stair's treads are invisible
# SI_EDITOR flats (dais_skeleton) so the dais is solid and climbable as
# drawn.
SCREEN10_RELIFT = {
    (240, 2, 14175, 12639, 0): 40, (240, 5, 14495, 12703, 48): -8,
    (240, 1, 14495, 12831, 48): -8, (421, 1, 14495, 12831, 48): -8,
    (457, 0, 14495, 12895, 48): -24, (457, 0, 14527, 12895, 48): -24,
    (206, 0, 14175, 12479, 0): 56, (332, 2, 14175, 12511, 24): 56,
    (484, 1, 14175, 12511, 24): 56, (782, 10, 14144, 12380, 0): 56,
    (107, 0, 14527, 12927, 24): -24, (101, 0, 14527, 12959, 24): -24,
    (100, 0, 14527, 12991, 24): -24,
}
DAIS_TOP = 56
DAIS_X = (14208, 14463)          # inclusive world extents of the top
DAIS_Y = (12544, 12799)
STAIR_X = 14463                  # the stair's treads, max-corner x (128 wide)
INVISIBLE_FLAT = 747             # 128x128x8 SI_EDITOR, SOLID only (474,
                                 # the same box, is SEA: water to the knock-
                                 # back check, test_monster_eggs)
INVISIBLE_LAND = 797             # 128x128x0 SI_EDITOR SOLID|LAND: what a
                                 # body stands on (exact_reach /
                                 # getPositionInfo); 636, the same box, is
                                 # SI_DAMAGING
# The stair's tread tops, row by row south of the dais (each 32 deep, keyed
# by the row's max y). Every top is at least the drawn step block's in
# that row — 107 (48), 101 (40), 100 (32) relifted, the two 112s (16) the
# shot leaves at z 0 — and none rises more than 8 over the row below, the
# engine's step. The 112 at the foot (row 13023) is why the stair ends in
# a three-row landing at 16 and one tread of 8 rather than six even steps.
STAIR_TOPS = {12831: 48, 12863: 40, 12895: 32, 12927: 24, 12959: 16,
              12991: 16, 13023: 16, 13055: 8}


def dais_skeleton():
    """The dais's invisible body and stair: 747 flats 8 a layer for the
    volume, a 797 land flat on each top a body stands on."""
    items = []
    for cx in (DAIS_X[0] + 127, DAIS_X[1]):
        for cy in (DAIS_Y[0] + 127, DAIS_Y[1]):
            # under the 240 slabs (z 40) to 40; the slab-less cell the
            # altar stands on to the top
            top = DAIS_TOP if (cx, cy) == (DAIS_X[0] + 127, DAIS_Y[0] + 127) \
                else 40
            for z in range(0, top, 8):
                items.append(MapItem.placed_item(cx, cy, z, INVISIBLE_FLAT, 0))
            items.append(MapItem.placed_item(cx, cy, DAIS_TOP, INVISIBLE_LAND, 0))
    # Each layer z covers every row whose top is above z, from the dais
    # edge south, with 128-deep flats ending on that run's last row (an
    # overlap northward lands on rows at least as high).
    for z in range(0, DAIS_TOP - 8, 8):
        end = max(y for y, top in STAIR_TOPS.items() if top > z)
        while end > DAIS_Y[1]:
            items.append(MapItem.placed_item(STAIR_X, end, z, INVISIBLE_FLAT, 0))
            end -= 128
    # One land flat per tread height, ending on the southernmost row of
    # that height (rows of one height are contiguous; the rows it reaches
    # north of them are higher and stand on their own).
    for top in sorted(set(STAIR_TOPS.values())):
        end = max(y for y, t in STAIR_TOPS.items() if t == top)
        items.append(MapItem.placed_item(STAIR_X, end, top, INVISIBLE_LAND, 0))
    return items


# The cave the shot is closed into, columns 100..117 (x 12800..15103),
# rows 90..103 (y 11520..13311); '?' and every cell the window decides
# follow the shot. The chamber is the shot's floor, a west bay (cols
# 102..106), and the passage the shot shows at its top left going on
# north-west to trigger 200; the south opening (cols 110..112, row 103)
# is the way down to the hall. Row 103 west of it is the rock pad 201's
# northbound line ends on.
GUARDIAN_MASK_CELL0 = (100, 90)
GUARDIAN_MASK = [
    '##################',   # 90
    '##################',   # 91
    '######..##########',   # 92
    '#####...##########',   # 93
    '#####....#########',   # 94
    '#####....#########',   # 95
    '#####...??########',   # 96
    '###............###',   # 97
    '##..............##',   # 98
    '##.............###',   # 99
    '###.............##',   # 100
    '####...........###',   # 101
    '####.........#####',   # 102
    '##########......##',   # 103
]
TRIGGER_200 = (13759, 12031)
# Three of the shot's items are all-black frames the decomposer matched to
# the black right of the dais: 735 f0 twice (a 320-wide SF_QUALITY flat)
# and 411 f178 (an SF_CONTAINER). The void there paints the same black, so
# they buy the window nothing it keeps (88.31 -> 88.07%, all from pixels
# they hid), and a quality flat and a container standing in the rock read
# to map_validate as quest pieces on a black floor. Left out.
SCREEN10_BLACK_FILLERS = ((735, 0, 14744, 12604, 0), (735, 0, 14692, 12968, 0),
                          (411, 178, 14720, 12556, 0))


def place_screen10(items):
    """Stamp screen10, put the dais pieces on the dais, close the cave."""
    items, shot = cave_vignette.stamp(items, 'screen10', 9)
    items = shot.drop(items, SCREEN10_BLACK_FILLERS)
    shot.relift(items, SCREEN10_RELIFT)
    cave = cave_vignette.Cave(shot, GUARDIAN_MASK_CELL0, GUARDIAN_MASK)
    items = cave.build(items, 9)
    items += dais_skeleton()
    # Elevated crests cover XY cells without painting their ground-level
    # projection. Keep the original plates and all 30 screen10 edge tiles
    # beneath them so low-resolution play repaints every opening.
    ground_cover = cave_vignette.void_cover(items)
    return guardian_shell_tops(items, cave) + ground_cover



def guardian_shell_tops(items, cave):
    """Cap the guardian shell and replace its convex corner strips with posts."""
    cell = cave_vignette.CELL
    rock = {k for k in cave.cells if k not in cave.floor_cells
            and not cave.windowed(k)}
    shell_keys = {cave_vignette._key(it) for it in cave.shell(cave.floor_cells)}
    corners = {((cx + 1) * cell - 1, (cy + 1) * cell - 1)
               for cx, cy in rock
               if cave.floor128((cx + 1, cy)) and cave.floor128((cx, cy + 1))}
    # The south face owns the final 32-unit corner strip. Shortening that
    # piece makes room for the post without overlapping solid boxes.
    widths = {shape: width for width, shape in cave_vignette.WALL_X.items()}
    out = []
    for it in items:
        if (it.x, it.y) in corners and it.shape in widths and \
                cave_vignette._key(it) in shell_keys:
            width = widths[it.shape] - 32
            short = cave._piece(cave_vignette.WALL_X.get(width, cave_vignette.POST),
                                it.x - 32, it.y, it.z)
            post = cave._piece(cave_vignette.POST, it.x, it.y, it.z)
            if not any(cave.sh.paints_window(t) for t in (short, post)):
                out.extend((short, post))
                continue
        out.append(it)
    # Interior rock tops are clipped individually from the protected shot.
    # Five convex gaps use flat rock at the same 104-unit top as the caps.
    for cx, cy in sorted(rock):
        # The south shelf would hide the floor behind its invisible faces.
        if cy == 103 and 105 <= cx <= 109:
            continue
        crest = MapItem.placed_item((cx + 1) * cell - 1, (cy + 1) * cell - 1,
                                    2 * CAVE_COURSE, SHAPE_CLIFF_TOP,
                                    (12, 13, 14)[(cx + cy) % 3])
        if cave.floor128((cx, cy - 1)) or cave.floor128((cx - 1, cy)):
            crest.shape, crest.frame, crest.z = 301, 0, 104
        if not cave.sh.paints_window(crest):
            out.append(crest)
    return out


def build_zone_2_chamber():
    """Zone 2: Main chamber (4x4 chunks) with Galjeron's body."""
    items = []
    x0 = MAP_X_START + 512    # wider than the passage
    y0 = MAP_Y_START + 1024   # below the entry passage

    # Terrain floor (4x4 chunks)
    items.extend(generate_terrain_grid(x0, y0, 4, 4, GLOB_CAVE_FLOOR))

    # The cavern's walls are two courses (96) — the largest space on the
    # map, taller than the passages that lead into and out of it. Ground
    # course first.
    #
    # NORTH: the throat (zone 1) opens into this room over x0+1024..x0+2048,
    # and until 2026-09-15 the other half of the north edge, x0..x0+1024,
    # had NO wall — a floor edge onto the void, which is walkable in-engine
    # (current_map.cpp:773). Walled now; the upper course runs the whole
    # width as a lintel over the throat's opening.
    items.extend(cave_run_x(x0, x0 + 1024, y0))
    items.extend(cave_run_y(y0, y0 + 2048, x0))
    items.extend(cave_run_y(y0, y0 + 2048, x0 + 2047))

    # SOUTH: THE GAP IS LOAD-BEARING, and it is why this wall carries an
    # explicit doorway. This line sits exactly on the zone-2 / zone-3
    # boundary (y0+2047 = MAP_Y_START+3071, and zone 3 starts at
    # MAP_Y_START+3072), so it is the ONLY way south to the Elemental
    # Dungeon teleporter. Before the 2026-07-30 picket-fence sweep the wall
    # was 50% hole — four 128-long segments spread over 1024 units — and
    # that porosity WAS the passage. Making it solid sealed the map: the
    # exit trigger went unreachable and Map 9 became a dead end. Caught by
    # an Avatar-width flood, not by eye.
    #
    # The doorway is centred on zone 3, which spans x0+1024..x0+2048, so
    # the opening lines up with the passage it leads into rather than
    # sitting arbitrarily in the wall. The upper course is continuous over
    # it: a 48-unit-high lintel, and the Avatar is 40.
    items.extend(cave_run_x(x0, x0 + 2048, y0 + 2047,
                            gaps=[(x0 + 1408, x0 + 1664)]))

    # Far faces retain their upper course. Invisible near faces keep the
    # 96-unit barrier and the south doorway clear beneath its lintel.
    for z in (CAVE_COURSE,):
        items.extend(cave_run_x(x0, x0 + 2048, y0, z=z))
        items.extend(cave_run_y(y0, y0 + 2048, x0, z=z))
        items.extend(wall_run_y(y0, y0 + 2048, x0 + 2047, SHAPE_BLOCKER_Y, z=z))
        items.extend(wall_run_x(x0, x0 + 2048, y0 + 2047, SHAPE_BLOCKER_X, z=z))

    # No ceiling (sixteen squares floated over this room at z=48, one per
    # chunk); see the note above cave_run_x.

    # === GALJERON'S BODY ===
    # Dead NPC shape at center of chamber
    body_x = x0 + 1024
    body_y = y0 + 1024
    items.append(MapItem.placed_item(
        x=body_x, y=body_y, z=0,
        shape=SHAPE_NPC_GUARD_ARMORED, frame=146  # dead/prone frame
    ))

    # Galjeron's Journal (TypeBook) — next to body
    items.append(MapItem.placed_item(
        x=body_x + 64, y=body_y + 32, z=0,
        shape=SHAPE_BOOK_CLOSED, frame=6, quality=1  # brown book frame; quality triggers usecode read
    ))

    # Galjeron's backpack — near body
    items.append(MapItem.placed_item(
        x=body_x - 64, y=body_y + 64, z=0,
        shape=SHAPE_BACKPACK, frame=0
    ))

    # Old weapon near body
    items.append(MapItem.placed_item(
        x=body_x + 96, y=body_y - 32, z=0,
        shape=SHAPE_LONGSWORD, frame=0
    ))

    # === GUARDIAN CREATURE ===
    # The troll in the lair, and the MONEGG trigger at the lair's mouth
    # that hatches it (lv_monster_eggs: a shape-500 egg never hatches on
    # its own). Until 2026-10-11 the egg stood at (x0+1600, y0+512) with
    # no trigger, inside a lair boulder's box (shape 237), and never
    # hatched. Now it stands in the corner behind the spires, 1,176 units
    # off the line pad -> sword -> south door, so a player who keeps to
    # that line never hatches it; one who walks up to the lair meets it
    # about 540 units off. It fights on sight (activity 1).
    items.extend(monster_group(
        1, trigger=(x0 + 1408, y0 + 640, 0), box=(5, 5),
        eggs=[(x0 + 1920, y0 + 96, 0, SHAPE_MON_LAIR_GUARDIAN)]))

    # Bones lead from the north-east lair toward Galjeron. Its rubble
    # floor and the damp wall groups are authored in dress_cave.
    items.append(MapItem.placed_item(
        x=x0 + 1500, y=y0 + 300, z=0, shape=SHAPE_BONES_A, frame=0
    ))
    items.append(MapItem.placed_item(
        x=x0 + 1700, y=y0 + 400, z=0, shape=SHAPE_BONES_B, frame=0
    ))
    items.append(MapItem.placed_item(
        x=x0 + 1600, y=y0 + 700, z=0, shape=SHAPE_BONES_A, frame=0
    ))
    items.append(MapItem.placed_item(
        x=x0 + 1856, y=y0 + 224, z=0, shape=SHAPE_BONES_B, frame=1
    ))
    items.append(MapItem.placed_item(
        x=x0 + 1344, y=y0 + 864, z=0, shape=SHAPE_BONES_A, frame=1
    ))

    return items


def build_zone_3_passage():
    """Zone 3: Deeper passage (2x3 chunks) toward Elemental Dungeon."""
    items = []
    x0 = MAP_X_START + 1536  # same width as entry passage
    y0 = MAP_Y_START + 3072  # below the main chamber
    WORKED_Y = y0 + 768      # where the cave gives way to hewn stone

    # Terrain floor (2x3 chunks) — the chamber's glob; see GLOB_CAVE_FLOOR_B.
    items.extend(generate_terrain_grid(x0, y0, 2, 3, GLOB_CAVE_FLOOR))

    # The cave half: walls one course.
    items.extend(cave_run_y(y0, WORKED_Y, x0))
    items.extend(cave_run_y(y0, WORKED_Y, x0 + 1023))

    # The worked half: the Zealan masons' stone — the same pair the
    # temple is built from, two courses, carved faces set into the west
    # wall (the face this projection shows), and two columns flanking the
    # way to the teleporter. This is the design doc's "signs of ancient
    # construction"; it used to be two rock slabs floating at z=4.
    for z in (0, 40):
        items.extend(wall_run_y(WORKED_Y, y0 + 1536, x0, WALL_NS,
                                frame=WALL_PLAIN, z=z))
        items.extend(wall_run_y(WORKED_Y, y0 + 1536, x0 + 1023,
                                WALL_NS if z == 0 else SHAPE_BLOCKER_Y,
                                frame=WALL_PLAIN if z == 0 else 0, z=z))
        items.extend(wall_run_x(x0 - 1, x0 + 1023, y0 + 1535, WALL_EW,
                                frame=WALL_PLAIN, z=z))
    # Broken wall remnants mark the worked edge. Invisible replacements
    # retain the existing backstops while darkness surrounds the passage.
    for it in items:
        if it.shape == WALL_NS and it.y >= WORKED_Y:
            if it.x == x0 + 1023 or it.z > 0 or it.y < y0 + 1280:
                it.shape, it.frame = SHAPE_BLOCKER_Y, 0
        elif it.shape == WALL_EW:
            if it.x not in (x0 + 383, x0 + 511, x0 + 639) or it.z > 0:
                it.shape, it.frame = SHAPE_BLOCKER_X, 0
    # Continue the east backstop above the former 80-unit wall.
    items.extend(wall_run_y(WORKED_Y, y0 + 1536, x0 + 1023,
                            SHAPE_BLOCKER_Y, z=88))
    for it in items:
        if (it.shape, it.x, it.y, it.z) == (WALL_EW, 14335, 16895, 0):
            it.frame = 0
    items.extend(column(x0 + 192, y0 + 1152))
    items.extend(column(x0 + 832, y0 + 1152))

    # Teleport TRIGGER (ID 202) at far end -> Map 11 (Elemental Dungeon)
    # SWAPPED 2026-07-31: the 07-25 relocation comments were written under
    # the pre-771d5c7 inverted helper names, so the ACTIVE trigger had been
    # built on the quest egress line (the playtest C1 bounce class). Ids and
    # roles unchanged; positions exchanged. See build_map_13's base pair.
    # (pad pushed to y0+768, 2026-07-31: at y0+1016 it sat 32 outside
    # trigger 203's hatch box — one step south of arrival was a bounce.)
    items.append(MapItem.teleport_target(
        x=x0 + 512, y=y0 + 768, z=0,
        teleport_id=202
    ))

    # Teleport DEST (ID 203) for returns from Map 11. Moved north
    # 2026-07-04 (was y0+1200, 200 units from the onward trigger —
    # walking deeper after returning bounced you forward again).
    items.append(MapItem.teleporter(
        x=x0 + 512, y=y0 + 1400, z=0,
        teleport_id=203, dest_npc=203, dest_map=11
    ))

    # Floor debris in the cave half only — the masons kept theirs swept.
    items.append(MapItem.placed_item(x=x0 + 895, y=y0 + 511, z=0,
                                     shape=SHAPE_BOULDER_PILE, frame=2))

    return items


# Four-cell focal patch, using earth from 437 and transition frames from 455.
# Keys are existing floor max corners; all support boxes remain unchanged.
HALL_EARTH = {
    (13823, 14207): (386, 6), (13951, 14207): (386, 7),
    (13695, 14335): (386, 0), (13823, 14335): (4, 33),
    (13951, 14335): (4, 31), (14079, 14335): (386, 24),
    (13695, 14463): (386, 1), (13823, 14463): (4, 30),
    (13951, 14463): (4, 32), (14079, 14463): (386, 11),
    (13823, 14591): (386, 1), (13951, 14591): (386, 24),
}


def dress_cave(items):
    """Three authored focal groups, damp earth, and a broken stone threshold."""
    from glob_catalog import GlobReader
    globs = GlobReader()
    shaped = []
    for it in items:
        if it.is_glob_egg and it.quality == GLOB_CAVE_FLOOR and it.y >= 13312:
            tiles = globs.glob_to_items(it.quality, it.x, it.y, it.z)
            for tile in tiles:
                rng = random.Random(f'4009:floor:{tile.x}:{tile.y}')
                tile.frame = rng.randrange(7)
                if (tile.x, tile.y) in HALL_EARTH:
                    tile.shape, tile.frame = HALL_EARTH[tile.x, tile.y]
                elif tile.x >= 14464 and 13440 <= tile.y <= 13824:
                    tile.shape, tile.frame = 300, rng.choice((0, 1, 2))
                elif tile.y >= {13951: 16127, 14079: 16383, 14207: 16255,
                                14335: 16127, 14463: 16255, 14591: 16383,
                                14719: 16255, 14847: 16511}.get(tile.x, 16895):
                    tile.shape, tile.frame = 35, rng.choice((0, 1, 2, 3))
                elif (tile.x, tile.y) in {(13951, 15999), (14079, 16127),
                                         (14207, 16127), (14463, 16127),
                                         (14591, 16255), (14719, 16127)}:
                    tile.shape, tile.frame = 6, rng.randrange(6)
                shaped.append(tile)
        else:
            shaped.append(it)
    # These five mushrooms predate this slice and remain at their original spots.
    shaped.extend(MapItem.placed_item(x, y, 0, 65, frame) for x, y, frame in (
        (12960, 14016, 2), (13280, 14832, 9), (13952, 15200, 14),
        (14752, 14432, 5), (14024, 15560, 0)))
    shapes = load_typeflag(str(Path(__file__).resolve().parents[3] / 'shared/build/TYPEFLAG.DAT'))
    site = lv_dressing.Site(9, shaped, shapes, seed=4009)
    # Each tuple is an explicit world position chosen for this composition.
    pieces = {
        'Broken funerary vessels': (
            (13184, 12672, 229, 0), (13280, 12640, 526, 6),
            (13312, 12672, 465, 4), (13376, 12704, 465, 9)),
        'Fungus at the seep': (
            (13024, 14624, 65, 4), (13216, 14624, 65, 8),
            (13088, 14752, 465, 3), (13184, 14720, 526, 6),
            (12992, 14720, 526, 8)),
        'Masons abandoned threshold': (
            (13952, 16064, 526, 7), (14048, 16096, 526, 6),
            (14016, 16000, 465, 7), (14112, 16032, 465, 12),
            (14080, 15936, 322, 0),
            (14528, 15936, 526, 8), (14624, 16000, 526, 7),
            (14624, 16192, 465, 4), (14592, 16032, 465, 9),
            (14048, 16160, 465, 3), (14688, 16128, 553, 6)),
    }
    pieces['Broken funerary vessels'] += ((13311, 12799, 6, 0), (13439, 12799, 6, 1), (13567, 12927, 6, 2), (13392, 12736, 553, 2))
    wall_groups = {
        'Lair mouth scrape': ((13728, 13568, 152, 1), (13792, 13632, 553, 7), (13664, 13632, 322, 4)),
        'West drip roots': ((13376, 14912, 152, 1), (13088, 14016, 152, 1), (13184, 14144, 321, 0), (13184, 14080, 322, 1)),
        'South drift': ((13952, 15136, 322, 2), (13888, 15168, 321, 1), (13984, 15008, 526, 6)),
        'Lair debris': ((14592, 14176, 322, 3), (14656, 14272, 321, 2), (14528, 14240, 526, 8)),
        'North seep': ((13152, 13664, 65, 5), (13248, 13728, 526, 7),
                       (13216, 13824, 553, 4)),
        'South seep': ((13408, 15072, 65, 10), (13488, 15120, 526, 8),
                       (13392, 15200, 553, 1)),
        'East seep': ((14656, 14816, 65, 4), (14576, 14736, 526, 6),
                      (14640, 14656, 553, 6)),
    }
    # Pebbles connect the restored caps to the neighbouring wall debris.
    pieces['Fungus at the seep'] += (
        (13024, 13888, 553, 0), (13248, 13760, 465, 5),
        (14656, 14400, 465, 7), (14624, 14496, 553, 2),
        (14048, 15136, 465, 4), (13888, 15040, 553, 3),
        (14592, 14784, 465, 8))
    for rows in wall_groups.values():
        pieces['Fungus at the seep'] += rows
    for name, rows in pieces.items():
        site.set_piece(name, [MapItem.placed_item(x, y, 0, shape, frame)
                              for x, y, shape, frame in rows])
    # Keep this small map below 1,800 records without packing. The shared
    # glob writer collides with the compiler archive during pin derivation.
    # Protection keeps every authored record loose while pack records the
    # exclusions and set-piece ledger for the structural audit.
    site.protected_raw.update(id(it) for it in site.items)
    return site.pack()


def build_map_09():
    """Build complete Map 9 item list."""
    items = []
    items.extend(build_guardian_chamber())
    items.extend(build_zone_2_chamber())
    items.extend(build_zone_3_passage())
    # The worked passage's west wall is the one stone face this map shows.
    items = accent_reliefs(items, [('x', MAP_X_START + 1536)])
    # screen10 and the cave it closes into (2026-10-17). After everything
    # it cuts into, before the void.
    items = place_screen10(items)
    items = dress_cave(items)
    # The void floor (2026-09-16): black plates under every void cell within
    # view of a floor — the engine never clears the frame without
    # `usehighres` (.claude/rules/map-geometry.md, last section). Last, so
    # it sees every floor. cave_vignette.void_cover is lv_furnish.void_floor
    # with a 128 black tile wherever the 256 plate would lie under a loose
    # 301 tile (both are SI_DRAW, so the plate could draw over it).
    # VQ-001: screen10's black east edge excludes 301 in Cave.build;
    # these 35:10 tiles cover that excluded ground after the stamp. They
    # are absent from the vignette. Removing them leaves the same visible
    # black as unpainted pixels and breaks the protected window's score.
    items.extend(cave_vignette.void_cover(items))
    return items


if __name__ == '__main__':
    items = build_map_09()
    print(f"Map 9: {len(items)} items")
    globs = sum(1 for i in items if i.is_glob_egg)
    teles = sum(1 for i in items if i.is_teleport_egg)
    mons = sum(1 for i in items if i.is_monster_egg)
    print(f"  Glob eggs: {globs}")
    print(f"  Teleport eggs: {teles}")
    print(f"  Monster eggs: {mons}")
    print(f"  Other items: {len(items) - globs - teles - mons}")

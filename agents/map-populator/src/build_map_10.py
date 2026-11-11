#!/usr/bin/env python3
"""
build_map_10.py — Map 10: Lost Vale Overworld

Central hub map with 10 sub-zones, 16 NPCs, quest locations, and
connections to Maps 11, 13, and 18.

Layout: ~50x50 chunks (25,600x25,600 world units)

PHASE B, 2026-10-16/17 (docs/research/2026-10-16-screenshot-reconstruction/
phaseB/map10/REPORT.md). The ground is lv_map10_ground's Field (terrain
chunks, RELIEF tiers, the lake, STAIRS) in the 1994 materials, emitted by
lv_vale_terrain.Field: rock, earth and 386 edges, 125 crests, 26-32 faces
with a crest plate at the foot where the 48 courses stop above the ground,
crest-edged shore banks, invisible-wall barriers and lake rails. The eight
Map 10 screenshots (02, 09, 17, 18, 19, 20, 21, 22) are stamped verbatim
(stamp_shots), and then the shots are closed into the field: shot_closure
(hidden cells, seam faces under cut-off scarps), shot_completions (the
1994 huts, screen17's stair tail), stair_underfill, under_floors,
shot_supports, shot_rails and the shots' own lake rails, band_plates. The
zone builders below still place every NPC, quest item, egg and prop;
lift_props raises a prop onto a tier the field has raised.

Every pinned item (map_pins.json: eight teleports, NPC starts, the quest
items and event eggs) is where it was, except the moves the shots imply,
recorded in each vignette's placement.pin_moves. build_map_10() ends with
a check that no solid prop stands on a track and every track tile has
ground.

Zone coordinate assignments (from design doc):
  Entry:            (10240-15360, 1024-4096)     10x6 chunks
  Hoskuld Village:  (3072-8192, 5120-11264)      10x12 chunks
  Gunnar Village:   (17408-22528, 5120-11264)    10x12 chunks
  Ezrekal's:        (11264-14336, 11264-14336)   6x6 chunks
  Test Area:        (4096-8192, 15360-18432)      8x6 chunks
  The Lake:         (11264-15360, 15360-20480)    8x10 chunks
  Sacred Circle:    (18432-22528, 15360-18432)    8x6 chunks
  Cloud Approach:   (5120-9216, 20480-24576)      8x8 chunks
  Temple Approach:  (16384-20480, 20480-24576)    8x8 chunks
  Moriens Ruins:    (11264-14336, 21504-24576)    6x6 chunks
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from u8_map import MapItem
from building_prefab import REGISTRY as _PREFAB_LIST
from vignette_place import (stamp as stamp_vignette, load as load_vignette,
                            region as vignette_region,
                            world_items as vignette_items)
from lv_furnish import column, raised_platform, void_floor, WALL_EW, WALL_PLAIN
from lv_monster_eggs import monster_group
from lv_landscape import track, tile_run, span, cliff_run_y
from lv_map10_ground import (map10_field, paint_earth, load_pins, STAIRS,
                             stair_items, rails as lake_rails,
                             shot_closure, under_floors, shot_supports,
                             stair_underfill, shot_rails, band_plates,
                             plateau_cells, flush_edges, stair_cells, lake_banks, coast_banks)
from lv_hut1994 import complete_huts
from lv_vale_terrain import step_stair, stair_barriers, STEP_X
from lv_shapes import (
    SHAPE_PLAQUE_ON_Y_WALL, NPCNUM_GOLD_PLAQUE,
    SHAPE_GROUND_FLAT, SHAPE_GROUND_VARIANT_C, SHAPE_ROCK_SLAB_GROUND,
    SHAPE_MUSHROOM_CLUSTER, SHAPE_GRASS_PATCH_A, SHAPE_GRASS_PATCH_B,
    SHAPE_WATER_SURFACE_SMALL_B,
    SHAPE_WOOD_PLANK_WALL_SE, SHAPE_WOOD_PLANK_WALL_SW,
    SHAPE_WOOD_PLANK_CORNER_POST,
    SHAPE_LARGE_GATE, SHAPE_BONES_A, SHAPE_BONES_B, SHAPE_ROCK_SPIRE_CLUSTER,
    SHAPE_DESK, SHAPE_TABLE_WORKBENCH, SHAPE_CHEST_ORNATE,
    SHAPE_CAULDRON, SHAPE_BOTTLE_GREEN, SHAPE_WELL,
    SHAPE_TEST_PLANT, SHAPE_NPC_GUARD_ARMORED,
    SHAPE_GRAVEL, SHAPE_SLAB_PALE, SHAPE_ROCK_SLAB_CRACKED,
    SHAPE_STANDING_STONE, SHAPE_RUBBLE_PILE, SHAPE_RUBBLE_SMALL, SHAPE_SACRED_ROCK,
    SHAPE_STONE_SMALL, SHAPE_TREE_DEAD, SHAPE_TREE_TRUNK,
    SHAPE_TREE_STUMP_GREY, SHAPE_BUSH, SHAPE_COLUMN_RUIN_TALL,
    SHAPE_PILLAR_STONE, SHAPE_STONE_BROKEN,
    SHAPE_PLATFORM_FLAGSTONE, SHAPE_COLUMN_STONE,
    SHAPE_NPC_PEASANT_MALE, SHAPE_NPC_SEATED_CHARRED,
    SHAPE_NPC_PEASANT_SMALL, SHAPE_NPC_CHILD, SHAPE_NPC_SORCERER,
    SHAPE_ZEALAN_ELDER, SHAPE_SPEAR_CHILD_DARK, SHAPE_SPEAR_CHILD_BLOND,
    SHAPE_FLASK_ALCHEMICAL,
    SHAPE_PLACEHOLDER_INVISIBLE_EGG, SHAPE_KEY, SHAPE_CHEST_LOCKED, SHAPE_TRAP,
    SHAPE_PASSAGE_STONE, SHAPE_BOULDER_LARGE, SHAPE_SPECIAL_ROOT,
    SHAPE_MON_PROWLER, SHAPE_MON_WILDERNESS, SHAPE_MON_ZOMBIE,
    SHAPE_BLOCKER_X, SHAPE_BLOCKER_Y,
    SHAPE_ABACUS, SHAPE_BEDROLL, SHAPE_HAT, SHAPE_ROPE, SHAPE_POTION_REAL,
    NPCNUM_ABACUS, NPCNUM_BEDROLL, NPCNUM_FEDORA, NPCNUM_BULLWHIP,
    NPCNUM_POTION,
)
# EggReapply on every arrival pad (205, 212, 206, 210), 2026-10-10. The
# Test Plant EggPlantTest blows away (build_test_grounds) is a fixed record,
# and World::switchMap re-reads every fixed record on each entry, so it
# stood again after any trip off the map. The egg (lv-new/REAPPLY.UNK)
# destroys it again once `haveMark` is set, which the scene sets after the
# plant is gone, and hatches as the player lands.
from build_map_11 import reapply_egg


# The 1994 screenshots shown on this map, placed by vignette_place.stamp
# (docs/research/2026-10-16-screenshot-reconstruction.md, phase B):
#   screen18  the mushroom-garden scarp (giant mushroom 625, the iron-barred
#             colonnade, a two-course scarp dropping south)
#   screen21  the lava crossing and the skull-post pen on its knoll
#   screen17  the gargoyle stair down into the sunken temple's pit
#   screen02  the Lake's rock shore, the drowned body, the fish
#   screen09  the tarn shelf and its waterfall into the Lake
#   screen19  Atli's hut in Gunnar, its dirt yard sunk in the rock
#   screen20  the Gunnar commons, the campfire west of Hrodny's hut
#   screen22  the Gunnar crop garden, on the old hall-keep lot
VIGNETTES = ('screen18', 'screen21', 'screen17', 'screen02', 'screen09',
             'screen19', 'screen20', 'screen22')
# 1994-only art in these shots: none is an item (the Water Zombies and the
# Gunnar elder and children are actors, not placed).
ART_MAP = {}
# Shot items moved along the view ray (vignette_place `slides`, local
# coordinates): k steps of (8, 8, 2) draw exactly the same pixels, so the
# shot is unchanged, and only the boxes the item meets move. screen17's top
# stair block 107:1 was solved at local (895,735,72), its top at z 120, 8
# over the shelf it heads: the Avatar on the shelf just north of it (PAD_210
# and the ground round it) was then below it by y and above the shelf's
# crest 125 by z, while the block sorts under the next step and that under
# the crest: 107 -> 107 -> 1 -> 125 -> 107, logged 28,712 times through the
# whole endgame scene (verify3 F1, test_paint_cycles section 8). Four steps
# down the ray it is the same sprite with its top at the shelf's 112, a
# step flush with the shelf rather than a lip over it, clear of every
# body on the shelf, and the 1994 Avatar's own spot (screen17's actor at
# local (927,735,112)) no longer stands inside it.
RAY_SLIDES = {
    'screen17': {(107, 1, 895, 735, 72): -4},
}


# === PASSAGE TEST TRIGGER (quest step 8, DD-007a convention) ===
# quality = pinned EggPlantTest class id (shared/build/lv_manifest.json)
#         - 0x47F = 1434 - 1151 = 283
# EggPlantTest::hatch() (LOST VALE/PLNTST.UNK) searches the Avatar's
# inventory for the Passage stone (TypeBushKey, frame 0), consumes it,
# and blows away every TypeShortmushroom (shape 871, frame 0) within
# 100 cells of the EGG (100 x 32 = 3,200 world units, as retail scales
# `within N cells`), so the egg must sit within 3,200 units of the Test
# Plant, or the scene consumes the stone and destroys nothing.
PLNTST_EGG_QUALITY = 283

# npcNum packs the hatch trigger box: x range = high nibble, y range =
# low nibble (Egg::getXRange/getYRange). 0x44 = 4x4 -> +/-128 unit box
# centered on the egg (same DD-007a convention as build_map_39.py's LB
# egg, verified in-game 2026-07-03).
PLNTST_EGG_NPCNUM = 0x44

# Ragnar's quest-bag drop point — hardcoded in the 1994 source
# (UNK files/UNK/RAGNAR.UNK:837 `bag.pop(16447,25727,64)`), compiled
# as-is. The bag (TypeBag=637) holds the OTHER copy of the Passage
# stone (TypeBushKey=798); build_ragnar_cache_ruins() below builds
# real terrain plus a climbable ruin dais under this exact point so
# the pop lands on (well, 8 units above) a boulder crown at z=56.
RAGNAR_BAG_DROP = (16447, 25727, 64)

# === SHAPE CONSTANTS ===
# Most SHAPE_* ids used below come straight from lv_shapes.py (imported
# above) under their canonical names. The names below are either (a) local
# aliases kept because the local name carries map-specific meaning that
# differs from (or is narrower than) the canonical lv_shapes name, or (b) a
# constant with no lv_shapes equivalent yet.

# --- local aliases (same numeric shape id as a canonical lv_shapes constant) ---
# Bones/remains: SHAPE_BONES_A (235) and SHAPE_BONES_B (237) — real skeletal
# remains on the ground — now come straight from lv_shapes (imported above).
# This file used to alias "SHAPE_BONES"/"SHAPE_BONES_B" to shapes 189/190,
# which are full STANDING humanoid NPC sprites (322/350 animation frames), NOT
# bones. That misnomer made the Passage Test Grounds and the lake death-deck
# look populated with people — a 2026-07-05 in-game playtest had a tester
# repeatedly mistaking them for wandering NPCs. Switched to the verified
# skeletal shapes (same SF_CONTAINER family, but flat footpad z=1 vs z=5).
SHAPE_CHEST = SHAPE_DESK                    # local alias (205) — renders as a wooden desk,
                                             # not a chest (lv_shapes); kept as the local
                                             # "storage container" name used throughout.
# NOTE: the next two render as furniture, NOT what their names imply — verified
# against U8SHAPES.FLX. Kept as-is (acceptable village furniture); do not assume.
SHAPE_BARREL = SHAPE_TABLE_WORKBENCH        # local alias (208) — actually a table/workbench
SHAPE_CRATE = SHAPE_CHEST_ORNATE            # local alias (307) — actually an ornate carved chest
SHAPE_POTION = SHAPE_FLASK_ALCHEMICAL       # local alias (809) — alchemical flask; kept as
                                             # SHAPE_POTION for readability at call sites
                                             # (340 rendered as a DOOR — base-game
                                             # placeholder for unmade LV potion art; 809 is
                                             # a real flask).

# SHAPE_KEY comes from lv_shapes (82, engine name "key blank" — the real
# pickable SF_QUALITY key). Fixed twice 2026-07-02: originally 641 ("skull",
# unpickable scenery), then briefly 505 which prints "Switch" in-game. The
# engine name table (shape_names.py) is now the identity authority.

# NPC shapes — must be animated character shapes (from u8monsters.ini):
# SHAPE_NPC_GUARD_ARMORED (574)=guard, SHAPE_NPC_PEASANT_MALE (707)=peasant1,
# SHAPE_NPC_SEATED_CHARRED (835)=peasant2, SHAPE_NPC_PEASANT_SMALL (836)=peasant3,
# SHAPE_NPC_CHILD (708)=child — all imported directly from lv_shapes above.
# Usecode dispatch goes through the engine's npcnum+1024 mechanism.


# === CLAN-VILLAGE HOUSES (village construction pipeline) ===
# Rustic single-story prefab houses lifted from real base-game maps (see
# building_prefab.py), placed at the original hut positions. Cottage-scale and
# open-front (so an NPC standing at the old hut spot stays outside walls and
# reachable) to match the LV reference (screen19) — NOT the too-tall 2-story
# Tenebrae keep globs, which read as urban fortresses.
_PREFAB = {p.name: p for p in _PREFAB_LIST}

# All houses are cottage-scale (<= ~560, near the original 512 hut) so NPCs kept
# at their original positions stay at the open edge and reachable. The snug
# stone hut is used for lots that hold an NPC; empty lots mix in a timber barn.
HOME_HUT  = "hut_small_red"   # rustic prefab hut for the homes
WOOD_WALL_REMAP = {
    24:  856,   # SE stone wall → wood-plank SE wall
    20:  857,   # SW stone wall → wood-plank SW wall
    255: 858,   # stone corner post → wood corner post
    # NOTE: shape 556 (interior floor, frames 27-29) is intentionally NOT
    # remapped — it stays the original stone/tile floor. Remapping it to a
    # 4-frame custom shape left items pointing at non-existent frames 27-29.
}


def _house_buildings(hut_positions, occupied=(), hall_lots=()):
    """Place clan-village buildings at the original hut spots.

    Empty hall lots use an elongated version of the village's red-roof hut.
    """
    hall_lots = set(hall_lots) - set(occupied)
    items = []
    for i, (hx, hy) in enumerate(hut_positions):
        if i in hall_lots:
            hy -= 384
        hut = _PREFAB[HOME_HUT].stamp(hx, hy, 0, shape_remap=WOOD_WALL_REMAP)
        if i in hall_lots:
            import copy
            # Three roof and floor bays lengthen the hut along its ridge.
            middle = [p for p in hut if p.y == hy + 256 and p.shape in (412, 556)]
            for p in hut:
                if p.y >= hy + 384:
                    p.y += 384
            for dy in (128, 256, 384):
                for p in middle:
                    q = copy.copy(p)
                    q.y += dy
                    hut.append(q)
            for x in (hx, hx + 480):
                for y in (hy + 448, hy + 576, hy + 704):
                    hut.append(MapItem.placed_item(x, y, 0, 857, 0))
                for y in (hy + 480, hy + 608, hy + 736):
                    hut.append(MapItem.placed_item(x, y, 0, 858, 2))
        items.extend(hut)
    return items


# === PASSAGE TEST GROUNDS (quest step 8, the SW-corner vision-quest site) ===
# TESTPLAN.UNK / lv-patched/PLNTST.UNK's EggPlantTest::hatch() runs the
# Passage Test at HARD 1994 coordinates far to the south of everything the
# rebuilt Map 10 previously tiled: the Avatar teleports to (13055,30079,64),
# Atli/Thordis to (12927,29823,64), and five whirlwind+plant pop pairs fire
# across (12639..12873, 29567..29801, z=64). None of those had terrain — the
# scene "teleported into void". These constants pin the region + the exact
# scene coordinates so map_walkability.py and the builder agree.
#
# Walk surface MUST be z=64: the scene items are POPped/teleported to z=64,
# so the ground under them has to present a walkable top at z=64. Glob 40
# (GLOB_BARREN_GROUND) is 16x shape 242 (flat LAND, footpad (4,4,0)) at
# internal z=0, so a glob-40 egg PLACED at z=64 lays a contiguous flat floor
# whose walk surface is exactly z=64 (top = egg_z + tile_z + zd = 64+0+0).
# This is the Map-10-native delivery of the Map-11 raised-floor convention
# (individual flat footpad-z=0 tiles at the target z, build_map_11 platform 3).
TESTGROUNDS_ORIGIN = (12288, 29184)     # SW corner, chunk-aligned (24*512, 57*512)
TESTGROUNDS_CHUNKS = (2, 2)             # 1024x1024 plateau (covers all scene coords)
TESTGROUNDS_Z = 64                      # walk surface / scene z
# Every absolute coordinate the TESTPLAN/PLNTST scene touches (all at z=64):
TESTPLAN_AVATAR_TP = (13055, 30079)     # Avatar.teleport dest
TESTPLAN_NPC_TP = (12927, 29823)        # Atli/Thordis teleport dest
TESTPLAN_POPS = (                        # (wind pop, plant pop) x5
    (12777, 29801), (12767, 29791),
    (12873, 29737), (12863, 29727),
    (12745, 29673), (12735, 29663),
    (12649, 29705), (12639, 29695),
    (12777, 29577), (12767, 29567),
)


# === THE GROUND, IN ONE PLACE ===
# (x0, y0, chunks_x, chunks_y, z): the vale's outline. Chunk (cx, cy) covers
# (512cx, 512cx+512] x (512cy, 512cy+512]. Every zone's ground used to be
# emitted by its own build function and the connecting terrain by twenty
# more rectangles, four chunks were emitted twice, and 80 chunks inside the
# vale's outline were never emitted at all — black pits between the zones.
# This table is the outline lv_map10_ground.map10_field() builds the height
# field on (its tiers, the lake, the rim beyond it); the field is the ground.
TERRAIN = [
    # zones
    (10240, 1024, 10, 6, 0),      # entry
    (3072, 5120, 10, 12, 0),      # Hoskuld village
    (17408, 5120, 10, 12, 0),     # Gunnar village
    (11264, 11264, 6, 6, 0),      # Ezrekal's
    (4096, 15360, 8, 6, 0),       # west clearing
    (11264, 15360, 8, 10, 0),     # the lake
    (18432, 15360, 8, 6, 0),      # Sacred Circle
    (5120, 20480, 8, 8, 0),       # cloud approach
    (16384, 20480, 8, 8, 0),      # temple approach
    (11264, 21504, 6, 6, 0),      # Moriens ruins
    (16384, 24576, 2, 3, 0),      # Ragnar's cache
    # the Passage Test grounds: corridor, ramp (cell rows), plateau
    (12288, 24576, 2, 7, 0),
    (12288, 28160, 2, 1, 24),
    (12288, 28672, 2, 1, 48),
    (12288, 29184, 2, 2, 64),
    # connecting ground
    (3072, 1024, 14, 4, 0),
    (15360, 1024, 14, 4, 0),
    (3072, 3072, 14, 4, 0),
    (15360, 3072, 14, 4, 0),
    (10240, 4096, 10, 2, 0),
    (8192, 5120, 18, 12, 0),
    (3072, 11264, 10, 4, 0),
    (8192, 11264, 6, 8, 0),
    (14336, 11264, 16, 4, 0),
    (3072, 13312, 2, 4, 0),
    (4096, 13312, 8, 4, 0),
    (11264, 14336, 8, 2, 0),
    (14336, 13312, 8, 4, 0),
    (4096, 18432, 2, 4, 0),
    (5120, 18432, 12, 4, 0),
    (16384, 18432, 8, 4, 0),
    (20480, 18432, 4, 4, 0),
    (9216, 20480, 4, 2, 0),
    (11264, 20480, 6, 2, 0),
    (14336, 20480, 4, 8, 0),
    # the holes the rectangles above left inside the outline (2026-09-15):
    # both flanks of the lake, the strip north of the temple approach, and
    # the bay east of the Sacred Circle
    (8192, 15360, 6, 6, 0),
    (15360, 15360, 6, 6, 0),
    (15360, 18432, 2, 4, 0),
    (18432, 13312, 8, 4, 0),
]

# The two old terraces (z=24, z=48) on the way to the Passage Test grounds
# were 24-unit risers, which a walking actor refuses — scanForValidPosition
# probes 0/±4/±8 and nothing else (.claude/rules/map-geometry.md) — so the
# vision-quest site could only be reached by jumping. Eight cell rows of
# 128 at z = 8, 16 … 64 replace them (the field's cells, x 12288..13311).
RAMP_ROWS = [(28159 + 128 * k, 8 * k) for k in range(1, 9)]   # (y, z)
RAMP_X = (12288, 13312)
SLAB_FRAMES = (0, 1, 2, 3, 4, 5, 6)                            # 301 plain slabs
PALE_FRAMES = (0, 1, 2, 1, 0, 2)                               # 71 plain pale stone
CRACKED_FRAMES = (0, 1, 2, 3, 4, 5, 6, 7)                      # 299
GRAVEL_FRAMES = (0, 1, 3, 4, 7, 10, 13, 17, 22, 25)            # 6


def terrain_chunks():
    """{(cx, cy): z} for every chunk with ground; first rectangle wins."""
    chunks = {}
    for x0, y0, nx, ny, z in TERRAIN:
        for cx in range(nx):
            for cy in range(ny):
                chunks.setdefault((x0 // 512 + cx, y0 // 512 + cy), z)
    return chunks


def vignette_inputs():
    """{shot: (region cells, world items)} for the shots on this map."""
    out = {}
    for shot in VIGNETTES:
        vig = load_vignette(shot)
        out[shot] = (vignette_region(vig, ART_MAP, RAY_SLIDES.get(shot)),
                     vignette_items(vig, ART_MAP, RAY_SLIDES.get(shot)))
    return out


def testgrounds_plateau():
    """The Passage Test plateau in cells: (cx0, cy0, ncx, ncy)."""
    return (TESTGROUNDS_ORIGIN[0] // 128, TESTGROUNDS_ORIGIN[1] // 128,
            TESTGROUNDS_CHUNKS[0] * 4, TESTGROUNDS_CHUNKS[1] * 4)


def build_field():
    """The Vale's height field (lv_map10_ground): the outline above, the
    tiers the 1994 shots stand on and their closure, the lake with the
    screen02 island, the rim, the material lattice."""
    shots = vignette_inputs()
    field = map10_field(terrain_chunks(), RAMP_ROWS, RAMP_X,
                        testgrounds_plateau(), TRACKS, shots, load_pins())
    paint_earth(field, TRACKS, shots)
    return field


def build_ground(field):
    """Every floor, crest, cliff face, barrier and lake rail the field
    implies outside the shots, and the stairs onto the walkable tiers.
    South and east boundary faces stop at the adjacent ground height.
    Invisible courses above them keep the Vale closed to walking and
    climbing, continuing the Passage Test plateau's flush treatment.
    """
    items = field.emit()
    for stair in STAIRS.values():
        items += stair_items(stair)
    # VQ-009 and VQ-010: the north stairs replace whole field cells with
    # narrow step blocks. Their base floors keep void_floor from laying
    # 256-unit black plates across the adjacent earth and processional.
    for name in ('garden', 'temple'):
        for c in sorted(stair_cells(STAIRS[name])):
            items.append(field.floor_item(c, 0))
    items += lake_rails(field)
    items += lake_banks(field) + coast_banks(field)
    items += flush_edges(field, field.flush)
    return items


def props(items, spec, z=0):
    """Place (x, y, shape, frame) tuples at z."""
    for x, y, shape, frame in spec:
        items.append(MapItem.placed_item(x=x, y=y, z=z, shape=shape,
                                         frame=frame))


def build_entry_area():
    """Entry Area — arrival from the Elemental Dungeon, the way back to Pagan.

    Landscape pass 2026-09-15: the 256-spaced pickets went (the north line
    is the vale's rim, build_rim(); west and east bordered ground), and
    with them the two chimneys-as-pillars, the slab floating at z=16 as
    an "arch", the mushrooms-as-ruins. The arrival is a paved court of
    rock slabs around the four teleport eggs, two temple columns where
    the track leaves it southward, dead trees and rock either side."""
    items = []
    x0, y0 = 10240, 1024

    # === TELEPORT EGGS ===
    # The original trigger-205 placement sat 512 units due north of the
    # arrival dest — squarely on the natural walking line — so a few steps
    # into the Vale bounced the player straight back to Map 11 (in-game
    # 2026-07-04). Return triggers now live OFF the walking line, each
    # marked with a visible paving slab (the Map 8 "stand here" precedent).
    # They are NOT point traps (this comment said so until 2026-10-10):
    # npcNum is the hatch range, x (npcNum >> 4) * 32 and y (npcNum & 0xF)
    # * 32 either side, and every LV trigger carries its own id there, so
    # 204's box is +/-384 square and 213's +/-416 x +/-160. map_walkability
    # checks pad-to-egg distance; test_route_reach.arrival_corridors walks
    # each arrival pad along the heading the player arrives with.

    # TRIGGER (ID 204) -> Map 11 (Elemental Dungeon), on a marked slab west
    # of the court. Moved 2026-10-10 (was (x0+3328, y0+768), in the court's
    # north middle): its box covered the line north from pad 212, the line
    # the Avatar arrives on from Map 8, so a held key carried him from Map
    # 8 through Map 10 to Map 11 once trigger 213 was out of the way. Here
    # it is approached heading west or north-west from the pads and the
    # track, both of which end on Map 11's pad-room walls.
    # SWAPPED 2026-07-31: the 07-25 relocation comments were written under
    # the pre-771d5c7 inverted helper names, so the ACTIVE trigger had been
    # built on the quest egress line (the playtest C1 bounce class). Ids and
    # roles unchanged; positions exchanged. See build_map_13's base pair.
    items.append(MapItem.teleporter(
        x=x0 + 1664, y=y0 + 1024, z=1,
        teleport_id=204, dest_npc=204, dest_map=11
    ))
    items.append(MapItem.placed_item(
        x=x0 + 1664, y=y0 + 1024, z=1,
        shape=SHAPE_ROCK_SLAB_GROUND, frame=3, quality=0
    ))

    # ARRIVAL PAD (ID 205) — from Map 11.
    items.append(MapItem.teleport_target(
        x=x0 + 2560, y=y0 + 1536, z=0,
        teleport_id=205
    ))
    items.append(reapply_egg(x0 + 2560, y0 + 1536, 0))

    # ARRIVAL PAD (ID 212) — from Pagan (Map 8). Walked in heading north
    # up Map 8's bone chamber (or north-east or east to its slab), the
    # Avatar arrives here walking the same way.
    # SWAPPED 2026-07-31: the 07-25 relocation comments were written under
    # the pre-771d5c7 inverted helper names, so the ACTIVE trigger had been
    # built on the quest egress line (the playtest C1 bounce class). Ids and
    # roles unchanged; positions exchanged. See build_map_13's base pair.
    items.append(MapItem.teleport_target(
        x=x0 + 3584, y=y0 + 1536, z=0,
        teleport_id=212
    ))
    items.append(reapply_egg(x0 + 3584, y0 + 1536, 0))

    # TRIGGER (ID 213) -> Pagan (Map 8), on a marked slab: the court's
    # north-west portal corner. Moved 2026-10-10 (was (x0+3584, y0+1024),
    # 512 north of pad 212): a body crossed its box 288 ahead on the line
    # the Avatar arrives on from Map 8, and a 2.0 s hold through the Map 8
    # gateway bounced him straight back
    # (docs/playtest-2026-10-10-mover.md finding 2). Now no body east of
    # x 13280 or south of y 2016 touches it: clear of every line north or
    # north-east from pad 212 (x 13760 and up), and 544 north of pad 205.
    # From both pads and the track it is approached heading north or
    # north-west, and those land on Map 8's pad 213 walking into the wall
    # west of the doorway.
    items.append(MapItem.placed_item(
        x=x0 + 2560, y=y0 + 768, z=1,
        shape=SHAPE_ROCK_SLAB_GROUND, frame=3, quality=0
    ))
    items.append(MapItem.teleporter(
        x=x0 + 2560, y=y0 + 768, z=1,
        teleport_id=213, dest_npc=213, dest_map=8
    ))

    # The court: pale stone on the floor grid with the pads and both
    # triggers inside it. Zero-height LAND over the glob floor — a flood
    # sees no change (71: no SI_DRAW, so it draws over the moss; 301 did
    # not — lv_landscape's note).
    tile_run(items, span(12288, 14336), span(1536, 2816), 0,
             SHAPE_SLAB_PALE, PALE_FRAMES)
    # Two columns flanking the track south (lv_furnish.column: plinth,
    # shaft, crown — 88 tall; a lone 40-tall shaft reads as a fence post).
    for cx in (13007, 13615):
        items.extend(column(cx, 2975))
    # Dead trees and an outcrop either side of the court.
    props(items, [
        (11391, 1919, SHAPE_TREE_DEAD, 1),
        (14975, 3455, SHAPE_TREE_DEAD, 3),
        (11007, 3327, SHAPE_TREE_TRUNK, 6),
        (15103, 1663, SHAPE_TREE_TRUNK, 7),
        (12159, 3839, SHAPE_TREE_STUMP_GREY, 1),
        (11007, 2431, SHAPE_ROCK_SPIRE_CLUSTER, 1),
        (10879, 2687, SHAPE_RUBBLE_PILE, 2),
        (11135, 2559, SHAPE_STONE_SMALL, 3),
        (14847, 1791, SHAPE_ROCK_SPIRE_CLUSTER, 4),
        (14719, 1919, SHAPE_RUBBLE_SMALL, 7),
        (14463, 3711, SHAPE_BUSH, 4),
        (11647, 3583, SHAPE_BUSH, 5),
    ])
    return items


def build_hoskuld_village():
    """Clan Hoskuld Village — settlement with 8 NPCs."""
    items = []
    x0, y0 = 3072, 5120

    # Ground: the field — an earth basin against the vale's west rim
    # (lv_map10_ground). The palisade went in phase B (2026-10-16): the
    # 1994 villages have none.

    # === BUILDINGS — 5 huts ===
    hut_positions = [
        (x0+1024, y0+1536),   # Hut 1 — Elder's hut
        (x0+2560, y0+1024),   # Hut 2 — near center
        (x0+1536, y0+3072),   # Hut 3 — Hunter/Farmer home
        (x0+3584, y0+2048),   # Hut 4 — near spring
        (x0+2048, y0+4608),   # Hut 5 — edge of village
    ]

    # The long hall occupies empty lot one; the elder retains hut zero.
    items.extend(_house_buildings(hut_positions, occupied={0}, hall_lots={1}))

    # Central gathering area (open space between huts)
    gather_x, gather_y = x0 + 2048, y0 + 2048
    items.append(MapItem.placed_item(x=gather_x, y=gather_y, z=0,
                                     shape=SHAPE_ROCK_SLAB_GROUND, frame=0))

    # Spring/well area — a stone well on the open ground (the shape-3 grass
    # "spring" tiles went in phase B: the 1994 villages are earth and rock)
    spring_x, spring_y = x0 + 3840, y0 + 2816
    items.append(MapItem.placed_item(x=spring_x, y=spring_y, z=0,
                                     shape=SHAPE_WELL, frame=0))

    # Farming plots: rows of bushes (434 frames 0-3, walk-through). Were
    # shape 126, which is the blue water-rock shore tile.
    farm_x, farm_y = x0 + 1024, y0 + 4096
    for dx, dy, frame in (
            (0, 0, 0), (192, 32, 1), (384, 0, 2), (608, 64, 3),
            (32, 192, 2), (224, 224, 0), (448, 192, 3), (640, 256, 1),
            (96, 384, 1), (320, 416, 2),
            (960, 128, 3), (1184, 96, 0), (1408, 160, 2),
            (992, 352, 0), (1216, 320, 1), (1440, 384, 3),
            (1088, 544, 2), (1344, 576, 0)):
        items.append(MapItem.placed_item(farm_x + dx, farm_y + dy, 0,
                                         SHAPE_BUSH, frame))

    # === NPCs (8 in Hoskuld Village) ===
    # Female Elder — in her hut near center
    items.append(MapItem(
        x=x0+1280, y=y0+1792, z=0, shape=SHAPE_NPC_PEASANT_MALE, frame=0,
        npcnum=100, mapnum=10, quality=0  # NPC 100 — Female Elder
    ))
    # Male Veteran — near the spring
    items.append(MapItem(
        x=x0+3584, y=y0+2560, z=0, shape=SHAPE_NPC_GUARD_ARMORED, frame=0,
        npcnum=101, mapnum=10, quality=0  # NPC 101 — Veteran
    ))
    # Sigrid, the Female Hunter — south of the Hunter/Farmer home (hut lot
    # 3), her schedule() home. npcnum 102 dispatches to class 1126, which is
    # where SIGRID.UNK now compiles (u8c_symbols.LV_NPC_SHAPES). Before
    # 2026-07-26 she was pinned at class 1452, outside every dispatch
    # window, so this villager was mute and her 2.4 KB of dialogue
    # unreachable. MOVED 2026-10-09 from x0+4608, y0+1280 = (7680,6400),
    # which was neither of her schedule points: every Map 10 entry snaps
    # the LV actors back to their FIXED starts (fork map.cpp, docs/
    # playtest-2026-10-09-schedules.md finding 4), so she reappeared there
    # on each hop. One unit from lv-new/SIGRID.UNK S1's home point
    # (4895,8991,0).
    items.append(MapItem(
        x=x0+1824, y=y0+3872, z=0, shape=SHAPE_NPC_PEASANT_MALE, frame=0,
        npcnum=102, mapnum=10, quality=0  # NPC 102 — Sigrid (Hunter)
    ))
    # Male Farmer — in farming area
    items.append(MapItem(
        x=x0+1536, y=y0+4352, z=0, shape=SHAPE_NPC_PEASANT_MALE, frame=0,
        npcnum=103, mapnum=10, quality=0  # NPC 103 — Farmer
    ))
    # Male Child (ZCHILD) — roaming village. Since 2026-10-25 the body of
    # screen20's dark-haired spear child (889).
    items.append(MapItem(
        x=x0+2304, y=y0+2304, z=0, shape=SHAPE_SPEAR_CHILD_DARK, frame=0,
        npcnum=104, mapnum=10, quality=0  # NPC 104 — Child
    ))
    # Ragnar — south of the edge hut (Hut 5), his schedule() home. MOVED
    # 2026-10-08 from x0+2048, y0+3584 = (5120,8704), which overlapped Hut
    # 3's wall (exact_reach: no standing level at z 0 there); one unit from
    # lv-patched/RAGNAR.UNK change 13's home point (5439,10527,0).
    items.append(MapItem(
        x=x0+2368, y=y0+5408, z=0, shape=SHAPE_NPC_GUARD_ARMORED, frame=0,
        npcnum=105, mapnum=10, quality=0  # NPC 105 — Ragnar
    ))
    # Thordis — in front of the Elder's hut (Hut 1), her schedule() home.
    # MOVED 2026-10-08 from x0+3072, y0+1536 = (6144,6656), inside the clan
    # hall keep's corner (exact_reach: the only standing level there is the
    # keep roof at 144); one unit from lv-patched/THORDIS.UNK S1's home
    # point (4415,7423,0), which EggShades now sends her back to as well.
    items.append(MapItem(
        x=x0+1344, y=y0+2304, z=0, shape=SHAPE_NPC_PEASANT_MALE, frame=0,
        npcnum=106, mapnum=10, quality=0  # NPC 106 — Thordis
    ))
    # Tyorvi, Thordis's brother — east of the spring hut (Hut 4). MOVED
    # 2026-10-08 from Gunnar (19456,8960): every source makes him Clan
    # Hoskuld ("Thordis? The Elder of Clan Hoskuld she is. Also my sister
    # she is."), and his retargeted schedule() home (lv-patched/TYORVI.UNK
    # S1) is (7423,7519,0), one unit from here, so a new game no longer
    # teleports him across the vale on the first scheduler run. His stash
    # slot is in Gunnar, south of the still-house by the still kettle.
    items.append(MapItem(
        x=x0+4352, y=y0+2400, z=0, shape=SHAPE_NPC_PEASANT_MALE, frame=0,
        npcnum=115, mapnum=10, quality=0  # NPC 115 — Tyorvi
    ))

    # Containers — household items
    # The open stockade storage rests under the unoccupied hall roof.
    items.append(MapItem.placed_item(5856, 6016, 0, SHAPE_CRATE, 0))
    items.append(MapItem.placed_item(x=x0+1280, y=y0+1536, z=0, shape=SHAPE_BARREL, frame=0))
    items.append(MapItem.placed_item(x=x0+2816, y=y0+1280, z=0, shape=SHAPE_CHEST, frame=0))
    items.append(MapItem.placed_item(x=x0+1792, y=y0+3328, z=0, shape=SHAPE_CRATE, frame=0))
    items.append(MapItem.placed_item(x=x0+3840, y=y0+2304, z=0, shape=SHAPE_BARREL, frame=0))

    # Scrub around the village (was shape 127: an 8x8 red brick floor)
    # and a few stones.
    props(items, [
        (x0+512, y0+768, SHAPE_BUSH, 1), (x0+4352, y0+512, SHAPE_BUSH, 2),
        (x0+4864, y0+3584, SHAPE_BUSH, 3), (x0+768, y0+5632, SHAPE_BUSH, 0),
        (x0+3328, y0+5120, SHAPE_BUSH, 5),
        (x0+4608, y0+4608, SHAPE_RUBBLE_SMALL, 7),
        (x0+256, y0+2816, SHAPE_RUBBLE_SMALL, 6),
        (x0+640, y0+3584, SHAPE_TREE_TRUNK, 8),
    ])

    return items


def build_gunnar_village():
    """Clan Gunnar Village — settlement with 8 NPCs."""
    items = []
    x0, y0 = 17408, 5120

    # Ground: the field — an earth basin with the rock the 1994 yards are
    # sunk in (lv_map10_ground RELIEF). The palisade went in phase B
    # (2026-10-16): no 1994 shot of the village shows one, and its west run
    # crossed screen22's garden yard.

    # === BUILDINGS — 5 huts + workshop + still ===
    hut_positions = [
        (x0+1536, y0+1024),   # Hut 1 — Atli's hut (elder)
        (x0+3072, y0+1536),   # Hut 2
        (x0+1024, y0+3072),   # Hut 3 — Farmer's home
        (x0+3584, y0+3072),   # Hut 4 — Hrodny's home
        (x0+2560, y0+4608),   # Hut 5 — edge
    ]
    # Lots 1, 3 and 4 are the 1994 shots' huts (screen19 Atli's, screen22
    # the garden's on the old hall-keep lot, screen20 Hrodny's), stamped and
    # completed by build_map_10 (lv_hut1994); the prefab stands on 2 and 5.
    SHOT_LOTS = {0, 2, 3}
    items.extend(_house_buildings(
        [p for i, p in enumerate(hut_positions) if i not in SHOT_LOTS]))

    # Moonshine still — a still-house (grounded wood hut) with the still
    # apparatus (barrels, crate, potion) clustered at its open SE front. The
    # Moonshiner NPC (109) sits at +(256,256), the open-front spot, like the
    # occupied home lots. Replaces the old floating loose props.
    # Moonshiner's house (wood hut) + an OPEN-AIR still in the clear ground just
    # south of it. Props inside a hut are hidden by its own walls from the SE
    # camera, and the design doc calls the still an "open-air workspace" — so the
    # distilling gear sits outside where it's fully visible. A storage chest
    # stays in the house. The Moonshiner NPC (109) works at the still (below).
    still_x, still_y = x0 + 4096, y0 + 2048
    items.extend(_PREFAB[HOME_HUT].stamp(still_x, still_y, 0, shape_remap=WOOD_WALL_REMAP))
    items.append(MapItem.placed_item(x=still_x+160, y=still_y+192, z=0, shape=SHAPE_CRATE, frame=0))  # house storage
    # A tight still STATION hard against the house's south edge (always visible
    # from outside, reads as a workspace not yard clutter): a workbench at the
    # back corner, cauldron + bottles + flasks clustered in front. NPC 109 works
    # here.
    #
    # The workbench (208, 96x160 footpad) stands WEST of NPC 109's spot and
    # wholly south of the wall line, its far edge on the corner rubble's
    # near edge (y 7744). Until 2026-10-07 it sat at +(160,600): box
    # x(21568,21664] y(7608,7768], straddling the south wall (856, y
    # (7648,7680]) and the zero-depth vine line (426, y 7680) and burying
    # NPC 109's start box. ItemSorter cannot order a box that pierces a
    # wall face: the cycle 426 -> 208 -> 526 -> 426 (and -> 707) logged
    # about 110,000 `Cycle in paint dependency graph` lines a session
    # (docs/playtest-2026-10-02-pt-activity.md finding 7). Here it touches
    # the rubble (526, x(21472,21536]) and nothing else, and NPC 109 keeps
    # the open ground south and east of him.
    items.append(MapItem.placed_item(x=still_x+32, y=still_y+736, z=0, shape=SHAPE_BARREL, frame=0))    # workbench
    items.append(MapItem.placed_item(x=still_x+256, y=still_y+632, z=0, shape=SHAPE_CAULDRON, frame=0))  # still kettle
    items.append(MapItem.placed_item(x=still_x+208, y=still_y+680, z=0, shape=SHAPE_BOTTLE_GREEN, frame=0))
    items.append(MapItem.placed_item(x=still_x+320, y=still_y+648, z=0, shape=SHAPE_BOTTLE_GREEN, frame=0))
    items.append(MapItem.placed_item(x=still_x+272, y=still_y+700, z=0, shape=SHAPE_BOTTLE_GREEN, frame=0))
    items.append(MapItem.placed_item(x=still_x+176, y=still_y+664, z=0, shape=SHAPE_POTION, frame=0))

    # Inventor's workshop — house hut + a tight work STATION against its south
    # edge (always visible), mirroring the still. A parts chest stays inside; two
    # workbenches with instruments (flasks) and a chemical bottle cluster outside.
    # No cauldron, so it reads distinct from the moonshiner's still.
    workshop_x, workshop_y = x0 + 4096, y0 + 4096
    items.extend(_PREFAB[HOME_HUT].stamp(workshop_x, workshop_y, 0, shape_remap=WOOD_WALL_REMAP))
    items.append(MapItem.placed_item(x=workshop_x+160, y=workshop_y+192, z=0, shape=SHAPE_CRATE, frame=0))   # house storage chest
    # Main workbench: same move and reason as the still's (above), the same
    # prefab offsets — it straddled this hut's south wall and buried NPC 108.
    items.append(MapItem.placed_item(x=workshop_x+32, y=workshop_y+736, z=0, shape=SHAPE_BARREL, frame=0))   # main workbench
    items.append(MapItem.placed_item(x=workshop_x+296, y=workshop_y+624, z=0, shape=SHAPE_CHEST, frame=0))    # parts bench
    items.append(MapItem.placed_item(x=workshop_x+216, y=workshop_y+680, z=0, shape=SHAPE_POTION, frame=0))   # instrument flask
    items.append(MapItem.placed_item(x=workshop_x+336, y=workshop_y+664, z=0, shape=SHAPE_POTION, frame=0))   # instrument flask
    items.append(MapItem.placed_item(x=workshop_x+264, y=workshop_y+712, z=0, shape=SHAPE_BOTTLE_GREEN, frame=0))   # chemical bottle
    # The inventor's abacus. NEW PLACEMENT 2026-07-26 (orphan triage,
    # decision D): TypeAbacus (ABACUS.UNK) was compiled but unreachable.
    # npcnum dispatches it to class 1254; use() counts the obsidian coins in
    # the Avatar's backpack and barks the total, so it is a working gadget
    # rather than set dressing. No quest depends on it.
    #
    # On the floor at the parts bench's east end, not on the bench. Until
    # 2026-10-07 it was at +(296,660, z 4) "sat on the parts bench": box
    # x(21768,21800] y(9812,9876] z[4,12), inside the bench (205, x(21640,
    # 21800] y(9744,9840] z[0,16)) and hanging off its front edge. A small
    # item inside a solid is the F11 trap (.claude/rules/map-geometry.md):
    # Item::canReach's line-of-sight sweeps run into the bench, so the
    # double-click that runs use() can be refused. Resting it on the bench
    # top (z 16) is the other half of that rule (the depth sort cycled
    # 11,000 times for a potion on furniture), and this builder never puts
    # a small item on a solid's top. Here, x(21804,21836] y(9744,9808] z
    # [0,8), it touches nothing; an Avatar east of it, x(21836,21900], has a
    # clear sight line along y 9808.
    items.append(MapItem(x=workshop_x+332, y=workshop_y+592, z=0,
                         shape=SHAPE_ABACUS, frame=0, npcnum=NPCNUM_ABACUS))

    # Spring/well area — a stone well on the open ground (the shape-3 grass
    # "spring" tiles went in phase B: the 1994 village is earth and rock)
    spring_x, spring_y = x0 + 1280, y0 + 2304
    items.append(MapItem.placed_item(x=spring_x, y=spring_y, z=0,
                                     shape=SHAPE_WELL, frame=0))

    # === NPCs (8 in Gunnar Village) ===
    # Male Elder (Atli) — outside his hut's south door (hut lot 1), his
    # night schedule() point. MOVED 2026-10-09 from x0+1792, y0+1280 =
    # (19200,6400), inside the hut, 543 units from either schedule point,
    # where every Map 10 entry snapped him back (docs/playtest-2026-10-09-
    # schedules.md finding 4). ON lv-patched/ATLI.UNK S1's "Lab 1" point
    # (19231,6943,0), which EggShades also sends him home to: one unit in
    # from (19232,6944) since 2026-10-17, where his body's box met the
    # east jamb of screen19's door (the shot's 150 at x 19232..19327).
    # Since 2026-10-25 his body is the 1994 elder of screen19/20 (888), on
    # frame 60, stand SE, looking out of his door as the shot's elder does:
    # Mythran's wider body facing N/NE in the gap (frames 0/15/30) has
    # 16-27% painted over by the east jamb (test_schedule_destinations
    # check 4), SE 7%.
    items.append(MapItem(
        x=x0+1823, y=y0+1823, z=0, shape=SHAPE_ZEALAN_ELDER, frame=60,
        npcnum=107, mapnum=10, quality=0  # NPC 107 — Atli
    ))
    # Female Inventor — at her workbench station beside the house
    items.append(MapItem(
        x=x0+4224, y=y0+4672, z=0, shape=SHAPE_NPC_PEASANT_MALE, frame=0,
        npcnum=108, mapnum=10, quality=0  # NPC 108 — Inventor
    ))
    # Male Moonshiner — standing at his still station beside the house
    items.append(MapItem(
        x=x0+4224, y=y0+2624, z=0, shape=SHAPE_NPC_PEASANT_MALE, frame=0,
        npcnum=109, mapnum=10, quality=0  # NPC 109 — Moonshiner
    ))
    # Female Farmer — in farming area
    items.append(MapItem(
        x=x0+1280, y=y0+4608, z=0, shape=SHAPE_NPC_PEASANT_MALE, frame=0,
        npcnum=110, mapnum=10, quality=0  # NPC 110 — Farmer
    ))
    # Female Child of Elder — outside father's hut. Since 2026-10-25 the
    # body of screen20's blond spear child (890).
    items.append(MapItem(
        x=x0+2304, y=y0+1536, z=0, shape=SHAPE_SPEAR_CHILD_BLOND, frame=0,
        npcnum=111, mapnum=10, quality=0  # NPC 111 — Child
    ))
    # Ingjald — outside his hut's south door (Hut 2), his schedule() home.
    # MOVED 2026-10-08 from x0+3328, y0+1792 = (20736,6912), inside the
    # hut's storage chest (307); one unit from lv-patched/INGYALD.UNK S1's
    # home point (20767,7455,0).
    items.append(MapItem(
        x=x0+3360, y=y0+2336, z=0, shape=SHAPE_NPC_GUARD_ARMORED, frame=0,
        npcnum=112, mapnum=10, quality=0  # NPC 112 — Ingjald
    ))
    # Hrodny — outside her home, east of the door
    items.append(MapItem(
        x=x0+4352, y=y0+3328, z=0, shape=SHAPE_NPC_PEASANT_MALE, frame=0,
        npcnum=113, mapnum=10, quality=0  # NPC 113 — Hrodny
    ))
    # Changtar — in village
    items.append(MapItem(
        x=x0+2816, y=y0+2560, z=0, shape=SHAPE_NPC_SORCERER, frame=0,
        npcnum=114, mapnum=10, quality=0  # NPC 114 — Changtar
    ))

    # Hrodny's locked chest — shape 618, engine name "locked chest"
    # (SF_CONTAINER, class LCHST_EW). The lock is the SHAPE_TRAP record
    # contained right after it (quality 0x100 | HRODNY_KEY_ID), as in every
    # retail locked chest; the chest's own quality is not read by KEYRING.
    # History: 205 = desk, then 307 which prints "Wardrobe" in-game.
    # LOCK ID CHANGED 160 -> 20 (2026-07-27, egg-queue pass). The compiled
    # HRODNY class (1137) spawns the "lost" key itself: her
    # `case "How can I open the temple?"` creates a TypeBag holding a
    # TypeKey, calls setQuality(20) on it, and pops the bag into the world
    # (verified in the built FLX at 0x4802: `push byte +20; calli
    # setQuality`). At lock ID 160 that spawned key opened nothing, so the
    # one key the QUEST hands you was inert. 20 is the 1994 source's number
    # and collides with no other lock — zero items on any map carried
    # quality 20 before this change.
    #
    # The 1994 design had no pre-placed key: the chest stays shut until you
    # ask her, and her bag is the "lost" key you find. A placed q20 key
    # "somewhere in the village" (a 2026-03 reading of her "gone, the key
    # is" line) was kept as a safety net from 2026-07-27. It was REMOVED
    # 2026-10-11 (Douglas): her option comes back whenever she is talked to
    # healed, the bag (lv-patched HRODNY change 1 pops it at z 0, not the
    # 1994 z 64) lands and opens the chest in-engine
    # (docs/playtest-2026-10-10-questbits.md Q4), and the spare let full
    # run part 6 skip the errand. test_chest_locks pins its absence.
    HRODNY_KEY_ID = 20
    # MOVED 2026-09-03 (exit-test blocker, docs/playtest-2026-09-02-quest-
    # chain.md test Z-a): was x0+3584, y0+3584 = (20992, 8704, 0), which is
    # the hut's west WALL column — the chest shared that cell with wall piece
    # 858 and the wall won the hit test. Standing inside the hut, a 16-point
    # probe sweep over the chest's whole predicted sprite area returned the
    # wall, the floor and the Avatar, never shape 618. An unclickable chest
    # means no Tiny Tar, and no Tiny Tar means the Ancient Temple can never
    # be entered (the crack is the only way in, DD-005).
    #
    # Nor does an interior cell work. (21152, 8640, 0) — inside the hut, on
    # standable floor, in an empty cell — is still unclickable: the hut's
    # south wall run at y=8704 is 40 tall and sorts IN FRONT of anything
    # north of it, so the chest sits inside the wall's sprite. Verified on a
    # fresh map-10 load (the fix cannot be seen from a map-10 save): a
    # 20-point probe sweep over the whole area returned the wall pieces at
    # (21120/21280, 8704), the post at (21152, 8704) and the floor at
    # (21119, 8575) — never shape 618. Same failure as the wall column, one
    # tile further in.
    #
    # So it goes on the open ground outside her door: x0+3744, y0+3712 =
    # (21152, 8832, 0). exact_reach gives that cell a single standable level
    # 0 and no occupants, the road runs just south of it at y=8839, and
    # nothing tall stands between it and the camera. Still "at Hrodny's
    # home", and a player walking up the road cannot miss it.
    #
    # MOVED 2026-10-10 one tile west, to x0+3616 = (21024, 8832, 0), the
    # same distance in front of the same wall run. At x0+3744 its west face
    # stood 32 units east of the hut prefab's rubble chip (526 frame 4,
    # 64x64x16 at (21024, 8768)), diagonally against it: walking up the
    # chest's west side toward the north-east the Avatar wedged at
    # (21049, 8857), N the rubble, E the chest, NE both, and those three
    # are all the mover tries (docs/playtest-2026-10-11-full-run-part6.md
    # finding 6). Now the chip sits on the chest's north face, east half,
    # and the west face is open ground north to the hut's west wall
    # (test_route_reach.chest_west_side).
    #
    # MOVED 2026-10-16/17 (phase B, the 1994 screenshots) INSIDE the hut, to
    # x0+3808, y0+3648 = (21216, 8768, 0). screen20 puts the 1994 hut's
    # roof on (20992..21503) x (8192..), walls flush with its edge as
    # screen19's are, and the old spot straddled that west wall
    # (vignettes/screen20.json pin_moves). A first cut, (21120, 8832),
    # stood flush against the wall inside, so nobody could walk its west
    # face (test_route_reach.chest_west_side started inside the wall);
    # here its west face is 96 off the wall, a body's width and more of
    # open floor north to the hut's north wall, and its south face is 32
    # north of the two potions below. It is 287 north of the south wall
    # and its door (lv_hut1994), so the south wall's sprite stops short of
    # it, and the roof lifts as the Avatar comes in. The hut prefab and
    # its rubble chip are gone with the lot.
    items.append(MapItem.placed_item(
        x=x0+3808, y=y0+3648, z=0,
        shape=SHAPE_CHEST_LOCKED, frame=0, quality=HRODNY_KEY_ID
    ))
    # THE LOCK (2026-10-08). KEYRING 004F:0445 scans the chest for a TRAP
    # with quality/256 == 1 and opens it only for a key whose quality equals
    # the trap's low byte; with no such trap it opened for ANY key, including
    # the Cliff Key and key blanks (docs/playtest-2026-10-08-intrinsics.md,
    # C4). quality/256 == 1 also makes TRAP use() a no-op, so the chest's
    # own use() can call it safely. Contained records must follow the chest.
    items.append(MapItem.contained_item(
        shape=SHAPE_TRAP, frame=0, quality=0x100 | HRODNY_KEY_ID
    ))
    # ── THE TINY TAR POTIONS (DD-005) — INSIDE THE CHEST ────────────────
    # SHAPE_POTION_REAL (859) frame 8, npcnum 229 so the engine patch
    # dispatches TYPEPOTION (class 1253). POTION.UNK::use() frame 8 spawns
    # makeAvatarTiny(), waits ~33 s, then makeAvatarBig() — which kills the
    # Avatar if a full-size body cannot fit where it re-grows. Shrunk, the
    # Avatar is 32x32 and fits the Map 18 crack; at 64x64 he does not. This
    # is the only thing in the game that can shrink you, and the crack is
    # the only way into the Ancient Temple.
    #
    # THREE, not two: Hrodny's line is plural ("Potions, I have, from
    # generation to generation passed on") and the mechanic can kill you,
    # so the player needs retries. Three is enough to fail twice.
    #
    # CONTAINED, as of 2026-09-03. MapItem.contained_item() explains the
    # on-disk encoding (x = container depth, y = gump slot); these records
    # MUST stay directly after the chest above. Before this they sat on the
    # ground at the chest's ORIGINAL site (x0+3488..3536, y0+3576..3664),
    # which was inside the hut's west wall column — the same spot that made
    # the chest itself unclickable — so a full exit test on 2026-09-02
    # never saw them and concluded no potion existed on the map. The
    # 2026-08-18 F11 fix (potions interpenetrating the chest and the
    # shape-526 furniture broke drag-and-drop; potions resting on a tall
    # neighbour's top face made the depth sort cycle) is moot for a
    # contained item, which has no world box at all. In the chest they are
    # what Hrodny's dialogue says they are — "locked in a chest" — and both
    # keys (the one she spawns and the pre-placed one) are the way to them.
    for _ in range(3):
        items.append(MapItem.contained_item(
            shape=SHAPE_POTION_REAL, frame=8,   # frame 8 = Tiny Tar
            npcnum=NPCNUM_POTION
        ))
    # ── Protection (frame 5) and invisibility (frame 7) potions. NEW
    # PLACEMENT 2026-10-08 (Douglas: "Hrodny's hut"). TypePotion::use()
    # frame 5 grants timed immortality, frame 7 toggles INVISIBLE; neither
    # was placed anywhere, so both branches were checked in bytecode only
    # (docs/reviews/2026-09-30-four-anomalies.md §4). They were placed on
    # the open ground outside her door, beside her chest: boxes
    # x(21184,21216] and x(21248,21280], y(8800,8832], z 0. Since phase B
    # (2026-10-16) screen20's hut stands over that ground, so they lie on
    # its floor, 32 south of the chest (y <= 8768). Top-level records, so
    # they come after the chest's contents above.
    items.append(MapItem(x=x0+3808, y=y0+3712, z=0,
                         shape=SHAPE_POTION_REAL, frame=5,  # protection
                         npcnum=NPCNUM_POTION))
    items.append(MapItem(x=x0+3872, y=y0+3712, z=0,
                         shape=SHAPE_POTION_REAL, frame=7,  # invisibility
                         npcnum=NPCNUM_POTION))
    # Moonshine bottles
    items.append(MapItem.placed_item(x=x0+4160, y=y0+2112, z=4, shape=SHAPE_POTION, frame=1))
    items.append(MapItem.placed_item(x=x0+4224, y=y0+2176, z=4, shape=SHAPE_POTION, frame=1))

    # Containers
    items.append(MapItem.placed_item(x=x0+1792, y=y0+1024, z=0, shape=SHAPE_BARREL, frame=0))
    items.append(MapItem.placed_item(x=x0+3328, y=y0+1792, z=0, shape=SHAPE_CRATE, frame=0))

    # Farming area: rows of bushes (was 126, the blue water-rock tile)
    farm_x, farm_y = x0 + 768, y0 + 4608
    for i in range(6):
        for j in range(3):
            items.append(MapItem.placed_item(
                x=farm_x + i * 256, y=farm_y + j * 256, z=0,
                shape=SHAPE_BUSH, frame=(i + j) % 4
            ))

    # Scrub (was 127, red brick) and a dead trunk by the north fence
    props(items, [
        (x0+256, y0+512, SHAPE_BUSH, 2), (x0+4864, y0+5120, SHAPE_BUSH, 1),
        (x0+768, y0+1792, SHAPE_BUSH, 3), (x0+4352, y0+384, SHAPE_TREE_TRUNK, 9),
        (x0+320, y0+5760, SHAPE_RUBBLE_SMALL, 8),
    ])

    return items


def build_ezrekal_dwelling():
    """Ezrekal's Dwelling — the hermit's stockade between the villages.

    Landscape pass 2026-09-15: the four-wall shack with a 3x2 grid of roof
    squares floating at z=12 (the hygiene test's six roof_small/roof_low
    counts for this map; 220 is the blue-black tiled roof) is now a
    roofless wood-plank enclosure — the 856/857/858 set the villages'
    huts use, panels missing where it has fallen — with its opening on
    the east. Ezrekal's start (12800,12544), the bedroll and the reagent
    bench with the two typed potions are where they were (all pinned,
    map_pins.json); the garden rows of 126 (blue water-rock) and 127 (red
    brick) are bushes."""
    items = []
    x0, y0 = 11264, 11264

    # The stockade: inside is (12319..13951] x (12191..12927]; the opening
    # on the east side spans y (12415..12671].
    fallen = {(12927, 12191), (13567, 12191), (13183, 12959), (12319, 12543)}
    for x in span(12288, 13952):
        for y in (12191, 12959):
            if (x, y) not in fallen:
                items.append(MapItem.placed_item(
                    x=x, y=y, z=0, shape=SHAPE_WOOD_PLANK_WALL_SE, frame=0))
    for y in span(12160, 12928):
        if (12319, y) not in fallen:
            items.append(MapItem.placed_item(
                x=12319, y=y, z=0, shape=SHAPE_WOOD_PLANK_WALL_SW, frame=0))
        if y not in (12543, 12671):
            items.append(MapItem.placed_item(
                x=13983, y=y, z=0, shape=SHAPE_WOOD_PLANK_WALL_SW, frame=0))
    for x, y in ((12319, 12191), (13983, 12191), (12319, 12959),
                 (13983, 12959)):
        items.append(MapItem.placed_item(
            x=x, y=y, z=0, shape=SHAPE_WOOD_PLANK_CORNER_POST, frame=0))

    # Herb garden south of the stockade: two rows of bushes
    for i in range(6):
        for j, y in enumerate((13311, 13567)):
            items.append(MapItem.placed_item(
                x=12415 + i * 192, y=y, z=0,
                shape=SHAPE_BUSH, frame=(i + j) % 4
            ))

    # Shelter with stored reagents. The desk (205, 160x96) stood at
    # (x0+2560, y0+1280) until 2026-10-10: box x(13664,13824] y(12448,
    # 12544], 127 units inside the east doorway and across its north half,
    # with the pinned potions (y 12640..12672, moved south after build 7)
    # across the south. That left
    # a 32-unit lane, y (12544, 12640] less a body, between them: every
    # mouse walk or run in through the door at y 12479..12607 stopped dead
    # at the desk (avatar_mover, 200 of 1,800 holds), the "wedged runs" of
    # playtest-2026-10-10-full-run-part5 finding 8. Against the north wall
    # it is clear of the doorway's whole width.
    items.append(MapItem.placed_item(x=x0+2560, y=y0+1023, z=0, shape=SHAPE_CHEST, frame=0))
    items.append(MapItem.placed_item(x=x0+2304, y=y0+1280, z=0, shape=SHAPE_BARREL, frame=0))

    # Ezrekal NPC
    items.append(MapItem(
        x=x0+1536, y=y0+1280, z=0, shape=SHAPE_NPC_SORCERER, frame=0,
        npcnum=116, mapnum=10, quality=0  # NPC 116 — Ezrekal
    ))

    # Reagent items (SHAPE_POTION here is 809, an alchemical FLASK — scenery
    # dressing, deliberately left inert)
    items.append(MapItem.placed_item(x=x0+2560, y=y0+1536, z=4, shape=SHAPE_POTION, frame=2))
    items.append(MapItem.placed_item(x=x0+2304, y=y0+1536, z=4, shape=SHAPE_POTION, frame=3))

    # ── Working potions at the healer's. NEW PLACEMENTS 2026-07-26 (orphan
    # triage, decision D). TypePotion (POTION.UNK) was compiled but
    # unreachable; npcnum dispatches these two to class 1253. These are on
    # SHAPE_POTION_REAL (859 since DD-005; was 766), NOT the local
    # SHAPE_POTION flask above, so the drinkable ones are visually distinct
    # from the reagent dressing.
    #
    # TypePotion::use() switches on frame: 1 = restore health, 2 = restore
    # mana. Both are placed on Ezrekal's shelf because he is the Vale's
    # healer — the one location where a working potion needs no
    # justification. Frames 4 (damage) and 6-7 (sleep/invisibility) are
    # deliberately NOT placed: they are effects with balance consequences.
    # Frame 8 (Tiny Tar) IS placed, but in Hrodny's locked chest — it is a
    # quest item, not shelf stock. It used to be unplaceable for a different
    # reason: shape 766 had only frames 0-7 and no frame-8 art existed.
    #
    # They stood at (x0+2560, y0+1408) and (x0+2496, y0+1408) until build 7:
    # box y (12640, 12672], 159 units inside the east doorway and across
    # its last 31 units south, so a hold W in through the door at y 12671
    # stopped 88 units in (avatar_mover; playtest-2026-10-11-build7 D1).
    # They now stand in the row of flasks at y0+1536, between the two
    # 809s, 97 units south of the doorway's line.
    items.append(MapItem(x=x0+2496, y=y0+1536, z=4,
                         shape=SHAPE_POTION_REAL, frame=1,  # health
                         npcnum=NPCNUM_POTION))
    items.append(MapItem(x=x0+2432, y=y0+1536, z=4,
                         shape=SHAPE_POTION_REAL, frame=2,  # mana
                         npcnum=NPCNUM_POTION))

    # ── Guest bedroll. NEW PLACEMENT 2026-07-26 (orphan triage, decision D).
    # TypeBedroll (BEDROLL.UNK) dispatches to class 1255. This is NOT a
    # flavour item despite being filed with the joke items: its use() is the
    # base game's bed code — it asks how many periods to rest, advances the
    # clock, and restores HP and mana in full, refusing while enemies are
    # near. That makes it a rest point, so exactly ONE is placed, and at
    # Ezrekal's rather than in a village hut: the dwelling sits between both
    # villages and is already the map's safe waypoint.
    items.append(MapItem(x=x0+1408, y=y0+1536, z=0,
                         shape=SHAPE_BEDROLL, frame=0, npcnum=NPCNUM_BEDROLL))

    # Path markers to both villages
    # The yard's dressing and the ground about it
    props(items, [
        (12511, 12351, SHAPE_BUSH, 4),
        (13439, 12351, SHAPE_STONE_SMALL, 5),
        (14335, 12287, SHAPE_TREE_STUMP_GREY, 2),
        (11839, 12799, SHAPE_TREE_DEAD, 3),
        (11711, 13823, SHAPE_ROCK_SPIRE_CLUSTER, 5),
        (13887, 13951, SHAPE_RUBBLE_SMALL, 6),
    ])
    return items


def build_test_area():
    """Former west clearing (was the placeholder Test Area).

    The Passage Test proper — the Test Plant, the PLNTST trigger egg, and
    the whole vision scene — lives in build_test_grounds() at the vale's
    real SW corner now (the 1994 TESTPLAN coordinates, ~x12800/y29800).
    This western clearing kept its barren ground + ambient bones/rocks so
    it still reads as walkable wilderness and stays connected to the Cloud
    Approach; only the plant + egg were relocated south (2026-07-05). The
    egg had to move: the scene it hatches teleports the Avatar to
    (13055,30079) and pops mushrooms across (12639..12873, 29567..29801),
    all of which were VOID up here in the west."""
    items = []
    x0, y0 = 4096, 15360
    # ground: TERRAIN table. Landscape pass 2026-09-15: a dead tree, a
    # stump, an outcrop — the clearing was bones on bare moss.
    props(items, [
        (4735, 16255, SHAPE_TREE_DEAD, 3),
        (7551, 17791, SHAPE_TREE_STUMP_GREY, 0),
        (4479, 17919, SHAPE_ROCK_SPIRE_CLUSTER, 5),
        (7807, 15743, SHAPE_RUBBLE_PILE, 3),
        (7935, 15871, SHAPE_STONE_SMALL, 7),
    ])

    # Open clearing at center (plant + egg relocated to build_test_grounds)
    plant_x, plant_y = x0 + 2048, y0 + 1536

    # Surrounding clear ground (already tiled)

    # Bones/remains of previous test-takers
    items.append(MapItem.placed_item(x=plant_x-512, y=plant_y-256, z=0,
                                     shape=SHAPE_BONES_A, frame=0))



    return items


def build_test_grounds():
    """Passage Test Grounds — the SW-corner vision-quest site (quest step 8).

    Fixes the "Test scene teleports into void" gap: EggPlantTest::hatch()
    (lv-patched/PLNTST.UNK) teleports the Avatar to (13055,30079,64), an
    NPC to (12927,29823,64), and pops five whirlwind+plant pairs across
    (12639..12873, 29567..29801, z=64) — all of which had NO terrain. The
    scene never sends the player home: afterward the Avatar has the Mark
    and is poisoned and must WALK back north out of the grounds.

    Layout (all glob-40 barren floor, the map's proven LAND ground; the
    eggs and the ramp come from the TERRAIN table via build_terrain):
      - a z=64 plateau (2x2 chunks) covering every scene coordinate with
        margin — walk surface exactly z=64 (glob-40 tiles are flat
        footpad-z=0 shape 242; PLACED at egg-z 64 -> top 64);
      - an on-foot link NORTH to Moriens Ruins (its south edge is at
        y=24576, directly above this x-band): a flat z=0 corridor and
        then a RAMP of eight tile rows at z = 8, 16 … 64. Until
        2026-09-15 this was two glob terraces at z=24 and z=48 — 24-unit
        risers, which the walking actor refuses (0/±4/±8 only,
        .claude/rules/map-geometry.md); map_walkability's STEP_Z=24
        model passed them and test_route_reach's exact model did not.
        The rim (build_rim) rises beside the ramp and around the plateau.
    """
    items = []
    # --- Test Plant + PLNTST trigger egg (relocated from build_test_area)
    # North-center of the plateau, where the avatar first arrives from the
    # corridor. Same DD-007a wiring: SHAPE_TEST_PLANT (871, TypeShortmushroom)
    # frame 0 is the exact type+frame the hatch foreach destroys, and quality
    # 10 is the tag EggReapply destroys it by again on re-entry; the egg
    # (quality 283 = pinned EggPlantTest 1434 - 0x47F, npcnum 0x44 = +/-128
    # hatch box) sits 32 units south of the plant, well inside its own
    # 100-unit area search. Both at z=64, resting on the plateau floor.
    # Custom art since 2026-10-11 (docs/art-track.md contract 13): a spined
    # bulb on a (3,3,4) solid box, x (12704,12800] y (29312,29408], which
    # the Avatar walks round into the egg's box. It was shape 126 frame 0, a
    # blue-crystal ground tile he walked over.
    plant_x, plant_y = 12800, 29408
    items.append(MapItem.placed_item(
        x=plant_x, y=plant_y, z=TESTGROUNDS_Z,
        shape=SHAPE_TEST_PLANT, frame=0, quality=10  # Test Plant
    ))
    items.append(MapItem(
        x=plant_x, y=plant_y + 32, z=TESTGROUNDS_Z,
        shape=SHAPE_PLACEHOLDER_INVISIBLE_EGG, frame=0,
        quality=PLNTST_EGG_QUALITY, npcnum=PLNTST_EGG_NPCNUM
    ))

    # --- Sparse dressing (this is the vision-quest corner) --------------
    # Rock spires + bones of test-takers who did not survive. Kept at the
    # plateau EDGES/CORNERS, > 128 units off every scene coordinate and off
    # the north-center walk path, so they never block the teleport/pop
    # cells or the avatar's walk back (map_walkability asserts this).
    # The W-edge spire is at x 12416, not 12384 (2026-10-10): its box
    # x(12256,12384] pierced the rim's wall column x(12256,12288], and the
    # Avatar standing at (12352,29632) closed a paint-sort loop through
    # both (`Cycle in paint dependency graph 66 -> 1`, 225 lines in 4 s;
    # docs/research/2026-10-10-map10-paint-cycles.md section 5.2). At
    # x(12288,12416] it only touches the column under half-open boxes.
    # The broken spire stood in the SE corner at (13216,30144) until
    # 2026-10-10: box x(13088,13216] y(30016,30144], 33 units east of the
    # Avatar's teleport box and drawn after it, 42 of his pixels (5%) once
    # the flush rim stopped hiding him whole. In the NE corner it stands
    # behind every scene coordinate in the paint order.
    for dx, dy, shp, fr in [
        (12416, 29760, SHAPE_ROCK_SPIRE_CLUSTER, 0),  # rock spire, W edge
        (13248, 29520, SHAPE_BONES_A, 0),     # remains, E edge
        (12448, 30144, SHAPE_BONES_B, 0),     # remains, SW corner
        (13280, 29312, SHAPE_ROCK_SPIRE_CLUSTER, 2),  # broken spire, NE corner
    ]:
        items.append(MapItem.placed_item(x=dx, y=dy, z=TESTGROUNDS_Z,
                                         shape=shp, frame=fr))

    return items




def build_the_lake():
    """The Lake — water body with Water Zombies, the Passage Stone.

    Landscape pass 2026-09-15: the island is a 3x3 slab deck and the
    causeway a two-lane pier, both on the floor grid at z=8; the props
    that stood on open water (a mushroom, a chimney "ruin" with grass,
    the corner scrub) are on the shores, as stones and bones and a rock
    spire; the shores themselves are the vale's ground now that the
    holes either side of the lake are filled. The water body, the stone,
    the eggs and the zombie hatch sites are unchanged."""
    items = []
    x0, y0 = 11264, 15360
    lake_x, lake_y = x0 + 1024, y0 + 1536

    # REMOVED 2026-07-25 (H4): a 44-item "below-datum" layer used to live
    # here — solid ground under core water (z=-3), core lake water (z=-2),
    # ground under shore water (z=-2), shore water (z=-1), and ground under
    # shallow water (z=-1), keyed off a `shore_positions` list.
    #
    # z is UNSIGNED to the engine, so none of those negative values placed
    # anything BELOW the surface: they serialized to z=253-255 and rendered
    # as scattered debris floating ~253 units ABOVE the lake (confirmed by
    # isometric render, layers decomposed). They were also redundant: the
    # real lake body is glob-based, 1,026 SEA tiles at z=0, and every one of
    # the 21 stray water items was already covered by it (verified within
    # 512 units). The lake plays correctly without them, so they are simply
    # deleted rather than re-grounded.
    #
    # If a genuine lake BED is ever wanted, place it at a real low z under
    # the glob water — never at a negative z.

    # A ripple on the open water
    items.append(MapItem.placed_item(x=lake_x+512, y=lake_y-256, z=0,
                                     shape=SHAPE_WATER_SURFACE_SMALL_B, frame=0))

    # The island, the causeway and the pier (rewritten 2026-10-16, phase
    # B). The 1994 lake shot (screen02) stands where the old 3x3 slab deck
    # was: a broad rock shore at z 8 with the drowned body, and open water
    # where the pier used to run into the deck. So the island is the
    # shot's shore carried on past its frame, and the pier stops a cell
    # short of the shot, turns west along a deck and runs north beside the
    # window as a causeway onto the island — all rock at 8 over the water,
    # an 8-unit step up from the south shore (lv_map10_ground ISLAND,
    # CAUSEWAY, DECK, PIER; the field emits them). Crossing is MEANT to be
    # dangerous (Ragnar: "full of undead water creature it is").
    #
    # The rails (2026-10-11, playtest-2026-10-11-monsters2 finding 2, and
    # 2026-10-12 monsters3 finding 2): one course of retail's invisible
    # wall in the water's strip against every walkable shore — the
    # island's, the causeway's, the pier's and the lake's own banks — at
    # the shore's height (lv_map10_ground.rails, from the cells). A
    # zombie's blow plays the Avatar's stumbleBackwards, 64 units, and on
    # the old pier it took him over the edge into CLRWATER, which drowned
    # him; walled, a stumble or a step toward the water is refused
    # (test_monster_eggs F3/F4).
    island_x, island_y = lake_x + 1536, lake_y + 1536

    # The Passage Stone (quest steps 7-8) — the same TypeBushKey=798
    # "rock" that RAGNAR.UNK:835 spawns inside the quest bag popped to
    # RAGNAR_BAG_DROP (16447,25727,64): TWO sources of one stone is
    # 1994-intended (the island is the find; Ragnar's bag is the hint
    # path), and PLNTST's egg consumes whichever one the Avatar carries.
    # FRAME MUST BE 0 (the PLNTST foreach filters frame=0); quality 0 —
    # the check is type-only, and the old q50 meant nothing (shape 580
    # was SF_GENERIC too). Replaces the SI_FIXED magic-burst VFX (580)
    # that could never be picked up — the same trap the elemental
    # talismans hit (lv_shapes.SHAPE_TALISMAN_GEM). It lies on screen02's
    # shore at z 8, where it always was.
    items.append(MapItem.placed_item(
        x=island_x + 64, y=island_y - 64, z=8,
        shape=SHAPE_PASSAGE_STONE, frame=0, quality=0
    ))

    # Water Zombies (872). Until 2026-10-11 the five eggs stood in the
    # lake at z=0 with no trigger: nothing hatched them, and hatched by
    # hand they stood in CLRWATER, which drowns what stands on it
    # (playtest-2026-10-11-monsters finding 3). Now they haunt the pier
    # and the deck, in three one-shot waves (Douglas, 2026-10-11): two,
    # then one, then two, each hatched by its own MONEGG trigger across
    # the pier between its rails (lv_monster_eggs) as the Avatar walks
    # north. Wave 1, at the pier's south end and wholly on it (its box
    # used to reach the shore, where a blow could stumble him into the
    # lake beside the pier), wakes two on the pier's south half; wave 2,
    # halfway along, one on its north half; wave 3, a pier tile short of
    # the deck, two on the deck round the Passage Stone. Each wave's
    # trigger lies north of the last wave's zombies, so it fires only once
    # he has got past them, and every zombie sees him at once
    # (lv_monster_eggs.wakes_at_once). One-shot (frame 1): MONEGG destroys
    # each egg as it hatches, so a player who backs off the pier to heal
    # and comes on again meets no fresh ones; they come back only with the
    # map, like every FIXED item. Every spot is on rock at z=8 with 32
    # units of it, and no rail, on every side (test_monster_eggs.py).
    # The stone has a second source, Ragnar's bag, so the island and its
    # zombies can be left alone.
    #
    # MOVED 2026-10-16 (phase B): wave 2's egg from (13888,19008) and wave
    # 3's trigger from (13824,18816), both in what screen02 shows as open
    # water, onto the causeway (x 13184..13439) the pier now turns onto:
    # wave 2 waits on it ahead of the turn, wave 3 fires where it meets
    # the island, the two by the Passage Stone on the shot's own shore.
    for group, trigger, box, eggs in (
            (1, (13824, 20352, 8), (4, 2), [(13888, 19936), (13792, 19744)]),
            (2, (13824, 19456, 8), (4, 1), [(13344, 19008)]),
            (8, (13312, 18816, 8), (4, 1), [(13855, 18271), (14016, 18400)])):
        items.extend(monster_group(
            group, trigger=trigger, box=box,
            eggs=[(x, y, 8, SHAPE_MON_ZOMBIE) for x, y in eggs]))

    # The shores: stones, small rocks, bones, a spire or two — on the
    # ground outside the water (north y < 15360, south y > 20480, west
    # x < 11264, east x > 15360), clear of the tracks.
    props(items, [
        (11903, 15295, SHAPE_STONE_SMALL, 20), (12543, 15231, SHAPE_RUBBLE_SMALL, 6),
        (13311, 15327, SHAPE_STONE_SMALL, 22), (13887, 15263, SHAPE_MUSHROOM_CLUSTER, 18),
        (14591, 15295, SHAPE_RUBBLE_SMALL, 8), (12159, 15199, SHAPE_BONES_A, 1),
        (11903, 20575, SHAPE_RUBBLE_SMALL, 7), (12799, 20543, SHAPE_STONE_SMALL, 19),
        (12543, 20671, SHAPE_BONES_B, 0), (14655, 20735, SHAPE_MUSHROOM_CLUSTER, 20),
        (11135, 17151, SHAPE_ROCK_SPIRE_CLUSTER, 6), (11135, 18815, SHAPE_RUBBLE_SMALL, 2),
        (11263, 16383, SHAPE_STONE_SMALL, 24), (11007, 19967, SHAPE_TREE_TRUNK, 6),
        (15743, 15743, SHAPE_ROCK_SPIRE_CLUSTER, 8), (15615, 17919, SHAPE_STONE_SMALL, 25),
        (15679, 19583, SHAPE_RUBBLE_SMALL, 7), (15743, 16639, SHAPE_TREE_STUMP_GREY, 3),
    ])

    # Wilderness kith (76, 85-105 hp, 12-16 a blow), between zones on dry
    # ground. They were in the lake's NW and SE corners, in the water.
    # Each stands 897 units (x or y, from its box) off the shortest walk
    # between the quest's stops, outside the +/-768 square in which
    # CombatProcess::seekTarget picks a target, so a player who keeps to
    # the ways never meets one. Its trigger is off the way, between it and
    # the way, 544-800 short of it: a player who strays toward it fires
    # the trigger inside its seek square, and it hatches in the fast area
    # and fights (lv_monster_eggs). Until 2026-10-11 the triggers stood on
    # the ways 1,180-1,410 short, where a kith hatched outside the fast
    # area, or loitered out of it, and came passive or not at all
    # (playtest-2026-10-11-monsters2 finding 1). The box is (5, 5): a
    # range byte of 0x64-0x74 would sit in the engine's npcNum promotion
    # window (test_engine_patch.py). Group 3's egg stood at (10944,17312)
    # until 2026-10-17; screen09's tarn shelf (RELIEF, z 64, to y 17151)
    # put its face in the kith's 192 body and the shelf between it and its
    # trigger, so it moved west to the shelf's foot, x 10463: 32 clear of
    # the shelf face (x 10496) and of the scrub prop at x 10239, the walk
    # north to the trigger straight (screen09.json pin_moves).
    items.extend(monster_group(
        3, trigger=(10144, 16512, 0), box=(5, 5),
        eggs=[(10463, 17312, 0, SHAPE_MON_WILDERNESS)]))
    items.extend(monster_group(
        4, trigger=(15776, 21696, 0), box=(5, 5),
        eggs=[(15232, 22016, 0, SHAPE_MON_WILDERNESS)]))

    return items


def build_sacred_circle():
    """Sacred Circle — ceremonial gathering place for Shield restoration.

    Landscape pass 2026-09-15: eight standing stones (38, the plain grey
    monoliths) on the ring where the mushroom clusters stood (decorative,
    map_pins.json), a 5x5 paving of slabs at the centre, the Sacred Rock
    a rounded monolith set just off the exact centre — (20480,16896) is
    map_walkability's MAP10_ROOT_SEED and must stay standable — and dead
    trees beyond the ring. The special root, the EggShades egg and every
    SHADES scene coordinate are untouched."""
    items = []
    x0, y0 = 18432, 15360
    center_x, center_y = x0 + 2048, y0 + 1536

    # Paving under the ceremony: zero-height LAND (71, the overlay
    # flat), so the scene's teleport-ins (20224..20672, 17216..17472)
    # stay walkable.
    tile_run(items, span(20096, 20736), span(16512, 17152), 0,
             SHAPE_SLAB_PALE, PALE_FRAMES)

    # The ring: eight monoliths on the 768 radius
    import math
    for i in range(8):
        angle = i * (2 * math.pi / 8)
        sx = center_x + int(768 * math.cos(angle))
        sy = center_y + int(768 * math.sin(angle))
        items.append(MapItem.placed_item(x=sx, y=sy, z=0,
                                         shape=SHAPE_STANDING_STONE,
                                         frame=2 + i % 2))

    # The special root (quest steps 9-10, poison-cure arc). Ezrekal's hint
    # (EZREKAL.UNK:3108): the nightmare-tea root "By the standing stones it
    # grew" — the Sacred Circle's stone ring IS the game's standing stones,
    # so the root rests in the open barren ground just outside the east
    # stone. SHAPE_SPECIAL_ROOT (869, custom art since 2026-10-11,
    # docs/art-track.md contract 12), FRAME 0 to match both of Ezrekal's
    # `foreach (type = TypeWeedz) and (frame = 0)` filters
    # (TYPE_SHAPES.TypeWeedz == 869). Carryable (not SI_FIXED); walkability
    # asserted by map_walkability.run_map10 section (e).
    items.append(MapItem.placed_item(
        x=21376, y=16640, z=0,
        shape=SHAPE_SPECIAL_ROOT, frame=0, quality=0
    ))

    # The Sacred Rock (quality 100, decorative; nothing reads it, see
    # map_pins.json). Was a 721 chimney on the centre point; a 4x4 rock
    # there would block the seed cell, so it stands 64 units north-west.
    # CUSTOM ART since 2026-09-20 (art track item 3, docs/art-track.md
    # contract 3): shape 863, a ninth standing stone kin to the eight on
    # the ring. It was shape 66 frame 4, a dark striated lump that read as
    # rubble from a cave mouth, 6 px taller than the ring it stands in.
    # The position is frozen: the box clears MAP10_ROOT_SEED (20480,
    # 16896) by exactly one world unit on each axis.
    items.append(MapItem.placed_item(
        x=20415, y=16831, z=0,
        shape=SHAPE_SACRED_ROCK, frame=0, quality=100
    ))

    # Grass at the four approaches
    for sx, sy in [(center_x-1024, center_y), (center_x+1024, center_y),
                   (center_x, center_y-1024), (center_x, center_y+1024)]:
        items.append(MapItem.placed_item(x=sx, y=sy, z=0, shape=SHAPE_GRASS_PATCH_A, frame=0))

    # EGGSHADES trigger (quest steps 14-15, the shield-restoration ceremony
    # — carries the ONLY avatarPoisoned cure in the corpus, SHADES.UNK:429).
    # UnkEgg dispatch: class = quality + 0x47F, so quality 294 -> EggShades
    # (1445, manifest-pinned). Was quality=2 (a label, not a class id — it
    # selected MONEGG). npcNum packs the hatch box per DD-007a (x range =
    # high nibble, y range = low nibble, ×32 units): 0x88 = ±256, wide
    # enough that visiting the circle center reliably crosses it. The
    # scene's teleport-ins land at (20224-20672, 17216-17472) — see
    # lv-patched/SHADES.UNK header for the coordinate retarget.
    items.append(MapItem(
        x=center_x, y=center_y + 256, z=0,
        shape=SHAPE_PLACEHOLDER_INVISIBLE_EGG, frame=0,
        quality=294, npcnum=0x88  # EggShades 1445
    ))

    # Beyond the ring
    props(items, [
        (19199, 16127, SHAPE_TREE_DEAD, 1),
        (21759, 17791, SHAPE_TREE_DEAD, 3),
        (19583, 17663, SHAPE_TREE_TRUNK, 7),
        (21887, 15871, SHAPE_ROCK_SPIRE_CLUSTER, 9),
        (22015, 16127, SHAPE_RUBBLE_SMALL, 8),
        (18815, 17919, SHAPE_RUBBLE_PILE, 2),
    ])
    return items


def build_cloud_approach():
    """Cloud Cliffs Approach — the valley to the foot of the cliffs.

    Landscape pass 2026-09-15: the eight "climbing" ground tiles at z =
    0, 2, 4 … 14 were phantom standing levels (nothing on the 4-unit
    lattice but the first), and the pinned pad, gate and trigger at z=8
    stood on the one at z=6. They now stand on a stone terrace — one
    tier of raised flagstone, top exactly 8 — at the valley's end, the
    gate in two stone stubs with a lane open either side (lock 170
    matches no key on any map, as on Map 13, so the way must stay open),
    canyon walls two courses high either side of the terrace, the track
    coming down the valley between dead trees and rock. The 256-spaced
    pickets went: the west line is the rim, the east bordered ground."""
    items = []
    x0, y0 = 5120, 20480

    # The terrace: (6527..7807] x (22911..24575], top z=8
    terrace_xs = span(6528, 7808)
    terrace_ys = span(22912, 24576)
    items.extend(raised_platform(terrace_xs, terrace_ys, 0))

    # Locked gate requiring Key to the Clouds
    CLIFF_KEY_ID = 170
    items.append(MapItem.placed_item(
        x=x0 + 2048, y=y0 + 3072, z=8,
        shape=SHAPE_LARGE_GATE, frame=0, quality=CLIFF_KEY_ID
    ))

    # Teleport TRIGGER (ID 206) past the gate -> Map 13
    # SWAPPED 2026-07-31: the 07-25 relocation comments were written under
    # the pre-771d5c7 inverted helper names, so the ACTIVE trigger had been
    # built on the quest egress line (the playtest C1 bounce class). Ids and
    # roles unchanged; positions exchanged. See build_map_13's base pair.
    # Restores the design too: the KEY-LOCKED GATE (y0+3072) now stands
    # between the vale and the active trigger, so Tyorvi's key gates the
    # cliffs again.
    items.append(MapItem.teleport_target(
        x=x0 + 2048, y=y0 + 2816, z=8,
        teleport_id=206
    ))
    items.append(reapply_egg(x0 + 2048, y0 + 2816, 8))

    # Teleport DEST (ID 207) for returns from Map 13
    items.append(MapItem.teleporter(
        x=x0 + 2048, y=y0 + 3584, z=8,
        teleport_id=207, dest_npc=207, dest_map=13
    ))

    # Gate stubs on the terrace, two courses (z 8 and 48): west
    # (6527..6911], east (7295..7807]; the gate box is (7040..7168], so
    # the lanes (6911..7040] and (7168..7295] are open.
    for z in (8, 48):
        for x in (6655, 6783, 6911):
            items.append(MapItem.placed_item(x=x, y=23552, z=z,
                                             shape=WALL_EW, frame=WALL_PLAIN))
        for x in (7423, 7551, 7679, 7807):
            items.append(MapItem.placed_item(x=x, y=23552, z=z,
                                             shape=WALL_EW, frame=WALL_PLAIN))

    # Canyon walls either side of the terrace, y (22400..24576]
    cliff_run_y(items, 22400, 24576, 6527, 96, phase=1)
    cliff_run_y(items, 22400, 24576, 7839, 96, phase=4)

    # The valley floor
    props(items, [
        (5887, 21247, SHAPE_TREE_DEAD, 3),
        (8447, 21887, SHAPE_ROCK_SPIRE_CLUSTER, 2),
        (8319, 22143, SHAPE_RUBBLE_PILE, 3),
        (6015, 23423, SHAPE_TREE_TRUNK, 7),
        (8575, 23935, SHAPE_TREE_STUMP_GREY, 4),
        (5631, 22399, SHAPE_RUBBLE_SMALL, 6),
        (8063, 20991, SHAPE_TREE_TRUNK, 6),
        (6143, 20735, SHAPE_STONE_SMALL, 4),
        (8703, 24319, SHAPE_ROCK_SPIRE_CLUSTER, 7),
    ])
    return items


def build_temple_approach():
    """Ancient Temple Approach — the processional, the shelf, the pit.

    Phase B (2026-10-16): the 1994 shot of the temple (screen17) is a
    stair of cobble step blocks going down between gargoyles off a z 112
    rock shelf into a pit — the sunken temple. The shelf is the field's
    (lv_map10_ground RELIEF), the shot's stair is the shot's own; here:

      * the processional: three lanes of pale stone from the vale south
        to the foot of the shelf's north stair (lv_map10_ground STAIRS
        'temple', thirteen 8-unit steps up to 104, a step below the
        shelf), between two pairs of temple columns;
      * on the shelf, between the shot's gargoyles at the head of its
        stair, the arrival pad 210 and its eggs — MOVED from
        (18432,22784,0) on the old paved way to (18432,22719,112)
        (vignettes/screen17.json pin_moves): every return from Map 18
        lands at the top of the 1994 stair and walks north off the shelf;
      * the shot's stair carried on below its frame, four more steps
        (tops 32, 24, 16, 8) to the pit floor;
      * the pit floor, open to the forecourt south of it, and trigger 211
        on it where it always was, paved, its hatch box narrowed to the
        strip a walk S off the stair comes down (TRIGGER_211_RANGE).

    The shape-114 gate (lock 180) was removed 2026-09-25, because no key in
    1994 or here opens it and the temple's barrier is the crack
    (docs/reviews/2026-09-25-keyless-gates.md); its stubs went with the
    old paved way in phase B."""
    items = []
    x0, y0 = 16384, 20480

    # The processional: three lanes x (18304..18687] from y 20480 to the
    # stair foot at 21600, zero-height LAND (71) on the floor grid; the
    # forecourt round trigger 211, x (18048..18815], y (23552..24575].
    tile_run(items, (18431, 18559, 18687), span(20480, 21504), 0,
             SHAPE_SLAB_PALE, PALE_FRAMES)
    tile_run(items, span(18048, 18816), span(23552, 24576), 0,
             SHAPE_SLAB_PALE, PALE_FRAMES)
    # Columns flanking the processional
    for y in (20863, 21375):
        items.extend(column(18239, y))
        items.extend(column(18815, y))
    # Columns flanking the forecourt
    for y in (23935, 24447):
        items.extend(column(17919, y))
        items.extend(column(18943, y))

    # Teleport ARRIVAL PAD (ID 210) — arrival from Map 18, on the shelf at
    # the head of the 1994 stair (see the docstring).
    # SWAPPED 2026-07-31: the 07-25 relocation comments were written under
    # the pre-771d5c7 inverted helper names, so the ACTIVE trigger had been
    # built on the quest egress line (the playtest C1 bounce class). Ids and
    # roles unchanged; positions exchanged. See build_map_13's base pair.
    items.append(MapItem.teleport_target(x=PAD_210[0], y=PAD_210[1],
                                         z=PAD_210[2], teleport_id=210))
    items.append(reapply_egg(*PAD_210))

    # Teleport TRIGGER (ID 211) -> Map 18, on the pit floor south of the
    # stair; its hatch box is TRIGGER_211_RANGE's (below).
    items.append(MapItem.teleporter(
        x=x0 + 2048, y=y0 + 3072, z=0,
        teleport_id=211, dest_npc=TRIGGER_211_RANGE, dest_map=18
    ))

    # EGGENDGAME trigger (quest step 18, the restoration finale).
    # quality 299 -> class 1450 EggEndgame (lv-new/ENDGAME.UNK,
    # manifest-pinned).
    #
    # ON THE ARRIVAL PAD (moved 2026-09-29). EggEndgame's text is about the
    # vale, not the shrine, so it fires as the player comes back out of the
    # temple into the Vale. It used to sit 768 units north of the pad on
    # the middle lane, commented "the only path back", and in-engine it was
    # not: a player could step west off the pad and walk to Ezrekal around
    # it (docs/playtest-2026-09-27-bag-ezrekal.md, finding 1). Since the bag
    # moved to Ezrekal, that player got the bag with no top-up process,
    # because this scene is what spawns topUpReagents. Centred on target
    # 210, where every return from Map 18 lands, the box contains the
    # arrival point, and the engine hatches a non-teleport egg the moment
    # the Avatar is inside (EggHatcherProcess::run skips only TeleportEggs
    # after a teleport). It moved up onto the shelf with the pad (phase B):
    # z 112, so its hatch z span (64, 160] holds the arrival.
    #
    # npcnum 0x86 = x +/-256, y +/-192: box x 18176..18688, y 22528..22912,
    # clear of trigger 211's box (x 18336..18528, y 23456..23648, and z 0;
    # TRIGGER_211_RANGE). Not 0x66: range
    # bytes 100-116 fall in the engine's Actor promotion window
    # (test_engine_patch.py).
    #
    # Gate chain: hatch() returns unless `godsFree`, which only
    # EggAOCeremony (Map 18 altar, quality 296) sets, so arriving before
    # the ceremony does nothing. Its replay guard `endgameStarted` is real
    # (manifest bit 1814, compiled as push/pop global 0716h) and is covered
    # by test_uc_eggs P10.
    items.append(MapItem(
        x=PAD_210[0], y=PAD_210[1], z=PAD_210[2],
        shape=SHAPE_PLACEHOLDER_INVISIBLE_EGG, frame=0,
        quality=299, npcnum=0x86  # EggEndgame 1450
    ))

    # Either side of the way
    props(items, [
        (17151, 21247, SHAPE_TREE_DEAD, 1),
        (19711, 21759, SHAPE_TREE_DEAD, 3),
        (17023, 22911, SHAPE_TREE_TRUNK, 6),
        (19839, 23167, SHAPE_TREE_STUMP_GREY, 2),
        (17407, 23935, SHAPE_ROCK_SPIRE_CLUSTER, 3),
        (19583, 24319, SHAPE_RUBBLE_PILE, 2),
        (19967, 20863, SHAPE_RUBBLE_SMALL, 6),
        (16767, 20735, SHAPE_STONE_SMALL, 8),
    ])
    return items


# Arrival pad 210 (from Map 18) and its EggReapply and EggEndgame: on the
# temple shelf at the head of screen17's stair, between its gargoyles. y
# 22719, flush north of where the solve put the stair's top block (107:1,
# y 22720..22751 to z 120); since that block slid down the view ray
# (RAY_SLIDES) it lies at y 22688..22719, x 18304..18399, top 112, under
# the pad's west half, and the arriving body still overlaps no solid
# (avatar_mover.resting).
PAD_210 = (18432, 22719, 112)

# Trigger 211's hatch box: npcNum 0x33, x and y +/-96 about (18432,23552),
# so it fires for the body's max corner in x [18336, 18592), y [23456,
# 23712), z (-48, 48] (EggHatcherProcess::run, avatar_mover.hatch_box).
# That is the strip a walk S off screen17's stair comes down: the shot's
# z 112 cell x (18431,18559], y (23295,23423] stands under the stair's
# foot, and a walk S slides off its north-west corner and runs on S down
# its west face, x 18336..18399, into the box. Until 2026-10-24 it was
# 0xD3, x +/-416: x [18016, 18912), the pit's whole mouth (x 18111..19071)
# but its east 160 units. A walk off the foot SW toward the villages fired
# it and sent the Avatar back to Map 18 right after the endgame, 306 of
# 336 holds from the landing (docs/playtest-2026-10-17-replay-leg6.md
# finding 3). Now the mouth is open west of the box (x 18111..18335) and
# east of it (18592..19071), and the box lies inside the old one, so no
# position fires it that did not before.
# test_route_reach.temple_stair_foot holds both sides of that.
TRIGGER_211_RANGE = 0x33


def build_moriens_ruins():
    """Birthplace of Moriens — optional lore ruins.

    Landscape pass 2026-09-15: was four "broken" wood-wall pieces, three
    mushrooms and a stool (158) as the "plaque/inscription trigger" — a
    stool, and nothing read its quality 5. Now a small stone ruin:
    cracked paving, two tall columns and two broken stubs, rubble, a dead
    tree, remains. The track to the Passage Test grounds passes east of it.

    Since 2026-09-25 a one-course wall stub stands between the two tall
    columns and carries a gold plaque on its south face: quality 66 of
    TypeNSGoldPlaque, "BIRTHPLACE*OF*MORIENS", which the 1994 PLAQUENS.UNK
    already holds (marked for this expansion, 8/10/94). Shape 614 with
    npcnum 235, as Map 17's plaques are (docs/art-track.md contract 6)."""
    items = []
    x0, y0 = 11264, 21504

    tile_run(items, (12159, 12287, 12415), span(22272, 22784), 0,
             SHAPE_ROCK_SLAB_CRACKED, CRACKED_FRAMES)
    props(items, [
        (12063, 22207, SHAPE_COLUMN_RUIN_TALL, 0),
        (12447, 22207, SHAPE_COLUMN_RUIN_TALL, 0),
        (12063, 22783, SHAPE_PILLAR_STONE, 2),
        (12447, 22783, SHAPE_PILLAR_STONE, 7),
        (12287, 22335, SHAPE_STONE_BROKEN, 0),
        (12543, 22463, SHAPE_RUBBLE_PILE, 2),
        (11967, 22591, SHAPE_RUBBLE_SMALL, 7),
        (12351, 22591, SHAPE_BONES_A, 0),
        (11647, 22911, SHAPE_TREE_DEAD, 1),
        (13439, 23679, SHAPE_TREE_TRUNK, 6),
        (11519, 21887, 899, 3),
        (13567, 22143, SHAPE_STONE_SMALL, 6),
    ])
    # The inscription: a wall stub between the tall columns (x 12096..12351,
    # 32 deep, 40 tall) and the plaque on its south face, centred, at z=16.
    for x in (12223, 12351):
        items.append(MapItem.placed_item(x=x, y=22207, z=0,
                                         shape=WALL_EW, frame=WALL_PLAIN))
    items.append(MapItem(x=12255, y=22208, z=16,
                         shape=SHAPE_PLAQUE_ON_Y_WALL, frame=0, quality=66,
                         npcnum=NPCNUM_GOLD_PLAQUE))
    return items


def build_ragnar_cache_ruins():
    """Lakeside ruins cache — real ground under Ragnar's bag drop.

    RAGNAR.UNK pops the quest bag (Passage stone inside) at the 1994
    coordinate RAGNAR_BAG_DROP = (16447,25727,64). On our rebuilt Map 10
    that point was VOID: every zone and connector stopped at y=24576, and
    nothing put ground (let alone ground at z~64) beneath it. This pad:
      - extends barren terrain 2x3 chunks south of the Temple Approach
        (TERRAIN table), so the site is walkable from the approach;
      - stands a large boulder under the exact drop point: its LAND crown
        tops out at z=56 and the bag pops 8 units above it, visually
        resting on it (pop() places exactly — no gravity);
      - climbs to the crown by a stepped stair of raised-flagstone tiers
        east of the boulder, tops at 8, 16 … 48, then the crown at 56.
        Until 2026-09-15 this was two slabs at z=24 and z=48 — 16- and
        24-unit risers the walking actor refuses (0/±4/±8 only;
        .claude/rules/map-geometry.md); map_walkability's STEP_Z=24 model
        passed them and test_route_reach's exact model did not;
      - dresses the pad as the "ruins" Ragnar describes: a broken pillar,
        a fallen column, cracked paving, scatter.
    """
    items = []
    x0, y0 = 16384, 24576
    bx, by, bz = RAGNAR_BAG_DROP

    # The plinth: boulder crown at 0+56=56. Origin at (bx+32, by+32) so
    # the 64x64 footprint (max-corner origin) is centered on the drop.
    items.append(MapItem.placed_item(
        x=bx + 32, y=by + 32, z=0,
        shape=SHAPE_BOULDER_LARGE, frame=0
    ))
    # The stair: column j (1..6) east of the boulder tops out at 56 - 8j
    # and is solid flagstone down to the ground.
    for j in range(1, 7):
        for t in range(7 - j):
            items.extend(raised_platform(
                [bx + 32 + 128 * j], [by + 64], 8 * t))

    # Ruin dressing
    props(items, [
        # VQ-005: both pillars stand on the painted yard floor, clear of
        # the rim and bag stair. The old pale pillar had support on the
        # rim, but its sprite's base projected beyond the crest's paint.
        (bx + 288, by - 672, SHAPE_PILLAR_STONE, 2),
        (bx + 544, by - 576, SHAPE_COLUMN_RUIN_TALL, 0),
        (bx + 288, by - 64, SHAPE_ROCK_SLAB_CRACKED, 3),
        (bx - 32, by + 224, SHAPE_ROCK_SLAB_CRACKED, 1),
        (bx + 32, by + 352, SHAPE_STONE_BROKEN, 1),
        (bx - 224, by + 128, SHAPE_GRASS_PATCH_A, 1),
        (bx + 192, by + 192, SHAPE_GRASS_PATCH_B, 0),
        (bx + 480, by + 288, SHAPE_RUBBLE_SMALL, 7),
        (bx - 96, by - 480, SHAPE_TREE_TRUNK, 8),
    ])

    # ── The hat and the whip. NEW PLACEMENTS 2026-07-26 (orphan triage,
    # decision D). TypeFedora (FEDORA.UNK) -> class 1258 and TypeBullwhip
    # (BULLWHIP.UNK) -> class 1256 were compiled but unreachable. Both are
    # pure flavour: each implements only look(), barking "Fedora" and
    # "Bullwhip" respectively. Nothing reads them, no quest touches them.
    #
    # A fedora beside a bullwhip in a set of overgrown ruins is the 1994
    # authors' joke, and putting the pair at the foot of the ruin dais is
    # the one placement that makes it land. They are OUTSIDE the plinth and
    # its climbing steps so they cannot interfere with reaching Ragnar's
    # quest bag on the crown.
    #
    # Both shapes are stand-ins (see lv_shapes.py): U8 has no fedora and no
    # whip anywhere in its shape table, so these are a helmet and a coiled
    # rope. The joke reads from the bark, not the sprite.
    items.append(MapItem(x=bx - 288, y=by + 256, z=0,
                         shape=SHAPE_HAT, frame=0, npcnum=NPCNUM_FEDORA))
    items.append(MapItem(x=bx - 352, y=by + 288, z=0,
                         shape=SHAPE_ROPE, frame=0, npcnum=NPCNUM_BULLWHIP))

    return items


def build_wilderness():
    """The open ground between the zones: outcrops, dead trees, stones,
    the small ruins the wilderness always had (a broken pillar and a
    slab where a chimney stood), and the three prowler eggs. Ground and
    the tracks come from build_terrain()/build_tracks(); this used to be
    build_connecting_terrain, twenty terrain rectangles plus dots."""
    items = []

    # Outcrops: a spire cluster with rubble and a stone at its foot
    for x, y, f in [(8703, 8063, 0), (10239, 9599, 3), (16639, 7551, 1),
                    (7935, 12799, 5), (9599, 14847, 2), (16511, 12543, 9),
                    (10111, 17151, 11), (17023, 16895, 4), (8319, 21631, 6),
                    (14719, 22399, 8), (21375, 12415, 10), (4735, 3839, 7),
                    (20351, 3199, 0), (9087, 3455, 5)]:
        props(items, [
            (x, y, SHAPE_ROCK_SPIRE_CLUSTER, f),
            (x + 128, y + 96, SHAPE_RUBBLE_PILE, 2 + f % 2),
            (x - 96, y + 160, SHAPE_STONE_SMALL, f % 9),
        ])

    # Dead trees
    props(items, [
        (6655, 2431, SHAPE_TREE_DEAD, 1), (18943, 2047, SHAPE_TREE_DEAD, 3),
        (10239, 7167, SHAPE_TREE_DEAD, 0), (15359, 9855, SHAPE_TREE_DEAD, 1),
        (8319, 10111, SHAPE_TREE_DEAD, 3), (6015, 13439, SHAPE_TREE_DEAD, 1),
        (16895, 14079, SHAPE_TREE_DEAD, 3), (20735, 13567, SHAPE_TREE_DEAD, 1),
        (10495, 19839, SHAPE_TREE_DEAD, 0), (15231, 21503, SHAPE_TREE_DEAD, 3),
        (3583, 8319, SHAPE_TREE_TRUNK, 6), (12543, 6271, SHAPE_TREE_TRUNK, 7),
        (14335, 4223, SHAPE_TREE_TRUNK, 9), (9855, 12159, SHAPE_TREE_TRUNK, 6),
        (12031, 9343, SHAPE_TREE_STUMP_GREY, 0), (17151, 4223, SHAPE_TREE_STUMP_GREY, 3),
        (9855, 18559, SHAPE_TREE_STUMP_GREY, 1), (17663, 18175, SHAPE_TREE_STUMP_GREY, 4),
        (7167, 4351, SHAPE_BUSH, 4), (11391, 3071, SHAPE_BUSH, 5),
        (16255, 3455, SHAPE_BUSH, 4), (14207, 8319, SHAPE_BUSH, 5),
        (8831, 16511, SHAPE_BUSH, 4), (16383, 17279, SHAPE_BUSH, 5),
        (12799, 7167, SHAPE_MUSHROOM_CLUSTER, 19), (9471, 10879, SHAPE_MUSHROOM_CLUSTER, 21),
        (15743, 12287, SHAPE_MUSHROOM_CLUSTER, 23), (10751, 15743, SHAPE_MUSHROOM_CLUSTER, 18),
    ])

    # The small ruins ("cool fallen ruins"): a broken pillar, a fallen
    # block, a cracked slab, grass
    for x, y in [(8959, 8447), (15487, 8959), (7935, 13567), (15999, 13439),
                 (9983, 18943), (14463, 18943)]:
        props(items, [
            (x, y, SHAPE_PILLAR_STONE, 2),
            (x + 96, y + 64, SHAPE_STONE_BROKEN, 0),
            (x - 32, y + 192, SHAPE_ROCK_SLAB_CRACKED, 5),
            (x + 160, y - 96, SHAPE_GRASS_PATCH_A, 0),
        ])

    # Wilderness spiders (807, 2-6 hp: vermin), one group each. Each
    # MONEGG trigger (lv_monster_eggs) stands between its spider and the
    # way it was on, 544-640 short of the egg, where every position in its
    # box is in the spider's seek square: it hatches inside the fast area
    # and comes at once. They were on the ways 900-1,350 short, and the
    # spiders of groups 5 and 6 hatched outside the fast area, passive
    # (playtest-2026-10-11-monsters2 finding 1). Groups 5-7 (1-4 and 8:
    # build_the_lake).
    for group, trigger, egg in ((5, (9044, 13544, 0), (8500, 13000, 0)),
                                (6, (16044, 12360, 0), (15500, 13000, 0)),
                                (7, (9860, 19532, 0), (10500, 19500, 0))):
        items.extend(monster_group(group, trigger=trigger, box=(5, 5),
                                   eggs=[egg + (SHAPE_MON_PROWLER,)]))

    return items


# === THE TRACKS ===
# Worn earth, every polyline point a tile max corner: lv_map10_ground
# lays an earth band 1-3 tiles wide along each (the 1994 roads are earth,
# 4/386, not 425 cobble). Each village lane keeps clear of the huts' wall
# boxes, and no tier stands on one (the check at the end of build_map_10
# proves both).
RIVERBED = [(11135, 5119), (10751, 7167), (11135, 9215), (10623, 11263),
            (10879, 13311), (11391, 14975), (11519, 15359)]
TRACKS = [
    # the arrival court south to the fork
    [(13311, 2943), (13311, 4479)],
    # the fork west to Hoskuld and its gathering slab
    [(13311, 4479), (11007, 5375), (9343, 6655), (8703, 7807), (7935, 7807),
     (7679, 7039), (5375, 7039), (5247, 7167)],
    # the fork east into Gunnar, past the well, south of the rock Atli's
    # yard is sunk in (screen19), across the commons (screen20) to
    # Hrodny's door
    [(13311, 4479), (15615, 5375), (17279, 6655), (17279, 7935),
     (18303, 7935), (19839, 8063), (20607, 8447), (20863, 8959)],
    # the fork south past Ezrekal's, down the lake's east shore, to the
    # temple processional and the foot of the shelf's stair
    [(13311, 4479), (13311, 7679), (13567, 10367), (14207, 11775),
     (14207, 13183), (14591, 14975), (15487, 14975), (15487, 15871),
     (15487, 18431),
     (16511, 19455), (17919, 20223), (18431, 20607), (18431, 21503)],
    # east shore to the Sacred Circle
    [(15487, 15871), (16639, 15871), (18815, 16255), (19583, 16895)],
    # Hoskuld south to the west clearing and the cloud approach
    [(5247, 7167), (5375, 8319), (5887, 9215), (5887, 10495), (5247, 11135),
     (5247, 13055), (5631, 15359), (6143, 16895), (6655, 18943),
     (7167, 20607), (7167, 22783)],
    # Gunnar south to the Sacred Circle, east of screen20's rock
    [(20863, 8959), (20863, 9727), (20735, 10495), (20479, 11135),
     (20479, 15743)],
    # the lake's south shore, Moriens' ruins, the corridor to the ramp
    [(15487, 18431), (15487, 20607), (13823, 20607), (12799, 21631),
     (12799, 24575), (12799, 28159)],
]


def track_cells():
    """The 128 cells the track polylines cross (lv_landscape.track's
    staircase), for the check below; the earth itself is the field's."""
    cells = set()
    for pts in TRACKS:
        cells.update(track([], pts, width=1))
    return cells


def build_tracks():
    """The dry gravel riverbed from the north rim to the lake (6 draws over
    the 301/4 floor: it has neither SI_DRAW nor SI_OCCL)."""
    items = []
    track(items, RIVERBED, shape=SHAPE_GRAVEL, frames=GRAVEL_FRAMES)
    return items


# Footpads (tiles) of every solid prop this builder places at ground level,
# for the track check. LAND tiles with no height (301, 299, 386, 6, 92, 94,
# 3, 242) and walk-through bushes (434) are not blockers and are not listed.
_PROP_PADS = {
    66: (4, 4), 75: (7, 7), 56: (2, 2), 152: (2, 2), 524: (3, 3), 526: (2, 2),
    553: (1, 1), 394: (2, 2), 293: (1, 1), 494: (2, 1), 38: (2, 2), 62: (4, 1),
    130: (1, 4), 61: (1, 1), 249: (1, 1), 113: (4, 4), 15: (4, 1), 26: (4, 1),
    32: (1, 4), 29: (1, 1), 856: (4, 1), 857: (1, 4), 858: (1, 1), 664: (2, 2),
    796: (2, 2), 205: (5, 3), 208: (3, 5), 307: (4, 2), 618: (3, 2),
    235: (3, 4), 237: (4, 3), 114: (4, 4), 65: (2, 2),
}


def _check_tracks(items, field):
    """Every track cell is ground at z 0 (no tier, water or lava stands on
    a way), and no solid prop stands on one (Box::overlaps arithmetic on
    max-corner boxes)."""
    cells = track_cells()
    for tx, ty in cells:
        c = (tx // 128, ty // 128)
        assert field.H.get(c) == 0 and c not in field.water and \
            c not in field.lava, f'track tile ({tx},{ty}) on {field.H.get(c)}'
    for it in items:
        pad = _PROP_PADS.get(it.shape)
        if pad is None or it.z != 0 or it.is_glob_egg:
            continue
        w, h = pad[0] * 32, pad[1] * 32
        for tx, ty in cells:
            if it.x - w < tx and tx - 128 < it.x and \
               it.y - h < ty and ty - 128 < it.y:
                raise AssertionError(
                    f'shape {it.shape} at ({it.x},{it.y}) stands on the '
                    f'track tile ({tx},{ty})')


_NOT_PROPS = {2, 73, 500, 508}        # glob, usecode, monster, teleport eggs


def lift_props(items, field):
    """A zone builder's prop standing on a cell the field has raised (a
    tier the 1994 shots put there) goes up onto it: the dead trees, rocks
    and ruins of the old flat vale keep their places on the new ground.
    Pins never sit there (map10_field asserts it)."""
    out = []
    for it in items:
        h = field.lift_H.get((it.x // 128, it.y // 128), 0)
        if it.shape not in _NOT_PROPS and it.x >= 64 and h >= 16 and \
                it.z < h - 8:
            it = MapItem.from_bytes(it.to_bytes())
            it.z += h
        out.append(it)
    return out


def shot_completions():
    """What the shots show only part of, finished inside their windows
    after the stamp (which clears every generated item there): the huts
    the village shots show two sides of (lv_hut1994), and screen17's stair,
    which leaves the frame 40 above the pit floor — four more 32-deep
    steps of its two cobble columns x (18336..18527], tops 32 to 8 — with
    invisible wall down both its open sides from the shelf's foot (y 22784)
    to the pit floor, where the shot's rails are too low to stop a body
    stepping off the upper steps."""
    items = complete_huts()
    tail = step_stair((18431, 18527), (23103, 23135, 23167, 23199),
                      (32, 24, 16, 8))
    items += tail
    height = {shape: h for h, shape in STEP_X.items()}
    rows = {}
    for it in vignette_items(load_vignette('screen17'), ART_MAP,
                             RAY_SLIDES.get('screen17')) + tail:
        if it.shape in height and it.y > 22783:
            rows[it.y] = max(rows.get(it.y, 0), it.z + height[it.shape])
    ys = sorted(rows)
    items += stair_barriers(18335, 18527, ys, [rows[y] for y in ys])
    return items


def stamp_shots(items):
    """Stamp every shot (vignette_place.stamp clears what the generators
    put in its window), holding the quest's own items out of the clearing:
    a pinned item a shot was placed to stand on its ground — the Passage
    Stone on screen02's shore, Atli at screen19's door, Hrodny's chest and
    potions in screen20's hut — goes through as it is, its contained
    records (MapItem.contained_item: they must follow their container)
    with it. stamp() refuses a pin in a window outright, because a pin
    move is a decision; these are the decisions: none of these move but
    the chest, pad 210 and Atli's one unit off the jamb, recorded in the
    vignettes' pin_moves."""
    pins = {(p['shape'], p['x'], p['y'], p['z']) for p in load_pins()}
    pins |= {(SHAPE_CHEST_LOCKED, 21216, 8768, 0),
             (SHAPE_ZEALAN_ELDER, 19231, 6943, 0)}
    held, rest, carry = [], [], False
    for it in items:
        if it.x < 64 and carry:                 # a contained record
            held.append(it)
            continue
        carry = (it.shape, it.x, it.y, it.z) in pins
        (held if carry else rest).append(it)
    for shot in VIGNETTES:
        rest = stamp_vignette(rest, shot, 10, art_map=ART_MAP, fill=None,
                              slides=RAY_SLIDES.get(shot))
    return rest + held


def temple_near_wall(items):
    """Keep the stair-foot cliff collision while exposing the landing.

    These two face planes close the screenshot's stair tail beyond the
    screen17 window. Their full-height drawn courses hide m10b-17; the
    coincident invisible wall shapes have the same 128 by 32 footpads.
    """
    for it in items:
        if (it.x, it.y) == (18559, 23423) and it.z in (8, 56) and \
                it.shape in (26, 32):
            it.shape = {26: 497, 32: 498}[it.shape]
            it.frame = 0
    return items


# Each landmark is an explicit composition at world coordinates.
# Reservations keep subsequent prefab and cluster placement out of its scene.
DRESSING_SCENES = {'fallen court portico': [[12927, 3103, 0, 875, 0],
                          [13055, 3103, 0, 875, 0],
                          [13567, 3103, 0, 875, 0],
                          [13823, 3103, 0, 875, 0],
                          [13055, 3359, 0, 905, 0],
                          [13183, 3423, 0, 905, 0],
                          [13567, 3295, 0, 905, 0],
                          [13759, 3327, 0, 905, 0],
                          [13855, 3583, 0, 914, 0],
                          [13983, 3583, 0, 914, 2],
                          [12991, 3199, 0, 899, 3],
                          [13631, 3167, 0, 910, 6],
                          [13887, 3167, 0, 910, 7],
                          [13631, 3647, 0, 910, 2],
                          [14047, 3519, 0, 899, 4]],
 'well yard fence repair': [[7135, 8735, 0, 148, 2],
                            [7167, 8863, 0, 146, 0],
                            [7359, 8895, 0, 150, 0],
                            [7295, 9055, 0, 910, 7],
                            [7103, 9151, 0, 667, 0],
                            [7423, 9247, 0, 910, 3],
                            [7487, 9087, 0, 909, 0],
                            [7551, 9119, 0, 909, 0]],
 'collapsed dry-bed crossing': [[10847, 6751, 0, 148, 2],
                                [11359, 6975, 0, 148, 2],
                                [10975, 6783, 0, 150, 0],
                                [11263, 7167, 0, 150, 0],
                                [10783, 7135, 0, 667, 1],
                                [10943, 7423, 0, 667, 0],
                                [11455, 7135, 0, 910, 8],
                                [10815, 7263, 0, 910, 6]],
 'smith charcoal yard': [[18623, 10399, 0, 911, 0],
                         [18527, 10335, 0, 911, 5],
                         [18559, 10463, 0, 911, 3],
                         [18495, 10591, 0, 440, 0],
                         [18591, 10719, 0, 540, 0],
                         [18687, 10591, 0, 320, 0],
                         [18879, 10463, 0, 667, 0],
                         [18943, 10527, 0, 667, 1],
                         [19007, 10655, 0, 667, 0],
                         [18975, 10847, 0, 667, 1],
                         [18495, 10207, 0, 910, 7],
                         [18431, 10303, 0, 910, 6],
                         [18367, 10431, 0, 910, 7],
                         [18431, 10527, 0, 910, 8],
                         [18655, 10527, 0, 910, 6],
                         [18719, 10399, 0, 910, 7],
                         [18655, 10239, 0, 910, 8]],
 'hermit drying yard': [[13375, 12319, 0, 148, 2],
                        [13631, 12319, 0, 148, 2],
                        [13535, 12319, 0, 150, 0],
                        [13343, 12479, 0, 909, 0],
                        [13407, 12543, 0, 909, 0],
                        [13535, 12543, 0, 909, 0],
                        [13439, 12607, 0, 909, 0],
                        [13503, 12639, 0, 909, 0]],
 'last stand at the dead tree': [[7871, 17119, 0, 75, 0],
                                 [7327, 17247, 0, 900, 0],
                                 [7711, 17535, 0, 900, 0],
                                 [7391, 17375, 0, 667, 0],
                                 [7519, 17407, 0, 667, 1],
                                 [7455, 17503, 0, 899, 4],
                                 [7615, 17023, 0, 156, 0],
                                 [7775, 17215, 0, 156, 2],
                                 [7871, 17375, 0, 156, 0],
                                 [7231, 17663, 0, 156, 2],
                                 # Retail flat sword, axe, and dagger frames.
                                 [7359, 17087, 0, 243, 1],
                                 [7359, 17663, 0, 244, 1],
                                 [7807, 17567, 0, 245, 1]],
 'broken votive crescent': [[20031, 17599, 0, 909, 0],
                            [20127, 17663, 0, 909, 0],
                            [20255, 17695, 0, 910, 6],
                            [20351, 17663, 0, 909, 0],
                            [20447, 17567, 0, 909, 0],
                            [20383, 17791, 0, 910, 8],
                            [20191, 17823, 0, 465, 3],
                            [20095, 17759, 0, 465, 7]],
 'abandoned canyon scaffold': [[5983, 23007, 0, 148, 2],
                               [6015, 23135, 0, 146, 0],
                               [6207, 23135, 0, 148, 2],
                               [6175, 23007, 0, 150, 0],
                               [6447, 23583, 0, 667, 1],
                               [6303, 23327, 0, 910, 8],
                               [5919, 23359, 0, 900, 0],
                               [6239, 23455, 0, 910, 6]],
 'fallen west colonnade': [[11615, 21887, 0, 293, 2],
                           [11743, 21599, 0, 905, 0],
                           [11935, 21663, 0, 905, 0],
                           [11839, 21791, 0, 910, 6],
                           [11999, 21919, 0, 899, 4],
                           [11615, 22015, 0, 910, 7],
                           [11455, 21855, 0, 910, 3],
                           [11647, 21535, 0, 47, 0],
                           [11775, 21535, 0, 47, 0],
                           [12031, 21535, 0, 47, 0],
                           [11903, 21535, 0, 494, 0],
                           [11391, 21727, 0, 46, 0],
                           [11391, 21855, 0, 46, 0],
                           [11391, 21983, 0, 46, 0],
                           [11519, 21503, 0, 898, 4],
                           [11647, 21503, 0, 898, 5],
                           [11775, 21503, 0, 898, 0],
                           [11391, 21631, 0, 898, 0],
                           [11519, 21631, 0, 898, 1],
                           [11647, 21631, 0, 898, 2],
                           [11775, 21631, 0, 898, 3],
                           [11903, 21631, 0, 898, 4],
                           [11519, 21759, 0, 898, 4],
                           [11647, 21759, 0, 898, 5],
                           [11775, 21759, 0, 898, 0],
                           [11903, 21759, 0, 898, 1],
                           [11647, 21887, 0, 898, 2],
                           [11775, 21887, 0, 898, 3],
                           [11903, 21887, 0, 898, 4],
                           [11775, 22015, 0, 898, 0],
                           [11903, 22015, 0, 898, 1],
                           [11519, 21887, 0, 898, 5],
                           [11647, 22015, 0, 898, 2]],
 'processional memorial': [[16671, 22495, 0, 38, 0],
                           [16863, 22591, 0, 38, 1],
                           [16767, 22687, 0, 909, 0],
                           [16703, 22783, 0, 905, 0],
                           [16927, 22751, 0, 910, 6],
                           [16831, 22879, 0, 910, 8],
                           [16607, 22719, 0, 465, 3],
                           [17023, 22655, 0, 910, 2]],
 'failed pilgrim bivouac': [[13023, 27743, 0, 900, 0],
                            [13023, 27871, 0, 901, 1],
                            [13023, 27615, 0, 909, 0],
                            [13087, 27711, 0, 909, 0],
                            [13055, 27967, 0, 910, 7],
                            [13023, 27551, 0, 465, 3],
                            [13119, 27903, 0, 465, 5],
                            [13119, 27615, 0, 156, 0],
                            [13119, 27839, 0, 156, 1],
                            [13023, 27999, 0, 156, 2],
                            [12927, 27519, 0, 6, 0],
                            [13055, 27519, 0, 6, 7],
                            [12927, 27647, 0, 6, 3],
                            [13055, 27647, 0, 6, 13],
                            [13183, 27647, 0, 6, 1],
                            [13055, 27775, 0, 6, 10],
                            [13183, 27775, 0, 6, 17],
                            [12927, 27775, 0, 6, 5],
                            [12927, 27903, 0, 6, 10]],
 'drowned watch cairn': [[11871, 18367, 12, 193, 0],
                         [12063, 18463, 0, 193, 0],
                         [11775, 18591, 0, 72, 1],
                         [12223, 18687, 0, 72, 0],
                         [12095, 18719, 0, 72, 1],
                         [11903, 18815, 0, 72, 0],
                         [12287, 18399, 0, 72, 1]],
 'long hall paving apron': [[5791, 6751, 0, 898, 1],
                            [5919, 6751, 0, 898, 3],
                            [6047, 6751, 0, 898, 0],
                            [5663, 6879, 0, 898, 2],
                            [5791, 6879, 0, 898, 4],
                            [5919, 6879, 0, 898, 1],
                            [6047, 6879, 0, 898, 2],
                            [6175, 6879, 0, 898, 0],
                            [5791, 7007, 0, 898, 3],
                            [5919, 7007, 0, 898, 0],
                            [6047, 7007, 0, 898, 4]],
 'abandoned excavation': [[17023, 25023, 0, 465, 0],
                          [17119, 25087, 0, 465, 2],
                          [17183, 25183, 0, 465, 7],
                          [17151, 25311, 0, 465, 11],
                          [17055, 25375, 0, 465, 4],
                          [16959, 25407, 0, 465, 6],
                          [16927, 25279, 0, 465, 3],
                          [16895, 25215, 0, 465, 13],
                          [17119, 24991, 0, 148, 2],
                          [17279, 25119, 0, 148, 2],
                          [17247, 24991, 0, 150, 0],
                          [17119, 25215, 0, 905, 0],
                          [16959, 24959, 0, 534, 0]]}


# Hand-shaped coast lobes, indexed along existing shore cells.
HEADLANDS = (
 ('E', 7, (1,2,2,3,3,2,1,1,1)),
 ('E', 22, (1,1,2,3,4,4,3,2,2,1,1,2,1)),
 ('E', 43, (1,2,3,3,2,2,1,1,2,2,1)),
 ('E', 59, (1,2,2,3,4,3,3,2,1,1)),
 ('E', 78, (1,2,3,3,3,2,1,2,1)),
 ('E', 96, (1,1,2,2,3,4,4,3,2,1,1,1)),
 ('E', 118, (1,2,2,3,3,2,2,1,1,2,1)),
 ('E', 135, (1,1,2,3,4,3,2,2,1)),
 ('E', 151, (1,2,3,3,2,1,1,2,3,2,1)),
 ('E', 174, (1,1,2,3,3,4,3,2,1,1)),
 ('E', 191, (1,2,2,3,2,1,1,2,1)),
 ('E', 206, (1,2,3,4,4,3,2,1,1)),
 ('E', 219, (1,2,2,3,3,2,1,1,2,1)),
 ('E', 231, (1,1,2,3,2,1,1)),
 ('S', 29, (1,2,3,3,2,2,1,1)),
 ('S', 42, (1,1,2,2,3,4,3,2,1,1)),
 ('S', 59, (1,2,3,4,4,3,3,2,1,1)),
 ('S', 78, (1,2,2,3,3,2,1,2,1)),
 ('S', 96, (1,1,2,3,4,3,2,2,1,1)),
 ('S', 116, (1,2,2,3,4,4,3,2,1,1,2,1)),
 ('S', 133, (1,2,3,3,2,1,1,2,2,1)),
 ('S', 150, (1,1,2,3,4,3,3,2,1)),
 ('S', 166, (1,2,3,3,2,2,1,1,1,2,1)),
)

def cliff_shore_pieces(site, field):
    from lv_vale_terrain import CREST_ROLE, pick, visible_role
    from u8_map import MapItem
    depths={(side,start+k):depth for side,start,row in HEADLANDS for k,depth in enumerate(row)}
    land=set()
    for (cx,cy), side in field.flush_side_list:
        if field.H[cx,cy] > 8:continue
        dx,dy=(0,1) if side=='S' else (1,0)
        depth=depths.get((side,cx if side=='S' else cy),1)
        for k in range(1,depth+1):
            n=cx+k*dx,cy+k*dy
            if n in field.water and n not in field.bank_guard:land.add(n)
    # One eroded western headland interrupts the tarn's rectangular bank.
    lake_depths=(2,3,4,5,6,6,7,7,6,6,5,4,3,3,4,5,6,5,4,3,2,2,3,2)
    for cy,depth in enumerate(lake_depths,136):
        for cx in range(88,90+depth):
            if (cx,cy) in field.water and (cx,cy) not in field.bank_guard:
                land.add((cx,cy))
    # Reservations cut genuine coves out of the contour before edge selection.
    land={c for c in land if not site.reason(MapItem.placed_item(
        c[0]*128+223,c[1]*128+223,24,301,0))}
    dry=set(field.H)-field.water-field.vwater
    pieces=[]
    solid_land=land|dry
    for cx,cy in sorted(land):
        drops={side for side,(dx,dy) in {'N':(0,-1),'E':(1,0),'S':(0,1),'W':(-1,0)}.items()
               if (cx+dx,cy+dy) not in solid_land}
        shape,z=(125,16) if drops else (301,24)
        frame=pick(CREST_ROLE[visible_role(drops)],cx,cy,salt=4010) if drops else pick((0,1,2,3,4,5),cx,cy,salt=4013)
        p=MapItem.placed_item(cx*128+223,cy*128+223,z,shape,frame)
        if not site.reason(p):pieces.append(p)
    return pieces


def dress_shore(site, field):
    hot = {(i.x//128, i.y//128) for i in site.expanded if i.shape == 409}
    basalt = []
    for cx, cy in sorted({(x+dx, y+dy) for x, y in hot
                           for dx, dy in ((1,0),(0,1),(-1,0),(0,-1))} - hot):
        floor = site.ground.get((cx, cy))
        if not floor or floor[0] not in (301,4,386) or floor[2] != 0:
            continue
        side = next((d for d in ((1,0),(0,1),(-1,0),(0,-1))
                     if (cx+d[0], cy+d[1]) in hot), None)
        frame = {(1,0):1, (0,1):3, (-1,0):7, (0,-1):9}[side]
        p = MapItem.placed_item(cx*128+127, cy*128+127, 0, 911, frame)
        if not site.reason(p):
            basalt.append((cx, cy, frame))
    if basalt:
        site.basalt_shore('cold lava margin', basalt)

    # Individual offshore remnants have unequal native silhouettes.
    offshore = {
        'east pass remnants': [(23231,4223,12,193,0),(23423,4351,0,193,0),
                                (23615,4479,0,72,1),(23519,4127,0,72,0)],
        'Gunnar sea rocks': [(23263,7007,0,72,0),(23423,7103,0,72,1),
                            (23359,7295,16,125,20)],
        'east strand teeth': [(23359,11359,12,193,0),(23519,11551,0,72,1),
                              (23199,11679,0,72,0)],
        'reedless cove rocks': [(23231,14143,0,72,1),(23423,14271,16,125,19),
                                (23583,14047,0,72,0)],
        'circle coast remnants': [(23231,16927,12,193,0),(23423,17023,0,193,0),
                                   (23583,17215,0,72,1)],
        'south-east breakers': [(23167,19903,0,72,1),(23391,20031,0,72,0),
                                 (23295,20191,16,125,22)],
        'temple sea teeth': [(21247,22271,0,193,0),(21407,22431,0,72,1),
                              (21343,22623,16,125,15)],
        'south processional rocks': [(18559,25247,0,72,0),(18719,25439,0,72,1),
                                      (18399,25535,16,125,20)],
        'cache strand rocks': [(17983,25311,0,72,1),(18175,25407,0,72,0),
                                (18079,25631,16,125,21)],
        'passage canyon teeth': [(14047,25983,12,193,0),(14239,26111,0,193,0),
                                  (14367,26271,0,72,1)],
        'lower passage rocks': [(13919,27583,0,72,0),(14111,27679,0,72,1),
                                 (14015,27871,16,125,19)],
        'cloud canyon remnants': [(7935,25247,0,193,0),(8127,25407,0,72,1),
                                   (7839,25535,0,72,0)],
    }
    for name, rows in offshore.items():
        site.set_piece(name, [MapItem.placed_item(*r) for r in rows])
    pieces = cliff_shore_pieces(site, field)
    # Textured water is sparse and confined to cells touching the new shore.
    for p in list(pieces):
        if p.shape != 125 or (p.x//128*17 + p.y//128*29) % 13:
            continue
        for dx,dy,frame in ((1,0,6),(0,1,4)):
            cx,cy=p.x//128+dx,p.y//128+dy
            if (cx,cy) not in field.water or (cx,cy) in field.bank_guard:
                continue
            it=MapItem.placed_item(cx*128+127,cy*128+127,1,347,frame)
            if not site.reason(it):
                pieces.append(it)
                break
    # Detached, irregular remnants of the western lake escarpment.
    for row in ((12511, 19871, 16, 125, 19),
 (12831, 20127, 16, 125, 22),
 (13215, 19935, 16, 125, 15),
 (13023, 19615, 16, 125, 20),
 (12895, 16351, 16, 125, 21),
 (13247, 16511, 16, 125, 15),
 (13503, 16159, 16, 125, 18),
 (13791, 16447, 16, 125, 19),
 (14975, 16735, 16, 125, 15),
 (14783, 17183, 16, 125, 22),
 (15135, 17823, 16, 125, 17),
 (12927, 15999, 16, 125, 18),
 (13983, 16191, 16, 125, 21),
 (13375, 20159, 16, 125, 19),
 (12671, 19423, 16, 125, 17),
 (12767, 19039, 16, 125, 20)):
        pieces.append(MapItem.placed_item(*row))
    # Two small fungus niches sit on the headland's flat 24-high plates.
    for row in ((11455,18111,24,907,3),(11583,18111,24,907,9),
                (11487,18207,24,907,14),(11583,19519,24,907,5),
                (11679,19583,24,907,11),(11551,19647,24,907,19)):
        pieces.append(MapItem.placed_item(*row))
    site.set_piece('seaward cliff shore', pieces)

def crossing_floor(items):
    """Replace two retained ground cells with the collapsed wooden decks."""
    from glob_catalog import GlobReader
    reader = GlobReader()
    decks = {(11263, 6911): 0, (11135, 7039): 1}
    chunks = {(x // 512, y // 512) for x, y in decks}
    replaced, result = set(), []
    for item in items:
        pieces = (reader.glob_to_items(item.quality, item.x, item.y, item.z)
                  if item.is_glob_egg and (item.x // 512, item.y // 512) in chunks
                  else [item])
        for piece in pieces:
            if ((piece.x, piece.y) in decks and piece.z == 0
                    and piece.shape in (4, 6, 71, 301, 386)):
                replaced.add((piece.x, piece.y))
            else:
                result.append(piece)
    if replaced != set(decks):
        raise ValueError('collapsed crossing requires both retained ground cells')
    result.extend(MapItem.placed_item(x, y, 0, 163, frame)
                  for (x, y), frame in decks.items())
    return result


def dress_vale(items, shapes, field):
    from lv_dressing import Site, KIT_HALL, KIT_DECORATIVE, KIT_DEADWOOD, prefab_family
    from dressing_metrics import REGIONS
    site = Site(10, crossing_floor(items), shapes, seed=4010)
    site.reserve('collapsed dry-bed crossing', (11007, 6783, 11263, 7039))
    # Breached steps leave the central track open beneath the fallen drums.
    site.walkable_set_piece('fallen court portico', [
        MapItem.placed_item(12927, 3487, 0, 299, 0),
        MapItem.placed_item(13055, 3487, 0, 299, 1),
        MapItem.placed_item(13567, 3487, 0, 299, 2),
        MapItem.placed_item(13695, 3487, 0, 299, 0),
        MapItem.placed_item(13823, 3487, 0, 299, 3),
    ])
    for name, records in DRESSING_SCENES.items():
        site.set_piece(name, [MapItem.placed_item(*r) for r in records])
        print(f'  Map 10 landmark: {name} ({len(records)} records)', flush=True)
    for i in list(site.expanded):
        if i.shape != 66:
            continue
        pieces = [MapItem.placed_item(i.x + 160, i.y + 96, i.z, 908, (i.frame + 5) % 12),
                  MapItem.placed_item(i.x + 128, i.y + 192, i.z, 465, (i.frame + 3) % 17)]
        if all(not site.reason(p) for p in pieces):
            site.set_piece(f'outcrop {i.x},{i.y}', pieces)
    interior = (3072, 1024, 22528, 30208)
    # Retail rock dressing contains excluded 301 bank frames. Safe copies
    # belong in the shared prefab inventory; loose rubble supplies this pass.
    earth = prefab_family('earth_brush_') + prefab_family('earth_debris_')
    site.swap_chunks(plain=875, family=earth, share=.55, where=interior)
    site.swap_chunks(plain=875, family=(437,435,434,438), share=1, where=interior)
    for name, kind, where in REGIONS[10]:
        kit = tuple(row for row in KIT_HALL if row[0] in (899,910))
        if kind in ('village','ruin'):
            kit += tuple(row for row in KIT_DEADWOOD if row[0] == 465)
        if kind == 'shore':
            kit = tuple(row for row in KIT_DECORATIVE if row[0] in (907,910))
        added = site.clusters(kit=kit, per100=10 if kind=='village' else 8,
                      where=where, floors={4, 301, 386, 71, 6, 125},
                      anchor='water' if kind=='shore' else 'seam')
        print(f'  Map 10 clusters: {name} ({len(added)} records)', flush=True)
    site.clusters(kit=tuple(row for row in KIT_HALL if row[0] in (899,910)),
                  per100=2.5, where=interior,
                  floors={4, 301, 386}, anchor='seam')
    dress_shore(site, field)
    return unpack_ground_runs(site.pack(), site)


def unpack_ground_runs(packed, site):
    import json
    import lv_globs
    from dressing_metrics import item_class
    eggs={(i.x//512,i.y//512):i for i in packed if i.is_glob_egg}
    loose=set()
    # Keep Thordis and Tyorvi visible at their literal schedule destinations.
    obscuring={(434,0,5280,9312,0),(910,2,21824,8032,0)}
    item_key=lambda p:(p.shape,p.frame,p.x,p.y,p.z)
    for (cx,cy),egg in eggs.items():
        if egg.quality < 3072:
            continue
        pieces=site.globs.glob_to_items(egg.quality,egg.x,egg.y,egg.z)
        # Authored wall runs remain explicit records for the lattice audit.
        if any(p.shape in (15,47) for p in pieces):
            loose.add(egg.quality)
            continue
        if any(item_class(site.sorter.info(p.shape),p.shape,p.frame) not in ('ground','void')
               for p in pieces):
            continue
        for dx,dy in ((1,0),(0,1)):
            if all((e:=eggs.get((cx+k*dx,cy+k*dy))) is not None
                   and e.quality==egg.quality for k in range(3)):
                loose.add(egg.quality)
    result,expanded,removed=[],[],set()
    for i in packed:
        if i.is_glob_egg and i.quality in loose:
            pieces=site.globs.glob_to_items(i.quality,i.x,i.y,i.z)
            result.extend(pieces)
            expanded.extend(p.to_bytes().hex() for p in pieces)
            removed.add(i.to_bytes().hex())
        else:
            result.append(i)
    dropped=[i for i in result if item_key(i) in obscuring]
    if {item_key(i) for i in dropped} != obscuring or len(dropped) != 2:
        raise ValueError('Map 10 schedule clearance props changed')
    dropped_records={i.to_bytes().hex() for i in dropped}
    result=[i for i in result if i.to_bytes().hex() not in dropped_records]
    if len(result)>20000:
        raise ValueError('Map 10 final raw record ceiling exceeded')
    doc=lv_globs.registry()
    provenance=doc['dressing']['10']
    provenance['eggs']=[key for key in provenance['eggs'] if key not in removed]
    provenance['records']=[key for key in provenance['records'] if key not in dropped_records]
    provenance['records'].extend(expanded)
    provenance['ledger'].append(dict(operation='unpack_ground_runs',
                                     eggs=len(removed),records=len(expanded)))
    provenance['ledger'].append(dict(operation='schedule_visibility_clearance',
                                     removed_props=len(dropped)))
    lv_globs.MANIFEST.write_text(json.dumps(doc,indent=2)+'\n')
    return result


def varied_ground_chunks(items):
    from glob_catalog import GlobReader
    from lv_vale_terrain import pick
    reader=GlobReader()
    out=[]
    for i in items:
        sacred=18432<=i.x<22528 and 15360<=i.y<18432
        passage=12288<=i.x<13312 and 24576<=i.y<30208
        if i.is_glob_egg and i.quality in (397,2241,875) and (sacred or passage):
            for p in reader.glob_to_items(i.quality,i.x,i.y,i.z):
                if p.shape in (301,4):
                    frames=(0,1,2,3,4,5) if p.shape==301 else (14,15,30,31,32,33)
                    p.frame=pick(frames,p.x//128,p.y//128,salt=4019)
                out.append(p)
        else:
            out.append(i)
    return out


def build_map_10():
    """Build complete Map 10 item list."""
    field = build_field()
    zones = []
    zones.extend(build_tracks())
    zones.extend(build_entry_area())
    zones.extend(build_hoskuld_village())
    zones.extend(build_gunnar_village())
    zones.extend(build_ezrekal_dwelling())
    zones.extend(build_test_area())
    zones.extend(build_test_grounds())
    zones.extend(build_the_lake())
    zones.extend(build_sacred_circle())
    zones.extend(build_cloud_approach())
    zones.extend(build_temple_approach())
    zones.extend(build_moriens_ruins())
    zones.extend(build_ragnar_cache_ruins())
    zones.extend(build_wilderness())
    # Exposed household stand-ins leave; covered furnishings retain their homes.
    roofs = [i for i in zones if i.shape in (412, 34, 36, 647)]
    zones = [i for i in zones if i.shape not in (92, 94) and
             (i.shape not in (205, 208, 307) or any(
                 r.x - 128 < i.x <= r.x and r.y - 128 < i.y <= r.y
                 for r in roofs))]
    # Low rubble replaces scattered gray stumps before retained shots restore their props.
    for i in zones:
        if i.shape == 152:
            i.shape, i.frame = 910, 6 + i.frame % 3
    items = varied_ground_chunks(build_ground(field)) + lift_props(zones, field)
    # The 1994 screenshots, verbatim (2026-10-16: the build must show each
    # published shot as it was; docs/research/2026-10-16-screenshot-
    # reconstruction.md). Last before the checks, so a vignette replaces
    # whatever the generators put inside its window; then the cells each
    # shot never shows a floor in get the field's own ground, and the huts
    # the shots show two sides of get the other two.
    items = stamp_shots(items)
    items += shot_closure(field)
    items += shot_completions()
    shots = vignette_inputs()
    items += stair_underfill(items, shots)
    items += under_floors(field, shots, items)
    # VQ-007: screen02's offset slab and crevice tile have incomplete
    # paint over their z=8 land footprints. Continue the island beneath
    # them at that height; the shot's shore and water footprints stay put.
    for x, y in ((13695, 18303), (14079, 18047)):
        items.append(MapItem.placed_item(
            x, y, 8, SHAPE_ROCK_SLAB_GROUND, 0))
    items += shot_supports(field, shots, items)
    items += shot_rails(field, shots) + lake_rails(field, shots=True)
    # the steps of a course between flat floors nothing draws (a shot's
    # rim over the field beyond its frame): a crest plate under the higher,
    # never inside a shot's frame
    items += band_plates(items, shots)
    # Full-lattice probes found unsupported paint at these floor cells.
    # The floors continue the cell material beneath the existing art.
    for z, cells in (
            (64, ((70, 167), (70, 168))),
            (0, ((72, 165), (73, 165), (72, 167), (73, 167))),
            (0, ((74, 167), (75, 166), (75, 167), (151, 58), (151, 59)))):
        items.extend(field.floor_item(c, z) for c in cells)
    # Inset diamond sprites leave one-pixel gaps at these cell borders.
    # Offset under-floors close the paint without raising the surface.
    for cx, cy, dx, dy in ((74, 167, 0, -8), (151, 58, -4, 0),
                           (75, 166, -4, 0), (72, 165, 0, -8),
                           (72, 165, 0, -64)):
        floor = field.floor_item((cx, cy), 0)
        floor.x += dx
        floor.y += dy
        items.append(floor)
    # Own-material floors cover the Hrodny edge probes. The closure
    # columns below preserve the original reached set at their borders.
    for x, y, frame in ((20095, 8511, 30), (20287, 8767, 33),
                        (20223, 8575, 30), (20351, 8703, 33),
                        (20479, 8703, 31), (20479, 8831, 30),
                        (20219, 8575, 30)):
        items.append(MapItem.placed_item(x, y, 0, 4, frame))
    items.append(MapItem.placed_item(20607, 8831, 0, 386, 4))
    # The under-floors paint beneath reliefs without opening their bottoms.
    # These strips close exactly the 20 newly supported lattice positions;
    # the pre-repair arrival flood loses no positions.
    for shape, x, y in ((497, 19424, 7616), (498, 19264, 7520),
                        (497, 20288, 8639), (846, 20447, 8767)):
        for z in (0, 48):
            items.append(MapItem.placed_item(x, y, z, shape, 0))
    items = temple_near_wall(items)
    _check_tracks(items, field)
    # The void floor (2026-09-16): black plates under every void cell within
    # view of a floor — the engine never clears the frame without
    # `usehighres` (.claude/rules/map-geometry.md, last section). Last, so
    # it sees every floor, the rim included; it overlaps floors harmlessly.
    from parse_typeflag import load_typeflag
    shapes = load_typeflag(os.path.join(os.path.dirname(__file__), "../../../shared/build/TYPEFLAG.DAT"))
    items = dress_vale(items, shapes, field)
    items.extend(void_floor(items))
    return items


if __name__ == '__main__':
    items = build_map_10()
    globs = sum(1 for i in items if i.is_glob_egg)
    teles = sum(1 for i in items if i.is_teleport_egg)
    mons = sum(1 for i in items if i.is_monster_egg)
    npcs = sum(1 for i in items if i.npcnum > 0 and not i.is_teleport_egg)
    print(f"Map 10: {len(items)} items")
    print(f"  Glob eggs: {globs}")
    print(f"  Teleport eggs: {teles}")
    print(f"  Monster eggs: {mons}")
    print(f"  NPC items: {npcs}")
    print(f"  Other items: {len(items) - globs - teles - mons}")

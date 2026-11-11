#!/usr/bin/env python3
"""
lv_shapes.py — Single source of truth for every U8SHAPES.FLX shape ID used by
               the Lost Vale map builders (build_map_09/10/11/13/17/18.py).

Why this file exists
---------------------
Each build_map_XX.py historically declared its own local `SHAPE_*` constants,
guessed from context rather than verified against the actual rendered art.
The SAME local name ended up meaning DIFFERENT shape ids in different files
(e.g. `SHAPE_ROOF_B` = 37 in build_map_09.py but = 9 in build_map_11/17/18.py;
`SHAPE_ROCK_B` = 301 in build_map_11.py but = 300 in build_map_13.py), and
several ids were flat-out mislabeled (e.g. shape 189/190 were called
"bones" but are actually 322/350-frame full humanoid NPC sprites; shape 158
was called "book" in build_map_17/18.py but is a wooden stool; shapes
65/92/94 were called "rock" but render as a mushroom cluster and grass
patches respectively).

This module replaces all of those per-file guesses with UNAMBIGUOUS
canonical names — one constant per (shape id, visual meaning) — verified by
actually rendering the shapes with shape_render.py and looking at the
output. Every constant below is commented with what it renders as, and
either "verified 2026-07-01" (rendered and visually confirmed during the
2026-07-01 shape audit / this module's creation) or "UNVERIFIED — named
from usage" (not independently re-rendered; name is inherited from how the
build_map_*.py files used it and may still be wrong).

THIS FILE SUPERSEDES the per-file `SHAPE_*` blocks at the top of each
build_map_XX.py. A later phase adopts this module in those builders; until
then, treat any discrepancy between a build_map_XX.py local constant and the
canonical value here as a bug in the build_map_XX.py file, not in this
module.

Relationship to TYPE_SHAPES (agents/usecode-compiler/src/u8c_symbols.py)
--------------------------------------------------------------------------
`TYPE_SHAPES` in u8c_symbols.py is a SEPARATE, LEGACY mapping used by the
usecode compiler to resolve `TypeXXX` identifiers referenced in .UNK source
files to shape ids. It is not kept in sync with this module and should not
be treated as a shape-identity reference — only the subset of TYPE_SHAPES
entries actually referenced by compiled .UNK sources matters there. Do not
use TYPE_SHAPES to look up "what does shape N look like"; use this module
(and shape_render.py, if a constant here is marked UNVERIFIED) instead.

Collisions inherited from the build_map_*.py files (documented, not fixed
here — fixing them is the later adoption phase's job):
  - SHAPE_ROOF_B: 37 in build_map_09.py vs. 9 in build_map_11/17/18.py.
    Canonical names: SHAPE_CAVE_CEILING_B (37) and SHAPE_ROCKY_RUBBLE_CEILING (9).
  - SHAPE_ROCK_B: 301 in build_map_11.py vs. 300 in build_map_13/17/18.py.
    Canonical names: SHAPE_ROCK_SLAB_GROUND (301) and SHAPE_BOULDER_PILE (300).
  - SHAPE_BOOK: 613 in build_map_09.py (a real book) vs. 158 in
    build_map_17/18.py (actually SHAPE_STOOL — a misnomer).
  - SHAPE_BONES / SHAPE_BONES_B: 235/237 in build_map_09/11/13/17/18.py
    (real skeletal remains, correct) vs. 189/190 in build_map_10.py (full
    humanoid NPC sprites — a misnomer; see SHAPE_NPC_ROBED_HUMANOID_A/B).
  - SHAPE_ROCK_A/B/C: 65/92/94 in build_map_09/10.py are actually a
    mushroom cluster and grass patches, not rock — see
    SHAPE_MUSHROOM_CLUSTER / SHAPE_GRASS_PATCH_A/B.
  - SHAPE_NPC: 400 in build_map_17/18.py is a fire/explosion VFX, not an
    NPC — see LEGACY_PLACEHOLDERS / SHAPE_PLACEHOLDER_FIRE_VFX.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shape_viewer import read_flx_entry, parse_shape_frames, SHAPES_FLX


# ---------------------------------------------------------------------------
# Effective U8SHAPES.FLX location
# ---------------------------------------------------------------------------
# Custom injected shapes (856-858, the wood-plank hut wall set) exist ONLY in
# shared/build/U8SHAPES.FLX, a patched copy produced by lv_wood_wall.py. Any
# code that needs to resolve a shape id to pixels/frame-count must prefer
# that file when present, and fall back to the base game's read-only copy
# under shared/data/u8-install/STATIC/ otherwise.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
BUILD_SHAPES_FLX = os.path.join(_BASE_DIR, "shared", "build", "U8SHAPES.FLX")


def _effective_shapes_flx_path():
    """Return the patched shared/build copy if it exists, else the base copy."""
    if os.path.exists(BUILD_SHAPES_FLX):
        return BUILD_SHAPES_FLX
    return SHAPES_FLX


# ===========================================================================
# TERRAIN / GROUND
# ===========================================================================

SHAPE_GROUND_FLAT = 3           # flat ground tile (UNVERIFIED — named from usage)
SHAPE_GROUND_RAISED = 4         # ground tile with elevation step (UNVERIFIED — named from usage)
SHAPE_GROUND_VARIANT_B = 128    # ground tile variant (UNVERIFIED — named from usage)
SHAPE_GROUND_VARIANT_C = 242    # ground tile variant (UNVERIFIED — named from usage)
SHAPE_GROUND_VARIANT_D = 409    # ground tile variant, build_map_10.py only (UNVERIFIED — named from usage)

SHAPE_ROCK_SLAB_GROUND = 301    # broken/cracked rock-slab ground tile (verified 2026-07-01
                                 # render); reused across files as both "rock rubble" and
                                 # "terrain height detail" — same shape, same meaning.

SHAPE_MUSHROOM_CLUSTER = 65     # gray/brown mushroom & fungus cluster on a cave floor
                                 # (verified 2026-07-01 render). build_map_09/10.py called
                                 # this SHAPE_ROCK_A — a misnomer, it is not rock.
SHAPE_GRASS_PATCH_A = 92        # green grass/foliage ground-decoration tile (verified
                                 # 2026-07-01 render). build_map_09/10.py called this
                                 # SHAPE_ROCK_B — a misnomer.
SHAPE_GRASS_PATCH_B = 94        # green grass/foliage ground-decoration tile variant
                                 # (verified 2026-07-01 render). build_map_09/10.py called
                                 # this SHAPE_ROCK_C — a misnomer.

SHAPE_VEGETATION_VARIANT = 127  # plant variant (UNVERIFIED — named from usage)

SHAPE_LAVA_POOL = 318           # large lava/molten-rock hazard area, 8x8 footpad (verified
                                 # 2026-07-01 render — glowing orange/red lava with a dark
                                 # rock rim)

SHAPE_WATER_SURFACE_SMALL = 347     # dark-blue rippling water surface, 4x4 footpad
                                     # (verified 2026-07-01 render)
SHAPE_WATER_SURFACE_LARGE = 669     # large water surface, 8x8 footpad (UNVERIFIED — named
                                     # from usage; same visual family as 347/710)
SHAPE_WATER_SURFACE_LARGE_B = 710   # large water surface variant, 8x8 footpad (UNVERIFIED
                                     # — named from usage)
SHAPE_WATER_SURFACE_SMALL_B = 738   # water surface variant, 4x4 footpad (UNVERIFIED — named
                                     # from usage)

SHAPE_TRAP_BURST_A = 435        # floor trap burst effect: dark rubble tile with a white/
                                 # blue-tinged spark burst (verified 2026-07-01 render —
                                 # note the color reads more frost/lightning than fire,
                                 # despite the inherited "FLAME" name used in
                                 # build_map_11/17.py; treat the element as UNVERIFIED)
SHAPE_TRAP_BURST_B = 436        # trap burst variant (UNVERIFIED — named from usage, same
                                 # family as 435)
SHAPE_TRAP_BURST_C = 437        # trap burst variant (UNVERIFIED — named from usage, same
                                 # family as 435)

SHAPE_DAMAGE_FLOOR = 198        # cracked/damaged dark stone floor tile, frame 0; carries
                                 # SI_DAMAGING (verified 2026-07-01 per task audit)


# ===========================================================================
# WALLS / CLIFFS
# ===========================================================================

SHAPE_CAVE_WALL_E = 26          # east-facing craggy cave/cliff wall, 4x1 footpad (verified
                                 # 2026-07-01 render)
SHAPE_CAVE_WALL_S = 32          # south-facing craggy cave/cliff wall, 1x4 footpad
                                 # (UNVERIFIED — named from usage; presumed rotated twin of 26)
SHAPE_CAVE_WALL_SHORT_E = 27    # shorter east-facing cave/cliff wall (UNVERIFIED — named
                                 # from usage)
SHAPE_CAVE_WALL_SHORT_S = 31    # shorter south-facing cave/cliff wall (UNVERIFIED — named
                                 # from usage)
SHAPE_CAVE_WALL_CORNER = 29     # cave/cliff wall corner piece, 1x1 footpad (UNVERIFIED —
                                 # named from usage)
SHAPE_CLIFF_FACE_DETAIL = 125   # rock face with extra carved/eroded detail (UNVERIFIED —
                                 # named from usage)

SHAPE_WOOD_BUILDING_WALL_A = 145   # wood-plank building wall with a lit window (verified
                                    # 2026-07-01 render)
SHAPE_WOOD_BUILDING_WALL_EW = 149  # ADDED 2026-07-30: the EAST-WEST partner of
                                    # SHAPE_WOOD_BUILDING_WALL_A. footpad (4,1,5)
                                    # = 128x32x40 against A's (1,4,5) = 32x128x40,
                                    # same 8 frames and same height — a matched
                                    # pair exactly like 489/492. Its absence is
                                    # why build_map_10.py built east-west hut and
                                    # ruin walls out of A, a NORTH-SOUTH shape:
                                    # 32 units of wall per 256-unit step. Use
                                    # wall_run_x with this, wall_run_y with A.
SHAPE_WOOD_BUILDING_WALL_B = 148   # wood-plank building wall variant (UNVERIFIED — named
                                    # from usage, same family as 145)
SHAPE_WOOD_BUILDING_WALL_C = 155   # wood-plank building wall variant, single frame
                                    # (UNVERIFIED — named from usage)

SHAPE_STONE_DUNGEON_WALL = 489     # MISNAMED (found 2026-09-14): not a wall run
                                    # piece. Its 12 frames are wall ORNAMENTS — a
                                    # lion-head gargoyle block, a carved capital, a
                                    # stacked-capstone corner, a little tower, a
                                    # barred window, a barred arch — and the base
                                    # game sets them on TOP of walls, 177 times in
                                    # all 42 maps. A run built from it reads as a
                                    # row of wall tops stacked on each other, which
                                    # is exactly what Map 18 looked like until the
                                    # walls were rebuilt from 10/15 below. Maps
                                    # 09/10/11/13/17 still build from it.
                                    # footpad (1,4,5) = 32x128x40 — LONG IN Y.
SHAPE_STONE_WALL_NS = 10           # THE stone wall, north-south run piece: the
                                    # base game's most-placed wall (5,550 uses),
                                    # footpad (1,4,5) = 32x128x40, 12 frames.
                                    # Frames verified 2026-09-14: 1 and 4 plain,
                                    # 0/2/3 with grass at the foot (outdoor), 5 a
                                    # carved face relief without grass, 6-11 the
                                    # dark set (plain, face, lamps, runes). Pair of
                                    # SHAPE_GLOB_WALL_PIECE (15) below, which is
                                    # the same wall long in x: there 1 is plain,
                                    # 0 the face relief, 2/3 grass, 4-9 dark.
SHAPE_STONE_WALL_EW = 492          # MISNAMED like 489 (2026-09-14): the same set of
                                    # ornaments long in x, 119 uses in the base game.
                                    # For an east-west WALL use SHAPE_GLOB_WALL_PIECE
                                    # (15). What follows is the 2026-07-27 note that
                                    # brought it in, kept for the stride finding.
                                    # ADDED 2026-07-27: the complementary orientation of
                                    # 489 and the piece every LV map was missing.
                                    # footpad (4,1,5) = 128x32x40 — LONG IN X, for
                                    # EAST-WEST runs (wall_run_x). Same 12 frames and
                                    # same 40-unit height as 489, i.e. the matching half
                                    # of one wall set. Its absence is why Map 18's
                                    # east-west "walls" were 87% hole: they were built
                                    # from 489, which is 32 wide in x, placed every 256.
                                    # The base game places 489 and 492 at a 128 stride
                                    # along their long axis (measured across all 42
                                    # retail maps: 28/34 and 36/44 spacings are exactly
                                    # 128; the wider ones are doorways).
SHAPE_STONE_DUNGEON_WALL_B = 490   # stone dungeon wall variant, 2 frames (UNVERIFIED —
                                    # named from usage, same family as 489). Also long
                                    # in Y (32x96); its X-partner is 493 (96x32).
SHAPE_STONE_WALL_EW_SHORT = 493    # ADDED 2026-07-27: three-quarter-length east-west
                                    # wall, footpad (3,1,4) = 96x32x32. Same set as
                                    # 492; used to finish a run off the 128 grid, which
                                    # is how the Tiny Tar crack in build_map_18.py lands
                                    # on an exact 32-unit aperture. 32 units tall, above
                                    # map_walkability's STEP_Z of 24, so it blocks
                                    # rather than being stepped over.

SHAPE_ROCK_SPIRE_CLUSTER = 66      # tall jagged gray rock spire cluster / stone rubble
                                    # (verified 2026-07-01 render)
SHAPE_BOULDER_PILE = 300           # rounded gray boulder pile (verified 2026-07-01 render)
SHAPE_OAK_TREE = 199               # large oak, one frame, 288x288x80 FIX|SOL|DRAW — no
                                    # LAND, so nothing stands on its canopy. Retail places
                                    # 24 of these across maps 3/4/6/41 (Tenebrae's own map
                                    # 41 has one, at z=88), so it is a known-good outdoor
                                    # asset, not a guess. 80 tall exceeds the engine's
                                    # climb72-on-jump reach from a z=48 lane in a single
                                    # course (see shape-ids.md's climb rule) — no stacking
                                    # needed, unlike the 40-tall rock-spire cluster above.

# --- The outdoor vocabulary (grid-rendered 2026-09-15 from the Plateau, Map
# --- 8, and the Tenebrae outskirts, Maps 4/5, for the Map 10 landscape pass;
# --- placed by lv_landscape.py / build_map_10.py). Footpads from TYPEFLAG.
SHAPE_CLIFF_TOP = 125              # rock-face top tile, 4x4x1 LND: the crest a cliff
                                    # course wears (Map 8 puts it one course above
                                    # every 26/32 run); frames 0-6 plain grey
SHAPE_CLIFF_CORNER = 29            # 1x1x6 rock post that fills the convex corner
                                    # where a 26 run meets a 32 run
SHAPE_BLOCKER_X = 497             # 4x1x6 FIX|SOL|EDITOR: retail's invisible wall,
                                    # a 26-sized box that is never drawn
                                    # (GameMapGump skips SI_EDITOR) and still
                                    # blocks (no collision path tests it);
                                    # 409 on the retail maps, 23 on Map 8
SHAPE_BLOCKER_Y = 498             # 1x4x6, the same along y (a 32-sized box);
                                    # 398 retail, 33 on Map 8
# A flat tile laid OVER a glob floor is drawn by the sorter's flat rules
# (sort_item.cpp:145-181): an SI_DRAW flat "always gets drawn first" — under
# the floor, invisible — and an SI_OCCL flat likewise; the glob floors (242,
# 3) are SI_OCCL, so an overlay must carry NEITHER flag. 301 and 386 carry
# SI_DRAW and vanished in-engine (2026-09-15); these four do not:
SHAPE_GRAVEL = 6                   # 4x4x0 LND dark grey gravel: a dry riverbed
SHAPE_TRACK_COBBLE = 425           # 4x4x0 LND dark cobbles with brown earth: the
                                    # worn track (frames 2,4,6,9,11,13,15,17,19)
SHAPE_SLAB_PALE = 71               # 4x4x0 LND pale smooth stone, frames 0-2 plain
                                    # (3-7 edged, 8-15 dark cobble): paving over a floor
SHAPE_COBBLE_GREY = 783            # 4x4x0 LND rounded grey stone paving, 16 frames
SHAPE_TRACK_DIRT = 386             # 4x4x0 LND grey rock with brown earth — SI_DRAW,
                                    # so ONLY as a floor in its own right, never over one
SHAPE_ROCK_SLAB_CRACKED = 299      # 4x4x1 LND cracked grey slab (8 frames), ruins;
                                    # 8 tall, so it draws over a floor (not a flat)
SHAPE_STANDING_STONE = 38          # 2x2x5 SOL; frames 2-3 are the plain grey
                                    # monoliths (0-1 are gargoyle busts)
SHAPE_RUBBLE_PILE = 524            # 3x3x1 LND rock rubble; frames 2-3 grey, 4-5 red
SHAPE_RUBBLE_SMALL = 526           # 2x2x2 LND small rocks; 0-2 dark, 6-8 grey
SHAPE_STONE_SMALL = 553            # 1x1x1 SOL single stone; 0-8 grey, 18-26 blue-grey
SHAPE_TREE_DEAD = 75               # 7x7x7 SOL bare tree, 224 wide: frames 0 brown,
                                    # 1 white, 3 grey; 4 is in leaf
SHAPE_TREE_TRUNK = 56              # 2x2x5 SOL|LND trunk; frames 6-7 grey dead,
                                    # 8-9 brown thin, 0-1 brown stout
SHAPE_TREE_STUMP_GREY = 152        # 2x2x5 SOL grey twisted stump, frames 0-4
SHAPE_BUSH = 434                   # 2x2x3, FIX only (walk-through): frames 0-3
                                    # green, 4-5 dead brown — crops and scrub
SHAPE_COLUMN_RUIN_TALL = 394       # 2x2x10 SOL tall grey stone column, 1 frame
SHAPE_PILLAR_STONE = 293           # 1x1x5 SOL pale pillar; 0-1,3-6 whole, 2 a
                                    # broken stub, 7-9 damaged, 10 rubble
SHAPE_STONE_BROKEN = 494           # 2x1x3 LND broken block, 2 frames
SHAPE_FENCE_X = 62                 # 4x1x5 SOL wooden fence panel long in x; 0-3
                                    # sound, 6-11 broken, 14-15 iron gate
SHAPE_FENCE_Y = 130                # 1x4x5 SOL the same panel long in y; 1-3 sound,
                                    # 0/6-11 broken
SHAPE_FENCE_POST = 61              # 1x1x5 SOL wooden post, frames 0-9


# ===========================================================================
# ROOFS / CEILINGS
# ===========================================================================

SHAPE_CAVE_CEILING_A = 34       # reddish-brown stone ceiling/roof tile block (verified
                                 # 2026-07-01 render)
SHAPE_CAVE_CEILING_B = 37       # gray stone ceiling/roof tile block, some frames raised/
                                 # textured (verified 2026-07-01 render). build_map_09.py
                                 # calls this SHAPE_ROOF_B — NOTE this collides in name
                                 # (but not id) with SHAPE_ROCKY_RUBBLE_CEILING (9), which
                                 # build_map_11/17/18.py also call SHAPE_ROOF_B.
SHAPE_CAVE_CEILING_WOOD = 162   # wood-plank floor texture reused overhead as a cave
                                 # ceiling variant (verified 2026-07-01 render) — material
                                 # mismatch (wood, not stone) versus its neighbors 34/37;
                                 # kept as-is since it's the placement, not the id, that's
                                 # in question.
SHAPE_ROCKY_RUBBLE_CEILING = 9  # rocky rubble mound tile used as a roof/ceiling overhang
                                 # (verified 2026-07-01 render). This is the shape
                                 # build_map_11/17/18.py call SHAPE_ROOF_B — a DIFFERENT id
                                 # from build_map_09.py's SHAPE_ROOF_B (37, see
                                 # SHAPE_CAVE_CEILING_B above).

SHAPE_BUILDING_ROOF = 220          # dark tiled building roof, blue-black tiles with an
                                    # orange ridge-trim seam (verified 2026-07-01 render)
SHAPE_BUILDING_ROOF_VARIANT = 335  # building roof variant (UNVERIFIED — named from usage,
                                    # same family as 220)


# ===========================================================================
# DOORS / GATES
# ===========================================================================

SHAPE_LV_DOORS = 342    # THE Lost Vale Double Doors — tall black S-facing door leaf
                         # (fp 4,1,10 = double height), SF_QUALITY lock, real usecode
                         # door class (344). This is the exact art in Origin's 1994 LV
                         # press screenshots (Ultima Codex); the SHIPPED game never
                         # places it anywhere (verified: 0 hits in base FIXED.DAT and
                         # all 1,513 globs, 2026-07-02). Frames 0/1 = mirrored leaves
                         # (ring right / ring left); frames 2-6 = open states (1x1).
                         # 340 is the E-facing twin (fp 1,4,10, class 342).
SHAPE_LV_DOORS_E = 340   # east-facing twin of the Lost Vale doors
SHAPE_DOOR_S = 69       # wooden door, south-facing, brass ring handle, multiple wood-tone
                         # frames (verified 2026-07-01 render)
SHAPE_DOOR_E = 68       # wooden door, east-facing, brass ring handle, multiple wood-tone
                         # frames (verified 2026-07-01 render)
SHAPE_LARGE_GATE = 114  # large ornate dark-red double-door/gate, ring handle (verified
                         # 2026-07-01 render)


# ===========================================================================
# PROPS / FURNITURE
# ===========================================================================

SHAPE_CAVE_BACKDROP_SMALL = 894  # Retail 334 paint with decorative physics.
SHAPE_CAVE_BACKDROP_LARGE = 895  # Retail 564 paint with decorative physics.
SHAPE_DECORATIVE_WATER = 896  # Navy lake paint over existing dry support.
SHAPE_SANCTUM_BACKDROP = 897  # Retail 566 paint with decorative physics.
SHAPE_COURT_COBBLE_FLAT = 898  # Retail 70 on the flat 71 row.
SHAPE_RUBBLE_DECORATIVE = 899  # Retail 524, fixed with no standing top.
SHAPE_BONES_DECORATIVE_A = 900  # Retail 235, fixed with no standing top.
SHAPE_BONES_DECORATIVE_B = 901  # Retail 237, fixed with no standing top.
SHAPE_CAVE_CREST_DECORATIVE = 902  # Retail 125 with clipped paint variants.
SHAPE_MOAT_BANK_DECORATIVE = 903  # Retail 94 with no standing top.
SHAPE_MOAT_FACE_DECORATIVE = 904  # Retail 85 with decorative physics.

SHAPE_FALLEN_WHITE_DRUM = 905
SHAPE_ROOTS_DECORATIVE = 906
SHAPE_FUNGUS_DECORATIVE = 907
SHAPE_SPIRES_DECORATIVE = 908
SHAPE_URN_DECORATIVE = 909
SHAPE_RUBBLE_526_DECORATIVE = 910
SHAPE_BASALT_DECORATIVE = 911
SHAPE_RELIEF_X_DECORATIVE = 912
SHAPE_RELIEF_Y_DECORATIVE = 913
SHAPE_AIR_FACE_DECORATIVE = 914
SHAPE_WALL_ROCK_SKIN = 915
SHAPE_STARS_SHIFTED = 916
SHAPE_STARS_SHIFTED_LAST = 928


SHAPE_TORCH = 295           # wall torch/sconce (UNVERIFIED — named from usage)
SHAPE_STALACTITE = 186      # hanging cave rock feature (UNVERIFIED — named from usage)

SHAPE_DESK = 205             # wooden roll-top desk, 3 wood-tone frames (verified
                              # 2026-07-01 render). build_map_10.py used this as
                              # SHAPE_CHEST — a misnomer (it's furniture, not a container).
SHAPE_TABLE_WORKBENCH = 208  # wooden desk-shaped table/workbench, 4 frames incl. a broken
                              # variant (verified 2026-07-01 render). build_map_10.py used
                              # this as SHAPE_BARREL — a misnomer.
SHAPE_CHEST_PLAIN = 306      # plain carved wood cabinet, single frame (renders chest-like;
                              # engine-name likely a cabinet variant of 307 — see below)
SHAPE_CHEST_ORNATE = 307     # MISNOMER — engine name (shape_names.py) is "wardrobe"!
                              # Ornate carved WARDROBE with metal fittings, single frame.
                              # The 2026-07-01 visual audit misread it as a treasure chest;
                              # confirmed in-game 2026-07-02 (single-click prints
                              # "Wardrobe"). Fine for hut furniture; for actual treasure
                              # chests use SHAPE_CHEST / SHAPE_CHEST_LOCKED below.
SHAPE_WARDROBE = SHAPE_CHEST_ORNATE  # honest alias — prefer this name in new code
SHAPE_CHEST = 78             # REAL treasure chest — engine name "chest" (SF_CONTAINER,
                              # SI_BAG, 5 frames: 0=closed .. 4=fully open, gilt fittings;
                              # verified 2026-07-02 render + name table). 117 is the
                              # E-facing twin ("chest", fp 2,3,2).
SHAPE_CHEST_E = 117          # east-facing real chest variant, engine name "chest"
SHAPE_CHEST_LOCKED = 618     # engine name "locked chest" — gilded lockbox, 1 frame,
                              # SF_CONTAINER, class LCHST_EW 0x26A. 673 is the E-facing
                              # twin. The chest's own quality is NOT its lock: KEYRING
                              # (0x4F) looks for a SHAPE_TRAP inside it (see below).
SHAPE_TRAP = 756             # engine name "trap", class TRAP 0x2F4, lives inside a chest.
                              # quality 0x100|keyid = the chest's lock (KEYRING 004F:0445
                              # opens the chest for a key whose quality == keyid; with no
                              # such trap ANY key opens it). quality < 0x100 = a booby
                              # trap: CHEST/LCHST use() calls TRAP use(), which explodes
                              # (FIRESPEL) when quality/256 == 0. Every retail locked chest
                              # carries one (docs/playtest-2026-10-08-intrinsics.md).
SHAPE_TABLE_DINING = 225     # long wooden dining table, 2 frames (plain + damaged)
                              # (verified 2026-07-01 render)
SHAPE_STOOL = 158            # wooden stool/bench, 2 frames (verified 2026-07-01 render).
                              # build_map_17/18.py called this SHAPE_BOOK — a clear
                              # misnomer; see SHAPE_BOOK_CLOSED (613) for the real book.
SHAPE_WELL = 664             # stone well-head with bucket and winch roof, 3 frames
                              # (verified 2026-07-01 render)
SHAPE_CAULDRON = 176         # metal pot/cauldron/kettle, 12 frames (verified 2026-07-01
                              # render)
SHAPE_BOTTLE_GREEN = 180     # green glass bottle (UNVERIFIED — named from usage)
SHAPE_FLASK_ALCHEMICAL = 809  # alchemical flask/potion container (UNVERIFIED — named from
                               # usage; per task note this is "a real flask", distinct from
                               # the unrelated base-game door placeholder shape 340)
SHAPE_KEY = 82               # REAL key — engine name "key blank" (SF_QUALITY, fp 1,1,0,
                              # 4 flat-lying gold-key frames; verified 2026-07-02 render +
                              # name table). History of wrong picks, all caught by the
                              # engine name table (shape_names.py):
                              #   641 = "skull" (skull-in-cage scenery, from TYPE_SHAPES)
                              #   505 = "switch" (looked key-ish in renders; prints
                              #         "Switch" in-game)
                              # Related: 79 = "keyring", 232 = "Key of the Caretaker".


# ===========================================================================
# QUEST ITEMS
# ===========================================================================

SHAPE_BOOK_CLOSED = 613     # closed brown leather book/tome; 24 cover-variant frames
                             # (frame 6 = brown cover); carries SF_QUALITY so its quality
                             # value triggers a usecode read-on-pickup (verified 2026-07-01
                             # per task note + render)
SHAPE_BACKPACK = 529        # real leather backpack, usable as a container (verified per
                             # task note)
SHAPE_PASSAGE_STONE = 798   # REAL small stone — engine name "rock" (SF_GENERIC, SI_SOLID
                             # only, fp 1,1,1, wt 1, 6 frames of small gray rocks; verified
                             # 2026-07-04 render + name table + TYPEFLAG). The Passage Test
                             # stone, quest steps 7-8: MUST match TYPE_SHAPES' TypeBushKey
                             # in u8c_symbols.py (RAGNAR.UNK spawns it into the quest bag;
                             # PLNTST.UNK's egg consumes it from the Avatar's inventory).
                             # Place at FRAME 0 ONLY — the PLNTST foreach filters
                             # (type = TypeBushKey) and (frame = 0). Replaced shape 580,
                             # whose SI_FIXED flag made the island stone unpickable (same
                             # trap the elemental talismans hit — see SHAPE_TALISMAN_GEM).
                             # NOT 796 (also named "rock"): that one is a 64x64x56 boulder
                             # with wt 0 — scenery, not a pocketable stone.
SHAPE_QUEST_BAG = 637       # REAL bag — engine name "bag" (SF_CONTAINER, SI_BAG, fp 1,1,1,
                             # wt 1, 1 frame: brown drawstring pouch; verified 2026-07-04
                             # render + name table + TYPEFLAG). Matches TYPE_SHAPES'
                             # TypeBag: usecode-spawned only (RAGNAR.UNK's stone bag at
                             # (16447,25727,64), HRODNY.UNK's key bag at (19588,23284,64)),
                             # never map-placed — documented here for the same
                             # keep-in-sync reason as SHAPE_TALISMAN_GEM. TYPEFLAG volume
                             # is 0, which ScummVM's Container::getCapacity() treats as
                             # capacity 32 — the stone (vol 2) and key fit fine. Replaced
                             # 225, the dining TABLE (see SHAPE_TABLE_DINING): Ragnar's
                             # "small bag hidden in the ruins" spawned as furniture.
SHAPE_LONGSWORD = 420       # steel longsword, weapon-equip shape; frame 0 = lying flat on
                             # the ground (verified per task note)
SHAPE_AXE = 419             # "axe" (engine name), weapon-equip shape, 1x3x1, SI_SOLID,
                             # weight 5, not SI_FIXED; frame 0 on the ground, as all
                             # thirteen of retail's world-placed axes and maces are
                             # (U8SAVE.000 NONFIXED). u8weapons.ini [axe]: base 6,
                             # mod 14, damage_type 0x06 = DMG_BLADE|DMG_BLUNT, so its
                             # blunt half survives a golem's 0x8A defense (Actor::
                             # calculateAttackDamage strips only the blade bit).
SHAPE_SPECIAL_ROOT = 869    # CUSTOM ART (not base game), since 2026-10-11: the "special
                             # root" for Tyorvi's nightmare elixir (quest steps 9-12),
                             # docs/art-track.md contract 12. One frame, FRAME 0: a pale
                             # gnarled root with violet leaves, injected by lv_art_props.py
                             # on donor 180's TYPEFLAG row (carryable, SF_GENERIC, opaque).
                             # MUST match TYPE_SHAPES' TypeWeedz in u8c_symbols.py:
                             # Ezrekal's two foreaches filter (type = TypeWeedz) and
                             # (frame = 0) within the Avatar (lv-patched/EZREKAL.UNK R2).
                             # Class 869 (lv-new/SPROOT.UNK) barks "special root". It was
                             # 399 frame 9, "eye of newt", a vine that read as a snake.
                             # Placed by build_sacred_circle "by the standing stones"
                             # (EZREKAL.UNK:3108's hint).


# ===========================================================================
# DECORATION
# ===========================================================================

SHAPE_BONES_A = 235   # real skeletal remains on the ground, 2 frames; ambient bone
                       # decoration (verified 2026-07-01 render)
SHAPE_BONES_B = 237   # real skeletal remains on the ground, variant, 2 frames (verified
                       # per task note)
SHAPE_BOULDER_LARGE = 796   # large boulder — engine name "rock" (SI_SOLID|SI_LAND,
                             # fp 2,2,7 = 64x64x56 world units, wt 0 so NOT carryable,
                             # 4 frames; verified 2026-07-04 TYPEFLAG + name table).
                             # SI_LAND top: the avatar can stand on it, so it doubles
                             # as a climbable plinth (used for Ragnar's cache dais on
                             # Map 10 — top at z+56 puts RAGNAR.UNK's hardcoded bag
                             # drop z=64 within one step of the crown). Do NOT confuse
                             # with 798 (SHAPE_PASSAGE_STONE), the small carryable
                             # "rock".


# ===========================================================================
# NPC / ACTOR SPRITES
# ===========================================================================

SHAPE_NPC_GUARD_ARMORED = 574       # armored guard NPC sprite (blue/gray armor, polearm);
                                     # frame 146 = prone corpse pose, usable as a lootable
                                     # decorative body when placed with the container family
                                     # flag (verified 2026-07-01 render + task note)
SHAPE_NPC_PEASANT_MALE = 707        # male peasant/villager NPC sprite, brown robe (verified
                                     # 2026-07-01 render)
SHAPE_NPC_CHILD = 708               # child NPC sprite (UNVERIFIED — named from usage, same
                                     # family as 707)
SHAPE_NPC_SORCERER = 200            # sorcerer/mage NPC sprite (UNVERIFIED — named from
                                     # usage)
SHAPE_NPC_SEATED_CHARRED = 835      # dark seated/charred-looking humanoid figure in a
                                     # wooden chair, 51 frames (verified 2026-07-01 render)
                                     # — DO NOT use for living/standing NPCs, it is posed
                                     # sitting.
SHAPE_NPC_PEASANT_SMALL = 836       # small/child-sized peasant NPC sprite variant
                                     # (UNVERIFIED — named from usage, same family as 835)

SHAPE_NPC_ROBED_HUMANOID_A = 189    # full robed humanoid NPC sprite (red hair, white robe),
                                     # 322 animation frames — NOT bones (verified 2026-07-01
                                     # render). build_map_10.py called this SHAPE_BONES — a
                                     # clear misnomer; see SHAPE_BONES_A/B (235/237) for the
                                     # real skeleton decoration shapes.
SHAPE_NPC_ROBED_HUMANOID_B = 190    # full humanoid NPC sprite variant, 350 animation frames
                                     # — NOT bones (verified per task note, same misuse as
                                     # 189). build_map_10.py called this SHAPE_BONES_B.


# ===========================================================================
# CORPSES / STATUES / ALTARS  (2026-07-19 art-placeholder audit)
# ===========================================================================
# Added by the 2026-07-19 audit (agents/map-populator/docs/art-placeholder-
# audit-2026-07-19.md) to retire three placements of the shape-400 "fire
# field" and one of the shape-721 "chimney". Identity for all three is
# established by the ENGINE's own name table (shape_names.engine_name, the
# authoritative source per shape_names.py) PLUS a render, PLUS TYPEFLAG.

SHAPE_SKELETON_SPRAWLED = 332   # engine name "skeleton"; 3 frames of a skeleton sprawled
                                 # flat on the ground (verified 2026-07-19 render).
                                 # TYPEFLAG [SI_SOLID, SI_LAND] SF_CONTAINER fp (2,3,1)
                                 # — same family and same flat z=1 footpad as the
                                 # already-blessed SHAPE_BONES_A/B (235/237, commit
                                 # 5c78f60). Use for a whole body lying where it fell;
                                 # 235/237 are scattered-remains piles.
                                 # REPLACED shape 400 ("fire field") in build_map_17.py's
                                 # Memorial Hall, where two corpses rendered as fire AND
                                 # carried SI_DAMAGING right beside the Shield halves.

SHAPE_STATUE_STONE = 443        # engine name "statue"; 4 visually distinct carved-stone
                                 # creature statues (verified 2026-07-19 render).
                                 # TYPEFLAG [SI_FIXED, SI_SOLID] SF_GENERIC fp (3,3,3).
                                 # A neutral, non-lying stand-in for a monumental figure.
                                 # Preferred over 275 (also "statue", but fp (6,6,6) — too
                                 # large for the Map 18 sanctum spacing) and over 700
                                 # ("statue of Mordea" — that name is a U8 Pagan lore
                                 # collision the Zealan sanctum must not print).
                                 # NOT a real fix for the three gods — see the audit doc;
                                 # it only stops them announcing themselves as "fire field".

SHAPE_GOD_CRYSTAL = 860         # CUSTOM ART (not base game). The three Zealan gods,
                                 # six frames: 0/1/2 encased in amber, 3/4/5 the same
                                 # three freed, in god order Felicitar, Doloras, Timyra.
                                 # Injected by lv_god_statues.py as step 4 of
                                 # tools/build_artifacts.sh — an injection made outside
                                 # that step is dropped on the next artifact rebuild
                                 # (.claude/rules/shape-ids.md).
                                 # TYPEFLAG copied from 443 (SI_FIXED|SI_SOLID) with the
                                 # footpad overridden to (6,6,8); the donor's (3,3,3) box
                                 # is far too small for art this size.
                                 # Frames differ in size: Doloras is the widest thing in
                                 # the sanctum at 92x81 encased. ONE TYPEFLAG entry governs
                                 # all six frames, so when setFrame(n+3) eventually frees
                                 # them, Felicitar's 24x110 figure still carries the same
                                 # 192-unit blocker as Doloras's 92x81 block. Clearance
                                 # must be budgeted for the encased widths, always.
                                 # Provenance: shared/docs/art-poc/gods/*/README.md

SHAPE_SACRED_ROCK = 863         # CUSTOM ART (not base game). The stone at the centre
                                 # of Map 10's Sacred Circle, one frame. Art track item
                                 # 3, docs/art-track.md contract 3, and the one item on
                                 # that track with NO 1994 original: "Sacred Smallish
                                 # Unusual-Colored Rock" was a joke placeholder in Plot
                                 # v1.1/v1.2 that became "Sacred Circle" before the
                                 # usecode snapshot. The look was decided instead
                                 # (Douglas, 2026-09-20): a NINTH STONE, kin to the eight
                                 # shape-38 monoliths already on the ring, so the
                                 # generator's reference is the ring itself. Injected by
                                 # lv_art_props.py (step 5/7). TYPEFLAG is 66's own
                                 # (SI_FIXED|SI_SOLID, SF_GENERIC) with the footpad
                                 # (4,4,8): x/y stay 4 because the box must clear
                                 # map_walkability's MAP10_ROOT_SEED (20480, 16896) by
                                 # the single world unit it has, and z goes 5 -> 8 for
                                 # the 64x96 screen box a 96 px sprite needs. No usecode
                                 # class at 863, and none is lost: EUSECODE entries 68
                                 # and 865 are both empty, so shape 66 printed nothing
                                 # either. No TYPE_SHAPES re-point: TypeSealingBoulder
                                 # resolves to 66 and COLPUZZL.UNK:175 reads it, but
                                 # guarded by getQ() = 299 on Map 11, and the Sacred Rock
                                 # is quality 100 on Map 10.

SHAPE_MESSAGE_SCROLL = 864      # CUSTOM ART (not base game). The Message Scroll
                                 # of Cloud City's Scroll Chamber, one frame. Art
                                 # track item 4, docs/art-track.md contract 4. Like
                                 # the Sacred Rock it has no 1994 original: Plot
                                 # v1.2 beats 13 and 14 give it its errand (found in
                                 # the deserted Cloud World, carried back to Ezrekal)
                                 # and items.yaml one line of content, and no
                                 # recovered usecode names it, so the reference is
                                 # the game's own scroll, shape 159. Injected by
                                 # lv_art_props.py (step 5/7). TYPEFLAG is 159's
                                 # (SI_SOLID, SF_QUALITY, footpad (2,2,1)), which
                                 # buys two things the 158 stool could not give: no
                                 # SI_FIXED, so the Avatar can pick it up and carry
                                 # it to Ezrekal, and SF_QUALITY, the one family
                                 # Item::I_getQuality answers for (item.cpp:2841), so
                                 # QUALITY_MSG_SCROLL 80 is readable the moment a
                                 # class asks. CLASS 864 EXISTS since 2026-09-21:
                                 # lv-new/MSGSCRL.UNK, pinned TYPEMESSAGESCROLL in
                                 # lv_manifest.json, dispatched off the shape number
                                 # (item.cpp:1516). look() barks "message scroll" and
                                 # use() opens the scroll gump with Odion's letter, so
                                 # the shape number and the class number are now one
                                 # decision: renumbering either silently unreads the
                                 # scroll. No TYPE_SHAPES re-point: nothing compiled
                                 # finds this item by type, and a re-point would send
                                 # FREE.UNK's debug grant here.

SHAPE_ELEMENTAL_PILLAR = 865    # CUSTOM ART (not base game). Map 11's four elemental
                                 # pillars, FOUR FRAMES in the map's element order
                                 # (0 Earth, 1 Air, 2 Fire, 3 Water; receptacle
                                 # quality 201-204 in the same order). Art track item
                                 # 5, docs/art-track.md contract 5. No 1994 art (Art
                                 # List v2.5 names them, three crossed out), so the
                                 # look was decided: the column IS its element on a
                                 # stone plinth, which is what the 1994 barks say
                                 # ("column of roaring flame"). Douglas chose Earth
                                 # and Air from the C2 sheet and Fire and Water from
                                 # C3 (2026-09-24). Injected by lv_art_props.py
                                 # (step 5/7): donor 38 (the ring stone: SI_FIXED |
                                 # SI_SOLID, SF_GENERIC), footpad (2,2,10) = a 32x96
                                 # screen box the 24-px column fills, 80 units of
                                 # collision. CLASS 865 EXISTS since 2026-09-24
                                 # (lv-new/ELMCOLMN.UNK, TYPEELEMENTALCOLUMN): look()
                                 # barks the element by frame. MUST stay equal to
                                 # u8c_symbols TYPE_SHAPES['TypeElementalColumn'],
                                 # which COLPUZZL.UNK:139 compiles into the search
                                 # that destroys a pillar; test_art_props asserts
                                 # the pair. Replaced 721, the engine's CHIMNEY.

SHAPE_PILLAR_RECEPTACLE = 866   # CUSTOM ART (not base game). The stone socket beside
                                 # each Map 11 pillar, one frame: a squat knee-high
                                 # pedestal with a hollow for a gem (art track item 5,
                                 # contract 5; approved as generated 2026-09-24).
                                 # Injected by lv_art_props.py: donor 443 (statue:
                                 # SI_FIXED | SI_SOLID, SF_GENERIC), footpad (3,3,3),
                                 # a 48x48 box, 24 units tall. THE SHAPE NUMBER CARRIES
                                 # NO USECODE MEANING: each receptacle is placed with
                                 # npcnum 120, and the engine patch in
                                 # Item::callUsecodeEvent dispatches every event to
                                 # class 1144 TYPERECEPTACLE off that npcnum, whatever
                                 # the shape. A class at 866 would never run. Replaced
                                 # 307, the WARDEW chest, whose SF_CONTAINER family
                                 # was why COLPUZZL reads getQ() and not getQuality().

SHAPE_TEST_PLANT = 871          # CUSTOM ART (not base game), since 2026-10-11:
                                 # the Passage Test plant, docs/art-track.md
                                 # contract 13. A spined yellow-green bulb with a
                                 # red fruit at its heart, one frame, on donor 65's
                                 # TYPEFLAG row (SI_FIXED|SI_SOLID, no SI_LAND),
                                 # footpad (3,3,4). MUST equal TYPE_SHAPES
                                 # ['TypeShortmushroom']: PLNTST.UNK:72 destroys it,
                                 # PLNTST creates five more, and REAPPLY.UNK destroys
                                 # the quality-10 one again on re-entry. Class 871
                                 # (lv-new/TESTPLNT.UNK) barks the 1994 "Strange
                                 # plant". It was shape 126 frame 0, a blue-crystal
                                 # SI_LAND ground tile the Avatar walked over.

SHAPE_ELIXIR = 868              # CUSTOM ART (not base game). Tyorvi's nightmare
                                 # elixir, one frame: the necromancy-reagent vial
                                 # (shape 395 frame 5, "vial of blood") with its red
                                 # liquid recoloured to a sea-green brew (Douglas,
                                 # 2026-10-09; docs/art-track.md contract 11). Built
                                 # by lv_art_props.py from the base vial at build
                                 # time, so no Origin pixel is committed. TYPEFLAG is
                                 # 180's, the engine's bottle (SI_SOLID, SF_GENERIC,
                                 # footpad (1,1,1), weight 1): carryable, and NOT
                                 # SF_REAGENT, so it never merges with blood and the
                                 # reagent code ignores it. NEVER PLACED: EZREKAL.UNK
                                 # creates it at runtime and TYORVI.UNK's two drink
                                 # filters destroy it, both through
                                 # u8c_symbols TYPE_SHAPES['TypeBottle'], which MUST
                                 # equal this (test_art_props asserts the pair).
                                 # CLASS 868 EXISTS (lv-new/ELIXIR.UNK, TYPEELIXIR):
                                 # look() barks "Tyorvi's elixir".

SHAPE_WATER_ZOMBIE = 872        # CUSTOM ART (not base game). The Water Zombie, an
                                 # ACTOR: the ghoul 142's 451 frames recoloured to
                                 # the 1994 zombie of screen02/09 (teal skin, green
                                 # kilt and slime; 2026-10-25, was candidate A's
                                 # blue-grey 2026-10-11), with its three shot poses
                                 # at frames 40, 81 and 112 (lv_actor_art.py).
                                 # Built by lv_monsters.py from the base ghoul at
                                 # build time, so no Origin pixel is committed;
                                 # TYPEFLAG row and ANIM.DAT entry are 142's, and
                                 # install_lv.sh writes its u8monsters.ini row (the
                                 # ghoul's stats). Hatched by the Lake's eggs
                                 # (SHAPE_MON_ZOMBIE below). CLASS 872
                                 # EXISTS (lv-new/WZOMBIE.UNK, TYPEWATERZOMBIE):
                                 # look() barks "water zombie".

SHAPE_HARPIE = 873              # CUSTOM ART (not base game). The Harpie, an ACTOR
                                 # drawn new in the torax 120's 240-frame layout
                                 # (the 86 frames its ANIM.DAT entry uses), from the
                                 # classic-harpy key poses Douglas picked (candidate
                                 # A, 2026-10-11; docs/art-track.md contract 9). Built
                                 # by lv_monsters.py from the committed indexed
                                 # frames; TYPEFLAG row and ANIM.DAT entry are 120's,
                                 # install_lv.sh writes its u8monsters.ini row (the
                                 # torax's stats). Hatched by the harpie zone's eggs
                                 # (SHAPE_MON_HARPIE below). CLASS 873 EXISTS
                                 # (lv-new/HARPIE.UNK, TYPEHARPIE): look() barks
                                 # "harpie".

# THE 1994 ART (2026-10-16, docs/research/2026-10-16-screenshot-reconstruction/
# phaseC-art.md). Pixels cut exactly from the published 1994 screenshots
# (shared/data/lv-1994-art/, registered in vignettes/art_registry.json) and
# injected verbatim by lv_art_props.py's 'indexed' rows. They are NEW ids,
# beside the custom art they replaced (862 -> 874, 870 -> 878); 862 is
# retired and 870 is 878's legacy alias (both below). No usecode class
# exists at any of them but 879's.
# Floor-layer shapes (874, 876, 877) take their registry hotspot with yoff + 1,
# which draws them one pixel higher, so a tile at z=0 lands on the pixels the
# reconstruction drew at z=1. Objects keep the registry hotspot.
SHAPE_CLOUD_1994 = 874          # cloud floor, 5 flat frames (3 and 4 are 0 and 2
                                 # mirrored), 62x32 @ (31,32); TYPEFLAG 163's row,
                                 # which is 301's with SI_DRAW swapped for SI_OCCL:
                                 # it draws over SI_DRAW floors (screen13's earth)
                                 # and under flat props lying on it.
SHAPE_WHITE_COLUMN_1994 = 875   # white column, frame 0 plain (the gem pillar's
                                 # shaft, under retail gem 596), frame 1 orange-
                                 # banded (obelisk drum, walkway post); 16x47 @
                                 # (8,47); donor 443, footpad (1,1,5).
SHAPE_GOLD_BRICK_1994 = 876     # gold brick floor, 2 flat frames @ (31,32);
                                 # TYPEFLAG 163's row like the cloud.
SHAPE_MARBLE_WALKWAY_1994 = 877  # marble walkway slab with its gold-trimmed face
                                 # and back rim in the one frame, 62x52 @ (31,52);
                                 # donor 113, footpad (4,4,1). 19 of its pixels are
                                 # inferred (registry inferred_px).
SHAPE_SHIELD_HALVES_1994 = 878  # the Shield halves as 1994 drew them: frame 0 the
                                 # sun half (left), frame 1 the eye half (right),
                                 # SHADES.UNK's frame order. Both anchored so
                                 # that the two at one position reassemble the
                                 # altar Shield of screen04 (879). Donor 828,
                                 # footpad (1,3,3).
SHAPE_SACRED_SHIELD_1994 = 879  # the reassembled Shield on the sanctum altar
                                 # (screen04): retail 828's disc with the 1994
                                 # emblems, 30x28 @ (6,32), 828's own anchor and row.
SHAPE_GEM_CAP_1994 = 880       # the gem on screen11's gem pillars: retail 596's
                                 # eight frames copied verbatim at build time (no
                                 # pixel committed) onto a FIXED donor, 443, with
                                 # 596's (1,1,1) footpad. 596 itself is
                                 # TypeTalisman, carryable, and its frames 0-3
                                 # are the Map 11 element talismans: a 596 on a
                                 # Map 17 pillar could be picked up and fed to a
                                 # receptacle (2026-10-17, phase C Map 17).
                                 # The vignettes keep 596, the shot's truth;
                                 # build_map_17 stamps them with art_map
                                 # {596: 880}.
SHAPE_STRIPED_PROP_1994 = 881   # the black-and-white striped thing lying on
                                 # Felicitar's plinth in screen04 (registry 2014,
                                 # SINGLE-SHOT, unidentified: bones or a ribcage,
                                 # no retail frame matches, best 146/690). 32x18
                                 # @ (-2,18), donor 443 (fixed), the solved
                                 # 32x32x8 box (1,1,1); 2026-10-17, phase C Map 18.
# Phase D (2026-10-25, docs/research/2026-10-16-screenshot-reconstruction/
# phaseD/static/REPORT.md): the screen12/13 pieces no retail frame matches,
# cut index for index where the shots show them.
SHAPE_NOOK_DAIS_1994 = 882       # screen12's throne-nook dais: 877's marble run
                                 # along y, two steps lighter (registry 2006,
                                 # 3 single-use frames), donor 113 (4,4,1)
SHAPE_WALKWAY_END_1994 = 883     # 877 cut on the screen vertical through its
                                 # front corner: the strips' east end (2007)
SHAPE_GOLD_EDGE_1994 = 884       # gold brick meeting the cloud (2008): f0/f1
                                 # cloud lobes over gold, f2 the gold corner
                                 # screen12 and screen13 both show; donor 163
SHAPE_SIDE_THRONE_1994 = 885     # screen12's left throne, side on (2009),
                                 # donor 223, (1,2,5)
SHAPE_CLOUD_RIM_1994 = 886       # screen13's floor tiles, each with its own
                                 # lobed rim (2015, single-use frames), donor 163

# PHASE E, screen07 (2026-10-30, docs/research/2026-10-16-screenshot-
# reconstruction/phaseE/pillars11/REPORT.md): the Pillar of Fire chamber's
# rock and floor as the shot draws them. PATCH rows (lv_art_props): each
# frame is the retail piece's own frame with the pixels the shot shows it
# owning replaced by the shot's, composed at build time so no Origin pixel
# is committed; one single-use frame per piece of the window.
SHAPE_CAVE_FACE_1994 = 891       # screen07's 26-family cave walls with the
                                 # 1994 spears, seams and the back wall's tip
                                 # (registry 2043), donor 26 (4,1,6)
SHAPE_CAVE_FLOOR_1994 = 892      # screen07's floor tiles round the pillar:
                                 # the lava pit's lip and glow (registry 2027),
                                 # donor 301 (4,4,0)

# THE 1994 ACTORS (2026-10-25, docs/research/2026-10-16-screenshot-
# reconstruction/phaseD/actors/REPORT.md). Actor clones built by
# lv_monsters.py (step 6) from lv_actor_art.py's derivations: the donor's
# TYPEFLAG row and ANIM.DAT table, the donor's frame layout, the 1994 shot
# pose verbatim at the frame the shot shows. NPC bodies: no u8monsters.ini
# row, no class (a placed LV NPC dispatches by npcnum, objId + 1024).
SHAPE_ZEALAN_ELDER = 888        # the white-haired elder of screen19/20, Atli
                                 # (npc 107): Mythran 190's 350 frames restyled,
                                 # 190's row and table; the shot poses at 60 (stand
                                 # SE) and 70-72 (SE talk).
SHAPE_SPEAR_CHILD_DARK = 889    # screen20's dark-haired spear child, npc 104:
                                 # the child 708's 100 frames at 0.8 scale with
                                 # tunic, cloak and spear; 708's row and table;
                                 # the shot pose at frame 1 (shown mirrored, W).
SHAPE_SPEAR_CHILD_BLOND = 890   # screen20's blond spear child, npc 111: as 889
                                 # with blond hair.

# RETIRED custom-art ids (2026-10-17). The 1994 screenshot art replaced them:
# 861 the Magnetic Obelisk (art track contract 1, 2026-09-15) by screen11's
# composite of retail pieces on 875 drums; 862 the cloud floor tile
# (contract 2, 2026-09-15) by 874. No build step injects them, no map places
# them, no class lives at them, and their U8SHAPES.FLX and TYPEFLAG.DAT slots
# stay the base game's (empty, filler row). NEVER reuse them: a save, a
# playtest record or a doc that names one must not find something else there
# (.claude/rules/shape-ids.md). test_art_props asserts all of it. Both were
# SI_FIXED map scenery, so a save holds them only as FIXED items of the map
# the player stood on when saving (ObjectManager saves the current map's
# objects; CurrentMap::writeback hands them back to the fixed list, which
# unloadFixed deletes on leaving): Map 17 saves made 2026-09-15..10-17 carry
# them until the player leaves Map 17, invisible and harmless.
RETIRED_SHAPE_IDS = (861, 862)

# LEGACY ALIAS (2026-10-17). 870 was the Shield halves cut from retail 828
# (contract 10, 2026-10-11) until 878, the 1994 halves, replaced it. It was
# retired with 861/862 at first, but the halves are CARRYABLE: a save made
# 2026-10-11..10-17 can hold them as 870 in the Avatar's pack, and an empty
# slot there aborts ScummVM the moment the pack opens
# (ContainerGump::run's `Assertion sh`, verify3 claim 2). So 870 is built as
# a verbatim copy of 878 -- frames and TYPEFLAG row -- by a 'copy' row in
# lv_art_props.py: old halves look and behave as the 1994 halves. It is
# never placed and no TYPE_SHAPES entry resolves to it; SHADES and REAPPLY
# name 870 by literal for those saves (test_art_props section 14).
SHAPE_SHIELD_HALVES_LEGACY = 870

SHAPE_SHADOW_PLATE = 564        # 8x8x0 LAND|SOLID|DRAW "shadow plate": frame 0 dark grey,
                                 # frames 2-6 PURE palette-black (index 0 only, 130x65 px —
                                 # a 256-unit diamond). Map 8 flanks its paving with frames
                                 # 2/5/6. lv_furnish.void_floor lays frame 2 under every
                                 # void cell within view of a floor: the engine never clears
                                 # the frame without `usehighres`, so unpainted void shows
                                 # the previous frame (docs/playtest-2026-09-15-cloud-tiles.md
                                 # finding 1). SI_DRAW sorts it UNDER every real floor at the
                                 # same z (.claude/rules/map-geometry.md), so the plates may
                                 # overlap floors freely and only show where nothing else is.

# ---------------------------------------------------------------------------
# TEMPLE / SANCTUM FURNITURE  (2026-09-14, the Inner Sanctum rebuild)
# ---------------------------------------------------------------------------
# Picked off a contact sheet of the base game's own interior furniture — the
# shapes the Tenebrae maps (40/41) and the Shrine (54) actually place — and
# verified by rendering each with shape_render.py on 2026-09-14. Footpads are
# from the base TYPEFLAG.DAT, given here as world units (x, y, z) and the SI
# flags that matter for placement.
SHAPE_COLUMN_RUNE = 512         # tall stone column with green runes down each
                                 # face; 2 frames. 32x32x88, FIX|SOL. Map 54
                                 # stands 53 of them. Tall enough to read
                                 # against the sanctum's 120-tall wall stacks.
SHAPE_COLUMN_STONE = 249        # pale fluted stone column, 21 frames (some
                                 # mossed / vined). 32x32x40, FIX|SOL.
SHAPE_PLATFORM_FLAGSTONE = 113  # raised flagstone platform tile, one step
                                 # (8) high, in the same blue-grey stone as
                                 # the shape-35 floor; 128x128x8 FIX|SOL|LND.
                                 # Six frames = the edge faces (see
                                 # build_map_18.raised_platform). No ROF bit,
                                 # which is why it is the dais kit and 77
                                 # (8x8, ROF) is not: CameraProcess::findRoof
                                 # would take a ROF tile beside the Avatar
                                 # for a ceiling and clip the room.
SHAPE_PAVING_RAISED = 70        # rough pale-grey cave paving, 8 high;
                                 # 128x128x8, FIX|SOL|LND. Map 54 floors its
                                 # catacombs with 1,760. Rougher than 113.
SHAPE_TAPESTRY_ON_X_WALL = 328  # hanging tapestry, 14 frames; 0x96x40 FIX.
                                 # Zero thickness in x: hangs on a wall that
                                 # runs along y (the sanctum's west wall).
SHAPE_TAPESTRY_ON_Y_WALL = 329  # the same 14 designs, 96x0x40: hangs on a
                                 # wall that runs along x (the north wall).
SHAPE_WALL_LAMP_ON_X_WALL = 317 # glowing wall lamp, 3 frames; 32x96x16
                                 # FIX|SOL, long in y -> west wall.
SHAPE_WALL_LAMP_ON_Y_WALL = 314 # the same, 96x32x16 -> north wall.
SHAPE_PLAQUE_ON_X_WALL = 599    # gold plaque, 1 frame; footpad (0,2,2) FIX|SOL:
                                 # zero thickness in x -> west wall.
SHAPE_PLAQUE_ON_Y_WALL = 614    # the same plaque, footpad (2,0,2) -> north
                                 # wall. Both carry retail signage classes of
                                 # their own, so an LV plaque must be placed
                                 # with NPCNUM_GOLD_PLAQUE.
SHAPE_CANDELABRA = 452          # multi-arm candelabra, 12 frames; 64x32x24 SOL
SHAPE_CANDLESTICK_TALL = 453    # floor-standing candlestick, 12 frames;
                                 # 32x32x40 SOL
SHAPE_CUSHION = 812             # floor cushion, 11 frames; 32x32x8 SOL —
                                 # 8 tall, so the Avatar steps over it.
SHAPE_URN = 229                 # large ceramic urn, 1 frame; 32x32x16 SOL|LND
SHAPE_BENCH_EW = 226            # long wooden bench, 2 frames; 224x32x8
                                 # SOL|LND — long in x
SHAPE_BENCH_NS = 231            # the same bench long in y; 32x224x8
SHAPE_THRONE_STONE = 289        # engine name "Stone throne"; 160x160x32 SOL.
                                 # Frame 0 has Mordea seated in it, frame 1
                                 # is the empty throne (rendered 2026-09-14).
SHAPE_WALL_CAP_X = 670          # 4x1x1 SOL|LND stone course, 128x32x8: the
                                 # footing and lintel courses retail lays
                                 # under and over its 15 wall pieces
                                 # (Tenebrae's harbour wall, Map 39).
SHAPE_WALL_STUB_X = 47          # 2x1x5 SOL stone wall stub, 64x32x40: the
                                 # half-width piece retail uses where a
                                 # 15 would not fit (Map 39's harbour wall).
SHAPE_GLOB_WALL_PIECE = 15      # the 128x32x40 stone wall segment glob 80
                                 # bakes along its floor tiles' south edge.
                                 # build_map_18's gate-hardening courses and
                                 # the DD-005 crack-line fills are built from
                                 # it, so any explicit wall on a line that
                                 # glob 80 used to wall should use it too.
SHAPE_STONE_WALL_NS_SHORT = 8  # 1x3x5 SOL|LND, 32x96x40: the three-quarter
                                 # length of SHAPE_STONE_WALL_NS (10), which
                                 # retail uses to finish a north-south run off
                                 # the 128 grid (Tenebrae's gate wall, Map 39).
SHAPE_WALL_CAP_Y = 692          # 1x4x1 SOL|LND, 32x128x8: SHAPE_WALL_CAP_X
                                 # (670) long in y, the lintel course retail
                                 # lays between the two 10 courses of a
                                 # north-south wall (603 uses on Map 39).
SHAPE_WALL_CAP_Y_SHORT = 726    # 1x3x1 SOL|LND, 32x96x8: the same lintel,
                                 # three-quarter length.

SHAPE_ALTAR_STONE = 550         # engine name "altar"; 2 frames of a carved stone altar
                                 # block (verified 2026-07-19 render). TYPEFLAG
                                 # [SI_SOLID, SI_LAND] SF_GENERIC fp (2,4,2).
                                 # Preferred over 429 (also "altar", but SI_BAG — clicking
                                 # would pop a container gump on a ceremony altar) and over
                                 # 206 ("Altar of Focus", a specific unrelated U8 artifact
                                 # whose name would mislead). REPLACED shape 721
                                 # ("chimney") as the Map 18 endgame ceremony centerpiece.


# ===========================================================================
# CUSTOM INJECTED SHAPES
# ===========================================================================
# These ids exist ONLY in the patched shared/build/U8SHAPES.FLX (produced by
# lv_wood_wall.py), not in the base game's U8SHAPES.FLX. Code that resolves
# these ids to pixels/frame-counts MUST use frame_count() below (or
# equivalent logic that prefers BUILD_SHAPES_FLX) — looking them up against
# the base game copy will fail.
#
# 855 is NOT one of them. It was declared here as SHAPE_WOOD_PLANK_FLOOR but
# never injected, never TYPEFLAG-patched and never placed (adversarial-review
# L14); the id is unallocated. Art injected by tools/png2shape.py starts at
# 859 — add its constant here when it is first placed on a map.

SHAPE_WOOD_PLANK_WALL_SE = 856      # 39x60 SE-facing wood-plank wall, replaces shape 24
                                     # (verified 2026-07-01, custom art)
SHAPE_WOOD_PLANK_WALL_SW = 857      # 40x61 SW-facing wood-plank wall, replaces shape 20
                                     # (verified 2026-07-01, custom art)
SHAPE_WOOD_PLANK_CORNER_POST = 858  # 16x48 wooden corner post, replaces shape 255 frames
                                     # 0-3 (verified 2026-07-01, custom art)


# ===========================================================================
# LEGACY_PLACEHOLDERS
# ===========================================================================
# *** WARNING ***
# Every shape in this section is a BASE-GAME PLACEHOLDER standing in for art
# that has not been made yet. They are catalogued here — with what they
# ACTUALLY render as — specifically so nobody mistakes them for the thing
# they're being used to represent. See shared/docs/art-placeholder-audit.md
# for the full priority-ranked replacement list (Shades, Water Zombie,
# Harpie, Shield halves, 3 Gods, Zealan NPCs, Elemental Columns, Magnetic
# Obelisk, and more all currently point at one of these).

SHAPE_PLACEHOLDER_FIRE_VFX = 400
# Renders as an animated fire/explosion visual effect (orange/red flame
# licking upward from a red-yellow burst ring), 30 frames — it is NOT an
# NPC (verified 2026-07-01 render). build_map_17/18.py use this as
# SHAPE_NPC for skeleton "dead" frames and god figures; per
# art-placeholder-audit.md it is also the current stand-in for the Water
# Zombie, Harpie, the 3 Gods, Zealan NPCs/child, the Monster Skull, and Lord
# British. Every one of those placements will visually read as a fire
# effect, not a character, until replaced.

SHAPE_PLACEHOLDER_MAGIC_BURST_VFX = 580
# Renders as an animated white/gray magic-burst spark effect (radiating
# spiky flash), 120 frames — it is NOT an item (verified 2026-07-01
# render). build_map_10/11/17/18.py use this as SHAPE_TALISMAN for quest
# items (including the Shield halves per art-placeholder-audit.md). Every
# one of those placements will visually read as a magic flash, not a solid
# object, until replaced.
# WARNING (in-game 2026-07-04): shape 580 is TYPEFLAG SI_FIXED — items
# placed with it CANNOT be picked up. Any carryable quest item still on
# 580 (Shield halves, ...) is unpickable scenery and needs the same fix
# the elemental talismans got below. Fixed so far: the elemental
# talismans (-> 596, below) and the Passage Stone (-> 798,
# SHAPE_PASSAGE_STONE in QUEST ITEMS).

SHAPE_SHIELD_HALVES = SHAPE_SHIELD_HALVES_1994   # 878
# The two halves of the Shield of the Ancients, the quest items, since
# 2026-10-17 the 1994 art (phase C, Map 17): frame 0 the sun half (half 1,
# screen11, beside the obelisk), frame 1 the eye half (half 2, screen12, in
# the throne nook). TYPEFLAG is 828's row (carryable, SF_GENERIC, NOT an
# equip-slot item), footpad (1,3,3).
#
# Was 870 (the retail 828 split, 2026-10-11; since 2026-10-17 878's legacy
# alias, SHAPE_SHIELD_HALVES_LEGACY), 539,
# retail "shield", from 2026-07-19 (and 580, SI_FIXED, before that). 539 had
# two faults: every Pagan shield of frame 0 (ten in the new game's NONFIXED)
# passed SHADES's half-1 check, and it is a shield-slot item whose worn frame
# the paperdoll draws as frame + 1.
#
# MUST equal TYPE_SHAPES['TypeAOFrizbee']: SHADES.UNK:138 finds the halves
# by it and tells them apart by frame 0/1. The RESTORED shield is 879
# (SHAPE_SACRED_SHIELD_1994, TypeSacredShield) since 2026-10-17, created by
# SHADES and popped onto the Map 18 altar by AOSCENE, never placed; it was
# 828 (TypeAOArtifact) until then.

SHAPE_TALISMAN_GEM = 596
# "gemstone ring" (engine name), 8 frames, TYPEFLAG carryable (not FIXED).
# The elemental talisman placeholder since 2026-07-04 (the Synopsis calls
# the tokens "gemstones"): frames 0-3 are visually distinct colored gems
# and encode element identity (0=Earth 1=Air 2=Fire 3=Water, matching the
# pillar/receptacle mapping in build_map_11.py). Replaced shape 580, whose
# SI_FIXED flag made the placed talismans unpickable (found in-game at the
# Fire site during the first COLPUZZL run).

SHAPE_PLACEHOLDER_GENERIC_PILLAR = 721
# Renders as a squat brick/stone pillar (reads as a chimney), 6 frames
# (verified 2026-07-01 render). build_map_10/11/17/18.py reuse this single
# shape for at least four unrelated concepts: SHAPE_PILLAR (elemental
# columns — custom art 865 since 2026-09-24, SHAPE_ELEMENTAL_PILLAR),
# SHAPE_OBELISK (magnetic obelisk — custom art 861 from 2026-09-15, retired
# 2026-10-17 for screen11's retail composite), SHAPE_ALTAR (temple altar), and
# SHAPE_SACRED_ROCK (stone circle marker — custom art 863). See
# art-placeholder-audit.md — HIGH priority (Elemental Columns), and
# docs/art-track.md for what remains.

SHAPE_PLACEHOLDER_INVISIBLE_EGG = 73
# A plain egg/marker shape with no visible sprite — renders as INVISIBLE
# in-game. Per art-placeholder-audit.md this is the current placeholder for
# the Hoskuld & Gunnar Shade ghosts, which are consequently invisible
# in-game until replaced with a translucent spirit sprite. build_map_10.py
# places one under this name as the Passage Test trigger (PLNTST egg,
# quality 283 + npcnum 0x44, DD-007a convention — same shape as
# SHAPE_LB_EGG below). Listed here so nobody reaches for shape 73
# expecting a visible marker egg.

SHAPE_DEBUG_REFLECT_MARKER = 636
# Renders as a bright orange diamond tile with the literal text "REFLECT"
# on it, 1 frame (verified 2026-07-01 render) — an SI_EDITOR debug/level-
# editor marker, not game content. Not used by any build_map_*.py today.
# Do not place this shape in real map content.


# ===========================================================================
# LORD BRITISH QUEST SCENE (quest step 1 — shared/docs/wiring.md)
# ===========================================================================

SHAPE_LB_EGG = 73            # SF_UNKEGG (the only shape with that family — see
                              # parse_typeflag.py), invisible trigger egg. Placed
                              # with quality = pinned EggLBScene class id - 0x47F and
                              # npcnum = 0x44 (4x4 hatch range, DD-007a convention —
                              # see build_shape_gallery.py's DD-007 spike, VERIFIED
                              # IN-GAME 2026-07-03). Do NOT confuse with
                              # SHAPE_LB_APPARITION below — this egg has NO sprite.
SHAPE_LB_APPARITION = 411    # "ghost" placeholder for the Lord British apparition —
                              # 201 frames, covers the puppet animation's frames 0-9
                              # (verified frame count 2026-07-03, wiring.md). TYPEFLAG
                              # family is SF_CONTAINER (verified 2026-07-03) — an odd
                              # fit for a scenery ghost (double-click would pop an
                              # empty container gump instead of doing nothing), but a
                              # plain item placement with no npcNum renders fine and
                              # is not npcnum-dispatched; the real LB art is a pending
                              # art-placeholder-audit item. Matches TYPE_SHAPES'
                              # TypeLordBritish entry in u8c_symbols.py — this value
                              # and that one must stay in sync (LORDBRIT.UNK's
                              # `foreach item where type = TypeLordBritish` filters on
                              # exactly this shape id).
SHAPE_MAGIC_SPARKLE = 587    # sparkle VFX (30 frames) — proven from retail STRATOS
                              # bytecode (`magic.create(TypeMagicSparkle, 11)` compiles
                              # to `push 024Bh` = 587; see wiring.md). Matches
                              # TYPE_SHAPES' TypeMagicSparkle entry.


# ===========================================================================
# Monster-egg creature shapes (M12)
# ===========================================================================
# A MonsterEgg (shape 500) packs its spawn into the quality word as
# (prob<<11)|monster_shape (see MapItem.monster_egg and ScummVM
# monster_egg.h: getMonsterShape()=quality&0x7FF, getProb()=(quality>>11)&0x1F).
# The low 11 bits are a real U8 actor shape. Before 2026-07-24 the builders
# passed a raw small id (10, 20, 40, ...) as the whole quality, which
# decoded to prob=0 (never hatch) and a terrain shape — so the harpie zone,
# Galjeron's lair, and the elemental sections spawned nothing.
#
# These are v1 base-game stand-ins (PLAN 4.1 accepts tuned base creatures
# until bespoke art exists). All are engine-name-verified TYPEFLAG family-6
# actors. Each is one constant — adjust flavor freely.
SHAPE_MON_LAIR_GUARDIAN = 83   # troll      — Galjeron's lair (Map 9)
SHAPE_MON_ZOMBIE        = SHAPE_WATER_ZOMBIE  # 872, was the ghoul 142 — the Lake (Map 10)
SHAPE_MON_WILDERNESS    = 76   # kith       — Vale wilds, winged (Map 10)
SHAPE_MON_PROWLER       = 807  # spider     — Vale wilds (Map 10)
SHAPE_MON_EARTH         = 214  # golem      — earth section (Map 11)
SHAPE_MON_AIR           = 509  # seeker     — air platforms, floating (Map 11)
SHAPE_MON_FIRE          = 96   # daemon     — fire section (Map 11)
SHAPE_MON_WATER         = 806  # skellot    — water section (Map 11)
# The harpie zone hatched 76 "kith" (a spider) until 2026-07-25, then 120
# "torax" (a sweep of all 43 named family-6 shapes found no winged creature
# in U8), and since 2026-10-11 the Harpie itself, 873 (contract 9).
SHAPE_MON_HARPIE        = SHAPE_HARPIE  # 873, was the torax 120 — harpie zone (Map 13)
SHAPE_MON_TEMPLE_GUARD  = 214  # golem      — Ancient Temple guardian (Map 18)

# Default spawn probability (high 5 bits of the egg quality, 0..31). Base
# game clusters at 3-7; 6 spawns reliably without the max churn of 7.
MONSTER_PROB_DEFAULT = 6


# ===========================================================================
# ITEM-BEHAVIOUR CLASS SHAPES (orphan triage, decision D — 2026-07-26)
# ===========================================================================
# Shapes for the LV item classes reached by the engine's npcnum+1024 patch
# (see NPCNUM_BANDS below). Each item is placed with a per-placement
# npcnum, so the behaviour attaches to THAT item and not to every item of
# the shape — which is why these can be ordinary base-game shapes without
# hijacking base-game content.
#
# Every id here was chosen by NAME from shared/corpus/shape_names.json and
# then checked against TYPEFLAG, because the compiler-side TYPE_SHAPES
# table is wrong for most of these (CLAUDE.md flags it as legacy and
# unverified, and it is):
#   TypeAbacus/TypeNSGoldPlaque -> 158, which is SI_FIXED and renders as a
#     wooden STOOL (see SHAPE_STOOL above);
#   TypeMonskul -> 189, a 322-frame SF_CONTAINER humanoid;
#   TypeFedora -> 578, an 81-frame SI_IGNORE/SI_DRAW effect shape.
# Placing on those would have repeated the SI_FIXED trap that made four
# quest items unpickable. None of the shapes below is SI_FIXED.

SHAPE_ABACUS = 375
# "abacus" (engine name), 1 frame, SI_SOLID, weight 3 — carryable, not
# SI_FIXED. TypeAbacus (ABACUS.UNK) only implements look()/use() and never
# branches on frame, so a single frame is sufficient.

SHAPE_BEDROLL = 534
# "bedroll" (engine name), 1 frame, SI_SOLID, weight 1 — carryable.
# NOTE this is not a flavour item despite being grouped with the joke
# items: TypeBedroll::use() (BEDROLL.UNK) is the base game's bed code —
# it asks how long to rest, advances the clock, and restores HP and mana
# in full. Placing one is a rest point, so exactly one is placed.

SHAPE_HAT = 531
# "helmet" (engine name), 10 frames, equipType 2 (head slot), weight 3,
# not SI_FIXED. Stands in for TypeFedora (FEDORA.UNK), which only barks
# "Fedora" on look(). U8 has no fedora; a helmet is the only head-slot
# wearable, so this is a placeholder for the joke, not a match.

SHAPE_ROPE = 533
# "rope" (engine name), not SI_FIXED, weight 10. Stands in for
# TypeBullwhip (BULLWHIP.UNK), which only barks "Bullwhip" on look().
# A name sweep of shape_names.json found NO whip/lash/flail shape in U8 at
# all, so a coiled rope is the closest silhouette. Placeholder, not a
# match — a real bullwhip needs art.

SHAPE_SKULL_LOOSE = 331
# "skull" (engine name), 26 frames, SI_SOLID|SI_LAND, weight 5, not
# SI_FIXED — a loose carryable skull. TypeMonskul (MONSKUL.UNK) barks
# "Strange skull" on look() and reads out a Zealan priestess's letter on
# use(); it never branches on frame. Deliberately NOT 641/663, which are
# also named "skull" but are SI_FIXED scenery.

SHAPE_POTION_REAL = 859
# CHANGED 766 -> 859 on 2026-07-27 (DD-005, the last step).
# For TypePotion (POTION.UNK), which branches on getFrame() 0-8:
#   0 empty, 1 heal, 2 mana, 3 heal-some, 4 damage, 5 protection,
#   6 sleep, 7 invisibility, 8 TINY TAR (shrink).
# The base game's potion (766) has only frames 0-7 — the expansion's ninth
# frame did not survive, so frame 8 could not be rendered or placed and
# NOTHING in the game could shrink the Avatar. Since DD-005 makes the
# shrink the way into the Ancient Temple, that was a hard progression
# stop: the Map 18 crack admits only a 32x32 body and nothing could
# produce one.
# 859 is a 9-frame copy of 766 generated and injected by
# agents/map-populator/src/lv_tiny_tar.py, wired into
# tools/build_artifacts.sh as a build step so it is not dropped by an
# artifact rebuild. Frames 0-7 are re-encoded unchanged; frame 8 is
# frame 1 with only its 36 liquid pixels recoloured to tar. TYPEFLAG is
# copied wholesale from 766, so it stays a carryable weight-1 potion.
# Distinct from build_map_10.py's local SHAPE_POTION, which is 809, an
# alchemical FLASK used as scenery/reagent dressing.


# ===========================================================================
# npcnum allocation (the engine's npcnum+1024 usecode dispatch)
# ===========================================================================
# The patched Item::callUsecodeEvent (tools/scummvm-patches/
# 0001-lost-vale-engine.patch) redirects an item's usecode to class
# npcnum+1024 when the item has a nonzero npcnum, is NOT an egg family
# (eggs reuse the npcnum byte for hatch ranges), is not EXT_PERMANENT_NPC,
# and that class is non-empty. npcnum is ONE BYTE in the 16-byte FIXED.DAT
# record, so the reachable class window is 1025-1279 and nothing outside it
# can ever be addressed this way.
#
# Two properties have to hold for any npcnum we hand out, and both were
# re-verified by scan on 2026-07-26:
#   1. class npcnum+1024 must be EMPTY in the base game's USECODE.FLX,
#      otherwise we would be overwriting a base-game class (106 of the 255
#      slots are occupied — the base game's own NPCs live here);
#   2. no item on ANY map may already carry that npcnum byte.
# On (2) the base game is clean: a scan of base FIXED.DAT found ZERO
# non-egg items carrying npcnum. Every base-game npcnum byte sits on an
# egg shape (2/73/500/508), which the patch excludes. So no base-game item
# can be hijacked by a class we add in this window.
#
# CORRECTION 2026-07-28: that last sentence used to be load-bearing and was
# only HALF true, and the missing half cost two live event eggs. The egg
# exclusion existed in `Item::callUsecodeEvent` (dispatch) but NOT in
# `Map::loadFixedFormatObjects` (the Actor promotion), so an egg whose hatch
# range happened to fall in 100-116 — 0x66, a plain +/-192, is enough — was
# promoted into an Actor at load time and could never hatch again. Map 18's
# EggCrackHint and EggAOCeremony were both dead this way, and both landed in
# slot 102, which is also Sigrid. The exclusion is now in BOTH places and is
# pinned by agents/map-populator/src/test_engine_patch.py. Ranges 0x64-0x74
# are legitimate and stay legitimate; the invariant is engine-side.
#
# Allocated bands:
#   100-116  villagers (build_map_10.py). ALSO the Actor-promotion window
#            in the patched map.cpp — the only npcnums that become real
#            Actors. All 17 slots are in use. An NPC/Actor class MUST live
#            here; an item class must not, because it does not need it.
#   120      the four Map 11 receptacles (TypeReceptacle, class 1144).
#   200-213  LV teleport ids. These sit on teleport eggs (shape 508), so
#            they are range/destination data and never dispatch — but the
#            numbers are reserved to keep the two namespaces readable.
#   228-249  LV item-behaviour classes (decision D). 228-236 assigned
#            below; 237-249 is headroom in the same verified-free run.
#
# Free contiguous runs still available (class empty AND byte unused
# anywhere): 76-83, 88-93, 121-127, 214-224, 237-249.
#
# Machine-readable form of the table above, so a future allocation can be
# checked against it instead of re-deriving it: band -> what owns it.
NPCNUM_BANDS = {
    (100, 116): "villagers / Actor-promotion window (build_map_10.py) — FULL",
    (120, 120): "Map 11 receptacles, TypeReceptacle class 1144",
    (200, 213): "LV teleport ids (on egg shapes — reserved, never dispatch)",
    (228, 249): "LV item-behaviour classes (decision D); 237-249 free",
}

NPCNUM_SHIELD_HALVES = 236   # -> class 1260 TYPEAOFRIZBEE  (Map 17)
NPCNUM_MONSKUL       = 228   # -> class 1252 TYPEMONSKUL    (Map 18)
NPCNUM_POTION        = 229   # -> class 1253 TYPEPOTION     (Map 10)
NPCNUM_ABACUS        = 230   # -> class 1254 TYPEABACUS     (Map 10)
NPCNUM_BEDROLL       = 231   # -> class 1255 TYPEBEDROLL    (Map 10)
NPCNUM_BULLWHIP      = 232   # -> class 1256 TYPEBULLWHIP   (Map 10)
NPCNUM_FEDORA        = 234   # -> class 1258 TYPEFEDORA     (Map 10)
NPCNUM_GOLD_PLAQUE   = 235   # -> class 1259 TYPENSGOLDPLAQUE (Map 17, since
                             #    2026-09-25; quality picks the text,
                             #    lv-patched/PLAQUENS.UNK)
# 233 -> 1257 TYPEPEDESTALS is pinned in lv_manifest.json but deliberately
# NOT placed — see docs/reviews/2026-07-25-orphan-triage.md section 6.


# ===========================================================================
# frame_count() helper
# ===========================================================================

_frame_count_cache = {}
_flx_data_cache = None


def _load_effective_flx_bytes():
    global _flx_data_cache
    if _flx_data_cache is None:
        with open(_effective_shapes_flx_path(), 'rb') as f:
            _flx_data_cache = f.read()
    return _flx_data_cache


def frame_count(shape_id):
    """Return the number of valid (non-null) frames for shape_id.

    Reads the effective U8SHAPES.FLX — the patched shared/build copy if it
    exists (so custom shapes 856-858 resolve correctly), otherwise the base
    game copy. Result is cached per shape_id for the life of the process.
    Returns 0 if the shape id has no data or no valid frames.
    """
    if shape_id in _frame_count_cache:
        return _frame_count_cache[shape_id]

    flx_data = _load_effective_flx_bytes()
    shape_data = read_flx_entry(flx_data, shape_id)
    if shape_data is None:
        _frame_count_cache[shape_id] = 0
        return 0

    frames = parse_shape_frames(shape_data)
    count = sum(1 for fr in frames if fr is not None)
    _frame_count_cache[shape_id] = count
    return count


if __name__ == "__main__":
    # Quick self-test: python3 lv_shapes.py
    print("effective U8SHAPES.FLX:", _effective_shapes_flx_path())
    checks = [
        (SHAPE_BOOK_CLOSED, 24),
        (SHAPE_CHEST_ORNATE, 1),
        (SHAPE_STOOL, 2),
        (SHAPE_WOOD_PLANK_WALL_SE, None),
    ]
    for shape_id, expected in checks:
        got = frame_count(shape_id)
        status = "OK" if (expected is None or got == expected) else "MISMATCH"
        print(f"  frame_count({shape_id}) = {got}  (expected {expected})  {status}")

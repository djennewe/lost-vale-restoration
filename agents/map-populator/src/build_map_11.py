#!/usr/bin/env python3
"""
build_map_11.py — Map 11: Elemental Dungeon

Large dungeon with four elemental sections, central hub, Four Pillars exit,
and teleporter pad.

Layout: ~40x40 chunks (20,480x20,480 world units)
  - Entry Hall (6x6 chunks, center-north)      worked stone
  - Central Hub (6x6 chunks, center)           worked stone
  - Earth Section (10x10 chunks, north-west)   cave
  - Air Section (10x10 chunks, north-east)     cave floor, terraces, spires
  - Fire Section (10x10 chunks, south-west)    cave, lava, causeways
  - Water Section (16x10 chunks, south-center) damp stone, islands
  - Four Pillars Chamber (8x6 chunks, south)   worked stone
  - Teleporter Pad (2x2 chunks, after pillars) worked stone

REBUILT 2026-09-15 (cleanup plan, docs/reviews/2026-09-14-map-cleanup-plan.md
§3, Map 11). What it had: 421 ceiling tiles laid one per 512-unit chunk
(6% cover, a grid of floating squares over every room, the Fire section's
at z=32 — below head height), 48 wall reliefs standing loose on floors,
six chests and two chimneys as decoration, and "platforms" and "walkways"
that were single 128-unit tiles every 256 or 512 units — the Air
section's talisman had to be grounded because its platform was nine
separate tiles. Now: no ceilings (the base game's dungeons and planes
stand open to the dark); the four worked rooms in the stone-wall pair
the temple uses, with columns, lamps and tapestries; the cave sections
in cave wall with cycled frames; real terraces and causeways built from
the platform kit on the 8-unit lattice; each section dressed after its
plane — Maps 44/45/46, the Planes of Fire/Water/Air, rendered on
2026-09-15.

THE BOUNDARY (plan §3, Map 11): every active pin — the four talismans,
the four pillars and receptacles, the two sealing boulders, the four
teleport eggs — keeps its coordinates, z and quality. (The seventeen
monster eggs did too until 2026-10-11, when they moved out of rock and
lava and gained their MONEGG triggers; test_monster_eggs.py.)
`test_route_reach.py` proves the four talismans and the pillars
chamber reachable from the arrival pad by a route that never stands on
a damaging tile, before and after this rebuild. Lava and flame stay
hazards beside the way, never on it; decorative water has no SEA flag.
Retail SEA tiles drown (the 2026-07-04 Earth-talisman finding) and lethal geometry
is puzzle content for another queue.
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from u8_map import MapItem, generate_terrain_grid
from lv_monster_eggs import monster_group
from lv_landscape import rim
from lv_furnish import (
    GLOB_FLAGSTONE_FLOOR, floor_grid, raised_platform, column, accent_reliefs,
    TIER, PAVING_FRAMES, WALL_NS, WALL_EW, WALL_PLAIN,
)
import lv_cave_vignette as cave_vignette
import vignette_place
from lv_shapes import (
    SHAPE_CAVE_WALL_E,               # 26: cave wall long in x (east-west runs)
    SHAPE_CAVE_WALL_S,                # 32: cave wall long in y (north-south runs)
    SHAPE_ROCK_SPIRE_CLUSTER,         # 66: jagged rock spire cluster, 128x128x40
    SHAPE_ROCK_SLAB_GROUND,           # 301: flat rock slab, floor marking
    SHAPE_BOULDER_PILE,               # 300: flat rubble patch
    SHAPE_BOULDER_LARGE,              # 796: a boulder, 64x64x56
    SHAPE_LAVA_POOL,                  # 318: 256x256 lava, damaging
    SHAPE_TRAP_BURST_A,               # 435-437: flame tiles, damaging
    SHAPE_TRAP_BURST_B,
    SHAPE_TRAP_BURST_C,
    SHAPE_STALACTITE,                 # 186: 96x96x48
    SHAPE_MUSHROOM_CLUSTER,           # 65: cave fungus
    SHAPE_BONES_A,
    SHAPE_BONES_B,
    SHAPE_CLIFF_FACE_DETAIL,          # 125
    SHAPE_TALISMAN_GEM,               # 596 — the talismans
    SHAPE_ELEMENTAL_PILLAR,           # 865: the elemental pillars (custom art)
    SHAPE_PILLAR_RECEPTACLE,          # 866: the receptacles (custom art)
    SHAPE_PAVING_RAISED,              # 70: raised paving, dark frames 0-2
    SHAPE_PLACEHOLDER_INVISIBLE_EGG,  # 73: UnkEgg, class = quality + 0x47F
    SHAPE_PLATFORM_FLAGSTONE,         # 113: raised flagstone
    SHAPE_TAPESTRY_ON_X_WALL,
    SHAPE_TAPESTRY_ON_Y_WALL,
    SHAPE_WALL_LAMP_ON_X_WALL,
    SHAPE_WALL_LAMP_ON_Y_WALL,
    SHAPE_URN,
    SHAPE_AXE,                        # 419: the hub's weapon cache
    SHAPE_MON_EARTH, SHAPE_MON_AIR, SHAPE_MON_FIRE, SHAPE_MON_WATER,  # M12 elemental creatures
    SHAPE_CAVE_FACE_1994,             # 891: screen07's walls, 1994 faces
    SHAPE_CAVE_FLOOR_1994,            # 892: screen07's floor, 1994 pit
    SHAPE_BLOCKER_X, SHAPE_BLOCKER_Y,
    SHAPE_CAVE_BACKDROP_LARGE, SHAPE_DECORATIVE_WATER,
)

REGISTRY = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'vignettes', 'art_registry.json')

SHAPE_BLOCKER_X_LOW = 704  # retail invisible 128 by 32 by 32 wall
SHAPE_BLOCKER_Y_LOW = 705  # retail invisible 32 by 128 by 32 wall

SHAPE_EXIT_PAD = 779  # retail Map 44's flat star-carved stone, 256x256x0


# The axe at the hub (build_central_hub), max corner, z: inside the north
# gap from the Entry Hall, on the way to every section.
HUB_WEAPON = (9599, 4479, 0)


from lv_art_props import CAVE_BACKDROP_CLIPS

# === TERRAIN GLOB INDICES ===
GLOB_DUNGEON_FLOOR = 42     # stone dungeon floor (16x shape 242, LAND —
                            # proven walkable in-game 2026-07-04): cobbles
                            # with moss, the cave sections' floor
GLOB_WORKED_FLOOR = GLOB_FLAGSTONE_FLOOR  # 65: the worked rooms' flagstones
                            # (2026-09-15 — moss on a hall floor read as a
                            # garden in-engine)
# Element-section floors FIXED 2026-07-04 after the first in-game visit
# (tester drowned at the Earth talisman): the original glob picks were
# never verified against TYPEFLAG —
#   55 = 16x shape 347 SEA (water plates; the Tenebrae-moat family),
#   60 = EMPTY (Fire section had no floor at all),
#   70 = shape-35 floor plus stray wall pieces (8/12/14/15/46) that tiled
#        a phantom "maze" across the whole Air section.
GLOB_EARTH_FLOOR = GLOB_DUNGEON_FLOOR
# 2026-09-15, from a scan of every 16-tile floor glob against TYPEFLAG:
# 480 (16x shape 425, scorched cracked earth) until 2026-10-17. Since then
# the Fire wing is floored in retail cave rock, glob 397 (16x 301), the
# floor the 1994 screen05 shows it with (place_screen05); 301 against 425
# at the shot's mouth read as a patch.
GLOB_FIRE_FLOOR = 397
GLOB_CHAMBER_FLOOR = 397    # the Four Pillars chamber, a cave since
                            # 2026-10-17 (screen07; build_four_pillars)
GLOB_LAVA_LAKE = 802        # 16x shape 409: the Plane of Fire's own lava
                            # (Map 44). LAND, and NOT harmless: its class
                            # CLRLAVA burns whatever touches it, and its
                            # frame-33 tiles kill (exact_reach.HURT_SHAPES_U8).
GLOB_WATER_FLOOR = GLOB_FLAGSTONE_FLOOR   # 65: shape-35 flagstones, damp stone
GLOB_AIR_FLOOR = 397        # 16x shape 301: grey rock slabs, no moss

# Quest items
SHAPE_TALISMAN = SHAPE_TALISMAN_GEM  # 596 "gemstone ring": carryable, frames
                                     # 0-3 = element identity. Was 580, whose
                                     # SI_FIXED flag made talismans unpickable
                                     # (in-game 2026-07-04).
SHAPE_PILLAR = SHAPE_ELEMENTAL_PILLAR  # 865, custom art since 2026-09-24 (art
                                     # track contract 5; was 721, the CHIMNEY).
                                     # Frames 0-3 are the elements in the order
                                     # below; TypeElementalColumn resolves here.
SHAPE_RECEPTACLE = SHAPE_PILLAR_RECEPTACLE  # 866, custom art (was 307, a chest).
                                     # The shape is cosmetic: dispatch is npcnum.
SHAPE_SEALING_BOULDER = SHAPE_ROCK_SPIRE_CLUSTER  # 66: FIXED|SOLID footpad 4x4x5 —
                                   # actually blocks (300/301 are flat rubble)

# ── Column puzzle wiring (COLPUZZL.UNK rewrite, 2026-07-04) ──────────────
# The four receptacles dispatch TypeReceptacle::use() via the engine's
# npcnum+1024 patch: npcnum 120 -> class 1144 (0x478), manifest-pinned
# TYPERECEPTACLE. npcnum is a single byte in the FIXED.DAT record, so the
# class must live in 1024-1279; 1144 sits in the empty base-FLX gap
# 1088-1153, outside the Actor-promotion range (100-116), and no base-map
# item carries npcnum 120 (scan 2026-07-04).
RECEPTACLE_NPCNUM = 120
# The doorway between the Four Pillars chamber and the Teleporter Pad is
# plugged by quality-299 sealing boulders; COLPUZZL destroys exactly
# quality-299 shape-66 items on completion (quality guards ambient rubble).
SEALING_BOULDER_QUALITY = 299

# ── Re-applying the puzzle on every arrival (2026-10-10) ─────────────────
# The pillars and boulders are fixed records, and World::switchMap re-reads
# every fixed record on each entry, so COLPUZZL's destroy() lasted only
# until the player left (docs/playtest-2026-10-10-maps3.md finding 1).
# EggReapply (lv-new/REAPPLY.UNK) destroys them again from the globals
# COLPUZZL sets. It stands on every arrival pad, so it hatches as the
# player lands. quality 307 -> class 1458 (manifest EGGREAPPLY; a UnkEgg
# quality, unrelated to Map 18's breach-wall quality 307). npcnum 0x44 =
# +/-128 round the pad; not 100-116, the engine's Actor promotion window.
# build_map_10 places the same egg on its pads for the Test Plant, and
# build_map_17 on its one pad for the Shield halves; the egg also removes
# the talismans here once used or carried (REAPPLY.UNK header).
REAPPLY_EGG_QUALITY = 307
REAPPLY_EGG_NPCNUM = 0x44



def reapply_egg(x, y, z):
    """An EggReapply egg on the arrival pad at (x, y, z)."""
    return MapItem(x=x, y=y, z=z, shape=SHAPE_PLACEHOLDER_INVISIBLE_EGG,
                   frame=0, quality=REAPPLY_EGG_QUALITY,
                   npcnum=REAPPLY_EGG_NPCNUM)


# Cave wall frames: 26 f0-6 and 32 f0-6 are all rock textures (grid-rendered
# 2026-09-15; f7/f8 are black, 26 f13 red). Runs cycle four so no wall is
# one tile repeated.
CAVE_FRAMES = (0, 1, 2, 3)
CAVE_COURSE = 48
# SHAPE_PAVING_RAISED's dark set, for the Fire causeways: (inner, +y face,
# +x face, corner) by analogy with the pale set 3/4/5.
DARK_PAVING = (0, 0, 1, 2)


# ── Wall-run helpers (2026-07-04 wall-spacing fix) ───────────────────────
# Items are MAX-CORNER boxes: an item at origin (x, y) with footpad
# (fx, fy, fz) occupies (x-fx*32, x] × (y-fy*32, y] × [z, z+fz*8).
# SHAPE_CAVE_WALL_E (26, footpad 4×1×6) and SHAPE_CAVE_WALL_S (32, footpad
# 1×4×6) are 128 units long along their run axis, but the original
# builders placed them every 256 units — every wall was a picket fence
# with a 128-unit hole per segment (map_walkability wall survey:
# 255/255 + 202/202 leaking joints). The base game tiles these shapes
# every 128. ALL wall runs go through these two helpers: 128 stride,
# spans sealed end to end, doorways carved via explicit `skip` origin
# lists (skipping origin o opens the span (o-128, o]).
#
# 2026-09-15: `shape` selects the wall — the cave pair by default, the
# stone pair (WALL_EW / WALL_NS, 128 long the same way) for the worked
# rooms. Cave runs cycle their frames; stone runs take `frame`.

def wall_run_e(items, x_start, y, span, frame=0, skip=(), z=0,
               shape=SHAPE_CAVE_WALL_E):
    """Tile a wall long in x along x, sealing (x_start, x_start+span].

    Segment origins are x_start+128 .. x_start+span every 128; the
    segment at origin o covers x (o-128, o] × y (y-32, y]. Origins listed
    in `skip` are omitted, opening the doorway span (o-128, o] each.
    """
    for i, x in enumerate(range(x_start, x_start + span, 128)):
        origin = x + 128          # max-corner: this segment covers (x, x+128]
        if origin in skip:
            continue
        fr = CAVE_FRAMES[i % len(CAVE_FRAMES)] if shape == SHAPE_CAVE_WALL_E else frame
        items.append(MapItem.placed_item(x=origin, y=y, z=z,
                                         shape=shape, frame=fr))


def wall_run_s(items, x, y_start, span, frame=0, skip=(), z=0,
               shape=SHAPE_CAVE_WALL_S):
    """Tile a wall long in y along y, sealing (y_start, y_start+span].

    Segment origins are y_start+128 .. y_start+span every 128; the
    segment at origin o covers y (o-128, o] × x (x-32, x]. Origins listed
    in `skip` are omitted, opening the doorway span (o-128, o] each.
    """
    for i, y in enumerate(range(y_start, y_start + span, 128)):
        origin = y + 128          # max-corner: this segment covers (y, y+128]
        if origin in skip:
            continue
        fr = CAVE_FRAMES[(i + 2) % len(CAVE_FRAMES)] if shape == SHAPE_CAVE_WALL_S else frame
        items.append(MapItem.placed_item(x=x, y=origin, z=z,
                                         shape=shape, frame=fr))


def stone_room(items, x0, y0, w, h, courses, skips):
    """Walls of a worked-stone room (x0..x0+w, y0..y0+h): `courses` of the
    stone pair, ground course carrying the doorways in `skips` = (north,
    south, west, east) skip sets, the upper courses continuous — a
    40-unit lintel the 40-tall Avatar passes under."""
    n, s, w_, e = skips
    for c in range(courses):
        first = len(items)
        z = c * 40
        lint = c > 0
        wall_run_e(items, x0, y0, w, frame=WALL_PLAIN, z=z, shape=WALL_EW,
                   skip=() if lint else n)
        wall_run_e(items, x0, y0 + h - 1, w, frame=WALL_PLAIN, z=z, shape=WALL_EW,
                   skip=() if lint else s)
        wall_run_s(items, x0, y0, h, frame=WALL_PLAIN, z=z, shape=WALL_NS,
                   skip=() if lint else w_)
        wall_run_s(items, x0 + w - 1, y0, h, frame=WALL_PLAIN, z=z, shape=WALL_NS,
                   skip=() if lint else e)
        # Preserve the doorway lintels as invisible solids. Their drawn
        # faces cover the quest bands on either side of each opening.
        if lint:
            for it in items[first:]:
                if it.shape == WALL_EW and (
                        (it.y == y0 and it.x in n) or
                        (it.y == y0 + h - 1 and it.x in s)):
                    it.shape, it.frame = SHAPE_BLOCKER_X, 0
                elif it.shape == WALL_NS and (
                        (it.x == x0 and it.y in w_) or
                        (it.x == x0 + w - 1 and it.y in e)):
                    it.shape, it.frame = SHAPE_BLOCKER_Y, 0


# ── Doorway skip lists (shared by both walls of each connection) ─────────
# Entry hall ↔ hub: opens x (9216, 9856] (the hub's designed north gap).
SKIP_X_ENTRY_HUB = frozenset({9344, 9472, 9600, 9728, 9856})
# Hub south gap ↔ hub-to-water corridor mouth: opens x (9472, 9984].
SKIP_X_HUB_WATER = frozenset({9600, 9728, 9856, 9984})
# Earth east / Air west doorways onto the y 5120-5631 corridors:
# opens y (5120, 5632].
SKIP_Y_SECTION_CORRIDOR = frozenset({5248, 5376, 5504, 5632})
# Hub west/east designed gaps (wider than the 512 corridors — fine, the
# corridor flank walls seal their own run): opens y (5120, 6144].
SKIP_Y_HUB_SIDE_GAPS = frozenset({5248, 5376, 5504, 5632,
                                  5760, 5888, 6016, 6144})
# Fire east ↔ Water west doorway: opens y (16384, 16896].
SKIP_Y_FIRE_WATER = frozenset({16512, 16640, 16768, 16896})
# Water south ↔ chamber north, chamber south ↔ pad north (the plugged
# quest doorway): opens x (8448, 8704].
SKIP_X_CHAMBER_DOOR = frozenset({8576, 8704})


def build_entry_hall():
    """Entry Hall — arrival from Map 9, introduction to the dungeon. The
    first worked stone the player sees after Map 9's cave."""
    items = []
    x0, y0 = 8192, 1024
    # Floor terrain (6x6 chunks)
    items.extend(generate_terrain_grid(x0, y0, 6, 6, GLOB_WORKED_FLOOR))
    # Walls — two courses of the stone pair; the south doorway x (9216,
    # 9856] lines up with the hub's north gap directly below.
    stone_room(items, x0, y0, 3072, 3072, 2, ((), SKIP_X_ENTRY_HUB, (), ()))

    # Teleport DEST (ID 202) — arrival from Map 9
    # SWAPPED 2026-07-31: the 07-25 relocation comments were written under
    # the pre-771d5c7 inverted helper names, so the ACTIVE trigger had been
    # built on the quest egress line (the playtest C1 bounce class). Ids and
    # roles unchanged; positions exchanged. See build_map_13's base pair.
    items.append(MapItem.teleporter(
        x=x0 + 1536, y=y0 + 128, z=1,
        teleport_id=202, dest_npc=202, dest_map=9
    ))
    # Teleport TRIGGER (ID 203) — return to Map 9, on a marked slab.
    # Moved 2026-07-04 (was (x0+1536, y0+256), 256 units from arrival
    # dest 202 — bounce risk per the map_walkability spacing rule).
    items.append(MapItem.placed_item(
        x=x0 + 1536, y=y0 + 128, z=1,
        shape=SHAPE_ROCK_SLAB_GROUND, frame=3, quality=0
    ))
    # (pad at y0+768, 2026-07-31: y0+512 was 64 from trigger 202's box.)
    items.append(MapItem.teleport_target(
        x=x0 + 1536, y=y0 + 768, z=0,
        teleport_id=203
    ))
    items.append(reapply_egg(x0 + 1536, y0 + 768, 0))

    # Two pairs of columns down the hall, lamps and tapestries on the two
    # faces this projection shows, urns in the corners. (Five wall reliefs
    # stood loose on the floor and two chimneys were the "columns".)
    for cy in (y0 + 1024, y0 + 2304):
        for cx in (x0 + 768, x0 + 2304):
            items.extend(column(cx, cy))
    for tx, fr in ((x0 + 768, 0), (x0 + 2304, 5)):
        items.append(MapItem.placed_item(
            x=tx, y=y0 + 1, z=0, shape=SHAPE_TAPESTRY_ON_Y_WALL, frame=fr))
    for ty, fr in ((y0 + 1536, 2), (y0 + 2560, 0)):
        items.append(MapItem.placed_item(
            x=x0 + 1, y=ty, z=0, shape=SHAPE_TAPESTRY_ON_X_WALL, frame=fr))
    for tx in (x0 + 384, x0 + 2688):
        items.append(MapItem.placed_item(
            x=tx, y=y0 + 32, z=16, shape=SHAPE_WALL_LAMP_ON_Y_WALL, frame=0))
    for ty in (y0 + 1024, y0 + 2048):
        items.append(MapItem.placed_item(
            x=x0 + 32, y=ty, z=16, shape=SHAPE_WALL_LAMP_ON_X_WALL, frame=0))
    for ux, uy in ((x0 + 64, y0 + 96), (x0 + 3008, y0 + 96),
                   (x0 + 64, y0 + 2976), (x0 + 3008, y0 + 2976)):
        items.append(MapItem.placed_item(x=ux, y=uy, z=0, shape=SHAPE_URN,
                                         frame=0))
    return items


def build_central_hub():
    """Central Hub — connects to all four elemental sections."""
    items = []
    x0, y0 = 8192, 4096
    # Floor terrain (6x6 chunks)
    items.extend(generate_terrain_grid(x0, y0, 6, 6, GLOB_WORKED_FLOOR))
    # Walls: north gap x (9216, 9856] to the entry hall; south gap
    # x (9472, 9984] where the hub-to-water corridor runs south; west and
    # east gaps y (5120, 6144] facing the earth and air corridors.
    stone_room(items, x0, y0, 3072, 3072, 2,
               (SKIP_X_ENTRY_HUB, SKIP_X_HUB_WATER,
                SKIP_Y_HUB_SIDE_GAPS, SKIP_Y_HUB_SIDE_GAPS))

    # Four columns marking the crossing, and the Earth way announced by
    # two rock spires flanking the west gap; lamps on the north and west
    # faces. (Two ground tiles at z=4 were the "Air hint", two reliefs the
    # "Fire hint", a puddle tile the "Water hint", five more reliefs the
    # lighting.)
    for cy in (y0 + 768, y0 + 2304):
        for cx in (x0 + 768, x0 + 2304):
            items.extend(column(cx, cy))
    for sy, fr in ((y0 + 896, 0), (y0 + 2176, 4)):
        items.append(MapItem.placed_item(x=x0 + 192, y=sy, z=0,
                                         shape=SHAPE_ROCK_SPIRE_CLUSTER,
                                         frame=fr))
    for tx in (x0 + 512, x0 + 2560):
        items.append(MapItem.placed_item(
            x=tx, y=y0 + 32, z=16, shape=SHAPE_WALL_LAMP_ON_Y_WALL, frame=0))
    items.append(MapItem.placed_item(
        x=x0 + 32, y=y0 + 512, z=16, shape=SHAPE_WALL_LAMP_ON_X_WALL, frame=0))
    items.append(MapItem.placed_item(
        x=x0 + 2048, y=y0 + 1, z=0, shape=SHAPE_TAPESTRY_ON_Y_WALL, frame=5))
    # The weapon cache (Douglas, 2026-10-11): an axe on the floor 380
    # units inside the north gap, where every way into the sections
    # starts. The golems' defense 0x8A strips blade and fire, so
    # Galjeron's sword (420, blade only) never hurts one; the axe's damage
    # type 0x06 keeps its blunt bit through that, halved by the golem's
    # pierce resistance (Actor::calculateAttackDamage). Of the retail
    # blunt weapons an early Avatar can carry it is the strongest (base 6,
    # mod 14; the mace is 4/11, the hammer 4/9) and keeps full blade
    # damage against everything else. Odd coordinates on the floor, clear
    # of every solid and of anything tall within 80 (map-geometry rule);
    # 8 tall, so it sorts above the flat floor at z 0.
    items.append(MapItem.placed_item(x=HUB_WEAPON[0], y=HUB_WEAPON[1],
                                     z=HUB_WEAPON[2], shape=SHAPE_AXE,
                                     frame=0))
    return items


def build_earth_section():
    """Earth Section — caves, rock formations, earth talisman."""
    items = []
    x0, y0 = 1024, 1024
    # Floor terrain (10x10 chunks)
    items.extend(generate_terrain_grid(x0, y0, 10, 10, GLOB_EARTH_FLOOR))
    # Outer walls
    wall_run_e(items, x0, y0, 5120)
    wall_run_e(items, x0, y0 + 5119, 5120)
    wall_run_s(items, x0, y0, 5120)
    # East wall — doorway y (5120, 5632] facing the earth-to-hub corridor
    # (which faces the hub's west gap).
    wall_run_s(items, x0 + 5119, y0, 5120, skip=SKIP_Y_SECTION_CORRIDOR)
    # Interior cave walls — creating narrow passages (rooms connect
    # around both wall ends; neither strands the talisman or the door)
    # Passage 1: horizontal wall dividing north area, x (1408, 3456]
    wall_run_e(items, x0 + 384, y0 + 1536, 2048)
    # Passage 2: vertical wall creating a maze element, y (2944, 4480]
    wall_run_s(items, x0 + 2560, y0 + 1920, 1536)
    # No ceiling (67 squares floated here at z=40).

    # Rock formations scattered throughout
    rock_positions = [
        (x0+400, y0+400), (x0+1200, y0+600), (x0+2000, y0+300),
        (x0+3200, y0+800), (x0+4000, y0+500), (x0+800, y0+2000),
        (x0+1600, y0+2500), (x0+3000, y0+2200), (x0+4200, y0+2800),
        (x0+600, y0+3600), (x0+1800, y0+3800), (x0+3400, y0+3400),
        (x0+2400, y0+4200), (x0+4600, y0+4000), (x0+1000, y0+4500),
        (x0+3800, y0+1200), (x0+2200, y0+1000), (x0+4400, y0+1600),
        (x0+700, y0+1400), (x0+2800, y0+3000)
    ]
    rock_shape_frames = [(SHAPE_ROCK_SPIRE_CLUSTER, 0), (SHAPE_ROCK_SLAB_GROUND, 0),
                         (SHAPE_BOULDER_PILE, 0), (SHAPE_CLIFF_FACE_DETAIL, 3)]
    for i, (rx, ry) in enumerate(rock_positions):
        shape, frame = rock_shape_frames[i % 4]
        items.append(MapItem.placed_item(x=rx, y=ry, z=0, shape=shape, frame=frame))
    # More of the cave: boulders and rubble at the walls' feet, bones from
    # what lives here, fungus in the corners. The north boulder is at
    # x0 + 1568, not 1536: there its 56-unit top reached 8 units into the
    # stalactite hung at (x0 + 1500, y0 + 224) from z 48 (found 2026-10-07;
    # retail embeds none of its 38 boulders in a solid).
    for bx, by, fr in ((x0 + 224, y0 + 2880, 0), (x0 + 4896, y0 + 3520, 1),
                       (x0 + 3456, y0 + 4896, 2), (x0 + 1568, y0 + 224, 3)):
        items.append(MapItem.placed_item(x=bx, y=by, z=0,
                                         shape=SHAPE_BOULDER_LARGE, frame=fr))
    for rx, ry, fr in ((x0 + 255, y0 + 4991, 0), (x0 + 4991, y0 + 255, 3),
                       (x0 + 2687, y0 + 2687, 6), (x0 + 4223, y0 + 3711, 1)):
        items.append(MapItem.placed_item(x=rx, y=ry, z=0,
                                         shape=SHAPE_BOULDER_PILE, frame=fr))
    for mx, my, fr in ((x0 + 160, y0 + 704, 2), (x0 + 4960, y0 + 4800, 9),
                       (x0 + 3000, y0 + 4700, 14)):
        items.append(MapItem.placed_item(x=mx, y=my, z=0,
                                         shape=SHAPE_MUSHROOM_CLUSTER, frame=fr))
    items.append(MapItem.placed_item(x=x0 + 3600, y=y0 + 1400, z=0,
                                     shape=SHAPE_BONES_A, frame=0))
    items.append(MapItem.placed_item(x=x0 + 1400, y=y0 + 3500, z=0,
                                     shape=SHAPE_BONES_B, frame=1))
    # Stalactites hang from the wall line, points ending above the Avatar.
    for sx, sy in [(x0+224, y0+800), (x0+1500, y0+224), (x0+4960, y0+1800),
                   (x0+4000, y0+4960), (x0+224, y0+4000), (x0+2600, y0+224)]:
        items.append(MapItem.placed_item(x=sx, y=sy, z=CAVE_COURSE,
                                         shape=SHAPE_STALACTITE,
                                         frame=(sx // 32) % 3))
    # MONSTERS (2026-10-11). A shape-500 egg never hatches on its own; a
    # MONEGG trigger hatches its group (lv_monster_eggs). The heavy hitters
    # stand 920+ units (x or y, from their boxes) off the shortest walk
    # door -> talisman -> door, outside the +/-768 square in which a
    # combat-activity monster picks a target (CombatProcess::seekTarget):
    # the section's caves are theirs, the talisman's way is not, unless
    # the player wanders. Each has a trigger of its own between it and
    # the walk, 512-544 units short of it, wholly inside its seek square,
    # so it hatches inside the fast area and comes at once
    # (lv_monster_eggs.wakes_at_once, hatch_fast_problem). Until
    # 2026-10-11 one trigger across the section doorway hatched them all,
    # 2,656-3,392 away, outside the fast area: Item::enterFastArea cleared
    # their combat when the Avatar came near, and they stood beside him
    # (playtest-2026-10-11-monsters2 finding 1). No trigger on the way
    # could serve: at 320x200 the fast area reaches about three chunks
    # from the camera, and a monster out of sight loiters +/- 320 round
    # its egg, so a golem off the walk's seek square has no spot both in
    # the fast area and out of the walk's reach.
    # Groups 1, 5, 6, 7: four golems (214, 150-175 hp, 15-25 a blow,
    # immune to blades) in the north caves. Two of the old four stood
    # inside rocks (235, 237).
    # Golems 1 and 7 are the north-west pocket's, north of Passage 1 (the
    # wall at y (2528, 2560], x 1408-3456). Both triggers are north of it
    # too, on the way in from the pocket's open east side, and the golem's
    # walk from its egg to any spot in its box is a straight one
    # (test_monster_eggs: the walk-distance check). Until 2026-10-12
    # trigger 7 stood south of the wall and trigger 1's box straddled its
    # east end, so both golems hatched fighting and milled behind the wall
    # (playtest-2026-10-12-monsters3 finding 1). Golem 1 also moved from
    # (3040, 2048) to below the rock spire at (3224, 2024), which stood
    # across its way east.
    for group, trigger, box, egg in (
            (1, (3584, 2240), (5, 5), (3040, 2240)),
            (5, (4608, 2592), (5, 5), (4608, 2048)),
            (6, (5376, 3264), (5, 5), (5376, 2720)),
            (7, (3200, 2208), (3, 3), (2688, 2496))):
        items.extend(monster_group(group, trigger=trigger + (0,), box=box,
                                   eggs=[egg + (0, SHAPE_MON_EARTH)]))
    # Talisman of Earth — deepest chamber (SW corner)
    items.append(MapItem.placed_item(
        # ODD coordinates, deliberately. GlobEgg::enterFastArea lays a
        # glob's contents at (_x & ~0x1FF) + 2*gx + 1, so every tile a
        # glob supplies has an odd origin and the glob's floor stops at
        # ...2047 / ...5631. An item on the next even coordinate is one
        # unit past the last tile, has no support, and falls out of the
        # world on load -- which silently ate three of the four talismans
        # and made step 4 uncompletable. Sit them on the glob's own cell.
        # z=4, not 0. A talisman resting at z=0 on the glob tile it
        # shares an origin with ties that tile in the sort order and
        # loses: it is drawn under the floor and TraceObjId never
        # returns it, so the player cannot click it. Frames 0/2/3 of
        # shape 596 are 5x7 and 5x4 sprites, far too small to survive
        # that; only frame 1 (11x14) ever showed through. Four units
        # of height breaks the tie -- verified in ScummVM 2026-09-06.
        x=x0 + 1023, y=y0 + 4607, z=4,
        shape=SHAPE_TALISMAN, frame=0, quality=101  # Earth talisman quality
    ))
    # Its alcove: two spires north-east of the talisman. The eastern one
    # stays north of the quest band so its face leaves the Avatar visible.
    items.append(MapItem.placed_item(x=x0 + 1407, y=y0 + 3967, z=0,
                                     shape=SHAPE_ROCK_SPIRE_CLUSTER, frame=8))
    items.append(MapItem.placed_item(x=x0 + 1023, y=y0 + 4223, z=0,
                                     shape=SHAPE_ROCK_SPIRE_CLUSTER, frame=4))
    return items


def build_air_section():
    """Air Section — the Plane of Air's idiom (Map 46): rock rising out
    of nothing, spires hanging in the dark, terraces stepping up. The
    talisman stays where the 2026-07-04 grounding put it."""
    items = []
    x0, y0 = 14336, 1024
    # Base floor terrain (10x10 chunks)
    items.extend(generate_terrain_grid(x0, y0, 10, 10, GLOB_AIR_FLOOR))
    # Outer walls
    wall_run_e(items, x0, y0, 5120)
    wall_run_e(items, x0, y0 + 5119, 5120)
    # West wall — doorway y (5120, 5632] facing the air-to-hub corridor.
    wall_run_s(items, x0, y0, 5120, skip=SKIP_Y_SECTION_CORRIDOR)
    wall_run_s(items, x0 + 5119, y0, 5120)
    # No ceiling (fifty squares floated here at z=120).

    # Two unequal ledges have broken shoulders and 8-unit risers. Their
    # 24-unit summits retain the original walking-height limit. The final
    # dressing pass gives each occupied cell its drop-facing rock crest.
    def terrace(kx, ky, tiers):
        out = []
        for tier, rows in enumerate(tiers):
            for row, lo, hi in rows:
                for col in range(lo, hi + 1):
                    out.append(MapItem.placed_item(
                        floor_grid(x0, kx + col), floor_grid(y0, ky + row),
                        tier * TIER, SHAPE_PLATFORM_FLAGSTONE, 0))
        return out
    # Each upper tier has a complete lower shoulder, including diagonal
    # stumble landings. Unequal low lobes break the two rock outlines.
    items.extend(terrace(8, 8, (
        ((-1,1,2),(0,0,4),(1,0,4),(2,-1,4),(3,-1,4),(4,0,4)),
        ((1,1,3),(2,1,3),(3,1,3)), ((2,2,2),))))
    items.extend(terrace(24, 20, (
        ((0,0,4),(1,0,5),(2,0,5),(3,0,4),(4,0,4),(5,1,2)),
        ((1,1,3),(2,1,3),(3,1,3)), ((2,2,2),))))

    # Spires hanging in the air, the plane's signature, well above the
    # Avatar; rock spires and boulders on the floor between the terraces.
    for sx, sy, sz in ((x0 + 1024, y0 + 3840, 64), (x0 + 3968, y0 + 1152, 80),
                       (x0 + 2560, y0 + 2560, 72), (x0 + 4480, y0 + 4480, 64),
                       (x0 + 640, y0 + 640, 80), (x0 + 3072, y0 + 4736, 88)):
        items.append(MapItem.placed_item(x=sx, y=sy, z=sz,
                                         shape=SHAPE_STALACTITE,
                                         frame=(sx // 32) % 3))
    for sx, sy, fr in ((x0 + 640, y0 + 2176, 0), (x0 + 4480, y0 + 640, 4),
                       (x0 + 2304, y0 + 4608, 8), (x0 + 4736, y0 + 3072, 1)):
        items.append(MapItem.placed_item(x=sx, y=sy, z=0,
                                         shape=SHAPE_ROCK_SPIRE_CLUSTER,
                                         frame=fr))
    for bx, by, fr in ((x0 + 1600, y0 + 4400, 0), (x0 + 3400, y0 + 800, 2),
                       (x0 + 4300, y0 + 2600, 3)):
        items.append(MapItem.placed_item(x=bx, y=by, z=0,
                                         shape=SHAPE_BOULDER_LARGE, frame=fr))

    # Groups 2, 8, 9: three seekers (509) on the north floor, 1,840-2,360
    # units from the walk doorway -> talisman, each hatched by a trigger
    # of its own 544 short of it toward the walk, as the Earth section's
    # golems are (see there). They floated at z 40/64/80 where the old
    # platforms were, over nothing; until 2026-10-11 one trigger across
    # the west doorway hatched all three outside the fast area, passive.
    for group, trigger, egg in ((2, (16384, 2592), (16384, 2048)),
                                (8, (17408, 2592), (17408, 2048)),
                                (9, (17792, 3360), (17792, 2816))):
        items.extend(monster_group(group, trigger=trigger + (0,), box=(5, 5),
                                   eggs=[egg + (0, SHAPE_MON_AIR)]))
    # Talisman of Air — GROUNDED 2026-07-04. The original placement
    # (x0+2816, z=100) floated in the 384-unit gap BETWEEN the two z=100
    # platform tiles (x0+2560 and x0+3072): unreachable, and the debug
    # teleport beside it dropped the avatar out of midair. It sits on the
    # floor, a pinned position; a terrace to carry it belongs with the
    # gameplay pass.
    items.append(MapItem.placed_item(
        x=x0 + 2816, y=y0 + 4096, z=0,
        shape=SHAPE_TALISMAN, frame=1, quality=102  # Air talisman quality
    ))
    return items


def build_fire_section():
    """Fire Section — the Plane of Fire's idiom (Map 44): dark rock
    causeways through lava. The lava and flame are hazards BESIDE the
    way; test_route_reach proves the way itself never stands on one."""
    items = []
    x0, y0 = 1024, 14336
    # Floor: scorched earth, with lava lakes as whole chunks in the four
    # quadrants. The lakes are HAZARDS, as the pits and flames below are:
    # shape 409 carries no SI_DAMAGING, but its class CLRLAVA burns
    # anything that touches it, 2-4 hp a contact, and its frame-33 tiles
    # (four of each lake's sixteen) kill outright. Until 2026-10-10 this
    # comment called them "walkable and harmless", and the south-east
    # quadrant held three of them, at (7,7), (8,6) and (8,7) — (8,6) and (8,7)
    # straight across the line from the Fire talisman to the only doorway
    # out. A run walking it died (playtest-2026-10-10-full-run-part5
    # finding 1). That quadrant's lakes now stand west of x 5120, so the
    # talisman's corner and the walk north-east to the doorway are clear
    # ground; test_route_reach measures LAVA_MARGIN on the lines a player
    # walks from the talisman, against the built map.
    #
    # Build 7 (playtest-2026-10-11-build7 L1) walked on north from the
    # talisman past the doorway's latitude and lost 2 hp to a FIREPIT at
    # (x0+4608, y0+2048). The column north of the talisman, x 5264 to the
    # east wall, held that pit, the lake (8,2), a second pit at (x0+4608,
    # y0+1024) and a flame at (x0+4352, y0+2176). The lake is now (6,2)
    # and the other three stand west of x 4610 (marked "moved" below), so
    # a walk held north from the talisman reaches the north wall unburnt.
    #
    # 2026-10-17: the north-west quadrant is rock round the 1994 screen05
    # torture pocket (place_screen05, SCREEN05_MASK). Its lakes (1,1),
    # (2,1) and (1,2), the pools (x0+1024, y0+1024), (x0+2048, y0+512) and
    # (x0+2048, y0+1536), the flames (x0+768, y0+768) and (x0+2176, y0+768)
    # and the spire (x0+640, y0+1664) stood in that rock or in the shot's
    # frame, which shows none of them, and are gone.
    LAKES = {(7, 1), (6, 2), (2, 6), (2, 7), (7, 7), (7, 6), (6, 7)}
    for cx in range(10):
        for cy in range(10):
            items.extend(generate_terrain_grid(
                x0 + cx * 512, y0 + cy * 512, 1, 1,
                GLOB_LAVA_LAKE if (cx, cy) in LAKES else GLOB_FIRE_FLOOR))
    # Outer walls
    wall_run_e(items, x0, y0, 5120)
    wall_run_e(items, x0, y0 + 5119, 5120)
    wall_run_s(items, x0, y0, 5120)
    # East wall — doorway y (16384, 16896], aligned with the water
    # section's west-wall doorway across the x=6143/6144 seam.
    wall_run_s(items, x0 + 5119, y0, 5120, skip=SKIP_Y_FIRE_WATER)
    # No ceiling (a hundred squares at z=32 — below head height).

    # THE CAUSEWAYS: dark raised paving, three tiles wide, one step up.
    # An east-west spine at rows 19..21 (y 16640..17023) from the west
    # wall to the Water doorway, a north-south spine at columns 19..21
    # (x 3328..3711) the full depth, and a branch along row 35 (y
    # 18688..18815) east to the talisman's corner. (Before: single ground
    # tiles at z=2 every 256 units — a dotted line.)
    def run(kx0, kx1, ky0, ky1):
        xs = [floor_grid(x0, k) for k in range(kx0, kx1 + 1)]
        ys = [floor_grid(y0, k) for k in range(ky0, ky1 + 1)]
        return raised_platform(xs, ys, z=0, shape=SHAPE_PAVING_RAISED,
                               frames=DARK_PAVING)
    # The east-west spine skips column 17: the pinned Fire monster egg at
    # (3072, 16896) sits in that tile, and a spawn inside a raised tile
    # is a stuck creature. A rubble patch marks the break.
    items.extend(run(1, 16, 19, 21))
    items.extend(run(18, 40, 19, 21))
    items.extend(MapItem.placed_item(x=floor_grid(x0, 17), y=floor_grid(y0, 20),
                                     z=0, shape=SHAPE_BOULDER_PILE, frame=5)
                 for _ in (0,))
    items.extend(run(19, 21, 1, 40))
    items.extend(run(22, 34, 34, 36))
    # Lava pools in the quadrants, none under a causeway (checked below),
    # flame tiles at their margins. UNDER_NW_ROCK: the ones the screen05
    # rock took (see LAKES above).
    UNDER_NW_ROCK = {(x0+1024, y0+1024), (x0+2048, y0+512), (x0+2048, y0+1536),
                     (x0+768, y0+768), (x0+2176, y0+768)}
    lava_positions = [p for p in (
        (x0+1024, y0+1024), (x0+2048, y0+512), (x0+3584, y0+2048),  # moved
        (x0+1536, y0+3072), (x0+3840, y0+3584), (x0+512, y0+4096),
        (x0+2048, y0+1536), (x0+3072, y0+1024), (x0+1024, y0+4608),  # moved
    ) if p not in UNDER_NW_ROCK]
    for lx, ly in lava_positions:
        items.append(MapItem.placed_item(x=lx, y=ly, z=0, shape=SHAPE_LAVA_POOL, frame=0))
    # The south-east quadrant's pool and its flame tile moved with its
    # lakes (2026-10-10): the pool from (x0+4352, y0+3840), the flame from
    # (x0+4352, y0+3072), both on the talisman's line to the doorway.
    # Each flame keeps the shape its place in this list gave it.
    flames = [((fx, fy), [SHAPE_TRAP_BURST_A, SHAPE_TRAP_BURST_B,
                          SHAPE_TRAP_BURST_C][i % 3])
              for i, (fx, fy) in enumerate((
                  (x0+768, y0+768), (x0+2176, y0+768), (x0+4096, y0+1280),
                  (x0+1280, y0+2176), (x0+2816, y0+2816), (x0+3328, y0+2176),  # moved
                  (x0+768, y0+3328), (x0+3328, y0+4096), (x0+1792, y0+3840),
                  (x0+3584, y0+3328), (x0+2176, y0+4864), (x0+3840, y0+4864),
              )) if (fx, fy) not in UNDER_NW_ROCK]
    flame_positions = [p for p, _ in flames]
    for (fx, fy), shape in flames:
        items.append(MapItem.placed_item(x=fx, y=fy, z=0, shape=shape, frame=0))
    # Rock spires rising out of the lava, boulders on the shore.
    for sx, sy, fr in ((x0 + 4864, y0 + 2944, 4),
                       (x0 + 1920, y0 + 4224, 8), (x0 + 4224, y0 + 640, 1)):
        items.append(MapItem.placed_item(x=sx, y=sy, z=0,
                                         shape=SHAPE_ROCK_SPIRE_CLUSTER,
                                         frame=fr))
    for bx, by, fr in ((x0 + 3072, y0 + 3200, 1), (x0 + 1152, y0 + 2176, 3)):
        items.append(MapItem.placed_item(x=bx, y=by, z=0,
                                         shape=SHAPE_BOULDER_LARGE, frame=fr))
    # Groups 3, 10-13: five daemons (96, 80-100 hp, 12-18 fire a blow) in
    # the section's west half, 32+ units clear of every lava tile and
    # flame, 1,960-3,920 units from the walk doorway -> talisman ->
    # doorway, so only a player who goes west, over the lava field or
    # down the north-south causeway, meets them. Each has a trigger of
    # its own 544-704 short of it toward the walk, as the Earth section's
    # golems do (see there), where no blow can stumble the Avatar into
    # lava (test_monster_eggs' knockback check: groups 3 and 13 moved for
    # it, the first daemon from (2720,14848), between a lake and a pool);
    # until 2026-10-11 one trigger across the doorway from the Water
    # section hatched all five outside the fast area, passive. Four of
    # the old five touched lava (409) or a fire pit (318); the fifth stood
    # inside a paving step. Group 3 moved on 2026-10-17 for screen05: the
    # egg 32 east, from (2848, 15104), where the daemon's body, stepped
    # the 32 an egg spot must allow, came within 25 of the shot's fire
    # field 400 by the rack, inside the 32 a body keeps from a burning
    # shape; the trigger from (3392, 14592) to the causeway at the
    # pocket's mouth, because the pocket now opens only east (rows
    # 117-118) and the walk from the egg round to the old box's north end
    # was 1.39 x the line (test_monster_eggs).
    for group, trigger, egg in ((3, (3520, 15104), (2880, 15104)),
                                (10, (3808, 15872), (3264, 15872)),
                                (11, (3296, 17408), (2752, 17408)),
                                (12, (3808, 18816), (3264, 18816)),
                                (13, (3232, 18368), (2688, 19072))):
        items.extend(monster_group(group, trigger=trigger + (0,), box=(5, 5),
                                   eggs=[egg + (0, SHAPE_MON_FIRE)]))
    # Talisman of Fire in the deepest chamber, at the end of the branch
    # causeway, on the floor.
    items.append(MapItem.placed_item(
        # Odd coordinate: on the glob's floor, not one unit past it.
        # z=4: clears the floor tile in the sort order (see Earth above).
        x=x0 + 4607, y=y0 + 4607, z=4,
        shape=SHAPE_TALISMAN, frame=2, quality=103  # Fire talisman quality
    ))
    # The lava must stay off the causeways: a pool or a lake under a
    # paving tile would be a hazard the flood cannot see. Checked at build
    # time.
    paving = [(it.x, it.y) for it in items if it.shape == SHAPE_PAVING_RAISED]
    hazards = [(lx, ly, 256) for lx, ly in lava_positions] + \
              [(fx, fy, 128) for fx, fy in flame_positions]
    for hx, hy, hd in hazards:
        for px, py in paving:
            assert not (hx - hd < px <= hx + 127 and hy - hd < py <= hy + 127), \
                f'hazard at ({hx},{hy}) under causeway tile ({px},{py})'
    for cx, cy in LAKES:
        lx, ly = x0 + cx * 512, y0 + cy * 512       # tiles cover (l, l+511]
        for px, py in paving:
            assert not (px - 128 < lx + 511 and lx < px and
                        py - 128 < ly + 511 and ly < py), \
                f'lava lake chunk {(cx, cy)} under causeway tile ({px},{py})'
    return items


def build_water_section():
    """Water section with navy decorative pools around four dry islands."""
    items = []
    x0, y0 = 6144, 14336
    # Base floor terrain (16x10 chunks — wider to bridge fire and air)
    items.extend(generate_terrain_grid(x0, y0, 16, 10, GLOB_WATER_FLOOR))
    # Outer walls
    # North wall — doorway x (9472, 9984] where the hub-to-water corridor
    # arrives from the north.
    wall_run_e(items, x0, y0, 8192, skip=SKIP_X_HUB_WATER)
    # South wall — doorway x (8448, 8704], aligned with the Four Pillars
    # chamber's north-wall doorway across the y=19455/19456 seam.
    wall_run_e(items, x0, y0 + 5119, 8192, skip=SKIP_X_CHAMBER_DOOR)
    # West wall — doorway y (16384, 16896] to the fire section.
    wall_run_s(items, x0, y0, 5120, skip=SKIP_Y_FIRE_WATER)
    wall_run_s(items, x0 + 8191, y0, 5120)
    # Close the Water bay's visible corner notch; the outer rim post stays.
    items.append(MapItem.placed_item(14335, 14336, 0, 29, 0))
    # Navy paint carries donor 202's decorative physics. The original
    # flagstone globs remain the support, and the barriers stay unchanged.
    # Rounded, bounded pools surround the four three-by-three dry islands.
    for kx, ky in ((12, 12), (40, 16), (26, 30), (48, 32)):
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if abs(dx) + abs(dy) > 4 or (abs(dx) <= 1 and abs(dy) <= 1):
                    continue
                items.append(MapItem.placed_item(
                    floor_grid(x0, kx + 1 + dx),
                    floor_grid(y0, ky + 1 + dy), 0,
                    SHAPE_DECORATIVE_WATER, 0))

    # Islands — 3x3 raised flagstone, one step, four of them, the last
    # beside the talisman's corner and clear of its cell. (Before: two
    # "islands" of single tiles 512 apart.)
    for kx, ky in ((12, 12), (40, 16), (26, 30), (48, 32)):
        xs = [floor_grid(x0, k) for k in range(kx, kx + 3)]
        ys = [floor_grid(y0, k) for k in range(ky, ky + 3)]
        items.extend(raised_platform(xs, ys, z=0))
    # Fungus, boulders, stalagmite spires in the damp.
    for mx, my, fr in ((x0 + 800, y0 + 900, 3), (x0 + 3400, y0 + 4200, 7),
                       (x0 + 6200, y0 + 1300, 11), (x0 + 7600, y0 + 3900, 15),
                       (x0 + 4700, y0 + 2600, 19), (x0 + 1500, y0 + 3400, 22)):
        items.append(MapItem.placed_item(x=mx, y=my, z=0,
                                         shape=SHAPE_MUSHROOM_CLUSTER, frame=fr))
    # The southern boulder stays north of the Water-talisman quest band.
    for bx, by, fr in ((x0 + 2600, y0 + 700, 0), (x0 + 5900, y0 + 3932, 2),
                       (x0 + 7800, y0 + 600, 1), (x0 + 400, y0 + 4800, 3)):
        items.append(MapItem.placed_item(x=bx, y=by, z=0,
                                         shape=SHAPE_BOULDER_LARGE, frame=fr))
    for sx, sy, fr in ((x0 + 1792, y0 + 2176, 0), (x0 + 5504, y0 + 1152, 4),
                       (x0 + 7040, y0 + 2944, 8)):
        items.append(MapItem.placed_item(x=sx, y=sy, z=0,
                                         shape=SHAPE_ROCK_SPIRE_CLUSTER,
                                         frame=fr))
    # Group 4: five small lizards (806, 2-7 hp), vermin, in the section's
    # north-east bay, the corner off every quest line. The trigger is a
    # retail strip across the bay's way in from the west, +/-32 x 480 at
    # x 13056: Avatar reference points x 13024-13151, y 14400-15423, from
    # the north wall (the Avatar's least y there is 14400) down. The
    # lizards stand 448-736 east of it, every one inside the 320x200 fast
    # area and seeing the Avatar at once from every position that fires it
    # (lv_monster_eggs.wakes_at_once, hatch_fast_problem).
    # MOVED 2026-10-24 (playtest-2026-10-17-replay-leg3 finding 4; Douglas:
    # not deliberate). The trigger stood at (9728,14528), +/-288 x 64,
    # across the mouth of the corridor from the hub, the one way into the
    # south half, and its eggs flanked that mouth, (9024,14400) to
    # (11424,15520): every player hatched them on the way to the Fire,
    # Water and pillars, and four took hp 30 -> 18. With those eggs no
    # trigger off the mouth hatched them all inside the fast area, so the
    # group moved whole. The strip now lies 2,144 or more off the straight
    # line between any two of the corridor's mouth, the Fire doorway, the
    # Water talisman and the pillars chamber's doorway (a walk through it
    # is 1,486 or more longer than the line), and test_monster_eggs pins
    # it off the mouth and the lines. A player who comes up the east wall
    # from the Water talisman enters the bay without crossing the strip.
    # Until 2026-10-11 four of the five stood across the section, 2,560-
    # 3,392 off the trigger, and hatched passive
    # (playtest-2026-10-11-monsters2 finding 1).
    items.extend(monster_group(
        4, trigger=(13056, 14880, 0), box=(1, 15),
        eggs=[(13504, 14688, 0, SHAPE_MON_WATER),
              (13792, 14688, 0, SHAPE_MON_WATER),
              (13632, 14944, 0, SHAPE_MON_WATER),
              (13504, 15200, 0, SHAPE_MON_WATER),
              (13792, 15200, 0, SHAPE_MON_WATER)]))
    # Talisman of Water on the talisman island (SE area)
    items.append(MapItem.placed_item(
        # Odd coordinate: on the glob's floor, not one unit past it.
        x=x0 + 6655, y=y0 + 4607, z=4,
        shape=SHAPE_TALISMAN, frame=3, quality=104  # Water talisman quality
    ))
    return items


# The Fire receptacle's spot (max corner). MOVED 2026-10-17 from (7680,
# 21760), 256 south of its pillar, where it painted 899 px of the 1994
# screen07 frame (the rubble mound). Here it is 255 east and 255 south of
# the pillar, the nearest spot SE of it whose sprite stays out of the
# frame, and its search box (footpad 48 grown by 300) still holds the Fire
# pillar's origin and no other (test_art_props). The vignette's candle post
# 453:6 beside the pillar was the other candidate: it would have been the
# one receptacle of the four that is not a socket, so a player who had
# learnt three sockets would look for a fourth.
FIRE_RECEPTACLE = (7935, 21759)


def build_four_pillars():
    """Four Pillars Chamber — exit area with elemental pillars.

    A CAVE since 2026-10-17: the 1994 screen07 shows the Pillar of Fire in
    cave rock, so the chamber's floor is the cave rock glob, its north,
    west and east stone walls are gone (the Water section's south wall and
    the map rim close it; the rock inside is place_screen07's mask), and
    only the south gate line stays masonry, as the gate hardening below
    needs."""
    items = []
    x0, y0 = 6144, 19456
    # Floor terrain (8x6 chunks)
    items.extend(generate_terrain_grid(x0, y0, 8, 6, GLOB_CHAMBER_FLOOR))
    # South doorway x (8448, 8704] to the Teleporter Pad room, plugged with
    # sealing boulders until the pillar puzzle completes. (The north
    # doorway, x (8448, 8704], is the Water section's.)
    # ── GATE HARDENING (2026-07-31, playtest test B) ────────────────────
    # The 2026-07-31 in-engine playtest walked OVER this south wall with
    # both sealing boulders intact: the engine auto-tries climb72..climb16
    # on jump (u8_avatar_mover_process.cpp), the wall was one course
    # (48 tall) with a bare standable top. Repro was (8328,22494,0) →
    # jump → on the wall top at z=48 → walk the top → drop into the pad
    # room → trigger 205 → Map 10, four pillars standing.
    #
    # Three courses of the 40-tall stone piece make the south line 120
    # tall (was three of the 48-tall cave piece, 144): climb72 from the
    # floor reaches nothing — the stack is continuous — and nothing within
    # a climb's reach of the gate line tops 40, so there is no ledge to
    # chain from. The pillars themselves top 80 since 2026-09-24 (custom
    # art 865, footpad z=10), and that is fine because they stand 1023
    # units from the line (their receptacles 767); test_route_reach.py
    # asserts the reach rule, so a taller standable placed NEAR the wall
    # fails the estate before any playtest. No column stands in this
    # room for the same reason. The courses
    # run CONTINUOUS across the doorway — a lintel over x (8448,8704] from
    # z=40 up — which the walking route never notices: the doorway below
    # stays 0..40 open (boulders 0..40 until the puzzle destroys them,
    # Avatar box 0..40 after). Since 2026-10-17 this line is the room's
    # only stone: three courses on their own, without stone_room.
    for z in (0, 40, 80):
        first = len(items)
        wall_run_e(items, x0, y0 + 3071, 4096, frame=WALL_PLAIN, z=z,
                   shape=WALL_EW, skip=SKIP_X_CHAMBER_DOOR if z == 0 else ())
        if z:
            for it in items[first:]:
                if it.x in SKIP_X_CHAMBER_DOOR:
                    it.shape, it.frame = SHAPE_BLOCKER_X, 0
    # No ceiling (48 squares floated here at z=56).

    # Four Elemental Pillars — arranged in a 2x2 grid in the center; the
    # receptacle beside each. (Each stood on a 3x3 square of 301 slabs off
    # the floor lattice until 2026-10-17; the floor is 301 now.)
    pillar_center_x = x0 + 2048
    pillar_center_y = y0 + 1536

    # Pillar of Earth (NW)
    items.append(MapItem.placed_item(
        x=pillar_center_x - 512, y=pillar_center_y - 512, z=0,
        shape=SHAPE_PILLAR, frame=0, quality=201  # Earth pillar quality
    ))
    items.append(MapItem(
        x=pillar_center_x - 512, y=pillar_center_y - 256, z=0,
        shape=SHAPE_RECEPTACLE, frame=0, quality=201,  # Earth receptacle
        npcnum=RECEPTACLE_NPCNUM
    ))
    # Pillar of Air (NE)
    items.append(MapItem.placed_item(
        x=pillar_center_x + 512, y=pillar_center_y - 512, z=0,
        shape=SHAPE_PILLAR, frame=1, quality=202  # Air pillar quality
    ))
    items.append(MapItem(
        x=pillar_center_x + 512, y=pillar_center_y - 256, z=0,
        shape=SHAPE_RECEPTACLE, frame=0, quality=202,  # Air receptacle
        npcnum=RECEPTACLE_NPCNUM
    ))
    # Pillar of Fire (SW)
    items.append(MapItem.placed_item(
        x=pillar_center_x - 512, y=pillar_center_y + 512, z=0,
        shape=SHAPE_PILLAR, frame=2, quality=203  # Fire pillar quality
    ))
    items.append(MapItem(
        x=FIRE_RECEPTACLE[0], y=FIRE_RECEPTACLE[1], z=0,
        shape=SHAPE_RECEPTACLE, frame=0, quality=203,  # Fire receptacle
        npcnum=RECEPTACLE_NPCNUM
    ))
    # Pillar of Water (SE)
    items.append(MapItem.placed_item(
        x=pillar_center_x + 512, y=pillar_center_y + 512, z=0,
        shape=SHAPE_PILLAR, frame=3, quality=204  # Water pillar quality
    ))
    items.append(MapItem(
        x=pillar_center_x + 512, y=pillar_center_y + 768, z=0,
        shape=SHAPE_RECEPTACLE, frame=0, quality=204,  # Water receptacle
        npcnum=RECEPTACLE_NPCNUM
    ))
    # Sealing boulders plugging the carved doorway x (8448, 8704] in the
    # south wall. Max-corner origins (8576, 22528) and (8704, 22528):
    # each 128×128×40 solid box covers (8448,8576] and (8576,8704], so
    # the two together seal the doorway span exactly, spanning both wall
    # bands (chamber y=22527, pad y=22528). TypeReceptacle::use()
    # destroys quality-299 shape-66 items when all four pillars are down
    # ("The way to the Lost Vale is open!").
    items.append(MapItem.placed_item(
        x=8576, y=22528, z=0,
        shape=SHAPE_SEALING_BOULDER, frame=0, quality=SEALING_BOULDER_QUALITY
    ))
    items.append(MapItem.placed_item(
        x=8704, y=22528, z=0,
        shape=SHAPE_SEALING_BOULDER, frame=0, quality=SEALING_BOULDER_QUALITY
    ))
    return items


def build_teleporter_pad():
    """Teleporter Pad — exit to Map 10 (Lost Vale)."""
    items = []
    x0, y0 = 8192, 22528
    # Floor terrain (2x2 chunks)
    items.extend(generate_terrain_grid(x0, y0, 2, 2, GLOB_WORKED_FLOOR))
    # Walls — worked stone, three courses all round (the 2026-07-31 gate
    # hardening, see build_four_pillars: 120 tall, continuous, no ledge).
    # North doorway x (8448, 8704] on the ground course only; the courses
    # above run over it as a lintel the boulders (0..40) and, after the
    # puzzle, the walking Avatar (0..40) pass under untouched.
    stone_room(items, x0, y0, 1024, 1024, 3, (SKIP_X_CHAMBER_DOOR, (), (), ()))
    # No ceiling (four squares at z=40).

    # Teleport pair to Map 10 (Lost Vale). MOVED 2026-07-04:
    # the original spot (x0+512, y0+512) sat directly between the return
    # arrival (dest 205) and the room's only doorway, so anyone coming
    # BACK from the Vale re-triggered it on their way out (the same
    # point-trap bounce as Map 10's trigger 205). The active trigger now
    # stands in the room's SE corner, clear of the doorway line.
    # SWAPPED 2026-07-31: the 07-25 relocation comments were written under
    # the pre-771d5c7 inverted helper names, so the ACTIVE trigger had been
    # built on the quest egress line (the playtest C1 bounce class). Ids and
    # roles unchanged; positions exchanged. See build_map_13's base pair.
    # MOVED 2026-10-10 from (x0+256, y0+512) into the room's NW corner.
    # He arrives from Map 10's court heading W or NW, and trigger 205's box
    # (npcNum 0xCD: x +/-384, y +/-416) covers the room's south-east 60%.
    # From the old spot a held key ran to the west wall, slid along it
    # (the engine retries a refused step 45 degrees, and a keyboard hold
    # then faces the slide) and wall-followed the room into that box in
    # 1.3-2.9 s (test_route_reach.arrival_corridors). In the corner west,
    # north-west and north are all wall: every held input stops where he
    # lands. Every spot in x 8259..8323, y 22619..22639 holds; this is
    # (8291,22639). The doorway is 160 east along the north wall.
    items.append(MapItem.teleport_target(
        x=x0 + 99, y=y0 + 111, z=0,
        teleport_id=204
    ))
    items.append(reapply_egg(x0 + 99, y0 + 111, 0))
    # Teleport DEST (ID 205) — return from Map 10, NW of the room with a
    # clear straight line to the doorway at x (8448,8704].
    items.append(MapItem.teleporter(
        x=x0 + 768, y=y0 + 768, z=1,
        teleport_id=205, dest_npc=205, dest_map=10
    ))
    # A charcoal stone pad with a carved star matches the worked floor and
    # marks the NW entry into trigger 205's box, x >= 8576, y >= 22880.
    # Its half-open footprint is (8575,8831] by (22879,23135], wholly
    # inside the trigger. Shape 779 has zero height and neither DRAW nor
    # OCCL, so it paints over the floor at z=0 without a standing step.
    # The NW arrival-to-doorway route stays clear.
    items.append(MapItem.placed_item(
        x=8831, y=23135, z=0, shape=SHAPE_EXIT_PAD, frame=0))
    # The west wall keeps the lamp clear of the seal and the NW arrival.
    items.append(MapItem.placed_item(
        x=x0 + 32, y=y0 + 512, z=16, shape=SHAPE_WALL_LAMP_ON_X_WALL, frame=0))
    return items


def build_corridors():
    """Connecting corridors (2026-07-04): floors + flanking walls so the
    carved section doorways actually lead somewhere.

    Glob eggs expand chunk-relative (GlobEgg::enterFastArea masks the
    egg position to its 512-chunk), so corridor floors are laid in
    512-aligned chunk columns/rows; the picket walls define the playable
    lane inside them. No ceilings — these read as open passages.
    """
    items = []
    # (a) Hub → Water: vertical corridor from the hub's south gap
    # x (9472, 9984] at y=7167 down to the water section's north-wall
    # doorway x (9472, 9984] at y=14336. The walkable lane is bounded by
    # the west wall column at x=9472 (body (9440,9472]) and the east
    # column at x=10016 (body (9984,10016]) — interior x (9472, 9984),
    # 512 wide. Floor: chunk snapping forces two chunk columns
    # (x 9216..10239); the strips outside the corridor walls are sealed
    # off by the hub south wall (row y≈7152) and water north wall
    # (row y≈14320) and connect to nothing.
    items.extend(generate_terrain_grid(9216, 7168, 2, 14,
                                       GLOB_DUNGEON_FLOOR))
    wall_run_s(items, 9472, 7168, 7168)     # west flank
    corridor_verge(items, 'y', 10016, 7168, 7168, 242)
    # (b) Earth → Hub: horizontal corridor, floor y 5120..5631 (1 chunk)
    # from x=6144 to x=8191 (4 chunks), joining the earth east-wall
    # doorway y (5120, 5632] to the hub's west gap y (5120, 6144].
    # Flank walls sit ON the floor edges: north flank body (5120,5152],
    # south flank body (5600,5632] — walkable lane y (5152, 5600],
    # 448 wide.
    items.extend(generate_terrain_grid(6144, 5120, 4, 1,
                                       GLOB_DUNGEON_FLOOR))
    wall_run_e(items, 6144, 5152, 2048)     # north flank
    corridor_verge(items, 'x', 5632, 6144, 2048, 242)
    # (c) Air → Hub: mirror corridor, floor y 5120..5631 from x=11264 to
    # x=14335 (6 chunks), joining the hub's east gap to the air
    # west-wall doorway y (5120, 5632].
    items.extend(generate_terrain_grid(11264, 5120, 6, 1,
                                       GLOB_DUNGEON_FLOOR))
    wall_run_e(items, 11264, 5152, 3072)    # north flank
    corridor_verge(items, 'x', 5632, 11264, 3072, 242)
    return items


def corridor_verge(items, axis, at, start, span, floor):
    """Retain the near flank's collision and paint a sealed stone verge."""
    run = wall_run_e if axis == 'x' else wall_run_s
    shape = SHAPE_BLOCKER_X if axis == 'x' else SHAPE_BLOCKER_Y
    for z in (0, 48):
        if axis == 'x':
            run(items, start, at, span, z=z, shape=shape)
            run(items, start, at + 160, span, z=z, shape=shape)
        else:
            run(items, at, start, span, z=z, shape=shape)
            run(items, at + 160, start, span, z=z, shape=shape)
    for end in range(start + 127, start + span, 128):
        x, y = (end, at + 127) if axis == 'x' else (at + 127, end)
        items.append(MapItem.placed_item(x, y, 0, floor, (end // 128) % 7))


def fire_water_doorway_view(items):
    """Clear the near jamb beside the Fire-to-Water quest band."""
    upper = []
    for it in items:
        if (it.shape == SHAPE_CAVE_WALL_S and it.z == 0
                and it.x in (6143, 6144) and it.y in (17024, 17152)):
            it.shape, it.frame = SHAPE_BLOCKER_Y, 0
            upper.append(MapItem.placed_item(it.x, it.y, 48, SHAPE_BLOCKER_Y, 0))
    return items + upper


def pad_quest_view(items):
    """Lower the pad's near walls and clear the gate shoulder's view."""
    for it in items:
        if it.shape == WALL_EW and (
                (it.y == 23551 and it.z >= 40) or
                (it.y in (22527, 22528) and 8192 < it.x <= 8960
                 and (it.z >= 40 or it.x <= 8448))):
            it.shape, it.frame = SHAPE_BLOCKER_X, 0
        elif (it.shape == WALL_NS and it.x == 9215 and 22528 < it.y <= 23552
              and it.z >= 40):
            it.shape, it.frame = SHAPE_BLOCKER_Y, 0
    return items


# The stone faces this projection shows: the north line and west wall of
# each worked room. (The pillars chamber's two left with its stone walls,
# 2026-10-17.)
RELIEF_LINES = [('y', 1024), ('x', 8192),        # entry hall
                ('y', 4096),                     # hub (west wall shared x)
                ('y', 22528)]                    # pad (west wall shared x)

# ── screen05, the daemon's torture pocket (2026-10-17) ───────────────────
# docs/research/2026-10-16-screenshot-reconstruction.md; the vignette is
# vignettes/screen05.json, origin (2048, 14080), anchored on the group-3
# daemon egg, on the shot's floor (moved 32 east to (2880, 15104), off the
# rack's fire field; build_fire_section).
# The pocket opens east, along rows 117-118, onto the north-south
# causeway; the rest of the Fire wing's north-west quadrant is rock, its
# south edge stepping down to the strip beside the causeway that holds
# the group-10 daemon egg (3264, 15872). Columns 8..25 (x 1024..3327),
# rows 112..127 (y 14336..16383); '?' and every cell the window decides
# follow the shot.
SCREEN05_MASK_CELL0 = (8, 112)
SCREEN05_MASK = [
    '##################',   # 112
    '##################',   # 113
    '##################',   # 114
    '##################',   # 115
    '##################',   # 116
    '##################',   # 117
    '#################.',   # 118
    '#################.',   # 119
    '################..',   # 120
    '################..',   # 121
    '###############...',   # 122
    '##############....',   # 123
    '#############.....',   # 124
    '############......',   # 125
    '##########........',   # 126
    '########..........',   # 127
]

# The shot's two fire fields 400 f0 are SF_QUALITY items, which
# map_validate wants on a floor that is not black. The one by the rack,
# (2687, 15071, 0), stands on its 301 tile, but the validator reads boxes
# round the origin as a centre, so the void plate west of the tile won
# the tie; relifted 2 (8 units south-east, 2 up: the same pixels) it reads
# its own tile. The one at the floor's lip, (2879, 15679, 48), was solved
# in the air over the black lip and no relift puts it over floor: left
# out (89.82 -> 89.00%).
SCREEN05_RELIFT = {(400, 0, 2687, 15071, 0): 2}
SCREEN05_LEFT_OUT = ((400, 0, 2879, 15679, 48),)


def place_screen05(items):
    """Stamp screen05 and close the Fire wing's north-west rock round it."""
    items, shot = cave_vignette.stamp(items, 'screen05', 11)
    items = shot.drop(items, SCREEN05_LEFT_OUT)
    shot.relift(items, SCREEN05_RELIFT)
    cave = cave_vignette.Cave(shot, SCREEN05_MASK_CELL0, SCREEN05_MASK)
    items = cave.build(items, 11)
    items = cave.underlay(items)
    return items + cave.dress(items, salt=5)


# ── screen07, the Pillar of Fire (2026-10-17) ────────────────────────────
# vignettes/screen07.json, origin (6272, 20608): the shot's pillar is the
# Fire pillar pin itself (865 f2 q203 at (7680, 21504)), held through the
# stamp, and the vignette's copy of it dropped. The 1994-only pieces:
#   2023  the 1994 Pillar of Fire, completed 2026-10-25 (phase D; 2020 was
#         its reference crop): the pin, 865 f2, whose art it now is;
#   2022  the lava glow and pit lip round the pillar (a residual): left
#         out. The best retail fit by window score, a lava tile 409 f20 at
#         (7448, 21272), buys 0.31 points but is a 128-unit flat off the
#         floor lattice, overlapping the 301 tiles, and a burning one;
#   2030-2039  the ten wall spikes. Stand-ins were searched by window
#         score: for each spike, every frame of the 26-32 wall family,
#         the 98-108 and 112 step blocks, 125, 186, 66, 138, 334, 393,
#         469, 472, 519-521 and 736, at the screen offset where the frame
#         best matches the spike's pixels, at z 0..96. Spike 0 is the
#         missing wall piece 26 f5 (89 of 89 px), at (7544, 21176, 48) it
#         adds 0.17; no frame gains as much as 0.05 for the others (spike
#         6's 107 f1 match, 107 of 125 px, costs 0.09 to 0.18 as a whole
#         sprite), so they are left out.
SCREEN07_PILLAR = (SHAPE_PILLAR, 7680, 21504, 0)
SCREEN07_LEFT_OUT = (2022, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037,
                     2038, 2039)
SCREEN07_STANDINS = [(26, 5, 7544, 21176, 48),     # spike 0 (2030)
                     # the rubble mound's right edge in front of the
                     # pillar's foot, which 865 f2 drew over until the
                     # 1994 pillar (phase D, +0.34 by window score)
                     (99, 1, 7580, 21432, 0),
                     # the right cliff's front course runs on to the frame
                     # edge in 1994: one more piece east of the vignette's
                     # two (phase E, 2026-10-30, +0.35; the best of every
                     # 26-32 frame at x 8191-8319, y 21375-21631)
                     (26, 2, 8191, 21503, 0)]
# An all-black cap flat 393 f11 the shot solved at z 0 on the rock band:
# LAND, so the void fill took the cell for floor and left the rest of it
# unpainted round the sprite. The void paints the same black (86.946 ->
# 86.934%). Left out.
SCREEN07_BLACK_FILLERS = ((393, 11, 7296, 20828, 0),)
# The cave the chamber became: columns 48..79 (x 6144..10239), rows
# 152..174 (y 19456..22399); row 175, the south gate line, is outside the
# box and stays masonry. The Water section's south wall closes row 152 and
# the map rim the east side. Column 48 is rock all the way down: the rim's
# west course stands at x 6144, straddling the box edge, so the closure
# rebuilds it as the rock's seen face one cell in. The rock is the shot's:
# its black band from the north-west corner across to x 8191 (the shot's
# rock top between the two cave walls at y 20991 and 21311), with the
# Earth socket on its north lip and the Fire pillar in the bay south of
# it; the cave goes round the band's east end, so all four pillars, both
# doorways and the shot's floor are one floor. A few outcrops round the
# corners. Phase E (2026-10-30) closed three cells of the notch north of
# the band, (57,160), (58,161), (59,162): their floor showed through above
# the right cliff where the shot is black (+0.93). The Earth socket in
# (59,161) keeps its north and east sides open.
SCREEN07_MASK_CELL0 = (48, 152)
SCREEN07_MASK = [
    '####............................',  # 152
    '###.............................',  # 153
    '##..............................',  # 154
    '#...............................',  # 155
    '#...............................',  # 156
    '#...............................',  # 157
    '######..........................',  # 158
    '#######.........................',  # 159
    '########.#.................##...',  # 160
    '#########.#..###............###.',  # 161
    '###########.####.............##.',  # 162
    '################................',  # 163
    '################................',  # 164
    '#.....##########................',  # 165
    '#......########.................',  # 166
    '#...............................',  # 167
    '#...............................',  # 168
    '#...............................',  # 169
    '#...............................',  # 170
    '#...............................',  # 171
    '###.............................',  # 172
    '###.........................###.',  # 173
    '#...............................',  # 174
]


def place_screen07(items, faces=True):
    """Stamp screen07 round the Fire pillar pin and close the chamber's
    cave. `faces=False` leaves the retail pieces 891/892 redraw in place
    (tools/art/screen07_cuts.py cuts the 1994 art against them)."""
    stub = (782, 0)          # any retail id: these are dropped at once
    art = {2023: (SHAPE_PILLAR, 2)}
    art.update({k: stub for k in SCREEN07_LEFT_OUT})
    shot = cave_vignette.Shot('screen07', art_map=art)
    items, shot = cave_vignette.stamp(items, shot, 11, keep=[SCREEN07_PILLAR])
    copy = [it for it in items
            if (it.shape, it.x, it.y, it.z) == SCREEN07_PILLAR and it.quality == 0]
    assert len(copy) == 1, copy
    items = [it for it in items if it is not copy[0]]
    ox, oy, oz = shot.origin
    left_out = [(stub[0], stub[1], ox + it['x'], oy + it['y'], oz + it['z'])
                for it in shot.vig['items'] if it['shape'] in SCREEN07_LEFT_OUT]
    items = shot.drop(items, left_out + list(SCREEN07_BLACK_FILLERS))
    items = shot.add(items, [MapItem.placed_item(x, y, z, s, f)
                             for s, f, x, y, z in SCREEN07_STANDINS])
    cave = cave_vignette.Cave(shot, SCREEN07_MASK_CELL0, SCREEN07_MASK)
    items = cave.build(items, 11)
    items = cave.underlay(items)
    items = items + cave.dress(items, salt=7)
    return screen07_faces(items, shot.origin) if faces else items


def screen07_rock_tops():
    """Paint the 96-unit crest along its view ray beneath the Avatar."""
    art = {2023: (SHAPE_PILLAR, 2)}
    art.update({k: (782, 0) for k in SCREEN07_LEFT_OUT})
    shot = cave_vignette.Shot('screen07', art_map=art)
    cave = cave_vignette.Cave(shot, SCREEN07_MASK_CELL0, SCREEN07_MASK)
    out = []
    for cx, cy in sorted(k for k in cave.cells if not cave.floor128(k)):
        cap = MapItem.placed_item(cx * 128 + 127 - 384,
                                  cy * 128 + 127 - 384, 0,
                                  301, (cx + cy) % 7)
        if not cave.windowed((cx, cy)) and not shot.paints_window(cap):
            out.append(cap)
    return out


def screen07_faces(items, origin):
    """Each retail wall and floor piece the 1994 art redraws (891, 892:
    registry 2043 and 2027, one frame per piece, `base` its retail shape and
    frame, `at` its vignette-local spot) takes its own frame. Exactly one
    item must stand at each spot."""
    with open(REGISTRY) as f:
        reg = json.load(f)
    ox, oy, oz = origin
    swap = {}
    for rid, shape in ((2043, SHAPE_CAVE_FACE_1994),
                       (2027, SHAPE_CAVE_FLOOR_1994)):
        for n, fr in enumerate(reg['shapes'][str(rid)]['frames']):
            x, y, z = fr['at']
            swap[(*fr['base'], ox + x, oy + y, oz + z)] = (shape, n)
    hit = {}
    for it in items:
        k = (it.shape, it.frame, it.x, it.y, it.z)
        if k in swap:
            hit[k] = hit.get(k, 0) + 1
            it.shape, it.frame = swap[k]
    bad = {k: hit.get(k, 0) for k in swap if hit.get(k, 0) != 1}
    assert not bad, f'screen07 faces: pieces not found exactly once: {bad}'
    return items


def build_rim(items):
    """Close the dungeon's outline with cave-wall rock.

    THE MAP HAD NO EDGE (found 2026-09-19, the same class as Map 13's
    missing rim). The engine supports any position with z <= 0
    unconditionally, so every unbuilt cell at floor level is walkable
    forever: `exact_reach` seeded at both arrival pads over the footprint
    plus 3,000 units reached 309,402 of 314,131 standable positions and a
    bbox of x 31..21023, y 31..25119 against a footprint of x 1024..19455,
    y 1024..23551. It escaped on all four sides.

    `lv_landscape.rim` stacks two courses of 26/32 (the shapes this
    builder already uses for its own cave walls) along every chunk edge
    with no neighbour, in the void just beyond the edge so no floor is
    lost, and a 125 crest one course above. The chunk set is read back off
    the glob eggs the section builders emit, the way `void_floor` reads
    their floors, so it cannot drift when a section's terrain grid
    changes.

    Every glob here sits at z=0, so the rim is a uniform 96 tall, which is
    the height of the two-course stone the rooms are walled with. The
    voids BETWEEN the sections lie outside the outline; each gets rimmed
    on both faces and receives its elemental surround beyond the barriers.

    A rim piece inside a section's own wall is left out (`unwalled`): the
    wall already closes that edge, and where the two kits' courses differ
    (the stone rooms' 40-unit 10/15 against the rim's 48-unit 32/26) each
    piece interpenetrates two of the other's, which the renderer cannot
    order. With the Avatar on pad 204, in the teleporter room's north-west
    corner, the rim's 32 at (8192,22784,0) sorted under him by x, the
    room's 10 at (8192,22656,40) over him by z, and the 10 under the 32 by
    y: 1 -> 32 -> 10 -> 1 (test_paint_cycles section 8). A rim piece that
    is the exact box of a section piece stays (two identical boxes always
    sort), so only the mixed courses go.
    """
    chunks = {(it.x // 512, it.y // 512): 0
              for it in items if it.is_glob_egg}
    # These coincident outer rims also face the connector lanes. Keep
    # their collision invisible so they cannot cover the cleared flanks.
    flush = {(cx, 10, 'south') for cx in (*range(12, 16), *range(22, 28))}
    flush |= {(19, cy, 'east') for cy in range(14, 28)}
    flush |= {(cx, 45, 'south') for cx in (16, 17)}
    flush |= {(17, cy, 'east') for cy in (44, 45)}
    return unwalled(rim(chunks, courses=2, crest=True, flush=flush), items)


def unwalled(rim_items, items):
    """`rim_items` less each piece whose box some solids of `items` contain
    in x and y and cover over its whole height, unless one of them is that
    very box (same position and footprint)."""
    flags = vignette_place._flags()

    def box(it):
        f = flags.get(it.shape)
        if not f or not f['solid']:
            return None
        xd, yd = f['xfoot'] * 32, f['yfoot'] * 32
        if it.flags & 0x20:                       # FLG_FLIPPED
            xd, yd = yd, xd
        return (it.x - xd, it.x, it.y - yd, it.y, it.z, it.z + f['zfoot'] * 8)

    walls = {}
    for it in items:
        b = None if it.is_glob_egg else box(it)
        if b:
            for cx in range(b[0] // 128, b[1] // 128 + 1):
                for cy in range(b[2] // 128, b[3] // 128 + 1):
                    walls.setdefault((cx, cy), set()).add(b)
    out = []
    for r in rim_items:
        rb = box(r)
        if rb is None or rb[4] == rb[5]:
            out.append(r)
            continue
        cover = {b for cx in range(rb[0] // 128, rb[1] // 128 + 1)
                 for cy in range(rb[2] // 128, rb[3] // 128 + 1)
                 for b in walls.get((cx, cy), ())
                 if b[0] <= rb[0] and rb[1] <= b[1] and b[2] <= rb[2]
                 and rb[3] <= b[3] and b[4] < rb[5] and rb[4] < b[5]}
        z = rb[4]
        for z0, z1 in sorted((b[4], b[5]) for b in cover):
            if z0 <= z < z1:
                z = z1
        if rb in cover or z < rb[5]:
            out.append(r)
    return out


# Phase 4 uses silhouettes and bounded material patches to distinguish the wings.
# Coordinates below describe individual scenes; the shared Site protects them
# before it considers the surrounding cave debris.
# Lava shore contours use the existing floor lattice. Cold corner cells
# join each lake to the causeway landscape without adding burning ground.
FIRE_LAKE_SHORES = {
    (7,1): ('.LL.', 'LLLL', 'LLLL', '.LLL'),
    (6,2): ('LLL.', 'LLLL', 'LLLL', '.LLL'),
    (2,6): ('.LLL', 'LLLL', 'LLLL', 'LLLL'),
    (2,7): ('LLLL', 'LLLL', 'LLL.', '.LL.'),
    (7,6): ('.LL.', 'LLLL', 'LLLL', 'LLLL'),
    (6,7): ('.LLL', 'LLLL', 'LLLL', '.LLL'),
    (7,7): ('LLLL', 'LLLL', 'LLL.', 'LL..'),
}

DRESSING_BOXES = {
    'entry hall': (8192, 1024, 11263, 4095),
    'hub': (8192, 4096, 11263, 7167),
    'earth': (1024, 1024, 6143, 6143),
    'air': (14336, 1024, 19455, 6143),
    'fire': (1024, 14336, 6143, 19455),
    'water': (6144, 14336, 14335, 19455),
    'four pillars': (6144, 19456, 10239, 22527),
    'pad room': (8192, 22528, 9215, 23551),
}

# Even-x wall fragments remain loose through pack(), as required by the
# baked-wall hygiene check. Their authored pixels retain the same projection.
DRESSING_SCENES = {
    'votive alcove': (
        (10239, 2655, 0, 38, 0),
        (10559, 2655, 0, 38, 2),
        (10206, 2879, 0, 47, 0),
        (10591, 2847, 0, 46, 0),
        (10335, 2815, 0, 899, 3),
        (10431, 2943, 0, 899, 0),
        (10303, 3007, 0, 465, 8),
        (10527, 3007, 0, 465, 12),
        (10463, 2783, 0, 900, 0),
        (10239, 3103, 0, 465, 3),
        (10303, 3167, 0, 465, 12),
    ),
    'golem root den': (
        (1983, 3615, 0, 66, 3),
        (2335, 3519, 0, 66, 8),
        (1823, 3839, 0, 57, 1),
        (2303, 3871, 0, 57, 3),
        (2079, 3967, 0, 65, 6),
        (2207, 4063, 0, 65, 7),
        (1919, 4031, 0, 65, 0),
        (2111, 3807, 0, 900, 0),
        (2111, 3583, 0, 899, 2),
        (2047, 3903, 0, 899, 4),
        (2431, 4095, 0, 465, 5),
        (1951, 4191, 0, 465, 13),
    ),
    'wind-broken ring': (
        # Eight surviving stones share a circle around the cleared scour.
        (18559, 2783, 0, 908, 4),
        (18831, 2895, 0, 908, 1),
        (18943, 3167, 0, 908, 8),
        (18831, 3439, 0, 908, 6),
        (18559, 3551, 0, 908, 0),
        (18287, 3439, 0, 908, 1),
        (18175, 3167, 0, 908, 5),
        (18287, 2895, 0, 908, 1),
        # Three fallen shoulders and their chips trail southeast with the wind.
        (19011, 3493, 0, 910, 6),
        (18923, 3611, 0, 910, 8),
        (18789, 3703, 0, 910, 7),
        (19037, 3581, 0, 465, 11),
        (18949, 3707, 0, 465, 2),
        (18819, 3673, 0, 465, 5),
    ),
    'charred offering': (
        (4639, 15391, 0, 75, 0),
        (4447, 15519, 0, 66, 1),
        (4831, 15583, 0, 66, 4),
        (4607, 15711, 0, 152, 0),
        (4479, 15775, 0, 899, 1),
        (4799, 15807, 0, 899, 0),
        (4671, 15839, 0, 900, 1),
        (4543, 15871, 0, 603, 0),
        (4767, 15903, 0, 603, 0),
        (4383, 15711, 0, 465, 10),
        (4479, 15839, 0, 465, 1),
        (4511, 15903, 0, 465, 4),
        (4575, 15935, 0, 465, 8),
        (4639, 15967, 0, 465, 2),
        (4703, 15935, 0, 465, 12),
        (4767, 15967, 0, 465, 7),
        (4831, 15903, 0, 465, 3),
        (4895, 15871, 0, 465, 16),
    ),
    'drowned portico': (
        (11455, 16703, 0, 46, 0),
        (11774, 16735, 0, 47, 0),
        (11391, 16863, 0, 46, 0),
        (11583, 16927, 0, 899, 0),
        (11711, 16991, 0, 899, 3),
        (11487, 17087, 0, 899, 4),
        (11807, 17119, 0, 899, 1),
        (11359, 17023, 0, 65, 6),
        (11295, 16895, 0, 65, 7),
        (11871, 16991, 0, 465, 9),
        (11615, 17183, 0, 465, 1),
    ),
    'broken ritual crescent': (
        # A broken horn at each end frames the empty ritual floor.
        (9119, 21215, 0, 908, 4),
        (9663, 21183, 0, 908, 8),
        (9727, 21343, 0, 910, 6),
        (9759, 21439, 0, 910, 8),
        (9663, 21503, 0, 910, 7),
        (9599, 21599, 0, 899, 2),
        (9471, 21663, 0, 899, 3),
        (9311, 21695, 0, 899, 0),
        (9215, 21631, 0, 910, 6),
        (9151, 21535, 0, 899, 4),
        (9375, 21471, 0, 900, 1),
        (9535, 21567, 0, 909, 0),
        (9247, 21471, 0, 909, 0),
        (9407, 21567, 0, 465, 8),
        (9471, 21631, 0, 465, 3),
        (9279, 21599, 0, 465, 6),
        (9215, 21471, 0, 465, 2),
        (9695, 21535, 0, 465, 15),
        (9599, 21663, 0, 465, 9),
    ),
    'last ward': (
        (9119, 22687, 0, 38, 0),
        (8958, 22719, 0, 47, 0),
        (9055, 22815, 0, 899, 3),
        (8959, 22815, 0, 899, 0),
        (9087, 22751, 0, 465, 12),
        (8991, 22783, 0, 465, 3),
    ),
}


def clipped_supports(items):
    """Retain every original clipped backdrop's editor-only support box."""
    present = {(it.shape,it.x,it.y,it.z) for it in items}
    return [MapItem.placed_item(*clip['at'],0,clip['support_shape'],0)
            for clip in CAVE_BACKDROP_CLIPS
            if clip['map'] == 11 and clip.get('kind') != 'window'
            and (clip['support_shape'],*clip['at'],0) not in present]


def legacy_lone_prop(it):
    """Retain ambient rocks only inside the protected cave masks."""
    if it.shape not in (65,66) or it.quality:
        return False
    if 1024 <= it.x <= 3327 and 14336 <= it.y <= 16383:
        return False
    if 6144 <= it.x <= 10239 and 19456 <= it.y <= 22399:
        return False
    return True


def cold_fire_bank():
    """Cold rock outside the rim separates the northbound walks from lava."""
    import random
    return [MapItem.placed_item(
        cx*128+127, cy*128+127, 0, 301,
        random.Random(f'11:cold-bank:{cx}:{cy}').randrange(7))
        for cx in range(40,48) for cy in range(108,112)]


def dressing_floors(items):
    """Filled halls and shaped earth, gravel, and water pockets."""
    import random
    from glob_catalog import GlobReader
    from item_sorter import ItemSorter
    import lv_dressing
    globs, sorter = GlobReader(), ItemSorter()
    windows = lv_dressing.shot_windows(11)
    out = []
    # Six grain patterns retain chunk packing without a repeating floor
    # lattice. Each chunk chooses independently and refuses a third twin.
    grain = {}
    for cx, cy in sorted({(it.x//512,it.y//512) for it in items}):
        choices = list(range(6))
        random.Random(f'11:grain:{cx}:{cy}').shuffle(choices)
        grain[cx,cy] = next(v for v in choices
                            if not (grain.get((cx-1,cy)) == grain.get((cx-2,cy)) == v
                                    or grain.get((cx,cy-1)) == grain.get((cx,cy-2)) == v))
    terraces = {(it.x, it.y, it.z) for it in items
                if it.shape == 113 and 14336 <= it.x < 19456}
    crest_frames = {frozenset('S'): (3, 4), frozenset('E'): (1, 2),
                    frozenset('N'): (9, 10), frozenset('W'): (7, 8),
                    frozenset('SE'): (0,), frozenset('SW'): (5,),
                    frozenset('NE'): (6,), frozenset('NW'): (11,),
                    frozenset('NSEW'): (16,)}
    for it in items:
        if (it.x, it.y, it.z) not in terraces or it.shape != 113:
            continue
        drop = frozenset(side for side, dx, dy in
                         (('N',0,-128),('S',0,128),('W',-128,0),('E',128,0))
                         if (it.x+dx,it.y+dy,it.z) not in terraces)
        rng = random.Random(f'11:ledge:{it.x}:{it.y}:{it.z}')
        it.shape, it.frame = 125, rng.choice(crest_frames.get(drop, (12,13,14)))
    # The four original pools retain their 112 navy tiles.
    for record in items:
        if (record.shape in (WALL_EW, WALL_NS) and record.z >= 40
                and not lv_dressing.paints_window(record, sorter, windows)):
            # Two overlapping 32-unit invisible courses reproduce this
            # 40-unit span exactly, including its original top face.
            # Existing 497 and 498 records retain all their fields.
            out.extend(MapItem.placed_item(record.x, record.y, record.z+dz,
                                           SHAPE_BLOCKER_X_LOW if record.shape == WALL_EW
                                           else SHAPE_BLOCKER_Y_LOW, 0)
                       for dz in (0,8))
            continue
        shore = (FIRE_LAKE_SHORES.get((record.x//512-2,record.y//512-28))
                 if record.is_glob_egg and record.quality == 802 else None)
        tiles = (globs.glob_to_items(record.quality, record.x, record.y, record.z)
                 if record.is_glob_egg and (record.quality in (42,65,397) or shore)
                 else [record])
        if shore:
            for tile in tiles:
                if shore[(tile.y%512)//128][(tile.x%512)//128] == '.':
                    tile.shape, tile.frame = 301, 0
        for tile in tiles:
            if tile.z != 0 or tile.shape not in (35, 242, 301):
                out.append(tile)
                continue
            if lv_dressing.paints_window(tile, sorter, windows):
                out.append(tile)
                continue
            x, y = tile.x, tile.y
            rng = random.Random(
                f'11:ritual-grain:{x}:{y}'
                if 6144 <= x < 10240 and 19456 <= y < 22528 else
                f'11:floor:{grain[x//512,y//512]}:{x%512}:{y%512}')
            if 1024 <= x < 6144 and 1024 <= y < 6144:
                tile.shape, tile.frame = 301, rng.randrange(7)
                # Two chambers of exposed soil, with a broken gravel fringe.
                a = ((x-2100)/1050)**2 + ((y-3700)/1250)**2
                b = ((x-4800)/1050)**2 + ((y-4400)/1200)**2
                c = ((x-3000)/1400)**2 + ((y-1550)/500)**2
                if min(a,b) < .85:
                    tile.shape, tile.frame = 4, rng.choice((30,31,32,33))
                elif min(a,b) < 1.25 or c < 1:
                    tile.shape, tile.frame = 6, rng.randrange(3)
            elif 14336 <= x < 19456 and 1024 <= y < 6144:
                tile.frame = rng.randrange(7)
                # Gravel scours a crescent round the broken ring and a
                # separate north-west talus pocket, with clear rock between.
                a = ((x-18300)/1320)**2 + ((y-3200)/1450)**2
                b = ((x-15300)/900)**2 + ((y-2300)/1200)**2
                if min(a,b) < 1:
                    tile.shape, tile.frame = 6, rng.randrange(3)
                if ((x-18559)/290)**2 + ((y-3167)/290)**2 < 1:
                    tile.shape, tile.frame = 71, rng.randrange(3)
            elif (tile.shape == 301 and 1024 <= x < 6144 and 14336 <= y < 19456):
                tile.frame = rng.randrange(7)
                if ((x-4600)/400)**2 + ((y-15700)/450)**2 < 1:
                    tile.shape, tile.frame = 6, rng.randrange(3)
            elif ((9472 < x < 9984 and 7168 <= y < 14336)
                  or (5120 <= y < 5632
                      and (6144 <= x < 8192 or 11264 <= x < 14336))):
                # Only the corridor walking strips become cut stone.
                # Their authored 242 verges remain outside these bands.
                tile.shape, tile.frame = 35, rng.choice((0,1))
            elif tile.shape == 35:
                tile.frame = rng.choice((0,1))
                if 6144 <= x < 14336 and 14336 <= y < 19456:
                    # Stone margins frame the original flood pockets.
                    if x < 6528 or x > 13950 or y < 14720 or y > 19150:
                        tile.shape, tile.frame = 71, rng.randrange(3)
                elif (8192 <= x < 11264 and 1024 <= y < 7168):
                    # Stone margins join the column bays, leaving one nave.
                    if x < 8704 or x > 10751 or (y < 1536) or (6656 <= y < 7168):
                        tile.shape, tile.frame = 71, rng.randrange(3)
                elif 8192 <= x < 9216 and 22528 <= y < 23552:
                    if x > 8959 or y < 22784:
                        tile.shape, tile.frame = 71, rng.randrange(3)
            else:
                tile.frame = rng.randrange(7)
            # Two uneven fragment courses continue the hall into each cave.
            if ((x, y) in ((6015,5247),(6143,5375),(6015,5503),(6143,5503),
                           (14463,5247),(14591,5375),(14463,5503),(14591,5503),
                           (6015,16511),(6143,16639),(6015,16895),(6143,16895),
                           (8575,19583),(8703,19583),(8575,19711),(8703,19711),
                           (8831,22271),(8959,22271),(8831,22399),(8959,22399))):
                tile.shape, tile.frame = 35, rng.choice((0,1))
            if (6144 <= x < 10240 and 19456 <= y < 22528
                    and ((x-9407)/500)**2 + ((y-21407)/440)**2 < 1):
                tile.shape, tile.frame = 6, rng.randrange(3)
            if (8192 <= x < 11264 and 4096 <= y < 7168
                    and ((x-8511)/240)**2 + ((y-5631)/280)**2 < 1):
                tile.shape, tile.frame = 6, rng.randrange(3)
            out.append(tile)
            if (x,y) in ((10111,6527),(10239,6527),(10111,6655),(10239,6655)):
                # Retained stone supports the decorative water paint.
                out.append(MapItem.placed_item(x,y,0,896,0))
    return out


def adopt_shared_dressing(site):
    """Element markers, wall paint, and cold lips retain the original route."""
    # Twelve low stone courses close each 256-unit marker on all four sides.
    # Their rough edge frames meet the inset water and the other elements.
    for element, x, y in (('Earth',8511,5631), ('Air',10879,5759),
                           ('Fire',10047,4543), ('Water',10111,6527)):
        kerb = [MapItem.placed_item(x+dx,y+dy,0,shape,0)
                for dx,dy,shape in (
                    (0,-128,670),(128,-128,670),
                    (0,160,670),(128,160,670),
                    (-128,0,692),(-128,128,692),
                    (160,0,692),(160,128,692),
                    (-128,-128,734),(160,-128,734),
                    (-128,160,734),(160,160,734))]
        site.walkable_set_piece('elemental crossing ' + element, kerb)
    site.set_piece('elemental crossing Water', [
        MapItem.placed_item(x,y,0,347,frame)
        for x,y,frame in ((10111,6527,0),(10239,6527,2),
                          (10111,6655,4),(10239,6655,5))])
    markers = (
        (8511, 5631, 0, 899, 2), (8543, 5567, 0, 910, 6),
        (8479, 5631, 0, 899, 0), (8607, 5535, 0, 465, 9),
        (10879, 5759, 0, 908, 4), (10783, 5663, 0, 465, 3),
        (10911, 5663, 0, 465, 11),
        (10047, 4543, 0, 911, 6), (10047, 4511, 0, 603, 0),
        (10111, 4575, 0, 603, 0), (10175, 4479, 0, 910, 8),
    )
    for element, rows in (('Earth', markers[:4]), ('Air', markers[4:7]),
                          ('Fire', markers[7:])):
        site.set_piece('elemental crossing ' + element,
                       [MapItem.placed_item(*row) for row in rows])
    site.paint_only('corridor reliefs', [
        MapItem.placed_item(7167, 5183, 48, 913, 0),
        MapItem.placed_item(12799, 5183, 48, 913, 0),
        MapItem.placed_item(9503, 10751, 48, 912, 0),
        MapItem.placed_item(9215, 1087, 48, 913, 2),
        MapItem.placed_item(10879, 1087, 48, 913, 4),
    ])
    # Paired urns flank the retained columns' south-facing feet.
    for x, y, a, b, c, d in (
        (8960,2048,-96,64,80,96), (10496,2048,-64,112,112,64),
        (8960,3328,-112,96,64,128), (10496,3328,-80,80,128,64),
        (8960,4864,-96,112,96,64), (10496,4864,-64,80,80,128),
        (8960,6400,-128,64,80,112), (10496,6400,-80,128,112,80),
    ):
        site.set_piece(f'urn pair {x} {y}', [
            MapItem.placed_item(x+a,y+b,0,909,0),
            MapItem.placed_item(x+c,y+d,0,909,0)])
    # Only the two low Air ledges receive clipped eight-unit riser paint.
    faces = [MapItem.placed_item(i.x,i.y,i.z,914,0)
             for i in site.items if i.shape == 125 and 14336 <= i.x < 19456
             and 1024 <= i.y < 6144 and i.z in (0,8,16)
             and not any(j.shape == 125 and j.x == i.x and j.y == i.y+128
                         and j.z == i.z for j in site.items)]
    site.paint_only('Air riser faces', faces)
    # Basalt occupies only retained cold cells beside each lake's hot cells.
    hot = {(i.x//128,i.y//128) for i in site.expanded if i.shape == 409}
    for n, (kx, ky) in enumerate(FIRE_LAKE_SHORES):
        cells = []
        for cy in range((ky+28)*4-1,(ky+28)*4+5):
            for cx in range((kx+2)*4-1,(kx+2)*4+5):
                floor = site.ground.get((cx,cy))
                if not floor or floor[0] not in (301,4,386) or floor[2] != 0:
                    continue
                neighbours = [(dx,dy) for dx,dy in ((1,0),(0,1),(-1,0),(0,-1))
                              if (cx+dx,cy+dy) in hot]
                if neighbours:
                    frame = {(1,0):1,(0,1):3,(-1,0):7,(0,-1):9}[neighbours[0]]
                    piece = MapItem.placed_item(cx*128+127,cy*128+127,0,911,frame)
                    if site.reason(piece) is None:
                        cells.append((cx,cy,frame))
        if cells:
            site.basalt_shore(f'cold lake lip {n}', cells)
    # Two broken courses of fragments border each hall-to-cave doorway.
    for name, points in (
        ('Earth threshold', ((5919,5503),(5983,5567),(6047,5503),(6111,5567))),
        ('Air threshold', ((14431,5503),(14543,5583),(14655,5519),(14815,5567))),
        ('Water threshold', ((9409,15015),(9503,15089),(10081,15009),(10177,15057))),
        ('Fire threshold', ((6509,16429),(6633,16467),(6511,17063),(6579,17199))),
        ('Pillars threshold', ((7903,19615),(7959,19671))),
        ('Pad threshold', ((8959,22335),(9039,22431))),
    ):
        site.set_piece(name, [MapItem.placed_item(x,y,0,910,f)
                             for (x,y),f in zip(points,(6,7,8,6))])


def dress_elemental_caves(items):
    """Protect the authored scenes, then dress their wall and seam verges."""
    from parse_typeflag import load_typeflag
    import lv_dressing
    import lv_globs
    shapes = load_typeflag(str(lv_globs.ROOT / 'shared/build/TYPEFLAG.DAT'))
    site = lv_dressing.Site(11, dressing_floors(items), shapes, seed=4011)
    site.reserve('wind-broken ring', (17983,2591,19135,3711))
    site.walkable_set_piece('broken ritual crescent', [
        MapItem.placed_item(x, y, 0, 70, frame)
        for x, y, frame in ((9279,21183,3), (9407,21183,3),
                            (9535,21183,3), (9279,21311,4),
                            (9535,21311,5))])
    for name, rows in DRESSING_SCENES.items():
        site.set_piece(name, [MapItem.placed_item(*row) for row in rows])
    adopt_shared_dressing(site)
    # Pebbles, collapsed masonry, bones, and brush retain the dry flood.
    hall_debris = ((899,4,4),(465,17,3),(900,2,1),(901,2,1))
    cave_debris = ((899,4,2),(465,17,4),(900,2,1),(901,2,1),(321,5,1),(322,5,1))
    for name, kit, density, floors, anchor in (
        ('entry hall', hall_debris, 8, {35,71}, 'wall'),
        ('hub', hall_debris, 9, {35,71}, 'wall'),
        ('earth', cave_debris, 10, {301,4,6}, 'seam'),
        ('air', cave_debris, 8, {301,6}, 'wall'),
        ('fire', cave_debris, 4, {301}, 'wall'),
        ('water', hall_debris, 9, {35,71,896}, 'seam'),
        ('four pillars', ((465,17,3),(899,4,1)), 5, {301}, 'wall'),
    ):
        site.clusters(kit=kit, per100=density, where=DRESSING_BOXES[name],
                      floors=floors, anchor=anchor)
    # Retail's pebble groups follow the open Air floor and clear the ledges.
    import random
    for cx in range(28, 38):
        for cy in range(2, 12):
            rng = random.Random(f'11:air-talus:{cx}:{cy}')
            pick = rng.random()
            if .35 <= pick < .55:
                number = rng.choice((956,957))
            else:
                continue
            site.place_prefab(number, x=cx*512+255, y=cy*512+255,
                              where=DRESSING_BOXES['air'])
    site.set_piece('Pillars threshold', [
        MapItem.placed_item(7831,19691,0,909,0)])
    # Wind carries the broken ring's smallest chips out through its breach.
    site.set_piece('wind-broken ring', [MapItem.placed_item(x,y,0,465,f)
        for x,y,f in ((18803,3537,3),(18887,3579,5),(18961,3517,8),
                      (19021,3639,11),(18837,3671,2),(18763,3589,13),
                      (18693,3687,7),(18917,3733,16))])
    site.set_piece('charred offering', [MapItem.placed_item(x,y,0,465,f)
        for x,y,f in ((4407,15945,2),(4487,15997,8),(4591,15957,13),
                      (4679,15895,3),(4779,15995,5),(4861,15941,11))])
    # A fallen landing beside the flooded nave has four connected footings.
    site.set_piece('fallen Water landing', [MapItem.placed_item(x,y,0,shape,f)
        for x,y,shape,f in (
            (6991,15103,899,0),(7067,15147,465,3),(7115,15217,465,8),
            (7021,15243,465,11),(6953,15189,465,2),(7139,15113,899,3),
            (7183,15359,899,4),(7257,15407,465,13),(7311,15321,465,5),
            (7205,15275,465,7),(7149,15429,465,1),(7319,15469,899,1),
            (6999,15583,899,2),(7073,15637,465,9),(7137,15547,465,4),
            (7031,15501,465,16),(6959,15663,465,12),(7161,15691,899,0),
            (7327,15647,899,3),(7409,15601,465,10),(7463,15719,465,6),
            (7353,15757,465,14),(7269,15733,465,0),(7417,15809,899,4),
        )])
    # Partial surrounds fill void cells beside retained rim fragments.
    site.beyond('lava', partial=True, where=(0,12288,5119,14335))
    site.beyond('lava', partial=True, where=(5120,12288,6143,13823))
    site.beyond('lava', partial=True, where=(0,14336,1023,19455))
    site.beyond('lava', partial=True, where=(0,19456,6143,21503))
    site.beyond('rock', where=(0,0,6143,1023), z=96, family=(388,))
    site.beyond('rock', where=(0,1024,1023,6143), z=96, family=(388,))
    sea = []
    sea.extend(site.beyond('deep_water', where=(6144,12288,9215,14335)))
    sea.extend(site.beyond('deep_water', where=(10240,12288,16383,14335)))
    sea.extend(site.beyond('deep_water', where=(14336,14336,16383,21503)))
    sea.extend(site.beyond('deep_water', where=(10240,19456,14335,21503)))
    # Partial sea strips retain loose tiles, avoiding repeated packed slivers.
    site.floor_order.update(id(i) for i in sea if not i.is_glob_egg)
    packed = site.pack()
    # Ground eggs precede loose pools, pads, and shot-owned floor overlays.
    # Their original layer order keeps the visible surface and the hazard
    # surface in agreement after packing.
    return [it for it in packed if it.is_glob_egg] + [
        it for it in packed if not it.is_glob_egg]


def build_map_11(screen07_faces=True):
    """Build complete Map 11 item list."""
    items = []
    items.extend(build_entry_hall())
    items.extend(build_central_hub())
    items.extend(build_earth_section())
    items.extend(build_air_section())
    items.extend(build_fire_section())
    items.extend(build_water_section())
    items.extend(build_four_pillars())
    items.extend(build_teleporter_pad())
    items.extend(build_corridors())
    items = fire_water_doorway_view(items)
    items = pad_quest_view(items)
    items = accent_reliefs(items, RELIEF_LINES)
    # The map's outline, read off the terrain the sections above emitted.
    items.extend(build_rim(items))
    # The two 1994 shots and the caves they close into (2026-10-17). After
    # the rim (it reads the glob eggs these cut into tiles), before the
    # void.
    items = place_screen05(items)
    items = place_screen07(items, faces=screen07_faces)
    # Ground-level backfill for the six eight-unit lip probes: moving
    # 32 units north-west follows their view ray down to z=0. The cover
    # calculation must see these floors before it chooses its black cells.
    items += [MapItem.placed_item(x, y, 0, 301, 0)
              for x, y in ((2559, 15103), (2687, 14911), (6751, 21119))]
    # Raised cap flats cover the invisible back faces of this cave. Their
    # ground-level view-ray copies preserve the top's pixels and let the
    # Avatar draw in front; the original cave barriers stay in place.
    items.extend(screen07_rock_tops())
    items.extend(clipped_supports(items))
    items = [it for it in items if it.shape not in (186, 796)
             and not legacy_lone_prop(it)]
    items.extend(cold_fire_bank())
    for it in items:
        if it.shape in (SHAPE_TAPESTRY_ON_X_WALL, SHAPE_TAPESTRY_ON_Y_WALL) and it.frame == 5:
            it.frame = 2
    items = dress_elemental_caves(items)
    items.extend(cave_vignette.void_cover(items))
    # Retain the screenshot's upper-edge black behind the offset floor.
    items.extend(MapItem.placed_item(*clip['at'], 0,
                                     SHAPE_CAVE_BACKDROP_LARGE, 7 + n)
                 for n, clip in enumerate(CAVE_BACKDROP_CLIPS)
                 if clip['map'] == 11 and tuple(clip['at']) == (6879, 21119))
    return items


if __name__ == '__main__':
    items = build_map_11()
    globs = sum(1 for i in items if i.is_glob_egg)
    teles = sum(1 for i in items if i.is_teleport_egg)
    mons = sum(1 for i in items if i.is_monster_egg)
    print(f"Map 11: {len(items)} items")
    print(f"  Glob eggs: {globs}")
    print(f"  Teleport eggs: {teles}")
    print(f"  Monster eggs: {mons}")
    print(f"  Other items: {len(items) - globs - teles - mons}")

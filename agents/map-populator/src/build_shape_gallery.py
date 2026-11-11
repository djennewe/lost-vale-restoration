#!/usr/bin/env python3
"""
build_shape_gallery.py — Compact visual test map (Map 22) for shape inspection.

Layout (walk south from spawn at 4096,2048):

  Section A (y≈2560):  3 real Tenebrae buildings copied exactly (z-shifted)
  Section B (y≈7168):  New primitive huts using 622 blocks + various roofs
  Section C (y≈9728):  Individual shape samples in a tight row
  Section D (y≈12288): Roof frame sweep — frames 0–49 for 10 key shapes
  Section E (y≈17408): Cloud City shape candidates (pillars, floors, railings)
  Section F (y=20096):  DD-007 spike — one shape-73 UnkEgg (quality dispatch
                         proof, PLAN.md 2.1/2.2); see MainActor::teleport
                         recipe in _section_dd007_spike()

In-game:
    MainActor::teleport 22 4096 2048 0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from u8_map import MapItem, generate_terrain_grid, MapArchive
from parse_typeflag import load_typeflag
from lv_shapes import SHAPE_PLACEHOLDER_INVISIBLE_EGG

MAP_SLOT = 22

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
BASE_FIXED = os.path.join(
    BASE_DIR, "shared", "data", "u8-install", "STATIC", "FIXED.DAT")


def _place(items, x, y, z, shape, frame=0, quality=0):
    items.append(MapItem.placed_item(x=x, y=y, z=z, shape=shape,
                                     frame=frame, quality=quality))


# ---------------------------------------------------------------------------
# Section A: Copy real Tenebrae buildings exactly
# ---------------------------------------------------------------------------

def _extract_region(archive, map_num, rx, ry, rw, rh, skip_globs=True):
    """Extract all items within a rectangle from a base game map."""
    items = archive.get_map_items(map_num)
    region = []
    for it in items:
        if skip_globs and it.shape == 2:
            continue
        if rx <= it.x < rx + rw and ry <= it.y < ry + rh:
            region.append(it)
    return region


def _relocate(region, dest_x, dest_y):
    """Relocate items preserving original z values (no z-shift).

    Tenebrae buildings are designed for terrain at z=0 — walls go
    underground (z=-128..-104), floors sit at z=0, roofs at z=88+.
    Our gallery terrain is also z=0, so no shifting needed.
    """
    if not region:
        return []

    src_x = min(it.x for it in region)
    src_y = min(it.y for it in region)

    out = []
    for it in region:
        out.append(MapItem(
            x=it.x - src_x + dest_x,
            y=it.y - src_y + dest_y,
            z=it.z,
            shape=it.shape,
            frame=it.frame,
            quality=0,
            flags=0,
        ))
    return out


def _section_tenebrae_copies(items):
    """Copy 3 real Tenebrae building clusters into the gallery."""
    if not os.path.exists(BASE_FIXED):
        print("  (skipping — no base FIXED.DAT)")
        return

    # Must read the PRISTINE base: after an install_lv.sh run the install
    # dir holds the built LV artifact, and the Map 39 region copied below
    # overlaps the LORDBRIT quest-step-1 additions — the gallery silently
    # grew 2 extra items (caught 2026-07-27, the FIXED.DAT reproducibility
    # break was exactly this).
    from base_input import pristine_base
    archive = MapArchive(pristine_base(BASE_FIXED, what='gallery base FIXED.DAT'))

    # Building 1: Map 39 — small stone structure (622 walls + 565 platform)
    # Region around (16700,18700) with ~40 items
    r1 = _extract_region(archive, 39, 16700, 18700, 1200, 1200)
    relocated = _relocate(r1, 1024, 2560, )
    items.extend(relocated)
    print(f"  Building 1 (Map 39 stone): {len(relocated)} items")

    # Building 2: Map 41 — wooden walls (690) + 271 floor
    # Region around (12000,13600) with ~25 items
    r2 = _extract_region(archive, 41, 12000, 13600, 1200, 1200)
    relocated = _relocate(r2, 3584, 2560, )
    items.extend(relocated)
    print(f"  Building 2 (Map 41 wood): {len(relocated)} items")

    # Building 3: Map 41 — larger building section
    # Region around (18752,12096) — the dense area from before
    r3 = _extract_region(archive, 41, 18752, 12096, 2048, 2048)
    relocated = _relocate(r3, 6144, 2560, )
    items.extend(relocated)
    print(f"  Building 3 (Map 41 large): {len(relocated)} items")

    # Building 4: Map 39 — larger stone building (622 + terrain)
    r4 = _extract_region(archive, 39, 13600, 18700, 1200, 1200)
    relocated = _relocate(r4, 1024, 4608, )
    items.extend(relocated)
    print(f"  Building 4 (Map 39 stone 2): {len(relocated)} items")


# ---------------------------------------------------------------------------
# Section B: Primitive huts using verified shapes + correct spacing
# ---------------------------------------------------------------------------

def _stone_hut(items, hx, hy):
    """Small stone hut: 622 walls at 64-unit spacing, 412 roof."""
    # 622 = 2x2x4 footpad → tiles every 64 world units
    STEP = 64
    W = 5  # blocks wide (E-W)
    D = 7  # blocks deep (N-S)

    # Walls at z=-104 (same as Tenebrae) — sprites extend upward
    wz = -104

    # North wall
    for i in range(W):
        _place(items, hx + i * STEP, hy, wz, 622, frame=0)
    # South wall
    for i in range(W):
        _place(items, hx + i * STEP, hy + D * STEP, wz, 622, frame=0)
    # West wall
    for j in range(1, D):
        _place(items, hx, hy + j * STEP, wz, 622, frame=0)
    # East wall (leave gap for door)
    for j in range(1, D):
        if j == D // 2:
            _place(items, hx + W * STEP, hy + j * STEP, 48, 68, frame=0)
            continue
        _place(items, hx + W * STEP, hy + j * STEP, wz, 622, frame=0)

    # Roof — 412 tiles at z=88 (same as Tenebrae)
    for rx in range(0, W * STEP, 128):
        for ry in range(0, D * STEP, 128):
            _place(items, hx + rx, hy + ry, 88, 412, frame=0)


def _wood_hut(items, hx, hy):
    """Wooden hut: 690/691 wall panels, 271 roof."""
    # 690 = 2x5 footpad (64×160), 691 = 5x2 (160×64)
    wz = -8

    # North wall — 691 (5x2, wide E-W): 3 panels
    for i in range(3):
        _place(items, hx + i * 160, hy, wz, 691, frame=0)
    # South wall
    for i in range(3):
        _place(items, hx + i * 160, hy + 448, wz, 691, frame=0)
    # West wall — 690 (2x5, tall N-S): 2 panels
    _place(items, hx, hy + 64, wz, 690, frame=0)
    _place(items, hx, hy + 224, wz, 690, frame=0)
    # East wall — 1 panel + door gap
    _place(items, hx + 480, hy + 64, wz, 690, frame=3)
    _place(items, hx + 480, hy + 224, 0, 68, frame=0)  # door

    # Roof — 271 (8x8 footpad = 256×256)
    _place(items, hx, hy, 8, 271, frame=0)
    _place(items, hx + 256, hy, 8, 271, frame=0)
    _place(items, hx, hy + 256, 8, 271, frame=0)
    _place(items, hx + 256, hy + 256, 8, 271, frame=0)


def _mixed_hut(items, hx, hy):
    """Mixed: stone base (622) + wood upper (690/691) + 412 roof."""
    wz = -8

    # Stone base ring (622 every 64 units)
    for i in range(7):
        _place(items, hx + i * 64, hy, wz, 622, frame=0)
        _place(items, hx + i * 64, hy + 384, wz, 622, frame=0)
    for j in range(1, 6):
        _place(items, hx, hy + j * 64, wz, 622, frame=0)
        if j != 3:  # door gap
            _place(items, hx + 384, hy + j * 64, wz, 622, frame=0)

    # Door
    _place(items, hx + 384, hy + 192, 0, 68, frame=0)

    # Wood upper on two sides (690 at z=0)
    _place(items, hx, hy + 64, 0, 690, frame=0)
    _place(items, hx, hy + 224, 0, 690, frame=0)

    # Roof — 412 at z=10
    for rx in range(0, 384, 128):
        for ry in range(0, 384, 128):
            _place(items, hx + rx, hy + ry, 10, 412, frame=0)


def _flat_hut(items, hx, hy):
    """Simple: 690/691 walls at z=0 (no underground), 412 roof at z=6."""
    # 691 for N/S walls (5x2, 160×64), 690 for E/W walls (2x5, 64×160)
    # North wall
    for i in range(3):
        _place(items, hx + i * 160, hy, 0, 691, frame=0)
    # South wall
    for i in range(3):
        _place(items, hx + i * 160, hy + 384, 0, 691, frame=2)
    # West wall
    _place(items, hx, hy + 64, 0, 690, frame=0)
    _place(items, hx, hy + 224, 0, 690, frame=0)
    # East wall + door
    _place(items, hx + 448, hy + 64, 0, 690, frame=3)
    _place(items, hx + 448, hy + 224, 0, 68, frame=0)

    # Roof at z=6
    for rx in range(0, 448, 128):
        for ry in range(0, 384, 128):
            _place(items, hx + rx, hy + ry, 6, 412, frame=0)


def _section_test_huts(items):
    """Section B: 4 test huts using verified Tenebrae shapes."""
    Y = 7168
    SP = 1536

    print("  Hut 1: Stone (622 walls, 412 roof)...")
    _stone_hut(items, 1024, Y)

    print("  Hut 2: Wood (690/691 walls, 271 roof)...")
    _wood_hut(items, 1024 + SP, Y)

    print("  Hut 3: Mixed (622 base + 690 upper, 412 roof)...")
    _mixed_hut(items, 1024 + SP * 2, Y)

    print("  Hut 4: Flat wood (690/691 at z=0, 412 roof at z=6)...")
    _flat_hut(items, 1024 + SP * 3, Y)


# ---------------------------------------------------------------------------
# Section C: Individual shape reference
# ---------------------------------------------------------------------------

def _section_shape_samples(items):
    """Section C: Key shapes laid out in a tight row."""
    Y = 9728
    X0 = 1024
    SP = 256

    # Wall shapes
    walls = [622, 690, 691, 565, 75, 199, 145, 148, 155, 704, 705]
    for i, sid in enumerate(walls):
        _place(items, X0 + i * SP, Y, 0, sid, frame=0)

    # Roof shapes
    roofs = [412, 271, 220, 162, 164, 240, 37, 77, 661, 9, 34, 335]
    for i, sid in enumerate(roofs):
        _place(items, X0 + i * SP, Y + 512, 0, sid, frame=0)
        _place(items, X0 + i * SP, Y + 768, 8, sid, frame=0)  # elevated

    # Doors
    doors = [68, 69, 114, 174, 505, 288]
    for i, sid in enumerate(doors):
        _place(items, X0 + i * SP, Y + 1280, 0, sid, frame=0)

    # Roof edge pieces
    edges = [647, 648, 353, 354, 355, 356, 45, 84, 211, 212]
    for i, sid in enumerate(edges):
        _place(items, X0 + i * SP, Y + 1792, 0, sid, frame=0)


# ---------------------------------------------------------------------------
# Section D: Roof frame sweep — all frames for key roof shapes
# ---------------------------------------------------------------------------

def _section_roof_frame_sweep(items):
    """Section D: Every frame (0–49) of roof/floor shapes for visual ID.

    Walk south from Section C. Each row is one shape, columns are frames 0–49.
    Shapes tested: 412 (main roof), 271 (flat roof), 220 (floor/roof),
                   9 (floor tile), 162, 164 (peaked roofs).
    Also includes wall panel frames: 690, 691 (wooden walls).

    Teleport: MainActor::teleport 22 4096 12288 0
    """
    Y0 = 12288
    X0 = 1024
    COL_SP = 192   # spacing between frames (columns)
    ROW_SP = 512   # spacing between shapes (rows)

    shapes_to_sweep = [412, 271, 220, 9, 162, 164, 690, 691, 647, 648]

    for row, sid in enumerate(shapes_to_sweep):
        y = Y0 + row * ROW_SP
        for frame in range(50):
            x = X0 + frame * COL_SP
            _place(items, x, y, 0, sid, frame=frame)


# ---------------------------------------------------------------------------
# Section E: Cloud City shapes — white/gold palette candidates
# ---------------------------------------------------------------------------

def _section_cloud_city_shapes(items):
    """Section E: Shapes for Cloud City (white marble, gold, pillars).

    Walk south from Section D. Tests white/gold floor tiles, pillars,
    railings, and other candidates for the Cloud City aesthetic.

    Teleport: MainActor::teleport 22 4096 17408 0
    """
    Y0 = 17408
    X0 = 1024
    SP = 256

    # Pillar/column shapes (white pillars visible in screen11/12)
    pillars = [148, 155, 301, 302, 303, 304, 305, 306, 307, 308]
    for i, sid in enumerate(pillars):
        _place(items, X0 + i * SP, Y0, 0, sid, frame=0)

    # Floor/platform shapes — looking for white marble, gold tiles
    floors = [565, 271, 220, 9, 34, 37, 77, 162, 164, 240, 335, 661]
    for i, sid in enumerate(floors):
        for f in range(6):  # first 6 frames of each
            _place(items, X0 + i * SP, Y0 + 512 + f * 192, 0, sid, frame=f)

    # Railing/fence shapes (gold railings in screen12)
    railings = [704, 705, 75, 199, 353, 354, 355, 356, 45, 84]
    for i, sid in enumerate(railings):
        _place(items, X0 + i * SP, Y0 + 1792, 0, sid, frame=0)
        _place(items, X0 + i * SP, Y0 + 2048, 0, sid, frame=1)
        _place(items, X0 + i * SP, Y0 + 2304, 0, sid, frame=2)


# ---------------------------------------------------------------------------
# Section F: DD-007 spike — UnkEgg quality dispatch proof-of-life
# ---------------------------------------------------------------------------

# SF_UNKEGG is shape 73 and only shape 73 (verified against TYPEFLAG.DAT
# family data — see parse_typeflag.py). The engine instantiates any shape-73
# item as an Egg and, on Avatar approach, fires usecode event 7 ("hatch")
# ONCE on class (quality + 0x47F) — see Item::getEggScriptClass() and
# Egg::hatch() in scummvm-lv/engines/ultima/ultima8/world/{item,egg}.cpp
# (read-only reference; do not edit).
#
# quality = pinned EGGSPIKE class id (shared/build/lv_manifest.json) - 0x47F
#         = 1453 - 1151 = 302
# EGGSPIKE::hatch() (agents/usecode-compiler/src/lv-new/EGGSPIKE.UNK) barks
# "DD-007 SPIKE: the egg hatched." on approach.
DD007_SPIKE_QUALITY = 302

# npcNum packs the hatch trigger box: x range = high nibble, y range = low
# nibble (Egg::getXRange/getYRange, egg.h). 0x44 = x range 4, y range 4 —
# the engine's EggHatcherProcess multiplies each nibble by 32 world units
# (range_mul, egg_hatcher_process.cpp), so this is a +/-128 unit box
# centered on the egg.
DD007_SPIKE_NPCNUM = 0x44


def _section_dd007_spike(items):
    """Section F: one shape-73 UnkEgg for the DD-007 spike (PLAN.md 2.1/2.2).

    Placed well clear of Section E (which ends at y=19712) so its (empty,
    invisible) footprint doesn't interact with any other gallery item.

    Verification: MainActor::teleport 22 4096 19840 0 then walk south/east
    toward (4096, 20096) — crossing into the +/-128 unit box hatches the
    egg once and barks "DD-007 SPIKE: the egg hatched."
    """
    x, y, z = 4096, 20096, 0
    items.append(MapItem(
        x=x, y=y, z=z,
        shape=SHAPE_PLACEHOLDER_INVISIBLE_EGG,  # 73 = SF_UNKEGG
        frame=0,
        quality=DD007_SPIKE_QUALITY,
        npcnum=DD007_SPIKE_NPCNUM,
    ))
    print(f"  DD-007 spike egg: shape=73 quality={DD007_SPIKE_QUALITY} "
          f"npcnum=0x{DD007_SPIKE_NPCNUM:02X} at ({x},{y},{z})")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_shape_gallery():
    """Build Map 22 shape gallery. Returns list[MapItem]."""
    shapes = load_typeflag()
    print("Building Shape Gallery (Map 22)...")

    items = []

    # Terrain: 16x40 chunks (extended south for new sections)
    print("  Terrain base...")
    items.extend(generate_terrain_grid(0, 0, 16, 40, 40))

    print("  Section A: Tenebrae building copies...")
    _section_tenebrae_copies(items)

    print("  Section B: Test huts...")
    _section_test_huts(items)

    print("  Section C: Shape samples...")
    _section_shape_samples(items)

    print("  Section D: Roof frame sweep (frames 0–49)...")
    _section_roof_frame_sweep(items)

    print("  Section E: Cloud City shapes...")
    _section_cloud_city_shapes(items)

    print("  Section F: DD-007 spike (UnkEgg quality dispatch)...")
    _section_dd007_spike(items)

    # Arrival teleport
    items.append(MapItem.teleporter(
        x=4096, y=2048, z=0,
        teleport_id=250, dest_npc=250, dest_map=22))

    print(f"\n  Gallery total: {len(items)} items")
    return items


if __name__ == '__main__':
    items = build_shape_gallery()
    globs = sum(1 for i in items if i.is_glob_egg)
    print(f"\nMap {MAP_SLOT}: {len(items)} items ({globs} glob eggs)")

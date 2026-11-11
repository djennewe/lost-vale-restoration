# U8 Shape Catalog — Globs and Type Flags

Analysis of GLOB.FLX and TYPEFLAG.DAT from the GOG Ultima 8 Gold Edition.

## GLOB.FLX Overview

| Metric | Value |
|--------|-------|
| Total entries | 3,072 |
| Non-empty entries | 2,129 |
| Total items across all globs | 44,659 |
| Average items per non-empty glob | ~21 |

### Glob Size Distribution

| Items per Glob | Count | Notes |
|----------------|-------|-------|
| 0–4 | 625 | Empty or single-item globs |
| 5–9 | 12 | Small prefabs |
| 10–14 | 40 | Small terrain tiles |
| 15–19 | 547 | **Most common — standard 16-item terrain tiles** |
| 20–29 | 366 | Medium prefabs |
| 30–49 | 341 | Large structures |
| 50–79 | 150 | Complex structures |
| 80–124 | 34 | Very large compound structures |

The 16-item glob (547 instances) is the standard terrain tile — a 4x4 grid of
ground shapes filling one 512x512 chunk.

### Glob Record Format

```
Offset  Size  Type    Field
------  ----  ------  -----
0x00    2     uint16  itemcount
0x02    1     uint8   x          (relative offset, 0–255)
0x03    1     uint8   y          (relative offset, 0–255)
0x04    1     uint8   z          (relative offset, 0–255)
0x05    2     uint16  shape
0x07    1     uint8   frame
```

Items repeat `itemcount` times. Positions are **relative** to the glob egg's
position on the map. Total entry size = `2 + (itemcount * 6)` bytes.

### Most-Used Shapes in Globs

| Shape | Uses | Flags | Description |
|-------|------|-------|-------------|
| 35 | 2,766 | FIX,SOL,LND,DRW | Terrain with height detail |
| 3 | 2,702 | FIX,SOL,LND | Flat ground |
| 301 | 1,720 | FIX,SOL,LND,DRW | Terrain with height detail |
| 347 | 1,660 | FIX,SOL,SEA | Water surface |
| 334 | 1,306 | FIX,SOL,DRW | Wall/cliff face |
| 125 | 1,134 | FIX,SOL,LND,DRW | Rock face with detail |
| 128 | 1,124 | FIX,SOL,LND | Ground variant |
| 32 | 1,065 | FIX,SOL,LND,DRW | Cliff/wall (1x4 footpad) |
| 26 | 1,035 | FIX,SOL,LND,DRW | Cliff/wall (4x1 footpad) |
| 4 | 1,027 | FIX,SOL,LND,DRW | Ground with elevation |
| 29 | 939 | FIX,SOL,LND,DRW | Cliff/wall (1x1 footpad) |
| 409 | 916 | FIX,SOL,LND | Ground variant |
| 34 | 824 | FIX,SOL,LND,ROF | Roof/overhang terrain |
| 9 | 819 | FIX,SOL,LND,ROF | Roof terrain |
| 242 | 758 | FIX,SOL,LND | Ground variant |

### Wall/Cliff Shapes (Directional)

The engine uses directional wall shapes with footpads encoding orientation:

| Shape | Footpad | Direction |
|-------|---------|-----------|
| 26 | (4,1,6) | East-facing wall |
| 27 | (3,1,6) | East-facing (shorter) |
| 28 | (2,1,6) | East-facing (shortest) |
| 29 | (1,1,6) | Corner piece |
| 30 | (1,2,6) | South-facing (short) |
| 31 | (1,3,6) | South-facing (medium) |
| 32 | (1,4,6) | South-facing wall |

---

## TYPEFLAG.DAT Overview

| Metric | Value |
|--------|-------|
| Total shapes | 2,048 |
| Bytes per entry | 8 |
| File size | 16,384 bytes |

### Shape Categories

| Category | Count | SI Flags | Description |
|----------|-------|----------|-------------|
| Terrain (land) | 206 | FIX,SOL,LND | Flat ground, raised ground, slopes |
| Terrain (sea) | 14 | FIX,SOL,SEA | Water tiles, rivers, lava |
| Walls/Cliffs | 89 | FIX,SOL,DRW | Vertical surfaces with draw-order |
| Roofs | 36 | FIX,ROF | Overhead tiles (huts, caves) |
| Containers | 73 | SOL (family=6) | Chests, bags, barrels, crates |
| Quality items | 60 | SOL (family=1) | Doors, keys, levers, special items |
| Weapons | 15 | equip=6 | Swords, axes, bows, etc. |
| Armour | 12 | equip=1-5 | Shields, helmets, body armour |
| Damaging | 25 | DMG | Traps, lava, spikes |
| Decorations | 1,466 | SOL | Furniture, flora, props, rocks |
| Non-solid | 48 | — | Overlays, effects, translucent |
| Eggs | 4 | — | Glob/Teleport/Monster/Standard |

### Special Shape Numbers

| Shape | Family | Purpose |
|-------|--------|---------|
| 2 | SF_GLOBEGG | Glob expansion marker |
| 73 | SF_UNKEGG | Standard trigger egg |
| 500 | SF_MONSTEREGG | Monster spawner |
| 508 | SF_TELEPORTEGG | Teleport trigger/destination |

### Large Footpad Shapes (4x4+)

161 shapes have a 4x4 or larger footpad, suitable for terrain tiling:

| Footpad | Count | Typical Use |
|---------|-------|-------------|
| 4x4 | 95 | Standard ground tiles |
| 8x8 | 12 | Large platform/roof tiles |
| 4x4+z | 26 | Raised ground with height |
| 5x5+ | 28 | Large structures, platforms |

### Flag Combinations

| Flags | Count | Meaning |
|-------|-------|---------|
| FIX,SOL | 814 | Standard fixed solid item |
| FIX,SOL,LND | 137 | Walkable terrain |
| FIX,SOL,LND,DRW | 69 | Terrain with draw-order (cliffs) |
| FIX,SOL,DRW | 20 | Non-terrain walls |
| FIX,SOL,LND,ROF | 17 | Terrain with roof behavior |
| FIX,SOL,ROF | 14 | Roof tiles |
| SOL | 651 | Movable solid items |
| FIX | 40 | Fixed non-solid (decorative) |
| (none) | 286 | Non-fixed, non-solid |

### Door Shapes (Family = SF_QUALITY)

60 shapes with family=1 (SF_QUALITY). Key door shapes:

| Shape | Footpad | Notes |
|-------|---------|-------|
| 68 | (1,4,5) | Door (east-facing) |
| 69 | (4,1,5) | Door (south-facing) |
| 114 | (4,4,5) | Large door/gate |
| 135 | (1,4,5) | Door variant |
| 136 | (1,4,0) | Low door/gate |
| 194 | (4,1,5) | Door variant |

The `quality` field on SF_QUALITY items serves as a key/lock identifier.

### Sea/Water Shapes

| Shape | Footpad | Notes |
|-------|---------|-------|
| 57 | (6,5,2) | Large water tile |
| 63 | (4,4,2) | Standard water |
| 72 | (4,4,3) | Deep water |
| 129 | (4,4,7) | Very deep water |
| 347 | (4,4,0) | Surface water (most common) |
| 669 | (8,8,0) | Large water surface |
| 710 | (8,8,0) | Large water surface variant |
| 738 | (4,4,0) | Water variant |

### Damaging Shapes

| Shape | Footpad | Notes |
|-------|---------|-------|
| 318 | (8,8,0) | Large damage area (lava?) |
| 385 | (7,7,9) | Large elevated damage zone |
| 435–438 | (4,4,1) | Flame/trap tiles |
| 636 | (4,4,0) | Ground-level damage |
| 685 | (3,3,10) | Tall damage column |

---

## Implications for Lost Vale

### Reusable Terrain Shapes

For the Lost Vale overworld (described as "once lush, now barren"), the most
relevant terrain shapes are:

1. **Ground tiles** (shapes 3, 6, 11, 128, 242, 409): Flat walkable terrain
2. **Cliff/wall tiles** (shapes 26–32, 125, 334, 301): Vertical boundaries
3. **Water tiles** (shapes 347, 669, 710): For the Lake area
4. **Roof tiles** (shapes 9, 34, 37, 77): For cave/overhang areas

### Reusable Structural Shapes

For Cloud City, dungeons, and interiors:
- **Containers** (73 shapes): Chests, barrels for loot placement
- **Doors** (60 SF_QUALITY shapes): Entry/exit points with lock mechanics
- **Damaging tiles** (25 shapes): For traps in the Elemental Dungeon

### Glob Reuse Strategy

The base game's 2,129 globs provide extensive terrain variety. For Lost Vale:
- Standard terrain globs can be reused directly (e.g., 16-item ground tiles)
- New globs may be needed for Cloud City's unique architecture
- The glob system allows efficient terrain tiling — ~16 items per chunk
- Existing cave/dungeon globs can be reused for the Elemental Dungeon

### Available Glob Slots

Of 3,072 total glob entries, 943 are empty and available for new prefabs.

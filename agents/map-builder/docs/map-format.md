# Ultima 8 Map Format Specification

Reverse-engineered from the Pentagram engine source code (`pentagram-u8/pentagram`)
and verified against the GOG Ultima 8 Gold Edition data files.

## Overview

U8 maps are composed of three interlocking systems:

1. **FIXED.DAT** — A FLX archive containing 256 map slots. Each slot holds a flat
   array of 16-byte item records describing every permanent object on that map.
2. **GLOB.FLX** — A FLX archive of 3,072 prefab templates ("globs"). Glob eggs in
   FIXED.DAT reference these by index; the engine expands them at load time.
3. **TYPEFLAG.DAT** — A flat binary file with 2,048 entries (8 bytes each). Each
   entry describes the properties of one shape number: physics flags, family type,
   footpad dimensions, animation, weight, and volume.

The engine (Pentagram/ScummVM) loads maps into a 64x64 chunk grid. Each chunk is
512 world units on a side, giving a total coordinate space of **32,768 x 32,768**
world units per map.

---

## 1. FIXED.DAT — Map Item Archive

### File Structure

FIXED.DAT is a standard U8 FLX archive:

| Region | Offset | Size | Description |
|--------|--------|------|-------------|
| Title | 0x00 | 82 bytes | ASCII title, padded with 0x1A |
| Reserved | 0x52 | 2 bytes | — |
| Entry count | 0x54 | 4 bytes | uint32 LE — always 256 |
| Reserved | 0x58 | 40 bytes | — |
| Index table | 0x80 | 2048 bytes | 256 x (uint32 offset, uint32 size) |
| Data | 0x880+ | variable | Concatenated map data blobs |

Each of the 256 index entries points to a map's item data. Empty maps have
offset=0 and size=0.

**Verified against GOG data:**
- File size: 1,403,824 bytes (1,370.9 KB)
- Entry count: 256
- Non-empty maps: 42
- All non-empty entries have size divisible by 16 (no partial records)

### Item Record Format (16 bytes)

Each item in a map is stored as a fixed 16-byte record:

```
Offset  Size  Type    Field       Description
------  ----  ------  ----------  -----------
0x00    2     sint16  x           X coordinate (world units) or container depth
0x02    2     sint16  y           Y coordinate (world units)
0x04    1     sint8   z           Z coordinate (height)
0x05    2     uint16  shape       Shape number (indexes into U8SHAPES.FLX + TYPEFLAG.DAT)
0x07    1     uint8   frame       Frame number within the shape
0x08    2     uint16  flags       Item flags (runtime state)
0x0A    2     uint16  quality     Multi-purpose field (see below)
0x0C    1     uint8   npcnum      NPC number (for eggs and actors)
0x0D    1     uint8   mapnum      Map number (for cross-map references)
0x0E    2     uint16  next        Linked-list pointer (unused in disk format)
```

Source: `Map::loadFixedFormatObjects()` in `world/Map.cpp`

### Coordinate System

- **X, Y**: Signed 16-bit integers in world units (0–32,767 typical range)
- **Z**: Signed 8-bit integer representing height (-128 to +127)
- **Chunk mapping**: `chunk_x = x / 512`, `chunk_y = y / 512` (64 chunks per axis)
- **Isometric**: The engine renders in an isometric projection; X increases right,
  Y increases down-right, Z increases upward

### Container Nesting

Items can be placed inside containers using a stack-based encoding in the X field:

1. When a **container item** (family = SF_CONTAINER) is encountered, it is pushed
   onto a container stack and the nesting depth increments.
2. Subsequent items with X values matching the current nesting depth are placed
   **inside** the container at the top of the stack.
3. When X decreases, containers are popped from the stack until depths match.
4. Items at depth 0 (X is a normal world coordinate) are placed directly on the map.

```
// Pentagram pseudocode
while (contdepth != x && contdepth > 0) {
    cont.pop();
    contdepth--;
}
if (contdepth > 0) {
    cont.top()->addItem(item);
} else {
    itemlist.push_back(item);
}
if (family == SF_CONTAINER) {
    cont.push(item);
    contdepth++;
}
```

### Quality Field Semantics

The `quality` field has different meanings depending on the item's shape family:

| Family | quality meaning |
|--------|----------------|
| SF_GENERIC (0) | Unused (typically 0) |
| SF_QUALITY (1) | Arbitrary quality value (e.g., door lock IDs) |
| SF_QUANTITY (2) | Stack count |
| SF_GLOBEGG (3) | Glob index into GLOB.FLX |
| SF_UNKEGG (4) | Egg-specific parameter |
| SF_CONTAINER (6) | Container lock/key ID |
| SF_MONSTEREGG (7) | Monster shape + spawn parameters (packed) |
| SF_TELEPORTEGG (8) | Teleport destination ID |
| SF_REAGENT (9) | Quantity |

### Item Flags

The `flags` field contains runtime state bits. Common values observed:

| Bit | Hex | Meaning |
|-----|-----|---------|
| 0 | 0x0001 | FLG_FAST (in active area) |
| 10 | 0x0400 | FLG_GUMP (has gump open) — observed on some eggs |

(Most flags are runtime-only and stored as 0x0000 in FIXED.DAT.)

### Extended Flags (Engine-Internal)

The engine adds extended flags during loading:

- **EXT_FIXED**: Item is from FIXED.DAT (permanent, not dynamic)
- **EXT_INCURMAP**: Item is registered in the current map's chunk grid
- **EXT_LERP_NOPREV**: Freshly created item (no interpolation history)

These are not stored in the disk format.

---

## 2. GLOB.FLX — Prefab Templates

### File Structure

GLOB.FLX is a standard FLX archive containing prefab item groups.

**Verified against GOG data:**
- File size: 296,916 bytes (290.0 KB)
- Entry count: 3,072
- Non-empty entries: 2,129
- Total items across all globs: 44,659

### Glob Record Format

Each glob entry starts with an item count, followed by 6-byte item records:

```
Offset  Size  Type    Field       Description
------  ----  ------  ----------  -----------
0x00    2     uint16  itemcount   Number of items in this glob
0x02    1     uint8   x           Relative X offset (0–255)
0x03    1     uint8   y           Relative Y offset (0–255)
0x04    1     uint8   z           Relative Z offset (0–255)
0x05    2     uint16  shape       Shape number
0x07    1     uint8   frame       Frame number
```

Items repeat `itemcount` times starting at offset 0x02. Total entry size =
`2 + (itemcount * 6)` bytes.

Source: `MapGlob::read()` in `world/MapGlob.cpp`

### How Globs Are Expanded

When the engine encounters a **glob egg** (shape with family SF_GLOBEGG) in
FIXED.DAT:

1. The egg's `quality` field is the glob index into GLOB.FLX
2. The engine looks up the glob template by index
3. Each glob item is instantiated at the **egg's position + the item's relative
   offset**
4. The glob egg itself is not rendered — it exists only as a placement marker

Globs are the primary mechanism for terrain tiling. In Map 8 (Plateau), 1,414 out
of 4,306 items are glob eggs — they define the ground terrain.

### Glob Placement Grid

Glob eggs in FIXED.DAT are typically placed on a 512-unit grid (matching chunk
boundaries):

```
(511, 511)  (1023, 511)  (1535, 511)  ...
(511, 1023) (1023, 1023) (1535, 1023) ...
```

The most-used globs in Map 8:
- Glob 1757: 298 instances (primary terrain tile)
- Glob 2603: 223 instances (secondary terrain)
- Glob 262: 91 instances
- Glob 2632: 83 instances
- Glob 397: 79 instances

---

## 3. TYPEFLAG.DAT — Shape Properties

### File Structure

A flat binary file with no header. Each shape number (0–2047) has an 8-byte entry.

**Verified against GOG data:**
- File size: 16,384 bytes (exactly 2,048 x 8)
- Entries: 2,048

### Record Format (8 bytes per shape, U8 format)

```
Byte 0: Physics flags (low byte)
  Bit 0 (0x01): SI_FIXED    — Item is fixed/immovable
  Bit 1 (0x02): SI_SOLID    — Item is solid (collision)
  Bit 2 (0x04): SI_SEA      — Water tile
  Bit 3 (0x08): SI_LAND     — Land tile
  Bit 4 (0x10): SI_OCCL     — Occludes items behind it
  Bit 5 (0x20): SI_BAG      — Can hold items (bag-like)
  Bit 6 (0x40): SI_DAMAGING — Damages on contact
  Bit 7 (0x80): SI_NOISY    — Produces sound when stepped on

Byte 1: More flags (low nibble) + family (high nibble)
  Bit 0 (0x01): SI_DRAW     — Has special draw order
  Bit 1 (0x02): SI_IGNORE   — Ignored by pathfinder
  Bit 2 (0x04): SI_ROOF     — Is a roof tile
  Bit 3 (0x08): SI_TRANSL   — Semi-transparent
  Bits 4-7:     family       — Shape family (see SFamily enum)

Byte 2: Equipment type (low nibble) + X footpad (high nibble)
  Bits 0-3: equiptype (0=none, 1=shield, 2=arm, 3=head, 4=body, 5=legs, 6=weapon)
  Bits 4-7: x footpad dimension

Byte 3: Y footpad (low nibble) + Z footpad (high nibble)
  Bits 0-3: y footpad dimension
  Bits 4-7: z footpad dimension (height)

Byte 4: Animation type (low nibble) + animation data (high nibble)
  Bits 0-3: animtype
  Bits 4-7: animdata

Byte 5: Unknown (low nibble) + extra flags (high nibble)
  Bits 0-3: unknown
  Bit 4 (0x10): SI_EDITOR   — Editor-only item
  Bit 5 (0x20): SI_EXPLODE  — Explodes on destruction
  Bit 6 (0x40): SI_UNKNOWN46
  Bit 7 (0x80): SI_UNKNOWN47

Byte 6: Weight (0–255)

Byte 7: Volume (0–255)
```

Source: `TypeFlags::load()` and `ShapeInfo.h`

### Shape Family Types (SFamily enum)

| Value | Name | Description |
|-------|------|-------------|
| 0 | SF_GENERIC | Standard items (terrain, walls, decorations) |
| 1 | SF_QUALITY | Items with meaningful quality value |
| 2 | SF_QUANTITY | Stackable items (arrows, reagents) |
| 3 | SF_GLOBEGG | Glob expansion egg |
| 4 | SF_UNKEGG | Standard trigger egg |
| 5 | SF_BREAKABLE | Breakable containers |
| 6 | SF_CONTAINER | Containers (chests, bags) |
| 7 | SF_MONSTEREGG | Monster spawn egg |
| 8 | SF_TELEPORTEGG | Teleport destination/trigger egg |
| 9 | SF_REAGENT | Reagent items |
| 15 | SF_15 | Unknown (7 shapes have this in base game) |

**Family distribution in base game (2,048 shapes):**

| Family | Count | Notes |
|--------|-------|-------|
| GENERIC | 1,901 | Terrain, walls, decorations, props |
| QUALITY | 60 | Doors, keys, special items |
| QUANTITY | 1 | Shape for stackable items |
| GLOBEGG | 1 | Shape 2 only |
| UNKEGG | 1 | Shape for standard eggs |
| CONTAINER | 73 | Chests, bags, barrels |
| MONSTEREGG | 1 | Shape 500 only |
| TELEPORTEGG | 1 | Shape 508 only |
| REAGENT | 2 | Reagent items |
| UNK15 | 7 | Unknown purpose |

### Special Shape Numbers

| Shape | Family | Purpose |
|-------|--------|---------|
| 2 | SF_GLOBEGG | Glob egg (quality = glob index) |
| 500 | SF_MONSTEREGG | Monster spawn egg |
| 508 | SF_TELEPORTEGG | Teleport egg |

---

## 4. Map Management (Engine)

### Map Grid

```
MAP_NUM_CHUNKS  = 64
mapChunkSize    = 512     (U8; Crusader uses 1024)
Total map size  = 64 × 512 = 32,768 world units per axis
```

Items are placed into a 2D grid of chunk lists:
```cpp
items[chunk_x][chunk_y]  // where chunk = coordinate / 512
```

### Map Count and Numbering

The engine supports 256 maps (indices 0–255). Base game U8 uses 42 of these:

| Map | Items | Description |
|-----|-------|-------------|
| 3 | 1,835 | — |
| 4 | 4,377 | — |
| 5 | 2,691 | — |
| 6 | 2,908 | — |
| 7 | 2,230 | — |
| **8** | **4,306** | **Plateau (LV entry point)** |
| 12 | 2,410 | — |
| 14 | 2,956 | — |
| 15 | 2,400 | — |
| 16 | 1,052 | — |
| 20 | 596 | — |
| 21 | 2,665 | — |
| 24 | 558 | — |
| 25 | 1,044 | — |
| 26 | 1,355 | — |
| 28 | 1,369 | — |
| 29 | 150 | — |
| 31 | 3,663 | — |
| 33 | 131 | — |
| 37 | 5,054 | — |
| 39 | 4,624 | — |
| 40 | 1,963 | — |
| 41 | 3,859 | — |
| 43 | 784 | — |
| 44 | 2,523 | — |
| 45 | 1,276 | — |
| 46 | 385 | — |
| 47 | 2,442 | — |
| 49 | 4,447 | — |
| 50 | 4,555 | — |
| 51 | 2,507 | — |
| 54 | 1,729 | — |
| 56 | 182 | — |
| 57 | 4,257 | — |
| 62 | 5,715 | — |
| 63 | 752 | — |
| 159 | 3 | Minimal (test?) |
| 200 | 36 | Small interior |
| 222 | 87 | Small interior |
| 223 | 1,233 | — |
| 243 | 14 | Minimal |
| 255 | 480 | — |

**Available for Lost Vale:** Maps 10, 11, 13, 17–19, 22–23, 27, 30, 32, 34–36,
38, 42, 48, 52–53, 55, 58–61, 64–158, 160–199, 201–221, 224–242, 244–254.
Map 10 is confirmed as the Lost Vale overworld from usecode analysis.

### Map Loading Sequence

```
1. World::switchMap(newmap)
2.   → GameData::getFixed()->get_datasource(newmap)   // get FLX entry
3.   → Map::loadFixed(datasource)                     // parse 16-byte records
4.     → Map::loadFixedFormatObjects(fixeditems, ds, EXT_FIXED)
5.   → CurrentMap::loadMap(map)                        // place into grid
6.     → CurrentMap::loadItems(fixeditems)
7.       → CurrentMap::addItem(item)                   // items[cx][cy].push_front()
8.       → EggHatcherProcess::addEgg(egg)              // register eggs
```

---

## 5. Egg System

Eggs are invisible trigger objects placed on maps. They are the primary mechanism
for map transitions, monster spawning, and scripted events.

### Teleport Eggs (Shape 508)

Two roles determined by the `frame` field:

| Frame | Role | Fields |
|-------|------|--------|
| 0 | **Destination** | quality bits 8-15 = destination map; npcnum = teleport ID; mapnum = target map |
| 1 | **Trigger** | quality = teleport ID to look up; triggers when Avatar enters range |

When the Avatar walks over a trigger egg (frame=1), the engine searches all maps
for a destination egg (frame=0) with a matching teleport ID, and moves the Avatar
to that location.

**Example from Map 8:**
```
Trigger:  shape=508 frame=1 pos=(14590,11210,48) quality=1
Dest:     shape=508 frame=0 pos=(14540,11004,48) quality=258 npc=51 map=8
```

### Monster Eggs (Shape 500)

Spawn monsters when the chunk they're in becomes active:

| Field | Meaning |
|-------|---------|
| quality | Packed: monster shape + spawn parameters |
| npcnum | Number of monsters to spawn (typically 1) |
| mapnum | Activity range or monster subtype ID |
| frame | Spawn behavior (0=normal, 1=respawn) |

### Glob Eggs (Shape 2)

Expand into prefab item groups at map load time (see Section 2).

---

## 6. Implications for Lost Vale Map Creation

### Creating New Maps

To add Lost Vale maps to FIXED.DAT:

1. **Choose map slots**: Use unoccupied indices. Map 10 is confirmed for the LV
   overworld. Other LV maps can use any of the 200+ available slots.
2. **Build item arrays**: Create 16-byte records for each item, including:
   - Terrain glob eggs (shape 2) on the 512-unit grid
   - Structural items (walls, floors, decorations)
   - Teleport eggs for map transitions
   - Monster eggs for creature spawns
   - Containers with nested items
3. **Register globs**: If new terrain patterns are needed, add entries to GLOB.FLX.
   Existing globs can be reused — the base game has 2,129 defined patterns.
4. **Update FIXED.DAT**: Insert new map data at an unused FLX index, updating the
   FLX index table to point to it.

### Map 8 Modification (Double Doors)

The LV entry requires modifying Map 8 to add:
- A teleport trigger egg near the double doors leading to the new area
- A corresponding destination egg in the new Beyond Double Doors map
- Optionally: a door item (SF_QUALITY family) with lock/key quality

Map 8 currently has 4,306 items across 152 unique shapes. The double door
modification adds a small number of items to an existing, well-populated map.

### Transition Egg Pattern

For each map-to-map transition, place a **pair** of eggs:

```
Map A (source):
  Trigger egg:  shape=508, frame=1, quality=<unique_id>, pos=<door_location>

Map B (destination):
  Dest egg:     shape=508, frame=0, quality=<packed>, npc=<unique_id>,
                mapnum=<target_map>, pos=<arrival_location>
```

### Coordinate Design Notes

- Typical terrain items span 1–4 footpad units (32–128 world units)
- Indoor areas use z=0 as floor level; outdoor varies with terrain
- Negative z values exist (underground, caves, water)
- The 32,768-unit range per axis provides substantial space for complex maps

---

## References

- Pentagram source: `world/Map.cpp`, `world/ItemFactory.cpp`, `world/CurrentMap.cpp`,
  `world/MapGlob.cpp`, `world/World.cpp`, `graphics/ShapeInfo.h`,
  `graphics/TypeFlags.cpp`, `games/GameData.cpp`
- Repository: https://github.com/pentagram-u8/pentagram
- FLX format: `agents/usecode-disasm/docs/usecode-format.md`
- Verified against: GOG Ultima 8 Gold Edition (DOS data files)

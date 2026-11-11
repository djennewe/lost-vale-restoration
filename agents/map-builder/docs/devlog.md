# map-builder — Devlog

## Session 1 — 2026-03-21 — Track A: Map Format Research

### Tasks Completed

**A1: U8 Map Format Research** — DONE
- Fetched and analyzed 7 Pentagram source files (Map.cpp, ItemFactory.cpp,
  World.cpp, CurrentMap.cpp, MapGlob.cpp, ShapeInfo.h, GameData.cpp, TypeFlags.cpp)
- Documented the complete FIXED.DAT → item record → chunk grid pipeline
- Key finding: 16-byte item records, 64x64 chunk grid, 512 units/chunk
- Output: `docs/map-format.md`

**A2: FIXED.DAT Analysis** — DONE (combined with A1)
- Verified FLX structure against GOG data: 256 entries, 42 non-empty maps
- Parsed Map 8 (Plateau) in detail: 4,306 items, 1,414 glob eggs, 152 shapes
- Found all teleport egg pairs and monster eggs
- Confirmed all entries have size divisible by 16 (no format anomalies)
- Output: appended to `docs/map-format.md`

**A3: Base Game Map Catalog** — DONE
- Parsed all 42 non-empty maps with item counts, bounding boxes, shapes
- Traced full teleport connectivity graph between maps
- Identified Map 40 as central hub (17 teleport eggs, connects 4+ maps)
- Confirmed Map 10 is empty and available for LV overworld
- Mapped size categories for reference during LV map design
- Output: `docs/base-game-maps.md`

**A4: GLOB.FLX + TYPEFLAG.DAT Analysis** — DONE
- GLOB.FLX: 3,072 entries, 2,129 non-empty, 44,659 total items
- Standard terrain tile = 16 items per glob (547 instances at this size)
- TYPEFLAG.DAT: 2,048 shapes, 8 bytes each, full flag/family decode
- Categorized all shapes: 206 terrain, 89 walls, 73 containers, 60 doors, etc.
- Identified top 25 most-used shapes in globs
- Output: `docs/shape-catalog.md`

**A5: Asset Reuse Plan** — DONE
- Cross-referenced Art List v2.5 items, locations, creatures against shape catalog
- Terrain for all LV areas achievable with existing shapes
- Identified 10 new art requirements, ranked by priority
- Core items (keys, doors, books, potions) all reusable
- Main gaps: Shield halves, god statues, Water Zombie, Harpie, cloud tiles
- Output: `docs/asset-reuse-plan.md`

### Key Findings

1. **Map 10 confirmed available** — empty slot, confirmed by usecode MapLostVale
2. **214 map slots available** — more than enough for the expansion
3. **Extensive shape reuse possible** — the "barren valley" aesthetic maps well
   to existing rocky terrain shapes
4. **943 empty glob slots** — room for new terrain patterns
5. **Container nesting works via X-coordinate encoding** — documented the exact
   stack-based mechanism for placing items inside containers
6. **Teleport egg system is simple** — just TRIGGER/DEST pairs with matching IDs

### Infrastructure Set Up

- Copied `u8_flex.py` from usecode-disasm agent to `agents/map-builder/src/`
- All format specs cross-verified against actual GOG data files

### Next: Track B

Moving to Track B (Map Design). Starting with B1 (map-level overview) which
requires the format knowledge from Track A plus the corpus files.

---

## Session 1 (continued) — Track B: Map Design

### Tasks Completed

**B1: Map-Level Overview** — DONE
- Assigned map slots: 9 (Galjeron), 10 (LV overworld), 11 (dungeon),
  13 (cliffs), 17 (Cloud City), 18 (temple)
- Defined 12 primary transitions + 2 optional (Pagan return)
- Reserved teleport IDs 200–213 (base game uses 0–105)
- Created full connection graph and production order
- Output: `docs/map-design-overview.md`

**B2: Map 8 Modification (Plateau Entry)** — DONE
- Analyzed Map 8 structure: 4,306 items, 152 shapes, 15 teleport eggs
- Documented double door modification approach (additive, ~4 items)
- Key mechanism: SF_QUALITY door + matching key
- Noted blocker: exact door coordinates need in-game verification
- Output: `docs/map-08-plateau-entry.md`

**B3: Map 9 (Galjeron's Chamber)** — DONE
- Small interior design: ~8×8 chunks, ~300 items
- Three zones: entry passage, main chamber, deeper passage
- Galjeron's body + journal + guardian creature placement
- Output: `docs/map-09-galjeron-chamber.md`

**B4: Map 11 (Elemental Dungeon)** — DONE
- Hub-and-spoke design: ~40×40 chunks, ~3,500 items
- Central hub + 4 elemental sections (Earth, Air, Fire, Water)
- Four Pillars exit mechanism + teleporter pad
- Non-linear design: sections tackled in any order
- 17–25 monster eggs across all sections
- Output: `docs/map-11-elemental-dungeon.md`

**B5: Map 10 (Lost Vale Overworld)** — DONE
- Largest map: ~50×50 chunks, ~4,000 items
- 10 sub-zones with coordinate assignments
- 16 NPCs placed across two villages + Ezrekal's dwelling
- The Lake (Water Zombies), Test Area (PLNTST), Sacred Circle
- Cloud Cliffs approach (locked gate), Temple approach
- Optional: Birthplace of Moriens ruins
- Output: `docs/map-10-lost-vale.md`

**B6: Maps 13 + 17 (Cloud Areas)** — DONE
- Cloud Cliffs: ~10×25 chunks, vertical climb using full z-range
- 3–4 Harpie encounters on narrow ledges
- Cloud City: ~25×25 chunks, floating architecture
- Magnetic Obelisk puzzle (MAGNET), Shield halves + skeletons
- Collapsing ground hazards, deserted god quarters
- Output: `docs/map-13-17-cloud-areas.md`

**B7: Map 18 (Ancient Temple)** — DONE
- End-game map: ~12×15 chunks, ~800 items
- Outer hall (guardian/barrier), transition hall (Tiny Tar shrink)
- Inner sanctum: 3 gods in resin + altar for Shield
- FREE.UNK ceremony triggers god liberation
- 6 new art pieces needed (3 encased + 3 speaking god figures)
- Output: `docs/map-18-ancient-temple.md`

### Key Design Decisions

1. **Non-linear Elemental Dungeon** — all four sections accessible from
   central hub in any order
2. **Bi-directional transitions** — every connection has a return path
3. **Pagan return travel** — optional teleporter per Synopsis recommendation
4. **Sub-zones within maps** — all LV overworld locations on one map (Map 10)
   rather than splitting into multiple maps
5. **Teleport ID range 200+** — avoids conflicts with base game IDs 0–105

### Track B Summary

All 7 map areas now have comprehensive design documents with:
- Layout diagrams with zone definitions
- Coordinate assignments
- Item lists and estimates
- Teleport egg specifications
- Monster egg placement
- Key items and quest object placement
- Art requirements
- Dependencies and blockers

Total estimated items across all new maps: ~11,800
Total new maps: 6 (plus Map 8 modification)
Total teleport egg pairs: 7 primary + 1 optional

---

## Session 1 (continued) — Track C: Prototype Tools (Stretch Goal)

### Tasks Completed

**C1: FIXED.DAT Reader/Writer** — DONE
- Built `src/u8_map.py` extending the FLX reader with map-specific classes
- `MapItem` class: 16-byte record parsing/serialization
- Factory methods: glob_egg(), teleport_trigger(), teleport_dest(), monster_egg()
- `MapArchive` class: load/save entire FIXED.DAT archives
- `generate_terrain_grid()` utility for chunk-aligned glob egg placement
- Verified against real FIXED.DAT: 42 maps, 87,603 items parsed correctly

**C2: Map Item Placer** — DONE (integrated into u8_map.py)
- MapItem factory methods serve as the item placer
- generate_terrain_grid() handles terrain tiling
- No separate tool needed — the API is sufficient

**C3: Test Map for Map 10** — DONE
- Generated `shared/maps/FIXED_TEST.DAT` with all 42 original maps + Map 10
- Map 10 test content: 122 items
  - 100 terrain glob eggs (10x10 chunk grid, glob 1757)
  - 8 teleport eggs (4 transitions: dungeon, cliffs, temple, Pagan)
  - 4 placed decorations (stone marker, rocks)
  - 9 water tiles (3x3 lake)
  - 1 monster egg (water zombie placeholder)
- Verified: reload produces identical item counts

**C4: ScummVM Testing Instructions** — DONE
- Step-by-step guide for testing in ScummVM
- Debugger commands for teleporting to Map 10
- Transition testing checklist
- Python code examples for custom map generation
- Output: `docs/scummvm-testing.md`

### Track C Summary

All stretch goals completed. The prototype toolchain can:
1. Read any FIXED.DAT file and parse all map items
2. Create new maps with terrain, transitions, decorations, and monsters
3. Write valid FIXED.DAT files that include both original and new maps
4. Generate terrain grids aligned to the 512-unit chunk system

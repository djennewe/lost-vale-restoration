# Agent: map-builder — Memory

> **FROZEN 2026-03-21 — per-agent history, not current project state (L18).**
> This agent's work is COMPLETE: Phase 2 (map design and format spec). The file records how that work was
> done and what was decided; it has not been maintained since.
>
> Live status is `TODO.md`; strategy is `PLAN.md`; the review-driven
> queue is `docs/reviews/2026-07-19-improvement-plan.md`.


## Identity
I am the **map-builder** agent for the Ultima: The Lost Vale restoration project.
My job is Phase 2: designing new maps for the Lost Vale expansion using existing
U8 tile assets and the ScummVM/Pentagram engine capabilities.
I work in `agents/map-builder/` and write outputs to `shared/maps/` (to be created).
I do not touch other agents' directories.

## My Scope
Design all new game maps needed for the Lost Vale expansion, starting from the
double-door entry point on the Plateau (map 8 in the base game). Maps must be
faithful to the design documents, usecode analysis, and art notes in the corpus.

## Current Status
- **Phase:** COMPLETE — Tracks A, B, C all done
- **Branch:** `agent/map-builder`
- **Last commit:** Track C complete (prototype tools + test map)
- **Prerequisites:** Phase 0 (corpus-builder: COMPLETE) and Phase 1 (usecode-disasm: COMPLETE)

## Task Queue

### Track A: Map Format Research (no dependencies — start immediately)

| Task | Status | Description | Output |
|------|--------|-------------|--------|
| A1 | DONE | Research U8 map format from Pentagram source | `docs/map-format.md` |
| A2 | DONE | Analyze FIXED.DAT structure (combined with A1) | `docs/map-format.md` |
| A3 | DONE | Catalog base game maps — 42 maps, connectivity graph | `docs/base-game-maps.md` |
| A4 | DONE | GLOB.FLX (2,129 globs) + TYPEFLAG.DAT (2,048 shapes) | `docs/shape-catalog.md` |
| A5 | DONE | Art List v2.5 cross-reference + reuse plan | `docs/asset-reuse-plan.md` |

### Track B: Map Design (depends on Track A + corpus files in `shared/corpus/`)

| Task | Status | Description | Output |
|------|--------|-------------|--------|
| B1 | DONE | Map-level overview: slots, connections, transitions | `docs/map-design-overview.md` |
| B2 | DONE | Map 8 modification — double doors entry design | `docs/map-08-plateau-entry.md` |
| B3 | DONE | Galjeron's Chamber (Map 9) — interior design | `docs/map-09-galjeron-chamber.md` |
| B4 | DONE | Elemental Dungeon (Map 11) — 4 sections + pillars | `docs/map-11-elemental-dungeon.md` |
| B5 | DONE | Lost Vale overworld (Map 10) — 10 sub-zones, 16 NPCs | `docs/map-10-lost-vale.md` |
| B6 | DONE | Cloud Cliffs (Map 13) + Cloud City (Map 17) | `docs/map-13-17-cloud-areas.md` |
| B7 | DONE | Ancient Temple (Map 18) — shrine + god-freeing | `docs/map-18-ancient-temple.md` |

### Track C: Prototype Tools (stretch goal — attempt only after A1-A4 and B1+B5)

| Task | Status | Description | Output |
|------|--------|-------------|--------|
| C1 | DONE | FIXED.DAT reader/writer (MapArchive + MapItem) | `src/u8_map.py` |
| C2 | DONE | Map item placer (integrated into u8_map.py) | `src/u8_map.py` |
| C3 | DONE | Test map for Map 10 (122 items, terrain+transitions) | `shared/maps/FIXED_TEST.DAT` |
| C4 | DONE | ScummVM testing instructions | `docs/scummvm-testing.md` |

### Dependency Notes
- Track A: NO external dependencies. Start immediately.
- Track B: Depends on Track A for format understanding + corpus files.
- Track C: Stretch goal. Depends on A + B. Do NOT block completion on it.
- The FLX reader at `agents/usecode-disasm/src/u8_flex.py` should be COPIED to `agents/map-builder/src/`, not modified in place.

## Map Requirements

Derived from the questline, design documents, and usecode analysis.
Map numbers reference the base game (maps 0–9); Lost Vale maps start at 10+.

### Required Maps

#### 1. Entry: Double Doors on Plateau (map 8 modification)
- **Type:** Modification of existing map
- **Description:** The double doors in Bonecrusher's Cave on the Plateau are
  already present in the base game as locked, non-functional doors. The expansion
  must add: key puzzle to unlock, transition to Beyond Double Doors area.
- **Key items:** Key to Double Doors
- **References:** Plot v1.2 beat 3, Dino's Guide

#### 2. Beyond Double Doors / Galjeron's Chamber
- **Type:** New interior map or map section
- **Description:** Small chamber where Galjeron's dead body and journal are found.
  Synopsis suggests a guardian creature here. Connects to the Elemental Dungeon.
- **Key items:** Galjeron's Journal
- **References:** Plot v1.2 beat 4, Synopsis beat 4

#### 3. Elemental Dungeon
- **Type:** New map, 4-section structure
- **Description:** Dungeon divided into four elemental sections (Earth, Air, Fire,
  Water), each containing a talisman/gemstone. Four elemental pillars at the exit
  block the path to the Lost Vale — destroyed with opposite-element talismans.
- **Sub-areas:** Earth Section, Air Section, Fire Section, Water Section, Pillar Exit
- **Key items:** Talisman of Earth/Air/Fire/Water, Pillar Receptacles
- **Monsters:** Multi-elemental agent (proposed), section-specific elementals
- **Notes:**
  - Synopsis suggests teleporter pad at exit for quick return
  - "Build obstacles!" (Walk Through annotation)
  - Resource Schedule: maps assigned to Brian M. in May–June 1994
- **References:** Plot v1.2 beats 5-6, Synopsis, Art List v2.5

#### 4. Lost Vale Overworld (MapLostVale, map 10)
- **Type:** New exterior map
- **Description:** Hidden valley, once lush now barren. Two water sources, one per
  clan. Connects to: clan villages, Ezrekal's dwelling, test area, the lake,
  Cloud Cliffs approach, Sacred Circle, Ancient Temple.
- **Sub-areas:**
  - Clan Hoskuld Village (near one water source)
  - Clan Gunnar Village (near other water source)
  - Ezrekal's Dwelling (apart from both communities)
  - Test Area / Rite of Passage (PLNTST trigger location)
  - The Lake (water zombies, Passage Stone location)
  - Sacred Circle / Sacred Rock (Shield restoration ceremony)
- **Map number:** 10 (confirmed from Ragnar's schedule code referencing map 10)
- **Art notes:** "Barren is sometimes boring. I hope we're planning on using some
  cool fallen ruins." (Synopsis)
- **References:** Plot v1.2 beat 7, Discord analysis, usecode (MapLostVale)

#### 5. Cloud Cliffs
- **Type:** New map, vertical climb
- **Description:** Treacherous cliff path from the Lost Vale up to Cloud City.
  Bones of dead Zealans who attempted the climb. Home to the Harpie monster.
  Locked until the Avatar obtains the Key to the Clouds from Tjorvi.
- **Monsters:** Harpie
- **Key items:** Key to the Clouds (TypeCliffKey)
- **Usecode flags:** climbedCliffs, attemptedCliffs, agreeToClimb
- **Art notes:** Originally "Cliffs of Insanity" — renamed "Cloud Cliffs" in usecode
- **Notes:** Cliffs usecode was marked red X (never completed by Brian M.)
- **References:** Plot v1.2 beat 13, Discord analysis

#### 6. Cloud City
- **Type:** New map, floating/cloud architecture
- **Description:** Suspended city in the clouds, former home of the Zealan gods.
  Now deserted. The Avatar finds the message scroll and two Shield halves near
  the skeletons of Snori and Hoskuld/Flossie. Features a magnetic obelisk puzzle.
- **Key items:** Shield halves, Message Scroll, Magnetic Obelisk
- **Usecode:** MAGNET.UNK (magnetic puzzle), cloudCity flag
- **Art notes:**
  - "Bob's red stone architecture turned white and gold"
  - "Cloud-like terrain"
  - "Collapsing ground" (environmental hazard)
  - "Avatar dying in cloud terrain" sprite needed
- **Notes:** Maps assigned to Sheri G. in July (5 days), building globs by Lisa S. (3 days)
- **References:** Plot v1.2 beat 14, Art List v2.5, Sheri blog

#### 7. Ancient Temple / Shrine of the Ancient Ones
- **Type:** New interior map
- **Description:** Temple where the three Zealan gods (Felicitar, Doloras, Timyra)
  are imprisoned in amber-like resin ("like the shields in the movie Dune").
  Requires Tiny Tar potions to enter portions (shrink mechanic). Contains the
  altar where the restored Shield is placed. Ezrekal accompanies the Avatar.
- **Key items:** Restored Shield of the Ancients, Tiny Tar Potion
- **Usecode flags:** templeOpen, ezToTemple, godsFree, godsSpoke, getPowerAO
- **Art notes:** "Zealan God 1/2/3, encased in resin" and "speaking" variants
- **Notes:** End-game usecode mostly MISSING from snapshot — design from plot docs
- **References:** Plot v1.2 beats 17-18, Discord steps 17-21

### Map Design Constraints

- **Pitch Doc:** "approximately five new maps" — may have grown during development
- **Engine:** ScummVM Ultima 8 engine (absorbed Pentagram April 2020)
- **Tile assets:** Must use existing U8 tile set plus any new tiles we create
- **Travel:** Synopsis strongly recommends allowing travel back and forth between
  Pagan and the Lost Vale
- **Scale:** Total expansion was planned for approximately 4 months of development
  with a small team

## Completion Criteria
Maps are "done enough" when:
1. Map format documented with item record structure (Track A complete)
2. All 7 map areas have design documents with layout descriptions
3. All connection points between maps defined with map slot assignments
4. Tile asset requirements catalogued
5. STRETCH: At least one map has a programmatic prototype (Track C)
6. Root MEMORY.md Active Agents table updated

## Inputs I Consume
- `shared/corpus/plot-documents/` — all YAML files for quest structure
- `shared/corpus/usecode-index/` — usecode analysis and cross-reference
- `shared/corpus/GAP-ANALYSIS.md` — what's documented vs. needs design
- `shared/corpus/plot-documents/known-gaps.md` — specific missing content
- Base game map data from `shared/data/u8-install/` (when extracted)
- ScummVM Ultima 8 engine source for map format specifications

## Outputs I Produce
```
shared/maps/                          # TBD — map data and design docs
agents/map-builder/docs/
├── map-format.md                    # U8 map format specification
├── base-game-maps.md               # base game map catalog
├── shape-catalog.md                # glob and type flag documentation
├── asset-reuse-plan.md             # tile reuse analysis
├── map-design-overview.md          # overall map plan + connection graph
├── map-08-plateau-entry.md         # Map 8 double doors modification
├── map-XX-galjeron-chamber.md      # Galjeron's Chamber design
├── map-XX-elemental-dungeon.md     # Elemental Dungeon design
├── map-10-lost-vale.md             # Lost Vale overworld design
├── map-XX-cloud-areas.md           # Cloud Cliffs + Cloud City design
├── map-XX-ancient-temple.md        # Ancient Temple / Shrine design
└── devlog.md                       # session journal
```

## Devlog
See `agents/map-builder/docs/devlog.md` for session-by-session narrative.

## Last Updated
- By: coordinator
- Date: 2026-03-21 (activated with task queue)

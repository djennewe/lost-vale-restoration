# Map 11 — Elemental Dungeon

Design document for the four-section elemental dungeon connecting Galjeron's
Chamber (Map 9) to the Lost Vale overworld (Map 10).

## Overview

| Property | Value |
|----------|-------|
| Map slot | 11 |
| Type | New dungeon |
| Size | ~40×40 chunks (20,480×20,480 world units) |
| Estimated items | ~3,500 |
| Terrain style | Underground, four elemental themes |
| Entry | From Map 9 (Galjeron's Chamber) |
| Exit | To Map 10 (Lost Vale) via Four Pillars |

## Story Context

**Beats 5–6:** The Avatar enters a dungeon divided into four elemental sections.
Each contains a talisman. At the exit, four elemental pillars block the path to
the Lost Vale. Each pillar is destroyed with the opposite-element talisman.

**Synopsis:** "We need an NPC here — perhaps a guardian left behind by the Titans.
A multi-elemental agent who shows up throughout."

**Walk Through annotation:** "Build obstacles!"

## Layout

```
                    From Map 9
                   Teleport DEST
                        │
              ┌─────────┴─────────┐
              │                   │
              │   Entry Hall      │
              │   (introduction)  │
              │                   │
              │    ┌─────┐        │
              │    │ Hub │        │
              │    │     │        │
              │    └──┬──┘        │
              │    ╱  │  ╲        │
        ┌─────┴───╱───┼───╲──────┤
        │    ╱         │      ╲   │
   ┌────┴──┴─┐   ┌────┴────┐ ┌┴──┴────┐
   │  EARTH  │   │  FIRE   │ │  AIR   │
   │ Section │   │ Section │ │Section │
   │         │   │         │ │        │
   │  ⊕gem   │   │  ⊕gem   │ │ ⊕gem   │
   └─────────┘   └─────────┘ └────────┘
        │              │          │
        └──────────┐   │   ┌─────┘
                   │   │   │
              ┌────┴───┴───┴────┐
              │                 │
              │  WATER Section  │
              │                 │
              │     ⊕gem        │
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              │  Four Pillars   │
              │  ╔═══╗ ╔═══╗   │
              │  ║ E ║ ║ A ║   │
              │  ╚═══╝ ╚═══╝   │
              │  ╔═══╗ ╔═══╗   │
              │  ║ F ║ ║ W ║   │
              │  ╚═══╝ ╚═══╝   │
              │       │         │
              │  Teleporter Pad │
              └────────┬────────┘
                       │
              To Map 10 (Lost Vale)
              Teleport TRIGGER
```

## Zone Details

**Rebuilt 2026-09-15** (cleanup plan step 3, `build_map_11.py`). What the
map had: 421 ceiling tiles laid one per 512-unit chunk over every room (the
Fire section's at z=32, below head height), 48 wall reliefs standing loose
on floors, six chests and two chimneys as decoration, "platforms" and
"walkways" that were single tiles every 256 or 512 units. Now: no ceilings;
the entry hall, hub, Four Pillars chamber and pad in the temple's stone-wall
pair on flagstone (65), two courses, columns on plinths, lamps and
tapestries on the faces the projection shows — the pad gate three courses
(120, the sanctum's standard; `test_route_reach` gate coverage updated from
144); the cave sections in cave wall with cycled frames; Fire on scorched
earth (glob 480, shape 425) with lava-yellow lakes (glob 802, shape 409 —
walkable, the Plane of Fire's own ground) and dark raised causeways (70)
in a cross and a branch to the talisman, fire pits and flame tiles beside
them and never under them (asserted at build time); Air on grey rock slabs
(glob 397) with two three-tier terraces and stalactite spires hanging in
the dark, the Plane of Air's idiom; Water on damp flagstone with four real
islands, fungus, boulders and stalagmites — no water, because SEA tiles
drown (the 2026-07-04 finding) and lethal geometry is the gameplay queue's;
Earth with its talisman in a spire alcove and more of the cave. Every pin
— talismans, pillars, receptacles, boulders, teleports, seventeen monster
eggs — unmoved (`map_pins.json`). `test_route_reach` now floods with
SI_DAMAGING among the mover flags (stricter than the engine, whose Avatar
walks onto lava and burns) and proves all four talismans and the chamber
reachable that way. Hygiene row zero; entry, hub, Fire, pillars, Air and
Water shot in-engine at 640x400.

**The 1994 screenshots, 2026-10-17** (phase B of the screenshot
reconstruction; `docs/research/2026-10-16-screenshot-reconstruction/phaseB/map11/REPORT.md`).
Two published shots now stand in the map verbatim, each closed into a cave
by `lv_cave_vignette` (`place_screen05`, `place_screen07`):

- **screen05, the daemon's torture pocket**, Fire wing north-west
  (origin (2048, 14080)). The Fire wing's floor is cave rock (glob 397,
  301) rather than scorched earth (480), as the shot shows it. The
  north-west quadrant is rock round the pocket (`SCREEN05_MASK`), and the
  pocket opens east onto the north-south causeway. The lakes (1,1),
  (2,1) and (1,2), three pools, two flames and a spire stood in that rock
  and are gone. The group-3 daemon egg moved to (2880, 15104), off the
  shot's fire field, and its trigger moved to (3520, 15104), the
  causeway at the pocket's mouth. Fire fields (400) are on the map now
  and in `exact_reach.HURT_SHAPES_U8`. Built window 89.00% (floor 82.80).
- **screen07, the Pillar of Fire**, around the Fire pillar pin. The Four
  Pillars chamber is a cave: its floor is glob 397 and its north, west
  and east stone walls are gone. The Water section's south wall, the
  rim and `SCREEN07_MASK`'s rock close it, and the south gate line
  stays three courses of masonry. The pillar is our 865 f2 until the
  phase-C pillar art. Spike 0 is the retail wall 26 f5, the only
  stand-in the window-score search kept. The **Fire receptacle moved to
  (7935, 21759)** (`FIRE_RECEPTACLE`), 255 east and 255 south of its
  pillar, off the frame, and its within-300 box still holds only its own
  pillar. The other three stay 256 south of theirs. The paving squares,
  the centre slab, the lamps and the tapestries left with the walls.
  Built window 86.93% (floor 86.44).

### Entry Hall (~6×6 chunks, center-north)
**Coordinates:** (8192–11264, 1024–4096)

- Introduction to the dungeon atmosphere
- Stone corridors with ancient carved walls
- Transition from natural cave (Map 9) to constructed dungeon
- Teleport DEST egg (ID 203) for return from Map 9
- Teleport TRIGGER egg (ID 202+) for going back to Map 9
- Optional: first encounter with multi-elemental agent (if implemented)

### Central Hub (~6×6 chunks, center)
**Coordinates:** (8192–11264, 4096–7168)

- Central room connecting to all four sections
- Four corridors branching to each elemental section
- Each corridor entrance visually themed to hint at its element:
  - Earth: brown/grey stone, root shapes
  - Air: open arches, elevated walkway
  - Fire: warm-colored stone, torch shapes
  - Water: damp walls, pool shapes
- Optional: recurring guardian NPC patrols this area

### Earth Section (~10×10 chunks, north-west)
**Coordinates:** (1024–6144, 1024–6144)

- **Theme:** Caves, rock formations, earthquakes
- **Terrain:** Heavy use of cliff/rock shapes (3, 6, 65, 128, 242, 409)
- **Hazards:** Narrow passages, falling rock traps (damaging tiles)
- **Monsters:** Earth-themed creatures (monster eggs, shape 500)
  - Suggested: Golem-type or stone creature (reuse existing monster shapes)
- **Talisman:** Talisman of Earth placed in the deepest chamber
  - Item: TypeEarthItem (referenced in usecode), SF_QUALITY
  - Guarded by the section boss or puzzle
- **Puzzle concept:** Navigate through collapsing tunnels, find stable path
  to the talisman chamber

### Air Section (~10×10 chunks, north-east)
**Coordinates:** (14336–19456, 1024–6144)

- **Theme:** Open spaces, high platforms, wind
- **Terrain:** Elevated platforms at various z-levels (z=40–120)
  - Use ground shapes placed at high z for floating platforms
  - Gaps between platforms (falling = damage or teleport back)
- **Hazards:** Missing floor tiles, wind gusts (scripted movement?)
- **Monsters:** Air-themed creatures
  - Suggested: Flying creatures (reuse bat/bird shapes if available)
- **Talisman:** Talisman of Air on the highest platform
  - Item: SF_QUALITY with matching quality value
- **Puzzle concept:** Platforming across gaps, finding the path upward
- **Art note:** Most challenging section with existing assets — existing shapes
  are ground-oriented. Use translucent shapes (SI_TRANSL) for cloud effects.

### Fire Section (~10×10 chunks, south-west)
**Coordinates:** (1024–6144, 14336–19456)

- **Theme:** Lava, flames, heat
- **Terrain:** Dark stone floor with lava pools
  - Lava: Damaging shapes (318, 435–438, 636) covering floor areas
  - Safe paths: Narrow stone walkways between lava pools
  - Fire effects: Torch shapes, flame decorations
- **Hazards:** Lava floor (damaging on contact), flame jets
- **Monsters:** Fire-themed creatures
  - Suggested: Fire elementals or flame creatures
- **Talisman:** Talisman of Fire surrounded by a lava maze
  - Item: TypeFireItem (referenced in usecode), SF_QUALITY
- **Puzzle concept:** Navigate lava maze, find safe path, possibly use
  water-related items to cool sections

### Water Section (~10×10 chunks, south-center)
**Coordinates:** (6144–14336, 14336–19456)

- **Theme:** Flooded chambers, underwater passages
- **Terrain:** Water tiles (347, 669, 710, 738) filling large areas
  - Partially submerged walkways
  - Islands of dry ground in water-filled rooms
- **Hazards:** Deep water (damage or drowning), water currents
- **Monsters:** Water-themed creatures
  - Suggested: Water zombies (previewing the Lake encounter on Map 10)
- **Talisman:** Talisman of Water on an island in the center of a flooded room
- **Puzzle concept:** Find a way across the flooded chambers, possibly raising/
  lowering water levels

### Four Pillars Chamber (~8×6 chunks, south)
**Coordinates:** (6144–10240, 19456–22528)

- Open chamber with four elemental pillars arranged in a square
- Each pillar: SF_QUALITY item with a unique quality value
- Each pillar receptacle: SF_QUALITY item adjacent to the pillar
- Pillar destruction: Avatar places the opposite-element talisman in the
  receptacle (Fire talisman → Water pillar, etc.)
- **Pillar shapes:** Use distinctive tall solid shapes (z-footpad >= 5)
  - Shapes from Art List v2.5: Pillar of Earth/Air/Fire/Water
  - Pillar Receptacle: handwritten addition to Art List
- When all four pillars are destroyed, the passage to the Lost Vale opens

### Teleporter Pad (~2×2 chunks, after pillars)
**Coordinates:** (8192–9216, 22528–23552)

- Placed just past the Four Pillars
- Bi-directional teleport to Map 10 (Lost Vale overworld)
- TRIGGER egg (ID 204) → transitions to Map 10
- DEST egg for returns from Map 10 (ID 205)
- Synopsis: "Will this area have a teleporter pad so the player can return
  here quickly?"

## Teleport Eggs

| Type | Shape | Frame | Quality | NPC | Map | Zone | Notes |
|------|-------|-------|---------|-----|-----|------|-------|
| DEST | 508 | 0 | 458 | 202 | 9 | Entry | Arrival from Map 9 |
| TRIGGER | 508 | 1 | 203 | 0 | 0 | Entry | Return to Map 9 |
| TRIGGER | 508 | 1 | 204 | 0 | 0 | Exit | Go to Map 10 |
| DEST | 508 | 0 | 461 | 205 | 10 | Exit | Return from Map 10 |

## Monster Eggs

| Zone | Count | Type | Shape Quality | Notes |
|------|-------|------|---------------|-------|
| Earth Section | 4–6 | Earth creatures | TBD | Spread through section |
| Air Section | 3–4 | Air creatures | TBD | On platforms |
| Fire Section | 4–6 | Fire creatures | TBD | Near lava edges |
| Water Section | 4–6 | Water creatures | TBD | In water areas |
| Hub/passages | 2–3 | Mixed/guardian | TBD | Patrol encounters |
| **Total** | **17–25** | | | Base game Map 8 has 19 |

## Item Estimates

| Category | Count | Notes |
|----------|-------|-------|
| Glob eggs (terrain) | ~800 | Cave/dungeon floor tiles |
| Wall shapes | ~600 | Directional cave walls |
| Decorations | ~400 | Stalactites, rubble, torches, etc. |
| Elemental features | ~200 | Lava, water, air gaps, earth rubble |
| Doors/gates | ~20 | Section entrances, locked passages |
| Monster eggs | ~25 | Creature spawns |
| Teleport eggs | 4 | Entry/exit transitions |
| Quest items | 8 | 4 talismans + 4 pillar receptacles |
| Containers | ~15 | Treasure chests, supply caches |
| Roof tiles | ~200 | Cave ceilings |
| **Total** | **~2,272** | Conservative estimate |

## Design Principles

1. **Non-linear:** Player can tackle the four sections in any order from the hub.
   No section requires items from another section.

2. **Escalating difficulty:** Suggest Earth → Fire → Water → Air as the intended
   order (easiest to hardest), but don't enforce it.

3. **Visual distinctiveness:** Each section must look clearly different through
   terrain choices and color palette. The hub hints at each section's theme.

4. **Manageable scale:** Each section should take 15–30 minutes of gameplay.
   The entire dungeon is ~60–120 minutes.

5. **Return path:** The teleporter pad at the exit ensures the player never
   needs to re-traverse the entire dungeon.

## Dependencies

- Map 9 (Galjeron's Chamber) for entry transition
- Map 10 (Lost Vale overworld) for exit transition
- Talisman item shapes (may need new art or use gem placeholder shapes)
- Pillar shapes (may need new art; Art List says these were designed)
- Monster shapes for section-themed creatures
- Multi-elemental agent NPC (optional — Synopsis suggestion only)

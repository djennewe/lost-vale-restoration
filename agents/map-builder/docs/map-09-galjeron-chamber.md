# Map 9 — Beyond Double Doors / Galjeron's Chamber

Design document for the small interior map connecting Bonecrusher's Cave (Map 8)
to the Elemental Dungeon (Map 11).

## Overview

| Property | Value |
|----------|-------|
| Map slot | 9 |
| Type | New interior |
| Size | ~8×8 chunks (4,096×4,096 world units) |
| Estimated items | ~300 |
| Terrain style | Cave / underground passage |
| Entry | From Map 8 (Plateau double doors) |
| Exit | To Map 11 (Elemental Dungeon) |

## Story Context

**Beat 4:** Inside the double doors, the Avatar finds Galjeron's dead body and
his journal. Galjeron searched for the Lost Vale and was killed by a guardian
creature. His journal describes the four elemental gemstones needed to pass
through the Elemental Dungeon.

**Synopsis note:** "There should be some sort of guardian within this room.
Something that actually killed Galjeron."

## Layout

```
    From Map 8 (double doors)
    Teleport DEST (ID 201)
         │
    ┌────┴────────────────────────────┐
    │                                  │
    │    Entry passage                 │
    │    (narrow, cave walls)          │
    │         │                        │
    │    ┌────┴────┐                   │
    │    │         │                   │
    │    │  Main   │                   │
    │    │ Chamber │                   │
    │    │         │    Guardian's     │
    │    │  ✝      │    lair area     │
    │    │  body   │    (monster egg) │
    │    │  +book  │                   │
    │    │         │                   │
    │    └────┬────┘                   │
    │         │                        │
    │    Passage deeper                │
    │    (narrowing cave)              │
    │         │                        │
    │    Teleport TRIGGER (ID 202)     │
    │    To Map 11 (Elemental Dungeon) │
    │                                  │
    └──────────────────────────────────┘

    Approximate scale: 1 square = 2 chunks (1024 world units)
```

### Zones

**Zone 1: Entry Passage (2×2 chunks)**
- Narrow cave passage from the double doors
- Teleport DEST egg (ID 201) for return trips from Map 8
- Teleport TRIGGER egg (ID 200) for returning to Map 8
- Cave wall shapes (26–32, cliff faces) on both sides
- Roof shapes overhead (34, 37, 162)
- Dim, foreboding atmosphere

**Zone 2: Main Chamber (4×4 chunks)**
- Open cave room, the largest space in the map
- Galjeron's body: NPC shape in "dead" frame, placed on the ground
- Galjeron's Journal: TypeBook item next to the body (triggers dialogue on use)
- Scattered personal effects around the body (backpack, weapon, etc.)
- Guardian creature's lair area — bones, debris, signs of struggle
- Monster egg (shape 500) for the guardian creature
- Ambient items: stalactites, rubble, old torch sconces

**Zone 3: Deeper Passage (2×3 chunks)**
- Passage leading from the chamber toward the Elemental Dungeon
- Narrowing cave that transitions to more structured stonework
- Signs of ancient construction (carved walls, faded markings)
- Teleport TRIGGER egg (ID 202) at the far end → Map 11

## Item List

### Terrain (glob-based)

| Item Type | Count | Shapes | Notes |
|-----------|-------|--------|-------|
| Ground globs | ~20 | Glob eggs (shape 2) | Cave floor terrain |
| Cave walls | ~40 | Shapes 26–32, 125, 301 | Directional cliff shapes |
| Roof tiles | ~15 | Shapes 34, 37, 162 | Cave ceiling |
| Rubble/rocks | ~15 | Shapes 65, 92, 94 | Floor debris |

### Placed Items

| Item | Shape | Family | Quality | Notes |
|------|-------|--------|---------|-------|
| Galjeron's body | NPC shape | GENERIC | 0 | Dead frame; placed at (~2048, ~2048, 0) |
| Galjeron's Journal | TypeBook | QUALITY | Read trigger | Usecode activates dialogue |
| Backpack | TypeBackPack | CONTAINER | 0 | Galjeron's belongings |
| Old weapon | TypeWeapon | GENERIC | 0 | Near body — sword or axe |
| Torch sconces | Decoration | GENERIC | 0 | x4, mounted on walls |
| Stalactites | Decoration | GENERIC | 0 | x6, hanging features |
| Bones (old) | Decoration | GENERIC | 0 | x3, scattered near lair |

### Eggs

| Type | Shape | Frame | Quality | NPC | Map | Position | Notes |
|------|-------|-------|---------|-----|-----|----------|-------|
| Teleport DEST | 508 | 0 | 456 | 200 | 8 | Entry | Return from Map 8 |
| Teleport TRIGGER | 508 | 1 | 201 | 0 | 0 | Entry | Go back to Map 8 |
| Teleport TRIGGER | 508 | 1 | 202 | 0 | 0 | Exit | Go to Map 11 |
| Teleport DEST | 508 | 0 | 459 | 203 | 11 | Exit | Return from Map 11 |
| Monster egg | 500 | 0 | (guardian) | 1 | 0 | Lair area | Guardian creature |

## Guardian Creature Design

The Synopsis says "some sort of guardian... something that actually killed
Galjeron." Options:

1. **Reuse existing monster** — Use a base game creature shape (e.g., a ghoul,
   daemon, or skeleton warrior). Simple and proven.

2. **Multi-elemental agent preview** — If the Elemental Dungeon uses a recurring
   guardian (Synopsis suggestion), this could be its first appearance. Creates
   narrative continuity.

3. **Unique creature** — A new monster type. Requires new art (see
   asset-reuse-plan.md).

**Recommendation:** Option 1 for initial implementation, upgradeable to
Option 2 if the multi-elemental agent is implemented.

## Terrain Construction

Use existing cave/dungeon globs where possible. The base game has extensive
cave terrain in Maps 28, 46, and 63 (small cave interiors). Analyze their glob
usage patterns for reuse:

- Map 46: 240 globs in a 5×10 chunk space — good reference for narrow caves
- Map 63: 206 globs in an 8×22 chunk space — good reference for cave+building

For ~8×8 chunks with ~20 glob eggs and ~280 placed items, the map is
comparable in density to the smaller base game interiors.

## Atmosphere Notes

- This is the player's first step into LV content — it should feel immediately
  different from the Plateau
- The cave should feel ancient and undisturbed except for Galjeron's remains
- Transition from natural cave to hewn stone suggests the Elemental Dungeon
  builders were an advanced civilization
- The guardian creature should be a credible threat — Galjeron was presumably
  capable but fell to it

## Dependencies

- Map 8 modification (B2) must provide the entry transition
- Guardian creature shape selection (can use placeholder)
- Galjeron's Journal text (depends on NPC dialogue agent)

# Map 18 — Ancient Temple / Shrine of the Ancient Ones

Design document for the end-game map where the Zealan gods are freed.

## Overview

| Property | Value |
|----------|-------|
| Map slot | 18 |
| Type | New interior |
| Size | ~12×15 chunks (6,144×7,680 world units) |
| Estimated items | ~800 |
| Terrain style | Ancient stone temple, shrine interior |
| Entry | From Map 10 (Lost Vale, Temple approach) |
| Exit | Return to Map 10 |

## Story Context

**Beats 16–18:** After the Shield restoration ceremony, the Avatar and Ezrekal
enter the Ancient Temple. Hrodny's Tiny Tar potions allow the Avatar to enter
parts of the temple (shrink mechanic). Inside, the three Zealan gods are
imprisoned in amber-like resin. The Avatar places the restored Shield on the
altar, and the gods are freed.

**Key usecode files:**
- FREE.UNK (40.9 KB) — god-freeing ceremony
- POTION.UNK (4.6 KB) — Tiny Tar potion mechanic

**Usecode flags:** templeOpen, ezToTemple, godsFree, godsSpoke, getPowerAO

**Design decision DD-002:** Temple and Shrine are one map area. The "Temple"
is the outer structure; the "Shrine" is the inner sanctum where the gods are.

## Layout

```
    From Map 10 (Lost Vale)
    Teleport DEST (ID 210)
         │
    ┌────┴──────────────────────────────┐
    │                                    │
    │   TEMPLE EXTERIOR                  │
    │   (normal-size passage)            │
    │                                    │
    │   ┌────────────────────┐           │
    │   │  Outer Hall        │           │
    │   │  (Ezrekal waits)   │           │
    │   │                    │           │
    │   │  Guardian/Barrier  │           │
    │   │  (must overcome)   │           │
    │   └────────┬───────────┘           │
    │            │                       │
    │   ┌────────┴───────────┐           │
    │   │                    │           │
    │   │  Transition Hall   │           │
    │   │  (narrowing)       │           │
    │   │                    │           │
    │   │  ╔══════════╗      │           │
    │   │  ║ TINY     ║      │           │
    │   │  ║ ENTRY    ║      │           │
    │   │  ║ (shrink) ║      │           │
    │   │  ╚════╤═════╝      │           │
    │   │       │             │           │
    │   └───────┼─────────────┘           │
    │           │                         │
    │   ┌───────┴─────────────────┐      │
    │   │                         │      │
    │   │   INNER SANCTUM         │      │
    │   │   (Shrine of the        │      │
    │   │    Ancient Ones)        │      │
    │   │                         │      │
    │   │   ┌─────┐ ┌─────┐      │      │
    │   │   │God 1│ │God 2│      │      │
    │   │   │resin│ │resin│      │      │
    │   │   └─────┘ └─────┘      │      │
    │   │       ┌─────┐          │      │
    │   │       │God 3│          │      │
    │   │       │resin│          │      │
    │   │       └─────┘          │      │
    │   │                         │      │
    │   │      ◊◊◊ ALTAR ◊◊◊     │      │
    │   │   (place Shield here)   │      │
    │   │                         │      │
    │   └─────────────────────────┘      │
    │                                    │
    └────────────────────────────────────┘
```

## Zone Details

### Temple Exterior (4×4 chunks)
**Coordinates:** (2048–4096, 512–2560)

- Stone temple entrance — imposing ancient architecture
- Large doorway or archway (opened by templeOpen flag)
- Teleport DEST (ID 210) for arrival from Map 10
- Teleport TRIGGER (ID 211) for return to Map 10
- Ezrekal may wait here if the Avatar enters alone first
- Path leading inward, flanked by carved walls

### Outer Hall (6×4 chunks)
**Coordinates:** (1536–4608, 2560–4608)

- Grand entrance hall with columns and ceremonial decorations
- Guardian or barrier that must be overcome:
  - **Option A (Plot v1.2):** Explosive barrier — "some sort of explosive and a
    nice piece of usecode will do very well here"
  - **Option B (Synopsis):** Guardian creature — reuse the multi-elemental agent
    from the Elemental Dungeon, "which can only be slain by someone bearing the
    intact shield"
- Ezrekal accompanies the Avatar (ezToTemple flag)
- Ancient inscriptions on walls (decorative)

### Transition Hall (4×3 chunks)
**Coordinates:** (2048–4096, 4608–6144)

- Passage narrows from grand hall toward the shrine
- Walls close in, ceiling lowers
- Contains the Tiny Entry — a passage too small for normal-size Avatar
- Standard egg (shape 73) triggers POTION usecode
- After using Tiny Tar potion: Avatar shrinks and can pass through

**Tiny Tar mechanic:**
- The engine's POTION.UNK handles the shrink effect
- The narrow passage is defined by collision shapes
- Small doorway (low z-footpad shapes) blocks normal passage
- After shrinking, Avatar can pass through

### Inner Sanctum (8×5 chunks)
**Coordinates:** (1024–5120, 6144–8704)

- The heart of the temple — the Shrine of the Ancient Ones
- Dramatic reveal: three Zealan gods encased in amber-like resin
  - "Like the shields in the movie Dune" (Plot v1.2)
  - Three unique shapes (new art needed — god figures in resin)
  - Positioned around the altar in a triangular arrangement
- Central altar for placing the restored Shield
  - Large decoration shape on a raised platform
  - SF_QUALITY item with a trigger quality for Shield placement
- When Shield is placed: FREE.UNK triggers the ceremony
  - Gods are freed from resin
  - Speaking god shapes replace encased versions
  - Dialogue: gods give wisdom, cure Avatar's poison
  - Reward: Bag of Reagents (TypeBagOReagents)
  - getPowerAO flag set

## Key Items

| Item | Shape | Location | Notes |
|------|-------|----------|-------|
| God 1 (Felicitar) encased | New art | Sanctum | Resin-encased figure |
| God 2 (Doloras) encased | New art | Sanctum | Resin-encased figure |
| God 3 (Timyra) encased | New art | Sanctum | Resin-encased figure |
| God 1 speaking | New art | Sanctum | After freeing |
| God 2 speaking | New art | Sanctum | After freeing |
| God 3 speaking | New art | Sanctum | After freeing |
| Altar | Decoration | Sanctum | Shield placement target |
| Restored Shield | TypeAOFrizbee | Placed on altar | Quest-critical |
| Bag of Reagents | TypeBagOReagents | Given by gods | Reward |
| Restored Shield (armor) | Armour shape | Given by gods | Reward |

## Teleport Eggs

| Type | ID | Position | Notes |
|------|----|----------|-------|
| DEST | 210 | Exterior | Arrival from Map 10 |
| TRIGGER | 211 | Exterior | Return to Map 10 |

## Item Estimate

| Category | Count | Notes |
|----------|-------|-------|
| Glob eggs | ~80 | Temple floor terrain |
| Wall shapes | ~200 | Temple walls, columns |
| Roof shapes | ~60 | Temple ceilings |
| Decorations | ~150 | Inscriptions, torches, urns |
| Door shapes | ~8 | Hall entrances |
| God figures | 6 | 3 encased + 3 speaking (new art) |
| Quest items | ~5 | Altar, Shield, rewards |
| Eggs | ~8 | Teleports + triggers |
| Containers | ~10 | Ancient chests, urns |
| **Total** | **~527** | |

## Art Requirements (This Map)

| Asset | Priority | Count | Notes |
|-------|----------|-------|-------|
| Zealan God encased | Must-have | 3 | "Like Dune shields" |
| Zealan God speaking | Must-have | 3 | Free from resin |
| Temple wall textures | Should-have | — | Can reuse dungeon walls |
| Altar decoration | Nice-to-have | 1 | Can use existing large stone |

## End-Game Events

The end-game sequence (beats 17–18) is the most significant missing usecode:

1. Avatar places restored Shield on altar
2. FREE.UNK triggers (40.9 KB — substantial ceremony)
3. Gods freed from resin (shape swap: encased → speaking)
4. Gods speak to Avatar:
   - Cure the poison (avatarPoisoned flag cleared)
   - Explain about the Titans and Ether Titan potential
   - Give Bag of Reagents
   - Give restored Shield (armor — maxes armor rating)
   - May offer insight about Britannia (U9 teaser)
5. Water flows again, plants return in the Lost Vale
6. getPowerAO flag set

**Note:** The end-game usecode (steps 17–21) is MISSING from the recovered
snapshot. The ceremony sequence in FREE.UNK exists (40.9 KB) but may be
incomplete. The NPC dialogue agent will need to design the god dialogue
and ceremony implementation.

## Atmosphere

- Ancient, sacred atmosphere — this is the holiest site of the Zealan religion
- Torchlight or ethereal glow illuminating the sanctum
- The encased gods should be visually striking — three figures frozen in
  translucent resin, positioned around a central altar
- Sense of power and reverence — the room should feel like a place where
  the Avatar is in the presence of forces far greater than themselves
- After the gods are freed: dramatic transformation — light fills the room,
  the atmosphere shifts from oppressive to glorious

## Dependencies

- Map 10 (Lost Vale) for entry transition
- Shield restoration (SHADES ceremony) must have occurred
- Tiny Tar potion mechanic (POTION.UNK)
- FREE.UNK ceremony implementation
- God figure shapes (6 new art pieces — highest priority new art)
- NPC dialogue agent for god speech and ceremony text
- Bag of Reagents implementation (TypeBagOReagents — usecode MISSING)

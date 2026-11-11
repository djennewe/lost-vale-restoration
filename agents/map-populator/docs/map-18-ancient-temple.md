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

### Inner Sanctum (a cave behind the crack)
**Coordinates:** (1024–5120, 6144–9344); the walkable cave is x 2304–3839,
y 6144–9215.

**Rebuilt 2026-10-17 as the 1994 screenshot screen04** (`build_inner_sanctum()`
in `build_map_18.py`; evidence and scores in
`docs/research/2026-10-16-screenshot-reconstruction/phaseC/map18/REPORT.md`).
screen04 is the ceremony: the three gods in amber on retail plinths (37
frames 10/13), the altar (550) on the bare floor with the Shield on it, the
Avatar beside it, on cave rock (301) between craggy cave walls (26–32). The
reconstruction (`vignettes/screen04.json`) is stamped verbatim at its origin
(1408, 6912, 0) and the cave round it is closed by `lv_cave_vignette.Cave`
from `SANCTUM_MASK` (128-unit cells):

- **Antechamber** behind the breach (x 2304–3455, y 6144–7167): the breach
  rubble and EggTempleEntry. The temple masonry ends at the crack line
  (y=6143, shapes 15/47, `BREACH_PIECES`), unchanged.
- **Two passages** round the rock the shot shows at its top (its south face
  on y 7551, x 2688–2975).
- **The shrine** (y 7552–9215): the shot's floor, its west wall on x 2303,
  and the floor run out past the frame on every side.
- Rock north or west of the floor is cave wall, two 48-unit courses; rock
  south or east of it is retail's invisible wall, so the floor ends at black
  there as the 1994 caves do. Nothing generated paints into the shot's
  window; the void is covered by `lv_cave_vignette.void_cover` (cell tiles
  over the cave's SI_DRAW floor, 564 plates elsewhere).
- The old rectangle's outline (shoulders y=6175, x=1024, x=5119, south line
  y=9343) is retail's invisible wall three courses high, 144
  (`sanctum_outline()`), so the anti-climb gate lines still hold.

Pins (screen04's `placement.pin_moves`): Felicitar 860 f0 q301 (2783,8031,16),
Doloras f1 q302 (3039,7903,16), Timyra f2 q303 (3039,8415,16), each on her
plinth; altar q310 (3127,8175,0); EggAOCeremony q296 (3072,8320,0), whose
±192 box holds screen04's Avatar spot (3256,8152); the priestess's skull 331
(npcnum 228) off the frame at (2496,8448,0). The striped prop on Felicitar's
plinth is 881 (the 1994 single-shot sprite). The Shield is not placed: the
restored Shield is 879 and AOSCENE pops it to (3111,8167,16), the shot's spot.

Gone with the 2026-09-14 room: the two-tier dais and processional way (113,
70), candelabra, rune columns, cushions, candlesticks, the colonnade,
tapestries, lamps, urns, the flagstone globs and the temple walls on the
west, east and south lines.

**History.** The sanctum was a flagstone hall from 2026-09-14 to 2026-10-17
(colonnade, processional way, two-tier dais), built after the floor glob 80
turned out to be a lattice of low walls. **The other three zones followed on 2026-09-14**, same floor, same kit. Every
zone boundary glob 80 used to wall is an explicit run of its wall piece (15)
with one 256-unit doorway on the centre line, x 2944–3199:

- Exterior → Outer Hall at y=2559; Outer Hall → Transition Hall at y=4607
  (that run also seals two of glob 80's per-chunk doorways, x 1727–1855 and
  4287–4415, which opened onto the void because the Transition Hall is
  narrower than the hall above it); the Outer Hall's north shoulders at
  y=2591.
- The crack line (y=6143) is built to DD-005's numbers in the same pieces:
  128-unit pieces to 2815, the 64-unit stub owning 2753..2816, nothing to
  2879, pieces from 2879, a stub for the last 64 — clear span 2817..2879 as
  before (`test_crack_geometry.py`, 32 positions for the shrunken body, 0
  for the full-size one).
- Exterior: the gate (114) set into the north wall's face on the axis,
  three pairs of columns, banners and lamps either side of the gate.
- Outer Hall: two rows of four columns, a pew down each side aisle,
  tapestries on the north line and shoulders and the west wall. The
  guardian egg is untouched.
- Transition Hall: two stations of stone walls jutting in from the sides
  (2048 → 1280 → 1024 wide) with a column at each inner end — the "walls
  close in" the design called for; the two wooden hut-wall stubs and the
  twelve rubble-ceiling squares at z=20 (below head height) are gone.

**The walls themselves changed on the same day.** Every run on the map had
been built from 489/492, and those are not wall pieces: their frames are wall
ornaments — gargoyle caps, carved corners, barred windows — that the base
game sets on top of walls (177 and 119 uses in all 42 maps). Runs of them
read in-engine as rows of wall tops stacked on each other. The map's walls
are now the base game's stone-wall pair, shape 10 long in y and 15 long in x
(5,550 and 4,314 uses), plain frame 1, with the carved-face frames (10 f5,
15 f0) set into every fourth ground-course piece of the faces this projection
shows (`accent_reliefs()`). Maps 09/10/11/13/17 still build from 489/492.

`map_walkability.run_map18` changed with it: the raster reads the 63-unit
crack as two free cells, and only the sanctum's lattice had been stopping
its full-size flood. It now adjudicates the crack with `Box::overlaps` over
the expanded items, seals those cells for the full-size flood when the
engine would refuse the body, and asks the raster the question it can
answer — whether any *other* route reaches the altar.

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
| God 1 (Felicitar) sealed | 860 frame 0 (the 1994 pixels) | (2783,8031,16), on her plinth | q301; run 6-17 ends on frame 3 |
| God 2 (Doloras) sealed | 860 frame 1 (the 1994 pixels) | (3039,7903,16), on her plinth | q302; run 18-29 ends on frame 4 |
| God 3 (Timyra) sealed | 860 frame 2 (the 1994 pixels) | (3039,8415,16), on her plinth | q303; run 30-41 ends on frame 5 |
| Gods freed | 860 frames 3-5 (1994 scale) | the same items | AOSCENE kicks each run; GODANIM steps it; TEMPLENT re-applies (range 2400) |
| Altar | 550 | (3127,8175,0), on the floor | q310; Shield placement target |
| Striped prop | 881 (1994, single-shot) | (2815,8031,16), Felicitar's plinth | scenery |
| Restored Shield | 879 (`TypeSacredShield`), q83 | carried in; AOSCENE pops it to (3111,8167,16) | Quest-critical; class 879 look() |
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

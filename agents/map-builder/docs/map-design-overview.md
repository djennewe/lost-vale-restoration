# Map Design Overview — The Lost Vale

Overall map plan, slot assignments, connection graph, and transition points for
the Lost Vale expansion. All design decisions reference the corpus documents in
`shared/corpus/` and the format specifications in this directory.

## Map Slot Assignments

| Map # | Name | Type | Est. Size | Reference Size |
|-------|------|------|-----------|----------------|
| 8 | Plateau (modified) | Existing + new items | 4,306+ items | Already populated |
| 9 | Beyond Double Doors / Galjeron's Chamber | New interior | ~300 items | Like Map 56 (182) |
| 10 | Lost Vale Overworld | New exterior | ~4,000 items | Like Map 8 (4,306) |
| 11 | Elemental Dungeon | New dungeon | ~3,500 items | Like Map 49 (4,447) |
| 13 | Cloud Cliffs | New vertical climb | ~1,200 items | Like Map 46 (385) × 3 |
| 17 | Cloud City | New floating city | ~2,000 items | Like Map 54 (1,729) |
| 18 | Ancient Temple / Shrine | New interior | ~800 items | Like Map 63 (752) |

**Rationale:** Map 10 is confirmed from usecode (`MapLostVale`). Adjacent slots
(9, 11, 13, 17, 18) are all empty and available. Grouping LV maps in a recognizable
range aids debugging and organization.

**Total new items:** ~11,800 across 6 new maps + modifications to Map 8

## Connection Graph

```
                         PAGAN (base game)
                              │
                           Map 8
                          Plateau
                       (double doors)
                              │
                           Map 9
                     Galjeron's Chamber
                              │
                           Map 11
                      Elemental Dungeon
                    ┌─────────┼─────────┐
                    │   Four Pillars    │
                    │   (dungeon exit)  │
                    │         │         │
                    │      Map 10      │
                    │   Lost Vale OW    │
                    │    ╱  │  │  ╲    │
                    │   ╱   │  │   ╲   │
                    │ Clan  │  │  Clan  │
                    │ Hosk. │  │  Gunn. │
                    │       │  │       │
                    │    Ezrekal's     │
                    │    Dwelling      │
                    │       │         │
                    │    Test Area    │
                    │    The Lake     │
                    │  Sacred Circle  │
                    │       │         │
                    │    Map 13       │
                    │  Cloud Cliffs   │
                    │       │         │
                    │    Map 17       │
                    │  Cloud City     │
                    │       │         │
                    │    Map 18       │
                    │ Ancient Temple  │
                    │                 │
                    └── Teleporter ───┘
                    (back to dungeon exit)
```

## Transition Point Definitions

Each transition requires a TRIGGER egg (frame=1) at the source and a DEST egg
(frame=0) at the destination. Teleport IDs must be unique within the global space.

### Reserved Teleport ID Range

Base game uses teleport IDs 0–105 (observed range). Lost Vale teleport IDs
start at **200** to avoid conflicts.

### Transition Table

| ID | From | To | Description |
|----|------|----|-------------|
| 200 | Map 8 (Plateau) | Map 9 (Galjeron's Chamber) | Double doors entry |
| 201 | Map 9 (Galjeron's Chamber) | Map 8 (Plateau) | Return from chamber |
| 202 | Map 9 (Galjeron's Chamber) | Map 11 (Elemental Dungeon) | Passage deeper |
| 203 | Map 11 (Elemental Dungeon) | Map 9 (Galjeron's Chamber) | Return from dungeon |
| 204 | Map 11 (Elemental Dungeon) | Map 10 (Lost Vale) | Four Pillars exit |
| 205 | Map 10 (Lost Vale) | Map 11 (Elemental Dungeon) | Return teleporter pad |
| 206 | Map 10 (Lost Vale) | Map 13 (Cloud Cliffs) | Cliff base entry |
| 207 | Map 13 (Cloud Cliffs) | Map 10 (Lost Vale) | Return from cliffs |
| 208 | Map 13 (Cloud Cliffs) | Map 17 (Cloud City) | Cliff top → city |
| 209 | Map 17 (Cloud City) | Map 13 (Cloud Cliffs) | Return from city |
| 210 | Map 10 (Lost Vale) | Map 18 (Ancient Temple) | Temple entrance |
| 211 | Map 18 (Ancient Temple) | Map 10 (Lost Vale) | Return from temple |

**Optional transitions:**

| ID | From | To | Description |
|----|------|----|-------------|
| 212 | Map 10 (Lost Vale) | Map 8 (Plateau) | Synopsis: allow travel back to Pagan |
| 213 | Map 8 (Plateau) | Map 10 (Lost Vale) | Return to LV (after first visit) |

The Synopsis "strongly recommends allowing travel back and forth between Pagan
and the Lost Vale" (Note 3). This can be implemented as a permanent teleporter
near the Four Pillars exit on Map 10 and a corresponding return on Map 8.

## Map Summaries

### Map 8 — Plateau (Modification)

**Changes needed:**
- Add TRIGGER egg (ID 200) near the double doors in Bonecrusher's Cave
- Optionally add a key/lock mechanism on a door item (SF_QUALITY shape)
- No terrain changes required — the double doors already exist in the base game

**Location:** Bonecrusher's Cave is in the Plateau area. The exact coordinates
of the double doors need to be identified from the base game (the doors are
present but non-functional in U8).

**Story context:** Beat 3 — Mythran tells the Avatar about Galjeron and the
double doors. The Avatar finds the key and enters.

### Map 9 — Beyond Double Doors / Galjeron's Chamber

**Layout concept:**
```
Entry from Map 8 (north)
    │
    ▼
┌──────────────────┐
│   Small cavern    │
│                   │
│   Galjeron's     │
│   body + journal  │
│                   │
│   Guardian       │
│   creature       │
│                   │
│   Passage deeper ─┼── To Map 11
└──────────────────┘
```

**Size:** ~8×8 chunks (~4,000×4,000 world units)
**Items:** ~300 (terrain globs, body, journal, guardian creature, decorations)

**Key elements:**
- Galjeron's dead body (NPC shape, dead frame)
- Galjeron's Journal (TypeBook item — describes the four elemental tokens)
- Guardian creature (Synopsis: "something that actually killed Galjeron")
- Monster egg for the guardian (shape 500)
- Transition to Elemental Dungeon

**Story context:** Beat 4 — Avatar discovers Galjeron's remains and learns about
the elemental gemstones.

### Map 10 — Lost Vale Overworld

**Layout concept:**
```
                 ┌── From Map 11 (Dungeon Exit / Four Pillars)
                 │   + Teleporter pad (return to dungeon)
                 ▼
    ┌────────────────────────────────────────┐
    │                                        │
    │   ┌─────────┐        ┌─────────┐      │
    │   │ Clan    │        │ Clan    │      │
    │   │ Hoskuld │        │ Gunnar  │      │
    │   │ Village │        │ Village │      │
    │   │  ⊕      │        │  ⊕      │      │
    │   └─────────┘        └─────────┘      │
    │       water                water       │
    │       source              source       │
    │                                        │
    │            Ezrekal's                   │
    │            Dwelling                    │
    │                                        │
    │         Test Area                      │
    │        (PLNTST)                        │
    │                                        │
    │         The Lake                       │
    │       (water zombies)                  │
    │                                        │
    │        Sacred Circle                   │
    │       (Sacred Rock)                    │
    │                                        │
    │      ┌── To Map 13 (Cloud Cliffs)     │
    │      │                                 │
    │      ── To Map 18 (Ancient Temple)    │
    │                                        │
    │     Birthplace of Moriens (optional)   │
    │                                        │
    └────────────────────────────────────────┘
```

**Size:** ~50×50 chunks (~25,000×25,000 world units)
**Items:** ~4,000 (terrain globs, two villages, NPCs, locations)

**Key sub-areas (all within one map):**

1. **Dungeon Exit / Entry Point** — where Avatar arrives from the Elemental Dungeon.
   Teleporter pad for return travel (Synopsis suggestion). Possible second
   teleporter for return to Pagan (Map 8).

2. **Clan Hoskuld Village** — near one water source. NPCs: female elder
   (descendant of Flossie's family), veteran (PTSD), hunter + farmer couple,
   child (ZCHILD), Ragnar, Thordis.

3. **Clan Gunnar Village** — near other water source. NPCs: male elder (Atli),
   inventor (atheist), moonshiner, conservative farmer, elder's daughter, Ingyald.

4. **Ezrekal's Dwelling** — apart from both communities. The Avatar must be
   escorted by representatives from both clans to reach her.

5. **Test Area** — location of the Passage Test (PLNTST). Contains the nasty
   plant with poisonous spines. Standard egg triggers the test event.

6. **The Lake** — body of water with Water Zombie monster eggs. Passage Stone
   found here. Ragnar's bag contains a key used at this location.

7. **Sacred Circle / Sacred Rock** — ceremonial gathering place. Shield
   restoration ceremony (SHADES event). Open area for the two clan leaders
   and Ezrekal to gather.

8. **Cloud Cliffs approach** — path leading to the base of the Cloud Cliffs.
   Locked gate requiring Key to the Clouds (TypeCliffKey) from Tyorvi.

9. **Ancient Temple entrance** — path to the Ancient Temple. Accessible after
   the Shield restoration.

10. **Birthplace of Moriens** (optional) — small ruin. Synopsis Note 5:
    "would please a great number of customers."

**Art notes:** "Barren is sometimes boring. I hope we're planning on using some
cool fallen ruins." Use rocky terrain shapes with scattered ruins and minimal
vegetation. Two distinct water sources mark the clan territories.

**Story context:** Beats 7–11, 14–16 — the core Lost Vale questline plays out
here across multiple sub-areas.

### Map 11 — Elemental Dungeon

**Layout concept:**
```
Entry from Map 9
    │
    ▼
┌───────────────────────────────────────┐
│                                       │
│   ┌─────────┐     ┌─────────┐        │
│   │  EARTH  │     │   AIR   │        │
│   │ Section │─────│ Section │        │
│   │  ⊕gem   │     │  ⊕gem   │        │
│   └────┬────┘     └────┬────┘        │
│        │               │             │
│     Central             │             │
│      Hub  ◄────────────┘             │
│        │                              │
│   ┌────┴────┐     ┌─────────┐        │
│   │  FIRE   │     │  WATER  │        │
│   │ Section │─────│ Section │        │
│   │  ⊕gem   │     │  ⊕gem   │        │
│   └─────────┘     └─────────┘        │
│                                       │
│         ┌──────────────┐              │
│         │ Four Pillars │              │
│         │ (exit gate)  │              │
│         │  E  A  F  W  │              │
│         └──────┬───────┘              │
│                │                      │
│         To Map 10 (Lost Vale)         │
│                │                      │
│         Teleporter Pad                │
│         (return to here)              │
└───────────────────────────────────────┘
```

**Size:** ~40×40 chunks (~20,000×20,000 world units)
**Items:** ~3,500

**Key elements:**

1. **Central hub** — connects all four sections. Avatar can tackle sections in
   any order (non-linear design).

2. **Earth Section** — rock/cave themed. Talisman of Earth. Use existing rock
   and cave terrain. Monsters: earth-themed creatures.

3. **Air Section** — open, elevated platforms. Talisman of Air. Most challenging
   to design with existing assets (see asset-reuse-plan.md). Monsters: air-themed.

4. **Fire Section** — lava and flame themed. Talisman of Fire. Use damaging
   shapes (435–438, 636) for fire hazards. Monsters: fire-themed.

5. **Water Section** — flooded chambers. Talisman of Water. Use sea shapes
   (347, 669, 710). Monsters: water-themed.

6. **Four Pillars** — exit area. Four elemental pillars block the passage.
   Avatar uses opposite-element talisman on each (Fire on Water pillar, etc.).
   Uses SF_QUALITY items with quality values for pillar/talisman matching.

7. **Teleporter Pad** — at the exit, for quick return (Synopsis suggestion).
   Bi-directional teleport egg pair to Map 10.

**Design notes:**
- Synopsis: "We need an NPC here — perhaps a guardian left behind by the Titans.
  A multi-elemental agent who shows up throughout."
- Walk Through: "Build obstacles!"
- Each section should be substantial enough to be a challenge (~10×10 chunks each)
- Hub-and-spoke layout allows non-linear exploration

**Story context:** Beats 5–6 — Avatar collects four elemental talismans and
destroys the pillars to reach the Lost Vale.

### Map 13 — Cloud Cliffs

**Layout concept:**
```
    To Map 17 (Cloud City) ← top
         │
    ┌────┴────────────────┐
    │    Cliff summit      │
    │                      │
    │    Harpie nests      │
    │    ↑                 │
    │    Narrow ledge      │
    │    ↑                 │
    │    Switchback path   │
    │    ↑                 │
    │    Bones / remains   │
    │    ↑                 │
    │    Cliff base        │
    │                      │
    └────┬────────────────┘
         │
    From Map 10 (Lost Vale) ← bottom
```

**Size:** ~10×25 chunks (~5,000×12,000 world units) — tall and narrow
**Items:** ~1,200

**Key elements:**
- Vertical climb using z-axis variation (z range: 0 at base to 120+ at summit)
- Narrow paths (1–2 chunk wide) with cliff walls on both sides
- Bones/skeletons of Zealans who tried and failed the climb
- Harpie monster eggs (shape 500) scattered along the path
- Locked gate at base requiring Key to the Clouds (TypeCliffKey)

**Usecode flags:** climbedCliffs, attemptedCliffs, agreeToClimb

**Story context:** Beat 12 — Avatar climbs to reach Cloud City. The Harpie is
the primary combat threat.

### Map 17 — Cloud City

**Layout concept:**
```
    ┌──────────────────────────────────┐
    │                                  │
    │   Floating platforms             │
    │                                  │
    │   ┌──────────┐                   │
    │   │ Main     │                   │
    │   │ Plaza    │                   │
    │   │          │   Magnetic        │
    │   │  Scroll  │   Obelisk         │
    │   │  here    │                   │
    │   └──────────┘                   │
    │                                  │
    │   God's Quarters                 │
    │   (deserted)                     │
    │                                  │
    │   Shield Half 1     Skeleton 1   │
    │   Shield Half 2     Skeleton 2   │
    │                                  │
    │   Collapsing ground              │
    │   (damaging tiles)               │
    │                                  │
    └──────┬───────────────────────────┘
           │
    From Map 13 (Cloud Cliffs)
```

**Size:** ~25×25 chunks (~12,000×12,000 world units)
**Items:** ~2,000

**Key elements:**
- Architecture: white and gold stone (recolored from "Bob's red stone")
- Cloud-like terrain (may need new shapes or creative use of existing)
- Floating platforms at high z values
- Collapsing ground sections (damaging shapes 435–438 as hazards)
- Magnetic Obelisk (MAGNET puzzle — seals equipment)
- Message Scroll from the gods
- Two shield halves near two skeletons (Snori and Hoskuld/Flossie)
- Deserted god quarters (empty rooms with abandoned furnishings)

**Usecode:** MAGNET.UNK (10.7 KB)

**Story context:** Beat 13 — Avatar finds Cloud City deserted, discovers the
scroll and shield halves.

### Map 18 — Ancient Temple / Shrine of the Ancient Ones

**Layout concept:**
```
    From Map 10 (Lost Vale)
         │
    ┌────┴────────────────┐
    │  Temple Exterior     │
    │  (normal-size entry) │
    │         │            │
    │  Tiny Entry          │
    │  (Tiny Tar needed)   │
    │         │            │
    │  Inner Sanctum       │
    │                      │
    │  ┌─────────────────┐ │
    │  │  God 1 (resin)  │ │
    │  │  God 2 (resin)  │ │
    │  │  God 3 (resin)  │ │
    │  │                 │ │
    │  │    ◊ Altar ◊    │ │
    │  │ (place Shield)  │ │
    │  └─────────────────┘ │
    │                      │
    └──────────────────────┘
```

**Size:** ~12×15 chunks (~6,000×7,500 world units)
**Items:** ~800

**Key elements:**
- Temple exterior with normal entrance
- Tiny entry section requiring Tiny Tar potion (shrink mechanic)
- Inner sanctum with three god figures encased in resin
  ("like the shields in the movie Dune")
- Altar for placing the restored Shield of the Ancients
- Barrier/guardian at entry (Synopsis: reuse multi-elemental agent or use
  explosive mechanism — Plot v1.2: "some sort of explosive and a nice piece
  of usecode")

**Usecode flags:** templeOpen, ezToTemple, godsFree, godsSpoke, getPowerAO
**Usecode files:** FREE.UNK (40.9 KB), POTION.UNK (4.6 KB)

**Story context:** Beats 16–18 — Avatar and Ezrekal enter the Temple, place
the Shield on the altar, free the gods, receive rewards.

---

## Map Production Order

Recommended order to maximize unblocked progress:

1. **B2: Map 8 modification** — smallest change, tests the transition system
2. **B3: Map 9 (Galjeron's Chamber)** — small interior, tests map creation
3. **B5: Map 10 (Lost Vale overworld)** — largest map, central hub
4. **B4: Map 11 (Elemental Dungeon)** — complex but self-contained
5. **B6: Maps 13 + 17 (Cloud areas)** — requires Cloud City design decisions
6. **B7: Map 18 (Ancient Temple)** — end-game, depends on god statue art

---

## Design Constraints

### Engine Limitations
- Max 256 maps total (214 available)
- Max 32,768 world units per axis per map
- Z range: -128 to +127
- Items per map: no hard limit (largest base game = 5,715)
- Chunk size: 512 world units (64 chunks per axis)

### Travel Between Pagan and Lost Vale
Synopsis Note 3: "strongly recommends allowing travel back and forth."
Implemented via teleport egg pair (IDs 212/213) connecting Map 10 and Map 8.
This allows the player to return to the base game world at any time, making
the expansion feel less isolated.

### Teleporter Pad at Dungeon Exit
Synopsis suggestion. Implemented as teleport egg pair (IDs 204/205) between
Map 11 (dungeon exit) and Map 10 (LV overworld entry). Allows the player to
return to the dungeon entrance quickly after reaching the Lost Vale.

### Backtracking Support
All transitions are bi-directional (each has a return path). The player can
always return to a previous area. This is consistent with the base game's
teleport egg pairing pattern.

# Maps 13 & 17 — Cloud Cliffs + Cloud City

Design document for the Cloud Cliffs vertical climb and Cloud City floating
architecture.

---

## Map 13 — Cloud Cliffs

### Overview

| Property | Value |
|----------|-------|
| Map slot | 13 |
| Type | New vertical climb |
| Size | ~10×25 chunks (5,120×12,800 world units) |
| Estimated items | ~1,200 |
| Terrain style | Narrow cliff paths, dramatic height |
| Entry | From Map 10 (Lost Vale, Cloud Cliffs approach) |
| Exit | To Map 17 (Cloud City) |

### Story Context

**Beat 12:** The Avatar climbs the Cliffs of Insanity (renamed "Cloud Cliffs" in
usecode) to reach Cloud City. Bones of Zealans who failed the climb litter the
path. The Harpie monster attacks during the ascent.

**Usecode:** climbedCliffs, attemptedCliffs, agreeToClimb

### Layout

```
    Cloud City (Map 17)
    Teleport TRIGGER (ID 208) ← top (z ≈ 120)
         │
    ┌────┴──────────┐
    │  Summit       │
    │  plateau      │  ← z = 112–120
    │       │       │
    │  Harpie       │
    │  nest area    │  ← z = 96–112
    │       │       │
    │  Narrow       │
    │  ledge (E)    │  ← z = 80–96
    │       │       │
    │  Switchback   │
    │  ┌─┐  │       │  ← z = 56–80
    │  │ │  │       │
    │  │ └──┘       │
    │       │       │
    │  Bones /      │
    │  warning area │  ← z = 32–56
    │       │       │
    │  Rocky climb  │
    │  begins       │  ← z = 8–32
    │       │       │
    │  Cliff base   │
    │  (locked gate)│  ← z = 0
    └────┬──────────┘
         │
    From Map 10 (Lost Vale)
    Teleport DEST (ID 206)
```

### Vertical Design

The map uses the full z-axis range to create a climbing experience:

| Elevation | z Range | Feature |
|-----------|---------|---------|
| Base | 0–8 | Gate area, entry from Lost Vale |
| Lower cliffs | 8–32 | Initial rocky ascent, wide path |
| Warning zone | 32–56 | Bones/remains, path narrows |
| Switchbacks | 56–80 | Path zigzags up cliff face |
| Narrow ledge | 80–96 | One-item-wide path, exposure |
| Harpie zone | 96–112 | Monster encounters, nests |
| Summit | 112–120 | Plateau before Cloud City |

### Key Elements

**Locked gate at base:**
- SF_QUALITY door with quality matching Key to the Clouds (TypeCliffKey)
- Tyorvi's key must be obtained first (beats 10–13)

**Climbing path:**
- Use cliff wall shapes (26–32) for vertical surfaces
- Ground shapes placed at increasing z values for the path
- Narrow paths (1–2 item widths) create tension
- Switchback layout maximizes the use of limited horizontal space

**Bones and remains:**
- Skeleton/bone decoration shapes scattered on ledges
- Tells the story of Zealans who attempted the climb
- Sets the atmosphere before the Harpie encounters

**Harpie encounters:**
- 3–4 monster eggs (shape 500) at upper elevations
- Harpies attack on narrow ledges — dangerous combat
- Nests near the summit with bones and debris

**Summit plateau:**
- Small flat area at the top (z ≈ 120)
- Teleport TRIGGER (ID 208) to Cloud City
- View point over the Lost Vale below

### Teleport Eggs

| Type | ID | Position | Notes |
|------|----|----------|-------|
| DEST | 206 | Base (z=0) | Arrival from Map 10 |
| TRIGGER | 207 | Base (z=0) | Return to Map 10 |
| TRIGGER | 208 | Summit (z=120) | Go to Map 17 |
| DEST | 209 | Summit (z=120) | Return from Map 17 |

### Monster Eggs

| Count | Type | Elevation | Notes |
|-------|------|-----------|-------|
| 3–4 | Harpie | z=80–112 | Upper cliff encounters |

---

## Map 17 — Cloud City

### Overview

| Property | Value |
|----------|-------|
| Map slot | 17 |
| Type | New floating city |
| Size | ~25×25 chunks (12,800×12,800 world units) |
| Estimated items | ~2,000 |
| Terrain style | White/gold stone, cloud terrain, floating platforms |
| Entry | From Map 13 (Cloud Cliffs summit) |
| Exit | Return to Map 13 |

### Story Context

**Beat 13:** The Avatar finds Cloud City deserted. The gods' home is empty.
A magnetic obelisk puzzle. The Avatar discovers the Message Scroll from the gods
and the two Shield halves near the skeletons of Snori and Hoskuld/Flossie.

**Art notes:**
- "Bob's red stone architecture turned white and gold"
- "Cloud-like terrain"
- "Collapsing ground"
- "Avatar dying in cloud terrain" sprite needed

**Usecode:** MAGNET.UNK (10.7 KB), cloudCity flag

### Layout

```
    ┌──────────────────────────────────────┐
    │                                      │
    │   Entry from Cliffs                  │
    │   (south edge)                       │
    │        │                             │
    │   ┌────┴────┐                        │
    │   │ Arrival │                        │
    │   │ Plaza   │                        │
    │   └────┬────┘                        │
    │        │                             │
    │   ┌────┴──────────────────┐          │
    │   │                      │          │
    │   │    Main Plaza        │          │
    │   │                      │          │
    │   │   ┌──────────┐       │          │
    │   │   │ Magnetic │       │          │
    │   │   │ Obelisk  │       │          │
    │   │   └──────────┘       │          │
    │   │                      │          │
    │   └────┬─────────┬───────┘          │
    │        │         │                   │
    │   ┌────┴──┐ ┌────┴──┐               │
    │   │ God's │ │ God's │               │
    │   │ Hall  │ │ Study │               │
    │   │  A    │ │  B    │               │
    │   └───────┘ └───────┘               │
    │                                      │
    │   ┌──────────────────────┐           │
    │   │  Scroll Chamber      │           │
    │   │  (Message Scroll)    │           │
    │   └──────────────────────┘           │
    │                                      │
    │   ┌──────────────────────┐           │
    │   │  Memorial Hall       │           │
    │   │  Skeleton 1 + Shield │           │
    │   │  Skeleton 2 + Shield │           │
    │   │  (collapsing ground) │           │
    │   └──────────────────────┘           │
    │                                      │
    │   ╔═══════════════════╗              │
    │   ║ CLOUD PLATFORMS   ║              │
    │   ║ (floating, gaps)  ║              │
    │   ║ hazardous terrain ║              │
    │   ╚═══════════════════╝              │
    │                                      │
    └──────────────────────────────────────┘
```

### Zone Details

**Arrival Plaza (5×5 chunks):**
- Entry from Cloud Cliffs (teleport DEST ID 208)
- First view of the deserted city
- White/gold stone architecture (recolored building shapes)
- Empty, abandoned feel — dust, fallen banners

**Main Plaza (8×8 chunks):**
- Central area of the city
- Magnetic Obelisk at center (MAGNET puzzle)
  - Large distinctive shape (decoration or unique art)
  - Usecode: equipment gets magnetically sealed to obelisk
  - Player must figure out how to retrieve equipment
- Pathways branching to other areas
- Collapsing ground sections (damaging shapes — tiles disappear underfoot)

**God's Halls A & B (5×5 chunks each):**
- Two deserted grand halls where the gods once held court
- Abandoned furnishings, empty thrones, faded decorations
- Lore items: plaques, inscriptions (PLAQUENS usecode)
- Architecture showing former grandeur — columns, arches

**Scroll Chamber (5×4 chunks):**
- Room where the Message Scroll is found
- The scroll: TypeBook or similar document item
- Contains the message from the gods explaining the Titans' attack
- Puzzle or obstacle to reach it (optional)

**Memorial Hall (6×5 chunks):**
- Where the Avatar finds the two skeletons and Shield halves
- Skeleton 1 (Snori/Flossie) with Shield Half 1
- Skeleton 2 (Hoskuld) with Shield Half 2
- The skeletons are positioned as if they died together
- Collapsing ground hazard in this area (damaging floor tiles)
- Shield halves: TypeAOFrizbee items (SF_QUALITY)

**Cloud Platforms (10×8 chunks):**
- Floating platform sections with gaps between them
- Ground shapes placed at high z values with void between
- Damaging shapes (or lethal fall) for the gaps
- Tests the player's navigation skills
- Cloud-like terrain (translucent shapes, mist effects if available)

### Magnetic Obelisk Puzzle

The MAGNET.UNK usecode (10.7 KB) implements this puzzle:
- When Avatar approaches, equipment is magnetically pulled to the obelisk
- Player must solve the puzzle to free their equipment
- Sheri's blog confirms this mechanic

**Implementation:**
- Large decoration shape for the obelisk
- Standard egg (shape 73) triggers MAGNET usecode
- The usecode handles equipment removal and return

### Key Items

| Item | Shape Type | Location | Notes |
|------|-----------|----------|-------|
| Message Scroll | TypeBook | Scroll Chamber | Quest-critical |
| Shield Half 1 | TypeAOFrizbee | Memorial Hall | Near skeleton 1 |
| Shield Half 2 | TypeAOFrizbee | Memorial Hall | Near skeleton 2 |
| Magnetic Obelisk | Decoration | Main Plaza | MAGNET puzzle |
| Skeleton 1 (Snori) | NPC shape (dead) | Memorial Hall | Near Shield half |
| Skeleton 2 (Hoskuld) | NPC shape (dead) | Memorial Hall | Near Shield half |

### Teleport Eggs

| Type | ID | Position | Notes |
|------|----|----------|-------|
| DEST | 208 | Arrival Plaza | From Cloud Cliffs |
| TRIGGER | 209 | Arrival Plaza | Return to Cliffs |

### Art Requirements

| Asset | Priority | Notes |
|-------|----------|-------|
| White/gold stone textures | Should-have | Recolor existing stone shapes |
| Cloud terrain tiles | Nice-to-have | New shapes or creative sea tile use |
| Collapsing ground effect | Nice-to-have | Can use damaging shapes as proxy |
| Magnetic Obelisk | Nice-to-have | Unique decoration shape |

### Atmosphere

- Eerie silence — a city built for gods, now completely empty
- Architecture suggests immense power and beauty, now fading
- White and gold color scheme contrasts with the dark volcanic Pagan world
- Cloud effects around the edges (if cloud terrain shapes are available)
- Sense of height — the city is above the clouds
- The desertedness should feel recent-ish — furniture overturned, not crumbled

---

## Combined Cloud Area Dependencies

- Map 10 (Lost Vale) for Cliffs approach
- Harpie monster shape (new art or placeholder)
- Key to the Clouds (TypeCliffKey) mechanics
- MAGNET usecode implementation
- Shield half item shapes (TypeAOFrizbee)
- Cloud terrain tiles (optional — can use existing shapes creatively)

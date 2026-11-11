# Map 10 — Lost Vale Overworld

Design document for the central hub map of the Lost Vale expansion.

## Overview

| Property | Value |
|----------|-------|
| Map slot | 10 (confirmed from usecode: `MapLostVale`) |
| Type | New exterior |
| Size | ~50×50 chunks (25,600×25,600 world units) |
| Estimated items | ~4,000 |
| Terrain style | Barren valley with ruins, two water sources |
| Entry | From Map 11 (Elemental Dungeon, Four Pillars exit) |
| Connections | Maps 13 (Cloud Cliffs), 18 (Ancient Temple) |

## Story Context

**Beats 7–11, 14–16:** The Lost Vale is the core questline hub. The Avatar
arrives from the Elemental Dungeon, meets two feuding Zealan clans, undergoes
the Passage Test, investigates the Passage Stone mystery at the Lake, visits
Ezrekal, pursues the Key to the Clouds subplot, and participates in the Shield
restoration ceremony at the Sacred Circle.

**Art direction:** "Barren is sometimes boring. I hope we're planning on using
some cool fallen ruins." (Synopsis)

## Layout

```
 N ↑

       ┌───────────────────────────────────────────────┐
       │                                               │
       │   ENTRY (from Elemental Dungeon)              │
       │   + Return Teleporter                         │
       │   + Pagan Return Teleporter (optional)        │
       │              │                                │
       │    ┌─────────┴─────────┐                      │
       │    │                   │                      │
       │    ▼                   ▼                      │
       │  ┌─────────────┐  ┌─────────────┐            │
       │  │  CLAN       │  │  CLAN       │            │
       │  │  HOSKULD    │  │  GUNNAR     │            │
       │  │  VILLAGE    │  │  VILLAGE    │            │
       │  │             │  │             │            │
       │  │  ≈ spring   │  │  ≈ spring   │            │
       │  └──────┬──────┘  └──────┬──────┘            │
       │         │                │                    │
       │         └───────┬────────┘                    │
       │                 │                             │
       │         EZREKAL'S DWELLING                    │
       │         (isolated, between clans)             │
       │                 │                             │
       │    ┌────────────┼────────────┐                │
       │    │            │            │                │
       │    ▼            ▼            ▼                │
       │  TEST        THE         SACRED               │
       │  AREA        LAKE        CIRCLE               │
       │ (PLNTST)  (zombies)   (ceremony)              │
       │                                               │
       │              │                                │
       │    ┌─────────┴─────────┐                      │
       │    │                   │                      │
       │    ▼                   ▼                      │
       │  CLOUD CLIFFS        ANCIENT TEMPLE           │
       │  APPROACH            APPROACH                 │
       │  → Map 13            → Map 18                 │
       │  (locked gate)       (after ceremony)         │
       │                                               │
       │         [Birthplace of Moriens]                │
       │         (optional ruins)                      │
       │                                               │
       └───────────────────────────────────────────────┘
```

## Zone Coordinate Assignments

The map is divided into logical zones. All coordinates in world units.

| Zone | X Range | Y Range | Chunks | Purpose |
|------|---------|---------|--------|---------|
| Entry | 10240–15360 | 1024–4096 | 10×6 | Arrival from dungeon |
| Hoskuld Village | 3072–8192 | 5120–11264 | 10×12 | Clan Hoskuld settlement |
| Gunnar Village | 17408–22528 | 5120–11264 | 10×12 | Clan Gunnar settlement |
| Ezrekal's Dwelling | 11264–14336 | 11264–14336 | 6×6 | High Priestess home |
| Test Area | 4096–8192 | 15360–18432 | 8×6 | Passage Test location |
| The Lake | 11264–15360 | 15360–20480 | 8×10 | Water + zombies |
| Sacred Circle | 18432–22528 | 15360–18432 | 8×6 | Ceremony site |
| Cloud Cliffs Approach | 5120–9216 | 20480–24576 | 8×8 | Path to cliffs |
| Temple Approach | 16384–20480 | 20480–24576 | 8×8 | Path to temple |
| Moriens Ruins | 11264–14336 | 21504–24576 | 6×6 | Optional ruins |

## Zone Details

### Entry Area

**Coordinates:** (10240–15360, 1024–4096)

The Avatar arrives here from the Elemental Dungeon (Map 11). First view of
the Lost Vale — should immediately convey the "barren but once-great" feel.

**Items:**
- Teleport DEST egg (ID 204): arrival from Map 11
- Teleport TRIGGER egg (ID 205): return to Map 11
- Optional: Teleport pair (IDs 212/213) for return to Pagan (Map 8)
- Ruined gateway or archway marking the entrance
- Scattered ruins and rubble suggesting former grandeur
- Path splitting left (Clan Hoskuld) and right (Clan Gunnar)

**Terrain:** Rocky barren ground (shapes 3, 6, 128, 242). Cliff walls around
the edges (shapes 26–32). Ruins using wall/building shapes in damaged frames.

### Clan Hoskuld Village

**Coordinates:** (3072–8192, 5120–11264)

Settlement of the first Zealan faction. Located near one of the two water
sources (a spring or well).

**Structures:**
- 4–5 small huts (building shapes + roof shapes)
- Central gathering area
- Farming plots (barren ground with a few sparse plants)
- Spring/well water source (sea shapes 347, 474)

**NPCs (all within this zone):**
- Female Elder (descendant of Flossie's family) — hut near center
- Male Veteran (PTSD) — near the spring, sometimes drunk
- Female Hunter — at edge of village, facing outward
- Male Farmer — in farming area
- Male Child (ZCHILD) — roams the village area
- Ragnar — between village and fields; has a schedule (usecode)
- Thordis — in or near the village

**Key items:**
- Ragnar's Bag (given during conversation)
- Household containers with supplies

### Clan Gunnar Village

**Coordinates:** (17408–22528, 5120–11264)

Settlement of the second Zealan faction. Near the other water source.
Separated from Hoskuld by the central valley.

**Structures:**
- 4–5 small huts
- Moonshine still area (Moonshiner's workspace)
- Inventor's workshop
- Spring/well water source

**NPCs:**
- Male Elder (Atli) — hut near center, melancholic
- Female Inventor — workshop area
- Male Moonshiner — near still
- Female Farmer (conservative) — in farming area
- Female Child of Elder — near father (note: struck through in Character List)
- Ingyald — in or near the village
- Hrodny — has Tiny Tar potions in a locked chest
- Changtar — in or near the village

**Key items:**
- Hrodny's locked chest (SF_CONTAINER with quality = key ID)
- Tiny Tar potions (inside chest)
- Key to Hrodny's chest (elsewhere in the village — lost)
- Moonshine bottles (decoration/consumable)

### Ezrekal's Dwelling

**Coordinates:** (11264–14336, 11264–14336)

Isolated dwelling between the two villages, accessible by paths from both.
The Synopsis says the Avatar must be "escorted by a representative from
*both* rival factions" to reach her.

**Structure:**
- Single modest dwelling, separate from both communities
- Herb garden area
- Shelter with stored reagents and scrolls

**NPC:**
- Ezrekal — inside or near the dwelling

**Key items:**
- Potion ingredients (reagent shapes)
- The Special Root (delivered by Avatar, used to brew nightmare potion)
- TypeBushKey (referenced in usecode — purpose unclear, possibly related)

### Test Area (PLNTST)

**Coordinates:** (4096–8192, 15360–18432)

Location of the Rite of Passage. Contains the "nasty plant with delectable
fruit guarded by long poisonous spines."

**Layout:**
- Open area with the Test Plant at center
- Standard egg (shape 73) triggers PLNTST usecode
- The plant: decorative shape (Test Tree/Plant from Art List)
- Surrounding area: clear ground for the test encounter
- Bones/remains of previous test-takers (optional)

**Mechanics:**
- Avatar approaches plant → egg triggers PLNTST event
- Avatar always fails → gets poisoned (avatarPoisoned flag)
- After test: teleported/directed to Thordis and Atli for the mark

### The Lake

**Coordinates:** (11264–15360, 15360–20480)

Body of water with Water Zombies. The Passage Stone is here, lost when the
young woman was killed.

**Layout:**
- Central water body using sea shapes (347, 669, 710)
- Shore area around the lake
- Shallow wading areas and deeper sections
- Small island or peninsula where the Passage Stone rests
- Water Zombie monster eggs (shape 500) around the lake

**Key items:**
- Passage Stone — on the lakebed or shore (SF_QUALITY item)
- Evidence of the young woman's death (bones, belongings)

**Monsters:** 4–6 Water Zombie monster eggs

**Story:** Beat 8 — Avatar uses the key from Ragnar's bag, fights Water
Zombies, recovers the Passage Stone.

### Sacred Circle

**Coordinates:** (18432–22528, 15360–18432)

Ceremonial gathering place for the Shield restoration ceremony. Contains the
"Sacred Smallish Unusual-Colored Rock."

**Layout:**
- Open clearing with stone circle arrangement
- Central rock/altar (distinctive decoration shape)
- Seating/standing positions for clan leaders and Ezrekal
- Clear sightlines for the ceremony set piece

**Mechanics:**
- SHADES usecode triggers the ceremony
- The shades of Snori and Hoskuld/Flossie appear and speak
- Shield halves are joined → Shield restored
- Clans reconciled (game flags updated)

**Key items:**
- Sacred Rock — large distinctive decoration shape at center

### Cloud Cliffs Approach

**Coordinates:** (5120–9216, 20480–24576)

Path leading from the Lost Vale to the base of the Cloud Cliffs (Map 13).

**Layout:**
- Winding path through rocky terrain, climbing gradually
- Locked gate requiring Key to the Clouds (TypeCliffKey)
- The gate: SF_QUALITY door with quality matching the key
- Teleport TRIGGER (ID 206) past the gate → Map 13
- Teleport DEST (ID 207) for returns from Map 13

**Usecode flags:** climbedCliffs, attemptedCliffs, agreeToClimb

### Ancient Temple Approach

**Coordinates:** (16384–20480, 20480–24576)

Path leading to the Ancient Temple (Map 18). Accessible after the Shield
restoration ceremony (templeOpen flag).

**Layout:**
- Stone path through ruins
- Gate or barrier (opens after ceremony — usecode controlled)
- Teleport TRIGGER (ID 210) → Map 18
- Teleport DEST (ID 211) for returns from Map 18

**Usecode flags:** templeOpen, spokeOfOpenTemple, spokeTemple

### Birthplace of Moriens (Optional)

**Coordinates:** (11264–14336, 21504–24576)

Small ruin in the Lost Vale. Synopsis Note 5: "This would not be a difficult
thing to do, and would please a great number of customers."

**Layout:**
- Ruined building foundation (wall shapes in broken frames)
- Plaque or sign identifying the location (PLAQUENS usecode?)
- No gameplay function — purely lore/fan service

## NPC Placement Summary

| NPC | Zone | Usecode File | Clan | Role |
|-----|------|-------------|------|------|
| Female Elder | Hoskuld Village | (unnamed) | Hoskuld | Leader |
| Male Veteran | Hoskuld Village | (unnamed) | Hoskuld | PTSD veteran |
| Female Hunter | Hoskuld Village | (unnamed) | Hoskuld | Hunter |
| Male Farmer | Hoskuld Village | (unnamed) | Hoskuld | Farmer |
| Male Child | Hoskuld Village | ZCHILD.UNK | Hoskuld | Roaming child |
| Ragnar | Hoskuld Village | RAGNAR.UNK | Hoskuld | Passage Stone info |
| Thordis | Hoskuld Village | THORDIS.UNK | — | Passage Test ceremony |
| Atli (Male Elder) | Gunnar Village | ATLI.UNK | Gunnar | Leader |
| Female Inventor | Gunnar Village | (unnamed) | Gunnar | Atheist inventor |
| Male Moonshiner | Gunnar Village | (unnamed) | Gunnar | Moonshine maker |
| Female Farmer | Gunnar Village | (unnamed) | Gunnar | Conservative |
| Ingyald | Gunnar Village | INGYALD.UNK | Gunnar | — |
| Hrodny | Gunnar Village | HRODNY.UNK | — | Tiny Tar potions |
| Changtar | Gunnar Village | CHANGTAR.UNK | — | — |
| Tyorvi | Gunnar Village | TYORVI.UNK | — | Key to Clouds |
| Ezrekal | Ezrekal's Dwelling | EZREKAL.UNK | Independent | High Priestess |

**Total NPCs:** ~16 (comparable to a base game town)

## Teleport Eggs

| Type | ID | Shape | Frame | Quality | NPC | Map | Zone | Notes |
|------|----|-------|-------|---------|-----|-----|------|-------|
| DEST | 204 | 508 | 0 | 460 | 204 | 11 | Entry | From dungeon |
| TRIGGER | 205 | 508 | 1 | 205 | 0 | 0 | Entry | Return to dungeon |
| TRIGGER | 206 | 508 | 1 | 206 | 0 | 0 | Cliffs | To Cloud Cliffs |
| DEST | 207 | 508 | 0 | 463 | 207 | 13 | Cliffs | From Cloud Cliffs |
| TRIGGER | 210 | 508 | 1 | 210 | 0 | 0 | Temple | To Ancient Temple |
| DEST | 211 | 508 | 0 | 467 | 211 | 18 | Temple | From Ancient Temple |
| TRIGGER | 212 | 508 | 1 | 212 | 0 | 0 | Entry | To Pagan (Map 8) |
| DEST | 213 | 508 | 0 | 469 | 213 | 8 | Entry | From Pagan return |

## Monster Eggs

| Zone | Count | Monster Type | Notes |
|------|-------|-------------|-------|
| The Lake | 4–6 | Water Zombie | Around lake edges |
| Wilderness areas | 3–4 | Various | Between zones, random encounters |
| **Total** | **7–10** | | |

## Item Estimate

| Category | Count | Notes |
|----------|-------|-------|
| Glob eggs | ~1,500 | Terrain tiling for ~50×50 area |
| Wall/cliff shapes | ~400 | Valley boundaries |
| Building shapes | ~300 | Two villages + dwelling |
| Roof shapes | ~100 | Building roofs |
| Decoration shapes | ~500 | Ruins, furniture, props, vegetation |
| Water shapes | ~200 | Lake + two springs |
| NPC shapes | ~16 | Villagers |
| Container shapes | ~30 | Chests, barrels, bags |
| Door shapes | ~15 | Building entrances |
| Egg shapes | ~25 | Teleports + monsters + triggers |
| Quest items | ~10 | Passage Stone, potions, keys, etc. |
| **Total** | **~3,096** | |

## Atmosphere and Art Direction

- The valley should feel vast but desolate — once fertile, now dying
- Scattered ruins of a formerly great civilization
- Two distinct water sources create the geographic division between clans
- The lake should feel dangerous — murky water, reeds, bones on shore
- Ezrekal's dwelling should feel isolated — away from both settlements
- The Sacred Circle should feel ancient and ceremonial
- Cloud Cliffs should be visible from the valley as a dramatic backdrop
- Sparse, struggling vegetation — not completely dead but clearly suffering
- "Cool fallen ruins" per Synopsis — broken columns, crumbled walls, overgrown foundations

## Dependencies

- Map 11 (Elemental Dungeon) for entry transition
- Map 13 (Cloud Cliffs) for cliff approach transition
- Map 18 (Ancient Temple) for temple approach transition
- NPC dialogue agent for conversation files
- Water Zombie art (if creating new monster shape)
- Test Plant art (Art List: "Test Tree/plant/fruit")

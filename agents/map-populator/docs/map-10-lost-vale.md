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

## Phase B ground (2026-10-16/17): the 1994 screenshots

The landscape pass below is history. The Vale's ground now comes from
`lv_map10_ground.py` (the `Field` heights: terrain chunks, `RELIEF`
tiers, the lake, `STAIRS`) emitted by `lv_vale_terrain.Field` in the 1994
materials (301 rock, 4 earth, 386 edges, 125 crests, 26-32 faces), and
eight 1994 screenshots (02, 09, 17, 18, 19, 20, 21, 22) are stamped
verbatim as vignettes (`vignettes/screenNN.json`, `vignette_place.stamp`).
After the stamp the build closes the shots into the field:

- `shot_closure`: field ground in the cells a shot shows no floor in (a
  lake cell it hides stays water), and the seam faces a shot's higher
  cells turn to the field, including the courses under a scarp the frame
  cut off above its foot (screen18's mesa);
- `shot_completions`: the huts the village shots show two sides of
  (`lv_hut1994`), screen17's stair tail; `stair_underfill` fills under
  the shot's floating step blocks;
- `under_floors` / `shot_supports`: floors under half-lattice crests, under
  partial-art tiles (screen21's 781:0) and under screen17's body 405;
- `shot_rails` and the shots' own lake rails (`rails(f, shots=True)`);
- `band_plates`: a crest plate under any floor a course above the floor
  south or east of it where nothing draws the step (never inside a frame).

One shot item is moved, along the view ray only (`RAY_SLIDES`, through
`vignette_place`'s `slides`; same pixels, other boxes): screen17's top
stair block 107:1, four steps down to top 112, because at its solved top
120 the Avatar on the shelf closed `107 -> 107 -> 1 -> 125` at pad 210
for the whole endgame scene (verify3 F1; `test_paint_cycles` section 8
now stands him on every arrival pad and shot Avatar spot).

Faces whose 48 courses stop above the ground (tiers of 64, 112, 160 over
the 0 floor) get a crest plate at the foot (`lv_vale_terrain.foot`), as
retail stands such faces on a floor at their own base. Shore cells draw
their bank with a crest whose frame shows the visible sides
(`visible_role`). Single jag notches in a `RELIEF` edge and lone island
cells in the lake are filled in.

Pin moves the shots imply are recorded in each vignette's
`placement.pin_moves`: pad 210 with its eggs to (18432,22719,112) on
screen17's shelf, Hrodny's chest into screen20's hut at (21216,8768), the
wave-2 zombie egg and wave-3 trigger onto the causeway (screen02), the
wilderness kith egg of group 3 to (10463,17312) (screen09's tarn shelf),
and Atli's start one unit off screen19's door jamb. Scores, tests and open
issues: `docs/research/2026-10-16-screenshot-reconstruction/phaseB/map10/REPORT.md`.

## Zone Details

**Landscape pass 2026-09-15** (cleanup plan section 3, `build_map_10.py`,
`lv_landscape.py`). What the map had: a flat quilt of moss-cobble globs
with 256-spaced cave-wall pickets for every zone edge (a 50% hole per
piece), 19 chimneys (721) as pillars and columns, six roof squares
floating at z=12 over Ezrekal's shack, blue water-rock (126) and red
brick (127) as crops, a mushroom and a chimney "ruin" on the open lake,
80 chunks of black void inside the outline, and two quest sites — the
Passage Test grounds (24-unit terraces) and Ragnar's cache (16- and
24-unit steps) — that a walking actor cannot reach (the engine steps
0/±4/±8 and nothing else; `test_route_reach.py` now has goals for both).
Now: one `TERRAIN` table gives every chunk its ground and the holes are
filled; the vale is closed by a rim of cliff (two 48-unit courses on the
128 stride with a rock crest, generated from the table's edge by
`lv_landscape.rim`, standing in the void so no ground is lost); worn
cobble tracks (425) join the arrival court, both villages, Ezrekal's, the
lake shore, the Sacred Circle and both approaches, and a gravel riverbed
(6) runs from the north rim to the lake; the villages keep every hut and
NPC and gain a palisade with gates on the track lines, their crops
bushes; Ezrekal's is a roofless wood-plank stockade; Moriens' birthplace
and Ragnar's cache are stone ruins (the stool "plaque" went — nothing
read it); the Sacred Circle is eight standing stones on pale paving with
the Sacred Rock a monolith 64 units off the seed cell; the lake has a 3×3
deck and a two-lane pier; the cloud approach a flagstone terrace under
its pinned pad, gate and trigger, between canyon walls; the temple
approach a three-lane paved way with a colonnade and a forecourt; dead
trees and rock outcrops on the open ground; the corridor to the test
grounds a ramp of eight 8-unit rows and the cache a stepped stair. Both
quest gates (locks 170 and 180) match no key on any map, so each stands
in two stubs with a lane open beside it. Every pinned item is where it
was (`map_pins.json`). Hygiene row zero; route 70/70, walkability
137/137; fourteen sites shot in-engine at 640×400.

One engine fact this pass found (`lv_landscape.py`, `lv_shapes.py`): a
zero-height tile laid over a glob floor is sorted by the flat rules, and
an SI_DRAW flat (301, 386) or an SI_OCCL one is drawn UNDER the floor —
invisible. Overlays must be flats with neither flag (6, 71, 425, 783).

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
- Key to Hrodny's chest: NOT placed. Asking her "How can I open the temple?" pops a bag holding it (1994 HRODNY.UNK:1117-1120). A placed "lost in the village" key existed 2026-03..10 and was removed 2026-10-11.
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
| Tyorvi | Hoskuld Village (start and home slot; stash slot by the Gunnar still-house) | TYORVI.UNK | Hoskuld | Key to Clouds |
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

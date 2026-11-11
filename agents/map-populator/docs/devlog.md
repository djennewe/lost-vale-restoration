# Map Populator — Development Log

## 2026-03-21: Full Map Assembly Complete

### Session Summary

Built all 7 map tasks (F1-F8) in a single session, producing a complete
FIXED.DAT with 48 maps and 92,954 total items.

### Work Completed

**F1: Map 8 Modification**
- Added 11 items to existing Map 8 (Plateau)
- Functional double door (shape 114, lock ID 150) at Bonecrusher's Cave (~2560, 1536)
- Key placed in chest nearby (shape 641, matching lock ID)
- Teleport trigger ID 200 behind doors -> Map 9
- Teleport dest IDs 201 (return from Map 9) and 212 (return from Map 10)
- Teleport trigger ID 213 (go from Map 8 to Map 10, after first visit)
- Decorative torch sconces and rubble

**F2: Map 9 — Galjeron's Chamber (148 items)**
- 3 zones: entry passage, main chamber, deeper passage
- 26 glob eggs for cave floor terrain
- Galjeron's dead body (shape 400, frame 7) with journal (shape 158) and backpack
- Guardian monster egg (quality 20) in lair area
- Bones, stalactites, rubble, 4 torch sconces
- 4 teleport eggs: IDs 200 (dest), 201 (trigger), 202 (trigger), 203 (dest)

**F3: Map 11 — Elemental Dungeon (1,771 items)**
- 7 zones: entry hall, central hub, earth/air/fire/water sections, four pillars, teleporter pad
- 584 glob eggs across varied dungeon terrain types
- Earth section: 4 monsters, talisman (quality 101), maze walls
- Air section: 3 monsters, elevated platforms (z=16-100), talisman (quality 102)
- Fire section: 5 monsters, lava pools (shape 318), flame traps, talisman (quality 103)
- Water section: 5 monsters, flooded chambers, dry islands, talisman (quality 104)
- Four pillars: 4 pillar/receptacle pairs (qualities 201-204)
- 4 teleport eggs: IDs 202, 203, 204, 205

**F4: Map 10 — Lost Vale Overworld (1,701 items)**
- 10 sub-zones as specified in design doc
- 1,008 glob eggs covering ~50x50 chunk area
- 16 NPCs placed across Hoskuld Village (7), Gunnar Village (9), Ezrekal (1)
- Quest items: Passage Stone, Hrodny's locked chest, Tiny Tar potions, key
- Test Area with PLNTST usecode trigger
- The Lake with 5 water zombie monsters and passage stone on island
- Sacred Circle with stone arrangement and SHADES trigger
- Cloud Cliffs approach with locked gate (key ID 170) and teleport pair
- Temple approach with gate and teleport pair
- Birthplace of Moriens ruins (optional lore area)
- Connecting terrain with scattered ruins and wilderness monsters
- 8 teleport eggs: IDs 204-213 (all required connections)

**F5: Map 13 — Cloud Cliffs (599 items)**
- 7 vertical zones using full z-range (0-120)
- 238 glob eggs for cliff terrain
- Base zone with locked gate (key ID 170)
- Progressive elevation: lower cliffs, warning zone, switchbacks, narrow ledge
- Harpie zone (z=96-112) with 4 monster eggs (quality 40)
- Summit plateau at z=118-120
- Bones/skeletons scattered throughout warning zone and ledges
- 4 teleport eggs: IDs 206, 207, 208, 209

**F6: Map 17 — Cloud City (714 items)**
- 7 zones: arrival plaza, main plaza, 2 god halls, scroll chamber, memorial hall, cloud platforms
- 189 glob eggs for white stone architecture
- Magnetic Obelisk with MAGNET usecode trigger (standard egg, quality 3)
- Message Scroll (quality 80) in scroll chamber
- Two skeletons with Shield Halves (qualities 81, 82) in memorial hall
- Collapsing ground hazards (damage tiles)
- Cloud platforms with gaps and stepping stones
- 2 teleport eggs: IDs 208, 209

**F7: Map 18 — Ancient Temple (407 items)**
- 4 zones: temple exterior, outer hall, transition hall, inner sanctum
- 92 glob eggs for temple floor
- Temple guardian monster (quality 50) in outer hall
- Tiny Tar entry with POTION usecode trigger (standard egg, quality 4)
- Three Zealan gods encased in resin: Felicitar (q301), Doloras (q302), Timyra (q303)
- Central altar (quality 310) with FREE usecode trigger (standard egg, quality 5)
- 2 teleport eggs: IDs 210, 211

**F8: Assembly**
- Loaded base FIXED.DAT (42 maps, 87,603 items)
- Added Map 8 modifications (11 items)
- Added 6 new maps (5,340 items)
- Verified all 14 teleport pairs (200-213) — ALL OK
- Saved to shared/build/FIXED.DAT
- Reload verification: 48 maps, 92,954 items confirmed

### Architecture Notes

Each map has its own builder script (`build_map_NN.py`) that returns a list of
MapItem objects. The assembly script (`build_all_maps.py`) orchestrates loading,
building, verification, and saving. This modular approach allows individual maps
to be modified and rebuilt independently.

### Shape Selection Rationale

Key shape choices documented in each builder script header. General approach:
- Terrain: existing globs from GLOB.FLX (indices 40-80 range)
- Walls: shapes 26-32 (directional cliffs), 145-155 (building walls), 489-490 (stone walls)
- Water: shapes 347, 669, 710, 738
- Damage: shapes 318 (lava), 435-438 (flame traps), 636 (ground damage)
- Doors: shapes 68/69 (standard), 114 (large gate)
- Containers: shapes 205 (chest), 208 (barrel), 307 (crate)
- NPCs: shape 400 (placeholder — needs proper art)
- Quest items: shape 580 (gem/talisman placeholder)

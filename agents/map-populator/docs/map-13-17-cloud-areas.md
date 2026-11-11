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

### Layout (rebuilt 2026-10-17 round the 1994 shots)

Five published 1994 shots are of this map (screen01, 13, 14, 15, 16) and
are placed verbatim; everything else is extrapolated in their grammar
(`lv_map13_tiers.py`; window fit `map13_window_fit.json` by
`lv_map13_views.py --fit`). Report:
`docs/research/2026-10-16-screenshot-reconstruction/phaseB/map13/REPORT.md`.

```
  y 1279-1407  the north leg's dead end (CLIMB_STUB, z 120): its three
               lanes run one row past the turn west and stop
  y 1535-1663  summit leg (z 120) west over the cloud sea onto the
               plateau's NE corner; harpie trigger 2 at (4863,1663)
  y 1663-2431  summit plateau = screen01 (z 120); trigger 209 across its
               south (4351,2303); harpie eggs (4287,2175)/(4287,2047)
  x 5247-7039  screen13, the city edge (z 120): retail earth (4 f30-33,
  y 1151-2687  carried 2 cells past the shot), the 1994 cloud patches
               (874) and the gold street's corner (876), open to the
               turn's east lane; an island over the cloud sea, which runs
               on east to x 8191 north of y 4095 (CX_EAST, CY_EAST)
  x 5119       north leg, z 68 -> 120 by y 2687; pad 208 on it (5119,2303);
               rest point (5087,3039); harpie lane pair y 3967, trigger 1
               (5119,4479); screen14's skull ring path joins at (37,35-36)
  y 5631-7679  the lake: screen15 (stepping stones), screen16 (causeway
               landing) - jump-only, curbed off the climb
  y 7935       east leg along the lake's south shore, z 64 -> 68
  x 4095       lower leg, z 0 -> 64, from the climb's foot (4095,10239)
  y 10240+     the valley (z 0): pad 207, trigger 206, EggCloudCliffs,
               the ruined wall
```

The summit is entered from the north-east because screen01 shows the
ground south and east of its plateau lower: a climb tile at 120 there drew
over the shot's bone pillar. Trigger 209 is crossed heading south.

**No bounce between 13 and 17 (2026-10-17, pass d).** From pad 208 a
keyboard hold NE used to wall-follow N up the leg, W along the summit leg
and S into trigger 209 in 3.5 s (verifier finding 6). The leg's dead end
(`CLIMB_STUB`) stops it: a hold up the leg still has north to go past the
turn. `test_route_reach` holds both pads (208 here, 209 on Map 17) in all
8 headings, every mode, moving and standing, for 8 s: none reaches a
trigger (in the mover, none in 16 s either). A pad on screen13's island
was tried and bounced (keyboard W/N runs wall-followed onto the summit
leg), so pad 208 stays on the leg, three cells from the island.

### Vertical Design

**Dressed as a cliff 2026-09-15** (cleanup plan step 5, `build_map_13.py`).
What the map had: the climb polyline rising over a flat green field, each
zone's "cliff walls" one 48-tall course at z=0 — so from the ledge at z=96
the walls were far below and the map read as a ramp between two fences;
bone piles at z=34..48 four hundred units off the path, rocks at z=8+2i,
cliff-detail pieces at z=80+2i and 36 harpie-zone tiles at z=96..107 with
1-unit risers, all phantom standing levels by the 4-unit-lattice rule; and
the wide lanes in shape 128, which draws as bright blue tiles. Now each
zone's flanking walls are stacked in 48-unit courses to the path's height
in that zone plus one (`zone_walls`), so the canyon deepens as you climb;
one or two courses of rock sit under the drop side of every path tile from
z=48 up with their tops flush with the ledge (`build_ledge_faces`); the
wide lanes are the path's own shape 3; dressing sits on the valley floor
or on the path's lanes at the path's z; the gate stands in two stone
stubs with the valley open beyond them (lock 170 matches no key on any
map — TODO.md §4 row 13); and a colonnade ruin marks the summit.
`climb_tiles()`, `CLIMB_WAYPOINTS`, `CLIMB_WIDE` and every pinned egg are
untouched. Hygiene row zero; route, riser and lattice checks green; base,
lower cliffs, switchback, ledge and summit shot in-engine at 640x400.

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
| pad | 207 | (4096,11776,0) | Arrival from Map 10 |
| trigger | 206 | (3328,11520,0) | Return to Map 10 |
| trigger | 209 | (4351,2303,120) | To Map 17, across the summit plateau |
| pad | 208 | (5119,2303,120) | Return from Map 17, on the north leg |

### Monster Eggs

| Group | Trigger | Eggs | Notes |
|-------|---------|------|-------|
| 3 | (5119,6143,76) | (5183,5631,76) | first lane harpie (2026-10-24) |
| 1 | (5119,4479,84) | (5183,3967,96) | second lane harpie (2026-10-24; was a pair) |
| 4 | (5119,2687,120) | (5183,2175,120) | top of the north leg (2026-10-30) |
| 2 | (4863,1663,120) | (4287,2175,120) | summit (2026-10-30; was a pair) |

Every wave is one harpie (Douglas, 2026-10-24 and 2026-10-30). Rest point
between the lane and the top: `HARPIE_REST` (5087,3039,112).

### Dressing (2026-10-17)

`build_dressing`: 66 spire clusters with 152 stumps and 138 cracks at
retail's density (about 7 per 100 dressable cells; retail's 301-floored
maps run 1-20, median 8), clustered as retail clusters them, plus a bone
scatter (235/332/358/219) on ledges in sight of the walk. Only on ground
nobody walks (and the valley's cliff feet off the arrival ground), and
never where a piece's projected box could reach a 1994 window.

### Shot edges, cloud holes, paint cycles (2026-10-17, pass c)

- Under screen01's cloud lies a filler cloud (`cloud_fill`): the plane's
  lattice tile slid down the view ray, so it shows only through the holes
  the shot's 32-unit cloud grid leaves.
- The shots' own cells get completion faces down to lower generated
  ground (`shot_faces`), and north/west faces beside a shot or void are
  drawn rather than black (`exposed`), except where a piece could draw
  into a window. The window fit refuses completion pieces per side.
- Riser crests cover every side a lane steps down on; a lip stack ends at
  z 0 with no gap.
- Three shot pieces are moved along the view ray or cut to their in-window
  part (`RAY_SLIDES`, `SHOT_CUTS`); this closed the two paint cycles the
  engine logged on this map. `test_paint_cycles` section 6 frames the whole
  climb and summit.
- Both left open here were done in pass d (same day): the pad 208 →
  trigger 209 wall-follow (the leg's dead end, above) and screen13 (the
  city edge, east of the turn: built window 75.92 / class 75.97 against
  its replay's 75.97). `test_paint_cycles` section 6 now frames the dead
  end and every cell of screen13's island too.

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

### Layout (rebuilt 2026-10-17: the open 1994 city)

`build_map_17.py` now builds the city the two published 1994 shots show.
The shots are stamped in verbatim (`vignette_place.stamp`), and the rest
is built around them in their own pieces. The stone rooms, tapestries, lamps
and daises of 2026-09-15 are gone. Evidence and scores:
`docs/research/2026-10-16-screenshot-reconstruction/phaseC/map17/REPORT.md`.

North (low y) is up-right on screen. The processional runs from the arrival
in the south to the throne nook in the north:

| Place | World (x, y) | What |
|---|---|---|
| Arrival landing | 3200-6016, 9472-10496 | Gold. Pad 209 at (4608, 9984) with EggReapply. Drum colonnades on both flanks. Plaque 68 on a stele. |
| Channel and pier | y 10496-11264 | A void channel, curbed both sides. Trigger 208 (4608, 11008) is on the cloud pier beyond it, reached only by the bridge at the channel's east end (x 5760-6016). |
| South street | 4224-4992, 7936-9472 | Gold, gem pillars every 256. Plaque 55 on a stele south of the plaza. |
| Obelisk plaza (screen11) | origin (1280, 4736, 0) | All cloud. The retail obelisk (12 f14-f17, cap 545, skull 814) on four banded drums. A ring of gem pillars, the skeletons, and the sun Shield half (878 f0, q81). Screen11's outer square of plain columns is carried round. |
| Processional street | 3712-4480, 4480-6144 | Gold, gem pillars. Plaques 69/70 on steles at its head. |
| Walkway and throne nook (screen12) | origin (1024, 1024, 0) | Two raised marble strips (877, top z 8) at y 3103 and 3583, running x 1663-6655, with banded posts on both sides every 192. Gold aisles between them. The nook holds throne 223 and the eye Shield half (878 f1, q82). Gold forecourt to the south. |
| East court | 5632-6912, 4864-6272 | Gold, a grid of gem pillars, reached along strip C (y 5759). |
| Scroll court | 2688-3968, 1024-2048 | Gold. The Message Scroll (3328, 1536, 8) sits on a marble plinth, with drums and gem pillars round it. |

**Materials and edges:**
- Floors are the 1994 cloud 874 (f0-f2) and gold 876, all at z 0.
- Gold areas have ragged two-cell lobes.
- The cloud runs 8-10 cells past every feature, and the rim is smoothed.
- Void lies only beyond the cloud's edge. Retail's invisible curb (497/498) guards every walkable side facing it.
- Black void plates (`void_floor`) cover the void in view.

**Gem pillars** are the white column 875 f0 with a gem on top. The gem is 880, a fixed copy of retail 596. The shot's own 596 is `TypeTalisman`, which a player could carry to a Map 11 receptacle.

**Shot windows stay exact:**
- `window_clear` drops any generated item that would paint into either shot's window.
- Each built window equals its vignette replay pixel for pixel: screen11 99.929%, screen12 87.413% class.

### Magnetic Obelisk Puzzle

The MAGNET.UNK usecode pulls the Avatar's magic items to the obelisk. It is
still unplaced (`derive_map_pins` DEFERRED, EGGMAGNET q281), for four reasons:
- it depends on H1's process semantics;
- no candle can be lit;
- the ankh arrangement is undecided;
- the hard-coded pop target (15615, 19839, 120) has to be retargeted.

The obelisk's front drum (4127, 7199, 0) carries quality 90, and that is
where the egg goes once the work is done.

### Key Items

| Item | Shape | Location | Notes |
|------|-------|----------|-------|
| Message Scroll | 864 q80 | (3328, 1536, 8) | Route-test pinned |
| Shield Half 1 (sun) | 878 f0 q81, npcnum 236 | (4259, 7199, 0), screen11 | `TypeAOFrizbee` = 878 |
| Shield Half 2 (eye) | 878 f1 q82, npcnum 236 | (3559, 3311, 0), screen12 | |
| Gold plaques | 614 q55/68/69/70, npcnum 235 | On steles | Class 1259 |

### Teleport Eggs

| Type | ID | Position | Notes |
|------|----|----------|-------|
| Arrival pad | 209 | (4608, 9984, 0) | From the Cloud Cliffs. A hold in any one direction reaches no trigger. |
| Trigger | 208 | (4608, 11008, 0) | Back to the Cliffs, round the channel. |

---

## Combined Cloud Area Dependencies

- Map 10 (Lost Vale) for Cliffs approach
- Harpie monster shape (new art or placeholder)
- Key to the Clouds (TypeCliffKey) mechanics
- MAGNET usecode implementation
- Shield half item shapes (TypeAOFrizbee)
- Cloud terrain tiles (optional — can use existing shapes creatively)

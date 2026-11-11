# Map cleanup plan, 2026-09-14

The work queue for bringing the other Lost Vale maps up to the standard Map 18
reached today (`cf12959`, `5c88d3a`). Companion to
`agents/map-populator/docs/map-18-ancient-temple.md`, which records what was
done there and why; this document says what to do with the rest, in what
order, and what must not move. `TODO.md` §4 carries the checkboxes.

Every number below was measured on 2026-09-14 against the built `FIXED.DAT`
(hash `c39b9c…`) with globs expanded, or counted in the builder source. Where
a count is from the whole map on a base-game slot (08, 39) it says so.

## 1. What Map 18 taught

Three defect classes, one method.

**The defects.**

1. **The lattice.** Glob 80 is not a floor tile — it bakes four 40-tall wall
   pieces along each chunk's south edge. Tiling it stamped a grid of stubs
   every 512 units. Only Map 18 tiled glob 80 (measured across all eleven
   tiling globs the builders use), so this exact defect is gone from the
   project. Its *family* is not: **chunk-stride placement of an item that
   does not span a chunk** — one 128-unit roof or ceiling tile per 512-unit
   chunk, 6% cover, drawn as a grid of floating squares. That loop shape
   exists in 09, 10, 11 and 17.
2. **Stacked wall tops.** Shapes 489/492 are wall *ornaments* — gargoyle
   caps, carved corners, barred windows — that the base game sets on top of
   walls (177 and 119 uses in all 42 retail maps). Runs built from them read
   as rows of wall tops stacked on each other. The base game's stone wall is
   the shape-10 (north-south) / 15 (east-west) pair, 5,550 and 4,314 uses,
   plain frame 1, carved-face frames 10 f5 / 15 f0. Map 17 has 148 of 489
   as walls; 09/10/11/13 build their cave walls from 26/32, which is right.
3. **No design.** Chimneys (721) standing in for columns, stools (158) for
   inscriptions, chests for "ceremonial decoration", wall reliefs (295) adrift
   mid-floor, and floors laid as a uniform quilt. The temple's answer was a
   *kit* pulled off contact sheets of what the base game's own interiors
   place — columns on plinths, raised flagstone platforms, tapestries and
   lamps on the two wall faces the projection shows, candles, pews, urns —
   and one authored brief per zone.

**The method, per zone, in this order.**

1. Floor: the wall-less glob (65 for flagstone; the cave/terrain globs are
   already clean). Every wall placed explicitly, one doorway per boundary
   where the circulation goes, sized on purpose (`wall_run_x/_y` with
   `gaps=`; a one-body aperture is sized by `Box::overlaps`, never by the
   cell flood — `.claude/rules/map-geometry.md`).
2. Walls: 10/15 for stonework (`accent_reliefs()` idiom for the visible
   faces), 26/32 for cave. Never 489/492 as a run.
3. Remove every chunk-stride grid, every 721 that is not a pinned quest
   item, every loose 295, every stool/chest "decoration".
4. Brief the zone in one paragraph — what it is for, what the player does
   there, what they should see — and dress it from the kit and from the
   base-game reference map for that kind of space (§3 names one per map).
   Render the reference region first (`iso_render.py --map N --x --y --w
   --h`, or `map_preview`'s `expand_globs` path when the CLI drops shapes).
5. Verify: builder → `build_all_maps.py` → the estate → `map_walkability`
   for that map → in-engine on a fresh world at 640x400 (`width=640
   height=400 aspect_ratio=false scaler=normal scale_factor=1` in
   `scummvm.ini`; the engine has no zoom, so a 2x canvas is the "zoomed out"
   view) → walk the map's quest steps from
   `docs/playtest-2026-09-07-full-run-1-18.md`.
6. `/artifact-rehash`, one commit per map, `TODO.md` §4 row updated with the
   date and what ran in ScummVM.

## 2. What binds every map

- **Pins are an inventory, derived, not a list from memory.** The first
  draft of this section named things from the 2026-07-19 audit that the
  compiled sources no longer bear out (found by the 2026-09-15 review of
  `d178ff9`): the active `lv-patched/PLNTST.UNK:72` filters
  `TypeShortmushroom`, not `TypeStatue` — and (the derivation found,
  2026-09-15) `TypeShortmushroom` is shape 126, the single Test Plant
  beside its egg, while the eight ring items are shape 65, so the whole
  Sacred Circle dressing including the central 721 is decorative; Map 17's MAGNET egg is deliberately absent
  (`build_map_17.py:248` onward — four blockers, the first an engine
  semantics question) so its obelisk is a placeholder nothing reads today;
  and its "plaques" are 158s carrying quality 6 while `TYPENSGOLDPLAQUE`
  (1259) is unplaced because no LV quality exists for it
  (`shared/docs/wiring.md`). So Phase 0 produces
  `agents/map-populator/src/map_pins.json` — one row per object with map,
  shape, frame, quality, npcnum, x, y, z and a class:
  **active** (something compiled reads it now: the four elemental pillars
  and receptacles, qualities 201–204, `TypeElementalColumn`; the four
  talismans; the Passage Test plant ring and `TypeBushKey`; every wired
  egg; every teleport pair; NPC starts; the sealing boulders),
  **decorative-with-quality** (placed for a future wiring: the Sacred Rock
  721 q100, the obelisk, the 158 "plaques"), or **deferred** (a trigger
  removed on purpose — MAGNET, the candle trick). Active rows are frozen
  unless a test moves with them; decorative rows may change shape and
  position freely, and their qualities are recorded so a later wiring finds
  them; deferred rows are never restored to satisfy a pin. The hygiene test
  (§4) reads this file. Derivation: grep every `foreach … type =` and
  `typeclass` in `lv-patched/` and `lv-new/` against `TYPE_SHAPES`, then
  the builders' quality constants against the compiled egg/class tables.
- **Pinned positions.** Teleport egg pairs (200–213), every shape-73 egg by
  quality, monster eggs, quest items (shield halves 539, key 82 q99,
  talismans 596, potions 859, the bag 637, the root/tea/elixir items) and
  NPC start positions must survive unmoved unless a test is updated with
  them. `test_route_reach.py` floods 09/10/11/13/17/18 from their arrival
  pads to their goals with the engine's box arithmetic; `map_walkability`
  suites cover 08/09/10/11/18/39 plus the event eggs; `build_all_maps.py`'s
  validator ratchets the WARN count downward. All of it must stay green
  after every zone, not just at the end.
- **z is a 4-unit lattice** and every riser is 0, 4 or 8 — the Map 13 climb
  (`CLIMB_Z_STEP`) and the rule above. Any raised platform is a step of 8
  per tile (the temple's `raised_platform`, top ≤ STEP_Z 24).
- **Roofs.** `CameraProcess::findRoof` takes any ROF-flagged item beside the
  Avatar for a ceiling and clips the room at its z. So: no ROF tile at floor
  level (77 is out; 113/70 are the platform kit), and a roof is either
  continuous at 128 stride over the whole room or absent. The base game's
  interiors stand open to the black; absent is the default.
- **Circulation is designed, never accidental.** The 2026-07-30 note in
  `TODO.md` §4 is the scar: Maps 10 and 17's walls were solidified and
  sealed their routes, because the holes *were* the doorways. Every boundary
  gets its doorway from the route the player walks, then the Avatar-width
  flood proves it.

## 3. The maps

Ordered by the player's route, which is also close to the order the work
should go (§4). "Session" means a day like the temple's: four zones,
~1,000 items, verified in-engine and committed.

### Map 09 — Galjeron's Chamber (198 items; 3 zones; ½ session)

**Now.** Cave walls 26/32 (right), floor globs 45/48 (right). Ceiling
squares 37 ×16 and 34 ×4 placed one per chunk at z — floating. Wall reliefs
295 ×6 adrift. Rock slabs and a "red square" grid in zone 1, crates in zone
3, planters on a grid. The first thing the player sees of the expansion.

**Reference.** Bonecrusher's cave on Map 8 (the retail geometry the player
just walked through — match it) and the catacomb rooms of Maps 49–51.

**Brief.** Zone 1: a cave throat, low, stalactites (186), rubble (66/300),
one bone pile (235/237) as foreshadowing. Zone 2: Galjeron's body and his
effects as the design doc has them — the journal, the pack — with the
guardian's lair read as a lair: bones, a dragged carcass, claw-scored
walls (26/32 have a scored frame set). Zone 3: the cave giving way to
worked stone — the first 10/15 courses and a carved-face relief or two
where the Zealan masons started, leading to trigger 202.

**Pinned.** Teleports 200/201 (Map 8), 202/203 (Map 11); monster egg; the
journal (TypeBook, 613); route 09 in `test_route_reach.py`; walkability
`run_map9`.

**Do.** Drop the 20 ceiling squares and the 6 reliefs; cave ceilings only
where continuous (the throat). Replace the slab/red-square grids with
authored props. Keep every wall as 26/32.

### Map 11 — Elemental Dungeon (2,593 items; 9 zones; 2 sessions)

**Now.** The worst grid artefacts on the project after Map 18's: 138 rubble
ceilings (9) and 282 cave ceilings (34) on chunk stride, drawn as red
diamonds over every room; 48 wall reliefs; 6 chests; 6 chimneys of which
four are the pinned pillars and two (hub, `build_central_hub` lines 234–235)
are decoration. Cave walls 26/32 (right); floors glob 42 and 65. The
sections are square rooms joined by long straight corridors — readable as a
diagram, not a place.

**Reference.** The Planes: Map 44 (Fire, 2,523 items, 96 shapes) for the
lava idiom, Map 45 (Water) for flooded floors, Map 46 (Air, 385 items) for
floating platforms, Maps 49–51 (Catacombs) for Earth and for the corridors.
Render each before dressing its section.

**Brief.** Entry hall and hub as worked stone (10/15, columns on plinths,
lamps) so the contrast with Map 9's cave lands. Earth: cave (26/32),
boulders, collapsing-floor traps where the doc puts them, the talisman in a
rock-walled alcove. Air: platforms as `raised_platform` tiers stepping up
on the 8-lattice with real gaps, translucent shapes where the base game
uses them on 46. Fire: dark floor (35 frames 4/5), lava pools (318 and the
435–438 set) laid as pools with stone walkways between, torches (568) on
sconces. Water: 347/669 water with island floors, the walkways partly
submerged. Four Pillars chamber: the pillars stay 721 (pinned) but stand on
a dais each, receptacles beside them, the room otherwise the temple's kit.
Corridors: doorways at each end, a lamp every 512, nothing else.

**Pinned.** Teleports 202/203 (Map 9), 204/205 (Map 10); the four pillars and
receptacles (qualities 201–204 and their partners); the four talismans (596,
at z=4 — `docs/playtest-2026-09-06-step4-talismans.md`, do not lower them);
the sealing boulders (`SEALING_BOULDER_QUALITY`, route 11 in
`test_route_reach.py` proves both states); monster eggs; `run_map11`.

**What stays fixed, stated once.** The brief above changes geometry —
tiers, gaps, lava, water — and geometry changes traversal and damage
without a line of usecode. So the boundary is: every active pin's
coordinates, z and quality are frozen; the four routes arrival → talisman
and the route arrival → pillars chamber → teleporter 204 are added to
`test_route_reach.py` as goals *before* the section is dressed, and must
stay reachable by the full-size body with no damaging tile on the proven
path (extend `route()` with a "no DMG-flag item under any reached cell"
assertion); platform tiers are 8-unit steps on the lattice, and a gap is a
gap only where the flood proves the far side is still reached by the
intended way round. Collapsing floors, lava mazes and flooded rooms as
*mechanics* — where the player can be hurt or cut off — are puzzle content
and belong to §6, not this pass. Acceptance is the extended route test
green plus step 4 (four tokens, way opened) walked in-engine on a fresh
world.

**Do.** Delete both ceiling grids (420 items), the 48 reliefs, the chests,
the two decorative chimneys. Dress the five rooms per the brief within the
boundary above.

### Map 17 — Cloud City (726 items; 8 zones; 1½ sessions)

**Now.** The ugliest map left: 148 ornament pieces (489) as every wall, 37
chimneys as columns, 100 roof squares plus 60 rubble ceilings on chunk
stride, 5 stools of which some are the pinned plaques, 5 chests, 4 reliefs.
Floor glob 65 (right; the `GLOB_CLOUD_FLOOR = 78` constant is an empty glob
and is unused — delete it). `TODO.md` §4 still says "glob 78 not rendering";
that row is stale.

**Reference.** Tenebrae's palace and halls on Maps 40/41 (the grandest
retail interiors: 249 columns, 328/329 tapestries, 289 thrones, 226/231
benches, 452 candelabra) for the halls; Map 37 (Argentrock, the monastery)
for pale stone in the open; the temple itself for the kit.

**Brief.** Arrival plaza: an open pale-flagstone square (35 frames 4/5 over
the glob, or the glob's own), a colonnade on two sides, fallen banners
(tapestries at z=0 lying flat is not possible — use 812 cushions and 229
urns as debris, and leave gaps in the colonnade where columns "fell"). Main
plaza: the obelisk (pinned 721 until art) on a two-tier dais at the centre,
paths of raised flagstone radiating to the halls, the collapsing-ground
tiles where the doc puts them. God's Halls A and B: two thrones (289 frame
1, the empty one), a dais each, tapestries, the plaques (pinned 158) on the
dais steps where a reader would stand. Scroll chamber: small, a desk (205),
candlesticks, the scroll. Memorial hall: the two skeletons and halves as
placed (2026-07-19 fix stays), the room otherwise bare stone — the one room
with no colour. Cloud platforms: `raised_platform` tiers with real gaps,
translucent 703-style effects only if the base game's 46 uses them there;
the cloud *tiles* themselves are custom art (§5) and the platforms should be
built so a later tile swap is one constant.

**Pinned.** Teleports 208/209 (Map 13); the two skeletons (332) and shield
halves (539); the scroll; route 17 in `test_route_reach.py` (arrival to the
memorial hall and back). **Decorative-with-quality, free to move:** the
obelisk (721, `QUALITY_OBELISK`) — its MAGNET egg is deliberately absent and
MAGNET.UNK pops inventory to a hard-coded (15615, 19839, 120) that must be
reconciled when that puzzle is wired, so record the obelisk's new position
in `map_pins.json` and leave the egg out; the four 158 "plaques" (quality
6) — `TYPENSGOLDPLAQUE` is unplaced, nothing reads them, so they can become
real plaque shapes (599/614) as decoration today, quality kept.

**Do.** Replace every 489 with 10/15 runs and designed doorways (this is the
map the 2026-07-30 solidification sealed — the flood test now exists, so
design the doorways first, then wall). Delete 160 roof/ceiling squares, 37
chimneys (all but the obelisk), the chests and reliefs. Dress the eight
zones. The validator's WARN ratchet is already at zero
(`test_map_roundtrip.py`, `MAX_KNOWN_WARNS = 0`), so there is nothing for
this map to bring down there.

### Map 13 — Cloud Cliffs (776 items; 8 zones; 1 session)

**Now.** Structurally the best of the four: a verified, walkable climb on
the 4-unit lattice (`docs/playtest-2026-09-01-stock-bindings-climb.md`)
with cave walls 26/32 as the ledge edges and glob 52/49 terrain. What it
lacks is a cliff: the preview reads as a green ramp with parallel fences.
No 489/492, no grids.

**Reference.** The Plateau's cliff faces on Map 8 (shape 125, 26–32 in
their cliff frames) and Argentrock's shore cliffs on Map 37.

**Brief.** Keep every z of the climb polyline exactly. Against its outer
edge, build the drop: cliff faces (125) below each ledge in stacked courses
so the height is visible, boulders (300/796) and rock spires (66) on the
inside, bones (235/237) on the warning-zone ledges, the harpie nests as
bone-and-rubble clusters at the eggs. The gate at the base as a real gate
(114) in a 10/15 wall. Summit: a flat pale plateau with the teleport in a
small colonnade ruin — the first sight of the city above.

**Pinned.** Teleports 206/207 (Map 10), 208 (Map 17); the locked gate
(quality = `TypeCliffKey`'s lock); the 4 harpie eggs; the climb waypoints
(routes 13 in `test_route_reach.py`, `climbto.py`/`hike.py` in the
harness). Re-run the base→summit walk after every zone; a decoration that
lands on a ledge at off-lattice z is a phantom standing level.

### Map 10 — The Lost Vale (3,090 items; 14 zones; 2–3 sessions, last)

**Now.** The overworld: barren-ground glob 40 ×1,240, village ground 43,
shore 55; two villages built by the prefab pipeline (`build_villages.py`,
`building_prefab.py` — the best-looking content on the map and already
glob-native); the lake (F4 said the shipped island differed from source;
the serialized item multiset matches the builder at `d178ff9`, so that is
no longer demonstrated — a lake/causeway playtest may still be owed); the
Sacred Circle (eight mushroom clusters, `TypeShortmushroom`, active; one
central rock, 721 q100, decorative); 20 chimneys, all decoration; 6 roof
squares; cave walls 26/32 as cliff lines. No 489/492. Reads as a flat quilt
with dots.

**Reference.** The Plateau (Map 8, 4,306 items, 152 shapes) for barren
terrain vocabulary — rocks, dead trees, cliff lines, paths — and the
outskirts of Tenebrae (Map 4/5) for village grounds.

**Brief.** This is landscape work, a different craft from the halls: the
brief per zone is a *view*, not furniture. Give the vale edges — cliff
lines (26/32/125) that close it — and give the interior relief: rock
outcrops, dead trees, a dry riverbed to the lake, worn paths (a 128-wide
run of a path tile between the villages, the Sacred Circle and the temple
approach). Villages stay as the pipeline makes them; dress the ground
around them (fences, wells, the huts' roofs in the terracotta frames the
docs asked for — `TODO.md` §4). The lake per F4. Ezrekal's dwelling and
Ragnar's cache ruins as ruins (the wood-plank set 856–858 exists for this).
The temple approach as a processional: the Map 18 court's colonnade begins
here.

**Pinned.** More than any map: eight teleports (204/205, 206/207, 210/211,
212/213), every NPC start position and loiter leash (`ee238a9`-era engine
work; F1), the Passage Test stone, its eggs and its mushroom ring
(`PLNTST`, `TypeBushKey`, `TypeShortmushroom`), Tyorvi's key/root/tea
items, the three Tiny Tar potions on clear floor
(`.claude/rules/map-geometry.md`, the F11 lesson), routes 10 in
`test_route_reach.py`, `run_map10` (the largest walkability suite). The
central Sacred Rock (721 q100) is decorative and may change. Work zone by
zone with the suite after each.

### Maps 08 and 39 — base-game slots (audit only, ¼ session)

The Lost Vale additions are 67 items on Map 8 (the double-door route:
darkness tiles, invisible blockers 497/498, cave walls) and 2–3 on Map 39
(the Lord British egg and apparition). Both were verified in-engine and
neither has the three defects — the 489/492/220 counts on those slots are
Origin's own. Audit the 67 for a stray grid or relief; otherwise leave them.

## 4. Order, and why

1. **Phase 0 — the inventory, the kit and the gate (1 session).**
   - `map_pins.json`, derived as §2 says, before anything else.
   - `lv_furnish.py`: the temple's helpers, generalised on the way out.
     `column()` hard-codes its plinth at z=0 (`build_map_18.py:116`) and
     `accent_reliefs()` embeds Map 18's north-line y values and west-wall
     x values (`:866`); they take a base elevation and a list of
     `(axis, coordinate, face)` wall lines instead. **Acceptance: the
     extraction alone leaves Map 18's serialized item list identical** —
     `test_map_roundtrip.py`'s capture before and after, and the `FIXED.DAT`
     hash unchanged. No other change rides in that commit.
   - `test_map_hygiene.py` over the built `FIXED.DAT`, one section per
     defect class, with the specification tight enough that the defect it
     names cannot pass it:
     - *Lattice:* raw glob eggs with quality 80 on any LV map = 0 (checked
       on the eggs, before expansion), and, after expansion, no shape-15/47
       piece at a chunk's south edge that no builder placed (the baked
       signature: x ≡ 127/191/383/511 mod 512 on a y ≡ 511 mod 512 line).
     - *Chunk-stride roofs:* group ROF-flagged items into 4-connected
       components on the 128 grid at equal z; a component fails if it has
       fewer than 12 tiles **or** its bounding-box coverage is under 90%
       (a pair repeated every 512 units has two tiles and passes a
       neighbour test — that is why coverage, not adjacency), unless its
       bounding box is inside a roof region the map declares; and every
       component's z is at least 40 above the highest walking surface under
       it (`findRoof` clips the room at the roof's z otherwise).
     - *Ornaments as walls:* 489/492 at z = 0 anywhere = 0; at z > 0 only
       with a 10/15/26/32 piece directly beneath.
     - *Placeholders:* 721, 158, 295, 78 not in `map_pins.json` = 0 for a
       cleaned map; 295 additionally within 32 units of a wall face.
     - *Ratchet:* today's counts per map recorded in the test, increases
       fail, and a map's rows flip to zero in the commit that cleans it.
   This is what stops the defects coming back while five maps are open.
2. **Map 09** — small, first impression, a warm-up for the cave idiom.
3. **Map 11** — the biggest artefact count and the longest quest stretch
   (steps 3–4).
4. **Map 17** — the ugliest, and the one whose walls have already sealed a
   route once; do it with the flood test in hand.
5. **Map 13** — dress a climb that already works; the z rule makes this the
   one where verification is the whole job.
6. **Map 10** — last because it is the largest, its villages are already
   the best content on it, and it carries the most pinned positions. Also
   because landscape is a different brief and benefits from the kit and the
   hygiene gate being settled.

Total: roughly eight sessions, plus the art track alongside.

## 5. The art track (parallel, not blocking)

The pipeline is `tools/png2shape.py` and `lv_god_statues.py`; shape 860 is
the worked example; the `agy` route in
`shared/docs/art-poc/gods/wake/README.md` is the generation record. Each
replacement lands whenever it is ready, without waiting for its map — the
cleanup builds each item's *setting* (dais, alcove, ring of columns) so the
swap is one constant. But the integration contract differs by what the
thing *is*, and each replacement gets its own written contract before the
art is made:

- **Static props** (cloud tiles, the Sacred Rock, the obelisk while MAGNET
  stays deferred): a shape injected as a numbered build step, TYPEFLAG
  footpad and flags, and — only if a compiled `foreach … type =` reads it —
  a `TYPE_SHAPES` re-point. Nothing else.
- **Interactive objects** (the elemental pillars and receptacles, a future
  wired obelisk, real plaques): the engine dispatches a shape's `look()`
  / `use()` / `gotHit()` from the class whose number equals the shape
  (`item.cpp:1516`, the mechanism the gods use). Re-pointing `TYPE_SHAPES`
  moves the *filter*, not the *handlers*: a new shape needs its class
  compiled at the new number, and class numbers are pinned in
  `lv_manifest.json` and frozen. So each of these is a manifest decision
  plus a compile, not a two-file edit. `TypeNSGoldPlaque` → 599 is the same
  shape of problem: the plaque class (1259) has no LV quality and is
  unplaced, so the map-side swap is decoration only until that text exists.
- **Actors** (the Tiny Tar Avatar, the water zombie, the harpie): sprite
  frames are not enough. `AnimationTracker::init`
  (`animation_tracker.cpp:63`) looks the actor's animation up *by shape*
  and refuses to move it when none exists, so a new actor shape needs
  animation data bound to that shape, and the usecode-driven statue
  animation of 860 is not that template. Until someone owns the anim-data
  binding, actors keep base-game shapes that already animate.

## 6. Decisions still open

- Whether the four Elemental Dungeon sections get *puzzle* content (the
  design doc's collapsing tunnels, platforming, lava maze, flooded rooms) or
  only dressing. The plan above dresses inside the boundary its Map 11
  section states; anything that can hurt or cut off the player is puzzle
  content, and puzzles are usecode work and a different queue.

## 7. Revision record

- 2026-09-15: the art track (§5) started — `docs/art-track.md` carries the
  queue and the per-item contracts, and the Magnetic Obelisk (shape 861)
  is the first static prop landed, through a table-driven build step
  (`lv_art_props.py`) so later props are a row each.

- 2026-09-15: six corrections from the Codex review of `d178ff9` applied
  (pin inventory derived rather than recalled; art track split by
  integration contract; the Map 11 dressing/gameplay boundary stated;
  hygiene test specified by coverage and clearance, not adjacency; the WARN
  ceiling and the F4 mismatch claims withdrawn; kit extraction generalised
  with a byte-identical acceptance). Each was checked against the file it
  cited before being taken.
- Whether Map 10's dry riverbed/paths are worth a custom path tile or use a
  retail one (the Plateau's).

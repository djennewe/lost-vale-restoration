# Maps 9 / 11 / 18 / 8 / 39 — macro layout v2 (FableDesigner, 2026-10-12)

For AstraInteriors. World units; tile = 128, chunk = 512. All pins exact x/y/z
(v1's +16 god raise was wrong — everything stays at pinned z).

## Shared rules (from the game-scale critique)
- **Floor:** 301 f0-6 is the sole base fill (glob 397 on full chunks, loose tiles on
  partial). Rough f7-37 and gravel 6 appear only as the tile itself, never overlay,
  never leaving holes. v1's black floor holes are an instant fail.
- **Walls:** full 26-32 family, run lengths 1-3 tiles (retail median), 29 posts on
  convex corners, black frames ONLY on back faces, 334/564 caps at z=96. No straight
  run longer than 4 tiles anywhere a camera can see.
- **Game-scale composition rule:** at any point on the quest spine, the 320×200 frame
  should contain (a) a wall or outcrop within ~3 tiles on at least one side, and
  (b) at least one feature (dressing cluster, dais, pool, lava glow). Caves are
  corridors-and-chambers, not halls.
- Worked stone = tomb kit (290/296/294/293/240/352/556/423/38/259/550), never the
  Tenebrae town kit.

## Map 9 — Galjeron's lair (screen10 is the target look)
Pins: trigger 200 (14336,12416); pad 201 (13696,14208) — needs rock face due north
(arrival_corridors, x≤13823); pad 202 (14336,16128); trigger 203 (14336,16760);
MONEGG trigger (14208,13952); troll egg (14720,13408); body (13824,14336), journal
613 (13888,14368), pack, sword.

Shape: one cave, three beats along the spine (N→S):
1. **Arrival fissure** (13400-14100, 13900-14500): narrow (384-512), rock face due
   north of pad 201; Galjeron's body + journal + pack in a bone-ringed alcove just
   east — the first frame after arrival should contain the body.
2. **Guardian chamber** (13800-15100, 12300-13700): the one large space (~1300 across)
   — centerpiece a stepped 240-arcade dais with 290/296 skeleton-relief panels and
   259 claw statues (screen10), centred ~(14400,12900); troll egg (14720,13408) and
   MONEGG trigger stay inside; blood 332/bones dense here (R≈0.2).
3. **South passage** (14100-14600, 14600-16900): winding 384-640 wide, two direction
   changes, down to pad 202/trigger 203.
66 + 152 replace every 796. Flood with ExactReach from pad 201: all pins, 0 leak.

## Map 11 — Elemental dungeon (screens 05/07)
Pins (never touch): talismans 596 (2047,5631,4) E / (17152,5120,0) F / (5631,18943,4)
W / (12799,18943,4) A; pillars 865 (7680/8704, 20480/21504) + receptacles 866 at
y+256; boulders 66 q299 (8576/8704, 22528); trigger 202 (9728,1152,1); pad 203
(9728,1792); pad 204 (8291,22639); trigger 205 (8960,23296,1); 17 monster eggs +
triggers; axe (9599,4479). Never add new 596/865/66-q299.

Per-wing identity (the four frames a player remembers):
| Wing | Composition | Materials |
|---|---|---|
| Earth (NW, talisman (2047,5631,4)) | three chambers linked by winding passages; talisman in a 259-claw alcove; rubble mounds 122/125, boulder chokes | 301/6/125, 66/152 |
| Fire (NE, talisman (17152,5120,0)) | noise-masked 409 lava bodies with crust edges; rock ridges (301+125 lips) on the exact old causeway lines (LAVA_MARGIN holds); mesas in the lava; talisman on a mesa reached by ridge | 409/122/299; glow props 453 |
| Water (SW, talisman (5631,18943,4)) | 347 pools + 128 shores + 72 spikes; talisman islet with 510 basin shrine nearby; decision C (lethal vs dry) is the user's — build lethal behind a WATER_MARGIN check, fall back dry | 347/128/72/510 |
| Air (SE, talisman (12799,18943,4)) | 469/472-edged islands + 193/186 isles over darkness; stepping-stone routes on the pinned walk lines | 469/472/193/186/527 |
- **Pillar chamber** (7400-9200, 20200-21900): screen07 staging — each 865 pillar gets
  its element's apron (Earth 125/6, Fire 122+two 453 posts+mound, Water 128 rim,
  Air 469 fringe); receptacles clear; gate_coverage/gate_reach geometry unchanged.
- **Hub + corridors:** tomb-kit rotunda at the junction; corridors wind (cave_mask)
  centred on the same doorway spans; 2-3 bends per 1500u so no corridor shows both
  ends in one frame.
- Entry hall (pad 203): tomb kit, 38 gargoyles flanking the inner door.

## Map 18 — Shrine of Kumash-Ghar (screen04 + screen17)
Pins: gods 860 (2304,7680)f2 / (3840,7680)f0 / (3072,6656)f1 all z=0; altar 550
(3072,8192,24); EggAOCeremony (3072,8320,24); skull 331 (n228); EggTempleEntry
(2864,6240); EggCrackHint (2864,6048)+(3072,4800); gate 114 q180 (3136,640); trigger
210 (3072,1408); pad 211 (3072,1792); golem trigger+egg; crack y=6143 x2817-2879
stays shape 15/47 (TEMPLENT/CRACKHNT/BREACH_PIECES).

Beats from entrance to sanctum (N→S):
1. **Forecourt** (2600-3600, 300-1300): rock court on 301; gargoyles 38 flanking gate
   114; 70-cobble approach strip (screen17). First view at pad 211: gate + gargoyles
   up-screen, cave mouth beyond.
2. **Outer hall** (2500-3700, 1900-4600): tomb kit (352/556 floor, 290/296, 293
   columns, 240 cornice, 423 fringe); golem encounter stays.
3. **Crack passage** (2700-3400, 4700-6200): narrowing rock fissure; the 15/47 masonry
   seal at y=6143 reads as the Titans' wall set IN cave rock — frame it with craggy
   outcrops both sides (clear of lane x2700-2880).
4. **Sanctum** (2100-4100, 6300-8500): cave shrine on 301; walls on the same lines,
   three 48 courses; gods at pinned xyz unified by one floor apron + plinth-slab
   rings at z=0 + offering/bone scatter inside the triangle; altar 550 pinned;
   Doloras plinth dressing ≤ x=3136. Camera rule: rock wall within ~3 tiles behind
   each god (screen04 top-right).

## Map 8 — Plateau (polish only, stays retail)
1. 71:0 → 71:9 (Map 8's own frame, build_map_08.py:466-469).
2. Delete the 301 z=1 slab in Mythran's dining room (:484-487).
3. Optional: delete the redundant invisible slab under trigger 200 (:428-431).
No other changes; LB apparition pins (2200,2208-2230,8) untouched.

## Map 39 — Tenebrae fringe (polish, no 1994 shot: stay retail-idiomatic)
1. Oak hedge: non-periodic y-wander (hash of x), max-y ≥ 20343 (test_map39_south_edge).
2. Bushes: clumps of 2-4 with mixed frames, not a cycling line.
3. Swap the 4 rock spires for 434 clumps on retail dirt-patch grass frames.
4. Replace the visible void band with lower retail forest + moat bank.
5. Fix stale docstring :43-44. LBSCENE pins (17150,19700-19850,48) untouched.

## Acceptance windows (scale 1, ×3)
- Map 9: (14400,12900) dais chamber vs x3/screen10; (13696,14208) arrival.
- Map 11: (8300,20900) pillar chamber vs x3/screen07; one window per wing centred on
  its talisman; corridor window showing a bend, not a straight hall.
- Map 18: (3072,7300) sanctum vs x3/screen04; (3136,800) forecourt vs x3/screen17.
- Every window: zero black floor holes, no straight wall run crossing the full frame.

# Fable review of the visual-quality plan (2026-11-01)

Reviewed: `docs/research/2026-11-01-visual-quality-plan.md` against
`CLAUDE.md`, `.claude/rules/map-geometry.md`, the tour data
(`~/projects/lv-art-review/tour/*/review.json`, 370 stops), a
dozen of its captures, `docs/research/2026-10-12-organic-maps.md`,
`docs/research/2026-10-16-screenshot-reconstruction.md`, `HANDOFF.md`, and
the builders and tools the plan names. Every number below was re-measured
on the built `shared/build/FIXED.DAT` (fc92ee5f) and the pristine
`STATIC/FIXED.DAT.bak` unless marked `[INFERENCE]`.

## Verdict: approve with changes

The scope matches Douglas's items 1-4, the order is right, phases 1-3 have
measurable gates, and the two tools are thin wrappers over code that already
exists (`item_sorter.overdrawn`, `Painter.built`). Three things in §0/§4 are
wrong enough to send a slice in the wrong direction (the 564:2 "filler"
diagnosis, the "retail lowers near walls" claim, and the Map 13 skull-ring
hypothesis), one budget risk is unmentioned (the object-ID cap), and the
acceptance numbers are guesses where they could be calibrated against retail.
None of this changes the phase structure.

## What I verified

| Claim in the plan | Result |
|---|---|
| 564:2 counts per map (§0 table), 35:10 counts, Map 8's 1,714 / 1,052 retail | Exact. Map 8 built = retail (28,244 vs 28,235 records; plate counts identical). Map 39 has 274 of ours, 0 retail. |
| 564:2 "draws as walkable black" | True by construction: TYPEFLAG 564 is `LAND|SOLID`, zd 0, a floor. But see required change 1. |
| Map 18 walls 120 tall, Map 9 hall walls 96 | `build_map_18.py:799-806` (three 40-courses, "120 beats the climb": tallest adjacent step 46 + jump 72 < 120); `build_map_09.py:274` (two 48-courses). |
| "That is how retail U8 treats near walls in its interiors" (§4.1) | **False.** Retail Tenebrae stacks 10/15 at z 0/48/96 (Map 3: 42/116/118 and 74/267/204 pieces; Map 39: 77/566/587; Map 5 likewise), i.e. three courses, ~136 tall. Retail caves (Map 8) stack 26/27/32 at z 0/48/104/160, four courses. Retail hides the Avatar behind near walls just as we do. |
| Map 13 skull ring 745 at (4159,4895,80) "not drawn: draw order or roof cut" | The offline sorter disagrees: `overdrawn()` on the ring = 0.0, and `Painter.built()` at the m13-26 camera (4175,4863,96) paints the ring and the Avatar at frame centre (`/tmp/m13-26-offline.png`, 0.4 s, 2,120 items). The in-engine capture shows neither and its scenery is offset ~(-50,-65) px from the offline frame. Something other than sort order is at work — most likely the Avatar's actual post-teleport position [INFERENCE]. |
| Painter cost (void_audit feasibility) | 0.4 s per 640x400 frame at 2,120 items in view. A whole-map camera grid is feasible offline; it is not a 7-minute-estate test. |
| 347:16 "draws near-black" | Confirmed: frame 16 is flat (0,0,24). 347 is not `SI_ANIMATED` in TYPEFLAG, so a frame swap sticks; frame 0 has ripples. |
| "FIXED reloads on map entry, so old saves pick up map changes" (§9) | Half true. The map the save was made on carries its instantiated items (`map-geometry.md` "Verify a map fix on a FRESH world"; the cp24 case). Other maps reload on switch (`build_map_18.py:79-82`). |
| Captures: m09-14, m13-26, m17-07, m18-16, m18-17, m10a-62, m10b-21, m08-09 | All real except m17-07, where the Message Scroll is mostly visible (the column clips one corner); a downgrade candidate for the Astra pass. m08-09 shows an LV-cut doorway opening onto retail black no retail player ever sees. |

## Required changes, ranked

### 1. §0 bullet 1 misdiagnoses the 564:2 plates; phase 3.1 must target the cause, not the cover

The plates are not filler laid where ground should be. They are
`lv_furnish.void_floor()`'s last-resort cover (`lv_furnish.py:171-194,
271-291`): a black plate under every 128-cell that nothing paints, within
view of a floor, so the engine does not show the previous frame there
(`Ultima8Engine::paint()` clears only with `usehighres`). Swapping the
frame or deleting the plates changes nothing a player sees for the better:
without them those pixels are stale frames, and with a textured frame the
black becomes a wrong texture over void. The cause is that every LV map is
zones standing in void with no backdrop and, at some edges, no curb.

Two consequences for phase 3:

- **Walkability is a curb problem, not a plate problem.** 564 is LAND, and
  the engine supports any unblocked position at z ≤ 0 anyway
  (`build_map_18.py:794-797`). Replacing a plate with 301 leaves the void
  exactly as walkable. Every skirt needs a visible rim or a 497/498 curb
  (`lv_landscape.rim(flush=...)`), and `exact_reach` leak = 0 is part of
  the phase 3 acceptance.
- **The metric must separate walkable black from black in frame.** "Void
  share per frame" (§5 acceptance) counts cave darkness beyond a wall —
  which is retail's own idiom (organic-maps §1.2) — the same as a black
  floor under the Avatar. Report two numbers: (a) *walkable black*: reachable
  cells (`exact_reach`) whose top paint is 564:2 / 35:10 / 334 / unpainted
  — tolerance zero on every map; (b) *frame black share*, with per-region
  thresholds (change 7).

Evidence: m09-14 (Avatar on 35:10 beside the hall wall), m08-09, m10b-21
(the plateau floats in black because nothing paints the ground below its
rim, not because a plate is there).

### 2. Phase 3 has no item budget, and the obvious fix blows it on Map 10

Raw FIXED records now: Map 10 20,559 (2,426 plates), Map 11 9,516 (2,792),
Map 13 6,447, Map 17 5,481, Map 9 1,019, Map 18 1,737, Map 39 5,108.
Object IDs run 256-32766 and every FIXED record takes one on load
(organic-maps §3). Replacing each 256-unit plate with four 128 tiles puts
Map 10 at 27,837 before phase 4 adds a single prop. Required:

- a per-map raw-record gate in `build_all_maps.py` (organic-maps suggested
  25k) that phase 3 and 4 slices must pass;
- skirts laid as glob eggs (one record per 512 chunk) or 256-unit plates.
  564 frame 0 is a textured 256 flagstone plate; a rock and a cloud recolour
  of it through the art track (`docs/art-track.md`, next ID 887) would skirt
  at today's record count. Decide this in phase 0, not per slice.

### 3. Phase 2's retail precedent is wrong; state the policy as ours and name the mechanism

Retail does not lower near walls (table above). The 50% rule is a stricter
standard than Pagan's, which is a legitimate choice but must be presented to
Douglas as one, and the threshold should come from measurement: run
`avatar_visibility.py` on a retail route (Tenebrae streets and a house
interior, the Map 8 corridor) first, and set the LV number against that.

The fix palette should name the documented lever instead of leaving it to
each slice: lower only the *drawn* courses and keep the anti-climb height
in retail's invisible wall 497/498 (`SI_EDITOR`, never drawn, still solid;
the `rim(flush=...)` pattern in `map-geometry.md`). The invisible box must
be coincident with the drawn course so the lowered top is not a standing
level.

Map 18's crack line is a special case the plan does not mention: the six
breach records (`BREACH_PIECES`, quality 307, at z 0/40/80 over x
2815/2943, `build_map_18.py:90-96`) are what `EggTempleEntry`/`EggCrackHint`
destroy, `TEMPLENT`/`CRACKHNT` key on shapes 15/47, and
`test_crack_geometry.py` checks both states. A 497/498 backstop cannot
cover the aperture or the breach never opens, so the full 120 stack must
stay over x 2688..2943 before the breach (it reads as a pier over the
crack) while the rest of the line drops to one course with the invisible
wall behind it. The capture m18-16 is the strongest case for doing this:
the player is invisible exactly where the crack has to be found.

Also check what a lowered wall reveals beyond it (the sanctum cave floor
is already in view at m18-16's lower left); run `void_audit` after phase 2
per map (change 8).

### 4. The Map 13 skull-ring hypothesis is contradicted offline; fix the capture tool first

Offline, nothing covers the ring and the painter draws it and the Avatar at
the m13-26 camera; in-engine neither shows and the scenery is offset. The
first check is not the Object channel on the sort — it is where the engine
put the Avatar after `teleport 13 4175 4863 96` (an unsupported spot falls
through `scanForValidPosition`) and where the camera actually was.
`tour_capture.py` records `ok: True` and the requested coordinates only.
Make it log the engine's actual Avatar and camera position per capture.
This is also a precondition for phase 0 step 3: "void_audit within 2
points of in-engine captures at 10 stops" is meaningless unless the
offline camera is the engine's camera.

### 5. Map 8 and Map 39: classify by who exposed the black, then decide

§0 bullet 2 ("every Map 8 item is a decision, not a default fix") is too
broad. The seam doorways are LV cuts (`BASE_ITEM_REMOVALS`, glob 936) and
they lead onto retail black plates behind a retail wall that no retail
player walked (m08-09, m08-12, m08-14, m08-49; the trigger-200 pocket).
Map 39's treeline void is seen only from the LV lane. Those are ours by the
same logic the plan applies to LV maps, and default to a fix (a skirt or a
floor; organic-maps §5 already proposed the Map 39 lower forest and moat
bank). Only black that a retail player sees on a retail route (the trench
m08-05, the spitter corridor m08-37/38, the doors chamber east third
m08-47) is Douglas's call under §6.1. The backlog's retail/LV field should
therefore be three-valued: retail-visible, retail-geometry-LV-exposed, LV.

### 6. §9's savegame claim is half wrong and affects verification

A save carries the instantiated items of the map it was made on; only
*other* maps reload FIXED on entry. Every verifier walk in phases 1-4 starts
a new game or arrives by map switch, never from a checkpoint on the map
under test (`map-geometry.md`, "Verify a map fix on a FRESH world").

### 7. Calibrate the thresholds against retail before adopting them

"No reachable frame over 10% black" will fail retail caves and pass a
black floor. Run `void_audit` on retail Map 3 (town), 5, 8 (cave), 22, and
on the Map 8 LV route as it stands, and publish those numbers as the
baseline. Then: walkable black = 0 everywhere; frame black share per region
class (exterior, cave, cloud) no worse than retail's same class; an
allow-list for true chasms and the accepted Map 13 north edge. Same for
phase 2's 50%: retail-derived (change 3).

### 8. Phase 2 before phase 3 is right, but the two must share an owner per map

Lowering a near wall uncovers whatever stands behind it — on an LV map,
void. Phase 2's acceptance should not count void, and the phase 3 baseline
for a map must be taken *after* its phase 2 slice lands. Simplest: one
builder owner carries both phases for a map, in sequence.

### 9. Assign the "repetition" category (63 items) or declare it out

The plan's four phases cover void, occlusion, dressing and stand-ins.
Ground repetition (glob 40 stripes, glob 65 checker, 91-98% 512-unit repeat
— organic-maps §1.1) is the tour's second-largest architecture/repetition
source and the first cause that research named. Phase 4's direction cannot
make a region "read as its place" on a wallpaper floor. Either put ground
variety in phase 4 with its own acceptance (distinct ground frames per
region, repeat share) or state in §7 that it is deferred, so the Astra
grading is not asked to pass something the phase never touched.

### 10. Tag shot-bound items with their window's floor score

Map 13's "black holes and black vertical slabs on the terraces"
(m13-23..27) are partly screen14's own pieces (`SHOT_CUTS`,
`build_map_13.py:139-155`: the 564:3 plate cut to two 35:10 tiles). A
phase 3 fix there is a `test_vignettes` regression. The backlog field
"touches a 1994 shot window" should carry the window name and its
`FLOORS` score, and such items need the vignette's own evidence before any
change.

## Answers to the review questions

**1. Items 1-4, order, acceptance.** Covered, in Douglas's order. Phase 1 and
2 acceptance is measurable; phase 3's needs the metric split (change 1) and
calibration (change 7); phase 4's is Astra-only — add the organic-maps
density numbers (props per 100 walkable tiles, clustering R, retail targets
3/7/10/17 by terrain) as a measured gate beside the grading. Phase 1's
Map 11 pad-room item is dressing class apart from the lamp in the doorway;
keep the lamp, move the rest to phase 4. Phase 1's Message Scroll item is a
downgrade candidate (m17-07).

**2. Root causes.** 564:2 as "the cause" is wrong (change 1); retail-vs-LV
is right for Map 8's geometry and wrong about who exposes it (change 5);
map-edge skirts are the right lever and need the budget (change 2); near-wall
heights are the right lever with the wrong precedent (change 3).

**3. Agent split.** Sound. Adjustments: Fable's per-slice design reviews are
a rate-limited bottleneck for little gain — batch Fable to the plan, the
phase 0 tools and backlog, the phase 4 direction, and the final report;
Codex review covers slice code. Astra's ~15 pairs per run cannot grade
every item of every phase; make the two tools the primary acceptance and
Astra the audit of a sample plus the disputed items, with the orchestrator
doing first-pass grading (it reviewed all 370 captures already). The Codex
tooling specs must point at `item_sorter.overdrawn`, `roof_z`,
`Painter.built`, `exact_reach` and `test_route_reach` legs by name, or the
tools get re-invented. Verifier stays in the main checkout (CLAUDE.md).

**4. Tools.** Feasible. `avatar_visibility.py` is a loop over cells calling
`overdrawn()`, which already makes the roof cut and skips SI_EDITOR; the
unmodelled case (no direct edge) is the cycle case. Cost: `overdrawn`
scans the whole item list per call, so bucket items by chunk and use a
128-unit lattice map-wide with 32 on the quest legs; one standing frame
per facing is enough. `void_audit.py`: 0.4 s per frame measured; whole-map
grids are an offline batch (Map 10 ~1,000 cameras at 512 spacing), and the
estate test samples tour stops and legs. Count unpainted (-1) and palette
index 0 both as black; calibrate against the engine's *actual* camera
(change 4). Thresholds: change 7.

**5. Risks and gaps.** Shot windows: change 10. Anti-climb: change 3.
Savegames: change 6. Paint cycles: covered; add `test_sanctum_clearance`
and `test_crack_geometry` to the Map 18 slice. Scope creep: change 9 is
the one category with no home. Retail fidelity: change 5. Lighting: U8 has
none to speak of; not a gap. Animation: animated props (campfire 267,
torches, the waterfall 439 with 435-438 foam) are the cheapest life a
region can get and belong in the direction's kit lists. Actor placement:
NPC and monster spots go through the same `overdrawn` gate
(`test_schedule_destinations` check 4 already) — name it in phase 2's
acceptance. The ghost follower and the Map 9 wraith are actors, not map
art; the Astra confirmation step catches them. One more: a full re-tour
should diff each capture against the previous tour's and send only changed
frames to grading.

**6. Phase 4 direction.** Below.

## Optional improvements

- Phase 0 backlog: record each stop's engine camera and Avatar position
  (change 4) so every later re-capture is comparable.
- Map 10 lake: 347 frame 0 or the 128/126 shore set from organic-maps §5;
  no new art needed.
- `tools/integrate.sh` after each phase merge is in §8; add the per-map
  record count to its report.
- Players run 320x200 without `usehighres`: the harness captures are the
  *best* case. Say so on the card page so Douglas grades against the right
  floor.
- Fold the organic-maps v3 generators (`2026-10-12-organic-maps/v3/`,
  Astra's Map 10 and Map 17 iterations) into phase 4's shared dressing
  module rather than starting from `build_map_13.build_dressing` alone;
  they already do hash-seeded clustered scatter.

## Phase 4 direction sketch

"Reads as its place" means a player dropped into one 320x200 frame can say
which region he is in from the ground, the walls and two props, and the
frame matches the nearest 1994 shot's materials. Per region:

| Region | Reads as | Anchor shots | Ground and edges | Kit |
|---|---|---|---|---|
| Map 10 highlands | Barren grey rock in tiers, scarps, a lava field at the cliff gate | 02, 09, 17, 18, 21 | 301 rock, 386 edges, 48/96 tiers with cliff faces; shores 128/126 | spires 66, mushroom scarp 625/466, skull-post pen, lava 409 with 122 crust |
| Map 10 villages | Brown-earth yards, huts, crops, a camp | 19, 20, 22 | 4 earth 60-75% of the frame, rock at the margins | huts 145-150/194/412, crop rows 649/650, fire 267, logs 666, urns |
| Map 10 lake | Dark water with a worked shore and a waterfall | 02, 09, 15 | 347 f0, 128/126 banks, 439 + 435-438 | zombies' eggs, bones, reeds |
| Map 13 | A cliff staircase of 301 ledges up to white cloud | 01, 14, 15, 16 | 56-unit ledges, cloud 874 at the summit edge, stepping stones over dark water at the base | bones, skull ring, spires; lanes kept clear |
| Map 17 | A white-and-gold city on cloud with no walls | 11, 12, 13 | cloud to every frame edge, gold streets 875, walkway 879, lobes 880/881 | columns 877, gem pillars 878, thrones 223, drums, shield halves |
| Map 18 | A rock court outside, a tomb-kit hall, a cave shrine | 04, 17 | cobble 70 approach, 301 cave floor, tomb kit 290/296/293/240 | gargoyles 38, altar 550, plinths, rubble at the crack |
| Map 11 | Four wings with one signature each, joined by a tomb-kit hub | 05, 07 | Earth: winding 301 chambers; Fire: 409 lava with crust, black beyond; Water: pools or a dry bed (Douglas's §6.2); Air: islands over void with 469/472 edges | boulders 193, roots, banded fire pillar, 453 posts, 72 spikes, 186/193 isles |
| Map 9 | A cave camp beside a tomb dais, a lair, then Zealan masonry | 10 | 301 floor, 26-32 walls with 334 caps | the dais kit, Galjeron's camp, troll-lair bones, 10/15 masonry only at the exit |
| Maps 8, 39 | Retail | none | retail; skirts only where LV exposes an edge | retail |

The direction document should contain, per region: the one-line read;
anchor shots and their windows (keep-outs); the ground materials by shape
and frame with the transition set; the prop kit with frames; density targets
(props per 100 walkable tiles and clustering R against retail's 3/7/10/17);
composition beats along the quest route (one feature per frame, an interior
wall within three tiles); the forbidden list (the stand-ins in §7.3, and
435-438 as ground); keep-outs (pins, routes, `FIRE_LINES`, shot windows);
and the acceptance: two or three named camera points per region rendered at
320x200 beside the anchor shot, plus the density numbers. Placement outweighs
art about 7:3 (organic-maps §8), so the document orders work placement
first and lists new art only where the kit has no retail piece.

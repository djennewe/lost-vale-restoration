# Phase B, Map 13 (Cloud Cliffs): screen01, 13, 14, 15, 16 — status 2026-10-17 (d)

## Pass (d): the 208 → 209 bounce (verifier finding 6) and screen13 (branch `wt/map13fix`)

Both items pass (c) left open (its Open 5 and 6) are done. No pin moved;
Map 17 is unchanged.

### Scores (built FIXED.DAT; `lv_map13_views.py`, `vignette_built_window.py --actors`)

| shot | replay | built | --actors / class94 |
|---|---:|---:|---:|
| screen01 | 94.09 | 91.94 | 94.98 |
| screen14 | 89.44 | 88.38 | 89.86 |
| screen15 | 95.93 | 94.53 | 95.98 |
| screen16 | 94.27 | 93.25 | 94.59 |
| **screen13** | **75.97** (was 74.13) | **75.92** | **75.97** |

The four placed shots are unchanged to the hundredth. The window fit was
re-run with screen13 in it. It came back byte-identical (114 cells): no
generated cell draws into screen13's window. screen13 has no recorded
actors (its Avatar is not reconstructed), so `--actors` equals the plain
class score. Its built window matches its own replay.
Evidence (this folder, regenerated): `screen13_built_window.png`,
`screen13_class_diff.png`, `screen13_context.png`, and the other shots'.

### The bounce (finding 6)

From pad 208 (5119,2303,120), a keyboard hold NE used to slide N up the
leg's east lane. At the turn's north row, the refused step's slides (NE,
then NW) turned it W along the summit leg, SW onto the plateau and S into
trigger 209. That took 3.5 s running, or 5.5-6.1 s walking.

**Fix:** `build_map_13.CLIMB_STUB`. The north leg's three lanes run one
row past the turn, (38-40, 10) at z 120, and stop, curbed round over the
cloud. A hold up the leg still has north to go at the turn, so it runs on
into the dead end and stops there. These cells are north of y 1663 and
east of x 4351, so they draw into no window.

Measured with `avatar_mover.hold`, the mover `test_route_reach` uses:
8 headings × 8 modes × moving/standing.

| pad | before, 8 s | after, 8 s | after, 16 s |
|---|---|---|---|
| Map 13 pad 208 | 5 triggers (all NE keyboard) | 0 (91 stop, 37 clear) | 0 (126 stop, 2 clear: down the climb into the valley) |
| Map 17 pad 209 | 0 | 0 (68 stop, 60 clear) | 0 (75 stop, 53 clear) |

`arrival_corridors` now holds the 13 ↔ 17 pair (`FULL_HOLD = (208, 209)`)
in all 8 headings, every mode, moving and standing, for 8 s. Its world is
8,000 units round the eggs on those maps (4,500 elsewhere). The other
gateways keep their route headings and the 4 s bound. Other fixes tried:

- **Pad 208 on screen13's island.** The placement block asked for the
  arrival to get the composition. Every pad tried on the island bounced:
  (6559,2079) with a keyboard run N at 4.7 s, (6431,2079) with a keyboard
  run W at 4.2 s, and (5759,1663) with keyboard runs W at 2.4-3.1 s. Each
  run went out of the island's west corner, W along the summit leg and
  onto the plateau. So the pad stays on the leg, and the composition lies
  three cells north-east of it.

### screen13, the city edge

- **Origin (3456,-384,120)**, written to `vignettes/screen13.json`
  `placement`. The earth diamond lies at z 120 east of the climb's turn,
  x 5247-6783, y 1151-2687. Its west corner (40,13) is the turn's east
  lane, and it is open to the turn along (40-41, 12-14); the climb curbs
  the rest of its side. It does not draw into screen01's window, and the
  climb draws into none of screen13's.
- **Art.** Cloud 2000 → 874 and gold brick 2004 → 876 (`ART_STANDIN`),
  each laid one unit below the shot's z (`STANDIN_DZ`, the phaseC z rule).
- **Duplicate cloud tiles.** Two cells held three frames each at one
  position: (2591,2367) f2/f1/f4 and (2975,2463) f0/f2/f3. Each now keeps
  the one frame that draws (f4, f3). The replay is unchanged by this.
- **The gold street corner.** It was not in the JSON before. It is now
  four 2004 tiles on the 31-mod-128 lattice, at the registry's exact hits
  (232,136), (232,168), (200,152) and their lattice neighbour. Their local
  positions are (3103,2335) f0, (3231,2335) f0, (3103,2463) f0 and
  (3231,2463) f1, at z 1. Each tile and frame was kept only if it raised
  the class score; together they add +1.85.
  - The replay was republished: class 74.125 → 75.972, strict 73.117 →
    74.964, unmatched 25.88 → 24.03.
  - `vignette_replay.py --check screen13` reports `identical`.
- **Ground past the frame.** `SHOT_FLOORS` gives screen13's halo and
  hidden cells retail earth (4 f30-33) instead of 301
  (`lv_map13_tiers.Cell.floor`). Rims keep the 125 crest.
- **Cloud.** A shot's cell counts as cloud only for 874 at the sea's
  plane (z ≤ 57) (`vignette_layer`). Without that, screen13's patches on
  the earth would have turned its halo into cloud sea and put `cloud_fill`
  tiles under them.
- **The cloud sea runs on east** to x 8191, north of y 4095 (`CX_EAST`,
  `CY_EAST`). Unpainted pixels in a 640 × 400 frame, measured with the
  field ending at x 6655 and then with it running east:
  - from the gold street (6623,2015): 15,285 → 0;
  - from the island's middle (5951,1919): 2,717 → 0;
  - from its east tip (6911,1663): 21,813 → 64.
  - Further south the field keeps its edge. A cloud tile east of the
    valley's east edge covered an Avatar standing against it 53%
    (`map13_rim_drawn`).
  - The valley's rim (on CX1's chunks) is untouched.
- **Item counts.** Map 13 has 6,412 raw items (5,792 before), well under
  the 25,000 bound.

### Tests (this build)

All 13 pass:

- test_map_hygiene (60/60)
- test_map_edges
- test_route_reach (158/158, with the 8-heading 8 s rows for 208 and 209)
- test_paint_cycles (41/41; section 6 now also frames the dead end and
  every cell of screen13's island)
- test_schedule_destinations (200)
- test_monster_eggs (420)
- test_map_roundtrip (14/14)
- test_climb_width (24/24)
- test_endgame_hatch_box (20)
- test_art_props
- test_crack_geometry (10)
- test_sanctum_clearance (22)
- test_map_pins_fresh (3/3; `map_pins.json` regenerated, FIXED prefix
  changed, no pin moved)

Test changes:

- **test_map_edges** `footprint()` failed first: screen13's island
  (reached to x 7039) lies east of every z-0 floor, and the footprint
  counted only z-0 floors.
  - It now also counts zero-height LAND floors at any z that are not
    roofs. Rim crests (125, one unit tall) are excluded.
  - Map 13's footprint becomes x 1536-8191. Map 10's grows one chunk west
    and north (a 301 at z 104 on its edge). Every other footprint is
    unchanged.

### Open

1. **None of this is checked in ScummVM:** the dead end, the island, the
   gold corner, the earth halo, the cloud running east.
2. **screen13 reconstruction gaps.** The Avatar is still not
   reconstructed (`actors: []`). The cloud rim lobes are still not
   recovered (about 6.8k px). The gold street is the four in-window
   tiles: in the world it is a 2 × 2 corner at the island's edge that
   leads nowhere.
3. **Black seen from the dead end.** Standing at (5119,1343,120), the
   map's north edge (y < 0) shows as black in the frame's top-right
   corner. Nothing can be laid at negative y.
4. **Pass (c)'s Open 7 stands:** 6,586 black climb-frame pixels.
   The island's frames were not added to that count.

---

# Status 2026-10-17 (c)

## Pass (c): the verifier's Map 13 findings 2, 3, 7 (branch `wt/map13fix`)

Findings 2 (cloud holes), 3 (cliff voids, tread seams) and 7 (paint
cycles) are fixed. Findings 6 (the pad 208 wall-follow into 209) and the
screen13 integration are **not done** in this pass (Open 5, 6 below).

### Scores (built FIXED.DAT; `lv_map13_views.py`, `vignette_built_window.py --actors`)

| shot | replay | built, before | **built, now** | --actors / class94, before | **--actors / class94, now** |
|---|---:|---:|---:|---:|---:|
| screen01 | 94.09 | 91.51 | **91.94** | 94.57 | **94.98** |
| screen14 | 89.44 | 88.26 | **88.38** | 89.74 | **89.86** |
| screen15 | 95.93 | 94.52 | **94.53** | 95.98 | **95.98** |
| screen16 | 94.27 | 93.24 | **93.25** | 94.58 | **94.59** |

Every window is at or above its previous score; none of the changes may
lower one (the window fit checks every piece it adds).

Black pixels a player sees (offline engine-order paint, union of 640x400
frames centred on every climb tile and summit cell, windows excluded):
20,637 before, **6,586** now. Paint cycles from those frames: 2 distinct
(the two logged) before, **0** now.

### What changed

1. **Cloud holes in screen01 (finding 2).** `lv_map13_tiers.cloud_fill`:
   under every shot cell that shows cloud, and every void/hidden cell
   below the plane beside cloud, one 874 tile, laid as the plane's
   lattice tile slid 4 steps down the view ray (-32, -32, -8). It draws
   exactly the plane's pixels and sorts under the shot's own tiles, so it
   shows only through the holes their 32-unit grid leaves. The 62-px 874
   frame also left sprite-level holes where lattice and off-lattice tiles
   meet; the slid filler covers those too (a plain z 48 filler did not:
   8 px low). screen01 +0.41 class.
2. **Tread seams (finding 3).** A rim cell that is also a riser takes the
   crest of all the sides it steps down on (`emit`: drops ∪ risers): the
   east lane's E crest drew no south side. And `courses_down` ends a lip
   stack whose last gap over z 0 is under 8 with a lip at z 0 (the lower
   leg's east lane showed a 4-unit seam over the valley floor).
3. **Cliff voids (finding 3).**
   - `exposed()`: a ROCK cell beside a shot cell, a void or the field's
     edge gets drawn frames on its north and west faces too (the camera
     sees behind it there), except a piece that could draw into a window,
     which keeps the black frame the shot shows.
   - `shot_faces()`: the shots' own cells get completion faces where the
     generated ground beside them is lower — a LOCK cell below its
     lowest shot piece in that strip, a HIDDEN cell under its floor — in
     the tier grammar, skipping any piece that would meet a shot item's box.
   - The window fit (`lv_map13_views.py --fit`) now also refuses those
     completion pieces per (cell, side) where they take window pixels
     (fit entries `["unfaced", side mask]`, `build_map_13.UNFACED`). It was
     re-run; 114 cells.
   - screen14's black plate 564:3 (z 137, 256 across) is laid as the two
     35:10 quarters that reach the window (`SHOT_CUTS`), at the offsets
     that draw its own pixels there; the rest drew a black diamond above
     the window.
4. **Paint cycles (finding 7).** Reproduced offline with `item_sorter.py`
   from the climb's cameras on the old build: `564:6@(4207,4199,104) ->
   566:0@(4255,4223,64) -> 26:8@(4160,4172,96)` (screen14) and
   `66:7@(4223,2623,104) -> 66:9@(4319,2495,112) -> 125:1@(4351,2559,112)`
   (screen01). Both are the shots' own pieces, solved inside their
   neighbours: a reconstruction fixes position only up to the view ray.
   - `RAY_SLIDES` (`vignette_layer(slides=)`): screen01's 66:9 slides k=4
     onto the crest top, 66:7 k=8 clear of the crest (steps of (8, 8, 2)
     draw identical pixels).
   - screen14's 564:6 and 26:8 draw no pixel of any window: dropped
     (`SHOT_CUTS` with no pieces).
   - `test_paint_cycles.py` section 6 frames Map 13 from every second
     climb tile and every summit cell and requires no cycle at all. On the
     old build the same frames find both knots (9 cameras, e.g.
     (5119,4607,84) and (5119,2559,120)); sections 1-5 framed only the old
     summit spots, which is why it passed.

### Tests (this build)

All pass: test_map_hygiene, map_edges, route_reach (158/158),
schedule_destinations, monster_eggs, map_roundtrip, climb_width,
endgame_hatch_box, art_props, crack_geometry, sanctum_clearance,
paint_cycles (41/41, new section 6), map_pins_fresh (map_pins.json
regenerated; FIXED 32e8330f…), png2shape. No art or usecode change.

### Open

5. **Finding 6 (bounce 208 → 209) is not fixed.** Pins unchanged; the
   `arrival_corridors` extension to 8 headings / 8 s is not made.
6. **screen13 is not integrated.** Its 13 × 13-cell earth diamond at z 120
   (window ground x ∈ ox+[1898,3194], y ∈ oy+[1618,2914]) does not fit the
   current summit. It fits east of the north leg over the cloud sea, with
   its west column on the leg's east lane: origin about (3456, -384, 120)
   puts it at x 5247-6783, y 1151-2687, level with the leg's z 120 run
   (y 1663-2687). That needs the field widened to x 6783 (CX1 52), earth
   (shape 4 f30-33) as a floor material, and pad 208 (and perhaps
   trigger 209, "the city edge") moved onto it — which is also the natural
   fix for finding 6. A z 120 floor at x ≥ 5248 cannot reach screen01's
   window (its east corner is (4760, 2104) at z 120). Its JSON has no gold
   brick (2004) items; the street corner is not reconstructed.
7. **Black left on the climb's frames** (6,586 px): the climb foot's
   z 4 tiles (no room for a crest), screen14/16's own black 393 pieces,
   and the shot sides the fit refuses (15 shot cells).

---

# Status 2026-10-17 (b)

**State:** the four shots are placed verbatim, and every Map 13 test but one
passes. The one failure is a design conflict with Map 17 and needs a
decision (see Open 1). Branch `wt/vignettes-map13`.

## Scores

Both measures come from `python3 agents/map-populator/src/lv_map13_views.py`
run on the built FIXED.DAT. Each number is a percentage of all frame pixels.

| shot | replay class | built (`vignette_built_window.py`) | class94 (built + actors + 1994 cloud) | class94 − replay |
|---|---:|---:|---:|---:|
| screen01 | 94.09 | 84.93 | **94.57** | +0.47 |
| screen14 | 89.44 | 88.26 | **89.74** | +0.30 |
| screen15 | 95.93 | 94.52 | **95.98** | +0.04 |
| screen16 | 94.27 | 93.24 | **94.58** | +0.31 |

- All four shots now reach or beat the replay on class94; the target was replay − 0.5.
- The `built` column paints no actors. It also uses the retail painter, which does not draw the stand-in cloud 862. That is why `built` is lower, and on screen01 much lower.

## Changes in this pass

### Tests made green

- **The climb's curbs** (`build_curbs`):
  - no curb at z 0 or toward the new **foot apron** (`foot_apron()`: the foot row is valley floor across the first lanes);
  - no curb where the climb steps onto a shot's ground at its own level (the summit and screen14's spur);
  - a neighbour only 8 up now gets a curb. Before, the lake's stepping stones beside the east leg could be stepped onto.
- **Valley rim:** `build_valley_rim(valley)` keeps only the rim pieces beside valley cells. The old y filter let the east edge leak.
- **Tiers:**
  - `lv_map13_tiers.emit` no longer puts a crest below z 0 (a z −4 crest wrapped to 252);
  - riser crests are chosen by role, not frame 14.
- **Harpies:**
  - summit eggs x 4223 → 4287 (32-unit edge clearance);
  - `HARPIE_REST` y 3071 → 3039 (it was 1 unit inside the lane pair's seek square).
- **Validator:** `map_validate` skips SI_FIXED|SI_LAND pieces. screen14's retail 735 slab was being reported as "supporting itself".

### The summit is now entered from the north-east

screen01 shows the ground south and east of the plateau lower: there are crest lips on (33,19) and (34,18). The old arrival tiles (34,19) and (33,20) at z 120 drew over the shot's bone pillar, costing 344 window pixels.

The new route:

1. The north leg continues over the cloud to y 1663.
2. It turns west and ends on (34,12).
3. Its south lane steps onto the plateau corner (34,13).

`CLIMB_WIDE` now covers y 1663–10111. `CLIMB_CUTS = {(31,60)}` drops the bend lane that drew 246 pixels into screen15. The climb no longer draws into any window except 19 pixels from (32,60), which is under the fit's threshold.

### Pin moves

All of these follow from the shots.

| item | was | now |
|---|---|---|
| pad 208 | (4351,2303,120) | **(5119,2303,120)**, on the north leg, east of trigger 209's box |
| trigger 209 | (4351,1919,120) | **(4351,2303,120)**, across the plateau's south |
| harpie trigger 2 | — | (4863,1663,120), across the summit leg |

Notes:

- The pad was first tried at (4351,1919). There, an arrival held south walked into 209, and the way back north crossed its box. Then at (4991,1663), where the pad-to-trigger walk ran south-west and carried a Map 17 arrival into Map 17's trigger 208.
- `map_pins.json` is regenerated.
- `tools/map_viewer/locations.json`: the Map 13 rows are rewritten.

### The window fit (`lv_map13_views.py --fit`)

The fit now works in two passes:

1. **LOWER** goes down to z 24 and then z 0 before giving up and making a cell void.
2. **FILL** raises every void cell to its highest standing neighbour's level (snapped to 8), then lowers it the same way. It can also refill a void beside cloud with cloud.

Supporting changes:

- "Good" pixels are the vignette's own matches, plus shot-black pixels the vignette leaves unpainted. This makes the fit deterministic and independent of the previous fit file.
- A lost pixel that nothing paints is charged to the cell at z 0 under it.
- The fit now holds 90 cells. Void cells: 33 before, 10 now.

### Dressing (`build_dressing`)

- **What:** 77 pieces. These are 66 spire clusters (frames weighted to retail), 152 stumps, 138 cracks, and a bone scatter (235/332/358/219) on ledges within 4 cells of the walk.
- **Density:** about 7.4 pieces per 100 dressable cells. Retail's 301-floored maps run 1–20 per 100 floor tiles, median about 8. Pieces cluster at 32-unit offsets, as retail's do: retail's nearest-spire median is 128.
- **Where:**
  - only on ground nobody walks;
  - plus the valley's cliff feet, kept off the arrival ground (`VALLEY_CLEAR`);
  - never where a piece's projected box comes within 16 px of a window (`window_rects`/`in_a_window`, computed from the vignette cameras).

## Tests (run on this build)

| test | result |
|---|---|
| test_map_edges | pass |
| test_monster_eggs | pass |
| test_map_roundtrip | pass |
| test_climb_width | pass |
| test_map_pins_fresh | pass |
| test_map_hygiene | pass |
| test_paint_cycles | pass |
| test_schedule_destinations | pass |
| test_endgame_hatch_box | pass |
| test_art_props | pass |
| test_crack_geometry | pass |
| test_sanctum_clearance | pass |
| test_route_reach | **153/154**: gateway 209 fails (Open 1) |

### Test changes, and why

- **test_route_reach:**
  - the gateway rows and the summit route points now use the moved pins;
  - `EGRESS (13,208)` stays 'S';
  - `APPROACH 209` changed 'N' → 'S'. The plateau is now crossed southward onto the trigger, so 'N' would misstate the route.
- **test_climb_width:**
  - `SUMMIT_Y1` is replaced by `build_map_13.summit_cells()`. The climb no longer ends at a y boundary;
  - screen14's ground through `CLIMB_SPURS` (`spur_ground()`) counts as on the climb. It is the climb's one designed side opening.
  - These follow the approved reroute; they are not loosened checks.

## Evidence (this folder)

- `screenNN_built_window.png`, `screenNN_class94_diff.png`, `screenNN_context.png`: regenerated.
- `map13_whole.png`: a whole-map preview, engine-order painter, at half scale.

## Open

1. **Gateway 209 against Map 17 (needs a decision).** Trigger 209's box is ±416 × ±32, so it can only be crossed north–south. From the north-east entry it is crossed heading south. An arrival on Map 17 still holding south reaches Map 17's trigger 208, which is 384 south of pad 209, in 0.44–0.9 s. Fix options:
   - move Map 17's trigger 208 off pad 209's south line (Map 17's own branch);
   - put trigger 209 on the summit leg, crossed heading west. Then the plateau becomes optional;
   - add a southern way onto the plateau that stays outside screen01's window. None found: every cell at 120 south of row 20 draws into it.
2. **Contexts still show some void.** Black patches remain beside screen14 and screen16, where even a floor at z 0 draws into a window. Thin riser stripes are also still visible on the north leg in screen14's context. Choosing riser crests by role removed one of them, but not all.
3. **The causeway is still jump-only** and curbed off the climb (1994 design). Whether the player can reach it is still a design decision.
4. **Not checked in ScummVM** (out of scope for this pass). The new summit leg over the cloud, the pad on the north leg, and the dressing all need a playtest.

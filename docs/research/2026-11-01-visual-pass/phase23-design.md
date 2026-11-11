# Phases 2 and 3: executable design (2026-11-02)

**Status:** design for review. Written by Fable after the phase 1 merge
(`94cc07d`, FIXED `89da4e16`). It carries change 8 of the plan review: one
owner per map runs phase 2 (the Avatar behind near walls) and then phase 3
(the void pass) in sequence, and the phase 3 baseline for a map is taken
after its phase 2 lands. Nothing here is built; numbers marked *current*
were measured on the merged build at 2026-11-02 (`/tmp/claude-1000/audits-p1`,
`void_audit.py`/`avatar_visibility.py` at `--step 128`, Map 8 with
`--arrival 29680 24400 56`).

Inputs: `2026-11-01-visual-quality-plan.md` §4, §5, §11;
`fable-plan-review.md`; `backlog.json` (phase 2: 16 items, phase 3: 32);
`astra-high-items.json`; `retail-calibration.md`; `audit-tools.md`; the
phase 1 reports and Astra's phase 1 grades
(`~/projects/lv-art-review/vq1/*/REPORT.md`, `phase1.html`);
the builders and tests named per slice.

Each slice section (§4) is written to stand alone as a Codex spec. §1 and
§2 are the shared rules and techniques every slice cites; read them once.

## 0. Where the build stands after phase 1

| Map | Class | Reached cells | Walkable black (specified / prop pixel) | Frame black mean / p95 / max | Cells <50% visible / hidden (of sampled) | Raw records / expanded |
|---|---|---:|---:|---:|---:|---:|
| 8 (LV shelf component) | cave | 15,758 | 256 inherited pocket / 0 | 34.6 / 61.3 / 78.8 | 14.7% / 7.1% (931) | 5,689 / 29,009 |
| 9 | cave | 5,908 | 0 / 19 | 26.1 / 53.4 / 64.3 | 26.6% / 10.1% (335) | 1,019 / 1,349 |
| 10 | exterior | 398,699 | 31 unpainted / 42 | 2.1 / 16.4 / 51.2 | 4.7% / 2.2% (24,192) | 20,571 / 37,566 |
| 11 | cave | 140,466 | 6 / 165 | 8.3 / 36.0 / 56.5 | 12.1% / 5.2% (8,534) | 9,515 / 17,825 |
| 13 | exterior | 20,686 | 0 / 5 | 9.9 / 39.3 / 59.2 | 3.8% / 1.2% (1,144) | 6,447 / 7,692 |
| 17 | cloud | 62,424 | 16 / 19 | 8.8 / 41.5 / 72.6 | 1.2% / 0.1% (3,728) | 6,665 / 6,665 |
| 18 | cave | 11,839 | 0 / 0 | 18.0 / 45.3 / 64.7 | 13.6% / 6.5% (707) | 1,750 / 2,530 |
| 39 | town | 177,351 | 0 / 14 | 7.0 / 39.1 / 75.8 | 12.7% / 6.1% (10,430) | 5,108 / 29,068 |

"Specified" walkable black is a floor probe owned by 564:2, 35:10, 334 or
nothing painted; "prop pixel" is a probe that landed on a prop's own black
pixel (bones 235/237, the Map 11 lava pools 318, Map 39's 162/727). The
retail comparators are in `retail-calibration.md` §Retail distributions.

Where the specified cells are (the phase 3 hit list):
- Map 10, 31 unpainted: x 9023..9631 / y 21151..21535 at z 0, 8 and 64
  (the garden mesa and stair, screen18/21), and x 19359..20511 /
  y 7487..8799 at z 0 (Gunnar's yard and Hrodny's chest, screen19/20/22).
- Map 11, 6: four at z 8 in x 6144..6815 / y 20480..21183 (screen07,
  VQ-043) and two at z 8 near (2623, 14975) (screen05, VQ-045).
- Map 17, 16 plates of 564:2 in one row: x 2463..2943, y 2975 (the walkway
  court south of screen12).
- Map 8, 256: the pristine trigger-pocket plates, allow-listed (§1.3 rule A).

## 1. Acceptance rules

### 1.1 The three instruments

1. **Walkable black** — `void_audit.py`, every reached 32-unit cell
   (`walkable_black_step=32` regardless of `--step`), the floor probe at the
   Avatar's bottom centre with foreground walls and roofs excluded
   (`void_audit.py:238-290`). Field `reason` ∈ {`specified_black_floor`,
   `unpainted_floor`, `black_floor_pixel`, `drawn_floor`}.
2. **Frame black share** — the same tool's `frame_black_share` per sampled
   camera (unpainted or palette-0 pixels over the 640x400 frame), summarised
   as mean / p95 / max over reachable cameras.
3. **Avatar visibility** — `avatar_visibility.py`, minimum over 72 walk and
   stand poses of the visible fraction after sorting with the roof cut
   (`visibility()`, `:67`). The Map 18 sanctum legs use `Poses(shape=867)`
   (Tiny Tar, 32x32x32), as `test_tiny_sanctum_visibility.py` does.

Both tools take the same flood as `test_monster_eggs.dry_flood` with
`ARRIVAL` (`test_monster_eggs.py:145`); Map 8 uses `--arrival 29680 24400 56`
(the shelf component) and Map 39 its first teleport target (19116, 3316, 48).

### 1.2 Quest legs

`test_route_reach.py` has no leg polylines: its `route()` calls are a flood
from one seed plus targets tested with `reached_near(..., ring=96)`
(`:72-98`, `:100`), and the module executes on import. Legs are therefore
defined in a new module, **`agents/map-populator/src/quest_legs.py`**
(gate 0, §3):

- `LEGS = {map: [(label, (x, y, z), (x, y, z), body, shape), ...]}` — the
  seed-to-target chain of each `route()` call, consecutive targets in the
  order the call lists them, seeds first. The tables, copied from
  `test_route_reach.py:1150-1507` and the vq1 engine walks:

  | Map | Legs (start → end) |
  |---|---|
  | 8 | shelf: (29680,24400,56) → first seam (29808,24383,56) → second seam (30400,26768,56) → (30400,30712,56); door chamber: pad 200 (20111,3175,8) → trigger 201 (20415,2783,1) |
  | 9 | (13696,14208,0) → trigger 203 (14336,16760,0); → trigger 200 (13759,12031,0); → dais top (14360,12792,56) |
  | 10 | (12800,2560,0) → Ezrekal (12800,12544,0) → Hoskuld slab (5120,7168,0) → Gunnar well (18688,7680,0) → Hrodny's chest (21104,8768,0) → Sacred Circle (20480,16896,0) → lake causeway (13824,19456,8) → Ragnar's cache (16447,25727,56) → Passage Test plant (12800,29300,64) → 207 (7168,24064,8) → 211 (18432,23552,0) → 213 (12800,1792,0); Ezrekal's house (12640,12704,0) → (12580,13124,0) → (12895,13439,0) → (14207,12543,0) |
  | 11 | (9728,1792,0) → Earth (2047,5631,4) → Air (17152,5120,0) → Fire (5631,18943,4) → Water (12799,18943,4) → chamber (8192,20992,0) → exit (8960,23296,0) (last leg with quality-299 boulders dropped) |
  | 13 | (4096,11776,0) → summit (4351,1919,120) → 209 (4351,2303,120) |
  | 17 | (4608,9984,0) → half 1 (4259,7199,0) → half 2 (3559,3311,0) → scroll court (3328,1536,0) → walkway top (2303,3103,8) → east court (6271,5823,0) → 208 (4608,11008,0) |
  | 18 | full size: (3072,1792,0) → 210 (3072,1408,0); → crack approach (2848,6080,0) [INFERENCE: the hall cell in front of the slit x 2817..2879]; tiny (shape 867, `TINY_BODY`): (2864,6504,0) → altar (3256,8152,0) → skull (2496,8512,0) |
  | 39 | arrival (19116,3316,48) → CITY (18562,14406,48) → lane egg (17150,19700,48) through the tunnel x 16096..16223 |

  The gate 0 owner may reorder Map 10's chain from the replay leg docs
  (`docs/playtest-2026-10-1{1,7}-replay-leg*.md`); the set of endpoints is
  fixed.
- `leg_cells(map, items, shapes) -> {label: set((x, y, z))}`: the shortest
  path on the 32-lattice between endpoints over the dry flood, found by a
  BFS that reuses `ExactReach.flood`'s neighbour rule (add
  `ExactReach.shortest_path(reach, a, b)` beside `flood`, same step and
  riser rules, endpoints matched with `reached_near` ring 96), dilated by
  one cell on each side (a 3-cell band). Deterministic: ties broken by
  (x, y, z).
- The legs are the only "quest route" the visibility rule knows. Scripted
  interaction points keep their existing gate: `test_schedule_destinations`
  check 4 and `deliberate_use` (`OVERDRAWN_MAX = 0.10`).

### 1.3 The rules, with numbers

**A. Walkable black.** Every reached cell with `reason` in
{`specified_black_floor`, `unpainted_floor`} is a failure, except cells
listed in that map's `inherited_black` (an exact coordinate list). Only
Map 8 has one: the 256 pristine pocket cells (`void-map08-walkable.json`,
all 564:2, the trigger-200 pocket and the first-seam pocket the vq1 report
describes as "the preserved retail pocket"). An LV cut that exposes more
retail black gets no allowance (`retail-calibration.md` §Proposed
acceptance). `black_floor_pixel` cells (props) are counted and ratcheted,
not failed. Target per map: 0 outside the allow-list, i.e. Map 10 −31,
Map 11 −6, Map 17 −16.

**B. Avatar visibility on quest legs.** On every cell of every leg band,
`min_visible >= 0.50` over 72 poses, except cells inside that map's
`occlusion_allow` boxes (world rectangles with a one-line reason, each
needing Douglas's sign-off in the slice's card page). Retail does not meet
this — 20.66% of Tenebrae's cells and 57.79% of the Map 8 cave's fail 50%
in the worst pose (`retail-calibration.md`) — so this is our standard, as
plan §11.3 states, and it applies to the leg bands only. The one known
allow box is Map 18's crack pier (§4.1).

**C. Avatar visibility elsewhere.** Per map, over all reachable cells
sampled at step 128: share of cells with a pose below 50% and share with a
completely hidden pose must not exceed the class limit and must not rise
above the map's pin (ratchet):

| Class | Cells below 50% | Cells completely hidden | Median of worst pose |
|---|---:|---:|---:|
| town / exterior / cloud (Maps 10, 13, 17, 39) | ≤ 21% | ≤ 6% | ≥ 100% |
| cave (Maps 8, 9, 11, 18) | ≤ 58% | ≤ 37% | ≥ 25% |

Current values are in §0; every map passes its class except Map 39 (6.1%
hidden against 6%, the lane tunnel VQ-021), so this rule mostly exists to
stop phase 3 skirts and crests from adding occluders.

**D. Frame black share by region class**, over reachable cameras at step
128, cameras inside the map's `frame_allow` boxes excluded:

| Class | Mean | P95 | Max | Retail source |
|---|---:|---:|---:|---|
| town / exterior (Maps 10, 13, 39) | ≤ 7% | ≤ 38% | ≤ 62% | Maps 3 and 5 |
| cloud (Map 17) | ≤ 7% | ≤ 38% | ≤ 62% | no retail analogue; the cloud sea has no legitimate black, so the town numbers apply, and the phase 3 design target is max ≤ 20% |
| cave (Maps 8, 9, 11, 18) | ≤ 47% | ≤ 77% | ≤ 91% | Map 8 south-east cave |

The only `frame_allow` box proposed is Map 13's accepted north edge
(VQ-054: stops m13-33/34/35/38, the summit strip north of screen01;
Douglas, 2026-10-25). Everything else that fails is work. Current
failures: Map 13 (mean 9.9, p95 39.3 — VQ-039 and VQ-054), Map 17 (8.8 /
41.5 / 72.6 — VQ-047), Map 39 (7.0 / 39.1 / 75.8 — VQ-040).

**E. Record budgets** (raw FIXED records; the object-ID cap is 32,500 and
every FIXED record takes one on load):

| Map | Now | Hard cap (gate in `build_all_maps`) | Phase 2+3 exit ceiling (leaves room for phase 4) |
|---|---:|---:|---:|
| 8 | 5,689 (expanded 29,009) | 7,000 raw; whole-map expansion ≤ 31,000 | 6,500 |
| 9 | 1,019 | 2,500 | 1,800 |
| 10 | 20,571 | 25,000 | 23,000 |
| 11 | 9,515 | 12,000 | 11,700 (D5) |
| 13 | 6,447 | 9,000 | 8,000 |
| 17 | 6,665 | 12,000 | 10,500 |
| 18 | 1,750 | 3,000 | 2,400 |
| 39 | 5,108 (expanded 29,068) | 6,500 raw; expansion ≤ 31,000 | 6,000 |

Skirts are glob eggs (one record per 512 chunk) or 256-unit plates; never
128-unit tiles over an area larger than a few chunks (§2.3).

**F. Shot windows.** Every `test_vignettes.FLOORS` score holds (floor −
0.25 slack, unpainted allowance). A slice that touches a window's cells
reports the window's before/after score in its report; the shot-bound
items carry their `shot_floor` in `backlog.json`.

**G. Geometry.** `test_route_reach`, `test_map_edges` (no new fall ≥ 104,
no leak past the footprint), `test_paint_cycles`, `test_map_hygiene`
(`void_in_view` 0), `test_map_pins_fresh` (pins frozen), plus the per-map
tests named in each slice. Every lowered wall is proved by `exact_reach`:
the flood from the map's seeds reaches exactly the cells it reached before
(set equality on the 32-lattice, per level), and `walk_off` reports no new
falls.

### 1.4 The permanent test and its ratchet

**`agents/map-populator/src/test_visual_quality.py`** (gate 0). Per map in
(8, 9, 10, 11, 13, 17, 18, 39):

1. `Scene(map)` + `reachable()`; walkable black at the full 32-lattice;
   frame cameras at step 256 (the distribution rule D is checked at 256 in
   the estate and at 128 in slice reports — both are recorded in the pin
   file); leg bands at step 32 through `quest_legs.leg_cells`; visibility
   over leg bands at 32 and over the map at 256.
2. Pins live in **one JSON per map**,
   `agents/map-populator/src/visual_pins/mapNN.json`, so parallel slices
   never edit the same file:
   ```json
   {"class": "cave",
    "inherited_black": [[x, y, z], ...],
    "occlusion_allow": [{"box": [x0, y0, x1, y1], "z": [z0, z1], "reason": "..."}],
    "frame_allow": [{"box": [...], "reason": "..."}],
    "pins": {"walkable_black_specified": 0, "walkable_black_prop": 19,
             "leg_cells_below_half": 0,
             "cells_below_half_share": 0.266, "cells_hidden_share": 0.101,
             "frame_black_mean": 0.261, "frame_black_p95": 0.534, "frame_black_max": 0.643,
             "records": 1019}}
   ```
3. Checks, in `test_map_hygiene.py`'s shape (`:322-335`): each measured
   value ≤ its pin (rule A's specified count is `== 0` outside
   `inherited_black`, not a pin); class limits of C and D are a second
   ceiling; rule B is `leg_cells_below_half == 0` outside `occlusion_allow`;
   rule E is `records <= cap`. When a value falls below its pin the test
   prints "lower these pins", as hygiene does, and the slice lowers them in
   its commit. Pins only go down.
4. Runtime target: ≤ 3 minutes for the eight maps (the step-128 audits
   above took 322 s for void and 21 s for visibility; floors dominate Map
   10). If the first run exceeds it, frames move to step 512; the walkable
   and leg checks stay at 32.

`build_all_maps.py` gains `RECORD_BUDGET = {map: cap}` checked in
`validate_and_gate` as an ERROR (the `KNOWN_FLOATING_LV_TELEPORTS` pattern,
`:74`, `:249-301`), so an over-budget map never writes.

### 1.5 Slice evidence protocol

Before any change and after each phase, from the slice worktree:

```bash
python3 -B agents/map-populator/src/void_audit.py MAP --step 128 --workers 4 --out EVID/<state>-audit
python3 -B agents/map-populator/src/avatar_visibility.py MAP --step 128 --workers 4 --out EVID/<state>-audit
python3 -B agents/map-populator/src/test_visual_quality.py MAP
```

plus `tour_capture.py` at every stop the slice's items cite (fresh world
per stop, `landed: true` required, `usehighres=false` as phase 1's Map 8
fix-up did), `tools/build_artifacts.sh --record`, `derive_map_pins.py`,
`tools/run_all_tests.sh` (53/54 with the worktree `test_integration_state`
exception), `codex exec review --base main`. The report follows the phase 1
`REPORT.md` shape: per item cause → change → stop table (walkable black,
frame black, min visible, before → after) → windows → records → hashes.
Astra grades a sample of stops after the merge (orchestrator).

## 2. Techniques (the shared palette)

### 2.1 T1 — lowered drawn courses behind a coincident 497/498 backstop

For a south- or east-facing near wall that must stay a barrier: keep the
ground course drawn (one course: 40 for the tomb kit 10/15, 48 for the
cave pair 26/32) and replace every drawn course above it with retail's
invisible wall — `SHAPE_BLOCKER_X = 497` (4x1x6, 128x32x48) on an x-run,
`SHAPE_BLOCKER_Y = 498` (1x4x6) on a y-run, `SI_EDITOR`: never drawn,
still solid (`lv_shapes.py:246-252`). The invisible pieces sit at the same
max-corner x/y as the drawn piece they replace, so the lowered top is not
a standing level (the 497 box at z 40 covers [40, 88) and overlaps the
Avatar's body box), and stacked at 48-unit steps until the old top is
reached or exceeded: a 120 stack becomes drawn 15 at z 0 plus 497 at z 40
and z 88 (top 136); a 96 cave wall becomes drawn 26 at z 0 plus 497 at
z 48 (top 96 — the height `lv_landscape._barrier_tops` uses: "96 above
the ground, more than the jump's climb72 reaches"; a lone drawn 48 course
with nothing above it is climbable). Emit with
`lv_landscape.cliff_run_x(items, x0, x1, y, top, frames=(0,), zs=[...],
shape=SHAPE_BLOCKER_X)` (`:83-92`) or the `_y` twin; the tomb-kit halls use
`u8_map.wall_run_x/_y` for the drawn course exactly as today.

Arithmetic the slice must measure, not assume: a drawn face h above the
ground covers the bottom h pixels of anything within 8h units of it in
x+y (`lv_landscape.py:131-141`). A 40 course therefore still hides more
than half of an adjacent standing Avatar (the sprite is about 60 px);
rule B is met one body-width (64) or more from the wall, so the band of
leg cells within one cell of a lowered wall must be measured and either
passes or goes into `occlusion_allow` with the reason "one-course wall
adjacency".

Proof per wall: `exact_reach` set equality (rule G), `gate_coverage`
where it exists (`test_route_reach.py:1079-1137`), and a visibility
sample at every leg cell within 512 units of the wall.

### 2.2 T2 — recessed walkable edge (pull the edge in; keep the face)

Where the drawn face must stay (a canyon wall, a pit, a tier that reads as
such), the barrier moves inward instead: one 128 strip of 497/498 at the
ground level, one cell inside the drawn face, so no reachable cell lies in
the covered band. This loses ground; use it only where T1 would destroy a
feature (Map 10's temple pit and relief tiers). The flood must lose
exactly the recessed strip and nothing else (rule G with the expected
delta listed).

### 2.3 T3 — edge skirts

A skirt is painted ground beyond the walkable area that the camera can
reach (1,280 units past a wall on x−y, 1,600 on x+y at 640x400;
`lv_furnish.VIEW_RX/VIEW_RY`) and the player cannot. Materials and
records:

| Material | Shape | Record cost | Walkable? | Use |
|---|---|---|---|---|
| retail rock floor glob 397 (16x 301) | glob egg | 1 per 512 chunk | yes — needs a curb | exterior rock plains at a rim's z (Map 10, Map 13) |
| lake glob 55 (16x 347 `SI_SEA`) | glob egg | 1 per chunk | enterable, drowns — needs a curb | water beyond a flush edge (Maps 10, 13) |
| cloud tile 874 | 128 tile | 1 per 128 cell | yes if reached; the layout's curbs keep the sea unreachable | Map 17 (phase 1 laid 1,077 this way) |
| cave backdrop plates 894 (334 frames) / 895 (564 frames) | 128 / 256 plate, donor 202: FIXED+DRAW, no LAND/SOLID | 1 per cell / block | no | cave darkness underpaint (Map 8, Map 11 if D5 says so) |

A LAND skirt is a seed for `void_floor` (`lv_furnish.void_cells`, seed =
every non-plate LAND flat), so the black plate ring moves outward by the
skirt's depth; a skirt deeper than `VIEW_RY` (four chunks) puts the ring
where no reachable camera sees it. The count stays roughly today's ring
(Map 10: 2,426 plates) and is recorded per slice. Backdrop plates are not
LAND and so today are neither seed nor cover; gate 0 adds them to the
cover set (`BACKDROP_SHAPES`) so `void_floor`/`void_cover` stop
double-plating under them.

Every skirt edge that is not a drawn cliff carries a curb: 497/498 at
base and base+48 (`_barrier_tops`), as `lv_landscape.rim(flush=...)`
lays on flush edges (`:131-141`) and `lv_map10_ground.flush_edges`
(`:191-225`) lays on Map 10's plateau. `test_map_edges` must still see no
leak and no new falls; a LAND skirt extends the footprint it measures.

Skirt z: beyond a drawn rim with a crest, the rim's crest z (the skirt is
the highland the rim is cut into); beyond a flush edge, the ground's own
z — and since nothing can sit below z 0, a flush edge on z-0 ground can
only be skirted by a material that reads as lower by convention: water
(D3, D4).

### 2.4 T4 — holes and slits

- **Corner slivers at per-cell faces** (Map 10 `lv_vale_terrain.Field._faces`
  `:459-512`, Map 13 `lv_map13_tiers.face_items` `:193-252`): each corner
  square belongs to one face and the other pieces are shortened (no two
  solid boxes may overlap — that is what closes paint cycles). Where the
  owning neighbour piece is absent (a jog, a dropped N/W face, a shot
  seam), the square shows black. Fix: emit a `POST = 29` (32x32) at every
  corner square no face claims, decided from the same neighbour table
  that shortens the pieces; posts are solid and overlap nothing.
- **Black "dark" frames** (26/32 f7-8, 27/28/31/30 f3; `lv_vale_terrain`
  `DARK`, `lv_map13_tiers` N/W unexposed frames): a face whose black frame
  is seen through a gap is a black slab. Use textured frames on every N/W
  face that any reachable camera can see (`exposed()` widened to "any
  8-neighbour is not rock"), or drop the DARK set entirely and measure.
- **Missing tops**: a tier or rock cell with no floor paints its top with
  the void plate (`lv_cave_vignette.py:28-30` "Rock has no floor: the
  map's void plates paint its top black"). Give rock cells a 301 top at
  the rock's crest z, outside shot windows, or a 125 crest (`CREST_FRAMES`).
- **Under-floors** under stairs and step blocks (the VQ-009/010 fix:
  `field.floor_item(c, 0)` under stair cells) so `void_floor` lays no plate
  across adjacent earth.

### 2.5 T5 — cloud-sea edges

Map 17's sea is 874 tiles at z 0 behind the layout's curbs
(`build_map_17.cloud_sea`, `:290-293`; `CLOUD_SEA_AREAS`). Extend
`CLOUD_SEA_AREAS` until no reachable camera sees past the sea: every
walkable boundary cell dilated by `VIEW_RX/VIEW_RY` (the
`cells_within_view` dilation, `lv_furnish.py:235-255`), clipped to x, y ≥
128. Record cost at 128 units is about 4,000 tiles (perimeter ≈ 36,000
units / 128 × 14 cells); it fits the cap. A 256-unit cloud plate through
the art track (874's texture on 564's footprint, donor 202 physics) would
quarter that; it is optional (D8), not required.

### 2.6 T6 — water

Map 10's lake is `WATER, WATER_DEEP = 347, 16` per water cell and glob 55
per whole-water chunk (`lv_vale_terrain.py:385-389, 412-415`); Map 13's
lake is 347:16 from the screen15/16 vignettes and their halo
(`lv_map13_tiers` `WATER_FRAME = 16`, "the plain navy the lake shots are
made of"). 347 is not `SI_ANIMATED`, so a frame choice sticks; frame 0 has
ripples. Both lakes are shot-bound (screen02/09; screen15/16), and the
1994 shots are navy, so the default is to keep 16 and fix what reads as
stripes: the "repeated blue edge sprites in the body" (VQ-041) are shore
pieces emitted for cells with a dry side (`SHORE_Z = 8` crest logic,
`lv_map10_ground.py:417-428`); identify their owners with
`Scene.paint(spot, avatar=True)` ownership at m10b-11/12 and remove or
re-frame the interior ones. Shores: the 128/126 bank set from
organic-maps §5 on the lake's outer perimeter only, outside windows.
Frame 0 outside windows is D7.

### 2.7 T7 — backdrop underpaint (the Map 8 pattern)

A drawn surface that hides the route (a 334/564 ceiling) becomes an
invisible solid of the same footprint (`499` for 564, `763` for 334, same
z: support preserved, `build_map_08.py:278-282`) plus a backdrop clone of
its art at `(x − 4z, y − 4z, 0)` (same screen projection, sorts under the
Avatar; `shelf_backdrop`, `:390-397`). Shapes 894/895 exist for the 334
and 564 frame sets. The test `test_map08_backdrop.py` checks every
replaced surface is under-painted. Beware VQ-003: a backdrop placed for a
ceiling paints into any opening the camera sees that ceiling through
(§4.8).

## 3. Gate 0: the shared-contract slice (one Codex agent, merged first)

Owns: `lv_furnish.py`, `lv_cave_vignette.py` (API only), `exact_reach.py`
(one method), `build_all_maps.py` (the gate), new `quest_legs.py`,
`test_visual_quality.py`, `visual_pins/map{08,09,10,11,13,17,18,39}.json`.
No builder changes; the built FIXED must be byte-identical before and after
(`tools/build_artifacts.sh --verify` passes against today's hashes).

1. `lv_furnish.floor_cells(..., painted=True)` also counts
   `BACKDROP_SHAPES = {SHAPE_CAVE_BACKDROP_SMALL, SHAPE_CAVE_BACKDROP_LARGE}`
   (894, 895) as painted cover; the seed is unchanged. `void_floor`,
   `void_cover` and `test_map_hygiene.void_in_view` all go through
   `void_cells`, so they agree by construction. Map 8 is the only map with
   backdrops today and it does not call `void_floor`, so no plate count
   changes; assert that.
2. `lv_cave_vignette.Cave.__init__(..., near_courses=2)`: `_face`'s S/E
   branch draws `near_courses` textured courses from z 0 and lays 497/498
   (`BLOCK_X/BLOCK_Y`, `:74-78`) for the rest of the two-course height,
   coincident. Default 2 reproduces today's bytes for Maps 9, 11, 18.
3. `ExactReach.shortest_path(reach, a, b)` (§1.2) and `quest_legs.py`.
4. `RECORD_BUDGET` in `build_all_maps.validate_and_gate` (§1.3 E).
5. `test_visual_quality.py` and the eight pin files, pinned to the
   measured values of the current build (the tool must reproduce §0 at
   step 128 within rounding; the pins are written at the step the test
   uses). Map 8's `inherited_black` is the 256-cell list; Map 13's
   `frame_allow` north box is left empty until D-list item 4 is answered,
   so Map 13 starts with its ratchet only.
6. Report: runtime per map, the pin files, and the leg bands rendered as
   one PNG per map over the visibility heatmap (so Douglas can see what
   "quest leg" means).

Gate to open the slices: estate passes with the new test at ≤ 3 min, FIXED
unchanged, `codex exec review` clean. Merged by the orchestrator; every
slice branches from that commit.

## 4. Slices

Each slice: one worktree, one builder owner, phase 2 commit(s) then
phase 3 commit(s), measured after each. "Owns" lists the only files the
slice edits besides its pin file, `ARTIFACTS.sha256` and `map_pins.json`
(both regenerated at merge). Stops are tour ids
(`~/projects/lv-art-review/tour/<area>/stops.json`).

### 4.1 Map 18 — Ancient Temple (`build_map_18.py`)

**Owns:** `build_map_18.py`, `visual_pins/map18.json`,
`test_tiny_sanctum_visibility.py` (extend only). Reads `lv_cave_vignette`
(gate 0's `near_courses`).

**Phase 2 — VQ-019 (high), VQ-024 (high).**

- VQ-019, Transition Hall near walls (stops m18-12 0%, m18-15 2.3%,
  m18-16 0% min visible). Today: `build_sanctum_gate_hardening` (`:820-870`)
  stacks 15/10 at z 40 and 80 over the crack line y 6143 (x 2047..4095)
  and the hall sides x 2048 and x 4095 (y 4608..6144), on top of
  `build_transition_hall`'s z-0 course; "120 beats the climb because the
  tallest chain step anywhere adjacent is the hall wall-relief top at 46
  (46+72 < 120)". T1: on the **east** side x 4095 and the **crack line**
  y 6143, keep the z-0 drawn course and replace the z 40/80 pieces with
  498 (east) / 497 (crack line) at z 40 and z 88 (top 136 ≥ 120). The
  **west** side x 2048 faces away from the camera and stays as it is. The
  breach pier is excluded: the six `BREACH_PIECES` (`:90-96`, quality 307:
  (2815,0,15), (2816,0,47), (2815,40,15), (2943,40,15), (2815,80,15),
  (2943,80,15)) stay byte-identical, so the drawn 120 stack remains over
  x 2688..2943 and the slit x 2817..2879 at z 0..40 is untouched. The
  `gate_coverage(18, ...)` lines (`test_route_reach.py:1079-1095`, (0,120)
  everywhere on y 6143 x 2080..4064 with the (2719, 2879, (40,120))
  exception, and on x 2048/4095 y 4768..6112) must pass unchanged — 497 at
  40 and 88 covers [40,136). `tag_breach` (`:99-113`) must still find
  exactly six. Also lower the Outer Hall's south line y 4607 and east line
  x 4607 if the audit shows leg cells below 50% there (they are one 40
  course today: measure first; T1 applies only if a second course exists).
- The pier is the one place the rule cannot hold: a full-size Avatar in
  front of x 2688..2943 at y ≥ 5983 is covered by the drawn upper
  courses, and those records are what `EggTempleEntry` destroys and
  `TEMPLENT`/`CRACKHNT` key on (shapes 15/47). Proposed
  `occlusion_allow` box: x 2624..3007, y 5983..6143, z 0..40, reason
  "breach pier: BREACH_PIECES q307 must stay drawn until the breach" (D11).
  Everything else on the hall leg must pass 50%.
- VQ-024, sanctum west passage (m18-19 13.8%; screen04 98.89 with zero
  unpainted allowance). The phase 1 fix-up lowered the island's north and
  middle lip and recorded "existing west-wall occlusion persists farther
  along the passage". Find the occluder with
  `visibility(scene, poses, spot, details=True)` (`sort_groups` names the
  covering items) at the west-turn cells x 2591..2687, y 7168..7551 with
  `Poses(shape=867)`; expected [INFERENCE] the island's south-row crest
  tiles at z 48/56/72 or the shrine's x 2303 wall run. Apply T1 to that
  run via `Cave(near_courses=1)` **only if** `sanctum_island`'s screen04
  pixel check (`:682-721`, raises on any change) and `test_sanctum_clearance`
  still pass; otherwise the fix is the island's own tiles (lower the
  south-row crest to z 48, 32 wide) as the fix-up did. The tiny legs in
  `test_tiny_sanctum_visibility.py` (`>= .9` on the approach, `.65/.9/.5`
  at the west turn) are the floor; extend them through y 7551.

**Phase 3 — VQ-048 (medium), VQ-050 (medium), VQ-056 (medium), VQ-063 (low).**

- VQ-048, sanctum east/south edges black between rock panels (m18-15..26):
  `SANCTUM_MASK`'s S/E faces go invisible whole when any piece would paint
  into screen04 (`Cave._face` `:636-637`), and `void_cover(ground,
  within=SANCTUM_BOX)` paints black outside the floor. Technique: a
  textured backfill the window check allows — 301 rock tops at z 48 on
  mask rock cells adjacent to the floor (T4 missing tops), each piece
  tested with `shot.paints_window` and dropped if it paints into screen04,
  plus 894 backdrop plates at z 0 under the sawtooth floor edge (T7, cover
  not seed) where a top is refused. Acceptance: frame black at m18-19/20/21
  down from 24.9 / 26.3 / 21.9%, screen04 pixels identical (the fix-up's
  "zero changed pixels out of 59,200" check), `test_sanctum_clearance` box
  `(2880, 6783, 0, 180, 639, 40)` clear.
- VQ-050, N/W rock courses with black joins (jagged shell, `jag=True`,
  `:593-638`): posts (29) at every notch the jag leaves (T4 corner
  slivers), measured at m18-17/18/22/25/26.
- VQ-056, Outer Hall north-wall jog at x 2048 (y 2560 vs 2591,
  `build_outer_hall` `:291-369`): one 10 piece (32x128x40) at the jog's
  open 32x31 notch, or a 47 stub, so the two lines meet; `RELIEF_LINES`
  unchanged. Stops m18-06/08.
- VQ-063, temple hall exterior corners (m18-05/12): the differing hall
  widths (Outer Hall x 1536..4607 vs 2048..4095) leave black outside the
  near corners; 895 plates under those corners (T7) or 301 at z 0 outside
  the wall with a 497 curb. Count the records (ceiling 2,400).

**Constraints:** no shot window but screen04 (origin per `SCREEN04` in the
builder; 98.89 / 0 unpainted); `test_crack_geometry` (tiny ≥ 8 positions,
full none; opened: ≥ 64 positions, "no lintel left"), `test_sanctum_clearance`,
`test_tiny_sanctum_visibility`, `gate_coverage(18)`, `test_paint_cycles`
(Map 18 frames), the breach line (`BREACH_PIECES`, `tag_breach`), the
entry egg box (2864, 6240, 0) ±256/±128, `EggCrackHint` ±192 on the hall
side. Fresh world for every capture.

**Acceptance numbers:** walkable black 0 (now 0); leg cells below 50%: 0
outside the pier box (now: m18-12/15/16 at 0 / 2.3 / 0%); map-wide
≤ 13.6% / ≤ 6.5% (cave limits 58/37); frame black ≤ 18.0 / 45.3 / 64.7
and lower at every VQ-048/050/056/063 stop; records ≤ 2,400.

### 4.2 Map 9 — Galjeron's cave (`build_map_09.py`)

**Owns:** `build_map_09.py`, `visual_pins/map09.json`.

**Phase 2 — VQ-026 (medium), VQ-029 (medium), VQ-032 (medium).**

- VQ-026, hall south and east walls (m09-16 0%, m09-17 0%, m09-18, m09-22):
  `build_zone_2_chamber` (`:265-406`) runs the cave pair 26/32 at z 0 and a
  full-width upper course at `z = CAVE_COURSE` (48) on all four sides. T1
  on the **south** line y 15359 (x 12800..14847, gap 14208..14464) and the
  **east** line x 14847 (y 13312..15359): keep the z-0 course, replace the
  z-48 course with 497/498 at z 48 (top 96, today's top: a lone drawn 48
  course is within climb72). North and west keep both courses.
- VQ-029, the lintel over the south doorway (m09-21): the z-48 course
  "runs the whole width as a lintel" (`:283-284`, `:299`). With T1 the
  lintel over the gap becomes a 497 at z 48 (the Avatar is 40: passes),
  and the doorway reads as a gap in a one-course wall. The north throat's
  lintel (x 13824..14848 at y 13312) faces away and stays.
- VQ-032, worked passage east wall 80 tall (m09-27): `build_zone_3_passage`
  (`:408-463`) lays `WALL_NS` at z 0 and 40 on x 13824 and x 14847. T1 on
  x 14847 only: drawn z 0, 498 at z 40 and z 88. `accent_reliefs(items,
  [('x', 13824)])` is the west line and is untouched.

**Phase 3 — VQ-051 (medium); VQ-062 accepted; VQ-001 waits for D10.**

- VQ-051, guardian cave closure box joints and slits (m09-01..06; screen10
  89.52 with a 794 unpainted allowance): `Cave(shot, (100, 90),
  GUARDIAN_MASK)` without `jag`, so the shell is short stacked runs with
  corner posts and no continuous cap. T4: 125 crest tiles on the shell's
  rock cells outside the window at z 96 (two courses) and posts at every
  convex corner; every added piece passes `shot.paints_window` → dropped,
  as `Cave.build` does for the shot's own pieces. Measure screen10 before
  and after; it must not fall below 89.27.
- VQ-062 (m09-12/19/27): accepted as the cave idiom; no work; the ratchet
  holds the frame numbers.
- VQ-001 (the dais black inside screen10): the phase 1 slice showed any
  floor there costs the window 8 points. Not in scope unless D10 says
  "revise screen10".
- The 19 prop-pixel cells (235/237/240/529 bones and the dais) are
  ratcheted, not fixed.

**Constraints:** screen10 (origin per `place_screen10`; `SCREEN10_BLACK_FILLERS`,
`SCREEN10_RELIFT`), `GUARDIAN_MASK` cells, `dais_skeleton` (747/797 at
`DAIS_X/Y`, `DAIS_TOP = 56`), the route `(13696,14208,0) → 203 / 200 /
dais top (14360,12792,56)`, trigger 200 corridor `([], ['N'])` and 203
`([], ['S'])` in `arrival_corridors`, `test_map_edges` (skips 35:10),
`void_cover(items)` last (`:487`; it emits the 30 tiles of 35:10 the
screen10 edge needs — do not remove them).

**Acceptance numbers:** specified walkable black 0 (now 0; prop pixels
≤ 19); leg cells below 50%: 0 (now: m09-16/17/20 at 0%, m09-14 50.2%);
map-wide ≤ 26.6% / ≤ 10.1%; frame black ≤ 26.1 / 53.4 / 64.3 and lower at
m09-01..06; screen10 ≥ 89.27; records ≤ 1,800.

### 4.3 Map 11 — Elemental Dungeon (`build_map_11.py`)

**Owns:** `build_map_11.py`, `visual_pins/map11.json`. Reads
`lv_landscape.rim` and `lv_cave_vignette` (no edits).

**Phase 2 — VQ-020 (high).**

- Hub connector south walls (m11-49 5.7%, m11-50). `build_corridors`
  (`:1021-1062`): the Earth→Hub lane y (5152, 5600] (448 wide) is flanked
  by 26 courses at y 5152 (north) and y 5632 (south), 48 tall; the Air→Hub
  lane likewise over x 11264..14336; Hub→Water is flanked east/west at
  x 9472 / 10016 (512 wide). T1 does not help a 48 wall (one course is
  all there is) and T2 cannot recess a lane the leg runs through. Use the
  **drawn-course swap**: replace the south flank of Earth→Hub and Air→Hub
  and the east flank of Hub→Water with 497/498 at z 0 and z 48 (invisible,
  same box) and lay a 128-wide **floor strip** of the corridor's own glob
  tile (242 from glob 42 / 301 from glob 397) beyond it as a visual verge
  with its own 497/498 curb on the far side, so the corridor reads as a
  sunken lane between a drawn far wall and a low verge rather than a
  walled slot. Visibility on the lane then depends only on the far wall
  (behind the Avatar). If Douglas prefers a drawn near wall (D8 option c),
  the alternative is the cave kit's 16-tall kerb — there is none in the
  26/32 family, so that option means "leave it".
- Prove: `test_monster_eggs.py:165-171` (`HUB` box, corridor flanks x
  9472/10016, body x 9536..9984) and `SOUTH_PASSAGE` (`:859-890`) still
  pass; the Map 11 route (`step=16`, `SI_SOLID|SI_DAMAGING`,
  `hurt_margin=128`) reaches the same targets; `FIRE_LINES` clearance
  (`:1389-1396`) unchanged (not near the corridors).

**Phase 3 — VQ-043 (high), VQ-045 (high), VQ-065 (low); VQ-035 and VQ-038
(high) per D5.**

- VQ-043, screen07 rock band black tops and missing backfill (m11-11/12/13;
  screen07 97.27 with a 6-px allowance; four of the six specified cells are
  here at z 8): rock cells in `SCREEN07_MASK` (cols 48..79, rows 152..174)
  have no top ("Rock has no floor: the map's void plates paint its top
  black"). T4 missing tops: 301 (`ROCK_FLOOR_FRAMES`) at the rock's crest
  z 96 on every mask rock cell not in the window, posts at notches, and
  the four z-8 specified cells floored with the shot's own floor shape at
  the shot's z. Each piece `paints_window`-tested. `SCREEN07_PILLAR` (865 at
  (7680,21504,0)) and `SCREEN07_STANDINS` untouched; `screen07_faces`
  (891/892 swaps) untouched; `test_art_props.py:411-493` (pillars,
  `FIRE_RECEPTACLE = (7935, 21759)`) passes.
- VQ-045, Fire screen05 alcove black polygons beside the bench (m11-06;
  screen05 94.55, 0 unpainted; two specified cells at z 8 near (2623,
  14975)): `SCREEN05_LEFT_OUT` records the 400 that "was solved in the air
  over the black lip". Floor the two cells and the lip with the alcove's
  floor at the shot's z (the relifted 400's frame 2 lip stays); pieces
  window-tested.
- VQ-065, Water bay wall-top corner notch (m11-08): a 29 post at the
  section's NE corner (x 14335, y 14336) where the 26 run and 32 run meet
  without one; the rim's own post at (14368, 14336) is outside and stays.
- VQ-035 / VQ-038, black beyond the 96 rims and between sections (27
  stops): `build_rim` (`:1256-1293`) rims every section outline with
  visible 96 rock and a crest; the voids between sections are exterior
  ("each gets rimmed on both faces and stays black"). Under the cave
  calibration this is retail's idiom (Map 8's cave: mean 46% black), and
  Map 11 is already inside the cave limits (8.3 / 36.0 / 56.5). Default
  (D5 option a): accept, ratchet the numbers, fix only reachable black.
  Option b: 895 plates (frame 0, dark flagstone) at z 0 in every void
  block within view of a floor, about 1,600 records (cap 12,000), cover
  not seed (gate 0), giving a dark-stone exterior instead of black.
- The 150 prop-pixel cells are the Fire wing's lava pools (318 f0, hurt
  shape, dry-flood reachable but never walked); ratcheted, not fixed. The
  5 cells of 35:10 and 1 of 564:2 are `void_cover` output over loose 301
  (`lv_cave_vignette.py:645-697`); they vanish when the tops above are
  floored.

**Constraints:** screen05 origin (2048, 14080), screen07 origin (6272,
20608); `gate_coverage(11)` and `gate_reach(11)` (pad room y 22527/22528,
x 8192/9215, (0,120)); the two sealing boulders at (8576,22528) and
(8704,22528) q299 are pinned (VQ-016 is phase 4 and needs Douglas);
`test_map_hygiene` row 11; `build_rim`'s `unwalled` (`:1296-1335`, the
`1 -> 32 -> 10 -> 1` cycle) if the corridor flanks change height;
`test_paint_cycles.py:445`.

**Acceptance numbers:** specified walkable black 0 (now 6); leg cells
below 50%: 0 (now m11-49 5.7%); map-wide ≤ 12.1% / ≤ 5.2%; frame black
≤ 8.3 / 36.0 / 56.5 (cave limits 47/77/91), lower at m11-06/11/12/13 and,
if D5 = b, mean ≤ 5%; screen05 ≥ 94.30, screen07 ≥ 97.02; records
≤ 11,000.

### 4.4 Map 10 — the Lost Vale (`build_map_10.py`, `lv_map10_ground.py`, `lv_vale_terrain.py`)

**Owns:** the three files above (`lv_map10_ground` and `lv_vale_terrain`
are imported by nothing else), `visual_pins/map10.json`. Does not edit
`lv_landscape.py` (it imports `track, tile_run, span, cliff_run_y`).

The Field (`lv_vale_terrain.Field`) is the engine for everything here:
cells of 128, heights per cell, `_faces` per cell (`:459-512`),
`_barriers` 497/498 at h and h+48 on dropping sides of walk cells
(`:443-457`), `_globs` one egg per all-plain same-height chunk
(`ROCK_GLOBS = (397, 397, 397, 2241)`, `EARTH_GLOB = 875`, `LAKE_GLOB = 55`,
`:375-403`), `foot()` crest plates where courses stop above ground
(`:160-171`). The outer rim is a one-cell band of ground at `RIM_Z = 104`
(160 beside raised ground, a second band at 152 for `cx < 70 and cy < 95`)
with no barrier of its own (`lv_map10_ground.rim_cells` `:150-174`,
`map10_field` `:521-528`); beyond it, only `void_floor` plates (2,426).

**Phase 2 — VQ-025 (medium), VQ-027 (medium), VQ-028 (medium), VQ-033 (medium).**

- VQ-025, east and south rim faces hide the Avatar (11 stops, m10b-52 0%,
  m10b-64 2.6%; a sample 224 units inside the rim): the 104 rim's south and
  east faces cover a body within ~830 units. Two cases by the ground's z:
  - ground at z ≥ 48 (the Passage Test plateau, already flush via
    `flush_edges`; Ragnar's cache tier 56; the Sacred Circle crest 104):
    T1 as the plateau does — `rim_cells(..., flush=...)` plus
    `flush_edges` for every S/E rim edge beside raised ground, visible
    courses ending at the ground, 497/498 at h and h+48;
  - ground at z 0 (Gunnar's yard, the lake's south shore, the temple
    forecourt, the garden/knoll surroundings): a flush edge has no
    drawn course at all (`_flush_tops(0)` is empty) and the ground ends
    at an invisible wall over the skirt. This is D3: (a) keep the drawn
    rim and pull the walkable edge in by T2 (a 497/498 strip one cell
    inside, losing a 128 strip of yard), or (b) flush edge + water skirt
    (glob 55 beyond the barrier, a 128/126 shore line on the barrier's
    strip), or (c) flush edge + rock plain. Recommended (b) on the map's
    east edge x 22528 and the southern zones' south edges; (a) is the
    fallback where Douglas wants the rim kept.
    The leg cells that must pass are those within 830 units of a S/E rim:
    Gunnar well, Hrodny's chest, Sacred Circle, lake causeway, Ragnar's
    cache, Passage Test.
- VQ-027, raised reliefs (shelf and relief cliff faces in front of the west
  lake tip and the south-west tier; m10a-41/47, m10b-46/59 0%; screen09
  94.84 /148, screen18 98.58 /55, screen21 93.53 /540): the `RELIEF`
  rectangles (`lv_map10_ground.py:60-101`: garden 104, knoll 64, temple
  112, tarn 64/112 "scenery, not walked", plateau 56, crest 104) emit S/E
  faces of 48-course stacks over walked ground. T2 for the tarn shelf (not
  walked: recess the walk cells beside its S/E faces by one cell with a
  497/498 strip); T1 for the garden and knoll where the walk is on the
  tier itself (their S/E edges flush, barriers at h/h+48, the drop drawn
  from the lower ground's side as the crest `foot()` plates do). Every
  relief edge in a shot window keeps its pixels: run `test_vignettes` on
  screen09/18/21 after each change and compare `keep=` strings.
- VQ-028, Passage Test canyon walls (m10b-20, m10b-58, m10b-61): the ramp
  `RAMP_ROWS`/`RAMP_X` (`:360-361`) and `TERRAIN` rows at 24/48/64 sit
  inside `RIM_HIGH = 160` rim cells. T1: the rim cells east of the ramp
  (x > 13312) and south of the corridor get flush S/E edges with barriers
  at h/h+48 at the ramp's own z per row (the 4-lattice rule:
  `map-geometry.md` "A walking actor changes z by 0, ±4 or ±8"). The 10-10
  spire paint cycle `66 -> 1` against the rim column (`:1203-1215`) must
  not return: `test_paint_cycles` frames the spire at (12383, 29631, 64).
- VQ-033, temple pit near wall over the stair foot (m10b-17; screen17
  93.69 / 59): the pit is the three `TEMPLE_Z = 112` rects "open to the
  forecourt south of it"; the stair foot is the shot's tail
  (`shot_completions`, `:2002-2023`) with `stair_barriers(18335, 18527,
  …)`. T2: the stair-foot cells covered by the pit's south face (the rect
  `(112, 135,178,140,183 keep='E')`) lose their walkable strip to a 497
  curb if `temple_stair_foot` (`test_route_reach.py:961-1026`,
  `TEMPLE_FOOT_YS = range(23263, 23352, 16)`, `TEMPLE_LEAVE`) still passes;
  otherwise T1 on that face (flush, barrier at 112/160). Trigger 211's box
  (18432, 23552, 0) ±96 and `PAD_210 = (18432, 22719, 112)` unchanged.

**Phase 3 — VQ-034 (high), VQ-036 (high), VQ-041 (high), VQ-042 (high), VQ-057 (medium), VQ-061 (medium); the 31 unpainted cells.**

- VQ-034, the Vale boundary and canyon rims end against black (29 stops;
  screen17/19/20/21 windows): T3 skirt. Extend `map10_field` with a band
  of **skirt cells** outside the rim band, four cells deep beyond every
  rim cell (so the ring of plates beyond lies past `VIEW_RY`), kind
  'skirt', z = the adjacent rim cell's z (104 / 152 / 160) on N/W and
  drawn-rim edges, and z 0 water (`LAKE_GLOB`) or rock per D3 beyond flush
  S/E edges. Skirt cells are not in `walk`, emit through `_globs` as one
  egg per chunk (397 rock, 55 water) and loose tiles only at partial
  chunks, with faces between skirt levels from `_faces` as today. The
  Passage Test mesa's surround is the same band. Record estimate: +900
  eggs/tiles, the plate ring moves (count ±200); report both. The N/W
  band at 152 ("great cliffs to the Northwest") becomes the inner edge of
  the 152 skirt. Skirt pieces inside a shot window are dropped by
  `shot_closure`'s rule (the vignette owns its pixels); a skirt that shows
  in a window must match the shot (compare `test_vignettes` scores before
  and after; screen19 (18816, 6272) and screen20 (19712, 7552) look east
  toward the x 22528 edge).
- VQ-036, modular cliff joins expose vertical black slits (16 stops;
  screen17/18/21): per-cell faces shortened to the corner post
  (`_faces` `:459-512`, `POST_SE = (0,1,2)`, `POST_NE = (6,7,9)`), N/W
  faces dropped over void (`:472-475`) and `DARK` frames on N/W faces. T4:
  a post at every corner square no face claims; N/W faces drawn with `LIT`
  frames wherever the neighbour cell is not rock at the same or higher z;
  `seam_faces` (`:282-362`) against shot cells slid along the ray as
  `shot_faces` does. Verify at m10a-55/57/59/62, m10b-15..18/20/46/47/55/57/61..63.
- VQ-041 / VQ-042, the lake (m10a-49/55, m10b-10/11/12/42/43/53; screen02
  98.40 / 0, screen09 94.84 / 148): T6. Keep `WATER_DEEP = 16` unless D7
  says otherwise; find the body's striping owners with `Scene.paint`
  ownership at m10b-11/12 (expected: `SHORE_Z` crest pieces on interior
  cells with a dry side, and `lake_rails`); make interior shore cells
  plain water; on the outer perimeter lay the 128/126 bank set
  (organic-maps §5) outside the windows; the rectangle's corners get a
  one-cell jag (`ISLAND box jag 2` is the precedent). `rails` (497/498 in
  the water cell's strip, `:618-646`) stay; the causeway (13824, 19456, 8)
  and the two VQ-007 slabs stay.
- VQ-057, scaffold corner (m10a-48/61; screen18/21): the wooden frame's
  south corner over a tier discontinuity — a `foot()` plate or an
  under-floor at the corner cell (T4 under-floors).
- VQ-061, lava/rock join NE (m10a-54; screen18/21): lava cells are plain
  flats at 0 with `LAVA_EDGE` frames on dry sides; a raised neighbour's
  face comes down to 0 and the gap between is black. T4: a crest `foot()`
  plate under the face's foot on lava-adjacent cells, or the lava edge
  frame on the rock side. The lava's footprint and frames stay identical
  (never frame 33; the Map 10 route models no hurt margin, so any lava
  cell added beside the leg would go unnoticed by the estate).
- The 31 unpainted cells: garden mesa/stair x 9023..9631 / y 21151..21535
  (z 0/8/64) and Gunnar/Hrodny x 19359..20511 / y 7487..8799 (z 0): floor
  them with the cell's own material (`field.floor_item(c, z)`), checking
  each against screen18/21 and screen19/20/22 windows.

**Constraints:** eight windows (screen02 (13184,17792), 09 (10496,15616),
17 (17536,22016), 18 (9088,19584), 19 (18816,6272), 20 (19712,7552), 21
(8320,20608), 22 (17408,7680)); `RAY_SLIDES`; 68 pinned rows (`map_pins`);
the route (`:1468-1510`) and Ezrekal's house; `map10_wedges`,
`temple_stair_foot`, Hrodny's chest checks (`:873-898`), `test_map_edges`
(5.8 s), `test_paint_cycles` Map 10 frames, `test_endgame_hatch_box`
(`build_map_10()`), the lake rails, the lava's footprint and frames
(never frame 33). Records: cap 25,000, exit 23,000.

**Acceptance numbers:** specified walkable black 0 (now 31); leg cells
below 50%: 0 (now m10b-52 0%, m10b-64 2.6%, m10a-47 11.8%, m10b-59 0%);
map-wide ≤ 4.7% / ≤ 2.2%; frame black: ratchet ≤ 2.1 / 16.4 / 51.2, design
target after the skirt mean ≤ 1%, p95 ≤ 8%, max ≤ 30% (the town limits
7/38/62 are the gate); all eight windows hold; records ≤ 23,000; the
expanded whole-map count reported (37,566 now; it is a warning, not a
gate — `retail-calibration.md` §Record budgets).

### 4.5 Map 13 — the Cloud Cliffs (`build_map_13.py`, `lv_map13_tiers.py`)

**Owns:** `build_map_13.py`, `lv_map13_tiers.py` (imported only by Map 13
and its tests), `lv_map13_views.py` / `map13_window_fit.json` if the fit is
re-run, `visual_pins/map13.json`. No phase 2 items.

**Phase 2:** none in the backlog; the leg (pad 207 → summit → 209) must
still pass rule B after phase 3, and `map13_rim_drawn`
(`test_route_reach.py:769-819`: holds E/SE/S/SW off pad 207 leave the
Avatar ≤ 10% covered) is the existing gate on the valley's S/E edges.

**Phase 3 — VQ-037 (high), VQ-039 (high), VQ-049 (medium), VQ-052 (medium), VQ-053 (medium), VQ-058 (medium); VQ-054 accepted.**

- VQ-039, valley south and east edges end as a slab over black (m13-01..12;
  screen15 95.98 / 495): `build_valley_rim` (`:826-854`) rims the whole
  field rectangle with `flush` on the map's south edge y 12288 and east
  edge x 6656, so beside valley cells there is no drawn piece at all —
  only 497/498 at z 0 and 48. T3 skirt beyond the barrier at z 0, four
  chunks deep (y 12288..14336, x 6656..8704), material per D4: dark water
  (glob 55, continuing screen15/16's navy; recommended), rock (397) or
  cloud (874 tiles). A water skirt is `SI_SEA` — cover, not floor, in
  `void_cells`; the rim's barrier already stops the walk. `map13_rim_drawn`
  must pass: a z-0 skirt draws nothing over the Avatar. `test_climb_width`
  ROI (1500, 0, 6700, 12300) unaffected.
- VQ-037, lake and skull-ring terraces black tops and slabs (11 stops;
  screen14 89.86 / 3, screen15, screen16 94.59 / 240): `SHOT_CUTS`'s two
  35:10 pieces at (4367,4323,137) and (4239,4323,137) are the shot's own
  and stay. The rest: `build_field`'s HIDDEN cells (region cells with no
  top) and `emit`'s black N/W frames. T4: every ROCK cell gets a crest
  (`crest_frame`) — HIDDEN cells included, at the shot's z where the
  window fit gives one — and N/W faces take textured frames when
  `exposed()`; widen `exposed()` to "any 8-neighbour is not rock at ≥ this
  z". Each piece `in_a_window`-refused (`:1038-1062`, `WINDOW_MARGIN = 16`).
  Re-run `lv_map13_views.py --fit` only if a window score moves; the
  three windows must hold.
- VQ-049 / VQ-053, summit tier slivers and cloud through gaps (m13-29..34,
  42; screen01 95.35 / 49, screen13 98.91 / 0, screen14): `face_items`'s
  corner ownership (`:196-200`) and `_walk` jogs leave corner squares;
  `cloud_fill` at z 48 shows through them. T4 posts at unclaimed corners
  (the `27 at 96 with a 29 post when E also drops` rule generalised to
  every S/E/N/W combination), and `courses_down`'s lip rule (a last lip at
  0 overlapping, "the 4-unit gap showed as a black seam") applied at every
  tier change, not only at the floor. `test_paint_cycles` frames every
  second climb tile and the summit (`:245-350`); no new cycle.
- VQ-052, the lake body as a navy pit (m13-15/16/18/19/20/44): T6 — the
  shots are made of 347:16; keep it (D7) and fix the blocky material
  boundary with a one-cell halo of `WATER` at the shore cells outside the
  windows, and the 128/126 bank set where rock meets water outside the
  windows.
- VQ-058, climb-foot zig-zag seam (m13-09/14; screen15): `foot_apron`
  (`:378-390`) sets the foot row to ROCK 0 valley; the seam is the 4-unit
  risers meeting the valley globs. A 125 crest strip at z 0 along the
  apron's north edge (T4), keeping `CLIMB_Z_STEP = 4` risers and
  `test_climb_width` FOOT holds.
- VQ-054 (m13-33/34/35/38): accepted north edge. Goes into
  `frame_allow` as one box (the summit strip, y < 1024 [INFERENCE: the
  slice draws it from the four stops' camera rects]) once Douglas confirms
  (D-list item 4), so rule D can be met by the rest of the map.

**Constraints:** five windows (screen01 (2176,0,56), 13 (3456,−384,120),
14 (−1024,256,0), 15 (−1024,2688,−8), 16 (−1152,1536,−8)); `SHOT_CUTS`,
`RAY_SLIDES`, `WINDOW_FILLS`, `UNFACED_BY_HAND`; the climb (`climb_tiles`,
`CLIMB_Z_TOP/STEP`, `lanes_at`, `summit_cells`, `test_climb_width`,
`test_harpie_corpses`, `HARPIE_REST` in `test_monster_eggs`); `CX_EAST =
63` cloud extension for `cy <= 31`; `MAP13_SOUTH_EDGE_Y = 12288`,
`MAP13_EAST_EDGE_X = 6656`; `test_map_edges` (2.6 s). Records: exit 8,000.

**Acceptance numbers:** specified walkable black 0 (now 0, 5 prop); leg
cells below 50%: 0; map-wide ≤ 3.8% / ≤ 1.2%; frame black from 9.9 / 39.3
/ 59.2 to the town limits ≤ 7 / 38 / 62 outside the north box (design
target mean ≤ 4%); all five windows hold; records ≤ 8,000.

### 4.6 Map 17 — the Cloud City (`build_map_17.py`)

**Owns:** `build_map_17.py`, `visual_pins/map17.json`. No phase 2 items
(1.2% below half, 2 hidden cells; the leg passes today — confirm with the
test, then only phase 3).

**Phase 3 — VQ-047 (medium); the 16 plates at y 2975.**

- VQ-047, the cloud plate boundary ends in stepped black (17 stops;
  screen11 99.93 / 0, screen12 97.94 / 0): T5. Replace `CLOUD_SEA_AREAS`'s
  two rectangles with a computed sea: every layout cell's boundary
  dilated by the `cells_within_view` window (`VIEW_RX = 1408`, `VIEW_RY =
  1856`), minus layout cells, clipped to cx, cy ≥ 1, as 874 tiles at z 0
  with `CLOUD_FRAMES` by position hash. No curbs on sea cells (`curbs()`
  reads `cells` only) and no path from the layout to the sea: the
  128-square-body route to trigger 208 (`:1180`) and the "direct channel
  crossing remains sealed" check from the phase 1 verifier are the
  proofs. `window_clear` drops nothing of the sea (floors are allowed in
  windows); screen11/12 pixel diffs must be zero (the stamp fills with
  `fill=(874, CLOUD_FRAMES)` already).
- The 16 plates at x 2463..2943, y 2975 (south of screen12's court):
  reachable cells whose floor is `void_floor`'s plate — a hole in the
  layout mask (`lobe()` smoothing) south of the walkway court. Add the
  cells to the layout as cloud (walkable) or as sea behind a curb; either
  way the floor paints. Check the walkway top (2303,3103,8) leg still
  reaches.
- Optional (D8): a 256-unit cloud plate (new art id, 874's texture 2x2 on
  564's footprint, donor 202 physics, cover not seed) to quarter the sea's
  record cost; not required to meet the cap.

**Constraints:** `GOLD_AREAS`, `STRIPS`, `PIER`, `BRIDGE`, `SOUTH_CUT =
10496`, the 400 curb records, the scroll (3328,1536,8) q80 and both
Shield halves pinned, `PAD_209`, `TRIGGER_208`, `reapply_egg`;
`test_art_props.py:623-627`; the route (`:1162`, `:1180`). Records: cap
12,000, exit 10,500 (from 6,665; the sea is about +4,000).

**Acceptance numbers:** specified walkable black 0 (now 16); leg cells
below 50%: 0; map-wide ≤ 1.2% / ≤ 0.1%; frame black from 8.8 / 41.5 /
72.6 to ≤ 7 / 38 / 62 (design target max ≤ 20%); screen11/12 identical;
records ≤ 10,500.

### 4.7 Map 39 — Tenebrae (`build_map_39.py`)

**Owns:** `build_map_39.py`, `visual_pins/map39.json`; may extend
`test_map39_south_edge.py` and `test_map39_lane.py` (never loosen).

**Phase 2 — VQ-021 (high).**

- The LV lane tunnel hides the Avatar (m39-02/03): `lane_glob_replacement`
  re-places glob 742 minus three bottom-course 15 pieces
  (`TENEBRAE_LANE_CUT`, z 48..88) and keeps "the lintel and upper courses
  over each cut"; `TENEBRAE_LANE_WALLS` add side walls at x 16095/16255
  (10/8 courses at z 48, cap 692 at 88, course at 96 to roof plates at
  136: "136 is 88 above the floor, out of climb72"). The retail upper
  courses over the cut and the roof plates are what cover the Avatar. T7
  on the tunnel's own pieces: the roof plates and the retail upper
  courses over the south-facing cut become invisible solids of the same
  box (499/763 for plates; for the 15 wall courses, 497 at the same
  max-corner — the climb-out height 136 is kept by the invisible box) plus
  894/895 backdrops at `(x − 4z, y − 4z, 0)`. The tunnel keeps its
  silhouette from the retail side. `test_map39_lane` (path through the
  tunnel; no path when x 16096..16223 is masked) and `test_map39_south_edge`
  §3 (no non-oak solid with top in [56,128) within a body width of an oak;
  every oak > 72) must pass; **`RETAIL_VOID_EXITS = 7709` exact** (§4) must
  not change, so no new support or drop anywhere near the lane.

**Phase 3 — VQ-040 (high), VQ-059 (medium); VQ-055 retail (D9).**

- VQ-040, treeline black beyond the oaks (m39-03/05..11;
  `retail-exposed-by-lv`): the 274 plates are `void_floor(_base_map_39_context()
  + items)` filtered by `_accepted` (`_ACCEPT_SOUTH_X/Y`, `_ACCEPT_EAST_X/Y`,
  `:470-480`). T3: ground beyond the oaks in Tenebrae's own material —
  retail grass/earth glob eggs at z 48 (the lane's `GROUND = 48`) over the
  accepted rectangles, one per chunk, with the oak line as the visual
  edge and 497/498 at z 48 and 96 along the oaks' outer side where no oak
  box closes a gap (the fences `:292-297` and `TENEBRAE_OPEN_EDGES` are
  the pattern). The 274 plates then fall out of `_accepted` by
  themselves. Organic-maps §5's "lower forest and moat bank" is the
  longer version; this slice does the ground only. `test_map39_south_edge`
  §1 sweeps (body 64x40 due south from y 20279 to 20543, x 14112..20511)
  must leak nowhere, §2 flood (void plates removed) must show no exposure
  with y ≥ 19480, §5 `void_in_view` south of 20479 / east of 20991 == 0
  with the skirt counted as cover.
- VQ-059, harbour end wall drops into black at the channel (m39-04):
  `TENEBRAE_HARBOUR_SOUTH` (x 13695..14079 at y 20511, courses to 136).
  Backdrop the wall's free faces and the channel end with retail water
  (347 at the channel's z) and a 894 plate under the wall's foot where
  nothing paints; no new standing level (§4's 7709).
- VQ-055, the main-gate canal as a black rectangle (m39-02/07/12): retail
  water under an arch; D9 — recommended leave.

**Constraints:** `TENEBRAE_LANE_*`, `TENEBRAE_TREELINE_*`,
`TENEBRAE_HARBOUR_*`, the LB egg (17150,19700,48) q304, the apparition;
`BASE_ITEM_REMOVALS` (the glob egg only); every retail record outside the
LV additions byte-identical (the phase 1 Map 8 pattern: "raw records for
every map except N byte-identical"); records raw ≤ 6,000, expansion
≤ 31,000 (29,068 now: each glob egg adds 16 expanded).

**Acceptance numbers:** specified walkable black 0 (now 0, 14 prop); leg
cells below 50%: 0 through the tunnel (m39-02/03); map-wide hidden share
from 6.1% to ≤ 6% (town), below-half ≤ 12.7%; frame black from 7.0 /
39.1 / 75.8 to ≤ 7 / 38 / 62; `RETAIL_VOID_EXITS` 7709; records ≤ 6,000.

### 4.8 Map 8 — Mythran's caves (`build_map_08.py`)

**Owns:** `build_map_08.py`, `test_map08_backdrop.py` (extend),
`visual_pins/map08.json`. Everything on Map 8 that is `retail` class waits
on D1/D2; the slice starts with the LV and `retail-exposed-by-lv` work.

**Phase 2 — retail items VQ-018, VQ-022, VQ-023 (high), VQ-030, VQ-031
(medium): D1.** If D1 = b, VQ-018's northern cave roofs over the door
chamber corridors (564 at z 88-96, 334 roofs; stops m08-36..47) get T7
exactly as the south shelf did: ceilings → 499/763 at the same z plus
894/895 backdrops; walls and shelves (VQ-022, VQ-023, VQ-030, VQ-031)
stay retail. The door-chamber leg (pad 200 → trigger 201) is then
measured; `door_approach`, `first_visit_approach`, `deliberate_use` on the
slab (20639,3967) and `chain_201_keyboard_run` must pass. If D1 = a, the
slice records the leg's visibility in the pin file as an `occlusion_allow`
box "retail roofs, Douglas 2026-11" and moves on.

**Phase 3 — VQ-003 (regressed), the VQ-004 / VQ-008 finish (Astra
"improved"), VQ-046's LV-route stops; VQ-044, VQ-060, VQ-064 retail (D2).**

- VQ-003, the first seam opening (m08-05/06/07). Phase 1 floored the
  threshold `(29695,24575,56)` with four 301s and kept the lintel
  `(29695,24415,104,32,6)`; the fix-up then placed 894/895 backdrops for
  every replaced surface at `(x − 4z, y − 4z, 0)`, and Astra graded the
  result **regressed**: "added rock overlaps the opening around (130, 205)
  in m08-05, reducing it to a black triangular slit with no visible floor
  repair", "a conspicuously straight upper edge, with a small detached
  rock fleck above it around (320, 213) in m08-06". Cause to confirm
  first: with `Scene.paint(camera(m08-05), avatar=True)` ownership, list
  every 894/895 record whose pixels fall in the box Astra names (m08-05
  around (130,205), m08-06 around (320,290) and (320,213)); expected
  [INFERENCE] the backdrop of a `LV_SHELF_CEILINGS` entry over the
  threshold, which from the trench camera (z 0) paints across the
  aperture that the removed wall segment `(29695,24447,56,32,1)` opened.
  Fix, in this order of preference: (1) restore the original 334/564
  ceiling records over the first seam (keep them drawn, as retail; the
  seam's ceiling was not what hid the Avatar at m08-07 — the raised
  retail shelf is, per the phase 1 report) and drop their 499/763 +
  backdrop replacements, so nothing paints into the aperture from the
  trench side; (2) if a ceiling there must stay invisible for the m08-07
  visibility (40.7%), clip: omit the backdrop for that one record and
  under-paint the aperture's floor only. Then the aperture: the removed
  segment's hole must read as a doorway — jambs are the retained lower
  rock courses; give the threshold's four 301s a visible dark-floor
  continuation one cell into the trench side (301 at z 56 at (29695,
  24703)?) only if it is outside the pocket's pristine records (the 304
  pocket cells are retail: do not add LAND there) — otherwise accept a
  dark doorway with a drawn threshold. Acceptance: Astra "fixed" or
  "improved" at m08-05/06/07 against the **tour2** before images (not the
  phase 1 after); walkable black on the exposed component stays 0 of
  15,454; m08-07 min visible ≥ 40.7%; frame black at m08-05/06 ≤ 20.82 /
  51.28% (the pre-phase-1 engine values); `test_map08_backdrop` updated
  to the new record set (its "every replaced surface is under-painted"
  check must still hold for every surface that remains replaced).
- VQ-004 / VQ-008 finish: Astra: "the exposed floor ends in conspicuous
  straight, tile-shaped steps against the black gaps (m08-10 right edge,
  m08-12 lower right)", "an isolated vertical rock panel immediately left
  of the Avatar around (310,125) in m08-09 / (270,150) in m08-49". T3 with
  895 plates (564's frames: 0 dark grey; the 334-clone 894 for cave rock)
  at z 0 projected, under every black block within view of the shelf's
  floor cells (the `cells_within_view` dilation of `LV_SHELF_FLOORS`,
  minus cells any retail item paints) — cover, not seed. The "rock panel"
  at the second seam is one of `upper_walls`' retained lower courses or
  the 498 swap's neighbour: identify by ownership at m08-09 and either
  remove the orphan course or add its neighbour course so the jamb reads
  as a jamb. Records: each 895 is one raw and one expanded record;
  expansion headroom is 3,491, so the plates are budgeted at ≤ 1,200 and
  the pin file records the expanded count.
- VQ-046 (18 stops, retail): the four on the LV route component
  (m08-45/46/47 door chamber, m08-15 plateau gate) are candidates for the
  same 895 underpaint if D2 = b; the rest are retail idiom.
- VQ-044 (pool bank, m08-03), VQ-060 (ledge notches, m08-02), VQ-064
  (island deck corner, m08-27): retail, off the LV route; D2 default
  leave.

**Constraints:** no shot window; `BASE_ITEM_REMOVALS` (globs 933, 936 and
the 43 shelf globs) and `SEAM_GLOB_ITEMS` / `SEAM2_GLOB_ITEMS`; the
trigger-200 pocket `(20415,2783,0)` on its 301 f3 slab at z 1; `TABLE[8]`
pads 200/213 at (20111/20143, 3175, 8), trigger 201, gated 212
(20575,3903,0); `LB_BACKSTOP_*`; `test_map08_backdrop` (backdrops are
FIXED+DRAW only; ceiling pixels painted at (29279/29343, 26495, 56); Avatar
≥ 0.97 there; first-seam floor pixels painted at (29311, 24415, 56)); the
shelf arrival (29680,24400,56) and the vq1 engine walks; every pristine
record outside `BASE_ITEM_REMOVALS` byte-identical; `usehighres=false`
captures for anything that changes a ceiling (the fix-up's stale-pixel
test: fresh vs shifted frames, zero differences).

**Acceptance numbers:** specified walkable black = the 256-cell
`inherited_black` list exactly (0 outside it); leg cells below 50%: 0 on
the shelf leg (m08-09 60.1%, m08-49 83.7% now; m08-07 40.7% is inside the
first-seam allow box if D1/D2 leave the retail shelf) and per D1 on the
door-chamber leg; map-wide ≤ 14.7% / ≤ 7.1% (cave 58/37); frame black
≤ 34.6 / 61.3 / 78.8 (cave 47/77/91) and lower at every stop the slice
cites; records raw ≤ 6,500, expansion ≤ 31,000.

## 5. Order and gates

```
gate 0 (shared contracts) ──merge──► wave 1: 18 · 9 · 11 · 10 · 13 · 17 · 39 · 8  (parallel, own worktrees)
                                       each: phase 2 → measure → phase 3 → measure → report → codex review
                                     ──merge order──► 18, 9, 11 (Cave consumers, back to back; run the three
                                       maps' tests after each), then 17, 13, 10 (void_floor consumers),
                                       then 39, then 8 (expansion headroom last, after D1/D2)
```

- **Gate 0 → wave 1:** §3's gate. Slices branch from the gate 0 merge
  commit. No slice edits `lv_furnish.py`, `lv_cave_vignette.py`,
  `lv_landscape.py`, `exact_reach.py`, `build_all_maps.py` or
  `quest_legs.py`; a slice that needs more from them writes the request to
  the orchestrator (`write agent://`) and the orchestrator lands it on
  main as a gate 0.1 that every slice rebases onto. `lv_map13_tiers.py`,
  `lv_map10_ground.py`, `lv_vale_terrain.py` are single-map modules and
  belong to their slice.
- **Inside a slice:** phase 2 is committed and measured (the after-audit
  and the leg table) before phase 3 starts, so the phase 3 "before" is
  the post-phase-2 build (plan §11.8). A phase 2 change that exposes new
  black behind a lowered wall is phase 3 work on the same branch, not a
  phase 2 regression.
- **Per merge (orchestrator):** resolve `map_pins.json` and
  `ARTIFACTS.sha256` by regenerating (`derive_map_pins.py`,
  `build_artifacts.sh --record`), never by picking a side; the merged
  map's pin rows must be identical to the slice's; `tools/integrate.sh
  --record`; full estate; re-run both audits on the merged map at step
  128 and diff against the slice's after-audit (same numbers ± rounding,
  else stop); Astra grades a sample of the slice's stops (≤ 15 pairs per
  run); card page to Douglas. Maps 9/11/18 are merged consecutively
  because all three run through `Cave`; after each, the other two maps'
  `test_paint_cycles`, `test_vignettes` and `test_visual_quality` rows
  must still pass.
- **Verifier walks (main checkout, fresh game or map switch, never a
  checkpoint on the map under test):** Map 18 hall → crack → tiny sanctum
  → altar; Map 9 chamber → trigger 203 and the dais; Map 11 arrival →
  Earth → Air → pad room; Map 10 the chain in §1.2; Map 13 pad 207 → summit;
  Map 17 arrival → scroll → halves → 208; Map 39 pad → tunnel → egg; Map 8
  shelf and door chamber. Log hygiene: zero `Cycle in paint dependency
  graph`, zero `Non-existent process`.
- **Phase exit:** every map's `test_visual_quality` rows at their
  post-phase-3 pins with rules A–G satisfied; a full re-tour of the phase
  2/3 stops diffed against tour2 and only changed frames sent to Astra;
  `TODO.md` checkbox per map with the date and the commands run.

## 6. Decisions for Douglas (ask before the slice they gate)

**Douglas's answers (2026-11-03).** These override the recommendations
below wherever they differ; every slice reads this list first.

| # | Answer | Effect on the slices |
|---|---|---|
| 1 | **(a) leave retail** (not the recommendation) | Map 8 phase 2 makes no changes to retail ceilings or walls; VQ-018/022/023/030/031 are allow-listed occlusions. VQ-003 is still Map 8's to fix. |
| 2 | (b) 895 underpaint where the LV route sees it | as recommended |
| 3 | (b) flush edge, invisible barrier, water beyond | as recommended |
| 4 | (a) dark water; north box confirmed (Douglas 2026-10-25) | Gate 0 fills Map 13's `frame_allow` north box. |
| 5 | **(b) fill every void block in view with 895 plates** (not the recommendation) | Map 11 phase 3 plates every black block in view, ~1,600 records. Map 11's exit ceiling rises from 11,000 to **11,700** (hard cap 12,000 unchanged); use 256-unit plates or glob eggs, never 128-unit tiles, to stay under it. |
| 6 | (a) decorative water, 347 clone with solid-floor physics, no `SI_SEA` | as recommended |
| 7 | (a) keep 347:16 navy, fix stripes and shores | as recommended |
| 8 | (a) quest legs + named items | as recommended |
| 9 | (a) leave the Map 39 canal | as recommended |
| 10 | (a) keep screen10's dais black; (a) keep the Map 11 boulders | as recommended |
| 11 | (a) `occlusion_allow` box x 2624..3007, y 5983..6143 | as recommended |

1. **Map 8 retail route occlusions** (VQ-018, 022, 023, 030, 031; gates
   Map 8 phase 2). (a) leave retail; (b) invisible ceiling + backdrop (the
   phase 1 shelf technique) on the LV route corridors' ceilings only
   (VQ-018), walls stay; (c) restyle the route's walls too.
   **Recommend (b).**
2. **Map 8 retail black on retail routes** (VQ-044, 046, 060, 064 and the
   trench; gates Map 8 phase 3). (a) leave as the cave idiom (the retail
   cave is 46% black on average); (b) 895 underpaint where the LV route
   component sees it (m08-15/45/46/47) only; (c) everywhere.
   **Recommend (b).**
3. **Map 10 south/east boundary where the ground is z 0** (VQ-025 and
   VQ-034). (a) keep the drawn 104 rim and recess the walkable edge one
   cell (Avatar still hidden within ~830 of the rim beyond that cell);
   (b) flush edge, invisible barrier, water skirt beyond (the Vale ends at
   water; no occlusion); (c) flush edge and a rock plain at the same z (an
   invisible wall across a plain). **Recommend (b).**
4. **Map 13 valley skirt material and the north box** (VQ-039, VQ-054).
   Material: (a) dark water continuing screen15/16; (b) rock; (c) cloud.
   North edge: confirm the accepted box so rule D excludes it.
   **Recommend (a), and confirm.**
5. **Map 11 black beyond intact rims and between sections** (VQ-035,
   VQ-038; 27 stops). (a) accept as cave idiom, ratchet only, fix the
   reachable black and the three holes; (b) 895 dark-stone plates in
   every void block in view (~1,600 records). **Recommend (a).**
6. **Map 11 Water section water** (plan §6.2; phase 3 water class).
   (a) decorative water: a 347 clone with donor-202 physics through the
   art track, no `SI_SEA`, cannot drown; (b) stay dry and dress it in
   phase 4. **Recommend (a)** — it is the same one-row art-track step as
   894/895 and removes the drowning risk by construction.
7. **Lake water frame on Maps 10 and 13** (VQ-041, VQ-052). (a) keep
   347:16 navy, which the 1994 shots are made of, and fix the stripes and
   shores; (b) 347:0 ripples outside the windows with navy inside (a
   visible seam at the window edge). **Recommend (a).**
8. **Near-wall standard scope.** (a) one drawn course on the near walls
   every quest leg passes plus the backlog's named items, elsewhere
   untouched; (b) every south/east near wall on every map; (c) retail: no
   lowering, allow-list the legs. **Recommend (a).**
9. **Map 39 main-gate canal** (VQ-055, retail). (a) leave; (b) a floor
   under the arch. **Recommend (a).**
10. **Carried from phase 1:** VQ-001 (Map 9 dais black is screen10's own
    pixels: (a) keep the shot, (b) revise screen10's floor and accept −8
    points) and VQ-016 (Map 11 sealing boulders are pinned and keyed by
    `COLPUZZL`/`REAPPLY`: (a) keep, (b) one reviewed slice that changes
    shape, pins and both usecode filters). **Recommend (a) for both in
    this phase.**
11. **Map 18 crack pier.** (a) accept the pier's occlusion in an
    `occlusion_allow` box x 2624..3007, y 5983..6143 (the breach records
    must stay drawn and keyed); (b) patch `TEMPLENT`/`REAPPLY` to also
    destroy 497 q307 so the pier's upper courses can be invisible (usecode
    change, verifier run). **Recommend (a).**

## 7. Summary

**Slices (9):** gate 0 (shared contracts: cover rule, `Cave(near_courses)`,
`shortest_path`, `quest_legs.py`, `RECORD_BUDGET`, `test_visual_quality.py`
+ eight pin files), then one per map:

| Slice | Phase 2 items | Phase 3 items | Key technique |
|---|---|---|---|
| 18 | VQ-019, VQ-024 | VQ-048, VQ-050, VQ-056, VQ-063 | T1 on the crack line and east hall wall (pier excluded), T4/T7 in the sanctum |
| 9 | VQ-026, VQ-029, VQ-032 | VQ-051 (VQ-062 accepted; VQ-001 → D10) | T1 on the hall's south/east and the worked passage's east |
| 11 | VQ-020 | VQ-043, VQ-045, VQ-065; VQ-035/038 → D5 | invisible near flank + verge; T4 tops in screen05/07 |
| 10 | VQ-025, VQ-027, VQ-028, VQ-033 | VQ-034, VQ-036, VQ-041, VQ-042, VQ-057, VQ-061 + 31 cells | T1/T2 per tier, T3 glob skirt (D3), T4 posts, T6 |
| 13 | — | VQ-037, VQ-039, VQ-049, VQ-052, VQ-053, VQ-058 (VQ-054 accepted) | T3 water skirt (D4), T4 crests/posts, T6 |
| 17 | — | VQ-047 + 16 cells | T5 computed cloud sea |
| 39 | VQ-021 | VQ-040, VQ-059 (VQ-055 → D9) | T7 on the tunnel, T3 glob ground beyond the oaks |
| 8 | VQ-018/022/023/030/031 → D1 | VQ-003 (regressed), VQ-004/008 finish, VQ-046 (D2); VQ-044/060/064 → D2 | T7 underpaint, aperture clip |

**Rules:** walkable black 0 outside Map 8's 256 inherited cells; ≥ 50%
Avatar on every quest-leg cell outside sign-off boxes; map-wide
visibility and frame black within the retail class limits (town 7/38/62
and 21%/6%; cave 47/77/91 and 58%/37%) and never above the per-map pins;
raw records under the caps (Map 10: 25,000); shot floors hold; geometry
proved on the built FIXED.

**Decisions needed:** 11 (§6), of which 1, 2 gate Map 8; 3 gates Map 10's
phase 2; 4 gates Map 13's phase 3; 5, 6 gate Map 11's phase 3; 7 gates the
lake work on 10 and 13; 8 is the policy every phase 2 slice applies; 9
Map 39; 10 and 11 can be answered at the merge.

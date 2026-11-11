# Map 10 paint cycles: `426 -> 856` and `426 -> 208` (2026-10-10)

This follows up finding 2 of `docs/playtest-2026-10-10-dialogue.md`: 22,590 `Cycle in paint dependency graph` lines. It also covers finding 4 of `docs/playtest-2026-10-10-mover.md`, the retail case `590 -> 235` on Map 8.

The engine work ran on Xvfb `:90` against an isolated copy of `shared/data/u8-install`. Every artifact hash matches `shared/build/ARTIFACTS.sha256` (FIXED `511902e8…`, TYPEFLAG `6bdb3036…`, U8SHAPES `69fbd861…`, EUSECODE `af5789a6…`). The binary was `scummvm-lv/scummvm` (mtime 2026-10-10 04:01) with `debugflag_enable Object` on. Plates are in `docs/research/2026-10-10-map10-paint-cycles/`.

## Verdicts

| # | Question | Answer |
|---|---|---|
| 1 | What are 426/856/208? | **Shape numbers, not object ids.** `item_sorter.cpp:414-415` prints `si->_shapeNum, d->_shapeNum`. 426 is the zero-depth vine strip, 856 the wood-plank SE wall and 208 the desk/workbench (`DESKNS`) |
| 2 | Where did the cycles happen? | **Not in Thordis's village.** They came from Gunnar's moonshine still at about (21600..21800, 7600..7770), where the Avatar stood at (21899,8911) for log lines 998-23676. The same session logged **0** cycles at (4665,7673) |
| 3 | Why? | **A stale save.** `run-s5-rite-granted.sav` (2026-09-06) carries Map 10's fixed items as they were then. That includes the workbench at its **pre-2026-10-07** spot, (21664,7768), straddling the hut's south wall. `3b3fc14` moved it in the builder, and the shipped `FIXED.DAT` has it at (21536,7904). **62 checkpoints** in `~/lv-checkpoints` carry the old spot |
| 4 | Is it a current-build defect? | **No.** After a hop off Map 10 and back (the map reloads from FIXED.DAT), the same camera logs **0** cycles. An offline scan of the shipped FIXED.DAT finds **no static paint cycle on any LV map** |
| 5 | Is it visible? | **Yes, but what shows is the placement itself.** The desk cuts through the wall's foot, and NPC 109 stands inside the desk with only his head and shoulders showing (plate A3; NPC 108 at the workshop, plate A5). The cycle-break reorder itself changes about 136 px of vine at the desk's leg |
| 6 | Offline scan | Static: **0 cycles** on Maps 9, 10, 11, 13, 17 and 18. Retail-only cycles exist on Maps 8 and 39. Actor-dependent: 4 knots, of which **2 are reachable and confirmed in-engine**: Map 10's test-grounds spire (`66 -> 1`) and Map 13's summit ridge (`3 -> 32`). See §5 |
| 7 | Fix | Nothing to change for 426/856/208 in the shipped map. Re-bank or map-hop the stale checkpoints. Optionally fix the two reachable actor knots (§6) |
| 8 | Map 8 `590 -> 235` | **Same class of mechanism, retail data.** A zero-depth web plane (590 `LARWEBNS`, U8SAVE.000 NONFIXED) passes through a pile of bones (235), and a third retail item closes the loop. It is not ours and not caused by the Lost Vale changes (§7) |

## 1. What the engine does

`ItemSorter::AddItem` (`item_sorter.cpp:194-244`) compares each new item with every item already in the list. For each pair whose screen footprints `overlap()` (`sort_item.h:305`), `SortItem::below()` (`sort_item.cpp:64-238`) decides which one draws first, and the later-drawn item records the other in `_depends`.

`below()` is a sequence of pairwise rules (clear in z, clear in y, clear in x, z tolerance, the y-flat/x-flat 32-unit centre tests, and so on). It is **not transitive**. Three boxes can therefore produce a < b < c < a.

`PaintSortItem` (`item_sorter.cpp:402-423`) paints depth-first:

1. It marks an item `_order = -2`.
2. It walks the item's `_depends`.
3. When a dependency is already on the stack (`-2`), it logs the line and then **`break`s**. The current item paints at once, ahead of every dependency left after the cyclic one in its sorted list. Those dependencies paint later, on top of it.

It happens once per frame, and the line is `debugC(kDebugObject)`. Players never see the log line. The only visible symptom is the paint order.

The message names `si` (the item being painted) and `d` (its dependency, which is already on the stack). So `426 -> 856` means a vine strip met the wall below it while that wall was still mid-paint.

## 2. The items and the mechanism

### 2.1 In-engine identification

These were read from `ObjectManager::findShape` on the loaded `run-s5-rite-granted` (copied to slot 1), Map 10, with the Avatar teleported to (21899,8911,0) and `CameraProcess::moveToAvatar` run (the save loads with a parked camera).

| objId | shape:frame | position | world box (half-open x/y, z) | TYPEFLAG |
|---|---|---|---|---|
| 4529 | 208:0 `DESKNS` | (21664,7768,0) | x(21568,21664] y(7608,7768] z[0,16) | 96x160x16, solid, land |
| 3004 | 856:0 | (21632,7680,0) | x(21504,21632] y(7648,7680] z[0,40) | 128x32x40, solid, land, occl |
| 11832 | 856:0 | (21792,7680,0) | x(21664,21792] y(7648,7680] z[0,40) | same |
| 1133 / 11833 / 1970 | 426:0 | (21600 / 21696 / 21760, 7680, 0) | x 96 wide, **y-flat at 7680**, z[0,16) | 96x0x16, not solid |
| 7164 | 526:4 | (21536,7744,0) | x(21472,21536] y(7680,7744] z[0,16) | rubble 64x64x16 |
| 109 (NPC) | 707:1 | (21632,7744,0) | x(21568,21632] y(7680,7744] z[0,40) | actor 64x64x40 |

The still house is `_PREFAB[HOME_HUT].stamp(still_x, still_y, …, shape_remap=WOOD_WALL_REMAP)` with `still_x, still_y = 21504, 7168` (`build_map_10.py:682-683`). Its south wall is the 856/858 run at y=7680, and the prefab's 426 vine strips lie on that wall's face. The workbench was placed at `+(160,600)`. The builder comment at `build_map_10.py:690-701` records the move to `+(32,736)`, which landed in `3b3fc14` (2026-10-07). The workshop has the same layout: its old workbench at (21664,9816), NPC 108 at (21632,9792) and vines at y=9728.

### 2.2 Why they form a cycle

The desk's box spans y 7608..7768. **The vine plane at y=7680 runs straight through it**, and the desk also pierces wall 3004 (y 7648..7680) and buries NPC 109's whole footprint. The engine's own rules then give three edges that contradict each other:

| edge (drawn first → drawn after) | rule in `below()` | arithmetic |
|---|---|---|
| 426@21600 → 526 | clear in Y (`sort_item.cpp:90`) | 426.y 7680 ≤ 526.yFar 7680 |
| 526 → 208 | clear in X (`:104`) | 526.x 21536 ≤ 208.xLeft 21568 |
| **208 → 426@21600** | y-flat vs non-flat centre (`:117-128`) | Y and X overlap. The z tolerance fails (both are 16 tall). 32-unit centres: 208 is (237+242)/2 = 239, 426 is (240+240)/2 = 240, so the desk counts as "behind" the vine |

So the desk is behind the vine, in front of the rubble, and the rubble is in front of the vine. NPC 109 closes a second loop the same way:

- 426 → 707: clear in Y, 7680 ≤ 7680.
- 707 → 208: the x+y rule at `:217`, 29376 < 29432.

The wall 856@21792 joins the loop through two more edges:

- 208 → 856: clear in X, 21664 ≤ 21664.
- 856 → 426@21696/21760: clear in Y. The vine is on the wall's face, which is the correct order.

That is where the `426 -> 856` messages come from.

The repo's sorter port (`agents/map-populator/src/item_sorter.py`) builds the graph from the old layout. Tarjan's strongly-connected-components algorithm over that graph returns **exactly the seven items above as one component**. The second component is the workshop's seven. Removing NPC 109 alone, or the rubble alone, leaves a cycle. Removing both, or moving the desk, leaves none.

### 2.3 It is not Thordis's village

The dialogue log (`/tmp/claude-1000/vdlg/lv_run.log`) gives the Avatar's position in each `objectInfo 1` line. Grouping the cycle lines by the position read before them:

- Every one of the 22,590 falls while the Avatar is at **(21899,8911)** (lines 2061-12111, and up to 23676). It is the same 1.5:1 mix of 13,554 `426 -> 856` to 9,036 `426 -> 208`.
- From line 23685 the Avatar is at (19808,6892) and then (4665,7673), and there are **0** cycle lines.

The report's "Where" bullet attached the window to the wrong teleport. The Avatar stood beside NPC 113 (Hrodny's talks, D1b) at the Gunnar still. My re-run gave **840 + 560 in 5 s** at the same spot, the same 1.5:1 ratio.

### 2.4 Stale save, not the shipped map

- **Save contents.** The ScummVM save's `OBJECTS` section holds every item of the current map, fixed ones included (`ext 0xb`, where 0xb = 0x1|0x2|0x8 and 0x1 is `EXT_FIXED`). So loading a Map 10 save restores Map 10 as it was on the day of the save, which is the `traps.md` "old save does not see new fixed items" rule.
- **Checkpoints affected.** A byte scan of `~/lv-checkpoints/*.sav` (`Item::saveData` layout, `item.cpp:2656-2667`) finds an old-spot workbench, at (21664,7768) and/or (21664,9816), in **62 checkpoints** and a new-spot one in none. The 62 are the `cp5b`–`cp33` saves taken on Map 10 (dated 2026-08-17 to 09-05), `run-s5`, `s7`–`s12`, `s15`, `s16` and `s18` (both s18 saves), the four `bag-q1-*map10*` saves (2026-10-03/04) and `slot1-before-2026-09-03`.
- **Only these two knots.** Running the component scan on the fixed items parsed out of `run-s5-rite-granted`, `run-s9-mark-given`, `cp10-passage-stone`, `cp33-bag-of-reagents` and `bag-q1-poll600-map10-2026-10-04` returns exactly the still and workshop knots and nothing else.
- **Control.** I teleported to Map 9 and back, which loads Map 10 from FIXED.DAT. At the same camera, `findShape 208` then lists (21536,7904) and (21536,9952), and 5 s gives **0** cycle lines. `debugflag_list` confirmed `Object (enabled)` at that moment. The workshop camera (21760,10010) also gave **0** fresh, and **301 `426 -> 208` + 301 `426 -> 426`** after `loadGame 1` restored the stale map.

## 3. Visible effect

Plates are in `docs/research/2026-10-10-map10-paint-cycles/`. The camera is on the Avatar at (21760,7960,0) for A1-A4 and (21760,10010,0) for A5.

- **A1 / A2.** Full frames, stale (run-s5) and fresh (after the map hop).
- **A3.** A 3x crop of A1 | A2.
  - **Stale:** the desk straddles the hut's south wall, drawn across the wall's foot. NPC 109 stands *inside* the desk, and the desk paints over his body below the shoulders. That follows from `707 → 208` above, which is correct by the sorter's rules: he really is inside the desk.
  - **Fresh:** the desk stands clear on open ground, and NPC 109 is visible full length against the wall.
- **A4.** The stale view with `GameMapGump::toggleFootpads`. The desk's box runs through the wall's box.
- **A5.** The workshop, stale | fresh: the same picture with NPC 108.

**What the cycle itself adds.** A pixel diff of A1 against A2 inside the station crop (200x140) changes 3,191 px. Almost all of them are the two desk silhouettes. The only other cluster is 136 px at the desk's right leg, which is vine pixels at the wall's foot.

The port's paint simulation agrees. Across 40 shuffled insertion orders, the logged pair moves around, and so do the pixels painted out of order:

- vine segments overdrawn by the wall or the desk, up to about 190 px per segment;
- or the vine painted over NPC 109, 139 px.

Each of these is a small strip at the wall's foot. A player sees the misplaced desk and the half-buried NPC. The reorder caused by the cycle is cosmetic noise on top. Elsewhere in the frame, A1 and A2 also differ in the east rim (the save predates the 2026-09-15 rim) and in walking NPCs.

## 4. Offline scan method

All runs used the shipped `shared/build/FIXED.DAT`, with globs expanded (`map_preview.expand_globs`), NPCs at their FIXED starts and contained items (x ≤ 2) dropped. Every rule comes from the port in `item_sorter.py`: `overlap`, `below`, `list_less` and the footpad/flip and screen-rect construction. The scratch drivers (`/tmp/claude-1000/vpaint/`) are not in the repo.

1. **Static graph per map.** Every item goes into a 64-px screen-space bucket by its frame rect. Each overlapping pair gets the engine's edge, with the later item in chunk order as `si`. Tarjan's algorithm then finds every strongly connected component.
   - `overlap` and `below` are translation-invariant: the camera only offsets screen coordinates after the per-coordinate integer division.
   - Clipping and occlusion only *remove* items or edges.
   - So zero components means no frame can cycle on static content.
   - Pairs where `below(a,b) == below(b,a)` (order-dependent) were listed separately. On every map they are exact duplicate items, for example four copies of `425:11` at (13311,4479,0) on Map 10, and duplicates cannot produce a visible reorder.
2. **Actor positions.** On a 64-unit lattice, every point gets standing levels from the tops of non-roof `SI_LAND` items under it. Points where a 64x64x40 actor box overlaps a solid are skipped, using `Box::overlaps` with half-open boxes.
   - For each remaining point, the Avatar (1:0) adds edges to the overlapping items.
   - A cycle through the actor exists when a dependency path runs from something drawn before it to something drawn after it, kept within 360 px.
   - Each hit was re-checked with a full per-camera port run that applies GameMapGump's roof cut.
   - Reachability comes from `exact_reach.ExactReach.flood`, seeded from `test_route_reach.py`'s arrival points (step 16).
3. **Zero-depth planes.** Every non-solid zero-depth item that has height (426/427, 328/329, …) got actor boxes placed straddling it.
4. **Interpenetration census.** This counts every pair of distinct boxes that overlap per `Box::overlaps`.

**A port limitation found on the way.** `shape_viewer.parse_shape_frames` returns `[]` for any shape with more than 500 frames: shapes **1** (1,550), **137**, **191** and **315**. `ItemSorter._make` then returns `None`, so `item_sorter.py` silently drops the Avatar from any graph it is given. I loaded shape 1's frames directly for steps 2-3. `test_paint_cycles.py` adds no Avatar, so it is unaffected today. Anyone who adds an Avatar there would get a false "no cycle".

## 5. Scan results

### 5.1 Static (shipped FIXED.DAT)

| map | items | overlapping pairs checked | cycles | notes |
|---|---|---|---|---|
| 9 | 1,017 | 11,694 | **0** | |
| 10 | 34,668 | 356,415 | **0** | 10 order-dependent pairs, all exact duplicates of 425 (5 stacks) |
| 11 | 17,848 | 231,291 | **0** | 42 duplicate pairs (26, 32) |
| 13 | 6,273 | 78,186 | **0** | 8 duplicate pairs (242) |
| 17 | 5,117 | 60,969 | **0** | |
| 18 | 2,796 | 33,873 | **0** | |
| 8 (FIXED, with LV additions) | 26,816 | 374,637 | 1, **retail** | 466:1@(11743,22431,48), 466:1@(11839,22303,48), 65:3@(11679,22303,48). It is present in the pristine retail FIXED.DAT too |
| 8 (+ U8SAVE.000 NONFIXED) | | | +1, **retail** | the bone cave (§7) |
| 39 | 28,594 | 542,879 | 1, **retail** | 199:0@(11999,17823,88), 56:1@(11615,17631,88), 57:3@(11743,17567,112). It is present in pristine retail too |

As a check, the same scan run on the stale layout (both old workbenches swapped back in) finds **exactly** the still knot and the workshop knot.

Plane straddling: Map 10's 60 vine planes (426/427) all lie on wall faces, so **no actor position straddles them**. On Maps 11 and 17, 24 straddling positions each produced 0 cycles. Maps 9, 13 and 18 have none.

The interpenetration census shows that overlap alone does not make a cycle: 9 / 82 / 573 / 30 / 92 / 31 overlapping box pairs on Maps 9 / 10 / 11 / 13 / 17 / 18. A cycle also needs a third item that each of the two is ordered against by a *different* rule.

### 5.2 Actor-dependent knots (the Avatar standing at one spot closes a loop)

| map | Avatar at | the other items | mechanism | reachable | in-engine |
|---|---|---|---|---|---|
| **10** | (12352,29632,64) | 66:0@(12384,29760,64) (rock spire), 32:1@(12288,29696,96) | The spire's box x(12256,12384] **pierces the rim wall column** x(12256,12288] (`32` at z 48 and 96, two y-cells). The spire is placed by `build_test_grounds` (`build_map_10.py:1145`) | **yes** | **`66 -> 1`, 225 lines in 4 s** (plate B1) |
| **13** | x=3008 (also 2976), y 448..896, z 120 | 3:0 summit tiles @(3072, 512..896, 120); 32 @(3072, 639..1023, 96) | `build_summit`'s z=120 floor tiles (`build_map_13.py:542-547`) **pass through `build_harpie_zone`'s cliff face** at x(3040,3072], y 511..1023, which stands 0..192 tall: four courses, the top two above the floor | **yes** | **`3 -> 32`, 212-226 lines in 4 s** at both x (plate B2) |
| 11 | (8128, 22592..23552, 104) | 125 @(8192,…,96) slab, 10:1 @(8192,…,80) | The slab z[96,104) overlaps the wall z[80,120) | no | not run |
| 18 | (5056,6272,16) | 10:1@(5119,6272,0), 15:1@(5120,6175,40) | wall/floor corner at a raised standing level | no | not run |

**What the two reachable knots look like on screen is not established.**

- **Map 13 (B2).** The Avatar is hidden there anyway, because the 192-tall ridge stands in front of him. That is correct occlusion: the wall face covers screen y 256..464 and he spans 276..316. The port predicts that the z 96 course paints over the floor tile at (3072,512) (516 px), but I could not separate that from the correct image in a plate.
- **Map 10 (B1).** The port predicts a 50 px reorder between the spire and the Avatar. I did not crop it.

## 6. Proposed fix (not applied)

1. **The reported 426/856/208 cycles: no map change.** The shipped FIXED.DAT already has the fix (`3b3fc14`). What keeps them alive is test state:
   - **Re-bank the Map 10 checkpoints.** For each of the 62, load it, hop to another map and back (or walk out and in), then save. That brings the save's Map 10 to the shipped layout, the rim included. Or
   - **have the harness hop Map 10 → 9 → 10 after every Map 10 load** before it counts log lines.

   Either way, a `Cycle … 426 -> 208` or `426 -> 856` line after loading a pre-10-07 save is a known stale-save artifact, not a regression. It belongs as a line in `.claude/skills/playtest/traps.md` beside "An old save does not see new fixed items". The dialogue report's finding 2 "Where" should say Gunnar still (21899,8911), not Thordis's village.
2. **Map 10 test grounds spire (optional, reachable).**
   - **Change:** move `(12384, 29760, SHAPE_ROCK_SPIRE_CLUSTER, 0)` to **x=12416** (`build_map_10.py:1145`).
   - **Effect:** its box becomes x(12288,12416], which only *touches* the rim column's x ≤ 12288 under half-open boxes. That removes all four interpenetrations with `32`.
   - **Checked offline:** the local actor scan then finds 0 knots (2,065 positions), and the same holds at x=12448.
   - **Constraint still met:** the docstring requires dressing "> 128 units off every scene coordinate". The nearest scene x is 12639, which leaves 223.
3. **Map 13 summit ridge (optional, reachable).**
   - **Change:** stop `build_harpie_zone`'s x=3072 face below the summit floor where `build_summit` paves over it (y ≤ 1023). That means dropping its z=96 and z=144 courses there, 8 items.
   - **Checked offline:** with those removed, the local actor scan finds 0 knots (1,454 positions).
   - **Why [INFERENCE]:** the 72-unit ridge that now stands up through the summit floor looks unintended; the floor slices it at z=120.
   - **Risk:** this changes the summit's walkable geometry, so `test_route_reach.py` (including `gate_reach`) and `test_map_edges.py` must re-pass. A smaller alternative is to leave it. The only cost is debug-log noise, with no established visible artifact.
4. **Maps 11 and 18 knots.** No action: the positions are unreachable.
5. **Tooling (proposal).** Let `item_sorter.py` load shapes with more than 500 frames, so the Avatar is never silently dropped. Then add the static component scan (§4 step 1) to `test_paint_cycles.py`. It covers every LV map in about 2 s per map and would catch the next desk-through-a-wall before a playtest does.

## 7. Map 8 `590 -> 235`, the bone cave: same class of mechanism

The port, run over Map 8 = retail FIXED + `build_map_08` additions + U8SAVE.000 NONFIXED with cameras across (20260..20500, 3260..3560), finds one component in every camera (30/30). In-engine at (20430,3250,0) it logs **`590 -> 235`, 205 lines in 4 s**. `findShape` names the same items:

| objId | item | box | origin |
|---|---|---|---|
| 29643 | 590:0 `LARWEBNS` @(20064,3080,5) | x(19968,20064] **y-flat at 3080**, z[5,45), translucent | U8SAVE.000 NONFIXED (retail) |
| 29644 | 235:1 `BONES` @(20127,3199,0) | x(20031,20127] y(3071,3199] z[0,8) | U8SAVE.000 NONFIXED (retail) |
| — | 65:21 @(20031,3167,0) | x(19967,20031] y(3103,3167] z[0,40), solid | retail FIXED (pristine; not in `build_map_08_additions`) |

The edges:

- **235 → 590** by the z-tolerance rule (`:111`): bones zTop−8 = 0 ≤ web z 5, and bones z 0 < web zTop−8 = 37.
- **590 → 65** by clear in Y: 3080 ≤ 3103.
- **65 → 235** by clear in X: 20031 ≤ 20031.

It is **the same class as Map 10's**: a zero-depth plane (here a web, there the vine) runs through a box (the bones 9 units behind the plane and 119 in front, there the desk), and a third item ordered by a different rule closes the loop. The differences:

- It is **Origin's data.** Both the web and the bones are new-game NONFIXED, which a FIXED builder cannot move, and the third item is pristine retail FIXED.
- The LV additions do not touch it.
- It reproduces on the unfixed control too (the mover report).

Plates C1/C2 (with footpads) show no visible reorder I could pick out: the web is translucent over grey bones. **No action proposed.** If it ever mattered, the only lever is a `NONFIXED` edit to the new-game save, which this project does not do.

## Disk changes

- **Report and plates:** this report and `docs/research/2026-10-10-map10-paint-cycles/` (9 PNGs).
- **Scratch:** `/tmp/claude-1000/vpaint/` holds the game copy, saves (slot 1 = `run-s5-rite-granted`), the log `lv_run.log`, the driver and raw shots.
- **Engine processes:** the ScummVM and Xvfb `:90` processes I started are stopped.
- **Untouched:** no other repo file, checkpoint or build artifact was changed.

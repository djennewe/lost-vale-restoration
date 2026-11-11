# Playtest 2026-10-10: gateway arrival corridors and paint knots (verifier)

This verifies `d665e3c` (arrival corridors: Map 10 triggers 213/204 moved, Map 8 trigger 201's y and pads 200/213 moved, Map 9 pad 201 moved) and `b66db3c` (Map 10 test-grounds spire, Map 13 summit ridge), as merged in `4e1eb70`.

- **Build under test.** `/tmp/claude-1000/vgate/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Every hash matches `shared/build/ARTIFACTS.sha256`: FIXED `29abf906…` (top level and `STATIC/`), EUSECODE `0e39b0b7…`, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…` and ANIM `77e9705d…`. The engine log reads `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1523614 bytes`.
- **Binary.** `scummvm-lv/scummvm`, mtime 06:37, which is newer than fork `8af4f74e` (03:35). The fork patch equals the fork diff (`PATCH_EQUAL`).
- **Harness.**
  - Xvfb `:93` (1280x800), with the window at (480,300).
  - My own `scummvm.ini` sets `frameLimit=true` and `usehighres=false`, with mute on and `SDL_AUDIODRIVER=dummy`.
  - Saves are private, and slot 1 is `run-s4-columns-done.sav` (md5 `cc6ed3a1…`, unchanged at the end). It is past step 3, so the double doors are open. It loads on Map 11.
  - The driver is the `vdlg` `drv.py`, re-pointed to this display.
- **Method.**
  - **Source triggers were entered on foot.** Each hold began outside the trigger's hatch box. The harness polled the log for `Loading Fixed items in map <dest>`, kept the input held for N more seconds, released, waited 2.5 s and then read `objectInfo 1`.
  - **Mouse run** is the right button at a 240 px offset (180 px for straight up; see harness anomaly 3). **Mouse walk** is a 110 px offset.
  - **Keyboard** is `Up` (forward, at walk speed) after a 0.25 s mouse burst to set the facing. **Keyboard run** is `Shift+Up`.
  - "C" means continuous: held 15 s after arrival.
- **Debug teleports** were used only to position for G3 and for the closed-door and wedge controls. None of them was a source of an egg-triggered claim. Each one ended outside every teleporter box, so `justTeleported` was cleared before the walk-in.
- Plates are in `docs/playtest-2026-10-10-gateways/`.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| G1 | No bounce on the 5 fixed pairs, held 2 s / 4 s / continuously, mouse run and keyboard | **FAIL**. 3 of 5 pairs hold, and 2 do not. **10→8 via 213 fails 9 of 9 northbound holds.** Every mouse run, mouse walk and keyboard walk, including a mouse run released at the arrival line, carries the Avatar through the open double doors into trigger 201 and on to Map 9. **8→9 via 201 fails under a held keyboard run.** Shift+Up held about 7.5 s wall-follows Map 9's hall into trigger 203 and on to Map 11 (2 of 2). |
| G1 · 205 (11→10) | | **PASS**, 7 of 7 |
| G1 · 212 (8→10) | | **PASS**, 9 of 9 (N and E) |
| G1 · 213 (10→8) | | **FAIL**, 9 of 9 northbound holds chain to Map 9. The NW heading and a doors-closed control stay on Map 8 |
| G1 · 200 (9→8) | | **PASS**, 7 of 7 |
| G1 · 201 (8→9) | | **FAIL (narrow)**. 8 of 8 mouse holds and keyboard-walk holds pass. Keyboard run held 8 s → Map 11, 2 of 2 |
| G2 | The moved return triggers are findable and work on purpose | **PASS**. The 213 and 204 slabs are both visible from the court (`G2-213-approach`). 204 → Map 11 worked on 9 walk-ins, 213 → Map 8 on 14 of 14, 201 → Map 9 on more than 20 and 200 → Map 8 on more than 20. **Negative controls:** the old 204 spot does not fire; every 212 run crossed the old 213 spot without firing; holding north against the **closed** doors at x 20300/20390 stops at y 3140 with no teleport. But see finding 3 |
| G3 | Paint knots gone, scene right, summit walkable, 208/209 work | **PASS**. **0** `Cycle in paint` lines at the Map 10 spire (14 positions) and the Map 13 summit (10 positions). **Control:** the same binary and save with the old FIXED `511902e8` logs **228 `66 -> 1`** and **205 `3 -> 32`** lines in 4 s at the same spots. **Positive control in-session:** 191 retail `235 -> 65` lines in 4 s on Map 8. The plates draw right. `test_route_reach` gives 92/0. Walked: ledge → harpie zone → summit → west strip, and 209 → Map 17 → 208 → Map 13 → down into the harpie zone. Finding 4 (the summit's north edge is a lethal drop) is outside this change |
| L | Log hygiene | **PASS** for this change. 0 `stuck in process loop`, `Unhandled intrinsic`, Segmentation, Assertion, `Trying to access segment`, `popToContainer`, `stale gravity`, `FIXME` and `Non-existent process`. The only `Cycle in paint` pairs are the retail Map 8 bone cave: 21,936 `590 -> 235` and 5,371 `235 -> 65`. There were 94 stock `Invalid item N passed to area search` lines (shape 804, event 5) over 114 map loads |
| — | `tools/run_all_tests.sh` | **PASS**: `OVERALL: PASS — 44/44` (204 s) |
| — | Patch equals fork diff | **PASS** (`PATCH_EQUAL`) |
| — | `build_artifacts.sh`, `install_lv.sh` | **Not run**, on instruction. The hash match above stands in for them |

## G1: holds through the five pairs, FAIL

Arrival points are the pads. A mouse-walk hold released at the arrival line stopped exactly on Map 8 pad 213 at (20192,3300,0). Map 11 pad 204 was read at (8448,23040,0). Map 9 pad 201 was read at (13696,14208,0) after a run released at arrival. Every other arrival keeps moving for the log-poll latency. The calibration run on 205 released at arrival and still ended 320 units past the pad.

### 205: Map 11 → Map 10 pad (12800,2560), PASS

The start was (8640,22650), in at the pad room's north doorway, heading S. The pad room was re-entered each time by walking 204 back from the court.

| Hold | Start → arrival (s) | Ends at |
|---|---|---|
| mouse run 2 s | 1.21 | (12800,4200,0) |
| mouse run 4 s | 1.36 | (12800,5760,0) |
| mouse run C | 1.31 | (12648,12152,0) |
| key 2 s | 0.66 | (12800,3488,0) |
| key 4 s | 0.66 | (12800,4416,0) |
| key C | 0.56 | (11200,7072,0) |
| Shift+Up 6 s | 0.51 | (12800,7064,0) |

### 212: Map 8 → Map 10 pad (13824,2560), PASS

The start was (20600,3640), heading N (the route's heading). The E run started from (20288,3316).

| Hold | Ends at |
|---|---|
| mouse run 2 s | (13824,1096,0) |
| mouse run 4 s / C | (13764,1092,0) / (13764,1092,0) |
| key 2 s / 4 s / C | (13824,1760,0) / (13764,1100,0) / **(9564,1100,0)**: it slid 4,200 W along the north wall, with no trigger on the way |
| Shift+Up C | (4836,1092,0), 9,000 W along the same wall |
| mouse run E 4 s | (17192,2560,0) |

**Every N run crossed the old 213 spot (13824,2048) without a teleport.**

### 213: Map 10 → Map 8 pad (20192,3300), FAIL

The start was the court at (12900,2420), heading N. That is the route heading, and it is due north from pad 205.

| Hold | Loads | Ends at |
|---|---|---|
| mouse run 2 s (twice) | 8, **9** | Map 9 (13820,13380) / (13816,13384) |
| mouse run 4 s | 8, **9** | Map 9 (13816,13384) |
| mouse run C | 8, **9** | Map 9 (13820,13380) |
| **mouse run released at the arrival line** | 8, **9** | Map 9 (13696,14208), pad 201 itself |
| mouse walk 2 s | 8, **9** | Map 9 (13696,13808) |
| key 2 s / 4 s / C | 8, **9** | Map 9 (14152,13752) / (14712,13296) / (13028,13380) |
| mouse walk released at arrival | 8 | Map 8 (20192,3300,0), the pad |
| key released at arrival | 8 | Map 8 (20264,3228,8): it already moved **+72/−72, NE** |
| mouse run **NW** 2 s (twice) | 8 | Map 8 (20140,3280,0), **wedged** (finding 2) |
| mouse run 4 s, **doors closed** (control) | 8 | Map 8 (20312,3148,0): it slid NE and stopped at the closed leaves |

**Plates.**
- `G1-213-run2b-f00…f03`. f00 is the stale last Map 10 frame (harness anomaly 6). f01-f03 are Map 9.
- `G1-213-map8-pad-area` shows the doorway beside the pad.
- `G1-213-run4-doors-closed-view`.

**Cause, high confidence.**
- **The engine.** `U8AvatarMoverProcess::step` (`u8_avatar_mover_process.cpp:665-697`) retries a refused step at ±45° (`Direction_OneRight`, then `OneLeft`) before it gives up. Mouse and keyboard both route through it (lines 556, 585, 602).
- **The test.** `test_route_reach.arrival_corridors` walks straight lines and ends a line at the first refusal. That is where its `N: stops 104` comes from: the line meets the west jamb pillar.
- **What the engine does instead.** Blocked north, it steps NE, past the pillar into the open doorway. Trigger 201's box covers the door line (y < 3135), so it fires.
- **Pad 200 (20160,3420) is the same geometry 32 units west, and it holds.** Its north line meets the pillar where NE is refused too, and it stops at (20156,3140) or (20100,3160) in all 7 runs.
- **The key-tap row is the slide caught in the act.** The Avatar already stood 72 units NE of the pad.
- **With the doors closed** the slide ends on the leaves, which is why the pre-step-3 state passes. After step 3, every northbound return from the Vale is affected.

### 200: Map 9 → Map 8 pad (20160,3420), PASS

The start was (14336,12980), the throat heading N.

| Hold | Ends at |
|---|---|
| mouse run 2 s / 4 s / C | (20156,3140,8) / (20156,3148,8) / (20156,3148,8) |
| key 2 s / 4 s / C | (20100,3160,8) each |
| Shift+Up 8 s | (20156,3140,8) |

He stops in the niche west of the west jamb. That is also the negative control for 201's y change: y 3140 and 3160 are outside the box's `pta.y < 3135`, and 15 s holds there never fired.

### 201: Map 8 → Map 9 pad (13696,14208), FAIL (narrow)

The start was (20344..20408, 3260..3296), heading N through the open doors.

| Hold | Loads | Ends at |
|---|---|---|
| mouse run 2 s / 4 s / C | 9 | (13820,13380) / (13820,13380) / (13816,13384): the hall's north wall |
| key 2 s / 4 s / C | 9 | (13696,13408) / (13696,13376) / (13696,13376) |
| mouse run NE 4 s / C (from pad 200) | 9 | (14796,12932) / **(14812,12708)**. The second is **28 units** east of trigger 200's box edge (`pta.x − 64 < 14720`) and inside its y range |
| **Shift+Up 8 s (twice)** | 9, **11** | Map 11 (9728,2664) / (9728,2688) |

**The keyboard-run chain.**
- `G1-201-shift8b-contact` is a frame every 0.7 s. The Avatar runs the hall's walls, turns south, and crosses trigger 203 between 7.25 s and 7.92 s after arriving on Map 9.
- A refused step that succeeds at ±45° also turns him (`checkTurn(stepdir)`, line 725). Keyboard "forward" then follows the new facing, so a held keyboard run wall-follows.
- Keyboard walk stopped at the north wall instead (3 of 3).
- This is a chain-through, not a bounce-back. The old pad sat in the throat; the new pad puts the arrival in the hall that leads to 203.

## G2: the moved return triggers, PASS

- **Map 10 213, NW court corner.** The dark slab shows in `G2-213-approach` and `G1-205-cal-view`. Walked in from the court 14 times; each time it fired to Map 8.
- **Map 10 204, west of the court.** Its slab is visible from the court in the same plate. The Avatar walked off the court W/NW into it 9 times, always to Map 11 pad 204 (8448,23040): 8 deliberate returns between the 205 tests, plus one accidental crossing.
- **Map 8 201, the double doors.** With the doors open (run-s4), walked N through them more than 20 times, always to Map 9. Leaves: closed = shape 342 `TDOOR_EW` (20351,3071), open = 340 `TDOOR_NS` (20255/20479,3071). I closed and reopened them with double-clicks during the session; the save on disk was not touched.
- **Map 9 200.** Walked N up the throat more than 20 times, always to Map 8.

**Negative controls.**
- **The old 204 spot.** The Avatar stood at (13564,1796) and walked NW to (13520,1752): no load (`G2-old204-spot`, taken with footpads on).
- **The old 213 spot.** Crossed by all 9 northbound 212 runs.
- **Closed doors.** A 3 s N hold at x 20300 and at x 20390 stopped at (20294,3140) and (20390,3140), with no load (`G2-201-closed-doors-hold`).
  - The same hold at x 20450 went to **Map 10** (finding 3).

## G3: paint knots, PASS

Each count is a fresh `since()` window with the console closed and `debugflag_enable Object` confirmed by its reply.

| Spot | Shipped `29abf906` | Old FIXED `511902e8` (control, same binary/save) |
|---|---|---|
| Map 10 (12383,29631,64) | **0** in 5 s. Also 0 at 13 positions around it, (12379..12655, 29423..29631) | **228 `66 -> 1` in 4 s** |
| Map 13 (3008,640,120) | **0** in 4 s. Also 0 at (2856..3008, 456..876), 9 positions | **205 `3 -> 32` in 4 s** |
| Map 8 bone cave, positive control | **191 `235 -> 65` in 4 s** (retail, research §7) | — |

**The scene draws right.**
- **`G3-map13-summit-old-vs-new`.** The control shows the ridge across the summit with the Avatar hidden behind it, as in research plate B2. The shipped build shows a continuous floor with the Avatar standing at the knot spot.
- **`G3-map10-spire-old-vs-new`.** Both are clean; the spire sits about 8 px further right.

**Summit route.**
- **Offline.**
  - `test_route_reach.py`: 92/0, including "the summit is walkable from the Lost Vale arrival pad" and "TRIGGER 209 to Cloud City is reachable".
  - `test_paint_cycles.py`: 36/0. `test_map_edges.py`: all 6 contained.
  - An `ExactReach` flood from pad 208 and the ledge, old FIXED against new (`/tmp/claude-1000/vgate/py/summit_diff.py`), gains **624 positions, all at z=120, x 3047..3135, y 519..927**: the strip where the ridge stood. It loses **0**.
- **In-engine.**
  - A positioning teleport put the Avatar on the narrow ledge (4096,2560,104).
  - He walked N through the harpie zone to (4096,792,120) and W across the summit to x 2856.
  - He walked N at x 4096 into 209, which went to Map 17. He arrived at pad 209 and walked on to (5376,10736) (`G3-209-arrival-map17`).
  - He walked S into 208, which went to Map 13 pad 208. He walked on S 2 s down to (4096,1440,116) in the harpie zone (`G3-208-arrival-map13`).
- **Not walked:** the lower climb from pad 207 to the ledge. `b66db3c` does not touch it.

## Findings outside the brief

1. **`arrival_corridors` does not model the engine's ±45° slide or keyboard wall-following.** That is the root cause of both G1 failures.
   - **The slide.** The test's "stops N" is where the engine *tries the diagonal*. A line that stops on a corner is not a stop.
   - **Wall-following.** A held keyboard run turns at each slide and keeps going, so "clear 2880 / stops 824" does not bound where a held key ends.
   - **Fix direction.** Model `step()`'s alt-direction retry, at least for the mouse heading. That would have flagged pad 213 (x 20192) and passed pad 200 (x 20160), matching what the engine did.
2. **Wedge at Map 8 (20140,3280,0) after a NW-heading arrival from 213.** This reproduced 2 of 2.
   - **What happens.** He arrives at the pad, slides there at z=0, and then refuses all 8 mouse directions (1.5 s each, console verified closed) and keyboard Up and Down.
   - **The way out.** Up+SPACE (jump) frees him, landing at (19960,3452,8) and at (20540,3680,0).
   - **The surroundings** are retail bone piles and mushrooms (`F-wedge-20140-3280-zoom`, with footpads). The neighbouring floor reads z=8 and z=16.
   - **Likely cause [INFERENCE].** The pad's move to (20192,3300) puts a NW arrival into this pocket.
3. **Trigger 212's box reaches the double doors' east approach.**
   - **What happens.** Pushing N against the doors from x 20450 (closed) or x 20464 (open) slides NE across x 20484 into 212's box, which sends the Avatar to Map 10 instead of through the doors (2 of 2).
   - **Not this change.** 212 did not move [INFERENCE: placement unchanged in `d665e3c`]. But a player aiming at the east leaf is sent to the Vale.
4. **Map 13's summit has no north edge, and walking off it kills the Avatar.**
   - **What happened.** A walk N from (3404,692,120), west of 209's box (x 3680..4576), left the plateau. He fell to **(3404,−164,0) and died** (`hp: 0`, flags 1000; `F-map13-north-edge-fall` shows the death book).
   - **Why.** Falls of 104 or more are lethal (`gravity_process.cpp:322-331`).
   - **Why the tests miss it.** `test_map_edges.py --maps 13` prints `margin 0 on north: a leak there cannot show`. `ExactReach` drops items at y < 64.
   - **Not this change [INFERENCE].** It predates `b66db3c`, whose removed courses are at x 3072.
5. **Thin margin on 201's NE arrival.** A 15 s NE run stopped 28 units east of trigger 200's box, inside its y range. It held, but a body width is 64.
6. **Untested hypothesis.** The same keyboard wall-follow may carry other long-hall arrivals onward, for example 202 into Map 9's hall towards 200, or 203. Only the five pairs in the brief were run.

## Harness anomalies

1. **Starting Xvfb.** `( Xvfb … & )` from the tool shell died with the call. A `setsid nohup` script (`xv.sh`) worked.
2. **Discarded runs.**
   - An interrupted cell left the console open and the right button down. The first 205 calibration ran paused, and I discarded it.
   - My `back201()` also walked "to Map 8 coordinates" while on Map 10 after an accidental 212 crossing. That invalidated five 201 holds, which I discarded and re-ran.
   - The re-runs are what the table shows.
3. **Straight-up mouse runs.** A 240 px upward offset puts the cursor above the 400 px window, so a straight-up mouse run does nothing. Use 180 px, which is still above the run threshold (`mouse.cpp:166-172`).
4. **`con()` double-toggles.** It retries a reply-less command, so `GameMapGump::toggleFootpads` toggled twice. I used a single chord+type for it instead.
5. **Parked camera.** run-s4 predates `f9a9aba`, so the camera parked after every debug teleport. `CameraProcess::moveToAvatar` before each plate fixed it.
6. **Stale pixels.**
   - With `usehighres=false` the void keeps stale pixels: a Map 11 chest shows north of the Map 13 summit in the new half of `G3-map13-summit-old-vs-new`.
   - The first plate after a map load is the old map (`G1-213-run2b-f00`).

## Disk changes

- **Repo:** this report, plus `docs/playtest-2026-10-10-gateways/` (85 PNGs). `run_all_tests.sh` and the three map tests ran read-only apart from `__pycache__`.
- **Scratch** in `/tmp/claude-1000/vgate/`:
  - `game/` (shipped bytes) and `game-ctl/` (FIXED `511902e8`, from `vpaint`);
  - `scummvm.ini`, `run.sh`, `run-ctl.sh`, `go.sh` and `xv.sh`;
  - `saves/ultima8.001` (run-s4, md5 unchanged), `lv_run.log` (43,420 lines) and `lv_ctl.log`;
  - `py/drv.py`, `py/summit_diff.py` and `sp/`.
- **Stopped:** my ScummVM instances and Xvfb `:93`.
- **Not touched:** source, builders, maps, the fork, `shared/`, `TODO.md`, `HANDOFF.md` and `~/lv-checkpoints` (read only; nothing banked).

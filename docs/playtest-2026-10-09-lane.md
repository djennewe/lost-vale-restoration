# Map 39 walked lane to the Lord British egg: in-engine verification (2026-10-09)

**Build under test.** `main` at `f3d83af`, plus the uncommitted `ARTIFACTS.sha256` and `build_scummvm.sh` changes. The change under test is `7e9308c` (wt/lane). The fork is `4ccd3fe7`.
- **Log line.** `usecode/eusecode.flx: 2619303567614e4576432b19b0797332, 1525855 bytes`.
- **Game copy.** `/tmp/claude-1000/vlane/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Its sha256 values match `shared/build/ARTIFACTS.sha256`:
  - EUSECODE `760d631e592d…`
  - U8SHAPES `69fbd86123e8…`
  - TYPEFLAG `6bdb303654a5…`
  - ANIM `77e9705da254…`
  - FIXED `9fbe86da9083…`, in both places.
- **Harness.**
  - Xvfb `:88` at 1280x800, with the window at (480,300).
  - My own `scummvm.ini` (`usehighres=true`, `frameLimit=false`) and save directory.
  - The `run1009` `drv.py`/`h.py`, re-pointed to `:88` and `vlane`, with the mouse-walk reference at (320,214).
- **Plates.** They are in `docs/playtest-2026-10-09-lane/`.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| L1 | From a world fresh to Map 39, arrive at the east-gate pad on foot through Map 40's gate, then walk the route with cheats off until the LB egg hatches | **PASS** |
| L2 | Step 1 fires on its own: lbStarted 0→1, the scene plays, lbDone 1 | **PASS** |
| L3a | The tunnel is passable, and the Avatar is hidden inside it | **PASS** |
| L3b | Both openings show a lintel | **PARTIAL**. The south opening shows one (plate). The north opening faces −y, which U8's fixed camera never shows. The lintel items are in the map data, but I could not see them |
| L3c | The moved rock looks right | **PASS** |
| L3d | Negative controls at the tunnel walls, y≈19800: the Avatar neither climbs out nor drops into the hollow | **FAIL** for the keyboard jump (UP+SPACE). East wall: he goes through the wall to z 0 in the hollow, then on under the field. West wall: he wedges mid-air inside the wall and can no longer move. **The retail niche's own side walls do exactly the same (C2, C3)**, so this is pre-existing engine/retail behaviour, not something the lane's pieces introduced. Stepping into the walls and mouse jumps were refused, and he never climbed out |
| L3e | No `Cycle in paint` near the tunnel | **PASS** during play: 0 lines over every walk through it. There were 2 lines `692 -> 1 -> ... -> 692`, both during the adversarial C2 jump through the retail niche wall (692 is the retail niche lintel) |
| L4 | No new drop into the gate pool or void along the route; the 10-08 death spot stays away | **PASS** on the route. The route's nearest point is 1,897 units from the death spot (17834,17750). One fall into the retail canal bed happened ~220 units off the route, when my driver overshot (finding 2) |
| L | Log hygiene | **PASS** for LV code. 0 `Unhandled intrinsic`, 0 Segmentation, 0 Assertion, 0 segment access. The other warnings are known retail families or come from the adversarial wedge (see L) |
| C1 | `tools/run_all_tests.sh` | **PASS**: `OVERALL: PASS — 44/44 test file(s)`. `test_map39_lane.py` gave `OK: 7 passed, 0 failed` |
| C2 | Tracked patch equals the fork diff | **PASS**: `PATCH_EQUAL` at `4ccd3fe7` |
| C3 | `build_artifacts.sh`, `install_lv.sh`, `build_scummvm.sh` | **SKIPPED** on instruction. The sha256 match above stands in for them. The Compilation Report was not re-read; this change touches only FIXED |

**Cheats used: none.** `Cheats` appears 0 times in the log. The console was used only for:
- `objectInfo`, `getGlobal`, `findShape` and `debugflag_enable Object`;
- `Kernel::listProcesses`;
- `Ultima8Engine::saveGame` (through the save gump) and `loadGame`.

There were no teleports, no `Cheat::toggle` and no flag writes. The Map 3 guard's menu was clicked on screen.

**Checkpoint banked:** `~/lv-checkpoints/run1009b-s01-lb-done.sav` (new; md5 `41bdd72b…`).
- It is on Map 39 at (17046,19922,48), hp 30, with lbStarted 1 and lbDone 1.
- I reloaded it once: the same position and flags came back, and a walk burst moved him to (17046,19986,48).

## Method

- **Start.** `~/lv-checkpoints/run1008-s00-prologue-after-execution.sav` is on Map 3 (11747,5811,48), the post-execution dock. It had never loaded Map 39.
  - On arrival, `findShape 66` listed the four LV rocks at (17540,20010), (17380,19960), (17220,20000) and **(17800,19900)**, and none at the old (17060,19950).
  - So the world was carrying the new FIXED map, not an old saved copy.
- **Saves.** Saves went through `Ultima8Engine::saveGame`, which opens the save gump. I clicked slot 1 and then OK, and checked that the slot's mtime moved. Each one was copied to `sp/<name>.sav`. A reload copied a bank over `ultima8.001` and ran `loadGame 1`.
- **Gait (harness, see anomaly 1).** At 640x400, mouse distance is judged with screen y counted double. A walk needs `hypot(sx, 2·sy) ≤ ~76` px; I used 60. Anything larger runs, about 550 units/s.

## L1: the walk, PASS

| Leg | Positions read (x,y,z), map | Note |
|---|---|---|
| Map 3 dock → gate | (11747,5811) → (11747,4707) → (11643,4411) → (11643,3507) → (11567,2639): **GUARD1** "Halt, stranger!" | Picked **I am Avatar.** → "All right, Avatar, now I know ya" → **Bye** from the screen. Then (11639,2183) → (11535,1983) → **Map 40** |
| First attempt | Death at (12575,2111), m3 | I left the guard's menu unanswered, and he beat the Avatar from hp 29 to 0 while my driver kept walking (finding 4). I restarted from the checkpoint |
| Map 40 | Arrived at (13038,15042), then the AVATAR detour (map 0, `[0405 02] = 1`). Then (13038,15002) → (10902,15002) → (10826,14230) → (10766,14074) → **MAP 40→39** | Map 40's id-0 teleporter (10506,14070), range 0x54. Route from `rt.py`, with the map-3 and map-41 trigger boxes masked. Plate `L1-01` |
| Map 39 arrival | (19034,14070,48): the pad (19130,14070) plus one walk burst west. lbStarted 0, lbDone 0 | `L1-01-m39-arrival-pad` |
| → (16975,14383) → (16975,14911) → (16935,14983) → (16903,14991) | (17298,14070) → (16966,14402) → (16966,14930) → (16898,15006) | `L1-02` |
| → (15319,16631) | Run gait. It zig-zagged along the diagonal, as far as (14734,17170), then settled at (15282,16622) | Off-line by up to ~550, always at z 48. `L1-03` |
| x 15319 by the canal, y 17536..17840 | (15282,17542) → (15282,17606) → (15282,17670) → (15258,17918). The earlier attempt passed (15282,17734) → (15210,17910) → (15270,17850) | **x 15210..15282**, 37-109 west of 15319. That is the side away from the drop: the bridge's z-48 floor (242) ends at x 15359. `L4-01`, `L1-04` |
| → (15399,17903) → (15959,18039) | (15386,17918) → (15770,17918) → (15970,18054) | `L1-05` |
| → (15959,18343) → (16039,18415) | (15970,18310) → (16054,18394) | |
| → (16191,19400), the east niche | (16054,18490) … (16138,19342) → **(16194,19398,48)** | `L3-01` |
| South through the tunnel, 64-unit steps | y 19398, 19430, 19494, 19558, 19622, 19686, 19750, 19814, 19878, 19942, 20006, **20070**, all at x 16194, z 48 | `L3-02-tunnel-00..10` |
| → (16239,20047) → east | (16214,20050) → (16342…16982,20050) → (17014,20050). A 0.6 s nudge east gave **(17046,20050)** | 17014 is west of the box edge 17022, so I nudged east |
| North into the box | Three 1 s walk bursts north. The log showed `Item: 4836 (shape 73) calling usecode event 7 @ 05AF:0080`. The Avatar was at (17046,19890) after the scene | That is inside x [17022,17342), y [19572,19892) |

## L2: step 1, PASS

- **Flags.** Before the hatch, lbStarted was 0 and lbDone 0 (read on arrival and again at the pre-hatch bank).
- **The scene.** From the hatch I took 44 plates over ~110 s, with no console attached.
  - The apparition gave the full message: "Avatar, I have found a portal through which I can speak…", "…Mythran…", and "Only with his aid canst thou escape. Farewell, Avatar…". Plates: `L2-scene-00/06/13/22`.
  - It then vanished (`L2-scene-28`, `-43`).
  - The camera was back on the Avatar by `-28`. Plate `L2-01` is a mobility burst after the scene: (17046,19890) → (17046,19922).
- **Afterwards.** `getGlobal`: **lbStarted 1, lbDone 1**. `[0405 02] = 1`.

## L3: the tunnel

### L3a: passable and hidden, PASS

- **The walk.** It ran south at constant x 16194 and z 48 from 19398 to 20070, 64 units per 1 s burst, with no stall.
- **Hidden.** In `L3-02-tunnel-00` (y 19398) through `-08` (19878), the Avatar is not drawn. At `-09` (19942) he shows in the south doorway, half behind the jamb, and at `-10` (20006) he is in full view.
  - So he is hidden for about 480-540 units of y.
  - That includes the stretch north of the niche face: the wall block stands between him and the camera.

### L3b: lintels, PARTIAL

- **South opening (PASS).** `L3-03-south-opening-from-field` and the zoom `L3-03b-south-opening-zoom` show the pale jamb and the pale-slab floor. The wall's horizontal course runs unbroken across the top of the opening: lintel 670 at z 88..96, x 15999..16255, y 19935..19967. There is no gap to the roof.
- **North opening (NOT DEMONSTRATED visually).** It is in the −y face, which U8's fixed view never draws. In the built map:
  - retail 692 runs at z 88..96 over the niche, x 15999..16031 and 16223..16255, y 19455..19583;
  - 670 runs at z 88..96 over the cut back, x 16127..16255, y 19583..19615, with 13/0 and 15/1 above it at z 96..136.
  - Source: `vlane/geo/near.py 16000,19200,16300,20100`.

### L3c: the moved rock, PASS

- **Placement.** In `L2-01-after-scene-mobile` the four rocks project where `findShape` puts them. The Avatar's own (17046,19922) gives (344,231), (394,246), (421,273) and **(514,291)**.
- **Appearance.** The (17800,19900) rock stands alone on grass, clear of the three others and of the main-gate slab, upright and not clipped.
- **The old spot.** (17060,19950) is empty, and it is where the walk came up into the box.

### L3d: negative controls at y≈19800, FAIL (pre-existing behaviour)

I started each test from bank `w-m39-tunnel-mid-post` at (16190,19802,48), taken after step 1.

| Test | Input | Result |
|---|---|---|
| Step east | Mouse-walk +x for 1.5 s | Stops at **(16222,19802,48)**, flush with the east wall (x 16223..16255) |
| Step west | Mouse-walk −x | Stops at (16170,19782,48) |
| T1 | SPACE only, standing | No change (16190,19802,48) |
| T2 | Facing east, UP only, 2.5 s | No change (16222,19802,48) (`L3-06`) |
| M1 / M2 | Facing east, both buttons, or RMB+SPACE (the mouse jump) | **Refused**, (16222,19802,48) (`L3-12`, `L3-13`) |
| M3 / M4 | Facing west, RMB+SPACE, or both buttons | **Refused** (`L3-14`) |
| **East T4** | Facing east, UP+SPACE for 0.35 s (the keyboard jump, which runs the climb scan) | **(16725,19802,0)**: through the east wall into the gate block's hollow at z 0. Held for 2.5 s (the first run) it went on to (17557,19802,0), then (17653,19802,0), **under the field** and invisible (`L3-04`, `L3-05`, `L3-07`). hp 30 |
| **West T5** | Facing west, UP+SPACE | **(16125,19782,54) frame 170**: wedged mid-jump inside the west wall's footprint. The body spans x 16061..16125 and the wall x 16063..16095. Six more inputs (UP+SPACE, a mouse walk east) did nothing. `Kernel::listProcesses 1` was empty, ef went 0x122→0x102, and the log shows **3× `Seem to be stuck in process loop - killing current process!`**. This is a soft-lock: only a reload gets out (`L3-08`) |
| **Retail C2** | Retail niche **east** side wall (8/0, x 16223..16255, y 19487..19583). Avatar at (16222,19554), facing east, UP+SPACE | **(16725,19554,0)**: the same drop into the hollow (`L3-10`). This is where the 2 `Cycle in paint 692 -> 1` lines came from |
| **Retail C3** | Retail niche **west** side wall (x 15999..16031). Avatar at (16098,19534), facing west, UP+SPACE | **(16045,19534,56) frame 170**: the same mid-air wedge (`L3-11`) |
| Retail C1 | Gate wall's north face, (16334,19450) | The jump went along the face at z 48: (15926…14950,19450), about 450 per jump, with no drop (`L3-09`) |

**What these show.**
- The Avatar never climbs onto a wall top: z never went above 56.
- Stepping into the walls and mouse jumps are refused.
- The keyboard jump goes 450-500 units forward, and against an N-S wall of this hollow gate block it either goes through (+x) or wedges (−x).
- The retail niche walls behave identically, so the lane's walls reproduce a retail hole rather than adding a new kind.
- The claim as written does not hold. The lane does extend the exposed wall surface from the niche's ~96 units to ~450.
- Cause [INFERENCE]: the jump animation's large per-frame steps against 32-thick walls with nothing under the hollow; see finding 1.

### L3e: paint cycles, PASS

- **During play.** There were 0 `Cycle in paint` lines through all walks of the niche, the tunnel, the field and the scene.
- **During the adversarial jump.** C2 produced 2 lines, `692 -> 1 -> ... -> 692` (log lines 14981 and 14983), with the Avatar inside the retail niche wall.

## L4: drops along the route, PASS

- **The death spot.** (17834,17750) is **1,897 units** from the nearest route segment. The walk never went east of x 17046 south of y 15000.
- **The water.** The sea nearest the route is at z 0. Its distance from each leg is 168-2000 units (`vlane/geo/sea.py`).
- **No drowning.** Every position read on the route was z 48.
- **The canal-bed fall (off route).** My run-gait burst from (15898,17958) toward (15959,18039) overshot to (16181,18271,**0**), then went on to (16063,18055,8). That is the retail canal bed (shape 126, LAND), not the gate pool or void (`L4-02`). hp stayed 30. I reloaded `w-m39-canal-n` and walked the legs at walk gait. See finding 2.

## L: log hygiene

`vlane/lv_run.log`: 15,921 lines over two launches and nine in-game loads.

| Pattern | Count | Context |
|---|---|---|
| `Unhandled intrinsic` | 0 | |
| Segmentation / Assertion / `Trying to access segment` | 0 / 0 / 0 | |
| `Seem to be stuck in process loop` | 3 | All at lines 14393-14395, while the Avatar was wedged in the west wall (T5, adversarial) |
| `Non-existent process PID (0) in implies` | 5 | 1 in the retail GUARD1 talk on Map 3 (line 1809); 3 in the Map 0 AVATAR detour (2108-2111); 1 on Map 39 entry (3360, the known Tenebrae-entry one) |
| `popToContainer to invalid container` + `Destroying orphaned ethereal object` (shape 174) | 6 + 6 | Map 39 entry (3330-3357), the known retail family (10-09 Aramina report, there on m41) |
| `Cycle in paint` | 2 | C2 only (L3e) |
| `No SchedulerProcess` | 0 | |

## Findings outside the brief

1. **The keyboard jump (UP+SPACE) goes through, or wedges inside, the N-S walls of Tenebrae's hollow gate block, both retail and lane.**
   - **Through (+x).** He ends at z 0 in the sealed hollow and then wanders under the field at z 0.
   - **Wedged (−x).** He hangs mid-air at z 54-56, the runaway guard kills 3 processes, and he never moves again.
   - **Evidence.** T4/T5 on the lane walls, C2/C3 on the retail niche walls. This is the `U8AvatarMoverProcess` path at `u8_avatar_mover_process.cpp:464-503`: a keyboard direction with no mouse runs the climb scan, then `doAnim(jump)`.
   - **Mouse jumps are refused at the same spots** (M1-M4), and those are what most players use.
   - **Severity.** Low-medium: a reload is needed. The lane makes it easier to meet, because ~450 units of tunnel wall now face a walker.
   - **Possible directions** [INFERENCE]: an engine-side sweep fix in the jump tracker, or a floor in the hollow at z 48 so the drop lands somewhere.
   - Confidence: high on the behaviour (four reproductions), low on the mechanism.
2. **The brief's waypoints (15959,18039) and (15959,18343) run 40 units from an unrailed drop.**
   - **The geometry.** The z-48 floor (92) ends at x 15999 along y 17791..18303, and the canal bank and bed lie below it (85/86 at z 8..40, 126 at z 0..8). It is a retail drop, not the gate pool; the sea (347) is one tile further east.
   - **What happened.** A run-gait overshoot took the Avatar into the bed alive.
   - **The test's route differs.** `test_map39_lane.py` now prints a different line here, (15535,17911) → (16039,18367), which cuts across well clear of the edge.
   - **Advice.** A player or verifier should follow the test's line, not the hand list.
   - The x-15319 bridge stretch has the same 40-unit margin to the bridge's east edge (x 15359).
3. **A world fresh to Map 39 reaches the lane in about 10 minutes of play from the prologue,** and needs only the guard's menu. The chain is Map 3 gate → Map 40 → the AVATAR detour → Map 40 west to the id-0 gate at (10506,14070) → Map 39. No door, fight or cheat is needed. This is the walk the 10-09 full run could not make.
4. **GUARD1 kills an unanswered Avatar.** On the first attempt the guard's "I am Avatar / I am the Avatar! / Who is your name?" menu sat open while the driver probed directions, and the guard took hp 29 → 0. This is retail, but a walker script must answer the menu first.

## Harness anomalies

1. **Gait threshold at 640x400.** The mouse distance counts screen y double. A walk is `hypot(sx, 2·sy)` ≤ ~76 px; at 95 px he runs. The 10-09 driver's plain `sdir` magnitude ran on screen-vertical directions even at "60".
2. **`Ultima8Engine::saveGame` opens the save gump** in this build. The save takes a click on the slot thumbnail (525,110) and then OK (430,233), and the gump closes the console. A blind `con()` around it times out.
3. **New PNGs written under `/tmp` sometimes read as "not found"** by the image reader on the first try, and are found on the second.
4. **The first eval cell timed out at 30 s,** because the default cell deadline is shorter than one `con()` round trip ×3.

## Disk changes

- **Wrote** this report and 40 plates in `docs/playtest-2026-10-09-lane/`.
- **Wrote** `~/lv-checkpoints/run1009b-s01-lb-done.sav` (new; nothing overwritten).
- **Scratch** in `/tmp/claude-1000/vlane/`:
  - `game/`, `scummvm.ini`, `run.sh`, `lv_run.log` and `trace.txt` (timestamped positions);
  - `py/` (`drv.py`, `h.py`) and `geo/` (`sea.py`, `near.py`);
  - `saves/`;
  - `sp/` (the banks `w-m40-arrive`, `w-m40-westgate`, `w-m39-arrive`, `w-m39-a`, `w-m39-canal-n`, `w-m39-canal-s`, `w-m39-b`, `w-m39-niche`, `w-m39-tunnel-south`, `w-m39-prehatch`, `run1009b-s01-lb-done`, `w-m39-tunnel-mid-post` and `ck-verify`; the scene frames; the montages).
- **Stopped:** my ScummVM and Xvfb `:88`. No other process was touched.
- **Not touched:** `shared/`, `~/.config/scummvm`, source, builders, maps, the fork, `TODO.md` and `HANDOFF.md`. Nothing was committed.

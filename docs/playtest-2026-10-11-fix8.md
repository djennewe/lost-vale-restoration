# Fix 8 verification: Fire talisman column, Ezrekal's east door and potions, Map 13 rim, Map 8 key chest (2026-10-11)

**Build under test.** main `df800bf` (fix 8 merged at `27a3e7c`: `76e9d84`, `afaf4a9`, `b20653b`, `32608f9`). Game copy `/tmp/claude-1000/vf8/game`, made from vf7's copy with both FIXED.DAT copies replaced from `shared/build/`. All five match `shared/build/ARTIFACTS.sha256`: FIXED `ee4182d0…` (root and `STATIC/`), EUSECODE `b73b47fa…`, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`. The binary is `scummvm-lv/scummvm`, built 2026-10-10 23:57, after fork `b867a30c`.

**Harness.** Xvfb `:93`, vf7's ini: 320×200, no width/height keys, `frameLimit=true`, `usehighres=false`, `SDL_AUDIODRIVER=dummy`. The driver is `vf8/py/vf.py`, a copy of vf7's with the paths changed. Films were taken with `ffmpeg x11grab` at 25 fps. `vf8/py/camtrack.py` reads the Avatar's world track out of a film: the camera follows him, so it phase-correlates consecutive frames (with the centre masked) and converts the screen shift to world units. It was validated on a passing run: the film's track ended at (12566,12608), and `objectInfo` read (12564,12610).

**Cheats.** Cheats were on only for teleports *to a start point*. That covers the D1, L1 and R1 trial starts, and the Map 10/8 hop that refreshed Map 8. Every Map 8 key, chest and door action and the walk into T201 ran with cheats off (`Cheats = false` echoed). The walks into 204 (Map 11) and 207 (Map 13) were walked, and the maps loaded fresh.

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| L1 | Map 11, fresh load: N from the Fire talisman (5560,18880) to the north wall, and NE then N, keep hp; no gotHit on 318/409 | **PASS** | 4 of 4 lines reached the north wall (y 14400-14410) at hp 30, with **0** `event 6` lines from any item. FIREPIT 12231 now stands at (4608,16384) and 12226 at (4096,15360). Negative control: a walk into 12231 logs `event 6 @ 013E:00B6` |
| D1a | Map 10: mouse **walks** W into Ezrekal's east door at y 12600-12671 pass ≥250 inside | **PASS**, 6 of 6 | Ends x 12804-13642 |
| D1b | Map 10: mouse **runs** W into the door at y 12600-12671 pass ≥250 inside | **FAIL**, 12 of 33 stopped outside | Every stop is a **standing start with the Avatar already facing W**, from x 14300 or 14407. They end at (14048-14064, 12678-12763), the build 7 stop. The same start with any other facing passed 6 of 6, and runs under way passed 6 of 6. Cause partly captured; see D1 and finding 1 |
| D1c | Potions at (13760/13696,12800) can be picked up | **PASS** | Both look-clicked (items 3806/3805). Each drag onto the Avatar logged `Dropped item in backpack`; weight 50→60→70 |
| R1 | Map 13: S/SE/E holds off pad 207 end against the rim with the Avatar drawn; no walk-off; no paint cycles | **PASS** | 9 holds (walk and run) plus 2 held-jump attempts at the rim. The Avatar is drawn at every end. All ends are at z 0 on m 13 and hp 30. **0** `Cycle in paint` lines while Map 13 was loaded |
| K1 | Map 8: the chest at its new spot is visible and clickable, holds the q99 key, step 3's key and doors work, and there are 0 `358 -> 1` lines | **PASS** | Chest 26267 at (20436,3340,0) is drawn and look-clicks, and its gump holds key 26266 **q99**. One key use unlocked both leaves, a double-click opened them (both shape 340), and a walk N reached **Map 9**. **0** `358 -> 1` over 2 fresh Map 8 loads. Negative control: a double-click with both leaves locked left them shape 342 |
| L | Log hygiene | **PASS** (stock noise only) | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Trying to access segment`, `popToContainer`, ERROR, `Invalid item`, `Invalid procid`. **2 × `Unhandled intrinsic 254 'isGameRunning()'`**, both from CHEST_EW `event 1 @ 004E:00A9` (the open and the gump-close double-click). Paint cycles were retail only, see K1 |
| Checks | Test estate; artifact hashes; fork | **PASS** / not triggered | `tools/run_all_tests.sh`: **46/46 PASS**. The game copy's sha256 equals `ARTIFACTS.sha256`. I did not run `tools/build_artifacts.sh`: the assignment forbids build scripts. Fix 8 touches only `agents/map-populator/**` and `ARTIFACTS.sha256`, so the fork-patch, usecode and shape checks do not trigger |

## L1: the Fire talisman's north column — PASS

**Fresh load.** I loaded `run1010-s04b-m11-three-talismans` and teleported to Map 10 (11900,2750). I then walked N into 204. The log shows `Loading Fixed items in map 11` and `event 7 @ 05B2:0080`, and the Avatar arrived at (8291,22607).

**FIREPITs (318) after the load** (`findShape 318`, 9 found): none is left in the talisman's column. 12231 is at **(4608,16384)**; build 7 found it at (5632,16384). 12226 is at **(4096,15360)**. `findShape 409/794/267` returned 0 found (finding 4).

For each line I teleported to the start, held the input, and collected every `calling usecode event 6` line from an item other than the Avatar:

| Line | Start | End | hp | event-6 hits | Plate |
|---|---|---|---|---|---|
| Walk N 14 s | (5560,18880) | (5538,14406), north wall | 30→30 | none | `L1-walkN-to-wall` |
| Walk NE 2.5 s, then N 12 s | (5560,18880) | (6072,14400), north wall | 30→30 | none | `L1-walkNE-then-N` |
| Walk N 14 s at x 5456 | (5456,18864) | (5438,14410), north wall | 30→30 | none | — |
| Run N 7 s | (5560,18880) | (5684,14404), north wall | 30→30 | none | `L1-runN` |
| (first attempt) walk N 10 s | (5560,18880) | (5538,15406), still walking | 30→30 | none | — |

**Negative control.** I walked N at x 4600 into FIREPIT 12231's new spot, twice: from (4600,17100) and from (4600,16700). Both logged `Item: 12231 (shape 318) calling usecode event 6 @ 013E:00B6`, so the detector sees a pit contact (`L1-neg-walk-into-firepit`). Neither contact cost hp (finding 3).

## D1: Ezrekal's east door — walks PASS, runs FAIL, potions PASS

**Setup.** I teleported from Map 11 to Map 10, so the map loaded fresh. `findShape 859` showed the two typed potions at **(13696,12800,4) frame 2** and **(13760,12800,4) frame 1** (npcnum 229). Each trial teleported to the start, held the right mouse button with the pointer W (340 px for runs, 110 px for walks), and then read `objectInfo 1`. A pass means the Avatar ends at x ≤ 13733, which is 250 inside the doorway's line at 13983.

### Walks — 6 of 6 pass

I walked from x 14300 for 4 s at y 12600, 12610, 12620, 12640, 12660 and 12671. The walks ended at (13642,12498), (12804,12610), (13310,12626), (13122,12618), (12804,12660) and (13122,12649) (`D1-walk-12610-inside`).

### Runs — 12 of 33 stop outside, all standing starts facing W

| Start | How the run began | Runs | Stopped outside | End of the stops |
|---|---|---|---|---|
| (14300,12610) | standing, facing W (his previous move was W) | 8 | **8** | (14048,12678) every time |
| (14300,12610) | standing, facing S or turned away (a 0.6 s walk S, or the turn left by a failed run) | 6 | 0 | (12564,12610) |
| (14300,12600) | standing, facing W | 1 | 0 | — |
| (14300,12600) | standing, facing N (first trial after Map 11) | 1 | 0 | — |
| (14300,12620) | standing, facing W | 2 | **1** | (14064,12712) |
| (14300,12640) | standing, after a W walk | 1 | 0 | — |
| (14300,12660) | standing, after a W walk | 1 | **1** | (14048,12728) |
| (14300,12671) | standing, after a W walk | 1 | **1** | (14064,12763) |
| (14191, 12600/12640/12671) | standing, facing W (on the worn-earth track) | 3 | 0 | — |
| (14407, 12600/12640) | standing, facing W | 2 | 0 | — |
| (14407,12671) | standing, facing W | 1 | **1** | (14049,12717) |
| (14800, 12610/12640/12660) | under way by the door, facing W or S | 6 | 0 | 12400-13636 |

So **build 7's stop still happens**, at the same place. Every stop ends against the east face of the south palisade segment (857 at (13983,12799)), 7-92 units south of the doorway's south jamb (12671).

**What decides it is the facing at a standing start.** At (14300,12610), facing W failed 8 of 8 and any other facing passed 6 of 6, with both step-parity flags (`fl 0x400` set and clear) on each side (`D1-faceW-14300-12610-stops-outside`, `D1-faceS-14300-12610-passes`). A 3 s pause before the run made no difference. A player gets here by walking up to the door, stopping, and then running on.

**The cause, as far as I captured it:**
- **Hit events.** A failing run's log holds only the Avatar's own `event 18` lines (88 of them). No item's gotHit (`event 6`) fired, and hp stayed 30.
- **Nearby NPCs.** Ezrekal (npc 116) stood at (12799,12831), 1,200 units west. No actor appears anywhere in the film's frames (`D1-film-faceW-run-sheet`).
- **Items.** FIXED.DAT has no solid within x 13600-14100, y 12350-12900 except the two palisade segments and the flask row at y 12800. The potions are 97 units south of the doorway's line and are not involved. Stops happened both before and after they were picked up.
- **The film.** `vf8/sp/D1-film-run-12610b.mkv`; the camera track is in `D1-film-run-12610b.track.txt`.
  - Frames 20-30: the Avatar runs W and slightly N, (14282,12604) → (14018,12556).
  - Frames 31-35: he slides S to (13972,12610). That is 11 units past the door's line, at the doorway.
  - Frames 38-42: in 4 frames (0.16 s) the view jumps **+92 E, +92 S** to (14064,12702).
  - Then he settles at (14048,12678), which is the `objectInfo` value. He turns, and stands with the button still held (`D1-film-faceW-run-frames28-43`).
  - [INFERENCE] The jump is the interpolated display snapping back to where the engine had actually committed him. The run's real steps went SW and never entered.
- **The model does not reproduce it.** `avatar_mover.hold(..., standing=True)` gives `clear` (≈2,200 units W, no y drift) for all six failing starts, with either step parity (`vf8/py/d1model.py`).
- **Worn-earth track.** The model has three worn-earth track tiles (425, frames 19/6/13) at x (13951,14207] across y 12415-12799, with TYPEFLAG footpad z 0. [INFERENCE] Starts at 14191 begin *on* the track and never failed, and every failure started east of its x 14207 edge. `traps.md` records a run refusing a 425 track lip on Map 10, so the leading suspect is the running step onto the track's east edge, which the model treats as flat. Not proven.

### Potions — PASS

From (13640,12720) both potions are drawn in front of the south palisade (`D1-potions-before-pickup`).
- Look-clicks logged `Item 3806 … (13760, 12800, 4)` and `Item 3805 … (13696, 12800, 4)`.
- Dragging each onto the Avatar logged `Dragging item 3806` → `Dropping object 3806` → `Dropped item in backpack`, and the same for 3805. Weight went 50→60→70 (`D1-potions-after-pickup`).
- `findShape 859` then listed both as contained (`(255, 255)`, `f: 0xc`).
- The pickup was a real drag, not `Item::grab`.

## R1: Map 13 rim — PASS

**Fresh load.** I teleported to Map 10 (7252,23200,8) and walked S into 207. The log shows `Loading Fixed items in map 13`. The button was still held at arrival, so the Avatar walked straight on S off pad 207 and stopped at **(4096,12272,0)**, drawn against the edge (`R1-S-walk-held-through-arrival`). Build 7's plate at this spot showed only the rim.

Each later hold started from a teleport onto pad 207 (4096,11776,0):

| Hold | End | Drawn | Plate |
|---|---|---|---|
| S walk 4 s | (4070,12274,0) | yes | `R1-S-walk` |
| S run 3 s | (4052,12284,0) | yes | `R1-S-run` |
| SE walk 4 s | (5392,12240,0), along the south edge | yes | `R1-SE-walk` |
| SE run 3 s | (6136,12280,0) | yes | `R1-SE-run` |
| SE walk 12 s | (6636,12268,0), the SE corner | yes | `R1-SE-walk-long` |
| E walk 4 s / 12 s | (4986,11750,0) both times, against a rock spire, not the rim | yes | `R1-E-walk-long` |
| E run 3 s | (6296,11928,0), still running | yes | `R1-E-run` |
| E run 6 s | (6644,11980,0), the east edge | yes | `R1-E-run-long` |

- Every end was on m 13 at z 0 with hp 30. There was no fall and no map change.
- Past the edge the plates show black void; the rim courses no longer stand in front of him.

**Negative control: jumping the rim.** At the south edge (from (4096,12150), mouse walk S, then Up + Space held 2.5 s) the film shows two jump animations (`R1-neg-jump-S-rim-film-sheet`). He stayed at (4096,12288,0). At the east edge (from (6560,11900)) he stayed at (6656,11964,0) (`R1-neg-jump-E-rim`). The invisible courses hold against the jump.

**Paint cycles.** 0 `Cycle in paint` lines between the Map 13 load and the next map change.

## K1: Map 8 key chest — PASS

**Start.** `run1010-s03a-m8-door-niche-current-fixed`: doors locked, key in the chest, saved before fix 8. The checkpoint carries the chest's old spot, so I hopped Map 8 → Map 10 → Map 8 (teleports; `Loading Fixed items in map 8`). Then:

1. **The chest.** `findShape 78`: item **26267** at **(20436,3340,0)**, `items: 1`. `findShape 82`: item **26266**, KEY, **q: 99**, contained. The chest is drawn SW of the Avatar on the bone field at (20430,3250) (`K1-chest-view`).
2. **Cheats off.** `Cheats = false`.
3. **Click.** A single click logged the chest's `dumpInfo` and `event 0 @ 004E:0080`.
4. **Open.** A double-click logged `event 1 @ 004E:00A9`, and the gump shows the key (`K1-chest-open-gump`). I dragged the gump clear of the doors.
5. **The key.** Double-click key 26266 (`event 1 @ 0052:04BB`), then click the west leaf: `Target result: Item 24005 … q: 1635`. Both leaves then read west **611** and east **99**: one use unlocked the pair (finding 2).
6. **Negative control** (taken earlier in the same visit, while both leaves read 1635/1123 after a second use re-locked them): double-clicking the west leaf ran `event 1 @ 0156:0098`, and `findShape 340` read 0. They stayed closed.
7. **Open.** With both unlocked, a double-click on the west leaf turned both into **shape 340** (q 867/355) (`K1-doors-opened`).
8. **Map 9.** Mouse walk N up the doorway column (x 20365-20383) → `Loading Fixed items in map 9`, Avatar at (13696,13376,0).
9. **Repeat.** Cheats on to teleport to (20383,3456,0), the spot of build 7's `358 -> 1` lines (`K1-avatar-at-20383-3456`; the Avatar, the chest and skeleton 358 are all drawn). Cheats off, then walk S 1.2 s and N 4 s → Map 9 again.

**Paint cycles on Map 8**, split by load:

| Segment | `358 -> 1` | `590 -> 235` | `235 -> 65` |
|---|---|---|---|
| s03a checkpoint load (old fixed items, before the hop) | 0 | 0 | 1,345 |
| First fresh Map 8 load (chest, key, doors, column walk) | **0** | 9,377 | 0 |
| Second fresh Map 8 load (stand at (20383,3456), column walk) | **0** | 791 | 0 |

The two pairs that did log are the retail skeleton pairs `32608f9` names, 590/235 and 235/65.

## Findings outside the brief

1. **Ezrekal's east door still turns runs away, when the run starts from a standstill already facing W** (D1b). This is reproducible: 8 of 8 at (14300,12610), and also at y 12620-12671 and from x 14407. The Avatar ends at (14048-14064, 12678-12763), against the south palisade's east face.
   - Not involved: hit events, NPCs and the potions.
   - Not reproduced by `avatar_mover`, which explains why `test_route_reach.map10_wedges` passes; its standing holds go clear.
   - **Suspect** [INFERENCE]: the worn-earth track's east edge at x 14207 (425 tiles, footpad z 0 in the model). Any start on the track passed, and every failing start lay east of it.
   - **Next step for the author:** film the failing start with `Kernel::toggleFrameByFrame`, or log `tryAnim` results at the 14207 edge. Then compare the engine's step-up against the 425 tiles' real height.
2. **One key use unlocks *both* door leaves, and a second use re-locks both.**
   - Observed: 1635/1123 → (use on west) → 611/99 → (use on east) → 1635/1123 → (use on west) → 611/99.
   - `docs/playtest-2026-07-31-doors-investigation.md` already records "the 0x400 LOCKED bit cleared on BOTH leaves".
   - The resume notes in `playtest-2026-10-10-full-run-part2.md:77` ("use it on both leaves") and `…part3.md:77` ("target both leaves") tell the reader to use it twice. That re-locks both, and it explains part 4's finding 4 ("the first key use on the west leaf did nothing").
   - Retail behaviour; the docs mislead.
3. **FIREPIT contact does not always hurt.** Two deliberate walks into 12231 each logged its `event 6` with hp 30→30. Build 7 lost 2 hp to two such events. [INFERENCE] The damage is chance-based, so L1 was judged on event-6 lines, not hp.
4. **`findShape 409`, `794` and `267` all read 0 found on the freshly loaded Map 11**, while `findShape 318` listed pits up to 1,600 px away. `test_route_reach`'s hazard list puts 409 lava on this map. Not followed up: I do not know whether the lakes load under another shape or `findShape` misses them. L1's event-6 check covers any shape.
5. **The retail bone-field cycles are heavy.** One fresh Map 8 stay of about 4 minutes logged 9,377 `590 -> 235` lines. They are retail (`32608f9`), but they bury anything else in the log; filter them before reading a Map 8 log.

## Harness anomalies

- One eval cell timed out mid-hold and left the right mouse button down. I released it with `xdotool mouseup 3` before the next trial.
- The cheat state survives `loadGame`. Cheats were on before the s03a load, so the toggle after it echoed `Cheats = false`, and I had to toggle again before the hop.
- The file reader missed freshly written PNGs several times on its first read; a second read found them.
- My console `con()` replies on Map 8 were often swamped by `590 -> 235` lines. Filtering on `shape N)` fixed `findShape`.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-fix8/` (30 plates).
- **Scratch** `/tmp/claude-1000/vf8/`:
  - the game copy (vf7's, with FIXED.DAT replaced), `scummvm.ini`, `saves/` (slot 1 overwritten by the checkpoints loaded), `lv_run.log`, `trace.txt`;
  - `py/` (`vf.py`, `camtrack.py`, `d1model.py`);
  - `sp/`: shots, films `D1-film-run-12610.mkv` (pass), `D1-film-run-12610b.mkv` (stop) and `R1-jump-S.mkv`, contact sheets, and the camera track `D1-film-run-12610b.track.txt`.
- **Banked nothing** in `~/lv-checkpoints`.
- **Stopped** my ScummVM (pid 3977397) and Xvfb `:93` (pid 3977392). I did not touch the other Xvfb instances running on this machine.
- No source, map, fork, `TODO.md` or `HANDOFF.md` edits; no install or build runs.

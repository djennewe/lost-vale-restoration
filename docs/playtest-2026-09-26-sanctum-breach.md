# The sanctum breach, verified in engine (2026-09-26)

Change under test: the uncommitted breach on HEAD `069305b`. Six Map 18 wall
records on y 6143 carry quality 307; `EggTempleEntry` (TEMPLENT) destroys
them when `templeOpen` is set, and `EggCrackHint` (CRACKHNT) re-destroys them
on every later arrival, from a second egg at the hall's north doorway.

Artifacts: the full `tools/build_artifacts.sh` exited 0 and
reproduced all four canonical hashes; EUSECODE.FLX `e7e19aad...`, FIXED.DAT
`4a3d3e18...`. `session.sh start` synced both into `shared/u8-lv-patched/`,
and the engine logged `usecode/eusecode.flx: aae44805..., 1505750 bytes` and
`Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)`. Binary
`scummvm-lv/scummvm` built 21:34:48, after the `build_scummvm.sh` edit at
21:34:45. `shared/data/u8-install/` already held both new hashes, so
`install_lv.sh` was not re-run. One ScummVM process (PID 3925281) ran every
test; no `Segmentation` or `Assertion` line in its log. Plates are in
`docs/playtest-2026-09-26-sanctum-breach/`, named by test ID, 640x400.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| S1 | Build and hashes | full build exit 0; TYPEFLAG, U8SHAPES, EUSECODE `e7e19aad`, FIXED `4a3d3e18` all OK; bytes identical to those on disk before | **PASS** |
| S2 | Compilation Report | 48 files, 46 succeed; failures `EALOGO.UNK` (unterminated block comment), `TJORVI.UNK` (unterminated string), the allowlist pair | **PASS** |
| S3 | Test estate | 31/31 on the briefed tree; the 30/31 at session end comes from files edited mid-session outside this change (finding 1) | **PASS** |
| S4 | Shape IDs | `SHAPE_GLOB_WALL_PIECE = 15` (`lv_shapes.py:708`), `GLOB_WALL_STUB = 47` (`build_map_18.py:399`), `TypeTempleWallPiece 15` / `TypeTempleWallStub 47` (`u8c_symbols.py:364-365`); built Map 18 holds exactly six q307 items, all shape 15 or 47; engine counts 265 and 2 equal the built map's | **PASS** |
| S5 | Geometry, engine box arithmetic | `test_crack_geometry.py` 10/10, 129 positions [2751..2879] for 64x40; `exact_reach` full body sanctum to hall: closed UNREACHED, opened REACHED; the doorway egg cannot be walked around, with or without the engine's z0 void support | **PASS** |
| S6 | ScummVM fork | no fork commit; only `build_scummvm.sh` `LV_SIZE` moved | **not triggered** |
| 1 | Before `templeOpen` | doorway egg hatched with no bark; wall egg barked the hint; 11 full-size pushes refused | **PASS** |
| 2 | Shrunken entry | one potion; `templeOpen` 0 to 1; all three barks in order; six records gone; breach open from both sides | **PASS** (QUAKE3 not demonstrated) |
| 3 | Full-size exit, zero potions | all three potions frame 0; walked out through the breach and off Map 18 to Map 10 | **PASS** |
| 4 | Re-entry at full size | wall resealed on arrival (control); doorway egg reopened it 1,370 units north of the wall; walked into the sanctum, no barks | **PASS** |
| 5 | Regrow near or in the breach | natural regrow at (2852, 6220) and adversarial regrow at (2872, 6152) inside the old wall line, hp 30 both times | **PASS** |
| 6 | Save and reload inside the open sanctum (added) | wall still open after load (260 and 1), `templeOpen` 1 | **PASS** |
| 7 | QUAKE3 audible | not attempted; this harness has no audio stream (09-26 unbroken run, A15) | **NOT DEMONSTRATED** |

## Method and harness writes

Saves and `scummvm.ini` were copied to the scratchpad first.
`~/lv-checkpoints/run-s16-tinytar.sav` was copied over `ultima8.001` and loaded
with `Ultima8Engine::loadGame 1`: Map 10 at (21760, 8544), `templeOpen` 0,
`godsFree` 0, `shieldFixed` 1, `spokeTemple` 1, three frame-8 Tiny Tar
(3963, 8603, 14459) in backpack 512.

That save predates `f9a9aba`, so its camera is parked at the Sacred Circle
and the Avatar is off screen (finding 5). **One position write per load:**
`Cheat::toggle` (echo `Cheats = true`), `MainActor::teleport 18 211`, then
`Cheat::toggle` (echo `Cheats = false`, log line 178). That lands exactly
where Map 10's trigger 211 lands, on Map 18 target 211 at (3072, 1792), and
the map switch resets the camera. Every egg under test is a usecode egg;
`justTeleported` affects teleport eggs only. The Map 10 trigger itself was
walked into later, in test 4. The same write was repeated after the second
`run-s16` load for test 5. Cheats were off for all movement.

Other console use: `debugflag_enable Object`, `objectInfo`, `findShape`,
`getGlobal`, one `Ultima8Engine::saveGame` and two `loadGame 1`.
`findShape` lists only the first 40 hits, so the wall is tracked by the total
counts for shapes 15 and 47 plus the q307 ids the list does show.

Two potions were drunk in the hall on arrival (8603 and 14459 as frame 0 after
regrowing), so exactly one full potion (3963) went to the wall.

## 1: before `templeOpen`, PASS

Read (a) on arrival: shape 15 **265**, shape 47 **2**, q307 ids 1924
(2815, 6143, 40) and 15738 (2816, 6143, 0) listed.

From (3072, 4256) a 1.3 s walk south hatched
`Item: 12701 (shape 73) ... 05B1:0080`; `objectInfo 12701` reads
`(3072, 4800, 0) q: 306 ... n: 136 ... range: 8, 8`. Eleven frames over 6 s
show no bark (`B1-doorway-egg-hatched-no-bark.png`,
`B1-doorway-egg-6s-sheet.png`). Counts after: still 265 and 2, `templeOpen` 0.
The doorway egg does nothing before the temple opens.

At the wall, egg 14291 (`05B1`) barked "The stone here is split from top to
bottom -- and there is open air beyond it. But the gap is no wider than my
hand." (`C1-wall-egg-hint-bark.png`). With potions in the pack, on the second
load, it barked the stronger line instead
(`H0-wall-egg-hint-with-potions-carried.png`).

**Negative controls:** three south pushes at (2828, 6100), two south-east,
and two more at (2852, 6100) inside the crack column: y stayed 6100 every time
(`C2-full-size-refused-at-closed-wall.png`). Two south-west pushes slid him
along the wall to (2332, 6100). None of these hatched `EggTempleEntry`: the
log's first `05B0` is line 3893, after the drink. Its hatch box starts at
y 6112 (egg y 6240, range 4), and a full-size body north of the wall has
y at most 6111.

## 2: shrunken entry, PASS

At (2852, 6100) potion 3963 logged `event 1 @ 04E5:00A9`
(`D1-drink-last-potion-at-crack.png`) and he read shape 708 about 1.5 s later.
One 1.2 s walk south, filmed every 0.4 s for 55 s:

| t from walk start (s) | Screen |
|---|---|
| 0 | tiny Avatar at the crack, wall whole (`D1b-shrunk-at-crack-wall-whole.png`) |
| 6.0 to 15.7 | "I am through. The air in here is old, and very still." (`D2-bark1-i-am-through.png`) |
| 16.3 to about 28 | "Behind me the split stone groans and slumps, and the crack falls open into a gap a man could walk through." (`D3-bark2-split-stone-groans.png`) |
| 28.6 | "Three shapes stand in the dark ahead of me, and something about them is wrong -- they do not move at all." (`D4-bark3-three-shapes.png`) |
| 29.2 to 30.5 | "Uh oh..." (the potion wearing off) |
| 31.1 | regrow flash; full size after (`D5-barks-2-3-then-uh-oh-zoom.png`, `D8-...`, `D9-...` sheets) |

Log: `Item: 12371 (shape 73) ... 05B0:0080`. `templeOpen` read **1**. Read (b):
shape 15 **260**, shape 47 **1**, no q307 listed, and `objectInfo 1924` /
`15738` answer `No such object`. So exactly five shape-15 and one shape-47
record went, the six the builder tagged.

Breach from the sanctum side: `D6-breach-from-sanctum-avatar-in-doorway.png`,
`D7-breach-from-sanctum.png`, with before and after zooms
`D10b-crack-zoom-before.png` and `D10-breach-zoom-after.png`. From the hall
side: `E2-breach-from-hall-side.png`, `E2b-breach-from-hall-zoom.png`. U8's
camera is fixed, looking from the south-east, so the hall-side plate shows
the same south face with the Avatar hidden behind it; the floor of the hall
shows through a full-height gap.

**Dressing judgement:** it reads as a clean, straight-sided rectangular
doorway with its lintel removed. There is no rubble, no broken course ends,
and the piece left at x 3007 is a full 40-unit course, so the "low ragged
step" in the builder comment does not show as one. Against the map dressing
standard and the bark's "groans and slumps", it does not read as a ruined
breach. This is a subjective call; the function is sound.

## 3: full-size exit with zero Tiny Tar, PASS

`findShape 859` after the entry: 3963, 8603, 14459, all **frame 0**. No full
potion anywhere in the pack.

**Negative control:** from (3104, 6264) three north pushes: the first slid to
(3060, 6220), then no movement
(`E1-full-size-north-refused-east-of-breach.png`). The standing wall east of
the breach still blocks, so the sweep took only the six.

From (2860, 6220) one 1.4 s walk north took him to (2756, 5820) at shape 1
(`E1b-full-size-walking-north-through-breach.png`). The route
(2847, 5600), (2900, 4800), (3080, 4780), (3080, 4500), (3072, 3000),
(3056, 1900) crossed the doorway egg again (`05B1`, silent). One burst north
logged `Unloading map 18` / `Loading Fixed items in map 10`, landing at
(18432, 22680) (`E3-map10-arrival-after-full-size-exit.png`), `templeOpen` 1.

The exit egg is the Map 18 teleporter at (3072, 1408), q466, teleport id
**210** to Map 10. Id 211 is Map 10's trigger into Map 18 (q467 at
(18432, 23552)). The brief's "trigger 211 -> Map 10" swaps the two.

## 4: re-entry at full size, PASS

A walk south on Map 10 into (18432, 23552) logged `Loading Fixed items in
map 18`, landing at (3072, 1792).

**Control, the reseal is real:** read (c) at the pad: shape 15 **265**,
shape 47 **2**, q307 stub 14678 at (2816, 6143, 0) listed. Fixed items came
back from FIXED.DAT, as `World::switchMap` (`unloadFixed` / `loadFixed`)
says they must.

From (3072, 4300) a 1.3 s walk south hatched doorway egg 6976 (`05B1`).
With the Avatar at (3072, 4776): shape 15 **260**, shape 47 **1**,
`No such object: 14678`. At that point the wall is about 450 px left of screen
centre, off screen. The first frame with the wall in view, at (2872, 5224),
already shows the gap (`F2-reentry-y5200-approach.png`, then
`F3-reentry-wall-in-view-breach-open.png`).

From (2828, 5924) a 1.5 s walk south took him to (2828, 6260) at full size;
`EggTempleEntry` 12477 hatched (`05B0`) and 14 s of frames show no bark
(`F4-reentry-full-size-in-sanctum-no-bark.png`, `F4-reentry-14s-sheet.png`).
Zero frame-8 potions were in the pack.

## 5: the regrow, PASS

Natural case (test 2): he regrew at (2852, 6220), 77 units south of the wall
line, hp 30, and walked on.

**Adversarial case:** `run-s16` reloaded into slot 1 and loaded again, the
same teleport write, walked to (2872, 6032). Potion 14459 was drunk there,
but the 0.3 s taps did not move the tiny Avatar and he regrew in place, north
of the wall; the harness's taps were too short. Potion 8603: walks of 0.6, 0.5, and 0.4 s
took him to **(2872, 6152)**. The tiny box is y 6121..6152, inside the old
wall line 6112..6143. `05B0` hatched. He was left standing for 50 s: barks,
the regrow flash (`H2-regrow-flash-in-wall-line.png`), then full size **in
place**, (2872, 6152, 0), hp 30, counts 260 and 1
(`H1-shrunk-in-wall-line-entry-barks.png`,
`H3-regrown-full-size-in-wall-line.png`, `H4-regrow-in-line-50s-sheet.png`).
The full 64-wide body at that origin covers x 2809..2872, all inside the
opened ground gap 2688..2879.

## 6: save and reload inside the open sanctum, PASS (added)

At (2828, 6260) after test 4, `Ultima8Engine::saveGame` (it always writes
slot 1), then `loadGame 1`: `-- Resetting Engine --` through `MAPS: ok`,
Avatar at (2828, 6260), shape 15 **260**, shape 47 **1**, `templeOpen` 1
(`G1-after-reload-in-sanctum-breach-open.png`). The current map's items come
back from the save's OBJECTS stream, so a player who saves inside is not
resealed on load.

## Findings outside the plan

1. **The tree gained an unbriefed second change during this session.**
   `lv-new/ENDGAME.UNK`, `lv-patched/EZREKAL.UNK`, `test_uc_eggs.py`, and
   `lv-patched-inventory.md` were modified at 21:44:27 to 21:45:45, after the
   build here finished (21:43:39); the breach files date 21:32 to 21:37. The
   change moves the Bag of Reagents hand-over from ENDGAME to Ezrekal ("B1"),
   and its EZREKAL header names this report as its record. This report does
   not verify it. `tools/run_all_tests.sh` is now **30/31**:
   `test_uc_eggs.py` fails "no bag from this scene: Ezrekal gives it now" and
   "no bag hand-over bark". The test simulates the BUILT
   `shared/build/EUSECODE.FLX` (`test_uc_eggs.py:5`), which is still
   `e7e19aad` from the pre-edit sources, so the failure is the unbuilt change
   (high confidence). Once rebuilt, EUSECODE will no longer match
   `ARTIFACTS.sha256` or `LV_SIZE`, so it needs the `/artifact-rehash`
   cascade and a separate engine check.
2. **The breach reads as a cut doorway** (test 2). Straight
   jambs, no rubble, a full-height course where the comment promises a low
   step.
3. **Both eggs re-hatch at the regrow.** In test 2, `05B1` and `05B0` logged
   on the same line (4338-4339) while he was still shape 708, after `05B0`
   had already fired at the crossing. With `templeOpen` set that only
   re-sweeps (TEMPLENT's `first` is 0). In the first test-5 attempt, the
   regrow north of the wall re-hatched `05B1` with `templeOpen` 0, so the hint
   probably barked a second time; the frames were not checked. The same
   pattern was noted in the 09-26 unbroken run (its finding 2).
4. **A drunk Tiny Tar stays in the pack as an empty bottle on top of the
   stack.** After the first drink, the next double-click on the stack hit
   14459 (frame 0), logged `04E5:00A9`, and did nothing. The full potions
   underneath had to be uncovered by dragging the empty aside. A player
   carrying three would see the second drink fail. This predates the change.
5. **`run-s16-tinytar.sav` is an old-build save.** Parked camera (pre-
   `f9a9aba`), the restored shield 10781 lying on the Sacred Circle, and the
   frame-4 `invisShield` 10783 beside it (`WARNING: Skipping invalid shape
   in sorter: 539,4!`), the item that asserts in `ContainerGump` if picked
   up. It was not touched.
6. The builder comment says 128 positions; `test_crack_geometry.py` prints
   129, [2751..2879]. Cosmetic.
7. `CLAUDE.md`, `.claude/settings.json`, and the untracked `.claude/agents/`
   are workflow edits unrelated to the breach, in the same working tree.

## Harness anomalies

- `ObjectManager::findShape` prints at most 40 items; wall state had to be
  read from totals.
- `Ultima8Engine::saveGame <name>` always writes slot 1, and the driver's
  retry sent it twice (both into slot 1).
- The tiny Avatar did not move on 0.3 s right-button taps; 0.4 s and longer
  moved him.
- A pack drop on the gump's lower border logs `Dropping object` and leaves the
  item where it was.

## Disk changes

- This report and `docs/playtest-2026-09-26-sanctum-breach/` (33 plates).
- `shared/build/` rewritten by `tools/build_artifacts.sh` with identical bytes
  (new mtimes).
- `shared/u8-lv-patched/USECODE/EUSECODE.FLX`, `STATIC/FIXED.DAT`, and
  `FIXED.DAT` synced from `shared/build/` by `session.sh start` (untracked).
- `~/.local/share/scummvm/saves/ultima8.000`, `.001`, `.002`, `timestamps`,
  `scummvm-history.txt` and `~/.config/scummvm/scummvm.ini` restored from
  copies taken first (md5 `3e7dc241...`, `083de199...`, `9231fe1e...`,
  `e5a2abea...`, `47c7389b...`, `a143fa3b...`).
- Scratchpad: session log, the in-sanctum save
  (`sanctum-open-2026-09-26.sav`), the driver.
- No source edited, nothing committed, `TODO.md` not edited. Session stopped.

# Batch retest: Map 39 falls, Map 17 tapestry, bag cap, hall rock, potion nudge (2026-10-04)

Change under test: `main` at `55414d4` plus the uncommitted fixes in
`build_map_39.py` (THE FALLS), `build_map_17.py`, `build_map_18.py`,
`lv-new/ENDGAME.UNK`, and `lv-new/CRACKHNT.UNK`, retesting the FAIL and
PARTIAL claims of `docs/playtest-2026-10-03-batch-merge.md`.

Artifacts: `tools/build_artifacts.sh` exit 0, all four OK (EUSECODE
`c9716c73...`, 1,507,239 bytes, first 5000 bytes md5 `4f47de88...`; FIXED
`e8800ad0...`). Binary `scummvm-lv/scummvm` built 2026-10-04 00:12 CDT, after
the fork tip `e0d6084d` (2026-09-19); `detection_tables.h:297` reads
`4f47de88..., 1507239`. All seven session logs read
`usecode/eusecode.flx: 4f47de8811f7fc091c3fa2fabe988283, 1507239 bytes.`
Plates are in `docs/playtest-2026-10-04-batch-retest/`, 640x400, named by
claim ID.

## Verdicts

| ID | Claim | Observed | Verdict |
|---|---|---|---|
| C0 | Build, hashes, estate, fork | estate 37/37; build exit 0, four OK; Compilation Report 46 of 48 (`EALOGO.UNK`, `TJORVI.UNK`), no warnings in the two changed classes; fork patch equals the fork diff | **PASS** |
| C1a | Both previous void routes refused | rim route: the Avatar stops at the new south wall, (14040, 20477, 8); avenue route: last session's start point (20896, 19300) is now inside oak (20990, 19440), and the east push stops at (20702, 19276, 48) | **PASS** |
| C1b | East pushes off the avenue hold at z 48 | seven y from 19300 to 17960: every east push stops at x 20670..20702, z 48 | **PASS** |
| C1c | Doorways and main gate | main gate: stop at (17330, 19492, 48) under the arch, both jambs hold; the three small doorways cannot be entered from the lane at all (finding 3); entered from the city side, each holds z 48, two with the Avatar at rest over the strip | **PARTIAL** (the lane walk the claim describes does not exist) |
| C1d | Rim ends walled, jump back up | south end walled and safe; climb from the rim (14202, 19700, 8) to the platform (14250, 19700, 48) with SPACE; **walking north along the rim into the new north wall drowned the Avatar in the gate pool, 2 of 2** (finding 1) | **PARTIAL** (north end FAIL) |
| C1e | NW corner refuses a push west | last session's fatal NW push and three more stop at x 14144..14148, z 48 | **PASS** |
| C1f | Plates; 0 paint cycles | avenue oaks, main gate threshold, both harbour walls plated; a doorway threshold cannot be seen from the camera (finding 5); 0 `Cycle in paint` while the Avatar lived, 17 after the session 2 drowning | **PARTIAL** |
| C2 | Map 17 NE tapestry visible in full | tapestry 5003 at (5847, 5121, 0) shows with its emblem whole; the bottom 7 or so of its 52 rows sit behind the east wall's south segments (finding 6) | **PARTIAL** |
| B1a | Split onto the bag's floor does not grow the frame | 13 + 12 in the bag, total 25 for 78 s (last session: 25 to 50 in 38 s) | **PASS** |
| B1b | Partial drag to ground refills 5 per poll to 25 | 13, 18 (7.1 s), 23, 25; ground stack 12 throughout; two-stack case 17, 22, 25 | **PASS** |
| B1c | Whole frame to the ground is recreated at 5 | new stack inside the bag at 5, then 10, 20, 25; ground stacks untouched | **PASS** |
| B1 checkpoint | "usecode behaviour, so a checkpoint is fine" | the 10-03 checkpoint resumes a top-up process from the old bytecode; under it a partial drag refilled 13 to 25 in one poll (finding 2) | **FAIL** (premise) |
| D1 | Hall rock visible from the hall approach; sanctum view | rock 5266 at (2975, 5631, 0) visible, its base on the wall's top-edge line (finding 7); sanctum side with the breach open plated | **PASS** |
| N | Nudge exactly once per hatch | visit 1: three observations then the nudge once; visit 2: the nudge once, no observation; trace resumes at offset 713 once per hatch | **PASS** |
| D2 | Observation barks and their once-only guard | three barks in order on the first hatch, flag 0 to 1; none on two later hatches; visit 3 without potions silent | **PASS** |
| A1 | Leaving Map 41 kills Aramina's atHome | `resetRef item=13` for 0x205, 0x204, 0xF0, 0x200; no item-13 process after; 0 `Invalid item 1037` | **PASS** |
| L | Log health, seven sessions | 0 `Non-existent process`, 0 `stuck`, 0 segfaults, 0 assertions; 17 `Cycle in paint` after a death; 3 unhandled `getNpcSlot` | **PASS** (lines attributed) |

## Method and harness writes

Saves (48 files, md5 list) and `scummvm.ini` (`a143fa3b`) were copied to the
session scratchpad first and restored at the end; `md5sum -c` passes on all
48 and the ini reads `a143fa3b` again. `./install_lv.sh` exited 0. The first
`session.sh start` synced EUSECODE (`2efc9e91` to `c9716c73`) and both
FIXED.DAT copies (`7650fba3` to `e8800ad0`) into `shared/u8-lv-patched/`.
Seven sessions, one ScummVM pid each. Devon's opening menu was closed at each
fresh start by clicking **Goodbye** from the screen.

Writes, all disclosed:

- **Teleports with cheats on**, each followed by `Cheat::toggle` back to
  `Cheats = false` (checked in the log) before any movement. Sessions 1 to 3
  are fresh worlds. Session 1: Map 39 (15600, 20040, 48). Session 2: Map 39
  (20550, 19300, 48), (17390, 19880, 48), (15660, 19340, 48), (15150, 19400,
  48) twice, (16170, 19400, 48), (14244, 19428, 48), (14170, 19700, 8),
  (14040, 19700, 8). Session 3: Map 39 (20550, 19300, 48), Map 17 (5950,
  5450, 0), Map 18 (2852, 5300, 0), Map 41 (16671, 19200, 48). Sessions 5 and
  6: Map 10 (18432, 22680, 0).
- **Checkpoint loads** through slot 1: `godsfree-at-exit-map18-2026-09-29.sav`
  (sessions 4 and 6), `~/lv-checkpoints/run-s16-tinytar.sav` (session 5),
  `~/lv-checkpoints/bag-q1-map10-2026-10-03.sav` (session 7).
- `Ultima8Engine::saveGame 1` once, after this build's bag hand-over (session
  4); copied to the scratchpad as `bag-q1-newproc-map10-2026-10-04.sav`.
- `CameraProcess::moveToAvatar` once (run-s16's parked camera).
- `UCMachine::traceClass 1457` and `stopTrace`, three times (session 5).
- `debugflag_enable Object` in every session; reads: `objectInfo`,
  `findShape`, `getGlobal`, `Kernel::listProcesses`.
- In-world: reagent drags and splits (B1), three potion drops on Map 10.

Every egg tested here hatched from a walk: the Map 18 exit trigger into
Map 10 (session 4, endgame scene and top-up spawn), trigger 211 into Map 18
four times, and the crack hint three times. In session 6 the endgame egg
hatched on a teleport arrival; that session served only the D1 sanctum view.
Every menu answer was clicked from the screen. Map 39, 17, 18, and 41
geometry was judged in fresh worlds; the D1 sanctum view re-entered Map 18
through trigger 211, so its items came from the current FIXED.DAT.

## C0: build, hashes, estate, PASS

- `tools/run_all_tests.sh`: `OVERALL: PASS — 37/37 test file(s)`.
- `tools/build_artifacts.sh`: exit 0; `TYPEFLAG.DAT OK 9f534e59`,
  `U8SHAPES.FLX OK a611e9be`, `EUSECODE.FLX OK c9716c73`, `FIXED.DAT OK
  e8800ad0`; all 14 teleport pairs verified.
- Compilation Report: 48 files, 46 succeed, failures `EALOGO.UNK` (line 14,
  unterminated block comment) and `TJORVI.UNK` (line 575, unterminated
  string), the `DEV_ALLOWLIST` pair; 508 warnings, none in `ENDGAME.UNK` or
  `CRACKHNT.UNK`.
- Fork: `lost-vale` tip `e0d6084d`; the patch-equality `diff -q` printed
  nothing. No fork commit in this change.

## C1a: previous void routes, PASS

**Rim route.** Session 1, from the lane on foot: west to (14136, 20040, 48),
south off the platform's open column to the rim at (14136, 20173, 8)
(`C1d-01-rim-drop-from-platform.png`), then south along the rim strip:
(14064, 20325, 8), (14064, 20461, 8), (14040, 20477, 8), then no further
movement. The Avatar stands half hidden behind the new south wall's east end
(`C1d-02-rim-south-end-at-wall.png`). Diagonal pushes south-east and
south-west stopped at (14072, 20477, 8) and (14008, 20477, 8)
(`C1d-03-rim-south-end-diagonals.png`). Last session the same walk reached
(14064, 20812, 0).

**Avenue route.** Last session's start point (20896, 19300) is now inside oak
(20990, 19440), box x 20702..20990, y 19152..19440. A 3 s east push from
(20550, 19300, 48) stopped at (20702, 19276, 48); north-east and south-east
pushes did not move him (`C1b-y19300-push-east.png`).

## C1b: avenue east edge, PASS

From x ~20500, a 3 s east push and 1.5 s north-east and south-east pushes at
each y:

| y | East push stops at | Lowest z |
|---|---|---|
| 19300 | (20702, 19276) | 48 |
| 19100 | (20670, 19108) | 48 |
| 18850 | (20702, 18812) | 48 |
| 18600 | (20690, 18592) | 48 |
| 18350 | (20698, 18328) | 48 |
| 18100 | (20682, 18072) | 48 |
| 17960 | (20690, 18008) | 48 |

Plates `C1b-y<y>-push-east.png` for each row and `C1f-01-avenue-oaks.png`.
The north-east pushes from y 18100 and 17960 slid past the last oak to
(20834, 17720, 48) and (20922, 17680, 48), north of the y 17922 closure end;
the brief puts that stretch out of scope and it was not pushed further.

## C1c: doorways and main gate, PARTIAL

**Main gate, PASS.** From the courtyard at (17390, 19880, 48), east of the
egg's box (x 17022..17278, y 19572..19828), north in 1 s bursts: (17390,
19680), (17330, 19524), (17330, 19492), then no movement; z 48 at every
read (`C1c-02-main-gate-threshold.png`, `C1c-03-main-gate-stop.png`). The
raised bridge (shape 565, z 80..88, y 19295..19423) stops a body at z 48,
and the lintel (z 96 from y 19423) keeps a climb off it. Negative control:
west along the threshold to the jamb, (16962, 19564, 48), then north,
north-west, and north-east pushes; all z 48. The east-bound push slid along
the gate wall's south face out to (20262, 19560, 48) without a drop. The LB
egg did not hatch (no `05AF` event in the log).

**The three small doorways cannot be walked from the lane.** Each is a niche
in the inner gate wall, open north to the city across the threshold strip
and closed on its south side by a wall course at y 19583..19615, z 48..136
(doorway 1: shapes 13, 15, 12 from x 14975 to 15231). Between the inner wall
and the outer wall (y 19935..19967, solid at z 48 from x 14335 to 17540 save
post gaps narrower than the body) there is no z 48 floor west of the
courtyard's own wall at x 16863..16895. An `exact_reach` flood from the lane
at (15600, 20040, 48) reaches the courtyard from x ~16944 east and none of
the niches. `C1c-01-lane-x15600-outer-wall-north.png` shows the outer wall
directly north of the lane at x 15600. Finding 3.

**From the city side each doorway holds.** Fresh world, teleport into the
city north of each doorway, walk south into the niche, push at the jambs,
walk back north:

| Doorway | Rest points over the strip (bottom centre y 19455..19487) | Lowest z |
|---|---|---|
| 2, x 15660 | passed through at walking pace both ways | 48 |
| 1, x 15150 | (15150, 19504, 48), still at z 48 two seconds later | 48 |
| 3, x 16170 | (16170, 19504, 48), still at z 48 two seconds later | 48 |

Negative control, offline: with the ten slabs removed from the shipped
FIXED.DAT, `ExactReach.mask(48)` reads False at (15150, 19504), (15660,
19504), and (16170, 19504); with them in, True. The same check at the main
gate reads True either way (finding 4).

## C1d: harbour rim, PARTIAL (north end FAIL)

South end: walled and safe (C1a above). The climb back: Avatar on the rim at
(14202, 19700, 8) after a 1 s walk east into the platform face; with the
cursor east and no direction held, SPACE held 0.6 s took him to (14250,
19700, 48) on the platform.

North end, run 1 (session 1, from the rim at (13984, 20061, 8), 1.2 s north
pushes at running pace): (13984, 19765, 8), then (13892, 19523, 1) and hp 0,
in the gate pool (x 13823..13951), followed by the death book
(`C1d-04-run1-after-north-push-in-pool.png`, `C1d-05-run1-death-book.png`).

North end, run 2 (session 2, from (14040, 19700, 8), 0.8 s walking pushes,
due north each time): (14040, 19604, 8), then (14020, 19584, 8), (14000,
19564, 8), then hp 0 (`C1d-07-walk2-fourth-push-dead.png`,
`C1d-08-walk2-gravestone.png`). The Avatar is under the gate wall's mass in
these frames; the positions and hp come from `objectInfo 1`. Finding 1.

## C1e: platform NW corner, PASS

From (14244, 19428, 48), last session's fatal 2 s north-west push, then
west 2 s, south-west 1.5 s, north 1.5 s, west 2 s, north-west 2 s: (14148,
19428, 48), (14148, 19428), (14128, 19576), (14144, 19440), (14144, 19440),
(14144, 19440). Lowest z 48. x 14144 puts the body's west edge on the new
fence's east face (x 14079). The Avatar stands under the roof slab, so
`C1e-01-platform-nw-corner-push-west.png` shows the harbour's north wall
from the south and not him.

## C1f: plates and paint cycles, PARTIAL

- Avenue oaks: `C1f-01-avenue-oaks.png`.
- Main gate threshold: `C1c-02-main-gate-threshold.png`, pale slabs under
  the arch with the Avatar on them.
- Harbour south wall: `C1d-02-rim-south-end-at-wall.png`.
- Harbour north wall: `C1f-02-harbour-north-wall-from-rim.png` and
  `C1e-01-platform-nw-corner-push-west.png`.
- Doorway threshold: **not demonstrated.** `C1c-05`, `C1c-06`, and `C1c-07`
  were taken with the Avatar on the strip and show only wall (finding 5).

`Cycle in paint dependency graph`: session 1, 0 in 1,845 lines; session 2,
17, all at log lines 4547..4563, after the Avatar read hp 0 at (0, 0, 0),
all `476 -> 580 -> ... -> 476`. The death gump blocked the console. In a
fresh session with the same load order, `objectInfo 476` answered `Reserved
objid: 476` and `objectInfo 580` answered `No such object: 580`, so neither
is a map item in that world. I attribute the lines to the death sequence,
about two chances in three; session 1's drowning produced none.
(Corrected in Round 2: the message prints shape numbers, not object ids,
so the `objectInfo` reading above tested the wrong thing. Shapes 476 and
580 are the drowning's ripple and spark sprites.)

## C2: Map 17 NE tapestry, PARTIAL

`findShape 329` lists item 5003, frame 5, at (5847, 5121, 0). From (5950,
5450, 0) the tapestry shows right of the lamp, dark folds and the gold
emblem (`C2-01-ne-tapestry-from-5950-5450.png`). Last session's plate showed
bare wall at that spot.

Measured against frame 5 rendered from the shipped `U8SHAPES.FLX` (24 x 52
px): the in-engine sprite shows 17.5 px from its top to the emblem (the
frame has 18) and 9 px below the emblem (the frame has 16). The bottom 7 or
so rows are behind a wall top. The occluders are the east wall's two
southern segments, shape 10 at (6143, 5503) and (6143, 5631), x 6111..6143,
y 5375..5631, z 0..80, screen columns x - y 480..768, in front of the
tapestry's 630..726. `build_map_17.py:361-366` checks the tapestry against
the segment at y 5119..5375 only. Finding 6.

## B1: reagent bag cap, PASS

**Getting a process from this build.** The 10-03 checkpoint cannot test B1
(finding 2), so the bag came from Ezrekal in this build. The 09-29 save
(Map 18 at the exit, `godsFree` 1, `endgameStarted` 0, `hasBag` 0): a walk
north loaded Map 10 0.70 s in, the endgame scene played, and the new
bytecode spawned the top-up as process 784 (`EGGENDGA`, `05AA:04E6`). Last
session's route to the stockade, a double-click on Ezrekal, menu
(`B1-01-ezrekal-menu.png`, overwritten and lost in Round 3; `R3-01` shows the same menu): **I have freed your gods!** Afterwards `hasBag`
1, bag 15316 reads `q: 1`, six shape-395 stacks of 25, frames 0, 6, 8, 9,
10, 14 (`B1-03-after-handover.png`). The bag opens with all six drawn as one
pile at its top-left, as last session (finding 7 there).

| Test | Action | Readings (`findShape 395`) | Result |
|---|---|---|---|
| B1a | 12 of frame-10 stack 1665 dropped on the bag's own floor (`SplitItemProcess splitting: 12: 13-12`, `B1-07-T5-slider-12.png`) | 1665 at 13 and new 7321 at 12, both inside the bag, at every read from 7.1 s to 78.2 s (`B1-08-T5-after.png`) | frame 10 total stays 25 |
| B1b | 12 of frame-14 stack 1395 to the ground at (12978, 12634, 0) | 1395: 18 (7.1 s), 23 (15.3 s), 25 (23.4 s), then 25 to 74.2 s; ground 8359 at 12 throughout (`B1-10-T1-after.png`) | 5 per poll to 25 |
| B1b, two stacks | 8 of 7321 to the ground (`8: 4-8`, `B1-11-T6-slider-8.png`) | bag total 17 (1665 13, 7321 4), 22 (7321 9), 25 (7321 12), then 25 to 62.4 s; 1665 stays 13; ground 3829 at 8 | one stack takes the refill; the cap lands on 25 exactly |
| B1c | all 25 of 1395 to the ground (`25: 0-25`) | no frame 14 in the bag at 5.3 s; new 4396 inside the bag at 5 (13.5 s), 10, 20, 25 (37.9 s), then 25 to 70.6 s; ground 1732 at 25 and 8359 at 12 (`B1-13-T4-after.png`); bag holds 7 items | recreated at 5 |

B1a's second stack is the negative control for last session's farm; B1b's
ground stacks are the controls that nothing outside the bag is written.

## D1: hall rock and sanctum view, PASS

Session 3, fresh world, Map 18 at (2852, 5300, 0): `findShape 526` lists
the hall rock 5266 at (2975, 5631, 0), frame 6, and the chips 8230, 8231,
8232 at z 0. The rock is visible (`D1-01-hall-approach-y5300.png`), and with
the Avatar beside it at (3060, 5540) (`D1-02-hall-rock-beside-avatar.png`).
Its base lands exactly on the breach wall's top-edge line (finding 7).

Sanctum side, breach open: session 6, `templeOpen` 1, Map 18 entered on foot
through trigger 211. On the walk south `findShape 15` listed no `q: 307`
wall pieces, so the doorway egg had reopened the breach. From the hall
(`D1-03-breach-open-from-hall.png`) and from the sanctum at (2852, 6452, 0)
and (2576, 6528, 0) (`D1-04-rubble-from-sanctum-breach-open.png`,
`D1-05-rubble-from-sanctum-west.png`): the gravel spill and grey piles lie
on both sides of the gap, nothing floats, nothing is buried. In `D1-04` the
large green figure in front of the Avatar is item 13462, shape 860 frame 4
(`TYPEZEAL`) at (3072, 6656, 0), a Zealan god figure. 0 `Cycle in paint`
in session 6.

## N and D2: crack hint barks, PASS

`run-s16-tinytar.sav`: Map 10, `templeOpen` 0, `crackHintGiven` 0, three
frame-8 potions (3963, 8603, 14459) in the pack. Each visit walked through
trigger 211, along the hall to (2852, 5628), and south onto the crack egg
with `traceClass 1457` on, filming one frame a second. In the new class the
three observation barks suspend at 0x180, 0x1E3, and 0x221 and the nudge at
0x2C8, followed by `ret` at 0x2C9 (713).

| Visit | Carrying | Hatch | Trace (offsets the process ran from) | Film | `crackHintGiven` |
|---|---|---|---|---|---|
| 1 | three potions | egg 1221, `event 7 @ 05B1:0080` | 128, 385, 484, 546, 713 | "The stone here is split..." frames 2-9, "Grit has sifted down..." 10-17, "But the gap is no wider than my hand." 18-21, the nudge 22-31, silent 32-57 | 0 to 1 |
| 2 | three potions | egg 15108 | 128, 713 | the nudge frames 1-11, silent 12-57 | 1 |
| 3 | none (dropped on Map 10) | egg 12671 | 128 | silent, 58 frames | 1 |

Plates: `D2-01` to `D2-03` (visit 1's observations), `N-01-v1-nudge.png`,
`N-02-v1-silent-after-nudge.png`, `N-03-v2-nudge-only.png`,
`N-04-v2-silent-after.png`, `N-05-v3-no-potions-silent.png`,
`D2-04-potions-dropped-on-map10.png`. Visit 2 is the control for the once-only
guard; visit 3 is the control for the potion test. Each visit left Map 18 on
foot by the north exit and came back through trigger 211.

## A1: Map 41 Aramina, PASS

Session 3, fresh world, (16671, 19200, 48), walk north to (16611, 17540):
Aramina's processes up (0x217 at `040D:01F0`, 0x205 at `040D:0704`, two
pathfinders and an anim process for item 13;
`A1-01-aramina-fast-area-in.png`). Walk south to (16695, 19512): the log
gained `LV: I_resetRef item=13` for 0x0205, 0x0204, 0x00F0, 0x0200, twice
(two crossings of the fast-area edge), and `Kernel::listProcesses` listed no
item-13 process (`A1-02-aramina-out-of-fast-area.png`). 0 `Invalid item 1037`.

## L: log health, PASS (lines attributed)

| Session | Content | Lines | Non-existent | stuck | Segmentation | Assertion | Cycle in paint | Invalid 1037 | Unhandled |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Map 39 rim (drowned) | 1,845 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | Map 39 (drowned) | 4,563 | 0 | 0 | 0 | 0 | **17** | 0 | 0 |
| 3 | Map 39, 17, 18, 41 | 2,924 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | endgame, bag, B1 | 1,839 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| 5 | crack hint, three visits | 9,081 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 6 | breach open, sanctum | 2,548 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 10-03 checkpoint | 387 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

The 17 paint cycles are C1f's, after a death. The three unhandled
intrinsics are `Npc::getNpcSlot()` for item 116, Ezrekal's conversation, as
last session. No `stuck in process loop` line in any session.

## Findings outside the plan

1. **The harbour's new north wall walks a player into the gate pool.** Two
   of two attempts died: running north along the rim, and walking north.
   `U8AvatarMoverProcess::step()` (`u8_avatar_mover_process.cpp:663-695`)
   answers a failed step by trying one direction right (north-east, the
   platform's west face, solid) and then one left (north-west); a walk or
   run that ends off land is accepted. The north step fails about 150 units
   short of the wall, each north-west side-step moves the Avatar about 20
   west, and the rim strip is 128 wide with deadly water (shape 347,
   `SI_SEA`) along its west side, so three presses put him in the pool.
   Before this change the rim ended at y 19455 with nothing north of
   it at x 13951..14079, a fall to z 0. A player who falls onto the rim and
   heads north, the natural way out, now drowns. The south wall
   does not do this: there both diagonals are blocked by the same wall
   (C1a). Sure of the deaths and positions; the mechanism is my reading of
   the mover, about four chances in five.
2. **The 10-03 bag checkpoint cannot test the new cap, and neither can any
   save taken after the endgame on an older build.** The top-up is spawned
   once and lives in the save's process list. Loading
   `bag-q1-map10-2026-10-03.sav` restores process 632 at `05AA:04E6`. That
   offset is the same instruction in both builds (the loop head after
   `wait(200)`), but the old routine opens with `init 10h` and the new one
   with `init 16h`, and the new code reads and writes `[BP-12h]`,
   `[BP-14h]`, and `[BP-16h]` (`stack` and `total`), below the restored
   frame. In the engine, under that process, 12 of frame 14 to the ground
   gave 13 then 25 in one poll (5.3 s to 14.4 s), where this build's own
   process gave 13, 18, 23, 25 (B1b). The split-onto-floor case held at 25
   under it, which I read as luck of the clobbered values. Sure of the
   readings; the clobbering is inference from the bytecode, about four
   chances in five. A checkpoint with a process from this build is at
   `<scratchpad>/sp/bag-q1-newproc-map10-2026-10-04.sav` (Disk changes).
3. **The three small doorways are reachable only from the city.** Each
   niche's south side is a full wall course (y 19583..19615, z 48..136),
   and the strip between the inner and outer walls west of x 16863 has no
   z 48 floor. C1c's "walking north from the lane through each of the three
   small doorways" cannot be done; the slabs protect a player walking from
   the city into a niche, which is what was tested. The `exact_reach`
   reach map is in the C1c section. Sure.
4. **The main gate's four slabs fill a strip that already had floor.**
   Retail grass (shape 3, frames 26 to 28) at y 19583 covers y 19455..19583
   for x 16895..17407, and `ExactReach.mask(48)` reads True at (17330,
   19492) and (17150, 19500) with the slabs removed. They are harmless and
   show as pale paving under the arch (`C1c-02`). The builder comment
   (`build_map_39.py`, `TENEBRAE_GATE_THRESHOLDS`) says the main gate's
   strip had no floor. Sure.
5. **A doorway threshold cannot be plated in the engine.** The niche lies
   under the wall walk and its south side is a full wall, so the camera
   sees wall whether the Avatar stands in the niche or north of it. C1f's
   doorway shot needs another kind of evidence, such as the offline mask
   check in C1c. Sure.
6. **The tapestry's bottom rows are behind the east wall's south
   segments** (C2). The span check in `build_map_17.py:361-366` covers the
   segment at y 5119..5375; the segments at y 5375..5631 cover screen
   columns 480..768 and overlap the tapestry's 630..726. Moving it so its
   columns end below 480, or lower than the wall top, is the author's call.
   Sure of the plate and the rows; the occluder is arithmetic on the item
   boxes, about four chances in five.
7. **The hall rock reads as lying on the parapet.** At 480 units north of a
   120-tall wall, the rock's base projects onto exactly the wall's top-edge
   line (480 / 4 = 120 screen rows), and that relation is fixed for every
   camera position (`D1-01`). With the Avatar beside it the floor reading
   comes back (`D1-02`). Judgement.
8. **The harbour south wall's frame selector never fires.**
   `TENEBRAE_HARBOUR_SOUTH` picks frames with `x % 256 == 159`; the four x
   are 13695, 13823, 13951, and 14079, whose remainders are 127 and 255. So
   every z 48 course is shape 15 frame 3 and every z 96 course frame 1.
   Frames 2 and 3 carry grass tufts at the base, so a tuft line runs along
   the middle of a wall that faces the black band (`C1d-02`). Cosmetic. Sure.
9. **Hrodny's chest refills on Map 10 reloads.** In session 5, after two
   Map 18 round trips and with the original three potions in the pack and
   then on the ground, `findShape 859` listed three more frame-8 potions at
   container position (255, 255) with `ef: 0x9`. At load there were none.
   That confirms last session's finding 12 guess: the potions can be
   multiplied by leaving and re-entering Map 10. Predates this change. I
   did not read the container's id; last session tied these items to
   `build_map_10.py:800-830`.
10. **One north-east push from the last avenue oak reaches the edge north
    of the closure** (C1b: (20922, 17680, 48) from y 18008). The drop there
    is on the brief's out-of-scope list; noted because it sits about 300
    units from the end of the new oak line.

## Harness anomalies

1. Short bursts only turn the Avatar: 0.6 s at offset 110 and 0.35 s at
   offset 110 moved nothing; 0.55 s at 130 and longer did.
2. A `route()` in session 2 thrashed for 300 s on the avenue and was killed;
   the position after it was fine.
3. `CameraProcess::moveToAvatar` through the console helper leaked an `i`
   and opened the pack (the known trap); closed with `i`.
4. `objectInfo` for a reserved or missing id answers `Reserved objid` or
   `No such object`, which the helper's regex does not match, so it
   reported "no reply" twice; the answers were in the log.
5. Session 6's teleport to Map 10 hatched the endgame egg on arrival; the
   scene was waited out (150 s) before any input.
6. Held SPACE climbed on the first try (C1d), where last session's three
   held presses did nothing; the difference is the cursor in the facing
   direction with no direction held, which `run()` needs (`:506-530`).

## Disk changes

- `docs/playtest-2026-10-04-batch-retest.md` (this record) and 47 plates in
  `docs/playtest-2026-10-04-batch-retest/`.
- `shared/build/` rebuilt by `tools/build_artifacts.sh`: byte-identical to
  the recorded hashes, new mtimes.
- `shared/data/u8-install/` rewritten by `./install_lv.sh`.
- `shared/u8-lv-patched/`: EUSECODE `2efc9e91` to `c9716c73` and both
  FIXED.DAT copies `7650fba3` to `e8800ad0`, synced by `session.sh start`.
- `~/.local/share/scummvm/saves/ultima8.001` overwritten four times by
  checkpoint copies and once by `saveGame 1`, then all 48 files restored;
  `md5sum -c` passes and no new save file remains.
  `~/.config/scummvm/scummvm.ini` restored (`a143fa3b`).
- Scratch only, under
  `/tmp/claude-1000/-home-douglas-projects-lost-vale/3b99e1ce-cfb9-4426-91ac-2a8e98a8eca2/scratchpad/`:
  the backup, seven session logs, drivers, film frames, the new
  disassemblies of 0x5AA and 0x5B1, and
  `sp/bag-q1-newproc-map10-2026-10-04.sav` (Map 10 at the stockade, bag
  15316 with `q: 1`, top-up process from this build).
- No tracked file modified; the author's uncommitted edits are untouched.
  `TODO.md` not touched.

## Round 2 (2026-10-04)

Change under test: the same tree plus a round of fixes. FIXED.DAT
`079829c1...`; EUSECODE unchanged at `c9716c73...` (1,507,239 bytes, first
5000 bytes md5 `4f47de88...`). `tools/build_artifacts.sh` exit 0 with all
four OK (`FIXED.DAT OK 079829c1`); `tools/run_all_tests.sh` 37/37;
Compilation Report 46 of 48 (`EALOGO.UNK`, `TJORVI.UNK`); `./install_lv.sh`
exit 0. The fork tip is still `e0d6084d` and the patch-equality `diff -q`
printed nothing; `scummvm-lv/scummvm` (2026-10-04 00:12 CDT) postdates it and
its detection entry still reads `4f47de88..., 1507239`, which is unchanged
because EUSECODE is. `session.sh start` synced both FIXED.DAT copies into
`shared/u8-lv-patched/` (`079829c1`); the session log reads `4f47de88...,
1507239 bytes`. One session, one fresh world, one ScummVM pid. Plates are
the `R2-` files in the same folder, 640x400.

### Round 2 verdicts

| ID | Claim | Observed | Verdict |
|---|---|---|---|
| C1d | Walking and running into either harbour wall from several x never puts the Avatar in the pool; both fatal approaches repeated; climb still works | run 1 replayed input for input: stops at (14076, 19520, 8), 11 presses after the stop, no move west; run 2 and a sweep at x 14048, 14064, 14079, walking and running, north and south: 12 of 12 end against the wall at z 8, lowest x 14048; climb (14202, 19700, 8) to (14250, 19700, 48) | **PASS** |
| C1f | Plates of the railing and both walls; 0 paint cycles; last round's 17 lines | three plates; 0 `Cycle in paint` in 6,514 lines; last round's lines were shapes 476 and 580, the drowning's ripple and spark sprites | **PASS** |
| C1c | City-side niches hold z 48 over the strip; main gate stops at the bridge | all three doorways now rest over the strip at z 48 (doorway 2 this round, 1 and 3 last round); main gate stops at (17330, 19492, 48) on this FIXED | **PASS** |
| C2 | Tapestry at x 4607 visible in full | item 6445, frame 5, at (4607, 5121, 0); the whole frame shows, its bottom on the floor line; no solid in front of its columns | **PASS** |
| D1 | Hall rock at (2975, 5503) visible and lying on the hall floor | rock 2370 at (2975, 5503, 0) shows on floor tiles with a band of floor between it and the wall's top edge | **PASS** |
| C1a | Rim route stops at the south wall | (14060, 20472, 8), then five presses and four diagonals with no movement | **PASS** |
| C1e | North-west corner | the six pushes from (14244, 19428, 48): lowest z 48, lowest x 14128 | **PASS** |
| L | Log health | 0 `Non-existent process`, 0 `stuck`, 0 segfaults, 0 assertions, 0 `Cycle in paint`, 0 `Invalid item 1037`, 0 unhandled intrinsics; the LB egg never hatched | **PASS** |

### Round 2 method and harness writes

Saves (48 files, md5 list) and `scummvm.ini` (`a143fa3b`) were copied to
`<scratchpad>/r2bak/` first and restored at the end; `md5sum -c` passes on
all 48, the file names match, and the ini reads `a143fa3b`. Devon's opening
menu was closed by clicking **Goodbye**. Writes:

- **Teleports with cheats on**, each followed by `Cheat::toggle` back to
  `Cheats = false` (the log's last toggle line reads false after every
  batch). Map 39: (14600, 20060, 48); for the sweep, (x, 19700, 8) and
  (x, 20250, 8) at x 14048, 14064, and 14079, four teleports per x; plates
  at (14064, 20300, 8), (14064, 19720, 8), (14260, 19950, 48); climb at
  (14170, 19700, 8); (14244, 19428, 48); (15660, 19400, 48); (17390, 19880,
  48); (14048, 19900, 8). Map 17 (4710, 5450, 0). Map 18 (2852, 5300, 0).
- `debugflag_enable Object`; reads: `objectInfo`, `findShape`.
- No checkpoint load, no save, no trace, no item writes.

No egg is under test this round. Every map claim was judged in the one fresh
world.

### C1d: harbour rim, PASS

The railing is eight shape-130 panels at x 13951..13983, z 8..48, covering
y 19455..20479 without a gap, flush with the north wall (y 19423..19455) and
the south wall (y 20479..20511). A body on the rim now has x 14047 at least.

**Run 1, replayed input for input.** From (14600, 20060, 48): walk to
(14136, 20060, 48), south 1 s pushes until the drop to (14136, 20172, 8),
route toward (14070, 20200), south 1 s pushes to the south wall, four 1.5 s
diagonal and west pushes, route toward (14050, 20420), north 1.2 s pushes at
running pace, the north-east and north-west 1.5 s pushes, then north 1.2 s
pushes again. Positions: south wall stop (14060, 20472, 8); north run
(14060, 20208), (14060, 19808), (14060, 19576), (14060, 19544), (14076,
19520, 8), then three presses, the two diagonals, and nine more north
presses with no movement (`R2-C1a-01-rim-south-wall-stop.png`,
`R2-C1d-01-run1-north-end.png`). The side-step that last round went
north-west into the pool went north-east by 16 units.

**Run 2.** Last round's teleport point, (14040, 19700, 8), now overlaps the
railing (a body there spans x 13976..14040), so the sweep's x 14048 is run 2
moved east by the eight units the railing takes. Each row is a teleport, 3 s
settle, then presses in one direction until the Avatar stops, plus six or
more presses after the stop:

| x | Walk north (0.8 s) | Run north (1.2 s) | Walk south (0.8 s) | Run south (1.2 s) |
|---|---|---|---|---|
| 14048 | (14048, 19532, 8), 9 presses | (14068, 19520, 8), 10 | (14048, 20474, 8), 10 | (14076, 20478, 8), 10 |
| 14064 | (14064, 19532, 8), 9 | (14064, 19540, 8), 9 | (14064, 20474, 8), 10 | (14048, 20474, 8), 10 |
| 14079 | (14079, 19532, 8), 9 | (14059, 19520, 8), 10 | (14079, 20474, 8), 10 | (14059, 20470, 8), 10 |

hp 30 and z 8 at every read; the lowest x seen in any row is 14048.

**Climb back.** Teleport to the rim at (14170, 19700, 8), a 1 s walk east
to (14202, 19700, 8), cursor east, SPACE held 0.6 s: (14250, 19700, 48)
(`R2-C1d-02-climb-back-onto-platform.png`).

**Adversarial, outside the claim.** At the railing, (14048, 19900, 8),
facing west: SPACE held with the cursor west left him in place, and three
both-button presses with the cursor on the pool at (13880, 19900) left him at
(14048, 19900, 8), hp 30 (`R2-X-01`, `R2-X-02`). The railing also stops a
deliberate jump toward the water.

### C1f: plates and paint cycles, PASS

- `R2-C1f-01-railing-and-south-wall.png`: the south wall's face and the
  wooden railing along the pool, from the rim at (14064, 20300, 8); the
  Avatar is behind the oak row in this view.
- `R2-C1f-02-railing-and-north-wall.png`: the railing running up to the
  north wall, the Avatar on the rim at (14064, 19720, 8).
- `R2-C1f-03-railing-from-platform.png`: the Avatar on the platform at
  (14260, 19950, 48), the railing between the rim and the pool, the south
  wall at left.

FIXED.DAT lists every z 48 course of the south wall as shape 15 frame 2 and
the z 96 courses as frames 1, 0, 1, 0 from west to east. Frame 2 carries
grass tufts at its base like frame 3, so the tuft line at z 48 is still
visible on the south face in `R2-C1f-01`; retail's own gate wall uses frame 2
at that course. Cosmetic, noted for the record.

`Cycle in paint dependency graph`: 0 in the session's 6,514 lines, which
covered Map 39 throughout (all runs, the sweep, plates, both jumps), then
Map 17 and Map 18.

**Last round's 17 lines.** `ItemSorter::PaintSortItem` prints the two sort
items' **shape** numbers (`item_sorter.cpp:414`, `si->_shapeNum,
d->_shapeNum`), so last round's `objectInfo 476/580` reading tested the
wrong thing. Shape 476 is a seven-frame expanding blue ripple ring (footpad
11x11x1, no flags) and shape 580 a 120-frame spark sprite
(`SHAPE_PLACEHOLDER_MAGIC_BURST_VFX`, `lv_shapes.py:784`). Map 39 places
neither (0 instances in FIXED.DAT), and the Avatar is shape 1. The cycle was
between two effect sprites the engine spawned for the drowning: neither the
corpse nor any placed item. Sure of the shapes; that the engine spawns these
two on a water death is inference from their art and their absence from the
map, about four chances in five.

### C1c, restated: PASS

Last round already showed doorways 1 and 3 holding with the Avatar at rest
over the strip and the main gate stopping at the bridge, on FIXED
`e8800ad0`. Because FIXED changed, both were spot-checked on `079829c1`, and
doorway 2, which last round only crossed at walking pace, was given the rest
test:

- Doorway 2: from (15660, 19400, 48), short bursts south: rest at (15660,
  19504, 48), bottom centre (15628, 19472) over the strip, still z 48 two
  seconds later; then into the niche to y 19576 and back out
  (`R2-C1c-01-doorway2-threshold.png`, wall only, as finding 5 explains).
- Main gate: from (17390, 19880, 48): (17390, 19680), (17330, 19524),
  (17330, 19492), stopped, z 48 throughout
  (`R2-C1c-02-main-gate-stop.png`).

Last round's offline control still stands: without the slabs the three
doorway rest points are not standable at z 48.

### C2: Map 17 tapestry, PASS

`findShape 329` lists item 6445, frame 5, at (4607, 5121, 0), between the
lamp and plaque 70. From (4710, 5450, 0) the tapestry shows on the north
wall west of the doorway (`R2-C2-01-tapestry-west-of-doorway.png`).
Measured at 6x against frame 5 rendered from the shipped FLX: top to emblem
17.5 px (the frame has 18), emblem bottom to tapestry bottom 15 px (16),
which is within a pixel, and its bottom edge sits on the floor line with no
wall top across it. Offline, no solid item taller than 8 stands in front of
its screen columns (x - y -610..-514).

### D1: hall rock, PASS

`findShape 526` lists rock 2370, frame 6, at (2975, 5503, 0), and the three
sanctum chips at z 0 as before. From (2852, 5300, 0)
(`R2-D1-01-hall-rock-from-y5300.png`) the rock lies on the hall's floor
tiles with a band of floor between its base and the breach wall's top edge.
At 608 units north its base projects 152 rows above the wall's base line,
32 above the 120-tall wall's top edge, where last round's 480 put it exactly
on that edge.

### C1a and C1e regression: PASS

C1a: the run 1 replay's first half is the rim route, stopping at (14060,
20472, 8) (C1d above). C1e: the six pushes from (14244, 19428, 48) gave
(14180, 19428), (14148, 19428), (14128, 19576), (14200, 19504), (14144,
19440), (14144, 19440), all z 48 (`R2-C1e-01-nw-corner-push-west.png`).
The lowest x, 14128 at y 19576, is on the platform's own 94 tile
(x 14079..14207, y 19455..19583).

### Round 2 findings

1. **Last round's paint-cycle attribution used the wrong id space** (C1f
   above); the conclusion, death-time effects and no placed item, stands
   with a better reason. A one-line correction was added under last round's
   C1f section.
2. **The z 48 tuft line on the harbour south wall remains** with frame 2
   (C1f above). Cosmetic.
3. **Run 2 cannot be repeated at its exact x.** The railing occupies part of
   the body box at (14040, 19700); x 14048 is the nearest legal start, and
   the sweep covered it.

### Round 2 harness notes

1. `goto()` thrashes on the 96-unit strip (the route toward (14070, 20200)
   ran out its budget in place), which made run 1 take about 10 minutes; the
   positions it ended at are the ones reported.
2. The Guardian cutscene ran on the first teleport, as expected; the walk
   started 20 s later.

### Round 2 disk changes

- This section appended to `docs/playtest-2026-10-04-batch-retest.md`, plus
  the one-line correction under last round's C1f section; 13 `R2-` plates in
  `docs/playtest-2026-10-04-batch-retest/`.
- `shared/build/` rebuilt by `tools/build_artifacts.sh`, byte-identical to
  the recorded hashes; `shared/data/u8-install/` rewritten by
  `./install_lv.sh`; `shared/u8-lv-patched/` FIXED.DAT, both copies,
  `e8800ad0` to `079829c1` by `session.sh start`.
- Saves and `scummvm.ini`: no save was written this round; all 48 files and
  the ini were restored from the round 2 backup and verified.
- Scratch only: `<scratchpad>/r2bak/`, `<scratchpad>/r2logs/` (tests, build,
  install, sweep, session logs), drivers, and renders of shapes 476 and 580.
- No tracked file modified; `TODO.md` not touched.

## Round 3 (2026-10-04)

Change under test: `lv-new/ENDGAME.UNK` polls with `wait(600)` (was 200).
EUSECODE `c7cb35e0...`, 1,507,239 bytes, first 5000 bytes md5 `4f47de88...`;
FIXED unchanged at `079829c1...`. `tools/build_artifacts.sh` exit 0 with all
four OK; `tools/run_all_tests.sh` 37/37; Compilation Report 46 of 48
(`EALOGO.UNK`, `TJORVI.UNK`); `./install_lv.sh` exit 0. `session.sh start`
synced EUSECODE into `shared/u8-lv-patched/` (`c7cb35e0`) and the log reads
`4f47de88..., 1507239 bytes`, so the installed ScummVM detects it. One
session, one ScummVM pid. Plates are the `R3-` files, 640x400.

The disassembly of class 0x5AA differs from last build's in one place:
`04CF: 0B C8 00 push 00C8h` became `04CF: 0B 58 02 push 0258h`.

### Round 3 verdicts

| ID | Claim | Observed | Verdict |
|---|---|---|---|
| P1 | Interval between refill steps about 20 to 40 s, over at least four steps | 602 ticks between every pair of polls, 11 intervals in a row; with no console reads, 10.0 s of wall time each (10.04, 10.03, 10.19, 10.03, 10.03 s) | **FAIL** (10 s, half the low end) |
| P2 | 5 per poll to 25; a split inside the bag stays at 25 | 3, 8, 13, 18, 23, 25, then 25 for two more polls; split 13 + 12 at 25 across five polls | **PASS** |
| P3 | 0 process errors | 0 `Non-existent process`, 0 `stuck`, 0 segfaults, 0 assertions; the top-up's trace shows only offsets 1218 (entry), 1239, and 1254 over 52 polls | **PASS** |

### How the top-up was spawned by this build

The same route as rounds 1 and 2: `godsfree-at-exit-map18-2026-09-29.sav`
(Map 18 at the exit, `godsFree` 1, `endgameStarted` 0, `hasBag` 0) loaded
through slot 1, `UCMachine::traceClass 1450` turned on, then a walk north
into the exit trigger. Map 10 loaded 0.72 s into the walk, EggEndgame
hatched (`Item: 12052 (shape 73) calling usecode event 7 @ 05AA:0080`), and
the scene spawned the top-up as process 705, first traced at tick 1451070,
offset 1218 (0x4C2, the routine's `init`). `Kernel::listProcesses` then read
`Process 705 ... classname: EGGENDGA, IP: 05AA:04E6`, and `endgameStarted`
read 1. Last round's route to the stockade, a double-click on Ezrekal, the
menu clicked from the screen (`R3-01-ezrekal-menu.png`): **I have freed
your gods!** Afterwards `hasBag` 1 and bag 15685 reads `q: 1`, with six
stacks of 25, frames 0, 6, 8, 9, 10, 14 (`R3-02-after-handover.png`).

### P1: poll interval, FAIL

Every poll shows in the trace as `running process 705 ... offset 1254`
(0x4E6, the instruction after the wait's `suspend`). Two timings:

- **With reads** (P2's run, a `findShape 395` after each poll): ticks
  1468528, 1469130, 1469732, 1470334, 1470936, 1471538, 1472140, so 602
  ticks each time; wall intervals 14.2, 14.2, 14.1, 13.8, 14.1, 14.0 s, which
  include each read's pause of about 5 s.
- **Without reads** (the log tailed, no console): ticks 1474548, 1475150,
  1475752, 1476354, 1476956, 1477558; wall intervals 10.04, 10.03, 10.19,
  10.03, 10.03 s.

The kernel runs at 60 ticks a second (`kernel.h:137`, `TICKS_PER_SECOND =
60`), so `wait(600)` is 10 s, and the 200 it replaced was 3.3 s. The step
from last build is three times longer, as the change intended; the claim's
20 to 40 s needs `wait(1200)` to `wait(2400)`. My reading of the cause: the
`ENDGAME.UNK` comment's "measured 6-13 s in ScummVM" (from round 1's
readings) counted the time each console read paused the world, and the
target was scaled from it. Round 1's finding 5 flagged that those readings
included the pauses. Sure of the measurement.

### P2: refill and split, PASS

**Refill.** 22 of frame-14 stack 6784 dragged to the ground at (12786,
12734, 0) (`SplitItemProcess splitting: 22: 3-22`, `R3-03-slider-22.png`),
leaving 3 in the bag. Read after each poll:

| Poll (tick) | Bag stack 6784 | Ground stack 15907 |
|---|---|---|
| 1468528 | 8 | 22 |
| 1469130 | 13 | 22 |
| 1469732 | 18 | 22 |
| 1470334 | 23 | 22 |
| 1470936 | 25 | 22 |
| 1471538 | 25 | 22 |
| 1472140 | 25 | 22 |

Five steps, each +5 except the last (+2 to the cap), then no change.

**Split inside the bag.** 12 of frame-10 stack 15682 dropped on the bag's
own floor (`12: 13-12`, `R3-04-split-in-bag-slider-12.png`): 15682 at 13
and new 15317 at 12, both inside the bag, total 25 at each of five polls
(ticks 1479364 to 1481772, 66 s); the bag holds 7 items
(`R3-05-after-split-polls.png`).

### P3: process errors, PASS

The session's log up to the end of P2 (1,911 lines): 0 `Non-existent
process`, 0 `stuck in process loop`, 0 segfaults, 0 assertions, 0 `Cycle in
paint`, 0 `Invalid item 1037`. Its nine `WARNING` lines are three startup
notices (theme, `gui-icons.dat`, `translations.dat`), the three `Unhandled
intrinsic 154 'Npc::getNpcSlot()'` for Ezrekal's conversation (as in round
1), and the three dumps of item 116 that come with them. Process 705
appears in the trace at offsets 1218, 1239, and 1254 only, 52 polls in all.
The whole session log, including the extra check below (2,025 lines), has
0 of the four process counters too.

### Round 3 findings

1. **The poll is 10 s, not 20 to 40 s** (P1). `wait(n)` counts kernel ticks
   at 60 a second.
2. **A checkpoint does pick up the new interval.** The note with this round
   said a checkpoint resumes its saved process with the old wait. For a
   process whose frame matches, that holds only for the wait already in
   flight: the saved IP is `05AA:04E6`, after the `push`, and every later
   loop executes `04CF push 0258h` from the new bytecode. Loading
   `~/lv-checkpoints/bag-q1-newproc-map10-2026-10-04.sav` on this build
   restored process 784 (spawned in round 1 under the 200-tick build) and
   traced polls at ticks 1467098, 1467700, 1468302, 1468904, 1469506: 602
   ticks and 10.02 to 10.05 s apart. The 10-03 checkpoint stays unusable for
   the frame reason in round 1's finding 2. Sure of the timings; that
   the newproc checkpoint's refill amounts also match was not re-read.
3. **A harness slip overwrote one round 1 plate.** Round 1's driver for the
   Ezrekal strike writes `B1-01-ezrekal-menu.png` into the docs folder; this
   round's run replaced it, and the original is not recoverable. The image
   now lives at `R3-01-ezrekal-menu.png` (same menu, same route, this build),
   `B1-01` no longer exists, and round 1's B1 text says so. The driver now
   writes `R3-01`.

### Round 3 method and harness writes

Saves (48 files, md5 list) and `scummvm.ini` (`a143fa3b`) were copied to
`<scratchpad>/r3bak/` first and restored at the end; `md5sum -c` passes on
all 48, the names match, and the ini reads `a143fa3b`. Writes:

- Checkpoint loads through slot 1: `godsfree-at-exit-map18-2026-09-29.sav`,
  then `~/lv-checkpoints/bag-q1-newproc-map10-2026-10-04.sav` (finding 2).
- `Ultima8Engine::saveGame 1` once, right after the hand-over, copied to
  `<scratchpad>/sp/bag-q1-poll600-map10-2026-10-04.sav`: Map 10 at the
  stockade, bag 15685 with `q: 1` and six stacks of 25, top-up process 705
  spawned by `c7cb35e0`. That is the checkpoint for later bag tests on this
  build.
- `UCMachine::traceClass 1450` (twice, once per load) and
  `debugflag_enable Object`; reads: `objectInfo`, `findShape`, `getGlobal`,
  `Kernel::listProcesses`.
- In-world: the 22 to the ground and the 12 inside the bag, both by drag
  and slider. No teleport, no cheats, no `Item::grab`.

### Round 3 disk changes

- This section appended; round 1's B1 line amended for the lost `B1-01`
  plate; five `R3-` plates; `B1-01-ezrekal-menu.png` gone (finding 3).
- `shared/build/` rebuilt (recorded hashes); `shared/data/u8-install/` by
  `./install_lv.sh`; `shared/u8-lv-patched/USECODE/EUSECODE.FLX` synced to
  `c7cb35e0`.
- Saves and `scummvm.ini` restored and verified.
- Scratch only: `<scratchpad>/r3bak/`, `<scratchpad>/r3logs/`, the
  `bag-q1-poll600-map10-2026-10-04.sav` checkpoint, and the 0x5AA
  disassembly of this build.
- No tracked file modified; `TODO.md` not touched by me.

## Round 4 (2026-10-04)

Change under test: `lv-new/ENDGAME.UNK` polls with `wait(1200)` (line 159).
EUSECODE `f870721e...`, 1,507,239 bytes, first 5000 bytes md5 `4f47de88...`;
FIXED unchanged at `079829c1...`. `tools/build_artifacts.sh` exit 0 with all
four OK; `tools/run_all_tests.sh` 37/37; Compilation Report 46 of 48
(`EALOGO.UNK`, `TJORVI.UNK`); `./install_lv.sh` exit 0. `session.sh start`
synced EUSECODE into `shared/u8-lv-patched/` (`f870721e`), and the log reads
`4f47de88..., 1507239 bytes`. Class 0x5AA differs from round 3's in one
place: `04CF: 0B 58 02 push 0258h` became `04CF: 0B B0 04 push 04B0h`. One
session, one ScummVM pid. Plates `R4-01` and `R4-02`, 640x400; no earlier
plate was written.

### Round 4 verdicts

| ID | Claim | Observed | Verdict |
|---|---|---|---|
| P1 | Polls about 1,202 ticks and about 20 s apart, over at least four intervals timed without console pauses | six intervals of exactly 1,202 ticks; wall 20.12, 20.02, 20.06, 20.00, 20.06, 20.00 s with no console attached | **PASS** |
| P2 | Refill steps 5 per poll to 25 | 8, 13, 18, 23, 25, then 25; ground stack 17 throughout | **PASS** |
| P3 | 0 process errors | 0 `Non-existent process`, 0 `stuck`, 0 segfaults, 0 assertions; process 705 at offsets 1239 and 1254 only, 14 polls | **PASS** |

### Source of the top-up process

`~/lv-checkpoints/bag-q1-poll600-map10-2026-10-04.sav` (round 3's
checkpoint), loaded through slot 1. `Kernel::listProcesses` read `Process
705 ... classname: EGGENDGA, IP: 05AA:04E6`: the process round 3's build
spawned, with the same frame layout as this build's. Its next loop executes
`04CF push 04B0h` from `f870721e`, so after the wait already in flight every
poll uses 1,200 (round 3, finding 2).

### P1: interval, PASS

`UCMachine::traceClass 1450` on, then the log tailed with no console attach.
Polls (`running process 705 ... offset 1254`) at ticks 1467924, 1469126,
1470328, 1471530, 1472732, 1473934, 1475136, at 3.78, 23.90, 43.92, 63.98,
83.98, 104.04, 124.04 s after the start of the watch. Intervals: 1,202 ticks
each; 20.12, 20.02, 20.06, 20.00, 20.06, 20.00 s. The first poll, 3.78 s in,
ended the wait carried in the save and is not counted as an interval.

### P2: refill, PASS

Pack open with `i`, bag 15685 (`q: 1`) opened by a double-click, its gump
moved clear. 17 of frame-14 stack 6784 dragged to the ground at (12786,
12734, 0) (`SplitItemProcess splitting: 17: 8-17`,
`R4-01-slider-17-to-ground.png`), leaving 8 in the bag. Read after each
poll (these reads pause the world, so the wall times are longer; the ticks
are not affected):

| Poll (tick) | Bag stack 6784 | Ground stack 15907 |
|---|---|---|
| 1477540 | 13 | 17 |
| 1478742 | 18 | 17 |
| 1479944 | 23 | 17 |
| 1481146 | 25 | 17 |
| 1482348 | 25 | 17 |

`R4-02-after-refill.png` shows the open gumps after the last read.

### P3: process errors, PASS

Session log, 392 lines: 0 `Non-existent process`, 0 `stuck in process
loop`, 0 segfaults, 0 assertions, 0 `Cycle in paint`, 0 unhandled
intrinsics. The only `WARNING` lines are the three startup notices (theme,
`gui-icons.dat`, `translations.dat`). Process 705 appears in the trace at
offsets 1239 and 1254 only, 14 polls.

### Round 4 method and harness writes

Saves (48 files, md5 list) and `scummvm.ini` (`a143fa3b`) were copied to
`<scratchpad>/r4bak/` first and restored at the end; `md5sum -c` passes on
all 48, the names match, and the ini reads `a143fa3b`. Writes:

- One checkpoint load through slot 1:
  `~/lv-checkpoints/bag-q1-poll600-map10-2026-10-04.sav`.
- `UCMachine::traceClass 1450` and `debugflag_enable Object`; reads:
  `objectInfo`, `findShape`, `getGlobal`, `Kernel::listProcesses`.
- In-world: one drag and slider (17 to the ground); pack and bag gumps
  opened, then closed with `i` before saving.
- `Ultima8Engine::saveGame 1` once, copied to
  `<scratchpad>/sp/bag-q1-poll1200-map10-2026-10-04.sav` (md5 `c10e7332`):
  Map 10 at the stockade, gumps closed, bag 15685 `q: 1` with six stacks of
  25, a frame-14 stack of 17 on the ground at (12786, 12734, 0), and the
  top-up process 705 polling at 1,202 ticks under `f870721e`. The process
  was spawned by round 3's build; its frame and layout are this build's.
- No teleport, no cheats, no `Item::grab`.

### Round 4 disk changes

- This section appended; plates `R4-01-slider-17-to-ground.png` and
  `R4-02-after-refill.png`. The folder holds 66 plates.
- `shared/build/` rebuilt (recorded hashes); `shared/data/u8-install/` by
  `./install_lv.sh`; `shared/u8-lv-patched/USECODE/EUSECODE.FLX` synced to
  `f870721e`.
- Saves and `scummvm.ini` restored and verified.
- Scratch only: `<scratchpad>/r4bak/`, `<scratchpad>/r4logs/`, the
  `bag-q1-poll1200-map10-2026-10-04.sav` checkpoint, and this build's 0x5AA
  disassembly.
- No tracked file modified; `TODO.md` not touched by me.

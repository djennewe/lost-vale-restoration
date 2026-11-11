# Process loops with a per-lap suspend, re-verified statically and in engine (2026-10-02)

Change under test: the staged merge of `worktree-agent-a9177e9b1a96238e0` on
`main` (HEAD `db28de4`, `--no-commit`), plus the unstaged edits made after the
2026-10-01 FAIL (`docs/playtest-2026-10-01-process-loops.md`):
`u8c_codegen.py` `_gen_process_block` now emits `suspend` (0x53) right after
the loop label (`.loop: suspend; body; jmp .loop`), `test_uc_lordbrit.py`
checks the backward `jmp` lands on that suspend, and the rehash cascade
(`ARTIFACTS.sha256`, `build_scummvm.sh` `LV_MD5`/`LV_SIZE`) is done.

Artifacts: EUSECODE `fcbe3c15` (1,505,635 bytes, md5-5000 `6ad8a4e2`), FIXED
`f92973ee`. Binary `scummvm-lv/scummvm` built 19:13 today, embedding
`6ad8a4e2...` and `1505635` (`scummvm-lv/engines/ultima/detection_tables.h:297`).
All three sessions' logs read `usecode/eusecode.flx: 6ad8a4e2..., 1505635
bytes` and `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)`.
Plates are in `docs/playtest-2026-10-02-process-loops-suspend/`, 640x400,
named by test ID.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| C0 | Test estate | `tools/run_all_tests.sh`: 35/35, round-trip 516/516, `test_uc_lordbrit.py` 13/13 | **PASS** |
| C1 | Full build and hashes | `tools/build_artifacts.sh` exit 0, all four OK; outputs byte-identical to what was on disk | **PASS** |
| C2 | Compilation Report | 48 files, 46 succeed; failures `EALOGO.UNK`, `TJORVI.UNK`; 523 warnings | **PASS** |
| C3 | ScummVM fork | tip still `e0d6084d`; `diff -q` of the fork diff against the tracked patch is silent | **PASS** |
| C4 | Maps, shapes | no builder, map, or shape-ID change in the diff | **not triggered** |
| C5 | Test mutation | removing the `emit_suspend()` in `_gen_process_block` (`u8c_codegen.py:1216`): `test_uc_lordbrit.py` 11 passed, 2 failed | **PASS** (author's claim reproduced) |
| S1 | Every process-block backward `jmp` lands on a `suspend`; 14 in total | 191 backward jumps in the 25 changed classes, 177 at db28de4; the 14 new ones all land on a fresh `suspend` (0 of 14 at `ae17224e`) | **PASS** (14 confirmed) |
| 1 | Aramina on Map 41: no freeze | atHome lapped at 0x0417 every 2 ticks for 4 min; frames changed at every 26 s sample; log grew; console opened every time; CPU 97 to 100%, equal to a Map 41 control with no atHome (99 to 101%) | **PASS** (findings 1 and 2) |
| 2 | Lord British vision | two runs: frames cycled through the speech; run 2 read frame 9 directly at 188 s with `lbDone` 1; apparition then gone; Avatar walked; re-armed egg hatched and did not replay | **PASS** |
| 3 | Protection potion | ACT_IMMORTAL (0x40000) set, cleared after 31 laps of 64 ticks (Int 15, limit 30) | **PASS** (save patched, disclosed) |
| 4a | Shades scene | squabble lapped 4 times; three asks answered from the screen; `avatarPoisoned` 1 to 0, `shieldFixed` 0 to 1; egg process ended | **PASS** |
| 4b | Passage Test | no stone: egg hatched, nothing played, flags 0; with stone: scene played, `haveMark`, `avatarPoisoned`, `firstPoisoned`, `plantScene` all 1 | **PASS** |
| 5 | No error lines, no CPU pinning | 0 `Non-existent process`, 0 `stuck in process loop`, 0 `Segmentation`, 0 `Assertion` in three sessions; CPU everywhere matched its control | **PASS** (finding 2: a new warning flood) |

## Method and harness writes

Saves and `scummvm.ini` were copied to the scratchpad first
(`/tmp/claude-1000/v1002/bak/`, 48 save files with an md5 list). `./install_lv.sh`
exited 0; session 1's `start` synced EUSECODE into `shared/u8-lv-patched/`
(it held `ae17224e`). One ScummVM pid per session; three sessions.

Writes, all disclosed:

- **Teleports with cheats on**, each followed by `Cheat::toggle` back to
  `Cheats = false` before movement: Map 41 (16671, 19200, 48) for test 1 and
  the control; Map 3 (14527, 5887, 8) and back for the persistence check;
  Map 39 (17070, 20050, 48) for test 2; Map 41 and back to Map 39 to re-arm
  the egg for test 2's control; Map 10 (20304, 17600, 4) for 4a; Map 10
  (12800, 29720, 64) for 4b.
- **Checkpoint loads** through slot 1 (`Ultima8Engine::loadGame 1`) from
  `~/lv-checkpoints/`: `run-s16-tinytar.sav` (test 3),
  `run-s13-shield-halves.sav` (4a), `run-s7-ragnar-stone.sav` (4b).
- **Save patching for test 3**, the 10-01 recipe: `Item::grab 14823`,
  `saveGame 1`, then in the gunzipped save the `Item` record for objid 14823
  (`e7 39`, shape 859) had its frame word changed from 1 to 5, and potions
  3963, 8603, 14459 from 8 to 4. `findShape 859` after `loadGame 1` read
  frames 5 and 4.
- `Item::grab 15048` (the stone, 4b); `MainActor::toggleCombat` once (the
  shield-halves save loads in combat mode); `CameraProcess::moveToAvatar`;
  `MainActor::useBackpack` (UI only); `UCMachine::traceClass` 1037, 1253, 1434,
  1443, 1445, 1455 and `tracePID 165` (logging only); `Kernel::listProcesses`
  and `processInfo` (reads).

Every scene was entered by a walk. Every menu answer was clicked from what the
screen showed.

## S1: every process-block loop lands on a suspend, PASS

The staged index alone was exported (`git checkout-index -a`) and built with
`build_eusecode.build(output_path=...)`: it reproduced `ae17224e` exactly, the
FLX that froze on 10-01. The db28de4 FLX (`7f885f5e`) from the 10-01
scratchpad was the third reference. A class diff of `ae17224e` against
`fcbe3c15` gives the same 25 classes as 10-01; the size deltas are ARAMINA +3,
EGGMAGNE +3, LVFREE +2, and +1 each in TYPEPOTI, TYPEAOFR, EGGCANDL, TYPEPOIS,
TYPELORD, EGGSHADE: 14 bytes, the file's whole growth (1,505,621 to
1,505,635).

Backward jumps per class, landing opcode counted:

| Class | db28de4 on suspend | ae17224e on suspend | fcbe3c15 on suspend |
|---|---|---|---|
| ARAMINA | 0 of 12 | 0 of 15 | 3 of 15 (0x0416, 0x071A, 0x07B7) |
| TYPEPOTI | 0 of 0 | 0 of 1 | 1 of 1 (0x04E1) |
| TYPEAOFR | 0 of 0 | 0 of 1 | 1 of 1 (0x0175) |
| EGGCANDL | 0 of 1 | 0 of 2 | 1 of 2 (0x0096) |
| EGGMAGNE | 0 of 44 | 0 of 47 | 3 of 47 (0x009B, 0x00F4, 0x0531) |
| TYPEPOIS | 0 of 10 | 0 of 11 | 1 of 11 (0x0F34) |
| TYPELORD | 0 of 1 | 0 of 2 | 1 of 2 (0x06C5) |
| EGGSHADE | 0 of 18 | 0 of 19 | 1 of 19 (0x1E18) |
| LVFREE | 0 of 26 | 0 of 28 | 2 of 28 (0x0196, 0x0D45) |

The 14 jumps the merge added are exactly the 14 that now land on a suspend;
the 177 older backward jumps (while and foreach loops) are unchanged. A
normalized instruction diff (addresses and jump displacements masked) shows
14 inserted `suspend` instructions, no deletions, and every other changed line
a `call`/`spawn` whose target is LVFREE (0x05AE) or the class itself. All 251
`call`/`spawn` sites into the 25 disassembled classes land on an `init`.

## 1: Aramina, PASS

Fresh world, teleport to Map 41 (16671, 19200, 48), cheats off
(`B0-map41-arrival.png`), Aramina (npc 13) at (16671, 16671, 48) with flags
0x40 (outside the fast area). With
`traceClass 1037`, a 2 s walk north:

```
tick 4450 running process 162, item 0, type 0, class 1037, offset 407
tick 4450 running process 165, item 0, type 0, class 1037, offset 1007
tick 4450 (still) running process 162, item 13, type 535, class 1037, offset 483
tick 4450 running process 165, item 0, type 0, class 1037, offset 1047
tick 4452 running process 165, item 0, type 0, class 1037, offset 1047
tick 4454 running process 165, item 0, type 0, class 1037, offset 1047
```

Offset 1007 (0x03EF) is atHome's entry, the line where 10-01 froze; offset
1047 (0x0417) is the instruction after the new loop-head suspend at 0x0416.
`B1-walk-north-into-fast-area.png`.

A watch then ran ten samples 26 s apart, each a CPU reading (`top`, 5 s), a
frame hash, the log delta, and a 0.8 s walk in a rotating direction:

| t | CPU | frame changed | atHome laps | ticks |
|---|---|---|---|---|
| 5 s | 96.4% | yes | 162 | 5390 to 5712 |
| 32 s | 98.4% | yes | 796 | 5714 to 7304 |
| 111 s | 97.2% | yes | 796 | 10486 to 12076 |
| 191 s | 98.2% | yes | 791 | 15252 to 16832 |
| 244 s | 99.4% | yes | 796 | 18426 to 20016 |

(five of ten rows shown; every row changed frame and logged about 795 laps).
The tick counter advanced 60 per second throughout, so the engine kept real
time. The console opened on every one of the dozens of reads that followed.
`B1-aramina-t005s.png`, `B1-aramina-t244s.png` (`compare -metric AE` between
them: 242,665 pixels differ).

**CPU control:** a fresh session on the same Map 41 spot, Aramina outside the
fast area, no ARAMINA process in `listProcesses`, no warnings: 99.2%, 99.8%,
100.8%. With the loop running the readings were 96 to 100%, so atHome adds no
measurable CPU. Map 3 at the start of session 1 read 78 to 80%; Xvfb software
rendering of Map 41 costs the difference. The 10-01 freeze read 106 to 110%
with a static frame and a static log.

**Negative control:** 10-01 ran this route on `ae17224e` and froze at offset
1007 (`docs/playtest-2026-10-01-process-loops/B1-frozen-t0.png`). The binary's
pinned size makes an in-engine replay of `ae17224e` impossible; the
bytecode difference at that point is the single `suspend` at 0x0416.

Two side effects of the now-living loop are findings 1 and 2.

## 2: Lord British vision, PASS

**Run 1** (session 2, fresh world, after the `lbSpoke` detour had already
fired): walked from (17070, 20050) (`A0-map39-start-south-of-egg.png`) into the egg box (x 17022 to 17278,
y 19572 to 19828; `build_map_39.py:83-84`, npcnum 0x44). The first walk
stopped at x 17010, 12 units short, and nothing happened for 260 s; a second
walk to (17194, 19718) hatched it: egg pid 168 (class 1455, offset 128), then
puppet pid 377 lapping at offset 1734 (0x06C6, after the loop-head suspend at
0x06C5). The apparition (item 2091) read frames 8, 2, 5, 2, 7, 1, 2, 4, 7, 2,
8, 2, 4, 2, 2 at about 9 s intervals (`A1-puppet-frame5-22s.png`,
`A1-puppet-frame1-50s.png`). 331 puppet slices at 1734 ran from tick 21996 to
26726; the last one has no following wait slice, so it took the
`lbDone = 1` branch (`setFrame(9); ret`). The console missed the frame-9
window in this run.

**Run 2** (session 3, fresh world): same walk, apparition 13748, frames 4, 6,
8, 2, 7, 1, 3, 2, 8, 5, 2, 2, 8, 2, 4, 1, 6, 2, 3, 7, 2, 5, then **frame 9 at
188 s** with `lbDone` 1 read immediately after (`A2-frame9-read-187s.png`),
then `No such object: 13748` and `findShape 411: 0 found`.

After both runs: `[06A5 01] = 1` (lbStarted), `[06A6 01] = 1` (lbDone). The
Avatar walked: run 2 moved from (17194, 19718) to (17194, 19950) on one 1 s
walk (`A3-avatar-walks-after-scene-run2.png`); run 1 walked out to
(17154, 20014) and back (`A3-avatar-walked-out-south.png`).

**Negative controls (run 1):**

- Walking out of the box and back in logged no class 1443 or 1455 slice
  (`A4-reentry-no-replay.png`). This proves little alone: eggs re-arm only
  when they leave the fast area.
- Re-armed with a map round trip (Map 41, then Map 39 at 17070, 20050): the
  reload restored the fixed apparition (item 6192), the walk-in hatched the
  egg (pid 350, class 1455, offset 128), the `lbStarted = 1` branch destroyed
  the apparition (`findShape 411: 0 found`), no class 1443 code ran, and the
  flags stayed 1 and 1 (`A4-rearmed-egg-hatch-no-replay.png`).

## 3: protection potion, PASS

Avatar Int 15, so `limit` is 30. Flags before: `400`. The patched frame-5
potion was double-clicked in the pack (`D0-pack-open.png`,
`D1-drank-frame5.png`); 14823 went to frame 0 and `protection()` started as
pid 1933. Polls of `objectInfo 1`: `40400` at 5 s (ACT_IMMORTAL set,
`D2-immortal-flag-set.png`), `400` at 62 s (`D3-immortal-cleared.png`).

Trace of pid 1933: 31 slices each at 1250 (0x04E2, after the loop-head
suspend at 0x04E1), 1258, and 1273 (after `wait(60)`), **64 ticks apart** on
every lap, ticks 1776034 to 1778016. On 10-01 the spacing was 62; the extra
two ticks per lap are the new suspend (usecode runs every second tick). The
last slice continues into LVFREE at 3209 (0x0C89), `safePlaySFX`, one byte
later than 10-01's 3208 because LVFREE `wait()` grew a byte. 31 laps is
`counter > limit` with limit 30, as on 10-01. The MAGIC2 sound was not heard
(no audio capture).

## 4a: the Shades scene, PASS

From `run-s13-shield-halves.sav` (Map 17, both halves in the pack, flags
`c00`, `avatarPoisoned` 1): combat off, teleport to (20304, 17600, 4), cheats
off (`E0-map10-circle-approach.png`), 1.5 s walk north. Egg 9679 hatched in
pid 11118. Offset 7705 (0x1E19, after squabble's loop-head suspend at 0x1E18)
appears exactly four times in the trace, so all four exchanges played, as on
10-01. The three asks, each clicked from the screen:

- "Can't you two get along!?" or **"Let's be reasonable!"**: picked the
  second (`E1-first-ask.png`).
- **"Yes, Priestess."** or "No, ...": picked the first (`E2-second-ask.png`).
- "Now, reunited, we are..." (`E3-reunited-bark.png`), the Shades in yellow
  (`E4-shade-speaks.png`).
- **"Please, High Priestess."** or "No, ... anyway": picked the first
  (`E5-heal-ask.png`).

After: `avatarPoisoned` 0, `shieldFixed` 1, `inShadeScene` 0, one shape-539
item, frame 2; `No such process: 11118`; the elders gone and the camera on
the Avatar (`E6-scene-ended.png`).

## 4b: the Passage Test, PASS

**Negative control:** from `run-s7-ragnar-stone.sav`, stone 15048 still in
its container (Avatar weight 30), teleport to (12800, 29720, 64), cheats off,
walk north: egg pid 7588 hatched (class 1434, offset 128), nothing played,
`haveMark`, `avatarPoisoned`, `firstPoisoned`, `plantScene` all 0
(`F0-no-stone-hatch-nothing-plays.png`).

**Positive:** reloaded, `Item::grab 15048` (weight 40), same teleport and walk
(`F0b-test-grounds-approach-with-stone.png`): pid 7641 ran the whirlwind and
plant scene (`F1-passage-test-scene.png`), then ended; all four flags 1,
weight 30 (stone consumed).

## 5: log and CPU, PASS for the named lines

| Session | Lines | Non-existent | stuck | Segmentation | Assertion | Invalid item (area search) |
|---|---|---|---|---|---|---|
| 1 (Aramina, persistence) | 107,921 | 0 | 0 | 0 | 0 | 97,814 |
| 2 (CPU control, LB run 1) | 1,594 | 0 | 0 | 0 | 0 | 0 |
| 3 (LB run 2, potion, Shades, Passage Test) | 1,157 | 0 | 0 | 0 | 0 | 0 |

No `Cycle in paint` lines in any session. Session 3 logged 25 `Skipping
invalid shape in sorter: 400,30..34` during the Passage Test's whirlwinds,
`539,4` once on load, and one each of `Trying to access segment 0000!` and
`Unhandled intrinsic 101 'process Item::combine()'` right after the Passage
Test; the 10-01 session that ran the Passage Test logged the same two lines,
so they predate this change. CPU matched its control everywhere it was
measured (Map 41 with and without atHome; Map 3 at 78 to 90%).

## Findings outside the plan

1. **Aramina's atHome is now an immortal process, and one more accumulates
   per visit.** `ARAMINA.UNK:219` opens atHome with `[[PT_ACTIVITY,
   referent]];`, which the compiler drops (`WARN ARAMINA.UNK:219: DROPPED
   PRAGMA`). Retail's atHome (class 0x40D, 0x0460) opens with `set info`
   (type 0x205, item 13), and retail's enterFastArea spawns it without
   waiting. In this build a spawned process starts at item 0, type 0
   (`uc_machine.cpp:1379`); `leaveFastArea` kills only item 13's types, and
   a map switch never kills item-0 processes (`world.cpp:184`,
   `kernel.cpp:323`). Before this merge atHome ran once and returned; it now
   loops forever. In engine: pid 165 survived the switch to Map 3 while
   enterFastArea (pid 162) died (`B2-map3-after-leaving-map41.png`), still
   lapping 30 times per second (`tracePID 165`). Back on Map 41
   (`B3-map41-second-visit.png`), Aramina still carried FLG_FASTAREA, so
   enterFastArea did not re-fire and no second process appeared. Once
   Aramina left the fast area (flags 0x40) and re-entered, a second atHome
   (pid 342) spawned beside the orphan (`B4-second-atHome-after-reentry.png`,
   `B5-console-two-atHome-processes.png`). Each Map 41 visit with an
   approach adds one. `Kernel::save` writes every process with no item or
   type filter (`kernel.cpp:385-402`), so the orphans ride into every save
   made after a Map 41 visit (read from source; no save was inspected).
   This is a regression against HEAD, where atHome ran once and ended, and
   it reaches the base-game route through East Tenebrae. The hinge is the
   dropped pragma: retail compiles it to `set info` 0x205, which the
   source's own `leaveFastArea` (`killProcess(referent, PT_ACTIVITY)`)
   already targets. `inKitchen` (`:274`) has the
   same dropped pragma and is unreachable today (finding 3 of 10-01:
   `araminaSchedule` compares against identifiers compiled as 0).
2. **Each atHome lap logs six `WARNING: Invalid item 1037 passed to area
   search!` on Map 41**, about 190 per second per process, about 9.4 KB of
   stderr per second; two processes doubled it (5,664 per 15 s). The search
   is centred on objid 0x040D, the class number (10-01 finding, test 3). On
   Map 3 objid 1037 is a water tile (shape 347), so the orphan searches
   around it silently; on a map where 1037 lands near something the filter
   matches, atHome would call `pathfind` on an Aramina who is on another map.
   That branch did not fire in this session.
3. **The compiler's dropped-pragma warning text is wrong for spawned
   functions.** `u8c_codegen.py:1382-1385` says the process "keeps its event
   identity and WILL be killed by the next map change". A spawned function
   has no event identity: it starts at item 0, which a map switch never
   kills. The build prints this warning 23 times (FREE, HRODNY, THORDIS,
   AIRSPEL, ARAMINA x7, EAPUZL, INGYALD, METHOD x4); any of those that sits
   in a spawned `process { }` block is immortal under the new loop
   semantics.
4. **The index alone is inconsistent.** `u8c_codegen.py` (MM),
   `test_uc_lordbrit.py` (AM), `build_scummvm.sh`, and `ARTIFACTS.sha256`
   all carry unstaged halves. The index's compiler builds `ae17224e`
   (reproduced here), its `ARTIFACTS.sha256` is HEAD's `7f885f5e`, and its
   `build_scummvm.sh` pins 1505576. Committing the index as it stands would
   ship the freezing compiler with a hash set that matches neither build.
5. **The regression test covers one class.** `test_uc_lordbrit.py` checks
   TYPELORD's loop only. The other 13 process loops have no test; the
   per-class back-jump count in S1 (a 40-line script over the disassembly)
   would cover all of them.
6. **LVFREE `wait()` is now a yielding infinite loop** when `retval` is
   nonzero (`0196: suspend; push retval; jne; ret; jmp 0196`). Dormant: no
   class calls 0x05AE:0x018A.
7. **The puppet's only exit is `lbDone`.** `puppet()` carries `set info` type
   1, which a map switch never kills, and only `use()` sets `lbDone`. If
   `use()` dies mid-scene (the `lbSpoke` case in finding 8 of 10-01), the
   puppet would lap every 10 ticks indefinitely. Not observed; static
   reading only.

## Harness anomalies

- `top -p $(pgrep -f 'scummvm.* -p ...')` matched the pgrep's own shell in
  session 2 and read 0.0%; matching on `^/home/.../scummvm-lv/scummvm`
  fixed it. Session 1's readings were taken from the correct pid (445304,
  the one `session.sh stop` killed).
- The console missed two consecutive `objectInfo` reads near the end of LB
  run 1 and so missed frame 9; run 2 caught it.
- After `loadGame` and a teleport on `run-s7-ragnar-stone.sav`, the camera
  stayed on a village and the Avatar did not move on the first walk;
  `CameraProcess::moveToAvatar` fixed it.
- `session.sh stop` ended ScummVM with SIGTERM in all three sessions (it
  needed `kill -9` on 10-01, when the engine was frozen).
- The `lbSpoke` detour fired during the first console commands after leaving
  Map 3 in sessions 2 and 3, and briefly put the Avatar on Map 0.

## Disk changes

- `docs/playtest-2026-10-02-process-loops-suspend.md` (this report) and 30
  plates in `docs/playtest-2026-10-02-process-loops-suspend/`.
- `shared/build/` rebuilt by `tools/build_artifacts.sh`: byte-identical to
  what was there (`fcbe3c15`, `f92973ee`; new mtimes).
- `shared/data/u8-install/` rewritten by `./install_lv.sh` (EUSECODE
  `fcbe3c15`).
- `shared/u8-lv-patched/USECODE/EUSECODE.FLX` synced by `session.sh start`
  from `ae17224e` to `fcbe3c15`.
- `~/.local/share/scummvm/saves/`: `ultima8.000`, `ultima8.001`, and
  `scummvm-history.txt` were overwritten during the session and restored
  from the backup; `md5sum -c` passes on all 48 files.
  `~/.config/scummvm/scummvm.ini` was rewritten by ScummVM (key order) and
  restored byte for byte (md5 `a143fa3b...`).
- Scratch only: `/tmp/claude-1000/v1002/` (staged-index tree, `ae17224e`
  FLX, disassemblies, logs, driver).
- No tracked file was modified; the staged merge and the unstaged edits are
  as the author left them. `TODO.md` was not touched.

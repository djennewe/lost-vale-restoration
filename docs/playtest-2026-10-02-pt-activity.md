# PT_ACTIVITY pinned at 0x205, verified statically and in engine (2026-10-02)

Change under test: the staged merge of `worktree-agent-a9177e9b1a96238e0` on
`main` (HEAD `db28de4`, `--no-commit`) plus unstaged edits. The new part is
`u8c_codegen.py` `PRAGMA_TYPES` gaining `'PT_ACTIVITY': 0x205`, pushed as a
word by the new `_push_pragma_type`, so `[[PT_ACTIVITY, referent]]` emits
`0B 05 02 40 06 4C 02 77`; `test_pragma.py` pins it; the rehash cascade is
done (`ARTIFACTS.sha256`, `build_scummvm.sh` `LV_MD5`/`LV_SIZE`).

Artifacts: EUSECODE `c9180526` (1,505,739 bytes, md5-5000 `a6c0b72b`), FIXED
`f92973ee`. Binary `scummvm-lv/scummvm` built 2026-10-02 20:41, after the fork
tip `e0d6084d` (2026-09-19), and carries `a6c0b72b...`. Both sessions' logs
read `usecode/eusecode.flx: a6c0b72b..., 1505739 bytes` and `Running Ultima
VIII: Pagan (Gold Edition + Lost Vale/DOS/English)`. Plates are in
`docs/playtest-2026-10-02-pt-activity/`, 640x400, named by test ID.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| C0 | Test estate | `tools/run_all_tests.sh`: 35/35; `test_pragma.py` 24/24; round-trip 516/516 | **PASS** |
| C1 | Full build and hashes | `tools/build_artifacts.sh` exit 0, all four OK; EUSECODE byte-identical to the `c9180526` on disk | **PASS** |
| C2 | Compilation Report | 48 files, 46 succeed; failures `EALOGO.UNK`, `TJORVI.UNK`; warnings 523 to 509; `DROPPED PRAGMA` lines 23 to 9 | **PASS** |
| C3 | ScummVM fork | tip still `e0d6084d`; `diff -q` of the fork diff against the tracked patch is silent | **PASS** |
| C4 | Maps, shapes | no builder, map, or shape-ID change in the diff | **not triggered** |
| C5 | Test mutation | `PRAGMA_TYPES` reverted to `{'PT_DEFAULT': 1}` in a scratch copy: `test_pragma.py` 22 passed, 2 failed | **PASS** |
| S | Count and four-class diff | 11 of 11 NPC classes match retail; 4 of 1,458 classes change, +104 bytes, 13 sites, nothing else | **PASS** |
| 1 | Aramina, Map 41 | atHome runs as item 13, type 0x205; a map switch kills it; leaving her fast area does **not**; a map return starts none; at most one ever runs | **FAIL** (one sub-claim false; findings 1, 3, 4) |
| 2 | Thordis, Ingjald, Hrodny, Map 10 | bark processes traced as type 0x205 on each NPC; wander, dialogue, and in-map re-entry all good; NPCs stand frozen after a map round trip and after another NPC's conversation | **PARTIAL** (findings 2, 3) |
| 3 | Regression spot checks | LB frame 9 at 140 s with `lbDone` 1; potion ACT_IMMORTAL set at 15 s, cleared by 66 s; Shades 4 squabble laps, 3 menus, flags right | **PASS** (potion lap spacing not measured) |
| 4 | Log and CPU | 0 `Non-existent process`, 0 `stuck in process loop`, 0 `Segmentation`, 0 `Assertion` in both sessions; Map 41 CPU with atHome equals its no-atHome control | **PASS** |

## Method and harness writes

Saves and `scummvm.ini` were copied first (`/tmp/claude-1000/v1002b/bak/`, 48
save files with an md5 list). `./install_lv.sh` exited 0; session 1's `start`
synced EUSECODE into `shared/u8-lv-patched/` (it held `fcbe3c15`, which was
copied out first as the diff reference). Two sessions, one ScummVM pid each.

Writes, all disclosed:

- **Teleports with cheats on**, each followed by `Cheat::toggle` back to
  `Cheats = false` before movement or any click: Map 41 (16671, 19200, 48)
  three times; Map 3 (14527, 5887, 8) four times; Map 10 (6144, 9400, 0),
  (21200, 11200, 0), (22148, 8260, 0), and (20304, 17600, 4); Map 39
  (17070, 20050, 48).
- **Checkpoint loads** through slot 1 (`Ultima8Engine::loadGame 1`):
  `~/lv-checkpoints/cp22-hastea.sav` (claim 2),
  `/tmp/claude-1000/v1002/sp/slot1-patched.sav` (the 10-01 potion recipe save
  from the previous run: potion 14823 at frame 5, three others at frame 4),
  `~/lv-checkpoints/run-s13-shield-halves.sav` (Shades).
- `MainActor::toggleCombat` once (the shield-halves save loads in combat
  mode); `CameraProcess::moveToAvatar` once; `MainActor::useBackpack` (UI);
  `UCMachine::traceClass` 1037, 1130, 1136, 1137, 1445, 766 and
  `debugflag_enable Object` (logging only); `Kernel::listProcesses`,
  `Kernel::processInfo`, `objectInfo`, `findShape`, `getGlobal` (reads).
  `Actor::hold` was not used: it kills (npc, 0x205), the type under test.

Plates were written by the driver's default path, which is this report's
folder; `LV_PLATES` was not set in the environment.

Every NPC approach and both scenes were entered on foot. Every menu answer was
clicked from what the screen showed.

## S: the count and the four-class diff, PASS

Count, rerun with my own script over all 12 files in
`shared/data/lv-usecode/U8/` that contain `[[PT_ACTIVITY` (comments stripped;
the raw count is the same), against `shared/data/u8-install/USECODE/EUSECODE.FLX.bak`:

| Class | Retail id | Source | Retail `0B 05 02 40 06 4C 02 77` |
|---|---|---|---|
| ARAMINA | 0x40D | 7 | 7 |
| BENTIC | 0x40C | 2 | 2 |
| CYRRUS | 0x416 | 7 | 7 |
| DARION | 0x405 | 6 | 6 |
| JENNA | 0x418 | 4 | 4 |
| KILANDRA | 0x410 | 2 | 2 |
| MORDEA | 0x407 | 7 | 7 |
| SALKIND | 0x403 | 4 | 4 |
| STELLOS | 0x417 | 4 | 4 |
| TORWIN | 0x41A | 4 | 4 |
| XAVIER | 0x419 | 7 | 7 |

`LES4_4.UNK` has one pragma and no retail class. The pattern occurs 124 times
in the new FLX.

Class diff, `fcbe3c15` against `c9180526`, all 1,458 entries:

```
0x40D ARAMINA    size 17624 -> 17680 (+56)  pattern 0 -> 7
0x46A THORDIS    size 37232 -> 37248 (+16)  pattern 0 -> 2
0x470 INGJALD    size 13849 -> 13865 (+16)  pattern 0 -> 2
0x471 HRODNY     size 20562 -> 20578 (+16)  pattern 0 -> 2
changed classes: 4 of 1458
```

A normalized instruction diff of the four classes (addresses and jump
displacements masked) shows 52 inserted instructions, 13 copies of `push
0205h; push dword [BP+06h]; push indirect 02h; set info`, and every other
changed line a self-class `call`/`spawn` whose offset moved. All 15 of those
land on an `init`. In ARAMINA the sites sit where retail's do: after the
event preamble's `set info; process exclude`, or directly after `init`.

The 14 warnings that vanished from the build are ARAMINA 7, THORDIS 2,
HRODNY 2, INGYALD 2, and METHOD 1. METHOD's class is unchanged because
`METHOD` is in `UNSAFE_TO_REPLACE` (`build_eusecode.py:181`) and never
reaches the FLX.

## 1: Aramina, FAIL

The pin itself is right (S and C5). What fails is the lifecycle the claim
describes: the fast-area exit kills nothing, because the call it makes is a
no-op (finding 1). What the change does achieve for Aramina: a map switch now
kills atHome, so the 10-02 orphan that survived on Map 3 and stacked a copy
per visit is gone.

**atHome runs as item 13, type 0x205: holds.** Walking north from the Map 41
landing put Aramina in the fast area (flags `0x40` to `0x2040`):

```
Process 171 class UCProcess, item 13, type 217, status ASD, classname: ARAMINA, IP: 040D:01F0
Process 278 class UCProcess, item 13, type 205, status AD, notify: 171, classname: ARAMINA, IP: 040D:041F
```

0x041F follows the loop-head `suspend` at 0x041E. Under `traceClass 1037` the
slices read `running process 482, item 13, type 517, class 1037, offset 1055`
(517 is 0x205), 450 of them in 15 s. `B1-walk-north-into-fast-area.png`,
`B1b-aramina-after-30s.png`.

**A map switch kills it: holds.** After each teleport to Map 3 the process
list held no ARAMINA process (`B2-map3-after-leaving-map41.png`), and the
Map 3 log took no area-search warnings.

**Leaving her fast area kills it: false.** Three walk-outs (flags `0x40`)
left pid 375 alive at the same IP each time. A later trace with pid 482 live:

```
out 0x60
OUT 10s: warnings 1812 slices {('482', '13', '517', '1055')} 302
in 0x2060
IN 10s: warnings 1800 slices {('482', '13', '517', '1055')} 300
```

atHome laps 30 times per second with Aramina outside the fast area. Her
`leaveFastArea` (0x022C) routes `killProcess(referent, PT_ACTIVITY)` through
`call 05AE:0CDB`, and LVFREE 0x0CDB is `init 00h; push byte 0; ret` (finding
1). The fork logs every `Kernel::resetRef`; each leave logged 0x0204, 0x00F0
and 0x0200 for item 13 and never 0x0205 (session 1 log lines 11332, 11364,
11393, 11422). `B4-aramina-out-of-fast-area.png`.

**Returning starts exactly one: false as stated.** After both map returns
Aramina read `0x2040` before the walk and no ARAMINA process appeared after
it (`B3-map41-visit2.png`, `B3-map41-visit3.png`). NPC-list items keep
FLG_FASTAREA through `CurrentMap::writeback` (`current_map.cpp:134-136`), so
`Item::enterFastArea` skips the usecode on return (`item.cpp:1889`). Only a
walk out and back in started one (pid 375, `B5-reentry-one-atHome.png`).
In-map re-entry while atHome lives starts nothing new: the old enterFastArea
(pid 369, then 113) waits on atHome (`implies` at 0x01EB) and its `process
exclude` (0x01A1) ends every later enterFastArea for item 13 (finding 4).

**No stacking: holds.** Across three map visits, three in-map cycles, and
two more traced cycles, the list never held more than one ARAMINA type-0x205
process.

**Responsive, CPU at control: holds.** With atHome: 97.8, 98.2, 98.2% at
(16671, 18704); 97.2, 99.6% later. Control at the same spot with no atHome
(after the talk below killed it): 98.4, 98.2, 99.6%
(`B6-cpu-control-no-atHome.png`). Map 3: 82.5, 83.1%. Frames changed between
samples; the console opened on every read.

**Warning flood (separate defect).** 6 `Invalid item 1037 passed to area
search!` per lap, 180 per second per live atHome (2,688 in 15 s on visit 1;
2,700 in 15 s with 450 traced slices). It continues outside the fast area
(1,812 in 10 s). Session 1 logged 41,570 in total. One window logged none
while pid 375 was alive (log lines 11352 to 11426, during the in-map cycles);
that is unexplained.

**Negative control, a click on Aramina:** she barked "I am sorry, but I can
not talk to you now. I must attend to her ladyship." (`C1-aramina-talk.png`),
and her `use()` still ran the compiled `enterConvo()`. That killed atHome
(375) and enterFastArea (369). After the bark she had one `LoiterProcess,
item 13, type 205` from the exitConvo epilogue
(`C2-after-aramina-bark.png`). A fresh fast-area entry later killed that
loiter (enterFastArea's direct `resetRef(referent, PT_ACTIVITY)`) and spawned
atHome 482.

## 2: Thordis, Ingjald, Hrodny, PARTIAL

`cp22-hastea.sav` (dated 17 August 2026; the other cp22,
`cp22-shield-halves.sav`, is from 2 September) loads on Map 10. NPC numbers from `build_map_10.py`: Thordis
106 (class 0x46A), Ingjald 112 (0x470), Hrodny 113 (0x471). In all three,
`enterFastArea` does `cSetActivity(ACT_LOITER)` (an engine `LoiterProcess`,
already type 0x205 at `loiter_process.cpp:44`) and then spawns a one-shot
`randomBark*()` whose first instruction is now the 0x205 `set info`. The
schedule identifiers compile as 0 (finding 5), so only `randomBarkAtHome`
runs.

**Bark processes carry 0x205: holds.** A bark whose random roll waits shows
in the trace under the NPC with type 517:

- Thordis: `7382, item 106, type 517` at 1504, 1512, 1527 (cycle 2).
- Ingjald: `4698, item 112, type 517` at 1113, 1121; then 2231, 5335, 5266
  in her three cycles.
- Hrodny: `6494, item 113, type 517` at 1213, 1221, 1236 (cycle 2).

Rolls with no wait finish inside their first slice and show only the
item-0 entry slice (0x0453 for Thordis).

**Wander: holds.** Four samples 3 s apart put Thordis at (5975, 6467),
(6035, 6887), (6395, 6527), (6183, 6859) under one loiter (6321)
(`E2-near-thordis.png`). Ingjald and Hrodny moved between every pair of reads.

**Leaving and returning in-map restarts once: holds.** Three cycles each.
Every re-entry ran one enterFastArea and spawned one bark; the loiter was
replaced once (Thordis 6321, 4090, 7377, 2377; Hrodny 4608, 3022, 6518,
3629; Ingjald 4715, 2219, 5300, 5189). Never two loiters on one NPC.
`E3-thordis-cycle1..3.png`, `F2-ingjald-hrodny-cycle1..3.png`,
`F3-ingjald-in.png`. On every exit the old loiter survived and kept walking
the NPC outside the fast area, for the same no-op reason as Aramina.

**Dialogue opens: holds.** Cheats off for each.

- Thordis: "Oh my, terrible this is. Sent you here Atli did?" and a scripted
  run of speech with two Avatar replies, then a fresh loiter (3984) and she
  walked on (`E4b-thordis-dialogue-opens.png`, `E5-thordis-dialogue-speech.png`,
  `E6-thordis-after-dialogue.png`). No menu in this game state.
- Ingjald: **What is your name?**, **What do you do?**, **bye**; picked the
  first, "Ingyald, my name is. Though other names called, I have been.",
  then **bye** from the second menu; loiter 1965, moving
  (`G1`..`G4`).
- Hrodny: **Tell me more of the Cliffs.**, **bye**. The first redisplays the
  menu (finding 6, `H2-hrodny-cliffs-option-redisplays.png`); **bye** closed
  it; loiter 1880, moving, sprite visible
  (`H3-hrodny-after-bye.png`, `H4-hrodny-visible-after-bye.png`).

**No frozen NPC: false in two cases, both from mechanisms that predate this
change.**

- After a Map 3 round trip, Ingjald and Hrodny stood at (20736, 6912) and
  (21760, 8448) for 10 s with flags `0x2040` and no process at all
  (`H5-after-map-round-trip.png`). A walk out and back gave each a loiter
  (945, 3781) and they moved. Same cause as claim 1's map return.
- Talking to Hrodny killed Ingjald's loiter: the process list before the
  round trip held Hrodny's 1880 and nothing for 112. Every conversation
  kills every 0x205 process in the world (finding 2).

No NPC vanished.

## 3: regression spot checks, PASS

**Lord British** (session 2, fresh world): walk from (17070, 20050) to
(17194, 19718). Apparition 13748 read frames 6, 5, 8, 3, 2, 3, 5, 7, 1, 1, then
**frame 9 at 140 s** with `lbDone` 1 (`A2-frame9-read-140s.png`); `lbStarted`
1; `findShape 411: 0 found` afterwards; the Avatar walked (17194, 19718) to
(17194, 19950) (`A3-avatar-walks-after-scene.png`).

**Protection potion:** Avatar Int 15. Double-click on the frame-5 potion in
the pack: `Item: 14823 (shape 859) calling usecode event 1 @ 04E5:00A9`;
14823 went to frame 0. `objectInfo 1` flags: `400` at 5 s, `40400` at 15 s
(`D2-immortal-flag-set.png`), `400` at 66 s (`D3-immortal-cleared.png`). Lap
spacing was not measured: I traced class 766 and the potion dispatches through
class 1253 (0x4E5). That class is byte-identical to `fcbe3c15`.

**Shades scene:** combat off, teleport to (20304, 17600, 4), cheats off, 1.5 s
walk north. Egg pid 11126; offset 7705 appears exactly 4 times in the trace.
Menus, each clicked from the screen: **Let's be reasonable!**
(`K1-first-ask.png`), **Yes, Priestess.** (`K2-second-ask.png`), the elders'
"To end our quarrels, resolved we are!" (`K2b-elders-resolved.png`), the
Shades in yellow, then **Please, High Priestess.** (`K3-heal-ask.png`).
After: `avatarPoisoned` 0, `shieldFixed` 1, one shape-539 item at frame 2,
`inShadeScene` 0 once the scene finished, `No such process: 11126`, elders
gone (`K4-scene-ended.png`).

## 4: log and CPU, PASS

| Session | Lines | Non-existent | stuck | Segmentation | Assertion | Invalid item 1037 | Cycle in paint | Unhandled intrinsic 154 |
|---|---|---|---|---|---|---|---|---|
| 1 (Map 41, Map 10 NPCs) | 162,789 | 0 | 0 | 0 | 0 | 41,570 | 110,783 | 12 |
| 2 (LB, potion, Shades) | 12,087 | 0 | 0 | 0 | 0 | 0 | 11,204 | 0 |

CPU is under claim 1. The 12 `Unhandled intrinsic 154 'Npc::getNpcSlot()'`
lines are finding 2; the paint-cycle lines are finding 7.

## Findings outside the plan

1. **LVFREE `killProcess` does nothing, at all 43 call sites.**
   `lv-patched/FREE.UNK:830-832` is `Kernel::resetRef(r,ptype);`, and the
   build says `WARN FREE.UNK:831: unknown identifier 'Kernel' compiled as push
   0`. The routine compiles to `0CDB: init 00h; push byte 0; ret`. Callers
   in the new FLX: AVATAR 4, ARAMINA 2, SIGRID 1, RAGNAR 3, THORDIS 4, ATLI 4,
   INGJALD 3, HRODNY 3, TYORVI 3, EZREKAL 3, EGGPLANT 2, TYPEPOIS 4,
   EGGSHADE 6, LVFREE 1. Every `leaveFastArea` that relies on it leaves its
   activity running, and so does each `killProcess` in scenes
   (`SHADES.UNK:135-137`, `PLNTST.UNK:85,91`). The pin made this visible:
   before it, the (npc, 0x205) a killProcess names was only the engine loiter.
   Unqualified `resetRef(...)` compiles to `calli 04 00CB` and works. Sure of
   the bytecode and the log; the in-engine consequence is shown for ARAMINA
   and the three villagers.
2. **Every conversation kills every 0x205, 0xF0, and 0x204 process in the
   world.** The compiled `enterConvo()` (`u8c_codegen.py:1257-1278`) passes
   `Npc::getNpcSlot()` (intrinsic 0x9A) to `Kernel::resetRef`. 0x9A is a null
   entry in `U8Intrinsics`, so it returns 0 (`Unhandled intrinsic 154` in
   the log) and `killProcesses(0, type)` matches every item
   (`kernel.cpp:311`). Observed: one click on Aramina killed atHome and the
   PESANT3 activity on item 67 (pid 461); the Hrodny conversation killed
   Ingjald's loiter. With this change the four classes' activities are also
   in that set.
3. **NPCs in the fast area at a map switch return frozen.** The switch kills
   their activity (item nonzero, type not 1, `world.cpp:184`), writeback
   keeps their FLG_FASTAREA, and the return skips their enterFastArea
   usecode. They stand until they leave and re-enter the fast area. Seen for
   Aramina, Ingjald, and Hrodny. Predates this change; the pin moves
   Aramina's atHome into the killed set, which is the intended fix for the
   10-02 orphans.
4. **enterFastArea waits on the activity it spawns.** `spawn atHome() ->
   return;` compiles to `spawn; implies 01 01; pop temp; suspend` (ARAMINA
   0x01E3 to 0x01EF), where retail spawns without waiting (10-02). With a
   looping atHome the enterFastArea process lives as long as atHome, and its
   `process exclude` ends every later enterFastArea for Aramina. Together
   with finding 1 this is what holds the count at one.
5. **Three of the 13 new set-info sites are unreachable.** `at_home`,
   `in_field`, `at_work`, `in_house`, `at_still` and `ACT_LOITER` compile as
   0 in THORDIS, INGYALD, and HRODNY (build warnings at `THORDIS.UNK:282,287`,
   `INGYALD.UNK:123,128`, `HRODNY.UNK:170,175`), so every schedule test takes
   its first branch and `randomBarkInField`, `randomBarkAtStill`, and
   `randomBarkAtWork` never spawn. `ACT_LOITER` as 0 happens to be loiter.
6. **Hrodny's "Tell me more of the Cliffs." is a dead option.** The menu adds
   it at `lv-patched/HRODNY.UNK:485`; the handler is `case "Tell me more of
   the cliffs."` at `:1111`. Picking it redisplays the menu (two
   GumpNotifyProcesses for `use()` pid 1878, gumps 10231 then 10214).
   Hrodny's `use()` bytes are unchanged by this diff.
7. **Map 10's north-east village spams `Cycle in paint dependency graph`**:
   110,783 lines in session 1 (526/426, 707/426, 426/208, 426/856, 856/208),
   starting at the teleport there. 707 is the villager shape. Map art, outside
   this change; it floods the log about as fast as the 1037 warning.
8. The dropped-pragma warning text (10-02 finding 3) still claims the process
   "WILL be killed by the next map change" on the nine surviving lines.

## Harness anomalies

- `cp22-hastea.sav` loaded with a static camera. The fast area follows the
  camera, so Thordis never entered it while the Avatar walked up to 500 units
  from her. `CameraProcess::moveToAvatar` makes another static camera; a map
  round trip installs the follow camera (`world.cpp:207-213`).
- `MainActor::useBackpack` closes the console itself, and the driver's
  trailing `exit` leaked into the game and opened the minimap. The no-exit
  form opened the pack.
- The first Thordis double-click landed beside her while she walked
  (`E4a-thordis-click-missed.png`).
- The potion trace named class 766 and recorded nothing; the right class is
  1253.

## Disk changes

- `docs/playtest-2026-10-02-pt-activity.md` (this report) and 50 plates in
  `docs/playtest-2026-10-02-pt-activity/`.
- `shared/build/` rebuilt by `tools/build_artifacts.sh`: byte-identical
  (`c9180526`, `f92973ee`, new mtimes).
- `shared/data/u8-install/` rewritten by `./install_lv.sh` (EUSECODE
  `c9180526`, as before).
- `shared/u8-lv-patched/USECODE/EUSECODE.FLX` synced by `session.sh start`
  from `fcbe3c15` to `c9180526`.
- `~/.local/share/scummvm/saves/`: `ultima8.000`, `ultima8.001`, and
  `scummvm-history.txt` were overwritten and restored from the backup;
  `md5sum -c` passes on all 48 files. `~/.config/scummvm/scummvm.ini` restored
  (md5 `a143fa3b...`, unchanged).
- Scratch only: `/tmp/claude-1000/v1002b/` (reference FLX copies,
  disassemblies, session logs, mutation tree, drivers).
- No tracked file modified; the staged merge and the unstaged edits are as
  the author left them. `TODO.md` not touched.

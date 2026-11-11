# Process blocks as loops, verified statically and in engine (2026-10-01)

Change under test: the uncommitted merge of `worktree-agent-a9177e9b1a96238e0`
on `main` (HEAD `db28de4`), staged with `--no-commit`. A bare `process { ... }`
block now compiles as a loop (`u8c_parser.py` tags the block, `u8c_ast.py`
carries `kind`, `u8c_codegen.py` `_gen_process_block` emits label, body,
backward `jmp`). A `spawn X` without `-> return` no longer emits
`push pid` / `implies` / `suspend`. `lv-patched/LORDBRIT.UNK` drops the arrow
on `spawn puppet(lb)` and adds `[[PT_DEFAULT, referent]];` to `puppet()`.
New `lv-patched/CANTRK.UNK` and `MAGNET.UNK` add `return;` to their process
blocks.

Artifacts: EUSECODE `ae17224e` (1,505,621 bytes, md5-5000 `6cd470fd`), FIXED
`f92973ee`. Binary `scummvm-lv/scummvm` built 21:29 today, embedding
`1505621`. Every session's log read `usecode/eusecode.flx: 6cd470fd...,
1505621 bytes` and `Running Ultima VIII: Pagan (Gold Edition + Lost
Vale/DOS/English)`. Plates are in `docs/playtest-2026-10-01-process-loops/`,
640x400, named by test ID.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| S0 | Test estate | `tools/run_all_tests.sh`: 35/35, round-trip 516/516 | **PASS** |
| S0b | Full build and hashes | `tools/build_artifacts.sh` exit 0, all four OK, EUSECODE `ae17224e`, FIXED `f92973ee` | **PASS** (cascade done on disk, but unstaged: finding 9) |
| S0c | Compilation Report | 48 files, 46 succeed; failures `EALOGO.UNK`, `TJORVI.UNK`; 523 warnings | **PASS** |
| S0d | ScummVM fork | no fork commit since `e0d6084d`; `diff -q` of the fork diff against the tracked patch is silent | **PASS** |
| S0e | Maps, shapes | no builder, map, or shape-ID change in the diff | **not triggered** |
| S1 | Retail process sections end in a backward jump | 0x2FE protection/invisible, 0x40D's three, GUARD1's one: all jump back | **PASS** |
| S1b | ...and the new codegen matches retail's shape | every retail loop target is a `suspend` (`.L0634: 53`, `.L071C: 53`, `.L0494: 53`, `.L0BEF: 53`, `.L0CF6: 53`, GUARD1 `.L103D: 53`); `_gen_process_block` emits none | **FAIL** |
| S2 | Per-class diff lists exactly the claimed classes | 25 classes differ, 16 are pure LVFREE ripple; but LVFREE itself gains two loops and EggMagnet gains three | **PARTIAL** |
| S3 | shieldMonitor unreachable | only two npcnum-236 items exist, frames 0 and 1; frame 3 is never created | **PASS** (it would freeze if reached) |
| 1 | Lord British vision, egg path | frames read 2, 1, 6, 7, 2, 1, 6, 7, 2, 1 across the speech, then 9, then gone; `lbDone` 1; Avatar walks after; re-entry does not replay | **PASS** |
| 1b | Hunk B (PT_DEFAULT on puppet) under a map switch | the AVATAR `lbSpoke` detour killed the whole scene before `puppet` existed; `lbStarted` 1, `lbDone` 0 | **NOT DEMONSTRATED** (finding 8) |
| 2 | Protection potion expires | ACT_IMMORTAL (0x40000) set, cleared after 31 laps of 62 ticks (Int 15, limit 30); expiry slice calls LVFREE `safePlaySFX` | **PASS** (MAGIC2 not heard) |
| 3 | Aramina behaves normally | engine froze the moment she entered the fast area: CPU pinned, log and screen static for over a minute | **FAIL** |
| 4 | Map 17 candle trick and magnet | neither egg exists in FIXED.DAT (no quality 280 or 281 egg on any map) | **NOT DEMONSTRATED** (unplaced) |
| 5a | Shades scene runs to completion | completes; `avatarPoisoned` 1 to 0, `shieldFixed` 0 to 1; the quarrel now plays four exchanges where it played one | **PASS** (behaviour changed) |
| 5b | Poison plant scene (TypePoisonPlant) | class 0x59C has no dispatch and no caller; the live Passage Test (EggPlantTest) ran and set its flags | **NOT DEMONSTRATED** for TypePoisonPlant; EggPlantTest **PASS** |
| 6 | No new errors in the log | 0 `Non-existent process`, 0 `stuck in process loop`, 0 `Segmentation`, 0 `Assertion` in four sessions; the Aramina freeze is silent | **PASS** for the named lines (the freeze logs nothing) |

## Method and harness writes

Saves and `scummvm.ini` were copied to the scratchpad first (`bakv1001/`;
`ultima8.000` md5 `3e7dc241...`, `ultima8.001` md5 `083de199...`) and
restored byte for byte at the end. `./install_lv.sh` exited 0;
`session.sh start` synced FIXED (both copies) and EUSECODE into
`shared/u8-lv-patched/` (it held `6e6386f9` before). One ScummVM pid per
session; four sessions.

Writes, all disclosed:

- **Teleports with cheats on**, each followed by `Cheat::toggle` to
  `Cheats = false` before movement: Map 39 (17070, 20050, 48) for test 1;
  Map 41 (16671, 19200, 48) for test 3; Map 10 (20304, 17600, 4) for 5a;
  Map 10 (12800, 29720, 64) for 5b; Map 39 (17130, 19720, 48), inside the LB
  egg box, for 1b only.
- **Checkpoint loads** through slot 1 (`Ultima8Engine::loadGame 1`):
  `run-s16-tinytar.sav` (test 2), `run-s13-shield-halves.sav` (5a),
  `run-s7-ragnar-stone.sav` (5b).
- **`Item::grab`**: health potion 14823 (test 2), Passage stone 15048 (5b).
- **Save patching for test 2.** No debugger command creates an item or sets a
  frame. Potion 14823 (shape 859, npcnum 229, dispatching to LV TypePotion,
  class 1253) was grabbed, the game saved to slot 1, and the gzip save was
  patched in the scratchpad: the `Item` record with objid `e7 39` had its
  frame word changed from 1 to 5, and three Tiny Tars (3963, 8603, 14459)
  from 8 to 4. The patched save was loaded with `loadGame 1`, and
  `findShape 859` confirmed frames 5 and 4.
- `MainActor::toggleCombat` once (the shield-halves save loads in combat
  mode), `CameraProcess::moveToAvatar`, `Ultima8Engine::closeItemGumps`,
  `MainActor::useBackpack` (UI only), and `UCMachine::traceClass` 1037, 1253,
  1443 (logging only).

Every scene was entered by a walk except 1b. Every menu answer was clicked
from what the screen showed.

## S1b: the loop shape differs from retail, FAIL

Retail TypePotion (0x2FE, `shared/data/USECODE.FLX`, frozen disassembler):

```
061A..0632  startup: setImmortal; limit = Int*2
.L0634: 53  suspend            <- loop target
0635: 59    push pid           <- first statement of the body, wait(60)
...
0682: 52 AF FF  jmp -> 0634
```

`invisible()` has the same shape (`.L071C: suspend`, `0795: jmp -> 071C`).
Aramina's three process loops jump to `suspend` at 0x0494, 0x0BEF, and 0x0CF6;
GUARD1's (0x1194) jumps to 0x103D, also `suspend`. Across all retail classes,
184 backward jumps land on a `suspend` opcode. The suspend is the
compiler's per-lap yield, independent of the body. `_gen_process_block`
(`u8c_codegen.py`) emits `label; body; jmp label`, so a lap whose body does
not itself yield never returns to the scheduler. `UCMachine::execProcess`
loops `while (!cede ...)` (`uc_machine.cpp:170`), and the kernel's
"stuck in process loop" guard (`kernel.cpp:186`) counts process runs per
tick, so it never fires inside a single run. The result is a hard freeze.

`docs/reviews/2026-07-23-h1-process-block-semantics.md` specified
`.loop: suspend; B; jmp .loop` and states that a plain `jmp` wrap "freezes
the candle puzzle, the magnet puzzle, and the shield monitor". The added
`return;` in CANTRK and MAGNET covers two of those; Aramina's loops are not
in that review's table and are the ones that fire.

## S2: the per-class diff, PARTIAL

db28de4 was rebuilt from `git archive` into the scratchpad with
`build_eusecode.build(output_path=...)` and reproduced `7f885f5e` exactly.
Class-by-class comparison against `ae17224e`:

- 16 classes differ only in `call/spawn 05AEh <offset>` targets (AVATAR,
  SIGRID, RAGNAR, THORDIS, ATLI, INGJALD, HRODNY, TYORVI, EZREKAL, TYPERECE,
  TYPEBEDR, EGGPLANT, EGGAOCER, EGGCLOUD, EGGENDGA, EGGTEMPL): 0 changed lines
  outside those targets. All 214 LVFREE call and spawn sites in the new FLX
  land on a function entry (`init`).
- 9 classes gain backward jumps: ARAMINA (3), TYPEPOTI (1), TYPEAOFR (1),
  EGGCANDL (1), **EGGMAGNE (3: hatch, friskAvatar, cleanSweep)**, TYPEPOIS (1),
  TYPELORD (1), EGGSHADE (1), and **LVFREE (2: `wait()` at 0x018A, loop
  0x0196..0x019B; `changeRef()` at 0x0D3B, loop 0x0D44..0x0D99)**. The claim
  names EggMagnet with two and describes LVFREE only as the ripple source.
- A reachability check over each new loop (any path from head to the `jmp`
  passing no `suspend` or `ret`) found yielding laps on every path in
  TYPEPOTI, EGGCANDL, EggMagnet hatch and friskAvatar, TYPEPOIS, TYPELORD;
  non-yielding paths in ARAMINA atHome and inKitchen, TYPEAOFR, EggMagnet
  cleanSweep, and both LVFREE loops. (It also flagged EGGSHADE's
  `squabble()`, through `num = 0`; startup sets `num` to 1, so that path is
  infeasible.)
- Size deltas match: ARAMINA +9 is three 3-byte `jmp`s; TYPELORD +3 is
  `push pid` / `push retval` / `implies` / `pop temp` / `suspend` removed
  (7 bytes), `set info` added (7), and one `jmp` (3); EGGCANDL +4 and
  EGGMAGNE +11 add one `ret` per added `return;`. Counting `push pid`,
  `implies`, and `suspend` per class, old against new, every class matches
  except TYPELORD at one fewer of each, so the arrow-less spawn rule changed
  no other compiled call. LVFREE `wait()`
  compiles to `0196: push retval; jne -> 019B; ret; 019B: jmp -> 0196`, a
  spin with nothing to change `retval`. No class calls 0x05AE:0x018A or
  0x05AE:0x0D3B, so both are dormant.

## S3: shieldMonitor, PASS

`equip()` spawns `shieldMonitor()` only when `getFrame() = 3`. TypeAOFrizbee
(class 1260) dispatches only through npcnum 236, carried by exactly two
placed items, `build_map_17.py:512` (frame 0) and `:524` (frame 1).
SHADES creates frames 4 and 2 with `create`, which gives npcnum 0, so those
dispatch to the base shape class. Nothing sets frame 3. The body has no
`wait`: `c` races to 100 inside one run, so a reachable shieldMonitor would
freeze the engine.

## 1: Lord British vision, PASS

**Run 1** (fresh world): teleported to (17070, 20050, 48), cheats off,
walked north; egg 13742 logged `event 7 @ 05AF:0080`. A 150 s film
(`filmLB`, 375 frames) hashed the apparition's silhouette per frame: 25
distinct masks, changing on every 0.4 s sample for about 4.4 s, then one mask
held about 2.4 s, repeating through the whole bark. That is `puppet()`'s
`wait(5)` cycle and its `wait(120)` hold every fourth cycle
(`A1-puppet-mid-speech-f0020.png`, `A1-puppet-mid-speech-f0026.png`). The
bark text ended at about 102 s; the apparition then showed one dark pose,
still for about 4 s (`A2-end-pose-after-bark-f0256.png`), and was gone when
the camera returned.

**Run 2** (second fresh world), for direct frame reads: walked in, then read
`objectInfo 13745` every 8 s: frame 2, 1, 6, 7, 2, 1, 6, 7, 2, 1 through the
speech, **frame 9** at 148.8 s (`A2-frame9-read-148s.png`), and
`No such object` at 162.2 s. Shape 411's frames 7 to 10 are the dark poses
(`A2b-shape411-frames-0-to-10.png`).

After: `[06A5 01] = 1` (lbStarted), `[06A6 01] = 1` (lbDone),
`findShape 411: 0 found`, `ef: 0x122`. Two walks moved the Avatar 280 units
south-east and back (`A3-avatar-walks-after-scene.png`). No warning beyond
the three startup lines in either run.

**Negative control:** walking back into the egg box at (17074, 19702) logged no
`event 7`, no apparition reappeared, and the flags stayed 1/1
(`A4-reentry-no-replay.png`). The 26 September report documents the old
build's single held pose.

## 1b: hunk B under a map switch, NOT DEMONSTRATED

Hunk B exists for a map switch during the scene. The only map switch near the
scene is AVATAR.UNK's `lbSpoke` branch (`UNK files/UNK/AVATAR.UNK:1277-1310`):
on the first schedule tick off the Docks map it waits 240 ticks, teleports to
Map 0, calls `lb.use()` on a fresh shape 411, and teleports back. In the first three fresh worlds it fired before the walk reached the egg. In session 2 it left
`lbStarted` 0 (`C0-lbspoke-detour-returned-lbstarted-0.png`), so that
`lb.use()` never enters TypeLordBritish::use.

To overlap the two, session 4 landed inside the egg box. The scene started
(`tick 968 ... class 1443, offset 128`; `G0-hunkB-scene-running-before-detour.png`),
its last slice was at use() offset 479 (tick 1194), and then the log shows
`Unloading map 39` / `Loading Fixed items in map 0` / `Unloading map 0` /
`Loading Fixed items in map 39` and no further class-1443 slice. `puppet`
spawns at 0x0278 (632), so it never existed. After: `lbStarted` 1,
`lbDone` 0, `findShape 411: 0 found`, `No such object: 3330`
(`G1-hunkB-after-detour-scene-gone.png`). Finding 8 covers the consequence.

## 2: protection potion, PASS

Avatar Int 15, so `limit` is 30. Before drinking: `flags: 400`. The
frame-5 potion was double-clicked in the pack (`D2-drank-frame5.png`):
`Item: 14823 (shape 859) calling usecode event 1 @ 04E5:00A9`. With
`traceClass 1253` on, protection() (pid 331) reached the loop at tick
1784530, then logged 31 slices at offset 1272 (0x04F8, right after the
`wait(60)` suspend), each 62 ticks apart, the last at tick 1786452. That
slice continues into class 1454 (LVFREE) at offset 3208 (0x0C88), inside
`safePlaySFX(MAGIC2, 200)` at 0x0C68, whose body calls `playSFX` at 0x0C6E
before reaching 0x0C88; use() (pid 302) resumes at 1786510 when its
`implies` releases.

Polls of `objectInfo 1`: `flags: 40408`, then `40400` (ACT_IMMORTAL 0x40000
set; `D3-immortal-flag-set.png`), then `400` (cleared). 31 laps is
`counter > limit` with limit 30, so the expiry is exactly the source's.

Not shown: the MAGIC2 sound itself (the harness has no audio capture). A
damage-based control was planned and is impossible in this build: the
frame-4 potion pushes three of `receiveHit`'s four arguments and deals no
damage (finding 10; `D1-frame4-potion-no-damage.png`, HP 30 before and after).

## 3: Aramina, FAIL

Aramina (npc 13) stood on Map 41 at (16671, 16671, 48). With
`UCMachine::traceClass 1037` on, a teleport to (16671, 19200, 48)
(`B0-map41-arrival-south-of-aramina.png`), cheats off, and a walk north:

```
754: Item: 13 (shape 282) calling usecode event 15 @ 040D:0197
757: tick 26560 running process 564, item 0, type 0, class 1037, offset 407
762: tick 26560 running process 561, item 0, type 0, class 1037, offset 1007
```

Offset 1007 is 0x03EF, `atHome()`. After that line the log never grew
(42,967 bytes over more than a minute), `top` showed the process at 106 to
110% CPU, the console would not open, and frames 15 s and 75 s apart were
pixel-identical (`compare -metric AE` = 0), including after Escape and `i`
keypresses (`B1-frozen-t0.png`, `B1-frozen-t15.png`,
`B2-frozen-t75-after-keys.png`). SIGTERM did not end it; `kill -9` did.

Why atHome never yields, from the bytecode:

- `enterFastArea()` compares `araminaSchedule` against `at_home`,
  `chow_down`, and `on_throne`, all unknown identifiers compiled as 0
  (`WARN ARAMINA.UNK:105/111/117`), so the first branch always spawns
  `atHome()`.
- atHome's egg search compiles to `push byte 10; push 040Dh; loop`,
  meaning 10 units around item 0x040D (`No such object: 1037` in the
  console). Retail's is `10*32` units around npc 13 with a `type == 0xAE`
  script. Every lap's `foreach` therefore finds nothing.
- All of the lap's yields (`wait(30)`, `wait(300)`, the bark suspends in
  `randomBarkAtHome` and `closeDoor`) sit inside that `foreach`. With no
  per-lap `suspend`, the lap spins forever.

Static control: db28de4's atHome is the same body with no backward jump
(it ran once and returned). An in-engine run of the old FLX was not
possible: the binary's detection entry is pinned to `1505621` bytes.

`inKitchen()` has the same structure (yields only inside its `foreach`);
`atCourt()` yields on every path.

## 4: Map 17 candle trick and magnet, NOT DEMONSTRATED

A scan of the built FIXED.DAT for shape-73 eggs found quality 283
(EggPlant), 294 (EggShades), and 304 (LB scene) and none with 280
(EggCandleTrick) or 281 (EggMagnet), on any map. `build_map_17.py:299-345`
records the magnet egg's removal on 26 July and lists step 12 as deferred
("NOTHING CAN LIGHT A CANDLE", no candle art). No debugger command places an
egg. The headers of the new `lv-patched/CANTRK.UNK` and `MAGNET.UNK` say
"Reachable: ... placed on Map 17"; that line is wrong (finding 7).

Static reading of the new bytecode: EggCandleTrick hatch returns on every lap
(`021C: ret` inside the loop, `021D: jmp`); EggMagnet hatch and friskAvatar
return on every lap; cleanSweep yields on its `count < 1` and
`candlesCorrect` paths, and its `count >= 1` path does not, because
`spawn safePlaySFX(MAGIC1, 200)` emits nothing (`WARN MAGNET.UNK:535`). That
lap pops the items to (15615, 19839), where the next lap's filter excludes
them, so it is bounded to one lap. See finding 6 for hatch's call into
cleanSweep.

## 5a: the Shades scene, PASS (behaviour changed)

From `run-s13-shield-halves.sav` (Map 17, both halves in the pack,
`avatarPoisoned` 1): combat off, teleport to (20304, 17600, 4), cheats off,
1.5 s walk north. `Item: 9679 (shape 73) calling usecode event 7 @
05A5:0080`; Thordis (106) and Ezrekal (116) logged `event 15`.

The quarrel played past its first exchange: during it the screen showed
Thordis's exchange-3 line "If not for Ingyald, control him, I would not have
to! Encourage Ingyald in this, you do!" (`E0b-squabble-exchange-3.png`).
`squabble()` now runs `num` 1 to 4 before returning; the old build played
only exchange 1. The scene then asked, and the answers were clicked from the
screen: **Let's be reasonable!** (`E1-first-ask.png`), **Yes, Priestess.**
(`E2-second-ask.png`), "Now, reunited, we are..." (`E3-reunited-bark.png`),
the Shades in yellow (`E4-shade-speaks.png`), **Please, High Priestess.**
(`E5-heal-ask.png`), then the view back on the Avatar with the elders gone
(`E6-scene-ended-camera-on-avatar.png`).

After: `avatarPoisoned` 0, `shieldFixed` 1, `inShadeScene` 0, one shape-539
item, frame 2, in the pack.

## 5b: poison plant, TypePoisonPlant NOT DEMONSTRATED, EggPlantTest PASS

TypePoisonPlant (class 1436) has no dispatch path: shape 126 dispatches to
class 126, npcnum is a byte so 1436 - 1024 is out of range, and no compiled
class references 0x059C. `lv-patched/PLNTST.UNK` runs the Passage Test
inline in EggPlantTest (class 0x59A, which this merge only rippled).

**Negative control:** from `run-s7-ragnar-stone.sav`, with the stone not
in the Avatar's possession, the egg hatched (`Item: 7570 (shape 73) ...
059A:0080`) and nothing played; `haveMark`, `avatarPoisoned`, `plantScene`
all stayed 0 (`F0-no-stone-hatch-nothing-plays.png`).

**Positive:** reloaded, `Item::grab 15048` (the stone), teleport to
(12800, 29720, 64), walk north: `event 7 @ 059A:0080`, the whirlwind and
plant pops played (`F1-passage-test-scene.png`), and after: `haveMark` 1,
`avatarPoisoned` 1, `firstPoisoned` 1, `plantScene` 1, weight 40 to 30
(stone consumed). U8 eggs re-arm only on leaving the fast area
(`egg.cpp:46-62`), which is why the reload was needed.

## 6: log, PASS for the named lines

| Session | Lines | Non-existent | stuck | Segmentation | Assertion | Cycle in paint |
|---|---|---|---|---|---|---|
| 1 (LB run 1, Aramina) | 762 | 0 | 0 | 0 | 0 | 0 |
| 2 (LB run 2, potion, Shades, Passage Test) | 29,876 | 0 | 0 | 0 | 0 | 27,526 |
| 3 (hunk B attempt) | 304 | 0 | 0 | 0 | 0 | 0 |
| 4 (hunk B) | 107 | 0 | 0 | 0 | 0 | 0 |

All 27,526 paint-cycle lines are `426 -> 208 -> ... -> 426`, all logged while
the Avatar stood at Map 10 (21760, 8544) after loading `run-s16-tinytar.sav`,
and none after the Shades hatch. FIXED.DAT is unchanged by this merge.
Session 2 also logged 25 `Skipping invalid shape in sorter: 400,30..34`
during the Passage Test's whirlwinds, and the known `539,4` once on load. The
Aramina freeze produced no log line at all.

## Findings outside the plan

1. **The process loop has no per-lap `suspend`** (S1b). Every reachable
   process block whose body can complete a lap without its own `wait`,
   bark, or `-> return` spawn freezes the engine. The H1 review specified the
   suspend and named this failure mode.
2. **Aramina freezes the game on approach** (test 3). She is a retail NPC
   in East Tenebrae (Map 41) whose class this build replaces, so it reaches
   any player of this build who walks near her, on the base-game route too.
3. **LVFREE `wait()` and `changeRef()` are now non-yielding spins** with no
   callers today. Any future LV source that resolves `wait` to LVFREE
   instead of retail 0x0581 would freeze on its first call.
4. **shieldMonitor would freeze if reached** (S3). Unreachable today.
5. **TypePoisonPlant::use() would hold the Avatar in stasis until cured.**
   It ends `spawn poisonAvatar() -> return; setAvatarInStasis(false);`
   (`0F06..0F15`), and poisonAvatar now loops until `avatarPoisoned` clears.
   Unreachable today.
6. **EggMagnet's hatch never reaches friskAvatar while the candles are
   wrong.** `hatch()` calls `cleanSweep()` in its own process
   (`call 0598 0522`), and cleanSweep now returns only once
   `candlesCorrect` is true. `killMagnet()` cannot stop it:
   `killProcess` compiles to nothing (`WARN MAGNET.UNK:562`). The MAGNET.UNK
   header's statement that friskAvatar yields through
   `spawn safePlaySFX(...)` is also wrong: that spawn emits nothing
   (`WARN MAGNET.UNK:266`); `lv-patched-inventory.md:329` repeats it. Moot
   while the egg is unplaced.
7. **The CANTRK and MAGNET headers claim the classes are placed on Map 17.**
   FIXED.DAT has no quality 280 or 281 egg, and `build_map_17.py:299-345`
   says the egg was removed and the step is deferred.
   `agents/usecode-compiler/docs/lv-patched-inventory.md:301-302` and `:315`
   repeat the claim.
8. **The LB scene can be killed for good by AVATAR.UNK's `lbSpoke` detour**
   (1b): if the Avatar is in the egg box when the detour fires (240 ticks
   after the first schedule tick off the Docks map), use() dies at the map
   switch, leaving `lbStarted` 1 and `lbDone` 0. use() returns at once when
   `lbStarted` is 1, and `MYTHRDLG.UNK:37` branches on `lbDone`, so step 1
   cannot finish. Exposure in real play depends on where a walking player
   first enters Map 39; reaching the egg requires arriving next to it. Hunk B
   does not help because the use() process itself dies.
9. **The rehash cascade is unstaged.** `shared/build/ARTIFACTS.sha256` and
   `build_scummvm.sh` show ` M` (working tree only). Committing the staged
   merge alone would ship a compiler that builds `ae17224e` against a
   canonical `7f885f5e`, and `tools/build_artifacts.sh` would fail
   verification on a clean checkout.
10. **The frame-4 (poison) potion deals no damage.** `TypePotion::use()`
    compiles `receiveHit` with three of its four arguments
    (`calli 0Ah 0053h`, 10 bytes including `this`; `POTION.UNK:96`).
    Pre-existing.
11. **The invisibility potion is a stub.** `TypePotion::invisible()` loses
    its body to parse errors (`POTION.UNK:206`, `:210`, `:228`) and compiles
    to `playSFX; set info; setFrame(0); ret`. Pre-existing.
12. **Paint-order cycles at Map 10 (21760, 8544):** 27,526 lines between
    objects 426 and 208 after loading `run-s16-tinytar.sav`. Not caused by
    this merge.
13. **The new `test_uc_lordbrit.py` cannot see a missing yield.** Its
    simulator treats op 0x53 as an unconditional no-op (the test's own
    comment, line 51), and its static check (line 148) asserts only that the
    backward `jmp` lands at the top of the process section. A lap-level
    `suspend` check over every `kind='process'` block, as the H1 review's
    verification plan describes, would have caught Aramina.

## Harness anomalies

- SIGTERM from `session.sh stop` did not end the spinning ScummVM; it needed
  `kill -9`.
- With `run-s16-tinytar.sav`'s parked camera, `i` opened the backpack off
  screen (`event 1 @ 0211:0103` logged, nothing visible); `b` did nothing.
  `MainActor::useBackpack` after `moveToAvatar` worked.
- Console commands consume game ticks in this build: the 240-tick `lbSpoke`
  detour fired while cheats were being toggled.
- The scratchpad held a stale `build.log` from an earlier session, which
  `noclobber` refused to overwrite; the build was rerun into
  `build-v1001.log`.

## Disk changes

- `docs/playtest-2026-10-01-process-loops.md` (this report) and 31 plates in
  `docs/playtest-2026-10-01-process-loops/`.
- `shared/build/` rebuilt by `tools/build_artifacts.sh`: byte-identical to
  what was there (`ae17224e`, `f92973ee`; mtimes 21:34).
- `shared/data/u8-install/` rewritten by `./install_lv.sh` (same bytes).
- `shared/u8-lv-patched/` synced by `session.sh start`: FIXED.DAT (both
  copies) and USECODE/EUSECODE.FLX now `f92973ee` / `ae17224e` (EUSECODE was
  `6e6386f9`).
- `~/.local/share/scummvm/saves/`: slot 1 was overwritten during the session
  and `ultima8.000` was autosaved; `ultima8.000`, `ultima8.001`, and
  `scummvm-history.txt` were restored from the backup and all 48 files now
  match it (md5 `3e7dc241...`, `083de199...`). `scummvm.ini` is unchanged.
- No tracked file was modified; the staged merge is as the author left it.

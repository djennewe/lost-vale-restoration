# Lord British scene and the lbSpoke detour, verified in engine (2026-10-04)

Change under test: new `agents/usecode-compiler/src/lv-patched/AVATAR.UNK`,
a byte copy of `shared/data/lv-usecode/UNK files/UNK/AVATAR.UNK` plus
`globalflag lbStarted;` and, after the `lbSpoke` branch's `wait (240);`,
`if lbStarted = 1 { return; }`; new `test_avatar_lbspoke_guard.py`; the
rehash in `build_scummvm.sh` and `shared/build/ARTIFACTS.sha256`. It answers
`docs/playtest-2026-10-01-process-loops.md` 1b and finding 8.

Artifacts: EUSECODE `18cc709c...`, 1,507,250 bytes, first 5000 bytes md5
`98b11c63...`; FIXED `079829c1...`. Plates are in
`docs/playtest-2026-10-04-lb-detour/`, 640x400.

## Verdicts

| ID | Claim | Observed | Verdict |
|---|---|---|---|
| C0 | Build, estate, compile, fork, binary | build exit 0, four OK; estate 38/38 (`test_avatar_lbspoke_guard.py` 4 passed); Compilation Report 46 of 48, the `DEV_ALLOWLIST` pair; the guard is in class 0x401 at 0x1963; fork patch equals the fork diff; binary built 13:31, after the rehash | **PASS** |
| L0 | Detection | every session log: `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: 98b11c635407f0f7f3c304e10615ae44, 1507250 bytes.` | **PASS** |
| L1 | Scene started inside the 240 ticks: no Map 0, scene completes on frame 9, flags 1/1/nonzero | two fresh worlds: detour and scene start on the same tick; the detour wakes at the guard 242 ticks later and ends; 0 `Loading Fixed items in map 0`; apparition read **frame 9** on the `lbDone` slice, gone after; `lbStarted` 1, `lbDone` 1, `lbSpoke` 1 | **PASS** |
| L2 | Ordinary case: detour to Map 0 and back, then the egg plays the full scene | detour woke at the guard with `lbStarted` 0, went to Map 0 and back; walking into the egg played the scene; **frame 9**; `lbDone` 1; the Avatar walks after | **PASS** |
| L3 | Mythran's post-message conversation opens | double-click on NPC 33 (`event 1 @ 0421:A125`) barked "Ah. So the message has arrived at last..." (the `lbDone` branch) | **PASS** (one harness stasis release, finding 1) |
| L4 | 0 process errors, no segfaults, no assertions | 0 segfaults, 0 assertions, 0 `stuck`; one `Non-existent process PID (0) in implies` in each world where Devon's farewell ran to its end, on Map 3 before any map switch, with no traced class-1025 slice in between | **PARTIAL** (one line per fresh world, outside the changed code, finding 2) |

## Method and harness writes

Saves (48 files, md5 list) and `scummvm.ini` (`a143fa3b`) were copied to the
scratchpad (`lbbak/`) first and restored at the end; `md5sum -c` passes on
all 48, the names match, and the ini reads `a143fa3b`. `./install_lv.sh`
exited 0. `session.sh start` synced EUSECODE into `shared/u8-lv-patched/`.
Three sessions, each a fresh world, one ScummVM pid each. Devon's opening
menu was answered by clicking **Goodbye** from the screen.

Writes, all disclosed:

- **Teleports with cheats on**, each followed by `Cheat::toggle` back to
  `Cheats = false` before movement or talk (each confirmed in the log).
  Session 1: Map 39 (17130, 19720, 48), inside the egg box; Map 8 (1611,
  1827, 0) and (1696, 1216, 48), beside Mythran. Session 2: Map 39 (17070,
  20050, 48), on the lane outside the box. Session 3: Map 39 (17130, 19720,
  48).
- **`Ultima8Engine::toggleAvatarInStasis`**: used in pairs to read the state
  (each call prints the new value, so two calls restore it), and once in
  session 1 to clear the stasis that blocked Mythran (finding 1).
- `UCMachine::traceClass` 1025 (AVATAR), 1443 (TypeLordBritish), 1455
  (EggLBScene); `debugflag_enable Object`. Reads: `objectInfo`, `findShape`,
  `getGlobal` (`0x405 2` lbSpoke, `0x6A5 1` lbStarted, `0x6A6 1` lbDone).
- No save written, no checkpoint loaded, no `Item::grab`.

The L1 landing is a debug teleport by design (it is 1b's setup). The L2
scene was entered by a walk. Mythran was talked to by a double-click on his
sprite.

**How the overlap was obtained.** Console reads pause the kernel (the
`tick` counter stops while the console is attached), so they cannot widen
the 240-tick window, but the gap between closing one console and opening the
next does run ticks. The overlap does not depend on that. The teleport
lands the Avatar inside the egg box; the egg hatches and spawns `use()` on
the arrival tick, and the same map switch starts the `schedule()` detour on
that same tick. In both L1 worlds the trace shows the two starting on one
tick (3022 and 5140), so the scene was always 240 ticks ahead of the guard.

## C0: build, tests, bytecode, PASS

- `tools/run_all_tests.sh`: `OVERALL: PASS — 38/38 test file(s)`;
  `test_avatar_lbspoke_guard.py PASS ... 4 passed, 0 failed`.
- `tools/build_artifacts.sh`: exit 0; `TYPEFLAG.DAT OK 9f534e59`,
  `U8SHAPES.FLX OK a611e9be`, `EUSECODE.FLX OK 18cc709c`, `FIXED.DAT OK
  079829c1`. EUSECODE is 1,507,250 bytes; `head -c 5000 | md5sum` gives
  `98b11c635407f0f7f3c304e10615ae44`, matching `build_scummvm.sh:54-55` and
  `scummvm-lv/engines/ultima/detection_tables.h:297`.
- Compilation Report: 48 files, 46 succeed, failures `EALOGO.UNK` and
  `TJORVI.UNK`. The patched `AVATAR.UNK` logs three parse errors (lines 57,
  566, 1249); the unpatched original gives the same three at lines 24, 533,
  and 1216 (33 added lines earlier), and both parse to seven functions, so
  they predate the patch.
- Class 0x401, disassembled from the built FLX: the wait at 0x194B..0x1962
  (`push 00F0h`, spawn of the wait routine, `suspend`), then `1963: push
  global 06A5h 01h; cmp; jne -> 196E; 196D: ret`.
- Fork: `lost-vale` tip `e0d6084d`; the patch-equality `diff -q` printed
  nothing. `scummvm-lv/scummvm` built 2026-10-04 13:31 CDT.

Two details of the source support the guard's timing. `use()` sets
`lbStarted` before its first `wait` (`lv-patched/LORDBRIT.UNK:90-94`), and
the spawn handler runs a new process once immediately, so the flag is up in
the hatch's own slice. And the guard and the teleport share one slice (no
yield between `wait (240)` and `Avatar.teleport`), so no scene can start
between the check and the teleport.

## L1: scene before the detour, PASS

**Session 1.** Fresh world; flags 0, 0, 0 on Map 3. Traces on; teleport into
the box. Log, in order:

```
Unloading map 3 / Loading Fixed items in map 39
tick 3022 running process 174, ... class 1025, offset 6411      (schedule)
tick 3022 (still) running process 174, ... class 1025, offset 6484   (the wait)
Item: 3330 (shape 73) calling usecode event 7 @ 05AF:0080
tick 3022 running process 104, ... class 1455, offset 128      (egg hatch)
tick 3022 running process 105, ... class 1443, offset 128      (use())
tick 3264 running process 174, ... class 1025, offset 6499     (0x1963, the guard)
```

Process 174 never ran again; `use()` ran to tick 9558, and the egg's hatch
resumed at 9560. No `Loading Fixed items in map 0` anywhere in the session.
Frame reads every 10 s or so gave 5, 1, 3, 2, 1, 5, 7, 2, 2, then gone at
110.5 s (`L1-01`, `L1-02`, `L1-04-last-read-frame2-99s.png`); the sampling
missed the last pose, but the trace shows it. `use()` resumed at offset 1402
(0x57A) on tick 9340 and set `lbDone` (0x57C). The puppet (process 34)
resumed at 1734 (0x6C6) on tick 9348 with no `(still)` continuation and never
ran again. From 0x6C6 the only way to end without a suspend is `lbDone = 1`
→ `setFrame(9)` (0x6D0..0x6D4) → `ret` (0x6DA). After: `lbSpoke` 1,
`lbStarted` 1, `lbDone` 1 (`L1-03-after-scene-session1.png`). The Avatar was
in stasis in that world (finding 1).

**Session 3, the clean repeat.** Fresh world; Devon's farewell waited out
(stasis read `false`, flags 0, 0, 0) before the teleport:

```
tick 5140 running process 106, ... class 1025, offset 6411
tick 5140 (still) running process 106, ... class 1025, offset 6484
Item: 3076 (shape 73) calling usecode event 7 @ 05AF:0080
tick 5140 running process 117, ... class 1443, offset 128
tick 5382 running process 106, ... class 1025, offset 6499
```

A watcher read the apparition on the `lbDone` slice (process 117, offset
1402, tick 11458, 121.9 s after the teleport): `Item 3075 (class
Container, shape 411) (uc: GHOST), 9, (17150, 19850, 48)`
(`L1b-02-final-pose-frame9.png`); 8 s later `findShape 411: 0 found`. After:
`lbSpoke` 1, `lbStarted` 1, `lbDone` 1; stasis `false`; a 1.5 s walk moved
the Avatar from (17130, 19720) to (17818, 20000)
(`L1b-03-after-scene-walked.png`). 0 `Loading Fixed items in map 0` in the
session.

The negative control is 10-01's session 4 on the build without the guard
(the same landing teleported to Map 0 at that point and killed `use()`), and
L2 below, where the same guard falls through and teleports because the
scene has not started.

## L2: ordinary case, PASS

Session 2, fresh world, farewell waited out (stasis `false`). Teleport to
the lane at (17070, 20050, 48), outside the egg box:

```
tick 9324 running process 218, ... class 1025, offset 6411
tick 9566 running process 218, ... class 1025, offset 6499     (guard, lbStarted 0)
Loading Fixed items in map 0
tick 9566 (still) running process 218, ... offset 6603
... (the Map 0 Lord British, process 156)
tick 9750 running process 218, ... offset 6715
Loading Fixed items in map 39
```

Back on the lane: `lbSpoke` 1, `lbStarted` 0, `lbDone` 0, stasis `false`
(`L2-01-back-from-detour-on-lane.png`). The detour's own `lb.use()` left
`lbStarted` 0, as 10-01 found. A straight walk north from x 17070 is blocked
by the outer wall's posts, so the route went east along the lane, north into
the courtyard at x 17650, and west into the box: egg 14125, `event 7 @
05AF` (`L2-02-scene-start-after-walk-in.png`). On the `lbDone` slice the
apparition read frame **9** (`L2-03-final-pose-frame9.png`); 8 s later it was
gone. After: `lbSpoke` 1, `lbStarted` 1, `lbDone` 1; stasis `false`; a walk
moved the Avatar from (17214, 19654) to (17682, 19922)
(`L2-04-after-scene-walked.png`).

## L3: Mythran, PASS (with a harness stasis release)

After session 1's L1 scene, teleport to Map 8 beside Mythran's house, then
upstairs at (1696, 1216, 48); Mythran is NPC 33 (`docs/playtest-2026-09-01-
stock-bindings-climb.md`), wandering around (1464..1876, 1180..1476, 48).
Clicks first answered `Can't look: avatarInStasis` and `Can't use:
avatarInStasis` (finding 1); one `toggleAvatarInStasis` cleared it. Several
strikes hit furniture while he walked; the third standstill strike logged
`Item: 33 (shape 190) calling usecode event 1 @ 0421:A125`, and he barked
"Ah. So the message has arrived at last. I confess, my friend, I have been
expecting you -- or someone very much like you. Some time ago, I received a
vision. In..." (`L3-03-mythran-reply.png`, `L3-04-mythran-lbdone-bark.png`).
That is the first bark of `MYTHRDLG.UNK`'s `if lbDone` branch with
`mythranToldZealans` unset. The conversation was not followed further.

## L4: log health, PARTIAL

| Session | Content | Lines | Non-existent | stuck | Segmentation | Assertion | Cycle in paint | Map 0 loads | Unhandled |
|---|---|---|---|---|---|---|---|---|---|
| 1 | L1, Map 8, Mythran | 8,570 | 0 | 0 | 0 | 0 | 3,534 | 0 | 3 |
| 2 | L2 | 3,386 | **1** | 0 | 0 | 0 | 0 | 1 (the detour) | 0 |
| 3 | L1 repeat | 1,801 | **1** | 0 | 0 | 0 | 0 | 0 | 0 |

The two `Non-existent process PID (0) in implies` lines are finding 2. The
paint cycles are all on Map 8 (finding 3). The three unhandled intrinsics are
`Npc::getNpcSlot()` for Mythran (item 33), the same family as Ezrekal's.

## Findings outside the plan

1. **The detour's release had been covering a stuck stasis.** In session 1
   I teleported off Map 3 while Devon's farewell was still running (about 30
   s of console reads, which pause the game, came between the Goodbye click
   and the teleport). `enterConvo()` freezes the Avatar, and the map switch
   killed the conversation before it could unfreeze him. On the old build
   the detour's `setAvatarInStasis(false)` (`AVATAR.UNK:1345` in the patched
   file) released it four seconds later; with the guard, nothing did, and
   the Avatar stayed in stasis through the scene and onto Map 8. In sessions
   2 and 3, with the farewell finished first, stasis read `false` before and
   after, and he walked. A player cannot leave Map 3 mid-conversation on
   foot, so I read this as a harness artifact. But any other way of
   changing maps while frozen (a scripted teleport out of a frozen scene)
   would now leave the freeze in place when it used to be cleared. My
   earlier sessions' "first teleport fires the Guardian cutscene" was this
   same detour. Sure of the readings; the mechanism (conversation freeze
   cut off by the map switch) is inference from the timing, about four
   chances in five.
2. **Devon's farewell ends with `Non-existent process PID (0) in implies`.**
   In both worlds where the farewell ran to its end, the warning followed
   Devon's `LV: I_resetRef item=2` lines on Map 3, before any map switch.
   Session 2 had the class-1025 trace on, and no AVATAR slice ran between
   the resetRef lines and the warning, so the changed branch did not produce
   it. Whether it predates this change was not established: the earlier
   sessions this week all teleported mid-farewell. Sure of where it sits;
   the source is Devon's conversation code by position, about four chances
   in five.
3. **Map 8's leftover backstop apparition causes paint cycles.** With the
   scene played at Tenebrae, item 14080 (shape 411) stands at (2200, 2326, 8)
   until the player walks into the backstop egg at (2200, 2230); my teleport
   skipped it. While it was on screen the log took 3,533 `Cycle in paint
   dependency graph 182 -> 411 -> ... -> 182` lines (the line prints shape
   numbers). No fixed shape 182 lies near it, so the partner is a non-fixed
   item. Map 8 is unchanged by this change. A walking player clears it on
   the approach, so exposure is small.
4. **10-01's "walked north" to the egg from (17070, 20050) does not work on
   today's map**: the outer wall's posts at y 19822..19967 leave gaps under
   a body's width. The courtyard is entered from x ~17540 east.

## Harness anomalies

1. Mythran wanders while each position read pauses the world, so the
   standstill strike aimed at stale positions three times and hit furniture
   (shapes 157, 164, 239); a bald figure beside the Avatar was not him.
2. The first frame sampling (every 10 s) straddled the 3.5 s frame-9 hold;
   a log watcher keyed on the `lbDone` slice caught it in sessions 2 and 3.

## Disk changes

- `docs/playtest-2026-10-04-lb-detour.md` (this record) and 16 plates in
  `docs/playtest-2026-10-04-lb-detour/`.
- `shared/build/` rebuilt by `tools/build_artifacts.sh` (recorded hashes);
  `shared/data/u8-install/` by `./install_lv.sh`;
  `shared/u8-lv-patched/USECODE/EUSECODE.FLX` synced to `18cc709c`.
- Saves and `scummvm.ini` restored and verified; no save was written.
- Scratch only, under
  `/tmp/claude-1000/-home-douglas-projects-lost-vale/3b99e1ce-cfb9-4426-91ac-2a8e98a8eca2/scratchpad/`:
  `lbbak/`, `lblogs/` (tests, build, install, three session logs), `lbsp/`
  (disassemblies of 0x401, 0x5A3, 0x5AF, 0x232).
- No tracked file modified; nothing committed; `TODO.md` not touched.

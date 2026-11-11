# Leftovers: Thordis lag, Atli's shield option, Tyorvi's drunk path, Mythran's scroll-back (2026-10-10)

**Build under test.** `main` `13e2731`, plus the uncommitted `build_scummvm.sh` detection change.
- **Game copy.** `/tmp/claude-1000/vleft/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Every hash matches `shared/build/ARTIFACTS.sha256`: EUSECODE `ebf03413…`, FIXED `511902e8…` in both places, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…` and ANIM `77e9705d…`.
- **Engine log line.** `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1523533 bytes`.
- **Binary.** `scummvm-lv/scummvm` has mtime 01:08:09, which is after fork `11bb31bd` (01:01:11).
- **Patch check.** `PATCH_EQUAL`. The command was `git diff 01bd8879 HEAD -- engines/ ':!…detection_tables.h' | diff -q - …patch`.
- **Harness.**
  - Xvfb `:94` (1280x800), with the window at (480,300).
  - `scummvm.ini` sets `usehighres=true` and **`frameLimit=true`**. Audio was `SDL_AUDIODRIVER=dummy`, and there was a private `saves/`.
  - The driver is the `veng` `drv.py`/`h.py`, re-pointed to this display and directory.
  - The second launch ran under `gdb` (`rungdb.sh`) so that I could take a backtrace if the engine hung; see anomaly 1.
- **Not run, on instruction:** `run_all_tests.sh`, `build_artifacts.sh`, `install_lv.sh` and `build_scummvm.sh`. The hash match stands in for them.
- **Plates.** They are in `docs/playtest-2026-10-10-leftovers/`.

**The session hit the request budget during T2.** T3 and the q83 half of T2 were not run.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| T1 | When the scene-end talk is skipped and the Avatar walks off, Thordis reaches home in the same pass as Atli's event 8, and plantScene reads 0 | **PASS**, natural hour with no time skip. Negative control (Avatar stays on the plateau) **PASS**. Talk control **PASS** |
| T2 | Atli's "I have this shield!" with atliMet 0 | **PARTIAL**. The q0 828 case **PASS**: the option appears and works. The q83 case is **NOT DEMONSTRATED** (budget; nothing was set up) |
| T3 | Tyorvi's drunk path: "Shut up and drink it!" and the Key | **NOT DEMONSTRATED** (budget). It last passed on the `49f44ee3` build (`playtest-2026-10-09-quirks.md` Q3); TYORVI is not in this change |
| T4 | Mythran (MYTHRDLG): after the talk the camera scrolls back exactly once, and Mythran resumes his activity | **PASS** |
| L | Log hygiene | **FAIL, but not from this change [INFERENCE]**. There are **11 `Seem to be stuck in process loop`** lines, all from walking the Avatar at the `run-s1-lbdone` load point (finding 1). Everything else is 0: `Unhandled intrinsic`, Segmentation, Assertion, segment access, `Cycle in paint` and `PID (0) in implies` |

**State writes.**
- `CameraProcess::moveToAvatar`, twice. Both old saves load with a parked camera (finding 3).
- `Item::grab 764`, which put Pagan's q0 828 in the pack. The pickup itself was not under test.
- Two teleports with cheats on, each followed by a verified `Cheats = false`: to Map 8 (2150,2440,48), upstairs near Mythran, and to Map 10 (19400,7200,0), near Atli.
- `Ultima8Engine::toggleAvatarInStasis`, once as a read pair (`true`, then `false`).
- **No `setGlobal`, no save written, no time skip.** Every talk and every menu answer was a click on the screen.

## T1: Thordis off the plateau in the same pass, PASS

**The save.** `cp10-test-done.sav` (md5 `0f9ba07e…`) is at game time 26161 s (hour 29.07) with plantScene 1 and endOfPlantScene 0. On load, Thordis was at (13103,29759,64) and the Avatar at (13055,30079,64) (`T1-00-load`).

**Route without the talk.**
1. **The walk.** I walked north down the ramp, (13055,30079,64) → (12951,29303,64) → (12833,28485,24) → (12833,26821,0). No teleport.
   - The camera had stayed parked on the plateau, and the Avatar stalled once he left the fast area. `CameraProcess::moveToAvatar` fixed it, and the walk went on (finding 3).
2. **Before the pass.** Thordis was at (13343,29519,64) and plantScene was 1 (`T1-02-off-plateau`).
3. **The pass.** It was the natural hour 29→30 crossing, about 595 s after the walk began. The scheduler lines are in slot order:
   ```
   Item: 106 (shape 707) calling usecode event 8 @ 046A:023F
   Item: 106 (shape 707) calling usecode event 16 @ 046A:03E7     <- she leaves the fast area in HER slot
   Item: 107 (shape 707) calling usecode event 8 @ 046B:0196
   ```
4. **Read right after the pass.**
   - Thordis is at **(4415,7423,0)**, m10.
   - Atli is at (19231,6943,0).
   - **plantScene is 0** and endOfPlantScene is 0 (`T1-03-after-pass`).
   - The teleport landed between 106's event 8 and 107's, so the self-heal in Thordis's own slot did it.

**Negative control: the Avatar stays on the plateau. PASS.** I reloaded the same save and left the Avatar at (13055,30079,64), inside x[12288,13312) y[29184,30208), for the whole natural hour-30 pass. The pass logged events 8 for 106 and 107. Afterwards plantScene was **still 1**, Thordis was at (13163,29699,64) on the plateau, and Atli was unmoved at (19122,9684,8) (`T1-04-neg-on-plateau-after-pass`).

**Control: the scene-end talk taken. PASS, as before.**
- **The talk.** In the same world, a double-click on Thordis logged `event 1 @ 046A:0ECD`, and the aftermath barks played (`T1-06-sheet`, `T1-07-sheet`).
- **After the talk.** plantScene 0, endOfPlantScene 1, 0x0F 0. Thordis stayed on the plateau at (13163,29411,72), and the camera was back on the Avatar (`T1-08-after-talk`).
- **The next pass.** I walked off by the same ramp to (12787,26846,0). At the next natural pass (hour 31), Thordis went to **(4415,7423,0)** and Atli to (19231,6943,0). endOfPlantScene stayed 1 (`T1-09-control-after-pass`).

## T2: Atli's "I have this shield!", PARTIAL

**The world.** `run-s1-lbdone.sav` has atliMet 0 and lbDone 1. `findShape 828` gives `Item 764 … (1090, 1678, 64) q: 0, f: 0x3400`. `Item::grab 764` put it in the pack: weight 20 → 50, and it is now at `(0, 0) q: 0`. I teleported to Map 10 (19400,7200,0).

**The chain, every answer clicked.**
1. A double-click on Atli logged `event 1 @ 046B:0392`.
2. **May I speak with you?** (`T2r-01-menu1`).
3. **I am not a Pagan.** (`T2r-02-menu2`).
4. **How do you know it is treacherous?** (`T2r-03-menu3`). The menu became **I am not a Hoskuld! / I am from Brittania! / Who or what are the Hoskulds? / bye** (`T2r-04-menu4`).
5. **I am from Brittania!** is a dead option (finding 2). Picking it re-showed the same menu: the GumpNotifyProcess changed from 8119/gump 13453 to 8166/gump 13444, with no bark (`T2r-06b-menu-redisplayed`).
6. **I am not a Hoskuld!** gave "Prove it!" (`T2r-07-prove-it`).
7. **The menu then offered "I have this shield!"**: I am from Brittania! / Who or what are the Hoskulds? / **I have this shield!** / You will have to trust me. / bye (`T2r-08-menu-shield`).
8. **Picking it** gave "Where got that did you? Looks it does much like the stories say the Shield-Which-Was-Broken looked! A wonderous item you have! Perhaps from the other…" (`T2r-09-shield-answer`, `T2r-10-shield-answer-b`).

**Static support for the q83 half (not in-engine).** The compiled loop at `046B:20FF-2137` is `loop … container+recursive`, then `calli 0019 Item::getQ` on the loop variable, `push byte 83`, `ne`, and `jne → loopnext`, with the `append "I have this shield!"` only on the not-83 path (`vleft/atli.dis:1293-1320`). The guard is compiled in, and the loop's back edge matches the unchanged hammer loop that follows it.

**q83: NOT DEMONSTRATED.** For a rerun:
- **Option (a).** Use `Item::setQuantity 764 83`. It writes the same `_quality` field [INFERENCE: check `cmdSetQuantity` first]. There is no `setQuality` command in the fork's debugger.
- **Option (b).** Use the q83 Shield from `run-s13-shield-halves` after the ceremony, in a world reset to atliMet 0 (fabricated).
- **The menu to read.** In either case, read step 7's menu, which should have 4 rows, not 5.

## T4: Mythran, PASS

**The world.** `run-s1-lbdone` (lbDone 1, Mythran intro not done). I teleported upstairs to (2150,2440,48) because walking from the load point hangs (finding 1). Mythran was loitering at z 48 (`T4-01-before-talk`).

**Talk 1.**
- **The talk.** It logged `event 1 @ 0421:A125`. The camera centred on Mythran with "Ah. So the message has arrived at last…" (`T4-02-talk-start`), then the menu **Tell me of this ancient race. / Lord British says they can help me. / Let us speak of other matters. / Farewell.** (`T4-03b-menu`).
- **Farewell** gave "Go carefully, my friend. The path you walk leads into the unknown…". The camera went back to the Avatar (`T4-04-after-farewell`).
- **Afterwards.** 0x0F 0, and Mythran had a **new `LoiterProcess 4009`** (it was 1410).
- **Walking.** Walking moved the Avatar to (2318,2504,48) with the camera following (`T4-05-walk-after`).
- **Gap.** My frame capture had a gap at the moment of this scroll, so talk 1 does not count toward "once".

**Talk 2 (the measured one).**
- **The menu.** "Welcome back, my friend…" (`T4-06-talk2-menu`), then the same menu.
- **The film.** I clicked **Farewell.** with a capture thread running throughout: 338 frames over 70 s. Phase correlation between consecutive frames (rows 130-400) found exactly **one** camera motion. It ran over frames 188-193 (t = 39.5…40.5 s, after the farewell bark), monotone, in steps of (-6,2) (-8,3) (-9,3) (-7,2) (-10,3) (-5,2), for a total of (-45,15) px. Then nothing moved for the remaining 29 s (`T4-07-farewell-scroll-sheet`).
- **Mythran resumed.** The log shows `Item: 33 … event 15 @ 0421:01A7`, and a new `LoiterProcess 5745`. The last frame shows him moved off his talk spot.

**Source check.** MYTHRDLG ends in a single `exitConvo()`; its only mention of `scrollBack` is in the comment. A second scroll to the same point would be invisible to film [INFERENCE: it would also be invisible to a player].

## L: log hygiene

`vleft/lv_run.log` has about 8,000 lines across two launches (the first launch is also kept as `lv_run.part1.log`).

| Pattern | Count |
|---|---|
| `Seem to be stuck in process loop - killing current process!` | **11** (finding 1) |
| `Unhandled intrinsic`, Segmentation, Assertion, `Trying to access segment`, `Cycle in paint` | 0 each |
| `Non-existent process PID (0) in implies` | 0, across three Thordis/Mythran/Atli farewells |

## Findings outside the brief

1. **Walking from the `run-s1-lbdone` load point freezes the engine and trips the runaway guard, which kills the Avatar mover and the scheduler.**
   - **Where.** The Avatar loads at Map 8 (2200,2300,8), frame 885, inside the LB backstop egg's box.
   - **Reproduced four times.** Two mouse walks and two keyboard Up taps each froze the world for about 30 s (log silent, console unreachable, CPU ~90%). Each logged 2-3 `Seem to be stuck in process loop`.
   - **Control.** Idling 36 s after the same load logged 0 warnings.
   - **After a trip.** `Kernel::processTypes` lists **no U8AvatarMoverProcess and no SchedulerProcess**. Walking is dead until a reload, which recreates both (the fork's load-time guard).
   - **Escape.** Teleporting away before any movement avoids it.
   - **Not established.** I did not get a backtrace (`ptrace_scope` 1 blocks attaching; the gdb-launched rerun never re-tripped it because it teleported first). Whether fork `11bb31bd`'s `_zLost` path is involved is open. The 10-09 lane report saw the same 3× guard with a wall-wedged Avatar on `bbcfa209`, so the guard firing on a wedged mover predates it.
   - **Confidence.** High that it reproduces; open on the cause. It affects anyone using this checkpoint for Mythran or Atli work.
2. **Atli's "I am from Brittania!" (with "!") is a dead option, and it is a 1994 defect.**
   - **Where.** After "How do you know it is treacherous?", the menu adds `"I am from Brittania!"` (`lv-patched/ATLI.UNK:957`, recovered `LOST VALE/ATLI.UNK:584`). The only case for it is `"I am from Brittania."` with a period (recovered `:608`), so the pick re-shows the menu.
   - **Workaround.** "I am not a Hoskuld!" reaches the same "Prove it!" branch.
   - **Not yet listed.** It is not in `lv-patched-inventory.md`.
3. **`cp10-test-done` and `run-s1-lbdone` both load with a parked camera** (`CameraProcess`, and the Avatar stalls once he leaves the fast area). Both saves predate the `f9a9aba` fix (cp10 is dated 2026-08-17). `cp10-test-done` also loads with **0x0F = 1**. `CameraProcess::moveToAvatar` recovers the camera. After the Thordis talk, 0x0F read 0 and the camera followed without help. This is old-save state, not this build [INFERENCE].
4. **Atli's position reads alternate** between about (19432..19592, 6752..6884) every read during her loiter, so standstill strikes never fire. Quick read-then-click strikes hit her within 3-4 tries.

## Harness anomalies

1. **A redisplayed menu looked like a hang, and I killed my first instance on that reading.** The world was static, the log was silent and CPU sat at about 100%, but that is normal for an open conversation menu. Under gdb the rerun showed the console answering and the GumpNotify pid changing, which is finding 2. The real freezes are in finding 1.
2. **`h.P()` matches gdb** when the game runs under gdb. Match the scummvm path instead.
3. **`drv.strike()` treats `event 18` as `event 1`** (its substring test), so it reports false hits. Use a regex on `event 1 @`.
4. **`chord()` raised "console would not open"** twice. Both times the engine was frozen (finding 1).

## Disk changes

- **Wrote** this report and the plates in `docs/playtest-2026-10-10-leftovers/`: T1-00…09 and the two aftermath sheets, T2-* (first world) and T2r-* (rerun), and T4-01…07.
- **Scratch** in `/tmp/claude-1000/vleft/`:
  - `game/`, `scummvm.ini`, `run.sh` and `rungdb.sh`;
  - `lv_run.log`, `lv_run.part1.log` and `gdb.out`;
  - `saves/` (`ultima8.001` is a copy of `run-s1-lbdone`);
  - `sp/` (frames), `py/`, `atli.dis`, `flags.py` and `savinfo.py`.
- **Stopped:** my ScummVM, my gdb and Xvfb `:94`.
- **Not touched:** source, builders, maps, the fork, `shared/`, `TODO.md`, `HANDOFF.md` and `~/lv-checkpoints` (read-only; nothing banked).

# Avatar mover: one decision per kernel tick, fork `8af4f74e` (2026-10-10)

**Build under test.** `main` `b1788b3`, plus the uncommitted `build_scummvm.sh` detection change.
- **Game copy.** `/tmp/claude-1000/vmover/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Every hash matches `shared/build/ARTIFACTS.sha256`: EUSECODE `af5789a6…`, FIXED `511902e8…` in both places, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…` and ANIM `77e9705d…`. The engine log reads `usecode/eusecode.flx: … 1523547 bytes`.
- **Binary under test.** `scummvm-lv/scummvm`, mtime 04:01:51, which is after fork `8af4f74e` (03:35:20) and `avatar_mover_process.o` (03:35:23).
  - The build tree's `avatar_mover_process.cpp` equals the fork HEAD's copy (`diff` printed nothing).
  - `gdb ptype AvatarMoverProcess` on the binary shows `_lastRunTick`.
- **Patch check.** `PATCH_EQUAL`. The command was `git diff 01bd8879 HEAD -- engines/ ':!…detection_tables.h' | diff -q - tools/scummvm-patches/0001-lost-vale-engine.patch`.
- **Control binary.** `/tmp/claude-1000/vmover/ctl/scummvm`, built only to compare against.
  - Made with `cp -a scummvm-lv`, then `git show 8af4f74e -- engines/ | patch -R -p1`, then `make`. The make rebuilt the 10 objects that include `avatar_mover_process.h`.
  - `ptype` shows no `_lastRunTick`. It is therefore the 11bb31bd engine exactly.
- **Harness.**
  - Xvfb `:98` (1280x800), with the window at (480,300).
  - My own `scummvm.ini` sets **`frameLimit=true`** and `usehighres=true`, with `SDL_AUDIODRIVER=dummy` and a private `saves/`.
  - The driver is the `veng` `drv.py`/`h.py`, re-pointed to this display.
  - **Every session ran under gdb** (`rungdb.sh`), so the kernel tick, the process list and breakpoint hit counts come straight from the engine:
    - `kernel.cpp:188` is the runaway guard's `warning(...)` line;
    - `avatar_mover_process.cpp:82` is the new early `return`;
    - `Process::fail` was logged with a backtrace.
- **Sessions.** Five launches, each on a fresh copy of `run-s1-lbdone.sav` (md5 `2b31b12e…`) in slot 1:
  1. fixed: M1, then M2 and M3;
  2. control: the M1 negative control and the wall-clock A/B;
  3. fixed: the per-tick speed A/B;
  4. fixed: attributing the early returns;
  5. control: the per-tick speed A/B.
- **Not run, on instruction:** `build_artifacts.sh`, `install_lv.sh` and `build_scummvm.sh`. The hash match above stands in for them.
- **Plates.** They are in `docs/playtest-2026-10-10-mover/`.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| M1 | The `run-s1-lbdone` repro (Up tap, Left held 5 s, mouse bursts, SPACE, Up+SPACE) gives 0 guard lines and 0 kills. The tick advances, the mover and the SchedulerProcess stay alive, the game stays responsive, and a debug teleport gets the Avatar out, after which he walks | **PASS**. 0 `stuck in process loop` lines and 0 hits on the guard line. The tick advanced after every step. pid 3 (the mover) and pid 5 (the scheduler) were present after every step. The backpack gump opened. After the teleport he walked. **The new early return fired 857 times, all while the Avatar was wedged.** **Negative control (unfixed binary), same save and same Up tap:** frozen 19 s, then 3 guard kills, then no mover and no scheduler, which is the research report reproduced |
| M2 | No regression in normal movement | **PASS**. The A/B against the unfixed binary is **equal in units per tick** for walking, running and keyboard. Jumps went 512/504/512 (the jumps report gave 512/504/512). The tunnel walls stopped the Avatar at x 16223 / 16160 / 16159 (the same). Ledge climbs reached z 40 and z 16, 2 of 2 each (the same). Combat toggled, and the attack anim ran 4 times by breakpoint count. Double-click use, a drag into the pack, a Mythran talk start and end, and a walked-in Map 8 → Map 10 gateway all worked. **The early return fired 0 times in any of this.** |
| M3 | A LoiterProcess NPC walks normally | **PASS**. Mythran (item 33, `LoiterProcess 1410`) walked on screen (24-frame sheet) and covered 300+ units between reads, with PathfinderProcess and ActorAnimProcess entries. He also resumed after the talk (`event 15`). The fix's code is not on any NPC path |
| L | Log hygiene | **PASS** for this change. On the fixed binary: 0 `stuck in process loop`, `Unhandled intrinsic`, Segmentation, Assertion, `Trying to access segment`, `popToContainer`, `stale gravity` and `FIXME`. There were two `Non-existent process PID (0) in implies` and some debug-only `Cycle in paint`. **Both also occur on the unfixed control**, so neither comes from this change (findings 3 and 4) |
| — | Patch equals fork diff | **PASS** (`PATCH_EQUAL`) |
| — | `tools/run_all_tests.sh` | **PASS**: `OVERALL: PASS — 44/44 test file(s)` (197.9 s) |

**State writes.**
- Teleports with cheats on, each followed by a verified `Cheats = false`.
- `debugflag_enable Object` (session 1 and session 2).
- `CameraProcess::moveToAvatar`: the save loads with a parked camera, as the leftovers report found (its finding 3).
- `Ultima8Engine::loadGame 1` twice, each over the same fresh checkpoint copy.
- `Ultima8Engine::closeItemGumps` once.
- No `setGlobal`, no item creation and no save.

**Input.**
- The Up and Left keys were `keydown`/`keyup`.
- Mouse walks were right-button bursts at a 110 px offset (walk) or 240 px (run).
- A jump was `keydown Up`, then `keydown space` 60 ms later, a hold, and both keys released.
- An attack was a double left-click in combat mode.

## M1: the run-s1-lbdone freeze, PASS

### Session 1, fixed binary: the brief's sequence end to end

**After the load.** The Avatar was at (2200,2300,8), frame 885 (`M1-00-load`). The tick was 877490. There were 11 processes, the same list as the research report: HOURGLAS and FREE UCProcesses, Camera, Loiter (Mythran), Delay, Music, Audio, Heal, EggHatcher, **U8AvatarMoverProcess pid 3** and **SchedulerProcess pid 5**.

After each step I took 3 screenshots 2 s apart, then a gdb read.
- **"live"** means 3 different frame hashes. The fireplace animates, so a frozen engine gives identical hashes, as the control below shows.
- **"Early returns"** is the cumulative hit count on `avatar_mover_process.cpp:82`, the new `return`.

| Step | Live | Tick | Mover / scheduler | Early returns | Stuck lines |
|---|---|---|---|---|---|
| Up tap 0.4 s (`M1-01`) | yes | 879548 | pid 3 / pid 5 | (breakpoint set after this step) | 0 |
| Left held 5 s (`M1-02`) | yes | 881200 | pid 3 / pid 5 | 152 | 0 |
| 8 mouse bursts, 1.0-2.0 s each, walk and run offsets, all directions (`M1-03`) | yes | 883074 | pid 3 / pid 5 | 385 | 0 |
| SPACE tap; SPACE held 1.5 s; Up+SPACE held 1.0 s ×2; SPACE held 0.8 s with the cursor on the Avatar (`M1-04`) | yes | 884440 | pid 3 / pid 5 | 393 | 0 |
| Down, Right, Up and Right, each held 1 s | yes | — | — | — | 0 |
| `i`: the backpack gump opened and closed (`M1-05`) | — | — | — | — | 0 |

- **`Process::fail`.** Over the whole session, every call came from `Kernel::killProcesses` (6111) or `killProcessesNotOfType` (12). Those are map unloads on teleports. **None came from `Kernel::runProcesses`.**
- **The guard line.** The breakpoint on `kernel.cpp:188`, set after the Up tap, was never hit, and the log has 0 guard lines. The Up tap itself is covered by its 0 log lines and by the mover still being pid 3 afterwards.
- **Where the Avatar ended up.** At the end of the sequence he was at **(2483,2504,48)**, on the upper floor. A jump had carried him out of the wedge (finding 1). `M1-06` shows the view after `moveToAvatar`.

### Session 1, run 2 (reload): positions after each step

| Step | Avatar after | Live | Stuck |
|---|---|---|---|
| Up tap | (2200,2300,8) | yes | 0 |
| Left 5 s | (2200,2300,8) | yes | 0 |
| mouse ×6 (1.0-2.0 s, walk and run offsets) | (2200,2300,8) every time | yes | 0 |
| SPACE tap | (2200,2300,8) | yes | 0 |
| SPACE held 1.5 s | (2200,2300,8) | yes | 0 |
| Up+SPACE #1 | **(2303,2300,8)** | yes | 0 |
| Up+SPACE #2 | **(2351,2300,48)**, the upper floor (`M1-07`) | yes | 0 |
| jumpUp | (2351,2300,48) | yes | 0 |
| mouse walk E 1.2 s, then S 1.2 s | (2367,2276,48), then **(2367,2508,48)**: +232 S (`M1-08`) | — | 0 |

### Session 1, run 3 (reload): the teleport out

1. An Up tap and Left held 2 s. The Avatar stayed wedged at (2200,2300,8) and the world stayed live.
2. `MainActor::teleport 8 2344 2486 0` put him at (2344,2486,0) (`M1-09`).
3. Walks:
   - The 0.6 s N burst only turned him, as in harness anomaly 2 of the jumps report.
   - A 1.0 s N burst moved him −104.
   - A 1.0 s E burst moved him +172/+68.
   - Later bursts were W −200, N (+72,−72), a run E of +136 and a run S of +136. `M1-10` was taken after the E burst.

**Two more wedges, beyond the brief** (session 1, the same binary):
- **Inside the 40-high stump on Map 10 (11007,3327,0)** (`M1-11`). The Up tap moved him **out** to (11215,3327,0). That is not a wedge (the lateral scan freed him), and there were 0 early returns.
- **Inside the Map 39 tunnel's east wall (16262,19800,48)** (`M1-12`; the camera is parked here and the Avatar is hidden).
  - An Up tap and Left held 3 s left him at the same spot, frame 501, with **+106 early returns** and 0 stuck lines.
  - A mouse walk W 1.5 s then took him into the tunnel at (16162,19692,48).
  - So the fix also holds on a second, independent wedge geometry.

### Negative control: session 2, the unfixed binary, the same save and the same Up tap

| t after the tap | Frame hash | Stuck lines |
|---|---|---|
| 0.0 … 19.1 s (7 samples) | **`be357610`, identical every time** | 0 |
| 22.3 s | changes | **3** |
| 25 … 44 s | a new hash every sample | 3 |

- **The kills.** gdb caught 3× `GUARD-FIRED` at `kernel.cpp:188`. Each was followed by `Process::fail` ← `Kernel::runProcesses:189`. The log lines are 8454-8456.
- **The process list afterwards** had 9 entries, with **no U8AvatarMoverProcess and no SchedulerProcess**, and `Ultima8Engine::_instance->_avatarMoverProcess = 0x0`. The tick went 877042 → 879194 (`M1-C1-control-after-up-tap`).
- **Conclusion.** This is the leftovers/research symptom exactly, on this save. A reload recreated pid 3 and pid 5.

### Where the early returns came from

- **Session 4 (fixed)** logged the tick, the Avatar's position and `_lastAnim` at every early return. All 6 hits fired **at (2200,2300,8)** during the idle after load. The animations were `lookRight`, `stand`, `lookLeft`, `stand`, `lookRight` and `stand`: the zero-length idle head-shakes the research report describes.
- **Session 4 controls.** After the teleport to valid floor, 40 s of idle added 0 hits, and four walk/run bursts with gdb sampling added 0.
- **Session 1.** Over the walking, running, keyboard, jump, tunnel-wall, climb, combat, attack, use, drag, talk and gateway tests, the count stayed at **857**. It rose only in the tunnel-wall wedge, to 963.
- **Reading.** In normal play the new check never takes its `return`, so `run()` executes exactly as before apart from storing the tick.

## M2: normal movement, PASS

### Speed per kernel tick (A/B)

**Method.** I sampled the kernel tick and the Avatar's `_x` from gdb three times during one held input. The process stops for each sample, but the button or key stays held and the tick does not advance while it is stopped. All runs used the J5 stretch, Map 39 heading W from (16334,19450,48). Each cell gives the speed over two windows, in units per tick.

| Input | Fixed (sessions 3 and 4) | Unfixed (session 5) |
|---|---|---|
| Mouse walk (110 px) | 6.07/6.29, 6.21/6.21, 6.48/6.07, 6.34/6.07, 6.27/6.07 | 6.07/6.48, 6.00/6.27, 6.34/6.07 |
| Mouse run (240 px) | 9.65/12.0, 10.12/12.22, 9.65/12.0, 9.65/12.0, 9.78/12.0 | 9.78/12.0, 9.65/12.0, 9.33/12.0 |
| Keyboard Up (after a 0.3 s facing burst) | 6.17/6.26, 6.17/6.36, 6.17/6.33 | 6.17/6.26, 6.00/6.33, 6.09/6.26 |

**Distance covered by the first sample**, the same delay after button-down:

| Input | Fixed | Unfixed |
|---|---|---|
| walk | x 16190 / 16190 / 16174 / 16182 / 16190 | 16190 / 16190 / 16182 |
| run | 16286 ×5 | 16286 / 16294 / 16294 |
| keyboard | 16030 / 16046 / 16046 | 16046 / 16030 / 16030 |

**Start-up from rest is the same as well.**

**Wall-clock figures.**
- **Session 1 (fixed):**
  - a 1.0 s mobility burst S went **+232**, the jumps report's figure, in 5 of 5 tunnel resets;
  - mouse walk for 1.5 s went −504/−496/−400;
  - a mouse run for 1.0 s went −584 ×3;
  - keyboard Up for 1.5 s went −600 ×3.
- **Session 2 (unfixed):**
  - walk went −304/−296/−304, and run went −384/−400/−384;
  - the gdb bracket showed only **68-70 ticks for a 2.0 s hold**, where the fixed session had 128.
- **Why the difference.** It is a tick-rate difference, not a speed difference: under `frameLimit` without frame skip, the engine runs slower than real time when frames are slow, and the machine's load average was about 9. Session 5, on the same unfixed binary, ran at full rate, and its per-tick figures above match. So wall-clock A/Bs on this machine are not evidence (harness anomaly 1).

### Jumps, climbs and walls (fixed; the jumps report used the 11bb31bd build, the same engine minus this fix)

| Test | This run | Jumps report |
|---|---|---|
| Open ground, from (16334,19450,48) facing W, Up+SPACE 0.35 s ×3 | −512, −504, −512, z 48 | 512, 504, 512 |
| The same on the **unfixed** control (session 2) | −512, −504, −512 | — |
| Tunnel wall: E flush x 16222, at y 19950 / 19710 | 16223 / 16223, z 48 | 16223 |
| W flush x 16160, at y 19950 / 19802 | 16160 / 16159 | 16160 / 16159 |
| Clear of the wall, E from x 16190 (y 19710) | 16222 | 16222 |
| Mobility S 1.0 s after each | +232 ×4, (+68,+172) ×1 | +232 |
| Stump 56, Map 10, from (11007,3391,0) facing N | **(11007,3335,40)** ×2 | the same ×2 |
| Rock 526, Map 10, from (14719,1983,0) facing N | **(14719,1919,16)** ×2 (`M2-03-rock526-climbed`) | the same ×2 |

### Combat, use, drag, conversation, map change

- **Combat.** `c` set Actor flags `800` (`M2-04-combat-on`), and a second `c` read `0`.
  - The first double-clicks in new directions turned the Avatar, which is stock `checkTurn` (`M2-05a-attack-turn-sheet`).
  - Four double-clicks in one direction hit the `doAnim(Animation::attack, mousedir)` line (`u8_avatar_mover_process.cpp:166`) **4 times** by breakpoint count (`M2-05-attack-swing-sheet`).
  - The early-return count did not change.
- **Double-click use.** A double-click on the Avatar logged `Item: 1 (shape 1) calling usecode event 1 @ 0401:0080` and opened the paperdoll (`M2-07-use-avatar-paperdoll`).
  - A double-click on bowl 13103 (BATHSTUF) logged only its look line. BATHSTUF has no use event (`M2-07a`). That is the item, not the mover.
- **Drag.** Jug 12470 dragged onto the Avatar logged `Dragging item 12470` / `Dropping object 12470` / `Dropped item in backpack`. Weight went 20 → 30, and the jug went into the pack at (255,255) (`M2-08-drag-jug-to-pack`).
  - An earlier drop aimed at a wall-top pixel bounced back to its origin (`M2-08a`). That was my aim.
- **Conversation.**
  1. A double-click on Mythran logged `Item: 33 (shape 190) calling usecode event 1 @ 0421:A125` and "Ah. So the message has arrived at last…" (`M2-09-talk-start`).
  2. The menu showed Tell me of this ancient race. / Lord British says they can help me. / Let us speak of other matters. / Farewell. (`M2-10`).
  3. **Farewell.** gave "Go carefully, my friend…" (`M2-11-farewell`), then `Item: 33 … event 15 @ 0421:01A7`.
  4. The camera was back on the Avatar (`M2-12-after-talk`), and a 1.0 s walk moved him +104.
- **Teleporter egg (walked in).**
  1. `teleport 8 20500 3560 0`, outside trigger 212's box (`M2-13-before-gateway`).
  2. One 1.0 s north walk gave `Unloading map 8` / `Loading Fixed items in map 10`, with the Avatar at **Map 10 (13824,2456,0)**. That matches `playtest-2026-07-31-retest-hardened-gates.md` D8 (`M2-14-after-gateway-map10`).
  3. Walks there went +104 S and +208 E.
  - A first attempt with a **2.0 s** hold went Map 8 → 10 → 8 (finding 2).

## M3: NPC movement, PASS

Mythran (item 33) has `LoiterProcess 1410` in every process list.
- **Position reads.** With the Avatar idle upstairs, six reads over 60 s gave (1888,2232), (1908,2232), (1996,2340), (2131,2093), (2446,1994) and (2328,2228), all at z 48.
- **Processes.** The lists in session 1 show a `PathfinderProcess` and an `ActorAnimProcess` for item 33.
- **On screen.** A 24-frame capture at about 0.25 s shows him walking across the room in a normal step cycle (`M3-01-mythran-loiter-sheet`).
- **After the talk.** He resumed with `event 15`, as in the leftovers report's T4.
- **Structure.** `AvatarMoverProcess::run()` is the only function the fork commit changes, and NPCs have no AvatarMoverProcess. In the unfixed control the scheduler died with the mover. In the fixed run it survived every input (pid 5 in every process list).

## L: log hygiene

The counts come from `vmover/lv_run.log` (10,400 lines), split by launch:

| Launch | Binary | stuck | PID (0) in implies | Cycle in paint (debug flag) | Other patterns |
|---|---|---|---|---|---|
| 1 (gdb) 04:09 | fixed | **0** | 0 | 3124 | 0 |
| 2 (gdb) 04:58 | **unfixed** | **3** (the control) | 0 | 1299 | 0 |
| 3 (gdb) 05:16 | fixed | 0 | 2 | 0 | 0 |
| 4 (gdb) 05:26 | fixed | 0 | 0 | 0 | 0 |
| 5 (gdb) 05:31 | **unfixed** | 0 | 1 | 0 | 0 |

"Other patterns" means `Unhandled intrinsic`, Segmentation, Assertion, `Trying to access segment`, `popToContainer`, `stale gravity`, `FIXME` and `ANIMLOCK`.

Two short launches at 04:08 show 0 of everything. The first ran with no display (my Xvfb had not started) and was killed. The second was a plain launch, stopped to move under gdb.

**Other warnings:** `Invalid item 16164/5450/5098 passed to area search` (shape 804, event 5), each 1-2 times. These are stock, from both binaries' sessions.

## Estate

`tools/run_all_tests.sh` printed **`OVERALL: PASS — 44/44 test file(s)`** in 197.9 s. Among them:
- `test_uc_dialogue.py`: 301 passed, including the D19a-c checks for the `wt/atli-bang` merge;
- `test_roundtrip.py`: 516 of 516;
- `test_scummvm_patch_sync.py`: 3 passed.

I did not run `build_artifacts.sh`, on instruction. The game copy's hash match against `ARTIFACTS.sha256` stands in for it.

## Findings outside the brief

1. **From the LB-room wedge, two Up+SPACE jumps carry the Avatar up through the ceiling onto the floor above.**
   - **The sequence:**
     1. (2200,2300,8) → (2303,2300,8);
     2. → **(2351,2300,48)**, on the upper storey, which he then walks normally (run 2, `M1-07`, `M1-08`);
     3. run 1 ended at (2483,2504,48) the same way.
   - **Reading** [INFERENCE]. The jump sweep ignores the ceiling slab the Avatar's body already overlaps (his box z[8,48) against the slab's z[40,48)). So the rise is not cut, and the landing scan finds the slab top.
   - **Why it is new.** Before this fix, the same input never got that far (the first Up froze the mover). So this is a new *reachable* outcome, but only from an embedded start, which walking cannot create (research report §5).
   - **Here it is benign:** the upstairs is Mythran's floor. In general, a wedged Avatar can jump through whatever he is embedded in.
   - **Worth knowing for the unwedge design** listed as an option in the research report. A jump is already a de-facto unwedge, and it is not a controlled one.
2. **The Map 8 → Map 10 gateway bounces back if the walk is held for 2 s.**
   - **What happened.** `teleport 8 20500 3560 0`, then a 2.0 s north hold, gave `Loading Fixed items in map 10` and then, at once, `Unloading map 10` / `Loading Fixed items in map 8`. The Avatar ended at Map 8 (20260,3260,0), the 213 arrival pad. A 1.0 s hold stays on Map 10 (13824,2456).
   - **Reading** [INFERENCE from the build_map_10 pair at lines 475/481, not measured]. The continuing walk carries him from Map 10's arrival point into its return trigger.
   - **Same on the unfixed build?** Not tested on the control. The mover change cannot affect egg boxes, but a player who holds the mouse across the transition gets the ping-pong.
   - **Worth a check with `exact_reach.py`:** the distance from Map 10's 212 arrival point to the 213 trigger box along the arrival heading.
3. **`Non-existent process PID (0) in implies` appears during debug teleports on Map 39**, 2× on the fixed binary and 1× on the **unfixed** control.
   - **When.** It follows `LV: I_resetRef item=105/106/107/108 …` lines inside a `Cheats = true` … `Cheats = false` teleport window.
   - **Cause.** This is not the mover. It is some usecode spawn whose pid is 0 while the Map 10 villagers' refs are reset. Earlier reports counted this pattern at 0 "across farewells", so this teleport-time occurrence is not covered by them. I did not trace the class.
4. **`Cycle in paint dependency graph 590 -> 235` repeats about 500 times a visit on Map 8 near (20260..20500, 3260..3560)**, the bone cave at the Lost-Vale gateway. It appears with the same pair of sort indices on the **unfixed** control (495 in one visit). It is a `debugC(kDebugObject)` line, so it shows only with `debugflag_enable Object`. Not a regression; noted for the next verifier who greps for it.
5. **`run-s1-lbdone.sav` still needs re-banking.** The research report recommended it. Every load wastes idle time on zero-length head-shakes, which are harmless now, and on the old build any movement killed the scheduler.

## Harness anomalies

1. **Wall-clock movement A/Bs are unreliable on this machine.** One unfixed session ran about 33 ticks/s while walking, against about 62 ticks/s in the others, all at load average ~9 with `frameLimit=true`. Bracket bursts with gdb tick reads, or sample the tick and the Avatar's `_x` from gdb, before comparing builds.
2. **gdb's `run <redirection>` replaces `--args`.** The first gdb launch came up in the ScummVM launcher. Use `set args <all args> >>log 2>&1` or `run <all args> >>log`. Also, gdb reads stdin only while the inferior is stopped, so a `kill` typed while the game ran waited for the next SIGINT (the research report's harness note).
3. **`ps … | split()[1]` picked gdb's pid instead of the inferior's** on the control launch. Filter out the gdb line.
4. **`chord()` raised "console would not open" twice.** Once was right after the Map 10 arrival and once after a keyboard hold. Both times a retry worked, and the game was live. These were transient, not freezes.
5. **`getMainActor()` is not callable from gdb on this build.** It is inlined. Use `((Item*)ObjectManager::_objectManager->_objects._storage[1])->_x`.

## Disk changes

- **Wrote** this report and the plates in `docs/playtest-2026-10-10-mover/`: `M1-00`…`M1-12` (13), `M1-C1` (control), `M2-*` (16) and `M3-01`.
- **Scratch** in `/tmp/claude-1000/vmover/`:
  - `game/`, `scummvm.ini`, `run.sh`, `rungdb.sh`, `gdbinit` and `procs.py`;
  - `lv_run.log` and `gdb.out` (every trace and counter above), plus `ctl1.gdb`;
  - `saves/` (`ultima8.001` is a copy of `run-s1-lbdone`);
  - `sp/`, `py/` and `fix.diff`;
  - **`ctl/`, a 1.1 GB copy of `scummvm-lv` with the fix reversed and rebuilt**: the control binary. Delete it when done.
- **Stopped:** all five of my gdb/ScummVM instances and Xvfb `:98`.
- **Not touched:** source, builders, maps, `scummvm-lv/`, `scummvm-lv-console/`, `shared/`, `TODO.md`, `HANDOFF.md` and `~/lv-checkpoints` (read only; nothing banked).

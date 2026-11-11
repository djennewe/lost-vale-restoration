# Ezrekal's east door: the standing-start "run stop" is a jump the harness asked for (2026-10-11)

**Question.** In `docs/playtest-2026-10-11-fix8.md` (D1b, finding 1), a mouse run W into Ezrekal's east door on Map 10 stops outside at (14048-14064, 12678-12763). It happens only from a standing start with the Avatar already facing W, from (14300,12610) or from x 14407 at y 12600-12671, and it failed 8 of 8. The camera snaps +92 E/+92 S in 0.16 s. `avatar_mover.py` does not reproduce it, and the worn-earth track's east edge (425, x 14207) was the suspect.

**Answer.** It is not a run and not a map defect. Every failing trial was a **targeted jump**, which the trial driver triggered by accident.
- `vf8/py/vf.py` `run()` "primes" each hold with a left click 0.25 s before it presses the right button. U8 reads both buttons pressed within the double-click timeout (400 ms) as **jump**.
- If the Avatar already faces the mouse direction, the mover jumps at once. Otherwise `checkTurn` turns him first and the jump request is dropped. That is the whole facing dependence.
- With `targetedjump` on, the jump aims at whatever land item is under the pointer. From (14300,12610), the pointer 340 px W lies on top of the **south palisade segment 857** (item 32473 at (13983,12799,0)).
- The jump arcs SW toward the palisade and meets its corner in mid-air at z 20. It stops there, falls 23 units, plays `land` and `stand`, and the 2.5 s hold runs out about then.

The track is not involved: an unprimed run from the same start crosses x 14207 with every `tryAnim` returning SUCCESS.

**Proposed fix: no map tweak and no model change.** Drop the left-click prime from the trial driver (or press the right button more than 400 ms after it), then re-judge fix8 D1b. Details are under *Proposed fix*.

## Verdicts

| ID | Claim tested | Verdict | Evidence |
|---|---|---|---|
| G1 | The stop reproduces under gdb, launched directly | **PASS** | Traced trial E1: (14300,12610) facing W, primed hold 2.5 s → (14064,12702,0). The untraced A, R0, R1 and R2 trials → **(14048,12678,0)** each time, vf8's exact end |
| G2 | Animation chosen | **Identified** | A **jump**, not walk→run. `MOVER L436 both buttons within dbl-click timeout -> MOVE_JUMP` (`|m1.down - m0.down|=367 ms, timeout=400 ms`), then L512 *facing already == mousedir* → climb72..climb16 `tryAnim`s, all END_OFF_LAND, then `jump()` → `TargetedAnimProcess(jumpUp)` |
| G3 | Each step's target and result | **Traced** | jumpUp frames 5-13 move (-26,+10) each, z 0→30→23; frame 14's target (14037,12713,20) is `valid=False`, `blocker=#32473:s857f0@(13983,12799,0)` → `_blocked` → `ActorAnimProcess` terminates |
| G4 | What makes the +92/+92 snap | **Identified: the fall** | `stand` at z 23 is unsupported → `Item::hurl(0,0,0,2)` (the GravityProcess) drops z 23→0 in 12 ticks (0.2 s). A 23-unit drop moves the sprite 23 px down. `camtrack.py` assumes z is constant, so it reads 23 px down as world (+92,+92). It is not a scanForValidPosition shift, a stumble, or a hurl sideways |
| G5 | Items involved | **Identified** | Jump target and mid-air blocker: palisade **857, item 32473 at (13983,12799,0)**, pointer point (13956,12746,40). Landing support: floor 242 item 14760 at (14079,12671,0). The 425 track tile 17481 at (14207,12671) is only `land` under the arc, and never a blocker |
| G6 | The 425 track's east edge stops a run | **Refuted** | E2, unprimed and traced: `walk` (14300→14204) SUCCESS, `run` (14204→14012) SUCCESS, `run` (14012→13820) SUCCESS. The run crosses x 14207 and the doorway with no adjustment at all |
| G7 | Why `avatar_mover` misses it | **Explained** | It models walk/run holds only. Its docstring says "WHAT IT DOES NOT MODEL: jumping" (`avatar_mover.py:103`), so `map10_wedges` correctly finds every walk/run start clear |
| C1 | Control: same start and facing, no prime | **PASS 5 of 5** | B, R0, R1, R2 → (12764/12748, 12610), inside; traced E2 → (13532,12610) |
| C2 | Control: vf8's other failing starts, no prime | **PASS 3 of 3** | (14407,12671) → (12855,12671); (14300,12671) → (12748,12671); (14300,12660) → (12748,12660) |
| C3 | Control: prime, facing S | **PASS** (jump dropped) | E5: L436 sets MOVE_JUMP, L512 never fires; `lookRight`×2 + `stand` turn him; then walk→run → (13516,12610) |
| C4 | Control: prime, start x 14191 | **PASS**, but it was also a jump | E4: the same pointer offset now lies on floor 242 item 22162 inside, `jump()` target (13687,12576,0), so the Avatar lands inside. This is why "starts on the track" passed |
| C5 | A jumped Avatar still gets in if the hold continues | **PASS** | E3b: primed (gap 0.1 s), hold 7 s. He lands at (14064,12702). Walk W, NW and SW are blocked, then a `step` NW → (14048,12678), a walk NW → (13988,12618), runs W → (13508,12618), inside |

Totals for (14300,12610) facing W, 2.5 s holds: **every primed hold whose jump fired ended outside, 5 of 5** (E1, A, R0, R1, R2). In E3 the prime landed too late, no jump fired, and he ran in. E3b's 7 s hold jumped, landed outside, then entered. **Unprimed: 5 of 5 pass.** vf8's 8 of 8 stops are the primed case.

## Setup

- **Build.** main `ac56acd`. The game copy `/tmp/claude-1000/vdoor/game` is vf8's tree with all six artifact files replaced from `shared/build/`. Each matches `ARTIFACTS.sha256`: FIXED `09bde917…` (root and `STATIC/`), EUSECODE `b484c2fa…`, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`. The binary is `scummvm-lv/scummvm` (built 2026-10-11 02:05, not stripped, `-g` and no `-O`), whose sources all predate it.
- **Harness.** Xvfb `:93` (started by me). vf8's ini: 320×200, no width/height keys, `frameLimit=true`, `SDL_AUDIODRIVER=dummy`. Saves go in `vdoor/saves`. The driver `vdoor/py/vd.py` is vf8's `vf.py` with the paths changed and ScummVM launched as `gdb -batch -ex 'source trace.gdb.py' -ex run --args scummvm-lv/scummvm …`. ptrace_scope 1 allows a direct launch.
- **Fresh map.** The first session loaded `run1010-s04b-m11-three-talismans` (Map 11) and teleported to Map 10, so the log shows `Loading Fixed items in map 10` from the shipped FIXED.DAT. I saved there (`sp/m10-fresh.sav`), and later gdb sessions loaded that save, which was made on this build.
- **The tracer.** `vdoor/py/trace.gdb.py` holds 36 Python breakpoints. Every `stop()` logs and returns False, so the game never halts. The heavy ones are disabled. A breakpoint on `Debugger::cmdObjectInfo` turns them on while `vdoor/TRACE_ON` exists, so each trial's `objectInfo 1` read brackets the trace. Breakpoints:
  - `U8AvatarMoverProcess::step`, mover lines 434/436/443/465/507/512/556, `jump()` lines 761/770;
  - `Actor::tryAnim` (603, 616, and returns 604/618/628/639/641);
  - `AnimationTracker::step` (186 entry, 312 sweep block, 323 `getPositionInfo` with land/blocker, 364 scan result, 377 invalid block, 394 commit, 411 unsupported);
  - `ActorAnimProcess::run` (292, 220 hurl, 223 done, 247 fall, 251 blocked);
  - `Item::collideMove`, `Item::move`, `Item::hurl`, `Item::fall`, `GravityProcess::run`, `Actor::doAnim`.

  All are filtered to object 1. The trial recipe is vf8's: teleport to (14300,12900), walk 0.6 s to set the facing, teleport to the start, then hold the right button 2.5 s with the pointer 340 px W.

## The mechanism, frame by frame (trial E1, `sp/E1.trace.txt`)

```
--- trace ON  avatar (14300,12610,0) dir=12 lastAnim=lookRight
t640990 MOVER L434 both-buttons check: |m1.down - m0.down|=367 ms, timeout=400 ms, m0.state=0 m1.state=1
t640990 MOVER L436 both buttons within dbl-click timeout -> MOVE_JUMP  mouselength=2 mousedir=12 facing=12
t640990 MOVER L512 JUMP: facing already == mousedir, no turn -> jumping
t640990 TRY  climb72 … climb16 dir=12 -> END_OFF_LAND (all eight)
t640990 MOVER jump() targeted: mouse=(-120,-46) TraceCoordinates -> obj 32473 at (13956,12746,40)
t640990 MOVER jump() -> TargetedAnimProcess(jumpUp) xrange=312 yrange=148 maxrange=480 target=#32473:s857f0@(13983,12799,0)
t641010 ANIM STEP target=(14274,12620,9)  d=(-26,10,9)  valid=True sup=False land=#22678:s242
 …                     (14248,12630,10) (14222,12640,19) (14196,12650,20) (14170,12660,25)
t641030 ANIM STEP target=(14144,12670,30) d=(-26,10,5)  valid=True sup=False land=#17481:s425f6@(14207,12671,0)
t641042 ANIM STEP target=(14064,12702,23) d=(-27,11,-2) valid=True sup=False land=#14760:s242f2@(14079,12671,0)
t641046 ANIM STEP target=(14037,12713,20) d=(-27,11,-3) valid=False blocker=#32473:s857f0@(13983,12799,0)
t641046 ANIM STEP BLOCKED (invalid, not onground/zd)      ; animation_tracker.cpp:377
t641046 ANIM terminate: BLOCKED                              ; actor_anim_process.cpp:251
t641046 DOANIM stand dir=12 at=(14064,12702,23)
t641046 ANIM STEP UNSUPPORTED at (14064,12702,23) land=#14760:s242f2
t641050 GRAV hurl xs=0 ys=0 zs=0 grav=2
t641050…641060 collideMove z 23 -> 21 -> 17 -> 11 -> 3 -> 0   (force=False)
t641062 DOANIM land dir=16 at=(14064,12702,0)
t641106 DOANIM stand dir=12 at=(14064,12702,0)
```

1. **The jump request.** `vf.run()` left-clicks, sleeps 0.25 s, then presses the right button. xdotool latency made the gap 367 ms in E1, and 206-249 ms with a 0.1 s sleep. Both buttons are unhandled, so `u8_avatar_mover_process.cpp:423-439` sets MOVE_JUMP. MOVE_MOUSE_DIRECTION is not set yet (the right button is not HANDLED), so the request takes the branch at line 506.
2. **Facing decides it.** Line 509 `if (checkTurn(mousedir, false)) return;`. Facing S, the mover turns and returns, and MOVE_JUMP was already cleared at 507, so the hold becomes an ordinary walk→run (C3). Facing W, there is nothing to turn, so the mover goes on to the climb probe (no climb fits) and then `jump(Animation::jump, W)`.
3. **The target.** `jump()` (line 749) is targeted: `TraceCoordinates` under the pointer returns the palisade 857's top, (13956,12746,40). It is `is_land()` and within 480 range, so a `TargetedAnimProcess(jumpUp)` runs. `setTargetedMode` spreads (target − animation's own travel) over the off-ground frames, which is the (-26,+10)/frame SW drift. Its z part is capped at 16 (the palisade top is at 40).
4. **The block.** On frame 14 the Avatar's box (13973..14037, 12649..12713, 20..60) meets the palisade's NE corner (east face x 13983, south jamb y 12671). The tracker is in mid-air, so it is `_blocked` with no `scanForValidPosition` (that runs only for on-ground frames).
5. **The drop and the "snap".** The follow-up `stand` is unsupported at z 23, so `Item::hurl` starts the GravityProcess, which drops him to z 0 in 0.2 s at the same x,y. On screen that is 23 px straight down. `camtrack.py` converts a screen shift to world with z held constant. For a pure screen-down shift it computes x+y = 8·23 = 184, or +92/+92. The whole fix8 film track follows the same way from this arc:
   - The apex (14144,12670,30) reads as (14024,12550). vf8 reported "(14282,12604) → (14018,12556)".
   - The blocked point (14064,12702,23) reads as **(13972,12610)**. vf8 reported "slides S to (13972,12610)".
   - The fall reads as "+92 E, +92 S" to (14064,12702).

   So the Avatar never reached the doorway. The film showed a jump arc read as a flat track.
6. **Why he "stays" there.** The jump, fall and land take 130 ticks (2.2 s at 60 ticks/s) after the request. A 2.5 s hold ends while he lands, often after one adjusted `step` NW to **(14048,12678)**, which is vf8's recorded end. Held longer, he works round the corner and enters (C5). Build 7's stops at "(14070,12686..12706)" with the "stumble pose" film look like the same jump [INFERENCE: vf7's `vf.py` also defaults `PRIME = True`, line 193; I did not re-run build 7].

Plates (`docs/research/2026-10-11-ezrekal-door-run-stop/`):
- `A1-faceW-14300-12610-pointer-on-palisade-857-top.png`: the start, with the pointer (blue arrow) on the south palisade's top.
- `A2-primed-hold-is-a-targeted-jump-sheet.png`: film frames 6-51 (0.24-2.04 s). The jump pose begins at 0.6 s, he drops beside the palisade corner, and he lands at 1.56 s.
- `A3-primed-ends-14048-12678-outside.png`: the end, outside.
- `B1-unprimed-ends-12764-12610-inside.png`: the same start and facing, no left click, inside.
- `C1-14191-12600-pointer-on-floor-inside.png`: from x 14191 the same pointer offset falls on floor inside the stockade, so that jump lands inside.

## Why `avatar_mover` misses it

There is nothing to miss in its domain. Its holds are walk/run steps, and the engine agrees with it: from every start vf8 reported failing, the unprimed run passes (C1, C2). The run's own `tryAnim`s across x 14207 all return SUCCESS (G6). The stop needs a **jump**, which the model excludes by design (`avatar_mover.py:103`). It also needs a pointer whose screen offset happens to fall on the palisade top. Neither is map geometry `test_route_reach.map10_wedges` should be asked to judge.

## Proposed fix (nothing applied)

1. **Harness, required.** In the private trial driver (`/tmp/claude-1000/vf8/py/vf.py`, inherited from vf7), `run()` sends `click 1` 0.25 s before `mousedown 3` whenever `PRIME` is true, which is the default. Either drop it, or make the gap ≥ 0.5 s (above the 400 ms `getDoubleClickTime()` this build reported), or prime with something that does not touch mouse button 0. The repo's own drivers (`session.sh walk`, `nav.walk`) do not prime, so the repo has nothing to fix. The prime was there to beat "the first input after a console close is swallowed". In the 8 unprimed holds this session (C1's 5, including the traced E2, and C2's 3) the first input was never swallowed.
2. **Re-judge fix8 D1b.** Its 12 "stops" are primed jumps. On this evidence, mouse runs W into the door from a standing start pass: 8 of 8 unprimed holds across y 12610-12671 and x 14300/14407 (C1 + C2).
3. **Map: no tweak.** The palisade, doorway and 425 track behave correctly for walk and run. A *deliberate* jump at the palisade top that ends against its corner is stock U8 behaviour, and a held direction still carries the Avatar in (C5).
4. **Model: no change needed.** If a guard against this class of false alarm is wanted, it belongs in the playtest docs, not `test_route_reach`. Suggested `traps.md` line: *"A left click less than 400 ms before a right-button hold is a JUMP, aimed at the land item under the pointer. If the Avatar already faces the pointer it fires at once; otherwise the turn swallows it. Never prime a walk/run with a left click."*

## Harness anomalies

- vf8's `vf.run(..., PRIME=True)` is itself the defect found here (above).
- One eval cell timed out in mid-hold, at the 30 s default, and left the right button down. I released it with `xdotool mouseup 3` before the next trial. Trial T0, the first, is therefore a 30 s+ hold and is not counted.
- On the first launch under gdb, ScummVM re-created its window at (320,200), so the driver's `windowmove` had gone to a dead window id. I moved it again before any input.
- In trial E3 the 0.25 s prime landed after the left click had already been marked handled. No jump happened, and it ran through to (11852,12482). The jump needs both presses inside the same mover poll window, so the prime is not fully deterministic. vf8 still saw 8 of 8.

## Disk changes

- **Wrote** this report and `docs/research/2026-10-11-ezrekal-door-run-stop/` (5 plates).
- **Scratch** `/tmp/claude-1000/vdoor/`:
  - `game/` (vf8's tree with this build's artifacts) and `scummvm.ini`;
  - `saves/`, where slot 1 is overwritten by `m10-fresh`;
  - `lv_run.log`, `gdbtrace.txt` (the full tracer output) and `trace.txt`;
  - `py/` (`vd.py`, `trace.gdb.py`, plus copies of `camtrack.py` and `d1model.py`);
  - `sp/` (per-trial traces `T1`, `E1`, `E2`, `E3`, `E3b-jump-then-hold7`, `E4…`, `E5…`, films `A-…mkv`, `B-…mkv`, `C-…mkv`, stills and frames).
- **Stopped** my ScummVM, its gdb and Xvfb `:93` (pid 4042633, which I started). I did not touch any other process.
- No source, map, fork, `TODO.md` or `HANDOFF.md` edits. No install or build runs. Nothing banked in `~/lv-checkpoints`.

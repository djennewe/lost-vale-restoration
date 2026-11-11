# The `run-s1-lbdone` walk freeze (leftovers finding 1)

Investigated 2026-10-10 under gdb on a private Xvfb `:96`. The game copy, ini
and save directory were in `/tmp/claude-1000/vfreeze/`. The problem is
finding 1 of `docs/playtest-2026-10-10-leftovers.md`: loading
`~/lv-checkpoints/run-s1-lbdone.sav` and then moving the Avatar freezes the
world for about 30 s, then logs `Seem to be stuck in process loop` and leaves
the game with no U8AvatarMoverProcess and no SchedulerProcess.

## Verdicts

| Question | Answer |
|---|---|
| What loops | An **engine** loop. U8AvatarMoverProcess and the Avatar's own ActorAnimProcess alternate inside one `Kernel::runProcesses` pass. No usecode is involved: the LB egg's class (EGGLBSCE, 0x5AF) is not running during the loop. |
| Why | The save puts the Avatar at (2200,2300,8). That spot is **not a valid position** under either the saved or the current geometry. Every animation the mover starts is refused on its first frame, so the anim process ends in zero time. `Process::wakeUp` then schedules the mover again in the same pass. |
| `_zLost` / 11bb31bd / bbcfa209 | **Not involved.** A scratch build with both commits reverted reproduced the freeze identically, with the same three kills. The stand frame never reaches the code either commit changed. |
| Save-state artifact? | **Yes, as the trigger.** The Avatar's position comes from the 2026-09-06 run, which almost certainly reached the unreachable egg box by debug teleport [INFERENCE]. The loop it exposes is latent in unmodified upstream code. |
| Can a fresh-game player hit it? | **Not through this spot or the LB egg.** Walking into the egg box from valid floor hatches the egg, and nothing freezes. **Yes, in principle, through any other wedge.** The pre-bbcfa209 Map 39 jump wedge produced the same 3× guard on 2026-10-09. Any teleport or scripted move that lands the Avatar inside geometry would too. |
| Fix | Let the mover make at most one decision per kernel tick (diff below). I built and tested it in a scratch copy: no freeze and no kills on Up, a held Left, mixed keyboard and mouse input, and jump; normal walking is unchanged. **Not applied** to the fork. |

## 1. Reproduction and backtraces

The binary was `scummvm-lv/scummvm`, built 2026-10-10 01:08 and carrying the
whole fork patch, `11bb31bd` included. The artifacts in the game copy match
`shared/build/` by sha256. The save went into slot 1, gdb launched the game as
a child process, and I sent one 0.4 s Up tap.

- **Before input:** the world was live and idle, and the log was silent.
- **After the tap:** the screen was frozen (identical md5 at +4 s and +5.5 s), and CPU sat at ~100% on thread 1.
- **Reproduced 3 of 3** on this binary (runs 1, 2 and 6 below), and again on the bisect binary (run 3).

**Thread 1, run 1** (every other thread was parked in futex/nanosleep;
`thread apply all bt` is in the scratch `gdb.out`):

```
#0  Item::getLocation (this=0x55555adc4030)                       item.h:104
#1  CurrentMap::scanForValidPosition (x=2200, y=2300, z=8, item=<Avatar>,
        movedir=dir_west, wantsupport=true, ...)                  current_map.cpp:855
#2  AnimationTracker::step                                        animation_tracker.cpp:361
#3  Actor::tryAnim (anim=step, dir=dir_west)                      actor.cpp:612
#4  U8AvatarMoverProcess::step (action=step, dir_west, adjusted=true)   u8_avatar_mover_process.cpp:662
#5  U8AvatarMoverProcess::step (action=walk, dir_west, adjusted=false)  u8_avatar_mover_process.cpp:683
#6  U8AvatarMoverProcess::handleNormalMode                        u8_avatar_mover_process.cpp:585
#7  AvatarMoverProcess::run                                       avatar_mover_process.cpp:101
#8  Kernel::runProcesses   (num_run = 44798)                      kernel.cpp:166
#9  Ultima8Engine::runGame                                         ultima8.cpp:639
```

**Samples from run 2.** I restarted, sent the same tap, and interrupted twice.
In both samples the Avatar was at (2200,2300,8) and the tick stood at 877652;
the pass never ended.

| Sample | Time after tap | Thread 1 was in | `num_run` |
|---|---|---|---|
| A | +3 s | `scanForValidPosition(2176,2324,8, dir_southwest)` ← `tryAnim(walk, dir_southwest)` ← `step(walk, dir_west)` (altdir1) | 10622 |
| B | +9 s | `getPositionInfo` ← `tryAnim(step, dir_northwest)` ← `step(step, dir_west, adjusted)` | 27444 |

That is about 2,700 runs/s under gdb, so the guard's 65,535 comes at about
24 s, which matches the reported ~30 s.

**The process list during the loop** has 11 entries:

- **Usecode:** a UCProcess of class HOURGLAS (0xE3), and a UCProcess of class FREE (0x581, ip 0x1C3D).
- **Mythran (item 33):** a Loiter process.
- **Engine:** CameraProcess, DelayProcess, U8MusicProcess, AudioProcess, HealProcess, EggHatcherProcess, U8AvatarMoverProcess (pid 3) and SchedulerProcess (pid 5).
- **Absent:** no EGGLBSCE process. The anim processes don't show up in a snapshot because each one is created and erased within the cycle.

**The cycle**, traced with breakpoints on the mover's `waitFor(doAnim)`
(u8_avatar_mover_process.cpp:730), `ActorAnimProcess::terminate` and
`Process::wakeUp`. It repeated 155 times in a few seconds:

```
MOVER doAnim action=2(stand) stepdir=12(west) res=0(FAILURE)
AAP terminate pid=22xx action=2 dir=12 firstFrame=0 step=1   <- actor_anim_process.cpp:251 (blocked)
wakeUp pid=3                                                <- the mover, made next in the pass
```

**Runaway-guard kills.** The same three kills, in the same order, happened in
runs 2 and 3, and in run 6 through the turn path below:

| Order | Process | pid |
|---|---|---|
| 1 | U8AvatarMoverProcess | 3 |
| 2 | SchedulerProcess | 5 |
| 3 | UCProcess, class FREE (1409), ip 0x1C3D | varies |

The third is inside the function at 0x1C19, a `suspend` loop that polls the
call at 0x1BF1 until a timer expires. That is FREE::wait (lv-patched
`FREE.UNK:150`) [INFERENCE from the disassembly shape].

Three log lines match (lv.log lines 83-85). After the trip, the post-guard list
has neither pid 3 nor pid 5, and `Ultima8Engine::_avatarMoverProcess` is
null. That matches the leftovers report.

## 2. The looping code path

Every link below is unmodified upstream code; the fork's diff against
`01bd8879` does not touch these lines.

1. `Kernel::runProcesses` runs the mover. Up sets `MOVE_FORWARD`, so `handleNormalMode` calls `step(walk, dir)` (u8_avatar_mover_process.cpp:585).
2. `step()` tries the direction, then both neighbours, then recurses with `step`. All return FAILURE, so `action = stand` (:711-713). It then calls `waitFor(avatar->doAnim(stand, dir))` (:730), which suspends the mover.
3. The new ActorAnimProcess is appended to the list and runs later in the same pass. `init()` succeeds and sets `_lastAnim = stand`. Its first `stepFrom` fails:
   - `getPositionInfo` reports the stand frame's target (the current spot) as invalid. The frame is on-ground, so `scanForValidPosition` runs (animation_tracker.cpp:354-366).
   - Every candidate z (0, ±4, ±8) and lateral shift is blocked. The tracker sets `_blocked` and the process calls `terminate()` (actor_anim_process.cpp:227-252) on the tick it started.
4. `Process::terminate` wakes its waiter. `Process::wakeUp` calls `Kernel::setNextProcess(this)` (process.cpp:62-67), which re-inserts the mover **directly after the current process**. The mover runs again in the same pass, and the cycle returns to step 1.
5. The pass never finishes, so the tick never advances, rendering stops and key-up events are never processed. At `num_run > 65534`, `kernel.cpp:186-190` calls `fail()` on whatever is current. The parity makes that the mover.
6. **`num_run` is never reset after a kill**, so every later process in the pass is failed too. Those are the SchedulerProcess and the FREE timer that sit after the mover in the list. This is where the "killed the scheduler" symptom comes from.

### A second path: a held turn key

I tested this against a scratch fix that only guarded the `step()` fallback.

- **Input:** a single 0.8 s Left hold.
- **Result:** it still tripped the guard (run 6), with the same three kills. The guard fired within ~4 s, faster than the step path, because each turn iteration is cheap.
- **Trace (run 7, doAnim breakpoint):** `checkTurn` → `AvatarMoverProcess::turnToDirection` → `Actor::turnTowardDir` (actor.cpp:709) issues a chain of zero-length turn anims (`lookLeft`/`stand` across all directions).
- **Why it never ends:** while the key is "held", `getTurnDirForTurnFlags` (u8_avatar_mover_process.cpp:567-569) rotates the target again on every wake. The key-up can never arrive, because the pass never ends.

So the root is general: **any** mover decision made for an embedded Avatar
completes in zero time. A fix in one branch is not enough; this was tested.

**Idle is harmless**, which is why idling after the load logs nothing. The idle
head-shake anims are also zero-length here, but the next idle decision issues
no new anim (`currentIdleTime != 0`, :621-652), so the cycle stops after one
round.

## 3. Why the Avatar is embedded

**Probes.** These are `CurrentMap::getPositionInfo` calls, made from gdb for
the Avatar's body (64×64×40, shape flags 0x22):

| Position | Geometry | valid | supported | Reported blocker |
|---|---|---|---|---|
| (2200,2300,8) | as loaded (fixed items from the save) | 0 | 0 | upper floor 164 at (2303,2303,40), box z[40,48) |
| (2200,2300,8) | after a Map 3 round trip (fixed items from today's `FIXED.DAT`) | 0 | 0 | cup 182 at (2228,2300,16) |
| (2200,2300,0) | after the round trip | 0 | 1 | cup 182 |

- **The table.** The body box x(2136,2200] y(2236,2300] z[8,48) also overlaps the solid table 263 at (2260,2340,0), whose shape info gives 128×128×16 and flags 0x0A. The engine reports only one blocker per probe.
- **The room.** The ground floor is z 0. The ceiling (164) starts at z 40, exactly the Avatar's height, so z 8 can never be valid under it.
- **The trigger.** The stand frame's `scanForValidPosition` can't find a free spot within ±8 z or a small lateral shift, and that triggers the loop.

**How it got there.** The checkpoint's provenance (f6444a6, and the archived
HANDOFF-log-through-2026-09-05 lines 44-47 and 53-54) records "Avatar stable
at (2200, 2300, 8)". It also records that the "map-8 LORDBRIT backstop egg is
not walk-reachable" and that the scene "fires correctly once you are in the
box". The Avatar's z equals the egg's z (8). Together that points to a debug
`MainActor::teleport 8 2200 2300 8` into the box [INFERENCE: the session that
made it left no teleport line in the docs I found]. "Stable" only meant idle:
idle issues no move, as shown above.

**Stale fixed items: a separate save-state effect, not the cause.**

- **What I saw:** as loaded, Map 8's fixed items come from the save, not from `FIXED.DAT`. gdb showed slab 301 at **(2200,2326,1)** with `EXT_FIXED`, while today's `FIXED.DAT` has it at (2200,2208,1) (`build_map_08.py`, moved 2026-10-07).
- **Why:** the current map's items, fixed ones included, are serialized with the objects.
- **Refresh:** a map change reloads them, which matches wave1 R4.
- **Not the cause:** the spot is invalid under both versions.

**Side note on wave1 R4** (`docs/playtest-2026-10-07-wave1.md:391`). R4
"stood outside the egg box at (2200, 2470, 8)", but that position is invalid
too. The probe reports blocker 222 at (2236,2444,0), and the floor there is
z 0. It was harmless only because nothing tried to move.

## 4. Bisect: 11bb31bd and bbcfa209 are not involved

The bisect binary came from a scratch copy of `scummvm-lv/`
(`/tmp/claude-1000/vfreeze/build`):

1. Reverse-apply `git -C scummvm-lv-console show 11bb31bd -- engines/`, then the same for `bbcfa209`, with `patch -R -p1`.
2. Rebuild with `make`.
3. Confirm the result: `animation_tracker.{cpp,h}` now diff empty against `01bd8879`, and gdb `ptype AnimationTracker` has no `_zLost`. `scummvm-lv/` and `scummvm-lv-console/` were not touched.

Run 3 on that binary gave the same freeze: the screen stayed static, and
thread 1 was in `scanForValidPosition` ← `tryAnim(walk, dir_northwest)` ←
`U8AvatarMoverProcess::step`, with `num_run = 19434`. The same three kills
followed (pid 3, pid 5, then the FREE (1409) process at ip 7229), with three
log lines.

**This matches the code.** Both commits change only:

- the large-step sweep (`|dx| >= xd-8`, …), which a 0-delta stand frame never enters;
- `_zLost` bookkeeping on blocked rising steps, which affects z only and never `_blocked`.

The stand-frame path at animation_tracker.cpp:354-366 is upstream's.

## 5. Can a player on a fresh game hit it?

**Not via the LB egg or this spot.**

I ran this on the shipping binary after a Map 3 round trip, so the fixed items
were current (run 4b):

1. I found standable cells inside the egg's hatch region with a gdb scan of `getPositionInfo`. The floor is z 0: for example (2120,2278..2406,0) and (2328..2376,2374..2406,0).
2. I teleported to valid floor at (2344,2486,0), outside the box.
3. I walked north with the mouse. A breakpoint on `Egg::hatch` caught `EGG HATCH obj=14611 shape=73 q=304 (2200,2230,8)` with the Avatar at (2344,2414,0).
4. I walked several more bursts around the room, ending at (2424,2406,0).

Results: 0 guard lines, and the mover and scheduler were alive. With
`lbStarted` = 1 the egg only runs its apparition cleanup (`lv-new/LBSCENE.UNK`).
The egg's usecode never moves the Avatar, and neither does the scene's
(`lv-patched/LORDBRIT.UNK`: no Avatar teleport or move).

A walking player only stands on positions the engine has validated, and a
stand from a valid supported spot plays for real ticks. So walking cannot
create the precondition. I did not settle whether the room is reachable from
outside the house on foot; it doesn't affect the answer.

**Through other wedges: yes, in principle.** The precondition is "Avatar
embedded plus movement input", and it has occurred without cheats:

- `docs/playtest-2026-10-09-lane.md:116` (T5) records the same symptom, 3× `Seem to be stuck in process loop` with the mover gone. A keyboard jump had wedged the Avatar inside a Map 39 wall, and the retail niche walls did the same (C3).
- bbcfa209 fixed that jump wedge. The tunnel-wall jumps since then show 0 wedges: 24 in `docs/playtest-2026-10-09-engine.md` (E4a) and 21 in `docs/playtest-2026-10-10-jumps.md` (J4a).
- Any future wedge would hit the same loop: a teleport egg or usecode `teleport` landing inside geometry, a jump case not yet found, or an item moved onto the Avatar.
- **What the player sees:**
  - a freeze of ~30 s on the step path, or a few seconds on the turn path;
  - then no walking until a reload;
  - NPC schedules stop with the SchedulerProcess;
  - and whatever FREE timer sat after the mover is killed early.

## 6. Proposed fix (fork; not applied)

The fix makes the mover decide at most once per kernel tick. A real animation
ends on a later tick than it started (it plays at least one frame), so only the
zero-length cycle is cut. In that case the mover waits for its next tick
instead of being re-run in the same pass. The diff is against
`scummvm-lv-console` (`engines/ultima/ultima8/world/actors/`):

```diff
--- a/engines/ultima/ultima8/world/actors/avatar_mover_process.h
+++ b/engines/ultima/ultima8/world/actors/avatar_mover_process.h
@@ -143,6 +143,10 @@
 	MButton _mouseButton[2];
 
 	uint32 _movementFlags;
+
+	// Kernel tick of the last run() that got past the once-per-tick check.
+	// Not saved: it only has to outlive one Kernel::runProcesses pass.
+	uint32 _lastRunTick;
 };
 
 } // End of namespace Ultima8
--- a/engines/ultima/ultima8/world/actors/avatar_mover_process.cpp
+++ b/engines/ultima/ultima8/world/actors/avatar_mover_process.cpp
@@ -33,7 +33,7 @@
 namespace Ultima8 {
 
 AvatarMoverProcess::AvatarMoverProcess() : Process(),
-		_lastAttack(0), _idleTime(0), _movementFlags(0) {
+		_lastAttack(0), _idleTime(0), _movementFlags(0), _lastRunTick(0) {
 	_type = 1; // CONSTANT! (type 1 = persistent)
 }
 
@@ -66,6 +66,22 @@
 	Actor *avatar = getControlledActor();
 	assert(avatar);
 
+	// LOST VALE: at most one decision per kernel tick. Most branches below
+	// end in waitFor(doAnim(...)), and Process::wakeUp() schedules the woken
+	// mover NEXT in the same Kernel::runProcesses pass. An Avatar embedded in
+	// geometry (a teleport into furniture, a jump wedged in a wall) has every
+	// animation refused on its first frame, so the anim process ends at once
+	// and the mover runs again, and again: the step fallback and a held turn
+	// key both spun until the runaway guard ("Seem to be stuck in process
+	// loop") killed this mover and every process after it in the pass, the
+	// SchedulerProcess among them. A real animation ends on a later tick than
+	// it starts, so only that zero-length cycle is cut; the mover just
+	// decides again on its next tick.
+	const uint32 tick = Kernel::get_instance()->getTickNum();
+	if (tick == _lastRunTick)
+		return;
+	_lastRunTick = tick;
+
 	// busy, so don't move
 	if (avatar->isBusy()) {
 		_idleTime = 0;
```

**Why this shape:**

- **It covers every path.** The cycle can start from any mover branch that ends in `waitFor(doAnim/turn…)`: the step fallback, `checkTurn`/`turnTowardDir` on a held turn key, slow-from-run, and readying a weapon. I tested a step-only guard (a `tryAnim(stand)` check before `doAnim`) and it **still tripped the guard** on a held Left (run 6). Guarding the mover's entry covers every branch with one check.
- **No save-format change.** `_lastRunTick` is transient, and `kernel.h` is already included.
- **The kernel stays as it is.** The alternative is to stop `setNextProcess` from re-running a woken process in the same pass. That changes timing for every waiter in the game, usecode included.
- **The Avatar stays wedged, but the world stays alive.** The player can still reload or teleport, and no process is killed.

**Verified in the scratch build only**: `scummvm-lv` sources plus this diff,
run 8, on `run-s1-lbdone`.

| Input | Result |
|---|---|
| Up tap | world live (screens differ 4 s later); 0 guard lines |
| Left held 1.5 s | world live; 0 guard lines |
| Up, Left, Down, Right, Up, Right ×2; six mouse walks (including run distance); SPACE; Up+SPACE | world live; 0 guard lines and 0 `Process::fail` hits. `lvprocs` lists the mover (pid 3), SchedulerProcess (pid 5) and FREE; the tick advanced to 881298. The Avatar was still at (2200,2300,8), wedged, as expected |
| Regression: teleport to valid (2344,2486,0), walk north 0.6 s, then east 1 s | reached (2344,2414) and then (2520,2414,0). The 0.6 s north burst covered 72 units, the same as the unfixed binary in run 4b |

**Optional extras, not built or tested:**

- **Contain the guard's collateral.** In `Kernel::runProcesses`, reset `num_run = 0` after the guard's `p->fail()`. Then one runaway kills one process, not the rest of the pass. It would also limit the load-time kills noted in the comment in `AvatarMoverProcess::terminate()` (2026-08-18: eight processes). Upstream's guard has the same over-kill [INFERENCE: the code is unmodified].
- **Unwedge.** When the mover finds its Avatar at an invalid position, search further (a wider `scanForValidPosition`, or upward) and move him out. This is a behaviour change and needs its own design.
- **Checkpoint hygiene.** `run-s1-lbdone.sav` should be re-banked with the Avatar on valid floor, for example (2344,2414,0), which is inside the egg box. Until then, "teleport before the first move" (the leftovers report's workaround) is mandatory.

## Harness notes

- **gdb queues commands.** gdb reads typed commands only while the inferior is stopped. A `kill` / `file` / `run` written while the game ran was executed at the next SIGINT. My first "fixed binary" check therefore drove the *previous* instance; I caught this by its start time, and the result was discarded and redone (runs 5x/8). Check `ps -o lstart` on the child before sending input.
- **Never call `MainActor::teleport` from gdb while stopped inside `GameMapGump::PaintThis`.** A map switch mid-paint invalidates the item-list iterator and segfaulted the game (run 4, a harness artifact). Teleport at a `tbreak Kernel::runProcesses` instead.
- **Never rebuild a binary while gdb has it loaded.** gdb itself died with a bus error.
- **Use `set language c++` after interrupting in a libc frame**, or `Ultima::Ultima8::…` expressions fail with "No type".
- **The game copy needs a top-level `FIXED.DAT`** for detection. Without it the launcher appears instead of the game.

## Disk changes

- **Wrote** this report.
- **Scratch**, in `/tmp/claude-1000/vfreeze/`:
  - `game/` (a copy of `shared/data/u8-install`, plus a top-level `FIXED.DAT`);
  - `saves/` (`ultima8.001` = `run-s1-lbdone`; `ultima8.000` is an engine autosave);
  - `build/` (the scratch ScummVM: the full `scummvm-lv` sources plus the proposed fix);
  - `fix.diff`, `gdb.out` (every backtrace and sample above), `lv.log`, the `procs.py`/`scan.py`/`sample.gdb` gdb helpers, and screenshots `r*.png`.
- **Stopped:** my gdb sessions, my ScummVM instances and Xvfb `:96`.
- **Not touched:** `scummvm-lv/`, `scummvm-lv-console/`, `shared/`, the builders, `~/lv-checkpoints/` (read only), `TODO.md` and `HANDOFF.md`.

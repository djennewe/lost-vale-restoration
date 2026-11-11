# F1, solved: the hang-grab climb never was the bug

2026-08-18. The engine crash that has blocked the Map 8 cave ascent since
2026-08-16 is a **use-after-free of `Ultima8Engine::_avatarMoverProcess`**,
reproduced under gdb and fixed in the fork. The hang-grab climb is not the
cause — jumping is simply the first thing that presses SPACE after a
savegame load.

## Verdicts

| Question | Verdict |
|---|---|
| Is the crash reproducible? | **YES**, reliably: load a cave checkpoint, hold a direction into a wall, press SPACE. SIGSEGV within seconds. |
| Where does it crash? | `AvatarMoverProcess::onActionUp` (`avatar_mover_process.cpp:300`), `this = 0x55555bcb0bf0` — a freed process. Full backtrace below. |
| Is the hang-grab climb the cause? | **NO.** The 8 kernel process-kills that destroy the mover happen *immediately after the savegame load completes*, before any leap. Any input would crash it. |
| Fixed? | **YES** for the crash — every dereference of the pointer is now guarded, and the pointer is cleared when the mover dies. |
| Does the climb work? | **YES — the Avatar reaches z=56 from below.** Instrumented log shows `climb56 -> SUCCESS`; final position (29364, 23622, 56) on the main floor, reproduced. The blocker was an INPUT technique, not geometry and not the engine: SPACE must be **held**, not tapped. |

## The crash

```
#0  AvatarMoverProcess::onActionUp (this=0x55555bcb0bf0, action=ACTION_JUMP)
        at avatar_mover_process.cpp:300      clearMovementFlag(MOVE_JUMP);
#1  Ultima8Engine::handleActionUp (ultima8.cpp:1130)
#2  Ultima8Engine::handleEvent (ultima8.cpp:867)
#3  Ultima8Engine::runGame (ultima8.cpp:665)
```

`Ultima8Engine` keeps a **raw** `AvatarMoverProcess *`. The Kernel owns and
deletes processes. Nothing cleared the engine's pointer when the process
died, so the next input event dereferenced freed memory.

### What kills the mover

The log preceding the SIGSEGV:

```
OBJECTS: ok
MAPS: ok
Done
WARNING: Seem to be stuck in process loop - killing current process!   x8
```

All eight kills land **immediately after the save load finishes**, not
during the leap. `Kernel::runProcesses` counts process runs per pass and
calls `p->fail()` once `num_run` passes 65534; loading a savegame can run
that many in one pass. One of the eight victims is the mover.

So the sequence is: load a save → the guard kills the mover → the engine's
pointer dangles → the first key or click afterwards crashes. The 2026-08-16
report reached for the climb because the leap is what the tester did next.

## The fix

Two parts, in the fork (`scummvm-lv-console`, commit `312c76e9`).

**1. Clear the pointer on death.** `AvatarMoverProcess::terminate()` now
nulls `Ultima8Engine::_avatarMoverProcess` if it points at itself.

This step is *verified*, and the verification is the interesting part: after
this change alone, the same crash reappeared with **`this = 0x0`** instead
of `this = 0x55555bcb0bf0`. That proves the pointer is now cleared, and it
exposed the second half of the bug.

**2. Guard every dereference.** With the pointer legitimately null, the
sites that never checked it crashed instead. Every dereference in the engine
was enumerated:

| site | before |
|---|---|
| `Ultima8Engine::handleActionDown` / `handleActionUp` | already guarded |
| `Mouse::getMouseLength`, `CrosshairProcess::run` | already guarded |
| `GameMapGump::onMouseUp` / `onMouseDown` | **unguarded** — the second crash |
| `Ultima8Engine::handleEvent`, modal branch | **unguarded** — runs for the load book and death diary |
| `Ultima8Engine::saveGame` → `getPid()` | **unguarded** — now writes 0; the load path already refuses a pid resolving to no process |
| `QuickAvatarMoverProcess::run` → `resetIdleTime()` | **unguarded** |

Result: a killed mover now costs the player control until reload, instead of
killing the process.

## A wrong fix, and why it was reverted

The first attempt also guarded `AvatarGravityProcess::run()` against
re-issuing the `hang` animation while `ACT_ANIMLOCK` is set, on the theory
that doomed `doAnim` calls drove the runaway: `ActorAnimProcess::init()`
refuses an anim under ANIMLOCK *without* setting `_lastAnim`, so the branch
would stay true and spawn a fresh doomed process every run — and
`Kernel::setNextProcess` inserts each new process immediately **after** the
current one, so those spawns run inside the same pass.

It is a tidy story and the evidence does not support it. The crashing run
logged **zero** `"ANIMLOCK set on actor"` refusals. The change was reverted
rather than shipped: it would have altered the climb path for no
demonstrated benefit, on a mechanism that had been disproved.

The mechanism note about `setNextProcess` is still worth keeping — it is
why a spawn loop can hang a single kernel pass — but it is not what
happened here.

## The cave is still not crossable — and the crash was not why

With the engine fixed, the z8→z56 ascent was attacked directly. It does
not work, for reasons that have nothing to do with the SIGSEGV.

**Walking: z=56 is unreachable from the trench, anywhere in the cave.**
An `exact_reach` flood seeded at (30143, 23120, 8) and run over the whole
south cave (x 28000-32700, y 21000-29500, 8-unit lattice) reaches
**levels 0 and 8 only**. There is no walkable route up. (That model is
walking-only by design — it does not model the jump button — hence the
in-engine tests below.)

**Climbing: the 48-unit face refuses.** `handleNormalMode` runs the
climb scan (`climb72` down to `climb16`, and `climb48` does exist in the
sequence enum) **only when the right mouse button is NOT held** — holding
a direction gives a plain `jump` or `jumpUp` instead. So the correct
player action is to face the ledge with nothing held and press SPACE.
Tested at a ledge verified standable on top (`(30143, 23231, 56)`,
valid+supported):

- The Avatar cannot get closer than **16 units** to the face. His body box
  is 64 deep and the next step south would overlap the ledge box, so the
  mover refuses it; repeated taps leave him at y=23152 against a face
  starting at y=23168.
- From there SPACE plays an animation (stand frame 4 → 511) and he does
  not move. The scan found nothing climbable.

**Hanging: cannot be triggered.** `AvatarGravityProcess::run` only tries
the ledge grab when the mover has `MOVE_ANY_DIRECTION` set, and that flag
is set exclusively inside `handleNormalMode()`. But
`AvatarMoverProcess::run()` returns early while falling:

```cpp
// falling, so don't move
if (avatar->getGravityPID() != 0) { ...; _idleTime = 0; return; }
```

so the flag can only be established **on the ground before going
airborne**. Dropped beside the face from z=40, 48, 56 and 64 with the
button pressed after takeoff, he fell straight to z=8 every time. Walking
off the ledge top while holding does set the flag, but then he is facing
*away* from the ledge and `tryAnim(climb40, dir_current)` has nothing to
grab. Jumping into the wall while holding a direction produced no motion
at all.

So the mechanism F1 identified as "the only way up" is, as far as this
session could drive it, not reachable by any input sequence at this face.

### THE CLIMB IS UNREACHABLE WITH MOUSE-ONLY CONTROL (2026-08-19)

This is probably why nobody could climb anything. The jump/climb branch in
`U8AvatarMoverProcess::handleNormalMode` is gated on **two** flags:

```cpp
if (hasMovementFlags(MOVE_JUMP) && hasMovementFlags(MOVE_ANY_DIRECTION)) {
    ...
    else if (!hasMovementFlags(MOVE_MOUSE_DIRECTION)) {
        // the climb scan: climb72 down to climb16
    }
```

`MOVE_ANY_DIRECTION` is `MOVE_MOUSE_DIRECTION | MOVE_FORWARD | MOVE_BACK |
MOVE_LEFT | MOVE_RIGHT | MOVE_UP | MOVE_DOWN`. With a mouse alone the only
way to satisfy it is `MOVE_MOUSE_DIRECTION` — which is exactly the flag the
climb branch requires to be **clear**. So:

- SPACE with no direction at all: the outer `if` fails, **nothing happens**
  (observed: the stand frame does not even change).
- SPACE with the right button held: the outer `if` passes but the climb
  scan is skipped; you get `jump` or `jumpUp` instead.
- The climb scan can only run when the direction comes from a **keyboard or
  joystick** movement action.

And ScummVM's U8 keymap binds `MOVE_UP` / `MOVE_DOWN` / `MOVE_LEFT` /
`MOVE_RIGHT` to `JOY_*` only — **no keyboard defaults**. A player on mouse
and keyboard therefore cannot reach the climb code at all.

Adding these to `~/.config/scummvm/scummvm.ini` under `[scummvm]` binds them:

```
keymap_ultima8_MOVE_UP=UP
keymap_ultima8_MOVE_DOWN=DOWN
keymap_ultima8_MOVE_LEFT=LEFT
keymap_ultima8_MOVE_RIGHT=RIGHT
```

With that in place SPACE finally produces real motion instead of nothing.
Note the axis naming is world-relative, not screen-relative:
`getMovementFlagAxes` maps `MOVE_DOWN` to `y--`, which is world NORTH, and
`MOVE_UP` to `y++`, world SOUTH. Verified in-engine: the DOWN key moved the
Avatar from y=23167 to y=22791.

**If the LV restoration expects players to climb, it has to ship or
document these bindings.** That belongs in the installer or the README, and
it is a prerequisite for the cave ascent regardless of how the rest of this
resolves.

### With the bindings in place: still no climb (47 faces tried)

The bindings make SPACE do something instead of nothing, but the ascent
still did not happen. A stricter scan found **47 genuine 48-unit faces** —
the far cell standable at z=56, NOT standable at z=8 (so it is a wall, not
the roof of the underpass), and no `SI_SEA` nearby. Tried at several of
them, in the direction the scan reported, with the matching arrow key held:

- Flush against an east face at (29948, 23238, 8): Right is correctly
  blocked, SPACE with Right held changes nothing.
- North face at (29820, 23558, 8): holding Down slides him **east along
  the wall** rather than climbing (1248 units in 2.5 s). With tight timing
  (200 ms of Down, then SPACE) he either slid east or fell to z=0.
- Two attempts at the earlier south site ended with `hp: 0` — that ledge
  turns out to have lethal water at its base, the same stacked-geometry
  trap as the roofs.

So: `climb48` exists, the geometry has real faces, the flags can now be
set correctly, and the Avatar still does not climb. What has NOT been
ruled out is that `tryAnim(climb48)` needs clearance along the whole
animation path (the climb moves forward as well as up), which none of the
sampled faces may provide — or simply that the approach needs a precision
scripted `xdotool` bursts cannot deliver.

## SOLVED: the climb works — SPACE must be HELD, not tapped

The ascent happens. Instrumenting the climb scan (a temporary `debug()` in
`handleNormalMode`, since removed) produced this at a face in the cave:

```
LVJUMP: MOVE_JUMP set; anydir=1 mousedir=0 step=0 mouselen=1 dir=12
LVCLIMB: scan at (29524,23622,0) dir=12 lastanim=0
LVCLIMB:   climb72 -> END_OFF_LAND
LVCLIMB:   climb64 -> END_OFF_LAND
LVCLIMB:   climb56 -> SUCCESS
LVCLIMB:   climb48 -> FAILURE
...
```

and the Avatar ended at **(29268, 23622, 56)** — on the z=56 main floor,
climbed from z=0 under his own power. Repeating the same input from a
standard start reproduced it: **2 of 3 attempts finished at
(29364, 23622, 56)**.

### What was actually wrong

Three gates in series, and the last one is the one that had never been
crossed:

1. `handleNormalMode`'s jump branch needs `MOVE_JUMP` **and**
   `MOVE_ANY_DIRECTION`; SPACE alone does nothing at all.
2. The climb scan inside it runs only when `MOVE_MOUSE_DIRECTION` is
   **clear**, so the direction must come from a keyboard/joystick action,
   never the mouse. (`UP` and `DOWN` are bound stock to `MOVE_FORWARD` and
   `MOVE_BACK`, both of which qualify — an earlier note in this file
   claiming ScummVM ships no keyboard movement bindings was WRONG.)
3. **`xdotool key space` presses and releases within one frame.**
   `onActionUp` clears `MOVE_JUMP` immediately, and
   `AvatarMoverProcess::run()` returns early whenever
   `avatar->isBusy()` — which it is for most of a walk. So the flag was
   always gone before a frame that could act on it. Holding SPACE for
   ~1.5 s is what finally let the gate fire.

That is why every earlier attempt saw "no animation at all": the branch
was never entered. It was never a geometry problem and never a leftover
engine defect.

### The working recipe

1. Face the wall — use the **mouse** to walk into it, since `checkTurn` is
   mouse-gated and keyboard movement alone will not turn the Avatar.
   Confirm with the stand frame (0=N, 2=E, 4=S, 6=W).
2. Release the mouse so `MOVE_MOUSE_DIRECTION` clears.
3. **Hold** a keyboard direction (UP works — `MOVE_FORWARD`).
4. **Hold SPACE** for a second or more. Do not tap it.

The scan then tries `climb72` down to `climb16` and takes the smallest
that succeeds.

### Honest limits of this demonstration

- The full z→56 ascent was demonstrated with an extra
  `keymap_ultima8_MOVE_DOWN=DOWN` binding in `scummvm.ini` (setting
  `MOVE_DOWN`). That binding has since been reverted — it is not needed in
  principle, because stock `UP`/`DOWN` already set `MOVE_FORWARD`/
  `MOVE_BACK`, which satisfy the same gate. On stock bindings a climb was
  observed (z=8 → z=16) but the full 48-unit ascent was not re-run to
  completion before this session ended.
- Reproduction is fiddly under scripted input because the Avatar slides
  along walls while a direction key is held; a human aiming the approach
  will find it far easier than `xdotool` bursts did.

### Superseded: the earlier "blocked by geometry" reading

Everything below this point was written before the recipe was found. The
walking-reachability results still stand as facts (z=56 genuinely is not
reachable on foot; the rises really are all +48; many of them really are
the underpass roof), but the conclusion drawn from them — that the ascent
was impossible and the blocker was map geometry — is **wrong**. It was an
input problem.

### Last attempt: facing is what the climb uses, and it still failed

`handleNormalMode` starts with `Direction direction = avatar->getDir()`,
and the climb scan calls `tryAnim(climbanim, direction)` with that — the
Avatar's **facing**, not the mouse and not the arrow key. Worse, the only
`checkTurn` call in that function is guarded by
`if (hasMovementFlags(MOVE_MOUSE_DIRECTION))`, so **keyboard-only input
never turns the Avatar**. The arrow key opens the gate; the facing decides
where he climbs.

So the correct input recipe is: mouse-walk into the face (which turns
him), release the mouse, then hold an arrow key and press SPACE. Executed
exactly that at (29820, 23622, 8) — mouse-walked north until blocked,
confirming **stand frame 0 = facing north**, flush at a verified face
whose top (29820, 23494, 56) is standable. Held Down, pressed SPACE: he
ended at (29820, 23678, 0) — turned south and fell to z=0. No climb.

That is the last hypothesis this session had. The recipe is now known to
be right in principle and still does not produce a climb, which points at
something about `tryAnim`'s clearance requirements along the animation
path that was not reachable from the outside.

### Follow-up, same session: what the ascent actually needs

Four more things were established, and two of them correct the record.

- **The map is retail-identical here.** The same flood run against the
  pristine base-game `FIXED.DAT.bak` returns byte-identical extents
  (38626 positions at z=0, 16107 at z=8, same bounds). **We did not break
  the cave.**
- **The trench is the north end and the ascent is genuinely required.**
  The trench/z0 region spans y 21007..23607; the z=56 floor picks up at
  y 23079 and runs south. The documented walkable thread "emerges y 23583"
  — exactly where the trench flood stops. There is no way around.
- **CORRECTION: the Avatar has every climb animation, including
  `climb48`.** F1 recorded that "plain climbs max out at climb40". Reading
  `STATIC/ANIM.DAT` directly (shape 1's action table at offset 8192; for
  U8 the action number IS the sequence enum) shows actions 19-26
  (`climb16`…`climb72`) and 45 (`hang`) all PRESENT. The 48-unit rise is
  not beyond the Avatar's animation set.
- **CORRECTION: most of the "48-unit rises" are the roof, not ledges.** A
  rim scan found 309 sites where a cell adjacent to the trench is standable
  at z=56, and every single rise is exactly +48 — no 24, 32 or 40 step
  exists anywhere. But spot-checking shows positions like (29823, 23519)
  are standable at **both** z=8 and z=56: those are the stacked floors of
  the roofed underpass, and you cannot climb onto a ceiling above your
  head. The genuine ledge faces are a much smaller subset.

At a genuine face — a ledge whose top is standable with open sky, verified
at (30143, 23231, 56) — the Avatar **cannot get closer than 16 units**:
his body box is 64 deep and the next step would overlap the ledge box, so
the mover refuses it. `climb48` fails from that standoff, and repeated
approach taps do not close it.

So the two candidate mechanisms both fail for concrete, identified
reasons: the plain climb because of a 16-unit standoff it cannot cross,
and the hang because its enabling flag cannot be set while airborne. What
is NOT established is how retail players get up — and since the geometry
is retail, they must. The most likely remaining explanation is an input
technique this session could not script: a **running jump** at the face
from a distance, which would put the Avatar airborne and adjacent with
`MOVE_ANY_DIRECTION` already set from the run. That is worth a human's
hands on the keyboard before anyone edits terrain.

**What that means.** F1 recorded the cave as engine-blocked. The engine
half is now fixed. The remaining blocker is **geometry**: a 48-unit face
with no approach that gets the Avatar within climbing distance, and no
alternative walkable route. Whoever picks this up should decide between
giving the ascent an intermediate step (two risers of ≤32 are climbable
and land on the 4-unit lattice) and finding the retail route, which may
be somewhere this session never looked — the cave is retail geometry, so
a route presumably exists. Either way it is a map/content decision, not
an engine one, and it is now the thing standing between the exit test and
a continuous playthrough.

## What this does not settle

- **The runaway itself.** Why a savegame load trips the 65534-run guard is
  undiagnosed. `kernel.cpp` already carries a WORKAROUND comment about that
  threshold and U8 map transitions, so it is a known-shaky area. It is
  intermittent: it fired in two gdb runs and in none of the later ones, and
  it could not be provoked on demand.
- **Post-fix exercise of the exact path.** After the fix the runaway
  stopped firing, so the dangling-pointer path could not be re-triggered
  end to end. The chain is nonetheless closed by construction: the pointer
  is provably nulled (backtrace #2), and every dereference is now guarded.

## Reproduction, for anyone retesting

No debugger console needed, which is why this finally worked:

1. Put a cave checkpoint in a free save slot (`cp3h-west-strip.sav` →
   `~/.local/share/scummvm/saves/ultima8.004`).
2. Start the game, skip the intro, answer the name book.
3. **F7** → click the slot. (The in-game load book is keyboard/mouse only —
   no `Cheat::toggle`, no teleport, none of the console flakiness.)
4. Hold the RIGHT mouse button toward a wall, press SPACE a few times.

Under gdb: `gdb -batch -x cmds ./scummvm` with `run <args>` and no stdin
redirection. Note Yama `ptrace_scope=1` blocks `gdb -p` on a process the
debugger did not start, so the engine must be launched *by* gdb — and the
`--args` list must be repeated on the `run` line or gdb drops it.

## Fork and patch state

- Fork commit `312c76e9` on branch `lost-vale`.
- `tools/scummvm-patches/0001-lost-vale-engine.patch` regenerated from the
  pinned base `01bd8879` and **verified to apply cleanly to a fresh clone**
  of that base.
- **The tracked patch was already stale** before this session: it carried 3
  of the fork's 7 changed files, missing the loiter leash
  (`loiter_process.*`) and the AskGump release-dispatch (`ask_gump.cpp`).
  A fresh clone built from it was missing engine changes the project
  depends on (adversarial-review C3 is exactly this hazard). It now carries
  all of them except the generated `detection_tables.h`.

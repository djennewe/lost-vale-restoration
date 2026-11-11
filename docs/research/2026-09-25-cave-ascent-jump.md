# Research: the floor and the Map 8 cave ascent (2026-09-25)

**The floor cannot change the climb decision.** From a z=0 start the engine
decides the climb in `Actor::tryAnim(climb56, west)`, and nothing in that
path reads the z<=0 freebie or a z=0 floor tile. An offline replica of
`tryAnim` over the built Map 8 gives identical results with and without the
184 floor tiles at every x from 29492 to 29544 and at z 0, -4 and -8, and it
reproduces the in-engine window. The 4/4 against 2/11 in
`docs/playtest-2026-09-25-map8-floor.md` (W1b) therefore comes from state
the floor does not touch. Two candidates fit the record, both unverified: a
leaked debugger command that toggled combat mode, and the ghoul seen in the
trench plates. Confidence that the floor is not the cause: about nine in
10. Confidence in either candidate: about one in three each.

Source read against `scummvm-lv-console` at `e0d6084d`; all paths below are
relative to `engines/ultima/ultima8/`. Nothing was built, installed, or
launched.

## Verdicts

| ID | Question | Verdict |
|---|---|---|
| Q1 | Does the climb test need a support item under the start? | **No.** The start box enters only as a blocker exclusion. |
| Q2 | Does the z<=0 freebie enter the climb decision? | **No.** climb56 has no on-ground frame and ends at z=56. |
| Q3 | Does a floor tile change `tryAnim` at the window? | **No.** Replica: identical at 42 positions. |
| Q4 | Can a grounded or falling flag differ? | **No** at z=0: gravity never starts there. |
| Q5 | Can z drift below 0? | **Only on canonical, only after a blocked on-ground step**, and z<0 would widen the window. No attempt recorded one. |
| Q6 | What makes "first attempt works, later fail"? | **Not established.** Combat-mode toggle by leaked keystrokes, or the ghoul. |

## The decision path, step by step

1. **SPACE sets `MOVE_JUMP`; UP sets `MOVE_FORWARD`**
   (`world/actors/avatar_mover_process.cpp:253`, `onActionDown`).
2. **The mover skips a tick while busy or falling** and keeps the flag:
   `isBusy()` returns at `avatar_mover_process.cpp:70`, a live gravity PID at
   `:81`. A deferred SPACE is processed later with both flags set, so it
   defers the climb and cannot cancel it.
3. **Combat mode has no jump at all.** `run()` sends an in-combat Avatar to
   `handleCombatMode()` (`:99`); that function
   (`world/actors/u8_avatar_mover_process.cpp:92`) never reads `MOVE_JUMP`.
   Every `MOVE_JUMP` read in the file is in `handleHangingMode` (`:78-82`)
   or `handleNormalMode` (`:438-507`).
4. **Normal mode runs the climb scan** in both jump branches: `:464` (jump
   plus a direction) and `:506` (jump alone, which first calls
   `checkTurn(mousedir)` and so depends on where the cursor sits). Both try
   `climb72` down to `climb16` and keep the lowest success (`:485-491`,
   `:518-525`).
5. **`Actor::tryAnim`** (`world/actors/actor.cpp:595`) steps an
   `AnimationTracker`, then requires `getPositionInfo(end).supported`
   (`:633-639`).
6. **`AnimationTracker::step`** consults support only on frames flagged
   `AFF_ONGROUND` (`world/actors/animation_tracker.cpp:332`, `:379-386`); an
   off-ground frame fails only if blocked.
7. **`getPositionInfo`** (`world/current_map.cpp:694`) uses the start box
   only to exclude blockers the mover already overlaps (`:730`). Support is
   an item top equal to the target z with land within 8 (`:769`), or the
   freebie `target._z <= 0` (`:773`).

The Avatar's anims from `STATIC/ANIM.DAT` (shape 1, direction west):

| anim | frames | on-ground frames | total dz | travel |
|---|---|---|---|---|
| climb56 | 11 | none | 56 | 56 units west, all after the rise |
| climb64, climb72 | 15, 30 | first three (at the start z) | 64, 72 | 80, 64 |
| climb48 | 11 | first one | 48 | 40 |
| jump | 18 | first three and last five | 0 | 408 |

So climb56 rises 56 straight up at the start x, then moves 56 west onto
the shelf. Its verdict depends on blockers in the rise column and on
support at the end, where the shelf's shape-301 tiles at z=56 supply it. A
shape-301 tile at z=0 has footpad (4,4,0): it cannot overlap a box at z>=0
(`Box::overlaps`, `misc/box.h:100`) and it supports only z=0. It never
enters the climb56 computation.

## The offline replica

`docs/research/2026-09-25-cave-ascent-jump/climb_sim.py` reimplements
`getPositionInfo`, `Box::overlaps`, `AnimationTracker::step`, and the end
check of `tryAnim` over the built `FIXED.DAT` (globs expanded, Map 8), with
frame data read from `ANIM.DAT`. It runs every climb anim west from
(x, 23622, z), on canonical items and on canonical plus the 184 tiles from
`floor.diff`.

```
z=0   x 29492..29500: no climb        x 29504..29524: climb56    x 29528..29544: no climb
z=-4  every x: no climb (no climb height lands on 56)
z=-8  x 29492..29500: no climb        x 29504..29544: climb64
canonical and floored identical at all 42 (x, z) pairs
```

In-engine, 2026-09-01 test A3 found climbs at 29508, 29516 and 29524 and
failures at 29500 and 29532. The replica matches every tested point; 29504
was never tried in-engine.

Limits: the replica sees `FIXED.DAT` only, so NPCs, monsters, and anything
from `NONFIXED.DAT` are invisible to it. The working-tree `FIXED.DAT` hashes
`6c518f4f…` against canonical `00925049…` because of the uncommitted Map 17
edits; `build_map_08.py` has no change since `64a548b`, so Map 8 is the
canonical Map 8.

## The other mechanisms, checked

- **Gravity at z=0.** `GravityProcess::run` terminates when `z <= 0` and
  falling (`world/gravity_process.cpp:104`) and clamps a target below 0 to
  0 (`:115`). `ActorAnimProcess` starts a fall only when `pt.z > 0`
  (`world/actors/actor_anim_process.cpp:211`, `:239`, `:350`). Nothing
  starts gravity for an Avatar standing at z=0 on either build. A stale
  gravity PID would log `FIXME: Removing stale gravity pid`
  (`avatar_mover_process.cpp:84`).
- **z below 0.** This is the one floor-dependent difference found.
  `scanForValidPosition` (`world/current_map.cpp:779`) runs only when an
  on-ground step is blocked. It probes z offsets `{0, -4, 4, -8, 8}`
  (`:905`) and counts support only from solid tops. Over void at z=0 it
  can return z=-4 or -8; a floor tile marks offsets -8..-1 invalid, so with
  the floor z stays at 0 or above. The replica shows z=-4 kills the climb
  and z=-8 widens the window (climb64), so a drift would show as mixed
  results. Every recorded position read z=0, and `Actor::teleport` moves to
  the exact z given (`actor.cpp:437-450`), so each attempt started at z=0 if
  the reads were current.
- **A cached ground item.** There is none. `info.land` feeds only the
  footstep sound switch (`world/actors/actor_anim_process.cpp:468-469`) and
  the bridge-slope adjustment (`world/actors/animation_tracker.cpp:301-330`).
  It is recomputed on every step and nothing stores it on the Actor.
- **Repeat-frame skip.** `AnimAction::getAnimRange` drops frame 0 when the
  last anim equals this one in the same direction
  (`world/actors/anim_action.cpp:56`). A second climb56 straight after a
  climb56 would start at frame 1 and end at z=49. Successful attempts walked
  on after the climb (they end at x 29356..29364, 100 units past the climb's
  end), so the last anim was a walk. Ruled out.

## Why later attempts failed: two candidates

**Combat mode toggled by leaked debugger keystrokes.** `dbg.sh` opens the
console with Ctrl+Alt+D, a toggle. The playtest records that about every
other call the teleport did not land and letters reached the game (`i`
opened the pack). The teleport command `MainActor::teleport 8 29516 23622 0`
contains one lowercase `c`, the stock **Combat** key (`metaengine.cpp:46`,
handled at `ultima8.cpp:928-931`). Each leaked teleport therefore toggles
combat mode, and it stays toggled across later teleports. In combat mode
SPACE does nothing (step 3 above) and UP plays `advance`: 72 units per 14
ticks against `walk`'s 200 per 18. A failed attempt moved 286 units in the
1.6 s hold; the 2026-09-01 plain walk from x=29500 moved 504. That is
consistent with `advance`, but it does not discriminate: a `readyWeapon`
inserted by `checkWeapon` would shorten combat travel, and the normal-mode
failure path (a jump blocked by the z=56 shelf at frame 6, a fall from
about z=16, then a walk) also lands short of 504. The `0x800` read below
decides it. The first attempt of a session comes before
any leak, which fits the pattern. The floored session's four attempts would
have needed an even number of leaks, or none.

**The ghoul.** Shape 142 is SI_SOLID with the Avatar's footpad (2,2,5), and
the trench plate P1 shows a wandering ghoul on both builds. A body in the
rise column or the landing box (about x 29300..29472, y 23558..23622,
z 56..96) makes `tryAnim` fail. A hit during the hold runs
`killAllButFallAnims` (`actor.cpp:1239`) and then `stumbleBackwards`
(`:1284`), which aborts a climb in progress. The nearest ghoul egg is at
(30018, 23534, 56), 306 units from the trench seed, with range (0, 1) and a
48-unit z window (`world/egg_hatcher_process.cpp:58`), so it hatches only for
an Avatar standing at z 9..104 over that spot. The ghoul in the plates is
from elsewhere. An in-map `tp` does not reload the map
(`world/world.cpp:110`), so a ghoul that has found the Avatar stays for
every later attempt.

## The in-engine test that separates these

Protocol as W1, on both builds, with these reads before each SPACE and after
each result. Each read must be confirmed as fresh, for instance by reading
twice and requiring the reply to carry the command typed last.

1. `ObjectManager::objectInfo 1`: x, y, z, `hp`, and actor `flags`. Bit
   `0x800` is `ACT_INCOMBAT` (`world/actors/actor.h:402`).
2. `ObjectManager::findShape 142`: every ghoul, against the rise column and
   the landing box.
3. `Kernel::listProcesses 1`: any GravityProcess or ActorAnimProcess still
   attached to the Avatar at keydown.
4. After a failure, `objectInfo 1` again for `hp`.

Predictions. If `0x800` is set before every failure and clear before every
success, the cause is the leak; `MainActor::toggleCombat` flips it back, and
issuing each dbg command only after a console-open check removes it. If a
ghoul is in the box or `hp` drops, it is the ghoul. If z reads below 0, it
is the void drift, and that one would favour the floor. A z=0 start with
`0x800` clear, no ghoul within 200 units, and a failure anyway would
contradict this analysis.

A second test is cheaper: run the canonical protocol, read `flags` before
every attempt, and issue `MainActor::toggleCombat` whenever `0x800` is set. If canonical
then climbs at the floored build's rate, the floor played no part.

## What this means for the two decisions

- **Floor Map 8's south route or not.** W1b gives the floor no support. The
  source says a z=0 floor cannot make the climb more reliable. The case for
  flooring rests on its other effects: the strict model reaches the gate
  approach (W1a) and pathfinding stops needing `--engine-void`. The case
  against stays as the playtest found it: the floor is invisible from every
  plated position, so a player gains nothing.
- **Keep the cave ascent as-is.** Nothing in the source argues against it.
  The 17-unit window at x 29508..29524 is a property of retail geometry and
  the climb56 frame data, and it is identical on both builds. The 2/11 does
  not measure what a player sees until the combat-mode and ghoul readings
  exist. The 2026-09-01 record of 5/5 on stock bindings stands.

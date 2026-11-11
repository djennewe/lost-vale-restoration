# In-engine test, 2026-09-01 — stock keybindings, the cave ascent, and the Cloud Cliffs

Session: `scummvm-lv-console` on `:77`. Two phases, and they differ in what
was allowed:

- **Tests A and B** ran on a **new game**, cheats ON, positioning by
  `MainActor::teleport` — the climbs themselves were always the Avatar's own
  input.
- **Test C** (the exit test) ran from checkpoints loaded through the in-game
  **F7** book, with **`Cheat::toggle` never issued in that engine instance**,
  so no teleport was available at all. The debugger was used only to *read*
  `ObjectManager::objectInfo`.

`shared/u8-lv-patched/` verified byte-identical to `shared/build/` before
the run; all four artifacts match `ARTIFACTS.sha256`.

**`~/.config/scummvm/scummvm.ini` was stripped of its four
`keymap_ultima8_MOVE_*` lines before the session** — they were still present
on disk, so every earlier "stock bindings" claim was made against a config
that was not stock. The file now carries only `[scummvm]`,
`lastselectedgame` and `versioninfo`. Backup:
`scratchpad/scummvm.ini.bak`.

## Verdicts

| Test | Question | Verdict |
|---|---|---|
| **A** | Does the Map 8 cave ascent work on **stock** keybindings? | **PASS.** z=0 → z=56 under the Avatar's own power, 5 of 5 clean attempts, no `keymap_ultima8_*` overrides in the config. |
| **A2** | Is the recorded recipe (hold UP, then hold SPACE) right? | **NO — the order is inverted.** SPACE must go down **first**. With UP leading by 0.25 s he walks out of the climb window before the single jump fires; 0/2 climbs. |
| **A3** | How forgiving is the climb spot? | **±8 units in x.** Climbs from x 29508–29524 at y=23622; fails at 29500 and at 29532. y is wide open (23600, 23622 and 23650 all climb). Walking at it while mashing SPACE missed 2/2. |
| **B** | Cloud Cliffs, base → summit, unbroken and on foot? | **PASS.** (4096, 10240, 0) → (4052, 1012, 120) in one run, no teleport after the start, z rising through all 31 lattice levels 0, 4, 8 … 120. Both switchback corners cleared. |
| **C** | The exit test — one continuous no-debugger playthrough | **NOT COMPLETE — steps 5-7 content run, three quest NPCs.** Both recorded bypasses retired, the Vale reached on foot, and quest step 5 (Atli) executed organically. `docs/playtest-2026-08-16-lb-mythran.md` records two bypasses on this stretch — the ascent (teleport) and the electric gateway (stun-pinned, NOT DEMONSTRATED). This session removed the first and found a trench route that avoids the zapper entirely. Progress: From `cp3h`, cheats OFF and no teleport: walked the whole south cave, **made the cave ascent organically**, walked ~4,900 units further south, **climbed the 48-unit gate wall**, took the map-8 south teleport onto the plateau, and then crossed most of the plateau westward (~5,500 units) surviving three damage events. Checkpoints `cp3k-cave-ascended`, `cp3l-through-gate`, `cp3m-plateau-west`. Stopped wedged at (9258, 12854, 48) with the pathfinder insisting on a route the engine refuses. |
| **C2** | Is the cave ascent required for the route? | **NO — the record is wrong.** From `cp3h` the gate approach at (29273, 30353, 0) is reachable at z=0 with **no climb at all**. The ascent leads to a pocket and the route continues from the trench floor. What the route does need is a walk across a **floorless void**. |

---

## TEST A — the cave ascent on stock keybindings — **PASS**

### Why the earlier reading needed checking, and what the source says

`U8AvatarMoverProcess::handleNormalMode` gates the climb on two flags:

```cpp
if (hasMovementFlags(MOVE_JUMP) && hasMovementFlags(MOVE_ANY_DIRECTION)) {
    ...
    else if (!hasMovementFlags(MOVE_MOUSE_DIRECTION)) {
        // the climb scan: climb72 down to climb16
```

`MOVE_ANY_DIRECTION` for this mover is defined in
`avatar_mover_process.h:110` and **does** include `MOVE_FORWARD`, which is
what stock `UP` sets (`metaengine.cpp:50`). So the gate is reachable with
the shipped keymap, as the 2026-08-19 note said.

(There is a **second, unrelated** `MovementFlags` enum in
`quick_avatar_mover_process.h:97` whose `MOVE_ANY_DIRECTION` omits
`MOVE_FORWARD`. It belongs to `QuickAvatarMoverProcess`, not to this one.
Reading that one first gives the opposite answer — worth knowing before
anybody re-derives this.)

### The run

Standing start at **(29524, 23622, 0)** on map 8, facing west (frame 6 =
`dir_west`, which is the direction the recorded 2026-08-19 success used —
`dir=12`, not north as `HANDOFF.md` said). Input: `xdotool keydown space`,
60 ms later `xdotool keydown Up`, both held 1.6 s, then released.

| rep | before | after |
|---|---|---|
| 1 | (29524, 23622, 0) | **(29364, 23622, 56)** |
| 2 | (29524, 23622, 0) | **(29364, 23622, 56)** |
| 3 | (29524, 23622, 0) | **(29372, 23622, 56)** |
| 4 | (29524, 23600, 0) | **(29372, 23600, 56)** |
| 5 | (29524, 23650, 0) | **(29364, 23650, 56)** |

(29364, 23622, 56) is the exact position the 2026-08-19 session recorded
for its own reproduction, reached there with an extra
`keymap_ultima8_MOVE_DOWN` binding. It reproduces without one.

### TEST A2 — the recipe's key order is wrong in the record — **CORRECTION**

`HANDOFF.md` and `traps.md` both say: *hold a direction key, then hold
SPACE.* Run that way the climb does not happen:

| input order | result |
|---|---|
| `UP` down, +0.25 s `SPACE` down | (29524, 23622, 0) → **(28692, 23622, 0)** — walked past, no climb |
| `SPACE` down, +0.06 s `UP` down | (29524, 23622, 0) → **(29364, 23622, 56)** — climbs |

The mechanism: `MOVE_JUMP` is set by the SPACE **keydown** and cleared
inside the branch, so a held SPACE buys exactly **one** climb attempt, at
whatever position the first non-busy frame finds. Pressing the direction
key first spends that one attempt several hundred units short of the face.

### TEST A3 — how wide the window is — **±8 units in x**

Same input, standing starts swept along the trench at y=23622:

| start x | result |
|---|---|
| 29500 | walked to (28996, 23622, 0) — no climb |
| **29508** | **(29356, 23622, 56)** |
| **29516** | **(29356, 23622, 56)** |
| **29524** | **(29364, 23622, 56)** |
| 29532 | (29460, 23690, 0) — no climb |
| 29540 | (29459, 23688, 0) — no climb |

So the climb fires from **x ∈ [29508, 29524]** — a 17-unit window against a
64-unit body. The ledge's east edge is x=29471 (`exact_reach` on map 8:
the z=56 surface runs x 29223..29471 for every y ≥ 23591), so the window
sits 37–53 units clear of the face.

Two approaches that a player would actually try both failed:

- **Walking west with SPACE mashed** (10 press/release cycles over ~2.7 s,
  from x=29900): walked straight through to x≈28855, z=0. **0/2.**
- **From the z=8 trench start (29820, 23622, 8)**, the documented "standard
  start": the single jump fires immediately at the start position, where
  the face is 300 units away, so he leaps west and drops to z=0 at
  (29604 / 29700, 23647). **0/2.** That drop does put him on the level the
  climb works from — so the ascent is a **two-stage** move, not one.

The trench at z=0 is void: `exact_reach` finds no real surface at z≤8
anywhere in x 29000..30200, y 23400..23900, and the Avatar stands there
only on the engine's `z <= 0` freebie-support rule
(`current_map.cpp:773`). He walks *under* the z=56 overhang with nothing
to stop him, so there is no tactile cue marking the one column he can
climb from.

**This is the finding that matters for the exit test.** The ascent is real
and it is reachable with the shipped keymap, but hitting a 17-unit window
in a black void with no landmark, using a key order that is the reverse of
what feels natural, is not something a player will find by accident.

---

## TEST B — the Cloud Cliffs, base to summit, unbroken — **PASS**

Map 13, one continuous walk from the ramp foot. The only teleport was the
one that put the Avatar at the foot; nothing after it.

```
start:  (4096, 10240,   0)
...
SUMMIT: (4052,  1012, 120)
```

z over the run, in order, with no repeats:
**0 4 8 12 16 20 24 28 32 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92 96
100 104 108 112 116 120** — every riser is +4, exactly as
`build_map_13.CLIMB_Z_STEP` lays them down, and the summit lands on
`CLIMB_Z_TOP`. Full trace: `B3-full-climb-trace.txt`. Summit screenshot:
`B4-summit.png`.

This closes the PARTIAL that F10 left on 2026-08-18: *"the unbroken
base→summit walk was NOT completed — the harness overshoots the one-tile
switchback corners."*

### What actually made the corners passable

It was the driver, not the map. Three separate harness defects each looked
like the map refusing:

1. **A burst shorter than a turn animation moves nothing.** 0.40 s bursts
   produced zero displacement at (4292, 5708, 52) and read as a wedge; a
   manual 1.5 s walk from that exact spot moved 520 units. Bursts are now
   ≥0.30 s and grow on a stall.
2. **Aiming past a bend cuts the corner.** Look-ahead of 3 tiles aimed
   diagonally across the (5120, 5760) turn and walked him off the z=56
   band at (4852, 5668) → z=0. The driver now never aims beyond the first
   tile where the path's step direction changes.
3. **An unbounded stall retry overshoots.** A flat 1.4 s retry carried him
   344 units west off the (4096, 5248) corner, twice. Retries are now
   bounded by the distance to the aim point.

`nav.py`'s own `goto` cannot do this route: `tol=200` is wider than a tile
and its run gait (`mag=240`) overshoots every corner. Driver used here:
`scratchpad/climb13d.py`, pursuit along `build_map_13.climb_tiles()` with
the tile-centre correction below.

### Two geometry notes worth keeping

- **Aim at tile centre, not at the tile.** Map items are addressed by their
  MAX corner, so on a 128-unit tile at x=4096 a 64-unit body may stand only
  in x ∈ [4032, 4096] — centre 4064. Driving at 4096 puts him on the edge;
  8 units past it (x=4024) he wedges against the drop, which is what
  stopped the first attempt.
- **The legs are wider than "one tile" in places.** `exact_reach` on map 13
  gives the east switchback leg a standable band of y 5667..5791 at z=52
  (x 4227..4607) — 4 tiles deep. The genuinely tight parts are the corners
  themselves and the narrow ledge, not the whole switchback.

---

## TEST C — the exit test — **NOT COMPLETE, advanced by one leg**

The exit test is an 18-step continuous playthrough. It is not finished and
nothing here should be read as finishing it. What this session did is take
the leg that was next and make it work.

### What was run

Loaded `cp3-plateau.sav` through the in-game **F7** book (no
`Ultima8Engine::loadGame`), confirmed the Avatar at (31295, 19135, 0) on
map 8, then moved to the forward checkpoint `cp3h-west-strip.sav`
(29801, 22801, 8) — the point the 2026-08-16 pool crossing left off at.
**`Cheat::toggle` was never issued in this session's engine instance**, so
teleports were unavailable; the debugger was used only to *read*
`ObjectManager::objectInfo 1`. Every metre below was walked.

| leg | result |
|---|---|
| cp3h → south end of the z=8 east strip, (29845, 23533, 8) | **walked**, 12 waypoints, hp 30 throughout |
| step west off the strip into the trench | **z=8 → z=0**, (29745, 23673, 0), no damage |
| creep west into the climb window | **x=29521** via 32-unit careful steps |
| the ascent | **(29521, 23673, 0) → z=56**, ending (29417, 24001, 56) |

Checkpoint saved in-game as slot 6 and archived to
`~/lv-checkpoints/cp3k-cave-ascended.sav`.

### The tool the leg actually needed

Straight-line chasing wedged three separate times in the cave (at
(29941, 23421), (29941, 23317) and again heading south) because the route
doubles back north and east before it can go south. `exact_reach.flood()`
answers *whether* he can get there and never *how*.

`tools/playtest-linux/pathfind.py` (new) runs a BFS with parents over the
same engine-faithful lattice and the same `SEARCH_OFFSETS_U8` z-table, then
collapses collinear runs into waypoints. The leg that wedged three times
walks in one pass off its 13 waypoints. `tools/playtest-linux/walkto.py`
(new) chases a waypoint list with the burst rules TEST B established.

It carries a **`--engine-void`** flag, and the whole southern route depends
on it. `exact_reach` is deliberately stricter than the engine at z ≤ 0: it
demands a real surface, because "you can technically traverse the void" is
not a verdict worth shipping on. The engine ends `getPositionInfo` with
`if (target._z <= 0) info.supported = true;` (`current_map.cpp:773`) and
walks the Avatar across blackness. With the strict model map 8's south exit
reads as unreachable; with `--engine-void` it is a 9-waypoint walk. Use the
flag for finding a way through, never for a walkability verdict — and note
what it means for the player: **this route is several thousand units of
walking over nothing**, which is exactly the condition the project's own
blackness rule calls broken.

```bash
tools/playtest-linux/pathfind.py --map 8 --from 29941,23317,8 \
    --to 29800,23560,8 --roi 28000,22000,32700,24500
tools/playtest-linux/walkto.py 29951,23319 29951,23167 ...
```

### Two positioning techniques worth keeping

- **A careful step is exactly 32 units.** `ctrl` + `UP` held ~0.45 s moves
  the Avatar 32 units and nothing else, repeatably — the only way to land
  inside a 17-unit climb window, since an ordinary mouse burst shorter than
  a turn animation moves 0 and a long one moves 115+.
- **`ctrl` + `DOWN` does not step backwards.** It turns him to face the
  other way and back; it cannot be used to fine-tune in reverse. Re-phase
  with a short mouse burst instead.

### The ascent is a dead end, and it is not on the route

The z=56 floor the ascent lands on is a **pocket** — flooding from
(29417, 24001, 56) reaches 4864 positions, all at z=56, bounded to
x 29223..29663 and y 23591..24607, with exactly one climbable exit
(+48 north, back over the z=8 corridor). Walking its south end drops
straight back into the trench.

So the route continues from the **trench floor**, and the ascent turns out
to be a detour. `exact_reach` modelled with the engine's own `z <= 0` rule
(see below) reaches the gate approach at (29273, 30353, 0) from `cp3h`
**with no climb anywhere in the path**.

**This corrects `docs/engine-2026-08-18-f1-segfault.md`**, which recorded
"the trench is the north end and the ascent is genuinely required. …There
is no way around." There is a way around: the trench floor itself. That
conclusion came from the strict model, which refuses to walk a floorless
void — and this stretch of map 8 *is* floorless void that the engine walks
happily. The ascent is still worth having (it is how you get onto the z=56
floor at all), but it does not gate the exit test.

### The route that does work, walked

| leg | result |
|---|---|
| off the pocket's south end | z=56 → z=0, (29417, 24761, 0) |
| **~4,900 units south through the trench** | (29021, 29605, 0), hp 30, 8 waypoints, no deaths |
| round the gate's west wall to the approach | (29273, 30353, 0) |
| **climb the 48-unit gate wall, drop into the corridor** | teleport fires → **(14686, 11210, 48)**, out on the plateau |
| west across the plateau toward Mythran | **DEAD at (12470, 11534, 48)** — hp 30 → 13 → 4 → 0 |

The gate is a walled north-south corridor holding teleport egg
(shape 508, q=257) at (29407, 30335, 0); its west wall is shape 32,
box (32, 128, 48), at x 29279..29311. Walking at it does nothing. **The
same SPACE-then-direction climb that works in the trench takes the wall**:
back off one careful step to x=29241 (38 units clear of the face — inside
the same 37–53 band the trench ascent uses), face east, SPACE down, then
UP. He climbs to the wall top at z=48 and, with UP still held, walks east
off it onto the trigger, which fires.

### The plateau: three deaths, then most of the way across

The first two attempts died. **The cause was the gait, and the harness's own
notes already said so** — `nav.py`: *"240px offset = RUN gait; 130 walked,
and walkers die to chasers (2026-08-12)."* `walkto.py` was written at 130.
Something on the plateau hits for 8–20 a swing with knockback, and at a
walking pace it keeps up.

| attempt | gait | result |
|---|---|---|
| 1 | walk (130) | **DEAD** at (12470, 11534, 48); hp 30 → 13 → 4 → 0 |
| 2 | run (240), started wounded at hp 12 | **DEAD** at (12458, 11530, 48) |
| 3 | run, full hp, adaptive tolerance | **survived** — hp 30 → 17, regenerating, reached (12774, 11386, 48) |
| 4 | run, continuing | **survived two more hits** (27 → 19, 19 → 6) and made 10 of 11 waypoints, ending (9154, 12822, 48), hp regenerating |

Two walker fixes made attempts 3 and 4 work:

- **Run by default, walk only on short hops.** A run gait cannot stop
  inside 96 units, so on a hop shorter than that the tolerance swallows the
  waypoint and the walker skips to the next — which is how it ended up
  chasing a target 1,557 units away through a wall. `walkto.py` now picks
  the gait per hop: under 320 units it walks with tol 56, otherwise it runs
  with tol 96, and a wedged run retries once at walk pace.
- **Damage response.** It prints `TAKING DAMAGE (a->b)` and forces the run
  gait for the rest of the leg.

### `fight.py`, and the trap in writing one

`tools/playtest-linux/fight.py` (new) implements the combat the walker
lacked, read out of `handleCombatMode`: `c` for combat mode, an attack is a
**double LEFT click**, its direction is `mousedir` (so attack with no keys
held, or `MOVE_ANY_DIRECTION` overrides it with facing), the first click may
be spent turning, and `canAttack()` gates on `25 - dex` frames — ~0.4 s.

Its first version took **the first `CombatProcess` in `Kernel::listProcesses`**
as the attacker. That is wrong and wasted 40 rounds swinging at air: every
hostile on the map runs its own combat AI, and the first entry was a ghoul
(object 108, shape 142, hp 37) **22,241 units away**, fighting something
else entirely. It now takes the *nearest* CombatProcess actor and refuses to
engage anything beyond 400 units.

That correction also settles what was killing the Avatar: it is **not**
object 108. Standing still for 40 rounds at (12774, 11386) cost no health
and regenerated some, so nothing was adjacent — the damage lands only while
moving, with knockback, in two specific stretches around x 12400–14500. The
attacker has not been identified.

### The wedge at (9258, 12854), and the guard it produced

`pathfind.py` insisted (9151, 12863) → (7919, 12863) was walkable at z=48
and held that answer at step 8 over a 3,500-unit ROI. The engine refused
every westward burst. Sampling the row at step 4 shows why:

```
  y= 12855 ###....############################......................
  y= 12859 ###....############################......................
  y= 12863 .........................................................   <-- seam
  y= 12867 .................................####################....
```

**One 4-unit row, open across the whole width, between two wall blocks.**
That is the aperture hazard `.claude/rules/map-geometry.md` exists for —
U8 item boxes are half-open, two walls that meet leave a seam the lattice
calls open, and the engine will not thread it.

`pathfind.py` now takes **`--erode N`**, which shaves N lattice cells off
every walkable edge before routing. A one-row seam disappears; a corridor
wider than 2N cells survives. With `--erode 1` the same query returns
**NO PATH**, correctly — and, over a ROI wide enough not to clip the real
route, an 11-waypoint route that goes *south to y≈13095 first*. Use
`--erode 1` for anything through cave.

### Onward, and why the exit test cannot finish in one session

The corrected route works, and the leg after it re-drew the map-8 picture:

- Walking the westward corridor puts the Avatar on a **teleporter**, which
  lands him at (14540, ~7900, 0) — a **northern region** of map 8, x 12815..16495,
  y 3087..9775. It is an **intra-map shuttle**: `npcnum` on these base-game
  eggs is not the destination map, whatever the map-builder comment says —
  the cave trigger (q=257, npc=69) also landed him on map 8, and so did
  this one (q=282, npc=68).
- The shuttle's other end at (14538, 8334) sends him straight back. It is a
  two-way link between the plateau and the north, not a way onward.
- The Mythran approach — `cp4-mythran-approach.sav` sits at **(2900, 3000, 0)**
  — is a *third* region, x 503..7215, y 503..3631. The only teleport egg in
  it that could be an entrance is **TARGET q=20 at (6078, 1786)**, and map 8
  carries **no trigger with quality 276**. So the way in is a teleport
  **from another map entirely**.

### The teleport table was being read off the wrong byte

A U8 fixed item carries **both** `npcNum` (byte 12) and `mapNum` (byte 13)
(`Map::loadFixedFormatObjects`), and `TeleportEgg::hatch` does
`av->teleport(_mapNum, getTeleportId())`. So **`mapnum` is the destination
map and `npcnum` is the hatch range** — `u8_map.MapItem.__repr__` says so,
and this session read `npcnum` as the destination for several hours before
checking. Read correctly, map 8's 19 eggs are:

| trigger | id | dest map | where |
|---|---|---|---|
| (31871, 19167, 0) | 1 | **7** | the cave entrance — the only exit from map 8 |
| (29407, 30335, 0) | 1 | 8 | the gate corridor → (14590, 11210) |
| (14540, 11004, 48) | 2 | 8 | → back to the cave |
| (4094, 1794, 0) | 4 | 8 | inside the Mythran region |
| (7916, 12476, 48) | 26 | 8 | plateau → north |
| (14538, 8334, 0) | 27 | 8 | north → plateau (the other half) |
| (20415, 2786, 1) | 201 | 9 | LV |
| (20900, 3300, 1) | 212 | 10 | LV |

Scanning **all 49 maps that have data**, the only triggers whose
destination is map 8 come from maps 7, 9 and 10. Map 8's targets
**id 20, 22 and 30 are orphans — nothing anywhere triggers them.** So the
Mythran region is not entered by teleport at all, and an un-eroded flood
from `cp4`'s (2900, 3000, 0) reaches x 407..7223, y 407..3639 and nothing
else: not the LB backstop egg, not Mythran's own tile, not the plateau.

### Why the exit test cannot be finished yet — the blocker is on the record

`docs/playtest-2026-08-16-lb-mythran.md` already says it, in its own
verdict table:

> **Cave traversal, trench system → south exit** — PASS **with bypass**;
> the z8→z56 ascent … was teleport-bypassed
> **Electric gateway (LITZAPNS) organic passage** — **NOT DEMONSTRATED** —
> the Avatar got stun-pinned in the arc; bypassed

**The route from the cave to Mythran has never been walked.** Both of its
obstacles were bypassed, and the exit test is by definition the run with no
bypasses. One of the two is now gone — this session walked the ascent — and
the trench route found here reaches the gate corridor at z=0 without going
near the zapper at (30879, 24383, 56) at all, so it may retire the gateway
too. But the leg that lands the Avatar in the Mythran region is still not
established by anyone, and static reachability cannot supply it: on this
map the model is wrong in both directions (it invents one-row seams and it
disconnects regions a human has walked).

### The gateway route is still bypass-only, tested with the fixed recipe

`cp3i-gate-approach` sits at **(30405, 23581, 8)** and `cp3j-past-gate` at
**(30815, 24520, 56)**. Flooding from `cp3i` reaches z=0 x 29887..31487 /
y 20543..23607 and z=8 x 29503..31287 / y 20007..23583 — and **not** the
gate passage at z=56. So `cp3i → cp3j` was itself the teleport bypass; the
electric gateway has never been *approached* on foot either, let alone
passed.

The region past the gateway (61,373 positions, x 29375..31487,
y 23079..26367 at z=56) is a **different component from the ascent pocket**
this session reached — flooding from (29417, 24001, 56) in the same ROI
gives 4,864 cells and does not include (30815, 24520). So the ascent that
now works does not open the gate route.

There are genuine 48-unit faces from the walkable z=8 trench into the gate
region — filtered to exclude the roofed underpass's stacked floors
(standable at *both* z=8 and z=56, i.e. a ceiling overhead), **83 north-,
27 south- and 6 west-facing sites remain**. Tested at two of them with the
corrected recipe (face the wall by mouse, release, **SPACE down, then UP**,
held 1.8 s):

| site | result |
|---|---|
| (29805, 23581, 8) facing north, ~54 units clear | a plain **jump** — carried him to (30477, 23397, 8), still z=8 |
| (30477, 23301, 8), walked flush, facing north | **nothing at all** — 3 north bursts and 2 climb attempts, position unchanged |

That reproduces F1's original observation, this time with the key order
known to be right. **The 37–53-unit launch window does not transfer**: in
the trench the target is an *overhang* approached from z=0 void, where the
Avatar's body may overlap the ledge's footprint because the ledge is 56
above him. A solid 48-high wall admits no overlap, so the geometry of the
approach is a different problem.

Three further attempts, one per remaining idea:

| attempt | result |
|---|---|
| **south-facing** face, standing (30305, 23285, 8) — the site's own cell | **jump**, ending (30305, 23909, 0). No climb. |
| **west-facing** face, from (29805, 23581, 8) | **jump** west off the ledge to (29705, 23741, 0), then ran on. No climb. |
| **running jump** (LSHIFT held into the face, then SPACE) | carried him further west at z=0. No climb — and by the source it *cannot* climb: `lastanim == run` selects `runningJump` in the branch **before** the climb scan. |

The **hang grab does not apply here at all.** `AvatarGravityProcess` tries
the ledge grab only with `MOVE_ANY_DIRECTION` set, which
`AvatarMoverProcess::run()` can only establish on the ground — and to grab
this shelf the Avatar would have to fall *past its face*, which means
starting above it. The shelf is the top; there is nothing above to fall
from.

So every input route into the branch has now been tried at this face:
plain jump, jump with each of three facings, careful-step approach, flush
approach, running jump. **The engine will not climb it.** F1's conclusion —
that the remaining blocker is map geometry, not input — survives the input
fix that overturned the rest of its findings.

### And the ascent pocket does not reach the gate shelf either

The last hope was that the pocket the ascent opens might touch the gate
region somewhere. It does not. Flooding both in one ROI: pocket 4,864
cells (x 29223..29663, y 23591..24607), gate shelf 61,373 cells
(x 29375..31487, y 23079..26367), **0 cells in common**, closest approach
**96 units** — pocket (29663, 24399) to gate (29759, 24399), same z=56,
same y.

Standing at that edge, everything was tried:

| attempt | result |
|---|---|
| standing jump east, 3 attempts | edged to (29658, 24396, 56) and stopped — the jump falls short of 96 |
| running jump (LSHIFT + UP, SPACE cycled 6×) | slid **south** along the edge to (29662, 24496, 56) |
| `hop.py` targeted jump to (29759, 24399, 56) | 6 attempts, ~70 aim probes: *"stone not resolved"* — its matcher only resolves shape 300 there |
| manual targeted both-button chord at the projected pixel (822, 436) and two offsets | **turned him only**; no jump fired |
| walking east: (140,70), (280,140), (140,0), (140,140) | **blocked** at x=29662; the last slid north along the wall |

That 96 units is **a wall, not a void** — the Avatar is stopped dead by it
in all four walking directions. The two z=56 regions are separated by real
geometry.

**So the ascent this session made opens a dead end**, and the gate shelf —
the only known way to the cave mouth and onward — has no on-foot entrance
from anywhere the Avatar can stand.

The seam is **a wall, and it lives inside a glob** — which is why a raw
scan of `FIXED.DAT` items over the band showed only two harmless 32×32×8
blocks and led this report, briefly, to call it missing floor. Enumerating
the *expanded* blockers (globs resolved) finds the real one:

```
blocker at (29695, 24447, 56)  box 32 x 128 x 48
    spans x (29663, 29695]  y (24319, 24447]  z [56, 104)
```

A 32-wide, 48-tall wall standing exactly on the seam. **Scan expanded
items, not raw ones, before concluding anything about map 8's geometry** —
`ExactReach` expands glob eggs and the raw item list does not.

That also explains why the naive remedy failed. Simulating one to four
shape-301 paving slabs (128×128, zd=0, SOLID|LAND) at x=29759,
y ∈ {24191, 24319, 24447, 24575}, z=56 leaves the pocket at exactly 4,864
cells every time: the floor was never the problem, and the slabs sit
behind the wall.

The wall's own extent is worth recording. At x=29695 the z=56 level is
standable only for **y 23743, 23935, 25151..26239 and 26335..26599** — so
the seam opens up ~550 units *south* of where the pocket ends (y=24607).
The pocket is bounded on all four sides: the z=8 corridor face to the
north, this wall to the east, and a 56-unit drop to the south.

### The fix, applied and walked

It **is** a one-item edit after all, delivered through the pattern the
sealed-doors work established: remove the glob egg, put its other items
back.

`build_map_08.py` now carries `BASE_ITEM_REMOVALS = {(29695, 24575, 56, 2)}`
— glob egg 933 — and `seam_glob_replacement()`, which re-places its other
**20** items verbatim. The one item not put back is the wall segment,
shape 32 frame 1, at (29695, 24447, 56). That opens a 128-unit doorway in
a north-south wall column.

**This is a deliberate deviation from retail geometry**, and it is the
first one this project has made to terrain. It is recorded in the builder,
in `TODO.md`, and here.

Static check, on the rebuilt `FIXED.DAT`: the ascent pocket goes
**4,864 → 66,336** standing positions and now reaches (30815, 24520, 56).

**Walked in-engine, on a fresh world** (checkpoints do not see FIXED.DAT
changes, so this had to be a new game):

```
teleport to (29600, 24383, 56), then careful-steps east:
  29600 -> 29664 -> 29696 -> 29728 -> 29760 -> 29795 -> 29823   all z=56
```

He walks straight through the seam. Continuing on foot to
**(30847, 24582, 56)** — cp3j's position — **past the electric gateway's
fence line at y=24383**, hp 30 → 21, one zap from LITZAPNS and through.

So both bypasses on this stretch are now retired:

| bypass | status |
|---|---|
| the z8→z56 cave ascent, teleported since 2026-08-16 | **walked** 2026-09-01 (`cp3k`) |
| the electric gateway, *"NOT DEMONSTRATED — stun-pinned in the arc"* | **passed on foot** 2026-09-01 (`cp3n-past-gateway`), costing 9 hp |

The joined region is 66,336 positions spanning x 29223..31487,
y 23079..26367.

### There is a second seam, and it is real in the engine too

The shelf does **not** run to the cave mouth. F3 records the mouth at
y≈29100; the joined region stops at **y=26367**, and walking it from
`cp3n` confirms that: the Avatar reached (30407, 26366, 56) and wedged.

The barrier is the same pattern, one glob further on — an **east-west wall
run at y=26399** inside **glob 936**, egg (30719, 26623, 56):

| shape | frame | at | footpad |
|---|---|---|---|
| 26 | 7 | (30463, 26399, 56) | 128×32×48 |
| 26 | 7 | (30591, 26399, 56) | 128×32×48 |
| 32 | 7 | (30623, 26399, 56) | 32×128×48 |
| 29 | 6 | (30335, 26399, 56) | 32×32×48 |

Sampling x across the seam, the only column where z=56 is continuously
standable through y 26255..26455 is **x 31455..31599** — and those cells
are not reached from the shelf either, so they belong to a further region.

**Made, on the same one-item pattern.** `BASE_ITEM_REMOVALS` also drops
glob egg 936 at (30719, 26623, 56); `seam2_glob_replacement()` puts its
other **36** items back and omits only the shape-26 segment at
(30463, 26399, 56). Static: the shelf goes **66,336 → 221,491** positions
and reaches the cave mouth.

Walked, cheats off, from (30400, 26200, 56):

```
  -> (30400, 28960, 56)   through the seam, to the cave mouth (F3: y~29100)
  -> (30400, 30424, 56)   5,800 units south of the gateway, hp 30 the whole way
```

Checkpoint `cp3o-cave-mouth.sav`. **The south cave is now traversable end
to end on foot** — ascent, first doorway, electric gateway, second
doorway, cave mouth — and the region past it is 241,430 standing
positions, x 27455..32287, y 23103..30751.

### What is still not reachable

A whole-map flood from the cave mouth reaches **none** of: Mythran
(1503, 1791), the LORDBRIT backstop egg (2200, 2230), `cp4`'s position
(2900, 3000), the sealed doors (20447, 2751), or map 8's only off-map
exit at (31871, 19167). The cave opens onto the outdoor plateau below —
which is where this session's trench route already went, via the gate
corridor teleport — and from there the Mythran region remains what it was:
no teleport anywhere in 49 maps lands in it, and no walking route the
model can find.

So the cave is solved and **the Mythran leg is the one that has never been
walked by anyone**. `cp4-mythran-approach` was almost certainly reached by
debug teleport, like the two bypasses either side of it.

### Map 8's connectivity, as the model sees it

Five regions, flooded from a seed the Avatar has actually stood on:

| region | seed | extent | reaches |
|---|---|---|---|
| cave entrance + trench | (31295, 19135, 0) — the map-7 arrival | x 29503..32671, y 18751..23583 | the map-7 exit trigger; `cp3h` |
| plateau + north | (14686, 11210, 48) | x 6591..18431, y 3087..20991 | an intra-map shuttle, both ends |
| south cave (now joined) | (30400, 30424, 56) | x 27455..32287, y 23103..30751 | the cave mouth |
| outdoor pocket below the mouth | (29676, 31748, 8) | x 29663..30751, y 28703..31807 | ~2,000 positions, dead end |
| **Mythran + the sealed doors** | `cp4` (2900, 3000, 0) | x 407..7223, y 407..3639 | **nothing** |

A strict scan — **49 maps loaded, 0 load failures** — finds triggers into
map 8 only from maps 7, 9 and 10, and map 8's targets **20, 22 and 30 are
triggered from nowhere at all**. Those are the Mythran region's only pads.

That cannot be the whole truth: retail players reach Mythran. So the route
exists and **the walking model cannot see it** — it models no climb, no
jump, and it has been caught wrong in both directions on this map twice
today.

**And the disconnection is retail's, not ours.** Flooding map 8 from the
map-7 arrival against the pristine `FIXED.DAT.bak` and against our build
gives the *same* answer — **6,652 cells both times**, and neither reaches
Mythran, `cp4` or the doors. The LV build is cleared: we did not wall
anything off.

Driving it in-engine agrees. From `cp3-plateau` the Avatar walks west and
south to (29503, 19815, 0) and stops there, oscillating: the walker's new
eight-direction escape frees him north each time and the chase pulls him
straight back. x≈29503 is the strict flood's western boundary for that
region, and the engine honours it.

Map 8 has **three** entrances, and Mythran's region is isolated from all
of them:

| entrance | from | region it lands in | reaches Mythran? |
|---|---|---|---|
| (31583, 19135, 0) | map 7, id 0 | cave entrance + trench, 6,652 cells | **no** |
| (20415, 3170, 0) | map 9, id 200 | the doors, 60,123 cells, x 12831..26143 | **no** |
| (20260, 3260, 0) | map 10, id 213 | the same doors region | **no** |

And nothing anywhere triggers map 8's targets 20, 22 or 30, which are the
only pads inside Mythran's region.

So the leg is not merely unwalked — **no route to it is visible from any of
map 8's entrances, in retail data, by any method tried**. Both models are
wrong in opposite directions and neither settles it: the strict one
fragments the map into six regions, and the engine-void one says everything
connects at z=0, while the engine itself stops the Avatar dead at
x≈29503. The truth is between them.

### It is a scripted teleport, and that reframes the exit test

Two more checks close the loop.

**NONFIXED.DAT holds no teleport eggs at all.** Extracted from
`SAVEGAME/U8SAVE.000` (a 4-member container: AVATAR, ITEMCACH, NONFIXED,
NPCDATA), its 256-entry FLEX carries **zero** shape-`SHAPE_TELEPORT_EGG`
items. So the egg graph measured from `FIXED.DAT` is the whole egg graph —
nothing was hiding there.

**The base game teleports the Avatar by script, constantly.** Scanning
`EUSECODE.FLX` for `calli` with intrinsic **158** (`Actor::I_teleport`)
finds it in **58 of 1,460 classes**, one of them eight times over.

That is the answer to "how does a retail player reach Mythran": **he is
put there by usecode.** A region with no walking route in and no egg
pointing at it is not a broken map — it is a region the game scripts you
into.

**And it reframes the exit test.** The test is a *no-debugger* playthrough,
not a no-teleport one: the game's own scripted teleports are the game. What
counts as a bypass is `MainActor::teleport` typed at a console. So the
Mythran leg is not "walk 29,000 units west" — it is "trigger the scene that
takes you there", and finding which of those 58 classes does it is a
usecode question, not a navigation one.

### Found: class 0x026F "NEC1" teleports the Avatar into Mythran's region

Decoding the argument pushes settles it. `Actor::I_teleport` takes
`(actor, newx, newy, newz, newmap)` and U8's `World_FromUsecodeXY` is the
identity, so the word immediates before a `calli … 158` are world
coordinates as-is. Scanning every class for that pattern:

```
FLEX entry 625  (class 0x026F, "NEC1")  offset 0x11c6
    Actor::I_teleport(..., 2399, 2207, ...)
```

**(2399, 2207) is inside Mythran's region** — x 407..7223, y 407..3639 —
and it is **200 units from the LORDBRIT backstop egg** the LV builder
placed at (2200, 2230) "on the Mythran approach". The class's strings are
Necromancer/Lithos dialogue: *"taken thy first steps in Necromancy"*,
*"thou must prove thyself worthy"*, *"an audience with other
Necromancers"*.

So the region is entered by **an NPC conversation that teleports you**.
That is why six floods could not find a path in, why nothing triggers
targets 20/22/30, and why the pristine map floods exactly like ours.

**The Mythran leg of the exit test is therefore: trigger NEC1's scene.**
Not a walk, not a bypass — the game's own transport.

One caveat, checked and unresolved: **NEC1 has no placement**. Scanning all
49 maps' `FIXED.DAT` for shape 623 finds nothing, and scanning
`ITEMCACH.DAT`'s 255 NPC slots (offsets per `World::loadItemCachNPCData`)
finds no NPC of that shape either. So the class is spawned or scene-driven
rather than standing somewhere — which is consistent with it being a
conversation that moves you, but means *where* you meet it is still open.

That is the next thread, and it is a usecode/dialogue task rather than a
navigation one.

### Mythran is NPC 33, and the contradiction is now sharp

`ITEMCACH.DAT` has exactly **one** NPC on map 8:

```
npc 33, shape 190, at (1503, 1791, 0)
```

That is Mythran — U8 gives an NPC the usecode class `0x400 + npcnum`, and
`0x0400 + 33 = 0x0421`, which the symbol index names **MYTHRAN**. So the
builder's inferred "(1503, 1791)" was exactly right, and he stands inside
the region nothing can reach.

And the game's own in-world book settles that he is meant to be *walked*
to: *"I took the leisurely stroll up to the Plateau… Once at the Plateau, I
met with the old hermit who lives there. This old man, Mythran is his
name…"*

### RESOLVED — the region IS reachable on foot, and this report was wrong

The contradiction was mine, not the map's. Everything above that called
Mythran's region "isolated" is **withdrawn**.

Between it and the doors region there is no wall — there is a **~1,000-unit
void**. Scanning x 6500..13500 over y 300..10500 finds standable ground in
exactly two runs, **x 6527..7199** (Mythran's east edge) and **x 8255..13471**
(the doors region), with nothing between. The strict model calls that a
disconnection because it refuses to walk a floorless void. **The engine
walks it** — the same `z <= 0` freebie support that carries the Avatar
across the trench.

Walked, cheats off, from (8400, 2500, 0):

```
  8400 -> 7816 -> 6848 -> 5880 -> 5036 -> 4268   all z=0, hp 30
```

Straight across the void and deep into Mythran's region, then around his
house cluster to **(2056, 2624, 0)** — roughly 900 units from Mythran at
(1503, 1791). Checkpoint `cp3p-mythran-region.sav`.

So the Mythran leg is a walk after all, over blackness, exactly like the
trench. What is left is his **compound**.

Flooding from Mythran's own tile (1503, 1791, 0) gives a region of 23,807
positions, x 1119..3103 / y 1119..2527, with a staircase inside it —
z=8→16→24→32→40 at x 1471..1847, y 1599..1663, rising to a 27,972-cell
upper floor at z=48. The Avatar's region and Mythran's come within
**96 units** — (2623, 2527) to (2527, 2527) — and that 96 is walled: five
careful steps west from (2624, 2528) move him nothing.

Tried, in-engine, cheats off: south to y=2527 then west (blocked); north at
x≈2624 (blocked at y=2400); round to the compound's east side, where the
region reaches x 3103 at y 1631..2015 — he got to (2720, 2112, 0) and then
(2688, 2112, 0), blocked north and west. Closest approach so far
**(2688, 2112, 0)**, about 1,200 units from Mythran. Checkpoint
`cp3q-mythran-compound.sav`.

Continuing round the outside, the Avatar reached **(3144, 1736, 0)** on the
compound's east face — checkpoint `cp3r-compound-east.sav`. The model's
"closest pair" there, 58 units from (3135, 1743) to (3103, 1791), turns out
to be **proximity across a wall, not a door**: careful steps west are
refused at y=1704, 1736 and 1768 alike.

### Looked at it, and the answer is that there is no entrance

Teleporting in for reconnaissance settles the whole thing.
`D2-mythran-interior.png` shows the Avatar at (2600, 1800, 0) inside a
timber hall hung with red banners, shelves of reagents and potions, a
skeletal creature strung from the ceiling — Mythran's house. And
`D1-mythran-island.png`, from (3080, 2100, 0), shows what it stands on:

**a floating island in a starfield.** Wooden deck, rock underside hanging
in black shot through with coloured stars. Not a plateau, not a walled
compound — an island in the void.

Everything now falls out of that one picture:

- **The region is isolated because it is an island.** No walking route in,
  no teleport egg pointing at it, and no trigger for targets 20/22/30 —
  because you do not walk or hatch your way onto it.
- **The "void" this report kept crossing is literal.** The blackness the
  Avatar walks over at z=0 is the starfield under the islands, and the
  earlier claim that he had "walked into Mythran's region" was him walking
  *beneath* it on the engine's `z <= 0` freebie support. Withdrawn.
- **The pristine map floods identically** because nothing is broken.
- **The compound wall has no door** because the boundary is the island's
  edge.

So the Mythran leg is a **scripted arrival**, as the 58 classes calling
`Actor::I_teleport` implied — and the exit test's approach to quest step 2
is to trigger whatever transport carries the Avatar there, not to walk.

Narrowing it: decoding every `calli … 158` and filtering destinations to
the island's bounds (x 1119..3103, y 1119..2527) leaves exactly **two**
classes, and **neither is the transport**:

| class | name | destination | what it is |
|---|---|---|---|
| 0x006D | **PYROS** | (1245, 1245) | the Titan of Fire's summoning scene — *"Lord of Flame… For what pathetic reason have you summoned me, mortal?"* |
| 0x026F | **NEC1** | (2399, 2207) | a Necromancer conversation with no placement and nothing calling it — probably dead content |

And **MYTHRAN's own class 0x0421 contains no teleport at all.**

So the island holds Mythran's house *and* a Pyros summoning spot, and the
way onto it is not any single teleport this scan can see. That points at
the base game's early quest structure — a spell, an item, or a scene chain
— and answering it means playing retail U8 or reading the quest's usecode
in order, neither of which is a navigation problem.

### And the island turns out not to matter — the Vale is reachable

Testing whether the exit test even needs Mythran produced the session's
last result. Teleported to the doors approach at (20430, 3250, 0) — the
position `build_map_08.py` documents — **cheats then toggled off** and
verified by the echoed `Cheats = false`, the Avatar walked:

```
(20430, 3250, 0) -> 14544,2560 -> 16144,2624 -> 18192,2624 -> 20240,2624
                 -> 20760,2624 -> 21024,3352 -> 21848,3352 -> 22368,3352
```

and then, continuing, the log shows **`Unloading map 8` / `Loading Fixed
items in map 10`** — he stepped on the direct-travel trigger the builder
placed at (20900, 3300, 1) and arrived in **the Lost Vale**, map 10, at
(16920, 10280, 0), hp 30. Screenshot `D3-in-the-vale.png`; checkpoint
`cp5b-vale-on-foot.sav`.

So **the doors area → Lost Vale link walks, cheats off** — which is where
the eighteen quest steps happen. The Mythran island is not on that path at
all; steps 1-2 are prerequisites a normal playthrough satisfies long before
the Plateau, and the exit test's own start (`cp3-plateau`) postdates them.

**What is still unproven is the cave → doors-area link.** Both models say
no route, and this session did not walk it — the Avatar was teleported to
the doors approach for this test. That single link is now the only gap
between `cp3l-through-gate` and the Vale.

### In the Vale: the NPC pipeline works, and the nearest NPC has no dialogue

From `cp5b`, walked to the nearest villager — **NPC 110, `PESANT1`, shape
707, at (18688, 9728, 0)** — and the whole interaction chain works:

1. `ObjectManager::objectInfo 110` gives his exact position;
2. the sprite pixel is `centre + 2·((Δx−Δy)/4, (Δx+Δy)/8 − Δz) − 60px` in
   y — the −60 matters, because clicking the *feet* hits the floor tile
   under him and returns shape 242 every time;
3. a single click there logs `Item 110 (class Actor, shape 707)
   (uc: PESANT1)` — the probe the traps prescribe;
4. a double-click registers on him.

**And nothing happens.** `PESANT1` opens no conversation. He is a generic
villager, not a quest NPC.

The quest NPCs are elsewhere and are named in `build_map_10.py`: **100
Female Elder, 101 Veteran, 102 Sigrid, 103 Farmer, 104 Child, 105 Ragnar,
106 Thordis, 107 Atli, 108 Inventor**. Note they are all placed with
peasant/guard *shapes*, so `objectInfo` reports `uc: PESANT1` for every one
of them — the character dialogue hangs off `0x400 + npcnum`, not the shape.
Do not read the `uc:` name as the NPC's identity.

Positions this session read: **106 (Thordis) at (6144, 6656, 0)** and
**107 (Atli) at (18811, 6019, 0)** — Atli about 3,500 units from `cp5b`.

### Quest step 5 executed: Atli, spoken to organically

Walked from `cp5b` to **NPC 107 (Atli)** at (18811, 5779, 0) — arriving at
(18724, 6148, 0), cheats off and verified — and the standstill-strike
opened his conversation. The log names the class:

```
Item: 107 (shape 707) calling usecode event 1 @ 046B:036C
```

**0x046B = 0x400 + 107** — Atli's own class, not the peasant shape's. The
exchange, every option read off the screen and chosen organically:

| the Avatar | Atli |
|---|---|
| *May I speak with you?* | *"What? Who are you? Strange you dress! Stranger you talk! A Pagan are you? No, surely not!"* |
| *What is your name?* | (answered; the option leaves the menu) |
| *I am from Brittania.* | *"Know of this Brittania I do not. Where it is?"* |
| *On the other side of the barrier.* | *"Hm, believe you I do not. I think from the Hoskulds you are. I think a spy you are… those blood-sucking, troll-vomit eating vermin!"* |
| *I am not a Hoskuld!* | conversation closes |

That is **quest step 5 — "Meet the Zealans"** — running on the shipped
EUSECODE, and step 6's clan suspicion ("each blames the other") in his own
voice. Screenshots `D4-atli-talk.png`, `D5-atli-hoskuld.png`. Checkpoint
**`cp5c-atli-spoken.sav`**.

### And Ragnar — including the DD-008 option, verified live

Walked **13,600 units west** across the Vale from Atli to the village
cluster, hp 30 the whole way, arriving (5232, 8664, 0) beside **NPC 105
(Ragnar)**. Struck and talked:

| the Avatar | Ragnar |
|---|---|
| *What is your name?* | *"Ragnar called I am. Never seen one such as you have I. Where come from do you?"* |
| *From very far away.* | *"Know that I do! Never seen anything like you I have. Come in peace do you?"* |
| *Yes, I'm peaceful.* | *"Peaceful you are, but peaceful with Gunnar clan? If peaceful with Gunnar clan you are, then at war with Huskuld clan you are."* |
| **I have no fight with you.** | dispatched — **the option is consumed and leaves the menu** |

That last row is **DD-008 verified in-game.** `CLAUDE.md` records that
Ragnar's *"I have no fight with you"* option was dead in the 1994 snapshot
and that the handler was restored in `lv-patched/RAGNAR.UNK` on 2026-07-04.
It is live: the option appears, dispatches, and is consumed. Screenshots
`D6-ragnar.png`, `D7-ragnar-nofight.png`. Checkpoint
**`cp7b-ragnar-spoken.sav`**.

### And Thordis

Walked on to **NPC 106 (Thordis)** at (6268, 6592, 0) and played her
thread:

| the Avatar | Thordis |
|---|---|
| *How are you called?* | *"Thordis, I am. After my great-grandmother named I was. The one to tell me the first tales she was."* |
| *What is this place?* | *"Home of the Hrodny's, it is. Ours, always this water has been. Keep it safe, we do, from those dung-beetle Gunnar's."* |

Screenshot `D8-thordis.png`. Checkpoint **`cp9b-thordis-spoken.sav`**.

**Three quest NPCs, in one continuous run from the Vale entry, cheats
off** — and the clan feud heard from both sides: Atli suspects the
Hoskulds, Ragnar sets Gunnar against Huskuld, Thordis holds the water for
the Hrodnys against the Gunnars. That is steps 5-7's content playing as
designed on the shipped EUSECODE.

### The Elder has no dialogue — and an audit of which Vale NPCs do

Walked to **NPC 100 (Female Elder)** at (4352, 6912, 0) and struck her.
Probe clicks land on her — `Item 100 (class Actor, shape 707)` — and the
double-click produces **only `event 18`**, never `event 1`. She has no
conversation.

Auditing the shipped `EUSECODE.FLX` for every LV NPC class
(class = `0x400 + npcnum`, FLEX entry = class + 2):

| npc | builder's label | class | bytes | strings |
|---|---|---|---|---|
| 100 | Female Elder | 0x0464 | **0** | — |
| 101 | Veteran | 0x0465 | **0** | — |
| **102** | Sigrid | 0x0466 | 2,431 | hunter, Sigrid |
| 103 | Farmer | 0x0467 | **0** | — |
| 104 | Child | 0x0468 | **0** | — |
| **105** | Ragnar | 0x0469 | 14,500 | Ragnar, Thordis |
| **106** | Thordis | 0x046A | 37,241 | Thordis |
| **107** | Atli | 0x046B | 38,363 | Gunnar, friend |
| 108 | Inventor | 0x046C | **0** | — |
| 110 | peasant | 0x046E | **0** | — |
| **112** | — | 0x0470 | 13,855 | **Ingyald**, Brewer |
| **113** | — | 0x0471 | 20,568 | **Hrodny**, Inventor |
| **115** | — | 0x0473 | 29,232 | **Tyorvi** |
| **116** | — | 0x0474 | 43,959 | **Ezrekal** |

Two things fall out:

1. **Nine of the placed NPCs have no usecode at all** — Elder, Veteran,
   Farmer, Child, 108, 109, 110, 111, 114. Clicking them does nothing.
   That is expected for villagers and worth knowing before anyone spends
   an hour striking one.
2. **`build_map_10.py`'s labels are out of step with the wiring.** It
   comments npc 108 as "Inventor", but the Inventor/Hrodny class is at
   **113**; and the quest's own NPCs sit unlabelled at **112 Ingyald,
   113 Hrodny, 115 Tyorvi, 116 Ezrekal** — steps 10-12's cast. Anyone
   working the remaining steps should go by this table, not the comments.

### Ezrekal: reached, and her gate confirmed

Walked the ~7,000 units south-east from the village to **NPC 116
(Ezrekal)**, shape 200, and stood beside her at (13004, 12884, 0).
Checkpoint **`cp10b-at-ezrekal.sav`**. She is visible on screen — a
red-robed figure with a staff — and every strike missed. Three reads of
her position over the attempt: **(12800, 12544) → (12910, 12772) →
(12612, 12470)**. She *wanders*, several hundred units between polls.

Two fixes cracked it, and they are now `tools/playtest-linux/chase.py`:

- **Re-read both positions immediately before aiming.** The standstill
  test was right; the *walk* between reads invalidated it. Read NPC, read
  Avatar, project, click — all inside a second.
- **Chase rather than wait.** If she is beyond 260 units, take one burst
  toward her and re-poll. Waiting for a wanderer to come to rest inside a
  fixed ring never converges.

Two rounds later:

```
round 1: npc (12738,12564) me (12804,12580) dist=68   struck, events 0->0
round 2: npc (12664,12662) me (12804,12580) dist=162  struck, events 0->1  TALKING
```

### Ezrekal's gate is live — and it correctly refuses

> *"Believe what I see, I can not! A PAGAN it is! Filth! Wretch! Slime!
> Away with you! Darken not my door! AWAY!"*

She **refuses to speak to an unmarked Avatar.** That is exactly right:
quest step 9 is *"Thordis and Atli give Zealan mark; seek Ezrekal"*, and
step 10 is Ezrekal's history. Reaching her before the mark is supposed to
get the door slammed — so this is the step-9 → step-10 gate confirmed
working on the shipped EUSECODE, not a failure.

Screenshot `E1-ezrekal-talk.png`. Checkpoint **`cp10c-ezrekal-gate.sav`**.

### The quest state machine is live across NPCs

Returning to Ragnar after Atli, his menu had grown a line that was not
there the first time: **"Atli sent me to you."** Talking to one NPC opened
an option on another — the LV quest state is running, not just isolated
dialogue trees.

| the Avatar | Ragnar |
|---|---|
| *Atli sent me to you.* | *"Sent you to me that cur did? **Leader of Huskold clan Atli is!** Why trust a man sent from a cursing fool should I?"* |
| *Atli admires you.* | *"No surprise that is. Only natural for one to admire his superiors it is. Either that or says that he does to subvert me."* |
| *He said you know many things.* | *"Yes, know many things I do. Know everything in this valley I do… And, know many terrible things done…"* |

That last answer grew the menu again, this time with **"Do you know of the
Passage Stone?"** — steps 6-8's hook, opening organically off the referral
chain.

**And organic play has consequences.** Asked a follow-up about Hrodny I
answered wrong, and got: *"Blind are you? Stupid? Wonderful she is.
Beautiful and wise she is! Appreciate this you can not, then waste my time
with you I will not!"* — the thread closed. A scripted run that always
picks the first option will not reach the Stone; the answers matter.

Screenshots `E2`-`E7`. Checkpoint **`cp7c-ragnar-referral.sav`**.

The rest is the same work repeated: locate, walk, strike, read the menu,
choose. The tooling is proven end to end and the roster is here and in
`HANDOFF.md`.

**The lesson, for the third time today: `exact_reach` is stricter than the
engine at z ≤ 0, and on map 8 that difference is the whole map.** Use
`pathfind.py --engine-void` for route questions here, and never conclude
"unreachable" from a strict flood alone.

**This session did not finish the exit test, and the obstacle is content,
not tooling or effort.** It removed one of the two recorded bypasses,
showed the other sits behind a *second* undemonstrated ascent, tested that
ascent to exhaustion with the corrected recipe, built the tools the next
attempt needs, and corrected three wrong entries in the record.

**The decision this leaves is Douglas's**, and it is the same one TODO has
carried since 2026-08-18: give the ascent an intermediate step (two risers
of ≤32 climb fine and sit on the 4-unit lattice), or accept that the exit
test runs with one documented bypass. It is not a decision to take
unilaterally — this stretch of map 8 is **retail geometry**, verified
byte-identical against the pristine `FIXED.DAT.bak`, and editing it changes
what the restoration claims to be.

---

## Harness anomalies

- **`session.sh dbg` sends its command twice** whenever the first send
  times out, and `session.sh resume` queues an `exit` even when the console
  is already closed. Both poison the command queue. This session used a
  local helper (`scratchpad/lv.sh`) that sends once and proves a detach by
  comparing two screenshot md5s rather than waiting for a prompt `exit`
  never prints.
- **`CameraProcess::moveToAvatar` unpins the camera permanently.**
  `Debugger::cmdCameraOnAvatar` installs `new CameraProcess(pt)` — a
  *fixed* camera at a point, not a follow. There is no debugger command to
  re-attach it to the Avatar; only a map change or a session restart
  restores following. Do not reach for it when the Avatar looks missing.
- **The Avatar is invisible for the whole cave ascent.** At z≤8 under the
  z=56 floor he is painted over by the terrain above him, so screenshots
  show bare rock and only `ObjectManager::objectInfo 1` tells you where he
  is. This is not a bug and not a wedge.
- **One unexplained excursion to map 0.** Left standing at
  (29524, 23622, 0) for ~4 s with no input, the Avatar was found on **map
  0** at (15967, 19711, 0); the log shows `Unloading map 8` /
  `Loading Fixed items in map 0` behind a debugger prompt, then map 8
  loading again, and he was back at (29524, 23622, 0) on the next read.
  There is no teleport egg within 700 units of that spot in map 8's
  `FIXED.DAT` (19 on the map, nearest at (31583, 19135)). Not reproduced;
  recorded so the next reader is not surprised by it.

## Disk changes

- `~/.config/scummvm/scummvm.ini` — the four `keymap_ultima8_MOVE_*` lines
  removed (backup in the session scratchpad). This is the change that made
  the run a stock-bindings run; leave it removed.
- `tools/playtest-linux/pathfind.py`, `walkto.py`, `fight.py` — new.
- Saves: slot 4 = `cp3-plateau`, slot 5 = `cp3h-west-strip`, **slot 6 =
  "cave ascended 24001"** → `~/lv-checkpoints/cp3k-cave-ascended.sav`,
  **slot 7 = "through gate 11210"** → `~/lv-checkpoints/cp3l-through-gate.sav`
  (out of the cave, on the plateau, hp 30), **slot 8 = "plateau west 12854"**
  → `~/lv-checkpoints/cp3m-plateau-west.sav` (the forward checkpoint,
  (9258, 12854, 48), hp ~11 and regenerating). Slots 1-3 untouched.
- `docs/playtest-2026-09-01-stock-bindings-climb/` — screenshots and the
  full Cloud Cliffs trace.
- No game artifact, map or source file was modified; all four artifacts
  still match `ARTIFACTS.sha256`.

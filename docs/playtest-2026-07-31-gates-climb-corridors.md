# In-engine playtest, 2026-07-31 — the jump gates, the Map 13 climb, the Map 17 corridors

Session run on kaga/Linux against branch `agent/village-pipeline` (tip
`f78587a`), text-console ScummVM (`scummvm-lv-console/scummvm`) on the Xvfb
harness (`tools/playtest-linux/session.sh`). Debug teleports, `setGlobal`,
`Cheat::toggle` and `Cheat::toggleInvincibility` were used freely — this is
NOT the clean-room run.

Screenshots: `docs/playtest-2026-07-31/`.

---

## Verdicts

| Test | Question | Verdict |
|---|---|---|
| **A** | Does the jump climb Map 18's sanctum wall? | **FAIL — YES IT DOES.** `templeOpen` set to 1 with a full-size Avatar, no potion. DD-005 is bypassable. |
| **B** | Does the jump climb Map 11's sealing boulders? | **FAIL — the boulders hold, the wall beside them does not.** Reached the Map 10 exit with both boulders intact. Four-pillar puzzle is bypassable. |
| **C** | Is the Map 13 climb walkable base→summit on foot, and does the summit trigger fire? | **PASS.** Summit reached at z=118, trigger → Map 17. Two navigation re-positions, both my error, both documented below. |
| **D** | Corridor route to the Memorial Hall + shield half pickup? | **PASS.** Memorial Hall reached on foot, shield half in the pack (weight 20 → 60). |

Two of the four verdicts are new quest-gate failures. Both were predicted by
the 2026-07-31 static audit's Open Question ("CAN THE JUMP BUTTON CLIMB OVER
THE QUEST GATES?"). The answer is yes for both barriers, though for Map 11 the
mechanism is not the one the audit expected.

---

## The jump input mechanics (determined before any test, not guessed)

Grepped from the `scummvm-lv/` tree that the console build is a sibling of:

* **`engines/ultima/ultima8/metaengine.cpp:71`** —
  `{ ACTION_JUMP, "JUMP", _s("Jump (fake both-button-click)"), "SPACE", nullptr }`
  in `U8_KEYS`. The U8 jump action is the **SPACE key**. (`LCTRL` at line 91 is
  the *Crusader* binding and does not apply; U8's `LCTRL` is `MOVE_STEP`,
  "Careful step".) The mouse equivalent is both buttons pressed inside the
  double-click timeout (`u8_avatar_mover_process.cpp:422-440`).
* **`world/actors/avatar_mover_process.cpp:230`** — `ACTION_JUMP` sets
  `MOVE_JUMP`; **line 299 `onActionUp` CLEARS it**. A zero-length synthetic tap
  can therefore be set and cleared inside one 30 fps frame and never seen, so
  every jump in this session was sent as `xdotool keydown space` / sleep /
  `keyup space`. X autorepeat during the hold produces a burst of jumps, which
  is what the "jump bursts" below are.
* **`u8_avatar_mover_process.cpp:506-541`** (inside `handleNormalMode`) — the
  branch taken when `MOVE_JUMP` is set with **no** direction flag:

  ```
  if (checkTurn(mousedir, false)) return;          // turns instead, if facing != cursor
  nextanim = jump;  (jumpUp if mouselength==0 || MOVE_STEP)
  climbanim = climb72;  while (climbanim >= climb16) { if (tryAnim(climbanim,dir)==SUCCESS) nextanim = climbanim; --climbanim; }
  if (nextanim == jump) jump(jump, direction); else doAnim(nextanim, direction);
  ```

  This is the load-bearing detail for interpreting negative results: **a plain
  forward jump only happens after the whole `climb72..climb16` scan has run and
  failed.** Observing an ordinary jump is positive evidence that the climb was
  attempted and refused.
* Lines 464-500 (`MOVE_JUMP` **with** a direction) run the same scan whenever
  the direction came from the keyboard rather than the mouse
  (`!hasMovementFlags(MOVE_MOUSE_DIRECTION)`).
* `direction` in every case is `avatar->getDir()` — the facing, not the cursor.
  The protocol used throughout was therefore: right-mouse walk into the
  barrier (which sets facing and presses the Avatar against it), release,
  leave the cursor where it is so `checkTurn` is a no-op, then hold SPACE.

**Input was validated before it was trusted.** On Map 18 open ground at
(2932,5768,0), a held-SPACE burst moved the Avatar to (2973,6105,0) — 337
units — and a 5-frame screenshot burst shows the jump animation and the camera
scrolling. On Map 11, jumps facing *away* from the boulders moved the Avatar
(8480,22396) → (8440,22308) while jumps facing *into* them produced no
movement and no animation at all. Both are controls proving the key registers
on the map under test.

---

## TEST A — Map 18, the Tiny Tar crack wall — **FAIL (bypassable)**

Setup: `MainActor::teleport 18 2864 6080 0`, full-size Avatar (shape 1),
`templeOpen` (`0x412`) read **0** at the start.

### A1. At the crack aperture itself — no climb

Walked south into the wall at the aperture; stopped at **(2844, 6100, 0)** and
would not advance (`A1-at-crack-wall.png` shows him in the gap). Six
consecutive 2 s jump bursts moved him to **(2842, 6110, 0)** and no further.
z stayed 0; y never reached 6143. `templeOpen` still 0.

That is expected: there is no wall *at* the aperture, so there is nothing for
`tryAnim(climb40)` to grab.

### A2. At plain wall, 150-250 units either side — climbs on the first burst

| approach x | after walking into the wall | after one 2 s jump burst |
|---|---|---|
| 2600 | (2576, 6108, **0**) | **(2576, 6156, 40)** |
| 3000 | (2976, 6108, **0**) | **(2976, 6156, 40)** |

Both criteria from the test brief are met simultaneously: **y > 6143 while
full-size** and **standing at z ≈ 40 on the wall top**. Reproduced at two
independent x positions, first burst each time, and stable across two further
bursts. `A2-on-wall-top-z40.png`.

### A3. It is a complete bypass, not a ledge you get stuck on

From (2976,6156,40) four southward walks took the Avatar to
**(2747,6569,0) → (2815,8261,0) → (2815,9189,0)** — deep inside the sanctum,
still shape 1, still 30/30 HP (`A3-inside-sanctum-after-climb.png`).

**`UCMachine::getGlobal 0x412 1` then read `[0412 01] = 1`.**

`templeOpen` was set with no Tiny Tar potion, no shrink, and no visit to
Hrodny. The whole DD-005 chain (key → chest → potion → shrink → crack) is
optional. Quest steps 17-18 are reachable without it.

### A4. Why the wall top is standable at all

A supporting probe, since the audit assumed the top was bare:

| teleport target | resting position |
|---|---|
| (2844, 6000, 40) — open ground, control | (2844, 6000, **0**) — falls straight down, x/y unchanged |
| (3000, 6128, 40) — on the wall line | (3000, 6000, **0**) — pushed 128 north, falls |
| (2844, 6143, 40) — on the wall line | (3004, 6303, 0) |
| (2864, 6504, 0) — sanctum interior | (2864, 6504, 0) — holds |

So a *teleport* to z=40 on the wall does not stick — but `climb40` lands the
Avatar at y=6156, i.e. **just past** the wall's own y-max of 6143, on whatever
sits immediately south of it (the roof plates the audit noted). The climb
target is not the wall's own top face; it is the surface one step beyond it.
Raising the wall pieces alone may therefore not be sufficient — whatever the
Avatar lands on at (x, 6156, 40) has to go too, or the whole line has to be
taller than 72.

---

## TEST B — Map 11, the sealing boulders — **FAIL (bypassable, via the wall)**

Setup: `MainActor::teleport 11 8576 22300 0`, both quality-299 shape-66
boulders present and untouched (no pillar or receptacle was ever used).

Boulder geometry from `build_map_11.py:731-738` and the built FIXED.DAT: two
128×128×40 solid boxes with max corners (8576,22528) and (8704,22528), i.e.
covering x 8449..8704, y 22401..22528 with no gap between them.

### B1. The boulders themselves refuse the climb

| approach x (start y=22350) | blocked at | 3 × 2 s jump bursts |
|---|---|---|
| 8544 | (8520, 22398, 0) | no movement, no animation |
| 8608 | (8584, 22398, 0) | no movement, no animation |
| 8480 (first run) | (8480, 22396, 0) | no movement, no animation |

`B2-pressed-against-boulders.png`. A 6-frame screenshot burst during a held
SPACE at (8480,22396) shows the Avatar completely static — and the control
(jump facing north, away) moved him 88 units, so the input was live.

The boulder tops *are* standable — `MainActor::teleport 11 8640 22450 40`
leaves the Avatar resting at (8640,22450,**40**) indefinitely
(`B4-standing-on-boulder-z40.png`) — so this is `tryAnim` failing on the
approach face, not an unstandable top. Do not read this as "40-tall shape-66
is safe".

### B2. The chamber's own south wall, ~150 units west, is climbable — and that is the whole puzzle

Reproduced twice, second time cleanly from a fresh teleport:

```
teleport 11 8480 22350 0
walk SW  -> (8328, 22494, 0)     still inside the Four Pillars chamber
jump     -> (8328, 22542, 48)    ON TOP of the south wall  (B6-jump1.png)
jump     -> (8225, 22560, 48)    walking the wall top       (B6-jump2.png)
jump     -> map 10 (13568, 1792, 1)                          (B6-jump3.png)
```

The last line is the teleporter-pad room's exit trigger firing. Per the test
brief that is conclusive on its own: the Avatar left the Elemental Dungeon for
the Lost Vale **with both sealing boulders intact and all four pillars
standing.**

So the boulders are not the weak point — the 48-tall wall run they are set
into is. Any fix that only raises the boulders will not close this.

### B3. A methodology note that cost a run

An earlier sweep teleported to (8640, 22420, 0) and (8704, 22420, 0) and
"walked through" to the pad room. **Those results are invalid**: y=22420 is
*inside* the boulder box (y 22401..22528), so the Avatar was placed inside the
plug and the engine resolved him out the south face. Any future boulder test
must start at y ≤ 22400.

---

## TEST C — Map 13, the climb, base to summit on foot — **PASS**

Cheats + `Cheat::toggleInvincibility` on (4 harpie eggs sit on the upper
climb; none of them ever engaged, so invincibility was never load-bearing).

### C1. A route defect found on the way to the climb foot

`MainActor::teleport 13 3072 11776 0` is the **arrival target** (shape 508,
frame 1, quality 207). The **active return teleporter** — shape 508, frame 0,
quality 462, npcNum 206, `dest_map=10` — is at **(4096, 11776, 0)**, which is
exactly the x of the whole climb line and 1024 units due east of where the
player lands. Its npcNum 206 = 0xCE gives a hatch box of ±384 x / ±448 y, so
it fires anywhere in x 3712..4480, y 11328..12224.

Walking east from the arrival pad toward the climb, as the brief instructs,
bounced the Avatar to Map 10 three times before I routed around it:

```
teleport 13 3072 11776 0
E 1s -> (3072, 11776, 0)
E 1s -> (3696, 11776, 0)
E 1s -> map 10 (7168, 24064, 14)      <- return teleporter
```

`build_map_13.py:210-227` carries a long comment about review finding **H6**,
which relocated this trigger in 2026-07-25 precisely because "simply walking
off the arrival pad toward the gate stepped onto the return trigger and
bounced the player straight back to Map 10". In the built data the two eggs
sit the other way round from what that comment describes: the *active* one is
on the route and the *target* is off it. This is consistent with the
`teleporter()` / `teleport_target()` rename recorded in HANDOFF (commit
771d5c7) having corrected the helper semantics without swapping the two call
sites' coordinates. **H6 is live again.** Not fixed here — the brief forbade
source edits.

Working route: north from the arrival pad to y ≈ 10000 (clear of the ±448
box), then east to x ≈ 4100, then south to the climb foot.

### C2. The ramp itself

Started on foot at the foot tile, (4032, 10240, 0), and walked north. z rises
with y exactly as `climb_tiles()` predicts (118 × k / 88):

```
(4032, 10240,  0)      foot
(4032,  9950,  3)
(4032,  9441,  8)
(4032,  8932, 13)
(4032,  8394, 19)
(4028,  7265, 31)
(4028,  6623, 38)
(4028,  5978, 44)      approaching the switchback corner
```

No seam, no riser refusal, no stall attributable to geometry anywhere on this
leg. `C4-on-ramp.png`, `C5-stuck-9441.png` (a harness stall, not a wall — see
Anomalies), `C6-switchback-approach.png`.

### C3. The switchback

Walking *north* past y=5760 walks off the end of the east-turning leg into the
512-unit gap and drops the Avatar to z=0 at (4028, 5517, 0)
(`C7-fell-into-switchback-gap.png`). That is the designed switchback and my
navigation error, but it is worth recording that the fall is silent and
harmless — the Avatar lands on the z=0 void and can then walk the whole map
underneath the ramp.

Re-positioned to the corner (4032, 5760, 47) — a teleport, disclosed — and the
switchback walks correctly:

```
E  (4032,5760,47) -> (4212,5760,48) -> (4403,5760,51) -> (4914,5760,56) -> (5141,5760,58)
N  (5141,5472,60) -> (5141,5219,63)
W  (4568,5219,68) -> (4195,5219,72) -> (4163,5219,72)
```

`C8-switchback-east-leg.png`, `C9-switchback-west-leg.png`.

### C4. The narrow ledge and the summit

One further re-position was needed: walking north at x=4163 is 67 units east
of the one-tile ledge (x 3969..4096), so the Avatar walked off it and fell to
z=0 again, then continued north into **negative y (-325)** over the void. From
(4032, 5248, 72) the ledge walks cleanly to the top:

```
(4032, 4707, 79)  (4032, 4318, 83)  (4032, 4033, 86)
(4032, 3676, 90)  (4032, 3303, 94)  (4032, 2914, 98)
(4032, 2136,106)  (4032, 1763,110)  (4032, 1374,114)
(4032,  985,118)   <- summit plateau, CLIMB_Z_TOP
```

### C5. The summit trigger fires

One more northward leg from (4032, 985, 118) put the Avatar on the trigger at
(4096, 512, 120) and teleported him to **Map 17**, landing at the map-17
arrival target (5376, 11136, 0) — the position sampled mid-walk was
(5376, 10136, 0) because the walk button was still held after the map change.
`C10-summit.png`, `C11-map17-arrival.png`.

**Verdict: PASS.** Nothing on the climb refused a step. The two interruptions
were both me steering off a one-tile-wide path, and both are recoverable by
walking back rather than only by teleport.

### C6. Caveat the climb does not gate what it looks like it gates

The terrain *beside* the ramp is walkable at z=0 for the ramp's entire length:
from (4164, 7260, 0) the Avatar walked north to (4164, 5164, 0) and later to
y = -325, never on the path. This is the documented
`getPositionInfo` rule (`current_map.cpp:773`, `if (target._z <= 0)
info.supported = true`). It does not open the summit — the plateau and its
trigger are at z=118/120, out of reach from the void — but it means the climb
is not a corridor, and anything placed *beside* the ramp is reachable without
climbing.

---

## TEST D — Map 17 corridors and a shield half — **PASS**

Entered from Test C's teleport at the Map 17 arrival.

### D1. Route

```
(5376,10136,0)  W,W -> (3472,10136,0)   E -> (3680, 9240,0)   through the south-wall gap
                N,N -> (3680, 7336,0) -> (3680, 6336,0) -> (3680, 5336,0) -> (3680, 4336,0)
```

`D1-plaza.png`. The Main Plaza crosses cleanly.

### D2. The new corridors work — and are not required

The **east corridor (x 5120-5631)** was traversed southbound in one leg:
(5580, 4468, 0) → **(5380, 5524, 0)**, i.e. straight through the y 4608..5119
strip that had no floor before commit `c453b4d`. `D3-in-corridor.png`.

Northbound from (5400, 5440, 0) stalled repeatedly; sidestepping east and
going north at **x = 5808** crossed the strip anyway — and 5808 is *outside*
the corridor's east flank wall (x=5663). The same happened at x=3680 in D1.
So the y 4735..5119 gap is passable anywhere at z=0, exactly as HANDOFF's
same-day audit predicted. The corridors are correct and welcome as level
design; they were **not** a hard block in-engine, and the "quest-blocking"
severity in the 2026-07-31 commit message should be read down to "a data hole
and a blackness-rule violation".

### D3. The Memorial Hall and the shield half

Reached the hall on foot and located the halves at the surveyed coordinates
(both confirmed in the built FIXED.DAT: shape 539 at (6208,1568) q=81 and
(7232,1568) q=82, each beside a shape-332 skeleton at (6144,1536) /
(7168,1536)). Approached the eastern one at (7220, 1660, 0)
(`D5-memorial-hall.png`, `D6-at-shield.png`).

Pickup, following the HANDOFF recipe with one correction:

1. `i` to open the pack (`D7-pack-open.png`); dragged the gump clear by its
   brown flap, twice, until the dark interior was fully inside the 640×480
   surface (`D8-gump-moved.png`, `D9-gump-placed.png`).
2. `mousedown 1` on the shield at screen (772,408), held ~0.9 s, then 8 px
   increments. The lift is confirmable on screen: a ghosted copy of the shield
   follows the cursor while the original stays drawn.
3. **Dropping into the pack gump's dark interior gave a red-X cursor and the
   drop was refused.** Dropping onto the **Avatar's own sprite** gave the blue
   up-arrow cursor and worked. *This is the correction to the recipe — go for
   the Avatar, not the open pack.*
4. `ObjectManager::objectInfo 1` → **`total weight: 60`**, up from 20.
   **+40 = one shield half** (a skeleton would have been +190).
   `D10-shield-pickup.png` shows the half sitting inside the open backpack and
   gone from the ground.

The skeleton-wins-the-click hazard did not materialise here: at (7232,1568)
the shield renders well clear of the skeleton at (7168,1536).

---

## Harness anomalies

* **The command pipeline degraded twice**, both times mid-Test-C, and both
  times the symptom was `MainActor::teleport` silently not executing while
  `ObjectManager::objectInfo` kept answering. A `session.sh stop` / `start`
  cleared it each time. Any teleport used as test setup must be
  read-back-verified, not assumed — one Test-B sweep and two Test-C legs were
  run against a position the Avatar was never at, and had to be discarded.
* **`Cheat::toggle` reported `Cheats = false` on the first call after a fresh
  `start`** in two of three sessions, i.e. it started enabled and the first
  toggle turned it *off*. Always call it twice and read the reply; a teleport
  issued while cheats are off fails silently with no log line.
* **The harness has no jump verb.** Every jump here used an ad-hoc
  `keydown space / sleep / keyup space` helper (kept in the session scratchpad,
  not committed, per the brief's write restrictions). `session.sh` would
  benefit from a `jump [holdsecs]` verb next to `walk` — the keyup-clears-the-
  flag trap above is exactly the kind of thing that belongs encoded in the
  harness rather than rediscovered.
* **`session.sh walk`'s direction comment is wrong.** It says "due south (+y)
  is roughly dx -80 dy +80"; measured, `(-80,+80)` is a *southeast* diagonal.
  The correct basis is the isometric 2:1 one: world +x → screen (+2,+1),
  world +y → screen (−2,+1). So N=(140,−70), S=(−140,+70), E=(140,+70),
  W=(−140,−70). Calibrated on Map 13 open ground and used for all of C and D.
* A fresh `start` lands mid-conversation with Devon (the "Who are you? /
  Goodbye" menu). Clicking "Goodbye" at screen (915,338) and waiting ~8 s
  clears it; the `start` verb's Escape presses do not.
* `scummvm-lv/` (the human-play tree) has a **stale detection entry** —
  eusecode md5 `044d45ee…` / size 1502558, against the installed
  `8dcc0917…` / 1502369 — which is what `install_lv.sh`'s warning is about.
  `scummvm-lv-console/` is current and detection was confirmed live:
  *"Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)"*.

## Disk changes

* `./install_lv.sh` run (installs the four artifacts into
  `shared/data/u8-install/`).
* `shared/u8-lv-patched/STATIC/FIXED.DAT` refreshed from `shared/build/`
  — it was stale at `8e5d27ec…` against the current `b4ae97bb…`. The other
  three artifacts already matched by sha256 and were left alone.
* This report and `docs/playtest-2026-07-31/` (35 screenshots).
* No source file, map builder or artifact was modified.

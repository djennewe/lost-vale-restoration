# Playtest 2026-10-24: trigger 211's box, the Map 11 rats, the harpie corpse

This session verifies three uncommitted map fixes in ScummVM:

- **Map 10, trigger 211.** `build_map_10.TRIGGER_211_RANGE` = 0x33. The box was ±416×±96 and is now ±96×±96.
- **Map 11, rat group 4.** The group moved from the corridor mouth to the Water section's north-east bay. Its trigger is now a ±32×480 strip at x 13056.
- **Map 13, harpie corpses.** The map is unchanged; `test_harpie_corpses.py` is new.

I walked every decisive move. Each fix has a before-control: the same move, made on the same engine with a save that still carries the old map items.

## Verdicts

| Claim | Verdict | Evidence |
|---|---|---|
| **C1a** After the endgame, a walk SW or W off the stair foot leaves without going to Map 18 | **PASS, 0 of 71 holds fired** (finding 1 covers what the claim does not) | **Walked:** from the shelf after the real EggEndgame: 9 holds (SW, W, NW; walk and run). **Positioned:** 12 z 0 landing spots × {SW walk, SW run, W walk, SW keyboard}, 3 bottom-step spots × {SW, W, SW keyboard}, one keyboard pilot, 4 reruns of off-spot holds (anomaly 1) and 4 follow-ups after a W stop: 62 valid holds. None unloaded Map 10. **Before-control:** `s18b` still carries the old item (n 211, range 13,3). Walked down to the bottom-step wedge (18496,23255,8), one SW walk went to **Map 18**. On the new item, the same SW walk from the same wedge stayed on Map 10 at (18136,23551,0) |
| **C1b** The deliberate entries still work | **PASS** | **S from the stair:** walked descent to (18352,23311,0), then a S hold: **3 of 3** went to Map 18. **Mouse S off the bottom step:** **9 of 15** fired. The west three x positions (18399, 18431, 18463) fired at both y values and both gaits. x 18495 and 18527 stopped at y 23263, against the cell, as claimed. **Forecourt N** from y 23900: x **18336, 18432, 18591 fired**, while **18335 and 18592 did not**. That is the half-open box [18336, 18592) to the unit. **Leg 6's NW** from (18720,23808): 2 of 2 fired. A 1.0 s N hold confirmed the landing: `Unloading map 10` → `Loading Fixed items in map 18`, (3072,1792) |
| **C1c** A keyboard S hold down the stair is turned SW at the foot and mostly misses 211 | **PASS (measured): 0 of 12 fired** | Six shelf starts × {Up, Shift+Up}, each held 6 s after a S facing. 3 reached the pit floor and left SW/S. 7 stopped on the stair: 3 at (18412,23000,72) and 4 at the bottom-step wedge (z 8). 2 never faced S and stayed on the shelf. The simulator gives the same split (stops at z 48-72, clears SW, no fires). The cost is that a keyboard player reaches 211 only from the forecourt or with the mouse |
| **C2a** From the hub, down the corridor, past the mouth and on to the Fire doorway: no rats | **PASS** | After the hop, I walked from the Map 11 arrival (9728,1896) S through the hub and the corridor to (9728,15496). I followed on to the Fire doorway (6208,16656), the Water talisman (12712,18672) and the pillars doorway (8640,19336). **0 `event 7 @ 0481`** and **`findShape 806`: 0** the whole way. **Before-control:** `s03b` still carries the old trigger 27731 (9728,14528), range 9,2. A 2 s S walk from (9728,13900) logged `Item: 27731 (shape 73) calling usecode event 7 @ 0481:0080`, and **4 rats** appeared at the mouth. They took hp 27 → 23 |
| **C2b** A walk E into the bay across the strip hatches the rats, and they attack | **PASS** | **Negative control:** at x 12980, just west of the strip, a N walk 15276 → 14580 and back S to 14940 gave no `event 7`, and `findShape 806` read 0. **Crossing:** one E walk (12980 → 13292, y 14940) logged `Item: 2898 (shape 73) calling usecode event 7 @ 0481:0080`, and `findShape 806` listed **five** rats (ids 160-164). Over the next 15 s they went into combat (flags 0x800…) and took **hp 29 → 22 → 18** |
| **C3** A lane harpie's corpse in the middle lane: the Avatar passes with a sidestep; does a straight walk stall? | **PASS; the straight walk stalls** | Sword bank, walked into the trigger, `c`, fought: harpie 160 died in ~14 s, and the Avatar kept hp 30. The corpse lies at (5183,6047,76), box x 5055-5183, y 5919-6047. **Straight:** with the Avatar at (5119,6119) (box wholly inside the corpse's x span), N walk, N run and a second N walk moved **0** units each. **Sidestep:** W 0.8 s → (5015,6119), then N → (5015,5623): **passed**. **Partial overlap:** from (5223,6215), N slid right to (5247,6103), and a second N passed to (5247,5703) |

Not run, because this assignment excluded rebuilds: the verifier's always-checks, `tools/run_all_tests.sh` and a full `tools/build_artifacts.sh`. The main agent should run both.

## Build pinned

- **The copy.** `shared/u8-lv-patched` and `scummvm-lv-console/scummvm` were copied once to `/tmp/claude-1000/fix1024/`. They were hashed at the start (`pinned-start.sha256`), and `sha256sum -c` matched at the end:
  - FIXED.DAT, top level and `STATIC/`: `ef2ed0f4…`
  - EUSECODE `2e3b71c2…`, U8SHAPES `efb16af1…`, TYPEFLAG `d26d1531…`, ANIM `696dbeb9…`
  - u8monsters.ini `7f666fe9…`, binary `d371f7ce…`
- **What changed.** Against the FIXED the harpie banks were built on (`1a9ce209`), a per-map item comparison (`u8_map.MapArchive`, all 256 maps) differs on **maps 10 and 11 only**.
- **In engine, after the hop or map change:**
  - Map 10: `objectInfo 9870` reads `(18432, 23552, 0) q: 467, m: 18, n: 51 … range: 3, 3`.
  - Map 11: `findShape 73` lists trigger **2898 (13056,14880,0), range 1,15**. `findShape 500` lists eggs 2899-2903 at (13504,14688), (13792,14688), (13632,14944), (13504,15200) and (13792,15200).
- **The driver.** `/tmp/claude-1000/replay1017/py` was copied to `fix1024/py` with its paths repointed. Display :95, 320×200 at scale 2, text-console build.

## C1a: leaving down the stair (PASS, 0 of 71)

**Setup (walked).**
1. Load `replay1017-s18a` (Map 18, just S of trigger 210).
2. Walk N 1.6 s: `Unloading map 18` → `Loading Fixed items in map 10`. This is a real map load of the new FIXED (`c1-01`).
3. Leave EggEndgame untouched for about 230 s (`c1-02-endgame-done`). endgameStarted (0x716) = 1, godsFree = 1, and the Avatar stood at (18432,22615,112). Scratch save `c1-post-endgame`.

**Descents.** Repeated 1.0 s S presses go down the stair.
- From (18432,22615,112): (18500,23019,64) → (18500,23051,56) → (18500,23163,32) → **(18352,23311,0)**. All 8 descents from there landed on the same spot (`c1a-01`).
- From the pad's own spot (18432,22719,112) the descent **wedges on the bottom step at (18496,23255,8)**, and S is refused there (`c1a-03`). This is leg 6's wedge, reproduced on both the old and the new items.

**Walked holds off the foot, new item (0 fired).**
- From (18352,23311,0):
  - SW walk → (17684,24107) twice
  - SW run → (17100,24563)
  - W walk → (18112,23263)
  - W run → (17984,23135)
  - NW walk → (18124,22883)
  - NW run → (18112,22867)
- From the wedge (18496,23255,8): SW walk → (18136,23551,0), then SW again → (17540,24267).
- **W does not leave the pit.** It stops against the west wall at x ≈ 18111-18123, which is the simulator's 'stops' too. A S or SW hold from there then leaves without firing: (18119,23247) → (18119,24303), and (18115,23243) → (17671,24047).

**Positioned grid (setup teleport, cheats off, then a walked hold).**
- **Spots.** 12 of the 42 z 0 landing spots: x 18335-18527, y 23263-23343, corners and middle. Also the bottom step at (18496,23255,8), (18431,23247,8) and (18527,23247,8).
- **Result.** 57 valid holds, 0 fired. Every SW mouse hold ended out of the pit to the south-west, at x 16503-17891 and y 23835-25223.
- **Lost teleports.** 4 holds started off-spot, because `ATTACH FAILED` dropped their teleport. They were detected by comparing the teleport position with the requested spot, then rerun; the reruns also gave 0 fires.
- **Keyboard holds that were not SW.** 2 of the 16 keyboard holds, from (18527,23263) and (18479,23263), never took a SW facing. The prime press did not turn him, and the hold walked NW. They are no-fire holds, but not SW keyboard holds.

**Negative control (old item, same engine).**
- **The save.** `replay1017-s18b` (md5 `dc9b57e4`), loaded with no hop: `objectInfo 9870` reads `n: 211 … range: 13, 3`.
- **The walk.** The descent wedged at (18496,23255,8), and one SW walk gave `Unloading map 10`. The Avatar was on **Map 18 at (3000,1864)** (`c1a-ctl-old-foot`, `c1a-ctl-old-after-SW`).
- **On the new item.** The same walk from the same wedge does not fire (`c1a-04`).

Plate `c1-00-map-pit-holds.png` maps every hold of the session over the simulator's rest levels, with the old (orange) and new (red) boxes.

## C1b: the deliberate entries (PASS)

- **S down the stair.** Three walked descents to (18352,23311,0), each followed by a 3 s S hold (walk, run, walk). All 3 went to Map 18. A player who walks S from the pad reaches 211.
- **Mouse S off the bottom step (z 8).** 15 holds, 9 fired:

  | x | y 23231 walk | y 23247 walk | y 23247 run |
  |---|---|---|---|
  | 18399 | fired | fired | fired |
  | 18431 | fired | fired | fired |
  | 18463 | fired | fired | fired |
  | 18495 | stop (18495,23263) | stop (18471,23263) | stop (18471,23263) |
  | 18527 | stop (18527,23263) | stop (18503,23263) | stop (18503,23263) |

  The east half stops against the z 112 cell under the stair's foot. That is the fixer's "fires or stops" (their 42/72; this run, 9/15).
- **Forecourt N** (walk, 3 s) from y 23900:

  | x | Result |
  |---|---|
  | 18335 | no fire, slid to (18247,23108) |
  | 18336 | fired |
  | 18432 | fired |
  | 18591 | fired |
  | 18592 | no fire, stopped at (18592,23500) |

  The edges sit exactly where `EggHatcherProcess::run`'s half-open test puts them for range 3.
- **Leg 6's NW from (18720,23808).** Walk and run, both fired.
- **The landing.** In the 3 s forecourt holds the Avatar ended back on Map 10's shelf (finding 3). A 1.0 s N hold from (18432,23900) settled the landing: `Unloading map 10` → `Loading Fixed items in map 18`, at **(3072,1792,0)** (`c1b-02`).

## C1c: keyboard S down the stair (PASS, measured)

Each hold: a mouse S tap to face S, then `Up` (walk) or `Shift+Up` (run) held for 6 s.

| Start (z 112) | Up | Shift+Up |
|---|---|---|
| (18432,22719) | stop (18412,23003,72) | stop (18500,23255,8) |
| (18432,22615) | **left** (18128,24127,0) | stop (18500,23255,8) |
| (18400,22780) | **left** (18124,23896,0) | **left** (18164,24392,0) |
| (18464,22780) | stop (18412,23000,72) | stop (18412,23000,72) |
| (18496,22780) | stop (18524,23256,8) | stop (18496,23262,8) |
| (18400,22615) | shelf (18556,22779,112) | shelf (19100,22192,112) |

- **0 of 12 fired.** Every hold that reached the floor was turned SW and left, west of the box.
- **The simulator agrees.** `avatar_mover.hold` from the same starts gives 'stops' at z 48-72 or 'clear' SW, with no trigger.
- **Not tested.** A keyboard S hold on the old item.

## C2a: the hub-to-south walk hatches nothing (PASS)

- **Before-control (old items).**
  - **The save.** `replay1017-s03b` (md5 `4fdbe669`), with no hop. `findShape 73` lists 27731 at (9728,14528) with range 9,2, and the five eggs at the old spots, (9024,14400) to (11424,15520).
  - **The walk.** A setup teleport to (9728,13900), then a walked 2 s S hold to (9728,14724).
  - **The hatch.** `Item: 27731 (shape 73) calling usecode event 7 @ 0481:0080`, and `findShape 806` then listed **4 rats**: 155-158 at (9356-9788, 14424-14816). hp went 27 → 23 (`c2-ctl-old-rats`). This is leg 3 finding 4, reproduced.
- **Hop.** `MainActor::teleport 9 13696 13760 0`, then `11 9728 1896 0`. After it, the new trigger 2898 and the eggs 2899-2903 were present, and `findShape 806` read 0.
- **Walk (new items).** All of it was walked, from (9728,1896):
  - 4 S runs (≈ 3,500 units each) through the entry hall, the hub, the hub-to-Water corridor and its mouth, to (9728,15496) (`c2a-01`);
  - the follower W/S to the **Fire doorway (6208,16656)** (`c2a-02`);
  - SE/E to the **Water talisman** area (12712,18672) (`c2a-03`), via a step off the z 8 island at (9392,18368) (`c2a-03b`);
  - W to the **pillars-chamber doorway** (8640,19336) (`c2a-04`).
- **Result.** Over the whole log span: **0** `(shape 73) … event 7` lines, and **`findShape 806` read 0** at the mouth, the Fire doorway and the pillars doorway.

## C2b: the bay strip hatches and the rats attack (PASS)

- **Approach.** The follower took him from the pillars doorway N/NE/E to (12980,15276). x 12980 is west of the strip's x 13024-13151. Scratch save `c2b-west-of-strip`.
- **Negative control.**
  - N walk at x 12980, y 15276 → 14580, then S back to 14940.
  - Both legs ran the length of the strip's y span, 44 units west of it.
  - No `event 7`, and `findShape 806` read 0.
- **Crossing.**
  - One 1.2 s E walk, (12980,14940) → (13292,14940).
  - It logged `Item: 2898 (shape 73) calling usecode event 7 @ 0481:0080`.
  - 0.3 s later, `findShape 806` listed five rats, 160-164, at (13292-13420, 14860-15008). They had already closed on him from the eggs 448-736 east (`c2b-01`).
- **Attack.**
  - Rats read flags 0x800808 / 0x800c08 (the combat bit).
  - hp 29 → 22 within 2.5 s, then 18 (`c2b-02`, `c2b-03`).
  - Two rats were at hp 0 (flag 0x8000) by about 10 s. The Avatar was not in combat mode (finding 5).

## C3: the harpie corpse (PASS; the straight walk stalls)

- **Setup.** Bank `harpie1024-m13-south-sword-hp30.sav` (md5 `2d5dc63d`), with no hop. Map 13's items are identical to that bank's build (above). `findShape 500` read 27278 (5183,5631,76) and the other three eggs.
- **The approach.** Four walked 0.9 s N presses up the middle lane at x 5119. The fourth hatched harpie 160 at the egg, with hp 34 (`c3-01`).
- **The fight.** `c`, then the 10-24 v2 driver: double-click toward the harpie when the box gap is ≤ 40, else a 0.8 s advance and a swing. The harpie had 34 → 12 → 6 → 0 hp at 3.6 s intervals, and the Avatar kept hp 30 (`c3-02`). Corpse 160: (5183,6047,76), flags 0x1400.
- **Passing.** `c` again (Avatar flags 0x408, out of combat), then:

  | Start | Move | End |
  |---|---|---|
  | (5119,6119), box x 5055-5119, inside the corpse's 5055-5183 | N walk 1.5 s | (5119,6119): **0** |
  | same | N run 1.5 s | **0** (`c3-03`) |
  | same | N walk 1.5 s | **0** |
  | same | **W 0.8 s** | (5015,6119) |
  | (5015,6119) | N 2.0 s | **(5015,5623): past the corpse** (`c3-04`) |
  | (5223,6215), box 5159-5223, overlapping the corpse by 24 | N | slid right to (5247,6103) and stopped |
  | (5247,6103) | N again | **(5247,5703): past** (`c3-05`) |

- **Mobility.** A 0.6 s S press between the stalls also moved 0. That is the known short-press loss (harness anomaly 2), not the corpse: the corpse is north. Each stall used a 1.5 s press, the length that moved him everywhere else this session.

## Findings

1. **Severity: low (route, not a regression). 211 still fires for some SW/W holds that start ON the stair, above its foot.**
   - **Scope.** C1a's claim covers the z 0 landing and the test covers only that. A player who turns SW part-way down is not covered.
   - **Simulator.** `avatar_mover.hold`, 4 s, all 8 modes, ran from every stair rest cell on an 8-unit lattice (x 18340-18600, y 22700-23264, z > 0). Of 23,976 holds from 999 cells, **139 fire 211**:
     - 134 are keyboard holds;
     - **5 are mouse SW runs**, from (18468-18500, 23132-23156, 32);
     - the firing cells are z 16-48, plus the bottom step's NW corner at x 18400-18402, y 23231, z 8 (keyboard SW).
   - **In engine.** Ten holds at the predicted cells, setup teleport then the hold. **6 went to Map 18:**
     - (18400,23231,8) keyboard SW: 2 of 2
     - (18468,23148,32) mouse SW run: 1 of 2
     - (18500,23132,32) mouse SW run: 1 of 2
     - (18468,23108,40) keyboard W: 1 of 2
     - (18420,23180,24) keyboard SW: 0 of 2
   - **Natural rest points.** None of the 10 positions a walked descent actually rested at in this session is a firing cell, by the same simulator: (18500,23019/23051/23163), (18496,23015-23255) and (18352,23311).
   - **Not a regression.** The new box lies inside the old one, so every such fire also fired before.
   - **Fix for the author, if wanted.** Extend `temple_stair_foot`'s leaving holds to the stair cells. The narrow ones are the mouse SW runs at z 32.
2. **Severity: info. The descent from pad 210's own spot wedges on the bottom step.**
   - **Where.** From (18432,22719,112), S presses stop at (18496,23255,8), on both the old and the new items. S is refused there; SW and W leave.
   - **From the post-endgame spot.** The descent from (18432,22615,112) lands on the floor at (18352,23311,0) instead.
   - **Where the endgame left him.** In this run EggEndgame left the Avatar at (18432,22615), not on the pad's 22719.
3. **Severity: info (not this change). A held N through 211 can bounce straight back.**
   - **The arrival.** 211 lands the Avatar at (3072,~1792) on Map 18, just S of trigger 210.
   - **The bounce.** A mouse N or NW hold that is still down walks into 210 and back to Map 10's shelf. All 5 of the 3 s forecourt holds that fired ended on Map 10 at z 112: (18432,22223), (18328,22511), (18432,21815,56).
   - **Who sees it.** A player who keeps holding the button through the transition.
4. **Severity: info. One engine/simulator divergence.**
   - **What happened.** The SW walk from the wedge (18496,23255,8) stopped in engine at (18136,23551,0) after about 466 units. The simulator says 'clear', and continues SW.
   - **Harmless.** A second SW press went on to (17540,24267).
   - **Elsewhere the two agree.** Every W/NW stop matched the simulator to the unit, for example (18112,23263) and (18112,22867).
5. **Severity: info. Two of the five bay rats died within about 10 s without the Avatar attacking.**
   - **What I saw.** Rats 160 and 164 read hp 0, flags 0xa0e2/0xa0c2. Avatar flags were 0, not in combat.
   - **Cause.** Not traced [INFERENCE: rats striking each other in the scrum].
   - **The claim is unaffected.** The other three kept attacking.
6. **Severity: info. 5 transient `Cycle in paint` lines in `lv_c1b.log`.**
   - **The lines.** `125 -> 107 -> … -> 125`, `125 -> 1`, `1 -> 107`. Each came right after a setup teleport onto the shelf or stair, among about 120 such teleports.
   - **Known.** This is the known shelf knot, transient, as in vignettes-verify4. 0 in the other logs.
7. **Severity: info. Not tested: the bay's south door.**
   - **The gap.** The strip spans y 14400-15423. The section runs to y 19455, so a player who comes up the east wall from the Water talisman can enter the bay from the south without crossing the strip.
   - **Status.** The author documents this in `build_map_11.py`. I did not walk it.

## Harness anomalies

1. **`ATTACH FAILED` about 20 times.**
   - **Lost commands.** 4 setup teleports were lost, so their grid holds started where the previous hold ended. I detected them by comparing the teleport position with the requested spot, discarded them and reran them. One scratch save (`c1-foot-walked`) also failed.
   - **Cheat toggles.** Every one landed: each log's `Cheats = true/false` lines strictly alternate.
2. **Short presses (0.6 s) often moved 0** in C3 (S and E). This is the known first-input-after-console-close loss. Each decisive hold was 1.0-3.0 s.
3. **The keyboard facing comes from a mouse tap.** At (18527,23263) and (18479,23263) the SW tap did not turn him, and the keyboard hold walked NW (C1a).
4. **The follower hit `NO RAY`** on Map 11's z 8 island at (9392,18368). Manual E/SE steps freed it.
5. **No matplotlib in the kernel.** The pit plate was drawn with PIL.

## Console commands (whole session)

- `debugflag_enable Object` after each of the 5 starts.
- **Reads:**
  - `ObjectManager::objectInfo 1` (every position read), `objectInfo 9870` and `objectInfo 2898`;
  - `ObjectManager::findShape 508 / 500 / 73 / 806 / 873`;
  - `UCMachine::getGlobal 0x716 1` and `0x40E 1`.
- **`Cheat::toggle`: 122 on/off pairs**, each wrapped round one `MainActor::teleport`. They were all setup: the shelf, landing, step and forecourt spots on Map 10, the Map 11 corridor spot for the old-items control, and the Map 9 ⇄ 11 hop. Logs: `lv_c1.log` 6/6, `lv_c1b.log` 113/113, `lv_c2old.log` 3/3, `lv_c1old.log` and `lv_c3.log` 0. Cheats were off for every hold.
- **`MainActor::teleport`: 122 requests**, 4 lost to anomaly 1.
- **`Ultima8Engine::saveGame`: 6 scratch-save attempts (5 written; `c1-foot-walked` failed)**, into the session's own savepath only.
- **Not used:** `loadGame` (reloads were restarts with `--save-slot=1`), `toggleCombat` (C3 used the `c` key), heal, invincibility, item cheats and `setGlobal`. A grep of every log for `invincib|Cheat::heal|Cheat::items|setGlobal` finds 0.

## Log hygiene

| Log | Session | `Cycle in paint` | Assertion / Segmentation / `stuck in process loop` / `Non-existent process` | `Unhandled intrinsic` |
|---|---|---|---|---|
| `lv_c1.log` | the endgame | 0 | 0 | 0 |
| `lv_c1old.log` | the old-211 control | 0 | 0 | 0 |
| `lv_c1b.log` | C1 grid, C1b, C1c | 5 (finding 6) | 0 | 0 |
| `lv_c2old.log` | Map 11 | 0 | 0 | 0 |
| `lv_c3.log` | the harpie | 0 | 0 | 0 |

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-24-fixes-211-rats-corpses/` (27 plates):
  - `c1-00-map-pit-holds` (every Map 10 hold, both boxes), `c1-01`, `c1-02-endgame-done` and `c1-end`;
  - `c1a-*` (with the old-item control), `c1b-*`;
  - `c2-ctl-old-rats`, `c2a-01`…`04` and `c2a-03b-island-z8`, `c2b-01`…`03`;
  - `c3-00`…`05`.
- **No other tracked file was touched.** That includes `TODO.md`, by the assignment. No rebuild, no commit.
- **`~/lv-checkpoints/`: nothing written.** I used `replay1017-s18a`, `s18b`, `s03b` and `harpie1024-m13-south-sword-hp30` read-only.
- **Scratch** is `/tmp/claude-1000/fix1024/`:
  - the pinned `game/` and `bin/`, `pinned-start.sha256` and `pinned-end.sha256`;
  - `py/` (the replay driver with its paths repointed);
  - the logs `lv_c1.log`, `lv_c1old.log`, `lv_c1b.log`, `lv_c2old.log` and `lv_c3.log`, plus `trace.txt`;
  - `c1_results.json`, `c2_results.json` and `c3_results.json` (every hold: start, teleport landing, end, map, fired);
  - the scratch saves in `sp/*.sav`: `c1-post-endgame`, `c1-step-wedge`, `c1-foot-after-sw`, `c2-m11-new-arrival` and `c2b-west-of-strip`.
- **Stopped** my ScummVM and Xvfb `:95`. A `pgrep` for `fix1024|Xvfb :95` finds nothing.

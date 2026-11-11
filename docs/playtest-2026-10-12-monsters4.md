# Playtest 2026-10-12: LV monster eggs, round 4 (golems 1/7 north of the wall, Lake shore rails)

This is the verifier pass on main `f2418dd`, fork `e48f8716`.

**Setup**
- Display and window: Xvfb :92, ScummVM at 320x200 ×2, frameLimit on.
- Binary: a copy at `/tmp/claude-1000/vmon4/bin/scummvm`, sha256 `21f07b14…`. It is identical to `scummvm-lv/scummvm`, which was built at 20:33 on 2026-10-11, after the fork commit at 20:31.
- Game data: an isolated copy of `shared/u8-lv-patched` at `/tmp/claude-1000/vmon4/game`.
- Hashes: `shared/build`, the harness dir and my copy all match `ARTIFACTS.sha256`:
  - FIXED `6abe1497` (in both places);
  - EUSECODE `f0a9e709`;
  - U8SHAPES `e0af51ea`;
  - TYPEFLAG `7c1d8454`;
  - ANIM `696dbeb9`.
- Timing of the copy: when I arrived, Main's `tools/integrate.sh --record --force` was still running. `shared/build` then still held FIXED `96d144d8`, and TYPEFLAG and U8SHAPES were half rebuilt. I waited for it to finish and copied after the harness step had landed.
- Base save: `~/lv-checkpoints/replay1011-s07-m10-ragnar-told-stone.sav`, used read-only, loaded once.
- Fresh maps: every map I judged was entered from another map. On each arrival I read `findShape 500`: 17 eggs on all 3 Map 11 arrivals, and 10 on all 3 Map 10 arrivals. The new golem-1 egg read `(3040, 2240, 0)` in-engine.

**Cheats and debug aids used:**
- **`Cheat::toggle`** and **`Cheat::toggleInvincibility`**. Invincibility was on for the whole session, and the Avatar's hp read 30 throughout.
- **`MainActor::teleport`**, used only for positioning. Every trigger under test was then walked into. The teleports were:
  - Map 11: (4200,2240), (3900,2960), (3232,3300), (3290,1650), (4300,2440).
  - Map 10: (13820,20800) twice, (13300,20750), (13630,20560), (14080,20560), (10144,16050), (11150,17000), (9300,19560), (11150,19500), (14200,20640), (14314,20766).
  - Map hops via (7212,16956) on Map 10 and (4200,2240) on Map 11.
- **`MainActor::toggleCombat`**, for the fights.
- **Debug flags:** `debugflag_enable Object` and `debugflag_enable Actor`.
- **No item cheats.** The Avatar fought unarmed: all his blows logged `type=1`.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| G1a | Map 11: entering from the east through (3424-3807, 2080-2463) hatches golem 1, which walks straight to the Avatar and attacks | **PASS**. 2 of 2 runs (mid-box and SE-corner entries) |
| G1b | (3104-3359, 2112-2367) hatches golem 7, which reaches him without going round the wall | **PASS, with a caveat**. The box was entered from the north. Reaching it from the east with golem 1 alive was not achieved (finding 2) |
| G1-neg | Old trigger spots (3232,3040) and (3520,2592) | **PASS**. Walked across both and nothing hatched. The in-engine trigger list has no trigger left at either |
| S1a | Walk on and off the pier's foot | **PASS** (2 visits) |
| S1b | South shore: stopped short of the water | **PASS**. The least y reached on the south shore was 20544 |
| S1c | Wave 1 fights on and near the pier foot: nobody drowns, and stumbles toward the water are stopped | **PASS**. 7 fights over 2 fresh visits: 256 blows on the Avatar, 31 of his blows landed, 0 water events. One caveat: a zombie was never knocked *north* into the rail by a blow (section S1c) |
| S1d | West shore near kith 3 and spider 7 | **PASS**. Both hatched on their own triggers, and both fights at the rail ended with the Avatar at x ≤ 11262 |
| L | Log hygiene, and `Cycle in paint` from the rails | **PASS**. 0 `Cycle in paint`, 0 `failed to set stats`, no errors |
| Estate | `tools/run_all_tests.sh` | **PASS**: 52/52 in 393 s. `test_monster_eggs` 421/0 |
| Build | `tools/build_artifacts.sh` | **NOT RUN by me**, because the brief bars build scripts. Main's `integrate.sh --record` ran it during setup, and every hash matches `ARTIFACTS.sha256` |
| Patch | Tracked patch == fork diff | **PASS** (`diff -q` was silent; the fork is unchanged at `e48f8716`) |
| Shapes / usecode | `SHAPE_*` / `TYPE_SHAPES`; Compilation Report | **Skipped**. The change has no new shape (497 and 498 are retail) and no usecode |

## G1 Map 11, golems 1 and 7: PASS (G1b with a caveat)

**Run A: golem 1, mid-box entry from the east.**
- From (4200,2240) the Avatar ran west along y 2240. Trigger 5368 (group 1) fired with him at (3432,2240).
- Golem 124 hatched and logged `_target found: 1`.
- **First read:** (3328,2240), hp 158, `f 0x20c2`, `800`. It had walked east along its egg's own row, y 2240, from (3040,2240) to 104 units from him.
- **Blows:** `received hit from 124 (dmg=23)`, then `21` and `16`.
- Plates: `G1-golem1-hatched-first-read`, `G1-golem1-attacks`. The plate shows the wall's east end behind them, with both on its north side.

**Run C: golem 1, entry at the box's south-east corner** (after a map hop, 17 eggs).
- From (4300,2440) he walked west. Trigger 15315 fired at (3516,2440), which is beside the wall's east end (3456,2560).
- Golem 126 read (3456,2368), `c00`, on its first read, which is on the line from its egg to him.
- **Blows:** `dmg=19`, `15`, then 17, 19, 25, 16 and 17 (`G1-golem1-se-corner-entry`).
- This is the entry point the old trigger straddled. The golem came to him north of the wall, with no detour.

**Run B: golem 7** (after a map hop, 17 eggs).
- From (3290,1650) he walked south along x 3290, which keeps out of box a. Trigger 17004 (group 7) fired at (3290,2178).
- Golem 125 hatched and logged `_target found: 1`. Its first read was (3208,2360), `808`.
- It came north-east from its egg at (2688,2496), was never further east than x 3244, and was never south of the wall.
- **Blows:** `dmg=20`, `24`, `22` (`G1-golem7-first-read`, `G1-golem7-attacks`).
- 16 eggs were left, so golem 1's egg stayed unhatched: box b does not reach group 1.

**Negative controls (on the fresh map before run B):**
- **Old trigger 7 (3232,3040), box ±160.** He walked north along x 3232 from y 3204 to 2652, through the old box: no `event 7` (`G1-neg-old-t7-south`, taken at the start of that walk).
- **Old trigger 1 (3520,2592).** He walked east along y 2652 from x 3336 to 3744, through the old box and below the new box a (y ≤ 2463): no `event 7` (`G1-neg-old-t1`).
- **In-engine trigger list.** `findShape 73` shows only two Map 11 triggers west of x 4000: (3584,2240) `n 85` and (3200,2208) `n 51`.

## S1 The Lake's shore rails: PASS

**S1a Pier foot.**
- **Visit 1.** He walked north from (13820,20800,0): (13820,20696,0), then (13820,20328,8). He was on the pier at z 8, and wave 1 fired (trigger 18724, zombies 127 and 128) (`S1-on-pier-foot-z8-wave1`).
- **Back off, visit 1.** South to (13860,20624,0).
- **Visit 2 (fresh), the same both ways:** (13820,20320,8) on the pier, then (13860,20552,0) on the shore.
- **Fight 3** also took him back onto the foot at (13866,20452,8).

**S1b South shore.** This is the rail along y (20447,20479].
- **Walk.** He walked north from (13264,20786) and stopped at (13388,20558), then (13380,20550) (`S1-south-shore-walk-N`).
- **Teleport.** A positioning teleport to (14080,20560) settled at (14080,20544).
- **Floor.** Across every south-shore read in the session, y was never below 20544. A body against the rail stands at y ≥ 20543.

**S1c Fights.** The worst case for the Avatar is a zombie south of him while he stands at the waterline, because its blows stumble him north.

| Fight | Where | Hits on him | His blows landed | Where he ended | Water events |
|---|---|---|---|---|---|
| 1 (visit 1) | (13380,20550), zombies 127 and 128 south of him (`S1-fight1-zombies-south-of-him`) | 18 in 30 s, then 16 with combat on | 0 | Slid west along the rail to (12560,20546). Every read was y 20546. Zombie 127 also came to rest on the rail line, at (13288,20544) and (13112,20544) | 0 |
| 2 | The corner where the pier's west rail meets the shore rail, (13630,20560) | 9 | 0 | Pushed east to (13822,20560,0), the shore at the foot (`S1-fight-pier-foot-shore`) | 0 |
| 3 | On the foot at z 8 | 6 | 0 | (13930,20452,8), against the pier's east rail (`S1-fight-on-pier-foot`) | 0 |
| 4 | East of the foot, (14080,20544) | 10 | 0 | Pushed east along the rail to (14408,20544) (`S1-fight-east-of-foot`) | 0 |
| 5 (visit 2, walked in; wave 1 = 131, 132) | The shore at the foot, zombie 132 on the foot at (13872,20464,8) | 15 | 8 on 132 | (14028,20592,0) (`S1-fight5-blows-at-foot`) | 0 |
| 6 | East shore of the foot, 131 west of him | 4 | 8 on 131 | 131 went west along the shore | 0 |
| 7 | Teleported 110 south of 131 to strike it north | 6 | 15 on 131 | 131 moved *south* to (14324,20868) before and between blows (`S1-fight7-blows-north`) | 0 |

- **No drownings.** Across the session the log has 0 lines with `shape 347` (CLRWATER) and no `I_resetRef` on item 1 or on any zombie.
- **Survivors.** All four zombies were alive at their last read.
- **Hp.** The Avatar's hp stayed 30, because he was invincible.
- **Stumbles.** Stumbles still moved him in every fight: 800 units of sliding west in fight 1, and 330 east in fight 4. Each slide ran along the rail and never crossed it. `[INFERENCE]` The north component of each stumble was blocked by the rail. The engine logs no stumble vector, so this rests on the position reads.
- **Caveat.** I never got a zombie knocked north into the rail by a blow of mine. In fight 7 it kept stepping south. "Zombies don't drown" rests on:
  - zombie 127 standing on the rail line at y 20544 under its own movement;
  - the 0 water events;
  - the static check below.

**S1d West shore.** This is the rail along x (11263,11295].
- **Kith 3.** He walked south from (10144,16050), and trigger 7749 fired at (10144,16578), hatching kith 129.
  - After a positioning teleport to (11150,17000) he walked east and stopped at (11226,16972) (`S1-west-shore-walk-E`).
  - The kith attacked from the west, at (11108,16956): 20 blows in 35 s.
  - He ended at (11258,16972), with his body's max x 5 short of the rail face at 11263 (`S1-west-shore-kith3-fight`).
- **Spider 7.** He walked east along y 19560, and trigger 19291 fired at (9916,19560), hatching spider 130.
  - After a teleport to (11150,19500) he walked east and stopped at (11254,19500).
  - The spider struck 9 times from (11184,19504), and he ended at (11262,19500) (`S1-west-shore-spider7-fight`).

**Static cross-check** (`exact_reach.ExactReach` on my copy of FIXED `6abe1497`, Map 10, step 16, globs expanded, level 0):
- I looked for every standable position whose body overlaps z-0 water and which is 8-adjacent to a standable dry position. There are 566.
- **All of them lie on the north shore (y ≈ 15360) or the east shore (x ≈ 15360).**
- There are none on the south or west shore. The north and east shores are the two the commit leaves unrailed by design.

## L Log hygiene: PASS

`/tmp/claude-1000/vmon4/lv_run.log` has 8,673 lines, covering 1 load and about 30 minutes of play.
- **`Cycle in paint`: 0.** That includes the 7 fights pressed against the new rails.
- **`failed to set stats`: 0.** There were no error or assert lines and no crash.
- **WARNINGs (47):**
  - 41 ANIMLOCK, from zombies 131 (24) and 132 (17);
  - 1 `Invalid procid N in waitlist`;
  - 1 MIDI transition;
  - 4 GUI start-up lines.
- **Hatches:** 8 `event 7 @ 0481` lines, one per trigger walked into, plus one repeat (finding 1).

## Findings outside the brief

1. **Wave 1's trigger fired a second time within visit 1, and hatched nothing.**
   - Trigger 18724 logged `event 7` again (log line 4957) when fight 3 took the Avatar back onto the pier's foot.
   - `findShape 872` still listed only 127 and 128.
   - So the one-shot holds on the Lake as it did on Map 11 last round.
2. **On the east route, golem 1 pins the Avatar before box b.**
   - In run C, three walks toward box b with golem 126 alive and striking stalled at (3336,2484), just south of the box: every blow's stumble cancelled the walk.
   - In play, golem 7 will usually hatch only after golem 1 is dead, or when a player swings north round it.
   - This is not a defect, but it is why G1b was shown from the north.
3. **`Damage: N` is logged for an invincible Avatar.** Lines such as `received hit from 124 (dmg=16,type=4) Damage: 16` appear while `objectInfo 1` reads hp 30. This is a log-reading trap, not a game defect.
4. **The test estate took 393 s, not ~7 s** (as in round 3). `test_monster_eggs` reports 421 passed, where the commit message says 420/0.

## Harness anomalies

- **The first walk after a teleport or a console attach often moved ≤ 104 units or not at all** (the Avatar turning, `[INFERENCE]`). A second burst then moved normally. This is noted only because it made positioning walks take two calls.
- **The console stayed open once** after two unanswered `objectInfo` reads (a cell timeout), and the world was paused until I closed it. Nothing I judged fell inside that pause.
- **Setup raced Main's `integrate.sh --record`** (Setup above). I copied only after its harness step had landed and the hashes matched.

## Disk changes

- This report.
- `docs/playtest-2026-10-12-monsters4/`: 18 plates.
- Scratch only, in `/tmp/claude-1000/vmon4/`:
  - game copy, binary copy, engine-data copy and ini;
  - saves and `sp/base.sav`;
  - `lv_run.log`, `estate.log`, `trace.txt`, the `sp/` frames and `py/vm.py`.
- I stopped my own ScummVM. Xvfb :92 was already running; I reused it and did not kill it.
- Nothing in source, maps, the fork, `shared/`, `~/lv-checkpoints`, TODO or HANDOFF was changed.

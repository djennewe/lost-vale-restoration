# Playtest 2026-10-12: LV monster eggs, round 3 (fast-area triggers, one-shot, Lake rails, lane harpies)

This is the verifier pass on main `26dc98b` (18bea87 merged), fork `e48f8716`.

**Setup**
- Display and window: Xvfb :92, ScummVM at 320x200 ×2 (no width/height keys), frameLimit on.
- Binary: a copy at `/tmp/claude-1000/vmon3/bin/scummvm`, sha256 `21f07b14…`, identical to `scummvm-lv/scummvm` (built 2026-10-11 20:33, after the fork commit at 20:31).
- Game data: an isolated copy of `shared/u8-lv-patched` at `/tmp/claude-1000/vmon3/game`.
- Hashes: every one equals `ARTIFACTS.sha256`. That holds for `shared/build`, the harness copy and my copy:
  - FIXED `96d144d8` (both places);
  - EUSECODE `f0a9e709`;
  - U8SHAPES `e0af51ea`;
  - TYPEFLAG `7c1d8454`;
  - ANIM `696dbeb9`.
- Base save: `~/lv-checkpoints/replay1011-s07-m10-ragnar-told-stone.sav`, used read-only. I copied it into my scratch slot and loaded it three times: at start, after the golem death, and after the first shore drowning.
- Fresh maps: the save is on Map 10, so I never judged Map 10 until I had left it and come back. Every map I tested was entered from a different map. On each arrival I checked the egg count with `findShape 500`: Map 11 had 17, Map 10 had 10, Map 13 had 4. These match the shipped table, and every egg is frame 1.

**Cheats and debug aids used:**
- **`Cheat::toggle`**, and **`Cheat::toggleInvincibility`**. Invincibility was on for almost the whole session, with two exceptions:
  - It was off on the first golem-6 approach, before I had enabled it, and the golem killed the Avatar.
  - It was off for about 4 s on Map 13, run 1, so he would take harpie damage for the rest-point test.
- **`MainActor::teleport`**, used for positioning short of every trigger, always followed by a walk in. One teleport went to Map 11 by mistake (a helper default) in the middle of P3. I went back to Map 10, which reloaded fresh, and restarted wave 1.
- **`MainActor::toggleCombat`**, and **`Ultima8Engine::loadGame`**.
- **Debug flags:** `debugflag_enable Object` and `debugflag_enable Actor`. The `Actor` flag is what prints the `received hit` and `[COMBAT n]` lines.
- **No item cheats and no `Item::grab`.** The Avatar fought unarmed: all his blows log `type=1`.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| P1 | Map 11: each golem, seeker and daemon hatches inside the fast area and attacks unprovoked, with 0x800 kept | **PARTIAL**. Seekers 2, 8 and 9, golems 5 and 6, and daemons 3, 10, 11 and 12 PASS. Daemon 13 hatched and closed to striking range, but I left before it landed a blow. **Golems 1 and 7 hatch behind a rock wall from their own triggers** (finding 1). 0x800 was set in every read of every hatchling |
| P2 | Leave and re-enter a section doorway: no duplicates within the visit | **PASS** |
| P3 | Pier: waves 2/1/2, the Avatar never knocked into the water, zombies don't drown | **FAIL**. The hatch order 2/1/2 PASS, and the railed pier and deck held for about 40 blows. **The Avatar drowned twice on the open shore beside the pier's foot**, once after walking there. **Three zombies drowned** there (finding 2) |
| P4 | Harpies: both lane harpies on each of 3 runs; the rest point heals with the summit pair asleep; the summit pair hatches at its trigger | **PASS** (caveats in the section) |
| P5 | Map 10 kith and spiders hatch only off the paths, toward them | **PASS**. 5 of 5 negative controls stayed quiet, and 5 of 5 approaches hatched a monster that attacked |
| L | Log hygiene | **PASS with a note**: 0 `failed to set stats`, no crash. All 196 `Cycle in paint` lines fall inside the window after the Avatar drowned |
| Estate | `tools/run_all_tests.sh` | **PASS**: 52/52. It took 372 s, not ~7 s (finding 5) |
| Build | `tools/build_artifacts.sh` | **NOT RUN**: the brief barred build and install scripts. The on-disk hashes match `ARTIFACTS.sha256` |
| Patch | Tracked patch == fork diff | **PASS** (`diff -q` was silent; the fork is unchanged at `e48f8716`) |
| Shapes | `SHAPE_*` / `TYPE_SHAPES` agreement | **Skipped**: no new or renumbered shape IDs. 497 and 498 are retail |

## P1 Map 11, monsters on their own triggers: PARTIAL

**How each was tested:**
- Teleport to a spot 500-900 units on the walk side of the trigger, then walk toward the egg through the trigger's (5,5) box.
- Then read `findShape` and `objectInfo` for the new actor, and watch the `Actor` debug log.
- The Avatar was never in combat mode. His actor flags read `0x1`, `0x9` or `0x401`, and never had 0x800 set. **Every blow he took was therefore unprovoked.**
- **Reading the flags.** ACT_INCOMBAT is 0x800 (`actor.h:403`). Every hatchling read showed `800`, `808`, `c00`, `c08`, `800808` or `800c08`, so 0x800 was set in all of them. Every hatchling's first item flags had 0x2000 (FASTAREA).

| Group | Trigger fired at the Avatar's position | Actor | First read | Attacked unprovoked |
|---|---|---|---|---|
| Golem 6 | (5376,3296) | 124 / 130 | hp 157, `f 0x20e2`, `800c08` | Yes. Run 1, without invincibility: it walked 500 units from its egg and **killed the 30-hp Avatar** (`P1-g6-1`, `P1-g6-avatar-killed`). The redo logged `received hit from 130 (dmg=19,type=4)` (`P1-g6-redo`) |
| Golem 5 | (4608,2308) | 129 | hp 156, `800` | Yes: `dmg=24`, `dmg=25` (`P1-g5-2`) |
| Golem 7 | (3232,3080) | 124 | `f 0x20e2`, `800808` | **Not from the trigger side** (finding 1) |
| Golem 1 | (3404,2636) | 125 | hp 172, `800c08` | **No**: it never came round the wall (finding 1) |
| Seeker 2 | (16384,2780) | 126 | `0x30e2`, `800808` | Yes: `dmg=15`, `Damage: 15` (`P1-s2-2`) |
| Seeker 8 | (17396,2776) | 127 | `808` | Yes: `dmg=14` (`P1-s8-1`) |
| Seeker 9 | (17580,3400), walking east | 128 | `0x30e2`, `800808` | Yes: `dmg=16` (`P1-s9-3`) |
| Daemon 10 | (3740,15698,8) | 131 | `808` | Yes: `dmg=12`, `dmg=16`, `type=29` |
| Daemon 3 | (3490,14708,8) | 132 | `0x20e2`, `800` | Yes: `dmg=15`, `14` (`P1-d3-1`) |
| Daemon 11 | (3400,17566,8) | 133 | `800` | Yes: `dmg=17` |
| Daemon 12 | (4016,18816,8), walking west along the branch causeway | 135 | `0x20e2`, `808` | Yes: `dmg=16` ×2 (`P1-d12-1`) |
| Daemon 13 | (3380,~18184) | 134 | `[COMBAT 134] _target found: 1`, then `_target (1) in range` ×2 | **Not shown.** Daemon 133 was pinning the Avatar, so I teleported away and 134 was destroyed before it landed a blow |

**Negative control (one-shot within the visit).**
- Trigger 13 fired `event 7` a second time on my return (log line 4098).
- No new daemon appeared, because its egg was already consumed.

**An observation, not a defect.** Daemon trigger 10 sits east of the causeway's centre. On a walk down the middle at x 3550, the Avatar crossed its y band without firing it. It fired only at x 3740, which is consistent with "toward each".

## P2 No stacking: PASS

The water doorway (group 4, trigger 9392) is the only doorway trigger left on Map 11.

- **First pass.** It hatched all 5 lizards, 136-140, every one with `f` 0x2000 and 0x800, including 139 and 140 at (10168,15640) and (11756,15796) (`P2-lizards-1st-pass`).
- **Re-crossings with lizards alive.** Twice out and back across the doorway: the trigger stayed `hatched=1`, nothing hatched, and `findShape 806` showed only the original ids (`P2-lizards-reentry`, `-reentry2`).
- **Re-entry after leaving.** I teleported to (9728,9000), and the lizards left the fast area and were destroyed. I came back to (9728,14000) and walked south through the doorway.
  - Trigger 9392 fired `event 7 @ 0481:0080` again.
  - **0 lizards** appeared, and `findShape 500` listed 0 MonsterEggs left on Map 11 (`P2-doorway-reentry-after-leaving`).
- Taken with the daemon-13 re-fire above, every one-shot egg was consumed by its hatch and none hatched twice.

## P3 Lake pier: FAIL

**Hatch order: PASS.** The waves hatched as `event 7` from three separate triggers, in order, on all three visits:

| Visit | Wave 1 (2) | Wave 2 (1) | Wave 3 (2) |
|---|---|---|---|
| 1 | 148, 149 at (13792,19969) and (13856,20056) | 150 at (13888,19096) | 151, 152 |
| 2 | 161, 162 | not re-tested | not re-tested |
| 3 | 124, 125 | not re-tested | not re-tested |

- All of them were at z 8, on slabs.
- Wave 3 fired when a wave-2 blow stumbled the Avatar north into its box (`P3-w2-fight`).

**Railed pier and deck: PASS.** I fought with double-click attacks in combat mode:
- **Wave 1, west lane.** 4 + 12 blows with the Avatar flush against the west rail (x 13760, so his body was 13696-13760). He was pushed south along the pier: x 13760, z 8 throughout (`P3-w1-west-rail`).
- **Waves 2 and 3, west lane at y 18836-19184.** 12 + 19 blows from three zombies. x stayed 13760 and z stayed 8 (`P3-w3-fight`).
- **Deck, north-east corner (14075,18250).** 9 blows: he stayed at (14075,18242,8) (`P3-deck-fight`).
- **The zombies stayed on the slabs.** They stood at z 8, or 16 on the Passage Stone.

**Drownings off the pier's south end: FAIL.** The pier's south end is open onto the shore. The shore is z-0 ground from y 20480 south, and the lake (CLRWATER, shape 347) runs along y ≤ 20479 on both sides of the pier, unrailed. Wave-1 zombies follow the Avatar off the pier, and a blow on the shore throws him into the lake.

1. **Zombie 149 drowned (wave 1, visit 1).**
   - The fight had drifted to the pier's foot, with 149 at (13824,20440,8).
   - The log then shows `Item 23280 (shape 347) … event 6 @ 015B:0080`, then `I_resetRef item=149`. 23280 is the water tile at (13567,20479).
   - No blow on 149 is logged before it, and the Avatar was alive and on the shore.
   - The body persisted, dead, at (1866,5850,0), and was listed on later Map 10 visits.
2. **The Avatar drowned (visit 2), placed by teleport.**
   - He stood at (13640,20560,0) on the shore west of the pier's foot, 80 units from the waterline.
   - `Actor 1 received hit from 162 (dmg=9)`; the attacker was south-east of him.
   - Then `Item 23108 (shape 347) … event 6`, `I_resetRef item=1`, and the Avatar ended at (0,0,0) (`P3-shore-west`, `P3-avatar-drowned-shore`).
3. **The Avatar drowned again (visit 3), walking in.** This time there was no positioning teleport after the map hop:
   - He walked onto the pier, hatched wave 1, walked back off the pier's south end, then west and north along the shore to (13520,20580,0).
   - Zombie 124, at (13500,20700), hit him: `dmg=6`.
   - The stumble threw him about 64 units north. The log shows `Item 2133 (shape 347)` (water at (13567,20479)), then `I_resetRef item=1`, and he ended at (0,0,0) (`P3-walked-shore`).
4. **Zombies 162 and 124 drowned after the Avatar went into limbo.**
   - 162 had been on the pier at (13820,20372,8) and drowned in tile 3847; 124 had been on the shore at (13442,20652) and drowned in tiles 12384 and 6350, at x 13311 and 13183, y 20479.
   - With no target they wander, and the unrailed shoreline is beside them.

So the rails do what they claim on the pier and the deck. The hazard has moved to the pier's foot, where wave 1's fight naturally drifts: the zombies come at the Avatar from the pier, and his stumbles carry him onto the shore and north-west. Confidence is high for 2-4, since the log sequence is the same as finding 2 of the previous round. How zombie 149 got into the water is `[INFERENCE]`: no blow on it was logged.

## P4 Map 13 harpies: PASS

**Lane pair, 3 of 3 runs.** For each run I hopped Map 13 → Map 10 → Map 13, so the map was fresh with 4 eggs, then walked north from (4031,4415,84):

| Run | Trigger | Harpies | First read |
|---|---|---|---|
| 1 | 29688 | 153 and 154 | at (4000,3200) and (4192,3200), z 96, `800808` |
| 2 | 24435 | 157 and 158 | z 99, `800c08` |
| 3 | 1200 | 159 and 160 | z 98, `800c08` |

- Both harpies logged `_target found: 1` on every run (plates `P4-r1/2/3-lane-hatch`).
- Runs 2 and 3 walked x 4043-4051; the previous round's run 2, which lost a harpie, walked x 4031.
- Run 1 took `dmg=9` and `dmg=6`, leaving him at hp 21.

**Rest point.**
- I left the lane pair behind with a teleport (they were destroyed out of the fast area), then teleported to (4031,2560) and walked north.
- **Healing:** at (4031,1912,112) hp went 22 → 24 in 104 s. At (4031,1608,112), 55 units past `HARPIE_REST` (4031,1663,112), it went 24 → 26 in 94 s.
- **Summit pair asleep:** the whole time there was no `event 7`, the 2 summit eggs remained, and `findShape 873` was empty (`P4-r1-rest-point`, `-rest-point-after`).
- `HealProcess` heals anywhere. The rest point's claim is "nothing wakes here", and that held.

**Summit pair.** Walking on north, trigger 27399 fired at (4223,1216,116):
- 155 and 156 hatched on the summit, at (3584,282,120) and (3428,332,120), both 0x800 with `f` 0x2000.
- 155 logged `_target found: 1`, and 0 eggs were left (`P4-r1-summit-hatch`, `-summit-after`).
- I did not see a summit harpie land a blow.

## P5 Map 10 kith and spiders: PASS

For each group I walked once across the old trigger's centre and once toward the egg through the new trigger. The builder describes the old triggers as standing on the ways, so their centres stand in for "the main paths".

| Group | Negative: across the old trigger | Positive: toward the egg | Result |
|---|---|---|---|
| Kith 3 | (9700→10724, 15904): no hatch, `findShape 76` empty | south from (10144,16050) | 141, hit for 14 |
| Kith 4 | (15950→16910, 21216): none | west at y 21696 | 142, `dmg=15/13` |
| Spider 5 | (9350→10166, 14336): none | north-west from (9500,14000) | 143, hits for 1 |
| Spider 6 | (16512, 11500→12332): none | south-west from (16500,11900) | 144, hits for 1 |
| Spider 7 | (9300→10260, 19776): none | east at y 19560 | 145, hits for 1 |

- Every hatchling was in the fast area with 0x800 set.
- Plates: `P5-*-neg-way`, `P5-*-pos*`.
- **Caveat:** the old spider-7 line, y 19776, passes only 84 units south of the new box, whose y range is (19372,19692]. A player wandering slightly north of that way fires it.

## L Log hygiene: PASS with a note

`/tmp/claude-1000/vmon3/lv_run.log` has 14,291 lines, covering 3 loads and about 65 minutes of play.
- `failed to set stats`: 0. No crash, no error or assert lines.
- **`Cycle in paint`: 196.** All of them are at log lines 13225-13425: 188 are `476 -> 872` and 8 are `580 -> 872`. They fall entirely inside the window after the Avatar drowned on the shore (visit 2), while he was in limbo at (0,0,0), and they stopped at the reload. No other window logged any. Neither 476 nor 580 is in Map 10's FIXED items or globs, so the pair is `[INFERENCE]` the drowned state's own items against a zombie.
- **WARNINGs:**
  - 33 × ANIMLOCK, all from monsters in combat;
  - 4 MIDI transitions;
  - 3 `Invalid procid N in waitlist`;
  - 4 GUI start-up lines.

## Findings outside the brief

**1. Golems 1 and 7 hatch behind a wall from their own triggers.**
- **The wall.** A run of shape 26 (footprint 4×1×6) stands at y 2560, x 1536-3456, so it fills y (2528,2560] at z 0-48.
- **Which side everything is on.** Both eggs are north of the wall: golem 7 at (2688,2496) and golem 1 at (3040,2048). Trigger 7 at (3232,3040) is south of it. Trigger 1 at (3520,2592) sits just past the wall's east end.
- **Golem 7 (124).**
  - It hatched in the fast area with 0x800, and found its target.
  - It then milled north of the wall for more than 20 s, at (2600-3400, 2150-2510).
  - From (3320,2512), north of the wall, it struck the Avatar at (3404,2636), south of it: `dmg=24`.
  - It attacked properly only after he went round the wall's end to (3520,2336) (`P1-g7-3-behind-wall`, `P1-g7-4`, `P1-g1-g7-north`).
- **Golem 1 (125).** It stayed north of the wall as well. It never reached him, and it was destroyed when I left.
- **Path lengths.** A flood with `exact_reach` (ExactReach, level 0, step 32) gives trigger-to-egg walking distances of 544 for groups 1, 5 and 6, against 1,344 for group 7, whose straight line is 769.
- **Cause.** `[INFERENCE]` The builder's checks (`wakes_at_once`, the seek-square test) measure the straight distance and ignore the wall, while the monster's direct approach does not route round it. Confidence: high that the wall separates them (the plates and the flood); the code-level cause is unverified.

**2. The Lake's drowning hazard has moved to the shore at the pier's foot (P3).**
- Two Avatar drownings and three zombie drownings, all against the shoreline y ≤ 20479 within about 640 units west of the pier.
- One of the Avatar drownings was reached on foot with no positioning cheat.
- A rail, or a dry apron, along the shore at the pier's foot would cover the spot where wave 1's fight ends up.

**3. A drowned zombie's body outlives the map.** Zombie 149 drowned on Map 10 visit 1 and stayed dead at (1866,5850,0), with item map field 0. `findShape 872` still listed it on later Map 10 visits after hops through Map 13. It is harmless as far as I saw.

**4. Balance (unchanged from round 2).** Without invincibility, golem 6 killed the step-7 Avatar (30 hp) within seconds of hatching (`P1-g6-avatar-killed`). The golems hit for 15-25 a blow.

**5. The test estate takes minutes, not ~7 s.** `run_all_tests.sh` took 372 s, with the game running alongside:
- `test_route_reach` 67-83 s;
- `test_monster_eggs` 65-70 s;
- `test_map39_south_edge` 30 s.

The first attempt hit the tool's 300 s limit. CLAUDE.md's "~7s" is stale.

**6. Minor.**
- Lizard 137 struck lizard 139 three times (friendly fire).
- Lizard 138 died to `received hit from 1 (dmg=150,type=4)` while the Avatar was not attacking. The cause is unknown `[INFERENCE]`, possibly a landing.
- A hatchling the Avatar teleports away from is destroyed (FLG_FAST_ONLY). Because the eggs are one-shot, it is then gone for the rest of the visit. That is by design (see the module note), and is noted only because it removed golem 1 and daemon 13 from this test.

## Harness anomalies

- **The first golem-6 run logged no blows.** The `Actor` debug flag was still off, and the pause/death book was up by the time I looked (`P1-g6-2`).
- **A helper defaulted to `m=11`.** One Map 10 positioning teleport went to Map 11; the plate taken there was deleted.
- **Walks under attack stall.** Short `W` legs sometimes moved the Avatar south, because stumbles override the walk.
- **Combat mode slows walking** to single steps. I toggled it off to walk between fights.

## Disk changes

- This report.
- `docs/playtest-2026-10-12-monsters3/`: 67 plates.
- Scratch only, in `/tmp/claude-1000/vmon3/`:
  - game copy, binary copy, engine-data copy and ini;
  - saves, and the scratch copy of the base save at `sp/base.sav`;
  - `lv_run.log`, `estate.log`, the `sp/` frames and `py/vm.py`.
- I stopped my own ScummVM. Xvfb :92 was already running; I reused it and did not kill it.
- Nothing in source, maps, the fork, `shared/`, `~/lv-checkpoints`, TODO or HANDOFF was changed.

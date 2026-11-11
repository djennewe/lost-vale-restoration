# Playtest 2026-10-11: the Water Zombie (872) and the Harpie (873)

Verifier pass on art-track contract 9 (main `d7278d0`). Ran on Xvfb :92 with ScummVM at 320x200 ×2, frameLimit on and music on. The binary was a pinned copy of `scummvm-lv/scummvm` (sha256 `f55ef3e2…`, built 2026-10-11 18:07). It ran an isolated copy of `shared/u8-lv-patched` under `/tmp/claude-1000/vmon/`. The loaded artifacts matched `ARTIFACTS.sha256`: EUSECODE `02fa9d9f`, U8SHAPES `e0af51ea`, TYPEFLAG `7c1d8454`, ANIM `696dbeb9`, FIXED `cc7410a1`. The base save was `run1010-s07-m10-ragnar-told-stone.sav`. Every test hopped Map 10 → 13 → 10 first, so each map was a fresh load.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| Z1-hatch | Walking into a Lake egg on Map 10 hatches a water zombie | **FAIL**: nothing hatches with the shipped bytes (finding 1) |
| H1-hatch | Walking into a harpie-zone egg on Map 13 hatches a harpie | **FAIL**: the same cause |
| Z1-art | The zombie draws drowned blue-cyan in every direction | **PASS** (diagnostic hatch; see "Method") |
| Z1-look | Look says "water zombie" | **PASS when the objId allows it**: hijacked at objId 149 (finding 2) |
| Z1-combat | Walks to and attacks the Avatar, deals damage, can be killed, death plays, leaves a corpse | **PASS**, with a caveat: it only attacks once provoked (finding 4) |
| Z1-stats | hp/stats come from the `u8monsters.ini` row, not engine defaults | **PASS** |
| H1-art | The harpie draws in all directions, flaps | **PASS** |
| H1-look | Look says "harpie" | **PASS when the objId allows it**: fails at objId 149 (finding 2) |
| H1-combat | Attacks with talons, deals damage, dies, leaves a corpse | **PASS** |
| H1-frames | Note wrong-facing frames | **CONFIRMED** for the west-facing (dir 6) attack. Dir-7 death: **PARTIAL** (see H1) |
| H1-stats | Stats from the ini row | **PASS** |
| INI | `u8monsters.ini` is read from the game dir | **PASS**: strace shows the game-dir file opened |
| INI-neg | Negative control: with no ini, "failed to set stats" appears | **NOT DEMONSTRATED**: variant built (`gameE`), never run (budget) |
| L | 0 "Cycle in paint", no crash | **PASS**: 0 cycles, 0 "failed to set stats", no crash in 4 logs |
| Estate | `tools/run_all_tests.sh`, `build_artifacts.sh` | **NOT RUN**: the brief barred build/install scripts, and the estate run was skipped (budget) |

## Method

**Run A (shipped bytes):**
- Map 13: walked the climb lane north along x 4096 from y 1920 to 624, at z 112-120, past all four harpie eggs.
- Map 10: walked the pier north from (13887,20700) to 18268, between the Lake eggs.
- `findShape 873` and `findShape 872` returned 0 both times. The eggs were present, `findShape 500` listed all of them.
- Plates: `A1-m13-harpie-lane-no-hatch`, `A2-m10-pier-no-hatch`.

**Runs B-D: diagnostic copies of `FIXED.DAT`, in `/tmp` only.**
- **Hatch path.** Each copy adds a MONEGG trigger: shape 73, quality 2, class 0x481. The retail mechanism is unchanged, so `MonsterEgg::hatch` → `loadMonsterStats` runs exactly as it would in the game.
- **B (shipped egg positions):**
  - Map 13: a trigger on the lane at (4096,1600,116).
  - Map 10: a trigger on the pier at (13887,19900,8). Only the zombie eggs were regrouped (monId 1) so they hatch alone.
- **C and D (open ground):** extra eggs on the open south shore of Map 10. In D, a ghoul (142) egg and a torax (120) egg as donor controls.
- **Map hashes.** `MapArchive` round-trips the shipped `FIXED.DAT` byte-for-byte (`cc7410a1`). The variants hash `5522f729…` (B), `e94dbc3f…` (C) and `d984c501…` (D). They are not shipped bytes.
- **Debug actions.** For combat and plates I used `Actor::hold` to place monsters, `Cheat::maxstats`, `Cheat::equip` (Deceiver), invincibility, and `debugflag_enable Actor`, which logs every hit.

## Z1 / H1 hatch: FAIL

`MonsterEgg` derives from `Item`, not `Egg` (`world/monster_egg.h:31`). `CurrentMap::addItem` registers only `Egg`s with the `EggHatcherProcess` (`current_map.cpp:270`). Proximity therefore never hatches a shape-500 egg.

In U8 they are hatched by MONEGG (class 0x481):
- MONEGG is an UnkEgg with quality 2.
- Its `hatch()` searches a 3584-unit area for shape 500 and calls `MonsterEgg::hatch` on every egg whose `mapNum>>3` equals the trigger's `mapNum & 0x1F`.

Retail places 179 such triggers, all of them in `U8SAVE.000`'s `NONFIXED.DAT`:
- maps 3, 4, 5, 7, 8, 14, 15, 21, 28, 31, 37, 41, 44, 45, 47, 49, 50, 51, 57 and 62;
- 0 of them are in `FIXED.DAT`.

Maps 10 and 13 have **no** shape-73 q2 egg, in `FIXED.DAT` or anywhere else. The only UnkEggs there are quality 283/294/299/307 and 297.

This is not new with 872/873. The 2026-09-18 Map 10 walk saw the same eggs fail to hatch when they spawned ghouls. Every LV monster egg on maps 8-18 that is not covered by a retail trigger is inert:

| Map | Shape-500 eggs | MONEGG triggers |
|---|---|---|
| 8 | 19 | 0 |
| 9 | 1 | 0 |
| 10 | 10 | 0 |
| 11 | 17 | 0 |
| 13 | 4 | 0 |
| 18 | 1 | 0 |

## Z1 Water Zombie: art, look, combat, stats

- **Art.** `Z1-walk-attack-8dir-sheet` puts the Avatar at each of the 8 compass points around a zombie that is in combat. The zombie walks to him and attacks in all 8 directions, drawn the same drowned pale blue-cyan in each. Idle and loiter frames: `Z1-loiter-sheet`. Beside a ghoul: `C1-zombie-vs-ghoul`.
- **Look.** A click on objId 148 ran `calling usecode event 0 @ 0368:0080` and barked "water zombie" (`Z1-look-water-zombie`). The corpse barks it too.
- **Combat.** The zombie hits the Avatar for logged damage of 6-12, inside the ini's 6-12:
  - `Actor 1 received hit from 148 (dmg=9,type=1) Damage: 9`
  - `… (dmg=10) Damage: 10`
  - `… (dmg=11) Damage: 11`

  Those three killed a 30-hp Avatar in the first fight.
- **Death.** It was killed with a sword: hp 41 → 0, flags 0x1000, final frame 219. The death collapse plays (`Z1-death-sheet`). The corpse stays on the ground (`Z1-corpse`).
- **Stats.** Seven zombie hatches rolled hp 41, 45, 47, 48, 49, 50, 50 and dex 14-16. Every one had ac 15, defense 0x50 and align 8 / enemy 6 (that is, 0x68), and no hatch logged "failed to set stats".
  - **Donor control.** A ghoul hatched from an egg in the same session read hp 35, dex 16, ac 15, def 50, align 8, enemy 6.
  - **Why this proves the ini.** `ultima8.dat`'s `u8monsters.ini` has no shape-872 row, so non-zero stats can only come from the game-dir file. strace of run A shows `openat(".../vmon/game/u8monsters.ini") = 17` after `ultima8.dat` (fd 12).

## H1 Harpie: art, look, combat, stats, frames

- **Art.** It flaps in every direction (`H1-walk-8dir-sheet`). In `H1-attack-8sides-sheet` the harpie is held on each of the Avatar's 8 sides while it attacks. Beside a torax: `C2-harpie-vs-torax`.
- **Look.** A click on objId 148 ran `event 0 @ 0369:0080` and barked "harpie" (`H1-look-harpie`).
- **Combat.** Talon hits for dmg 7-14, inside the ini's 7-14:
  - Map 13: harpie 150 hit the unarmed Avatar 4 times (13, 12, 7 and 10) and landed `Damage: 10`. A second engagement there killed him.
  - Map 10: `received hit from 149 (dmg=10) Damage: 10`.
- **Death.** The death plays, rearing and then dropping flat (`H1-death-sheet`), and leaves a corpse at frame 218 with flags 0x1000.
- **Stats.** hp 42, 43, 49, 50, 52 and dex 8-12, with ac 28, def 0x82 and align 4 / enemy 2 (0x24). The donor torax hatched alongside read hp 50, dex 10, ac 28, def 82, align 4, enemy 2.
- **West-facing (dir 6) attack: confirmed.** In `H1-attack-facing-west-dir6-big` the harpie stands east of the Avatar and attacks west, away from the viewer. Its ready frames show the back of its head. The lunge and strike frames turn its face and chest toward the viewer.
- **Dir-7 death: PARTIAL.** `H1-death-facing-nw-big` was meant to show the harpie dying while it faced north-west (it stood south-east of the Avatar). It shows her face and chest toward the viewer through the last combat frames, and then the drop. I did not establish the engine direction frame by frame, so this is inconclusive.
- **Death drop.** The falling frames fold the wings and drop the body to a flat corpse, with no visible pop. The smaller "dropping" phase is not noticeable at 1x.
- **Untested.** The `type=meat` treasure: I did not open a corpse.

## Findings that were not part of the plan

1. **The LV monster eggs never hatch** (Z1/H1 above). The fix belongs in the map builders: place a MONEGG trigger (shape 73, quality 2, `mapnum` = group, `npcnum` = hatch box) near each egg group. With such a trigger the art works.
2. **The fork's LV npcnum dispatch hijacks monster usecode.**
   - `Item::callUsecodeEvent` (`world/item.cpp`, the "Lost Vale: FIXED.DAT NPC items with npcnum dispatch" block) sends any non-egg item with `_npcNum != 0` to class `_npcNum + 1024` if that class is non-empty.
   - `MonsterEgg::hatch` calls `setNpcNum(objID)`, and hatched monsters get objIds below 256. So every hatched monster dispatches to a class in 0x400-0x4FF: the retail NPC classes and the egg classes. 124 of those are non-empty.
   - **Observed.** Harpie objId 149 → class 0x495 MORDHAT (an egg class whose only event is hatch): a click dumped the item and ran no look. Zombie objId 149 failed the same way. ObjId 148 → 0x494, which is empty, so its look worked.
   - **Wider risk.** Other objIds run egg `enterFastArea` (0xF) handlers, or NPC dialogue classes, on a monster. This hits retail monsters on LV maps too.
3. **The shipped egg positions misplace both monsters, even once hatched** (run B).
   - **Zombies drown in their own lake.** Four of the five Lake zombies hatched, and the fifth, at (12800,19456), produced nothing. The one that moved walked into CLRWATER (class 0x15B, shape 347, event 6). The engine then logged `I_resetRef` and moved it to map 0 (6548,4675) with `ACT_DEAD` set. The rest stand frozen in the water.
   - **Harpies hatch inside the cliff face.** All four harpie eggs (z 98-110) sit beside or below the lane (z 112-120).
     - 148 and 151 hang inside the cliff course, and a click hits the cliff piece instead (shape 32).
     - 149 fell and died on landing: `received hit from 0 (dmg=52,type=180)`. Same outcome on two runs.
     - 150 fell, took 7 damage and then attacked through the cliff base, where the cliff occludes the fight (`H2-m13-cliffbase-attack-sheet`).
4. **Both monsters are passive until provoked.** The eggs carry activity 0 (loiter): 292 of the 418 retail eggs use 1 (combat). On open ground a zombie and a harpie loitered beside the Avatar for 20 s and more without attacking. Each fought back only after it was hit, or after taking fall damage.
5. **Harpie armour.** Torax armour 28 / defense 0x82 meant a max-stats Avatar's starting sword never damaged one ("No damage" every time). The Deceiver did 1-2 per hit. This comes from the donor row as designed, but it makes the harpie very hard to kill with early gear.

## Harness anomalies

- The window came up at 320,200 instead of the requested 480,300 once, and `chord()` failed until a manual `windowmove`.
- Click-to-look on a wandering zombie needs a screen detector (cyan centroid). `Actor::hold`'s `px` is biased by about +40 window px in y.
- `Cheat::equip` gives no console reply (it closes the console).

## Disk changes

- This report.
- `docs/playtest-2026-10-11-monsters/`: 28 files. Stills are in `-1x.png` and `-2x.png` pairs; frame sheets are at the window's 2x scale.
- Scratch only: `/tmp/claude-1000/vmon/`, holding:
  - `game*` copies; B-D carry the modified FIXED, and E has no ini;
  - the logs `lv_run-{A,B,C,D}.log` and `strace-A.txt`;
  - the recordings in `rec/`.
- Nothing in the repo source, the maps, `~/lv-checkpoints` or `shared/` was changed.

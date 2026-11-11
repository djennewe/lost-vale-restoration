# Single-build replay, leg 5: steps 12-15 done (elixir, Key q170, the climb, both 878 halves, the ceremony; Shield 879 restored, Avatar cured) (2026-10-18)

Leg 5 continues from leg 4's bank `replay1017-s12b-m10-root-given-brew-waited-hp30.sav` (`docs/playtest-2026-10-17-replay-leg4.md`), on the same pinned game copy. The session stopped at the request budget, standing in the Sacred Circle just after the ceremony. It did not stop on a defect.

## Build pinned (re-checked)

- **Game copy.** `/tmp/claude-1000/replay1017/game` was not re-copied or modified. `sha256sum -c ../pinned.sha256` gave OK for all six files at the start and at the end: EUSECODE `2e3b71c2…`, FIXED (root and `STATIC/`) `8db11ee3…`, U8SHAPES `efb16af1…`, TYPEFLAG `d26d1531…`, ANIM `696dbeb9…`.
- **Binary.** `/tmp/claude-1000/replay1017/bin/scummvm-console`, the same file as legs 1-4. The log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: 84615e29d097543ed69da844fbc3948f, 1528891 bytes`.
- **Ini.** `scummvm.ini` unchanged: 320×200, `scale_factor=2` (window 640×400). Xvfb `:95`.
- **Log.** `/tmp/claude-1000/replay1017/lv_run5.log` (14,893 lines, four process starts appended to one file). The trace is `trace5.txt`.
- **Cheats: 0.** `Cheat` appears 0 times in the log. The console was used only for `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object` and `saveGame`. Every move, drag, menu pick and conversation was player input.
- **Deaths: 2. Reloads: 3.** All three reloads were of `replay1017-s13b-m13-pre-lane-z80-hp30.sav`, by stopping the engine, copying the bank to slot 1 and relaunching with `--save-slot=1` (no `loadGame`). `debugflag_enable Object` was re-sent after each start.
  1. Reload 1, hp 9, alive. The two lane harpies (873) took the Avatar from 30 to 9 in about 4 s while he stood at the trigger (finding 1).
  2. Death 1. A lure down the lane and the ramp to the Map 13 ground floor. Harpie hits took him 30 → 20 → 10, and he died while trying to circle the harpie (`f1-death-harpie-ground`).
  3. Death 2. The same lure again. He was stun-locked on the ground floor at hp 5 (`f1b-death2-harpie-ground`).

## Outcome

- **Furthest step completed: 15.** shieldFixed `[0409]` = 1, avatarPoisoned `[0404]` = 0, inShadeScene `[0452]` = 0. The restored Shield is **shape 879** (item 2680, class TYPESACR, q83, `f: 0xc`, in the pack). `findShape 878` and `findShape 828` both read 0.
- Steps 16-18 were NOT DEMONSTRATED (budget).

## Verdicts

| Step / segment | Verdict | Evidence |
|---|---|---|
| **12: elixir** | **PASS** | Ezrekal (116) was chased down around the stockade, and the strike logged `event 1 @ 0474:034A`. Menu "Can you help me? / Have you made the elixir? / bye" (`s12a`) → **Have you made the elixir?** → "Yes, I have. Take it to him now you can." (`s12b`). `[0723]` = 1, `[0426]` = 1. Elixir 20216 (**shape 868**, TYPEELIX) is in the pack, and weight went 50 → 60 |
| **12: Tyorvi, drunk path, Key** | **PASS** | He was at Hoskuld (7627,7483), and the strike logged `event 1 @ 0473:0354`. iAmDrunk `[0724]` read 1. Picks, read from the screen: **I have something for you from Ezrekal.** (`s12c`, `s12d`) → **It is an elixar.** (`s12e`) → **It is a potion.** (`s12f`) → **It will heal your dreams.** (`s12g`). The menu then offered "Just try it, please." and "Shut up and drink it!" together (`s12h`) → **Shut up and drink it!** → "All right, all right! Have to shout you do not! Try it I will." (`s12i`) → "Hmmm, taste too bad that did not…" (`s12j`) → menu "May I have the Key to the Clouds? / bye" (`s12k`) → "Well, treacherous it is, but brave you are… Here, here the Key to the Clouds is." (`s12l`). Key 18739, shape 82, **q170**, `f: 0xc`. `findShape 868` = 0 (the elixir was drunk), and givenTea `[0425]` = 1. All of this was **one talk**: on the drunk path, "Just try it" is the refusal branch (`lv-patched/TYORVI.UNK:2294-2372`), so the 10-11 two-talk order is not needed |
| 13: Map 10 → Map 13 | **PASS** (finding 3) | Hoskuld → S along x 7047 (an erode-0 field; at erode 1 the terrace is cut off) → the terrace. The arrival pad 206 (7168,23296) does not send. The **active teleporter is 207 at (7168,24064,8)**, south of the gate, through its east lane (x 7168-7295) → **Map 13 (4096,11824,0)** (`s13a`) |
| **13: EggCloudCliffs** | **PASS** | A N walk logged `event 7 @ 05A8:0080`. Bark 1: "The ancient handholds carved into the cliff face glow faintly as I approach. This must be the path." (`s13b`). Bark 2: "The wind howls around me, but the handholds hold firm. The Zealans built well." (`s13c`). attemptedCliffs `[040F]` and climbedCliffs `[0407]` both read 1 at the first query; there was no lag this time |
| 13: lower climb | **PASS, 0 falls** | A walk-gait field from the pinned FIXED (erode 0): N along x 4096 to z 60 → E along y 7776 → N along x 5128 to the lane plaza (5128,4776,80) (`s13d`) |
| **13: lane harpie pair (873)** | **PASS (they hatch and attack); FAIL as a fair fight for this Avatar** (findings 1, 2) | Trigger `0481` at (5119,4479) hatched 160 (hp 43) and 161 (hp 45) at their egg spots (5023,3999) and (5183,3967) on every crossing from the south. Unarmed with 30 hp, the Avatar cannot fight them: 2 deaths and 3 reloads. **What got through:** the fast-area mechanics. A walk from (5232,4640) N into the box logged the hatch, then a 3.0 s run S along x 5232 stopped at (5232,6144). Both harpies were destroyed (`findShape 873: 0`), while the trigger stayed spent. The walk back N through the box logged no `event 7` and no harpie, and he reached the summit at hp 30 (`s13e`) |
| 13: summit pair | **PASS (hatch)**; the evasion was partial | Trigger 2 `0481` (4863,1663) hatched **only one** harpie (162, at (4479,1847)), the same as 10-11 monsters2 finding 4. The fast-area trick failed here: a wall at x 5272, y 1368 blocked the run east. The harpie closed and took hp 30 → 6. A run W/S down the strip reached teleporter 209 → **Map 17 (4608,9984,0) at hp 7** (`s13f`) |
| **13: both Shield halves (878)** | **PASS** | There are no skeletons beside the halves on this build. Drag 1: half 31797 (878 f0 q81) at (4259,7199), from (4332,7144,8): `Dragging item 31797` → `Dropped item in backpack`, w 60 → 90 (`s13g`). Drag 2: half 16623 (878 f1 q82) at (3559,3311), from (3472,3244,8): `Dragging item 16623` → `Dropped item in backpack`, w 90 → 120 (`s13h`). Both read `f: 0xc` |
| 13: rest on Map 17 | — | Map 17 has no monsters. hp went 10 → 30 in 20 min of idle play (1 hp/min) |
| 13: Map 17 → Map 13 → Map 10 | **PASS, hp 30** | Walked to teleporter 208 (4608,11008) → Map 13 pad 208 (5119,2303,120). A 25-round run field went S down the lane, the bottom plaza and the ramp to teleporter 206 → **Map 10 (6960,23504,8)**. Crossing T1 from the north logged `0481`. Nothing caught him (`findShape 873: 0`). EggReapply `05B2` fired on arrival, and both halves and the Key were still in the pack (`s13i`) |
| 14: to the Sacred Circle | **PASS** | An erode-0 field from the terrace: N, NE, E along y 20968 (south of the lake), NE → (20444,17788). Then two N walks into egg 28745 (20480,17152, ±256) |
| **14-15: the ceremony** | **PASS** | `event 7 @ 05A5:0080`. The elders' quarrel (`s14a`). Ezrekal: "Can't you do something to stop them?" → menu "Can't you two get along!? / Let's be reasonable!" (`s14b`) → **Let's be reasonable!** → "Yes, Priestess. / No, it is mine now." (`s14c`) → **Yes, Priestess.** The halves were laid down (`s14d`) and the shades of Hoskuld and Gunnar spoke (`s14e`). Then "Please, High Priestess. / No, thanks anyway." (`s15a`) → **Please, High Priestess.** |
| **15: state after the ceremony** | **PASS** | shieldFixed `[0409]` = 1, avatarPoisoned `[0404]` = 0, inShadeScene `[0452]` = 0 (read about 100 s after the last pick). **Shield 879** item 2680, TYPESACR, q83, `f: 0xc`, in the pack. 878 and 828 both read 0. Weight went 120 → 90 |
| 16-18 | **NOT DEMONSTRATED** | Budget |
| GHOST 411 follower | **Not seen** | `findShape 411: 0 found` on Map 13, on Map 17 and at the end on Map 10 |
| Log hygiene (`lv_run5.log`) | **PASS for LV code**, with one note | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Unhandled intrinsic`, ERROR and `Cheat`. There are **8 `Cycle in paint`** lines, all `219 -> 875 -> … -> 219` on Map 17 at the half-1 site (finding 4). Map 13 logged 0, with the Object channel on |

## Findings

1. **Severity: high (balance; it blocks a player who has no weapon). The lane harpie pair is a death trap for the replay's Avatar (30 hp, unarmed).**
   - **What happened.** Each harpie hits for about 5-10. A hit interrupts the Avatar's run, so two harpies stun-lock him. Standing in the trigger cost 21 hp in about 4 s. Two lures down to the open ground floor each ended in death.
   - **The design expects a fight.** `build_map_13.py:378-383` says "a player who has beaten the lane pair can stand there and heal".
   - **No leg of this replay picked up a weapon.** Galjeron's sword (420) lies beside Map 9's pad 201 at (13920,14304). Map 11 has another sword at (2591,15199) and the hub axe 419 at (9599,4479).
   - **Blocker: no.** The evasion in finding 2 gets a player through without fighting, but no ordinary player would find it.
   - **Repro.** `replay1017-s13b-m13-pre-lane-z80-hp30.sav`: walk N about 200 units.
2. **Severity: info (mechanics; this is how the climb was passed). A hatched monster is `FLG_FAST_ONLY` (flags `0x20e2`), so it is destroyed when it leaves the fast area. MONEGG (`0481`) re-arms only on its own `leaveFastArea`.**
   - **The MONEGG code.** Its disassembly (`0481` hatch: `mapArray & 0x80` gate, set after hatching, cleared in event 10) and `Item::leaveFastArea` (`item.cpp:1968`) give this rule.
   - **The window.** The trigger's chunk is (9,8). The eggs' chunks are (9,7) and (10,7). With the camera at x ≈ 5232, the chunks with cx−cy ≥ 2 leave the fast area at y ≈ 5900, and chunk (9,8) only at y ≈ 6400. [The numbers come from the `in_fa` port in `py/leg3_helpers.py`. It matched every observed disappearance this leg.]
   - **The recipe.** Hatch from the east side of the lane. Immediately run S about 1500 units to y 5900-6300. Both harpies are then destroyed and the trigger stays spent. Walk back N: the box crossing logs nothing.
   - **Why it matters.** The same mechanics explain monsters2's "summit pair stays asleep" and the replay's vanishing harpies. They also mean any egg monster can be shed by out-running it 2-3 chunks.
3. **Severity: info (route guide drift). The Map 10 → 13 teleporter is 207 at (7168,24064,8), south of the key gate.** Pad 206 (7168,23296) is the arrival point, frame 1. Leg 4's Resume ("Trigger 206 at (7168,23296,8) leads to Map 13") had this backwards. The Avatar walked through the gate's east lane (x 7168-7295) without using the Key; the gate stubs leave both lanes open, as the builder intends (`build_map_10.py:1481-1482,1521-1523`).
4. **Severity: low (paint). Map 17 has a `219 -> 875` draw-order knot beside half 1.** It logged 8 lines while the Avatar stood at (4328-4412, 7064-7148, z 8), next to the 878 f0 half at (4259,7199) among the white columns (875). The vignette-verify passes did not cover this spot. Repro: `replay1017-s13e-m17-both-halves-878-hp10.sav`, walk to (4332,7144).
5. **Severity: info. On the drunk path, Tyorvi offers both "Just try it, please." and "Shut up and drink it!" at once, and the Key comes in one talk.** With iAmDrunk = 1, "Just try it" is the refusal (tyorviPissed, exitConvo). 10-11 leg 4 took it first and needed a second talk.
6. **Severity: info. Only one summit harpie hatched** (162). This repeats monsters2 finding 4 at the other pair.

## Harness anomalies

1. **Console-read overhead is lethal near monsters.** Each `lv.q` costs about 1.5 s of unpaused world time with no movement input: the chord poll, `exit`, and the sleeps. A read-step-read lure loop moves the Avatar slower than a harpie (about 150 u/s). What worked was one decision, then a long continuous hold with no reads.
2. **Short walk presses were dropped again.** A 0.6-0.75 s walk N/W after a `prime()` sometimes did not move him, so the trigger was not entered. I fixed it by reading `pos` and checking the log for `event 7` before the escape run.
3. **Reloads by restart.** `lv.stop()`, then copy the bank to `saves/ultima8.001`, then `lv.start(log='lv_run5.log', slot=1)`, then re-send `debugflag_enable Object` (it sometimes needs two tries).
4. **New kernel-only helpers; `py/` was not edited.** `chase(npc, er)` (approach plus strike), `harp()` (positions of all 873s plus the Avatar's position and hp in one attach), `step_along`, `lure*`, `amapF` (an ASCII reach map of a Field) and `sheet` (contact sheets). I also disassembled `0481` to `/tmp/claude-1000/replay1017/monegg.dis`.

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `replay1017-s12c-m10-elixir-in-pack-hp30.sav` | `51948a77` | Stockade (12751,12591), elixir 868 in the pack, w 60 |
| `replay1017-s12d-m10-cliff-key-q170-hp30.sav` | `43a5ae7a` | Hoskuld (7707,7255), Key 18739 q170, givenTea = 1. **Step 12 done** |
| `replay1017-s13a-m13-arrival-hp30.sav` | `5851afe2` | Map 13 (4096,11880,0) |
| `replay1017-s13b-m13-pre-lane-z80-hp30.sav` | `1f84f975` | Map 13 (5128,4776,80), just south of the lane trigger, no harpies. **Rerun point for finding 2** |
| `replay1017-s13c-m13-summit-lane-pair-evaded-hp30.sav` | `31821672` | Map 13 summit (5084,2596,120) |
| `replay1017-s13d-m17-arrival-hp7.sav` | `37d3bee4` | Map 17 (4608,9984,0), hp 7 |
| `replay1017-s13e-m17-both-halves-878-hp10.sav` | `03afd224` | Map 17 (3560,3156,16), both halves, hp 10 |
| `replay1017-s13f-m17-both-halves-rested-hp30.sav` | `5532885d` | The same spot, hp 30 |
| `replay1017-s13g-m13-summit-pad208-halves-hp30.sav` | `891938b2` | Map 13 pad 208 (5119,2303,120) |
| `replay1017-s13h-m10-back-with-halves-hp30.sav` | `1b8d6ae6` | Map 10 terrace (6960,23504,8), both halves. **Step 13 done** |
| **`replay1017-s15-m10-shield-879-restored-cured-hp30.sav`** | `f32ba4ec` | Sacred Circle (20496,17088,0), Shield 879 in the pack, cured. **Steps 14-15 done; leg 6 resume point** |

## Resume (leg 6)

1. **Load.**
   - Use the same game copy, binary and `scummvm.ini` (320×200, `scale_factor=2`; keep it).
   - Copy `~/lv-checkpoints/replay1017-s15-m10-shield-879-restored-cured-hp30.sav` to `saves/ultima8.001`.
   - Run `lv.start(log='lv_run6.log', slot=1)`, then `lv.q('debugflag_enable Object')` (retry until echoed). Set `lv.SCALE = 2` and `lv.TRACE = …/trace6.txt`, then `from leg3_helpers import *`.
2. **State.**
   - Map 10 (20496,17088,0), in the Sacred Circle. hp 30, weight 90.
   - Pack: Shield 879 q83, Key 18739 q170, POTION f1 (full heal, never drunk), POTION f3, Ragnar's empty bag.
   - Flags `[0409]` = 1, `[0404]` = 0, `[0723]` = 1, `[0425]` = 1, `[0407]` = 1, `[040F]` = 1.
   - Elders and Ezrekal are around the circle.
3. **Lattice.** Use `erA = nav.get_er(10,(0,0,24000,31800), forbid=trigger_forbids(triggers(items10),96)+hazards(exp10,shp10,{409:160,438:160})+[(11000,15000,15700,20950)], step=16, water=256)`, which loads from the cache in under 1 s. Use erode 0 for the terrace and the gaps, and erode 1 elsewhere.
4. **Step 16, after 10-11 leg 5.**
   - Hrodny (NPC 113) is near her hut (≈21639,8447). Talk 1: What is your name? → bye. Talk 2: I have been healed! → How can I open the temple?
   - Her bag (key q20) appears at about (19588,23284). Drag it into the pack.
   - At the chest by (20904,8884), go pack → bag → double-click the key → click the chest. Take the three Tiny Tar potions (859 f8).
   - The Map 10 spare key is removed on this build.
5. **Step 17.**
   - Trigger 211 is at (18432,23552) (walk S from about (18340,22968)) → Map 18 (3072,2024).
   - Map 18 was rebuilt: replan from the pinned FIXED. Expect the crack hint, a Tiny Tar through the breach, and then the altar egg (approach W, then N). The Shield on the altar is **879** now, and AOSCENE takes about 80 s untouched.
6. **Step 18.** Go out the breach → trigger 210 → EggEndgame (190 s untouched) → Ezrekal → "I have freed your gods!" → the reagent bag.
7. **Monsters.** If an egg monster chases, out-run it by 2-3 chunks without console reads; it is then destroyed (finding 2). The Map 18 golem was destroyed off-screen on 10-11.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-17-replay-leg5/` (30 plates: `s12a`-`s12l`, `s13a`-`s13i`, `s14a`-`s14e`, `s15a`, `s15c`, `f1`, `f1b`).
- **Wrote** the 11 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/replay1017/`:
  - `lv_run5.log`, `trace5.txt`, `monegg.dis` and `sp/l5-*`, plus the contact sheets `sp/sheet-*`.
  - Slot 1 holds the `s15` save.
  - `py/` is unchanged.
- **Stopped:** my ScummVM and Xvfb `:95`.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and the binaries. The game copy's hashes were re-checked at the end: all OK.

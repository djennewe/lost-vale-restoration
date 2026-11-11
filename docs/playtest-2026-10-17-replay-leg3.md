# Single-build replay, leg 3: step 3 done (the doors and T201, alive this time), steps 4 and 5 done, step 6 done (Ragnar's first talk) (2026-10-17/18)

Leg 3 continues from leg 2's corridor-pocket bank (`docs/playtest-2026-10-17-replay-leg2.md`), on the same pinned game copy. The session stopped at the request budget, after Ragnar's first talk. It did not stop on a defect.

## Build pinned (re-checked)

- **Game copy.** `/tmp/claude-1000/replay1017/game` was not re-copied or modified. `sha256sum -c ../pinned.sha256` gave OK for all six files at the start and at the end: EUSECODE `2e3b71c2…`, FIXED (root and `STATIC/`) `8db11ee3…`, U8SHAPES `efb16af1…`, TYPEFLAG `d26d1531…`, ANIM `696dbeb9…`.
- **Binary.** `/tmp/claude-1000/replay1017/bin/scummvm-console`, the same file as legs 1 and 2. The log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)`, `usecode/eusecode.flx: 84615e29d097543ed69da844fbc3948f, 1528891 bytes` and `Setting Video Mode 320x200...`.
- **Ini.** `scummvm.ini` as leg 2 left it: 320×200 with `scale_factor=2`, so the window is 640×400. Xvfb was `:95`.
- **Log.** `/tmp/claude-1000/replay1017/lv_run3.log` (16,317 lines). The trace is `trace3.txt`.
- **Cheats: 0.** `Cheat` appears 0 times in the log.
  - The console was used only for `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object` and `saveGame`.
  - Attaching the console pauses the world. I used that pause to read positions and to plan the door sequence between moves.
  - Every move, drag, key use, door and menu pick was player input.
- **Deaths: 0. Reloads: 0.**

## Outcome

- **Furthest step completed: 6.** Ragnar's first talk is done: ragnarMet `[0448]` = 1.
- **Steps 3, 4 and 5 are complete and banked.**
- **Step 7 (Ragnar's tale) is not started.** The Avatar stands next to Ragnar in his field.

## Verdicts

| Step / segment | Verdict | Evidence |
|---|---|---|
| Pocket → doors chamber | **PASS, hp 30 → 25** (finding 2) | Run E 1.6 s to (18996,5100). Walk/run N to (19296,5004). Then one held run, E 1.8 s + N 2.9 s. The pair of shape-808s hatched on the corridor exit and hit once, stopping the run at (20268,4724) (`s03a`). A second N run of 2.4 s ended at (20468,3164), in front of the **east** leaf, with 808 153 about 690 units behind |
| **Step 3: chest → key → leaves → T201 → Map 9** | **PASS** (finding 3) | I paused the world before every step. Chest 31495 `event 1 @ 004E:00A9`; the gump opened at x 70-360, y 0-240. I dragged it by its left frame from (82,60) to (82,230). Key 31494 `event 1 @ 0052:04BB`, then `Target result: Item 31174` (the east leaf, q 1123 → 99). A double-click on the east leaf gave `event 1 @ 0156:0098`. **Both** leaves became shape 340 (31172 (20255,3071) q 867; 31174 (20479,3071) q 355) (`s03b`). Both 808s were adjacent by then. Run NW 0.7 s + N 0.6 s → `Unloading map 8` → **Map 9 (13696,13760,0), hp 25** (`s03c`) |
| Map 9 → T203 → Map 11 | **PASS** | T203 is at (14336,16760), npc 0xCB, box x [13952,14720] y [16408,17112]. The distance-field follower went S along x 13696, then E/SE/SW → **Map 11 (9728,1896,0)**, hp 27 (`s03d`). No troll (83) hatched |
| **Step 4: four talismans** | **PASS, hp 30 → 19** (findings 4, 5) | I dragged each talisman (shape 596) onto the Avatar. Each logged `Dragging item N` → `Dropped item in backpack`. Air 18134 (17152,5120,0): w 40 → 50. Earth 17586 (2047,5631,4): w → 60. Fire 21148 (5631,18943,4): w → 70. Water 27725 (12799,18943,4): w → 80. The water-zone trigger at the south passage hatched 4 rats (806), which took 30 → 18 |
| **Step 4: four receptacles** | **PASS** (the bark was not captured, finding 6) | Each double-click logged `(shape 866) … event 1 @ 0478:00B4`. Air 21051 q202: "The earth talisman grows heavy with power!" (`s04a`). Water 21054 q204: "The fire talisman blazes in my hand!" (`s04b`). Fire 21052 q203: "The water talisman glows with a cold light!" (`s04c`). Earth 21049 q201: "The air talisman howls with fury!" (`s04d`). Afterwards `[06A1]`-`[06A4]` = 1, `[06EC]` (1772, allColumnsDestroyed) = 1, `findShape 865: 0 found`, and weight 80 → 40 |
| Step 4: T205 → Map 10 | **PASS** | The sealing boulders 66 at (8576/8704,22528), which are in FIXED, are gone in game. The route went S at x 8546 to (8546,23390) → **Map 10 (13104,2256,0)**, hp 27 (`s04e`) |
| **Step 5: Atli, Rite of Passage** | **PASS** | NPC 107 at Lab 1. A standstill strike logged `Item: 107 … event 1 @ 046B:0392`. My picks, read from the screen: May I speak with you? → What is your name? → I am from Brittania. → On the other side of the barrier. → (rant) → I am not a Hoskuld! → You will have to trust me. → Why must I leave? → Is there some way I may stay? → Then I will become a Zealan. → **Rite of Passage?** (`s05a`) → I wish to take the test. (`s05b`, new against 10-11) → Where is the Passage Stone? → Took the Stone? → I will find the stone. → bye. Afterwards atliMet `[0457]` = 1 and testFromAtli `[042E]` = 1 |
| **Step 6: Ragnar, first talk** | **PASS** | NPC 105 (GUARDMAN shape 574, class 0469 RAGNAR) at (7179,17075). Strike `event 1 @ 0469:0237`, then "Greetings I say." My picks: What is your name? (`s06a`) → From very far away. → Farewell. ("Well you travel, I hope.", `s06b`). Afterwards ragnarMet `[0448]` = 1, ragnarToldStone `[044A]` = 0 and ragnarPissed `[044B]` = 0 |
| Steps 7+ | **NOT DEMONSTRATED** | Budget |
| GHOST 411 follower | **Not seen** | `findShape 411: 0 found` on Map 10 at the end |
| Log hygiene (`lv_run3.log`) | **PASS for LV code** | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, ERROR and `Cheat`. **1** `Unhandled intrinsic 254 'isGameRunning()'`, the known CHEST_EW `004E` family. **968** `Cycle in paint`, every one of them the retail `590 -> 235 -> … -> 590` bone-chamber knot on Map 8 |

## Findings

1. **Severity: low (presentation). In the Map 8 spitter corridor the Avatar is not drawn.** At the pocket and along the corridor (y ≈ 5000-5100), the window centre is solid black (pixel max 0 over an 80×100 box) and only the mesa to the north paints (`F1`). Leg 2's `l2-pocket-cal.png` shows the same frame. The blue arrow at the centre of those frames is the mouse pointer, not a missile. The world is live (frames differ), and the Avatar is drawn again once he reaches the doors chamber. A player crosses this corridor blind.
   - **Repro.** `replay1017-s02d-m08-corridor-pocket-hp30.sav`.
   - **Cause.** Not traced [INFERENCE: the corridor has no floor items (engine void), and something at a higher z paints over the Avatar].
2. **Severity: high for a player (retail, carried over from leg 2). The pair of shape 808 is the `[invisible]` monster** (`u8monsters.ini`: hp 15-25, damage 4-6). That is why no plate in leg 2 or here shows them.
   - **Where they come from.** Their eggs are at (20562,4670) and (20500,4724), right on the corridor's exit into the chamber. MONFAST egg 31095's chunk (40,8) enters the 320×200 fast area on a diagonal running from about (19530,4776) to (19950,5208) (the `current_map.cpp` fast-area model).
   - **The effect.** They hatch about 1000 units ahead and intercept the northward turn. Here one hit took hp 30 → 25 and stopped a held run at (20268,4724).
   - **What worked.** A second N run straight past them, then the door sequence with the world paused between steps (finding 3).
   - **Repro.** `replay1017-s02d-…`, then the runs in the step-3 row.
3. **Severity: info. This answers leg 2 finding 5: use the key on the east leaf, then double-click it.**
   - **One use unlocked both leaves.** From (20468,3164), right in front of the east leaf, the key's target was 31174, and it took q 1123 → 99.
   - **One double-click opened both.** Both leaves went to shape 340.
   - **Where the gap is.** The swung leaves stand at x 20255 and x 20479, so the open gap is anchor x ≈ [20319,20447]. A NW 0.7 s + N 0.6 s run from (20468,3164) entered T201's box (x [20031,20799], y < 3135).
   - **Why this is faster.** From that spot the chest (dy 112) is in reach too, so the sequence needs no repositioning.
   - **What the pauses cost.** Pausing the world (attaching the console) before each step left only the input latency as game time. The run arrived with an 808 adjacent and took no further hit.
4. **Severity: medium (route; the rebuilt Map 11). The south half of Map 11 has one entrance from the north, the passage at x 9560-9980, y 14316-14380. The water-zone trigger (9728,14528), range 288×64, covers the passage's mouth.**
   - **The strip.** Its box in anchor space is y > 14464. That leaves a strip y ∈ [14412,14464] for anyone who wants to slip past.
   - **What happened.** One 192-unit walk S (14236 → 14468) hatched 4 rats (806 `RAT`, damage 1-2). They took hp 30 → 18 while the follower ran on to the Fire section, and they had despawned by the time I reached the talisman.
   - **Classification.** By design, most likely: a guardian at the gate.
   - **Not established.** Whether any player route avoids it.
5. **Severity: low (route). The Fire section is reached only through the narrow z 8 doorway at x ≈ 6111, y 16895 → 18335.**
   - **The model.** An erode-1 lattice at step 16 finds no route in. Erode 0 does.
   - **Change since 10-11.** That run's x ≈ 6144 doorway "from the Water section" is the same one. The Fire zone's west-side trigger eggs (2976-4064, 15104-19072; demons, shape 96) are avoidable from the east.
   - **Not seen.** No demon hatched.
6. **Severity: info. The receptacle order is free, and the bark names the talisman consumed, not the receptacle.** The first use (Air) consumed one talisman, and each later use consumed one more: w 80 → 70 → 60 → 50 → 40.
   - **Not captured.** The final "The way to the Lost Vale is open!" bark. I waited 3 s before the next plate, and it had gone.
   - **What is verified.** The flags it stands for: 1697-1700 and 1772 = 1, 0 pillars left.
   - So the bark text itself is NOT DEMONSTRATED.
7. **Severity: info. Map 9's T201 landing is (13696,13760), not (13696,14208).** Leg 2 landed at 14208. The arrival egg 201 sits at (13696,14208), frame 1. Harmless.

## Harness anomalies

1. **A hit stops a held run.** The 808's first contact ended the 2.9 s N leg after a few units. Plan a follow-up run. I first read the stop as a blocked lattice cell.
2. **Mouse presses.**
   - A 0.7 s walk N at mag 110 moved 0 units, twice. A 0.6 s run at mag 240 moved 96.
   - The first leg of a multi-leg hold (a NE 0.58 s) was dropped.
3. **The Map 11 lattice.** It needs erode 0 (finding 5). The follower oscillates in front of the receptacles, about 16 rounds at walk gait each. It is harmless, but slow.
4. **New helpers, all in the eval kernel only. `py/` was not edited.**
   - `in_fa()`: a port of the fast-area code.
   - `drag()` and `pickup()`: drags verified in the log.
   - `strike()`: an NPC standstill strike.
   - `mclick()`/`sadv()`/`advance_to_menu()`: menu picks and speech advance, by colour. The speech colours are Atli (49,254,49), Ragnar (205,202,238) and Thordis (255,133,49); menu red is (213,48,49).
   - Routes were built from the pinned FIXED with trigger-egg forbids (anchor-space boxes, margin 96) and hazard forbids (409 +128/160, 318/435-437 +128/160).

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `replay1017-s03-m09-arrival-hp25.sav` | `413aa06f` | Map 9 (13696,13760), **step 3 done** |
| `replay1017-s03b-m11-arrival-hp27.sav` | `4fdbe669` | Map 11 (9728,1896) |
| `replay1017-s04a-m11-four-talismans-hp20.sav` | `308b3937` | Map 11 (12706,18870), w 80, all four talismans |
| `replay1017-s04b-m11-columns-destroyed-hp25.sav` | `86068f05` | (7694,20834), 1697-1700 = 1, 1772 = 1, w 40 |
| `replay1017-s04c-m10-arrival-step4-done-hp27.sav` | `e489406c` | Map 10 (13104,2256), **step 4 done** |
| `replay1017-s05-m10-atli-rite-hp30.sav` | `b53d86b6` | Lab 1 (19120,7072), atliMet and testFromAtli = 1 |
| **`replay1017-s06-m10-ragnar-first-talk-hp30.sav`** | `22997ec2` | Ragnar's field (7296,17256,0), hp 30, ragnarMet = 1. **Leg 4 resume point** |

Scratch saves: `sp/l3-m11-air-earth.sav`, `sp/l3-m11-three.sav`.

## Resume (leg 4)

1. **Load.**
   - Use the same game copy, binary and `scummvm.ini` (320×200, `scale_factor=2`; keep it).
   - Copy `~/lv-checkpoints/replay1017-s06-m10-ragnar-first-talk-hp30.sav` to `saves/ultima8.001`.
   - Run `lv.start(log='lv_run4.log', slot=1)`, then `debugflag_enable Object`.
   - Projection: `lv.SCALE = 2`, and aim at `proj(...)` + (0,40). For an NPC body, aim at `proj(x-32,y-32,z)` + (0,10).
2. **State.**
   - Map 10 (7296,17256,0), hp 30, weight 40.
   - The pack holds POTION f1 (full heal) and f3. The f1 potion was never drunk.
   - Steps 1-6 are done. Flags: `[0457]` = 1, `[042E]` = 1, `[0448]` = 1, `[044A]` = 0, `[044B]` = 0.
   - Ragnar (NPC 105) was standing at (7179,17075).
3. **Step 7 (Ragnar's tale).** Talk to him again. 10-11 used: Atli sent me to you. → Atli admires you. → I believe that he is sincere. → He spoke of you and Hrodny. → He said you could help me. → Do you know of the Passage Stone? → Yes, I do. → **Why do you not go there?** → Farewell. Check `[044A]` = 1.
4. **Step 8 (Passage Stone, lake island).** The pier is two columns of shape 301 at z 8, x 13696-13951, y 18176-20479. Keep to **x 13848**.
   - **This build puts Water Zombie (872) trigger eggs on the pier.** id 1 at (13824,20352,8), range 4×2. id 2 at (13824,19456,8), range 4×1. id 8 at (13312,18816,8), range 4×1, on the island. The eggs are at (13344-14016, 18271-19936, z 8).
   - A crossing will hatch zombies: hold the run, drag the stone (shape 798) from the island, and leave at once. Drink f1 if hit.
   - On the south-shore approach, keep 420+ off the lake (10-11 death 1).
5. **Then.** The test ramp: walk S along x 12872 from (12872,27568) to (12872,29192,64), then 0.7 s more S. The test egg is `0x59A` at (12800,29440,64). Then talk to Thordis for step 9 (her speech is orange), then Ezrekal (step 10) per the 10-11 leg 4 report.
6. **Lattices.** Build them as in this leg: `nav.get_er(10,(0,0,20600,31800),forbid=trigger boxes+hazards,step=16,water=256)`. The trigger list is the shape-73 q 2 items; npcnum's high nibble times 32 is the x range, and its low nibble times 32 the y range.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-17-replay-leg3/` (14 plates: `s03a`-`s03d`, `s04a`-`s04e`, `s05a`-`s05b`, `s06a`-`s06b`, `F1`).
- **Wrote** the 7 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/replay1017/`:
  - `lv_run3.log`, `trace3.txt` and `sp/l3-*`, `sp/atli-*`, `sp/rag-*`.
  - Disassemblies: `tdoor.dis` and `chest.dis`.
  - Slot 1 holds the `s06` save.
  - `py/` is unchanged.
- **Stopped:** my ScummVM and Xvfb `:95`.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and the binaries. The game copy's hashes were re-checked: all OK.

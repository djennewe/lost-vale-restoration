# Single-build replay of the 1→18 run, leg 3: step 4 finished, steps 5-9 done (2026-10-11)

Leg 3 of the one-build replay. It continues from leg 2's banked save on the same pinned game copy (`docs/playtest-2026-10-11-replay-leg2.md`).

## Build pinned (re-checked)

- **Game copy.** `/tmp/claude-1000/replay/game`, as legs 1 and 2 left it; it was not re-copied. `sha256sum -c ../pinned.sha256` inside it gave OK for all six files at the start (19:09) and at the end (20:05): EUSECODE `4182e079…`, FIXED (root and `STATIC/`) `122b4374…`, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`.
- **Binary.** `/tmp/claude-1000/pinned-bin/scummvm-4182e079` (sha256 `1502d576…`), one process for the whole session. The log (`replay/lv_run3.log`) reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)`, `usecode/eusecode.flx: d00d0d5962e966129c2277c7cea7844b, 1526311 bytes` and `Setting Video Mode 320x200...`. There is no `Couldn't identify`.
- **Harness.**
  - Same ini (320×200, music on, `SDL_AUDIODRIVER=dummy`). Xvfb `:95`.
  - Leg 1's `rp.py`/`navr.py`, used from the eval kernel with the prime left click off. Each run starts with a sacrificial 0.2 s right press.
  - Routes are `exact_reach` (DryReach) lattices built from the **pinned** `game/STATIC/FIXED.DAT`, not `shared/build/`. The lattice is computed with the console open, which pauses the game.
  - Hazards are forbidden with margins: 318 / 435-437 +160, 409 +192, shape-500 eggs +320 (Map 11) or +400 (Map 10), and the Map 10 lake zone (11264-15360, 15360-20480) +420.
  - Talks were driven by a screen reader. It finds the red menu rows by their bullets and matches the wanted option by word-width signature. If two rows scored within 20 px of each other, it stopped and I picked by row index from a screenshot. Every pick was checked afterwards on a contact sheet.
- **Cheats: 0.** `Cheat` appears 0 times in `lv_run3.log`. The console was used only for `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object`, `saveGame` and `loadGame`.
- **Deaths: 2 (drowning), with 2 reloads.** Both are described in the findings.

## Outcome

- **Furthest step completed: 9.** endOfPlantScene 1050 = 1.
- **Step 10 (Ezrekal) is not started.** The Avatar is at the foot of the test ramp, heading for her.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| 4: Fire talisman (5631,18943,4) | **PASS** | From the island, W along y 18903, then NW to (6216,16968), N to y 16864, then W through the doorway to (5832,16864,8). S along x≈5608 (lakes +192, egg (5120,17920) +320) to (5608,18784). The drag logged `Dragging item 27020` → `Dropped item in backpack`, and w went 50 → 60. hp 30 throughout (`s04d`) |
| 4: out of the Fire section | **PASS, first line** | The reverse line N along x 5608, then E. hp 30. Part 5's CLRLAVA death did not recur with the margins |
| 4: four receptacles | **PASS** | Each double-click logged `(shape 866) calling usecode event 1 @ 0478:00B4`. 27744 q201: "The earth column has been destroyed." (`A1`). 27755 q202: "The earth talisman grows heavy with power!" (`A2`). 27777 q204 (`A3`). 27766 q203: "The water talisman glows with a cold light!" (`A4`). Then **"The way to the Lost Vale is open!"** (`A5`). Afterwards `[06A1]`-`[06A4]` = 1 and `[06EC]` (1772) = 1 (`A6`), and `findShape 865: 0 found`. Weight went 60 → 20 |
| 4: T205 → Map 10 | **PASS** | E to (8616,21872), then S through the opened doorway to (8544,22880), then SE and S → **Map 10 (13088,3168,0)** (`A7`, `s04f`) |
| **5: Atli, Rite** | **PASS** | He was at Lab 1 (19231,6943) and wandering; a colour-tracked double-click logged `Item: 107 … event 1 @ 046B:0392`. Picks, from the screen: May I speak with you? → What is your name? → I am from Brittania. → On the other side of the barrier. → (rant, click-through) → I am not a Hoskuld! (`B0`) → You will have to trust me. → Why must I leave? → Is there some way I may stay? → Then I will become a Zealan. → **Rite of Passage?** (`B1`) → bye. atliMet `[0457]` = 1 and testFromAtli `[042E]` = 1 (`B2`). One talk, as in part 5 |
| **6: Ragnar, first talk** | **PASS** | Field (6927..7172, 17236..17295). What is your name? → From very far away. → Farewell. The menus were checked on a contact sheet |
| **7: Ragnar's tale** | **PASS** | Talk 2: Atli sent me to you. → Atli admires you. → I believe that he is sincere. → He spoke of you and Hrodny. → He said you could help me. → Do you know of the Passage Stone? → Yes, I do. → **Why do you not go there?** (`C1`) → Farewell. ragnarMet `[0448]` = 1, ragnarToldStone `[044A]` = 1, ragnarPissed `[044B]` = 0 (`C2`). The bag was not fetched |
| **8: Passage Stone, lake island** | **PASS after 2 deaths** (findings 1-2) | Up the pier at **x 13848** (z 8) from the south shore, to (13848,18456,16). The drag logged `Dragging item 17508` → `Dropped item in backpack`, and objectInfo gave `shape 798 (uc: TOSSROCK) … f: 0xc`, w 20 → 30. No zombie egg hatched |
| **8: ramp and Passage Test** | **PASS** | A walk-gait S along x 12872 from (12872,27568,0) to (12872,29192,64), then a further 0.7 s S. The log shows `Item: 19904 (shape 73) calling usecode event 7 @ 059A:0080`. Frames are in `D1`. haveMark `[0411]`, avatarPoisoned `[0404]`, firstPoisoned `[040A]` and plantScene `[0419]` all read 1 (`D2`). `findShape 798` lists only the template (0,0) item, so the stone was consumed |
| **9: Thordis's Mark speech, on the plateau** | **PASS** | **Both the Avatar and Thordis were on screen** at 320×200 after the scene (contrast part 5 finding 3). Double-clicking her logged `Item: 106 … event 1 @ 046A:0ECD`. Her barks: "Sad to say it I am. But give you the Zealan Mark I will…" (`D3`), then "Well, speak to Ezrekal you can, but afraid I am no good it will do…". endOfPlantScene `[041A]` = 1 and plantScene `[0419]` = 0 (`D4`) |
| 10-18 | **NOT DEMONSTRATED** (budget) | — |
| Music on | **PASS (no hang)** | 56 min of play; the console answered throughout |
| Log hygiene (`lv_run3.log`, 8,343 lines) | **PASS** | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Unhandled intrinsic`, `Cycle in paint` and ERROR. Leg 2's `10 -> 1` and `590 -> 235` cycles did not appear on Map 11 or Map 10 this leg |

## Findings

1. **Death 1: drowned on the south shore of the Vale lake, on a route held about 200 units off the water.** Severity: route note, not an LV defect.
   - **The route.** The lattice route from Ragnar's field to the pier forbade the lake zone with a 200-unit margin. It ran E along y 20687, while the lake's last water row is shape 347 at y 20352..20479, x ≥ 11264.
   - **What happened.** From (10344,19960), hp 30, the run was SE 1.38 s then E 2.02 s. The log then shows `Item: 13928 (shape 347) calling usecode event 6 @ 015B:0080`, and the Avatar was at (0,0,0) with hp 0 (`F1`).
   - **The retry.** A 420-unit margin (route along y 20903) with legs ≤ 1.8 s arrived at hp 30, twice, by an identical deterministic path.
   - **Reading.** As in part 7 finding 1, this is open-loop overshoot near deadly water [INFERENCE: the drift was not observed; there was no read between the two legs].
2. **Death 2: drowned on the island pier at x 13960, about 9 units outside the pier's east tile edge.** Severity: medium as a player trap; low confidence on cause.
   - **The pier.** It is two columns of shape 301 tiles at z 8, with anchors x 13823/13951, so it spans x 13696..13951 from y 18176 to 20479 (pinned FIXED). The Avatar's footpad is 2×2 (64 units), so the body at x 13960 spans 13896..13960 and overlaps the tiles by 55.
   - **What happened.** A run N 1.6 s from (13960,20488,8) reached (13960,19584,8) at hp 30. The next run N 1.75 s ended in death: two water items `14333` and `14378 (shape 347) event 6 @ 015B:0080` (`F2`).
   - **What worked.** At **x 13848**, on the pier's centre, three 1.0 s runs N reached (13848,18840,8) and the island with no loss. The return S at x 13848 was clean as well.
   - **Contrast.** Part 5 walked this pier at x 13976.
   - **Not established.** Why a 55-unit overlap did not hold the Avatar [INFERENCE: the run's step lands the body past the edge, or some 301 frames do not cover their full footpad]. `exact_reach` (DryReach) reports no standable cell on the pier at all, so the model cannot judge it either.
   - **Advice for a player.** Keep to the centre of the pier.
3. **Step 9 played where the test is, visible.** After the PLNTST scene the camera showed the Avatar standing and Thordis beside the pool at 320×200. A double-click on her played the Mark speech at once. Part 5's "invisible scene" (finding 3) did not recur on this build. Note that the scene needed **no click to start**: the frames (`D1`) show the Avatar lying down, a black frame, then Thordis walking in.
4. **Receptacle use needs about 100 units of reach, and the box hides behind the Avatar.**
   - **Out of reach.** From about 257 units, a double-click on 27744 logged only two `event 0` looks, and no bark explained why.
   - **Hidden.** With the Avatar standing south-east of a box, the box draws behind his sprite. One double-click hit the Avatar and opened the paperdoll; BackSpace closed it.
   - **Severity.** Low; this is the same "reach without feedback" pattern as leg 2 finding 3.
5. **Atli wandered at Lab 1 during the talk window.** The first double-click on the robe landed on **Tyorvi** (item 115, at Gunnar in this period: `event 16 @ 0473:0237`). Atli was found by colour tracking. Not a defect.
6. **NPC speech colours differ by speaker.** Atli's speech is green (49,254,49) and Thordis's is orange (255,133,49). The rant needed a click to advance, and it sat unadvanced for more than 25 s. A harness that waits for one colour stalls on a talk. Harness note.

## Harness anomalies

- **Word-width menu matching** worked for 22 of 25 picks. The three rejections were near-ties: "I am not a Hoskuld!" (before calibration), "Yes, I do." against "No, I don't", and "Why do you not go there?" against a row of the same length. Those were picked by row index from a screenshot. A cursor left over the menu breaks a row in two, so park the mouse at (620,390) before reading.
- **The follower oscillates** near a goal when the remaining leg is shorter than a run's minimum. Finish with walk-gait presses.
- **The DryReach lattice has no route from z 64 at the test ramp top**, because the ramp is narrow at erosion 1. Walk it by hand: N walk-gait 3.0 s + 2.4 s took the Avatar from (12872,29192,64) to (13055,28279,8).
- `saveGame` worked every time (13 of 13).

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `replay1011-s04d-m11-four-talismans.sav` | `42f215d0` | Map 11 (5608,18784,0) by the Fire talisman spot, w 60, all four talismans |
| `replay1011-s04e-m11-pillars-destroyed.sav` | `cca50c5e` | Map 11 (7800,21872,0), 1697-1700 = 1, 1772 = 1 |
| `replay1011-s04f-m10-arrival-step4-done.sav` | `20a4e93c` | Map 10 (13088,3168,0). **Step 4 done** |
| `replay1011-s05-m10-atli-rite.sav` | `227d7976` | Lab 1 (19308,7132), atliMet and testFromAtli = 1 |
| `replay1011-s07-m10-ragnar-told-stone.sav` | `86d35cdb` | Ragnar's field (7212,16956), 1096/1098 = 1, 1099 = 0 |
| `replay1011-s08a-m10-passage-stone-in-pack.sav` | `7e223b54` | Lake island (13848,18456,16), stone 17508 in the pack |
| `replay1011-s09-m10-passage-test-mark-speech-done.sav` | `7d611480` | Test plateau (12872,29192,64), haveMark and poisoned set, endOfPlantScene 1 |
| **`replay1011-s09b-m10-ramp-foot-toward-ezrekal.sav`** | `a3a017a8` | Map 10 (13055,28279,8) at the ramp foot, hp 30, w 20, steps 4-9 done. **Leg 4 resume point** |

Scratch saves are in `/tmp/claude-1000/replay/sp/l3-*.sav`, including `l3-pier-base.sav` (13848,20496,8) at the pier's south end.

## Resume (leg 4)

1. **Start.** Use the same game copy and ini. Launch `/tmp/claude-1000/pinned-bin/scummvm-4182e079` with `--save-slot=1` after copying `replay1011-s09b-…` to `saves/ultima8.001`, then send `debugflag_enable Object`.
2. **To Ezrekal (step 10).** The last read had her at home (12799,12543).
   - A DryReach route (erosion 1, lake +420) from (12871,27503,0) runs N to (12871,24607), NE to (14919,22559), then via (15303,21383) to (15783,20903). It goes N along **x 15783** to 16735, then (15815,14511) to (14303,12999) outside the stockade. The route from the exact s09b spot returned None, so walk a little N or W first, then replan.
   - Enter by the north fence gap (x≈12880-12940); the east door is x 13983 (parts 5 and 6).
   - Picks per part 5's step-10 row, ending **Perhaps I will try the Cliffs.**
3. **Then** Tyorvi (step 11), the root (21376,16640) and the elixir (step 12) per parts 5 and 6. Then steps 13-15, Hrodny's errand: the key comes **only from her bag** on this build (do not rely on part 6's spare at (22016,6144)). Then the temple, Tiny Tar, the altar and the endgame per parts 6 and 7.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-replay-leg3/` (18 plates: `A1-A7`, `B0-B2`, `C1-C2`, `D1-D4`, `F1-F2`).
- **Wrote** the 8 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/replay/`: `lv_run3.log`, `trace3.txt`, `sp/l3-*`, the talk frames `sp/{atli,rag,rag2,plnt,thor}-*.png`, and new `er_10_*`/`er_11_*` pickles built from the pinned FIXED. The game copy is unchanged; its hashes were re-checked at the end.
- **Stopped:** my ScummVM (`pinned-bin/scummvm-4182e079 … --config=/tmp/claude-1000/replay/…`) and Xvfb `:95`. Other agents' Xvfb (`:92`, `:94`, `-displayfd`) and the `vmon` ScummVM were left alone.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and both binaries.

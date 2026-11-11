# Single-build replay, leg 4: steps 7-11 done, step 12 partway (root handed over, brew waited; the elixir is not collected yet) (2026-10-18)

Leg 4 continues from leg 3's Ragnar bank (`docs/playtest-2026-10-17-replay-leg3.md`), on the same pinned game copy. The session stopped at the request budget, standing in Ezrekal's stockade. It did not stop on a defect.

## Build pinned (re-checked)

- **Game copy.** `/tmp/claude-1000/replay1017/game` was not re-copied or modified. `sha256sum -c ../pinned.sha256` gave OK for all six files at the start and at the end: EUSECODE `2e3b71c2…`, FIXED (root and `STATIC/`) `8db11ee3…`, U8SHAPES `efb16af1…`, TYPEFLAG `d26d1531…`, ANIM `696dbeb9…`.
- **Binary.** `/tmp/claude-1000/replay1017/bin/scummvm-console`, the same file as legs 1-3. The log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `eusecode.flx: 84615e29d097543ed69da844fbc3948f, 1528891 bytes`.
- **Ini.** `scummvm.ini` unchanged: 320×200, `scale_factor=2` (window 640×400). Xvfb `:95`.
- **Log.** `/tmp/claude-1000/replay1017/lv_run4.log` (8,677 lines). The trace is `trace4.txt`.
- **Cheats: 0.** `Cheat` appears 0 times in the log.
  - The console was used only for `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object` and `saveGame`. There were no loads; one process ran the whole leg.
  - Every move, drag, menu pick and conversation was player input.
- **Deaths: 0. Reloads: 0.** hp was 30 at every read.

## Outcome

- **Furthest step completed: 11.** tyorviDreams `[0424]` = 1.
- **Step 12 is partway.** The root is handed over: givenRoot `[0427]` = 1. The brew wait is done: Ezrekal's `event 16 @ 0474:0264` fired, and justGotRoot `[0428]` went 1 → 0. Next comes "Have you made the elixir?" (gotElixir `[0723]` is still 0).
- **Step 8 used Ragnar's bag, not the lake island** (finding 1). No Water Zombie was met. The lake pier was not walked, so the zombie crossing is NOT DEMONSTRATED.

## Verdicts

| Step / segment | Verdict | Evidence |
|---|---|---|
| **Step 7: Ragnar's tale** | **PASS** | NPC 105 strike `event 1 @ 0469:0237`, "So we meet again." Picks, read from the screen: Atli sent me to you. → Atli admires you. → I believe that he is sincere. → He spoke of you and Hrodny. → He said you could help me. → Do you know of the Passage Stone? → Yes, I do. → **Why do you not go there?** (`s07a`) → Farewell (`s07b` shows the menu just before it). ragnarMet `[0448]` = 1, ragnarToldStone `[044A]` = 1, ragnarPissed `[044B]` = 0 |
| **Step 8: Passage Stone from Ragnar's bag** | **PASS** (finding 1) | The tale's `bag.pop(16447,25727,64)` placed BAG 19729 (shape 637) holding TOSSROCK 19730 (798). Route: field → S along x 7708 → E along y 23512 → (16952,24296) → S into the walled yard through its open north side → W up the stair (shape 113) to (16556,25724,48) (`s08a`). The drag logged `Dragging item 19729` → `Dropped item in backpack`, and weight went 40 → 60 (`s08b`) |
| **Step 8: ramp and Passage Test** | **PASS** | Walked up the ramp along x 12892 to (12892,29244,64). The next S walk logged `Item: 5422 (shape 73) calling usecode event 7 @ 059A:0080`. The scene ran untouched (`s08c`, 45 frames). Afterwards haveMark `[0411]`, avatarPoisoned `[0404]`, firstPoisoned `[040A]` and plantScene `[0419]` all read 1. The stone was consumed **from inside the bag**: `findShape 798` lists only the island stone 5421. Weight went 60 → 50, and the empty bag stays in the pack. The Avatar was left at (13055,30079,64) with Thordis on screen (`s08d`) |
| **Step 9: Thordis's Mark speech** | **PASS** | Strike `event 1 @ 046A:0ECD`. "Oh my, terrible this is. Send you here Atli did?" → "So cruel those Gunnar's are!…" → "As much I thought. In the days before the Great Cataclysm…" → "…afraid you are doomed I am." → (Avatar) "This can not be!" (`s09a`) → "Sad to say it I am. But give you the Zealan Mark I will…" → (Avatar) "Is there no shred of hope?" → "Well, speak to Ezrekal you can, but afraid I am no good it will do. Leave you alone now I will." (`s09b`). endOfPlantScene `[041A]` = 1 and plantScene `[0419]` = 0 |
| Plateau → Ezrekal | **PASS** | Walked down the ramp, then an erode-1 field: N along x 12951, NE, E along y 21123, N along **x 16003** (about 640 off the lake) to y 14851, NW/W to the garden. Entered the stockade by the **south gap** (x 13056-13183 in the south palisade, y 12959) |
| **Step 10: Ezrekal, poison thread** | **PASS** | Strike `event 1 @ 0474:034A`. Every pick was read from the screen: May I know your name? → I am from Britannia. → Yes, I am from outside. → Can you help me? → I have been poisoned. → But I'm dying! → Prepare my funeral?! → I don't want a funeral! → You said the Ancient Ones were gone! → What kind of eternal peace? → When will they return? → A city in the clouds? → Where will I be until then? → I don't want to be an undead! → Cloud City? → How?! How can I be healed? → Where is the Cloud City? → Tell me more of the Cloud City. → Has anyone ever been there? → Are the Ancient Ones still there? (`s10a`) → **Perhaps I will try the Cliffs.** → bye. The menu after it lists the Shield once: "Tell me of the Shield. / Where is the Sacred Circle? / How can I awaken the Ancients? / Key to the Clouds? / bye" (`s10b`). ezrekalMet `[0433]`, spokePoison `[0443]`, spokeFuneral `[0444]` and sentToTyorvi `[0417]` = 1 |
| **Step 11: Tyorvi** | **PASS** | He was at Hoskuld (7537,7525). Strike `event 1 @ 0473:0354`. Menu "What is your name? / What do you do? / Do you have the Key to the Clouds? / bye" → Do you have the Key to the Clouds? → Tell me of these nightmares. → How can you stop the dreams? → Have you spoken to Ezrekal? (`s11a`) → **I will speak to Ezrekal for you.** tyorviDreams `[0424]` = 1 and tyorviMet `[043B]` = 0, as on 10-11 |
| **Step 12: root** | **PASS** | On this build the root is **shape 869** (TYPESPEC), item 19610 at (21376,16640,0); `findShape 399` reports 0. Approached from the north-west so the root draws in front of the Avatar (`s12a`). The drag logged `Dragging item 19610` → `Dropped item in backpack`, and weight went 50 → 60 |
| **Step 12: root handed over** | **PASS** | Ezrekal was in the stockade. Menu "I have found the root. / Can you help me? / bye" → I have found the root. The next menu read "Can you help me? / Is Tyorvi's elixir ready yet? / bye" (`s12b`). givenRoot `[0427]` = 1, justGotRoot `[0428]` = 1, weight 60 → 50 |
| **Step 12: brew wait** | **PASS** | Walked out of the east door to (14751,14039). The log shows `Item: 116 (shape 200) calling usecode event 16 @ 0474:0264`. Afterwards `[0428]` = 0 |
| Step 12: elixir, Key; step 13 onward | **NOT DEMONSTRATED** | Budget. A strike at Ezrekal from 695 units, with her off screen, was refused before the stop |
| Lake Water Zombies (872) | **NOT DEMONSTRATED** | The pier was not walked (finding 1) |
| GHOST 411 follower | **Not seen** | `findShape 411: 0 found` on Map 10 at the end |
| Log hygiene (`lv_run4.log`) | **PASS** | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Unhandled intrinsic`, `Cycle in paint`, ERROR and `Cheat`. The Object channel was on for the whole leg (it was enabled at start, there were no loads, and click dumps log throughout), so the 0 for `Cycle in paint` is a real 0 |

## Findings

1. **Severity: info (route). Ragnar's bag is a working second source of the Passage Stone, and it avoids the lake pier.** None of the 10-10, 10-11 or 10-17 runs had fetched the bag before.
   - **The source.** `lv-patched/RAGNAR.UNK:1040-1057`: "Why do you not go there?" sets ragnarToldStone and creates a BAG holding a TypeBushKey (798) at (16447,25727,64).
   - **Where it lands.** It stands on the top step of a stair inside a walled yard south-east of the lake: walls x 16328-17480, y 24664-26200, with the north side open between x ≈ 16456 and 17352. The stair (shape 113) rises westward from x ≈ 17200 (z 0) to x ≈ 16560 (z 48). The bag is reachable from (16556,25724,48).
   - **What happened there.** No monster or trigger egg is near it, and nothing hatched.
   - **What it proves.** PLNTST's `foreach recursive` takes the stone from inside the bag. The empty bag stays in the pack (weight 10).
   - **Why I took it.** The pier is lined with three zombie triggers. Trigger 1 (13824,20352) and trigger 2 (13824,19456) span the railed walkway's full width, and trigger 3 (13312,18816) covers the island end, with two zombie eggs beside the stone (13855,18271) and (14016,18400). The zombies hit for 6-12 and attack unprovoked (`docs/playtest-2026-10-11-monsters2.md`). The Avatar has 30 hp and no weapon.
   - **Repro.** `replay1017-s07-m10-ragnar-told-stone-hp30.sav`.
2. **Severity: info (route guide). On this build the lake pier is not leg 3's "two columns of shape 301 at z 8".** It is a railed walkway of shape 125 at z 0, with rails 498/497:
   - north from the shore along x anchors 13823/13951 (x 13696-13951) to y 19455;
   - west along y ≈ 19400;
   - north along x anchors 13311/13439 (x 13184-13439) to the island at y ≈ 18815.
   - The 301 slabs at z 8 cover only the island top (y 17919-18431). Leg 3's "keep to x 13848" holds only on the first section.
3. **Severity: info. The stockade has four palisade gaps.** North x 12800-12927 and 13440-13567 (y 12191), south x 13056-13183 (y 12959), west y 12416-12543 (x 12319) and east y 12416-12671 (x 13983). Ezrekal wanders through them: at one read she stood outside the north wall (12796,12090).
4. **Severity: low (presentation, harness-adjacent). A speech-advance press can start a world drag through the bark text.** During Thordis's speech the press-move-release on the text logged `Dragging item 16761` (a shape-871 poison plant) and `Dragging item 16730` (a fixed shape-301 tile), each followed by `Dropping object` with no move. Nothing was displaced as far as I saw, and the plant still read (12735,29663,64). A player who clicks through barks over the plant bed could tug the plants, though [INFERENCE: whether a non-fixed plant can actually be moved this way was not tested].

## Harness anomalies

1. **`lv.attach()` failed several times** (`ATTACH FAILED`), always right after a detach, and twice while `event 18 @ 0401:3477` lines flooded the log after a follower run. A bare `lv.attach()` + `lv.detach()` cleared it each time. One `bank()` failed this way and was retried. Once a timed-out cell left the console attached, and the world paused; an explicit `lv.detach()` fixed it.
2. **The lattice ROI.** Leg 3's recipe `(0,0,20600,31800)` cuts Map 10 off at x 20600, so the Sacred Circle and root area snap to x 20591. Use **`(0,0,24000,31800)`**. It builds in about 10 s.
3. **Leg 3's helpers are now a file.** `py/leg3_helpers.py` (`strike`, `npcpos`, `pickup`, `drag`, `mclick`, `sadv`, `analyze`, `advance_to_menu`, `triggers`, `trigger_forbids`, `hazards`, `in_fa`) was written by ReplayLeg3 at my request, re-typed from its kernel. I used it unchanged. `analyze()` merges adjacent menu rows into one group, so I picked by pixel y read from a cropped plate (rows are 20 px apart).
4. **Strikes.** Three double-clicks each log `event 1`, two to five times. Each talk still opened once.
5. **New kernel-only helpers.** `pk`/`pk2` (pick + advance + crop the menu), `talk_pages`, `preview` (a field path dump) and `amap2` (an ASCII lattice map). `py/` was not edited.

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `replay1017-s07-m10-ragnar-told-stone-hp30.sav` | `ed2b047c` | Ragnar's field (7132,17092), `[044A]` = 1, bag spawned. **Step 7 done** |
| `replay1017-s08a-m10-ragnar-bag-stone-in-pack-hp30.sav` | `08957a01` | Yard stair top (16556,25724,48), bag 19729 + stone 19730 in the pack, w 60 |
| `replay1017-s08b-m10-passage-test-marked-poisoned-hp30.sav` | `f112e308` | Test plateau (13055,30079,64), haveMark/poisoned = 1, Thordis beside. **Step 8 done** |
| `replay1017-s09-m10-thordis-mark-speech-done-hp30.sav` | `0134418e` | Same spot, endOfPlantScene = 1. **Step 9 done** |
| `replay1017-s10-m10-ezrekal-sent-to-cliffs-hp30.sav` | `e042d756` | Stockade (13155,12763), 1075/1091/1092/1047 = 1. **Step 10 done** |
| `replay1017-s11-m10-tyorvi-dreams-hp30.sav` | `7735caf3` | Hoskuld (7507,7707), 1060 = 1. **Step 11 done** |
| `replay1017-s12a-m10-root-in-pack-hp30.sav` | `11dd8ca1` | Circle (21363,16547), root 19610 in the pack, w 60 |
| **`replay1017-s12b-m10-root-given-brew-waited-hp30.sav`** | `c6fa077e` | Stockade (13151,12839), givenRoot = 1, justGotRoot = 0, w 50. **Leg 5 resume point** |

## Resume (leg 5)

1. **Load.**
   - Use the same game copy, binary and `scummvm.ini` (320×200, `scale_factor=2`; keep it).
   - Copy `~/lv-checkpoints/replay1017-s12b-m10-root-given-brew-waited-hp30.sav` to `saves/ultima8.001`.
   - Run `lv.start(log='lv_run5.log', slot=1)`, then `debugflag_enable Object`. Set `lv.SCALE = 2`.
   - Then `from leg3_helpers import *`.
2. **State.**
   - Map 10 (13151,12839,0), just inside the stockade's south gap. hp 30, weight 50.
   - The pack holds POTION f1 (full heal, never drunk), POTION f3 and Ragnar's empty bag.
   - Flags `[0411]` = 1, `[0404]` = 1 (poisoned), `[041A]` = 1, `[0433]` = 1, `[0417]` = 1, `[0424]` = 1, `[0427]` = 1, `[0428]` = 0 and `[0723]` = 0.
   - Ezrekal (NPC 116) was last read at (12456,12842), on the west side of the stockade.
3. **Step 12, the rest.**
   - Walk to within about 300 units of her, then `strike(116)`. Pick **"Have you made the elixir?"** (or the "Is Tyorvi's elixir ready yet?" row, whichever is offered). Check `[0723]` (1827) = 1 and `[0426]` (1062) = 1. The elixir is shape 868, w +10.
   - Then go to Tyorvi (Hoskuld/Gunnar or the stash near (21650,8000); 10-11 found her at the stash). The 10-11 picks: I have something for you from Ezrekal. → It is an elixar. → It is a potion. → It will heal your dreams. → Just try it, please. (the talk exits) Talk 2: the same chain → **Shut up and drink it!** → May I have the Key to the Clouds? Expect Key 82 q170.
4. **Step 13.**
   - Map 10 → Map 13: Gunnar → S along x ≈ 16000 → W along y ≈ 21271 (keep y ≥ 20950: the lake ends at y 20479) → the terrace (7019,23435,8). Trigger 206 at (7168,23296,8) leads to Map 13.
   - EggCloudCliffs, then the climb. Map 13 was rebuilt with a lane stagger: build the lattice fresh from the pinned FIXED at erode 0, and walk the climb legs. Harpie (873) triggers are on the lane. Then teleporter 209 → Map 17. The halves are **shape 878**. Then back down to Map 10.
5. **Lattice.** Use `erA = nav.get_er(10,(0,0,24000,31800), forbid=trigger_forbids(triggers(items10),96)+hazards(exp10,shp10,{409:160,438:160})+[(11000,15000,15700,20950)], step=16, water=256)`, then `nav.Field(erA, goal, erode=1)` and `FW.follow(10, F, tol=150, rounds=30, maxsecs=1.8)`. Use erode 0 in the stockade gaps and on stairs. Give every follow cell a timeout of 600 s or more.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-17-replay-leg4/` (13 plates: `s07a`-`s07b`, `s08a`-`s08d`, `s09a`-`s09b`, `s10a`-`s10b`, `s11a`, `s12a`-`s12b`).
- **Wrote** the 8 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/replay1017/`:
  - `lv_run4.log`, `trace4.txt` and `sp/l4-*`.
  - `py/leg3_helpers.py` (new, written by ReplayLeg3); the other `py/` files are unchanged.
  - Slot 1 holds the `s12b` save.
- **Stopped:** my ScummVM and Xvfb `:95`.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and the binaries. The game copy's hashes were re-checked at the end: all OK.

# Full 1→18 run, cheats off, part 5: step 4 finished, Map 10 steps 5-8, 10 and 11 done, root collected. NOT COMPLETED (2026-10-10)

**Build under test.** main `4a40dc8`, fork `8af4f74e` (binary `scummvm-lv/scummvm` 11:00, newer than the fork commit).
- **Game copy.** `/tmp/claude-1000/vrun5/game` is an rsync of the part-4 copy with no `.bak` files. sha256 matches `shared/build/ARTIFACTS.sha256`: EUSECODE `709c6bd1…`, FIXED `22cada6f…` (root and `STATIC/`), U8SHAPES `69fbd861…` and TYPEFLAG `6bdb3036…`. The log reads `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1525518 bytes`.
- **Harness.** Xvfb `:96`, `frameLimit=true`, `usehighres=false`, `scale_factor=2`, no width/height keys; the log reads `Setting Video Mode 320x200`. The save dir is private. The driver is part 4's, copied and retargeted: `vrun5/py/v5.py` and `nav.py`. The session added `seek()`, a straight-line waypoint runner, and screen-driven conversation helpers.
- **Start.** `~/lv-checkpoints/run1010-s04b-m11-three-talismans.sav`: Map 11 (6212,18204,0), hp 30, three talismans held.

**Outcome.**
- **Furthest step completed: 11.** Tyorvi's "I will speak to Ezrekal for you." set tyorviDreams.
- **Step 12 is partway.** The root is in the pack but has not been handed to Ezrekal.
- **Step 9 is NOT done.** Thordis's Mark speech never played (finding 3), but the game still owes it: endOfPlantScene is 0, and its guard fires on her next talk.
- **Cheats: 0.** `Cheat` appears 0 times in `vrun5/lv_run.log`.
- **Console use.** Only `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object`, `saveGame` and `loadGame`. Two loads came after deaths.
- **Player input.** Everything else was mouse runs and walks, look clicks, double-clicks, drags and on-screen menu picks.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| 4: Fire talisman (5631,18943,4) | **PASS** | Fire doorway → (5584,18864). The drag logged `Dragging item 2560` and `Dropped item in backpack`, and weight went 50 → 60 (`s04-01`) |
| 4: way out of the Fire section | **PASS on the second line**; the first line was a death (finding 1) | The first line ran north toward the doorway: hp 30 → 23 → 14 → 8 → 0 at (5456,18640), with `CLRLAVA` (shape 409) usecode event 6 firing (`F1`). After a reload, a route with 192-unit margins round the LAKES chunks reached the doorway at hp 30 |
| 4: four pillars | **PASS** | Each receptacle was double-clicked from about 64-100 units with the pack closed; the log shows `Item: <rec> (shape 866) calling usecode event 1 @ 0478:00B4`. Earth ← Air: "The air talisman howls with fury!", then the column destroyed (`s04-02`, `s04-03`). Air ← Earth, Water ← Fire ("The fire talisman blazes…", `s04-05`) and Fire ← Water ("The water talisman glows with a cold light!") followed, then **"The way to the Lost Vale is open!"** (`s04-04`). Afterwards getGlobal 1697-1700 and 1772 all read 1, and `findShape 865` reports 0 found |
| 4: exit through T205 → Map 10 | **PASS** | Through the opened doorway x≈8532, then S, then E → **Map 10 (12800,2560,0)** (`s04-06`) |
| 5: Atli, first contact and Rite | **PASS** | At (19595,9995), daytide point. Picks: May I speak with you? → What is your name? → I am from Brittania. → On the other side of the barrier. → (troll-vomit rant) → I am not a Hoskuld! → **You will have to trust me.** → Why must I leave? → Is there some way I may stay? → Then I will become a Zealan. → **Rite of Passage?** Afterwards atliMet 1111 = 1 and testFromAtli 1070 = 1 (`s05-01`). This was one talk, not the guide's two (finding 6) |
| 6: Ragnar, first talk | **PASS** | Field point (7039,17151). "What is your name?" → "From very far away." / "I am new to your land." → Farewell. ragnarMet 1096 = 1 |
| 7: Ragnar's tale | **PASS** | The second talk opened with "Atli sent me to you." (`s06-01`). Then Atli admires you. → I believe that he is sincere. → He spoke of you and Hrodny. → He said you could help me. → Do you know of the Passage Stone? → Yes, I do. → **Why do you not go there?** gave the bag tale (`s07-01`). ragnarToldStone 1098 = 1 and ragnarPissed 1099 = 0. **The bag was not fetched**; I used the island stone instead |
| 8: Passage Stone, lake island (13888,18368,8) | **PASS** | Walked up the pier at x 13976 (z 8) from the south shore; hp 30, and no zombie egg hatched. The first drag from 250 units was refused; from (13976,18412) it worked: `Dropped item in backpack`, weight +10 (`s08-00`) |
| 8: ramp and Passage Test | **PASS** | Walked (12876,27648) → (12876,29272,64), then a short walk south hatched it. Afterwards haveMark 1041, avatarPoisoned 1028 and firstPoisoned 1034 all read 1, the stone was consumed (`findShape 798` lists only the template), and the Avatar was at (13055,30079,64) |
| 9: Thordis's Mark speech | **NOT DONE** (finding 3) | The witness was teleported to (12927,29823,64), and neither she nor the Avatar is drawn: both are behind the plateau rim (`s08-01`, `s08-02`). Clicks hit the rock (items 4796/16677). Later plantScene was 0 and endOfPlantScene 0, with Thordis home at (4415,7423) |
| 10: Ezrekal's history and poison thread | **PASS** | Stockade house. May I know your name? → I am from Britannia. → Yes, I am from outside. → Can you help me? → I have been poisoned. → But I'm dying! → Prepare my funeral?! → I don't want a funeral! → You said the Ancient Ones were gone! → What kind of eternal peace? → When will they return? → A city in the clouds? → I don't want to be an undead! → Cloud City? → How?! How can I be healed? → Where is the Cloud City? → Tell me more of the Cloud City. → Has anyone ever been there? → **Perhaps I will try the Cliffs.** ("to the sacred place I will…", `s10-03`). Afterwards ezrekalMet 1075, spokePoison 1091, spokeFuneral 1092 and sentToTyorvi 1047 all read 1 |
| 11: Tyorvi | **PASS** | At the stash (21439,7815). Do you have the Key to the Clouds? → Tell me of these nightmares. (the drunk dream bark, `s11-00`; **the talk did not end**) → How can you stop the dreams? → Have you spoken to Ezrekal? → **I will speak to Ezrekal for you.** (`s11-01`). Afterwards tyorviDreams 1060 = 1 |
| 12: root (21376,16640) | **PARTIAL** | The drag from (21347,16451) was refused (out of reach); from (21347,16683) it worked: `Dropped item in backpack`, weight 20 → 30. **Not handed over.** When I came back Ezrekal was in the garden (12580..12895,13124..13439), and I could not find a way to her from the house in the remaining budget |
| 12 (rest), 13-18 | **NOT DEMONSTRATED** (budget) | — |
| Log hygiene (`vrun5/lv_run.log`) | **PASS** | 0 each of: `stuck in process loop`, Segmentation, Assertion, `Unhandled intrinsic`, `Cycle in paint` and `Non-existent process` |

## Findings

1. **The Fire section's "harmless" lava lakes are damaging, and they kill a player who walks straight out from the Fire talisman.**
   - **The tiles.** The LAKES chunks use `GLOB_LAVA_LAKE` (802, 16× shape 409), and `objectInfo` reports them as `uc: CLRLAVA`: items 5864 (5631,18431), 9154 (5503,18431) and 2920 (5375,18431). They run usecode event 6 `@ 0199:0080` while the Avatar is beside or on them.
   - **What happened.** hp went 30 → 0 in about 33 s on the line north from the talisman at (5416..5520, 18544..18640): chunk (8,7) lies directly north of the talisman corner.
   - **What the builder says.** `build_map_11.py:495-497` says the lakes are "the Plane of Fire's yellow ground, which is walkable and harmless". The `hazards` assert at `:577-585` checks only the 318 pools and the flame traps, and `test_route_reach`'s damage-free claim cannot see these tiles either.
   - **Workaround.** A 192-unit margin round all ten LAKES chunks gave a clean route.
   - **Plate:** `F1-fire-lava-lake-death.png`.
   - **Confidence.** High that CLRLAVA does the damage: there was no monster near, and no other usecode fired in the death window. The exact damage rule is not traced.
2. **Ezrekal's menu lists "Tell me of the Shield." twice** after "Perhaps I will try the Cliffs." The menu reads: Where is the Sacred Circle? / Tell me of the Shield. / How can I awaken the Ancients? / Has anyone ever been there? / Key to the Clouds? / **Tell me of the Shield.** / bye (`s10-01-ezrekal-menu-duplicate-shield.png`). Probably an `askList+=` that should be `^=` in the "Perhaps I will try the Cliffs." case (`LP:EZREKAL.UNK` around 2024-2052) [INFERENCE, the source was not read]. It is cosmetic, a duplicate entry a player will see.
3. **After the Passage Test, the scene is invisible, so a player cannot find the witness.**
   - **The two teleports.** PLNTST moves the Avatar to (13055,30079,64) and Thordis to (12927,29823,64). Both lie south of the plateau rim, so the camera shows only the cliff face. That is plate `s08-01`, taken 30 s into the scene, and it shows no Avatar and no Thordis.
   - **Click attempts.** Walking north brought the Avatar back into view at (12907,29435), but Thordis stayed hidden behind the rim (`s08-02`). Double-clicks at her projected point hit rock items 4796 and 16677.
   - **What the game did next.** About 20 game-minutes later, the self-heal or schedule sent her home: plantScene 0, and endOfPlantScene still 0.
   - **Effect.** Step 9's speech is therefore deferred to her home (4415,7423). Per `LP:THORDIS.UNK:640-686` it plays on her next talk wherever she is; this was not exercised.
   - **Player-facing.** The scene does not say who the witness is, and a 320×200 player sees an empty cliff. 2026-10-09 played this talk on the plateau, so it may depend on the camera or resolution [INFERENCE].
4. **Deadly-lake margin on the south and east shore track.** I died twice by drowning (the grave screen, then position (0,0,0), hp 0), both while running between the documented track waypoints along x≈15400-15500:
   - (15231,20639) → (15600,18431);
   - (15419,15995,**z 1**) → (15487,15600).

   The lake zone's east edge is x 15360. The track's waypoints (15487,15871) and (15487,18431) sit 127 units from it, which is about one body width, and a run that drifts about 70 units west drowns. Route at x ≥ 15520 here: `exact_reach` with the lake box forbidden plus a 300 margin went N along x 15527 with no loss. Plate `F5-east-lake-shore-drowning.png`.
5. **Ezrekal's garden could not be reached from her house.** Inside the stockade, at (12779,12155) in the north fence gap, every south, SW and SE walk was refused (`vrun5/sp/ez33.png`). She was at (12580,13124) in the garden period. NOT DEMONSTRATED whether the garden opens elsewhere; for the 09-18 east door, see the route guide. This is an open question, not a confirmed defect.
6. **Atli's talk differs from the route guide.** The guide's "talk 1 ends at I am not a Hoskuld!" did not hold. "I am not a Hoskuld!" led to "Prove it!" and then "You will have to trust me.", and the same talk ran on to the Rite (`LP:ATLI.UNK:1166-1275,1510-1535,1669-1690`). This is not a defect; it saves a second talk.
7. **tyorviMet (1083) read 0** after a full Tyorvi talk that set tyorviDreams. The guide says the first talk sets it. I did not pick "What is your name?" [INFERENCE: that pick sets it]. Not a blocker.
8. **Fence and palisade wedges on Map 10 tracks.**
   - **Fork east track.** The Avatar wedged at (17399..17407,7959..8223), on the inside corner of the fence. A 0.8 s walk N freed him; the 640 u/s run did not (`sp/gun0.png`).
   - **Ezrekal's door.** The east door x 13983 wedged runs, and walk-gait steps cleared it.

## Harness anomalies

- **A fast click on a conversation row is sometimes dropped.** `xdotool click` with no settle time missed rows twice: Atli "Why must I leave?" and "Rite of Passage?". A mousemove, a 0.4 s settle, then a down/up with 0.25 s hold worked every time.
- **`save()` right after a conversation closes can fail silently** ("currently unavailable"). The slot mtime did not move. A retry 2 s later worked, and the s07 bank was re-copied from the good save.
- **`nav.go` stalls.** It fails when the start snaps to an unreachable lattice level (the root spot at z 8) and when the first leg is blocked by a fence. `seek()` with alternating run and walk recovered both.
- **NPC double-clicks.** Moving NPCs need the click on the current sprite. `chase_click`, which clicks the blue pixel centroid, worked first time for Ragnar.

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `run1010-s04c-m11-four-talismans.sav` | `bd49ee81…` | Map 11 (5584,18864,0), hp 30, all four talismans |
| `run1010-s04d-m11-pillars-destroyed.sav` | `4834d4bb…` | Map 11 (7808,21824,0), all pillars down, 1772 = 1 |
| `run1010-s04e-m10-arrival-step4-done.sav` | `cb92359a…` | Map 10 pad 205 (12800,2560,0). **Step 4 done** |
| `run1010-s05-m10-atli-rite.sav` | `8ad826c8…` | Near Atli (19316,9652), atliMet and testFromAtli set |
| `run1010-s07-m10-ragnar-told-stone.sav` | `142b5131…` | Ragnar field (7212,17472), ragnarMet and ragnarToldStone set |
| `run1010-s08-m10-passage-test-marked-poisoned.sav` | `a78b57f1…` | Plateau (12907,29435,64), haveMark and poisoned set |
| `run1010-s10-m10-ezrekal-sent-to-tyorvi.sav` | `1ca4466a…` | Ezrekal's house, sentToTyorvi set |
| `run1010-s11-m10-tyorvi-dreams.sav` | `3955cb02…` | Tyorvi's stash, tyorviDreams set |
| `run1010-s12a-m10-root-in-pack.sav` | `60fb9c74…` | Sacred Circle (21347,16683), root in the pack, weight 30 |
| **`run1010-s12b-m10-root-inside-ezrekal-stockade.sav`** | `560da6fb…` | Map 10 (12779,12155,0) in Ezrekal's north fence gap, root in the pack, hp 30. **Resume point** |

## Resume here

1. **Load.** Load `run1010-s12b-…`, send `debugflag_enable Object`, then one look-click.
2. **Reach Ezrekal and hand over the root.** She is in the house (12799,12543) or the garden (12895,13439) in firstebb and lastebb.
   - Either wait in-game for her to come inside, or find the garden entrance (finding 5).
   - Pick "I have found the root." (givenRoot 1063).
3. **The brewing wait.** Walk away to about (14662,14214) until her `leaveFastArea` fires. Come back and pick "Have you made the elixir?".
4. **Tyorvi, the Key.** Take the vial to Tyorvi: something from Ezrekal → elixar → heal dreams → Just try it → May I have the Key.
5. **Thordis at home (4415,7423)** for the deferred step-9 speech (endOfPlantScene 1050).
6. **Then step 13 onward** per `/tmp/claude-1000/run1009/route-guide.md`.

**Shore hazard.** Keep x ≥ 15520 on the east shore (finding 4).

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-10-full-run-part5/`: 19 plates (`s04-01…06`, `s05-01`, `s06-01`, `s07-01`, `s08-00…02`, `s10-01…03`, `s11-00…01`, `F1`, `F5`).
- **Wrote** the 10 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/vrun5/`: `game/`, `saves/`, `sp/` (screens and `w-*.sav`), `py/`, `lv_run.log`, `trace.txt`, `er_*.pkl` and `scummvm.ini`.
- **Stopped:** my ScummVM and Xvfb `:96`.
- **Not touched:** source, builders, maps, the fork, `TODO.md`, `HANDOFF.md` and `shared/`.

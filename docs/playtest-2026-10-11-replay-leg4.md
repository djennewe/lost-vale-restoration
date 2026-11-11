# Single-build replay of the 1→18 run, leg 4: steps 10-12 done, step 13 partway (both Shield halves held, at the Map 13 summit) (2026-10-11)

Leg 4 of the one-build replay. It continues from leg 3's banked save on the same pinned game copy (`docs/playtest-2026-10-11-replay-leg3.md`). The session stopped at the request budget, not on a defect.

## Build pinned (re-checked)

- **Game copy.** `/tmp/claude-1000/replay/game`, as legs 1-3 left it; it was not re-copied. Running `sha256sum -c ../pinned.sha256` inside it gave OK for all six files at the start (20:22) and at the end (22:22): EUSECODE `4182e079…`, FIXED (root and `STATIC/`) `122b4374…`, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`.
- **Binary.** `/tmp/claude-1000/pinned-bin/scummvm-4182e079` (sha256 `1502d576…`). One process ran the whole session. The log (`replay/lv_run4.log`) reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)`, `usecode/eusecode.flx: d00d0d5962e966129c2277c7cea7844b, 1526311 bytes` and `Setting Video Mode 320x200...`.
- **Harness.**
  - The ini is the same (320×200, music on, `SDL_AUDIODRIVER=dummy`), on Xvfb `:95`.
  - The driver is leg 1's `rp.py`/`navr.py`, used from the eval kernel. The prime left click was off (`rp.PRIME=False`), and every run began with a sacrificial 0.2 s right press.
  - Menus were read from the screen. Red menu rows are found by their bullets. The wanted option is matched by its **total pixel width**, predicted exactly from the glyph widths of `U8FONTS.FLX` font 0: width = 2·Σ glyph width − 4, which held to the pixel on every menu.
  - A pick needed a unique match within ±4 px. Otherwise the driver stopped and I picked from a screenshot of the menu.
  - Every pick is on a contact sheet (`C1`, `C2`) or a menu plate (`A1`, `B1`).
- **Cheats: 0.** `Cheat` appears 0 times in `lv_run4.log`. The console was used only for `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object` and `saveGame`. There were no loads.
- **Deaths: 0.** hp was 30 at every read.

## Outcome

- **Furthest step completed: 12.** The Key to the Clouds is in the pack, q170.
- **Step 13 is partway.** EggCloudCliffs fired and the climb is done: climbedCliffs 1031 = 1. Both Shield halves are in the pack, and the Avatar is at the Map 13 summit landing (4096,512,120), on the way back down to the Vale.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| 10: to Ezrekal | **PASS** | Ramp foot → lattice route N, then NE, then N along x≈15855 (lake +420), then into the stockade by the east door → (13159,12807). hp 30 |
| **10: Ezrekal, poison thread** | **PASS** | All picks were taken from the screen, as listed under "Ezrekal's talk" below. The talk ended on **Perhaps I will try the Cliffs.** The menu after it, "Tell me of the Shield. / Where is the Sacred Circle? / How can I awaken the Ancients? / Key to the Clouds? / bye", lists the Shield **once** (`A1`), so part 5 finding 2 is fixed on this build (`lv-patched/EZREKAL.UNK` M5). ezrekalMet 1075, spokePoison 1091, spokeFuneral 1092 and sentToTyorvi 1047 all read 1 (`A2`) |
| **11: Tyorvi** | **PASS** | He was at Hoskuld (7423,7519) and the double-click logged `Item: 115 … event 1 @ 0473:0354`. Do you have the Key to the Clouds? → Tell me of these nightmares. (the dream bark ran for about 60 s) → How can you stop the dreams? → Have you spoken to Ezrekal? → **I will speak to Ezrekal for you.** tyorviDreams 1060 = 1. tyorviMet 1083 = 0, as in part 5 finding 7 |
| 12: root | **PASS** | On this pinned build the root is **shape 399**, item 19947 at (21376,16640,0), the pre-`b3afce6` shape; `findShape 869` reports 0. From (21355,16651,8) the drag logged `Dragging item 19947` → `Dropped item in backpack`, and weight went 20 → 30 |
| 12: root handed over | **PASS** | Ezrekal was found in the stockade by colour tracking, and the click logged `event 1 @ 0474:034A`. The menu read "I have found the root. / Can you help me? / bye". After the pick the next menu offered "Is Tyorvi's elixir ready yet?" (`B1`). givenRoot 1063 = 1 and justGotRoot 1064 = 1 (`B2`), and weight went 30 → 20 |
| 12: brewing wait | **PASS** | I walked away to about (14551,13951) and back. The log shows `Item: 116 … event 16 @ 0474:0264`. Afterwards 1064 read 0 |
| 12: elixir | **PASS** | "Have you made the elixir?" was picked from the screen. Afterwards 1827 = 1 and 1062 = 1 (`B4`), and weight went 20 → 30 |
| **12: Key, drunk path** | **PASS** | She was at the stash (≈21650,8000). **Talk 1:** I have something for you from Ezrekal. → It is an elixar. → It is a potion. → It will heal your dreams. → **Just try it, please.** → the talk exits (`C1`). **Talk 2:** the same chain → **Shut up and drink it!** → silent pause → menu "May I have the Key to the Clouds? / bye" → Key (`C2`). `findShape 82`: item 4185, **q 170**, `f: 0xc`. givenTea 1061 = 1, iAmDrunk 1828 = 1 and 1062 = 1 (`C3`). Weight stayed 30 |
| 13: Map 10 → Map 13 | **PASS** | Stash → Gunnar → S along x 16215 → W along y 21271 (lake +790) → terrace (7019,23435,8) → **Map 13 (4096,12096,0)** |
| 13: EggCloudCliffs with the q170 Key | **PASS** | A walk N past the egg at (4096,11264) gave two barks: "The ancient handholds carved into the cliff face glow faintly as I approach. This must be the path." (`D1`), then "The wind howls around me, but the handholds hold firm. The Zealans built well." (`D2`). attemptedCliffs 1039 read 1 at once. climbedCliffs 1031 read **0 after 15 s unpaused and 1 after the climb** (`D2b`), the same lag as in part 6 |
| 13: the climb | **PASS, 0 falls** | I used an erosion-0 DryReach lattice from the pinned FIXED with 1.0 s legs: (4096,11544,0) → (3988,8156,20) → (4192,7128,32) → (4948,5540,60) → (4136,2536,104), then N runs to the summit. Teleporter 209 → **Map 17 (5376,11032,0)** (`D3`). There were no `DROP`s and hp stayed 30. Contrast part 6 finding 2, which had 6 falls |
| 13: Shield halves | **PASS** | Drag 1: `Dragging item 21439` → `Dropped item in backpack` (q81), weight 30 → 70. Drag 2: `Dragging item 19622` (q82), weight 70 → 110. Both now read `f: 0xc`. Each drag came from (≈6224/7248,1688), with the half east of the Avatar and the skeleton not in the way |
| 13: Map 17 → Map 13 | **PASS** | S along x 5376/5508 to the 208 pad → **Map 13 (4096,512,120)** |
| 13: descent and Map 10 return; 14-18 | **NOT DEMONSTRATED** (budget) | — |
| Music on | **PASS (no hang)** | 2 h of play; the console answered throughout |
| Log hygiene (`lv_run4.log`, 14,165 lines) | **PASS** | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Unhandled intrinsic`, `Cycle in paint` and ERROR |

### Ezrekal's talk

Every pick was taken from the screen:

May I know your name? → I am from Britannia. → Yes, I am from outside. → Can you help me? → I have been poisoned. → But I'm dying! → Prepare my funeral?! → I don't want a funeral! → You said the Ancient Ones were gone! → What kind of eternal peace? → When will they return? → A city in the clouds? → **Where will I be until then?** → I don't want to be an undead! → Cloud City? → How?! How can I be healed? → Where is the Cloud City? → Tell me more of the Cloud City. → Has anyone ever been there? → **Are the Ancient Ones still there?** → Perhaps I will try the Cliffs.

## Findings

1. **Part 5's step-10 pick list is out of date (route guide drift, not a defect).** Two options must be picked that part 5 does not list:
   - **"Where will I be until then?"** After "A city in the clouds?", the menu offers "I want to be healed! / Where will I be until then? / bye". "I don't want to be an undead!" is added only by the second option (`lv-patched/EZREKAL.UNK:1753-1787`).
   - **"Are the Ancient Ones still there?"** "Perhaps I will try the Cliffs." is added only by that case (`:2112-2142`), as the M5 header note says (`:322-327`). After "Has anyone ever been there?", the menu read "Tell me of the Shield. / How can I awaken the Ancients? / Are the Ancient Ones still there? / bye".
2. **The climb took no falls.** With an erosion-0 lattice built from the pinned FIXED and 1.0 s legs, the climb went from the foot to z 104 without a single drop. The legs went to the lattice's own route points, and the route jogged E at (4568-4948, 5540-5816) past the bend where part 6 fell. Part 6 finding 2 therefore reads as a driver effect, not as terrain that drops a careful walker [INFERENCE: one run].
3. **climbedCliffs (1031) lags.** It read 0 for about 15 s of unpaused play after both cliff barks, and 1 after the climb. This repeats part 6's note. Low severity, because nothing gates on it before the summit.
4. **Tyorvi's dream bark is long.** "Tell me of these nightmares." keeps the talk on about six bark pages, about 60 s with clicks. The menu then comes back in the same talk. That matches part 5, and this is not the talk ending.
5. **A Map 10 monster egg sits at (15500,13000), on the walk from the stockade east.** An egg-margin lattice gave NO ROUTE from (15479,13271). The pinned FIXED has ten shape-500 eggs on Map 10. Three are off the lake: (8500,13000), (15500,13000) and (10500,19500). Nothing hatched in this session. This is a note only.
6. **Ezrekal and Tyorvi move between the console read and the click.** Aiming from `objectInfo` alone missed three or four times each, because the console pauses the world and they walk on once it closes. Two things worked: a colour-tracked click on Ezrekal's robe (82,8,0), and a click on robe pixels within 90 px of Tyorvi's projected point taken right after the sacrificial click. Both took 1-4 tries. This is the same pattern as part 7 finding 2.

## Harness anomalies

- **`navr.get_er` builds its lattice from `shared/build/FIXED.DAT`** through `exact_reach.load_map`'s defaults (`DEFAULT_FIXED`), not from the pinned copy.
  - **What I changed.** From the stash onward, every lattice was rebuilt from `game/STATIC/FIXED.DAT` + `TYPEFLAG.DAT`. The leg-3 pickles were reused for the ramp → stockade and Hoskuld legs. The circle-area lattice used on the root trip (ROI 15000-22800 × 12000-18500) was a `shared/build` one; I deleted it once I noticed.
  - **Reading.** It routed correctly on the ground it covered.
- **The menu matcher's word-gap split fails.** Glyphs with a negative x-offset ('f') close the space after "am" to 6 px. The total-width test has no such problem. One 2-px kerning miss ("Tell me more of the Cloud City.", 356 against 358) tied with another option and was picked by hand.
- **Lattice routing on the whole-Vale ROI takes 30-100 s per replan.** Smaller ROIs build in under 2 s.
- `saveGame` worked every time (10 of 10).

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `replay1011-s10-m10-ezrekal-sent-to-cliffs.sav` | `9e081d30` | Stockade (13159,12807), 1075/1091/1092/1047 = 1 |
| `replay1011-s11-m10-tyorvi-dreams.sav` | `e610345a` | Hoskuld (7471,7415), 1060 = 1 |
| `replay1011-s12a-m10-root-in-pack.sav` | `5e4f37ad` | Sacred Circle (21355,16651), root 19947 in the pack, w 30 |
| `replay1011-s12b-m10-elixir-in-pack.sav` | `b9dd2f0f` | Stockade (12771,12739), 1063/1827/1062 = 1, w 30 |
| `replay1011-s12c-m10-cliff-key-q170.sav` | `4e33dae6` | Stash (21627,7971), Key 4185 q170, 1061 = 1. **Step 12 done** |
| `replay1011-s13a-m13-cliffs-egg.sav` | `146a6a92` | Map 13 (4096,11544,0), 1039 = 1, 1031 = 0 |
| `replay1011-s13b-m17-cloud-city-arrival.sav` | `fe2fcca4` | Map 17 (5376,11032,0), 1031 = 1 |
| `replay1011-s13c-m17-both-shield-halves.sav` | `57707efe` | Map 17 (7248,1688,0), halves 21439 and 19622 in the pack, w 110 |
| **`replay1011-s13d-m13-summit-with-halves.sav`** | `138f162b` | Map 13 (4096,512,120) at the summit landing, both halves, Key, hp 30, w 110. **Leg 5 resume point** |

Scratch saves are in `/tmp/claude-1000/replay/sp/l4-*.sav`.

## Resume (leg 5)

1. **Start.** Use the same game copy, binary and ini. Copy `replay1011-s13d-…` to `saves/ultima8.001`, launch with `--save-slot=1`, then send `debugflag_enable Object`.
2. **Descend Map 13 and return to the Vale.**
   - Descend with the reverse of the erosion-0 climb route. Its waypoints, top to bottom: (4136,2536,104), (4136,4744,80), (4364,5156,72), (4948,5156,64), (4948,5540,60), (4568,5816,52), (4036,5940,48), (4192,7128,32), (3988,8156,20), (4220,9492,8), (4096,10440,0).
   - Then step onto teleporter 206 at **(3328,11520,0)** to reach Map 10 (7168,23296,8).
   - Map 13's monster eggs are at (4096,768), (4608,1280), (3584,1536) and (4352,1792), z ≈ 100-110. The summit landing is beside them, so leave promptly.
3. **The ceremony (steps 14-15).** Go S of the lake (y ≈ 21300 held clear of the lake) to (20364,17532), then walk N. Per part 6: Let's be reasonable! → Yes, Priestess. → Please, High Priestess.
4. **Then, per parts 6 and 7:**
   - Hrodny: How can I open the temple? Take the key from **her bag**, which appears at about (19588,23284).
   - The chest and the Tiny Tar.
   - Processional → Map 18, then the crack, then the altar: approach W, then N.
   - Trigger 210 → EggEndgame → Ezrekal "I have freed your gods!".

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-replay-leg4/`, which holds 12 plates: `A1-A2`, `B1-B2`, `B4`, `C1-C3`, `D1-D3`, `D2b`.
- **Wrote** the 9 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/replay/`:
  - `lv_run4.log`, `trace4.txt`, `sp/l4-*.sav`, the talk frames `sp/{ez,ez2,ty,ty2,ty3,m13,cc}-*.png` and `sp/g-*.png`;
  - two new lattice caches, `er_10_12000_6000_22800_14000_1_1740554504832528599.pkl` and `er_10_15000_12000_22800_18500_1_1740554504832528599.pkl`, which I deleted (both were built from `shared/build`);
  - the pinned lattices lived only in the kernel.
- The game copy is unchanged; its hashes were re-checked at the end.
- **Stopped:** my ScummVM (`pinned-bin/scummvm-4182e079 --config=/tmp/claude-1000/replay/scummvm.ini`) and the Xvfb `:95` that my start launched. Other agents' Xvfb (`:92`, `:94`, `-displayfd`) were left alone.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and both binaries.

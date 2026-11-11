# Build 7 verification: puzzle persistence, 212/206 slabs, MIDI lock, cliff key, Fire line, Ezrekal's door, plateau rim (2026-10-11)

**Build under test.** main `3e52ca6`. Game copy `/tmp/claude-1000/vb7/game`, sha256 equal to `shared/build/ARTIFACTS.sha256`: EUSECODE `2ca7b486…` (log: `usecode/eusecode.flx: d00d0d59…, 1526011 bytes`), FIXED `e03510ec…` (root and `STATIC/`), U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`. Binary `scummvm-lv/scummvm`, built 2026-10-10 22:41, after fork commit `b867a30c` (20:30).

**Harness.** Xvfb `:94`, 320×200 ini with no width/height keys. **Music on**: no `music_driver` key (auto: Miles AdLib), `mute=false`, `SDL_AUDIODRIVER=dummy`. `frameLimit=true`. Driver `vb7/py/v7.py` + `nav7.py`, copied from part 6. Films were taken with `ffmpeg x11grab` at 25 fps.

**Cheats.** Cheats were on for debug teleports *to a start point*. Every trigger, egg and scene under test was **walked into**, and the egg or teleport hatched in the log. Cheats were off for every talk.

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| P1 | Map 11 pillars and q299 boulders stay gone across a hop; a pre-solve hop keeps them | **PASS** | s04d hop 205→Map 10→walk 204: `findShape 865` 0, q299 66 none, pad room exits north. s04b control: 865 = 4, both q299 boulders present, doorway sealed |
| P2 | Map 10 Test Plant stays gone after haveMark across a hop; present before | **PASS** | s08 hop (walked 205): 126 q10 none. s07 control, same hop: 126 q10 at (12800,29408,64) |
| G1a | 212 slab (20639,3967) visible at 320×200; Avatar drawn on it | **PASS** | `G1-view-slab-from-west`, `G1-key-E-start-slab-visible`, `G1-key-E-avatar-on-slab` |
| G1b | Mouse and keyboard walks onto 212 fire it | **PASS**, 7 of 7 | Mouse walk E, W and SE; mouse run E; key Up E; key Up S; Shift+Up E. All loaded Map 10 |
| G1c | North in the doorway column does not fire 212 | **PASS**, 3 of 3 | Mouse walk N and key N at x 20382-20383 went through the doors to **Map 9**. A mouse run N at x 20495 ended at (20799,3143) on Map 8. None loaded Map 10 |
| G1d | Map 13 206 slab visible from pad 207 and fires on a walk W | **PASS** | `G1-206-view-from-pad207` (slab 80 px left of the Avatar). A walk W from (4052,11676) loaded Map 10. The Avatar is drawn on the slab: `G1-206-walkW-avatar-on-slab` |
| M1 | 100+ combat toggles at varied intervals, during music transitions too: no hang; combat music starts and stops | **PASS** (start of combat music inferred) | **280 toggles**, 140 `Doing a MIDI transition! trans: 9` lines, 0 hangs. Toggles ran at 20 ms-1.5 s intervals: standing, walking, crossing 212, and in bursts begun on the `Loading Fixed items in map 10` line. The game answered the console after every series |
| T1 | The q170 key climbs; a non-170 key does not | **PASS** | q170 key: hatch `event 7 @ 05A8`, bark "The ancient handholds … This must be the path." (`T1-q170-egg-6`), climbedCliffs 1031 0→1. q99 key (cp22-hastea, no 170 in the pack): bark "The cliff face rises … require some sort of key or token…" (`T1-neg-q99-egg-6`), 1031 stays 0 after 20 s unpaused |
| T2 | After the Key, the accompany chain, then the next visit says 'You weren't at the cliffs.' once, then the normal menu | **NOT DEMONSTRATED** | The accompany chain is reached only through "She told me of the cliffs.", which needs toldCliffs (Hrodny). From s12d it was not offered (`T2-spoken-ezrekal-menu`). See finding 4 |
| E1 | Ezrekal lists 'Tell me of the Shield.' once after 'Perhaps I will try the Cliffs.' | **NOT DEMONSTRATED** | Budget. It needs a talk of about 19 picks from s09 |
| L1 | Map 11 from the Fire talisman, straight N/NE to the east doorway: no hp loss | **FAIL** (the straight N line) | 4 of 5 lines kept hp. **Walking straight N from the talisman's column (x 5560) lost 2 hp**: 30→28, with two `Item: 12231 (shape 318) calling usecode event 6 @ 013E:00B6`. Item 12231 is a **FIREPIT** (318) at **(5632,16384,0)**, due north of the talisman (5631,18943) (`L1-firepit-on-north-line`) |
| D1 | Ezrekal's east door: a run W through y 12480-12620 passes the doorway | **PARTIAL** | Passes at y 12480, 12500, 12503, 12579, 12584, 12586, 12610 and 12620 (once). **It stopped at (14070,12686..12706), outside the door, in 3 of 4 runs at y 12600-12620** (12600 twice, 12620 once). A walk at 12620 passed. The control at y 12450 stopped at 14054, as the wall requires |
| R1 | Plateau rim at 320×200: the Avatar and the witness are visible after the test teleport | **PASS** | s07 + the stone, walked into EggPlantTest (`event 7 @ 059A`). Avatar (13055,30079,64) and Thordis (12927,29823,64) are both drawn, and the rim is below them (`R1-after-test-teleport`) |
| L | Log hygiene | **PASS** for this change, with stock noise | 0 each of `stuck in process loop`, Segmentation, Assertion, `Unhandled intrinsic`, `Non-existent process`, `Trying to access segment`, `popToContainer` and ERROR. 11 `Invalid item … area search` over 38 map loads; 3 `Invalid procid … in waitlist`. **2,068 `Cycle in paint`**, see finding 3 |

## P1: Map 11 puzzle persistence — PASS

- **Solved state** (`run1010-s04d-m11-pillars-destroyed`). On load, `findShape 865` gave 0 found and there was no q299 shape 66.
  - Out: walked S through the doorway into 205's box, and Map 10 loaded at (13004,2764).
  - Back: walked NW then N into trigger 204 at (11904,2048), and Map 11 loaded at (8291,22607), pad 204.
  - After the hop: 865 = 0 and q299 = none. The four receptacles (866) are still there.
  - Walking E/NE/N from the pad left the room through the doorway to (8595,21887) (`P1-arrive-204-m11`, `P1-padroom-exit-north`).
- **Control** (`run1010-s04b-m11-three-talismans`). On load, 865 = 4, and q299 boulders 29180/29181 stood at (8576/8704, 22528).
  - I debug-teleported to Map 10 (11900,2750) and walked N into 204. Map 11 loaded at (8291,22607).
  - After the hop: 865 = 4 and q299 boulders 20966/21617. The same walk out stopped at (8603,22607), sealed (`P1-neg-presolve-hop`, `P1-neg-padroom-sealed`).
- **Not run:** the 203 return (Map 9). It is the same egg class on the other arrival pad.

## P2: Test Plant — PASS

- `run1010-s08` (haveMark set): 126 q10 none on load. I debug-teleported to Map 11 (8400,22700) and walked SE into 205, which loaded Map 10 at pad 205. 126 q10 stayed none, and 126 was 5 found before and after.
- Control `run1010-s07`, same route: 126 q10 was item 31663 at (12800,29408,64) on load, and item 1539 at the same spot after the hop. That confirms FIXED.DAT carries the plant, and that a hop re-reads it without haveMark.

## G1: 212 on Map 8 and 206 on Map 13 — PASS

Start `run1010-s03b`. I debug-teleported to Map 10, then walked N into 213 to reach a freshly loaded Map 8 (niche (20143,3143,8)), and walked back by 213 after every trial.

| Input | Start | Result |
|---|---|---|
| Mouse walk SE | (20431,3791) | Map 10 |
| Mouse run E (positioning leg) | (20139,3884,8) | Map 10 |
| Mouse walk E | (20237,3953,8) | Map 10 |
| Mouse walk W (positioning leg) | (20947,3947) | Map 10 |
| Key Up facing E | (20272,3928) | Map 10. Film: the Avatar's feet are on the slab, drawn, one frame before the fade (`G1-key-E-avatar-on-slab`) |
| Key Up facing S | (20627,3593,8) | Map 10, arrival (13824,3616), no bounce |
| Shift+Up facing E | (20264,3904) | Map 10 |
| Mouse walk E along y 4111 (south of the box) | (20383,4111) | No fire, ended (21111,4111). Correct: the box is y [3871,3999) |
| **Neg.** mouse walk N, doorway column | (20383,4279) | Through the doors to **Map 9** (pad 201) |
| **Neg.** key N, doorway column | (20382,4274) | **Map 9** |
| **Neg.** mouse run N | (20495,4247) | Stayed on Map 8, ended (20799,3143) |

Map 13: I walked into 207 from the terrace lane at x 7252, and the Avatar landed on pad 207. From the pad the pale slab shows at the expected pixel (`G1-206-view-from-pad207`). A walk W fired 206 to Map 10 (6768,23296,8) with the Avatar visible on the slab.

## M1: MIDI under combat toggling — PASS

The `c` key was sent through xdotool. 70 toggles were sent standing on Map 8, and 48 while walking. 48 + 40 + 46 more went in while walking across 212/213, and 28 in a burst started on the Map 10 load line. Every series ended with an even count.

The log carries 140 `trans: 9` lines, one per combat exit. That is the `restoreMusic()` transition the hang was racing. Combat entry is not logged, so **combat music starting** is inferred from the leave transitions [INFERENCE]: there is no audio capture on the dummy driver. The binary postdates the lock commit. There was no freeze, and every `objectInfo` was answered.

## T1: Cliff key quality — PASS

- **q170.** `run1010-s12d`; key 10999 q170 in the pack.
  - Route in: walked into Map 10's 207 by the x 7252 lane, beside the closed terrace gate 9902 (114, q170). The key's double-click logged `event 1 @ 0052:04BB` and `Target result: Item 9902`, and the gate stayed shape 114.
  - On Map 13 I walked N from pad 207 into EggCloudCliffs. The positive bark showed, and climbedCliffs 1031 read 1 after ~25 s unpaused.
  - The physical climb was not repeated; part 6 did it on this key.
- **q99.** `cp22-hastea`: q99 key 4528 in the inventory, no 170 key anywhere (q20 key 10550 on the map).
  - I teleported to Map 13 (4096,11800), waited 20 s, then walked N into the egg (`event 7 @ 05A8`). The refusal bark showed, attemptedCliffs went to 1, and climbedCliffs stayed 0.

## T2: Tyorvi after the Key — NOT DEMONSTRATED

From `run1010-s12d` (tyorviMet 0, iAmDrunk 1, givenTea set, Key held):

- **Talk 1.** "What is your name?" (`T2-talk1`, `-name`) gave the drunk monologue, and the talk ended. tyorviMet went 0→1.
- **Clearing iAmDrunk.** A 1,600-unit walk away cleared it (leaveFastArea).
- **Talks 2-4** opened on **"Calm down, Tyorvi."** (tyorviPissed set).
  - "I wish to apologize for my rudeness." got "Well, a much better attitude you have now. Speak to you I will." (`T2-apology`), and tyorviPissed 1086 read 0 afterwards. So T5 works.
  - The next menu added "I have spoken to Ezrekal." That led to "She told me of the poison. / She told me of my funeral." (`T2-spoken-ezrekal-menu`), with **no "She told me of the cliffs."** (toldCliffs unset). There is no other road to "Yes, accompany me." from this save.
- **What would test it:** a save with toldCliffs set (after Hrodny's cliffs case) and the Key. Banked for that: `vb7-m10-climbed-key-q170-pad206` (attempted + climbed set, tyorviDrunk 0, tyorviPissed 1 at save time).

## L1: Fire talisman to the east doorway — FAIL on the straight N line

Each run started from a teleport to (5560,18880,0), 71 west of the talisman, on a Map 11 reloaded by walking in through 204.

| Line | End | hp |
|---|---|---|
| Walk N 4.5 s, E | (6090,17502), at the east wall short of the doorway | 30→30 |
| Run NE, N, E | (6108,17516) | 30→30 |
| Run N 3.2 s, NE | **(6252,16676), through the doorway** | 30→30 |
| **Walk N 9 s, E** | (6108,16156) | **30→28**; two gotHit events on FIREPIT 12231 |
| Walk NE 2.5 s, N | (6108,15828) | 29→29 |

FIREPIT 12231 (shape 318, `uc: FIREPIT`) stands at (5632,16384,0), exactly on the talisman's x and level with the doorway's south jamb (16384). A player who picks up the talisman and walks north toward the doorway's latitude walks into it. The runs that passed it stayed east of it or stopped short.

[INFERENCE] The pit moved with the lakes in `ccc479d`, and the five "natural lines" in `test_route_reach` measure lava (409) only, not 318.

## D1: Ezrekal's east door — PARTIAL

| Start y (x 14004-14407) | Gait | End | Passed |
|---|---|---|---|
| 12450 (control, below the opening) | run | (14054,12450) | no (correct) |
| 12480 | run | (13670,12480) | yes |
| 12500 / 12503 | run | (13654,12500) | yes |
| 12558 | walk | (13632,12474) | yes |
| 12579 / 12584 / 12586 | run | (13476..13736, 12586..12792) | yes |
| **12600** | run ×2 (one filmed) | **(14070,12686) both** | **no** |
| 12610 | run | (13382,12610) | yes |
| **12620** | run ×2 | (14070,12706), then (13566,12620) | **1 of 2** |
| 12620 | walk | (13508,12670) | yes |

The filmed failure shows the running Avatar pitching into the stumble pose, then ending SE of the doorway, outside the stockade (`D1-row12600-run-stumble`). Both failing runs end at the same (14070, ~12690). [INFERENCE] Something east of the door near y 12620-12700 refuses the running step, as the part-5 track wedge did. `findShape 425` lists no track tile in x 13900-14400, so I did not identify it. Check with `exact_reach` at x 14006-14070, y 12600-12700.

## R1: Plateau rim at the Passage Test — PASS

- `run1010-s07` has no stone in the pack; the first walk-in hatched the egg with nothing to consume.
- `Item::grab 30091` took the Passage stone (798) from (13888,18368,8). A hop to Map 11 and back re-armed the egg, and the walk-in hatched `event 7 @ 059A`. The stone was consumed (weight 30→20).
- Avatar (13055,30079,64) and Thordis (12927,29823,64) are both drawn at 320×200, standing on the plateau with the rim below them (`R1-after-test-teleport`). This contrasts with part 5's finding 3.

## Findings outside the brief

1. **L1's FIREPIT on the talisman's north line.** See above: −2 hp, item 12231 at (5632,16384,0).
2. **The S hold off Map 13's pad 207 ends with the Avatar hidden.** Walking S from the 207 arrival (x 7252 lane, held 2 s) ended at (4096,12272,0) against the south rim. **The Avatar is not drawn there**: the rim's cliff face covers the screen centre, 2 s and 10 s after the load (`F-m13-rim-avatar-hidden`). This is the designed stopping place for S holds (build_map_13's 206 comment).
3. **Paint cycles.** 2,068 `Cycle in paint dependency graph` lines in total:
   - 1,394 `590 -> 235 -> … -> 590`, 21 `235 -> 65 -> …` and 12 `358 -> 1 -> …` while Map 8 was loaded;
   - 640 `235 -> 65 -> … -> 235` while Map 10 was loaded.
   
   These are shape numbers. The Map 8 ones accrued during the 212 trials around the bone field. Not traced.
4. **T2 depends on toldCliffs.**
   - The only roads to "Yes, accompany me." are "She told me of the cliffs." and "Tell me more of the Cliffs.". Both need toldCliffs, which Hrodny writes.
   - Also: after the apology the same menu still lists "Calm down, Tyorvi." and "I wish to apologize…" for the rest of that talk (`T2-after-apology-menu`). It is cosmetic, because tyorviPissed did read 0.
   - Talk 1 from s12d (first meeting, drunk) set tyorviPissed by the next talk [INFERENCE: the drunk first-meeting branch]. A player who meets Tyorvi drunk has to apologise before any quest option appears.
5. **Map 10 → 13 terrace gate.** Gate 9902 (114, q170) did not open after the key was used on it: the target logged and the shape stayed 114. The x 7252 lane beside it reaches 207 anyway, as in part 6. [INFERENCE] The gate is decorative or the lane bypasses it; this was not examined further.
6. **The doorway-column negatives go to Map 9 with the doors open** (s03b state survives the hop: doors are non-fixed). This is expected behaviour and agrees with maps3 G3.

## Harness anomalies

- **The first mouse input after a console close is often swallowed** (part 6 finding 4). Placement needed 2-6 retries, and the trial functions re-send a leg that produced <40 units.
- **`nav7.go` primed with a left click at (320,150), with cheats on, and opened the retail dev menu.** I closed it with "Done", and priming was off afterwards.
- `nav7` printed NO ROUTE on Map 10's court and around Tyorvi. The cached lattices are part 6's; walked by hand.
- Blind advance clicks (320,60/100) during a bark can land on an ask-menu row when the menu is drawn there. That cost one Tyorvi talk. Red-pixel menu detection over the whole frame fixed it.
- `ffmpeg x11grab` needs ~1.5 s to start. The first G1 film started after the teleport.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-build7/` (36 plates).
- **Banked** `~/lv-checkpoints/vb7-m10-climbed-key-q170-pad206.sav` (Map 10 pad 206; Key q170; attempted + climbed set; tyorviMet 1; tyorviPissed 1 at save time).
- **Scratch** `/tmp/claude-1000/vb7/`: the game copy, `saves/` (slot 1 overwritten by the checkpoints loaded), `sp/` (shots, films, the in-session save), `py/`, `lv_run.log`, `trace.txt`, `scummvm.ini`, and symlinks to part 6's Map 10/13 lattice pickles.
- **Stopped** my ScummVM (pid 3776058) and Xvfb `:94` (pid 3776052).
- No source, maps, fork, TODO.md or HANDOFF.md edits.

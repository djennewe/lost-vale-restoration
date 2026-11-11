# Fix 10 verification: Map 13 curbs on both lane edges and round every bend, Tyorvi T12 (2026-10-11)

**Build under test.** main `40cdf5c` (fix 10 merged: `d2e202e` Map 13 curbs, `37f36db` Tyorvi T12), plus the working tree's detection change. The game copy is `/tmp/claude-1000/vf10/game`, made from vf9's copy. All five artifacts were copied from `shared/build/`, and FIXED went into both places it lives. All match `shared/build/ARTIFACTS.sha256`:

| File | sha256 |
|---|---|
| FIXED | `eff07302…` (root and `STATIC/`) |
| EUSECODE | `4182e079…`. The log reads `usecode/eusecode.flx: d00d0d59…, 1526311 bytes`, and the game was identified |
| U8SHAPES | `69fbd861…` |
| TYPEFLAG | `6bdb3036…` |
| ANIM | `77e9705d…` |

**Binary and display.** The binary is `scummvm-lv/scummvm`, built 2026-10-11 04:17, after fork `b867a30c` (2026-10-10 20:30). Xvfb `:93` ran with vf9's ini: 320×200, no width/height keys, `frameLimit=true`, `SDL_AUDIODRIVER=dummy`.

**Driver.** `vf10/py/vf.py` is vf9's driver with `PRIME = False`, so there is no left click before a right hold (traps.md). Every trial checked combat bit 0x800. None was voided: the only combat flag seen came from the cp32 save itself, and it was cleared with `c` before any talk.

**Cheats.** Cheats were on only for teleports. Every run, walk and talk happened with cheats off, and each was confirmed by the echoed `Cheats = false`.

**How Map 13 was loaded.** From `run1010-s12d`, I walked S into pad 207 on Map 10. The log shows `Loading Fixed items in map 13`. `findShape` reports **112 × 497 and 298 × 498**, which is exactly what `exact_reach.load_map(13)` reads from `eff07302`. The pre-fix FIXED gives 93 + 232: the 85 new items.

**How the trials were run.**
- Each trial: teleport to the start, set the facing with a 0.7 s mouse walk, teleport back onto the exact start (the facing is kept), hold the input, then read `objectInfo 1`.
- "key" is a Shift+Up hold. "keywalk" is Up alone. "mouse" is a right-button hold with the pointer 340 px out. "mousewalk" uses 110 px.
- Each end was classified against `build_map_13.climb_cells()`. A body overhang was measured as the fraction of the 64×64 box that lies off the climb cells.
- All 116 trials are in `vf10/sp/climb_trials.json`.

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| C1 | Shift+Up runs from (4064,10000) and the N1 start stay on the climb up to the N1→E bend; 5+ runs per leg | **PASS** | **N1: 11 of 11** keyboard runs stayed on the climb, 0 ended at z 0. That is 6 from (4064,10000) (1.5-9 s) and 5 from (4064,10346) (2-10 s). Ends ran from (4064,8912,12) to (4124,5910,48). **E 5/5, N2 5/5, W 5/5, N3 5/5.** The 7 s N3 run reached the summit at (3940,724,128). **Negative control,** pre-fix FIXED `09bde917` in the same harness: N1 keyboard runs went off **5 of 5**: (3772,8328,0), (3424,7980,0), (3224,7148,8), (3772,8322,0) and (3224,7494,0). W 1/1 went off at (3688,5216,0) and E 1/1 at (5444,6020,0) |
| C2 | Holds carried past each bend (mouse and keyboard, walk and run) stop at or slide along the curbs, never drop, and never teeter at (3896,5104,76) | **PASS**, but keyboard holds can turn back (finding 1) | **52 holds past the four bends, 0 drops.** Every end was on a climb cell with **0 body overhang**. Per bend: N1→E 12, E→N2 17 (with the diagnostic reruns), N2→W 11, W→N3 12. Mouse and walk holds stop with the body against the curb: x 5248 at E→N2, y 5068 at N2→W, x 3904-3908 at W→N3, y 5568-5580 at N1→E. **The W→N3 teeter spot:** a keyboard run ended at (3920,5104,76) with the body wholly on the bend square. The old build's mouse hold teetered at (3884,5260,76), with 31% of the body off. **Four outer-corner notches**, pushed diagonally by mouse and key: no slip-through. At NW the Avatar could not move at all |
| C3 | Mouse runs and walks climb end to end; no visible change; 0 `Cycle in paint` on Map 13 | **PASS** | **5 of 5 climbs** from the foot (4064,10346,0) reached the summit and went on through to Map 17: 3 runs and 2 walks, each one continuous hold with the pointer turned at each leg (`C3-mouse-run-…`, `C3-mouse-walk-…`). **No visible change:** I took plates from the old and new builds at 4 places (N1 mid, E→N2 bend, W→N3 bend, the lowest stretch). Three are pixel-identical. The fourth differs only inside the Avatar's sprite box (`C3-no-visible-change-…`). **0 `Cycle in paint`** in the whole log: 3 sessions and 11 Map 13 loads |
| T1 | Pissed Tyorvi: "Calm down" → apology → the menu no longer has "Calm down", the apology or "Shove off"; the normal options follow | **PASS** on cp32 and cp23 | **cp32** (tyorviPissed 1): greeting "Calm down, Tyorvi. / bye" (`T1-01`). "Calm down" gives "Calm down / I wish to apologize… / Shove off, you lush! / bye" (`T1-03`). The apology reply is "Well, a much better attitude…" (`T1-04`). The menu after it is "**I have spoken to Ezrekal. / bye**" (`T1-05`). That leads on to "She told me of the poison. / She told me of my funeral. / bye" (`T1-06`). tyorviPissed then read 0, and the next talk opened "I have freed the Ancient Ones. / bye" (`T1-07`). **cp23-ceremony-done** gave the same sequence (`T1-11`…`T1-13`). **Edge:** "Calm down" picked twice lists the apology and "Shove off" twice, and one apology clears every copy (`T1-08`, `T1-09`). **Negative control:** "Shove off" still angers him ("Have to take this I do not!"), ends the talk and leaves tyorviPissed 1 (`T1-10`) |
| L | Log hygiene | **PASS** | Across all 3 sessions, 0 each of: `Cycle in paint`, `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Trying to access segment`, `popToContainer`, ERROR, `Invalid item`, `Unhandled intrinsic`, `Invalid procid`. WARNINGs are stock (translations.dat, gui-icons, theme, timestamps, MIDI transition ×3) plus one `Skipping invalid shape in sorter: 539,4!` on loading old `cp23`. That is the known old-save invisShield (`playtest-2026-09-25-ceremony-plaques.md:63`). hp stayed 30 through all 116 trials |
| Checks | Test estate; hashes; fork | **PASS**, partly not run | `tools/run_all_tests.sh`: **46/46 PASS**. That includes `test_climb_width` 28/28, `test_uc_dialogue` 455/455, `test_route_reach` 138/138, `test_paint_cycles` 40/40, `test_map_edges` and `test_scummvm_patch_sync` 3/3. The game copy's hashes match the canonical file. I did **not** run `tools/build_artifacts.sh`: the assignment forbids build scripts. The fork is unchanged since `b867a30c` |

## C1: keyboard runs up every leg — PASS

| Leg, start | Shift+Up holds | Ends | Old FIXED `09bde917` |
|---|---|---|---|
| N1, (4064,10000,0) → N | 1.5, 2, 3, 4.5, 6 and 9 s | All 6 on the climb. Examples: (4064,8912,12), (4144,8096,24), (3940,7532,28) and (4016,6304,44). The 9 s run went round the bend to (5232,5584,60) | 3 of 3 off: (3772,8328,**0**), (3424,7980,**0**), (3224,7148,8) |
| N1, (4064,10346,0) → N | 2, 4, 6, 7 and 10 s | All 5 on the climb: (4064,8922,12), (3932,7726,28), (3932,6534,40), (4124,5910,48) and (4804,5574,56) | 2 of 2 off: (3772,8322,0), (3224,7494,0) |
| E, (4232,5728,52) → E | 0.8, 1.2, 1.6, 2.0 and 2.4 s | All 5 on the climb. The ends were (5056,5728,60) and (5076,5660,60); then (5244,5820,60) twice, against the bend's curb; and (5240,5224,64), which had turned up N2 | 1 of 1 off: (5444,6020,0) |
| N2, (5088,5760,60) → N | 0.5, 0.8, 1.0, 1.4 and 2.0 s | All 5 on the climb: (5088,5376,64), (5088,5072,64) ×2, (5160,5064,64) and (5228,5452,60) | — |
| W, (5088,5216,64) → W | 0.8, 1.2, 1.6, 2.0 and 2.6 s | All 5 on the climb: (4304,5216,76), (4120,5216,76), (3920,5104,76), and twice up N3 to (3920,4832/4848,80) | 1 of 1 off: (3688,5216,0) |
| N3, (4064,5120,76) → N | 2, 3, 4, 5 and 7 s | All 5 on the climb: (4188,3732,92), (3940,3156,96), (4212,2620,104), (4184,2024,108), and the summit (3940,724,128) | — |

**How a keyboard run behaves now.** The headings still swing: the N1 ends range over x 3904-4144, which covers all three lanes. A swing now ends at a curb, and the run turns back up the lane instead of leaving it. That matches the commit's model.

**Descending holds.** S down N3 for 6 s ended at (4064,5368,76). S down N1 for 6 s ended at (3940,9908,4), by mouse and by key alike (finding 2). Both stayed on the climb.

## C2: holds past the bends — PASS

Each mode was started from all three lanes of the leg before the bend: x 3936/4064/4192 or y 5136/5248/5360, and so on.

| Bend | Mouse run | Mouse walk | Up (walk) | Shift+Up (run) |
|---|---|---|---|---|
| N past N1→E | 3/3: (3936,5580,48), (4164,5568,48), (4292,5568,52) | 3/3: y 5572-5576 | 3/3: two stopped at y 5572, one followed the E leg to (4792,5596,56) | 3/3: on along the E leg to (4768,5876,56), (5232,5584,60), (4804,5574,56) |
| E past E→N2 | 3/3: (5128,5880,60), (5228,5636,60), (5240,5736,60) | 3/3: x **5248**, the curb face | 3/3, plus 5 reruns. From the south and middle lanes: (5248,5888,60) and (5224,5888,60). From y 5664-5700, all 4 holds of 3-4 s turned back W along the south lane, to (4548,5868,52) and similar. The 1-2 s holds reached (5016,5664,60) and (5224,5664,60) | 3/3: (5244,5820,60) ×2; (5240,5224,64), which had turned N |
| N past N2→W | 3/3: y 5056-5060 | 3/3: y **5068** | 3/3: y 5068 | 2/2: (5160,5064,64) stopped. The 2.0 s run turned back S, to (5228,5452,60) |
| W past W→N3 | 3/3: x 3920-3940 | 3/3: x **3904-3908** | 3/3: one stopped at (3904,5136,76), two turned up N3 to y 4188/4300 | 3/3: (3920,5104,76), and twice up N3 |

**The adversarial pushes, one mouse and one key each:**
- **Lane edges, straight at the edge:**
  - W off N1's west edge at z 20: refused, ended at (3914,8256,20). The old build gave (3694,8300,**0**).
  - E off the lowest stretch's east edge at z 4: the mouse push was refused at (4214,9964,4). The key push turned S and ran out of the foot to the pad apron, (4214,11028,0). That is a walk down, not a drop (finding 1).
  - S off the E leg: refused.
- **Diagonally into each outer-corner notch.** Commit `d2e202e` notes a 32-unit notch at each corner.
  - SE at E→N2: (5218,5868,60) on both holds.
  - SW at W→N3: (3910,5352,76).
  - NW at N1→E: no movement at all, twice.
  - NE at N2→W: (5222,5070,64).

  None of the pushes got through a notch: half a body does not fit.

## C3: end-to-end climbs and no visible change — PASS

Each climb was one continuous hold from (4064,10346,0), with the pointer moved at each leg. Runs used the legs N 9 s, E 2.4, N 1.5, W 2.8, N 8. Walks used N 25 s, E 7, N 4.5, W 8, N 22.

All 5 climbs reached the summit pad, and the log shows `Loading Fixed items in map 17` each time. The run ends on Map 17 were (5376,11136,0) and (5376,10688,0) ×2; both walks ended at (5376,7832,0). The plates are `C3-mouse-run-foot-to-top-arrives-map17` and `C3-mouse-walk-foot-to-top-arrives-map17`. hp stayed at 30.

**Visible change.** The old (`09bde917`) and new (`eff07302`) builds were teleported to the same 4 points, and a plate was taken 4 s after each teleport with the pointer parked in a corner:
- (4064,8000,24): 0 px differ.
- (5120,5760,60): 0 px differ.
- (4096,9900,4): 0 px differ.
- (4000,5250,76): 1,244 px differ, all inside the Avatar's sprite box.

The composite plate is `C3-no-visible-change-old09bde917-left-new-eff07302-right`.

## T1: Tyorvi T12 — PASS

| Step | cp32-endgame-done | cp23-ceremony-done |
|---|---|---|
| Flags | tyorviPissed 1, tyorviMet 1, iAmDrunk 0, haveMark 1, givenTea 1 | the same |
| Greeting | "Calm down, Tyorvi. / bye" (`T1-01`) | the same (`T1-11`) |
| "Calm down" | "Calm down / I wish to apologize for my rudeness. / Shove off, you lush! / bye" (`T1-03`) | the same (`T1-12`) |
| Apology | "Well, a much better attitude you have now. Speak to you I will." (`T1-04`) | the same |
| Menu after | **"I have spoken to Ezrekal. / bye"** (`T1-05`) | the same (`T1-13`) |
| Next | "She told me of the poison. / She told me of my funeral. / bye" (`T1-06`). After bye, tyorviPissed read 0. The next talk opened "I have freed the Ancient Ones. / bye" (`T1-07`) | — |

**Edge.** "Calm down" picked a second time adds a second copy of the apology and of "Shove off": the menu had five options (`T1-08`). The apology then removed every copy, and the menu was again "I have spoken to Ezrekal. / bye" (`T1-09`).

**Negative control.** "Shove off, you lush!" still barks "Have to take this I do not!", ends the talk, and leaves tyorviPissed at 1 (`T1-10`). fix9's `T1-03` plate shows the pre-fix menu after the apology.

**Not demonstrated in the engine: the drunk acceptance.** No checkpoint reaches the pissed greeting with tyorviDrunk set and attemptedCliffs clear: both saves have tyorviDrunk 0 and attemptedCliffs 1. The simulator's D19c covers the drunk case (estate 455/455).

## Findings outside the brief

**1. A keyboard hold that meets a bend's outer corner or a lane edge does not stop there: it turns and walks back.**
- **Where it was seen:**
  - **E→N2, Up from the north lane:** all 4 holds of 3-4 s started at y 5664-5700 turned back W along the south lane, ending at x 4548-4948 (`F1-keywalk-E-at-EN2-corner-turns-back-W-film-sheet`). The 1 s and 2 s holds from y 5664 had not yet turned: they ended at (5016,5664,60) and against the curb at (5224,5664,60).
  - **N2→W:** a 2 s Shift+Up turned back S, to (5228,5452,60).
  - **The lowest stretch:** a key push E into the east edge at z 4 ran out of the foot, to (4214,11028,0).
- **No drop and no hp lost.** Every one of these stayed on climb cells or walked down to the foot apron.
- **The difference from a mouse hold.** A mouse hold stops against the curb. A held key keeps the slid heading, so a corner turns it as much as 180°.
- **Cause** [INFERENCE]: this is the same mover rule commit `d2e202e` describes (the refused step's slide becomes the facing).
- **What a player would see:** a player who holds Up at the top of the E leg walks back down it.

**2. The foot boulders block the west lane, and the new curb leaves exactly one body width beside the lower one.**
- **The boulders.** `build_lower_cliffs` puts `SHAPE_BOULDER_LARGE` (796, 2×2, z+56, SOLID|LAND) on the outer lanes: (3968,9984,4) on the west lane, and (4224,9344,8) and (4224,8576,16) on the east lane.
- **Runs into the lower one.**
  - Straight down the west lane, by mouse and by key: the run stopped dead at (3940,9908,4).
  - A mouse run up the west lane from (3936,10346,0) stalled for 4 s at (3956,10054,0).
  - A Shift+Up from the same start was deflected and ran E along the foot to (6116,10710,0). That is valley floor, never on the raised climb.
- **The gap.** The new west curb (x (3808,3840]) and this boulder (x (3904,3968]) leave x (3840,3904]: exactly 64 units, one body. `.claude/rules/map-geometry.md` warns about one-body apertures.
- **The stall is not the curb's doing** [INFERENCE from the geometry; I did not rerun it on the old FIXED]. At the stall point the curb is 52 units clear of the body.
- **Who is affected.** The east-lane boulders do not stop runs: the east-lane starts slid round them and climbed to (4140,7702,28) and (3948,7974,24). Middle-lane starts are unaffected. A player can steer round.

**3. Tyorvi's "Calm down" stacks duplicates** (1994 `+=`). This is cosmetic, and T12 clears every copy (T1 edge).

**4. cp32 and cp23 carry the parked camera** from before `f9a9aba`. After each teleport the view did not follow the Avatar until `CameraProcess::moveToAvatar`. The first four talk attempts missed because of it. cp32 also loads with combat on (flags `c00`).

## Harness anomalies

- **Swallowed first press after a teleport.** It happened 4 times. The driver retried, and the retries left the NW-corner push with no movement at all, which is the refusal it was testing.
- **`read` would not open new PNGs in `/tmp`** (`not found` for files that `ls` showed). I viewed those plates through `display()` in the eval kernel.
- **Tyorvi wanders.** Each talk took 1-6 double-click tries.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-fix10/` (23 plates).
- **Scratch** `/tmp/claude-1000/vf10/`:
  - the game copies `game/` (the build under test) and `game-old/` (FIXED `09bde917`, for the negative controls);
  - `scummvm.ini`, `saves/` (slot 1 overwritten), `lv_run.log` (plus split copies), `trace.txt`, `estate.log`, `py/vf.py` and `py/m13q.py`;
  - in `sp/`: `climb_trials.json`, `vf10-m13-fresh.sav`, the film `E-keywalk-diag.mkv` and the old/new visual-diff plates.
- **Banked nothing** in `~/lv-checkpoints`.
- **Stopped** my ScummVM and the Xvfb `:93` I started (pid 15907, 04:20).
- No source, map, fork, `TODO.md` or `HANDOFF.md` edits. No install or build runs.

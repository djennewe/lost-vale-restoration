# Fix 9 verification: Tyorvi's Key question and Cliffs menu, Ezrekal's Shield, Ragnar's Thordis line, Map 13 run curbs and foot-wall gap (2026-10-11)

**Build under test.** main `ac56acd` (fix 9 merged at `f86aacd`: `6eb3c87`, `9cf3151`, `f86aacd`). The game copy is `/tmp/claude-1000/vf9/game`, made from vf8's copy. Its FIXED.DAT (both the root and `STATIC/`) and its EUSECODE were replaced from `shared/build/`. All five files match `shared/build/ARTIFACTS.sha256`:

| File | sha256 |
|---|---|
| FIXED | `09bde917…` (root and `STATIC/`) |
| EUSECODE | `b484c2fa…`. The log reads `usecode/eusecode.flx: d00d0d59…, 1526214 bytes` |
| U8SHAPES | `69fbd861…` |
| TYPEFLAG | `6bdb3036…` |
| ANIM | `77e9705d…` |

The binary is `scummvm-lv/scummvm`, built 2026-10-11 02:05. That is after fork `b867a30c`. ScummVM ran on Xvfb `:94` with vf8's ini: 320×200, no width/height keys, `frameLimit=true`, `SDL_AUDIODRIVER=dummy`. The driver is `vf9/py/vf.py`, a copy of vf8's with the paths changed.

**Cheats.** Cheats were on only for teleports to a start point (next to an NPC, or a climb or foot start). Every talk and every run happened with cheats off. Map 13 was loaded by walking S into pad 207 from Map 10: the log shows `Loading Fixed items in map 13`, and `findShape 15` lists the new foot wall, 3711/3839 and 4351/4479.

**Read H1 before the Map 13 numbers.** The harness's "prime" left-click, fired 0.4 s before the right button goes down, makes the Avatar **jump**. That jump caused every stop at the foot wall that I first logged, and it probably caused fix 7's and fix 8's run stops as well. All C1/C2 verdicts below use runs **without** the prime click.

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| T1 | After the Key (s12d), Tyorvi's menu has no "Do you have the Key to the Clouds?". Before the Key (s12c), it does | **PASS** | s12d (givenTea 1), three menus checked: the first meeting "What is your name? / What do you do? / bye" (`T1-01`); the pissed greeting "Calm down, Tyorvi. / bye" (`T1-02`); after the apology, the same list plus "I have spoken to Ezrekal." (`T1-03`). Also the toldCliffs greeting "Tell me more of the Cliffs. / bye" (`T2-01`); fix 7's `T2-01` listed the Key question there. **Negative control:** s12c (givenTea 0) offers "What is your name? / What do you do? / **Do you have the Key to the Clouds?** / I have something for you from Ezrekal. / bye" (`T1-04`) |
| T2 | "Tell me more of the Cliffs." → "I am going there." removes both options | **PASS**, both picks | "I am going there." → "Yes, accompany me. / No, don't accompany me. / Our deaths won't be in vain? / bye" (`T2-03`). After a reload, "No reason, really." → "Killed your best friend? / bye" (`T2-04`). Neither menu keeps either option. Fix 7's `T2-03` kept both |
| E1 | "Tell me again of the Shield." leaves the menu | **PASS** | Natural road from `run1010-s08`, where Ezrekal had not yet been met. Talk 1 set mentionShield 1072 to 1, and "Tell me of the Shield." left the menu after its story (`E1-01`, `E1-02`). In talk 2 the greeting offered "Can you help me? / **Tell me again of the Shield.** / bye" (`E1-03`). After the story the menu read "Can you help me? / How was it lost? / Can you make another shield? / bye" (`E1-04`) |
| R1 | Ragnar: "I met someone named Thordis." cannot be re-picked to re-add the follow-ups | **PASS** | From `cp9b-thordis-spoken` (ragnarMet 1, thordisMet 1, spokeOfThordis 0). Menu before: "Atli sent me to you. / I met someone named Thordis. / Farewell" (`R1-01`). Menu after the pick: "Atli sent me to you. / Thordis is a good person. / I was not impressed. / Farewell" (`R1-02`). The option is gone, so it cannot be picked again. spokeOfThordis 1770 went 0→1 |
| C1 mouse | Mouse runs up every leg stay on the lane | **PASS** | 13 clean runs, all on the lane, 0 falls, hp 30 throughout: N1 ×2, E ×1, N2 ×2, W ×1, N3 ×4 (one of them the plate run), plus 3 W-leg/bend runs that stayed on. The ends lie inside the 3-lane extents, for example N3 (4196,1388,116) and (4060,1456,116), and N1 (4144,6680,40) |
| C1 keyboard | Shift+Up runs stay on the lane | **FAIL** on the lower N leg | Lower N leg (N1): **4 of 5 left the climb.** The ends were (3236,6964,**0**), (5528,6672,0), (5528,6680,0) and (3772,8328,0). The 5th was a 1.5 s run, which was still on the lane at (4064,8912,12). Film sheet `C1-key-N1-off-lane-film-sheet`: the heading turns to NE mid-run. E, N2, W and N3: 8 of 8 on the lane. See C1 |
| C1 bends | Report the bends | **Both bends drop him to z 0** | **E held past the E→N bend:** 3 of 3 runs (2 mouse, 1 keyboard) went off the corner's east side to z 0: (5448,5864,0), (5672,5880,0) and (5344,6160,0) (`C1-bend-E-held-past-off-east`). **W held past the W→N bend:** 3 of 4 fell to z 0, at (3452,5084,0) ×2 and (3544,5104,0). One teetered at (3896,5104,76), with the body 8 units over the west edge (`C1-bend-W-held-past-teeters-3896-5104`). No hp was lost on any bend fall |
| C2 | A run N off the pad area through the foot-wall gap does not wedge | **PASS** | 6 of 6 clean runs N from x 3984, 4050, 4160 and 4208 (mouse ×4, keyboard ×2) went straight through with x unchanged (`C2-new-gap-run-x4208-through`). From the pad row: 4 of 4 runs (3.5 s) reached y 9300-9600. **Negative control:** the same mouse runs on the pre-fix FIXED (`ee4182d0`, one-tile gap) stopped at the old east stub in 3 of 4 lined-up starts: (4332,10822), (4304,10818), (4274,10818) (`C2-neg-old-gap-stop-4274-10818`) |
| L | Log hygiene | **PASS** (stock and checkpoint noise only) | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Trying to access segment`, `popToContainer`, ERROR, `Invalid item`, `Unhandled intrinsic`. **0** `Cycle in paint` while Map 13 was loaded. 5 × `Invalid procid … in waitlist`, each printed right after `UCLISTS: ok` while a checkpoint loaded (from the saved process table). 7 × `Cycle in paint 475 -> 126`, on the old `cp9b` checkpoint's Map 10 fixed items (traps.md) |
| Checks | Test estate; hashes; fork | **PASS**, partly not run | `tools/run_all_tests.sh`: **46/46 PASS**, including `test_uc_dialogue` 445/445 and `test_scummvm_patch_sync` 3/3. The game copy's hashes match. `test_climb_width.py`: 17/17. I did not run `tools/build_artifacts.sh`, because the assignment forbids build scripts. The fork is unchanged since `b867a30c`, so the fork check is not triggered |

## T1 / T2: Tyorvi — PASS

**T1, after the Key.** State: `run1010-s12d`. Flags: givenTea 1061 = 1, hasTea 1, haveMark 1, sentToTyorvi 1, toldCliffs 0, tyorviMet 0.

1. **Talk 1** was a first meeting. The menu had no Key question (`T1-01`). "What is your name?" ran his drunk speech, and the talk ended.
2. **Leaving the fast area.** I teleported out of his fast area, which cleared iAmDrunk 1828 (`leaveFastArea`), and back.
3. **Talk 2** opened "Calm down, Tyorvi. / bye" (`T1-02`). "Calm down" → "I wish to apologize…" → the menu gained "I have spoken to Ezrekal." (`T1-03`).

None of these menus has the Key question.

**T1 negative control, before the Key.** `run1010-s12c` (givenTea 0): the first-meeting menu lists "Do you have the Key to the Clouds?" (`T1-04`).

**T2.** The Key save was `vf7-sober-key` (fix 7's: tyorviMet 1, givenTea 1, iAmDrunk 0). I set toldCliffs naturally:
- Hrodny talk 1: "What is your name?".
- Hrodny talk 2: "I have spoken to Ezrekal." → "She told me of my funeral." → toldCliffs 1040 = 1.
- Saved as `vf9-toldcliffs`.

The Tyorvi runs, both from that save:

| Run | Picks | Resulting menu | Plates |
|---|---|---|---|
| 1 | Greeting "Tell me more of the Cliffs." → "I am going there. / No reason, really." → **"I am going there."** | "Yes, accompany me. / No, don't accompany me. / Our deaths won't be in vain? / bye" | `T2-01`, `T2-02`, `T2-03` |
| 2 (after a reload) | "Tell me more of the Cliffs." → **"No reason, really."** (reply: "Just curious, are you? …") | "Killed your best friend? / bye" | `T2-04` |

Picking "Killed your best friend?" ended the talk.

## E1 / R1 — PASS

- **mentionShield is reachable from a natural save only through Ezrekal's first meeting.** Its only writers are "They did (not) mention you." (`EZREKAL.UNK:1373/1391`). s09 and s12b already have ezrekalMet = 1 and mentionShield = 0, so I used `run1010-s08` (ezrekalMet 0).
- **The road:** "May I know your name?" → "I am from Britannia." → "Yes, I am from outside." → "I have heard from the Ancient Ones." → "They did mention you." → "Tell me of the Shield." Then bye. Saved as `vf9-s08-mentionshield`.
- **Talk 2:** "Tell me again of the Shield." → it left the menu (`E1-03`, `E1-04`).
- **R1:** see the verdict table.

## C1: Map 13 climb runs

**Method.** Each trial teleported to a start on the lane (cheats on, then off), set the facing with a 0.7 s walk, held the input, and then read `objectInfo 1`.
- Mouse runs held the right button with the pointer 340 px out.
- Keyboard runs held Shift+Up, which runs forward in the facing direction.
- Each end was classified against `build_map_13.climb_cells()` for a 64-unit body.
- Trials with the combat flag (0x800) set were voided (H2).

All trials are in `vf9/sp/climb_trials.json`.

| Leg | Mouse | Shift+Up |
|---|---|---|
| N1, foot (4064,10000) → N, 6 s | 2/2 on the lane: (4144,6680,40), (4132,6692,40) | **1/5 on the lane.** Off: (3236,6964,0), (5528,6672,0) ×2, (3772,8328,0). The 1.5 s run was on the lane at (4064,8912,12) |
| E, (4232,5728) → E, 1.4 s | 1/1: (5056,5728,60) | 2/2: (5216,5792,60), (5188,5548,60) |
| N2, (5088,5760) → N, 0.7-0.9 s | 2/2: (5088,5664,60), (5088,5432,64) | 1/1: (5160,5072,64) |
| W, (5088,5216) → W, 1.4 s | 1/1: (4304,5216,76) | 2/2: (3936,5216,76), (3920,5216,76) |
| N3, (4064,5120) → N, 6 s | 4/4: (4196,1388,116), (4060,1456,116), (4196,1572,120) and one more | 3/3: (3904,1568,116), (4148,1252,116), (3940,1188,124) |

**Why the keyboard runs leave N1** [INFERENCE from `u8_avatar_mover_process.cpp:584-587`].
- **Forward steps keep the turned heading.** The keyboard path steps `direction` forward each frame. When a step is refused, the mover slides one heading over, and that slid heading then *stays* the facing. The mouse path re-reads the pointer on every step.
- **The film agrees.** It shows the heading turning NE (`C1-key-N1-off-lane-film-sheet`).
- **Where he leaves.** N1's lowest stretch has no curbs (path z < 9), and its west edge has none at all. The run leaves the lane there, east or west. One W exit ended at z 0 from a lane at z 20.
- **N3 held** in 3 of 3 keyboard runs.

## C2: the foot-wall gap — PASS (with a negative control)

| Layout | Runs | Result |
|---|---|---|
| New gap, x (3839,4223] | 6 runs N from y 11050 at x 3984 / 4050 / 4160 / 4208 (mouse ×4, keyboard ×2) | All passed straight to y 9794-10146 |
| New gap, x (3839,4223] | 4 runs N from the pad row, 3.5 s | All reached y 9300-9600 |
| Pre-fix FIXED `ee4182d0` (restarted on a copy, walked in fresh; `findShape 15` lists 3967 and 4223) | The same runs | Stopped at the old east stub from x 4130 / 4160 / 4208: (4274,10818), (4304,10818), (4332,10822). x 4050 passed; x 3984 slid to 4048 and got through |

## Findings outside the brief

**H1. The harness's prime click makes the Avatar jump. It produced fix 7's foot-wall wedge and probably fix 8's D1 door stops.**

- **The mechanism.** `vf.run()` left-clicks 0.25 s before `mousedown 3`. Both buttons are then down within the double-click timeout, so `u8_avatar_mover_process.cpp:423-440` sets `MOVE_JUMP`. At lines 464-470, `checkTurn` uses up that jump only if the Avatar is not already facing the pointer.
- **What the film shows.** With the prime, standing runs N that faced N crouched and leapt with arms raised (`H1-prime-click-jump-frames`). They landed against the east stub at **(4239,10816)**, which is fix 7's exact wedge point, from x 4050, 3 of 3 (`H1-prime-jump-stop-4239-10816-sheet`).
- **The pattern.** With the prime, the same starts and facings stopped 7 of 7 times when facing N and 0 of 2 when facing E or S. Without the prime they went straight 6 of 6.
- **Fix 8's D1** found that "facing W at a standing start" decided the door stops. That is the jump condition [INFERENCE: not rerun].
- **The real-player case.** A player who left-clicks just before holding the right button gets the same jump, and the stop it caused here was not a trap: a second run went through, 2 of 2.
- **The fix.** Set `PRIME = False` in the harness. After a teleport or load the first press can be swallowed, so retry when the start does not move; hold presses at least 0.6 s.

**H2. Console typing can leak `c` into the game and turn combat on.** Twice, after a `Cheat::toggle` / `Cheat::heal` / `Cheat::toggle` attach, `objectInfo` read flags `c00` (in combat). `MainActor::toggleCombat` did not clear it; the `c` key did. Combat-mode runs behaved erratically (a keyboard "E" run ended 700 units W), so those trials are voided. Check bit 0x800 on every trial.

**3. Tyorvi's apology options never leave the menu.** After "I wish to apologize for my rudeness." the menu still lists "Calm down, Tyorvi.", "I wish to apologize…" and "Shove off, you lush!" (`T1-03`, `TYORVI.UNK:2412-2472`). None of those cases removes its own or its sibling's label. "Shove off" after a successful apology re-angers him and ends the talk. D19b's sibling class does not catch this: the cases remove nothing at all.

**4. Keyboard runs on N1** (C1). This needs curbs on the lowest stretch and the west edge, or a mover change for forward-key runs.

**5. Both bends drop a held run to the valley** (C1 bends). E→N held E: 3 of 3 to z 0. W→N held W: 3 of 4 to z 0 and 1 teeter. The agent's note on the W bend ("teeters") understates it. No hp was lost.

**6. Fall damage happened in the contaminated set only.** Two keyboard N3 runs with the prime cost 5 hp each (30→25→20). Clean N3 keyboard runs did not fall.

## Harness anomalies

- **H1** (the prime-click jump) and **H2** (combat leaks).
- **Swallowed inputs.** The first right-button press after a teleport or load was often swallowed, and 0.3 s walks never moved him. Several "from = start" trials show this.
- **Failed save.** One `saveGame` failed right after Ezrekal's `exitConvo`; the retry worked.
- **Tyorvi and Ezrekal wander.** Talks took 1-4 teleport+click tries. A misclick hit floor tiles 3952 and 5491, and desk 30628; all harmless.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-fix9/` (26 plates).
- **Scratch** `/tmp/claude-1000/vf9/`:
  - `game/` (the build under test) and `game-old/` (FIXED `ee4182d0`, for the C2 control);
  - `scummvm.ini`, `saves/` (slot 1 overwritten), `lv_run.log`, `trace.txt`, `py/vf.py`, `py/m13q.py`;
  - in `sp/`: saves `vf9-toldcliffs`, `vf9-s08-mentionshield` and `vf9-m13-fresh`; films `C2-film-4050.mkv`, `C1-key-N1*.mkv` and `C1-key-N3-fall.mkv`; `climb_trials.json`.
- **Banked nothing** in `~/lv-checkpoints`.
- **Stopped** my ScummVM.
- **Xvfb `:94`** (pid 3880104, started 23:59 by an earlier session) was already running. I used it and left it running.
- No source, map, fork, `TODO.md` or `HANDOFF.md` edits. No install or build runs.

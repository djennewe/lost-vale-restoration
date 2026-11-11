# Fix 7 verification: Tyorvi's drink pause, Map 13 climb width, Hrodny's chest, Tyorvi after the Key, Ezrekal's Shield option (2026-10-11)

**Build under test.** main `2729115`. Game copy `/tmp/claude-1000/vf7/game`, made from vb7's copy with FIXED and EUSECODE replaced from `shared/build/`. Its sha256 matches `shared/build/ARTIFACTS.sha256`: FIXED `5b3875ab…` (root and `STATIC/`), EUSECODE `b73b47fa…` (log: `usecode/eusecode.flx: d00d0d59…, 1526009 bytes`), U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`. The binary is `scummvm-lv/scummvm`, built 2026-10-10 23:57, after fork `b867a30c`.

**Harness.** Xvfb `:94`, vb7's ini: 320×200, no width/height keys, `frameLimit=true`, `SDL_AUDIODRIVER=dummy`. Driver `vf7/py/vf.py`, a copy of `v7.py` with the paths changed. Films were taken with `ffmpeg x11grab` at 25 fps; frame timing uses a ±14 colour match because the yuv conversion shifts the text colours.

**Cheats.** Cheats were on only to teleport *to a start point*: next to a wandering NPC, a climb leg, or the chest's west side. Each time they were toggled off in the next console attach. Every talk, walk, egg, teleport trigger, key use and chest open happened with cheats off.

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| F1 | Drunk and sober drink paths pause about 1 s, then "Hmmm, taste too bad…", then the Key menu | **PASS** | Film frames. **Drunk:** "All right… Try it I will." ends at frame 323; "Hmmm" appears at frame 357, **1.36 s** later; then the "May I have the Key…" menu. **Sober:** "Oh, all right. Give it to me." ends at frame 186; "Hmmm" appears at frame 215, **1.16 s** later; then the Key menu. Part 6 saw about 20 s here. |
| F2 | Map 13 climb, freshly loaded, walked from pad 207 to the summit with mouse and with keyboard: no falls to z 0 | **PASS for walking** (0 falls in 2 full climbs). **Running drifts and falls** (finding 1) | Mouse walk: 39 position samples from (4050,11510,0) to (4025,1064,120), 0 drops. Keyboard (Up plus Left/Right turns): 55 samples to (4006,1162,124), 0 drops, including about 40 diagonal back-and-forth steps at every bend. hp 30 throughout. |
| F6 | Chest at (21024,8832): no wedge walking up its west side NE; clickable; the q20 key opens it; Tiny Tars inside | **PASS** | 5 of 5 trials got past: NE ×3, N, run NE. A click on the chest logged `Item 26361 (shape 618) LCHST_EW (21024,8832,0)`. Double-click without the key: "locked chest" (the negative control). q20 key 19205 → `Target result: Item 26361` → shape **78**. Double-click → `004E:00A9` and TRAP `02F4:0080` → gump. Contents: three 859 frame 8 (19207, 19208, 26359, `f 0x2008`) |
| T2 | With toldCliffs and the Key: "Tell me more of the Cliffs" → "I am going there" → "Yes, accompany me" → next visit "You weren't at the cliffs." once → then the normal menu | **PASS** | toldCliffs came from a walked Hrodny talk ("She told me of my funeral."). tyorviDrunk 1082 went 0→1 on "Yes, accompany me". After the q170 egg and the climb, visit 2 offered "You weren't at the cliffs." The reply was "Was I not? -hic- Gathering my climbing gear I was…", the option dropped, and 1082 went 1→0. Visit 3: "Tell me more of the Cliffs. / Do you have the Key…? / bye" |
| E1 | Ezrekal from s09: after "Perhaps I will try the Cliffs.", "Tell me of the Shield." is listed once | **PASS** | The post-Cliffs menu lists the Shield option once (`E1-03`). After the Shield story it is gone and "How was it lost? / Can you make another shield?" appear (`E1-04`) |
| L | Log hygiene | **PASS** (one stock warning) | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Trying to access segment`, `popToContainer`, ERROR, `Cycle in paint`, `Invalid item`, `Invalid procid`. **2 × `Unhandled intrinsic 254 'isGameRunning()'`**: one on the locked chest's double-click, one on the open. Part 6 logged the same 2 |

## F1: Tyorvi's drink pause — PASS

Both runs start from `run1010-s12c-m10-elixir-in-pack` (tyorviMet 0, iAmDrunk 0, hasTea 1, givenTea 0).

### Drunk path (talk 1)

1. The first-meeting menu was "What is your name? / What do you do? / Do you have the Key…? / I have something for you from Ezrekal. / bye".
2. The chain ran: "I have something for you…" → "It is an elixar." → "It is a potion." → "It will heal your dreams." → **"Shut up and drink it!"** (`F1-drunk-01`).
3. Film `vf7/sp/f1d_drink.mkv`:
   - "All right… Try it I will." shows over frames 65-322 and times out by itself.
   - Frames 323-356 show no text (`F1-drunk-03-pause-frame340`, sheet `F1-drunk-sheet-frames318-362`).
   - "Hmmm, taste too bad that did not…" appears at frame 357 (`F1-drunk-04`).
   - The menu "May I have the Key to the Clouds? / bye" appears at frame 683 (`F1-drunk-05`).
4. The pause is 34 frames = **1.36 s**.

### Sober path (reload, then talk 2)

1. Talk 1 was drunk. "bye" alone did not set tyorviMet, so I took "What is your name?", and tyorviMet went 0→1.
2. A teleport about 2,300 units away left iAmDrunk at 0.
3. Talk 2 opened on "Are you OK, Tyorvi?" (the random drunk-story tier). iAmDrunk was still 0, so the drink cases took the sober branch.
4. The chain ran: "It is an elixar." → "It will heal your dreams." → **"Just try it, please."** (`F1-sober-01`).
5. Film `f1s_drink.mkv`:
   - "Oh, all right. Give it to me." shows over frames 65-185 (`F1-sober-02`).
   - "Hmmm…" appears at frame 215 (`F1-sober-04`, sheet `F1-sober-sheet-frames182-215`).
   - The Key menu appears at frame 504 (`F1-sober-05`).
6. The pause is 29 frames = **1.16 s**.
7. The Key was then taken: item 28583 shape 82 **q170**, `f 0xc`.

[INFERENCE] The 0.16-0.36 s above 1.0 s is the destroy loop plus the process scheduling around the bark's return.

**Negative control.** The old `wait (1000)` gave about 20 s of silence here (part 6 finding 1). That build was not rerun here.

## F2: the Map 13 climb — PASS for walking

- **Fresh load.** From `vf7-accompany` (Map 10), I walked S down the x 7252 lane into 207, and the log showed `Loading Fixed items in map 13`.
- **Egg.** I walked N into EggCloudCliffs. The log showed `event 7 @ 05A8`, with the handholds bark. climbedCliffs 1031 and attemptedCliffs 1039 both read 1.
- **Save.** `vf7-m13-foot-climbed`, taken on this freshly loaded map.

**Mouse walk** (right button, pointer 110 px out). Legs N → E → N → W → N along the waypoints, x near 4032, bursts of 0.6-2 s.
- 0 drops.
- Path: z rose 0→124 by (4183,9682,4) … (3983,5682,48) … (5059,5118,64) … (4029,4644,80) … (3969,1216,124), and ended on the summit at (4025,1064,120) (`F2-mouse-walk-summit`).
- Widest drift: x 3919 at y 6218, and x 4211 at y 10622 (that one in the valley, before the climb).

**Keyboard walk** (Up = forward; Left/Right = 45° turns, Right clockwise). Reloaded the foot save.
- 0 drops, ending on the summit at (4006,1162,124) (`F2-key-walk-summit`).
- My autopilot overshot every waypoint and stepped back and forth on the diagonals: SW/NE at (3942-4118, 6154-6330), SE/NW at (3998-4130, 5634-5766) and (5006-5138, 5090-5222), W/E at (4970-5178, 5662), SE/NW at (4070, 5250) and NE/SW at (4146, 1022). **None of these fell.** That is 40-odd extra diagonal and reverse steps on the bends where part 6 fell.
- Every walking sample lay on a `climb_cells()` cell, within 8 of its z.

**Baseline.** Part 6 had 21 DROP lines walking the old one-tile climb.

## F6: Hrodny's chest — PASS

I hopped Map 13 → Map 10, so the map was freshly loaded. `findShape 618`: item 26361 at (21024,8832,0), q20.

| Start | Input | End | Passed |
|---|---|---|---|
| (20880,8960) | walk NE 2.5 s | (21364,8788) | yes |
| (20940,8900), hugging the west face | walk NE 2.5 s | (21372,8780) | yes |
| (20940,8960) | walk N 2.5 s | (20880,8204) | yes |
| (20921,8857), part 6's wedge point moved 128 W | walk NE 2.5 s | (20928,8240) | yes |
| (20880,8960) | run NE 1.5 s | (21140,8784) | stopped east of the chest, after 314 units; not on the west side |

- **Click.** A single click logged the chest's `dumpInfo` (`F6-chest-look`).
- **Negative control.** Double-click without the key: "locked chest" (`F6-neg-locked-dblclick`).
- **Key.** The q20 key (19205, the pre-placed spare) was taken with `Item::grab`; the pickup was not under test. Double-click key → `event 1 @ 0052:04BB` → click chest → `Target result: Item 26361`. objectInfo then read **shape 78 CHEST_EW**.
- **Open.** Double-click opened the chest gump (`F6-chest-open-gump`). The TRAP fired `02F4:0080` and did no damage.
- **Contents.** Three 859 frame 8 items (`f 0x2008`, container coordinates), the Tiny Tars.
- **Not run:** the q170 key against the locked chest. The q20 key lay over it in the pack.

## T2: Tyorvi after the Key — PASS

The state comes from the F1 sober run: Key q170 in the pack, tyorviMet 1, givenTea 1, iAmDrunk 0.

1. **Hrodny.** Talk 1: "What is your name?" (hrodnyMet). Talk 2: "I have spoken to Ezrekal." → **"She told me of my funeral."** → toldCliffs 1040 = 1.
2. **Tyorvi, visit 1.** The menu was **"Tell me more of the Cliffs." / "Do you have the Key to the Clouds?" / bye** (`T2-01`).
   - "Tell me more…" → "I am going there. / No reason, really." (`T2-02`).
   - "I am going there." → "… Yes, accompany me. / No, don't accompany me. / Our deaths won't be in vain? / bye" (`T2-03`).
   - "Yes, accompany me." → "Gather my climbing gear I will. Meet you there I will." (`T2-04`). tyorviDrunk 1082 = 1.
3. **The climb.** Map 13 egg, then the climb (F2), then walked W off pad 207 into 206 → Map 10. Flags: 1082 = 1, 1031 = 1, 1039 = 1, 1040 = 1.
4. **Visit 2.** The menu was **"You weren't at the cliffs." / "Do you have the Key…?" / bye** (`T2-05`).
   - The pick got "Was I not? -hic- Gathering my climbing gear I was… and a drink or two, perhaps. Climbed them without me you did? Then need me you did not." (`T2-06`).
   - The menu then lost the option (`T2-07`), and 1082 read 0.
5. **Visit 3**, after a teleport away and back: **"Tell me more of the Cliffs." / "Do you have the Key…?" / bye** (`T2-08`). There was no "You weren't at the cliffs.".

## E1: Ezrekal's Shield option — PASS

From `run1010-s09`, I talked to Ezrekal through the stockade fence. The road:

1. Can you help me?
2. I have been poisoned.
3. But I'm dying!
4. Prepare my funeral?!
5. I want to be healed!
6. I don't want a funeral!
7. You said the Ancient Ones were gone!
8. Where will I be until then?
9. I don't want to be an undead!
10. Cloud City?
11. How?! How can I be healed? The menu here already had "Tell me of the Shield." (`E1-01`).
12. Where is the Cloud City?
13. Tell me more of the Cloud City.
14. Are the Ancient Ones still there?
15. **Perhaps I will try the Cliffs.** (`E1-02`)

The next menu was "Tell me of the Shield. / Where is the Sacred Circle? / How can I awaken the Ancients? / Has anyone ever been there? / Key to the Clouds? / bye". The Shield option is listed **once** (`E1-03`). Picking it removed it and added "How was it lost? / Can you make another shield?" (`E1-04`).

## Findings outside the brief

1. **Running on the climb still drifts off the lanes and falls.** Mouse run (pointer 340 px), single-leg trials, each from a debug-teleported start on the lane:

   | Leg | Start | End | Result |
   |---|---|---|---|
   | E leg (switchback) | (4005,5749,48) | (4689,6129,**0**) | **fall**, twice, identical end (film `vf7/sp/f2_runE_rep1.mkv`, `F2-run-E-drop-sheet`) |
   | E leg | (4032,5696,48), lane centre | (4554,6100,**0**) | **fall** |
   | E leg | (4005,5682,48) | (4577,5950,52) | off the lane to the S, standing at z 52 (a ledge-face top) |
   | E leg | (4005,5620,48) | (4933,5924,56) | off the lane to the S, z 56 |
   | W leg | (5056,5184,64) | (4285,4989,76) | off the lane to the N, z 76 |
   | upper N leg | (4032,5100,76) | (4272,2764,100) | off the lane to the E (x > 4224), z 100 |
   | lower N leg | (4032,9800,4) | (4148,8108,24) | on the lane; drifted E by 116 |

   - **The pattern.** A run drifts to the *right* of its heading on every ascending leg (S of E, N of W, E of N). It ends on the ledge tops, and on the E leg it goes over them.
   - [INFERENCE] A running step refuses the +4 riser, and the mover's right-first slide then carries the Avatar sideways. Walking never did this.
   - Falls do no damage (hp 30) and land on the z-0 floor, so this costs time, not the game.
   - `test_climb_width`'s HOLDS cover walking holds only.

2. **A run N off the arrival line wedges on the foot wall.** Running N from (4050,10958) slid E to (4239,10816) and stopped against the ruined wall's east stub (x 4095-4479, y 10752). Four more N runs did not move; neither did a run W to (4143,10816) and three N runs after it. A walk W to x 4039 freed it (`F2-run-N-wedge-foot-wall`). The gap is one 128-unit tile (3967-4095), so a run has to be lined up on it. A mouse walk drifts too (to x 4211 at y 10622) but got through.
3. **The Key question outlives the Key.** "Do you have the Key to the Clouds?" stays on Tyorvi's menu after he has handed the Key over (`T2-01`, `T2-05`, `T2-08`). The add at `TYORVI.UNK:517` is gated only on `sentToTyorvi and haveMark`. Cosmetic: its drunk answer is flavour text.
4. **"I am going there." and "No reason, really." stay on the menu after you pick one** (`T2-03`). The removal at `TYORVI.UNK:1207` names `"No reason, really. \f J'y vais. \g", "I am going there."`, which match neither added string (`1193`), so the removal does nothing. Cosmetic.
5. **Tyorvi's first-meeting "bye" does not set tyorviMet.** Only "What is your name?" does (getGlobal 1083 read 0 after a talk ended with "bye"). A player who says only "bye" meets him drunk again next time.
6. **Conversation barks are not dismissed by a click below the text** at (320,380). Every bark in this session timed out by itself: about 10.3 s for the long drunk line, 4.8 s for "Give it to me.". So F1's 1.2-1.4 s pause always follows the timeout, not a click. I did not test a click on the text itself.

## Harness anomalies

- **Tyorvi and Hrodny loiter fast.** Three console attaches between reading an NPC and clicking let them move off screen. Fix: one attach that turns cheats on, reads the NPC and teleports (`MainActor::teleport` closes the console itself); a second that turns cheats off, reads the Avatar and the NPC and parks the pointer; then a double-click right after `exit`. That worked 7 of 9 times.
- One talk attempt with the NPC behind the Avatar double-clicked the Avatar and opened the paperdoll. Escape opened the pause book instead of closing it; **Backspace** (CLOSE_GUMPS) closed the gumps.
- The console now runs several commands per attach; `getGlobal` batches of 6-10 worked.
- `saveGame vf7-toldcliffs-key` failed silently once, right after Hrodny's `exitConvo` (finding 6 in part 6 is the same). The retries later succeeded.
- My autopilots overshot waypoints with minimum bursts of 0.5-0.6 s and stepped back and forth. That was harmless for walking. For running it produced junk (teleport "recoveries" onto off-lane spots), so the running numbers above come only from the clean single-leg trials.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-fix7/` (30 plates).
- **Scratch** `/tmp/claude-1000/vf7/`:
  - the game copy, `saves/`, `scummvm.ini`, `py/vf.py`, `lv_run.log`, `trace.txt`;
  - `sp/`: shots, films `f1d_drink.mkv`, `f1s_drink.mkv`, `f2_runE_rep1-3.mkv` (and a large `f1_drunk.mkv`), climb tracks `f2_*_trk.json`;
  - in-session saves `vf7-sober-key`, `vf7-accompany`, `vf7-m13-foot-climbed`, `vf7-m10-back-climbed`.
- **Banked nothing** in `~/lv-checkpoints`.
- **Stopped** my ScummVM and Xvfb `:94`.
- No source, maps, fork, `TODO.md` or `HANDOFF.md` edits; no install or build runs.

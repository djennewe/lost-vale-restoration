# Single-build replay, leg 2: island → Mythran (step 2) → back to the plateau with two potions → T26 → spitter corridor → doors chamber; step 3 reached Map 9 but the Avatar died on arrival (2026-10-17)

Leg 2 continues from leg 1's banked island landing (`docs/playtest-2026-10-17-replay-leg1.md`), on the same pinned game copy.

## Build pinned (re-checked)

- **Game copy.** `/tmp/claude-1000/replay1017/game` was not re-copied or modified. `sha256sum -c ../pinned.sha256` gave OK for all six files at the start and at the end of the session: EUSECODE `2e3b71c2…`, FIXED (root and `STATIC/`) `8db11ee3…`, U8SHAPES `efb16af1…`, TYPEFLAG `d26d1531…`, ANIM `696dbeb9…`.
- **Binary.** `/tmp/claude-1000/replay1017/bin/scummvm-console`, the same file as leg 1. The log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: 84615e29d097543ed69da844fbc3948f, 1528891 bytes`.
- **Log.** `/tmp/claude-1000/replay1017/lv_run2.log` (23,072 lines). The trace is `trace2.txt`.
- **Harness change: 320×200 from the north pad on (harness anomaly 1).** At the north pad I stopped the game and edited the ini to `width=320`, `height=200` and `scale_factor=2`; the window stays 640×400. The 640×400 ini is kept as `scummvm-640x400.ini`. The log shows `Setting Video Mode 320x200`. Everything before the north pad ran at 640×400, as in leg 1.
- **Cheats: 0.** `Cheat` appears 0 times in `lv_run2.log`. The console was used for `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object`, `saveGame` and `loadGame`, and nothing else. Attaching it pauses the world, and I used that pause to read positions and plan between moves. Every move, drag, key use, door and menu pick was player input.
- **Deaths: 3. Reloads: 2.**
  1. MISSTRAP and FIREBOMB hits after a held run drifted near spitter 1 at (16668,5572). I reloaded `s02c`.
  2. SP3 FIREBOMBs after an east run overshot to x 20728 in the corridor (finding 3). I reloaded `s02d`.
  3. The Avatar died to the 808s while going through the doors. He arrived on Map 9 at hp 0 (finding 4). The session ended there.

## Outcome

- **Step 2 is complete and banked.** Mythran's flags `[0717]`-`[071B]` = 1, `[071C]` = 0 and lbDone `[06A6]` = 1.
- **The furthest bank** is the corridor pocket on Map 8 (18168,5100,0), hp 30, holding one heal potion (f3).
- **Step 3 is NOT banked.** The run went pocket → chamber → chest → key. One key use unlocked both leaves, the west leaf opened, and T201 took the Avatar to Map 9 (13696,14208). He arrived dead: two shape-808 monsters had taken hp 30 → 0 during the last few seconds.
- **Not blocked.** The sequence works. It needs either more hp or a faster finish (see Resume).

## Verdicts

| Step / segment | Verdict | Evidence |
|---|---|---|
| Island landing → lane → pad 4 | **PASS, hp 22 → 11** (finding 1) | S walk 0.5 s → y 1830, NW 0.3 s + W run 1.8 s → (5574,1810), then W 2.0 s → (4474,1810), then W 1.0 s → pad 4 → (2688,1816). Plate `F1-island-lane-hit` |
| Upstairs → **step 2 (Mythran)** | **PASS** | Strike `event 1 @ 0421:A125`. My picks, from the screen: (one accidental first pick, harness anomaly 2) → Who searched for the Zealans? → What happened to him? → Where are these double doors? → How do I open the doors? → Farewell. Afterwards `[0717 01]`-`[071B 01]` = 1, `[071C]` = 0 and `[06A6]` = 1 (log lines 2357-2363). Plates `s02a`-`s02c` |
| Island loop for potions | **PASS** (finding 2) | Egg 2 (3071,1791) → hut pad → walk W through the open door → island (6078,1786) → lane → (4282,1806). I dragged POTION 31220 (f1, full heal) and 31221 (f3, +5-9) onto the Avatar: `Dropped item in backpack` ×2, weight 20 → 40 (`s02d`). Then pad 4 → west side, rested to hp 30, and banked `s02b` |
| Egg 2 → plateau → T26 → north pad | **PASS, hp 30 → 21** | Field follower: NE, N to y 13394, W along y 13366-13190, then W at y 13274 → T26 → pad 26 (14540,7972,0). It took 9 damage near (8294,13034) and no Torax was met. I rested to 30 and banked `s02c` |
| North pad → spitter 1 → pocket | **PASS on the 2nd try; 1 death** | Try 1 (one held run, which also used the wrong mouse origin, harness anomaly 3) drifted to (16544,5696), and the escape run died at (16668,5572). Try 2 used segment runs with a paused read between each: W/E to (15548,7200) → E 2.0 s (16780,7200) → NE 1.45 s (17124,6680) → NE 0.85 s (17428,6376) → N 2.35 s (17448,5140) → E 1.3 s (18064,5100) → walk E (18168,5100), hp 30. That spot is out of SP1, SP2, SP3 and the egg's fast area at 320×200. Banked `s02d` |
| Pocket → doors chamber, first contact | **PASS on the 3rd approach; 1 death** (finding 3) | See the step-3 section below |
| **Step 3: key → leaves → T201 → Map 9** | **PARTIAL.** Every mechanism worked and the Avatar reached Map 9, but dead | Chest `event 1 @ 004E:00A9`. Key 31494 `event 1 @ 0052:04BB`, then `Target result: Item 31172` (the west leaf). That one use set **31172 q 1635 → 611 and 31174 q 1123 → 99**. A leaf double-click gave `event 1 @ 0156:0098`, and the west leaf opened. Then `Unloading map 8` → `Loading Fixed items in map 9` → (13696,14208,0) **hp 0**. Plates `s03a`-`s03d`, `F3` |
| Steps 4+ | **NOT DEMONSTRATED** | Budget |
| GHOST 411 follower | **Present, not near the Avatar** | `findShape 411`: one GHOST (class Container) at (2200,2208,8) on the MYTHAUS island's west side, about 600 units from the Avatar at (2688,1816). It was drawn as a grey figure by the fireplace. It did not follow |
| Log hygiene (`lv_run2.log`) | **PASS for LV code** | 0 each of `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, ERROR and `Cheat`. **1** `Unhandled intrinsic 254 'isGameRunning()'`, the known CHEST_EW `004E` family. **1,937** `Cycle in paint`, all the retail `590 -> 235 -> … -> 590` bone-chamber knot |

### Step 3 in detail: getting past the 808 pair

The MONFAST egg 31095 (20494,4570) runs class `04BB`. On `enterFastArea` it checks bit 0x80 of its mapArray. If the bit is clear, it hatches every MonsterEgg within 112×32 whose monId matches, then sets the bit. `leaveFastArea` clears the bit (`monfast.dis`).

The hatched actors are `FLG_FAST_ONLY|FLG_DISPOSABLE` (`monster_egg.cpp:53`), so each is destroyed when its own chunk leaves the fast area (`item.cpp:2000`). A fresh pair therefore hatches every time the egg's chunk (40,8) re-enters the fast area.

- **First contact (attempt 2).** I stopped at (20204,5100), where the egg had just entered the fast area. 808s 153/154 came 400-600 units south-west in about 3 s and stood on my northward line at (20206,5018)/(20308,5044). I could not go north, because x < 20216 is walled at y ≈ 4680. That cost hp 30 → 9.
- **Retreat.** I ran west 1.5 s + 2.0 s. The 808s moved about 200 u/s against the Avatar's run of about 700 u/s. Within about 3.5 s, 154 had left the fast area and was gone (`findShape 808: 1 found`). At the pocket I opened the pack (`i`), and the f1 potion took hp 9 → 30.
- **What worked (attempt 3).** One held run from (18096,5190): NE 0.75 s, E 2.9 s, N 2.5 s. It passed 153 (now alone) on the corridor's north side. The fresh pair 155/156 hatched behind the Avatar, and he reached (20352,3986) at hp 30 with them 600-800 units south. A N run of 1.4 s ended on top of the chest (20472,3382,16). A walk N of 0.55 s reached **(20541,3195,8)**: the chest (185,222) and the leaves were both in reach, 156 was about 740 away, and hp was 30.
- **The sequence, with the world paused between steps to plan:**
  1. Double-click the chest. The chest gump covers the leaves (`s03b`).
  2. Drag the gump down by its left frame, (62,60) → (62,280).
  3. Double-click the key (127,377).
  4. Click the west leaf at `proj(20287,3055,40) + (0, 40)` = (263,77) at SCALE 2. Both leaves unlocked.
  5. Double-click the leaf. The west leaf opened.
  6. Run NW 0.6 s / N 1.2 s. That ended at (20513,3135): the Avatar was in front of the still-closed **east** leaf, and an 808 was in contact (hp 30 → 20 → 15).
  7. W 0.75 s + N 1.5 s reached the T201 box, but the hp was gone (step 6 below).

## Findings

1. **Severity: medium (route). The island lane damage is the retail LITZAPEW gates, and a stop or a step near a post costs 4-9 hp.** It is not a blocker. This also corrects leg 1's F2: as 10-10 part 2 already established, the shape-264 spheres move only in x on rows y 1599-1695 and 1887-1983, and they never touch the lane.
   - **The landing wedge.** The landing (5962,1766) is wedged only because the post 293 at (5887,1727) occupies y [1695,1727].
   - **The way off.** A mouse walk S needs at least 0.5 s to register. It moves in 64- or 128-unit steps (1766 → 1830; 1786 → 1914, which is in the south sphere row). Then NW until y is in 1792-1822, then W runs.
   - **Damage seen.** hp 23 → 19 at (5962,1830). hp 20 → 11 on the run 5574 → 4474, which crosses two gates. On the second pass the run went 6034 → 4682 → 4282 at hp 24 → 24 with no damage.
   - **Repro.** `replay1017-s01c-m08-island-landing-hp22.sav`.
   - Plate `F1`.
2. **Severity: info (route aid). Two potions sit on the island's east lane and are easy to miss.** They are POTION 31220 frame 1 (full heal: hp := 2×STR) and 31221 frame 3 (+5..9), at (4185,1656,16)/(4226,1616,16) on the dark table by pad 4.
   - **Reach.** They can be reached from (4282,1806): `canReach` box gaps 33/86. Drag each from the table to the Avatar.
   - **Why it matters.** The f1 potion is what let this leg survive the first 808 contact.
3. **Severity: high for a player, retail content. At 640×400 the spitter fast areas cover the whole north route, and at 320×200 they still frame the doors-chamber approach tightly.** Death 2 came from SP3 26910 (22090,6934) entering the fast area when an east run overshot to x 20728 (`event 15 @ 031B` → FIREBOMB 804 `event 5 @ 0324`).
   - **The window.** At 320×200, with y ≈ 5100, the corridor exit must be left northward between x 20216 (the wall) and about 20300 (SP3's fast area). The MONFAST egg enters the fast area at the same x, so the 808s hatch about 450 units from the Avatar.
   - **Fast-area model.** `in_fa()` in the kernel notes reimplements `current_map.cpp:418-506`.
   - **Repro.** `replay1017-s02d-m08-corridor-pocket-hp30.sav`, then E 3.8 s.
4. **Severity: high for a player. Not a blocker, but the step-3 save is missing: the 808 pair kills an unarmed 30-hp Avatar during a door sequence whose every step works.**
   - **What is new.** The pair re-hatches on every fast-area entry of chunk (40,8), and each actor is destroyed when its own chunk leaves the fast area. Both monsters are about 3.5× slower than a running Avatar (about 200 u/s). That makes a kite-and-dash approach viable. It is new against 10-11 finding 2, which needed the now-removed T212 round trip.
   - **How the run went.** It got the Avatar to the chest with a 740-unit lead at hp 30. The death came because the open leaf is the **west** one. A run aimed NW from (20541,3195) stopped in front of the closed east leaf while an 808 was in contact. Each paused planning step also costs about 0.3 s of input latency.
   - **Last good state.** The pocket bank `s02d`. Plates `s03c`/`s03d`/`F3`.
   - **Classification.** Retail monsters on the LV quest route. As on 10-11, this is a balance question: a pre-placed weapon, or a quest-gated MONFAST.
5. **Severity: low. One key use unlocks both leaves (31172 1635 → 611 and 31174 1123 → 99), but the double-click opened only the west leaf.** That is unlike 10-11, where both opened.
   - **Effect.** The passable gap is x [20223,20351].
   - **Not verified.** Whether the east leaf would open on its own double-click was not tested.

## Harness anomalies

1. **The resolution switch.** I went from 640×400 to 320×200 at the north pad. 10-10 part 3 finding 1 showed that the 640×400 fast area puts both spitters in range of the pocket, and my `in_fa` model agreed: at 640×400 the pocket has SP1 and SP2 in its fast area, and at 320×200 none of them. 320×200 is the retail resolution. The window is still 640×400 (`scale_factor=2`).
   - **Projection.** `lv.SCALE = 2`. The world → window projection is `proj(...)` plus **(0, +40)**, the leg-1 +20 game-px constant doubled. It was verified on the leaf click.
2. **Dialogue.** A mousedown on a bark dismisses it, and the AskGump that replaces it then takes the mouse-up. One Mythran pick (the first) was therefore made by the release, not chosen: the reply was to "Lord British says they can help me.", the same pick 10-11 made.
   - **The fix.** `sadv()` presses on the text, moves to (620,390), then releases. After that every pick was read from the screen.
3. **The movement origin.** The mover measures the mouse direction from screen centre **+14 game px** in y (`Mouse::getMouseDirectionWorld`). At SCALE 2 a 110-px "NE" press read as N. `lv.run`/`runvec` now use `lv.morigin()`.
4. **Fixes to `py/lv.py`, made in place.**
   - The `globs()` regex now reads the `[0717 01] = 1` reply form.
   - New `save()`/`bank()`/`scratch()` helpers assert that the slot file changed.
   - `proj()` takes a scale factor.
   - `morigin()` was added.
5. **Presses.** Mouse presses under about 0.5 s often do not move the Avatar at all, prime press or not. Walk steps are 64/128 units.
6. **The console as a pause.** A kernel helper `pz()` attaches and leaves the console attached (the world paused) to read 808 positions. A following `lv.q()` then *closes* the console with its chord, so q's commands run detached. Always `lv.detach()` before acting after `pz()`.
7. **Two traps that fired.** `loadGame` opens the chooser, and slot 1 must then be double-clicked at (318,108). One stray `Escape` opened the Pagan book; a second Escape closed it.

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `replay1017-s02-m08-mythran-intro-done.sav` | `b23cac62` | Upstairs (1636,1452,48), hp 18, step 2 flags set |
| `replay1017-s02b-m08-island-two-potions-hp30.sav` | `96c79312` | Island west side (2912,1816,0), hp 30, weight 40 (POTION f1 + f3) |
| `replay1017-s02c-m08-north-pad26-hp30.sav` | `8d896656` | North pad (14540,7972,0), hp 30, both potions |
| **`replay1017-s02d-m08-corridor-pocket-hp30.sav`** | `596531dc` | Pocket (18168,5100,0), hp 30, both potions. **Leg 3 resume point** |

Note: `s02d` was banked before the f1 potion was drunk, so it holds **both** potions.

## Resume (leg 3)

1. **Load.** Use the same game copy and binary, and **`scummvm.ini` as it now is (320×200, `scale_factor=2`)**. Copy `~/lv-checkpoints/replay1017-s02d-m08-corridor-pocket-hp30.sav` to `saves/ultima8.001` and start with `lv.start(log=…, slot=1)`. Then send `debugflag_enable Object`. Use `lv.SCALE = 2`, and aim at `proj(...)` + (0,40).
2. **State.** Map 8 (18168,5100,0), hp 30. The pack holds POTION f1 (red, full heal) and f3 (yellow). Step 2 is done. The doors are locked and the key is in chest 31495.
3. **The approach that worked.**
   1. From the pocket, hold one run: NE 0.75 s, E 2.9 s, N 2.5 s (a step NE first keeps the line on the corridor's north side).
   2. Then N 1.4 s, then walk N 0.55 s, to stand at about **(20541,3195,8)**.
   3. The 808s hatch behind you and need 4+ s to arrive.
4. **The sequence. Pre-plan it all, and send it as one batch with no reads in between.**
   1. Double-click the chest (185,222).
   2. Drag the gump down by its left frame, (62,60) → (62,280).
   3. Double-click the key (127,377), then click the west leaf (263,77).
   4. Double-click the west leaf (263,77).
   5. **Then run W first, about 0.5 s to x ≈ 20300, and only then N.** The open gap is the west leaf, x [20223,20351].
   6. Expect contact about 4 s after arrival.
   7. Keep the f1 potion for after Map 9, or drink it first: open the pack with `i` and double-click the red potion.
5. **Better still.** Step to about (20330,3195) before opening the chest; it is in reach of the chest and in front of the west leaf. That makes the final move a straight N run.
6. **Then.** Map 9 arrives at (13696,14208); T203 box x [13952,14784), y [16408,17176) → Map 11. Map 9 and Map 11 were rebuilt after 10-11, so re-plan the routes from the pinned FIXED. Then step 4 (four talismans, receptacles, T205 → Map 10), then step 5 (Atli).

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-17-replay-leg2/` (10 plates: `s02a`-`s02d`, `s03a`-`s03d`, `F1`, `F3`).
- **Wrote** the 4 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/replay1017/`:
  - `lv_run2.log`, `trace2.txt` and `sp/l2-*`.
  - Disassemblies: `monfast.dis`, `potion.dis` and `misstrap.dis`.
  - **The changed `scummvm.ini`**, with the old one at `scummvm-640x400.ini`.
  - The edited `py/lv.py` (harness anomaly 4).
  - Slot 1 holds the `s02d` save. Slot 0 is the engine's autosave.
- **Stopped:** my ScummVM and Xvfb `:95`.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and the binaries. The game copy's hashes were re-checked: all OK.

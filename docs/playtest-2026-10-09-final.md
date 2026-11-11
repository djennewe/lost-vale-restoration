# Final verification: recreated scheduler, Tyorvi's new stash, Aramina's retail bits (2026-10-09)

**Build under test.** `main` at `c9929e4`, plus the uncommitted `ARTIFACTS.sha256` and engine patch. The fork is `e3d2f40c`.
- The log reads `usecode/eusecode.flx: cd847392987c3e1f6f7b4bc9e4169838, 1525384 bytes`.
- The game copy `/tmp/claude-1000/vfin/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Its sha256 values match `shared/build`: EUSECODE `25503d8a99d0…`, U8SHAPES `bb0e4cda1e46…`, TYPEFLAG `794d4b80a918…`, ANIM `77e9705da254…`, and FIXED `13321f0782d1…` in both places.
- `scummvm-lv/scummvm` (mtime 08:06:26) is newer than fork commit `e3d2f40c` (08:06:12). `strings` finds `No SchedulerProcess in savegame; recreating` in the binary, and the code is at `scummvm-lv/engines/ultima/ultima8/ultima8.cpp:1768-1771`.
- Plates are in `docs/playtest-2026-10-09-final/` at 640x400.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| F1 | A no-scheduler save logs the recreate line, and `event 8` fires at an hour boundary with the Avatar on the map. Negative control: a save that already has a scheduler logs no line and gets no second one | **PASS** |
| F2 | Tyorvi stands at (21823,8031,0) in threemoons, firstebb and lastebb, drawn in full and clickable | **PASS** |
| F3 | After the Passage Test with plantScene set, Thordis leaves the plateau and reaches (4415,7423,0) without falling off z 64 | **PASS**, by two routes. Finding 2 covers the self-heal route's one-hour lag |
| F4 | After the ceremony in `run-s13`, Atli, Thordis and Ezrekal are at their schedule homes and none is inside a wall | **PASS** |
| F5 | Several NPCs are at their new points after an hour boundary, for at least one more period | **PASS** for 6 period changes. **Defect:** a schedule teleport made inside the fast area is undone (finding 1) |
| F6 | Aramina: retail 0x203 on meeting, 0x204/0x205 on name/job, old 0x65F stays 0, her route still runs, ORLOK's "Tell me of Aramina." appears afterwards | **PASS** |
| F7 | `cp2-palace.sav` still loads and plays | **PASS** |
| L | Log hygiene | **PASS** for LV code. No `Unhandled intrinsic`, process-loop, Segmentation, Assertion, teleport-failure or segment-access lines. The only warnings are the known retail-context ones (see L) |
| C1 | `tools/run_all_tests.sh` | **PASS**: `OVERALL: PASS — 43/43 test file(s)` |
| C2 | Tracked patch equals the fork diff | **PASS**: `PATCH_EQUAL` (`git diff 01bd8879 HEAD -- engines/ ':!…detection_tables.h' \| diff -q - …patch`) |
| C3 | `build_artifacts.sh`, `install_lv.sh`, `build_scummvm.sh` | **SKIPPED** on instruction (already run). The sha256 match and binary mtime above stand in for them, and the usecode Compilation Report was not re-read |

## Method

- **Isolation.**
  - Xvfb `:86` (1280x800), with the window at (480,300).
  - Scratch `/tmp/claude-1000/vfin/` holds `scummvm.ini` (`usehighres=true`, `frameLimit=false`) and `saves/`.
  - `run.sh` runs `scummvm-lv/scummvm --config=… --savepath=… --extrapath=scummvm-lv/dists/engine-data --debuglevel=1 --path=vfin/game --save-slot=1 ultima8`.
  - The driver is the `vca` `drv.py`/`h.py`, re-pointed to `:86`, with the mouse-walk reference at (320,214).
  - Only my own pids were started and stopped.
- **Saves.** Each checkpoint was copied over `saves/ultima8.001` and loaded, either at launch or with `Ultima8Engine::loadGame 1`. The checkpoints were `run-s11-tyorvi-key`, `cp10-test-done`, `run-s13-shield-halves` and `cp2-palace`. Game time was read from each save's INFO block (`vfin/savinfo.py`) after `Ultima8Engine::saveGame`.
- **Game-state writes.**
  - Teleports with cheats on, each followed by a verified `Cheats = false`.
  - `CameraProcess::moveToAvatar`.
  - `MainActor::toggleCombat`, needed on the 09-07 saves.
  - `debugflag_enable Object`.
  - The retail dev menu's **Time** option for every period step. It is a click on the Avatar with cheats on, then "Time", which runs `SetTimeInGameHours(TimeInGameHours() + 4)` (`lv-patched/AVATAR.UNK:979-1002`). Plates: `F5-00-dev-menu`, `F5-01-devtime-bark`.
  - **No `setGlobal`.** Every conversation answer and every talk was clicked on screen.
- **First launch (`lv_run.part0-nodisplay.log`).** My first launch came up without a display: the Xvfb had died with its subshell. That log still shows the recreate line, and it is kept as a second sample.

## F1: the recreated scheduler, PASS

**Recreate on load.** `run-s11-tyorvi-key.sav` (md5 `96e20997…`, hour 27.76, bloodwatch, `sched=False`) was loaded at launch:

```
75: KERNEL: ok
76: WARNING: No SchedulerProcess in savegame; recreating!
77: APP: ok
```

`Kernel::processTypes` then lists `SchedulerProcess: 1` and `U8AvatarMoverProcess: 1`.

**An hour boundary with the Avatar on the map.**
- **Setup.** The Avatar stood still at Map 10 (19456,9056,0), Tyorvi's Gunnar spot from the save, and was not teleported.
- **The pass.** At the hour-27→28 crossing (bloodwatch→firstebb; the next save read hour 28.09) the log shows `event 8` for every LV NPC:
  ```
  Item: 102 (shape 707) calling usecode event 8 @ 0466:0165
  Item: 105 (shape 574) calling usecode event 8 @ 0469:00CC
  Item: 106 (shape 707) calling usecode event 8 @ 046A:023F
  Item: 107 (shape 707) calling usecode event 8 @ 046B:0196
  Item: 112 (shape 574) calling usecode event 8 @ 0470:0234
  Item: 113 (shape 707) calling usecode event 8 @ 0471:023C
  Item: 115 (shape 707) calling usecode event 8 @ 0473:0186
  Item: 116 (shape 200) calling usecode event 8 @ 0474:018B
  ```
- **The moves.**
  - Ezrekal 116 went from (12799,12543), her bloodwatch home, to **(12895,13439)**, her firstebb garden point.
  - Sigrid 102 went from (4895,8991), her bloodwatch point, to **(5503,16383)**, her firstebb hunt point.
  - Tyorvi 115 stayed at (19520,9220), 170 units from the Avatar, as canSafeTeleport requires.
- **A second crossing.** The second load of the same save is described under the in-game reload test below. On that load the Avatar was teleported to (19231,7100) and waited there, and at the 27→28 crossing `event 8` fired again for all 8 NPCs. Tyorvi then went from (19520,9220) to his stash and was read at (22123,7731), loitering, with Ezrekal at (12895,13439).

**Negative controls.**

| Load | Saved scheduler | Recreate line | `processTypes` |
|---|---|---|---|
| `F1-after-load-save.sav`: run-s11 loaded, then saved at once (its KERNEL holds `SchedulerProcess` ×1), then reloaded in game | yes | **none** (`KERNEL: ok`, `APP: ok`) | `SchedulerProcess: 1` |
| `cp10-test-done.sav` (native scheduler) | yes | **none** | `SchedulerProcess: 1` |
| `cp2-palace.sav` and its replayed save `F7-cp2-after-play.sav` | yes | **none** | `SchedulerProcess: 1` |
| **Adversarial:** `run-s11` loaded *in game* over a running world that already had a live scheduler | no | `Resetting Kernel...`, `KERNEL: ok`, `WARNING: No SchedulerProcess in savegame; recreating!` | `SchedulerProcess: 1`, not 2 |

The four recreate lines in the two logs are 1 + 3: the headless launch, the first launch, and the in-game reloads of `run-s11` and `run-s13`. Every one came from a `sched=False` save.

**Pass at load.** A recreated scheduler has `_lastRun = 0`, so it runs a full pass at once on load as well as at the next hour. In the log, the second `run-s11` load (line 265) is followed by `event 8` for all actors at line 366, before any hour boundary. This is harmless: every schedule is guarded by canSafeTeleport. It matches what `newGame` does.

## F2: Tyorvi at the new stash point, PASS

| Period (hour) | Read | Plate | Talk |
|---|---|---|---|
| firstebb (28) | Teleported to the stash at the 27→28 pass, then loitering at (22123,7731), (21837,7851), (21763,8151) and others, all z 0 | `F2-01` shows him on open ground south of the still-house, drawn in full | Double-click → `event 1 @ 0473:0354`, and the menu opens (`F2-02`) |
| threemoons (36) | **(21823,8031,0)** exactly, read with the Avatar at (15500,8000) | `F2-04` shows him on the lane east of the hut, drawn in full | `event 1 @ 0473:0354`, menu **I have spoken to Ezrekal. / Do you have the Key to the Clouds? / bye** (`F2-05`) |
| lastebb (40) | **(21823,8031,0)** exactly; on arrival at the view spot, (21667,8151) | `F2-06` shows him drawn in full | `event 1 @ 0473:0354` (`F2-07`) |
| bloodwatch→firstebb (52) | Home (7423,7519) → stash. The Avatar was 760 units away at (21823,8791), so the pass teleported him into view | `F2-08` | — |

- **Coverage.** `geo/occl.py` runs the new `ItemSorter.overdrawn` with shape 707. It reads **0%** at (21823,8031) and **100%** at the old point (22335,7647), where the cliff (shape 32 at (22560,7936,48)) covers him. Every loiter spot I read (for example (22123,7731), (22123,7921) and (21837,7851)) reads 0%, and (21319,8391) reads 5%.
- **The other periods.** At daytide, eventide and bloodwatch, with the Avatar far away, he was at home (7423,7519) (see F5).

## F3: Thordis off the plateau, PASS (two routes)

`cp10-test-done.sav` has a scheduler; it is at hour 29.07, plantScene 1, endOfPlantScene 0. On load, Thordis is at (13103,29399,**64**) and the Avatar at (13055,30079,64) on the Test Grounds.

**Route A: the scene-end conversation.**
1. A double-click on Thordis logged `event 1 @ 046A:0E71`, and the restored aftermath played: "Sad to say it I am. But give you the Zealan Mark I will…" (`F3-01`).
2. Then plantScene was 0 and endOfPlantScene 1.
3. Over 120 s on the plateau, with the Avatar beside her, I read her position 10 times. She stayed between z 64 and 72 the whole time, at (12983..13343, 29219..29819) (`F3-04`), and **never read z 0**.
4. I teleported the Avatar to (15500,8000) and waited for the natural hour-29→30 pass (`event 8` for all 8 NPCs). Thordis was then at **(4415,7423,0)**. She was later seen loitering at her house at (4521,7327,0) (`F3-05`).

**Route B: the self-heal only (no conversation).** I reloaded the same save, left at once for (15500,8000), and stepped the dev-menu Time:

| Step | Thordis | Atli | plantScene |
|---|---|---|---|
| Before | (13283,29579,72) | (19122,9684,8) | 1 |
| +4 h (daytide, hour 33) | **(13283,29579,72), unmoved** | (19615,9855,0) | **0** |
| +4 h (threemoons, hour 37) | **(4415,7423,0)** | (19615,9855,0) | 0 |

She reaches home, but only on the second pass (finding 2).

## F4: send-homes after the Sacred Circle ceremony, PASS

**State at load.** `run-s13-shield-halves.sav` logged `No SchedulerProcess in savegame; recreating!`. It holds both halves in the pack (12073 q81 and 2932 q82), with shieldFixed 0 and avatarPoisoned 1.

**The ceremony.**
- I teleported to (20304,17600), turned cheats off, waited 20 s and toggled combat off. I then walked north-east.
- The log shows `Item: 8487 (shape 73) calling usecode event 7 @ 05A5:0080` (EggShades).
- From the screen I picked **Let's be reasonable!**, **Yes, Priestess.** (`F4-01`) and **Please, High Priestess.** (`F4-02b`). The three elders spoke their lines (`F4-02`).
- After the scene, inShadeScene was 0 and shieldFixed 1. The elders logged `event 16` (leaveFastArea), as the send-homes moved them.

**Afterwards** (hour 30, firstebb):

| Elder | Read | Target | Plate |
|---|---|---|---|
| Atli 107 | (19231,6943,0) → loitering at (19143,6975,0) | (19231,6943) | `F4-04-atli…`: on open ground by his hut, next to the well |
| Thordis 106 | **(4415,7423,0)** → loitering at (4595,7363,0) | (4415,7423) | `F4-04-thordis…`: open ground between two huts |
| Ezrekal 116 | **(12799,12543,0)** → (13135,12495,0) | (12799,12543) | `F4-04-ezrekal…`: inside the open yard of her stockade, not inside a fence |

The test's check 4 also covers the EggShades points; it passes in the 43/43 run.

## F5: more periods, PASS, with one defect

The world is `run-s11`. The Avatar was parked at (15500,8000) unless noted, and each row is one dev-menu step.

| Period (hour) | Sigrid | Ragnar | Thordis | Atli | Ingjald | Hrodny | Tyorvi | Ezrekal |
|---|---|---|---|---|---|---|---|---|
| threemoons (36) | (4895,8991) | (7039,17151) | (4415,7423) | (19615,9855) | (20767,7455) | (21759,8447) | **(21823,8031)** | (12799,12543) |
| lastebb (40) | (4895,8991) | (7039,17151) | (4415,7423) | (19231,6943) | (20767,7455) | (21759,8447) | **(21823,8031)** | (12895,13439) |
| eventide (44) | (4895,8991) | **(5439,10527)** | (4415,7423) | (19615,9855) | (20767,7455) | (21759,8447) | (7423,7519) | (12799,12543) |
| bloodwatch (48) | (4895,8991) | (7039,17151) | (4415,7423) | (19231,6943) | (20767,7455) | (21759,8447) | (7423,7519) | (12799,12543) |
| firstebb (30, cp10 world) | (5503,16383) | (7039,17151) | (4415,7423) | (19231,6943) | (20767,7455) | (21759,8447) | (21823,8031) | (12895,13439) |

Every value is exact against the schedule tables (`lv-patched/*.UNK`, `lv-new/SIGRID.UNK`), and every z is 0. Each step logged `event 8` for all 8 NPCs.

**Daytide (hour 32), Avatar at (21823,8791).**
- Correct: Sigrid (5503,16383), Ragnar, Thordis in the field (5247,9343), Atli (19615,9855) and Ezrekal (12799,12543).
- Hrodny and Tyorvi were held because the Avatar was within 700 units of them (N3 behaviour).
- **Ingjald was wrong** (finding 1).

## F6: Aramina on retail bits, PASS

The save is `cp2-palace.sav`: MORDEA alive, 0x207 = 1. Every flag was read with `UCMachine::getGlobal`.

| Bit | At load | After talk 1 |
|---|---|---|
| 0x203 araminaMet | 0 | **1** |
| 0x204 araminaName | 0 | **1** |
| 0x205 araminaJob | 0 | **1** |
| 0x65F / 0x660 / 0x661 (old) | 0 / 0 / 0 | **0 / 0 / 0** |
| 0x0F, 0x27, 0x3C, 0xBF, 0xD6, 0x11A, 0x147, 0x36(2) | 0 | 0 (0x0F read 1 only *during* the later ORLOK conversation, then 0 after "Goodbye.", which is retail METHOD's convo flag) |
| 0x207(2) | 1 | 1 |

**1. ORLOK first (negative control).** The talk logged `Item: 10 (shape 403) calling usecode event 1 @ 040A:1CCB` (`F6-01`). I picked **What is your name? → My name is Avatar.**, then **Tell me of Tenebrae.** The submenu was **Tell me its history. / Goodbye.**, with no Aramina option (`F6-03`).

**2. Aramina, m41, at home.**
- **The talk.** It logged `Item: 13 (shape 282) calling usecode event 1 @ 040D:10E9` and gave **"How may I serve you, stranger?"** (`F6-07`).
- **The menu.** It read **By what are you called? / bye** (`F6-08`).
  - "By what are you called?" gave "My name is Aramina." and the menu **What do you do here? / bye** (`F6-10`).
  - "What do you do here?" gave "I am merely a servant here." (`F6-11-job-0`) and the menu **Tell me about the palace. / bye** (`F6-12`).
  - Then bye.

**3. ORLOK again.**
- **The menu.** It read **What do you mean by poison? / What do you do? / Tell me of your tales. / Tell me of Tenebrae. / Goodbye.** (`F6-14`).
- **The Tenebrae submenu.** It now read **Tell me its history. / Tell me of Aramina. / Goodbye.** (`F6-15`).
- **The pick.** "Tell me of Aramina." gave "Aramina, poor girl ye know, she is really Lady Mordea's sister…" (`F6-16`).
- **Static check.** ORLOK 0x40A is byte-identical to retail (`cmp` of the two disassemblies), and its option is gated by `962C: push global 0203h 01h`.

**4. Second negative control (`F6-17`).** I reloaded `cp2-palace` fresh and talked to her again. The talk logged `event 1 @ 040D:10E9`, gave "How may I serve you, stranger?", and I picked **bye** at once. 0x203 stayed **0**, because the source sets araminaMet only inside the "By what are you called?" case (`U8/ARAMINA.UNK:744`).

**The route.** In the fresh reload, before any talk, I read her eight times over 40 s:
- `Kernel::listProcesses 13` showed `Process 187 class UCProcess, item 13, type 205 … classname: ARAMINA, IP: 040D:04B8` (the atHome route function), plus a PathfinderProcess.
- Her positions included (17179,15459), next to marker f3 (17172,15444); (16495,15967), next to f5 (16479,15903); and (17104,15866) and (17059,15659), between f1 and f3.
- So **the route runs.** After a conversation it is replaced by a LoiterProcess (finding 3).

## F7: the old Tenebrae save, PASS

`cp2-palace.sav` (2026-07-30) loaded with `KERNEL: ok`, `Reclaimed 0 _objIDs on load.` and no recreate line, showing the palace (`F7-01`).
- **Play.** It then played teleports to m39, m41 and m39, four conversations, and walks.
- **The save.** "Saving game is currently unavailable" appeared once, while an ORLOK menu was open. After "Goodbye." the save worked.
- **The reload.** `Reclaimed 4 _objIDs on load.`, `SchedulerProcess: 1`, and 0x203/0x204/0x205 = 1 persisted (`F7-02`).

## L: log hygiene

`vfin/lv_run.log` ends at 178,501 lines over one launch with seven in-game loads. `lv_run.part0-nodisplay.log` has 127 lines.

| Pattern | Count | Context |
|---|---|---|
| `Unhandled intrinsic` | 0 | |
| `stuck in process loop` | 0 | |
| Segmentation / Assertion | 0 / 0 | |
| `Trying to access segment` | 0 | |
| teleport failures | 0 | |
| `No SchedulerProcess in savegame; recreating` | 3 (+1 headless) | Only `sched=False` saves |
| `Terminated/No AvatarMoverProcess` | 0 | |
| `Non-existent process PID (0) in implies` | 2 | Both on m39 entry in Tenebrae, right after `I_resetRef item=24/72/73/79 type=0x00F0` and before `event 15` of a shape-699 item (retail content; seen before in the 10-09 Aramina report) |
| `popToContainer to invalid container (76)` + `Destroying orphaned ethereal object (6662)` (shape 174) | 1 + 1 | m41 re-entry; known (10-09 Aramina report) |
| `Cycle in paint dependency graph` | 133,454 | All on Map 10 views by Gunnar and Atli's door: `426->856`, `426->208`, `856->208`, `208->526`, and 7× `707->426`. None in Tenebrae or the ceremony. The shapes are the Gunnar wood walls, workbench, small rubble and NPCs. This is a known family (09-26 reports); the count scales with the time spent standing at (21823,8791) |

## Findings

1. **A schedule teleport inside the fast area is walked back by the loiter leash.**
   - **Evidence.**
     - `t-bloodwatch.sav`, Avatar at (21823,8791), dev-menu step to daytide. Ingjald's `event 8` teleported him to his still point: he read **(22015,8031,0)** at +7.9 s (784 units from the Avatar, so canSafeTeleport passed).
     - He then walked straight home: (21727,8031) at 14 s, (21502,7854) at 20 s, (20959,7423) at 28 s, and (20767,7463) from 73 s on.
     - `Kernel::listProcesses 112` shows the **same `LoiterProcess 5997`** before and after the teleport, driving fresh PathfinderProcesses.
     - The same thing happened in the first daytide step, where he was read at (20663,7599) and (20479,7375).
   - **Cause.** The fork's loiter leash anchors on the LoiterProcess's first run (`loiter_process.cpp:75-81`, `_anchorX/_anchorY`). A teleport that keeps the actor in the fast area fires no leave/enter event, so the old loiter survives with its old anchor.
   - **Scope.**
     - It affects any loitering NPC whose `schedule()` teleports it while the Avatar is 700+ units away but the NPC stays inside the fast area.
     - With the Avatar off-screen (all my far-parked steps), every NPC stayed at its point.
     - A player near Gunnar at noon sees Ingjald pop to the still and walk home.
   - **Fix direction** [INFERENCE]: re-anchor the loiter when the actor moves more than about 10×32 from the anchor in one step, or kill PT_ACTIVITY and re-set it after `safeTeleport`.
   - Confidence: high on the mechanism and medium on the fix.
2. **The plateau self-heal releases Thordis one pass late.** The scheduler visits actors in id order (`scheduler_process.cpp`, `_nextActor` 1→255). Thordis (106) therefore runs `schedule()` while plantScene is still 1 and returns; Atli (107) clears it in the same pass. In route B she was still on the plateau after the first pass and reached home on the second. That is one game hour (≈15 real minutes at 1×) at natural speed. Route A, the conversation, has no lag. This is low severity. A fix would clear the flag before 106 runs, or have Thordis carry the same self-heal. Confidence: high.
3. **A conversation ends Aramina's at-home route.** After talk 1, `Kernel::listProcesses 13` showed only `LoiterProcess … type 205`. The ARAMINA route UCProcess at `040D:04B8` was gone, and she loitered near the door ((16771,16291) and nearby) instead of visiting the markers. The cause is `exitConvo()` setting activity 0 (the known limitation in CLAUDE.md, "does not replicate the full base game `METHOD::exitConvo()`"). This change did not cause it. A fresh entry (fast-area enter) restarts the route.
4. **The recreated scheduler runs a pass at once on load** (`_lastRun = 0`): line 366 after the load at 265. This is benign and probably desirable, because an old save's NPCs snap to their current-period points far from the Avatar. It is noted only because it means "an hour boundary" is not needed for the first pass.
5. **A schedule teleport can be seen happening.** The canSafeTeleport radius (700) is smaller than the view. In `F2-08`, Tyorvi appears on screen at the stash with the Avatar 760 units away. This is retail behaviour and is noted for the N3 wording only.

## Harness anomalies

1. **My first ScummVM launch had no display.** The `(Xvfb … &)` subshell died. The game still loaded headless and logged the recreate line (`lv_run.part0-nodisplay.log`). `setsid nohup Xvfb` fixed it.
2. **`noclobber` is set in the tool shell**, so `>` onto an existing file fails. Use `>>`.
3. **Ezrekal-style click theft did not occur, but Aramina's sprite needed a ~10 px lower aim** than the plane projection gives on m41 (z 48). The grey-dress pixel match (10-09 Aramina report) found her when she was walking.
4. **`frameLimit=false` let the natural hour 29→30 crossing arrive within seconds of the wait starting.** The cp10 save was already at 29.54 after the conversation.

## Disk changes

- **Wrote** this report, 36 plates for F1-F7 and plate `F8-01` in `docs/playtest-2026-10-09-final/`.
- **Scratch in `/tmp/claude-1000/vfin/`:**
  - `game/`, `scummvm.ini`, `run.sh` and `xvfb.log`;
  - the logs: `lv_run.f1-f7.log` (the F1-F7 session, renamed), `lv_run.log` (the F8 session) and `lv_run.part0-nodisplay.log`;
  - `saves/`: `ultima8.001` holds my F8 run's state, since `gtime` saves to slot 1; the engine also wrote `timestamps`;
  - `py/` (driver), `savinfo.py`, `geo/occl.py`, and `dis/` (ORLOK and ARAMINA disassemblies);
  - `sp/`: frames, plus the saves `F1-after-load-save`, `t-{daytide,threemoons,lastebb,eventide,bloodwatch,daytide2}`, `F3-*`, `F3b-*`, `F7-*` and `f8-threemoons`.
- **Not touched:** `shared/`, `~/lv-checkpoints` (read only), `~/.config/scummvm`, and every source, builder, map, fork, TODO or HANDOFF file. Nothing was committed.
- **Stopped:** my ScummVM and Xvfb `:86`.

## F8: leash re-anchor (fork 4ccd3fe7)

**Build.** The artifacts are unchanged; the game copy is the same `vfin/game` as above. Fork `4ccd3fe7` ("Loiter leash re-anchors after a teleport or scripted walk") re-anchors a LoiterProcess when the actor is more than 480 units from its anchor on x or y (`loiter_process.cpp`, `LEASH_JUMP = 480`).

### Verdicts

| ID | Claim | Verdict |
|---|---|---|
| F8a | After the repro, Ingjald is teleported to the still (22015,8031) and stays loitering there | **PASS** |
| F8b | Negative control: an NPC its schedule did not move keeps loitering around its own spot, and no NPC drifts away unbounded | **PASS** |
| F8c | The binary postdates `4ccd3fe7`, and the patch equals the fork diff | **PASS** |
| L | Log hygiene, F8 session | **PASS**: 0 `Unhandled intrinsic`, 0 `Non-existent process`, 0 process-loop, 0 Segmentation, 0 Assertion and 0 segment-access lines in 50,522 lines. The 49,730 `Cycle in paint` lines are the known Map 10 family; the other warnings are the three ScummVM GUI-theme startup lines |

### F8c: binary and patch, PASS

- **Fork.** The `lost-vale` tip is `4ccd3fe7`, committed 10:09:25.
- **Binary.** `scummvm-lv/scummvm` has mtime 10:09:31 and `world/actors/loiter_process.o` 10:09:27. `scummvm-lv/…/loiter_process.cpp` matches the fork's copy (`diff` → `SRC_SAME`) and contains the `LEASH_JUMP` block.
- **Patch.** `git diff 01bd8879 HEAD -- engines/ ':!engines/ultima/detection_tables.h' | diff -q - tools/scummvm-patches/0001-lost-vale-engine.patch` prints **`PATCH_EQUAL`**.

### F8a: Ingjald stays at the still, PASS

**Setup.** One fresh launch on the rebuilt binary loaded `sp/t-bloodwatch.sav`, a save that has a scheduler (no recreate line). I teleported the Avatar to (21823,8791) on Map 10, and turned cheats off. I then stepped the dev-menu Time twice: bloodwatch → firstebb, then firstebb → daytide (hour 56). The Avatar stood still from the teleport to the end.

**Reads.** At each read I took `objectInfo` and `Kernel::listProcesses` for 112, 113 and 115:

| t after the daytide step | Ingjald 112 | LoiterProcess |
|---|---|---|
| 10.5 s (pass still running) | (20878,7630) | 6024 |
| 24.0 s | **(22015,7951)**, teleported to the still | 6024 |
| 37.5 s | (22247,7727) | 6024 |
| 51.1 s | (22135,7851) | 6024 |
| 64.6 s | (21719,8159) | 6024 |
| 78.1 s | (22119,7647) | 6024 |
| 91.6 s | (22179,7587) | 6024 |
| 105.2 s | (21799,7591) | 6024 |
| 118.7 s | (22115,7655) | 6024 |
| 132.3 s | (21703,8215) | 6024 |

- **Bounds.** For 108 s after the teleport, the reads stayed inside x 21703..22247 and y 7587..8215. The largest per-axis distance from the still point is **444**, and he never moved toward home (20767,7455).
- **Same process, new anchor.** This is the same LoiterProcess 6024 that walked him home under `e3d2f40c` (finding 1). It now wanders around the still.
- **Event.** The log for the step shows `Item: 112 (shape 574) calling usecode event 8 @ 0470:0234`.
- **Plate.** `F8-01-ingjald-at-still-daytide` was taken at 140 s, with Ingjald at (21975,7903) by the still-house corner and Hrodny in the centre.

**The way back.** The next step was daytide → threemoons (hour 60). Ingjald's schedule teleported him home: (20783,7455) at 24 s, still under LoiterProcess 6024. For 70 s he stayed within **356** of (20767,7455), at x 20555..21123 and y 7443..7747. The re-anchor works in both directions.

### F8b: negative control, PASS

**Hrodny 113.** Her schedule held her at every step, because the Avatar was within 700 of her. She ran under one LoiterProcess, **6019**, across all three periods: firstebb 80 s, daytide 132 s and threemoons 94 s, for 22 reads in about 5 minutes. Every read was inside x 21363..22083 and y 8111..8715. Her farthest read from her own point (21759,8447) was 396 on x and 336 on y. Her loiter was never re-anchored away, and she did not drift.

**Tyorvi 115** gives two more checks:
- In firstebb, already at the stash under LoiterProcess 5706, he stayed within (21643..22155, 7923..8331).
- At daytide, `canSafeTeleport` passed and he went home, which is outside the fast area: his loiter went away, and he read (7423,7519) with none.
- At threemoons he came back to the stash with `event 15` (enterFastArea) and a new LoiterProcess 4578. He then stayed within **360** of (21823,8031).

**Unbounded drift.** No NPC drifted unbounded. Across the session every loitering read is within 444 of its NPC's current schedule point.

**Edge left open** [INFERENCE]: a loiter re-anchors whenever a pathfinder detour carries the actor more than 480 from the anchor. A target is at most ±320 from the anchor, so that needs a path that overshoots by 160 or more. No re-anchor without a teleport was seen in about 5 minutes × 3 NPCs. A longer soak in a cluttered spot, such as Ezrekal's stockade, would bound this better.

### F8 disk changes

- **Wrote** this section and plate `F8-01-ingjald-at-still-daytide.png`.
- **Scratch.**
  - The F1-F7 log was renamed to `vfin/lv_run.f1-f7.log`, and the F8 session is `vfin/lv_run.log`.
  - The save `sp/f8-threemoons.sav` is the state at hour 60.
  - `saves/ultima8.001` is that same hour-60 save.
- **Stopped:** my ScummVM and Xvfb `:86`.

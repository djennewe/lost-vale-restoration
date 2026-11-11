# Compiler wave 2 final build, instance A, verified in engine (2026-10-07)

Build under test: the uncommitted tree on top of `main` `a2aaf16`. EUSECODE
`8c5a8419`, FIXED `c3d29a1f`, ScummVM `scummvm-lv/scummvm` (14:17, after fork
`10d59e56`, 13:53). The session log reads `usecode/eusecode.flx:
e1fed4c81e85b86ff1b59810ab50f94a, 1524630 bytes` and `Running Ultima VIII:
Pagan (Gold Edition + Lost Vale/DOS/English)`. I used the standard harness on
display `:77`. Plates are in `docs/playtest-2026-10-07-wave2-final-a/` at
640x400.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| A1 | Passage Test, then Thordis's "other people" menus and yes/no | **PARTIAL.** The scene, the one-menu fix and the yes/no wait all pass. But the "What else" branch now soft-locks the game: an ask with an empty list that `use()` waits on forever (finding 1) |
| A2 | Double-clicking the Avatar opens the paperdoll, no segfault | **PASS.** Four double-clicks and one look-click, no crash. The paperdoll toggles open and shut |
| A3 | Atli "Tell me more of the test." answers; bye leaves him loitering and the Avatar free | **PASS** |
| A4 | Lord British scene at Tenebrae from a fresh world reaches `lbDone` 1 | **PASS.** Hatch process type is 0x210 |
| A5 | Map 18 south colonnade is off the wall | **PASS.** Columns end at y 8447 and plinths at 8495; nothing is drawn on the outside face |
| A6 | Log hygiene | **PASS with notes.** 4 `Non-existent process`, all old; 0 stuck; 0 Segmentation; 0 Assertion; 29 `Cycle in paint` (debug level, finding 3); 0 Unhandled intrinsic |
| — | Fork patch equals the fork diff | **PASS.** `diff -q` is silent (`PATCH-EQUAL`) |

## Method and harness writes

- **Backup.** I backed up the 48 saves and `scummvm.ini`, with an md5 list, to `/tmp/claude-1000/w3a/bak/`. The driver is a copy of `/tmp/claude-1000/w2a/py/` with its `pgrep` narrowed to `-p …/shared/u8-lv-patched`, so it ignores instance B.
- **Artifact sync.** `session.sh start` synced `STATIC/FIXED.DAT`, `FIXED.DAT` and `USECODE/EUSECODE.FLX` from `shared/build`.
- **One session:**
  - fresh world: A4, then A2;
  - `run-s7-ragnar-stone.sav`: A1, run 1;
  - `run-s7` again: A1, run 2;
  - `cp8-atli-met.sav`: A3, then A5.
- **Loading saves.** Each checkpoint was copied over `ultima8.001` and loaded with `Ultima8Engine::loadGame 1`.
- **Game-state writes:**
  - teleports with cheats on, each followed by a toggle back to `Cheats = false`;
  - `Item::grab 15048`, once per run;
  - `CameraProcess::moveToAvatar`, many times;
  - `debugflag_enable Object`;
  - `UCMachine::setGlobal 0x455 1 1` and `0x456 1 1` in run 2 only. In run 1, finding 1 shows the organic route to those flags.
- **Organic play.** I walked into both scene eggs and clicked every menu answer from the screen.

## A1: Passage Test and Thordis, PARTIAL

**Scene (run 1).**
- **Setup.** `run-s7`, `Item::grab 15048` (weight 30→40), a teleport to Map 10 (12800, 29720, 64), `moveToAvatar`, then a 1.6 s walk north.
- **Hatch.** The walk logged `Item: 7570 (shape 73) calling usecode event 7 @ 059A:0080`. One second later, `Kernel::listProcesses` showed `Process 7470 class UCProcess, item 7570, type 210, … classname: EGGPLANT`, the new hatch type.
- **I then left it alone for 130 s.** Afterwards:
  - `avatarPoisoned`, `haveMark`, `plantScene` and `firstPoisoned` all read 1;
  - weight was 30, and `findShape 798` found only the Map 0 copy (13751), so the stone was consumed;
  - no scene `UCProcess` was left;
  - the Avatar walked from (13055, 30079) to (12855, 30079) (`A1-01`, `A1-02`).

**MINIAIR (run 2).** Same setup. `findShape 481` at 11 s read `Item 12371 (class Item, shape 481) (uc: MINIAIR), 32, (12873, 29737, 64)`, and at 29 s it read 0. The whirlwind is visible in `A1-15`. The four flags and the stone ended as in run 1. Neither run window logged any `Non-existent`, `stuck`, `Unhandled`, `combine` or `segment 0000` line.

**Thordis after the scene.** The double-click logged `event 1 @ 046A:0E43`.
- **Scene-end talk.** It played through "Oh my, terrible this is…" to "…Leave you alone now I will." (`A1-03`, `A1-04`). Afterwards `endOfPlantScene` was 1, `plantScene` 0, and she had a `LoiterProcess`.
- **First meeting.** The save has `thordisMet` 0, so I picked **How are you called?** and then **bye**.

**"Tell me about the other people.": one menu at a time.**
- **Main menu:** **Help me, I've been poisoned. / The Test was impossible! / Tell me about the other people. / bye** (`A1-06`).
- **First pick.** "My people or the others?", then the single row **Your people. • The others.** (`A1-07`). `Kernel::listProcesses` showed one `GumpNotifyProcess` (gump 3852), owned by `toldOthersConvo` (pid 1968, type 1). `use()` (pid 1948, **type 207**) was suspended on it. Wave 2 had two gumps here.
- **Your people. path.** **Your people.** → "Of me, Tyorvi, or Ragnar…" → **Ragnar • Tyorvi • You / The others.** (`A1-08`).
  - **You** → "Nothing to tell, there is. Clan Elder, I am…" (`A1-09`).
  - **Tyorvi** → "My younger brother…".
  - **Ragnar** → his line. `toldMyTribe` then read 1.
  - The next menu was **The others.** alone. Picking it ended `toldOthersConvo`, because its `if` comes earlier in the routine (1994 structure).
- **Back in `use()`.** It resumed with a single main menu (`A1-10`): one `GumpNotifyProcess`, and `use()` at a new IP.
- **The others. path.** I picked **bye**, then talked again. "What else, wish you to know?" came with **The others.** (`A1-11`), then **Ezrekal • Hrodny • Ingyald / Atli** (`A1-12`). Atli, Ingyald, Hrodny and Ezrekal each answered.
- **Then the soft-lock** (finding 1, `A1-13`, `A1-14`).

**Yes/No waits (run 2).** With `toldMyTribe` and `toldOthers` set to 1, I picked **Tell me about the other people.**
- **She asked.** "Told you of everyone, I have…" and then "Tell you again of them, I should?" were followed by **Yes. • No.**
- **Negative control.** I did not click for about 30 s. "Make up your mind" never appeared in the frames or the log, and the menu stayed up (`A1-17`).
- **Wait chain.** `listProcesses` showed `LVFREE` (pid 242, `05AE:00F9`) suspended on the `GumpNotifyProcess`. THORDIS `toldOthersConvo` (pid 180) waited on LVFREE, and `use()` (type 207) waited on that.
- **No.** "Make up your mind, you should." played (`A1-18`), and the main menu came back (`A1-19`). Both flags still read 1.
- **Yes.** After **bye** I talked again, and the Yes/No row appeared again (`A1-20`). **Yes** gave "My people or the others?" (`A1-21`).
  - Both flags now read 0, which is the reset branch.
  - The menu was **Your people. • The others.** (`A1-22`).
  - **The others.** gave one menu with Atli in it (`A1-23`). **Atli** played "The leader of the other clan…" (`A1-24`).
  - **Your people.** ended the routine, and the main menu returned.
- **After bye.** Thordis had a `LoiterProcess` and no `UCProcess`, and the Avatar walked from (12637, 29119) to (12949, 29119) (`A1-25`).

## A2: double-clicking the Avatar, PASS

Fresh world, Map 39, after the Lord British scene. The camera was centred.

- **Look click.** A single click logged the Avatar's `dumpInfo` and `calling usecode event 0 @ 0401:00B2` (`A2-01`).
- **Double-click 1** (`event 1 @ 0401:0080`). The paperdoll opened with STR/INT/DEX/ARMR/HITS/MANA/WGHT (`A2-02`). The Avatar's `f` went from `0x2441` to `0x2541`, which is `CONTAINER_GUMP_OPEN` 0x100.
- **Double-click 2.** It closed: `f` was back to `0x2441` (`A2-03`). This matches retail `use()`, which toggles.
- **Double-click 3.** It reopened (`A2-04`).
- **Double-click on the gump frame** (window 390, 140). It closed: `objectInfo 1` read `f: 0x2441` (`A2-05`).
- **Double-click 4.** It reopened (`A2-06`). Another double-click closed it.
- **Survival.** The ScummVM pid (17737) was unchanged throughout, and the session log has 0 `Segmentation`.

## A3: Atli, PASS

- **Setup.** `cp8-atli-met.sav` on Map 10, with `atliMet` 1, `testFromAtli` 1, `atliToldTest` 0 and `ingyaldMet` 0. The double-click logged `event 1 @ 046B:037B`.
- **Path.** Menu **Is there some way I may stay? / bye** (`A3-01`) → **Then I will become a Zealan.** → **Rite of Passage? / bye** → **I wish to take the test. / Tell me more of the test. / bye** (`A3-02`).
- **Tell me more of the test.** Atli answered "Very dangerous it is. Ready in your heart, mind and soul you must be. First take the Passage Stone to the southwest corner…" (`A3-03`). The next menu was **That's all? / Where is the Passage Stone? / bye** (`A3-04`), with both test options removed, as `ATLI.UNK:1660-1669` says.
- **bye** (`A3-05`, `A3-06`):
  - Atli had `LoiterProcess` 7602 and no `UCProcess`;
  - he moved from (18690, 9444) to (19150, 9444) in 4 s;
  - the Avatar walked from (18944, 9428) to (18848, 9428).
- **Negative control.** A second conversation opened normally (`A3-07`). After **bye**, he had a `LoiterProcess` again, and the Avatar walked from (18848, 9428) to (18952, 9428).
- **Warnings.** No `Non-existent`, `stuck` or `Unhandled` line in either window.

## A4: Lord British scene, PASS

- **Fresh world.** I clicked Devon's **Goodbye.** `lbDone` and `lbStarted` read 0.
- **Teleport.** Map 39 (17070, 20050, 48). The `lbSpoke` detour went to Map 0 and back (`Loading Fixed items in map 39 / 0 / 39`), and `[0405 02] = 1` (`A4-01`).
- **Walk-in.** I walked east to x 17634, north to y 19742, then west for 2.6 s: `Item: 14127 (shape 73) calling usecode event 7 @ 05AF:0080`.
  - In wave 2-a the egg was 14125. Both are lane eggs of the same class.
- **Hatch process type.** Class 0x5AF's disassembly opens `0082: push 0210h / set info / process exclude`, so the hatch runs as 0x210. I took this from the bytecode; the scene process had ended before I listed processes.
- **The scene.** The apparition spoke "Avatar, I have found a portal through which I can speak…" (`A4-02`, `A4-02b`). The camera scrolled back at about 56 s.
- **After.** `lbDone` 1 and `lbStarted` 1. The Avatar walked from (16974, 19682) to (17390, 19682) (`A4-03`), and the process list held no UCProcess.
- **Warnings.** The scene window logged no `Non-existent`, `stuck`, `Unhandled`, `Assert`, `Segment` or `Cycle` line.

## A5: Map 18 south colonnade, PASS

From `cp8` on Map 10, I teleported to Map 18. That logged `Loading Fixed items in map 18`, so the fixed items came from the new FIXED.DAT.

- **Columns.** `findShape 249` lists the colonnade at x 1536 and 4608, y 6835, 7238, 7641, 8044 and **8447**, with two shafts each. Nothing is south of 8447.
- **Plinths.** `findShape 113` lists the side plinths at x 1584 and 4656, up to **y 8495**. 8495 is the largest y of any shape 113 inside the sanctum's x range (1024-5120).
- **Clearance.** A 128-deep plinth box is y(8367, 8495], which leaves 176 clear units to the wall's y(8671, 8703].
- **Plates from inside.** At (1900, 8250, 0) (`A5-01`) and (4300, 8250, 0) (`A5-02`):
  - the south wall's outside face is plain stone;
  - each end column shows only its capital above the wall top, behind the wall;
  - no plinth face is drawn on the wall.
- **Plates from the south.** At (1700, 8950, 0) (`A5-03`) and (4500, 8950, 0) (`A5-04`), standing in the void south of the wall: the outside face is clean along its whole run, and the column tops appear behind the parapet.
- **Comparison.** Wave 1 (`docs/playtest-2026-10-07-wave1.md`, part 2, finding 2) had plinth and column painted on this face, with the pair at y 8720/8672.
- **Not done.** I did not walk-test the aisle.

## A6: log hygiene

One session, 4,178 lines (`/tmp/claude-1000/w3a/session1.log`):

| Pattern | Count | Where |
|---|---|---|
| `Non-existent process` | 4 | All `PID (0) in implies`. Line 79 is Devon's farewell (old, 10-04 finding 2). Lines 170, 171 and 173 are the AVATAR first-teleport detour on Map 0 (wave 2-a finding 4, unchanged) |
| `stuck in process loop` | 0 | |
| `Segmentation` | 0 | |
| `Assertion` | 0 | |
| `Cycle in paint` | 29 | Lines 1401-1416 and 2515-2545, `475 -> 126 -> … -> 475` and `126 -> 707 -> … -> 126`. These come from Map 10 during Thordis's conversations at the Passage Plant. They are `debugC(kDebugObject)` and print only because `debugflag_enable Object` is on (finding 3) |
| `Unhandled intrinsic` | 0 | No `Unhandled` line of any kind. Also 0 `segment 0000` and 0 `Item::combine` |

## Findings

1. **Thordis's "What else" branch soft-locks the game.** This is new with `THORDIS.UNK` change 4.
   - **Repro (run 1, organic).** After the Your people. path had set `toldMyTribe` 1:
     - talk to Thordis, then pick **Tell me about the other people.** → **The others.**;
     - pick **Atli**, **Ingyald**, **Hrodny** and **Ezrekal**, in that order;
     - Ezrekal's two lines play (`toldOthers` now reads 1). After that no menu appears, and the Avatar cannot walk (13047, 29799 unchanged after two walk bursts).
     - A double-click on the Avatar does nothing; the world click logged only a `dumpInfo`.
     - It was still frozen after more than 60 s (`A1-13`, `A1-14`).
   - **Process list:**
     ```
     Process 6384 class UCProcess, item 106, type 1, status ASD, notify: 6451, classname: THORDIS, IP: 046A:9398
     Process 6509 class GumpNotifyProcess, item 1, type 200, status AD, notify: 6384, gump: 2646
     Process 6451 class UCProcess, item 106, type 207, status ASD, classname: THORDIS, IP: 046A:40F2
     ```
     `046A:9398` is the resume point after Ezrekal's closing `tempKey = ask(tempList)`. The bytecode at 0x9385-0x9397 is `push slist [BP-0Ah]; calli 06 004A (Item::ask); push retval; implies; suspend`.
   - **Why the list is empty.** In the `toldMyTribe = true` branch, `tempList` starts as `<<"The others.">>` (`THORDIS.UNK:1873`). That entry is removed at 1945. After the fourth person, every `if not toldX` add is skipped.
   - **Engine side.** `Item::I_ask` (`world/item.cpp:3172`) returns 0 only for a null list, so an empty list builds an `AskGump` with no entries and a live notify process. Nothing can ever answer it.
   - **The routine-level waits.** `toldOthersConvo` waits on that gump. Since change 4 (`toldOthersConvo();` as a plain call), `use()` waits on `toldOthersConvo`, so `exitConvo()` never runs. Stasis persists, and the traps file notes that a game in permanent stasis is unsaveable.
   - **Under the old `spawn … -> return`** `use()` kept its own menu, and **bye** freed the Avatar. Only an orphan process would have leaked. **[INFERENCE: not played on the old build.]**
   - **Which paths hang.** Both "What else" branches end this way: `toldMyTribe` 1 with all four others told, and the mirror case with `toldOthers` 1 and You/Tyorvi/Ragnar told. The first-time "My people or the others?" branch keeps the other header in the list, so it is safe.
   - **Why a player cannot avoid it.** Each completing flag is set only inside a block, and that block's own ask is the empty one once the flag completes. Whichever flag a player completes second, they complete it on a "What else" branch. So the organic route to the yes/no question always passes through this soft-lock. That is why run 2 set the two flags with `setGlobal`.
   - **Confidence.** High on the hang and its mechanism. The fix belongs to the author. Options: skip the final `ask` when `tempList` is empty, or keep a closing entry in `tempList`.
2. **Thordis's sub-menus silently end on backward picks.** This is 1994 structure, now visible.
   - `toldOthersConvo` is a run of sequential `if tempKey = …` blocks, not a loop. Picking an entry whose block comes earlier than the current one ends the routine with no reply. For example, after the Your people. chain, **The others.** returns you to the main menu.
   - It does not hang; I hit it twice (run 1 after Ragnar, run 2 after Atli).
3. **`Cycle in paint dependency graph`, 29 lines, Map 10 Passage Plant.** The shapes are 475, 126 and 707 (707 is the Zealan NPC shape). They appeared while Thordis loitered into the plant tiles during conversations.
   - These are `debugC(kDebugObject)` lines, so a player's log never shows them. No paint glitch is visible in the plates.
   - Wave 2-a saw none in its windows; it may simply never have had Thordis inside the plant tiles. This is low severity.
4. **The parked camera returns after conversations on Map 10.** `CameraProcess::moveToAvatar` centred the camera, but after each Thordis or Atli conversation the Avatar was off-centre again (`A1-02` vs `A1-03`; the `run-s7` plates).
   - It is the same family as wave 2-a findings 2 and 5. Harness strikes needed the camera re-centred before each one.
5. **A3's claim line reference.** "ATLI.UNK:1306" does not match the patched file. The case is `lv-patched/ATLI.UNK:1639`; 1306 is presumably the recovered snapshot's numbering. The option itself was verified.

## Harness anomalies

1. The `read` tool returned "not found" for a PNG written less than a second earlier. Retrying worked.
2. The menu-pixel detector also fires on the Avatar's own red speech, such as "Well met, Thordis!" or "Is there no shred of hope?". Waits were confirmed by plate.
3. `CameraProcess::moveToAvatar` prints nothing. `con()` therefore reported "no reply" and sent it twice, which is harmless.

## Disk changes

- **Wrote** this report and the 46 plates in `docs/playtest-2026-10-07-wave2-final-a/`.
- **`session.sh start` synced** `shared/u8-lv-patched/STATIC/FIXED.DAT`, `FIXED.DAT` and `USECODE/EUSECODE.FLX` to `shared/build`'s `c3d29a1f` and `8c5a8419`.
- **Saves.** The 48 saves and `scummvm.ini` are restored, and the sorted md5 list equals the pre-session list (`RESTORED-IDENTICAL`). ScummVM had rewritten `ultima8.000`, and slot 1 held the loaded checkpoints.
- **Scratch** under `/tmp/claude-1000/w3a/`: driver copy, the session log, films, `eus_all.txt` (a full disassembly of the build) and `thordis.dis`.
- **Untouched:** no source, builder, map, fork, TODO or HANDOFF file, and no commit.
- **Session.** Stopped; ScummVM 17737 and Xvfb 17718 are killed.

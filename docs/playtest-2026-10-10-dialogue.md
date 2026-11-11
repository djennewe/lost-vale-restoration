# Dialogue near-miss fixes (`wt/atli-bang`), in-engine (2026-10-10)

**Build under test.** `main` `b1788b3` (merge of `wt/atli-bang`), plus the uncommitted `build_scummvm.sh` detection change.
- **Game copy.** `/tmp/claude-1000/vdlg/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Every hash matches `shared/build/ARTIFACTS.sha256`: EUSECODE `af5789a6…` (1,523,547 B), FIXED `511902e8…` in both places, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…` and ANIM `77e9705d…`.
- **Engine log line.** `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1523547 bytes`. That md5 is the engine's detection hash, not the md5 of the whole file.
- **Binary.** `scummvm-lv/scummvm` has mtime 2026-10-10 04:01:51. Fork `8af4f74e` is dated 03:35:20, so the binary is newer.
- **Harness.**
  - Xvfb `:97` (1280x800), with the window at (480,300).
  - `scummvm.ini` sets `frameLimit=true` and `usehighres=true`. Audio was `SDL_AUDIODRIVER=dummy`, and there was a private `saves/`.
  - The driver is the `vleft` `drv.py`/`h.py`, re-pointed to this display and directory.
  - **Menu reading.** I added a menu reader that finds AskGump option bullets by their pixel pattern (centre (213,48,49), with (189,12,8) on all four sides). Option text was read from 3× zoom crops, and barks from crops in the NPC's bark colour.
  - **Every answer was a click on a bullet found on screen.** Plates are in `docs/playtest-2026-10-10-dialogue/`.
- **Not run, on instruction:** `run_all_tests.sh`, `build_artifacts.sh`, `install_lv.sh` and `build_scummvm.sh`. The hash match stands in for them.

**The session hit the request budget after D4.** D2 and D6 were not run.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| D1 | Atli: after "How do you know it is treacherous?" the menu reads "I am from Brittania." with a period, and the pick gets "Know of this Brittania I do not. Where it is?", then the barrier / another world / not important menu. "Hrodny sent me to you." gets "Oh, she did, did she?…" and leaves the menu | **PASS**, both halves, from natural saves and organic talks (one teleport per NPC) |
| D2 | Hrodny / Ingjald / Tyorvi healed-branch options (temple opened, Ancient Ones found or freed, and Ingjald's "Shield … restored!") | **NOT DEMONSTRATED** (request budget). No talk was started |
| D3 | Thordis, testFromAtli set: "Tell me of the Test." → "I will take your Test." gets "Sure of yourself, you are…", then Yes. and No. each get their reply | **PASS**. Both Yes. and No. end the talk, as the source says |
| D4 | Ezrekal, first meeting: "The Ancient Ones are in Britannia." gets "Ah, relieves my heart…". The ball-of-fire thread's "Tell me more of the Great Cataclysm." gets the history | **PASS**. The roll was silent in **5 of 14** Cataclysm picks; see below |
| D5 | Ragnar, first meeting: "Yes, I'm peaceful." leaves the menu after its reply | **PASS** (finding 1 is a different, unfixed near-miss on the same menu) |
| D6 | Tyorvi's drunk path end to end | **NOT DEMONSTRATED** (request budget). It last passed on the 10-09 build (`playtest-2026-10-09-quirks.md` Q3) |
| D7 | Atli, atliMet 0: the "I have this shield!" option is absent with a held 828 of quality 83 and present with quality 0 | **PASS**. This was a **targeted debugger setup**, described below |
| L | Log hygiene | **PARTIAL**. 0 each of `stuck in process loop`, `Unhandled intrinsic`, Segmentation, Assertion, `Trying to access segment` and `PID (0) in implies`. **But 22,590 `Cycle in paint dependency graph` lines** (finding 2) |

**State writes.**
- **Loads.** `Ultima8Engine::loadGame 1`, each over a fresh copy of a checkpoint: `run-s1-lbdone` ×2, `run-s5-rite-granted` and `run-s9-mark-given` ×2.
- **Shield setup.** `Item::grab 764` twice, and **`Item::setQuantity 764 83`** once (D7).
- **Teleports with cheats on**, each followed by a verified `Cheats = false`. They went near Atli, Ragnar, Hrodny, Thordis and Ezrekal.
- **Other commands.** `CameraProcess::moveToAvatar` (old saves load with a parked camera) and `MainActor::toggleCombat` (`run-s9` loads in combat mode).
- **Not used:** `setGlobal`, a save, or a time skip.

## D1: Atli, PASS

**(a) "I am from Brittania."**
- **The world.** `run-s1-lbdone` (atliMet 0) with Pagan's q0 shield grabbed. I teleported to Map 10 (19400,7200,0), and the talk logged `event 1 @ 046B:0392`.
- **The menus.**
  1. **May I speak with you?** gave "What? Who are you? Strange you dress…" (`D1-02-may-i-speak-bark`).
  2. **I am not a Pagan.** gave "Hmmm, I thought not… Too treacherous the way is." (`D1-03-not-pagan-bark`).
  3. **How do you know it is treacherous?** (`D1-04-treacherous-*`) gave the menu **I am not a Hoskuld! / I am from Brittania. / Who or what are the Hoskulds? / bye**. The period is visible in the zoom (`D1-04-treacherous-menu`).
- **The pick.** **I am from Brittania.** gave **"Know of this Brittania I do not. Where it is?"** (`D1-05-from-brittania-bark`).
- **The next menu.** It read **On the other side of the barrier. / In another world. / That is not important. / bye** (`D1-05-from-brittania-menu`).
- **Repeat.** The same pick gave the same menu in the q83 world (`D7-q83-05-from-brittania-menu`).
- **Negative.** The menu no longer comes back unanswered, which is what the leftovers report saw with "!".

**(b) "Hrodny sent me to you."**
- **The world.** `run-s5-rite-granted`: atliMet 1, hrodnyMet 0, haveMark 0, not poisoned.
- **Setting hrodnyMet by play.** I talked to Hrodny (113, `event 1 @ 0471:0D5B`, `D1b-01`). **What is your name?** answered, and `getGlobal 0x45C` (hrodnyMet) read 1. Then **bye**.
- **Atli.** The talk logged `event 1 @ 046B:0392`. The menu read **Hrodny sent me to you. / Is there some way I may stay? / bye** (`D1b-04-atli-menu`).
- **The pick.** It gave **"Oh, she did, did she? Well, a meddling, blasphemer she is. Know what she told you I do not, but welcome here you are not. Leave you must...and quickly."** (`D1b-05-hrodny-sent-me-bark`).
- **The next menu.** It read **Is there some way I may stay? / She is a blasphemer? / Why must I leave? / bye**. The option left the menu (`D1b-05-hrodny-sent-me-menu`).

## D3: Thordis, PASS

**The world.** The same `run-s5-rite-granted` world after D1b (testFromAtli 1, thordisMet 0). I teleported near Thordis at (4415,7423).
1. **First talk** (`event 1 @ 046A:0ECD`). The menu was How are you called? / What is it you do? / What is this place? / bye (`D3-01`). **How are you called?** answered, thordisMet read 1, and I chose **bye**.
2. **Second talk.** The menu was **The Gunnar's say you have the Stone. / Can you direct me to the Test? / Tell me of the Test. / Tell me about the other people. / bye** (`D3-04-thordis-second-menu`).
3. **Tell me of the Test.** gave "To tell, what is? Rite of Passage, it is. Proves, worthy of being a Zealan, you are. Strong enough, you are not." (`D3-05-tell-test-bark`). The menu then gained **I will take your Test. / Not strong enough?**, and "Tell me of the Test." was gone (`D3-05-tell-test-menu`).
4. **I will take your Test.** gave **"Sure of yourself, you are. Fear failure and death, do you not?"** (`D3-06-take-test-bark`). The menu read **Yes. / No. / Not strong enough? / …**, and "I will take your Test." was gone (`D3-06-take-test-menu`).
5. **Yes.** gave **"Good, then survive it, you may. Without fear, only a fool lives…"**, and the talk ended with no menu for 15 s (`D3-07-yes-bark`, `-bark1`, `-end`).
6. **Third talk.** "Tell me of the Test." was offered again (`D3-08`). I repeated the chain (`D3-09`, `D3-10`).
7. **No.** gave **"Then survive it, you will not. Without fear, only a fool lives…"**, and the talk ended (`D3-11-no-bark`, `-end`).

**Afterwards.** A 2 s walk moved the Avatar (4665,7673) → (5373,8381). The stasis was released (`D3-12`).

## D4: Ezrekal, PASS

**The world.** `run-s9-mark-given`: ezrekalMet 0, haveMark 1, poisoned, spokeOfCataclysm 0.
- The save loads in combat mode with a parked camera. Both were cleared with `toggleCombat` and `moveToAvatar`.
- I teleported near Ezrekal's stockade, and the talk logged `event 1 @ 0474:034A`.

**(a) The Britannia thread.** Each step is a pick, followed by the menu or bark it gave:
1. **May I know your name?** (`D4-01`). The menu became Can you help me? / I am from Britannia. / What do you do? / bye (`D4-02`).
2. **I am from Britannia.** → Yes, I am from outside. / No, I am not from outside.
3. **No, I am not from outside.** → … Britannia is not in the Vale.
4. **Britannia is not in the Vale.** → The Titans are in / not in Britannia (`D4-05`).
5. **The Titans are not in Britannia.** → **The Ancient Ones are in Britannia. / The Ancient Ones are not in Britannia. / Who are the Ancient Ones?** (`D4-06-titans-not-menu`).
6. **The Ancient Ones are in Britannia.** → **"Ah, relieves my heart this news does. Perhaps in my lifetime return to us they will."** (`D4-07-ao-in-britannia-bark`). Both Ancient-Ones options then left the menu (`D4-07-…-menu`).

**(b) The ball-of-fire thread** (second load of `run-s9-mark-given`). Each step is a pick, then the menu or bark it gave:
1. **What do you do?** → **High Priestess of what?**
2. **High Priestess of what?** → **What does the High Priestess do?**
3. **What does the High Priestess do?** → How do they speak through you? / When are the special days? (`D4b-05`).
4. **When are the special days?** → Why are there no more special days? / **Ball of fire in the sky?** (`D4b-06`).
5. **Ball of fire in the sky?** → **What happened to the ball of fire?** (`D4b-07`).
6. **What happened to the ball of fire?** → "During the Great Cataclysm it was. Spoken of it have I not? The most tragic day in the history our people it is." (`D4b-08-what-happened-bark`). The menu then offered **Tell me more of the Great Cataclysm.** (`D4b-08-…-menu`).
7. **Tell me more of the Great Cataclysm.** → **"In the early days of our history, too reckless the young Zealans were becoming…"**, the cliffs/Gudbrand history, over 150 s of pages (`D4b-09-cataclysm-ball-of-fire-bark`).

**The silent roll, counted.** The not-shieldFixed branch rolls `urandom(3)`, and only 1 and 2 bark.
- **Classifying a pick.** A pick counts as **silent** when the menu went away, no green text appeared within 12 s, and no menu came back. If the pick had missed, the menu would have stayed. Silent picks end the talk, as the source's `exitConvo` says.
- **The samples.** There were 14 picks in total:
  - 1 from the "Why have you been away from your people?" in-conversation add (`D4-09`);
  - 12 from the top-level add on re-talks (`D4-10-retalk-1-menu` shows it first in the menu);
  - 1 from the ball-of-fire thread.
- **The result.** 5 picks were silent and 9 told a story. Of the 9, 5 were "In the early days…" (`D4-11-…-12-bark`) and 4 were "Shortly after the Shield of the Ancients was lost, a terrible plague…" (`D4-11-…-13-bark`).
- **Reading.** 5/14 is consistent with 1 in 3. This is the known, unchanged quirk named in EZREKAL's M2 header.

## D5: Ragnar, PASS

**The world.** `run-s5-rite-granted`: ragnarMet 0, thordisMet 0. I teleported near Ragnar's hut, and the talk logged `event 1 @ 0469:0237`.
1. **What do you do here?** gave "Do here? Hard to understand you are… When find it I can." (`D5-02`). See finding 1 for the menu.
2. **What is your name?** gave "Ragnar called I am…". The menu gained **From very far away. / I am new to your land.** (`D5-03`).
3. **From very far away.** gave "Know that I do! Never seen anything like you I have. Come in peace do you?" (`D5-04-far-away-bark`). The menu gained **Yes, I'm peaceful. / Leave me alone.** (`D5-04-…-menu`).
4. **Yes, I'm peaceful.** gave **"Peacful you are, but peaceful with Gunnar clan? If peaceful with Gunnar clan you are, then at war with Huskold clan you are."** (`D5-05-peaceful-bark`).
   - **The next menu:** What do you do here? / When you can find game? / I am new to your land. / Leave me alone. / **I am peaceful with all. / I have no fight with you.** / Farewell. (`D5-05-peaceful-menu`).
   - **"Yes, I'm peaceful." is gone.**
5. **Farewell.** ended the talk. ragnarMet then read 1 and thordisMet 0.

## D7: Atli's shield option with q83 vs q0, PASS (a targeted check, set up with the debugger)

**What I changed.** No natural save carries the restored Shield with atliMet 0. I set it up as follows:
- Loaded `run-s1-lbdone` (atliMet 0).
- Ran `Item::grab 764`. That is Pagan's 828 (`(1090,1678,64) q: 0`), and weight went 20 → 50.
- **For the q83 world only,** ran `Item::setQuantity 764 83`. The fork's command writes `Item::setQuality`, and it printed `setQuantity: 764 now 83`.
  - Afterwards `findShape 828` read `Item 764 (class Item, shape 828) (uc: AORTA), 0, (0, 0) q: 83 …` in the pack.
  - That is the same shape, frame and container as the real restored Shield. Only the quality differs from the q0 world.
- Teleported to Map 10 near Atli.

**Same path in both worlds.** May I speak with you? → I am not a Pagan. → How do you know it is treacherous? → I am from Brittania. → That is not important. → I am not a Hoskuld! → "Prove it!"

| World | Menu after "Prove it!" |
|---|---|
| q0 (`D7-q0-01-not-hoskuld-menu`) | **I have this shield!** / You will have to trust me. / bye. The pick gave "Where get that did you? Looks it does much like the stories say the Shield-Which-Was-Broken looked! A wonderous item you have! Perhaps from the other…" (`D7-q0-02-have-shield-bark`) and left the menu |
| q83 (`D7-q83-07-not-hoskuld-menu`, bark `-bark` "Prove it!") | You will have to trust me. / bye. **No shield option** |

**After the q83 talk,** item 764 was still in the pack at q 83.

## D2 and D6: NOT DEMONSTRATED

The request budget ran out after D4.
- **D2's worlds are identified.** Copy each save, then talk to the NPC:

  | Save | atliMet | hrodnyMet | ingyaldMet | tyorviMet | ezrekalMet | haveMark | poisoned | shieldFixed | templeOpen | godsFree | iAmDrunk | givenTea |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | `vqb/sp/q1-pre-altar.sav` | 1 | 1 | **0** | 1 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 1 |
  | `vqb/sp/q1-gods-free.sav` | 1 | 1 | **0** | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 1 |

  - **Ingjald is unmet in the q1 saves,** so he needs one first-meeting talk before his healed branch appears.
  - **For Ingjald's "restored!"** (templeOpen 0), `cp25-hrodny-key` / `cp30-altar-ready` have ingyaldMet 1, cured, shieldFixed 1 and templeOpen 0.
- **For D6** use `run-s11-tyorvi-key`, or the 10-09 `vquirks/sp/q3-pre-drink.sav`.

## Findings outside the brief

1. **Ragnar's first-meeting "What do you do here?" never leaves the menu.**
   - **What the source does.** The case (`lv-patched/RAGNAR.UNK:318`) removes `"What do you do?"` (no "here"), so the answered option stays.
   - **In the engine** it stayed through every later menu (`D5-02` … `D5-05` menus).
   - **Effect.** The answer is harmless, but it is the same family as the near-misses this change fixed.
   - **Not listed.** It is not among RAGNAR change 14's three, and I did not check whether D19b pins it.
2. **22,590 `Cycle in paint dependency graph` warnings.**
   - **The pairs.** 13,554 are `426 -> 856 -> … -> 426` and 9,036 are `426 -> 208 -> … -> 426`.
   - **Where.** They sit in log lines 998-23676. That window opens with the teleport to Thordis's village at (4665,7673) on Map 10, and it also spans Thordis's talks and the first Ezrekal session. They stop before the second `run-s9` load.
   - **Not established.** I did not identify objects 426/208/856. This is a sort-order cycle among world items, a render-order issue, not usecode. Earlier reports counted 0, but their sessions did not stand in Hoskuld [INFERENCE].
   - **Next step.** Worth an `objectInfo 426` / `208` / `856` from the same spot.
3. **The ATLI case's own removal `"Iam from Brittania."` is inert, as the inventory says.** The next statement replaced the whole list, and nothing was stranded (`D1-05` menu).
4. **During Ezrekal's conversations the camera centres on her** and returns to the Avatar after the talk ends (`D4-11-…-bark`, `D4-12`). This is noted only because it made avatar-centred strikes miss while a long history bark was still playing. That is a harness effect, not a defect.
5. **`run-s9-mark-given` loads in combat mode** (`flags c00`) with a parked camera, and `run-s5`/`run-s1` load with a parked camera. All of them predate `f9a9aba`.
   - **Repeated after the jump.** `run-s9`'s camera parked again after the first teleport (Avatar `f: 0x41`, no fast area) until a second `moveToAvatar`.

## Harness anomalies

1. **A pack gump and the minimap opened** from leaked keystrokes after a `moveToAvatar`. I closed the pack with a double-click on its frame. The minimap stayed open in the corner of some plates.
2. **The bullet detector misses a bullet under the mouse cursor.** The pick routine now parks the cursor at the window corner after every click.
3. **`objectInfo` of an NPC on a map that is not loaded prints `No such object`,** which the driver's regex treated as a timeout.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-10-dialogue/`, 134 plates (D1-*, D1b-*, D3-*, D4-*, D4b-*, D5-*, D7-q0-*, D7-q83-*).
- **Scratch** in `/tmp/claude-1000/vdlg/`:
  - `game/`, `scummvm.ini`, `run.sh` and `lv_run.log` (25,483 lines);
  - `saves/` (`ultima8.001` is a copy of `run-s9-mark-given`);
  - `sp/`, `py/`, `fl.py`, `flags.py` and `savinfo.py`.
- **Stopped:** my ScummVM and Xvfb `:97`.
- **Not touched:** source, builders, maps, the fork, `shared/`, `TODO.md`, `HANDOFF.md`, `~/lv-checkpoints` (nothing banked) and `vqb/`.

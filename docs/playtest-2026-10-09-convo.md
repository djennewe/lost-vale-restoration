# Conversation bracket: retail enterConvo/exitConvo in every LV NPC (2026-10-09)

**Build under test.** `main` at `f3d83af`, plus the uncommitted `ARTIFACTS.sha256` and `build_scummvm.sh`.
- The log reads `usecode/eusecode.flx: 2619303567614e4576432b19b0797332, 1525855 bytes`.
- The game copy `/tmp/claude-1000/vconvo/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Its sha256 values match `shared/build/ARTIFACTS.sha256`: EUSECODE `760d631e592d…`, U8SHAPES `69fbd86123e8…`, TYPEFLAG `6bdb303654a5…`, ANIM `77e9705da254…`, and FIXED `9fbe86da9083…` in both places.
- The fork is `4ccd3fe7`. `scummvm-lv/scummvm` is dated Oct 9 20:29.
- **Harness.** Xvfb `:89` (1280x800), with the window at (480,300) and my own `scummvm.ini` and save directory. The driver is the `vfin` `drv.py`/`h.py`, re-pointed.
- **Session 1** (`lv_run.s1.log`) ran with `frameLimit=false`, which leaves the game running unthrottled; see harness anomaly 1. **Session 2** (`lv_run.log`) ran with `frameLimit=true`.
- Plates are in `docs/playtest-2026-10-09-convo/`.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| C1 | After Aramina's farewell her ARAMINA UCProcess (type 205, `040D:04B8`) runs again, not a LoiterProcess, and she keeps visiting her markers | **PASS** |
| C2 | All eight Vale NPCs get their activity back after talk + bye. Avatar stasis is false and nobody is frozen | **PASS** for the normal farewell (8/8 NPCs). See **finding 1**: the invisible-Avatar abort leaves the NPC with no activity |
| C3 | 0x0F reads 1 during every talk and 0 after the farewell | **PASS**: 0 after every farewell (15/15 read). The "during" reading proves something only on talks that started at 0. See **finding 2** (old saves load with 0x0F=1) |
| C4 | At talk start the camera centres on the NPC and both turn to face. At talk end it scrolls back to the Avatar. Mythran scrolls back once | **PASS** for the LV Vale and Tenebrae NPCs. **Mythran: NOT DEMONSTRATED** (out of budget) |
| C5 | The scene exceptions do not break the scenes | **PARTIAL**. The Passage Test end **PASS**. The Sacred Circle ceremony (run-s13) was **NOT DEMONSTRATED**. The plantScene stand-still branch was **not reached** (see C5) |
| C6 | Talking while invisible gives the "Hello...?" family and no menu. No NPC is left with 0x0F stuck at 1 | The bark and no-menu part **PASS**. **Defect: Hrodny is left frozen** (finding 1). 0x0F part **PASS** |
| C7 | The quest-critical dialogues still work end to end | **PARTIAL**. Ragnar's bag chain **PASS**. Thordis's Passage Test **PASS**. Ezrekal root→patience→walk-away→elixir (868) **PASS**. Tyorvi's drink→Key was **NOT COMPLETED** (the drunk roll ended the talk and the budget ran out). Hrodny's temple talk was **NOT DEMONSTRATED** |
| L | Log hygiene, and exactly one `Non-existent process PID (0) in implies` per farewell | **PASS**. 0 `Unhandled intrinsic`, process-loop, Segmentation, Assertion or segment-access lines. The implies count is exactly 1 per conversation end, 18/18. One of those 18 is the **invisible abort**, which is not a farewell |
| — | `run_all_tests.sh`, `build_artifacts.sh`, patch-equals-fork | **SKIPPED** on instruction (already run). The sha256 match above stands in for the build |

**State writes.** I used teleports with cheats on, each followed by a verified `Cheats = false`. Other writes were `debugflag_enable Object`, `CameraProcess::moveToAvatar` (once, on the parked-camera `cp21-root` save), `Item::grab` of the invisibility potion (C6), and `toggleAvatarInStasis` twice per read (a net no-op). There was no `setGlobal`. Every answer and every talk was clicked on screen.

## C1: Aramina, PASS

**Setup.** I loaded `cp2-palace.sav` (0x0F=0), teleported to m41 (16860,16260,48) and turned cheats off.

**Before the talk.** The process list was `Process 99 class UCProcess, item 13, type 205, … ARAMINA, IP: 040D:04B8`, plus a PathfinderProcess.

**Talk 1.**
- The double-click logged `event 1 @ 040D:10E9`.
- The camera scrolled over about two frames to centre on her (`C1-sheet-talk-start`, `C1-02-camera-on-aramina`). In the zooms, the Avatar faces up-right toward her and she faces down-left toward him.
- The menu was **By what are you called? / bye** (`C1-01-talk-menu`). It is drawn at the Avatar's screen position, which is now off-centre and partly clipped at the left edge; see finding 5.
- During the talk: `0x0F = 1`, with `Process 10 … type 207, ARAMINA, IP: 040D:15D1` and a GumpNotifyProcess.
- I picked **bye**. The camera scrolled back to the Avatar (`C1-sheet-bye`, `C1-04-camera-back-on-avatar`).
- Then: **`Process 126 class UCProcess, item 13, type 205, ARAMINA, IP: 040D:04B8`**, a PathfinderProcess, no LoiterProcess, and 0x0F 0. Stasis read false, and a walk burst moved the Avatar 464 units.
- The log shows exactly one `Non-existent process PID (0)` line. It also shows one `popToContainer to invalid container (73)` with `Destroying orphaned ethereal object` (shape 174), the known m41 family. It fired when the camera came back.

**The route afterwards.** Over 70 s she read (16491,15908), next to marker f5 (16479,15903), and (17128,15525), next to f3 (17172,15444), among others. She stayed on z 48. She logged **no event 16 (leaveFastArea)** after the talk.

**Talk 2 (a different exitConvo site).** The path was **By what are you called? → What do you do here? menu → bye** (`C1-05`).
- Afterwards: `Process 121 class UCProcess, item 13, type 205, ARAMINA, IP: 040D:04B8`, 0x0F 0, and one implies line.

**Negative control.** Under the old codegen, finding 3 of `playtest-2026-10-09-final` saw only a LoiterProcess after a talk. That did not happen on either farewell.

## C2 / C3 / C4: the Vale NPCs, PASS (normal farewell)

**Setup.** I loaded `cp7c-ragnar-referral.sav` (native scheduler, h2 bloodwatch). I teleported near each NPC, and walked where possible. Each NPC was talked to by double-click and dismissed with its on-screen bye or Farewell. After each farewell I read the process list, 0x0F, stasis twice and the positions.

| NPC | Talk event | After the farewell | 0x0F after | Stasis |
|---|---|---|---|---|
| Ragnar 105 | `0469:0237` | new LoiterProcess 3844, walking | 0 | false |
| Thordis 106 | `046A:0E71` | new LoiterProcess 3147 (was 2218); moved (4598,7414)→(4598,7786) | 0 | false |
| Sigrid 102 | `0466:0231` | new LoiterProcess 2346, walking | 0 | false |
| Tyorvi 115 | `0473:0354` | new LoiterProcess 1058 (was 1534) | 0 | false |
| Hrodny 113 | `0471:0D5B` | **1 s after: `UCProcess, item 113, type 205, HRODNY, IP: 0471:0609`** (randomBarkAtHome) with an ActorBarkNotifyProcess, plus new LoiterProcess 2480. Later: the LoiterProcess only | 0 | false |
| Ingjald 112 | `0470:0934` | new LoiterProcess 2711 (was 2934). No bark UCProcess was caught at 1 s | 0 | false |
| Atli 107 | `046B:0392` | new LoiterProcess 3550 | 0 | false |
| Ezrekal 116 | `0474:034A` (the no-Mark "A PAGAN!!" refusal path) | LoiterProcess 1647, walking | 0 | false |

- **0x0F during the talk read 1 every time** (Ragnar, Thordis, Sigrid, Tyorvi, Hrodny, Ingjald, Atli, Ezrekal). From Thordis on, each talk started at 0, so those readings prove the set.
- **Camera.** Each talk start shows the NPC at the centre of the screen (`C2-*-01-talk`). Each farewell shows the camera back on the Avatar (`C4-ragnar-bye-sheet` frames 4-7, `C4-sigrid-sheet`, `C4-thordis-sheet`, `C4-tyorvi-sheet`).
- **Ingjald and Hrodny's bark processes.** These are one-shot `[[PT_ACTIVITY]]` processes (`lv-patched/HRODNY.UNK`, `THORDIS.UNK` `randomBarkAtHome`). They return at once when no case rolls. One was caught live for Hrodny; Ingjald's was not caught. Each class handler visibly ran, because every NPC got a **new** LoiterProcess PID.
- **The recreated-scheduler save.** `cp21-root` (a native scheduler) gave the Ezrekal and Tyorvi talks in C7. No `sched=False` save was loaded in this session, so "with the scheduler recreated" is untested here.

## C5: scene exceptions, PARTIAL

**The Passage Test end, PASS.**
- **Before.** `cp10-test-done.sav` had plantScene 1, endOfPlantScene 0 and thordisToldTest 0. Thordis was on the plateau (13103,29519,64) under a LoiterProcess.
- **The talk.** It logged `event 1 @ 046A:0E71`. The aftermath barks played at real-time speed, ending with "Sad to say it I am. But give you the Zealan Mark I will…" (`C7-thordis-02-mark-line`).
- **During.** `Process 6073 … type 207, THORDIS, IP: 046A:1308`, with stasis true.
- **After.** plantScene **0**, endOfPlantScene **1**, 0x0F **0** and stasis false. Thordis had a new LoiterProcess 5180, and there was one implies line.
- **The camera** went back to the Avatar (`C7-thordis-03-scene-end-sheet` frame 2).
- **Position.** She read (13223,29763,64), (13043,29643,64) and (13283,29403,72). She stayed on the plateau and did not fall.

**The plantScene stand-still branch.** This is `Thordis::enterFastArea`'s `if plantScene = true return`. **It was not reached.** The aftermath clears plantScene *before* `exitConvo()` (`lv-patched/THORDIS.UNK:678-683`), so the spawned handler takes the loiter branch.
- The branch is reachable only when thordisToldTest is 1, that is, when Atli is the witness and Thordis is talked to elsewhere while plantScene is 1. No checkpoint has that state.
- **[INFERENCE]** On that path she would stand still until the self-heal or the next fast-area entry.

**Sacred Circle ceremony (run-s13): NOT DEMONSTRATED.** The request budget ran out first.

## C6: invisible Avatar, bark PASS, NPC left frozen (defect)

**Setup.** The frame-7 potion (859 f7 at (21280,8832)) is not in any checkpoint's Map 10 state. A Map 11 → 10 hop loaded it (`findShape 859` gave 7 records after the hop, against 5 before). The potion was `Item::grab`bed and drunk from the pack beside Hrodny (`event 1 @ 04E5:00A9`). The Avatar's flags went 0x2441 → **0x2455** (INVISIBLE|OWNED).

**The talk.**
- The double-click on Hrodny logged `event 1 @ 0471:0D5B`. Hrodny barked **"Is someone there...?"**. The Avatar is drawn ghosted, and **no menu** opened (`C6-04-invisible-barks`).
- The camera did not move, and 0x0F was untouched: it read 1 before and after, because this save carries a stuck 1 (finding 2). The Avatar was still invisible afterwards (0x2455).

**The defect.** Afterwards Hrodny had **no processes at all**. She read `(21539,8503)` three times over 34 s with an empty `listProcesses` result.
- When I teleported 4,000 units away and back, she logged `event 16 @ 0471:033F` then `event 15 @ 0471:02C4`, and **then** `LoiterProcess 14074`.
- See finding 1 for the cause.

**No menu while invisible.** This held. In session 1, under `frameLimit=false`, the potion wore off before the strike landed (finding 3), and that talk got the normal menu as it should.

## C7: quest-critical dialogues, PARTIAL

- **Ragnar's bag chain, PASS.**
  - **The path, picked from the screen.** Atli sent me to you. → Atli admires you. → I believe that he is sincere. → He spoke of you and Hrodny. → He said you could help me. → Do you know of the Passage Stone? → Yes, I do. → Why do you not go there?
  - **The bag.** He told the bag story (`C7-ragnar-02-bag-line`). ragnarToldStone went to **1**, and `findShape 637` gave `Item 2495 (class Container, shape 637) (uc: BAG), (16447, 25727, 64)`.
  - **The menu** came back without the "why" option (`C7-ragnar-03`). The Farewell is in the C2 table.
- **Thordis's Passage Test, PASS** (see C5).
- **Ezrekal root → patience → elixir, PASS** (`cp21-root.sav`, root 399 f9 in the pack; the parked camera was fixed with `moveToAvatar`).
  - **The handover.** The menu was **I have found the root. / Can you help me? / bye**. Picking the root gave givenRoot 1 and justGotRoot 1, and the root left the pack.
  - **Ready 1.** The menu was **Can you help me? / Is Tyorvi's elixir ready yet? / bye**. "Ready yet?" gave **"Ah, always in a hurry the young are. No, ready it is not."**, and the talk ended (`C7-ezrekal-02`).
  - **Ready 2.** Asked again, it gave **"Patience, my friend, patience. Time these things take."** (`C7-ezrekal-03`), so it answers both times.
  - **The walk-away.** I walked out of the stockade to (14624,14256). The log shows `event 16 @ 0474:0264`, and justGotRoot went to **0**.
  - **The elixir.** Back at her, **Have you made the elixir?** gave "Yes, I have. Take it to him now you can." (`C7-ezrekal-04`). givenElixir and hasTea went to 1, and the pack holds **`Item 12166 (class Item, shape 868) (uc: TYPEELIX), 0`**. There is no shape-395 item on the map.
  - Every one of these farewells ended with LoiterProcess, 0x0F 0 and one implies line.
- **Tyorvi drink → Key, NOT COMPLETED.**
  - Tyorvi was at the stash (22031,7999). **I have something for you from Ezrekal.** was offered, and he was drunk ("-hic-").
  - **The path.** It is an elixar. → It is a potion. → It will heal your dreams. Then the menu offered **It might work! / Just try it, please. / Shut up and drink it! / bye**.
  - **The end.** I picked "Just try it, please." That ended the talk: givenTea 0, and the camera went back to the Avatar. The route guide's drunk path needs "Are you OK, Tyorvi?" first, so this is consistent with the drunk roll, not a defect.
  - The budget ran out before a retry. The 868 elixir was offered as the "something" option, so the TYORVI filter does see shape 868.
- **Hrodny's temple talk: NOT DEMONSTRATED** (the budget ran out).

## L: log hygiene

| Log | Lines | Unhandled intrinsic | Process loop | Segmentation / Assertion | Segment access | `Non-existent process PID (0)` | `popToContainer` | `Cycle in paint` |
|---|---|---|---|---|---|---|---|---|
| `lv_run.s1.log` | 39,024 | 0 | 0 | 0 / 0 | 0 | **12** = 12 conversation ends | 2 (m41, shape 174, known) | 28,438 (Map 10, known family) |
| `lv_run.log` | 26,240 | 0 | 0 | 0 / 0 | 0 | **6** = 5 conversation ends + 1 invisible abort | 0 | 23,838 |

In session 1, each `event 1` for an LV NPC is followed by exactly one implies warning before the next talk: the line pairs run from 2807/3584 to 38088/38106.

## Findings

1. **The invisible-Avatar abort leaves an LV NPC with no activity until it leaves and re-enters the fast area.**
   - **The retail path.** Retail enterConvo (`METHOD 057C:0BCF`) kills the NPC's 0x205/0x200/0xF0/0x204 processes. On the invisible path (`0CB3` → `0D7C-0DB8`) it barks, calls `Item::enterFastArea` (0x67), then calls `0581:2A56(0x207)`, which ends the calling conversation process.
   - **Why nothing restarts her.** ScummVM's `Item::enterFastArea()` calls the usecode event only when `FLG_FASTAREA` is clear (`world/item.cpp:1888`), so here it does nothing. The compiler's added `spawn <class>::enterFastArea` sits after the `exitConvo` spawn, and on this path it is never reached.
   - **Evidence.** Hrodny had an empty process list and stood still for 34 s or more. She recovered only on `event 16` then `event 15`.
   - **Scope.** Under ScummVM, retail NPCs share this. It is new for LV, because the old bracket had no invisible abort.
   - **Fix direction** [INFERENCE]. Either have the fork's `I_enterFastArea` re-run the event for an NPC with no activity, or spawn the class handler from the LV use() before the abort can kill it.
   - Confidence: high on the mechanism.
2. **Every Map-8-onward checkpoint (cp3n+, run-s3+, all `cp5`-`cp34`, `bag-q1-*`) loads with global 0x0F = 1.** Saves before that, and `cp2-palace`, read 0.
   - **Consequence.** The first LV farewell on this build clears it, because retail exitConvo writes 0. On those saves a "during the talk = 1" reading proves nothing.
   - **Likely source** [INFERENCE]. The only non-METHOD writers are retail PESANT1 (`02C3:0234-0288`), GUARDMAN (`023E`), DARION, RHIAN and CALGUARD. Each sets 1, barks, then sets 0, so a process killed mid-bark leaves 1. On an affected save, retail barks that check 0x0F stay muted until the first LV farewell.
3. **`frameLimit=false` (the 10-09 harness setting) runs the game unthrottled.** `ultima8.cpp:624-631` runs `TICKS_PER_FRAME` ticks every loop with no wait. Timed effects expire within seconds: the invisibility potion's 1800 ticks ran out before a strike landed, conversation barks flash by, and NPCs cover hundreds of units between reads. Use `frameLimit=true` for anything timed.
4. **Old checkpoints carry the parked camera** (`cp21-root`; the 09-25 trap). After a teleport the view stayed on the Sacred Circle. `CameraProcess::moveToAvatar` recovered it.
5. **With the camera on the NPC, the ask menu is drawn at the Avatar's screen position.** When the Avatar is far off-centre it is clipped: Aramina's "By what are you called?" sat at x≈0 (`C1-01`). This is retail AskGump behaviour; it is noted for players.
6. **The elixir 868 reports `q: 0` in objectInfo**, not quantity 1. It is a non-stacking SF_GENERIC item, so this is probably moot [INFERENCE]. TYORVI still offered "something from Ezrekal".

## Harness anomalies

1. Session 1 ran unthrottled (finding 3). I restarted with `frameLimit=true` for session 2.
2. Strikes on wandering NPCs needed several tries. Two console round-trips take about 4 s, so I read the position once and clicked at once. For Aramina, a grey-dress pixel match worked.
3. `goto` stalled against Gunnar huts and inside Ezrekal's stockade. The probe freed it.

## Disk changes

- **Wrote** this report and 35 plates in `docs/playtest-2026-10-09-convo/`.
- **Scratch** in `/tmp/claude-1000/vconvo/`: `game/`, `scummvm.ini` (now `frameLimit=true`), `run.sh`, `saves/ultima8.001` (a copy of `cp21-root`, played on), `lv_run.s1.log`, `lv_run.log`, `sp/`, `py/`, `dis/` (disassemblies), and `flags.py`.
- **Stopped:** my ScummVM and Xvfb `:89`.
- **Not touched:** source, builders, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and `~/lv-checkpoints` (read-only).

# Compiler wave 2 (c89bf07..a2aaf16), instance A, verified in engine (2026-10-07)

Change under test: the wave-2 compiler commits on `main`. Artifacts: EUSECODE
`13ccb939` (md5-5000 `dbce2958`, 1,524,536 bytes), FIXED `14774b0b`. Both
session logs read `usecode/eusecode.flx: dbce29589ae46b798dc8056c84dddcd3,
1524536 bytes` and `Running Ultima VIII: Pagan (Gold Edition + Lost
Vale/DOS/English)`. I used the standard harness on display :77. Plates are in
`docs/playtest-2026-10-07-wave2-a/` at 640x400.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| A1 | Lord British scene at Tenebrae, from a fresh world | **PASS**: walked into the egg; `lbDone` 1; the puppet ended on its `setFrame(9)` path; Mythran opened his `lbDone` branch |
| A2 | Passage Test from `run-s7` | **PASS** on MINIAIR, the four flags, the stone, the stasis release and 0 `combine`/`segment 0000`. **FAIL** on "poison damage ticks continue": no code deals poison damage (finding 3) |
| A3a | Thordis "Tell me about the other people." | **FAIL**: two ask menus are on screen at once and overlap (rule 5) |
| A3b | Thordis yes/no (`askYesNo`, THORDIS.UNK:1879) | **FAIL**: the answer is taken before the player clicks. "Make up your mind, you should." plays while Yes/No is still on screen |
| A4 | Atli "Tell me more of the Test", exit leaves him loitering | **NOT DEMONSTRATED**: ran out of request budget |
| A5 | Log hygiene | **FAIL**: 1 Segmentation fault (finding 1, which predates wave 2); 4 `Non-existent process PID (0) in implies`, 3 of them new on the Map 0 detour (finding 4) |

## Method and harness writes

- I backed up 48 saves and `scummvm.ini` (md5 list) to `/tmp/claude-1000/w2a/bak/`.
- `session.sh start` synced `USECODE/EUSECODE.FLX`, which was stale at `3943f176`.
- Session 1 started from a fresh world, then loaded `run-s7-ragnar-stone.sav`. It ended in a segfault. Session 2 loaded `run-s7` again.
- Game-state writes:
  - teleports with cheats on, each followed by a toggle back to off;
  - `Item::grab 15048`, twice;
  - `CameraProcess::moveToAvatar`;
  - `toggleAvatarInStasis`, used in pairs to read the state;
  - `debugflag_enable Object` and `traceClass` on 1025, 1443, 1455, 1434 and 0x46A;
  - `Ultima8Engine::saveGame` into slot 1 (restored afterwards);
  - `UCMachine::setGlobal 0x455 1 1` and `0x456 1 1` (`toldMyTribe`, `toldOthers`), to reach `askYesNo`.
- I clicked every menu answer from the screen. I walked into both scene eggs; I did not teleport onto them.

## A1: Lord British scene, PASS

- **Fresh world.** I clicked Devon's **Goodbye** and waited out the farewell. Stasis then read false.
- **Teleport to the lane.** Map 39 (17070, 20050, 48), outside the egg box. The `lbSpoke` detour took the Avatar to Map 0 and back (`Loading Fixed items in map 0`, then map 39). `lbSpoke` read 1, `lbStarted` 0 and `lbDone` 0 (`A1-01`).
- **Walk into the egg.** I walked east, north at x 17650, then west into egg 14125 (17150, 19700, box ±128): `Item: 14125 (shape 73) calling usecode event 7 @ 05AF:0080` (`A1-02`, `A1-03`).
- **Apparition.** It animated (`A1-04`). The puppet (process 411, class 1443) looped at offsets 1800/1932/1947 until `use()` set `lbDone` at tick 18774. At tick 18782 it ran offset 1800 (0x708) with no continuation.
  - 0x708 is `push global 06A6; push 1; cmp; jne; push byte 9; … setFrame; jmp end`, so the puppet ended on its `setFrame(9)` path.
  - The last plate before removal shows the dark, side-facing pose of frames 7-12 (`A1-05`). Gone at the next plate (`A1-06`).
  - I took the frame from the bytecode path, not from a `findShape` read.
- **After the scene.** `lbDone` 1, `lbStarted` 1, and the Avatar walked from (17254, 19818) to (17670, 19818).
- **Mythran (Map 8, NPC 33).** The double-click logged `event 1 @ 0421:A125`, and he barked "Ah. So the message has arrived at last…" (`A1-08`). The menu offered **Tell me of this ancient race. / Lord British says they can help me. / Let us speak of other matters. / Farewell** (`A1-09`). After **Farewell** came "Go carefully, my friend…". Stasis then read false, Mythran had a `LoiterProcess`, and the Avatar walked.
- **Negative control.** Before the walk-in, the detour ran with `lbStarted` 0 and went to Map 0. It did not kill a scene.

## A2: Passage Test, PASS except poison damage

The setup was `run-s7`, `Item::grab 15048` (weight 30→40), a teleport to Map 10 (12800, 29720, 64), `moveToAvatar`, and a 1.6 s walk north. That logged `event 7 @ 059A:0080`. I ran it twice.

- **Run 1 (hands-off film).** The trace shows ten 10-step loops: five winds × (0..9, 25..34). The scene process ended on its own.
- **Run 2.** `findShape 481` at 12 s read `Item 5705 (shape 481) (uc: MINIAIR), 4, (12745, 29673, 64)`. At 26 s it read `Item 3692 … (uc: MINIAIR), 30, (12777, 29577, 64)`, and at 40 s it read 0 (`A2-05-run2-whirlwind-12s/26s`).
- **Both runs after the scene:**
  - `avatarPoisoned`, `haveMark`, `plantScene` and `firstPoisoned` all read 1.
  - Weight was 30, and `findShape 798` found only the Map 0 copy (13751), so the stone was consumed.
  - Thordis had no process.
  - Stasis read false, and the Avatar walked from (13055, 30079) to (12855, 30079) (`A2-03`, `A2-06`).
- **Warnings.** Each run window logged 0 `Item::combine`, 0 `segment 0000`, 0 `Unhandled`, 0 `stuck` and 0 `Cycle in paint`. This confirms rule 6's claim.
- **Poison damage: FAIL as claimed.** HP read 30 at four reads 20-25 s apart, with `avatarPoisoned` 1. See finding 3.

## A3: Thordis, FAIL (two defects)

Session 2, after run 2. The double-click logged `event 1 @ 046A:0E43`. The scene-end conversation played through to "Leave you alone now I will." (`A3-05`; session 1 `A3-02`). Afterwards `endOfPlantScene` was 1, `plantScene` 0, stasis false, and she had a `LoiterProcess`.

The save has `thordisMet` 0. So I picked **How are you called?**, then **bye**, and talked to her again. The menu was **Help me, I've been poisoned! / The Test was impossible! / Tell me about the other people. / bye** (`A3-06`).

**"Tell me about the other people."** "My people or the others?" appears. Then **two ask menus are open at once**. `Kernel::listProcesses` shows two `GumpNotifyProcess` (gumps 827 and 2988), owned by `toldOthersConvo` (process 6932, type 1) and by `use()` (process 6943, type 0x209). The second menu's **Your people. / The others.** row is drawn over the first menu's **bye** row (`A3-08`, `A3-08b`).

- Picking **The others.** gave "Of Atli, Ingyald, Hrodny or Ezrekal…". The next menu overlapped two rows: `Ezrekal * Hrodny * Ingyald` over "The Test was impossible!", and `Atli * Your people.` over "bye" (`A3-09`, `A3-09b`).
- Picking **Atli** played his line. Picking **Your people.** ended `toldOthersConvo`, and the main menu was left alone.
- **Cause: rule 5.** THORDIS.UNK:1181 `spawn toldOthersConvo() -> return;` no longer makes `use()` wait, so `use()` loops straight back to `answer = ask(askList)`. Confidence: high. The process list shows both asks live.

**askYesNo.** With `toldMyTribe` and `toldOthers` set to 1, I picked **Tell me about the other people.** again.

- She said "Told you of everyone, I have. No others, there are." and then "Tell you again of them, I should?".
- **Yes. / No.** appeared, to the right of the main menu's **bye**. Then, with no click, she said "**Make up your mind, you should.**" (the `reply != true` branch). The Yes/No row stayed on screen (`A3yn` plates: `A3-11-yesno-not-waited.png`).
- In the trace, the caller's spawn of `05AE:00CB` and the resume at 0x847E (`push process result`) happen on the same tick, 1370412.
- **Cause: LVFREE `askYesNo` (0x5AE:0x00CB).** `key = Avatar.ask(keyList)` compiles to `calli 06 004A` followed directly by `push retval`, with no `implies`/`suspend`. So `key` is the ask's pid, not its answer. Neither strcmp matches, the result is -1, and the caller reads "not yes".
  - Retail and the THORDIS sites wait on `ask`; this assigned form does not.
  - Rule 3 covers process intrinsics used as statements only. A process intrinsic used as a value inside an assignment is not waited on.
  - The caller side is rule 2's new spawn-and-wait, and it works: it receives the routine's return value. The defect is inside the routine.
  - I did not compile the pre-wave-2 tree for this function, so I have not established whether it is new. Before wave 2 the caller read a stale retval, so the symptom would have differed. Confidence that the bytes cause what I saw: high.

## A4: Atli, NOT DEMONSTRATED

Not run. The session hit its request budget after A3.

## A5: log hygiene

| Session | Lines | Non-existent PID (0) | stuck | Segmentation | Assertion | Cycle in paint | Unhandled |
|---|---|---|---|---|---|---|---|
| 1 (A1, A2 run 1, A3 part) | 7,121 | 4 | 0 | **1** | 0 | 0 | 0 |
| 2 (A2 run 2, A3) | 544 | 0 | 0 | 0 | 0 | 0 | 0 |

Logs: `/tmp/claude-1000/w2a/session1.log` and `session2.log`.

## Findings

1. **Double-clicking the Avatar crashes ScummVM (segfault).** In session 1 a double-click I meant for Thordis landed on the Avatar. The log shows `Item: 1 (shape 1) calling usecode event 1 @ 0401:0080`, then `Segmentation fault (core dumped)`.
   - `lv-patched/AVATAR.UNK:57-61` `use()` compiles `CONTAINER_GUMP_OPEN` and `Gump_MainMenu` to 0: `push byte 0; bit_and` and `openGump(0)`. Retail 0x401 has `push 0100h` and `openGump(1)`.
   - `Item::openGump(0)` builds a `PaperdollGump` from gump shape 0, with `getGumpItemArea(0)`.
   - `cmp_avatar.py` gives byte-identical `use()` from the pre-wave-2 compiler (3b3fc14), so this is **not wave 2**. It ships today all the same: any player who double-clicks the Avatar to open the paperdoll crashes the game.
   - Confidence: high on the bytes and on that crash. Medium on the exact engine dereference (no core: apport, `ulimit -c 0`).
   - Fix: pin both constants (0x100, 1).
2. **After Mythran's LV dialogue the camera stays centred on Mythran.** The patch preamble spawns retail `057C:0BCF` (enterConvo, which runs `Camera::setCenterOn(referent)`). `TypeMythranLVDlg`'s `exitConvo()` codegen only does stasis and loiter; it never scrolls back.
   - After **Farewell**, two walks left Mythran at screen centre with the Avatar off-centre (`A1-10`..`A1-13`). A player walking away will leave the fast area.
   - This predates wave 2. The patch and the exitConvo codegen are both untouched. Confidence: high.
3. **No code deals poison damage after the Passage Test.** `lv-patched/PLNTST.UNK:27-28` says so: "the ongoing poison DAMAGE ticks … are deliberately NOT wired". In the whole EUSECODE, only `TYPEPOIS` (0x59C) reads `avatarPoisoned` in a loop, and it has no caller (10-01 report 5b).
   - HP stayed at 30 for about 100 s while poisoned. The claim's premise is wrong; this is not a regression.
4. **Three new `Non-existent process PID (0) in implies` on the AVATAR detour (Map 0).** They come from class 1025 process 202 (item 9461, type 524), between offsets 13346→13361 and 13391→13406, and from process 91 at 13943→13958. The 10-04 L2 run of the same detour had none.
   - Reading: rule 3. A process intrinsic called as a statement now waits, and when the intrinsic returns no process (pid 0) the `implies` warns. The scene still completed. Disassemble 0x401 at 0x3442..0x349E and 0x3677..0x3686 to name the intrinsic.
   - The 4th line is Devon's farewell; it is old (10-04 finding 2).
5. **`moveToAvatar` leaves a parked camera** that stays put through the Passage Test's own teleport of the Avatar (`A2-04` vs `A2-06`). The harness causes it, as in wave 1.

## Harness anomalies

1. The brown-pixel motion tracker hit the Avatar's shield once. That double-click is how finding 1 surfaced. The tracker then got an exclusion box.
2. `strike()` aims with a centred-camera projection. On Map 8 (camera on Mythran) and Map 10 (camera parked) it missed. Diff-based tracking reached the NPC in 2-19 tries.
3. Run 1 of A2 (session 1) went unplated, apart from the film.

## Disk changes

- Wrote this report and the plates in `docs/playtest-2026-10-07-wave2-a/`.
- `session.sh start` synced `shared/u8-lv-patched/USECODE/EUSECODE.FLX` to `13ccb939`, matching `shared/build`.
- Saves (48 files) and `scummvm.ini` were restored; the sorted md5 list equals the pre-session list. ScummVM had rewritten `ultima8.000` and slot 1 was overwritten; both are restored.
- Scratch under `/tmp/claude-1000/w2a/`: driver copy, logs, the post-test save, disassemblies, and `pre/`, a `git archive` of the 3b3fc14 compiler.
- No source, builder, map, fork, TODO, HANDOFF or commit was touched. The session is stopped, and no :77 process is left.

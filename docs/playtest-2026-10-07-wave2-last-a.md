# Compiler wave 2 last build, instance A, verified in engine (2026-10-07)

Build under test: the uncommitted tree on top of `main` `a2aaf16`, with
`lv-patched/THORDIS.UNK` change 5 (each person block's closing
`tempKey = ask(tempList)` in `toldOthersConvo` guarded by
`if toldMyTribe = false` / `if toldOthers = false`) and the `FREE.UNK`
regrow-failure `Camera::setCenterOn(1)`. EUSECODE `a95a8df0`, FIXED
`c3d29a1f`. The session log reads `usecode/eusecode.flx:
e1fed4c81e85b86ff1b59810ab50f94a, 1524708 bytes` and `Running Ultima VIII:
Pagan (Gold Edition + Lost Vale/DOS/English)`. The binary is
`scummvm-lv/scummvm` (15:41:45). Standard harness, display `:77`. Plates are in
`docs/playtest-2026-10-07-wave2-last-a/` at 640x400.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| L1 | The "What else" soft-lock is gone; mirror; all-told Yes/No | **PASS.** Driven organically, with no `setGlobal`. After Ezrekal, the main menu returned, **bye** freed the Avatar and no THORDIS `UCProcess` was left. The mirror (You → Tyorvi → Ragnar with `toldOthers` 1) returned the same way. Yes/No waited 30 s; **No** gave "Make up your mind, you should." and the menu returned; **Yes** reset both flags and offered **Your people. • The others.** |
| L2 | First-time path (both flags 0) | **PASS.** "My people or the others?" with **Your people. • The others.**, and each person's lines played (You, Tyorvi and Ragnar in the first conversation; Ezrekal, Atli, Ingyald and Hrodny after the Yes reset). A completion in a non-last block (Hrodny) also returns cleanly |
| L3 | A gold plaque and the Message Scroll: gump opens, closes, play continues | **PASS.** The q68 plaque on Map 17 opened "FORBIDDEN TO MORTALS" and closed on a click. The scroll opened page 1, paged to "Odion" on page 3, and closed on the third click. The Avatar walked after each, and no `UCProcess` was left |
| L4 | Log hygiene | **PASS.** One session of 1,044 lines. `Non-existent process` 0, `stuck in process loop` 0, `Segmentation` 0, `Assertion` 0, `Cycle in paint` 0 (see note), `Unhandled intrinsic` 0. There were also 0 `Unhandled` of any kind, 0 `segment 0000` and 0 `Item::combine` |

Not run, as the brief directed: `run_all_tests.sh`, `build_artifacts.sh`,
`install_lv.sh` and `build_scummvm.sh`. Instead, `session.sh start` synced
`USECODE/EUSECODE.FLX`. Afterwards `cmp` found all five game-copy artifact
paths identical to `shared/build`.

## Method

- **Backup.** I backed up the 48 files in `~/.local/share/scummvm/saves` and
  `scummvm.ini`, with an md5 list, to `/tmp/claude-1000/w4a/bak/`. The
  driver is a copy of `/tmp/claude-1000/w3a/py/`, re-pointed at the w4a
  scratch and this plate folder. Its `pgrep` is narrowed to
  `-p …/shared/u8-lv-patched`.
- **Checkpoint.** I used `cp9b-thordis-spoken.sav` (Map 10, `thordisMet` set,
  `toldMyTribe` 0, `toldOthers` 0, not poisoned), copied over
  `ultima8.001` and loaded with `Ultima8Engine::loadGame 1`. One session.
- **Game-state writes:**
  - one cross-map teleport (Map 10 → Map 17) and one in-map teleport on
    Map 17, each with cheats toggled on and back off;
  - `CameraProcess::moveToAvatar` before each talk strike;
  - `debugflag_enable Object` from the Map 17 part onward (log line 444).
    It was **off** for the whole Thordis part.
- **No** `setGlobal`, `Item::grab` or other flag write. Every Thordis
  menu answer was clicked from the screen.

## L1: the soft-lock, the mirror, Yes/No, PASS

Thordis's flags were advanced only by talking. The sequence ran across six
conversations, read with `UCMachine::getGlobal 0x455`/`0x456`
(`toldMyTribe`/`toldOthers`).

**Conversation 2: the repro (`toldMyTribe` 1, `toldOthers` 0).** This is
final-a finding 1's exact path. Conversation 1 is in L2.
- Main menu **Why will no one speak to me? / Tell me about the other people. / bye** (`L1-01`).
- **Tell me about the other people.** → "What else, wish you to know?" (`L1-02`) → **The others.** alone (`L1-03`).
- **The others.** → "Of Atli, Ingyald, Hrodny or Ezrekal…" → **Ezrekal • Hrodny • Ingyald / Atli** (`L1-04`).
- **Atli** → "The leader of the other clan…" (`L1-05`) → **Ezrekal • Hrodny • Ingyald** (`L1-06`).
- **Ingyald** → "A truer sign of the gods displeasure…", "Strangle him myself…" (`L1-07`) → **Ezrekal • Hrodny** (`L1-08`).
- **Hrodny** → her three lines (`L1-09`) → **Ezrekal** alone (`L1-10`).
- **Ezrekal** → "A good-for nothing, dried up old hag…" (`L1-11`) and "Sooner such food to Atli, yield…" (`L1-12`).
- **Then the main menu came back:** **Why will no one speak to me? / bye**
  (`L1-13`). This is where final-a froze.
  - Flags read 1 / 1.
  - `listProcesses` showed only `UCProcess 1518, item 106, type 207, THORDIS,
    IP 046A:18FE` and its `GumpNotifyProcess`. That is `use()` waiting on its
    own menu. No `toldOthersConvo` process was left, and nothing was waiting
    on an empty ask.
- **bye.** Thordis had `LoiterProcess 885` and no `UCProcess`.
  - The first 1.2 s walk burst right after the console closed did not move
    the Avatar (`L1-14`; harness anomaly 1).
  - The next three bursts walked him (6784, 6240) → (6784, 6600) → (6584, 6600) → (6688, 6600), with `flags 0` (`L1-15`).

**Conversation 3: all told, the wait and No.**
- **Tell me about the other people.** → "Told you of everyone, I have. No others, there are." (`L1-17`) → "Tell you again of them, I should?" (`L1-18`) → **Yes. • No.**
- **Negative control.** I left it alone for about 30 s (`L1-19`, ten frames
  across 27 s on `sheet-yn.png`). "Make up your mind" never appeared, and the
  menu stayed.
  - Wait chain: `LVFREE` (pid 587, `05AE:00F9`) waited on the
    `GumpNotifyProcess`.
  - THORDIS `toldOthersConvo` (pid 535, type 1, `046A:8483`) waited on
    LVFREE, and `use()` (pid 424, type 207) waited on that.
- **No.** "Make up your mind, you should." (`L1-20`), then the main menu
  returned (`L1-21`). Flags still read 1 / 1.
- **bye.** The Avatar walked (6688, 6600) → (6688, 6832).

**Conversation 4: Yes.**
- Same opening, then **Yes. • No.** again (`L1-23`).
- **Yes.** → "My people or the others?" (`L1-24`) → **Your people. • The others.** (`L1-25`).
- Flags read **0 / 0**, which is the reset branch.
- The rest of conversation 4 is L2's second half.

**Conversation 6: the mirror (`toldMyTribe` 0, `toldOthers` 1).**
`toldOthers` 1 was reached organically in conversation 5 (L2).
- **Tell me about the other people.** → **Your people.** alone (`L1-26`) → **Ragnar • Tyorvi • You** (`L1-27`).
- **You** → "Nothing to tell, there is. Clan Elder…" (`L1-28`) → **Ragnar • Tyorvi**.
- **Tyorvi** → "My younger brother…" (`L1-29`) → **Ragnar** alone (`L1-30`).
- **Ragnar** → "Our hunter, Ragnar is…" (`L1-31`).
- **Then the main menu returned** (`L1-32`). Flags read 1 / 1, and the only
  THORDIS process was `use()` (type 207, `046A:18FE`) on its menu gump.
- **bye.** `LoiterProcess 3497` and no `UCProcess`. The Avatar walked
  (6720, 7136) → (6616, 7136) (`L1-33`).

## L2: the first-time path, PASS

**Conversation 1 (both flags 0).**
- Main menu **Why will no one speak to me? / Tell me about the other people. / bye** (`L2-01`).
- The pick gave "My people or the others?" (`L2-02`) and the single row **Your people. • The others.** (`L2-03`).
- **Your people.** → "Of me, Tyorvi, or Ragnar…" → **Ragnar • Tyorvi • You / The others.** (`L2-04`).
- **You** → her two lines (`L2-05`) → **Ragnar • Tyorvi / The others.** (`L2-06`).
- **Tyorvi** → his line → **Ragnar • The others.** (`L2-07`).
- **Ragnar** → his line (`L2-08`).
- **Back in `use()`.** The main menu returned (`L2-09`). Flags read 1 / 0.
  `listProcesses` showed only `use()` (type 207, `046A:18FE`) on its gump.
- **bye.** Thordis loitered, and the Avatar walked (6532, 6396) → (6844, 6396).

**Conversation 4, after Yes (both flags 0 again).**
- **The others.** → **Ezrekal • Hrodny • Ingyald / Atli • Your people.** (`L2-10`).
- **Ezrekal** played her lines → **Hrodny • Ingyald • Atli / Your people.** (`L2-11`).
- **Atli** is a backward pick, so it returned silently to the main menu (`L2-12`). That is final-a finding 2, the 1994 structure.
- Flags 0 / 0. `toldEzrekal` stayed set.

**Conversation 5: completion in a non-last block.**
- "My people or the others?" → **The others.** → **Hrodny • Ingyald • Atli / Your people.**, with Ezrekal correctly absent (`L2-13`).
- **Atli** → **Hrodny • Ingyald / Your people.**
- **Ingyald** → **Hrodny • Your people.** (`L2-14`).
- **Hrodny** → her three lines (`L2-15`). This block sets `toldOthers` and
  skips its ask. `tempKey` stays "Hrodny", so the Ezrekal block is not
  entered, and the main menu returned (`L2-16`).
- Flags read 0 / 1, and only `use()` was on its gump.
- This is the guarded case final-a did not exercise: the completing person
  is not the last block.

## L3: plaque and Message Scroll, PASS

**The map hop.** The teleport Map 10 → Map 17 logged `Loading Fixed items in
map 17`, so the old-save trap did not apply. `findShape 614` found 4, with
q70 (5055, 5121), q69 (2495, 5121), q68 (5055, 9217) and q55 (4127, 7680),
all `n: 235`. `findShape 864` found 1: `Item 5487 (uc: TYPEMESS) (3328, 1536,
8) q: 80`.

**Gold plaque q68 (entry court).**
- **Negative control.** From (5000, 9420), about 210 units away, a
  double-click logged only the look trace and no `event 1`, and no gump
  opened (`L3-00`). That is the engine's 128-unit use reach working as it
  should.
- **Look.** A single click logged `event 0 @ 04EB:0080` and barked "plaque" (`L3-01`).
- **Use.** From (5176, 9284), a double-click logged `Item: 708 (shape 614)
  calling usecode event 1 @ 04EB:00A9`. The gold plaque gump read "FORBIDDEN
  TO MORTALS" (`L3-02`).
- **Close.** One click closed it (`L3-03`).
- **After.** `listProcesses` had no `UCProcess` or `GumpNotifyProcess`, and the
  Avatar walked (5176, 9284) → (5176, 9516).
- **Earlier attempt.** I opened it once before that. The console chord closed
  that gump instead (`L3-03b`, harness anomaly 2).

**Message Scroll.**
- **Setup.** An in-map teleport to (3330, 1640, 0) put the Avatar beside the plinth.
- **Look.** It logged `event 0 @ 0360:0080` and barked "message scroll" (`L3-04`).
- **Use.** A double-click logged `Item: 5487 (shape 864) calling usecode event 1 @ 0360:00B1`. The scroll gump opened on "TO FELICITAR, TO DOLORAS, TO TIMYRA…" (`L3-05`).
- **Paging.** Click 1 showed page 2, "…broken from within… the only key ever
  made for that door." (`L3-06`). Click 2 showed page 3, "Odion" alone
  (`L3-07`), which is the shipped look. Click 3 closed it (`L3-08`).
- **After.** No `UCProcess` or `GumpNotifyProcess` was left, and the Avatar
  walked (3330, 1640) → (3330, 1976). The scroll is still on its plinth.

## L4: log hygiene, PASS

The session log is `/tmp/claude-1000/w4a/session1.log` (1,044 lines).

| Pattern | Count |
|---|---|
| `Non-existent process` | 0 |
| `stuck in process loop` | 0 |
| `Segmentation` | 0 |
| `Assertion` | 0 |
| `Cycle in paint` | 0 |
| `Unhandled intrinsic` | 0 |

- **Other patterns.** 0 `Unhandled`, 0 `segment 0000`, 0 `Item::combine`
  and 0 `Invalid item`.
- **Warnings.** Only three ScummVM GUI-startup warnings (`gui-icons.dat`,
  `translations.dat`, theme fallback).
- **Note on `Cycle in paint`.** It is `debugC(kDebugObject)`, and `Object`
  was off for the whole Map 10 part. It was enabled only from line 444 (Map 17).
  The 0 therefore does not re-measure final-a finding 3, which saw the
  Map 10 Passage Plant lines with the flag on. This run was in the Hrodny
  village, not at the plant.

## Findings

1. **Change 5 removes an option a player could see before.** In the
   first-time branch the list keeps the other header. When the fourth
   person is told (`L2-16`), the guard skips the ask, and **Your people.**
   is no longer offered in that conversation. Before change 5 it was
   offered, but picking it was a backward pick, which ended the routine
   silently (final-a finding 2). So nothing reachable is lost. The player
   gets the main menu at once, and a new conversation offers "What else" →
   **Your people.** Mentioned only so the author knows the menu changed.
2. **Two unguarded asks remain, at the group headers.** These are
   `THORDIS.UNK:1949` (the "Your people." block) and `:1983` (the "The
   others." block).
   - **What makes them empty.** Either list is empty if all three (or all
     four) person flags are set while the group flag is still false.
   - **Organic play.** Every person block sets its group flag when it
     completes the set. The Yes branch clears all nine flags together.
     Neither ordinary path makes the state, and I found no way to make it.
   - **Where it could come from.** A save that set the person flags one by
     one, or a future script that clears only the group flags. **[INFERENCE:
     not exercised.]**
3. **Hrodny's three barks take more than 40 s of wall time.** At the
   harness's clock rate a `listProcesses` 40 s after the pick still showed
   `toldOthersConvo` in `ActorBarkNotifyProcess` (`046A:913D`). It finished
   about 10 s later. That is not a hang; it is recorded so the next
   verifier does not mistake it for one.

## Harness anomalies

1. **The first walk burst after a console close sometimes does nothing.**
   It happened twice: after bye in conversation 2, and on Map 17. The next
   burst moved the Avatar. The process lists taken just before showed no
   stasis holder, so I read it as a focus/timing miss. Retry a burst once
   before calling the Avatar frozen.
2. **The ctrl+alt+d chord closes a readable (plaque) gump.** A
   `listProcesses` taken with the plaque open showed the plaque's
   `UCProcess` and `GumpNotifyProcess` already terminated (`AtD`/`ATD`,
   gump 0), and the follow-up click landed on the floor. Do not open the
   console while judging a readable gump's close.
3. **The camera drifts off the Avatar after conversations.** This is
   final-a finding 4. Thordis also loiters fast enough that a two-read
   standstill `strike` kept missing. One `moveToAvatar` → `objectInfo` →
   immediate double-click (`fstrike`, verified by a type-207 THORDIS
   process) hit on the first try every time.

## Disk changes

- **Wrote** this report and 59 plates in
  `docs/playtest-2026-10-07-wave2-last-a/`.
- **`session.sh start` synced** `shared/u8-lv-patched/USECODE/EUSECODE.FLX`
  from `shared/build`. The other four paths were already identical.
- **Saves.** All 48 save files and `scummvm.ini` were restored from the
  backup with `rsync --delete`. The sorted md5 list equals the pre-session
  list (`RESTORED-IDENTICAL`). ScummVM had rewritten `ultima8.000` and
  `scummvm-history.txt`, and `ultima8.001` held the checkpoint.
- **Scratch** in `/tmp/claude-1000/w4a/`: the backup, driver copy, session
  log, md5 lists and frame films.
- **Untouched:** no source, builder, map, fork, TODO or HANDOFF file;
  `~/lv-checkpoints`; display `:78`. No commit.
- **Session.** Stopped; ScummVM 504312 and Xvfb 504292 are killed.

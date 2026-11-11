# Wave 2 last build, instance B: Tyorvi, Map 10 exits, Aramina (2026-10-07)

Build under test: EUSECODE `a95a8df0` (1,524,708 bytes), FIXED `c3d29a1f`. The
session log reads `usecode/eusecode.flx: e1fed4c81e85b86ff1b59810ab50f94a,
1524708 bytes` and `Running Ultima VIII: Pagan (Gold Edition + Lost
Vale/DOS/English)`. The binary is `scummvm-lv/scummvm` (15:41), and its
`detection_tables.h:297` carries `e1fed4c8…`/1524708. Plates are in
`docs/playtest-2026-10-07-wave2-last-b/` at 640x400.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| M1 | Tyorvi: the Key to the Clouds chain gives the key; a second talk does not offer "I have something for you from Ezrekal."; `findShape 82` unchanged | **PASS**. The chain ran on the drunk roll. `findShape 82` went from 2 to 3 and `givenTea` to 1. On the second talk the option was gone, and the count stayed 3 |
| M2 | Map 10 conversation exits: Ingjald, Hrodny (with "Tell me more of the cliffs."), Ragnar | **PASS**. Each NPC went back to a `LoiterProcess` with no `UCProcess` left, and the Avatar walked after every exit. I ran Ragnar twice, exiting from two different menus |
| M3 | Aramina's `+`-joined strings are spaced correctly | **PASS**. "You're Avatar, aren't you?", the menu option "Yes, I am Avatar." (whose `case nameStr` dispatches) and "'Tis a grand day, friend Avatar." are all spaced correctly. These lines need `devonInRule`, which I set by `setGlobal` |
| M4 | Tiny Tar regrow failure: the camera follows the Avatar after the kill | **NOT DEMONSTRATED**. The regrow at (2912, 4676, 0) succeeded (hp 30), so the failure branch never ran (finding 1). The budget stopped any retry |
| M5 | Log hygiene | **PASS**. In 6,953 lines: 0 `Unhandled intrinsic`, 0 `Non-existent process`, 0 `stuck in process loop`, 0 Segmentation, 0 Assertion, 0 `Cycle in paint`, 0 `Camera::get*`. There was 1 `Skipping invalid shape in sorter: 539,4`, on loading `run-s16-tinytar.sav` (finding 3) |

The brief said not to run `run_all_tests.sh`, `build_artifacts.sh`, `install_lv.sh` or
`build_scummvm.sh`, so I did not. I did not check the fork patch either, since
instance A covers it.

## Method and isolation

- **Display and game copy.** I used display `:78` and the game copy `/tmp/claude-1000/w4b/game`, which is `shared/u8-lv-patched` with the four `shared/build` artifacts copied over it the way `sync_one` does. `cmp` matched all five destination paths.
- **Launch.** Config was `w4b/scummvm.ini` and saves were in `w4b/saves/`. The command line was `scummvm --config=… --savepath=… --debuglevel=1 --extrapath=…/dists/engine-data -p w4b/game -x 1 ultima8`. One pid ran for the whole session.
- **Driver.** A copy of w3b's `drv.py`/`h.py`, with pgrep narrowed to `w4b/[g]ame`.
- **Saves.**
  - `cp22-hastea.sav` was loaded at launch, for M1-M3.
  - `run-s16-tinytar.sav` was copied over `ultima8.001` and loaded with `Ultima8Engine::loadGame 1`, for M4.
- **Game-state writes:**
  - teleports with cheats on, each followed by a toggle back to off;
  - `debugflag_enable Object`;
  - `CameraProcess::moveToAvatar` after same-map teleports;
  - `UCMachine::setGlobal` on `0x4B6` (`devonInRule`) and `0x65F` (`araminaMet`), for M3 only (details there).
- **Played by hand.** No `Item::grab`. I picked every menu answer from the screen and drank the potion with a double-click in the pack.
- **Refreshing Map 10.** `cp22-hastea` (08-17) carries an old Map 10. Before testing, I made a hop from Map 10 to Map 3 and back.

## M1: Tyorvi, PASS

**At load.** `hasTea` (0x426) read 1, `givenTea` (0x425) 0 and `haveMark` 1. `findShape 82` returned 2: the pack's q99 key 4528 and the Map 10 q20 key.

**The chain.**
- **Opening.** The double-click logged `Item: 115 (shape 707) calling usecode event 1 @ 0473:033D`. The menu offered **Tell me more of the Cliffs. / Do you have the Key to the Clouds? / I have something for you from Ezrekal. / bye** (`M1-01`).
- **The roll was drunk** ("Shomething from Ezkkre...Esbak..."). The drunk route to the key is the 1994 one (`TYORVI.UNK` "Shut up and drink it!" case), so I took it rather than retrying for a sober roll.
- **Path, all clicked from the screen:**
  1. **It is an elixar.** → "A what?"
  2. **It is a potion.** → "A poshun? From Eshrk...Ezzkre...that hag? -hic-…"
  3. **It will heal your dreams.** → "Heal -hic- my dreams? …"
  4. **Shut up and drink it!** (`M1-02`) → "All right, all right! Have to shout you do not! Try it I will." There was a ~30 s wait, then "Hmmm, taste too bad that did not…".
  5. **May I have the Key to the Clouds?** (`M1-03`) → "Well, treacherous it is, but brave you are. … Here, here the Key to the Clouds is." (`M1-04`).

**Results:**
- `findShape 82` went from 2 to **3**. The new item is `Item 18550 (class Item, shape 82) (uc: KEY), 0, (0, 0) q: 0, f: 0xc` (contained).
- Weight went from 110 to 120.
- `givenTea` read **1**, and `hasTea` was still 1.
- `findShape 395` = 0, so the elixir bottle was consumed.

**Negative control: PASS.** I talked to him again (`event 1 @ 0473`). The menu was
**Tell me more of the Cliffs. / Are you OK, Tyorvi? / Do you have the Key to the
Clouds? / bye** (`M1-06`).
- "I have something for you from Ezrekal." is absent, so the chain cannot start again.
- **Static check of the other routes.** In the patched source, "May I have the Key…" is added only by the two drink cases. Those are reachable only through the Ezrekal option, and both of its adders (lines 384 and 2246) now test `givenTea = false`.
- **After bye.** `findShape 82` was still **3**. Tyorvi had `LoiterProcess 7453`, and the Avatar walked from (19432, 8760) to (19536, 8760).

## M2: Map 10 conversation exits, PASS

| NPC | Talk (log) | Path clicked | Right after the exit | ~5 s later | Avatar walk |
|---|---|---|---|---|---|
| Ingjald 112 | `event 1 @ 0470` | **What is your name?** ("Ingyald, my name is…") → **bye** (`M2-01`) | `UCProcess type 207 @ 0470:3670` waiting on an `ActorBarkNotifyProcess` (farewell bark "A new batch tomorrow will I have", `M2-02`) | `LoiterProcess 6269` + pathfinder; no UCProcess; moved (20881,6971)→(21069,6951) | (20700,6900)→(20768,6968) |
| Hrodny 113 | `event 1 @ 0471` | **Tell me more of the cliffs.** (`M2-03`) → "What more to tell, is there? Dangerous, they are, in the old tales. Forbidden to climb, they were. For somewhere above the clouds, to the home of the gods." (`M2-04`) → next menu **What about Tyorvi? • bye**, so the option was removed (`M2-05`) → **bye** | `LoiterProcess 5810` already running | `LoiterProcess 5810` only; moved (21719,8457)→(21785,8751) | (21900,8300)→(22180,8580) |
| Ragnar 105, run 1 | `event 1 @ 0469` | **Atli sent me to you. / Farewell.** (`M2-07`) → **Farewell.** | UCProcess `0469:3895` + farewell bark | `LoiterProcess 2606` only; moved (5096,9060)→(5176,9140) | (5050,8420)→(5050,8652) |
| Ragnar 105, run 2 | `event 1 @ 0469` | **Atli sent me to you.** → "Sent you to me that cur did? Leader of Huskold clan Atli is! …" → **Atli admires you. / Atli does curse a lot. / Farewell.** (`M2-09`) → **Farewell.** | the same bark wait | `LoiterProcess 2641` + pathfinder; moved (5340,9360)→(5108,9592) | the diagonal push was blocked by the hut wall; W/N/E/S moved 104/96/104/104 units |

Ingjald and Ragnar loiter under their hut roofs, which win the click. I reached
both by teleporting inside the hut (a same-map teleport plus `moveToAvatar`).

## M3: Aramina, PASS

Aramina (13) is on **Map 40** at (12927, 8575, 48) in this save. I reached her with a map-switch teleport to (13077, 8675, 48).

**First talk, as loaded** (`devonInRule` 0x4B6 = 0, `araminaMet` 0x65F = 0).
- The double-click logged `event 1 @ 040D:10BB`.
- She greeted "How may I serve you, stranger?" (`M3-01`), then offered **By what are you called? / bye** (`M3-02`). The answer was "My name is Aramina." (`M3-03`), which is a literal string.
- **No `+` join is reachable in this state.** All three English `+` sites (`ARAMINA.UNK:587`, `687`, `1278`) are inside the `devonInRule` branch.
- In the bytecode, `use()` builds `"Yes, I am " + getName() + "."` and then branches on global `04B6` (`devonInRule`), and `getName()` is the Avatar's name.

**Second talk, with the branch forced.** `setGlobal 0x4B6 1 1` and `0x65F 1 0`, both read back.
- She greeted "Good day to you, stranger." (`M3-04`).
- **What is your name?** gave "I am Aramina, my friend. I work here in the palace for Devon. **You're Avatar, aren't you?** Devon speaks of you often." (`M3-05`).
- The next menu was **Yes, I am Avatar. • bye** (`M3-06`). The concat is spaced correctly.
- Clicking it dispatched `case nameStr`: "Yes, I knew it was you. Did you really save him?" (`M3-07`), then **Yes, I did. / Well, it was nothing, really. / bye**.

**Third talk** (`araminaMet` 1).
- She greeted "**'Tis a grand day, friend Avatar.**" (`M3-08`).
- The menu was **bye** alone (`M3-09`). That is expected: only the German branch adds an option there (1994).
- After bye, she had a `LoiterProcess` and the Avatar walked.
- I set `devonInRule` back to 0 afterwards.

The brief's example "Yes, I am Aramina." does not exist in the source. The
string is "Yes, I am " + the Avatar's name, so on screen it reads "Yes, I am Avatar.".

## M4: Tiny Tar regrow failure, NOT DEMONSTRATED

**Setup.**
- I loaded `run-s16-tinytar.sav` and made a map-switch teleport to Map 18 (2848, 5520, 0). The Avatar's `ef` read `0x122`, and `EXT_CAMERA` (0x20, `item.h:700`) is the camera-follow bit.
- I opened the pack with `i` and double-clicked potion 14459: `event 1 @ 04E5:00A9`. The shrink played, and the Avatar became shape 708.

**The attempt.** I teleported the tiny Avatar to final-b's death spot, (2912, 4676, 0) (`M4-01`), and filmed for 75 s.
- He regrew there normally: shape 1, hp 30, `ef 0x122`, at (2912, 4676, 0). So `canExistAt` passed and the failure branch never ran.

**How to judge it next time.** Kill the Avatar in the failure branch, then read `objectInfo 1`. `ef & 0x20` set means the camera follows him. `CameraProcess::terminate` clears that bit and the item constructor sets it (`camera_process.cpp:122,151`).

## Findings

1. **The regrow at (2912, 4676, 0) is not deterministic between runs.**
   - **What differs.** In final-b, session s01 logged `Item 1 … (2912, 4676, 0) … ef: 0x102 … Actor hp: 0` (`/tmp/claude-1000/w3b/lv_run.s01.log:8804`). Here, the same coordinates gave a successful regrow.
   - **Possible causes [INFERENCE].** Something transient blocking the full-size box, such as a loitering NPC or a gate's open/closed state, or a teleport that does not reproduce how the walk arrived.
   - **Next step.** A deterministic M4 repro needs a spot judged with `exact_reach.py`, or a tiny walk into a gap only the tiny body fits.
   - **Same log line, unrelated to this change.** In final-b's death, `ef 0x102` lacked `EXT_CAMERA`, which supports the old-build observation.
2. **Ingjald's and Ragnar's loiter areas sit under their hut roofs.** Clicks from outside hit the roof (`Item 14714 (shape 412) … z 40`), so a player has to step inside to talk. That is the same family as the Hrodny note in wave 1.
3. **One `Skipping invalid shape in sorter: 539,4` on loading `run-s16-tinytar.sav`.** Shape 539 is the shield half, and frame 4 does not exist. It comes from the old save and was not seen on this build's own items.
4. **`hasTea` stays 1 after the key.** It is harmless now that every adder tests `givenTea`, but any future `hasTea`-only test would reopen the duplicate.
5. **Tyorvi's drunk path reaches the key without "Just try it, please."** (that pick ends the talk when he is drunk). The brief's "retry for the sober branch" was not needed.

## Harness anomalies

- **`CameraProcess::moveToAvatar` never answers `con()`.** It sent twice each time, harmlessly.
- **A teleport's leaked `exit` opened the minimap once** (it showed in the pack plate). I toggled it off with `m`.
- **`setsid`/subshell `&` launches died when the Bash call returned.** Xvfb and ScummVM ran as supervised services `w4b-xvfb`/`w4b-scummvm` instead.
- **The red-pixel menu detector false-fires on Aramina's red carpets and on the Avatar's tunic.** I confirmed every menu by plate.

## Disk changes

- **Wrote** this report and 26 plates in `docs/playtest-2026-10-07-wave2-last-b/` (M1-01…06, M2-01…10, M3-01…09, M4-01).
- **Scratch in `/tmp/claude-1000/w4b/`:**
  - the game copy, `scummvm.ini` and saves (`ultima8.001` = `run-s16-tinytar.sav`; ScummVM may have written `ultima8.000`/`timestamps`);
  - `lv_run.log`;
  - the driver in `py/`;
  - frames in `sp/`;
  - `aramina_prev.dis`.
- **Not touched:** `:77`, `shared/`, `~/.config/scummvm`, `~/.local/share/scummvm`, `~/lv-checkpoints` (read only), and any source, builder, map, fork, TODO or HANDOFF file.
- **Session.** Nothing was committed. ScummVM and Xvfb `:78` are stopped.

# Compiler wave 2, instance C: steps 15-18, the bag, conversation exits (2026-10-07)

Change under test: compiler wave 2, commits `c89bf07..a2aaf16` on `main`.
Artifacts: EUSECODE `13ccb939`, FIXED `14774b0b`, U8SHAPES `a611e9be`, TYPEFLAG
`9f534e59`, all equal to `shared/build/ARTIFACTS.sha256`. The session log reads
`usecode/eusecode.flx: dbce29589ae46b798dc8056c84dddcd3, 1524536 bytes` and
`Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)`. Binary
`scummvm-lv/scummvm` (12:50:18). Plates are in `docs/playtest-2026-10-07-wave2-c/`
(640x400).

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| C1a | Tiny Tar entry sets `templeOpen` | **PASS**, with one new visual defect (finding 1) |
| C1b | Altar scene: real, waited `scrollTo` pans; `godsFree` 1 | **PASS** |
| C1c | EggEndgame on the Map 10 pad: `endgameStarted` 1, closing barks | **PASS** |
| C1d | Ezrekal's **I have freed your gods!** gives the bag once: `hasBag` 1, six stacks of 25 | **PASS** (negative control PASS) |
| C1e | Top-up refills a drained stack within about 40 s | **PASS** (15 → 20 → 25 over two polls, about 37 s of game time) |
| C2 | Gold plaque and Message Scroll gumps | **NOT DEMONSTRATED** (budget) |
| C3 | Conversation exits for Ingjald, Hrodny, Ezrekal, Ragnar; Hrodny's cliffs line | **PARTIAL**: Ezrekal PASS on both exits (the bag branch's `exitConvo` and **bye**); the other three and the cliffs line were not run (budget) |
| C4 | Aramina's greeting spacing | **NOT DEMONSTRATED** (budget) |
| C5 | Log hygiene | **PASS** on the five named lines (all 0); **288 `Unhandled intrinsic`**, all `Camera::getX/getY/getZ` from the Tiny Tar routines (finding 1) |

Checks this instance skipped: `run_all_tests.sh`, `build_artifacts.sh` and
`install_lv.sh` were not run, because the brief forbade them. Artifacts were
already built and estate-tested, and another instance was playing.

## Method

I used an isolated copy, so nothing touched `:77`, `shared/u8-lv-patched`,
`~/.config/scummvm` or `~/.local/share/scummvm`. The game was copied to
`/tmp/claude-1000/w2c/game`, with the four artifacts copied over it as
`session.sh` `sync_one` does (sha256 checked). The config went to
`/tmp/claude-1000/w2c/scummvm.ini`, saves to `/tmp/claude-1000/w2c/saves/`,
and the display was `Xvfb :79`. ScummVM was launched with `--config`,
`--savepath`, `-p <copy>` and **`-x 1`**. That loads slot 1 directly with no
intro, no name entry and no Devon menu. `~/lv-checkpoints/run-s16-tinytar.sav`
was copied in as `ultima8.001`. The driver was a copy of the `v1007` `drv.py`/`h.py`,
pointed at `:79` and this log. Its `h.P()` pgrep was narrowed to this instance's
game directory, because the original pattern also matches the other instances.

Game-state writes:
- teleports with cheats on, each followed by `Cheat::toggle` back to false:
  Map 10 (18432, 23200), Map 18 (2864, 5980), Map 18 (2864, 6292), Map 10
  (12960, 12704);
- `CameraProcess::moveToAvatar` once;
- `debugflag_enable Object`;
- `Item::grab 772` (the restored shield, which this old save leaves on the
  Sacred Circle).

Every egg in C1 hatched from a walk: trigger 211 both ways, crack hint,
TempleEntry, the altar (twice), trigger 210, and EggEndgame (twice). Every menu
answer was clicked from the screen.

## C1: steps 16 to 18, PASS

**Start.** Map 10 (21760, 8544), `templeOpen` 0, `godsFree` 0, `shieldFixed` 1,
`endgameStarted` 0, `hasBag` 0. Three frame-8 Tiny Tar (3963, 8603, 14459) in
the pack. I walked south into trigger 211, then took the hall route to the
crack. `EggCrackHint` hatched (`05B1:0080`, `C1-01`).

**Negative control.** Three full-size south pushes at x 2864: stopped at
(2864, 6108) (`C1-02`).

**Tiny Tar, timed.** Drink 2 (8603, `event 1 @ 04E5:00A9`) was filmed at about
0.6 s per frame with the console closed. Times are from the double-click:

| t (s) | |
|---|---|
| 0 to 9.8 | barks and stasis (each `Avatar.bark` in `makeAvatarTiny` now waits, rule 3) |
| 9.8 to 12.7 | lightning, then **a black screen** (finding 1) |
| 13.3 | walk south |
| about 14 | `EggTempleEntry` (`05B0:0080`); "I am through. The air in here is old, and very still." over the tiny Avatar in the crack (`C1-07`) |
| 41.1 to 43.4 | black again: `makeAvatarBig` |
| after | full size at (2864, 6292), inside the sanctum, hp 30 (`C1-09`) |

Drink 3 (3963, on the way out) gave the same timings, 10.3/12.6 and
41.4/43.7. The playable tiny window is therefore 28.4 s, and the crossing
took 1.6 s. The POTION bytecode confirms rule 5: `spawn 05AE:1FB9` (makeAvatarTiny)
with no `implies`, then `FREE::wait(0x7D0)` implied, then `spawn 05AE:21B8`. So
the 2000-tick wait now runs alongside the shrink. I could not compare against
the old build in this session.

`templeOpen` read 1. Drink 1 was wasted while I was making plates: the window
closed before the walk. That run is not counted, apart from its log lines.

**Altar, negative control.** The save has no shield in the pack. Walking into
the altar egg hatched `05A7:0080` and barked "I sense great power here, but I
lack the artifact needed for the ceremony." `godsFree` stayed 0 (`C1x-...`).

**Getting the shield.** I left through the crack with potion 3963, took trigger
210, and the walk-in hatched EggEndgame (`05AA:0080`) on the pad. With
`godsFree` 0 it returned and `endgameStarted` read 0 (negative control). I ran
`Item::grab 772` (weight 80 → 120), then took trigger 211 back. The breach was
open on re-entry: no `q: 307` wall pieces. I walked through it to the altar.

**Altar, real.** Hatched by a walk (`05A7`). Film at 0.55 s per frame, console
closed:

| t (s) | |
|---|---|
| 0.5 to about 11 | "I place the artifact upon the altar..." (`C1-10`) |
| about 15 to 32 | white (`C1-11`); on 09-26 the white came at 19 s, when the QUAKE3 spawn was waited on. It now starts earlier, as rule 5 predicts |
| 32 to 33.7 | fade in on Timyra |
| 33.7 to 36.5 | hold, Timyra breaks (`C1-12`) |
| 36.5 to 38.2 | **scroll** (consecutive frame diff 25-29) (`C1-13`) |
| 38.2 to 40.4 | hold, Felicitar (`C1-14`) |
| 40.4 to 42.0 | scroll |
| 42.0 to 44.3 | hold, Doloras (`C1-15`) |
| 44.3 to 45.9 | scroll back; snap at 47.0 (`setCenterOn(1)`) |
| about 48 on | "It is done. The Ancient Ones are free..." (`C1-16`) |

The holds after each scroll's arrival are 2.2-2.3 s, which is the full
`wait(145)`. A scroll that was not waited on would leave about 1.3 s, since
`wait(145)` would then start under the 0.75 s scroll. That is my evidence that the
pans are waited on. Afterwards: `godsFree` 1, gods 3993/10828/11428 at frames
4/5/3, and a walk moved the Avatar 200 units with `f: 0x2041`.

**Endgame.** Out by the breach and trigger 210. The arrival walk hatched `05AA`
at 0.34 s. Film at 0.65 s per frame, 150 s, console closed. Opening black about 2 s;
barks in order from 4 s to 101 s. The two closing barks, "And with the power
of the Ancient Ones now restored..." and "The Guardian's prison weakens. It is
time to go home.", each show as one page (`C1-17` to `C1-19`, zoom `C1-22`).
Black from 102 to 106 s, world from 107 s (`C1-20`, `C1-21`). The run is about
21 s shorter than 09-26 E4, which matches the reagent-bag bark that moved to
Ezrekal.

After: `endgameStarted` 1, `hasBag` 0. **Exactly one** EGGENDGA process:
`Process 6439 ... IP: 05AA:04EF`, the top-up. The hatch process itself had
ended, which is rule 5 (`spawn topUpReagents() -> return` no longer holds the
hatch). The Avatar walked 18432 → 18640.

**Bag.** At Ezrekal's stockade, a double-click (`event 1 @ 0474:0333`) opened a
menu of **I have freed your gods!**, **I would speak to you of Tyorvi.** and
**bye** (`C1-23`). Picking the first played "What a wonderful time this is!..."
(`C1-24`). Then `hasBag` read 1, bag 10904 (`q: 1`) was in the pack, and it held
six shape-395 stacks of 25: frames 0 (10947), 6 (10948), 8 (15001), 9 (15487),
10 (15729) and 14 (5761). Weight went 120 → 280.

**Negative control:** a second talk, the same option. She said "Yes yes! I
know! Wonderful it is... the bag I gave you..." (`C1-25`). Afterwards there
was still one `q: 1` bag, and `hasBag` was 1.

**Top-up.** I dragged frame-14 stack 5761 to the ground and set the slider to
10 (`SplitItemProcess splitting: 10: 15-10`). Reads of 5761 at wall times of
6, 18, 30, 43, 55, 67, 79 and 93 s were 15, 15, **20**, 20, **25**, 25, 25, 25.
The ground stack 5845 stayed at 10 throughout. Each read paused the game for
about 3 s, so the 25 came within about 37 s of game time (`C1-26`).

## C3: conversation exits, PARTIAL

**Ezrekal.** After the bag branch's `exitConvo`, she had `LoiterProcess 466` and
moved (12848, 12496) → (12848, 12400) in 5 s, and the Avatar walked 312 units.
After a third talk, I clicked **bye**. 3.3 s later she had `LoiterProcess 6321`,
a `PathfinderProcess` and an `ActorAnimProcess`, and the Avatar walked 208
units (`C3-ezrekal-after-bye.png`). The Avatar was never frozen.

Ingjald, Hrodny (and her **Tell me more of the cliffs.**) and Ragnar were not
run. Those need `cp22-hastea.sav`. Ingjald (112) and Hrodny (113) sat at their
slots, outside the fast area, in this world.

## C2, C4: NOT DEMONSTRATED

These were not reached before the request budget ran out. Setup for whoever runs them:
- C2: findShape 614 lists the plaques; the Message Scroll is shape 864, placed by
  `build_map_17.py`.
- C4: Aramina is on Map 40 in `cp22-hastea.sav` (wave-1 C2).

## C5: log hygiene

Whole session, 20,284 lines:

| Line | Count |
|---|---|
| `Non-existent process` | 0 |
| `stuck in process loop` | 0 |
| `Segmentation` | 0 |
| `Assertion` | 0 |
| `Cycle in paint` | 0 |
| `Unhandled intrinsic` | 288, made up of 96 each of 195 `Camera::getX()`, 196 `Camera::getY()` and 197 `Camera::getZ()` |
| `Skipping invalid shape` | 1 (the known `539,4` on load) |
| `segment 0000` | 0 |
| `Npc::getNpcSlot` | 0 |

96 = 3 drinks × 2 routines × 16 `move_to` calls.

## Findings

1. **FAIL-class defect from rule 1: while Tiny Tar shrinks or regrows, the
   camera jumps to world (0, 0) and the screen goes black for about 2.3 s.**
   - The `Camera::` spelling now compiles. `lv-patched/FREE.UNK:1395-1415`
     (makeAvatarTiny) and `:1434-1492` (makeAvatarBig) do
     `Camera::setCenterOn(0)`, then
     `Camera::move_to(Camera::getX(), Camera::getY(), Camera::getZ() ± 1, map)`.
   - In LVFREE (class 0x5AE) these are now real `calli 0xBE`/`0xBF`, and also
     `calli 0xC3/0xC4/0xC5` (e.g. 0x2120-0x216D, 0x23C7-0x2414). The U8
     intrinsic table has 0 in those slots (`u8_intrinsics.h`, the six `0, //U`
     after `I_moveTo`), so each call logs `Unhandled intrinsic` and returns 0,
     and `move_to` parks the camera at (0, 0, 255).
   - What the player sees: lightning, then black void, with any live bark
     drawn in the bottom-left corner (the crack hint's "Hrodny's dark potions
     are in my pack...", `C1-05`). The shrink and regrow animations are never
     seen. The view returns when `setCenterOn(1)` runs (`C1-06`, `C1-08`).
   - Before wave 2 these statements were dropped, so the camera stayed on the
     Avatar. The rule file `.claude/rules/camera-intrinsics.md` already warns
     that `getX`/`getY` are unusable under U8. Its "`Camera::` is dropped"
     section is now out of date.
   - `FREE.UNK:860-874` `changeRef` has the same `getX`/`getY` pattern
     (0x106A-0x1100). I did not trace whether it is reachable.
   - Confidence: high (bytecode, log, frames). Fix direction: write the
     shrink camera with `Avatar.getX()/getY()` and literal z, or drop those
     `move_to`s.
2. **Bark statements now wait (rule 3), so scene timings moved.** In
   makeAvatarTiny the shrink starts at about 10 s after the drink, behind two
   blocking barks. The altar white comes at about 15 s (12 s on 09-26 R2, 19 s on
   09-26 unbroken). No beat was lost.
3. **`run-s16-tinytar.sav` does not carry the shield in the pack.** The old-build
   save has it (772, frame 2) on the Sacred Circle. Anyone repeating C1 from
   this checkpoint needs `Item::grab 772` on Map 10, or a different checkpoint.
4. **The breach does open on Map 18 re-entry once `templeOpen` is 1**, so the
   sanctum is no longer sealed for a player who has run out of potions
   (09-26 finding 4 no longer holds).
5. `Npc::getNpcSlot` (item 116) logged 0 times across three Ezrekal talks.
   Earlier sessions logged three per talk, so something in wave 2 resolved
   that call.

## Harness anomalies

- A plain `Xvfb &` from the bash tool died at once, and ScummVM started anyway
  against no display. I killed it within seconds; it touched only the
  isolated config and saves. After that I ran Xvfb and ScummVM from the eval
  kernel with `start_new_session`.
- `-x 1` is a much better loader than intro skip plus `loadGame`, and it
  sidesteps the Devon-menu trap.
- Walk quanta of 60 to 104 units would not land in the crack's 32-unit column.
  I used two same-map teleports instead, both north and south of the crack and
  outside the TempleEntry egg's box.
- The empty bottle sits on top of the potion stack, and double-clicking it does
  nothing. Moving it aside inside the pack took two drags.
- `read` intermittently reported freshly written PNGs as missing; retrying
  worked.

## Disk changes

- New: this report and 28 plates in `docs/playtest-2026-10-07-wave2-c/`.
- Scratch in `/tmp/claude-1000/w2c/`: game copy, ini, saves (slot 1 = the
  checkpoint copy; ScummVM wrote `ultima8.000`, `timestamps` and history
  there), session log `lv_run.log`, driver `py/`, frames `sp/`, disassembly
  `dis/`.
- Not touched: `:77`, `shared/u8-lv-patched`, `~/.config/scummvm`,
  `~/.local/share/scummvm`, any source, builder, map, fork, TODO or HANDOFF.
  Nothing was committed. ScummVM, its stdin tail, and `Xvfb :79` are stopped.

# Single-build replay of the 1→18 run, leg 1: from a new game to step 1 done, then to the MYTHAUS hut door on Map 8 (2026-10-11)

This is leg 1 of a replay of the complete no-cheats run on **one pinned build**. Later legs continue from the banked saves on the same game copy. Do not re-copy it.

## Build pinned

- **Game copy.** `/tmp/claude-1000/replay/game` was copied once from `shared/u8-lv-patched` at 14:00, and its two `.bak` files were removed. The hashes are in `/tmp/claude-1000/replay/pinned.sha256`. All of them match `shared/build/ARTIFACTS.sha256`:

  | File | sha256 |
  |---|---|
  | EUSECODE | `4182e079245952870108870c2557c669a8ad45033f19b64cd4d4a5fb4107c4c7` |
  | FIXED (root and `STATIC/`) | `122b43740a0171ca87c94cb331159b99f541a401eea38ab523ef80faa7a35ded` |
  | U8SHAPES | `69fbd861…` |
  | TYPEFLAG | `6bdb3036…` |
  | ANIM | `77e9705d…` |

  The engine log reads `usecode/eusecode.flx: d00d0d5962e966129c2277c7cea7844b, 1526311 bytes`.
- **Binary.** `scummvm-lv/scummvm` (2026-10-11 04:17) was used as it is. Detection matched: the log shows `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and no `Couldn't identify`.
- **Harness.**
  - Xvfb `:95`, window at (480,300), `scale_factor=2`.
  - The ini (`/tmp/claude-1000/replay/scummvm.ini`) has no width/height keys, and the log reads `Setting Video Mode 320x200`. It sets `frameLimit=true`, `usehighres=false`, `mute=false` and volumes of 192, with `SDL_AUDIODRIVER=dummy`. Music was on.
  - The driver is `/tmp/claude-1000/replay/py/rp.py` + `navr.py`, which are part 7's `v7.py`/`nav7.py` re-pointed. Its prime left click now waits **0.6 s** before any right hold (traps.md).
- **New game.** The intro was skipped with Escape and the name typed. **Do not pass `--save-slot=1` with an empty save dir.** It printed `Starting New Game (slot 1)` and then the modal "Error running game: Reading data failed" (`sp/boot0.png`). Without the flag the new game started normally. This is a harness note.
- **Cheats: 0.** `Cheat` appears 0 times in `lv_run.log`. The console was used only for `objectInfo`, `getGlobal`, `debugflag_enable Object`, `saveGame` and `loadGame`. Every move, hop, door and menu pick was player input.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| Prologue: Devon, the execution egg, the guard's questions | **PASS (walked)**, in world 3 (worlds 1 and 2 died, harness, findings 1-2) | Devon: "Who are you?" in world 1, **Goodbye.** in worlds 2-3. EXCUTION egg `event 7 @ 0483:0080`, walked in south at (11615,5287,48). Guard: What just happened here? → I go by Avatar. → The beach. → To return home. Plates `ex_04`, `g1`, `s00-prologue-after-execution` |
| Map 3 gate guard → Map 40 | **PASS** | GUARD1 "I am Avatar." → "Bye" (`menu_stop`), then N → **Map 40 (13038,14586)**. The AVATAR detour fired (`Loading Fixed items in map 0`, once) |
| Map 40 → Map 39 (id-0 gate) | **PASS** | (10810,14094) → W → **Map 39 (18834,14070,48)** |
| **Step 1: LB egg via the tunnel lane** | **PASS** | Route through the canal side and the tunnel to (17086,19954). Walking N fired `05AF`, and the apparition's speech played (`s01-lb-apparition`). Afterwards `[0405]=1` (lbSpoke), `[06A5]=1` (lbStarted) and `[06A6]=1` (lbDone) (`s01-lb-flags`) |
| Map 39 → east gate → Map 40 | **PASS after 1 reload** (finding 4) | One drop into the canal bed at (15642,17608,z8); I reloaded. The retry used short legs via (15959,18343) → (15535,17911) → (15082,17918). Then E → **Map 40 (10810,14094)** |
| Map 40 palace → Map 7 | **PASS** (finding 5) | Door 1 (shape 227 pair) opened by double-click. Door 10003 (12159,7199) took `event 1 @ 0045:0098` on the second double-click and became DOOR_NS f2, but the gap it leaves is narrow (finding 5). Door 3 was passed. N on x≈13140 → **Map 7 (15071,25967,8)** |
| Map 7 → Map 8 | **PASS on the third line; 2 deaths** (finding 6) | Death 1: a Torax (shape 120) took hp 30 → 3 → 0 at the barn (12335,23431). Death 2: hp 30 → 0 at (10171,19719) while my route planner ran with the world live. The pass was one held-run "blast" (10 s, no reads) to (9943,19987). The cave mouth needs y≈19700-19790 at x 9795 (finding 7). **Map 8 (31295,19135,0)** |
| Map 8 pool: 7 targeted hops + strip | **PASS after 2 drownings** (finding 3) | 2399 → G 7788 → H 2615 → I → J 3172 → D → E → strip shape 301 (29679,22379,8). hp 30 |
| Strip → trench (engine-void detour) | **PASS** | `pathfind.py --water-margin 32 --engine-void`, 16 waypoints, hp 30, → (29855,23627,0) |
| Trench → gate trigger → plateau | **PASS, by walking** (finding 8) | A plain walk E at (29263,30443,0) fired the trigger. No jump was needed: (14590,11210,48) |
| Plateau → MYTHAUS hut door | **PASS, hp 30** | Shroom-avoiding waypoints (14039,11991) → (14039,12959) → (14127,13415) → (14127,14175) → (14199,15134). Stopped at the door, (14162,15166,48) (`hutdoor4`) |
| Step 2 (Mythran) and later | **NOT DEMONSTRATED** (budget) | — |
| Music on | **PASS (no hang)** | 75 min of play with music unmuted. 2 `MIDI` lines; the console answered throughout |
| Log hygiene (`replay/lv_run.log`, 26,865 lines, worlds 1-3) | **PASS for LV code** | 0 each of `Unhandled intrinsic`, `stuck in process loop`, Segmentation, Assertion. 3 `Non-existent process PID (0) in implies` at lines 2541-2544, in the prologue (the known Devon/retail family). 222 `Cycle in paint`: 218 are `476 -> 580 -> …` and 4 are `321 -> 476`, both retail shape pairs and not LV art. Where they occur was not traced |

## Findings

1. **The camp fire hurts more than the 10-08 report says, and routers walk straight through it.**
   - **Why the router does it.** The Avatar starts at (14527,5887,8), only 128 east of CAMPFIRE 1890 (shape 267, (14399,5855,8)), so a westward route crosses it.
   - **What it cost.** World 1 lost hp 30 → 14: five `event 6 @ 010B:00E2` hits while the walker stalled beside the fire.
   - **The fix.** A forbid box of −260/+100 in x and −260/+250 in y clears it.
   - **Classification.** Retail.
2. **The execution egg takes the mover, and a held run then walks the Avatar off the dock to drown.**
   - **What happened.** World 2 hatched EXCUTION (`0483`) mid-run. The run kept going, and the Avatar drowned on CLRWATER 1870/1876 (`015B:0080`).
   - **The rule.** Approach the egg in short presses and stop on the first `0483` line.
   - **Classification.** Harness, not LV.
3. **A pool hop needs SPACE held about 0.6 s, with the cursor on the stone's top face.**
   - **What does not work.** A tap (`xdotool key space`) only sometimes jumped: one tap jumped, but several taps did nothing.
   - **The aim.** With 320×200 ×2, the top face of a 96×96 stone draws about **+19 px** below `proj(anchor − 48, z 8)`. Aiming at the raw projection traces onto the stone's near edge.
   - **The two drownings.** Both came from aims at (137,315) and (115,311), which put the landing on the near edge or in water. The second probe also logged CLRWATER 14493.
   - **The range limit** is `str × 32` per axis from the Avatar's centre (`u8_avatar_mover_process.cpp:751-765`; str 15 gives 480). A miss outside the top face makes him shake his head.
4. **The Map 39 canal drop is still there off the walked line.**
   - **What happened.** A NW leg from (15702,18138) dropped the Avatar to (15642,17608,8) in the canal bed. From there `exact_reach` finds no route back (erode 0 or 1).
   - **The fix.** Stay on x ≤ 15282 for y 17536-17918, with legs ≤ 0.9 s.
   - **Classification.** This is lane-doc finding 2 again. Retail, low severity.
5. **Palace door 10003 (12159,7199): when open, it leaves about a 32-unit window for the Avatar's x.**
   - **The geometry.** The open DOOR_NS (shape 68, footpad 1×4) sits in the east 32 of the 128-wide doorway. The wall pieces are at x 12031 and 12191.
   - **What I saw.** North was refused at x 12038, 12142, 12150 and 12246. It walked at x **12118**.
   - **Effect.** A player will feel it as a sticky doorway.
   - **Classification.** Retail.
6. **Map 7 is still lethal, and the world runs while the harness thinks.**
   - **The Torax.** A pair of Torax (shape 120, items 112/113), hatched by MONFAST eggs (`04BB`), did hp 30 → 3 in one 3 s burst at the barn.
   - **The bad save.** A save taken 6 s after an hp-30 read loaded at **hp 1** (`sp/w3-m7-mid.sav`). Saves can capture a mid-fight state. Read hp right before saving, not before planning.
   - **What worked.** Precompute the whole route, then run it as held legs with no reads (`blast`).
7. **The Map 7 → Map 8 cave mouth (trigger (9498,19702), range 66) is narrow.**
   - At x 9795, W is refused at y 19671, 19827 and 19903. It went through from **y 19703**.
   - The route models end at y 19767 and call the trigger cell itself unreachable.
8. **The Map 8 gate-wall trigger fired on a plain walk east into the wall at (29263,30443,0).** Part 1's "Up then SPACE" was not needed. My follow-up keyboard Up+SPACE then sent the Avatar **north on the plateau into the return trigger** (14540,11004 ±96), and he landed back at (29375,29703,0).
   - **The rule.** After the walk-in, read the position before any further input.
   - **Not a defect.** It is a trap for a scripted player, since both triggers work as designed.

## Harness anomalies

- **The first mouse press after a console close is usually dropped.** So are runs under about 0.7 s. My `gom` loop counts no-move rounds and lengthens the first leg.
- **Distinguishing "turned" from "jumped".** A screen diff over 8 (mean abs) separates them. Use it instead of a console read.
- **`menu` detection by red pixels also matches red NPC barks** (GUARD1's "I -really- do appreciate your plight").
- **Route computation of 10-60 s runs with the world live.** That caused death 2. Plan before loading, or use cached `er_*.pkl`.

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `replay1011-s00-prologue-after-execution.sav` | `421b0f02` | Map 3 (11679,6031,48), hp 30, after the execution and its questions |
| `replay1011-s01-m39-lb-done.sav` | `b52c0240` | Map 39 (17026,19798,48), lbSpoke/lbStarted/lbDone 1 |
| `replay1011-s01b-m8-plateau-pad.sav` | `9893fa1a` | Map 8 plateau pad (14782,11298,48), hp 30 |
| **`replay1011-s01c-m8-mythaus-hut-door.sav`** | `cda74665` | Map 8 (14162,15166,48) at MYTHAUS DOOR_NS 7820 (14079,15167), door still closed, hp 30. **Leg 2 resume point** |

Scratch saves are in `/tmp/claude-1000/replay/sp/w3-*.sav`, one at every waypoint (the m39 tunnel, m40 corridor, m7 near-trigger, each hop, trench, gate and so on). **`w3-m7-mid.sav` is hp 1; do not use it.**

## Resume (leg 2)

1. **Start.** Use the same `/tmp/claude-1000/replay/game` and ini, and the same Xvfb `:95` recipe. Copy `replay1011-s01c-…` to `saves/ultima8.001`, start with `--save-slot=1`, and send `debugflag_enable Object`.
2. **The door.** DOOR_NS 7820 is right beside the Avatar, at screen (290,165) on `hutdoor4`. Double-click it; the first click after a console close tends to be a look only. Then walk west at **y 15134**, where the egg fires inside the doorway (part 1 finding 5). You land on the island at about (6078,1786,0); stop and re-aim west.
3. **The walkway.** At y 1818, run bursts that stop only at x≈5494 and x≈4710, then x 4326, then walk to pad 4 (part 2 finding 1). Then go W at y 1816 → (1904,1816) → N (1904,1688) → the stair → (1832,2056,48) upstairs.
4. **Mythran (step 2).** Picks: Lord British says they can help me. → Who searched for the Zealans? → What happened to him? → Where are these double doors? → How do I open the doors? → Farewell.
5. **After that.** Follow parts 2-7. Map 8 north (spitters, shape 808s) is the next hard leg: cross each spitter zone in one held run under 3.3 s, then arrive from Map 9 via T200 so the 808 pair does not respawn (part 4).

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-replay-leg1/` (14 plates).
- **Wrote** the 4 checkpoints above in `~/lv-checkpoints/`.
- **Scratch** in `/tmp/claude-1000/replay/`: the pinned `game/`, `pinned.sha256`, `scummvm.ini`, `saves/`, `sp/`, `py/`, `lv_run.log`, `trace.txt` and `er_*.pkl`.
- **Stopped:** my ScummVM and Xvfb `:95`.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and the binary.

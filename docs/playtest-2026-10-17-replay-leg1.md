# Single-build replay of the 1→18 run, leg 1: from a new game to step 1 done, then across Map 8 to the MYTHAUS island (2026-10-17)

This is leg 1 of the replay on today's build. Later legs continue from the banked saves on the same game copy. **Do not re-copy it.** The 10-11 replay (`docs/playtest-2026-10-11-replay-leg1.md`) was the model.

## Build pinned

- **Game copy.** `/tmp/claude-1000/replay1017/game` was copied once from `shared/u8-lv-patched`, and its two `.bak` files (`STATIC/FIXED.DAT.bak`, `USECODE/EUSECODE.FLX.bak`) were removed. The hashes are in `/tmp/claude-1000/replay1017/pinned.sha256`. All of them match `shared/build/ARTIFACTS.sha256`. `sha256sum -c` gave OK for all six files at the end of the session.

  | File | sha256 |
  |---|---|
  | EUSECODE | `2e3b71c24f3aac38736512736627506b6ac33e940b6345c273c63a37a4ccd5e3` |
  | FIXED (root and `STATIC/`) | `8db11ee35c1f0c1c247785568fa6d01f11a6cced54122b3d012b0eda480698c9` |
  | U8SHAPES | `efb16af1…` |
  | TYPEFLAG | `d26d1531…` |
  | ANIM | `696dbeb9…` |

  The engine log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: 84615e29d097543ed69da844fbc3948f, 1528891 bytes`. There is no `Couldn't identify`.
- **Binary.** The text-console build `scummvm-lv-console/scummvm` (2026-10-17 10:28) was copied once to `/tmp/claude-1000/replay1017/bin/scummvm-console`, sha256 `d371f7cecb6a3abff93bc2c968f13a4c9441fae201ce3b797bc85d926c25cbe3`. Its debugger reads stdin, and every reply lands in the log.
- **Harness.**
  - Xvfb `:95` (1280×800), with the window at (480,300).
  - Ini `/tmp/claude-1000/replay1017/scummvm.ini`: 640×400, `usehighres=true`, `scale_factor=1`, music on (volumes 192, `SDL_AUDIODRIVER=dummy`). Saves go to `/tmp/claude-1000/replay1017/saves`, and the log is `/tmp/claude-1000/replay1017/lv_run.log`.
  - Driver: `/tmp/claude-1000/replay1017/py/` (see **Harness** below).
- **Cheats: 0.** `Cheat` appears 0 times in `lv_run.log`. The console was used only for `objectInfo`, `findShape`, `getGlobal`, `debugflag_enable Object`, `saveGame` and `loadGame`. Every move, hop, door and menu pick was player input.
- **Deaths: 3. Reloads: 4** (one of them a new game).
  1. **Harness.** At the very start, a speed-calibration run S walked the Avatar into the camp's water (CLRWATER `015B:0080`). No save existed yet, so this was a new game.
  2. **Finding 1.** At the MYTHAUS hut door, a Torax hatched on the plateau took hp 30 → 0 and knocked the Avatar 280 south.
  3. **Finding 1.** The save banked at the door had captured the hit in progress: it loaded at hp 20 with the Torax adjacent, and the Avatar died about 10 s later.
  4. The fourth reload was the island landing (hp 22), after the sphere traps took hp to 10 (finding 2).

## Outcome

Step 1 is complete. The furthest point is **Map 8, the MYTHAUS island landing (5962,1766,0), at hp 22**, inside the hut teleport. Step 2 (Mythran) was not reached in this leg's budget.

## Verdicts

| Step / segment | Verdict | Evidence |
|---|---|---|
| New game, intro skip, Devon | **PASS** (world 2; finding 4) | Devon: "Who are you?" in world 1, **Goodbye.** in world 2. No `--save-slot` was passed |
| Prologue: the execution egg and the guard | **PASS (walked)** | `Item 2481 (shape 73) … event 7 @ 0483:0080`, egg at (11732,5844,48), range 11,11, walked in from the north. Guard: What just happened here? → I go by Avatar. → The beach. → To return home. Plates `s00a`, `s00b`, `s00c`. Bank `s00` hp 30 |
| Map 3 gate guard → Map 40 | **PASS** | GUARD1 "I am Avatar." → "Bye" (`s00d`), then N → **Map 40 (13038,14938,48)** |
| Map 40 → Map 39 | **PASS** | Teleporter (10506,14070) → **Map 39 (18930,14070,48)** |
| **Step 1: LB egg via the tunnel lane** | **PASS** | The lane route ran down the canal side at walk gait, keeping x ≤ 15290 for y 17450-17960, then through the tunnel (16167,19583→19983), then E along y 20050. The egg (17150,19700) q 304 fired at (17122,19694): `@ 05AF`. The apparition spoke (`s01a`). Afterwards `[0405 01] = 1`, `[06A5 01] = 1` and `[06A6 01] = 1` (lbSpoke, lbStarted, lbDone; plate `s01b`, scene end `s01c`). Before the scene all three read 0 |
| Map 39 → east gate → Map 40 | **PASS**, no canal drop | Back through the tunnel at walk gait, then a run to (19500,14072) → **Map 40 (10882,14022)** |
| Map 40 palace → Map 7 | **PASS** | DOOR_EW 29569 (12287,9215): `event 1 @ 0045:0098`. DOOR_EW 29533 (12159,7199): opened; north passes at **x 12114** (the 10-11 finding 5 window). DOOR_NS 29532 (12287,6975): `0044:0098`. Then N on x 13042-13306 → **Map 7 (14787,25955,8)** |
| Map 7 → Map 8 | **PASS, 0 deaths, hp 30** | Distance-field run W along y 25935, then N, NW, W and N to (10175,19823). The cave mouth needs y ≈ 19700: walk N to (9803,19699), then run W → **Map 8 (31295,19135,0)**. No Torax contact |
| Map 8 pool: 7 hops + strip | **PASS first try, 0 drownings, hp 30** | Stones 2399 → G → H → I → J → D → E (shape 780), each landing at the exact centre. Then shape 301 item 12119 (29695,22399,8) → (29677,22377,8). Aim: `proj(anchor−48, z 8) + 20 px` in 640×400 (finding 5). Plate `s01d` |
| Strip → trench → gate trigger → plateau | **PASS, but the gate needed a jump** (finding 3) | The engine-void field went to (29745,23677,0), then (29277,30401,0). Five walk-ins E would not fire teleporter (29407,30335) q257; keyboard Up+SPACE did → **(14687,11210,48)**. Bank `s01b` |
| Plateau → MYTHAUS hut door | **PASS on the second try; 2 deaths** (finding 1) | Torax 143 (shape 120). A run from the pad got there at hp 30, and the door DOOR_NS 30967 (14079,15167) opened (`0044:0098`) |
| Hut door → island | **PASS** | Walk W through the doorway → island (5962,1766,0) at hp 22 (the Torax hit as he went in) |
| Island walkway → stair → **step 2 (Mythran)** | **NOT DEMONSTRATED** (budget; finding 2) | Shape-264 spiked spheres took hp 22 → 10 at (5945,1813) while the Avatar was wedged by the post. I reloaded the landing |
| Music on | **PASS (no hang)** | The console answered throughout |
| Log hygiene (`lv_run.log`, 18,979 lines) | **PASS** | 0 each of `stuck in process loop`, Segmentation, Assertion, `Unhandled intrinsic`, ERROR and `Cheat`. **3** `Non-existent process PID (0) in implies`, in the prologue (the known Devon/retail family, as on 10-11). **2** `Cycle in paint`, both `301 -> 1` (the pool strip tile against the Avatar while he stood on it) |

## Findings

1. **Severity: high for a player, low for the build.** A Torax (shape 120), hatched on the Map 8 plateau, waits at the MYTHAUS hut door and kills a player who stops there. It is not a blocker.
   - **The monster.** Actor 143, `uc: TORAX`, at (14232,15107,48), hp 21 (`objectInfo 143`).
   - **Where it comes from.** The retail Map 8 FIXED places three Torax monster eggs on the plateau: (13320,11528), (14623,12447) and (15391,13183), quality 14456/12408, shape 120. The nonfixed MONFAST eggs (`04BB`) hatch them on enterFastArea. On 10-11 the same walk met none.
   - **The deaths.** Death 2 came about 20 s after arriving at the door. A FIRESHRO (794) `event 6 @ 031A` burst came first, then the knockback: (14147,15110) → (14147,15390), hp 0.
   - **Bad save.** The save banked 1 s after an hp-30 read loaded at **hp 20**, with the Avatar displaced to y 15174. It had caught the hit in progress, as on 10-11 (finding 6). That bank was deleted, and the resume save below replaces it.
   - **What worked.** Run straight from the plateau pad. On arrival, double-click the door at `proj(14063,15103,72)+20` without probing. Then walk W at once.
   - **Repro.** `replay1017-s01b-m08-plateau-pad.sav`, then walk to (14199,15170) and wait.
   - **Classification.** Retail placement. It is now lethal on the LV quest route. Consider moving the eggs or pre-placing a weapon.
2. **Severity: medium. Not a blocker yet.** On the MYTHAUS island landing, shape-264 spiked spheres (`event 5 @ 0108:00B0`) hit the Avatar on the lane itself, not only on the y ≈ 1986-2014 rows.
   - **The wedge.** The Avatar arrives at (5962,1766), against the post that 10-11 leg 2 described. From there W is refused, and a mag-75 walk S moves 128 units to y 1894.
   - **What happened.** Three presses took hp 22 → 17 → 9 at (5962,1830)/(5945,1813) (plate `F2`).
   - **Not settled.** Whether a faster first move escapes it is untested. Leg 2 must solve it (see Resume).
3. **Severity: low.** The plateau gate teleporter (29407,30335,0), q 257, npcnum 0x45, did not fire on a plain walk E. That contradicts 10-11 finding 8.
   - **Why.** Its hatch box starts at x1 = 29407 − 4·32 = **29279** (`egg_hatcher_process.cpp`), and the wall stops the Avatar at **x 29277**. Five walk-ins E/SE/NE all stopped there.
   - **What worked.** Face E with a short mouse walk, then keyboard `Up` + SPACE held 0.35 s. The jump carries him into the box, and he landed at (14687,11210,48). Plate `F3`.
   - **Classification.** A 2-unit miss, so it depends on luck. A player who only walks is stuck. Widen the egg's x range by 1 (to 0x55) or move it 32 west.
4. **Severity: harness.** The `--save-slot` trap was avoided by launching the new game without the flag. The first death was a calibration walk S from the start point, straight into the camp water. Never calibrate toward the shore.
5. **Aiming in 640×400 highres.** A world point draws at `(320 + (dx−dy)/4, 200 + (dx+dy)/8 − dz + 20)` from the Avatar (the `+20` is the traps.md constant). The pool hops worked first try with the cursor on the stone top `proj(anchor−48, z 8)+20` and SPACE held 0.6 s, repeated until the screen diff exceeds 8. That took 1-2 holds per stone.

## Harness

Everything is in `/tmp/claude-1000/replay1017/py/`; reuse it. From the eval kernel:

```python
import sys; sys.path.insert(0,'/tmp/claude-1000/replay1017/py'); import lv, rnav as nav, follow as FW
```

- **`lv.py`**: session, console, input and projection.
  - `start(log=…, slot=None)` launches Xvfb `:95` plus the pinned binary, with stdin = `tail -f cmds.txt`. `stop()` and `stop_all()` shut it down.
  - `q(*cmds)` runs: chord attach (waits for `Debugger entered`), each command (waits for a `debug>` prompt), then `exit`. It sends no `exit` after a closing command: `teleport`, `loadGame`, `saveGame`, `toggleCombat`, `heal`. If a stale `exit` closed the console before a command ran, it re-attaches so the queued command runs. The world is paused while attached, so reads cost no game time.
  - `pos()` returns `{x,y,z,map,hp,weight}`.
  - `run([(dir,secs),…], mag)` is one right-button hold. A mag of 240 or more runs, 75-110 walks, and 60 or less does nothing.
  - Also: `click`, `dclick`, `shot`, `grab`, and `proj(wx,wy,wz)` (add 20 to y).
- **`rnav.py`**: routing over the pinned FIXED/TYPEFLAG.
  - `get_er(map, roi, forbid=[boxes], void, water, hurt_margin)` builds exact_reach plus DryReach, with HURT_SHAPES and forbid boxes.
  - `Field(er, goal, erode)` is a BFS distance field from the goal. `Field.best(x,y,z)` gives the 8-direction ray that most lowers the geodesic distance.
- **`follow.py`**: `FW.follow(map, Field, tol, rounds, maxsecs)`, the follower used for every walked leg.
  - Each round: read pos, take `best()`, then a 0.12 s prime press at mag 60 (it absorbs the press dropped after a console close), then the main hold.
  - Gait: run if the ray is 400 units or more, else walk. Speeds: run 600 straight / 460 diagonal per axis; walk 300 / 230.
  - Unstick after 3 still rounds.
- **Constants.** Run speed is about 600 u/s straight, and the hold needs about 0.25 s to start. Menu rows are found from red-pixel rows; click with a mousemove, a 0.4 s settle and a 0.25 s hold.

## Checkpoints (all new; nothing overwritten)

| Name | md5 | State |
|---|---|---|
| `replay1017-s00-m03-prologue-after-execution.sav` | `9c56fc1e` | Map 3 (11679,5999,48), hp 30, after the execution and the guard |
| `replay1017-s01-m39-lb-done.sav` | `d6f29748` | Map 39 (17122,19694,48), hp 30, lbSpoke/lbStarted/lbDone = 1 |
| `replay1017-s01b-m08-plateau-pad.sav` | `7c6ef23d` | Map 8 plateau pad (14687,11210,48), hp 30 |
| **`replay1017-s01c-m08-island-landing-hp22.sav`** | `160e1ad1` | Map 8 MYTHAUS island landing (5962,1766,0), **hp 22**, against the post. **Leg 2 resume point** |

Scratch saves are in `/tmp/claude-1000/replay1017/sp/w2-*.sav`: m39 canal, m40 corridor, m7 arrival, m8 arrival, shore, each hop, strip, trench, gate and island landing. A `replay1017-s01c-m08-mythaus-hut-door` bank was written and then **deleted**, because it held a mid-hit state (finding 1).

## Resume (leg 2)

1. **Load.** Use the same game copy, ini and binary. Copy `~/lv-checkpoints/replay1017-s01c-m08-island-landing-hp22.sav` to `/tmp/claude-1000/replay1017/saves/ultima8.001`. Start with `lv.start(slot=1)`, or start and then `Ultima8Engine::loadGame 1`. Then `debugflag_enable Object`. Check `sha256sum -c pinned.sha256` inside `game/` first.
2. **State.** Map 8 (5962,1766,0), hp 22. The inventory is the starting backpack only, weight 20. Step 1 is done, step 2 is not.
3. **Move at once on load.** The spheres (shape 264) start hitting within seconds. Plan the first press before loading.
   - **Option A.** Run S/SW off the post first. A mag-75 S walk moves 128 units; 0.3 s at mag 70 may give the y 1818 lane. Then hold a W run, without stopping, to x ≈ 5494 → 4710 → 4326. Leg 2 of 10-11 did that at hp 30.
   - **Option B.** If the landing keeps wedging, go back through the hut teleport and come in again for a fresh landing (6078,1786).
4. **Then.** Pad 4 (4094,1794) → (2944,1816). W at y 1816 → (1904,1816) → N (1904,1688) → the stair → upstairs (1448-1832, 1632-2056, 48). Talk to Mythran (NPC 33); 10-11 used the picks: Lord British says they can help me. → Who searched for the Zealans? → What happened to him? → Where are these double doors? → How do I open the doors? → Farewell. Check `[0717]`-`[071B]` = 1.
5. **After step 2.** Island exit → plateau (14138,15118). **The Torax from finding 1 may still be there.** Then the west corridor along y 13382 → T26 → north pad → spitters → the doors chamber.
   - **Note:** trigger 212 is now gated on allColumnsDestroyed. The 10-11 "T212 → 213 round trip that despawns the 808 pair" is therefore no longer available. Plan step 3's 808 encounter without it.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-17-replay-leg1/` (13 plates: `s00a`-`s00d`, `s01a`-`s01g`, `F1`-`F3`).
- **Wrote** the 4 checkpoints above in `~/lv-checkpoints/`. One more bank was written and then deleted (finding 1).
- **Scratch** in `/tmp/claude-1000/replay1017/`: the pinned `game/`, `pinned.sha256`, `bin/`, `scummvm.ini`, `saves/`, `sp/`, `py/`, `lv_run.log`, `trace.txt` and `cmds.txt`.
- **Stopped:** my ScummVM and Xvfb `:95`.
- **Not touched:** source, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, and the repo binaries.

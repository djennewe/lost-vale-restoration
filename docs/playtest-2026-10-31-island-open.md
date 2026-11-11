# Playtest 2026-10-31: screen13's island left open under the floating cloud

This is a short in-engine check of one Map 13 change. Douglas chose (2026-10-31) to leave screen13's island open under the floating cloud. Phase E had curbed off the island cells where the cloud (z 216, no roof flag) draws over the Avatar. Those curbs are removed in `agents/map-populator/src/build_map_13.py` (uncommitted).

**Build under test.**
- Artifacts: TYPEFLAG `e25d7224`, U8SHAPES `2b274856`, ANIM `97ae5fc9`, EUSECODE `b47c324c` and **FIXED `fc92ee5f`**.
- `shared/build` `sha256sum -c ARTIFACTS.sha256`: all OK. `shared/u8-lv-patched` held the same five artifacts, with FIXED in both places, plus `u8monsters.ini` `0642d689`.
- Game directory: a pinned copy at `/tmp/claude-1000/island1031/game`. Binary: a copy of `scummvm-lv-console/scummvm`, `e0518ced…`, the same binary phase E used.
- `sha256sum -c pinned-start.sha256` was OK at the end for all eight pinned files: five artifacts, top-level FIXED, `u8monsters.ini` and the binary.
- Display: Xvfb :95.

**Harness.**
- Play: the phase E `lv.py` / `rnav.py` / `follow.py` drivers, copied and repointed at the pinned copy. Text console, 640×400 with `usehighres`. Movement was the walk gait. Edge pushes used the run gait (mag 240, 1.5 s).
- Shots: `vignette_capture.py`, run from a scratch repo shell whose `shared/u8-lv-patched` is a symlink to the pinned copy. There was no `shared/build` beside it, so the sync was a no-op.
- Not run: no rebuild, no estate run, no commit.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| C1 | The Avatar walks from the turn onto the formerly closed cells, is hidden by the cloud there, walks back out without wedging, and the island's outer edge still holds | **PASS.** He walked from the turn into **23 of the 75 formerly closed cells**, among them the core (46,14) and the three far edges: the east tip (54,15), the south-east (49,20) and the north-east (51,12) (`C1-o`). Under the cloud he is hidden: wholly at (46,14), all but a foot at (47,15), legs only at (49,20) and head only at (44,13) (`C1-b`, `C1-i`, `C1-e`, `C1-j`, crops `C1-n`). He walked back out to the turn twice (`C1-k`, `C1-m`). Every move displaced him, z stayed 120 and hp stayed 30. Idle `event 18` at (46,14) was 9 in 20 s, against 15 in 20 s at the turn: no spam. **Negative control:** 12 pushes against the outer edge at the three far edges. All 12 ended on the island, at z 120, on Map 13 (table below) |
| C2 | screen13 still captures at ≥ 97 in-engine | **PASS.** 97.02 class / 96.49 rgb in both passes, which were byte-identical (`C2-a`). The raw capture is pixel-identical to phase E's pass 1 (10-30). The change touched only the island's invisible curbs, and none of them is in the frame |
| C3 | The climb route still runs: the turn → north leg → pad 208 area (walk) | **PASS.** He walked from the turn (5184,1728,120) S down the north leg to (5080,2296,120), 40 units from pad 208 (5119,2303) (`C3-a`). Then he walked back N to the turn. No trigger hatched on the way |
| C4 | No `Cycle in paint` with the Object channel on while walking under the cloud | **PASS.** The play log (`Enabled debug flag 'Object'` and `'Actor'`, 3178 `calling usecode` lines) has **0** `Cycle in paint`. It also has 0 Assert, 0 ERROR, 0 `Non-existent process`, 0 `Unhandled intrinsic`, 0 Segmentation and 0 `stuck in process loop`. Both capture-session logs also have 0 `Cycle in paint` |

## C1: the island under the cloud (PASS)

**Setup.**
- Save: phase E's scratch save `E1-turn-hp30`, at the turn (5200,1728,120), hp 30.
- It holds the old Map 13 fixed items, so I hopped maps to reload the new FIXED. `Cheat::toggle` on, teleport to Map 10 (7234,23218,8), teleport back to Map 13 at the turn (5200,1728,120), `Cheat::toggle` off.
- The log shows `Unloading Fixed items from map 10` → `Loading Fixed items in map 13` (`C1-a`).
- No teleport went onto the island. Every island position below was reached on foot from the turn.

**The cells.**
- The builder's walk with the curbs removed covers 134 island cells. The HEAD version (`git show HEAD:…/build_map_13.py`, run against the same field) walked 59 of them. The **75** newly walkable cells are phase E's 73 closed cells plus the 2 south-east-rim cells beyond them that had been out of reach.
- Offline, on the pinned FIXED/TYPEFLAG (`rnav` exact reach from the turn, step 8):
  - all 75 cells are reachable;
  - the reachable set holds no lattice point outside the island and the climb, and no level other than 112-120.
- In-engine visits are listed below and marked with white dots in `C1-o` (red = formerly closed, green = open before, grey = climb, yellow = push tracks).

| Stop | Position | Cell | Under the cloud | Plate |
|---|---|---|---|---|
| core | (5892,1900,120) | (46,14) | wholly hidden | `C1-b` |
| east tip | (6924,1988,120) | (54,15) | visible (beside the gold corner) | `C1-c` |
| south-east edge | (6352,2576,120) | (49,20) | legs only showing under the lower patch | `C1-e` |
| north-east edge | (6560,1608,120) | (51,12) | visible | `C1-g` |
| core | (6120,2000,120) | (47,15) | hidden but for one foot | `C1-i` |
| west core | (5688,1728,120) | (44,13) | head and shoulders above the upper patch | `C1-j` |
| out | (5184,1728,120) | (40,13) turn | — | `C1-k` |
| core again | (5944,1848,120) | (46,14) | wholly hidden | `C1-l` |
| out again | (5212,1716,120) | (40,13) turn | — | `C1-m` |

Three of the six stops sit under the cloud far enough to be hidden whole or nearly so. Edge cells such as (54,15) and (51,12) had been closed by phase E's conservative rule: a cell closed if the outline anywhere in it met the cloud, plus 2 px. He stands in them in full view.

**Wedge check.**
- Every follow round that pressed toward a goal moved him. The repeats in the trace are the driver's own prime press plus overshoot around a 40-unit goal tolerance, not refusals.
- Idle `event 18 @ 0401:3477` over 20 s: 15 at the turn (open climb cell) and 9 at (46,14) under the cloud. Both are the same idle trickle, not the stuck-mover spam.

**Edge pushes (negative control).** Run gait, mag 240, 1.5 s, each from a standing start:

| From | Push | End | End cell |
|---|---|---|---|
| (6924,1988) (54,15) | E | (7028,1988) | (54,15) |
| (6932,1988) (54,15) | NE | (7036,1988) | (54,15) |
| (6940,1988) (54,15) | N | (6940,1988), no move | (54,15) |
| (6940,1988) (54,15) | SE | (6996,2044) | (54,15) |
| (6944,1984) (54,15) | S | (6404,2524) | (50,19), slid SW along the rim |
| (6352,2576) (49,20) | S | (6352,2680) | (49,20) |
| (6352,2576) (49,20) | SE | (6384,2680) | (49,20) |
| (6324,2620) (49,20) | E | (6388,2684) | (49,20) |
| (6328,2624) (49,20) | SW | (6120,2936) | (47,22), an island cell |
| (6560,1608) (51,12) | N | (6560,1608), no move | (51,12) |
| (6560,1608) (51,12) | NE | (6624,1608) | (51,12) |
| (6536,1608) (51,12) | E | (6640,1608) | (51,12) |

- Each push stopped inside its cell's far boundary: x ≤ 7039 at the tip, y ≤ 2687 at (49,20), and x ≤ 6655 with the north side flush at (51,12).
- The two long moves, S from the tip and SW from (49,20), slid along the island's stepped south-east rim and stayed on island cells.
- No push changed z (120 throughout) or map (13), and hp stayed 30.

## C2: screen13 capture (PASS)

- Two passes of `vignette_capture.py … screen13`, each in a fresh session. Avatar spot (6747,2331,216), on the floating cloud.
- Both passes: class **97.02%**, rgb 96.49%. The two `screen13_ingame.png` files are byte-identical (`C2-a`).
- The raw capture differs from phase E's 10-30 pass-1 raw by 0 px (230 px against its pass 2).

## C3: turn → north leg → pad 208 (PASS)

- Walked from the turn (5184,1728,120): S 576 along the north leg, then settled to **(5080,2296,120)**, beside pad 208 at (5119,2303,120) (`C3-a`).
- I walked back N up the leg to the turn area, (5264,1720,120) in the island's first open cell (41,13), then onto the island again for the second C1 round.
- The log shows no `event 7` and no harpie hatch on this leg. The only egg activity on Map 13 is `event 16 @ 0481` on harpie triggers 26922 and 30927. That is not a hatch.

## C4: paint cycles (PASS)

- Play log `lv_I1.log`: 0 `Cycle in paint`. The Object and Actor channels were enabled after the save load, and they persisted: `calling usecode` lines run to the end of the log.
- It also has 0 Assert, 0 ERROR, 0 `Non-existent process`, 0 `Unhandled intrinsic`, 0 Segmentation and 0 `stuck in process loop`.
- Capture-session logs (`lv_run.log`, `all_sessions.log`): 0 `Cycle in paint`.
- No positive control was run: no older-build knot spot lies on this route.

## Findings

**F1. Some formerly closed cells were never hidden spots.** Severity: info.
- (54,15) and (51,12) show the Avatar whole.
- Phase E's closure took the 64×64×40 box outline plus 2 px, at any 16-unit position in the cell, so cells that only graze the cloud's rim closed too.
- With the curbs gone this changes nothing for play. It only means "73 cells hidden" overstated the area where he actually vanishes.

**F2. Partial occlusion reads oddly.** Severity: info, design.
- At (44,13) only his head shows above the upper patch, and at (49,20) only his legs below the lower one (`C1-n`).
- This is the expected consequence of a z-ordered cloud with no `SI_ROOF`. It is Douglas's call whether that reads as "under a cloud".

## Harness anomalies

- **H1.** An eval cell timeout during the first follow left the text console attached (the same as phase E's H1). One `exit` sent by hand freed it.
- **H2.** Scattered `ATTACH FAILED` from `lv.pos()`. Its retry got a reading every time, and no position in this report comes from a failed read.
- **H3.** The setup landing on Map 10 at (7234,23218,8) logged `event 7 @ 05B2:0080` from egg 25726. It was setup only: the next console teleport took him back to Map 13, and the map change logged is the console's.

## Console commands used

- **Reads:** `ObjectManager::objectInfo 1`.
- **Flags:** `debugflag_enable Object` and `Actor`, after the load.
- **`Cheat::toggle`:** on and off around the two hop teleports, each verified by its echo (`Cheats = true` / `false`).
- **`MainActor::teleport` (setup only):** 10 (7234,23218,8), 13 (5200,1728,120); plus the per-shot teleports inside `vignette_capture`.
- **Not used:** saveGame, loadGame (the save was loaded with `--save-slot`), setGlobal, heal, invincibility, item cheats, a teleport onto the island.

## Disk changes

- **Wrote:**
  - this report;
  - `docs/playtest-2026-10-31-island-open/` (plates `C1-a`…`C1-o`, `C2-a`, `C3-a`).
- **Scratch only, `/tmp/claude-1000/island1031/`:**
  - the game, the binary, the repo shell, `py/` drivers, `saves/` (slot 1 = a copy of `E1-turn-hp30`), `sp/`, `ingame*/`, the logs and `bm13_head.py`.
- **Not changed:** `~/lv-checkpoints`, `shared/`, source, TODO and HANDOFF.
- My ScummVM and Xvfb :95 are stopped.

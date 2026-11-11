# Playtest 2026-10-30: phase E in-engine verification (cloud13, pillars11, actorfix)

Verifier pass on main `e5bf38e`, the phase E integration (Douglas's art review 2026-10-30).

**Build under test.**
- Artifacts: TYPEFLAG `e25d7224`, U8SHAPES `2b274856`, ANIM `97ae5fc9`, EUSECODE `b47c324c` (1529089 bytes), FIXED `7d7e2c93`. `shared/build` `sha256sum -c ARTIFACTS.sha256`: all OK.
- Game directory: a pinned copy of `shared/u8-lv-patched` at `/tmp/claude-1000/phaseE/game`, identical to `shared/build` at the start. `sha256sum -c pinned-start.sha256` was OK at the end for all eight pinned files: five artifacts, top-level FIXED, `u8monsters.ini` `0642d689`, and the binary.
- Binary: a copy of `scummvm-lv-console/scummvm`, `e0518ced…`, built 2026-10-30 20:33. That postdates fork tip `e48f8716`.
- Display: Xvfb :95.

**Harness.**
- Shots: `vignette_capture.py`, run from a scratch repo shell whose `shared/u8-lv-patched` is a symlink to the pinned copy. Its `SRC` points at the real `agents/map-populator/src`. There was no `shared/build` beside it, so the sync step was a no-op.
- `session.sh`: the current copy, with its `stop` narrowed to its own tail. The scratch copy also archives each session's log before truncating it, for E6.
- Play: the replay `lv.py` driver with `rnav`/`follow`, at 640×400 with `usehighres`.
- Not run: no rebuild, no estate run, no commit. The brief bars builds, and Main ran `integrate.sh` (estate 54/54 in the integration commit).

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| E1a | screen13 in-engine: the cloud draws over the tree crown, both mushrooms and the spire feet; class ≥ 97 | **PASS.** 97.02 in two passes (`E1-a`). The upper patch cuts the crown, the cloud covers the hidden mushroom's top, and the lower patch covers the spire feet, as in the GIF. The misses left are the Avatar's pose, the cursor and a few rim pixels |
| E1b | The Avatar is never hidden under the cloud where he can walk | **PASS.** Offline with the builder's own code, 59 open cells and 73 closed. An exact-reach BFS from the turn reaches 58 of the 59 open cells (the north tip (45,6) is unreachable) and **0 closed cells**. In-engine, a 17-point walk over the open ring (west strip, north rim, east lobe, south-west arc) ended in an open cell every time, with the Avatar drawn whole in all 17 plates (`E1-e`). **Negative control:** 8 run-gait pushes (1.5 s, mag 240) from boundary cells into the closed core, eastward, southward and south-eastward, all stopped in their open cell (`E1-i-*`) |
| E1c | The Map 13 climb works end to end (arrival → turn → north leg → pad 208/209 region) | **PASS for the route, with the harpies as a balance finding (F1).** The arrival was walked in from Map 10 trigger 207 to Map 13 (4096,12008). The lower climb was walked to the lane. After a map hop (setup), the walk went lane → north leg → turn (5200,1728,120) → island → pad 208 region (5032,2288,120). Trigger 209 → Map 17 (4608,9984,0) worked, walked from a positioning teleport west of the summit strip, because the summit harpie killed him on all three walked attempts |
| E2 | screen07 class ≥ 94; capture twice | **PASS.** 96.00 and 95.98. Both captures are identical bar 2 px, and no monster appeared in either. What is left: the Avatar's start facing (about 1.7% in the box round him), the spears on the left walls (the slice's known residual), the cursor and the status text |
| E3a | The four 865 pillars draw in the 1994 banded style, no paint cycles | **PASS.** All four drew in one plate after a map reload from the new FIXED (`E3-a`): Earth ochre/brown, Air white, Fire red with flame, Water blue. `Cycle in paint` = 0 with the Object channel on (913 `calling usecode` lines). The pinned FLX's 865 frames carry 0 pixels at indices 1-14 |
| E3b | The column puzzle still works in-engine | **PASS, all four receptacles.** Save `replay1017-s04a` (four talismans, pillars standing), with a hop to Map 10 and back. Fire receptacle 29926 q203: `event 1 @ 0478:00B4`, the bark "The water talisman glows with a cold light!", the Water talisman 27725 gone from the pack, and **only the Fire pillar (18610, f2)** destroyed (865: 4 → 3) (`E3-b`, `E3-c`). **Negative control:** a second use of the spent Fire receptacle consumed nothing and destroyed nothing (3 talismans, 3 pillars). Then Water (Fire talisman consumed, Water pillar f3 gone), Air (Earth talisman, Air pillar f1) and Earth (Air talisman, Earth pillar f0). In the end: 865 = 0, flags `06A1`-`06A4` = 1, `06EC` = 1, and both q299 sealing boulders gone (`E3-e`) |
| E4a | Atli talking SE shows the gesture, frames 70/71/72 cycling, with the short cane | **PASS.** npc 107 answered `objectInfo` (shape 888, after `LV: Slot 107 … updating`) before any hold. He was held 280 W and 120 N of the Avatar on open ground, and the talk was a double-click (`event 1 @ 046B:0392`). Through the bark, 84 grabbed frames hold exactly three distinct poses. Each matches a pinned-FLX frame at **100% of its opaque pixels**: 70, 71 and 72. Sequence: `…71,70,71,72,70,70,71…72…` (`E4-a`). Only the short cane shows |
| E4b | Atli walking in several directions with no tall staff | **PASS (visual).** After `bye` (`event 15 @ 046B:0290`, no `Non-existent process`), a 40 s film of his loiter shows him walking out and back. Plates from 8 motion headings show a short cane only (`E4-b`). Frame matches on the walk crops: 33 at 100%, 35 at 95%; the others partly matched (occlusion). Held stands N, W and NW also show the short cane (`E4-c`) |
| E4c | Children 889/890 walking with spears in hand, no black outline | **NOT DEMONSTRATED.** 104 = 889 and 111 = 890 after the hop (objectInfo). Holds placed them, but my crops missed both: they landed off-crop or behind rock (`E4-d`), and the session budget ended there |
| E5 | 19 shots; flag drops > 1 point vs 10-25 | **PASS for map content; one transient drop.** Table below and `ingame/SCORES-2026-10-30.md`. **screen01 −2.37**: GHOST 411 hovers over the frame in both passes. Its 640×400 diff is 0.56% of the surface, all in the ghost's box. Not map content |
| E6 | Log hygiene | **PASS for play sessions; capture-session note.** In 9 play logs (E1-E4, Object channel on): 0 `Cycle in paint`, 0 Assert, 0 ERROR, 0 `Non-existent process`, 0 `Unhandled intrinsic`, 0 Segmentation, 0 `stuck in process loop`. In the 25 archived capture-session logs (new games, no Object channel): 49 × `Non-existent process PID (0) in implies` (about 2 per fresh new game, the same as 10-25 F7), and 0 of everything else |

## E1: Map 13

**Arrival.**
- Save `harpie1024-m13-south-axe-hp30`.
- Setup: `Cheat::toggle` on, teleport to Map 10 (7230,23650,8), toggle off.
- That landing was inside 207's box (range 12×15), so I walked N out of the box, then S back in.
- The log shows `Unloading map 10` → `Loading Fixed items in map 13`, and he arrived at **(4096,12008,0)** (`E1-b`).

**Lower climb.** I walked N along x 4096 to z 60, then E, then N to (5128,6904,72) (`E1-c`).

**Lane, north leg, turn** (run E1c, after a 10 → 13 hop because of the deaths below):
- T1 `0481` at (5119,6143) hatched 160, and T2 (5119,4479) hatched its harpie.
- On this run both were shed with the fast-area run S (leg-5 finding 2).
- T3 (5119,2687) hatched 162, also shed.
- Then the north leg up to the turn, **(5200,1728,120)** (`E1-d`), banked to scratch.

**Island.** Plates `E1-isl-*` in scratch; the montage is `E1-e`.
- Every tour stop read back in an open cell: (41,13) (41,16) (43,18) (45,20) (47,21) (46,20) (44,18) (42,16) (41,11) (43,9) (45,7) (47,9) (49,10) (50,11) (48,10) (44,10) (42,12).
- **Pushes** (start → end):

| From | Push | End | Cell |
|---|---|---|---|
| (42,13) | E | (5496,1784) | (42,13) |
| (42,14) | E | (5488,1920) | (42,14) |
| (47,10) | S | (6032,1392) | (47,10) |
| (45,10) | S | (5832,1392) | (45,10) |
| (44,17) | E | (5756,2284) | (44,17) |
| (47,19) | E | (6124,2548) | (47,19) |
| (49,11) | S | (6316,1524) | (49,11) |
| (43,11) | SE | (5604,1524) | (43,11) |

**Pad 208 / 209.**
- Pad 208 region: reached at (5032,2288,120) (`E1-f`).
- Three walked attempts from the turn to 209 hatched the summit harpie (T4 at (4863,1663), strip x ±32 × y ±192) and ended in death: hp 30 → 0, twice in under 10 s (`E1-h`).
- With a positioning teleport to (4479,1791,120), west of the strip, the walk S to 209 logged `Unloading map 13` → `Loading Fixed items in map 17` and `event 7 @ 05B2`. He arrived on Map 17 at (4608,9984,0) (`E1-g`).
- A stop at (4452-4476, 2044) is a ledge: the route has to go W to x 4355 first. It is terrain, not the harpie.

## E5: the 19 shots (10-25 → 10-30)

| Shot | 10-25 | 10-30 | Δ |
|---|---|---|---|
| screen01 | 91.99 | 89.62 | -2.37 |
| screen02 | 91.26 | 91.26 | +0.00 |
| screen04 | 95.29 | 95.22 | -0.07 |
| screen05 | 86.82 | 86.35 | -0.47 |
| screen07 | 89.93 | 96.00 | +6.07 |
| screen09 | 89.81 | 89.81 | +0.00 |
| screen10 | 88.08 | 88.09 | +0.01 |
| screen11 | 98.24 | 98.24 | +0.00 |
| screen12 | 96.37 | 96.37 | +0.00 |
| screen13 | 93.99 | 97.02 | +3.03 |
| screen14 | 83.92 | 83.92 | +0.00 |
| screen15 | 94.32 | 94.32 | +0.00 |
| screen16 | 92.23 | 93.13 | +0.90 |
| screen17 | 91.04 | 91.04 | +0.00 |
| screen18 | 94.65 | 94.66 | +0.01 |
| screen19 | 91.03 | 91.88 | +0.85 |
| screen20 | 90.58 | 93.06 | +2.48 |
| screen21 | 88.32 | 89.19 | +0.87 |
| screen22 | 93.19 | 93.19 | +0.00 |

Negative control: every pass-1 raw capture was diffed against the 10-25 raw from the same spot (`E5-*-old-vs-new.png`, magenta = differs).
- 02, 11, 14, 15: 0.00%.
- 04, 09, 10, 12, 17, 22: about 0.1% (the Avatar's pose).
- Transients: 05 (fire), 16, 18 (lava fire), 19, 20 (ghost, Atli), 21 (ghost).
- Intended changes: 07 (5.98%) and 13 (2.62%).

## Findings

**F1. Balance: the climb's harpies, the summit one above all, kill a 30-hp axe Avatar.**
- **Severity:** medium. It is not a phase-E regression, but it blocks the claim's last leg for a scripted player.
- **This session:**
  - Lane harpie 1, fought: won, 30 → 17.
  - Lane harpie 2, fought at 21: lost, 22 → 3 → 0 in one round.
  - The summit harpie: 3 of 3 attempts lost. One fight from 18; two straight runs to 209 that were stun-locked at y 2044 (30 → 22 → 14 → 1 → 0).
- **What got through:** the fast-area escape. It worked on T1, T2 and T3; on T4 the hits interrupted the run.
- **Same as:** 10-25 V4 / H3.

**F2. T1 logged a second `event 7 @ 0481` when I walked back N through it after shedding its harpie (lv_E1c lines 305 and 712), and no second harpie appeared.** Severity: info. The egg's spent gate held.

**F3. The screen07 Avatar spot (7448,21368) is a closed pocket.** Severity: info. It holds 416 lattice cells, and exact reach finds no path to the chamber floor. A player never stands there, so it matters only to anyone who expects to walk out of the capture spot.

**F4. A map reload re-creates the four talismans on the floor while the carried ones stay in the pack (`findShape 596`: 4 → 8).** Severity: low. These are FIXED records, re-read on every entry. `[INFERENCE]` A player who re-enters Map 11 after collecting them sees them again. I did not check whether this happens on a real walk-in re-entry, as opposed to a debug hop.

**F5. A debug teleport to (8020,20820) on Map 11 buried the Avatar.** He was not drawn, and `event 18` spammed with no displacement. This is the teleport-wedge trap. Relocating fixed it.

## Harness anomalies

- **H1.** A cell timeout in the middle of a `q()` left the text console attached, and every later attach failed ("ATTACH FAILED") until I sent `exit` by hand.
- **H2.** Pass 1 screen20/22: `no X display :95`. The previous shot's `stop` had killed Xvfb, and the next `start` raced it. Pass 2 recovered both.
- **H3.** The walk gait refused N at (5128,6104) beside harpie 160's corpse, while the run gait moved freely.
- **H4.** The talk on Map 10 swings the camera onto Atli, and its menu text overlays his sprite. The poses were read during the barks instead.
- **H5.** The Object channel was proven on by `calling usecode` lines. No older-build knot spot lies on these routes, so there is no positive control.

## Console commands used

- **Reads:**
  - `ObjectManager::objectInfo` (1, 104, 107, 111);
  - `ObjectManager::findShape` (73, 500, 596, 865, 866, 873, 66);
  - `UCMachine::getGlobal` 0x6A1-0x6A4, 0x6EC.
- **Flags:** `debugflag_enable Object` and `Actor`, after every start.
- **`Cheat::toggle`:** always on/off around teleports, each verified by its echo.
- **`MainActor::teleport` (setup only):**
  - 10 (7230,23650,8) and (7234,23218,8);
  - 13 (5128,6904,72), (5240,6904,72), (4096,11776,0), (4479,1791,120);
  - 11 (8020,20820,0), (7448,21368,0), (8063,21759,0);
  - 10 (19300,7300,0), (20031,6783,0), (20127,6783,0);
  - plus the per-shot teleports inside `vignette_capture`.
- **`Actor::hold`, to place NPCs for plates:**
  - 107 with offsets (−144,−144), (−340,−150), (−280,−120) and 176-unit offsets in 8 directions;
  - 111 (200,−60), 104 (−60,200).
- **`Ultima8Engine::saveGame`:** once, to the scratch slot (`E1-turn-hp30`).
- **Combat:** the `c` key in the fight loop.
- **Not used:** setGlobal, heal, invincibility, item cheats, `Item::grab`, `Actor::talk`.

## Disk changes

- **Wrote:**
  - this report;
  - `docs/playtest-2026-10-30-phaseE-verify/` (plates);
  - `docs/research/2026-10-16-screenshot-reconstruction/ingame/SCORES-2026-10-30.md`.
- **Scratch only, `/tmp/claude-1000/phaseE/`:**
  - the game, binary, repo shell, `py/` drivers and `saves/`, with slot 1 overwritten by checkpoint copies;
  - the `lv_E*.log` logs, `run/lv-playtest/all_sessions.log`, `ingame*/`, `diffs/` and `sp/`.
- **Not changed:** `~/lv-checkpoints`, `shared/`, source, TODO and HANDOFF.
- My ScummVM and Xvfb :95 are stopped.

# Verifier pass 3: `integrate/vignettes2` (2026-10-17)

- **Branch:** HEAD 48c4767 ("Verifier-2 fixes…").
- **Brief:** the `remaining_for_main` list in `docs/playtest-2026-10-17-vignettes-verify2.md`.
- **Binary:** `scummvm-lv-console/scummvm`, the text-console build of fork tip e48f8716. Its `engines/ultima/detection_tables.h` carried the old EUSECODE size (1528485), so I copied the file over from `scummvm-lv/` and re-linked (`make -C scummvm-lv-console`). The detection now reads `eusecode.flx … 1528891 bytes`.
- **Game dir:** `shared/u8-lv-patched`, canonical against `shared/build/` (sha256 checked). The one exception is the scratch dir for claim 2, described there.

## Verdicts

| # | Claim | Verdict |
|---|---|---|
| 0a | `tools/build_artifacts.sh` (full rebuild) | **PASS**: all 5 artifacts match `ARTIFACTS.sha256`. The report shows 57 compiled, 55 succeeded, 2 failed, and the 2 failures are exactly `EALOGO.UNK` and `TJORVI.UNK` |
| 0b | `tools/run_all_tests.sh` | **PASS**: 53/53 |
| 1a | Map 18 ceremony, end to end, with the restored Shield 879 | **PASS** |
| 1b | Legacy path: a save holding the Shield as 828 q83 completes the same ceremony | **PASS** |
| 1c | The ending proceeds as before (compared with leg 5) | **PASS**, with one finding (F1: paint cycles at the Map 10 arrival shelf) |
| 2 | Legacy 870 halves: the backpack opens without a crash, and SHADES accepts them | **FAIL**: **opening the backpack aborts the engine** (`ContainerGump::run(): Assertion 'sh' failed`). SHADES itself accepts the 870 halves and gives Shield 879: **PASS** |
| 3a | Map 13: no `Cycle in paint` on verify2's 8 s mouse run S from pad 208 | **PASS**: 0 lines |
| 3b | Map 13: a walk up the whole climb | **NOT DEMONSTRATED**: I covered only the north leg, y 7311 → 4495, by input. The run ended on the request budget |
| 3c | The lane harpie pair hatches and meets the player | **PASS** |
| 4a | Shot windows: screen04, screen13, screen01, screen15 against SCORES.md | **PASS**: screen04, 13 and 01 reproduce to within 0.04 points; screen15 is up 3.05 |
| 4b | No black holes in screen01's window | **FAIL (minor)**: one black sliver about 5 × 50 px remains inside the window |

## 0. Build and estate

Logs are `/tmp/vv3/build.log` and `/tmp/vv3/tests.log`.

- **`build_artifacts.sh`:** `RESULT: PASS — all 5 artifacts match`, with FIXED `ab720e17…`, U8SHAPES `7676b65f…`, TYPEFLAG `ad64d96d…`, EUSECODE `2e3b71c2…` and ANIM `696dbeb9…`.
- **Compilation Report:** `Files compiled: 57 / Successful: 55 / Failed: 2`. The two failures are `EALOGO.UNK: Line 14:4: Unterminated block comment` and `TJORVI.UNK: Line 575:11: Unterminated string literal`.
- **Estate:** `OVERALL: PASS — 53/53`. That includes `test_uc_shades` 89/89 and `test_uc_reentry` 146/146.

## 1. The Map 18 ceremony

### 1a. Shield 879, walked from trigger 211 to the altar: PASS

**Start state.** I loaded `~/lv-checkpoints/replay1011-s13e-m10-back-with-halves.sav`, which holds the halves as **539** (items 19622 q82 and 21439 q81, `f: 0xc`). I warped to (20312,17744) outside the Sacred Circle egg and turned cheats off. A 1.6 s walk N logged `Item: 7773 (shape 73) calling usecode event 7 @ 05A5:0080` (`B1`). I picked each option from the screen:

1. "Let's be reasonable!" (`B2`)
2. "Yes, Priestess." (`B3`)
3. The halves were laid down and reforged (`B4`, `B4b`).
4. "Please, High Priestess." (`B5`)

Afterwards:

- `findShape 879`: item 15547, `TYPESACR`, **q83**, `f: 0xc` (in the pack).
- `findShape 539`: 0.
- shieldFixed [0409] = 1 and avatarPoisoned [0404] = 0. The weight went 110 → 60 (`B6`).

This run also exercises the new SHADES legacy-539 fallback in-engine; see finding F3. I banked the state as `/tmp/vv3/v3-879-after-shades.sav`.

**Tiny Tars.** I took two from Hrodny's chest with `Item::grab 19557` and `Item::grab 19626`. This is the one shortcut in the run (verify2 took them the same way).

**Map 10 → Map 18 on foot.**
1. I warped to (18340,22900), 650 units N of trigger 211, and turned cheats off.
2. I walked S. The log showed `Unloading map 10` → `Loading Fixed items in map 18`, and the Avatar arrived at (3072,1792,0) (`C0`).
3. I walked the hall: (3015,1800) → (3015,4671) → (2847,4679) → (2847,6000). On the way, `event 7 @ 0481` and `05B1` ×2 fired, and crackHintGiven [0725] = 1 (`C1`).

**Negative control: full size at the crack.** Two 1.5 s walks S stopped at **(2816,6104)** (the wall line is y 6143), and templeOpen [0412] stayed 0 (`C2`).

**The crack.**
- I opened the pack (`i`), single-clicked the potion to confirm it (`Item 19626 … shape 859, 8`), and double-clicked it. The log showed `event 1 @ 04E5:00A9` and the bark "I'm feeling funny" (`C3`), and `objectInfo` read shape **867**.
- **First potion, wasted.** The Avatar stood at x 2816. That puts his 32-wide box on the 64-unit stub (the clear span is 2817..2879), so the S walk was refused until the potion wore off, about 28 s later (`wait(2000)`).
- **Second potion.** I first set x 2848, then drank. Nine 0.5 s S bursts at mouse offset 200 took the Avatar (2848,6104) → (2848,6460). templeOpen [0412] = **1** (`C4`).

**Shrine → altar.**
1. I walked (3071,6463) → (3303,6471) → (3303,7880) (`C5`: the three amber gods on their plinths and the bare altar).
2. Two 1.0 s walks S, recorded at 20 fps with ffmpeg (`/tmp/vv3/cer879.mkv`, 115 s), logged `Item: 7004 (shape 73) calling usecode event 7 @ 05A7:0080` when the Avatar reached y ≈ 8200.
3. The console stayed closed for 85 s.

**What the recording shows:**
- **The Shield lands on the altar** as the "I place the artifact…" bark appears (`D1`, about 4 s after the hatch). After the scene, `findShape 879` read **item 15547 at (3111,8167,16)** `f: 0x2004`, which is exactly AOSCENE's `pop(3111, 8167, 16)`.
- **White fade**, then the "ground trembles" bark.
- **The camera visits each god at her new spot.** I checked each god's sprite against the screen centre when its stop began:

  | God | Pinned spot | Plate |
  |---|---|---|
  | Timyra | (3039,8415) | `D7` |
  | Felicitar | (2783,8031) | `D8` |
  | Doloras | (3039,7903) | `D9` |

  The camera then pans back to the Avatar, and the "It is done. The Ancient Ones are free…" bark plays (`D10`). Overview: `D3`.

**Shatter animations.** I took full-rate frames (`/tmp/vv3/f879full/`), deduplicated them, and cropped around each god (`D4`, `D5`, `D6`). Each run starts from the 1994 sealed statue: Timyra standing, Felicitar hunched, Doloras reclining in amber. It cracks, shatters, and ends on the freed figure. The figure stays the same size throughout, and its feet stay anchored on the plinth.

Bounding boxes of the god's saturated pixels (R − B > 40) per distinct frame, with the camera parked:

| God | Sealed | Freed figure | Feet row |
|---|---|---|---|
| Timyra | y 40..103 | y 50..89, x 40..61 across 6 frames | 89 |
| Felicitar | — | — | 129 in every frame |
| Doloras | — | — | 76..79 in every frame |

The horizontal centre also held steady within each run. No frame jumps appeared. Each anim frame holds for 4 capture frames, about 5 anim fps.

**State after the ceremony** (`D2`):
- godsFree [040E] = 1, templeOpen 1, shieldFixed 1, poisoned 0.
- `findShape 860`: Timyra 9073 frame **5**, Doloras 9074 frame **4**, Felicitar 9075 frame **3**.

The log from the hatch to here has 0 lines matching `WARN`, `rror`, `Cycle in paint`, `ssert` or `Non-existent`. I saved the state as `/tmp/vv3/v3-879-m18-gods-free.sav`.

### 1c. The ending: PASS

1. I walked back out through the open breach at full size (x 2780) and N up the hall to (3072,1776). A 1.6 s N walk logged `Loading Fixed items in map 10`, `event 7 @ 05B2` and **EggEndgame `Item: 17542 (shape 73) … event 7 @ 05AA:0080`**.
2. I recorded 210 s untouched (`/tmp/vv3/end879.mkv`). All six closing barks match leg 5's text word for word (`E0` crops, `E1`–`E6`):
   - "With the Ancient Ones freed…"
   - "Green returns…"
   - "The Zealans gather around me…"
   - "An elder steps forward…"
   - "And with the power of the Ancient Ones now restored…"
   - "The Guardian's prison weakens. It is time to go home."
3. The scene then fades to black and back.

**State afterwards:** endgameStarted [0716] = 1 and godsFree 1. The Avatar was released from stasis: a S walk moved him (18432,22719,112) → (18416,23003,68) (`E7`).

**Difference from leg 5:** the arrival is now PAD_210 at **(18432,22719,112)**, on the shelf the 10-17 Map 10 vignette pass built. Leg 5 arrived at (18432,22784,0). See F1.

### 1b. Legacy Shield 828 q83: PASS

1. I loaded `replay1011-s16b-m10-three-tiny-tar-bag-key.sav`. It holds `findShape 828`: item 25423 `AORTA` q83 in the pack, 879 = 0, three Tiny Tars, shieldFixed 1, templeOpen 0.
2. I took the same route: warp N of trigger 211 → walk S → Map 18 → hall → x 2872 → potion 19626 (`event 1 @ 04E5:00A9`) → nine bursts S, templeOpen = 1 → shrine (`F0`).
3. The S walk logged `Item: 24478 (shape 73) … event 7 @ 05A7:0080`.
4. The scene ran untouched for 90 s (`/tmp/vv3/cer828.mkv`, montage `F1`, the Shield on the altar in `F2`).

**Result:** godsFree = 1. `findShape 828`: 25423 q83 at **(3111,8167,16)** `f: 0x2004`. The gods are at frames 5, 4 and 3. The pan and shatter sequence is identical to 1a.

## 2. Legacy 870 halves: FAIL (backpack crash). SHADES accepts them: PASS

**How I made the save.** No pre-10-17 save holding 870 halves exists on disk:
- `sp/q1-halves870-in-pack.sav` (from `playtest-2026-10-11-gates.md`) is gone.
- Every `replay1011` and `run1010` checkpoint holds 539s.

So I made one. I copied `shared/u8-lv-patched` to `/tmp/vv3/game870`, and in its FIXED.DAT only, changed Map 17's two 878 halves to **870** (frame 0 q81 at (4259,7199) and frame 1 q82 at (3559,3311)); the halves' coordinates, frames and qualities are unchanged. Then:

1. I ran it, loaded `replay1011-s13b`, and hopped Map 10 → 17 so the fixed items reloaded.
2. `findShape 870` found both halves. I took them with `Item::grab 3354` and `Item::grab 20322`, then warped to (20312,17744) on Map 10.
3. I saved `/tmp/vv3/v3-halves870-m10.sav`.

The save therefore holds what a 10-11..10-17 save holds: two shape-870 items with frame 0 q81 and frame 1 q82, `n: 236`, in the pack. I loaded it on the **shipped** build (`session.sh start`, canonical game dir).

**The backpack: FAIL.** On load, `findShape 870` listed both halves in the pack. Pressing `i` then logged:

```
Item: 512 (shape 529) calling usecode event 1 @ 0211:0103
scummvm: engines/ultima/ultima8/gumps/container_gump.cpp:99: virtual void Ultima::Ultima8::ContainerGump::run(): Assertion `sh' failed.
… Aborted (core dump)
```

The log is kept at `/tmp/vv3/lv_run_870crash.log`.

- **What the player sees:** opening the pack kills the game. The 870 items are never drawn, because shape 870 is empty in U8SHAPES.
- **Reading:** `ContainerGump::run` asserts that every contained item has a shape, and 870's frames are gone. I am sure of the cause; it is the halves subagent's suspicion, confirmed.
- **Who hits it:** any player with a 10-11..10-17 save who picked up the halves and has not yet run SHADES. They crash the first time they open the pack.

**SHADES: PASS.** I restarted the session, loaded the same save, turned cheats off and walked N 1.6 s. That logged `Item: 16397 (shape 73) … event 7 @ 05A5:0080`. Then:

1. "Let's be reasonable!" (`I3`).
2. **"Yes, Priestess."** was offered (`I4`). That option only appears when the halves are found.
3. The scene laid the halves down. They are **invisible on the ground**, because the white shields seen in the 539 run (`B4`) are absent (`I5`). The log shows `WARNING: Skipping invalid shape in sorter: 870,0!` and `870,1!`.
4. The reforge produced the Shield; "Please, High Priestess." (`I6`).

Afterwards, `findShape 879` showed item 27627 q83 in the pack, `findShape 870` = 0, shieldFixed = 1 and poisoned = 0 (`I7`). With the 870s destroyed, `i` opened the pack with no crash, and the process stayed alive (`I8`).

So a player who never opens the pack can still finish, but the pack is the first thing a player opens.

## 3. Map 13

**3a. 8 s mouse run S from pad 208: PASS.**
- I warped to (5119,2303,120) on Map 13. Invincibility was on, cheats off.
- I held the right button at sdir(0,1,240) for 8.0 s and reached (5119,7311,72) (`G1`).
- **`Cycle in paint` during the run: 0** (log offset taken at the run start).
- A second leg, 4 s and 2 s N from (5119,7311,72) after a Map 10 hop, also logged **0**.
- The whole Map 13 portion of the session logged 0 cycle lines.

Verify2 logged 4 × `1 -> 125` on the same run.

**3c. Lane harpie pair: PASS.**
- The run S crossed trigger (5119,4479) from the north. It hatched `0481` but produced no 873, as expected: the pair stays behind a player who is walking down.
- After a hop to Map 10 and back to re-arm the egg, I walked N from (5119,7311). The log showed `Item: 10302 (shape 73) … event 7 @ 0481:0080`, and `findShape 873` listed:
  - **127** at (5023,4015,96), hp 42;
  - **128** at (5159,3991,96), hp 33.

  Both are `enemy: 2`, `flags: 800808`, beside the new egg spots (5023,3999) and (5183,3967).
- 6 s later they were at (4991,4479,88) and (5151,4447,88), closing on the Avatar at (5111,4599) (`G2`). They do meet him on the climb.

**3b. NOT DEMONSTRATED.** I did not walk the full climb from the base pad 207 to the summit. The run hit the request budget.

## 4. Shot windows

I ran `LV_SCUMMVM=…/scummvm-lv-console/scummvm python3 tools/playtest-linux/vignette_capture.py /tmp/vv3/vig screen04 screen13 screen01 screen15`. Outputs are copied to `vig/`.

| Shot | Frame at | Class (now) | SCORES.md | Δ |
|---|---|---|---|---|
| screen04 | +106,+50 | 95.22 | 95.26 | −0.04 |
| screen13 | +179,+129 | 75.97 | 75.97 | 0 |
| screen01 | +168,+101 | 91.63 | 91.63 | 0 |
| screen15 | +186,+100 | **94.32** | 91.27 | +3.05 |

**screen01 black holes: FAIL (minor).** I compared the capture's window with the 1994 shot pixel by pixel. That found 506 pixels that are black in the capture but not in the shot. Most are scattered single pixels along sprite outlines. One is a coherent hole:

- **a black vertical sliver about 5 px wide and about 50 px tall at window x ≈ 224–230, y ≈ 13–60**;
- it sits between the cliff face (right of the blood streaks) and the pale rock spire, where the 1994 shot has grey rock (`H1-screen01-window-crop-x3.png`, middle panel of `vig/screen01_ingame.png`).

There is also a small black wedge on the left edge at y ≈ 110–170.

## Findings outside the brief

1. **F1. 28,712 `Cycle in paint dependency graph 125 -> 107 -> ... -> 125` lines on Map 10's arrival shelf.**
   - **Where.** They start at log line 14977, right after the Map 18 → 10 arrival at PAD_210 (18432,22719,112), and stop at line 43811, when the Avatar walked off the shelf.
   - **How long.** That is the whole 200 s EggEndgame scene, at about 140 lines/s.
   - **What is there.** Shapes 125 (slabs at z 104 around (18431,22783)) and 107 (stairs stacked to z 72 at x 18431/18527) are the 2473a55 (10-17) shelf the pad stands on.
   - **What it means.** It depends on the Avatar standing there, so it is a dynamic knot `test_paint_cycles` does not see. It is on main too, since Map 10 is not changed on this branch. Every player who finishes the game sits in it for the whole finale.
   - **Leg 5's arrival** was (18432,22784,0), and it logged 0 cycles.
2. **F2. A first Tiny Tar can be wasted at the crack.** At x 2816 the 32-unit body still overlaps the stub. The clear band for the tiny Avatar is x 2848..2879, which is 32 units wide. Mouse steps there come in about 100-unit quanta, so I needed several tries to land in the band. Leg 5 reported 2836 → 2872 working [INFERENCE: the mover slid it]. Low severity, since the chest has spares.
3. **F3. SHADES's legacy-539 fallback works in-engine.** The 10-11 replay saves holding 539 halves (`replay1011-s13e`) now complete the ceremony and get Shield 879 (§1a). That closes verify2 finding 1 for 539.
4. **F4. Legacy halves on the ground are invisible during SHADES.** The 870s draw as nothing and log `Skipping invalid shape in sorter: 870,N!`. This is cosmetic; the reforge still works.

## Harness anomalies

- **`detection_tables.h` was stale.** The console build carried EUSECODE 1528485 and needed the copy plus re-link that the brief describes.
- **The chord sometimes misses.** `session.sh dbg`'s attach missed once after a scene, and my own `attach()` missed once mid-route. Re-chording with a fresh focus fixed it both times. Two settings mattered:
  - Detect the attach by counting `Debugger entered` lines.
  - For `saveGame`, `teleport` and `loadGame`, append no `exit`, because those commands close the console themselves.
- **`saveGame` right after SHADES** answered "Saving game is currently unavailable" (the known lag), and worked about 60 s later.
- **Short mouse bursts move the Avatar in about 100-unit steps, or not at all.** Holds under about 0.4 s, or a turn plus a hold under about 0.55 s, did nothing.
- **`read` caching:** re-reading one PNG path showed the old image, so use a unique name per capture.

## Disk changes

- **Written:**
  - this report;
  - `docs/playtest-2026-10-17-vignettes-verify3/`: plates A–I, the `vig/` capture outputs, and `H1`.
- **Rebuilt by `tools/build_artifacts.sh`:** `shared/build/*`, identical to the canonical hashes.
- **Modified:** `scummvm-lv-console/engines/ultima/detection_tables.h` (copied from `scummvm-lv/`; generated and outside the patch). `scummvm-lv-console/scummvm` was re-linked.
- **Restored** (cmp-verified against backups in `/tmp/vv3/`): `~/.local/share/scummvm/saves/ultima8.000`, `ultima8.001` and `~/.config/scummvm/scummvm.ini`.
- **Scratch, in `/tmp/vv3/`:**
  - `game870/` (the 870 FIXED copy);
  - the saves `v3-879-after-shades.sav`, `v3-879-m18-gods-free.sav` and `v3-halves870-m10.sav`;
  - the videos `cer879.mkv`, `cer828.mkv` and `end879.mkv`;
  - the logs.
- **Not touched:** sources, builders, maps, the fork's tracked files, TODO.md. The session is stopped.

# Verifier pass 4: `integrate/vignettes2` (2026-10-17)

- **Branch:** HEAD a307420 ("Verifier-3 fixes: 870 kept as a legacy alias…").
- **Brief:** five claims (870 legacy halves, paint knots at pads 210/204 and on the Map 13 north leg, estate + build, all 19 shot windows, the legacy-828 ceremony).
- **Binary:** `scummvm-lv-console/scummvm` (text-console build of fork tip e48f8716). Its `detection_tables.h` already matched `scummvm-lv/`'s (EUSECODE 1528891), so no re-link was needed.
- **Game dir:** `shared/u8-lv-patched`, sha256-identical to `shared/build/` for all five artifacts (checked before the first session). The negative control in §2 ran on verify3's scratch dir `/tmp/vv3/game870` (the 48c4767-era FIXED.DAT).

## Verdicts

| # | Claim | Verdict |
|---|---|---|
| 1 | A save holding the halves as 870 opens the backpack without a crash, the halves draw as the 1994 halves art, and SHADES still accepts them | **PASS** |
| 2a | No `Cycle in paint` with the Avatar ~60 s on Map 10 pad 210, walking off and back | **PASS**, with one transient line (finding F2) |
| 2b | The same on Map 11 pad 204 | **PASS**, but the in-engine check cannot discriminate there: the pre-fix build also logs 0 (finding F3) |
| 2c | The same on Map 13 during a run down the north leg from pad 208 | **PASS**: 0 lines |
| 3a | `tools/run_all_tests.sh` | **PASS**: 53/53 |
| 3b | Full `tools/build_artifacts.sh` matches `ARTIFACTS.sha256` | **PASS**: all 5 match. The Compilation Report shows 57/55/2, and the 2 are exactly `EALOGO.UNK` and `TJORVI.UNK` |
| 4 | All 19 shots re-captured and compared with SCORES.md | **PASS**: no map regression. Two shots dropped by more than 1 point (screen19 −3.06, screen22 −2.58). In both, every differing pixel is a transient actor: retail GHOST 411 (and a villager in screen19) |
| 5 | Map 18 ceremony from `replay1011-s16b` (legacy 828) reaches godsFree = 1 | **PASS** (shortened: templeOpen set by `setGlobal`, details in §5) |

## Method note: the `Object` debug flag (read before §2)

`Cycle in paint dependency graph` is a `debugC(kDebugObject, …)` line (`engines/ultima/ultima8/world/item_sorter.cpp:414`). It prints **only while `debugflag_enable Object` is on**, and the flag does not survive `loadGame`. My first session ran the claim-2 walks without the flag and logged 0 lines for that reason alone; I threw those numbers away. Every count below comes from a run where the flag was on, and each has a positive witness: `calling usecode` lines (the same flag's output) appear in the same window.

## 1. Legacy 870 halves: PASS

**Save.** I used `/tmp/vv3/v3-halves870-m10.sav`, verify3's manufactured save (both halves as shape **870** in the pack: item 3354 frame 0 q81 and item 20322 frame 1 q82, `n: 236`, `f: 0xc`). I loaded it on the shipped build. `findShape 870` listed both halves.

**Bytes.** In the installed `U8SHAPES.FLX`, shape 870's blob is byte-identical to 878's (941 bytes, `a == b`). TYPEFLAG rows 870 and 878 are both `020010330001030a`. The build log shows `shape 870 injected` and `TYPEFLAG slot 870 <- 878 footpad (1, 3, 3)` (`A0-870-vs-878-preview.png`: both shapes rendered out of the FLX).

**Backpack.** Pressing `i` opened the pack. The ScummVM pid (2663430) was unchanged afterwards, and the log has no `Assertion` line (`A1`, zoom `A1b`). Both halves draw at the pack's (0,0) slot, overlapping: the blue sun half (yellow sun) under the blue eye half (red eye), which is the 1994 halves art. Verify3 got `ContainerGump::run(): Assertion 'sh' failed` on this same keypress.

**SHADES.** I closed the pack, walked N for 1.6 s with cheats off, and picked each option from the screen:

1. "Let's be reasonable!" (`A2`)
2. "Yes, Priestess." (`A3`). This option appears only when the halves are found.
3. The halves were laid down and are **visible**: the 1994 sun half sits on the ground beside Ezrekal (`A4` montage, `A4b` zoom). The log for the whole scene has 0 `Skipping invalid shape` lines (verify3 logged `870,0`/`870,1` and showed nothing on the ground).
4. They were reforged into the Shield (`A5`).
5. "Please, High Priestess." (`A6`)

**State afterwards:**
- `findShape 879`: item 27705 `TYPESACR` **q83**, `f: 0xc` (in the pack).
- `findShape 870`: 0.
- shieldFixed [0409] = 1 and avatarPoisoned [0404] = 0.

**Negative control:** none applies directly. The control for this claim is verify3's crash on the same save and the same keypress, from the previous build.

## 2. Paint cycles at the arrival pads and the Map 13 north leg

Session 3 log: `/tmp/vv4/lv_run_session3_claim2.log`. Setup: `replay1011-s16b` loaded, cheats on, invincible, `debugflag_enable Object` set after the load and again after each map change. Each check started with a debug teleport to a different map, so the fixed items are the shipped FIXED.DAT's and not the save's.

### 2a. Map 10 pad 210: PASS, one transient line

| Step | Avatar | `Cycle in paint` |
|---|---|---|
| Teleport to (18432,22719,112), stand 60 s (`C1`) | (18432,22719,112) | 0 |
| Walk S down screen17's stair (`C2`) | → (18496,23047,56) | 0 |
| Walk N back up, across the shelf and off the north side (`C3`) | → (18496,22543,112) → (18496,22047,112) | 0 |
| Walk back S toward the pad, stand 30 s (`C4`) | (18400,22639,112); the gargoyle stops further S | 0 |
| Teleport to the stair foot (18496,23047,56), walk N up the stair and W onto the shelf beside the pad, stand 30 s (`C5`) | → (18496,22847,104) → (18436,22787,112) | **1** (`125 -> 1 -> ... -> 125`, see F2) |
| Stand on that stair step (18496,22847,104) for 15 s (`C6`) | | 0 |
| 4 more walks up from the stair foot (run and walk gaits) | to y 22351..22647 | 0 |
| 3 walks down from the pad (run and walk gaits) | to (18432,22951,80) / (18500,23051,56) | 0 |

The whole Map 10 window, about 6 minutes, logged 1 line.

**The endgame arrival, which is verify3 F1's own scenario (session 2, flag on).** I completed the legacy-828 ceremony (§5), then:

1. walked N out of the Map 18 hall;
2. the log showed `Loading Fixed items in map 10`, `event 7 @ 05B2`, then **EggEndgame `Item: 2214 (shape 73) … event 7 @ 05AA:0080`**;
3. the Avatar was at (18432,22719,112);
4. I recorded 216 s untouched (`F1`, montage `F2`).

Result: **0** `Cycle in paint` lines, endgameStarted [0716] = 1, and no `ssert`, `Non-existent` or `Skipping invalid` lines. Verify3 logged 28,712 lines in this same scene.

**Negative control: the pre-fix build reproduces F1.**
- I ran the same binary on `/tmp/vv3/game870`, whose Map 10 still has the stair's top block where the solve put it: 107:1 at (18431,22751) z 0/48/72. The shipped build has it at (18399,22719) z 0/48/64. I diffed the two FIXED.DATs: these are the only 3 Map 10 items that differ.
- I loaded `/tmp/vv3/v3-879-m18-gods-free.sav` and walked out of Map 18 to the pad 210 arrival. With the flag on, it logged **1,254 `Cycle in paint dependency graph 125 -> 107 -> ... -> 125` lines in 10 s** (`N3`); the run's log has 2,086 in total.
- So the check can see this knot, and on the shipped build it is gone.

### 2b. Map 11 pad 204: PASS, but the check is not discriminating

I teleported to (8291,22639,0), stood 60 s (`B1`), walked E to (8707,22639), S to (8707,22871), back W to (8411,22871), N to (8411,22671) and W to (8307,22671) (`B2`, `B3`), then stood 20 s. Result: **0** lines.

**Negative control (pre-fix build, flag on).** On the pre-fix build I stood on pad 204 for 20 s and took the same walk off and back (to (8315,22663)). That also logged **0**. The `1 -> 32 -> 10 -> 1` knot that `test_paint_cycles` §8 reports for the old rim did not show up in-engine from those positions. So the in-engine part of 2b cannot tell the two builds apart. The evidence that the fix works there is `test_paint_cycles.py` (75/75, including §8) and the FIXED diff (the new build drops 80 of Map 11's items: 9601 → 9521).

### 2c. Map 13, north leg from pad 208: PASS

| Run | Start → end | Lines |
|---|---|---|
| 8.0 s right-button run S at verify3's offset (-215,+107) (`D1`, `D2`) | (5119,2303,120) → (5119,7311,72) | 0 |
| Two 4 s runs N, back up the leg | → (5243,5643,76) → (5019,3491,108) | 0 |
| A 10 s + 8 s walk-gait descent S (`D3`) | (5119,2303,120) → (5119,6375,72) → (5183,8063,68) | 0 |

Map 13 total: **0**. The `Object` flag was confirmed live, with 1,049 `calling usecode` lines in the same window.

## 3. Estate and build: PASS

- **`tools/build_artifacts.sh`** (full rebuild; log `/tmp/vv4/build.log`): `RESULT: PASS — all 5 artifacts match`. The hashes are TYPEFLAG `d26d1531…`, U8SHAPES `efb16af1…`, ANIM `696dbeb9…`, EUSECODE `2e3b71c2…` and FIXED `8db11ee3…`.
  - **Compilation Report:** `Files compiled: 57 / Successful: 55 / Failed: 2`. The two failures are `EALOGO.UNK: Line 14:4: Unterminated block comment` and `TJORVI.UNK: Line 575:11: Unterminated string literal`, which is the `DEV_ALLOWLIST` pair.
  - The step-5 output shows the 870 row: `shape 870 frame 0 … 30x28`, `frame 1 … 24x28`, `validate_shape clean`.
- **`tools/run_all_tests.sh`** (log `/tmp/vv4/tests.log`): `OVERALL: PASS — 53/53`. The relevant suites:
  - `test_paint_cycles` 75/75
  - `test_art_props` 323/323
  - `test_vignettes` 39/39
  - `test_integration_state` 14/14
  - `test_scummvm_patch_sync` 3/3
- **Fork check:** skipped. The change touches no fork file, and `test_scummvm_patch_sync` passed in the estate.

## 4. All 19 shot windows: PASS (no map regression)

`LV_SCUMMVM=…/scummvm-lv-console/scummvm python3 tools/playtest-linux/vignette_capture.py docs/playtest-2026-10-17-vignettes-verify4/vig screen01 … screen22`, one fresh session per shot (log `/tmp/vv4/vig.log`).

| Shot | Map | Frame at | Class now | SCORES.md | Δ |
|---|---|---|---|---|---|
| screen01 | 13 | +168,+101 | 91.98 | 91.63 | +0.35 |
| screen02 | 10 | +166,+128 | 91.25 | 91.26 | −0.01 |
| screen04 | 18 | +106,+50 | 95.22 | 95.26 | −0.04 |
| screen05 | 11 | +178,+36 | 86.35 | 86.35 | 0 |
| screen07 | 11 | +172,+102 | 86.03 | 86.06 | −0.03 |
| screen09 | 10 | +242,+104 | 89.81 | 82.65 | +7.16 |
| screen10 | 9 | +164,+137 | 88.09 | 88.11 | −0.02 |
| screen11 | 17 | +284,+94 | 98.24 | 98.24 | 0 |
| screen12 | 17 | +116,+104 | 85.87 | 85.90 | −0.03 |
| screen13 | 13 | +179,+129 | 75.97 | 75.97 | 0 |
| screen14 | 13 | +176,+66 | 83.92 | 83.96 | −0.04 |
| screen15 | 13 | +186,+100 | 91.30 | 91.27 | +0.03 |
| screen16 | 13 | +181,+87 | 92.23 | 93.13 | −0.90 |
| screen17 | 10 | +130,+128 | 92.45 | 92.45 | 0 |
| screen18 | 10 | +175,+103 | 94.65 | 94.66 | −0.01 |
| **screen19** | 10 | +190,+95 | **91.40** | 94.46 | **−3.06** |
| screen20 | 10 | +217,+101 | 90.83 | 90.83 | 0 |
| screen21 | 10 | +188,+113 | 88.32 | 86.96 | +1.36 |
| **screen22** | 10 | +187,+79 | **93.17** | 95.75 | **−2.58** |

**Flagged: screen19 and screen22.** I compared each capture's in-engine panel with the 10-17 reference panel pixel by pixel (|ΔRGB| > 12):
- **screen19:** 2,038 differing pixels, all in window columns x 40..200, y 0..120. They are retail **GHOST 411** (the grey winged figure SCORES.md lists as following the Avatar), a villager at the left, and the Avatar's pose (`H1`).
- **screen22:** 1,512 differing pixels, all in x 120..200, y 0..120. They are GHOST 411 standing over the garden bed, and the Avatar's pose (`H2`).

Everything outside those boxes is identical, so the map content in both windows is unchanged.

**Re-capture** (`vig/rerun/`):

| Shot | Class | Δ vs SCORES.md | What changed |
|---|---|---|---|
| screen19 | **94.24** | −0.22 | The ghost moved off-frame |
| screen22 | **93.19** | −2.56 | The ghost again at the same spot |
| screen16 | **93.14** | +0.01 | Its −0.90 was a flying monster top-right in the first capture (`H3`) |

screen22's two captures agree: in a fresh session the ghost lands deterministically inside its window. See F4.

The other moves are expected:
- **screen01** (+0.35): its vignette JSON changed in a307420.
- **screen09** (+7.16): the animated waterfall's phase.
- **screen21** (+1.36): actor or pose.
- **screen14** (−0.04): alignment 1 px off.

## 5. Legacy-828 ceremony: PASS (shortened)

1. I loaded `replay1011-s16b-m10-three-tiny-tar-bag-key.sav`. It holds `findShape 828`: item 25423 `AORTA` **q83** in the pack, 879 = 0, shieldFixed 1, templeOpen 0.
2. I warped to (18340,22900) on Map 10 (`E0`), turned cheats off and walked S into trigger 211. The log showed `Unloading map 10` → `Loading Fixed items in map 18`, and the Avatar was at (3072,2024,0).
3. **Shortcut:** instead of the hall walk and the Tiny Tar crack, I set templeOpen with `UCMachine::setGlobal 0x412 1 1`. `AOSCENE.UNK` gates only on `godsFree`, `templeOpen` and `shieldFixed`, and then on an artifact at q83 (lines 22-79). I warped to (3303,7880,0) in the shrine (`E1`) and turned cheats off.
4. **Gate check:** a first attempt without that global hatched `05A7` and returned at once (godsFree stayed 0), as the `if not templeOpen return` gate predicts.
5. Two 1.0 s walks S logged `Item: 24478 (shape 73) calling usecode event 7 @ 05A7:0080`. The scene ran untouched for about 100 s. The montage (`E2`) shows the Shield placed on the altar, the white fade, the three gods shattering out of amber, and the freed figures.

**Result** (`E3`): godsFree [040E] = **1**.
- `findShape 828`: 25423 q83 at **(3111,8167,16)** `f: 0x2004`, which is the altar spot.
- The gods are at frames **5** (Timyra, 24440, (3039,8415)), **4** (Doloras, 24457, (3039,7903)) and **3** (Felicitar, 24571, (2783,8031)), the same as verify3.
- The scene window has 0 lines matching `Cycle in paint`, `WARN`, `rror`, `ssert`, `Non-existent` or `Skipping invalid`.

What the shortcut skips: the hall walk and the crack passage (TEMPLENT setting templeOpen). Verify3 1b covered both on this build's map and usecode, and neither part changed in a307420.

## Findings outside the brief

1. **F1. The `Cycle in paint` probe is silent unless `debugflag_enable Object` is on, and loads clear it.** A zero is therefore meaningless unless the same window also shows `calling usecode` lines. This cost me one whole pass of claim 2. Suggest adding it to `traps.md` under "Standard session setup": that section mentions the flag for click dumps, but not that the paint-cycle line depends on it too.
2. **F2. One transient `Cycle in paint dependency graph 125 -> 1 -> ... -> 125` on Map 10.** It was logged once, in the frame where the Avatar stood on screen17's stair at about (18496,22847,104), one step below the shelf crest (125, the slabs at z 104), while walking up from the foot. It did not recur:
   - standing on that spot for 15 s gave 0;
   - nine more stair traversals, up and down at both gaits, gave 0.

   It is one frame against verify3's 140 lines/s, and it is not the pad-210 knot (it involves the Avatar and 125, not 107). Low severity. `test_paint_cycles` §8 stands the Avatar only at pads and shot spots, so it would not see a mid-stair position.
3. **F3. Pad 204's in-engine check does not discriminate.** On the pre-fix FIXED.DAT, the Avatar standing on pad 204 and walking the room (flag on) logged 0 lines. Whatever `test_paint_cycles` §8 found there (`1 -> 32 -> 10 -> 1`) either needs a position or frame I did not reach, or the engine's sorter breaks that tie differently from the test's model. The pad-204 fix rests on the test alone; nothing in-engine contradicts it.
4. **F4. GHOST 411 now stands inside screen22's window in a fresh session.** It did in both captures, and it costs that shot about 2.6 points. It is a retail actor (AVATAR.UNK, documented in SCORES.md) and EUSECODE is unchanged, so this is placement luck relative to the Avatar spot, not map content. A capture driver that waits, or nudges the Avatar, would de-noise the score.
5. **F5. Debug-teleporting onto the screen17 stair at x 18432 buries the Avatar.** At (18432,23047,56) he sank into the stair blocks and could not walk out (`event 18` spam). At x 18496 he lands fine. This is the known teleport wedge, recorded for the next driver.

## Harness anomalies

- **Stale `exit` lines poisoned the command queue.** I wrote `exit` after `MainActor::teleport` or `loadGame` (both close the console themselves). The text console then drained one command per attach, and a `loadGame 1` ran twice. The fix was to track the attach state myself and never write `exit` after a closing command.
- **The chord failed for a few seconds after `loadGame` and after a map change.** Retrying after 1.5 s worked.
- **The session-2 wedge.** After a cheat toggle and teleport the world froze with `event 18` spam, and the chord stopped attaching. I restarted the session.
- **The pack would not open after SHADES** (the Avatar was still in the scene's stasis). Verify3's "pack opens after SHADES" step was not repeated. The claim-1 pack check is the pre-SHADES open.

## Disk changes

- **Written:**
  - this report;
  - `docs/playtest-2026-10-17-vignettes-verify4/`, which holds:
    - plates `A0`–`A6`, `B1`–`B3`, `C1`–`C6`, `D1`–`D3`, `E0`–`E3`, `F1`–`F2`, `N1`–`N3` and `H1`–`H3`;
    - `vig/` (all 19 `_ingame`/`_raw` pairs);
    - `vig/rerun/` (screen16, 19 and 22).
- **Rebuilt by `tools/build_artifacts.sh`:** `shared/build/*`, identical to the canonical hashes. `session.sh start` synced nothing, because the harness dir was already canonical.
- **Restored** (cmp-verified): `~/.local/share/scummvm/saves/ultima8.000` and `ultima8.001`. `~/.config/scummvm/scummvm.ini` is unchanged.
- **Scratch, in `/tmp/vv4/`:** the logs (`build.log`, `tests.log`, `vig.log`, `lv_run_session{1,2,3}*.log`, `lv_run_oldbuild_negctl.log`), `launch_old.sh` and `vig2/`.
- **Not touched:** sources, builders, maps, the fork, TODO.md, `/tmp/vv3/`. No session is running.

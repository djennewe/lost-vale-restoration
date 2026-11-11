# Tiny Tar body 867, the Avatar at 0.6 with the glow ramp: in-engine verification (2026-10-11)

**Build under test.** main `1792a9c` (merge of `8a4bfac`, art-track contract 8). The game copy is `/tmp/claude-1000/vtiny/game`, a copy of `shared/u8-lv-patched`. All five artifacts match `shared/build/ARTIFACTS.sha256`:

| File | sha256 |
|---|---|
| U8SHAPES | `95e786a5…` |
| ANIM | `c2e27898…` |
| EUSECODE | `4182e079…`. The log reads `usecode/eusecode.flx: d00d0d59…, 1526311 bytes` and `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` |
| FIXED | `122b4374…` (root and `STATIC/`) |
| TYPEFLAG | `6bdb3036…` |

**Binary and display.** The process was launched at 17:45 from `scummvm-lv/scummvm`, which was then still the 04:17 build. That build is byte-for-byte the size of `/tmp/claude-1000/pinned-bin/scummvm-4182e079` (same mtime, 41,568,560 bytes). The repo binary was rebuilt at 18:07, during the session, but the running process kept the image it had loaded at 17:45. Xvfb `:93` ran with vf10's ini: 320×200, no width/height keys, `frameLimit=true`, `SDL_AUDIODRIVER=dummy`.

**Driver.** `vtiny/py/vf.py` is vf10's driver with `PRIME = False`, so no left click comes before a right hold. Launches now use the pinned binary path. Every position read is `objectInfo 1`. Every drink, walk, run, jump and climb was mouse input on the screen with cheats off, and the off state was confirmed by the echoed `Cheats = false`. Cheats were on only for teleports, and for two `Item::grab` calls in the first `s16b` load (potions 25461 and 25462, which were never drunk in that load). Each drink was recorded with ffmpeg `x11grab` (lossless, 25 fps). The ramp claims are judged frame by frame from those films. A scene shift is measured by phase correlation on background regions, and the Avatar is compared after the scene is aligned.

**Drinks.** 12 Tiny Tars in all, from three saves:
- `run1010-s16b-m10-three-tiny-tar`, 3 loads: 6 drinks, plus the protection potion;
- `run1010-s17a-m18-arrival`, 3 loads: 6 drinks.

Before any Map 18 work, each `s17a` load was hopped to Map 17 and back (log: `Loading Fixed items in map 17`, then `… map 18`), so that the map's fixed items come from the shipped FIXED.

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| T1 | The f8 Tiny Tar plays the ramp; the full Avatar shrinks with a blue glow mid-ramp; no visible jump at the swap or after; ends as a tiny Avatar in armour | **PASS for the sprite.** The whole view snaps 16 px when the ramp ends (finding 1, usecode camera, not the art) | **Swap:** shape 1 after `turnToFace`, compared with frame 60 after `setType`: **0 px differ**. **End:** frame 69, compared with 867's `AS_STAND` frame 3 once the scene is aligned: **0 px differ**. **Sprite heights at 2×:** 101 → 95 → 89 → 85 → 79 → 75 → 69 → 65 → 61, then 69 = the tiny stand. The bottom row stays at y 233 in every frame. Frames 61-68 are pale blue-grey and match the committed `ramp-3x.png` "O60 glow" row. The end is the tiny Avatar in helm, armour and red tunic (`T1-tiny-avatar-stand-m10`) |
| T2 | Walk and run in all 8 directions, SW included; feet planted; jump works; a climb onto a 40-high item | **PASS.** The tiny Avatar **climbs** 40-high items | **Walk:** all 8 directions moved, SW included (−40,+40 and frame 5). **Run:** all 8 moved, and the run animation plays (`T2-tiny-run-NE-…`). **Feet:** the scene-stabilized walk and run strips show the planted foot holding its ground (visual judgement). **Jump:** a both-button click S moved him 148 units, with the crouch-and-leap frames (`T2-tiny-jump-frames`). **Climb:** from (2524,5792,0) facing N against the hall relief (shape 15, top z 40), he went to **(2524,5760,40)** on the top (`T2-tiny-climb40-…`, `T2-tiny-on-hall-relief-top-z40`). Full-size control at the same relief: (2524,5824,0) → (2524,5768,40) |
| T3 | The tiny Avatar passes S through the crack at x 2852 and the full-size one is refused; the 120-tall sanctum boundary still refuses a tiny jump or climb | **PASS** | **Full size:** walked S from (2852,5400). The hint egg fired (`event 7 @ 05B1`). He stopped at **(2852,6096)**, and a further 1.2 s push left him there (`T3-01`). **Tiny, from the same spot:** (2852,6096) → **6160 → 6236 → 6300**. The TempleEntry egg fired (`event 7 @ 05B0`) with the bark "Behind me the split stone groans and slumps…" (`T3-02`). **Boundary, tiny:** at the hall side (2576,6111), facing S, a both-button click and a click-then-hold jump both stayed at (2576,6111,0). At the sanctum side (2636,6178), a jump N played a leap up against the wall and he came down where he started, z 0 (`T3-tiny-sanctum-side-…`). **Full-size control** at (2576,6111): a both-button click was refused |
| T4 | Regrows by the reverse ramp with no jump; ends shape 1 frame 3; whether growing inside the crack still kills, if that is reachable without cheats | **PASS.** Growing **inside the crack is not reachable**, so that test was skipped. **Growing against a north or west wall kills** (finding 2) | **Ramp at (2852,6300), Map 18:** frame 60, compared with shape 1 frame 3 once the scene is aligned: **0 px differ** (the cursor excluded). The feet stay on one row throughout (`T4-regrow-…-3x`). Three reads were taken after a regrow with no input since. All three were shape 1, hp 30, frame 3; one caught a transient frame 505 first. Two regrows were filmed: Map 18, checked frame by frame, and Map 10, checked by eye. **Crack:** the egg box starts at y 6112, the wall line, so a tiny body in the aperture has already breached it. After the breach the full-size Avatar walked N through the crack, (2852,6300) → (2852,5900) |
| T5 | While tiny, the sleep and protection potions animate | **PARTIAL.** Protection: **PASS**. Sleep: **NOT DEMONSTRATED** | **Protection** (25461, f5, double-clicked on the ground while tiny): the tiny Avatar does the vertical leap, arms up, rise and land, with the bark "…I feel like fighting…". Flags went to `40000` (`T5-…-frames`). **Sleep:** none of the saves holds a frame-6 potion. `findShape 859` lists frames 1, 2, 5, 7, 8 on `s16b` and only 8 on `s17a` |
| L | Log hygiene | **PASS for this change.** Pre-existing Map 18 paint cycles (finding 4) | **0** each of: `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Trying to access segment`, `popToContainer`, ERROR, `Invalid item`, `Unhandled intrinsic`, `Invalid procid`, `Skipping invalid shape`. **4 WARNINGs**, all stock: translations.dat, gui-icons, theme, timestamps. **3,103 `Cycle in paint`, all on Map 18 and none on Map 10:** 113↔1 ×2926, 113↔867 ×152, 1↔15 ×18, 867↔15 ×7 |
| Checks | Test estate, hashes, fork patch | **PASS.** The build was not run | `tools/run_all_tests.sh`: **48/48 PASS**. That includes `test_tiny_tar` 36/36, `test_lv_tiny_avatar_art` 40/40, `test_integration_state` 14/14 and `test_scummvm_patch_sync` 3/3. The fork diff equals `0001-lost-vale-engine.patch` (`diff -q` clean, fork `b867a30c`). The game copy's hashes match the canonical file. I did **not** run `tools/build_artifacts.sh`, because the assignment forbids build scripts. No shape ID was added or renumbered (`TYPE_SHAPES` 867 is unchanged, per the contract) |

## T1: the shrink — PASS for the sprite

The ramp was filmed on Map 10 at (20622,8976), in open ground. The Avatar faced SE and the pack was dragged clear.

| Step | Film frame | What it shows |
|---|---|---|
| Drink | 0.7 s | `Item: 11499 (shape 859) calling usecode event 1 @ 04E5:00A9` |
| `turnToFace(southeast)` | 8.0-8.4 s | shape 1, turning |
| Lightning | 8.7-9.0 s | full-screen flash |
| Frame 60 | 9.0 s | **identical to the shape 1 frame before it** (0 px) |
| 61-68 | 9.2-14.6 s | shrink, pale glow (`T1-mid-ramp-frame63-glow-m10`). A position read at 10.4 s saw `shape 867), 64` |
| 69 → `AS_STAND` | 14.7 → 14.8 s | **0 px differ** with the scene aligned |

- **The plate** is `T1-shrink-ramp-m10-scene-aligned-3x`: shape 1 frame 3, then 60-69, then the 867 stand. Each crop is shifted by its measured camera offset, and a red line marks the feet row. The feet sit on the line in all twelve.
- **Colour.** The glow whitens the tunic almost completely at 63-66. That is what the picked plate shows: the "O60 glow" row of `shared/docs/art-poc/tiny-avatar/ramp-3x.png` is the same pale blue-grey figure.
- **Not a child.** `T1-tiny-avatar-stand-m10` shows a small Avatar in helm, pauldrons and red tunic.
- **Repeats.** All 12 drinks shrank him to shape 867. A second shrink, on Map 18 at the crack, was filmed (`T3-crack-m18.mkv`) and was not measured frame by frame.

## T2: moving while tiny — PASS

**Walk** (right-button hold, pointer 110 px out). The moves, with their ends:

| Hold | Δ (x, y) | End frame |
|---|---|---|
| 0.8 s, first potion: SW | (−40, +40) | 5 |
| W | (−56, 0) | |
| NW | (−36, −36) | |
| N | (0, −56) | |
| NE | (+48, −48) | |
| 1.5 s, third potion: W | −176 | |
| NW | (−128, −128) | |
| N | −240 | |
| NE | (+184, −184) | |
| E | +248 | |
| SE | (+160, +160) | |
| S | +280 | |

Every stop read shape 867, on the stand frame for its direction.

**Run** (pointer 340 px out). SW (−48,+48) and (−152,+152); W −64 and −244; NW (−28,−28) and (−140,−140); N −232; NE (+160,−160); E +240; SE (+168,+168); S +244.

**SW, the relocated frames 1550-1557.** SW walks and runs move, and they draw a proper Avatar walking screen-left, with no garbage frame and no pop. `T2-tiny-walk-SW-frames1550-1557-scene-stabilized-3x` has the frames re-registered on the ground. The planted foot keeps its ground position from frame to frame, and the swinging foot passes it. The run strip (`T2-tiny-run-NE-scene-stabilized-2x`) shows the long-stride run frames and the same planting. This is a visual judgement: I measured no per-frame foot position.

**Stride.** One pre-faced 2 s mouse walk E from (20250,8968) went **436** units tiny. Full size at the same start went 624 and 728. That is a ratio of 0.60-0.70, which agrees with the contract's 0.6. It is a single tiny trial, because the potion window ran out.

**Jump.** The `SPACE` jump key did nothing through xdotool (harness anomaly 1). The both-button click, left and right pressed together and released at once, is the input the mover uses for a jump and climb (`u8_avatar_mover_process.cpp:422-438, 506-537`).
- **Tiny on open floor**, facing S: (2524,5950) → (2524,6098), a jump of 148 units, with crouch and leap frames (`T2-tiny-jump-frames`).
- **The first click after a turn** only turns him (`checkTurn`, :509).

**Climb onto a 40-high item: he climbs it.** The test item is the hall relief, a shape 15 course (128×32×40 at z 0), (2432..2560, 5728..5760), Map 18.

| Body | Start | End |
|---|---|---|
| Full size | (2524,5824,0) | **(2524,5768,40)** |
| Tiny | (2524,5792,0), the tiny box flush with the face | **(2524,5760,40)** |

- The climb animation plays at 0.6 (`T2-tiny-climb40-onto-hall-relief-frames`), and he stands on the top (`T2-tiny-on-hall-relief-top-z40`).
- This is what contract 8 predicted: deltaZ is unscaled, so the tiny Avatar climbs whatever the full one climbs. Through the climb72 chain this reaches at most 40 + 72 = 112, under the boundary's 120, so it does not open the sanctum (T3).
- I did not walk the relief tops or try chaining from them.

## T3: Map 18 — PASS

**Crack, negative first.**
- Full size, walked S from (2852,5400): `Item: 21401 (shape 73) calling usecode event 7 @ 05B1:0080`, and the hint "The stone here is split from top to bottom…" (`T3-01`). He stopped at (2852,6096).
- A further 1.2 s push left him at (2852,6096,0). Two `SPACE` jumps there prove nothing, because that key never reached the mover (harness anomaly 1).

**Crack, tiny.**
- **The drink** at (2852,6096): `Item: 11499 (shape 859) calling usecode event 1`. The first double-click on the pack logged no use, and the retry did.
- **Pushes S, 0.6 s each:** 6096 (turn only), 6160, 6236, 6300, all shape 867 at z 0.
- **The egg:** `Item: 18506 (shape 73) calling usecode event 7 @ 05B0:0080`. The bark is "Behind me the split stone groans and slumps, and the crack falls open into a gap a man could walk through." (`T3-02`). On the third `s17a` load the TempleEntry barks also included "…The air in here is old and very still." (visible in `T3-tiny-sanctum-side-…`).

**The 120-tall boundary, tiny.**
- **Hall side**, (2576,6111), facing S, beside the x 2576 spot where the 2026-07-31 full-size Avatar climbed the old one-course wall:
  - a both-button click: no change, (2576,6111,0);
  - a click-then-hold jump: no change.
- **Sanctum side:** walked N from (2576,6230) to the wall, which deflected him to (2636,6178).
  - The both-button click only turned him to N.
  - The click-then-hold jump N then played a leap up against the wall face, and he came down at (2636,6178,0) (`T3-tiny-sanctum-side-climb-jump-attempts-frames`).
- **Full-size control:** a both-button click S at (2576,6111) stayed at (2576,6111,0).
- The same both-button input climbed the 40-high relief (T2), so the refusal is the wall's height, not dropped input.

## T4: the regrow — PASS; the failure branch: see finding 2

**Ramp** (`T4-regrow-ramp-m18-sanctum-scene-aligned-3x`, at (2852,6300) in the sanctum):
- **Sequence:** "Uh oh…", the turn to SE, the lightning (the teleport round trip), then 68 down to 60, pale mid-ramp, with the feet on one row.
- **The end:** frame 60 compared with shape 1 frame 3 after `setType`: 0 px differ in the sprite box once the scene is aligned. The arrow cursor was the only difference and is excluded.
- **Reads:** the regrow ends were shape 1 frame 3, hp 30, at (2852,6300) and at (20598,8876) on Map 10. In the sanctum, at (2636,6318,8), the first read caught `frame 505`, and 2 s later it was frame 3. [INFERENCE] That is an idle animation after `AS_STAND`.
- **Map 10:** the regrow there was filmed too, `T1-shrink-m10.mkv` at 57.6-61.4 s.

**"Growing inside the crack": not reachable without cheats, so skipped as instructed.**
- **Why.** EggTempleEntry's box starts at y 6112, the wall line. Any tiny position inside the 6112..6143 aperture is inside the egg box, and the egg breaches the wall on entry.
- **After the breach the crack fits a full body.** The full-size Avatar walked N through it, (2852,6300) → (2852,6196) → (2852,5900), so `canExistAt` there succeeds.

## T5: potions while tiny — PARTIAL

**Protection: PASS.**
- **Setup:** a fresh `s16b` load. I drank Tiny Tar 11499, and at shape 867 frame 3 I double-clicked the f5 potion 25461 where it lay on the ground at (21216,8832).
- **Log:** `Item: 25461 (shape 859) calling usecode event 1 @ 04E5:00A9`.
- **What played:** the tiny Avatar's vertical leap, arms up, rising on screen and landing, with the bark "…I feel like fighting…" (`T5-protection-potion-while-tiny-vert-leap-frames`). Flags went `0` → `40000`.

**Sleep: NOT DEMONSTRATED.** None of the three named saves holds a frame-6 potion.

## Findings outside the brief

**1. The whole view snaps 16 px at the end of each ramp.**
- **The cause.** `makeAvatarTiny` lowers the camera by one z unit per half-step (`Camera::move_to … getZ() - 1`), and `makeAvatarBig` raises it.
- **What a player sees.** Over the ramp the scene drifts 16 game px. Then `Camera::setCenterOn(Avatar)` puts it back in one frame:
  - the shrink: offsets 0 → −32 window px over 9.2-14.6 s, then 0 at 14.8 s;
  - the regrow: 0 → +32, then 0 at 57.2 s.

  The sprite does not jump relative to the ground. The whole view does (`F1-camera-snap-end-of-shrink-frame69-left-standright`).
- **Not from this change.** EUSECODE `4182e079` did not change in `8a4bfac`, and the camera calls have compiled since 2026-10-07 (FREE.UNK comment). [INFERENCE] The child body showed the same snap.

**2. Regrowing flush against a wall to the north or west kills the Avatar.**
- **How it was reached.** I reached it without cheats, apart from the teleport that placed him in the hall before the drink: drink at (2524,5900), walk N into the hall relief and stop at (2592,5792,8), then let go.
- **What happened.** The timer ran out, "Uh oh…", the lightning, and a full-size figure for one flash. Then "Here lies the Avatar", the death book, `hp 0` and flags `1400` (`F2b-…`).
- **A teleported placement does the same.** At (2576,6175), flush with the sanctum's crack wall, a teleported tiny Avatar died the same way (`F2a-…`).
- **Why** [INFERENCE from the geometry]. The anchor is the box's max corner. The tiny body is (x−32,x]×(y−32,y] and the full one is (x−64,x]×(y−64,y]. A tiny Avatar against a wall on his N or W side therefore regrows 32 units into it, `canExistAt(TypeAvatar…)` fails, and the patched failure branch kills him.
- **Before this change** [INFERENCE]. TYPEFLAG's (1,1,4) and EUSECODE are unchanged in this commit, so the child body did the same.
- **Why it matters.** The window is about 28 s and the hint sends the player hard against the pale block. A player who drinks, walks up against the north side of a relief and waits, or one who hugs the crack wall from the sanctum side, dies with only the "Uh oh…" bark as warning. This is a design call for the author: for example, nudge to the nearest spot that fits, or kill only in the crack.

**3. The tiny Avatar climbs onto the hall relief tops** (T2), as contract 8 predicted. Nothing above 112 is in reach of a climb chain from there, so the sanctum holds. The relief tops are a reachable place for a tiny Avatar.

**4. Map 18 paint cycles at the plinth (shape 113, (2672,5808,0), 128×128×8) and the relief courses (shape 15).**
- **Count:** 3,103 lines, all logged while the Avatar stood near or on them. 2,944 involve shape 1 and 159 involve shape 867.
- **Not from this change** [INFERENCE: FIXED and TYPEFLAG are unchanged in `8a4bfac`, and the full-size Avatar makes most of them]. This is the first session I know of that stood the Avatar there. No visible glitch was caught on a plate.

**5. The first move after the shrink is still lost.** At 6.5 s after the click the ramp had not finished, and the first SW walk did nothing. 2026-10-09 recorded the same.

**6. The left-click-then-right-hold jump at (2576,5900)** (full size, pointer to the N) did not jump in place. The film shows a climb onto something and a drop, and he ended at **(2913,6105,0)**, 337 E and 205 S, on the hall side of the crack line. On that load the crack had already been breached, so this is no boundary breach, and I did not chase it further. It is consistent with the 2026-10-11 trap: the click names a target under the pointer.

## Harness anomalies

1. **`SPACE` (ACTION_JUMP) did nothing** when sent by xdotool, either as `key` or as `keydown`/`keyup` with a 0.3 s hold. The both-button mouse click works.
2. **Every position read eats the potion window.** The chord retries let the game run between attempts, so several planned tiny tests were overtaken by the regrow. Those are re-run above with fewer reads, plus teleports, which pause the game while the console is open.
3. **Default 30 s eval timeout** interrupted the first walk loop once. Nothing was lost but the E and SE reads of that potion.
4. **`scummvm-lv/scummvm` was rebuilt at 18:07** by the main agent, mid-session. My process had loaded the 04:17 image at 17:45, which is the pinned binary. The driver now launches the pinned path.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-tiny-avatar/` (18 plates: T1-×4, T2-×5, T3-×3, T4-×2, T5-×1, F1, F2a, F2b).
- **Scratch** `/tmp/claude-1000/vtiny/`:
  - `game/`, the copy of `shared/u8-lv-patched`;
  - `scummvm.ini`, `saves/` (slot 1 overwritten), `lv_run.log`, `trace.txt`, `estate.log`, `xvfb.log` and `py/vf.py`;
  - in `sp/`: 13 lossless films (`*.mkv`, about 380 MB) and the working plates.
- **Banked nothing** in `~/lv-checkpoints`.
- **Stopped** my ScummVM (pid 830963) and the Xvfb `:93` I started (pid 830957).
- No source, map, fork, `TODO.md` or `HANDOFF.md` edits. No install or build runs.

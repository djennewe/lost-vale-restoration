# Tiny Tar crack and Aramina's retail schedule bit (2026-10-09)

**Build under test.** `main` at `73036a8`, plus the uncommitted lv-patched EZREKAL/TYORVI V2, `test_uc_dialogue`, inventory doc, `build_scummvm.sh`, `ARTIFACTS.sha256` and `map_pins.json`.
- The log reads `Running Ultima VIII: Pagan (Gold Edition + Lost Vale/DOS/English)` and `usecode/eusecode.flx: cd847392987c3e1f6f7b4bc9e4169838, 1525384 bytes`.
- The game copy `/tmp/claude-1000/vca/game` (rsync of `shared/u8-lv-patched`, no `.bak`) matches `shared/build` by sha256: EUSECODE `29fb0c29ab39…`, U8SHAPES `bb0e4cda1e46…`, TYPEFLAG `794d4b80a918…`, ANIM.DAT `77e9705da254…`, and FIXED `13321f0782d1…` in both places.
- Plates are in `docs/playtest-2026-10-09-crack-aramina/`, at 640x400.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| C1 | A Tiny Tar Avatar lined up on the east side of the pale block walks south through the crack; full size at the same spot is refused | **PASS** |
| C2 | Per-step displacement of the tiny Avatar in at least 4 directions | **PASS**: E, W, NE, SW, NW and S, each with a position read after the step |
| A1 | 0x207 takes MORDEA's values 1/2/3 over time; at_home she walks her route (markers 174); 0x663 stays 0 | **PARTIAL**. 1 → 3 was seen at the hour-4 boundary, written by MORDEA. The route walk and 0x663 = 0 PASS. **2 (on_throne, hour 8) is NOT DEMONSTRATED**: the session ended at game hour 5.6 |
| A2 | With 0x207 at 2 or 3 and 0x58 at 0, talking gives "attend to her ladyship", then the find-me-later line, then exits | **PASS for 0x207 = 3**. Not tested at 2 |
| A3 | Pre-Devon dialogue at home: "How may I serve you, stranger?" first, then "Good morrow to you." once met | **PASS** |
| A5 | A Tenebrae checkpoint saved before this build loads and plays | **PASS** (`cp2-palace.sav`, 2026-07-30) |
| L | Log hygiene | **PASS** for LV code: 0 `Unhandled intrinsic`, 0 `stuck in process loop`, 0 Segmentation, 0 Assertion. There are also 17 `Non-existent process PID (0) in implies`, 1264 `Cycle in paint` and 4 `Skipping invalid shape`, all in retail-content contexts (see L) |
| — | `tools/run_all_tests.sh` | **PASS**: `OVERALL: PASS — 43/43` |
| — | Patch equals the fork diff (`ed924d30`) | **PASS**: `PATCH_EQUAL` |
| — | `build_artifacts.sh` / `install_lv.sh` / `build_scummvm.sh` | **SKIPPED** on instruction: they were already run, and another verifier was running in parallel. The sha256 match above stands in for them |

## Method

- **Isolation.**
  - Xvfb `:85` (1280x800); the window sat at (480,300).
  - Scratch dir `/tmp/claude-1000/vca/`, with config `vca/scummvm.ini` (`usehighres=true`) and saves in `vca/saves/`.
  - Command (`vca/run.sh`): `SDL_AUDIODRIVER=dummy scummvm-lv/scummvm --config=… --savepath=… --extrapath=scummvm-lv/dists/engine-data --debuglevel=1 --path=vca/game --save-slot=1 ultima8`.
  - I started and stopped only my own Xvfb and ScummVM.
- **Driver.** The 10-08 `vet` driver `drv.py`/`h.py`, re-pointed to `:85`. I added faster console reads and a fix for the walk reference point (harness anomaly 1).
- **Saves.** Each was copied over `ultima8.001` and loaded:
  - `run-s16-tinytar.sav` was loaded at launch, for C1 and C2;
  - `cp2-palace.sav` was loaded with `Ultima8Engine::loadGame 1`, for A1, A2, A3 and A5.
- **Game-state writes.**
  - Teleports with cheats on, each followed by a toggle back to off (`Cheats = false` is in the log each time).
  - `CameraProcess::moveToAvatar` once: the 09-07 save had a parked camera.
  - `debugflag_enable Object`.
  - `Ultima8Engine::saveGame` (slot 1, my copy) to read the game clock out of the save's `APP` section.
  - **No `setGlobal`. No dev-menu Time.**
- **What was played, not set.** Every drink, drag, pick and talk was a click on the screen.
- **Unthrottled relaunch.** For the period-2 wait I relaunched once with `frameLimit=false` and loaded my own save. It gained only about 1.3× speed on Xvfb (harness anomaly 3).

## C1: through the crack, PASS

`run-s16-tinytar`: templeOpen 0, 0x5B 1, three f8 Tiny Tars (14459, 8603 and 3963) stacked at pack (5,13).

**Getting there.** I teleported to Map 18 (2852,5400) and walked south to (2852,5992). The log shows `Item: 1587 (shape 73) calling usecode event 7 @ 05B1:0080` (EggCrackHint), and the bark is "The stone here is split from top to bottom…" (`C1-00`).

**The empty bottle.** The first drink (C2, potion 14459) left the empty bottle on top of the stack. I dragged it off:
- the first drop bounced (`Dropping object 14459`, then nothing);
- the second logged `Throwing item to (3187, 6175, 95)`.

The same was done later for 8603.

**Negative control, full size, before the positive.**
- At (2844,6064), two 1.2 s south pushes stopped at **(2844,6096)**.
- At x **2852**, the column the tiny Avatar later used, a walk south from (2852,5872) stopped at **(2852,6104)**. A further 1.0 s push stayed at (2852,6104) (`C1-01`).
- The wall face is at y 6112..6143.
- Just before the drink, templeOpen read 0, and stub 3759 (shape 47, (2816,6143,0) q307) and piece 546 (shape 15, (2943,6143,80) q307) were both present.

**Positive, tiny.** The drink at (2852,6104) is a double-click on the stack: `Item: 8603 (shape 859) calling usecode event 1 @ 04E5:00A9`. Each south push lasted 0.5 s and was followed by `objectInfo 1`:

| t (s) | shape | position |
|---|---|---|
| 9.2 | 1 | (2852,6104,0) |
| 12.9 | 867 | (2852,6104,0) |
| 17.1 (S) | 867 | (2852,6104,0), turning or still in stasis |
| 21.4 (S) | 867 | (2852,6104,0) |
| 25.5 (S) | 867 | **(2852,6160,0)**, past the wall line |
| 30.8 (S) | 867 | (2852,6224,0) |
| 41.4 (S) | 867 | (2852,6280,0) |
| 79.8 | 1 | (2852,6280,0), regrown in the sanctum with hp 30 |

- **The egg.** Between the 6104 and 6160 reads, the log shows `Item: 2937 (shape 73) calling usecode event 7 @ 05B0:0080` (EggTempleEntry at (2864,6240), range 8,4, so its box starts at y 6112).
- **The bark.** "I am through. The air in here is old and very still." The tiny Avatar stands on the rubble south of the wall (`C1-02`). Full size again afterwards: `C1-03`.
- **Afterwards.** templeOpen = 1. A wall listing on y 6143 shows **0** q307 records: TEMPLENT's breach removed the stub and pieces, as designed.
- **Why the breach is not what let him through.** The egg could only fire once he was already in the 2817..2879 aperture (y > 6111). The pieces it destroys are at x ≤ 2816 and x ≥ 2880, outside his box, 2821..2852.
- **Plate gap.** On the hall side, the wall south of the Avatar occludes him from the fixed camera. The hall-side evidence is therefore the position reads plus the `C1-00`/`C1-01` views of the pale block.

## C2: tiny per-step displacement, PASS

**First potion (14459), at (2784,5796).** Two of the bursts moved him: W gave (2784,5796) → (2736,5796), which is −48, and S gave → (2736,5852), which is +56. The E and N bursts at 19 s and 25 s did not move him. He had regrown by 66 s.

**Third potion (3963), in the sanctum at (3020,6448).** I took a position read after every 0.6 s burst. A burst that did not move was retried once.

| Burst | Position | Δ |
|---|---|---|
| ready, 21.7 s | (3020,6448) | |
| E | (3076,6448) | **+56, 0** |
| "N" | (3048,6420) | −28, −28, i.e. **NW** |
| W | (2984,6420) | **−64, 0** |
| "S" | (2956,6448) | −28, +28, i.e. **SW** |
| NE (first try / retry) | 0 / (2988,6416) | **+32, −32** |
| SW (first try / retry) | 0 / (2960,6444) | **−28, +28** |

- **Regrow.** He was regrown by 80 s (`C2-03`).
- **The deflected bursts.** The N and S mouse bursts here moved him diagonally. A god crystal stands about 160 units due south of this spot, and rubble lies to the north. [INFERENCE] The mover sidestepped those blockers. C1's pure-S steps (+56/+64/+56, dx 0) show that S itself works.
- **Total.** That is per-step movement in E, W, NE, SW, NW and S.
- **Turning.** The first burst in a new direction often only turns him.

## A5: an old Tenebrae checkpoint, PASS

**The load.** `cp2-palace.sav` (2026-07-30, map 40) loaded: `Reclaimed 0 _objIDs on load.`, followed by the palace plate (`A5-01`).

**State at load.**
- The Avatar was at (12254,7270,48) m40, at game hour 2.74.
- 0x207 = 1, 0x58 = 0, 0x5B = 1, 0x63 = 0, 0x663 = 0, 0x4B6 = 0, and LV araminaMet 0x65F = 0.
- Aramina (13) was on **m41 at (16735,16127,48)**, MORDEA's at_home point (0x415F, 0x3EFF, 48).
- Mordea (7) was at (13151,7999,0) m40.

**Afterwards.** The save then played everything below: teleports, walks, door use, three conversations, two hour transitions, saves, and a reload in a second launch.

## A1: route and MORDEA's values, PARTIAL

**At home (0x207 = 1).**
- **Arrival.** I teleported to m41 (16700,14300,48), about 1,800 units from her house. The log shows `Item: 13 (shape 282) calling usecode event 15 @ 040D:01D2` (enterFastArea).
- **Processes.** `Kernel::listProcesses` shows `Process 839 … item 13, type 205, classname: ARAMINA, IP: 040D:04B8`, which is inside 0x0447. That is the function enterFastArea spawns when `0207h == 1` (atHome). There is also a PathfinderProcess 768 for item 13.
- **The route.** I took 14 position reads over 89 s and matched each to the nearest shape-174 marker on m41:

  | Frame | Marker position |
  |---|---|
  | f0 | (16639,16159) |
  | f1 | (17078,16170) |
  | f2 | (17100,15780) |
  | f3 | (17172,15444) |
  | f4 | (16639,15583) |
  | f5 | (16479,15903) |

  The reads visited 4 → 5 → 0 → 2 → 3 → 4 → 0 → 2 → 4 → 4 → 5 → 1 → 3, which is the 0-5 loop, sampled. The distance to the nearest marker was 21-206 units.

**Value change, 1 → 3.**
- **Setup.** I left the house to m41 (16632,14304), more than 700 units from her.
- **Timing.** At hour 3.57 (read from the save), I polled 0x207 every 50-60 s. It read 1 for 414 s, then **3** at 473 s.
- **Log order:**
  ```
  24941: Item: 7 (shape 189) calling usecode event 8 @ 0407:013B   (retail MORDEA schedule)
  24954: Item: 13 (shape 282) calling usecode event 16 @ 040D:0258 (Aramina leaveFastArea: teleported out)
  24967: Item: 13 (shape 282) calling usecode event 8 @ 040D:016B (her own schedule; returns, 0x58 = 0)
  ```
- **Where she went.** Aramina is now at **m40 (14106,11007,48)**: MORDEA's chow_down point, from the canSafeTeleport branch that writes `0207h = 3` at 05C6.

**Value 2: NOT DEMONSTRATED.** It needs hour 8. The last save read hour 5.60, with 0x207 still 3.

**0x663 / 0x4B6.** 0x663 read 0 at load, after the 1 → 3 change, and at the end. 0x4B6 read 0 throughout. Nothing set 0x207: all its values came from MORDEA.

## A3: pre-Devon dialogue at home, PASS

**Talk 1.** With 0x207 = 1, 0x58 = 0 and 0x65F = 0, a double-click logged `event 1 @ 040D:10E9`. It gave:
- **"How may I serve you, stranger?"** (`A3-01`);
- the menu **By what are you called? / bye** (`A3-02`);
- then "My name is Aramina." (`A3-03`), and the menu **What do you do here? / bye** (`A3-04`);
- then bye, and "Thank you, sir."

**After talk 1.** 0x65F = 1, but retail 0x203 is still 0 (finding 1).

**Talk 2.** **"Good morrow to you."** (`A3-05`), then the menu **Have you met Devon? / What do you do here? / bye** (`A3-06`).

## A2: busy with her ladyship, PASS at 0x207 = 3

- **Getting there.** I teleported to m40 (13850,10750,48) and walked into the kitchen. Aramina moved between the kitchen and Mordea's table, where Mordea barked "Too much salt!".
- **The talk.** A double-click on her logged `Item: 13 (shape 282) calling usecode event 1 @ 040D:10E9`. It gave:
  - **"I am sorry, but I can not talk to you now. I must attend to her ladyship."** (`A2-01`);
  - **"Find me later at my house in east Tenebrae, I will be there at Bloodwatch."** (`A2-02`).
- **The exit.** No ask menu appeared in the 8 s of frames that followed, and she walked off.
- **Flags at the time.** 0x207 = 3, 0x58 = 0.
- **The value-2 case** was not reached.

## L: log hygiene

`vca/lv_run.log` has 29,264 lines over both launches.

| Pattern | Count | Context |
|---|---|---|
| `Unhandled intrinsic` | 0 | |
| `stuck in process loop` | 0 | |
| Segmentation / Assertion | 0 / 0 | |
| `Non-existent process PID (0) in implies` | 17 | All within about 300 lines of the m40 kitchen arrival, each right after `LV: I_resetRef item=16607 type=0x00F0`. Item 16607 was not identified |
| `Cycle in paint dependency graph 426 -> 208` | 1264 | All in the `run-s16-tinytar` Map 10 view (old save) before the Map 18 teleport |
| `Skipping invalid shape in sorter` | 4 | `539,4` once on loading `run-s16-tinytar` (known). `114,120..122` on re-entering m41, next to `Destroying orphaned ethereal object (6745)` (shape 174 at (0,0,0)) and `popToContainer to invalid container (81)` (item 81, shape 574, retail class 0x23E) |

The implies warnings and the m41 warnings came from classes not in `modified_base_classes` (AORTA, ARAMINA, AVATAR, FLAGS). That attribution is [INFERENCE] from class ids. I did not trace item 16607.

## Findings

1. **Meeting Aramina sets LV bit 0x65F, not retail 0x203.** After the first talk, 0x65F = 1 and 0x203 = 0. This confirms batch-b finding 1 in-engine: her other flags are still LV-only, so retail code never sees that she has been met, and the reverse holds too.
2. **MORDEA moves Aramina only when canSafeTeleport passes**, which needs the Avatar more than 700 units from her and from her destination, or on another map. A player standing beside her at a period boundary keeps the old 0x207. This is retail behaviour, and it is why 0x207 lags the clock in several checkpoints. For example, `run-s16-tinytar` is at hour 8 with 0x207 = 3.
3. **The first drink window is easy to waste.** After the shape turns 867, the first one or two pushes are lost: the shrink keeps the stasis, and the first burst turns him. The C1 potion still crossed with time to spare (crossed at about 25 s, regrew at about 80 s).
4. **The tiny Avatar can stand in the aperture at x 2852.** That is 4 units inside the 2848..2879 strip, which full-size walking from x 2852 lands on naturally. A player lined up "hard against the east side of the pale block" at that x crosses without any fine adjustment.

## Harness anomalies

1. **The mouse-walk reference is (320, 214), not the window centre.** `Mouse::getMouseDirectionWorld` uses `height/2 + 14`. The `vet` driver's `walk()` aimed from (320, 200), which bent W into NW (one burst went (3048,6092) → (2724,5872)). With the reference corrected, E/W/S bursts are pure.
2. **The first mouse burst after a console close often does nothing.** A 0.7 s sleep before the burst helps.
3. **`frameLimit=false` gave only about 1.3× game speed on Xvfb.** 16 minutes advanced the clock from hour 4.37 to 5.60. So it is no shortcut for the hour-8 wait: budget about 40-55 real minutes per 4-hour period.
4. **`findShape 15` listed only a subset of the 265 records** (8 on y 6143), so a q307 count from it is a lower bound.
5. **Talking works at long range here.** The first Aramina talk landed with her about 540 units away. Grey-dress pixel matching ((189,189,189) and (172,173,172)) found her sprite reliably for strikes on a walking NPC.
6. **`Ultima8Engine::saveGame <name>` always writes slot 1.**

## Still needed

- **A1 value 2 and A2 at value 2.**
  - Load `/tmp/claude-1000/vca/sp/vca-after-A2-period1.sav` (hour 4.29, 0x207 = 3, Avatar on m41 (16650,14300)), or the slot-1 save at hour 5.60.
  - Stay more than 700 units from Aramina, or off m40, until hour 8: about 36-55 real minutes.
  - Expect 0x207 = 2 and Aramina at MORDEA's on_throne point on m40, then talk to her for the same two barks.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-09-crack-aramina/` (17 plates: C1-*, C2-*, A2-*, A3-*, A5-*).
- **Scratch in `/tmp/claude-1000/vca/`:**
  - `game/`, `scummvm.ini` (now carries `frameLimit=false`), `run.sh`, `xvfb.log` and `lv_run.log`;
  - `saves/` (`ultima8.001` is my hour-5.60 Tenebrae save; the engine also wrote `ultima8.000` and `timestamps`);
  - `dis/` (LV 0x40D, 0x407, 0x57C and 0x581 disassemblies);
  - `fork.diff`, the driver in `py/`, and frames plus `vca-after-A2-period1.sav` in `sp/`.
- **Not touched:** `shared/`, `~/lv-checkpoints` (read only), `~/.config/scummvm`, and every source, builder, map, fork, TODO or HANDOFF file. Nothing was committed.
- **Stopped:** my ScummVM and Xvfb `:85`.

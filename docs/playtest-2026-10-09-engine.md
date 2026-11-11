# Engine fixes: exitConvo restart, invisible abort, blocked-jump hit point, Sigrid/Atli starts (2026-10-09)

**Build under test.** `main` `909206d` plus the uncommitted `ARTIFACTS.sha256`, `build_scummvm.sh` and engine patch.
- **Game copy.** `/tmp/claude-1000/veng/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Every hash matches `shared/build/ARTIFACTS.sha256`: EUSECODE `49f44ee3a16c…`, U8SHAPES `69fbd86123e8…`, TYPEFLAG `6bdb303654a5…`, ANIM `77e9705da254…`, and FIXED `511902e8e753…` in both places.
- **Log line.** `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1523441 bytes`.
- **Binary.** `scummvm-lv/scummvm` is dated 22:40:35, which is after fork `bbcfa209` (22:29:19).
  - The build tree carries both changes: `animation_tracker.cpp:297` reads `GetInterpolatedCoords(start, end)`, and `item.cpp:3156` has the `I_enterFastArea` branch.
- **Patch check.** The tracked patch equals the fork diff. The command printed `PATCH_EQUAL`.
- **Harness.**
  - Xvfb `:91` (1280x800), with the window at (480,300).
  - `scummvm.ini` sets `frameLimit=true` and `usehighres=true`.
  - The driver is the `vconvo` `drv.py`/`h.py`, re-pointed to this display and directory, with the mouse-walk reference at (320,214).
- **Plates.** They are in `docs/playtest-2026-10-09-engine/`.
- **Not run, on instruction:** `run_all_tests.sh`, `build_artifacts.sh`, `install_lv.sh` and `build_scummvm.sh`. The hash match above stands in for them.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| E1 | After talk + bye, each talked-to NPC has exactly one activity process. Stasis is false. 0x0F reads 1 during and 0 after. No `PID (0)` implies per farewell | **PASS**, 9/9 NPCs (table below) |
| E2 | Retail Devon and Orlok get their activity back after bye | **PASS** |
| E3 | Invisible talk gives "Is someone there...?", no menu, and the NPC is not frozen | **PASS** |
| E4a | Map 39 tunnel: UP+SPACE at both side walls never passes through or wedges, and the tunnel still walks end to end | **PASS**: 0 of 24 jumps passed through or wedged |
| E4b | Pool-stone hops G→H→I, the cave ascent, and a low-ledge jump | **PARTIAL**. Hops **PASS** (plus I→J). Cave ascent **PASS** 5/5, with both controls refused. **Two behaviours differ from the earlier reports** (findings 1 and 2). The low-ledge jump was **NOT DEMONSTRATED** (see E4b) |
| E5 | On a fresh Map 10 load, Sigrid is at (4896,8992,0) and Atli at (19232,6944,0), on open ground | **PASS** |
| L | Log hygiene | **PASS**. In 12,856 lines there are 0 `Unhandled intrinsic`, process-loop, Segmentation, Assertion, segment-access or `Cycle in paint` lines. There are 3 `PID (0)` implies lines, none of them at a farewell (finding 3) |

**State writes.** Teleports with cheats on, each followed by a verified `Cheats = false`. `debugflag_enable Object` after each load. `Item::grab 5153` (the potion, for E3). `toggleAvatarInStasis` in pairs, plus one single toggle that undid a harness inversion (anomaly 1). `saveGame` once, to my own slot. Every talk and every answer was clicked on the screen.

## E1: the LV NPCs, PASS

**Aramina** (`cp2-palace.sav`, m41).
- Before the talk: `UCProcess type 205 ARAMINA 040D:04B9`, plus a PathfinderProcess.
- During: `type 207 040D:15B2`, with 0x0F = 1.
- After **bye**: `Process 42 UCProcess type 205 ARAMINA 040D:04B9`, a PathfinderProcess, no LoiterProcess, and 0x0F = 0.
- 15 s later it was the same single process, and she had moved (16643,15841).

**The eight Vale NPCs.** The same world was hopped into Map 10 for the first time. That is the E5 load, at hour 2 (bloodwatch).

| NPC | Talk event | During (0x0F) | After the farewell | 0x0F after | `PID(0)` |
|---|---|---|---|---|---|
| Sigrid 102 | `0466:0231` | type 207 (1) | LoiterProcess 6602 only | 0 | 0 |
| Thordis 106 | `046A:0E71` | 207 (1) | LoiterProcess 7412, plus THORDIS type 205 `08FC` (the one-shot `randomBarkAtHome`, which `Thordis::enterFastArea` spawns, `THORDIS.UNK:347-348`) | 0 | 0 |
| Tyorvi 115 | `0473:0354` | 207 (1) | LoiterProcess 2168 only | 0 | 0 |
| Ragnar 105 | `0469:0237` | 207 (1) | LoiterProcess 4876 only | 0 | 0 |
| Ezrekal 116 | `0474:034A` ("A PAGAN!!" refusal) | 207 (1) | LoiterProcess 1384 only | 0 | 0 |
| Atli 107 | `046B:0392` | 207 (1) | LoiterProcess 3101 only | 0 | 0 |
| Ingjald 112 | `0470:0934` | 207 (1) | LoiterProcess 5334 only (no bark process caught) | 0 | 0 |
| Hrodny 113 | `0471:0D5B` | 207 (1) | LoiterProcess 6828 with its Pathfinder/Anim children; later, 6828 only | 0 | 0 |

- **Stasis.** It read false after every completed farewell, by a toggle pair returning `true, false`.
- **The restart is the new path.** Each farewell logs `event 15 @ <class>:…` (enterFastArea) inside the farewell window.
- **No duplicates.** No NPC had two LoiterProcesses.
- **Plates:** `E1-<npc>-01-talk`, `-02-menu` and `-03-bye`.

## E2: retail Devon and Orlok, PASS (both on Map 39 in this save)

**Devon (NPC 2).**
- Before: `LoiterProcess 1245`.
- During: `UCProcess type 207 DEVON 0402:08D0` with 0x0F 1. The loiter process was killed.
- After **Goodbye.**: `LoiterProcess 1105` (plus its Pathfinder/Anim children), with `event 15 @ 0402:0261`, 0x0F 0, stasis false, and 0 implies lines.
- Plates: `E2-devon-01..03`.

**Orlok (NPC 10).**
- Before: `ORLOK type 205 040A:042C` and its child `040A:0841`.
- During: `type 207 040A:2113`, 0x0F 1.
- After **Goodbye.**: `ORLOK type 205 040A:042C` and its child `040A:099B`. This is the same shape as before the talk, with `event 15 @ 040A:0170`, 0x0F 0 and 0 implies lines.
- Plates: `E2-orlok-01..03`.

## E3: invisible Avatar, PASS

- **Setup.** This world had never loaded Map 10, so `findShape 859` listed `5153 f7 (21280,8832,0)`. I used `Item::grab 5153`, then double-clicked it in the pack.
- **The drink.** The log shows `event 1 @ 04E5:00A9`, and the Avatar's flags went 0x2441 → **0x2455**.
- **The talk.** The double-click on Hrodny (`event 1 @ 0471:0D5B`) barked **"Hello...?"** then **"Is someone there...?"**. No menu opened, and the Avatar was not drawn (`E3-02-invisible-talk-sheet`). The log showed `event 15 @ 0471:02C4` at once.
- **Right after.** Hrodny had `LoiterProcess 7382` with its Pathfinder/Anim children. 0x0F read 0, and there were 0 implies lines.
- **She moved.** Over 6 s she read (21677,8215) → (21917,8335) → (21857,8875). This is the negative of the 10-09 convo finding 1, where she had an empty list and stood still for 34 s.
- **Control.** The visible talk in E1 gave her normal menu.

## E4a: Map 39 tunnel, PASS

- **Setup.** `run1009b-s01-lb-done.sav`, then a walk from (17046,19922) to the tunnel's south mouth.
- **Positioning.** The flush positions were set by teleport (x 16222 east, x 16160 west), because the walk gait steps 32 units and stops at 16214. The facing came from a mouse walk into the wall.
- **The input.** I pressed Up first, then SPACE 60 ms later. SPACE first gives `jumpUp` in place (anomaly 2), so the first 14 attempts, made that way, are not counted.
- **Positive control.** At the lane C1 spot (16334,19450), facing west, the same input jumped **(16334 → 15822, z 48)**. That is 512 units, against lane C1's ~450, so the input does produce a real jump.

| Jumps (UP then SPACE) | Result |
|---|---|
| E flush, y 19950/19870/19802/19710/19650, held 0.35 s | ended **x 16223** (touching the wall, which spans [16223,16255)), z 48, or did not move |
| W flush at the same y | ended **x 16159** (touching the wall's x 16095 face), z 48 |
| E/W flush at y 19802, held 1.0 s and 2.5 s | the same: 16223 / 16159 |
| 28-34 units clear of the wall (E at 19710 and 19950; W at 19870, 19710 and 19650) | stopped at the wall, or short of it, at z 48 |
| Retail niche C2 (16222,19554) E / C3 (16098,19534) W | **16223 / 16095**, z 48. Lane: through the wall to z 0 / wedged at z 56 |

- **No failures.** None passed through or wedged. 0 `stuck in process loop`, 0 `Cycle in paint`.
- **Mobility.** A mobility burst after every flush jump moved the Avatar 32 units north and back.
- **The walk.** The tunnel walks from (16194,19400) to **(16194,20072)** at z 48, 32 units per burst with no stall (`E4a-tunnel-walk-south-end`).
- **Sheets:** `E4a-flush-*-sheet`, `E4a-C2-*`, `E4a-C3-*`, `E4a-C1-replica-*`.

## E4b: regression checks, PARTIAL

**Pool-stone hops (`run1009-s00-map8-pool-stone-g.sav`), PASS.** These are SPACE targeted jumps. Each aim pixel was checked first by a probe click that logged the stone.

| Hop | Aim (x,y,8) | Landed | Probe |
|---|---|---|---|
| G → H (7941) | (30794,21734) | **(30793,21734,8)** | `Item 7941 … STANSTON` |
| H → I (2046) | (30797,22130) | **(30797,22130,8)** | `Item 2046` |
| I → J (2150), extra | (30575,22351) | **(30575,22352,8)** | `Item 2150` |

- **The first tap only turns** the Avatar toward the cursor (`checkTurn`). The second tap jumps. hp stayed 30.
- **Plates:** `E4b-00-on-G`, `-01-on-H`, `-02-on-I`, `-03-on-J`, and the per-hop sheets.

**Cave ascent (part C protocol), PASS.** I teleported to (x,23622,0), did a 0.3 s walk west, then pressed SPACE and, 60 ms later, Up, both held 1.6 s.
- **In the window:** x 29516, 29508, 29524, 29512 and 29520 all ended at **z 56**, at x 29356-29364 (`E4b-cave-climbed`).
- **Controls:** x 29500 and 29532 did not climb, as before. But see finding 1.

**Low-ledge jump: NOT DEMONSTRATED.**
- **The candidate.** The 09-01 48-unit gate wall at (29241,30353) did not climb.
- **Why it failed.** The current Map 8 FIXED stacks a second shape-32 piece at z 48 on that wall (x 29311, y 30367-30751), so its top is z 96, not 48. That route note is stale (finding 4).
- **The search.** A search of Map 8 for a 16-40 unit land ledge on a z-0 floor found 0 candidates. The budget ended there.

## E5: Sigrid and Atli starts, PASS

- **The first load.** cp2-palace's world had never loaded Map 10. On the first Map 10 entry the log reads `LV: Created actor npc 102 … at (4896,8992,0)` and `… npc 107 … at (19232,6944,0)`.
- **Immediately after the entry's `event 8` (schedule)**, they read **(4895,8991,0)** and **(19231,6943,0)**: each schedule point, 1 unit off. Nothing used (7680,6400) or (19200,6400).
- **The snap path.** A Map 11 → 10 hop logged `LV: Slot 102 … updating pos to (4896,8992,0)` and `Slot 107 … (19232,6944,0)`.
- **Open ground.** `E5-01b-sigrid-start-marked` and `E5-02b-atli-start-marked` mark each start (yellow) on cobble and grass:
  - Sigrid's start is clear of every hut;
  - Atli's is south-west of his hut corner, outside it (the old start was inside the hut).
  - Both NPCs are loitering nearby in the plates.

## L: log hygiene

`veng/lv_run.log` has 12,856 lines. There are 0 `Unhandled intrinsic`, 0 process-loop, 0 Segmentation, 0 Assertion, 0 segment-access, 0 `Cycle in paint` and 0 `popToContainer` lines. There are **3** `Non-existent process PID (0) in implies` lines, each right after `skipping bark of '…' because item invalid` (finding 3). The farewell count is **0 in 11 farewells**, plus the invisible abort.

## Findings outside the brief

1. **A SPACE-first press that does not climb now barely moves the Avatar.** Part C's out-of-window controls walked about 600 units; here, at the cave, they move 0-200.
   - **The measurements.** At x 29500 with the 1.6 s protocol:
     - Up alone: −696;
     - SPACE then Up: **−104 and 0** (and −96 / −200 in the c1/c2 runs);
     - Up then SPACE: −536.
   - **Reading** [INFERENCE]. With SPACE first, the jump-alone branch makes a cursor-targeted jump. Its arc meets the overhang and now stops at the hit point; before, it was pushed past it. The Avatar stays mobile and no process looped.
   - **Impact.** Effectively none: a player who misses the climb window loses a few hundred units of walk.
2. **A keyboard jump at the cave can now land at z −4.**
   - **The evidence.** From (29500,23622,0), Up then SPACE ended at **(28964,23622,−4)**, twice. The Avatar walks in all four directions at z −4.
   - **History.** The 09-25 research (Q5) recorded no z<0 case.
   - **Reading** [INFERENCE]. An arc whose rise is clipped by an overhang now loses the clipped rise, but still plays the full descent. So the jump ends below its start z.
   - **Risk.** At z ≤ 0 the freebie support hides it. On a raised floor under a low overhang the same thing would end the jump inside the floor. **No such case was found or tested.** The tunnel's lengthwise jump landed level at z 48, (16194,19600) → (16194,19935).
   - Worth a look by the author. Confidence in the observation: high. Confidence in the mechanism: medium.
3. **Three `PID (0)` implies lines come from a retail Tenebrae scene, not a farewell.**
   - **The lines.** At lines 2943, 2972 and 3038, each is preceded by `skipping bark of 'Really, I was at home with my poor, sick mother.'` (or "Please sir, I have no more money." / "But-but who will feed my children?") `because item invalid`. They fired while I was teleporting around Map 39.
   - **Reading.** This is the retail bark/implies family with an absent speaker; it is not exitConvo.
4. **The 09-01 route note "climb the 48-unit gate wall at x 29241" is stale.** The wall at x 29279-29311 now has a z-48 piece on top (FIXED Map 8), and the climb from (29241,30353) does nothing. Confidence: high on the data; I did not check when it changed.
5. **The Map 8 pool hops land exactly on the aim** (3 of 3, at 340-396 units). The 10-09 full run's "shortfall is not a fixed function of range" (its finding 3) may have been the old interpolation [INFERENCE].

## Harness anomalies

1. **A stasis toggle pair can invert stasis.** A pair taken while exitConvo was still finishing left the Avatar in stasis: Ezrekal's refusal path (`event 15` logged, toggles `false,true`, then exitConvo's own `setAvatarInStasis(0)` landed between my two toggles). The next clicks logged `Can't use: avatarInStasis`. One toggle fixed it. Afterwards I read stasis only once 0x0F read 0.
2. **The keyboard jump needs Up before SPACE.** SPACE first, with the cursor near the Avatar, gives `jumpUp`, which jumps in place. The cave climb recipe (SPACE first) still works, because the climb scan runs in both branches.
3. **Strikes on loitering peasants missed** with standstill reads. A single read followed by an immediate double-click worked.

## Disk changes

- **Wrote** this report and 75 plates and sheets in `docs/playtest-2026-10-09-engine/`.
- **Scratch** in `/tmp/claude-1000/veng/`:
  - `game/`, `scummvm.ini`, `run.sh`, `lv_run.log` and `xvfb.log`;
  - `saves/` (`ultima8.001` is now the Map 8 world; the engine wrote `ultima8.000`);
  - `sp/` (frames, and `t-tunnel-s.sav`);
  - `py/`, `flags.py` and `savinfo.py`.
- **Stopped:** my ScummVM and Xvfb `:91`. Nothing else was touched.
- **Not touched:** source, builders, maps, the fork, `shared/`, `TODO.md`, `HANDOFF.md` and `~/lv-checkpoints` (read-only).

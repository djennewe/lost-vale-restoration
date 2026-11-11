# Playtest 2026-10-11: the gated Vale return (212), regrow beside a wall, quest-item respawn guards

Verifier pass on main `e5a36dd`, covering commits `f99b9a9` (EggValeReturn), `3212730`/`4219a4c` (regrow, FREE.UNK fixes 4-5) and `b931fb4` (EggReapply carryables, plus the SHADES and PLNTST latches). The setup:

- **Display and ini.** Xvfb `:93`, ScummVM at 320x200 ×2, `frameLimit=true`, muted, `SDL_AUDIODRIVER=dummy`, and no width/height keys.
- **Binary.** A copy of `scummvm-lv/scummvm` in `/tmp/claude-1000/vgate2/bin/` (sha256 `21f07b14…`, built 20:33, after fork commit `e48f8716` at 20:31).
- **Game copy.** An isolated copy of `shared/u8-lv-patched`, `u8monsters.ini` included. Its hashes matched `ARTIFACTS.sha256` at the start and again at the end: EUSECODE `f0a9e709` (the log reads md5 `84615e29…`, 1,528,216 bytes), FIXED `9552dee0` (root and `STATIC/`), U8SHAPES `e0af51ea`, TYPEFLAG `7c1d8454`, ANIM `696dbeb9`.
- **Driver.** `/tmp/claude-1000/vgate2/py/vg.py`, which is replay leg 1's `rp.py` with `PRIME = False`. A throwaway left click on empty ground came at least 1.2 s before every right-button hold.
- **Map hops.** Every placement, egg and trigger judgement was made after a map hop. Each arrival named below shows `Loading Fixed items in map N` in the log.

**Cheats used.** All of them are listed here, and none was used for a G1 walk or run:

- `Cheat::toggle`.
- `MainActor::teleport`, only to position the Avatar or to hop maps. Each one is named below.
- `Cheat::toggleInvincibility on` and `Cheat::heal`, in one G1a load only, against the 808 spitters.
- `Item::grab`: the bag's Passage stone (23410) and the two shield halves (17701 and 29987).
- `UCMachine::setGlobal`, for the latch tests and their controls: `shieldFixed` (bit 1033), `haveMark` (1041) and `givenRoot` (1063).
- `Ultima8Engine::toggleAvatarInStasis`, toggled twice by a regex miss, with the state restored.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| G1a | Flag 0: walking or running over the Map 8 slab does nothing, leg 2's repro run included | **PASS** |
| G1b | Flag 1: walking onto the slab sends the Avatar to Map 10's pad 212 | **PASS** |
| R1 | Regrow flush against the hall relief at (2592,5792,8): he survives, shifted about 32, and the camera glides back without a snap | **PASS** |
| R2 | The pre-breach crack death still happens | **NOT DEMONSTRATED**: it is not reachable without cheats (R2) |
| Q1-17a | After the ceremony (shieldFixed), re-entering Map 17 shows no halves | **PASS** |
| Q1-17b | With the halves in the pack, re-entering Map 17 shows none on the floor | **PASS** (negative control: 2 on the floor when not carried) |
| Q1-17c | A second ceremony cannot run | **PASS** with a manufactured state: no natural path gives halves after shieldFixed (Q1-17c) |
| Q1-10a | After givenRoot, the root does not respawn | **PASS** (control: it does when givenRoot = 0) |
| Q1-10b | The Passage stone does not respawn after use, and the Test cannot replay | **PASS** (controls for both) |
| Q1-11 | Used talismans do not respawn on Map 11 | **PASS** (static control: FIXED holds all 4) |
| L | Log hygiene | **PASS for these changes.** Pre-existing items and one new paint cycle are listed below (finding 4) |
| Estate | `tools/run_all_tests.sh` | **PASS, 52/52**, in two invocations: finding H1 |
| Fork | Patch equals fork diff | **PASS**: `diff -q` clean, and `test_scummvm_patch_sync` 3/3 |
| Build | `tools/build_artifacts.sh` | **NOT RUN**: the brief bars build scripts. The loaded bytes match `ARTIFACTS.sha256` |

## G1a: flag 0, the slab does nothing. PASS

**Save.** `replay1011-s02d-m8-pocket-t212-repro.sav` (md5 `01106c08`, which matches leg 2's table). Map 8 (18164,5020,0), hp 30, `allColumnsDestroyed` (bit 1772) = 0. `givenRoot`, `haveMark` and `shieldFixed` were all 0 too.

**A0, the negative control: no hop.** The save still carries the old engine teleporter, `Item 7173 (class TeleportEgg, shape 508) (20575,3903,0) q: 468, n: 17`. Leg 2's run (a held mouse run E 3.54 s, then N 2.5 s) logged `Unloading map 8` → `Loading Fixed items in map 10` and ended on **Map 10 (13824,2456,0)** (`G1-A0-noHop-control-end`). So the run does cross the slab's box, and the stale-save trap is real (finding 1).

**A1, after the hop: the repro run.**
- **Hop.** I reloaded the save and teleported to Map 9 (13696,13408,0) and back to the pocket (18164,5020,0).
- **The egg.** `findShape 73` shows `Item 4077 (class Egg, shape 73) (20575,3903,0) q: 308, n: 17, range 1,1`. `findShape 508` has nothing at that spot.
- **The run.** The same input: E 3.54 s, then N 2.5 s.
- **Log.** `Item: 4077 (shape 73) calling usecode event 7 @ 05B3:0080` (class 1459, EggValeReturn), with no map unload.
- **End state.** Map 8 (20564,3796,0), north of the slab, which he ran across (`G1-A1-repro-run-end-flag0`). There was no bark. `objectInfo 4077` then read `hatched=1`, which is the engine's latch until the egg leaves the fast area.
- **Death.** Two 808 spitters then took hp 30 → 11 → dead. That is the known leg-2 finding 2 balance issue, not this change.

**A3, a walk onto the slab, on a fresh load.**
- **Setup.** Invincibility on, then a hop: Map 9, then Map 8 (20575,4250,0), which snapped to (20614,4211,0).
- **The egg.** It was a fresh copy (`Item 2819 … q: 308 … hatched=0`).
- **The walk.** A walk-gait hold N for 1.6 s → (20619,3838,8), across the box (x [20543,20671), y [3871,3999)).
- **Log.** `Item: 2819 (shape 73) calling usecode event 7 @ 05B3:0080`, and nothing else.
- **4 s later.** Still on Map 8 (20784,3673,8), with `[06EC 01] = 0` (`G1-A3-walked-onto-slab-flag0`).

## G1b: flag 1, the slab sends him to Map 10's pad 212. PASS

**Save.** `run1010-s04e-m10-arrival-step4-done.sav`: Map 10 (12800,2560,0) on pad 205, `allColumnsDestroyed` = 1.

**Reaching Map 8, on foot with no cheats.**
- A walk N for 3.0 s from pad 205 crossed trigger 213.
- The log shows `Unloading map 10` → `Loading Fixed items in map 8`, and he arrived at **Map 8 (20143,3143,8)**, in the niche (`G1-B1-m8-arrival-via-213`).
- `findShape 73` shows the fresh `Item 1278 … (20575,3903,0) q: 308 … hatched=0`, and `findShape 508` has no TeleportEgg there.

**Walking to the slab.**
- The walk legs were SSE → (20195,3315,16), SSE again → (20855,3975,8), then W → (20759,3975,0).
- The last W leg logged `Item: 1278 (shape 73) calling usecode event 7 @ 05B3:0080`, then `Unloading map 8` → `Loading Fixed items in map 10`, then `Item: 2052 (shape 73) calling usecode event 7 @ 05B2:0080`. That last one is EggReapply, which sits on pad 212.
- He ended on **Map 10 at (13624,2560,0)** (`G1-B2-after-slab-flag1`).
- Pad 212 is (13824,2560), and pad 205 is (12800,2560). The 200-unit offset at the same y fits the W hold continuing after the landing [INFERENCE: I took no read between the landing and the release]. The EggReapply hatch is pad 212's egg.

## R1: regrow beside a wall. PASS

**Setup.**
- **Save.** `run1010-s17a-m18-arrival.sav`, holding three f8 Tiny Tars.
- **Hop.** Map 18 → Map 17 (5376,10936) → Map 18 (2524,5900,0), by teleport.
- **The drink.** I double-clicked Tiny Tar 25459 in the pack: `Item: 25459 (shape 859) calling usecode event 1 @ 04E5:00A9`.
- **Recording.** The whole run was filmed lossless at 25 fps (`sp/R1-regrow2.mkv`).

**The walk.** At 17 s, a walk-gait hold N for 2.0 s left him as shape **867** at **(2592,5792,8)**, flush against the relief/statue (`R1-tiny-at-wall`). There was no input after that.

**The outcome.**
- The read at 72 s: **shape 1, frame 3, at (2592,5824,8)**, hp 30, flags `400`. There was no death book and no `Here lies` (`R1-after-regrow`). That is a shift of +32 in y.
- In the 2026-10-11 tiny-avatar report (finding 2, plate `F2b`), the same spot and input killed him.

**The camera.** I measured it by phase correlation between consecutive frames of the film. Every step correlated at 0.89 or better.
- **The regrow ramp** (38.6-40.6 s): 16 steps of +2 window px, a drift of +32 px.
- **The end of the ramp** (40.88-41.68 s): 17 steps, each at most 4 window px (2 game px). They sum to dx +16, dy −40. That is the −32 drift undone, plus the view following the +32 world-y shift, which is (−8, +4) game px ×2.
- **No snap.** No single-frame move bigger than 4 px occurs after the ramp (`R1-regrow-glide-sheet`). The shrink's end glides the same way (10.36-11.12 s, 15 steps).
- **The old behaviour, for comparison.** Before the fix it moved 32 window px in one frame (tiny-avatar finding 1).

**First attempt.** It drank at (2592,5900) and walked N straight past the plinth to (2592,5604,0), with no wall contact. That regrow was in open floor and proves nothing. It was filmed as `sp/R1-regrow.mkv`.

**Not tested.** The west-wall case (sanctum wall (2576,6175)) and a corner that needs the +32/+32 attempt.

## R2: the pre-breach crack death. NOT DEMONSTRATED

**It is not reachable without cheats.** The pinned FIXED has:
- the crack wall: q307 shape 15 at (2815,6143) and shape 47 at (2816,6143), which fill y (6111,6143];
- EggTempleEntry: q305 at (2864,6240), npcnum `0x84`, so a box of x ±256 and y ±128.

The engine hatches it when `6240−128 ≤ y` (`egg_hatcher_process.cpp:83`). So any anchor at y ≥ 6112 and x in [2608,3184) hatches it and breaches the wall. A tiny body (anchor at the max corner, box (y−32, y]) cannot overlap the wall band without an anchor at y ≥ 6112. The 2026-10-11 tiny-avatar run (T4) reached the same conclusion in-engine. I did not cheat the Avatar into the crack.

## Q1: respawn guards

The EggReapply hatch (`event 7 @ 05B2`) was logged on **every** pad arrival in the session:
- Map 10 pad 212 (log line 7357);
- Map 11 pad 204 (7712, 9984);
- Map 10 pad 205 (7905, 10144);
- Map 17 pad 209 (8534, 8873, 9149).

The cheat-teleport arrivals (onto Map 10 at the court or the circle, and onto Map 18) logged none, because they land outside a pad's box. See finding 2.

### Q1-17a: shieldFixed, no halves. PASS
- **Save.** `run1010-s15-m10-shield-restored-cured.sav`, with all four flags at 1 (bits 1772, 1063, 1041 and 1033).
- **Route.** A teleport to Map 13 (4096,600,120), then a walk N for 1.8 s into trigger 209. That logged `Loading Fixed items in map 17` and landed him on **Map 17 (5376,11136,0)**.
- **Result.** `findShape 870: 0 found` (`Q1-M17-entry-shieldFixed1-no-halves`).

### Q1-17b: halves carried, none on the floor. PASS
- **Save.** `run1010-s13c-m17-cloud-city-arrival.sav`, with shieldFixed 0. It was hopped on foot: S into trigger 208 → Map 13 (4096,640,120), then N into 209 → Map 17 (5376,10936).
- **Control.** `findShape 870` found 2 on the floor: `17701 f1 (7232,1568,0) q82` and `29987 f0 (6208,1568,0) q81` (`Q1-M17-control-halves-on-floor`).
- **Carried.** `Item::grab 17701` and `Item::grab 29987` took the weight 30 → 90. The same on-foot hop out and back followed.
- **Result.** `findShape 870: 2 found`, both `(0,0) f: 0xc` (in the pack), and **none on the floor** (`Q1-M17-halves-carried-none-on-floor`).

### Q1-17c: a second ceremony cannot run. PASS (manufactured state)

**Why the state had to be manufactured.** Once shieldFixed is set, the 17a guard leaves no halves to collect. So I gave the latch its worst case: both 870 halves in the pack, plus shieldFixed set by `setGlobal`. This was in the Q1-17b session, saved as `sp/q1-halves870-in-pack.sav`.
- **Setup.** A teleport to Map 10 (20480,17760,0), south of the circle, then `setGlobal 1033 1 1`. A standing stone blocked the walk N, so I went around it W and then N to (20300,17108,0).
- **Log.** `Item: 547 (shape 73) calling usecode event 7 @ 05A5:0080` (EggShades).
- **Result.** No elder appeared, there was no speech, and he stayed free to move. After 13 s `findShape 870` still showed 2 in the pack, and the weight was still 90 (`Q1-ceremony-latch-shieldFixed1-after13s`).
- **Control.** `setGlobal 1033 1 0`, then a teleport to the court and back so the egg left the fast area (its latch reset), then the same walk N. The same `event 7 @ 05A5` logged, the elders were teleported in, and Ezrekal's "At fault who is, I care not!…" played (`Q1-ceremony-control-shieldFixed0`). So the `if shieldFixed = true return;` latch is the only difference.

### Q1-10a and Q1-10b: the root and the Passage stone. PASS

**With the flags at 1** (the `s15` save):
- Walked W from the court (12600,2300) into trigger 204 → Map 11 (8259,22639,0).
- Walked SE into Map 11's trigger 205 → Map 10 (13132,2892,0), on pad 205.
- **The root:** `findShape 869: 0 found`.
- **The stone:** `findShape 798` found 1, `23410 … (0,0) f: 0x8`, which is a contained copy (finding 3). There was no ground copy.
- **The Test Plant:** `findShape 871: 0 found`.

**Control, with the flags at 0** (`q1-halves870-in-pack.sav`, with `setGlobal 1063 1 0` and `setGlobal 1041 1 0`):
- The same on-foot route: court → 204 → Map 11 → 205 → Map 10 (13128,2888,0).
- **The root** came back: `18957 (21376,16640,0)`.
- **The stone** came back: `2641 (13888,18368,8)`, plus the contained copy.

**The Test cannot replay** (the `s15` session, haveMark = 1):
- `Item::grab 23410` (the contained stone) took the weight 60 → 70.
- A teleport to (12800,29720,64), then a walk N to (12800,29424,64).
- **Log.** `Item: 17392 (shape 73) calling usecode event 7 @ 059A:0080` (EggPlantTest).
- **Result.** No teleport, the stone was kept (weight 70), and the position did not change (`Q1-test-no-replay-haveMark1`).
- **Control.** `setGlobal 1041 1 0`, then out of the fast area and back, then the same walk. The same event fired, he was teleported to **(13055,30079,64)**, and the stone was consumed (weight 70 → 60) (`Q1-test-control-haveMark0-runs`).

### Q1-11: talismans. PASS
- **Route.** In the `s15` session (all four pillar flags set), I walked into trigger 204 → Map 11 pad 204, and EggReapply hatched.
- **Result.** `findShape 596: 0 found` and `findShape 865: 0 found`. The sealing boulders were gone too (no shape 66 with q 299 in the list) (`Q1-M11-arrival-no-talismans`).
- **Static control.** `MapArchive` on the game copy's FIXED lists Map 11's talismans 596 f0-f3 (q101-104) and pillars 865 f0-f3. So their absence is the guard at work, not missing records.

## L: log hygiene

`lv_run.log` covers the whole session: 9 loads and about 20 map loads.

| Pattern | Count |
|---|---|
| `stuck in process loop`, Segmentation, Assertion, `Non-existent process`, `Trying to access segment`, `popToContainer`, ERROR, `Unhandled intrinsic`, `Skipping invalid shape`, `failed to set stats` | 0 each |
| `WARNING: Invalid procid 5015 in waitlist for proc 6943` | 3: one per load of the s02d save, so it comes from the save |
| `WARNING: Invalid item 10658/11402 passed to area search` | 5: Map 8, right after shape 804 `event 5 @ 0324:00DD`, the retail spitter missiles |
| Stock WARNINGs | 4: translations.dat, gui-icons, theme, timestamps |
| `Cycle in paint 590 -> 235` | 3,629: the retail Map 8 bone-chamber pair |
| `Cycle in paint 126 -> 871 / 126 -> 1 / 126 -> 126` | 139 / 7 / 2, all at the Passage Test grounds (finding 4) |

No usecode or engine error came from EggValeReturn, EggReapply, the SHADES/PLNTST latches or the regrow.

## Findings outside the brief

1. **A save taken on Map 8 on an older build keeps the ungated TeleportEgg 212 until the player leaves Map 8** (control A0). The repro save still sent the run to Map 10. This affects dev checkpoints. For a player it would affect only someone whose last save is on Map 8 from a pre-`f99b9a9` build. Any test of this gate must hop first.
2. **EggReapply depends on pad arrival.**
   - A debug teleport onto Map 10 elsewhere reloads the fixed items without the guard: the root and the stone came back in the control session on the court teleport, before the walk through the pads.
   - That is harmless for play. Every cross-map usecode teleport I found lands on a pad: EggValeReturn → pad 212, and the reapply egg hatched there (line 7357). Every other usecode `teleport`/`safeTeleport` with `MapLostVale` in `lv-patched/` and `lv-new/` targets Map 10 from Map 10 itself, or an NPC.
   - Testers should know it, though: a teleport-in is not a guard test.
3. **A second Passage stone sits inside a container on Map 10** (shape 798, `f: 0x8`, item 23410 after the reload, ids vary). It is not on the ground, and EggReapply's sweep is non-recursive by design, so it survives haveMark. [INFERENCE] It is the copy that `build_map_10.py` says the bag (637) at Ragnar's cache holds. After the Test it is clutter, because the PLNTST latch refuses it (Q1-10b). Low.
4. **New paint cycles at the Passage Test grounds:** `126 -> 871` ×139, `126 -> 1` ×7 and `126 -> 126` ×2.
   - **When.** They were logged only after the control Test ran.
   - **Cause** [INFERENCE]. The scene's created replacement plants (871, custom art since contract 13) are sorting against the blue-crystal ground tiles (126).
   - **Untraced.** I did not trace positions or look for a visible glitch. Not from the changes under test.
5. **`run1010-s13d-m17-both-shield-halves.sav` carries the halves as shape 539** (`findShape 539`: 7901 q82 and 30508 q81 in the pack), and `findShape 870` read 0. These are pre-870-art halves, so the save cannot exercise EggReapply's carry check (TypeAOFrizbee = 870), and [INFERENCE] not SHADES's either. I did not check `s13e`. Use a fresh 870 pickup, as in Q1-17b, for ceremony tests.
6. **At the R1 spot the Avatar is drawn almost entirely behind the tall wall south of him.** Only his head shows (`R1-after-regrow`, `R1-regrow-glide-sheet`), so the regrow there is barely visible to a player. [INFERENCE] This is correct occlusion by the sanctum boundary (120 high). I did not check the sort.

## Harness anomalies

- **H1. The estate run timed out.** `tools/run_all_tests.sh` hit the tool's 300 s cap after 46/46 PASS: the machine was loaded by other sessions, and `test_route_reach` alone took 66 s. The six it had not reached (`test_uc_reentry` 140/140, `test_uc_shades` 58/58, `test_uc_sim` 38/38, `test_uc_tiny_regrow` 30/30, `test_uc_vale_return` 19/19 and `test_uses_imports` 41/41) were run by filter. In total, 52/52 PASS.
- **Engine state survives a load.** The cheats state and avatarInStasis both carry over, so a `Cheat::toggle` after a load sometimes turned cheats *off*. Read the echo every time.
- **Stasis was toggled by mistake.** My `con()` regex missed `avatarInStasis = …` (capital S) and resent the command, which toggled stasis twice. I restored it with a single raw toggle (log: `true`, `false`, `true`, then `false`).
- **A standing stone stopped the walk.** At the circle's south side a stone blocked N, and the first two walks there looked like dropped input. A screenshot showed the stone.

## Disk changes

- **Wrote** this report and `docs/playtest-2026-10-11-gates/`, which holds 17 plates (G1 ×5, Q1 ×9, R1 ×3; R1 includes the frame sheet).
- **Scratch** `/tmp/claude-1000/vgate2/`:
  - `game/` (the copy, hashes re-checked at the end), `bin/` (the scummvm copy and engine-data), `scummvm.ini` and `saves/` (slot 1 overwritten);
  - `lv_run.log`, `trace.txt`, `estate.log` and `py/vg.py`;
  - in `sp/`: working plates, the checkpoint copies, `q1-halves870-in-pack.sav`, and the films `R1-regrow.mkv` and `R1-regrow2.mkv`.
- **Stopped** my ScummVM (pid 1184237) and Xvfb `:93` (pid 1184217). Other agents' processes (:92, :94, :95) were left alone.
- **Not touched:** `~/lv-checkpoints` (read only, nothing banked), source, maps, the fork, `shared/`, `TODO.md` and `HANDOFF.md`. No build or install script was run.

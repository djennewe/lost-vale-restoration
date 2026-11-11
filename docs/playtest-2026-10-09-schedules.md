# Schedules retarget, EZREKAL V2 elixir, TYORVI V2 sober drink (2026-10-09)

**Build under test:** `main` at `73036a8`, plus the uncommitted lv-patched EZREKAL/TYORVI V2, the test_uc_dialogue check, the inventory doc, `build_scummvm.sh` detection, `ARTIFACTS.sha256` and `map_pins.json`.
- The log reads `usecode/eusecode.flx: cd847392987c3e1f6f7b4bc9e4169838, 1525384 bytes`.
- The game copy `/tmp/claude-1000/vse/game` (rsync of `shared/u8-lv-patched`, no `.bak`) has sha256 EUSECODE `29fb0c29ab39`, U8SHAPES `bb0e4cda1e46`, TYPEFLAG `794d4b80a918`, ANIM.DAT `77e9705da254`, and FIXED `13321f0782d1` in both places. These equal `shared/build`.
- Plates are in `docs/playtest-2026-10-09-schedules/`, at 640x400.

The session was cut short by the request budget. N1 is covered for one period of every NPC plus map-entry evidence; N4, N7 and the multi-period hourly run are **not demonstrated**.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| N1 | Each of the 8 NPCs is found at its scheduled point after the Avatar has been away, in at least two periods | **PARTIAL.** In firstebb, all 8 were at their exact firstebb points after a Map 3 → Map 10 hop. The second period was not reached (budget), and neither was a run of the hourly `SchedulerProcess` (finding 1) |
| N2 | No NPC is ever inside a wall, crate, lake or void, or on a roof | **PARTIAL, with one visual defect.** Every sighting read z 0, and each position checked with `exact_reach` is standable at z 0. But **Tyorvi's stash point sits in the strip the Gunnar south-east cliff paints over**: at (22511,7951) he was fully hidden, and nearer the point only his head shows (finding 2) |
| N3 | A schedule teleport never happens next to the Avatar | **PASS (one instance).** On the hop, the Avatar landed 160 units from Tyorvi's home. Tyorvi stayed there, at (7244,7490), while every far NPC was teleported to its firstebb point. His firstebb point is the Gunnar stash |
| N4 | Thordis leaves the Passage Test plateau and reaches her Hoskuld home | **NOT DEMONSTRATED** (budget). Related: in `run-s11-tyorvi-key.sav` she was still on the plateau at (12927,29823,**64**). The first Map 10 entry put her at (4415,7423,0) (finding 1) |
| N5 | Thordis, Ragnar and Ingjald start on open ground at their new starts; Tyorvi starts at his Hoskuld home | **PASS** for a fresh Map 10 load. The log reads `updating pos to` (4416,7424,0), (5440,10528,0), (20768,7456,0) and (7424,7520,0), and the plates show open ground. A true `newGame` was **not run** |
| N6 | The quest finds its NPCs; the elixir looks "1 vial of blood"; sober "Just try it, please." removes the vial; the Key follows | **PASS** |
| N7 | The EggShades send-homes put Atli, Thordis and Ezrekal at their schedule homes | **NOT DEMONSTRATED** (budget). Static: `SHADES.UNK:809/834/859` teleport to (12799,12543), (19231,6943) and (4415,7423) |
| L | Log hygiene | Part 1 (2,643 lines): 0 `Unhandled intrinsic`, 1 `Non-existent process`, 0 `stuck in process loop`, 0 Segmentation, 0 Assertion, 0 safeTeleport/`Npc::teleport` failures. The one `Non-existent process` came with the old-save crash (finding 3). Part 2 (184 lines): all 0 |
| C | `run_all_tests.sh`, `build_artifacts.sh`, `install_lv.sh`, `build_scummvm.sh`, fork patch | **SKIPPED** on instruction (already run, with a sibling verifier in parallel). The sha256 check above stands in |

## Method

- **Isolation.**
  - Display `:84` (Xvfb 1280x800), with the window at (480,300).
  - Scratch `/tmp/claude-1000/vse/`, with the config `vse/scummvm.ini` (`usehighres=true`) and saves in `vse/saves/`.
  - Command: `scummvm-lv/scummvm --config=… --savepath=… --extrapath=scummvm-lv/dists/engine-data --debuglevel=1 --path=vse/game --save-slot=1 ultima8`.
  - The driver is a copy of the `vsa` `drv.py`/`h.py`, re-pointed to `:84`.
  - I started and stopped only my own pids. The sibling's `:85` was not touched.
- **Saves.**
  - `run-s11-tyorvi-key.sav` (md5 `96e20997…`, hour 27 bloodwatch) was loaded at launch and used for N3, N5, N1 firstebb and N6.
  - `bag-q1-map10-2026-10-03.sav` crashed the engine on load (finding 3).
  - `cp34-altar-ready-head-20260926.sav` was loaded and nothing further was done with it.
- **Game time** was read from the save `INFO` block (`/tmp/claude-1000/vse/savinfo.py`), after an `Ultima8Engine::saveGame 1`. The clock was **never set**: there were no clock cheats, and the bedroll was not used.
- **Game-state writes:**
  - Teleports with cheats on, each followed by a toggle back to `Cheats = false`.
  - `MainActor::toggleCombat` once, plus `CameraProcess::moveToAvatar`, which was needed on the 09-07 save.
  - `debugflag_enable Object`.
  - `Item::grab 11290`, for the root.
  - `Actor::talk 116` once, because the herb-garden bushes won every click on Ezrekal. The second talk and both Tyorvi talks were screen double-clicks.
  - `saveGame 1` three times.
  - Every menu answer was clicked on screen.

## N1 / N3 / N5: the map-entry run (run-s11 world, firstebb)

**Before the hop**, the positions were the save's, from the old build: Thordis (12927,29823,64) on the plateau, Ragnar (5120,8704) at the old Hut 3 start, and Tyorvi (19447,9311) in Gunnar.

Over 3.5 real minutes the world crossed hour 27→28, which is bloodwatch→firstebb. **No NPC moved**, and no `event 8` was logged: this save has no `SchedulerProcess` (finding 1).

**The hop.** I went Map 3 → Map 10, landing at (7583,7583). The log shows the snap of every LV actor to its FIXED start (`LV: Slot 106 … updating pos to (4416,7424,0)`, Ragnar (5440,10528,0), Ingjald (20768,7456,0), Tyorvi (7424,7520,0)). It then shows `event 8` for every actor (`CurrentMap::loadMap` → `actor->schedule()`). The game time read 25514 s, which is hour 28 firstebb.

| NPC | firstebb point | read after the hop | z | plate |
|---|---|---|---|---|
| Sigrid 102 | (5503,16383) | (5503,16383) | 0 | `N1-F-sigrid-hunt-firstebb` |
| Ragnar 105 | (7039,17151) | (7039,17151) | 0 | `N1-F-ragnar-field-firstebb` |
| Thordis 106 | (4415,7423) | (4415,7423) | 0 | `N1-F-thordis-home-firstebb` |
| Atli 107 | (19231,6943) | (19231,6943) | 0 | `N1-F-atli-hutdoor-firstebb` |
| Ingjald 112 | (20767,7455) | (20767,7455) | 0 | `N1-F-ingjald-home-firstebb` |
| Hrodny 113 | (21759,8447) | (21759,8447) | 0 | `N1-F-hrodny-home-firstebb` |
| Ezrekal 116 | (12895,13439) | (12895,13439) | 0 | `N1-F-ezrekal-garden-firstebb` |
| Tyorvi 115 | (22335,7647) | **(7244,7490)**, Avatar 160 away: **N3** | 0 | `hop1` (scratch) |

On a later hop with the Avatar far from him, Tyorvi was read at exactly (22335,7647).

Each plate shows the NPC on open ground, loitering near the point.

**N5 plates.** Hops that landed within 700 units of each start show the NPC on open ground: `N5-ragnar-start-after-map-entry` (beside the hut's south-east corner, outside it), `N5-ingjald-start-…` and `N5-thordis-start-…`. Tyorvi at his home start is in `hop1` (the first hop). Not shown: the `Created actor` path of a true `newGame`.

## N6: PASS (run-s11 world, firstebb)

**Finding Ezrekal.** She was at her firstebb garden point (12895,13439) (`N6-01`).

**The root.** I put root 11290 in the pack with `Item::grab`. The talk menu was **I have found the root. / Can you help me? / bye** (`N6-02`). Picking the root gave "Ah, good that is. Take it I will and brew the tea I will." (`N6-03`). The next menu was **Can you help me? / Is Tyorvi's elixir ready yet? / bye** (`N6-04`), and givenRoot = justGotRoot = 1.

**Walking away.** I walked to (17571,16587). The log shows `Item: 116 … event 16 @ 0474:0264`, and justGotRoot then read 0.

**The hand-over.** On return the menu was **Can you help me? / Have you made the elixir? / bye** (`N6-06`). The pick gave "Yes, I have. Take it to him now you can." then "Hope it helps him, I do." (`N6-07`, `N6-08`), and givenElixir (0x723) = 1. The vial:

```
Item 10977 (class Item, shape 395) (uc: ERTHREAG), 5, (0, 0) q: 1 … f: 0xc
```

**The look.** A click on the vial in the pack logged `event 0 @ 018B:0080`, and the bark is **"1 vial of blood"** (`N6-09-vial-look`).

**Finding Tyorvi.** He was at his firstebb stash point (22335,7647). Talking to him logged `event 1 @ 0473:0354` (`N6-11`). The sober route:
1. **I have something for you from Ezrekal.** → "Want nothing from that old bag…"
2. **It is an elixar.** → "Take nothing from that bag I will!"
3. **It will heal your dreams.** → "Heal my dreams, you say? … Only if more of Ingyald's brew I drink."
4. **Just try it, please.** (`N6-17`) → "Oh, all right. Give it to me." → "Hmmm, taste too bad that did not. Hmmm. Actually feel a little better I do." (`N6-19`)
5. **May I have the Key to the Clouds?** (`N6-20`) → "Well, treacherous it is, but brave you are … Here, here the Key to the Clouds is." → "Now, rest I must…"

**Afterwards.**
- `findShape 395: 0 found`.
- givenTea (bit 1061) = 1.
- Pack weight went 30 → 40.
- The pack shows a second key and no red vial (`N6-22`).
- Not shown: the drunk route, which was retested yesterday.

## Findings

1. **Every save from the 09-06/07 run (`run-s3` … `run-s18`) has no `SchedulerProcess`, and nothing recreates it.** That includes the saves this brief names (`run-s11`, `run-s13`) and every save derived from them (`w2a/slot1-post-test`, `vsa-after-ceremony`, `vet/post-elixir`).
   - **Evidence.**
     - I parsed the KERNEL block of all 110 checkpoints: every `run-s3…s18` save reads `sched=False`.
     - Every other checkpoint reads True: the 07-30…09-05 saves, `cp34` (09-26), the 10-03/04 `bag-q1` saves, and `run1008-s00`.
     - `run-s3-doors-open` also lacks the `U8AvatarMoverProcess`. So the 09-06 runaway guard (`ultima8.cpp:1740` comment) failed both item-0 processes. The loadGame fix recreates only the mover.
     - In engine, `Kernel::listProcesses` shows no scheduler, and hour 27→28 passed with no `event 8`.
   - **Consequence.** In those worlds the only thing that runs `schedule()` is a map entry: `CurrentMap::loadMap` calls `actor->schedule()` for all 256 actors when `callCacheIn` is set.
     - Thordis's post-test exit therefore depends on a map switch, not on "the next scheduler run" (as the inventory doc says).
     - The same goes for a player whose game hit the runaway guard.
   - **Suggested fix.** In the same loadGame block, recreate a missing `SchedulerProcess`. Confidence: high.
2. **Tyorvi's stash point (22335,7647) is in the strip the Gunnar south-east cliff paints over** (N2).
   - **Evidence.**
     - In `N6-10-tyorvi-at-stash`, Tyorvi at (22511,7951) and the Avatar at (22475,7787) are both invisible. Both points are standable at z 0 by `exact_reach` (`vse/geo/stand.py`).
     - In `N2-tyorvi-stash-occlusion-0`, Tyorvi at (22211,7771) shows only his head above the rock rim. The stash point itself (marked yellow in scratch `occ0.png`) projects onto the rock face.
     - In `N2-…-2`, at (22265,7891), he is cut off at the knees.
   - **Effect.** To a player he looks to be inside the cliff, and he cannot be clicked until his loiter brings him north-west.
   - **Gap in the test.** `test_schedule_destinations.py` checks standability, not occlusion. Confidence: high.
3. **`bag-q1-map10-2026-10-03.sav` crashes this build on load.**
   - **The log:** `Non-existent process PID (2563, 0) in implies`, then `Process 632 caused an error at 05AA:04EA (item 0)` (EGGENDGAME, saved at a pre-`fc7e0bf` offset), then `Trying to access segment FFFF`, then the process exits.
   - **Reading.** This is old-save process drift, not this change, but that checkpoint is unusable now.
4. **Every Map 10 entry snaps all LV actors (100-116) back to their FIXED starts** (fork `map.cpp:269-276`), and the entry's `schedule()` call then moves the far ones.
   - So a schedule-placed or quest-placed NPC is reset by any map hop. The starts were moved onto the homes, which mostly masks this.
   - Sigrid's start is (7680,6400), which is neither of her points.
5. **`SHADES.UNK` `sendThordisHome` animates *Atli*** in its north-walk loop (1994 text). Seen statically only.
6. **Ezrekal's herb garden defeats clicks.** The bushes (434) and floor tiles take every click while she stands in them, so a player standing south of her cannot talk. One `Actor::talk` was needed. Confidence: medium (driver aim).

## Not done (budget)

- N1 second and third periods.
- The hourly `SchedulerProcess` run (the plan was `cp34` → Map 10, then the guest bedroll at (12672,12800) for +4 h steps).
- N4 (`cp10-test-done.sav` has a scheduler and plantScene 1).
- N7 (`run-s13`).
- A `newGame` for N5's `Created actor` path.

## Disk changes

- **Wrote** this report and 37 plates in `docs/playtest-2026-10-09-schedules/`.
- **Scratch in `/tmp/claude-1000/vse/`:**
  - `game/`, `scummvm.ini` and `saves/` (`ultima8.001` = the cp34 copy);
  - `lv_run.part1.log` and `lv_run.log`;
  - `py/`, `sp/` (frames, plus three saves `t0/t1/t2`);
  - `dis/`, `geo/stand.py`, `savinfo.py` and `schedscan.py`.
- **Not touched:** `shared/`, `~/lv-checkpoints` (read only), and every source, builder, map, fork, TODO or HANDOFF file.
- **Stopped:** my ScummVM and Xvfb `:84`.

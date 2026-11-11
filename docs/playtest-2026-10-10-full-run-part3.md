# Full 1→18 run, cheats off, part 3: through the Map 8 north traps to the doors chamber, NOT COMPLETED (2026-10-10)

**Build under test.** main `4a40dc8`, fork `8af4f74e`; `scummvm-lv/scummvm` is dated 11:00.
- **Game copy.** `/tmp/claude-1000/vrun3/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. sha256 matches `shared/build/ARTIFACTS.sha256`: EUSECODE `709c6bd1…`, FIXED `22cada6f…` (root and `STATIC/`), U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…` and ANIM `77e9705d…`. The log line reads `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1525518 bytes`.
- **Harness.** Xvfb `:95` with the window at (480,300), `frameLimit=true`, `usehighres=false` and a private save dir.
  - Until 11:24 the ini also carried `width=640`/`height=400`, inherited from part 2, which gives a 640×400 game screen (finding 1).
  - From 11:25 those keys were removed, so the game screen is 320×200 with `scale_factor=2`.
  - The driver is the part-2 `drv.py`/`vr.py`, re-pointed to `vrun3`.
- **Start.** `~/lv-checkpoints/run1010-s02b-m8-north-pre-spitter.sav`: Map 8 (15356,7228,0), hp 30, step 2 done.

**Outcome.** The furthest step completed is still **step 2**. Step 3 got further than before:
- **Spitter 1 crossed** (Map 8 north region), 30 → 18 hp. I banked a checkpoint in the safe pocket between the two spitter zones.
- **Spitter 2 crossed twice:** once at 30 → 30 hp, and once at 30 → 25 hp on the way into the doors chamber.
- **Doors chamber reached:** I reached the double-doors chamber, beside the key chest.
- **Blocked in the chamber.** Two retail **"invisible" monsters (shape 808)** hatch there and beat an unarmed Avatar from 25 hp to 0 in about 10 s (finding 3).

Over two attempts, their knockback once walked him to his death, and once shoved him into the old T212 box and on to Map 10 (pad 212). That is a skip, so I discarded it and reloaded. I stopped at the request budget.

**Cheats used: none.** `Cheats` appears 0 times in `vrun3/lv_run.log`. The console was used only for `objectInfo`, `findShape`, `listProcesses`, `debugflag_enable Object`, `saveGame` and `loadGame`. Every move was a mouse run or walk, or keyboard Up.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| Start room → spitter 1 → gap between the zones | **PASS (walked)**, hp 30 → 18 (one hit, source not identified), then rested to 30 | Blind run legs (14436,7228) → (16623,7231) → NE → (17344,6456) → N up the x≈17450 lane → NE → (18340,4776). Then into the gap pocket (18172,5032) |
| Resting heals | **PASS** | `HealProcess` gives +1 hp per 1800 frames (1 min). hp 21 → 30 by 11:33 while standing in the gap (`trace.txt`) |
| Gap → spitter 2 corridor → doors region | **PASS**, 2 of 2 crossings | A single blind run, SE then E along y≈5173. The first ended at (21364,4704) on hp 30 (`s03-01`). The second, (17824,4684) → (20800,4900) → NW → N along x 20330, ended at (20552,3676,8) on hp 25 (`s03-02`) |
| **Step 3: key → doors → T201 → Map 9** | **NOT DEMONSTRATED.** Blocked by two shape-808 "invisible" monsters (finding 3). 2 deaths, plus 1 skip discarded | `s03-03` sheet: the Avatar reeling and bleeding with no visible attacker. `findShape 808`: items 146 (20630,3706,8) hp 17 and 147 (20564,3764,0) hp 24, both adjacent |
| Steps 4-18 | **NOT DEMONSTRATED** | — |
| Log hygiene | **PASS for LV code** | 0 each of: `Unhandled intrinsic`, `stuck in process loop`, Segmentation, Assertion. About 9,500 `Cycle in paint 590 -> 235 -> … -> 590` lines, all in the bone chamber with retail NONFIXED items (fire 590 and bones 235) |

## Findings

1. **The part-2 "low-res" runs were not low-res, and the spitter gauntlet is much easier at retail 320×200.**
   - **The keys.** The ini carried `width=640`/`height=400`. `Ultima8Engine` reads those keys and ignores `usehighres` for the screen size (`ultima8.cpp:506-519`). The log printed `Setting Video Mode 640x400`, so the GameMapGump was 640×400. Part 2's finding-3 mitigation never took effect.
   - **Fast area.** `updateFastArea` sizes the fast area from those dims plus a half-chunk border, chunk by chunk (`current_map.cpp:418-506`).
     - At 640×400 both spitters were in the fast area at once from the gap (18172,5032). `findShape 795` showed f `0x2000` on both.
     - At 320×200 neither was (`0x0`), and the model I reimplemented agreed (plate `s03-00`).
   - **For future harnesses.** Leave out width/height, or check for `Setting Video Mode 320x200` in the log.
2. **The spitter can be beaten by timing, not by dodging.**
   - **The timer.** SPITTER (class 031B) starts its fire loop on `enterFastArea`. The first FIREBOMB comes only after `200+urandom(200)` ticks of the 60 Hz timer (`0581:1C19`/`1BF1` read `getCurrentTimerTick`), so at least 3.33 s after the zone is entered. `leaveFastArea` kills the loop.
   - **The rule.** Cross each zone in one held run of under about 3.3 s, with no console reads inside a zone. Each read costs game time.
   - **Run speed.** It is about 590 world units per second along each axis. Diagonals cover both axes at that rate.
   - **The safe pocket.** A diagonal band outside both spitters' zones lies at about (17650,4700)–(18300,5250). Inside it, use x 18050-18275 at y 5100 to stay out of the MISSTRAP lanes. A second wall-free pocket is the chamber interior north of y≈3750.
   - **Bomb behaviour.** Bombs fly along the 8-direction (exact axis in cardinal sectors, a randomised wedge on diagonals), go 1300-5000 units, and explode on impact with an area search of radius 192 (frame-0 bomb: 6×32). Being near the spitter is safe; being near a wall behind you, as seen from the spitter, is not.
3. **The step-3 blocker: two "invisible" monsters (shape 808) at the doors.**
   - **The spawn.** The NONFIXED MONFAST egg (shape 73, q 60, class 04BB) at (20494,4570) hatches the FIXED monster eggs (shape 500) at (20562,4670) and (20500,4724). Both have quality 0x2328/0x3B28, so the monster is shape 808 and they hatch with the Map 9 tag.
   - **When it fires.** It hatches whenever its chunk enters the fast area, and that covers the whole doors area: the chamber, the corridor exit from x≈20000 at y 5200, and the region to the east.
   - **The monster.** `u8monsters.ini [invisible]`: hp 15-25, damage 4-6, armour 5. They have no visible sprite: the plates show blood spray and stagger animations only (`s03-03`). Their hits knock the Avatar around. In 2 of 2 tries he was pushed out of the chamber or onto damage while the console was busy.
   - **Impact.** An unarmed 30-hp prologue Avatar cannot survive the chest → key → two leaves → door sequence. This is the "wandering ghost" in `agents/map-populator/docs/map-08-plateau-entry.md:69-75`, misidentified there: what kills is shape 808, not 411 (`findShape 411` returned 0).
   - **Classification.** All of this is retail content, not an LV code defect. It is a balance/route blocker for step 3 that the author should know about.
4. **There is a weapon on Map 8: the Bone Crusher (shape 815, base damage 11).** It is in the chest (shape 78) at **(23824,7128,0)**, together with an armguard 530 f4, 750 f3/f4, 756 and 815. That is the bottom corridor east of the doors region, past SP3 (shape 795 at (22090,6934)).
   - **Exposure.** The chest's east side (≈23900,7150-7200) is outside SP3's zone, but the walk there is about 6 s inside it.
   - **Other loot.** Healing potions (766 f1/f3) are in the plateau chest at (16351,17183,48), reached by T27 back to the plateau.
   - **Status.** Untried.
5. **Third spitter.** Shape 795 at (22090,6934) is item 8498. Its zone abuts spitter 2's, so there is no zone-free path east of the corridor exit at y > 4200 (grid in `trace.txt`/kernel notes). Saving or reading while standing in it (21364,4704) cost 25 hp.
6. **Old T212 still sits in the checkpoint's fixed items**, as the 10-10 traps entry predicts. Knockback in the chamber pushed the Avatar into it at y < 3428, x > 20484, and the trigger fired: **Map 10 pad (13824,2560,0)**. This confirms that T212 skips Maps 9 and 11 on arrival from this side. I discarded that run.

## Harness anomalies

- **Mouse aim off-window.** In 320×200 mode the walker's mouse offsets must stay inside the window. At a 240 px offset a world-SE run aimed below the window and did nothing. The fix was a clipped aim around the engine's reference point (160,114) in game pixels, ×2 for the window.
- **The first mouse press is often swallowed** after a `loadGame` or `saveGame`, and walk-gait presses in 320 mode often did nothing. A short run press works.
- **The console looks different in 320 mode.** It covers only the top 260 px, so part 2's detector (row 268) misreads it. The scrollbar pixels at (614,6)/(614,12), both `(32,161,32)`, are reliable.
- **Save without clicking.** `Ultima8Engine::saveGame <name>` saves straight to slot 1 with no dialog (`debugger.cpp:174-186`). Use it instead of clicking through the ScummVM dialog.
- **The death book cannot be closed with Escape** while the Avatar is dead (`menu_gump.cpp:191-195`). `loadGame 1` from the console still works.

## Checkpoints

- **`~/lv-checkpoints/run1010-s02c-m8-corridor-gap-hp30.sav`** (new; md5 `4d1b5cd9…`). Map 8 (18172,5032,0), hp 30, in the pocket between the spitter 1 and spitter 2 zones, step 2 done. Reloaded 2 times and good. **This is the resume point.**
- **`~/lv-checkpoints/run1010-s02d-m8-doors-chamber-ghosts.sav`** (new; md5 `50231cd4…`). Map 8 (20552,3676,8), hp 25, beside the chest. It is saved with both shape-808 monsters adjacent, so it dies on load unless you act at once. Kept as evidence only.
- **Scratch** in `/tmp/claude-1000/vrun3/sp/`: `w-gap-hp21`, `w-gap-hp30`, `w-past-sp2-hp30` (21364,4704; inside SP3's zone) and `w-chamber-hp25`.

## Resume here

1. **Setup.** Use a 320×200 ini (no width/height keys). Load `run1010-s02c-m8-corridor-gap-hp30.sav` and send `debugflag_enable Object`. Make one short run press first, because the first press is swallowed.
2. **Option A: arm first** (untried). Cross spitter 2 in one held run: SE to y≈5173, then E to x≈20300 (the riser). Then go S/SE through the region and E along the bottom corridor (y≈7250) to the Bone Crusher chest at (23824,7128). Stand at x≈23900 (outside SP3). Equip it, then return to the chamber and kill the two shape-808 monsters (hp 15-25, armour 5) before the door sequence.
3. **Option B: the speed line.** Arrive at the chest at full hp with the door sequence rehearsed: double-click the key in the chest gump, target both leaves, double-click the door, walk N onto T201 (20415,2786). Expect about 3 hp/s of damage once the monsters close in. Stay west of x 20484 while y < 3500 (old T212).
4. After Map 9, follow `/tmp/claude-1000/run1009/route-guide.md` from "Map 9 (Galjeron's Chamber)".

## Disk changes

- **Wrote** this report and its plates in `docs/playtest-2026-10-10-full-run-part3/`: `s03-00` (the spitter fast-area model at 320×200), `s03-01`, `s03-02` and `s03-03`.
- **Wrote** the two new checkpoints above (nothing overwritten).
- **Scratch** in `/tmp/claude-1000/vrun3/`: `game/`, `saves/`, `sp/`, `py/`, `u8dat/` (extracted `ultima8.dat` ini files), `lv_run.log`, `trace.txt`, `scummvm.ini`, `run.sh` and `xv.sh`.
- **Stopped:** my ScummVM and Xvfb `:95`.
- **Not touched:** source, builders, maps, the fork, `TODO.md`, `HANDOFF.md` and `shared/`.

## Session 2 (plan A: get the Bone Crusher first), NOT COMPLETED

**Harness.** Same game copy and Xvfb `:95`. The ini has no width/height keys, so the game screen is 320×200 (log: `Setting Video Mode 320x200`). Start: `run1010-s02c-m8-corridor-gap-hp30.sav`. Cheats: 0 `Cheats` lines.

**Outcome.** I did not get the Bone Crusher. One attempt, one death, and then I stopped at the request budget.

| Leg | Verdict | Evidence |
|---|---|---|
| Gap → spitter-2 corridor → south through the doors region to the SP3-free pocket (20750,7050) | **FAIL (death)** | A harness slip (a zero-length segment raised mid-run with the button held) left the Avatar at (19140,5360), inside spitter 2's zone after the timer had already run. The retry ran east, then the planned south turn at (20151-20175, 5175-5479) refused: the Avatar stopped at (20040,5244), then (20248,5244). hp 30 → 14 → 0 inside spitter 2's and spitter 3's zones, with the MONFAST egg active |
| Bone Crusher, potions, the shape-808 fight, step 3 | **NOT DEMONSTRATED** | Budget |

**Findings.**

1. **The planned south exit from the corridor end is closed in the engine.** The router's route (8-unit lattice, erosion 1) goes (20151,5175) → (20175,5479) → (20551,5887) → (20551,6863). In the engine the Avatar could not go south from x 20040-20250 at y≈5244: a walk at that line stopped twice. This is the aperture hazard in `.claude/rules/map-geometry.md`. Use `exact_reach.py` with erosion ≥ 2, plus the NONFIXED solids, to find a real lane south (around the riser, or further east via (20800,4900) → SW → (20583,5351)) before the next attempt.
2. **Console detection in 320×200 mode.** A fresh console has no scrollbar yet. The reliable test is the border: pixel (13,100) = (106,105,106) and (300,268) = (65,64,65).
3. **Run presses under about 0.4 s do nothing.** Startup takes about 0.37 s, so a "prime" press must be at least 0.6 s.

**Resume.** Unchanged: `~/lv-checkpoints/run1010-s02c-m8-corridor-gap-hp30.sav`. First find a verified lane south from the corridor end to the pocket outside SP3's zone at x≈20550-20750, y≈6860-7050. Then cross spitter 3's zone east along y≈7287 to the Bone Crusher chest; stand at x≈23900, which is outside SP3's zone.

**Disk changes.** Only this section. No new checkpoints. My ScummVM and Xvfb `:95` are stopped again.

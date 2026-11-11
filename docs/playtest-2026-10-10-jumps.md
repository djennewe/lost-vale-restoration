# Jump fixes: the overhang height give-back, raised floors, ledges, walls (2026-10-10)

**Build under test.** `main` `13e2731`, plus the uncommitted `build_scummvm.sh` detection change.
- **Game copy.** `/tmp/claude-1000/vjump/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Every hash matches `shared/build/ARTIFACTS.sha256`: EUSECODE `ebf03413…` (1,523,533 B), U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`, and FIXED `511902e8…` in both places.
- **Log line.** `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1523533 bytes`.
- **Binary.** `scummvm-lv/scummvm` is dated 2026-10-10 01:08:09. Fork `11bb31bd` is dated 01:01:11, and `animation_tracker.o` 01:01:14. The build tree's `animation_tracker.cpp` has all five `_zLost` sites.
- **Patch check.** `git diff 01bd8879 HEAD -- engines/ ':!engines/ultima/detection_tables.h' | diff -q - tools/scummvm-patches/0001-lost-vale-engine.patch` printed `PATCH_EQUAL`.
- **Harness.**
  - Xvfb `:93` (1280x800), with the window at (480,300).
  - My own `scummvm.ini` sets `frameLimit=true` and `usehighres=true`, with `SDL_AUDIODRIVER=dummy`.
  - The driver is the `veng` `drv.py`/`h.py`, re-pointed to this display and directory.
  - Jumps were filmed with `ffmpeg -f x11grab` at 15-20 fps.
- **Plates.** They are in `docs/playtest-2026-10-10-jumps/`.
- **Not run, on instruction:** `build_artifacts.sh`, `install_lv.sh` and `build_scummvm.sh`. The hash match above stands in for them.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| J1 | The keyboard jump (Up then SPACE) from Map 8 (29500,23622,0) now ends at z 0, over several tries and facings, and the Avatar stays mobile | **PASS**. It ended at z 0 in 11 of 11 jumps (W ×4, N, S, E, SW, and W from x 29492/29532/29540), plus 2 more Up-first jumps in J4c. It ended at the real z-8 floor top in 1 (NW). The 10-09 build gave z −4 from the same spot. The Avatar walked afterwards |
| J2 | On a raised floor under a low overhang, a jump lands at the floor z and never inside it | **PASS**. Map 39 arch at **(17023,19487,48)**, lintel bottom at z 96 (8 units of headroom): 2 jumpUps and 5 keyboard jumps all ended at z 48, and the Avatar walked afterwards. Map 39 tunnel lintel at **(16194,19600,48)** (0 headroom): 3 jumps and 2 jumpUps ended at z 48. Map 8 **(29823,23551,8)** (0 headroom): one jump ended at z 8 |
| J3 | An ordinary jump onto a 16-40-unit ledge still climbs | **PASS**. A 16-unit rock on Map 10 at (14719,1919) took 2 of 2 jumps to z 16. A 40-unit stump on Map 10 at (11007,3327) took 2 of 2 to z 40 |
| J4a | Map 39 tunnel side walls, y 19650..19950, both walls and both facings: jumps stop, with no pass-through and no wedge | **PASS**. In 21 jumps, 0 passed through and 0 wedged. Flush jumps ended at x 16223 (E) and 16159/16160 (W), all at z 48. Every mobility burst moved the Avatar |
| J4b | Pool-stone hops G→H→I (plus I→J) land on aim | **PASS** on the 10-09 aims: (30793,21734,8), (30797,22130,8) and (30575,22352,8). **But aiming at a stone's visual centre drowned the Avatar twice** (finding 1) |
| J4c | The cave ascent still climbs | **PASS**. SPACE then Up: 5 of 5 in the x 29508..29524 window reached z 56, and both controls (29500, 29532) stayed at z 0. Up-first did not climb in the window (finding 3) |
| J5 | The open-ground jump length is unchanged (lane C1 control) | **PASS**. From (16334,19450,48) facing W the jumps went 512, 504 and 512 units, against 10-09's 512 |
| L | Log hygiene | **PASS**. `vjump/lv_run.log` has 6,586 lines and 0 each of: `stuck in process loop`, `Unhandled intrinsic`, Segmentation, Assertion, `Trying to access segment`, `Cycle in paint`, `popToContainer`, `PID (0) in implies` and `stale gravity` |
| — | Patch equals fork diff | **PASS** (`PATCH_EQUAL`) |
| — | `tools/run_all_tests.sh` | **PASS**: 44 of 44 files discovered, and no non-PASS line printed (194.7 s) |

**State writes.**
- Teleports with cheats on, each followed by a verified `Cheats = false`.
- `debugflag_enable Object` after each load.
- `Ultima8Engine::loadGame 1` three times, each over a fresh copy of `run1009-s00-map8-pool-stone-g.sav`. Two of those recovered from the drownings.
- No `setGlobal`, no item creation and no save.

**Input.** Keyboard jumps were `keydown Up`, `keydown space` 60 ms later, a hold (0.35 s, or 1.6 s at the cave), then both keys released. Facing came first, from a 0.3 s right-button burst. A jumpUp was SPACE alone with the cursor on the Avatar. A pool hop was a probe click on the stone (which logs the item), then SPACE taps with the cursor on the same pixel.

## J1: the z −4 case, PASS

**Setup.** `MainActor::teleport 8 x 23622 0`, a facing burst, then Up and, 60 ms later, SPACE, held 1.6 s. Every start read z 0.

| Start | Facing | End | 10-09 build |
|---|---|---|---|
| (29500,23622,0) | W, try 1 | (28964,23622,**0**) | (28964,23622,**−4**) ×2 |
| same | W, tries 2-4 | (29060,…,**0**), (28964,…,**0**), (29068,…,**0**) | — |
| same | N | (29631,23675,**0**) | — |
| same | S | (29500,24174,**0**) | — |
| same | E | (30028,23622,**0**) | — |
| same | SW | (29172,23950,**0**) | — |
| same | NW | (29368,23490,**8**). This is a real floor: shape 564 frame 2 with its top at z 8, (29439,23551) 256×256×0 | — |
| (29492 / 29532 / 29540, 23622, 0) | W | (28956 / 28996 / 29004, 23622, **0**) | — |

**Mechanism.** An offline replica of `AnimationTracker::step` over the built Map 8 runs the Avatar's `jump` (ANIM.DAT action 17), heading west from (29500,23622,0).
- **Without the fix:** frames 6 and 7 (+2, +2) are refused by the z-56 shelf (shape 564), the full −20 descent still plays, and the jump ends at **z −4**. That is the 10-09 reading.
- **With the fix:** the same run ends at **z 0**.
- So this spot exercises the new `_zLost` path: the rise is cut by 4 units and the descent gives the 4 back.

**Mobility.** From (29068,23622,0), 1.0 s bursts moved E +104, then S +232, at z 0.

The Avatar is hidden under the shelf at this spot, so the position reads are the evidence. Those positions have no useful plate.

## J2: raised floor under a low overhang, PASS

**Finding the spots.** I scanned FIXED (globs expanded) for standable positions on a floor top z > 0 that have a SOLID item with zd > 0 and its bottom 40-60 units above the floor. A ceiling in that band cuts the rise of the `jump` (peak +20) and of the `jumpUp` (peak +24), so the new code path is exercised.
- **Counts:** 2,505 on Map 8, 1,957 on Map 39, 569 on Map 10, and 0 on Maps 11, 17, 18, 9 and 13.
- **Many are not player-accessible.** For example, Map 8's z-8 and z-56 floor-301 layers lie under 8-unit cave-floor slabs.
- **I chose the two Map 39 gateways the player walks through.**

**J2-2: the castle-wall arch at (17023,19487,48). The Avatar is visible.**
- **Geometry:**
  - The floor is shape 71 at z 48.
  - The lintel is shape 15 frame 1 at (17023,19455,96), 128×32×40. Its bottom is 48 units above the floor, so 8 units over the Avatar's head.
  - The replica rates the Avatar's box valid at z 48-56 and blocked at z 60.

| Jump | End |
|---|---|
| jumpUp ×2 (SPACE, cursor on the Avatar) | (17023,19487,**48**) both times. The sheet shows the crouch and the arms-up rise, then standing on the cobbles (`J2-2-arch-jumpUp-sheet`) |
| E (along the passage, under the lintel) ×2 | (17367,19487,**48**) both times (`J2-2-arch-E-sheet`, `J2-2-arch-E2-landed`) |
| W | (16991,19487,**48**). The arch's west side stopped it |
| S (out from under the lintel onto the grass, shape 3 at z 48) | (17023,19975,**48**) |
| N (into the wall) | (17023,19487,**48**), no movement |

- **Mobility after E2.** 1.2 s bursts moved W −200, then N −104, all at z 48.

**J2-1: the tunnel's south lintel at (16194,19600,48). Zero headroom.**
- **Geometry.** Shape 670 is at (16255,19615,88), 128×32×8, so its bottom is exactly on top of the Avatar's head. Every rising frame is refused, which makes this the largest give-back (20 units).
- **Results:**
  - S, twice: **(16194,19935,48)**. This matches 10-09's lengthwise (16194,19600) → (16194,19935).
  - N: **(16194,19088,48)**.
  - jumpUp ×2: (16194,19600,**48**).
- **Visibility.** The tunnel hides the Avatar, so these rest on position reads.

**J2-0: Map 8 (29823,23551,8).**
- **Geometry.** A floor-301 tile is at z 8, and the 125 slab sits at z 48 (zero headroom).
- **Results.** E ended at (30207,23551,**8**). W ended at (29595,23779,0) after the 1.6 s Up hold walked him off the z-8 layer's west edge, which is a walk-off, not a sink.
- **Weight.** This spot is inside the cave floor and not player-reachable, so it counts only as a mechanical check.

**Negative.** No jump in J2 ended below its floor or with a refused walk. 0 `stuck in process loop`.

## J3: low-ledge climb, PASS

**Finding the ledges.** The ledges came from a replica of `Actor::tryAnim` (climb16..climb72, the lowest success wins) run over the built FIXED. I accepted only starts on a real floor (not the z ≤ 0 void freebie) whose lowest successful climb is 16-40 units. Map 39 had 60+ and Map 10 had 60+.

| Ledge | Start, facing | Replica | Engine, Up then SPACE held 0.4 s |
|---|---|---|---|
| Rock shape 526 frame 7 at Map 10 (14719,1919,0), 64×64×16 | (14719,1983,0), N | climb16 → (14719,1919,16) | **(14719,1919,16)** ×2 (`J3-a-rock526-climb-sheet`, `J3-a-rock526-climbed-z16`) |
| Stump shape 56 frame 6 at Map 10 (11007,3327,0), 64×64×40 | (11007,3391,0), N | climb40 → (11007,3335,40) | **(11007,3335,40)** ×2 (`J3-b-block56-climbed`) |

**Negative.** The same input at the walls and lintels, which are taller than 72 or have no headroom, never climbed (J2, J4a).

## J4a: Map 39 tunnel walls, PASS

The flush positions were set by teleport, as in 10-09.

| Jumps (Up then SPACE) | Result |
|---|---|
| E flush x 16222, at y 19950/19870/19802/19710/19650, held 0.35 s | ended **x 16223**, z 48, every time |
| W flush x 16160, at the same y, held 0.35 s | ended **x 16160 / 16159**, z 48 |
| E/W flush at y 19950, 19802 and 19650, held 1.0 s | the same: 16223 / 16160 or 16159, z 48 |
| Clear of the wall: E from x 16190 (y 19710, 19950); W from x 16194 (y 19870) | **stopped at 16222 / 16222 / 16162**, z 48. The input produces travel, and the wall stops it |
| Retail niche C2 (16222,19554) E / C3 (16098,19534) W | **16223 / 16095**, z 48. This matches 10-09 |

- **Mobility.** After each 1.0 s-hold and niche jump, a 1.0 s south burst moved +232 (one +64,+192; C3 +72,+64) and a north burst moved −96 to −104.
- **Wall hits.** None passed through or wedged.

## J4b: pool-stone hops, PASS (with finding 1)

From `run1009-s00-map8-pool-stone-g.sav`, the aim pixels were projected from the 10-09 aim points and each was confirmed by a probe click.

| Hop | Aim | Probe | Landed |
|---|---|---|---|
| G → H | (30794,21734,8) | `Item 7941 … STANSTON` | **(30793,21734,8)** (`J4-hop-G-H`, `-sheet`) |
| H → I | (30797,22130,8) | `Item 2046` | **(30797,22130,8)** (`J4-hop-H-I`, `-sheet`) |
| I → J (extra) | (30575,22351,8) | `Item 2150` | **(30575,22352,8)** (`J4-hop-I-J`, `-sheet`) |

- **Taps.** As in 10-09, the first tap only turned the Avatar and the second jumped. hp stayed 30.
- **A first G → H attempt** aimed 4 px lower on screen and landed at (30809,21750,8). That is still on H, and it follows the cursor.

## J4c: cave ascent, PASS

The protocol is the 10-09 part-C one: teleport to (x,23622,0), a 0.3 s walk west, then SPACE and, 60 ms later, Up, both held 1.6 s.

| x | End |
|---|---|
| 29508, 29516, 29524, 29512, 29520 | **(29356 / 29356 / 29372 / 29352 / 29368, 23622, 56)**, 5 of 5 |
| control 29500 | (28996,23622,0), no climb |
| control 29532 | (28932,23622,0), no climb |
| Up first, then SPACE, at 29516 and 29508 | (28980,…,0) and (28972,…,0), **no climb** (finding 3) |

## J5: open-ground jump length, PASS

From (16334,19450,48) facing W, Up then SPACE held 0.35 s, three times:
- **Ends:** (15822,19450,48), (15830,19450,48) and (15822,19450,48).
- **Lengths:** 512, 504 and 512 units, against 10-09's 512.

From open ground at z 0 (J1-E), the jump went 528 units.

## L: log hygiene, PASS

`vjump/lv_run.log` has 6,586 lines, from one launch and three in-game loads.
- **Zero counts:** `stuck in process loop`, `Unhandled intrinsic`, Segmentation, Assertion, `Trying to access segment`, `Cycle in paint`, `popToContainer`, `Non-existent process PID (0) in implies`, `stale gravity` and `FIXME`.
- **Engine warnings:** two `ANIMLOCK set on actor 120, skipping anim`, plus the stock startup warnings.

## Estate

`tools/run_all_tests.sh` reported **44 of 44 discovered file(s)**.
- **Result.** Filtering out PASS lines left only the banner, so there is no FAIL or ERROR line.
- **Runtime.** It ran in 194.7 s, with siblings sharing the CPU. The first run overran a 180 s tool deadline after printing only PASS lines.

## Findings outside the brief

1. **A pool hop aimed at a stone's visual centre drowns the Avatar.** It happened 2 of 2 times.
   - **What I did.** From G (30535,21520,8), I aimed at window pixel (331,269). The probe click there logged `Item 7941 … STANSTON` (stone H), so the cursor was on H's top face. SPACE jumped.
   - **What the log shows:** `7944 event 9` (left G), the egg `917 event 7`, `7941 event 9` (touched H, then released it), `15078/15068 (CLRWATER) event 6` (gotHit). Then hp 0 and the tombstone.
   - **Plate:** `F1-pool-center-aim-drown-sheet` shows the splash beside H.
   - **Reading** [INFERENCE].
     - `U8AvatarMoverProcess::jump` hands `TraceCoordinates`' point to `TargetedAnimProcess`, and the tracker lands the Avatar's **location** there. The location is the max-x/max-y corner of a 64×64 footprint, the screen-bottom corner.
     - Pixel (331,269) maps to about (30753,21694) on H, a 96×96 stone at x 30719..30815, y 21663..21759. The body then spans x 30689..30753 and y 21630..21694, so more than half of it hangs over water.
     - Every hop that landed safely aimed at the stone's front (screen-bottom) third.
   - **Is it new?** The code path is untouched by the fork (`u8_avatar_mover_process.cpp` is not in the diff), and no rise is cut over open water, so `_zLost` stays 0. This is most likely stock behaviour, not a regression.
   - **Why it matters.** A player who aims at the middle of a stone dies. Worth a line in the route guide: "aim at the near (bottom) edge of each stone".
2. **The give-back also lengthens some cut jumps** [INFERENCE from the replica]. A descent frame whose dz is absorbed to 0 is no longer refused by the floor plane, so it keeps its horizontal travel.
   - **The replica:** the tunnel-lintel jump S goes from "no travel" (old rule) to +176 (new rule), and the arch jump E from +176 to +240.
   - **In the engine** the tunnel S jump went +335, the same as 10-09's old-build reading, so the replica overstates it (it has no sweep or `scanForValidPosition`).
   - **Effect.** No landing changed level, and none crossed a wall. Noted only so a later "this jump goes further than before" is not a surprise.
3. **At the cave, Up-first does not climb even inside the window** (29516 and 29508 both jumped −536 to z 0). SPACE-first climbs 5/5.
   - **Reading** [INFERENCE]. With Up first, the walk starts during the 60 ms before SPACE. The mover defers the jump while the Avatar is busy, so by the time the climb scan runs he has walked west out of the 17-unit window.
   - **Effect.** Input order, not the fix. The 09-01/09-25 recipe is SPACE first, and it still works.
4. **SPACE-first controls at the cave travel far again.**
   - **Here:** x 29500 went −504 and x 29532 went −600.
   - **10-09 (finding 1):** −104, 0, −96 and −200.
   - **Cause.** The SPACE-alone branch depends on the cursor (checkTurn, mouselength, targeted jump). My cursor was left at the facing-walk point, theirs was not, so this does not compare the engine builds. I did not chase it.
5. **The Map 8 floor layers at z 8 and z 56 sit under 8-unit cave-floor slabs** at (29759..29951, 23519..23551) and around (29247..29535, 25151..25983).
   - **What it does.** Teleporting there puts the Avatar inside the cave floor, invisible.
   - **Who reaches them.** Not a player, but any overhang scan of Map 8 finds them first. This matters to the next verifier, not the game.

## Harness anomalies

1. **`proj()` in the `veng` driver is about 20-24 px high** for picking a point on an item's top face. It uses y = 200 + Δ, and `findShape`'s px note says +20. With 224 my aim landed 15/16 units off, and with 220 it was exact to the unit. The first drowning came from aiming with the old offset (+10).
2. **A 0.3-0.6 s right-button burst only turns the Avatar.** Mobility needs ≥ 1.0 s bursts. The first tunnel round's 0.6 s "mobility" reads are therefore no evidence, so it was repeated at 1.0 s.
3. **The test estate overran a 180 s tool deadline** on the first run. It was rerun with a longer limit.
4. **Overwriting `size`/`flags` in the eval kernel** (from an exec of `climb_sim.py`'s header) broke the driver once. That was my error, not the game's.

## Disk changes

- **Wrote** this report and the plates in `docs/playtest-2026-10-10-jumps/`: `J2-2-*` (3), `J3-*` (3), `J4-hop-*` (7) and `F1-pool-center-aim-drown-sheet`.
- **Scratch** in `/tmp/claude-1000/vjump/`:
  - `game/`, `scummvm.ini`, `run.sh`, `lv_run.log` and `xvfb.log`;
  - `saves/` (`ultima8.001` is a copy of the pool-stone checkpoint);
  - `sp/` (films and frames);
  - `py/`, `flags.py` and `savinfo.py`.
- **Stopped:** my ScummVM and Xvfb `:93`. Nothing else was touched.
- **Not touched:** source, builders, maps, the fork, `shared/`, `TODO.md`, `HANDOFF.md` and `~/lv-checkpoints` (read-only).

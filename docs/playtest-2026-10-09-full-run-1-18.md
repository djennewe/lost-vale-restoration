# Full 1→18 run, cheats off, second attempt — NOT COMPLETED (2026-10-09)

**Build under test.** The build is main `d6b9bc4`. The log reads `usecode/eusecode.flx: cd847392987c3e1f6f7b4bc9e4169838, 1525384 bytes`.
- **Game copy.** The copy at `/tmp/claude-1000/run1009/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Its sha256 values match `shared/build/ARTIFACTS.sha256` exactly: EUSECODE `25503d8a…`, U8SHAPES `bb0e4cda…`, TYPEFLAG `794d4b80…`, ANIM `77e9705d…`, and FIXED `13321f07…` in both places.
- **Fork.** The fork tip is `4ccd3fe7` (10:09:25), and the `scummvm-lv/scummvm` binary is newer (10:09:31).
- **Harness.** Xvfb `:87` ran with my own `scummvm.ini` (`usehighres`, `frameLimit=false`, mute) and my own save directory.
- **Plates.** They are in `docs/playtest-2026-10-09-full-run-1-18/`.

**Outcome.** The session's request budget ran out before any quest step was finished. The chain is banked alive on Map 8, mid-way across the stepping-stone pool, at `~/lv-checkpoints/run1009-s00-map8-pool-stone-g.sav`. Of the step flags, only `lbSpoke` (the Map 0 detour) is set.

## Verdicts

| Step | Verdict | Evidence |
|---|---|---|
| 1 Lord British, Map 39 primary egg | **FAIL (walked approach does not exist)** | The model routes in finding 1. The lane can only be reached through the Map 39 → 40 east-gate trigger box |
| 1 Lord British, Map 8 backstop egg (2200,2230,8) | **NOT DEMONSTRATED** (not reached) | `lbSpoke 1, lbStarted 0, lbDone 0` at the bank point |
| 2-18 | **NOT DEMONSTRATED** | Not reached |
| Hrodny's chest key, trap, crack hint, 828 at the altar, Ezrekal's brewing wait, NPC schedules | **NOT DEMONSTRATED** | Not reached |
| L log hygiene (`run1009/lv_run.log`, 10,067 lines, four in-game loads) | **PASS for LV code** | `Unhandled intrinsic` 0, `stuck in process loop` 0, Segmentation 0, Assertion 0, segment access 0, `Cycle in paint` 0. `Non-existent process PID (0) in implies` appeared 5 times, the known retail-prologue / map-entry family (10-04, 10-08) |

**Cheats used: none.** The console was used only for `objectInfo`, `getGlobal`, `findShape`, `debugflag_enable Object`, `Ultima8Engine::saveGame` and `loadGame`. Two loads came after deaths. There were no teleports, no `Cheat::toggle`, no `Item::grab` and no flag writes. Every door was opened by double-click, and every menu answer was clicked on screen.

## What was walked

1. **Map 3**, starting from `run1008-s00-prologue-after-execution.sav` at (11747,5811,48).
   - **Route.** North along x≈11690 → 11570, through the courtyard to the gate.
   - **The guard.** GUARD1 (NPC 4) stopped the Avatar at (11571,2675). I picked **I am Avatar.** ("All right, Avatar, now I know ya. Now get lost") and then **Bye** (`s00-01`).
   - **The gate.** Walking past him through the gate at (11516,~1700) sent the Avatar to **Map 40 (13038,15042,48)**.
2. **The AVATAR detour fired on arrival.** The log shows `Loading Fixed items in map 0` and then map 40 again. After it, `lbSpoke = 1`, `lbStarted = 0`, `lbDone = 0`.
3. **Map 40 palace.** The route came from `pathfind`, with Map 40's other trigger boxes masked. Three DOOR_NS doors were opened by double-click (`s00-02`).
   - The 08-12 note holds: the way east is the corridor at y≈6910-6970 from (12098,6910), not the doorway at x 12246.
   - Then the x≈13066 corridor north led to the trigger (13054,2322), and on to **Map 7 (15071,26039,8)**.
4. **Map 7: two deaths, then a clean crossing.**
   - **Death 1 at (11095,22563).** hp went 30 → 0 between two reads. A red-and-blue flying creature was beside the body (`s00-03`).
   - **Death 2 at the landing (14791,25999).** It was the same creature (`s00-04`).
   - Both were reloaded from `w-m7-arrive`.
   - **The crossing.** A 3 s run burst west from the landing, then the ford route (12479,25903) → (12479,23551). That passes through the barn: its north door leaves at (12447/12671,23583) wedge a mouse-walker, and the Up key freed him. Then (11839,23400) → (11807,21599) → (10175,21599) → (9823,20991) → (9823,19743) → the trigger (9498,19702). The arrival was **Map 8 (31479,19135,0)** at hp 30.
5. **Map 8, into the pool chamber.**
   - **The walk in.** (30383,19135) → (30383,19655) → (30239,19703) → (30223,20463,8): the north cave bank (`s00-05`). Then round by (30435,20331) to the south-east shore (30603,20811,8).
   - **The hops.** These used SPACE targeted jumps aimed by probe-verified pixels, with the plane point computed for the 640x400 high-res view (centre (320,200), camera z + 20).
     - **Shore → stone 3259 (30591,21151).** The plane point was (30563,21163), and he landed at **(30555,21124,8)** (`s00-06`).
     - **3259 → G 7944 (30591,21535), first try.** The plane point was 464 from the centre, and the Avatar drowned.
     - **Second try**, after a reload. The plane point was (30535,21520), 428 from the centre, and he landed **exactly** at (30535,21520,8) (`s00-07`, frames `sp/jG_*.png`).
   - **Banked there.**

## Findings outside the brief

1. **Map 39: the Lord British egg lane cannot be walked to from inside Tenebrae. Only the Map 8 backstop can fire step 1 without a cheat.**
   - **Method.** I ran `pathfind.py`'s DryReach lattice through a wrapper (`run1009/py/rt.py`) that adds forbidden anchor boxes. The routes ran from the city (18562,14406,48) to the courtyard (17700,19700,48).
   - **Unmasked.** The only route found is (19455,14407) → (19455,14207) → (20031,14207) → (20031,19519) → (17703,19519).
   - **Masked.** With the east-gate trigger's anchor box masked, there is **NO PATH**. The trigger is at (19600,14072), range 0x94, and the box is `x 19312..19951, y 13944..14263` (`egg_hatcher_process.cpp:68-85`, footpad 64). There is still no path with the box cut to y<14232, with climbs up to 40 or with falls up to 200.
   - **Conclusion.** The lane lies outside the east gate, and that gate is the retail Map 40 exit trigger. The 10-08 log already shows the walker bounced back to Map 40 from there.
   - **What it means.** The 10-08 advice ("hand-checked route clear of the gate pool") has nothing to find. A cheat-free player gets step 1 from the `build_map_08.py` backstop egg on Mythran's island. That is the designed fallback, but the primary Tenebrae egg is effectively unreachable on foot.
   - Confidence: high on the model; the engine was not walked through the gate.
2. **Map 7 is lethal for a prologue-fresh Avatar.** He has no weapon or armour (total weight 20, which is his own) and hp 30. A flying creature killed him twice from full hp, within one 5-10 s read interval each time. A real player may arm up in Tenebrae first; this chain cannot without exploring retail Tenebrae. Plan for run-gait bursts and frequent saves on Map 7.
3. **The targeted-jump shortfall is not a fixed function of range.**
   - **The data.** The same stone pair gave a drowning at a 464-unit plane point and an exact landing at 428. From the shore, 352 units gave a 40-unit shortfall.
   - **Likely cause** [INFERENCE]. Large per-frame steps go through `sweepTest` (`animation_tracker.cpp:268-291`). A blocking collision during flight (for example a SEA tile, or the target stone's side if the arc has already come down) stops the jump at the hit point.
   - **Practical rule.** Aim 30-40 units beyond the stone centre, not 110. The 08-16 rule assumed a 2x-scaled 320x240 surface; with `usehighres` the projection is 1x.
4. **The Map 40 palace is the walk; the doors are dynamic, so the FIXED model does not see them.** That model's y-6967 corridor is right. The Avatar wedged in a doorway at (12238..12246,7042) in every mouse direction, and a walk round by (12098,6910) cleared it.
5. **A mouse-walk wedge in a barn doorway** (Map 7 (12511,23535)) was cleared with the Up arrow key. The mouse walk refused all directions; the keyboard step moved him.

## Wall time

| Leg | Time |
|---|---|
| Setup, reading and routing analysis | about 25 min |
| Map 3 → Map 40 | about 4 min |
| Map 40 palace → Map 7 | about 15 min |
| Map 7 (two deaths) → Map 8 | about 15 min |
| Map 8 arrival → stone G | about 20 min |
| Total session | about 77 min (4,639 s from first load) |

## Checkpoints

- **`~/lv-checkpoints/run1009-s00-map8-pool-stone-g.sav`** (new). Map 8, (30535,21520,8), on stepping stone G (item 7944), hp 30, with `lbSpoke 1`, `lbStarted 0` and `lbDone 0`. It was saved with `Ultima8Engine::saveGame`, and the slot's mtime moved. It has not been reloaded.
- No `run1009-sNN` step checkpoint exists, because no step was completed.
- Scratch saves in `/tmp/claude-1000/run1009/sp/`: `w-m7-arrive`, `w-m7-b`, `w-m8-arrive`, `w-m8-bank`, `w-m8-hop0` and `w-m8-hop1-3259`.

## Resume here

Load `run1009-s00-map8-pool-stone-g.sav`, re-send `debugflag_enable Object`, then:

1. **Hop the rest of the chain.** Hop G → H (30815,21759) → I (30815,22143) → J (30591,22367) → D (30335,22111) → E (30111,22367) → west strip (29737,22377), aiming each about 30-40 beyond the stone centre with `aim_scan`/`jump_at` (`run1009` kernel code mirrored in `py/`). Save after every landing.
2. **Reach the trench.** Walk south to (29801,22801,8) and (29845,23533,8), then step west into the trench at (29745,23673,0).
3. **Cross to the gate.** Follow the `--engine-void` route south to (29021,29605,0), then go round to (29273,30353,0).
4. **Climb the gate wall.** Do the SPACE-then-UP climb at x=29241, facing east. That takes you to the plateau at (14686,11210,48). Do not step north (the trigger at (14540,11004) is ±96).
5. **Cross the plateau.** Run to the MYTHAUS egg (13988,15084,48), staying clear of x 12400-12500 (the attacker).
6. **Mythran's island.** Egg 20 → trigger (4094,1794) → (2944,1816). The backstop LB egg at (2200,2230,8) is step 1. Mythran upstairs is step 2.

The per-step guide for 2-18 is `/tmp/claude-1000/run1009/route-guide.md` (scratch, cited).

## Harness anomalies

- **`drv.chord()`** raised "console would not open" once. A retry succeeded.
- **Position reads alternate** between two positions about 104 apart after short mouse bursts toward a target under 60 units away. That is the minimum walk step, not a bad read; use a tolerance of 60 or more.
- **Xvfb.** Started from a bash subshell, it died with the tool call. It was run as a named service instead.
- **The first scout's "route guide" was never written.** It claimed a file it did not create, and a `task` agent rewrote it.

## Disk changes

- **Wrote** this report and 7 plates `s00-01..07` in `docs/playtest-2026-10-09-full-run-1-18/`.
- **Wrote** `~/lv-checkpoints/run1009-s00-map8-pool-stone-g.sav` (new file, nothing overwritten).
- **Scratch** in `/tmp/claude-1000/run1009/`:
  - the game copy, `saves/`, `sp/`, `lv_run.log` and `trace.txt`;
  - `py/` (`drv.py`, `h.py`, `rt.py`, `rtfall.py`, `rtclimb.py`, `edge*.py`) and `route-guide.md`.
- **Stopped:** my ScummVM and Xvfb `:87`.
- **Not touched:** source, builders, maps, the fork, `TODO.md`, `HANDOFF.md`, `shared/`, `~/.config/scummvm`.

# Full 1→18 run, cheats off, third attempt: Map 39 to Mythran's island, NOT COMPLETED (2026-10-10)

**Build under test.** main `13e2731` plus the uncommitted `build_scummvm.sh` detection change.
- **Game copy.** `/tmp/claude-1000/vrun/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. Its sha256 values match `shared/build/ARTIFACTS.sha256`: EUSECODE `ebf03413…`, U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`, and FIXED `511902e8…` in both places. The log reads `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1523533 bytes`.
- **Fork.** `scummvm-lv/scummvm` is dated 01:08:09, after fork tip `11bb31bd` (01:01:11).
- **Harness.** Xvfb `:95` (1280x800) with the window at (480,300). `scummvm.ini` sets `usehighres=true` and **`frameLimit=true`**, with my own save directory. The driver is the `veng` `drv.py`, re-pointed, plus `vrun/py/vr.py`.
- **Plates.** They are in `docs/playtest-2026-10-10-full-run-1-18/`.

**Outcome.** No new quest step was completed. I walked the whole chain from the Lord British courtyard on Map 39 to the landing on Mythran's island on Map 8, cheat-free, and stopped there when the session's request budget ran out. Step 2 (Mythran) is about 4,000 units further on, beyond the island walkway's spiked-ball lanes and an electric gate.

**Cheats used: none.** `Cheats` appears 0 times in the log. The console was used only to read state (`objectInfo`, `getGlobal`, `findShape`, `listProcesses`, `debugflag_enable Object`) and for `saveGame`/`loadGame`. There were no teleports, no `Item::grab` and no flag writes. Every door, hop and gate trigger was done by input.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| Start, step 1 state | lbSpoke 1, lbStarted 1, lbDone 1 | `fl()` at 01:17 |
| Map 39 LB courtyard → tunnel → east gate → Map 40 | **PASS (walked)** | The lane reversed: (16194,20062) → (16194,19422) through the tunnel → canal at walk gait → (18866,14130) → trigger id 5 → **Map 40 (10914,14094,48)**. hp 30 throughout |
| Map 40 palace → Map 7 | **PASS (walked)** | Three doors opened by double-click: DOOR_EW 14460 (12287,9215), DOOR_EW 14496 (12159,7199), DOOR_NS 14497 (12287,6975). Then x≈13100 north → **Map 7 (15071,26239,8)** |
| Map 7 → Map 8 | **PASS (walked)**, no damage this time | West along y≈25975 → barn (12551,23447) → (11863,21719) → (10239,21559) → (9879,19727) → **Map 8 (31571,19135,0)** |
| Map 8 pool chamber, 7 SPACE-targeted hops | **PASS, every hop landed exactly on its aim** (fix `11bb31bd`/`bbcfa209`) | shore → 6079 (30575,21135) → G (30575,21519) → H (30799,21743) → I (30799,22127) → J (30575,22351) → D (30319,22095) → E (30095,22351) → strip (29677,22377). Each aim pixel was probe-checked first. hp 30 |
| South strip → trench | **PASS after a detour** (finding 3) | `pathfind.py --water-margin 32 --engine-void`, 16 waypoints via (31295,23423,0) → (29773,23673,0) |
| Trench → gate trigger id 1 → plateau | **PASS**, by the new recipe (finding 1) | (29761,28645) → (28887,30431) → (29277,30433,0). **Up, then SPACE 60 ms later**, and the trigger fired: **(14687,11210,48)** |
| Plateau → MYTHAUS hut egg → island | **PASS** | West off the pad: a fire shroom took hp 30 → 15 (finding 2). Then a shroom-avoiding route (14039,11991) → (14039,12959) → (14127,13415) → (14127,14175) → (14199,15134). Double-click on DOOR_NS 9271 (14079,15167,48), a walk west at **y 15134**, and the egg fired: **island (6078,1786,0)** |
| Island walkway → trigger 4 → Mythran (step 2) | **NOT DEMONSTRATED** (budget). One death, two reloads (finding 4) | Banked at the landing |
| Steps 2-18 | **NOT DEMONSTRATED** | — |
| L log hygiene (39,066 lines) | **PASS for LV code**, with one note | 0 `Unhandled intrinsic`, 0 process-loop, 0 Segmentation, 0 Assertion, 0 `PID (0)` implies. **15 `Cycle in paint 59 -> 1 -> … -> 59`**, all on the island walkway (log lines 34054-35302): retail item 59 against the Avatar. Not LV code |

## Findings

1. **Map 8 gate wall: the "48-unit wall climb" never existed. The trigger is fired by a forward jump flush into the wall.**
   - **The wall.** The static analysis (`/tmp/claude-1000/vrun/route/map8-static-routes.md`, Q1) shows that every west-wall segment at x 29279-29311, y 30239-31007, is a z-0 piece plus a z-48 piece, so the top is 96 everywhere. Those z-48 records are in retail `FIXED.DAT.bak`, and `build_map_08.py` does not touch the wall. **The 10-09 engine report's finding 4 ("now has a z-48 piece") is wrong:** the wall was already 96 tall on 09-01.
   - **The trigger.** Trigger id 1's hatch box is x 29279..29598. The only reachable in-box cells are flush against the wall's west face (x = 29279, y 30303..30551, z 0).
   - **What worked.** The walk stopped at x 29277. A keyboard jump (**Up first, then SPACE**) from there fired the trigger at once. 09-01's "climb" was most likely the old reversed interpolation parking him in the box [INFERENCE].
   - **Impact.** Every route note that says "climb the gate wall" (route guide Leg E, the 10-09 full-run resume step 4) should read "jump forward into the wall's west face at y≈30431".
2. **The plateau's "unidentified attacker" is the retail FIRESHRO, shape 794.**
   - Class 031A: its `gotHit` explodes the shroom. Three exploded as the Avatar walked west off pad 1 along y 11210 (event 6 on items 7096, 3024 and 15749), for hp 30 → 15 with no monster present: `listProcesses` showed only engine processes, and `findShape 120` found 0 Toraxes.
   - 274 shape-794 items are in Map 8's FIXED. **`findShape 794` lists only the 40 in the fast area**, so use the FIXED dump for routing.
   - This explains the 09-01 plateau deaths better than the static report's Torax/MONEGG theory. MONEGG was never entered.
   - **Advice.** Leave pad 1 north-west, not along y 11210 (shrooms at (14367,11199) and (14239,11231)), and route at least 64 units clear of every 794.
3. **The strip → trench step is blocked by retail invisible walls.**
   - The blocking items are shape 713 at (29951,23455,0) (x 29695..29951, y 23423..23455, z 0-48) and 714 at (29983,23455,0). Both are `SI_SOLID|SI_EDITOR` and present in retail. The Avatar cannot go south from the strip at y 23421.
   - The way round is the `--water-margin 32 --engine-void` route east to (31295,23423), down to z 0, then west along y≈23569 to the trench (29773,23673,0).
   - The 09-01 "(29801,22801) → (29845,23533)" leg cannot be reproduced. With `--water-margin 128` (the default) `pathfind.py` reports NO PATH.
4. **Mythran's island walkway is a retail trap gauntlet: SPIKY spheres (shape 264, class 0108) and a LITZAPNS gate.**
   - **The spheres.** Six of them (NONFIXED, q2/q6) roll along x at 16 units per step in three lanes, bounded by shape-503 editor markers: x 5663-6079, 5151-5567 and 4639-5055. Each contact calls `receiveHit` for urandom(4)+2 with knockback, and repeated contacts cost **11-15 hp in about one second**. Their recorded rows are y[1567,1695) and y[1887,2015), but the film shows a sphere passing right beside the Avatar while he walks y 1750-1794 (plate `s02-07`), and the knockback once threw him north to y 1670. I could not establish a reliably safe y in the walking lane. The last attempt used y 1816, between the posts' y window [1791,1823]; it was banked untested.
   - **The gate.** LITZAPNS shape 837 at x 4447-4575 (posts at y 1663-1727 and 1823-1887) idles for a random time, shows frame 1 for 60 ticks and frame 2 for 30 ticks, then zaps the gap for 5-9 hp with knockback. **Cross only while `findShape 837` reports frame 0.**
   - **The death.** The death (`s02-05`, hp 23 → 0 at x 4400-4600) was my `go()` loop walking back and forth through the gate under knockback.
   - **Arrival.** My driver kept walking toward the plateau target after the hut egg fired. That drove the Avatar south-east into the y≥1887 sphere row (hp 26 → 6, `s02-04`). On arrival, stop and re-aim west.
   - All of this is retail content, not an LV defect. It is the hardest leg so far for an unarmed prologue Avatar with 30 hp.
5. **MYTHAUS hut door.** DOOR_NS 9271 opens on a double-click, but a west walk at y 15070-15102 wedges on the frame. The hatch fired from **y 15134**, inside the door's opening (y 15039..15167).
6. **Static routes for the rest of Map 8** (static analysis, `map8-static-routes.md`):
   - **MYTHAUS exit condition (Q3).** Egg 2 (3071,1791) teleports when **Z < 48**. The route guide's "z ≥ 48" is inverted, so leaving is a walk 128 east from pad 4 at ground level.
   - **Q4 waypoint lists:** plateau → shuttle T26 → north region → the doors at (20430,3250,0), avoiding T212 (x ≥ 20484), T27 and the troll egg.
   - None of this has been walked yet.

## Harness anomalies

- **Short mouse bursts often only turn the Avatar.** A walk burst under ~1.5 s did nothing at several stops. Walk-gait legs need 2-3 s bursts, and walking moves about 53 units per second.
- **Each console read costs about 6 s.** The world is paused while it runs, so readings are precise but slow.
- **The death book.** `loadGame` from it worked directly: no chooser was needed and the book was gone afterwards.

## Checkpoints

- **`~/lv-checkpoints/run1010-s01-m8-island-landing.sav`** (new; md5 `64d0934b…`). Map 8, island landing (6078,1816,0), hp 30, with lbDone 1, mythranToldZealans 0 and mythranIntroDone 0. It was saved with `saveGame` and the slot's mtime moved. It has not been reloaded.
- **Scratch banks** in `/tmp/claude-1000/vrun/sp/`: `w-m39-canal-n`, `w-m40-corridor`, `w-m7-arrive`, `w-m8-arrive`, `w-m8-shore`, `w-m8-hopG/H/I/J/D/E`, `w-m8-strip`, `w-m8-strip-s`, `w-m8-trench`, `w-m8-gate`, `w-m8-plateau-pad`, `w-m8-hut-door` and `w-m8-island-land`.

## Resume here

Load `run1010-s01-m8-island-landing.sav` and re-send `debugflag_enable Object`. The Avatar faces west on the island at y 1816.

1. **Cross the three sphere lanes.** Go west at y 1791..1823 (posts at x 5855-5887, 5343-5375 and 4831-4863). Read the spheres with `findShape 264` before each lane, and run through when that lane's two spheres are far from the line. The safe stops between lanes are anchor x≈5647 and x≈5135.
2. **Cross the zap gate.** Stop at x≈4700 and check `findShape 837` frame 0. Then run west in one burst to x≈4300, keeping y≈1799.
3. **Mythran.** Walk to (4215,1799) for trigger 4 and pad 4 (2944,1816). Then go west along y≈1831 to Mythran (1503,1791); the upstairs path is in Q3. Steps 2-18 then follow `/tmp/claude-1000/run1009/route-guide.md`, with the fixes in findings 1-3 and 6.

## Disk changes

- **Wrote** this report and 10 plates in `docs/playtest-2026-10-10-full-run-1-18/`.
- **Wrote** `~/lv-checkpoints/run1010-s01-m8-island-landing.sav` (new; nothing overwritten).
- **Scratch** in `/tmp/claude-1000/vrun/`:
  - `game/`, `saves/`, `sp/`, `lv_run.log`, `trace.txt` and `py/`;
  - `route/` (`map8.md` / `map8-static-routes.md`, `map8_route.py`, `r_q2.py`, `dump.py`, `NONFIXED.DAT`), written by subagent Map8Route and me.
- **Stopped:** my ScummVM and Xvfb `:95`. Nothing else was touched.
- **Not touched:** source, builders, maps, the fork, `TODO.md`, `HANDOFF.md` and `shared/`.

# Full 1→18 run, cheats off, part 2: Mythran's island → step 2 done → Map 8 north fire corridor, NOT COMPLETED (2026-10-10)

**Build under test.** main `b1788b3` plus the uncommitted `build_scummvm.sh` detection change. Fork `8af4f74e`; `scummvm-lv/scummvm` is dated 04:01:51, after the fork commit (03:35:20).
- **Game copy.** `/tmp/claude-1000/vrun2/game` is an rsync of `shared/u8-lv-patched` with no `.bak` files. sha256 matches `shared/build/ARTIFACTS.sha256`: EUSECODE `af5789a6…`, FIXED `511902e8…` (root and STATIC), U8SHAPES `69fbd861…`, TYPEFLAG `6bdb3036…`, ANIM `77e9705d…`. The log line reads `usecode/eusecode.flx: 7545064984f3c73b6142d1a87f6d279e, 1523547 bytes`.
- **Harness.** Xvfb `:99` (1280x800), with the window at (480,300), `frameLimit=true` and a private save dir. The driver is the `vrun` `drv.py`/`vr.py`, re-pointed. The first launch used `usehighres=true`. From 05:45 the run used `usehighres=false` with `scale_factor=2` (finding 3).
- **Plates.** They are in `docs/playtest-2026-10-10-full-run-part2/`.

**Outcome.** The furthest step completed is **step 2 (Mythran's intro)**. Step 3 is blocked, and not by an LV defect. The only walking route from the plateau shuttle to the double doors runs through a retail fire-trap corridor in Map 8's north region, and it killed the unarmed 30-hp prologue Avatar five times. I stopped at the session's request budget, with a checkpoint banked before the corridor.

**Cheats used: none.** `Cheats` appears 0 times in the log. The console was used only for `objectInfo`, `getGlobal`, `findShape`, `debugflag_enable Object`, `saveGame` and `loadGame`. Every move was a mouse walk or run, every talk a double-click, and every menu answer a click.

## Verdicts

| Step / leg | Verdict | Evidence |
|---|---|---|
| Island walkway: sphere lanes and zap gates → trigger 4 | **PASS (walked)**, after one hit-and-reload (finding 1) | Run bursts at y 1818: (6078) → 5494 → 4710 → 4326, then a walk → **pad 4 (2928,1816,0)**. hp 30 (`s02-01`) |
| Pad 4 → Mythran upstairs | **PASS** | Due west at y 1816 → (1904,1816) → north (1904,1688) → up the stair (1868,1644,0) → (1424,1644,48). Then by `pathfind` to (1832,2056,48) |
| **Step 2: Mythran** | **PASS** | Before the talk: lbDone 1, mToldZ/G/D/K 0, mIntro 0, mStock 0. Double-click → "Ah. So the message has arrived at last…" (`s02-02`). Picks: **Lord British says they can help me. → Who searched for the Zealans? → What happened to him? → Where are these double doors? → How do I open the doors? → Farewell.** ("Go carefully, my friend…", `s02-04`). After: **mToldZ 1, mToldG 1, mToldD 1, mToldK 1, mIntro 1, mStock 0** |
| Camera after the talk | **PASS** | It was back on the Avatar, and Mythran walked off (`sp/s02-05-after-bark.png`) |
| Island exit egg 2 (z < 48) → plateau | **PASS** | A walk east at (3064,1808,0) → **(14138,15118,48)**. This confirms the Q3 reading that the 10-08/route-guide "z ≥ 48" was inverted |
| Plateau pad 22 → T26 → north region | **PASS**, hp 30 → 20 | A shroom-avoiding `rt.py` route, 19 waypoints; T26 fired at (7986,12670) → **pad 26 (14540,7940,0)** (`s03-02`). The −10 came near (7954,13518), the MONFAST Troodle spot. Not chased |
| **Step 3: north region → doors → Map 9** | **NOT DEMONSTRATED — blocked by retail traps** (finding 2). 5 deaths | Furthest point (20020,5228,0), about 2,000 units short of the chest (20436,3370) |
| Steps 4-18 | **NOT DEMONSTRATED** | — |
| Leftovers finding 1 (the mover runaway) | **Not reproduced** [INFERENCE: consistent with fork `8af4f74e`] | I walked into and out of the LB backstop egg's box region upstairs (Mythran stood inside it at (2306,2162,48)). 0 `stuck in process loop` all session |
| L log hygiene (36,487 lines) | **PASS for LV code** | 0 each of: `Unhandled intrinsic`, `stuck in process loop`, Segmentation, Assertion, segment access and `PID (0) in implies`. **36 `Cycle in paint`**, the retail item-59/Avatar family on the island walkway (10-10 part 1 saw 15) |

## Findings

1. **The island walkway's damage is the shape-59 zap gates, not the spheres.** Part 1's finding 4 named only the LITZAPNS 837 gate.
   - **The gates.** Each sphere lane has a retail **LITZAPEW (shape 59, class 003B)** gate: x[5823,5887), [5311,5375), [4799,4863) and [4383,4447), each y[1727,1855).
   - **The cycle.** Its idle wait compiles to a discarded `urandom` (`retail_all.dis:~220`), so the gate cycles with no rest: frame 1 for 60 ticks, frame 2 for 30, then a zap, about every 120 ticks. Damage is `urandom(5)+5`, and the zap needs the body to overlap the gate box.
   - **The spheres.** They move only in x, at y 1663/1695/1983 with a 96-unit footprint. Their rows never touch an Avatar at y 1791..1822, the lane between the posts.
   - **The hit.** I took 30 → 14 by stopping inside gate 2 between short bursts. **The recipe:** at y 1818, run bursts that stop only at x ≈ 5494 and ≈ 4710 (outside every gate zone), then x 4326. That went through at hp 30.
2. **Map 8 north region: a retail fire-trap corridor, the step-3 blocker.**
   - **The traps.** All are retail (`findShape`, read only):
     - **Two SPITTERs (shape 795, class 031B)** at (16671,5375,0) and (19138,4502,0). Each hurls FIREBOMBs (804) along the 8-direction toward the Avatar every 200+urandom(200) ticks while it is in the fast area. They have no `gotHit`, so they cannot be killed.
     - **Five MISSTRAPs (696, class 02B8)** fire FIREMISS (697) south at 64 per tick, for `urandom(8)+4` each. They sit at (14879,6655), (15807,6655), (17279,4607), (17951,4607) and (18431,4607); their lanes cross both corridor legs.
   - **No safe route.** A fast-area-aware router (`vrun2/rtfa.py`) found **NO PATH** from pad 26 to the doors outside either spitter's fast area, even with the fast area shrunk to 360×240 px.
   - **The deaths** (log-attributed):
     1. (17148,6844): the walk stalled at a wall corner (finding 4) under bombs.
     2. (16972,6964): hp 25 → 0.
     3. (20252,5292): at the riser corner by spitter 2, hp 30 → 0 over 4 reads.
     4. (20144,4776): after an overshoot, hp 11 → 0.
     5. (20014,5274), low-res: hp 25 → 0 in one read gap.
   - **One partial success.** Twice the spitter-1 half was crossed with 0-8 damage, by axis-aligned run legs: (16990,7228) → (16990,6700) → (17440,6676) → (17440,5160) → east along y 5164.
   - **Impact.** The step-3 route in the route guide (Q4 Leg B, "untested in engine") is lethal for an unarmed 30-hp Avatar. A real player would arm and armour first. If the LV design expects the doors to be reached this way, that is a balance/route issue for the author. It is not an LV code defect: every trap is retail.
3. **`usehighres=true` enlarges the fast area.** `CurrentMap::updateFastArea` uses the GameMapGump dims (`current_map.cpp:469-474`). At 640×400 the active zone is about 448×264 px half-size against about 288×164 at 320×200, so traps and spitters wake from about twice as far away.
   - **Effect.** High-res harness runs are harder than the retail game here.
   - **This run.** I switched to `usehighres=false`, `scale_factor=2` (window 640×400, same click coordinates after a `windowmove`). Spitter 1 was then passed unharmed once, and spitter 2 still killed the Avatar.
4. **Route-model seams.**
   - `dump.py`/`load_map` do **not** expand globs. I used `expand_globs` for every check, which gave 28,244 items against 4,371. Unexpanded, they hide solids such as shape-65 mushrooms.
   - The strict `rt.py` route's 24-unit jogs at (17143,6783) and (13831,14559) are too fine for the mouse walker. It accepts a stop within 56 units, then wedges on wall 26 (x[17151,17279) y[6783,6815)).
   - Clear x lanes, verified with expanded globs:
     - x[17399,17463) is clear from y 5100 to 6783;
     - y[5143,5207) is clear from x 17399 to 20250;
     - x[20166,20230) is clear from y 3250 to 5215.
5. **Each console read costs about 1 s of game time.** Three reads let 10 trap missiles fly, against 30 in 10 s idle. So reads are not free in a trap zone. Being hit also interrupts a run burst, which defeats blind timed sequences.

## Harness anomalies

- **A Farewell click missed.** The menu shifted 10 px between detection and the click, so the click landed on a stale row. Re-detecting the bullets fixed it. Bullet detection: pixel (213,48,49) with a black ring.
- **`go()`/`path()` do not notice an intra-map teleport.** After the egg-2 fade the walker kept aiming at the island target, a harmless 500-unit drift on the plateau. `go2` (in-kernel) checks for a jump of more than 1500 units.
- **Run bursts from a standstill often only turn the Avatar** (the `fl400` reads). A walk-gait fallback after one non-move fixed it.
- **Mythran strikes needed a frame-diff locator**, because projection clicks hit floor tiles while he loiters. It is a two-grab diff ANDed with a robe-colour mask.

## Checkpoints

- **`~/lv-checkpoints/run1010-s02-mythran-intro-done.sav`** (new; md5 `508fcedf…`). Map 8 upstairs (1832,2056,48), hp 30, after the talk. lbDone 1, mToldZ/G/D/K 1, mythranIntroDone 1. Not reloaded.
- **`~/lv-checkpoints/run1010-s02b-m8-north-pre-spitter.sav`** (new; md5 `ef4819ff…`). Map 8 north region (15356,7228,0), hp 30, step 2 done. Reloaded 5 times and good.
- **Scratch** in `/tmp/claude-1000/vrun2/sp/`: `w-pad4`, `s02-mythran-done`, `w-pad26`, `w-pad26-hp30` (14540,7940,0, hp 30) and `w-pre-spitter`.

## Resume here

Load `run1010-s02b-m8-north-pre-spitter.sav` and send `debugflag_enable Object`. Prefer `usehighres=false`.
1. **Cross spitter 1.** Use run legs with few reads: x → 16990 (the wall stops you at 17012), y → 6700, x → 17440, then y → 5160.
2. **Cross spitter 2.** Run east on y 5164 and **stop before the riser at x 20255**, with no reads near (20000-20300, 5150-5300). Then run north in the x[20166,20230) lane to y≈3310, or go further east (x≈21000, out of spitter 2's fast area) and come back west at y≈3600. Keep x < 20484 in y 3172..3491 (T212).
3. **The doors.** Chest (20436,3370) → key q99 → use it on both leaves → T201 → Map 9.

If it keeps failing: the Avatar needs equipment or hp the prologue does not give. Report it as a route/balance blocker for step 3 rather than cheat past it.

## Disk changes

- **Wrote** this report and the plates in `docs/playtest-2026-10-10-full-run-part2/`: `s02-01…04`, `s02-03b`, `s03-02`, `s03-03`, and the top-downs `s03-04` and `s03-05`.
- **Wrote** the two new checkpoints above (nothing overwritten).
- **Scratch** in `/tmp/claude-1000/vrun2/`: `game/`, `saves/`, `sp/`, `py/`, `lv_run.log`, `trace.txt`, `scummvm.ini` (+`scummvm.highres.ini`), `run.sh`, `rtfa.py`, `mk8.py` and `m8x.pkl`.
- **Stopped:** my ScummVM and Xvfb `:99`.
- **Not touched:** source, builders, maps, the fork, `TODO.md`, `HANDOFF.md` and `shared/`.

# Verifier pass: `integrate/vignettes` (2026-10-17)

The branch is HEAD 728d37e plus the uncommitted merge fixes. Every artifact was rebuilt from source in the main checkout.
Main's artifacts were rebuilt in a throwaway worktree of `main` 9d73b1b, and they reproduced main's recorded hashes exactly. That build is the baseline for claim 7.
ScummVM ran on `scummvm-lv-console/scummvm` (the text-console build, Oct 17 02:19, which postdates fork tip e48f8716) on the harness dir that `tools/integrate.sh` had just synced.

## Verdicts

| # | Claim | Verdict |
|---|---|---|
| 1 | `tools/integrate.sh` passes and is reproducible; estate 52/52 | **PASS** |
| 2 | Compilation Report failures are exactly the DEV_ALLOWLIST pair | **PASS** |
| 3 | Shape ids 874-880 are consistent; no pinned id renumbered | **PASS** |
| 4 | Moved pins are consistent everywhere | **PASS** (4 stale literals in tooling and test seeds: findings 4-5) |
| 5 | Routes and apertures (`exact_reach`); no 13<->17 bounce; pad 210; Atli | **PASS** (static). One 3.5 s wall-follow loop is finding 6 |
| 6a | Shot windows match the published SCORES.md | **PASS** (screen11/18/01 within 0.04 pt; screen19 better, explained) |
| 6b | Walk Map 13 base -> summit -> Map 17 -> back | **PARTIAL**: the climb and both triggers were walked. The base was reached by warp, because Map 10's trigger 207 is behind the key gate (shape 114 q170) |
| 6c | A Shield half is the 878 art and the quest item | **PASS** for the art, the look text and the class. The pickup was `Item::grab`; the drag was NOT DEMONSTRATED |
| 7 | Maps 8, 18, 39 unchanged vs main | **PASS** |

## 1. Integration (PASS)

`tools/integrate.sh` (verify mode) logged:

- `patch equals the fork diff (26 files)`
- `build rebuilt; all 5 match ARTIFACTS.sha256`
- `pins unchanged`
- `engine built; detection current (md5-5000 84615e29…, 1528216)`
- `install` and `harness` canonical
- `estate PASS — 52/52`
- `RESULT: PASS`

This run is a second, independent rebuild, and it produced exactly the recorded hashes: FIXED 64f0e85a…, U8SHAPES f151f945…, TYPEFLAG 33e15c95…, EUSECODE 2048fc6e…, ANIM 696dbeb9…. Logs are in `/tmp/lv-integrate.vEahtO/`.

## 2. Compilation Report (PASS)

56 files compiled, 54 succeeded, 2 failed. The two failures are exactly `EALOGO.UNK` (unterminated block comment) and `TJORVI.UNK` (unterminated string). Main's build has the same counts.

## 3. Shape ids (PASS)

The ids agree across every place they are recorded:

- `lv_shapes.py` has `SHAPE_CLOUD_1994=874` … `SHAPE_GEM_CAP_1994=880`, and `SHAPE_SHIELD_HALVES = SHAPE_SHIELD_HALVES_1994` (878).
- `u8c_symbols.py` has `'TypeAOFrizbee': 878`.
- The `docs/art-track.md` rows 874-881+ match.
- `.claude/rules/shape-ids.md` says 874-879, 880 the gem cap, and 881 next.

Nothing that was already numbered changed:

- In the diff against main, the only constant whose value changed is `SHAPE_SHIELD_HALVES` (870 -> 878), which is intended. 861 and 870 stay built.
- `lv_manifest.json` is unchanged against main.
- No usecode source names 870 or 878 as a literal. REAPPLY, SHADES and AORTA all go through `TypeAOFrizbee`.

## 4. Pins (PASS, with stale literals)

The built FIXED.DAT carries every pin the brief lists:

- Map 9: trigger 200 at (13759,12031).
- Map 10: pad 210 at (18432,22719,112).
- Map 11: receptacle 866 q203 at (7935,21759).
- Map 13: pad 208 at (5119,2303,120) and trigger 209 at (4351,2303,120).
- Map 17: pad 209 at (4608,9984); trigger 208 at (4608,11008); 878 f0 q81 at (4259,7199,0) and f1 q82 at (3559,3311,0); scroll 864 q80 at (3328,1536,8) resting on an 877 plinth (top 8); plaques 614 q69/70/55/68 at z16, each on the south face of a shape-15 stele.

`test_route_reach`'s gateway table matches the eggs. `derive_map_pins` reports "unchanged".

Atli's (19231,6943,0) agrees in three places: `build_map_10.py`, `lv-patched/ATLI.UNK:492` and `SHADES.UNK:849`.

The receptacles' `within 300` boxes each still hold exactly one pillar. q203 is 255 away from pillar f2.

Stale literals are listed under findings 4 and 5.

## 5. Routes (PASS, judged with `exact_reach`, step 8)

All of the following were run against the recorded FIXED/TYPEFLAG/ANIM.

**Map 13.** Pad 207 reaches trigger 209's hatch box (444 lattice positions). From pad 208 the flood reaches trigger 209, trigger 206 and pad 207, so the descent works too.

**Map 17.** Pad 209 reaches:
- both halves, the scroll and all four plaques, within a 64-unit ring;
- trigger 208's box (880 positions).

**Aperture margin.** I re-flooded with bodies of 72, 80 and 96 instead of 64. Every Map 13 and Map 17 target is still reached, so no leg of either route is a one-body-width aperture.

`pathfind.py --erode 1` reports NO PATH on Map 13. That is a tool limitation: erosion is applied per level, so it cuts every riser. It is not a seam.

**Bounce.** I ran `avatar_mover.hold` with all 8 headings × 8 modes, both moving and standing:

| Pad | 1.5 s | 4 s | 8 s |
|---|---|---|---|
| Map 17 pad 209 | 0 triggers | 0 triggers | 0 triggers |
| Map 13 pad 208 | 0 triggers | 1 trigger (finding 6) | 5 triggers, all NE keyboard holds (finding 6) |

**Map 10 pad 210.** Standable at z112 and reached from pad 205. Pad 210's own flood reaches pad 205 and triggers 211, 213 and 204. An arrival facing N (the way a Map 18 return arrives) holds clear in every mode.

**Atli.** I flooded with his body, his own record removed, from (19231,6943). He reaches both the hut interior and the outside. 371 of the 436 loiter targets (±320 on a 32 grid) are reachable; the 65 that are not are roof-top levels 40-96 only. He is not trapped.

## 6. In-engine

### 6a. Vignette captures (PASS)

`vignette_capture.py`, rerun on 2026-10-17:

| Shot | Published class | Today class | Today RGB |
|---|---|---|---|
| screen11 | 98.24 | 98.28 | 98.26 |
| screen18 | 94.62 | 94.65 | 94.47 |
| screen19 | 91.74 | **94.46** | 90.92 |
| screen01 | 91.21 | 91.21 | 91.16 |

The first screen11 attempt failed with "could not turn cheats on", which is a harness flake; the retry is the row above.

Screen19 is higher because the published capture had the grey winged figure (finding 1) painted over the roof, and today's did not.

Screenshots: `V1-V4`.

### 6b. Walk (PARTIAL)

1. **Start at the base (warp).** I warped to Map 13's pad 207 (`A0`), because the way in from Map 10 to trigger 207 is the key gate: shape 114 q170 at (7168,23552,8), double-click logged.
2. **Climb.** Walked the climb by mouse to the summit at z120 (`A1-A5`).
   - A harpie, and later two more on the summit, stun-locked the invincible Avatar. I moved them off with `Actor::hold`.
   - Run-gait bursts were sometimes refused where walk gait passed; harness notes below.
3. **Into Map 17.** Walked S into trigger 209. The log shows `Loading Fixed items in map 17`, and the Avatar arrived at (4608,10216,0) (`B1`).
   - Negative control: a further 2 s run held S stops at the void channel at (4608,10480) with no teleport (`B2`).
4. **To the half.** Walked to the sun half (`B3`).
5. **Back to Map 13.** Walked round the east end, then S into trigger 208. He arrived on Map 13 at (5119,2407,120) (`B6`).
   - Negative control: a 1.5 s run held W toward trigger 209 stops at (4939,2363) with no teleport (`B7`).

### 6c. Shield half (PASS for art and class; drag NOT DEMONSTRATED)

- `findShape 878` finds item 20255 (shape 878 f0 q81 n236) at (4259,7199,0) and item 21429 (f1 q82) at (3559,3311,0).
- My click on the half hit column 875 instead, so I used `Item::grab 20255`. The half is then contained (`f: 0xc`) and the pack weight goes 20 -> 50.
- The pack shows the blue sun-half sprite (`B4`).
- A single click on it in the pack logs `calling usecode event 0 @ 04EC:0080` (class 0x4EC = npcnum 236 dispatch) and barks **"Broken shield"** (`B5`).
- Not tested: the drag pickup, and the ceremony consuming the halves.

## 7. Untouched maps (PASS)

I compared FIXED.DAT item by item (x, y, z, shape, frame, flags, quality, npcnum, mapnum) across all 256 slots, main build against branch build. The only changed maps are 9, 10, 11, 13 and 17. Maps 3, 8, 18 and 39 are identical.

## Findings outside the brief

1. **The grey winged follower, identified.** It is a retail **GHOST, shape 411 frame 9**. Item 9471 `(uc: GHOST)` sat at (7208,23176,48), which is exactly Avatar + (40,−120,+40). (`F1`)
   - What creates it is `lv-patched/AVATAR.UNK` `schedule()`'s lbSpoke branch: `lb.create(TypeLordBritish,9); lb.pop(Avatar.getX()+40, Avatar.getY()-120, Avatar.getZ()+40)`. It runs 240 ticks after the first map switch off the Docks, and the log shows map 10 -> 0 -> 10.
   - It does not follow the Avatar. It stays where it was popped, and it is left behind on the map the player came back to.
   - It is not from this branch (AVATAR.UNK is unchanged), but a real player who leaves the Docks will be left a stray ghost beside him.
2. **Black void holes inside screen01's window.** There are 30 uncovered 32-unit cells in Map 13's cloud floor at x 3552-4064, y 1120-1504 (`V5`). Main has 15,413 there, so the branch is a big improvement. They are also visible in the published capture. They are visual only: z=0 supports anything.
3. **Large black voids in Map 13's mid-climb cliff faces**, around (4600-4900, 4300-4900) (`A2`, `A2b`), plus black seam lines between the riser treads. These are rendered pixels a player sees; they are not covered by a vignette score.
4. **Stale Map 17 arrival seed.** `test_monster_eggs.py:131` still floods Map 17 from the old pad (5376,11136,0). It is harmless today: Map 17 has no monster eggs, and the old seed is reachable from the new pad. It should still follow pad 209. `tools/map_viewer/compare_shots.py:39` has the same stale coordinate.
5. **Other stale docs and tooling:**
   - `tools/map_viewer/locations.json:23` still says Hrodny's chest is at (21024,8832).
   - The `exact_reach.py:102` CLI example uses the old pad/half coordinates.
   - `tools/art/static_items.py:96` still lists the 539 halves at (6208/7232,1568).
   - CLAUDE.md's Known Limitations says "53 files / 51 succeed"; the report says 56/54.
6. **A Map 13 wall-follow loop.** From pad 208, a keyboard hold NE carries the Avatar N along x≈5191, W along y≈1471, then S into trigger 209 at 3.5 s (run) or 5.5-6.1 s (walk). That sends him back to Map 17.
   - Outside the 1.5 s claim, and not on the arrival heading (he arrives facing S).
   - The `arrival_corridors` test checks only the S/W headings for 209 at 4 s, so it does not see this.
7. **254,668 "Cycle in paint" lines** in the session log, all `26 -> 564 -> … -> 26` (212k) and `125 -> 66 -> … -> 125` (42k). They were logged while on Map 13; the 564 is the shadow plate. `test_paint_cycles` passes, so its model does not cover these.

## Harness anomalies

- `session.sh dbg` replies get lost after a `MainActor::teleport` closes the console. A second teleport queued and ran on the next attach.
- My walk driver stalled often. Two causes:
  - **Harpie stun-lock.** The Avatar was invincible, and repeated hits interrupted every move until the harpies were moved off.
  - **Run gait.** At several riser spots run-gait bursts were refused while walk gait (mouse offset 90 px) passed. The same spot at (4488,1748) refused and later accepted the same input. I report this as an input-timing or stun artifact, not a geometry defect.
- Unarmed combat clicks did no damage to the harpie (hp stayed at 43).

## Disk changes

- **Written:** this report and `docs/playtest-2026-10-17-vignettes-verify/` (20 PNGs).
- **Regenerated by `tools/integrate.sh`, identical content:** the `shared/build/` artifacts, `scummvm-lv` build, `shared/data/u8-install` and `shared/u8-lv-patched`.
- **Session state:** the harness session was stopped, and `~/.config/scummvm` was rewritten by ScummVM on exit.
- **Temporary:** a throwaway worktree of `main` at `/tmp/vv/main-wt` was created and then removed. Captures are under `/tmp/vv/`.
- **Not touched:** any source, builder, map, the fork, or TODO.md.

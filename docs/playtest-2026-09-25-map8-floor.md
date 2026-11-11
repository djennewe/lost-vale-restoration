# Playtest: a floor under map 8's south route (2026-09-25)

The experiment behind TODO's **DECISION: does map 8's south route get
floored?** (`docs/playtest-2026-09-01-stock-bindings-climb.md`, test C2).
Plates of the route as it ships and as it would look with a z=0 floor laid
under it, from the same five camera positions.

**A z=0 floor is invisible from all five positions plated.** The Avatar
walks that route underneath the retail cave: under its z=56 and z=112
floors, behind its walls, and below the black 564 plates that retail uses as
the bottom of its chasms. All of those paint after anything at z=0, so the
new floor paints and is then covered. The plate pairs differ only by a
wandering ghoul, the mouse cursor, and a stale-pixel notch that also shows
on the canonical build (finding 2).

**The floor did change one thing in-engine: the cave ascent.** Under an
identical protocol the climb at x 29508..29524 succeeded 4/4 on the floored
build and 2/11 on canonical, and each canonical success was the first
attempt of its session (W1). The mechanism is not established.

Setup: fresh world for every plate (a new game, then `Cheat::toggle` and
`MainActor::teleport 8 x y 0`; no savegame, per the map-geometry rule), the
640x400 canvas, crop `+565+336`, **`usehighres=false`** (the player's
default) for every plate. The key was set back to `true` afterwards with the
game stopped. Harness: `scummvm-lv` on `:77`. The first teleport of each
session waited 22 s for the Guardian cutscene.

## Verdicts

| ID | Question | Verdict |
|---|---|---|
| R1 | Where is the floorless stretch? | **Located.** 993 of the route's 1,381 lattice steps stand on nothing; one run of 7,464 units plus three short gaps (§R1). |
| P1-P5 | Does a z=0 floor change what the player sees? | **NO CHANGE** at all five positions. |
| W1a | Does the floor change walkability? | **No, by construction** (zd=0 at z=0); strict `exact_reach` now reaches the gate approach. |
| W1b | Does the floor change the cave ascent? | **YES, in the floor's favour, on small numbers:** floored 4/4, canonical 2/11. Mechanism **NOT DEMONSTRATED**. |
| W2 | Does the test estate notice? | **No.** No test covers map 8's z=0 layer. |
| V1 | Revert restores the canonical artifacts | **PASS**, with one caveat about concurrent edits (§V1). |

## R1: the floorless stretch

`tools/playtest-linux/pathfind.py --engine-void` from the z=8 strip at
(29845, 23533, 8) to the gate approach (29273, 30353, 0), roi
`27000,20000,32700,31000`, gives 11 waypoints:

```
29847,23535 31295,23535 31295,23615 28895,23615 28895,29151 29023,29151
29023,29663 29151,29663 29151,30303 29271,30303 29271,30351
```

Each z=0 lattice step was checked against the strict `ExactReach.mask(0)`
(which demands a real surface). Void runs on the route:

| steps | length | from | to |
|---|---|---|---|
| 191..1123 | 7,464 units | (31295, 23615) | (28895, 28671) |
| 1211..1235 | 200 units | (29023, 29247) | (29023, 29439) |
| 1291..1315 | 200 units | (29151, 29759) | (29151, 29951) |
| 1371..1380 | 80 units | (29247, 30303) | (29271, 30351) |

The long run is two legs: west along y=23615 (the trench) under the z=56
shelf's 301 floor, then south down the column at x=28895, which for most of
its length (y 24679..28647) lies under the z=112 shelf's 301 and 6 floors
and the 564/334 plates above them. From y 28700 south the route is on
retail z=0 flats (564, 334, 6, 301) with the three short gaps between them.

## The floor that was tried

Saved as `docs/playtest-2026-09-25-map8-floor/floor.diff` (the builder is
reverted). `south_route_floor()` in `build_map_08.py`: eight rectangles of
128-cells plus 11 cells of ragged west edge, every cell with no retail z<=8
flat under it (checked against the expanded retail items; two candidate
edge cells that did overlap were dropped).

- **Shape 301** (`SHAPE_ROCK_SLAB_GROUND`), frames 0-6, the frames the
  adjacent retail cave floor uses (hundreds of them at z=8, 56 and 112 in
  this region). Frame picked by a hash of the cell, so no stride pattern.
  Frame counts: 0:24, 1:29, 2:31, 3:27, 4:23, 5:26, 6:24 (184 total).
- **184 items**, all at z=0. Map 8 in the built FIXED.DAT differed from
  canonical by exactly +184 shape-301 items and nothing else.
- Floored FIXED.DAT sha256 `dff8ee9c…` (see §V1 for what else it carried).

## P1-P5: the plates

Each pair is one teleport target, BEFORE on the canonical build and AFTER on
the floored build. The Avatar is at screen centre in every plate and is not
visible in any of them, which is the finding in miniature.

| ID | position | what covers the Avatar | pair |
|---|---|---|---|
| P1 | (29745, 23673, 0), the trench below the climb window | the z=56 shelf's 301 floor | `P1-trench-under-shelf-compare.png` |
| P2 | (28895, 24100, 0), the column's open north end, nothing overhead | the cave's west wall, painted in front of him | `P2-column-north-behind-wall-compare.png` |
| P3 | (28895, 26000, 0), mid-column | the black chasm floor: 564 frame 2 at z=56 | `P3-column-mid-pit-compare.png` |
| P4 | (29151, 29855, 0), one of the short gaps near the gate | the 564 ceiling plates at z=96 | `P4-gate-approach-compare.png` |
| P5 | (31359, 23743, 0), the trench's east end, 130 units from the drop off the strip | the 564 plate at z=56 and the 334 ceiling at z=152 | `P5-trench-east-end-compare.png` |

Changed pixels, BEFORE vs AFTER, per 640x400 plate: P1 1,503, P2 1,108,
P3 72, P4 86, P5 155. P3, P4 and P5 are the cursor. P1 and P2 are the
ghoul, which wanders between runs, plus the notch in finding 2.

P5 was added after the offline preview showed one new tile at the trench's
east end. In the engine that tile is covered too; the preview's painter
sorts by (x+y, z), which draws a z=0 tile after a z=56 plate with a smaller
x+y, and the engine does not.

The black in P3 is retail's own design: a chasm in the z=112 floor whose
bottom is a black 564 plate at z=56. The Avatar at z=0 is 56 units below
that bottom. The screen column through his feet crosses 564 at z=56 from
about (29215, 26320) onward, which is why the pit stays black over a z=0
floor.

Singles: `P<n>-*-before.png` and `P<n>-*-after.png` in the same directory.

### Offline previews

`agents/map-populator/src/map_preview.py` renders only the builder's
additions for map 8, so the previews come from the built FIXED.DAT
(globs expanded) through `iso_render.IsoRenderer`:

- `iso-preview-before.png` / `iso-preview-after.png`: the isometric preview
  of x 28300..31700, y 23300..30800. The new floor is covered by the
  shelves except for a few tiles at the trench's east end and along the
  column, which the engine covers (P5, and the painter note above).
- `plan-before.png` / `plan-after.png` / `plan-compare.png`: a plan view of
  the same box, north up, 8 units per pixel. The z<=8 layer is the base
  colour (black nothing, navy a 564 plate, tan a real floor); a grey wash
  marks where a floor at z 56..152 lies above it; the yellow dots are the
  route and the green squares plate positions P1-P4. The AFTER panel
  shows the 184 tiles and how little of them is outside the grey wash.

## W1: walking and climbing

- **By construction, walking does not change.** Each tile is zd=0 at z=0, which is on
  the 4-unit lattice, cannot block (`Box::overlaps` needs `_z + _zd > o._z`,
  `.claude/rules/map-geometry.md`), and supports standing only at z=0, where
  the engine's freebie already supported him (`current_map.cpp:773`). The
  climb scan looks for a standable top 16 to 72 above him; a z=0 top is not
  one. The 17-unit window at x 29508..29524 has no new blocker and no new
  top. That argument predicts no change to the climb either; the in-engine
  numbers below disagree with it.
- **The strict model changes.** `exact_reach.py --map 8 --seed
  29745,23673,0 --seed 29845,23533,8 --target 29273,30353,0 --roi
  27000,20000,32700,31000`:

  ```
  canonical: seed (29745,23673,0): NOT STANDABLE (levels here: [])
             reached 67448 of 796070 standable lattice positions
             UNREACHED gate-approach within 96 units
  floored:   seed (29745,23673,0): standing at level 0
             reached 364027 of 847038 standable lattice positions
             REACHED  gate-approach: stand at (29183, 30303, 0)
  ```

  So the strict model stops disagreeing with the engine about this route.
  It would let `pathfind.py` route here without `--engine-void`.
- **In-engine climb.** Protocol, identical on both builds: fresh session,
  `tp` to (x, 23622, 0) with the position re-read until it matches, a 0.3 s
  right-mouse burst toward world west (turns him without moving him; the
  start position is re-read afterwards), a settle (1 s for the first four
  canonical attempts, 2.5 s for every other), then `xdotool keydown
  --window <W> space`, 60 ms later `keydown --window <W> Up`, both held
  1.6 s. Success means ending at z=56.

  | build | session | attempts (start x: result) | climbs |
  |---|---|---|---|
  | floored | fresh | 29516: z56, 29516: z56, 29508: z56, 29524: z56 | **4/4** |
  | canonical | after the plates | 29516: z56, then 29520, 29516, 29524, 29516, 29516: z0 | 1/6 |
  | canonical | fresh | 29516: z56, then 29508, 29524, 29516, 29516: z0 | 1/5 |

  One more canonical attempt, right after the fresh session's success, was
  cut off by a command timeout and its result was never read. A failed
  attempt walks him west to x≈29230 at z=0. Successes end at (29356..29364,
  23622, 56), the position the 2026-09-01 record gives.

  Earlier attempts sent the key events without `--window` (about six on
  the floored build, four on canonical, some with the facing unverified).
  None climbed on either build, so those runs say nothing about the floor.

  One reading, unverified: over a floorless z=0 the Avatar stands only on
  the freebie support, with no `SI_LAND` item under him, and something in
  the jump path (a grounded or falling check) behaves differently after he
  has walked on nothing. The first attempt of a session comes straight off
  a teleport, which may reset that state. Eleven and four attempts are small
  numbers; this wants a source read of the jump branch before it is used
  for the cave-ascent decision.

## W2: the test estate

`tools/run_all_tests.sh` on the floored FIXED.DAT: 30/31, and the one failure
was Map 17 (finding 3), unrelated to the floor. `test_route_reach.py` checks
map 8 only for its gateway table and hatch-box clearances, and
`test_map_hygiene.py`'s `void_in_view` covers the LV maps (9, 10, 11, 13, 17,
18), so neither encodes "map 8's south route is void". On the canonical
build after the revert: **31/31 PASS**.

## V1: revert and hash check

`build_map_08.py` restored with `git checkout` (its diff held only this
experiment; `git diff --stat` on it is empty). `tools/build_artifacts.sh`
then printed:

```
  TYPEFLAG.DAT   OK    9f534e59c05b1f480735faee034b00f6c426c13c4f764763293c7b27a2022b13
  U8SHAPES.FLX   OK    a611e9be16bcd906a34f1ffc065c444b2c3c053f69ad9bf4ac7c55fa7f972bcd
  EUSECODE.FLX   DIFFERS   (built 7c3db807…; uncommitted usecode edits, expected)
  FIXED.DAT      DIFFERS   (built b9cc0da8…)
```

The FIXED.DAT mismatch comes from map 17. Uncommitted edits to `build_map_17.py`
and `lv_shapes.py` appeared in the working tree during the session. Map by
map against canonical, the rebuilt FIXED.DAT differs only in map 17 (+3
shape-614 items); map 8 is identical. To show the builder at HEAD reproduces
the canonical file, `build_all_maps.py --no-previews` was run in a throwaway
`git worktree` at HEAD (54e7f13) with `shared/data` linked in:

```
TYPEFLAG.DAT: OK
U8SHAPES.FLX: OK
EUSECODE.FLX: OK
FIXED.DAT: OK
```

`shared/build/FIXED.DAT` and `EUSECODE.FLX` were then restored from the
canonical copies taken before the first build, `tools/build_artifacts.sh
--verify` printed PASS for all four artifacts against the canonical hashes,
and `install_lv.sh` reinstalled them. The same restore and check ran again
after the follow-up climb sessions (W1). The worktree is removed.

## Findings outside the plan

1. **The route is underneath the map.** The Avatar is invisible for the
   whole south route, hidden by floors, walls and black plates that sit
   above him. A floor under him cannot fix that; making the route visible
   means routing it on a level the camera can see (the z=56 shelf the seam
   doorways already joined) or cutting the cover above it, which is retail
   geometry.
2. **The P1 notch is stale pixels.** A roughly 30x25 pixel gap in the
   cave wall at plate (114..145, 192..218) showed dark rock texture in the
   first canonical plate and black in both floored plates. A second
   canonical plate, in a fresh session, showed it black as well, with a
   different outline. Nothing paints there on either build, and with
   `usehighres=false` the gap keeps whatever the previous frame left. No
   `Cycle in paint dependency` line was logged on the floored build.
3. **Concurrent working-tree edits to map 17** (`build_map_17.py`,
   `lv_shapes.py`, three shape-614 items) arrived during this session and
   were baked into the floored FIXED.DAT. They produce two validator WARNs
   ("SF_QUALITY placement sits on pure-black floor", map 17 at
   (2495, 5121, 16) and (5055, 5121, 16)), which failed
   `test_map_roundtrip.py` on that build. They were left alone. The next
   `tools/build_artifacts.sh` on this tree will write a FIXED.DAT that
   differs from canonical for that reason.
4. **TODO's "unexplained, seen once (2026-09-05)" map-0 visit matches the
   Guardian cutscene.** That entry found the Avatar on map 0 at
   (15967, 19711, 0) and back a moment later. The playtest traps file
   (2026-09-19) records the first-teleport Guardian scene teleporting him
   to exactly (15967, 19711, 0) on map 0 and back. Same coordinates.
5. **The BFS detour.** The route leaves the drop point east to x=31295 before
   turning west along the trench, because the z=8 strip's south edge is
   walled until then. The long column runs at x=28895, west of the cave's
   west wall line.

## Harness anomalies

1. **`dbg.sh` alternates.** About every other call, a teleport did not
   land, and position reads returned the previous command's reply. Letters
   from a command typed at a closed console opened the pack (`i`) and the
   minimap (`m`). Worked around with a pixel probe that closes both before
   each plate and a retry loop that re-reads the position until it matches.
2. **Devon's conversation at a fresh start** took one click on
   **Goodbye.** at window (415, 158) and four to seven more to page his
   farewell; the chord is dead until it is gone.
3. **Key events need `--window`.** Plain `xdotool keydown space` and
   `keydown Up` moved the Avatar (UP reached the game) but never produced
   a climb in about ten tries across both builds; with `--window <W>` on both, the floored build
   climbed 4/4. The 2026-09-01 recipe does not say which form it used.

## Disk changes

- `docs/playtest-2026-09-25-map8-floor.md` (this file) and
  `docs/playtest-2026-09-25-map8-floor/`: `floor.diff`, the five plate
  pairs with a `-compare.png` each (P1-P5), `plan-*.png`,
  `iso-preview-*.png`.
- `shared/build/` and `shared/u8-lv-patched/`: canonical, all four hashes
  match `ARTIFACTS.sha256`.
- `~/.config/scummvm/scummvm.ini`: `usehighres=true` again.
- No source file changed; the map 17 and usecode edits in the working tree
  are someone else's and were not touched.

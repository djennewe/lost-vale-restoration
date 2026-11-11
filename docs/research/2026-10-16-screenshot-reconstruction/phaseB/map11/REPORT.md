# Phase B — Map 11 (screen05 fire wing, screen07 Pillar of Fire), 2026-10-17

Worktree `lv-wt-map11`, branch `wt/vignettes-map11`. Status: **INTEGRATED.**

## Scores (`vignette_built_window.py`, built FIXED.DAT; void counts as black)

| Shot | Replay class | Floor (−0.5) | Built window |
|---|---|---|---|
| screen05 | 83.295 | 82.80 | **89.00** |
| screen07 | 86.939 | 86.44 | **86.93** |
| screen10 (Map 9, unchanged) | 86.985 | 86.49 | 88.06 |

Evidence here: `screen05_built_window.png`, `screen07_built_window.png`
(shot | built | diff), `screen05_context.png`, `screen07_context.png` (3x3
windows, built shapes, Avatar at the shot's spot):
`python3 agents/map-populator/src/lv_cave_vignette.py context screen07 out.png 7448,21368,0`
(screen05: `2744,15160,0`). Neither context render shows an unpainted
(magenta) hole. screen07's window has 6 unpainted px, and the shot is
black there.

## What changed

- **Fire wing (screen05).** The floor glob is 480 → 397 (cave rock 301,
  what the shot shows). The NW quadrant is rock (`SCREEN05_MASK`, cols
  8..25, rows 112..127). The pocket opens east onto the N–S causeway, and
  the rock's south edge steps down to a strip beside the causeway.
  `UNDER_NW_ROCK` removed lakes (1,1), (2,1) and (1,2), pools (2048,15360),
  (3072,14848) and (3072,15872), flames (1792,15104) and (3200,15104), and
  the spire (1664,16000). The other flames keep their shapes.
  - Fire field 400 at (2687,15071,0): relifted 2, which leaves its pixels
    unchanged. Before that, map_validate's centre-box read the void plate
    beside its tile.
  - Fire field 400 at (2879,15679,48): left out. It hangs over the black
    lip and no relift puts it over floor (89.82 → 89.00).
- **Four Pillars chamber (screen07).** It is a cave now: glob 65 → 397. The
  N, W and E stone walls, lamps, tapestries, 301 paving squares and centre
  slab are gone. The south gate line stays: three stone courses, built
  explicitly. `SCREEN07_MASK` covers cols 48..79 and rows 152..174. Its
  rock is the shot's band, column 48 (so the rim's straddling west course
  is rebuilt as a seen face) and corner outcrops.
  - 2020 is the pin itself (865 f2 q203, held; the vignette's copy is
    dropped).
  - 2022 (lava glow residual) is left out. Its best fit, 409 f20 for
    +0.31, would be an off-lattice burning flat over the floor.
  - Spikes: a window-score search ran over the 26–32, 98–108/112, 125,
    186, 66, 138, 334, 393, 469, 472, 519–521 and 736 frames at the
    template-matched offset, z 0..96. It kept **spike 0 → 26 f5 at
    (7544,21176,48), +0.17**. Nothing else gains ≥ 0.05; spike 6's 107 f1
    costs 0.09–0.18 as a whole sprite. Those spikes are left out.
  - The all-black 393 f11 at z 0 is left out (−0.012). Being LAND, it
    stopped the void fill.
- **`lv_cave_vignette.py`.**
  - `Shot.add`: builder-solved stand-ins join the shot.
  - `Cave.underlay`: a 301 tile goes under floor cells whose only ground
    was a shot prop (screen07's 125 f7 left a hole).
  - **`Cave.fences`** also fences the unclassified fine cells of
    window-decided rock cells. Without them, mask floor beside such a cell
    opened onto the rock void, and Map 11 leaked off the map.
  - The context CLI stubs 1994 ids.
  - Map 9 was rebuilt with it and stays green, at 88.06%.
- **`build_map_11`** ends with `place_screen05`, then `place_screen07`, then
  `cave_vignette.void_cover`, which replaces `void_floor`. RELIEF_LINES
  lost the chamber's lines.

## Pin moves (map_pins.json regenerated)

- **Fire receptacle 866 q203 npcnum 120: (7680,21760) → (7935,21759)**
  (`FIRE_RECEPTACLE`). It sits 255 E / 255 S of the pillar, the nearest
  spot SE whose sprite stays out of the frame. Its within-300 box holds
  only the Fire pillar.
  - I chose this over the plan's candle post 453:6: with the socket, all
    four receptacles are the same object. A candle post would be the odd
    one out for a player who has learnt three sockets.
- **Daemon egg group 3: (2848,15104) → (2880,15104).** From the old spot,
  the 32-unit egg-margin check put the body within 25 of the rack's fire
  field.
- **MONEGG trigger group 3: (3392,14592) → (3520,15104),** on the causeway
  at the pocket's mouth. The pocket opens only east now, so the old walk
  was 1.39 × the line.
- Both vignette placement blocks record these moves with their reasons.

## Test changes

- `exact_reach.HURT_SHAPES_U8` += 400 FIREFELD. Its gotHit reaches
  receiveHit at 0190:0173; `test_route_reach`'s survey asked for it.
- `test_art_props`: the "256 south" check now takes Fire at
  `FIRE_RECEPTACLE`. The within-300 and box-overlap checks are unchanged
  and pass.
- `usecode-compiler/test_uc_sim.py`: the Fire receptacle fixture mirrors
  the new spot.

## Tests (built FIXED.DAT `6f3ac5b6…`, all exit 0)

The 13 acceptance tests:

- test_map_hygiene
- test_map_edges (maps 9 and 11 PASS)
- test_route_reach: LAVA_MARGIN lines pass, and the Fire talisman,
  chamber and exit are reachable
- test_paint_cycles
- test_schedule_destinations
- test_monster_eggs
- test_map_roundtrip (validator 0 WARN)
- test_climb_width
- test_endgame_hatch_box
- test_art_props
- test_crack_geometry
- test_sanctum_clearance
- test_map_pins_fresh

Also run and passing: test_uc_sim, test_uc_reentry, test_uc_vale_return.

The build gives Map 11 9,597 raw items, under the 25,000 limit; validation
reports 0 WARN.

## Open

- **screen07 sits at its floor:** 86.93 against 86.44, and 0.01 under the
  replay class. The 1994 pillar and lava glow (phase C art) are most of
  what is missing.
- The rock south of screen05's lip has invisible faces wherever a
  textured face would paint into the frame. From a lower camera it reads
  as a black chasm between the pocket and the wing floor.
- Not verified in ScummVM. The Fire receptacle should get an in-engine use
  check: talisman → pillar destroyed.

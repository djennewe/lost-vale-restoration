# Phase B — Map 9 (screen10, guardian dais), 2026-10-17

Worktree `lv-wt-map11`, branch `wt/vignettes-map11`.

## Result

| Check | Value |
|---|---|
| Replay class score (vignette_replay) | 86.99% |
| Acceptance floor (replay − 0.5) | 86.49% |
| **Built window** (`vignette_built_window.py screen10`, built FIXED.DAT) | **88.06%** |

Evidence: `screen10_built_window.png` (shot | built | diff),
`screen10_context.png` (3x3 windows, engine order, built shapes, Avatar on
the dais top at (14360,12792,56); render with
`python3 agents/map-populator/src/lv_cave_vignette.py context screen10 out.png 14360,12792,56`).

## What changed

- **New module `lv_cave_vignette.py`** (cave closure for a stamped shot):
  `stamp` (vignette_place.stamp holding back named pins), `Shot.classify`
  (per 32-unit floor cell: floor / prop / rock / black, from an engine-order
  paint of the vignette), `Cave` (ASCII 128-grid mask outside the window;
  window decides inside), `Cave.build` (rebuilds every generated item in the
  mask box; invisible 497/498/846/501 fences, two courses, on the shot's
  walk/rock boundary; textured 26-32 runs on faces the camera sees,
  invisible wall on back faces; nothing generated may paint the window),
  `Cave.dress` (clustered 782/235/237 at wall feet, ~3 per 100 cells),
  `relift` (x+4h, y+4h, z+h draws the same pixels), `Shot.drop`,
  `void_cover` (void_floor with 128 black 35 f10 tiles where a 564 plate
  would lie under a loose SI_DRAW 301 tile — the plate otherwise draws
  over the floor), `window_score`, `context_png`.
  Candidate for promotion into vignette_place.
- **build_map_09.py**: floor glob 45 → 397 (301 cave rock). Zone 1 (the
  throat) replaced by `build_guardian_chamber` + `place_screen10`.
- **Dais-top z resolved: 56** = tomb-kit panels 246/247/249 (40) + 240
  slab (16). Relifted (pixel-identical): the three 240 slabs to z 40, altar
  block 206 + arms 332 + blood 484 + pebble 782 to the top, blood runs
  421/457 onto the faces, steps 107/101/100 to the floor. The dais body
  and stair are invisible: 747 (solid) layers + 797 (LAND) treads; tread
  tops in `STAIR_TOPS` (474 is SEA and 636 is DAMAGING — not usable).
- Three all-black filler items of the shot (735 f0 ×2, 411 f178) are left
  out: the void paints the same black, and map_validate flags a quality
  flat and a container on black floor (88.31 → 88.06%).

## Pin moves

- **Trigger 200 (return to Map 8): (14336,12416) → (13759,12031)**, head of
  the north-west passage the shot shows at its top left. At the old spot
  its hatch box covered the floor behind the dais. Updated:
  `test_route_reach.py` gateway TABLE and Map 9 route target, `map_pins.json`
  (regenerated), `tools/map_viewer/locations.json`. No usecode reads it.

## Tests (all on the rebuilt FIXED.DAT, all green)

test_map_hygiene, test_map_edges, test_route_reach (155/155, incl. new
target "the guardian dais top is reachable up its stair"), test_paint_cycles,
test_schedule_destinations, test_monster_eggs, test_map_roundtrip,
test_climb_width, test_endgame_hatch_box, test_art_props,
test_crack_geometry, test_sanctum_clearance, test_map_pins_fresh.

Test change: `test_map_edges.footprint` now also counts chunks with loose
z-0 LAND ground (not the void markers 564 / 35 f10 / invisible flats):
the guardian chamber's floor is loose 301 tiles, so a glob-only footprint
reported the chamber itself as a leak.

## Open

- The shot's second claw statue and stair front (reconstruction residual)
  are still missing; the window passes without them.
- Zone 2's east wall shows its outer face to the void (pre-existing).

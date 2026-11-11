# Phase E, slice cloud13: screen13's floating cloud (2026-10-30)

Branch `wt/cloud13`, worktree `lv-wt-cloud13`. Builds went into the
worktree's private `shared/build` (`tools/build_artifacts.sh --record`).
The main checkout's build, install and ScummVM trees were not touched.
EUSECODE did not change (`b47c324c…`), so the detection md5 is unchanged.

Douglas's finding (review card 2): in 1994 the white cloud floats above the
scene. It draws over the big tree, over a mushroom the tree partly hides,
and over the spires' feet. Our build laid it as ground-level floor, so the
tree and spires painted over it, and the mushroom was missing.

No new shape ids. 886's frames changed, and screen13's vignette, Map 13's
builder and `lv_map13_tiers.vignette_layer` changed.

## What the shot says the cloud is

- **The props stand below the cloud.** The upper patch's lobes cover the
  tree crown. 74 f0 sits at local z 40 and is 40 tall, so its top is at
  local 80. The lower patch covers the tree's foot, the second mushroom's
  top and the spires' feet. `SortItem::below` (`sort_item.cpp:70-80`) sets
  a flat and a solid in order by z before anything else. So for the
  patches to draw over the crown everywhere they meet it on screen, they
  must lie at or above the crown's top.
- **The Avatar stands on the cloud.** His legs draw over the lower patch:
  at x 150 of the 6× crop, the patch's rim runs at y 258 and his legs fill
  y 260-345. An Avatar on the earth would sit under a cloud at local 80 or
  higher, and that cloud would draw over his legs. So his feet are at the
  cloud's level, and the props' ground is below it.
- **screen01** shows only the cloud sea at z 56/57, which nothing pierces.
  It decides nothing here, and its window is unchanged.

**Decision.** The cloud patches and the gold corner float 96 over the earth
(local 97, world 216). The Avatar of the shot stands on them. Each item was
slid 12 view-ray steps of (8, 8, 2), which is (+384, +384, +96), so every
pixel is unchanged:
- 96 clears the crown by 16 and keeps the 128 lattice.
- The earth island and its props stay where phase B put them, at the
  summit's level (120), still joined to the climb's turn.
- I did not lower the earth by 96 under a cloud left at 120, which is the
  other way to get the same pixels. That slides the earth 384 north-west,
  where it lands under nine of the climb's cells: the turn, the stub and
  the north leg's top, (38-40, 10-13). The lane's rock would then stand
  inside the shot's earth.

**The missing pieces, found with retail art:**
- **The mushroom behind the tree** is retail 65 f0, at screen (48,109),
  matching 290 px exactly. It sits at local (2687, 2719, 0). The tree draws
  over its left side and the cloud over its top, as in 1994.
- **The grey shape at the top edge** was a phase-D residual. It is retail
  66 f7, matching 171 of 174 px, at local (2367, 2175, 0). It is a spire
  whose foot the upper patch hides.

## Build changes

- **`vignettes/screen13.json`**
  - The 35 floor tiles (2015), the gold (2004 ×2, 2008) and the Avatar are
    at +384, +384, +96.
  - Two items added: 65:0 and 66:7.
  - Notes, residuals, `world_bbox` and verify updated (`--publish
    --write-verify`).
- **`build_map_13.FLOATING`** = `{'screen13': {2015, 2004, 2008}}`.
  - `lv_map13_tiers.vignette_layer(…, floating=)` lays those items but
    gives them no region cell and no top.
  - `shot_region()` gives the same region for `city_edge_cells` and the
    shot-floor map.
  - The island's field, halo, fit and faces are those of the earth alone,
    so nothing generated around it changed. Four region cells that only
    floating tiles touched now take the halo's earth: (49,19), (50,18),
    (52,14) and (52,16).
- **The Avatar under the cloud** (`build_map_13`, "UNDER THE FLOATING
  CLOUD"). The floating layer draws over an Avatar walking the island
  below it, because the z test comes first. It carries no `SI_ROOF`, so
  `CameraProcess::findRoof` never cuts it away either.
  - **Rule:** `under_floating()` closes a cell if, with his reference point
    anywhere in it on a 16-unit grid, his box outline meets an opaque
    floating pixel. The outline is the 64×64×40 box projected, plus 2 px;
    it contains every standing and walking frame of shape 1 (checked on
    frames 0-15).
  - **Walls:** closed cells get the curbs a drop gets (retail 497/498,
    invisible).
  - **Callers:** `walk_cells(closed=)`, `build_curbs`, `city_edge_cells`.
  - **Result:** 73 of the island's 134 walked cells are closed. 59 stay
    open: the west strip along the climb's turn and the north rim
    (`map13_island_walk.png`: green open, red closed). Wherever he can
    walk, the cloud never covers him. The cells beyond the closed ones
    (the south-east rim) are out of reach.
  - **Cost:** 1.35 s per build, reading the built U8SHAPES as
    `build_map_17` does.
- **886's frames** (registry 2015; PNGs in
  `shared/data/lv-1994-art/ReconCloud/screen13_floor/`):
  - Shot pixels the tree crown and the spires used to cover now belong to
    the nearest tile, copied index for index: f3 166 px, f12 61, f17 92,
    f16 6.
  - Where a branch tip or spire edge shows past a rim (49 px across f5,
    11, 15, 21, 26, 27 and 32), the tile pixel is transparent.
  - f3's new block reached the window's right edge, so its north-east cap
    beyond the edge is drawn. That is 180 px of the tile's own texture,
    mirrored about x 281 and lobed, recorded as `inferred_px`.
  - The registry's hotspot, size, `opaque_px`, `match`, `xy` and notes are
    updated for the 11 frames.
  - The cloud's own indices are 1-3 and 11, as in every 2000/2015 frame
    since phase C. U8 never runs `CycleProcess` (`ultima8.cpp:1406-1411`
    starts it for Crusader only), so these indices are static colours
    here.

## Scores

| | before | after |
|---|---|---|
| screen13 built window `--actors` (class) | 95.88 | **98.91** |
| screen13 replay `--built` (class / strict) | 95.915 / 95.154 | **98.944 / 98.173** |
| screen13 in-engine (class / rgb) | 93.99 / 93.46 | **97.02 / 96.49** |
| screen01 built / in-engine | 95.35 / 91.98 | 95.35 / 91.99 |
| screen14 built / in-engine | 89.82 / 85.91, 83.92 | 89.82 / 83.92, 83.92 |
| screen15 built / in-engine | 95.99 / 94.34 | 95.99 / 94.32 |
| screen16 built / in-engine | 94.60 / 92.23 | 94.60 / 92.24 |

**screen14 in-engine** varies from run to run on main's own build. Two
captures of it gave 85.91 and 83.92, and a dynamic figure at the frame's
top centre accounts for the difference. My build gives 83.92 twice. The
built window and the non-terrain map items within 1,500 of the spot are
identical.

`test_vignettes` floor: screen13 95.88 → 98.91.

**What is left (1.06%):**
- the Avatar's pose (1:197 is the nearest retail frame);
- a few rim-shading pixels where the crown's twigs and the cloud cross.

**In-engine method:**
- **Pinned copy:** `/tmp/claude-1000/cloud13/game`, copied from main's
  `shared/u8-lv-patched`.
- **Before:** main's artifacts and vignettes.
- **After:** this branch's artifacts, synced by the session.
- **Binary and display:** `scummvm-lv-console/scummvm` on display :96,
  with a private `XDG_RUNTIME_DIR`.
- **Harness:** private copies of `session.sh` and `vignette_capture.py`,
  with the `stop` pkill narrowed to this session's own `commands.txt`.
- The screen13 capture teleports to the new Avatar spot,
  (6747, 2331, 216), on the floating cloud.
- The session was stopped afterwards.

**Images (beside this file):**
- `screen13_ingame_before.png` and `screen13_ingame_after.png`: shot |
  in-engine | misses, ×3;
- `screen13_built_before.png` and `screen13_built_after.png`;
- `map13_island_walk.png`;
- the contact sheet `phaseE-cloud13-contact.png`. Its rows:
  1. 1994 | in-engine before | after;
  2. 1994 | built window before | after;
  3. the tree close-up;
  4. the edited 886 frames, before | after, with f3's drawn cap in blue;
  5. the island's open and closed cells.

## Artifacts

- `U8SHAPES.FLX` `b209d6d9…`
- `FIXED.DAT` `31d339d7…`
- `TYPEFLAG`, `ANIM` and `EUSECODE` unchanged.
- `ARTIFACTS.sha256` was recorded and `map_pins.json` regenerated.

## Tests

`tools/run_all_tests.sh` in the worktree:
- First run: 53 of 54 passed. All of these passed:
  - `test_route_reach` 166/166;
  - `test_map_edges`;
  - `test_monster_eggs` 459/459;
  - `test_harpie_corpses` 3/3;
  - `test_paint_cycles` 76/76, including §5-8 on Map 13, whose island
    frames are now the 59 open cells;
  - `test_vignettes` 39/39;
  - `test_art_props` 464/464.
- The only failure was `test_map_pins_fresh` (hash prefix), fixed by
  regenerating `map_pins.json`.
- The final state was run once more after the commit (see the commit
  message / final report).

## For Douglas

1. **The island under the cloud is walled off** where the cloud would hide
   the Avatar (73 cells), not left open with him vanishing under it.
   - If you would rather it be open, delete the `under_floating` call in
     `build_curbs` and `city_edge_cells`.
   - If you would rather the whole island be scenery, add a curb across
     the turn's east lane.
2. **Art sign-off:**
   - f3's drawn north-east cap (180 px, never in a window);
   - the crown and spire-foot pixels now owned by f3/f12/f16/f17;
   - the 49 rim pixels opened for branch tips.

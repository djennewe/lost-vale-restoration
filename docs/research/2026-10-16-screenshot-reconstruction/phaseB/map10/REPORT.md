# Phase B — Map 10, status 2026-10-17 (BMap10c): all tests green, not yet verified in ScummVM

All of this work is in the main checkout and is uncommitted. BMap10 and
BMap10b got all eight windows to target. BMap10c (this session) closed
the failing tests, made the context renders, and fixed the seams and
voids those renders showed. Nothing has been run in the engine. The
`verifier` pass is still to do.

## Scores

FIXED.DAT is `a6bc69c441b2956d…`, and map_pins.json was regenerated
against it. Map 10 holds 20,559 raw items. The scores come from
`vignette_built_window.py --actors` and are palette-class figures for the
whole frame. Each shot's target is its replay class score minus 0.5.

| Shot | Built + actors | Target | Margin |
|---|---:|---:|---:|
| 18 | 98.58 | 97.90 | +0.68 |
| 02 | 95.96 | 95.54 | +0.42 |
| 09 | 93.75 | 93.18 | +0.57 |
| 17 | 93.69 | 92.27 | +1.42 |
| 19 | 95.85 | 95.57 | +0.28 |
| 20 | 95.69 | 94.94 | +0.75 |
| 21 | 93.53 | 92.79 | +0.74 |
| 22 | 97.26 | 96.20 | +1.06 |

The images in this folder:
- `screenNN_built_diff.png`: three panels, the shot, the built window and
  the mismatches in red.
- `screenNN_context.png`: 3×3 windows round each shot, engine-order
  painter (`vignette_paint.Painter`), at 2×. The yellow box is the shot's
  frame, and magenta marks pixels nothing paints.
- `map_10.png`: the whole-map preview (`map_preview.py 10 --scale 1`).
  That tool draws invisible walls as blue boxes.

## Tests (final build, all run on it)

| Test | Result |
|---|---|
| test_map_hygiene | OK 60/0 |
| test_map_edges | PASS |
| test_route_reach | OK 156/0 |
| test_paint_cycles | OK 40/0 |
| test_schedule_destinations | OK 200/0 |
| test_monster_eggs | OK 421/0 |
| test_map_roundtrip | OK 14/14 |
| test_climb_width | OK 28/0 |
| test_endgame_hatch_box | OK 20/0 |
| test_art_props | 203/0 |
| test_chest_locks | 3/0 |
| test_crack_geometry | OK 10/0 |
| test_sanctum_clearance | OK 22/0 |
| test_map_pins_fresh | OK 3/0 |

## Pin moves (each recorded in its vignette's `placement.pin_moves`)

| Pin | From | To | Recorded in |
|---|---|---|---|
| Pad 210 + EGGENDGAME + EGGREAPPLY | (18432,22784,0) | **(18432,22719,112)** | screen17 |
| Hrodny's chest | (21024,8832) | **(21216,8768)** | screen20 |
| Zombie wave 2 egg | (13888,19008,8) | (13344,19008,8) | screen02 |
| Wave 3 MONEGG trigger | (13824,18816,8) | (13312,18816,8) | screen02 |
| Atli's map start | (19232,6944,0) | (19231,6943,0) | screen19 |
| **Wilderness kith egg, group 3 (new)** | (10944,17312,0) | **(10463,17312,0)** | screen09 |

**Pad 210, 22720 → 22719.** The shot's top stair block, 107:1 at
(18431,22751,72), spans y 22720..22751 up to z 120. A body at 22720 met
it by one unit. At 22719 the pad rests on the shelf crest.

**Hrodny's chest.** At (21120,8832) it stood flush against the hut's west
wall on the inside, so there was no walk along its west face. In its new
spot:
- 96 units of open floor lie west of it.
- Its south face is 32 north of the two potions.
- It is 287 north of the south wall.
- The route goal in `test_route_reach` moved with it, to (21104,8768).

**Kith egg 76.** Screen09's tarn shelf (z 64, down to y 17151) did two
things to it:
- its face met the kith's 192×192 body;
- the shelf stood between the egg and its trigger (10144,16512).

Its new spot:
- It sits at the shelf's west foot.
- It is 32 clear of the face and of the scrub prop 524.
- The walk to the trigger is straight.
- y is kept, so the seek square still covers the whole trigger box.

## What changed this session

**Item 1: test_monster_eggs (8 failures).**
- **The lake rails inside screen02.** The rails in the shots' own water
  cells (`f.vwater`) were laid before the stamp, and the stamp cleared
  them. That left screen02's north shore and its old pier mouth open onto
  the water at z 0.
  - `lv_map10_ground.rails(f, shots=True)` now lays those rails after the
    stamp.
- **Egg 76** moved (see the table above).

**Item 2: test_route_reach (4 failures).**
- **Pad 210** moved one unit (see above).
- **Hrodny's chest** and its route goal moved (see above).
- **`exact_reach.HURT_SHAPES_U8`** gained 216 and 438. Both are
  SI_DAMAGING in retail TYPEFLAG (0x41 and 0x47).
  - 216 LIGHT: its gotHit gives an overlapping Avatar a 255 receiveHit
    through METHOD 057C:0080 (216:01C7), and destroys any other hitter.
  - 438 WATER4: its gotHit is CLRWATER's spawn of WATER 056E:0080, which
    drowns whoever `isOn` it. The foam is 8 deep, so its top is at bank
    height and a body beside it counts as on it.
  - The comment block cites both. The route floods now keep clear of
    both shapes.

**Item 4: seams, void and islands from the context renders.** All of
these are general fixes, map-wide:
- **Cliff feet** (`lv_vale_terrain.foot`, `_faces`, `seam_faces`).
  - On tiers of 64, 112 and 160 over the 0 floor, the 48 courses stopped
    at z 8. Nothing painted the band from z 0 to 8.
  - This happened at the foot of every such cliff on the map.
  - A crest plate now fills that band.
  - The fix follows retail, which stands z 8 faces on a z 8 floor.
- **Shot scarps cut off by the frame** (`Field._seams`).
  - `f.faced` is now a dict of the lowest face z on each side.
  - Seams now add the courses under a shot's lowest face. This fixed the
    large hole under screen18's mesa scarp.
- **Shore banks** (`Field._top`, `visible_role`).
  - A shore cell takes an 8-deep crest whenever any neighbour is lower,
    or is the shot's water.
  - The crest frame is picked so it draws the visible S and E sides.
    Retail's 'NS' frame draws neither of them.
- **Hidden lake cells.** A shot cell with no floor that was lake water
  now stays water. Screen09 had left dirt tiles standing in the lake.
- **Island fringe.** Single shore cells with no land beside them now
  become water (ISLAND jag round screen02).
- **One-cell jag notches** in RELIEF edges are filled in (`relief_cells`;
  example: screen17's east arm).
- **`stair_underfill`.** Step blocks now fill under screen17's floating
  1994 step blocks, which had left a hole through the stair's side
  outside the frame.
- **Knoll stair head.** A crest plate under the tier's edge cells draws
  the top step's 8 riser (`stair_items`, for stairs that descend south).
- **`under_floors`.** A tile that paints under ¾ of its cell gets a floor
  at its own z. These are screen21's 781:0 and 466:1 (`_holed`).
- **`band_plates`.** It adds a crest plate under any floor a course above
  the floor south or east of it where no art draws the step.
  - Whether a side is drawn is measured on the painter (`_draws`).
  - It never puts a plate whose sprite reaches into a shot's frame
    (`shot_frames`).
  - The first version did reach into the frames. It cost screens 02 and
    18 about 1 point each.

Unpainted pixels in the context renders, before → after:

| Screen | Before | After |
|---|---:|---:|
| 18 | 7,306 | 1,395 |
| 09 | 4,455 | 781 |
| 17 | 5,908 | 302 |
| 21 | 7,654 | 1,078 |
| 02 | 1,907 | 687 |
| 19 | 128 | 0 |
| 20 | 25 | 25 |
| 22 | 0 | 0 |

**Item 5: docs.**
- `build_map_10.py` module docstring (the phase B ground).
- `agents/map-populator/docs/map-10-lost-vale.md`: new section "Phase B
  ground".
- `docs/art-track.md`: the "126s" row now names screen21's 126:13.

## Test edits (all sessions)

- `test_route_reach`:
  - the pad 210 coordinates (now 22719);
  - the Hrodny's chest route goal, to (21104,8768).
- `test_map_hygiene`: the roof tests skip the shots' own pieces.
- `test_art_props`: a 126 is allowed only where a shot places one.
- `test_schedule_destinations`: the `doorway()` relaxation (BMap10b).

No check was weakened this session. `HURT_SHAPES_U8` grew, which makes
the hazard checks stricter.

## Changed files (whole phase B, uncommitted)

- **`agents/map-populator/src/`:**
  - `build_map_10.py`
  - `lv_map10_ground.py` (new)
  - `lv_vale_terrain.py` (new)
  - `lv_hut1994.py` (new)
  - `exact_reach.py`
  - `vignette_built_window.py`
  - `map_pins.json`
  - the tests named above
- **Vignette `placement` blocks only:** `screen02.json`, `screen09.json`,
  `screen17.json`, `screen19.json`, `screen20.json`.
- **Docs:**
  - `agents/map-populator/docs/map-10-lost-vale.md`
  - `docs/art-track.md`
  - this folder

## Open issues

1. **Not run in ScummVM.** Nothing here has been run in the engine yet.
   Still to check:
   - Pad 210 arrival at y 22719.
   - The chest's clickability inside the hut.
   - Atli's loiter.
   - The foot plates' look in the engine.
2. **Remaining unpainted spots in the context renders.** All of them are
   the shots' own items at their region edges, which phase B may not
   edit:
   - Screen21's lava edge and 781 crater, inside the frame. They are
     identical in the replay.
   - Screen09's foam tiles past its east edge. The foam is 0..8 and
     draws no side.
   - Screen02's 301:0 tile at z 0 at (13695,18303), and its 125:13 crest
     at (14719,18815), whose frame draws no south side.
   - Screen17's balustrade over air east of its stair.
   - Screen18's 32-wide gap in the shot's 27 run at x 10336..10367.
3. **Black void plates still show in two long diagonal strips** where 564
   paving (256×256) meets the field ground:
   - Screen18, cells (74..77,150..153).
   - Screen17's processional, (144..147,168..171).

   They were not investigated, for lack of budget.
4. **Not done:** the 1994 crop gardens for Hoskuld, and the jagged rim.
5. **Margins.** Screen19 (+0.28) and screen02 (+0.42) have the thinnest
   margins. Re-score after any change near them.

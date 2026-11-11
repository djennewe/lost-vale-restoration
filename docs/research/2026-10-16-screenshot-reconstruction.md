# Rebuilding the 1994 screenshots exactly (2026-10-16)

**New rule (Douglas, 2026-10-16).** Our build must recreate each published 1994
Lost Vale screenshot exactly. Those shots are the only areas whose look we
actually know, so we match them and extrapolate everything else around them.

This doc covers the reconstruction phase. Each of the 19 shots is now an item
list in world coordinates (a **vignette**). Re-rendered in the engine's own
draw order, the vignettes reproduce their shots at 74-99.9% palette-class
agreement with every frame pixel counted (§2). 13 of the 19 score 92% or
higher. No builder, artifact or pin has been changed yet.
Placing the vignettes into the maps is the next phase (§5); it needs the
decisions in §4 and the fixes in §6.

**Reviewed 2026-10-16.** Two independent reviews were run:
- Astra reviewed the reconstruction: `2026-10-16-screenshot-reconstruction/astra-review.md`.
- Fable 5.1 reviewed Astra's review, re-measuring every number:
  `fable-5.1-meta-review.md`.

This doc carries Fable's corrected wording. §6 lists what must change before
integration.

## 1. How it was done

1. **The shots are native game pixels.** A 1994 screenshot is a crop of the
   320×200 screen at 1:1 scale. The crops are 271-320 wide and 180-186 high.
   Every GIF colour lies within 8 RGB of
   a U8PAL entry. So each pixel maps back to a palette entry, and every sprite
   on screen is a U8 frame placed at an integer offset.
2. **`agents/map-populator/src/shot_decompose.py`** is new. It template-matches
   all ~18,900 frames of the 860 retail shapes against a shot, then
   greedy-explains the image. The first pass explains 85-95% of the pixels in
   16 shots. The cloud shots score lower because their art is from 1994:
   screen11 46%, screen12 25%, screen13 65%.
3. **Five reconstruction passes** (cloud, cliffs, village, vale, interiors)
   then cleaned each decomposition:
   - dropped spurious hits;
   - filled ground hidden behind objects from the 128-unit lattice;
   - solved world (x, y, z) from the projection plus what each object rests on;
   - recorded actors (the Avatar, NPCs, monsters) separately;
   - cut every piece of 1994-only art from the shots as a residual mask.
     Three cloud frames and the banded column are confirmed by independent
     instances in other shots. Cloud f3/f4 turned out to be f0/f2 mirrored,
     and are now complete. Felicitar has 42 inferred pixels and the walkway
     19. The fire pillar and the screen19 elder crops are reference crops,
     with clean re-cuts beside them. The Water Zombies, the wall spikes, foam,
     halo and beam are drafts or residuals, not sprites. Grades per asset are
     in `vignettes/art_registry.json` (D-track).
4. **Verification.** Each pass re-rendered its vignette with
   `agents/map-populator/src/vignette_paint.py`, which applies the engine's
   own draw order (`item_sorter.py`, a port of ScummVM's ItemSorter). That
   render was then diffed against the shot.

## 2. Results

Vignettes are in `agents/map-populator/src/vignettes/screenNN.json`. The 1994
art is in `shared/data/lv-1994-art/<pass>/`, registered with a grade in
`vignettes/art_registry.json`. Evidence and the pass reports are in
`2026-10-16-screenshot-reconstruction/` (`screenNN_render.png`,
`screenNN_diff.png`, `Recon*-REPORT.md`, `D-track.md`).

One command replays every vignette and prints these numbers:
`python3 agents/map-populator/src/vignette_replay.py`. It paints in world
coordinates (origin + local) in the engine's draw order. All 19 published
renders are pixel-identical to it; `D-track.md` lists the seven that were
re-published and why. Every column below counts the whole frame:
- **Strict / Class.** A pixel counts if it is painted and exactly the shot's
  palette RGB (strict) or in its palette class (class). Unpainted pixels
  count as misses. Class is the headline figure.
- **+void.** The points that counting unpainted void as the engine's black
  would add. This is large only in the caves (05, 07, 10).
- **+actors.** The points that excluding the unrendered 1994 actors' sprite
  pixels would add (02, 09, 19, 20).
- **Provenance.** Matched pixels split as retail / cross-shot-validated 1994 /
  single-shot 1994 / inferred / unmatched.
  - screen11's 1994 share is now mostly validated: the sun shield half
    re-appears in the screen04 altar shield, and cloud f3/f4 are mirrored
    f0/f2.
  - Its single-shot 10.3 points are the plain column's paint.
- **Tolerance.** screen10 drops from 87.0 to 75.9% under strict RGB
  matching. It is the only shot where the palette-class tolerance does real
  work.

| Shot | Map, area | Strict | Class | +void | +actors | Provenance | Items | 1994-only art |
|---|---|---:|---:|---:|---:|---|---:|---|
| 01 | 13 summit edge over the cloud | 94.0 | **94.1** | 0.0 | 0.0 | 87.6 / 6.5 / 0.0 / 0.0 / 5.91 | 85 | cloud floor (also in 11) |
| 02 | 10 lake shore | 95.7 | **96.0** | 0.0 | 2.4 | 96.0 / 0.0 / 0.0 / 0.0 / 3.96 | 90 | Water Zombie ×2 poses (unrendered) |
| 04 | 18 sanctum | 99.9 | **99.9** | 0.0 | 0.0 | 91.3 / 1.0 / 7.6 / 0.0 / 0.09 | 106 | 3 gods in amber; altar shield = sun half + eye half |
| 05 | 11 fire wing | 82.9 | **83.3** | 12.2 | 0.0 | 83.3 / 0.0 / 0.0 / 0.0 / 16.70 | 124 | none |
| 07 | 11 Pillar of Fire | 86.9 | **86.9** | 8.3 | 0.0 | 80.3 / 0.0 / 6.6 / 0.0 / 13.06 | 136 | fire pillar (reference crop), lava glow, wall spikes (spike 0 is retail 26:5) |
| 09 | 10 lake waterfall | 93.7 | **93.7** | 0.0 | 1.0 | 93.7 / 0.0 / 0.0 / 0.0 / 6.32 | 82 | Water Zombie pose (unrendered); the waterfall is retail 439 + foam 435-438 |
| 10 | 9 guardian dais | 75.9 | **87.0** | 4.9 | 0.0 | 87.0 / 0.0 / 0.0 / 0.0 / 13.02 | 111 | none; dais-top z unresolved |
| 11 | 17 obelisk plaza | 99.9 | **99.9** | 0.0 | 0.0 | 7.3 / 82.4 / 10.3 / 0.0 / 0.06 | 114 | cloud floor ×5 frames (f3/f4 = mirrored f0/f2), plain and banded white columns, shield half (sun) |
| 12 | 17 walkway and throne nook | 82.5 | **82.8** | 0.0 | 0.0 | 8.6 / 37.0 / 37.1 / 0.0 / 17.18 | 157 | walkway slab, gold brick ×2, shield half (eye, draft, not placed) |
| 13 | 13 summit / city edge | 75.0 | **76.0** | 0.0 | 0.0 | 44.3 / 28.4 / 3.3 / 0.0 / 24.03 | 125 | cloud rim lobes (not recovered); gold brick ×4, the street corner (added 2026-10-17, phase B Map 13 pass d) |
| 14 | 13 skull ring | 89.3 | **89.4** | 0.2 | 0.0 | 89.4 / 0.0 / 0.0 / 0.0 / 10.56 | 70 | small scraps |
| 15 | 13 lake stepping stones | 95.7 | **95.9** | 0.1 | 0.0 | 95.9 / 0.0 / 0.0 / 0.0 / 4.07 | 67 | small scraps |
| 16 | 13 lake landing | 94.3 | **94.3** | 0.0 | 0.0 | 94.3 / 0.0 / 0.0 / 0.0 / 5.73 | 67 | bone scatter |
| 17 | 10 sunken temple stair | 92.7 | **92.8** | 0.0 | 0.0 | 92.8 / 0.0 / 0.0 / 0.0 / 7.23 | 112 | none |
| 18 | 10 mushroom-garden scarp | 98.1 | **98.4** | 0.0 | 0.0 | 98.4 / 0.0 / 0.0 / 0.0 / 1.60 | 88 | none |
| 19 | 10 Gunnar hut (Atli's) | 95.8 | **96.1** | 0.0 | 1.2 | 96.1 / 0.0 / 0.0 / 0.0 / 3.93 | 119 | Zealan elder (unrendered) |
| 20 | 10 Gunnar commons, campfire | 94.7 | **95.4** | 0.0 | 2.0 | 95.4 / 0.0 / 0.0 / 0.0 / 4.57 | 97 | elder with staff, two spear children (unrendered) |
| 21 | 10 lava field, skull-post pen | 92.9 | **93.3** | 0.0 | 0.0 | 93.3 / 0.0 / 0.0 / 0.0 / 6.71 | 84 | skull beam (residual) |
| 22 | 10 Gunnar crop garden | 95.8 | **96.7** | 0.0 | 0.0 | 96.7 / 0.0 / 0.0 / 0.0 / 3.30 | 129 | blue root plants ×2 (not placed) |

screen22's earlier 96.6% was its pass's own coordinate frame; its items are
unchanged.

Most of the remaining misses fall into five groups: actors drawn in 1994-only
art, the mouse cursor, animation phase (the waterfall foam), draw-order ties,
and parts the shot shows only at its frame edge.

![screen11 shot / vignette / diff](2026-10-16-screenshot-reconstruction/screen11_diff.png)
![screen04 shot / vignette / diff](2026-10-16-screenshot-reconstruction/screen04_diff.png)
![screen22 shot / vignette / diff](2026-10-16-screenshot-reconstruction/screen22_diff.png)

## 3. What the shots show that we got wrong

- **The 1994 maps are almost entirely retail art.** Our custom art does not
  match the 1994 pieces it stands in for:
  - **Cloud floor.** Three complete 62×32 frames (f0-f2), on the same mask
    and hotspot as retail 301, one frame per 128 cell. The two "partial"
    frames f3/f4 are f0 and f2 mirrored (FLG_FLIPPED placements), so they
    are now complete too. All five are confirmed by independent tiles in
    screen01, 12 and 13. Our 862 is a different drawing, and its 8-unit
    height buries z=0 items.
  - **Obelisk.** It is entirely retail: shape 12 frames 14-17, cap 545 and
    skull 814, standing on four banded 1994 white columns. Our 861 is
    redundant.
  - **Gods in amber.** The recovered gods are 33×53, 43×38 and 31×67 px,
    against our 860 frames of 36×124, 96×71 and 54×124. They stand on
    retail plinths 37:10/13.
  - **Fire pillar.** It is a dark banded column with a red cap, not our 865
    frame 2 flame. The crop also carries pit and wall pixels, so it is a
    reference for redrawing, not a sprite.
  - **Shield halves.** The screen11 half (sun emblem) is complete; the
    screen12 half is only a draft.
  - **Zealan villagers** (an elder and two spear-carrying children) are
    1994-only sprites. Ours use retail 707 and 708.
- **The architecture is retail, and the 2-D composition reproduces the
  shots.** Heights, hidden faces and z choices finer than 32 units are solved,
  not observed, where noted.
  - **Huts** are retail planks and posts (145-150, 194) under a 412 hip roof
    at z=40, with 410/118 eaves; `hut_spec.json` in the village report lists
    every piece.
  - The **screen19 "blue pots" are crop row 649 frame 2.**
  - The **temple stair** is built from retail step blocks
    98/99/100/107/112, not 70 cobble.
  - The **pen** is the skull-post kit 148/153/156/157/162.
  - The **Cloud City columns** are one 16×47 white column. With retail gem
    596 on top it is a gem pillar; with orange bands it is an obelisk drum
    or a walkway post.
- **The 1994 cliff climb is a staircase of 56-unit ledges:** one 48-unit
  course plus an 8-unit crest, which is the engine's jump-climb. The screen01
  Avatar is in the climb pose (1:244).
- **The sanctum has no dais.** The altar stands on the floor, the shield is
  already on it, and all three gods fit in one frame.

## 4. Decisions needed before integration

1. **Replace our custom art with the 1994 pixels wherever a shot shows the
   real thing.** That means: retire 861 (Douglas's pick from the art track)
   for the retail composite; replace 862 with the 1994 cloud frames; replace
   860 frames 0-2 (shatter frames 3-41 would need redrawing at the 1994
   scale); replace 865 frame 2 and 870 frames 0/1; and add the 1994 Water
   Zombie poses to 872. Under the new rule this is required. Only cloud f0-f2,
   the banded column, gold brick f0 and the sun shield half are ready now;
   the rest are references for redrawing.
   - **One wrinkle: actors.** A shot shows one or two poses. The rest of each
     animation has to be drawn to match them.
2. **Pin moves implied by the chosen origins.** The shots fix relative
   layout, not absolute coordinates.
   - **Forced by the pixels, within each window:** the god spacing, an altar
     with no dais, the shield halves and skeletons beside the obelisk and in
     the nook, the stair steps and shelf, the shore at z=8, the tier heights
     relative to each window, and 866 kept out of the screen07 window.
   - **Our choices:** every origin, the Map 13 lane at x=4864, the candle
     post as receptacle (moving 866 out of frame would be enough), Hrodny's
     chest (it depends on a hidden wall), and the cloud z-encoding.
   - Every move is listed in its vignette's `placement.pin_moves`.

   | Map | What moves |
   |---|---|
   | 18 | Gods to (2783,8031,16), (3039,7903,16) and (3039,8415,16). Altar to z=0 and EggAOCeremony to z=0. Skull 331 out of frame. South wall from y 8703 to y 9215 or beyond. AOSCENE `shield.pop` and camera coordinates follow, which is a usecode change and an EUSECODE rehash. |
   | 13 | The climb is rerouted through the four cliff views: a new lane at x=4864, and the old summit north of y 767 becomes cloud at z=57. Pad 208 to (4351,1279,120), trigger 209 to (4351,895,120), harpie groups 1 and 2 and their triggers. `CLIMB_WAYPOINTS` is rewritten. |
   | 17 | Shield half 1 next to the obelisk, half 2 in the throne nook, skeletons next to the obelisk. The plaza dais and the god-hall daises are removed. |
   | 10 | Pad 210 with EGGENDGAME and EGGREAPPLY to (18432,22720,**112**), on the temple-stair shelf. Hrodny's chest moves +96 x. The lake gains shore cells inside the monster-test rectangle. |
   | 11 | Fire receptacle 866 replaced by the 1994 candle post 453:6 beside the pillar (npcnum 120 dispatch works for any shape). Optionally, the daemon egg moves 40 units. |
3. **Map 17's layout.** screen11 and screen12 fix the plaza and the throne
   nook. Where they sit relative to each other (and to MAGNET's 1994 target
   (15615,19839)) is still our extrapolation.

## 5. Integration plan

1. **Art.**
   - Feed the 1994 frames from `shared/data/lv-1994-art/` into the art-track
     builders (`lv_art_props.py`, `lv_monsters.py`): cloud 862, columns 874+,
     walkway, gold brick, gods 860, fire pillar 865, shield 870, villager
     sprites.
   - IDs follow `.claude/rules/build-artifacts.md`, so nothing is renumbered.
2. **Builders.** Each map builder places its vignettes verbatim at their
   origins.
   - Generated terrain is suppressed inside each vignette's footprint and
     blended at its border.
   - Pins move as listed in §4.2.
   - The rest of the map is extrapolated in the same style: the organic-maps
     plan, 2026-10-12.
3. **A permanent regression test**, `test_vignettes.py`.
   - It loads the built FIXED.DAT window, plus every item whose projected
     rectangle enters the frame, and injects the actors from the JSON.
   - It paints the result with a `vignette_paint` that reads the built
     artifacts. Today the painter is hard-wired to the retail `.bak` files.
   - It asserts per-region goldens (floor, props, actors). The global figure
     is diagnostic only, so the unresolved 17-26% on 12/13 is never locked in
     as acceptable.
4. **Final proof is in-engine.** The 1994 camera was not centred on the
   Avatar: he is at (36,125) in screen11 and (214,170) in screen04. So the
   `/playtest` fixture:
   - scripts the camera to the vignette's camera position;
   - places the Avatar at the vignette's actor position and frame;
   - hides the cursor and pins the animation tick;
   - crops to each GIF's own size;
   - diffs the result against the 1994 GIF.

   "Exact" applies to that fixture view; a player walking there sees the same
   scene from a different camera.
5. **Open reconstruction work:**
   - screen12: cloud lobes over gold, the left throne, the nook rim.
   - screen13: cloud rim lobes.
   - screen10: z of the items on the dais top.
   - screen14: the outline of the path's back edge.

## 6. Fixes before integration (Fable 5.1, ordered)

Each fix has its own acceptance check in `fable-5.1-meta-review.md`.

**Status 2026-10-16 (`D-track.md`).** Done:
- items 1-7;
- the painter half of 10 (`Painter.built()`);
- the art-directory and `png2shape.py` check of 11.

The png2shape check found more traps than index 255: the chroma key, trim
and duplicate palette entries; one teal shot pixel was already lost.

Still open: 8, 9, the neighbour check of 10, and the TYPEFLAG half of 11.

**Blockers:**
1. Do not feed `s07_fire_pillar.png` or `art_s19_elder_draft.png` to any
   builder.
2. Mark cloud f3/f4 as partial. `screen11.json` wrongly says they were
   "completed from screen13".
3. Regenerate `screen22.json`, or re-publish its number as 95.4%.

**Then:**

4. One replay manifest. Today it has 2 camera signs, 2 footprint units,
   4 shape-reference conventions, `/tmp` paths and 17 unresolved art paths.
   The fix is a single `art_registry.json`, so that one `replay.py`
   reproduces every published render byte for byte.
5. A uniform score contract per shot: strict, class, void points,
   excluded-actor points, and the provenance split.
6. Cross-shot validation as the acceptance test for every 1994 asset.
7. Clean masks:
   - Fill the Water Zombie holes (27, 21 and 48 pixels) and drop the strays.
   - Complete f3/f4 from screen13.
   - Re-cut the elder and the pillar.
8. Decide the cloud z-encoding. Under the current z=1/z=2 scheme the Avatar
   settles 1 px lower in-engine.
9. Tag each pin move `forced_by: shot | origin | design`.
10. Make the painter read the built artifacts, with a projected-rectangle
    neighbour check.
11. Fix the art directory: 18 of the 65 PNGs are previews, not P-mode
    assets. Palette index 255 is a real teal used here as transparency;
    check `png2shape.py` against that trap. Ship TYPEFLAG changes with the
    art (862 to zd 0; 860 to per-frame footprints).

## 7. Phase A: screen18 end to end (2026-10-16)

**Result.** The pipeline holds up in the real engine. The shot's window
scores the same in ScummVM as in the offline renderer.

**What changed:**
- `vignette_place.stamp(items, shot, map)` is new. It expands every glob
  egg in the chunks the vignette touches into loose tiles, removes every
  generated item whose box meets the vignette's 128-unit cells, adds the
  vignette at its origin, and fills the floor of cells the shot never shows.
  Pinned items are never removed silently. Eggs are always kept.
- `build_map_10.py` stamps `VIGNETTES = ('screen18',)` after
  `build_wilderness()`.
- `vignette_built_window.py` paints a shot's window from the built
  FIXED.DAT.

**Scores** (all-frame, palette RGB within 12):

| Check | Match |
|---|---|
| Reconstruction (vignette JSON, offline) | 97.1% |
| Built FIXED.DAT window, offline engine-order paint | **97.15%** |
| **In ScummVM**, Avatar teleported to the shot's actor spot, 640×400 canvas, 1994 frame located by alignment at (+175,+103) | **97.11%** class / 96.91% RGB |

**How the capture works.** `usehighres` gives a 640×400 native canvas. The
whole 1994 320-wide frame fits around an Avatar-centred camera, so no
scripted camera is needed: teleport the Avatar to the shot's actor
position, capture, and find the 1994 frame by alignment. The remaining
misses are the Avatar's facing (the teleport keeps the old direction) and
the frame-edge pixels the reconstruction already missed.

**Map tests.** They pass on the stamped build: hygiene, edges, route reach,
paint cycles, schedule destinations, monster eggs and round-trip.
`test_map_pins_fresh` fails only on the FIXED.DAT hash, as any rebuild does.

**Not committable yet.** The vignette is an island. Its z=104 mesa ends at
the edge of the 1994 frame with no cliff face east or south-east of the
window, so the void shows there in-engine (`phaseA/screen18_ingame_raw.png`).
Closing and extending the mesa into the surrounding terrain is the Map 10
part of phase B. The verifier runs then.

Evidence is in `phaseA/`: the in-engine capture, the in-engine vs 1994
diff, and the offline built-window diff.

## 8. Outcome: all 19 shots in the build (2026-10-17)

The plan ran A → B → C, with D alongside.

| Phase | What happened |
|---|---|
| A | screen18 went end to end and proved the engine renders the offline replay: 97.11% in-engine vs 97.15% offline. |
| B | Map 10 (8 shots), Map 9 (screen10), Map 11 (screen05, 07) and Map 13 (screen01, 14, 15, 16, then screen13) were placed with closure terrain. |
| C | Map 17 was rebuilt as the open 1994 city around screen11 and screen12; Map 18's sanctum became screen04's cave shrine with the 1994 gods. |
| D | The data contract, cleaned masks, 1994 art shapes 874-881 and `png2shape --indexed`. |

| Map | Shots | In-engine class match (`ingame/SCORES.md`) |
|---|---|---|
| 9 | 10 | 88.1 |
| 10 | 02, 09, 17, 18, 19, 20, 21, 22 | 82.7-95.8 |
| 11 | 05, 07 | 86.4, 86.1 |
| 13 | 01, 13, 14, 15, 16 | 75.97-94.3 |
| 17 | 11, 12 | **98.2**, 85.9 |
| 18 | 04 | 95.3 (the Shield reaches the altar during the ceremony) |

- **Offline numbers.** The built windows painted offline with actors
  (`test_vignettes.py` floors) run 1-10 points higher than in-engine. The
  engine does not place the 1994 actors, and it animates water, lava and
  foam.
- **Verification.** There were four verifier passes
  (`docs/playtest-2026-10-17-vignettes-verify{,2,3,4}.md`) and
  `tools/integrate.sh` reproducible with the estate at 53/53. In ScummVM:
  - the Map 18 ceremony runs end to end, on both the 879 and legacy 828
    paths;
  - the Map 13 ↔ 17 gateways do not bounce;
  - no paint knots at the arrival pads or on the climb;
  - old 870-half saves load.
- **Art changes.** 861 and 862 are retired. 870 is now an alias of 878.
- **Open items** are listed in TODO.md §4.

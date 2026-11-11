# D-track: replay manifest, score contract, art grades and clean masks (2026-10-16)

This is the work on Fable 5.1's go-forward items 1-6 and 9 (painter half) and
the art-directory half of 11 (`fable-5.1-meta-review.md`). One command now
replays every vignette, checks it against its published render and prints
the uniform scores:

    python3 agents/map-populator/src/vignette_replay.py            # all 19
    python3 agents/map-populator/src/vignette_replay.py screen11 --check
    python3 agents/map-populator/src/vignette_replay.py --built    # retail art from shared/build/

Nothing under `build_map_*.py`, `vignette_place.py`, the build or the engine
was touched or run.

## screen18 (for the coordinator)

**`screen18.json` items and `placement.origin_world` are unchanged**: the same
88 items, byte-for-byte equal shape/frame/x/y/z, origin (9088,19584,0). Its
camera was already in the painter sign. Only `verify` (new score contract)
and the `art_1994`/`actors` normalisation touched the file, and screen18 has
no 1994 art and one rendered actor. `vignette_place.py` reads none of the
changed fields.

## What changed

### 1. Blockers

- **Fire pillar and screen19 elder are reference crops.** In
  `art_registry.json` they are kind `reference-crop`, grade `reference-only`
  (ids 2020 and 2040), and the `screen07.json`/`screen19.json` notes say so.
  The "replace it with these pixels" line is gone. Both
  `ReconInteriors-REPORT.md` and `ReconVillage-REPORT.md` now say "reference
  crop". Clean re-cuts are separate files (item 6).
- **Cloud f3/f4 are no longer contradictory, and are now complete.** f3 is f0
  mirrored and f4 is f2 mirrored:
  - The 288 px observed of f3 equal mirror(f0) 288/288.
  - The 481 px observed of f4 equal mirror(f2) 480/481. The odd pixel is the
    top tip, which is dark (an occluder) in screen11 and cloud-white in
    screen13.

  So the 1994 tile set is three drawings plus their FLG_FLIPPED placements.
  f3 and f4 were completed as those mirror images, 1024 px each. As whole
  diamonds they are re-found in screen13 at 996/1024 (168,136) and 1013/1024
  (96,76). The notes in `screen11.json` and `screen13.json` now say this.
- **screen22.** The JSON's items are exactly what produced its render. The
  ReconVillage pass painted them in its own frame, local + (4224,3584), with
  512-unit chunk order, and there the replay is 0 px from the published
  render. In world coordinates the same items differ by 58 px, all from
  chunk-order ties.

  The replay now paints in world coordinates, the engine's frame. So the
  render was re-published (old copy in `superseded/`), and the number moves
  from 96.6 to **96.70** (all-frame class). No item changed.

### 2. One replay manifest

- **`agents/map-populator/src/vignettes/art_registry.json`** holds every 1994
  asset, 48 frames under 37 synthetic ids (2000-2074). Each shape has a
  world-unit footprint, sort flags, `replaces` and a kind. Each frame has:
  - a repo-relative P-mode PNG path;
  - a numeric hotspot, or null when the frame is never placed;
  - its source shot and top-left;
  - its grade, the cross-shot record, `inferred_px` and a note.
- **All 19 vignettes are normalised:**
  - Camera: one sign, the painter's. 04/05/07/10 were negated, and their
    origin notes now say so. Each camera also carries `crop: [W,H]`.
  - Item shapes are retail (< 860) or registry ids (>= 2000):
    - screen01: `'CLOUD1994'` became 2000.
    - screen04: `None`/860/828 with `render_id` 9001-9005 became 2010-2014.
      Each keeps `replaces`/`replaces_frame` (860:0-2, 828).
    - screen07: 865/`None` with 9101/9102/9110-9119 became 2020/2022/2030-2039.
  - The dead `art`, `render_id` and `world` item fields are gone. The 17
    unresolvable `art/…` paths and both `/tmp` paths are gone.
  - The two spikes with a textual hotspot now have numeric ones. Spikes 2 and
    8 sit one row below their last pixel, which is what reproduces the
    published render.
  - Actors have a concrete frame or `unrendered: true` + `art_1994 {id, frame}`
    + `screen_xy`: the zombies, the elder and the two children.
  - `art_1994` entries reference registry ids instead of carrying their own
    png/footprint/hotspot.
- **`vignette_replay.py`** is new. It:
  - builds a `Painter` from the registry;
  - paints `origin_world + local` with the camera shifted to match (origins
    are multiples of 128, so the shift is exact);
  - compares against the published render, reading the middle panel of the
    older composite renders;
  - prints the score contract.

  `--publish` rewrites a stale render/diff pair and `--write-verify` stores
  the scores in each JSON's `verify`.

  World coordinates are not a cosmetic choice. C division and the 512-unit
  chunk order both depend on absolute coordinates. The local frame gets
  screen05 wrong: one item sits at a negative local coordinate, worth 20 px.
  It gets screen22 wrong by 58 px, and screen09 differs by 2 px.

### 3. Painter on the built artifacts

`vignette_paint.Painter(typeflag=…, shapes=…)` still defaults to the retail
`.bak` files, so existing callers are unchanged. `Painter.built()` reads
`shared/build/TYPEFLAG.DAT` + `U8SHAPES.FLX`. `vignette_replay.py --built`
gives identical numbers on 04/11/18/22, since the vignettes use only retail
ids and registry art.

### 4. Score contract

`verify` in every JSON now holds the same fields, with `vignette_replay.py`'s
docstring as the definition:
- `all_frame_strict` and `all_frame_class`, with unpainted pixels counted as
  mismatches;
- `void_as_black_points`;
- `excluded_actor_points`;
- `provenance_points` {retail, cross_shot_validated_1994, single_shot_1994,
  inferred, unmatched};
- `published_render_identical` and the `replay` command.

The pass texts on unexplained pixels survive as `verify.residuals`. The old
per-pass numbers are dropped: each used its own convention, and the pass
reports keep them.

### 5. Cross-shot validation

Every frame was searched in every other shot by FFT class matching
(`vignette_replay.py --validate-art` reruns the search, about 8 minutes, and
flags any frame whose curated registry grade differs from the automatic one):
- positions fully in bounds, and positions at least 50% visible;
- plain and mirrored;
- the mismatch components counted at the best position.

**Grade rule:** cross-shot-validated if the best match covers at least 97% of
the visible pixels, or at least 85% with at most 3 mismatch blobs of 10 px or
more (occluders). Kinds `reference-crop` and `residual` get grades
`reference-only` and `residual`. The results are in the grade table below and
in each registry frame's `cross_shot`.

New findings from the search:
- **The altar's Sacred Shield in screen04 is the sun half from screen11 plus
  the eye half from screen12.** It matches 608/609 as that composite. This
  validates the sun half (339/339 in screen04), the eye-half draft (269/274)
  and the altar shield.
- **Wall spike 0 is not 1994 art.** It is exactly retail 26:5 (89/89), and
  screen14 shows the same pixels owned by retail 26:14. Spike 6 resembles
  retail 107:1 at 107/125.
- **The plain column is the banded column without its three bands**: 572/710,
  with exactly three 46-px mismatch blobs. Its shaft is validated through the
  banded column.
- **The screen14/15 white dashes** (10 and 11 px) are exact parts of the
  screen04 striped prop [INFERENCE: the same 1994 bone/rib object].

### 6. Clean masks

| Asset | Before | After | How |
|---|---|---|---|
| Water Zombie s02_a (2050:0) | 660 px, components [658,1,1], 27 holes | 685 px, 1 component, 0 holes | dropped 2 strays; filled holes with the screen02 pixels at their place (grey shading over grey rock that the render matched by coincidence) |
| Water Zombie s02_b (2050:1) | 701 px, 21 holes | 722 px, 1 component, 0 holes | holes filled from screen02 (blue skin specks the colour of the water) |
| Water Zombie s09 (2050:2) | 651 px, [647,4], 48 holes | 695 px, 1 component, 0 holes | dropped the 4-px patch; holes filled from screen09 |
| cloud f3 / f4 (2000:3/4) | 288 / 481 px | 1024 / 1024 px | mirror(f0) / mirror(f2); see item 1 |
| elder, screen19 (2041:0, new `art_s19_elder.png`) | 819 px reference crop | 703 px, 1 component | removed 113 doorway/plank pixels reachable from outside the figure through the doorway palette, then 3 jamb-edge spur pixels |
| fire pillar (2021, new `s07_fire_pillar_upper.png`) | 1525 px reference crop, 13 holes | 1068 px, 1 component, 0 holes | kept rows 0-63; rows 64-90 are `to_be_drawn` |

Notes on the last two rows:
- **Elder.** The doorway palette is {12,23,168-173,177,187-189,217-219,238,253};
  it is absent from the screen20 elder except 11 enclosed px of 217-219
  shading, which are kept. One enclosed transparent pixel at (21,16) is real
  doorway fill (shot palette 188) between arm and body, so it stays
  transparent.
- **Fire pillar.** Row 64 is where the lava glow first cuts the shaft. Below
  the cap only columns 0-20 are kept; columns 21+ are wall texture. 8 lava
  pixels (palette 233-237) were removed and 12 holes filled from the shot
  (tan band highlights).

Every opaque pixel of the cleaned sprites equals the source shot at its
source position:
- the zombies 685/685, 722/722 and 695/695;
- the elder 703/703;
- the pillar 1068/1068;
- f3/f4 against their observed pixels, 288/288 and 480/481.

So nothing was invented. The only documented inferred pixels in the registry
are Felicitar's 42 and the walkway's 19. The walkway's 19 are the pixels no
screen12 instance shows matching; ReconCloud's report said 34 by an
unrecorded consensus.

### 7. Art directory hygiene and the index-255 trap

- 19 non-asset files moved into `previews/` subfolders: 18 RGB/RGBA previews,
  sheets and x4/x6 zooms, plus the full-frame `screen01_cloud_observed.png`
  evidence. 7 of these are in ReconCliffs, 4 in ReconVale and 8 in
  ReconVillage.
- `shared/data/lv-1994-art/*/*.png` is now exactly the 48 registered P-mode
  assets.
- **`tools/png2shape.py`** maps index 255 correctly. A P-mode PNG with tRNS
  255 converts to RGBA with those pixels transparent, and `quantize()` emits
  only 0..254. Four other traps remain for these PNGs:
  1. The default magenta chroma key (tolerance 60) deletes any purple/pink
     1994 pixel unless `--no-key` is passed.
  2. `trim_to_alpha` crops the canvas and so moves the registry hotspot,
     unless `--no-trim` is passed.
  3. U8PAL has 7 duplicate-RGB pairs: 2/144, 9/28, 10/51, 11/15, 13/140,
     46/191 and 47/239. The RGB round trip remaps the higher index to the
     lower one. That is visually identical, but not index-identical.
  4. A real teal pixel (24,125,125) cannot be stored in these PNGs at all.

  **The trap has already cost one pixel.** Screen04 pixel (139,78) is palette
  255 in the shot, inside the striped prop 2014's box, and the extraction
  dropped it. Screen10 has two more teal pixels, at (86,126) and (81,136),
  outside any asset.

  Recommendation (png2shape.py is not D-track's file): add an indexed
  pass-through mode for U8PAL P-mode sources (no key, no trim, no quantize),
  and carry teal as an explicit mask.

## Replay results

**Before re-publishing, 12 of 19 published renders were pixel-identical to
the JSON replay**: 01, 04, 07, 10, 12, 14, 15, 16, 17, 18, 19 and 20. screen07
joined them through the numeric spike hotspots, with no re-publish. The other
seven were re-published from the replay with `--publish`; the old pairs are
in `superseded/`.

| Shot | Differed by | Why |
|---|---|---|
| 02 | 118 px | The docs copy was stale. ReconVale's own final composite (`/tmp/…/screen02_verify.png`) equals the JSON replay exactly; the docs copy predates the last augment round. |
| 09 | 55 px | Same as 02. The final pass composite is within 2 px of the replay; those 2 px are chunk-order ties. |
| 21 | 197 px | Same as 02. The final pass composite equals the replay exactly. |
| 05 | 20 px | One item is at a negative local coordinate. The world frame is the engine's. |
| 22 | 58 px | Village-frame chunk order; see item 1. |
| 11 | 1 px | The f4 tip pixel, now mirror(f2). |
| 13 | 82 px | f3/f4 completed. |

After that, `vignette_replay.py --check` exits 0, with **19/19 identical**.
The 17/18 renders remain shot|render|diff composites from ReconVale; their
middle panels are identical.

## Per-shot scores (uniform contract)

All values are percent of the whole frame:
- **strict** and **class** count unpainted pixels as mismatches;
- **+void** is what counting unpainted-and-shot-black pixels as matched would
  add;
- **+actors** is what excluding the unrendered 1994 actor sprites would add;
- the **provenance** column splits the matched pixels as retail / cross-shot-validated 1994 /
  single-shot 1994 (single-shot, reference-only and residual grades) /
  inferred / unmatched.

| Shot | strict | class | +void | +actors | provenance |
|---|---:|---:|---:|---:|---|
| 01 | 94.0 | 94.1 | 0.0 | 0.0 | 87.6 / 6.5 / 0.0 / 0.0 / 5.91 |
| 02 | 95.7 | 96.0 | 0.0 | 2.4 | 96.0 / 0.0 / 0.0 / 0.0 / 3.96 |
| 04 | 99.9 | 99.9 | 0.0 | 0.0 | 91.3 / 1.0 / 7.6 / 0.0 / 0.09 |
| 05 | 82.9 | 83.3 | 12.2 | 0.0 | 83.3 / 0.0 / 0.0 / 0.0 / 16.70 |
| 07 | 86.9 | 86.9 | 8.3 | 0.0 | 80.3 / 0.0 / 6.6 / 0.0 / 13.06 |
| 09 | 93.7 | 93.7 | 0.0 | 1.0 | 93.7 / 0.0 / 0.0 / 0.0 / 6.32 |
| 10 | 75.9 | 87.0 | 4.9 | 0.0 | 87.0 / 0.0 / 0.0 / 0.0 / 13.02 |
| 11 | 99.9 | 99.9 | 0.0 | 0.0 | 7.3 / 82.4 / 10.3 / 0.0 / 0.06 |
| 12 | 82.5 | 82.8 | 0.0 | 0.0 | 8.6 / 37.0 / 37.1 / 0.0 / 17.18 |
| 13 | 73.1 | 74.1 | 0.0 | 0.0 | 44.3 / 29.8 / 0.0 / 0.0 / 25.88 |
| 14 | 89.3 | 89.4 | 0.2 | 0.0 | 89.4 / 0.0 / 0.0 / 0.0 / 10.56 |
| 15 | 95.7 | 95.9 | 0.1 | 0.0 | 95.9 / 0.0 / 0.0 / 0.0 / 4.07 |
| 16 | 94.3 | 94.3 | 0.0 | 0.0 | 94.3 / 0.0 / 0.0 / 0.0 / 5.73 |
| 17 | 92.7 | 92.8 | 0.0 | 0.0 | 92.8 / 0.0 / 0.0 / 0.0 / 7.23 |
| 18 | 98.1 | 98.4 | 0.0 | 0.0 | 98.4 / 0.0 / 0.0 / 0.0 / 1.60 |
| 19 | 95.8 | 96.1 | 0.0 | 1.2 | 96.1 / 0.0 / 0.0 / 0.0 / 3.93 |
| 20 | 94.7 | 95.4 | 0.0 | 2.0 | 95.4 / 0.0 / 0.0 / 0.0 / 4.57 |
| 21 | 92.9 | 93.3 | 0.0 | 0.0 | 93.3 / 0.0 / 0.0 / 0.0 / 6.71 |
| 22 | 95.8 | 96.7 | 0.0 | 0.0 | 96.7 / 0.0 / 0.0 / 0.0 / 3.30 |

Fable's acceptance numbers:
- **screen02 reads 96.0 (+2.4 excluded).** Fable had +2.3. The cleaned zombie
  masks are 46 px larger in total (48 hole pixels filled, 2 strays dropped).
- **screen05 reads 83.3 (+12.2 void).** As expected.
- **screen11 reads 7.3 / 82.4 / 10.3 / 0 / 0.06, not 7.3 / 80.5 / 11.6.** Two
  grades rose on new evidence:
  - the sun shield half (0.58 pts) is validated by the screen04 altar shield;
  - f3/f4 (1.33 pts) are mirrors of the validated f0/f2.

  What stays single-shot is the plain column's paint, 10.3 pts.

With every pixel counted, 13 of 19 shots score 92% or more (class). The six
below are 05, 07, 10, 12, 13 and 14.

## Per-asset grades

There are 48 frames: 9 cross-shot-validated, 27 single-shot, 2
reference-only and 10 residual (spike 0 counts as residual: it is retail
art). Each registry frame's `note` gives the evidence.

| id:frame | file | kind | px | source | best other shot | grade |
|---|---|---|---:|---|---|---|
| 2000:0 | `cloud_floor_f0.png` | sprite | 1024 | 11 (189,17) | 13 1019/1024 | **cross-shot-validated** |
| 2000:1 | `cloud_floor_f1.png` | sprite | 1024 | 11 (253,81) | 12 914/1024 (2 occluder blobs) | **cross-shot-validated** |
| 2000:2 | `cloud_floor_f2.png` | sprite | 1024 | 11 (61,17) | 13 1013/1024 | **cross-shot-validated** |
| 2000:3 | `cloud_floor_f3.png` | sprite (= mirror f0) | 1024 | 11 (-35,1) | 13 996/1024 | **cross-shot-validated** |
| 2000:4 | `cloud_floor_f4.png` | sprite (= mirror f2) | 1024 | 11 (285,1) | 13 1013/1024 | **cross-shot-validated** |
| 2001:0 | `white_column_plain.png` | sprite | 710 | 11 (60,102) | 12 572/710 (= banded minus 3 bands) | **single-shot** |
| 2001:1 | `white_column_banded.png` | sprite | 698 | 12 (4,20) | 11 630/698 (1 blob) | **cross-shot-validated** |
| 2002:0 | `shield_half_sun_s11.png` | sprite | 339 | 11 (183,138) | 04 339/339 | **cross-shot-validated** |
| 2003:0 | `marble_walkway_strip_tile.png` | sprite | 1527 | 12 (29,79) | 13 155/1527 | **single-shot** (19 inferred px) |
| 2004:0 | `gold_brick_floor.png` | sprite | 1024 | 12 (29,163), edge | 13 371/1024 | **single-shot** |
| 2004:1 | `gold_brick_floor_f1.png` | sprite | 1016 | 12 (-3,147) | 13 317/1016 | **single-shot** |
| 2005:0 | `shield_half_eye_s12_draft.png` | sprite-draft | 274 | 12 (126,58) | 04 269/274 | **cross-shot-validated** |
| 2010:0 | `s04_god_felicitar_P1.png` | sprite | 1502 | 04 (111,29) | 21 176/1502 | **single-shot** (42 inferred px) |
| 2011:0 | `s04_god_doloras_P2.png` | sprite | 1181 | 04 (205,57) | 21 121/1181 | **single-shot** |
| 2012:0 | `s04_god_timyra_P3.png` | sprite | 1712 | 04 (78,96) | 21 114/1712 | **single-shot** |
| 2013:0 | `s04_shield_on_altar.png` | sprite | 609 | 04 (168,104) | 11 sun 339 + 12 eye = 608/609 | **cross-shot-validated** |
| 2014:0 | `s04_striped_prop_P1.png` | sprite-draft | 166 | 04 (136,64) | 14 118/166 | **single-shot** |
| 2020:0 | `s07_fire_pillar.png` | reference-crop | 1525 | 07 (170,60) | 10 373/1525 | **reference-only** |
| 2021:0 | `s07_fire_pillar_upper.png` | sprite-partial | 1068 | 07 (170,60) | 10 293/1068 | **single-shot** (rows 64-90 to draw) |
| 2022:0 | `s07_lava_glow_and_pit.png` | residual | 1376 | 07 (156,67) | 05 188/1376 | **residual** |
| 2030:0 | `s07_wall_spike_0.png` | sprite-draft | 89 | 07 (188,36) | 14 89/89 = retail 26:5 | **residual** (not 1994 art) |
| 2031-2039 | `s07_wall_spike_1..9.png` | sprite-draft | 86-125 | 07 | at most 40/116, except spike 6: 17 114/125 (retail 107:1-like) | **single-shot** |
| 2040:0 | `art_s19_elder_draft.png` | reference-crop | 819 | 19 (140,60) | 20 157/819 | **reference-only** |
| 2041:0 | `art_s19_elder.png` | sprite-draft | 703 | 19 (140,60) | 20 147/703 | **single-shot** |
| 2041:1 | `art_s20_elder_staff_draft.png` | sprite-draft | 757 | 20 (167,44) | 19 158/757 | **single-shot** |
| 2042:0/1 | `art_s20_spear_child_{dark,blond}_draft.png` | sprite-draft | 200/203 | 20 | 14 51/200, 40/203 | **single-shot** |
| 2045:0/1 | `art_s22_blue_plant_{a,b}_draft.png` | sprite-draft | 159/142 | 22 | 62/159, 40/142 | **single-shot** |
| 2050:0 | `art_wzombie_s02_a.png` | sprite-draft | 685 | 02 (140,6) | 09 44/685 | **single-shot** |
| 2050:1 | `art_wzombie_s02_b.png` | sprite-draft | 722 | 02 (182,58) | 09 47/722 | **single-shot** |
| 2050:2 | `art_wzombie_s09.png` | sprite-draft | 695 | 09 (10,42) | 02 50/695 | **single-shot** |
| 2060-2062 | fish halo, foam, skull beam | residual | 427/1549/1037 | 02/09/21 | (halo 16 388/427: navy water, uninformative) | **residual** |
| 2070-2074 | screen14-16 scraps | residual | 10-125 | 14/15/16 | 2070/2072 = parts of 2014 in screen04 | **residual** |

## Open issues

1. **Cloud z-encoding (go-forward 7)** is unchanged and still open: cloud at
   z=1, objects at z=2, and the Avatar settles 1 px lower in-engine.
2. **screen13 stacks duplicate cloud flats at one position.** (2591,2367,1)
   carries f2, f1 and f4, and (2975,2463,1) carries f0, f2 and f3. In-engine
   these are z-fighting duplicates. Pick one per position before integrating
   screen13. Since f3/f4 are mirrors, the choice is between f0/f2 placements
   with and without FLG_FLIPPED.
3. **screen07:**
   - spike 0 is retail 26:5, so the vignette is missing (or mis-sorting) a
     wall 26 piece at shot (188,36);
   - spike 6 is probably retail 107:1;
   - the pillar's lower third has to be drawn before 2021 can ship.
4. **The teal index-255 convention.** One shot pixel is already lost (screen04
   (139,78), in 2014). png2shape needs `--no-key --no-trim` for these PNGs, or
   an indexed mode.
5. **Single-shot assets need a second source or an explicit sign-off before
   they ship:** gods, walkway, gold brick, plain column paint, villagers,
   zombies, plants, spikes. Felicitar keeps its 42 inferred pixels.
6. **Cameras and frames.** `camera.sx0/sy0` stay in the local frame; the
   world camera is computed (`vignette_replay.world_camera`). Any future
   `test_vignettes.py` must paint in world coordinates, as the replay does;
   painting in the local frame can differ by tens of pixels on sort ties.
7. **`verify.residuals` texts** are the passes' own notes. Their percentages
   (e.g. screen07 "~4.8%") predate the uniform contract.

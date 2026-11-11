# ReconCloud — screen11/12/13 vignettes (Map 17 Cloud City)

Working dir: `/tmp/lv-shots/recon/ReconCloud`. Tools written here: `engine_paint.py` (engine-faithful painter: item_sorter.py's port of ScummVM's
SortItem::below/overlap + PaintSortItem, compositing frames in that order; retail art from U8SHAPES.FLX.bak/TYPEFLAG.DAT.bak,
1994 drafts registered as shapes 2000+), `region_search.py` (retail frame search inside a box), `actor_search.py` (Avatar frames, shape 1).

## screen11 — obelisk forum (DONE)
- Coverage before: 46% (decomposer). After: **99.94%** of all 58,011 px reproduced by the engine-order render
  (`screen11_final_diff.png`: shot | render | green=match red=mismatch).
- Cloud floor: 3 exact frames (f0-f2, 62x32 diamond, 301's mask/hotspot) laid one per 128 cell, random frame per cell
  (lattice map in vignette). Two edge cells use 2 more frames (f3, f4), partial here, both found again in screen13.
- **The obelisk is 100% retail**: 12 f17 + 12 f16 (z42), 12 f15 + 12 f14 (z82), cap 545 (z122), skull 814 at its foot (z42),
  standing on four banded 1994 columns (2x2 ring, 64 apart). Our 861 does not match the shot at all
  (`cmp_obelisk_shot_vs_retailcomposite_vs_861.png`) -> retire 861, build the obelisk from these retail pieces.
- Gem pillars = 1994 white column (16x47, footprint 1x1x5) + **retail gem 596** (frames 2,3,4,5,6,7) on top at z+40.
- Shield half (sun emblem) = 1994 art on retail 828's left-half outline -> replaces our 870 frame 0 (hand emblem).
- Skeletons 218 f0, 219 f0 and bottles 471 f1 are retail, exact. Avatar = shape 1 frame 23 (exact).
- Residual 34 px explained in the vignette (bottle outline 21 px unexplained, 1994 sort 8 px, skull eye colour 2 px).
- Z model (all shots): cloud tiles z=1 (lets cloud lie over z=0 earth in screen13), objects z=2.
- Placement: Map 17 Main Plaza, origin_world (1280,4736,0) -> front drum at (4128,7200,2), one unit off the old
  obelisk pin (4095,7167). Pin moves: 861 retired/replaced, shield half 870f0 q81 (6208,1568,0)->(4264,7204,2),
  Memorial Hall skeletons -> obelisk forum, plaza dais + candelabras removed.

## screen12 — walkway + throne nook (PARTIAL)
- Coverage before 25% -> render match **82.8%** (`screen12_final_diff.png`).
- Cloud floor: same 3 frames, phase (29,3). Columns: the banded 1994 column, stacked x2 (z2/z42) for the four colonnade posts, single elsewhere.
- **Marble walkway** = one 62x52 frame (`art/marble_walkway_strip_tile.png`) repeating every 128 along x in BOTH strips: a 128x128x8 slab with gold/white back rim and gold-trimmed front face; upper strip sits 480 further -y (32-grid). 34 always-hidden rim px inferred.
- **Gold brick** = 2 exact frames (f0 complete, f1 1016/1024), also in screen13.
- Retail nook items accepted by the render: throne 223 f3, bones 235 f1/237 f1, rubble 526 f6/f7 and 553, vases 471 f6/f7, 663 f1, 843, straw 720 f1, 504.
- Not done: cloud-lobe edge over gold, nook dais floor/rims, left throne, Avatar, shield half B (draft colour-key cut only).

## screen13 — summit / city edge (PARTIAL)
- Decision: Map 13 summit [INFERENCE]: retail earth + tree/mushroom/spires + cloud patches over earth + gold street corner.
- Render match **74.0%** with retail earth, cloud f0-f4 placements on a 32-unit grid, gold f0/f1, retail props.
- Cloud f3/f4 (partial from screen11) re-found exactly here. Rim/lobe frames not recovered: they are cloud pieces with lobed outline
  laid at 32-unit offsets (one repeats at screen steps (24,-4)/(48,8), e.g. patch (150,5) == (126,9) == (102,13) == (134,149)).

## Key conclusions
1. Cloud floor = 3 exact frames (+2 partial); our 862 is a different drawing -> replace with f0-f2 (`cmp_cloud_f0-2_vs_862.png`).
2. Obelisk = retail pieces only (12 f14-f17, 545, 814) on banded 1994 columns -> retire 861.
3. Gem pillars = 1994 white column + retail gem 596. Shield half 1 (sun) exact, replaces 870 f0.
4. Z model: cloud z=1 over z=0 ground (earth/gold), objects z=2.

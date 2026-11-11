# ReconVale — screens 17, 18, 21, 02, 09 → world-coordinate vignettes

All five vignettes, verify renders and art drafts are in this directory. Nothing tracked in the repo
was edited, and no build, install, ScummVM run or test was started.

## Summary

| shot | decomposer coverage (before) | exact match, whole frame (after)¹ | exact match on item pixels | items | actors | art_1994 | placement (Map 10 origin) | pin moves |
|---|---|---|---|---|---|---|---|---|
| 17 gargoyle stair | 89.1% | **92.8%** | 94.2% | 112 | 1 | 0 | (17536, 22016, 0), temple approach | 3 (pad 210 and its 2 eggs → z 112) |
| 18 cliff/mushroom/colonnade | 92.8% | **98.4%** | 99.1% | 88 | 1 | 0 | (9088, 19584, 0), mushroom-garden south scarp | 0 (1 conditional) |
| 21 lava / skull pen | 92.8% | **93.3%** | 95.6% | 84 | 2 | 1 | (8320, 20608, 0), lava field on the gate road | 0 |
| 02 lake shore | 92.4% | **98.4%** | 98.4% | 90 | 4 | 3 | (13184, 17792, 0), the Lake | 0 |
| 09 waterfall | 91.2% | **94.5%** | 95.3% | 82 | 2 | 2 | (10496, 15616, 0), west edge of the Lake | 0 |

¹ "After" is a strict engine render: the ported ScummVM paint order, with each pixel compared exactly by
palette class against the GIF. Pixels of the 1994-only Water Zombies are excluded. Retail actors are
rendered, not excluded. "Before" is shot_decompose's greedy coverage, which never checks paint order.
The two numbers are close in meaning, but "after" is the harder test.

Files per shot:
- `screenNN.vignette.json`, in the contract format. `items[].why` is `matched`, `matched-aug` (taken from
  the raw candidates), `lattice-fill` (`-hidden` when the tile is fully hidden), `stair-model`, or has
  `+OFF-LATTICE` appended.
- `screenNN_verify.png` is ×3, three panels: shot | render | diff. In the diff, red is a mismatch and blue
  is no item. The zombie pixels show red there, but they are excluded from the numbers.
- `verify.local_frame_render_identical = true`: the vignette in local coordinates renders the same,
  pixel for pixel, as the solve.
- Vignette-local x,y are on the retail 128k+127 tile lattice. Lowest item z = 0. Place a vignette with
  `world = local + origin_world`.

## Method
1. **Raw candidates.** `scan_all.py` runs the shot_decompose search on every retail shape and keeps
   every candidate, without the greedy step (`raw_screenNN.json`). An extra edge search finds frames
   clipped by the top border, which the decomposer's anchors miss. It found the 66.3/66.6/66.7 rock
   spires in 17 and 18.
2. **Camera.** One ground tile fixes the lattice. Retail tiles sit at 128k+127: 1553 of 1767 shape-301
   placements in FIXED.DAT.bak. I used the engine's integer projection, `sx = x/4 - y/4` and
   `sy = x/8 + y/8 - z` with C truncation. This matters because some screen positions cannot be
   reached at any z that is a multiple of 8.
3. **World solve.**
   - Lattice shapes (fixed land flats, flat tiles ≥128, cliffs 26-34) are placed only on retail
     residues. The residues come from FIXED.DAT.bak with the GLOB.FLX globs expanded (640k items).
   - Props sit on their region's tier surface.
   - Cliffs, the pen and the stairs are solved by coordinate descent on render agreement.
   - Each shot's ground phases fix the relative tiers modulo 32. The tier values I chose are justified
     per shot below.
4. **Loops.** I ran greedy add from the raw candidates, then prune, then lattice-fill, then frame-swap.
   A step was kept only if exact matches went up. Hidden lattice cells were filled when the fill
   changed no pixel.

## Per shot

### screen17 — gargoyle stair (Map 10, temple approach)
- **Content.** All retail:
  - two gargoyles 38.0 on the z 112 plateau;
  - stalagmite spires 66.3/66.7/66.8 at the top edge;
  - cliffs 26/29/32 in two courses either side;
  - dirt 386/4 over 301 rock.
- **Stair.** It is **not** 70-cobble. It is the retail cobble step blocks 98/112/99/100/107 frame 1
  (heights 8-48), with a 335 kerb on the west side and 84/355/356/211 brick strips forming the east
  wall.
- **Stair geometry.** The left kerb gives the geometry exactly: one step per 32 units of +y, 8 units
  lower each step (screen −8,+12). I rebuilt the stair as a model:
  - rows at y = 799 + 32k (local), top = 104 − 8k;
  - x columns 799 (kerb), 895 and 991 (cobble), 1023 (wall).
- **Two versions.** A render-optimal fit with free z per block scores 0.6 points higher (54,788 against
  54,457 matched pixels of 58,696), but it puts blocks at random heights. The shipped version is physically
  consistent.
- **Unexplained.**
  - The east brick wall below the stair (x 196-245, 623 px) is under-built: the shot shows a tall
    84/355 brick face there, and the course-by-course greedy added only 11 strips. The cliff face west of
    the stair (575 px) has the wrong frame or z on 26.3.
  - The left 32 cliff column (336 px).
  - The bottom-right corner (307 px).
- **Avatar.** 1.4, standing between the gargoyles.

### screen18 — scarp, giant mushroom, colonnade (Map 10, mushroom garden)
- **Content.** All retail:
  - giant mushroom 625.0, small mushroom 626.0, 465/466 clusters;
  - colonnade: columns 249.12, iron bars 575.0/576.0;
  - spires 66.0 and 66.6, stones 799/757/768;
  - scarp of 26/27 in two courses (z 0 and 48), with a 125 crest at 96, so the plateau surface is 104.
- **Unexplained.**
  - The top-centre light-grey rock: mostly fixed by the edge hit 66.6. The remaining 528 px are now
    partly explained.
  - The right-edge 249 column (281 px).
- **Avatar.** 1.4.

### screen21 — lava crossing, skull-post pen (Map 10, lava field)
- **Layout.** A z 64 knoll with brown dirt carries the pen. The pen uses the retail skull-post kit:
  148 posts, 153/157 rails, 156, and a 162 deck. A one-course cliff (32 run along y at local x 895)
  faces east down to a 409 lava pool with 122 crust at z 0. A cobble stair of 102/104/105/106/108
  frame 1 climbs west from the lava to the knoll.
- **Eye-serpent.** It is **retail 509 "seeker" frame 126**, a 100% match.
- **Avatar.** 1.181.
- **Unexplained.**
  - The L-shaped skull-carved deck-edge beam of the pen (1037 px), saved as `art_pen_skullbeam_s21.png`.
  - The lava's dark rock islands and edge (≈600 px).
  - Some 409 tiles kept off-lattice, marked `+OFF-LATTICE`.
- **Stair caveat.** The stair-block z values come from render ordering (16-80) and have not been checked
  as a physical stack [INFERENCE].

### screen02 — lake shore (Map 10, the Lake)
- **Terrain.**
  - Rock 301/125/70 shore with a 128 jagged rim at z 8.
  - Water 347 at z 0. **Deep water is 347.16, a plain navy tile at 100% class 158, on the 128 lattice.**
    Earlier passes used 710, and the decomposer's 710, 685 and 671/762 hits in the navy were spurious.
  - The rock stack in the water is 128.17.
- **Actors.**
  - The body is **Avatar 1.252** (dead frame, 795/856 px).
  - The jawed creature is **retail 81.4 "fish"** (860/860 px).
  - Two Water Zombies, 1994-only art.
  - A scimitar 541.0 lies by the body; it is a map item.
- **Unexplained.** A deep-navy halo round the fish (427 px): `art_fishhalo_s02.png`.

### screen09 — waterfall (Map 10, decided against Map 11)
- **The waterfall is retail shape 439 frame 0**, at 2862/3057 px. It sits at residue (31,31), the same
  residue as all five retail placements. It falls a single 48 course into foam 435/436/437/438 (all
  animated), which is the retail idiom in maps 4, 25 and 26: 439 at z 8 over foam at z 0. **No new
  waterfall art is needed.** This corrects the v2/v3 research ("no shape identified").
- **Layout.**
  - Upper tarn: 347.17 at z 56, inside a 128/668 rim, on a z 64 shelf.
  - Cliff: 32/26/27/29 in one course, z 8 to 56.
  - Foam pool: z 0 to 8, which is lake level.
- **Actors.** Avatar 1.190 and one Water Zombie (1994 art) on the shelf.
- **Unexplained.** Foam edges (1549 px): static frames cannot match one animation phase across all
  tiles. Saved as `art_foam_s09.png`.
- **Why Map 10 and not Map 11.**
  - Same water and rim kit as screen02.
  - The Water Zombie is the Lake monster (preview-3, our lake eggs).
  - Open-air cliffs topped with 301/125.
  - Almost no black void: one weak 334 hit, 56/127 px.
  - Map 11's Water Section deliberately has no water (`build_map_11.py:41,719`), and its 1994 shots
    (05/07) are black-void caves.

## 1994-only art
- **Water Zombie.** Three poses: `art_wzombie_s02_a.png` (front), `_s02_b.png` (back, club raised),
  `_s09.png` (lunging). The comparison with our 872 is `art_wzombie_vs_872.png`.
  - The 1994 zombie is teal with bright-green slime blotches and a dark-green loincloth. It is stockier
    than ours.
  - 872 (a recolour of ghoul 142) is pale blue-grey with no kilt. The best silhouette overlap
    (intersection over union) is only 0.57-0.64.
  - **Recommendation:** recolour and redraw 872 toward these pixels: a teal/green ramp plus the kilt.
    Only 3 of the 451 frames have a 1994 reference, so a pixel replacement of the whole set is not
    possible.
- **None of the other custom shapes (860-870) appear in these five shots.** Nothing else here replaces
  existing custom art.
- The remaining drafts (pen beam, fish halo, foam residual) are U8PAL-indexed PNGs with index 255
  transparent. Their footprints are null because no shape is proposed yet [INFERENCE].

## Placement and pin moves (details in each JSON's `placement`)
- **17 → Map 10 at (17536, 22016, 0).**
  - The stair centre lands on the pad/trigger column x 18432, with the gargoyles at y 22751.
  - The vignette needs a **z 112 shelf** north of the temple pit. The pit floor is z 0.
  - **Pin moves:** pad 210, EGGENDGAME and EGGREAPPLY move from (18432,22784,0) to (18432,22720,112).
  - Trigger 211 (18432,23552,0) stays on the pit floor. The stair must be extended by 4 rows
    [INFERENCE].
  - 196 existing items in the footprint are replaced, including the current 249/113/15 columns and
    gate pieces.
  - I rejected Map 18 for this shot: the materials are the Vale's surface (301 rock, 386/4 dirt, 66
    spires, open cliffs), and the stair descends into the ground.
- **18 → Map 10 at (9088, 19584, 0).**
  - The scarp runs along world y 20607, x 9471-10335, and drops south.
  - The garden becomes a **z 104 mesa**.
  - No pins in the window. Egg group 7 at (10500,19500) and its trigger (9860,19532) need z 104 only if
    the mesa is extended north over them.
- **21 → Map 10 at (8320, 20608, 0).**
  - The pen centre lands at (9007, 21775).
  - The lava lies on the road-end → gate line, at x 9343-9583, y 21119-21503.
  - The knoll is z 64.
  - The gate pins (z 8) are unchanged. The knoll must step down to the gate shelf beyond the window.
  - The shot puts lava right on the route, so the lane rule needs a causeway or the shot's rock islands.
- **02 → Map 10 at (13184, 17792, 0).** The origin was found by search over 128-multiples inside the
  lake rectangle so that every egg and quest pin in the window stands on vignette land at z 8: egg
  group 8 at (13855,18271) and (14016,18400), group 2 at (13888,19008), and the passage stone
  (13888,18368,8). The two zombies land at (13880,18535) and (14175,18696). **Flag:** the window
  (13311-14719, 17919-19327) puts z 8 shore inside the lake rectangle, replacing 144 water cells. The
  shot demands it.
- **09 → Map 10 at (10496, 15616, 0).**
  - The tarn shelf is entirely west of x 11264. The foam pool is the lake's west edge.
  - One foam column (x 11136-11263) spills just outside the rectangle: **flag**.
  - No pins in the window. Egg (10944,17312,0) group 3 is one tile south and goes to z 64 only if the
    shelf is extended.
- **Overlaps.** 18 and 21 meet at y 20735 without overlapping, and at the seam 18's lower ground and
  21's empty north-east corner are both z 0. No other windows overlap.

## Side findings (for the main agent; no files edited)
- `lv_shapes.py:129-135` and `build_map_11.py:66` call 435-437 "trap burst / flame tiles, damaging".
  Retail places 435/436/437/438 only as waterfall foam around 439. Worth checking before Map 11 uses
  them as fire hazards.
- The temple stair kit is 98-112 f1 + 335/84/355/356/211, not 70. The research layout's "70-cobble
  stair" is wrong.
- Every Vale vignette implies real tiers: 17 needs 112, 18 needs 104, 21 and 09 need 64. Today Map 10
  is almost flat at z 0. This is the main structural change these shots demand.

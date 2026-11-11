# ReconCliffs: screens 01, 14, 15 and 16 (Map 13, Cloud Cliffs)

All four shots are Map 13. Deliverables: `screenNN.vignette.json` (one per shot),
renders and diffs (`sNN_final_render.png`, `sNN_final_diff.png`; the diff is ×3:
shot | render | shot with wrong pixels red and uncovered pixels blue), the art drafts
in `art/`, and `placement_overview.png`. The toolkit is `tk.py` (painter) and
`cropsearch.py` (search for small items). The working state is in `screenNN_state.json`.

## Summary

| shot | area | decomposer coverage | covered px match | frame px match | items | actors | art_1994 | placement origin (dx,dy,dz) |
|---|---|---|---|---|---|---|---|---|
| 01 | summit edge over the cloud | 89.5 % | 97.3 % | 94.1 % | 85 (11 cloud tiles) | Avatar 1:244 (climb pose), skeleton warrior 119:83 | cloud floor (3 frames, replaces 862) | (2176,-1024,+56) |
| 14 | skull ring under the north face | 91.0 % | 93.0 % | 89.4 % | 70 | Avatar 1:198 on the ring | white dash (10 px) | (-1024,256,0) |
| 15 | lake causeway, south part | 94.7 % | 98.9 % | 95.9 % | 67 | Avatar 1:17 on a stone | red blob, white fragment | (-1024,2560,-8) |
| 16 | lake causeway, north landing | 93.9 % | 96.7 % | 94.3 % | 67 | Avatar 1:172 on the 193 pillar | white bone scatter, white rib piece | (-1152,1536,-8) |

- **Decomposer coverage** counts 2-D hits with no consistency check and no draw order.
- **Covered px match** is measured on the pixels my items draw.
- **Frame px match** is measured on the whole frame. Black where nothing is drawn counts as the engine background.
- Both of my numbers come from a single 3-D item list. That list is painted by an engine-faithful sorter (the
  `item_sorter.py` port of ScummVM ItemSorter), using the retail `.bak` TYPEFLAG and U8SHAPES.
- A pixel matches when its RGB is within 12 (L1 distance).

## Method

- **Tier z from the 128-unit lattice.** For tile hotspots the residue
  t = (hy - 16*(hx - lat)/32) mod 32 gives z ≡ K - t (mod 32).
  - I checked the retail stacking rule on maps 31, 37 and 62. Courses 26-32 stack 48 apart on one (x,y). Crest 125
    sits at the top of the course. The plateau's 301 is at the crest's z + 8.
- **Parity check.** For an even sx, an engine screen point satisfies
  (x//8 + y//8) ≡ (x//4 - y//4)/2 (mod 2).
  - So a hit with an odd sy offset needs an odd relative z, whatever its x and y are.
  - This removed spurious hits, such as screen01's 768:0.
  - It also exposed two real 1994 quirks: the cloud floor's z, and 796:0 (both below).
- **z refinement.** z was refined by coordinate descent on exact-pixel agreement.
  - Lattice items step in 32s and other items in 8s.
  - A move needs a gain of more than 15-20 px; ties keep the structural z.
- **Missed items.** I searched the unexplained pixels, masking the explained ones as unknown, with
  `find_missing`. On top of that I ran `cropsearch.py`, which scans all retail shapes 0-855 inside a window.
- **Hidden ground.** `lattice_fill2` / `fill_objects` add a 301 tile under each unsupported object, but only when the
  tile adds no wrong pixels.
- **Water** (347:16 is flat navy) is plane-filled on the lattice of a seen water tile. Each tile is kept only if it adds
  matches and no wrong pixels.
- **Uniform navy.** The 710, 762, 671 and 685 "navy block" hits matched flat navy anywhere. I dropped them.

## Findings that matter for the build

1. **The 1994 climb is a staircase of 56-unit ledges.**
   - screen01's tiers are 8, 64, 120 and 176: one 48-unit course plus an 8-unit crest each. That is exactly the
     engine's `climb56`.
   - The Avatar's frame there, 1:244 with arms raised, is the climb pose.
   - screen16's pillar-to-plateau step is 32 (a climb32).
   - Our build uses a walkable 4-unit ramp. My proposal keeps a walkable lane outside every camera view, so the
     quest spine does not depend on `climb56`'s flakiness (docs/research/2026-09-25-cave-ascent-jump.md).
2. **screen01's white is the 1994 cloud floor, not retail art.**
   - It is the same 3-frame flat tile that ReconCloud recovered from screen11:
     `/tmp/lv-shots/recon/ReconCloud/art/cloud_floor_f{0,1,2}.png`, 62×32, hotspot (31,31), random frame per
     cell. Patches of screen01 match screen11 at 99 %.
   - 11 tiles are registered exactly in screen01. Its observed pixels are in `art/screen01_cloud_observed.png`.
   - Parity puts it at an odd z relative to the cliffs: local z1, world z57 with dz +56. It sits on 32-unit
     sub-lattices.
   - Our 862 is a different single-frame 63×34 slab with a different texture (`art/cmp_862_vs_1994cloud.png`).
     **Replace 862 with the 1994 frames.** Its TYPEFLAG should be flat (zd 0). 113's 8-unit slab is wrong for it.
3. **796:0 needs an odd z** (25 or 33) for a pixel-exact match in both lake shots, while 796:1 sits at even z.
   - Retail never places 796; frame 0's hotspot is evidently one pixel off.
   - Build it at z-1 (one pixel low) so the stone tops stay walkable (z must step by 0/4/8, per F10).
   - 393:9, 393:11 (screen14) and 122:20 (screen15) also need odd z. They are decoration, and the odd z is recorded.
4. **Lattice offset.** The vignette tiles sit on the retail 127-mod-128 lattice. `build_map_13`'s climb tiles are on
   0 mod 128.
   - Keep each vignette's translation a multiple of 128, so its screen layout stays exact.
   - Align the seams with the climb tiles by hand, or move the nearby climb tiles to 127.

## Per shot

### screen01: summit edge (verify: covered 97.3 %, frame 94.1 %)

- **Tiers in local coordinates:**
  - lower-left terrace: courses at z0, crests at 48;
  - east front ledge: courses at z8;
  - mid plateau: 301 at 64, rim crests 125 at 56, with the Avatar and the skeleton warrior on it;
  - a ledge one tile wide at 120: crests at 112 on 32-courses at 64, with bones, a spear and 522 blood drips on the face (z96);
  - top crag: crests at 168 on 32-courses at 120;
  - cloud at z1, north of the mid plateau's north rim.
- **Unexplained (3,515 px):**
  - 1,862 px in the cloud strip: partial cells and frames that do not match exactly;
  - 183 px of brown smear around the right-hand bones (no retail match);
  - draw-order cases at the bottom edge (369:15, 32:4, 30:4).
- **Placement:**
  - With dz +56 the mid plateau becomes the summit at z120, and the cloud sea lies north at z57.
  - **Pins move:** 208 pad (4096,512)→(4351,1279,120); 209 trigger (4096,128)→(4351,895,120); harpie group-2 eggs
    and trigger. The summit floor north of y 767 becomes cloud.
  - Collides with 18 climb cells (z112-120) and 128 current items (path tiles, colonnade, rim courses).

### screen14: skull ring (verify: covered 93.0 %, frame 89.4 %)

- **Layout:**
  - upper-left plateau at 112, with crests at 104;
  - the path at 80 along the foot of a north face of 26/32/370/566 courses with 138 ledge strips;
  - skull ring 745:0 at z80 on the path (the only z with support), with the Avatar on it at z96.
- **Unexplained (6,160 px):**
  - the mouse cursor (146 px) and the purple UI line on the right edge (240 px);
  - the irregular black-and-white outline of the path's back edge (no retail frame);
  - face draw-order cases.
- The 66:5 spire's base is off-screen and floats at 96. It needs a hidden pillar.
- **Placement:** dz 0, with the ring at world (4159,4895,80). The route uses the path's east end.
  - **Pins move:** harpie group-1 trigger and eggs, to the new x=4864 lane.

### screen15: lake causeway (verify: covered 98.9 %, frame 95.9 %)

- **Layout:**
  - water 347 at 32;
  - shore 128 at 32;
  - NW bank: courses at 40 under ground at 88;
  - causeway north-south at x≈5119-5135 local: 186 tops at 80, 796:1 at 88, 796:0 at 81 or 89;
  - Avatar 1:17 on stone 46.
- **Unexplained (2,028 px):**
  - a 743-px band along the top edge;
  - a red blob (25 px), extracted;
  - a white fragment.
- **Placement:** dz -8. This is the lake at the foot of the climb.

### screen16: causeway landing (verify: covered 96.7 %, frame 94.3 %)

- **Layout:**
  - water at 32, the same as screen15;
  - face courses at 8 and 56 under crests at 104, with the plateau at 112;
  - the Avatar on the 193:0 pillar (top 80);
  - 796 stones running south.
- **Unexplained (3,351 px):**
  - 1994-only white bone pieces: a 66×27 scatter and an 18×19 rib, both extracted. No retail shape 0-855 matches
    (`cs16_bones.json`).
  - lower-left water cells that would add wrong pixels.
- **Placement:** dz -8. It continues 32 east of screen15's line, with the ledge at world (4127,6143,72).

## Proposed route for Map 13

The proposal is drawn in `placement_overview.png`. Coordinates are world (x,y,z).

1. base (4096,10240,0): unchanged.
2. Ramp to (4096,7680,72): 18 risers of +4.
3. Across the screen15 stones, x 4111, y 7487→6607, at 72-80.
4. Across the screen16 stones, x 4143, y 6543→6255, to the 193 ledge at (4127,6143,72).
5. East lane to (4864,6144), then north to (4864,4991,80).
6. West along the screen14 path to the ring at (4159,4895,80), and back.
7. North up the x=4864 lane, 80→116, to (4864,1664).
8. West to (4352,1664,120), onto the south rim crests (top 120) and the summit mid plateau.

Base pins 206 and 207 and EGGCLOUDCLIFFS are untouched. Every moved pin is listed in the vignettes' `pin_moves`.
`test_monster_eggs`, `test_climb_*` and exact_reach must be re-run on the result.

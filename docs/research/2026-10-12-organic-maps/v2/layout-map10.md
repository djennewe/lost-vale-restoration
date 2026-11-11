# Map 10 (The Vale) — macro layout v2 (FableDesigner, 2026-10-12)

Design authority doc for AstraVale. Coordinates in world units (chunk = 512, tile = 128).
Every pin in `map_pins.json` (68 rows) keeps exact x/y/z. Water never leaves the old
lake rectangle 11264-15360 × 15360-20480 (test_monster_eggs monotonicity) — the two
village "springs" below are bank-tile+well features, NOT 347 water, unless the user
approves real water there.

## Why v1 failed at game scale (drive every choice from this)
At game scale (one screen ≈ 970×970 units ≈ 7.5×7.5 tiles) screen20 shows: TWO cliff
faces in ONE frame, three elevation tiers (hut above, yard, drop below), dirt as the
MAJORITY material (62-77% in village shots), a ragged dithered dirt↔rock boundary, and
4+ props/figures. v1 at the same scale shows: one flat plane, zero elevation change,
rock-majority ground with small square-edged dirt specks, a uniform 2-course wall far
away, ~0.5 props. Fix = composition + elevation + material inversion, not more noise.

## Region plan (1 char = 1024 units; x → 0..24, y ↓ 0..31)
```
     x 0    4    8    12   16   20   24
y  0  ^^^^^^^^^^^^^CCCCC^^^^^^^^^^^^^^   ^ = outer mountain backstop (non-walk)
   2  ^^^^^####..TT.TT..####^^^^^^^^^^   C = catacomb facade, T = pads/triggers 204/205/212/213
   4  ^^^##.....#####.......###^^^^^^^   # = cliff band / ridge arm (walkable tops T1)
   6  ^^^#.w............#......##^^^^^   w = west spring well (5632,6144)
   8  ^^^#.HHH..........#..GGGG..#^^^^   H = Hoskuld village basin, G = Gunnar ravine village
  10  ^^^#.HHH....r.....##.GGGG..#^^^^   r = ruins cluster (10240,10240)
  12  ^^^##....._S______.##......#^^^^   S = Ezrekal's shack (12800,12544), _ = open scrub plain
  14  ^^^^#.....____________....##^^^^
  16  ^^^^#..m..~LLLL~......O)..#^^^^^   L = lakes, O = Sacred Circle (20415,16831), ) = horseshoe crest
  18  ^^^#...mm.LLLLLL......##..#^^^^^   m = mushroom garden (9216-10752, 18432-20992)
  20  ^^^#......LLpLLL..........#^^^^^   p = pier (foot y=20480)
  22  ^^^#vvvv..............E...#^^^^^   v = lava field, E = temple approach + pad210/trigger211
  24  ^^^#vGv###...####...###...#^^^^^   G(v row) = cliff gate 114 (7168,23552,8), ### = south scarp
  26  ^^^^####..BB64646464......#^^^^^   B = Ragnar bag drop (16447,25727,64); 64 = z=64 shelf
  28  ^^^^^^^P..6464646464....##^^^^^   P = Passage Plant terrace (12800,29440,64)
  30  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

## Elevation tiers (z per region, ramps)
| Tier | z | Where | Edge treatment |
|---|---|---|---|
| T0 valley floor | 0 | scrub plain, villages, lake shore, lava approach | — |
| T1 ridge arms | 48 | arms separating basins: (8600-9800, 3500-13500) N-S spine; (17400-18600, 5000-16000) east spine; village back walls | 1-course jagged face, 125 crests picked by role; earth ramps 256 wide where roads cross: (9216,11776), (17920,10240) |
| T2 plateaus | 96 | Gunnar back wall (21800-23000, 6000-10000); Sacred Circle horseshoe crest (20800-22000, 15800-17400) — crest BEHIND the circle (NE), circle itself stays z=0 | 2 courses, spires on top |
| T3 south shelf | 64 | y 24500-30500 between x 11000-18500; holds bag drop + Passage Plant (both pinned z=64) | ramp up at (14848, 24320), 384 wide |
| T4 backdrop cliffs | 96→288 | NW quadrant x<3500 y<12000 tallest ("great cliffs to the NW", EZREKAL.UNK:1707); whole map rim | terraced 48/level, run lengths 1-3 tiles (retail median 128-192), 497/498 backstop straight behind |

## Regions in detail
1. **North catacomb front (10800-14800, 1200-3000).** Pads 205 (12800,2560) /
   212 (13824,2560), triggers 204 (11904,2048,1) / 213 (12800,1792,1). Build a ruined
   temple facade INTO the north cliff: two rock spurs (T1, z48→96) framing the pad
   cluster, fallen 290/296 panels and a toppled 293 column half-buried in dirt.
   **First view at pads 205/212:** facade up-screen behind, open scrub falling away
   down-screen, road heading south, spires silhouetted on the T1 arms left and right.
2. **Hoskuld village (4300-7900, 6700-10900).** Basin: dirt floor **65-75%** (material
   inversion — dirt body, rock at edges only), enclosed N and W by T1 arm + T4 NW
   cliffs; open to SE. Huts get attached dirt yards (ragged 386 boundary, 2-4 tiles
   beyond walls), blue-pot stacks against walls (screen19), log piles, one campfire
   commons at (5376,9216) (screen20). Fenced crop garden (649/650 rows, stone posts +
   iron rail, screen22) at (6400,8448), 640×512. Spring: well prop + 126/128 damp
   ring at (5632,6144) ("northern most water hole", ATLI.UNK:1603) — dry bank tiles.
   NPCs 100-106,115 all stay put; keep 1-tile clearance round each start/leash.
3. **Central scrub (9500-16500, 10500-15200).** The open-space lung. Mostly rock with
   large soft-edged dirt sheets (patch radius 600-1200, NOT per-tile noise), ruins
   cluster at (10240,10240) ("cool fallen ruins", Synopsis p2), Ezrekal's shack
   (12800,12544) with its own dirt yard + potion shelf pins at (13696-13760,12800,4).
   Sightline: from the shack door (faces S) the lake and pier are visible down-screen.
4. **Southern lakes (11264-15360, 15360-20480).** 2-3 lobes; pier foot fixed y=20480;
   passage stone (13888,18368,8) on a bank islet; zombie eggs (13792-14016,
   18271-19936, z=8) must land on 128/126 bank tiles (z=8 tops). Shore = 128 (rock
   side) / 126 (dirt side), one 347 ripple band, rails on all deep edges.
5. **Mushroom garden (9216-10752, 18432-20992).** "Primary mushroom garden" (Synopsis
   p3 §8): 625 giants + 466 clusters + 794, dead tree 75, iron-railed beds
   (screen22/18), on a dirt sheet. Density target: retail Plateau ~10 props/100 tiles,
   clustered R 0.2-0.3.
6. **Gunnar village (18400-22200, 6300-10000).** Ravine composition (screen20): two
   cliff arms (T1 west spine, T2 back wall east) converging NW→SE with the village in
   the 1500-2500-unit slot between; dirt floor 60-75%. NPCs 107-114, chest
   (21024,8832), potions pins stay. Red keep (glob 573) is off-style — **flag to user:
   replace with great-hut group or keep** (do not silently delete).
7. **Sacred Circle terrace (19800-21800, 15800-17600).** Circle of 9 stones around
   Sacred Rock 863 (20415,16831,0), SHADES egg (20480,17152), root 869 (21376,16640)
   — all z=0, UNMOVED (decision D deferred). Horseshoe T2 crest wraps NE behind it so
   it reads as a promontory without moving a pin; open sightline W across the lake.
8. **Lava field (6000-10500, 20700-24300)** on the gate approach (THORDIS "cross the
   liquid fire"; screen21): 409 noise-masked pools with crust-edge frames, dark 122/125
   rubble ridges, skull-post wooden pen prop at (8960,21760), eye-serpent eggs none
   (no new monsters). Keep a clean 384-wide walk lane from road to gate: path from
   (9728,20992) → (7168,22784). Never f33 within 2 tiles of the lane.
9. **Cliff gate (7168,23296-24064, z=8).** Pad 206 + egg (7168,23296,8), gate 114
   q170 (7168,23552,8), trigger 207 (7168,24064,8). Gate set in the south scarp face.
   **First view at pad 206:** gate shelf, lava glow up-screen-right, scarp behind.
10. **Temple approach (17800-19200, 22000-24000).** Pad 210 + ENDGAME egg
    (18432,22784), trigger 211 (18432,23552) → Map 18. Screen17 composition: a 70-cobble
    stair descending S between stone edges, 38 gargoyles flanking at (18176,23296) and
    (18688,23296). **First view at pad 210:** gargoyle stair down-screen, Sacred-Circle
    crest on the horizon up-screen.
11. **South shelf (T3, z=64)** holding bag drop + Passage Plant ("farthest corner,
    south and west", THORDIS.UNK:1203 — the plant terrace is the SW end of the shelf).
    Barren, bone scatter, harpie-nest dressing ("left out on the rocks for the
    Harpies").

## Roads (meandered earth bands, width 1-3 tiles, Chaikin)
- N pads (12800,2560) → Hoskuld (6400,8960): via (10752,5632).
- Hoskuld → shack (12800,12544) → pier (13312,20480) east bank.
- Shack → Gunnar (19968,8448) via T1 ramp (17920,10240).
- Gunnar → Sacred Circle (20480,16640).
- Pier/west bank → mushroom garden → lava lane → gate 206.
- Sacred Circle → temple approach pad 210.
Roads are dirt (4/386), NOT 425 cobble. 425 only at the gate shelf and temple stair.

## Material legend
| Code | Material | Shapes |
|---|---|---|
| rock | grey cracked rock | glob 397/2241 fill, 301 f0-6 tiles; f7-37 rough ≤8%, as the tile itself (never an overlay) |
| dirt | brown earth | glob 875, 4 f14/15/30-33 |
| edge | dirt↔rock | 386 corner set (26 frames; disputed frames 5/6/10/14/15 checked by eye) + retail transition globs 455/448/1433/627/628/264 for whole chunks |
| water | lake only | 347 (f16 deep, ripple f0-13 shallows), 128/126 banks, rails |
| lava | fire field | 409 (f0/15/20/30 crust edges, f5/10/25 interior, f33 only ≥2 tiles off-lane), 122 shore |
| cliff | faces | 26-32 family runs 1-3 tiles, 29 posts on convex corners, 125 crests role-picked, black frames only on back faces |
| props | dressing | 66 spires, 625/466/794 mushrooms, 75 dead trees, 666 logs, 524/526 rubble, 235/237/332 bones (clusters, hash-seeded, R≈0.3, ~8-10/100 tiles near features, ~2 in open scrub) |

## Acceptance (judge at game scale)
Render 970×970 windows at scale 1, ×3 nearest:
- (4800,8700) vs screen20/19: dirt-majority, two faces in frame, yard boundary ragged.
- (12900,18200) lake pier vs screen02: jagged blue rim, no stair-steps.
- (8200,22400) lava vs screen21: three materials in one frame.
- (20300,16600) Sacred Circle: crest behind, open west.
- Every window: ≥3 props or features; no 512-period repeat visible.

---

# Implementation recipe (self-contained — no v2 Vale mock exists; AstraVale died before rendering)

## Generator pipeline (order matters)
1. **Corner lattice.** Label every 128-unit lattice corner R/E/W over the whole map.
   - Base label from the region plan above (regions → polygons), then perturb the
     polygon boundaries with domain-warped value noise so no boundary follows a
     chunk line. Dirt sheets: distance-to-region-centre < r*(0.75+0.5*noise) with
     r = 600-1200. Roads: distance to the meandered polyline < 120+150*noise.
   - Determinism: every random draw = hash(tile_ix, tile_iy, salt) — the
     splitmix-style hash in /tmp/lv-maps-research/CloudMapsProposal/mock17.py:41-54
     is a good reference implementation. NEVER a sequential RNG.
   - Repair pass: flip labels until every 2×2 corner pattern is one a transition
     frame can draw (no checkerboard diagonals, no NW-only water); the loop in
     /tmp/lv-maps-research/ValeProposal/mock_vale.py:181-192 shows the idiom.
2. **Ground emission per 512 chunk.**
   - Uniform R chunk → one glob egg from pool (397,397,397,2241), hash-picked.
   - Uniform E chunk → glob 875 (hash-mix a minority of retail transition globs
     455/448/1433/627/628/264 for ragged patch chunks — that is retail Map 21's
     idiom). Do NOT use 434/435/437 (the v1 mock's speckled "burnt" dirt — see
     crit_map10_village.png right panel — came from that pool).
   - Uniform W chunk → glob 262.
   - Mixed chunk → 16 direct tiles, no glob underneath (overlay order undefined):
     301 f0-6 / 4 f14,15,30-33 / 347 / 386 via corner table / 128 (rock bank) /
     126 (dirt bank) via FBANK corner table.
   - Corner tables: F386 + FBANK in /tmp/lv-maps-research/ValeProposal/mock_vale.py:25-40
     (agreed frames only); RefArtCatalog.md §5 has the independent second table.
     Frames 386:5/6/10/14/15 and 128:4/8/16 are disputed — verify by eye first.
3. **Lake.** Blob union clipped to 11264-15360 × 15360-20480; pass-1 blob set that
   fit all pins: (13900,18400,1150),(12700,17500,850),(12050,16250,520),
   (12750,19650,600),(14700,16900,520); force-water (13568,17920)-(14336,18816) and
   (13568,18560)-(14208,20480) keeps the pier wet; pier foot y=20480. Banks must use
   **128 grey on the rock side** — the v1 lake read as a floating mud causeway
   because 126 brown dominated (crit_map10_lake.png). 347 ripple band on shallows,
   rails on every deep edge (~166), drop props 738(12800,16640), 299(14431,19135).
4. **Rim/cliffs.** BFS depth-to-void per tile; NW band depth 2-7 tiles terraced
   48/level to 288; SE 0-2, ≤96. Faces 26-32 family with run lengths 1-3 tiles,
   29 posts on convex corners, textured frames only on camera-facing sides, 125
   crests picked by role (fix CREST_FRAMES), straight 497/498 backstop behind.
   Protected cells: every pin + 3-tile margin (NPC/egg/teleport), 1-tile (roads).
   Interior T1/T2 ridge arms use the same walker along the arm polygons of the
   region plan, with 256-384-wide earth ramp gaps at the road crossings
   (9216,11776), (17920,10240), (14848,24320).
5. **Lava field** (region 8): same corner-lattice approach with L label; 409 crust
   frames at boundaries, interior f5/10/25, f33 ≥2 tiles from the protected lane
   (9728,20992)→(7168,22784); 122/125 rubble ridges hash-scattered.
6. **Villages/dressing** (regions 2/5/6): earth yards (dirt sheets attached to each
   hut), fenced 649/650 crop gardens, clustered scatter via Poisson-disc seeded by
   tile hash, cluster R≈0.2-0.3, density ~8-10/100 tiles near features, ~2 in open
   scrub. Clusters keep off pins, roads, ramps.
7. **Void plates last**, then invisible curbs on every walkable void edge.

## Item budget (measured in pass 1, ValeProposal §6)
Today 9,797 raw; naive all-tiles ≈ 26.8k (too close to the 32,510 objID cap).
Target ≈ 20k: uniform chunks as globs, only mixed chunks tiled, random patches as
transition globs, rim band ≈ 4.6k replacing ≈ 1.6k old rim. Decision A (custom
GLOB.FLX sixth artifact) halves it to ≈ 10-12k — user call before building.
Add the per-map item-count gate (ceiling 25k) to build_all_maps in the same pass.

## Tests that must re-pass
test_route_reach (13 targets; pass-1 terrain prototype passed all 13),
map_walkability, test_schedule_destinations (loiter leashes on floor),
test_monster_eggs (water seek + knockback rails; z=8 zombie eggs must sit on bank
tiles), test_paint_cycles, test_map_roundtrip, test_endgame_hatch_box,
test_art_props, test_climb_width, test_map_edges; re-derive map_pins afterwards.
Flagged user decisions: A (glob budget), red keep replacement, real spring water,
D (Sacred Circle promontory — layout already fakes it with the horseshoe crest).

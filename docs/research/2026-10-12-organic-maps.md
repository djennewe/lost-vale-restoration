# Organic LV maps: diagnosis and proposal (2026-10-12)

Research only. No builder, artifact or test was changed. Seven research
passes fed this: reference-art catalogue, retail terrain idioms, terrain
technique, and per-map proposals for Cloud (13/17), Vale (10), interiors
(9/11/18) and the modified base maps (8/39). Mocks were made by importing
each builder, post-processing its item list in `/tmp`, and rendering with
`iso_render`. They are **offline renders, not in-engine**. The picked renders
are in `2026-10-12-organic-maps/`.

**Trap found along the way:** `shared/data/u8-install/STATIC/FIXED.DAT`, which
`iso_render.py`'s CLI uses by default (`:195-198`), is **our installed build**,
not retail. The pristine retail copy is `STATIC/FIXED.DAT.bak` (or the
`u8-pkg-expanded` copy). Every retail number below comes from the pristine
file.

## 1. Why every LV map looks like wallpaper

There are four causes, shared across the maps. Each one is measured.

1. **One glob per 512-unit chunk, and the wrong glob.** A glob is a stored
   4×4 block of tiles, placed by one map item (an egg).
   - The LV maps draw on 1-5 distinct ground globs. Retail outdoor maps draw
     on 74-229.
   - As a result, 91-98% of LV ground tiles repeat exactly 512 units away.
     Retail's figure is 56-65%.

   | Map | 512-unit repeat | Distinct ground (shape:frame) | Ground globs |
   |---|---|---|---|
   | 9 | 98% | 20 | 45 |
   | 10 | 91% | 69 | 40 ×1344, 43, 55 |
   | 11 | 91% | 48 | 65, 42, 397, 480, 802 |
   | 13 | 97% | 22 | 52, 49 |
   | 17 | 94% | 18 | 65 only |
   | 18 | 95% | 21 | 65 only |
   | retail 3 / 8 / 50 | 65 / 57 / 56% | 205 / 186 / 199 | 73 / 91 / 22 |

   - **Glob 40** fills Map 10 (`build_map_10.py:107`, `:357-380`). It is
     shape 242, a mossy Tenebrae flagstone, including its paving↔grass
     *edge* frames. Retail places it 17-21 times. The diagonal green stripes
     in the Vale are glob 40 repeating.
   - **Glob 65** fills Maps 17 and 18 and Map 11's halls (`lv_furnish.py:57`).
     It is a checker of shape 35 frames 2/3, which retail uses only as E/W
     edge frames.
   - Across LV, 37-42% of ground cells are edge frames used as fill. Retail
     uses 6-25%, and only where two materials actually meet.
2. **Outlines are 512-quantised rectangles.**
   - `lv_landscape.rim()` (`:118-206`, `CHUNK=512`) builds every outer wall.
     `room()` (`build_map_17.py:147-168`) and `stone_room`
     (`build_map_11.py:229`) build the rooms.
   - LV cliff runs have a median length of 3,072 units, and every run is at
     least 8 tiles. Retail's median is 128-192 units, and 60-75% of its runs
     are 2 tiles or shorter.
   - Retail hides the map's rectangle five ways: a ragged walkable outline;
     a "mountain-top" sheet that runs past the camera; black 334/564 caps in
     caves; water or void that runs to the edge; and an invisible 497/498
     backstop behind a jagged visible face.
3. **Frames come from linear position formulas, which read as stripes.**
   - Examples: `(x//T*5 + y//T*3) % n` (`lv_landscape.py:255`),
     `(i + z//48 + phase) % 7` on cliff faces (`:91`, `:102`), and `i % len`
     on Map 9.
   - `CREST_FRAMES` treats 125 f0-6 as "plain grey". They are actually
     directional edges and corners, so `(x+y)%7` scatters edges facing in
     random directions along the crest.
4. **Scatter is sparse and evenly spread.** These are props per 100 walkable
   tiles; R < 1 means the props cluster.

   | Map | Props per 100 tiles | Clustering R |
   |---|---|---|
   | LV 10 / 11 / 13 | 1.0 / 0.2 / 0.1 | — |
   | Retail cave | 3 | — |
   | Retail lava | 7 | — |
   | Retail Plateau | 10 | 0.2-0.3 |
   | Retail coast | 17 | — |

   The LV props are hand-typed lone dots. Map 39's hedge, for example, is 40
   oaks on a ruler line, and its bushes cycle frames 0,2,1,3.

## 2. What the 1994 record says the maps look like

Every screenshot is accounted for in the RefArtCatalog report; the
highlights:

- **The 1994 maps are stock retail terrain.**
  - The grey cracked rock in screens 01/04/05/10/14/16/17/18/19/21 is pixel
    for pixel **301 f0-6**, retail's cave floor (glob 397, 1,600 eggs).
  - The brown earth is **4 f14/15/30-33** (glob 875).
  - Their ragged boundary is **386**, a 26-frame corner set.
  - Art List v2.5 lists **Cloud World as the only new terrain**.
- **The Vale is barren rock and brown earth, not grass.**
  - "once lush and beautiful, but is now barren and desolate" (Plot v1.2
    p1 §7; Walk Through p1 §VII).
  - Green appears only at the ending: "Gods released, water flows, green
    plants" (Plot v1.2 p3 §19).
  - Green covers at most 4% of any shot, and that green is crops (649/650,
    screen22).
- **Cloud City has no walls.**
  - screen11 shows a continuous flat cloud floor (matching 862). The
    obelisk stands on white drums with orange bands, ringed by smooth white
    pillars with coloured gem caps.
  - screen12 shows a raised lavender-white marble walkway with gold trim,
    lined both sides by white drum columns with gold bands; a throne nook
    with two 223 thrones; and gold small-brick patches lapped by cloud.
  - Art List v2.5: "take Bob's red stone architecture and turn it white and
    gold", where Bob's red stone is **233 f2**. "Cloud-like terrain.
    Collapsing ground."
  - EZREKAL.UNK:1349-1352: "White as the clouds the walls are and bright as
    gold the streets are."
- **The Cliffs (13)** are 301 ledges climbing in tiers, with bones, a skull
  ring (745) and spires. At the top, **the edge drops into white cloud, not
  black** (screen01). At the base are stepping stones (186/796) over dark
  water (screen15/16).
- **The interiors are caves.**
  - Map 18's sanctum is a cave shrine on 301 with craggy walls; the altar is
    retail **550:0** (screen04).
  - Map 11's Fire wing is a cave over black void, with a banded pillar in
    lava (screens 05/07).
  - Map 9 is plausibly screen10: a 240/290/296 tomb-kit dais with claw
    statues and ghouls [INFERENCE].
- **Maps 8 and 39 have no 1994 shot.** They should stay retail.

## 3. Shared engine and build constraints

Every proposal below has to fit these.

- **Object-ID cap.** Map items take IDs from 256-32766
  (`object_manager.cpp:74`), and every FIXED item gets one when the map
  loads. Glob contents are created only near the player.
  - Laying Map 10's ground tile by tile would be about 34.7k items, **over
    the cap**.
  - Maps 9/13/17/18 can afford loose tiles. Map 11 would reach about 18k.
  - Add a per-map item-count gate to `build_all_maps` (suggested ceiling
    25k).
- **Overlay order is undefined.** A 386 or 4 tile laid over a 301 glob
  floor has no defined draw order: both are SI_DRAW and neither is SI_OCCL
  (`sort_item.cpp:145-181`). Mixed chunks therefore need direct tiles with
  **no glob under them**.
- **Footprints.**
  - Shape 862, the cloud tile, has a 128×128×**8** footprint, so a cloud
    floor at z=0 buries every pinned z=0 item. It needs a flat twin.
  - Shape 9 carries `SI_ROOF` and is listed in `test_map_hygiene`'s
    `CEILING_SHAPES` (`:69`).
- **Determinism.** Randomness must come from a hash of each tile's
  coordinates plus a salt, never from a sequential RNG stream. That keeps
  `ARTIFACTS.sha256` stable and keeps a local edit local.
- **Geometry.**
  - Item boxes are half-open; a walker steps only 0/4/8; void plates are
    placed last.
  - A jagged face can open a one-body-width aperture, so keep a continuous
    497/498 backstop behind it (`.claude/rules/map-geometry.md`).
  - Open cloud or ground at z=0 can be walked off, so every edge needs
    invisible curbs.
- **Water.** Shapes 347 and 351 cannot be walked. 564 can (it is LAND).
  Standing on 347 drowns a body that gets knocked back there.

## 4. Shared tooling (do this first)

One module, `agents/map-populator/src/lv_terrain.py`, which every builder
calls. The three proposals that drafted an API converge on this shape:

```python
Material(name, fill=[(shape, frame, weight)], trans=shape)   # trans: a 26-frame corner set
Terrain(seed, mask_txt, legend, keep_out)   # ASCII mask per map, one char per 128 or 512 cell
  .outline(band)       # noise erosion inside a band; keep-out radius; keep arrival component
  .corner_labels()     # mask + domain-warped noise -> material per lattice corner
  .ground_items(globs) # uniform chunk -> 1 retail glob egg; mixed chunk -> 16 direct tiles
  .rim(flush)          # jagged cliff walker (retail run-length histogram, 27/28/30/31 offsets,
                       #   29 posts on convex corners, lips on seams, 7/8 frames only on back faces,
                       #   straight 497/498 backstop)
  .tracks(polys, w)    # Chaikin/Catmull meander, width 1-3, drawn as earth not 425
  .scatter(kit, per100, R)   # clustered Poisson, hash-seeded, keeps off pins and tracks
cave_mask(rects, force, line) / cave_shell(cells)  # interiors: noisy outline, 301 floor, 26-32 family
```

- **Corner tables.** The frame-to-corner tables for 386, 128, 126 and 347
  are derived from pixels in the agents' scratch scripts.
  - The two classifiers disagree on 386 frames 5, 6, 10, 14 and 15 and on
    128 frames 4, 8 and 16. **Check those by eye before shipping.**
  - Shapes 4 and 9 share Origin's identical 26-mask layout, so one table
    covers both.
- **Fix in the same pass:** `CREST_FRAMES` / `crest_tile` (pick the frame
  by role), and the misnamed `lv_shapes.py` entries: 9 is a ground
  transition, not ROCKY_RUBBLE_CEILING; 128 is a rock↔water shore; 186 is a
  floating stone, not STALACTITE; 300 is a floor, not BOULDER_PILE; 409 is
  lava.
- **Decision A, the glob budget for Map 10** (see §6). Without new globs,
  Map 10 lands at about 20k raw items: uniform chunks as retail globs, mixed
  chunks as tiles, ragged patches from retail's 19 rock↔earth transition
  globs. With a custom `GLOB.FLX`, it lands at about 10-12k and is drawn the
  way retail draws: a Wang prototype needed 140 unique globs for the whole
  map.

## 5. Per-map proposals

Priority follows the user's complaint and the size of the win.

### Map 17 Cloud City (P1: looks nothing like the shots)

What's there now: six grey-stone walled rooms (957 wall pieces) on glob 65
flagstone, with grey fluted columns, tapestries and lamps. Cloud tile 862
appears only on 78 tiles of three islands nobody can reach.

![Map 17 obelisk before/after](2026-10-12-organic-maps/m17-obelisk-before-after.png)
![Map 17 proposed layout](2026-10-12-organic-maps/m17-mock-full.png)

- **Delete:** `room`, `build_hall_corridors`, `RELIEF_LINES` /
  `accent_reliefs`, `_PLATE_Y_FIX` / `_reposition_plate`, and every wall,
  tapestry and lamp.
- **Ground.** An open cloud sea (noisy unions of discs and capsules) over
  void, with gold-brick streets and plazas, and raised white-marble walkways
  (**37 f11/13/14/15**) with gold kerbs (**45 f3**, **84 f4**).
- **Furniture.**
  - Drum colonnades along the walkways.
  - A 10-pillar ring around the obelisk, on a drum cluster.
  - A throne nook with **223** thrones, rubble 524 f2/3 and blue vases
    183 f2.
- **Kept at their exact coordinates:**

  | Placement | Position |
  |---|---|
  | Teleport trigger 208 | (5376,11520,0) |
  | Pad 209 + REAPPLY egg | (5376,11136) |
  | Scroll 864 | (3328,1536,8) |
  | Shield halves 870 | (6208,1568) and (7232,1568) |
  | Obelisk 861 | (4095,7167,16) |
  | Plaques 614 | qualities 55/68/69/70 |
  | Hall A / Hall B route goals | unchanged |

  The mock moved one rubble box off half 1; no decor box may overlap a pin.
- **Edges.** Invisible curbs on every cloud edge, about 614 pieces.
  Estimated total ≈4.3k items against 5.1k now, so paint cost goes **down**.
- **New art (art track; the next free ID is 874):**

  | ID | Item | How |
  |---|---|---|
  | 874 | Flat cloud | 862's pixels on a flat 4×4×0 row (donor 71 or 3, not 35). Optional scalloped-edge frames (screen13). **Prerequisite for everything else.** |
  | 875 | Gold brick | Recolour of 34. Reference: screen12 lower left. |
  | 876 | White/gold drum | Recolour of 233 f2. Reference: screen11 base. |
  | 877 | Banded round column | 2×2×10, drawn new. |
  | 878 | Gem-capped pillar | 5 frames, one per gem colour. |
  | later | Cloud↔void and cloud↔gold edge set (the 1994 "Cloud globs"), a white stele, collapsing cloud | — |

  Interim stand-ins: recoloured 233 f2/f3, plus 346 for the gems.
- **Tests that follow:**
  - `test_art_props` expects 78 × 862 south of y 11776.
  - `test_map_edges` and an `exact_reach` flood.
  - `test_route_reach`, `test_map_hygiene` (void ratchet),
    `test_paint_cycles`, `test_sanctum_clearance`.
  - Re-derive `map_pins`.
- **Decision B:** move the whole city so the obelisk's foot sits at
  MAGNET's hard-coded target (15615,19839,120) (`MAGNET.UNK:225`)?
  - For: it is where 1994 put it [INFERENCE], and it removes the lv-patched
    pop-target blocker.
  - Against: every pin has to be re-pinned, including the literal that
    `derive_map_pins` greps.

### Map 10 The Vale (P2: biggest area, most visible)

![Map 10 ground, glob 40 vs rock/earth autotile](2026-10-12-organic-maps/m10-ground-before-after-close.png)
![Lake quadrant after](2026-10-12-organic-maps/m10-lake-after.png)
![Village after](2026-10-12-organic-maps/m10-village-after.png)

- **Ground.**
  - Replace the rectangle table `TERRAIN` (`:284-330`) with a 48×63 ASCII
    mask in which each lattice corner is R (rock), E (earth) or W (water).
  - Fill: rock = glob 397 (mixed with glob 2241), earth = glob 875,
    transitions = 386. In village yards, earth is 60-75% of the ground.
  - Earth comes from meandered bands along the old `TRACKS`, from hut
    yards, from wet rings round the water, and from low-frequency noise.
  - Delete the 425 tracks and the `_check_tracks` cell check.
- **Lake.**
  - Two or three noisy lobes ("the southern lakes"), **clipped to the old
    rectangle** (11264-15360 × 15360-20480), so every distance
    `test_monster_eggs` measures can only grow.
  - The pier foot stays at y 20480.
  - 128/126 bank tiles, a 347 ripple band, and rails generated on every
    deep-water edge (about 166, replacing the 92 hand-listed ones).
  - Delete the two props that would land on banks: 738 at (12800,16640)
    and 299 at (14431,19135).
- **Rim.**
  - A tile-resolution cliff band built from BFS depth to the void.
  - North-west: 2-7 tiles deep, terraced up to 288 ("great cliffs to the
    Northwest").
  - South-east: 0-2 tiles deep and at most 96 high, so it never hides the
    player.
  - The band never covers a pin, and keeps a 3-tile margin round NPCs,
    eggs and teleports.
- **Villages.**
  - Drop both rectangular palisades and the shape-3 "spring" tiles.
  - Earth yards round the huts.
  - Replace the bush grids with 649/650 crop rows in small fenced gardens
    (screen22).
  - Glob 573, the red keep, is off-style for screen19 (noted only).
- **Dressing.** Clusters instead of dots: spires 66 with rubble and 466
  mushrooms, 625 giant mushrooms, dead-tree groves 75, logs 666. Raise the
  density toward retail's roughly 10 per 100 tiles.
- **Kept.** All 65 positioned pins in `map_pins.json` are present in the
  full mock at the same shape and x/y/z. The lists are in the ValeProposal
  report: teleports 204-213, REAPPLY/PLANTTEST/ENDGAME/SHADES eggs, monster
  groups 1-8, NPCs 100-116, and the quest items.
- **Routes.**
  - TerrainTechnique's prototype was flooded with the `test_route_reach`
    engine: **all 13 Map 10 targets are reachable**.
  - The ValeProposal mock's cliff band takes 1,728 floor tiles out of the
    walkable area and has not been flooded yet.
- **Optional, quest-sensitive:**
  - Raise the Sacred Circle onto a promontory (THORDIS.UNK:858). This
    changes pinned z, so `test_uc_shades` must follow.
  - A lava strip on the cloud approach ("cross the liquid fire", screen21).
  - A waterfall (screen09). No shape has been identified for it.

### Map 13 Cloud Cliffs (P3: low-risk re-skin)

![Map 13 summit before/after](2026-10-12-organic-maps/m13-summit-before-after.png)

Same x/y/z for every walkable tile. Curbs, eggs, teleports and
`CLIMB_WAYPOINTS` are untouched.

| Part | Now | Proposed |
|---|---|---|
| Valley | glob 49 (shape 242) | glob 397 (301) |
| Climb path and lanes | shape 3 grass | shape 4 brown earth, with 425 at the foot (shape 4 is SI_DRAW) |
| Summit ground | — | Noise mix of earth and flat cloud (874), gold brick in the corner by pad 209 |
| Summit dressing | 249/113 colonnade | trunk 74 f1, spires 66, 65, bones |
| Top edge | black | cloud, not black (screen01) |
| Later | — | Irregular 66/193 outcrops on the valley floor, clear of the climb cells |

Avoid 435-438: they look like snow but are SEA|DAMAGING foam.

### Maps 9, 11, 18 Interiors (P4)

![Map 9 before/after](2026-10-12-organic-maps/m09-before-after.png)
![Map 18 sanctum before/after](2026-10-12-organic-maps/m18-sanctum-before-after.png)

- **Shared change:** `cave_mask` + `cave_shell` as described in §4.
  - Floor: glob 397 on full chunks, loose 301 tiles on partial ones.
  - Walls: the 26-32 family, with textured frames facing the camera and
    black frames on back faces, 29 posts at corners, and 334 caps at z=96.
  - Apertures of at least 192 units.
  - Worked stone moves from the Tenebrae town kit (10/15 walls, `column()`,
    tapestries, lamps, urns, pews) to retail's **tomb kit**: 290/296 walls
    (the same footprints as 10/15), 294 for 47, 293 columns, 240 arcade
    slabs, 352/556 floor, 423 fringe, 38 gargoyles, 550 altar.
    `gate_coverage` checks boxes, not shape numbers, so the swap is
    geometry-neutral.
- **Map 9.**
  - Mocked: three rectangular boxes become one cave.
  - `exact_reach` flood: every pin reached from pad 201, 0 leak.
  - Records go from 633 to about 885, before void plates.
  - Shape 796 (a floating icicle rock) becomes 66 + 152.
  - Pad 201 still needs a rock face due north (the `arrival_corridors`
    check).
- **Map 11**, by wing:

  | Wing | Change |
  |---|---|
  | Earth | Three chambers joined by winding 384-640-wide passages, replacing the straight walls at `:391/393` |
  | Fire | Noise-masked 409 lava with crust frames and a 122 shore, never f33 near a walk line. Causeways become rock ridges on the same lines, so `LAVA_MARGIN` holds. Drop 318 (it is a fire-pit grate, not lava). Two 453 posts and a 122 mound at the Fire pillar (screen07). |
  | Water | 347 pools, 128 shores, 72 spikes |
  | Air | 469/472-edged islands, with 193/186 isles over 347 or a walkable 564 floor |
  | Corridors | Winding passages centred on the same doorway spans |
  | Hub, pillars chamber and pad room | Re-skinned in the tomb kit |

  - Never add a quality-299 shape 66, a 596 or an 865: COLPUZZL and
    REAPPLY filter on them.
- **Map 18.**
  - The sanctum becomes a cave shrine on 301, with walls on the **same
    lines** in three 48-unit courses.
  - Outcrops stay clear of lane x 2700-2880.
  - The gods go on 240 plinths, with Doloras's plinth max at x=3136.
  - The crack line y=6143 **stays 15/47**: TEMPLENT/CRACKHNT and
    `BREACH_PIECES` key on those shapes.
  - Outer hall in the tomb kit; exterior a rock court with gargoyles and a
    70-cobble approach (screen17).
- **Optional art:** a screen04-accurate god plinth, and an 865 f2 redraw
  (screen07 shows a banded dark column with a red cap, not a flame)
  [INFERENCE].

### Maps 8 and 39 Modified base maps (P5: polish)

- **Map 8 is retail** apart from 11 LV records. Three fixes:
  - Pale slab 71:0 → **71:9**, Map 8's own frame (`build_map_08.py:466-469`).
  - Delete the 301 z=1 slab in Mythran's dining room (`:484-487`).
  - Optionally delete the invisible, redundant slab under trigger 200
    (`:428-431`).
- **Map 39: the LV dressing is what looks systematic.**

  ![Map 39 before/after](2026-10-12-organic-maps/m39-before-after.png)

  - Oak hedge: give the y values a non-periodic wander, keeping max-y at
    least ~20343 for `test_map39_south_edge`.
  - Bushes in clumps.
  - Swap the 4 rock spires for 434 clumps on retail dirt-patch grass frames.
  - Replace the visible void band with a lower retail forest and a moat
    bank.
  - Fix the stale docstring at `:43-44`.

## 6. Decisions for the user

| # | Decision | Options | Recommendation |
|---|---|---|---|
| A | Map 10 ground budget | (1) Retail globs + loose tiles, ≈20k items, no new artifact. (2) Custom `GLOB.FLX` as a sixth build artifact, ≈10-12k items, retail's own method. It needs a build step, install copy + `.bak`, a hash line, and pointing `GlobReader` at it. | (2) if a sixth artifact is acceptable; otherwise (1) is workable |
| B | Cloud City location | Keep the current pins, or translate the city to MAGNET's 1994 obelisk coordinate | Keep for now; revisit when MAGNET is wired |
| C | Map 11 Water/Air hazard | Real 347 water / sky void (lethal, behind margin tests) or a dry bed / walkable 564 | Lethal with margin tests: closer to retail and to 1994 |
| D | Sacred Circle promontory | Leave at z=0, or raise it (re-pin, `test_uc_shades`) | Defer until after the ground pass |
| E | Collapsing cloud ("Avatar dying in cloud terrain") | Design decision before any art | Defer |

## 7. Suggested order

1. `lv_terrain.py` + crest-frame fix + `lv_shapes.py` renames + the ID-count
   gate + a pristine-retail default in `iso_render`, all verified against
   the current maps. The renames and the ID gate change nothing visible;
   the crest fix changes every cliff top.
2. Art 874 (flat cloud). Then Map 17 re-layout with interim recolours, then
   875-878.
3. Map 10 ground, lake and rim, after decision A.
4. Map 13 re-skin.
5. Map 9, then 18, then 11 (largest, most route-sensitive).
6. Map 8/39 polish.

Each step goes through `tools/integrate.sh`, the verifier, and an in-engine
`/playtest` before its TODO checkbox flips.

## 8. Pass 2 (Fable art direction, Astra mocks)

The user's verdict on pass 1 was "definitely better, but not good enough".
Pass 2 ran one Fable design agent and three Astra (`gpt-6-astra`) graphics
agents. **All three Astra agents hit the provider's usage limit mid-run.**
AstraCloud finished two iterations, AstraInteriors finished one, and
AstraVale wrote a full-map mock to `/tmp/lv-maps-research/v2/AstraVale/`:
19,959 raw items, all 65 positioned pins present, no water outside the
old rectangle. It never reported, and the files landed after Fable's review,
so Fable never saw them. Fable completed, and wrote its Map 10 layout as an
implementer-ready recipe. Everything is in
`2026-10-12-organic-maps/v2/`: `fable-report.md`, three layouts
(`layout-map10.md`, `layout-map17-13.md`, `layout-interiors.md`), and the
renders.

**Method change.** Every mock is now judged inside one 320×200 game frame
(about 970 world units), side by side with the 1994 shot at ×3. Whole-map
renders hid most of the problems.

**What still read as synthetic in pass 1** (Fable, at game scale):
- **Material inversion.** 1994 village frames are 62-77% dirt with rock at
  the margins; the mock was mostly rock with dirt crumbs.
- **Flatness.** screen20 shows three height tiers and two cliff faces in a
  single frame; the mock shows one plane.
- **Void in frame.** screen11 is cloud to every edge.
- **Pillars.** Recoloured 233s read as stacked crates. The 1994 posts are
  about 15 px wide and the donor is 32, so the columns must be drawn, not
  recoloured.
- **Edges.** Still cut at chunk or tile resolution.
- **Props.** About 10× too sparse, and not clustered.

![Map 17 walkway iterations vs screen12](2026-10-12-organic-maps/v2/astra-m17-iter-screen12.png)
![Map 17 obelisk iterations vs screen11](2026-10-12-organic-maps/v2/astra-m17-iter-screen11.png)
![Draft art 874-881](2026-10-12-organic-maps/v2/astra-draft-art-874-881.png)

**What landed:**
- **Map 17.** Drawn art: round banded columns (877), gem pillars (878), a
  kerbed raised walkway (879) and the throne nook. The screen12 panel is the
  closest anything has come to the 1994 look.
- **Draft art 874-881** covers the flat cloud, gold brick, the drum, the
  columns and walkway, an 18-frame cloud-lobe edge set (880) and a
  cloud-over-gold set (881). Together these are the 1994 "Cloud globs".
- **Interiors.** The Map 9 tomb dais reads as screen10, and the Map 18 cave
  sanctum works. There are draft god plinths and a banded fire-pillar cap.

**Fable's macro layouts (v2).** All pins stay at their exact x/y/z.
- **Map 10:**
  - Regions: Hoskuld basin, Gunnar ravine, central scrub, southern lakes,
    mushroom garden, lava field at the cliff gate, temple approach.
  - Height tiers: T0 at z=0; T1 ridge arms at 48; T2 plateaus at 96; a z=64
    south shelf on the two pinned z=64 items; north-west backdrop cliffs up
    to 288.
  - A horseshoe crest behind the Sacred Circle makes it read as a promontory
    without moving any pin.
- **Map 17:**
  - A processional axis: arrival gold, gold street, obelisk forum, walkway Y,
    god's terraces, throne court.
  - Height rhythm: cloud 0, walkway 8, terraces 16, a drum mound from 16 to
    96.
  - A colonnade post every 192 units on both sides of the walkway.
  - A pillar ring of radius 420 round the obelisk.
  - No void within about 1500 units of any route.
- **Interiors:** per-map composition beats, and a camera rule: a wall within
  about 3 tiles and one feature in every frame along the main path.

**Ranked remaining gaps** (Fable): placement outweighs art about 7:3.
1. Map 10: AstraVale's mock predates Fable's layout. The outline is still
   rectangular, the ground is flat, and the props are sprinkled evenly.
2. Apply the 880/881 lobes to every cloud rim.
3. Cloud shadow contrast.
4. Floor holes and monotone floors in the interiors.
5. Dressing density everywhere.
6. Obelisk mound and pad removal.
7. Walkway furnishing.
8. Gold and marble recolour tweaks.
9. A waterfall for screen09: the only art gap with no draft.
10. Map 8/39 polish.

**New decisions raised:**
- Raise the obelisk (z 40/56), or give it a shallow pedestal (the default)?
- Replace Gunnar's red keep?
- Real 347 water at the village springs, or dry wells?
- A water pool in the Map 13 valley?

These sit alongside decisions A-E in §6.

## 9. Pass 3 (2026-10-13: Astra builds, Fable reviews live)

The Astra usage limit had reset by morning, so the three Astra agents
resumed from their own round-2 work and applied Fable's layouts. Fable
reviewed each iteration as it landed. **All three Astra agents hit the
usage limit again after about 12 minutes.** Each had landed one or two full
iterations first, with REPORT.md checkpoints. Everything is in
`2026-10-12-organic-maps/v3/`: `fable-verdict.md`, the three Astra reports,
`art_contracts.json` (specs for 874-881), and the renders.

**Fable's verdict: closeness to the 1994 look at game scale, 1-10**

| Map | Score | Evidence |
|---|---|---|
| 10 village (screens 19/20/22) | 6 (the garden panel alone, 7) | `v3/astravale-iter02_pair_screen22.png` |
| 10 highlands (screens 17/18/02/09) | 4 | `v3/astravale-iter02_pair_screenshelf.png` |
| 17 Cloud City | 5 | `v3/astracloud-iter01_m17_pair_screen11.png` |
| 13 summit and climb | 3 | `v3/astracloud-iter01_m13_pair_screen16.png` |
| 9 arrival and dais | 5 | `v3/astrainteriors-iteration02_map09_dais.png` |
| 11 element wings | 4 | `v3/astrainteriors-iteration02_map11_fire_lava.png` |
| 18 shrine | 4 | `v3/astrainteriors-iteration02_map18_godwest.png` |
| 39 hedge and forest | 5 | `v3/astrainteriors-iteration02_map39_hedge.png` |

![Map 10 garden vs screen22](2026-10-12-organic-maps/v3/astravale-iter02_pair_screen22.png)
![Map 17 obelisk vs screen11](2026-10-12-organic-maps/v3/astracloud-iter01_m17_pair_screen11.png)

**What landed:**
- **Map 10:**
  - Ground follows the 1994 split: grey highlands, and basins 60-75% dirt.
  - Height tiers at z=48, 64 and 96-288, with textured cliff drops.
  - The garden now has a ring of dirt round it.
  - Raw items 23,274 (target ≤22k); 65/65 pins; all 13 route targets
    reachable in Astra's flood.
  - Astra found a real bug in its own round-2 generator: cliff frames
    27/28/30/31 f2/3 and 29 f6 are solid black, and the generator had been
    picking them. It now selects frames by role.
- **Map 17:**
  - Blue-grey cloud stipple restored, lobed rims, and desaturated gold.
  - The obelisk's drum mound is 3×3 plus 2×2.
  - Posts every 192 units along the walkway, and a pillar ring of radius 420.
  - 5,772 items. 11 pins exact and 2 deferred; Astra's report says which.
- **Map 9:** a real tomb dais 48 units high, with six 8-unit stair courses
  and blood shapes 839 and 423. Shape 332 turned out to be severed arms.

**Remaining, ranked by Fable**

Placement:
1. Black void in frame (Vale seams, Map 13 cliff faces, Map 9 frame bottom,
   Map 11 lava surrounds). Fix with backfill based on what is actually
   occluded, within about 1500 units of every route.
2. Grey ground that uses a single frame. Mix frames by coordinate hash and
   add rock clusters.
3. Functional dressing groups: the screen20 camp (fire 267, logs, bedroll),
   the screen19 urn stack, and mushroom colonies at cliff edges.
4. Camera framing:
   - Map 9's dais framing.
   - Map 18's plinths should be stepped stone, not a flat plate.
   - Clean up the Vale temple masonry.
   - Add banks to Map 11's lava and shrink its extent.
5. Cloud City:
   - Put cloud under the gem ring and move the gold forum south.
   - Cluster the furniture.
   - Rebuild the Map 13 climb toward screen16 (water, falls, ledges).
6. Budgets: the Vale is still over 22k items, and the pin floods for Cloud
   and the interiors have not been run.

New art:
1. De-stripe the cloud tile and polish the 880/881 lobes. Every Map 17 and
   Map 13 shot depends on this.
2. Waterfall frames. Drafts exist but were never placed.
3. God-shrine slabs, plinths and the fire pillar.
4. Optionally, an iron-railing fence.

**New user decisions:**
- **Map 18 god trio.** Keep the pinned spacing, or move the flanking god
  pins about 500 units inward? The screen04 composition needs the move:
  the gods are 1536 units apart, so they cannot share one 320-px frame.
- **Map 11 wing assignment.** Fable endorses the pinned assignment (Earth NW,
  Air NE, Fire SW, Water SE) over its own round-2 memo.

# ReconVillage — screen19 / screen20 / screen22 (Map 10, Gunnar village)

## Method
- **Candidates**: `shot_decompose` accepted hits, plus targeted loose searches (`find_hits`, anchor/full 0.3-0.5) over the shapes in play, plus lattice candidates (every frame of a shape at every lattice cell, scored on pixels not yet explained).
- **z per shape class** comes from retail co-occurrence (retail `FIXED.DAT.bak`, globs expanded):
  - rock 125 sits 48 above dirt 4, on 48-high faces 31/32 (4564 retail pairs);
  - flats 386/301 rest on 125 tops (+8);
  - roof 412 sits +40 over dirt 4 (1875 pairs);
  - walls 145-150 and posts 148 share z; eaves 410 and trim 118 sit +40.
- **x,y** are solved exactly from the hotspot for that z, with C truncation: `sx = x//4 - y//4`, `sy = x//8 + y//8 - z`.
- **Fitting**: greedy add/remove of candidates. Objective = exact palette-class matches - 0.25 × wrong pixels.
- **Painter**: an engine-faithful one, built from the `item_sorter.py` port. It uses `SortItem::below/overlap/occludes`, `ItemSorter::AddItem` list insertion and the `PaintSortItem` DFS. Items are composited in paint order.
- **Hidden ground**: filled on the lattice only where a test add changes no visible pixel. These items are marked `lattice-fill` or `inferred`.
- **Round trip**: every JSON was re-rendered from its own `items` + `actors` + `camera` (results below).

## Results
| shot | decomposer coverage | vignette frame match (covered px) | items | 1994 art | placement |
|---|---|---|---|---|---|
| screen19 | 90.6% | **96.1%** (96.6%) | 119 (84 matched, 35 hidden fill) | 2 (elder sprite, doorway fill) | Gunnar hut lot 1 (Atli), origin (18816,6272,0) |
| screen20 | 90.6% | **95.4%** (95.8%) | 97 (91 matched, 6 fill) | 3 (elder w/ staff, 2 spear children) | Gunnar hut lot 4 (Hrodny), origin (19712,7552,0) |
| screen22 | 84.7% | **96.6%** (96.8%) | 129 (121 matched, 8 hut floor) | 2 (blue root plants) | Gunnar hut lot 3 (hall-keep lot), origin (17408,7680,0) |

Every remaining wrong pixel is one of these:
- 1994-only actors;
- 1994-only plants;
- the doorway fill;
- small 1994 litter (white/red/blue sticks in screen22);
- objects cut by the frame edge;
- a sort tie on 1-2 eave/rock pixels.

The match figures include retail actors: the Avatar in all three shots, which is exact.

## screen19 — Atli's hut (south front + east side), Avatar at the door, elder in the doorway
Vignette-relative coordinates (origin O = shot-world (4480,3584)).

**Ground**
- The yard is a **sunken dirt trench**: 4-tiles at z=0 on lattice 128k+127.
- Rock plateaus lie on the left and in front: 125 at z=48 on the half-lattice 128k+63 (walk surface z=56).
- The plateaus stand on 48-high faces 31:1, 29:7 and 32:13, which rise from the yard.
- 386/301 lie on the plateau at z=56.
- The mountain behind rises in 32-face courses at z=48 and z=96.

**Hut (exact)**
- Roof boxes span rel x 127..639 (4 tiles wide).
- **South wall** (front, the line at rel y=639), west to east:
  1. post 148:15
  2. wall 150:0
  3. post 148:8
  4. **door gap 128** (rel x 287..415)
  5. wall 150:0
  6. wall 194:1
  7. corner post 148:0
- **East wall**: 146:0 | 145:0 | 145:1 (X-braced).
- **Roof**: 412 at z=40. It is a hip roof:
  - ridge column 43/48;
  - west edge from S to N: 25, 26, 29;
  - slopes 32/33/34.
- **Eaves and trim**:
  - 410:3 eaves at z=40 along the front, +64 out;
  - 118:3/4 trim on the east eave;
  - 118:5 trim on the NW.
- The **"blue pot stack" is retail 649:2**: the blue crop row (192x64), standing at z=0 against the wall. It is the same art as screen22's crops.
- Full construction table: `hut_spec.json`.

**Actors**
- Avatar = shape 1 frame 11, exact (790/790 px).
- Elder = a 1994-only sprite. No frame of the 52 retail actor shapes matches it. `art_s19_elder_draft.png` is a **reference crop, not a sprite** (it includes the doorway fill and the jamb plank); the clean re-cut is `art_s19_elder.png` (art_registry 2041 frame 0; D-track 2026-10-16).

**Unexplained pixels**
- The elder.
- The doorway: a flat palette-188 fill.
- About 150 px of plank wall right of the door.

**Pins**
- The vignette is shifted by (14336,2688), so Atli's pinned home (19231,6943,0) lands inside the door gap, flush with its east jamb, on z=0.
- The 1994 elder's feet map to (19191,6931). No pin moves.

## screen20 — campfire yard west of a hut; Avatar lying; elder + two spear-carrying children
**Ground and hut**
- The yard is dirt 4 at z=0.
- There is a rock plateau on the left: 125 at z=48 on faces 31/29/32/35.
- A dark cliff 26/29 stands at the top right.
- Hut roof 412/118/647 at **z=40**: the hut stands **on the yard level**. Pixel test: putting the roof at z=-24, i.e. the hut one tier lower, loses 2,410 px. So the reported "three tiers" is really two tiers plus a roof.
- The hut shows its west side and NW corner: 412:31, then 29 ×4, i.e. at least 5 rows deep.
- Merge test against screen19 (`test_same_hut_19_20.json`): the two shots show **different huts** of the same design.

**Props**
- Campfire = four 267 items in a 2×2 cluster (64×64).
- Log pile = three 838 logs at z 0/8/16.

**Actors**
- Avatar = shape 1 frame **252** (lying), exact (838 px).
- The elder (with a staff) and two small spear-carriers (one dark-haired, one blond) are 1994-only sprites.
- Drafts: `art_s20_elder_staff_draft.png`, `art_s20_spear_child_dark_draft.png`, `art_s20_spear_child_blond_draft.png`.

**Pin move**
- Hrodny's chest (21024,8832,0) → (21120,8832,0).
- Reason: its 96×64 box straddles the vignette hut's west wall line. [INFERENCE: that wall is hidden in the shot; walls are assumed flush with the roof edge, as they are in screen19.]

## screen22 — Gunnar crop garden west of a hut
**Garden (exact)**
- Square iron-fenced garden, rel x 351..831, y 479..991.
- Stone posts 148 (frames 17/20/25) stand on a 224-grid: x {383, 607, 831}, y {511, 735|767 (a double pillar mid-side), 991}.
- Fences: 207 runs along y, 287 runs along x; gate/end pieces 515:1 and 516:0.
- **Crops**:
  - 650:2 (green) and 650:1 (blue), 64×192, side by side;
  - 391 sprouts and 538 loose vegetables;
  - mushroom cluster 466:1 in the SW quarter.
- Outside the garden:
  - giant mushroom 65:8;
  - dead tree 56:8;
  - bush 434:4;
  - scrub 210.

**Hut**
- Its roof is 4 rows deep: west edge from N to S is 31, 29, 26, 25.
- South wall 149:1; eaves 410:3; west trim 118:5.
- It stands 192 east of the garden's east fence.

**Actors and 1994 art**
- Avatar = shape 1 frame 51, exact.
- 1994-only art: two blue stalked root plants (`art_s22_blue_plant_a/b_draft.png`).

## Which village — evidence
- **Gunnar for all three.**
  - The elder sprite is male (white hair and beard), and the same sprite appears in screen19 and screen20. Atli is "Elder of Clan Gunnar", "Frère Aîné" (ATLI.UNK:33).
  - Hoskuld's Elder is a woman: "Back to your Elder, go. Her duty, it is" (THORDIS.UNK:880-883).
  - Crops and fields are Gunnar's:
    - HRODNY.UNK:345, 626, 753, 800 (water to the fields, tending the crops);
    - INGYALD.UNK:550 "In the field";
    - SHADES.UNK:380 Atli "Grow again, our crops shall!";
    - ATLI.UNK:2223.
- [INFERENCE] There is no village capture scene in the recovered source. The Avatar is poisoned and wakes at the Passage Test grounds (PLNTST.UNK:98-108). screen20 is therefore placed as the Gunnar commons.

## Placement (Map 10, Gunnar village; huts at z=0 on the village ground)
- **screen19** → hut lot 1 (Atli, (18944,6144)). Shift (14336,2688).
- **screen20** → hut lot 4 (Hrodny, (20992,8192)). Shift (15744,4096).
- **screen22** → hut lot 3 (18432,8192), currently the off-style hall keep (glob 573). Shift (13184,4096).

Pairwise footprint overlap between the three placed vignettes: 0 items.

The only builder items outside the replaced lots that touch a vignette area are:
- pins 107 (Atli), 111 (child) and 114 (Changtar), all clear;
- the west palisade, which sits over vignette ground flats only.

## Comparison with our art
- `compare_actors_1994_vs_ours.png`: our Zealans use retail 707 (hooded peasant) and 708 (child). The 1994 elder (white hair, staff) and the 1994 children (grey clothes, spears) are different sprites.
- No custom shape 860-873 corresponds to anything in these shots, so `replaces` is null everywhere.
- The 1994 actors need new LV actor shapes. The drafts are single frames, so walk-cycle frames would have to be drawn.

## Files
- `screenNN.vignette.json` — output contract per shot.
- `screenNN_vignette_render.png` — the render.
- `screenNN_vignette_diff.png` — shot | render | wrong pixels in red, ×3.
- `hut_spec.json` — hut construction table.
- `art_*_draft.png` — U8PAL-indexed drafts, index 255 transparent.
- `art_*_preview.png` — ×8 previews of the drafts.
- `compare_actors_1994_vs_ours.png` — 1994 actors vs our 707/708/574.
- `test_same_hut_19_20.json` — the screen19/screen20 merge test.
- `screenNN_cands.json` / `screen19_cands.json` — candidate pools.
- Intermediate diffs: `s19_*.png`, `s20_*.png`, `s22_*.png`.

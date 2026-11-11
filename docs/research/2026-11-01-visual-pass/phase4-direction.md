# Phase 4: art direction and executable design for dressing (2026-11-09)

This is the spec for phase 4 of the visual-quality pass
(`docs/research/2026-11-01-visual-quality-plan.md` §7). One Codex agent
executes one map section. Each map section in §3 stands alone: it carries its
regions, palettes, limits, and no-touch list.

Three files came with this document and none is committed:

- `agents/map-populator/src/dressing_metrics.py`: the measuring module
  (extended, see §1.1);
- `docs/research/2026-11-01-visual-pass/phase4/mock.py` and `make_mocks.py`:
  the offline renderer and the mock generator;
- the PNGs in `phase4/` (§6). They contain Origin art and stay out of git.

No builder, test, or artifact was edited. `tools/build_artifacts.sh` and
ScummVM were not run. Every number below was measured on the built
`shared/build/FIXED.DAT` (main at `dd13030`) or on the pristine retail
`FIXED.DAT.bak`.

## 0. The direction in one page

1. **Retail dresses by the chunk.** A retail map is 6 to 11 expanded items
   per raw record because 76% to 93% of its outdoor props arrive inside
   GLOB.FLX prefabs that carry a 512-unit floor chunk and its props together.
   Glob 124 is sixteen grass tiles, a tree, four mushrooms, and three root
   tangles, and retail places it 66 times. Our maps place 0 dressing prefabs.
2. **The cheapest move is egg substitution.** Our rock floors are already
   glob 397 eggs (824 on Map 10 alone). Changing an egg's glob number from
   397 to one of retail's fourteen dressed rock chunks adds spires, stumps,
   pebbles, and fungus at zero raw records. The same holds for grass (Map 39)
   and for every filler plate: one prefab egg replaces four 256-unit plates.
3. **Every region's surroundings get a decision** (§3, "beyond"). Caves and
   stone halls return to darkness, which is the retail idiom. The Vale's
   south and east edge becomes a rock shore. The Fire and Water sections
   stand in lava and dark water. The cloud sea ends in a star field.
4. **The Vale stays barren.** The 1994 design says rock and brown earth, and
   green covers at most 4% of any shot. Its richness comes from four ground
   materials, dead wood, bones, ruins, pools, and cliffs, which is what
   retail's Map 21 does.
5. **Numbers are floors.** Each region has a sentence a player would
   recognise, and Astra grades against the sentence. The density, mix, and
   repetition numbers in §4 keep a region from passing while still bare.
6. **Retail has no prefab for barren earth, cloud, or gold.** Those are ours
   to author, and that needs GLOB.FLX to become a sixth build artifact
   (decision D2).

## 1. Retail calibration, measured

### 1.1 The instrument

`agents/map-populator/src/dressing_metrics.py` reads a built `FIXED.DAT`,
expands glob eggs as `GlobEgg::enterFastArea` does, and classifies every
visible item from TYPEFLAG alone into ground, void, trim, structure, small
prop (footprint up to 96x96), and large prop. All shares are over 128-unit
ground cells.

```bash
cd agents/map-populator/src
python3 dressing_metrics.py 10 11 13            # whole maps, the built FIXED
python3 dressing_metrics.py 3 5 7 --retail      # pristine retail
python3 dressing_metrics.py --calibrate         # retail range per region type
python3 dressing_metrics.py --regions           # every LV region against its targets
python3 dressing_metrics.py 10 --box 3072 1024 22528 30208 --json out.json
```

New in this pass: `RETAIL_TYPES` (which retail maps are which region type),
`REGIONS` (every LV region with its type and box), `TARGETS` (the per-type
acceptance numbers), `measure_regions`, `calibrate`, and a `--glob` option so
the module can read a built GLOB.FLX later. `python3 dressing_metrics.py
--regions` currently ends with `118 target failures`.

The metrics that carry the direction:

| Metric | Meaning |
|---|---|
| `props.props_per_100` | small and large props per 100 ground cells |
| `props.dressed_share` | share of ground cells with something placed on them or on a neighbour |
| `props.bare_share` | share of ground cells with nothing placed and no change of material within four cells (about a quarter screen) |
| `props.grouped_share` | share of small props in a single-link group of three or more (link 192 units) |
| `props.nn_median` | median distance from a small prop to its nearest neighbour |
| `props.stride_share` | share of same-shape props whose nearest-twin vector is one of that shape's two commonest; 1.0 is a lattice |
| `props.from_globs` | share of props that arrived inside a prefab |
| `ground.top1` | share of ground that is the commonest material |
| `ground.seam_density` | share of adjacent ground pairs that differ in material |
| `repetition.period_excess` | the §11.9 tile-period measure: how far the best-matching lag (2 to 16 cells) stands above the median lag |
| `repetition.modal_chunk` | share of full chunks identical, floor and contents, to the commonest chunk |
| `records.expansion` | expanded items per raw record |

The brief's first-cut "small props" count treated cliff blocks as props. The
module files `SI_LAND|SI_SOLID` pieces under structure, which is why Map 13
reads 1.3 props per 100 cells here and 16.3 in the brief.

### 1.2 Region types and their retail references

Types were assigned from 1/16 overviews of all 31 populated retail maps
(`phase4/retail-overviews.png`, `retail-overviews-barren.png`,
`retail-map07-overview.png`). Map 22 has zero FIXED records.

| Type | Retail maps | What they are |
|---|---|---|
| grass | 3, 5, 7, 4, 6 | outdoor valleys ringed by cliff and a brown mountain-top band |
| town | 39, 40, 41 | Tenebrae and the palace grounds |
| barren | 21 | grey rock plateau, earth patches, pools, sea on one side |
| cave | 28, 47, 49, 57, 62, 31, 14 | 301-floored caves in black |
| lava | 12, 44, 24, 25 | rock and earth standing in a lava sea |
| temple | 63, 54, 15, 50, 51 | stone interiors and the catacombs |
| sky | 43 | the Ethereal Void platform over a star field |

Retail has one sky map and one barren outdoor map. Targets for those two
types rest on a single reference each, plus the 1994 shots.

### 1.3 Density, mix, and repetition per type

Output of `python3 dressing_metrics.py --calibrate` (low to high across the
type's maps), with our whole-map figures beside them.

| Type | props / 100 | dressed | bare | top material | seams | period excess | modal chunk |
|---|---:|---:|---:|---:|---:|---:|---:|
| grass | 7.3 to 17.2 | 28 to 45% | 13 to 39% | 45 to 53% | 12 to 14% | 10 to 28% | 12 to 41% |
| town | 22.9 to 34.2 | 48 to 63% | 4 to 9% | 46 to 56% | 15 to 19% | 18 to 25% | 27 to 33% |
| barren | 3.8 | 24% | 13% | 39% | 15% | 34% | 22% |
| cave | 5.4 to 33.5 | 54 to 83% | 0 to 18% | 32 to 63% | 14 to 42% | 13 to 40% | 8 to 51% |
| lava | 1.5 to 6.0 | 27 to 31% | 4 to 35% | 34 to 70% | 11 to 24% | 20 to 23% | 22 to 61% |
| temple | 7.8 to 157 | 34 to 93% | 2 to 32% | 42 to 81% | 3 to 22% | 15 to 35% | 3 to 46% |
| sky | 7.0 | 14% | 23% | 72% | 8% | 59% | 62% |

| LV map | props / 100 | dressed | bare | top material | seams | period excess | modal chunk |
|---|---:|---:|---:|---:|---:|---:|---:|
| 9 | 4.9 | 66% | 1% | 77% | 6% | 51% | 4% |
| 10 | 1.4 | 15% | 29% | 56% | 10% | 25% | 28% |
| 11 | 0.9 | 32% | 10% | 34% | 8% | 58% | 24% |
| 13 | 1.3 | 33% | 36% | 36% | 9% | 18% | 34% |
| 17 | 3.9 | 12% | 61% | 89% | 4% | 7% | 1% |
| 18 | 5.9 | 59% | 3% | 73% | 5% | 45% | 13% |

Read against retail: Maps 10, 11, and 13 hold a quarter to a tenth of the
props of their type; Maps 9, 11, and 18 repeat their floor at a stride retail
never reaches outside a prop-free map; Map 17 is one material with nothing in
three fifths of it.

### 1.4 How retail clusters

- **Props come in groups.** 85% to 96% of retail small props sit in a group
  of three or more on grass, town, and barren maps (caves: 32% to 94%). Ours:
  65% on Map 10, 12% on Map 11, 0% on Maps 13 and 18.
- **Neighbours are one to two tiles apart.** The median nearest-neighbour
  distance is 51 to 72 units on ten of twelve retail maps sampled. Ours is 241
  on Map 11 and 304 on Map 13. `build_map_13.py:1090-1099` measured the same
  thing for spires alone on 17 October 2026: nearest spire a median 128 away,
  85% within 200, at 32-unit offsets.
- **Groups mix shapes.** 49% to 69% of retail groups of two or more hold at
  least two shapes on eight of the twelve sampled maps.
- **Clark-Evans R** is 0.34 to 0.63 on retail outdoor and town maps, where
  1.0 is random and lower is clumped. Map 10's north plain reads 1.19, which
  is more even than random.
- **Retail strides too, at chunk scale.** `stride_share` is 37% to 74% on
  retail maps because prefabs repeat. The eye accepts it because the modal
  chunk stays under 41% outdoors and no prefab family has fewer than four
  members. A stride limit of 75% is the retail ceiling; ours reaches 88% on
  Map 18 and 100% in several regions.
- **Ground changes in patches.** Retail outdoor maps hold 1.4 to 4.1
  material patches per 100 cells and caves about 6.4. Ours hold 0.4 (Map 17)
  to 1.9 (Map 13), with Map 10 at 0.9.

### 1.5 Glob use

| Map | raw records | expanded / raw | dressing eggs | props from prefabs |
|---|---:|---:|---:|---:|
| retail 3 | 1,835 | x10.8 | 186 | 76% |
| retail 5 | 2,691 | x7.3 | 167 | 93% |
| retail 7 | 2,230 | x10.3 | 106 | 85% |
| retail 39 | 4,624 | x6.2 | 288 | 85% |
| retail 40 | 1,963 | x9.1 | 254 | 79% |
| retail 49 (cave) | 4,447 | x4.5 | 147 | 45% |
| retail 21 (barren) | 2,665 | x3.8 | 10 | 6% |
| LV 10 | 21,864 | x2.2 | 0 | 0% |
| LV 11 | 10,065 | x1.8 | 0 | 0% |
| LV 13 | 6,298 | x1.5 | 0 | 0% |
| LV 17 | 9,284 | x1.0 | 0 | 0% |

Expanded items per ground cell is the measure of fast-area load that does not
depend on map size. Retail runs 1.1 to 2.0 outdoors and in towns and 2.7 to
2.8 in caves. Map 10 is at 1.22, so it has room to double its content before
it is as dense as Tenebrae, provided the raw records come down (§5.5).

## 2. Glob inventory

### 2.1 What exists

GLOB.FLX has 3,072 slots; 1,513 hold items and retail maps use 1,510 of
them. `/tmp/claude-1000/p4/ginv.py` classified every prefab by floor
material and prop content with the metrics module's classes; the two contact
sheets `phase4/globs-retail-A.png` and `globs-retail-B.png` render 72 of
them with the viewer's painter. A prefab egg snaps to its 512-unit chunk, so
a prefab is always a whole chunk.

| Family | Globs (retail use count) | Content | Suits |
|---|---|---|---|
| rock, spires | 395 (82), 398 (79), 396 (78), 399 (71), 400 (52) | sixteen 301 tiles, one to three spire clusters 66 | Maps 9, 10, 11, 13, 18 sanctum |
| rock, stumps | 774 (41) | 301, two grey stumps 152 | Maps 10, 13 |
| rock, pebbles | 956 (57), 957 (53) | 301, nine pebbles 465, nothing solid | every rock floor, including beside routes |
| rock, spires in pebbles | 955 (23), 953 (21), 958 (18), 952, 954, 947 | 301, 66, 465, some 152 | Maps 9, 10, 11, 13 |
| rock, fungus | 882 (16), 881 (16), 877 (14), 1659 (13), 878, 879, 885 | 301, 465, mushrooms 65 | Map 9, Map 11 Earth, Map 13 valley, Map 10 lake side |
| rock and earth tier corners | 386 (93), 384 (85), 387 (72), 455 (17), 452 (16), 388 (16) | raised 301 top with cliff faces and 386 earth transitions | Map 10 and 13 rock mass behind north and west rims; 455 is a flat rock-to-earth seam |
| ~~rock shore~~ **excluded** | 1537 to 1554 | 301 bank floors, bank 128, rippled 347 frames 0-24 | **Not used on Maps 10 or 13** (Douglas 2026-11-09: "map13 shores look wrong ... the wrong tiles"). These are retail's grassland riverbanks: a flat pale cobble band at ground level with rippled water. The 1994 shots meet water with a rock cliff instead; see "Cliff shore" below this table. |
| deep water | 262 (already ours), 298 (18) with rocks 72 | 347 | beyond the shore |
| earth, plain | 875 (477), 437 (35), 264 (23), 435, 434, 438 | sixteen earth tiles 4, different frame mixes | Map 10 earth, to break glob 875's single pattern |
| earth, dead tree | 1901 (8), 1902 (6) | earth, one dead tree 75, one stump 56 | Map 10 |
| lava | 2360 (79), 2365 (70), 2374 (82), 2368 (24), 802 (ours) | lava 409, embers 603 and 604 | beyond Map 11's Fire section, Map 10 lava field |
| lava shore | 2474 (34), 2473 (29), 2469 (20), 2476 (22), 2475 (19) | basalt 122 meeting lava | Map 11 Fire lakes, Map 10 lava field (§7.4 dirt and lava) |
| star field | 2916 (97), 2632 (83) | sixteen star tiles 351 | beyond Map 17's and Map 13's cloud sea |
| black mass | 393 (165), 773 (196), 938 (197), 2313 (36), 1230 (164) | raised black 334 caps, some with a cave face | cave wall backs on Maps 9, 11, 18 where a wall top shows |
| grass forest | 124 (66), 125 (66), 891 (64), 1014 (49), 1013 (39), 13 (35) | grass 3, tree, mushrooms 65, roots 57, earth patch | Map 39's south skirt only |
| earth bank over water | 379, 613, 616, 617, 618, 868, 869 | grass top, rooted earth bank 85 to 91, water | Map 39 moat bank |
| ruined arcade | 1345, 1347, 1344, 1346, 1501, 2988, 1871 | flagstone 35, relief walls 246 and 252, columns 249 | Map 18 exterior and halls, Map 10 Moriens ruins |

**Cliff shore (replaces the retail rock-shore globs, 2026-11-09).** Every
Lost Vale shore, on Map 13's valley and lake and on Map 10's south/east edge
and lake, is built from the pieces the 1994 lake shots use. Counted from
the `vignettes/screen02`, `screen09`, `screen15` and `screen16` item lists:
- **open water** is 347 frame 16, the flat navy (phase 2-3 D7; glob 262 is
  sixteen of it). The other 347 frames (0-8, 17) appear **only in the cell
  touching land**, a few per shot, never as fill;
- **the land edge** is 125 crests chosen by drop side (`CREST_BY_DROP`;
  interior 12-14 and lumps 15-22 for variety), with 26 courses under them
  where the land stands above the water, sinking into it as screen16's face
  does, and a 125 lip where the edge is flush (Map 10's D3 edge);
- **bank 128** is used sparingly at the waterline, as in the shots (frames
  4-8, 14, 15; at most a few per screen), never as a continuous band;
- **in the water:** stepping-stone pillars as screen15 has them, and rocks
  70 and 72;
- **the outline** is ragged along the cell field, never a 512-unit chunk
  notch;
- **excluded:** retail's river-shore globs 1537-1554 and their 301 bank-floor
  frames 6-37. That pale cobble band is what made the first mock wrong.

If records require shore prefabs, they are authored as LV globs (D2, slot
3072+) from exactly this vocabulary. The Map 13 slice's first deliverable is
a 640x400 mock of the valley shore in this vocabulary, for Douglas to sign
off before any building. Map 10's shore waits for that sign-off.

**Signed off by Douglas 2026-11-10** (`wt/vq4-m13` `7002a98`, `p4-m13/shore-mock.png`), with two fixes for the build: textured 347 edge frames and bank 128 stones at the waterline as screen16 has them, and offshore stacks that do not read as square blocks. Map 10's shore follows the same approved vocabulary.

Nothing in retail serves these, so they are ours to author:

- barren earth with dry brush (321, 322), dead wood (75 frame 0, 56), and
  bones;
- rock and earth mixed chunks with correctly oriented 386 corners (retail has
  one, glob 455);
- cloud floor with gold lapping it, cloud with white columns, and a ragged
  cloud-sea edge over stars;
- flagstone chunks with a proper fill (glob 65 is a checker of two edge
  frames, `docs/research/2026-10-12-organic-maps.md` §1);
- village yard chunks from the 1994 hut kit: fence 148, crates 149, pots
  649:2, the skull-post pen 153/156/157/162.

### 2.2 Can our build add globs?

Yes mechanically, and nothing does it today.

- The engine loads every slot of `static/glob.flx` (`game_data.cpp:290-304`,
  `_globs.resize(globflex->getCount())`), and a glob egg's number is its
  16-bit quality, so slots can be appended past 3,071.
- A glob record is `uint16 count` then `{x:u8, y:u8, z:u8, shape:u16, frame:u8}`
  per item. World position is `chunk + 2*x + 1`, so every item sits on an odd
  coordinate, which our 128-grid tiles (x mod 128 = 127) already do. Items
  carry no quality, npcnum, mapnum, or flags, and are created
  `FLG_DISPOSABLE | FLG_FAST_ONLY`. Eggs, pins, quest items, containers, and
  anything usecode searches for by quality stay as FIXED records.
- Missing pieces: `u8_flex.py` has no writer; `install_lv.sh` does not copy a
  GLOB.FLX; `ARTIFACTS.sha256` lists five artifacts; `GlobReader` defaults
  to the retail file and is constructed in 67 places under `agents/` and
  `tools/`. Slice 0 (§7) owns all four.
- The numbering rule follows `.claude/rules/shape-ids.md`: LV globs start at
  3072, are pinned in `lv_manifest.json`, and are never renumbered or reused.

## 3. Per-region direction

Conventions for every map section:

- **Boxes** are world `(x0, y0, x1, y1)`. They are the `REGIONS` rows of
  `dressing_metrics.py`.
- **Targets** are the type's row in §4.1 unless the region lists its own.
- **Egg substitution** means changing a plain floor egg's glob number to a
  dressed family member through `lv_dressing.swap_chunks` (§5).
- **A cluster** is two to five pieces from one kit within 160 units (§5.3).
- **A set piece** is hand-authored and named; the module validates it and
  raises on a violation.
- **Global no-touch**, in addition to each map's list: every `map_pins.json`
  row; every `quest_legs.LEGS` endpoint and its three-cell band; every 1994
  shot window with the 16-pixel margin (`test_vignettes.py` FLOORS may not
  drop by more than the 0.25 slack); every 497, 498, 501, and 846 record;
  the 4-unit z lattice for anything `SI_LAND|SI_SOLID`
  (`.claude/rules/map-geometry.md`).

### 3.1 Map 10: the Lost Vale

**Reads as:** a dead mountain valley of grey rock and brown earth where two
poor villages hang on beside a dark lake, shut in by cliffs to the north and
west and falling to black water in the south and east.

**Grounding.** Plot v1.2 p1 §7: "once lush and beautiful, but is now barren
and desolate". The eight shots on this map (screens 02, 09, 17, 18, 19, 20,
21, 22) are rock 301, earth 4, the 386 corner set, 125 crests, and the hut
kit; green appears only as crops in screen22. Retail's Map 21 is the same
palette at 3.8 props per 100 cells with pools, earth patches, and a brown
mountain-top band (`phase4/retail-overviews-barren.png`).

**Now:** 21,864 raw records (cap 25,000), x2.2 expansion, 1.4 props per 100
cells, top material 56%, bare 29%. 8,112 loose interior ground tiles
(3,378 of 301, 2,692 of 4, 2,042 of 386) exist because `Field._globs`
(`lv_vale_terrain.py:375-403`) emits an egg only for a chunk of one plain
material.

**Palette, whole map.**

| Layer | Shapes and globs |
|---|---|
| ground | rock 301 (globs 397, 2241, then the dressed rock families); earth 4 (globs 875, 437, 264, 435, 434, 438 in rotation); gravel 6 for the dry riverbed; cobble 71 and paving 299 only where a builder already lays them |
| seams | 386 corner set, oriented by neighbour (retail glob 455 is the reference); earth bank 85 to 91 where earth stands over water |
| dead wood | dead tree 75 frame 0 (confirm each frame in a render; one frame is in leaf and is barred here), stump 56, grey stump 152, root tangle 57, dry brush 321 and 322 |
| stone | spire cluster 66 in groups, pebbles 465, rubble 524, 526, 782, pile 300 |
| death | bones 235 and 237, skull posts 153, 156, 157 |
| green, rationed | crops 649 and 650, sprigs 391, bushes 434: villages and Ezrekal's rows only |
| water | 347 frame 16 through glob 262; the cliff shore (§2.1); rocks in water 72 and glob 298; fungus 65 within three cells of water |

**Density.** Whole map inside the outline: at least 6 props per 100 cells
(now 1.8), bare at most 12% (now 26%), top material at most 50% (now 59%),
at least 150 dressing eggs.

**Beyond the edges.**

- *North and west:* rock mass. The rim and the 2,048-unit `edge_skirt` stay.
  Its 1,569 loose 301 tiles at z 104, 152, and 160 become rock eggs, and one
  chunk in five takes a tier-corner prefab (384, 386, 387, 388, 452) so the
  sheet has relief and earth streaks as retail's Map 7 band does.
- *South and east:* a rock shore (decision D6), built as the cliff shore of
  §2.1: the flush edge's land cells take 125 lips by drop side, and the first
  ring of water stays 347:16 with rocks 72 and stepping stones on one chunk
  in six. No retail rock-shore globs.
  Deep water beyond stays 262. The flush edge, its 497 and 498
  courses, and `coast_banks` do not move, so reach and legs are unchanged.
  This answers VQ-025, VQ-028, and VQ-061 (the "thin, broken tile fringe"
  over "a flat navy void").
- *Past the skirt:* the 669 black plates 564:2 west of x 10751 stay.

**Regions.**

| Region | Box, floor z | Type | Reads as | Prop palette and set pieces |
|---|---|---|---|---|
| Entry | 10240,1024,15360,4096, z 0 | barren | the head of the pass, a paved court gone to ruin | Keep the 71 court and the two columns. Broken paving margin (299 fragments, rubble 526), two fallen-column groups (46, 47, 494), dead tree 75 pair at the court's south corners. |
| Hoskuld village | 3072,5120,8192,11264, z 0 | village | a fenced hamlet of plank huts round a well | Yards: fence 148, crates 149, pots 649:2, the 18-bush plot regrouped into two uneven beds. Lot 1's keep (glob 573) becomes a long hall in the hut kit (D7). Desks 205 and 208 and wardrobes 307 move under a roof or leave. |
| North plain | 8192,4096,17408,11264, z 0 | barren | open dead ground between the villages, crossed by an earth track | Egg substitution at 40% of plain rock chunks; dead-wood and bone clusters on earth; one set piece: a dry riverbed of gravel 6 with a collapsed footbridge (planks 145 to 150, glob 635 is the reference). Mock: `m10-north-plain-*`. |
| Gunnar village | 17408,5120,22528,11264, z 0 | village | the smith's village under a rock shelf | Screens 19, 20, 22 fix most of it. Outside the windows: yard chunks, the pen kit, the still and workshop yards (barrels, crates, a woodpile of 56 and 152). |
| Ezrekal's | 11264,11264,14336,14336, z 0 | village | a hermit's stockade with the only living garden | The two herb rows stay green (434, 391). Add a drying rack and jars inside; outside the stockade nothing green. |
| West clearing | 4096,15360,8192,18432, z 0 | barren | a killing ground | Bones in three groups, skull posts, a dead tree. The eight 94 grass cubes on y 15360 leave (stand-in list). |
| Lake | 11264,15360,15360,20480, water z 0 | shore | a black tarn with a rock island | Screens 02 and 09 fix the pier, deck, and tarn shelf. Elsewhere the bank becomes the cliff shore of §2.1 on the land side, with fungus 65 and reeds (391) within three cells of water and rocks 72 in the water. |
| Sacred Circle | 18432,15360,22528,18432, z 0 | barren | standing stones on a bare crest | The eight 38 stones, Sacred Rock 863, and the 5x5 of 71 stay. Ring of pebble chunks (956, 957) only; no solids within 384 of `MAP10_ROOT_SEED`. The eight 94 on y 18431 leave. |
| Cloud approach | 5120,20480,9216,24576 | barren | a stair cut into the canyon toward the sky | Screens 18 and 21 fix the mesa and knoll. Scaffold 148/157/162 near (8959,21791) is regrouped as one lashed frame. Lava field (cells 72,168 to 87,183): lava shore prefabs 2469, 2473, 2474, 2476 round the 409 pool, the 54 lava records keeping their tuples, frame 33 never used. |
| Moriens ruins | 11264,21504,14336,24576, z 0 | ruin | a fallen colonnade | Arcade prefabs 1345, 1347, 2988 as two broken wall runs on the north and west sides; columns 394 and pillars 293 kept; rubble at every column foot. |
| Temple approach | 16384,20480,20480,24576 | barren | a processional stair under a cliff | screen17 fixes the stair. The shelf (z 112) takes gargoyle pairs 38 at the stair head and nothing else tall; `PAD_210` (18432,22719,112) and the trigger-211 box stay clear. |
| Ragnar's cache | 16384,24576,17408,26112, z 0 | barren | a boulder with something behind it | No change beyond pebble chunks; the 796 boulder is quest geometry. |
| Passage Test | 12288,24576,13312,30208, z 0 to 64 | barren | a bare ledge where one plant grows | The Test Plant 871 is the only green. Bones at the ramp foot. The spire at (12416,29760) stays clear of the rim column. |

**Stand-ins on this map (plan §7 item 3):** the keep glob 573; desks 205 at
(5888,6400), (21800,9840), (13824,12287) and 208 at six spots; wardrobes 307
at five; spire clusters 66 used as lone boulders (33 records; each becomes a
300 pile or joins a spire group); grass 94 and 92 patches on rock.

**Transitions (plan §7 item 4):** earth to rock through oriented 386;
earth to lava through basalt 122; land to water through the cliff shore of
§2.1 (125 crests and lips, 26 courses, bank 128 only sparingly at the waterline).

**No-touch on this map.** The 68 pin rows; `TESTPLAN_*`, `RAGNAR_BAG_DROP`
(16447,25727,64); the 2,615 records of 497 and 498 and both 846; closure
columns at (19424,7616), (19264,7520), (20288,8639), (20447,8767);
`temple_near_wall` at (18559,23423); `_check_tracks` (no solid on a `TRACKS`
cell); canyon rim cells (50,192) and (61,192) at 104; `bank_guard` (bank art
two cells clear of every window); the eight shot windows.

**Budget.** Raw must end at or below 20,000 (§5.5 says how). Expanded items
per ground cell at most 2.0.

### 3.2 Map 13: the Cloud Cliffs

**Reads as:** a barren valley floor at the foot of a grey cliff that climbs
in ledges past a black lake to a summit standing in cloud.

**Grounding.** Screens 01, 13, 14, 15, and 16: 301 ledges with 125 crests,
bones, a skull ring, spires; "the edge drops into white cloud". The 1994
climb is a staircase of 56-unit ledges.

**Now:** 6,298 raw (cap 9,000), 1.3 props per 100 cells, bare 36%. The
valley is 100% one material with a modal chunk of 72%.

| Region | Box, floor z | Type | Reads as | Prop palette and set pieces |
|---|---|---|---|---|
| Valley | 1536,10240,6656,12288, z 0 | barren | the dead ground where the climb begins | Egg substitution at 50% from the fungus and spire families; earth patches (glob 437, 264 with a 455 seam) so the floor has a second material; bone and stone clusters. The ruined wall at y 10752 (six pieces of shape 15) becomes a collapsed rock spur: faces 26 and 27, posts 29, rubble 524 and 526; its upper east course stays 497 at (4351,10752,40) and (4479,10752,40). The three 796 boulders leave. Mock: `m13-valley-*`. |
| Climb and tiers | 1536,1664,6656,10240, z 0 to 224 | cave | bare ledges, each with something small on it | Extend `build_dressing`'s rule through the shared module: clusters on flat rock cells with no drop that are not the climb, a shot cell, or a walked cell. Add fungus within three cells of the lake, a second bone group on the north leg. Tier joins: VQ-049 and VQ-053's "repeating diagonal bands" go by choosing face frames from a hashed rng (§5.3 rule 6). |
| Summit and cloud | 1536,0,8191,1663, z 120 | sky | the last rock before the cloud | Shot-fixed. Outside the windows: two white column stumps 875 and a gold brick fragment 876 at the cloud's edge, announcing the city. |

**Beyond the edges.**

- *South, east, and west of the valley:* the cliff shore of §2.1. The 140
  glob 262 eggs keep their places, with their water at 347:16; the land cells
  that touch them become rims or lips. This answers VQ-039 ("a straight
  diagonal slab edge... a large flat void"). The mock's 31 retail shore-chunk
  swaps are withdrawn; that mock is wrong (Douglas, 2026-11-09).
- *Lake:* VQ-037 and VQ-052 ("large angular cutouts", "disconnected blue
  texture scraps") are chunk-snapped water against a ragged bank. The bank
  outline outside the screen15 and screen16 windows is redrawn on the 128
  grid with bank frames chosen by neighbour, and the two black slabs at the
  upper right take rock tops.
- *West ridge and east shelf:* rock mass, kept.
- *Cloud sea:* 874 stays; where it ends (x beyond 8191, y beyond the
  `frame_allow` strip) the 376 black plates become star-field eggs (D4),
  one egg where four plates stood.
- *North:* the accepted black strip `frame_allow` [0,0,8000,1800] becomes
  stars under D4; the box stays in `visual_pins/map13.json`.

**Stand-ins:** shape-15 wall (above); 796 at (1792,12032), (6400,12160),
(2560,10432); lone spires from `build_base_zone`. The six 186 and ten 796 of
screens 15 and 16 are 1994 content and stay.

**No-touch.** Pins: trigger 206 (3328,11520,0), EggCloudCliffs
(4096,11264,0), pad 207 (4096,11776,0), trigger 209 (4351,2303,120), pad 208
(5119,2303,120), four MONEGG triggers, four harpie eggs. Leg (4096,11776,0)
to (4351,1919,120) to (4351,2303,120). `VALLEY_CLEAR`
(2687,10111,4735,11135) takes flat pieces only. `SHOT_CUTS`, `RAY_SLIDES`,
`WINDOW_FILLS`, `UNFACED_BY_HAND`, `climb_tiles`, `CLIMB_Z_TOP`,
`CLIMB_Z_STEP`, `lanes_at`, `summit_cells`, `HARPIE_REST`, `CX_EAST`. The
162 records of 497 and 232 of 498. The island under screen13's floating
layer stays walkable. Nothing widens the summit neck (it draws into
screen01).

**Budget.** Raw at most 7,000; cap 9,000.

### 3.3 Map 17: the Cloud City

**Reads as:** a white and gold city of columns standing on cloud under a
night sky, with streets of gold brick and no walls.

**Grounding.** screen11 (obelisk plaza on continuous cloud, white drums with
orange bands, gem-capped pillars) and screen12 (raised lavender marble
walkway with gold trim, the throne nook, gold brick lapped by cloud).
EZREKAL.UNK:1349-1352: "White as the clouds the walls are and bright as gold
the streets are." Retail's only sky map, 43, is a platform over a star field
(`phase4/retail-reference-frames.png`, upper right).

**Now:** 9,284 raw (cap 12,000), no globs, 5,910 records of cloud 874. Inside
the city box (1664,1024,6912,11264): 7.9 props per 100 cells, top material
78%, bare 30%.

| Region | Box | Reads as | Direction |
|---|---|---|---|
| Scroll court | 2688,1024,3968,2048 | a small shrine court | Keep the plinth, columns, and gem pillars. Add a 877 marble border one tile wide on three sides, cloud lapping the fourth. |
| Walkway field (screen12) | 1664,2560,6784,4096 | the raised marble way | Shot-fixed inside the window. East of it, extend the walkway's post rhythm with two broken posts and a fallen drum so the row ends. |
| Processional street | 3712,4480,4480,6144 | the main street | Gem pillars every 256 on both sides read as a ruler. Keep the count, shift pairs by 32 to 64 units off the line, and replace three with two-drum columns or a bare stump. |
| Obelisk plaza (screen11) | 2944,6016,5248,8064 | the heart of the city | Shot-fixed. The ring of 875 at 160 spacing outside the window gets the same break in rhythm. |
| East court | 5632,4864,6912,6272 | a ruined colonnaded court | The 3x3 pillar grid becomes an L of five standing pillars, two stumps, and two fallen, with the bottles and bones regrouped at one corner. |
| Arrival landing | 3200,9472,6016,10496 | a gold terrace at the cloud's edge | Keep pad 209 clear. The eight columns on x 3455 and x 5759 stay as the terrace's frame; add marble 877 steps down to the pier and two gem pillars at the bridge head. |
| South street, forecourt, aisles | as built | gold streets | Gold edge stays ragged on its two-cell hash. |

**Material mix.** Cloud stays the floor (the shots say so). The second and
third materials grow: gold 876 from 688 cells to about 900 through two small
side courts off the processional, and marble 877 as borders and steps.
Target inside the city box: top material at most 72%.

**Beyond the edges (decision D4).**

- *Cloud sea:* 874 stays, 2,587 tiles. Its outer boundary, now a straight
  sawtooth, is redrawn as lobes two to five cells deep (`OUTLINE_GROW`
  with the hashed rng), so cloud visibly ends in air.
- *Beyond the sea:* a star field. The 615 black plates 564:2 become about
  198 star eggs (globs 2916 and 2632, sixteen 351 tiles each). The mock
  measured raw 9,284 to 8,867. Mock: `m17-arrival-edge-*`.
- *North and west coordinate limit:* unpainted ground past x 255 and y 255
  cannot take an item. VQ-047's worst cameras (44.78% black at (2719,287,0))
  need the playable boundary moved south-east, which is outside this phase;
  it stays in the backlog.

**Stand-ins:** the four shape-15 steles at (3647,4543), (4703,4543),
(4159,8255), (4159,9599) become a two-drum white column 875 on a marble 877
slab, each keeping its plaque 614 with the same quality and the same reach.

**Transitions:** gold to cloud is the ragged hash edge plus one LV prefab
family, "gold lapped by cloud"; marble to cloud is the 877 kerb.

**No-touch.** Scroll 864 (3328,1536,8); Shield halves 878 frame 1 at
(3559,3311,0) and frame 0 at (4259,7199,0), frames load-bearing; plaques 614
at (3615,4544,16), (4671,4544,16), (4127,8256,16), (4127,9600,16); obelisk
front drum 875:1 at (4127,7199,0); pad 209 and EggReapply (4608,9984,0);
trigger 208 (4608,11008,0). The 400 curb records and the 1,331 recess walls
of `column_recesses()` (all 2,228 quest-band cells stay at 50% visible or
better). The 26 movables keep clear boxes. The channel between landing and
pier stays sealed. `GOLD_AREAS`, `STRIPS`, `PIER`, `BRIDGE`, `SOUTH_CUT`.
`window_clear()` keeps both shot windows. No 435 to 438 (they are
`SEA|DAMAGING` foam).

**Budget.** Raw at most 9,500; cap 12,000.

### 3.4 Map 11: the Elemental Dungeon

**Reads as:** four caves, each drowned in its own element, joined by cut
stone halls: an earth cave walled in living rock, a wind-scoured cavern in
the dark, a fire cave standing in a lava sea, and a flooded hall.

**Grounding.** screen05 (the Fire torture pocket) and screen07 (the Pillar
of Fire) are cave rock 301 with 26 to 32 faces. Retail's Map 12 stands its
dungeon in lava; retail's caves stand in black.

**Now:** 10,065 raw (cap 12,000), 0.9 props per 100 cells, period excess
58%. 2,867 records are 895 paving plates outside the walls, which Astra
graded as more floor (VQ-045, VQ-065 regressed; VQ-020's new problem).

| Region | Box, floor | Type | Reads as | Prop palette and set pieces |
|---|---|---|---|---|
| Entry hall | 8192,1024,11264,4096, glob 65 | temple | a cut-stone antechamber | Flagstone fill from the LV flagstone family (glob 65 is an edge-frame checker). Column pairs kept; relief panels 246 and 252 on the north wall; urns in pairs at column feet; the frame-5 tapestry at (10496,1025) becomes frame 0 or 2. |
| Hub | 8192,4096,11264,7168, glob 65 | temple | a crossing with four doors, each marked for its element | One marker per door: basalt 122 and embers 603 for Fire, a 896 pool for Water, rubble 524 for Earth, a bare spire 66 for Air. `HUB_WEAPON` stays clear. Frame-5 tapestry at (10240,4097) replaced. |
| Earth | 1024,1024,6144,6144, glob 42 | cave | a root cellar of the mountain | Egg substitution is unavailable on glob 42 (shape 242), so this section's floor moves to rock eggs with fungus chunks (877, 881, 882, 1659) and earth patches (437, 455 seam). Root tangles 57 at wall feet, mushrooms 65 in groups, golem lairs marked with 300 piles. The six 186 and four 796 leave. |
| Air | 14336,1024,19456,6144, glob 397 | cave | a high cavern where the wind has stripped everything | Spire chunks (395 to 400) at 35%, pebble chunks at 20%. The two 113 terraces become rock ledges (125 crest over 26 faces). The six 186 and three 796 leave. |
| Fire | 1024,14336,6144,19456, glob 397 with 802 lakes | lava | a rock island in a lava sea | Spire and pebble chunks at 40%; lava shore prefabs (2469, 2473, 2474, 2476) at lake edges that are not causeway; basalt 122 margin. Causeways of 70, pools 318, and flames stay. Mock: `m11-fire-north-wall-*`. |
| Water | 6144,14336,14336,19456, glob 65 | temple | a flooded hall with four dry islands | The 896 pools and 113 islands stay. Fungus 65 regrouped at the islands; fallen blocks 46 and 47 in the pools; the four 796 leave. |
| Four Pillars | 6144,19456,10240,22528, glob 397 | cave | a bare ritual cave | Pebble chunks only outside `SCREEN07_MASK`; no column and nothing standable taller than 40 near the south gate line. |
| Pad room and corridors | 8192,22528,9216,23552; three corridors | temple | plain cut stone | Corridor verges of 242 stay. One relief per corridor mid-length. |

**Beyond the walls (decision D3).** `stone_void_cover`'s 895 plates go.
What replaces them, by the section they are nearest:

- *Fire:* lava. One egg per chunk from 2360, 2365, 2374, 802 (lava burns
  without `SI_DAMAGING`; these chunks lie outside the rim and outside every
  `FIRE_LINES` margin). The mock replaced the Fire quadrant's plates and
  measured raw 10,065 to 9,766.
- *Water:* dark water, glob 262.
- *Earth:* rock mass on the north and west (tier-corner prefab 388 and rock
  eggs at rim height 96), darkness on the south and east.
- *Air, the halls, the corridors, the pad room:* darkness. Black plates
  564:2 at z 0 keep the frame painted.
- *Shot masks:* `SCREEN05_MASK` and `SCREEN07_MASK` keep what they have.

Expected raw after the swap: about 8,000, from four plates becoming one egg
on the lava, water, and rock chunks.

**Stand-ins:** frame-5 tapestries (two); 796 and 186 (13 and 12 records);
66 used as lone boulders in the hub and every section. The sealing boulders
(66 quality 299) at (8576,22528) and (8704,22528) stay (phase 2-3 decision
10, VQ-016).

**Transitions:** rock to lava through 122 basalt and the lava shore
prefabs (VQ-097, VQ-158); hall flagstone to cave rock through a broken
threshold: two courses of 35 fragments and rubble 526 at each doorway.

**No-touch.** The 50 pin rows. Talismans 596 at (2047,5631,4),
(17152,5120,0), (5631,18943,4), (12799,18943,4), z 4 deliberate. Pillars 865
at (7680,20480), (8704,20480), (7680,21504), (8704,21504); receptacles 866 at
(7680,20736), (8704,20736), (7935,21759), (8704,21760). Teleports 202 to 205,
exit pad 779 (8831,23135), both reapply eggs. `FIRE_LINES` and
`LAVA_MARGIN = 128`; no lava or flame under a causeway. The 524 records of
497 and 462 of 498. `HUB` and `SOUTH_PASSAGE` monster boxes.
`SCREEN07_STANDINS`, the 891 and 892 face swaps, `SCREEN05_RELIFT`. Reach:
140,466 cells on arrival and 141,350 opened must hold.

**Budget.** Raw at most 10,000; cap 12,000.

### 3.5 Map 18: the Ancient Temple

**Reads as:** a temple cut into the mountain: a forecourt under the cliff,
two cold halls of dressed stone, and behind a cracked wall a raw cave where
three gods stand in amber.

**Grounding.** screen04: the sanctum is cave rock 301 with the altar on the
floor and the gods on retail plinths 37. Retail's Map 63 is the hall
reference: flagstone, column rows, relief walls, black beyond
(`phase4/retail-reference-frames.png`, lower left).

**Now:** 2,388 raw, 12 under the phase 2-3 ceiling of 2,400. Void cover is
1,088 of those: 544 black plates and 541 backings of 895, which Astra graded
as hall paving outside the walls (VQ-056 and VQ-063 regressed).

| Region | Box | Type | Reads as | Prop palette and set pieces |
|---|---|---|---|---|
| Exterior | 2048,512,4095,2559 | temple | a forecourt under the cliff | Floor becomes cobble 70 with a flagstone approach to the gate (VQ-137 says it reads as another hall). Gargoyle pair 38 flanking gate 114. Rock mass on the north and west (cliff faces 26 and 32 two courses with crest), darkness south and east. |
| Outer Hall | 1536,2560,4607,4607 | temple | a pillared hall with benches | LV flagstone fill. The eight columns stay; two become broken stumps. Benches 231 at (4448,3328) and (4448,3968) move off the east wall (VQ-122). A raised dais of 37 at the north end with urns. Frame-5 tapestries at (3584,2560) and 328 at (1537,3968) replaced. Mock: `m18-outer-hall-*`. |
| Transition Hall | 2048,4608,4095,6143 | temple | the hall that ends at a cracked wall | Rubble thickens toward the breach: 526 and 524 in three groups growing south, the lone rubble at (2975,5503) joins one (VQ-198). Frame-5 tapestries at (2816,4608) and (3424,4608) replaced. |
| Inner Sanctum | 1024,6144,5120,9344 | cave | a raw cave shrine | Outside the screen04 window: pebble chunks, fungus at the west wall, bones at the south edge. The skull 331 gets a 37 plinth fragment beside it so it reads (VQ-196). |

**Beyond the walls (decision D3).** The 541 backings of 895 go and the
black plates under them stay: darkness beyond the halls. The mock measured
raw 2,388 to 2,090. The sanctum keeps its 52 rock tops at z 48 and gains a
continuous crest on the north and west shell so the wall has a back.

**Stand-ins:** the four frame-5 tapestries (VQ-085). The pale 47 post at
(2816,6143) is breach-line geometry and stays (VQ-163 goes to Douglas's
feedback queue).

**Transitions:** masonry to cave at the breach (VQ-123): the nine gravel
flats of shape 6 stay, and fallen blocks 46 and 47 carry the hall's stone two
cells into the cave, north of y 6783 only at the lane's sides.

**No-touch.** The breach line: `BREACH_Y` 6143, `BREACH_QUALITY` 307, six
records at (2815, z 0, 15), (2816, z 0, 47), (2815, z 40, 15),
(2943, z 40, 15), (2815, z 80, 15), (2943, z 80, 15); `tag_breach` raises
unless exactly six exist; the line stays shapes 15 and 47 because TEMPLENT
and CRACKHNT key on them. Crack clear span x 2817..2879, z 0..40. Entry lane
x 2700..2880, y 6144..6783 takes no solids; rubble boxes keep y minus depth
at or above 6143. Pins: skull 331 (2496,8448,0); gods 860 at (2783,8031,16),
(3039,7903,16), (3039,8415,16); altar 550 (3127,8175,0); the four eggs; pad
211 (3072,1792,0); trigger 210 (3072,1408,0); gate 114 (3136,640,0). The
Shield is never placed (`SCREEN04_LEFT_OUT`). `gate_coverage(18)`; the 494
records of 497, 498, and 501; `sanctum_island`; `west_passage_backdrop`;
`RELIEF_LINES`. screen04's contract is zero changed pixels of 59,200.

**Budget.** Raw at most 2,400; cap 3,000.

### 3.6 Map 9: Galjeron's cave

**Reads as:** a damp cave where a man died beside his journal, opening
south into a worked stone passage.

**Grounding.** screen10 (the tomb dais in the guardian chamber). Retail
caves 49 and 57: spires, fungus, pebbles, black beyond a tall jagged face
(`phase4/retail-reference-frames.png`, lower right).

**Now:** 1,226 raw (cap 2,500), top material 77%, period excess 51%. The
hall is 98% one tile.

| Region | Box | Reads as | Prop palette and set pieces |
|---|---|---|---|
| Guardian chamber | 12800,11520,15103,13311 | the tomb | Shot-fixed inside the window. Outside it: pebble chunks and one bone group. |
| Hall | 12800,13312,14847,15359 | the cave where Galjeron lies | Egg substitution at 60% from the fungus family (877, 881, 882, 1659) and pebbles; an earth patch round the body (glob 437 with a 455 seam) so the eye lands there; the troll lair marked with bones and a 300 pile. The six 186 and three 796 leave; the spire at (14208,14400) beside the body leaves (VQ-142). Mock: `m09-hall-*`. |
| Passage | 13824,15360,14847,16895 | cave turning to masonry | A threshold at y 16128 (VQ-140): broken flagstone and rubble across the join. An exit marker at trigger 203 (VQ-151): the two columns framed with a lintel relief. |

**Beyond the walls.** Darkness, which VQ-062 already accepts. VQ-051
regressed on the 125 crest strip with "black triangular gaps": the strip
becomes continuous along the whole guardian shell or is removed where it
cannot be. The 450 black plates and 30 tiles of 35:10 stay, and
`void_cover(items)` stays last.

**Stand-ins:** 186 at six spots (z 48), 796 at three, 66 at three.

**No-touch.** Pad 201 (13696,14208,0); trigger 200 (13759,12031,0); journal
613 (13888,14368,0); MONEGG trigger (14208,13952,0); troll egg
(14720,13408,0); pad 202 (14336,16128,0); trigger 203 (14336,16760,0); body
574 (13824,14336), pack 529, sword 420. `SCREEN10_BLACK_FILLERS`,
`SCREEN10_RELIFT`, `dais_skeleton`, `STAIR_TOPS`. The 178 invisible wall
records. No ceilings. screen10's floor is 89.52.

**Budget.** Raw at most 1,800; cap 2,500.

### 3.7 Map 8: Mythran's caves, LV parts only

**Reads as:** retail's caves, unchanged, with the two places Lost Vale adds
looking as if they had always been there.

Phase 2-3 decisions D1 and D2 keep retail geometry. Phase 4 touches three
things:

- **South shelf (x 27903..32255, y 23679..30719, z 56).** The z 0 skirts of
  895 beyond the shelf go back to retail darkness. VQ-023 ("a detached tile
  floating in black") and VQ-044 ("the intervening black gap remains")
  regressed on exactly those patches. The mock removed 391 records. The
  shelf floor's 301 tiles over 894 and 895 backdrops stay, and
  `test_map08_backdrop.py` still holds. Add fungus and pebble pieces on the
  LV-exposed 301 tiles away from the `shelf` legs.
- **Door chamber (x 20095..21316, y 2591..3999).** The pale Vale-return slab
  71:0 at (20639,3967,0) becomes 71:9 (VQ-091); position and box unchanged.
- **Mythran's house.** The 301 slab at z 1 under the Lord British apparition
  (2200,2208,8) goes (VQ-100). If the apparition 411 still shows before its
  scene, that is a usecode item and joins that queue.

**No-touch.** `TELE_201_DEST` (20111,3175,8), `TELE_212_DEST`
(20143,3175,8), trigger 201 (20415,2783,1), `EggValeReturn` (20575,3903,0),
chest 78 at (20436,3340,0) (tuned against a paint cycle), interactives at
y 3180 or more, both seam lists, the 256 `inherited_black` cells, every
pristine record outside `BASE_ITEM_REMOVALS`, the five `occlusion_allow`
boxes.

**Budget.** Raw at most 6,500; expansion at most 31,000.

### 3.8 Map 39: Tenebrae, the LV lane only

**Reads as:** the back lawn of Tenebrae where the wall gives onto a wood.

**Now:** 5,085 raw, 30,065 expanded against 31,000. Expansion binds first.

- **South skirt (x 12900..22900, y 20479..22400).** The 68 plain grass eggs
  (glob 1) take forest prefabs 124, 125, 891, 1013, 1014, 13 at 40% to 60%.
  The mock swapped 28 at zero raw records and about 220 expanded items.
  Stump 56 is `SI_LAND`, so the slice re-runs `test_map39_south_edge.py`
  (`RETAIL_VOID_EXITS = 7709` exact) and drops any prefab that adds a
  standing level a walker can reach. Mock: `m39-lane-*`.
- **Oak line.** The 40 oaks 199 keep their collision role (neighbours
  overlap 24 units or more in x). Their y wanders by a hashed offset that
  keeps the maximum y at 20343 or more, so the line stops reading as ruled.
- **Lawn.** The four spires 66 at (17800,19900), (17220,20000),
  (17380,19960), (17540,20010) become bush clumps 434 of three (VQ-149). The
  19 bushes regroup into five clumps.
- **Moat bank.** Earth-bank prefabs 379, 613, 616 on the harbour columns if
  expansion allows; otherwise deferred.

**No-touch.** Egg 73 (17150,19700,48) and its ±128 hatch box; apparition 411
(17150,19850,48); the leg through the lane tunnel (x 16096..16223,
y 19584..19968); `TENEBRAE_GATE_THRESHOLDS`; the 4,623 pristine records as
raw prefix; no non-oak solid with a top in [56,128) within a body width of
an oak; rocks 181 units or more north of the trees; the canal (D9).

**Budget.** Raw at most 6,000; expansion at most 31,000.

## 4. Acceptance

### 4.1 Per-region targets (`dressing_metrics.TARGETS`)

A floor sits at or under the weakest retail map of the type; a ceiling at or
over it. `village`, `shore`, and `ruin` have no single-type retail map and
borrow from `barren` and `town`.

| Type | props / 100, min | dressed, min | bare, max | grouped, min | stride, max | top material, max | seams, min | period excess, max | modal chunk, max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| barren | 3.5 | 24% | 15% | 60% | 75% | 55% | 10% | 35% | 25% |
| shore | 5.0 | 24% | 15% | 60% | 75% | 55% | 10% | 35% | 25% |
| ruin | 8.0 | 24% | 15% | 60% | 75% | 55% | 10% | 35% | 25% |
| village | 15.0 | 45% | 10% | 80% | 75% | 55% | 10% | 35% | 25% |
| town | 20.0 | 45% | 10% | | | | | | |
| cave | 5.0 | 50% | 18% | 45% | 65% | 65% | | 40% | 50% |
| lava | 1.5 | 25% | 35% | | | 70% | 10% | | 60% |
| temple | 8.0 | 34% | 20% | | 75% | 80% | | 35% | |
| sky | 7.0 | 14% | 25% | | | | | | 62% |

Regions under 400 ground cells skip the two repetition limits
(`REPEAT_MIN_CELLS`). Density also has an aim band so a slice does not bury
a region in pebbles: barren 4 to 12, cave 6 to 20, village 15 to 30 props
per 100 cells. The mock's Map 13 valley reads 25.3 and is over the band.

### 4.2 Per-map numbers

| Map | props / 100, min (now) | top material, max (now) | bare, max (now) | period excess, max (now) | raw ceiling (now, cap) | expanded per ground cell, max (now) |
|---|---:|---:|---:|---:|---:|---:|
| 9 | 8 (4.9) | 65% (77%) | 5% (1%) | 40% (51%) | 1,800 (1,226; 2,500) | 2.9 (2.77) |
| 10, inside the outline | 6 (1.8) | 50% (59%) | 12% (26%) | 30% (27%) | 20,000 (21,864; 25,000) | 2.0 (1.22) |
| 11 | 5 (0.9) | 45% (34%) | 10% (10%) | 40% (58%) | 10,000 (10,065; 12,000) | 2.9 (1.75) |
| 13 | 5 (1.3) | 45% (36%) | 15% (36%) | 30% (18%) | 7,000 (6,298; 9,000) | 2.9 (1.49) |
| 17, city box | 8 (7.9) | 72% (78%) | 15% (30%) | 20% (13%) | 9,500 (9,284; 12,000) | 2.0 (1.41) |
| 18 | 8 (5.9) | 65% (73%) | 5% (3%) | 40% (45%) | 2,400 (2,388; 3,000) | 2.9 (2.85) |
| 8 | region targets only | | | | 6,500 (5,923; 7,000) | whole-map expansion 31,000 |
| 39 | region targets only | | | | 6,000 (5,085; 6,500) | whole-map expansion 31,000 |

Map 18's expanded ceiling leaves almost no room; its dressing arrives by
substitution and by removing the 895 backings first.

### 4.3 The permanent test

`agents/map-populator/src/test_dressing.py`, written by slice 0 beside
`test_visual_quality.py`:

1. For each map, `measure_regions` and the whole-map `measure` on the built
   `FIXED.DAT` with the built GLOB.FLX.
2. A pin file per map, `dressing_pins/mapNN.json`, holds each `RATCHET`
   value per region. A `min` value may only rise and a `max` value may only
   fall, with `--record` rewriting the file as `test_visual_quality.py`
   does.
3. Target failures are listed per region. At slice 0 the 118 current
   failures are recorded as the baseline; a map's slice exits with zero for
   that map, or with each survivor named in `dressing_pins` as an allowance
   with the reason (a shot window that fixes the floor, for example).
4. Record limits: the raw ceilings and the expanded-per-cell limits of §4.2,
   and `RECORD_BUDGET` stays the hard cap in `build_all_maps.py`.
5. Three structural checks that numbers miss: no prefab is 4-adjacent to
   itself more than twice in a row; no prop of 64 units or more in footprint
   stands inside a leg band; no dressing record paints into a shot window.

`test_visual_quality.py` keeps running. Decision D3 changes two of its pins:
Maps 11 and 18 are class `cave` (limits mean 47%, p95 77%, max 91% frame
black), and their frame-black pins rise when the 895 fill goes, staying
inside the class limits. That re-record needs Douglas's yes.

### 4.4 Astra's re-tour

Per region, Astra receives the region's "reads as" sentence, its mock from
`phase4/`, the phase 2-3 capture, and the new in-engine 640x400 capture, and
returns:

- **reads-as:** yes, partly, or no, with the evidence in the frame;
- **generated-look check:** any lattice, stride, stacked wall top, roof
  square on a stride, or repeating corner tile, each with frame coordinates;
- **the 13 regressed items** by id, regraded: VQ-025, 028, 061 (Map 10);
  VQ-045, 065 (Map 11); VQ-056, 063 (Map 18); VQ-037, 052, 058 (Map 13);
  VQ-051 (Map 9); VQ-023, 044 (Map 8). A slice exits with none of its items
  still regressed;
- **new problems,** as in phases 2-3.

Astra also grades the mocks before any builder work (plan §7.1). Grades go
to `/tmp/claude-1000/vq4/grade/grade-mNN-K.json` in the phase 2-3 schema,
in short checkpointed runs.

### 4.5 Douglas's notes from the walkable viewer

`docs/map-feedback/OPEN.md` is generated by
`tools/map_viewer/feedback_server.py` from `events.jsonl`. It reads "Nothing
open" today. Each slice reads it at start and again before it exits. A note
inside a region is a requirement for that region and outranks this document;
the slice records the note's id, what it changed, and answers it through the
server's API. A note that contradicts a no-touch item stops the slice and
comes back as a question.

## 5. The shared dressing module

`agents/map-populator/src/lv_dressing.py`, written by slice 0, generalises
`build_map_13.build_dressing` and `lv_cave_vignette.Cave.dress`.

### 5.1 API

```python
site = lv_dressing.Site(mapnum, items, shapes, seed)
# Built once per builder after all geometry and quest content, before any
# void fill. Expands globs, derives the floor, and assembles the exclusions.

site.swap_chunks(plain=397, family=ROCK_DRESSED, share=0.40, where=box)
# Egg substitution. Returns the eggs changed.

site.clusters(kit=KIT_DEADWOOD, per100=4.0, where=box,
              floors={4, 386}, anchor='seam')     # 'wall', 'seam', 'water', 'open'
# Loose clusters of two to five pieces. Returns the records added.

site.set_piece('dry riverbed', pieces)
# Hand-authored records. Validated against every exclusion; raises on a
# violation and names the piece.

site.beyond(kind, where=box)      # 'dark', 'stars', 'lava', 'water', 'shore', 'rock', 'forest'
# Fills void cells in view of a floor (lv_furnish.cells_within_view) with
# one prefab egg per chunk, or 564:2 plates for 'dark'.

site.pack()
# Last. Folds loose dressing and loose ground into LV prefabs per chunk
# (section 5.5) and returns the final item list.

site.report()     # per-region dressing_metrics rows and the record ledger
```

Kits and families live in `lv_dressing.py` as named constants (`ROCK_DRESSED`,
`ROCK_FUNGUS`, `SHORE_SE`, `SHORE_NW`, `LAVA_SEA`, `STARS`, `GRASS_FOREST`,
`KIT_DEADWOOD`, `KIT_STONE`, `KIT_BONES`, `KIT_HALL`, `KIT_YARD`). The
values in `phase4/make_mocks.py` are the starting set.

### 5.2 Exclusions

`Site` builds one 32-unit mask and every placement consults it:

| Source | Excluded |
|---|---|
| `test_vignettes` windows | any piece whose projected box plus 16 px reaches a window (`build_map_13.in_a_window` is the model) |
| `quest_legs.leg_cells(mapnum, items, shapes)` | solids within the band plus 64 units; flats (zd 0, no `SI_SOLID`) are allowed in the band |
| `map_pins.json` | 96 units round every pinned item; the hatch box of every egg; 128 round every teleport pad |
| movable items | their clear boxes and reach rays (Map 17's 26, Map 9's body, pack, and sword) |
| 497, 498, 501, 846 | no solid within 32 units, so a barrier is never thickened or stepped |
| per-map lines | `FIRE_LINES` and `LAVA_MARGIN`, `TRACKS`, `VALLEY_CLEAR`, the Map 18 entry lane, monster boxes |
| south and east rims | no piece taller than 40 within 8 times its height of a scripted point (`item_sorter.overdrawn`) |

**Paint-cycle safety.** Before a piece is accepted: its box overlaps no
solid; no item with zd of 8 or more lies within 80 units when the piece is a
small flat; nothing rests on a solid's top face; an overlay on a floor is a
flat with neither `SI_DRAW` nor `SI_OCCL`. `test_paint_cycles` runs in every
slice, and the verifier runs the affected stops with the Object channel on.

**Standing levels.** A piece with `SI_LAND|SI_SOLID` goes in only at a z on
the 4-unit lattice and only where `exact_reach` shows no new reachable top;
otherwise the kit's non-land alternative is used.

### 5.3 Clustering rules

1. Cluster seeds are at least 448 units apart; cluster size is drawn from
   (2, 3, 3, 4, 5); pieces sit on the 32-unit lattice within 160 units of the
   seed.
2. A cluster of three or more holds at least two shapes.
3. At least 60% of a region's seeds are anchored: at a wall foot, on a
   material seam, at a water edge, or beside a set piece. Open-ground seeds
   make up the rest.
4. The median nearest-neighbour distance of a region's small props is 128
   units or less.
5. A prefab family has at least four members in use per region; no member
   is more than 25% of that region's substituted chunks; no member is
   4-adjacent to itself more than twice.
6. Frames come from an rng seeded by (map, cell), never from a linear
   formula of x and y (`organic-maps.md` §1 item 3).
7. Solid-bearing prefabs (spires, stumps, trees) need the whole chunk
   outside every leg band; flat-only prefabs (956, 957) may touch a band.
8. A chunk qualifies for substitution only when its egg is the plain member
   and no other record of the builder's lies in the chunk box.
9. Rows keep their count and lose their ruler: any run of four or more of
   one shape on one line gets hashed offsets of 32 to 64 units, and one in
   four becomes a broken or fallen variant.

### 5.4 What it replaces

| Existing code | Becomes |
|---|---|
| `build_map_13.build_dressing` and its constants | `site.clusters` with the same measured parameters |
| `lv_cave_vignette.Cave.dress` (Maps 9, 11, 18) | `site.clusters(anchor='wall')` |
| `build_map_10.build_wilderness` and the per-zone scatter in `props()` lists | `swap_chunks`, `clusters`, and named `set_piece`s |
| `TENEBRAE_BUSHES`, `TENEBRAE_LANE_SCATTER` | `clusters` and `swap_chunks` |
| hand lists of 66, 796, 186, 300 in `build_map_09` and `build_map_11` | removed or `clusters` |
| `stone_void_cover` (11), `textured_void` (18), `route_backdrops` skirts (8), `valley_water_skirt` (13), the water part of `edge_skirt` (10), the black part of `cloud_sea`'s surround (17), `tenebrae_skirt` (39) | `site.beyond(kind)` |
| `lv_furnish.void_floor` | stays, called last, as the fallback that guarantees no unpainted cell |

`lv_furnish.column`, `raised_platform`, `accent_reliefs`, and
`lv_landscape.rim` stay as they are.

### 5.5 Staying under the record caps

Three levers, in the order they are used:

1. **Substitution, zero records.** Rock, grass, and filler chunks change
   their glob number. This works today with retail's GLOB.FLX.
2. **Plates to eggs.** A void fill of four 256-unit plates per chunk becomes
   one egg. Measured in the mocks: Map 11 minus 299 in one quadrant, Map 17
   minus 417, Map 18 minus 298 by removal.
3. **LV prefabs (decision D2).** `site.pack()` folds what is left:
   - *Authored prefabs* in `lv_globs.py`: about 60 named chunks for barren
     earth, mixed rock and earth, cloud and gold, flagstone, and village
     yards, numbered from 3072.
   - *Packed ground:* any chunk whose loose ground tiles are all quality 0,
     flag-free, unpinned, and on odd coordinates becomes one prefab, deduped
     by content hash. Map 10 holds 9,685 loose tiles of 301, 4, and 386
     (inside and outside the outline), all flag-free, 9,680 of them on odd
     coordinates, in 777 chunk-and-height groups. Packing them takes raw
     from 21,864 to about 13,000. That is the room Map 10's dressing needs.

Without D2, Map 10 has 3,136 records of headroom and its loose clusters
alone (the mock added 271 for one of twelve regions) would use most of it.

Fast-area load is checked separately by the expanded-per-cell limit and by
the verifier's object-count reading at the densest stop of each map.

## 6. Mock renders

All in `docs/research/2026-11-01-visual-pass/phase4/`, produced by
`python3 make_mocks.py` (20 seconds) from the built `FIXED.DAT` with the
viewer's painter. Each mock is the built record list with the direction's
edits applied; no builder ran. They contain Origin art and stay uncommitted.

| Map | Region | Files | Edits and measured effect |
|---|---|---|---|
| 8 | south shelf | `m08-south-shelf-before.png`, `-mock.png`, `-mock-quarter.png` | 391 skirt plates of 895 removed; raw 5,923 to 5,532 |
| 9 | hall | `m09-hall-*` | nine 186 and 796 records out, five egg swaps, eight cluster pieces; props per 100 from 3.9 to 23.8 |
| 10 | north plain | `m10-north-plain-*` | 26 egg swaps, 271 cluster pieces; props per 100 from 0.4 to 11.3, dressed 4% to 42%, bare 19% to 3%, target failures 6 to 1 |
| 11 | Fire, north wall | `m11-fire-north-wall-*` | 895 plates to lava eggs, 22 egg swaps; raw 10,065 to 9,766; target failures 3 to 0 |
| 13 | valley | `m13-valley-*` | 20 egg swaps, 31 shore swaps, 19 cluster pieces; target failures 6 to 3 |
| 17 | arrival edge | `m17-arrival-edge-*` | black plates to star eggs; raw 9,284 to 8,867 |
| 18 | outer hall | `m18-outer-hall-*` | 313 backings of 895 and four frame-5 tapestries removed, 19 cluster pieces; raw 2,388 to 2,090 |
| 39 | lane | `m39-lane-*` | 28 forest swaps, four spires to 12 bush pieces; raw 5,085 to 5,093 |

Reference images in the same folder: `globs-retail-A.png`,
`globs-retail-B.png` (72 prefabs, labelled with number and item count),
`retail-reference-frames.png` (retail Maps 7, 43, 63, 49 at game scale),
`retail-overviews.png`, `retail-overviews-barren.png`,
`retail-map07-overview.png`.

What the mocks leave out, which the builders must not: legs are straight
lines between endpoints; shot windows and pins are not consulted; paint
cycles are not checked; the lava and star chunks snap to wherever a plate
stood, so the Map 11 mock shows a lava chunk inside the screen05 pocket's
outer wall; the hall kit on Map 18 is random scatter where the direction
wants a dais and regrouped benches; Map 17's sea edge is still straight; the
Map 13 valley is over its density band.

I looked at every before and mock frame at game scale. I did not open the
eight quarter-scale frames.

## 7. Slices and order

| Slice | Owner | Files owned | Exit checks |
|---|---|---|---|
| 0, shared | one Codex agent, merged first | new: `lv_dressing.py`, `lv_globs.py`, `test_dressing.py`, `dressing_pins/`; edits: `dressing_metrics.py`, `lv_furnish.py`, `lv_landscape.py`, `lv_cave_vignette.py`, `glob_catalog.py` (`GlobReader` default), `u8_flex.py` (writer), `tools/build_artifacts.sh`, `install_lv.sh`, `ARTIFACTS.sha256`, `lv_manifest.json`, `build_all_maps.py` (budgets) | FIXED.DAT byte-identical to `f1c3ccc1` with the module imported and unused; GLOB.FLX built with retail's 3,072 slots byte-identical and LV slots appended; estate green; baseline pins recorded |
| 18 | one agent | `build_map_18.py` | §3.5 |
| 9 | one agent | `build_map_09.py` | §3.6 |
| 8 | one agent | `build_map_08.py` | §3.7 |
| 39 | one agent | `build_map_39.py` | §3.8 |
| 11 | one agent | `build_map_11.py` | §3.4 |
| 13 | one agent | `build_map_13.py`, `lv_map13_tiers.py` | §3.2 |
| 17 | one agent | `build_map_17.py` | §3.3 |
| 10 | one agent | `build_map_10.py`, `lv_map10_ground.py`, `lv_vale_terrain.py`, `build_villages.py` | §3.1 |

Every map slice exits on the same list:

1. `test_dressing.py` shows zero target failures for the map, or named
   allowances.
2. `test_visual_quality.py`, `test_vignettes.py` (every floor within 0.25),
   `test_paint_cycles.py`, `test_route_reach.py`, `test_map_hygiene.py`
   (`void_in_view` 0), `test_crack_geometry.py`, and the map's own tests
   pass; `tools/run_all_tests.sh` is green.
3. `map_pins.json` rows for the map are unchanged.
4. Raw and expanded counts are inside §4.2.
5. The slice report lists each shot window it draws near, each regressed VQ
   item it claims, each stand-in it replaced, and each feedback note it
   answered.

**Order.** Slice 0, then 18, 9, 8, and 39 in parallel (small, and they
exercise every `beyond` kind except shore and stars), then 11, 13, and 17 in
parallel, then 10 alone. A map slice that needs a new kit or prefab adds it
through a pull request against slice 0's files, merged before the map slice;
map slices do not edit shared modules. Each merge follows plan §8:
`codex exec review`, merge with pins resolved per map, `tools/integrate.sh
--record`, estate, verifier pass in ScummVM on a fresh world, Astra re-tour,
card page. One full quest replay runs after slice 10.

## 8. Decisions for Douglas

**Douglas's answers (2026-11-09).** These override the recommendations
below wherever they differ; every slice reads this table first.

| # | Answer | Effect on the slices |
|---|---|---|
| D1 | **(c) as (b), plus a hand-authored set piece in every region** (not the recommendation) | Each map slice designs one set piece per region it owns: hand-placed, not from `lv_dressing`, named in its report with its 640x400 capture. §3's set-piece lists are the starting point. |
| D2 | (a) GLOB.FLX is a sixth artifact; LV prefabs from slot 3072 | as recommended; slice 0 builds it |
| D3 | (a) darkness beyond cave and hall walls; lava round Fire, dark water round Water, rock behind Earth | as recommended |
| D4 | (a) star field beyond the cloud sea, ragged cloud edge | as recommended |
| D5 | (b) canon barren, plus reeds and moss within three cells of water | as recommended |
| D6 | (a) rock shore with coves, deep water beyond | **Corrected 2026-11-09:** the shore is the 1994 cliff shore of §2.1, not retail river-shore globs (Douglas: "map13 shores look wrong ... the wrong tiles"). Map 13 mocks it first for sign-off; Map 10 follows. |
| D7 | (a) replace Hoskuld's keep with a long hall in the 1994 hut kit | as recommended |
| D8 | (b) cloud-rim lobes (shape 898) only if Astra still grades the cloud edge hard | as recommended |

**D1 (plan §6.3). How far phase 4 goes.**
(a) A density target per map. (b) Each region reads as its place, graded by
Astra against a sentence, with the §4 numbers as floors. (c) As (b), plus a
hand-authored set piece in every region.
I would pick (b) because the numbers alone pass a pebble field, and (c)
doubles the hand work on Map 10.

**D2. GLOB.FLX as a sixth build artifact.**
(a) Yes: LV prefabs from slot 3072, authored and packed. (b) Retail prefabs
only, by substitution. (c) No prefab work.
I would pick (a) because retail has nothing for barren earth, cloud, or
gold, and Map 10 cannot reach its density under 25,000 records without
packing.

**D3. Beyond cave and hall walls on Maps 9, 11, and 18.**
(a) Darkness, with lava round Fire, dark water round Water, and rock behind
Earth; the frame-black pins for Maps 11 and 18 are re-recorded inside the
cave class limits. (b) Keep the 895 paving. (c) Commission a dark rock
ceiling tile.
I would pick (a) because it is what retail does and it clears four of the 13
regressions.

**D4. Beyond the cloud sea on Maps 17 and 13.**
(a) A star field (retail globs 2916 and 2632). (b) Black. (c) Flat navy 896.
I would pick (a) because retail's own sky map uses it and it costs fewer
records than black.

**D5. Green in the Vale.**
(a) Canon barren: green only as crops, Ezrekal's herbs, and the Test Plant.
(b) As (a), plus reeds and moss within three cells of water. (c) Grass
meadows.
I would pick (b) because the 1994 notes hold green for the ending, and a
little at the water keeps the lake from reading as oil.

**D6. The Vale's south and east edge.**
(a) A rock shore with coves on the first water ring, deep water beyond.
(b) Keep the flush strip. (c) A raised rim.
I would pick (a) because it keeps your D3 flush edge and its barriers, and
the Map 13 mock shows it reading as a coast.

**D7. Hoskuld's keep (glob 573) among the huts.**
(a) Replace it with a long hall in the 1994 hut kit. (b) Keep it.
I would pick (a) because it is on the plan's stand-in list and the kit is
already proven in screens 19, 20, and 22.

**D8. New art.**
(a) None in phase 4; retail and existing LV shapes only. (b) Draw cloud rim
lobes (next ID 898) if Astra still grades the cloud edge as hard after the
ragged outline.
I would pick (b) because the reconstruction notes the 1994 lobes as "not
recovered" and nothing in retail stands in for them.

## 9. Summary

- **Region types:** barren, village, shore, ruin, cave, lava, temple, sky,
  and town, across the 39 `REGIONS` rows on eight maps.
- **Headline numbers:** retail is x3.8 to x10.8 expanded per raw record with
  76% to 93% of outdoor props inside prefabs; ours is x1.0 to x2.2 with
  none. Our maps hold 0.9 to 5.9 props per 100 cells against 3.8 (barren) to
  34 (town). The region table shows 118 target failures today.
- **The void decisions:** darkness for caves and halls, lava and water round
  Map 11's Fire and Water, a rock shore for the Vale and the Map 13 valley,
  stars beyond the cloud sea, forest south of Tenebrae.
- **Slices:** one shared slice, then Maps 18, 9, 8, 39, then 11, 13, 17,
  then 10.
- **Decisions needed:** D1 to D8 above; D2 and D3 block slice 0.

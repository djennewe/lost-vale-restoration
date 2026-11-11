# Map 10 phases two and three visual pass

4 November 2026. Branch `wt/vq2-m10`, based on `ba34836`.

The build improves the assigned map slice and preserves the exact original arrival flood. Strict phase exit remains incomplete: 336 quest-band cells below half visibility remain. The permanent ratchet passes; this is a partial completion of the design acceptance numbers.

## Item findings, stop measurements, and images

Stop tables use the phase baseline: gate zero to phase two for phase two items, then phase two to final for phase three items. Walkable black is the exact stop floor probe (zero or one); the map-wide census below covers every reached 32-unit lattice position. Frame black is percent of 640×400 pixels, including unpainted pixels. Minimum visibility evaluates 72 Avatar poses. Values are before → after. Image links lead to fresh engine captures.

### VQ-025: Vale east and south rim faces hide the Avatar

Status: **fixed**. Raised south and east exterior rims painted over the Avatar. All original ground now receives flush S/E edges at the adjacent ground height and two invisible 497/498 courses at h and h+48. Ground at z0 looks across the phase three water skirt. Two cloud-canyon end cells retain their raised supports so their existing walls retain their placement. All 11 cited stops exceed half visibility.

| Stop | Walkable black | Frame black | Minimum visible | Images |
|---|---:|---:|---:|---|
| m10b-29 | 0 → 0 | 54.9582% → 61.2102% | 0.000% → 100.000% | [before](m10/before/m10b-29.png), [after](m10/phase2/m10b-29.png) |
| m10b-32 | 0 → 0 | 37.0562% → 45.2500% | 0.000% → 100.000% | [before](m10/before/m10b-32.png), [after](m10/phase2/m10b-32.png) |
| m10b-33 | 0 → 0 | 37.1133% → 45.3070% | 0.000% → 100.000% | [before](m10/before/m10b-33.png), [after](m10/phase2/m10b-33.png) |
| m10b-38 | 0 → 0 | 37.0562% → 45.2586% | 0.000% → 100.000% | [before](m10/before/m10b-38.png), [after](m10/phase2/m10b-38.png) |
| m10b-41 | 0 → 0 | 37.0562% → 45.2500% | 0.000% → 100.000% | [before](m10/before/m10b-41.png), [after](m10/phase2/m10b-41.png) |
| m10b-47 | 0 → 0 | 37.1812% → 45.4000% | 0.000% → 100.000% | [before](m10/before/m10b-47.png), [after](m10/phase2/m10b-47.png) |
| m10b-51 | 0 → 0 | 49.0125% → 57.2625% | 0.000% → 100.000% | [before](m10/before/m10b-51.png), [after](m10/phase2/m10b-51.png) |
| m10b-52 | 0 → 0 | 39.8125% → 48.0625% | 0.000% → 100.000% | [before](m10/before/m10b-52.png), [after](m10/phase2/m10b-52.png) |
| m10b-56 | 0 → 0 | 37.0562% → 45.2500% | 0.000% → 100.000% | [before](m10/before/m10b-56.png), [after](m10/phase2/m10b-56.png) |
| m10b-60 | 0 → 0 | 36.0562% → 44.2375% | 0.000% → 100.000% | [before](m10/before/m10b-60.png), [after](m10/phase2/m10b-60.png) |
| m10b-64 | 0 → 0 | 24.8062% → 31.7285% | 2.561% → 100.000% | [before](m10/before/m10b-64.png), [after](m10/phase2/m10b-64.png) |

### VQ-027: Raised reliefs hide adjacent floor positions

Status: **improved**. The exterior rim hid the cache witness; its flush boundary restores m10b-59 to full visibility. Three internal relief witnesses remain: m10a-41 is covered by the retained screen09 cliff, m10a-47 by the garden mesa top floors, and m10b-46 by the Sacred Circle crest. A one-cell recess left the first two witnesses reachable and unchanged in visibility. Further relief reconstruction needs a design that preserves the protected window pixels and original route. The 336 remaining low-visibility quest-band cells are reported, and their pin was lowered from 841.

| Stop | Walkable black | Frame black | Minimum visible | Images |
|---|---:|---:|---:|---|
| m10a-41 | 0 → 0 | 0.0770% → 0.0770% | 40.895% → 40.895% | [before](m10/before/m10a-41.png), [after](m10/phase2/m10a-41.png) |
| m10a-47 | 0 → 0 | 0.0758% → 0.0758% | 11.809% → 11.809% | [before](m10/before/m10a-47.png), [after](m10/phase2/m10a-47.png) |
| m10b-46 | 0 → 0 | 2.5520% → 4.9367% | 38.191% → 38.191% | [before](m10/before/m10b-46.png), [after](m10/phase2/m10b-46.png) |
| m10b-59 | 0 → 0 | 21.8219% → 26.3672% | 0.000% → 100.000% | [before](m10/before/m10b-59.png), [after](m10/phase2/m10b-59.png) |

### VQ-028: Passage Test canyon walls hide the Avatar

Status: **fixed**. High exterior rim courses beside the Passage Test ramp obscured the lower corridor. Flush edges follow each ramp row height; original two-course barriers remain. End-support cells at (50, 192) and (61, 192) stay at 104 because lowering them moved existing canyon wall ends and removed eight original reached cells in a rejected trial. Final exact reach is identical, and all three witnesses exceed half visibility. The spire paint-cycle test passes.

| Stop | Walkable black | Frame black | Minimum visible | Images |
|---|---:|---:|---:|---|
| m10b-20 | 0 → 0 | 15.3320% → 20.9145% | 31.941% → 90.464% | [before](m10/before/m10b-20.png), [after](m10/phase2/m10b-20.png) |
| m10b-58 | 0 → 0 | 36.9563% → 45.1375% | 0.000% → 100.000% | [before](m10/before/m10b-58.png), [after](m10/phase2/m10b-58.png) |
| m10b-61 | 0 → 0 | 21.3371% → 27.2598% | 78.780% → 100.000% | [before](m10/before/m10b-61.png), [after](m10/phase2/m10b-61.png) |

### VQ-033: Temple pit near wall hides the stair-foot Avatar

Status: **fixed**. Four generated face records at (18559, 23423), z8 and 56, cover the temple stair tail. Coincident 497/498 replacements retain collision dimensions and remove their LAND flag. The temple landing improves from 0% to 95.375% worst-pose visibility. Trigger211, PAD_210, stair geometry, and pinned records retain their values; temple_stair_foot passes.

| Stop | Walkable black | Frame black | Minimum visible | Images |
|---|---:|---:|---:|---|
| m10b-17 | 0 → 0 | 0.4473% → 0.5133% | 0.000% → 95.375% | [before](m10/before/m10b-17.png), [after](m10/phase2/m10b-17.png) |

### VQ-034: Vale boundary and canyon rims lack a visible backdrop

Status: **fixed**. The old field ended at black void plates. A deterministic 16-cell (2048-unit) skirt continues N/W rock at the adjacent 104/152/160 rim height and paints water outside flush S/E edges. Four cells did not cover the full configured view wedge. Skirt cells stay outside walk, use globs where possible, and preserve a pre-skirt height snapshot for prop lifting and a pre-skirt edge list for barriers. Concave flush-edge wedges are forced to z0 water so neighbouring high skirts cannot obscure the route. The far south skirt becomes water before the signed-coordinate limit. No final sampled frame exceeds 10% black.

| Stop | Walkable black | Frame black | Minimum visible | Images |
|---|---:|---:|---:|---|
| m10a-02 | 0 → 0 | 1.8062% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10a-02.png), [after](m10/after/m10a-02.png) |
| m10a-03 | 0 → 0 | 0.5941% → 0.0879% | 100.000% → 100.000% | [before](m10/phase2/m10a-03.png), [after](m10/after/m10a-03.png) |
| m10a-07 | 0 → 0 | 6.9648% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10a-07.png), [after](m10/after/m10a-07.png) |
| m10a-09 | 0 → 0 | 0.1660% → 0.1660% | 100.000% → 100.000% | [before](m10/phase2/m10a-09.png), [after](m10/after/m10a-09.png) |
| m10a-35 | 0 → 0 | 1.1430% → 0.0867% | 100.000% → 100.000% | [before](m10/phase2/m10a-35.png), [after](m10/after/m10a-35.png) |
| m10a-46 | 0 → 0 | 4.5598% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10a-46.png), [after](m10/after/m10a-46.png) |
| m10a-53 | 0 → 0 | 10.0633% → 0.1688% | 100.000% → 100.000% | [before](m10/phase2/m10a-53.png), [after](m10/after/m10a-53.png) |
| m10a-57 | 0 → 0 | 18.5801% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10a-57.png), [after](m10/after/m10a-57.png) |
| m10a-58 | 0 → 0 | 21.3285% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10a-58.png), [after](m10/after/m10a-58.png) |
| m10a-59 | 0 → 0 | 19.6770% → 1.0621% | 99.875% → 99.875% | [before](m10/phase2/m10a-59.png), [after](m10/after/m10a-59.png) |
| m10a-60 | 0 → 0 | 31.2699% → 0.8840% | 95.854% → 95.854% | [before](m10/phase2/m10a-60.png), [after](m10/after/m10a-60.png) |
| m10b-07 | 0 → 0 | 5.8758% → 0.5160% | 100.000% → 100.000% | [before](m10/phase2/m10b-07.png), [after](m10/after/m10b-07.png) |
| m10b-21 | 0 → 0 | 43.6949% → 1.8590% | 100.000% → 100.000% | [before](m10/phase2/m10b-21.png), [after](m10/after/m10b-21.png) |
| m10b-23 | 0 → 0 | 20.5102% → 0.0063% | 100.000% → 100.000% | [before](m10/phase2/m10b-23.png), [after](m10/after/m10b-23.png) |
| m10b-25 | 0 → 0 | 20.4703% → 0.0063% | 100.000% → 100.000% | [before](m10/phase2/m10b-25.png), [after](m10/after/m10b-25.png) |
| m10b-28 | 0 → 0 | 4.6410% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10b-28.png), [after](m10/after/m10b-28.png) |
| m10b-29 | 0 → 0 | 61.2102% → 1.4062% | 100.000% → 91.160% | [before](m10/phase2/m10b-29.png), [after](m10/after/m10b-29.png) |
| m10b-31 | 0 → 0 | 13.9535% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10b-31.png), [after](m10/after/m10b-31.png) |
| m10b-32 | 0 → 0 | 45.2500% → 0.0000% | 100.000% → 90.802% | [before](m10/phase2/m10b-32.png), [after](m10/after/m10b-32.png) |
| m10b-33 | 0 → 0 | 45.3070% → 0.0570% | 100.000% → 91.160% | [before](m10/phase2/m10b-33.png), [after](m10/after/m10b-33.png) |
| m10b-38 | 0 → 0 | 45.2586% → 0.0086% | 100.000% → 90.802% | [before](m10/phase2/m10b-38.png), [after](m10/after/m10b-38.png) |
| m10b-41 | 0 → 0 | 45.2500% → 0.0000% | 100.000% → 91.160% | [before](m10/phase2/m10b-41.png), [after](m10/after/m10b-41.png) |
| m10b-46 | 0 → 0 | 4.9367% → 0.0000% | 38.191% → 38.191% | [before](m10/phase2/m10b-46.png), [after](m10/after/m10b-46.png) |
| m10b-50 | 0 → 0 | 13.9535% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10b-50.png), [after](m10/after/m10b-50.png) |
| m10b-51 | 0 → 0 | 57.2625% → 0.0000% | 100.000% → 96.419% | [before](m10/phase2/m10b-51.png), [after](m10/after/m10b-51.png) |
| m10b-52 | 0 → 0 | 48.0625% → 0.0000% | 100.000% → 91.160% | [before](m10/phase2/m10b-52.png), [after](m10/after/m10b-52.png) |
| m10b-56 | 0 → 0 | 45.2500% → 0.0000% | 100.000% → 91.160% | [before](m10/phase2/m10b-56.png), [after](m10/after/m10b-56.png) |
| m10b-58 | 0 → 0 | 45.1375% → 0.0000% | 100.000% → 90.802% | [before](m10/phase2/m10b-58.png), [after](m10/after/m10b-58.png) |
| m10b-60 | 0 → 0 | 44.2375% → 0.0000% | 100.000% → 96.419% | [before](m10/phase2/m10b-60.png), [after](m10/after/m10b-60.png) |

### VQ-036: Modular Vale cliff joins expose vertical black slits

Status: **improved**. Generated N/W faces selected black back-face frames, while NE post frames 6/7/9 were black or half-width. Exposed faces now select textured LIT frames and generated NE posts select full-width3/4/5. Height joins retain crest caps, closing an eight-unit band found by the verifier. Retained shot faces and posts stay unchanged. Thin residual painted seams remain, including 302 unpainted pixels at m10a-55 and 262 at m10b-17. A trial adding 128 physically safe corner posts changed none of the six inspected seam witnesses, and was omitted. Further closure needs matching art coverage or shot-face reconstruction that retains all window floors.

| Stop | Walkable black | Frame black | Minimum visible | Images |
|---|---:|---:|---:|---|
| m10a-55 | 0 → 0 | 0.1187% → 0.1187% | 100.000% → 100.000% | [before](m10/phase2/m10a-55.png), [after](m10/after/m10a-55.png) |
| m10a-57 | 0 → 0 | 18.5801% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10a-57.png), [after](m10/after/m10a-57.png) |
| m10a-59 | 0 → 0 | 19.6770% → 1.0621% | 99.875% → 99.875% | [before](m10/phase2/m10a-59.png), [after](m10/after/m10a-59.png) |
| m10a-62 | 0 → 0 | 0.2133% → 0.2133% | 100.000% → 100.000% | [before](m10/phase2/m10a-62.png), [after](m10/after/m10a-62.png) |
| m10b-15 | 0 → 0 | 0.5828% → 0.2723% | 100.000% → 100.000% | [before](m10/phase2/m10b-15.png), [after](m10/after/m10b-15.png) |
| m10b-16 | 0 → 0 | 0.4738% → 0.2723% | 90.464% → 90.464% | [before](m10/phase2/m10b-16.png), [after](m10/after/m10b-16.png) |
| m10b-17 | 0 → 0 | 0.5133% → 0.1969% | 95.375% → 95.375% | [before](m10/phase2/m10b-17.png), [after](m10/after/m10b-17.png) |
| m10b-18 | 0 → 0 | 31.4617% → 0.0746% | 100.000% → 100.000% | [before](m10/phase2/m10b-18.png), [after](m10/after/m10b-18.png) |
| m10b-20 | 0 → 0 | 20.9145% → 1.7855% | 90.464% → 90.464% | [before](m10/phase2/m10b-20.png), [after](m10/after/m10b-20.png) |
| m10b-46 | 0 → 0 | 4.9367% → 0.0000% | 38.191% → 38.191% | [before](m10/phase2/m10b-46.png), [after](m10/after/m10b-46.png) |
| m10b-47 | 0 → 0 | 45.4000% → 0.0000% | 100.000% → 90.802% | [before](m10/phase2/m10b-47.png), [after](m10/after/m10b-47.png) |
| m10b-55 | 0 → 0 | 0.3988% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10b-55.png), [after](m10/after/m10b-55.png) |
| m10b-57 | 0 → 0 | 3.8699% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10b-57.png), [after](m10/after/m10b-57.png) |
| m10b-61 | 0 → 0 | 27.2598% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10b-61.png), [after](m10/after/m10b-61.png) |
| m10b-62 | 0 → 0 | 6.3469% → 0.1023% | 77.889% → 77.889% | [before](m10/phase2/m10b-62.png), [after](m10/after/m10b-62.png) |
| m10b-63 | 0 → 0 | 42.8996% → 0.0922% | 100.000% → 100.000% | [before](m10/phase2/m10b-63.png), [after](m10/after/m10b-63.png) |

### VQ-041: Lake body and repeated blue edge sprites read as black stripes

Status: **fixed**. Ownership inspection identified glob 55 as the repeated stripes: its 16 tiles include four edge-frame water sprites. Existing glob 262 has the same tile positions and 16 navy 347:16 tiles. Generated lake and skirt water now use 262. Fresh engine comparisons at m10b-11 show the repeated generated edge sprites removed from open water; blue details inside the protected screenshot reconstruction remain. WATER_DEEP remains 16, and protected shot water, island underlays, causeway, and pier remain unchanged.

| Stop | Walkable black | Frame black | Minimum visible | Images |
|---|---:|---:|---:|---|
| m10a-49 | 0 → 0 | 0.0270% → 0.0270% | 100.000% → 100.000% | [before](m10/phase2/m10a-49.png), [after](m10/after/m10a-49.png) |
| m10a-55 | 0 → 0 | 0.1187% → 0.1187% | 100.000% → 100.000% | [before](m10/phase2/m10a-55.png), [after](m10/after/m10a-55.png) |
| m10b-10 | 0 → 0 | 0.0871% → 0.0871% | 100.000% → 100.000% | [before](m10/phase2/m10b-10.png), [after](m10/after/m10b-10.png) |
| m10b-11 | 0 → 0 | 0.1137% → 0.1137% | 100.000% → 100.000% | [before](m10/phase2/m10b-11.png), [after](m10/after/m10b-11.png) |
| m10b-12 | 0 → 0 | 0.0266% → 0.0266% | 100.000% → 100.000% | [before](m10/phase2/m10b-12.png), [after](m10/after/m10b-12.png) |
| m10b-42 | 0 → 0 | 0.0000% → 0.0000% | 100.000% → 96.419% | [before](m10/phase2/m10b-42.png), [after](m10/after/m10b-42.png) |

### VQ-042: Lake perimeter is rectangular and lacks a shore transition

Status: **improved**. The perimeter lacked articulated bank art. Generated outer lake and low coast banks now use 128 frames 3/2/9/10 outside all protected windows and a two-cell guard. Lake rails receive a second invisible course to prevent jumping onto the bank tops. Existing rails and the island stay intact. The estate reserves all new 126 records, so the proposed 126 earth-bank component is blocked by `test_art_props.py:692`. Physical corner erosion opened 144 additional reached cells in a rejected trial; the rectangular collision footprint is retained. A shared contract update permitting 126 bank frames 2/3/9/10 while retaining the plant 871 assertion would permit the earth-bank option.

| Stop | Walkable black | Frame black | Minimum visible | Images |
|---|---:|---:|---:|---|
| m10a-41 | 0 → 0 | 0.0770% → 0.0770% | 40.895% → 40.895% | [before](m10/phase2/m10a-41.png), [after](m10/after/m10a-41.png) |
| m10b-10 | 0 → 0 | 0.0871% → 0.0871% | 100.000% → 100.000% | [before](m10/phase2/m10b-10.png), [after](m10/after/m10b-10.png) |
| m10b-12 | 0 → 0 | 0.0266% → 0.0266% | 100.000% → 100.000% | [before](m10/phase2/m10b-12.png), [after](m10/after/m10b-12.png) |
| m10b-42 | 0 → 0 | 0.0000% → 0.0000% | 100.000% → 96.419% | [before](m10/phase2/m10b-42.png), [after](m10/after/m10b-42.png) |
| m10b-43 | 0 → 0 | 0.0426% → 0.0426% | 100.000% → 100.000% | [before](m10/phase2/m10b-43.png), [after](m10/after/m10b-43.png) |
| m10b-53 | 0 → 0 | 0.1168% → 0.1168% | 100.000% → 100.000% | [before](m10/phase2/m10b-53.png), [after](m10/after/m10b-53.png) |

### VQ-057: Tier scaffold corner exposes a black support gap

Status: **improved**. The scaffold corner exposed the boundary beyond the tier. The extended skirt and restored crest cap fill its background and height join; the scaffold itself retains its records. m10a-48 has zero unpainted frame pixels. m10a-61 retains 32 unpainted pixels elsewhere in the frame, so the item remains conservatively marked improved pending visual regrading.

| Stop | Walkable black | Frame black | Minimum visible | Images |
|---|---:|---:|---:|---|
| m10a-48 | 0 → 0 | 0.0715% → 0.0000% | 100.000% → 100.000% | [before](m10/phase2/m10a-48.png), [after](m10/after/m10a-48.png) |
| m10a-61 | 0 → 0 | 0.4621% → 0.1910% | 93.430% → 93.430% | [before](m10/phase2/m10a-61.png), [after](m10/after/m10a-61.png) |

### VQ-061: Lava extension contains black gaps against the rock

Status: **improved**. The lava/rock witness saw exposed terrain joins and the black background. The skirt, textured generated faces/posts, and retained crest caps reduce its frame black. All 54 lava records retain their full tuples, including footprint and frame; no lava cell or frame33 was added. m10a-54 retains 273 unpainted pixels in the whole frame. Further local seam closure needs matching painted coverage within the protected-window constraints.

| Stop | Walkable black | Frame black | Minimum visible | Images |
|---|---:|---:|---:|---|
| m10a-54 | 0 → 0 | 1.5668% → 0.2391% | 100.000% → 100.000% | [before](m10/phase2/m10a-54.png), [after](m10/after/m10a-54.png) |

### The 31 specified floor probes

Status: **fixed**. Own-material floors and offset under-floors repair all 16 garden/stair probes, all four Gunnar probes, and all 11 Hrodny probes. Four invisible closure columns at (19424, 7616), (19264, 7520), (20288, 8639), and (20447, 8767), each at z0/48, prevent 20 newly supported cells while preserving every original reached cell. The first three use existing 497/498 walls; the last uses retail's existing 96×32×48 invisible wall 846. Its SI_EDITOR flag hides it in the engine. No custom art ID was added.

The final Hrodny repair combines existing earth4 and transition386 floor art with precisely fitted closure columns. An earlier individual-floor search rejected broad tiles because they opened six additional cells. A later combined search found that exact one-unit anchor offsets let 497 and 846 close those cells without touching original reached Avatar bodies. Independent full-map verification confirms zero specified-black probes, 42 prop-black probes, exact original reach, unchanged leg count, and all window floors. [Exact floor and wall tuples](m10/constraints/hrodny-complete-plan.json), [independent candidate metrics](m10/constraints/hrodny-complete-metrics.json).

Screen21 improves and its holes fall from 540 to zero. The seven-probe debt in the initial phase-three commit is resolved by completion commit `1965524`.

| Region | Specified black before | After |
|---|---:|---:|
| Garden and stair |16|0|
| Gunnar |4|0|
| Hrodny |11|0|
| Total |31|0|

## Screenshot windows

Every window retains its FLOORS value, tolerance, protected shot content, keep strings, and RAY_SLIDES. The full 39-check vignette suite passes.

| Window | Score gate zero → phase two → final | Holes gate zero → phase two → final |
|---|---:|---:|
| screen02 | 98.416037% → 98.416037% → 98.416037% | 0 → 0 → 0 |
| screen09 | 94.841753% → 94.841753% → 94.841753% | 148 → 148 → 148 |
| screen17 | 93.686111% → 93.723593% → 93.723593% | 59 → 59 → 59 |
| screen18 | 98.579816% → 98.579816% → 98.579816% | 55 → 55 → 55 |
| screen19 | 97.086749% → 97.086749% → 97.086749% | 0 → 0 → 0 |
| screen20 | 97.703459% → 97.703459% → 97.703459% | 0 → 0 → 0 |
| screen21 | 93.526042% → 93.526042% → 93.939236% | 540 → 540 → 0 |
| screen22 | 97.258287% → 97.258287% → 97.258287% | 0 → 0 → 0 |

## Audits and record budget

Phase two was committed first as `9383dcc`, then measured with its immutable artifact snapshot. Its exposed background produces three frame-black ratchet failures pending the phase three skirt; those bounds were kept at their gate-zero values. Phase three subsequently passes every permanent bound. Fresh phase-specific engine snapshots preserve the exact artifacts used for each capture.

| Measure | Gate zero | Phase two | Final |
|---|---:|---:|
| Raw records |20,571|19,260|21,864|
| Expanded records |37,566|36,255|48,204|
| Exact reached cells |398,699|398,699|398,699|
| Specified black |31|31|0|
| Prop black |42|42|42|
| Low-visibility quest cells |841|336|336|
|128-unit frame black mean |2.095358%|2.662764%|0.051376%|
|128-unit frame black p95 |16.411719%|20.003516%|0.232031%|
|128-unit frame black maximum |51.191406%|60.371094%|2.736328%|

The final 128-unit census samples 24, 192 cameras: 415 below half visibility and 167 hidden, with median minimum visibility 100%. The default 256-unit permanent ratchet reports 1.647139% below half, 0.832060% hidden, mean frame black 0.044086%, p95 0.208398%, and maximum 1.868359%. The 336 low-visibility leg cells remain a strict exit failure despite the passing ratchet. Total black floor probes are 42, all prop cases.

Raw records remain 1, 136 below the 23, 000 phase exit ceiling and 3, 136 below the 25, 000 map cap. Expanded items exceed the 32, 500 diagnostic cap by 15, 704; this is the expanded-count warning required by §4.4, while raw records meet the budget. Skirt depth and new joins explain the expansion. Only the count pins rise; all other changed permanent pins decrease.

Independent final verification found zero lost and zero gained arrival cells. All 54 lava tuples, 68 pin rows, monster eggs, teleports, quest triggers, and the route remain protected by the estate. Source changes are limited to the three owned map modules and Map 10 visual pins, with required regenerated map pins and artifact manifest. Other maps retain their artifact records.

Audits: [baseline](m10/before-audit/), [phase two](m10/phase2-canonical-audit/), [final](m10/after-audit/), and [permanent ratchet](m10/after-test/map10-metrics.json). Commands use `python3 -B agents/map-populator/src/void_audit.py 10 --step 128 --workers 4 --out <directory>` and the corresponding `avatar_visibility.py` command. The final ratchet is test_visual_quality.py 10. Full route-band data: [phase two](m10/phase2-legs.json), [final](m10/after-legs.json).

## Remaining quest-band visibility

The 336 remaining cells are deduplicated across 9,295 unique quest-band cells. Bands overlap, so their row counts sum differently. The retained relief and screenshot terrain remains the principal unresolved geometry; the table preserves every band result for merge-level follow-up.

| Leg | Cells | Below half | Minimum visible |
|---|---:|---:|---:|
| vale-1 | 955 | 7 | 16.709% |
| vale-2 | 1190 | 30 | 11.055% |
| vale-3 | 1295 | 36 | 11.055% |
| vale-4 | 352 | 76 | 0.000% |
| vale-5 | 789 | 16 | 13.073% |
| vale-6 | 868 | 0 | 89.892% |
| vale-7 | 794 | 55 | 0.000% |
| vale-8 | 863 | 55 | 0.000% |
| vale-9 | 905 | 79 | 0.000% |
| vale-10 | 1103 | 53 | 0.000% |
| vale-11 | 2303 | 15 | 13.819% |
| house-1 | 96 | 27 | 11.321% |
| house-2 | 69 | 0 | 70.775% |
| house-3 | 193 | 1 | 45.703% |

## Validation and review

- `tools/build_artifacts.sh --record`: passed. Placement validation reports zero warnings and errors. The documented EALOGO and TJORVI compilation failures remain; the inherited Map 39 warnings remain. [Build log](m10/build.log.gz).
- `tools/run_all_tests.sh`: 56 of 57 files passed. The sole failure is the allowed test_integration_state.py install mismatch through the main-data symlink. The private harness game matches all six canonical locations; three engine-tree checks skip because this worktree has no engine checkout. No main install was rewritten. [Estate log](m10/tests.log.gz), [individual relevant checks](m10/test-logs/).
- Exact routes: 166 checks pass. Map edges pass, paint cycles pass 76 checks, art props pass 504 checks, and screenshot windows pass 39 checks.
- Independent verifier: final hash confirmed, exact flood equality, all eight windows pass, bank collision footprints identical, and post changes retain physical dimensions. No actionable material bug found.
- `codex exec review --base main`: first attempt could not create the bubblewrap loopback namespace. The danger-full-access retry found no actionable regressions: all 166 routes, all 39 vignette checks, and Map 10 boundaries pass; generated records match the artifact. The reviewer stopped its broader paint-cycle run before completion; the separate full estate covers it. [Review log](m10/review.log.gz).

## Engine evidence

All three states contain 56 successful fresh-world captures, 168 total, with landed true and exact requested coordinates, including z. Final captures use the frozen canonical artifact. Every image is 640×400. Final manifest checks pass, with complete phase-two and final log coverage and 49 matching baseline logs. Every stop uses a fresh world, 640×400 game surface, and usehighres=false.

All ScummVM launches use official tour_capture.py with `LV_DISPLAY=:64`, XDG_RUNTIME_DIR=/tmp/claude-1000/vq2-m10, a private config, and the existing console binary. A private xdotool wrapper adds 120ms between debugger chord events to resolve dropped keyboard delivery; official capture scripts remain unchanged. Failed attempts were retried in fresh sessions. Baseline log collection began during its batch, so its log coverage is partial. Phase two and final logs are retained per stop. Frozen runner trees live under the private runtime directory. The superseded pre-Hrodny final batch was moved outside repository evidence and replaced in full.

## Artifact SHA-256 hashes

| Artifact | Final SHA-256 |
|---|---|
| TYPEFLAG.DAT | `ac0b33486fc167d98c07c32011de348c11ae0cefb8d89fc2597ef984133a5fd1` |
| U8SHAPES.FLX | `aad6ed7b8961f416b6fae225d467427899a4487db768b6fb486ed5b5cb3e73ba` |
| ANIM.DAT | `97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443` |
| EUSECODE.FLX | `b47c324cdad77646c27755acfdd5bca53a9d92e16268db229f18e7dd780d4205` |
| FIXED.DAT | `87db9f776b5376b062d8f014c700ce2d15e0ac8de9e1d869bc3e9fea73d2c0fb` |

Phase two FIXED: `19b07efbaaeb2be1f77588cf9721dad7cbf4ff00b240ff80e54dc57408782019`. Gate-zero FIXED: `89da4e165833bff0b4da526cfa2cbc434336f6816e3964ae9982bd804a2eb767`. The four other artifact hashes remain identical across phases.

## Scope and remaining work

VQ-027 relief reconstruction, residual cliff/lava paint seams, and physical lake corner shaping remain incomplete for the reasons above. No shared generator, test, quest-leg definition, custom art ID, pinned item, or protected retail content was changed. Astra regrading remains with the merge-level review. No TODO file was edited because it falls outside the owned files. Main advanced through other slices during this run and retains its other local changes; its current FIXED hash differs from this slice. No main file was written by this slice. Nothing was merged or pushed.

Phase three implementation commit: `49c0e2f`. [Capture provenance](m10/capture-provenance.json) records frozen artifact hashes and confirms official capture scripts match byte for byte.

Post-completion `test_visual_quality.py 10` reports zero failures in 70.644s. The separate `--strict` run reports one failure: 336 quest-band cells below half visibility. [Ratchet log](m10/postcommit-ratchet.log.gz), [strict log](m10/strict-test.log.gz). The final review found no actionable regressions. The final estate remains 56/57, with the allowed integration-state failure.

Captured logs are scanned for paint cycles, invalid shapes, and missing art; none occur in the retained logs. All five warning types also occur in the baseline: headless ALSA audio, unavailable translations, GUI icons, fallback theme, and `Non-existent process PID (0) in implies.`. [Evidence checks](m10/evidence-checks.json) records exact capture positions, image dimensions, config, per-state log coverage, warning counts, and scan results.

[Final capture log](m10/capture-final.log.gz), [manifest and log checks](m10/evidence-checks.json), and [session status](m10/session-status.txt) complete the engine evidence. The private display is stopped. Required game-data symlinks remain unstaged; directory-only ignore patterns expose their names in worktree status. The build directory is a private copy.

Raw logs are stored as gzip archives; decompression preserves their complete output.

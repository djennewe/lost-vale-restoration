# Phase 4 shared slice 0.1

The shared APIs, 12 appended prefabs, and seven decorative shape rows are
implemented on `wt/vq4-s01`, based on main `01710d14`. The orchestrator
subsequently updated Map 8's return slab and FIXED hash. This revision changes
the four forest payloads and the shared archive import; visual pins remain unchanged.

The orchestrator's commits `1babc5a4` (free filler-donor slot) and
`732900e1` (Map 8 frame-nine slab and FIXED hash) are preserved. The
verification below records the subsequent forest and archive-import revision.

## Request 1: forest prefabs

Four `grass_wood_0` through `grass_wood_3` rows occupy **3216 through
3219**, after every first-wave packed slot through 3215. Each retains
sixteen grass tiles and now contains three different tree or deadwood
silhouettes, two bushes (434), a fern (414), roots (57), and two mushroom
groups (65). All prop bases are z zero. Mushrooms stand beside the trunk
bases, toward the foreground, clear of every solid collision box.

| Slot | Composition | Tree and stump anchors (local x, y) |
|---|---|---|
| 3216 | Large oak shoulder, smaller leafy tree, grey stump | (287,319), (511,223), (95,447) |
| 3217 | Smaller leafy tree, white dead tree, stump round an open glade | (223,255), (511,479), (127,479) |
| 3218 | Large oak against the east edge, brown dead tree, stump | (511,383), (223,223), (383,479) |
| 3219 | Smaller leafy tree, broad grey dead tree, stump | (383,255), (255,511), (95,159) |

Retail shape 199 supplies the oak, shape 75 frame four the smaller leafy
tree, shape 75 frames zero, one, and three the dead trees, and shape 152
the stumps. All 12 trunk anchors are distinct and use the 32-unit lattice
with the GLOB format's odd-coordinate offset. The unequal silhouettes,
edge-reaching groups, and glade break the repeated orchard rows.

The request explicitly sanctions rewriting these four unmerged payloads.
Only their four `globs.grass_wood_N.sha256` manifest fields changed; their
IDs and every other payload pin remain unchanged. `test_dressing.py`
checks hashes through the manifest, so it has no separate fixed hash table
to update. New composition checks cover distinct trunk anchors, mixed
silhouettes, ground-level bases, undergrowth, and mushrooms near trunk feet.
Existing internal solid-overlap, solid-top-face, standing-level, external
collision, and whole-chunk leg-band checks remain in force.

```python
family = lv_dressing.prefab_family('grass_wood_')
site.swap_chunks(plain=1, family=family, share=.5,
                 where=(12900, 20479, 22900, 22400))
```

The synthetic clear-grass check accepts 32 substitutions, eight of each
member. Its negative controls refuse a complete quest band and an external
oak collision. The existing `GRASS_FOREST` retail family remains unchanged:
Map 39 already calls it, and changing its meaning would alter FIXED.DAT.
Its owner can adopt the new family in the next builder slice.

Map and visual pin fields changed for this request: none. The four
sanctioned prefab payload pins are listed above. The GLOB hash is below.

The supplied `shared-flex-import.patch` is applied exactly to `lv_globs.py`.
It selects the sibling writer as `_lv_globs_flex`. A fresh-process negative
control preloads the compiler's reader, confirms it has no `write`, imports
`lv_globs`, and requires its writer's `write` method. The Map 18
fresh-interpreter workaround remains unchanged.

## Request 2: clipped moat banks

Eight paint-only prefabs append after the forest rows:

| Slots | Names | Retained terrain |
|---|---|---|
| 3220 through 3223 | `moat_west_0` through `moat_west_3` | Grass-side column ending at x 13567 |
| 3224 through 3227 | `moat_east_0` through `moat_east_3` | Grass-side column beginning after x 14079 |

The prefabs contain decorative grass caps at z 40 and rooted earth faces at
z eight. Their sprite tops meet grass at z 48. Shapes 903 and 904 have
neither LAND nor SOLID. The rows emit no water or supporting grass.
`moat_bank` requires existing shape-three grass at z 48 before accepting a
piece and retains every input record, including channel water at z zero.
All emitted boxes remain outside x 13568 through 14079. Every accepted
piece passes the shared placement exclusions.

```python
site.moat_bank('west', where=CHANNEL_BANK_BOX)
site.moat_bank('east', where=CHANNEL_BANK_BOX)
```

Negative controls cover absent grass, grass at the wrong level, hatch-box
exclusion, and a different map. Independent checks preserve water at z zero
and all original records. Adoption and the exact bank extent belong to the
Map 39 builder owner. Pin fields changed: none.

## Request 3: VQ-091 marker frame

`test_route_reach.py:668` now expects shape 71, frame nine at
(20639,3967,0), with the existing heading and door state. This is the only
field changed in that file.

The orchestrator paired the assertion with `build_map_08.py`'s frame-nine
return slab in commit `732900e1`, including the recorded FIXED hash. That
commit is preserved; this revision makes no builder changes.

## Request 4: props within occupied chunks

`place_prefab` expands one prefab, omits its ground and void tiles, and
validates each remaining prop independently. It accepts safe props beside
existing contents, preserves all original records, requires existing floor
support at the prop's base, and indexes each acceptance before checking the
next prop. Its ledger records accepted counts and rejection reasons.

```python
added = site.place_prefab(877, x=chunk_x, y=chunk_y, z=0, where=HALL)
```

The floor and unrelated prop remain byte-identical in the positive control.
Negative controls cover a map-pin mask, a decoded 0xff hatch box, quest
bands, missing support, an empty prefab, and retail bones' reachable top.
Existing `reason` and `_new_top` checks remain in force. Rejected props can
leave a partial group, which the returned list and ledger expose for the
builder's composition decisions. No new prefab or pin field is needed.

## Request 5: unmeasurable stride baselines

`stride_share` now returns `None` when no shape has six small-prop instances.
`limits` consequently leaves that field unpinned. Six repeated instances
produce a measurable value and remain subject to targets and ratchets.

```python
# One-time migration of existing zero stride pins only:
# python3 agents/map-populator/src/test_dressing.py --record-stride
```

The migration removed only **17** `props.stride_share: ["max", 0.0]` fields,
all under the named region's `pins` dictionary:

| Map | Regions |
|---|---|
| 9 | guardian chamber, passage |
| 10 | entry, north plain, west clearing, lake, cloud approach, moriens ruins, passage test |
| 11 | earth, air, fire, four pillars, pad room |
| 13 | valley, summit |
| 18 | sanctum |

Map 8's current stride pins are measurable and remain unchanged. All whole,
budget, other metric, allowance, target-failure, provenance, and visual-pin
fields remain unchanged. A JSON comparison against main verified that these
17 deletions comprise the entire pin diff. Tests cover empty and five-item
samples, six-item measurement, omitted pins, and a measured regression.

## Request 6: decorative art rows

| Shape | Export | Retail sprite | TYPEFLAG donor | Footpad |
|---|---|---|---|---|
| 898 | `SHAPE_COURT_COBBLE_FLAT` | 70, all 23 frames | 71 | (4,4,0) |
| 899 | `SHAPE_RUBBLE_DECORATIVE` | 524, six frames | 465 | (3,3,1) |
| 900 | `SHAPE_BONES_DECORATIVE_A` | 235, two frames | 465 | (3,4,1) |
| 901 | `SHAPE_BONES_DECORATIVE_B` | 237, two frames | 465 | (4,3,1) |
| 902 | `SHAPE_CAVE_CREST_DECORATIVE` | 125, 23 frames with seven crops each | 202 | (4,4,0) |
| 903 | `SHAPE_MOAT_BANK_DECORATIVE` | 94, 11 frames | 465 | (4,4,1) |
| 904 | `SHAPE_MOAT_FACE_DECORATIVE` | 85, seven frames | 465 | (1,4,4) |

R1 copies 70's cobbles onto 71's exact zero-height row. R3 copies rubble and
bones onto FIXED rows with LAND and SOLID clear, retaining their original
footpads and sprite heights. `KIT_HALL` exposes 899, and `KIT_BONES` exposes
900 and 901. The last two allocations support request two. All seven are
static copy rows without classes or animation entries.

```python
site.set_piece('court paving', court_records_using_SHAPE_COURT_COBBLE_FLAT)
site.clusters(kit=lv_dressing.KIT_HALL, per100=4, where=HALL,
              floors={301}, anchor='wall')
site.clusters(kit=lv_dressing.KIT_BONES, per100=4, where=SANCTUM,
              floors={301}, anchor='wall')
site.cave_crest('continuous cave back', authored_crest_records)
```

R4's crest input uses shape 902 with retail frame numbers zero through 22.
Each anchor tries the full sprite, upper eight, 16, 24, or 32 pixel strips,
and left and right halves. The largest safe crop is selected. Output frames
are `retail_frame * 7 + crop_index`. All variants retain the retail canvas
and anchor, and clipping only removes pixels.

Shot checks examine the remaining opaque pixels with the existing 16-pixel
margin. The route check protects every walking and standing pose, including
flips and headings, at every quest-band cell. Existing covered pixels may
remain covered; additional covered pixels refuse the cap. If every crop is
unsafe, the named piece fails atomically. Direct placement of shape 902
also invokes this route check.

A negative control catches a walking-pose obstruction that frame zero misses.
Other controls reject fully covered shot windows and new Tiny Tar occlusion,
and permit existing covered pixels. Contained inventory records cannot supply
existing cover. Ambiguous paint order receives conservative pixel protection.
The generic art checks cover every new
copy and TYPEFLAG donor. `.claude/rules/shape-ids.md` and `docs/art-track.md`
record the allocations; D8's conditional cloud-rim lobes take **905**.

R2's raised 37 dais remains excluded. The no-new-standing-top rule is
unchanged. Map 13's later requests remain follow-up work under request seven;
its two stride-field deletions above are the authorized shared migration.

## Artifact identities and images

`tools/build_artifacts.sh --record` completed against the isolated data and
private six-artifact build directory. Compilation succeeded for 55 of 57
sources, with EALOGO and TJORVI remaining the documented allowlist pair.

| Artifact | SHA-256 |
|---|---|
| GLOB.FLX | `f96fc65fb8456b0b3ca766791feea5f27c6b06f4163a388aa6136bf1d53f1671` |
| FIXED.DAT | `c04a3f905bcf2fc44db500db55423a88d551e23ae1077c4364fef1906b23b7cd` |
| U8SHAPES.FLX | `074e00be59d1a361fc9876c7daae2f56b6981d3a8c63c44b0ec228334a6d88c3` |
| TYPEFLAG.DAT | `8839ab2f5e6fbe5fe5d303938760a99a819204d96c4318b35269b39f52171ef0` |
| ANIM.DAT | `97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443` |
| EUSECODE.FLX | `b47c324cdad77646c27755acfdd5bca53a9d92e16268db229f18e7dd780d4205` |

GLOB.FLX contains 3,228 slots. Its first 3,216 payloads, comprising all retail
slots and all pre-existing LV slots, match main byte for byte. Every existing
manifest glob pin remains unchanged. Shape and TYPEFLAG comparisons differ
only at 898 through 904. ANIM and EUSECODE retain their original hashes. FIXED retains the
orchestrator's frame-nine slab hash.
[Original identity evidence](p4-s01/identities.json) includes the initial
pin paths. [Revision identity evidence](p4-s01/revision-identities.json)
confirms that only the four sanctioned prefab payload pins changed from
`732900e1`; the other five artifacts retain that commit's hashes. Every
payload below slot 3216 also matches main's archive byte for byte.

The contact sheets use `phase4/mock.py`'s `Stage.glob_sheet`, with its glob
reader pointed explicitly at the private built GLOB.FLX. I inspected all
12 new prefabs at full image size. The revised forest contact sheet and shuffled four-by-three tiling were
opened and inspected. They show uneven canopies, deadwood, clear ground,
and mushrooms at trunk feet; the tiling has no repeated orchard grid. The banks read as rooted earth beneath
grass. A channel context render confirms the preserved water opening.

These local images contain Origin art and are **uncommitted**:

- `p4-s01/forest-prefabs.png`, slots 3216 through 3219, two-by-two contact sheet.
- `p4-s01/forest-tiled.png`, shuffled four-by-three tiling at 640x400.
- `p4-s01/moat-prefabs.png`, slots 3220 through 3227.
- `p4-s01/moat-context.png`, retained grass and water with both bank sides.
- `p4-s01/crest-variants.png`, three source frames with all seven crops.
- `p4-s01/bank-frames.png` and `p4-s01/bank-donors.png`, donor studies.

The donor studies rejected rocky water sprites for the moat. The committed
rows use grass caps and rooted earth from the retained bank vocabulary.
All final sheets and both additional final renders were opened and inspected.

## Verification and limits

`tools/build_artifacts.sh --record` completed successfully, preserving all
five non-GLOB hashes from `732900e1`. `git diff --check` passed. The
compiler-first import probe passed, and reverse application of the supplied
patch passed `git apply --reverse --check`, confirming the exact import fix.

`codex exec review --base main` could not inspect the diff because
bubblewrap failed with `Failed RTM_NEWADDR: Operation not permitted`.
The retry, `codex -c 'sandbox_mode="danger-full-access"' exec review --base main`,
reported no actionable regressions. Its dressing, art, and map-pin checks
passed. Its separate estate run stopped during paint-cycle checks; the
required complete estate result is recorded separately below.

Evidence: [recorded build](p4-s01/revision-build.log.gz),
[initial sandbox failure](p4-s01/revision-review-sandbox.log.gz),
[completed review](p4-s01/revision-review.log.gz), and
[artifact and pin boundaries](p4-s01/revision-identities.json).

`tools/run_all_tests.sh` completed: **57 of 58 test files pass**. The sole
failure is the permitted `test_integration_state.py` shared-install mismatch:
installed U8SHAPES, TYPEFLAG, FIXED, and GLOB differ from the private build.
Installation remains untouched. The dressing run reports zero failures and
104 existing target debts. Art checks pass all 777 assertions; paint cycles
pass 76, route reach passes 166, the filler-donor test passes 42, and map-pin
freshness passes three. [Complete estate evidence](p4-s01/revision-estate.log.gz)
and [dressing evidence](p4-s01/revision-dressing.log.gz) retain the outputs.

Both final images were regenerated from the recorded GLOB and inspected.
The contact sheet is 640x480; the four-by-three tiling is 640x400, painted
at twice the output canvas size and reduced with the mock's box filter.
Its rows use slots (3218,3216,3219,3217), (3217,3219,3216,3218), and
(3219,3218,3217,3216). Canopies, deadwood, and ground gaps join irregularly
across chunk edges. No map builder adopts the redesigned slots in this
revision.

The earlier shared-slice review found crest occlusion defects involving
contained inventory, ambiguous painter ordering, and walking poses beyond
frame zero. Those fixes and their negative controls remain in this branch.
The earlier evidence remains available in `p4-s01/verifier.md` and the
original compressed logs.

The existing worktree, private six-artifact build directory, and shared-data
symlinks were retained. The orchestrator's separate commits `1babc5a4` and
`732900e1` were already present at entry. No Map 18 builder change,
installation, ScummVM launch, merge, push, or main checkout write occurred.
The two forest PNGs remain uncommitted because they contain Origin art.

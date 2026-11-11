# Visual-quality backlog

The tour’s 798 issues become 198 root-cause items covering 788 map-content reports, with 10 excluded observations. The 111 high reports collapse to 39 high items. All 370 stops remain indexed in [backlog.json](backlog.json).

Each item preserves the original issue text, stop, and zero-based `issue_index`. Compound reports belong to their primary cause; `related_items` connects overlapping work. Severity remains the highest original severity, including suspected false positives.

## Items by phase and severity

| Phase | High | Medium | Low | Total |
|---|---:|---:|---:|---:|
| 1: Specific defects and route floor | 14 | 2 | 1 | 17 |
| 2: Avatar visibility | 7 | 9 | 0 | 16 |
| 3: Void, edges, holes, filler, and water | 12 | 16 | 4 | 32 |
| 4: Dressing and transitions | 6 | 66 | 61 | 133 |
| Total | 39 | 93 | 66 | 198 |

## Top 15 by severity and reach

Reach counts distinct reporting stops. Ties use source-issue count, then item ID. Every entry below is high severity; ranking spans all phases.

| Item | Map | Phase | Stops | Issues | Cause |
|---|---:|---:|---:|---:|---|
| VQ-066 | 10 | 4 | 56 | 56 | Vale ground between set pieces lacks regional dressing |
| VQ-034 | 10 | 3 | 29 | 29 | Vale boundary and canyon rims lack a visible backdrop |
| VQ-035 | 11 | 3 | 18 | 18 | Dungeon outer rims expose black exterior filler |
| VQ-036 | 10 | 3 | 16 | 16 | Modular Vale cliff joins expose vertical black slits |
| VQ-001 | 9 | 1 | 11 | 11 | Black reconstruction tiles cover the guardian-dais floor |
| VQ-037 | 13 | 3 | 11 | 11 | Lake and skull-ring terraces contain black tops and slabs |
| VQ-067 | 10 | 4 | 10 | 11 | Grass patches on raised cliff tiles read as green cubes |
| VQ-038 | 11 | 3 | 9 | 9 | Black filler remains between dungeon sections and corridors |
| VQ-039 | 13 | 3 | 8 | 9 | Valley south and east edges end as a slab over black |
| VQ-040 | 39 | 3 | 8 | 8 | Tenebrae lane treeline has black filler beyond it |
| VQ-068 | 11 | 4 | 8 | 8 | Water section and lizard bay lack habitat dressing |
| VQ-069 | 11 | 4 | 7 | 8 | Air section lacks an elemental identity and dressing |
| VQ-018 | 8 | 2 | 7 | 7 | Retail northern cave roofs hide route and wing positions |
| VQ-002 | 18 | 1 | 6 | 6 | Rock island between sanctum passages draws as a black pit |
| VQ-041 | 10 | 3 | 6 | 6 | Lake body and repeated blue edge sprites read as black stripes |

## Retail and screenshot protection

`MapArchive`, `exact_reach.expand_globs`, and `GlobReader` compared both requested FIXED archives at issue locations. Per-item evidence includes matching, added, and removed records. The retail template additionally confirms bone-shelf carryables and the potion.

`retail_class` has three values: `lv` (173 items), `retail-exposed-by-lv` (five), and `retail` (20). The five LV-exposed items are VQ-003, VQ-004, VQ-008, VQ-040, and VQ-090. VQ-004, VQ-040, and VQ-090 now default to fixes; 15 items retain `decision_required`. VQ-090 has per-source classes because its four witnesses span both retail and LV-exposed locations. Its retail witnesses retain their decision scope.

Map 8’s 1,714 black 564:2 plates match pristine retail. LV cuts expose the black at m08-09, m08-12, m08-14, and m08-49. The trigger-200 pocket at (20415,2783,0) also inherits black floor; `metadata.retail_exposure_regions` records it, and the adjacent m08-48 niche carries the exposure tag with zero source issues. Map 39’s tunnel, oak barrier, and 274 black plates are LV changes. The inherited boundary beyond its lane treeline is `retail-exposed-by-lv`; its main-gate canal rectangle remains `retail`.

All 19 vignette regions and origins were checked with builder art mappings and slides. The 115 shot-bound items have `shot_window` lists and `shot_floor` mappings, with scalar pairs in each `shot_evidence` entry. Scores copy `test_vignettes.FLOORS[screenNN][0]`; the test applies 0.25 points of slack separately. `touches_shot` flags overlap and proximity within 512 world units. Camera envelopes are labelled as approximate; sprite overlap requires a fix-specific render check.

VQ-037 protects the screen14 `SHOT_CUTS` pieces seen around m13-23 through m13-27. `build_map_13.py:147` cuts one 564:3 plate into two 35:10 tiles at (4367,4323,137) and (4239,4323,137); each occurs once in expanded built FIXED. The screen14 floor is 89.86. The other two `SHOT_CUTS` entries emit no pieces. Attribution covers the surviving quarters; other reported holes and vertical faces require individual identification and a vignette check before changes.

## False positives and accepted content

- VQ-062 (`m09-12:0, m09-19:1, m09-27:1`): The reviews explicitly call this expected exterior beyond clean walls.
- VQ-169 (`m08-30:1`): A moving figure behind a retail counter can produce correct foreground occlusion; replay is pending.
- VQ-171 (`m08-43:1`): The potion rests on drawn ground and exists in the retail new-game template.
- VQ-173 (`m09-15:1`): The issue text describes a clean, legible body scene and supplies no defect.
- VQ-175 (`m10b-08:0`): A teleported pose inside the well sprite needs a natural approach replay.
- VQ-189 (`m13-40:0`): The review explicitly calls the mushroom overlap correct occlusion.
- VQ-190 (`m13-31:2`): The bone cluster belongs to the prescribed screen01 composition.
- VQ-192 (`m13-15:1`): The icicle-like stepping stones belong to the prescribed screen15 composition.

VQ-054 preserves four north-edge reports as the boundary Douglas accepted on 25 October 2026. These are visible void observations with an accepted disposition. Water-section art and retail terrain changes retain their decision status.

## Excluded observations

- Following or roaming actors: `m08-45:2`, `m09-07:1`, `m09-18:1`, `m11-01:2`, `m11-07:3`, `m11-30:3`, `m11-36:2`, `m11-48:2`, and `m13-10:2`. Follower identity remains unverified.
- Water capture: `m08-03:2` describes the harness placing the Avatar on water after a dry-flood standability result.
- Mouse cursor: visible in captures; zero original issue records concern it.

## Verification

`python3 -B /tmp/lv-vq-backlog/validate_backlog.py docs/research/2026-11-01-visual-pass` passes with schema-two checks: all 798 issues occur exactly once; severities, map overrides, IDs, owners, counts, bounds, hashes, 19 shot regions, retail classes, all shot scores, trigger-200 coordinates, and both screen14 cut records agree.

The single-stop capture test recorded m13-26 at (15967,19711,0), Map zero, with `landed: false`; VQ-012 now requires a landed capture before a geometry diagnosis. [Retail calibration](retail-calibration.md) records the offline audits. The full route replay and Astra grading remain pending.

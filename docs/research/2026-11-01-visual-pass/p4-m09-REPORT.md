# Phase four Map 09: review corrections

The visual corrections are implemented; strict acceptance remains unmet because the compact earth patch, restored fungus, and exposed darkness conflict with the previous pins. This report supersedes the acceptance claims recorded at `5706abf`. No pin was weakened to conceal those conflicts.

Branch: `wt/vq4-m09`. Worktree: `~/projects/lv-wt-vq4-m09`. Revision date: 9 November 2026 (America/Chicago). No merge or push occurred.

## Hall

**Reads as:** the cave where Galjeron lies.

The earth patch now occupies a four-cell-wide footprint with clipped corners: four earth interiors from the 437 palette and eight 386 transitions from the 455 palette. The twelve cells surround the body, journal, pack, and sword. The other hall cells retain cave rock, with the existing small 300 scrape at the lair. The former broad earth polygon is removed. VQ-142’s body-side spire stays removed, along with the six 186 and three 796 stand-ins from the original slice.

All five inherited mushrooms are restored at their original coordinates and frames, including the orange cap at (13280,14832), the large western growth at (12960,14016), and the cave-passage mushroom at (14024,15560). The five authored seep fungi now use visible cap frames 4, 5, 8, and 10. Seven additional pebble and stone records connect those caps to the wall-foot groups. One cap moves laterally to break the projected straight run.

**Set piece:** Fungus at the seep, 34 explicit-coordinate records protected by `Site.set_piece`. Capture: [hall-seep](p4-m09/setpieces/hall-seep.png). The inherited mushrooms remain inherited map records, outside the authored composition.

**Fungus substitution edge:** the original safe 60% `ROCK_FUNGUS` substitution probe accepted zero chunks. Whole-chunk eligibility and the complete-family requirement prevent substitution in this compact, pinned hall. The existing [probe](p4-m09/swap-probe.json) records that limitation. This revision supplies visible fungus through restored records and validated explicit placements. A true 60% egg substitution remains undone; it requires a shared placement API that can validate individual prefab props in partly occupied chunks while preserving pins, hatch boxes, quest bands, and standing-level checks. No shared module was edited.

## Passage

**Reads as:** cave turning to masonry.

The flagstone begins at different depths across the eight floor columns, from y 16127 to y 16511. Six gravel fragments and rubble on both sides interrupt the join at y 16128. The threshold composition grows from five to eleven explicit-coordinate records. The inherited cave mushroom returns north of the join.

The full-height brick enclosure is removed from view. Invisible 497 and 498 replacements retain its collision footprint; their 48-unit boxes cover the former 40-unit courses. Existing invisible barriers retain their serialized records. Short western and southern masonry remnants and the two original columns identify the worked exit. The existing central lower southern panel receives the carved relief frame. Darkness surrounds the passage; no new drawn perimeter wall is introduced.

**Set piece:** Masons abandoned threshold. Capture: [masons-threshold](p4-m09/setpieces/masons-threshold.png). VQ-140 is the threshold correction. The columns and relief retain the VQ-151 exit marker.

## Guardian chamber

**Reads as:** the tomb. The guardian composition and protected screenshot geometry retain their prior records. **Set piece:** Broken funerary vessels, eight records. Capture: [tomb-vessels](p4-m09/setpieces/tomb-vessels.png). VQ-051 retains the five convex shell fills; VQ-001 retains the protected dais silhouette.

## Measurements and surviving failures

The following comparison uses the reviewed `5706abf` result as its before state. The original phase-four target-failure counts were guardian zero, hall two, and passage one. Current regional targets are guardian zero, hall one, and passage zero.

| Region | Props per 100 cells | Grouped share | Rock or largest material share | Seam share | Raw records | Target failures |
|---|---:|---:|---:|---:|---:|---:|
| guardian chamber | 7.44 → 7.44 | 75.00% → 75.00% | 53.95% → 53.95% | 11.94% → 11.94% | 604 → 604 | 0 → 0 |
| hall | 8.98 → 13.28 | 56.25% → 92.59% | 43.36% → 91.80% | 22.29% → 6.88% | 383 → 394 | 0 → 1 |
| passage | 7.29 → 12.50 | unmeasured → 54.55% | 47.92% → 45.83% | 14.53% → 23.26% | 165 → 172 | 0 → 0 |

Whole-map raw and expanded counts are 1,596, against the 1,800 phase ceiling and 2,500 hard cap. Expanded records per ground cell are 2.815, below 2.9. Record bounds rise within those budgets. Improved dressing bounds and visibility bounds are tightened. Full measurements and pin changes: [revision-dressing-metrics.json](p4-m09/revision-dressing-metrics.json).

`test_dressing.py 9 --strict` reports 13 failures, comprising one regional target and twelve pin failures. Every surviving category is listed below; whole-map and budget-area failures are separately printed in [revision-dressing.log](p4-m09/revision-dressing.log).

| Failure | Current | Existing bound | Reason retained |
|---|---:|---:|---|
| Hall top material target | 91.80% | maximum 65% | The requested four-cell earth patch leaves the rest of the hall cave rock. |
| Hall top material and largest patch pins | 91.80% | maximum 43.36% | Those bounds were established with the rejected earth sheet. |
| Hall seam pin | 6.88% | minimum 22.29% | The small patch has fewer material boundaries than the rejected sheet. |
| Hall stride pin | 43.75% | maximum 0% | Restored mushrooms and added pebbles cross the metric’s six-instance threshold; the cave target is maximum 65%. |
| Whole and budget top material pins | 64.90% | maximum 40.92% | Cave rock returns across the hall. The whole-map target of maximum 65% passes. |
| Whole and budget largest patch pins | 64.37% | maximum 40.56% | The continuous hall rock floor is intentional. |
| Whole and budget seam pins | 11.64% | minimum 17.56% | The broad earth boundary is removed. |
| Whole and budget stride pins | 35.48% | maximum 0% | The restored fungus and mixed wall-foot groups have a measurable nearest-twin vector share. |

Ordinary visual quality retains three frame-black failures: mean 20.35% against 19.76%, p95 41.34% against 37.36%, and maximum 51.82% against 47.17%. These increases follow removal of the blue brick enclosure, exposing the specified darkness. Existing bounds remain. Quest-band cells below half visibility improve from 66 to 60; sampled below-half share improves from 8% to 5.33%. Specified or unpainted walkable black remains zero, prop-black probes remain 19, and sampled completely hidden share remains zero. The 60-cell strict visibility debt is inherited. [Visual measurements](p4-m09/revision-visual/map09-metrics.json).

## Windows, provenance, and scope

Screen10 retains the 89.517253% class score and its 89.27% floor. The corrected and reviewed palette-index windows have zero changed pixels: [window comparison](p4-m09/revision-window.json). The body, journal, pack, sword, teleport and monster eggs, 178 pre-existing invisible barriers, dais, stair treads, and black fillers retain their serialized records. Only the generated FIXED hash prefix changes in `map_pins.json`. `void_cover(items)` remains last. The built-map comparison finds Map 09 as the sole changed map and zero lost protected records: [integrity comparison](p4-m09/revision-integrity.json).

FIXED.DAT SHA-256: `f64db239878f1530836fe2d338433c0466f97a6c3bcf63c059b351e7e59dbcf4`. The other five artifacts retain their reviewed hashes, including GLOB.FLX `aabc1ad36f42c6bdd01cfcb7271f0765983a9914489d62a96a9bcb5e1d7c88ca`. [Recorded build](p4-m09/revision-build.log).

`docs/map-feedback/OPEN.md` reads “Nothing open.” No feedback API action is required. No new shape, prefab, shared source change, or test change is included. The bone standing-level restriction from the original guardian work remains.

## Capture inspection

The initial correction captures exposed a projected run of caps; one authored cap was moved sideways and the groups gained connecting stones. The complete final tour contains 27 fresh-world captures, with three additional set-piece captures. All use the unchanged `tour_capture.py`, `LV_DISPLAY=:82`, `XDG_RUNTIME_DIR=/tmp/claude-1000/vq4-m09`, and `usehighres=false`.

I inspected all 27 final after-images and all three final set-piece images individually at 640 by 400. The hall reads as the cave where Galjeron lies: rock surrounds the compact body patch, and visible caps gather at the walls. The passage reads as cave turning to masonry: rubble interrupts the ragged paving edge, columns and short remnants mark the worked end, and darkness surrounds it. The guardian retains the tomb silhouette. The inherited near-wall occlusion and protected dais cutouts remain documented limits. The tomb and hall set-piece cameras were moved onto clear floor and retaken after a final overlap check; all three final set-piece cameras have zero solid overlaps. [Camera check](p4-m09/revision-camera-checks.json).

All 57 accepted images, including the unchanged 27 before-images, have `ok: true` and `landed: true`. The image audit validates every image against its built scene; its largest frame-black discrepancy is 0.423 percentage points. [Capture audit](p4-m09/capture-audit.json), [image hashes and inspection](p4-m09/capture-summary.json), and [runtime verification](p4-m09/revision-runtime-check.json) record the evidence. The private capture installation matches all six final artifacts.

## Estate and review

`tools/build_artifacts.sh --record` succeeds. `python3 agents/map-populator/src/test_dressing.py 9 --strict` completes with the thirteen failures described above. Ordinary visual quality has the three frame-black failures described above. No bounds or allowances were weakened to make these checks pass.

The final `tools/run_all_tests.sh` run finishes with 55 of 58 files passing. Failing files are `test_dressing.py`, `test_visual_quality.py`, and the allowed `test_integration_state.py`. Integration has ten passed assertions, one failed, and three skipped; its remaining failure is main’s shared installation `STATIC/FIXED.DAT`. The private harness matches all seven installed artifact copies. [Final estate](p4-m09/revision-estate.log).

All 39 vignette assertions, 76 paint-cycle checks, 166 route checks, 201 interaction-destination checks, 60 hygiene checks, and three pin-freshness checks pass. A preliminary estate overlapped artifact production and reported a Map 39 stale-frame failure. The targeted rerun and the complete final run both pass all 19 assertions for that file. The built-map comparison confirms that Map 39 retains its reviewed records.

Required `codex exec review --base main` was blocked by bubblewrap’s `Failed RTM_NEWADDR: Operation not permitted`. The unrestricted retry completed and identified two P2 findings: reconcile the dressing pins with the compact patch and restored fungus, and reconcile the frame-black pins with darkness beyond the broken masonry. Both remain open because the brief retains the existing ratchet contract. [Initial review](p4-m09/revision-review.log), [completed review](p4-m09/revision-review-unrestricted.log), and [review status](p4-m09/review-result.json).

Strict acceptance and the estate exit criterion remain unmet. The branch requires a decision on the named material, stride, and frame-black constraints before merge. The true 60% prefab substitution also remains the shared eligibility issue described above. No merge, push, main-checkout source edit, or shared-install write occurred.

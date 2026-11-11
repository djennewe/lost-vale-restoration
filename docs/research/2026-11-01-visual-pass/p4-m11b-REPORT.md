# Phase 4 Map 11 second run

## Merge-review corrections, 10 November 2026

The Hub has four framed elemental markers, including a textured blue basin, and Air has an eight-spire ring around a cleared pale stone floor. This section records the current merge-review correction and supersedes the earlier verification results below. The approved water-count correction from `842032f5` remains intact.

### Hub: elemental crossing

Each marker has the same 320-unit square kerb around a 256-unit inset. Twelve existing stone courses and corner pieces rise 8 units through `walkable_set_piece`. All four route proofs pass. The Water inset retains four shape-896 tiles over dry flagstone, with shape-347 textured water frames at the kerb. Earth retains its rubble, Air its spire, and Fire its basalt and embers. Three props move inward to clear their kerbs.

Current captures: [crossing](p4-m11b/revision/captures/m11-elemental-crossing.png), [north doors](p4-m11b/revision/captures/m11-elemental-crossing-north.png), and [Earth doorway](p4-m11b/revision/captures/m11-elemental-crossing-west.png).

### Air: wind-broken ring

Eight spires occupy an explicitly authored circle of radius 384 units. Three collapsed stone shoulders and their chip fan trail southeast. The centre has pale shape-71 stone surrounded by dark gravel and remains clear of props. The original scene reservation and the Air ledge faces remain. Narrow foreground spire frames retain the circle while clearing sampled Avatar poses. Six irregular chip positions preserve main's stride bound.

Current capture: [wind-broken ring](p4-m11b/revision/captures/m11-wind-broken-ring.png).

### Measurements and protected content

Every non-count dressing and visual bound is compared with main. Both comparisons report zero regressions. Record counts stay inside the 10,000 raw ceiling and 2.9 expanded records per land cell. Full measurements are in [dressing metrics](p4-m11b/revision/metrics.json) and [visual metrics](p4-m11b/revision/visual/map11-metrics.json).

| Measure | Previous second run | Correction |
|---|---:|---:|
| Whole-map raw records | 9731 | 9730 |
| Whole-map expanded records | 22821 | 22868 |
| Hub raw records | 410 | 412 |
| Hub expanded records | 964 | 1019 |
| Air raw records | 632 | 629 |
| Air expanded records | 2394 | 2386 |
| Air stride share | 0.216327 | 0.218487 |
| Whole-map expanded records per land cell | 1.901433 | 1.905349 |

Main's Air stride bound is 0.218750. Final low-visibility sampling finds 193 of 2,000 samples below half visibility, against main's 194 of 1,998. No quest-band sample falls below half visibility. Specified walkable black remains zero.

[Identity checks](p4-m11b/revision/identities.json) retain all 50 Map 11 pin rows, 986 anti-climb wall records, 276 original causeway pieces, 96 interior lava tiles, six lava pools, 10 flames, two seals, and 112 Water-section tiles. Every other map's raw records remain unchanged. The 3,875-slot main GLOB prefix and the complete 4,047-slot pre-correction prefix remain byte-identical. The accepted ritual crescent, urn pairs, reliefs, and transitions retain their builder definitions. The derived `map_pins.json` artifact hash is refreshed; every pin row retains its value.

| Region | Target failures from main to current | Set piece |
|---|---|---|
| Entry hall | 0 to 0 | Votive alcove |
| Hub | 3 to 0 | Elemental crossing |
| Earth | 0 to 0 | Golem root den |
| Air | 0 to 0 | Wind-broken ring |
| Fire | 0 to 0 | Charred offering |
| Water | 0 to 0 | Drowned portico |
| Four pillars | 1 to 1 | Broken ritual crescent |
| Pad room | 0 to 0 | Last ward |

Four Pillars retains its named `ground.top1` allowance at 0.887556. No allowance is added.

### Verification and inspection

- `tools/build_artifacts.sh --record`: successful, zero validation warnings or errors. All six recorded hashes verify. [Final build](p4-m11b/revision/build-visibility.log.gz).
- `test_dressing.py 11 --strict`: zero failures, with the retained Four Pillars allowance. [Strict log](p4-m11b/revision/dressing.log.gz).
- `tools/run_all_tests.sh`: 57 of 58 files pass. The sole failure is the permitted `test_integration_state` shared-install mismatch. All 1,017 art checks and 39 vignette checks pass. Screen05 remains 94.55 and screen07 remains 97.28. [Estate](p4-m11b/revision/estate.log.gz).
- `codex exec review --base main`: the default sandbox hits the known bubblewrap namespace failure. The unrestricted final retry completes with no actionable findings. Its additional estate attempt was incomplete; the separate full estate run above completed. The preliminary stale dressing bounds and map-pin hash findings are resolved by the measured pin refresh. [Final review](p4-m11b/revision/review.log.gz).
- `git diff --check`: clean. Main remains outside the write scope; no merge or push occurred.

All 11 final captures were personally inspected at 640 by 400. Every capture uses a fresh world, display `:85`, runtime `/tmp/claude-1000/vq4-m11b`, and `usehighres=false`, and records `landed: true`. The [capture inventory](p4-m11b/revision/captures/captures.json), [inspection notes](p4-m11b/revision/inspection.json), [validation](p4-m11b/revision/capture-validation.json), and [provenance](p4-m11b/revision/provenance.json) bind the captures to the final artifact snapshot. Settled Map 11 log tails contain zero paint-cycle or process warnings; the startup warnings are counted separately.

Retaken tour stops: [m11-02](p4-m11b/revision/captures/m11-02.png), [m11-20](p4-m11b/revision/captures/m11-20.png), [m11-32](p4-m11b/revision/captures/m11-32.png), [m11-37](p4-m11b/revision/captures/m11-37.png), [m11-42](p4-m11b/revision/captures/m11-42.png), [m11-27](p4-m11b/revision/captures/m11-27.png), and [m11-50](p4-m11b/revision/captures/m11-50.png).

Builder commits, before the evidence commit:

```text
0ef56bd9 Frame the Map 11 element markers and compose the wind ring
a5359f60 Break repeated spacing in the Map 11 wind debris
5a6aba00 Keep the wind ring foreground clear of sampled walking poses
```

## Earlier second-run record

Both rejected scenes are rebuilt, and the requested shared slice 0.2 paths are adopted on `wt/vq4-m11b`, from main `9a201022`. Main is the baseline for every ratchet comparison. Builder changes and evidence were committed throughout the run.

The required estate run completed with 56 of 58 files passing. The remaining failures are the permitted integration-state mismatch and a stale whole-map water-tile count. The count correction awaits the explicit test-ownership exception requested from Douglas. All owned builder work is committed; this test-scope decision prevents a compliant estate result.

## Geometry and budgets

All 50 Map 11 pin rows retain their values. All 986 original anti-climb wall records, 276 causeway pieces, 96 interior lava cells, six lava pools, 10 flames, two seals, and 112 Water-pool tiles retain their bytes. Raw records on Maps 8, 9, 10, 13, 17, 18, and 39 remain identical to main. [Identity checks](p4-m11b/identities.json) also verify the complete baseline GLOB prefix and the four unchanged art and usecode artifacts.

Map 11 records move from 9,685 to 9,731 raw, against the 10,000 ceiling, and from 20,910 to 22,821 expanded. Expanded records per land cell are 1.901433, against 2.9. Regional record-count increases stay within these budgets. All non-count bounds are preserved or tightened against main.

## Regions

Shares are fractions from zero to one. Ground-cell counts give each regional denominator. Exact measurements and every target failure are in [before-metrics.json](p4-m11b/before-metrics.json) and [after-metrics.json](p4-m11b/after-metrics.json).

### Entry hall

**Reads as:** a cut-stone antechamber.

The retained statue and broken wall shoulders frame the alcove. Eight decorative urns pair at the four column feet, and two upper-wall reliefs use paint-only shape 913. The filled flagstone and contrasting margins remain.

**Set piece:** votive alcove. [Capture](p4-m11b/setpieces/m11-votive-alcove.png).

**Target failures:** 0 → 0.

| Metric | Main | After |
|---|---:|---:|
| Ground cells | 576 | 576 |
| Props per 100 cells | 12.673611 | 14.930556 |
| Dressed share | 0.505208 | 0.555556 |
| Bare share | 0.003472 | 0.000000 |
| Grouped small-prop share | 0.627119 | 0.746479 |
| Stride share | 0.404255 | 0.338983 |
| Dominant material share | 0.548611 | 0.548611 |
| Material seam density | 0.067935 | 0.067935 |
| Period excess | 0.125926 | 0.125926 |
| Modal chunk share | 0.083333 | 0.083333 |
| Raw records | 550 | 563 |
| Expanded records | 1100 | 1113 |

### Hub

**Reads as:** a crossing with four doors, each marked for its element.

Earth has broken masonry, Air has a bare decorative spire, Fire has basalt and embers, and Water has a three-cell navy pool over retained supporting stone. Separate marker reservations preserve the crossing. Eight urns pair at the column feet. The two loose legacy spires leave; HUB_WEAPON and the four doors remain clear.

**Set piece:** elemental crossing. [Capture](p4-m11b/setpieces/m11-elemental-crossing.png).
The [north-door capture](p4-m11b/setpieces/m11-elemental-crossing-north.png) complements the crossing view.

**Target failures:** 3 → 0.

| Metric | Main | After |
|---|---:|---:|
| Ground cells | 576 | 576 |
| Props per 100 cells | 2.430556 | 14.062500 |
| Dressed share | 0.319444 | 0.531250 |
| Bare share | 0.072917 | 0.039931 |
| Grouped small-prop share | 0.000000 | 0.812500 |
| Stride share | 1.000000 | 0.392857 |
| Dominant material share | 0.548611 | 0.543403 |
| Material seam density | 0.065217 | 0.082428 |
| Period excess | 0.125439 | 0.123300 |
| Modal chunk share | 0.138889 | 0.111111 |
| Raw records | 354 | 410 |
| Expanded records | 894 | 964 |

### Earth

**Reads as:** a root cellar of the mountain.

The original root-and-fungus den and its two bounded soil pockets remain. North and west exterior calls select prefab 388 at z 96. Two uneven courses of flagstone fragments and non-standing rubble connect the cave mouth to its hall.

**Set piece:** golem root den. [Capture](p4-m11b/setpieces/m11-golem-root-den.png).

**Target failures:** 0 → 0.

| Metric | Main | After |
|---|---:|---:|
| Ground cells | 1600 | 1600 |
| Props per 100 cells | 10.750000 | 11.062500 |
| Dressed share | 0.500625 | 0.506250 |
| Bare share | 0.000000 | 0.000000 |
| Grouped small-prop share | 0.577236 | 0.598425 |
| Stride share | 0.201681 | 0.201681 |
| Dominant material share | 0.535625 | 0.533125 |
| Material seam density | 0.117308 | 0.120513 |
| Period excess | 0.073243 | 0.072917 |
| Modal chunk share | 0.030000 | 0.020000 |
| Raw records | 712 | 713 |
| Expanded records | 2228 | 2233 |

### Air

**Reads as:** a high cavern where the wind has stripped everything.

Seven non-standing rock shoulders form a broken ring around an empty centre. A collapsed east arc and an outward fan of chips make its breach legible. The scene has 27 explicit prop coordinates. The two retained rock ledges receive 20 clipped, paint-only riser faces at z zero, eight, and 16. The high perimeter caps receive no added faces.

**Set piece:** wind-broken ring. [Capture](p4-m11b/setpieces/m11-wind-broken-ring.png).

**Target failures:** 0 → 0.

| Metric | Main | After |
|---|---:|---:|
| Ground cells | 1600 | 1600 |
| Props per 100 cells | 17.000000 | 18.375000 |
| Dressed share | 0.510625 | 0.579375 |
| Bare share | 0.001250 | 0.001250 |
| Grouped small-prop share | 0.835556 | 0.865854 |
| Stride share | 0.218750 | 0.216327 |
| Dominant material share | 0.640000 | 0.637500 |
| Material seam density | 0.057051 | 0.060256 |
| Period excess | 0.160714 | 0.158988 |
| Modal chunk share | 0.090000 | 0.090000 |
| Raw records | 631 | 632 |
| Expanded records | 2352 | 2394 |

### Fire

**Reads as:** a rock island in a lava sea.

All seven lakes receive oriented decorative basalt on their existing cold cells. The accepted lip counts are nine, one, eight, six, eight, eight, and two. Partial beyond calls fill legal void cells beside the retained rim. The offering retains its tree, spires, stump, bones, and embers, with an uneven chip fringe. Threshold fragments continue into the Water-side shoulder.

**Set piece:** charred offering. [Capture](p4-m11b/setpieces/m11-charred-offering.png).

**Target failures:** 0 → 0.

| Metric | Main | After |
|---|---:|---:|
| Ground cells | 1387 | 1387 |
| Props per 100 cells | 5.191060 | 8.579668 |
| Dressed share | 0.263879 | 0.402307 |
| Bare share | 0.000000 | 0.000000 |
| Grouped small-prop share | 0.607843 | 0.660714 |
| Stride share | 0.323529 | 0.307692 |
| Dominant material share | 0.696467 | 0.695025 |
| Material seam density | 0.139387 | 0.141629 |
| Period excess | 0.089007 | 0.088338 |
| Modal chunk share | 0.036585 | 0.036585 |
| Raw records | 877 | 876 |
| Expanded records | 2434 | 2481 |

### Water

**Reads as:** a flooded hall with four dry islands.

The original 112 navy pool tiles and four dry islands remain. Plain glob 262 supplies the north, east, and exposed south exterior sea. Partial strips remain loose through packing, so the uniform sea introduces no repeated packed slivers. The portico remains, with grouped fallen landing debris and broken doorway shoulders.

**Set piece:** drowned portico. [Capture](p4-m11b/setpieces/m11-drowned-portico.png).

**Target failures:** 0 → 0.

| Metric | Main | After |
|---|---:|---:|
| Ground cells | 2560 | 2560 |
| Props per 100 cells | 9.335938 | 10.664062 |
| Dressed share | 0.404687 | 0.427734 |
| Bare share | 0.142578 | 0.119531 |
| Grouped small-prop share | 0.584211 | 0.650442 |
| Stride share | 0.141304 | 0.140909 |
| Dominant material share | 0.699219 | 0.699219 |
| Material seam density | 0.068780 | 0.068780 |
| Period excess | 0.121249 | 0.121249 |
| Modal chunk share | 0.106250 | 0.093750 |
| Raw records | 777 | 779 |
| Expanded records | 3336 | 3370 |

### Four pillars

**Reads as:** a bare ritual cave.

Five eight-unit slabs form a broken raised arc around an open ritual floor. Two decorative rock horns, collapsed masonry arms, urns, and bones complete the crescent. A small gravel scour sits beneath it. The architecture uses walkable_set_piece, and the decorative scene uses set_piece. The pillar entrance and pad approach receive floor fragments and non-standing debris; a decorative entrance urn groups the northern fragments. Every pillar, socket, seal, clipped support, and protected shot remains.

**Set piece:** broken ritual crescent. [Capture](p4-m11b/setpieces/m11-broken-ritual-crescent.png).

**Target failures:** 1 → 1.

| Metric | Main | After |
|---|---:|---:|
| Ground cells | 667 | 667 |
| Props per 100 cells | 9.595202 | 10.794603 |
| Dressed share | 0.541229 | 0.577211 |
| Bare share | 0.025487 | 0.014993 |
| Grouped small-prop share | 0.525424 | 0.537313 |
| Stride share | 0.318182 | 0.300000 |
| Dominant material share | 0.962519 | 0.887556 |
| Material seam density | 0.039056 | 0.083808 |
| Period excess | 0.144603 | 0.010781 |
| Modal chunk share | 0.090909 | 0.030303 |
| Raw records | 807 | 806 |
| Expanded records | 1405 | 1418 |

The retained allowance is `ground.top1`: the bare ritual cave and protected screen07 floor constrain material replacement. Its bound is tightened to the measured value. The focal scour reduces the dominant material share while preserving the cave sentence.

### Pad room

**Reads as:** plain cut stone.

The original ward, exit pad, arrivals, and walking lane remain. The cave-side shoulder gains broken threshold fragments. Each of the three corridors receives its relief at z 48 through paint_only; their stone walking strips and 242 verges remain.

**Set piece:** last ward. [Capture](p4-m11b/setpieces/m11-last-ward.png).

**Target failures:** 0 → 0.

| Metric | Main | After |
|---|---:|---:|
| Ground cells | 64 | 64 |
| Props per 100 cells | 14.062500 | 14.062500 |
| Dressed share | 0.718750 | 0.718750 |
| Bare share | 0.000000 | 0.000000 |
| Grouped small-prop share | unmeasurable | unmeasurable |
| Stride share | unmeasurable | unmeasurable |
| Dominant material share | 0.500000 | 0.500000 |
| Material seam density | 0.178571 | 0.178571 |
| Period excess | 0.260417 | 0.260417 |
| Modal chunk share | 0.250000 | 0.250000 |
| Raw records | 136 | 136 |
| Expanded records | 201 | 201 |

## Shared slice adoption

1. The removed Hub mask permits the elemental crossing and door markers. Actual hatch boxes, monster-placement constraints, pins, and quest bands remain protected.
2. The exterior sea uses only plain deep water: glob 262 and its partial 347 frame-16 tiles.
3. Shapes 908, 909, 910, and 911 supply non-standing spires, urns, rubble, and basalt. The pre-existing decorative rubble and bone rows remain available in the scene palette.
4. Shape 909 supplies all eight column-foot urn pairs.
5. Shapes 912 and 913 supply the three corridor reliefs at z 48 and the two entry reliefs. Shape 914 supplies only the 20 low Air ledge faces. All use paint_only.
6. Partial lava surrounds fill mixed chunks while retaining their rim members and FIRE_LINES clearances.
7. The shared invisible-collision flag correction is inherited. The existing editor-only support and collision records remain.
8. Decorative basalt occupies 42 cold-side cells across all seven lakes. Six doorway transitions use stone fragments and non-standing rubble on clear shoulders; protected walking bands and shot pixels are retained.
9. The Earth exterior adopts the explicit 388 family at z 96.

Shared request 10 is the [prepared water-test correction](p4-m11b/shared-water-test.patch): scope the 112-tile count to the Water section, retaining the frame, height, and flagstone-support checks across all 115 decorative water tiles. The original brief forbids test edits, so this patch remains unapplied pending an explicit exception. No shared module, test, recovered source, or shape allocation is edited. The additional footing debris and entrance urn preserve main’s grouping bounds; the small ritual scour and varied floor frames preserve its material and repetition bounds.

## Windows, visual items, and feedback

The complete estate reports screen05 at 94.55% and screen07 at 97.28%, matching main. Both remain within the required 0.25-point range; all 39 vignette checks pass against the final artifacts.

VQ-045 and VQ-065 adopt their elemental exterior replacements. VQ-097 and VQ-158 adopt the cell-level basalt shore transition. VQ-020 retains the open connector views. VQ-035, VQ-038, and VQ-043 retain their earlier geometry and protected cave treatment. Fresh Astra grading remains outside this slice. The two frame-five tapestry replacements and the removed 186 and 796 stand-ins from the merged first run remain. The new ritual crescent replaces its loose effigy with a low architectural arc.

`docs/map-feedback/OPEN.md` contains no open notes. No feedback-server response was needed.

## Verification and evidence

- `tools/build_artifacts.sh --record`: successful, zero map-validation warnings or errors. `--verify`: all six canonical hashes match.
- `test_dressing.py 11 --strict`: zero failures, one retained named target allowance in Four pillars.
- Strict visual quality: zero failures. Frame black mean falls from 0.052639 to 0.041879; p95 falls from 0.206844 to 0.186805. Specified walkable black remains zero. Other visibility bounds hold against main.
- `tools/run_all_tests.sh`: 56 of 58 files pass. Route checks pass 166, paint-cycle checks pass 76, vignette checks pass 39, object hygiene passes 60, monster eggs pass 459, and map-pin freshness passes three.
- `test_art_props.py`: 1,016 passed, one failed. The global count expects 112 shape-896 tiles; the requested Hub marker adds three, while all 112 original Water tiles remain. Every decorative water tile now has shape-35 support. The prepared patch scopes only the count to the Water section. An in-memory preview of that exact patch passes all 1,017 checks without modifying the repository test.
- `test_integration_state.py`: the permitted failure. The shared install and harness retain different FIXED and GLOB bytes; engine checks also skip because this worktree has no local engine build. Capture games use private canonical snapshots. The shared install is unchanged.
- `codex exec review --base main`: the default sandbox failed to start commands owing to a bubblewrap user-namespace error. The unrestricted retry completed with one P2 finding about the new Hub water tiles. Its support issue is corrected in the builder. Its count issue remains pending the test-ownership exception. The final unrestricted review confirms the count mismatch as its sole P2 finding; its fresh art test reports 1,016 passed and one failed, and its hygiene test passes all 60 checks.
- `git diff --check`: clean. No test, shared module, recovered source, or shape allocation is changed. Main remains outside the write scope. No merge or push was performed.

The [build log](p4-m11b/pool-support-build.log.gz), [dressing log](p4-m11b/dressing.log.gz), [visual log](p4-m11b/visual.log.gz), [estate log](p4-m11b/estate.log.gz), [initial review](p4-m11b/review.log.gz), [final review](p4-m11b/review-final.log.gz), and [proposed-test preview](p4-m11b/proposed-test-preview.log.gz) preserve the commands and results. Per-test logs are in [checks](p4-m11b/checks/).

### Capture provenance and inspection

The baseline contains 52 fresh, landed captures. The final artifact snapshot supplies 52 regional after-captures and 14 set-piece and detail captures, all at 640 by 400. Every final image was personally inspected at its full pixel dimensions. The [inspection notes](p4-m11b/inspection.json) bind each observation to its image SHA-256. The [inventory](p4-m11b/capture-inventory.json), [validation](p4-m11b/capture-validation.json), and [engine-log audit](p4-m11b/capture-log-audit.json) record landings, dimensions, coverage, and warnings.

Captures use display `:85`, runtime `/tmp/claude-1000/vq4-m11b`, and `usehighres=false`. The unchanged `tour_capture.py` starts a fresh world for every stop. A private xdotool wrapper spaces modifier and focus events, following the first run’s capture method. Private games hold separate baseline and final artifacts; [provenance](p4-m11b/provenance.json) records hashes and configuration. All accepted Map 11 capture log tails have zero paint-cycle warnings and zero process warnings. Earlier startup warnings are separately counted in the audit.

The original green 242 corridor verges remain visible in both baselines and final captures. The partial Avatar occlusion beside the Water east wall also matches its baseline. These retained features are recorded in the inspection notes.

### Remaining shared request

The original brief forbids test edits. The [four-line correction](p4-m11b/shared-water-test.patch) remains unapplied while the explicit exception is pending. Applying it here, or having the shared owner land it, permits the required estate rerun. The present estate result exceeds the user’s allowed failure list, so this run records that unresolved result explicitly.

## Commits

Builder and evidence commits, oldest first:

```text
4addc39f Record Map 11 second-run baseline and evidence plan
3cff6805 Preserve the first Map 11 baseline capture batch
0fdabfc4 Compose Map 11 ritual scenes and adopt shared dressing paths
21f4c0bf Preserve Map 11 geometry comparisons and baseline tour progress
c9142d52 Retain marker support and compose irregular debris transitions
58382b3f Break repeated ritual grain and threshold chip spacing
84167468 Record Map 11 dressing improvements and baseline capture progress
24a8c904 Tighten Map 11 dressing and visibility pins against main
c256fe00 Finish pillar and pad doorway fragment transitions
6a7686e3 Complete the landed baseline tour and preserve the capture runner
ab4779e0 Group the ritual entrance fragments around a decorative urn
04951489 Record final Map 11 ratchets and the first inspected scenes
360594a7 Limit riser paint to the two low Air ledges
cdb87b6b Record the regional report and corrected riser measurements
a4ac9b1c Refresh the Map 11 artifact hash with all pin rows unchanged
3c4f02e6 Place the Hub water marker over retained flagstone
9d9af03b Preserve inspected scenes and the proposed shared water assertion fix
f47f9508 Record both composed scenes and the supported Hub marker measurements
b715e672 Preserve the first regional after captures and inspection notes
2f80405d Preserve regional inspection evidence and the complete estate logs
a3f5b77b Preserve final regional captures and verification results
```

The final report and audit are committed after this list. The branch remains `wt/vq4-m11b`. Main advanced only its HANDOFF during this run; its artifact hashes and all comparison pins remain identical to the starting baseline.

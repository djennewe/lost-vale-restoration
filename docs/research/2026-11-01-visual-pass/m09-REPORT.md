# Map 09 phases two and three

Map 09 improves visibility and guardian-shell coverage, with **68 of 633 quest-band cells still below 50% visibility**. The baseline has 116. The prescribed one-course walls and protected screen10 geometry prevent the zero-cell exit criterion from being met within this slice. No occlusion allowance was added.

Branch: `wt/vq2-m09`, based on `ba34836`. Phase two: `d3c2dce`. Phase three: `7ae7fda`. The final evidence commit is recorded in the branch history.

## VQ-026: hall near walls

Cause: the south and east walls drew both 48-unit courses, hiding the Avatar near those walls. Change: replace only their upper courses with coincident 497 and 498 blockers at z 48. North and west retain both drawn courses. The hall barrier remains 96 units tall.

Disposition: **improved**. The retained ground course still obscures adjacent positions. This is a measured limitation of the specified one-course treatment.

| Stop | Walkable black | Frame black % | Minimum visible % |
|---|---:|---:|---:|
| m09-16 | 0 → 0 | 50.248 → 49.504 | 0.00 → 23.32 |
| m09-17 | 0 → 0 | 43.452 → 43.452 | 0.00 → 14.70 |
| m09-18 | 0 → 0 | 12.840 → 12.840 | 23.99 → 100.00 |
| m09-22 | 0 → 0 | 40.912 → 40.912 | 0.00 → 12.26 |

## VQ-029: south doorway lintel

Cause: the continuous drawn upper course crosses the south doorway. Change: the same phase-two south backstop replaces its lintel with 497 at z 48. The 40-unit Avatar retains clearance beneath it. The north throat lintel stays drawn.

Disposition: **fixed** at the cited stop, with 96.25% of the worst pose visible.

| Stop | Walkable black | Frame black % | Minimum visible % |
|---|---:|---:|---:|
| m09-21 | 0 → 0 | 20.610 → 20.610 | 41.21 → 96.25 |

## VQ-032: worked-passage east wall

Cause: two drawn 40-unit masonry courses stand in front of the reachable passage. Change: retain the east ground course, substitute 498 at z 40, and continue the blocker at z 88. The west wall, west reliefs, columns, and south masonry remain.

Disposition: **improved**. The cited stop rises above complete occlusion but remains below 50%. Further work would change the specified retained ground course or nearby south wall.

| Stop | Walkable black | Frame black % | Minimum visible % |
|---|---:|---:|---:|
| m09-27 | 0 → 0 | 49.178 → 49.178 | 0.00 → 33.29 |

## VQ-051: guardian-shell joints and tops

Cause: short stacked shell runs have exposed corner joins and open tops. Change: add 116 retail shape-125 interior crests at z 96. Fourteen 29 posts replace existing south-face corner strips; the corresponding pieces are shortened by 32 units. Every generated crest and replacement corner sprite passes `shot.paints_window`. The collision occupancy of each corner replacement exactly equals its original occupancy.

Ten otherwise admissible crests are excluded where a north or west neighbour is floor. The full-cap candidate created two completely hidden 256-unit samples. This near-face exclusion restores the phase-two visibility distributions while preserving most of the coverage improvement. No new shape ID or shared-module change is required.

Disposition: **improved**. Protected-window clipping and the visibility-preserving near-face exclusion remain intentional limits.

The phase-three baseline below is the measured post-phase-two build.

| Stop | Walkable black | Frame black % | Minimum visible % |
|---|---:|---:|---:|
| m09-01 | 0 → 0 | 29.972 → 11.713 | 100.00 → 100.00 |
| m09-02 | 0 → 0 | 32.902 → 24.984 | 100.00 → 100.00 |
| m09-03 | 0 → 0 | 28.623 → 16.354 | 100.00 → 100.00 |
| m09-04 | 0 → 0 | 37.619 → 20.705 | 99.87 → 99.87 |
| m09-05 | 0 → 0 | 28.441 → 19.049 | 100.00 → 100.00 |
| m09-06 | 0 → 0 | 51.711 → 35.975 | 1.75 → 1.75 |

## VQ-062: accepted cave exterior

Cause: black exterior beyond the hall and passage walls. Section 4.2 accepts this cave idiom. No dedicated change was made. The global frame ratchets hold, despite small per-stop changes caused by the specified wall and shell work.

Disposition: **blocked from further change by the accepted scope**.

| Stop | Walkable black | Frame black % | Minimum visible % |
|---|---:|---:|---:|
| m09-12 | 0 → 0 | 45.340 → 45.340 | 97.06 → 100.00 |
| m09-19 | 0 → 0 | 13.644 → 13.697 | 100.00 → 100.00 |
| m09-27 | 0 → 0 | 49.178 → 49.178 | 0.00 → 33.29 |

## VQ-001: protected dais black

Cause: screen10's protected black silhouette excludes generated floor, and `void_cover` supplies its required edge covers. Douglas's decision D10 keeps those pixels. The phase-one report measured an eight-point window loss from continuous replacement floor. This slice preserves `SCREEN10_BLACK_FILLERS`, `SCREEN10_RELIFT`, `GUARDIAN_MASK`, and `dais_skeleton`.

Disposition: **blocked by D10's protected screenshot**. Zero reached cells have specified or unpainted black floor. The 19 prop-pixel probes remain.

The in-slice guardian observations below compare the original baseline with the final build. Their floors remain drawn. VQ-001 received no implementation change; frame differences come from VQ-051 and the hall walls.

| Stop | Walkable black | Frame black % | Minimum visible % |
|---|---:|---:|---:|
| m09-01 | 0 → 0 | 29.972 → 11.713 | 100.00 → 100.00 |
| m09-03 | 0 → 0 | 28.623 → 16.354 | 100.00 → 100.00 |
| m09-04 | 0 → 0 | 37.619 → 20.705 | 99.87 → 99.87 |
| m09-05 | 0 → 0 | 28.401 → 19.049 | 100.00 → 100.00 |
| m09-06 | 0 → 0 | 51.599 → 35.975 | 1.75 → 1.75 |
| m09-16 | 0 → 0 | 50.248 → 49.504 | 0.00 → 23.32 |


## Measurements, windows, and record budgets

All stop tables use the independent floor probe at the Avatar's bottom centre, a 640 by 400 offline frame, and the minimum visible fraction across 72 walk and stand poses. Their full rows are in `m09/before-stop-metrics.json`, `phase2-stop-metrics.json`, and `after-stop-metrics.json`. The phase-two tables compare the initial baseline with the final build; phase three preserves their visibility results.

| Measurement | Before | Phase two | Phase three |
|---|---:|---:|---:|
| Reached cells | 5,908 | 5,908 | 5,908 |
| Specified or unpainted black probes | 0 | 0 | 0 |
| Prop black probes | 19 | 19 | 19 |
| Quest-band cells below 50% | 116 | 68 | 68 |
| Raw records | 1,019 | 1,027 | 1,226 |
| Expanded records | 1,349 | 1,357 | 1,556 |
| Screen10 class score % | 89.517253 | 89.517253 | 89.517253 |
| Screen10 total unpainted pixels | 794 | 794 | 794 |

Screen10's score floor is 89.27%, with its 794-pixel allowance. Palette-index renders are pixel-identical across all three states, with zero changed pixels and identical SHA-256 hashes (`m09/window-scores.json`). Every item in this report shares the window scores and record counts above. The exit record ceiling is 1,800, leaving 574 records. The `void_cover` call remains last. All 405 baseline ground-cover records remain, including all 30 original 35:10 tiles. The final outer ring adds 75 plates because the crests are land surfaces. Elevated crests count as XY cover while painting above the ground projection. The initial cap candidate therefore discarded ground plates and left stale pixels in low-resolution play. A fresh m09-02 capture exposed this; the offline probe measured 777 newly unpainted pixels. Preserving the full pre-cap ground cover restores that stop to zero unpainted pixels. All 14 stops retain their phase-two unpainted counts, with zero newly uncovered pixels. No pinned item moved.

| Step-128 map distribution | Before | Phase two | Phase three |
|---|---:|---:|---:|
| Cells below 50% visibility | 26.567% | 16.119% | 16.119% |
| Completely hidden cells | 10.149% | 1.791% | 1.791% |
| Median minimum visibility | 99.505% | 100% | 100% |
| Frame black mean | 26.054% | 26.088% | 24.174% |
| Frame black p95 | 53.395% | 53.429% | 51.799% |
| Frame black max | 64.307% | 64.307% | 64.307% |

The permanent test samples visibility at 256 units and frames at 512 units. Its final pins are 13.158% below half, zero hidden, 100% median, and frame mean/p95/max 19.814%/37.361%/47.170%. Every improved pin was tightened. Record pins rose within the published ceiling. Phase two temporarily exceeded the frame-mean and frame-p95 pins; phase three restores both below the original baseline. The phase-two visual test recorded those two failures explicitly.

Exact geometry comparisons use the built archives, expand globs, run the dry arrival flood, compare world XYZ sets, and call `walk_off`. Every phase has the same 5,908 positions, zero lost or gained positions, zero falls, zero void, zero off-map results, and the same 90 inherited teeter records. `m09/geometry.json` records the comparison. Independent verification also compares the half-open unit occupancy of the corner replacements.

## Evidence protocol

Before changes, after phase two, and after phase three:

```sh
python3 -B agents/map-populator/src/void_audit.py 9 --step 128 --workers 4 --out EVID/STATE-audit
python3 -B agents/map-populator/src/avatar_visibility.py 9 --step 128 --workers 4 --out EVID/STATE-audit
python3 -B agents/map-populator/src/test_visual_quality.py 9 --report128 --out EVID/STATE-audit
```

Final pins were recorded with `test_visual_quality.py 9 --record --report128`. Each audit includes artifact provenance. The raw void audit reports 19 black probes and a false zero-tolerance summary because it includes prop pixels; the permanent test distinguishes those 19 from specified or unpainted floors and passes.

Fresh in-engine captures use the unchanged `tour_capture.py`, display `:62`, runtime directory `/tmp/claude-1000/vq2-m09`, and a private ScummVM config with `usehighres=false`. Baseline and phase-two runtime copies freeze the tool, artifacts, and private game directory while subsequent builds run. A private `xdotool` wrapper spaces debugger modifier transitions by 120 ms. The capture script itself is byte-identical in all three environments. Image validation rejects a frame-black discrepancy above 1.5 percentage points, which caught a landed capture still showing the intro movie. Rejected images and retry logs are retained. All game-data entries under `shared/data` link to main; `shared/build` and the installed capture game are private copies. No installation modifies those main-checkout data links.

All 42 required captures are valid: 14 before, 14 after phase two, and 14 after phase three. Every image is 640 by 400, every metadata row has `ok: true` and `landed: true`, and the contact sheets were visually inspected. Engine frame-black measurements agree with the corresponding offline frames within 0.286 percentage points across all 42 captures. `m09/capture-summary.json` and `engine-frame-metrics.json` retain the measurements and image hashes.

Saved engine logs cover eight baseline stops and all 14 stops after each phase. They contain zero paint-dependency-cycle lines and zero `Non-existent process` lines while on Map 09. Each saved fresh-world session retains three inherited `Non-existent process` warnings during its Map 0 prelude: 24 in the saved baseline sample, 42 after phase two, and 42 after phase three. Raw-log zero-warning hygiene therefore remains qualified by this unchanged prelude. No usecode or engine change was authorized for this slice.

## Artifact hashes

TYPEFLAG, U8SHAPES, ANIM, and EUSECODE remain identical across both phases:

```text
ac0b33486fc167d98c07c32011de348c11ae0cefb8d89fc2597ef984133a5fd1  TYPEFLAG.DAT
aad6ed7b8961f416b6fae225d467427899a4487db768b6fb486ed5b5cb3e73ba  U8SHAPES.FLX
97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443  ANIM.DAT
b47c324cdad77646c27755acfdd5bca53a9d92e16268db229f18e7dd780d4205  EUSECODE.FLX
```

FIXED hashes identify each map state:

```text
89da4e165833bff0b4da526cfa2cbc434336f6816e3964ae9982bd804a2eb767  before
0d77edd01e51ed6f87993d21eb5d422da669aa6ee852796c838df765e378d0fc  phase two
fcc45a0431cc366a5d6097688a1acb67b19455a97d10933d2a19b5f24b9b8975  phase three
```

Every item shares these hashes. `tools/build_artifacts.sh --record` succeeds for both phases. The final compiler report has 55 successful compilations and the two allowlisted failures, EALOGO.UNK and TJORVI.UNK. `derive_map_pins.py` regenerated the inventory for both commits.

## Estate and review

Final permanent visual test: zero failures, with the 68-cell phase-exit debt printed. The strict zero-leg exit criterion remains unmet; no claim of strict acceptance is made.

`tools/run_all_tests.sh`: **56 of 57 test files passed**. The sole failure is the allowed `test_integration_state.py`: 10 assertions passed, one failed, and three were skipped. Its private harness-byte check passes in all six places. Its installation check fails because `shared/data/u8-install/STATIC/FIXED.DAT` still holds main's installed bytes. That directory is a symlink to main, so this slice leaves it untouched. The process exits one for that sole allowed failure. Earlier runs were interrupted for the cover-preservation corrections; their partial output is retained separately. The completed estate uses FIXED `fcc45a04`.

Constraint results: paint cycles 76 passed; route reachability 166 passed; monster eggs 459 passed; interaction destinations 201 passed; all 39 vignette assertions passed; map hygiene 60 passed; pin freshness three passed; the permanent visual test passed across all eight maps. Full output is `m09/tests.log`, with the integration failure preserved separately.

Independent verifier: phase-two and phase-three exact geometry and screen10 checks pass. Corner solid occupancy matches. All added sprites are clipped from the protected window. The verifier identified retained ground walls, the untouched worked south wall, guardian shell, and screen10 prop 411:14 as remaining route occluders. Details are in `m09/verifier-phase2.md`.

`codex exec review --base main` initially could not inspect the repository because bubblewrap returned `Failed RTM_NEWADDR: Operation not permitted`. The retry uses the workspace's existing unrestricted execution policy. The final review after full ground-cover preservation completed with exit code zero and no actionable regressions. An ephemeral retry avoided a CLI session-recording error that occurred after the preceding review printed its verdict. Its independent hygiene, edge-containment, pin-freshness, and all 39 vignette checks passed, and FIXED matched the updated manifest. An earlier review confirmed both Map 09 exits and the guardian dais. The complete estate result is reported separately.

## Remaining work and boundaries

- VQ-026: improved, with adjacent hall ground-course occlusion remaining.
- VQ-029: fixed at its cited stop; global quest-band debt remains elsewhere.
- VQ-032: improved, with 33.29% worst-pose visibility at its cited stop.
- VQ-051: improved; protected-window clips and ten near-face cap exclusions remain.
- VQ-062: blocked from further change by the accepted cave-exterior scope.
- VQ-001: blocked by D10's instruction to preserve screen10's black dais silhouette.

Continuous in-engine walks remain for the orchestrator's verifier. This slice supplies fresh teleports and built-geometry route evidence.

The 68 remaining leg cells require a reviewed scope extension for retained lower walls, guardian near faces, protected screenshot props, or an explicit allowance. No shared-module or new-shape request arose. Retail content, quest positions, and usecode were unchanged. No merge, push, or main-checkout write occurred.

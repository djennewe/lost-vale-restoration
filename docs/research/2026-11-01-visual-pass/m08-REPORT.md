# Map 08 visual quality, phases two and three

Branch: `wt/vq2-m08`, based on `ba34836`. Phase two: `740d7ad`. Phase three implementation: `3afd91c`.

Map 08’s frame black improves while physical geometry and Avatar visibility stay unchanged. The first-seam aperture receives complete opaque repaint. The 79 existing shelf-band occlusions remain an explicit limitation. Astra’s final grade is pending the orchestrator’s post-merge review.

## Evidence and phase order

Phase two committed the D1 retail-roof decision before phase three. Baseline and post-phase-two `void_audit.py 8 --arrival 29680 24400 56 --step 128 --workers 4`, `avatar_visibility.py` with the same arguments, and `test_visual_quality.py 8` reproduce the baseline. Phase three was committed before the post-commit audits. `final-audit/map08-metrics.json` and its hashes identify the stable rebuilt artifacts; the separate void and visibility rows are in `after-audit/`.

All 31 before and 31 after captures have `landed: true`, with 640×400 surfaces. The manifests record each actual position and the captured artifact hashes. Captures use `tour_capture.py` through a runtime driver, private display `:68`, `XDG_RUNTIME_DIR=/tmp/claude-1000/vq2-m08`, an explicit private config with `usehighres=false`, and a fresh session per stop. The baseline runner has private copies of the baseline build and patched game. The after runner uses the worktree’s build and private patched game. At m08-08, both worlds enable `Cheat::toggleInvincibility on` and use an initial settle of 8 seconds followed by map-position polling, because nearby retail ghouls kill or knock the fresh Avatar away during the normal settle of 22 seconds. The manifest records this exception. Earlier setup attempts were discarded.

Each stop table compares the same requested witness coordinate on both builds: one floor probe (zero or one black probe), modelled frame-black percentage, and minimum Avatar visibility across 72 poses. These model measurements use the requested camera even where the live Avatar settles elsewhere, preserving a controlled before-to-after comparison. The per-stop JSON files record both requested and captured coordinates. Full-component walkable black remains exactly the 256 inherited cells. The pristine pocket has 304 cells; the exposed component has zero walkable black across 15,454 cells (`m08/pocket.json`). The manifests preserve the requested and settled positions; some retail teleports settle at another height (m08-17 and m08-27 settle at z 48). PNG frame-black measurements are listed separately in `m08/capture-metrics.json`.

## Phase-two leg table

The phase-two build has the baseline artifact hashes. Its before captures also supply the phase-two after frames because D1 changes no game bytes.

| Band | Band cells | Below half outside allowances, before → after phase two |
|---|---:|---:|
| shelf-1 | 15 | 0 → 0 |
| shelf-2 | 252 | 79 → 79 |
| shelf-3 | 378 | 0 → 0 |
| door-1 | 53 | 0 → 0 |

Band overlaps leave 682 unique tested cells. Phase three retains these visibility counts.

## Per-item results

### VQ-003: Improved: aperture repaint repaired

Cause: Ownership leaves air between the retained threshold and lintel unpainted. At m08-06 (320,290), the model had no owner while an intermediate low-resolution capture held RGB (32,20,0), consistent with retained-frame residue. Retained retail walls and shelves own most neighbouring pixels; the 894/895 surface backdrops do not repaint the complete removed-wall sprite.

Change: Added two black 895:2 decorative plates behind the aperture at z 0. They repaint 755 formerly unpainted pixels in each m08-05/06 model frame, cover every opaque pixel of the removed 32:1 wall, and change zero existing visible colours. The four physical 301 threshold tiles, lintel, ceilings, and raised shelf retain their records. The new regression checks the removed wall mask and both aperture witness pixels. The retained grey fleck remains retail; Astra’s final grade is pending.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-05](m08/before/m08-05.png) → [after](m08/after/m08-05.png) | 1 → 1 | 20.15 → 20.15 | 0.00 → 0.00 |
| [m08-06](m08/before/m08-06.png) → [after](m08/after/m08-06.png) | 1 → 1 | 50.74 → 50.74 | 0.12 → 0.12 |
| [m08-07](m08/before/m08-07.png) → [after](m08/after/m08-07.png) | 0 → 0 | 24.97 → 24.97 | 40.70 → 40.70 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

### VQ-004: Improved

Cause: The repaired shelf’s 301 floor ends at irregular black underlay borders and uncovered cells in its view envelope.

Change: Retained each original underlay. Added 256-unit 895:0 skirts over uncovered view blocks, with retail painted-cover cells subtracted. The first-seam camera windows are excluded because retained ceilings cut new plates into detached fragments there. The skirts supply no LAND, SOLID, or ROOF flags.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-10](m08/before/m08-10.png) → [after](m08/after/m08-10.png) | 0 → 0 | 34.10 → 33.65 | 100.00 → 100.00 |
| [m08-12](m08/before/m08-12.png) → [after](m08/after/m08-12.png) | 0 → 0 | 23.08 → 10.02 | 100.00 → 100.00 |
| [m08-14](m08/before/m08-14.png) → [after](m08/after/m08-14.png) | 0 → 0 | 59.29 → 18.98 | 100.00 → 100.00 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

### VQ-008: Improved

Cause: The isolated panel is the retained 31:4 upper jamb at (30335,26367,104), with 29 end pieces. Its lower 32:7 course is black, so the textured upper panel appears detached.

Change: Changed that lower course to frame zero. The collision box and upper jamb stay in place. Skirt and floor-border paint reduce the surrounding black. Hiding the upper panel was tried and discarded because it exposed more black.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-09](m08/before/m08-09.png) → [after](m08/after/m08-09.png) | 0 → 0 | 23.46 → 23.09 | 60.07 → 60.07 |
| [m08-49](m08/before/m08-49.png) → [after](m08/after/m08-49.png) | 0 → 0 | 24.51 → 23.96 | 83.69 → 83.69 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

### VQ-046: Improved at the four approved route stops

Cause: Black extends beyond the painted retail floor in the four D2 route witness windows. Other witnesses retain retail cave darkness.

Change: Added decorative view skirts seeded at m08-15 (29151,30303), m08-45 (20319,3247), m08-46 (20031,3423), and m08-47 (21199,3855). No retained retail record changed. Some other cameras can see the same LV skirt pixels.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-01](m08/before/m08-01.png) → [after](m08/after/m08-01.png) | 0 → 0 | 68.03 → 68.03 | 100.00 → 100.00 |
| [m08-06](m08/before/m08-06.png) → [after](m08/after/m08-06.png) | 1 → 1 | 50.74 → 50.74 | 0.12 → 0.12 |
| [m08-08](m08/before/m08-08.png) → [after](m08/after/m08-08.png) | 0 → 0 | 22.81 → 22.26 | 100.00 → 100.00 |
| [m08-11](m08/before/m08-11.png) → [after](m08/after/m08-11.png) | 0 → 0 | 26.50 → 26.49 | 100.00 → 100.00 |
| [m08-13](m08/before/m08-13.png) → [after](m08/after/m08-13.png) | 0 → 0 | 38.06 → 38.06 | 96.50 → 96.50 |
| [m08-15](m08/before/m08-15.png) → [after](m08/after/m08-15.png) | 1 → 1 | 69.21 → 69.01 | 0.00 → 0.00 |
| [m08-33](m08/before/m08-33.png) → [after](m08/after/m08-33.png) | 0 → 0 | 67.50 → 67.50 | 85.18 → 85.18 |
| [m08-34](m08/before/m08-34.png) → [after](m08/after/m08-34.png) | 0 → 0 | 47.00 → 47.00 | 100.00 → 100.00 |
| [m08-35](m08/before/m08-35.png) → [after](m08/after/m08-35.png) | 0 → 0 | 33.79 → 33.79 | 100.00 → 100.00 |
| [m08-37](m08/before/m08-37.png) → [after](m08/after/m08-37.png) | 0 → 0 | 62.37 → 62.37 | 0.00 → 0.00 |
| [m08-38](m08/before/m08-38.png) → [after](m08/after/m08-38.png) | 1 → 1 | 59.74 → 59.74 | 0.00 → 0.00 |
| [m08-40](m08/before/m08-40.png) → [after](m08/after/m08-40.png) | 1 → 1 | 72.33 → 72.33 | 0.00 → 0.00 |
| [m08-41](m08/before/m08-41.png) → [after](m08/after/m08-41.png) | 0 → 0 | 28.76 → 28.76 | 100.00 → 100.00 |
| [m08-42](m08/before/m08-42.png) → [after](m08/after/m08-42.png) | 0 → 0 | 74.25 → 74.02 | 0.00 → 0.00 |
| [m08-44](m08/before/m08-44.png) → [after](m08/after/m08-44.png) | 0 → 0 | 75.77 → 75.77 | 97.37 → 97.37 |
| [m08-45](m08/before/m08-45.png) → [after](m08/after/m08-45.png) | 0 → 0 | 51.55 → 51.25 | 95.95 → 95.95 |
| [m08-46](m08/before/m08-46.png) → [after](m08/after/m08-46.png) | 0 → 0 | 46.29 → 46.04 | 100.00 → 100.00 |
| [m08-47](m08/before/m08-47.png) → [after](m08/after/m08-47.png) | 0 → 0 | 49.00 → 48.26 | 0.00 → 0.00 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

### VQ-018: Blocked by D1, accepted retail occlusion

Cause: The backlog identifies retail roof, wall, or shelf occlusions in these areas. Stop measurements use the requested witness coordinates on both builds.

Change: Douglas’s D1 answer of 3 November 2026 retains them. Phase two clarified the approved VQ-018 pin reason as “retail roofs, Douglas 2026-11”. The baseline pin files already supplied the witness envelopes. Geometry and measured pins remain unchanged in phase two.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-36](m08/before/m08-36.png) → [after](m08/after/m08-36.png) | 0 → 0 | 78.11 → 78.11 | 0.00 → 0.00 |
| [m08-37](m08/before/m08-37.png) → [after](m08/after/m08-37.png) | 0 → 0 | 62.37 → 62.37 | 0.00 → 0.00 |
| [m08-38](m08/before/m08-38.png) → [after](m08/after/m08-38.png) | 1 → 1 | 59.74 → 59.74 | 0.00 → 0.00 |
| [m08-40](m08/before/m08-40.png) → [after](m08/after/m08-40.png) | 1 → 1 | 72.33 → 72.33 | 0.00 → 0.00 |
| [m08-42](m08/before/m08-42.png) → [after](m08/after/m08-42.png) | 0 → 0 | 74.25 → 74.02 | 0.00 → 0.00 |
| [m08-43](m08/before/m08-43.png) → [after](m08/after/m08-43.png) | 0 → 0 | 64.08 → 64.08 | 3.50 → 3.50 |
| [m08-47](m08/before/m08-47.png) → [after](m08/after/m08-47.png) | 0 → 0 | 49.00 → 48.26 | 0.00 → 0.00 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

### VQ-022: Blocked by D1, accepted retail occlusion

Cause: The backlog identifies retail roof, wall, or shelf occlusions in these areas. Stop measurements use the requested witness coordinates on both builds.

Change: Douglas’s D1 answer of 3 November 2026 retains them. Phase two clarified the approved VQ-018 pin reason as “retail roofs, Douglas 2026-11”. The baseline pin files already supplied the witness envelopes. Geometry and measured pins remain unchanged in phase two.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-05](m08/before/m08-05.png) → [after](m08/after/m08-05.png) | 1 → 1 | 20.15 → 20.15 | 0.00 → 0.00 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

### VQ-023: Blocked by D1, accepted retail occlusion

Cause: The backlog identifies retail roof, wall, or shelf occlusions in these areas. Stop measurements use the requested witness coordinates on both builds.

Change: Douglas’s D1 answer of 3 November 2026 retains them. Phase two clarified the approved VQ-018 pin reason as “retail roofs, Douglas 2026-11”. The baseline pin files already supplied the witness envelopes. Geometry and measured pins remain unchanged in phase two.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-15](m08/before/m08-15.png) → [after](m08/after/m08-15.png) | 1 → 1 | 69.21 → 69.01 | 0.00 → 0.00 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

### VQ-030: Blocked by D1, accepted retail occlusion

Cause: The backlog identifies retail roof, wall, or shelf occlusions in these areas. Stop measurements use the requested witness coordinates on both builds.

Change: Douglas’s D1 answer of 3 November 2026 retains them. Phase two clarified the approved VQ-018 pin reason as “retail roofs, Douglas 2026-11”. The baseline pin files already supplied the witness envelopes. Geometry and measured pins remain unchanged in phase two.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-17](m08/before/m08-17.png) → [after](m08/after/m08-17.png) | 0 → 0 | 0.05 → 0.05 | 0.00 → 0.00 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

### VQ-031: Blocked by D1, accepted retail occlusion

Cause: The backlog identifies retail roof, wall, or shelf occlusions in these areas. Stop measurements use the requested witness coordinates on both builds.

Change: Douglas’s D1 answer of 3 November 2026 retains them. Phase two clarified the approved VQ-018 pin reason as “retail roofs, Douglas 2026-11”. The baseline pin files already supplied the witness envelopes. Geometry and measured pins remain unchanged in phase two.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-02](m08/before/m08-02.png) → [after](m08/after/m08-02.png) | 0 → 0 | 30.64 → 30.64 | 11.60 → 11.60 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

### VQ-044: Blocked by D2, retained off-route retail

Cause: These black regions belong to retail routes outside D2’s four approved witnesses.

Change: Retained every pristine record. The pool-bank m08-03 camera also sees part of the shelf’s new skirt, giving an incidental frame-black reduction; its retail floor, walls, and water remain unchanged.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-03](m08/before/m08-03.png) → [after](m08/after/m08-03.png) | 0 → 0 | 55.94 → 54.63 | 0.00 → 0.00 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

### VQ-060: Blocked by D2, retained off-route retail

Cause: These black regions belong to retail routes outside D2’s four approved witnesses.

Change: Retained every pristine record. The pool-bank m08-03 camera also sees part of the shelf’s new skirt, giving an incidental frame-black reduction; its retail floor, walls, and water remain unchanged.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-02](m08/before/m08-02.png) → [after](m08/after/m08-02.png) | 0 → 0 | 30.64 → 30.64 | 11.60 → 11.60 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

### VQ-064: Blocked by D2, retained off-route retail

Cause: These black regions belong to retail routes outside D2’s four approved witnesses.

Change: Retained every pristine record. The pool-bank m08-03 camera also sees part of the shelf’s new skirt, giving an incidental frame-black reduction; its retail floor, walls, and water remain unchanged.

| Stop (before → after captures) | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| [m08-27](m08/before/m08-27.png) → [after](m08/after/m08-27.png) | 1 → 1 | 57.83 → 57.83 | 100.00 → 100.00 |

Windows: Map 08 has no pinned 1994 screenshot window. Records: phase two 5,689 raw and 29,009 expanded; phase three 5,923 raw and 29,243 expanded. Hashes and common verification appear below.

## Map measurements

| Metric | Before | After |
|---|---:|---:|
| walkable_black_specified | 0 | 0 |
| walkable_black_prop | 0 | 0 |
| leg_cells_below_half | 79 | 79 |
| cells_below_half_share | 14.228% | 14.228% |
| cells_hidden_share | 10.569% | 10.569% |
| median_min_visible | 100.000% | 100.000% |
| frame_black_mean | 36.642% | 21.988% |
| frame_black_p95 | 65.258% | 36.768% |
| frame_black_max | 71.456% | 52.273% |
| records | 5689 | 5923 |
| expanded_records | 29009 | 29243 |

At step 128, frame black mean / p95 / max changes from 34.608% / 61.279% / 78.753% to 22.961% / 42.230% / 66.079%. Map-wide visibility remains 14.715% below half and 7.089% hidden at step 128. The 256-unit visibility pins remain 14.228% and 10.569%; frame pins use the baseline 512-unit fallback. All improved pins were lowered; only the two record-count pins rose, within the 6,500 raw and 31,000 expanded ceilings.

The physical-record multiset is identical. Exact-reach set equality holds for 15,758 shelf cells and 60,164 door-component cells, with zero lost or gained cells at any level (`m08/geometry.json`). The pin comparison is in `m08/pin-ratchet.json`. Every pristine raw record outside `BASE_ITEM_REMOVALS` survives byte-identically. Only Map 08’s archive records changed. No new shape ID was added.

The outstanding 79 cells are all on `shelf-2`, x 29727..30431, y 25279..26367, z 56 (`m08/leg-debt.json`). Sampled occluders include retained 26:8 near-wall courses at (29951/30079/30207,26271,56/104). Their repair needs a further approved retail-wall pass along that leg, beyond the named second-seam jamb treatment in §4.8. D1 retains retail walls, so those courses remain in this slice. A visibility-only counterfactual omitting 12 upper second-seam wall records reduces 79 below-half cells to 61 (`m08/one-course-counterfactual.json`); adjacent drawn base courses still fail the half-visible rule. No new wall-adjacency allowance or zero-course treatment was approved. This report does not invent an occlusion allowance. `test_visual_quality.py 8` passes its measured ratchets; strict phase exit remains blocked by those 79 cells.

## Verification and review

- `tools/build_artifacts.sh --record`: passed. Only FIXED changed; the other four canonical hashes match the baseline.
- `test_map08_backdrop.py`: 10 tests passed, including opaque repaint, pristine-record preservation, seam visibility and frame bounds, and record ceilings.
- `tools/run_all_tests.sh`: 56 of 57 test files passed. The sole failure is the permitted `test_integration_state.py`: the symlinked main install’s `STATIC/FIXED.DAT` differs from this branch’s canonical FIXED. The private harness matches all six checked locations. Three local engine-tree checks were skipped. Full output: `m08/estate.txt`.
- `codex exec review --base main`: the sandbox could not enter its namespace (`Failed RTM_NEWADDR: Operation not permitted`). The unrestricted rerun found one P1 stale-hash finding, resolved by the completed artifact rebuild. The follow-up unrestricted review found no actionable regressions and independently passed the 10 backdrop tests, visual-quality ratchets, and builder-to-archive record comparison.
- Shot scores: all 39 `test_vignettes.py` checks passed. The 19 window scores and unpainted allowances are in `m08/vignettes.txt`; Map 08 has no window. All 62 captures passed metadata, landing, image-size, health, pause-menu, artifact-hash, and display validation (`m08/capture-validation.json`). After the final Map 08 arrival in each session, cycle warnings and nonexistent-process warnings are both zero. Full-session startup logs contain 90 before and 93 after nonexistent-process warnings during the inherited introduction. The m08-05/06 aperture witness pixels are black; final engine frame black is 20.596% and 51.094%, within the 20.82% and 51.28% bounds. The model counts uncovered pixels as black, so the repaint repairs opacity while leaving its frame-black measure unchanged (`m08/aperture-repaint.json`).

Canonical SHA-256 hashes:

```text
ac0b33486fc167d98c07c32011de348c11ae0cefb8d89fc2597ef984133a5fd1  TYPEFLAG.DAT
aad6ed7b8961f416b6fae225d467427899a4487db768b6fb486ed5b5cb3e73ba  U8SHAPES.FLX
97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443  ANIM.DAT
b47c324cdad77646c27755acfdd5bca53a9d92e16268db229f18e7dd780d4205  EUSECODE.FLX
b5cb9a419a4de9e9bf376d629cdba31902c3e0ad8d5f4fd136dcd5806aafd801  FIXED.DAT
```

## Remaining work and boundaries

- VQ-003 repaints the aperture. The retained shelf and grey fleck stay retail; Astra’s final visual grade remains outstanding.
- VQ-004 and VQ-008 improve paint and jamb continuity; Astra’s final grade remains outstanding.
- D1 intentionally retains VQ-018/022/023/030/031. D2 intentionally retains off-route VQ-044/060/064 and the remaining VQ-046 retail witnesses.
- The 79-cell leg debt remains measured and unweakened. The main-checkout verifier walk and Astra grading remain with the merge owner. No shared source or shared acceptance test changed.
- The private worktree, game-data symlinks, baseline runtime copy, and rebuilt hash and pin inventories support the requested isolation. The main checkout’s pre-existing status is unchanged. No merge, push, or main-checkout edit occurred.

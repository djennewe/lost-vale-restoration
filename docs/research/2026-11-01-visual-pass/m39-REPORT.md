# Map 39 phases 2 and 3

The ground beyond Tenebrae's oaks and the harbour channel now paints the visible void. The tunnel has three fewer failing leg cells; VQ-021 remains incomplete because the remaining occluders are adjacent retail content outside the authorised cut. This is an improvement slice with explicit remaining phase-exit debt.

Branch: `wt/vq2-m39`, based on `ba34836`. Phase 2 commit: `e9f3964`. Phase 3 commit: `aa4f511`. Evidence date: 3 November 2026, America/Chicago. The phase 2 step-128 audit finished before phase 3 implementation began.

## VQ-021: tunnel occlusion

Cause: the glob's flat roof pieces, upper masonry, and added east flank paint over the actor. The permitted south cut ends at x=16255. A course at `(16383,19967,96)` occupies x=16256..16383 and still covers the tunnel from this camera. The city-side view also sees a neighbouring roof at `(16639,19711,136)` beyond the replaced glob.

Change: eight flat roof pieces become matching 499/763 support plates with projected 894/895 underpaint at z=0. At x=16127 and 16255, each lintel of 8 units and upper course of 40 units becomes one 497 at z=88, retaining its top at 136. The added east flank uses paired 498 pieces at z=48 and 88. Decorative underpaint supplies no support. The adjacent x=16383 course and lintel retain their original records.

Baseline to phase 2:

| Stop | Walkable black | Frame black | Minimum visible |
|---|---:|---:|---:|
| m39-02 | 0 → 0 | 2.04% → 2.05% | 0.00% → 0.00% |
| m39-03 | 0 → 0 | 11.99% → 12.00% | 0.00% → 0.00% |

The unscoped experiment at x=16383 raised m39-03's minimum visibility to 57.65%. The verifier found that course outside the cut, and it was restored before the phase 2 commit. The shipped result keeps m39-03 at 0%. Completion requires broader retail scope for the adjacent course and neighbouring roof. No occlusion allowance was added.

The wall underpaint left nine newly black pixels at m39-03 during phase 2. Its mean-frame pin stayed frozen, and the phase 3 ground pass reduced the frame mean below that pin. The initial phase 2 visual run also printed record-pin failures before the authorised count adjustments.

## VQ-040: ground beyond the treeline

Cause: the retail grass ends at the oak barrier. The 274 accepted void plates paint the ground beyond it black.

Change: the initial accepted plates identify 76 chunks. 68 chunks use retail grass glob one at z=48. The two harbour columns use 64 individual grass tiles to preserve the lower channel and quay. The original oaks close the skirt from the playable field, so the existing barriers suffice. Every original black plate disappears; 52 new plates cover the skirt's outer view ring. The extended forest and moat-bank dressing remain phase 4 work.

Phase 2 to phase 3:

| Stop | Walkable black | Frame black | Minimum visible |
|---|---:|---:|---:|
| m39-03 | 0 → 0 | 12.00% → 0.55% | 0.00% → 0.00% |
| m39-05 | 0 → 0 | 21.49% → 0.43% | 61.59% → 61.59% |
| m39-06 | 0 → 0 | 21.87% → 0.29% | 92.85% → 92.85% |
| m39-07 | 0 → 0 | 11.93% → 0.48% | 100.00% → 100.00% |
| m39-08 | 0 → 0 | 23.24% → 0.15% | 81.81% → 81.81% |
| m39-09 | 0 → 0 | 31.25% → 0.07% | 86.24% → 86.24% |
| m39-10 | 0 → 0 | 34.77% → 0.01% | 90.45% → 90.45% |
| m39-11 | 0 → 0 | 23.00% → 0.74% | 96.88% → 96.88% |

Status: improved. Every cited frame improves, while the map's unrelated retail edges retain their phase-exit debt.

## VQ-059: harbour south end

Cause: the south wall's free faces and the channel end previously met unpainted ground.

Change: 42 retail 347:16 water tiles continue the channel at its existing z=0, with max corners x=13695..13951 and y=20639..22303. 18 decorative 894 pieces paint the quay strip and the south wall's foot. These backdrops have no LAND, SOLID, SEA, OCCL, or ROOF flags. They add no standing level.

Phase 2 to phase 3:

| Stop | Walkable black | Frame black | Minimum visible |
|---|---:|---:|---:|
| m39-04 | 0 → 0 | 13.66% → 0.44% | 100.00% → 100.00% |

Status: improved. The final south-edge test retains exactly 7,709 retail void exits and finds zero exposure near the lane.

## VQ-055: retained retail canal

Douglas's answer D9 retains the main-gate canal. Its retail records and geometry are unchanged. The whole-frame numbers below improve because the skirt paints other visible regions.

Baseline to phase 3:

| Stop | Walkable black | Frame black | Minimum visible |
|---|---:|---:|---:|
| m39-02 | 0 → 0 | 2.04% → 0.67% | 0.00% → 0.00% |
| m39-07 | 0 → 0 | 11.93% → 0.48% | 100.00% → 100.00% |
| m39-12 | 0 → 0 | 5.72% → 0.54% | 100.00% → 100.00% |

Status: retained by D9, outside the implementation work.

## Geometry and leg measurements

Both constraints files and the compressed [reach arrays](m39/reachability.npz) show 177,351 reached cells, zero added cells, and zero removed cells on the 32-unit lattice. The verifier also compared solid occupancy on the tunnel's finer boundary partitions and found zero changed regions. All 4,623 pristine retail records outside the removed glob remain as the raw prefix. Every other map slot is byte-identical. The egg at `(17150,19700,48)` q304, the apparition, and the oak line retain their positions.

| Band | Cells | Before below 50% | Phase 2 | Phase 3 |
|---|---:|---:|---:|---:|
| town-1 | 1162 | 319 | 319 | 319 |
| town-2 | 904 | 119 | 116 | 116 |
| Unique union | 1957 | 437 | 434 | 434 |
| Tunnel subset | 24 | 22 | 19 | 19 |

The two bands overlap, so their counts do not add to the unique union. Minimum visibility remains 0% on both full bands. The tunnel subset improves from 22 to 19 cells below 50%, out of 24; it does not meet the zero-cell exit target.

Evidence: [phase 2 constraints](m39/phase2-constraints.json), [final constraints](m39/after-constraints.json), and the [before](m39/before-legs.json), [phase 2](m39/phase2-legs.json), and [after](m39/after-legs.json) leg tables.

## Map measurements, windows, and budgets

Specified walkable black stays zero. 14 prop-pixel black probes remain. Stop tables measure floor paint separately from foreground cover; frame black counts pure-black and unpainted pixels in a 640 by 400 frame of 256,000 pixels. Minimum visibility is the fraction of a pose's opaque pixels still visible, taking the worst of 72 walking and standing poses. The step-128 rows use 10,430 cameras: 1,325 samples remain below half visible, while fully hidden samples fall from 635 to 634.

| Step-128 metric | Before | Phase 2 | Phase 3 |
|---|---:|---:|---:|
| Frame mean | 7.03% | 7.03% | 6.70% |
| Frame p95 | 39.05% | 39.05% | 39.04% |
| Frame maximum | 75.80% | 75.80% | 75.80% |
| Cells below 50% | 12.70% | 12.70% | 12.70% |
| Completely hidden | 6.09% | 6.08% | 6.08% |
| Raw records | 5108 | 5115 | 5085 |
| Expanded items | 29068 | 29075 | 30065 |

The permanent test uses 2,373 visibility samples at 256 units and 455 frame samples at 512 units. Its final mean is 8.49%, p95 is 47.00%, maximum is 63.06%, and leg-cell pin is 434. Every improved pin is lowered; unchanged pins retain their previous ceilings. Expansion rises within the authorised 31,000 ceiling. Step-128 values and their current artifact hashes are recorded separately in `visual_pins/map39.json`.

The record inventory removes 274 records and adds 244: 68 glob eggs, 64 grass tiles, 42 water tiles, 18 decorative backdrops, and 52 outer cover plates. Raw headroom is 915 below the 6,000 exit ceiling. Expanded headroom is 935 below the 31,000 budget and 2,435 below the object-ID cap. [Record inventory](m39/phase3-records.json).

Map 39 has no 1994 screenshot window. All 19 windows are on unchanged map slots and use unchanged art, so their pixels and scores remain identical. The full estate's `test_vignettes.py` supplies the floor checks; [all measured scores](m39/window-scores.json) and the [detailed log](m39/test_vignettes.log) are preserved.

The step-128 mean now meets 7%; p95 remains 39.04% against 38%, maximum remains 75.80% against 62%, and the hidden share remains 6.08% against 6%. The worst frame is retail at `(7839,17439,48)`, far outside the permitted LV additions. The normal ratchet passes; strict phase exit remains incomplete.

## Captures and provenance

Every capture uses `LV_DISPLAY=:67`, `XDG_RUNTIME_DIR=/tmp/claude-1000/vq2-m39`, `usehighres=false`, and a fresh world. ScummVM runs through `tour_capture.py`. A wrapper increases settle time to 45 seconds and retries a missing position reply; unsuccessful stops are rerun in fresh worlds. Frozen private baseline and phase 2 copies keep their artifacts stable while final builds proceed. Final capture metadata also compares installed artifact hashes with build hashes.

| State | Landed at requested map and z | Paint cycles | Process warnings |
|---|---:|---:|---:|
| before | 11/11 | 0 in 3 logs | 9 in 3 logs |
| phase2 | 11/11 | 0 in 11 logs | 33 in 11 logs |
| after | 11/11 | 0 in 11 logs | 35 in 11 logs |

The baseline controls already emit process warnings. Final logs contain 35 process warnings, compared with 33 in phase 2, including bootstrap and retail NPC activity; the extra two were not isolated in this map-only slice. The zero-process-warning goal is unmet. Diagnosing or changing the shared usecode and capture bootstrap remains outside this slice. No paint cycles occur in the logged phase 2 and final captures. A traversal in the engine was not added; exact route tests and the mandated fresh-world stop captures provide the route evidence.

The final validator confirms exact requested map, x, y, and z for all 33 captures, and matching installed and build hashes for all 11 final stops. Every cited engine frame also has fewer pure-black pixels than its baseline and phase 2 counterpart. [Final validation](m39/final-verification.json).

| Stop | Engine black before | Phase 2 | Phase 3 |
|---|---:|---:|---:|
| m39-02 | 0.88% | 1.11% | 0.66% |
| m39-03 | 8.38% | 7.25% | 0.54% |
| m39-04 | 10.39% | 10.38% | 0.25% |
| m39-05 | 14.26% | 14.26% | 0.46% |
| m39-06 | 14.29% | 14.28% | 0.33% |
| m39-07 | 7.59% | 7.79% | 0.56% |
| m39-08 | 15.37% | 15.38% | 0.21% |
| m39-09 | 19.86% | 19.83% | 0.13% |
| m39-10 | 23.76% | 23.83% | 0.07% |
| m39-11 | 13.04% | 12.75% | 0.19% |
| m39-12 | 2.65% | 2.51% | 0.60% |

The first baseline void audit loaded the original map but recorded a later hash when writing provenance. It was replayed against the frozen baseline archive. The saved replay carries the original hash and reproduces the baseline measurements. The early baseline frames m39-03 and m39-05 were repeated against that frozen copy. Visual review also rejected a Pagan-intro image at m39-08 despite its successful landing record; a fresh capture replaced it. All 33 final images were reviewed as world scenes without intro or modal overlays.

| Stop | Baseline | Phase 2, also phase 3 baseline | Phase 3 |
|---|---|---|---|
| m39-02 | [Image](m39/before/m39-02.png) | [Image](m39/phase2/m39-02.png) | [Image](m39/after/m39-02.png) |
| m39-03 | [Image](m39/before/m39-03.png) | [Image](m39/phase2/m39-03.png) | [Image](m39/after/m39-03.png) |
| m39-04 | [Image](m39/before/m39-04.png) | [Image](m39/phase2/m39-04.png) | [Image](m39/after/m39-04.png) |
| m39-05 | [Image](m39/before/m39-05.png) | [Image](m39/phase2/m39-05.png) | [Image](m39/after/m39-05.png) |
| m39-06 | [Image](m39/before/m39-06.png) | [Image](m39/phase2/m39-06.png) | [Image](m39/after/m39-06.png) |
| m39-07 | [Image](m39/before/m39-07.png) | [Image](m39/phase2/m39-07.png) | [Image](m39/after/m39-07.png) |
| m39-08 | [Image](m39/before/m39-08.png) | [Image](m39/phase2/m39-08.png) | [Image](m39/after/m39-08.png) |
| m39-09 | [Image](m39/before/m39-09.png) | [Image](m39/phase2/m39-09.png) | [Image](m39/after/m39-09.png) |
| m39-10 | [Image](m39/before/m39-10.png) | [Image](m39/phase2/m39-10.png) | [Image](m39/after/m39-10.png) |
| m39-11 | [Image](m39/before/m39-11.png) | [Image](m39/phase2/m39-11.png) | [Image](m39/after/m39-11.png) |
| m39-12 | [Image](m39/before/m39-12.png) | [Image](m39/phase2/m39-12.png) | [Image](m39/after/m39-12.png) |

Landing records: [before](m39/before/captures.json), [phase 2](m39/phase2/captures.json), and [after](m39/after/captures.json). Audit summaries: [before](m39/before-audit/void-map39-summary.json), [phase 2](m39/phase2-audit-final/void-map39-summary.json), and [after](m39/after-audit/void-map39-summary.json). Large raw audit JSON and ranked tables are compressed for the committed evidence.

## Build, estate, and review

`tools/build_artifacts.sh --record`: PASS. The full rebuild reproduces FIXED `d42949fa048bd5f91a3dde256a36287575ed23cd93dc9a23ad12c06942b8855a`, with a final map-validation summary of zero warnings and zero errors. The quest-step placement pre-check retains two warnings for the unchanged retail shape-174 and apparition placements. Compilation processes 57 files: 55 succeed, and the two failures are the existing EALOGO and TJORVI allowlist pair. `derive_map_pins.py` regenerates the pin inventory.

`tools/run_all_tests.sh`: 56/57 test files pass. The sole failure is the explicitly allowed `test_integration_state.py`: the symlinked install target has `STATIC/FIXED.DAT != canonical FIXED.DAT`. The private capture harness passes its six canonical-byte checks. The shared install remains untouched. [Failure detail](m39/test_integration_state.log).

`test_visual_quality.py 39 --record`: PASS, zero failures. `test_map39_lane.py`: nine passes. `test_map39_south_edge.py`: 19 passes, including exactly 7,709 retail void exits. The masked-tunnel negative control, water clearance, oak climb checks, and stale-frame coverage checks remain in force.

The required `codex exec review --base main` initially failed to inspect the checkout because bubblewrap could not create its network namespace. Rerunning with `-c 'sandbox_mode="danger-full-access"'` completed and found no actionable regressions. Its independent lane, edge, and visual-quality checks passed. The high-effort verifier independently confirmed retail preservation, exact reach equality, solid occupancy, shape flags, and record budgets. Its verdict retains the VQ-021 and phase-exit limitations.

A discarded invisible-item experiment exposed a shared-model defect: `exact_reach.py` calls 0x0010 equipped, while the engine uses that bit for invisible items and uses 0x0200 for equipped items. That approach lost modelled collisions and was discarded. The shipped native 497/498 replacements avoid that defect. A future invisible-item change needs a shared-model correction and tests; this slice leaves the prohibited shared module unchanged.

Evidence: [build](m39/build.log), [hash checks](m39/hashes.log), [estate](m39/tests.log), [review](m39/review.log), and [initial sandbox failure](m39/review-sandbox.log).

## Artifact hashes and remaining work

| FIXED state | SHA-256 |
|---|---|
| Before | `89da4e165833bff0b4da526cfa2cbc434336f6816e3964ae9982bd804a2eb767` |
| Phase 2 | `ff322f034a6c5c1d8f9a35d97daeb53827d449eceec11baa32df17e12316bf70` |
| Phase 3 | `d42949fa048bd5f91a3dde256a36287575ed23cd93dc9a23ad12c06942b8855a` |

The other four artifacts retain their baseline hashes:

```text
ac0b33486fc167d98c07c32011de348c11ae0cefb8d89fc2597ef984133a5fd1  TYPEFLAG.DAT
aad6ed7b8961f416b6fae225d467427899a4487db768b6fb486ed5b5cb3e73ba  U8SHAPES.FLX
97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443  ANIM.DAT
b47c324cdad77646c27755acfdd5bca53a9d92e16268db229f18e7dd780d4205  EUSECODE.FLX
```

VQ-021 remains blocked at the named views by adjacent retail geometry outside the cut. VQ-040 and VQ-059 improve at every cited stop. VQ-055 remains retail by D9. Broader retail work is required for the outstanding frame and visibility class limits; no additional sign-off box was invented. Astra's visual grading and merge integration remain with the orchestrator.

The branch is unmerged and unpushed. Main's pre-existing user changes remain untouched. Game-data symlinks remain untracked setup entries; built artifacts and installed game copies stay private. `TODO.md` is left for merge integration because the slice's permitted file list excludes it.

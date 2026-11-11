# Map 17b: quest-leg visibility

Branch: `wt/vq2-m17b`, based on `d9dea9e`.

Quest-leg cells below half visibility fell from 46 to zero. All 2,228 cells of the revised quest band pass, with a minimum of 52.56% over 72 poses. `test_visual_quality.py 17 --strict` passes with zero failures. Both 1994 windows are pixel-identical.

## Quest-leg occlusion

Status: fixed. White columns (875), gem caps (880), and the obelisk composite (12, 545, 814) painted over the Avatar. Marble slab rims (877) and throne furniture (526) contributed at some cells. A single 40-unit drum already covers more than half of an adjacent pose. The original audit found 46 distinct failing quest-band cells, including completely hidden poses beside the obelisk.

T2 recesses keep the deterministic walking bands clear of these shadows. The builder adds 1,331 deduplicated invisible-wall records, including the additional posts encountered by the revised shortest paths. Column recesses reach 192; the obelisk recess reaches 240. Their tops exceed the neighbouring 88-unit posts and 128-unit obelisk structure by more than climb72. All 7,953 original records remain unchanged, including every drawn item, all 400 perimeter curbs, the Shield halves, the scroll, plaques, teleport eggs, and reapply egg.

The recesses remove exactly 1,340 body-overlap positions from the original 62,424-cell dry flood, leaving 61,084. No other cells are lost, no cells are added, and `walk_off` finds zero falls before and after. The expected footprint delta and every removed coordinate are recorded in `m17b/geometry.json`. The other 255 raw FIXED archive entries are byte-identical.

The cell-by-cell cause and disposition are listed below and in `m17b/quest-cell-disposition.json`. Every original failing cell is physically excluded by a recess. The sprites at those coordinates retain their original visibility; the new quest bands follow clear ground.

| Leg | Band cells, before → after | Below half, before → after | Minimum visible %, before → after |
|---|---:|---:|---:|
| cloud-1 | 290 → 276 | 13 → 0 | 35.09 → 52.56 |
| cloud-2 | 428 → 478 | 19 → 0 | 0.00 → 52.56 |
| cloud-3 | 176 → 175 | 0 → 0 | 53.37 → 59.64 |
| cloud-4 | 263 → 239 | 7 → 0 | 36.30 → 52.86 |
| cloud-5 | 566 → 546 | 4 → 0 | 36.45 → 52.86 |
| cloud-6 | 582 → 579 | 3 → 0 | 35.09 → 70.48 |

Overlapping leg bands share cells; the distinct-cell total changes from 2,245 to 2,228. Full per-cell pose minima are preserved in the compressed leg-cell JSON files. The [before band heatmap](m17b/before-audit/map17-legs.png) and [after band heatmap](m17b/phase2-pins/map17-legs.png) show the route changes beneath the preserved artwork.

## Engine stops

These are camera witnesses on ground reachable in both builds. The two original shot stops are retained. Each floor entry is a black floor probe out of one; frame and visibility values come from the built-scene audits. All drawn content stays unchanged, so the witness values stay unchanged. Stop m17b-08 remains an off-band visibility failure; the quest-leg standard applies to the revised band.

| Stop | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| m17b-01 | 0 → 0 | 0.487 → 0.487 | 100.00 → 100.00 |
| m17b-02 | 0 → 0 | 0.519 → 0.519 | 91.56 → 91.56 |
| m17b-03 | 0 → 0 | 0.355 → 0.355 | 100.00 → 100.00 |
| m17b-04 | 0 → 0 | 0.251 → 0.251 | 100.00 → 100.00 |
| m17b-05 | 0 → 0 | 0.198 → 0.198 | 70.85 → 70.85 |
| m17b-06 | 0 → 0 | 0.263 → 0.263 | 95.11 → 95.11 |
| m17b-07 | 0 → 0 | 0.602 → 0.602 | 100.00 → 100.00 |
| m17b-08 | 0 → 0 | 0.261 → 0.261 | 35.84 → 35.84 |
| m17b-09 | 0 → 0 | 0.291 → 0.291 | 100.00 → 100.00 |
| m17b-10 | 0 → 0 | 0.341 → 0.341 | 100.00 → 100.00 |
| m17b-11 | 0 → 0 | 0.362 → 0.362 | 100.00 → 100.00 |
| m17b-12 | 0 → 0 | 0.143 → 0.143 | 100.00 → 100.00 |
| m17-03 | 0 → 0 | 0.271 → 0.271 | 100.00 → 100.00 |
| m17-05 | 0 → 0 | 0.497 → 0.497 | 98.10 → 98.10 |

Engine captures use `LV_DISPLAY=:72`, `XDG_RUNTIME_DIR=/tmp/claude-1000/vq2-m17b`, a private `usehighres=false` configuration, and a fresh world for every stop. Baseline scripts, artifacts, and the installed game were frozen privately before the first build. After captures use the worktree artifacts. The capture adapter invokes the unchanged `tour_capture.py`, retains its fresh-world launch and surface crop, sends debugger commands once, and checks title and menu overlays. Repository capture helpers remain unchanged. `capture-provenance.json` records script and artifact hashes and the exact launcher configuration.

All 14 before captures and all 14 after captures are accepted: `landed: true`, exact requested coordinates, 640×400 surfaces, and zero title or menu overlays. All 28 logs are retained. Each phase records 42 inherited startup process warnings on Map 0 and zero Map 17 paint-cycle or process warnings. The summary JSON files record each image hash and measured screenshot black share. The final after runner freezes its own scripts, artifacts, and installed game, so the verifier rebuild cannot change the bytes used by a fresh capture.

## Windows, records, and pins

| Window | Class score %, before → after | Unpainted pixels, before → after | Changed pixels | Floor |
|---|---:|---:|---:|---:|
| screen11 | 99.929324 → 99.929324 | 0 → 0 | 0 | 99.93 |
| screen12 | 97.942896 → 97.942896 | 0 → 0 | 0 | 97.94 |

Both window floors hold with the existing 0.25-point slack. No screenshot compromise or occlusion allowance is needed.

| Measurement | Before | After |
|---|---:|---:|
| Raw and expanded records | 7,953 | 9,284 |
| Phase 2 and 3 exit ceiling | 10,500 | 10,500 |
| Specified-black reached cells | 0 | 0 |
| Prop-black reached cells | 19 | 16 |
| Quest-band cells below half | 46 | 0 |
| Permanent sampled cells below half | 18 / 913 (1.9715%) | 15 / 902 (1.6630%) |
| Permanent sampled cells fully hidden | 1 / 913 (0.1095%) | 0 / 902 (0%) |
| Permanent frame mean, p95, max | 2.0816%, 8.5914%, 29.6414% | 2.0816%, 8.5914%, 29.6414% |
| Step-128 sampled cells | 3,728 | 3,640 |
| Step-128 cells below half | 43 | 30 |
| Step-128 cells fully hidden | 2 | 0 |
| Step-128 frame mean, p95, max | 2.2007%, 17.4427%, 44.7773% | 2.2470%, 17.4531%, 44.7773% |

Every improved acceptance pin was lowered. Record pins rose within the exit ceiling. Every other acceptance pin stays unchanged or falls; no allowance was added. `report_step128` records the current audit distributions. Removing interior cameras raises its frame mean and percentile slightly through the changed sample population; painted frames at surviving positions remain identical. The permanent frame acceptance pins remain unchanged.

## Phase sequence and verification

Phase 2 implementation: `d2d1b9f`. Its complete before and after audits, strict check, interaction review, estate, canonical rebuild, and fresh-world captures completed before phase 3 began.

Phase 3 repeats both step-128 audits and `test_visual_quality.py 17 --strict` after the phase 2 commit. All measured metrics and all five artifact hashes match the phase 2 exit exactly; `phase-comparison.json` records the comparison. No floor change is needed: specified-black debt is zero, and editor walls paint no pixels. The accepted after tour uses the same artifact hash and supplies engine evidence for both final phase states.

`tools/build_artifacts.sh --record` passed, retaining the EALOGO and TJORVI compiler allowlist pair. `derive_map_pins.py` changed only the FIXED hash prefix. The final phase 2 and phase 3 strict Map 17 visual tests both passed with zero failures. The full estate passed 56 of 57 files. The sole failure is the permitted `test_integration_state` worktree exception: the symlinked install target holds different FIXED bytes. Its other 10 assertions passed, and three absent worktree-engine checks skipped. The private capture harness holds canonical bytes. The final eight-map permanent visual test passed in 86.951 seconds. The verifier rebuilt after the estate and confirmed all five canonical hashes. The [verifier report](m17b/verifier-REPORT.md) records its precommit pass and complete limits.

## Review findings

The mandatory verifier identified two carryable-footprint intersections in the first recess candidate. The sun-half recess was removed, and the throne-side recess moved eight units east, placing its western face exactly at the eye half's maximum x. Both full 32×96×24 Shield boxes are now clear. A four-cell disconnected pocket disappeared with that correction. A potential jump onto an invisible 96-unit top was addressed by raising column backstops to 192 and the obelisk backstop to 240.

A broader prop scan also found the movable skull (814) and prop 471 intersecting recess solids. The obelisk's front ground strip is now omitted, clearing the skull and fixed drum completely. The gem-pillar recess ends at x4255, exactly clear of prop 471's western edge. Their art stays in place. The retained z48 blocker above the drum prevents standing on the drum or skull top. Two movable bone containers (235) also need their full 96×128×8 boxes clear. Six backstop strips now start at z8, exactly above those boxes. These strips still block the 40-unit Avatar after a container is removed, and overlap the next course at z48, closing their z56 tops. The complete scan of all 26 movable items now finds zero new solid intersections.

The verifier's independent static `Item::canReach` model finds a clear approach to each of the 26 movable items and the fixed obelisk front drum. Representative positions are `(4223,7199,0)`, `(3519,3295,0)`, and `(4127,7263,0)`. Restoring the rejected sun-half recess blocks all three test rays in the negative control. This models full built footpads, 128-unit interaction range, and the engine's three 2×2×2 sight rays. Actual in-engine inventory pickup was not exercised. The obelisk's MAGNET wiring remains deferred; its south face retains a clear approach and remains clear of the added solids.

`codex exec review --base main` encountered the local bubblewrap user-namespace failure. Re-running with `-c 'sandbox_mode="danger-full-access"'` completed with no actionable defects. The reviewer independently passed route reachability, map-pin freshness, map round-trip, and hygiene checks, and confirmed generated records and the recorded artifact hash. Logs retain both attempts. The final review of the settled prop clearances also found no actionable defects and independently passed strict visual checks, pin freshness, route reachability, and hygiene. Generated records match the built artifact and its manifest hash.

## Artifact hashes

The baseline FIXED hash is `441472b72708812cdea308c3e1245f091775e84b12105eaf78841467ad013b34`. Final hashes:

```text
ac0b33486fc167d98c07c32011de348c11ae0cefb8d89fc2597ef984133a5fd1  TYPEFLAG.DAT
aad6ed7b8961f416b6fae225d467427899a4487db768b6fb486ed5b5cb3e73ba  U8SHAPES.FLX
97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443  ANIM.DAT
b47c324cdad77646c27755acfdd5bca53a9d92e16268db229f18e7dd780d4205  EUSECODE.FLX
abd14635501999361122b176321f4655603cf4b109c259fc4cfeded5063ac648  FIXED.DAT
```

## Remaining work and scope

- Quest-leg visibility: fixed, 46 → 0, without an occlusion allowance.
- Phase 3 floor debt: zero; no further floor implementation is required.
- VQ-047 north and west coordinate-limit pixels remain inherited from the merged Map 17 slice. Its optional 20% maximum target remains outside this item.

Only the Map 17 builder, its visual pins, regenerated map pins and artifact hashes, this report, and its evidence are changed. No shared module, retail record, pinned-item position, or shape ID changed. Game data entries are symlinks; build artifacts and capture installations are private copies. No merge or push occurred. The main checkout has no changes attributable to this branch. Concurrent main activity is recorded in `main-isolation.json`. The five setup data symlinks remain untracked and excluded from the commits.

## Original failing cells

The primary occluder is the final pixel owner covering the largest part of the worst pose. The JSON evidence also retains every secondary owner and its pixel count. Every row below becomes unreachable inside the explicit recess footprint.

| Cell (x, y, z) | Before min visible % | Primary shape:frame at (x, y, z) |
|---|---:|---|
| (2271, 2911, 0) | 36.446 | 875:1 at (2335, 2975, 8) |
| (2271, 2943, 0) | 40.162 | 875:1 at (2335, 2975, 8) |
| (2271, 3071, 8) | 36.446 | 875:1 at (2303, 3103, 8) |
| (2271, 3103, 8) | 46.166 | 875:1 at (2303, 3103, 8) |
| (2271, 3391, 0) | 36.446 | 875:1 at (2335, 3455, 8) |
| (2271, 3423, 0) | 40.162 | 875:1 at (2335, 3455, 8) |
| (2271, 3551, 8) | 36.446 | 875:1 at (2303, 3583, 8) |
| (2271, 3583, 8) | 46.166 | 875:1 at (2303, 3583, 8) |
| (2815, 1503, 0) | 48.248 | 875:0 at (2879, 1535, 0) |
| (2847, 1503, 0) | 36.295 | 875:0 at (2879, 1535, 0) |
| (2879, 1503, 0) | 41.704 | 875:0 at (2879, 1535, 0) |
| (3359, 6399, 0) | 41.704 | 875:0 at (3359, 6431, 0) |
| (3391, 3391, 0) | 36.446 | 875:1 at (3423, 3423, 0) |
| (3391, 3423, 0) | 40.162 | 875:1 at (3423, 3423, 0) |
| (3423, 3391, 0) | 42.003 | 875:1 at (3423, 3423, 0) |
| (3839, 7135, 0) | 36.446 | 875:0 at (3871, 7167, 0) |
| (3871, 7135, 0) | 41.704 | 875:0 at (3871, 7167, 0) |
| (3935, 7071, 0) | 44.888 | 12:17 at (4095, 7199, 40) |
| (3967, 7071, 0) | 0.799 | 12:17 at (4095, 7199, 40) |
| (3967, 7103, 0) | 37.952 | 12:17 at (4095, 7199, 40) |
| (3999, 7071, 0) | 0.000 | 12:17 at (4095, 7199, 40) |
| (3999, 7103, 0) | 0.000 | 12:17 at (4095, 7199, 40) |
| (3999, 7135, 0) | 26.657 | 875:1 at (4063, 7199, 0) |
| (4031, 7071, 0) | 0.149 | 12:16 at (4127, 7167, 40) |
| (4031, 7103, 0) | 0.000 | 12:17 at (4095, 7199, 40) |
| (4031, 7135, 0) | 0.301 | 12:17 at (4095, 7199, 40) |
| (4063, 7071, 0) | 21.973 | 12:16 at (4127, 7167, 40) |
| (4063, 7103, 0) | 0.299 | 12:16 at (4127, 7167, 40) |
| (4095, 7103, 0) | 13.752 | 875:1 at (4127, 7135, 0) |
| (4127, 7103, 0) | 41.106 | 875:1 at (4127, 7135, 0) |
| (4159, 7903, 0) | 41.704 | 875:0 at (4159, 7935, 0) |
| (4255, 8159, 0) | 35.090 | 875:0 at (4287, 8191, 0) |
| (4255, 8191, 0) | 43.930 | 875:0 at (4287, 8191, 0) |
| (4255, 8415, 0) | 35.090 | 875:0 at (4287, 8447, 0) |
| (4255, 8447, 0) | 43.930 | 875:0 at (4287, 8447, 0) |
| (4255, 8671, 0) | 35.843 | 875:0 at (4287, 8703, 0) |
| (4255, 8703, 0) | 44.569 | 875:0 at (4287, 8703, 0) |
| (4255, 8927, 0) | 35.843 | 875:0 at (4287, 8959, 0) |
| (4255, 8959, 0) | 44.569 | 875:0 at (4287, 8959, 0) |
| (4255, 9183, 0) | 35.090 | 875:0 at (4287, 9215, 0) |
| (4255, 9215, 0) | 43.930 | 875:0 at (4287, 9215, 0) |
| (4255, 9439, 0) | 36.446 | 875:0 at (4287, 9471, 0) |
| (4255, 9471, 0) | 45.208 | 875:0 at (4287, 9471, 0) |
| (5855, 6111, 0) | 35.090 | 875:0 at (5887, 6143, 0) |
| (5855, 6143, 0) | 43.930 | 875:0 at (5887, 6143, 0) |
| (5887, 6111, 0) | 40.359 | 875:0 at (5887, 6143, 0) |

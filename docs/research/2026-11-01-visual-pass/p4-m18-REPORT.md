# Map 18 phase four dressing

Map 18 has zero regional target failures and zero strict dressing failures. Each region has a hand-authored set piece protected by `site.set_piece`. The specified paving, plinth, bones, low rubble, and continuous crest work includes substitutions and stopped items below.

Branch: `wt/vq4-m18`. Starting main tip: `4d3d514`. Main advanced with coordination documents while this work ran; this branch keeps its original base. No merge or push occurred.

## Metrics and preservation

The built artifact supplies every measurement. Proportions below use each region's 128-unit ground cells. The regional targets skip repetition limits below 400 cells; the existing repetition ratchets still apply. Both baseline and final metric JSON files are in [p4-m18](p4-m18/).

## Exterior

Reads as: A forecourt under the cliff.

Rough flat 71 paving surrounds a flagstone approach. Two gargoyles, 38 frames 0 and 1, flank the existing gate at (2783,895,0) and (3423,895,0). Three explicit debris fans follow the court margins. Two cliff courses of 26 and 32 and a single 125 crest back the north and west masonry. The south and east surroundings are dark.

Set piece: **gate wardens**, [640 by 400 capture](p4-m18/setpieces/m18-sp-gate-wardens.png). All pieces and the peripheral debris use explicit coordinates inside `site.set_piece`.

Claimed: VQ-137, the court reading as another hall. Shape 70 is substituted by flat shape 71 to preserve the floor's standing level and the pinned z-zero approach. The requested raised 70 treatment remains partial; shared request R1 below records it. No feedback notes were open.

Target failures: 3 → 0. Ground cells: 256 → 256. Raw records: 104 → 120. Expanded records: 344 → 374.

| Metric | Before | After |
|---|---:|---:|---:|
| `props.props_per_100` | 6.640625 | 12.109375 |
| `props.dressed_share` | 0.593750 | 0.675781 |
| `props.bare_share` | 0.000000 | 0.000000 |
| `props.grouped_share` | 0.000000 | 0.400000 |
| `props.stride_share` | 1.000000 | 0.666667 |
| `ground.top1` | 0.976562 | 0.750000 |
| `ground.seam_density` | 0.050000 | 0.066667 |
| `repetition.period_excess` | 0.578726 | 0.122768 |
| `repetition.modal_chunk` | 0.250000 | 0.062500 |

Window: screen04 retains 98.886824% across 59,200 pixels, with zero changed pixels. The exterior and halls add no shot-window content.

## Outer hall

Reads as: A pillared hall with benches.

The nave uses 35 fill frames 0 and 1, framed by rough 71 stone. All eight column bases remain; two crowned shafts are removed to make stumps. The east benches move from x=4448 to x=4224. A broken votive screen and an urn occupy the north end, with explicit debris groups at bench feet and the south margin. The four frame-five tapestries across both halls become existing blue or green frames.

Set piece: **broken votive screen**, [640 by 400 capture](p4-m18/setpieces/m18-sp-votive-screen.png), with fragments at (2527,3007,0) and (2719,3039,0), and an urn at (2623,2959,0).

Claimed: VQ-056 and VQ-063, both graded regressed because paving escaped the walls; VQ-122, the east benches; and VQ-085, tapestry stand-ins. The 37 dais remains stopped under the new-standing-top exclusion. R2 specifies the shared change. No feedback notes were open.

Target failures: 3 → 0. Ground cells: 384 → 384. Raw records: 129 → 127. Expanded records: 489 → 504.

| Metric | Before | After |
|---|---:|---:|---:|
| `props.props_per_100` | 6.770833 | 10.416667 |
| `props.dressed_share` | 0.513021 | 0.606771 |
| `props.bare_share` | 0.078125 | 0.013021 |
| `props.grouped_share` | 0.000000 | 0.425000 |
| `props.stride_share` | 1.000000 | 0.714286 |
| `ground.top1` | 0.979167 | 0.625000 |
| `ground.seam_density` | 0.043956 | 0.087912 |
| `repetition.period_excess` | 0.564889 | 0.080037 |
| `repetition.modal_chunk` | 0.208333 | 0.041667 |

Window: screen04 retains 98.886824% across 59,200 pixels, with zero changed pixels. The exterior and halls add no shot-window content.

## Transition hall

Reads as: The hall that ends at a cracked wall.

Rough stone borders the dressed nave. Two small gravel groups lead toward the fallen arch, followed by a denser chip group beside the original rubble at (2975,5503,0). Added 526 chips are at (3103,5471,0), (3039,5599,0), and (3167,5663,0). Existing breach gravel, the pale 47 post, all six quality-307 records, the clear aperture, and the entry lane stay intact.

Set piece: **fallen arch**, [640 by 400 capture](p4-m18/setpieces/m18-sp-fallen-arch.png), with a 46 fragment at (3487,5343,0), a raw 47 fragment at (3584,5439,0), and irregular gravel fans.

Claimed: VQ-198, the isolated rubble; VQ-123, the masonry-to-cave transition; VQ-085, the remaining frame-five tapestries; and VQ-063's exterior corner. The requested low 524 piles remain stopped because their reachable 8-unit tops violate the placement contract. R3 covers that substitution. VQ-163's keyed pale post remains unchanged. No feedback notes were open.

Target failures: 2 → 0. Ground cells: 192 → 192. Raw records: 161 → 162. Expanded records: 341 → 356.

| Metric | Before | After |
|---|---:|---:|---:|
| `props.props_per_100` | 8.854167 | 15.104167 |
| `props.dressed_share` | 0.739583 | 0.859375 |
| `props.bare_share` | 0.000000 | 0.000000 |
| `props.grouped_share` | 0.000000 | 0.517241 |
| `props.stride_share` | 1.000000 | 0.666667 |
| `ground.top1` | 0.979167 | 0.625000 |
| `ground.seam_density` | 0.044944 | 0.089888 |
| `repetition.period_excess` | 0.552664 | 0.116667 |
| `repetition.modal_chunk` | 0.083333 | 0.083333 |

Window: screen04 retains 98.886824% across 59,200 pixels, with zero changed pixels. The exterior and halls add no shot-window content.

## Sanctum

Reads as: A raw cave shrine.

The shot-owned shrine retains its rock floor and ceremony. Authored gravel tongues cross the antechamber and the south fringe. Five mushrooms form a west-wall group. Fallen masonry carries the hall stone into the cave at the lane's east side. The skull remains at its pin beside a broken stone fragment. All 52 z-48 rock-top positions and the clipped west-passage art remain.

Set piece: **priestess memorial**, [640 by 400 capture](p4-m18/setpieces/m18-sp-priestess-memorial.png), with a 38 fragment at (2591,8671,0) and two nearby pebbles. Supporting authored pieces also have captures: [west-wall fungus](p4-m18/setpieces/m18-sp-west-wall-fungus.png) and [fallen breach masonry](p4-m18/setpieces/m18-sp-breach-masonry.png).

Claimed: VQ-196, the skull context, and the paving-related new problems reported under VQ-048 and VQ-050. VQ-024's art-track fix remains intact. The requested 37 fragment, bones, and continuous north and west crest remain partial: the source uses a 38 fragment, fungus and pebbles, and the existing rock tops. Adding the full crest raised quest-band occlusion, so that portion was stopped. R2, R3, and R4 specify the shared requests. No feedback notes were open.

Target failures: 2 → 0. Ground cells: 278 → 278. Raw records: 1160 → 848. Expanded records: 1160 → 1018.

| Metric | Before | After |
|---|---:|---:|---:|
| `props.props_per_100` | 1.798561 | 6.474820 |
| `props.dressed_share` | 0.579137 | 0.600719 |
| `props.bare_share` | 0.025180 | 0.007194 |
| `props.grouped_share` | n/a (4 small props) | 0.764706 |
| `props.stride_share` | 0.000000 | 0.000000 |
| `ground.top1` | 0.967626 | 0.636691 |
| `ground.seam_density` | 0.041176 | 0.149020 |
| `repetition.period_excess` | 0.137480 | 0.124628 |
| `repetition.modal_chunk` | 0.111111 | 0.111111 |

Window: screen04 retains 98.886824% across 59,200 pixels, with zero changed pixels. The exterior and halls add no shot-window content.

## Whole-map result

Raw records fall from 2,388 to 1,870, below the 2,400 exit ceiling and 3,000 hard cap. Expanded records fall from 3,168 to 2,864. Expanded records per ground cell fall from 2.854 to 2.506, below 2.9. Regional target failures fall from 10 to zero; no target allowance was added.

The 541 broad 895 backings and 22 894 backings are removed. Three clipped 895 west-passage backdrops stay. Black backing closes the rooms. A further 96 zero-height black plates cover the off-map north view: offsets of 1008 in x, 1009 in y, and 252 in z preserve projected position under truncating division while keeping the stored coordinates valid and the height on the 4-unit lattice. This extra coverage fixes stale forest pixels found in the first low-resolution engine capture. It is additional work required by the darkness change.

Every pinned row is unchanged. The `map_pins.json` artifact header was regenerated because `test_map_pins_fresh.py` requires its FIXED hash to match. All 494 anti-climb records, six keyed breach records, and the 52 z-48 rock-top positions are preserved. Every FIXED map payload outside Map 18 is byte-identical to the starting build.

The permanent visibility sample retains 155 positions. Positions below half visibility fall from 16 to 14; the one fully hidden position stays one. Existing quest-band debt stays 13 cells. The 128-unit audit samples 707 positions in both states, with 44 below half visibility and three fully hidden; the expected eight height swaps follow the relocated benches. Floor-black failures stay zero. The authorized D3 cave-class frame-black fractions change from mean 0.005402, p95 0.014337, and maximum 0.055707 to mean 0.092912, p95 0.268490, and maximum 0.302762, measured across 26 frames of 256,000 pixels. These remain below the cave-class limits of 0.47, 0.77, and 0.91. Improved dressing and visual pins are recorded; the exterior raw count rises to 120 and the Transition Hall raw count rises to 162 within the authorized budgets.

The static fast-area selection ranks m18-17 highest among the 26 stops at 1,205 expanded items. A fresh `Ultima8Engine::engineStats` reading there reports 2,266 objects in 32,511 slots, with 61 NPCs in 255 slots. [Load evidence](p4-m18/load-stats.log) records the settled map and position.

## Shared requests and stopped items

R1, exact 70 paving: a shared static copy row with retail 70 frames and donor 71 TYPEFLAG, including its zero-height footpad, would preserve the z-zero court contract. The shared registry would allocate and export `SHAPE_COURT_COBBLE_FLAT` before the map uses it. This slice allocates no shape. The current 71 floor is the flat rough-stone substitution.

R2, 37 architecture: `Site.set_piece` rejects reachable 8-unit plinth tops. An explicit shared API for named architectural standing surfaces would need to permit those tops outside pin clearances and quest bands, retain the 4-unit lattice checks, and prove route and shot preservation. Such an exception also needs a direction change to the no-new-standing-top rule. The raised dais and the skull-side 37 fragment are stopped pending that change.

R3, low rubble and bones: 524, 235, and 237 have reachable 8-unit LAND tops. The shared registry would need static copy rows for the exact retail 524, 235, and 237 sprites, using donor 465 flags (FIXED, with LAND and SOLID clear), the original horizontal footpads, and their original sprite-sorting heights. The hall and bone kits would then expose those allocated decorative IDs. These are shared copy rows and allocations. The current scene uses 526 chips, flat gravel, pebbles, fungus, and non-land stone fragments. No shared kit or shape was changed here.

R4, continuous cave crest: new 96-high caps above the passage increased quest-band occlusion from 13 to 40 cells. The passing source keeps the existing 52 tops. The partial new caps read as detached floating tops in engine captures and were removed. A continuous visible back needs a window-clipped decorative crest with no LAND or SOLID box, authored in the shared art module, with its exclusion bounds and route visibility checked there. The source preserves the current route while this item is stopped.

## Engine evidence

All 58 requested captures have `ok: true` and `landed: true`: 26 baseline frames, 26 final tour frames, and six set-piece frames. Every frame is 640 by 400. I inspected all 32 after and set-piece views at native size, including the refreshed rubble and cap-removal views. The forecourt has black above the cliff, and the detached new cave caps are gone. Every requested x and y matches its readback. The moved-bench stop m18-10 settles from requested z 8 to floor z 0.

Captures use display `:81`, runtime directory `/tmp/claude-1000/vq4-m18`, private game and configuration copies, and `usehighres=false`. Each stop starts a fresh world through `tools/playtest-linux/tour_capture.py`. The baseline runner points the unmodified session implementation at frozen baseline artifacts. Retried final stops use an external import runner that waits 1 s after debugger replies and makes at most three fresh-world attempts. Repository capture scripts remain unchanged. GLOB.FLX is copied explicitly into the private harness because the session script synchronizes the older five artifacts.

The main game installation and main checkout receive no writes. The feedback page read “Nothing open” at entry and before completion. No feedback-server action was needed. The captures and this report provide the evidence for a later Astra re-tour; no Astra regrade is claimed.

## Build, estate, and review

`tools/build_artifacts.sh --record` completes. Compilation succeeds for 55 of 57 sources; EALOGO and TJORVI remain the two documented allowlist failures. `test_dressing.py 18 --strict` reports zero failures and zero target failures. `test_visual_quality.py 18 --record --report128` reports zero failures and preserves the existing 13-cell phase-exit debt.

`tools/run_all_tests.sh` passes 57 of 58 test files. The sole failure is the allowed `test_integration_state`: the shared main install has its original FIXED.DAT and GLOB.FLX. The private harness matches all seven checked destinations. Route reachability passes 166 checks, paint cycles pass 76, hygiene passes 60, and vignette checks pass 39. Map-pin freshness passes all three checks.

The requested `codex exec review --base main` first failed because bubblewrap could not create its network namespace. The unrestricted rerun found the import-collision defect described below. The final unrestricted review reports no actionable regressions and passes strict dressing, visual quality, map-pin freshness, hygiene, crack geometry, and sanctum clearance. Its full-build and engine-playtest exclusions are covered by this slice's separate build and capture evidence.

The review also found a compiler-first `u8_flex` import collision in map-pin derivation. The builder now uses a fresh Python interpreter for that context and returns the complete packed FIXED records. `test_map_pins_fresh.py` passes all three checks. A separate compiler-first check preserves all 1,870 complete records byte for byte.

The independent verifier found two packed 47 wall fragments that the hygiene audit classified as baked walls. Their even x anchors retain raw FIXED records. No shared packer or test changed. Verifier checks cover the pins, breach, anti-climb records, screenshot pixels, clearance, Tiny Tar visibility, hygiene, and tour paint cycles. The off-map backing and final cap removal pass the verifier's follow-up checks.

Build, strict dressing, visual measurements, estate, verifier, review, capture-method, and identity evidence live beside the images in [p4-m18](p4-m18/). Derived changes are limited to the artifact hashes, packed-prefab manifest and provenance, map-pin header, and this map's ratchets. Shared modules and tests remain unchanged.

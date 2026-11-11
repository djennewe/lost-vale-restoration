# Phase 4 Map 08: Lost Vale cave additions

Branch `wt/vq4-m08`, based on `4d3d5142`; revision of reviewed commit `b56ce589`. Work dated 9 November 2026, America/Chicago.

The two regional set pieces now have room-corner compositions: **the hollow fairy ring** on the south shelf and **the vigil camp** in the door chamber. Both use explicit coordinates through `site.set_piece`. The four smaller mushroom and gravel pockets remain dressing. This revision replaces only the original 15 primary-set-piece records with 27 records. Darkness outside the shelf, all floor work, the smaller pockets, and the house correction survive.

Regional target failures remain five before Phase 4 and three after, each covered by the existing retail-preservation allowances. Strict dressing and visual quality pass. VQ-091 remains deferred to the shared slice.

## South shelf

**Reads as:** a worn rock shelf inside Mythran's retail caves, with a hollow ring of giant fungus in a recess, gravel caught around its feet, and darkness beyond its edges.

**The hollow fairy ring** spans 608 by 608 world units including footprints. Eight giant mushrooms form an irregular ring around three central stones. Five further stones connect the cap groups and break the perimeter. The ring's empty centre and alternating cap colours give the scene a silhouette visible in the 640×400 camera. It occupies exposed 301 floor away from the shelf legs.

[Final set-piece capture](p4-m08/setpieces-fix/m08-sp-fairy-ring.png), camera (31168,27744,56).

The original three-mushroom seep garden is superseded. West shelf gravel, east shelf fungus, south shelf gravel fan, and lower shelf seep retain their original coordinates and their separate `site.set_piece` reservations. Their refreshed captures remain contextual dressing evidence:

| Dressing pocket | Capture |
|---|---|
| West shelf gravel | [capture](p4-m08/setpieces-fix/m08-sp-west-gravel.png) |
| East shelf fungus | [capture](p4-m08/setpieces-fix/m08-sp-east-fungus.png) |
| South shelf gravel fan | [capture](p4-m08/setpieces-fix/m08-sp-south-fan.png) |
| Lower shelf seep | [capture](p4-m08/setpieces-fix/m08-sp-lower-seep.png) |

| Metric | Before Phase 4 | Final |
|---|---:|---:|
| Props per 100 cells | 6.36 | 9.18 |
| Dressed cells | 56.21% | 64.97% |
| Bare cells | 14.62% | 2.47% |
| Grouped small props | 71.70% | 81.72% |
| Prop stride | 88.46% | 58.06% |
| Top material | 82.63% | 82.63% |
| Material seams | 11.66% | 11.66% |
| Tile-period excess | 55.28% | 19.86% |
| Modal chunk | 34.67% | 6.67% |
| Raw records | 1819 | 1859 |
| Expanded records | 2944 | 2984 |

Target failures fall from three to one. Top-material share remains 82.63% against 65%, allowed because §3.7 preserves the exposed 301 floor and retail geometry. The final shelf composition stays within the cave density aim band.

The 301 floor, supports, 894 and 895 underpaint, both seam lists, and first-aperture repaint remain. Floor-frame variation from the accepted slice remains. The 213 decorative 895:0 skirts already changed to 895:2 remain black, including the plateau witness skirt. The 184 original black backings remain. No paving returns outside the shelf, and no scatter or chunk substitution is introduced.

VQ-023 and VQ-044 remain claimed for removal of detached paving. VQ-046 retains cave darkness at all four LV route-witness surrounds. VQ-018, VQ-022, VQ-030, VQ-031, VQ-060, and VQ-064 retain their retail limits. The independent Astra regrade remains with integration.

## Door chamber

**Reads as:** the retail bone chamber and paired stone approach to the sealed doors, with a traveller's vigil camp tucked into its west corner.

**The vigil camp** comprises a supply crate, rolled bedroll, dropped torch, and a campfire encircled by seven small stones. Its warm wood and fire give it a focal point among the chamber's grey bones. The crate forms the back of the composition; the bedroll and torch lie on visible floor beside it. The fire uses existing retail shape 267 and remains damaging; it sits outside the quest bands. The camp sits west of the return lane, clear of the chest, contained key, hatch boxes, pins, and quest legs.

[Final set-piece capture](p4-m08/setpieces-fix/m08-sp-vigil-camp.png), camera (20287,3967,0).

The five-pebble doorward stonefall is superseded. The 19 decorative paving backings beyond this chamber stay black. All physical floors and the 71:0 return marker remain.

| Metric | Before Phase 4 | Final |
|---|---:|---:|
| Props per 100 cells | 24.69 | 38.27 |
| Dressed cells | 65.43% | 86.42% |
| Bare cells | 0.00% | 0.00% |
| Grouped small props | 70.00% | 80.00% |
| Prop stride | 100.00% | 82.35% |
| Top material | 66.67% | 66.67% |
| Material seams | 21.83% | 21.83% |
| Tile-period excess | 56.82% | 56.82% |
| Modal chunk | 100.00% | 100.00% |
| Raw records | 83 | 94 |
| Expanded records | 206 | 217 |

Two target failures remain: prop stride 82.35% against 65%, and top material 66.67% against 65%. The paired retail 394 colonnade and retained floor explain these allowances. The chamber has 81 ground cells, so the shared contract excludes its two repetition limits. Its baseline density already exceeds the cave aim band; this revision adds one composed camp with 11 records.

**VQ-091 remains deferred.** `test_route_reach.py`'s `DELIBERATE[212]` still requires shape 71, frame zero, at (20639,3967,0). The orchestrator owns the shared test update and subsequent frame-nine change. This slice changes neither marker identity nor position.

## Mythran's house

VQ-100 still removes the single 301 slab at z 1 below the pinned apparition at (2200,2208,8). No house furnishing is added. The house is outside `REGIONS[8]` and has no additional regional set-piece obligation. [Before](p4-m08/before/m08-32.png) and [retained after](p4-m08/after/m08-32.png) remain pixel-equivalent to this revision.

The apparition remains visible before its scene in the baseline and final map. Its pin and placement stay unchanged; hiding it until the scene belongs to the usecode queue.

## Geometry, windows, and pins

[Revision validation](p4-m08/fix-validation.json) compares the accepted artifact with the final artifact. Only archive entry eight changes. Exactly 15 old primary-set-piece records leave and 27 new records enter. Every other accepted record survives, including both darkness changes. Anti-climb walls, map-pin rows, and quest bands remain identical: shelf-1 15 cells, shelf-2 252, shelf-3 378, and door-1 53. The one-field `fixed_sha256_prefix` refresh tracks the new artifact.

Map 08 has no pinned 1994 screenshot window. The other 255 archive entries and the other five artifacts remain byte-identical to the accepted slice, preserving its [39 passing window checks and scores](p4-m08/vignettes.txt). Screens 19 and 20 retain 97.087% and 97.703% ([comparison](p4-m08/window-comparison.json)). The new estate also runs all window assertions.

Raw records rise from 5,923 before Phase 4 to 5,973 final, below 6,500; expanded records rise from 29,243 to 29,293, below 31,000. This revision adds 12 records compared with `b56ce589`. No prefab or shape ID is allocated, and every retail glob slot survives unchanged. Improved dressing pins tighten to the final metrics. Record pins rise within the authorised budget.

Visual-quality measurements match the accepted slice: 79 leg cells below half-visible, 14.228% of sampled cells below half-visible, 10.569% hidden, median minimum visibility 100%, and both black-floor measures zero. The inherited 79-cell retail-wall debt remains. Frame-black mean, p95, and maximum stay 36.566%, 65.258%, and 71.456%, within the cave limits of 47%, 77%, and 91%. No visibility or darkness bound rises in this revision.

Final FIXED.DAT SHA-256: `a7c9f6cac65f0e3c83b60965b8c77e21d3d00b706387599a2a989c5dcb914363`.

## Captures and verification

The final revision retakes all six set-piece and dressing cameras in [setpieces-fix](p4-m08/setpieces-fix/captures.json) and all seven affected tour views in [after-fix](p4-m08/after-fix/captures.json). The affected stops are m08-09, m08-12, m08-49, m08-45, m08-46, m08-47, and m08-48. The remaining 16 accepted after views remain pixel-equivalent, recorded in [the model comparison](p4-m08/fix-pixel-comparison.json). The original 23 before views remain in `p4-m08/before/`.

Every refreshed capture uses `tour_capture.py` through the existing log-preserving retry wrapper, display `:83`, runtime `/tmp/claude-1000/vq4-m08`, `usehighres=false`, and a fresh world. The existing invincibility setting prevents monsters from killing the Avatar during settling. The final validation requires `landed: true`, `ok: true`, positive health, 640×400 images, and zero post-arrival paint-cycle warnings. [Inspection evidence](p4-m08/fix-inspection.json) identifies the final images inspected at game resolution. Original `setpieces/` images are superseded evidence.

- `tools/build_artifacts.sh --record`: passed; only FIXED.DAT changes among the six merged artifacts. [Build](p4-m08/build-fix.txt).
- `python3 agents/map-populator/src/test_dressing.py 8 --record --strict`: zero failures, three preserved retail allowances. [Dressing](p4-m08/dressing-fix.txt).
- `python3 agents/map-populator/src/test_visual_quality.py 8 --record --workers 2`: zero failures; inherited leg debt unchanged. [Visual quality](p4-m08/visual-fix.txt).
- `tools/run_all_tests.sh`: 57 of 58 test files pass. The sole failure is the permitted shared-install `test_integration_state.py` check: 10 assertions pass, one fails, and three skip because this worktree has no engine source tree. The private harness has all seven canonical artifact copies; the shared install carries main's FIXED.DAT. [Estate](p4-m08/estate-fix.txt).
- `codex exec review --base main`: the default sandbox failed with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`. The unrestricted retry found stale hashes during iteration; the final recording build and derived pins resolve that finding. The final unrestricted review finds no actionable regressions and independently passes all 166 route checks, strict Map 8 dressing, and backdrop checks. [Initial retry](p4-m08/review-fix-unrestricted.txt), [final review](p4-m08/review-fix-final.txt).

The first camp layout also failed the closed-door movement check. Relocating the camp west restores the targeted open-door and closed-door checks. The final estate verifies the complete quest route. The first ring layout removed two visible sampled positions; shifting two caps by 32 units restores the accepted visibility ratios.

## Feedback and shared requests

`docs/map-feedback/OPEN.md` says “Nothing open.” No feedback response is required.

1. **VQ-091:** the orchestrator owns the shared route-test update from frame zero to frame nine at the existing marker position. This slice leaves it deferred.
2. **Pre-scene apparition:** the usecode queue must keep the Map 08 backstop apparition hidden until its Lord British scene reveals it, preserving its pin, trigger lookup, and alternate-placement cleanup. Relevant sources are `lv-new/LBSCENE.UNK` and `lv-patched/LORDBRIT.UNK`.

No new kit, prefab, shared dressing API, or shape is requested. Shared tests and modules remain unchanged. Game data links to main; builds and capture runtime remain private. No install, merge, or push is performed. The final validation compares main's relevant tracked files with its own HEAD to confirm this slice leaves them untouched.

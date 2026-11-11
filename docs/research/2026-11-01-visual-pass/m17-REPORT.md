# Map 17 visual-quality phases 2 and 3

Branch: `wt/vq2-m17`, based on `ba34836`. Phase 2 baseline:
`ad93e0a`. Phase 3 implementation: `7fd167a`.

Specified-black floor cells fell from 16 to zero. Frame black at step 128
fell from 8.77% / 41.54% / 72.64% to 2.20% / 17.44% / 44.78%
(mean / p95 / max). Both 1994 windows remain pixel-identical. All 62,424
reachable cells, all 400 curbs, and all nonfloor records are unchanged.
The permanent test passes its pins; strict acceptance retains the 46-cell
quest-band visibility debt inherited from `ba34836`. The north and west
coordinate limits also retain earlier frame pixels in low-resolution play.

## Phase 2

Section 4.6 specifies no phase 2 implementation items. The unchanged build
was measured and committed before phase 3. `test_visual_quality.py 17`
passed with zero ratchet failures, 6,665 raw and expanded records, and
62,424 reached cells. `void_audit.py 17 --step 128 --workers 4` found 16
specified-black cells and 19 prop-black cells. `avatar_visibility.py 17
--step 128 --workers 4` found 43 cells below half visibility and two fully
hidden cells among 3,728 sampled positions.

The permanent quest-band check found 46 cells below half visibility. This
matches `ba34836` and contradicts section 4.6's statement that the leg passes.
The phase 3 floor work retains this baseline debt. A separately authorized
Map 17 phase 2 pass or a Douglas-approved allowance would be required to
resolve it. No shared module or allowance was changed.

The phase 2 FIXED hash remains
`89da4e165833bff0b4da526cfa2cbc434336f6816e3964ae9982bd804a2eb767`.
Evidence: `m17/before-audit/` and `m17/phase2-audit/map17-metrics.json`.
Because phase 2 changes no game records, this is also the phase 3 baseline.

## VQ-047: cloud-sea boundary

**Status: improved.** Two fixed sea rectangles left visible black plates
beyond the other city edges. The sea now uses `cells_within_view` on the
layout's world-coordinate max corners, removes layout cells, and clips to
cell indices at least one. Position hashes retain the existing 874 frame
selection. The sea contains 2,587 tiles, compared with 1,077 previously.
The playable layout supplies the curbs, so the sea introduces no curb
records and no reachable cells.

The table uses the floor probe at each tour camera, frame black over
640×400 pixels, and minimum visibility over 72 walk and stand poses.
Percentages are percentages of frame pixels or opaque Avatar pixels.
Each floor entry is a black-probe count out of one. These are built-scene
measurements; the adjacent engine captures provide the visual evidence.

| Stop | Walkable black, before → after | Frame black %, before → after | Min visible %, before → after |
|---|---:|---:|---:|
| m17-07 | 0 → 0 | 3.39 → 3.39 | 100.0 → 100.0 |
| m17-10 | 0 → 0 | 39.14 → 0.06 | 100.0 → 100.0 |
| m17-12 | 0 → 0 | 68.87 → 24.69 | 100.0 → 100.0 |
| m17-13 | 0 → 0 | 46.56 → 0.06 | 100.0 → 100.0 |
| m17-15 | 0 → 0 | 0.16 → 0.16 | 100.0 → 100.0 |
| m17-16 | 0 → 0 | 53.26 → 38.89 | 100.0 → 100.0 |
| m17-17 | 0 → 0 | 9.60 → 0.22 | 100.0 → 100.0 |
| m17-18 | 0 → 0 | 2.27 → 0.09 | 100.0 → 100.0 |
| m17-20 | 0 → 0 | 0.11 → 0.11 | 100.0 → 100.0 |
| m17-21 | 0 → 0 | 26.56 → 0.07 | 100.0 → 100.0 |
| m17-22 | 0 → 0 | 23.71 → 3.89 | 100.0 → 100.0 |
| m17-25 | 0 → 0 | 19.30 → 11.53 | 100.0 → 100.0 |
| m17-29 | 0 → 0 | 25.51 → 0.07 | 100.0 → 100.0 |
| m17-30 | 0 → 0 | 46.70 → 46.70 | 100.0 → 100.0 |
| m17-31 | 0 → 0 | 18.37 → 3.31 | 100.0 → 100.0 |
| m17-33 | 0 → 0 | 23.90 → 0.06 | 100.0 → 100.0 |
| m17-34 | 0 → 0 | 54.21 → 0.20 | 100.0 → 100.0 |
| m17-03 | 0 → 0 | 0.27 → 0.27 | 100.0 → 100.0 |
| m17-05 | 0 → 0 | 0.50 → 0.50 | 98.1 → 98.1 |

The current phase 1 build already closes the sea at m17-15 and m17-20;
those stops retain their low black shares. At m17-07 the surviving black
is also unchanged. At m17-30 the requested coordinate clip leaves the
north map limit visible, so its 46.70% black share is unchanged. The
step-128 worst camera is `(2719,287,0)`, at 44.78% black. Other north and
west cameras also see the coordinate limit. The 20% design target remains
unmet there; the formal 7% / 38% / 62% frame limits pass. Removing this
last boundary would require changing the prescribed clip or moving the
playable boundary. With `usehighres=false`, those unpainted coordinate-limit
regions also retain earlier frame pixels. The engine captures expose this
remaining limitation, so VQ-047 remains improved. The stop table reports
the audit's black-or-unpainted measure; each capture summary also records
the PNG's actual pure-black share, which differs where old pixels remain.

## Walkway court: 16 specified-black cells

**Status: fixed.** The layout already contains the affected cells. The
hole arose after stamping: `fill_gaps` counted a raised walkway slab as
cover for the cell containing its centre. Its uncovered strip then
received black plates, whose 256-unit coverage also overlapped adjacent
cloud. Ground-level flat floors now supply coverage for `fill_gaps`, so
cloud remains beneath raised slabs. This adds 10 cloud tiles while
preserving every raised slab and pinned item.

| Probe | Walkable black, before → after | Frame black | Min visible |
|---|---:|---|---|
| All reached cells at x 2463..2943, y 2975, z 0 | 16 / 16 → 0 / 16 | Included in map distribution below | Map visibility unchanged |
| m17-05, walkway camera | 0 / 1 → 0 / 1 | 0.50% → 0.50% | 98.1% → 98.1% |

`geometry.json` records equality of the complete 32-unit reached-cell
sets. The permanent route test covers the raised walkway at
`(2303,3103,8)`, trigger 208 with the 128-square body, and arrival-channel
constraints. A separate exact-reach flood at step 8 within x 4096..5120 and
y 9728..11392 reaches no return trigger from the arrival pad, confirming
that the direct channel crossing remains sealed. The full estate result
appears below.

## Windows, pins, and records

| Window | Class score before → after | Unpainted pixels before → after | Changed built pixels |
|---|---:|---:|---:|
| screen11 | 99.9293% → 99.9293% | 0 → 0 | 0 |
| screen12 | 97.9429% → 97.9429% | 0 → 0 | 0 |

The two windows apply to both items above. Their floors of 99.93 and
97.94 hold with the test's existing slack. `before-stops.json` and
`after-stops.json` retain the exact scores.

| Measurement | Before | After |
|---|---:|---:|
| Raw records | 6,665 | 7,953 |
| Expanded records | 6,665 | 7,953 |
| Phase 2 and 3 exit ceiling | 10,500 | 10,500 |
| Cloud records (874) | 4,390 | 5,910 |
| Black plates (564:2) | 847 | 615 |
| Specified-black reached cells | 16 | 0 |
| Prop-black reached cells | 19 | 19 |
| Quest-band cells below half visibility | 46 | 46 |
| Step-128 cells below half visibility, of 3,728 | 43 (1.1534%) | 43 (1.1534%) |
| Step-128 fully hidden cells, of 3,728 | 2 (0.0536%) | 2 (0.0536%) |
| Median of minimum visibility | 100% | 100% |
| Step-128 frame black mean | 8.7663% | 2.2007% |
| Step-128 frame black p95 | 41.5374% | 17.4427% |
| Step-128 frame black max | 72.6375% | 44.7773% |
| Permanent step-512 frame black mean | 9.3332% | 2.0816% |
| Permanent step-512 frame black p95 | 42.8157% | 8.5914% |
| Permanent step-512 frame black max | 63.5160% | 29.6414% |

Every improved pin was lowered, including its step-128 report value.
Record pins rose within the exit ceiling. Visibility pins, prop-black
pins, and allowances retain their baseline values. `geometry.json`
confirms that Map 17 is the sole changed raw FIXED archive entry; the
other 255 entries are byte-identical. A record multiset comparison also
confirms that Map 17's nonfloor records are unchanged.

## Captures and reproducibility

Engine captures use display `:66`, runtime directory
`/tmp/claude-1000/vq2-m17`, `usehighres=false`, and a fresh world per stop.
The unchanged `tour_capture.py` and its shell helpers were copied to a
frozen baseline runner under that runtime directory, retaining private
baseline artifacts while the worktree rebuilt. `capture-provenance.json`
records matching script hashes and the original FIXED hash. After captures
use the worktree's rebuilt artifacts. Before and after PNG names use the
17 VQ-047 tour stop IDs, with m17-03 and m17-05 added for the two
1994 window locations. The retry adapter is preserved as
`capture-runner.txt`. It calls `tour_capture.main`, keeps the tool's
fresh-world launch and surface crop, waits for game initialization,
clears detected title or menu overlays, holds debugger modifiers for 0.4 s, and sends
each debugger command once. Its readback includes the final partial log
line because replies append to the existing `debug>` prompt. Settle time
is at least 22 s; the initial retry batch used 35 s. Failed attempts are replaced by fresh successful captures.
Repository capture helpers remain unchanged. An image check rejects title
and menu overlays even when position readback succeeds.
`overlay-templates.npz` supplies the two image-check templates.

Large per-cell audit JSON and tab-separated files are stored as deterministic gzip
files alongside the original summaries and heatmaps. Stop and capture
measurement scripts are preserved as `stop-metrics.txt` and
`capture-summary.txt`.

All 19 before captures and all 19 after captures are accepted: `landed:
true`, 640×400 game surfaces, and zero title or menu overlays. All
19 before positions and all 19 after positions match the requested
coordinates exactly. The two capture-summary JSON files record image
hashes, artifact hashes, pure-black screenshot shares, and overlay checks.

After logs cover 19 of 19 stops. They contain zero paint-cycle or
nonexistent-process warnings on Map 17. The baseline logs available for
14 stops likewise contain no Map 17 warnings. The captured startup
sequences recorded 42 baseline and 57 after warnings outside Map 17;
their map numbers and messages are retained in the summaries. These are
the inherited Guardian sequence's Map 0 process warnings.

Both measurement phases ran:

```sh
python3 -B agents/map-populator/src/void_audit.py 17 --step 128 --workers 4 --out EVID/STATE-audit
python3 -B agents/map-populator/src/avatar_visibility.py 17 --step 128 --workers 4 --out EVID/STATE-audit
python3 -B agents/map-populator/src/test_visual_quality.py 17
```

After implementation, `test_visual_quality.py 17 --record --report128`
passed with zero failures and refreshed the pins and artifact hashes.
`test_visual_quality.py 17 --strict` failed exactly once:
`phase-exit debt leg_cells_below_half=46 (target 0)`. The floor audit's
standalone `walkable_black_pass` remains false because it includes the
19 allowed prop-black pixels; the permanent test distinguishes them and
records zero specified-black cells.

## Build, estate, and review

`tools/build_artifacts.sh --record` passed. The compiler retained exactly
the EALOGO and TJORVI allowlist failures. `derive_map_pins.py` regenerated
the inventory with unchanged pinned records.

`tools/run_all_tests.sh` completed: 56 of 57 test files passed. The sole
failure was the permitted `test_integration_state` worktree exception:
nine assertions passed, two failed, and three engine-tree assertions were
skipped. The two failures were stale FIXED bytes in the private harness
copy, which the after captures have now synchronized, and the main checkout's
symlinked install target, which this slice leaves untouched. The route
test passed 166 assertions, map hygiene passed 60, paint cycles passed 76,
and vignettes passed 39. The eight-map permanent visual test also passed.
`sha256sum -c ARTIFACTS.sha256` confirmed all five artifacts. Compressed
estate, integration-state, build, strict-test, and review logs accompany
this report.

The requested `codex exec review --base main` first encountered the local
bubblewrap failure: `bwrap: loopback: Failed RTM_NEWADDR: Operation not
permitted`. Re-running with `-c 'sandbox_mode="danger-full-access"'`
completed. The reviewer found no actionable regressions, independently
passed the Map 17 visual-quality and map-hygiene checks, and confirmed the
canonical FIXED hash. The inherited quest-band debt was also confirmed.
There were no review findings requiring implementation changes.
A follow-up review of the final pins and capture adapter also found no
actionable regressions. It independently passed visual quality, map
hygiene, route reachability, and vignettes, and verified all five hashes.

Final artifact hashes:

```text
ac0b33486fc167d98c07c32011de348c11ae0cefb8d89fc2597ef984133a5fd1  TYPEFLAG.DAT
aad6ed7b8961f416b6fae225d467427899a4487db768b6fb486ed5b5cb3e73ba  U8SHAPES.FLX
97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443  ANIM.DAT
b47c324cdad77646c27755acfdd5bca53a9d92e16268db229f18e7dd780d4205  EUSECODE.FLX
2923990eb39ded5d3a58edca385bc83b964b089473c3e46386dd16cccef6ef2c  FIXED.DAT
```

## Remaining work and scope

- VQ-047: improved. Cloud sea closes the interior stepped edges. The
  prescribed north and west coordinate clip retains edge black and keeps
  the optional 20% maximum target out of reach.
- Walkway court's 16 specified-black cells: fixed. All 16 now probe drawn
  cloud, with unchanged reachability and screenshot windows.
- Quest-band visibility: blocked by section 4.6's explicit phase 2 scope.
  The baseline already measures 46 failing cells. A separate phase 2 scope or
  approved allowance is required for strict acceptance.
- Optional 256-unit cloud shape: omitted. The existing cloud shape meets
  the record ceiling, and this slice has no authorization for a new ID.

No merge, push, main-checkout edit, retail-content change, pinned-item
move, new shape, or shared-module edit occurred. Game data uses symlinks to
the main checkout. Artifacts and the installed capture game are private
copies. TODO.md remains unchanged because it is outside this slice's
allowed files.

The five setup symlinks under `shared/data/` remain untracked because the
ignore patterns match directories. They remain outside the commits.

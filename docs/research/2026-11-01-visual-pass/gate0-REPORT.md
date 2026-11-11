# Gate 0: visual-quality contracts

Implemented on `wt/vq2-gate0`, based on `616d151`. The game artifacts remain byte-identical. The permanent visual test passes against the measured baseline in 87.643 seconds in the final estate run with four workers. Final phase-exit violations remain explicit ratchets for the map slices.

## Shared changes

1. Painted cover includes decorative cave backdrops 894 and 895 in `floor_cells(..., painted=True)`. They contribute no floor seeds. `void_cells`, `void_floor`, `void_cover`, and the hygiene audit share this cover calculation. Map 8 remains the sole backdrop consumer and does not call `void_floor`; the rebuilt FIXED hash proves that plate counts and all other records stayed unchanged.
2. `Cave(..., near_courses=2)` preserves the existing two drawn courses. Zero or one retains the requested lower drawn courses and adds invisible blockers for the remaining courses of the 96-unit face. Replacement blockers follow each piece's jagged offset. Short pieces use 32-unit strips of perpendicular blockers extending into the rock. North and west faces retain their existing invisible treatment. Invalid course counts raise `ValueError`. No map builder changed.
3. `ExactReach.shortest_path(reach, a, b)` uses deterministic breadth-first search, cardinal in-plane edges, stationary XY level transitions, and the flood's enumerated riser table. Endpoint matching uses `reached_near(..., ring=96)`; ties sort by world coordinates. Unreached or disconnected endpoints raise `ValueError`. `quest_legs.py` carries all specified endpoints and dilates each path into a reachable three-cell band at its standing level.
4. `RECORD_BUDGET` blocks raw record overflow in `validate_and_gate`. Maps 8 and 39 also block expanded counts above 31,000. Errors use the existing validator report schema and prevent promotion of FIXED. The visual test records both counts and carries Map 11's D5 exit ceiling of 11,700.
5. `test_visual_quality.py` measures floors and bands at 32 units, map-wide visibility at 256 units, and frames at 512 units. Eight independent JSON pin files hold current measurements, the step-128 report values, and signed allowances. `--record` rejects weakened existing pins. Improvements print “lower these pins”. `--strict` also enforces the final phase-exit rules.
6. Eight PNGs in `gate0/` show full 32-unit quest bands in blue over the step-128 visibility heatmaps. Green indicates visibility and red indicates occlusion. The worst sampled level supplies each XY colour. Fine leg-cell visibility supplies the heatmap beneath disconnected bands, including the door chamber and Tiny Tar sanctum. Compact per-map metric JSON files preserve measurements and runtimes.

## Quest-state and allowance details

Chains use the arrival flood to match their consecutive endpoints; a talisman or chest coordinate can itself be solid and cannot seed the next flood. Map 8's shelf and door chamber use separate arrival components. Tiny Tar's sanctum legs use body `(32,32,32)` and shape 867. Map 11's final leg removes quality-299 boulders from both reachability and visibility.

The unrestricted Map 39 dry flood found a shorter path through retail trigger corridors. Its second leg therefore passes through a tunnel waypoint `(16191,19935,48)`, and asserts that the path enters x 16096..16223, y 19584..19968. The resulting band contains 24 tunnel cells. This preserves the specified city and egg endpoints while covering the named LV lane.

Map 8 has exactly 256 inherited specified-black coordinates. Their coordinates remain frozen. D1 allowances for VQ-018/022/023/030/031 use the existing backlog camera-witness envelopes, with their source and approval recorded in each reason. These envelopes are conservative and retain the outstanding LV occlusion ratchet. Map 13's confirmed D4 frame box is `[0,0,8000,1800]`, from VQ-054. Map 18's D11 crack-pier box is `[2624,5983,3007,6143]`.

## Permanent pins and runtime

Per-map runtimes below are from the pin-recording run. Fractions below are displayed as percentages; JSON retains full precision. Visibility uses 256-unit samples, and frame distributions use 512-unit samples with frame allowances excluded. The specified-black column excludes the 256 Map 8 inherited cells. All median-of-worst-pose pins are 100%.

| Map | Runtime (s) | Specified black | Prop black | Leg cells below 50% | Raw records | Expanded records |
|---|---:|---:|---:|---:|---:|---:|
| 8 | 4.776 | 0 | 0 | 79 | 5,689 | 29,009 |
| 9 | 1.637 | 0 | 19 | 116 | 1,019 | 1,349 |
| 10 | 37.892 | 31 | 42 | 841 | 20,571 | 37,566 |
| 11 | 13.840 | 6 | 165 | 191 | 9,515 | 17,825 |
| 13 | 3.861 | 0 | 5 | 3 | 6,447 | 7,692 |
| 17 | 5.566 | 16 | 19 | 46 | 6,665 | 6,665 |
| 18 | 1.803 | 0 | 0 | 33 | 1,750 | 2,530 |
| 39 | 17.223 | 0 | 14 | 437 | 5,108 | 29,068 |

| Map | Below 50% | Hidden | Frame mean | Frame p95 | Frame max |
|---|---:|---:|---:|---:|---:|
| 8 | 14.228% | 10.569% | 36.642% | 65.258% | 71.456% |
| 9 | 28.947% | 2.632% | 22.134% | 41.347% | 47.170% |
| 10 | 4.687% | 0.900% | 1.050% | 8.732% | 27.042% |
| 11 | 11.824% | 0.606% | 5.297% | 21.982% | 36.041% |
| 13 | 3.237% | 1.439% | 5.815% | 21.527% | 35.250% |
| 17 | 1.972% | 0.110% | 9.333% | 42.816% | 63.516% |
| 18 | 16.129% | 6.452% | 10.268% | 26.773% | 30.598% |
| 39 | 13.696% | 4.214% | 8.931% | 47.000% | 63.056% |

The timed command was:

```sh
python3 -B agents/map-populator/src/test_visual_quality.py --record --out ~/projects/lv-wt-vq2-gate0/docs/research/2026-11-01-visual-pass/gate0
```

Result: zero failures; 86.941 seconds inside the measurement loop, 87.86 seconds including startup and contract checks. The initial step-128 report run took 414.980 seconds. The permitted 512-unit frame fallback reduced the estate workload; floor and leg spacing remain 32 units.

## Comparison with design section 0

Every unfiltered step-128 visibility and frame distribution rounds to the design table. Reached-cell counts and raw and expanded record counts also match. Specified and prop black counts match, including Map 8's 256 inherited cells. Map 13's filtered report distribution differs because D4 now excludes the accepted north box; unfiltered values below remain available in each metric JSON.

| Map | Below 50% / hidden | Frame mean / p95 / max |
|---|---|---|
| 8 | 14.7% / 7.1% | 34.6% / 61.3% / 78.8% |
| 9 | 26.6% / 10.1% | 26.1% / 53.4% / 64.3% |
| 10 | 4.7% / 2.2% | 2.1% / 16.4% / 51.2% |
| 11 | 12.1% / 5.2% | 8.3% / 36.0% / 56.5% |
| 13 | 3.8% / 1.2% | 9.9% / 39.3% / 59.2% |
| 17 | 1.2% / 0.1% | 8.8% / 41.5% / 72.6% |
| 18 | 13.6% / 6.5% | 18.0% / 45.3% / 64.7% |
| 39 | 12.7% / 6.1% | 7.0% / 39.1% / 75.8% |

## Verification

- `tools/build_artifacts.sh`: PASS, all five canonical hashes match. The expected recovered-source compiler failures remain the EALOGO and TJORVI allowlist pair.
- `sha256sum -c ARTIFACTS.sha256` in the private worktree build directory: all five OK.
- Shared API negative controls run with the permanent test: deterministic path ties, disconnection, illegal one-unit risers, default cave emission, zero and one drawn courses, invalid course counts, backdrop cover without seeds, and raw and expanded overflow rejection.
- `git diff --check`: passed.
- `tools/run_all_tests.sh`: PASS, 57/57 test files. The permanent visual test passed in 86.776 seconds initially and 87.643 seconds after the review fixes. `test_integration_state.py` passed 10 assertions, with four local engine and harness checks skipped.
- Initial `codex exec review -c 'sandbox_mode="danger-full-access"' --base main`: two P2 findings, both fixed as described below. The follow-up review found no actionable regressions; its independent visual test passed in 87.713 seconds, hygiene passed 60 checks, and route reachability passed 166 checks. The post-fix estate rerun passed 57/57 files. A final review including the completed leg heatmaps also found no actionable regressions; its visual test passed in 86.821 seconds.

Canonical hashes:

```text
ac0b33486fc167d98c07c32011de348c11ae0cefb8d89fc2597ef984133a5fd1  TYPEFLAG.DAT
aad6ed7b8961f416b6fae225d467427899a4487db768b6fb486ed5b5cb3e73ba  U8SHAPES.FLX
97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443  ANIM.DAT
b47c324cdad77646c27755acfdd5bca53a9d92e16268db229f18e7dd780d4205  EUSECODE.FLX
89da4e165833bff0b4da526cfa2cbc434336f6816e3964ae9982bd804a2eb767  FIXED.DAT
```

## Review findings and fixes

The initial sandboxed review could not read the repository: bubblewrap failed with `Failed RTM_NEWADDR: Operation not permitted`. Re-running with the workspace's unrestricted access produced a complete review, including an independent eight-map visual test pass in 87.288 seconds.

- Jagged upper walls: the initial straight blocker run exposed a Tiny Tar foothold at `(255,415,48)`. Replacement blockers now follow each removed piece's offset. A regression check covers both face directions and zero, one, and two drawn courses. Window clipping still tests the original two-course face, so lowering a course preserves the original clipping decision.
- Stale report evidence: the initial writer retained old step-128 distributions and substituted new floor, leg, and record counts. Each run now writes its current measurements. Fresh step-128 distributions appear only with `--report128`. Each new measurement includes the five artifact hashes. The CLI regression check seeds an old report, runs a mocked current audit, and confirms that the old distribution is omitted. Historical pin metadata and this report's snapshots carry the artifact hashes that identify their measured build.

## Spec conflicts and remaining work

The strict rules in sections 1.3 and 1.4 cannot all pass on the byte-identical current build. It has 31 specified-black cells on Map 10, six on Map 11, and 16 on Map 17; all eight maps have quest-band occlusions outside the accepted boxes. Frame-class violations also remain. Gate 0 therefore enforces the measured pins and record caps, prints each phase-exit debt, and exposes `--strict` for final acceptance. No new occlusion sign-offs were invented for LV defects. Map slices must reduce these debts.

Frame pins use 512-unit sampling under the runtime fallback. Visibility remains at 256 units, and the 128-unit report distributions are retained separately. The two sample grids produce different distributions, as the design anticipates.

The initial report run also exposed a test implementation error: applying an expanded 32,500 ceiling to Map 10 rejected its existing 37,566 expanded items. The spec applies expansion ceilings to Maps 8 and 39; the corrected test uses those two ceilings and the per-map raw budgets.

Record counts are pinned to current measured values as requested. A future slice that adds skirt records will need an explicit record-pin adjustment within the published budget; the blanket “pins only go down” rule conflicts with those planned record additions. This slice makes no such adjustment.

Retail has no invisible wall matching a 32- or 64-unit drawn piece. Those pieces use 497/498 turned into the rock in 32-unit strips. Their front edges retain the original jagged offsets; their inward extension occupies the rock side. This supplies the requested barrier using existing shapes. Default two-course output remains unchanged.

No merge, push, installation, or ScummVM launch occurred. Main-checkout edits were left untouched. Game data entries are symlinks to the main checkout; built artifacts are private worktree copies.

# Retail visual calibration

Measured on 1 November 2026 against pristine retail FIXED, art, animation, and physics. Retail towns have zero walkable-black cells. The retail southeast cave has 263 black-floor cells out of 3,848 reached cells (6.83%), and its sampled frames reach 90.63% black. Every populated sample includes positions where a walk or stand pose is completely hidden. Pristine Map 22 contains zero FIXED records, so its distributions are unavailable.

## Inputs and measurement

Both audits ran for Maps 3, 5, 8, and 22 with `--fixed shared/data/u8-install/STATIC/FIXED.DAT.bak --retail-art`. The latter selects `TYPEFLAG.DAT.bak`, `U8SHAPES.FLX.bak`, and `ANIM.DAT.bak`. GLOB and palette inputs are the shared retail files. The pristine FIXED SHA-256 is `2ef821057eab275042818f984ff83e0d5e7680b5c035fd88bb837ead13f22705`; each audit JSON records every input and audit-source hash.

| Map | Arrival seed (x, y, z) | Reached standing cells | Frame and visibility samples |
|---|---|---:|---:|
| 3 | (11532,1980,48), retail target 0 | 75,042 | 4,594 |
| 5 | (7424,11264,48), retail target 1 | 139,770 | 8,589 |
| 8 | (31583,19135,0), retail target 0, southeast cave | 3,848 | 199 |
| 22 | None, empty map | 0 | 0 |

`exact_reach` supplies the 32-unit dry flood used by `test_monster_eggs.dry_flood`. Frame and visibility cameras use a 128-unit subsample of that same flood. Walkable black checks **every reached 32-unit standing cell**, including cells between frame cameras. These are connected standing regions from the listed seeds; teleports, jumps, other disconnected cave regions, and dynamic NONFIXED items are outside this sample. Town samples include reachable interiors and climbable objects. Map 8's sample covers the southeast cave; it does not establish a baseline for the northern spitter corridor or Mythran's island.

Walkable black probes the Avatar's bottom centre, at (x-32,y-32), on the supporting floor. A floor-only paint retains solid, land, and roof surfaces at or below the standing level, including drawn ground visible through furniture sprites. Foreground walls and overhead slabs cannot contaminate this probe. An unpainted or pure-black pixel counts; a top painted floor owner of 564:2, 35:10, or shape 334 also counts. This is a point probe per standing cell, with tolerance zero. The flood retains its existing requirement for a real supporting surface; floorless walks beyond that flood need `exact_reach.walk_off` checks in the later map slices.

Frame black share is the fraction of all 640x400 pixels that are unpainted or pure black, with every shape included. The old `void_share` remains a separate unpainted and specified-filler diagnostic. `black_share` remains an alias for frame black share. Near-black RGB channels at most eight remain available for screenshot comparison.

Avatar visibility evaluates all 72 distinct walk and stand poses across eight headings, with the retail animation and the existing roof cut and sorter. The tables use the minimum visible fraction across those poses at each sampled position.

## Retail distributions

Percentages below are measured fractions multiplied by 100. P05 and P95 are the fifth and 95th percentiles across sampled cameras.

| Map | Frame black min | Mean | P05 | Median | P95 | Max |
|---|---:|---:|---:|---:|---:|---:|
| 3 | 0.00% | 6.26% | 0.00% | 0.55% | 37.72% | 59.25% |
| 5 | 0.00% | 4.46% | 0.00% | 0.38% | 30.55% | 61.77% |
| 8 | 17.02% | 46.30% | 19.00% | 45.48% | 76.09% | 90.63% |
| 22 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |

A 10% frame ceiling fails 911 of 4,594 town cameras on Map 3, 1,280 of 8,589 on Map 5, and all 199 cave cameras. The two black metrics therefore require independent acceptance rules.

| Map | Walkable-black cells / reached cells | Share | Zero-tolerance result |
|---|---:|---:|---|
| 3 | 0 / 75,042 | 0.00% | Pass |
| 5 | 0 / 139,770 | 0.00% | Pass |
| 8 | 263 / 3,848 | 6.83% | Fail |
| 22 | 0 / 0 | Unavailable | Unavailable |

All 263 Map 8 failures have a top painted floor owner of 564:2. Zero-tolerance walkable black exceeds this retail cave's standard. The report preserves that result.

| Map | Worst-pose visible min | Mean | P05 | Median | P95 | Max |
|---|---:|---:|---:|---:|---:|---:|
| 3 | 0.00% | 78.34% | 0.00% | 100.00% | 100.00% | 100.00% |
| 5 | 0.00% | 82.91% | 0.40% | 100.00% | 100.00% | 100.00% |
| 8 | 0.00% | 43.25% | 0.00% | 26.55% | 100.00% | 100.00% |
| 22 | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |

| Map | Cells with a pose below 50% visible | Cells with a completely hidden pose | Median of each cell's median-pose visibility |
|---|---:|---:|---:|
| 3 | 949 / 4,594 (20.66%) | 272 / 4,594 (5.92%) | 100.00% |
| 5 | 1,407 / 8,589 (16.38%) | 397 / 8,589 (4.62%) | 100.00% |
| 8 | 115 / 199 (57.79%) | 72 / 199 (36.18%) | 38.45% |
| 22 | Unavailable | Unavailable | Unavailable |

A requirement for at least 50% visibility at every standing cell fails all three populated retail samples. A stricter LV requirement at quest interactions remains a separate design choice.

## Proposed acceptance

These regional distribution thresholds pass the measured retail samples, with rounded slack:

| Metric | Town and built exterior, Maps 3 and 5 baseline | Cave, Map 8 southeast baseline |
|---|---:|---:|
| Mean frame black share | At most 7% | At most 47% |
| P95 frame black share | At most 38% | At most 77% |
| Maximum frame black share | At most 62% | At most 91% |
| Cells below 50% worst-pose visibility | At most 21% | At most 58% |
| Cells with a completely hidden pose | At most 6% | At most 37% |
| Median worst-pose visibility | At least 100% | At least 25% |

I would use these as provisional regional regression limits. A map-wide average can conceal an individual missing floor or an obscured quest interaction, so the ranked cells still require review. The samples supply no retail cloud-city analogue; Map 17 needs shot-based acceptance. Other cave regions need their own matched-route baseline before these numbers become a broader cave policy.

**Walkable black remains zero on LV-authored and LV-exposed routes.** The retail comparator can pass a zero-new-black regression rule with an explicit coordinate allow-list of the 263 inherited cells. Its raw walkable-black result remains 263 and fails strict zero. LV cuts that expose additional retail black receive no inherited allowance. A uniform absolute-zero rule and a passing pristine Map 8 result cannot both be claimed from these measurements.

## Record budgets

Counts include records before visibility, containment, or editor filtering. Expansion uses `expand_globs`, which retains an empty glob egg as a marker. Raw FIXED count measures permanent map-load records; expanded count measures the whole-map replacement expansion. Each summary gives both fractions of the requested 32,500-object budget and both headroom values.

| Retail map | FIXED records | Raw budget used | Raw headroom | Items after expansion | Expanded budget used |
|---|---:|---:|---:|---:|---:|
| 3 | 1,835 | 5.65% | 30,665 | 19,900 | 61.23% |
| 5 | 2,691 | 8.28% | 29,809 | 19,694 | 60.60% |
| 8 | 4,306 | 13.25% | 28,194 | 28,235 | 86.88% |
| 22 | 0 | 0.00% | 32,500 | 0 | 0.00% |

The same read-only counts on the current LV build are:

| LV map | FIXED records | Raw budget used | Raw headroom | Items after expansion | Expanded budget used |
|---|---:|---:|---:|---:|---:|
| 8 | 4,371 | 13.45% | 28,129 | 28,244 | 86.90% |
| 9 | 1,019 | 3.14% | 31,481 | 1,349 | 4.15% |
| 10 | 20,559 | 63.26% | 11,941 | 37,554 | 115.55% |
| 11 | 9,516 | 29.28% | 22,984 | 17,826 | 54.85% |
| 13 | 6,447 | 19.84% | 26,053 | 7,692 | 23.67% |
| 17 | 5,481 | 16.86% | 27,019 | 5,481 | 16.86% |
| 18 | 1,737 | 5.34% | 30,763 | 2,517 | 7.74% |
| 39 | 5,108 | 15.72% | 27,392 | 29,066 | 89.43% |

Map 10's whole-map expansion exceeds 32,500 by 5,054 items. Glob tiles are temporary fast-area content, so that total alone cannot establish simultaneous object-ID exhaustion. Permanent FIXED records remain allocated while the fast area adds glob items, actors, and other objects. A live peak requires separate measurement; these counts supply an early budget warning. Replacing Map 10's 2,426 large plates with four tiles each would raise its raw count from 20,559 to 27,837 (85.65% of 32,500), before dressing.

## Capture verification and reproduction

The one-stop test used display `:88`, runtime directory `/tmp/claude-1000/tc-test`, and the text-console binary. `MainActor::teleport` returns false from the debugger handler and detaches itself. The capture runner sends it once through `cmd` while attached, waits for settling, explicitly attaches, and uses `dbg ObjectManager::objectInfo 1` for the fresh position reply. The screenshot is taken with the text console still attached and the world paused.

The m13-26 test requested Map 13 at (4175,4863,96). The fresh reply recorded Map zero at (15967,19711,0), producing `at` and `landed: false` in `/tmp/claude-1000/tc-test/captures/captures.json`. This verifies position reporting and detects the failed landing. It leaves the cause of that landing unresolved. `session.sh status` subsequently reported display `:88` down with no Xvfb or ScummVM process. A landed skull-ring capture remains a prerequisite for a geometry diagnosis.

Both audit commands used this form for each requested map; Map 8 additionally used `--arrival 31583 19135 0`:

```bash
python3 -B agents/map-populator/src/void_audit.py 3 \
  --fixed shared/data/u8-install/STATIC/FIXED.DAT.bak --retail-art \
  --step 128 --workers 4 --out /tmp/claude-1000/retail-calibration
python3 -B agents/map-populator/src/avatar_visibility.py 3 \
  --fixed shared/data/u8-install/STATIC/FIXED.DAT.bak --retail-art \
  --step 128 --workers 4 --out /tmp/claude-1000/retail-calibration
```

All eight audit invocations completed with exit zero. Empty Map 22 emits `status: empty_map`, null distributions, and header-only rankings. Outputs under `/tmp/claude-1000/retail-calibration` include full JSON, summaries, frame rankings, walkable-cell rankings, and heatmaps. Primary frame rankings contain both black metrics. The additional 32-unit walkable rankings leave frame share blank where no camera was sampled.

`python3 -B /tmp/claude-1000/check-visual-audits.py` passed eight focused checks, including separation of drawn floor from a frame with more than 90% black, the three named floor kinds, overhead cover, furniture transparency, and fresh position parsing. `python3 -B /tmp/lv-vq-backlog/validate_backlog.py docs/research/2026-11-01-visual-pass` passed source accounting and the updated retail and shot fields. Map content, merged artifacts, and vignette scores were unchanged; no build or commit was performed.

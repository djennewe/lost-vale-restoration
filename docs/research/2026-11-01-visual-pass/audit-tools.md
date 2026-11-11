# Offline audit baseline, 1 November 2026

Both tools ran on Maps 9, 10, 11, 13, 17, and 18 at step 32: 640,028 reachable
positions each. Avatar visibility falls below 50% in at least one pose at
47,683 positions; 27,210 positions hide him completely in at least one pose.
Outputs are in `/tmp/claude-1000/audits/`.

Capture validation found agreement at all 10 visibility stops. Rendered
near-black shares agree with all 13 captures within 0.14 percentage points.
The requested comparison of specified-filler void with capture near-black
exceeds two percentage points at three stops. Those quantities differ:
capture near-black includes dark terrain and other black shapes. The table
below preserves that discrepancy. Thresholds and filler definitions remain
fixed.

## Commands and outputs

The following commands ran for each map, using 12 worker processes on this
14-processor host:

```bash
python3 -B agents/map-populator/src/void_audit.py MAP \
  --step 32 --out /tmp/claude-1000/audits \
  --validate-tour ~/projects/lv-art-review/tour
python3 -B agents/map-populator/src/avatar_visibility.py MAP \
  --step 32 --out /tmp/claude-1000/audits \
  --validate-tour ~/projects/lv-art-review/tour
```

Each map has `void-mapNN.json`, a PNG heatmap, a ranked TSV, and a summary
JSON. Each cell records unpainted share, specified-filler black share,
other black share, total black share, near-black share, and the five largest
four-connected void regions, with pixel counts and half-open screen boxes.
The visibility files use the `avatar-mapNN` prefix: cell JSON, a PNG
heatmap, summaries, and `-quest-low.json` and `-quest-low.tsv` lists.
JSON shares are fractions. Heatmaps show the worst standing level at each
sampled XY position, with x increasing east and y increasing south.

The complete run took 708 s, about 12 minutes, including capture comparisons
and output writes. No ScummVM process ran, no artifacts were rebuilt, and no
commit was created. Repository writes comprise the two scripts and this note.

## Reach, rendering, and limits

The flood reuses `test_monster_eggs.dry_flood`, `ARRIVAL`, and `FLOOD_STEP`
through their parsed declarations. Importing that test would execute its
suite. The flood uses the built FIXED and TYPEFLAG, expands retail GLOB.FLX,
excludes SEA tiles, and retains ExactReach's half-open box arithmetic. Larger
`--step` values subsample the same 32-unit flood; they preserve connectivity.

Painting uses `Painter.built()` and its existing sorter. Fixed records
precede expanded glob tiles within each chunk; the Avatar enters first in
his chunk. Contained, equipped, invisible, and editor records are excluded.
The 640×400 projection uses C integer division and a camera at Avatar z + 20.
`ItemSorter.roof_z` supplies CameraProcess's 64×64×16 roof probe; the cut
retains SI_DRAW items above the roof limit.

The void scan caches sorted, painted camera atlases by world chunk,
standing z, and roof limit. The first, middle, and final camera in each
chunk are checked pixel-for-pixel against the original single-frame
painter. Any discrepancy triggers direct painting for every camera in that
chunk. Paint cycles also trigger direct painting. The baseline checked
9,894 cameras across 3,322 chunk scenes and used direct painting in 107
chunks. These checks sample atlas equivalence; cameras elsewhere in an
accepted chunk use its cached image.

Visibility evaluates all 72 distinct walk and stand frame/mirror pairs,
nine per heading, read by `avatar_mover.sprite_frames` from built ANIM.DAT.
Frames with identical sorter intersection and occlusion predicates share a
sort. Coverage accumulates opaque sprite masks after the Avatar in the
final order; whole-item culling yields zero visibility. The denominator is
the pose's full opaque pixel count.

Quest-route output uses **all reachable cells**, the requested fallback.
`test_route_reach` executes tests on import and exposes target coordinates
without importable leg paths. The JSON and TSV label this fallback. These
counts therefore include cells beyond quest routes.

Reachability models the full-size Avatar walking on the shipped geometry.
It retains puzzle blockers, excludes disconnected areas, and omits Map 18's
sanctum beyond the Tiny Tar crack. Runtime puzzle changes, the shrunken
Avatar, jumping, moving actors, and the tour's wandering ghost are outside
this baseline. Void atlas frames contain the map alone; capture checks add
a standing Avatar. The visibility audit always adds him.

## Map baseline

Void means unpainted pixels plus pure-black pixels owned by 564:2 or 35:10.
Black pixels owned by other shapes have their own field. Visibility counts
use the minimum across all 72 poses. Times include validation when requested.

| Map | Reached positions | Mean void | Median void | Maximum void | Frames above 10% void | Visibility below 50% | Completely hidden | Void time | Visibility time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 9 | 5,908 | 26.00% | 24.51% | 67.86% | 4,799 | 1,639 | 868 | 8.58 s | 9.20 s |
| 10 | 398,712 | 2.35% | 0.00% | 57.00% | 35,185 | 24,067 | 14,703 | 271.04 s | 49.03 s |
| 11 | 140,466 | 8.57% | 2.14% | 63.61% | 44,092 | 18,412 | 10,535 | 117.36 s | 20.65 s |
| 13 | 20,686 | 9.97% | 1.10% | 65.25% | 6,726 | 702 | 221 | 46.16 s | 7.24 s |
| 17 | 62,417 | 13.33% | 3.92% | 78.84% | 24,694 | 934 | 9 | 135.81 s | 9.28 s |
| 18 | 11,839 | 18.13% | 14.87% | 69.43% | 7,229 | 1,929 | 874 | 13.31 s | 16.30 s |

## Void capture comparison

Capture near-black means every RGB channel is at most eight, on all 256,000
game pixels. Offline near-black uses the same rule and the retail palette.
`black_share` separately measures unpainted pixels and all pure-black paint.
No terrain, interface pixels, or image borders were masked out.

The delta column compares offline and capture near-black, in percentage
points. The specified-filler void column remains the audit's primary metric.

| Stop | Specified-filler void | Offline near-black | Capture near-black | Delta |
|---|---:|---:|---:|---:|
| m09-14 | 53.77% | 57.54% | 57.55% | -0.01 |
| m09-16 | 48.05% | 51.40% | 51.42% | -0.02 |
| m09-17 | 43.45% | 45.26% | 45.23% | 0.03 |
| m10b-52 | 39.81% | 40.51% | 40.53% | -0.02 |
| m10b-64 | 24.81% | 25.00% | 25.13% | -0.14 |
| m11-49 | 32.82% | 37.05% | 37.07% | -0.02 |
| m13-02 | 11.13% | 12.32% | 12.33% | -0.01 |
| m13-03 | 29.97% | 30.14% | 30.15% | -0.01 |
| m17-01 | 9.52% | 9.60% | 9.61% | -0.01 |
| m17-11 | 58.43% | 58.50% | 58.50% | 0.00 |
| m18-12 | 27.36% | 27.48% | 27.50% | -0.02 |
| m18-15 | 24.57% | 25.10% | 25.13% | -0.02 |
| m18-16 | 15.84% | 16.39% | 16.41% | -0.02 |

The strict void-to-capture differences at m09-14, m09-16, and m11-49 are
3.78, 3.37, and 4.25 percentage points. Owner inspection explains them:
m09-14 has 6,630 pure-black pixels from other shapes, including 334, 31,
and 393, and 3,022 dark, nonzero pixels. At m11-49, 10,818 dark, nonzero
pixels account for 4.23 percentage points, including terrain shapes 242 and
26. Broadening the filler set would change the requested metric. The
renderer comparison supports keeping those measurements separate.

Each map's `-validation.json` records these values. The 13
`STOP-void-validation.png` files show capture on the left and offline paint
on the right. `black-provenance.json` records the Map 9 owner inspection.

## Avatar capture comparison

Reviewer labels are qualitative observations of the recorded screenshots.
The audit predicts hidden when its minimum visible fraction is below 50%.
All eight hidden stops and both clean stops agree.

| Stop | Capture verdict | Minimum visible | Median visible | Agreement |
|---|---|---:|---:|---|
| m09-16 | Hidden | 0.00% | 8.94% | Yes |
| m09-17 | Hidden | 0.00% | 0.00% | Yes |
| m10b-52 | Hidden | 0.00% | 0.00% | Yes |
| m10b-64 | Hidden | 2.56% | 8.34% | Yes |
| m11-49 | Hidden | 5.66% | 12.60% | Yes |
| m13-02 | Clean | 100.00% | 100.00% | Yes |
| m17-01 | Clean | 100.00% | 100.00% | Yes |
| m18-12 | Hidden | 0.00% | 0.00% | Yes |
| m18-15 | Hidden | 2.29% | 8.25% | Yes |
| m18-16 | Hidden | 0.00% | 0.00% | Yes |

All 720 poses at those stops also matched the original, ungrouped,
640×400 `Painter.paint(owner=True)` measurement exactly. Twelve additional
cells, comprising the highest reachable level and a deterministic random
cell on every map, added 864 exact pose comparisons. Results are in
`avatar-mapNN-validation.json` and `optimization-checks.json`.

Additional inline checks compared region boxes with a pixel flood fill on
100 randomized masks and compared the indexed roof lookup with global
`roof_z` at 30 cells per map. Every comparison agreed.

## Artifact identity

The output JSON records full SHA-256 hashes for the four built inputs,
palette, and reach-test sources. The built inputs used here were:

| Artifact | SHA-256 |
|---|---|
| FIXED.DAT | `fc92ee5f03957f4fc06323f1da3a4cde15eeff4ab9cb541695bbcef41ce06e32` |
| U8SHAPES.FLX | `2b274856ab81f291c432df1bb60e9e2bf77e1c4c82edbd029f83dcdc85db1711` |
| TYPEFLAG.DAT | `e25d7224d1020647150b34f5b0c0a8527b8267ce5df1dfb5e452599d31cdd44d` |
| ANIM.DAT | `97ae5fc9ddaa6ef515427103264a3095a6d42776ac51e530954fb4846b4d0443` |

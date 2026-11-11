# Map nine independent verification

Verified on 9 November 2026 (America/Chicago) against frozen final artifacts on `wt/vq4-m09`.

Final FIXED SHA-256: `872be156468dca321a7859ec111c963c0cb9d3bf2acb6c9637bf561f0ea19cd2`.

Baseline FIXED: `/tmp/claude-1000/vq4-m09/baseline-run/shared/build/FIXED.DAT`.

Final GLOB SHA-256: `aabc1ad36f42c6bdd01cfcb7271f0765983a9914489d62a96a9bcb5e1d7c88ca`, identical to the slice baseline. Both comparisons therefore expand the same 60 registered LV globs and retail globs.

## Verdicts

- PASS: three explicit-coordinate `Site.set_piece` compositions. `build_map_09.py:534` defines the coordinates, and line 563 submits each composition through the existing exclusions. Final manifest ledger contains Broken funerary vessels, eight records; Fungus at the seep, 27 records; and Masons abandoned threshold, five records. Structural provenance contains all 40 added records and zero packed eggs.
- PASS: frozen quest data. All seven Map nine pin records, six event or teleport eggs, four loose quest objects, and 178 anti-climb records retain their complete serialized bytes. All 174 rows across `map_pins.json` remain identical to HEAD. Its generated FIXED hash prefix is the sole metadata change.
- PASS: protected screen10. Independent `vignette_built_window.window('screen10', actors=True, fixed=...)` comparison gives exactly `89.51725310215876%` for both artifacts, with zero unpainted non-black pixels in either window.
- PASS: five convex fills. Added shape 301 frame zero records sit at z=104 at `(13183,12927)`, `(13311,13055)`, `(13439,13311)`, `(13951,11903)`, and `(13951,12031)`. The dangerous south shelf, cells 105 through 109 of row 103, remains excluded (`build_map_09.py:302`). Common 128-unit visibility samples contain zero newly fully hidden positions and zero newly below-half positions.
- PASS for walking: added positive LAND tops remain unreachable. An eight-unit `ExactReach` flood from `(13696,14208,0)` reaches zero standing positions on every added positive LAND top, including all five caps and all 11 new 16-unit props. Jumping and movable-prop arrangements require runtime evidence.
- PASS: the existing quest route remains connected. Both floods reach trigger 203, trigger 200, and the guardian dais approach. The z=56 dais retains exactly 431 reached lattice positions. Levels 16 through 64 retain their previous reached counts.
- PASS: stand-ins removed. Expanded shape counts change as follows: 186, six to zero; 796, three to zero; 66, three to zero.
- PASS: whole-map and regional dressing targets. `python3 -B agents/map-populator/src/test_dressing.py 9 --strict` exits zero: `raw 1578, expanded 1578, per cell 2.783`, `0 failures; 0 target failures`.
- PASS: ordinary visual ratchets. Independent contract checks and `test_visual_quality.measure` return zero pin violations. Measured values include 66 leg cells below half visibility, 0.08 sampled below-half share, zero hidden share at the pinned spacing, and `0.19760770089285715` mean frame black share.
- PARTIAL: strict visual phase exit. Its target requires zero leg cells below half visibility; 66 remain, reduced from 68. Ordinary ratchets pass with this inherited debt.
- PASS: source isolation. `git diff --name-only HEAD` contains the builder, its dressing and visual pins, generated map-pin hash metadata, canonical artifact hashes, and manifest. Shared Python modules and tests have no edits. Comparing every FIXED map payload finds only Map nine changed.
- PASS: loose-record alternative. A compiler-first import probe builds 1578 records and zero glob eggs while `register_packed` and `lv_globs.build` are replaced with failure sentinels. Neither sentinel fires. The final manifest retains the original 60 glob definitions. Record count stays within the 1800-record phase ceiling.
- PASS: canonical hashes. `sha256sum -c ARTIFACTS.sha256` from `shared/build` reports OK for all six artifacts.
- PARTIAL: full estate and full recorded build. The author runs these checks. I read the completed full-build report, which contains the expected EALOGO and TJORVI compilation failures, and its recorded final hashes. I skipped duplicate full builds and estate runs at the author's explicit request; the fresh final estate was still running when this report was written.
- NOT DEMONSTRATED independently: installed-game behavior, fresh-world walking, adversarial jump attempts, and after-capture appearance. The author owns installation and runtime captures. I launched no ScummVM process and installed no files.

## Evidence

The geometry comparison used built records, expanded through `GlobReader`, with these parameters:

```python
before = MapArchive(baseline).get_map_items(9)
after = MapArchive(final).get_map_items(9)
roi = (12000, 11200, 15360, 17200)
er = ExactReach(items, shapes, roi, step=8)
reach, seeded = er.flood([(13696, 14208, 0)])
```

Full-byte `Counter` comparisons operate on `item.to_bytes()`. Anti-climb selection uses shapes 497, 498, 501, and 846; eggs use 73, 500, and 508; loose quest objects use 574, 613, 529, and 420. Every frozen selection reports zero missing and zero added records. Added LAND top checks intersect the final reached mask with each added item's half-open bottom-centre support footprint.

| Measurement | Baseline | Final |
|---|---:|---:|
| Raw records | 1226 | 1578 |
| Expanded records | 1556 | 1578 |
| Walking positions reached | 91945 | 91266 |
| z=0 positions reached | 86686 | 85467 |
| z=8 positions reached | 4540 | 5080 |
| z=56 positions reached | 431 | 431 |
| 128-unit visibility samples | 335 | 334 |
| Below-half visibility samples | 54 | 53 |
| Fully hidden visibility samples | 6 | 6 |

The common 128-unit sample set contains 318 positions. The remaining samples differ because dressing changes the dry flood. This comparison establishes the stated sampled result. It leaves visibility between sample positions unmeasured.

| Region | Props per 100 cells | Largest material share | Target failures |
|---|---:|---:|---:|
| Guardian chamber | 7.441860 | 0.539535 | 0 |
| Hall | 8.984375 | 0.433594 | 0 |
| Passage | 7.291667 | 0.479167 | 0 |
| Whole | 8.112875 | 0.409171 | 0 |

Whole-map bare share is `0.010582010582010581`; period excess is `0.148546799826032`. Final `Site.pack()` still executes `_budgets()`, records the composition ledger, and emits structural provenance after `protected_raw` preserves loose records.

The compiler-first probe ran this sequence with metadata writes intercepted in memory:

```python
sys.path.insert(0, 'agents/usecode-compiler/src')
import u8_flex
sys.path.insert(0, 'agents/map-populator/src')
import build_map_09, lv_globs
with patch.object(lv_globs, 'register_packed', side_effect=AssertionError), \
     patch.object(lv_globs, 'build', side_effect=AssertionError), \
     patch.object(Path, 'write_text', return_value=0):
    items = build_map_09.build_map_09()
```

Output identifies the compiler's `u8_flex.py`, then reports `BUILDER 1578 GLOBS 0`. No game or artifact files were written by this probe.

## Failures resolved during verification

The first frozen candidate reduced worst-pose visibility at `(13215,14111,0)` from 1.0 to `0.48204419889502764`. Deleting either nearby root isolated the cause: removing shape 321 gave `0.6706666666666666`, and removing shape 322 gave `0.713855421686747`. Removing the stump left the result unchanged.

The author moved shape 322 from `(13248,14080)` to `(13184,14080)`. An in-memory placement probe returned `Site.reason = None`, and the final built artifact gives `0.6139240506329114` at the affected sample. Final comparison finds zero new below-half samples among all 318 common positions.

The author also replaced packed records after review found an archive-import collision during pin derivation. The final loose-record compiler-first probe above exercises that failure path with glob-writing calls configured to fail immediately.

## Findings outside the brief

1. Strict visual phase exit remains incomplete because of 66 inherited low-visibility quest-band cells. The final ordinary visual result explicitly reports that debt.
2. `main` advanced after the worktree's HEAD, `4d3d514`. Direct comparison against current `main` also includes inherited HANDOFF and phase4-direction differences. The author's working edits remain confined to the owned slice and generated metadata.
3. Fungus at the seep includes seven secondary wall groups across the hall. The three ledger entries represent three regional compositions; the hall composition distributes secondary groups across its region.

## Disk changes

I wrote only `docs/research/2026-11-01-visual-pass/p4-m09/verifier.md`. Checks used `python3 -B`, read-only artifact inspection, temporary test directories, and intercepted metadata writes. I performed no source edit, rebuild, installation, main-checkout write, or ScummVM launch.

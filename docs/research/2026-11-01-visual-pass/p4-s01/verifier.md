# Shared slice 0.1 verification

Date: 9 November 2026. Worktree: `~/projects/lv-wt-vq4-s01`. Branch: `wt/vq4-s01`. Compared with main `01710d14` and its existing build artifacts.

## Verdicts

- PASS: forest prefabs occupy appended slots 3216 through 3219. Every member accepts clear grass and refuses an external colliding oak. Existing `GRASS_FOREST` stays `(124, 125, 891, 1013, 1014, 13)`. The new family resolves through `prefab_family('grass_wood_')`.
- PASS: moat prefabs occupy slots 3220 through 3227. Independent synthetic placement retained grass at z=48 and real water records at z=0 byte for byte. Both banks avoided x=13568 through 14079, added no LAND or SOLID boxes, refused z=0 grass, and emitted eight decorative records per bank in the test span.
- PASS: occupied-chunk placement preserves original records, omits prefab floors, validates each prop, and rejects missing support, protected pins, hatch areas, quest bands, and new standing tops. Evidence: `test_dressing.py` contract suite passed in `s01-estate.log`; implementation at `Site.place_prefab`.
- PASS: stride evidence stays absent below six same-shape props. The contract suite checks zero, five, and six instances, and preserves measured ratchets. Recursive JSON comparison with main found exactly 17 removed `props.stride_share` fields, every value `['max', 0.0]`, with no other pin changes.
- PASS: new shape and TYPEFLAG rows are exactly 898 through 904. `test_art_props.py` passed all 777 checks against built artifacts. Flat cobbles retain donor 71 physics at zero height. Rubble and bones retain their footpads with LAND and SOLID clear. All 161 crest frames contain opaque pixels.
- PASS: crest selection protects shot windows and every walking and standing pose supplied by `avatar_visibility.Poses`, including heading and flip variants. Independent checks covered all 23 retail source frames: a covering shot window refused every placement atomically; every accepted variant preserved the Tiny actor's visible pixels at a synthetic quest-band point. Additional adversarial controls now reject contained-record cover and ambiguous paint ordering, and preserve inherited direct cover.
- PASS: source and artifact boundaries are preserved. Direct byte comparison found `FIXED.DAT`, `ANIM.DAT`, and `EUSECODE.FLX` identical to main. Every old GLOB payload, slots zero through 3215, stayed identical. Existing manifest glob pins stayed identical. Shape and TYPEFLAG differences were exactly rows 898 through 904.
- PARTIAL: marker expectation 212 changes from frame zero to frame nine at the requested position. The unchanged Map 8 builder emits frame zero. Route verification therefore has the expected outstanding failure until the Map 8 slice changes the builder.
- FAIL: full estate completed with 55 of 58 files passing. `test_png2shape.py` failed four assertions owing to its newly occupied hardcoded donor 900; `test_route_reach.py` failed the expected marker-212 assertion; `test_integration_state.py` failed the allowed shared-install mismatch. The png2shape regression remains outstanding pending ownership approval.
- PASS: post-estate `tools/build_artifacts.sh` completed with exit zero, without `--record`. All six artifacts matched their canonical hashes. A fresh byte comparison after this build reconfirmed every main and old-row preservation boundary.
- PASS: final Codex review completed with no actionable regressions. An earlier unrestricted pass reported the expected Map 8 marker mismatch as P2. The initial restricted attempt failed with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`; subsequent unrestricted retries inspected the source and tests.
- PASS: `git diff --check` returned exit zero.
- NOT DEMONSTRATED: in-engine appearance and runtime dispatch. Douglas explicitly forbids ScummVM and shared installation for this slice. Offline forest and moat context images were inspected; they establish sprite arrangement and bank context only.

## Failures

The route test now expects shape 71, frame nine at `(20639, 3967, 0)`. The shipped Map 8 record remains shape 71, frame zero. This split is explicitly required by the slice ownership rules. No Map 8 builder was edited.

The unrestricted review reports:

```text
[P2] Synchronize the marker expectation with the Map 8 builder
FAIL trigger 212 (map 8): its marker, shape 71 frame 9, is at (20639,3967,0)
```

Cause confidence: high. Source diff, builder inspection, and expanded FIXED geometry agree.

The png2shape negative control assumes donor 900 is filler. This slice allocates row 900, so the command unexpectedly succeeds and consumes temporary free slot 861. The subsequent intended injection then fails because that slot is occupied:

```text
FAIL filler donor exits 1: rc=0
ERROR: slot 861 is not empty ... refusing to overwrite an existing shape
FAIL TYPEFLAG inherited the donor's flags: ['SI_FIXED']
FAIL TYPEFLAG took the authored footpad: (3,4,1)
```

Cause confidence: high. `test_png2shape.py:170` selects donor 900, and the source diff assigns decorative bones to that row. The fixture already discovers a free target slot dynamically, so using the same free slot for this donor control is a concrete correction. This test is outside the slice's explicit owned file list.

## Evidence commands and results

`tools/run_all_tests.sh`, launched by the author and observed by the verifier, completed with 55 of 58 test files passing in `shared/build/s01-estate.log`. `test_art_props.py` passed all 777 checks. The final targeted `python3 agents/map-populator/src/test_dressing.py` rerun, after both crest fixes, completed with zero failures and 104 existing target failures in `shared/build/s01-dressing.log`.

The estate failures are:

```text
test_png2shape.py: FAILED: 38 passed, 4 failed
test_route_reach.py: FAILED: 165 passed, 1 failed
test_integration_state.py: FAILED: 9 passed, 1 failed, 4 skipped
OVERALL: FAIL: 3/58 test files failed
```

Full temporary logs remain at `/tmp/lv-tests.dAKvkX`. The route failure is the requested marker-212 split. The integration failure compares the shared installed U8SHAPES, TYPEFLAG, and GLOB files with this worktree's new rows; installation is prohibited for this slice.

`tools/build_artifacts.sh --record`, completed before verification, records 57 files compiled, 55 successful, and two failed. The failures are the documented allowlist pair, EALOGO.UNK and TJORVI.UNK.

`~/projects/lv-wt-vq4-s01/tools/build_artifacts.sh > ~/projects/lv-wt-vq4-s01/shared/build/s01-verifier-build.log 2>&1` ran after the estate and source review completed. Exit zero. The Compilation Report remained 57 compiled, 55 successful, and the same allowlist pair failed. Final output:

```text
TYPEFLAG.DAT OK
U8SHAPES.FLX OK
ANIM.DAT OK
EUSECODE.FLX OK
FIXED.DAT OK
GLOB.FLX OK
RESULT: PASS: all 6 artifacts match the canonical hashes
```

GLOB SHA-256: `c789b4a5f201b8c5033cec01c9b8fe083881f5f8f3319ff35da697acfed633bc`.

Post-build independent comparisons again found FIXED, ANIM, and EUSECODE byte-identical to main, all old 3216 GLOB payloads preserved, and shape and TYPEFLAG changes confined to 898 through 904.

Independent Python checks loaded `u8_flex.FlexArchive` for payload comparison, compared TYPEFLAG in 8-byte rows, and recursively compared JSON pins against `git show main:<path>`. Results:

```text
FIXED.DAT IDENTICAL True
ANIM.DAT IDENTICAL True
EUSECODE.FLX IDENTICAL True
U8SHAPES.FLX COUNTS 2048 2048 OLD CHANGED [898, 899, 900, 901, 902, 903, 904]
GLOB.FLX COUNTS 3216 3228 OLD CHANGED []
TYPEFLAG sizes 16384 16384 CHANGED ROWS [898, 899, 900, 901, 902, 903, 904]
OLD GLOB PINS CHANGED []
```

Independent placement checks used `Site` with isolated exclusions, genuine built shape metadata, actual glob expansion, and `ItemSorter.overdrawn`. Output:

```text
PASS all four forest members accept on clear grass and reject an external oak collision
PASS both moat banks preserve grass z48 and actual water z0 records, avoid strip13568..14079, add no standing surface, and refuse z0 grass
PASS all23 source crest frames reject a covering shot window atomically
PASS accepted variants from all23 source frames preserve Tiny actor visibility at a synthetic quest-band point
PASS walking pose, contained record, ambiguous ordering, and inherited cover controls
Independent adversarial checks completed
```

The forest contact sheet shows asymmetric tree and root groups with differing anchors. The moat context image shows retained grass banks around a clear channel. These images were read from `p4-s01/forest-prefabs.png` and `p4-s01/moat-context.png`.

## Findings outside the brief

1. Resolved: contained records counted as existing actor cover in the first all-pose implementation. At cap `(4047, 4223, 8)`, adding an identical existing record with flag 8 changed rejection from true to false. The author added `MapItem.FLG_CONTAINED` to the cover exclusion and a permanent negative control. Independent rerun passed.
2. Resolved: footprint ordering missed sprite overhang. A cap at `(4095, 4255, 8)` obscured three shape-one frame-zero pixels at `(4095, 4095, 0)` in `Painter.built().order`, while the original guard returned false. The author now checks every candidate opaque pixel intersection conservatively, including ambiguous footprint ordering, and added the exact negative control. Independent rerun passed.
3. Outstanding: the estate's `test_png2shape.py` assumes donor 900 is unused. New shape 900 makes that negative control succeed and contaminates its temporary fixture, producing four failures. This test lies outside the explicit slice ownership list; the author has requested approval for a concrete dynamic-slot correction.
4. Runtime sorting and appearance remain untested under Douglas's explicit ScummVM prohibition. Existing cover uses direct sorter dependencies; ambiguous candidate intersections are conservatively refused.

## Disk changes

The verifier wrote this report and `shared/build/s01-verifier-build.log`.

The full build regenerated these worktree-local files: `TYPEFLAG.DAT`, `U8SHAPES.FLX`, `ANIM.DAT`, `EUSECODE.FLX`, `FIXED.DAT`, `GLOB.FLX`, `lv_manifest.json`, and `map_manifest.json`. The six merged artifacts remain untracked. The build used private worktree outputs and the shared read-only game-data source.

No source, builder, main checkout, installed game, or image was written by the verifier.

# Art phase three verification

The corrected art passes independent art, geometry, background, window, and capture checks. The final estate passes 56 of 57 test files, with only the permitted integration-state mismatch against the unchanged main install. The repeated supported rebuild reproduces all five canonical hashes. This report replaces the earlier check that measured black masks against visible window pixels.

Verification uses FIXED `d6ea352da90954c60306be898d46e13a1b8ba023646e0872d9ee2798d6bfe27f` and U8SHAPES `99ac982244eae904a61e4ff688a721a4bb86ec458dca7614661f3d2dd95529d5`.

## Verdicts

- PASS: all 112 Water tiles copy retail 347 frame 16 and retain their original flagstone support. Shape 896 has no SEA, SOLID, LAND, or OCCL flags.
- PASS: shape 895 has 91 frames and retains its original seven decoded frames and complete TYPEFLAG row. All 84 additional frames match their binary masks and declared retail source frames, including dimensions and anchors.
- PASS: all three complete protected windows retain every palette pixel, both with and without reference actors. Screen04 remains 98.88682432432432%, screen05 94.55287019246975%, and screen07 97.27654569892474%.
- PASS: removing nonfixed objects, animated shapes, and shapes 865, 860, and 400 leaves all three windows pixel-identical to their baseline controls. This includes the gods and their changing ceremony frames.
- PASS: rendering permanent fixed flat backgrounds alone creates zero newly unpainted pixels in all three windows. Screen04 and screen05 remain pixel-identical in this control. Screen07 changes two background palette pixels, both covered by the same permanent fixed, nonanimated shape 125 frame 7 at (6812,21272,0). Pixel (41,1) changes background palette 0 to 27, and (43,2) changes 0 to 28. Their actual rendered values remain 25 and 26 in both builds.
- PASS: the 47 Map 11 texture clips overlap zero actual DRAW-ground sprite pixels and zero protected-window pixels. The uncut negative control records 47,897 intersections with ground pixels and 55,192 with protected-window pixels.
- PASS: the 34 black clips retain 29,197 opaque black pixels, entirely inside the protected-window union and matching the original permanent background there. All 47 replacement editor supports retain the original filler dimensions and solid flag.
- PASS: all five exact-reach and walk-off comparisons match across baseline, phase two, and corrected phase three. Map 11 retains 140,466 arrival positions and 141,350 opened positions. Map 18 retains 11,839 arrival, 15,824 Tiny Tar, and 15,064 opened positions. Every coordinate and level matches, with zero falls, void landings, and off-map exits. All other raw map payloads remain byte-identical.

## Named stops

Built-map frame comparisons use the post-phase-two archive and corrected final build.

| Stop | Exterior filler-black pixels | Total black pixels | Minimum Avatar visibility |
|---|---:|---:|---:|
| m11-06 | 17,451 → 0 | 32,437 → 14,986 | 100% → 100% |
| m11-11 | 4,939 → 0 | 17,231 → 12,292 | 100% → 100% |
| m11-12 | 3,311 → 0 | 15,124 → 11,813 | 100% → 100% |
| m11-13 | 880 → 0 | 9,408 → 8,528 | 100% → 100% |

## Corrected findings

The initial texture-only replacement removed black pixels that the original fillers painted inside the protected windows. Independent rendering found 5,871 changed screen05 pixels and 3,451 changed screen07 pixels, recorded in `verifier-phase3-window-finding.json`. Retaining original fillers repaired the windows but left small exterior tails. The source now separates each filler's editor support, protected-window black paint, and exterior texture.

The first review then missed background hidden by foreground objects. Its black-mask criterion used the complete visible window. Removing dynamic objects from that version exposed 150 newly unpainted screen05 pixels and two screen07 pixels; permanent-background-only rendering exposed 10,329 and 1,680. `background-finding.json` records the rejected version. The corrected masks derive from the original permanent background and preserve floor paint beneath objects and pillars. The expanded dynamic-removal controls and permanent-background coverage checks now pass. The allowed art test includes a permanent regression check. No actionable source finding remains.

## Estate, captures, and rebuild

`tools/run_all_tests.sh` passes 56 of 57 test files. The sole failure is `test_integration_state.py`: the unchanged main install has older U8SHAPES, TYPEFLAG, and FIXED files. The private capture harness passes. The art test passes 707 checks, the route test passes 166, paint cycles pass 76, and vignettes pass 39. The permanent visual check completes in 87.337 seconds. After capture completion, `tools/build_artifacts.sh` reproduces all five expected SHA-256 hashes. Compilation succeeds for 55 of 57 files, retaining only the documented EALOGO and TJORVI pair. Map validation reports zero warnings and errors. `git diff --check` passes.

Capture manifest checks pass for 12 before PNGs, one phase-two PNG, and 12 replacement final PNGs, all 640 by 400 with exact requested coordinates, `ok: true`, and `landed: true`. Every replacement final record declares the corrected artifact hashes, `usehighres: false`, `fresh_world: true`, and display `:71`. Earlier records use the original capture schema. The parent ran these captures and owns the final Codex review. This verifier launched no ScummVM process and changed no installed game copy.

Evidence: `verifier-phase3-art.log`, `verifier-phase3-geometry.log`, `verifier-phase3-background-controls.log`, `verifier-phase3-background-pixels.log`, `verifier-phase3-stops.log`, `verifier-phase3-no-reference-actors.log`, `verifier-phase3-estate.log.gz`, `verifier-phase3-build.log.gz`, and `verifier-phase3-capture-manifests.log`. Earlier rejected and retained-filler intermediate logs are labelled separately. Verifier writes comprise this report, its evidence logs, and reproduced private build outputs. No source or main-checkout file is changed by this verifier.

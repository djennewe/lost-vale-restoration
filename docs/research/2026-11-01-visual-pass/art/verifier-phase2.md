# Art phase two verification

The Map 18 witness and screenshot contract pass independent verification. The full estate passes 56 of 57 test files, with the permitted integration-state failure. The supported rebuild passes.

- PASS: Tiny Tar at m18-19 improves from 0% minimum visibility to 100% across 72 walking and standing poses. The original built map supplies the negative control.
- PASS: screen04 retains 98.88682432432432%, with zero changed palette pixels against an independent render using the immutable baseline artifacts.
- PASS: arrival, Tiny Tar, and opened floods retain exactly 11,839, 15,824, and 15,064 reached positions. Every reached coordinate and level matches. Walk-off results match, with zero falls, void landings, or off-map exits in all three states.
- PASS: every raw archive payload outside Map 18 remains byte-identical.
- PASS: the continuous west-passage jog has 32 reachable positions on a 16-unit lattice and minimum visibility 82.89473684210527%. Its lowest value occurs at (2527,7375,0). The jog follows x 2671 from y 7199 to 7295, moves west to x 2527 at y 7295, then continues south through y 7551.
- PASS: the same 32 positions across 72 Tiny Tar poses produce 2,304 paint frames with zero dependency cycles.
- PARTIAL: protected wall adjacency retains occlusion at x 2591, y 7391 and 7423, and beside the island at x 2671. The visible jog avoids these positions. The named witness and continuous visible route pass; visibility at every passage cell remains outside that claim.
- NOT DEMONSTRATED here: in-engine walking or captures. The parent owns the required tour captures on display :71. This verifier launched no engine and changed no installed game copy.

The review found one completeness issue: retail 566 has 15 frames, and the initial clone copied frame zero alone. The parent expanded the copy recipe to all 15 frames. The supported rebuild now contains all 15 frames, and all five canonical artifact hashes verify. The updated targeted art test passes 530 checks with zero failures, including the 15-frame copy, exact screen04 hash, and the visible jog.

Evidence: `verifier-phase2-geometry.log`, `verifier-phase2-passage.log`, `verifier-phase2-visible-route.log`, and `verifier-phase2-passage-cycles.log`.

The full estate reports the sole failure in `test_integration_state.py`: the private harness and symlinked main install hold older art and FIXED bytes. The estate passes its 88.266-second visual-quality check, 166 route checks, 76 paint-cycle checks, and 39 vignette checks. The supported `tools/build_artifacts.sh --record` run reports 55 successful compilations of 57, with only the documented EALOGO and TJORVI failures. Map validation reports zero warnings and errors.

Disk changes are limited to this report, the listed evidence logs, the estate, build, art-props, and hash logs, private build outputs, and regenerated `shared/build/ARTIFACTS.sha256`. No source, commit, main-checkout file, or installed game was changed by this verifier.

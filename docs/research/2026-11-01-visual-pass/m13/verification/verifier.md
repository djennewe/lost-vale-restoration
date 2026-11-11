# Map 13 independent verification

The independent verifier found no unresolved source defect.

- Corner collision unions match across 2,496 side, height, and lower-floor configurations.
- The wall-only replacement preserves the complete 20,686-cell reachable set.
- Final terrain changes preserve the reached count, with the intentional 41-position apron level shift.
- The quest band contains 843 cells, with zero below half visible and a minimum of 93.53 percent.
- Candidate edge checks pass. Candidate climb checks pass all 24 assertions, including 256 FOOT holds.
- The inlet changes 44 cells and overlaps no climb cells. Seven shore-halo cells avoid walked ground and protected windows.
- All five window scores and unpainted counts remain unchanged; direct render comparisons show zero changed pixels.
- All 13 Map 13 pinned rows remain present.

The cap review found that the terrain strip at `(3615,2303,24)` initially missed the transform. Applying `summit_face_caps` to terrain resolved it. The corrected source and diagnostic archive both contain 6,298 records with identical item multisets. Every shortened strip and post preserves its original solid union without overlap. The two completion strips remap fit keys to both replacements without collisions; the terrain cap retains its original cell identity. All three original strip tuples are absent from vignette-owned records.

The verifier ran read-only candidate checks with explicit temporary archives, including `test_map_edges.py --maps 13 --fixed ...` and `test_climb_width.py ...`. Source and shared artifacts were left untouched. Final build, strict visual test, estate, and capture evidence are recorded separately by the slice author.

The final evidence review found no misleading claims. Both states contain 36 valid paired captures covering every specified stop, with matching image hashes and dimensions. All 47 report table rows match the stop JSON and settled positions. Pins, audits, post-commit metrics, strict results, artifact hashes, window scores, camera counts, compiler counts, estate results, and review conclusions agree. Official capture scripts retain their original bytes. The report identifies the north-background residue, corrected m13-26 witness, startup warnings, and permitted integration failure.

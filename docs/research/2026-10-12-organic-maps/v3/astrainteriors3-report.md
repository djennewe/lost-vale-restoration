# Interiors v3 research

Research-only; repository/shared/build unchanged. Built on copied round-2 mock_v2.py, elements_forest.py, refinements.py. Reproduction: generate_v3.py (all writes confined here).

## Iterations saved
- `iteration01_*`: all 15 game-scale comparisons. Counts Map9 1,905; Map11 22,943; Map18 4,209; Map39 6,177. Fable rejected remaining black rim incursions, monotone hub, overlarge lava sheet and money-shot cameras.
- `iteration02_*`: corrected 256u cap footprint inclusion (old 128u test let roofs cross floor), replaced fake blood: **332 is severed arms, actual blood 839 + 423 red cascade**. Added 48u tomb dais with six 8u stair courses. Pin/flood audit pending. Rim/camera/hub/lava refinement remains in progress.

Changed vs v2: partial 334 masks and 564 rocky caps + painted void plates; full wall family textured inner faces; coherent 301 rough patches/gravel feet and rubble/bone clusters; north guardian dais with 240/296/259, stairs and blood; full Map18 complex plus pinned crack; all four Map11 wings, tomb-kit reskin, connected Fire-pillar inlet; lower Map39 forest and hedge bays.

## Hard composition constraints discovered
The layout memo swaps element names. Source + pinned frames are Earth NW (2047,5631), Air NE (17152,5120), Fire SW (5631,18943), Water SE (12799,18943). V3 preserves these.

Screen04's complete compact trio is impossible at fixed pins + native scale: west/east gods differ by 1536u at equal y = 384 projected pixels, already wider than 320px before sprites. Individual god-centred comparison frames will be provided rather than relocating gods or silently zooming out.

Draft art remains explicit render-only substitution: shrine/plinth and Fire-pillar art from v2. No shape IDs allocated/artifacts modified. Foundation-first/depth rendering is approximate, not ScummVM. All 1994 comparisons use RefArtCatalog/x3 verbatim; native frames 320×200, ×3 nearest neighbour. Retail hall camera selection still provisional.

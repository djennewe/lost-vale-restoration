# The Passage Test plant (shape 871)

Art track item 13, `docs/art-track.md` contract 13. Candidates 2026-10-11,
waiting on Douglas's pick.

The "Test of Rutabaga": "a nasty plant with delectable fruit at its heart,
guarded by long poisonous spines" (Plot v1.2 beat 8). Today it is shape 126
frame 0, which is not a plant: a blue-crystal ground tile the Avatar walks
over (`compare.png`, first sprite).

`tools/art/gen_test_plant.sh`, with `reference-plants.png` (base 65 frames
0/2/6, 625, 753) as the idiom reference.

| | Axis | Generator | Game scale (box 48x56) |
|---|---|---|---|
| **A** | faithful: a squat swollen yellow-green bulb, a crown of long dark-tipped spines, one red fruit at the heart. At 1x U8PAL pushes the green to yellow | agy, Nano Banana | 48x46, sized by width |
| **B** | colour: A's plant with livid purple flesh and pale bone spines | agy, Nano Banana | 45x48 |
| **C** | form: the bulb lifted on a short stalk, a giant thistle, spines purple-tipped | **Codex gpt-image-2** | 47x48 |

**C came from the fallback route.** agy's image quota ran out on C (`429
RESOURCE_EXHAUSTED`, gemini-3.1-flash-image, its log says no substitute was
drawn), so `gen_test_plant.sh --codex C` ran the same description through
Codex after its usage cap reset. Its log shows the built-in `image_gen`
output copied from `~/.codex/generated_images/`; nothing was drawn by
script. That route takes no reference image, and it returned a transparent
background instead of magenta (`C_codex_transparent.png`, as generated).
`static_items.py flatten` composited it onto magenta as `C_raw.png`: fed
as it was, its faint soft-alpha pixels widened the first trim and left the
sprite at 38x40. So C differs from A and B in generator as well as form.

**All three are judged at despill 0.** The build recipe's hue-based despill
(margin 16) stripped the purple-black spine tips, the plant's menace, from
every candidate (A 121 px, B 971, C 141); at margin 0 none shows a magenta
fringe at 4x. An `lv_art_props.py` frame tuple carries the margin.

## Plates

- `compare.png`: 1x row, the placeholder 126.0, the mushroom 65.0, the
  rock spire 66.0 and bones 235.0 that stand on the same plateau, the
  Avatar, then the candidates; 4x row, the placeholder and the candidates.
- `site-1x.png`, `site-2x.png`: the test-grounds plateau from FIXED.DAT,
  before and with each candidate at (12800, 29408, 64), an Avatar for
  scale. A composite (floors first, then props by x+y), not an engine shot.
- `preview_report.json`.

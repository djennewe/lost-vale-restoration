# The special root (shape 869)

Art track item 12, `docs/art-track.md` contract 12. Candidates 2026-10-11,
waiting on Douglas's pick.

No 1994 art. Ezrekal's one description is "Brightly colored I think it
was, maybe purple." (`LOST VALE/EZREKAL.UNK:3142`); the brief asked for a
gnarled, pale root. The two disagree on colour, so colour is B's axis.

`tools/art/gen_special_root.sh`, agy (Nano Banana), with
`reference-reagents.png` (base 395 frames 16/19/20 and 399 frames 4/7/9) as
the idiom reference. All three logs read clean: each names the Nano Banana
`image-generator` subagent and reports no quota error.

| | Axis | Game scale |
|---|---|---|
| **A** | pale: an ivory, bone-white gnarled taproot, two forks, a cut end | 21x16, 23 colours |
| **B** | purple: A's root in violet (Ezrekal's line). Raw, it reads a little like a gloved hand; at 1x U8PAL turns the violet hot pink | 18x16, 17 colours |
| **C** | crown: A's pale root with a small tuft of violet leaves at the cut end | 17x16, 27 colours |

## A pipeline finding: purple art needs despill 0

The build recipe despills at margin 16, stripping key-coloured bleed off
the edge BY HUE, and violet is magenta's neighbour: it ate 102 of B's
pixels (18x16 became 13x11) and 11 of C's leaf pixels. B and C are judged
at despill 0, which an `lv_art_props.py` frame tuple carries (its fifth
element). A keeps 16.

## Plates

- `compare.png`: 1x row, the placeholder 399 frame 9, the wood reagent
  395.20, a ring stone, the Sacred Rock 863 and the Avatar, then A/B/C;
  4x row, the placeholder and the candidates.
- `site-1x.png`, `site-2x.png`: the east side of the Sacred Circle from
  FIXED.DAT, before and with each candidate at (21376, 16640), an Avatar
  for scale. A composite, not an engine shot.
- `preview_report.json`.

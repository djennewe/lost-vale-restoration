# The Message Scroll (shape 864)

Art track item 4, `docs/art-track.md` contract 4. Landed 2026-09-21.

**A document with an errand and no text.** Plot v1.2 beat 13 has the Avatar
find it in the deserted Cloud World beside the two Shield halves; beat 14 has
him carry it to Ezrekal and show it to her. `items.yaml:121` gives the one
line of content anyone wrote down: "message from one of the gods addressed to
Love, Hate, and Apathy explaining the Titans' attack". No 1994 art, and no
recovered usecode names it.

## The reference is the game's own scroll

`reference-base-scroll.png` is base shape 159 frames 0 and 3 pulled out of
`U8SHAPES.FLX` and rendered on magenta: a flat parchment lying open on the
floor, rolled at both ends, ink across the middle, a thin dark outline. That
is the idiom, and the generator was told to match its material, palette and
construction. Shape 159 is also the TYPEFLAG donor, which is where the
engine-side behaviour comes from: no `SI_FIXED`, so the Avatar can pick the
scroll up, and `SF_QUALITY`, so its quality 80 is readable.

## What was wrong before

The chamber's centrepiece was a wooden plank bench: shape 158, 32x40 px,
`SI_FIXED`, standing on the plinth. The first column of `compare-4x.png` is
that bench composited on the plinth exactly as the candidates are.

## Five candidates, two passes

`tools/art/gen_message_scroll.sh`. One axis each: **A** the sheet open flat,
**B** the same with a wax seal, **C** one end still rolled.

**Every v1 candidate read as a BLANK sheet at game scale.** The whole risk on
this item is the downscale: 1024 px to 22, so the ink band survived as three
grey pixels and the object said "parchment" without ever saying "a written
message". v2 pinned the ink as its own clause (the darkest thing in the
drawing, strokes a twentieth of the sheet thick, three or four long lines).

**A2 ships**, 30x22 px: the sheet open flat, both ends rolled, four lines of
dark strokes across the middle. **Douglas reviewed the candidate sheet and
the in-engine plate on 2026-09-21 and kept it ("keep as is"), so the choice
is settled.** B2 was the only real alternative and stays one filename away
in `lv_art_props.py`. It reads well too; its wax seal is a European idiom on
a Zealan god's message, and the ink block behind the seal reads a little
like a plaque. C's asymmetric roll reads as a rug at 1x.

## The resize is non-uniform, and that is the projection

The generator draws the sheet square, seen from straight above; the game sees
the floor at the 2:1 isometric angle. So the row carries both `width` 30 and
`height` 22, and `png2shape` squashes. Every candidate before that squash
reads as a scroll standing upright against the plinth.

## Landed

`after-plinth-640x400.png` and `after-scroll-4x.png` are in-engine on a fresh
world; the session report is `docs/playtest-2026-09-21-message-scroll.md`.
The engine's own line: one item, shape 864, (3328, 1536, 8), quality 80,
`shapeinfo f: 2, fam: 1`. The Avatar picked it up, +10 total weight.

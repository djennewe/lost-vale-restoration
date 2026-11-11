# Encased gods, second pass — the projection fix (2026-09-13)

Douglas, looking at the in-engine plates: *"they look a little skinny and 2D."*

**The cause is camera angle, not width.** U8's camera is high, so every solid
in the sanctum shows a wide 2:1 diamond on top — look at the wall stubs beside
each god. The v1 crystals were generated from a much lower angle: one big
front face and a sliver of top. That projection mismatch is what reads as
flat. Doloras never drew the complaint, and she is the one whose block has a
real top plane.

Width is second-order. The cover's own Felicitar is a narrow slab and still
reads as a solid, because its facets are right.

## The three candidates

All `codex-image` / gpt-image-2, one prompt each, Timyra only — the direction
gets picked on one god before spending generations on the other two.

| | Shape | At `--height 124` | Verdict |
|---|---|---|---|
| **A** | rectilinear crate | 91 × 123 px | correct projection, obviously manufactured — the same failure `resin_encase --mode block` was rejected for |
| **B** | faceted boulder | 91 × 124 px | **recommended.** Broad facetted top, lit left flank, dark right flank; the figure fills it |
| **C** | tall prism | 54 × 124 px | keeps the cover's shard silhouette, gains a real sliced top plane, still slim |

`compare-*.png` are those four (v1 included) put through the real pipeline —
keyed, scaled, quantized to `U8PAL.PAL` — and pasted onto an actual screenshot
of the temple floor at 1×, then enlarged 3×. That is the surface the complaint
was made on, so it is the surface the decision is made on.

## The prompt that mattered

Pinning geometry rather than adjectives. The load-bearing clauses:

- *seen FROM ABOVE at the steep angle of a 2:1 isometric floor tile*
- *a large flat TOP face, a wide diamond exactly twice as wide as it is tall*
- *LEFT face mid-value, RIGHT face clearly darker* — three planes, three values
- *the block's near vertical edge crosses in front of part of the silhouette*,
  which is the cue that separates "suspended in" from "painted on"

**A refusal worth recording.** The first attempt said the figure was "nude
with smooth featureless doll anatomy" — the wording the freed set used — and
came back `moderation_blocked, safety_violations=[sexual]`. The figure inside
the amber is only ever a dark silhouette, so the anatomy language was not
needed at all; describing it as *"a plain dark, nearly black silhouette... no
surface detail of any kind... a flat shadow shape, like a fly in amber"*
generated first time. Same asset, no compromise.

## Douglas picked C (2026-09-13)

*"C looks most like the box art."* — and it does: the cover's blocks are
prisms, not boulders and certainly not crates. C keeps that identity and fixes
only the projection.

Felicitar and Doloras were then generated in the same idiom, each matched to
its own cover silhouette — Felicitar a slender vertical shard, Doloras a squat
block, because she kneels. All three are injected as frames 0/1/2.

| God | Frame | Sprite | Built at |
|---|---|---|---|
| Felicitar | 0 | 36 × 124 px | `--height 124` |
| Doloras | 1 | 96 × 71 px | `--height 86` |
| Timyra | 2 | 54 × 124 px | `--height 124` |

`set-at-game-scale.png` is the three on real temple floor at 1×, enlarged 3×.

## The tolerance trap that came with them

**Key tolerance drops 95 → 40, and it is not cosmetic.** v1 was bright
everywhere, so keying black generously cost nothing. These have a genuinely
dark shadowed facet and a dark silhouette, and at 95 the key ate both: the
blocks came out **hollow**, floor visible straight through them, the figures
reduced to wireframe. It looks exactly like a rendering bug and it is a key
setting. 40 still takes the glow fade off the edges and leaves the shadow side
intact; a sweep at 95/60/40/25/12 put the knee at 40.

## Settled: the freed three stay as they are (2026-09-13)

The question was whether they needed the same pass — the freed Felicitar is
24 px wide, so the ceremony swaps a heavy prism for a thin figure. Douglas:
*"I think its good as is."*

So the contrast is the point, not a defect. A body that was filling a block of
amber a moment ago should look slighter standing on its own, and the read the
frame swap wants is "the shell is gone", which a like-for-like mass would
blunt. **Do not re-generate the freed frames to match the blocks.** If this
comes up again, it has been asked and answered.

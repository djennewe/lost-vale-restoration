# The Sacred Rock (shape 863)

Art track item 3, `docs/art-track.md` contract 3. Landed 2026-09-20.

**The one item on the track with no 1994 original.** "Sacred Smallish
Unusual-Colored Rock" was a joke placeholder in Plot v1.1/v1.2 that became
"Sacred Circle" before the usecode snapshot, with zero occurrences in the
recovered source. So there was nothing to redraw, and Douglas decided the
look instead: **a ninth stone**, kin to the eight shape-38 monoliths
already standing on the circle's ring.

## The reference is the ring

`reference-ring-stones.png` is shape 38 frames 2 and 3 pulled out of
`U8SHAPES.FLX`, flood-filled to magenta and scaled, passed to agy the way
the obelisk passed its screenshot crop: match this material, these tones,
this dressing. The deciding constraint from the contract is that the
centre stone must read as belonging to the ring.

## What was wrong before

`before-circle-640x400.png`, in-engine at 640x400 from (20480, 17100, 0):
eight pale dressed monoliths on the ring (27x59 px), and on the centre
paving a dark striated lump (shape 66 frame 4, 41x65) that reads as rubble
from a cave mouth. It failed on material and on scale at once, standing
6 px taller than its own fence. `before-rock-4x.png` is it at 4x.

## Six candidates, two passes

`tools/art/gen_sacred_rock.sh`. Each candidate differs in one axis:
**A** plain, **B** a vertical line of shallow uncoloured runes on the lit
face, **C** a dressed shaft with a rough unworked crown.

**v1 (A, B, C) all read as stacked masonry**, wrapped in a heavy black
keyline, in neutral grey. Two of those three defects turned out to be
artifacts of judging at 1024 px: **the keyline and the neutral grey both
disappeared in the U8PAL quantize**, so at game scale every candidate is
the ring's cold blue-grey with no outline. Only the stacked-block reading
was real, and v2 pinned it as its own clause ("ONE SINGLE PIECE OF STONE
... no joints, no mortar lines and no stacked tiers"), with the aspect
ratio and the absence of a keyline pinned beside it.

**v2 (A2, B2, C2) fixed the silhouette.** `compare-1x.png` and
`compare-4x.png` put all six at game scale beside a ring stone, each run
through the real pipeline (`png2shape`, height 96, key FF00FF tolerance
130 despill 16, donor 66).

**C2 ships:** a dressed tapering shaft with shallow weathering bands and a
rough broken crown, one continuous piece of stone, 57x95 px. **Douglas
reviewed the before/after and the candidate sheet on 2026-09-20 and
approved it ("keep as is"), so the choice is settled**; B2 was the only
real alternative and stays one filename away in `lv_art_props.py`. B2 is clean
but reads as a smooth gravestone and its runes are illegible at 1x; A2 is
a plain block whose weathering bands still read as two joints.

## Landed

`after-circle-640x400.png` is the same framing as the before plate, on a
fresh world with `usehighres=false`. `after-approach-640x400.png` is the
whole circle from the north, and `after-rock-4x.png` the stone at 4x.
`ObjectManager::findShape 863` returns one item at (20415, 16831, 0)
quality 100.

Engine side: donor 66's own TYPEFLAG entry, footpad (4,4,8), no usecode
class, no `TYPE_SHAPES` re-point, position frozen by one free world unit
against `MAP10_ROOT_SEED`. The contract has the full chain.

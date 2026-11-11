# Resin encasement, built locally from the picked art (2026-09-13)

The 1994 Art List wants each god in two states — "encased in resin" and
"speaking". These are the encased state, composited by `tools/resin_encase.py`
from the three picks in the parent directory, **not** re-generated: a frame
swap only reads as the resin breaking if the statue underneath is provably the
same statue.

Two strengths are kept, because the choice is a judgement call:

| | shell | opacity | rim | spec | reads as |
|---|---|---|---|---|---|
| `*_resin-strong.png` | 3 px | 0.30 | 1.2 | 0.5 | sealed in amber; the stone goes bronze |
| `*_resin-subtle.png` | 2 px | 0.18 | 1.06 | 0.3 | a glassy skin; the stone stays stone |

`*_x3.png` is each one read back out of a patched `U8SHAPES.FLX` at 3×.

## The margin is a checkerboard, and that is the point

Half the resin margin's pixels are transparent, in a 1px checker — how 1994
VGA art painted translucency in a palette with no alpha channel. It only
survives if the compositing happens at **game scale**: built at the source's
~14× resolution it averages back into flat fill under png2shape's Lanczos
downscale, which is exactly what the first attempt did (it came out as a
yellow sticker outline around the sprite).

So `resin_encase.py` resizes first and composites after, and png2shape must
then be run **without `--height`**, or it resizes again and mangles the dither:

```bash
tools/resin_encase.py shared/docs/art-poc/gods/felicitar_B_raw.png \
    --out /tmp/resin --height 110
tools/png2shape.py /tmp/resin/felicitar_B_resin.png --donor 443 \
    --no-key --no-trim --shape-id 860 --flx /tmp/scratch.flx \
    --no-typeflag --force --preview /tmp/felicitar_B_resin_x3.png
```

## Frame order, when these are placed

`build_map_18.py` places the god's **initial** state, which is encased. So:

    frames 0/1/2  resin    Felicitar, Doloras, Timyra
    frames 3/4/5  free     the same three, shell gone

and the freeing is `setFrame(n + 3)` in a `foreach` inside `AOSCENE::hatch`,
which needs a `TypeGodStatue` entry pointing at shape 860 — the scene has no
handle on those items today.

## Costs

The shell adds 3 px of height and 3 px per side. Timyra is the tight one: 100
× 110 free, 106 × 113 encased, against props at ±128 units.

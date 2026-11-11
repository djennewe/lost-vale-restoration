# The gods encased — amber crystals (2026-09-13)

Frames 0/1/2 of shape 860: the state the player finds them in. **Generated**,
not composited — `codex-image` / gpt-image-2, one prompt per god.

| God | Sprite | Built at | Figure inside |
|---|---|---|---|
| Felicitar | 48 × 124 px | `--height 124` | standing, arms raised overhead |
| Doloras | 98 × 86 px | `--height 86` | kneeling, hunched, head bowed |
| Timyra | 61 × 124 px | `--height 124` | turned right, knees bent, hands at her face |

```bash
tools/png2shape.py shared/docs/art-poc/gods/encased/felicitar_encased_raw.png \
    --donor 443 --height 124 --key 000000 --key-tolerance 95 \
    --shape-id 860 --flx /tmp/scratch.flx --no-typeflag --force \
    --preview /tmp/f_x3.png
```

**Key BLACK, not magenta.** gpt-image-2 ignored the flat-magenta instruction on
all three and returned them on black with a soft glow fading into it. Keying
black at tolerance 95 cuts the glow, which is correct: U8 sprites composite
with no additive blending, so a halo would paint a dark ring onto the floor.

## What the cover actually shows, and what two procedural attempts missed

The light comes from INSIDE the amber. The block is a solid field of luminous
orange, and the god is a **dark, nearly black silhouette** suspended in it,
backlit so only a contour and a few warm highlights catch the light. A pale
side facet down one edge gives it depth; the sliced top plane is the brightest
thing in the picture.

`procedural/` holds what `tools/resin_encase.py` produced before that was
understood. `--mode block` drew rectilinear crates that read as packaging;
`--mode gem` drew a tapering hull with a bright band around a dark window,
which read as a 2D outline of a gem laid over the sprite — the value
relationship inverted, a bright figure on a dark ground ringed in gold. The
tool is still useful and both modes still work; it simply cannot paint
volume, and volume is the whole of this asset.

## The trade-off this makes

Compositing guaranteed the figure inside the amber was the same figure, pixel
for pixel, as the freed frame. **Generating breaks that.** The poses match and
the silhouettes are close, but the encased figure is a separate render, so the
frame swap at the freeing shows a change of figure as well as a loss of amber.

That may be acceptable — light returning to a body reads as transformation —
but it is a real consequence and was not the plan. If it jars in-engine, the
fix is to re-derive the freed frames as brightened versions of these
silhouettes rather than as separate art.

## Cost against the sanctum

Doloras's boulder is **98 px wide**, the widest asset in the set, against props
at ±128 units. Check her clearance first when placing.

#!/usr/bin/env python3
"""
lv_god_frames.py — generate shape 860's frames 3..41 at the 1994 scale.

Shape 860 frames 0-2 are the three gods in amber exactly as the 1994 team
drew them: screen04's pixels, imported index for index from
`shared/data/lv-1994-art/ReconInteriors/s04_god_*.png` through
vignettes/art_registry.json (2010/2011/2012) by lv_god_statues.py. Nothing
here touches them.

This file derives everything after them from the art the shatter was first
built with (2026-09-14), redrawn so the animation starts on the 1994 statue:

    3 4 5     the three freed gods at rest (the standing poses)
    6..41     three 12-frame runs: 6 frames of the amber breaking, then 6
              of the god rising from the released pose to the standing one

THE 1994 SCALE. Our encased art was 124 px tall (Timyra, Felicitar) where
the 1994 Timyra is 67: the 1994 gods are human-sized, not giants. Every
figure keeps its old height times FIG_SCALE = 67/124, the 1994 Timyra over
ours (the one god whose 1994 and 2026 poses agree, standing with her hands
at her face), so the three freed gods keep their relative heights and come
out ~59 px tall, a head over the Avatar. The shard speeds and canvas margins
scale with them.

THE 1994 PALETTE. The figures are re-quantized to the U8PAL indices the
three 1994 statues use (RAMP, 58 indices: the 163-175 amber/brown ramp, the
50-62 yellows and oranges, the dark greys of the figures inside). A freed god
is therefore drawn in the colours the player saw her sealed in, and the
olive bronze of the 2026 render is gone. The shards are not re-quantized at
all: they are the 1994 statue's own pixels, cut into pieces.

CONTINUITY. A run's first frame IS the 1994 statue, pixel for pixel, at the
statue's own hotspot, so the cut from the sealed frame into the run is
invisible. The figure revealed by the break stands on the god's footprint
centre, FOOT_DY pixels above the hotspot (a 64x64 box's base diamond is
16 px tall; its centre is 8 above the front corner the hotspot marks).

EVERYTHING IS WRITTEN INDEXED. Each frame is a P-mode PNG on U8PAL with
index 255 transparent, and `run/anchors.json` records each frame's hotspot,
so lv_god_statues imports every frame verbatim (png2shape.indexed_pixels).
The magenta key, the despill pass and png2shape's trim and rescale are out
of the build path: they ran here, once, on the figure sources.

WHY THE RUN SHARES ONE CANVAS. A trim is per-frame, so a run trimmed frame
by frame would re-centre on every flying shard and the god would jitter on
her own feet. A run's 12 frames are one canvas with one hotspot. The rest
frames 3-5 are cropped with their hotspot carried, which is the same thing.

Usage:
    python3 lv_god_frames.py          # rewrites shared/docs/art-poc/gods/run/
"""

import json
import math
import os
import random
import sys

THIS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(THIS, '..', '..', '..'))
sys.path.insert(0, THIS)
sys.path.insert(0, os.path.join(ROOT, 'tools'))

from PIL import Image                                             # noqa: E402
from png2shape import key_out, despill_edge, trim_to_alpha, scale_to  # noqa: E402

ART = os.path.join(ROOT, 'shared', 'docs', 'art-poc', 'gods')
OUT = os.path.join(ART, 'run')
ANCHORS = os.path.join(OUT, 'anchors.json')
REGISTRY = os.path.join(THIS, 'vignettes', 'art_registry.json')

MAGENTA = (255, 0, 255)
KEY = 255

SHATTER_LEN = 6
WAKE_LEN = 6
RUN_LEN = SHATTER_LEN + WAKE_LEN

# The 1994 Timyra (registry 2012) is 67 px tall; our encased Timyra was 124.
FIG_SCALE = 67 / 124

# Head/side room on the canvas for shards leaving the block, at the old
# scale times FIG_SCALE. Cosmetic: it stops a shard being clipped mid-flight.
SIDE_ROOM = round(14 * FIG_SCALE)
TOP_ROOM = round(10 * FIG_SCALE)

# Shard count. At ~35 px wide each of 15 pieces is still a few pixels across.
SHARDS = 15

# The revealed figure's feet: the centre of the god's 64x64 base diamond.
FOOT_DY = 8

# Per-god sources. `statue` is the registry id of the 1994 statue, which
# also fixes the frame (2010 -> frame 0). Heights are the OLD game-scale
# heights each pose was drawn at; FIG_SCALE is applied on top. Doloras kneels
# released and stands at the end, so his silhouette grows over the wake.
GODS = [
    # name,       statue, released,                        rel_h, standing,                      std_h
    ('felicitar', 2010, 'freed/felicitar_final_raw.png', 110, 'wake/felicitar_stand_raw.png', 110),
    ('doloras',   2011, 'freed/doloras_final_raw.png',    72, 'wake/doloras_stand_raw.png',   110),
    ('timyra',    2012, 'freed/timyra_final_raw.png',    110, 'wake/timyra_stand_raw.png',    110),
]

# Everything generated on magenta needs the despill pass the freed set
# needed (docs/playtest-2026-09-14-god-animation.md).
FIG_KEY = (MAGENTA, 130, 16)


def load_palette():
    from shape_viewer import load_palette as _lp, PALETTE_FILE
    return _lp(PALETTE_FILE)


def statue(sid):
    """Registry id -> (RGBA image, P image, hotspot, repo-relative PNG)."""
    with open(REGISTRY) as f:
        fr = json.load(f)['shapes'][str(sid)]['frames'][0]
    p = Image.open(os.path.join(ROOT, fr['png']))
    assert p.mode == 'P', f'{fr["png"]} is {p.mode}, not P-mode'
    rgba = p.convert('RGBA')
    px = rgba.load()
    idx = p.load()
    for y in range(p.height):
        for x in range(p.width):
            if idx[x, y] == KEY:
                px[x, y] = (0, 0, 0, 0)
    return rgba, p, tuple(fr['hotspot']), fr['png']


def ramp(palette):
    """The U8PAL indices the three 1994 statues use (the shared palette)."""
    used = set()
    for _n, sid, *_ in GODS:
        used |= set(statue(sid)[1].getdata())
    used.discard(KEY)
    return sorted(used)


def sprite(rel_path, height):
    """One magenta-keyed source render -> an RGBA sprite at the 1994 scale."""
    key_rgb, tol, despill = FIG_KEY
    img, _ = key_out(Image.open(os.path.join(ART, rel_path)), key_rgb, tol)
    img = trim_to_alpha(img)
    img = scale_to(img, round(height * FIG_SCALE), None)
    img, _ = despill_edge(img, key_rgb, despill)
    return img


def match_bronze(img, ref):
    """Grade `img`'s metal to `ref`'s, per channel, on the opaque pixels only.

    The in-between poses do not all come from the same generator: the two
    ends of every wake came from Nano Banana with the god's own sprite as a
    character reference, the gpt-image-2 poses had no reference input and
    came out lighter and warmer, flashing brighter mid-wake. So shift and
    scale each channel so the figure's mean and spread match the
    reference's. Only pixels the key left opaque are touched.
    """
    def stats(im):
        px = [p for p in im.getdata() if p[3]]
        n = len(px) or 1
        out = []
        for c in range(3):
            vals = [p[c] for p in px]
            m = sum(vals) / n
            sd = (sum((v - m) ** 2 for v in vals) / n) ** 0.5
            out.append((m, sd or 1.0))
        return out

    src, dst = stats(img), stats(ref)
    lut = []
    for c in range(3):
        sm, ss = src[c]
        dm, ds = dst[c]
        lut.append([max(0, min(255, round((v - sm) * (ds / ss) + dm)))
                    for v in range(256)])
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (lut[0][r], lut[1][g], lut[2][b], a)
    return out


def place(canvas, img, foot=None):
    """Paste `img` with its bottom-centre on `foot` (default: the canvas's
    bottom-centre)."""
    cw, ch = canvas.size
    w, h = img.size
    fx, fy = foot if foot is not None else (cw // 2, ch)
    canvas.alpha_composite(img, (fx - w // 2, fy - h))


def shard_map(img, n, rng):
    """Voronoi-partition the opaque pixels into n shards.

    Returns a list of (shard_pixels, cx, cy) where shard_pixels is a list of
    (x, y, rgba). Seeds are drawn from the opaque pixels themselves, so a
    shard is never empty and the partition follows the silhouette.
    """
    w, h = img.size
    px = img.load()
    solid = [(x, y) for y in range(h) for x in range(w) if px[x, y][3] > 0]
    if not solid:
        return []
    seeds = rng.sample(solid, min(n, len(solid)))
    buckets = [[] for _ in seeds]
    for x, y in solid:
        best, bd = 0, None
        for i, (sx, sy) in enumerate(seeds):
            d = (x - sx) ** 2 + (y - sy) ** 2
            if bd is None or d < bd:
                best, bd = i, d
        buckets[best].append((x, y, px[x, y]))
    return [(b, sx, sy) for (sx, sy), b in zip(seeds, buckets) if b]


def shatter_frames(enc, rel, canvas_size, block_xy, foot, rng):
    """Six frames: the 1994 amber breaks and the god inside is uncovered.

    Frame 0 is the intact statue at `block_xy`. NOTHING IS PARTLY
    TRANSPARENT — the shape format has no alpha — so the break is told with
    whole pixels: the shards separate and travel, and each simply stops
    being drawn after its own lifetime. Falling shards are clipped at the
    canvas bottom, the statue's lowest row.
    """
    cw, ch = canvas_size
    ew, eh = enc.size
    ox, oy = block_xy

    shards = shard_map(enc, SHARDS, rng)
    vel, life = [], []
    for _pix, sx, sy in shards:
        # Radial from the block's middle plus an upward bias, so the break
        # throws pieces up rather than only sideways.
        dx = (sx - ew / 2) / max(ew / 2, 1)
        dy = (sy - eh / 2) / max(eh / 2, 1)
        m = math.hypot(dx, dy) or 1.0
        speed = rng.uniform(3.4, 6.4) * FIG_SCALE
        vel.append((dx / m * speed,
                    dy / m * speed - rng.uniform(1.6, 3.2) * FIG_SCALE))
        # Staggered exits; nothing lives past frame 4, so the last shatter
        # frame is the god alone and the wake starts from a clean silhouette.
        life.append(rng.randint(2, SHATTER_LEN - 2))

    REVEAL = 2      # the god is drawn once the shell has visibly opened

    frames = []
    for k in range(SHATTER_LEN):
        f = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
        if k >= REVEAL:
            place(f, rel, foot)
        layer = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
        sp = layer.load()
        for (pix, _sx, _sy), (vx, vy), lf in zip(shards, vel, life):
            if k > lf:
                continue
            tx = int(round(vx * k))
            ty = int(round(vy * k + 0.55 * FIG_SCALE * k * k))
            for x, y, rgba in pix:
                nx, ny = ox + x + tx, oy + y + ty
                if 0 <= nx < cw and 0 <= ny < ch:
                    sp[nx, ny] = rgba
        f.alpha_composite(layer)
        frames.append(f)
    return frames


def wake_frames(keys, canvas_size, foot=None):
    """Six frames from the released pose to the standing one.

    ONE DRAWN POSE PER FRAME, no dissolves (a blend is half-transparent,
    which the shape format cannot carry). With in-betweens missing it holds
    the poses it has for two frames each, so a partial set still shows
    every pose that exists.
    """
    out = []
    last = len(keys) - 1
    for k in range(WAKE_LEN):
        i = round(k / (WAKE_LEN - 1) * last)
        f = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
        place(f, keys[i], foot)
        out.append(f)
    return out


def to_indexed(img, palette, allowed, exact):
    """RGBA -> P image on U8PAL, 255 transparent. A pixel whose RGB is one
    of the 1994 statue's own colours keeps that index (`exact`), so the
    statue's pixels survive verbatim; every other pixel takes the nearest
    index in `allowed`."""
    out = Image.new('P', img.size, KEY)
    out.putpalette([c for rgb in palette for c in rgb][:768])
    src, dst = img.load(), out.load()
    cache = dict(exact)
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = src[x, y]
            if a < 128:
                continue
            rgb = (r, g, b)
            i = cache.get(rgb)
            if i is None:
                i = min(allowed, key=lambda j: (palette[j][0] - r) ** 2 +
                        (palette[j][1] - g) ** 2 + (palette[j][2] - b) ** 2)
                cache[rgb] = i
            dst[x, y] = i
    return out


def crop_indexed(p, anchor):
    """Crop a P image to its opaque box, carrying the anchor."""
    xs = [x for y in range(p.height) for x in range(p.width)
          if p.getpixel((x, y)) != KEY]
    ys = [y for y in range(p.height) for x in range(p.width)
          if p.getpixel((x, y)) != KEY]
    l, t, r, b = min(xs), min(ys), max(xs) + 1, max(ys) + 1
    return p.crop((l, t, r, b)), (anchor[0] - l, anchor[1] - t)


def build_god(name, sid, rel_p, rel_h, std_p, std_h, seed, palette, allowed):
    enc, _p, (hx, hy), _png = statue(sid)
    rel = sprite(rel_p, rel_h)
    std = sprite(std_p, std_h)

    # Four in-betweens, each scaled on the ramp between the released and
    # standing heights and graded to the released pose's metal.
    mids = []
    for n in (1, 2, 3, 4):
        p = f'wake/{name}_mid{n}_raw.png'
        if os.path.exists(os.path.join(ART, p)):
            h = round(rel_h + (std_h - rel_h) * (n / 5.0))
            mids.append(match_bronze(sprite(p, h), rel))
    poses = [rel] + mids + [std]

    # The canvas: the statue sits on its bottom edge, centred; the figures'
    # feet are FOOT_DY above the statue's hotspot. Wide and tall enough for
    # every pose and the shards' margin.
    ew, eh = enc.size
    fig_w = max(p.size[0] for p in poses)
    cw = max(ew, fig_w) + 2 * SIDE_ROOM
    ox = (cw - ew) // 2
    fig_h = max(p.size[1] for p in poses)
    oy = max(TOP_ROOM, TOP_ROOM + fig_h - hy + FOOT_DY)
    ch = oy + eh
    anchor = (ox + hx, oy + hy)
    foot = (anchor[0], anchor[1] - FOOT_DY)

    rng = random.Random(seed)
    frames = shatter_frames(enc, rel, (cw, ch), (ox, oy), foot, rng)
    frames += wake_frames(poses, (cw, ch), foot)
    assert len(frames) == RUN_LEN, len(frames)

    exact = {palette[i]: i for i in allowed}
    out = [to_indexed(f, palette, allowed, exact) for f in frames]
    rest, rest_anchor = crop_indexed(out[-1], anchor)
    return out, anchor, rest, rest_anchor, len(mids)


def main():
    print("=== shape 860 frames 3..41 at the 1994 scale ===")
    palette = load_palette()
    allowed = ramp(palette)
    os.makedirs(OUT, exist_ok=True)
    anchors = {'fig_scale': FIG_SCALE, 'ramp': allowed, 'gods': {}}
    for i, (name, sid, rp, rh, sp, sh) in enumerate(GODS):
        frames, anchor, rest, rest_anchor, nmid = build_god(
            name, sid, rp, rh, sp, sh, 41 + i, palette, allowed)
        for k, f in enumerate(frames):
            f.save(os.path.join(OUT, f'{name}_{k:02d}.png'),
                   transparency=KEY)
        rest.save(os.path.join(OUT, f'{name}_rest.png'), transparency=KEY)
        anchors['gods'][name] = {'statue': sid, 'run': list(anchor),
                                 'rest': list(rest_anchor),
                                 'canvas': list(frames[0].size)}
        print(f"  {name:<10} run canvas {frames[0].size[0]}x{frames[0].size[1]} "
              f"anchor {anchor}  rest {rest.size[0]}x{rest.size[1]} "
              f"@{rest_anchor}  in-betweens {nmid}")
    with open(ANCHORS, 'w') as f:
        json.dump(anchors, f, indent=1)
        f.write('\n')
    print(f"  ramp: {len(allowed)} indices  -> {OUT}")


if __name__ == '__main__':
    main()

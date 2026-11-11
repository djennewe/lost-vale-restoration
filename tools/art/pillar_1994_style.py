#!/usr/bin/env python3
"""
pillar_1994_style.py: redraw the Earth, Air and Water pillars (865 frames 0,
1, 3) in the style of the 1994 Pillar of Fire (frame 2, art_registry 2023).

Douglas's review of phase D (2026-10-30, card 4): the AI-drawn element
columns stood beside a 1994-style fire pillar and did not belong with it.
Each of the three is now the fire pillar's own banded dark column with an
element-coloured cap and flare in place of the red gem, the flames and the
lava. Every frame keeps 2023's canvas (46x106) and hotspot (18,104), so the
three draw on the same footprint at the same height and the puzzle, the
receptacles and Map 11's geometry are untouched.

How, from 2023's P-mode PNG (U8PAL indices, 255 transparent):

  * The column is every pixel inside its silhouette: x 16..36 down to row
    45, x 23..36 below. Its lower-left (x 16..22, rows 46..90) is the part
    screen07 hides behind the rubble mound; 2023 leaves it out, these
    frames draw it, row r copied from row 10 + (r - 46) mod 36 of the same
    column, where the column shows in full and the black rings repeat.
  * The gem is the red ramp (36..46) in rows 0..8; the flare is every
    other pixel outside the column (the flanking flames, the lava pool) and
    the warm flecks inside it (yellows and oranges). The column's rust
    mottling (the browns, the olive greys) is the fire's glow on the stone.
  * Each part is recoloured by luminance onto one element ramp: the
    source pixels' luminance range is stretched over the ramp's and each
    pixel takes the ramp entry nearest its stretched luminance. Shape and
    shading are the 1994 pixels; only the hue changes.

      earth  cap: ochre ramp 163..172      flare: browns 163..173 + 214..217
             mottling kept (it is earth's own brown)
      air    cap: pale ramp 144..146, 240..243   flare: greys 240..249
             mottling: greys 241..249
      water  cap: blues 136..142           flare: blues 148..155 + 136..137
             mottling: slate greys 246..251 + 152

  * No pixel lands on a cycling index (1..14); the build asserts it. 2023
    itself carried 88 index-9 greys (the shot's (48,48,48)) until
    2026-10-30, when they became 28, U8PAL's identical entry.

Writes shared/data/lv-1994-art/ReconInteriors/s07_pillar_{earth,air,water}
_1994style.png (art_registry 2024, 2025, 2026). Deterministic: rerunning
rewrites the same bytes.
"""
import colorsys
import json
import os

import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ART = os.path.join(REPO, 'shared', 'data', 'lv-1994-art', 'ReconInteriors')
FIRE = os.path.join(ART, 's07_fire_pillar_complete.png')
OUT = {'earth': 's07_pillar_earth_1994style.png',
       'air': 's07_pillar_air_1994style.png',
       'water': 's07_pillar_water_1994style.png'}
REG_ID = {'earth': '2024', 'air': '2025', 'water': '2026'}
REGISTRY = os.path.join(REPO, 'agents', 'map-populator', 'src', 'vignettes',
                        'art_registry.json')

KEY = 255
GEM = set(range(36, 47))
WARM = {54, 55, 61, 103} | set(range(228, 235))
MOTTLE = set(range(160, 176)) | {179, 185, 189} | set(range(194, 200)) \
    | set(range(209, 224))

RAMPS = {
    'earth': {'cap': list(range(163, 173)),
              'flare': list(range(163, 174)) + [214, 215, 216, 217],
              'mottle': None},
    'air': {'cap': [144, 145, 146, 240, 241, 242, 243],
            'flare': list(range(240, 250)),
            'mottle': list(range(241, 250))},
    'water': {'cap': list(range(136, 143)),
              'flare': list(range(148, 156)) + [136, 137],
              'mottle': [246, 247, 248, 249, 250, 251, 152]},
}


def lum(rgb):
    r, g, b = (c / 255.0 for c in rgb)
    return colorsys.rgb_to_hls(r, g, b)[1]


def column_mask(h, w):
    """The column's silhouette once its lower-left is drawn: x 16..36 from
    row 6 to row 91 (2023 itself shows x 23..36 below row 45)."""
    m = np.zeros((h, w), bool)
    m[6:92, 16:37] = True
    return m


def recolour(a, sel, ramp, pal):
    """Pixels `sel` of `a` onto `ramp` by stretched luminance."""
    if not sel.any():
        return
    src = a[sel]
    ls = np.array([lum(pal[i]) for i in src])
    lo, hi = ls.min(), ls.max()
    rl = np.array([lum(pal[i]) for i in ramp])
    t = (ls - lo) / (hi - lo) if hi > lo else np.full_like(ls, 0.5)
    want = rl.min() + t * (rl.max() - rl.min())
    a[sel] = np.array(ramp)[np.abs(want[:, None] - rl[None, :]).argmin(1)]


def build(fire, pal):
    h, w = fire.shape
    base = fire.copy()
    col = column_mask(h, w)
    # the hidden lower-left of the shaft, copied from the full rows above
    for r in range(46, 91):
        s = 10 + (r - 46) % 36
        for x in range(16, 23):
            if base[r, x] == KEY:
                base[r, x] = base[s, x]
    op = base != KEY
    gem = op & np.isin(base, list(GEM))
    gem[9:] = False
    warm = op & np.isin(base, list(WARM))
    flare = op & ~gem & (~col | warm)
    mottle = op & col & ~gem & ~warm & np.isin(base, list(MOTTLE))
    out = {}
    for el, rp in RAMPS.items():
        a = base.copy()
        recolour(a, gem, rp['cap'], pal)
        recolour(a, flare, rp['flare'], pal)
        if rp['mottle']:
            recolour(a, mottle, rp['mottle'], pal)
        assert not np.isin(a[a != KEY], list(range(1, 15))).any(), el
        out[el] = a
    return out


def main():
    img = Image.open(FIRE)
    assert img.mode == 'P', FIRE
    flat = img.getpalette()
    pal = [tuple(flat[3 * i:3 * i + 3]) for i in range(256)]
    fire = np.array(img)
    with open(REGISTRY) as f:
        reg = json.load(f)
    for el, a in build(fire, pal).items():
        o = Image.fromarray(a.astype(np.uint8), 'P')
        o.putpalette(flat)
        path = os.path.join(ART, OUT[el])
        o.save(path, transparency=KEY)
        fr = reg['shapes'][REG_ID[el]]['frames'][0]
        fr['opaque_px'] = int((a != KEY).sum())
        print(f'{el}: {path} ({fr["opaque_px"]} px)')
    with open(REGISTRY, 'w') as f:
        f.write(json.dumps(reg, indent=1) + '\n')


if __name__ == '__main__':
    main()

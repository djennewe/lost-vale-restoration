#!/usr/bin/env python3
"""
elixir_plate.py: the plate for art-track contract 11, Tyorvi's elixir
(shape 868, docs/art-track.md).

Renders the elixir out of the BUILT shared/build/U8SHAPES.FLX beside what
it must not be mistaken for: the blood vial it was until 2026-10-09 (base
395 frame 5, the necromancy reagent) and the eight potions of base 766.
One row at 6x for reading, one at 1x for the size the player sees:

    shared/docs/art-poc/elixir/elixir-plate.png

Needs the built artifacts (tools/build_artifacts.sh): the elixir exists
only once lv_art_props.py has injected it.

Usage:
    python3 tools/art/elixir_plate.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'agents', 'map-populator', 'src'))

from shape_viewer import (read_flx_entry, load_palette,          # noqa: E402
                          parse_shape_frames, frame_to_image,
                          PALETTE_FILE)
from lv_shapes import SHAPE_ELIXIR                               # noqa: E402
from PIL import Image, ImageDraw                                 # noqa: E402

BUILT = os.path.join(ROOT, 'shared', 'build', 'U8SHAPES.FLX')
OUT = os.path.join(ROOT, 'shared', 'docs', 'art-poc', 'elixir')
BG = (24, 24, 28)
INK = (210, 210, 215)


def row(entries, palette, scale, pad, label_h):
    imgs = [frame_to_image(f, palette, scale=scale, bg_color=BG)
            for _, f in entries]
    w = sum(i.width for i in imgs) + pad * (len(imgs) + 1)
    h = max(i.height for i in imgs) + pad * 2 + label_h
    img = Image.new('RGB', (w, h), BG)
    draw = ImageDraw.Draw(img)
    x = pad
    for (label, _), im in zip(entries, imgs):
        img.paste(im, (x, pad + label_h))
        if label_h:
            draw.text((x, 2), label, fill=INK)
        x += im.width + pad
    return img


def main():
    if not os.path.exists(BUILT):
        raise SystemExit(f'{BUILT} absent — run tools/build_artifacts.sh')
    data = open(BUILT, 'rb').read()
    pal = load_palette(PALETTE_FILE)
    elixir = read_flx_entry(data, SHAPE_ELIXIR)
    if not elixir:
        raise SystemExit(f'shape {SHAPE_ELIXIR} is not in {BUILT}')
    # Labels are short because a vial is 36 px wide at 6x.
    entries = [('868', parse_shape_frames(elixir)[0]),
               ('395.5', parse_shape_frames(read_flx_entry(data, 395))[5])]
    potions = parse_shape_frames(read_flx_entry(data, 766))
    entries += [(f'766.{i}', f) for i, f in enumerate(potions[:8])]

    big = row(entries, pal, 6, 12, 14)
    small = row(entries, pal, 1, 6, 0)
    sheet = Image.new('RGB', (big.width, big.height + small.height), BG)
    sheet.paste(big, (0, 0))
    sheet.paste(small, (0, big.height))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, 'elixir-plate.png')
    sheet.save(path)
    print(f'wrote {path} {sheet.size[0]}x{sheet.size[1]}')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
pillar_plates.py: the before-and-reference plates for art-track contract 5
(the elemental pillars 865 and their receptacles 866, docs/art-track.md).

Renders straight out of the BASE GAME's U8SHAPES.FLX, so it needs no build
artifacts and reproduces byte-for-byte on any clone with game data:

    shared/docs/art-poc/pillars/before-pillars-1x.png
    shared/docs/art-poc/pillars/before-pillars-4x.png    what Map 11 shows now
    shared/docs/art-poc/pillars/reference-ring-stones-4x.png
    shared/docs/art-poc/pillars/reference-talisman-gems.png

The before plate is the contract's evidence: shape 721 frames 0-3 are the
four "elemental pillars" (two stone chimneys and two red brick ones with an
open flue), and shape 307 is the "receptacle" (an ornate chest with a stag
on each door). The gem plate is the neighbouring finding: shape 596 frames
0-3, the four talismans as placed, are a flask, a ring and two gems, while
frames 4-7 of the same shape are a matched set of four.

Usage:
    python3 tools/art/pillar_plates.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'agents', 'map-populator', 'src'))

from shape_viewer import (read_flx_entry, load_palette,          # noqa: E402
                          parse_shape_frames, frame_to_image,
                          SHAPES_FLX, PALETTE_FILE)
from PIL import Image, ImageDraw                                 # noqa: E402

OUT = os.path.join(ROOT, 'shared', 'docs', 'art-poc', 'pillars')
BG = (24, 24, 28)
INK = (210, 210, 215)


def sheet(entries, palette, scale, path, pad=12, label_h=14):
    """entries: [(label, frame)] -> one labelled contact sheet."""
    imgs = [frame_to_image(f, palette, scale=scale, bg_color=BG)
            for _, f in entries]
    w = sum(i.width for i in imgs) + pad * (len(imgs) + 1)
    h = max(i.height for i in imgs) + pad * 2 + label_h
    sh = Image.new('RGB', (w, h), BG)
    draw = ImageDraw.Draw(sh)
    x = pad
    for (label, _), img in zip(entries, imgs):
        sh.paste(img, (x, pad + label_h))
        draw.text((x, 2), label, fill=INK)
        x += img.width + pad
    sh.save(path)
    print(f'wrote {path} {sh.size[0]}x{sh.size[1]}')


def main():
    data = open(SHAPES_FLX, 'rb').read()
    palette = load_palette(PALETTE_FILE)

    def frames(shape):
        return parse_shape_frames(read_flx_entry(data, shape))

    os.makedirs(OUT, exist_ok=True)
    pillar, recept = frames(721), frames(307)
    # Element labels are the MAP's frame order (build_map_11.py), which the
    # 2026-07-04 decision fixed and the dialogue doc's bark table missed.
    before = [('721 f0  Earth', pillar[0]), ('721 f1  Air', pillar[1]),
              ('721 f2  Fire', pillar[2]), ('721 f3  Water', pillar[3]),
              ('307 f0  receptacle', recept[0])]
    sheet(before, palette, 4, os.path.join(OUT, 'before-pillars-4x.png'))
    sheet([(lab.split()[0] + ' ' + lab.split()[1], f) for lab, f in before],
          palette, 1, os.path.join(OUT, 'before-pillars-1x.png'))

    gem = frames(596)
    sheet([('596 f0  Earth', gem[0]), ('596 f1  Air', gem[1]),
           ('596 f2  Fire', gem[2]), ('596 f3  Water', gem[3])],
          palette, 8, os.path.join(OUT, 'reference-talisman-gems.png'))

    stone = frames(38)
    sheet([(f'38 f{i}', stone[i]) for i in range(4)],
          palette, 4, os.path.join(OUT, 'reference-ring-stones-4x.png'))


if __name__ == '__main__':
    main()

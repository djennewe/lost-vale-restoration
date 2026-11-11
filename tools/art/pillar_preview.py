#!/usr/bin/env python3
"""
pillar_preview.py: game-scale previews for art-track contract 5 candidates.

"Judge a candidate at game scale, never at 1024" is the track's recorded
lesson (the Sacred Rock's keyline and grey both vanished in the U8PAL
quantize). So every candidate goes through the SAME pipeline the build
would run, png2shape.build_frame (key, trim, resize, despill, quantize,
encode), is decoded back as the engine would draw it, and is rendered:

  * at two heights the contract leaves open, 72 px (footpad (4,4,5), the
    64x72 box, z=5) and 96 px (footpad (4,4,8), the 64x96 box, z=8);
  * at 1x beside the chimney it replaces (721 f0, 56 px) and a ring stone
    (38 f2, 59 px) for scale, and at 4x on its own;
  * with a PALETTE CHECK: the top palette indices of each frame. Element
    identity survives only as distinct hues, so if two of the four frames
    share their three most-used indices the candidate has failed at game
    scale whatever the raw looks like, and the report says so.

The receptacle candidate goes through the same pipeline at 40 px (footpad
(3,3,3), the 48x48 box) beside the chest it replaces (307 f0).

Outputs, under shared/docs/art-poc/pillars/:
    <cand>_preview_h72.png, <cand>_preview_h96.png   (1x strip + 4x strip)
    R_preview_h40.png
    preview_report.json                               (sizes, fit, palettes)

Usage:
    python3 tools/art/pillar_preview.py A B C        # candidates on disk
    python3 tools/art/pillar_preview.py --receptacle R
"""

import json
import os
import sys
from collections import Counter
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(HERE, '..'))   # tools/png2shape.py
sys.path.insert(0, os.path.join(ROOT, 'agents', 'map-populator', 'src'))

from PIL import Image, ImageDraw                                  # noqa: E402
from png2shape import build_frame, footpad_screen_size            # noqa: E402
from lv_wood_wall import encode_shape_blobs                       # noqa: E402
from shape_viewer import (read_flx_entry, load_palette,           # noqa: E402
                          parse_shape_frames, frame_to_image,
                          SHAPES_FLX, PALETTE_FILE)

OUT = os.path.join(ROOT, 'shared', 'docs', 'art-poc', 'pillars')
MAGENTA = (255, 0, 255)
BG = (24, 24, 28)
INK = (210, 210, 215)
ELEMENTS = ('earth', 'air', 'fire', 'water')
PILLAR_HEIGHTS = {72: (4, 4, 5), 96: (4, 4, 8)}
RECEPTACLE_HEIGHT = {40: (3, 3, 3)}


def args_for(height, donor):
    """The build's own recipe: flat-magenta key at tolerance 130, despill
    16, bottom-centre anchor (lv_art_props.frame_args)."""
    return SimpleNamespace(
        no_key=False, key_rgb=MAGENTA, key_tolerance=130, key_despill=16,
        no_trim=False, height=height, width=None, alpha_threshold=128,
        anchor='bottom-center', donor=donor, xoff=None, yoff=None)


def decode(blobs):
    return parse_shape_frames(encode_shape_blobs(blobs))


def top_indices(frame, n=3, exclude=()):
    c = Counter(p for p in frame['pixels'] if p != 0xFF and p not in exclude)
    return [i for i, _ in c.most_common(n)]


def element_tops(frames, n=3, family_depth=6):
    """The palette indices that carry each frame's IDENTITY. The shaft is
    the same stone on every frame, so its indices dominate every histogram
    and a plain top-n says "they all match". Family indices are those in
    every frame's top family_depth; each frame's element indices are its
    top-n with the family removed. Two frames with the same element top-n
    are the same colour at game scale, whatever the raw looked like."""
    tops = [set(top_indices(f, family_depth)) for f in frames]
    family = set.intersection(*tops) if tops else set()
    return [top_indices(f, n, exclude=family) for f in frames], sorted(family)


def strip(entries, palette, scale, pad=10, label_h=13):
    # At 1x the sprites are narrower than their labels, so the labels
    # collide; the 1x strip carries no labels and its caption lives in the
    # page that shows it.
    if scale == 1:
        label_h, pad = 0, 6
    imgs = [frame_to_image(f, palette, scale=scale, bg_color=BG)
            for _, f in entries]
    w = sum(i.width for i in imgs) + pad * (len(imgs) + 1)
    h = max(i.height for i in imgs) + pad * 2 + label_h
    sh = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(sh)
    x = pad
    for (lab, _), im in zip(entries, imgs):
        # bottom-align so the feet share a line, as they do on a floor
        sh.paste(im, (x, h - pad - im.height))
        if label_h:
            d.text((x, 2), lab, fill=INK)
        x += im.width + pad
    return sh


def stack(plates, pad=10):
    w = max(p.width for p in plates)
    h = sum(p.height for p in plates) + pad * (len(plates) - 1)
    out = Image.new('RGB', (w, h), BG)
    y = 0
    for p in plates:
        out.paste(p, (0, y))
        y += p.height + pad
    return out


def preview(cand, frames_paths, heights, donor, refs, palette, flx, report):
    """One candidate, every height: (blobs, report rows, plates)."""
    for height, footpad in heights.items():
        blobs, rows = [], []
        for i, p in enumerate(frames_paths):
            blob, rep = build_frame(p, args_for(height, donor), palette,
                                    flx, i)
            blobs.append(blob)
            rows.append(rep)
        frames = decode(blobs)
        box = footpad_screen_size(*footpad)
        fits = [r['size'][0] <= box[0] and r['size'][1] <= box[1]
                for r in rows]
        tops, family = element_tops(frames)
        clashes = [(a, b) for a in range(len(tops)) for b in range(a + 1,
                   len(tops)) if tops[a] == tops[b]]
        entries = refs + [(f'{cand} f{i}', f) for i, f in enumerate(frames)]
        one = strip(entries, palette, 1)
        four = strip([(f'{cand} f{i}  {r["size"][0]}x{r["size"][1]}', f)
                      for i, (f, r) in enumerate(zip(frames, rows))],
                     palette, 4)
        path = os.path.join(OUT, f'{cand}_preview_h{height}.png')
        stack([one, four]).save(path)
        one.save(os.path.join(OUT, f'{cand}_h{height}_1x.png'))
        four.save(os.path.join(OUT, f'{cand}_h{height}_4x.png'))
        report[f'{cand}_h{height}'] = {
            'height': height, 'footpad': footpad, 'box': box,
            'frames': [{'size': r['size'], 'colors': r['colors'],
                        'fits_box': fit, 'top_palette': t}
                       for r, fit, t in zip(rows, fits, tops)],
            'family_palette': family,
            'palette_clashes': clashes, 'plate': os.path.basename(path),
        }
        print(f'{cand} @ {height}px footpad {footpad} box {box}: '
              + ', '.join(f'f{i} {r["size"][0]}x{r["size"][1]}'
                          f'{"" if fit else " OVER BOX"}'
                          for i, (r, fit) in enumerate(zip(rows, fits)))
              + (f'  PALETTE CLASH {clashes}' if clashes else '  hues distinct'))


def main(argv):
    data = open(SHAPES_FLX, 'rb').read()
    palette = load_palette(PALETTE_FILE)

    def base(shape, frame):
        return parse_shape_frames(read_flx_entry(data, shape))[frame]

    report = {}
    if '--receptacle' in argv:
        i = argv.index('--receptacle')
        cands = argv[i + 1:]
        refs = [('307 f0 chest', base(307, 0))]
        for cand in cands:
            preview(cand, [os.path.join(OUT, f'{cand}_raw.png')],
                    RECEPTACLE_HEIGHT, 443, refs, palette, data, report)
        argv = argv[:i]
    refs = [('721 f0 chimney', base(721, 0)), ('38 f2 ring stone', base(38, 2))]
    for cand in argv:
        paths = [os.path.join(OUT, f'{cand}_f{i}_{e}_raw.png')
                 for i, e in enumerate(ELEMENTS)]
        missing = [p for p in paths if not os.path.exists(p)]
        if missing:
            print(f'{cand}: frames missing, run split_sheet.py first: '
                  f'{[os.path.basename(m) for m in missing]}')
            continue
        preview(cand, paths, PILLAR_HEIGHTS, 38, refs, palette, data, report)
    rp = os.path.join(OUT, 'preview_report.json')
    old = json.load(open(rp)) if os.path.exists(rp) else {}
    old.update(report)
    json.dump(old, open(rp, 'w'), indent=1)
    print('report ->', rp)


if __name__ == '__main__':
    main(sys.argv[1:])

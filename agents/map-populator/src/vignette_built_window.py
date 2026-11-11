"""vignette_built_window.py — paint a shot's window from the BUILT FIXED.DAT
in engine draw order, with the BUILT U8SHAPES.FLX and TYPEFLAG.DAT (so the
art track's shapes draw as the game draws them), and diff it with the 1994
GIF.

usage: python3 vignette_built_window.py [--actors] screenNN out.png

Items: every map item (globs expanded) within +/-4000 world units of the
vignette, generous enough that anything whose sprite reaches the window is
painted. Prints the all-frame match (palette RGB within 12; a pixel nothing
paints counts only if the shot is black there) and the palette-class match
vignette_replay.py reports, and writes shot | built | diff at x3.

--actors adds the vignette's rendered actors (the Avatar, NPCs, and the
`built` 1994 actors lv_actor_art.py derives) at their recorded spots, as
vignette_replay.py --built does. A built map holds no Avatar, so without
them the window scores below the replay by the actors' pixels; with them
the two numbers are directly comparable. An actor carrying `npcnum` is
that map NPC in the shot's pose, so it is painted in place of the map's
start record for the same npcnum, never beside it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

SRC = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(SRC, '..', '..', '..'))
sys.path.insert(0, SRC)
import shot_decompose as SD  # noqa: E402
import vignette_place as V  # noqa: E402
from glob_catalog import GlobReader  # noqa: E402
from u8_map import MapArchive  # noqa: E402
from vignette_paint import Painter  # noqa: E402


def window(shot, actors=False, fixed=None, painter=None):
    """Paint `shot`'s window from the built FIXED.DAT (or `fixed`).

    Returns (out, rgb, rgb_score, class_score): `out` the palette indices
    painted (-1 where nothing paints), `rgb` the 1994 shot, the all-frame
    RGB-within-12 score and the palette-class score, both in percent."""
    v = V.load(shot)
    ox, oy, oz = V.origin(v)
    mp = v['placement']['map']
    arch = MapArchive(fixed or os.path.join(REPO, 'shared', 'build', 'FIXED.DAT'))
    gr = GlobReader()
    cam = v['camera']
    csx = cam['sx0'] + (ox // 4 - oy // 4)
    csy = cam['sy0'] + (ox // 8 + oy // 8 - oz)
    _, (H, W), rgb = SD.load_shot(shot)
    # Cull round the window's own ground point (its centre projected to z 0),
    # not round the origin: a vignette whose local coordinates are large (the
    # Map 13 shots sit 3,000-6,000 units from theirs) lost most of its window.
    cx = 2 * (csx + W // 2) + 4 * (csy + H // 2)
    cy = 4 * (csy + H // 2) - 2 * (csx + W // 2)
    shown = {(a['npcnum'], a['shape']) for a in v['actors']
             if actors and 'npcnum' in a and not a.get('unrendered')}
    items = []
    for it in arch.get_map_items(mp):
        if abs(it.x - cx) > 4000 or abs(it.y - cy) > 4000:
            continue
        if it.is_glob_egg:
            items += [dict(shape=g.shape, frame=g.frame, x=g.x, y=g.y, z=g.z)
                      for g in gr.glob_to_items(it.quality, it.x, it.y, it.z)]
        elif (it.npcnum, it.shape) in shown:
            continue
        else:
            items.append(dict(shape=it.shape, frame=it.frame, x=it.x, y=it.y, z=it.z))
    if actors:
        for a in v['actors']:
            if a.get('unrendered'):
                continue
            items.append(dict(shape=a['shape'], frame=a['frame'], x=a['x'] + ox,
                              y=a['y'] + oy, z=a['z'] + oz, flags=a.get('flags', 0)))
    out, _ = (painter or Painter.built()).paint(items, csx, csy, W, H)
    pal = SD.PAL
    m = out >= 0
    eq = (np.abs(pal[np.where(m, out, 0)] - rgb).sum(-1) <= 12) & m
    blank = (~m) & (rgb.sum(-1) <= 12)
    sidx = np.abs(rgb[:, :, None, :].astype(int) - pal[None, None]).sum(-1).argmin(-1)
    cls = m & (SD.CLS[np.where(m, out, 0)] == SD.CLS[sidx])
    return (out, rgb, (eq | blank).sum() / (H * W) * 100,
            cls.sum() / (H * W) * 100)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('shot')
    ap.add_argument('out_png')
    ap.add_argument('--actors', action='store_true',
                    help="paint the vignette's rendered retail actors too")
    args = ap.parse_args()
    out, rgb, rgb_score, cls_score = window(args.shot, args.actors)
    pal = SD.PAL
    m = out >= 0
    print(f'{args.shot}: built-window all-frame match {rgb_score:.2f}% '
          f'class {cls_score:.2f}% '
          f'(unpainted {(~m).sum()} px{", actors" if args.actors else ""})')
    H, W = out.shape
    eq = (np.abs(pal[np.where(m, out, 0)] - rgb).sum(-1) <= 12) & m
    blank = (~m) & (rgb.sum(-1) <= 12)
    o = np.zeros((H, W, 3), np.uint8)
    o[m] = pal[out[m]]
    dif = rgb.astype(np.uint8).copy()
    bad = ~(eq | blank)
    dif[bad] = (dif[bad] * 0.3 + np.array([255, 0, 0]) * 0.7).astype(np.uint8)
    Image.fromarray(np.concatenate([rgb.astype(np.uint8), o, dif], 1)) \
        .resize((W * 9, H * 3), Image.NEAREST).save(args.out_png)


if __name__ == '__main__':
    main()

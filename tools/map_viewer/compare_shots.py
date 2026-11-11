#!/usr/bin/env python3
"""compare_shots.py -- score the map viewer's tiles against ScummVM shots.

For each in-engine screenshot below (docs/playtest-*), cut the same window
out of the viewer's 1x tiles, find the pixel offset that matches best (the
engine's camera does not sit exactly on the logged Avatar position), and
write compare/<name>.png: the shot, the viewer at the shot's scale, and in
magenta every pixel that differs by more than TOL in any channel. Prints
the share of matching pixels; the README quotes it.

    python3 tools/map_viewer/compare_shots.py \\
        --data-root ~/projects/lost-vale \\
        --out /tmp/claude-1000/gallery/maps
"""

import argparse
import json
import os
import re

import numpy as np
from PIL import Image

TOL = 12
SEARCH = 8   # +/- pixels around the anchor

# name, map, shot (under docs/), the logged Avatar or item position, where
# that point falls in the shot at 1x, the shot's scale.
SHOTS = [
    ('plateau', 10, 'playtest-2026-10-11-static-art/'
     'P1-test-plant-871-plateau-1x.png', (12800, 29408, 64), (84, 139), 1),
    ('sacred-circle', 10, 'playtest-2026-10-11-static-art/'
     'R1-root-869-east-stone-1x.png', (21376, 16640, 0), (167, 154), 1),
    ('lake-deck', 10, 'playtest-2026-10-12-monsters3/P3-deck-fight.png',
     (14075, 18242, 8), (159, 120), 2),
    ('map13-arrival', 13, 'playtest-2026-10-11-full-run-part6/'
     's13-01-m13-arrival.png', (4096, 11880, 0), (160, 120), 2),
    ('map17-arrival', 17, 'playtest-2026-10-11-replay-leg4/'
     'D3-m17-cloud-city-arrival.png', (5376, 11136, 0), (134, 133), 2),
    ('map18-arrival', 18, 'playtest-2026-10-11-replay-leg5/'
     'A2-m18-arrival.png', (3072, 1792, 0), (218, 91), 2),
]


def tdiv(a, b):
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q


def window(out, m, left, top, w, h):
    page = open(os.path.join(out, f'map{m:02d}.html'), encoding='utf-8').read()
    cfg = json.loads(re.search(r'const C = (\{.*?\});\n', page, re.S).group(1))
    ox, oy = cfg['origin']
    T = cfg['tile']
    im = Image.new('RGB', (w, h))
    for tx in range((left - ox) // T, (left + w - ox) // T + 1):
        for ty in range((top - oy) // T, (top + h - oy) // T + 1):
            p = os.path.join(out, f'map{m:02d}', 'base', '0',
                             f'{tx}_{ty}.{cfg["ext"]}')
            if os.path.exists(p):
                im.paste(Image.open(p), (ox + tx * T - left, oy + ty * T - top))
    return np.asarray(im).astype(np.int16)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--data-root', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    cdir = os.path.join(args.out, 'compare')
    os.makedirs(cdir, exist_ok=True)
    lines = []
    for name, m, shot, (x, y, z), (ax, ay), k in SHOTS:
        e = Image.open(os.path.join(args.data_root, 'docs', shot)).convert('RGB')
        e1 = np.asarray(e)[k // 2::k, k // 2::k].astype(np.int16)
        h, w = e1.shape[:2]
        sx = tdiv(x, 4) - tdiv(y, 4)
        sy = tdiv(x, 8) + tdiv(y, 8) - z
        R = SEARCH
        big = window(args.out, m, sx - ax - R, sy - ay - R, w + 2 * R, h + 2 * R)
        best = max(((np.abs(big[dy:dy + h, dx:dx + w] - e1).max(2) <= TOL).mean(),
                    dx, dy) for dy in range(2 * R + 1) for dx in range(2 * R + 1))
        score, bx, by = best
        mine = big[by:by + h, bx:bx + w]
        diff = np.zeros((h, w, 3), np.uint8)
        diff[np.abs(mine - e1).max(2) > TOL] = (255, 0, 255)
        s = 2 if k == 1 else k
        ww, hh = w * s, h * s
        sheet = Image.new('RGB', (3 * ww + 16, hh), (60, 60, 60))
        for i, a in enumerate((e1, mine, diff)):
            sheet.paste(Image.fromarray(a.astype(np.uint8)).resize(
                (ww, hh), Image.NEAREST), (i * (ww + 8), 0))
        sheet.save(os.path.join(cdir, f'{name}.png'))
        line = (f'{name:14s} map {m:2d}  {shot.split("/")[-1]} ({k}x)  '
                f'offset ({bx - R:+d},{by - R:+d})  '
                f'{score:6.1%} of pixels within {TOL}/255')
        print(line)
        lines.append(line)
    with open(os.path.join(cdir, 'results.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
pillar_plinth.py: put sheet C3's plinth under the columns cut from sheet C2.

Art-track contract 5 landed Earth and Air from candidate sheet C2 and Fire
and Water from C3 (Douglas's frame mix, 2026-09-24). The two sheets drew
the same isometric plinth (246 px wide, top vertex near row 758, foot at
row 1023 in every cut frame) in different stone: C2's is violet, C3's is
the ring stones' blue-grey. In the chamber the four columns read as one
family and the plinths split them into a north pair and a south pair
(playtest 2026-09-24, finding 2). This script rebuilds the two C2 frames
on C3's plinth so all four stand on the same block.

How:

  * C2's plinth in each frame is the connected component of violet pixels
    (blue well above an equal red and green) that holds the side faces.
    Connectivity matters because the Air twister's shading uses the same
    blues over the top face; enclosed by the twister's grey and its dark
    outline, that shading forms its own components and is left alone.
  * A clean C3 plinth is assembled from C3's Fire and Earth frames (warm
    columns, so the blue-grey plinth is everything that is not red over
    blue) and its Water frame (a saturated column against the plinth's low
    saturation); C3's Air frame is pale grey itself and is left out. Every
    C3 column covers the whole top face, so the top face is never observed
    there: it is filled with C2 Air's top-face texture re-coloured from
    C2's top-face mean to the mean of the rim the donors do show. A dark
    donor pixel inside the top face is a column's own outline and counts as
    unobserved. What is left (the twister's tip) fills by mirroring across
    the plinth's axis, then from the nearest plinth pixel in the column.
  * Each C2 frame then has its plinth component replaced pixel for pixel
    by the clean plinth (aligned on the plinth's left edge). Everything
    else, the column included, stays. Anti-aliased edge pixels between
    column and plinth that fail the violet test survive as a fringe one
    pixel wide at 1024, which the 10x downscale to 96 px removes.

Outputs, under shared/docs/art-poc/pillars/:
    C2_f0_earth_c3plinth_raw.png, C2_f1_air_c3plinth_raw.png   (build inputs)
    plinth_check.png    the clean plinth, its holes in red, both results
    plinth_report.json  counts, alignment offsets, the two means

Usage:
    python3 tools/art/pillar_plinth.py
"""

import json
import os
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'shared', 'docs', 'art-poc', 'pillars')

from PIL import Image  # noqa: E402

PLINTH_TOP = 740        # above the top vertex (row 758) in every frame
BODY_ROWS = (870, 960)  # rows where the plinth is its full 246 px wide
SEED_ROW = 950          # a side-face row, for the connected component
TOP_FACE_RED = 85       # C2's top face is the light stone: red above this

# (frame, test for "this pixel is plinth, not column")
DONORS = [('C3_f2_fire_raw.png', 'cool'), ('C3_f0_earth_raw.png', 'cool'),
          ('C3_f3_water_raw.png', 'dull')]
TEXTURE = 'C2_f1_air_raw.png'   # the clearest C2 top face
TARGETS = [('C2_f0_earth_raw.png', 'C2_f0_earth_c3plinth_raw.png'),
           ('C2_f1_air_raw.png', 'C2_f1_air_c3plinth_raw.png')]


def is_key(p):
    """The magenta key: red and blue above 140 with green under 110."""
    return p[0] > 140 and p[2] > 140 and p[1] < 110


def is_violet(p):
    """C2's plinth stone: blue well above an equal red and green."""
    return (not is_key(p)) and p[2] - p[0] > 35 and p[2] - p[1] > 35 \
        and abs(p[0] - p[1]) < 25


def is_cool(p):
    """Plinth against a warm column (Fire, Earth): blue not below red."""
    return (not is_key(p)) and p[2] >= p[0] - 5


def is_dull(p):
    """Plinth against the saturated Water column: low saturation."""
    return (not is_key(p)) and max(p) - min(p) < 45 and p[2] >= p[0] - 5


TESTS = {'cool': is_cool, 'dull': is_dull}


def load(name):
    im = Image.open(os.path.join(OUT, name)).convert('RGB')
    return im, im.load()


def left_edge(px, w):
    """Leftmost and rightmost content x in the plinth's full-width rows."""
    xs = [x for y in range(*BODY_ROWS) for x in range(w)
          if not is_key(px[x, y])]
    return min(xs), max(xs)


def c2_plinth(im, px):
    """The violet component holding the side faces: {(x, y): colour}."""
    w, h = im.size
    lo, hi = left_edge(px, w)
    seed = next((x, SEED_ROW) for x in range(lo, hi)
                if is_violet(px[x, SEED_ROW]))
    comp = {seed: px[seed]}
    todo = deque([seed])
    while todo:
        x, y = todo.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and PLINTH_TOP <= ny < h \
                    and (nx, ny) not in comp and is_violet(px[nx, ny]):
                comp[(nx, ny)] = px[nx, ny]
                todo.append((nx, ny))
    return comp, lo


def clean_plinth():
    """(x, y) -> colour for every plinth pixel, in donor-0 coordinates."""
    tex_im, tex_px = load(TEXTURE)
    texture, tex_lo = c2_plinth(tex_im, tex_px)
    x0 = None
    plinth = {}
    footprint = set()
    for name, test in DONORS:
        is_plinth = TESTS[test]
        im, px = load(name)
        lo, hi = left_edge(px, im.width)
        if x0 is None:
            x0, x1 = lo, hi
            shift_tex = x0 - tex_lo
            top = {(x + shift_tex, y): p for (x, y), p in texture.items()
                   if p[0] > TOP_FACE_RED}
        shift = x0 - lo
        for y in range(PLINTH_TOP, im.height):
            for x in range(im.width):
                p = px[x, y]
                if is_key(p):
                    continue
                k = (x + shift, y)
                footprint.add(k)
                if is_plinth(p) and k not in plinth \
                        and (k not in top or sum(p) > 240):
                    plinth[k] = p
    # Holes: the whole C2 plinth outline, plus footprint pixels that have
    # plinth on both sides in their row, minus what the donors gave.
    outline = {(x + shift_tex, y) for (x, y) in texture}
    rows = {}
    for (x, y) in plinth:
        lo, hi = rows.get(y, (x, x))
        rows[y] = (min(lo, x), max(hi, x))
    top_row = min(y for (x, y) in outline)
    inside = {(x, y) for (x, y) in footprint
              if y >= top_row and y in rows and rows[y][0] < x < rows[y][1]}
    holes = (outline | inside) - set(plinth)
    from_donors = len(plinth)
    # Top face: C2's texture, re-coloured to the rim the donors show.
    c2_mean = [sum(p[i] for p in top.values()) / len(top) for i in range(3)]
    rim = [plinth[k] for k in top if k in plinth]
    c3_mean = [sum(p[i] for p in rim) / len(rim) for i in range(3)]
    filled_top = 0
    for k in holes:
        if k in top:
            p = top[k]
            plinth[k] = tuple(max(0, min(255, int(round(
                c3_mean[i] * p[i] / c2_mean[i])))) for i in range(3))
            filled_top += 1
    axis = (x0 + x1) / 2
    filled_mirror = 0
    for (x, y) in sorted(holes):
        if (x, y) in plinth:
            continue
        mx = int(round(2 * axis - x))
        if (mx, y) in plinth and (mx, y) not in holes:
            plinth[(x, y)] = plinth[(mx, y)]
            filled_mirror += 1
    still = [h for h in holes if h not in plinth]
    filled_near = 0
    for (x, y) in sorted(still):
        for d in range(1, 300):
            hit = next(((x, yy) for yy in (y - d, y + d)
                        if (x, yy) in plinth and (x, yy) not in still), None)
            if hit:
                plinth[(x, y)] = plinth[hit]
                filled_near += 1
                break
    left = [h for h in holes if h not in plinth]
    stats = {'footprint': len(footprint), 'outline': len(outline),
             'from_donors': from_donors, 'holes': len(holes),
             'filled_top': filled_top, 'filled_mirror': filled_mirror,
             'filled_nearest': filled_near, 'unfilled': len(left),
             'c2_top_mean': [round(v) for v in c2_mean],
             'c3_top_rim_mean': [round(v) for v in c3_mean],
             'rim_px': len(rim)}
    return plinth, x0, stats, holes


def replace(target, plinth, plinth_x0):
    im, px = load(target)
    comp, lo = c2_plinth(im, px)
    shift = lo - plinth_x0
    replaced = missing = 0
    for (x, y) in comp:
        q = plinth.get((x - shift, y))
        if q is None:
            missing += 1
            continue
        px[x, y] = q
        replaced += 1
    return im, {'shift': shift, 'component': len(comp),
                'replaced': replaced, 'no_plinth_pixel': missing}


def main():
    plinth, x0, stats, holes = clean_plinth()
    report = {'plinth': stats, 'plinth_x0': x0, 'frames': {}}
    results = []
    for src, dst in TARGETS:
        im, st = replace(src, plinth, x0)
        im.save(os.path.join(OUT, dst))
        report['frames'][dst] = st
        results.append((dst, im))
        print(f'{dst}: component {st["component"]} px, replaced '
              f'{st["replaced"]}, shift {st["shift"]}, no plinth pixel for '
              f'{st["no_plinth_pixel"]}')
    # check plate: clean plinth, holes in red, then each result's base
    w, top_row = 256, PLINTH_TOP - 20
    plate = Image.new('RGB', ((w + 10) * (2 + len(results)) - 10,
                              1024 - top_row), (24, 24, 24))
    canvas = Image.new('RGB', (w, 1024), (255, 0, 255))
    cp = canvas.load()
    for (x, y), p in plinth.items():
        if 0 <= x < w:
            cp[x, y] = p
    plate.paste(canvas.crop((0, top_row, w, 1024)), (0, 0))
    marked = canvas.copy()
    mp = marked.load()
    for (x, y) in holes:
        if 0 <= x < w:
            mp[x, y] = (255, 0, 0)
    plate.paste(marked.crop((0, top_row, w, 1024)), (w + 10, 0))
    for i, (dst, im) in enumerate(results):
        plate.paste(im.crop((0, top_row, min(im.width, w), 1024)),
                    ((w + 10) * (2 + i), 0))
    plate.save(os.path.join(OUT, 'plinth_check.png'))
    json.dump(report, open(os.path.join(OUT, 'plinth_report.json'), 'w'),
              indent=1)
    print('plinth:', stats)
    print('check plate ->', os.path.join(OUT, 'plinth_check.png'))


if __name__ == '__main__':
    main()

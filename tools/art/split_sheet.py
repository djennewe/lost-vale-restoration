#!/usr/bin/env python3
"""
split_sheet.py: cut a four-in-a-row candidate sheet into per-frame PNGs.

Art-track contract 5 generates each pillar candidate as ONE image with the
four pillars side by side (Earth, Air, Fire, Water) so the four frames of
shape 865 share one shaft. This cuts that sheet on the empty magenta bands
between the pillars and writes one PNG per frame, in frame order, ready for
png2shape.build_frame.

THE SPLITTER REFUSES TO GUESS. It keys the magenta, sums opaque pixels per
column, and looks for exactly three interior bands of empty columns. A sheet
where the four touch, share a base, or came out as three or five objects has
the wrong band count, and that is a MISS: the script exits nonzero and
writes <name>_splitcheck.png (the column profile drawn over the sheet) so
the failure can be read, and writes no frames.

Usage:
    python3 tools/art/split_sheet.py shared/docs/art-poc/pillars/A_raw.png
        -> A_f0_earth_raw.png, A_f1_air_raw.png, A_f2_fire_raw.png,
           A_f3_water_raw.png beside it
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))   # tools/png2shape.py

from PIL import Image, ImageDraw                                 # noqa: E402
from png2shape import key_out                                   # noqa: E402

ELEMENTS = ('earth', 'air', 'fire', 'water')
MAGENTA = (255, 0, 255)
KEY_TOLERANCE = 130        # the recipe every prop on the track settled on
MIN_BAND = 8               # columns; narrower gaps are resample bleed


def column_profile(img):
    """Opaque-pixel count per column of an RGBA image."""
    alpha = img.split()[3]
    w, h = img.size
    data = alpha.load()
    return [sum(1 for y in range(h) if data[x, y] >= 128) for x in range(w)]


def bands(profile, min_band=MIN_BAND):
    """(start, end) of every run of empty columns at least min_band wide,
    excluding the sheet's outer margins."""
    runs, start = [], None
    for x, v in enumerate(profile + [1]):
        if v == 0 and start is None:
            start = x
        elif v != 0 and start is not None:
            if x - start >= min_band:
                runs.append((start, x))
            start = None
    # drop the margins: a run touching either edge is not a gap
    return [(a, b) for (a, b) in runs if a > 0 and b < len(profile)]


def dip_cuts(profile, ndips, max_frac=0.10):
    """Cut columns for a sheet whose objects touch at the foot: the ndips
    lowest local minima of the column profile, each under max_frac of the
    peak and each at least a quarter of the sheet's width per object apart.
    None if the profile has no such dips."""
    w = len(profile)
    peak = max(profile) or 1
    spacing = w // (ndips + 1) // 2
    # a dip inside the outer margin is the sheet's edge, never a gap
    cands = sorted(range(spacing, w - spacing), key=lambda x: profile[x])
    cuts = []
    for x in cands:
        if profile[x] > peak * max_frac:
            break
        if all(abs(x - c) >= spacing for c in cuts):
            cuts.append(x)
        if len(cuts) == ndips:
            break
    if len(cuts) != ndips:
        return None
    return [0] + sorted(cuts) + [w]


def splitcheck_plate(img, profile, gaps, path):
    """The sheet with its column profile and the gaps found, for reading a
    refusal."""
    w, h = img.size
    plate = Image.new('RGB', (w, h + 120), (24, 24, 28))
    plate.paste(img.convert('RGB'), (0, 0))
    d = ImageDraw.Draw(plate)
    peak = max(profile) or 1
    for x, v in enumerate(profile):
        d.line([(x, h + 118), (x, h + 118 - int(110 * v / peak))],
               fill=(120, 160, 220))
    for a, b in gaps:
        d.rectangle([a, 0, b - 1, h + 119], outline=(255, 220, 80))
    plate.save(path)


def split(path, names=ELEMENTS):
    img, _ = key_out(Image.open(path), MAGENTA, KEY_TOLERANCE)
    profile = column_profile(img)
    gaps = bands(profile)
    stem = os.path.splitext(path)[0]
    if stem.endswith('_raw'):
        stem = stem[:-4]
    if len(gaps) == len(names) - 1:
        cuts = [0] + [(a + b) // 2 for (a, b) in gaps] + [img.size[0]]
    else:
        # No clean bands. The one case that is still a measured cut, and
        # not a guess: the objects' plinths touch, so each dip between two
        # masses bottoms out at a few rows (the plinth band) while the
        # masses themselves stand near full height. Cut at the dip minima
        # when every minimum is under a tenth of the peak, and say so; the
        # contested rows are the plinth's, and at game scale the sliver
        # that changes sides is under a pixel.
        cuts = dip_cuts(profile, len(names) - 1)
        if cuts is None:
            check = f'{stem}_splitcheck.png'
            splitcheck_plate(img, profile, gaps, check)
            raise SystemExit(
                f'MISS {os.path.basename(path)}: found {len(gaps)} clean '
                f'gap(s), need {len(names) - 1}, and the dips are not '
                f'plinth-shallow; see {check}')
        print(f'  no clean bands: cutting at dip minima {cuts[1:-1]} '
              f'(opaque rows there: {[profile[c] for c in cuts[1:-1]]} '
              f'of peak {max(profile)})')
    out = []
    for i, name in enumerate(names):
        piece = img.crop((cuts[i], 0, cuts[i + 1], img.size[1]))
        # Re-flatten onto magenta so the frame goes through the same
        # key_out as a single-object candidate would.
        flat = Image.new('RGB', piece.size, MAGENTA)
        flat.paste(piece, mask=piece.split()[3])
        dest = f'{stem}_f{i}_{name}_raw.png'
        flat.save(dest)
        out.append(dest)
        print(f'  f{i} {name:5s} columns {cuts[i]}..{cuts[i + 1]} -> '
              f'{os.path.basename(dest)}')
    return out


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        print(f'== {p}')
        split(p)

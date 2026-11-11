#!/usr/bin/env python3
"""
lv_map13_views.py — Map 13's 1994 windows (build_map_13.VIGNETTES) on the
built map, and the fit that keeps them (screenshot reconstruction phase B,
2026-10-17).

    python3 lv_map13_views.py            # scores + evidence, built FIXED.DAT
    python3 lv_map13_views.py --fit      # recompute map13_window_fit.json

SCORES, per shot, all-frame, from shared/build/FIXED.DAT (globs expanded):

  built   vignette_built_window.py's own number (palette RGB within 12; a
          pixel nothing paints counts only where the shot is black), run as
          that script runs it, its diff image saved here;
  class   the replay's measure (vignette_replay.py: palette class, every
          frame pixel counted) on the built window with the shot's actors
          painted in — the number to hold against the replay's. The cloud
          is the 1994 floor itself (shape 874) since phase C.

EVIDENCE (docs/research/2026-10-16-screenshot-reconstruction/phaseB/map13/):
screenNN_built_window.png (vignette_built_window.py's shot | built | diff),
screenNN_class_diff.png (shot | built+actors | misses in red),
screenNN_context.png (3 x 3 windows round the shot painted from the built
map in engine order, the shot's own window outlined).

THE FIT. This projection is orthographic: whether a point is hidden does
not depend on where the camera is, only whether the frame clips it. So
what a shot's frame shows is what every camera shows there, and a cell
the generator lays that would draw into a shot's window must not. --fit
builds the map in memory (build_map_13.build_map_13(fit=trial)), paints
each window with the actors, and lowers by one tier
every generated cell that took FIT_MIN or more of the vignette's matching
pixels, until none does; the result is map13_window_fit.json, which the
builder reads. The climb's cells are never moved (a climb cell that draws
into a window is reported: that is a layout error, not a fit).
"""

import json
import os
import subprocess
import sys
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw

SRC = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(SRC, '..', '..', '..'))
sys.path.insert(0, SRC)

import vignette_replay as VR          # noqa: E402
import shot_decompose as SD           # noqa: E402
from glob_catalog import GlobReader   # noqa: E402
from u8_map import MapArchive         # noqa: E402
from build_map_13 import VIGNETTES    # noqa: E402

SHOTS = VIGNETTES
OUT = os.path.join(REPO, 'docs', 'research',
                   '2026-10-16-screenshot-reconstruction', 'phaseB', 'map13')
FIXED = os.path.join(REPO, 'shared', 'build', 'FIXED.DAT')
FIT_MIN = 4                 # pixels a cell may take before it is lowered
FIT_LEVELS = (232, 224, 176, 168, 144, 120, 112, 104, 80, 72, 64, 56, 40,
              24, 0)

with open(os.path.join(SRC, 'vignettes', 'art_registry.json')) as _fh:
    REGISTRY = json.load(_fh)
PAINTER = VR.make_painter(REGISTRY, built=True)


def load_vig(shot):
    with open(os.path.join(SRC, 'vignettes', f'{shot}.json')) as fh:
        return json.load(fh)


VIGS = {s: load_vig(s) for s in SHOTS}


def camera(shot):
    v = VIGS[shot]
    csx, csy = VR.world_camera(v)
    w, h = VR.shot_size(v)
    return csx, csy, w, h


def as_dicts(items, gr=None):
    gr = gr or GlobReader()
    out = []
    for it in items:
        if it.is_glob_egg:
            out += [dict(shape=g.shape, frame=g.frame, x=g.x, y=g.y, z=g.z)
                    for g in gr.glob_to_items(it.quality, it.x, it.y, it.z)]
        else:
            out.append(dict(shape=it.shape, frame=it.frame, x=it.x, y=it.y,
                            z=it.z))
    return out


def actors(shot):
    v = VIGS[shot]
    ox, oy, oz = v['placement']['origin_world']
    return [dict(shape=a['shape'], frame=a['frame'], x=a['x'] + ox,
                 y=a['y'] + oy, z=a['z'] + oz, actor=True)
            for a in v['actors'] if not a.get('unrendered')]


def paint(items, cam_x, cam_y, w, h, owner=False):
    keep = [d for d in items
            if -320 < d['x'] // 4 - d['y'] // 4 - cam_x < w + 320
            and -320 < d['x'] // 8 + d['y'] // 8 - d['z'] - cam_y < h + 520]
    res = PAINTER.paint(keep, cam_x, cam_y, w, h, owner=owner)
    return (res[0], res[2], keep) if owner else (res[0], keep)


def class_score(img, shot):
    sidx = VR.shot_index(shot)
    drawn = img >= 0
    match = drawn & (VR.CLS[np.where(drawn, img, 0)] == VR.CLS[sidx])
    return 100.0 * match.mean(), match, sidx


def vignette_items(shot):
    """The shot's items as the builder places them (art mapped, dz applied)."""
    import build_map_13 as B
    import lv_map13_tiers as T
    items, _, _ = T.vignette_layer((shot,), 13, B.ART_STANDIN, B.STANDIN_DZ,
                                   B.RAY_SLIDES, B.SHOT_CUTS)
    return [dict(shape=i.shape, frame=i.frame, x=i.x, y=i.y, z=i.z)
            for i in items]


# ── evidence ─────────────────────────────────────────────────────────────

def built_items():
    arch = MapArchive(FIXED)
    return as_dicts(arch.get_map_items(13))


def save_class_diff(shot, img, match, sidx, path):
    pal = VR.PAL
    shot_rgb = pal[sidx].astype(np.uint8)
    drawn = img >= 0
    render = np.zeros(img.shape + (3,), np.uint8)
    render[drawn] = pal[img[drawn]]
    diff = (shot_rgb * 0.35).astype(np.uint8)
    diff[match] = shot_rgb[match]
    diff[drawn & ~match] = (255, 0, 0)
    h, w = img.shape
    Image.fromarray(np.concatenate([shot_rgb, render, diff], 1)) \
        .resize((w * 9, h * 3), Image.NEAREST).save(path)


def save_context(shot, items, path, k=1):
    cam_x, cam_y, w, h = camera(shot)
    cx, cy = cam_x - k * w, cam_y - k * h
    W, H = (2 * k + 1) * w, (2 * k + 1) * h
    img, _ = paint(items + actors(shot), cx, cy, W, H)
    out = np.zeros((H, W, 3), np.uint8)
    drawn = img >= 0
    out[drawn] = VR.PAL[img[drawn]]
    im = Image.fromarray(out)
    ImageDraw.Draw(im).rectangle([k * w - 1, k * h - 1, (k + 1) * w,
                                  (k + 1) * h], outline=(255, 255, 0))
    im.save(path)


def evidence():
    os.makedirs(OUT, exist_ok=True)
    items = built_items()
    rows = []
    for shot in SHOTS:
        png = os.path.join(OUT, f'{shot}_built_window.png')
        res = subprocess.run(
            [sys.executable, os.path.join(SRC, 'vignette_built_window.py'),
             shot, png], capture_output=True, text=True, check=True)
        built = float(res.stdout.split('match ')[1].split('%')[0])
        cam = camera(shot)
        img, _ = paint(items + actors(shot), *cam)
        cls, match, sidx = class_score(img, shot)
        save_class_diff(shot, img, match, sidx,
                        os.path.join(OUT, f'{shot}_class_diff.png'))
        save_context(shot, items, os.path.join(OUT, f'{shot}_context.png'))
        replay = VIGS[shot]['verify']['all_frame_class']
        rows.append((shot, replay, built, cls))
    print(f"{'shot':9s} {'replay':>7s} {'built':>7s} {'class':>7s}  class - replay")
    for shot, replay, built, cls in rows:
        print(f'{shot:9s} {replay:7.2f} {built:7.2f} {cls:7.2f}  {cls - replay:+.2f}')
    return rows


# ── the fit ──────────────────────────────────────────────────────────────

def lower(kind, z):
    if kind in ('cloud', 'water', 'void'):
        return ('void', 0)
    below = [lv for lv in FIT_LEVELS if lv < z]
    return ('rock', below[0]) if below else ('void', 0)


def _rounds(B, T, trial, good, climb, gr, label, max_rounds):
    """Lower every generated cell that takes FIT_MIN or more of a window's
    good pixels, one level a round, until none does. A shot's own (LOCK)
    cell cannot be lowered: each of its completion pieces
    (lv_map13_tiers.shot_faces, named by piece_key) or its cloud filler
    that takes them is marked B.UNFACED and goes without, piece by piece,
    so the courses of a side that draw outside every window stay."""
    for rnd in range(max_rounds):
        field, _, (_, locked, _) = B.build_field(trial)
        keys = {}
        raw = B.build_map_13(trial, keys=keys)
        items = as_dicts(raw, gr)
        vkeys = {(d['shape'], d['x'], d['y'], d['z'])
                 for s in SHOTS for d in vignette_items(s)}
        taken, by_lock = Counter(), Counter()
        for shot in SHOTS:
            cam = camera(shot)
            img, own, keep = paint(items + actors(shot), *cam, owner=True)
            _, match, _ = class_score(img, shot)
            lost = good[shot] & ~match
            for (py, px) in np.argwhere(lost):
                k = own[py, px]
                if k < 0:
                    # Nothing paints it: the cell at z 0 under it was void
                    # (its plate painted the shot's black) and is ground
                    # now, drawn higher up the screen.
                    sx, sy = cam[0] + px, cam[1] + py
                    taken[((2 * sx + 4 * sy) // 128,
                           (4 * sy - 2 * sx) // 128)] += 1
                    continue
                d = keep[k]
                at = (d['shape'], d['x'], d['y'], d['z'])
                if d.get('actor') or at in vkeys:
                    continue
                if at in keys:
                    # A completion piece: a LOCK cell's goes without it, a
                    # HIDDEN cell is lowered like a generated one.
                    c, key = keys[at]
                    if c in locked:
                        by_lock[(c, key)] += 1
                    else:
                        taken[c] += 1
                    continue
                c = (d['x'] // 128, d['y'] // 128)
                taken[c] += 1
                if c in locked and d['shape'] == T.SHAPE_CLOUD:
                    by_lock[(c, T.CLOUD_KEY)] += 1
        bad = [c for c, n in taken.items() if n >= FIT_MIN and c in field
               and c not in locked and field[c].kind != T.VOID]
        stuck = [c for c in bad if c in climb]
        bad = [c for c in bad if c not in climb]
        gone = B.unfaced(trial)
        bare = sorted((c, key) for (c, key), n in by_lock.items()
                      if n >= FIT_MIN and c in locked
                      and key not in gone.get(c, ()))
        print(f'{label} round {rnd}: {sum(taken.values())} pixels taken, '
              f'{len(bad)} cells lowered, {len(bare)} shot pieces unfaced'
              + (f', climb cells drawing in a window: {sorted(stuck)}'
                 if stuck else ''))
        if not bad and not bare:
            return trial
        for c in bad:
            cell = field[c]
            trial[c] = lower(cell.kind, cell.z)
        for c, key in bare:
            trial[c] = (B.UNFACED,
                        sorted(B.unfaced(trial).get(c, frozenset()) | {key}))
    return trial


def fit(max_rounds=30):
    """Two passes. LOWER: every generated cell that draws into a window
    goes down a level (FIT_LEVELS, to z 0) until none does. FILL: every
    cell left void (a shot's hidden cell outside the halo, or one LOWER
    took to the bottom) is raised to its highest standing neighbour's level
    and lowered the same way, so a hole is ground at the highest level no
    window sees, and stays void only where even a floor at z 0 would draw
    into one. A window's good pixels are those its vignette alone matches,
    and the shot's black that the vignette leaves unpainted (where the
    built map's void plates paint black and match)."""
    import build_map_13 as B
    import lv_map13_tiers as T
    gr = GlobReader()
    climb = {(T.cell_of(x), T.cell_of(y)) for (x, y) in B.climb_cells()}
    good = {}
    for shot in SHOTS:
        cam = camera(shot)
        img, _ = paint(vignette_items(shot) + actors(shot), *cam)
        _, alone, sidx = class_score(img, shot)
        good[shot] = alone | ((img < 0) & (VR.CLS[sidx] == VR.CLS[0]))
    trial = _rounds(B, T, {}, good, climb, gr, 'lower', max_rounds)
    field, _, (_, locked, vcells) = B.build_field(trial)
    for c, cell in sorted(field.items()):
        if cell.kind != T.VOID or c in climb:
            continue
        levels = []
        for dx, dy in T.SIDES.values():
            n = field.get((c[0] + dx, c[1] + dy))
            if n is None:
                continue
            if n.kind in (T.ROCK, T.HIDDEN):
                levels.append(n.z)
            elif n.kind == T.LOCK and not vcells[(c[0] + dx, c[1] + dy)][
                    'water'] and n.z:
                levels.append(n.z)
        if levels:
            trial[c] = ('rock', max(levels) // 8 * 8)
        elif any(getattr(field.get((c[0] + dx, c[1] + dy)), 'kind', None)
                 == T.CLOUD for dx, dy in T.SIDES.values()):
            trial[c] = ('cloud', T.CLOUD_Z)
    trial = _rounds(B, T, trial, good, climb, gr, 'fill', max_rounds)
    data = {'note': 'written by lv_map13_views.py --fit: generated cells '
                    'lowered so nothing they draw lands in a 1994 window, '
                    'and void cells filled as high as no window sees',
            'cells': {f'{cx},{cy}': list(v)
                      for (cx, cy), v in sorted(trial.items())}}
    with open(B.FIT_FILE, 'w') as fh:
        json.dump(data, fh, indent=1)
        fh.write('\n')
    print(f'wrote {B.FIT_FILE}: {len(trial)} cells')


if __name__ == '__main__':
    if '--fit' in sys.argv[1:]:
        fit()
    else:
        evidence()

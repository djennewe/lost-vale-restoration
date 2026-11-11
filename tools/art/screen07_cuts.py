#!/usr/bin/env python3
"""
screen07_cuts.py: cut screen07's 1994 rock, floor and flame pixels onto the
pieces of Map 11 that draw them (phase E, 2026-10-30, Douglas's card 3).

After phase D the Pillar of Fire's window (built, with the Avatar) matched
the shot at 91.2%. What was left was not placement: no retail frame, z or
position reproduces it (phaseE/pillars11/REPORT.md has the searches). It is
the 1994 art on retail-shaped pieces:

  * the spears in the cave walls and the seam where the right cliff's two
    courses meet, the back wall's pointed east end;
  * the lava pit round the pillar's foot: its glow and lip on the floor;
  * the pillar's own left flame and the lava by the candle post, which the
    phase-D cut stopped short of.

Method, on the map build_map_11 emits with the retail pieces in place
(`screen07_faces=False`), painted in engine order by the built painter with
865's frames read from the registry PNGs, the vignette's Avatar included:

  1. The pillar (registry 2023). Every missed pixel in its canvas whose shot
     colour is a flame or lava colour and that a floor or step block owns
     goes into the frame, and every pixel the pillar owns and misses takes
     the shot's index (the candle post's outline down x 30). 2023's
     inferred_px is recomputed: the frame pixels the pillar does not show
     as themselves in the shot. pillar_1994_style.py then redraws the other
     three pillars from it.
  2. Repaint. Every 26-family wall (registry 2043, shape 891) and 301 floor
     tile (2027, 892) owning at least MIN_PX missed pixels gets a frame:
     those pixels at the shot's index. Missed pixels the black void tile
     (35 f10) owns, the back wall's tip, go to the nearest wall in screen
     distance. The PNG holds only the shot's pixels; lv_art_props' `patch`
     row lays them over the retail frame at build time, so no Origin pixel
     is committed, and build_map_11.screen07_faces swaps each piece for its
     frame. Same footprint, flags and position: nothing sorts differently.

Shot indices are the nearest U8PAL entry outside the cycling range 1..14
(index 9 and 28 are both (48,48,48)). The mouse pointer at (34..39, 15..20)
and the status text along the bottom are never cut.

Writes the PNGs under shared/data/lv-1994-art/ReconInteriors/ (s07_face_NN,
s07_floor_NN) and rewrites registry 2043 and 2027 and 2023's frame entry.
Deterministic. Run it after a change to Map 11's screen07 window, then
rebuild (tools/build_artifacts.sh).
"""
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(REPO, 'agents', 'map-populator', 'src')
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_map_11 as B11  # noqa: E402
import item_sorter as IS  # noqa: E402
import pillar_1994_style  # noqa: E402
import shot_decompose as SD  # noqa: E402
import vignette_place as V  # noqa: E402
from glob_catalog import GlobReader  # noqa: E402
from vignette_paint import Painter  # noqa: E402
from vignette_replay import frame_dict  # noqa: E402

SHOT = 'screen07'
ART_DIR = 'shared/data/lv-1994-art/ReconInteriors'
REGISTRY = os.path.join(SRC, 'vignettes', 'art_registry.json')
MIN_PX = 8
FACE_SHAPES = {26}
FLOOR_SHAPES = {301}
VOID_TILE = (35, 10)
PILLAR = 865
UI = [(32, 13, 42, 23), (136, 179, 153, 186), (155, 178, 160, 183)]


def shot_indices():
    _, (h, w), rgb = SD.load_shot(SHOT)
    pal = SD.PAL.astype(int)
    d = np.abs(rgb[:, :, None, :] - pal[None, None]).sum(-1)
    d[:, :, 1:15] = 1 << 20
    d[:, :, 255] = 1 << 20
    return d.argmin(-1)


def ui_mask(shape):
    m = np.zeros(shape, bool)
    for x0, y0, x1, y1 in UI:
        m[y0:y1, x0:x1] = True
    return m


def warm_indices():
    import colorsys
    out = set()
    for i in range(15, 255):
        h, s, v = colorsys.rgb_to_hsv(*(SD.PAL[i] / 255.0))
        if s > 0.6 and h <= 0.17 and v > 0.45:
            out.add(i)
    return out


class Window:
    """The shot's window over Map 11 (retail pieces in place), painted."""

    def __init__(self, reg):
        self.vig = V.load(SHOT)
        self.ox, self.oy, self.oz = V.origin(self.vig)
        cam = self.vig['camera']
        self.csx = cam['sx0'] + (self.ox // 4 - self.oy // 4)
        self.csy = cam['sy0'] + (self.ox // 8 + self.oy // 8 - self.oz)
        _, (self.H, self.W), _ = SD.load_shot(SHOT)
        self.painter = Painter.built()
        self.items = self._items(B11.build_map_11(screen07_faces=False))
        self.reload_pillars(reg)

    def reload_pillars(self, reg):
        frames = [frame_dict(reg['shapes'][str(r)]['frames'][0])
                  for r in (2024, 2025, 2023, 2026)]
        self.painter.extra[PILLAR] = (frames, self.painter.info(PILLAR))

    def _items(self, items):
        cx = 2 * (self.csx + self.W // 2) + 4 * (self.csy + self.H // 2)
        cy = 4 * (self.csy + self.H // 2) - 2 * (self.csx + self.W // 2)
        gr = GlobReader()
        out = []
        for it in items:
            if abs(it.x - cx) > 4000 or abs(it.y - cy) > 4000:
                continue
            if it.is_glob_egg:
                out += [dict(shape=g.shape, frame=g.frame, x=g.x, y=g.y, z=g.z)
                        for g in gr.glob_to_items(it.quality, it.x, it.y, it.z)]
            else:
                out.append(dict(shape=it.shape, frame=it.frame, x=it.x,
                                y=it.y, z=it.z, flags=it.flags))
        for a in self.vig['actors']:
            if not a.get('unrendered'):
                out.append(dict(shape=a['shape'], frame=a['frame'],
                                x=a['x'] + self.ox, y=a['y'] + self.oy,
                                z=a['z'] + self.oz, flags=a.get('flags', 0)))
        return out

    def paint(self):
        img, seq, own = self.painter.paint(self.items, self.csx, self.csy,
                                           self.W, self.H, owner=True)
        sprite = {self.painter._kmap[id(s)]: s for s in seq}
        return img, own, sprite


def misses(img, want):
    m = img >= 0
    return ~(m & (SD.CLS[np.where(m, img, 0)] == SD.CLS[want]))


def save_png(a, rel):
    o = Image.fromarray(a.astype(np.uint8), 'P')
    o.putpalette([int(c) for rgb in SD.PAL for c in rgb])
    o.save(os.path.join(REPO, rel), transparency=255)


def cut_pillar(win, reg, want, ui):
    img, own, sprite = win.paint()
    x, y, z = B11.SCREEN07_PILLAR[1:]
    pid = next(k for k, it in enumerate(win.items)
               if (it['shape'], it['frame'], it['x'], it['y'], it['z']) ==
               (PILLAR, 2, x, y, z))
    s = sprite[pid]
    left, top = s.sr[0], s.sr[1]
    fr = reg['shapes']['2023']['frames'][0]
    path = os.path.join(REPO, fr['png'])
    a = np.array(Image.open(path))
    h, w = a.shape
    miss = misses(img, want) & ~ui
    shapes = np.array([it['shape'] for it in win.items] + [-1])[own]
    warm = np.isin(want, sorted(warm_indices()))
    canvas = np.zeros_like(miss)
    canvas[max(top, 0):top + h, max(left, 0):left + w] = True
    add = canvas & miss & warm & np.isin(shapes, [301, 99, 100, 488])
    fix = canvas & miss & (own == pid)
    ys, xs = np.nonzero(add | fix)
    a[ys - top, xs - left] = want[ys, xs]
    save_png(a, fr['png'])
    # repaint: which frame pixels does the pillar show as themselves?
    win.reload_pillars(reg)
    img, own, sprite = win.paint()
    shown = (own == pid) & ~misses(img, want)
    inferred = [[int(fx), int(fy)] for fy, fx in zip(*np.nonzero(a != 255))
                if not (0 <= top + fy < win.H and 0 <= left + fx < win.W
                        and shown[top + fy, left + fx])]
    fr.update(width=w, height=h, opaque_px=int((a != 255).sum()),
              inferred_px=inferred)
    fr['source']['match'] = int(shown.sum())
    print(f'2023: +{int(add.sum())} flame/lava px, {int(fix.sum())} px '
          f're-cut, {len(inferred)} inferred')
    return int(add.sum()), int(fix.sum())


def cut_pieces(win, want, ui):
    img, own, sprite = win.paint()
    miss = misses(img, want) & ~ui
    items = win.items
    key = lambda k: (items[k]['shape'], items[k]['frame'])   # noqa: E731
    faces = {k for k in sprite if items[k]['shape'] in FACE_SHAPES}
    floors = {k for k in sprite if items[k]['shape'] in FLOOR_SHAPES}
    take = {k: (own == k) & miss for k in faces | floors}
    # the void tile's missed pixels: the nearest wall's
    void = np.isin(own, [k for k in sprite if key(k) == VOID_TILE]) & miss
    shown = [k for k in faces if items[k]['shape'] == 26 and (own == k).any()]
    for y, x in zip(*np.nonzero(void)):
        def dist(k):
            l, t, r, b = sprite[k].sr
            return max(l - x, 0, x - r + 1) + max(t - y, 0, y - b + 1)
        k = min(shown, key=lambda k: (dist(k), k))
        if dist(k) <= 16:
            take[k][y, x] = True
    out = {2043: [], 2027: []}
    for k in sorted(take, key=lambda k: (items[k]['y'], items[k]['x'],
                                         items[k]['z'])):
        sel = take[k]
        if sel.sum() < MIN_PX:
            continue
        it, s = items[k], sprite[k]
        assert not s.flipped, it
        ys, xs = np.nonzero(sel)
        l, t = int(xs.min()), int(ys.min())
        a = np.full((int(ys.max()) - t + 1, int(xs.max()) - l + 1), 255)
        a[ys - t, xs - l] = want[ys, xs]
        base = win.painter.frame(it['shape'], it['frame'])
        sx_bot, sy_bot = s.sr[0] + base['xoff'], s.sr[1] + base['yoff']
        rid = 2043 if k in faces else 2027
        n = len(out[rid])
        rel = f"{ART_DIR}/s07_{'face' if rid == 2043 else 'floor'}_{n:02d}.png"
        save_png(a, rel)
        out[rid].append({
            'png': rel, 'hotspot': [sx_bot - l, sy_bot - t],
            'width': int(a.shape[1]), 'height': int(a.shape[0]),
            'opaque_px': int(sel.sum()),
            'base': [it['shape'], it['frame']],
            'at': [it['x'] - win.ox, it['y'] - win.oy, it['z'] - win.oz],
            'source': {'shot': SHOT, 'xy': [l, t], 'match': int(sel.sum())},
            'grade': 'single-shot',
            'note': 'patch: the pixels the shot shows this piece owning, '
                    'over its retail frame (lv_art_props builds the frame)'})
    return out


def main():
    with open(REGISTRY) as f:
        reg = json.load(f)
    want = shot_indices()
    win = Window(reg)
    ui = ui_mask(want.shape)
    cut_pillar(win, reg, want, ui)
    with open(REGISTRY, 'w') as f:
        f.write(json.dumps(reg, indent=1) + '\n')
    pillar_1994_style.main()
    with open(REGISTRY) as f:
        reg = json.load(f)
    win.reload_pillars(reg)
    for old in glob.glob(os.path.join(REPO, ART_DIR, 's07_face_*.png')) + \
            glob.glob(os.path.join(REPO, ART_DIR, 's07_floor_*.png')):
        os.remove(old)
    cuts = cut_pieces(win, want, ui)
    names = {2043: ("screen07's cave walls (26 family) with the 1994 spears, "
                    "the right cliff's course seam and the back wall's tip: "
                    "one patch per piece (shape 891)", [128, 32, 48]),
             2027: ("screen07's floor round the Pillar of Fire: the lava "
                    "pit's glow and lip, one patch per tile (shape 892)",
                    [128, 128, 0])}
    for rid, frames in cuts.items():
        reg['shapes'][str(rid)] = {
            'name': names[rid][0], 'kind': 'sprite-patch',
            'footprint': names[rid][1], 'flags': {}, 'replaces': None,
            'frames': frames}
        print(f'{rid}: {len(frames)} frames, '
              f'{sum(f["opaque_px"] for f in frames)} px')
    with open(REGISTRY, 'w') as f:
        f.write(json.dumps(reg, indent=1) + '\n')


if __name__ == '__main__':
    main()

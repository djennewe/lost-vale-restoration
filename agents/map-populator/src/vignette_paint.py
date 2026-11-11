"""vignette_paint.py - paint a vignette item list with the engine's sort.

Uses agents/map-populator/src/item_sorter.py (a verbatim port of ScummVM's
SortItem::below / overlap / occludes, ItemSorter::AddItem and PaintSortItem)
to get the paint order, then composites the frames in that order.  Retail
shapes come from the pristine retail U8SHAPES.FLX.bak / TYPEFLAG.DAT.bak by
default; pass typeflag=/shapes= (or Painter.built()) to paint the built
artifacts in shared/build/ instead.  1994-only drafts are registered as extra
shapes (id >= 2000) with their own frames (dict: pixels/width/height/xoff/yoff)
and footprint.

    from vignette_paint import Painter
    p = Painter()                      # retail .bak files
    p = Painter.built()                # shared/build/TYPEFLAG.DAT + U8SHAPES.FLX
    p.add_shape(2001, frames, xd=32, yd=32, zd=40, solid=True, land=False)
    img_idx, order = p.paint(items, cam_sx, cam_sy, W, H)

items: list of dicts {shape, frame, x, y, z}.  Screen position of an item's
hotspot = (x/4 - y/4 - cam_sx, x/8 + y/8 - z - cam_sy)  (C division per
term, as the engine).  Returns an HxW array of palette indices (-1 = never
painted) and the painted order.
"""
import os
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'agents/map-populator/src'))
import item_sorter as IS  # noqa: E402

STATIC = os.path.join(REPO, 'shared/data/u8-install/STATIC')
BUILD = os.path.join(REPO, 'shared/build')


def retail_file(name):
    """The retail copy of STATIC/<name>: the .bak an in-place install keeps,
    or the file itself on an install that was never patched in place."""
    bak = os.path.join(STATIC, name + '.bak')
    return bak if os.path.exists(bak) else os.path.join(STATIC, name)


RETAIL_TYPEFLAG = retail_file('TYPEFLAG.DAT')
RETAIL_SHAPES = retail_file('U8SHAPES.FLX')


class Painter(IS.ItemSorter):
    def __init__(self, typeflag=RETAIL_TYPEFLAG, shapes=RETAIL_SHAPES):
        super().__init__(typeflag=typeflag, shapes=shapes)
        self.extra = {}

    @classmethod
    def built(cls, build_dir=BUILD):
        """A Painter over the built artifacts (tools/build_artifacts.sh)."""
        return cls(typeflag=os.path.join(build_dir, 'TYPEFLAG.DAT'),
                   shapes=os.path.join(build_dir, 'U8SHAPES.FLX'))

    def add_shape(self, sid, frames, xd, yd, zd, solid=True, land=False):
        self.extra[sid] = (frames, dict(fixed=1, solid=solid, land=land,
                                        occl=False, draw=False, roof=False,
                                        trans=False, editor=False, xd=xd,
                                        yd=yd, zd=zd, anim=False))

    def info(self, shape):
        if shape in self.extra:
            return self.extra[shape][1]
        return super().info(shape)

    def frame(self, shape, frame):
        if shape in self.extra:
            fr = self.extra[shape][0]
            return fr[frame] if frame < len(fr) else None
        return super().frame(shape, frame)

    def order(self, items, cam_sx, cam_sy, clip):
        objs = [IS._Item(it['shape'], it['frame'], it['x'], it['y'], it['z'],
                         it.get('flags', 0)) for it in items]
        idx = sorted(range(len(objs)), key=lambda k: (objs[k].y // IS.CHUNK,
                                                      objs[k].x // IS.CHUNK, k))
        lst = []
        self._kmap = {}
        for k in idx:
            it = objs[k]
            if self.info(it.shape)['editor']:
                continue
            s = self._make(it, cam_sx, cam_sy)
            if s is None or not IS._intersects(clip, s.sr):
                continue
            s.order = -1
            self._kmap[id(s)] = k
            addpoint = None
            for s2 in lst:
                if addpoint is None and IS.list_less(s, s2):
                    addpoint = s2
                if s2.occluded:
                    continue
                if IS.overlap(s, s2):
                    if IS.below(s, s2):
                        if s2.occl and IS.occludes(s2, s):
                            s.occluded = True
                            break
                        IS._insert_sorted(s2.depends, s)
                    elif s.occl and IS.occludes(s, s2):
                        s2.occluded = True
                    else:
                        IS._insert_sorted(s.depends, s2)
            if addpoint is None:
                lst.append(s)
            else:
                lst.insert(lst.index(addpoint), s)
        out = []

        def paint(si):
            if si.occluded:
                return
            si.order = -2
            for d in si.depends:
                if d.order == -1:
                    paint(d)
            si.order = len(out)
            out.append(si)
        sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
        for s in lst:
            if s.order == -1:
                paint(s)
        return out

    def paint(self, items, cam_sx, cam_sy, W, H, owner=False):
        clip = (0, 0, W, H)
        seq = self.order(items, cam_sx, cam_sy, clip)
        img = np.full((H, W), -1, int)
        own = np.full((H, W), -1, int)
        for si in seq:
            fr = self.frame(si.shape, si.frame)
            a = np.asarray(fr['pixels'], dtype=np.int64).reshape(fr['height'], fr['width'])
            if si.flipped:
                a = a[:, ::-1]
            l, t = si.sr[0], si.sr[1]
            h, w = a.shape
            y0, y1 = max(t, 0), min(t + h, H)
            x0, x1 = max(l, 0), min(l + w, W)
            if y1 <= y0 or x1 <= x0:
                continue
            sub = a[y0 - t:y1 - t, x0 - l:x1 - l]
            m = sub != 255
            img[y0:y1, x0:x1][m] = sub[m]
            own[y0:y1, x0:x1][m] = self._kmap[id(si)]
        return (img, seq, own) if owner else (img, seq)

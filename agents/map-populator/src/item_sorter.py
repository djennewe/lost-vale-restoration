#!/usr/bin/env python3
"""item_sorter.py — ScummVM's Ultima 8 paint sorter, ported to find
`Cycle in paint dependency graph` before a playtest does.

The engine draws a frame by building a dependency graph over every visible
item (ItemSorter::AddItem: for each pair whose screen footprints overlap,
SortItem::below decides which is drawn first) and then painting it
depth-first (ItemSorter::PaintSortItem). `below` is a pairwise heuristic,
not an order: boxes that pierce one another can make it intransitive, and
the walk then meets an item already on its own stack and logs

    Cycle in paint dependency graph <a> -> <b> -> ... -> <a>

once per frame (item_sorter.cpp:414, shape numbers, not object ids). In
ScummVM that has run to 110,000 lines a session (Map 10's north-east
village, a workbench through a hut wall) and 3,500 (Map 8's backstop Lord
British on Mythran's dining table). This module reproduces it offline.

Ported verbatim from scummvm-lv-console/engines/ultima/ultima8/world/:
SortItem::setBoxBounds, ::below, ::overlap, ::occludes, ::listLessThan
(sort_item.cpp/.h), ItemSorter::AddItem's screen rect from the shape frame
(mirrored, and the footpad swapped, for FLG_FLIPPED) and its pair loop,
DependsList::insert_sorted, and PaintSortItem's cycle check. The
SORTITEM_OCCLUSION_EXPERIMENTAL block is compiled out in the engine, so it
is not ported.

What it does NOT model, so a zero here is evidence and not proof:
  * the engine's item order is chunk list order as the map was loaded and
    as items moved since; this uses (chunk row, chunk column, list order);
  * for cycles(), GameMapGump's roof cut (items at z >= the roof over the
    Avatar are not drawn) is the caller's job: pass only the items the
    camera would draw; overdrawn() makes the cut itself;
  * lerped (moving) positions, the dragging item, highlight passes.

    from item_sorter import ItemSorter
    cycles = ItemSorter().cycles(items, camera=(x, y, z))
    share, culprits = ItemSorter().overdrawn(items, shape, frame, x, y, z)

overdrawn() (2026-10-09) answers "can the player see and click an NPC
standing here": Tyorvi's first Gunnar stash point drew him inside the
south-east cliff (docs/playtest-2026-10-09-schedules.md finding 2), and
test_schedule_destinations.py now runs it on every schedule point.
"""

import os
import struct
import sys
from collections import namedtuple

import numpy as np

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from shape_viewer import (read_flx_entry, parse_shape_frames,  # noqa: E402
                          _parse_one_frame)

TYPEFLAG = os.path.join(REPO, 'shared', 'build', 'TYPEFLAG.DAT')
SHAPES = os.path.join(REPO, 'shared', 'build', 'U8SHAPES.FLX')

# The harness's 640x400 game view, centred on the camera
# (GameMapGump::PaintThis passes the surface's clip rect).
CLIP_640x400 = (-320, -200, 320, 200)

CHUNK = 512          # U8 map chunk size (CurrentMap)

FLG_INVISIBLE = 0x0010   # Item flags (item.h)
FLG_FLIPPED = 0x0020

# No U8SHAPES.FLX frame (retail or ours) reaches more than 210 pixels from
# its hotspot (measured 2026-10-09: 210 across, 176 down), so two sprites
# whose hotspots are farther apart than this cannot share a pixel.
REACH = 320

# The fields _make reads, for an item that is not a map record.
_Item = namedtuple('_Item', 'shape frame x y z flags', defaults=(0,))


def _div(a, b):
    """C integer division (truncates toward zero)."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q


class _SI:
    """One SortItem."""
    __slots__ = ('shape', 'frame', 'flipped', 'x', 'y', 'z', 'x_left',
                 'y_far', 'z_top', 'sx_left', 'sx_right', 'sx_top', 'sy_top',
                 'sx_bot', 'sy_bot', 'fbigsq', 'flat', 'sr', 'draw', 'solid',
                 'occl', 'roof', 'anim', 'trans', 'land', 'occluded',
                 'order', 'depends')


def _intersects(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _contains(a, b):
    return a[0] <= b[0] and b[2] <= a[2] and a[1] <= b[1] and b[3] <= a[3]


def overlap(a, b):
    """SortItem::overlap (sort_item.h)."""
    if not _intersects(a.sr, b.sr):
        return False
    ptd = (a.sx_top - b.sx_bot, a.sy_top - b.sy_bot)
    pbd = (a.sx_bot - b.sx_top, a.sy_bot - b.sy_top)
    return not (a.sx_right <= b.sx_left or a.sx_left >= b.sx_right or
                -pbd[0] - pbd[1] * 2 >= 0 or pbd[0] - pbd[1] * 2 >= 0 or
                -ptd[0] + ptd[1] * 2 >= 0 or ptd[0] + ptd[1] * 2 >= 0)


def occludes(a, b):
    """SortItem::occludes (sort_item.h)."""
    if not _contains(a.sr, b.sr):
        return False
    ptd = (a.sx_top - b.sx_top, a.sy_top - b.sy_top)
    pbd = (a.sx_bot - b.sx_bot, a.sy_bot - b.sy_bot)
    return (a.sx_right >= b.sx_right and a.sx_left <= b.sx_left and
            -pbd[0] - pbd[1] * 2 <= 0 and pbd[0] - pbd[1] * 2 <= 0 and
            -ptd[0] + ptd[1] * 2 <= 0 and ptd[0] + ptd[1] * 2 <= 0)


def list_less(a, b):
    """SortItem::listLessThan (U8: no sprites)."""
    if a.z != b.z:
        return a.z < b.z
    return a.flat > b.flat


def below(s1, s2):
    """SortItem::below (sort_item.cpp), U8 branches (no sprite/invitem)."""
    d = lambda v: _div(v, 32)                                   # noqa: E731
    if s1.flat and s2.flat:
        if s1.z != s2.z:
            return s1.z < s2.z
    else:
        if s1.z_top <= s2.z:
            return True
        if s1.z >= s2.z_top:
            return False
    yf1, yf2 = s1.y_far == s1.y, s2.y_far == s2.y
    if yf1 and yf2:
        if d(s1.y) != d(s2.y):
            return s1.y < s2.y
    else:
        if s1.y <= s2.y_far:
            return True
        if s1.y_far >= s2.y:
            return False
    xf1, xf2 = s1.x_left == s1.x, s2.x_left == s2.x
    if xf1 and xf2:
        if d(s1.x) != d(s2.x):
            return s1.x < s2.x
    else:
        if s1.x <= s2.x_left:
            return True
        if s1.x_left >= s2.x:
            return False
    if s1.z_top - 8 <= s2.z and s1.z < s2.z_top - 8:
        return True
    if s1.z >= s2.z_top - 8 and s1.z_top - 8 > s2.z:
        return False
    if yf1 != yf2:
        if d(s1.y) <= d(s2.y_far):
            return True
        if d(s1.y_far) >= d(s2.y):
            return False
        c1 = _div(d(s1.y_far) + d(s1.y), 2)
        c2 = _div(d(s2.y_far) + d(s2.y), 2)
        if c1 != c2:
            return c1 < c2
    if xf1 != xf2:
        if d(s1.x) <= d(s2.x_left):
            return True
        if d(s1.x_left) >= d(s2.x):
            return False
        c1 = _div(d(s1.x_left) + d(s1.x), 2)
        c2 = _div(d(s2.x_left) + d(s2.x), 2)
        if c1 != c2:
            return c1 < c2
    if s1.flat or s2.flat:
        if s1.z != s2.z:
            return s1.z < s2.z
        for a, b, first in ((s1.flat, s2.flat, True),
                            (s1.trans, s2.trans, False),
                            (s1.anim, s2.anim, False),
                            (s1.draw, s2.draw, True),
                            (s1.solid, s2.solid, True),
                            (s1.occl, s2.occl, True),
                            (s1.fbigsq, s2.fbigsq, True)):
            if a != b:
                return a > b if first else a < b
    if s1.x == s2.x and s1.y == s2.y and s1.trans != s2.trans:
        return s1.trans < s2.trans
    if s1.land and s2.land and s1.roof != s2.roof:
        return s1.roof < s2.roof
    if s1.roof != s2.roof:
        return s1.roof > s2.roof
    if s1.z != s2.z:
        return s1.z < s2.z
    if xf1 or xf2 or yf1 or yf2:
        if s1.sx_left != s2.sx_left:
            return s1.sx_left > s2.sx_left
        if s1.sy_bot != s2.sy_bot:
            return s1.sy_bot < s2.sy_bot
    if s1.x + s1.y != s2.x + s2.y:
        return s1.x + s1.y < s2.x + s2.y
    if s1.x_left + s1.y_far != s2.x_left + s2.y_far:
        return s1.x_left + s1.y_far < s2.x_left + s2.y_far
    if s1.y != s2.y:
        return s1.y < s2.y
    if s1.x != s2.x:
        return s1.x < s2.x
    if s1.shape != s2.shape:
        return s1.shape < s2.shape
    return s1.frame < s2.frame


class ItemSorter:
    def __init__(self, typeflag=TYPEFLAG, shapes=SHAPES):
        with open(typeflag, 'rb') as fh:
            self._tf = fh.read()
        with open(shapes, 'rb') as fh:
            self._flx = fh.read()
        self._frames = {}
        self._masks = {}

    def info(self, shape):
        """(flags, footpad x, y, z in world units, animated) per
        TypeFlags::loadTypeFlags' U8 byte layout."""
        b = self._tf[shape * 8:shape * 8 + 8]
        return dict(fixed=b[0] & 1, solid=bool(b[0] & 2), land=bool(b[0] & 8),
                    occl=bool(b[0] & 0x10), draw=bool(b[1] & 1),
                    roof=bool(b[1] & 4), trans=bool(b[1] & 8),
                    editor=bool(b[5] & 0x10),
                    xd=(b[2] >> 4) * 32, yd=(b[3] & 0xF) * 32,
                    zd=(b[3] >> 4) * 8, anim=(b[4] & 0xF) != 0)

    def frame(self, shape, frame):
        if shape not in self._frames:
            data = read_flx_entry(self._flx, shape)
            frames = parse_shape_frames(data) if data else []
            if not frames and data and len(data) >= 6:
                # parse_shape_frames refuses more than 500 frames, and the
                # Avatar (shape 1, 1,550 frames), 137, 191 and 315 have
                # more: _make then dropped them, so a graph with the Avatar
                # in it silently had no Avatar (2026-10-10 paint-cycles
                # report, section 4). Read those one frame at a time.
                frames = _FrameTable(data)
            self._frames[shape] = frames
        frames = self._frames[shape]
        return frames[frame] if frame < len(frames) else None

    def _make(self, it, cam_sx, cam_sy):
        fr = self.frame(it.shape, it.frame)
        if fr is None:
            return None                    # "Skipping invalid shape in sorter"
        inf = self.info(it.shape)
        flipped = bool(it.flags & FLG_FLIPPED)
        xd, yd = (inf['yd'], inf['xd']) if flipped else (inf['xd'], inf['yd'])
        s = _SI()
        s.shape, s.frame, s.flipped = it.shape, it.frame, flipped
        s.x, s.y, s.z = it.x, it.y, it.z
        s.x_left, s.y_far = it.x - xd, it.y - yd
        s.z_top = it.z + inf['zd']
        s.sx_left = _div(s.x_left, 4) - _div(s.y, 4) - cam_sx
        s.sx_right = _div(s.x, 4) - _div(s.y_far, 4) - cam_sx
        s.sx_top = _div(s.x_left, 4) - _div(s.y_far, 4) - cam_sx
        s.sy_top = _div(s.x_left, 8) + _div(s.y_far, 8) - s.z_top - cam_sy
        s.sx_bot = _div(s.x, 4) - _div(s.y, 4) - cam_sx
        s.sy_bot = _div(s.x, 8) + _div(s.y, 8) - s.z - cam_sy
        s.fbigsq = xd == yd and xd >= 128
        s.flat = inf['zd'] == 0
        if flipped:
            left = s.sx_bot + fr['xoff'] - fr['width']
        else:
            left = s.sx_bot - fr['xoff']
        top = s.sy_bot - fr['yoff']
        s.sr = (left, top, left + fr['width'], top + fr['height'])
        s.draw, s.solid, s.roof = inf['draw'], inf['solid'], inf['roof']
        s.trans, s.land, s.anim = inf['trans'], inf['land'], inf['anim']
        s.occl = inf['occl'] and not inf['trans']
        s.occluded, s.order, s.depends = False, -1, []
        return s

    def mask(self, si):
        """The SortItem's sprite as a boolean array over si.sr: True where
        the frame paints (palette index 0xFF is transparent), mirrored for
        FLG_FLIPPED as Render::paint mirrors it."""
        key = (si.shape, si.frame, si.flipped)
        m = self._masks.get(key)
        if m is None:
            fr = self.frame(si.shape, si.frame)
            m = np.frombuffer(bytes(fr['pixels']), dtype=np.uint8).reshape(
                fr['height'], fr['width']) != 0xFF
            if si.flipped:
                m = m[:, ::-1]
            self._masks[key] = m
        return m

    def roof_z(self, items, x, y, z):
        """z of the roof GameMapGump cuts at with the camera on a subject
        standing at (x, y, z), else None. CameraProcess::findRoof boxes the
        camera point (the subject's z + 20) as 64x64x16, and
        getPositionInfo takes the lowest SI_ROOF item that overlaps it in
        XY (strictly) with its bottom at or above that box's top."""
        cz, best = z + 20 + 16, None
        for it in items:
            inf = self.info(it.shape)
            if not inf['roof'] or it.z < cz:
                continue
            xd, yd = ((inf['yd'], inf['xd']) if it.flags & FLG_FLIPPED
                      else (inf['xd'], inf['yd']))
            if it.x - xd < x and x - 64 < it.x and \
               it.y - yd < y and y - 64 < it.y and (best is None
                                                    or it.z < best):
                best = it.z
        return best

    def overdrawn(self, items, shape, frame, x, y, z):
        """How much of an actor's sprite the map paints over.

        The actor is (shape, frame) standing at (x, y, z); `items` are the
        map items around it, globs expanded, the actor itself left out.
        Returns (fraction, culprits): the share of the actor's opaque pixels
        that some item drawn AFTER it covers, and (shape, frame, x, y, z,
        pixels) for each such item. A covered pixel is one the player
        cannot see the actor in and cannot click it at (ItemSorter::Trace
        hits the front-most opaque pixel).

        "Drawn after" is the engine's dependency edge: an item whose screen
        footprint overlap()s the actor's and that the actor is below(). As
        in GameMapGump, items at or above the roof over the subject are not
        drawn (unless SI_DRAW), nor are SI_EDITOR shapes or FLG_INVISIBLE
        items. An SI_OCCL item that occludes() the actor culls it whole.
        Not modelled: paint order between items with no direct edge (the
        order then comes from list position and other items' edges)."""
        npc = self._make(_Item(shape, frame, x, y, z), 0, 0)
        nm = self.mask(npc)
        zlimit = self.roof_z(items, x, y, z)
        cover = np.zeros_like(nm)
        culprits = []
        for it in items:
            if it.flags & FLG_INVISIBLE or \
               abs(_div(it.x, 4) - _div(it.y, 4) - npc.sx_bot) > REACH or \
               abs(_div(it.x, 8) + _div(it.y, 8) - it.z - npc.sy_bot) > REACH:
                continue
            inf = self.info(it.shape)
            if inf['editor'] or (zlimit is not None and it.z >= zlimit
                                 and not inf['draw']):
                continue
            s = self._make(it, 0, 0)
            if s is None or not overlap(npc, s) or not below(npc, s):
                continue
            if s.occl and occludes(s, npc):
                cover[:] = True
                culprits.append((it.shape, it.frame, it.x, it.y, it.z,
                                 int(nm.sum())))
                continue
            l0, t0 = max(npc.sr[0], s.sr[0]), max(npc.sr[1], s.sr[1])
            l1, t1 = min(npc.sr[2], s.sr[2]), min(npc.sr[3], s.sr[3])
            hit = (self.mask(s)[t0 - s.sr[1]:t1 - s.sr[1],
                                l0 - s.sr[0]:l1 - s.sr[0]] &
                   nm[t0 - npc.sr[1]:t1 - npc.sr[1],
                      l0 - npc.sr[0]:l1 - npc.sr[0]])
            if hit.any():
                cover[t0 - npc.sr[1]:t1 - npc.sr[1],
                      l0 - npc.sr[0]:l1 - npc.sr[0]] |= hit
                culprits.append((it.shape, it.frame, it.x, it.y, it.z,
                                 int(hit.sum())))
        return float(cover[nm].mean()) if nm.any() else 0.0, culprits

    def cycles(self, items, camera, clip=CLIP_640x400):
        """Every cycle the engine would log painting one frame of `items`
        with the camera at `camera`. Each cycle is the list of
        (shape, frame, x, y, z) from the item met again to the item that
        met it. Editor-only shapes (eggs) are dropped, as GameMapGump
        drops them unless editor items are shown."""
        cx, cy, cz = camera
        cam_sx = _div(cx - cy, 4)
        cam_sy = _div(cx + cy, 8) - cz
        order = sorted(range(len(items)),
                       key=lambda k: (items[k].y // CHUNK,
                                      items[k].x // CHUNK, k))
        lst = []
        for k in order:
            it = items[k]
            if self.info(it.shape)['editor']:
                continue
            s = self._make(it, cam_sx, cam_sy)
            if s is None or not _intersects(clip, s.sr):
                continue
            addpoint = None
            for s2 in lst:
                if addpoint is None and list_less(s, s2):
                    addpoint = s2
                if s2.occluded:
                    continue
                if overlap(s, s2):
                    if below(s, s2):
                        if s2.occl and occludes(s2, s):
                            s.occluded = True
                            break
                        _insert_sorted(s2.depends, s)
                    elif s.occl and occludes(s, s2):
                        s2.occluded = True
                    else:
                        _insert_sorted(s.depends, s2)
            if addpoint is None:
                lst.append(s)
            else:
                lst.insert(lst.index(addpoint), s)

        found, stack, painted = [], [], [None]

        def paint(si):
            if si.occluded:
                return
            si.order = -2
            stack.append(si)
            for d in si.depends:
                if d.order == -2:
                    found.append([(t.shape, t.frame, t.x, t.y, t.z)
                                  for t in stack[stack.index(d):]])
                    break
                if d.order == -1:
                    paint(d)
            stack.pop()
            si.order = painted[0].order + 1 if painted[0] else 0
            painted[0] = si

        limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(limit, 20000))
        try:
            for s in lst:
                if s.order == -1:
                    paint(s)
        finally:
            sys.setrecursionlimit(limit)
        return found


def _insert_sorted(dep, other):
    """DependsList::insert_sorted: before the first listLessThan-greater."""
    for i, n in enumerate(dep):
        if list_less(other, n):
            dep.insert(i, other)
            return
    dep.append(other)


class _FrameTable:
    """A shape's frames parsed on demand from its U8 frame index (the
    layout parse_shape_frames reads: a frame count at byte 4, then 6 bytes
    a frame, a 24-bit offset and a 16-bit size)."""

    def __init__(self, data):
        self._data = data
        self._n = struct.unpack_from('<H', data, 4)[0]
        self._cache = {}

    def __len__(self):
        return self._n

    def __getitem__(self, k):
        if k not in self._cache:
            off = 6 + k * 6
            fr = None
            if off + 6 <= len(self._data):
                fo = struct.unpack_from('<I', self._data, off)[0] & 0xFFFFFF
                fs = struct.unpack_from('<H', self._data, off + 4)[0]
                if fo + 18 <= len(self._data):
                    fr = _parse_one_frame(self._data, fo, fs)
            self._cache[k] = fr
        return self._cache[k]

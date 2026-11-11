#!/usr/bin/env python3
"""
lv_cave_vignette.py — a 1994 cave screenshot stamped into an LV map and
closed into the cave around it (phase B, 2026-10-17; maps 9 and 11).

`vignette_place.stamp` puts a reconstructed shot into a map verbatim. In a
cave that leaves three problems this module solves:

1. THE SHOT IS 2-D. The reconstruction solved each piece for the pixels,
   so walls stand as fragments, caps float at z=48 over floor, and the
   floor runs on under the rock. U8's projection never rotates, so the
   picture is the same from every camera — but a body can walk where the
   picture shows rock. `classify` paints the vignette in engine order and
   reads, for every 32-unit cell whose floor point lies in the window,
   what the shot shows there: floor (F), a low prop (P), rock — a wall or
   anything solved at z >= 48 — (R), or black (V). `fences` then stands
   retail's invisible wall (497/498/846/501, two 48-unit courses, 96: out
   of a 72-unit climb's reach) on every blocked cell beside a walkable
   one. The window is unchanged: those shapes are SI_EDITOR and never
   drawn.
2. THE SHOT ENDS AT ITS FRAME. Outside the window the builder declares
   which 128-unit cells are floor and which are rock (`Cave.rock`), and
   `shell` closes the rock: a face the camera sees (rock north or west of
   floor) gets two courses of the 26-32 cave-wall family in short runs
   with a 0/32 jag and a 29 post on each convex corner, textured frames
   only; a face it does not see (rock south or east of floor) gets the
   invisible wall, so the floor ends at black as the shots' own lips do
   (screen05's bottom-left, screen10's dais foot). Rock has no floor: the
   map's void plates (lv_furnish.void_floor) paint its top black, which is
   what every cave shot shows above its walls.
3. NOTHING ELSE MAY PAINT INTO THE WINDOW. Every generated item whose
   sprite reaches the window is dropped (a wall becomes invisible wall).

Everything is deterministic: frames, run lengths and jags come from a hash
of the coordinates and a salt.

Also here, because the three shots need them:
  * `relift`: an item at (x, y, z) draws exactly where (x+4h, y+4h, z+h)
    does (h even; C division per term), so a piece the reconstruction
    solved on the floor can be stood on the structure the shot shows it
    on (screen10's dais top) without moving a pixel;
  * `window_score` / `context_png`: vignette_built_window's all-frame
    score on an in-memory item list, and a 3x3-window context render in
    the engine's draw order, built artifacts.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import vignette_place as V                       # noqa: E402
from u8_map import MapItem                       # noqa: E402

CELL = 128
FINE = 32
COURSE = 48
ROCK_FLOOR = 301                                 # retail cave rock, glob 397
ROCK_FLOOR_FRAMES = tuple(range(7))
GLOB_ROCK_FLOOR = 397

# The 26-32 cave-wall family, textured frames only (frame sheet rendered
# 2026-10-17: 26/32 f7-8, 27/28/30/31 f2-3, 31 f5 and 29 f6/f18 are black,
# 26 f13 red). Long in x: 26 (128), 27 (96), 28 (64); long in y: 32, 31,
# 30; 29 is the 32x32 post.
WALL_X = {128: 26, 96: 27, 64: 28}
WALL_Y = {128: 32, 96: 31, 64: 30}
POST = 29
TEXTURED = {26: (0, 1, 2, 3, 4, 5, 6), 32: (0, 1, 2, 3, 4, 5, 6),
            27: (0, 1, 4), 28: (0, 1, 4), 30: (0, 1, 4), 31: (0, 1, 4),
            29: (0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17)}
# Retail's invisible walls (SI_EDITOR, never drawn), 48 tall: x-long 497
# (128) and 846 (96), y-long 498 (128) and 501 (96).
BLOCK_X = {128: 497, 96: 846}
BLOCK_Y = {128: 498, 96: 501}
INVISIBLE = {497, 498, 846, 501}

GROUND = {ROCK_FLOOR}
ROCK_SHAPES = {26, 27, 28, 29, 30, 31, 32, 334, 393, 138, 564}

_PAINTER = None
_BUILT = None


def _h(*v):
    h = 2166136261
    for a in v:
        h = ((h ^ (a & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def painter():
    """Painter over the retail shapes (the window fit's view of a map whose
    shots hold only retail art; built_painter() is vignette_built_window's)."""
    global _PAINTER
    if _PAINTER is None:
        from vignette_paint import Painter
        _PAINTER = Painter()
    return _PAINTER


def built_painter():
    global _BUILT
    if _BUILT is None:
        from vignette_paint import Painter
        _BUILT = Painter.built()
    return _BUILT


def _key(it):
    return (it.shape, it.frame, it.x, it.y, it.z)


def _d(it):
    return dict(shape=it.shape, frame=it.frame, x=it.x, y=it.y, z=it.z,
                flags=getattr(it, 'flags', 0))


def relift(it, h):
    """(x, y, z) -> (x+4h, y+4h, z+h): the same pixels, h units higher."""
    assert h % 2 == 0
    it.x += 4 * h
    it.y += 4 * h
    it.z += h
    return it


class Shot:
    """One vignette: its world items and its window."""

    def __init__(self, shot, art_map=None):
        self.shot = shot
        self.vig = V.load(shot)
        self.art_map = art_map or {}
        self.origin = V.origin(self.vig)
        ox, oy, oz = self.origin
        cam = self.vig['camera']
        self.csx = cam['sx0'] + (ox // 4 - oy // 4)
        self.csy = cam['sy0'] + (ox // 8 + oy // 8 - oz)
        self.W, self.H = cam['crop']
        self.items = V.world_items(self.vig, self.art_map)
        self.keys = {_key(it) for it in self.items}
        self.region = V.region(self.vig, self.art_map)
        self.lifted = set()

    # -- projection -----------------------------------------------------
    def screen(self, x, y, z=0):
        return x // 4 - y // 4 - self.csx, x // 8 + y // 8 - z - self.csy

    def floor_in_window(self, x, y):
        sx, sy = self.screen(x, y)
        return 0 <= sx < self.W and 0 <= sy < self.H

    def paints_window(self, it, p=None):
        """Does the item's sprite reach the window at all?"""
        p = p or painter()
        from item_sorter import _Item
        s = p._make(_Item(it.shape, it.frame, it.x, it.y, it.z,
                          getattr(it, 'flags', 0)), self.csx, self.csy)
        if s is None:
            return False
        if p.info(it.shape)['editor']:
            return False
        l, t, r, b = s.sr
        return r > 0 and b > 0 and l < self.W and t < self.H

    # -- what the shot shows at each floor cell ---------------------------
    def classify(self):
        """{fine cell max corner (x, y): 'F'|'P'|'R'|'V'} for every 32-unit
        cell whose centre's floor point projects inside the window. Black
        (unpainted, or a black pixel: caps, the void) is V whatever paints
        it; the cave-wall family R; ground at z 0 F; anything else — a
        prop, or a structure the shot draws there (screen10's dais) — P."""
        if hasattr(self, '_cls'):
            return self._cls
        import shot_decompose as SD
        its = [_d(i) for i in self.items]
        img, _, own = painter().paint(its, self.csx, self.csy, self.W,
                                      self.H, owner=True)
        black = (img < 0) | (SD.PAL[np.where(img >= 0, img, 0)].sum(-1) <= 12)
        ox, oy, _ = self.origin
        out = {}
        for x in range(ox - 2048 + FINE - 1, ox + 4096, FINE):
            for y in range(oy - 2048 + FINE - 1, oy + 4096, FINE):
                cx, cy = x - FINE // 2, y - FINE // 2
                sx, sy = self.screen(cx, cy)
                if not (2 <= sx < self.W - 2 and 1 <= sy < self.H - 1):
                    continue
                votes = {'F': 0, 'P': 0, 'R': 0, 'V': 0}
                win = (slice(sy - 1, sy + 2), slice(sx - 2, sx + 3))
                for k, dark in zip(own[win].ravel(), black[win].ravel()):
                    if k < 0 or dark:
                        votes['V'] += 1
                        continue
                    it = its[k]
                    if it['shape'] in GROUND and it['z'] == 0:
                        votes['F'] += 1
                    elif it['shape'] in ROCK_SHAPES:
                        votes['R'] += 1
                    else:
                        votes['P'] += 1
                out[(x, y)] = max('FPRV', key=lambda c: votes[c])
        self._cls = out
        return out

    def relift(self, items, table):
        """Apply `relift` to the stamped vignette items named in `table`
        ({(shape, frame, x, y, z) world key: h}); they stay the shot's."""
        hit = set()
        for it in items:
            k = _key(it)
            if k in table and k in self.keys and k not in hit:
                hit.add(k)
                relift(it, table[k])
                self.keys.add(_key(it))
                self.lifted.add(_key(it))
        missing = set(table) - hit
        if missing:
            raise ValueError(f'{self.shot}: relift keys not in the stamp: '
                             f'{sorted(missing)}')
        return items

    def drop(self, items, keys):
        """Leave the stamped vignette items named in `keys` out (the builder
        says why); they leave the classification too."""
        keys = set(keys)
        gone = {_key(it) for it in items if _key(it) in keys}
        if gone != keys:
            raise ValueError(f'{self.shot}: drop keys not in the stamp: '
                             f'{sorted(keys - gone)}')
        self.items = [it for it in self.items if _key(it) not in keys]
        self.keys -= keys
        self.__dict__.pop('_cls', None)
        return [it for it in items if _key(it) not in keys]

    def add(self, items, new):
        """Add items the builder solved for the shot itself (a retail
        stand-in for 1994 art, placed where its pixels match rather than
        at the 1994 piece's spot): they join the shot, so `Cave.build`
        keeps them and the classification sees them."""
        for it in new:
            self.items.append(it)
            self.keys.add(_key(it))
        self.__dict__.pop('_cls', None)
        return items + list(new)

    def owned(self):
        """Keys of the vignette items that own at least one window pixel."""
        its = [_d(i) for i in self.items]
        _, _, own = painter().paint(its, self.csx, self.csy, self.W, self.H,
                                    owner=True)
        return {_key(self.items[k]) for k in np.unique(own) if k >= 0}


def stamp(items, shot, map_num, keep=(), fill=None):
    """vignette_place.stamp, holding back the pins in `keep` ((shape, x, y,
    z) tuples) that the builder places inside the region on purpose: the
    pillar the shot itself shows, for one. Returns the new list and the
    Shot."""
    keep = set(keep)
    held = [it for it in items if (it.shape, it.x, it.y, it.z) in keep]
    rest = [it for it in items if (it.shape, it.x, it.y, it.z) not in keep]
    sh = shot if isinstance(shot, Shot) else Shot(shot)
    out = V.stamp(rest, sh.shot, map_num, sh.art_map, fill)
    return out + held, sh


def expand_chunks(items, chunks):
    """Replace the glob eggs whose 512-chunk is in `chunks` with their
    tiles, so the builder can cut them cell by cell."""
    gr = V._globs()
    out = []
    for it in items:
        if it.is_glob_egg and (it.x // 512, it.y // 512) in chunks:
            out.extend(gr.glob_to_items(it.quality, it.x, it.y, it.z))
        else:
            out.append(it)
    return out


def _box(it):
    info = V._flags().get(it.shape) or {'xfoot': 0, 'yfoot': 0, 'zfoot': 0}
    xd, yd = info['xfoot'] * 32, info['yfoot'] * 32
    if getattr(it, 'flags', 0) & 0x20:              # FLG_FLIPPED
        xd, yd = yd, xd
    return it.x - xd + 1, it.x + 1, it.y - yd + 1, it.y + 1


def _is_floor(it):
    info = V._flags().get(it.shape)
    return bool(info and (info['land'] or info['sea']) and info['zfoot'] <= 1
                and it.z == 0)


def _cells_of(it, size):
    x0, x1, y0, y1 = _box(it)
    return {(cx, cy) for cx in range(x0 // size, (x1 - 1) // size + 1)
            for cy in range(y0 // size, (y1 - 1) // size + 1)}


class Cave:
    """The cave a shot is closed into.

    `mask` is the cave drawn on the 128 grid, one string per row, one
    character per cell: '.' floor, '#' rock, anything else (by convention
    '?') left to the window. `cell0` = (column, row) of the first
    character (world x // 128, y // 128). The mask's rectangle is the box
    this closure owns: every generated item in it is rebuilt from the
    mask. Inside the window the shot decides (Shot.classify), whatever
    the mask says."""

    def __init__(self, shot, cell0, mask, salt=0, jag=False, near_courses=2):
        if type(near_courses) is not int or not 0 <= near_courses <= 2:
            raise ValueError("near_courses must be zero, one, or two")
        self.near_courses = near_courses
        self.jag = jag
        self.sh = shot
        self.salt = salt
        c0, r0 = cell0
        self.design = {}
        for j, row in enumerate(mask):
            for i, ch in enumerate(row):
                self.design[(c0 + i, r0 + j)] = ch
        self.cells = set(self.design)
        self.box = (c0 * CELL, r0 * CELL, (c0 + len(mask[0])) * CELL,
                    (r0 + len(mask)) * CELL)
        self.fine = {}                      # fine cell index -> walkable?
        self.win128 = {}
        for (x, y), c in shot.classify().items():
            self.fine[(x // FINE, y // FINE)] = c in 'FP'
            w = self.win128.setdefault((x // CELL, y // CELL), [0, 0])
            w[0 if c in 'FP' else 1] += 1
        self.outside_floor = set()

    @staticmethod
    def _in(k, rects):
        x, y = k[0] * CELL, k[1] * CELL
        return any(a <= x and x + CELL <= b and c <= y and y + CELL <= d
                   for (a, c, b, d) in rects)

    def windowed(self, k):
        """A 128 cell the window decides: half or more of its fine cells."""
        w = self.win128.get(k)
        return w is not None and sum(w) >= 8

    def floor128(self, k):
        if self.windowed(k):
            w = self.win128[k]
            return w[0] >= w[1]
        if k in self.cells:
            return self.design[k] == '.'
        return k in self.outside_floor

    def walk32(self, f):
        if f in self.fine:
            return self.fine[f]
        return self.floor128((f[0] * FINE // CELL, f[1] * FINE // CELL))

    # -- the closure -----------------------------------------------------
    def build(self, items, map_num):
        """Return `items` closed: generated items in the box rebuilt from
        the mask, the shot fenced, the rock shelled."""
        sh = self.sh
        pins = V._pinned(map_num)
        chunks = {(cx * CELL // 512, cy * CELL // 512) for cx, cy in self.cells}
        items = expand_chunks(items, chunks)
        owned = sh.owned()
        gr = V._globs()
        for it in items:
            for t in (gr.glob_to_items(it.quality, it.x, it.y, it.z)
                      if it.is_glob_egg else [it]):
                if _is_floor(t) and _key(t) not in sh.keys:
                    self.outside_floor |= {k for k in _cells_of(t, CELL)
                                           if k not in self.cells}
        floor_cells = {k for k in self.cells if self.floor128(k)}
        self.floor_cells = floor_cells
        kept, have_ground = [], set()
        for it in items:
            key = _key(it)
            cells = _cells_of(it, CELL)
            if V._is_egg(it) or (it.shape, it.x, it.y, it.z) in pins:
                kept.append(it)
                continue
            if key in sh.keys:
                # The shot's own items stay, except ground the window never
                # shows that lies under rock: from the next camera over it
                # would read as floor in the middle of the rock's black top.
                if _is_floor(it) and key not in owned and \
                        not (cells & floor_cells) and \
                        not any(self.floor128(k) for k in cells):
                    continue
                kept.append(it)
                if _is_floor(it):
                    have_ground |= cells
                continue
            if not (cells & self.cells):
                # Outside the box: the rest of the map, minus anything that
                # is not floor and paints into the shot.
                if not _is_floor(it) and sh.paints_window(it):
                    continue
                kept.append(it)
                if _is_floor(it):
                    have_ground |= cells
                continue
            if _is_floor(it):
                if cells <= floor_cells:
                    kept.append(it)
                    have_ground |= cells
                continue
            if cells <= floor_cells and not (cells & sh.region) and \
                    not sh.paints_window(it):
                kept.append(it)
        add = []
        for k in sorted(floor_cells - have_ground):
            cx, cy = k
            add.append(MapItem.placed_item(
                cx * CELL + CELL - 1, cy * CELL + CELL - 1, 0, ROCK_FLOOR,
                ROCK_FLOOR_FRAMES[_h(cx, cy, self.salt) % 7]))
        add += self.fences()
        add += self.shell(floor_cells)
        return kept + add

    def underlay(self, items):
        """A 301 tile under every floor cell `build` left without one. A
        shot item that is LAND and flat (a cliff detail 125, a pebble, a
        step block) counts as ground in `build`, so a cell whose only
        ground is such a piece got no tile and shows void round its sprite
        (screen07's 125 f7 at its bottom edge, 2026-10-17). The tile is the
        cell's own, on the 127-mod-128 lattice, under the piece."""
        tiles = {(it.x // CELL, it.y // CELL) for it in items
                 if it.shape == ROCK_FLOOR and it.z == 0
                 and it.x % CELL == CELL - 1 and it.y % CELL == CELL - 1}
        gr = V._globs()
        for it in items:
            if it.is_glob_egg:
                tiles |= {(t.x // CELL, t.y // CELL)
                          for t in gr.glob_to_items(it.quality, it.x, it.y, it.z)
                          if _is_floor(t)}
        return items + [MapItem.placed_item(
            cx * CELL + CELL - 1, cy * CELL + CELL - 1, 0, ROCK_FLOOR,
            ROCK_FLOOR_FRAMES[_h(cx, cy, self.salt) % 7])
            for cx, cy in sorted(self.floor_cells - tiles)]

    # -- dressing ---------------------------------------------------------
    def dress(self, items, per100=3, salt=0):
        """Rubble and bones clustered against the rock, on the floor this
        closure made outside the window: about `per100` props per hundred
        floor cells (retail caves run 3, the 2026-10-12 organic-maps
        census), in clusters of two to four at the foot of a wall (R < 1:
        retail scatter clusters). Nothing on an egg, a pin or another
        solid; nothing that reaches the window."""
        sh = self.sh
        cells = sorted(k for k in self.floor_cells
                       if not self.windowed(k) and k not in sh.region)
        rocky = [k for k in cells if any(
            (k[0] + dx, k[1] + dy) in self.cells and
            (k[0] + dx, k[1] + dy) not in self.floor_cells
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        n_clusters = max(1, round(len(cells) * per100 / 100 / 3))
        rocky.sort(key=lambda k: _h(k[0], k[1], salt, 11))
        taken = []
        for it in items:
            if it.is_glob_egg:
                continue
            x0, x1, y0, y1 = _box(it)
            if (x1 - x0) * (y1 - y0) >= 128 * 128 and _is_floor(it):
                continue                                  # a floor tile
            taken.append((x0, x1, y0, y1))
        out = []
        for k in rocky[:n_clusters]:
            h = _h(k[0], k[1], salt, 13)
            kit = [(782, (h >> s) % 12) for s in (0, 4, 8)][:2 + h % 2]
            if h % 3 == 0:
                kit.append((235 if h & 64 else 237, (h >> 7) % 2))
            for i, (shape, frame) in enumerate(kit):
                hh = _h(k[0], k[1], i, salt, 17)
                x = k[0] * CELL + 31 + 32 * (hh % 4)
                y = k[1] * CELL + 31 + 32 * ((hh >> 2) % 4)
                it = MapItem.placed_item(x, y, 0, shape, frame)
                b = _box(it)
                if any(b[0] < t[1] and t[0] < b[1] and b[2] < t[3] and t[2] < b[3]
                       for t in taken) or sh.paints_window(it):
                    continue
                cb = _cells_of(it, CELL)
                if not cb <= self.floor_cells:
                    continue
                taken.append(b)
                out.append(it)
        return out

    # -- invisible fences on the shot's walk/rock boundary ----------------
    def fences(self):
        """Two courses of invisible wall on every blocked fine cell the
        window decides that touches a walkable one (window or not).

        A 128 cell the window decides can reach past the frame: the fine
        cells whose centre falls outside it are not classified, and take
        the cell's majority (walk32). Those of a rock cell are fenced too,
        or a mask floor cell beside it opens onto the rock's void through
        them (screen07, 2026-10-17: (56,160) into (56,161))."""
        fine = set(self.fine)
        for (cx, cy) in self.win128:
            if self.windowed((cx, cy)):
                k = CELL // FINE
                fine |= {(cx * k + i, cy * k + j)
                         for i in range(k) for j in range(k)}
        cand = set()
        for f in fine:
            if self.walk32(f):
                continue
            if any(self.walk32((f[0] + dx, f[1] + dy))
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                cand.add(f)
        covered, out = set(), []
        for f in sorted(cand, key=lambda c: (c[1], c[0])):
            if f in covered:
                continue
            best = None
            for n, axis in ((4, 'x'), (4, 'y'), (3, 'x'), (3, 'y')):
                for off in range(n):
                    cells = [((f[0] - off + i, f[1]) if axis == 'x'
                              else (f[0], f[1] - off + i)) for i in range(n)]
                    if any(self.walk32(c) for c in cells):
                        continue
                    gain = sum(1 for c in cells if c in cand and c not in covered)
                    if best is None or gain > best[0]:
                        best = (gain, n, axis, cells)
            if best is None:
                continue                    # a lone sliver: no body fits
            _, n, axis, cells = best
            last = max(cells)
            shape = (BLOCK_X if axis == 'x' else BLOCK_Y)[n * FINE]
            for z in (0, COURSE):
                out.append(MapItem.placed_item(last[0] * FINE + FINE - 1,
                                               last[1] * FINE + FINE - 1, z,
                                               shape, 0))
            covered |= set(cells)
        return out

    # -- the rock's faces outside the window ------------------------------
    def shell(self, floor_cells):
        def floor(k):
            return k in floor_cells or (k not in self.cells and self.floor128(k))
        rock = {k for k in self.cells if k not in floor_cells
                and not self.windowed(k)}
        spans = {'S': {}, 'E': {}, 'N': {}, 'W': {}}
        for (cx, cy) in sorted(rock):
            s_face = floor((cx, cy + 1))
            if s_face:
                spans['S'].setdefault(cy, []).append(
                    (cx * CELL, cx * CELL + CELL))
            if floor((cx + 1, cy)):
                # the south run owns the corner strip of a convex corner
                spans['E'].setdefault(cx, []).append(
                    (cy * CELL, cy * CELL + CELL - (FINE if s_face else 0)))
            if floor((cx, cy - 1)):
                spans['N'].setdefault(cy, []).append(
                    (cx * CELL, cx * CELL + CELL))
            if floor((cx - 1, cy)):
                spans['W'].setdefault(cx, []).append(
                    (cy * CELL, cy * CELL + CELL))
        out = []
        for side, lines in spans.items():
            for line, sp in lines.items():
                sp.sort()
                run = list(sp[0])
                for a, b in sp[1:] + [(None, None)]:
                    if a is not None and a == run[1]:
                        run[1] = b
                        continue
                    out += self._face(side, line, run[0], run[1])
                    if a is not None:
                        run = [a, b]
        return out

    def _piece(self, shape, x, y, z):
        fr = TEXTURED[shape]
        return MapItem.placed_item(x, y, z, shape,
                                   fr[_h(x, y, z, shape, self.salt) % len(fr)])

    @staticmethod
    def _cut(length, pick):
        """Split a run length (a multiple of 32) into 128/96/64/32 pieces."""
        out, left, i = [], length, 0
        while left:
            n = min((128, 96, 64)[pick(i) % 3], left)
            if left - n == 32 and n > 64:
                n -= 32                       # leave 64, never a lone post
            out.append(n)
            left -= n
            i += 1
        return out

    def _face(self, side, line, a, b):
        """Pieces along one straight face of the rock covering [a, b) along
        the run. S/E faces are seen: cave wall, two courses, short pieces,
        some stepped 32 out over the floor. N/W faces are not: invisible
        wall in the rock's edge strip, so the floor ends at black."""
        sh = self.sh
        if side in ('S', 'E'):
            edge = (line + 1) * CELL - 1
        else:
            edge = line * CELL + FINE - 1
        xrun = side in ('S', 'N')

        def put(shape, end, off, z):
            if xrun:
                return MapItem.placed_item(end - 1, edge + off, z, shape, 0)
            return MapItem.placed_item(edge + off, end - 1, z, shape, 0)

        def invisible(lo, hi):
            res, pos = [], lo
            while pos < hi:
                n = 128 if hi - pos >= 128 or hi - lo < 96 else 96
                if hi - pos < n:
                    pos = hi - n               # overlap back, inside the run
                for z in (0, COURSE):
                    res.append(put((BLOCK_X if xrun else BLOCK_Y)[n], pos + n, 0, z))
                pos += n
            return res

        if side in ('N', 'W'):
            return invisible(a, b)
        pieces = self._cut(b - a, lambda i: _h(a, line, i, self.salt))
        res, original, pos = [], [], a
        for i, n in enumerate(pieces):
            inner = 0 < i < len(pieces) - 1
            jag = FINE if self.jag and inner and _h(line, pos, self.salt, 7) % 3 == 0 else 0
            shape = POST if n == 32 else (WALL_X if xrun else WALL_Y)[n]
            for z in (0, COURSE):
                it = put(shape, pos + n, jag, z)
                it.frame = TEXTURED[shape][_h(it.x, it.y, z, shape, self.salt)
                                           % len(TEXTURED[shape])]
                original.append(it)
                if z < self.near_courses * COURSE:
                    res.append(it)
                elif n in BLOCK_X:
                    res.append(put((BLOCK_X if xrun else BLOCK_Y)[n],
                                   pos + n, jag, z))
                else:
                    # Retail has no 32- or 64-long invisible wall. Turn a
                    # 128 wall into the rock for each 32-unit face strip;
                    # its front edge coincides with the removed jagged piece.
                    blocker = BLOCK_Y[128] if xrun else BLOCK_X[128]
                    for end in range(pos + FINE, pos + n + 1, FINE):
                        res.append(put(blocker, end, jag, z))
            pos += n
        if any(sh.paints_window(it) for it in original):
            return invisible(a, b)              # nothing generated in the shot
        return res


# -- the void ---------------------------------------------------------------

VOID_TILE = (35, 10)        # 128x128 LAND flat, all black: a cell-sized plate


def void_cover(items, within=None):
    """lv_furnish.void_floor for a map with loose SI_DRAW floor (301): the
    256-unit black plate (564) is SI_DRAW too, and where it overlaps a 301
    tile the engine's flat rules may draw it OVER the floor (seen as black
    diamonds in the screen10 window, 2026-10-17). A plate whose block holds
    such a tile is replaced by one 128 black tile (35 f10, LAND, so the
    hygiene count sees the cell covered) per void cell it served. Those
    tiles are LAND, so test_map_hygiene counts them as floor and looks a
    view further out from them: the cover is repeated until no void cell
    in view is left uncovered.

    `within` (x0, y0, x1, y1), when given, limits the swap to the blocks
    inside that box (the cave). A map whose other floors are SI_DRAW globs
    with open edges (Map 18's temple court) would otherwise breed black
    LAND tiles out from them, view after view, and a body could walk on
    them off the map; outside the box every block keeps its plate, which
    never seeds another ring."""
    import lv_furnish as LF
    from map_preview import GlobReader, expand_globs
    from parse_typeflag import load_typeflag
    p = built_painter()
    shapes = load_typeflag(os.path.join(V.HERE, '..', '..', '..', 'shared',
                                        'build', 'TYPEFLAG.DAT'))
    expanded = expand_globs(items, GlobReader())
    drawn = set()
    for it in expanded:
        if it.shape == LF.VOID_PLATE or it.z != 0:
            continue
        inf = p.info(it.shape)
        if inf['land'] and inf['draw'] and inf['zd'] <= 8:
            drawn |= {(cx * CELL + CELL - 1, cy * CELL + CELL - 1)
                      for cx, cy in _cells_of(it, CELL)}
    if within is not None:
        bx0, by0, bx1, by1 = within
        drawn = {(x, y) for x, y in drawn if bx0 <= x < bx1 and by0 <= y < by1}
    S = LF.VOID_PLATE_SPAN
    out = []
    for _ in range(8):
        void = LF.void_cells(expanded + out, shapes)
        if not void:
            break
        blocks = {((x // S) * S + S - 1, (y // S) * S + S - 1) for x, y in void}
        for bx, by in sorted(blocks):
            block = {(bx - S + CELL * (i + 1), by - S + CELL * (j + 1))
                     for i in range(2) for j in range(2)}
            if not (block & drawn):
                out.append(MapItem.placed_item(bx, by, 0, LF.VOID_PLATE,
                                               LF.VOID_PLATE_FRAME))
                continue
            for x, y in sorted(block & void):
                out.append(MapItem.placed_item(x, y, 0, *VOID_TILE))
    return out


# -- measurement -----------------------------------------------------------

def _window_items(items, sh, rad=4000):
    ox, oy, _ = sh.origin
    cx, cy = ox + 900, oy + 700
    gr = V._globs()
    out = []
    for it in items:
        if abs(it.x - cx) > rad or abs(it.y - cy) > rad:
            continue
        if it.is_glob_egg:
            out += [dict(shape=g.shape, frame=g.frame, x=g.x, y=g.y, z=g.z)
                    for g in gr.glob_to_items(it.quality, it.x, it.y, it.z)]
        else:
            out.append(dict(shape=it.shape, frame=it.frame, x=it.x, y=it.y,
                            z=it.z))
    return out


def window_score(items, shot, png=None):
    """vignette_built_window's number on an in-memory list: all-frame match,
    palette RGB within 12, an unpainted pixel matching only a black one."""
    import shot_decompose as SD
    sh = shot if isinstance(shot, Shot) else Shot(shot)
    _, (H, W), rgb = SD.load_shot(sh.shot)
    out, _ = painter().paint(_window_items(items, sh), sh.csx, sh.csy, W, H)
    pal = SD.PAL
    m = out >= 0
    eq = (np.abs(pal[np.where(m, out, 0)] - rgb).sum(-1) <= 12) & m
    blank = (~m) & (rgb.sum(-1) <= 12)
    if png:
        from PIL import Image
        o = np.zeros((H, W, 3), np.uint8)
        o[m] = pal[out[m]]
        dif = rgb.astype(np.uint8).copy()
        bad = ~(eq | blank)
        dif[bad] = (dif[bad] * 0.3 + np.array([255, 0, 0]) * 0.7).astype(np.uint8)
        Image.fromarray(np.concatenate([rgb.astype(np.uint8), o, dif], 1)) \
            .resize((W * 9, H * 3), Image.NEAREST).save(png)
    return float((eq | blank).sum()) / (H * W) * 100


def context_png(items, shot, png, k=1, scale=2, actors=()):
    """(2k+1) x (2k+1) windows around the shot's, engine draw order, the
    BUILT shapes; the shot's window outlined red, unpainted pixels dark
    magenta so real void shows. `actors`: extra dict items (the Avatar)."""
    import shot_decompose as SD
    from PIL import Image, ImageDraw
    sh = shot if isinstance(shot, Shot) else Shot(shot)
    W, H = sh.W, sh.H
    its = _window_items(items, sh, rad=2500 + k * 1600) + list(actors)
    img, _ = built_painter().paint(its, sh.csx - k * W, sh.csy - k * H,
                                   (2 * k + 1) * W, (2 * k + 1) * H)
    o = np.zeros(img.shape + (3,), np.uint8)
    m = img >= 0
    o[m] = SD.PAL[img[m]]
    o[~m] = (48, 0, 48)
    im = Image.fromarray(o)
    d = ImageDraw.Draw(im)
    d.rectangle([k * W - 1, k * H - 1, (k + 1) * W, (k + 1) * H],
                outline=(255, 0, 0))
    im.resize((im.width * scale, im.height * scale), Image.NEAREST).save(png)
    return png


def _main(argv):
    """python3 lv_cave_vignette.py context screenNN out.png [x,y,z]

    The context render of a shot from the BUILT shared/build/FIXED.DAT:
    3x3 windows round the shot's, engine draw order, built shapes, with
    the Avatar drawn at x,y,z (frame 0) when given."""
    if len(argv) < 3 or argv[0] != 'context':
        print(_main.__doc__)
        return 2
    from u8_map import MapArchive
    # Only the camera is read here: 1994-only art ids get a stub shape.
    sh = Shot(argv[1], art_map={it['shape']: (782, 0)
                                for it in V.load(argv[1])['items']
                                if it['shape'] >= V.FIRST_SYNTHETIC_ID})
    arch = MapArchive(os.path.join(V.HERE, '..', '..', '..', 'shared', 'build',
                                   'FIXED.DAT'))
    items = arch.get_map_items(sh.vig['placement']['map'])
    actors = []
    if len(argv) > 3:
        x, y, z = (int(v) for v in argv[3].split(','))
        actors.append(dict(shape=1, frame=0, x=x, y=y, z=z))
    context_png(items, sh, argv[2], actors=actors)
    print(argv[2])
    return 0


if __name__ == '__main__':
    sys.exit(_main(sys.argv[1:]))

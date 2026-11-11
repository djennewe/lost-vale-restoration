"""
lv_vale_terrain.py — cell-level terrain for the Vale (Map 10) in the 1994
materials, with retail cliff closure.

The 1994 screenshots (docs/research/2026-10-16-screenshot-reconstruction.md)
show the Vale as grey cracked rock (301 f0-6, retail glob 397/2241) and
brown earth (4 f14/15/30-33, glob 875) meeting along a ragged 386 edge, on
real height tiers closed by cliff faces. This module is the generator for
that: a `Field` of 128-unit cells, each with a walk-surface height, and a
corner lattice of materials, emitted the way retail lays its ground.

  ground   a chunk whose 16 cells are plain floor at one height in one
           material is one retail glob egg at that height; any other chunk
           is 16 loose tiles with NO glob under them (two SI_DRAW flats at
           one z have no defined draw order, .claude/rules/map-geometry.md).
  edges    the corner lattice picks 301 / 4 / 386: a cell's four corners
           are rock or earth, and the 386 frame is the one whose pixels
           carry earth in exactly those quadrants (EDGE_FRAMES, measured
           from the frames by quadrant colour, 2026-10-16). Patterns 386
           cannot draw (the two diagonals, and earth everywhere but the
           north-east) are repaired away by growing earth.
  cliffs   a cell standing 16+ above a neighbour is an edge cell. Its top
           is a crest (125 at h-8) whose frame is picked by ROLE — which
           sides drop — from retail's own usage (CREST_ROLE, tallied over
           every 125 in the pristine FIXED.DAT); its dropping sides get
           48-unit courses of the 26-32 family in the cell's outer 32-unit
           strip, from h-56 down while above the lower ground (retail's
           (8, 56) under a crest at 104 is its commonest stack). Faces the
           camera sees take textured frames, including the north and west
           faces exposed through joins in the height field.
           Convex corners facing the camera get a 29 post.
  barriers two courses of retail's invisible wall (497/498) on the edge of
           every top a player can reach — walkable tiers and anything low
           enough to jump onto (72) — so nobody walks or jumps off a cliff.

Every random choice is a hash of the cell's coordinates and a salt, never a
sequence, so a local edit stays local and the build stays reproducible.
"""

from u8_map import MapItem

CELL = 128
CHUNK = 512
STRIP = 32
WATER, WATER_DEEP, LAKE_GLOB = 347, 16, 262
# Glob 55 includes four edge-frame tiles; 262 is sixteen navy 347:16 tiles.
LAVA = 409
LAVA_EDGE = (0, 15, 20, 30)              # crusted frames on the pool's rim
LAVA_INNER = (5, 10, 25)                 # never 33, which kills
COURSE = 48

ROCK, EARTH, EDGE, CREST = 301, 4, 386, 125
ROCK_FRAMES = (0, 1, 2, 3, 4, 5, 6)
EARTH_FRAMES = (14, 15, 30, 31, 32, 33)
ROCK_GLOBS = (397, 397, 397, 2241)
EARTH_GLOB = 875

# 386 by earth quadrants (NW, NE, SE, SW) as a 4-bit string.
EDGE_FRAMES = {
    '1000': (21, 5), '0100': (16, 6), '0010': (22, 23), '0001': (14, 15, 18),
    '1100': (7,), '0110': (0, 1), '0011': (2, 3), '1001': (4,),
    '1101': (8, 9), '1110': (10, 11), '0111': (12, 13),
    # No 386 frame carries earth everywhere but the north-east, nor either
    # diagonal; `smooth` all but removes them and the mostly-earth frames
    # stand in for the few left.
    '1011': (24, 25), '1010': (24, 25), '0101': (24, 25),
}

# 125 crest frame by the sides that drop, retail's own choice per pattern.
CREST_ROLE = {
    '': (12, 13, 14), 'S': (3, 4), 'E': (1, 2), 'W': (7, 8), 'N': (9, 10),
    'ES': (0,), 'NE': (6,), 'SW': (5,), 'NW': (11,),
    'NES': (3,), 'NSW': (4,), 'ESW': (15,), 'NESW': (0,),
    'NS': (9, 10), 'EW': (1, 2), 'NEW': (6,),
}


def visible_role(sides):
    """The CREST_ROLE key for an 8-deep plate whose own sides are the only
    edge drawn over `sides` (a shore bank, a cliff's foot): the camera
    sees a plate's south and east sides, and retail's frame for a
    pattern does not always draw them ('NS' is a north frame, 'NES' a
    south one), so the frame is picked by the visible sides first."""
    s, e = 'S' in sides, 'E' in sides
    if s and e:
        return 'ES'
    if s:
        return 'SW' if 'W' in sides else 'S'
    if e:
        return 'NE' if 'N' in sides else 'E'
    return ''.join(k for k in 'NESW' if k in sides)


# Faces: shape by run length along the strip, and frames by visibility.
FACE_X = {128: 26, 96: 27, 64: 28}      # runs along x (south / north strips)
FACE_Y = {128: 32, 96: 31, 64: 30}      # runs along y (east / west strips)
LIT = {26: (0, 1, 2, 3, 4, 5, 6), 32: (0, 1, 2, 3, 4, 5, 6),
       27: (0, 1), 28: (0, 1), 31: (0, 1, 4), 30: (0, 1)}
DARK = {26: (7, 8), 32: (7, 8), 27: (3,), 28: (3,), 31: (3,), 30: (3,)}
POST = 29
# Full-width textured posts close both visible faces at terrain joins.
# Frame 6 is black; frames 7 and 9 paint only one half of the post.
POST_SE, POST_NE = (0, 1, 2), (3, 4, 5)
BAR_X, BAR_Y = 497, 498                  # invisible wall, 128x32 / 32x128
JUMP_CLIMB = 72                          # the jump auto-climbs this high

SIDES = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
OPPOSITE = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
FACE_SHAPES = {26, 27, 28, 29, 30, 31, 32, 566}


def hsh(*vals, salt=0):
    """splitmix64 over the values: deterministic per coordinate."""
    h = (salt * 0x9E3779B97F4A7C15 + 0x632BE59BD9B4E019) & 0xFFFFFFFFFFFFFFFF
    for v in vals:
        h = (h ^ (v & 0xFFFFFFFFFFFFFFFF)) * 0xBF58476D1CE4E5B9 & 0xFFFFFFFFFFFFFFFF
        h ^= h >> 31
        h = (h * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        h ^= h >> 29
    return h


def unit(*vals, salt=0):
    return (hsh(*vals, salt=salt) >> 11) / float(1 << 53)


def pick(seq, *vals, salt=0):
    return seq[hsh(*vals, salt=salt) % len(seq)]


def noise(x, y, scale, salt=0):
    """Smooth value noise in [0, 1) at world (x, y), lattice `scale`."""
    fx, fy = x / scale, y / scale
    ix, iy = int(fx // 1), int(fy // 1)
    tx, ty = fx - ix, fy - iy
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a = unit(ix, iy, salt=salt)
    b = unit(ix + 1, iy, salt=salt)
    c = unit(ix, iy + 1, salt=salt)
    d = unit(ix + 1, iy + 1, salt=salt)
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def fbm(x, y, scale, salt=0):
    return (noise(x, y, scale, salt) * 0.6 + noise(x, y, scale / 2.3, salt + 7) * 0.3
            + noise(x, y, scale / 5.1, salt + 13) * 0.1)


def cell_of(x, y):
    return x // CELL, y // CELL


def courses(h, low):
    """Face course z's under a crest at h-8 down to ground `low`."""
    zs = []
    z = h - 8 - COURSE
    while z >= 0 and z + COURSE > low:
        zs.append(z)
        z -= COURSE
    return sorted(zs)


def foot(h, low):
    """The z's of 8-deep plates under the lowest course down to `low`.
    A stack of 48 courses under a crest at h-8 ends 8 or more above the
    ground when h is not 8 + 48k over it (the tarn shelf's and the
    knoll's 64, the temple's 112 and the rim's 160 over the 0 floor all
    stop at z 8); nothing then paints the band under the face, and the
    engine, which never clears the frame, shows the last frame through
    it. Retail stands such a face on a floor at its own base (map 6's
    z 8 faces on 35 at z 8); the field's floor is lower, so a crest
    plate, whose sides are that band, fills it inside the cell."""
    zs = courses(h, low)
    return list(range(low, zs[0], 8)) if zs and zs[0] > low else []


def _tile(x, y, z, shape, frame):
    return MapItem.placed_item(x=x, y=y, z=z, shape=shape, frame=frame)


class Field:
    """Cells (cx, cy) covering x [128cx, 128cx+127], y likewise.

    H        cell -> walk-surface top z (ground cells only)
    earth    set of lattice corners (ix, iy) at world (128ix, 128iy) that
             are earth; every other corner is rock
    skip     cells someone else emits (a vignette, the lake, a stair):
             they count as ground at H for their neighbours' faces, and
             emit nothing here
    walk     cells whose top a player reaches: their drops get barriers
    open     (cell, side) pairs that get neither face nor barrier (a stair
             head, a ramp)
    water    cells of lake water at 0 (347, SEA): a chunk of nothing else
             is the uniform navy glob 262
    lava     cells of lava at 0 (409; CLRLAVA burns what touches it)
    shore    rock at 8 over the water (the screen02 island and the lake's
             causeway): a cell beside water is a 125 crest at 0 whose
             frame faces the water, the rest 301 at 8
    """

    def __init__(self, salt=10):
        self.H = {}
        self.earth = set()
        self.skip = set()
        self.walk = set()
        self.open = set()
        self.noseam = set()      # skipped cells that get no seam faces (stairs)
        self.faced = {}          # (skipped cell, side) -> lowest z a shot faces it from
        self.hidden = {}         # shot -> cells it shows no floor in
        self.water = set()
        self.vwater = set()      # a shot's own water cells (rails, shore crests)
        self.lava = set()
        self.shore = set()
        self.salt = salt
        self.skirt = set()

    # -- materials -------------------------------------------------------
    def corners(self, c):
        cx, cy = c
        return ((cx, cy), (cx + 1, cy), (cx + 1, cy + 1), (cx, cy + 1))

    def pattern(self, c):
        return ''.join('1' if k in self.earth else '0' for k in self.corners(c))

    def smooth(self, iters=2):
        """Majority-of-nine on the earth corners: no specks, no pinches.
        Growing earth to repair undrawable patterns instead cascades
        across the map (tried: 3,458 earth corners became 9,893)."""
        earth = self.earth
        for _ in range(iters):
            cand = {(ix + dx, iy + dy) for ix, iy in earth
                    for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
            earth = {(ix, iy) for ix, iy in cand
                     if sum((ix + dx, iy + dy) in earth for dx in (-1, 0, 1)
                            for dy in (-1, 0, 1)) >= 5}
        self.earth = earth

    def floor_item(self, c, z):
        cx, cy = c
        x, y = cx * CELL + CELL - 1, cy * CELL + CELL - 1
        p = self.pattern(c)
        if p == '0000':
            return _tile(x, y, z, ROCK, pick(ROCK_FRAMES, cx, cy, salt=self.salt))
        if p == '1111':
            return _tile(x, y, z, EARTH, pick(EARTH_FRAMES, cx, cy, salt=self.salt))
        return _tile(x, y, z, EDGE, pick(EDGE_FRAMES[p], cx, cy, salt=self.salt))

    # -- heights ---------------------------------------------------------
    def drops(self, c):
        """{side: lower ground z} for every side that drops 16 or more."""
        h = self.H[c]
        out = {}
        for s, (dx, dy) in SIDES.items():
            if (c, s) in self.open:
                continue
            n = (c[0] + dx, c[1] + dy)
            hn = self.H.get(n)
            if hn is None:
                if h >= 16:
                    out[s] = 0
            elif hn <= h - 16:
                out[s] = hn
        return out

    # -- emission --------------------------------------------------------
    def emit(self, cells=None, floors=True, faces=True, force=False):
        """Items for `cells` (default: every non-skip cell; `force` emits
        listed skip cells too — a vignette's hidden cells). The lit faces
        against a shot's higher cells are `seam_faces`, laid separately."""
        cells = [c for c in (cells if cells is not None else self.H)
                 if c in self.H and (force or c not in self.skip)]
        items = []
        globbed = set()
        if floors:
            items += self._globs(cells, globbed)
        for c in sorted(cells):
            d = self.drops(c)
            if floors and c not in globbed:
                items += self._top(c, d)
            if faces and d:
                items += self._faces(c, d)
            if faces:
                items += self._seam_walls(c)
        return items

    def _seams(self, c):
        """(side, neighbour, its height, course z's, foot plate z's) for
        every HIGHER skipped neighbour of this cell (a vignette's tier at
        the edge of its window) whose drop onto this cell nobody closes:
        not a stair's, not an open side. A side the shot already faces
        down to this cell's ground is closed; one it faces only part way
        (its frame cut the scarp off above the foot) gets the courses
        under the shot's lowest face, and plates under them where they
        stop above the ground (`foot`). The back faces (south, east) the
        shot draws are left as they are."""
        if c in self.noseam:
            return []
        h = self.H[c]
        out = []
        for s, (dx, dy) in SIDES.items():
            n = (c[0] + dx, c[1] + dy)
            if n not in self.skip or n not in self.H or n in self.noseam or \
                    (c, s) in self.open or self.H[n] < h + 16:
                continue
            top = self.faced.get((n, OPPOSITE[s]))
            if top is not None and (s in 'SE' or top <= h):
                continue
            if top is None:
                top = self.H[n] - 8
            zs, z = [], top - COURSE
            while z >= 0 and z + COURSE > h:
                zs.append(z)
                z -= COURSE
            plates = list(range(h, min(zs, default=top), 8))
            out.append((s, n, self.H[n], sorted(zs), plates))
        return out

    def _seam_walls(self, c):
        """A higher skipped neighbour to the south or east turns its back
        face to this cell, which the camera never sees: invisible wall in
        this cell's strip stops a body there and paints nothing over the
        shot behind it."""
        X, Y = c[0] * CELL + CELL - 1, c[1] * CELL + CELL - 1
        out = []
        for s, n, hn, zs, _ in self._seams(c):
            if s in 'SE':
                bar = BAR_X if s == 'S' else BAR_Y
                out += [_tile(X, Y, z, bar, 0) for z in courses(hn, self.H[c])]
        return out

    def seam_faces(self, cells=None, force=False):
        """The lit faces of every higher skipped neighbour to the north or
        west: in the NEIGHBOUR's own south or east strip, where retail
        and the shots put a cliff's face, continuing the shot's face run.
        They stand in the shot's cells, so they are laid after the stamp
        (which clears every generated item there). Where the courses stop
        above this cell's ground, foot plates in the neighbour fill the
        band under them (`foot`)."""
        cells = [c for c in (cells if cells is not None else self.H)
                 if c in self.H and (force or c not in self.skip)]
        out = []
        salt = self.salt + 5
        feet = {}
        for c in sorted(cells):
            X, Y = c[0] * CELL + CELL - 1, c[1] * CELL + CELL - 1
            for s, n, hn, zs, plates in self._seams(c):
                if s == 'N':
                    x, y, shape = X, Y - CELL, FACE_X[CELL]
                elif s == 'W':
                    x, y, shape = X - CELL, Y, FACE_Y[CELL]
                else:
                    continue
                for z in zs:
                    out.append(_tile(x, y, z, shape,
                                     pick(LIT[shape], x, y, z, salt=salt)))
                if plates:
                    sides, zp = feet.get(n, ('', set()))
                    feet[n] = (sides + OPPOSITE[s], zp | set(plates))
        for n in sorted(feet):
            sides, zp = feet[n]
            role = visible_role(sides)
            x, y = n[0] * CELL + CELL - 1, n[1] * CELL + CELL - 1
            for z in sorted(zp):
                out.append(_tile(x, y, z, CREST,
                                 pick(CREST_ROLE[role], n[0], n[1], salt=salt)))
        return out

    def _skirt_join(self, c):
        return c in self.skirt and any(
            (c[0]+SIDES[s][0], c[1]+SIDES[s][1]) in self.H
            for s in self.drops(c))

    def _plain(self, c):
        return (c in self.skirt and not self._skirt_join(c) or
                not self.drops(c)) and c not in self.water and \
            c not in self.lava and c not in self.shore

    def _wet_sides(self, c):
        """The sides of a shore cell against water: the field's, and a
        shot's own (vwater), whose edge the shore's crest must draw."""
        wet = self.water | self.vwater
        return ''.join(s for s in 'NESW'
                       if (c[0] + SIDES[s][0], c[1] + SIDES[s][1]) in wet)

    def _globs(self, cells, globbed):
        """One retail glob egg per chunk that is 16 plain cells at one
        height in one material."""
        want = set(cells)
        chunks = {(cx // 4, cy // 4) for cx, cy in want}
        items = []
        for kx, ky in sorted(chunks):
            block = [(kx * 4 + i, ky * 4 + j) for i in range(4) for j in range(4)]
            if not all(b in want for b in block):
                continue
            if all(b in self.water for b in block):
                items.append(MapItem.glob_egg(kx * CHUNK + CHUNK - 1,
                                              ky * CHUNK + CHUNK - 1, 0, LAKE_GLOB))
                globbed.update(block)
                continue
            hs = {self.H[b] for b in block}
            if len(hs) != 1 or not all(self._plain(b) for b in block):
                continue
            pats = {self.pattern(b) for b in block}
            if pats == {'0000'}:
                glob = pick(ROCK_GLOBS, kx, ky, salt=self.salt + 1)
            elif pats == {'1111'}:
                glob = EARTH_GLOB
            else:
                continue
            items.append(MapItem.glob_egg(kx * CHUNK + CHUNK - 1,
                                          ky * CHUNK + CHUNK - 1,
                                          hs.pop(), glob))
            globbed.update(block)
        return items

    def _top(self, c, d):
        h = self.H[c]
        cx, cy = c
        X, Y = cx * CELL + CELL - 1, cy * CELL + CELL - 1
        if c in self.water or c in self.vwater:
            # (a vwater cell is emitted only when a shot hides it: a lake
            # cell its frame left no floor in)
            return [_tile(X, Y, 0, WATER, WATER_DEEP)]
        if c in self.skirt and not self._skirt_join(c):
            return [self.floor_item(c, h)]
        if c in self.lava:
            dry = any((cx + dx, cy + dy) not in self.lava
                      for dx, dy in SIDES.values())
            return [_tile(X, Y, 0, LAVA,
                          pick(LAVA_EDGE if dry else LAVA_INNER, cx, cy,
                               salt=self.salt + 4))]
        if c in self.shore:
            # an 8-deep crest whose sides are the bank over the water, or
            # over any lower ground beside it; a flat rock tile would leave
            # that band unpainted
            low = set(self._wet_sides(c)) | {
                s for s, (dx, dy) in SIDES.items()
                if self.H.get((cx + dx, cy + dy), -1) < h}
            if low:
                return [_tile(X, Y, h - 8, CREST,
                              pick(CREST_ROLE[visible_role(low)], cx, cy,
                                   salt=self.salt + 2))]
            return [_tile(X, Y, h, ROCK, pick(ROCK_FRAMES, cx, cy, salt=self.salt))]
        if not d:
            return [self.floor_item(c, h)]
        cx, cy = c
        role = ''.join(s for s in 'NESW' if s in d)
        frames = CREST_ROLE.get(role, CREST_ROLE[''])
        out = [_tile(cx * CELL + CELL - 1, cy * CELL + CELL - 1, h - 8, CREST,
                     pick(frames, cx, cy, salt=self.salt + 2))]
        if c in self.walk or any(h - low <= JUMP_CLIMB for low in d.values()):
            out += self._barriers(c, d)
        return out

    def _barriers(self, c, d):
        cx, cy = c
        X, Y = cx * CELL + CELL - 1, cy * CELL + CELL - 1
        h = self.H[c]
        out = []
        for z in (h, h + COURSE):
            if 'S' in d:
                out.append(_tile(X, Y, z, BAR_X, 0))
            if 'N' in d:
                out.append(_tile(X, Y - CELL + STRIP, z, BAR_X, 0))
            if 'E' in d:
                out.append(_tile(X, Y, z, BAR_Y, 0))
            if 'W' in d:
                out.append(_tile(X - CELL + STRIP, Y, z, BAR_Y, 0))
        return out

    def _faces(self, c, d):
        cx, cy = c
        X, Y = cx * CELL + CELL - 1, cy * CELL + CELL - 1
        h = self.H[c]
        out = []
        salt = self.salt + 3

        def run(shape_by_len, length, x, y, side, lit):
            shape = shape_by_len[length]
            # A lower neighbour exposes this face through terrain joins.
            frames = LIT[shape]
            for z in courses(h, d[side]):
                out.append(_tile(x, y, z, shape,
                                 pick(frames, x, y, z, salt=salt)))

        # A back face (north, west) over the void is never seen and never
        # walked into: leave it out.
        for s in ('N', 'W'):
            dx, dy = SIDES[s]
            if s in d and self.H.get((cx + dx, cy + dy)) is None:
                d = {k: v for k, v in d.items() if k != s}
        se = 'S' in d and 'E' in d
        if 'S' in d:
            if se:
                run(FACE_X, 96, X - STRIP, Y, 'S', True)
            else:
                run(FACE_X, 128, X, Y, 'S', True)
        if 'N' in d:
            if 'E' in d:
                run(FACE_X, 96, X - STRIP, Y - CELL + STRIP, 'N', False)
            else:
                run(FACE_X, 128, X, Y - CELL + STRIP, 'N', False)
        if 'E' in d:
            y1 = Y - (STRIP if 'S' in d else 0)
            y0 = Y - CELL + (STRIP if 'N' in d else 0)
            run(FACE_Y, y1 - y0, X, y1, 'E', True)
        if 'W' in d:
            y1 = Y - (STRIP if 'S' in d else 0)
            y0 = Y - CELL + (STRIP if 'N' in d else 0)
            run(FACE_Y, y1 - y0, X - CELL + STRIP, y1, 'W', False)
        for corner, sides, x, y, frames in (
                ('se', ('S', 'E'), X, Y, POST_SE),
                ('ne', ('N', 'E'), X, Y - CELL + STRIP, POST_NE)):
            if all(s in d for s in sides):
                low = min(d[s] for s in sides)
                for z in courses(h, low):
                    out.append(_tile(x, y, z, POST, pick(frames, x, y, z, salt=salt)))
        if d:
            role = visible_role(d)
            for z in foot(h, min(d.values())):
                out.append(_tile(X, Y, z, CREST,
                                 pick(CREST_ROLE[role], cx, cy, z, salt=salt)))
        return out


# ---------------------------------------------------------------------------
# Stairs: retail's cobble step blocks (frame 1), the screen17 kit.
# ---------------------------------------------------------------------------
STEP_X = {8: 98, 16: 112, 24: 99, 32: 100, 48: 107}   # 96 x 32 blocks
STEP_FRAME = 1


def _stack(height):
    """Block heights, bottom up, that fill `height` (a multiple of 8)."""
    parts = []
    while height >= COURSE:
        parts.append(COURSE)
        height -= COURSE
    if height == 40:
        parts += [32, 8]
    elif height:
        parts.append(height)
    return parts


def step_stair(x_cols, y_rows, tops, base=0):
    """A stair of 96x32 step blocks. `x_cols`: block max-corner x's (96
    apart); `y_rows`: each step's max-corner y (32 apart); `tops`: each
    step's walk-surface z. Every step is solid from `base` to its top, so
    nothing walks under it."""
    items = []
    for y, top in zip(y_rows, tops):
        for x in x_cols:
            z = base
            for part in _stack(top - base):
                items.append(_tile(x, y, z, STEP_X[part], STEP_FRAME))
                z += part
    return items


def stair_barriers(x_lo, x_hi, y_rows, tops, base=0):
    """Invisible walls down both sides of a stair (x in (x_lo, x_hi]), so
    its open sides are not a drop: 32x128 pieces, one per 128 of length,
    courses from the ground to 96 over the highest step they flank."""
    items = []
    ys = sorted(y_rows)
    lo, hi = ys[0] - STRIP, ys[-1]
    for y in range(lo + CELL, hi + CELL, CELL):
        span = [t for r, t in zip(y_rows, tops) if y - CELL < r <= y]
        if not span:
            continue
        top = max(span) + 2 * COURSE
        for x in (x_lo, x_hi + STRIP):
            z = base
            while z < top:
                items.append(_tile(x, min(y, hi), z, BAR_Y, 0))
                z += COURSE
    return items

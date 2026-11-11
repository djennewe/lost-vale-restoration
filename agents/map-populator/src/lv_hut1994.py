"""
lv_hut1994.py — the Gunnar huts of the 1994 screenshots, made whole.

screen19 shows Atli's hut from the south-east: retail plank walls (145, 146,
149, 150, 194) and posts (148) under a 412 hip roof at z 40, 410 eaves 64
out along the front, 118 trims down the sides (ReconVillage-REPORT.md).
screen20 and screen22 show two more huts of the same design from the other
side, roof and trims only. A shot shows two walls of a hut at most; the
camera never sees the other two from outside (they face away), but a
player inside does once the roof lifts, and they are what closes the hut.

`complete_huts()` builds each hut whole on its roof's footprint — walls
flush with the roof's edge, as screen19's are — and returns only the pieces
its shot does not already place, so every shot keeps its own pixels.

Roof frames are retail's own 4-wide 412 roofs (maps 4, 5, 7, 8, 37: a 4x4
is rows [31,30,27,28] [29,42,33,33] [26,32,34,33] [25,32,32,34]; a 4x8
repeats [29,48,33,33] between a [29,44,..] and a [29,43,..] row).
"""

from u8_map import MapItem
from vignette_place import load, world_items

ROOF, EAVE, TRIM = 412, 410, 118
WALL_Y128, WALL_Y96 = 145, 146      # runs along y (west / east walls)
WALL_X128, WALL_X96 = 149, 150      # runs along x (north / south walls)
POST = 148
ROOF_Z = 40
FOOT = {ROOF: (128, 128), EAVE: (128, 32), TRIM: (32, 128),
        WALL_Y128: (32, 128), WALL_Y96: (32, 96), WALL_X128: (128, 32),
        WALL_X96: (96, 32), POST: (32, 32), 194: (128, 32), 255: (32, 32),
        647: (32, 128)}


def roof_rows(rows):
    """412 frames per row of a 4-wide hip roof `rows` deep."""
    mids = rows - 3
    if mids == 1:
        mid = [[29, 42, 33, 33]]
    else:
        mid = [[29, 44, 33, 33]] + [[29, 48, 33, 33]] * (mids - 2) + \
              [[29, 43, 33, 33]]
    return [[31, 30, 27, 28]] + mid + [[26, 32, 34, 33], [25, 32, 32, 34]]


def _run(items, a0, a1, fixed, along_x, door=None):
    """Wall pieces covering (a0, a1] along x (or y), at max corner `fixed`
    across, leaving `door` = (d0, d1] open: 128 pieces, then 96, then
    posts for what is left."""
    a = a0
    while a < a1:
        if door and door[0] <= a < door[1]:
            a = door[1]
            continue
        room = (door[0] if door and a < door[0] else a1) - a
        for length, shape in ((128, WALL_X128 if along_x else WALL_Y128),
                              (96, WALL_X96 if along_x else WALL_Y96),
                              (32, POST)):
            if room >= length:
                break
        end = a + length
        x, y = (end - 1, fixed) if along_x else (fixed, end - 1)
        items.append(MapItem.placed_item(x, y, 0, shape, 0))
        a = end


def hut(x0, y0, rows, door):
    """A 4-wide hut (512) `rows` tiles deep, roof north-west corner at
    (x0, y0); `door` = (side, a0, a1): a 128 gap in that wall."""
    w, d = 512, rows * 128
    x1, y1 = x0 + w - 1, y0 + d - 1
    items = []
    for j, frames in enumerate(roof_rows(rows)):
        for i, f in enumerate(frames):
            items.append(MapItem.placed_item(x0 + 127 + 128 * i,
                                             y0 + 127 + 128 * j, ROOF_Z, ROOF, f))
    for x, y in ((x0 + 31, y0 + 31), (x1, y0 + 31), (x0 + 31, y1), (x1, y1)):
        items.append(MapItem.placed_item(x, y, 0, POST, 0))
    side, d0, d1 = door
    _run(items, x0 + 32, x1 - 31, y0 + 31, True, (d0, d1) if side == 'N' else None)
    _run(items, x0 + 32, x1 - 31, y1, True, (d0, d1) if side == 'S' else None)
    _run(items, y0 + 32, y1 - 31, x0 + 31, False, (d0, d1) if side == 'W' else None)
    _run(items, y0 + 32, y1 - 31, x1, False, (d0, d1) if side == 'E' else None)
    for i in range(4):
        items.append(MapItem.placed_item(x0 + 127 + 128 * i, y1 + 64, ROOF_Z, EAVE, 3))
    for j in range(rows):
        y = y0 + 127 + 128 * j
        items.append(MapItem.placed_item(x0 - 1, y, ROOF_Z, TRIM, 5))
        items.append(MapItem.placed_item(x1 + 32, y, ROOF_Z, TRIM, 3 + j % 2))
    return items


# (shot, roof north-west corner, rows, door). screen19's door is the shot's
# own gap; the others face the yard each shot shows.
HUTS = [
    ('screen19', (18944, 6272), 5, ('S', 19104, 19232)),
    ('screen20', (20992, 8192), 7, ('S', 21024, 21152)),
    ('screen22', (18432, 8192), 4, ('S', 18592, 18720)),
]


def _box(it):
    w, d = FOOT.get(it.shape, (0, 0))
    return it.x - w, it.x, it.y - d, it.y


def _meets(a, b):
    return a[0] < b[1] and b[0] < a[1] and a[2] < b[3] and b[2] < a[3]


# A shot's wall piece one strip behind the hut's wall line (north of a
# south wall, west of an east wall) is a recessed bay, not a second wall:
# screen19's 194 window piece stands at y 6879, 32 inside the 6911 line,
# and a post in front of it would paint over it.
X_WALLS, Y_WALLS = {WALL_X128, WALL_X96, 194}, {WALL_Y128, WALL_Y96, 647}


def _covered(it, have):
    x0, x1, y0, y1 = _box(it)
    for h in have:
        if h.shape == ROOF or h.z != it.z:
            continue
        hb = _box(h)
        if _meets(hb, (x0, x1, y0, y1)):
            return True
        if h.shape in X_WALLS and _meets(hb, (x0, x1, y0 - 32, y1 - 32)):
            return True
        if h.shape in Y_WALLS and _meets(hb, (x0 - 32, x1 - 32, y0, y1)):
            return True
    return False


def complete_huts(huts=HUTS):
    """Every piece of each hut its shot does not already place: a roof
    tile where the shot has none at that cell, a wall or post where none
    of the shot's walls, posts or trims meets its box or stands one strip
    behind it."""
    out = []
    for shot, (x0, y0), rows, door in huts:
        have = [it for it in world_items(load(shot)) if it.shape in FOOT]
        for it in hut(x0, y0, rows, door):
            if it.shape == ROOF:
                if any(h.shape == ROOF and (h.x, h.y) == (it.x, it.y) for h in have):
                    continue
            elif _covered(it, have):
                continue
            out.append(it)
    return out

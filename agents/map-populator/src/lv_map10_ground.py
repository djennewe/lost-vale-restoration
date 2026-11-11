"""
lv_map10_ground.py — the Vale's ground, heights and closure (Map 10).

The 1994 screenshots of the Vale (screens 02, 09, 17-22) show grey rock and
brown earth on real height tiers: a 104 mesa over the mushroom garden, a 64
knoll by the lava, a 112 shelf over the sunken temple, a 64 tarn shelf west
of the lake, and the Gunnar village's dirt yards sunk in a 56 rock plateau.
build_map_10 places each shot verbatim (vignette_place.stamp); this module
builds everything around them so no shot is an island:

  * `map10_field()` — the height field over the vale's outline: ground at
    the TERRAIN table's heights, the Passage Test ramp as eight 8-unit
    cell rows, a cliff rim one cell beyond the outline (two courses and a
    crest, a third tier behind it in the north-west, Fable's "great cliffs
    to the Northwest"), and the RELIEF masks — hand-laid per area, as
    retail's maps are, so each tier continues a shot's own edge at the
    shot's own height and closes it with cliff faces outside the shot.
  * the material lattice — earth in the village basins, along every track,
    on the garden mesa and in scattered sheets; rock everywhere else; the
    vignettes' own border tiles seed the lattice at their edges so the
    386 transitions run into each shot's ground.
  * stairs (retail cobble step blocks) onto the walkable tiers.

lv_vale_terrain.Field does the emission. Pins never sit on a raised cell
(map10_field asserts it); props the zone builders put on a cell that is now
raised are lifted onto it (`lift_props`).
"""

import json
import os

from u8_map import MapItem
from lv_vale_terrain import (Field, CELL, fbm, noise, unit, pick, step_stair,
                             stair_barriers, EDGE_FRAMES, FACE_SHAPES, STEP_X,
                             STEP_FRAME, CREST, COURSE, STRIP, BAR_X, BAR_Y,
                             FACE_X, FACE_Y, LIT, POST, POST_SE, _stack, CREST_ROLE)

STEP_SHAPES = frozenset(STEP_X.values())
FALL_HURTS = 80      # exact_reach: a fall this deep hurts, 104 kills

HERE = os.path.dirname(os.path.abspath(__file__))
PINS = os.path.join(HERE, 'map_pins.json')

RIM_Z = 104          # two 48 courses and a crest: the old rim's height
BACK_Z = 152         # the north-west backdrop behind it
RIM_HIGH = 160       # three courses: beside the ramp, the plateau, a tier
ROOFS = {412, 34, 36, 647}   # roof tiles: LAND at z 40, not a floor
LAKE = (11264, 15360, 15360, 20480)       # x0, y0, x1, y1: the old rectangle

# ---------------------------------------------------------------------------
# RELIEF: the tiers, per area, as cell rectangles (inclusive), laid in order
# (a later rectangle overwrites an earlier one). Heights stay on retail's
# stacks — 56/64 (one course and a crest), 104/112 (two) — so every drop
# is whole courses. `jag` erodes the rectangle's outline by up to that
# many cells, by a hash of the cell, except where `keep` says (a side a
# shot fixes): retail's cliff runs are 1-3 tiles, not a ruler line.
# ---------------------------------------------------------------------------
GARDEN_Z, KNOLL_Z, TEMPLE_Z, TARN_Z, PLATEAU_Z, CREST_Z = 104, 64, 112, 64, 56, 104


def _rect(z, x0, y0, x1, y1, walk=False, jag=0, keep='', salt=0):
    return dict(z=z, box=(x0, y0, x1, y1), walk=walk, jag=jag, keep=keep,
                salt=salt)


RELIEF = [
    # The lava field (screen21) runs on south-east into what was a void
    # notch between the cloud approach and Moriens' ruins: valley floor.
    _rect(0, 72, 168, 87, 183),
    # The mushroom garden mesa (screen18): the shot's scarp at y 20607
    # runs on east and west, the mesa closes north of the window and stops
    # short of spider group 7 (trigger (9860,19532), egg (10500,19500)).
    _rect(GARDEN_Z, 71, 154, 84, 160, walk=True, jag=1, keep='SN', salt=1),
    # The knoll with the skull-post pen (screen21): the shot's east face at
    # x 9215 stays; it runs on south past the window and closes there.
    _rect(KNOLL_Z, 64, 162, 71, 176, walk=True, jag=1, keep='ENS', salt=2),
    # The temple shelf (screen17): the shot's z 112 plateau, a west and an
    # east arm framing the pit the stair goes down into, the pit open to
    # the forecourt south of it (trigger 211). The shot sees past the
    # shelf face's east end (x 18943) down into the pit, so the east arm
    # starts a cell beyond it, at x 19072.
    _rect(TEMPLE_Z, 135, 172, 150, 177, walk=True, jag=1, keep='N', salt=3),
    _rect(TEMPLE_Z, 135, 178, 140, 183, walk=True, jag=1, keep='E', salt=4),
    _rect(TEMPLE_Z, 149, 176, 151, 183, walk=True, jag=1, keep='W', salt=5),
    # The tarn shelf (screen09) and the higher ground behind it, out over
    # the lake's north-west corner: scenery, not walked. The shot sees the
    # waterfall's cliff over open ground north of y 16000, so the shelf
    # starts south of it.
    _rect(TARN_Z, 82, 125, 87, 133, jag=1, keep='E', salt=6),
    _rect(TEMPLE_Z, 81, 117, 89, 121, jag=1, keep='S', salt=7),
    # Gunnar (screens 19, 20): the rock plateau the yards are sunk in.
    _rect(PLATEAU_Z, 152, 53, 159, 58, jag=1, keep='', salt=8),
    _rect(PLATEAU_Z, 148, 57, 153, 60, jag=0, salt=9),
    # (the east block stands north-east of screen20's south-west crest
    # corner at (20799, 7999), so it ends at y 7935, behind the shot's face)
    _rect(PLATEAU_Z, 163, 60, 165, 61, jag=1, keep='W', salt=10),
    _rect(PLATEAU_Z, 152, 67, 158, 73, jag=1, keep='E', salt=11),
    # The Sacred Circle's horseshoe crest, north-east behind the ring.
    _rect(CREST_Z, 163, 120, 171, 126, jag=1, salt=12),
    _rect(CREST_Z, 169, 127, 172, 129, jag=1, salt=13),
]


def relief_cells(r):
    """The cells of one RELIEF rectangle after its jag. A cell the jag took
    from between two it kept, on opposite sides, comes back: a notch one
    cell wide shows the void plate through the gaps its four faces leave
    (screen17's east arm at (151,180))."""
    x0, y0, x1, y1 = r['box']
    out = set()
    for cx in range(x0, x1 + 1):
        for cy in range(y0, y1 + 1):
            d = {'W': cx - x0, 'E': x1 - cx, 'N': cy - y0, 'S': y1 - cy}
            side = min(d, key=d.get)
            if r['jag'] and d[side] < r['jag'] and side not in r['keep']:
                if unit(cx, cy, salt=900 + r['salt']) < 0.45:
                    continue
            out.add((cx, cy))
    notches = {(cx, cy) for cx in range(x0, x1 + 1) for cy in range(y0, y1 + 1)
               if (cx, cy) not in out and
               ({(cx - 1, cy), (cx + 1, cy)} <= out or
                {(cx, cy - 1), (cx, cy + 1)} <= out)}
    return out | notches


def apply_relief(field, relief=RELIEF):
    for r in relief:
        for c in relief_cells(r):
            field.H[c] = r['z']
            field.walk.discard(c)
            if r['walk']:
                field.walk.add(c)


def _cells_of_chunks(chunks):
    cells = {}
    for (kx, ky), z in chunks.items():
        for i in range(4):
            for j in range(4):
                cells[(kx * 4 + i, ky * 4 + j)] = z
    return cells


def lake_cells():
    x0, y0, x1, y1 = LAKE
    return {(cx, cy) for cx in range(x0 // CELL, x1 // CELL)
            for cy in range(y0 // CELL, y1 // CELL)}


def rim_cells(ground, nw=lambda cx, cy: False, flush=frozenset()):
    """Cells one step beyond the outline (8-neighbourhood) get the rim;
    where `nw` says so a second band behind it gets the backdrop height.
    `flush` cells get no raised rim on their south and east sides."""
    rim = {}
    for (cx, cy) in ground:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (cx + dx, cy + dy)
                if n in ground or n in rim:
                    continue
                if (cx, cy) in flush and (dx > 0 or dy > 0):
                    continue
                rim[n] = RIM_Z
    back = {}
    for (cx, cy) in rim:
        if not nw(cx, cy):
            continue
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (cx + dx, cy + dy)
                if n not in ground and n not in rim:
                    back[n] = BACK_Z
    rim.update(back)
    return rim


def plateau_cells(plateau):
    """The Passage Test plateau's cells: (cx0, cy0, ncx, ncy)."""
    return {(plateau[0] + i, plateau[1] + j) for i in range(plateau[2])
            for j in range(plateau[3])}


def flush_sides(plate, H):
    """(cell, side) for each ground cell's south or east side over void."""
    return [(c, s) for c in sorted(plate) for s, n in
            (('S', (c[0], c[1] + 1)), ('E', (c[0] + 1, c[1])))
            if n not in H]


def flush_edges(f, plate):
    """Close south and east edges in the 32-unit strip beyond the ground.

    Faces end at the adjacent ground height. Two invisible courses above
    that height retain the anti-climb barrier. The z=0 edges have no drawn
    face; their water skirt is emitted separately.
    """
    out = []
    salt = f.salt + 6
    sides = f.flush_side_list
    for (cx, cy), s in sides:
        h = f.H[(cx, cy)]
        X, Y = cx * CELL + CELL - 1, cy * CELL + CELL - 1
        if s == 'S':
            x, y, shape, bar = X, Y + STRIP, FACE_X[CELL], BAR_X
        else:
            x, y, shape, bar = X + STRIP, Y, FACE_Y[CELL], BAR_Y
        for z in range(h - COURSE, -1, -COURSE):
            out.append(MapItem.placed_item(x, y, z, shape,
                                           pick(LIT[shape], x, y, z, salt=salt)))
        for z in (h, h + COURSE):
            out.append(MapItem.placed_item(x, y, z, bar, 0))
    done = {c for c, _ in sides}
    for c in sorted(done):
        if (c, 'S') in sides and (c, 'E') in sides:
            x, y = c[0] * CELL + CELL - 1 + STRIP, c[1] * CELL + CELL - 1 + STRIP
            for z in range(f.H[c] - COURSE, -1, -COURSE):
                out.append(MapItem.placed_item(x, y, z, POST,
                                               pick(POST_SE, x, y, z, salt=salt)))
    return out



# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------
def _seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    L = vx * vx + vy * vy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L))
    qx, qy = ax + t * vx, ay + t * vy
    return ((px - qx) ** 2 + (py - qy) ** 2) ** 0.5


def earth_corners(field, discs, tracks, salt=40):
    """Earth on the lattice corners: discs (x, y, r) with a noisy edge, and
    bands along the track polylines 1-3 tiles wide."""
    ixs = [c[0] for c in field.H]
    iys = [c[1] for c in field.H]
    segs = [(a, b) for pts in tracks for a, b in zip(pts, pts[1:])]
    for ix in range(min(ixs), max(ixs) + 2):
        for iy in range(min(iys), max(iys) + 2):
            x, y = ix * CELL, iy * CELL
            warp = (fbm(x, y, 900, salt) - 0.5) * 2
            hit = False
            for dx, dy, r in discs:
                d = ((x - dx) ** 2 + (y - dy) ** 2) ** 0.5
                if d < r * (1.0 + 0.45 * warp):
                    hit = True
                    break
            if not hit:
                w = 110 + 170 * noise(x, y, 700, salt + 3)
                for (ax, ay), (bx, by) in segs:
                    if min(ax, bx) - 400 <= x <= max(ax, bx) + 400 and \
                       min(ay, by) - 400 <= y <= max(ay, by) + 400 and \
                       _seg_dist(x, y, ax, ay, bx, by) < w:
                        hit = True
                        break
            if hit:
                field.earth.add((ix, iy))


EDGE_BY_FRAME = {f: p for p, fs in EDGE_FRAMES.items() for f in fs
                 if p not in ('1011', '1010', '0101')}


def seed_from_vignette(field, items):
    """Set the lattice corners at a vignette's ground tiles to what the
    tile shows, so the generated transitions meet the shot's ground."""
    for it in items:
        s, f = it.shape, it.frame
        if it.x % CELL != CELL - 1 or it.y % CELL != CELL - 1:
            continue
        c = (it.x // CELL, it.y // CELL)
        ks = field.corners(c)
        if s == 4:
            pat = '1111'
        elif s in (301, 125):
            pat = '0000'
        elif s == 386 and f in EDGE_BY_FRAME:
            pat = EDGE_BY_FRAME[f]
        else:
            continue
        for k, bit in zip(ks, pat):
            if bit == '1':
                field.earth.add(k)
            else:
                field.earth.discard(k)


def load_pins(map_num=10):
    with open(PINS) as f:
        return [p for p in json.load(f)['maps'][str(map_num)] if p['x'] >= 64]



# ---------------------------------------------------------------------------
# The lake: the screen02 island, its causeway and pier, at 8 over the water
# ---------------------------------------------------------------------------
# The shot puts a broad rock shore at z 8 where the old 3x3 deck was, and
# open water where the pier ran into it (x 13696..13951, y 18816..19327).
# So the pier stops a cell short of the shot, turns west along a deck and
# runs north as a causeway beside the window onto the island, which the
# shot's shore continues beyond its frame.
ISLAND = dict(box=(100, 136, 116, 146), jag=2, salt=21)
CAUSEWAY = [(cx, cy) for cx in (103, 104) for cy in range(147, 151)]
DECK = [(cx, 151) for cx in range(103, 109)]
PIER = [(cx, cy) for cx in (107, 108) for cy in range(151, 160)]
SHORE_Z = 8


def island_cells():
    x0, y0, x1, y1 = ISLAND['box']
    out = set()
    for cx in range(x0, x1 + 1):
        for cy in range(y0, y1 + 1):
            d = min(cx - x0, x1 - cx, cy - y0, y1 - cy)
            if d < ISLAND['jag'] and unit(cx, cy, salt=ISLAND['salt']) < 0.5 + 0.2 * d:
                continue
            out.add((cx, cy))
    return out


# The lava pool of screen21 runs on south-east of the shot's corner.
LAVA_POOL = dict(centre=(76.5, 170.0), radii=(3.6, 4.6), salt=31)


def lava_cells():
    (ux, uy), (rx, ry) = LAVA_POOL['centre'], LAVA_POOL['radii']
    out = set()
    for cx in range(int(ux - rx) - 1, int(ux + rx) + 2):
        for cy in range(int(uy - ry) - 1, int(uy + ry) + 2):
            d = ((cx - ux) / rx) ** 2 + ((cy - uy) / ry) ** 2
            if d < 0.8 + 0.4 * unit(cx, cy, salt=LAVA_POOL['salt']):
                out.add((cx, cy))
    return out


# ---------------------------------------------------------------------------
# Stairs onto the walkable tiers (retail cobble step blocks, 32 deep, 8 a
# step, solid to the ground). (name, x of the first 96-wide column, columns,
# y of the top step's max corner, direction of descent in y, top, cells)
# ---------------------------------------------------------------------------
STAIRS = {
    # garden mesa (104), down north at x (9216, 9600]
    'garden': dict(x0=9216, cols=4, y_top=19711, dy=-1, top=GARDEN_Z),
    # knoll (64), down south at x (8448, 8832]
    'knoll': dict(x0=8448, cols=4, y_top=22687, dy=1, top=KNOLL_Z),
    # temple shelf (112), down north at x (18304, 18688], pad 210's line
    'temple': dict(x0=18304, cols=4, y_top=22015, dy=-1, top=TEMPLE_Z),
}


def stair_rows(s):
    """[(y max corner, top)] for each step: 8 below the tier, down to 8."""
    n = s['top'] // 8 - 1
    rows = []
    for k in range(n):
        if s['dy'] < 0:
            y = s['y_top'] - 32 * k
        else:
            y = s['y_top'] + 32 * k
        rows.append((y, s['top'] - 8 * (k + 1)))
    return rows


def stair_items(s):
    """The step blocks and side walls of one STAIRS entry; for a stair
    that descends south, a crest plate (south frame) under the tier's
    edge cells over its head, whose side is the top step's 8 riser: the
    tier's flat floor draws none, and the camera sees it."""
    from lv_vale_terrain import CREST_ROLE
    xs = [s['x0'] + 96 * (i + 1) - 1 for i in range(s['cols'])]
    rows = stair_rows(s)
    ys = [y for y, _ in rows]
    tops = [t for _, t in rows]
    items = step_stair(xs, ys, tops)
    items += stair_barriers(s['x0'] - 32, s['x0'] + 96 * s['cols'], ys, tops)
    if s['dy'] > 0:
        cy = s['y_top'] // CELL - 1
        for cx in range(s['x0'] // CELL, (s['x0'] + 96 * s['cols']) // CELL):
            items.append(MapItem.placed_item(
                cx * CELL + CELL - 1, cy * CELL + CELL - 1, s['top'] - 8,
                CREST, pick(CREST_ROLE['S'], cx, cy, salt=62)))
    return items


def stair_cells(s):
    """{cell: height} for the cells the stair covers wholly (a partly
    covered cell keeps its own floor under the blocks)."""
    rows = stair_rows(s)
    out = {}
    for cx in range(s['x0'] // CELL, (s['x0'] + 96 * s['cols']) // CELL):
        for cy in {y // CELL for y, _ in rows}:
            covered = [t for y, t in rows if y // CELL == cy]
            if len(covered) == 4:
                out[(cx, cy)] = max(covered)
    return out


# ---------------------------------------------------------------------------
# The field
# ---------------------------------------------------------------------------
def map10_field(terrain_chunks, ramp_rows, ramp_x, plateau, tracks, vignettes,
                pins):
    """The Vale's Field. `vignettes`: {shot: (region cells, world items)}."""
    f = Field(salt=10)
    cells = _cells_of_chunks(terrain_chunks)
    for y, z in ramp_rows:
        for cx in range(ramp_x[0] // CELL, ramp_x[1] // CELL):
            cells[(cx, y // CELL)] = z
    f.H.update(cells)
    f.walk |= {c for c, z in cells.items() if z >= 16}
    apply_relief(f)

    lake = lake_cells()
    land = {c for c in lake if f.H.get(c, 0) != 0}
    shore = (island_cells() | set(CAUSEWAY) | set(DECK) | set(PIER)) & lake
    for c in lake - land - shore:
        f.H[c] = 0
        f.water.add(c)
    for c in shore:
        f.H[c] = SHORE_Z
        f.shore.add(c)
        f.walk.add(c)
    # Keep bank art clear of every screenshot window.
    protected = set().union(*(region for region, _ in vignettes.values()))
    f.bank_guard = {(cx + dx, cy + dy) for cx, cy in protected
                    for dx in range(-2, 3) for dy in range(-2, 3)}
    for c in lava_cells():
        if f.H.get(c) == 0:
            f.lava.add(c)

    for s in STAIRS.values():
        for c, z in stair_cells(s).items():
            f.H[c] = z
            f.skip.add(c)
            f.noseam.add(c)
        # the tier's edge onto the stair head is open
        rows = stair_rows(s)
        y_head = rows[0][0]
        head = (y_head // CELL) + (1 if s['dy'] < 0 else -1)
        for cx in range(s['x0'] // CELL, (s['x0'] + 96 * s['cols']) // CELL):
            f.open.add(((cx, head), 'N' if s['dy'] < 0 else 'S'))

    # the shots: their cells are theirs; their tops are the heights the
    # field closes against
    for shot, (region, items) in vignettes.items():
        tops, wet = {}, set()
        for it in items:
            info = _flags(it.shape)
            if info is None or it.shape in ROOFS:
                continue
            # every cell the item's footprint reaches (the screen19 rock
            # lies on the half lattice, 128k+63)
            x0, y0 = it.x - info['xd'] + 1, it.y - info['yd'] + 1
            cells = {(cx, cy) for cx in range(x0 // CELL, it.x // CELL + 1)
                     for cy in range(y0 // CELL, it.y // CELL + 1)}
            if info['sea'] and info['zd'] <= 8:
                # water, and the waterfall's foam (435-438, 8 deep)
                wet |= cells
            if it.shape in STEP_SHAPES:
                # a shot's own stair: the field puts no seam face in or
                # against its cells (screen17's runs down the shelf face)
                f.noseam |= cells
            if info['land'] and info['xd'] >= 128 and info['yd'] >= 128:
                # a cell takes the top of a tile that covers its centre
                for c in cells:
                    mx, my = c[0] * CELL + CELL // 2, c[1] * CELL + CELL // 2
                    if x0 <= mx <= it.x and y0 <= my <= it.y:
                        tops[c] = max(tops.get(c, -1), it.z + info['zd'])
        # cells no floor of the shot covers (under its props, behind its
        # cliffs): the field fills them at its own height (shot_closure)
        f.hidden[shot] = set(region) - set(tops) - wet
        # the sides of its cells a shot already closes with a cliff face,
        # and the lowest z it faces each from: the field puts no seam face
        # against them, or only the courses under a scarp the frame cut off
        # above its foot (screen18's mesa, Field._seams)
        for it in items:
            info = _flags(it.shape)
            if it.shape not in FACE_SHAPES or info is None:
                continue
            c = (it.x // CELL, it.y // CELL)
            for side, hit in (('S', it.y % CELL == CELL - 1),
                              ('N', (it.y - info['yd'] + 1) % CELL == 0),
                              ('E', it.x % CELL == CELL - 1),
                              ('W', (it.x - info['xd'] + 1) % CELL == 0)):
                if hit:
                    f.faced[(c, side)] = min(f.faced.get((c, side), it.z),
                                             it.z)
        # a wet cell whose only land is a rock in the water (35 at its top 0)
        # is water for the rails
        f.vwater |= {c for c in wet if tops.get(c, 0) < SHORE_Z}
        design = {c: f.H.get(c, 0) for c in region}
        design_water = {c for c in region if c in f.water}
        for c in region:
            f.skip.add(c)
            f.water.discard(c)
            f.shore.discard(c)
            f.lava.discard(c)
            if c in tops:
                f.H[c] = tops[c]
            elif c in wet:
                f.H[c] = 0
            elif c not in f.H:
                f.H[c] = 0
        # A cell the shot shows no floor in (behind a gargoyle, under a
        # roof or a log pile, under a stair) takes the LOWEST height round
        # it — the shot's own floors, and the field's beyond its window: a
        # hole in a plateau stays plateau, the ground under a stair or at
        # a cliff's foot stays the ground. One that was the lake's water
        # and comes out at the water's 0 stays water (vwater: shot_closure
        # lays its tile, the shot rails close it): screen09's window edge
        # left dirt tiles standing in the lake.
        for c in sorted(f.hidden[shot]):
            near = []
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + dx, c[1] + dy)
                if n in tops:
                    near.append(tops[n])
                elif n in region:
                    near.append(design[n])
                elif n in f.H:
                    near.append(f.H[n])
            f.H[c] = min(near) if near else design[c]
            if c in design_water and f.H[c] == 0:
                f.vwater.add(c)

    # The island's jagged fringe (ISLAND jag 2) round screen02, whose
    # window is the island's middle now, left single cells of bank standing
    # alone in the lake: a shore cell with no land beside it is water.
    def landed(c):
        return any(n in f.H and n not in f.water and n not in f.vwater and
                   f.H[n] > 0 for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]),
                                        (c[0], c[1] + 1), (c[0], c[1] - 1)))
    alone = [c for c in sorted(f.shore) if not landed(c)]
    while alone:
        for c in alone:
            f.shore.discard(c)
            f.walk.discard(c)
            f.water.add(c)
            f.H[c] = 0
        alone = [c for c in sorted(f.shore) if not landed(c)]

    ground = set(f.H)
    for c, z in rim_cells(ground, nw=lambda cx, cy: cx < 70 and cy < 95,
                          flush=ground).items():
        # beside the raised ramp and plateau the rim stands a course higher
        # (the ground round it, not the rim cells already laid)
        hi = max((f.H[n] for n in ((c[0] + dx, c[1] + dy)
                                   for dx in (-1, 0, 1) for dy in (-1, 0, 1))
                  if n in ground), default=0)
        f.H[c] = max(z, RIM_HIGH if hi >= 16 else z)
    # The cloud terrace's two canyon-end anchors retain their rim support.
    # lift_props places their last wall courses on these cells; lowering
    # those anchors would move the walls into eight existing route cells.
    for c in ((50, 192), (61, 192)):
        f.H[c] = RIM_Z
    # Every exterior south and east edge closes from outside. Retain
    # the ground set for flush_edges before a skirt extends the field.
    f.flush = ground
    f.flush_side_list = flush_sides(f.flush, f.H)
    for c, s in f.flush_side_list:
        f.open.add((c, s))

    for p in pins:
        c = (p['x'] // CELL, p['y'] // CELL)
        z = f.H.get(c)
        assert c in f.skip or z is None or z <= p['z'] + 8, \
            f'pin {p["shape"]} at ({p["x"]},{p["y"]},{p["z"]}) under a cell at {z}'
    f.lift_H = dict(f.H)
    edge_skirt(f)
    return f


def edge_skirt(f, depth=16):
    """Paint 2,048 units beyond the closed boundary using chunk globs.

    North and west rock continues at its rim height. Flush edges and
    the two cloud-canyon end supports look out over z=0 water. The
    pre-skirt edge list keeps their invisible barriers in place.
    """
    import heapq
    from lv_furnish import VIEW_RX, VIEW_RY

    # One additional cell leaves room for 256-unit plate rounding.
    max_seed = 255 - (VIEW_RX//CELL + VIEW_RY//CELL)//2 - 1
    original = dict(f.H)
    best, queue = {}, []

    def offer(c, distance, wet, height):
        if c in original or not (0 <= c[0] < 256 and 0 <= c[1] < 256):
            return
        key = (distance, 0 if wet else 1, height)
        if c in best and best[c] <= key:
            return
        best[c] = key
        heapq.heappush(queue, (*key, *c))

    for c, height in sorted(original.items()):
        wet = c in f.flush or c in {(50, 192), (61, 192)}
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    offer((c[0] + dx, c[1] + dy), 1, wet, 0 if wet else height)
    while queue:
        distance, material, height, cx, cy = heapq.heappop(queue)
        if best[cx, cy] != (distance, material, height) or distance >= depth:
            continue
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    offer((cx + dx, cy + dy), distance + 1, material == 0, height)
    # Every flush edge looks out over water through its whole view wedge.
    # A nearer cliff around a concave corner must not grow a raised skirt
    # across the Avatar's view of that coast.
    coast = set()
    for (cx, cy), side in f.flush_side_list:
        if side == 'S':
            coast.update((cx+dx, cy+dy) for dx in range(-depth, depth+1)
                         for dy in range(1, depth+1))
        else:
            coast.update((cx+dx, cy+dy) for dx in range(1, depth+1)
                         for dy in range(-depth, depth+1))
    f.skirt = set(best)
    for c, (_, material, height) in best.items():
        # The south skirt reaches the signed map-coordinate limit. Water
        # beyond this line paints the corner without seeding a void-floor
        # ring outside the serializable 0..32767 world.
        if c in coast or c[1] > max_seed:
            material, height = 0, 0
        f.H[c] = height
        if material == 0:
            f.water.add(c)


_SF = None


def _flags(shape):
    global _SF
    if _SF is None:
        from vignette_paint import Painter
        _SF = Painter.built()
    if shape >= 2048:
        return None
    b = _SF._tf[shape * 8:shape * 8 + 8]
    return dict(land=bool(b[0] & 8), sea=bool(b[0] & 4), solid=bool(b[0] & 2),
                xd=(b[2] >> 4) * 32, yd=(b[3] & 0xF) * 32, zd=(b[3] >> 4) * 8)


def paint_earth(f, tracks, vignettes, salt=40):
    """The material lattice: village basins, track bands, the garden
    mesa's top, scattered sheets in the scrub; then the shots' own edge
    tiles, so the transitions run into each shot's ground."""
    # Outwash gathers at the broken court, dry crossing, killing ground,
    # and ruin feet. Unequal lobes leave each region's rock field visible.
    washes = [
        (11390, 3480, 680), (14830, 2230, 780), (11680, 1360, 430),
        (10880, 7020, 1300), (11580, 8670, 1000), (15510, 9970, 1250),
        (9040, 5010, 650), (16480, 6500, 530),
        (12480, 13380, 790), (13560, 11900, 520),
        (7370, 17200, 1040), (4660, 16240, 600),
        (19320, 17750, 1000), (21900, 16180, 480),
        (6130, 23100, 970), (8050, 23900, 590),
        (11720, 21830, 670), (13720, 23900, 610),
        (16680, 22460, 1040), (19820, 21180, 640),
        (12780, 27480, 800),
        (6040, 12280, 900), (8460, 14100, 1600),
        (17680, 12680, 1450), (20330, 14300, 1450),
        (9900, 17200, 730), (16980, 19050, 590),
        (15140, 23100, 1450), (10700, 20700, 510),
        # Dry fans below the northern scars and the two village drainages.
        (7400, 2500, 1300), (18100, 2600, 1450),
        (6040, 13600, 1250), (3600, 14300, 700),
        (16600, 15000, 1250), (15200, 19500, 1100), (8000, 19100, 1000),
    ]
    discs = list(EARTH_DISCS) + scrub_sheets() + washes
    earth_corners(f, discs, tracks, salt=salt)
    f.smooth()
    for shot, (region, items) in vignettes.items():
        seed_from_vignette(f, items)


# Village basins (dirt-majority, screens 19/20/22) and the garden mesa.
EARTH_DISCS = [
    (5600, 7700, 1700), (5100, 9700, 1500), (6900, 9000, 1200),     # Hoskuld
    (18300, 8500, 1500), (19900, 7500, 1600), (21200, 9000, 1400),  # Gunnar
    (19800, 9900, 1300), (21300, 6600, 1100),
    (9900, 19300, 700),                                             # garden
    (8800, 21500, 500),                                             # knoll
]


def scrub_sheets(n=12, salt=77):
    out = []
    k = 0
    lake = lake_cells()
    while len(out) < n and k < 400:
        x = int(4000 + unit(k, 1, salt=salt) * 17000)
        y = int(2500 + unit(k, 2, salt=salt) * 20000)
        r = int(600 + unit(k, 3, salt=salt) * 600)
        k += 1
        if (x // CELL, y // CELL) in lake:
            continue
        out.append((x, y, r))
    return out


def rails(f, shots=False):
    """One course of invisible wall (497/498) in a water cell's strip
    against every walkable land cell beside it, at that land's height:
    a blow's stumble (64 units) or a step never takes a body onto the
    water (test_monster_eggs F3/F4; build_map_10 build_the_lake's rails,
    now generated from the cells). `shots`: the shots' own water cells
    (f.vwater) instead of the field's — their rails lie in the shots'
    regions, which the stamp clears, so they are laid after it."""
    out = []
    water = f.water | f.vwater
    for c in sorted(f.vwater if shots else f.water):
        cx, cy = c
        X, Y = cx * CELL + CELL - 1, cy * CELL + CELL - 1
        for s, (dx, dy) in (('N', (0, -1)), ('S', (0, 1)), ('W', (-1, 0)), ('E', (1, 0))):
            n = (cx + dx, cy + dy)
            if n in water or n in f.lava or n not in f.H:
                continue
            z = f.H[n]
            if z > 8:
                continue          # a cliff face closes it
            if s == 'N':
                out.append(MapItem.placed_item(X, Y - CELL + 32, z, 497, 0))
            elif s == 'S':
                out.append(MapItem.placed_item(X, Y, z, 497, 0))
            elif s == 'W':
                out.append(MapItem.placed_item(X - CELL + 32, Y, z, 498, 0))
            else:
                out.append(MapItem.placed_item(X, Y, z, 498, 0))
    return out


def coast_banks(f):
    """Shore pieces beyond the flush z=0 boundaries' invisible walls."""
    banks = {}
    for c, side in f.flush_side_list:
        if f.H[c] > 8:
            continue
        dx, dy = (0, 1) if side == 'S' else (1, 0)
        n = c[0]+dx, c[1]+dy
        if n not in f.water or n in f.bank_guard:
            continue
        # The signed cliff coast uses stone lips, with occasional bank stones.
        shape = 128 if unit(*c, salt=4010) < .08 else 125
        frame = pick((4, 8, 14, 15), *c, salt=4011) if shape == 128 else pick(
            CREST_ROLE[side], *c, salt=4012)
        banks.setdefault(n, (shape, frame))
    return [MapItem.placed_item(cx*CELL+CELL-1, cy*CELL+CELL-1, 0,
                                shape, frame)
            for (cx, cy), (shape, frame) in sorted(banks.items())]


def lake_banks(f):
    """Rock banks on the outer lake perimeter, behind the rails.

    The art contract reserves 126 for retained shots; generated banks use 128.

    The original island, causeway, pier, and screenshot cells keep their
    shore art. Upper invisible courses protect the new bank tops from a
    jump over the existing one-course lake rails.
    """
    out = []
    wet = f.water | f.vwater
    frames = {'N': 3, 'W': 2, 'E': 9, 'S': 10}
    x0, y0, x1, y1 = (v // CELL for v in LAKE)
    for c in sorted(f.water & lake_cells()):
        cx, cy = c
        if c in f.bank_guard or min(cx-x0, x1-1-cx, cy-y0, y1-1-cy) > 2:
            continue
        dry = [(side, (cx+dx, cy+dy)) for side, (dx, dy) in
               (('N', (0, -1)), ('W', (-1, 0)), ('E', (1, 0)), ('S', (0, 1)))
               if (cx+dx, cy+dy) in f.H and (cx+dx, cy+dy) not in wet
               and f.H[cx+dx, cy+dy] <= 8]
        if not dry:
            continue
        X, Y = cx * CELL + CELL - 1, cy * CELL + CELL - 1
        # Collision stays 128 by 128 by eight; the continuous blue bank art
        # gives way to the same crest vocabulary as the outer Vale shore.
        side = dry[0][0]
        shape = 128 if unit(*c, salt=4020) < .16 else 125
        role = {'N': 'S', 'W': 'E', 'E': 'W', 'S': 'N'}[side]
        frame = pick((4, 8, 14, 15), *c, salt=4021) if shape == 128 else pick(
            CREST_ROLE[role], *c, salt=4022)
        out.append(MapItem.placed_item(X, Y, 0, shape, frame))
        for side, n in dry:
            x = X-CELL+STRIP if side == 'W' else X
            y = Y-CELL+STRIP if side == 'N' else Y
            bar = BAR_X if side in 'NS' else BAR_Y
            out.append(MapItem.placed_item(x, y, f.H[n]+COURSE, bar, 0))
    return out


def shot_closure(f):
    """Ground for the cells each shot shows no floor in, at the heights
    map10_field gave them (the lowest ground round each), so a plateau
    behind a gargoyle or a yard under a roof is whole; and the faces the
    shots' higher cells turn to it and to the rest of the field. Emitted
    after the stamp (the hidden cells are the shot's, skipped by
    Field.emit; the faces stand in the shot's cells)."""
    cells = set()
    for shot_cells in f.hidden.values():
        cells |= shot_cells
    cells = sorted(cells)
    return f.emit(cells=cells, force=True) + f.seam_faces() + \
        f.seam_faces(cells=cells, force=True)


def under_floors(f, vignettes, items):
    """A floor under each shot cell that no floor covers on the 128 grid.

    The village shots lay their plateau crests on the half lattice
    (128k + 63), so a crest covers a quarter of four cells, and the cells
    between a hut and the plateau's face hold only faces. The void floor
    (lv_furnish.void_floor) counts a cell covered only by a tile on its
    own grid, and its 256-unit black plate at z 0 then draws over the
    shot's own z 0 yard tiles in the same block (two flats at one z have
    no defined order). So each such cell gets a floor of its own at the
    meets it, so whatever the shot shows there draws over it.

    A tile that covers its cell but paints under three quarters of it
    (screen21's 781:0, a crater over the knoll; 466:1) is no floor: its
    cell gets one at the tile's own z, under it, as it would in retail."""
    from lv_furnish import floor_cells
    from map_preview import GlobReader, expand_globs
    from parse_typeflag import load_typeflag
    shapes = load_typeflag(os.path.join(HERE, '..', '..', '..', 'shared',
                                        'build', 'TYPEFLAG.DAT'))
    cover = floor_cells([it for it in expand_globs(items, GlobReader())
                         if not _holed(it.shape, it.frame)], shapes,
                        eggs_as_chunks=False, painted=True)
    out = []
    for shot in sorted(vignettes):
        region, vitems = vignettes[shot]
        flats = []
        for it in vitems:
            info = _flags(it.shape)
            if info and (info['land'] or info['sea']) and info['zd'] <= 8:
                flats.append((it.x - info['xd'] + 1, it.y - info['yd'] + 1,
                              it.x, it.y, it.z))
        for c in sorted(region):
            X, Y = c[0] * CELL + CELL - 1, c[1] * CELL + CELL - 1
            if (X, Y) in cover:
                continue
            holed = [it.z for it in vitems if (it.x, it.y) == (X, Y) and
                     _holed(it.shape, it.frame)]
            z = min(holed) if holed else min(
                [f.H.get(c, 0)] +
                [f.H[n] for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]),
                                  (c[0], c[1] + 1), (c[0], c[1] - 1))
                 if n in f.H] +
                [fz - 8 for x0, y0, x1, y1, fz in flats
                 if x0 <= X and x1 >= X - CELL + 1 and
                 y0 <= Y and y1 >= Y - CELL + 1])
            out.append(f.floor_item(c, max(z, 0)))
            cover.add((X, Y))
    return out


_HOLED = {}


def _holed(shape, frame):
    """A cell-wide LAND or SEA flat whose frame paints under three
    quarters of the 1,024 pixels a full 128x128 floor tile does."""
    if (shape, frame) not in _HOLED:
        info = _flags(shape)
        holed = False
        if info and (info['land'] or info['sea']) and info['zd'] <= 8 and \
                info['xd'] == CELL and info['yd'] == CELL:
            from vignette_paint import Painter
            out, _ = Painter().paint(
                [dict(shape=shape, frame=frame, x=1024, y=1024, z=0)],
                -150, 100, 300, 300)
            holed = int((out >= 0).sum()) < 768
        _HOLED[(shape, frame)] = holed
    return _HOLED[(shape, frame)]


def shot_supports(f, vignettes, items, map_num=10):
    """A floor a course under each shot container the 1994 frame sets
    into its floor, where map_validate looks for one (the tile whose max
    corner lies within 64 of the item's): screen17's body 405 lies at
    z 111 on the 112 shelf, so nothing at or under its z holds it up."""
    from map_validate import validate_placement
    shot = {(it.shape, it.x, it.y, it.z)
            for _, vits in vignettes.values() for it in vits}
    out = []
    for iss in validate_placement(items, map_num):
        if 'no floor support' not in iss['msg'] or \
                (iss['shape'], iss['x'], iss['y'], iss['z']) not in shot:
            continue
        c = ((iss['x'] - 63) // CELL, (iss['y'] - 63) // CELL)
        out.append(f.floor_item(c, max(iss['z'] // 8 * 8 - 8, 0)))
    return out


def stair_underfill(items, vignettes):
    """Step blocks under every shot step block that floats: the 1994
    frames draw a stair's blocks only as deep as the camera sees them
    (screen17's runs down from the shelf as 48-deep blocks stepping 8, so
    under its lower steps is air to the pit floor), and outside the frame
    that air is a hole through the stair's side. Each gets retail's step
    blocks (frame 1, `_stack`) from the highest top under its footprint up
    to its own bottom, solid as step_stair's steps are."""
    from map_preview import GlobReader, expand_globs
    boxes = []
    for it in expand_globs(items, GlobReader()):
        info = _flags(it.shape)
        if it.x >= 64 and info and it.shape not in (BAR_X, BAR_Y) and \
                (info['solid'] or info['land']):
            boxes.append((it.x - info['xd'], it.x, it.y - info['yd'], it.y,
                          it.z + info['zd']))
    out = []
    for shot in sorted(vignettes):
        for it in vignettes[shot][1]:
            if it.shape not in STEP_SHAPES or it.z == 0:
                continue
            info = _flags(it.shape)
            x0, y0 = it.x - info['xd'], it.y - info['yd']
            below = max([top for a, b, c, d, top in boxes
                         if a < it.x and x0 < b and c < it.y and y0 < d and
                         top <= it.z], default=0)
            if (it.z - below) % 8:
                continue
            z = below
            for part in _stack(it.z - below):
                out.append(MapItem.placed_item(it.x, it.y, z, STEP_X[part],
                                               STEP_FRAME))
                z += part
    return out


def shot_rails(f, vignettes):
    """Invisible wall along every drop out of a shot that would hurt or
    kill (FALL_HURTS, 80). The 1994 frames close their scarps with a crest
    and nothing else (screen18's garden mesa, screen17's shelf over the
    pit), and the field's own barriers stop at a shot's cells. Each shot
    crest (125, often on the half lattice) and each shot cell the shot
    floors is an edge source at its top; a side whose ground beyond (the
    field's height there) lies FALL_HURTS or more below gets two courses
    in the source's strip on that side, as Field lays on its own walkable
    tiers. A shot's own stair cells are never fenced off. They paint
    nothing."""
    sources = []
    for shot in sorted(vignettes):
        region, vitems = vignettes[shot]
        for it in vitems:
            if it.shape == CREST:
                sources.append((it.x - CELL + 1, it.y - CELL + 1, it.x, it.y,
                                it.z + 8))
        for c in sorted(set(region) - f.hidden.get(shot, set()) - f.noseam):
            if c in f.H:
                sources.append((c[0] * CELL, c[1] * CELL, c[0] * CELL + CELL - 1,
                                c[1] * CELL + CELL - 1, f.H[c]))
    out, seen = [], set()
    for x0, y0, x1, y1, top in sources:
        for s, (px, py) in (('S', (x1 - CELL // 2, y1 + 1)),
                            ('N', (x1 - CELL // 2, y0 - 1)),
                            ('E', (x1 + 1, y1 - CELL // 2)),
                            ('W', (x0 - 1, y1 - CELL // 2))):
            beyond = (px // CELL, py // CELL)
            if beyond in f.noseam or top - f.H.get(beyond, 0) < FALL_HURTS:
                continue
            if s in 'NS':
                x, y, bar = x1, (y1 if s == 'S' else y0 + STRIP - 1), BAR_X
            else:
                x, y, bar = (x1 if s == 'E' else x0 + STRIP - 1), y1, BAR_Y
            for z in (top, top + COURSE):
                if (x, y, z, bar) not in seen:
                    seen.add((x, y, z, bar))
                    out.append(MapItem.placed_item(x, y, z, bar, 0))
    return out


def shot_frames(vignettes):
    """Each shot's frame on screen, (sx0, sy0, sx1, sy1) in the painter's
    world screen coordinates (screen_x = x/4 - y/4, screen_y = x/8 + y/8
    - z), from its camera, as vignette_built_window places it."""
    import shot_decompose as SD
    import vignette_place as V
    out = []
    for shot in sorted(vignettes):
        v = V.load(shot)
        ox, oy, oz = V.origin(v)
        cam = v['camera']
        csx = cam['sx0'] + (ox // 4 - oy // 4)
        csy = cam['sy0'] + (ox // 8 + oy // 8 - oz)
        _, (h, w), _ = SD.load_shot(shot)
        out.append((csx, csy, csx + w, csy + h))
    return out


def band_plates(items, vignettes):
    """An 8-deep crest plate under every floor that stands 8 (up to 15)
    over the floor south or east of it with nothing drawing the step
    between them. The camera sees a tier's south and east sides; a flat
    tile has none, so a step of a course or less between flat floors (a
    shot's z 8 rim over the field's water or ground beyond its frame, a
    tile one course down in a shot's floor) leaves a band the engine
    never paints, where it shows the last frame. Deeper drops are the
    faces' (Field._faces, `foot`). Floors are the LAND or SEA tiles at
    least a cell wide covering a cell's centre (roofs aside); a step is
    drawn when some solid or land box at least 8 deep spans it on that
    boundary. The plate lies inside the higher cell, under its floor, its
    frame picked by the sides it draws (visible_role). None goes where its
    sprite would reach into a shot's frame: inside it the 1994 frame is
    the reference, and what it shows there is the shot's."""
    from map_preview import GlobReader, expand_globs
    from exact_reach import FLG_FLIPPED
    from lv_vale_terrain import CREST_ROLE, visible_role
    tops, edges = {}, {}
    for it in expand_globs(items, GlobReader()):
        info = _flags(it.shape)
        if it.x < 64 or info is None or it.shape in ROOFS or \
                it.shape in (BAR_X, BAR_Y):
            continue
        xd, yd = info['xd'], info['yd']
        if it.flags & FLG_FLIPPED:
            xd, yd = yd, xd
        x0, y0, z1 = it.x - xd + 1, it.y - yd + 1, it.z + info['zd']
        if (info['land'] or info['sea']) and xd >= CELL and yd >= CELL:
            for cx in range(x0 // CELL, it.x // CELL + 1):
                for cy in range(y0 // CELL, it.y // CELL + 1):
                    mx, my = cx * CELL + CELL // 2, cy * CELL + CELL // 2
                    if x0 <= mx <= it.x and y0 <= my <= it.y:
                        tops[(cx, cy)] = max(tops.get((cx, cy), -1), z1)
        if info['zd'] >= 8 and (info['solid'] or info['land']):
            edges.setdefault(('S', it.y), []).append(
                (x0, it.x, it.z, z1, it.shape, it.frame))
            edges.setdefault(('E', it.x), []).append(
                (y0, it.y, it.z, z1, it.shape, it.frame))
    frames = shot_frames(vignettes)
    out = []
    for c in sorted(tops):
        tc = tops[c]
        X, Y = c[0] * CELL + CELL - 1, c[1] * CELL + CELL - 1
        sides = ''
        for s, n, key, lo in (('S', (c[0], c[1] + 1), ('S', Y), X - CELL + 1),
                              ('E', (c[0] + 1, c[1]), ('E', X), Y - CELL + 1)):
            tn = tops.get(n)
            if tn is None or not 0 < tc - tn < 16:
                continue
            if not any(a <= lo + CELL - 1 and b >= lo and za <= tn and
                       zb >= tc and _draws(sh, fr, s)
                       for a, b, za, zb, sh, fr in edges.get(key, ())):
                sides += s
        # a box of the shot's own already fills the plate's place (a crest
        # whose frame draws no side): nothing to add under it
        taken = any(a == X - CELL + 1 and b == X and za == tc - 8
                    for a, b, za, zb, sh, fr in edges.get(('S', Y), ()))
        sx, sy = X // 4 - Y // 4, X // 8 + Y // 8 - (tc - 8)
        if sides and not taken and not any(
                sx - 40 < x1 and x0 < sx + 40 and sy - 48 < y1 and y0 < sy + 8
                for x0, y0, x1, y1 in frames):
            out.append(MapItem.placed_item(
                X, Y, tc - 8, CREST,
                pick(CREST_ROLE[visible_role(sides)], c[0], c[1], salt=61)))
    return out


_DRAWS = {}


def _draws(shape, frame, side):
    """Does the frame paint its box's south (or east) side? Measured on
    the painter: at least 4 in 5 of the points on that side, its whole
    depth, are painted (125's role frames draw some sides and not others;
    a face draws the side it faces)."""
    if (shape, frame) not in _DRAWS:
        from vignette_paint import Painter
        info = _flags(shape)
        X = Y = 1024
        out, _ = Painter().paint([dict(shape=shape, frame=frame, x=X, y=Y,
                                       z=0)], -300, 0, 600, 600)
        got = {}
        for s, run in (('S', info['xd']), ('E', info['yd'])):
            pts = [(X - t, Y, z) if s == 'S' else (X, Y - t, z)
                   for t in range(4, run - 3, 8)
                   for z in range(1, info['zd'])]
            hit = sum(out[x // 8 + y // 8 - z, x // 4 - y // 4 + 300] >= 0
                      for x, y, z in pts)
            got[s] = bool(pts) and hit >= 0.8 * len(pts)
        _DRAWS[(shape, frame)] = got
    return _DRAWS[(shape, frame)][side]

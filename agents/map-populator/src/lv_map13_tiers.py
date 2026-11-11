"""
lv_map13_tiers.py — Map 13's terrain as a field of 128-unit cells, built in
the 1994 shots' own idiom (docs/research/2026-10-16-screenshot-reconstruction.md,
phase B).

The four Map 13 shots (screen01, 14, 15, 16) show one material and one
grammar, and retail's cave maps (37, 14, 16, 20, 28, 31, 62 …) use the same:

  * floors are 301 frames 0-6, one tile per 128 cell on the 127-mod-128
    lattice (the glob grid every retail floor sits on);
  * a raised cell whose neighbour is lower is a RIM: its top is a 125 crest
    at floor - 8 (top flush with the floor), chosen BY ROLE from the sides
    that drop — retail map 37 etc. measured 2026-10-16:
        S 3/4   E 1/2   N 9/10   W 7/8   SE 0   SW 5   NE 6   NW 11
    (125 f12-14 are the interior crests, f15-22 lumps);
  * under the crest, on each side that drops, courses of 26 (an east-west
    face, 128 x 32) or 32 (a north-south face, 32 x 128) stacked 48 apart
    INSIDE the crest's own cell, in its edge strip — retail places 26 at the
    crest's (x, y) for a south face and at y - 96 for a north face, 32 at x
    for an east face and at x - 96 for a west face (2,000+ placements). The
    bottom course may sink below the lower floor; that floor, drawn in
    front, hides it, as screen16's face sinks under its water;
  * faces the camera sees (south, east) take the drawn frames (26/32 f0-6);
    faces it never sees (north, west) take the black ones (26/32 f7/8),
    exactly retail's split — except beside a shot or a void, where the
    camera does see behind a cell (exposed(); 2026-10-17), and outside the
    windows there they are drawn too;
  * an east or west face that meets a south or north face at the cell's
    corner is shortened (31 = 96 long, 30 = 64) so no two pieces overlap:
    overlapping solid boxes are what close paint-sort cycles.

A Field maps (cx, cy) -> Cell. Cell index k covers world (128k - 1, 128k +
127], so its tile's max corner is 128k + 127 (corner(k)).

Kinds:
  ROCK   a floor at z (raised or not); rims and faces where it drops;
  WATER  347 at z (SI_SEA: never walkable);
  CLOUD  the cloud sea at CLOUD_Z — the 1994 cloud floor (art_registry 2000,
         built as shape 874), laid one unit below the plane because its
         hotspot sits a pixel lower than the 1994 frame's;
  VOID   nothing: the drop below the shot's black;
  LOCK   a vignette cell — nothing is emitted, the vignette owns it; its
         level (for the neighbours' faces) is what the shot shows there;
  HIDDEN a vignette cell the shot shows no ground in: a floor tile in a
         protected window, or a crest outside the windows.
Every random choice is a hash of the cell and a salt (deterministic).
"""

from u8_map import MapItem

CELL = 128
COURSE = 48

ROCK, WATER, CLOUD, VOID, LOCK = 'rock', 'water', 'cloud', 'void', 'lock'
HIDDEN = 'hidden'

SHAPE_FLOOR = 301
FLOOR_FRAMES = (0, 1, 2, 3, 4, 5, 6)
SHAPE_CREST = 125
SHAPE_FACE_X = 26          # 128 x 32: a south or north face
SHAPE_FACE_Y = 32          # 32 x 128: an east or west face
SHAPE_FACE_Y96 = 31        # 32 x 96
SHAPE_FACE_Y64 = 30        # 32 x 64
SHAPE_POST = 29           # 32 x 32: the convex corner of two seen faces
POST_SEEN = (0, 1, 2, 4, 5)
SHAPE_WATER = 347
WATER_FRAME = 16           # the plain navy the lake shots are made of
SHAPE_CLOUD = 874          # the 1994 cloud floor (art_registry 2000), 5 flat frames
CLOUD_FRAMES = (0, 1, 2)   # the three whole drawings; 3 and 4 mirror 0 and 2
CLOUD_Z = 57               # the 1994 cloud plane (screen01: local 1 + 56)
CLOUD_DZ = 1               # 874's hotspot sits one pixel lower than the 1994
                           # frame's (phaseC-art.md, the z=0 encoding), so it
                           # draws the plane from one unit below it

# Frames by role. Visible = the camera's side (south, east).
FACE_X_SEEN = (0, 1, 2, 3, 4, 5, 6)
FACE_X_HIDDEN = (7, 8)
FACE_Y_SEEN = (0, 1, 2, 3, 4, 5, 6)
FACE_Y_HIDDEN = (7, 8)
FACE_Y96_SEEN = (0, 1, 4)
FACE_Y96_HIDDEN = (2, 3)
FACE_Y64_SEEN = (0, 1, 4)
FACE_Y64_HIDDEN = (2, 3)

# 125 by the set of sides that drop (retail measurement, module doc).
CREST_BY_DROP = {
    frozenset('S'): (3, 4), frozenset('E'): (1, 2),
    frozenset('N'): (9, 10), frozenset('W'): (7, 8),
    frozenset('SE'): (0,), frozenset('SW'): (5,),
    frozenset('NE'): (6,), frozenset('NW'): (11,),
    frozenset('NS'): (3, 4), frozenset('EW'): (1, 2),
    frozenset('NSE'): (0,), frozenset('SEW'): (0,),
    frozenset('NSW'): (5,), frozenset('NEW'): (6,),
    frozenset('NSEW'): (16,),
}
CREST_INTERIOR = (12, 13, 14)

SIDES = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}


def corner(k):
    """Max corner of cell k on the 127-mod-128 lattice."""
    return k * CELL + CELL - 1


def cell_of(v):
    """The cell whose (128k - 1, 128k + 127] holds coordinate v."""
    return v // CELL


def hsh(cx, cy, salt=0):
    """A deterministic 32-bit hash of a cell and a salt."""
    h = (cx * 73856093) ^ (cy * 19349663) ^ (salt * 83492791)
    h = (h ^ (h >> 13)) * 0x5BD1E995 & 0xFFFFFFFF
    return h ^ (h >> 15)


def pick(seq, cx, cy, salt=0):
    return seq[hsh(cx, cy, salt) % len(seq)]


class Cell:
    __slots__ = ('kind', 'z', 'edge', 'floor')

    def __init__(self, kind, z=0, edge=None, floor=None):
        self.kind = kind
        self.z = z
        # LOCK only: per side, the level the vignette's cell presents to a
        # neighbour on that side (None = the cell's own level).
        self.edge = edge or {}
        # ROCK / HIDDEN: (shape, frames) of its floor tile, None for 301
        # (a shot of another ground carried out past its frame: screen13's
        # earth, build_map_13.SHOT_FLOORS). Rims keep the 125 crest.
        self.floor = floor

    def level(self, side=None):
        """The floor height a neighbour's face must come down to."""
        if self.kind == VOID:
            return 0
        if self.kind == CLOUD:
            return CLOUD_Z
        if self.kind == LOCK and side is not None and side in self.edge:
            return self.edge[side]
        return self.z

    def __repr__(self):
        return f'{self.kind}{self.z}'


OPPOSITE = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}


def neighbour_level(field, cx, cy, side, outside=0):
    dx, dy = SIDES[side]
    nb = field.get((cx + dx, cy + dy))
    if nb is None:
        return outside
    return nb.level(OPPOSITE[side])


def courses_down(top, floor):
    """What stands under a crest whose base is `top`, down to a neighbour's
    `floor`: (kind, base z) pairs, kind 'course' (48 tall, stacked down
    from the crest; the lowest may sink below the floor) or 'lip' (a 125
    crest, 8 tall) where less than a course is left above z 0, so no piece
    goes below z 0. A stack whose last lip would leave a gap of less than
    8 over z 0 ends in a lip at z 0 that overlaps the one above it: the
    4-unit gap showed as a black seam along the lower leg's east lane
    (verifier 2026-10-17 finding 3)."""
    out = []
    z = top
    while z > floor:
        if z - COURSE >= 0:
            z -= COURSE
            out.append(('course', z))
        elif z - 8 >= 0:
            z -= 8
            out.append(('lip', z))
        else:
            out.append(('lip', 0))
            break
    return out


# Pieces by strip length: (shape, seen frames, hidden frames).
X_PIECES = {128: (26, FACE_X_SEEN, FACE_X_HIDDEN), 96: (27, (0, 1, 4), (2, 3)),
            64: (28, (0, 1, 4), (2, 3))}
Y_PIECES = {128: (SHAPE_FACE_Y, FACE_Y_SEEN, FACE_Y_HIDDEN),
            96: (SHAPE_FACE_Y96, FACE_Y96_SEEN, FACE_Y96_HIDDEN),
            64: (SHAPE_FACE_Y64, FACE_Y64_SEEN, FACE_Y64_HIDDEN)}


def face_items(cx, cy, top, drops, crest_fr=0, bare=False, window=None):
    """Faces under a rim whose crest's base is `top`, on each side in
    `drops` ({side: lower floor}), inside the cell's edge strips. Each
    paired corner square gets a 29 post outside protected windows; both
    adjoining strips are shortened (27/28 along x, 31/30 along y) so no
    boxes overlap. Protected windows retain their original ownership:
    south takes both south corners, east the north-east, north the
    north-west. Generated back faces outside windows carry rock texture.
    Where less than a course is left above z 0 the cell is closed
    by lips (125, 8 tall) under its crest. North and west faces retain
    the hidden frames inside a protected window. `bare` remains accepted
    for existing callers; all generated back faces outside windows are drawn."""
    import random
    X, Y = corner(cx), corner(cy)

    def frame(frames, salt):
        if window and window(X, Y, max(0, top - 48), CELL, CELL, 96):
            return pick(frames, cx, cy, salt)
        return random.Random(f'm13:face:{cx}:{cy}:{top}:{salt}:{frames}').choice(frames)

    out = []
    lips = set()
    at = {}                                   # course base -> sides there
    for side, floor in drops.items():
        for kind, z in courses_down(top, floor):
            if kind == 'lip':
                lips.add(z)
            else:
                at.setdefault(z, set()).add(side)
    for z in sorted(at):
        here = at[z]
        salt = 11 + z // COURSE
        # Close each paired corner with its own post. The two adjoining
        # strips stop before that square, preserving their collision union.
        corners = {(a, b) for a in 'NS' for b in 'EW'
                   if a in here and b in here}
        changed = []
        if ('N', 'E') in corners:
            changed.append((X, Y, z, 32, CELL, COURSE))
        if ('S', 'W') in corners:
            changed.append((X, Y, z, CELL, 32, COURSE))
        if ('N', 'W') in corners:
            changed.append((X, Y - 96, z, CELL, 32, COURSE))
        guarded = window and any(window(*box) for box in changed)
        if not guarded:
            for a, b in sorted(corners):
                out.append(MapItem.placed_item(
                    X - 96 * (b == 'W'), Y - 96 * (a == 'N'), z,
                    SHAPE_POST, frame(POST_SEEN, salt)))
            for side in sorted(here):
                if side in 'NS':
                    length = CELL - 32 * sum(b in here for b in 'EW')
                    x, y = X - 32 * ('E' in here), Y - 96 * (side == 'N')
                    shape, fs, fh = X_PIECES[length]
                else:
                    length = CELL - 32 * sum(a in here for a in 'NS')
                    x, y = X - 96 * (side == 'W'), Y - 32 * ('S' in here)
                    shape, fs, fh = Y_PIECES[length]
                xd, yd = (length, 32) if side in 'NS' else (32, length)
                drawn = side in 'SE' or (not (window and window(
                    x, y, z, xd, yd, COURSE)))
                out.append(MapItem.placed_item(
                    x, y, z, shape, frame(fs if drawn else fh, salt)))
            continue
        for side in sorted(here):
            seen = side in 'SE'
            if side in 'SN':
                if side == 'S':
                    # The south-east corner of two seen faces is a 29 post
                    # (retail's convex corner: neither 26 nor 32 draws its
                    # end), the south face one piece shorter.
                    post = 'E' in here
                    x1, length, y = X - 32 * post, 128 - 32 * post, Y
                    if post:
                        out.append(MapItem.placed_item(
                            X, Y, z, SHAPE_POST, frame(POST_SEEN, salt)))
                else:
                    x1 = X - 32 * ('E' in here)
                    length, y = 128 - 32 * ('E' in here), Y - 96
                shape, fs, fh = X_PIECES[length]
                drawn = seen or (not (window and window(
                    x1, y, z, length, 32, COURSE)))
                out.append(MapItem.placed_item(
                    x1, y, z, shape, frame(fs if drawn else fh, salt)))
            else:
                y1 = Y - 32 * ('S' in here)
                length = 128 - 32 * ('S' in here)
                if side == 'W':
                    length -= 32 * ('N' in here)
                x = X if side == 'E' else X - 96
                shape, fs, fh = Y_PIECES[length]
                drawn = seen or (not (window and window(
                    x, y1, z, 32, length, COURSE)))
                out.append(MapItem.placed_item(
                    x, y1, z, shape, frame(fs if drawn else fh, salt)))
    for z in sorted(lips):
        out.append(MapItem.placed_item(X, Y, z, SHAPE_CREST, crest_fr))
    return out


def crest_frame(cx, cy, drop_sides):
    key = frozenset(drop_sides)
    return pick(CREST_BY_DROP.get(key, CREST_INTERIOR), cx, cy, 3)


def drops_of(field, cx, cy, outside=0, smooth=frozenset()):
    """{side: lower level} for every side of ROCK cell (cx, cy) whose
    neighbour is below its floor, except a 4- or 8-unit riser between two
    cells of `smooth` (the climb's own steps); and the set of sides that
    are such risers."""
    c = field[(cx, cy)]
    drops, risers = {}, set()
    for side, (dx, dy) in SIDES.items():
        lv = neighbour_level(field, cx, cy, side, outside)
        if lv >= c.z:
            continue
        if (cx, cy) in smooth and (cx + dx, cy + dy) in smooth \
                and c.z - lv <= 8:
            risers.add(side)
            continue
        drops[side] = lv
    return drops, risers


def emit(field, outside=0, smooth=frozenset(), globbed=frozenset(),
         floor_frames=FLOOR_FRAMES, window=None):
    """Items for every ROCK / WATER / CLOUD cell of the field. A ROCK cell
    is a rim (crest + faces) wherever a neighbour's level is below its
    floor — even 8 lower, or the step shows as a slit of void. Between two
    cells of `smooth` (the climb) a 4- or 8-unit riser keeps the floor
    tile and gets a crest under it, by the riser's sides (crest_frame),
    whose side fills the step: the interior frame 14 draws no side, and
    its risers showed as black slits.
    A cell in `globbed` has its floor from a glob egg: only its faces
    here. `outside` is the level beyond the field (void = 0). `window`:
    face_items'."""
    out = []
    bare = exposed(field)

    def floor(c, cx, cy):
        if c.z >= 8 and not c.floor and not (window and window(
                corner(cx), corner(cy), c.z - 8, CELL, CELL, 8)):
            drops, risers = drops_of(field, cx, cy, outside, smooth)
            return MapItem.placed_item(
                corner(cx), corner(cy), c.z - 8, SHAPE_CREST,
                crest_frame(cx, cy, set(drops) | risers))
        shape, frames = c.floor or (SHAPE_FLOOR, floor_frames)
        return MapItem.placed_item(corner(cx), corner(cy), c.z, shape,
                                   pick(frames, cx, cy, 1))
    for (cx, cy), c in sorted(field.items()):
        X, Y = corner(cx), corner(cy)
        if c.kind == WATER:
            out.append(MapItem.placed_item(X, Y, c.z, SHAPE_WATER, WATER_FRAME))
            continue
        if c.kind == CLOUD:
            out.append(MapItem.placed_item(
                X, Y, CLOUD_Z - CLOUD_DZ, SHAPE_CLOUD,
                pick(CLOUD_FRAMES, cx, cy, 2)))
            continue
        if c.kind == HIDDEN:
            out.append(floor(c, cx, cy))
            continue
        if c.kind != ROCK:
            continue
        drops, risers = drops_of(field, cx, cy, outside, smooth)
        top = c.z - 8
        if (cx, cy) in globbed:
            out.extend(face_items(cx, cy, top, drops, bare=(cx, cy) in bare,
                                  window=window))
            continue
        if not drops or top < 0:
            # A floor under 8 has no room for a crest (z < 0 wraps in
            # FIXED.DAT): the tile alone, its low side open.
            out.append(floor(c, cx, cy))
            if risers and top >= 0 and out[-1].shape != SHAPE_CREST:
                out.append(MapItem.placed_item(
                    X, Y, top, SHAPE_CREST, crest_frame(cx, cy, risers)))
            continue
        # A rim cell that is also a riser (a climb lane over the cloud,
        # its south neighbour 4 lower) takes the crest of every side it
        # steps down on: the E crest alone draws no south side, and the
        # step showed as a black seam between the treads (verifier
        # 2026-10-17 finding 3).
        fr = crest_frame(cx, cy, set(drops) | risers)
        out.append(MapItem.placed_item(X, Y, top, SHAPE_CREST, fr))
        out.extend(face_items(cx, cy, top, drops, fr, (cx, cy) in bare,
                              window))
    return out


def exposed(field):
    """Rock whose eight neighbours include lower rock or another material.

    Water, cloud, and lower terraces expose the backs of north and west
    faces. Their textured frames close the black slabs between tiers.
    """
    out = set()
    for (cx, cy), c in field.items():
        if c.kind != ROCK:
            continue
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = field.get((cx + dx, cy + dy))
                if n is None or n.kind != ROCK or n.z < c.z:
                    out.add((cx, cy))
    return out


# ── The vignettes: the 1994 shots, verbatim ─────────────────────────────
# vignette_place.stamp() places ONE shot into a generated map. Map 13 has
# four, two pairs of them sharing cells (screen14/16 in y 5120-5375,
# screen15/16 in the lake), and its terrain is generated around them rather
# than cut away for them, so this layer does the same job for all four at
# once: their items at origin + local (exact duplicates, the lake's shared
# water, laid once), the union of their 128-unit regions, and what each
# region cell shows — the level the generated neighbours must meet.

FACE_SHAPES = frozenset({26, 27, 28, 29, 30, 31, 32, 33, 167, 370, 566})
# The sides a 125 crest frame says its cell drops on (CREST_BY_DROP read
# backwards, unambiguous frames only).
CREST_LIPS = {0: 'SE', 1: 'E', 2: 'E', 3: 'S', 4: 'S', 5: 'SW', 6: 'NE',
              7: 'W', 8: 'W', 9: 'N', 10: 'N', 11: 'NW'}


def vignette_layer(shots, map_num, art_map, standin_dz=None, slides=None,
                   cuts=None, floating=None):
    """(items, region, cells) for `shots` on `map_num`.

    art_map     1994-art id -> shape (keeping the item's frame) or
                (shape, frame), as vignette_place takes it;
    standin_dz  shape -> z drop, for art whose hotspot differs from the
                1994 frame's (874: one unit, phaseC-art.md);
    slides      {(shot, shape, frame, local x, y, z): k}: move that item k
                steps of (8, 8, 2) along the view ray. Every step draws
                exactly the same pixels (screen x = x/4 - y/4, y = x/8 +
                y/8 - z, all exact), so the shot is unchanged; only which
                boxes the item meets is (build_map_13.RAY_SLIDES);
    cuts        {(shot, shape, frame, local x, y, z): ((shape, frame),
                [(dx, dy, dz), ...])}: lay those pieces at the item's place
                plus each offset instead of the item — the part of a big
                piece that draws in the shot's window, without the part
                beyond it (build_map_13.SHOT_CUTS);
    floating    {shot: vignette shapes}: that shot's items of those shapes
                are laid but are no ground: they float over the shot's
                ground, so they add no cell to `region` and no top to
                `cells` (build_map_13.FLOATING, screen13's cloud);
    cells       (cx, cy) -> {'top': highest walkable top over the cell's
                centre or None, 'water': only water there, 'cloud': the
                cloud sea's own floor there (874 at the plane, not
                screen13's floating patches),
                'edge': {side: base of the lowest face piece in that edge
                strip}, 'lips': sides its top crest's frame drops on}.
    """
    import vignette_place as VP
    standin_dz = standin_dz or {}
    slides = dict(slides or {})
    cuts = dict(cuts or {})
    floating = floating or {}
    items, ground, seen, region = [], [], set(), set()
    for shot in shots:
        vig = VP.load(shot)
        if vig['placement']['map'] != map_num:
            raise ValueError(f'{shot} belongs to map '
                             f"{vig['placement']['map']}, not {map_num}")
        ox, oy, oz = VP.origin(vig)
        afloat = frozenset(floating.get(shot, ()))
        for it in vig['items']:
            shape, frame = it['shape'], it['frame']
            lands = shape not in afloat
            name = (shot, shape, frame, it['x'], it['y'], it['z'])
            k = slides.pop(name, 0)
            dz = 0
            if shape in art_map:
                to = art_map[shape]
                shape, frame = (to, frame) if isinstance(to, int) else to
                dz = standin_dz.get(shape, 0)
            elif not isinstance(shape, int) or shape >= VP.FIRST_SYNTHETIC_ID:
                raise ValueError(f'{shot}: item {it} is 1994-only art with '
                                 'no stand-in in art_map')
            x, y, z = (ox + it['x'] + 8 * k, oy + it['y'] + 8 * k,
                       oz + it['z'] - dz + 2 * k)
            pieces = [(shape, frame, x, y, z)]
            if name in cuts:
                (shape, frame), offsets = cuts.pop(name)
                pieces = [(shape, frame, x + ddx, y + ddy, z + ddz)
                          for (ddx, ddy, ddz) in offsets]
            for key in pieces:
                if key in seen:
                    continue
                seen.add(key)
                items.append(MapItem.placed_item(key[2], key[3], key[4],
                                                 key[0], key[1]))
                if lands:
                    ground.append(items[-1])
        region |= VP.region(dict(vig, items=[it for it in vig['items']
                                             if it['shape'] not in afloat]),
                            art_map)
    stale = [s for s in list(slides) + list(cuts) if s[0] in shots]
    if stale:
        raise ValueError(f'slides/cuts name no item of their shot: {stale}')
    flags = VP._flags()
    cells = {}
    for (cx, cy) in region:
        X, Y = corner(cx), corner(cy)
        px, py = X - 64, Y - 64
        tops, water, cloud = [], True, False
        edge, lips, crest_z = {}, '', None
        for it in ground:
            f = flags.get(it.shape)
            if not f:
                continue
            w, d = f['xfoot'] * 32, f['yfoot'] * 32
            if it.shape in FACE_SHAPES:
                side = _face_side(it.x, it.y, w, d, X, Y)
                # A post is a convex corner, filed under the south face as
                # face_items lays it (piece_side): in another strip it is
                # the end of a face that strip's own pieces already name.
                # screen01's north-east post (29:7, 2026-10-17) read as a
                # north face from z 120 raised the cloud cell beyond it into
                # the window.
                if side and (it.shape != SHAPE_POST or side == 'S'):
                    edge[side] = min(edge.get(side, it.z), it.z)
                continue
            if not (f['land'] or f['sea']) or f['xfoot'] < 2 or f['yfoot'] < 2:
                continue
            if not (it.x - w < px <= it.x and it.y - d < py <= it.y):
                continue
            tz = it.z + f['zfoot'] * 8
            tops.append(tz)
            water &= f['sea']
            cloud |= it.shape == SHAPE_CLOUD and it.z <= CLOUD_Z
            if it.shape == SHAPE_CREST and (crest_z is None or tz > crest_z):
                crest_z, lips = tz, CREST_LIPS.get(it.frame, '')
        top = max(tops) if tops else None
        cells[(cx, cy)] = dict(
            top=top, water=bool(tops) and water, cloud=cloud,
            edge={s: z for s, z in edge.items() if top is None or z < top},
            lips=set(lips) if crest_z == top else set())
    return items, region, cells


def _face_side(x, y, w, d, X, Y):
    """The edge strip of cell (X - 128, X] x (Y - 128, Y] a face piece with
    max corner (x, y) and footprint w x d stands in, if any: a piece no
    deeper than 32 across the strip and covering at least 32 of the
    cell's side along it."""
    def along(a1, la, b1):
        return min(a1, b1) - max(a1 - la, b1 - CELL) >= 32
    if d <= 32 and along(x, w, X):
        if Y - 32 < y <= Y:
            return 'S'
        if Y - CELL < y <= Y - 96:
            return 'N'
    if w <= 32 and along(y, d, Y):
        if X - 32 < x <= X:
            return 'E'
        if X - CELL < x <= X - 96:
            return 'W'
    return None


# The window fit's refusals (lv_map13_views.py) are per piece: a shot
# cell's completion piece by piece_key, its cloud filler by CLOUD_KEY. Until
# 2026-10-17 they were per side, and refusing a whole side for the one
# course that drew into a window left the courses that did not as void
# beside the mid-climb windows (verifier 2026-10-17 pass 2, A3).
CLOUD_KEY = 'C'


def piece_key(it):
    """A completion piece's refusal key: its side (piece_side) and z, as
    face_items lays it (before any shot_faces slide)."""
    return f'{piece_side(it.shape, it.x, it.y)}{it.z}'


def piece_side(shape, x, y):
    """The side of its cell a face_items piece (shape, max corner x, y)
    stands on: an x piece (26/27/28) S or N by its y, the post (29) S, a y
    piece (32/31/30) E or W by its x, a lip (125) 'L'."""
    if shape == SHAPE_CREST:
        return 'L'
    if shape == SHAPE_POST:
        return 'S'
    if shape in (26, 27, 28):
        return 'S' if y % CELL == CELL - 1 else 'N'
    return 'E' if x % CELL == CELL - 1 else 'W'


# How far shot_faces slides a completion piece along the view ray to clear
# a shot item's box (steps of (8, 8, 2), vignette_layer's `slides`).
FACE_SLIDE_MAX = 8


def _box_of(flags, it):
    f = flags.get(it.shape)
    if not f:
        return None
    return (it.x - f['xfoot'] * 32, it.y - f['yfoot'] * 32, it.z,
            it.x, it.y, it.z + max(f['zfoot'] * 8, 1))


def _meets_any(b, boxes):
    x0, y0, z0, x1, y1, z1 = b
    return any(x0 < bx1 and bx0 < x1 and y0 < by1 and by0 < y1 and
               z0 < bz1 and bz0 < z1
               for (bx0, by0, bz0, bx1, by1, bz1) in boxes)


def shot_faces(field, cells, vitems, refused=None, outside=0, window=None,
               around=(), keys=None):
    """Faces under the shots' own cells where the generated ground beside
    them lies lower (verifier 2026-10-17 finding 3: black slabs in the
    mid-climb cliffs and under screen01's window). A shot draws only what
    its frame showed, so a LOCK cell's faces stop at the frame's edge, and a
    HIDDEN cell is a floor alone; beside a lower neighbour both showed void.
    On each side whose neighbour (not another shot cell) is lower than what
    the cell presents there, courses in the tier grammar go on down to it:
    from the base of the shot's lowest piece in that strip (`edge`), else
    from its crest's base if its top crest drops that way, else flush under
    its top — a HIDDEN cell's own floor. Drawn frames on every side (beside
    a shot the camera sees behind a cell, `exposed`), but where a piece
    could draw into a window (`window`, face_items'). No piece overlaps a
    piece of the shot's own (overlapping solid boxes close paint cycles): one
    whose box would meet a shot item's is slid along the view ray, k steps
    of (8, 8, 2) as RAY_SLIDES moves a shot's own piece, which draws the
    same pixels, to the nearest k (|k| <= FACE_SLIDE_MAX, z >= 0) where it
    meets no shot item, no other completion piece and no generated piece
    in `around`; with none, it is left out, and the void it would have
    closed showed black beside the mid-climb windows (verifier 2026-10-17
    pass 2, A3). `refused`: {cell: set of piece_key} of the LOCK cells'
    pieces the window fit (lv_map13_views.py) found drawing into a window;
    a HIDDEN cell it lowers instead. `keys`, a dict, is filled with
    {(shape, x, y, z) as laid: (cell, piece_key)} for the fit to name what
    it sees."""
    refused = refused or {}
    import vignette_place as VP
    flags = VP._flags()
    boxes = [b for b in (_box_of(flags, it) for it in vitems) if b]

    out, stuck = [], []
    for (cx, cy), c in sorted(field.items()):
        if c.kind not in (LOCK, HIDDEN):
            continue
        v = cells.get((cx, cy))
        starts = {}
        for side, (dx, dy) in SIDES.items():
            nb = field.get((cx + dx, cy + dy))
            if nb is not None and nb.kind == LOCK:
                continue
            lower = outside if nb is None else nb.level(OPPOSITE[side])
            if c.kind == HIDDEN:
                start = c.z
            elif side in v['edge']:
                start = v['edge'][side]
            elif v['top'] is None:
                continue
            elif side in v['lips']:
                start = v['top'] - 8
            else:
                start = v['top']
            if lower < start:
                starts.setdefault(start, {})[side] = lower
        gone = refused.get((cx, cy), ())
        for start, drops in sorted(starts.items()):
            fr = crest_frame(cx, cy, drops)
            for it in face_items(cx, cy, start, drops, fr, True, window):
                key = piece_key(it)
                if key in gone:
                    continue
                (stuck if _meets_any(_box_of(flags, it), boxes)
                 else out).append((it, ((cx, cy), key)))
    taken = boxes + [_box_of(flags, it) for it, _ in out]
    taken += [b for b in (_box_of(flags, it) for it in around) if b]
    for it, name in stuck:
        for k in sorted(range(-FACE_SLIDE_MAX, FACE_SLIDE_MAX + 1),
                        key=lambda k: (abs(k), k)):
            if not k or it.z + 2 * k < 0:
                continue
            moved = MapItem.placed_item(it.x + 8 * k, it.y + 8 * k,
                                        it.z + 2 * k, it.shape, it.frame)
            b = _box_of(flags, moved)
            if not _meets_any(b, taken):
                out.append((moved, name))
                taken.append(b)
                break
    if keys is not None:
        keys.update(((it.shape, it.x, it.y, it.z), name) for it, name in out)
    return [it for it, _ in out]


# The cloud filler: the plane's own lattice tile slid 4 steps down the view
# ray (-32, -32, -8), so it draws exactly the pixels a tile on the plane
# would and sorts under every tile that is on it.
CLOUD_FILL_SLIDE = -4


def cloud_fill(field, cells, refused=None):
    """The 1994 cloud under screen01's own cloud (verifier 2026-10-17
    finding 2). The shot lays its cloud tiles on a 32-unit grid, so they
    overlap and leave 32-unit holes between them, and a hole drew the void
    floor's black plate as a black diamond inside the window, where the shot
    shows cloud. One 874 per cell, the plane's lattice tile slid down the
    view ray (CLOUD_FILL_SLIDE), under every shot cell that shows cloud and
    every VOID or HIDDEN cell below the plane beside a cloud cell (the
    shot's or the sea's): the shot's tiles draw over it, so it shows only
    through their holes."""
    k = CLOUD_FILL_SLIDE
    fill_z = CLOUD_Z - CLOUD_DZ + 2 * k

    def cloudy(c):
        n = field.get(c)
        return n is not None and (n.kind == CLOUD or (
            n.kind == LOCK and cells[c]['cloud']))
    out = []
    for (cx, cy), c in sorted(field.items()):
        if c.kind == LOCK:
            if not cells[(cx, cy)]['cloud'] or \
                    CLOUD_KEY in (refused or {}).get((cx, cy), ()):
                continue
        elif not (c.kind == VOID or (c.kind == HIDDEN and c.z < fill_z)) or \
                not any(cloudy((cx + dx, cy + dy))
                        for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            continue
        out.append(MapItem.placed_item(corner(cx) + 8 * k, corner(cy) + 8 * k,
                                       fill_z, SHAPE_CLOUD,
                                       pick(CLOUD_FRAMES, cx, cy, 2)))
    return out


# ── Curbs: retail's invisible wall at every edge a walker could fall off ──

SHAPE_CURB_X = 497        # 128 x 32 x 48, SOLID|EDITOR: never drawn
SHAPE_CURB_Y = 498        # 32 x 128 x 48

# A side of cell (cx, cy) and the curb beyond it, in the neighbour's
# adjoining strip, as (shape, max-corner x, max-corner y).
CURB_AT = {
    'E': lambda X, Y: (SHAPE_CURB_Y, X + 32, Y),
    'W': lambda X, Y: (SHAPE_CURB_Y, X - 128, Y),
    'S': lambda X, Y: (SHAPE_CURB_X, X, Y + 32),
    'N': lambda X, Y: (SHAPE_CURB_X, X, Y - 128),
}


def edge_curbs(levels, walkers, min_drop, open_sides=frozenset()):
    """A course of invisible wall beyond every side of every cell in
    `walkers` ({(cx, cy): standing z}) whose neighbour's level (`levels`,
    a function of the neighbour cell and the side it faces) is `min_drop`
    or more below it, except the (cell, side) pairs in `open_sides`.
    SOLID without LAND, so it supports nothing: no standing level is added,
    and a jump cannot land on it either."""
    out = []
    for (cx, cy), z in sorted(walkers.items()):
        for side, (dx, dy) in SIDES.items():
            if ((cx, cy), side) in open_sides:
                continue
            if levels((cx + dx, cy + dy), OPPOSITE[side]) > z - min_drop:
                continue
            shape, x, y = CURB_AT[side](corner(cx), corner(cy))
            out.append(MapItem.placed_item(x, y, z, shape, 0))
    return out

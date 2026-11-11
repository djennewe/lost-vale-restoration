#!/usr/bin/env python3
"""dressing_metrics.py -- how dressed is a map, measured the way retail is.

Phase 4 of the visual-quality pass (docs/research/2026-11-01-visual-pass/
phase4-direction.md) sets its acceptance numbers from retail maps. This
module computes those numbers for any map of any FIXED.DAT, whole or per
world rectangle, so the same code calibrates on retail and gates ours.

It reads the BUILT artifact with glob eggs expanded (map-geometry.md: test
what ships), and classifies every visible item from TYPEFLAG alone, so no
shape list has to be kept in step with the art track:

  ground     a tile the eye reads as floor: a flat of 64x64 or more, or a
             LAND tile of 128x128 or more that is at most 8 tall (retail's
             grass, bank and crest tiles 70/94/125/126/128 are 8 tall, and
             a zero-height test files them under props)
  void       a ground-class item that is filler or backdrop, not material:
             VOID_FRAMES (564:2, 35:10) and BACKDROP_SHAPES (water, stars, and decorative backdrop copies)
  trim       an edge piece: at most 8 tall, at most 32 across one way and
             96 or more the other (retail's 131/138/302 cave edging, the
             670/692 kerbs)
  structure  LAND and SOLID and not ground: walls, blocks, cliffs, stairs
  prop       everything else the engine draws; `small` up to 96x96 in
             footprint, `large` above (root tangles 57, spire clusters 66)

Per 128-unit cell the ground material is the top ground item covering the
cell centre (highest z, void last, later record on a tie), which is what an
overview shows. All shares are over ground cells, never over records, so a
256 plate counts as its four cells.

Usage:
    python3 dressing_metrics.py 10 11 13                # the built FIXED
    python3 dressing_metrics.py 3 5 7 --retail          # pristine retail
    python3 dressing_metrics.py 10 --box 17408 6272 22528 9728
    python3 dressing_metrics.py 10 --json out.json
    python3 dressing_metrics.py --regions               # every LV region
    python3 dressing_metrics.py 11 --regions            # one map's regions
    python3 dressing_metrics.py --calibrate             # retail, per type

REGIONS names every LV region with its type; TARGETS holds the per-type
acceptance numbers; RETAIL_TYPES names the retail maps they were read from.
"""

import argparse
import collections
import contextlib
import io
import json
import math
import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

with contextlib.redirect_stdout(io.StringIO()):
    import item_sorter as isort                      # noqa: E402
    from u8_map import MapArchive                    # noqa: E402
    from glob_catalog import GlobReader              # noqa: E402

BUILD = os.path.join(REPO, 'shared', 'build')
STATIC = os.path.join(REPO, 'shared', 'data', 'u8-install', 'STATIC')

CELL = 128                 # one ground tile
CHUNK = 512                # one glob / CurrentMap chunk
FLG_CONTAINED = 0x0008

VOID_FRAMES = {(564, 2), (35, 10)}      # lv_furnish.void_floor's plates
BACKDROP_SHAPES = {347, 351, 894, 895, 902} | set(range(916,929))            # land excludes water, stars, and decorative backdrop copies

LINK = 192                 # props this close (centre to centre) are a group
BARE_RADIUS = 4            # cells; (2r+1)^2 cells is about a quarter screen
MAX_LAG = 16               # ground-period search, in cells
REPEAT_MIN_CELLS = 400     # regions smaller than this skip repetition limits


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

class Source:
    """One FIXED.DAT with the TYPEFLAG and GLOB.FLX it is read against."""

    def __init__(self, fixed=None, typeflag=None, shapes=None, glob=None,
                 retail=False):
        if retail:
            fixed = fixed or os.path.join(STATIC, 'FIXED.DAT.bak')
            typeflag = typeflag or os.path.join(STATIC, 'TYPEFLAG.DAT.bak')
            shapes = shapes or os.path.join(STATIC, 'U8SHAPES.FLX.bak')
        self.arch = None if fixed is False else MapArchive(fixed or os.path.join(BUILD, 'FIXED.DAT'))
        self.sorter = isort.ItemSorter(
            typeflag=typeflag or os.path.join(BUILD, 'TYPEFLAG.DAT'),
            shapes=shapes or os.path.join(BUILD, 'U8SHAPES.FLX'))
        self.globs = GlobReader(glob or (os.path.join(STATIC, 'GLOB.FLX.bak')
                                       if retail and os.path.exists(os.path.join(STATIC, 'GLOB.FLX.bak'))
                                       else os.path.join(STATIC, 'GLOB.FLX') if retail else None))
        self._info = {}

    def info(self, shape):
        inf = self._info.get(shape)
        if inf is None:
            inf = self._info[shape] = self.sorter.info(shape)
        return inf

    def raw(self, mapnum):
        return self.arch.get_map_items(mapnum)

    def expanded(self, raw):
        """[(item, glob number or None)]: globs expanded as
        GlobEgg::enterFastArea does, each item keeping where it came from.
        An empty or missing glob keeps its egg, as map_preview does."""
        out = []
        for it in raw:
            if it.is_glob_egg:
                got = self.globs.glob_to_items(it.quality, it.x, it.y, it.z)
                if got:
                    out.extend((g, it.quality) for g in got)
                    continue
            out.append((it, None))
        return out


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def item_class(inf, shape, frame):
    """'skip', 'void', 'ground', 'trim', 'structure', 'small' or 'large'."""
    if inf['editor']:
        return 'skip'
    xd, yd, zd = inf['xd'], inf['yd'], inf['zd']
    flat = zd == 0 and xd >= 64 and yd >= 64
    tile = inf['land'] and zd <= 8 and xd >= 128 and yd >= 128
    if flat or tile:
        if (shape, frame) in VOID_FRAMES or shape in BACKDROP_SHAPES:
            return 'void'
        return 'ground'
    if zd <= 8 and min(xd, yd) <= 32 and max(xd, yd) >= 96:
        return 'trim'
    if inf['land'] and inf['solid']:
        return 'structure'
    return 'small' if xd <= 96 and yd <= 96 else 'large'


def _cells(x, y, xd, yd):
    """128-cells whose centre lies in the half-open box (x-xd, x] x (y-yd, y]
    (Box::contains: the high edge is in the box)."""
    cx0 = -(-(x - xd + 1 - CELL // 2) // CELL)
    cx1 = (x - CELL // 2) // CELL
    cy0 = -(-(y - yd + 1 - CELL // 2) // CELL)
    cy1 = (y - CELL // 2) // CELL
    for cx in range(cx0, cx1 + 1):
        for cy in range(cy0, cy1 + 1):
            yield cx, cy


class Layers:
    """A map split into ground cells, void cells and placed things."""

    def __init__(self, src, raw, box=None, *, legacy_area=False):
        self.src = src
        self.raw = [it for it in raw if _in_box(it, box)]
        self.box = box
        self.ground = {}        # (cx, cy) -> (shape, frame, z, roof)
        self.void = set()       # cells only filler or backdrop covers
        self.things = []        # (cls, x, y, z, shape, frame, glob)
        self.items = 0          # expanded records (in the box)
        self.glob_items = 0
        self.eggs = collections.Counter()   # glob number -> eggs
        best = {}
        n = 0
        for it, glob in src.expanded(raw):
            n += 1
            if not _in_box(it, box):
                continue
            self.items += 1
            if glob is not None:
                self.glob_items += 1
            if it.flags & (isort.FLG_INVISIBLE | FLG_CONTAINED):
                continue
            inf = src.info(it.shape)
            cls = item_class(inf, it.shape, it.frame)
            if legacy_area and it.shape in (347,351):
                cls = 'ground'
            if cls == 'skip':
                continue
            if cls in ('ground', 'void'):
                rank = (0 if cls == 'void' else 1, it.z, n)
                for c in _cells(it.x, it.y, inf['xd'], inf['yd']):
                    if c not in best or rank > best[c][0]:
                        best[c] = (rank, it.shape, it.frame, it.z,
                                   inf['roof'], cls)
            else:
                self.things.append((cls, it.x - inf['xd'] // 2,
                                    it.y - inf['yd'] // 2, it.z,
                                    it.shape, it.frame, glob))
        for it in self.raw:
            if it.is_glob_egg:
                self.eggs[it.quality] += 1
        for c, (_, shape, frame, z, roof, cls) in best.items():
            if box and not (box[0] <= c[0] * CELL + 64 <= box[2]
                            and box[1] <= c[1] * CELL + 64 <= box[3]):
                continue
            if cls == 'void':
                self.void.add(c)
            else:
                self.ground[c] = (shape, frame, z, roof)

    def of(self, *classes):
        return [t for t in self.things if t[0] in classes]


def _in_box(it, box):
    return (box is None or
            (box[0] <= it.x <= box[2] and box[1] <= it.y <= box[3]))


# ---------------------------------------------------------------------------
# Ground: material mix, patches, transitions, repetition
# ---------------------------------------------------------------------------

def ground_metrics(lay):
    g = lay.ground
    n = len(g)
    if not n:
        return dict(cells=0)
    mat = collections.Counter(v[0] for v in g.values())
    tile = collections.Counter(v[:2] for v in g.values())
    shares = [c / n for _, c in mat.most_common()]
    entropy = -sum(p * math.log(p) for p in shares)
    # Patches: 4-connected cells of one material (shape).
    seen, patches = set(), []
    for c in g:
        if c in seen:
            continue
        m, stack, size = g[c][0], [c], 0
        seen.add(c)
        while stack:
            x, y = stack.pop()
            size += 1
            for d in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if d not in seen and d in g and g[d][0] == m:
                    seen.add(d)
                    stack.append(d)
        patches.append(size)
    # Transitions: adjacent ground pairs of different material.
    pairs = diff = 0
    seams = collections.Counter()
    for (x, y), v in g.items():
        for d in ((x + 1, y), (x, y + 1)):
            w = g.get(d)
            if w is None:
                continue
            pairs += 1
            if w[0] != v[0]:
                diff += 1
                seams[tuple(sorted((v[0], w[0])))] += 1
    return dict(
        cells=n,
        materials=len(mat),
        materials_1pct=sum(1 for p in shares if p >= 0.01),
        top1=shares[0], top3=sum(shares[:3]),
        top=[[s, round(c / n, 4)] for s, c in mat.most_common(6)],
        effective_materials=math.exp(entropy),
        top_tile=tile.most_common(1)[0][1] / n,
        roof_share=sum(1 for v in g.values() if v[3]) / n,
        largest_patch=max(patches) / n,
        patches_per_100=100 * len(patches) / n,
        seam_density=diff / pairs if pairs else 0.0,
        seams=[[a, b, c] for (a, b), c in seams.most_common(6)],
    )


def repetition_metrics(lay):
    """The tile period (plan section 11.9).

    r(p) is the share of ground cells whose (shape, frame) equals the cell
    p cells away, averaged over the x and y axes. `same_neighbour` is r(1):
    how often a tile is its own neighbour. `period` is the lag from 2 to
    MAX_LAG with the highest r, and `period_excess` is how far that lag
    stands above the median lag, which is what the eye picks up as a
    stride. `modal_chunk` is the share of full 512 chunks whose ground AND
    contents are the map's single most common chunk: the measure of a
    one-material plain."""
    g = lay.ground
    if not g:
        return {}
    r = {}
    for p in range(1, MAX_LAG + 1):
        same = tot = 0
        for (x, y), v in g.items():
            for d in ((x + p, y), (x, y + p)):
                w = g.get(d)
                if w is not None:
                    tot += 1
                    same += v[:2] == w[:2]
        r[p] = same / tot if tot else 0.0
    lags = sorted(r[p] for p in range(2, MAX_LAG + 1))
    period = max(range(2, MAX_LAG + 1), key=lambda p: (r[p], -p))
    # Chunk signatures: the 16 ground tiles plus everything standing in it.
    per = CHUNK // CELL
    chunks = collections.defaultdict(dict)
    for (x, y), v in g.items():
        chunks[(x // per, y // per)][(x % per, y % per)] = v[:2]
    inside = collections.defaultdict(list)
    for cls, x, y, z, shape, frame, _ in lay.things:
        inside[(x // CHUNK, y // CHUNK)].append(
            (cls, x % CHUNK // 32, y % CHUNK // 32, shape))
    plain = collections.Counter()
    full = collections.Counter()
    nfull = 0
    for k, cells in chunks.items():
        if len(cells) < per * per:
            continue
        nfull += 1
        gsig = tuple(sorted(cells.items()))
        plain[gsig] += 1
        full[(gsig, tuple(sorted(inside.get(k, ()))))] += 1
    return dict(
        same_neighbour=r[1],
        period=period, period_match=r[period],
        period_excess=r[period] - lags[len(lags) // 2],
        lag_match={p: round(v, 4) for p, v in r.items()},
        chunks=nfull,
        modal_ground_chunk=(plain.most_common(1)[0][1] / nfull
                            if nfull else 0.0),
        modal_chunk=full.most_common(1)[0][1] / nfull if nfull else 0.0,
        distinct_chunks=len(full) / nfull if nfull else 0.0,
    )


# ---------------------------------------------------------------------------
# Props: density, clustering, strides
# ---------------------------------------------------------------------------

def _groups(pts, link=LINK):
    """Single-link groups of points closer than `link` (union-find over a
    grid hash)."""
    parent = list(range(len(pts)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    grid = collections.defaultdict(list)
    for i, (x, y) in enumerate(pts):
        grid[(x // link, y // link)].append(i)
    for i, (x, y) in enumerate(pts):
        gx, gy = x // link, y // link
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in grid.get((gx + dx, gy + dy), ()):
                    if j > i and ((x - pts[j][0]) ** 2
                                  + (y - pts[j][1]) ** 2) <= link * link:
                        a, b = find(i), find(j)
                        if a != b:
                            parent[a] = b
    out = collections.defaultdict(list)
    for i in range(len(pts)):
        out[find(i)].append(i)
    return list(out.values())


def _nearest(pts):
    """Distance from each point to its nearest other point."""
    grid = collections.defaultdict(list)
    step = 256
    for i, (x, y) in enumerate(pts):
        grid[(x // step, y // step)].append(i)
    out = []
    for i, (x, y) in enumerate(pts):
        best, ring = None, 1
        gx, gy = x // step, y // step
        while best is None or best > (ring - 1) * step:
            for dx in range(-ring, ring + 1):
                for dy in range(-ring, ring + 1):
                    if max(abs(dx), abs(dy)) != ring and ring > 1:
                        continue
                    for j in grid.get((gx + dx, gy + dy), ()):
                        if j != i:
                            d = math.hypot(x - pts[j][0], y - pts[j][1])
                            if best is None or d < best:
                                best = d
            ring += 1
            if ring > 64:
                break
        out.append(best if best is not None else float('inf'))
    return out


def prop_metrics(lay):
    g = lay.ground
    n = len(g)
    counts = collections.Counter(t[0] for t in lay.things)
    props = lay.of('small', 'large')
    small = lay.of('small')
    out = dict(
        small=counts['small'], large=counts['large'], trim=counts['trim'],
        structure=counts['structure'],
        shapes=len({t[4] for t in props}),
        top=[[s, c] for s, c in collections.Counter(
            t[4] for t in props).most_common(8)],
        from_globs=(sum(1 for t in props if t[6] is not None) / len(props)
                    if props else 0.0),
    )
    if not n:
        return out
    out.update(
        small_per_100=100 * counts['small'] / n,
        props_per_100=100 * len(props) / n,
        trim_per_100=100 * counts['trim'] / n,
        structure_per_100=100 * counts['structure'] / n,
    )
    # Coverage: how much ground has something on or beside it, and how much
    # is bare -- nothing placed and no change of material within BARE_RADIUS.
    busy = collections.Counter()
    for t in lay.things:
        busy[(t[1] // CELL, t[2] // CELL)] += 1
    dressed = sum(1 for (x, y) in g
                  if any((x + dx, y + dy) in busy
                         for dx in (-1, 0, 1) for dy in (-1, 0, 1)))
    r = BARE_RADIUS
    bare = 0
    for (x, y), v in g.items():
        ok = True
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                c = (x + dx, y + dy)
                w = g.get(c)
                if c in busy or (w is not None and w[0] != v[0]):
                    ok = False
                    break
            if not ok:
                break
        bare += ok
    out.update(dressed_share=dressed / n, bare_share=bare / n)
    # Clustering of the small props.
    pts = [(t[1], t[2]) for t in small]
    if len(pts) >= 8:
        nn = sorted(_nearest(pts))
        mean_nn = sum(nn) / len(nn)
        area = n * CELL * CELL
        expected = 0.5 / math.sqrt(len(pts) / area)
        groups = _groups(pts)
        sizes = sorted(len(q) for q in groups)
        in3 = sum(s for s in sizes if s >= 3)
        mixed = sum(1 for q in groups if len(q) >= 2
                    and len({small[i][4] for i in q}) >= 2)
        multi = sum(1 for q in groups if len(q) >= 2)
        by_item = sorted(s for s in sizes for _ in range(s))
        per = collections.Counter((x // CHUNK, y // CHUNK) for x, y in pts)
        nch = max(1, n // 16)
        mean = len(pts) / nch
        var = (sum((c - mean) ** 2 for c in per.values())
               + (nch - len(per)) * mean ** 2) / nch
        out.update(
            nn_median=nn[len(nn) // 2],
            clark_evans=mean_nn / expected,
            groups_per_100=100 * len(groups) / n,
            grouped_share=in3 / len(pts),
            singles_share=sum(1 for s in sizes if s == 1) / len(pts),
            group_size_median=by_item[len(by_item) // 2],
            mixed_groups=mixed / multi if multi else 0.0,
            chunk_vmr=var / mean if mean else 0.0,
        )
    out['stride_share'] = stride_share(small)
    return out


def stride_share(things, least=6):
    """How much of the small-prop placement sits on a stride.

    For each shape placed `least` times or more, take every instance's
    vector to its nearest same-shape instance (32-unit lattice, sign
    folded). The share of instances whose vector is one of that shape's two
    commonest is 1.0 for a lattice or a row and near 2/n for a scatter.
    Returns the instance-weighted mean over shapes, or None when no shape
    has enough instances to measure."""
    by = collections.defaultdict(list)
    for t in things:
        by[t[4]].append((t[1], t[2]))
    hit = tot = 0
    for pts in by.values():
        if len(pts) < least:
            continue
        vecs = []
        for i, (x, y) in enumerate(pts):
            best = None
            for j, (u, v) in enumerate(pts):
                if j != i:
                    d = (x - u) ** 2 + (y - v) ** 2
                    if best is None or d < best[0]:
                        best = (d, (u - x) // 32, (v - y) // 32)
            vx, vy = best[1], best[2]
            if (vx, vy) < (0, 0):
                vx, vy = -vx, -vy
            vecs.append((vx, vy))
        top = sum(c for _, c in collections.Counter(vecs).most_common(2))
        hit += top
        tot += len(vecs)
    return hit / tot if tot else None


# ---------------------------------------------------------------------------
# Records and globs
# ---------------------------------------------------------------------------

def glob_metrics(lay):
    src = lay.src
    raw, eggs = len(lay.raw), sum(lay.eggs.values())
    kinds = {}
    for num in lay.eggs:
        cls = collections.Counter(
            item_class(src.info(g['shape']), g['shape'], g['frame'])
            for g in src.globs.get_glob(num))
        kinds[num] = ('dressing' if cls['small'] + cls['large'] else
                      'built' if cls['structure'] + cls['trim'] else
                      'ground')
    by_kind = collections.Counter()
    for num, c in lay.eggs.items():
        by_kind[kinds[num]] += c
    return dict(
        raw=raw, expanded=lay.items,
        expansion=lay.items / raw if raw else 0.0,
        eggs=eggs, egg_share=eggs / raw if raw else 0.0,
        glob_item_share=lay.glob_items / lay.items if lay.items else 0.0,
        distinct_globs=len(lay.eggs),
        eggs_ground=by_kind['ground'], eggs_built=by_kind['built'],
        eggs_dressing=by_kind['dressing'],
        top=[[num, c, kinds[num], len(src.globs.get_glob(num))]
             for num, c in lay.eggs.most_common(10)],
    )


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def measure(src, mapnum, box=None, raw=None, *, legacy_area=False):
    """Measure land ground. legacy_area preserves historical regional ratchets.

    Targets and whole-map budgets always use the default land area.
    """
    raw = src.raw(mapnum) if raw is None else raw
    lay = Layers(src, raw, box, legacy_area=legacy_area)
    out = dict(map=mapnum, box=list(box) if box else None,
               void_cells=len(lay.void))
    out['records'] = glob_metrics(lay)
    out['ground'] = ground_metrics(lay)
    out['repetition'] = repetition_metrics(lay)
    out['props'] = prop_metrics(lay)
    return out


# The numbers a ratchet test pins, as (path, direction): 'min' values may
# only rise, 'max' values may only fall.
RATCHET = (
    ('props.props_per_100', 'min'),
    ('ground.seam_density', 'min'),
    ('props.small_per_100', 'min'),
    ('props.dressed_share', 'min'),
    ('props.grouped_share', 'min'),
    ('props.bare_share', 'max'),
    ('props.stride_share', 'max'),
    ('ground.top1', 'max'),
    ('ground.largest_patch', 'max'),
    ('repetition.modal_chunk', 'max'),
    ('repetition.period_excess', 'max'),
    ('records.raw', 'max'),
)


def pick(metrics, path):
    v = metrics
    for key in path.split('.'):
        v = v.get(key) if isinstance(v, dict) else None
        if v is None:
            return None
    return v


def check(metrics, limits):
    """Compare against {path: (kind, bound)}; returns the failures as
    (path, value, kind, bound). A metric the region is too small to have
    (fewer than 8 small props) is skipped, not failed."""
    bad = []
    for path, (kind, bound) in limits.items():
        v = pick(metrics, path)
        if v is None:
            continue
        if (kind == 'min' and v < bound) or (kind == 'max' and v > bound):
            bad.append((path, v, kind, bound))
    return bad


COLUMNS = (
    ('cells', 'ground.cells', '{:>6d}'),
    ('top1%', 'ground.top1', '{:>5.0%}'),
    ('top3%', 'ground.top3', '{:>5.0%}'),
    ('effM', 'ground.effective_materials', '{:>4.1f}'),
    ('patch%', 'ground.largest_patch', '{:>6.0%}'),
    ('seam%', 'ground.seam_density', '{:>5.1%}'),
    ('sm/100', 'props.small_per_100', '{:>6.1f}'),
    ('lg/100', None, '{:>6.1f}'),
    ('all', 'props.props_per_100', '{:>5.1f}'),
    ('trim', 'props.trim_per_100', '{:>5.1f}'),
    ('dress%', 'props.dressed_share', '{:>6.0%}'),
    ('bare%', 'props.bare_share', '{:>5.0%}'),
    ('grp3%', 'props.grouped_share', '{:>5.0%}'),
    ('CE', 'props.clark_evans', '{:>4.2f}'),
    ('strd%', 'props.stride_share', '{:>5.0%}'),
    ('same1', 'repetition.same_neighbour', '{:>5.0%}'),
    ('per', 'repetition.period', '{:>3d}'),
    ('exc', 'repetition.period_excess', '{:>5.1%}'),
    ('modal', 'repetition.modal_chunk', '{:>5.0%}'),
    ('raw', 'records.raw', '{:>6d}'),
    ('x', 'records.expansion', '{:>4.1f}'),
    ('dEgg', 'records.eggs_dressing', '{:>4d}'),
)


def row(m):
    cells = []
    for name, path, fmt in COLUMNS:
        if name == 'lg/100':
            v = (pick(m, 'props.props_per_100') or 0) - (
                pick(m, 'props.small_per_100') or 0)
        else:
            v = pick(m, path)
        width = len(fmt.format(0))
        cells.append(fmt.format(v) if v is not None else ' ' * (width - 1) + '-')
    return ' '.join(cells)


def header():
    return ' '.join(f'{name:>{len(fmt.format(0))}}'
                    for name, _, fmt in COLUMNS)


# ---------------------------------------------------------------------------
# Region types, their retail references, and the phase 4 targets
# ---------------------------------------------------------------------------

# Retail maps that are one region type end to end (identified from 1/16
# overviews, 2026-11-09). `calibrate()` measures them; TARGETS below were set
# from that run and are the numbers phase4-direction.md section 1 quotes.
RETAIL_TYPES = {
    'grass':   (3, 5, 7, 4, 6),       # outdoor valleys and their villages
    'town':    (39, 40, 41),          # Tenebrae and the palace grounds
    'barren':  (21,),                 # rock plateau, earth patches, pools
    'cave':    (28, 47, 49, 57, 62, 31, 14),
    'lava':    (12, 44, 24, 25),
    'temple':  (63, 54, 15, 50, 51),  # stone interiors
    'sky':     (43,),                 # the Ethereal Void platform
}

# Every LV region phase 4 dresses: map -> [(name, type, (x0, y0, x1, y1))].
# Boxes are the builders' zone constants (phase4-direction.md section 3).
REGIONS = {
    8: [('door chamber', 'cave', (20095, 2591, 21316, 3999)),
        ('south shelf', 'cave', (27903, 23679, 32255, 30719))],
    9: [('guardian chamber', 'cave', (12800, 11520, 15103, 13311)),
        ('hall', 'cave', (12800, 13312, 14847, 15359)),
        ('passage', 'cave', (13824, 15360, 14847, 16895))],
    10: [('entry', 'barren', (10240, 1024, 15360, 4096)),
         ('hoskuld village', 'village', (3072, 5120, 8192, 11264)),
         ('north plain', 'barren', (8192, 4096, 17408, 11264)),
         ('gunnar village', 'village', (17408, 5120, 22528, 11264)),
         ('ezrekal', 'village', (11264, 11264, 14336, 14336)),
         ('west clearing', 'barren', (4096, 15360, 8192, 18432)),
         ('lake', 'shore', (11264, 15360, 15360, 20480)),
         ('sacred circle', 'barren', (18432, 15360, 22528, 18432)),
         ('cloud approach', 'barren', (5120, 20480, 9216, 24576)),
         ('moriens ruins', 'ruin', (11264, 21504, 14336, 24576)),
         ('temple approach', 'barren', (16384, 20480, 20480, 24576)),
         ('passage test', 'barren', (12288, 24576, 13312, 30208))],
    11: [('entry hall', 'temple', (8192, 1024, 11264, 4096)),
         ('hub', 'temple', (8192, 4096, 11264, 7168)),
         ('earth', 'cave', (1024, 1024, 6144, 6144)),
         ('air', 'cave', (14336, 1024, 19456, 6144)),
         ('fire', 'lava', (1024, 14336, 6144, 19456)),
         ('water', 'temple', (6144, 14336, 14336, 19456)),
         ('four pillars', 'cave', (6144, 19456, 10240, 22528)),
         ('pad room', 'temple', (8192, 22528, 9216, 23552))],
    13: [('valley', 'barren', (1536, 10240, 6656, 12288)),
         ('climb', 'cave', (1536, 1664, 6656, 10240)),
         ('summit', 'sky', (1536, 0, 8191, 1663))],
    17: [('scroll court', 'sky', (2688, 1024, 3968, 2048)),
         ('walkway field', 'sky', (1664, 2560, 6784, 4096)),
         ('processional', 'sky', (3712, 4480, 4480, 6144)),
         ('obelisk plaza', 'sky', (2944, 6016, 5248, 8064)),
         ('east court', 'sky', (5632, 4864, 6912, 6272)),
         ('arrival', 'sky', (3200, 9472, 6016, 10496))],
    18: [('exterior', 'temple', (2048, 512, 4095, 2559)),
         ('outer hall', 'temple', (1536, 2560, 4607, 4607)),
         ('transition hall', 'temple', (2048, 4608, 4095, 6143)),
         ('sanctum', 'cave', (1024, 6144, 5120, 9344))],
    39: [('lane and lawn', 'town', (15900, 19400, 21000, 20479))],
}

# {type: {metric path: (kind, bound)}}. Floors sit at or just under the
# weakest retail map of the type; ceilings at or just over it. `village`,
# `shore` and `ruin` have no single-type retail map and borrow: village from
# town, shore and ruin from barren with a higher density floor.
_BARREN = {
    'props.props_per_100': ('min', 3.5),
    'props.dressed_share': ('min', 0.24),
    'props.bare_share': ('max', 0.15),
    'props.grouped_share': ('min', 0.60),
    'props.stride_share': ('max', 0.75),
    'ground.top1': ('max', 0.55),
    'ground.seam_density': ('min', 0.10),
    'repetition.period_excess': ('max', 0.35),
    'repetition.modal_chunk': ('max', 0.25),
}
TARGETS = {
    'barren': _BARREN,
    'shore': dict(_BARREN, **{'props.props_per_100': ('min', 5.0)}),
    'ruin': dict(_BARREN, **{'props.props_per_100': ('min', 8.0)}),
    'village': dict(_BARREN, **{
        'props.props_per_100': ('min', 15.0),
        'props.dressed_share': ('min', 0.45),
        'props.bare_share': ('max', 0.10),
        'props.grouped_share': ('min', 0.80),
    }),
    'town': {
        'props.props_per_100': ('min', 20.0),
        'props.dressed_share': ('min', 0.45),
        'props.bare_share': ('max', 0.10),
    },
    'cave': {
        'props.props_per_100': ('min', 5.0),
        'props.dressed_share': ('min', 0.50),
        'props.bare_share': ('max', 0.18),
        'props.grouped_share': ('min', 0.45),
        'props.stride_share': ('max', 0.65),
        'ground.top1': ('max', 0.65),
        'repetition.period_excess': ('max', 0.40),
        'repetition.modal_chunk': ('max', 0.50),
    },
    'lava': {
        'props.props_per_100': ('min', 1.5),
        'props.dressed_share': ('min', 0.25),
        'props.bare_share': ('max', 0.35),
        'ground.top1': ('max', 0.70),
        'ground.seam_density': ('min', 0.10),
        'repetition.modal_chunk': ('max', 0.60),
    },
    'temple': {
        'props.props_per_100': ('min', 8.0),
        'props.dressed_share': ('min', 0.34),
        'props.bare_share': ('max', 0.20),
        'props.stride_share': ('max', 0.75),
        'ground.top1': ('max', 0.80),
        'repetition.period_excess': ('max', 0.35),
    },
    'sky': {
        'props.props_per_100': ('min', 7.0),
        'props.dressed_share': ('min', 0.14),
        'props.bare_share': ('max', 0.25),
        'repetition.modal_chunk': ('max', 0.62),
    },
}


def measure_regions(src, mapnum):
    """[(name, type, metrics, failures)] for every REGIONS row of a map."""
    raw = src.raw(mapnum)
    out = []
    for name, kind, box in REGIONS.get(mapnum, ()):
        m = measure(src, mapnum, box=box, raw=raw)
        limits = TARGETS[kind]
        if m['ground'].get('cells', 0) < REPEAT_MIN_CELLS:
            # Too few chunks for a period or a modal chunk to mean anything.
            limits = {p: b for p, b in limits.items()
                      if not p.startswith('repetition.')}
        out.append((name, kind, m, check(m, limits)))
    return out


def calibrate(src):
    """{type: {metric path: (low, high)}} over RETAIL_TYPES, whole maps."""
    paths = sorted({p for t in TARGETS.values() for p in t})
    out = {}
    for kind, maps in RETAIL_TYPES.items():
        got = [measure(src, m) for m in maps]
        out[kind] = {}
        for p in paths:
            vals = [pick(g, p) for g in got if pick(g, p) is not None]
            if vals:
                out[kind][p] = (min(vals), max(vals))
    return out


def _main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('maps', type=int, nargs='*')
    ap.add_argument('--regions', action='store_true',
                    help='one row per REGIONS box, with its target failures')
    ap.add_argument('--calibrate', action='store_true',
                    help='retail range per region type (implies --retail)')
    ap.add_argument('--glob', help='GLOB.FLX to expand eggs with')
    ap.add_argument('--retail', action='store_true',
                    help='pristine FIXED.DAT.bak with the .bak art')
    ap.add_argument('--fixed')
    ap.add_argument('--box', type=int, nargs=4,
                    metavar=('X0', 'Y0', 'X1', 'Y1'))
    ap.add_argument('--json', help='write the full metrics here')
    args = ap.parse_args()
    if args.calibrate:
        src = Source(retail=True, glob=args.glob)
        for kind, rng in calibrate(src).items():
            print(f'{kind} (maps {RETAIL_TYPES[kind]})')
            for p, (lo, hi) in rng.items():
                print(f'    {p:<28} {lo:8.3f} .. {hi:8.3f}')
        return
    src = Source(fixed=args.fixed, retail=args.retail, glob=args.glob)
    if args.regions:
        print(f"{'map':>3} {'region':<17}{'type':<8}" + header())
        bad = 0
        for m in args.maps or sorted(REGIONS):
            for name, kind, got, fails in measure_regions(src, m):
                print(f'{m:>3} {name:<17}{kind:<8}' + row(got))
                for path, v, k, bound in fails:
                    bad += 1
                    print(f'      FAIL {path} = {v:.3f}, {k} {bound}')
        print(f'{bad} target failures')
        return
    print(f"{'map':>4} " + header())
    full = []
    for m in args.maps:
        got = measure(src, m, box=args.box)
        full.append(got)
        print(f'{m:>4} ' + row(got))
    if args.json:
        with open(args.json, 'w') as fh:
            json.dump(full, fh, indent=1)


if __name__ == '__main__':
    _main()

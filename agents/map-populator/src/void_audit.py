#!/usr/bin/env python3
"""Audit built-map void at reachable, Avatar-centred 640x400 cameras.

    python3 -B void_audit.py 9 --step 32 --out /tmp/claude-1000/audits

The flood is test_monster_eggs.dry_flood, on its 32-unit lattice. --step
subsamples that lattice (32, 64, ...); it never changes flood connectivity.
Painter.built supplies both sorting and painting. Chunk-sized camera atlases
reuse the sorted scene and pixels, with separate atlases for each standing
level and roof cut. avatar_visibility imports the shared read-only helpers.

walkable_black tests the floor at the Avatar's bottom centre, independently
of foreground walls and roofs. Every reached 32-unit cell is tested, even
when --step subsamples frame cameras. Its tolerance is zero.
frame_black_share counts all unpainted and pure-black frame pixels.
void_share retains the older unpainted and specified-filler diagnostic.
near_black_share uses RGB channels <= 8, for comparison with tour captures.
All shares are fractions, and region boxes are half-open game-pixel boxes.
--fixed selects an archive; --retail-art uses pristine .bak art and physics.
--arrival X Y Z overrides the LV arrival or the first retail teleport target.
"""

import argparse
import ast
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import time

import numpy as np
from PIL import Image, ImageDraw

import item_sorter as IS
from exact_reach import (ExactReach, SI_SEA, AVATAR_BODY,
                         FLG_CONTAINED, FLG_EQUIPPED)
from map_preview import GlobReader, expand_globs
from parse_typeflag import load_typeflag
from shape_viewer import PALETTE_FILE, load_palette
from u8_map import MapArchive
from vignette_paint import BUILD, STATIC, Painter

SRC = Path(__file__).resolve().parent
W, H = 640, 400
FILLERS = {(564, 2), (35, 10)}
OBJECT_ID_CAP = 32500
NEAR_BLACK = 8
DEFAULT_OUT = '/tmp/claude-1000/audits'
VALIDATION_IDS = {
    9: ('m09-14', 'm09-16', 'm09-17'),
    10: ('m10b-52', 'm10b-64'),
    11: ('m11-49',),
    13: ('m13-02', 'm13-03'),
    17: ('m17-01', 'm17-11'),
    18: ('m18-12', 'm18-15', 'm18-16'),
}


def test_declarations(filename, names):
    """Load named declarations without importing a script's test execution.

    The source is trusted repository Python. Only named functions and literal
    assignments are selected; all other top-level statements stay unexecuted.
    """
    path = SRC / filename
    tree = ast.parse(path.read_text(), filename=str(path))
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id in names for t in node.targets):
            ast.literal_eval(node.value)
            nodes.append(node)
    found = {n.name if isinstance(n, ast.FunctionDef) else n.targets[0].id
             for n in nodes}
    if found != set(names):
        raise ValueError(f'{path}: missing declarations {set(names) - found}')
    return compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec')


def reachable(mapnum, raw, arrival=None, typeflag=None):
    """Reuse the dry flood and arrival coordinates from the existing test."""
    ns = dict(ExactReach=ExactReach, SI_SEA=SI_SEA,
              expand_globs=expand_globs, gr=GlobReader(), DRY_ITEMS={},
              shapes=load_typeflag(str(typeflag or Path(BUILD) / 'TYPEFLAG.DAT')))
    exec(test_declarations('test_monster_eggs.py',
                          {'dry_flood', 'ARRIVAL', 'FLOOD_STEP'}), ns)
    if not raw:
        return [], None
    if arrival is None:
        arrival = ns['ARRIVAL'].get(mapnum)
    if arrival is None:
        pad = next((i for i in raw if i.is_teleport_target), None)
        if pad is None:
            raise ValueError(f'map {mapnum}: no default arrival; use --arrival X Y Z')
        arrival = (pad.x, pad.y, pad.z)
    ns['ARRIVAL'][mapnum] = tuple(arrival)
    er, reach = ns['dry_flood'](mapnum, raw)
    cells = [(int(er.x_of(i)), int(er.y_of(j)), int(z))
             for z, mask in reach.items() for i, j in zip(*np.nonzero(mask))]
    if not cells:
        raise ValueError(f'map {mapnum}: arrival flood reached no cells')
    return cells, tuple(arrival)


def camera(x, y, z):
    """GameMapGump camera origin, with CameraProcess's z offset of 20."""
    return IS._div(x - y, 4) - W // 2, IS._div(x + y, 8) - z - 20 - H // 2


class Scene:
    """Built records in engine chunk order, with cached sprite bounds."""

    def __init__(self, mapnum, fixed=None, retail_art=False):
        self.fixed = Path(fixed or Path(BUILD) / 'FIXED.DAT')
        def art(name):
            if not retail_art:
                return Path(BUILD) / name
            bak = Path(STATIC) / (name + '.bak')
            return bak if bak.exists() else Path(STATIC) / name
        self.typeflag = art('TYPEFLAG.DAT')
        self.shapes = art('U8SHAPES.FLX')
        self.anim = art('ANIM.DAT')
        self.painter = Painter(typeflag=str(self.typeflag), shapes=str(self.shapes))
        self.painter.info = lru_cache(maxsize=None)(self.painter.info)
        self.raw = MapArchive(str(self.fixed)).get_map_items(mapnum)
        gr = GlobReader()
        # CurrentMap::loadItems appends fixed records; GlobEgg appends its
        # temporary tiles after those records. Preserve that order per chunk.
        records = [i for i in self.raw if not i.is_glob_egg] + [
            g for i in self.raw if i.is_glob_egg
            for g in gr.glob_to_items(i.quality, i.x, i.y, i.z)]
        expanded_count = len(expand_globs(self.raw, gr))
        self.record_counts = dict(
            fixed_records=len(self.raw), items_after_glob_expansion=expanded_count,
            object_id_cap=OBJECT_ID_CAP,
            fixed_cap_share=len(self.raw) / OBJECT_ID_CAP,
            fixed_headroom=OBJECT_ID_CAP - len(self.raw),
            expanded_cap_share=expanded_count / OBJECT_ID_CAP,
            expanded_headroom=OBJECT_ID_CAP - expanded_count)
        self.records = [i for i in records
                        if not i.flags & (FLG_CONTAINED | FLG_EQUIPPED |
                                          IS.FLG_INVISIBLE)]
        self.records.sort(key=lambda i: (i.y // IS.CHUNK, i.x // IS.CHUNK))
        self.items, self.sprites = [], []
        for i in self.records:
            if self.painter.info(i.shape)['editor']:
                continue
            si = self.painter._make(i, 0, 0)
            if si is not None:
                self.items.append(vars(i).copy())
                self.sprites.append(si)
        self.rects = np.array([s.sr for s in self.sprites], dtype=np.int32).reshape(-1, 4)
        self.roofs = [i for i in self.records if self.painter.info(i.shape)['roof']]
        self.roof_chunks = defaultdict(list)
        for i in self.roofs:
            inf = self.painter.info(i.shape)
            xd, yd = ((inf['yd'], inf['xd']) if i.flags & IS.FLG_FLIPPED
                      else (inf['xd'], inf['yd']))
            # A camera's 64-square box can overlap a roof in these chunks.
            for cx in range((i.x-xd+1)//IS.CHUNK, (i.x+63)//IS.CHUNK+1):
                for cy in range((i.y-yd+1)//IS.CHUNK, (i.y+63)//IS.CHUNK+1):
                    self.roof_chunks[cx, cy].append(i)
        self.palette = np.array(load_palette(PALETTE_FILE), dtype=np.uint8)
        self.black_indices = (self.palette == 0).all(1)
        self.near_indices = (self.palette <= NEAR_BLACK).all(1)
        self.chunk_cache = {}

    def roof(self, spot):
        roofs = self.roof_chunks.get((spot[0]//IS.CHUNK, spot[1]//IS.CHUNK), ())
        return self.painter.roof_z(roofs, *spot)

    def select(self, rect, roof=None):
        l, t, r, b = self.rects.T
        ids = np.flatnonzero((l < rect[2]) & (r > rect[0]) &
                             (t < rect[3]) & (b > rect[1]))
        return [int(k) for k in ids if roof is None or
                self.items[k]['z'] < roof or self.sprites[k].draw]

    def chunk(self, key):
        """Sorted scene and camera-union bounds for (chunk x, y, z, roof)."""
        if key not in self.chunk_cache:
            cx, cy, z, roof = key
            x, y = cx * IS.CHUNK, cy * IS.CHUNK
            origins = [camera(a, b, z) for a in (x, x + IS.CHUNK - 1)
                       for b in (y, y + IS.CHUNK - 1)]
            left, top = min(a for a, b in origins), min(b for a, b in origins)
            right = max(a for a, b in origins) + W
            bottom = max(b for a, b in origins) + H
            rect = (left, top, right, bottom)
            ids = self.select(rect, roof)
            self.chunk_cache[key] = rect, ids
        return self.chunk_cache[key]

    def paint(self, spot, avatar=False):
        """Uncached reference frame, also used to validate atlas crops."""
        sx, sy = camera(*spot)
        ids = self.select((sx, sy, sx + W, sy + H), self.roof(spot))
        items = [self.items[k] for k in ids]
        if avatar:
            items.insert(0, dict(shape=1, frame=0, x=spot[0], y=spot[1], z=spot[2]))
        out, seq, own = self.painter.paint(items, sx, sy, W, H, owner=True)
        filler = np.array([(i['shape'], i['frame']) in FILLERS for i in items])
        fill = (own >= 0) & filler[np.maximum(own, 0)] if items else own >= 0
        return out, fill, seq, own


def walkable_chunk(task):
    """Probe floor paint under the bottom centre, without foreground cover.

    A floor surface is LAND, ROOF, or SOLID with its top at or below z.
    The half-open footprint must contain the actor's bottom centre. Only
    these surfaces contribute to the floor atlas. The top painted owner at
    that centre supplies the pixel and shape, including decorative 334.
    """
    key, spots = task
    scene = _SCENE
    z = key[2]
    centres = [(x - AVATAR_BODY[0] // 2, y - AVATAR_BODY[1] // 2)
               for x, y, _ in spots]
    pixels = [(IS._div(x, 4) - IS._div(y, 4),
               IS._div(x, 8) + IS._div(y, 8) - z) for x, y in centres]
    sx, sy = min(x for x, y in pixels) - 2, min(y for x, y in pixels) - 10
    right, bottom = max(x for x, y in pixels) + 3, max(y for x, y in pixels) + 11
    ids = [k for k in scene.select((sx, sy, right, bottom))
           if scene.sprites[k].z_top <= z and
           (scene.sprites[k].land or scene.sprites[k].roof or scene.sprites[k].solid)]
    items = [scene.items[k] for k in ids]
    out, _, own = scene.painter.paint(items, sx, sy, right-sx, bottom-sy, owner=True)
    rows = []
    for spot, (mx, my), (px, py) in zip(spots, centres, pixels):
        supports = [scene.sprites[k] for k in ids
                    if scene.sprites[k].x_left < mx <= scene.sprites[k].x and
                    scene.sprites[k].y_far < my <= scene.sprites[k].y]
        top = max((s.z_top for s in supports if s.z_top >= z-8), default=z)
        # LAND may lie up to eight units below the actor's feet.
        yy, xx = py + z - top - sy, px - sx
        owner = int(own[yy, xx])
        item = items[owner] if owner >= 0 else None
        index = int(out[yy, xx])
        specified = bool(item and ((item['shape'], item['frame']) in FILLERS
                                  or item['shape'] == 334))
        black = index < 0 or bool(scene.black_indices[max(index, 0)]) or specified
        rows.append(dict(x=spot[0], y=spot[1], z=z, walkable_black=black,
                         floor_shape=item['shape'] if item else None,
                         floor_frame=item['frame'] if item else None,
                         floor_palette_index=index,
                         reason=('specified_black_floor' if specified else
                                 'unpainted_floor' if index < 0 else
                                 'black_floor_pixel' if black else 'drawn_floor')))
    return rows


def regions(mask, limit=5):
    """Largest four-connected components, exact row-run union and bounds."""
    if not mask.any():
        return []
    if mask.all():
        return [dict(pixels=int(mask.size), bbox=[0, 0, mask.shape[1], mask.shape[0]])]
    parent, stats, prev = [], [], []

    def root(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    # Row runs avoid a Python visit for every one of the 256,000 pixels.
    padded = np.pad(mask.astype(np.int8), ((0, 0), (1, 1)))
    edges = np.diff(padded, axis=1)
    for y, row in enumerate(edges):
        starts, ends = np.flatnonzero(row == 1), np.flatnonzero(row == -1)
        cur, j = [], 0
        for l, r in zip(starts.tolist(), ends.tolist()):
            k = len(parent)
            parent.append(k)
            stats.append([r - l, l, y, r, y + 1])
            while j < len(prev) and prev[j][1] <= l:
                j += 1
            q = j
            while q < len(prev) and prev[q][0] < r:
                other = root(prev[q][2])
                if other != k:
                    parent[other] = k
                    a, b = stats[k], stats[other]
                    a[:] = [a[0] + b[0], min(a[1], b[1]), min(a[2], b[2]),
                            max(a[3], b[3]), max(a[4], b[4])]
                q += 1
            cur.append((l, r, k))
        prev = cur
    result = sorted((s for k, s in enumerate(stats) if parent[k] == k), reverse=True)
    return [dict(pixels=s[0], bbox=s[1:]) for s in result[:limit]]


def measures(scene, out, filler):
    painted = out >= 0
    black = painted & scene.black_indices[np.maximum(out, 0)]
    void = ~painted | (black & filler)
    return dict(void_share=float(void.mean()),
                unpainted_share=float((~painted).mean()),
                filler_black_share=float((black & filler).mean()),
                other_black_share=float((black & ~filler).mean()),
                black_share=float((~painted | black).mean()),
                frame_black_share=float((~painted | black).mean()),
                near_black_share=float((~painted | scene.near_indices[
                    np.maximum(out, 0)]).mean()),
                regions=regions(void))


_SCENE = None


def void_chunk(task):
    key, spots = task
    scene = _SCENE
    (sx, sy, right, bottom), ids = scene.chunk(key)
    items = [scene.items[k] for k in ids]
    out, seq, own = scene.painter.paint(items, sx, sy, right - sx, bottom - sy,
                                       owner=True)
    fillers = np.array([(i['shape'], i['frame']) in FILLERS for i in items])
    fill = (own >= 0) & fillers[np.maximum(own, 0)] if items else own >= 0
    rows = []
    for spot in spots:
        x, y = camera(*spot)
        sub = out[y - sy:y - sy + H, x - sx:x - sx + W]
        fsub = fill[y - sy:y - sy + H, x - sx:x - sx + W]
        rows.append(dict(x=spot[0], y=spot[1], z=spot[2],
                         **measures(scene, sub, fsub)))
    # A dependency pointing forward in final paint order identifies a cycle.
    # Such chunks use the original per-camera painter throughout.
    cycle = any(d.order > si.order for si in seq for d in si.depends)
    # Check the first, central, and final camera against the single-frame
    # path as well, recording every pixel discrepancy without a tolerance.
    mismatch = fill_mismatch = 0
    samples = sorted({0, len(spots)//2, len(spots)-1})
    for index in samples:
        spot = spots[index]
        direct, direct_fill, _, _ = scene.paint(spot)
        x, y = camera(*spot)
        mismatch += int(np.count_nonzero(direct != out[y-sy:y-sy+H, x-sx:x-sx+W]))
        fill_mismatch += int(np.count_nonzero(direct_fill != fill[y-sy:y-sy+H, x-sx:x-sx+W]))
    if mismatch or fill_mismatch or cycle:
        # Exact per-camera rendering for a chunk whose cycle changes the
        # order under the larger clip. Preserve the measured discrepancy.
        rows = [dict(x=p[0], y=p[1], z=p[2], **measures(scene, *scene.paint(p)[:2]))
                for p in spots]
    return rows, dict(key=list(key), samples=len(samples), pixels=mismatch,
                      filler_pixels=fill_mismatch, cycle=cycle)


def groups(scene, cells, step):
    result = defaultdict(list)
    for p in cells:
        if (p[0] - 31) % step or (p[1] - 31) % step:
            continue
        result[(p[0] // IS.CHUNK, p[1] // IS.CHUNK, p[2], scene.roof(p))].append(p)
    return sorted(result.items(), key=lambda t: (t[0][:3], t[0][3] or -1))


def workers():
    return max(1, min(12, (os.cpu_count() or 2) - 1))


def parallel(fn, tasks, count):
    with ProcessPoolExecutor(max_workers=count,
                             mp_context=multiprocessing.get_context('fork')) as pool:
        yield from pool.map(fn, tasks, chunksize=1)


def heatmap(rows, field, path, step, title):
    xs, ys = [r['x'] for r in rows], [r['y'] for r in rows]
    x0, y0 = min(xs), min(ys)
    grid = np.full(((max(ys) - y0) // step + 1,
                    (max(xs) - x0) // step + 1), np.nan)
    for r in rows:
        i, j = (r['y'] - y0) // step, (r['x'] - x0) // step
        v = r[field]
        grid[i, j] = v if np.isnan(grid[i, j]) else max(grid[i, j], v)
    v = np.nan_to_num(grid)
    rgb = np.stack((255 * v, 210 * (1 - v), np.full_like(v, 45)), -1).astype('uint8')
    rgb[np.isnan(grid)] = (24, 24, 30)
    scale = max(1, min(4, 1200 // max(grid.shape)))
    img = Image.fromarray(rgb).resize((grid.shape[1]*scale, grid.shape[0]*scale),
                                     Image.Resampling.NEAREST)
    canvas = Image.new('RGB', (max(img.width, 640), img.height + 60), (24, 24, 30))
    canvas.paste(img, (0, 60))
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 6), title, fill='white')
    draw.text((8, 23), f'x east, y south; origin ({x0},{y0}); step {step}; '
              'worst level per cell', fill='white')
    draw.text((8, 40), 'Green 0%, red 100%; dark = unsampled or unreachable', fill='white')
    canvas.save(path)


def provenance(scene=None):
    paths = ([scene.fixed, scene.shapes, scene.typeflag, scene.anim] if scene else
             [Path(BUILD) / n for n in ('FIXED.DAT', 'U8SHAPES.FLX',
                                        'TYPEFLAG.DAT', 'ANIM.DAT')])
    paths += [Path(PALETTE_FILE), SRC / 'test_monster_eggs.py',
              SRC / 'test_route_reach.py',
              (Path(BUILD) / 'GLOB.FLX' if (Path(BUILD) / 'GLOB.FLX').exists()
               else Path(STATIC) / 'GLOB.FLX'),
              SRC / 'void_audit.py', SRC / 'avatar_visibility.py',
              SRC / 'exact_reach.py', SRC / 'item_sorter.py', SRC / 'vignette_paint.py']
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=1, allow_nan=False) + '\n')


def distribution(values):
    """Fractional distribution with explicit empty-map results."""
    a = np.asarray(values, dtype=float)
    if not len(a):
        return dict.fromkeys(('min', 'mean', 'p05', 'median', 'p95', 'max'))
    return dict(zip(('min', 'mean', 'p05', 'median', 'p95', 'max'),
                    map(float, (a.min(), a.mean(), *np.percentile(a, [5, 50, 95]), a.max()))))


def validation_stops(mapnum, tour):
    wanted = set(VALIDATION_IDS.get(mapnum, ()))
    for path in sorted(Path(tour).glob('*/stops.json')):
        for s in json.loads(path.read_text()):
            if s['id'] in wanted:
                yield s, path.parent / (s['id'] + '.png')


def validate(scene, mapnum, tour, outdir):
    rows = []
    for stop, capture in validation_stops(mapnum, tour):
        spot = tuple(stop[k] for k in ('x', 'y', 'z'))
        out, fill, _, _ = scene.paint(spot, avatar=True)
        cap = np.asarray(Image.open(capture).convert('RGB'))
        if cap.shape != (H, W, 3):
            raise ValueError(f'{capture}: expected 640x400 game pixels')
        row = dict(id=stop['id'], map=mapnum, x=spot[0], y=spot[1], z=spot[2],
                   **measures(scene, out, fill))
        row['capture_near_black_share'] = float((cap.max(2) <= NEAR_BLACK).mean())
        row['black_delta_pp'] = 100*(row['black_share'] - row['capture_near_black_share'])
        row['near_black_delta_pp'] = 100*(row['near_black_share'] - row['capture_near_black_share'])
        rows.append(row)
        rgb = scene.palette[np.maximum(out, 0)]
        Image.fromarray(np.concatenate((cap, rgb), axis=1)).save(
            outdir / f"{stop['id']}-void-validation.png")
    if len(rows) != len(VALIDATION_IDS[mapnum]):
        raise ValueError(f'map {mapnum}: missing tour validation stops')
    write_json(outdir / f'void-map{mapnum:02d}-validation.json', rows)
    return rows


def arguments(description):
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument('map', type=int, metavar='MAP')
    ap.add_argument('--fixed', type=Path, default=Path(BUILD) / 'FIXED.DAT')
    ap.add_argument('--retail-art', action='store_true', help='use pristine .bak art and physics')
    ap.add_argument('--arrival', type=int, nargs=3, metavar=('X', 'Y', 'Z'))
    ap.add_argument('--step', type=int, default=32, help='sample spacing, multiple of 32')
    ap.add_argument('--out', type=Path, default=Path(DEFAULT_OUT))
    ap.add_argument('--workers', type=int, default=workers())
    ap.add_argument('--validate-tour', type=Path, help='also compare recorded tour stops')
    args = ap.parse_args()
    if not 0 <= args.map < 256:
        ap.error('MAP must be in 0..255')
    if args.step < 32 or args.step % 32 or args.workers < 1:
        ap.error('--step must be a positive multiple of 32; --workers must be positive')
    if not args.fixed.is_file():
        ap.error(f'FIXED archive does not exist: {args.fixed}')
    if args.validate_tour and args.map not in VALIDATION_IDS:
        ap.error('no tour-validation stops for this map')
    args.out.mkdir(parents=True, exist_ok=True)
    return args


def main():
    args = arguments(__doc__.splitlines()[0])
    start = time.monotonic()
    global _SCENE
    _SCENE = Scene(args.map, args.fixed, args.retail_art)
    cells, arrival = reachable(args.map, _SCENE.raw, args.arrival, _SCENE.typeflag)
    tasks = groups(_SCENE, cells, args.step)
    print(f'map {args.map}: {len(cells)} reached; {sum(len(s) for k,s in tasks)} '
          f'sampled; {len(tasks)} chunk scenes; {args.workers} workers', flush=True)
    rows, checks = [], []
    for batch, check in parallel(void_chunk, tasks, args.workers):
        rows.extend(batch)
        checks.append(check)
    floor_rows = [r for batch in parallel(walkable_chunk, groups(_SCENE, cells, 32),
                                          args.workers) for r in batch]
    floor_rows.sort(key=lambda r: (not r['walkable_black'], r['x'], r['y'], r['z']))
    floors = {(r['x'], r['y'], r['z']): r for r in floor_rows}
    for row in rows:
        row.update({k: v for k, v in floors[row['x'], row['y'], row['z']].items()
                    if k not in ('x', 'y', 'z')})
    rows.sort(key=lambda r: (r['x'], r['y'], r['z']))
    ranked = sorted(rows, key=lambda r: (-r['frame_black_share'], r['x'], r['y'], r['z']))
    shares = np.array([r['void_share'] for r in rows])
    frame_shares = np.array([r['frame_black_share'] for r in rows])
    black_count = sum(r['walkable_black'] for r in floor_rows)
    summary = dict(cells=len(rows), reachable_cells=len(cells),
                   status='measured' if cells else 'empty_map',
                   record_counts=_SCENE.record_counts,
                   walkable_black_cells=black_count,
                   walkable_black_share=black_count / len(cells) if cells else None,
                   walkable_black_tolerance=0,
                   walkable_black_pass=black_count == 0 if cells else None,
                   frame_black_share=distribution([r['frame_black_share'] for r in rows]),
                   mean_void_share=float(shares.mean()) if len(shares) else None,
                   median_void_share=float(np.median(shares)) if len(shares) else None,
                   max_void_share=float(shares.max()) if len(shares) else None,
                   frames_above_10_percent=int((frame_shares > .1).sum()),
                   void_frames_above_10_percent=int((shares > .1).sum()),
                   atlas_fallback_chunks=sum(bool(c['pixels'] or c['filler_pixels']
                                                  or c['cycle']) for c in checks))
    result = dict(map=args.map, step=args.step, arrival=arrival, frame=[W, H],
                  camera_z_offset=20, shares='fractions', provenance=provenance(_SCENE),
                  walkable_black_step=32,
                  summary=summary, cells=rows, atlas_checks=checks)
    if rows:
        heatmap(rows, 'frame_black_share', args.out / f'void-map{args.map:02d}.png', args.step,
                f'Map {args.map}: FRAME BLACK SHARE')
        heatmap(floor_rows, 'walkable_black', args.out / f'void-map{args.map:02d}-walkable.png',
                32, f'Map {args.map}: WALKABLE BLACK (tolerance 0)')
    write_json(args.out / f'void-map{args.map:02d}.json', result)
    write_json(args.out / f'void-map{args.map:02d}-walkable.json', floor_rows)
    with (args.out / f'void-map{args.map:02d}-ranked.tsv').open('w') as f:
        f.write('rank\tx\ty\tz\twalkable_black\tframe_black_percent\tvoid_percent\tlargest_regions\n')
        for k, r in enumerate(ranked, 1):
            f.write(f"{k}\t{r['x']}\t{r['y']}\t{r['z']}\t{int(r['walkable_black'])}"
                    f"\t{100*r['frame_black_share']:.3f}\t{100*r['void_share']:.3f}"
                    f"\t{json.dumps(r['regions'])}\n")
    with (args.out / f'void-map{args.map:02d}-walkable-ranked.tsv').open('w') as f:
        f.write('rank\tx\ty\tz\twalkable_black\tframe_black_percent\tfloor_shape\tfloor_frame\treason\n')
        frames = {(r['x'], r['y'], r['z']): r for r in rows}
        for k, r in enumerate(floor_rows, 1):
            frame = frames.get((r['x'], r['y'], r['z']))
            share = f"{100*frame['frame_black_share']:.3f}" if frame else ''
            f.write(f"{k}\t{r['x']}\t{r['y']}\t{r['z']}\t{int(r['walkable_black'])}"
                    f"\t{share}\t{r['floor_shape']}\t{r['floor_frame']}\t{r['reason']}\n")
    if args.validate_tour:
        validate(_SCENE, args.map, args.validate_tour, args.out)
    summary['elapsed_seconds'] = round(time.monotonic() - start, 2)
    write_json(args.out / f'void-map{args.map:02d}-summary.json', summary)
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""build_map_viewer.py -- walkable HTML map viewer for the Lost Vale maps.

Renders each LV map from the BUILT FIXED.DAT (glob eggs expanded) as an
isometric tile pyramid at game scale and writes one self-contained viewer
page per map (viewer.html is the template), plus an index page.

Rendering reuses the map-populator toolchain rather than re-implementing it:
  * u8_map.MapArchive reads FIXED.DAT; map_preview.expand_globs +
    glob_catalog.GlobReader expand the glob eggs exactly as
    GlobEgg::enterFastArea does;
  * item_sorter (the port of ScummVM's ItemSorter/SortItem) supplies the
    screen projection (SortItem::setBoxBounds: sx = x/4 - y/4,
    sy = x/8 + y/8 - z, C division per term), the shape-frame decoding
    (including shapes with > 500 frames such as the Avatar), and the
    pairwise below()/overlap()/occludes() rules; this script builds the
    engine's dependency graph over the whole map (a spatial hash replaces
    the engine's all-pairs loop, the candidate order is the engine's list
    order) and paints it depth-first as ItemSorter::PaintSortItem does;
  * SI_TRANSL shapes are painted as RenderSurface::PaintTranslucent paints
    them: palette indices that carry a U8XFormPal entry are blended
    (dst * (256 - a) + 256 * c) >> 8, every other index is opaque.

Not drawn, as GameMapGump does not draw them: SI_EDITOR shapes (eggs, the
497/498 rails), FLG_INVISIBLE and FLG_CONTAINED items. They go to the
overlay JSON instead, with map_pins.json's explanations where one matches.

Usage (artifacts and game data live in the main checkout, not a worktree):
    python3 tools/map_viewer/build_map_viewer.py \\
        --data-root ~/projects/lost-vale \\
        --out /tmp/claude-1000/gallery/maps  [--maps 10 11 ...]
"""

import argparse
import html
import json
import math
import os
import shutil
import sys
import time
from collections import defaultdict

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MP_SRC = os.path.join(REPO, 'agents', 'map-populator', 'src')
sys.path.insert(0, MP_SRC)

from u8_map import MapArchive                          # noqa: E402
from glob_catalog import GlobReader                    # noqa: E402
from map_preview import expand_globs                   # noqa: E402
from shape_viewer import load_palette                  # noqa: E402
import item_sorter as isort                            # noqa: E402

MAPS = (10, 11, 13, 17, 18, 9, 8, 39)
TILE = 512
LEVELS = 4            # downsample factors 1, 2, 4, 8
MARGIN = 160          # screen pixels around the placed content
CELL = 32             # height-surface grid, world units
FLG_CONTAINED = 0x0008
AVATAR_SHAPE = 1

# gfx/xform_blend.cpp U8XFormPal: palette index -> (r, g, b, a); the rest 0.
U8_XFORM = {8: (48, 48, 48, 80), 9: (24, 24, 24, 128), 10: (64, 64, 24, 64),
            11: (80, 80, 80, 80), 12: (180, 90, 0, 80), 13: (0, 0, 252, 40),
            14: (0, 0, 104, 40)}


# ---------------------------------------------------------------------------
# Paint order: ItemSorter::AddItem + PaintSortItem over the whole map
# ---------------------------------------------------------------------------

def paint_order(sorter, items):
    """Return the painted SortItems in paint order (occluded ones culled).

    SortItem::listLessThan orders the engine's list by (z, flat first) and
    inserts each new item before the first greater one, so the list is that
    key with ties in insertion order: `ins` records the insertion index."""
    ins = {}

    def key(s):
        return (s.z, 0 if s.flat else 1, ins[id(s)])

    order = sorted(range(len(items)),
                   key=lambda k: (items[k].y // isort.CHUNK,
                                  items[k].x // isort.CHUNK, k))
    B = 256
    buckets = defaultdict(list)
    made = []
    for n, k in enumerate(order):
        s = sorter._make(items[k], 0, 0)
        if s is None:
            continue
        ins[id(s)] = n
        bx0, by0 = s.sr[0] // B, s.sr[1] // B
        bx1, by1 = (s.sr[2] - 1) // B, (s.sr[3] - 1) // B
        cands = {}
        for bx in range(bx0, bx1 + 1):
            for by in range(by0, by1 + 1):
                for s2 in buckets.get((bx, by), ()):
                    cands[id(s2)] = s2
        for s2 in sorted(cands.values(), key=key):
            if s2.occluded:
                continue
            if isort.overlap(s, s2):
                if isort.below(s, s2):
                    if s2.occl and isort.occludes(s2, s):
                        s.occluded = True
                        break
                    isort._insert_sorted(s2.depends, s)
                elif s.occl and isort.occludes(s, s2):
                    s2.occluded = True
                else:
                    isort._insert_sorted(s.depends, s2)
        for bx in range(bx0, bx1 + 1):
            for by in range(by0, by1 + 1):
                buckets[(bx, by)].append(s)
        made.append(s)

    painted = []
    for root in sorted(made, key=key):
        if root.order != -1 or root.occluded:
            continue
        root.order = -2
        stack = [[root, 0]]
        while stack:
            top = stack[-1]
            si, i = top
            pushed = False
            while i < len(si.depends):
                d = si.depends[i]
                i += 1
                if d.order == -2:          # cycle: the engine stops here
                    i = len(si.depends)
                    break
                if d.order == -1 and not d.occluded:
                    top[1] = i
                    d.order = -2
                    stack.append([d, 0])
                    pushed = True
                    break
            if pushed:
                continue
            stack.pop()
            si.order = len(painted)
            painted.append(si)
    return painted


# ---------------------------------------------------------------------------
# Compositing
# ---------------------------------------------------------------------------

class Painter:
    def __init__(self, sorter, palette):
        self.sorter = sorter
        self.pal = np.array(palette, dtype=np.uint16)
        self.xf_on = np.zeros(256, dtype=bool)
        self.xf_rgb = np.zeros((256, 3), dtype=np.uint16)
        self.xf_ia = np.zeros(256, dtype=np.uint16)
        for i, (r, g, b, a) in U8_XFORM.items():
            self.xf_on[i] = True
            self.xf_rgb[i] = (r, g, b)
            self.xf_ia[i] = 256 - a
        self._cache = {}

    def frame_idx(self, shape, frame, flipped):
        key = (shape, frame, flipped)
        arr = self._cache.get(key)
        if arr is None:
            fr = self.sorter.frame(shape, frame)
            arr = np.frombuffer(bytes(fr['pixels']), dtype=np.uint8).reshape(
                fr['height'], fr['width'])
            if flipped:
                arr = arr[:, ::-1]
            self._cache[key] = arr
        return arr

    def blit(self, canvas, ox, oy, s):
        """Paint SortItem s onto canvas whose (0,0) is screen (ox, oy)."""
        idx = self.frame_idx(s.shape, s.frame, s.flipped)
        h, w = canvas.shape[:2]
        l, t = s.sr[0] - ox, s.sr[1] - oy
        x0, y0 = max(0, l), max(0, t)
        x1, y1 = min(w, l + idx.shape[1]), min(h, t + idx.shape[0])
        if x0 >= x1 or y0 >= y1:
            return
        sub = idx[y0 - t:y1 - t, x0 - l:x1 - l]
        dst = canvas[y0:y1, x0:x1]
        m = sub != 0xFF
        if s.trans:
            xm = m & self.xf_on[sub]
            om = m & ~xm
            dst[om] = self.pal[sub[om]]
            if xm.any():
                si = sub[xm]
                d = dst[xm].astype(np.uint32)
                v = (d * self.xf_ia[si][:, None] + 256 * self.xf_rgb[si]) >> 8
                dst[xm] = np.minimum(v, 255)
        else:
            dst[m] = self.pal[sub[m]]


def save_tile(img, path, fmt):
    if fmt == 'webp':
        img.save(path, 'WEBP', lossless=True, quality=60, method=4)
    else:
        img.save(path, 'PNG', optimize=True)


# ---------------------------------------------------------------------------
# Per-map data
# ---------------------------------------------------------------------------

def roof_hidden(sorter, painted):
    """Items GameMapGump would cut with the Avatar under each roof.

    CameraProcess::findRoof only counts an SI_ROOF item whose bottom is at
    or above the camera box's top, the subject's z + 20 + 16; the subject
    here is an Avatar on the lowest SI_LAND surface of each cell. Every item
    at or above that roof's z whose centre it covers is cut, unless SI_DRAW.
    Returns (set of id(SortItem) cut, set of the (cx, cy) cells a counted
    roof covers)."""
    def cells(s):
        for cx in range(s.x_left // CELL, (s.x - 1) // CELL + 1):
            for cy in range(s.y_far // CELL, (s.y - 1) // CELL + 1):
                yield cx, cy

    floor = {}
    for s in painted:
        if s.land and not s.roof:
            for k in cells(s):
                if k not in floor or s.z_top < floor[k]:
                    floor[k] = s.z_top
    roofz = {}
    for s in painted:
        if not s.roof:
            continue
        for k in cells(s):
            if s.z >= floor.get(k, 0) + 36 and (k not in roofz
                                                or s.z < roofz[k]):
                roofz[k] = s.z
    hidden = set()
    if not roofz:
        return hidden, set()
    for s in painted:
        if s.draw:
            continue
        cx = ((s.x + s.x_left) // 2) // CELL
        cy = ((s.y + s.y_far) // 2) // CELL
        rz = roofz.get((cx, cy))
        if rz is not None and s.z >= rz:
            hidden.add(id(s))
    return hidden, set(roofz)


def height_grid(sorter, items):
    """Walkable surface tops per CELL x CELL world cell: the z + zd of every
    SI_LAND or SI_SOLID item covering it, lowest four, 255 = none. Returned
    as an RGBA image (one level per channel) and its origin cell."""
    tops = defaultdict(set)
    for it in items:
        inf = sorter.info(it.shape)
        if not (inf['land'] or inf['solid']):
            continue
        top = min(254, it.z + inf['zd'])
        for cx in range((it.x - inf['xd']) // CELL, (it.x - 1) // CELL + 1):
            for cy in range((it.y - inf['yd']) // CELL, (it.y - 1) // CELL + 1):
                tops[(cx, cy)].add(top)
    if not tops:
        return None, 0, 0
    cxs = [k[0] for k in tops]
    cys = [k[1] for k in tops]
    gx0, gy0 = min(cxs), min(cys)
    gw, gh = max(cxs) - gx0 + 1, max(cys) - gy0 + 1
    arr = np.full((gh, gw, 4), 255, dtype=np.uint8)
    for (cx, cy), ts in tops.items():
        lv = sorted(ts)[:4]
        arr[cy - gy0, cx - gx0, :len(lv)] = lv
    return Image.fromarray(arr, 'RGBA'), gx0, gy0


def overlay_entries(sorter, overlay_items, pins):
    pin_by_pos = {}
    for p in pins:
        pin_by_pos[(p['shape'], p['x'], p['y'], p['z'])] = p
    out = []
    used = set()
    for it in overlay_items:
        q, n = it.quality, it.npcnum
        if it.shape == 500:
            kind = 'monster'
            label = f'monster egg: shape {q & 0x7FF}'
        elif it.shape == 508:
            if it.frame == 1:
                kind, label = 'tele_target', f'teleport arrival pad {q & 0xFF}'
            else:
                kind, label = 'teleporter', f'teleporter -> pad {q & 0xFF}'
        elif it.shape == 73:
            kind, label = 'egg', f'egg q{q} frame {it.frame}'
        else:
            kind = 'editor'
            label = f'editor-only shape {it.shape}'
        inf = sorter.info(it.shape)
        e = dict(k=kind, x=it.x, y=it.y, z=it.z, s=it.shape, f=it.frame,
                 q=q, n=n, label=label, w=inf['xd'], d=inf['yd'], h=inf['zd'])
        if it.shape == 73 or (it.shape == 508 and it.frame != 1):
            # Egg hatch box: x +/- 32 * xrange, y +/- 32 * yrange
            # (egg.h getXRange/getYRange, EggHatcherProcess range_mul)
            e['rx'] = ((n >> 4) & 0xF) * 32
            e['ry'] = (n & 0xF) * 32
        p = pin_by_pos.get((it.shape, it.x, it.y, it.z))
        if p:
            e['why'] = p['why']
            if p['kind'] == 'monster_trigger':
                e['k'] = 'trigger'
                e['label'] = f'monster trigger q{q}'
            used.add(id(p))
        out.append(e)
    for p in pins:
        if id(p) in used or 'CONTAINED' in p.get('why', ''):
            continue
        label = (f"NPC {p['npcnum']} start (shape {p['shape']})"
                 if p['kind'] == 'npc' else
                 f"{p['kind'].replace('_', ' ')}: shape {p['shape']}")
        out.append(dict(k='pin', x=p['x'], y=p['y'], z=p['z'], s=p['shape'],
                        f=p['frame'], q=p['quality'], n=p['npcnum'],
                        label=label, why=p.get('why', '')))
    return out


def build_map(mapnum, arch, globs, sorter, painter, pins, locs, title,
              out_dir, fmt):
    t0 = time.time()
    raw = arch.get_map_items(mapnum)
    items = expand_globs(raw, globs)
    drawable, overlay_items = [], []
    for it in items:
        if it.flags & FLG_CONTAINED:
            continue
        if sorter.info(it.shape)['editor'] or it.flags & isort.FLG_INVISIBLE:
            overlay_items.append(it)
        elif sorter.frame(it.shape, it.frame) is not None:
            drawable.append(it)
    painted = paint_order(sorter, drawable)
    t_sort = time.time() - t0

    minx = min(s.sr[0] for s in painted) - MARGIN
    miny = min(s.sr[1] for s in painted) - MARGIN
    maxx = max(s.sr[2] for s in painted) + MARGIN
    maxy = max(s.sr[3] for s in painted) + MARGIN
    ox = (minx // TILE) * TILE
    oy = (miny // TILE) * TILE
    ntx = -(-(maxx - ox) // TILE)
    nty = -(-(maxy - oy) // TILE)

    tile_items = defaultdict(list)
    for s in painted:
        for tx in range((s.sr[0] - ox) // TILE, (s.sr[2] - 1 - ox) // TILE + 1):
            for ty in range((s.sr[1] - oy) // TILE,
                            (s.sr[3] - 1 - oy) // TILE + 1):
                tile_items[(tx, ty)].append(s)

    hidden, roof_cells = roof_hidden(sorter, painted)
    roof_tiles = set()
    for s in painted:
        if id(s) in hidden:
            for tx in range((s.sr[0] - ox) // TILE,
                            (s.sr[2] - 1 - ox) // TILE + 1):
                for ty in range((s.sr[1] - oy) // TILE,
                                (s.sr[3] - 1 - oy) // TILE + 1):
                    roof_tiles.add((tx, ty))

    mdir = os.path.join(out_dir, f'map{mapnum:02d}')
    if os.path.isdir(mdir):
        shutil.rmtree(mdir)
    ext = fmt
    have = {'base': [set() for _ in range(LEVELS)],
            'noroof': [set() for _ in range(LEVELS)]}

    def tile_path(layer, lv, tx, ty):
        return os.path.join(mdir, layer, str(lv), f'{tx}_{ty}.{ext}')

    def render(layer, keys, skip):
        os.makedirs(os.path.join(mdir, layer, '0'), exist_ok=True)
        for (tx, ty) in keys:
            canvas = np.zeros((TILE, TILE, 3), dtype=np.uint16)
            n = 0
            for s in sorted(tile_items[(tx, ty)], key=lambda s: s.order):
                if skip and id(s) in skip:
                    continue
                painter.blit(canvas, ox + tx * TILE, oy + ty * TILE, s)
                n += 1
            if n == 0 and layer == 'base':
                continue
            save_tile(Image.fromarray(canvas.astype(np.uint8), 'RGB'),
                      tile_path(layer, 0, tx, ty), fmt)
            have[layer][0].add((tx, ty))

    render('base', sorted(tile_items), None)
    render('noroof', sorted(roof_tiles), hidden)
    t_tiles = time.time() - t0 - t_sort

    # Zoom-out levels: 2x2 children -> one tile, box-filtered.
    for lv in range(1, LEVELS):
        for layer in ('base', 'noroof'):
            parents = {(tx // 2, ty // 2) for tx, ty in have[layer][lv - 1]}
            if not parents:
                continue
            os.makedirs(os.path.join(mdir, layer, str(lv)), exist_ok=True)
            for px, py in sorted(parents):
                big = Image.new('RGB', (TILE * 2, TILE * 2))
                for dx in (0, 1):
                    for dy in (0, 1):
                        c = (px * 2 + dx, py * 2 + dy)
                        src = None
                        if c in have[layer][lv - 1]:
                            src = tile_path(layer, lv - 1, *c)
                        elif layer == 'noroof' and c in have['base'][lv - 1]:
                            src = tile_path('base', lv - 1, *c)
                        if src:
                            big.paste(Image.open(src), (dx * TILE, dy * TILE))
                save_tile(big.resize((TILE, TILE), Image.BOX),
                          tile_path(layer, lv, px, py), fmt)
                have[layer][lv].add((px, py))

    # Thumbnail: the coarsest level stitched and fitted into 480 px.
    lv = LEVELS - 1
    f = 2 ** lv
    tw, th = -(-ntx // f), -(-nty // f)
    full = Image.new('RGB', (tw * TILE, th * TILE))
    for tx, ty in have['base'][lv]:
        full.paste(Image.open(tile_path('base', lv, tx, ty)),
                   (tx * TILE, ty * TILE))
    full = full.crop((0, 0, max(1, (maxx - ox) // f), max(1, (maxy - oy) // f)))
    lit = full.convert('L').point(lambda v: 255 if v > 12 else 0).getbbox()
    if lit:                      # void-floor plates and margins are black
        full = full.crop((max(0, lit[0] - 8), max(0, lit[1] - 8),
                          min(full.width, lit[2] + 8),
                          min(full.height, lit[3] + 8)))
    full.thumbnail((480, 480), Image.LANCZOS)
    full.save(os.path.join(mdir, 'thumb.png'), optimize=True)

    hgrid, gx0, gy0 = height_grid(sorter, drawable)
    if hgrid is not None:
        hgrid.save(os.path.join(mdir, 'heights.png'), optimize=True)

    ovl = overlay_entries(sorter, overlay_items, pins)
    cfg = dict(
        map=mapnum, title=title, tile=TILE, ext=ext, levels=LEVELS,
        origin=[ox, oy], ntiles=[ntx, nty],
        bounds=[minx, miny, maxx, maxy],
        tiles={layer: [sorted(f'{a}_{b}' for a, b in have[layer][lv])
                       for lv in range(LEVELS)] for layer in have},
        roofs=bool(hidden),
        roofcells=[v for k in sorted(roof_cells) for v in k],
        heights=dict(cell=CELL, gx0=gx0, gy0=gy0,
                     w=hgrid.width if hgrid else 0,
                     h=hgrid.height if hgrid else 0),
        overlay=ovl, locations=locs,
        stats=dict(items=len(items), raw=len(raw), drawn=len(painted),
                   culled=len(drawable) - len(painted),
                   overlay=len(overlay_items)),
    )
    t_total = time.time() - t0
    cfg['stats'].update(sort_s=round(t_sort, 1), tiles_s=round(t_tiles, 1),
                        total_s=round(t_total, 1))
    return cfg


# ---------------------------------------------------------------------------
# Avatar sprite sheet (shape 1: stand 0-7, walk/run frames from ANIM.DAT)
# ---------------------------------------------------------------------------

def avatar_assets(anim_path, painter, out_dir):
    import struct
    d = open(anim_path, 'rb').read()
    off = struct.unpack_from('<I', d, 4 * AVATAR_SHAPE)[0]
    acts = {}
    for name, act in (('walk', 0), ('run', 1), ('stand', 2)):
        ao = struct.unpack_from('<I', d, off + act * 4)[0]
        size, rep = d[ao], d[ao + 2] & 0xF
        p = ao + 4
        dirs = []
        for _ in range(8):
            fr = []
            for _ in range(size):
                b = d[p:p + 6]
                p += 6
                fr.append([b[0] + ((b[1] & 7) << 8),
                           struct.unpack('b', b[4:5])[0],
                           bool(b[5] & 0x20)])
            dirs.append(fr)
        acts[name] = dict(repeat=rep, dirs=dirs)
    frames = sorted({f[0] for a in acts.values() for dr in a['dirs'] for f in dr})
    cells, x = {}, 0
    imgs = []
    for fn in frames:
        fr = painter.sorter.frame(AVATAR_SHAPE, fn)
        idx = painter.frame_idx(AVATAR_SHAPE, fn, False)
        rgba = np.zeros(idx.shape + (4,), dtype=np.uint8)
        m = idx != 0xFF
        rgba[m, :3] = painter.pal[idx[m]].astype(np.uint8)
        rgba[m, 3] = 255
        imgs.append((x, Image.fromarray(rgba, 'RGBA')))
        cells[fn] = [x, 0, fr['width'], fr['height'], fr['xoff'], fr['yoff']]
        x += fr['width'] + 1
    sheet = Image.new('RGBA', (x, max(im.height for _, im in imgs)))
    for px, im in imgs:
        sheet.paste(im, (px, 0))
    sheet.save(os.path.join(out_dir, 'avatar.png'), optimize=True)
    return dict(cells=cells, actions=acts)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def write_pages(out_dir, cfgs, avatar, titles):
    tpl = open(os.path.join(HERE, 'viewer.html'), encoding='utf-8').read()
    nav = [dict(map=c['map'], title=c['title']) for c in cfgs]
    for c in cfgs:
        page = (tpl.replace('__TITLE__', html.escape(
                    f"Map {c['map']} - {c['title']}"))
                .replace('/*__CONFIG__*/null', json.dumps(c, separators=(',', ':')))
                .replace('/*__AVATAR__*/null', json.dumps(avatar, separators=(',', ':')))
                .replace('/*__NAV__*/null', json.dumps(nav)))
        with open(os.path.join(out_dir, f"map{c['map']:02d}.html"), 'w',
                  encoding='utf-8') as fh:
            fh.write(page)

    cards = []
    for c in cfgs:
        st = c['stats']
        names = ', '.join(html.escape(l['name']) for l in c['locations'][:8])
        more = len(c['locations']) - 8
        if more > 0:
            names += f' and {more} more'
        cards.append(
            f'<a class="card" href="map{c["map"]:02d}.html">'
            f'<img src="map{c["map"]:02d}/thumb.png" alt="Map {c["map"]}">'
            f'<h2>Map {c["map"]} &mdash; {html.escape(c["title"])}</h2>'
            f'<p>{st["drawn"]} sprites drawn, {st["overlay"]} editor items '
            f'in the overlay. {names}</p></a>')
    page = INDEX_TPL.replace('__CARDS__', '\n'.join(cards))
    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(page)


INDEX_TPL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Lost Vale - walkable maps</title>
<style>
body{background:#111;color:#ddd;font:14px/1.4 system-ui,sans-serif;margin:0;padding:20px}
h1{font-size:22px;margin:0 0 4px} .sub{color:#999;margin:0 0 18px}
.grid{display:flex;flex-wrap:wrap;gap:16px}
.card{display:block;width:480px;background:#1b1b22;border:1px solid #333;
 border-radius:6px;padding:10px;color:#ddd;text-decoration:none}
.card:hover{border-color:#c9a14a}
.card img{display:block;max-width:100%;margin:0 auto;background:#000}
.card h2{font-size:16px;margin:8px 0 4px;color:#e8c872}
.card p{margin:0;color:#aaa;font-size:13px}
a{color:#e8c872}
</style></head><body>
<h1>Ultima 8: The Lost Vale &mdash; walkable maps</h1>
<p class="sub">Rendered from the built FIXED.DAT, U8SHAPES.FLX and TYPEFLAG.DAT
at game scale in the engine's paint order. Walk with WASD / arrow keys (Shift
runs), drag to pan, wheel to zoom. See <a href="README.txt">README.txt</a> for
how this was made and how it differs from ScummVM.</p>
<div class="grid">
__CARDS__
</div></body></html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--data-root', default=REPO,
                    help='checkout holding shared/build and shared/data')
    ap.add_argument('--out', required=True)
    ap.add_argument('--maps', type=int, nargs='+', default=list(MAPS))
    ap.add_argument('--format', choices=('png', 'webp'), default='webp')
    args = ap.parse_args()

    root = args.data_root
    build = os.path.join(root, 'shared', 'build')
    static = os.path.join(root, 'shared', 'data', 'u8-install', 'STATIC')
    for f in ('FIXED.DAT', 'U8SHAPES.FLX', 'TYPEFLAG.DAT', 'ANIM.DAT'):
        if not os.path.exists(os.path.join(build, f)):
            sys.exit(f'missing {build}/{f}: run tools/build_artifacts.sh there')
    os.makedirs(args.out, exist_ok=True)

    sorter = isort.ItemSorter(typeflag=os.path.join(build, 'TYPEFLAG.DAT'),
                              shapes=os.path.join(build, 'U8SHAPES.FLX'))
    painter = Painter(sorter, load_palette(os.path.join(static, 'U8PAL.PAL')))
    arch = MapArchive(os.path.join(build, 'FIXED.DAT'))
    glob_path = os.path.join(build, 'GLOB.FLX')
    globs = GlobReader(glob_path if os.path.exists(glob_path) else os.path.join(static, 'GLOB.FLX'))
    pins_all = json.load(open(os.path.join(MP_SRC, 'map_pins.json')))['maps']
    locdata = json.load(open(os.path.join(HERE, 'locations.json')))
    titles = locdata.get('titles', {})

    cfgs = []
    for m in args.maps:
        cfg = build_map(m, arch, globs, sorter, painter,
                        pins_all.get(str(m), []), locdata.get(str(m), []),
                        titles.get(str(m), f'Map {m}'), args.out, args.format)
        st = cfg['stats']
        print(f"map {m:2d}: {st['raw']} raw / {st['items']} expanded items, "
              f"{st['drawn']} drawn, {st['culled']} culled; "
              f"sort {st['sort_s']}s, tiles {st['tiles_s']}s, "
              f"total {st['total_s']}s; "
              f"{len(cfg['tiles']['base'][0])} base tiles, "
              f"{len(cfg['tiles']['noroof'][0])} roofs-off tiles", flush=True)
        cfgs.append(cfg)
    order = {m: i for i, m in enumerate(MAPS)}
    cfgs.sort(key=lambda c: order.get(c['map'], 99))

    avatar = avatar_assets(os.path.join(build, 'ANIM.DAT'), painter, args.out)
    write_pages(args.out, cfgs, avatar, titles)
    readme = os.path.join(HERE, 'README.txt')
    with open(readme, encoding='utf-8') as fh:
        text = fh.read()
    lines = ['', 'Last build (' + time.strftime('%Y-%m-%d %H:%M') + '):']
    for c in cfgs:
        st = c['stats']
        lines.append(f"  map {c['map']:2d}: {st['drawn']} sprites drawn, "
                     f"{st['culled']} occlusion-culled, render {st['total_s']}s")
    with open(os.path.join(args.out, 'README.txt'), 'w', encoding='utf-8') as fh:
        fh.write(text + '\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()

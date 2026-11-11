"""Shared phase 4 dressing, called after quest geometry and before void fill.

Site owns a private working list. pack() returns it and persists packed glob
rows and dressing provenance for the built-artifact structural checks.
No builder calls this API in slice 0. Set pieces reserve their entire box;
reserve() also accepts a footprint before the builder authors its contents.
"""
import ast
from collections import Counter, defaultdict
import copy
import json
import math
from pathlib import Path
import random

import dressing_metrics as dm
from glob_catalog import GlobReader
from item_sorter import ItemSorter, _Item, overlap, below, occludes, FLG_FLIPPED, FLG_INVISIBLE
from lv_furnish import cells_within_view, floor_cells
from map_preview import expand_globs
from quest_legs import leg_cells, LEGS
from u8_map import MapItem
import lv_globs
from lv_shapes import (SHAPE_RUBBLE_DECORATIVE, SHAPE_BONES_DECORATIVE_A,
                       SHAPE_BONES_DECORATIVE_B, SHAPE_CAVE_CREST_DECORATIVE)


def prefab_family(prefix):
    """Resolve appended IDs through the manifest, including packed slots."""
    return tuple(pin['id'] for name, pin in lv_globs.registry()['globs'].items()
                 if name.startswith(prefix))


HERE = Path(__file__).resolve().parent
ROCK_DRESSED = (395, 396, 398, 399, 400, 774, 953, 955, 958, 947, 956, 957)
ROCK_FUNGUS = (877, 881, 882, 1659, 956, 957, 395, 399)
# Retail riverbanks remain available outside Maps 10 and 13. Their cliff
# shores await the Map 13 mock approval (direction update cc50402).
SHORE_SE = (1547, 1543, 1551, 1548)
SHORE_NW = (1539, 1540, 1537, 1554)
LAVA_SEA = (2360, 2365, 2374, 802)
STARS = (2916, 2632)
GRASS_FOREST = (124, 125, 891, 1013, 1014, 13)
# The retail family stays stable for existing builders. Map slices opt into
# the appended safe copse family after their own placement and pin review.
GRASS_COPSE_NAMES = tuple(f'grass_wood_{k}' for k in range(4))

KIT_DEADWOOD = ((75, 1, 4), (56, 10, 3), (321, 5, 4), (322, 5, 4), (465, 17, 4), (57, 4, 1))
KIT_STONE = ((66, 5, 3), (152, 3, 3), (465, 17, 6), (782, 12, 2))
KIT_BONES = ((SHAPE_BONES_DECORATIVE_A, 2, 2), (SHAPE_BONES_DECORATIVE_B, 2, 2), (465, 17, 3), (322, 5, 2))
KIT_DECORATIVE = ((906, 4, 2), (907, 26, 2), (908, 12, 2), (909, 1, 2), (910, 9, 3), (905, 1, 2))
KIT_HALL = ((SHAPE_RUBBLE_DECORATIVE, 6, 3), (38, 4, 2), (47, 1, 2), (46, 1, 2), (910, 9, 3), (909, 1, 3))
KIT_YARD = ((149, 1, 2), (649, 3, 1), (321, 5, 3), (322, 5, 3), (465, 17, 4))
RAW_CEILING = {8: 6500, 9: 1800, 10: 20000, 11: 10000, 13: 7000, 17: 9500, 18: 2400, 39: 6000}
EXPANDED_PER_CELL = {9: 2.9, 10: 2.0, 11: 2.9, 13: 2.9, 17: 2.0, 18: 2.9}
BUDGET_BOX = {10: (3072, 1024, 22528, 30208), 17: (1664, 1024, 6912, 11264)}

MAP_TARGETS = {
    9: (8, .65, .05, .40), 10: (6, .50, .12, .30),
    11: (5, .45, .10, .40), 13: (5, .45, .15, .30),
    17: (8, .72, .15, .20), 18: (8, .65, .05, .40),
}


def map_targets(mapnum):
    if mapnum not in MAP_TARGETS: return {}
    density, material, bare, period = MAP_TARGETS[mapnum]
    return {'props.props_per_100': ('min',density), 'ground.top1': ('max',material),
            'props.bare_share': ('max',bare), 'repetition.period_excess': ('max',period)}


# An author can supply a more specific fallen form to set_piece().
BROKEN = {75: (56, 0), 66: (152, 0), 875: (905, 0), 149: (782, 0),
          235: (237, 0), 237: (235, 0), 38: (47, 0)}


def loosen_rows(pieces, mapnum, seed, broken=None):
    """Retain row counts, hash offsets, and replace one in four pieces.

    Unknown fallen forms raise, so an author can supply the right variant.
    Hand-authored irregular groups pass through unchanged.
    """
    pieces = copy.deepcopy(list(pieces))
    variants = dict(BROKEN, **{})
    variants.update(broken or {})
    moved = set()
    for axis in ('x', 'y'):
        rows = defaultdict(list)
        for i in pieces:
            rows[i.shape,i.z,getattr(i,axis)].append(i)
        other = 'y' if axis == 'x' else 'x'
        for (shape,z,coordinate), row in rows.items():
            if len(row) < 4: continue
            if shape not in variants: raise ValueError(f'row shape {shape} needs a broken variant')
            row.sort(key=lambda i:getattr(i,other))
            phase = random.Random(f'{seed}:{mapnum}:{shape}:{axis}:{coordinate}').randrange(4)
            for k,i in enumerate(row):
                if id(i) in moved: continue
                rng = random.Random(f'{seed}:{mapnum}:{i.x//32}:{i.y//32}:{shape}')
                setattr(i,axis,getattr(i,axis)+rng.choice((-64,-32,32,64)))
                if k%4 == phase: i.shape,i.frame = variants[shape]
                moved.add(id(i))
    return pieces


def _constants(filename, names):
    """Read literal test contracts without executing a test suite."""
    env = {}
    for node in ast.parse((HERE / filename).read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in names:
                # Only literal containers and names of preceding constants.
                if any(not isinstance(n, (ast.Expression, ast.Constant, ast.List, ast.Tuple,
                        ast.Dict, ast.Set, ast.Load, ast.Name, ast.UnaryOp, ast.USub))
                       for n in ast.walk(node.value)):
                    raise ValueError(f'nonliteral contract {filename}:{name}')
                env[name] = eval(compile(ast.Expression(node.value), filename, 'eval'),
                                 {'__builtins__': {}}, env)
    if set(names) != set(env):
        raise ValueError(f'missing contracts in {filename}: {set(names) - set(env)}')
    return env


def shot_windows(mapnum):
    floors = _constants('test_vignettes.py', {'FLOORS'})['FLOORS']
    rows = []
    for name, floor in floors.items():
        v = json.loads((HERE / 'vignettes' / f'{name}.json').read_text())
        if v['map'] != mapnum:
            continue
        ox, oy, oz = v['placement']['origin_world']
        cam = v['camera']
        rows.append(dict(name=name, floor=floor,
                         rect=(cam['sx0'] + ox // 4 - oy // 4,
                               cam['sy0'] + ox // 8 + oy // 8 - oz, *cam['crop'])))
    return rows


def box(it, sorter):
    inf = sorter.info(it.shape)
    xd, yd = inf['xd'], inf['yd']
    if it.flags & 0x20:
        xd, yd = yd, xd
    return (it.x - xd, it.y - yd, it.x, it.y, it.z, it.z + inf['zd'])


def xy_overlap(a, b, margin=0):
    return a[0] - margin < b[2] and b[0] < a[2] + margin and a[1] - margin < b[3] and b[1] < a[3] + margin


def cells32(b, margin=0):
    # Include a zero-width decorative footprint's containing cell.
    return {(x, y) for x in range((b[0] - margin) // 32, (b[2] + margin) // 32 + 1)
                   for y in range((b[1] - margin) // 32, (b[3] + margin) // 32 + 1)}


def paints_window(it, sorter, windows):
    b = box(it, sorter)
    x0, y0, x1, y1, z0, z1 = b
    bounds = (x0 // 4 - y1 // 4, x0 // 8 + y0 // 8 - z1,
              x1 // 4 - y0 // 4, x1 // 8 + y1 // 8 - z0)
    sprite = sorter._make(_Item(it.shape, it.frame, it.x, it.y, it.z, it.flags), 0, 0)
    if sprite is not None:
        bounds = (min(bounds[0], sprite.sr[0]), min(bounds[1], sprite.sr[1]),
                  max(bounds[2], sprite.sr[2]), max(bounds[3], sprite.sr[3]))
    if it.shape == SHAPE_CAVE_CREST_DECORATIVE:
        # Cropped variants keep their source canvas. Test the remaining
        # paint with the window margin. Transparent pixels permit clipping.
        import numpy as np
        mask = sorter.mask(sprite)
        yy, xx = np.where(mask)
        return any(bool(np.any((xx + sprite.sr[0] >= x - 16) &
                               (xx + sprite.sr[0] < x + w + 16) &
                               (yy + sprite.sr[1] >= y - 16) &
                               (yy + sprite.sr[1] < y + h + 16)))
                   for x, y, w, h in (r['rect'] for r in windows))
    return any(bounds[0] - 16 < x + w and bounds[2] + 16 > x and
               bounds[1] - 16 < y + h and bounds[3] + 16 > y
               for x, y, w, h in (r['rect'] for r in windows))


def _line_cells(points, margin):
    out = set()
    for a, b in zip(points, points[1:]):
        n = max(1, math.ceil(math.dist(a[:2], b[:2]) / 16))
        for k in range(n + 1):
            x, y = (round(a[i] + (b[i] - a[i]) * k / n) for i in (0, 1))
            out |= cells32((x, y, x, y), margin)
    return out


class Site:
    def __init__(self, mapnum, items, shapes, seed):
        self.mapnum, self.shapes, self.seed = mapnum, shapes, seed
        self.items = copy.deepcopy(items)
        # Map 39 keeps its 4,623 retail FIXED records as an exact prefix.
        self.protected_raw = {id(i) for i in self.items[:4623]} if mapnum == 39 else set()
        self.globs, self.sorter = GlobReader(), ItemSorter()
        self.windows = shot_windows(mapnum)
        self.mask = defaultdict(set)  # 32-unit cells -> reason strings
        self.solid_mask = defaultdict(set)
        self.reservations = []
        self.scripted = []
        self.added, self.swapped, self.seeds = [], [], []
        self.ledger = []
        self._packed = False
        self.floor_order = set()
        self._refresh()
        self.bands = leg_cells(mapnum, self.items, shapes)
        self.leg_mask = set()
        for band in self.bands.values():
            for x, y, z in band:
                self.leg_mask |= cells32((x - 16, y - 16, x + 16, y + 16), 64)
        self._exclusions()

    def _refresh(self):
        self.expanded = expand_globs(self.items, self.globs)
        self.src = dm.Source(fixed=False)
        self.src.globs = self.globs
        self.layers = dm.Layers(self.src, self.items)
        self.ground = self.layers.ground
        self.water_cells = {(i.x//128,i.y//128) for i in self.expanded if i.shape==347}
        self.spatial = defaultdict(list)
        self._crest_cover = {}
        if hasattr(self,'_surface_reach'): del self._surface_reach
        if hasattr(self,'_sky_cameras'): del self._sky_cameras
        for it in self.expanded:
            if it.flags & MapItem.FLG_CONTAINED:
                continue
            self._index(it)

    def _refresh_appended(self, pieces, *, indexed=False):
        """_refresh after loose records were appended to self.items, done
        incrementally where that is exact. A piece that is not a glob egg,
        ground, void or water cannot change glob expansion, ground or
        water_cells; expand_globs passes it through as the same object; and
        appended pieces index after everything already in each spatial cell,
        where a full rebuild would put them. Any other piece takes the full
        rebuild. `indexed`: the caller already ran _index on each piece.
        A full rebuild costs seconds on Map 10, and set_piece used to run
        one per scene (694 s build profile, 2026-11-10)."""
        for p in pieces:
            if (p.is_glob_egg or p.shape == 347 or dm.item_class(
                    self.src.info(p.shape), p.shape, p.frame) in ('ground', 'void')):
                return self._refresh()
        self.expanded.extend(pieces)
        self._crest_cover = {}
        for attr in ('_surface_reach', '_sky_cameras'):
            if hasattr(self, attr):
                delattr(self, attr)
        if not indexed:
            for it in pieces:
                if not it.flags & MapItem.FLG_CONTAINED:
                    self._index(it)

    def _index(self, it):
        for cell in cells32(box(it, self.sorter), 80):
            self.spatial[cell].append(it)

    def _mark(self, b, reason, margin=0, solid=False):
        mask = self.solid_mask if solid else self.mask
        for c in cells32(b, margin):
            mask[c].add(reason)

    def _exclusions(self):
        pins = json.loads((HERE / 'map_pins.json').read_text())['maps'].get(str(self.mapnum), [])
        self.scripted = [(p['x'], p['y'], p['z']) for p in pins if p['x'] > 64 and p['y'] > 64]
        for p in pins:
            if p['x'] <= 64 or p['y'] <= 64:
                continue
            self._mark((p['x'], p['y'], p['x'], p['y']), 'map pin', 96)
        for it in self.expanded:
            if it.flags & MapItem.FLG_CONTAINED:
                continue
            b, inf = box(it, self.sorter), self.sorter.info(it.shape)
            if it.shape in (73, 500, 508):
                rx, ry = (it.npcnum >> 4) * 32, (it.npcnum & 15) * 32
                if it.shape == 508:
                    rx = ry = max(128, rx, ry)
                self._mark((it.x - rx, it.y - ry, it.x + rx, it.y + ry), 'egg hatch or teleport')
            if not inf['fixed'] and not inf['editor']:
                self._mark(b, 'movable clear box and reach rays', 96)
            if it.shape in (497, 498, 501, 846):
                self._mark(b, 'anti-climb wall', 32, solid=True)
        if self.mapnum == 10:
            from build_map_10 import TRACKS
            for line in TRACKS:
                for c in _line_cells(line, 96): self.solid_mask[c].add('TRACKS')
        if self.mapnum == 11:
            vals = _constants('test_route_reach.py', {'FIRE_TALISMAN_STAND', 'FIRE_DOOR', 'FIRE_NORTH_WALL_Y', 'FIRE_LINES', 'LAVA_MARGIN'})
            for line in vals['FIRE_LINES'].values():
                for c in _line_cells(line, vals['LAVA_MARGIN']): self.mask[c].add('FIRE_LINES and LAVA_MARGIN')
            for b in ((9536, 13888, 9984, 14911),):
                self._mark(b, 'monster box')
        if self.mapnum == 13:
            self._mark((2687, 10111, 4735, 11135), 'VALLEY_CLEAR')
        if self.mapnum == 18:
            self._mark((2688, 6015, 3072, 6623), 'Map 18 breach and entry lane', 96)

    def reserve(self, name, footprint):
        """Reserve (x0,y0,x1,y1) for a builder's hand-authored set piece."""
        if self._packed:
            raise ValueError('site is already packed')
        self.reservations.append((name, tuple(footprint)))
        self._mark(footprint, f'set piece {name}')

    def _near(self, b):
        seen = set()
        for c in cells32(b, 80):
            for it in self.spatial.get(c, ()):
                if id(it) not in seen:
                    seen.add(id(it))
                    yield it

    def _crest_support(self, it, other):
        inf = self.sorter.info(it.shape)
        if other.shape != 125 or inf['solid'] or inf['land']:
            return False
        b, ob = box(it,self.sorter), box(other,self.sorter)
        if b[4] != ob[5] or not (ob[0] <= b[0] and ob[1] <= b[1] and b[2] <= ob[2] and b[3] <= ob[3]):
            return False
        if not hasattr(self,'_surface_reach'):
            er = self._reach_model(step=32)
            reach,_ = er.flood(self._arrival())
            self._surface_reach = er,reach
        er,reach = self._surface_reach
        i,j = er.index_of(it.x,it.y)
        return b[4] in reach and bool(reach[b[4]][i,j])

    def reason(self, it, *, ground=False, allow_reservation=None, architecture=False):
        """Return the first exclusion violated, or None. No mutation."""
        inf, b = self.sorter.info(it.shape), box(it, self.sorter)
        if self.mapnum in (10,13) and it.shape == 301 and 6 <= it.frame <= 37:
            return 'retail riverbank floor excluded by cliff-shore direction'
        if self.sorter.frame(it.shape, it.frame) is None:
            return 'missing shape frame'
        if paints_window(it, self.sorter, self.windows):
            return 'shot window and FLOORS'
        if it.shape == SHAPE_CAVE_CREST_DECORATIVE and self._crest_occludes(it):
            return 'cave crest increases quest-band occlusion'
        cells = cells32(b)
        for c in cells:
            reasons = self.mask.get(c, set())
            if allow_reservation is not None:
                reasons = reasons - {f'set piece {allow_reservation}'}
            if reasons: return sorted(reasons)[0]
        solid = inf['solid'] and inf['zd'] > 0
        true_flat = inf['zd'] == 0 and not inf['solid']
        prop = dm.item_class(inf,it.shape,it.frame) not in ('ground','void')
        if prop and not true_flat and not architecture and max(inf['xd'],inf['yd']) >= 64 and cells & self.leg_mask:
            return 'quest leg band with 64-unit margin'
        if solid:
            if not architecture and cells & self.leg_mask: return 'quest leg band with 64-unit margin'
            for c in cells:
                if self.solid_mask.get(c): return sorted(self.solid_mask[c])[0]
        if inf['zd'] > 40:
            for x, y, z in self.scripted:
                if (it.x >= x or it.y >= y) and math.hypot(it.x - x, it.y - y) <= 8 * inf['zd']:
                    return 'south or east rim of scripted point'
        for other in self._near(b):
            oi, ob = self.sorter.info(other.shape), box(other, self.sorter)
            crest_support = self._crest_support(it,other)
            if not ground and not crest_support and inf['zd'] == 0 and max(inf['xd'], inf['yd']) <= 96 and oi['zd'] >= 8 and xy_overlap(b, ob, 80):
                return 'small flat beside tall item'
            if not xy_overlap(b, ob):
                continue
            if (oi['solid'] or solid) and b[4] < ob[5] and ob[4] < b[5]:
                return 'overlapping solid'
            if solid and ob[4] == b[5]:
                return 'existing item on new solid top face'
            if oi['solid'] and oi['zd'] and b[4] == ob[5] and not crest_support:
                return "solid top face"
            if not ground and not crest_support and inf['zd'] == 0 and max(inf['xd'], inf['yd']) <= 96 and oi['zd'] >= 8:
                return 'small flat beside tall item'
            if not ground and inf['zd'] == 0 and (inf['draw'] or inf['occl']) and oi['land'] and oi['zd'] == 0 and it.z == other.z:
                return 'overlay has SI_DRAW or SI_OCCL'
        if not ground and inf['land'] and solid:
            if it.z % 4: return 'standing level off 4-unit lattice'
            if not architecture and self._new_top(it): return 'new reachable standing top'
        return None

    def _pose_cover(self, actor, x, y, z):
        """Existing opaque cover for one pose, using ItemSorter arithmetic."""
        import numpy as np
        mask = self.sorter.mask(actor)
        cover = np.zeros_like(mask)
        limit = self.sorter.roof_z(self.expanded, x, y, z)
        for other in self.expanded:
            if other.flags & (FLG_INVISIBLE | MapItem.FLG_CONTAINED):
                continue
            inf = self.sorter.info(other.shape)
            if inf['editor'] or (limit is not None and other.z >= limit and not inf['draw']):
                continue
            si = self.sorter._make(other, 0, 0)
            if si is None or not overlap(actor, si) or not below(actor, si):
                continue
            if si.occl and occludes(si, actor):
                cover[:] = True
                break
            l, t = max(actor.sr[0], si.sr[0]), max(actor.sr[1], si.sr[1])
            r, b = min(actor.sr[2], si.sr[2]), min(actor.sr[3], si.sr[3])
            cover[t-actor.sr[1]:b-actor.sr[1], l-actor.sr[0]:r-actor.sr[0]] |= (
                self.sorter.mask(si)[t-si.sr[1]:b-si.sr[1], l-si.sr[0]:r-si.sr[0]])
        return cover

    def _crest_occludes(self, it):
        # Protect every opaque pixel of every walking and standing pose.
        # Existing covered pixels may stay covered. Cached cover is reset
        # whenever the site's expanded geometry is refreshed.
        from avatar_visibility import Poses
        import numpy as np
        if not hasattr(self, '_crest_poses'):
            self._crest_poses = {}
        candidate = self.sorter._make(it, 0, 0)
        for label, a, b, body, shape in LEGS.get(self.mapnum, ()):
            if not self.bands.get(label):
                continue
            if shape not in self._crest_poses:
                self._crest_poses[shape] = Poses(self.sorter, shape=shape)
            poses = self._crest_poses[shape]
            for x, y, z in self.bands[label]:
                sx, sy = x // 4 - y // 4, x // 8 + y // 8 - z
                l, t, r, bottom = poses.bounds
                if (candidate.sr[2] <= sx+l or candidate.sr[0] >= sx+r or
                        candidate.sr[3] <= sy+t or candidate.sr[1] >= sy+bottom):
                    continue
                for frame, flip in poses.frames:
                    actor = self.sorter._make(_Item(shape, frame, x, y, z,
                        FLG_FLIPPED if flip else 0), 0, 0)
                    # Paint order without a direct footprint dependency can
                    # still put this sprite in front. Conservatively protect
                    # every pixel intersection, including that ambiguous case.
                    l, t = max(actor.sr[0],candidate.sr[0]), max(actor.sr[1],candidate.sr[1])
                    r, b = min(actor.sr[2],candidate.sr[2]), min(actor.sr[3],candidate.sr[3])
                    if r <= l or b <= t:
                        continue
                    hit = (self.sorter.mask(candidate)[t-candidate.sr[1]:b-candidate.sr[1],
                                                      l-candidate.sr[0]:r-candidate.sr[0]] &
                           self.sorter.mask(actor)[t-actor.sr[1]:b-actor.sr[1],
                                                  l-actor.sr[0]:r-actor.sr[0]])
                    if not hit.any():
                        continue
                    key = (shape,frame,flip,x,y,z)
                    if key not in self._crest_cover:
                        self._crest_cover[key] = self._pose_cover(actor,x,y,z)
                    covered = self._crest_cover[key][t-actor.sr[1]:b-actor.sr[1],
                                                      l-actor.sr[0]:r-actor.sr[0]]
                    if np.any(hit & ~covered):
                        return True
        return False

    def _skin_occludes(self, pieces):
        """Compare every nearby walking pose before and after wall paint."""
        from avatar_visibility import Poses
        from vignette_paint import Painter
        import numpy as np
        if not hasattr(self,'_surface_reach'):
            er = self._reach_model(step=32)
            reach,seeded = er.flood(self._arrival())
            if not seeded:
                raise ValueError('wall skin requires a reachable visibility baseline')
            self._surface_reach = er,reach
        er,reach = self._surface_reach
        spots = {(1,int(er.x_of(i)),int(er.y_of(j)),z)
                 for z,r in reach.items() for i,j in zip(*np.where(r))}
        for label,a,b,body,shape in LEGS.get(self.mapnum,()):
            spots |= {(shape,x,y,z) for x,y,z in self.bands.get(label,())}
        painter = Painter.built()
        skins = [self.sorter._make(i,0,0) for i in pieces]
        poses = {}
        drawables=[]
        for it in self.expanded:
            inf=self.sorter.info(it.shape)
            if it.flags & (FLG_INVISIBLE | MapItem.FLG_CONTAINED) or inf['editor']:continue
            si=self.sorter._make(it,0,0)
            if si is not None:drawables.append((it,inf,si))
        rects=np.array([si.sr for it,inf,si in drawables]).reshape(-1,4)
        for shape,x,y,z in sorted(spots):
            if shape not in poses: poses[shape]=Poses(self.sorter,shape=shape)
            ps=poses[shape]
            sx,sy=x//4-y//4,x//8+y//8-z
            l,t,r,b=ps.bounds
            if not any(s.sr[0]<sx+r and s.sr[2]>sx+l and s.sr[1]<sy+b and s.sr[3]>sy+t for s in skins):continue
            roof=self.sorter.roof_z(self.expanded,x,y,z)
            for frame,flip in ps.frames:
                actor=MapItem.placed_item(x,y,z,shape,frame)
                if flip:actor.flags |= FLG_FLIPPED
                a=self.sorter._make(actor,0,0)
                left,top,right,bottom=a.sr
                ids=np.flatnonzero((rects[:,0]<right) & (rects[:,2]>left) &
                                   (rects[:,1]<bottom) & (rects[:,3]>top))
                world=[vars(drawables[k][0]) for k in ids
                       if roof is None or drawables[k][0].z<roof or drawables[k][1]['draw']]
                # Ambiguous dependencies can place an actor at either end
                # of a chunk's insertion order. Both must preserve paint.
                for first in (True,False):
                    old=([vars(actor)]+world) if first else (world+[vars(actor)])
                    new=([vars(actor)]+world+[vars(p) for p in pieces]) if first else (world+[vars(p) for p in pieces]+[vars(actor)])
                    _,_,before=painter.paint(old,left,top,right-left,bottom-top,owner=True)
                    _,seq,after=painter.paint(new,left,top,right-left,bottom-top,owner=True)
                    if any(d.order>s.order for s in seq for d in s.depends):return True
                    old_index=0 if first else len(old)-1
                    new_index=0 if first else len(new)-1
                    if np.any((before==old_index) & (after!=new_index)):return True
        return False

    def _new_top(self, it):
        # A local exact-reach model seeded on every pre-existing standing
        # cell is conservative: even disconnected approaches are protected.
        from exact_reach import ExactReach
        import numpy as np
        b = box(it, self.sorter)
        roi = (max(0, b[0] - 160), max(0, b[1] - 160), b[2] + 160, b[3] + 160)
        nearby = list(self._near((roi[0], roi[1], roi[2], roi[3])))
        before = ExactReach(nearby, self.shapes, roi, step=8)
        after = ExactReach(nearby + [it], self.shapes, roi, step=8)
        seeds = [(int(before.x_of(i)), int(before.y_of(j)), z)
                 for z in before.levels for i, j in zip(*np.where(before.mask(z)))]
        reach, _ = after.flood(seeds)
        top = it.z + self.sorter.info(it.shape)['zd']
        return top in reach and bool(np.any(reach[top] & ~before.mask(top)))

    def _accept(self, pieces, *, ground=False, allow_reservation=None, architecture=False, prefab_stack=False):
        for it in pieces:
            is_floor = dm.item_class(self.sorter.info(it.shape), it.shape, it.frame) in ('ground', 'void')
            why = self.reason(it, ground=ground and is_floor, allow_reservation=allow_reservation, architecture=architecture)
            if why: return why
        # Compare members too, without mutating the live site.
        for k, it in enumerate(pieces):
            b = box(it, self.sorter)
            for other in pieces[:k]:
                ob, oi = box(other, self.sorter), self.sorter.info(other.shape)
                ii = self.sorter.info(it.shape)
                if xy_overlap(b, ob):
                    overlap = b[4] < ob[5] and ob[4] < b[5]
                    if overlap and ((oi['solid'] and oi['zd']) or (ii['solid'] and ii['zd'])):
                        return 'prefab or cluster self overlap'
                    if not prefab_stack and ((oi['solid'] and oi['zd'] and b[4] == ob[5]) or (ii['solid'] and ii['zd'] and ob[4] == b[5])):
                        return 'prefab or cluster solid top face'
        return None

    def _prefab_reachable_top(self, pieces):
        from exact_reach import ExactReach
        import numpy as np
        boxes = [box(p,self.sorter) for p in pieces]
        roi = (max(0,min(b[0] for b in boxes)-256),max(0,min(b[1] for b in boxes)-256),
               max(b[2] for b in boxes)+256,max(b[3] for b in boxes)+256)
        nearby = list(self._near(roi))
        before = ExactReach(nearby,self.shapes,roi,step=8)
        after = ExactReach(nearby+pieces,self.shapes,roi,step=8)
        seeds = [(int(before.x_of(i)),int(before.y_of(j)),z)
                 for z in before.levels for i,j in zip(*np.where(before.mask(z)))]
        reach,_ = after.flood(seeds)
        return any(np.any(r & ~before.mask(z)) for z,r in reach.items())

    def _mutable(self):
        if self._packed: raise ValueError('site is already packed')

    def swap_chunks(self, *, plain, family, share, where):
        self._mutable()
        if not 0 <= share <= 1: raise ValueError('share outside [0,1]')
        plain_items = self.globs.glob_to_items(plain,0,0,0)
        if not plain_items or any(self.sorter.info(i.shape)['zd'] or dm.item_class(self.sorter.info(i.shape),i.shape,i.frame) != 'ground' for i in plain_items):
            raise ValueError('plain member must be a flat floor chunk')
        family = tuple(dict.fromkeys(family))
        if self.mapnum in (10,13) and any(1537 <= n <= 1554 for n in family):
            raise ValueError('retail river-shore globs are excluded; use approved LV cliff-shore prefabs')
        if len(family) < 4: raise ValueError('substitution needs at least four family members')
        candidates = []
        for egg in self.items:
            if id(egg) in self.protected_raw or not egg.is_glob_egg or egg.quality != plain: continue
            x, y = egg.x & ~511, egg.y & ~511
            if not (where[0] <= x and where[1] <= y and x + 511 <= where[2] and y + 511 <= where[3]): continue
            cb = (x, y, x + 511, y + 511)
            if any(other is not egg and xy_overlap(cb, box(other, self.sorter)) for other in self.items): continue
            candidates.append(egg)
        candidates.sort(key=lambda e: random.Random(f'{self.seed}:{self.mapnum}:{e.x//512}:{e.y//512}').random())
        # Equal complete batches ensure four members and the 25% ceiling.
        count = int(len(candidates) * share) // len(family) * len(family)
        changed, used = [], Counter()
        for egg in candidates:
            if len(changed) >= count: break
            x, y = egg.x & ~511, egg.y & ~511
            options = sorted(family, key=lambda n: (used[n], random.Random(f'{self.seed}:{x}:{y}:{n}').random()))
            for number in options:
                if used[number] >= count // len(family): continue
                pieces = self.globs.glob_to_items(number, egg.x, egg.y, egg.z)
                if not pieces: continue
                # A plain floor has zero height, so retaining it in the
                # safety index cannot obstruct a replacement's props.
                solid = any(self.sorter.info(p.shape)['solid'] and self.sorter.info(p.shape)['zd'] for p in pieces)
                cb = (x, y, x + 511, y + 511)
                why = 'solid prefab in leg band' if solid and cells32(cb) & self.leg_mask else self._accept(pieces, ground=True)
                if why: continue
                if self._run_three(number, x // 512, y // 512): continue
                egg.quality = number
                changed.append(egg); used[number] += 1
                for p in pieces: self._index(p)
                break
        # A partial eligible batch cannot satisfy the family-share contract.
        if changed and (len(used) < 4 or max(used.values()) / len(changed) > .25):
            for egg in changed: egg.quality = plain
            changed = []
        self.swapped.extend(changed)
        self.ledger.append(dict(operation='swap', changed=len(changed), raw_delta=0))
        self._refresh()
        return changed

    def place_prefab(self, number, *, x, y, z=0, where=None):
        """Add safe props from a prefab to an occupied chunk, retaining floors.

        x and y identify the containing chunk, as for a glob egg. Each prop
        is checked against exclusions and accepted earlier props. Floor and
        void tiles are omitted; rejected props are counted in the ledger.
        """
        self._mutable()
        pieces = self.globs.glob_to_items(number, x, y, z)
        if not pieces:
            raise ValueError(f'empty prefab {number}')
        added, rejected = [], Counter()
        for it in pieces:
            cls = dm.item_class(self.sorter.info(it.shape), it.shape, it.frame)
            if cls in ('ground', 'void'):
                continue
            bounds = box(it, self.sorter)
            why = None
            if where is not None and not (where[0] <= bounds[0] and where[1] <= bounds[1]
                                         and bounds[2] <= where[2] and bounds[3] <= where[3]):
                why = 'outside placement box'
            # A prop needs the existing floor at its anchor and base height.
            support = self.ground.get((it.x // 128, it.y // 128))
            if not support or support[2] + self.sorter.info(support[0])['zd'] != it.z:
                why = why or 'no existing floor at prop base'
            why = why or self.reason(it)
            if why:
                rejected[why] += 1
                continue
            self.items.append(it); self.added.append(it); added.append(it)
            self._index(it)
        self._refresh()
        self.ledger.append(dict(operation='prefab_props', prefab=number,
                                added=len(added), rejected=dict(rejected)))
        return added

    def moat_bank(self, side, *, where):
        """Overlay the clipped Tenebrae banks on retained z=48 grass.

        The west/east rows occupy only their grass-side 128-unit column.
        They supply no support, grass, or water. The channel and all its
        retained records remain intact.
        """
        self._mutable()
        if self.mapnum != 39 or side not in ('west', 'east'):
            raise ValueError('moat bank requires Map 39 and side west or east')
        family = prefab_family(f'moat_{side}_')
        if len(family) != 4:
            raise ValueError('build the four clipped moat bank prefabs first')
        cx = 26 if side == 'west' else 27
        added = []
        for cy in range(where[1] // 512, where[3] // 512 + 1):
            n = random.Random(f'{self.seed}:moat:{side}:{cy}').choice(family)
            for it in self.globs.glob_to_items(n, cx * 512, cy * 512, 0):
                b = box(it, self.sorter)
                if not (where[0] <= b[0] and where[1] <= b[1] and
                        b[2] <= where[2] and b[3] <= where[3]):
                    continue
                if b[0] < 14080 and b[2] >= 13568:
                    raise ValueError('moat bank enters the no-grass strip')
                support = self.ground.get((it.x // 128, it.y // 128))
                if not support or support[0] != 3 or support[2] != 48:
                    continue
                if self.reason(it):
                    continue
                self.items.append(it); self.added.append(it); added.append(it)
                self._index(it)
        self._refresh()
        self.ledger.append(dict(operation='moat_bank', side=side, added=len(added)))
        return added

    def cave_crest(self, name, pieces):
        """Place decorative caps, selecting the largest safe cropped frame.

        Input frames name retail 125 frames (zero through 22). Each anchor
        tries the full sprite, upper strips, and half sprites. A cap with no
        safe variant is refused; the complete named piece stays atomic.
        """
        from lv_art_props import CREST_CROPS
        self._mutable()
        chosen = []
        for original in pieces:
            if original.shape != SHAPE_CAVE_CREST_DECORATIVE or not 0 <= original.frame < 23:
                raise ValueError('cave crest requires decorative shape and retail frame 0..22')
            candidates = []
            for k in range(len(CREST_CROPS)):
                it = copy.deepcopy(original)
                it.frame = original.frame * len(CREST_CROPS) + k
                if not self._accept(chosen + [it], ground=True, allow_reservation=name):
                    candidates.append(it)
            if not candidates:
                raise ValueError(f'{name}: no window-safe, route-safe crest at {original.x},{original.y}')
            chosen.append(max(candidates, key=lambda p: int(self.sorter.mask(
                self.sorter._make(p, 0, 0)).sum())))
        return self.set_piece(name, chosen)

    def _run_three(self, number, x, y):
        occupied = {(i.x // 512, i.y // 512) for i in self.items if i.is_glob_egg and i.quality == number}
        for dx, dy in ((1, 0), (0, 1)):
            for offset in range(3):
                if all((x + (k - offset) * dx, y + (k - offset) * dy) in occupied | {(x, y)} for k in range(3)):
                    return True
        return False

    def clusters(self, *, kit, per100, where, floors, anchor='seam'):
        self._mutable()
        if anchor not in ('wall', 'seam', 'water', 'open'): raise ValueError('unknown anchor')
        if per100 < 0: raise ValueError('negative density')
        cells = [c for c, v in self.ground.items() if v[0] in floors and
                 where[0] <= c[0] * 128 + 64 <= where[2] and where[1] <= c[1] * 128 + 64 <= where[3]]
        def anchored(c):
            x, y = c
            if any(abs(x * 128 + 64 - (b[0] + b[2]) / 2) + abs(y * 128 + 64 - (b[1] + b[3]) / 2) < 384 for _, b in self.reservations): return True
            neighbours = [self.ground.get((x+dx,y+dy)) for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))]
            if anchor == 'seam': return any(v and v[0] != self.ground[c][0] for v in neighbours)
            if anchor == 'water': return any((x+dx,y+dy) in self.water_cells for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)))
            # Open requests still retain the 60% anchor floor.
            return any(self.sorter.info(i.shape)['solid'] and self.sorter.info(i.shape)['zd'] >= 40
                       for i in self._near((x*128, y*128, x*128+128, y*128+128)))
        order = sorted(cells, key=lambda c: (not anchored(c), random.Random(f'{self.seed}:{self.mapnum}:{c}').random()))
        target = round(len(cells) * per100 / 100)
        added, seeds, anchored_count = [], [], 0
        for cx, cy in order:
            if len(added) >= target: break
            x, y = cx * 128 + 64, cy * 128 + 64
            if any(math.hypot(x-px,y-py) < 448 for px,py in self.seeds + seeds): continue
            is_anchor = anchored((cx,cy))
            if not is_anchor and (anchored_count / (len(seeds) + 1)) < .60: continue
            rng = random.Random(f'{self.seed}:{self.mapnum}:{cx}:{cy}')
            pieces = []
            for _ in range(rng.choice((2,3,3,4,5)) * 12):
                if len(pieces) >= 5: break
                shape, nf, weight = rng.choices(kit, [p[2] for p in kit])[0]
                # Each cell has its own RNG, also when a seed is skipped.
                px, py = x + 32 * rng.randint(-5,5), y + 32 * rng.randint(-5,5)
                if math.hypot(px-x,py-y) > 160: continue
                c = (px//128, py//128)
                if c not in self.ground or self.ground[c][0] not in floors: continue
                if not (where[0] <= px <= where[2] and where[1] <= py <= where[3]): continue
                frame_rng = random.Random(f'{self.seed}:{self.mapnum}:{px//32}:{py//32}:{shape}')
                it = MapItem.placed_item(px, py, self.ground[c][2], shape, frame_rng.randrange(nf))
                if self.reason(it):
                    it = MapItem.placed_item(px, py, self.ground[c][2], 465, frame_rng.randrange(17))
                if any(p.x == px and p.y == py for p in pieces): continue
                if self._accept(pieces + [it]): continue
                pieces.append(it)
                if len(pieces) >= 2 and len(pieces) >= rng.choice((2,3,3,4,5)): break
            if len(pieces) < 2 or (len(pieces) >= 3 and len({p.shape for p in pieces}) < 2): continue
            # Links keep each cluster's nearest neighbours within 128 units.
            if any(min(math.hypot(p.x-q.x,p.y-q.y) for q in pieces if q is not p) > 128 for p in pieces): continue
            self.items.extend(pieces); self.added.extend(pieces); added.extend(pieces)
            seeds.append((x,y)); anchored_count += is_anchor
            for p in pieces: self._index(p)
        self.seeds.extend(seeds)
        self._refresh_appended(added, indexed=True)
        self.ledger.append(dict(operation='clusters', added=len(added), seeds=len(seeds), anchored=anchored_count))
        return added

    def set_piece(self, name, pieces):
        self._mutable()
        pieces = copy.deepcopy(list(pieces))
        # Existing reservations remain protected, including other set pieces.
        for it in pieces:
            why = self.reason(it, allow_reservation=name)
            if why: raise ValueError(f'{name}: {it.shape}@{it.x},{it.y},{it.z}: {why}')
        why = self._accept(pieces, allow_reservation=name)
        if why: raise ValueError(f'{name}: {why}')
        self.items.extend(pieces); self.added.extend(pieces)
        if pieces:
            boxes = [box(i,self.sorter) for i in pieces]
            self.reserve(name, (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)))
        self.ledger.append(dict(operation='set_piece', name=name, added=len(pieces)))
        self._refresh_appended(pieces)
        return pieces

    def _reach_model(self, pieces=(), *, step=8, step_z=8):
        from exact_reach import ExactReach, SI_SEA, HURT_SHAPES_U8
        all_items = self.expanded + list(pieces)
        boxes = [box(i, self.sorter) for i in all_items]
        if not boxes:
            raise ValueError('route proof requires existing geometry')
        roi = (max(0, min(b[0] for b in boxes)-128),
               max(0, min(b[1] for b in boxes)-128),
               min(65535, max(b[2] for b in boxes)+128),
               min(65535, max(b[3] for b in boxes)+128))
        return ExactReach(all_items, self.shapes, roi, step=step, step_z=step_z,
                          mover_flags=2 | SI_SEA, hurt_shapes=HURT_SHAPES_U8)

    def _arrival(self):
        arrivals = _constants('test_monster_eggs.py', {'ARRIVAL'})['ARRIVAL']
        if self.mapnum in arrivals:
            return [arrivals[self.mapnum]]
        seeds = list(dict.fromkeys(a for label,a,b,body,shape in LEGS.get(self.mapnum,()) if shape==1))
        if not seeds:
            raise ValueError('route proof requires explicit seeds on this map')
        return seeds

    def walkable_set_piece(self, name, pieces, *, seeds=None):
        """Accept named low architecture only after a complete route proof.

        Tops rise at most eight units from existing land. Exact walking
        floods include walk-offs. A separate conservative climb72 guard
        refuses new footholds beside previously unreachable raised tops.
        """
        import numpy as np
        self._mutable()
        pieces = copy.deepcopy(list(pieces))
        if not name or not pieces:
            raise ValueError('walkable architecture needs a name and pieces')
        for it in pieces:
            inf = self.sorter.info(it.shape)
            if not (inf['land'] and inf['solid'] and 0 < inf['zd'] <= 8):
                raise ValueError(f'{name}: architecture requires a flat low standing top')
            if it.z % 4 or (it.z + inf['zd']) % 4:
                raise ValueError(f'{name}: standing level off 4-unit lattice')
            support = self.ground.get((it.x//128, it.y//128))
            if not support or it.z != support[2] + self.sorter.info(support[0])['zd']:
                raise ValueError(f'{name}: architecture must rise from retained floor')
            why = self.reason(it, allow_reservation=name, architecture=True)
            if why:
                raise ValueError(f'{name}: {why}')
        for it in pieces:
            b = box(it,self.sorter)
            if any(b[0] < x <= b[2]+63 and b[1] < y <= b[3]+63 and b[4] <= z < b[5]
                   for band in self.bands.values() for x,y,z in band):
                raise ValueError(f'{name}: architecture changes a quest leg cell')
        why = self._accept(pieces, allow_reservation=name, architecture=True)
        if why:
            raise ValueError(f'{name}: {why}')
        # The same ROI and lattice make all before/after masks comparable.
        before = self._reach_model(pieces, step=8, step_z=8)
        from exact_reach import ExactReach, SI_SEA, HURT_SHAPES_U8
        before = ExactReach(self.expanded, self.shapes, before.roi, step=8,
                            step_z=8, mover_flags=2 | SI_SEA,
                            hurt_shapes=HURT_SHAPES_U8)
        after = ExactReach(self.expanded+pieces, self.shapes, before.roi, step=8,
                           step_z=8, mover_flags=2 | SI_SEA,
                           hurt_shapes=HURT_SHAPES_U8)
        seeds = list(seeds if seeds is not None else self._arrival())
        old, seeded = before.flood(seeds)
        if not seeded:
            raise ValueError(f'{name}: no reachable seed')
        old = before.walk_off(old)['reach']
        new, _ = after.flood(seeds)
        new = after.walk_off(new)['reach']
        for z, reached in new.items():
            allowed = old.get(z, np.zeros_like(reached)).copy()
            for it in pieces:
                b = box(it, self.sorter)
                if b[5] == z:
                    # Support uses the engine's half-open body overlap.
                    xs = np.array([after.x_of(k) for k in range(after.NX)])
                    ys = np.array([after.y_of(k) for k in range(after.NY)])
                    allowed |= ((xs[:,None] > b[0]) & (xs[:,None] < b[2]+64) &
                                (ys[None,:] > b[1]) & (ys[None,:] < b[3]+64))
            if np.any(reached & ~allowed):
                raise ValueError(f'{name}: architecture opens a new route at z {z}')
        xs = np.array([before.x_of(k) for k in range(before.NX)])
        ys = np.array([before.y_of(k) for k in range(before.NY)])
        for z,reached in old.items():
            lost = reached & ~new.get(z,np.zeros_like(reached))
            for it in pieces:
                b = box(it,self.sorter)
                if b[4] <= z < b[5]:
                    # Standing on the replacement top consumes the old
                    # floor positions whose body intersects this slab.
                    lost &= ~((xs[:,None]>b[0]) & (xs[:,None]<b[2]+64) &
                              (ys[None,:]>b[1]) & (ys[None,:]<b[3]+64))
            if np.any(lost):
                raise ValueError(f'{name}: architecture closes a retained route at z {z}')
        # A walking flood probes only offsets zero, four, and eight.
        # Reject every new foothold that could assist a climb16..climb72
        # to a retained top within the estate's two-tile jump envelope.
        for it in pieces:
            b = box(it,self.sorter)
            for sx,sy,top,xd,yd in before.supports:
                if not 16 <= top-b[5] <= 72:
                    continue
                if not xy_overlap(b,(sx-xd,sy-yd,sx,sy),256):
                    continue
                candidates = [(int(before.x_of(i)),int(before.y_of(j)))
                              for i,j in zip(*np.where(before.mask(top)))
                              if sx-xd < before.x_of(i) < sx+64 and sy-yd < before.y_of(j) < sy+64]
                if not candidates:
                    continue
                if not any(top in old and old[top][before.index_of(x,y)] for x,y in candidates):
                    raise ValueError(f'{name}: architecture opens a new route by climb72')
        for it in pieces:
            b = box(it, self.sorter)
            if b[5] not in new or not new[b[5]][after.index_of(it.x,it.y)]:
                raise ValueError(f'{name}: intended top is unreachable')
        self.items.extend(pieces); self.added.extend(pieces)
        boxes = [box(i,self.sorter) for i in pieces]
        self.reserve(name, (min(b[0] for b in boxes), min(b[1] for b in boxes),
                            max(b[2] for b in boxes), max(b[3] for b in boxes)))
        self._refresh_appended(pieces)
        self.ledger.append(dict(operation='walkable_set_piece', name=name, added=len(pieces)))
        return pieces

    def paint_only(self, name, pieces, *, replaces=()):
        """Place decorative panels, faces, or an opaque skin over retained walls.

        A skin keeps every original record. Its final paint must conceal
        every original wall pixel, and may cover no additional quest-pose
        pixel. Only a replacement skin can cross VALLEY_CLEAR.
        """
        from vignette_paint import Painter
        import numpy as np
        self._mutable()
        pieces = copy.deepcopy(list(pieces))
        keys = [i.to_bytes() for i in replaces]
        targets = [i for i in self.items if i.to_bytes() in keys]
        if len(targets) != len(keys):
            raise ValueError(f'{name}: replacement wall absent or ambiguous')
        if any(not self.sorter.info(i.shape)['solid'] for i in targets):
            raise ValueError(f'{name}: replacement requires retained solid walls')
        for it in pieces:
            inf = self.sorter.info(it.shape)
            if it.shape not in (902,912,913,914,915) or inf['solid'] or inf['land']:
                raise ValueError(f'{name}: paint requires a decorative panel, face, or crest')
            if paints_window(it,self.sorter,self.windows) or (not targets and self._crest_occludes(it)):
                raise ValueError(f'{name}: paint changes protected window or quest pose')
            b = box(it,self.sorter)
            for c in cells32(b):
                reasons = self.mask.get(c,set()) - {f'set piece {name}'}
                if targets:
                    reasons = reasons - {'VALLEY_CLEAR'}
                if reasons:
                    raise ValueError(f'{name}: {sorted(reasons)[0]}')
        if targets and self._skin_occludes(pieces):
            raise ValueError(f'{name}: skin reduces Avatar visibility')
        painter = Painter.built()
        nearby = [i for i in self.expanded if any(xy_overlap(box(i,self.sorter),box(p,self.sorter),512) for p in pieces)]
        render = nearby + pieces
        sprites = [self.sorter._make(i,0,0) for i in render]
        sprites = [s for s in sprites if s is not None]
        if not sprites:
            raise ValueError(f'{name}: empty paint')
        left,top = min(s.sr[0] for s in sprites),min(s.sr[1] for s in sprites)
        right,bottom = max(s.sr[2] for s in sprites),max(s.sr[3] for s in sprites)
        out,seq,own = painter.paint([vars(i) for i in render],left,top,right-left,bottom-top,owner=True)
        if any(d.order > s.order for s in seq for d in s.depends):
            raise ValueError(f'{name}: paint cycle')
        # Rendering the target alone identifies all pixels that need a skin.
        for target in targets:
            tile,_,_ = painter.paint([vars(target)],left,top,right-left,bottom-top,owner=True)
            covered = np.zeros_like(own,dtype=bool)
            for k in range(len(nearby),len(render)):
                covered |= own == k
            if np.any((tile >= 0) & ~covered):
                raise ValueError(f'{name}: skin leaves wall sprite exposed')
        self.items.extend(pieces); self.added.extend(pieces)
        self._refresh_appended(pieces)
        self.ledger.append(dict(operation='paint_only',name=name,added=len(pieces),retained_walls=len(targets)))
        return pieces

    def basalt_shore(self, name, cells, *, z=0, frames=(0,)):
        """Paint basalt on retained cold rock cells adjacent to lava.

        Cells may include an explicit frame for an oriented contour.
        Causeways, lava, and all original records remain untouched.
        """
        self._mutable()
        pieces = []
        for cell in cells:
            cx,cy=cell[:2]
            frame=cell[2] if len(cell)==3 else random.Random(f'{self.seed}:basalt:{cx}:{cy}').choice(tuple(frames))
            if len(cell) not in (2,3):raise ValueError('shore cells are (cx,cy) or (cx,cy,frame)')
            support = self.ground.get((cx,cy))
            if not support or support[0] not in (301,4,386) or support[2] != z:
                raise ValueError(f'{name}: basalt requires retained cold floor')
            adjacent = any(i.shape == 409 and abs(i.x//128-cx)+abs(i.y//128-cy) == 1
                           for i in self.expanded)
            if not adjacent:
                raise ValueError(f'{name}: basalt requires a lava neighbour')
            pieces.append(MapItem.placed_item(cx*128+127,cy*128+127,z,911,frame))
        return self.set_piece(name,pieces)

    def swap_loose_chunks(self, *, floors, family, share, where):
        """Replace complete loose flat chunks, preserving tie precedence.

        Replacement tiles stay loose in each removed tile's record position;
        a same-height later overlay therefore keeps its existing precedence.
        """
        self._mutable()
        if not 0 <= share <= 1 or len(set(family)) < 4:
            raise ValueError('loose substitution needs a share and four members')
        groups = defaultdict(list)
        for k,it in enumerate(self.items):
            inf = self.sorter.info(it.shape)
            if (it.shape in floors and not it.is_glob_egg and inf['zd'] == 0 and
                not it.flags and not it.quality and not it.npcnum and not it.mapnum and
                not it.next_ptr and id(it) not in self.protected_raw):
                groups[it.x//512,it.y//512,it.z].append((k,it))
        candidates = []
        for (cx,cy,z),rows in groups.items():
            expected = {(cx*512+x,cy*512+y) for x in (127,255,383,511) for y in (127,255,383,511)}
            if len(rows) != 16 or {(i.x,i.y) for _,i in rows} != expected:
                continue
            if not (where[0]<=cx*512 and where[1]<=cy*512 and cx*512+511<=where[2] and cy*512+511<=where[3]):
                continue
            if any(i.is_glob_egg and (i.x//512,i.y//512)==(cx,cy) for i in self.items):
                continue
            candidates.append((cx,cy,z,rows))
        candidates.sort(key=lambda c:random.Random(f'{self.seed}:loose:{c[:3]}').random())
        count = int(len(candidates)*share)//len(family)*len(family)
        replacements=[];used=Counter();chosen={}
        for cx,cy,z,rows in candidates:
            if len(replacements)>=count: break
            for number in sorted(set(family),key=lambda n:(used[n],n)):
                if used[number]>=count//len(family):continue
                pieces=self.globs.glob_to_items(number,cx*512,cy*512,z)
                if len(pieces)!=16 or {(i.x,i.y) for i in pieces}!={(i.x,i.y) for _,i in rows}:continue
                if any(p.z!=z for p in pieces):continue
                if any(self.sorter.info(i.shape)['zd'] or dm.item_class(self.sorter.info(i.shape),i.shape,i.frame) not in ('ground','void') for i in pieces):continue
                # A floor replacement may change appearance, never support.
                old_by_xy = {(i.x,i.y):self.sorter.info(i.shape) for _,i in rows}
                old_items = {(i.x,i.y):i for _,i in rows}
                if any(self.shapes[p.shape].flags0 != self.shapes[old_items[p.x,p.y].shape].flags0 for p in pieces):continue
                if any(any(self.sorter.info(p.shape)[flag] != old_by_xy[p.x,p.y][flag]
                           for flag in ('xd','yd','land','solid','draw','occl','roof','trans','anim','editor')) for p in pieces):continue
                if self._accept(pieces,ground=True):continue
                if any(all(chosen.get((cx+(k-o)*dx,cy+(k-o)*dy))==number for k in range(3) if k!=o)
                       for dx,dy in ((1,0),(0,1)) for o in range(3)):continue
                replacements.append((rows,pieces));used[number]+=1;chosen[cx,cy]=number
                break
        if replacements and (len(used)<4 or max(used.values())/len(replacements)>.25):
            replacements=[]
        added=[]
        for rows,pieces in replacements:
            by_xy={(p.x,p.y):p for p in pieces}
            for k,old in rows:
                p=by_xy[old.x,old.y];self.items[k]=p;added.append(p)
        # Glob contents load after loose FIXED records. Retain all replaced
        # floors and overlapping same-height floor peers in FIXED order.
        for it in self.items:
            inf=self.sorter.info(it.shape)
            if inf['zd']==0 and dm.item_class(inf,it.shape,it.frame) in ('ground','void'):
                if any(it.z==p.z and xy_overlap(box(it,self.sorter),box(p,self.sorter)) for p in added):
                    self.floor_order.add(id(it))
        self.added.extend(added);self._refresh()
        self.ledger.append(dict(operation='swap_loose',changed=len(replacements),raw_delta=0))
        return added

    def _beyond_chunks(self, kind, *, where, z=0):
        self._mutable()
        if kind == 'shore' and self.mapnum in (10,13):
            raise ValueError('retail river-shore globs are excluded; cliff-shore prefabs await the Map 13 mock')
        families = {'stars': STARS, 'lava': LAVA_SEA, 'water': (262,298), 'shore': SHORE_SE,
                    'rock': (393,773,938,2313,1230), 'forest': GRASS_FOREST}
        if kind != 'dark' and kind not in families: raise ValueError(f'unknown beyond kind {kind}')
        real = [i for i in self.expanded if (i.shape,i.frame) != (564,2)]
        floors = floor_cells(real,self.shapes,eggs_as_chunks=False)
        cover = floor_cells(real,self.shapes,eggs_as_chunks=False,painted=True)
        void = cells_within_view(floors) - cover
        chunks = sorted({(x//512,y//512) for x,y in void})
        added = []
        for cx,cy in chunks:
            cb = (cx*512,cy*512,cx*512+511,cy*512+511)
            if not (where[0] <= cb[0] and where[1] <= cb[1] and cb[2] <= where[2] and cb[3] <= where[3]): continue
            if any((x//512,y//512)==(cx,cy) for x,y in cover): continue
            if any(id(i) in self.protected_raw and xy_overlap(cb,box(i,self.sorter)) for i in self.items): continue
            old = [i for i in self.items if i.shape==564 and i.frame==2 and (i.x//512,i.y//512)==(cx,cy)]
            if kind == 'dark':
                pieces = [MapItem.placed_item(cx*512+x,cy*512+y,z,564,2) for x in (255,511) for y in (255,511)]
                record = pieces
            else:
                choices = list(families[kind])
                random.Random(f'{self.seed}:{self.mapnum}:{cx}:{cy}').shuffle(choices)
                number = next((n for n in choices if not self._run_three(n,cx,cy)), None)
                if number is None: continue
                record = [MapItem.glob_egg(cx*512+255,cy*512+255,z,glob_index=number)]
                pieces = self.globs.glob_to_items(number,cx*512,cy*512,z)
                if not pieces: raise ValueError(f'empty beyond glob {number}')
                if any(self.sorter.info(p.shape)['solid'] and self.sorter.info(p.shape)['zd'] for p in pieces) and cells32(cb) & self.leg_mask:
                    continue
            if self._accept(pieces,ground=True): continue
            self.items = [i for i in self.items if i not in old] + record
            self.added.extend(record); added.extend(record)
            for p in pieces: self._index(p)
        self._refresh()
        self.ledger.append(dict(operation='beyond', kind=kind, added=len(added)))
        return added

    def _star_placements(self, original):
        """Cover every viewing camera using anchors in visible ground chunks."""
        import numpy as np
        from lv_art_props import STAR_LAYOUTS, STAR_LAYOUT_INDEX, STAR_LAYOUTS_PER_SHAPE
        if not hasattr(self,'_sky_cameras'):
            points=set()
            for (cx,cy),(shape,frame,z,roof) in self.ground.items():
                top=z+self.sorter.info(shape)['zd']
                for dx in (-96,-64,-32,0,32):
                    for dy in (-96,-64,-32,0,32):
                        x,y=cx*128+127+dx,cy*128+127+dy
                        if x>=0 and y>=0:points.add((x,y,top))
            cameras=[]
            for x,y,z in sorted(points):
                for width,height in ((320,200),(640,400)):
                    cameras.append((x//4-y//4,x//8+y//8-z,width,height,x//512,y//512))
            self._sky_cameras=np.array(cameras,dtype=np.int32).reshape(-1,6)
        cams=self._sky_cameras
        si=self.sorter._make(original,0,0)
        l,t,r,b=si.sr
        # Include the gap between lattice cameras. Chunk visibility below
        # keeps an additional eight-pixel margin for that same gap.
        visible=((cams[:,0]+cams[:,2]//2+8>l) & (cams[:,0]-cams[:,2]//2-8<r) &
                 (cams[:,1]-20+cams[:,3]//2+8>t) & (cams[:,1]-20-cams[:,3]//2-8<b))
        cams=cams[visible]
        if not len(cams):return []
        candidates=[]
        for cx,cy in sorted({(int(c[4]),int(c[5])) for c in cams}):
            x,y=cx*512+original.x%512,cy*512+original.y%512
            layout=(x-original.x,y-original.y,original.x<0,original.y<0)
            k=STAR_LAYOUT_INDEX.get(layout)
            if k is None:raise ValueError(f'star anchor outside authored layouts: {layout}')
            item=MapItem.placed_item(x,y,0,916+k//STAR_LAYOUTS_PER_SHAPE,
                                    (k%STAR_LAYOUTS_PER_SHAPE)*9+original.frame)
            if self.reason(item,ground=True):continue
            scx,scy=(cx-cy)*128,(cx+cy)*64
            # CurrentMap::ChunkOnScreen, with a margin between samples.
            cover=((scx+128>cams[:,0]-cams[:,2]//2-128+8) &
                   (scx-128<cams[:,0]+cams[:,2]//2+128-8) &
                   (scy-256<cams[:,1]-20+cams[:,3]//2+64-8) &
                   (scy+128>cams[:,1]-cams[:,3]//2-64+8))
            candidates.append((item,cover))
        remaining=np.ones(len(cams),dtype=bool)
        chosen=[]
        while remaining.any():
            best=max(candidates,key=lambda row:int(np.count_nonzero(row[1]&remaining)),default=None)
            if best is None or not np.any(best[1]&remaining):return []
            chosen.append(best[0]);remaining &= ~best[1]
            candidates.remove(best)
        return chosen

    def beyond(self, kind, *, where, z=0, family=None, partial=False, north=False):
        """Fill visible void, retaining every rim and occupied cell.

        Stars also cover negative-coordinate view rays on a shifted plane.
        Plain deep water is the deliberately uniform glob 262.
        """
        self._mutable()
        if family is None and kind != 'deep_water' and not partial and not north:
            return self._beyond_chunks(kind,where=where,z=z)
        if kind == 'shore' and self.mapnum in (10,13):
            raise ValueError('retail river-shore globs are excluded; use LV cliff shores')
        families = {'stars': STARS, 'lava': LAVA_SEA, 'water': (262,298),
                    'deep_water': (262,), 'shore': SHORE_SE,
                    'rock': (393,773,938,2313,1230), 'forest': GRASS_FOREST}
        if kind != 'dark' and kind not in families:
            raise ValueError(f'unknown beyond kind {kind}')
        choices = tuple(family) if family is not None else families.get(kind,())
        if kind == 'deep_water' and choices != (262,):
            raise ValueError('plain deep water requires glob 262 alone')
        if kind != 'dark' and not choices:
            raise ValueError('empty beyond family')
        real = [i for i in self.expanded if (i.shape,i.frame) != (564,2)]
        floors = floor_cells(real,self.shapes,eggs_as_chunks=False)
        cover = floor_cells(real,self.shapes,eggs_as_chunks=False,painted=True)
        # Retail stars have no LAND or SEA flag, but paint their entire cell.
        from lv_art_props import STAR_LAYOUTS, STAR_LAYOUTS_PER_SHAPE
        for it in real:
            if it.shape!=351 and not 916<=it.shape<=928:continue
            x,y=it.x,it.y
            if 916<=it.shape<=928:
                dx,dy,nx,ny=STAR_LAYOUTS[(it.shape-916)*STAR_LAYOUTS_PER_SHAPE+it.frame//9]
                x,y=x-dx,y-dy
            elif it.z==252:
                x,y=x-1008,y-1008
            cover.add((x//128*128+127,y//128*128+127))
        void = cells_within_view(floors) - cover
        if kind == 'stars' and north:
            from lv_furnish import VIEW_RX, VIEW_RY
            r = max(VIEW_RX,VIEW_RY+128)//128+1
            for x,y in floors:
                surface=self.ground.get((x//128,y//128))
                height=(surface[2]+self.sorter.info(surface[0])['zd']) if surface else 0
                x=(x-4*height)//128*128+127
                y=(y-4*height)//128*128+127
                for dx in range(-r,r+1):
                    for dy in range(-r,r+1):
                        xx,yy = x+128*dx,y+128*dy
                        if (xx < 0 or yy < 0) and abs(dx-dy)*128<=VIEW_RX and abs(dx+dy)*128<=VIEW_RY+128:
                            if (xx,yy) not in cover:void.add((xx,yy))
        chunks = sorted({(x//512,y//512) for x,y in void})
        added=[]
        for cx,cy in chunks:
            cb=(cx*512,cy*512,cx*512+511,cy*512+511)
            # A north or west boundary of zero includes its visible virtual wedge.
            if not (where[0] <= max(0,cb[0]) and where[1] <= max(0,cb[1]) and
                    cb[2] <= where[2] and cb[3] <= where[3]):continue
            cells={(cx*512+x,cy*512+y) for x in (127,255,383,511) for y in (127,255,383,511)}
            wanted=cells & void
            full = len(wanted)==16 and cx>=0 and cy>=0
            order=list(choices)
            random.Random(f'{self.seed}:{self.mapnum}:{cx}:{cy}').shuffle(order)
            number=next((n for n in order if kind=='deep_water' or not self._run_three(n,cx,cy)),None)
            if kind=='dark':
                pieces=[MapItem.placed_item(x,y,z,564,2) for x,y in sorted(wanted) if x>=0 and y>=0]
                record=pieces
            else:
                if number is None:continue
                source=self.globs.glob_to_items(number,cx*512,cy*512,z)
                if not source:raise ValueError(f'empty beyond glob {number}')
                if not full and number==388:
                    continue
                if full and kind!='stars':
                    pieces=source
                    record=[MapItem.glob_egg(cx*512+255,cy*512+255,z,glob_index=number)]
                else:
                    # Partial fill uses complete ground or backdrop cells. Lava
                    # has an eight-unit tile box, unlike flat sea and stars.
                    # Architecture from a family override requires a whole chunk.
                    pieces=[]
                    for p in source:
                        inf=self.sorter.info(p.shape)
                        if ((p.x,p.y) not in wanted or inf['zd']>8 or
                            (inf['xd'],inf['yd'])!=(128,128) or
                            dm.item_class(inf,p.shape,p.frame) not in ('ground','void')):continue
                        if p.x<0 or p.y<0:
                            if kind!='stars':continue
                            pieces.extend(self._star_placements(p))
                            continue
                        if kind=='stars':
                            p=MapItem.placed_item(p.x,p.y,p.z,916,p.frame)
                        pieces.append(p)
                    record=pieces
            if not pieces:continue
            if any(self.sorter.info(p.shape)['solid'] and self.sorter.info(p.shape)['zd'] for p in pieces) and cells32(cb)&self.leg_mask:continue
            if self._accept(pieces,ground=True,prefab_stack=number==388):continue
            if number==388 and self._prefab_reachable_top(pieces):continue
            # Retain fallback plates: they paint behind cover, and deleting
            # a partial plate could expose its other three cells.
            if kind=='stars':
                # Raw sky records precede retained floors and remain raw.
                # Glob expansion would move them after the cloud's lobes.
                prefix=4623 if self.mapnum==39 else 0
                self.items=self.items[:prefix]+record+self.items[prefix:]
                self.floor_order.update(id(i) for i in record)
            else:
                self.items.extend(record)
            self.added.extend(record);added.extend(record)
            for p in pieces:self._index(p)
        self._refresh()
        self.ledger.append(dict(operation='beyond',kind=kind,added=len(added)))
        return added

    def pack(self):
        self._mutable()
        groups = defaultdict(list)
        pins = {(p['shape'],p['x'],p['y'],p['z']) for p in json.loads((HERE/'map_pins.json').read_text())['maps'].get(str(self.mapnum),[])}
        added_ids = {id(i) for i in self.added}
        for i in self.items:
            inf = self.sorter.info(i.shape)
            is_ground = dm.item_class(inf,i.shape,i.frame) == 'ground' or i.shape in (347,351)
            eligible = id(i) not in self.protected_raw and (is_ground or id(i) in added_ids) and self.shapes[i.shape].family_name not in ('SF_QUALITY','SF_CONTAINER','SF_UNKEGG','SF_GLOBEGG','SF_MONSTEREGG','SF_TELEPORTEGG')
            if (eligible and id(i) not in self.floor_order and not i.is_glob_egg and i.shape not in (73,500,508) and not i.quality
                    and not i.flags and not i.npcnum and not i.mapnum and not i.next_ptr and i.x%2 and i.y%2
                    and (i.shape,i.x,i.y,i.z) not in pins and not paints_window(i,self.sorter,self.windows)):
                groups[i.x//512,i.y//512,i.z].append(i)
        removed, eggs = set(), []
        for (cx,cy,z), pieces in sorted(groups.items()):
            if len(pieces) < 2: continue
            content = [(p.x-cx*512,p.y-cy*512,0,p.shape,p.frame) for p in pieces]
            num = lv_globs.register_packed(content)
            eggs.append(MapItem.glob_egg(cx*512+255,cy*512+255,z, num))
            removed.update(id(p) for p in pieces)
        self.items = [i for i in self.items if id(i) not in removed] + eggs
        if eggs:
            lv_globs.build()
            self.globs = GlobReader()
        self._refresh()
        self._budgets()
        doc = lv_globs.registry()
        doc.setdefault('dressing', {})[str(self.mapnum)] = dict(
            records=[i.to_bytes().hex() for i in self.added if id(i) not in removed],
            eggs=[i.to_bytes().hex() for i in eggs + self.swapped],
            reservations=self.reservations, ledger=self.ledger)
        lv_globs.MANIFEST.write_text(json.dumps(doc,indent=2)+'\n')
        self._packed = True
        return self.items

    def _budgets(self):
        from build_all_maps import RECORD_BUDGET, EXPANDED_RECORD_BUDGET
        if len(self.items) > RECORD_BUDGET[self.mapnum]: raise ValueError('raw record cap exceeded')
        if len(self.expanded) > EXPANDED_RECORD_BUDGET.get(self.mapnum, math.inf): raise ValueError('expanded record cap exceeded')
        m = dm.measure(self.src,self.mapnum,box=BUDGET_BOX.get(self.mapnum),raw=self.items)
        cells = m['ground'].get('cells',0)
        if self.mapnum in EXPANDED_PER_CELL and (not cells or m['records']['expanded']/cells > EXPANDED_PER_CELL[self.mapnum]):
            raise ValueError('expanded records per ground cell exceeded')

    def report(self):
        rows = []
        for name,kind,where in dm.REGIONS[self.mapnum]:
            metrics = dm.measure(self.src,self.mapnum,box=where,raw=self.items)
            rows.append(dict(name=name,kind=kind,metrics=metrics,failures=dm.check(metrics,dm.TARGETS[kind])))
        return dict(regions=rows, ledger=self.ledger, raw=len(self.items), expanded=len(self.expanded))

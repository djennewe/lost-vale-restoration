#!/usr/bin/env python3
"""pathfind.py — waypoints between two world points, over exact_reach's
engine-faithful standability lattice.

exact_reach.flood() answers "can he get there"; it does not say HOW. Driving
a cave leg by chasing the target in a straight line wedges against every
inlet (three times on 2026-09-01 in map 8's south cave). This does a BFS
with parents over the same lattice and the same z-delta table, then collapses
collinear runs into waypoints the walker can chase one at a time.

    pathfind.py --map 8 --from 29941,23317,8 --to 29800,23560,8 \
                --roi 28000,20000,32700,29500
"""
import argparse, os, sys
from collections import deque
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                '..', '..', 'agents', 'map-populator', 'src'))
import numpy as np
from exact_reach import (ExactReach, load_map, Z_SEARCH_OFFSETS_U8,
                         SI_SEA, FLG_FLIPPED)


class EngineVoidReach(ExactReach):
    """ExactReach with the engine's z<=0 rule instead of its stricter one.

    getPositionInfo ends `if (target._z <= 0) info.supported = true;`
    (current_map.cpp:773), so the engine walks the Avatar across a floorless
    void at ground zero. exact_reach deliberately refuses to model that,
    because "you can technically traverse the void" is not a verdict worth
    shipping on. For ROUTE-FINDING the deviation hides real routes: map 8's
    whole south cave is crossed that way, and with the strict model the
    south exit reads as unreachable when the engine walks straight to it.

    Use this for finding a way through, never for a walkability verdict.
    """

    def mask(self, level):
        if level > 0:
            return super().mask(level)
        if level in self._mask:
            return self._mask[level]
        bxd, byd, bzd = self.body
        blk = np.zeros((self.NX, self.NY), dtype=bool)
        for (bx, by, bz, bxd_, byd_, bzd_) in self.blockers:
            if bz >= level + bzd or bz + bzd_ <= level:
                continue
            i0, i1 = self._kx(bx - bxd_, bx + bxd)
            j0, j1 = self._ky(by - byd_, by + byd)
            if i0 <= i1 and j0 <= j1:
                blk[i0:i1 + 1, j0:j1 + 1] = True
        ok = ~blk
        self._mask[level] = ok
        return ok


class DryMixin:
    """Refuse cells whose only footing is water.

    exact_reach records a SI_SEA tile as `support` (it is SI_SOLID), and at
    level <= 0 a support alone makes a cell standable. The engine agrees the
    Avatar can step there — and then he drowns. On 2026-09-02 that routed a
    16,000-unit walk straight across the vale's lake at (15392, 14788) and
    killed him at full health in one poll interval.

    So subtract the sea tops from every level. A router that plots a course
    through a lake is not routing.
    """

    water_margin = 128

    def __init__(self, items, shapes, roi, *a, **kw):
        self.water_margin = kw.pop('water_margin', DryMixin.water_margin)
        super().__init__(items, shapes, roi, *a, **kw)
        self.seas = []
        for it in getattr(self, '_expanded', []) or _expand(items, shapes):
            if it.shape < 0 or it.shape >= len(shapes):
                continue
            si = shapes[it.shape]
            if not (si.flags0 & SI_SEA):
                continue
            xd, yd = si.footpad_x * 32, si.footpad_y * 32
            if it.flags & FLG_FLIPPED:
                xd, yd = yd, xd
            self.seas.append((it.x, it.y, (it.z & 0xFF) + si.footpad_z * 8,
                              xd, yd))
        self._drymask = {}

    def mask(self, level):
        if level in self._drymask:
            return self._drymask[level]
        ok = super().mask(level).copy()
        bxd, byd, _ = self.body
        m = self.water_margin
        for (sx, sy, top, sxd, syd) in self.seas:
            # A margin either side: the walker's bursts overshoot, and one
            # step off a shoreline lattice row is a drowning (2026-09-02,
            # twice). Keep the route a body's width clear of any water.
            if not (level - 8 <= top <= level + 8):
                continue
            sxd, syd = sxd + m, syd + m
            i0, i1 = self._kx(sx - sxd, sx + bxd + m)
            j0, j1 = self._ky(sy - syd, sy + byd + m)
            if i0 <= i1 and j0 <= j1:
                ok[i0:i1 + 1, j0:j1 + 1] = False
        self._drymask[level] = ok
        return ok


def _expand(items, shapes):
    from exact_reach import expand_globs, GlobReader
    try:
        return expand_globs(items, GlobReader())
    except TypeError:
        return expand_globs(items)


class DryReach(DryMixin, ExactReach):
    pass


def eroded_mask(er, level, n):
    """mask(level) with n lattice cells shaved off every edge.

    exact_reach reports a standable cell wherever the body box fits, and map
    item boxes are half-open, so two walls that meet can leave a seam ONE
    lattice row wide that the model calls open and the engine refuses. That
    is the aperture hazard `.claude/rules/map-geometry.md` was written for,
    and on 2026-09-01 it sent the walker at a wall for half an hour: the
    BFS routed through y=12863 on map 8, a single 4-unit row between two
    wall blocks, and every westward burst in the engine was refused.

    Eroding by one cell deletes such a seam while leaving any corridor
    wider than 2n cells intact. Use it for routes through tight cave.
    """
    m = er.mask(level)
    for _ in range(n):
        e = m.copy()
        e[1:, :] &= m[:-1, :]
        e[:-1, :] &= m[1:, :]
        e[:, 1:] &= m[:, :-1]
        e[:, :-1] &= m[:, 1:]
        m = e
    return m


def snap(er, x, y, z):
    i, j = er.index_of(x, y)
    best = None
    for L in er.levels:
        if er.mask(L)[i, j] and (best is None or abs(L - z) < abs(best - z)):
            best = L
    return (i, j, best)


def bfs(er, start, goal, erode=0):
    si, sj, sL = start
    gi, gj, gL = goal
    if sL is None or gL is None:
        return None
    deltas = [d for d in Z_SEARCH_OFFSETS_U8 if abs(d) <= er.step_z]
    lvlset = set(er.levels)
    masks = {L: (eroded_mask(er, L, erode) if erode else er.mask(L))
             for L in er.levels}
    prev = {(si, sj, sL): None}
    q = deque([(si, sj, sL)])
    while q:
        cur = q.popleft()
        if cur == (gi, gj, gL):
            path = []
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            return path[::-1]
        i, j, L = cur
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if not (0 <= ni < er.NX and 0 <= nj < er.NY):
                continue
            for d in deltas:
                nL = L + d
                if nL not in lvlset:
                    continue
                if not masks[nL][ni, nj]:
                    continue
                key = (ni, nj, nL)
                if key in prev:
                    continue
                prev[key] = cur
                q.append(key)
    return None


def waypoints(er, path):
    """Collapse collinear lattice steps; emit a turn point per direction
    change, plus every level change."""
    pts = [(er.x_of(i), er.y_of(j), L) for (i, j, L) in path]
    out = [pts[0]]
    for k in range(1, len(pts) - 1):
        ax, ay, az = pts[k - 1]
        bx, by, bz = pts[k]
        cx, cy, cz = pts[k + 1]
        turn = ((bx - ax, by - ay) != (cx - bx, cy - by))
        if turn or bz != az:
            out.append(pts[k])
    out.append(pts[-1])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', type=int, required=True)
    ap.add_argument('--from', dest='src', required=True)
    ap.add_argument('--to', dest='dst', required=True)
    ap.add_argument('--roi', required=True)
    ap.add_argument('--step', type=int, default=8)
    ap.add_argument('--erode', type=int, default=0,
                    help='shave N lattice cells off every walkable edge '
                         'before routing, to reject one-row seams the engine '
                         'refuses (see eroded_mask). 1 is usually right for '
                         'cave.')
    ap.add_argument('--step-z', type=int, default=8,
                    help='max z rise per lattice step (8 = walking. The vale '
                         'terraces are built to STEP_Z=24, so a route up one '
                         'needs 24).')
    ap.add_argument('--water-margin', type=int, default=128,
                    help='world units of shoreline kept out of the route '
                         '(default 128 = one body width).')
    ap.add_argument('--allow-water', action='store_true',
                    help='let the route cross SI_SEA tiles. Off by default: '
                         'the engine walks onto water and the Avatar drowns '
                         '(see DryMixin).')
    ap.add_argument('--engine-void', action='store_true',
                    help="model the engine's z<=0 freebie support, so routes "
                         "across a floorless void are found (see "
                         "EngineVoidReach). Route-finding only.")
    a = ap.parse_args()
    roi = tuple(int(v) for v in a.roi.split(','))
    sx, sy, sz = (int(v) for v in a.src.split(','))
    tx, ty, tz = (int(v) for v in a.dst.split(','))
    items, shapes = load_map(a.map)
    if a.engine_void:
        cls = EngineVoidReach if a.allow_water else type(
            'DryVoidReach', (DryMixin, EngineVoidReach), {})
    else:
        cls = ExactReach if a.allow_water else DryReach
    kw = {} if a.allow_water else {'water_margin': a.water_margin}
    er = cls(items, shapes, roi, step=a.step, step_z=a.step_z, **kw)
    s = snap(er, sx, sy, sz)
    g = snap(er, tx, ty, tz)
    print(f"start snapped to level {s[2]} at ({er.x_of(s[0])},{er.y_of(s[1])})")
    print(f"goal  snapped to level {g[2]} at ({er.x_of(g[0])},{er.y_of(g[1])})")
    p = bfs(er, s, g, erode=a.erode)
    if p is None:
        print("NO PATH"); return 1
    wps = waypoints(er, p)
    print(f"{len(p)} lattice steps, {len(wps)} waypoints:")
    print(" ".join(f"{x},{y}" for (x, y, z) in wps))
    print("z profile:", " ".join(str(z) for (x, y, z) in wps))
    return 0


if __name__ == '__main__':
    sys.exit(main())

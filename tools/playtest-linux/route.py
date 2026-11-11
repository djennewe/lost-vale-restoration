#!/usr/bin/env python3
"""route.py — compute walk waypoints between two world points on one map.

Builds map_walkability's WalkGrid over the built FIXED.DAT (globs expanded)
and runs a parent-tracked BFS from start to goal, then simplifies the cell
path to corner waypoints nav.py can drive.

Usage:  route.py MAP x1,y1,z1 x2,y2[,z2]      print waypoints, one per line
        route.py MAP ... --body 1|2           mover width in cells (default 2,
                                              the real Avatar; falls back to 1
                                              automatically if 2 finds no path)

Caveats (both learned the hard way — see .claude/rules/map-geometry.md):
  * The cell raster over-restricts unaligned 64-wide corridors at body 2 and
    cannot adjudicate single-body apertures at all. Waypoints are guidance
    for the engine's own walker, not proof of passability.
  * Dynamic items (doors seeded from U8SAVE.000 -> NONFIXED.DAT) are
    invisible to FIXED.DAT, so a route happily runs through a closed door.
    The driver has to notice and open it.
"""
import os
import sys
from collections import deque

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, 'agents', 'map-populator', 'src'))

from map_walkability import WalkGrid, GlobReader, load_typeflag, CELL, STEP_Z, SEA  # noqa: E402
from u8_map import MapArchive  # noqa: E402

FIXED = os.path.join(REPO, 'shared', 'build', 'FIXED.DAT')


def find_path(grid, start, goal, body_cells):
    """BFS identical to WalkGrid.flood's neighbour rule, plus parents.
    start: (x,y,z); goal: (x,y). Returns list of (ci,cj,level) or None."""
    x0r, y0r, x1r, y1r = grid.roi
    ci_lo, cj_lo = x0r // CELL, y0r // CELL
    ci_hi, cj_hi = x1r // CELL, y1r // CELL
    gci, gcj = grid.cell_of(goal[0], goal[1])

    sx, sy, sz = start
    ci, cj = grid.cell_of(sx, sy)
    seed = None
    for rec in grid.levels(ci, cj):
        if rec["kind"] == SEA or rec["blocked"]:
            continue
        d = abs(rec["level"] - sz)
        if d <= 2 * STEP_Z and (seed is None or d < seed[1]):
            seed = (rec["level"], d)
    if seed is None or not grid._body_fits(ci, cj, seed[0], body_cells):
        return None

    src = (ci, cj, seed[0])
    parent = {src: None}
    q = deque([src])
    hit = None
    while q:
        node = q.popleft()
        ci, cj, lv = node
        if (ci, cj) == (gci, gcj):
            hit = node
            break
        for ni, nj in ((ci + 1, cj), (ci - 1, cj), (ci, cj + 1), (ci, cj - 1)):
            if not (ci_lo <= ni <= ci_hi and cj_lo <= nj <= cj_hi):
                continue
            for rec in grid.levels(ni, nj):
                if rec["kind"] == SEA or rec["blocked"]:
                    continue
                nl = rec["level"]
                if abs(nl - lv) > STEP_Z:
                    continue
                if not grid._body_fits(ni, nj, nl, body_cells):
                    continue
                nxt = (ni, nj, nl)
                if nxt not in parent:
                    parent[nxt] = node
                    q.append(nxt)
    if hit is None:
        return None
    path = []
    node = hit
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def corners(path):
    """Collapse a cell path to its direction-change corners (plus ends)."""
    if len(path) < 3:
        return path
    out = [path[0]]
    for a, b, c in zip(path, path[1:], path[2:]):
        if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
            out.append(b)
    out.append(path[-1])
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    body = 2
    if '--body' in sys.argv:
        body = int(sys.argv[sys.argv.index('--body') + 1])
    mapnum = int(args[0])
    x1, y1, z1 = (int(v) for v in args[1].split(','))
    g = [int(v) for v in args[2].split(',')]
    x2, y2 = g[0], g[1]

    pad = 512
    roi = (min(x1, x2) - pad, min(y1, y2) - pad,
           max(x1, x2) + pad, max(y1, y2) + pad)

    archive = MapArchive(FIXED)
    shapes = load_typeflag()
    items = archive.get_map_items(mapnum)
    grid = WalkGrid(items, roi, shapes, glob_reader=GlobReader())

    path = find_path(grid, (x1, y1, z1), (x2, y2), body)
    used_body = body
    if path is None and body == 2:
        path = find_path(grid, (x1, y1, z1), (x2, y2), 1)
        used_body = 1
    if path is None:
        print("NO PATH", file=sys.stderr)
        sys.exit(1)

    print(f"# map {mapnum}  {len(path)} cells, body={used_body}"
          + ("  (WARNING: body-1 fallback — corridors may pinch)" if used_body != body else ""),
          file=sys.stderr)
    for ci, cj, lv in corners(path):
        print(f"{ci * CELL + CELL // 2},{cj * CELL + CELL // 2}")


if __name__ == '__main__':
    main()

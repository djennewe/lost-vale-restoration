#!/usr/bin/env python3
"""
test_map_hygiene.py — the three defect classes Map 18 had, measured on the
BUILT FIXED.DAT with globs expanded, one section each, ratcheted per map.

Cleanup plan Phase 0 (docs/reviews/2026-09-14-map-cleanup-plan.md §4). The
temple's rebuild found three things wrong with every Lost Vale interior and
this file exists so none of them comes back while the other maps are open:

  LATTICE     a floor glob that bakes walls (glob 80: sixteen flagstones
              plus four 40-tall pieces along the chunk's south edge), which
              tiled stamps a grid of stubs. Checked on the RAW eggs (quality
              80 on a shape-2 egg) and, after expansion, as any shape-15/47
              piece the glob brought that no builder placed.
  ROOFS       a 128-unit ceiling tile per 512-unit chunk — 6% cover, drawn
              as a grid of floating squares — and ceilings below head
              height, which CameraProcess::findRoof takes for the room's
              ceiling and clips at. Ceiling-shape items are grouped into
              4-connected components on the 128 grid at equal z; a
              component fails if it has fewer than 12 tiles OR its
              bounding-box coverage is under 90% (a pair repeated every 512
              units has two tiles and would pass a neighbour test — that is
              why coverage), unless its box lies inside a region the map
              declares; and every ceiling tile with a walking surface under
              it stands at least 40 above that surface.
  ORNAMENTS   shapes 489/492 — gargoyle caps, carved corners, barred
              windows, the base game's wall TOPS — laid as walls. At z=0
              never; above z=0 only with a wall piece directly beneath.
  PLACEHOLDERS 721 (chimney) as a column, 158 (stool) as an inscription,
              295 (wall relief) adrift on a floor, 78 (chest) as decoration,
              unless map_pins.json lists that placement as active or
              decorative-with-quality (a quest object nothing may move).

Every count is per map and RATCHETED: today's numbers are pinned below and
may only go down; a map's row reaches zero in the commit that cleans it.
Terrain tiles that carry the ROF flag (3, 242, 412 …) are floors and are not
ceilings — the ceiling set is the shapes whose engine role is a roof.

    python3 agents/map-populator/src/test_map_hygiene.py          # all
    python3 agents/map-populator/src/test_map_hygiene.py 17       # one map

Plain script: exit 0 on pass, 1 on fail.
"""

import json
import os
import sys
from collections import Counter, deque

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_map import MapArchive                      # noqa: E402
from map_preview import GlobReader, expand_globs   # noqa: E402
from parse_typeflag import load_typeflag           # noqa: E402
from lv_furnish import void_cells                  # noqa: E402

FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
TYPEFLAG = os.path.join(BASE_DIR, 'shared', 'build', 'TYPEFLAG.DAT')
PINS = os.path.join(SRC_DIR, 'map_pins.json')

LV_MAPS = (9, 10, 11, 13, 17, 18)

SI_SOLID, SI_LAND, SI_ROOF = 0x02, 0x08, 0x10

GLOB_LATTICE = 80
BAKED_PIECES = {15, 47}
CEILING_SHAPES = {9, 34, 37, 77, 162, 220, 335}    # engine role: a roof
ORNAMENTS = {489, 492}
WALL_SHAPES = {7, 8, 10, 12, 13, 14, 15, 26, 27, 28, 29, 30, 31, 32, 46, 47,
               145, 149, 489, 490, 492, 493, 497, 498, 506, 619}
PLACEHOLDERS = {721: 'chimney-as-column', 158: 'stool-as-inscription',
                295: 'relief-adrift', 78: 'chest-as-decoration'}
RELIEF = 295
RELIEF_REACH = 32           # a relief belongs on a wall face

MIN_ROOF_TILES = 12
MIN_ROOF_COVER = 0.90
MIN_HEADROOM = 40

# Declared roof regions: {map: [(x0, y0, x1, y1), ...]} — a component whose
# bounding box lies inside one is exempt from the size/cover test (a small
# porch roof that is meant to be small). None declared yet.
ROOF_REGIONS = {}


def shot_items(mapnum):
    """(shape, frame, x, y, z) of every 1994-screenshot item placed on
    `mapnum`. The shots are placed verbatim (vignettes, 2026-10-16), so a
    shot's own pieces are what the 1994 frame shows, not a roof a builder
    laid: screen17's stair rail is ceiling shape 335 a course apart down
    the steps, and screens 02 and 21 lay single ceiling tiles. The roof
    tests skip them. (1994-only art, ids 2000 and up, is left out: its
    builder maps it to a shape of its own, never a ceiling.)"""
    import vignette_place as VP
    out = set()
    for f in sorted(os.listdir(VP.VIGNETTE_DIR)):
        if f.startswith('screen') and f.endswith('.json'):
            vig = VP.load(f[:-5])
            if vig['placement']['map'] != mapnum:
                continue
            ox, oy, oz = VP.origin(vig)
            out |= {(it['shape'], it['frame'], it['x'] + ox, it['y'] + oy,
                     it['z'] + oz) for it in vig['items'] if it['shape'] < 2000}
    return out


# ── The ratchet ──────────────────────────────────────────────────────────
# Counted 2026-09-15 on FIXED.DAT c39b9c… (Map 18 rebuilt, the others not);
# void_in_view counted 2026-09-16 on 5ba149… (9: 1,404; 10: 10,599; 11:
# 9,941; 13: 3,004; 17: 3,859; 18: 2,206) and pinned at 0 for every map once
# each builder laid its void floor (lv_furnish.void_floor) that day. A number
# may only go DOWN. When a run prints a lower count, lower the pin
# in the same commit; when it prints a higher one, that is the regression.
#
# Map 17's NE-corner tapestry fix (2026-09-30, docs/playtest-2026-09-26-
# lamps-plaques-lb.md Finding 2) first tried dropping the void_floor()
# plate at (5887, 5119) that was painting over it, which held this ratchet
# at 0 only by leaving 4 cells uncovered — rejected on rework (the ratchet
# must never rise). The landed fix re-anchors that plate's y from 5119 to
# 5087 instead (build_map_17.py's _PLATE_Y_FIX): lv_furnish's own
# `_cell()` maps both to the identical 128-unit band, so the same cell
# stays covered, while the plate's box no longer reaches the wall's — see
# build_map_17.py for the full geometry. void_in_view is 0 for every map
# again.
RATCHET = {
    9:  {'glob80': 0, 'baked': 0, 'roof_small': 0, 'roof_sparse': 0,
         'roof_low': 0, 'orn_ground': 0, 'orn_unsupported': 0,
         'placeholders': 0, 'relief_adrift': 0,
         'void_in_view': 0},      # cleaned 2026-09-15
    10: {'glob80': 0, 'baked': 0, 'roof_small': 0, 'roof_sparse': 0,
         'roof_low': 0, 'orn_ground': 0, 'orn_unsupported': 0,
         'placeholders': 0, 'relief_adrift': 0,
         'void_in_view': 0},      # cleaned 2026-09-15
    11: {'glob80': 0, 'baked': 0, 'roof_small': 0, 'roof_sparse': 0,
         'roof_low': 0, 'orn_ground': 0, 'orn_unsupported': 0,
         'placeholders': 0, 'relief_adrift': 0,
         'void_in_view': 0},      # cleaned 2026-09-15
    13: {'glob80': 0, 'baked': 0, 'roof_small': 0, 'roof_sparse': 0,
         'roof_low': 0, 'orn_ground': 0, 'orn_unsupported': 0,
         'placeholders': 0, 'relief_adrift': 0,
         'void_in_view': 0},
    17: {'glob80': 0, 'baked': 0, 'roof_small': 0, 'roof_sparse': 0,
         'roof_low': 0, 'orn_ground': 0, 'orn_unsupported': 0,
         'placeholders': 0, 'relief_adrift': 0,
         'void_in_view': 0},      # cleaned 2026-09-15
    18: {'glob80': 0, 'baked': 0, 'roof_small': 0, 'roof_sparse': 0,
         'roof_low': 0, 'orn_ground': 0, 'orn_unsupported': 0,
         'placeholders': 0, 'relief_adrift': 0,
         'void_in_view': 0},
}

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def box(it, shapes):
    si = shapes[it.shape]
    return (it.x, it.y, it.z, si.footpad_x * 32, si.footpad_y * 32,
            si.footpad_z * 8)


def xy_overlaps(a, b):
    """Box::overlaps in x and y only (half-open, max-corner boxes)."""
    ax, ay, _, axd, ayd, _ = a
    bx, by, _, bxd, byd, _ = b
    if ax <= bx - bxd or bx <= ax - axd:
        return False
    if ay <= by - byd or by <= ay - ayd:
        return False
    return True


def load_pins():
    if not os.path.exists(PINS):
        return {}
    data = json.load(open(PINS))
    out = {}
    for m, rows in data.get('maps', {}).items():
        out[int(m)] = {(r['shape'], r['x'], r['y'], r['z'])
                       for r in rows if r.get('class') in ('active',
                                                           'decorative')}
    return out


def roof_components(roofs):
    """4-connected groups of ceiling tiles at equal z on the 128 grid (an
    8x8 tile spans 256, so both strides count as adjacent)."""
    pos = {(r.x, r.y, r.z) for r in roofs}
    seen, comps = set(), []
    for k in pos:
        if k in seen:
            continue
        comp, q = [], deque([k])
        seen.add(k)
        while q:
            c = q.popleft()
            comp.append(c)
            for dx, dy in ((128, 0), (-128, 0), (0, 128), (0, -128),
                           (256, 0), (-256, 0), (0, 256), (0, -256)):
                n = (c[0] + dx, c[1] + dy, c[2])
                if n in pos and n not in seen:
                    seen.add(n)
                    q.append(n)
        comps.append(comp)
    return comps


def measure(mapnum, shapes, arc, gr, pins):
    raw = arc.get_map_items(mapnum)
    items = expand_globs(raw, gr)
    counts = {}

    # LATTICE
    counts['glob80'] = sum(1 for i in raw
                           if i.shape == 2 and i.quality == GLOB_LATTICE)
    placed = Counter((i.x, i.y, i.z, i.shape, i.frame) for i in raw)
    counts['baked'] = sum(1 for i in items if i.shape in BAKED_PIECES
                          and (i.x, i.y, i.z, i.shape, i.frame) not in placed)

    # ROOFS
    shots = shot_items(mapnum)
    roofs = [i for i in items if i.shape in CEILING_SHAPES
             and (i.shape, i.frame, i.x, i.y, i.z) not in shots]
    # Walking surfaces: LAND items that are neither ceilings nor walls (the
    # cave wall pair carries the LAND flag, and a roof resting on a 48-tall
    # wall's top is support, not a ceiling over a floor).
    lands = [box(i, shapes) for i in items
             if shapes[i.shape].flags0 & SI_LAND
             and i.shape not in CEILING_SHAPES and i.shape not in WALL_SHAPES]
    small = sparse = 0
    regions = ROOF_REGIONS.get(mapnum, ())
    for comp in roof_components(roofs):
        xs = [c[0] for c in comp]
        ys = [c[1] for c in comp]
        if any(rx0 <= min(xs) and max(xs) <= rx1 and ry0 <= min(ys)
               and max(ys) <= ry1 for rx0, ry0, rx1, ry1 in regions):
            continue
        span = ((max(xs) - min(xs)) // 128 + 1) * ((max(ys) - min(ys)) // 128 + 1)
        if len(comp) < MIN_ROOF_TILES:
            small += len(comp)
        elif len(comp) / span < MIN_ROOF_COVER:
            sparse += len(comp)
    counts['roof_small'] = small
    counts['roof_sparse'] = sparse
    low = 0
    for r in roofs:
        rb = box(r, shapes)
        under = [lb[2] + lb[5] for lb in lands
                 if lb[2] + lb[5] < r.z and xy_overlaps(rb, lb)]
        if under and r.z - max(under) < MIN_HEADROOM:
            low += 1
    counts['roof_low'] = low

    # ORNAMENTS
    orn = [i for i in items if i.shape in ORNAMENTS]
    counts['orn_ground'] = sum(1 for i in orn if i.z == 0)
    walls = [box(i, shapes) for i in items if i.shape in WALL_SHAPES]
    unsupported = 0
    for i in orn:
        if i.z == 0:
            continue
        ib = box(i, shapes)
        if not any(wb[2] + wb[5] == i.z and xy_overlaps(ib, wb) for wb in walls):
            unsupported += 1
    counts['orn_unsupported'] = unsupported

    # PLACEHOLDERS
    pinned = pins.get(mapnum, set())
    ph = [i for i in items if i.shape in PLACEHOLDERS
          and (i.shape, i.x, i.y, i.z) not in pinned]
    counts['placeholders'] = len(ph)
    adrift = 0
    for i in ph:
        if i.shape != RELIEF:
            continue
        ib = box(i, shapes)
        near = (ib[0] + RELIEF_REACH, ib[1] + RELIEF_REACH, ib[2],
                ib[3] + 2 * RELIEF_REACH, ib[4] + 2 * RELIEF_REACH, ib[5])
        if not any(xy_overlaps(near, wb) for wb in walls):
            adrift += 1
    counts['relief_adrift'] = adrift

    # VOID IN VIEW (2026-09-16). The engine never clears the frame without
    # `usehighres`, so a void cell a player can see shows stale pixels.
    # lv_furnish.void_floor lays black plates under them; this counts what
    # is left (docs/playtest-2026-09-15-cloud-tiles.md, finding 1).
    counts['void_in_view'] = len(void_cells(items, shapes))
    return counts


def main(argv):
    print('=' * 70)
    print('Map hygiene — lattice, roofs, ornaments, placeholders; ratcheted')
    if not os.path.exists(FIXED) or not os.path.exists(TYPEFLAG):
        print('  shared/build artifacts absent — run tools/build_artifacts.sh')
        return 1
    shapes = load_typeflag(TYPEFLAG)
    arc = MapArchive(FIXED)
    gr = GlobReader()
    pins = load_pins()
    if pins:
        print(f'  map_pins.json: {sum(len(v) for v in pins.values())} pinned '
              f'placements exempt')
    else:
        print('  map_pins.json absent — every placeholder counts')

    maps = [int(a) for a in argv] or list(LV_MAPS)
    suggestion = {}
    for m in maps:
        counts = measure(m, shapes, arc, gr, pins)
        pinned = RATCHET.get(m, {})
        print(f'\n  map {m}: ' + '  '.join(f'{k}={v}' for k, v in counts.items()))
        for k, v in counts.items():
            limit = pinned.get(k, 0)
            check(f'map {m} {k} <= {limit}', v <= limit,
                  f'got {v} — a defect the cleanup removed has come back')
        if any(v < pinned.get(k, 0) for k, v in counts.items()):
            suggestion[m] = counts

    if suggestion:
        print('\n  Lower these pins in RATCHET (counts went DOWN):')
        for m, c in suggestion.items():
            print(f'    {m}: {c},')

    print()
    print('=' * 70)
    if failed:
        print(f'FAILED: {passed} passed, {failed} failed')
        return 1
    print(f'OK: {passed} passed, 0 failed')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

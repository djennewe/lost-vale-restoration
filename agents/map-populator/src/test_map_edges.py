#!/usr/bin/env python3
"""
test_map_edges.py — does every Lost Vale map have an edge?

The check each LV map got once by hand (docs/playtest-2026-09-19-map11-rim.md
B3/B4, docs/playtest-2026-09-19-map13-rim.md A3), made repeatable. Per map:

  footprint  the bbox of the 512-unit chunks that carry a glob egg — the
             same chunk set `build_rim()` reads off the builders' output,
             so it reproduces the footprints those reports tabulated.
  seeds      every teleport TARGET egg on the map (frame 1, the arrival
             pads), flooded together.
  ROI        the footprint grown by 3,000 units on every side, NOT clamped
             to the map: a footprint on the coordinate edge keeps its
             margin, so a walk off that edge shows.
  flood      `exact_reach.ExactReach` over the BUILT FIXED.DAT with globs
             expanded and the BUILT TYPEFLAG (shapes 860-866 exist only
             there), at a 32-unit lattice with 8-unit z steps, then
             `walk_off` — every step off an edge the engine takes, where it
             lands, and the walk on from there.
  verdict    PASS when all of these hold, FAIL otherwise:
               - the reached bbox lies inside the footprint on all four
                 sides, and at least one seed is standable (an empty flood
                 would otherwise read as contained);
               - nothing reached lies off the map: outside [0, 32768) on
                 either axis, where CurrentMap::addItem drops an item;
               - no step off an edge falls FALL_LETHAL (104) or more, which
                 kills (gravity_process.cpp). Falls of 80-103 hurt and are
                 listed, not failed: the Cloud Cliffs' narrow ledge is
                 exposed on purpose.

WHY THE FALLS (2026-10-10, playtest finding 4). A walk north on Map 13's
summit fell from z=120 to (3404,-164,0) and killed the Avatar. This test
passed: its ROI was clamped to y >= 0 ("margin 0 on north: a leak there
cannot show"), exact_reach dropped every item at y < 64 — the summit's
whole north row — and a flood only enters supported positions, so it
never sees the step that leaves them. All three are fixed.

The engine supports any position at z <= 0 unconditionally
(current_map.cpp:773), so a map without a rim can be walked off forever.
`exact_reach` is deliberately stricter and requires a real surface; the
void floor's black plates (564, SOLID|LAND) supply one out to the view
distance, which is how the hand checks saw the leaks. `--engine-z0`
applies the engine's own rule instead, so a leak shows even where no
plate lies.

PART OF tools/run_all_tests.sh since 2026-09-25. HANDOFF used to say maps
10 and 11 take minutes each at a 32-unit lattice; measured, the six LV
maps take about 12 s together with the edge walk (map 10 5.8 s, map 13
2.6 s; 3.5 s before 2026-10-10, without it).

Maps 8 and 39 are base-game maps with LV additions. Their glob footprint
is the retail map (Map 8's spans 0..32767), so "past the footprint" means
"past the coordinate space" and the check cannot discriminate there.
`--include-base` runs them for the record; their verdict is informational.
On FIXED 263d0a29 neither has a fall of 80 or more; Map 39's retail north
row is reachable at y=-1 (x 10239..21055), far from any LV addition.

    python3 agents/map-populator/src/test_map_edges.py
    python3 agents/map-populator/src/test_map_edges.py --maps 9,17
    python3 agents/map-populator/src/test_map_edges.py --include-base
    python3 agents/map-populator/src/test_map_edges.py \\
        --fixed /path/FIXED.DAT --typeflag /path/TYPEFLAG.DAT

Plain script: exit 0 when every LV map passes, 1 otherwise.
"""

import argparse
import hashlib
import os
import sys
import time

import numpy as np

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_map import MapArchive                                   # noqa: E402
from parse_typeflag import load_typeflag                        # noqa: E402
from exact_reach import ExactReach, AVATAR_BODY, FALL_LETHAL    # noqa: E402

FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
TYPEFLAG = os.path.join(BASE_DIR, 'shared', 'build', 'TYPEFLAG.DAT')

LV_MAPS = (9, 10, 11, 13, 17, 18)
BASE_MAPS = (8, 39)          # retail maps with LV additions
CHUNK = 512
MARGIN = 3000
DEFAULT_STEP = 32
DEFAULT_STEP_Z = 8


class EngineZ0Reach(ExactReach):
    """ExactReach with the engine's own z <= 0 rule: any unblocked
    position at ground zero is standable, surface or not."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        if 0 not in self.levels:
            self.levels = sorted(set(self.levels) | {0})

    def mask(self, level):
        if level > 0:
            return super().mask(level)
        if level not in self._mask:
            self._mask[level] = ~self.blocked(level)
        return self._mask[level]


def sha256_short(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()[:12]


# Black void markers (lv_furnish.void_floor's 564 plate, lv_cave_vignette's
# 35 f10 cell tile) and the invisible SI_EDITOR flats are LAND but are not
# ground anybody was meant to walk: they never widen the footprint.
NOT_GROUND = {564, 474, 636, 644, 686, 747, 761, 797}


def footprint(items, shapes=None):
    """(x0, y0, x1, y1) inclusive world bbox of the chunks with ground: a
    glob egg, or (since 2026-10-17, when the 1994-screenshot interiors
    began laying their floor as loose 301 tiles, lv_cave_vignette) a loose
    LAND flat at z 0 that is not a void marker; and (since 2026-10-17,
    phase B Map 13 pass d) a loose zero-height LAND floor at any z that is
    no roof: screen13's earth island lies at z 120 over Map 13's cloud
    sea, east of every z-0 floor, and its own ground read as a leak. A rim's
    125 crest (one unit tall) is not a floor and never widens it."""
    chunks = {(it.x // CHUNK, it.y // CHUNK) for it in items if it.is_glob_egg}
    if shapes is not None:
        for it in items:
            if it.is_glob_egg or it.shape in NOT_GROUND or \
                    (it.shape, it.frame) == (35, 10) or \
                    not 0 <= it.shape < len(shapes):
                continue
            si = shapes[it.shape]
            if si.flags0 & 0x08 and (
                    si.footpad_z <= 1 if not it.z else
                    si.footpad_z == 0 and not si.flags1 & 0x04):
                chunks.add((it.x // CHUNK, it.y // CHUNK))
    if not chunks:
        return None
    cxs = [c[0] for c in chunks]
    cys = [c[1] for c in chunks]
    return (min(cxs) * CHUNK, min(cys) * CHUNK,
            (max(cxs) + 1) * CHUNK - 1, (max(cys) + 1) * CHUNK - 1)


def _spread(falls, n):
    """The deepest fall in each 512-unit chunk, deepest first, at most n:
    one line per place rather than n lines along the same edge."""
    best = {}
    for f in falls:
        k = (f[0] // CHUNK, f[1] // CHUNK)
        if k not in best or f[2] - f[3] > best[k][2] - best[k][3]:
            best[k] = f
    return sorted(best.values(), key=lambda f: (f[3] - f[2], f[1], f[0]))[:n]


def check_map(mapnum, arc, shapes, step, step_z, engine_z0):
    t0 = time.perf_counter()
    items = arc.get_map_items(mapnum)
    out = {'map': mapnum, 'ok': False, 'lines': []}
    say = out['lines'].append
    if not items:
        say('no items in FIXED.DAT')
        out['elapsed'] = time.perf_counter() - t0
        return out
    fp = footprint(items, shapes)
    if fp is None:
        say('no glob eggs and no floor tiles: no footprint to check against')
        out['elapsed'] = time.perf_counter() - t0
        return out
    fx0, fy0, fx1, fy1 = fp
    roi = (fx0 - MARGIN, fy0 - MARGIN, fx1 + MARGIN, fy1 + MARGIN)
    seeds = [(it.x, it.y, it.z & 0xFF) for it in items
             if it.is_teleport_target]

    cls = EngineZ0Reach if engine_z0 else ExactReach
    er = cls(items, shapes, roi, body=AVATAR_BODY, step=step, step_z=step_z)
    reach, seeded = er.flood(seeds)

    say(f'footprint  x {fx0}..{fx1}  y {fy0}..{fy1}')
    say(f'roi        x {roi[0]}..{roi[2]}  y {roi[1]}..{roi[3]}  '
        f'lattice {er.NX}x{er.NY} @ {step}, {len(er.levels)} levels')
    landed = {s[:3]: s[3] for s in seeded}
    for s in seeds:
        if s in landed:
            say(f'seed       ({s[0]},{s[1]},{s[2]}) standing at z={landed[s]}')
        else:
            say(f'seed       ({s[0]},{s[1]},{s[2]}) NOT STANDABLE '
                f'(levels here: {er.standable_levels(s[0], s[1])})')
    if not seeds:
        say('FAIL: no teleport target on this map')
    elif not seeded:
        say('FAIL: no seed standable, the flood is empty')
    else:
        if len(seeded) < len(seeds):
            say(f'WARN: {len(seeds) - len(seeded)} of {len(seeds)} seeds '
                f'did not land')
        walk = er.walk_off(reach)
        reach = walk['reach']
        any_reach = np.zeros((er.NX, er.NY), dtype=bool)
        for r in reach.values():
            any_reach |= r
        ij = np.argwhere(any_reach)
        xs = er.X0 + ij[:, 0] * step
        ys = er.Y0 + ij[:, 1] * step
        tot, stand = er.summary(reach)
        bx0, bx1, by0, by1 = (int(xs.min()), int(xs.max()),
                              int(ys.min()), int(ys.max()))
        say(f'reached    {tot:,} of {stand:,} standable positions  '
            f'bbox x {bx0}..{bx1}  y {by0}..{by1}')
        word = 'OUTSIDE' if mapnum in BASE_MAPS else 'FAIL'
        bad = False
        out_mask = (xs < fx0) | (xs > fx1) | (ys < fy0) | (ys > fy1)
        sides = []
        if bx0 < fx0:
            sides.append(f'west to x={bx0} ({fx0 - bx0} past)')
        if bx1 > fx1:
            sides.append(f'east to x={bx1} ({bx1 - fx1} past)')
        if by0 < fy0:
            sides.append(f'north to y={by0} ({fy0 - by0} past)')
        if by1 > fy1:
            sides.append(f'south to y={by1} ({by1 - fy1} past)')
        if sides:
            bad = True
            say(f'{word}: {int(out_mask.sum()):,} reached positions outside '
                f'the footprint; leaks ' + ', '.join(sides))
            k = int(np.argmax(np.where(out_mask,
                                       np.maximum.reduce([fx0 - xs, xs - fx1,
                                                          fy0 - ys, ys - fy1]),
                                       -1)))
            say(f'           farthest reached: ({int(xs[k])},{int(ys[k])})')
        off = walk['off_map']
        if off:
            bad = True
            say(f'{"OFF-MAP" if mapnum in BASE_MAPS else "FAIL"}: '
                f'{len(off):,} positions a walk reaches lie off the map '
                f'(x {min(p[0] for p in off)}..{max(p[0] for p in off)}, '
                f'y {min(p[1] for p in off)}..{max(p[1] for p in off)}), '
                f'e.g. {off[0]}')
        lethal = [f for f in walk['falls'] if f[2] - f[3] >= FALL_LETHAL]
        hurts = [f for f in walk['falls'] if f[2] - f[3] < FALL_LETHAL]
        if lethal:
            bad = True
            say(f'{"LETHAL" if mapnum in BASE_MAPS else "FAIL"}: '
                f'{len(lethal):,} steps off an edge fall {FALL_LETHAL} or '
                f'more and kill; deepest:')
            for (x, y, z0, z1) in _spread(lethal, 6):
                say(f'           ({x},{y}) z={z0} -> {z1}  ({z0 - z1})')
        if hurts:
            drops = sorted({f[2] - f[3] for f in hurts})
            say(f'hurts      {len(hurts):,} steps off an edge fall '
                f'{drops[0]}..{drops[-1]} (survivable)')
        if walk['teeter']:
            say(f'teeter     {len(walk["teeter"]):,} positions resting on '
                f'an edge with no land under the centre')
        if not bad:
            out['ok'] = True
            say('PASS: inside the footprint, on the map, and no lethal drop')
    out['elapsed'] = time.perf_counter() - t0
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--maps', help='comma-separated map numbers '
                    f'(default: {",".join(map(str, LV_MAPS))})')
    ap.add_argument('--include-base', action='store_true',
                    help='also run the retail maps 8 and 39 (informational)')
    ap.add_argument('--step', type=int, default=DEFAULT_STEP)
    ap.add_argument('--step-z', type=int, default=DEFAULT_STEP_Z)
    ap.add_argument('--engine-z0', action='store_true',
                    help="the engine's z<=0 rule: void at ground zero is "
                         'walkable with no surface')
    ap.add_argument('--fixed', default=FIXED)
    ap.add_argument('--typeflag', default=TYPEFLAG)
    args = ap.parse_args(argv)

    if args.maps:
        maps = [int(m) for m in args.maps.split(',')]
    else:
        maps = list(LV_MAPS) + (list(BASE_MAPS) if args.include_base else [])
    for p in (args.fixed, args.typeflag):
        if not os.path.exists(p):
            print(f'missing {p}: build with tools/build_artifacts.sh')
            return 1

    print(f'FIXED.DAT {sha256_short(args.fixed)}…  '
          f'TYPEFLAG.DAT {sha256_short(args.typeflag)}…  '
          f'step {args.step}  step_z {args.step_z}  '
          f'z<=0 rule: {"engine" if args.engine_z0 else "surface required"}')
    shapes = load_typeflag(args.typeflag)
    arc = MapArchive(args.fixed)

    failed = []
    for m in maps:
        r = check_map(m, arc, shapes, args.step, args.step_z, args.engine_z0)
        base = m in BASE_MAPS
        tag = 'PASS' if r['ok'] else ('INFO' if base else 'FAIL')
        print(f'\nmap {m}: {tag}  ({r["elapsed"]:.1f} s)'
              + ('  [base map: not discriminating]' if base else ''))
        for line in r['lines']:
            print(f'  {line}')
        if not r['ok'] and not base:
            failed.append(m)

    print()
    if failed:
        print(f'FAILED: maps {", ".join(map(str, failed))} can be walked '
              'out of, off the map, or off a lethal edge')
        return 1
    print(f'all {len([m for m in maps if m not in BASE_MAPS])} LV maps '
          'contained: no leak, nothing off the map, no lethal drop')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""
test_crack_geometry.py — the Tiny Tar crack, checked with the ENGINE'S OWN
box arithmetic rather than the 32-unit cell raster.

WHY THIS FILE EXISTS (2026-07-28). The crack is the entire DD-005 entry
route: an aperture in Map 18's Inner Sanctum wall that the shrunken Avatar
(shape 867, footpad 1x1 = 32x32) fits through and the normal one (shape 1,
2x2 = 64x64) does not. It shipped "proven" by map_walkability's footprint
flood, and it was IMPASSABLE AT BOTH SIZES.

The flood rasterises to 32-unit cells and marks a cell blocked only when a
blocker covers the cell CENTRE. The engine does not round: item boxes are
half-open — `Box::contains` is `px > _x - _xd && px <= _x`, so a 96-wide
filler at x=2848 occupies 2753..2848 INCLUSIVE, eating the first unit of
cell 89. Clear span was 2849..2879 = 31 units for a body needing 32, and
`Box::overlaps` is strict, so there was no valid x at all. The raster could
not see the missing unit; that is not a bug in the flood so much as the
wrong instrument for a one-body-width aperture.

So this test reimplements `Box::overlaps` exactly (ultima8/misc/box.h) and
asks the only two questions that matter, directly:

    how many x positions inside the wall line admit a 32x32 body?  (>0)
    how many admit a 64x64 body?                                   (0)

Both numbers come from the BUILT FIXED.DAT with globs expanded, so it tests
what ships rather than what the builder intended.
"""

import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_map import MapArchive          # noqa: E402
from map_preview import GlobReader, expand_globs   # noqa: E402
from parse_typeflag import load_typeflag           # noqa: E402

FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
TYPEFLAG = os.path.join(BASE_DIR, 'shared', 'build', 'TYPEFLAG.DAT')

# The Inner Sanctum wall line on Map 18, and the x window the crack lives in.
WALL_Y = 6143
# Blockers are collected over a WIDER window than positions are searched in,
# so a candidate x near the search edge still has stone on both sides of it.
# Without that the run simply ends where the window does and reads as free.
BLOCK_LO, BLOCK_HI = 2400, 3500
X_LO, X_HI = 2700, 3100
SI_SOLID = 0x02        # ShapeInfo flags0 bit 1

BODY_TINY = 32         # shape 867 footpad 1x1 — the shrunken Avatar
BODY_FULL = 64         # shape 1   footpad 2x2 — the normal Avatar
FULL_HEIGHT = 40       # shape 1   footpad z 5 = 40 units

# The breach (2026-09-26): the wall records EggTempleEntry and EggCrackHint
# destroy once `templeOpen` is set (build_map_18.BREACH_QUALITY).
BREACH_QUALITY = 307

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def overlaps(a, b):
    """ultima8/misc/box.h Box::overlaps, verbatim. Boxes are half-open:
    (x-xd, x]. Every comparison here is <=, which is what makes an exact
    fit a MISS rather than a squeeze."""
    ax, ay, az, axd, ayd, azd = a
    bx, by, bz, bxd, byd, bzd = b
    if ax <= bx - bxd or bx <= ax - axd:
        return False
    if ay <= by - byd or by <= ay - ayd:
        return False
    if az + azd <= bz or bz + bzd <= az:
        return False
    return True


print('=' * 70)
print('Tiny Tar crack — engine box arithmetic, not the cell raster')

if not os.path.exists(FIXED) or not os.path.exists(TYPEFLAG):
    print('  shared/build artifacts absent — run tools/build_artifacts.sh')
    sys.exit(1)

shapes = load_typeflag(TYPEFLAG)
items = expand_globs(MapArchive(FIXED).get_map_items(18), GlobReader())

blockers = []
breach = []
for it in items:
    si = shapes[it.shape]
    xd, yd, zd = si.footpad_x * 32, si.footpad_y * 32, si.footpad_z * 8
    if not (si.flags0 & SI_SOLID) or zd <= 0:
        continue
    if BLOCK_LO <= it.x <= BLOCK_HI and WALL_Y - 64 <= it.y <= WALL_Y + 64:
        blockers.append((it.x, it.y, it.z, xd, yd, zd))
        if it.quality == BREACH_QUALITY:
            breach.append((it.x, it.y, it.z, xd, yd, zd))

check('the sanctum wall line has solid blockers to test against',
      len(blockers) >= 5, f'{len(blockers)} found')


def valid_positions(body):
    """x values where a body-sized box straddling the wall line fits."""
    return [x for x in range(X_LO, X_HI)
            if not any(overlaps((x, WALL_Y, 0, body, body, 32), b)
                       for b in blockers)]

tiny = valid_positions(BODY_TINY)
full = valid_positions(BODY_FULL)

print(f'  clear span for a {BODY_TINY}-unit body: {len(tiny)} positions'
      + (f'  [{tiny[0]}..{tiny[-1]}]' if tiny else ''))
print(f'  clear span for a {BODY_FULL}-unit body: {len(full)} positions'
      + (f'  [{full[0]}..{full[-1]}]' if full else ''))

# The mechanic, both halves. The margin assertion is the one that would have
# caught the shipped bug: a single valid position is an exact fit the walk
# code has to hit dead-on, and zero is a sealed temple.
check('the SHRUNKEN Avatar has somewhere to stand in the crack', bool(tiny),
      'the DD-005 entry route is sealed — the temple cannot be entered')
check('...with real margin, not a single exact-fit alignment',
      len(tiny) >= 8, f'only {len(tiny)} valid position(s)')
check('the NORMAL Avatar has nowhere — the crack is still the gate',
      not full, f'{len(full)} position(s): the puzzle is bypassable')

# And the clear span is contiguous: a body that fits must be able to walk
# straight through rather than teleport between disjoint pockets.
if tiny:
    check('the shrunken-Avatar positions are one contiguous run',
          tiny == list(range(tiny[0], tiny[-1] + 1)),
          'disjoint pockets — something else is inside the aperture')

# THE OPENED STATE. The same arithmetic with the breach records removed,
# which is what the wall is after either egg's sweep. The full-size body
# gets its real height here, 40, because the courses above the doorway are
# part of what goes: a doorway that only admitted a 32-tall box would be
# the exact-fit trap again, one axis over.
print()
print('Opened (templeOpen): the breach records removed')
check('exactly six wall records carry the breach quality',
      len(breach) == 6, f'{len(breach)} found')
standing = [b for b in blockers if b not in breach]


def valid_open(body, height):
    return [x for x in range(X_LO, X_HI)
            if not any(overlaps((x, WALL_Y, 0, body, body, height), b)
                       for b in standing)]

full_open = valid_open(BODY_FULL, FULL_HEIGHT)
print(f'  clear span for a {BODY_FULL}x{FULL_HEIGHT} body: {len(full_open)} '
      'positions' + (f'  [{full_open[0]}..{full_open[-1]}]'
                     if full_open else ''))
check('the NORMAL Avatar walks through the opened breach',
      bool(full_open), 'the sanctum still has no full-size exit')
check('...with real margin (a doorway, not a squeeze)',
      len(full_open) >= 64, f'only {len(full_open)} valid position(s)')
check('...as one contiguous run',
      full_open == list(range(full_open[0], full_open[-1] + 1))
      if full_open else False, 'disjoint pockets inside the doorway')
check('...and headroom: a 120-tall body fits too (no lintel left)',
      bool(valid_open(BODY_FULL, 120)), 'a course still spans the doorway')

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

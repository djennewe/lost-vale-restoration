#!/usr/bin/env python3
"""
test_uc_tiny_regrow.py — the Tiny Tar's two FREE processes, run out of the
BUILT shared/build/EUSECODE.FLX in the simulator (u8c_sim.py), against the
real Map 18 geometry in the built FIXED.DAT.

1. makeAvatarBig() asks canExistAt(TypeAvatar, ...) where the tiny Avatar
   stands and kills him if a full-size body cannot exist there. The tiny
   footpad (867, 32x32) shares its max-x/max-y anchor with the full one
   (shape 1, 64x64), so the full body reaches 32 units further toward -x
   and -y. A tiny Avatar flush against a wall to his north or west
   therefore died for standing beside it (playtest 2026-10-11, finding 2:
   the hall relief at (2592,5792,8)). lv-patched/FREE.UNK fix 4 tries the
   +32 shifts before the kill; a gap only the tiny body fits, which is what
   the 1994 death is for, must still kill.

2. Both ramps lower or raise a detached camera one z unit per half-step,
   16 in all, and the 1994 code then re-attached it with setCenterOn,
   which puts it back at the Avatar's z + 20 in one frame: the whole view
   jumped 16 px at the end of every shrink and regrow (finding 1). Fix 5
   returns it with FREE's own scrollBack, so no instant re-aim is larger
   than the 1-unit ramp steps.
"""

import json
import os
import struct
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

import build_eusecode  # noqa: E402
import lv_manifest  # noqa: E402
from u8_flex import FlexArchive  # noqa: E402
from u8c_codegen import CodeGenerator  # noqa: E402
from u8c_parser import parse_file  # noqa: E402
from u8c_sim import BUILD_FLX, UCSim, SimWorld  # noqa: E402
from u8c_symbols import create_symbol_table, LV_NPC_SHAPES  # noqa: E402

FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
FREE_SRC = os.path.join(SRC_DIR, 'lv-patched', 'FREE.UNK')

SHAPE_AVATAR = 1
SHAPE_TINY = 867
SHAPE_WALL = 15        # the Map 18 relief/wall course, 128x32x40, SOLID
FLG_FLIPPED = 0x0020   # item.h:682
MAP_TEMPLE = 18

passed = 0
failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


# ── where the two processes are in the built LVFREE class ──────────────
# Compiled with the symbol setup build_eusecode.build() gives the provider
# pre-pass, then compared byte for byte with the FLX entry, so the offsets
# below are the built class's own.
manifest = lv_manifest.Manifest.load_if_exists(
    lv_manifest.DEFAULT_MANIFEST_PATH)
LVFREE = manifest.classes['LVFREE']
symbols = create_symbol_table(flx_path=build_eusecode.BASE_FLX)
symbols.load_manifest(manifest)
for _n, _i in LV_NPC_SHAPES.items():
    symbols.register_class(_n, _i)
for _n, _i in manifest.classes.items():
    symbols.register_class(_n, _i)
_ast = parse_file(FREE_SRC)
for _gf in _ast.globalflags:
    symbols.allocate_global_flag(_gf.name, _gf.bits)
_cg = CodeGenerator(symbols, filename='FREE.UNK',
                    class_name_override='LVFREE')
_compiled = bytes(_cg.generate_class(_ast))
_built = FlexArchive(BUILD_FLX).get_object(LVFREE + 2)
print('LVFREE in the built EUSECODE.FLX')
check(f'lv-patched/FREE.UNK compiles to the built LVFREE (class {LVFREE})',
      _compiled == _built,
      f'compiled {len(_compiled)} B, built {len(_built or b"")} B: '
      f'rebuild with tools/build_artifacts.sh')
OFF_TINY = _cg._function_table['makeavatartiny'][0][0]
OFF_BIG = _cg._function_table['makeavatarbig'][0][0]


def map_solids(mapnum, x, y, radius=256):
    """The SOLID items of the built FIXED.DAT map within `radius` of
    (x, y), as (shape, frame, x, y, z). Record: '<HHBHBHHBBH'."""
    data = FlexArchive(FIXED).get_object(mapnum)
    out = []
    for off in range(0, len(data), 16):
        ix, iy, iz, shape, frame, flags = struct.unpack_from(
            '<HHBHBH', data, off)
        if abs(ix - x) > radius or abs(iy - y) > radius:
            continue
        out.append((shape, frame, ix, iy, iz, flags))
    return out


def regrow(x, y, z, solids):
    """Run makeAvatarBig() with the tiny Avatar at (x, y, z) among
    `solids` ((shape, frame, x, y, z[, flags])). Returns (sim, avatar)."""
    w = SimWorld()
    avatar = w.add(SHAPE_TINY, objid=1, frame=69, x=x, y=y, z=z,
                   mapnum=MAP_TEMPLE)
    for s in solids:
        if not w.shapeflags.blockflags(s[0]):
            continue
        w.add(s[0], frame=s[1], x=s[2], y=s[3], z=s[4])
    sim = UCSim(world=w)
    sim.follow_spawns = True   # scrollBack is an LVFREE process
    sim.run_event(LVFREE, OFF_BIG, 0)
    return sim, avatar


def killed(sim):
    return any(n == 'Item::receiveHit' for (n, _a, _r) in sim.intrinsic_log)


def exists_checks(sim):
    return [struct.unpack_from('<HHH', a, 0)[1:]
            for (n, a, _r) in sim.intrinsic_log if n == 'canExistAt']


# ── 1. regrowing beside a wall ─────────────────────────────────────────
print('\n1. makeAvatarBig() beside a wall, and inside a gap')

# 1a. The organic repro: Map 18 hall, walked N into the relief.
HALL = (2592, 5792, 8)
hall = map_solids(MAP_TEMPLE, HALL[0], HALL[1])
check('Map 18 FIXED has the hall relief course N of the spot '
      '(shape 15 at (2560,5760,0))',
      any(s[:5] == (SHAPE_WALL, 1, 2560, 5760, 0) for s in hall))
check('no item near the hall spot is flipped (the sim reads unflipped '
      'footpads)', not any(s[5] & FLG_FLIPPED for s in hall))
sim, av = regrow(*HALL, hall)
check('hall (2592,5792,8): a full body does not fit where he stands',
      exists_checks(sim)[:1] == [(2592, 5792)], exists_checks(sim))
check('hall: he is not killed', not killed(sim))
check('hall: he grows back full size (shape 1, frame 3)',
      (av.shape, av.frame) == (SHAPE_AVATAR, 3), (av.shape, av.frame))
check('hall: he regrows shifted +32 y, off the relief: (2592,5824,8)',
      (av.x, av.y, av.z) == (2592, 5824, 8), (av.x, av.y, av.z))

# 1a'. The teleported repro (finding 2, F2a): flush with the sanctum's
# side of the crack wall, which runs along its north edge.
SANCTUM = (2576, 6175, 0)
sanctum = map_solids(MAP_TEMPLE, SANCTUM[0], SANCTUM[1])
check('no item near the sanctum spot is flipped',
      not any(s[5] & FLG_FLIPPED for s in sanctum))
sim, av = regrow(*SANCTUM, sanctum)
check('sanctum wall (2576,6175,0): not killed, grows full size',
      not killed(sim) and av.shape == SHAPE_AVATAR, av.shape)
check('sanctum wall: shifted out of the wall corner to (2608,6207,0)',
      (av.x, av.y, av.z) == (2608, 6207, 0), (av.x, av.y, av.z))

# 1b. A west wall: the first try, +32 x, fits. Shape 15 is 128x32x40, so
# five courses anchored at x X-32 fill (X-160..X-32] x (Y-96..Y+64].
X, Y = 4000, 4000
west = [(SHAPE_WALL, 1, X - 32, Y + 32 * k, 0) for k in range(-2, 3)]
sim, av = regrow(X, Y, 0, west)
check('west wall: not killed', not killed(sim))
check('west wall: shifted +32 x (the first candidate)',
      (av.x, av.y) == (X + 32, Y), (av.x, av.y))

# 1c. A north-west corner: neither axis alone fits, both +32 does. The
# north course fills (X-32..X+96] x (Y-64..Y-32].
north = [(SHAPE_WALL, 1, X + 96, Y - 32, 0)]
sim, av = regrow(X, Y, 0, west + north)
check('NW corner: not killed', not killed(sim))
check('NW corner: shifted +32 x and +32 y',
      (av.x, av.y) == (X + 32, Y + 32), (av.x, av.y))

# 1d. Walls all round: a 32x32 pocket. Nothing fits; he dies where he
# stood, full size (fix 1's cleanup).
east = [(SHAPE_WALL, 1, X + 128, Y + 32 * k, 0) for k in range(-2, 3)]
south = [(SHAPE_WALL, 1, X + 96, Y + 32, 0)]
sim, av = regrow(X, Y, 0, west + east + north + south)
check('walls all round: killed', killed(sim))
check('walls all round: dies where he stood, full size',
      (av.x, av.y, av.shape) == (X, Y, SHAPE_AVATAR),
      (av.x, av.y, av.shape))

# 1e. Inside the Map 18 crack, before the breach: the 63-wide aperture
# in the 32-deep wall at y 6111..6143 that only the tiny body fits.
CRACK = (2852, 6143, 0)
crack = map_solids(MAP_TEMPLE, CRACK[0], CRACK[1])
check('Map 18 FIXED has the crack stub (shape 47 to x 2816) and the wall '
      'from x 2879', any(s[0] == 47 and s[2] == 2816 for s in crack)
      and any(s[2] - 128 == 2879 and s[3] == 6143 and s[4] == 0
              for s in crack))
check('no item near the crack is flipped',
      not any(s[5] & FLG_FLIPPED for s in crack))
sim, av = regrow(*CRACK, crack)
check('inside the crack (2852,6143,0): killed', killed(sim),
      exists_checks(sim))
check('inside the crack: dies where he stood',
      (av.x, av.y, av.z) == CRACK, (av.x, av.y, av.z))

# 1f. Open ground: no shift, and no probe anywhere but where he stands
# (fix 4's first test and the 1994 one both ask about the same spot).
sim, av = regrow(X, Y, 0, [])
check('open ground: grows where he stands, probing only that spot',
      (av.x, av.y) == (X, Y) and not killed(sim)
      and set(exists_checks(sim)) == {(X, Y)},
      (av.x, av.y, exists_checks(sim)))


# ── 2. the camera at the end of each ramp ──────────────────────────────
print('\n2. No camera snap at the end of the shrink or the regrow')


def instant_jumps(sim):
    """(intrinsic, size) for every instant re-aim that moved the camera."""
    out = []
    for (name, before, after) in sim.camera_moves:
        if name == 'Camera::scrollTo':
            continue
        d = max(abs(after[i] - before[i]) for i in range(3))
        if d:
            out.append((name, d))
    return out


def ramp(offset, shape, x, y, z, solids=()):
    w = SimWorld()
    avatar = w.add(shape, objid=1, frame=3, x=x, y=y, z=z,
                   mapnum=MAP_TEMPLE)
    for s in solids:
        w.add(s[0], frame=s[1], x=s[2], y=s[3], z=s[4])
    sim = UCSim(world=w)
    sim.follow_spawns = True
    sim.run_event(LVFREE, offset, 0)
    return sim, avatar


for label, offset, shape, solids, end in (
        ('shrink', OFF_TINY, SHAPE_AVATAR, (), (X, Y)),
        ('regrow', OFF_BIG, SHAPE_TINY, (), (X, Y)),
        ('shifted regrow', OFF_BIG, SHAPE_TINY, west, (X + 32, Y))):
    sim, av = ramp(offset, shape, X, Y, 0, solids)
    jumps = instant_jumps(sim)
    steps = [n for (n, _b, _a) in sim.camera_moves if n == 'Camera::move_to']
    check(f'{label}: the ramp still steps the camera 16 times', len(steps) == 16,
          len(steps))
    check(f'{label}: no instant camera jump larger than one unit',
          all(d <= 1 for (_n, d) in jumps), jumps)
    check(f'{label}: ends following the Avatar at ({end[0]},{end[1]},20)',
          sim.camera_follow == 1
          and sim.camera_location() == (end[0], end[1], 20)
          and (av.x, av.y) == end,
          (sim.camera_follow, sim.camera_location(), (av.x, av.y)))

print(f'\n{passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

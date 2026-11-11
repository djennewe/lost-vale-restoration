#!/usr/bin/env python3
"""
test_lv_tiny_avatar_art.py — guards the derivation of the Tiny Tar body
(shape 867) from the Avatar, art-track contract 8 (docs/art-track.md).

Sections 1-3 hold whichever candidate is picked (method, scale): they are
the integration's contract, not the art's. Section 4 pins the pick
Douglas made on 2026-10-11 (O60, the R2 glow ramp, a scaled stride).

  1. 867's own ANIM.DAT action table is shape 1's, frame for frame, except
     that the frames the ramp displaces (60-67, walk south-west) are
     renumbered past the end of the shape, no action reaches 60-69, and
     deltaDir is scaled per direction by cumulative rounding.
  2. The ramp joins the two bodies without a pop: frame 60 is shape 1
     frame 3 verbatim (the setType swap in FREE.UNK makeAvatarTiny, and
     the setFrame(3) after setType(TypeAvatar) in makeAvatarBig), frame 69
     is the tiny body's own frame 3 (AS_STAND southeast), and it never grows.
  3. Scaling is about the anchor, and every method's output encodes and
     passes validate_shape.
  4. The pick, and the glow ramp: same geometry as the plain ramp, the
     same two ends, tinted between them.

Reads the pristine base game (shared/data/u8-install, via base_input) and
nothing built, so it runs on a fresh clone with game data.
"""

import os
import struct
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(os.path.dirname(SRC)))
sys.path.insert(0, SRC)

import lv_tiny_avatar_art as T                                 # noqa: E402
from base_input import pristine_base                           # noqa: E402
from lv_tiny_avatar import actor_anim                          # noqa: E402
from lv_wood_wall import (encode_frame, encode_shape_blobs,    # noqa: E402
                          validate_shape)
from shape_viewer import read_flx_entry, load_palette, PALETTE_FILE  # noqa: E402

STATIC = os.path.join(BASE, 'shared', 'data', 'u8-install', 'STATIC')

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}' + (f'\n        {detail}' if detail else ''))


def _base(name, empty):
    return pristine_base(os.path.join(STATIC, name),
                         lambda p: empty(open(p, 'rb').read()), name)


flx = open(_base('U8SHAPES.FLX',
                 lambda d: not read_flx_entry(d, T.TINY_SHAPE)), 'rb').read()
anim = open(_base('ANIM.DAT',
                  lambda d: not T.anim_offset(d, T.TINY_SHAPE)), 'rb').read()
pal = load_palette(PALETTE_FILE)
avatar = T.decode_frames(read_flx_entry(flx, T.AVATAR_SHAPE))
quant = T.Quantizer(pal, T.used_indices(avatar))

print('-- 1. the action table')
check('shape 1 has 1550 frames', len(avatar) == 1550, f'got {len(avatar)}')
moved = T.relocated_frames(anim)
check('the ramp displaces exactly shape 1 frames 60-67 (walk, dir 5)',
      moved == list(range(60, 68)), f'got {moved}')
relocate = {old: len(avatar) + i for i, old in enumerate(moved)}
STRIDE = 0.6
out = T.avatar_anim_table(anim, relocate, STRIDE)
check('867 gets an entry, appended after the base file',
      T.anim_offset(out, T.TINY_SHAPE) == len(anim))
a = 4 * T.TINY_SHAPE
check('no byte of the base file moves except entry 867',
      out[:a] == anim[:a] and out[a + 4:len(anim)] == anim[a + 4:])
try:
    actor_anim(out, T.TINY_SHAPE)
    decodes = True
except ValueError as e:
    decodes = str(e)
check('lv_tiny_avatar.actor_anim (the engine-faithful decoder) reads it',
      decodes is True, decodes)
src, new = T.decode_anim(out, T.AVATAR_SHAPE), T.decode_anim(out, T.TINY_SHAPE)
check('the same 64-action set as shape 1', sorted(src) == sorted(new))
hdr = [k for k in src if src[k][:3] != new[k][:3]]
check('every action keeps size, flags and frame repeat', not hdr, f'{hdr}')
bad_frame, bad_other, bad_sum, refs = [], [], [], set()
for k in src:
    for d in range(8):
        s_dir, n_dir = src[k][3][d], new[k][3][d]
        for (sf, sz, ss, _sd, sfl), (nf, nz, ns, _nd, nfl) in zip(s_dir, n_dir):
            refs.add(nf)
            if nf != relocate.get(sf, sf):
                bad_frame.append((k, d, sf, nf))
            if (sz, ss, sfl) != (nz, ns, nfl):
                bad_other.append((k, d))
        total = sum(f[3] for f in s_dir)
        got = sum(f[3] for f in n_dir)
        if abs(got - total * STRIDE) > 0.5 + 1e-9:
            bad_sum.append((k, d, got, total * STRIDE))
check('frames are shape 1\'s, 60-67 renumbered to 1550-1557', not bad_frame,
      f'{bad_frame[:5]}')
check('deltaZ, sfx and frame flags are shape 1\'s', not bad_other,
      f'{bad_other[:5]}')
check(f'each direction\'s total travel is shape 1\'s x {STRIDE}, rounded once',
      not bad_sum, f'{bad_sum[:5]}')
hit = sorted(r for r in refs if T.RAMP_FIRST <= r <= T.RAMP_LAST)
check('no action shows a ramp frame (60-69)', not hit, f'{hit}')
check('every frame the table names exists (< 1558)', max(refs) < 1558,
      f'max {max(refs)}')
same = T.decode_anim(T.avatar_anim_table(anim, relocate, 1.0), T.TINY_SHAPE)
check('stride 1.0 keeps every deltaDir',
      all([f[3] for f in same[k][3][d]] == [f[3] for f in src[k][3][d]]
          for k in src for d in range(8)))
try:
    T.avatar_anim_table(out, relocate, STRIDE)
    refused = False
except ValueError:
    refused = True
check('refuses an ANIM.DAT that already has 867', refused)

print('-- 2. the ramp')
src3 = avatar[T.RAMP_SOURCE_FRAME]
stand = src[2][3]
check('shape 1 frame 3 is stand, south-east (stand dir 3)',
      stand[3][0][0] == T.RAMP_SOURCE_FRAME)
for method in T.METHODS:
    for s in (0.5, 0.6, 0.7):
        ramp = T.make_ramp(src3, s, method, quant)
        tiny3 = T.scale_frame(src3, s, method, quant)
        hs = [f['height'] for f in ramp]
        check(f'{method} {s}: 10 frames; 60 = shape 1 frame 3, 69 = tiny '
              f'frame 3; never grows',
              len(ramp) == 10 and ramp[0] == src3 and ramp[-1] == tiny3
              and all(b <= a for a, b in zip(hs, hs[1:])), f'heights {hs}')
check('ramp scales are geometric from 1 to s',
      abs(T.ramp_scales(0.6)[0] - 1) < 1e-12
      and abs(T.ramp_scales(0.6)[-1] - 0.6) < 1e-12)

print('-- 3. scaling')
SAMPLE = [0, 3, 10, 62, 90, 170, 410, 636, 986, 1193, 1369, 1509]
ident = [i for i in SAMPLE
         if T.scale_frame(avatar[i], 1.0, 'nearest', quant) != avatar[i]]
check('nearest at scale 1 is the identity', not ident, f'{ident}')
for method in T.METHODS:
    fr = [T.scale_frame(avatar[i], 0.6, method, quant) for i in SAMPLE]
    drift = [i for i, f in zip(SAMPLE, fr)
             if abs(f['yoff'] - avatar[i]['yoff'] * 0.6) > 1.5]
    check(f'{method}: the anchor scales with the frame (yoff ~ 0.6x)',
          not drift, f'{drift}')
    blob = encode_shape_blobs([encode_frame(f['pixels'], f['width'],
                                            f['height'], f['xoff'],
                                            f['yoff']) for f in fr])
    errs = validate_shape(blob)
    check(f'{method}: encodes and passes validate_shape', not errs,
          f'{errs[:3]}')
    colours = set().union(*(f['pixels'] for f in fr)) - {T.TRANSPARENT}
    check(f'{method}: only colours the Avatar wears',
          colours <= T.used_indices(avatar), f'{colours - T.used_indices(avatar)}')
o = T.scale_frame(src3, 0.6, 'outline', quant)
w, h = o['width'], o['height']
px = o['pixels']


def opaque(x, y):
    return 0 <= x < w and 0 <= y < h and px[y * w + x] != T.TRANSPARENT


edge = [(x, y) for y in range(h) for x in range(w) if opaque(x, y) and not
        all(opaque(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1),
                                                   (0, -1)))]
check('outline: every silhouette edge pixel is index 0, as on shape 1',
      edge and all(px[y * w + x] == T.OUTLINE_INDEX for x, y in edge))

print('-- 4. the pick (Douglas 2026-10-11) and the glow ramp')
check('O60: outline method at 0.6, glow 0.4, stride scaled with the body',
      (T.SCALE, T.METHOD, T.GLOW, T.STRIDE) == (0.6, 'outline', 0.4, 0.6),
      f'{(T.SCALE, T.METHOD, T.GLOW, T.STRIDE)}')
plain = T.make_ramp(src3, T.SCALE, T.METHOD, quant)
glow = T.make_ramp(src3, T.SCALE, T.METHOD, quant, glow=T.GLOW,
                   glow_quant=T.Quantizer(pal, range(T.TRANSPARENT)))
check('the glow ramp keeps both ends (60 = shape 1 frame 3, 69 = tiny '
      'frame 3)', glow[0] == plain[0] and glow[-1] == plain[-1])
check('the glow changes no frame\'s size or anchor',
      all((g['width'], g['height'], g['xoff'], g['yoff'])
          == (p['width'], p['height'], p['xoff'], p['yoff'])
          for g, p in zip(glow, plain)))


def lum(f):
    px_ = [p for p in f['pixels'] if p != T.TRANSPARENT]
    return sum(sum(pal[p]) for p in px_) / len(px_)


tinted = [k for k in range(1, 9) if lum(glow[k]) > lum(plain[k]) + 10]
check('frames 61-68 are paler than the plain ramp\'s (the tint)',
      tinted == list(range(1, 9)), f'tinted ramp steps {tinted}')

print(f'\n{passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

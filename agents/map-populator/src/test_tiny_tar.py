#!/usr/bin/env python3
"""
test_tiny_tar.py — guards the Tiny Tar potion, the last link in DD-005.

The temple is entered by shrinking and squeezing through a 32-unit crack in
Map 18's Inner Sanctum wall. map_walkability's Map 18 suite proves the crack
admits a 32x32 body and refuses a 64x64 one. This file proves the other
half: that something in the game can actually PRODUCE a 32x32 body.

That is a chain of five links, and every one of them was broken as recently
as 2026-07-27:

  1. shape 859 must exist with >= 9 frames        (766 has only 0-7)
  2. its TYPEFLAG must make it a carryable potion (slot was empty)
  3. TypePotion must resolve to 859               (was 340, a DOOR)
  4. TypeTinytar must resolve to a body SMALLER
     than the Avatar's                            (was 340: TWICE AS TALL)
 4b. that body must be shape 867, its own clone
     of the child actor 708 in U8SHAPES, TYPEFLAG
     and ANIM.DAT, with shape 1's weight/volume  (was bare 708: the pack
                                                   read weight 520 against
                                                   capacity 200)
  5. TypeAvatar must resolve to 1 so the Avatar
     can grow back                                (was unmapped -> push 0,
                                                   i.e. shape 0 on re-grow)

and a frame-8 potion must actually be placed somewhere reachable, or the
sealed sanctum is unreachable by any means.

Because the injections live in tools/build_artifacts.sh (step 3/8 for the
potion, 6/8 for the body), a regression here most likely means a step was
dropped rather than that someone edited a constant.
"""

import json
import os
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(os.path.dirname(SRC)))
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(BASE, 'agents', 'usecode-compiler', 'src'))

import shape_render as sr                       # noqa: E402
from parse_typeflag import ShapeInfo            # noqa: E402
from u8_map import MapArchive                   # noqa: E402
from lv_shapes import SHAPE_POTION_REAL         # noqa: E402
from u8c_symbols import TYPE_SHAPES             # noqa: E402
from lv_tiny_avatar import actor_anim, TINY_AVATAR_ID, TYPEFLAG_DONOR, \
    TINY_FRAMES                                 # noqa: E402
from lv_wood_wall import num_frames, validate_shape  # noqa: E402
from base_input import pristine_base            # noqa: E402
import lv_tiny_avatar_art as art                # noqa: E402

BUILD = os.path.join(BASE, 'shared', 'build')
TINY_TAR_FRAME = 8
DONOR = 766
AVATAR_SHAPE = 1

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


print('=' * 66)
print('Tiny Tar potion (DD-005) — the shrink chain')
print('=' * 66)

# 1. the shape
flx = open(os.path.join(BUILD, 'U8SHAPES.FLX'), 'rb').read()
data = sr.read_flx_entry(flx, SHAPE_POTION_REAL)
check(f'shape {SHAPE_POTION_REAL} exists in the built U8SHAPES.FLX',
      bool(data), 'build_artifacts.sh step 3/8 (lv_tiny_tar.py) did not run')
frames = sr.parse_shape_frames(data) if data else []
check(f'it has at least {TINY_TAR_FRAME + 1} frames '
      f'(POTION.UNK branches on 0-{TINY_TAR_FRAME})',
      len(frames) > TINY_TAR_FRAME, f'got {len(frames)}')

if len(frames) > TINY_TAR_FRAME:
    tar, red = frames[TINY_TAR_FRAME], frames[1]
    geo = ('width', 'height', 'xoff', 'yoff')
    check('frame 8 matches the donor geometry',
          all(tar[k] == red[k] for k in geo))
    # It must not simply be a copy of the red potion.
    check('frame 8 is recoloured, not a duplicate of frame 1',
          tar['pixels'] != red['pixels'])
    opaque = sum(1 for p in tar['pixels'] if p != 0xFF)
    check('frame 8 has the same opaque pixel count as frame 1 (only the '
          'liquid changed, glass and cork intact)',
          opaque == sum(1 for p in red['pixels'] if p != 0xFF))

# 2. TYPEFLAG
tf = open(os.path.join(BUILD, 'TYPEFLAG.DAT'), 'rb').read()
ent = tf[SHAPE_POTION_REAL * 8:(SHAPE_POTION_REAL + 1) * 8]
si = ShapeInfo(SHAPE_POTION_REAL, ent)
check('TYPEFLAG entry copied from the donor potion',
      ent == tf[DONOR * 8:(DONOR + 1) * 8])
check('it is NOT SI_FIXED (a potion you cannot pick up is no use)',
      not (si.flags0 & 0x01))

# 3/4/5. the type mappings
check(f'TypePotion -> {SHAPE_POTION_REAL} (was 340, which is a DOOR)',
      TYPE_SHAPES['TypePotion'] == SHAPE_POTION_REAL,
      f"got {TYPE_SHAPES['TypePotion']}")
tiny = TYPE_SHAPES['TypeTinytar']
check('TypeTinytar and TypeTinyAvatar agree (the 1994 tiers use both names)',
      tiny == TYPE_SHAPES['TypeTinyAvatar'])
tiny_si = ShapeInfo(tiny, tf[tiny * 8:(tiny + 1) * 8])
av_si = ShapeInfo(AVATAR_SHAPE, tf[AVATAR_SHAPE * 8:(AVATAR_SHAPE + 1) * 8])
check('the shrunken form is genuinely SMALLER than the Avatar in x and y — '
      'this is the entire mechanic',
      tiny_si.footpad_x < av_si.footpad_x and tiny_si.footpad_y < av_si.footpad_y,
      f'tiny=({tiny_si.footpad_x},{tiny_si.footpad_y}) '
      f'avatar=({av_si.footpad_x},{av_si.footpad_y})')
check('the shrunken form has frames 60-69 for the shrink animation',
      num_frames(sr.read_flx_entry(flx, tiny) or b'\0' * 6) >= 70)
check('the shrunken form is a container (inventory survives setType)',
      tiny_si.family == av_si.family,
      f'family {tiny_si.family} vs avatar {av_si.family}')
check('TypeAvatar -> 1, so makeAvatarBig can grow back (was unmapped, '
      'so the Avatar re-grew as SHAPE 0)',
      TYPE_SHAPES.get('TypeAvatar') == AVATAR_SHAPE,
      f"got {TYPE_SHAPES.get('TypeAvatar')}")

# 4b. the shrunken body has its OWN slot (2026-10-08), and since 2026-10-11
# it is the Avatar scaled down (art-track contract 8). setType() swaps the
# Avatar's own shape and the engine reads the Avatar's weight/capacity from
# that shape's TYPEFLAG row, so on bare 708 the pack read 520/200. 867 is
# shape 1's frames at 0.6 with the shrink ramp at 60-69, 708's TYPEFLAG
# row (footpad included: the crack, sanctum and hatch-box tests size the
# tiny body as 32x32x32) with the Avatar's weight and volume, and its own
# ANIM.DAT table, without which the engine will not move it.
# 867 is pinned literally: a game saved while shrunk stores the Avatar's
# shape, so renumbering the body would strand that save on an empty slot.
check('TypeTinytar -> 867, its own slot (708 is two placed village '
      'children; its row cannot change for the Avatar)',
      tiny == TINY_AVATAR_ID == 867, f'got {tiny}, builder {TINY_AVATAR_ID}')
body = sr.read_flx_entry(flx, TINY_AVATAR_ID) or b''
check(f'U8SHAPES slot {TINY_AVATAR_ID} holds {TINY_FRAMES} frames: shape 1\'s '
      f'1550 and the 8 the ramp displaces (build step 6, lv_tiny_avatar.py)',
      len(body) > 6 and num_frames(body) == TINY_FRAMES,
      f'{num_frames(body) if len(body) > 6 else 0} frames')
errs = validate_shape(body) if body else ['missing']
check(f'slot {TINY_AVATAR_ID} passes validate_shape', not errs, f'{errs[:3]}')
if len(body) > 6 and num_frames(body) == TINY_FRAMES:
    pal = sr.load_palette(sr.PALETTE_FILE)
    av_blob = sr.read_flx_entry(flx, AVATAR_SHAPE)
    av = {i: art.decode_frame(av_blob, i) for i in (*range(8), *range(60, 68))}
    quant = art.Quantizer(pal, art.used_indices(
        art.decode_frames(av_blob)))
    tiny_f = {i: art.decode_frame(body, i)
              for i in (*range(8), *range(60, 70), *range(1550, 1558))}
    check('frame 60 is shape 1 frame 3 verbatim (the setType swaps do not '
          'pop)', tiny_f[60] == av[3])
    check('frame 69 is the tiny body\'s own frame 3, the stand AS_STAND '
          'southeast shows next', tiny_f[69] == tiny_f[3])
    hs = [tiny_f[k]['height'] for k in range(60, 70)]
    check('the ramp 60-69 never grows', all(b <= a for a, b in
                                            zip(hs, hs[1:])), f'{hs}')
    want = {i: art.scale_frame(av[i], art.SCALE, art.METHOD, quant)
            for i in (*range(8), *range(60, 68))}
    check(f'stand frames 0-7 are shape 1\'s at {art.SCALE}, {art.METHOD}',
          all(tiny_f[i] == want[i] for i in range(8)))
    check('frames 1550-1557 are shape 1\'s walk-SW 60-67 at the same scale',
          all(tiny_f[1550 + i] == want[60 + i] for i in range(8)))
row, child_row = (tf[s * 8:(s + 1) * 8] for s in (TINY_AVATAR_ID,
                                                  TYPEFLAG_DONOR))
check(f'TYPEFLAG row {TINY_AVATAR_ID} = {TYPEFLAG_DONOR}\'s in bytes 0-5 '
      f'(flags, family, footpad, equip, anim)',
      row[:6] == child_row[:6], f'{row.hex()} vs {child_row.hex()}')
body_si = ShapeInfo(TINY_AVATAR_ID, row)
check('its footpad is (1,1,4) = 32x32x32, the body the Map 18 crack admits',
      (body_si.footpad_x, body_si.footpad_y, body_si.footpad_z) == (1, 1, 4),
      f'got ({body_si.footpad_x},{body_si.footpad_y},{body_si.footpad_z})')
check(f'its weight/volume are shape {AVATAR_SHAPE}\'s, so the pack reads the '
      f'same shrunk as grown (was 50/200 on 708: weight 520, capacity 200)',
      (body_si.weight, body_si.volume) == (av_si.weight, av_si.volume),
      f'got {body_si.weight}/{body_si.volume}, '
      f'avatar {av_si.weight}/{av_si.volume}')
anim_path = os.path.join(BUILD, 'ANIM.DAT')
anim = open(anim_path, 'rb').read() if os.path.exists(anim_path) else b''
check('shared/build/ANIM.DAT was built (the fifth artifact)', bool(anim))
if anim:
    body_anim = actor_anim(anim, TINY_AVATAR_ID)
    check(f'ANIM.DAT gives {TINY_AVATAR_ID} an animation entry '
          f'(AnimationTracker will not move an actor without one)',
          body_anim is not None)
    base_anim = open(pristine_base(
        os.path.join(BASE, 'shared', 'data', 'u8-install', 'STATIC',
                     'ANIM.DAT'),
        lambda p: not art.anim_offset(open(p, 'rb').read(), TINY_AVATAR_ID),
        'base ANIM.DAT'), 'rb').read()
    relocate = {60 + i: 1550 + i for i in range(8)}
    # The same step then points each actor clone (lv_monsters.py: the
    # monsters 872-873 and the 1994 NPC bodies 888-890) at its donor's
    # table; those entries are the only other change.
    from lv_monsters import ACTORS
    from lv_tiny_avatar import clone_anim_entry
    expect = art.avatar_anim_table(base_anim, relocate, art.STRIDE)
    for m in ACTORS:
        expect = clone_anim_entry(expect, m['shape'], m['donor'])
    check(f'entry {TINY_AVATAR_ID} is shape 1\'s table with walk-SW 60-67 '
          f'renumbered 1550-1557 and the stride x {art.STRIDE}, appended to '
          f'the base file (plus the actor clones\' entries)',
          anim == expect)
    tiny_acts = art.decode_anim(anim, TINY_AVATAR_ID)
    av_acts = art.decode_anim(anim, AVATAR_SHAPE)
    walk = [(sum(f[3] for f in tiny_acts[0][3][d]),
             sum(f[3] for f in av_acts[0][3][d])) for d in range(8)]
    check(f'a walk cycle travels {art.STRIDE} of the Avatar\'s in every '
          f'direction', all(abs(t - a * art.STRIDE) <= 0.5 for t, a in walk),
          f'{walk}')
    for action, name in ((3, 'jumpUp'), (14, 'die'), (4, 'standUp'),
                         (32, 'lookLeft'), (49, 'kneel2')):
        check(f'867 has shape 1\'s action {action} ({name}); 708 had none '
              f'for most of them', action in tiny_acts)

# 6. actually placed and reachable
arc = MapArchive(os.path.join(BUILD, 'FIXED.DAT'))
tt = [i for i in arc.get_map_items(10)
      if i.shape == SHAPE_POTION_REAL and i.frame == TINY_TAR_FRAME]
check('at least one frame-8 Tiny Tar is placed on Map 10 — without it the '
      'sealed sanctum is unreachable by ANY means', len(tt) >= 1)
check('there are SPARES (the shrink can kill you; Hrodny says "Potions", '
      'plural)', len(tt) >= 2, f'only {len(tt)} placed')
check('each carries npcnum 229 so TYPEPOTION (1253) dispatches on use',
      all(i.npcnum == 229 for i in tt),
      f'npcnums {[i.npcnum for i in tt]}')

print()
print(f'OK: {passed} passed, {failed} failed' if failed == 0
      else f'FAILED: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

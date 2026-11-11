#!/usr/bin/env python3
"""
test_uc_sim.py — Headless pre-playtest vetting of the wired quest logic,
executed straight out of the BUILT shared/build/EUSECODE.FLX via the
engine-faithful simulator (u8c_sim.py).

Covers the full COLPUZZL click matrix and the LBSCENE guard — the exact
scenarios that previously needed a human in ScummVM.
"""

import json
import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8c_sim import UCSim, SimWorld  # noqa: E402

MANIFEST = os.path.join(BASE_DIR, 'shared', 'build', 'lv_manifest.json')

_manifest = json.load(open(MANIFEST))
CLS = _manifest['classes']
FLAGS = {k: v['bit'] for k, v in _manifest['global_flags'].items()}

RECEPTACLE_CLASS = CLS['TYPERECEPTACLE']          # 1144
LBSCENE_CLASS = CLS['EGGLBSCENE']                 # 1455
LORDBRIT_CLASS = CLS['TYPELORDBRITISH']           # 1443
USE_EVENT_OFFSET = 0x0080

# The pillar shape is whatever COLPUZZL compiles into its search, which is
# TYPE_SHAPES['TypeElementalColumn'] (865 since 2026-09-24, art track
# contract 5; was 721). Read it from the table so this mirror cannot drift
# from the bytecode it exercises; test_art_props asserts the table equals
# what build_map_11 places. The receptacle shape is cosmetic (npcnum
# dispatch) and mirrors the map's 866.
from u8c_symbols import TYPE_SHAPES
SHAPE_RECEPTACLE = 866
SHAPE_PILLAR = TYPE_SHAPES['TypeElementalColumn']
SHAPE_GEM = 596
SHAPE_BOULDER = 66
SHAPE_AVATAR = 1
SHAPE_EGG = 73
SHAPE_GHOST = 411

# Map-side layout mirror (build_map_11.py four-pillars chamber)
PILLARS = {  # quality: (frame, px, py)
    201: (0, 7680, 20480),
    202: (1, 8704, 20480),
    203: (2, 7680, 21504),
    204: (3, 8704, 21504),
}
RECEPTACLE_POS = {
    201: (7680, 20736),
    202: (8704, 20736),
    203: (7935, 21759),     # build_map_11.FIRE_RECEPTACLE (2026-10-17)
    204: (8704, 21760),
}
OPPOSITE_FRAME = {201: 1, 202: 0, 203: 3, 204: 2}
FLAG_OF = {
    201: FLAGS['EarthColumnDestroyed'],
    202: FLAGS['AirColumnDestroyed'],
    203: FLAGS['FireColumnDestroyed'],
    204: FLAGS['WaterColumnDestroyed'],
}

QUAKE3 = 49

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


def build_chamber(gem_frames=(0, 1, 2, 3)):
    """Fixture: Avatar (objid 1) near the chamber with gems in inventory,
    four pillars + receptacles, boulder plug, ambient decoys."""
    w = SimWorld()
    avatar = w.add(SHAPE_AVATAR, objid=1, x=8192, y=20992, z=0)
    gems = {}
    for f in gem_frames:
        g = w.add(SHAPE_GEM, frame=f, quality=101 + f)
        w.put_in_container(g, avatar)
        gems[f] = g
    pillars = {}
    recept = {}
    for q, (f, px, py) in PILLARS.items():
        pillars[q] = w.add(SHAPE_PILLAR, frame=f, quality=q, x=px, y=py)
        rx, ry = RECEPTACLE_POS[q]
        recept[q] = w.add(SHAPE_RECEPTACLE, quality=q, x=rx, y=ry,
                          npcnum=120)
    boulders = [
        w.add(SHAPE_BOULDER, quality=299, x=8768, y=22528),
        w.add(SHAPE_BOULDER, quality=299, x=8896, y=22528),
    ]
    # Decoys the quality guard must protect: ambient rubble (66, q=0)
    # near the chamber, and the decorative entry pillars (721) far away.
    decoy_rubble = w.add(SHAPE_BOULDER, quality=0, x=8000, y=21000)
    w.add(SHAPE_PILLAR, frame=0, x=9216, y=1536)
    return w, avatar, gems, pillars, recept, boulders, decoy_rubble


def click(sim, receptacle):
    # use() by the event table: since 2026-09-25 the class also carries
    # look(), which compiles first and sits at 0x0080.
    return sim.run_event(RECEPTACLE_CLASS, None, receptacle.objid, event=1)


def single_click(sim, receptacle):
    return sim.run_event(RECEPTACLE_CLASS, None, receptacle.objid, event=0)


def barks_text(sim):
    return [t for (_o, t) in sim.barks]


print('=' * 66)
print('S1: correct gem on the Earth receptacle (q=201)')
w, avatar, gems, pillars, recept, boulders, rubble = build_chamber()
sim = UCSim(world=w)
click(sim, recept[201])
check('air gem (frame 1) consumed from inventory',
      gems[1].destroyed and gems[1].objid not in avatar.contents)
check('other gems untouched',
      not gems[0].destroyed and not gems[2].destroyed
      and not gems[3].destroyed)
check('earth pillar destroyed', pillars[201].destroyed)
check('other pillars intact',
      not pillars[202].destroyed and not pillars[203].destroyed
      and not pillars[204].destroyed)
check('EarthColumnDestroyed flag set',
      sim.get_global(FLAG_OF[201], 1) == 1)
check('success barks in order',
      barks_text(sim) == ['The air talisman howls with fury!',
                          'The earth column has been destroyed.'],
      f'got {barks_text(sim)}')
check('sparkle created shape 587',
      any(w.items[o].shape == 587 for o in sim.created),
      f'created shapes {[w.items[o].shape for o in sim.created]}')
qspawns = [s for s in sim.spawns if b'\x31\x00' in s['args']]
check('QUAKE3 (49) rumble spawned', len(qspawns) >= 1,
      f'spawn args: {[s["args"].hex() for s in sim.spawns]}')
check('boulders intact after one pillar',
      not boulders[0].destroyed and not boulders[1].destroyed)
check('no completion flag yet',
      sim.get_global(FLAGS['allColumnsDestroyed'], 1) == 0)
check('no unstubbed-intrinsic warnings',
      not [x for x in sim.warnings if 'unstubbed' in x],
      f'{sim.warnings}')

print()
print('S2: wrong gems only (opposite missing) — repel, consume nothing')
w, avatar, gems, pillars, recept, boulders, rubble = build_chamber(
    gem_frames=(0, 2, 3))   # no air gem for the earth receptacle
sim = UCSim(world=w)
click(sim, recept[201])
check('nothing consumed',
      all(not g.destroyed for g in gems.values()))
check('pillar intact', not pillars[201].destroyed)
check('repel bark',
      barks_text(sim) == ['The column flares with energy and repels you!'],
      f'got {barks_text(sim)}')
check('no flags set', sim.get_global(FLAG_OF[201], 1) == 0)

print()
print('S3: re-click after destruction — silent return')
w, avatar, gems, pillars, recept, boulders, rubble = build_chamber()
sim = UCSim(world=w)
click(sim, recept[201])
n_barks = len(sim.barks)
click(sim, recept[201])          # same receptacle again
check('no new barks on re-click', len(sim.barks) == n_barks,
      f'got {barks_text(sim)}')
check('no further gems consumed',
      sum(1 for g in gems.values() if g.destroyed) == 1)

print()
print('S4: full solve — all four, completion opens the way')
w, avatar, gems, pillars, recept, boulders, rubble = build_chamber()
sim = UCSim(world=w)
for q in (201, 202, 203, 204):
    click(sim, recept[q])
check('all gems consumed', all(g.destroyed for g in gems.values()))
check('all pillars destroyed', all(p.destroyed for p in pillars.values()))
check('all four element flags set',
      all(sim.get_global(FLAG_OF[q], 1) == 1 for q in FLAG_OF))
check('allColumnsDestroyed set',
      sim.get_global(FLAGS['allColumnsDestroyed'], 1) == 1)
check('both boulders destroyed',
      boulders[0].destroyed and boulders[1].destroyed)
check('ambient rubble (q=0) SURVIVES the completion sweep',
      not rubble.destroyed)
check('completion bark present',
      'The way to the Lost Vale is open!' in barks_text(sim),
      f'got {barks_text(sim)}')

print()
print('S5: unknown receptacle quality — guard, total no-op')
w, avatar, gems, pillars, recept, boulders, rubble = build_chamber()
odd = w.add(SHAPE_RECEPTACLE, quality=999, x=8192, y=21000, npcnum=120)
sim = UCSim(world=w)
click(sim, odd)
check('nothing consumed', all(not g.destroyed for g in gems.values()))
check('no barks', not sim.barks, f'{barks_text(sim)}')
check('no pillars destroyed',
      all(not p.destroyed for p in pillars.values()))

print()
print('S6: single click on a receptacle — look() names it, changes nothing')
w, avatar, gems, pillars, recept, boulders, rubble = build_chamber()
sim = UCSim(world=w)
single_click(sim, recept[201])
check('look bark', barks_text(sim) == ['pillar receptacle'],
      f'got {barks_text(sim)}')
check('look consumes nothing', all(not g.destroyed for g in gems.values()))
check('look destroys nothing',
      all(not p.destroyed for p in pillars.values()))

print()
print('E1: EggLBScene hatch, lbStarted clear — spawns the scene')
w = SimWorld()
w.add(SHAPE_AVATAR, objid=1, x=17150, y=20000, z=48)
egg = w.add(SHAPE_EGG, quality=304, x=17150, y=19700, z=48, npcnum=0x44)
ghost = w.add(SHAPE_GHOST, x=17150, y=19850, z=48)
sim = UCSim(world=w)
sim.run_event(LBSCENE_CLASS, USE_EVENT_OFFSET, egg.objid)
scene = [s for s in sim.spawns if s['class'] == LORDBRIT_CLASS]
check('spawns TypeLordBritish::use (0x0080)',
      len(scene) == 1 and scene[0]['offset'] == USE_EVENT_OFFSET,
      f'{sim.spawns}')
check('this pointer passed (this_size=4)',
      scene and scene[0]['this_size'] == 4)
check('apparition untouched', not ghost.destroyed)

print()
print('E2: EggLBScene hatch, lbStarted set — cleanup destroys apparition')
w = SimWorld()
w.add(SHAPE_AVATAR, objid=1, x=2200, y=2400, z=8)
egg = w.add(SHAPE_EGG, quality=304, x=2200, y=2230, z=8, npcnum=0x44)
ghost = w.add(SHAPE_GHOST, x=2200, y=2326, z=8)
far_ghost = w.add(SHAPE_GHOST, x=9999, y=9999, z=0)
sim = UCSim(world=w)
sim.set_global(FLAGS['lbStarted'], 1, 1)
sim.run_event(LBSCENE_CLASS, USE_EVENT_OFFSET, egg.objid)
check('no scene spawn',
      not [s for s in sim.spawns if s['class'] == LORDBRIT_CLASS])
check('adjacent apparition destroyed', ghost.destroyed)
check('distant apparition untouched', not far_ghost.destroyed)

print()
print('M4: a followed spawn resolves `this` against the PARENT stack')
# Synthetic two-class FLX rather than a quest scenario, so the assertion is
# about the mechanism and cannot drift when quest bytecode changes. The
# parent hands the child `push dword [BP+06]` — a pointer into its OWN
# frame, the idiom in front of nearly every spawn. Resolving that after the
# child's zeroed stack was installed silently yielded objid 0, so children
# ran with a null `this` in the sim while the engine gives them a real item.
import struct as _struct  # noqa: E402
from u8_flx_packer import FlxPacker  # noqa: E402

_CHILD, _PARENT, _ENTRY, _AVATAR = 0x0300, 0x0301, 32 * 4, 1


def _mk_class(code):
    tbl = bytearray(32 * 4)
    _struct.pack_into('<I', tbl, 1 * 4, _ENTRY)
    body = bytes(tbl) + code
    hdr = bytearray(12)
    _struct.pack_into('<I', hdr, 4, len(body) + 12)
    return bytes(hdr) + body


_packer = FlxPacker(title='M4 fixture')
# child: push word [BP+0A] (its own resolved `this`), pop to global 0 w16, ret
_packer.set_entry(_CHILD + 2, _mk_class(
    bytes([0x3F, 0x0A, 0x4F, 0x00, 0x00, 16, 0x50])))
# parent: push dword [BP+06] (this-POINTER), spawn child this_size=2, ret
_packer.set_entry(_PARENT + 2, _mk_class(
    bytes([0x40, 0x06, 0x57, 0x00, 0x02])
    + _struct.pack('<HH', _CHILD, _ENTRY) + bytes([0x50])))

_sim = UCSim(_packer.build(), world=SimWorld())
_sim.follow_spawns = True
_sim.run_event(_PARENT, _ENTRY, _AVATAR, event=1)
_seen = _sim.get_global(0, 16)
check('child sees the parent\'s this objid, not 0',
      _seen == _AVATAR,
      f'child observed this={_seen}, expected {_AVATAR}')
check('no null-this warning raised on a well-formed spawn',
      not [w for w in _sim.warnings if 'null this' in w],
      f'{_sim.warnings}')

print()
print('=' * 66)
print(f'{"OK" if failed == 0 else "FAILED"}: '
      f'{passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

#!/usr/bin/env python3
"""
test_uc_plntst.py — Headless scene proof for quest step 8, the Passage
Test, driven through the engine-faithful simulator (u8c_sim.py) against
the BUILT shared/build/EUSECODE.FLX.

Drives EggPlantTest::hatch() (event 7, this = the trigger egg) — the
map-wired trigger patched in lv-patched/PLNTST.UNK to run the full 1994
TESTPLAN scene instead of only clearing a mushroom. With the Passage
stone in the pack and thordisToldTest set, the hatch must:
  - consume the Passage stone (TypeBushKey, frame 0) from the Avatar;
  - teleport the Avatar to the SW test grounds (13055,30079,64);
  - teleport the accusing NPC in to (12927,29823,64);
  - pop the five whirlwind + plant pairs (the vision);
  - grant the Zealan Mark and poison the Avatar
    (haveMark / avatarPoisoned / firstPoisoned).

The z=64 terrain that catches this scene is built by
build_map_10.build_test_grounds() and asserted walkable by
map_walkability.run_map10 — this test proves the usecode HALF (that the
scene actually fires and lands the Avatar on those coordinates).

Known / deliberately-simplified behavior (see lv-patched/PLNTST.UNK):
  - give(TypeZealMark) returns 0 (push-0): TypeZealMark is unmapped, and
    give() is a cross-class stub in the sim — so no Mark ITEM is created
    here; the haveMark FLAG (asserted) is the quest-visible grant.
  - the per-pop safePlaySFX audio cue and the poison DAMAGE-tick process
    are omitted (cosmetic / separate workstream); the flags latch inline.
  - the follow_spawns wait()/FX spawns land in FREE routines the sim
    can't execute; they are dropped as no-ops (headless has no real time),
    which is why sim.warnings carries one 'follow_spawns: dropped' note.
"""

import json
import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8c_sim import UCSim, SimWorld  # noqa: E402
from u8c_symbols import TYPE_SHAPES  # noqa: E402  (stone/plant/wind shapes)

MANIFEST = os.path.join(BASE_DIR, 'shared', 'build', 'lv_manifest.json')
_m = json.load(open(MANIFEST))
CLS = _m['classes']
FLAGS = {k: v['bit'] for k, v in _m['global_flags'].items()}

EGGPLANTTEST = CLS['EGGPLANTTEST']              # 1434 (0x59A)
HATCH_EVENT = 7                                 # Egg::hatch
EGG_QUALITY = EGGPLANTTEST - 0x47F              # 283 — UnkEgg quality convention
SHAPE_EGG = 73
STONE_SHAPE = TYPE_SHAPES['TypeBushKey']        # 798 — the Passage stone
PLANT_SHAPE = TYPE_SHAPES['TypeShortmushroom']  # 871 — the Test Plant / vision plants
WIND_SHAPE = TYPE_SHAPES['TypeMiniAirTitan']    # 481 — MINIAIR, the whirlwind
SHAPE_AVATAR = 1

# Scene coordinates from TESTPLAN.UNK / lv-patched/PLNTST.UNK (all z=64).
AVATAR_TP = (13055, 30079, 64)
NPC_TP = (12927, 29823, 64)

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


def build_fixture(with_stone=True, thordis_told=True):
    """Avatar (objid 1) at the plateau entrance, a Test Plant + the PLNTST
    egg beside it, optionally the Passage stone in the Avatar's pack."""
    w = SimWorld()
    avatar = w.add(SHAPE_AVATAR, objid=1, x=12800, y=29300, z=64)
    stone = None
    if with_stone:
        stone = w.add(STONE_SHAPE, frame=0, quality=0)
        w.put_in_container(stone, avatar)
    plant = w.add(PLANT_SHAPE, frame=0, quality=10, x=12800, y=29408, z=64)
    egg = w.add(SHAPE_EGG, quality=EGG_QUALITY, x=12800, y=29440, z=64,
                npcnum=0x44)
    sim = UCSim(world=w)
    sim.follow_spawns = True
    for f in ('thordisToldTest', 'atliToldTest', 'haveMark',
              'avatarPoisoned', 'firstPoisoned', 'plantScene'):
        sim.set_global(FLAGS[f], 1, 0)
    sim.set_global(FLAGS['thordisToldTest' if thordis_told
                         else 'atliToldTest'], 1, 1)
    return w, avatar, stone, plant, egg, sim


def hatch(sim, egg):
    return sim.run_event(EGGPLANTTEST, 0, egg.objid, event=HATCH_EVENT)


def tp_coords(sim):
    return [(t['x'], t['y'], t['z']) for t in sim.teleports]


print('=' * 66)
print(f'driving EggPlantTest::hatch  (class {EGGPLANTTEST} = '
      f'0x{EGGPLANTTEST:03X}, event {HATCH_EVENT}, egg quality {EGG_QUALITY})')
print('=' * 66)

print('P1: stone in pack + thordisToldTest — the full Passage Test fires')
w, avatar, stone, plant, egg, sim = build_fixture(with_stone=True,
                                                  thordis_told=True)
hatch(sim, egg)
check('EggPlantTest is the pinned class 1434 (0x59A)',
      EGGPLANTTEST == 0x59A, f'got {EGGPLANTTEST}')
check('Passage stone consumed from the Avatar',
      stone.destroyed and stone.objid not in avatar.contents)
check('haveMark flag set', sim.get_global(FLAGS['haveMark'], 1) == 1)
# RE-ENABLED 2026-07-27 (was deliberately inverted 2026-07-26, decision A,
# while the cure was unreachable). The EggShades trigger is now placed on
# Map 10 (quality 294) and the ceremony's avatarPoisoned clear at
# SHADES.UNK:429 is reachable, so the poison line in lv-patched/PLNTST.UNK
# is restored and this assertion is back to the faithful == 1.
check('avatarPoisoned set (poison re-enabled with the cure wired)',
      sim.get_global(FLAGS['avatarPoisoned'], 1) == 1)
check('firstPoisoned flag set',
      sim.get_global(FLAGS['firstPoisoned'], 1) == 1)
check('plantScene flag set', sim.get_global(FLAGS['plantScene'], 1) == 1)
tps = tp_coords(sim)
check('Avatar.teleport to (13055,30079,64) recorded',
      AVATAR_TP in tps, f'teleports={sim.teleports}')
av_tp = [t for t in sim.teleports
         if (t['x'], t['y'], t['z']) == AVATAR_TP]
check('...and it teleports the Avatar (objid 1)',
      any(t['obj'] == 1 for t in av_tp), f'{av_tp}')
check('accusing NPC teleport to (12927,29823,64) recorded (Atli branch)',
      NPC_TP in tps, f'teleports={sim.teleports}')
created = [w.items[o].shape for o in sim.created]
check('five whirlwinds popped (TypeMiniAirTitan x5)',
      created.count(WIND_SHAPE) == 5, f'created shapes={created}')
check('five vision plants popped (TypeShortmushroom x5)',
      created.count(PLANT_SHAPE) == 5, f'created shapes={created}')
# KNOWN: give(TypeZealMark) push-0 — TypeZealMark is unmapped -> 0 and
# give() is a cross-class stub returning 0, so no Mark item is created;
# the Mark is granted through the haveMark flag (checked above).
zeal = TYPE_SHAPES.get('TypeZealMark', 0)
check('KNOWN give(TypeZealMark) push-0: no Mark item created (flag grants it)',
      (zeal == 0) or not any(w.items[o].shape == zeal for o in sim.created))

print()
print('P2: NO stone in pack — hatch is a guarded no-op')
w, avatar, stone, plant, egg, sim = build_fixture(with_stone=False,
                                                  thordis_told=True)
hatch(sim, egg)
check('no teleport without the stone', not sim.teleports,
      f'{sim.teleports}')
check('haveMark NOT set without the stone',
      sim.get_global(FLAGS['haveMark'], 1) == 0)
check('avatarPoisoned NOT set without the stone',
      sim.get_global(FLAGS['avatarPoisoned'], 1) == 0)
check('plantScene NOT set without the stone',
      sim.get_global(FLAGS['plantScene'], 1) == 0)
check('Test Plant survives (no vision)', not plant.destroyed)

print()
print('P3: atliToldTest branch — Thordis is the accuser instead')
w, avatar, stone, plant, egg, sim = build_fixture(with_stone=True,
                                                  thordis_told=False)
hatch(sim, egg)
tps = tp_coords(sim)
check('Avatar still teleports to (13055,30079,64)', AVATAR_TP in tps,
      f'{sim.teleports}')
check('accusing NPC teleport to (12927,29823,64) recorded (Thordis branch)',
      NPC_TP in tps, f'{sim.teleports}')
check('haveMark set; avatarPoisoned set (poison re-enabled, see above)',
      sim.get_global(FLAGS['haveMark'], 1) == 1
      and sim.get_global(FLAGS['avatarPoisoned'], 1) == 1)

print()
print('=' * 66)
print(f'{"OK" if failed == 0 else "FAILED"}: '
      f'{passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

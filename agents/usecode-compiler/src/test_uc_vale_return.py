#!/usr/bin/env python3
"""
test_uc_vale_return.py — Map 8's return to the Vale (teleport 212) is gated
on quest state, run through the simulator against the BUILT
shared/build/EUSECODE.FLX and FIXED.DAT.

THE DEFECT (docs/playtest-2026-10-11-replay-leg2.md finding 1). Trigger
212, Map 8 -> Map 10's pad 212, was an engine TeleportEgg on a pale slab in
the doors chamber's bone field. TeleportEgg::hatch is unconditional, and
the slab lies on the first-visit way in from the spitter corridor: a mouse
run E 3.54 s, N 2.5 s from the corridor's pocket landed a fresh player on
Map 10 with steps 3 (key, doors, Map 9) and 4 (Map 11) undone.

THE FIX. The trigger is EggValeReturn (lv-new/VALERTRN.UNK), a usecode egg
on the same spot with the same hatch box, which calls teleportToEgg(10,
212) only once allColumnsDestroyed is set: COLPUZZL's last pillar, the
flag that opens the only way into the Vale.

  V1  the egg is on Map 8, with the box the TeleportEgg had, and no
      TeleportEgg anywhere carries id 212 (it would fire past the gate)
  V2  flag unset (a first visit): the hatch teleports nowhere, and says
      nothing; partial pillar progress does not open it either
  V3  flag set: one teleportToEgg, to a map and pad id where FIXED.DAT has
      exactly one arrival pad, Map 10's 212 — the pairing that build_all_
      maps.verify_teleport_pairs can only check by id
  V4  the chain: solving Map 11's four receptacles in the simulator sets
      the bit the egg reads, and then it teleports
"""

import json
import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
MAP_SRC = os.path.join(BASE_DIR, 'agents', 'map-populator', 'src')
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, MAP_SRC)

from u8c_sim import UCSim, SimWorld  # noqa: E402
from u8c_symbols import TYPE_SHAPES  # noqa: E402
from u8_map import MapArchive  # noqa: E402

MANIFEST = os.path.join(BASE_DIR, 'shared', 'build', 'lv_manifest.json')
FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
_m = json.load(open(MANIFEST))
CLS = _m['classes']
FLAGS = {k: v['bit'] for k, v in _m['global_flags'].items()}

EGG_CLASS_BASE = 0x47F          # UnkEgg dispatch: class = quality + 0x47F
VALE_RETURN = CLS.get('EGGVALERETURN')
RECEPTACLE = CLS['TYPERECEPTACLE']
HATCH = 7
USE = 1
SHAPE_AVATAR = 1
SHAPE_EGG = 73
SHAPE_TALISMAN = TYPE_SHAPES['TypeTalisman']          # 596
SHAPE_RECEPTACLE = 866
RECEPTACLE_NPCNUM = 120
# The slab spot and box trigger 212 had as a TeleportEgg (FIXED 93affb0b):
# (20575,3903,0), npcnum 0x11 — build_map_08 TELE_213_TRIGGER_*.
SPOT = (20575, 3903, 0)
BOX_NPCNUM = 0x11
COLUMN_FLAGS = ('EarthColumnDestroyed', 'AirColumnDestroyed',
                'FireColumnDestroyed', 'WaterColumnDestroyed')

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


def flag(g, name):
    b = FLAGS[name]
    return (g[b >> 3] >> (b & 7)) & 1


def set_flag(g, name):
    b = FLAGS[name]
    g[b >> 3] |= 1 << (b & 7)


_archive = MapArchive(FIXED)


def hatch(g, egg_rec):
    """Hatch the Map 8 egg with globals `g`; return the sim."""
    w = SimWorld()
    w.add(SHAPE_AVATAR, objid=1, x=egg_rec.x, y=egg_rec.y,
          z=egg_rec.z & 0xFF)
    egg = w.add(egg_rec.shape, quality=egg_rec.quality, x=egg_rec.x,
                y=egg_rec.y, z=egg_rec.z & 0xFF, npcnum=egg_rec.npcnum)
    sim = UCSim(world=w, globals_bits=g)
    sim.run_event(VALE_RETURN, None, egg.objid, event=HATCH)
    return sim


print('=' * 70)
print('Map 8 trigger 212: the return to the Vale is gated on quest state')
print('=' * 70)

check('EggValeReturn is a manifest-pinned class',
      VALE_RETURN is not None, 'no EGGVALERETURN in lv_manifest.json')

# ── V1: the egg replaces the TeleportEgg, box for box ───────────────────
print()
print('V1: Map 8 carries the usecode egg, and no TeleportEgg carries 212')
m8 = _archive.get_map_items(8)
eggs = [it for it in m8 if it.shape == SHAPE_EGG
        and it.quality + EGG_CLASS_BASE == VALE_RETURN]
check('exactly one EggValeReturn egg on Map 8', len(eggs) == 1,
      f'{len(eggs)}')
ungated = [(m, it) for m in _archive.non_empty_maps()
           for it in _archive.get_map_items(m)
           if it.is_teleporter and (it.quality & 0xFF) == 212]
check('no engine TeleportEgg teleporter with id 212 on any map '
      '(TeleportEgg::hatch is unconditional)', not ungated,
      '; '.join(f'map {m} ({it.x},{it.y},{it.z & 0xFF})'
                for m, it in ungated))
others = [m for m in _archive.non_empty_maps() if m != 8
          for it in _archive.get_map_items(m)
          if it.shape == SHAPE_EGG
          and it.quality + EGG_CLASS_BASE == VALE_RETURN]
check('no EggValeReturn egg on any other map', not others, f'{others}')
if len(eggs) != 1:
    print(f'\nFAILED: {passed} passed, {failed} failed')
    sys.exit(1)
egg = eggs[0]
check(f'it stands on the slab spot {SPOT} with the old box (npcnum '
      f'{BOX_NPCNUM:#x})',
      (egg.x, egg.y, egg.z & 0xFF) == SPOT and egg.npcnum == BOX_NPCNUM,
      f'({egg.x},{egg.y},{egg.z & 0xFF}) npcnum {egg.npcnum:#x}')

# ── V2: the first visit — nothing happens ───────────────────────────────
print()
print('V2: allColumnsDestroyed unset (a first visit) — no teleport')
g = bytearray(0x1000)
sim = hatch(g, egg)
check('no teleportToEgg', not sim.egg_teleports, f'{sim.egg_teleports}')
check('no Actor teleport either', not sim.teleports, f'{sim.teleports}')
check('silent (no 1994 line fits, and none is written)', not sim.barks,
      f'{sim.barks}')
check('no unstubbed intrinsic', not sim.warnings, f'{sim.warnings}')
g = bytearray(0x1000)
for name in COLUMN_FLAGS[:3]:
    set_flag(g, name)
sim = hatch(g, egg)
check('three pillars down, the fourth standing: still no teleport',
      not sim.egg_teleports, f'{sim.egg_teleports}')

# ── V3: the Vale is open — the teleport, and where it lands ─────────────
print()
print('V3: allColumnsDestroyed set — one teleport, to a pad that exists')
g = bytearray(0x1000)
set_flag(g, 'allColumnsDestroyed')
sim = hatch(g, egg)
check('exactly one teleportToEgg', len(sim.egg_teleports) == 1,
      f'{sim.egg_teleports}')
check('no unstubbed intrinsic', not sim.warnings, f'{sim.warnings}')
if sim.egg_teleports:
    dest = sim.egg_teleports[0]
    check('it goes to Map 10, pad 212', (dest['map'], dest['egg']) ==
          (10, 212), f'{dest}')
    pads = [it for it in _archive.get_map_items(dest['map'])
            if it.is_teleport_target and (it.quality & 0xFF) == dest['egg']]
    check(f'Map {dest["map"]} has exactly one arrival pad {dest["egg"]} '
          f'(MainActor::teleport finds it by id)', len(pads) == 1,
          f'{len(pads)}')
    elsewhere = [m for m in _archive.non_empty_maps() if m != dest['map']
                 for it in _archive.get_map_items(m)
                 if it.is_teleport_target and
                 (it.quality & 0xFF) == dest['egg']]
    check(f'no other map carries a pad {dest["egg"]}', not elsewhere,
          f'{elsewhere}')
    back = [it for it in _archive.get_map_items(dest['map'])
            if it.is_teleporter and it.mapnum == 8]
    check('...and that map still has its trigger back to Map 8 (213)',
          [it.quality & 0xFF for it in back] == [213],
          f'{[it.quality & 0xFF for it in back]}')

# ── V4: the chain — Map 11's receptacles set the bit the egg reads ──────
print()
print('V4: solve Map 11 in the simulator, then step on the slab')
w = SimWorld()
av = w.add(SHAPE_AVATAR, objid=1, x=0, y=0, z=0)
for f in range(4):
    w.put_in_container(w.add(SHAPE_TALISMAN, frame=f, quality=101 + f), av)
for it in _archive.get_map_items(11):
    if it.is_glob_egg:
        continue
    w.add(it.shape, frame=it.frame, quality=it.quality, x=it.x, y=it.y,
          z=it.z & 0xFF, npcnum=it.npcnum)
g = bytearray(0x1000)
recs = [it for it in w.items.values() if it.shape == SHAPE_RECEPTACLE
        and it.npcnum == RECEPTACLE_NPCNUM]
check('Map 11 has its four receptacles', len(recs) == 4, f'{len(recs)}')
for r in recs:
    UCSim(world=w, globals_bits=g).run_event(RECEPTACLE, None, r.objid,
                                              event=USE)
check('solving sets allColumnsDestroyed', flag(g, 'allColumnsDestroyed'))
sim = hatch(g, egg)
check('...and then the slab sends him to Map 10 pad 212',
      [(d['map'], d['egg']) for d in sim.egg_teleports] == [(10, 212)],
      f'{sim.egg_teleports}')

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

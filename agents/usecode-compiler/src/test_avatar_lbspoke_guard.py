#!/usr/bin/env python3
"""test_avatar_lbspoke_guard.py: the Avatar's lbSpoke detour must not kill
the Lord British scene.

AVATAR::schedule()'s lbSpoke branch (lv-patched/AVATAR.UNK, original
lines 1277-1310) waits 240 ticks after the first map switch off the Docks,
then teleports the Avatar to MapLBBlackness and back. If Tenebrae's
EggLBScene had started TypeLordBritish::use() in those 240 ticks, the
teleport's map switch killed it mid-scene with lbStarted 1 and lbDone 0,
and quest step 1 could never finish (ScummVM 2026-10-01,
docs/playtest-2026-10-01-process-loops.md 1b, finding 8). The patch ends
the branch without teleporting once lbStarted is set.

Runs the BUILT shared/build/EUSECODE.FLX's class 0x401, event 8
(schedule), in the simulator. Exits nonzero on any failure.
"""
import json
import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8c_sim import UCSim, SimWorld, SimError  # noqa: E402

_m = json.load(open(os.path.join(BASE_DIR, 'shared', 'build',
                                 'lv_manifest.json')))
FLAGS = {k: (v['bit'], v['width']) for k, v in _m['global_flags'].items()}
AVATAR = 0x401
SCHEDULE = 8              # U8 event 8, Avatar::schedule
MAP_TENEBRAE = 39
MAP_LB_BLACKNESS = 0

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def run_schedule(lb_spoke, lb_started):
    w = SimWorld()
    av = w.add(1, objid=1, x=17150, y=19700, z=48)
    av.mapnum = MAP_TENEBRAE
    sim = UCSim(world=w)
    sim.set_global(*FLAGS['lbSpoke'], lb_spoke)
    sim.set_global(*FLAGS['lbStarted'], lb_started)
    try:
        sim.run_event(AVATAR, None, av.objid, event=SCHEDULE,
                      max_steps=200000)
    except SimError as e:
        check('schedule ran without a simulator error', False, str(e))
    return sim


print('Avatar::schedule, the lbSpoke detour (built EUSECODE.FLX)')

sim = run_schedule(lb_spoke=0, lb_started=1)
check('scene already started: the detour does not teleport',
      not sim.teleports, f'{sim.teleports}')
check('scene already started: lbSpoke is latched, so it never fires again',
      sim.get_global(*FLAGS['lbSpoke']) != 0)

sim = run_schedule(lb_spoke=0, lb_started=0)
maps = [t['map'] for t in sim.teleports]
check('scene not started: the 1994 detour still runs (to map 0 and back)',
      maps == [MAP_LB_BLACKNESS, MAP_TENEBRAE], f'{sim.teleports}')

sim = run_schedule(lb_spoke=1, lb_started=0)
check('lbSpoke already set: no detour', not sim.teleports, f'{sim.teleports}')

print(f'\n{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

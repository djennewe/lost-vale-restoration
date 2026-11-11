#!/usr/bin/env python3
"""fight.py — make the Avatar fight back.

The walker chases waypoints and reads position; a hostile that engages
simply kills it (a ghoul did, twice, on map 8's plateau on 2026-09-01).
This is the missing behaviour.

Mechanics, from U8AvatarMoverProcess::handleCombatMode:
  * combat mode is the `c` key (ACTION_COMBAT);
  * an attack is a DOUBLE LEFT CLICK, and its direction is `mousedir` —
    the cursor's direction from the centre of the 640x480 surface — unless
    MOVE_ANY_DIRECTION is set, so attack with no keys held;
  * the first double-click may be spent turning (checkTurn returns true),
    so repeat;
  * canAttack() gates on (25 - dex) frames, ~0.4 s at dex 15.

The attacker's object id comes from the live CombatProcess, which is how
the engine itself knows who is swinging at you.
"""
import math
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nav

DISP = ":77"
AIM_PX = 150          # cursor offset from centre; sets mousedir only


def xdo(*args):
    subprocess.run(["xdotool", *args],
                   env={**os.environ, "DISPLAY": DISP}, capture_output=True)


def attacker_id(near=None, ring=400):
    """Object id of whatever is swinging at us.

    NOT simply the first CombatProcess in the list: every hostile on the map
    runs its own combat AI, so the list is full of actors fighting each other
    somewhere else. On 2026-09-01 the first entry was a ghoul 22,241 units
    away and fight.py spent 40 rounds hitting the air. Take the nearest
    CombatProcess actor, and only if it is actually within reach.
    """
    out = nav.ask("Kernel::listProcesses")
    ids = [int(i) for i in re.findall(r"class CombatProcess, item (\d+)", out)]
    if not ids:
        return None
    if near is None:
        p = nav.pos()
        near = (p[0], p[1]) if p else None
    if near is None:
        return ids[0]
    best, bid = None, None
    for i in ids:
        info = actor_info(i)
        if not info:
            continue
        d = math.hypot(info[0] - near[0], info[1] - near[1])
        if best is None or d < best:
            best, bid = d, i
    if best is None or best > ring:
        print("  nearest CombatProcess actor is %s units away — not the "
              "attacker" % (int(best) if best is not None else "?"), flush=True)
        return None
    return bid


def actor_info(objid):
    out = nav.ask("ObjectManager::objectInfo %d" % objid)
    m = re.search(r"Item %d .*?\((-?\d+), (-?\d+), (-?\d+)\).*?Actor hp: (\d+)"
                  % objid, out, re.S)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))


def aim(dx, dy):
    """Point the cursor along world delta (dx, dy). Isometric basis:
    world +x -> screen (+2,+1), world +y -> screen (-2,+1)."""
    sx, sy = (dx - dy), (dx + dy) / 2.0
    n = max(abs(sx), abs(sy)) or 1
    sx, sy = int(round(sx / n * AIM_PX)), int(round(sy / n * AIM_PX))
    w = nav.win()
    if not w:
        return
    xdo("windowfocus", w)
    r = subprocess.run(["xdotool", "getwindowgeometry", "--shell", w],
                       env={**os.environ, "DISPLAY": DISP},
                       capture_output=True, text=True)
    g = dict(l.split("=") for l in r.stdout.strip().splitlines())
    xdo("mousemove",
        str(int(g["X"]) + int(g["WIDTH"]) // 2 + sx),
        str(int(g["Y"]) + int(g["HEIGHT"]) // 2 + sy))


def fight(rounds=40):
    tid = attacker_id()
    if tid is None:
        print("no CombatProcess — nothing is attacking", flush=True)
        return True
    print("attacker is object %d" % tid, flush=True)
    nav.resume()
    xdo("key", "c")                      # draw weapon / combat mode
    time.sleep(0.6)
    for r in range(rounds):
        me = nav.pos() or nav.pos()
        if not me:
            print("  (no position)", flush=True)
            return False
        hp = getattr(nav.pos, "last_hp", None)
        him = actor_info(tid)
        if him is None:
            print("  target gone", flush=True)
            break
        hx, hy, hz, hhp = him
        d = math.hypot(hx - me[0], hy - me[1])
        print("  round %d: me hp=%s at (%d,%d)  target hp=%d at (%d,%d) dist=%d"
              % (r, hp, me[0], me[1], hhp, hx, hy, int(d)), flush=True)
        if hhp <= 0:
            print("  target down", flush=True)
            break
        if hp is not None and hp <= 0:
            print("  DEAD", flush=True)
            return False
        aim(hx - me[0], hy - me[1])
        nav.resume()
        xdo("click", "--repeat", "2", "--delay", "80", "1")
        time.sleep(0.55)
    nav.resume()
    xdo("key", "c")                      # sheathe
    time.sleep(0.5)
    return True


if __name__ == "__main__":
    sys.exit(0 if fight() else 1)

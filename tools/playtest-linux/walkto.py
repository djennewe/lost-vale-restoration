#!/usr/bin/env python3
"""walkto.py x,y [x,y ...] — walk to world targets, no teleports, no cheats.

Position is read only (ObjectManager::objectInfo), never written.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nav

# nav.py: "240px offset = RUN gait; 130 walked, and walkers die to chasers
# (2026-08-12)". Walking the plateau at 130 is exactly how a ghoul killed the
# Avatar at (12470,11534) on 2026-09-01 — it kept pace and hit him three
# times. Run by default; drop to WALK_MAG only where precision matters.
RUN_MAG  = 240
WALK_MAG = 130
MAG = RUN_MAG
SPEED = 600.0          # world units/second at RUN_MAG
TOL = 96               # a run gait cannot stop inside 56

def goto(tx, ty, budget=40, tol=TOL, mag=None, speed=None):
    mag = mag or MAG
    speed = speed or (600.0 if mag >= RUN_MAG else 260.0)
    stalls = 0
    last = None
    hp0 = None
    for _ in range(budget):
        p = nav.pos() or nav.pos()
        if not p:
            print("  (no position)", flush=True); return None
        x, y, z, mp = p
        hp = getattr(nav.pos, 'last_hp', None)
        d = math.hypot(tx - x, ty - y)
        tag = ""
        if hp is not None:
            if hp0 is None:
                hp0 = hp
            elif hp < hp0:
                tag = f"  <-- TAKING DAMAGE ({hp0}->{hp}), running"
                hp0 = hp
                mag, speed = RUN_MAG, 600.0
        print(f"  ({x},{y},{z}) map {mp} hp={hp} dist={int(d)}{tag}", flush=True)
        if hp is not None and hp <= 0:
            print("  DEAD", flush=True); return None
        if d <= tol:
            return p
        if last is not None and abs(x-last[0]) + abs(y-last[1]) < 12:
            stalls += 1
            # On map 8 a "wedge" is almost always DIRECTIONAL: the Avatar
            # cannot go the way we asked but can go several others. Probing
            # the eight compass directions for one burst each frees him
            # nearly every time, so do that before declaring defeat.
            if stalls in (3, 6, 9):
                print("  stalled — probing 8 directions", flush=True)
                for (px, py) in ((140,-70), (-140,70), (140,70), (-140,-70),
                                 (280,0), (-280,0), (0,140), (0,-140)):
                    nav.resume()
                    nav.walk(px, py, 1.0)
                    q = nav.pos()
                    if q and abs(q[0]-x) + abs(q[1]-y) > 24:
                        print(f"    freed toward ({px},{py}) -> ({q[0]},{q[1]},{q[2]})",
                              flush=True)
                        stalls = 0
                        last = None
                        break
            if stalls >= 12:
                print("  WEDGED", flush=True); return None
        else:
            stalls = 0
        last = (x, y)
        secs = min(1.5, max(0.35, d / speed))
        if stalls:
            secs = min(1.6, secs * (1 + 0.4*stalls), d / speed * 1.6 + 0.25)
        sx, sy = nav.screen_dir(tx - x, ty - y, mag)
        nav.resume()
        nav.walk(sx, sy, secs)
    print("  BUDGET", flush=True)
    return None

if __name__ == '__main__':
    print("start:", nav.pos(), flush=True)
    args = sys.argv[1:]
    forced = None
    if args and args[0] == '--walk':
        forced = WALK_MAG; args = args[1:]
    for a in args:
        tx, ty = (int(v) for v in a.split(','))
        p = nav.pos() or nav.pos()
        d = math.hypot(tx - p[0], ty - p[1]) if p else 9999
        # A run gait cannot stop inside 96 units, so on a SHORT hop the
        # tolerance swallows the waypoint and the walker skips to the next
        # one — which is how it ended up chasing a target 1557 units away
        # through a wall on 2026-09-01. Short hops walk; long hops run.
        if forced:
            mag, tol = forced, 56
        elif d < 320:
            mag, tol = WALK_MAG, 56
        else:
            mag, tol = RUN_MAG, 96
        print(f"-> ({tx},{ty})  dist={int(d)} "
              f"{'walk' if mag == WALK_MAG else 'run'} tol={tol}", flush=True)
        if goto(tx, ty, mag=mag, tol=tol) is None:
            if mag == RUN_MAG:
                print("   retrying at walk gait", flush=True)
                if goto(tx, ty, mag=WALK_MAG, tol=56) is not None:
                    continue
            print("FAILED", flush=True); sys.exit(1)
    print("final:", nav.pos(), flush=True)

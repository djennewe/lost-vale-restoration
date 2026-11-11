#!/usr/bin/env python3
"""trek.py x,y [x,y ...] — walk with a camera nudge on every stall.

After the Sacred Circle ceremony the camera stops following the Avatar; he
walks out of the fast area and then stops moving entirely. The world is not
paused and he is not wedged — `CameraProcess::moveToAvatar` puts the camera
back and he walks on. This driver calls it whenever progress stops.
"""
import math, os, subprocess, sys, time
sys.path.insert(0, '~/projects/lost-vale/tools/playtest-linux')
import nav
LV = '~/projects/lost-vale/tools/playtest-linux/lv.sh'

def camera():
    subprocess.run(['bash', LV, 'q', 'CameraProcess::moveToAvatar'],
                   capture_output=True, text=True)
    subprocess.run(['bash', LV, 'detach'], capture_output=True, text=True)

targets = [tuple(int(v) for v in a.split(',')) for a in sys.argv[1:]]
camera()          # start centred: a stale camera stalls the very first burst
expect_map = None
for tx, ty in targets:
    stalls = 0
    last = None
    for i in range(26):
        p = nav.pos() or nav.pos()
        if not p:
            continue
        x, y, z, m = p
        # Waypoints are map-local. nav.goto has carried this guard since
        # 2026-08-12, when continuing past a teleport dragged the Avatar
        # 2,100 units into something lethal; trek.py shipped without it on
        # 2026-09-02 and killed him on the map 18 -> map 10 return, driving
        # him at a map-18 coordinate that on map 10 is half the vale away.
        if expect_map is None:
            expect_map = m
        elif m != expect_map:
            print(f"  MAP CHANGED {expect_map} -> {m} at ({x},{y},{z}); "
                  f"stopping", flush=True)
            print("final:", p)
            sys.exit(0)
        d = math.hypot(tx - x, ty - y)
        print(f"  ({x},{y},{z}) d={d:.0f}", flush=True)
        if d < 160:
            break
        if last is not None and abs(x - last[0]) + abs(y - last[1]) < 16:
            stalls += 1
            if stalls in (2, 7):
                print("   camera nudge", flush=True)
                camera()
            if stalls in (3, 4, 5, 6, 8, 9, 10, 11):
                # The temple entry zone is a warren; the aim direction can
                # be a wall while a neighbour is open. Sweep like walkto.
                for ddx, ddy in ((600,0),(0,600),(-600,0),(0,-600),
                                 (450,450),(-450,450),(450,-450),(-450,-450)):
                    ax, ay = nav.screen_dir(ddx, ddy, 220)
                    nav.resume(); nav.walk(ax, ay, 1.5)
                    q = nav.pos() or nav.pos()
                    if q and (q[0], q[1]) != (x, y):
                        print(f"   freed toward ({ddx},{ddy})", flush=True)
                        break
            if stalls > 12:
                print("  WEDGED", flush=True)
                break
        else:
            stalls = 0
        last = (x, y)
        sx, sy = nav.screen_dir(tx - x, ty - y, 200)
        nav.resume()
        nav.walk(sx, sy, min(1.3, max(0.5, d / 520.0)))
print("final:", nav.pos() or nav.pos())

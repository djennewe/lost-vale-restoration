#!/usr/bin/env python3
"""hike.py x,y [x,y ...] — per-step eight-direction escape driver.

trek.py only probes directions once it has already stalled; in the villages
the Avatar is boxed by huts on nearly every step and that is far too late.
This tries the aim direction first and falls through the compass until one
of them actually reduces the distance, every single step. Slower per step,
but it is the only thing that gets through the Gunnar village.
"""
import math, sys, subprocess
sys.path.insert(0, '~/projects/lost-vale/tools/playtest-linux')
import nav
LV = '~/projects/lost-vale/tools/playtest-linux/lv.sh'

def camera():
    subprocess.run(['bash', LV, 'q', 'CameraProcess::moveToAvatar'],
                   capture_output=True, text=True)
    subprocess.run(['bash', LV, 'detach'], capture_output=True, text=True)

camera()
targets = [tuple(int(v) for v in a.split(',')) for a in sys.argv[1:]]
expect = None
for TX, TY in targets:
    best = 1e9
    stuck = 0
    for i in range(40):
        p = nav.pos() or nav.pos()
        if not p:
            continue
        x, y, z, m = p
        if expect is None:
            expect = m
        elif m != expect:
            print(f"MAP CHANGED {expect} -> {m} at ({x},{y},{z}); stopping",
                  flush=True)
            print("final:", p)
            sys.exit(0)
        d = math.hypot(TX - x, TY - y)
        if d < best - 40:
            best = d
            stuck = 0
            print(f"  ({x},{y},{z}) d={d:.0f}", flush=True)
        else:
            stuck += 1
            if stuck == 6:
                camera()
            if stuck > 16:
                print("  STUCK", flush=True)
                break
        if d < 220:
            break
        for ddx, ddy in ((TX - x, TY - y), (0, 500), (-500, 0), (500, 0),
                         (0, -500), (-350, 350), (350, 350), (-350, -350),
                         (350, -350)):
            sx, sy = nav.screen_dir(ddx, ddy, 210)
            nav.resume()
            nav.walk(sx, sy, 1.2)
            q = nav.pos() or nav.pos()
            if q and math.hypot(TX - q[0], TY - q[1]) < d - 30:
                break
print("final:", nav.pos() or nav.pos())

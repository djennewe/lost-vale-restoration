#!/usr/bin/env python3
"""climbto.py x,y [secs] — hold SPACE and push toward a world point.

The cave ascent recipe (2026-09-01): SPACE must be HELD, not tapped, and
the mover climbs in the direction the Avatar is pushed. Movement here is
nav.walk's right-button-held-off-centre, so the push direction comes from
screen_dir like every other leg.
"""
import os, sys, time, subprocess
sys.path.insert(0, '~/projects/lost-vale/tools/playtest-linux')
from nav import pos, screen_dir, win, xdo, DISP, resume

tx, ty = (int(v) for v in sys.argv[1].split(','))
secs = float(sys.argv[2]) if len(sys.argv) > 2 else 1.6
p = pos() or pos()
print("start:", p)
x, y, z, mp = p
sx, sy = screen_dir(tx - x, ty - y, mag=200)
w = win(); xdo("windowfocus", w)
r = subprocess.run(["xdotool", "getwindowgeometry", "--shell", w],
                   env={**os.environ, "DISPLAY": DISP},
                   capture_output=True, text=True)
g = dict(l.split("=") for l in r.stdout.strip().splitlines())
cx = int(g["X"]) + int(g["WIDTH"]) // 2 + sx
cy = int(g["Y"]) + int(g["HEIGHT"]) // 2 + sy
open("/run/user/1000/lv-playtest/commands.txt","a").write("exit\n")
time.sleep(1.5)
xdo("mousemove", str(cx), str(cy)); time.sleep(0.3)
xdo("keydown", "space"); time.sleep(0.06)
xdo("mousedown", "3"); time.sleep(secs)
xdo("mouseup", "3"); xdo("keyup", "space")
time.sleep(1.2)
print("after:", pos() or pos())

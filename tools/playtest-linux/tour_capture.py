#!/usr/bin/env python3
"""tour_capture.py — photograph a list of world spots in ScummVM.

    LV_DISPLAY=:91 XDG_RUNTIME_DIR=/tmp/claude-1000/tour-m10 \\
    LV_SCUMMVM=$PWD/scummvm-lv-console/scummvm \\
        python3 tools/playtest-linux/tour_capture.py STOPS.json OUTDIR

STOPS.json is a list of {"id": "m10-03", "map": 10, "x": .., "y": ..,
"z": .., "name": "..."}: each spot must be one the Avatar can stand on
(an exact_reach position), or the teleport buries him. For each stop, in a
FRESH session (a second MainActor::teleport in one console session was found
not to land, vignette_capture.py): cheats on, teleport, detach the console
so the world runs, wait for it to settle, capture the private display and cut
the 640x400 game surface to OUTDIR/<id>.png. Writes OUTDIR/captures.json
with the stop, the Avatar's position read back after the wait, and whether
the surface was found. Stops with a PNG and a recorded position are skipped, so a run
can be resumed.

Each parallel run needs its own LV_DISPLAY and XDG_RUNTIME_DIR (session.sh
keeps its log and command file there).
"""
import json
import os
import re
import subprocess
import sys
import time

import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SESSION = os.path.join(REPO, 'tools', 'playtest-linux', 'session.sh')
SHOT = os.path.join(REPO, 'tools', 'playtest-linux', 'shot.sh')
LOG = os.path.join(os.environ.get('XDG_RUNTIME_DIR', '/tmp'), 'lv-playtest',
                   'lv_run.log')
W, H = 640, 400
# The first teleport of a session fires the Guardian cutscene (AVATAR 0x0401
# at 0x1908, traps.md): about ten seconds on map 0 at (15967,19711,0) with
# the GHOST 411 apparition, then back to the target. A 6 s wait captured
# that limbo in 324 of 370 re-tour stops (2026-11-01), and earlier frames
# with the "ghost follower" were taken at its start. Wait it out.
SETTLE = 22
ACTOR_INFO = re.compile(
    r'Item 1 \(class MainActor, shape 1\)(?: \(uc: [^\n)]*\))?,\s*\d+,\s*'
    r'\((-?\d+),\s*(-?\d+),\s*(-?\d+)\)[^\n]*?\bm:\s*(\d+)')


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True)


def log_lines():
    try:
        with open(LOG, errors='replace') as f:
            return f.readlines()
    except FileNotFoundError:
        return []


def cheats_on():
    sh(SESSION, 'debugger')
    for _ in range(4):
        sh(SESSION, 'dbg', 'Cheat::toggle')
        states = [ln for ln in log_lines() if 'Cheats =' in ln]
        if states and states[-1].strip().endswith('true'):
            return True
    return False


def actual_position():
    """Read a fresh reply while dbg keeps the console attached and paused."""
    before = len(log_lines())
    if sh(SESSION, 'debugger').returncode:
        return None
    reply = sh(SESSION, 'dbg', 'ObjectManager::objectInfo 1')
    # dbg can truncate its printed reply; the session log retains every line.
    fresh = ''.join(log_lines()[before:])
    matches = list(ACTOR_INFO.finditer(fresh or reply.stdout))
    if reply.returncode or not matches:
        return None
    x, y, z, mapnum = map(int, matches[-1].groups())
    return dict(map=mapnum, x=x, y=y, z=z)


def window_origin():
    """The ScummVM window's top-left on the private display (xwininfo). The
    surface must be cut there, not at the first lit pixel: a view whose top
    or left edge is black void would otherwise shift the crop and fake a
    black band on the opposite edge."""
    disp = os.environ.get('LV_DISPLAY', ':77')
    env = dict(os.environ, DISPLAY=disp)
    wid = subprocess.run(['xdotool', 'search', '--class', 'scummvm'],
                         capture_output=True, text=True, env=env).stdout.split()
    if not wid:
        return None
    info = subprocess.run(['xwininfo', '-id', wid[-1]], capture_output=True,
                          text=True, env=env).stdout
    x = y = None
    for ln in info.splitlines():
        if 'Absolute upper-left X' in ln:
            x = int(ln.split(':')[1])
        elif 'Absolute upper-left Y' in ln:
            y = int(ln.split(':')[1])
    return (x, y) if x is not None and y is not None else None


def surface(path):
    raw = np.array(Image.open(path).convert('RGB'))
    at = window_origin()
    if at is None:
        return None
    x0, y0 = at
    s = raw[y0:y0 + H, x0:x0 + W]
    return s if s.shape[:2] == (H, W) else None


def capture(stop, outdir):
    sh(SESSION, 'stop')
    if sh(SESSION, 'start').returncode != 0:
        return dict(stop, at=None, landed=False, ok=False, why='session did not start')
    if not cheats_on():
        return dict(stop, at=None, landed=False, ok=False, why='cheats did not toggle on')
    # cmdTeleport returns false and detaches itself. dbg would wait for a
    # prompt, reattach, and queue a second teleport. cheats_on left the
    # console attached, so send this detaching command once through cmd.
    sh(SESSION, 'cmd', f"MainActor::teleport {stop['map']} {stop['x']} "
                       f"{stop['y']} {stop['z']}")
    time.sleep(SETTLE)
    at = actual_position()
    landed = bool(at and at['map'] == stop['map'] and
                  abs(at['x'] - stop['x']) <= 64 and
                  abs(at['y'] - stop['y']) <= 64)
    result = dict(stop, at=at, landed=landed)
    # The text console leaves the game surface intact while paused, so the
    # position and image describe the same settled world state.
    raw = os.path.join(outdir, f"{stop['id']}_raw.png")
    sh(SHOT, raw)
    surf = surface(raw)
    if surf is None:
        return dict(result, ok=False, why='no 640x400 game surface')
    Image.fromarray(surf).save(os.path.join(outdir, f"{stop['id']}.png"))
    os.remove(raw)
    if at is None:
        return dict(result, ok=False, why='no fresh MainActor position reply')
    return dict(result, ok=True)


def main():
    stops = json.load(open(sys.argv[1]))
    outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    out_json = os.path.join(outdir, 'captures.json')
    done = json.load(open(out_json)) if os.path.exists(out_json) else []
    have = {d['id'] for d in done if d.get('ok') and d.get('at') is not None}
    try:
        for stop in stops:
            if stop['id'] in have and os.path.exists(
                    os.path.join(outdir, f"{stop['id']}.png")):
                continue
            r = capture(stop, outdir)
            done = [d for d in done if d['id'] != stop['id']] + [r]
            json.dump(done, open(out_json, 'w'), indent=1)
            print(stop['id'], 'ok' if r.get('ok') else r.get('why'),
                  'at', r.get('at'), 'landed', r.get('landed'))
    finally:
        sh(SESSION, 'stop')


if __name__ == '__main__':
    main()

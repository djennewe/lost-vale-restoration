#!/usr/bin/env python3
"""vignette_capture.py — photograph each 1994 shot's place in ScummVM and
score it against the published GIF.

    export LV_SCUMMVM=$PWD/scummvm-lv-console/scummvm
    python3 tools/playtest-linux/vignette_capture.py OUTDIR screen18 screen11 ...

For each shot, in a FRESH session (session.sh stop/start: a second
MainActor::teleport in one console session was found not to land, so every
shot gets its own): cheats on, teleport the Avatar to the vignette's
recorded Avatar spot (world = origin + local; the window's ground centre when
the shot has no Avatar), wait for the world to settle, capture the private
display, cut the 640x400 game surface, and find the 1994 frame inside it by
palette-class alignment. The `usehighres` canvas is 640x400 native, so the
whole 320-wide 1994 frame fits round an Avatar-centred camera and no camera
scripting is needed. Writes OUTDIR/screenNN_ingame.png (shot | in-engine |
misses in red, x3) and prints the class and RGB match per shot.

The Avatar keeps his start facing, so his own pixels can differ from the
shot's pose; monsters and NPCs on their schedules may walk into the frame.
Everything else is the map.
"""
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(REPO, 'agents', 'map-populator', 'src')
sys.path.insert(0, SRC)
import shot_decompose as SD  # noqa: E402
import vignette_place as V  # noqa: E402

SESSION = os.path.join(REPO, 'tools', 'playtest-linux', 'session.sh')
SHOT = os.path.join(REPO, 'tools', 'playtest-linux', 'shot.sh')
SURFACE_W, SURFACE_H = 640, 400


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True)


def classes(rgb):
    d = np.abs(rgb[:, :, None, :] - SD.PAL[None, None, :, :]).sum(-1)
    return SD.CLS[d.argmin(-1)]


LOG = os.path.join(os.environ.get('XDG_RUNTIME_DIR', '/tmp'), 'lv-playtest', 'lv_run.log')


def cheats_on():
    """Toggle until the console last reported `Cheats = true`."""
    for _ in range(4):
        sh(SESSION, 'dbg', 'Cheat::toggle')
        with open(LOG, errors='replace') as f:
            states = [ln for ln in f if 'Cheats =' in ln]
        if states and states[-1].strip().endswith('true'):
            return True
    return False


def avatar_spot(vig):
    ox, oy, oz = V.origin(vig)
    for a in vig.get('actors', []):
        if a.get('shape') == 1 and not a.get('unrendered'):
            return ox + a['x'], oy + a['y'], oz + a['z']
    cam = vig['camera']
    _, (h, w), _ = SD.load_shot(vig['shot'])
    sx = cam['sx0'] + (ox // 4 - oy // 4) + w // 2
    sy = cam['sy0'] + (ox // 8 + oy // 8 - oz) + h // 2
    return 2 * sx + 4 * sy, 4 * sy - 2 * sx, 0


def surface(path):
    raw = np.array(Image.open(path).convert('RGB')).astype(int)
    lit = np.argwhere(raw.sum(-1) > 0)
    if not len(lit):
        return None
    y0, x0 = lit.min(0)
    return raw[y0:y0 + SURFACE_H, x0:x0 + SURFACE_W]


def align(sc, tc):
    h, w = tc.shape
    ys, xs = np.mgrid[0:h:3, 0:w:3]
    samp = tc[ys, xs]
    best, at = -1, (0, 0)
    for dy in range(sc.shape[0] - h + 1):
        for dx in range(sc.shape[1] - w + 1):
            s = (sc[ys + dy, xs + dx] == samp).mean()
            if s > best:
                best, at = s, (dx, dy)
    return at


def capture(shot, outdir):
    vig = V.load(shot)
    mp = vig['placement']['map']
    x, y, z = avatar_spot(vig)
    sh(SESSION, 'stop')
    started = sh(SESSION, 'start')
    if started.returncode != 0:
        print(f'{shot}: session did not start: {started.stderr.strip()}')
        return None
    if not cheats_on():
        print(f'{shot}: could not turn cheats on')
        return None
    sh(SESSION, 'dbg', f'MainActor::teleport {mp} {x} {y} {z}')
    time.sleep(5)
    raw = os.path.join(outdir, f'{shot}_raw.png')
    sh(SHOT, raw)
    surf = surface(raw)
    _, (h, w), rgb = SD.load_shot(shot)
    if surf is None or surf.shape[:2] != (SURFACE_H, SURFACE_W):
        print(f'{shot}: no game surface in the capture ({raw})')
        return None
    sc, tc = classes(surf), classes(rgb)
    dx, dy = align(sc, tc)
    crop = surf[dy:dy + h, dx:dx + w]
    cls = (sc[dy:dy + h, dx:dx + w] == tc)
    rgb_ok = np.abs(crop - rgb).sum(-1) <= 12
    dif = rgb.astype(np.uint8).copy()
    dif[~cls] = (dif[~cls] * 0.3 + np.array([255, 0, 0]) * 0.7).astype(np.uint8)
    Image.fromarray(np.concatenate([rgb.astype(np.uint8), crop.astype(np.uint8), dif], 1)) \
        .resize((w * 9, h * 3), Image.NEAREST) \
        .save(os.path.join(outdir, f'{shot}_ingame.png'))
    print(f'{shot}: map {mp} avatar ({x},{y},{z}) frame at (+{dx},+{dy}) '
          f'class {cls.mean() * 100:.2f}% rgb {rgb_ok.mean() * 100:.2f}%')
    return cls.mean()


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    for shot in sys.argv[2:]:
        capture(shot, outdir)
    sh(SESSION, 'stop')


if __name__ == '__main__':
    main()

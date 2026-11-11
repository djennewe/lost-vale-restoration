#!/usr/bin/env python3
"""Find an NPC sprite on screen and click it, in one shot.

LV village NPCs walk. Reading a position from one screenshot and clicking it
in a later call reliably lands on empty ground, which looks exactly like an
unresponsive NPC. This captures, locates and clicks inside a single
invocation so the target has no time to move.

    talk_to.py                       # nearest villager to screen centre
    talk_to.py --hint 700 380        # nearest villager to a view point
    talk_to.py --action left         # look instead of talk
    talk_to.py --dry                 # report candidates, click nothing

View coordinates are the 1450x873 space that shot.sh produces, which equals
window-frame points.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
POSTMOUSE = os.path.join(HERE, "postmouse")


def window():
    """(window_id, origin_x, origin_y) for the ScummVM window.

    Uses the winid helper rather than `orca computer list-windows`: orca
    reports "No windows found" when ScummVM is started from session.sh's
    pipeline subshell, even though the window is present.
    """
    sys.path.insert(0, HERE)
    from send import find_pid
    out = subprocess.run([os.path.join(HERE, "winid"), find_pid()],
                         capture_output=True, text=True)
    parts = out.stdout.split()
    if len(parts) < 3:
        raise SystemExit(f"no scummvm window found: {out.stderr.strip()}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def grab(win):
    from PIL import Image
    tmp = tempfile.mktemp(suffix=".png")
    subprocess.run(["screencapture", "-l", str(win), "-x", tmp], check=True)
    im = Image.open(tmp).convert("RGB")
    w, h = im.size
    # -l pads 68px of drop shadow on each side at 2x.
    im = im.crop((68, 68, w - 68, h - 68)).resize(((w - 136) // 2, (h - 136) // 2))
    os.unlink(tmp)
    return im


def is_robe(p):
    """The shape-707/708 villager robe: dark brown, R about 2x G, G about 2x B."""
    r, g, b = p
    return (52 <= r <= 125 and 26 <= g <= 80 and 6 <= b <= 52
            and r > g * 1.30 and g > b * 1.25)


def blobs(im, minpx=60, maxpx=3000):
    w, h = im.size
    px = im.load()
    seen = set()
    out = []
    # Step 2 for speed; sprites are ~18x45 at this scale so nothing is missed.
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if (x, y) in seen or not is_robe(px[x, y]):
                continue
            q = deque([(x, y)])
            seen.add((x, y))
            pts = []
            while q:
                cx, cy = q.popleft()
                pts.append((cx, cy))
                for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                    nx, ny = cx + dx, cy + dy
                    if (0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen
                            and is_robe(px[nx, ny])):
                        seen.add((nx, ny))
                        q.append((nx, ny))
            if minpx <= len(pts) * 4 <= maxpx:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                out.append({
                    "n": len(pts) * 4,
                    "cx": sum(xs) // len(xs),
                    "cy": sum(ys) // len(ys),
                    "w": max(xs) - min(xs), "h": max(ys) - min(ys),
                })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hint", nargs=2, type=int, default=None)
    ap.add_argument("--action", default="double")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    win, ox, oy = window()
    im = grab(win)
    hx, hy = a.hint if a.hint else (im.size[0] // 2, im.size[1] // 2)

    cands = blobs(im)
    # The Avatar wears the same palette in places, so drop anything sitting on
    # top of him: he is always dead centre of the view.
    acx, acy = im.size[0] // 2, im.size[1] // 2
    cands = [c for c in cands if abs(c["cx"] - acx) > 25 or abs(c["cy"] - acy) > 40]
    if not cands:
        print("no villager sprite found")
        return 1
    cands.sort(key=lambda c: (c["cx"] - hx) ** 2 + (c["cy"] - hy) ** 2)
    for c in cands[:5]:
        print(f"  cand view=({c['cx']},{c['cy']}) px={c['n']} {c['w']}x{c['h']}")
    best = cands[0]
    sx, sy = ox + best["cx"], oy + best["cy"]
    print(f"target view=({best['cx']},{best['cy']}) screen=({sx},{sy})")
    if a.dry:
        return 0
    sys.path.insert(0, HERE)
    from send import find_pid          # shares the one-instance check
    subprocess.run([POSTMOUSE, find_pid(), str(sx), str(sy), a.action], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

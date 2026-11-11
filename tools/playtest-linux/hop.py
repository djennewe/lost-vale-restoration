#!/usr/bin/env python3
"""hop.py — auto-aimed targeted jumps (built crossing the map 8 pool).

CURRENT INTERFACE (2026-08-16, post-crossing): use `calibrated_pixel` +
a SPACE tap — see docs/playtest-2026-08-16-pool-crossing.md for the full
physics. Summary: a SPACE tap with no direction flag runs the engine's
targeted jump to the plane point reconstructed from the CLICK PIXEL
(plane_point()); deliveries fall short at range, so aim `extra` (~110)
BEYOND the target along the flight line; the engine refuses aims past
str*32 per axis. The find_pixel/spiral/hop/main below predate that
understanding — they still work for short hops but calibrated_pixel is
what crossed every stone past C.

Why aiming is solvable at all (found 2026-08-16 in the engine source):
`targetedjump` is ON by default (u8_game.cpp:54), and a standing both-button
chord runs TargetedAnimProcess, which lands the Avatar AT the world coords
traced under the cursor (u8_avatar_mover_process.cpp:733) — provided the
traced item is_land() and within getStr()*32 units on each axis. The
2026-08-12 deaths were fixed-distance jumps: chording while the last anim
was run/runningJump bypasses targeting entirely, and a too-close cursor
degrades to jumpUp. So the protocol is:

  1. stand still long enough that the last anim is not a run
  2. spiral-probe single LEFT clicks around the predicted pixel until the
     Object debug log resolves the TARGET stone (shape+world coords match)
  3. chord both buttons at that exact pixel, >= 1.2 s after the last probe
     so the pair cannot register as a double-click (= use)
  4. verify the landing with objectInfo; on death, reload slot 1 (queue the
     loadGame BEFORE chording the debugger — the death diary blocks attach)

Projection (item_sorter.cpp:92, camera tracks the Avatar):
    screen_x = (x - y) / 4        screen_y = (x + y) / 8 - z
in NATIVE 320x240 pixels — ScummVM renders the game surface at 2x into the
640x480 window, so double both offsets (verified against probed stones,
2026-08-16). Frame-0 stones are the sunken-but-present variant: drawn low,
still clickable and landable.

Usage:  hop.py 29983,21311 30207,21535 ...     hop each stone in order
        hop.py --probe X,Y                     probe-identify only, no jump
Needs `debugflag_enable Object` (sent automatically) and a resumed game.
"""
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav import (  # noqa: E402
    LOG, CMDS, xdo, win, chord as dbg_chord, pos, resume, walk, screen_dir,
)

ITEMRE = re.compile(
    rb"Item (\d+) \(class (\w+), shape (\d+)\)"
    rb"(?: \(uc: (\w+)\))?, (\d+), \((\d+), (\d+), (\d+)\)")
STONE_SHAPE = 780
# Landing tolerance vs the stone's FIXED.DAT origin: the top surface is a
# footpad wide, and TraceCoordinates lands us wherever on it we clicked.
LAND_TOL = 100   # stones are 96x96; a centred landing is ~68 from the item
                 # origin, and the west-bank park spot (146 from stone A)
                 # must NOT count as "arrived"
SCALE = 2        # 320x240 native -> 640x480 game surface
STONE_HALF = 48  # footpad 3x3 (=96x96 world), height 8
STONE_TOP_Z = 8
CAMERA_Z_OFF = 20  # camera tracks the avatar at item z + 20 (camera_process.cpp)


def log_size():
    try:
        return os.path.getsize(LOG)
    except OSError:
        return 0


def read_from(offset):
    with open(LOG, "rb") as f:
        f.seek(offset)
        return f.read()


def game_center():
    w = win()
    if not w:
        raise RuntimeError("no scummvm window")
    import subprocess
    r = subprocess.run(["xdotool", "getwindowgeometry", "--shell", w],
                       env={**os.environ, "DISPLAY": ":77"},
                       capture_output=True, text=True)
    g = dict(l.split("=") for l in r.stdout.strip().splitlines())
    return (int(g["X"]) + int(g["WIDTH"]) // 2,
            int(g["Y"]) + int(g["HEIGHT"]) // 2)


def predict(av, tgt):
    """Pixel offset of tgt from the screen centre, Avatar (camera) at av."""
    ax, ay, az = av[0], av[1], av[2]
    tx, ty = tgt[0], tgt[1]
    tz = tgt[2] if len(tgt) > 2 else 8  # aim at the stone's top, not its base
    dpx = ((tx - ty) - (ax - ay)) // 4
    dpy = ((tx + ty) // 8 - tz) - ((ax + ay) // 8 - az)
    return SCALE * dpx, SCALE * dpy


def probe(px, py):
    """Single left click at absolute pixel; return items the Object
    debugflag logged for it."""
    before = log_size()
    xdo("mousemove", str(px), str(py))
    time.sleep(0.15)
    xdo("click", "1")
    time.sleep(0.55)
    out = []
    for m in ITEMRE.finditer(read_from(before)):
        out.append({
            "id": int(m.group(1)), "cls": m.group(2).decode(),
            "shape": int(m.group(3)),
            "uc": (m.group(4) or b"").decode(), "frame": int(m.group(5)),
            "x": int(m.group(6)), "y": int(m.group(7)), "z": int(m.group(8)),
        })
    return out


def plane_point(px, py, av):
    """World point the engine's TraceCoordinates reconstructs for a click
    at absolute pixel (px,py) on a z=8-top item, camera on the Avatar at
    av=(x,y,z). THIS, not the clicked artwork, is where a targeted jump
    goes (game_map_gump.cpp Z_FACE equations)."""
    mx = (px - 405) / 2.0 - 160
    my = (py - 196) / 2.0 - 120
    X = 2*mx + 4*(my + STONE_TOP_Z) + av[0] - 4*(av[2] + CAMERA_Z_OFF)
    Y = -2*mx + 4*(my + STONE_TOP_Z) + av[1] - 4*(av[2] + CAMERA_Z_OFF)
    return X, Y


def calibrated_pixel(target, av, is_target, extra=110):
    """THE aimer that crossed the pool (2026-08-16). Deliveries fall
    short of the plane point at range (deficit ~30-170 beyond ~200
    units), so scan the target's whole artwork and pick the pixel whose
    plane point lies |target| + `extra` ALONG the flight line, with
    perpendicular error penalized (an off-axis plane point lands in the
    water beside the stone). Aims past the engine's range cap
    (str*32 per axis from the avatar CENTRE; str 15 -> 480) are refused
    with a shakeHead, so reject them here. Returns (px, py, along, perp)
    or None."""
    bx, by = aim_pixel(av, target)
    fx, fy = target[0] - av[0], target[1] - av[1]
    fl = (fx*fx + fy*fy) ** 0.5 or 1
    want = fl + extra
    best = None
    bestscore = 1e9
    for oy in range(-46, 61, 8):
        for ox in range(-36, 37, 9):
            px, py = bx + ox, by + oy
            if not (410 <= px <= 1040 and 200 <= py <= 670):
                continue
            if not any(is_target(it) for it in probe(px, py)):
                continue
            X, Y = plane_point(px, py, av)
            if abs(X - (av[0]-32)) > 468 or abs(Y - (av[1]-32)) > 468:
                continue  # engine range cap -> would shakeHead
            along = ((X-av[0])*fx + (Y-av[1])*fy) / fl
            perp = abs((X-av[0])*(-fy) + (Y-av[1])*fx) / fl
            score = abs(along - want) + 1.6*perp
            if score < bestscore:
                bestscore = score
                best = (px, py, along, perp)
    return best


def spiral(step=8, rmax=64):
    yield (0, 0)
    r = step
    while r <= rmax:
        n = max(8, (2 * r) // step * 4)
        for i in range(n):
            import math
            a = 2 * math.pi * i / n
            yield (int(r * math.cos(a)), int(r * math.sin(a)))
        r += step


def aim_pixel(av, stone):
    """Project the stone's TOP-FACE CENTRE. The engine's targeted jump
    lands at the geometric plane point reconstructed from the click pixel
    (game_map_gump.cpp TraceCoordinates, Z_FACE case) — NOT at the
    clicked artwork. The stone sprite is drawn taller than its geometric
    8-unit top face, so a click high on the artwork extrapolates the
    plane BEHIND the stone (that was the deterministic north-landing
    bug). Aim only at the face-centre projection."""
    ax, ay, az = av
    lx, ly, lz = stone[0] - STONE_HALF, stone[1] - STONE_HALF, STONE_TOP_Z
    mx = ((lx - ly) - (ax - ay)) / 4.0
    my = ((lx + ly) / 8.0 - lz) - ((ax + ay) / 8.0 - (az + CAMERA_Z_OFF))
    cx, cy = game_center()
    return int(round(cx + SCALE * mx)), int(round(cy + SCALE * my))


def _is_target(it, target):
    return (it["shape"] == STONE_SHAPE
            and abs(it["x"] - target[0]) <= 48
            and abs(it["y"] - target[1]) <= 48)


def find_pixel(target, av):
    """DEEP-AIM (the technique that finally landed A->C, 2026-08-16).

    The targeted jump lands SHORT of the traced plane point at range
    (~85 units short at 260+), so aiming at the stone's top-face centre
    drowns the Avatar. But TraceCoordinates only needs the clicked PIXEL
    to be on the stone's artwork — the reconstructed plane point may lie
    far BEYOND the stone. So: find any artwork pixel, then walk the aim
    along the projected flight direction to the FARTHEST pixel that
    still traces the stone. The overshoot absorbs the shortfall and the
    landing settles onto the stone (A->C landed at the stone's exact
    origin)."""
    ax, ay = av[0], av[1]
    bx, by = aim_pixel(av, target)
    # screen-space unit step along the flight direction
    fdx, fdy = target[0] - ax, target[1] - ay
    sdx, sdy = (fdx - fdy) / 4.0, (fdx + fdy) / 8.0
    n = max(abs(sdx), abs(sdy)) or 1
    step = (SCALE * 3 * sdx / n, SCALE * 3 * sdy / n)  # ~6px steps
    hit = None
    for k in range(0, 12):
        px = int(round(bx + step[0] * k))
        py = int(round(by + step[1] * k))
        items = probe(px, py)
        ok = any(_is_target(it, target) for it in items)
        tag = "C" if ok else ",".join(str(i["shape"]) for i in items) or "-"
        print(f"    aim+{k}: ({px},{py}) -> {tag}", flush=True)
        if ok:
            hit = (px, py)
        elif hit is not None and k > 4:
            break  # walked off the far edge of the artwork
    return hit


def chord_jump(px, py):
    """Targeted jump: cursor on the stone pixel, SPACE. SPACE is the
    ACTION_JUMP keybinding ("fake both-button-click", metaengine.cpp:71)
    and sets MOVE_JUMP with NO mouse buttons involved — an actual mouse
    chord raises MOVE_MOUSE_DIRECTION a tick later, which routes to the
    fixed-distance jump branch (u8_avatar_mover_process.cpp:468) and was
    the cause of the 2026-08-12 deaths. Only the direction-less branch
    (:510) calls the targeted jump toward the traced cursor position.
    One tap per call: the tap is consumed by a turn-to-face when the
    facing is off (checkTurn eats the flag), and the caller's retry loop
    re-probes with a fresh camera before the next tap — never fire twice
    blind, the camera moves after a successful hop."""
    w = win()
    if w:
        xdo("windowfocus", w)
    xdo("mousemove", str(px), str(py))
    time.sleep(0.9)   # settle to stand; clears the double-click window
    xdo("keydown", "space")
    time.sleep(0.15)
    xdo("keyup", "space")
    time.sleep(2.6)   # turn or air time


def reload_slot1():
    """Death recovery per the 2026-08-12 protocol: queue the loadGame FIRST,
    then chord until the console drains it."""
    print("  RELOADING slot 1 (west bank)", flush=True)
    before = log_size()
    with open(CMDS, "a") as f:
        f.write("Ultima8Engine::loadGame 1\n")
    for _ in range(8):
        dbg_chord()
        time.sleep(1.5)
        if b"load" in read_from(before).lower():
            break
    resume()
    time.sleep(2.0)


def hop(target, max_tries=6):
    """One stone. Returns 'ok' | 'dead' | 'fail'."""
    tx, ty = target[0], target[1]
    for attempt in range(1, max_tries + 1):
        p = pos()
        if not p:
            print("  no position — assuming death diary", flush=True)
            return "dead"
        hp = getattr(pos, "last_hp", None)
        if hp is not None and hp <= 0:
            return "dead"
        x, y, z, mp = p
        d = ((x - tx) ** 2 + (y - ty) ** 2) ** 0.5
        print(f"  attempt {attempt}: at ({x},{y},{z}) hp={hp} "
              f"dist={int(d)}", flush=True)
        if d <= LAND_TOL:
            return "ok"
        resume()
        pix = find_pixel(target, (x, y, z))
        if not pix:
            # NEVER walk toward the target here — the target is a stone
            # in DEADLY water and the fallback walk drowned the Avatar
            # (2026-08-16). Re-probe after a beat; the camera may settle.
            print("    stone not resolved — re-probing", flush=True)
            time.sleep(1.0)
            continue
        print(f"    chord at {pix}", flush=True)
        chord_jump(*pix)
        p2 = pos()
        if not p2:
            return "dead"
        hp2 = getattr(pos, "last_hp", None)
        if hp2 is not None and hp2 <= 0:
            return "dead"
        x2, y2, z2, _ = p2
        d2 = ((x2 - tx) ** 2 + (y2 - ty) ** 2) ** 0.5
        print(f"    landed ({x2},{y2},{z2}) hp={hp2} dist={int(d2)}",
              flush=True)
        if d2 <= LAND_TOL:
            return "ok"
        if abs(x2 - x) + abs(y2 - y) < 24:
            # No real movement: usually the tap was consumed by the
            # turn-to-face (checkTurn eats MOVE_JUMP); tap again. If it
            # keeps refusing (shakeHead: trace missed the face), edge a
            # step toward the water so the artwork overlaps the aim.
            continue  # never blind-walk near deadly water
    return "fail"


def main():
    argv = sys.argv[1:]
    with open(CMDS, "a") as f:
        f.write("debugflag_enable Object\n")
    if argv and argv[0] == "--probe":
        t = tuple(int(v) for v in argv[1].split(","))
        p = pos()
        resume()
        print("pixel:", find_pixel(t, p[:3]))
        return
    targets = [tuple(int(v) for v in a.split(",")) for a in argv]
    for round_ in range(1, 6):
        print(f"=== crossing attempt {round_} ===", flush=True)
        ok = True
        for i, t in enumerate(targets):
            print(f"stone {i + 1}/{len(targets)} -> {t}", flush=True)
            r = hop(t)
            if r == "dead":
                reload_slot1()
                ok = False
                break
            if r == "fail":
                print("STUCK — stopping for a human look", flush=True)
                sys.exit(2)
        if ok:
            print("CHAIN COMPLETE", flush=True)
            print("final:", pos(), flush=True)
            sys.exit(0)
    print("five crossing attempts failed", flush=True)
    sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""nav.py — drive the Avatar to world waypoints on the current map.

Isometric mapping used throughout:
    screen_x  =  (wx - wy)
    screen_y  =  (wx + wy) / 2
so a desired world delta (dx,dy) becomes a screen offset the walk verb
can hold the right mouse button at.

Usage:  nav.py x1,y1  x2,y2 ...       walk through the waypoints
        nav.py --pos                  just report position
"""
import os, re, subprocess, sys, time

DISP = ":77"
RUN = "/run/user/1000/lv-playtest"
LOG = f"{RUN}/lv_run.log"
CMDS = f"{RUN}/commands.txt"
REPO = "~/projects/lost-vale"
POSRE = re.compile(r"Item 1 \(class \w+, shape \d+\), \d+, \((\d+), (\d+), (\d+)\).*?m: (\d+)")


def xdo(*args):
    subprocess.run(["xdotool", *args], env={**os.environ, "DISPLAY": DISP},
                   capture_output=True)


def win():
    r = subprocess.run(["xdotool", "search", "--class", "scummvm"],
                       env={**os.environ, "DISPLAY": DISP}, capture_output=True, text=True)
    ids = r.stdout.split()
    return ids[-1] if ids else None


def chord():
    """Attach chord, verified: wait for a new 'Debugger entered' line.
    Returns True when the attach was observed. A blocked attach (death
    diary up) returns False rather than lying (2026-08-16)."""
    try:
        before = open(LOG, "rb").read().count(b"Debugger entered")
    except OSError:
        before = 0
    for _ in range(3):
        w = win()
        if w:
            xdo("windowfocus", w)
        xdo("keydown", "ctrl", "keydown", "alt", "key", "d",
            "keyup", "alt", "keyup", "ctrl")
        for _ in range(8):
            time.sleep(0.5)
            try:
                now = open(LOG, "rb").read().count(b"Debugger entered")
            except OSError:
                now = before
            if now > before:
                return True
    return False


def _tail(f, size=262144):
    # The session log grows without bound; reading it whole made every
    # probe O(file) and eventually flaky (2026-08-12). Tail is enough.
    f.seek(0, 2)
    end = f.tell()
    f.seek(max(0, end - size))
    return f.read()


def nlines():
    with open(LOG, "rb") as f:
        return _tail(f).count(b"\n")


def prompts():
    with open(LOG, "rb") as f:
        return _tail(f).count(b"\ndebug>")


def ask(cmd, tries=3):
    """Send one debugger command, return its reply text.

    Rewritten 2026-09-18 alongside `pos()`: the old body wrote to
    `commands.txt` and waited for a new "debug> " prompt, and the command
    file stopped draining after the 2026-09-03 rebuild, so this returned ""
    forever — which is what `chase2.py`'s header notes. `console()` is
    defined below; both now share the dbg.sh keystroke transport.
    """
    for _ in range(tries):
        out = console(cmd)
        if out.strip():
            return out
    return ""


DBG_SH = os.path.join(REPO, "tools", "playtest-linux", "dbg.sh")


def console(cmd, settle=0.4):
    """Send ONE debugger command and return the log text written after it.

    TRANSPORT REWRITTEN 2026-09-18. Every function here used to append to
    `commands.txt`, which ScummVM drained from stdin — and stopped draining
    after the 2026-09-03 rebuild (dbg.sh's header; the playtest traps file).
    The symptom is total: `pos()` returned None forever, so `goto()` printed
    "(no position)" and every route in every script aborted on its first
    step. The console takes KEYSTROKES now, which is what dbg.sh sends, so
    this routes through it. dbg.sh also exits the console when it is done,
    so the game is running again on return — which is why `resume()` below
    has nothing left to do.

    KEEP THE SUBPROCESS. An inline version that chorded and typed with
    `xdotool --window` directly, to skip dbg.sh's ~5 s of fixed sleeps, was
    tried on 2026-09-18 and is a trap: the chord TOGGLES, so against an
    already-open console it closes it, and the command and the `exit` that
    follows are then typed INTO THE GAME. The first symptom is that every
    walk silently does nothing while position reads keep answering (the
    console is attached, and attached means paused); the second is worse —
    the stray keys reached the world and left the Avatar on map 0. A probe
    costs ~6 s. Spend it.
    """
    off = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    subprocess.run([DBG_SH, cmd], capture_output=True)
    time.sleep(settle)
    with open(LOG, "rb") as f:
        f.seek(off)
        return f.read().decode("latin1")


def pos(tries=3):
    """(x, y, z, map) or None, with hp on `pos.last_hp`."""
    for _ in range(tries):
        out = console("ObjectManager::objectInfo 1")
        m = None
        for m in POSRE.finditer(out):
            pass
        if m:
            hp = None
            for h in re.finditer(r"Actor hp: (\d+)", out):
                hp = int(h.group(1))
            pos.last_hp = hp
            return (int(m.group(1)), int(m.group(2)),
                    int(m.group(3)), int(m.group(4)))
    return None


def resume():
    """No-op since the 2026-09-18 transport rewrite, kept so the scripts
    that sandwich their walks in it keep working. `console()` goes through
    dbg.sh, which types `exit` after every command, so the console is
    already closed and the world already running when a command returns.
    The old body wrote `exit` into the command file, which no longer
    drains; on the old stdin transport an unguarded exit could also pile
    up (53 of them in one evening, 2026-08-17)."""
    return


def walk(sx, sy, secs):
    w = win()
    if not w:
        return
    xdo("windowfocus", w)
    r = subprocess.run(["xdotool", "getwindowgeometry", "--shell", w],
                       env={**os.environ, "DISPLAY": DISP}, capture_output=True, text=True)
    g = dict(l.split("=") for l in r.stdout.strip().splitlines())
    cx = int(g["X"]) + int(g["WIDTH"]) // 2 + sx
    cy = int(g["Y"]) + int(g["HEIGHT"]) // 2 + sy
    xdo("mousemove", str(cx), str(cy))
    time.sleep(0.25)
    xdo("mousedown", "3")
    time.sleep(secs)
    xdo("mouseup", "3")


def screen_dir(dx, dy, mag=240):  # 240px offset = RUN gait; 130 walked, and walkers die to chasers (2026-08-12)
    sx, sy = (dx - dy), (dx + dy) / 2.0
    n = max(abs(sx), abs(sy) * 1.0) or 1
    return int(round(sx / n * mag)), int(round(sy / n * mag))


def goto(tx, ty, tol=200, budget=14, expect_map=None):  # tol 110->200, speed 340->600: run gait (2026-08-12)
    last = None
    stuck = 0
    for i in range(budget):
        p = pos() or pos()   # one retry: a single missed debugger reply
                             # aborted whole routes (2026-08-12)
        if not p:
            print("  (no position)", flush=True); return False
        x, y, z, mp = p
        if expect_map is None:
            expect_map = mp
        elif mp != expect_map:
            # A teleporter fired. Waypoints are map-local coordinates, so
            # continuing would drag the Avatar blindly across the new map —
            # which killed him on 2026-08-12 (map 40 -> 7 landing, dragged
            # 2100 units north into something lethal, hp 30 -> 0).
            print(f"  MAP CHANGED {expect_map} -> {mp} at ({x},{y},{z}); "
                  f"stopping route", flush=True)
            return "map_changed"
        d = ((x - tx) ** 2 + (y - ty) ** 2) ** 0.5
        print(f"  at ({x},{y},{z}) map {mp}  dist={int(d)}  hp={getattr(pos, 'last_hp', None)}", flush=True)
        if d <= tol:
            return True
        if last and abs(x - last[0]) + abs(y - last[1]) < 40:
            stuck += 1
        else:
            stuck = 0
        last = (x, y)
        sx, sy = screen_dir(tx - x, ty - y)
        if stuck == 1:      # try sliding along the wall
            sx, sy = -sy, sx
        elif stuck >= 2:    # back off
            sx, sy = -sx, -sy
        secs = min(5.0, max(0.5, d / 600.0))
        resume()
        walk(sx, sy, secs)
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--pos":
        print(pos()); sys.exit(0)
    p0 = pos()
    route_map = p0[3] if p0 else None
    for arg in sys.argv[1:]:
        tx, ty = (int(v) for v in arg.split(","))
        print(f"-> waypoint ({tx},{ty})", flush=True)
        r = goto(tx, ty, expect_map=route_map)
        if r == "map_changed":
            break
        if not r:
            print(f"   FAILED to reach ({tx},{ty})", flush=True)
            break
    print("final:", pos(), flush=True)

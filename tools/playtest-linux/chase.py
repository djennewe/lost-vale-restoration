#!/usr/bin/env python3
"""chase.py <npcnum> — close on a wandering NPC and strike in one motion."""
import math, os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nav
DISP=":77"
def xdo(*a): subprocess.run(["xdotool",*a], env={**os.environ,"DISPLAY":DISP}, capture_output=True)
def info(n):
    out = nav.ask(f"ObjectManager::objectInfo {n}")
    m = re.search(r"Item %d .*?\((-?\d+), (-?\d+), (-?\d+)\)" % n, out, re.S)
    return tuple(int(g) for g in m.groups()) if m else None
def pixel(me, him):
    dsx=((him[0]-him[1])-(me[0]-me[1]))/4.0
    dsy=((him[0]+him[1])/8.0-him[2])-((me[0]+me[1])/8.0-me[2])
    w=nav.win()
    r=subprocess.run(["xdotool","getwindowgeometry","--shell",w],
                     env={**os.environ,"DISPLAY":DISP},capture_output=True,text=True)
    g=dict(l.split("=") for l in r.stdout.strip().splitlines())
    return (int(int(g["X"])+int(g["WIDTH"])//2+dsx*2),
            int(int(g["Y"])+int(g["HEIGHT"])//2+dsy*2-60))
n=int(sys.argv[1])
for rnd in range(14):
    him=info(n); me=nav.pos()
    if not (him and me): continue
    d=math.hypot(him[0]-me[0], him[1]-me[1])
    print(f"round {rnd}: npc {him} me {me[:3]} dist={d:.0f}", flush=True)
    if d > 260:
        sx,sy = nav.screen_dir(him[0]-me[0], him[1]-me[1], 130)
        nav.resume(); nav.walk(sx, sy, min(1.2, max(0.35, (d-180)/260.0)))
        continue
    him=info(n) or him; me=nav.pos() or me     # re-read, then aim at once
    px,py = pixel(me[:3], him)
    before=open(nav.LOG,'rb').read().count(b"calling usecode event 1 @")
    nav.resume(); xdo("windowfocus", nav.win())
    xdo("mousemove",str(px),str(py)); time.sleep(0.35)
    for _ in range(3):
        xdo("click","--repeat","2","--delay","80","1"); time.sleep(0.12)
    time.sleep(1.4)
    after=open(nav.LOG,'rb').read().count(b"calling usecode event 1 @")
    print(f"  struck at ({px},{py}) events {before}->{after}", flush=True)
    if after>before:
        print("  TALKING", flush=True); sys.exit(0)
print("no strike landed", flush=True); sys.exit(1)

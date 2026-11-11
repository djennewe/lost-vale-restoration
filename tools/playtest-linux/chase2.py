#!/usr/bin/env python3
"""chase2.py <npcnum> — chase.py's logic, but every debugger read goes
through lv.sh (one command per attach). nav.ask started returning empty on
back-to-back queries mid-session; lv.sh does not."""
import math, os, re, subprocess, sys, time
sys.path.insert(0, '~/projects/lost-vale/tools/playtest-linux')
import nav
DISP=":77"
LV='~/projects/lost-vale/tools/playtest-linux/lv.sh'
def xdo(*a): subprocess.run(["xdotool",*a], env={**os.environ,"DISPLAY":DISP}, capture_output=True)
def info(n):
    out = subprocess.run(['bash',LV,'q',f'ObjectManager::objectInfo {n}'],
                         capture_output=True, text=True).stdout
    m = re.search(r"Item %d .*?\((-?\d+), (-?\d+), (-?\d+)\)" % n, out, re.S)
    return tuple(int(g) for g in m.groups()) if m else None
def geom():
    w=nav.win()
    r=subprocess.run(["xdotool","getwindowgeometry","--shell",w],
                     env={**os.environ,"DISPLAY":DISP},capture_output=True,text=True)
    return dict(l.split("=") for l in r.stdout.strip().splitlines())
def pixel(me, him):
    dsx=((him[0]-him[1])-(me[0]-me[1]))/4.0
    dsy=((him[0]+him[1])/8.0-him[2])-((me[0]+me[1])/8.0-me[2])
    g=geom()
    return (int(int(g["X"])+int(g["WIDTH"])//2+dsx*2),
            int(int(g["Y"])+int(g["HEIGHT"])//2+dsy*2-60))
n=int(sys.argv[1])
for rnd in range(16):
    him=info(n); me=info(1)
    if not (him and me):
        print(f"round {rnd}: read failed", flush=True); continue
    d=math.hypot(him[0]-me[0], him[1]-me[1])
    print(f"round {rnd}: npc {him} me {me} dist={d:.0f}", flush=True)
    if d > 240:
        sx,sy = nav.screen_dir(him[0]-me[0], him[1]-me[1], 130)
        nav.resume(); nav.walk(sx, sy, min(1.2, max(0.4, (d-160)/260.0)))
        continue
    # The pixel formula assumes the camera is centred on the Avatar. After
    # the Sacred Circle ceremony it is not, and every strike lands on empty
    # ground. Re-centre it, THEN re-read both positions and aim.
    subprocess.run(['bash', LV, 'q', 'CameraProcess::moveToAvatar'],
                   capture_output=True, text=True)
    subprocess.run(['bash', LV, 'detach'], capture_output=True, text=True)
    time.sleep(0.8)
    him=info(n) or him; me=info(1) or me
    px,py = pixel(me, him)
    before=open(nav.LOG,'rb').read().count(b"calling usecode event 1 @")
    nav.resume(); xdo("windowfocus", nav.win())
    xdo("mousemove",str(px),str(py)); time.sleep(0.35)
    xdo("click","--repeat","2","--delay","80","1")
    time.sleep(2.0)
    after=open(nav.LOG,'rb').read().count(b"calling usecode event 1 @")
    print(f"  struck at ({px},{py}) events {before}->{after}", flush=True)
    if after>before:
        print("  TALKING", flush=True); sys.exit(0)
print("no strike landed", flush=True); sys.exit(1)

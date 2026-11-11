#!/usr/bin/env python3
"""
test_god_animation.py — the invariants shape 860's animation rests on.

Four separate files have to agree about frame numbers for the gods to move:
the shape builder that lays the frames out, the usecode class that steps
them, the ceremony that kicks a run, and the TYPEFLAG entry that makes the
engine deliver the event at all. Nothing else checks that they do, and every
disagreement is silent — a wrong run start plays another god's shatter, a
wrong animType plays nothing, and a class id that is not the shape id plays
nothing while looking completely correct in the source.

These read the SOURCE of each, not a rebuild, so a hand edit to any one of
them fails here rather than in the sanctum.
"""

import json
import os
import re
import sys

THIS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(THIS, '..', '..', '..'))
sys.path.insert(0, THIS)

import lv_god_frames as F                                          # noqa: E402
import lv_god_statues as G                                         # noqa: E402
from patch_typeflag import ENTRY_SIZE, set_anim                    # noqa: E402

UC = os.path.join(ROOT, 'agents', 'usecode-compiler', 'src', 'lv-new')
MANIFEST = os.path.join(ROOT, 'shared', 'build', 'lv_manifest.json')
TYPEFLAG = os.path.join(ROOT, 'shared', 'build', 'TYPEFLAG.DAT')

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def src(name):
    with open(os.path.join(UC, name)) as f:
        return f.read()


print('=' * 68)
print('Shape 860 animation — frame layout and dispatch')
print('=' * 68)

# ── Layout ───────────────────────────────────────────────────────────────
print('\nL: the frame table')
check('42 frames: 6 static plus three 12-frame runs',
      len(G.FRAMES) == G.RUN_BASE + 3 * G.RUN_LEN == 42, f'{len(G.FRAMES)}')
check('every frame has a name', len(G.NAMES) == len(G.FRAMES))
_reg = json.load(open(G.REGISTRY))['shapes']
_stat = [_reg[str(s)]['frames'][0] for s in G.STATUES]
check('frames 0-2 are the 1994 statues (registry 2010-2012) build_map_18 '
      'places, at the registry hotspots',
      [G.FRAMES[i] for i in range(3)] ==
      [(f['png'], tuple(f['hotspot'])) for f in _stat],
      f'{[G.FRAMES[i] for i in range(3)]}')
check('frames 3-5 are the standing rest frames',
      all(G.FRAMES[i][0].endswith(f'{G.GOD_NAMES[i - 3]}_rest.png')
          for i in (3, 4, 5)), f'{[G.FRAMES[i][0] for i in (3, 4, 5)]}')
from PIL import Image                                              # noqa: E402
_imgs = [Image.open(os.path.join(ROOT, p)) for p, _ in G.FRAMES]
check('every frame is a P-mode PNG (imported index for index)',
      all(im.mode == 'P' for im in _imgs))
check('the three freed gods stand at one height (the 1994 scale)',
      len({_imgs[i].size[1] for i in (3, 4, 5)}) == 1,
      f'{[_imgs[i].size for i in (3, 4, 5)]}')
for g in range(3):
    run = range(G.RUN_BASE + g * G.RUN_LEN, G.RUN_BASE + (g + 1) * G.RUN_LEN)
    check(f'  {G.GOD_NAMES[g]}: one canvas and one hotspot for the whole run',
          len({(_imgs[i].size, G.FRAMES[i][1]) for i in run}) == 1)
    # THE CONTINUITY. The run's first frame is the 1994 statue itself, at
    # the statue's own hotspot, so the cut from frame g into the run is
    # invisible.
    st, first = _imgs[g], _imgs[run[0]]
    (hx, hy), (ax, ay) = G.FRAMES[g][1], G.FRAMES[run[0]][1]
    sp, fp = st.load(), first.load()
    same = all(fp[ax - hx + x, ay - hy + y] == sp[x, y]
               for y in range(st.height) for x in range(st.width)
               if sp[x, y] != 255)
    extra = sum(1 for y in range(first.height) for x in range(first.width)
                if fp[x, y] != 255) - sum(1 for v in st.getdata() if v != 255)
    check(f'  {G.GOD_NAMES[g]}: the run starts on the 1994 statue, pixel for '
          f'pixel, nothing else drawn', same and extra == 0, f'extra {extra}')
    rest = _imgs[3 + g]
    last = _imgs[run[-1]]
    (rx, ry), (lx, ly) = G.FRAMES[3 + g][1], G.FRAMES[run[-1]][1]
    rp, lp = rest.load(), last.load()
    check(f'  {G.GOD_NAMES[g]}: the run ends on her rest frame, same pixels '
          f'at the same world point',
          all(lp[lx - rx + x, ly - ry + y] == rp[x, y]
              for y in range(rest.height) for x in range(rest.width)))

# ── The run arithmetic, shared by four files ─────────────────────────────
print('\nR: run starts agree with the ceremony and the driver')
runs = {enc: G.RUN_BASE + enc * G.RUN_LEN for enc in (0, 1, 2)}
check('runs start at 6, 18, 30', list(runs.values()) == [6, 18, 30], f'{runs}')

# AOSCENE kicks each god with `if god.getFrame() = E { god.setFrame(R); }`.
aoscene = src('AOSCENE.UNK')
kicks = dict((int(e), int(r)) for e, r in re.findall(
    r'if god\.getFrame\(\) = (\d+)\s*\{\s*god\.setFrame\((\d+)\);', aoscene))
check('AOSCENE kicks all three gods', len(kicks) == 3, f'{kicks}')
check('each kick lands on that god\'s run start', kicks == runs, f'{kicks} vs {runs}')
check('AOSCENE no longer does the old blanket +3 swap',
      'getFrame() + 3' not in aoscene)

# GODANIM ends each run on the matching rest frame.
godanim = src('GODANIM.UNK')
ends = dict((int(f), int(t)) for f, t in re.findall(
    r'if f = (\d+)\s*\{\s*setFrame\((\d+)\);', godanim))
want_ends = {r + G.RUN_LEN - 1: enc + 3 for enc, r in runs.items()}
check('GODANIM lands each run on its god\'s standing frame',
      ends == want_ends, f'{ends} vs {want_ends}')
check('GODANIM gates every frame below the first run frame',
      f'if f < {G.RUN_BASE}' in godanim,
      'the gate is what stops sealed gods self-shattering on sight')

# TEMPLENT maps a god caught mid-run back onto her own rest frame.
templent = src('TEMPLENT.UNK')
check('TEMPLENT recovers a god left mid-run',
      f'/ {G.RUN_LEN}' in templent and f'> {G.RUN_BASE - 1}' in templent,
      'a player who walks out mid-shatter must not come back to a frozen run')
for enc, r in runs.items():
    last = r + G.RUN_LEN - 1
    check(f'  mid-run recovery maps frame {last} to {enc + 3}',
          3 + (last - G.RUN_BASE) // G.RUN_LEN == enc + 3)

# ── Dispatch ─────────────────────────────────────────────────────────────
print('\nD: the engine can actually deliver anim()')
man = json.load(open(MANIFEST))
cid = man['classes'].get('TYPEZEALANGOD')
# item.cpp:1516 — `uint32 class_id = _shape`. This is not a preference.
check('the usecode class id EQUALS the shape id',
      cid == G.GODS_SHAPE_ID,
      f'class {cid} vs shape {G.GODS_SHAPE_ID}; the engine takes the class '
      f'from the shape number, so these can never diverge')
check('GODANIM declares the anim() event',
      'process anim()' in godanim and 'TypeZealanGod::anim' in godanim)

at, ad, asp = G.ANIM
check('animType is 5 (call the item\'s usecode anim())', at == 5, f'{at}')
check('animSpeed is non-zero', asp > 0,
      'animType non-zero with animSpeed 0 divides by zero in Item::setupLerp')
check('animType/animData/animSpeed all fit their nibbles',
      all(0 <= v <= 15 for v in G.ANIM), f'{G.ANIM}')
try:
    set_anim(b'\x00' * 8, 5, 0, 0)
    check('set_anim refuses a zero speed with a live animType', False)
except ValueError:
    check('set_anim refuses a zero speed with a live animType', True)

if os.path.exists(TYPEFLAG):
    e = open(TYPEFLAG, 'rb').read()[
        G.GODS_SHAPE_ID * ENTRY_SIZE:(G.GODS_SHAPE_ID + 1) * ENTRY_SIZE]
    check('the BUILT TYPEFLAG carries animType 5',
          (e[4] & 0x0F) == 5, f'byte4={e[4]:#04x}')
    check('the BUILT TYPEFLAG carries a non-zero animSpeed',
          (e[5] & 0x0F) > 0, f'byte5={e[5]:#04x}')
else:
    print('  SKIP  built TYPEFLAG.DAT absent')

# ── The composited run art ───────────────────────────────────────────────
print('\nA: the run art is one canvas per god')
check('shatter + wake = the run length',
      F.SHATTER_LEN + F.WAKE_LEN == F.RUN_LEN == G.RUN_LEN, f'{F.RUN_LEN}')
run_dir = os.path.join(ROOT, 'shared', 'docs', 'art-poc', 'gods', 'run')
if os.path.isdir(run_dir):
    from PIL import Image
    for name, *_ in F.GODS:
        sizes = set()
        missing = []
        for k in range(F.RUN_LEN):
            p = os.path.join(run_dir, f'{name}_{k:02d}.png')
            if os.path.exists(p):
                sizes.add(Image.open(p).size)
            else:
                missing.append(k)
        check(f'  {name}: all {F.RUN_LEN} run frames present', not missing,
              f'missing {missing}')
        check(f'  {name}: every run frame is the same size', len(sizes) == 1,
              f'{sizes} — differing sizes move the bottom-centre anchor and '
              f'the god jitters on her own feet')
else:
    print('  SKIP  run art not generated yet')

# ── The wake's key mapping, at every level of completeness ───────────────
print('\nW: the wake maps keys to frames without ever blending')
from PIL import Image                                              # noqa: E402

CANVAS = (8, 12)


def _keys(n):
    """n distinguishable 1-pixel-tall sprites."""
    out = []
    for i in range(n):
        im = Image.new('RGBA', (2, 2), (0, 0, 0, 0))
        im.putpixel((0, 0), (i + 1, 0, 0, 255))
        out.append(im)
    return out


def _which(frames, keys):
    """Recover, per frame, which key was pasted — by its marker pixel."""
    got = []
    for f in frames:
        px = f.load()
        found = None
        for x in range(f.width):
            for y in range(f.height):
                r, _g, _b, a = px[x, y]
                if a:
                    found = r - 1
                    break
            if found is not None:
                break
        got.append(found)
    return got


# THE FULL SET IS THE PATH THAT MATTERS and the one that has never run: until
# all six keys exist the fallback masks it. With six it must be the identity,
# one drawn pose per frame and no repeats.
full = _keys(F.WAKE_LEN)
check('six keys map one-to-one, in order',
      _which(F.wake_frames(full, CANVAS), full) == list(range(F.WAKE_LEN)),
      f'{_which(F.wake_frames(full, CANVAS), CANVAS and full)}')

# Partial sets must still show every pose that exists — the first version of
# this threw the in-betweens away and cut between the two ends.
for n in (2, 3, 4, 5):
    seq = _which(F.wake_frames(_keys(n), CANVAS), None)
    check(f'  {n} keys: all {n} appear, in order, none skipped',
          sorted(set(seq)) == list(range(n)) and seq == sorted(seq),
          f'{seq}')

# Whatever the count, every frame is exactly one key — never two composited,
# which is what a blend would look like and what the format cannot carry.
for n in (2, 4, 6):
    frames = F.wake_frames(_keys(n), CANVAS)
    colours = [len({px for px in f.getdata() if px[3]}) for f in frames]
    check(f'  {n} keys: every frame carries exactly one pose',
          all(c == 1 for c in colours), f'{colours}')

print()
print(f'OK: {passed} passed, {failed} failed' if not failed
      else f'FAILED: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

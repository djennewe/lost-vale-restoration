#!/usr/bin/env python3
"""
test_lv_monsters.py — the expansion's own actors as built (docs/art-track.md
contract 9, lv_monsters.py and lv_actor_art.py, build step 6/8).

The Water Zombie 872 must be the ghoul 142 in every file the engine reads
for an actor except the pixels, and the pixels must be the ghoul's through
lv_actor_art.ZOMBIE_REMAP with the 1994 poses at ZOMBIE_POSES' frames; the
1994 NPC bodies 888-890 must be their donors (Mythran 190, the child 708)
in the same way, with every frame the donor's table names drawn:

  1. ZOMBIE_REMAP: never a cycling or transparent index, the outline kept,
     and every index it names still drawn by the base ghoul;
  2. U8SHAPES slot 872: 451 frames; every frame but the three poses is the
     base ghoul frame's geometry and anchor with its pixels remapped; each
     pose is the registry cut-out index for index; no cycling index;
  2c. U8SHAPES slots 888-890: the donor's frame count, the frames
     lv_actor_art derives, every ANIM.DAT-referenced frame non-empty, the
     shot poses index-equal to the registry cut-outs; no cycling index;
     the elder's SE talk moving about the exact screen19 pose (71 adds
     only its hidden cane), no staff knob left, the cane below the hand
     kept; the children without their black outline, each upright frame's
     spear in the hand (2026-10-30, art review cards 6 and 7);
  3. TYPEFLAG row = the donor's row; ANIM.DAT entry animates as the donor,
     for every lv_monsters.ACTORS row;
  4. the Lake's five eggs hatch 872 (and no LV egg still hatches the ghoul);
  5. the u8monsters.ini writer copies the donor row with shape=872 (873
     with the Harpie's own stats over the torax's), leaves the engine's
     rows untouched, and writes none for the NPC bodies;
  6. class 872 is pinned and compiled, and its look() barks its name.

Reads the BUILT artifacts under shared/build/: run tools/build_artifacts.sh
first. Plain script: exit 0 on pass, 1 on fail.
"""

import json
import os
import struct
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'tools'))
sys.path.insert(0, os.path.join(BASE_DIR, 'tools', 'art'))
sys.path.insert(0, os.path.join(BASE_DIR, 'agents', 'usecode-compiler', 'src'))

from u8_map import MapArchive                                  # noqa: E402
from map_preview import GlobReader, expand_globs               # noqa: E402
from shape_viewer import read_flx_entry, parse_shape_frames, SHAPES_FLX  # noqa: E402
from base_input import pristine_base                           # noqa: E402
from lv_tiny_avatar import actor_anim                          # noqa: E402
from lv_tiny_avatar_art import decode_anim                     # noqa: E402
from lv_monsters import (MONSTERS, NPCS, ACTORS, CYCLING,      # noqa: E402
                         HARPIE_FRAMES, drawn_frames,
                         lv_monsters_ini, ini_sections)
import lv_actor_art as LA                                      # noqa: E402
from lv_shapes import (SHAPE_WATER_ZOMBIE, SHAPE_MON_ZOMBIE,     # noqa: E402
                       SHAPE_HARPIE, SHAPE_MON_HARPIE, SHAPE_ZEALAN_ELDER,
                       SHAPE_SPEAR_CHILD_DARK, SHAPE_SPEAR_CHILD_BLOND)
from u8_flex import UsecodeFlexArchive                         # noqa: E402

BUILD = os.path.join(BASE_DIR, 'shared', 'build')
GHOUL = 142
TORAX = 120
LV_MAPS = (9, 10, 11, 13, 17, 18)

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def built(name):
    return open(os.path.join(BUILD, name), 'rb').read()


def pose_ok(f, sid, fno, anchor, mirror=False):
    """Is frame f the registry PNG of 1994 cut-out sid:fno, read here on its
    own: cycling indices swapped for their static twin, the POSE_HOLES
    filled, mirrored when the table shows it flipped, trimmed to its opaque
    box, with `anchor` (cut-out coordinates, before mirroring) its hotspot?"""
    import numpy as np
    from PIL import Image
    if f is None:
        return False
    fr = LA.load_registry()['shapes'][str(sid)]['frames'][fno]
    a = np.array(Image.open(os.path.join(BASE_DIR, fr['png'])), np.uint8)
    for i, j in LA.CYCLE_TWINS.items():
        a[a == i] = j
    for (x, y), idx in LA.POSE_HOLES.get((sid, fno), {}).items():
        a[y, x] = idx
    ax, ay = anchor
    if mirror:
        a, ax = a[:, ::-1], a.shape[1] - 1 - ax
    ys, xs = np.nonzero(a != 255)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return ((f['width'], f['height'], f['xoff'], f['yoff'])
            == (a.shape[1], a.shape[0], ax - xs.min(), ay - ys.min())
            and list(f['pixels']) == a.flatten().tolist())


# --- 1. the remap ----------------------------------------------------------
print('=' * 70)
print('1. lv_actor_art.ZOMBIE_REMAP')
REMAP = LA.ZOMBIE_REMAP
bad = sorted(v for v in REMAP.values() if v in CYCLING or v == 255)
check('no remap target is a cycling index (1-14) or transparency (255)',
      not bad, str(bad))
OUTLINE = (0, 30, 31, 78, 79, 222, 223)
check('the ghoul\'s black outline is kept', not set(OUTLINE) & set(REMAP))
base = open(pristine_base(SHAPES_FLX, None, 'base U8SHAPES.FLX'), 'rb').read()
ghoul = parse_shape_frames(read_flx_entry(base, GHOUL))
_used = {p for f in ghoul for p in f['pixels']}
check('every index the remap names is one the base ghoul draws (a stale '
      'remap means the base art changed: re-derive it)',
      set(REMAP) <= _used, str(sorted(set(REMAP) - _used)))

# --- 2. U8SHAPES -----------------------------------------------------------
print('=' * 70)
print('2. U8SHAPES slot 872 is the ghoul recoloured, the 1994 poses in place')
flx = built('U8SHAPES.FLX')
_data = read_flx_entry(flx, SHAPE_WATER_ZOMBIE)
zomb = parse_shape_frames(_data) if _data else []
check(f'slot {SHAPE_WATER_ZOMBIE} holds {len(ghoul)} frames like the ghoul',
      len(zomb) == len(ghoul) == 451, f'{len(zomb)} vs {len(ghoul)}')
POSED = {t for _s, _f, t, _a in LA.ZOMBIE_POSES}
geom = [i for i, (g, z) in enumerate(zip(ghoul, zomb)) if i not in POSED
        and (g['width'], g['height'], g['xoff'], g['yoff'])
        != (z['width'], z['height'], z['xoff'], z['yoff'])]
check('every frame but the poses keeps the ghoul frame\'s size and anchor',
      not geom, str(geom[:8]))
px = [i for i, (g, z) in enumerate(zip(ghoul, zomb)) if i not in POSED
      and [REMAP.get(p, p) for p in g['pixels']] != list(z['pixels'])]
check('every frame but the poses is the ghoul\'s pixels through the remap',
      not px, str(px[:8]))
for sid, fno, target, anchor in LA.ZOMBIE_POSES:
    f = zomb[target] if len(zomb) > target else None
    check(f'frame {target} is registry {sid}:{fno} index for index, '
          f'anchored at cut-out {anchor}', pose_ok(f, sid, fno, anchor),
          f and str((f['width'], f['height'], f['xoff'], f['yoff'])))
cyc = sorted({p for z in zomb for p in z['pixels'] if p in CYCLING})
check('no pixel of 872 lands on a cycling palette index', not cyc, str(cyc))
check('the base ghoul itself is untouched in the built FLX',
      read_flx_entry(flx, GHOUL) == read_flx_entry(base, GHOUL))

# --- 2b. the harpie's drawn frames -----------------------------------------
print('=' * 70)
print('2b. U8SHAPES slot 873 is the committed harpie frames, in the torax layout')
_hdata = read_flx_entry(flx, SHAPE_HARPIE)
harp = parse_shape_frames(_hdata) if _hdata else []
want = drawn_frames(HARPIE_FRAMES, 240)
check(f'slot {SHAPE_HARPIE} holds the torax\'s 240 frames', len(harp) == 240,
      str(len(harp)))
diff = [i for i, (a, b) in enumerate(zip(want, harp))
        if (a['width'], a['height'], a['xoff'], a['yoff'], list(a['pixels']))
        != (b['width'], b['height'], b['xoff'], b['yoff'], list(b['pixels']))]
check('every frame is the committed build input, pixels and anchor', not diff,
      str(diff[:8]))
anim = built('ANIM.DAT')
refs = sorted({struct.unpack_from('<B', act, 4 + 6 * k)[0]
               + ((act[4 + 6 * k + 1] & 7) << 8)
               for act in actor_anim(anim, TORAX) if act
               for k in range((len(act) - 4) // 6)})
undrawn = [r for r in refs if harp and harp[r]['width'] <= 1]
check(f'every frame the torax\'s ANIM.DAT entry names ({len(refs)}) is drawn',
      not undrawn and len(refs) == 86, f'{len(refs)} refs, undrawn {undrawn}')
cyc = sorted({p for h in harp for p in h['pixels'] if p in CYCLING})
check('no pixel of 873 lands on a cycling palette index', not cyc, str(cyc))
check('the base torax itself is untouched in the built FLX',
      read_flx_entry(flx, TORAX) == read_flx_entry(base, TORAX))

def placed(f):
    """{(x, y) relative to the hotspot: index} of frame f's opaque pixels."""
    w = f['width']
    return {(k % w - f['xoff'], k // w - f['yoff']): p
            for k, p in enumerate(f['pixels']) if p != 255}


def check_elder(got):
    """The SE talk moves around the exact screen19 pose, and every staff is
    cut back to the cane (Douglas 2026-10-30, art review card 6)."""
    import numpy as np
    from PIL import Image
    sid, fno, t71, (ax, ay) = LA.ELDER_POSES[1]
    fr = LA.load_registry()['shapes'][str(sid)]['frames'][fno]
    cut = np.array(Image.open(os.path.join(BASE_DIR, fr['png'])), np.uint8)
    for i, j in LA.CYCLE_TWINS.items():
        cut[cut == i] = j
    shot = {(x - ax, y - ay): int(cut[y, x])
            for y, x in zip(*np.nonzero(cut != 255))}
    cane = {(x - ax, y - ay): i for x, y, i in LA.ELDER_TALK_CANE}
    still = [t for t, deg in LA.ELDER_TALK_SE.items() if deg == 0]
    check('the SE talk has exactly one still frame, the screen19 pose\'s 71',
          still == [t71], str(still))
    px71 = placed(got[t71])
    check(f'888: frame {t71} is registry {sid}:{fno} index for index (every '
          f'cut-out pixel at its place) plus only ELDER_TALK_CANE, none of '
          f'which lands on the cut-out', px71 == {**shot, **cane}
          and not set(cane) & set(shot))
    moving = [t for t in LA.ELDER_TALK_SE if t != t71]
    differ = [t for t in moving if placed(got[t]) != px71]
    check(f'888: the other talk frames {moving} move (each differs from '
          f'{t71})', differ == moving and len(moving) == 2, str(differ))
    turn = set()
    for y, (x0, x1) in LA.ELDER_FOREARM.items():
        turn |= {(x - ax, y - ay) for x in range(x0, x1 + 1)}
    for t in moving:
        px = placed(got[t])
        body = {k: v for k, v in shot.items() if k not in turn
                and k[0] > max(LA.ELDER_ROBE_EDGE.values()) - ax}
        check(f'888: talk frame {t} keeps the pose\'s body right of the arm',
              all(px.get(k) == v for k, v in body.items()))
    # The cane: every knob is gone and the cane below the hand stays.
    myth = parse_shape_frames(read_flx_entry(base, 190))
    knob_left, cane_lost = [], []
    for i, (kx, ky, gx, gy, fx, fy, keep) in LA.ELDER_STAFF.items():
        d, b = myth[i], placed(got[i])
        dpx = placed(d)
        for (x, y), p in dpx.items():
            if p in LA.STAFF_KNOB and abs(x + d['xoff'] - kx) <= 3 \
                    and abs(y + d['yoff'] - ky) <= 3 and b.get((x, y)) == p:
                knob_left.append(i)
                break
        if keep == 'F' and i not in LA.ELDER_ATTACK:
            n = max(abs(fx - gx), abs(fy - gy))
            for k in range(3, min(7, n)):
                x = round(gx + (fx - gx) * k / n) - d['xoff']
                y = round(gy + (fy - gy) * k / n) - d['yoff']
                if (x, y) in dpx and (x, y) not in b:
                    cane_lost.append(i)
                    break
    check(f'888: no staff knob survives in the {len(LA.ELDER_STAFF)} cut-back '
          f'frames', not knob_left, str(sorted(set(knob_left))[:12]))
    check('888: the cane below the hand is kept in every walk/stand/talk/cast '
          'frame', not cane_lost, str(cane_lost[:12]))
    refs = set(LA.referenced(decode_anim(built('ANIM.DAT'), 888)))
    shown = {i for i in refs if i < len(myth) and not LA.blank(myth[i])}
    no_cut = sorted(shown - set(LA.ELDER_STAFF) - set(LA.ELDER_TALK_SE)
                    - {p[2] for p in LA.ELDER_POSES}
                    - set(LA.ELDER_COMBAT_STAND) - set(LA.ELDER_DIE))
    check('888: every drawn Mythran frame the table shows is in ELDER_STAFF '
          '(or replaced), so no tall staff is left anywhere',
          no_cut == [300, 332, 333], str(no_cut))


def check_child(got, table, sid):
    """No black outline; the spear in the hand (Douglas 2026-10-30, card 7)."""
    import numpy as np
    dirs = LA.drawn_directions(table, len(got))
    edge_black = edge_all = 0
    unheld = []
    for i, f in enumerate(got):
        if i == LA.CHILD_POSE_FRAME or LA.blank(f):
            continue
        a = LA.arr(f)
        op = a != 255
        edge = op & ~LA._inner(op)
        edge_black += int((a[edge] == 0).sum())
        edge_all += int(edge.sum())
        if i in LA.CHILD_DEATH or dirs.get(i) not in LA.SPEAR_FACING:
            continue
        hands = list(zip(*np.nonzero(a == LA.CHILD_HAND)))
        tip, butt = LA.spear_offsets(dirs[i])
        ok = False
        for y, x in hands:
            line = set(LA._line(x, y, x + tip[0], y + tip[1])) | set(
                LA._line(x, y, x + butt[0], y + butt[1]))
            nb = [(xx, yy) for yy in (y - 1, y, y + 1)
                  for xx in (x - 1, x, x + 1) if (yy, xx) != (y, x)
                  and 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1]
                  and a[yy, xx] != 255]
            shaft = set(LA.SPEAR_SHAFT) | set(LA.SPEAR_TIP)
            on = [p in line and a[p[1], p[0]] in shaft for p in nb]
            if any(on) and not all(on):
                ok = True
        if not ok:
            unheld.append(i)
    check(f'{sid}: no black outline (index 0 on {edge_black} of {edge_all} '
          f'silhouette-edge pixels, under 6%; it was 87%)',
          edge_all and edge_black < 0.06 * edge_all)
    check(f'{sid}: every upright frame holds its spear (a hand pixel on the '
          f'shaft, touching the body)',
          not unheld, str(unheld[:12]))


# --- 2c. the 1994 NPC bodies -----------------------------------------------
print('=' * 70)
print('2c. U8SHAPES slots 888-890: the 1994 elder and spear children')
check('lv_shapes names them 888, 889, 890',
      (SHAPE_ZEALAN_ELDER, SHAPE_SPEAR_CHILD_DARK, SHAPE_SPEAR_CHILD_BLOND)
      == (888, 889, 890))
check('NPCS are those three, from Mythran 190 and the child 708',
      [(m['shape'], m['donor']) for m in NPCS]
      == [(888, 190), (889, 708), (890, 708)])
_anim = built('ANIM.DAT')
for m in NPCS:
    sid, donor = m['shape'], m['donor']
    _d = read_flx_entry(flx, sid)
    got = parse_shape_frames(_d) if _d else []
    n_donor = len(parse_shape_frames(read_flx_entry(base, donor)))
    check(f'{sid}: {len(got)} frames, at least the donor {donor}\'s '
          f'{n_donor} (a saved frame number stays valid)',
          len(got) == m['frames'] >= n_donor)
    want = LA.actor_frames(m['art'], base, _anim)
    diff = [i for i, (a, b) in enumerate(zip(want, got))
            if (a['width'], a['height'], a['xoff'], a['yoff'], list(a['pixels']))
            != (b['width'], b['height'], b['xoff'], b['yoff'], list(b['pixels']))]
    check(f'{sid}: every frame is lv_actor_art\'s derivation',
          len(want) == len(got) and not diff, str(diff[:8]))
    refs = LA.referenced(decode_anim(_anim, sid))
    empty = [r for r in refs if r >= len(got) or LA.blank(got[r])]
    check(f'{sid}: all {len(refs)} frames its ANIM.DAT table names are drawn',
          refs and not empty, str(empty[:12]))
    cyc = sorted({p for f in got for p in f['pixels'] if p in CYCLING})
    check(f'{sid}: no pixel on a cycling palette index', not cyc, str(cyc))
    check(f'{sid}: the base donor {donor} is untouched in the built FLX',
          read_flx_entry(flx, donor) == read_flx_entry(base, donor))
    if m['art'] == 'elder':
        poses = [(s, f, t, a, False) for s, f, t, a in LA.ELDER_POSES
                 if t not in LA.ELDER_TALK_SE]
    else:
        s, f = LA.CHILD_POSES[m['art'].split('-')[1]]
        poses = [(s, f, LA.CHILD_POSE_FRAME, LA.CHILD_POSE_ANCHOR, True)]
    for s, f, t, anchor, mirror in poses:
        fr = got[t] if len(got) > t else None
        check(f'{sid}: frame {t} is registry {s}:{f}'
              f'{" mirrored" if mirror else ""} index for index, anchored '
              f'at cut-out {anchor}', pose_ok(fr, s, f, anchor, mirror),
              fr and str((fr['width'], fr['height'], fr['xoff'], fr['yoff'])))
    if m['art'] == 'elder':
        check_elder(got)
    else:
        check_child(got, decode_anim(_anim, sid), sid)

# --- 3. TYPEFLAG and ANIM.DAT ----------------------------------------------
print('=' * 70)
print('3. TYPEFLAG and ANIM.DAT')
tf = built('TYPEFLAG.DAT')
for m in ACTORS:
    new, donor = m['shape'], m['donor']
    check(f'TYPEFLAG row {new} = row {donor} '
          f'({tf[donor * 8:donor * 8 + 8].hex()})',
          tf[new * 8:new * 8 + 8] == tf[donor * 8:donor * 8 + 8])
    a_new, a_old = actor_anim(anim, new), actor_anim(anim, donor)
    check(f'ANIM.DAT entry {new} animates exactly as {donor} '
          f'(shared action table)', a_new is not None and a_new == a_old)
    check(f'ANIM.DAT entry {new} points at {donor}\'s table',
          struct.unpack_from('<I', anim, 4 * new)[0]
          == struct.unpack_from('<I', anim, 4 * donor)[0])

# --- 4. the eggs -----------------------------------------------------------
print('=' * 70)
print('4. the eggs hatch 872 and 873')
check('lv_shapes SHAPE_MON_ZOMBIE is the Water Zombie',
      SHAPE_MON_ZOMBIE == SHAPE_WATER_ZOMBIE == 872)
check('lv_shapes SHAPE_MON_HARPIE is the Harpie',
      SHAPE_MON_HARPIE == SHAPE_HARPIE == 873)
arch = MapArchive(os.path.join(BUILD, 'FIXED.DAT'))
gr = GlobReader()
eggs = {m: [(i.x, i.y, i.quality & 0x7FF, i.quality >> 11)
            for i in expand_globs(arch.get_map_items(m), gr) if i.shape == 500]
        for m in LV_MAPS}
lake = [e for e in eggs[10] if e[2] == SHAPE_WATER_ZOMBIE]
check('Map 10 places five Water Zombie eggs with a nonzero probability',
      len(lake) == 5 and all(e[3] for e in lake), str(lake))
cliff = [e for e in eggs[13] if e[2] == SHAPE_HARPIE]
check('Map 13 places four Harpie eggs with a nonzero probability',
      len(cliff) == 4 and all(e[3] for e in cliff), str(cliff))
old = {m: [e for e in es if e[2] in (GHOUL, TORAX)] for m, es in eggs.items()}
check('no LV egg still hatches the ghoul 142 or the torax 120',
      not any(old.values()), str({m: v for m, v in old.items() if v}))

# --- 5. u8monsters.ini -----------------------------------------------------
print('=' * 70)
print('5. the u8monsters.ini writer')
ENGINE = ('[ghoul]\nshape=142\nhp_min=35\nhp_max=50\ndex_min=14\ndex_max=16\n'
          'damage_min=6\ndamage_max=12\narmour=15\nalignment=0x68\nunk=1\n'
          'damage_type=0x0001\ndefense_type=0x0050\n\n\n'
          '[ghost]\nshape=411\nhp_min=80\n\n'
          '[torax]\nshape=120\nhp_min=40\nhp_max=55\ndex_min=8\ndex_max=12\n'
          'damage_min=7\ndamage_max=14\narmour=28\nalignment=0x24\nunk=1\n'
          'damage_type=0x0001\ndefense_type=0x0082\ntreasure=type=meat\n')
out = lv_monsters_ini(ENGINE)
sec = ini_sections(out)
check('the engine text is kept byte for byte at the head of the file',
      out.startswith(ENGINE.rstrip('\n')))


def expected(m, donor_lines):
    """The donor's row, key for key, with shape= and the row's stats."""
    over = dict(m.get('stats', {}), shape=m['shape'])
    out = []
    for ln in donor_lines:
        if not ln.strip() or ln.startswith('#'):
            continue
        k = ln.split('=')[0].strip()
        out.append(f'{k}={over[k]}' if k in over else ln)
    return out


for m in MONSTERS:
    new, donor = m['ini'][1], m['ini'][0]
    check(f'[{new}] is the [{donor}] row with shape={m["shape"]} and '
          f'{sorted(m.get("stats", {})) or "no other change"}',
          [ln for ln in sec.get(new, []) if ln.strip()
           and not ln.startswith('#')] == expected(m, sec[donor]),
          str(sec.get(new)))
zombie = next(m for m in MONSTERS if m['shape'] == 872)
zs = zombie.get('stats', {})
check('the Water Zombie is softer than the ghoul on every combat stat '
      '(docs/playtest-2026-10-25-phaseD-verify.md F2: one killed an armed '
      '30-hp Avatar in about 10 s)',
      zs.get('hp_max', 50) < 50 and zs.get('damage_max', 12) < 12
      and zs.get('dex_max', 16) < 16 and zs.get('armour', 15) < 15, str(zs))
harpie = next(m for m in MONSTERS if m['shape'] == 873)
check('the Harpie is no longer blade-proof or armour 28 '
      '(playtest-2026-10-11-monsters finding 5)',
      harpie.get('stats', {}).get('defense_type') == '0x0000'
      and harpie['stats'].get('armour', 28) <= 15,
      str(harpie.get('stats')))
check('every MONSTERS row gets a section', all(m['ini'][1] in sec for m in MONSTERS))
check('no NPC body (888-890) gets a u8monsters.ini row',
      not any(f"shape={m['shape']}" in out for m in NPCS)
      and not any('ini' in m for m in NPCS))
try:
    lv_monsters_ini('[ghost]\nshape=411\n')
    refused = False
except SystemExit:
    refused = True
check('the writer refuses an engine file without the donor row', refused)
try:
    lv_monsters_ini(ENGINE.replace('armour=28\n', ''))
    refused = False
except SystemExit:
    refused = True
check('the writer refuses a stat override the donor row does not carry',
      refused)
_dat = os.path.join(BASE_DIR, 'scummvm-lv', 'dists', 'engine-data', 'ultima8.dat')
if os.path.exists(_dat):
    import zipfile
    real = zipfile.ZipFile(_dat).read('u8monsters.ini').decode('latin-1')
    rs = ini_sections(lv_monsters_ini(real))
    for m in MONSTERS:
        new, donor = m['ini'][1], m['ini'][0]
        check(f'against the built engine\'s ultima8.dat: [{new}] carries '
              f'the {donor}\'s row with its overrides',
              [ln for ln in rs[new] if ln.strip()] == expected(m, rs[donor]))
else:
    print(f'  (no {os.path.relpath(_dat, BASE_DIR)} here: the real engine '
          f'file is checked in the main checkout only)')

# --- 6. classes 872, 873 ---------------------------------------------------
print('=' * 70)
print('6. classes 872 and 873')
man = json.load(open(os.path.join(BUILD, 'lv_manifest.json')))
uc = UsecodeFlexArchive(os.path.join(BUILD, 'EUSECODE.FLX'))
for pin, sid, name in (('TYPEWATERZOMBIE', 872, b'water zombie'),
                       ('TYPEHARPIE', 873, b'harpie')):
    check(f'{pin} is pinned to the shape (look() runs in class = shape, '
          f'item.cpp:1516)', man['classes'].get(pin) == sid,
          str(man['classes'].get(pin)))
    cls = uc.get_class_data(sid)
    check(f'EUSECODE class {sid} is compiled and its look() barks '
          f'"{name.decode()}"', bool(cls) and name in cls)

print('=' * 70)
print(f'{passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

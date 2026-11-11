#!/usr/bin/env python3
"""
test_paint_cycles.py — the two places ScummVM logged `Cycle in paint
dependency graph` by the hundred thousand draw clean in a port of its
sorter (item_sorter.py).

1. Map 10, Gunnar village's still and workshop (TODO.md 2026-10-02): each
   workbench (208, 96x160) sat at +(160,600) from its hut, straddling the
   hut's south wall (856) and the zero-depth vine line (426) on its face,
   and burying the NPC who works there. ~110,000 lines a session, pairs
   426/208, 526/426, 707/426, 426/856, 856/208
   (docs/playtest-2026-10-02-pt-activity.md finding 7). The port finds
   426 -> 208 -> 526 -> 426 and 426 -> 208 -> 707 -> 426 there.
2. Map 8, the LORDBRIT backstop (docs/playtest-2026-10-04-lb-detour.md
   finding 3): the apparition (411, 96x96x48 at z 8) stood on Mythran's
   dining table (263) over its four cups (182, U8SAVE.000's NONFIXED.DAT)
   and up through the floor above (164 at z 40). 3,533 lines, logged as
   182 -> 411; the port's item order meets the same knot elsewhere, as
   149 -> 222 -> 411 -> 164 from every camera south of the house.
3. Map 18, the restored Shield on the Inner Sanctum altar (2026-10-09).
   Not a logged cycle but a placement made at run time: lv-new/AOSCENE.UNK
   pop()s the Shield (879 since 2026-10-17, screen04's spot on the floor
   altar; a legacy 828 is the same box) to fixed coordinates on the altar
   (550) top face, and
   map-geometry.md records that a small box resting on a solid's top face
   is exactly where the engine logged `Cycle ... 859 -> 526`. The three
   numbers are read out of AOSCENE.UNK and checked against build_map_18's
   altar: on its top face by the half-open box arithmetic, SI_LAND under
   it, overlapping no solid, and drawing without a cycle.
4. The two knots the Avatar closes by standing somewhere reachable
   (docs/research/2026-10-10-map10-paint-cycles.md section 5.2): Map 10's
   test-grounds spire through the rim column (`66 -> 1`) and Map 13's
   summit floor through the harpie zone's west face (`3 -> 32`). The
   Avatar (shape 1) is added to the frame at each spot; the port could not
   draw him before 2026-10-10, when item_sorter.frame learned to read
   shapes of more than 500 frames.
5-7. Map 8's doorway column, and Map 13 framed from every climb spot,
   with the Avatar on every climb cell and riser (each section says why).
8. The Avatar at every LV teleport arrival pad and at every 1994 shot's
   Avatar spot, and on the ground round each: Map 10's pad 210 logged
   28,712 lines through the endgame scene (verify3 F1), a knot no
   camera-only frame can see.
Cameras are the Avatar positions the engine logged from, plus ones the port
found cycling around the old placements; the NPCs stand at their start
spots, as on a fresh world. Both maps come from the builders' in-memory
output, so this fails on a builder edit before any rebuild; Map 8's base
is retail (the pristine FIXED.DAT, minus build_map_08's removals) plus the
new-game NONFIXED.DAT, because the cups are not ours.

The port's limits (item_sorter.py docstring) make zero cycles evidence,
not proof: the in-engine check is a log with no such line.

    python3 agents/map-populator/src/test_paint_cycles.py

Plain script: exit 0 on pass, 1 on fail.
"""

import contextlib
import io
import os
import re
import sys
import tempfile

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_map import MapArchive                     # noqa: E402
from map_preview import GlobReader, expand_globs  # noqa: E402
from item_sorter import ItemSorter, TYPEFLAG, SHAPES   # noqa: E402

BASE_FIXED = os.path.join(REPO, 'shared', 'data', 'u8-install', 'STATIC',
                          'FIXED.DAT')
U8SAVE = os.path.join(REPO, 'shared', 'data', 'u8-install', 'SAVEGAME',
                      'U8SAVE.000')
NEAR = 2200          # items farther than this from the camera cannot be in
                     # a 640x400 frame; dropping them only saves time

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def quiet(fn):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn()


def frame_cycles(sorter, items, cam, roof_cut=False):
    near = [i for i in items
            if abs(i.x - cam[0]) < NEAR and abs(i.y - cam[1]) < NEAR]
    if roof_cut:
        # GameMapGump::PaintThis: under a roof, nothing at or above the
        # roof's z is drawn unless it is SI_DRAW.
        zlimit = min((i.z for i in near
                      if sorter.info(i.shape)['roof'] and i.z >= 40
                      and i.x - sorter.info(i.shape)['xd'] < cam[0] <= i.x
                      and i.y - sorter.info(i.shape)['yd'] < cam[1] <= i.y),
                     default=None)
        if zlimit is not None:
            near = [i for i in near if i.z < zlimit
                    or sorter.info(i.shape)['draw']]
    return sorter.cycles(near, cam)


def show(cycles):
    return '; '.join(' -> '.join(f'{s}@({x},{y},{z})' for s, _f, x, y, z in c)
                     for c in cycles[:3])


for path in (TYPEFLAG, SHAPES):
    if not os.path.exists(path):
        print(f'  {path} absent — run tools/build_artifacts.sh')
        sys.exit(1)
sorter = ItemSorter()
gr = GlobReader()


def engine_items(raw):
    """A builder's items in the engine's list order: a glob's tiles are
    last in their chunks (GlobEgg::enterFastArea, FLG_FAST_ONLY:
    addItemToEnd)."""
    return [i for i in raw if not i.is_glob_egg] + [
        g for i in raw if i.is_glob_egg
        for g in gr.glob_to_items(i.quality, i.x, i.y, i.z)]


# --- 1. Map 10, Gunnar village --------------------------------------------
print('=' * 70)
print("Map 10 Gunnar village — the still's and the workshop's workbenches")
from build_map_10 import build_map_10              # noqa: E402
raw10 = quiet(build_map_10)
map10 = expand_globs(raw10, gr)
for cam in ((21760, 8544, 0),     # the Avatar's spot in both engine logs
            (20256, 7512, 0),     # the still's front, from the south-west
            (20512, 9560, 0),     # the workshop's front
            (21632, 8000, 0),     # beside the still station
            (21632, 10048, 0)):   # beside the workshop station
    c = frame_cycles(sorter, map10, cam)
    check(f'camera {cam}: no paint cycle', not c, show(c))

# --- 2. Map 8, the LORDBRIT backstop ---------------------------------------
print('=' * 70)
print("Map 8 — the backstop apparition in Mythran's dining room")
from base_input import pristine_base              # noqa: E402
import build_map_08                               # noqa: E402
from scan_npc_slots import read_u8save            # noqa: E402

if not (os.path.exists(BASE_FIXED) and os.path.exists(U8SAVE)):
    print('  game data absent (shared/data/u8-install) — cannot run')
    sys.exit(1)
base8 = quiet(lambda: MapArchive(pristine_base(BASE_FIXED, None,
                                               'FIXED.DAT base')))
base8 = [i for i in base8.get_map_items(8)
         if (i.x, i.y, i.z, i.shape) not in build_map_08.BASE_ITEM_REMOVALS]
with tempfile.TemporaryDirectory() as tmp:
    nf = os.path.join(tmp, 'NONFIXED.DAT')
    with open(nf, 'wb') as fh:
        fh.write(read_u8save(U8SAVE)['NONFIXED.DAT'])
    # x <= 2 marks a contained item (x = container depth), not a position.
    nonfixed8 = [i for i in MapArchive(nf).get_map_items(8) if i.x > 2]
map8 = (expand_globs(base8, gr) + quiet(build_map_08.build_map_08_additions)
        + nonfixed8)

app = (build_map_08.LB_BACKSTOP_APPARITION_X,
       build_map_08.LB_BACKSTOP_APPARITION_Y)
for cam in ((2200, 2660, 0),      # south of the house: the old spot cycled
            (1600, 2724, 0),      # from every camera south of y 2596
            (2880, 2852, 0),
            (2200, 2400, 0),      # in the room, the floor above cut away
            (app[0] + 64, app[1] + 128, 0)):
    c = frame_cycles(sorter, map8, cam, roof_cut=True)
    check(f'camera {cam}: no paint cycle', not c, show(c))

# --- 3. Map 18, the restored Shield on the altar ---------------------------
print('=' * 70)
print('Map 18 — the restored Shield where AOSCENE puts it, on the altar top')
from build_map_18 import build_map_18             # noqa: E402
from u8_map import MapItem                        # noqa: E402
AOSCENE = os.path.join(REPO, 'agents', 'usecode-compiler', 'src', 'lv-new',
                       'AOSCENE.UNK')
SHAPE_SHIELD, SHAPE_ALTAR, Q_ALTAR = 879, 550, 310
m = re.search(rb'shield\.pop\((\d+),\s*(\d+),\s*(\d+)\)',
              open(AOSCENE, 'rb').read())
check('AOSCENE.UNK pops the Shield to literal coordinates', m is not None)
raw18 = quiet(build_map_18)
map18 = expand_globs(raw18, gr)
altars = [i for i in map18 if i.shape == SHAPE_ALTAR and i.quality == Q_ALTAR]
check('build_map_18 places exactly one altar (550, quality 310)',
      len(altars) == 1, f'{len(altars)}')
if m and len(altars) == 1:
    sx, sy, sz = (int(v) for v in m.groups())
    alt = altars[0]
    a, s = sorter.info(SHAPE_ALTAR), sorter.info(SHAPE_SHIELD)
    # Box::contains is half-open: an item at x with depth xd covers
    # x-xd+1 .. x, so the Shield's span fits inside the altar's when both
    # low edges and both high edges nest.
    check(f'the Shield ({sx}, {sy}) sits within the altar top '
          f'({alt.x}, {alt.y})',
          alt.x - a['xd'] <= sx - s['xd'] and sx <= alt.x
          and alt.y - a['yd'] <= sy - s['yd'] and sy <= alt.y,
          f"shield x {sx - s['xd'] + 1}..{sx} y {sy - s['yd'] + 1}..{sy}; "
          f"altar x {alt.x - a['xd'] + 1}..{alt.x} y {alt.y - a['yd'] + 1}..{alt.y}")
    check(f'...resting on its top face (z {sz} = {alt.z} + {a["zd"]})',
          sz == alt.z + a['zd'])
    check('the altar is SI_LAND, so the Shield is supported there', a['land'])

    def overlaps(i, x, y, z, d):
        o = sorter.info(i.shape)
        return (x - d['xd'] < i.x and i.x - o['xd'] < x
                and y - d['yd'] < i.y and i.y - o['yd'] < y
                and z < i.z + o['zd'] and i.z < z + d['zd'])
    buried = [(i.shape, i.x, i.y, i.z) for i in map18
              if sorter.info(i.shape)['solid'] and overlaps(i, sx, sy, sz, s)]
    check('the Shield overlaps no solid (not buried)', not buried,
          f'{buried[:4]}')
    shield = MapItem(x=sx, y=sy, z=sz, shape=SHAPE_SHIELD, frame=0,
                     quality=83)
    for cam in ((3072, 8448, 24),     # the egg's south edge, the approach
                (3072, 8320, 24),     # on the ceremony egg
                (2700, 8400, 0), (3400, 8400, 0),
                (2600, 7800, 0), (3500, 7800, 0)):
        c = frame_cycles(sorter, map18 + [shield], cam)
        check(f'camera {cam}: no paint cycle with the Shield on the altar',
              not c, show(c))

# --- 4. The Avatar's own knots: Map 10's spire, Map 13's summit ------------
# Standing spots the report's scan found reachable and cycling (section 5.2),
# re-found by the same scan before the fix. A cycle that does not run
# through the Avatar is a static one, which section 1 and the maps' own
# scan cover; only his are counted here.
print('=' * 70)
print('The Avatar standing at the two reachable knots of 2026-10-10')
check('the port draws the Avatar (shape 1 has 1,550 frames)',
      sorter.frame(1, 0) is not None)
from build_map_13 import build_map_13             # noqa: E402
map13 = expand_globs(quiet(build_map_13), gr)
spots = [(map10, 10, 'the test-grounds spire by the rim column',
          (12383, 29631, 64))]
spots += [(map13, 13, "the summit by the harpie zone's west face", (x, y, 120))
          for x in (2975, 3007, 3039) for y in (447, 639, 831, 927)]
for items, mapnum, where, (ax, ay, az) in spots:
    av = MapItem(x=ax, y=ay, z=az, shape=1, frame=0)
    c = [cy for cy in frame_cycles(sorter, items + [av], (ax, ay, az))
         if any(s == 1 for s, *_ in cy)]
    check(f'map {mapnum}, {where}: the Avatar at ({ax},{ay},{az}) closes '
          f'no paint cycle', not c, show(c))

# --- 5. Map 8, the Avatar in the doorway column by the bone field ----------
# playtest-2026-10-11-build7 finding 3 logged 12 `358 -> 1` lines as the
# Avatar walked north up the doorway column (x 20383) to the double doors.
# The LV chest (78) at (20436,3370,0) overlapped the retail skeleton (358,
# U8SAVE's NONFIXED) at (20447,3487,0) by 11 units in y, and the Avatar at
# (20383,3456,0) closed 358 -> 1 -> 78 in 38 of his first 64 frames. The
# same run's 2,055 `590 -> 235` and `235 -> 65` lines are a retail knot
# (skeleton 235 at (20127,3199), mushrooms 65 at (20031,3167), 590 at
# (20064,3080,5)) with no LV item in it; the run's log credited 640 of them
# to Map 10 because a save load prints no "Loading Fixed items" line.
print('=' * 70)
print('Map 8 — the Avatar walking the doorway column past the LV chest')
chests = [i for i in map8 if i.shape == 78 and
          (i.x, i.y) == (build_map_08.CHEST_X, build_map_08.CHEST_Y)]
check('build_map_08 places the double-door key chest (78)', len(chests) == 1,
      f'{len(chests)}')
for ay, az in ((3440, 8), (3456, 0), (3472, 0)):
    knots = set()
    for fr in range(64):
        if sorter.frame(1, fr) is None:
            continue
        av = MapItem(x=20383, y=ay, z=az, shape=1, frame=fr)
        knots |= {tuple(s for s, *_ in cy)
                  for cy in frame_cycles(sorter, map8 + [av], (20383, ay, az))
                  if any(s == 1 for s, *_ in cy)}
    check(f'map 8, the Avatar at (20383,{ay},{az}), frames 0-63: closes no '
          f'paint cycle', not knots, f'{sorted(knots)}')

# --- 6. Map 13, every frame the climb and the summit show -------------------
# Sections 1-5 frame only the places a cycle was once logged. The 2026-10-17
# vignette session logged 254,668 more on Map 13 (26 -> 564 -> .. -> 26 and
# 125 -> 66 -> .. -> 125), with no Avatar in them: two 1994 shots' own
# pieces solved inside their neighbours (build_map_13.RAY_SLIDES /
# SHOT_CUTS). The port finds both from the climb's cameras on that build
# (e.g. (5119,4607,84) and (5119,2559,120)). So the map is now framed from
# the Avatar's spot on every second climb tile and every summit cell, and
# no frame may hold a cycle, the Avatar's or not. Since screen13 lies at
# the climb's turn (2026-10-17, pass d), the north leg's dead end and every
# cell of screen13's island are framed too.
print('=' * 70)
print('Map 13 — the climb, the summit and the city edge, every frame')
import build_map_13                               # noqa: E402
import lv_map13_tiers                             # noqa: E402
spots13 = build_map_13.climb_tiles()[::2] + [
    (lv_map13_tiers.corner(cx), lv_map13_tiers.corner(cy), z)
    for (cx, cy), z in sorted({**quiet(build_map_13.summit_cells),
                               **build_map_13.CLIMB_STUB,
                               **quiet(build_map_13.city_edge_cells)}.items())]
knots = {}
for cam in spots13:
    for cy in frame_cycles(sorter, map13, cam):
        knots.setdefault(frozenset(cy), (cam, cy))
check(f'map 13: {len(spots13)} climb, summit and city-edge frames close no '
      f'paint cycle', not knots,
      show([cy for (_cam, cy) in knots.values()]))

# --- 7. Map 13, the Avatar on every climb cell and mid-step on every riser -
# Section 6 frames the map with no one in it. The verifier's mouse run down
# the north leg (2026-10-17 pass 2, 3d) logged `1 -> 125 -> ... -> 1` four
# times: the Avatar's own knot. The engine draws a moving item at its
# lerped position (Item::doLerp: prev * (256 - f) + next * f, then >> 8),
# and the floor puts him at the LOWER z for the last quarter of a tick's
# step down a riser (or the first quarter of one up it) while his box
# still reaches into the higher cell: with every lane rising on the same
# row, the east lane's higher crest, its lower crest in front and he made a
# knot at every riser of both north-south legs (57 knots, 896 positions on
# FIXED 1482caca; build_map_13.climb_cells' lane stagger closes them). So
# he stands on every climb cell, its centre and flush with each side, and
# across every side to a climb neighbour at the higher of the two z; and on
# each side of every riser at the lower z, his box 1, 4 and 8 units into
# the higher cell (a tick moves him at most 32). Frames: walk, run and
# stand both ways along the riser or the leg. The camera is his position
# plus 20 in z (CameraProcess), he is first in his chunk's list
# (CurrentMap::addItem, push_front), and a glob's tiles are last in theirs
# (GlobEgg::enterFastArea, FLG_FAST_ONLY: addItemToEnd). Only the sprites
# round him are sorted (AV_CLIP); a cycle through him runs through items
# his sprite overlaps.
print('=' * 70)
print('Map 13 — the Avatar on every climb cell, and mid-step on every riser')
import concurrent.futures                          # noqa: E402
import multiprocessing                             # noqa: E402
import avatar_mover                                # noqa: E402
from item_sorter import FLG_FLIPPED                # noqa: E402

AV_CLIP = (-160, -140, 160, 120)
AV_NEAR = 700
raw13 = quiet(build_map_13.build_map_13)
eng13 = engine_items(raw13)
AV_FRAMES = {h: sorted({f for act in (avatar_mover.WALK, avatar_mover.RUN,
                                      avatar_mover.STAND)
                        for f in avatar_mover.sprite_frames(act, d)})
             for h, d in avatar_mover.DIRS.items()}
cells13 = build_map_13.climb_cells()


def standing_z(x, y):
    """The highest climb cell his box (x - 64, x] x (y - 64, y] is on."""
    return max((z for (cx, cy), z in cells13.items()
                if cx - 128 < x and x - 64 < cx and cy - 128 < y
                and y - 64 < cy), default=None)


AXES = {(0, -128): 'NS', (0, 128): 'NS', (-128, 0): 'EW', (128, 0): 'EW'}
av_spots = set()
for (X, Y), z in cells13.items():
    for x, y in ((X - 32, Y - 32), (X - 64, Y - 32), (X, Y - 32),
                 (X - 32, Y - 64), (X - 32, Y)):
        av_spots |= {(x, y, z, h) for h in 'NSEW'}
    for (dx, dy), axis in AXES.items():
        nz = cells13.get((X + dx, Y + dy))
        if nz is None:
            continue
        # across the side, at the higher z
        x = {128: X + 32, -128: X - 96}.get(dx, X - 32)
        y = {128: Y + 32, -128: Y - 96}.get(dy, Y - 32)
        av_spots |= {(x, y, standing_z(x, y), h) for h in axis}
        if nz >= z:
            continue
        # mid-step down from (X, Y) to its lower neighbour: drawn at the
        # lower z, his box 1, 4 and 8 units into this cell
        for e in (1, 4, 8):
            for t in (-64, -32, 0):
                if dy > 0:
                    p = (X + t, Y + 64 - e)
                elif dy < 0:
                    p = (X + t, Y - 128 + e)
                elif dx > 0:
                    p = (X + 64 - e, Y + t)
                else:
                    p = (X - 128 + e, Y + t)
                av_spots |= {(*p, nz, h) for h in axis}
av_spots = sorted(av_spots)


def avatar_knots(spot):
    x, y, z, h = spot
    near = [i for i in eng13 if abs(i.x - x) < AV_NEAR and abs(i.y - y) < AV_NEAR]
    found = set()
    for fr, flipped in AV_FRAMES[h]:
        av = MapItem(x=x, y=y, z=z, shape=1, frame=fr,
                     flags=FLG_FLIPPED if flipped else 0)
        for cy in sorter.cycles([av] + near, (x, y, z + 20), AV_CLIP):
            if any(s == 1 for s, *_ in cy):
                found.add((fr, tuple(cy)))
    return spot, found


knots = {}
with concurrent.futures.ProcessPoolExecutor(
        max_workers=max(1, (os.cpu_count() or 2) - 1),
        mp_context=multiprocessing.get_context('fork')) as pool:
    for spot, found in pool.map(avatar_knots, av_spots, chunksize=32):
        for fr, cy in found:
            key = frozenset((s, x, y, z) for s, _f, x, y, z in cy if s != 1)
            knots.setdefault(key, (spot, fr, cy))
check(f'map 13: the Avatar at {len(av_spots)} climb spots (cells, sides, '
      f'risers mid-step) closes no paint cycle', not knots,
      f'{len(knots)} knots, e.g. ' +
      '; '.join(f'{spot} frame {fr}: ' + ' -> '.join(
          f'{s}@({x},{y},{z})' for s, _f, x, y, z in cy)
          for spot, fr, cy in list(knots.values())[:3]))

# --- 8. The Avatar at every arrival pad and every shot's Avatar spot -------
# Sections 4-7 stand him where a knot was once logged. verify3 (2026-10-17,
# F1) logged 28,712 `125 -> 107 -> .. -> 125` lines while he stood on Map
# 10's pad 210 for the whole endgame scene: screen17's top stair block,
# solved with its top 8 over the shelf the pad is on, sorted over him by y
# while the shelf's crest under him sorted under him by z
# (build_map_10.RAY_SLIDES). A teleport puts him on a pad and a scene can
# hold him there, and a 1994 shot's Avatar spot is a place the shot says he
# stands, so he is checked on every LV arrival pad (every teleport target on
# the LV maps, and Map 8's 200 and 213) and every shot's Avatar spot, and on
# the ground round each within 64 units in steps of 32 where he can rest
# (the highest top at most 8 over the spot's z, his body clear of every
# solid), with section 7's frames (walk, run and stand, all eight
# headings; at a shot's spot its own frame too), camera, clip and order.
print('=' * 70)
print('The Avatar on every arrival pad and every 1994 shot\'s Avatar spot')
import vignette_place as VP                       # noqa: E402
import build_map_09                               # noqa: E402
import build_map_11                               # noqa: E402
import build_map_17                               # noqa: E402

eng_by_map = {
    8: map8,
    9: engine_items(quiet(build_map_09.build_map_09)),
    10: engine_items(raw10),
    11: engine_items(quiet(build_map_11.build_map_11)),
    13: eng13,
    17: engine_items(quiet(build_map_17.build_map_17)),
    18: engine_items(raw18),
}
spot_list = [(m, f'pad {i.quality}', (i.x, i.y, i.z), None)
             for m, items in eng_by_map.items() for i in items
             if i.is_teleport_target and (m != 8 or 200 <= i.quality <= 213)]
check('every LV map has an arrival pad, and Map 8 its two (200, 213)',
      {m for m, *_ in spot_list} == set(eng_by_map) and
      sorted(w for m, w, *_ in spot_list if m == 8) == ['pad 200', 'pad 213'],
      str(sorted((m, w) for m, w, *_ in spot_list)))
for _f in sorted(os.listdir(VP.VIGNETTE_DIR)):
    if _f.startswith('screen') and _f.endswith('.json'):
        _v = VP.load(_f[:-5])
        _o = VP.origin(_v)
        spot_list += [(_v['placement']['map'], _f[:-5],
                       (a['x'] + _o[0], a['y'] + _o[1], a['z'] + _o[2]),
                       a['frame']) for a in _v['actors'] if a['shape'] == 1]
_worlds = {m: avatar_mover.World(items, avatar_mover.load_shapes(),
                                 (0, 0, 32767, 32767))
           for m, items in eng_by_map.items()}
spot_jobs = []
for m, where, (x0, y0, z0), own in spot_list:
    for dx in (-64, -32, 0, 32, 64):
        for dy in (-64, -32, 0, 32, 64):
            x, y, z = x0 + dx, y0 + dy, z0
            if (dx, dy) != (0, 0):
                z = _worlds[m].landing(x, y, z0 + 8)
                if not _worlds[m].resting(x, y, z):
                    continue
            spot_jobs.append((m, where, x, y, z,
                              own if (dx, dy) == (0, 0) else None))


def spot_knots(job):
    m, _where, x, y, z, own = job
    near = [i for i in eng_by_map[m]
            if abs(i.x - x) < AV_NEAR and abs(i.y - y) < AV_NEAR]
    rz = sorter.roof_z(near, x, y, z)
    if rz is not None:
        # GameMapGump::PaintThis: under a roof, nothing at or above the
        # roof's z is drawn unless it is SI_DRAW
        near = [i for i in near if i.z < rz or sorter.info(i.shape)['draw']]
    frames = {f for fs in AV_FRAMES.values() for f in fs}
    if own is not None and sorter.frame(1, own) is not None:
        frames.add((own, False))
    found = set()
    for fr, flipped in sorted(frames):
        av = MapItem(x=x, y=y, z=z, shape=1, frame=fr,
                     flags=FLG_FLIPPED if flipped else 0)
        for cy in sorter.cycles([av] + near, (x, y, z + 20), AV_CLIP):
            if any(s == 1 for s, *_ in cy):
                found.add((fr, tuple(cy)))
    return job, found


spot_hits = {}
with concurrent.futures.ProcessPoolExecutor(
        max_workers=max(1, (os.cpu_count() or 2) - 1),
        mp_context=multiprocessing.get_context('fork')) as pool:
    for job, found in pool.map(spot_knots, spot_jobs, chunksize=4):
        for fr, cy in found:
            key = (job[0], job[1],
                   frozenset((s, x, y, z) for s, _f, x, y, z in cy if s != 1))
            spot_hits.setdefault(key, (job, fr, cy))
for m, where, (x0, y0, z0), _own in spot_list:
    bad = [v for (km, kw, _k), v in spot_hits.items()
           if (km, kw) == (m, where)]
    n = sum(1 for j in spot_jobs if j[:2] == (m, where))
    check(f'map {m}, {where} ({x0},{y0},{z0}): the Avatar at {n} spots on '
          f'and round it closes no paint cycle', not bad,
          f'{len(bad)} knots, e.g. ' + '; '.join(
              f'({j[2]},{j[3]},{j[4]}) frame {fr}: ' + ' -> '.join(
                  f'{s}:{f}@({x},{y},{z})' for s, f, x, y, z in cy)
              for j, fr, cy in bad[:2]))

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

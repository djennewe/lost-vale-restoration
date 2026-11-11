#!/usr/bin/env python3
"""
test_monster_eggs.py — every LV monster egg hatches, and hatches its
monster somewhere it can stand and fight.

WHY (playtest-2026-10-11-monsters findings 1, 3, 4). Until 2026-10-11 no
LV monster egg ever hatched: a shape-500 MonsterEgg is not an Egg, so only
a MONEGG trigger (UnkEgg quality 2, class 0x481) hatches it, and the LV
maps had none. Hatched by hand they stood in the Lake's water and drowned,
hung inside Map 13's cliff course or fell to their death, and loitered
beside the Avatar without attacking. lv_monster_eggs.py has the mechanism.

Against the BUILT FIXED.DAT (.claude/rules/map-geometry.md: test what
ships, globs expanded), for every monster egg on Maps 9, 10, 11, 13, 17
and 18:

  1. activity 1, combat (mapNum & 7), as 292 of retail's 418 eggs;
  2. a MONEGG trigger on the map whose group (mapNum & 0x1F) is the egg's
     (mapNum >> 3) and whose 3584-unit area search reaches it
     (CurrentMap::areaSearch: x in [tx - txd - 3584, tx + 3584]);
  3. the monster's own body (its TYPEFLAG footpad) at the egg stands the
     way CurrentMap::getPositionInfo stands an actor — no solid overlaps
     it, a support's top is exactly its z, LAND under its bottom centre
     within 8 — and it is DRY (no SEA tile's top at its z: CLRWATER
     drowns what stands on it), clear of everything that burns by 32
     (SI_DAMAGING or exact_reach.HURT_SHAPES_U8), and not on an edge: the
     same holds 32 units off in all eight directions;
  4. the Avatar can walk to it (a dry flood from the map's arrival pad
     reaches a position within 64 of it, within 8 of its z), so what
     hatches can come to him.

And for every MONEGG trigger on those maps:

  5. its group has an egg in reach (no orphan trigger) and is the only
     trigger of that group on the map;
  6. its hatch box (EggHatcherProcess::run: x1 <= px, px - 64 < x2, the
     same on y, tz - 48 < pz <= tz + 48) holds a position that dry flood
     reaches, so walking can fire it;
  7. its nearest egg is at least MIN_HATCH_GAP away (Chebyshev), so a
     monster never hatches on top of the Avatar.

playtest-2026-10-11-monsters2 (findings 1-4), the run that saw them hatch:

  F1. every LV egg is one-shot (frame 1): a frame-0 group hatched again
      on each return through its doorway, on top of its survivors;
  F2. every egg hatches inside the 320x200 fast area from every position
      that fires its trigger, at each z the Avatar stands at in the box,
      and a monster that does not see him at once (its seek square misses
      a box corner) has its whole loiter square inside it as well
      (lv_monster_eggs.hatch_fast_problem; outside, Item::enterFastArea
      clears its combat and it stands passive, and a loiterer that walks
      out is destroyed). The mirror of CurrentMap::updateFastArea is
      first checked against the run's log: which hatchlings came in fast;
  F3. no stumble (the Avatar's stumbleBackwards, ANIM.DAT shape 1 action
      13, which every blow plays, taken step by step as
      AnimationTracker::step and scanForValidPosition take it) from any
      spot he walks to in a trigger's box, or within that stumble's reach
      of an egg, ends in water, on a burning shape or off an edge: the
      Avatar drowned that way on the Lake's pier.

playtest-2026-10-12-monsters3 (findings 1-2), the round after:

  F4. no spot the Avatar walks to within FIGHT_ZONE (the seek range) of a
      trigger's box or an egg is on the water, and no stumble from one
      ends on it: the fight drifted off the railed pier onto the shore,
      and he drowned there;
  F5. from every spot in a trigger's box, the monster's shortest walk (its
      own body) to him is at most WALK_RATIO x the straight line, or
      WALK_SLACK over it: golems 1 and 7 hatched fighting behind a wall
      from their triggers and never came round it.

Douglas's decisions of 2026-10-11 on the balance check:

  8. the Lake's Water Zombies (Map 10) and the harpies (Map 13) are
     one-shot (frame 1) and come in waves — at least three on the Lake,
     of at most two zombies; at least four on the climb and the summit, of
     ONE harpie each (Douglas 2026-10-24 the climb's, 2026-10-30 the
     summit's: a hatched pair killed an armed new-game Avatar in 5 of 10
     fights, docs/playtest-2026-10-18-armed-harpie-pair.md) — each wave's
     trigger box wholly north of (past) the last wave's monsters, the way
     the player walks;
  9. build_map_13.HARPIE_REST, between the lane harpies and the summit's,
     is a spot the Avatar walks to and stands on, fires no trigger, and
     lies outside every egg's seek square (lv_monster_eggs.seek_square:
     a monster on its egg there would not wake to him), so resting there
     heals; at least two harpie waves lie south of it (the climb's lanes)
     and at least one north of it (the summit);
 10. the Map 11 hub holds a retail weapon whose damage type carries
     DMG_BLUNT, the bit a golem's 0x8A defense leaves: carryable, drawn,
     on clear floor with nothing tall to sort against, and walked to.

Douglas's decision of 2026-10-24 (playtest-2026-10-17-replay-leg3 finding
4, rats hatched across the one way into Map 11's south half):

 11. no Map 11 MONEGG trigger box covers SOUTH_PASSAGE (the corridor's
     last 512 and 512 out of its mouth), and each lies more than
     ROUTE_WANDER off the straight line between any two of the south
     half's ends: the corridor's mouth, the Fire doorway, the Water
     talisman and the pillars chamber's doorway.

Maps 8 and 39 carry retail eggs only (FIXED.DAT, 19 and 3; Map 8's are
hatched by retail triggers in U8SAVE.000's NONFIXED.DAT, Map 39's by none):

 12. their monster eggs and MONEGG triggers are the pristine base's,
     byte for byte.

    python3 agents/map-populator/src/test_monster_eggs.py

Plain script: exit 0 on pass, 1 on fail.
"""

import heapq
import math
import os
import sys

import numpy as np

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_map import MapArchive, MapItem                    # noqa: E402
from parse_typeflag import load_typeflag                   # noqa: E402
from map_preview import GlobReader, expand_globs           # noqa: E402
from base_input import pristine_base                       # noqa: E402
from exact_reach import (ExactReach, AVATAR_BODY, HURT_SHAPES_U8,  # noqa: E402
                         SI_SOLID, SI_SEA, SI_LAND, SI_DAMAGING, SI_ROOF_F1,
                         FLG_CONTAINED, FLG_EQUIPPED, FLG_FLIPPED,
                         Z_SEARCH_OFFSETS_U8)
from lv_monster_eggs import (MONEGG_RANGE, HATCH_Z,        # noqa: E402
                             ACTIVITY_COMBAT, SEEK_RANGE, seek_square,
                             FAST_DIMS, MAP_CHUNK, fast_chunks, hatch_cameras,
                             hatch_fast_problem)
from lv_tiny_avatar_art import decode_anim                 # noqa: E402

FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
TYPEFLAG = os.path.join(BASE_DIR, 'shared', 'build', 'TYPEFLAG.DAT')
ANIM = os.path.join(BASE_DIR, 'shared', 'build', 'ANIM.DAT')
BASE_FIXED = os.path.join(BASE_DIR, 'shared', 'data', 'u8-install', 'STATIC',
                          'FIXED.DAT')

# LV maps, and where a player arrives on each (the teleport targets the
# quest uses: test_route_reach's seeds).
ARRIVAL = {9: (13696, 14208, 0), 10: (12800, 2560, 0), 11: (9728, 1792, 0),
           13: (4096, 11776, 0), 17: (4608, 9984, 0), 18: (3072, 1792, 0)}
RETAIL_MAPS = (8, 39)
MONSTER_EGG = MapItem.SHAPE_MONSTER_EGG
UNK_EGG = MapItem.SHAPE_STANDARD_EGG
MONEGG_QUALITY = MapItem.MONEGG_QUALITY
HURT_MARGIN = 32
EDGE = 32
MIN_HATCH_GAP = 400
FLOOD_STEP = 32
FIGHT_ZONE = SEEK_RANGE        # how far round a trigger or egg a fight goes

# Douglas, 2026-10-11: the Lake's zombies come in waves (2, 1, 2), all
# one-shot; 2026-10-24: the climb's harpies one at a time (1, 1);
# 2026-10-30: the summit's too (1, 1). (map, monster shape, least waves,
# most monsters in a wave)
WAVES = ((10, 872, 3, 2), (13, 873, 4, 1))

# The Map 11 hub, build_map_11.build_central_hub: x0, y0 = 8192, 4096,
# 3072 square, as (x_lo_excl, y_lo_excl, x_hi, y_hi).
HUB = (8192, 4096, 11264, 7168)
# The one way into Map 11's south half (playtest-2026-10-17-replay-leg3
# finding 4: group 4's trigger across its mouth hatched rats on every
# player). build_map_11.build_corridors runs the hub-to-water corridor
# y 7168-14336 between flanks at x 9472 and 10016, so a 64-wide body's
# reference x is 9536-9984 (the flood's own span, checked below); its
# mouth opens into the Water section at y 14400, where the section's
# north wall (y 14336) ends under the body. The box is the corridor's
# last 512 and 512 straight on out of the mouth, as Avatar reference
# points (x_lo, y_lo, x_hi, y_hi), inclusive.
SOUTH_PASSAGE = (9536, 13888, 9984, 14911)
# The quest's ends in the south half, Avatar reference points at z 0: the
# corridor's mouth, the Fire doorway (the Water section's west wall,
# y (16384, 16896]), the Water talisman (a pin) and the Four Pillars
# chamber's north doorway (x (8448, 8704] on the y 19455/19456 seam). A
# player walks between any two; ROUTE_WANDER is how far off the straight
# line his walk is allowed to stray (a chunk).
SOUTH_HALF_ENDS = {'the corridor mouth': (9760, 14400),
                   'the Fire doorway': (6208, 16672),
                   'the Water talisman': (12799, 18943),
                   "the pillars chamber's doorway": (8608, 19456)}
ROUTE_WANDER = 512
# Retail weapons, shape -> damage_type, from the engine's u8weapons.ini
# (ultima8.dat; checked against it below when the file is here).
WEAPON_DAMAGE = {0x021C: 0x04, 0x021D: 0x02, 0x021E: 0x02, 0x01A4: 0x02,
                 0x01A3: 0x06, 0x01A2: 0x02, 0x01A1: 0x04, 0x032F: 0x24,
                 0x0336: 0x26, 0x0330: 0x64, 0x0335: 0x32, 0x0334: 0x22,
                 0x0333: 0x22, 0x0332: 0x22, 0x0331: 0x2A}
DMG_BLUNT = 0x04                       # WeaponInfo::DMG_BLUNT

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


if not (os.path.exists(FIXED) and os.path.exists(TYPEFLAG)):
    print('shared/build/FIXED.DAT or TYPEFLAG.DAT missing: run '
          'tools/build_artifacts.sh first')
    sys.exit(1)

shapes = load_typeflag(TYPEFLAG)
arch = MapArchive(FIXED)
gr = GlobReader()


def body_of(shape):
    si = shapes[shape]
    return si.footpad_x * 32, si.footpad_y * 32, si.footpad_z * 8


def boxes(items):
    """Every placed item, globs expanded, as rows of (x, y, z, xd, yd, zd,
    shape, flags0, flags1)."""
    out = []
    for it in expand_globs(items, gr):
        if it.flags & (FLG_CONTAINED | FLG_EQUIPPED):
            continue
        if not 0 <= it.shape < len(shapes):
            continue
        si = shapes[it.shape]
        xd, yd = si.footpad_x * 32, si.footpad_y * 32
        if it.flags & FLG_FLIPPED:
            xd, yd = yd, xd
        out.append((it.x, it.y, it.z & 0xFF, xd, yd, si.footpad_z * 8,
                    it.shape, si.flags0, si.flags1))
    return np.array(out, dtype=np.int64)


def stands(bx, x, y, z, body):
    """getPositionInfo for a body at max corner (x, y, z), plus dry and
    unburnt. Returns '' if it stands, else why not."""
    X, Y, Z, XD, YD, ZD, S, F0, F1 = bx.T
    w, d, h = body
    ovxy = (X - XD < x) & (x - w < X) & (Y - YD < y) & (y - d < Y)
    blk = ovxy & ((F0 & SI_SOLID) > 0) & (Z < z + h) & (Z + ZD > z) & \
        (XD > 0) & (YD > 0)
    if blk.any():
        return f'inside shape {sorted(set(S[blk].tolist()))}'
    sup = ovxy & (((F0 & (SI_SOLID | SI_LAND)) > 0) |
                  ((F1 & SI_ROOF_F1) > 0)) & (Z + ZD <= z)
    top = int((Z + ZD)[sup].max()) if sup.any() else None
    if top != z and not z <= 0:
        return f'unsupported (highest top under it {top})'
    sea = ovxy & ((F0 & SI_SEA) > 0) & (Z + ZD == z)
    if sea.any():
        return f'on water (shape {sorted(set(S[sea].tolist()))})'
    mx, my = x - w // 2, y - d // 2
    land = (X - XD < mx) & (mx <= X) & (Y - YD < my) & (my <= Y) & \
        (Z + ZD <= z) & (((F0 & SI_LAND) > 0) | ((F1 & SI_ROOF_F1) > 0))
    if not land.any() or int((Z + ZD)[land].max()) + 8 < z:
        return 'no land under its centre'
    m = HURT_MARGIN
    hurt = (X - XD - m <= x) & (x - w <= X + m) & (Y - YD - m <= y) & \
        (y - d <= Y + m) & (Z <= z + h) & (Z + ZD >= z) & \
        (np.isin(S, HURT_SHAPES_U8) | ((F0 & SI_DAMAGING) > 0))
    if hurt.any():
        return f'within {m} of burning shape {sorted(set(S[hurt].tolist()))}'
    return ''


DRY_ITEMS = {}


def dry_flood(mapnum, items):
    """The Avatar's walk from the arrival pad, water left out (a SEA tile
    is no floor to him: it drowns). DRY_ITEMS keeps the item list for the
    monsters' own floods (the walk-distance check)."""
    dry = DRY_ITEMS[mapnum] = [
        it for it in expand_globs(items, gr)
        if not (0 <= it.shape < len(shapes)
                and shapes[it.shape].flags0 & SI_SEA)]
    xs = [it.x for it in items if it.x > 64]
    ys = [it.y for it in items if it.y > 64]
    roi = (min(xs) - 128, min(ys) - 128, max(xs) + 128, max(ys) + 128)
    er = ExactReach(dry, shapes, roi, step=FLOOD_STEP, glob_reader=gr)
    reach, _ = er.flood([ARRIVAL[mapnum]])
    return er, reach


def reached(er, reach, x0, x1, y0, y1, zlo, zhi):
    """A flood position with x0 <= x < x1, y0 <= y < y1, zlo < z <= zhi?"""
    i0, i1 = er._kx(x0 - 1, x1)
    j0, j1 = er._ky(y0 - 1, y1)
    if i0 > i1 or j0 > j1:
        return None
    for L, r in reach.items():
        if zlo < L <= zhi and r[i0:i1 + 1, j0:j1 + 1].any():
            return L
    return None


def is_trigger(it):
    return it.shape == UNK_EGG and it.quality == MONEGG_QUALITY


print('=' * 70)
print('LV monster eggs: hatched by a trigger, on their feet, fighting')
trig_xd = shapes[UNK_EGG].footpad_x * 32
trig_yd = shapes[UNK_EGG].footpad_y * 32
total_eggs = 0
FLOODS = {}
for mapnum in sorted(ARRIVAL):
    items = arch.get_map_items(mapnum)
    eggs = [it for it in items if it.shape == MONSTER_EGG]
    trigs = [it for it in items if is_trigger(it)]
    total_eggs += len(eggs)
    if not eggs and not trigs:
        continue
    print(f'--- Map {mapnum}: {len(eggs)} eggs, {len(trigs)} triggers')
    bx = boxes(items)
    er, reach = dry_flood(mapnum, items)
    FLOODS[mapnum] = (bx, er, reach)

    def reaches(t, e):
        return (t.x - trig_xd - MONEGG_RANGE <= e.x <= t.x + MONEGG_RANGE
                and t.y - trig_yd - MONEGG_RANGE <= e.y <= t.y + MONEGG_RANGE)

    for e in eggs:
        mon = e.quality & 0x7FF
        tag = f'map {mapnum} egg {mon} at ({e.x},{e.y},{e.z})'
        check(f'{tag}: combat activity', e.mapnum & 0x07 == ACTIVITY_COMBAT,
              f'activity {e.mapnum & 0x07}')
        group = e.mapnum >> 3
        hatchers = [t for t in trigs
                    if t.mapnum & 0x1F == group and reaches(t, e)]
        check(f'{tag}: a MONEGG trigger of group {group} reaches it',
              hatchers, f'triggers here: '
              f'{[(t.x, t.y, t.mapnum & 0x1F) for t in trigs]}')
        body = body_of(mon)
        why = stands(bx, e.x, e.y, e.z, body)
        edge = [(dx, dy) for dx in (-EDGE, 0, EDGE) for dy in (-EDGE, 0, EDGE)
                if (dx or dy) and stands(bx, e.x + dx, e.y + dy, e.z, body)]
        check(f'{tag}: its {body[0]}x{body[1]} body stands there, dry, '
              f'unburnt, {EDGE} from any edge', not why and not edge,
              why or f'fails {EDGE} off toward {edge}')
        w, d, _ = body
        cx, cy = e.x - w // 2, e.y - d // 2
        L = reached(er, reach, cx - 64, cx + 64 + 64, cy - 64, cy + 64 + 64,
                    e.z - 8 - 1, e.z + 8)
        check(f'{tag}: the Avatar can walk to it from the arrival pad',
              L is not None)

    groups = {}
    for t in trigs:
        groups.setdefault(t.mapnum & 0x1F, []).append(t)
    for t in trigs:
        g = t.mapnum & 0x1F
        xr, yr = (t.npcnum >> 4) & 0xF, t.npcnum & 0xF
        tag = f'map {mapnum} trigger group {g} at ({t.x},{t.y},{t.z})'
        mine = [e for e in eggs if e.mapnum >> 3 == g and reaches(t, e)]
        check(f'{tag}: hatches {len(mine)} egg(s), the only trigger of its '
              f'group', mine and len(groups[g]) == 1,
              f'{len(groups[g])} triggers of group {g}')
        bw, bd, _ = AVATAR_BODY
        L = reached(er, reach, t.x - 32 * xr, t.x + 32 * xr + bw,
                    t.y - 32 * yr, t.y + 32 * yr + bd,
                    t.z - HATCH_Z, t.z + HATCH_Z) if xr and yr else None
        check(f'{tag}: its +/-{32 * xr}x{32 * yr} box is walked into from '
              f'the arrival pad', L is not None)
        if mine:
            gap = min(max(abs(e.x - t.x), abs(e.y - t.y)) for e in mine)
            check(f'{tag}: nearest egg {gap} away (>= {MIN_HATCH_GAP})',
                  gap >= MIN_HATCH_GAP)

check('the LV maps carry monster eggs at all', total_eggs > 0)


def box_reached(er, reach, t):
    """[(x, y, z)]: the flood positions inside trigger t's hatch box."""
    xr, yr = (t.npcnum >> 4) & 0xF, t.npcnum & 0xF
    bw, bd, _ = AVATAR_BODY
    i0, i1 = er._kx(t.x - 32 * xr - 1, t.x + 32 * xr + bw)
    j0, j1 = er._ky(t.y - 32 * yr - 1, t.y + 32 * yr + bd)
    return [(er.x_of(i), er.y_of(j), L) for L, r in reach.items()
            if t.z - HATCH_Z < L <= t.z + HATCH_Z
            for i in range(i0, i1 + 1) for j in range(j0, j1 + 1) if r[i, j]]


def hatchers_of(e, trigs):
    return [t for t in trigs if t.mapnum & 0x1F == e.mapnum >> 3 and
            t.x - trig_xd - MONEGG_RANGE <= e.x <= t.x + MONEGG_RANGE and
            t.y - trig_yd - MONEGG_RANGE <= e.y <= t.y + MONEGG_RANGE]


print('--- One-shot (playtest-2026-10-11-monsters2 finding 3)')
LV_EGGS = {m: [it for it in arch.get_map_items(m) if it.shape == MONSTER_EGG]
           for m in sorted(ARRIVAL)}
rehatch = [(m, e.x, e.y, e.frame) for m, es in LV_EGGS.items() for e in es
           if e.frame != 1]
check(f'all {sum(map(len, LV_EGGS.values()))} LV eggs are frame 1 (MONEGG '
      f'destroys a hatched egg whose frame is not 0), so a doorway walked '
      f'through again hatches nothing on top of the last hatch',
      not rehatch, f'frame-0 eggs: {rehatch}')

print(f'--- The fast area at {FAST_DIMS[0]}x{FAST_DIMS[1]} (finding 1): a '
      f'combat monster hatched outside it arrives passive')
# The mirror (lv_monster_eggs.fast_chunks) against the run that found it:
# lv_run.log of playtest-2026-10-11-monsters2 dumped each hatchling right
# after its hatch, item flag 0x2000 (FLG_FASTAREA) set or not. (map,
# trigger, box, egg, fast): fast means inside from every position in the
# box, not fast means outside from all of them.
CALIBRATION = (
    (11, (5888, 5376, 0), (2, 9), (3040, 2048), False),   # golem 125, 0xc2
    (11, (5888, 5376, 0), (2, 9), (2688, 2496), False),   # golem 126, 0xc2
    (11, (5888, 5376, 0), (2, 9), (4608, 2048), False),   # golem 127, 0xc2
    (11, (5888, 5376, 0), (2, 9), (5376, 2720), False),   # golem 128, 0xc2
    (9, (14208, 13952, 0), (5, 5), (14720, 13408), True),  # troll, 0x20e2
    (13, (4096, 3584, 92), (6, 2), (4032, 2688), True),    # harpie, 0x20e2
    (13, (4096, 3584, 92), (6, 2), (4160, 3072), True))    # harpie, 0x20c2
for mapnum, (tx, ty, tz), (xr, yr), (ex, ey), fast in CALIBRATION:
    sets = [fast_chunks(*c) for c in hatch_cameras((tx, ty), xr, yr, [tz])]
    own = (ex // MAP_CHUNK, ey // MAP_CHUNK)
    got = own in set.intersection(*sets) if fast else \
        own not in set.union(*sets)
    check(f'mirror: map {mapnum} egg ({ex},{ey}) from the trigger at '
          f'({tx},{ty}) is {"inside" if fast else "outside"} the fast area, '
          f'as the 2026-10-11 log showed', got)
for mapnum in sorted(ARRIVAL):
    if not LV_EGGS[mapnum]:
        continue
    bx, er, reach = FLOODS[mapnum]
    trigs = [it for it in arch.get_map_items(mapnum) if is_trigger(it)]
    for e in LV_EGGS[mapnum]:
        mon = e.quality & 0x7FF
        for t in hatchers_of(e, trigs):
            xr, yr = (t.npcnum >> 4) & 0xF, t.npcnum & 0xF
            zs = sorted({z for _, _, z in box_reached(er, reach, t)}) or [t.z]
            why = hatch_fast_problem((t.x, t.y), xr, yr, zs, (e.x, e.y),
                                     body_of(mon))
            check(f'map {mapnum} egg {mon} at ({e.x},{e.y}) hatched from '
                  f'({t.x},{t.y}) at z {zs}: inside the fast area, and so '
                  f'are its loiter steps unless it sees the Avatar at once',
                  not why, why)

print('--- Knockback (finding 2): no blow knocks the Avatar into water or '
      'onto a burning shape where he fights')
# A blow plays the victim's stumbleBackwards (Actor::receiveHitU8), a run of
# ANIM.DAT frames each moving 4 * Direction_X/YFactor * deltaDir. Every
# frame is ONGROUND, so AnimationTracker::step takes it if the spot is
# valid and supported, else the first of scanForValidPosition's z offsets
# that is, else an unblocked unsupported one (and he falls), else it stops
# the stumble. A pier 8 over the water is one such offset: that is how the
# Avatar went in off the 256-wide pier (CLRWATER's gotHit drowned him).
STUMBLE = 13                                    # Animation::stumbleBackwards
DIR_X = (0, 1, 1, 1, 0, -1, -1, -1)             # Direction_XFactor, U8
DIR_Y = (-1, -1, 0, 1, 1, 1, 0, -1)             # Direction_YFactor, U8
SCAN_Z = (0, -4, 4, -8, 8)                      # SEARCH_OFFSETS_U8
_anim = decode_anim(open(ANIM, 'rb').read(), 1)[STUMBLE][3]
STUMBLE_STEPS = [[(4 * DIR_X[d] * f[3], 4 * DIR_Y[d] * f[3]) for f in fr
                  if f[3]] for d, fr in enumerate(_anim)]
KNOCKBACK = max(max(abs(sum(s[0] for s in st)), abs(sum(s[1] for s in st)))
                for st in STUMBLE_STEPS)
print(f'  (the Avatar\'s stumble carries him up to {KNOCKBACK} units, ANIM.DAT '
      f'shape 1 action {STUMBLE})')
check('the stumble moves him at all (else this check proves nothing)',
      KNOCKBACK > 0)


def stance(B, x, y, z, body):
    """getPositionInfo for a body at (x, y, z): (valid, supported, what is
    fatal there: a SEA top at z under it, or a burning shape it touches)."""
    X, Y, Z, XD, YD, ZD, S, F0, F1 = B.T
    w, d, h = body
    ovxy = (X - XD < x) & (x - w < X) & (Y - YD < y) & (y - d < Y)
    if (ovxy & ((F0 & SI_SOLID) > 0) & (Z < z + h) & (Z + ZD > z) &
            (XD > 0) & (YD > 0)).any():
        return False, False, ''
    sup = ovxy & (((F0 & (SI_SOLID | SI_LAND)) > 0) |
                  ((F1 & SI_ROOF_F1) > 0)) & (Z + ZD <= z)
    top = int((Z + ZD)[sup].max()) if sup.any() else None
    mx, my = x - w // 2, y - d // 2
    land = (X - XD < mx) & (mx <= X) & (Y - YD < my) & (my <= Y) & \
        (Z + ZD <= z) & (((F0 & SI_LAND) > 0) | ((F1 & SI_ROOF_F1) > 0))
    landz = int((Z + ZD)[land].max()) if land.any() else None
    supported = z <= 0 or (top == z and landz is not None and landz + 8 >= z)
    fatal = ''
    if (ovxy & ((F0 & SI_SEA) > 0) & (Z + ZD == z)).any():
        fatal = 'in water'
    elif (ovxy & (Z <= z + h) & (Z + ZD >= z) &
          (np.isin(S, HURT_SHAPES_U8) | ((F0 & SI_DAMAGING) > 0))).any():
        fatal = 'burning'
    return True, supported, fatal


def knocked_in(bx, x, y, z, body=AVATAR_BODY):
    """'' if no stumble from (x, y, z), in any of the 8 directions, ends
    him in water or fire or drops him off; else where it does."""
    X, Y = bx[:, 0], bx[:, 1]
    B = bx[(X > x - 256) & (X - bx[:, 3] < x + 256) &
           (Y > y - 256) & (Y - bx[:, 4] < y + 256)]
    for d in range(8):
        px, py, pz = x, y, z
        for dx, dy in STUMBLE_STEPS[d]:
            nx, ny = px + dx, py + dy
            took = loose = None
            for vz in SCAN_Z:
                valid, supported, fatal = stance(B, nx, ny, pz + vz, body)
                if valid and supported:
                    took = (pz + vz, fatal)
                    break
                if valid and loose is None:
                    loose = pz + vz
            if took is None:
                if loose is None:
                    break                    # blocked: the stumble stops
                return f'dir {d}: off the edge at ({nx},{ny},{loose})'
            pz, fatal = took
            px, py = nx, ny
            if fatal:
                return f'dir {d}: {fatal} at ({px},{py},{pz})'
    return ''


for mapnum in sorted(ARRIVAL):
    if not LV_EGGS[mapnum]:
        continue
    bx, er, reach = FLOODS[mapnum]
    for t in (it for it in arch.get_map_items(mapnum) if is_trigger(it)):
        spots = box_reached(er, reach, t)
        bad = [(p, w) for p in spots for w in [knocked_in(bx, *p)] if w]
        check(f'map {mapnum} trigger ({t.x},{t.y},{t.z}): no stumble from '
              f'any of the {len(spots)} spots in its box ends in water or '
              f'fire or over an edge', spots and not bad,
              f'{len(bad)} do, e.g. {bad[:2]}')
    for e in LV_EGGS[mapnum]:
        i0, i1 = er._kx(e.x - KNOCKBACK - 1, e.x + KNOCKBACK + 1)
        j0, j1 = er._ky(e.y - KNOCKBACK - 1, e.y + KNOCKBACK + 1)
        spots = [(er.x_of(i), er.y_of(j), L) for L, r in reach.items()
                 if e.z - 8 <= L <= e.z + 8
                 for i in range(i0, i1 + 1) for j in range(j0, j1 + 1)
                 if r[i, j]]
        bad = [(p, w) for p in spots for w in [knocked_in(bx, *p)] if w]
        check(f'map {mapnum} egg {e.quality & 0x7FF} at ({e.x},{e.y},{e.z}):'
              f' no stumble from the {len(spots)} spots within {KNOCKBACK} '
              f'of it ends in water or fire or over an edge', not bad,
              f'{len(bad)} do, e.g. {bad[:2]}')

print(f'--- The fight drifts (playtest-2026-10-12-monsters3 finding 2): no '
      f'water within {FIGHT_ZONE} of a trigger or an egg to be stood on or '
      f'knocked into')
# The rails held on the pier, and the fight walked off its open foot onto
# the shore: the Avatar drowned there twice, once on a plain walk-in, and
# three zombies. Drowning is the one hazard that kills outright, so every
# spot the Avatar walks to within FIGHT_ZONE (the seek range: as far as a
# woken monster comes for him) of a trigger's box or an egg must be off
# the water (CLRWATER's gotHit drowns what Item::isOn it: footprints
# overlapping, the water's top at his z), and no stumble from it may end
# on the water. Only spots a stumble could take to water are simulated.


def sea_near(bx, spots, reach_xy):
    """The spots with a SEA top within 8 of their z inside their own box
    grown by reach_xy."""
    X, Y, Z, XD, YD, ZD, S, F0, F1 = bx.T
    sea = (F0 & SI_SEA) > 0
    SX, SY, SXD, SYD, ST = X[sea], Y[sea], XD[sea], YD[sea], (Z + ZD)[sea]
    w, d, _ = AVATAR_BODY
    return [p for p in spots
            if ((SX - SXD < p[0] + reach_xy) & (p[0] - w - reach_xy < SX) &
                (SY - SYD < p[1] + reach_xy) & (p[1] - d - reach_xy < SY) &
                (abs(ST - p[2]) <= 8)).any()]


for mapnum in sorted(ARRIVAL):
    if not LV_EGGS[mapnum]:
        continue
    bx, er, reach = FLOODS[mapnum]
    trigs = [it for it in arch.get_map_items(mapnum) if is_trigger(it)]
    places = [(f'trigger ({t.x},{t.y},{t.z})', t.x - 32 * ((t.npcnum >> 4) & 15),
               t.y - 32 * (t.npcnum & 15),
               t.x + 32 * ((t.npcnum >> 4) & 15) + AVATAR_BODY[0] - 1,
               t.y + 32 * (t.npcnum & 15) + AVATAR_BODY[1] - 1, t.z)
              for t in trigs] + \
             [(f'egg {e.quality & 0x7FF} at ({e.x},{e.y},{e.z})', e.x, e.y,
               e.x, e.y, e.z) for e in LV_EGGS[mapnum]]
    verdict = {}
    for what, x0, y0, x1, y1, z in places:
        i0, i1 = er._kx(x0 - FIGHT_ZONE - 1, x1 + FIGHT_ZONE + 1)
        j0, j1 = er._ky(y0 - FIGHT_ZONE - 1, y1 + FIGHT_ZONE + 1)
        spots = [(er.x_of(i), er.y_of(j), L) for L, r in reach.items()
                 if abs(L - z) <= HATCH_Z
                 for i in range(i0, i1 + 1) for j in range(j0, j1 + 1)
                 if r[i, j]]
        wet = sea_near(bx, spots, KNOCKBACK)
        for p in wet:
            if p not in verdict:
                X, Y = bx[:, 0], bx[:, 1]
                B = bx[(X > p[0] - 256) & (X - bx[:, 3] < p[0] + 256) &
                       (Y > p[1] - 256) & (Y - bx[:, 4] < p[1] + 256)]
                _, _, fatal = stance(B, *p, AVATAR_BODY)
                verdict[p] = (f'stands {fatal}' if fatal == 'in water' else
                              knocked_in(bx, *p))
        bad = [(p, verdict[p]) for p in wet if verdict[p]]
        check(f'map {mapnum} {what}: of the {len(spots)} spots within '
              f'{FIGHT_ZONE}, the {len(wet)} by water are off it and no '
              f'stumble from them ends in it', not bad,
              f'{len(bad)} are not, e.g. {bad[:3]}')

print('--- The monster can walk to him (playtest-2026-10-12-monsters3 '
      'finding 1)')
# Golems 1 and 7 hatched fighting behind a wall from their triggers, and
# milled there; golem 1 never reached the Avatar. The seek square and the
# fast area measure straight lines, so this measures the walk: for every
# spot the Avatar can stand in a trigger's box, the monster's shortest
# walk from its egg, with its own body (ExactReach lattice, 8-way, a
# step up or down of 4 or 8 as scanForValidPosition allows), to where its
# box comes within 32 of his, against the straight line from its egg to
# the nearest such place. A wall between them makes the walk the long way
# round; a stone in the way, a sidestep of about a body. So the walk may
# be 1.3 times the line, and never less than WALK_SLACK over it.
WALK_RATIO = 1.3
WALK_SLACK = 256
_STEPS8 = ((1, 0), (-1, 0), (0, 1), (0, -1),
           (1, 1), (1, -1), (-1, 1), (-1, -1))


def walk_from(mer, start, window):
    """Dijkstra over the monster's ExactReach lattice from `start` (x, y, z)
    inside window (x0, y0, x1, y1): {(level, i, j): distance}."""
    i0, i1 = mer._kx(window[0] - 1, window[2] + 1)
    j0, j1 = mer._ky(window[1] - 1, window[3] + 1)
    si, sj = mer.index_of(start[0], start[1])
    seed = next(((L, si + di, sj + dj) for L in mer.levels
                 if abs(L - start[2]) <= 8
                 for di in (0, -1, 1) for dj in (0, -1, 1)
                 if mer.mask(L)[si + di, sj + dj]), None)
    if seed is None:
        return {}
    levels = set(mer.levels)
    dz_ok = [0] + [d for d in Z_SEARCH_OFFSETS_U8 if d]
    s, diag = mer.step, mer.step * math.sqrt(2)
    dist, todo = {seed: 0.0}, [(0.0, seed)]
    while todo:
        dd, (L, i, j) = heapq.heappop(todo)
        if dist[(L, i, j)] < dd:
            continue
        m = mer.mask(L)
        for di, dj in _STEPS8:
            ni, nj = i + di, j + dj
            if not (i0 <= ni <= i1 and j0 <= nj <= j1):
                continue
            for dz in dz_ok:
                L2 = L + dz
                if L2 not in levels:
                    continue
                m2 = mer.mask(L2)
                if not m2[ni, nj]:
                    continue
                if di and dj and not ((m[i + di, j] or m2[i + di, j]) and
                                      (m[i, j + dj] or m2[i, j + dj])):
                    continue                        # no corner cutting
                nd, k = dd + (diag if di and dj else s), (L2, ni, nj)
                if nd < dist.get(k, 1e18):
                    dist[k] = nd
                    heapq.heappush(todo, (nd, k))
    return dist


def touching(mer, px, py, mon_body):
    """Lattice cells (i, j) where a monster body's box comes within 32 of
    the Avatar's at (px, py) on x and on y."""
    mxd, myd, _ = mon_body
    i0, i1 = mer._kx(px - AVATAR_BODY[0] - 33, px + 33 + mxd)
    j0, j1 = mer._ky(py - AVATAR_BODY[1] - 33, py + 33 + myd)
    return [(i, j) for i in range(i0, i1 + 1) for j in range(j0, j1 + 1)]


MON_REACH = {}
for mapnum in sorted(ARRIVAL):
    if not LV_EGGS[mapnum]:
        continue
    bx, er, reach = FLOODS[mapnum]
    trigs = [it for it in arch.get_map_items(mapnum) if is_trigger(it)]
    for e in LV_EGGS[mapnum]:
        mon = e.quality & 0x7FF
        if (mapnum, mon) not in MON_REACH:
            MON_REACH[(mapnum, mon)] = ExactReach(
                DRY_ITEMS[mapnum], shapes, er.roi, body=body_of(mon),
                step=FLOOD_STEP, glob_reader=gr)
        mer = MON_REACH[(mapnum, mon)]
        ei, ej = mer.index_of(e.x, e.y)
        ex, ey = mer.x_of(ei), mer.y_of(ej)
        for t in hatchers_of(e, trigs):
            spots = box_reached(er, reach, t)
            xs = [p[0] for p in spots] + [e.x]
            ys = [p[1] for p in spots] + [e.y]
            dist = walk_from(mer, (e.x, e.y, e.z),
                             (min(xs) - 1024, min(ys) - 1024,
                              max(xs) + 1024, max(ys) + 1024))
            at = {}
            for (L, i, j), dd in dist.items():
                at.setdefault((i, j), []).append((L, dd))
            worst = None
            for px, py, pz in spots:
                walk = line = None
                for i, j in touching(mer, px, py, body_of(mon)):
                    for L, dd in at.get((i, j), ()):
                        if abs(L - pz) > 8:
                            continue
                        ln = math.hypot(mer.x_of(i) - ex, mer.y_of(j) - ey)
                        walk = dd if walk is None else min(walk, dd)
                        line = ln if line is None else min(line, ln)
                over = (float('inf') if walk is None else
                        walk - max(WALK_RATIO * line, line + WALK_SLACK))
                if worst is None or over > worst[0]:
                    worst = (over, (px, py, pz), walk, line)
            check(f'map {mapnum} egg {mon} at ({e.x},{e.y}) from the trigger '
                  f'at ({t.x},{t.y}): from each of the {len(spots)} spots '
                  f'in its box the monster walks to him within '
                  f'{WALK_RATIO} x the line (or {WALK_SLACK} over it)',
                  spots and worst[0] <= 0,
                  f'from {worst[1]}: walk {worst[2] and round(worst[2])}, '
                  f'line {worst[3] and round(worst[3])}' if worst else
                  'no spot in the box')


def hatches_at(t, x, y, z):
    """EggHatcherProcess::run: does the Avatar at (x, y, z) fire `t`?"""
    xr, yr = (t.npcnum >> 4) & 0xF, t.npcnum & 0xF
    bw, bd, _ = AVATAR_BODY
    return (t.x - 32 * xr <= x and x - bw < t.x + 32 * xr and
            t.y - 32 * yr <= y and y - bd < t.y + 32 * yr and
            t.z - HATCH_Z < z <= t.z + HATCH_Z)


print('--- Waves (Douglas 2026-10-11, 2026-10-24, 2026-10-30): one-shot, '
      'a few at a time, each wave waking only past the last')
for mapnum, mon, min_waves, max_wave in WAVES:
    items = arch.get_map_items(mapnum)
    eggs = [it for it in items
            if it.shape == MONSTER_EGG and it.quality & 0x7FF == mon]
    trigs = {it.mapnum & 0x1F: it for it in items if is_trigger(it)}
    tag = f'map {mapnum} monster {mon}'
    check(f'{tag}: every egg is one-shot (frame 1: MONEGG destroys a '
          f'hatched egg whose frame is not 0)',
          eggs and all(e.frame == 1 for e in eggs),
          f'frames {sorted(e.frame for e in eggs)}')
    waves = {}
    for e in eggs:
        waves.setdefault(e.mapnum >> 3, []).append(e)
    check(f'{tag}: {len(eggs)} eggs in {len(waves)} waves (>= {min_waves}), '
          f'none of more than {max_wave}',
          len(waves) >= min_waves and
          all(len(w) <= max_wave for w in waves.values()),
          f'wave sizes {sorted(len(w) for w in waves.values())}')
    # The way runs north (y falls): order the waves by their triggers.
    order = sorted((g for g in waves if g in trigs),
                   key=lambda g: -trigs[g].y)
    for prev, nxt in zip(order, order[1:]):
        t = trigs[nxt]
        box_south = t.y + 32 * (t.npcnum & 0xF) + AVATAR_BODY[1]
        last = min(e.y - body_of(mon)[1] for e in waves[prev])
        check(f'{tag}: wave {nxt}\'s trigger (y {t.y}) lies wholly north of '
              f'wave {prev}\'s monsters, so it wakes only past them',
              box_south <= last, f'box reaches y {box_south}, monsters '
              f'from y {last}')

print('--- Map 13: a rest point between the lane harpies and the summit\'s')
import build_map_13                                        # noqa: E402
rest = getattr(build_map_13, 'HARPIE_REST', None)
check('build_map_13.HARPIE_REST is defined', rest is not None)
if rest is not None:
    rx, ry, rz = rest
    bx, er, reach = FLOODS[13]
    items = arch.get_map_items(13)
    check(f'the Avatar stands at the rest point {rest}, dry and unburnt',
          not stands(bx, rx, ry, rz, AVATAR_BODY),
          stands(bx, rx, ry, rz, AVATAR_BODY))
    check('the rest point is walked to from the arrival pad',
          reached(er, reach, rx - 31, rx + 1, ry - 31, ry + 1,
                  rz - 1, rz) is not None)
    fired = [(t.x, t.y) for t in items
             if is_trigger(t) and hatches_at(t, rx, ry, rz)]
    check('standing there fires no MONEGG trigger', not fired, str(fired))
    bw, bd, _ = AVATAR_BODY
    woken = []
    for e in items:
        if e.shape != MONSTER_EGG:
            continue
        x0, x1, y0, y1 = seek_square(e.x, e.y, body_of(e.quality & 0x7FF))
        # Anywhere in the Avatar's own box, not just his reference point.
        if x0 < rx and rx - bw < x1 and y0 < ry and ry - bd < y1:
            woken.append((e.x, e.y))
    check(f'no monster standing on its egg wakes to him there (no seek '
          f'square, {SEEK_RANGE} round the egg, meets his box)',
          not woken, str(woken))
    harp = [t.y for t in items if is_trigger(t) and any(
        e.shape == MONSTER_EGG and e.quality & 0x7FF == 873 and
        e.mapnum >> 3 == t.mapnum & 0x1F for e in items)]
    south = sorted(y for y in harp if y > ry)
    north = sorted(y for y in harp if y < ry)
    check('the rest point lies on the climb between the lane harpies\' '
          'waves (at least two south of it) and the summit\'s (at least one '
          'north of it)', len(south) >= 2 and north,
          f'harpie triggers at y {sorted(harp)}, rest at y {ry}')

print('--- Map 11: a blunt weapon at the hub')
weapons = [it for it in arch.get_map_items(11)
           if it.shape in WEAPON_DAMAGE and not it.flags & FLG_CONTAINED
           and HUB[0] < it.x <= HUB[2] and HUB[1] < it.y <= HUB[3]]
blunt = [it for it in weapons if WEAPON_DAMAGE[it.shape] & DMG_BLUNT]
check('the hub holds a weapon whose damage type carries DMG_BLUNT (0x04), '
      'which a golem\'s defense 0x8A does not strip', blunt,
      f'weapons there: {[(i.shape, i.x, i.y) for i in weapons]}')
bx, er, reach = FLOODS[11]
for it in blunt:
    si = shapes[it.shape]
    w, d, h = body_of(it.shape)
    tag = f'weapon {it.shape} at ({it.x},{it.y},{it.z})'
    check(f'{tag}: carryable (not SI_FIXED) and drawn (not SI_EDITOR)',
          not si.has_flag('SI_FIXED') and not si.has_flag('SI_EDITOR'))
    X, Y, Z, XD, YD, ZD, S, F0, F1 = bx.T
    mine = (X == it.x) & (Y == it.y) & (S == it.shape)
    buried = ~mine & (X - XD < it.x) & (it.x - w < X) & (Y - YD < it.y) & \
        (it.y - d < Y) & (Z < it.z + h) & (Z + ZD > it.z) & \
        ((F0 & SI_SOLID) > 0) & (XD > 0) & (YD > 0)
    tall = ~mine & (X - XD < it.x + 80) & (it.x - w - 80 < X) & \
        (Y - YD < it.y + 80) & (it.y - d - 80 < Y) & (ZD >= 8) & \
        ((F0 & SI_SOLID) > 0)
    check(f'{tag}: on clear floor, in no solid and with nothing tall '
          f'within 80 to sort against (map-geometry rule)',
          it.z == 0 and not buried.any() and not tall.any(),
          f'in {sorted(set(S[buried].tolist()))}, '
          f'near {sorted(set(S[tall].tolist()))}')
    cx, cy = it.x - w // 2, it.y - d // 2
    check(f'{tag}: the Avatar walks up to it from the arrival pad',
          reached(er, reach, cx - 96, cx + 96 + 64, cy - 96, cy + 96 + 64,
                  it.z - 9, it.z + 8) is not None)
_dat = os.path.join(BASE_DIR, 'scummvm-lv', 'dists', 'engine-data',
                    'ultima8.dat')
if os.path.exists(_dat):
    import configparser
    import zipfile
    ini = configparser.ConfigParser(interpolation=None)
    ini.read_string(zipfile.ZipFile(_dat).read('u8weapons.ini')
                    .decode('latin-1'))
    real = {int(ini[s]['shape'], 0): int(ini[s]['damage_type'], 0)
            for s in ini.sections()}
    check('WEAPON_DAMAGE matches the built engine\'s u8weapons.ini',
          all(real.get(k) == v for k, v in WEAPON_DAMAGE.items()),
          str({k: (v, real.get(k)) for k, v in WEAPON_DAMAGE.items()
               if real.get(k) != v}))
else:
    print(f'  (no {os.path.relpath(_dat, BASE_DIR)} here: WEAPON_DAMAGE is '
          f'checked against the engine file in the main checkout only)')

print('--- Map 11: the way into the south half fires no trigger '
      '(playtest-2026-10-17-replay-leg3 finding 4)')
# Group 4's trigger stood across the corridor's mouth, +/-288 x 64 at
# (9728,14528), and its rats hatched on every player bound for the Fire,
# the Water talisman or the pillars: hp 30 -> 18 (Douglas 2026-10-24: not
# deliberate). No trigger may cover the passage or its mouth, nor lie
# within ROUTE_WANDER of the straight line between two of the half's ends.
bx, er, reach = FLOODS[11]
px0, py0, px1, py1 = SOUTH_PASSAGE
i0, i1 = er._kx(px0 - 1024, px1 + 1024)
j0, j1 = er._ky(py0 - 1, 14400)
span = [er.x_of(i) for i in range(i0, i1 + 1)
        if any(r[i, j0:j1 + 1].any() for r in reach.values())]
check(f'the Avatar walks the corridor (y {py0}-14399) with his reference x '
      f'within the passage box\'s {px0}-{px1}', span and
      px0 <= min(span) and max(span) <= px1,
      f'x {min(span)}-{max(span)}' if span else 'not walked')
_ends = list(SOUTH_HALF_ENDS.items())
for t in (it for it in arch.get_map_items(11) if is_trigger(it)):
    xr, yr = (t.npcnum >> 4) & 0xF, t.npcnum & 0xF
    bw, bd, _ = AVATAR_BODY
    x_lo, x_hi = t.x - 32 * xr, t.x + 32 * xr + bw - 1
    y_lo, y_hi = t.y - 32 * yr, t.y + 32 * yr + bd - 1
    at_floor = t.z - HATCH_Z < 0 <= t.z + HATCH_Z
    tag = (f'map 11 trigger group {t.mapnum & 0x1F} at ({t.x},{t.y},{t.z}), '
           f'box x {x_lo}-{x_hi}, y {y_lo}-{y_hi}')
    check(f'{tag}: covers no spot of the south-half entrance passage '
          f'{SOUTH_PASSAGE}', not (at_floor and x_lo <= px1 and px0 <= x_hi
                                   and y_lo <= py1 and py0 <= y_hi))
    worst = None
    for k, (na, a) in enumerate(_ends):
        for nb, b in _ends[k + 1:]:
            n = max(1, int(math.dist(a, b)) // 8)
            for s in range(n + 1):
                x = a[0] + (b[0] - a[0]) * s / n
                y = a[1] + (b[1] - a[1]) * s / n
                d = math.hypot(max(x_lo - x, 0, x - x_hi),
                               max(y_lo - y, 0, y - y_hi))
                if worst is None or d < worst[0]:
                    worst = (d, na, nb, (round(x), round(y)))
    check(f'{tag}: more than {ROUTE_WANDER} off the straight line between '
          f'any two of the south half\'s ends (least {round(worst[0])}, '
          f'{worst[1]} - {worst[2]})', not at_floor or worst[0] > ROUTE_WANDER,
          f'at {worst[3]}')

print('--- Maps 8 and 39: retail eggs and triggers, untouched')
base = MapArchive(pristine_base(BASE_FIXED, None, 'base FIXED.DAT'))


def key(it):
    return (it.x, it.y, it.z, it.shape, it.frame, it.flags, it.quality,
            it.npcnum, it.mapnum)


for mapnum in RETAIL_MAPS:
    for what, pick in (('monster eggs', lambda i: i.shape == MONSTER_EGG),
                       ('MONEGG triggers', is_trigger)):
        built = sorted(key(i) for i in arch.get_map_items(mapnum) if pick(i))
        retail = sorted(key(i) for i in base.get_map_items(mapnum) if pick(i))
        check(f'map {mapnum}: {len(built)} {what}, the pristine base\'s',
              built == retail, f'{len(retail)} in the base')

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

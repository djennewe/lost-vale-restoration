#!/usr/bin/env python3
"""
test_uc_reentry.py — a fixed item that usecode changed stays changed when
the player leaves its map and comes back.

THE MECHANISM (docs/playtest-2026-10-10-maps3.md finding 1). Every LV
placement is a FIXED.DAT record, and `World::switchMap` unloads the old
map's fixed items and re-reads the new map's from FIXED.DAT on every entry
(scummvm-lv-console/engines/ultima/ultima8/world/world.cpp:170-196). So an
`item.destroy()` or `setFrame()` on a fixed record lasts until the next map
switch. A save is different: it carries the current map's fixed items as
objects (TODO "A save carries its map's fixed items"), so loading does not
undo a change. Retail keeps such state in globals and re-applies it in
usecode on entry; this project does the same with eggs gated on the
globals the change already writes.

Each persisted change gets two proofs here:

  * an ENTRY PATH — every way into the map hatches a re-apply egg before
    the player can reach the changed item. On Maps 10 and 11 the egg sits
    on every arrival pad, so the proof is engine hatch arithmetic
    (egg_hatcher_process.cpp:57-79) on each teleport target. On Map 18
    (one arrival, the sanctum behind a wall) the proof is a flood: with
    the egg boxes made solid, the changed items are unreachable from the
    arrival pad.
  * the RE-APPLY ITSELF, from the globals, run in the engine-faithful
    simulator against the built EUSECODE.FLX on the built FIXED.DAT's own
    records: solve, leave (a fresh reload of the map's records, globals
    kept), re-enter (hatch every usecode egg whose box holds the arrival
    pad), and the change is back.

Persisted changes covered (the audit is in the commit that added this):
  Map 11  four pillars (865) and two sealing boulders (66 q299) — COLPUZZL,
          re-applied by EggReapply (lv-new/REAPPLY.UNK) on both pads.
  Map 10  the Test Plant (126 frame 0 q10) — PLNTST, re-applied by
          EggReapply on all four pads.
  Map 18  the breach walls (q307) — EggCrackHint/EggTempleEntry; the freed
          gods' frames — EggTempleEntry. Their re-apply runs are
          test_uc_eggs.py P4c/P4f; this file proves the entry path.

Carryable quest items (docs/playtest-2026-10-11-static-art.md finding 2).
A fixed record the player PICKS UP is back on the ground at the next entry,
so each carryable quest item is removed again on arrival once the player
no longer needs one: when the step that consumes it is done, or when the
Avatar already carries one of it. Neither gate needs a new flag, and both
let a lost copy (dropped on another map, where the fixed-item reload
deletes it) come back.
  Map 10  the special root (869 f0) — givenRoot (Ezrekal takes it); the
          Passage stone (798 f0) — haveMark (EggPlantTest consumes it).
  Map 11  the four talismans (596 f0-3) — the element flag of the pillar
          each one destroys (COLPUZZL: the OPPOSITE element's talisman).
  Map 17  the Shield halves (878 f0/f1) — shieldFixed (the ceremony
          consumes both); EggReapply's first egg on Map 17, on pad 209.
And the two scenes a duplicate could replay, guarded at their hatch head:
  EggShades (lv-patched/SHADES.UNK) — its once-only latch is
          setEggXRange(1) on a fixed egg, which the next entry reloads, so
          a second pair of halves ran the ceremony again and made a second
          Shield; shieldFixed now ends it.
  EggPlantTest (lv-patched/PLNTST.UNK) — any second stone (the respawn,
          or Ragnar's bag after the island stone) replayed the Test and
          poisoned the Avatar again; haveMark now ends it.
One-time potions (Douglas 2026-10-30): Hrodny's protection and
invisibility potions (859 f5/f7) on Map 10, by the same two gates, but
with a new flag each, set when one is drunk (potionProtectionDrunk /
potionInvisDrunk, lv-patched/POTION.UNK change 2). Ezrekal's health and
mana (f1/f2) still restock and the Tiny Tars (f8) still refill: R11.
"""

import json
import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
MAP_SRC = os.path.join(BASE_DIR, 'agents', 'map-populator', 'src')
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, MAP_SRC)

from u8c_sim import UCSim, SimWorld  # noqa: E402
from u8c_symbols import TYPE_SHAPES  # noqa: E402
from u8_map import MapArchive  # noqa: E402

MANIFEST = os.path.join(BASE_DIR, 'shared', 'build', 'lv_manifest.json')
FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
_m = json.load(open(MANIFEST))
CLS = _m['classes']
FLAGS = {k: v['bit'] for k, v in _m['global_flags'].items()}

EGG_CLASS_BASE = 0x47F          # UnkEgg dispatch: class = quality + 0x47F
REAPPLY = CLS.get('EGGREAPPLY')
RECEPTACLE = CLS['TYPERECEPTACLE']
TEMPLENT = CLS['EGGTEMPLEENTRY']
CRACKHINT = CLS['EGGCRACKHINT']
USECODE_EGG_CLASSES = set(CLS.values())

HATCH = 7
USE = 1
SHAPE_AVATAR = 1
SHAPE_EGG = 73
AVATAR_FOOTPAD = 64             # shape 1, footpad 2x2
EGG_RANGE_MUL = 32              # egg_hatcher_process.cpp: U8 range_mul
EGG_Z_RANGE = 48

SHAPE_PILLAR = TYPE_SHAPES['TypeElementalColumn']     # 865
SHAPE_BOULDER = TYPE_SHAPES['TypeSealingBoulder']     # 66
SHAPE_PLANT = TYPE_SHAPES['TypeShortmushroom']        # 126
SHAPE_TALISMAN = TYPE_SHAPES['TypeTalisman']          # 596
SHAPE_GOD = TYPE_SHAPES['TypeZealanGod']              # 860
SHAPE_RECEPTACLE = 866
RECEPTACLE_NPCNUM = 120
BOULDER_Q = 299                 # build_map_11 SEALING_BOULDER_QUALITY
TEST_PLANT_Q = 10               # build_map_10 build_test_grounds
BREACH_Q = 307                  # build_map_18 BREACH_QUALITY
WALL_SHAPES = (TYPE_SHAPES['TypeTempleWallPiece'],
               TYPE_SHAPES['TypeTempleWallStub'])
# Pillar frame -> the COLPUZZL flag its destruction sets (frame = element,
# build_map_11 decision 2026-07-04: 0 Earth, 1 Air, 2 Fire, 3 Water).
PILLAR_FLAG = {0: 'EarthColumnDestroyed', 1: 'AirColumnDestroyed',
               2: 'FireColumnDestroyed', 3: 'WaterColumnDestroyed'}

# Carryable quest items and the flag that ends each one's use.
SHAPE_ROOT = TYPE_SHAPES['TypeWeedz']                 # 869
SHAPE_STONE = TYPE_SHAPES['TypeBushKey']              # 798
SHAPE_HALVES = TYPE_SHAPES['TypeAOFrizbee']           # 878
SHAPE_RESTORED = TYPE_SHAPES['TypeSacredShield']      # 879
# Talisman frame -> the pillar flag set when COLPUZZL consumes it: each
# pillar takes the OPPOSITE element's talisman (fire<->water, earth<->air).
TALISMAN_FLAG = {0: 'AirColumnDestroyed', 1: 'EarthColumnDestroyed',
                 2: 'WaterColumnDestroyed', 3: 'FireColumnDestroyed'}
EGGSHADES = CLS['EGGSHADES']
EGGPLANTTEST = CLS['EGGPLANTTEST']
EQ_BACKPACK = 6
SHAPE_BACKPACK = 529
ATLI, THORDIS, EZREKAL = 107, 106, 116

passed = 0
failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def flag(globals_bits, name):
    """A one-bit global, read the way UCSim.get_global reads it."""
    b = FLAGS[name]
    return (globals_bits[b >> 3] >> (b & 7)) & 1


def set_flag(globals_bits, name):
    b = FLAGS[name]
    globals_bits[b >> 3] |= 1 << (b & 7)



_archive = MapArchive(FIXED)
_records = {}


def records(mapnum):
    if mapnum not in _records:
        _records[mapnum] = _archive.get_map_items(mapnum)
    return _records[mapnum]


def hatches(egg, x, y, z):
    """EggHatcherProcess::run for an Avatar standing at (x, y, z)."""
    xr, yr = (egg.npcnum >> 4) & 0xF, egg.npcnum & 0xF
    ex, ey, ez = egg.x, egg.y, egg.z & 0xFF
    return (ex - EGG_RANGE_MUL * xr <= x
            and x - AVATAR_FOOTPAD < ex + EGG_RANGE_MUL * xr
            and ey - EGG_RANGE_MUL * yr <= y
            and y - AVATAR_FOOTPAD < ey + EGG_RANGE_MUL * yr
            and ez - EGG_Z_RANGE < z <= ez + EGG_Z_RANGE)


def egg_class(it):
    return it.quality + EGG_CLASS_BASE if it.shape == SHAPE_EGG else None


def arrivals(mapnum):
    return [it for it in records(mapnum) if it.is_teleport_target]


def load_world(mapnum, talismans=False, carry=()):
    """The map as switchMap leaves it: every record re-read from FIXED.DAT
    (glob eggs aside — they only expand to terrain). The Avatar, carrying
    one talisman per element when asked and each (shape, frame, quality)
    in `carry` (what he picked up before he left: the Avatar is not a
    fixed record, so his pack survives the switch), stands off the map."""
    w = SimWorld()
    av = w.add(SHAPE_AVATAR, objid=1, x=0, y=0, z=0)
    if talismans:
        for f in range(4):
            w.put_in_container(
                w.add(SHAPE_TALISMAN, frame=f, quality=101 + f), av)
    for shape, frame, quality in carry:
        w.put_in_container(w.add(shape, frame=frame, quality=quality), av)
    for it in records(mapnum):
        if it.is_glob_egg:
            continue
        w.add(it.shape, frame=it.frame, quality=it.quality,
              x=it.x, y=it.y, z=it.z & 0xFF, npcnum=it.npcnum)
    return w, av


def live(w, pred):
    return [it for it in w.items.values()
            if not it.destroyed and it.parent is None and pred(it)]


def is_pillar(it):
    return it.shape == SHAPE_PILLAR


def is_boulder(it):
    return it.shape == SHAPE_BOULDER and it.quality == BOULDER_Q


def is_test_plant(it):
    return (it.shape == SHAPE_PLANT and it.frame == 0
            and it.quality == TEST_PLANT_Q)


def is_receptacle(it):
    return it.shape == SHAPE_RECEPTACLE and it.npcnum == RECEPTACLE_NPCNUM


def enter(w, globals_bits, pad):
    """Arrive at `pad`: hatch every usecode egg whose box holds it. Returns
    (classes hatched, barks)."""
    hatched, barks = [], []
    for it in list(w.items.values()):
        cid = egg_class(it) if it.shape == SHAPE_EGG else None
        if cid not in USECODE_EGG_CLASSES or it.destroyed:
            continue
        if not hatches(it, pad.x, pad.y, pad.z & 0xFF):
            continue
        sim = UCSim(world=w, globals_bits=globals_bits)
        sim.run_event(cid, None, it.objid, event=HATCH)
        hatched.append(cid)
        barks.extend(t for _o, t in sim.barks)
    return hatched, barks


def solve(w, globals_bits, qualities):
    """Use each named receptacle with the talismans in the pack."""
    for r in live(w, is_receptacle):
        if r.quality in qualities:
            UCSim(world=w, globals_bits=globals_bits).run_event(
                RECEPTACLE, None, r.objid, event=USE)


print('=' * 70)
print('Re-entry: fixed-item changes re-applied from the globals')
print('=' * 70)

check('EggReapply is a manifest-pinned class',
      REAPPLY is not None, 'no EGGREAPPLY in lv_manifest.json classes')

# ── Entry paths on Maps 10, 11 and 17: an EggReapply egg on every pad ───
for mapnum in (11, 10, 17):
    print()
    print(f'R1 map {mapnum}: every arrival pad hatches EggReapply')
    eggs = [it for it in records(mapnum)
            if REAPPLY is not None and egg_class(it) == REAPPLY]
    pads = arrivals(mapnum)
    check(f'map {mapnum} has arrival pads', bool(pads))
    for pad in pads:
        hit = [e for e in eggs if hatches(e, pad.x, pad.y, pad.z & 0xFF)]
        check(f'map {mapnum}: pad {pad.quality & 0xFF} at '
              f'({pad.x},{pad.y},{pad.z & 0xFF}) is inside an EggReapply box',
              bool(hit), f'{len(eggs)} EggReapply eggs on the map')

# EggReapply sweeps its whole map by tag, so each tag must name exactly the
# records the change touched, and nothing on the other map.
print()
print('R2: the re-apply tags name exactly the changed records')
m11, m10 = records(11), records(10)
pillars = [it for it in m11 if is_pillar(it)]
check('map 11: four pillars, one per element frame',
      sorted(it.frame for it in pillars) == [0, 1, 2, 3],
      str([(it.frame, it.x, it.y) for it in pillars]))
check('map 11: two quality-299 sealing boulders',
      len([it for it in m11 if is_boulder(it)]) == 2)
check(f'map 10: one Test Plant ({SHAPE_PLANT} frame 0 q10)',
      len([it for it in m10 if is_test_plant(it)]) == 1)
check('map 10 carries no pillar or q299 boulder',
      not [it for it in m10 if is_pillar(it) or is_boulder(it)])
check('map 11 carries no Test Plant',
      not [it for it in m11 if is_test_plant(it)])

# ── Map 11: solve, leave, re-enter ──────────────────────────────────────
print()
print('R3: map 11 — solve the columns, leave, re-enter by each pad')
g = bytearray(0x1000)
w, av = load_world(11, talismans=True)
solve(w, g, {201, 202, 203, 204})
check('solving destroys all four pillars', not live(w, is_pillar))
check('...and both sealing boulders', not live(w, is_boulder))
check('...and sets allColumnsDestroyed',
      flag(g, 'allColumnsDestroyed') == 1)

w, av = load_world(11)
check('leaving and coming back reloads the pillars (the defect\'s cause)',
      len(live(w, is_pillar)) == 4)
check('...and the boulders', len(live(w, is_boulder)) == 2)

for pad in arrivals(11):
    w, av = load_world(11)
    receptacles = len(live(w, is_receptacle))
    hatched, barks = enter(w, g, pad)
    tag = f'pad {pad.quality & 0xFF}'
    check(f'{tag}: the pillars are gone on arrival', not live(w, is_pillar),
          f'{len(live(w, is_pillar))} left; hatched {hatched}')
    check(f'{tag}: the sealing boulders are gone on arrival',
          not live(w, is_boulder),
          f'{len(live(w, is_boulder))} left; hatched {hatched}')
    check(f'{tag}: the receptacles stay', len(live(w, is_receptacle))
          == receptacles == 4)
    check(f'{tag}: the re-apply is silent', not barks, str(barks))

print()
print('R4: map 11 — nothing is undone before it is done')
for pad in arrivals(11):
    w, av = load_world(11)
    enter(w, bytearray(0x1000), pad)
    check(f'pad {pad.quality & 0xFF}, puzzle untouched: all four pillars '
          'and both boulders stand',
          len(live(w, is_pillar)) == 4 and len(live(w, is_boulder)) == 2)

g = bytearray(0x1000)
w, av = load_world(11, talismans=True)
solve(w, g, {201, 203})          # Earth and Fire only
pad = arrivals(11)[0]
w, av = load_world(11)
enter(w, g, pad)
left = sorted(it.frame for it in live(w, is_pillar))
check('half solved (Earth, Fire): only those two pillars are re-destroyed',
      left == [1, 3], f'frames left {left}')
check('...and the boulders stay until all four are down',
      len(live(w, is_boulder)) == 2)

# ── Map 10: the Test Plant ───────────────────────────────────────────────
print()
print('R5: map 10 — the Test Plant PLNTST blew away stays gone')
for have in (0, 1):
    for pad in arrivals(10):
        w, av = load_world(10)
        # One of the scene's five popped plants: NONFIXED, quality 0, so it
        # survives a reload on its own and the re-apply must not touch it.
        popped = w.add(SHAPE_PLANT, frame=0, quality=0,
                       x=12767, y=29791, z=64)
        g = bytearray(0x1000)
        if have:
            set_flag(g, 'haveMark')
        hatched, barks = enter(w, g, pad)
        tag = f'pad {pad.quality & 0xFF}'
        if have:
            check(f'{tag}, haveMark set: the Test Plant is gone',
                  not live(w, is_test_plant), f'hatched {hatched}')
        else:
            check(f'{tag}, haveMark clear: the Test Plant stands',
                  len(live(w, is_test_plant)) == 1)
        check(f'{tag}: the scene\'s own plant survives', not popped.destroyed)

# ── Map 18: the existing re-apply eggs sit on the only way in ───────────
print()
print('R6: map 18 — every walk to the breach or the gods crosses its egg')
from exact_reach import ExactReach, load_map  # noqa: E402


def egg_blocker(egg):
    """A solid box that refuses exactly the positions where `egg` hatches:
    ExactReach blocks x in (bx - bxd, bx + 64) and z in (bz - 40, bz + bzd);
    the hatch set is x in [x1, x2 + 64), z in (ez - 48, ez + 48]."""
    xr, yr = (egg.npcnum >> 4) & 0xF, egg.npcnum & 0xF
    x1, x2 = egg.x - EGG_RANGE_MUL * xr, egg.x + EGG_RANGE_MUL * xr
    y1, y2 = egg.y - EGG_RANGE_MUL * yr, egg.y + EGG_RANGE_MUL * yr
    ez = egg.z & 0xFF
    return (x2, y2, ez - 8, x2 - x1 + 1, y2 - y1 + 1, 2 * EGG_Z_RANGE + 9)


def flood18(block):
    """Map 18 with the breach OPEN (templeOpen set, the walls destroyed),
    flooded from the arrival pad with the given eggs' boxes solid."""
    items, shapes = load_map(18)
    items = [it for it in items
             if not (it.shape in WALL_SHAPES and it.quality == BREACH_Q)]
    xs = [i.x for i in items if i.x >= 64]
    ys = [i.y for i in items if i.y >= 64]
    er = ExactReach(items, shapes,
                    (min(xs) - 64, min(ys) - 64, max(xs) + 64, max(ys) + 64))
    for egg in block:
        er.blockers.append(egg_blocker(egg))
    pad = arrivals(18)[0]
    reach, seeded = er.flood([(pad.x, pad.y, pad.z & 0xFF)])
    return er, reach if seeded else None


m18 = records(18)
check('map 18 has exactly one arrival pad', len(arrivals(18)) == 1)
breach = [it for it in m18 if it.shape in WALL_SHAPES and it.quality == BREACH_Q]
gods = [it for it in m18 if it.shape == SHAPE_GOD]
hints = [it for it in m18 if egg_class(it) == CRACKHINT]
entries = [it for it in m18 if egg_class(it) == TEMPLENT]
check('map 18: six breach records, three gods, two EggCrackHint, one '
      'EggTempleEntry',
      (len(breach), len(gods), len(hints), len(entries)) == (6, 3, 2, 1))
bx = sum(it.x for it in breach) // max(len(breach), 1)
by = max((it.y for it in breach), default=0)

er, reach = flood18([])
check('control: with no egg blocked, the open breach is reachable',
      reach is not None and bool(er.reached_near(reach, bx, by - 64, 0)))
check('control: ...and so are the gods',
      reach is not None and all(er.reached_near(reach, it.x, it.y,
                                                it.z & 0xFF, ring=160)
                                for it in gods))
er, reach = flood18(hints)
check('EggCrackHint boxes solid: the breach cannot be reached '
      '(it is reopened before the player gets there)',
      reach is not None and not er.reached_near(reach, bx, by - 64, 0))
er, reach = flood18(entries)
check('EggTempleEntry box solid: no god can be reached (their frames are '
      're-applied before the player gets there)',
      reach is not None and not any(er.reached_near(reach, it.x, it.y,
                                                    it.z & 0xFF, ring=160)
                                    for it in gods))

# ── Carryable quest items: picked up, they come back with the map ───────
# (docs/playtest-2026-10-11-static-art.md finding 2). name -> (map, shape,
# frames, the flag that ends each frame's use).
QUEST_ITEMS = {
    'special root': (10, SHAPE_ROOT, (0,), lambda f: 'givenRoot'),
    'Passage stone': (10, SHAPE_STONE, (0,), lambda f: 'haveMark'),
    'talisman': (11, SHAPE_TALISMAN, (0, 1, 2, 3),
                 lambda f: TALISMAN_FLAG[f]),
    'Shield half': (17, SHAPE_HALVES, (0, 1), lambda f: 'shieldFixed'),
}


def item_records(mapnum, shape):
    return [it for it in records(mapnum)
            if it.shape == shape and not it.flags & 0x0008]


def on_ground(w, shape, frame):
    return live(w, lambda it: it.shape == shape and it.frame == frame)


print()
print('R7: each carryable quest item is one tagged record, on its own map')
for name, (mapnum, shape, frames, _gate) in QUEST_ITEMS.items():
    recs = item_records(mapnum, shape)
    check(f'map {mapnum}: one {name} ({shape}) record per frame {frames}',
          sorted(it.frame for it in recs) == list(frames),
          str([(it.frame, it.quality, it.x, it.y) for it in recs]))
    others = [m for m in (10, 11, 17) if m != mapnum
              and item_records(m, shape)]
    check(f'...and no other re-applied map carries a {shape}', not others,
          f'also on {others}')

print()
print('R8: pick up, leave, re-enter — no second copy on the ground')
for name, (mapnum, shape, frames, gate) in QUEST_ITEMS.items():
    carry = [(shape, f, 0) for f in frames]
    w, av = load_world(mapnum, carry=carry)
    check(f'{name}: leaving and coming back reloads the record '
          '(the defect\'s cause)',
          all(len(on_ground(w, shape, f)) == 1 for f in frames))
    for pad in arrivals(mapnum):
        tag = f'map {mapnum} pad {pad.quality & 0xFF}'
        # Control: never picked up, never used.
        w, av = load_world(mapnum)
        enter(w, bytearray(0x1000), pad)
        check(f'{tag}: {name} not yet taken — it stays',
              all(len(on_ground(w, shape, f)) == 1 for f in frames))
        # Picked up and carried off the map: no second copy.
        w, av = load_world(mapnum, carry=carry)
        hatched, barks = enter(w, bytearray(0x1000), pad)
        held = [it for it in w.items.values() if it.parent == av.objid]
        check(f'{tag}: {name} carried — none back on the ground',
              not any(on_ground(w, shape, f) for f in frames),
              f'hatched {hatched}')
        check(f'{tag}: ...the carried one is untouched',
              len(held) == len(frames) and not any(it.destroyed
                                                   for it in held))
        check(f'{tag}: ...and the re-apply is silent', not barks, str(barks))
        # Used up (the step that consumes it is done), nothing carried.
        g = bytearray(0x1000)
        for f in frames:
            set_flag(g, gate(f))
        w, av = load_world(mapnum)
        enter(w, g, pad)
        check(f'{tag}: {name} used ({sorted({gate(f) for f in frames})}) '
              '— none back on the ground',
              not any(on_ground(w, shape, f) for f in frames))
    if len(frames) > 1:
        pad = arrivals(mapnum)[0]
        f0 = frames[0]
        w, av = load_world(mapnum, carry=[(shape, f0, 0)])
        enter(w, bytearray(0x1000), pad)
        check(f'{name}: only frame {f0} carried — only frame {f0} removed',
              not on_ground(w, shape, f0)
              and all(len(on_ground(w, shape, f)) == 1 for f in frames[1:]))
        g = bytearray(0x1000)
        set_flag(g, gate(f0))
        w, av = load_world(mapnum)
        enter(w, g, pad)
        used = [f for f in frames if gate(f) == gate(f0)]
        check(f'{name}: only {gate(f0)} set — only frame(s) {used} removed',
              all(bool(on_ground(w, shape, f)) == (f not in used)
                  for f in frames))

# Save compatibility: a save made before 2026-10-17 carries the halves as
# retired 870 (2026-10-11..17) or retail 539 (before), frame 0 quality 81
# and frame 1 quality 82 (build_map_17 QUALITY_SHIELD_HALF_1/2). Carried,
# each counts as that frame's half, so its 878 record goes; Pagan's own 539
# shields (quality 0) are not halves and take nothing away.
print()
print('R8b: map 17 — a pre-2026-10-17 save\'s halves (870 or 539) count')
_pad17 = arrivals(17)[0]
for desc, carry in (
        ('retired 870 halves', [(870, f, 81 + f) for f in (0, 1)]),
        ('retail 539 halves', [(539, f, 81 + f) for f in (0, 1)])):
    w, av = load_world(17, carry=carry)
    hatched, barks = enter(w, bytearray(0x1000), _pad17)
    held = [it for it in w.items.values() if it.parent == av.objid]
    check(f'{desc} carried — no 878 half back on the ground',
          not any(on_ground(w, SHAPE_HALVES, f) for f in (0, 1)),
          f'hatched {hatched}')
    check(f'{desc}: ...the carried ones are untouched',
          len(held) == 2 and not any(it.destroyed for it in held))
w, av = load_world(17, carry=[(870, 0, 81)])
enter(w, bytearray(0x1000), _pad17)
check('only the 870 sun half carried — only 878 frame 0 removed',
      not on_ground(w, SHAPE_HALVES, 0)
      and len(on_ground(w, SHAPE_HALVES, 1)) == 1)
w, av = load_world(17, carry=[(539, f, 0) for f in (0, 1)])
enter(w, bytearray(0x1000), _pad17)
check("Pagan's 539 shields (quality 0) carried — both 878 halves stay",
      all(len(on_ground(w, SHAPE_HALVES, f)) == 1 for f in (0, 1)))


def scene_egg(mapnum, cls):
    eggs = [it for it in records(mapnum) if egg_class(it) == cls]
    return eggs[0] if len(eggs) == 1 else None


def ceremony_world(halves):
    """The Sacred Circle as a fresh entry leaves it: the EggShades egg read
    from its FIXED.DAT record (so any setEggXRange latch is gone), the
    Avatar with a backpack holding the given half frames."""
    w = SimWorld()
    av = w.add(SHAPE_AVATAR, objid=1, x=20480, y=17100, z=0)
    pack = w.add(SHAPE_BACKPACK)
    w.put_in_container(pack, av)
    av.equipment[EQ_BACKPACK] = pack.objid
    held = []
    for f in halves:
        h = w.add(SHAPE_HALVES, frame=f, quality=81 + f)
        w.put_in_container(h, pack)
        held.append(h)
    for n in (ATLI, THORDIS, EZREKAL):
        w.add(SHAPE_AVATAR, objid=n, x=1000 + n, y=1000, z=0)
    rec = scene_egg(10, EGGSHADES)
    egg = w.add(SHAPE_EGG, quality=rec.quality, x=rec.x, y=rec.y,
                z=rec.z & 0xFF, npcnum=rec.npcnum)
    return w, av, pack, held, egg


def run_ceremony(w, egg, g, answers):
    sim = UCSim(world=w, globals_bits=g)
    sim.follow_spawns = True
    sim.answer_script = list(answers)
    sim.run_event(EGGSHADES, 0, egg.objid, event=HATCH)
    return sim


def restored(w):
    return [it for it in w.items.values()
            if it.shape == SHAPE_RESTORED and not it.destroyed]


SUCCESS = ["Let's be reasonable!", 'Yes, Priestess.', 'Please, High Priestess.']
print()
print('R9: a second pair of halves cannot run the ceremony again')
check('map 10 has exactly one EggShades egg',
      scene_egg(10, EGGSHADES) is not None)
g = bytearray(0x1000)
set_flag(g, 'avatarPoisoned')
w, av, pack, held, egg = ceremony_world((0, 1))
sim = run_ceremony(w, egg, g, SUCCESS)
check('first ceremony: shieldFixed set, one restored Shield, cure given',
      flag(g, 'shieldFixed') == 1 and len(restored(w)) == 1
      and flag(g, 'avatarPoisoned') == 0)
first_npcnum = egg.npcnum
check('...and it latched the egg in memory only (setEggXRange(1))',
      first_npcnum != scene_egg(10, EGGSHADES).npcnum,
      f'0x{first_npcnum:02X}')
# Leave and come back: the egg is the FIXED record again; the Avatar holds
# the Shield and a second pair of halves (the respawned 870s).
w, av, pack, held, egg = ceremony_world((0, 1))
w.put_in_container(w.add(SHAPE_RESTORED, quality=83), pack)
sim = run_ceremony(w, egg, g, SUCCESS)
check('re-entry with a second pair: nobody teleports',
      not sim.teleports, str(sim.teleports))
check('...no ask menu', not sim.asks, str([a[0] for a in sim.asks]))
check('...no second Shield', len(restored(w)) == 1,
      f'{len(restored(w))} restored shields')
check('...the halves are not consumed', not any(h.destroyed for h in held))
check('...and the scene is silent', not sim.barks, str(sim.barks))
# Control: the angry path sets no shieldFixed, so the 1994 retry stands.
g = bytearray(0x1000)
w, av, pack, held, egg = ceremony_world((0, 1))
run_ceremony(w, egg, g, ["Can't you two get along!?",
                         'You two are insufferable!'])
w, av, pack, held, egg = ceremony_world((0, 1))
sim = run_ceremony(w, egg, g, SUCCESS)
check('control: after the angry path the ceremony can be retried '
      '(elders teleport in)',
      any(t['obj'] == ATLI for t in sim.teleports), str(sim.teleports))

print()
print('R10: a second Passage stone cannot replay the Passage Test')
check('map 10 has exactly one EggPlantTest egg',
      scene_egg(10, EGGPLANTTEST) is not None)


def test_world(stone=True):
    w = SimWorld()
    av = w.add(SHAPE_AVATAR, objid=1, x=12800, y=29300, z=64)
    held = None
    if stone:
        held = w.add(SHAPE_STONE, frame=0, quality=0)
        w.put_in_container(held, av)
    rec = scene_egg(10, EGGPLANTTEST)
    egg = w.add(SHAPE_EGG, quality=rec.quality, x=rec.x, y=rec.y,
                z=rec.z & 0xFF, npcnum=rec.npcnum)
    return w, held, egg


def run_test(w, egg, g):
    sim = UCSim(world=w, globals_bits=g)
    sim.follow_spawns = True
    sim.run_event(EGGPLANTTEST, 0, egg.objid, event=HATCH)
    return sim


g = bytearray(0x1000)
set_flag(g, 'thordisToldTest')
w, held, egg = test_world()
sim = run_test(w, egg, g)
check('first Test: haveMark set, the Avatar poisoned, the stone consumed',
      flag(g, 'haveMark') == 1 and flag(g, 'avatarPoisoned') == 1
      and held.destroyed)
# Cured at the ceremony, then back with a second stone.
b = FLAGS['avatarPoisoned']
g[b >> 3] &= ~(1 << (b & 7)) & 0xFF
w, held, egg = test_world()
sim = run_test(w, egg, g)
check('second stone after the Mark: no teleport', not sim.teleports,
      str(sim.teleports))
check('...the Avatar is not poisoned again', flag(g, 'avatarPoisoned') == 0)
check('...and the stone is left in the pack', not held.destroyed)

# ── One-time potions (Douglas 2026-10-30, option c of the b931fb4 audit) ─
# Hrodny's protection (859 f5) and invisibility (859 f7) potions are fixed
# records like the quest items, and come back the same way. Drinking one
# sets its flag in TypePotion::use() (lv-patched/POTION.UNK change 2);
# EggReapply removes the record once that flag is set or the Avatar
# carries one. Ezrekal's health and mana (f1, f2) keep restocking, and the
# Tiny Tars (f8, in Hrodny's chest) keep refilling.
SHAPE_POTION = TYPE_SHAPES['TypePotion']              # 859
TYPEPOTION = CLS['TYPEPOTION']
POTION_FLAG = {5: 'potionProtectionDrunk', 7: 'potionInvisDrunk'}
RESTOCK = (1, 2)
TINY_TAR = 8


def potions(w, frame):
    """Live potions of a frame, top-level or not: load_world adds the
    chest's contained Tiny Tars as loose items, so this counts them too."""
    return [it for it in w.items.values() if not it.destroyed
            and it.shape == SHAPE_POTION and it.frame == frame]


print()
print('R11: map 10 — protection and invisibility are drunk once')
recs = item_records(10, SHAPE_POTION)
check('map 10: one placed potion each of frames 1, 2, 5, 7',
      sorted(it.frame for it in recs) == [1, 2, 5, 7],
      str([(it.frame, it.x, it.y) for it in recs]))
tars = [it for it in records(10) if it.shape == SHAPE_POTION
        and it.frame == TINY_TAR and it.flags & 0x0008]
check('map 10: three Tiny Tars, contained (in the chest)', len(tars) == 3)
check('...and no other re-applied map carries a potion record',
      not [m for m in (11, 17)
           if [it for it in records(m) if it.shape == SHAPE_POTION]])

for f in (1, 2, 5, 7, TINY_TAR):
    w = SimWorld()
    av = w.add(SHAPE_AVATAR, objid=1, x=0, y=0, z=0)
    pot = w.add(SHAPE_POTION, frame=f, npcnum=229)
    w.put_in_container(pot, av)
    g = bytearray(0x1000)
    UCSim(world=w, globals_bits=g).run_event(TYPEPOTION, None, pot.objid,
                                             event=USE)
    got = {n for n in POTION_FLAG.values() if flag(g, n)}
    want = {POTION_FLAG[f]} if f in POTION_FLAG else set()
    check(f'drinking frame {f} from the pack sets {sorted(want) or "no flag"}',
          got == want, f'set {sorted(got)}')

for pad in arrivals(10):
    tag = f'map 10 pad {pad.quality & 0xFF}'
    w, av = load_world(10)
    hatched, barks = enter(w, bytearray(0x1000), pad)
    check(f'{tag}: nothing drunk — all four placed potions stand',
          all(len(potions(w, f)) == 1 for f in (1, 2, 5, 7)))
    g = bytearray(0x1000)
    for name in POTION_FLAG.values():
        set_flag(g, name)
    w, av = load_world(10)
    hatched, barks = enter(w, g, pad)
    check(f'{tag}: both drunk — protection and invisibility are gone',
          not potions(w, 5) and not potions(w, 7), f'hatched {hatched}')
    check(f'{tag}: ...health and mana are back on the shelf',
          all(len(potions(w, f)) == 1 for f in RESTOCK))
    check(f'{tag}: ...all three Tiny Tars are still there',
          len(potions(w, TINY_TAR)) == 3)
    check(f'{tag}: ...and the re-apply is silent', not barks, str(barks))
    w, av = load_world(10, carry=[(SHAPE_POTION, 5, 0),
                                  (SHAPE_POTION, 7, 0)])
    enter(w, bytearray(0x1000), pad)
    held = [it for it in w.items.values() if it.parent == av.objid]
    check(f'{tag}: both carried undrunk — none back on the ground, the '
          'carried ones untouched',
          not live(w, lambda it: it.shape == SHAPE_POTION
                   and it.frame in POTION_FLAG)
          and len(held) == 2 and not any(it.destroyed for it in held))
for f, name in POTION_FLAG.items():
    g = bytearray(0x1000)
    set_flag(g, name)
    w, av = load_world(10)
    enter(w, g, arrivals(10)[0])
    check(f'only {name} set — only frame {f} removed',
          all(bool(potions(w, k)) == (k != f) for k in (1, 2, 5, 7)))

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

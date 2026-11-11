#!/usr/bin/env python3
"""
test_uc_shades.py — Headless scene proof for quest steps 14-15, the Sacred
Circle shield-restoration ceremony, driven through the engine-faithful
simulator (u8c_sim.py) against the BUILT shared/build/EUSECODE.FLX.

Drives EggShades::hatch() (event 7, this = the trigger egg placed by
build_map_10.build_sacred_circle(), quality 294 -> class 1445). This is THE
scene that clears avatarPoisoned — the only cure in the corpus — so with the
poison re-enabled (2026-07-27) it is quest-critical from step 8 onward.

The lv-patched/SHADES.UNK copy retargets the six 1994 teleport coordinates
to our Map 10 and reorders the hatch head (latch check first, shield check
before any NPC teleport). This test pins all of that:

  P1 success path: elders teleport IN to the patched circle coordinates,
     three ask menus, halves consumed, the restored shield created as
     shape 879 (TypeSacredShield) quality 83 and handed into the backpack,
     shieldFixed set, avatarPoisoned CLEARED, elders sent home to their
     village spots, and the egg latched via setEggXRange(1).
  P2 no shield halves: NOBODY teleports (the reorder's point), Ezrekal
     barks the bring-the-shield line, no latch.
  P3 post-success re-entry (XRange=1): hatch is silent — no menus, no
     teleports, no misleading bark.
  P4 angry path ("You two are insufferable!"): everyone goes home,
     nothing is granted, and the egg is NOT latched — the ceremony can be
     retried. This is the documented playability decision: doneShades is
     an undeclared 1994 flag (write = no-op) and stays that way on
     purpose, because declaring it would make this path a permanent
     soft-lock of the cure and the endgame.
  P6 the ceremony and the altar agree: the very item P1's ceremony
     created satisfies EggAOCeremony's search (godsFree set), the altar
     moves it out of the backpack onto its top face, and class 879's
     look() (lv-new/SACSHLD.UNK) names it "Ceremonial Shield of the
     Ancients Ones" there.
  P7 the altar refuses the look-alikes: Pagan's own 828 (quality 0,
     still "Zealan ceremonial shield ") and the old 539 frame 2, and
     leaves them in the pack.
  P8 save compatibility: a save made before 2026-10-17 carries the Shield
     as 828 quality 83; the altar accepts it and pops it to the same spot,
     and lv-new/AORTA.UNK (class 828) still names it.
  P9 save compatibility, the halves: a save made before 2026-10-17 carries
     them as retired 870 (2026-10-11..17) or retail 539 (before), frame 0
     quality 81 and frame 1 quality 82; SHADES falls back to each and the
     ceremony runs to the 879 Shield. One new and one old half also do.
  P10 Pagan's own 539 shields (quality 0, frames 0 and 1) are not halves:
     the scene is refused with the bring-the-shield bark, nothing consumed.

Known / deliberately-simplified behavior (see lv-patched/SHADES.UNK):
  - realDoAnim/turnToFace/flameBlast/killProcess-with-PT_* are the known
    corpus-wide no-op gaps (cosmetic choreography only);
  - squabble() runs one round, not four (H1 process-block semantics);
  - the invisible shield anchor create(TypeAOFrizbee, 4) references a
    frame shape 539 does not have — the engine's item sorter skips
    invalid frames, which reproduces the 1994 "invisible" intent.
"""

import json
import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8c_sim import UCSim, SimWorld  # noqa: E402
from u8c_symbols import TYPE_SHAPES  # noqa: E402

MANIFEST = os.path.join(BASE_DIR, 'shared', 'build', 'lv_manifest.json')
_m = json.load(open(MANIFEST))
CLS = _m['classes']
FLAGS = {k: v['bit'] for k, v in _m['global_flags'].items()}

EGGSHADES = CLS['EGGSHADES']                     # 1445 (0x5A5)
HATCH_EVENT = 7                                  # Egg::hatch
EGG_QUALITY = EGGSHADES - 0x47F                  # 294 — UnkEgg quality convention
SHAPE_EGG = 73
SHIELD_SHAPE = TYPE_SHAPES['TypeAOFrizbee']      # 878 — the two halves (1994 art)
RETAIL_SHIELD = 539                             # the halves' shape until 2026-10-11
RETIRED_HALVES = 870                            # the halves 2026-10-11..17 (retired)
HALF_QUALITY = (81, 82)                         # build_map_17 QUALITY_SHIELD_HALF_1/2
# The restored Shield of the Ancients: shape 879, the 1994 art (screen04
# shows it on the sanctum altar; lv_shapes.SHAPE_SACRED_SHIELD_1994, on
# 828's TYPEFLAG row), created by SHADES as TypeSacredShield and marked
# quality 83, which AOSCENE's altar still tests; class 879's look()
# (lv-new/SACSHLD.UNK) names it. Literal on purpose: the decision is the
# shape, and the TYPE_SHAPES entry has to follow it. 2026-10-08..17 it was
# 828 quality 83; Pagan's own 828 (quality 0) is EZREKAL's forgery.
RESTORED_SHAPE = 879
RESTORED_QUALITY = 83
PAGAN_SHIELD = 828                               # TypeAOArtifact (class 828 AORTA)
PAGAN_TEXT = 'Zealan ceremonial shield '         # class 828's look() at quality 0
# Where AOSCENE pops the restored Shield: the Map 18 altar's top face, at
# altar (3127, 8175, 0) + (-16, -8, +16), where screen04 shows it
# (test_uc_eggs.py P5 and map-populator test_paint_cycles.py check it too).
SHIELD_ON_ALTAR = (3111, 8167, 16)
EGGAOCEREMONY = CLS['EGGAOCEREMONY']             # 1447 — the temple altar
LOOK_EVENT = 0
SHADE_SHAPE = TYPE_SHAPES['TypeShades']          # 411 — the ghost shape
SHAPE_AVATAR = 1
EQ_BACKPACK = 6

# NPC objids (= npcnum; placements in build_map_10.py)
ATLI, THORDIS, EZREKAL = 107, 106, 116

# Patched scene coordinates (lv-patched/SHADES.UNK header changes 1 and 7:
# the send-homes are the S1 schedule home points since 2026-10-08)
TP_IN = {ATLI: (20224, 17216, 0), THORDIS: (20672, 17312, 0),
         EZREKAL: (20480, 17472, 0)}
TP_HOME = {ATLI: (19231, 6943, 0), THORDIS: (4415, 7423, 0),
           EZREKAL: (12799, 12543, 0)}

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


def held_by(w, item, holder):
    """True when item sits anywhere inside holder (any container depth)."""
    pid = item.parent
    while pid is not None:
        if pid == holder.objid:
            return True
        pid = w.get(pid).parent if w.get(pid) else None
    return False


def build_fixture(with_halves=True, egg_npcnum=0x88, halves_spec=None):
    """Avatar at the Sacred Circle with (optionally) both shield halves in
    a backpack, the three elders somewhere else on Map 10, and the
    EggShades trigger as placed by build_sacred_circle(). `halves_spec`,
    a list of (shape, frame, quality), replaces the default 878 pair."""
    w = SimWorld()
    avatar = w.add(SHAPE_AVATAR, objid=1, x=20480, y=17100, z=0)
    pack = w.add(529, quality=0)
    w.put_in_container(pack, avatar)
    avatar.equipment[EQ_BACKPACK] = pack.objid
    halves = []
    if with_halves:
        if halves_spec is None:
            halves_spec = [(SHIELD_SHAPE, fr, HALF_QUALITY[fr]) for fr in (0, 1)]
        for shape, fr, q in halves_spec:
            h = w.add(shape, frame=fr, quality=q)
            w.put_in_container(h, pack)
            halves.append(h)
    npcs = {n: w.add(SHAPE_AVATAR, objid=n, x=1000 + n, y=1000, z=0)
            for n in (ATLI, THORDIS, EZREKAL)}
    egg = w.add(SHAPE_EGG, quality=EGG_QUALITY, x=20480, y=17152, z=0,
                npcnum=egg_npcnum)
    sim = UCSim(world=w)
    sim.follow_spawns = True
    for f in ('inShadeScene', 'shieldFixed'):
        sim.set_global(FLAGS[f], 1, 0)
    sim.set_global(FLAGS['avatarPoisoned'], 1, 1)   # poisoned coming in
    return w, avatar, halves, npcs, egg, sim


def hatch(sim, egg):
    return sim.run_event(EGGSHADES, 0, egg.objid, event=HATCH_EVENT)


def tps_for(sim, objid):
    return [(t['x'], t['y'], t['z']) for t in sim.teleports
            if t['obj'] == objid]


print('=' * 66)
print(f'driving EggShades::hatch  (class {EGGSHADES} = 0x{EGGSHADES:03X}, '
      f'event {HATCH_EVENT}, egg quality {EGG_QUALITY})')
print('=' * 66)

# ── P1: the full success path ────────────────────────────────────────────
print('P1: both halves in pack — the full ceremony runs, cures the poison')
w, avatar, halves, npcs, egg, sim = build_fixture()
sim.answer_script = ["Let's be reasonable!", 'Yes, Priestess.',
                     'Please, High Priestess.']
hatch(sim, egg)
check('EggShades is the pinned class 1445 (0x5A5)',
      EGGSHADES == 0x5A5, f'got {EGGSHADES}')
for n, name in ((ATLI, 'Atli'), (THORDIS, 'Thordis'), (EZREKAL, 'Ezrekal')):
    check(f'{name} teleported IN to the circle {TP_IN[n]}',
          TP_IN[n] in tps_for(sim, n), f'{sim.teleports}')
check('three ask menus shown and answered', len(sim.asks) == 3,
      f'{[a[0] for a in sim.asks]}')
check('both shield halves consumed',
      all(h.destroyed for h in halves))
check('TypeSacredShield compiles to 879, the 1994 Shield',
      TYPE_SHAPES['TypeSacredShield'] == RESTORED_SHAPE,
      f"TYPE_SHAPES says {TYPE_SHAPES['TypeSacredShield']}")
check('TypeAOArtifact stays 828, Pagan\'s look-alike (ATLI change 5)',
      TYPE_SHAPES['TypeAOArtifact'] == PAGAN_SHIELD,
      f"TYPE_SHAPES says {TYPE_SHAPES['TypeAOArtifact']}")
whole = [it for it in w.items.values()
         if it.shape == RESTORED_SHAPE and not it.destroyed]
check('restored shield (879) exists in the world', len(whole) == 1,
      f'found {len(whole)}')
check('...at frame 0, the only frame 879 has, and quality 83',
      [(it.frame, it.quality) for it in whole] == [(0, RESTORED_QUALITY)],
      f'{[(it.frame, it.quality) for it in whole]}')
check('nothing created as an 828 (the 2026-10-08..17 restored shape)',
      not any(it.shape == PAGAN_SHIELD for it in w.items.values()),
      f'{[(it.shape, it.frame) for it in w.items.values()]}')
check('nothing created as the old 539 frame 2',
      not any(it.shape == RETAIL_SHIELD and it.frame == 2
              for it in w.items.values()),
      f'{[(it.shape, it.frame) for it in w.items.values()]}')
# WHERE it lands. The 1994 line popped the reforged shield at
# `Frizbee1.getX() - 60, ...` twenty lines AFTER Frizbee1.destroy(), so it
# materialised at about (-60,-30,0) and was lost — and it is the artifact
# quest step 17 needs on the temple altar, so the endgame was unreachable.
# lv-patched pops at firePoint1 (captured by the scene while the half lay
# on the ground) + the 1994 offsets. The sim can adjudicate this since
# 2026-07-28: WorldPoint members compile for real (they used to be
# push-first-word-regardless), getPoint passes pointers the engine way,
# and the sim's Item::push/getPoint/pop chain is engine-ported. The
# hand-over lays the halves at (Avatar.x ± 60, Avatar.y + 50); working the
# reforge offsets through puts the shield at (Avatar.x, Avatar.y + 20).
if whole:
    _ws = whole[0]
    check('...at a real world position, not the map origin '
          '(the 1994 destroyed-reference bug)',
          _ws.x > 1000 and _ws.y > 1000,
          f'popped at ({_ws.x},{_ws.y},{_ws.z})')
    check('...exactly where the arithmetic says: (Avatar.x, Avatar.y + 20)',
          (_ws.x, _ws.y) == (avatar.x, avatar.y + 20),
          f'popped at ({_ws.x},{_ws.y}) vs avatar ({avatar.x},{avatar.y})')
    check('...and handed into the backpack at the end of the scene',
          _ws.parent == avatar.equipment[EQ_BACKPACK],
          f'parent={_ws.parent} pack={avatar.equipment[EQ_BACKPACK]}')
check('shieldFixed flag set', sim.get_global(FLAGS['shieldFixed'], 1) == 1)
check('avatarPoisoned CLEARED by the ceremony (the cure)',
      sim.get_global(FLAGS['avatarPoisoned'], 1) == 0)
shade_barks = [t for _o, t in sim.barks if 'shade of Hoskuld' in t]
check('the shades speak (shadeTalk ran)', len(shade_barks) >= 1,
      f'{[t[:40] for _o, t in sim.barks]}')
shades = [it for it in w.items.values() if it.shape == SHADE_SHAPE]
check('shades created as shape 411 frames 0+1 and dismissed again',
      len(shades) == 2 and {s.frame for s in shades} == {0, 1}
      and all(s.destroyed for s in shades),
      f'{[(s.frame, s.destroyed) for s in shades]}')
for n, name in ((ATLI, 'Atli'), (THORDIS, 'Thordis'), (EZREKAL, 'Ezrekal')):
    check(f'{name} sent home to {TP_HOME[n]}',
          TP_HOME[n] in tps_for(sim, n), f'{sim.teleports}')
check('egg latched once-only via setEggXRange(1) (npcnum 0x88 -> 0x18)',
      egg.npcnum == 0x18, f'npcnum=0x{egg.npcnum:02X}')
check('inShadeScene released', sim.get_global(FLAGS['inShadeScene'], 1) == 0)

# ── P2: no shield halves ─────────────────────────────────────────────────
print()
print('P2: no halves — nobody teleports (hatch-order fix), bark only')
w, avatar, halves, npcs, egg, sim = build_fixture(with_halves=False)
sim.answer_script = []
hatch(sim, egg)
check('no teleports at all', len(sim.teleports) == 0, f'{sim.teleports}')
check('no ask menus', len(sim.asks) == 0)
check('Ezrekal barks the bring-the-shield line',
      any('Bring the sacred shield' in t for _o, t in sim.barks),
      f'{sim.barks}')
check('inShadeScene never latched',
      sim.get_global(FLAGS['inShadeScene'], 1) == 0)
check('egg not latched (npcnum still 0x88)', egg.npcnum == 0x88,
      f'npcnum=0x{egg.npcnum:02X}')

# ── P3: post-success re-entry ────────────────────────────────────────────
print()
print('P3: XRange already 1 (post-success) — hatch is silent')
w, avatar, halves, npcs, egg, sim = build_fixture(with_halves=True,
                                                  egg_npcnum=0x18)
sim.answer_script = []
hatch(sim, egg)
check('no teleports', len(sim.teleports) == 0, f'{sim.teleports}')
check('no ask menus', len(sim.asks) == 0)
check('no barks (no misleading bring-the-shield replay)',
      len(sim.barks) == 0, f'{sim.barks}')

# ── P4: the angry path stays retryable ───────────────────────────────────
print()
print('P4: "You two are insufferable!" — everyone leaves, retry stays open')
w, avatar, halves, npcs, egg, sim = build_fixture()
sim.answer_script = ["Can't you two get along!?",
                     'You two are insufferable!']
hatch(sim, egg)
check('elders were teleported in first',
      TP_IN[ATLI] in tps_for(sim, ATLI), f'{sim.teleports}')
for n, name in ((ATLI, 'Atli'), (THORDIS, 'Thordis'), (EZREKAL, 'Ezrekal')):
    check(f'{name} sent home after the insult',
          TP_HOME[n] in tps_for(sim, n), f'{sim.teleports}')
check('nothing granted: shieldFixed still 0',
      sim.get_global(FLAGS['shieldFixed'], 1) == 0)
check('avatarPoisoned still set (no cure on the angry path)',
      sim.get_global(FLAGS['avatarPoisoned'], 1) == 1)
check('halves NOT consumed', not any(h.destroyed for h in halves))
check('egg NOT latched — ceremony retryable (doneShades stays a dead '
      'flag by design)', egg.npcnum == 0x88, f'npcnum=0x{egg.npcnum:02X}')
check('inShadeScene released', sim.get_global(FLAGS['inShadeScene'], 1) == 0)

# ── P5: re-entry while the scene is running ──────────────────────────────
print()
print('P5: inShadeScene already latched — hatch refuses to double-fire')
w, avatar, halves, npcs, egg, sim = build_fixture()
sim.set_global(FLAGS['inShadeScene'], 1, 1)   # scene "in progress"
sim.answer_script = []
hatch(sim, egg)
check('no teleports (guard held)', len(sim.teleports) == 0,
      f'{sim.teleports}')
check('no ask menus', len(sim.asks) == 0)
check('no barks', len(sim.barks) == 0, f'{sim.barks}')
check('halves untouched', not any(h.destroyed for h in halves))


def altar(sim, w):
    """Run EggAOCeremony::hatch (the temple altar, quest step 17) in the
    same world and flag state, with the temple open. Returns the barks it
    added."""
    egg_ao = w.add(SHAPE_EGG, quality=EGGAOCEREMONY - 0x47F,
                   x=3072, y=8320, z=0, npcnum=0x88)
    sim.set_global(FLAGS['templeOpen'], 1, 1)
    sim.set_global(FLAGS['godsFree'], 1, 0)
    before = len(sim.barks)
    sim.run_event(EGGAOCEREMONY, 0, egg_ao.objid, event=HATCH_EVENT)
    return [t for _o, t in sim.barks[before:]]


def look(sim, item):
    """look() the way the engine dispatches it: class = the item's shape
    (item.cpp:1516; a create()d item has npcnum 0, so no npcnum override)."""
    before = len(sim.barks)
    sim.run_event(item.shape, 0, item.objid, event=LOOK_EVENT)
    return [t for _o, t in sim.barks[before:]]


# ── P6: the shield the ceremony makes is the one the altar takes ─────────
print()
print('P6: the ceremony\'s own shield, carried to the altar')
w, avatar, halves, npcs, egg, sim = build_fixture()
sim.answer_script = ["Let's be reasonable!", 'Yes, Priestess.',
                     'Please, High Priestess.']
hatch(sim, egg)
made = [it for it in w.items.values()
        if it.shape == RESTORED_SHAPE and not it.destroyed]
check('the ceremony made exactly one restored shield', len(made) == 1,
      f'found {len(made)}')
check('shieldFixed set by the ceremony itself',
      sim.get_global(FLAGS['shieldFixed'], 1) == 1)
barks = altar(sim, w)
check('the altar accepts it: godsFree SET',
      sim.get_global(FLAGS['godsFree'], 1) == 1, f'{barks}')
check('the artifact-on-altar bark fired',
      any('artifact upon the altar' in t for t in barks), f'{barks}')
if made:
    # ...and then puts it ON the altar (Douglas, 2026-10-09), out of the
    # backpack SHADES handed it into. AOSCENE's search is recursive, so the
    # Shield one container down is the case a real player has.
    shield = made[0]
    check('the restored Shield has left the Avatar and the backpack',
          not held_by(w, shield, avatar), f'parent={shield.parent}')
    check(f'it is a world item on the altar top {SHIELD_ON_ALTAR}',
          shield.parent is None and not shield.ethereal
          and (shield.x, shield.y, shield.z) == SHIELD_ON_ALTAR,
          f'parent={shield.parent} ethereal={shield.ethereal} '
          f'at ({shield.x}, {shield.y}, {shield.z})')
    check('no quality-83 879 is left anywhere in the Avatar\'s containers',
          not any(it.shape == RESTORED_SHAPE and it.quality == RESTORED_QUALITY
                  and held_by(w, it, avatar) for it in w.items.values()))
if made:
    said = look(sim, made[0])
    check('class 879 look() names it "Ceremonial Shield of the Ancients Ones"',
          said == ['Ceremonial Shield of the Ancients Ones'], f'{said}')
check('TYPESACREDSHIELD is pinned to 879, the shape (class = shape, '
      'item.cpp:1516)', CLS.get('TYPESACREDSHIELD') == RESTORED_SHAPE,
      str(CLS.get('TYPESACREDSHIELD')))

# ── P7: look-alikes do not open the temple ───────────────────────────────
print()
print("P7: Pagan's 828 and the old 539 frame 2 are refused at the altar")
for desc, shape, frame, quality, text in (
        ("Pagan's own 828 (quality 0)", PAGAN_SHIELD, 0, 0, PAGAN_TEXT),
        ('the old restored shield, 539 frame 2', RETAIL_SHIELD, 2, 0, None)):
    w, avatar, halves, npcs, egg, sim = build_fixture(with_halves=False)
    fake = w.add(shape, frame=frame, quality=quality)
    w.put_in_container(fake, w.items[avatar.equipment[EQ_BACKPACK]])
    sim.set_global(FLAGS['shieldFixed'], 1, 1)
    barks = altar(sim, w)
    check(f'{desc}: godsFree NOT set',
          sim.get_global(FLAGS['godsFree'], 1) == 0, f'{barks}')
    check(f'{desc}: the lack-the-artifact bark fired',
          any('lack the artifact' in t for t in barks), f'{barks}')
    check(f'{desc}: stays in the backpack (only the real Shield moves)',
          fake.parent == avatar.equipment[EQ_BACKPACK],
          f'parent={fake.parent} at ({fake.x}, {fake.y}, {fake.z})')
    if text is not None:
        said = look(sim, fake)
        check(f'{desc}: keeps its retail look() text {text!r}',
              said == [text], f'{said}')

# ── P8: save compatibility, the 2026-10-08..17 Shield (828 quality 83) ───
print()
print('P8: a pre-2026-10-17 save\'s Shield (828 q83) is accepted at the altar')
w, avatar, halves, npcs, egg, sim = build_fixture(with_halves=False)
legacy = w.add(PAGAN_SHIELD, frame=0, quality=RESTORED_QUALITY)
w.put_in_container(legacy, w.items[avatar.equipment[EQ_BACKPACK]])
sim.set_global(FLAGS['shieldFixed'], 1, 1)
barks = altar(sim, w)
check('legacy 828 q83: godsFree SET',
      sim.get_global(FLAGS['godsFree'], 1) == 1, f'{barks}')
check('legacy 828 q83: the artifact-on-altar bark fired',
      any('artifact upon the altar' in t for t in barks), f'{barks}')
check(f'legacy 828 q83: popped to the altar top {SHIELD_ON_ALTAR}',
      legacy.parent is None and not legacy.ethereal
      and (legacy.x, legacy.y, legacy.z) == SHIELD_ON_ALTAR,
      f'parent={legacy.parent} at ({legacy.x}, {legacy.y}, {legacy.z})')
said = look(sim, legacy)
check('legacy 828 q83: class 828 (lv-new/AORTA.UNK) still names it '
      '"Ceremonial Shield of the Ancients Ones"',
      said == ['Ceremonial Shield of the Ancients Ones'], f'{said}')

# ── P9: save compatibility, the halves (870 and 539, quality 81/82) ──────
print()
print('P9: a pre-2026-10-17 save\'s halves (870 or 539, q81/q82) run the '
      'ceremony')
for desc, spec in (
        ('retired 870 halves', [(RETIRED_HALVES, f, HALF_QUALITY[f])
                                for f in (0, 1)]),
        ('retail 539 halves', [(RETAIL_SHIELD, f, HALF_QUALITY[f])
                               for f in (0, 1)]),
        ('878 sun half + 870 eye half', [(SHIELD_SHAPE, 0, HALF_QUALITY[0]),
                                         (RETIRED_HALVES, 1, HALF_QUALITY[1])]),
        ('539 sun half + 878 eye half', [(RETAIL_SHIELD, 0, HALF_QUALITY[0]),
                                         (SHIELD_SHAPE, 1, HALF_QUALITY[1])])):
    w, avatar, halves, npcs, egg, sim = build_fixture(halves_spec=spec)
    sim.answer_script = ["Let's be reasonable!", 'Yes, Priestess.',
                         'Please, High Priestess.']
    hatch(sim, egg)
    check(f'{desc}: no bring-the-shield bark',
          not any('Bring the sacred shield' in t for _o, t in sim.barks),
          f'{[t[:40] for _o, t in sim.barks]}')
    check(f'{desc}: elders teleported in', TP_IN[EZREKAL] in tps_for(sim, EZREKAL),
          f'{sim.teleports}')
    check(f'{desc}: both halves consumed', all(h.destroyed for h in halves),
          f'{[(h.shape, h.frame, h.destroyed) for h in halves]}')
    whole = [it for it in w.items.values()
             if it.shape == RESTORED_SHAPE and not it.destroyed]
    check(f'{desc}: one restored Shield, 879 q83, in the backpack',
          [(it.quality, it.parent) for it in whole]
          == [(RESTORED_QUALITY, avatar.equipment[EQ_BACKPACK])],
          f'{[(it.quality, it.parent) for it in whole]}')
    check(f'{desc}: shieldFixed set, avatarPoisoned cleared',
          sim.get_global(FLAGS['shieldFixed'], 1) == 1
          and sim.get_global(FLAGS['avatarPoisoned'], 1) == 0)

# ── P10: Pagan's own 539s are not halves ─────────────────────────────────
print()
print("P10: Pagan's 539 shields (quality 0, frames 0/1) do not open the scene")
w, avatar, halves, npcs, egg, sim = build_fixture(
    halves_spec=[(RETAIL_SHIELD, f, 0) for f in (0, 1)])
sim.answer_script = []
hatch(sim, egg)
check('539 q0: Ezrekal barks the bring-the-shield line',
      any('Bring the sacred shield' in t for _o, t in sim.barks),
      f'{sim.barks}')
check('539 q0: no teleports, no ask menu',
      not sim.teleports and not sim.asks, f'{sim.teleports}')
check('539 q0: the shields stay in the pack',
      not any(h.destroyed for h in halves)
      and all(h.parent == avatar.equipment[EQ_BACKPACK] for h in halves))
check('539 q0: shieldFixed still 0',
      sim.get_global(FLAGS['shieldFixed'], 1) == 0)

print()
print(f'OK: {passed} passed, {failed} failed' if failed == 0
      else f'FAILED: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

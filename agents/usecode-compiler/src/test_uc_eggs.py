#!/usr/bin/env python3
"""
test_uc_eggs.py — Headless gate-chain proof for the three event eggs wired
in the 2026-07-27 egg-queue pass, driven through the engine-faithful
simulator (u8c_sim.py) against the BUILT shared/build/EUSECODE.FLX:

  EggCloudCliffs (1448, quality 297, Map 13)  — quest step 13
  EggAOCeremony  (1447, quality 296, Map 18)  — quest step 17
  EggEndgame     (1450, quality 299, Map 10)  — quest step 18

These are gate chains rather than set-pieces: what matters is that each
hatch fires exactly when its preconditions hold and is silent otherwise,
and that the flags they write are the ones the next link reads
(climbedCliffs -> five NPCs' dialogue tiers; godsFree -> EggEndgame).

UPDATED 2026-07-27: `templeOpen` NOW HAS A WRITER. It was read in 23
line-sites across the 1994 corpus and assigned in zero — the temple-opening
mechanism was never authored, and the 1994 writer ducked it in dialogue
(EZREKAL: "How managed it did you? How...oh, never mind"). Per DD-005 the
mechanism is Hrodny's Tiny Tar shrink, and the flag is now written by
EggTempleEntry (1456, quality 305, lv-new/TEMPLENT.UNK) sitting on the
sanctum side of the Tiny Tar crack on Map 18.

The egg deliberately gates on nothing. The gate is GEOMETRY: a 32-unit
aperture that the engine's canExistAt() footpad test admits for the
shrunken Avatar (shape 867, 32x32) and refuses for the normal one
(shape 1, 64x64). That half is proved by map_walkability's Map 18 suite,
which floods the map at both body widths; this file proves the usecode
half. P4 still checks AOSCENE stays silent while the flag is clear — that
is now an ordinary ordering assertion, not a pinned gap.
"""

import json
import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8c_sim import UCSim, SimWorld, SimError  # noqa: E402
from u8c_symbols import TYPE_SHAPES  # noqa: E402

MANIFEST = os.path.join(BASE_DIR, 'shared', 'build', 'lv_manifest.json')
_m = json.load(open(MANIFEST))
CLS = _m['classes']
FLAGS = {k: v['bit'] for k, v in _m['global_flags'].items()}

CLCLIMB = CLS['EGGCLOUDCLIFFS']    # 1448
AOSCENE = CLS['EGGAOCEREMONY']     # 1447
ENDGAME = CLS['EGGENDGAME']        # 1450
TEMPLENT = CLS['EGGTEMPLEENTRY']   # 1456 — the templeOpen writer (DD-005)
CRACKHINT = CLS['EGGCRACKHINT']    # 1457 — the 'far too narrow' bark
HATCH = 7
SHAPE_EGG = 73
SHAPE_AVATAR = 1
CLIFF_KEY = TYPE_SHAPES['TypeCliffKey']      # 82
# Tyorvi's give() stamps the Key to the Clouds with this quality and
# CLCLIMB's handholds accept only it (lv-patched/TYORVI.UNK T6,
# lv-new/CLCLIMB.UNK). Shape 82 is every key in the game; quality is the
# only thing that tells his apart. The retail qualities it must avoid, and
# why 170, are in CLCLIMB.UNK's header; P1d below re-checks the maps.
CLIFF_KEY_QUALITY = 170
# Keys a player can carry into the Vale that are NOT his: a retail key
# blank (quality 0, retail NONFIXED Map 40 and the q0 keys of cp26), the
# Map 8 door key (build_map_08 DOOR_LOCK_ID 99, the "Pagan q99 key" of
# docs/playtest-2026-10-10-replies.md finding 2) and Hrodny's chest key
# (build_map_10 HRODNY_KEY_ID 20).
OTHER_KEYS = (0, 20, 99)
AO_ARTIFACT = TYPE_SHAPES['TypeSacredShield']  # 879, the restored Shield
AO_QUALITY = 83     # SHADES setQ()s it; AOSCENE still tests this quality
# Where AOSCENE pops the Shield: the top face of the Map 18 altar (550 at
# (3127, 8175, 0), 64x128x16, top z 16), at altar + (-16, -8, +16) where
# screen04 shows it. agents/map-populator/src/
# test_paint_cycles.py checks the same three numbers, read from
# AOSCENE.UNK, against build_map_18's altar and the depth sort.
SHIELD_ON_ALTAR = (3111, 8167, 16)
# The pan's stops: each god's (x, y) with camera z = god z (16) + 20.
GOD_TIMYRA, GOD_FELICITAR, GOD_DOLORAS = (3039, 8415), (2783, 8031), (3039, 7903)
CAMERA_Z = 36
TYPE_BAG = TYPE_SHAPES['TypeBag']            # 637
TYPE_REAGENT = TYPE_SHAPES['TypeReagent']    # 395

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


def fixture(classid, quality, carry=None, flags=None, carry_frame=0,
            carry_quality=0):
    """Avatar with an optional carried item, plus the trigger egg."""
    w = SimWorld()
    avatar = w.add(SHAPE_AVATAR, objid=1, x=4096, y=11264, z=0)
    carried = None
    if carry is not None:
        carried = w.add(carry, frame=carry_frame, quality=carry_quality)
        w.put_in_container(carried, avatar)
    egg = w.add(SHAPE_EGG, quality=quality, x=4096, y=11264, z=0, npcnum=0x88)
    sim = UCSim(world=w)
    sim.follow_spawns = True
    for name in ('climbedCliffs', 'attemptedCliffs', 'godsFree', 'templeOpen',
                 'shieldFixed', 'endgameStarted', 'hasBag'):
        sim.set_global(FLAGS[name], 1, 0)
    for name, val in (flags or {}).items():
        sim.set_global(FLAGS[name], 1, val)
    return w, avatar, carried, egg, sim


def run(sim, egg, classid):
    return sim.run_event(classid, 0, egg.objid, event=HATCH)


print('=' * 68)
print('EGG-QUEUE gate chains  (CLCLIMB 1448 / AOSCENE 1447 / ENDGAME 1450)')
print('=' * 68)

# ── EggCloudCliffs ───────────────────────────────────────────────────────
print('P1: CLCLIMB with the Key to the Clouds — the climb succeeds')
w, av, key, egg, sim = fixture(CLCLIMB, 297, carry=CLIFF_KEY,
                               carry_quality=CLIFF_KEY_QUALITY)
run(sim, egg, CLCLIMB)
check('EggCloudCliffs is the pinned class 1448', CLCLIMB == 1448)
check('climbedCliffs set (unlocks 5 NPCs\' post-climb dialogue)',
      sim.get_global(FLAGS['climbedCliffs'], 1) == 1)
check('attemptedCliffs set', sim.get_global(FLAGS['attemptedCliffs'], 1) == 1)
check('the handholds bark fired',
      any('handholds' in t for _o, t in sim.barks), f'{sim.barks}')

print()
print('P2: CLCLIMB with no key — hint only, no progress')
w, av, key, egg, sim = fixture(CLCLIMB, 297, carry=None)
run(sim, egg, CLCLIMB)
check('climbedCliffs NOT set',
      sim.get_global(FLAGS['climbedCliffs'], 1) == 0)
check('attemptedCliffs set (first-visit hint recorded)',
      sim.get_global(FLAGS['attemptedCliffs'], 1) == 1)
check('the "require some sort of key" hint fired',
      any('key or token' in t for _o, t in sim.barks), f'{sim.barks}')

print()
print('P3: CLCLIMB replay guard — already climbed, hatch is silent')
w, av, key, egg, sim = fixture(CLCLIMB, 297, carry=CLIFF_KEY,
                               carry_quality=CLIFF_KEY_QUALITY,
                               flags={'climbedCliffs': 1})
run(sim, egg, CLCLIMB)
check('no barks on replay', len(sim.barks) == 0, f'{sim.barks}')

# docs/playtest-2026-10-10-replies.md finding 2: the handholds took any
# shape-82 key, so a Pagan q99 key climbed before Tyorvi gave his.
for _q in OTHER_KEYS:
    print()
    print(f'P1b: CLCLIMB with a quality-{_q} key that is not Tyorvi\'s — '
          'refused')
    w, av, key, egg, sim = fixture(CLCLIMB, 297, carry=CLIFF_KEY,
                                   carry_quality=_q)
    run(sim, egg, CLCLIMB)
    check(f'q{_q} key: climbedCliffs NOT set',
          sim.get_global(FLAGS['climbedCliffs'], 1) == 0)
    check(f'q{_q} key: the "key or token" hint fired, not the handholds',
          any('key or token' in t for _o, t in sim.barks)
          and not any('handholds hold firm' in t for _o, t in sim.barks),
          f'{sim.barks}')

print()
print('P1c: CLCLIMB with a q99 key AND Tyorvi\'s key in the pack — climbs')
w, av, key, egg, sim = fixture(CLCLIMB, 297, carry=CLIFF_KEY,
                               carry_quality=99)
_bag = w.add(TYPE_BAG)
w.put_in_container(_bag, av)
w.put_in_container(w.add(CLIFF_KEY, quality=CLIFF_KEY_QUALITY), _bag)
run(sim, egg, CLCLIMB)
check('a foreign key ahead of his in the pack does not hide his',
      sim.get_global(FLAGS['climbedCliffs'], 1) == 1, f'{sim.barks}')

print()
print(f'P1d: no key anywhere in the game data shares quality '
      f'{CLIFF_KEY_QUALITY}')
# The retail map data a player walks through (FIXED.DAT.bak, and U8SAVE.000's
# NONFIXED.DAT, where nearly every retail key lives) and the built
# FIXED.DAT the LV builders write. A key there with his quality would climb.
sys.path.insert(0, os.path.join(BASE_DIR, 'agents', 'map-populator', 'src'))
from u8_map import MapArchive  # noqa: E402
_STATIC = os.path.join(BASE_DIR, 'shared', 'data', 'u8-install')
_sources = [('retail FIXED.DAT', os.path.join(_STATIC, 'STATIC',
                                               'FIXED.DAT.bak')),
            ('built FIXED.DAT', os.path.join(BASE_DIR, 'shared', 'build',
                                             'FIXED.DAT'))]
_save = os.path.join(_STATIC, 'SAVEGAME', 'U8SAVE.000')
_tmp = None
if os.path.exists(_save):
    import tempfile
    from scan_npc_slots import read_u8save  # noqa: E402
    _tmp = tempfile.TemporaryDirectory()
    _nf = os.path.join(_tmp.name, 'NONFIXED.DAT')
    with open(_nf, 'wb') as _fh:
        _fh.write(read_u8save(_save)['NONFIXED.DAT'])
    _sources.append(('retail NONFIXED.DAT', _nf))
for _label, _path in _sources:
    if not os.path.exists(_path):
        print(f'  SKIP  {_label}: {_path} missing')
        continue
    _arch = MapArchive(_path)
    _keys = [(m, it.quality) for m in _arch.non_empty_maps()
             for it in _arch.get_map_items(m) if it.shape == CLIFF_KEY]
    check(f'{_label}: {len(_keys)} keys, none of quality '
          f'{CLIFF_KEY_QUALITY}',
          bool(_keys) and all(q != CLIFF_KEY_QUALITY for _m, q in _keys),
          str([k for k in _keys if k[1] == CLIFF_KEY_QUALITY]))
if _tmp is not None:
    _tmp.cleanup()

# ── EggAOCeremony ────────────────────────────────────────────────────────
print()
print('P4: AOSCENE with templeOpen CLEAR — silent (ordering: you must get in first)')
w, av, art, egg, sim = fixture(AOSCENE, 296, carry=AO_ARTIFACT,
                               carry_quality=AO_QUALITY,
                               flags={'shieldFixed': 1})
run(sim, egg, AOSCENE)
check('godsFree NOT set', sim.get_global(FLAGS['godsFree'], 1) == 0)
check('no barks — the scene never starts', len(sim.barks) == 0, f'{sim.barks}')
check('templeOpen still 0 (AOSCENE must not open the temple itself)',
      sim.get_global(FLAGS['templeOpen'], 1) == 0)

# ── EggTempleEntry: the writer DD-005 added ──────────────────────────────
print()
print('P4b: TEMPLENT past the crack — writes templeOpen, the missing link')
w, av, _c, egg, sim = fixture(TEMPLENT, 305)
run(sim, egg, TEMPLENT)
check('EggTempleEntry is the pinned class 1456', TEMPLENT == 1456)
check('templeOpen SET — the flag 23 corpus read-sites wait on',
      sim.get_global(FLAGS['templeOpen'], 1) == 1)
check('the "I am through" bark fired',
      any('I am through' in t for _o, t in sim.barks), f'{sim.barks}')


# The breach (2026-09-26): both classes destroy exactly the wall records
# build_map_18 tags BREACH_QUALITY, shape 15 or 47, and nothing else.
BREACH_Q = 307
WALL_PIECE = TYPE_SHAPES['TypeTempleWallPiece']   # 15
WALL_STUB = TYPE_SHAPES['TypeTempleWallStub']     # 47


def breach_world(w, egg):
    """Two tagged records and three decoys near the egg."""
    ex, ey = egg.x, egg.y
    tagged = [w.add(WALL_PIECE, quality=BREACH_Q, x=ex - 48, y=ey + 96, z=0),
              w.add(WALL_STUB, quality=BREACH_Q, x=ex - 47, y=ey + 96, z=0)]
    decoys = [w.add(WALL_PIECE, quality=0, x=ex + 144, y=ey + 96, z=0),
              w.add(WALL_STUB, quality=0, x=ex - 175, y=ey + 96, z=0),
              w.add(66, quality=BREACH_Q, x=ex, y=ey + 400, z=0)]
    return tagged, decoys


print()
print('P4b2: TEMPLENT opens the breach on the first hatch')
w, av, _c, egg, sim = fixture(TEMPLENT, 305)
tagged, decoys = breach_world(w, egg)
run(sim, egg, TEMPLENT)
check('both tagged wall records destroyed',
      all(t.destroyed for t in tagged), str([t.destroyed for t in tagged]))
check('untagged walls and a tagged non-wall shape left alone',
      not any(d.destroyed for d in decoys), str([d.destroyed for d in decoys]))
check('the breach bark fired',
      any('split stone groans' in t for _o, t in sim.barks), f'{sim.barks}')

print()
print('P4c: TEMPLENT replay — does not re-announce, still reopens the breach')
w, av, _c, egg, sim = fixture(TEMPLENT, 305, flags={'templeOpen': 1})
tagged, decoys = breach_world(w, egg)
run(sim, egg, TEMPLENT)
check('no barks on replay', len(sim.barks) == 0, f'{sim.barks}')
check('the tagged wall records destroyed on replay (map switch reseals)',
      all(t.destroyed for t in tagged), str([t.destroyed for t in tagged]))

# ── EggCrackHint: making the crack a fair puzzle ─────────────────────────
print()
print('P4d: CRACKHINT at the wall — observation only, no spoiler')
w, av, _c, egg, sim = fixture(CRACKHINT, 306)
run(sim, egg, CRACKHINT)
check('EggCrackHint is the pinned class 1457', CRACKHINT == 1457)
check('the "no wider than my hand" observation fired',
      any('no wider than my hand' in t for _o, t in sim.barks), f'{sim.barks}')
check('no potion hint when the player has not found the chest yet',
      not any('Hrodny' in t for _o, t in sim.barks), f'{sim.barks}')
# Option C of the 2026-10-07 "lining up on the crack" item: the hint says
# where the 32-unit strip is — hard against the pale shape-47 stub.
check('the hint says where the crack is (beside the pale block)',
      any('east side of the pale' in t for _o, t in sim.barks), f'{sim.barks}')

print()
print('P4e: CRACKHINT carrying a frame-8 Tiny Tar — the nudge appears')
w, av, _c, egg, sim = fixture(CRACKHINT, 306,
                              carry=TYPE_SHAPES['TypePotion'], carry_frame=8)
run(sim, egg, CRACKHINT)
check('the Hrodny-potions nudge fired',
      any('Hrodny' in t for _o, t in sim.barks), f'{sim.barks}')

print()
print('P4f: CRACKHINT after getting through — silent, reopens the breach')
w, av, _c, egg, sim = fixture(CRACKHINT, 306, flags={'templeOpen': 1})
tagged, decoys = breach_world(w, egg)
run(sim, egg, CRACKHINT)
check('no barks once templeOpen is set', len(sim.barks) == 0, f'{sim.barks}')
check('the tagged wall records destroyed',
      all(t.destroyed for t in tagged), str([t.destroyed for t in tagged]))
check('untagged walls and a tagged non-wall shape left alone',
      not any(d.destroyed for d in decoys), str([d.destroyed for d in decoys]))

print()
print('P4g: CRACKHINT, the doorway egg (y < 5500) before templeOpen — silent')
w, av, _c, egg, sim = fixture(CRACKHINT, 306)
egg.y = 4800
run(sim, egg, CRACKHINT)
check('no hint from the doorway egg', len(sim.barks) == 0, f'{sim.barks}')

print()
print('P4h: CRACKHINT re-hatched (the regrow): the observation does not repeat')
w, av, _c, egg, sim = fixture(CRACKHINT, 306)
run(sim, egg, CRACKHINT)
first = len(sim.barks)
run(sim, egg, CRACKHINT)
check('crackHintGiven SET by the first hatch',
      sim.get_global(FLAGS['crackHintGiven'], 1) == 1)
check('the second hatch adds no bark', len(sim.barks) == first,
      f'{sim.barks}')

print()
print('P4i: CRACKHINT, hint already given, now carrying a Tiny Tar: the nudge')
print('     still fires (the guard covers the observation alone)')
w, av, _c, egg, sim = fixture(CRACKHINT, 306, flags={'crackHintGiven': 1},
                              carry=TYPE_SHAPES['TypePotion'], carry_frame=8)
run(sim, egg, CRACKHINT)
check('the Hrodny-potions nudge fired',
      any('Hrodny' in t for _o, t in sim.barks), f'{sim.barks}')
check('the observation did not repeat',
      not any('no wider than my hand' in t for _o, t in sim.barks),
      f'{sim.barks}')
check('the where-to-stand line repeats for the potion carrier',
      any('east side of the pale' in t for _o, t in sim.barks), f'{sim.barks}')

print()
print('P4j: CRACKHINT carrying all three of Hrodny\'s potions: one nudge')
# docs/playtest-2026-10-03-batch-merge.md finding 7: the bark sat inside
# the potion search and played once per potion, about 40 s of one line.
w, av, _c, egg, sim = fixture(CRACKHINT, 306, flags={'crackHintGiven': 1},
                              carry=TYPE_SHAPES['TypePotion'], carry_frame=8)
for _ in range(2):
    extra = w.add(TYPE_SHAPES['TypePotion'], frame=8)
    w.put_in_container(extra, av)
run(sim, egg, CRACKHINT)
nudges = [t for _o, t in sim.barks if 'Hrodny' in t]
check('three potions carried, the nudge plays exactly once',
      len(nudges) == 1, f'{len(nudges)}: {sim.barks}')

print()
print('P5: AOSCENE with templeOpen forced — the ceremony runs, gods freed')
w, av, art, egg, sim = fixture(AOSCENE, 296, carry=AO_ARTIFACT,
                               carry_quality=AO_QUALITY,
                               flags={'shieldFixed': 1, 'templeOpen': 1})
run(sim, egg, AOSCENE)
check('godsFree SET (the flag EggEndgame reads)',
      sim.get_global(FLAGS['godsFree'], 1) == 1)
check('the artifact-on-altar bark fired',
      any('artifact upon the altar' in t for _o, t in sim.barks),
      f'{sim.barks}')
check('the Ancient Ones are freed bark fired',
      any('Ancient Ones are free' in t for _o, t in sim.barks))

# The Shield goes ON the altar (Douglas, 2026-10-09): AOSCENE push()es the
# quality-83 879 out of the pack and pop()s it to the altar's top face, as
# the bark says. Before, it stayed in the pack.
check('the Shield has left the Avatar\'s containers',
      not held_by(w, art, av), f'parent={art.parent}')
check(f'the Shield is a world item on the altar top {SHIELD_ON_ALTAR}',
      art.parent is None and not art.ethereal and not art.destroyed
      and (art.x, art.y, art.z) == SHIELD_ON_ALTAR,
      f'parent={art.parent} ethereal={art.ethereal} '
      f'at ({art.x}, {art.y}, {art.z})')
check('nothing is left in the ethereal void', not w.ethereal_stack,
      f'{w.ethereal_stack}')
_seq = [n for n, _b, _r in sim.intrinsic_log
        if n in ('Item::push', 'Item::pop', 'Item::bark')
        or n.startswith('Camera::')]
check('it moves just before the "artifact upon the altar" bark, '
      'before the pan',
      _seq[:3] == ['Item::push', 'Item::pop', 'Item::bark'], f'{_seq[:5]}')

# ── The ceremony's camera pan ────────────────────────────────────────────
# In screen04 all three gods fit one frame; the pan still leaves the Avatar
# and stops on each god so each shatter starts with the camera on her.
# These read the sim's intrinsic_log, which records the real calli args,
# so they check the sequence the engine would execute.
cam = [(n.split('::')[-1], b) for n, b in
       [(n, b) for n, b, _r in sim.intrinsic_log] if n.startswith('Camera::')]
camseq = [n for n, _b in cam]
fades = [n for n, _b, _r in sim.intrinsic_log if n.startswith('Fade')]


def _xy(buf):
    return (buf[0] | (buf[1] << 8), buf[2] | (buf[3] << 8))


check('the camera detaches from the Avatar before it pans',
      camseq[:1] == ['setCenterOn'] and cam[0][1] == b'\x00\x00',
      f'{camseq[:2]}')

# THE ONE THAT MATTERS. A finished scrollTo parks a DETACHED camera over its
# destination (camera_process.cpp: SetCameraProcess(nullptr) on completion),
# so a scene that forgets this leaves the Avatar frozen off the fast area
# with every NPC strike missing -- the shipped Sacred Circle bug in
# .claude/skills/playtest/traps.md.
check('the LAST camera call re-attaches to the Avatar (objid 1)',
      camseq[-1] == 'setCenterOn' and cam[-1][1] == b'\x01\x00',
      f'{camseq[-1]} {cam[-1][1].hex()}')

# Cover order: Timyra, Felicitar, Doloras.
stops = [_xy(b) for n, b in cam if n in ('move_to', 'scrollTo')]
check(f'the pan opens on Timyra {GOD_TIMYRA}, instantly (move_to, not a scroll)',
      camseq[1] == 'move_to' and stops[0] == GOD_TIMYRA, f'{camseq[1]} {stops[:1]}')
check(f'it then scrolls Felicitar {GOD_FELICITAR} -> Doloras {GOD_DOLORAS}, '
      'the cover order',
      stops[1:3] == [GOD_FELICITAR, GOD_DOLORAS], f'{stops[1:3]}')
_zs = [b[4] | (b[5] << 8) for n, b in cam if n in ('move_to', 'scrollTo')]
check(f'each god stop is at camera z {CAMERA_Z} (god z 16 + 20)',
      _zs[:3] == [CAMERA_Z] * 3, f'{_zs[:3]}')
check('and scrolls back to the Avatar before re-attaching',
      stops[3] == (av.x, av.y), f'{stops[3]} vs ({av.x}, {av.y})')

# The cut away from the Avatar has to happen under the white, or the player
# sees the camera teleport.
check('the cut to Timyra happens between FadeToWhite and FadeFromWhite',
      fades == ['FadeToWhite', 'FadeFromWhite'] and
      [n for n, _b, _r in sim.intrinsic_log
       if n.startswith('Fade') or n == 'Camera::move_to'] ==
      ['FadeToWhite', 'Camera::move_to', 'FadeFromWhite'],
      f'{fades}')

# Camera::getX/getY assert GAME_IS_CRUSADER and would abort under U8.
check('no Camera::getX/getY (both assert GAME_IS_CRUSADER)',
      not any(n in ('getX', 'getY') for n in camseq), f'{camseq}')

print()
print('P6: AOSCENE without the restored shield — refused with a hint')
w, av, art, egg, sim = fixture(AOSCENE, 296, carry=AO_ARTIFACT,
                               carry_quality=AO_QUALITY,
                               flags={'templeOpen': 1})
run(sim, egg, AOSCENE)
check('godsFree NOT set', sim.get_global(FLAGS['godsFree'], 1) == 0)
check('"Shield must be restored" hint fired',
      any('must be restored' in t for _o, t in sim.barks), f'{sim.barks}')

print()
print('P7: AOSCENE with no artifact carried — refused')
w, av, art, egg, sim = fixture(AOSCENE, 296, carry=None,
                               flags={'templeOpen': 1, 'shieldFixed': 1})
run(sim, egg, AOSCENE)
check('godsFree NOT set', sim.get_global(FLAGS['godsFree'], 1) == 0)
check('"I lack the artifact" refusal fired',
      any('lack the artifact' in t for _o, t in sim.barks), f'{sim.barks}')

# Save compatibility: from 2026-10-08 until 2026-10-17 SHADES made the
# Shield as 828 (TypeAOArtifact) quality 83, so a save from then, between
# the ceremony and the altar, still carries one. Pagan's 828s are quality 0.
LEGACY_SHIELD = TYPE_SHAPES['TypeAOArtifact']  # 828
print()
print('P5b: AOSCENE with a pre-2026-10-17 save\'s Shield (828 q83) — accepted')
w, av, art, egg, sim = fixture(AOSCENE, 296, carry=LEGACY_SHIELD,
                               carry_quality=AO_QUALITY,
                               flags={'shieldFixed': 1, 'templeOpen': 1})
run(sim, egg, AOSCENE)
check('legacy 828 q83: godsFree SET',
      sim.get_global(FLAGS['godsFree'], 1) == 1, f'{sim.barks}')
check(f'legacy 828 q83: popped to the altar top {SHIELD_ON_ALTAR}',
      art.parent is None and not art.ethereal and not art.destroyed
      and (art.x, art.y, art.z) == SHIELD_ON_ALTAR,
      f'parent={art.parent} at ({art.x}, {art.y}, {art.z})')

print()
print('P7b: AOSCENE with Pagan\'s own 828 (quality 0) — refused')
w, av, art, egg, sim = fixture(AOSCENE, 296, carry=LEGACY_SHIELD,
                               carry_quality=0,
                               flags={'shieldFixed': 1, 'templeOpen': 1})
run(sim, egg, AOSCENE)
check('Pagan\'s 828 q0: godsFree NOT set',
      sim.get_global(FLAGS['godsFree'], 1) == 0)
check('Pagan\'s 828 q0: "I lack the artifact" refusal fired',
      any('lack the artifact' in t for _o, t in sim.barks), f'{sim.barks}')
check('Pagan\'s 828 q0: stays with the Avatar', held_by(w, art, av),
      f'parent={art.parent}')

# ── EggEndgame ───────────────────────────────────────────────────────────
print()
print('P8: ENDGAME before the gods are freed — silent')
w, av, _c, egg, sim = fixture(ENDGAME, 299)
run(sim, egg, ENDGAME)
check('no barks', len(sim.barks) == 0, f'{sim.barks}')
check('endgameStarted NOT set',
      sim.get_global(FLAGS['endgameStarted'], 1) == 0)

print()
print('P9: ENDGAME with godsFree — the restoration finale plays')
w, av, _c, egg, sim = fixture(ENDGAME, 299, flags={'godsFree': 1})
run(sim, egg, ENDGAME)
check('endgameStarted SET (replay guard writes manifest bit 1814)',
      sim.get_global(FLAGS['endgameStarted'], 1) == 1)
check('the vale-healing bark fired',
      any('vale is healing' in t for _o, t in sim.barks), f'{sim.barks}')
check('the closing "time to go home" bark fired',
      any('time to go home' in t for _o, t in sim.barks))
check('no bag from this scene: Ezrekal gives it now (hasBag stays 0)',
      sim.get_global(FLAGS['hasBag'], 1) == 0)
check('no bag hand-over bark',
      not any('worn bag' in t for _o, t in sim.barks), f'{sim.barks}')

# P9's hatch() ends in `spawn topUpReagents() -> return;`, and fixture()
# sets follow_spawns, so sim.spawns already records that spawn's (class,
# offset). Reading it from here keeps this file synced with the real
# build even after a recompile moves the offset.
_topup_spawns = [s for s in sim.spawns if s['class'] == ENDGAME]
check('hatch() spawned exactly one topUpReagents process',
      len(_topup_spawns) == 1, f'{sim.spawns}')
TOPUP_OFFSET = _topup_spawns[0]['offset']

print()
print('P10: ENDGAME replay guard — the finale does not play twice')
w, av, _c, egg, sim = fixture(ENDGAME, 299,
                              flags={'godsFree': 1, 'endgameStarted': 1})
run(sim, egg, ENDGAME)
check('no barks on replay (guard holds)', len(sim.barks) == 0, f'{sim.barks}')

# ── topUpReagents: slow refill inside the bag, no duplication outside it ──
# docs/playtest-2026-09-29-endgame-egg-pad.md finding 4: the original rule
# refilled any depleted stack it found ANYWHERE the Avatar carried it, bag
# or not, so splitting a stack onto the ground minted reagents for free.
#
# Douglas's 2026-10-01 correction kept the bag bottomless for partial drags
# (casting a reagent IS dragging part of a stack out). His 2026-10-02
# decision meters it, because at 333fdd1 a stack in the bag went straight
# back to 25 each poll and dropping reagents on the ground farmed about
# 24-25 per poll without limit. The rule now: inside the tagged bag a
# stack gains at most 5 per poll, capped at 25 (12 -> 17 -> 22 -> 25); a
# frame missing from the bag AND the rest of the Avatar is recreated at 5
# and climbs 5 per poll; nothing outside the bag is ever written.
#
# These enter topUpReagents directly (bypassing hatch(), which this build
# no longer uses to create the bag): a fixture builds the bag and its
# contents by hand, tags the bag with quality 1 the way EZREKAL.UNK's B1a
# does, sets endgameStarted and hasBag, then runs the process straight
# from TOPUP_OFFSET. The loop never returns, and wait() returns at once in
# the sim, so run_topup counts polls itself: each wait() is a spawn of FREE
# (class 0x581), and the spawn that would START poll N+1 raises SimError.
# Poll k therefore runs completely between wait k and wait k+1.


class _PollLimit(list):
    """sim.spawns that stops the run when poll N+1's wait() is spawned."""
    def __init__(self, polls):
        super().__init__()
        self.polls = polls
        self.waits = 0

    def append(self, spawn):
        super().append(spawn)
        if spawn['class'] == 0x581:
            self.waits += 1
            if self.waits > self.polls:
                raise SimError('poll limit')


def topup_world():
    w = SimWorld()
    av = w.add(SHAPE_AVATAR, objid=1, x=0, y=0, z=0)
    return w, av


def run_topup(w, av, polls=1):
    sim = UCSim(world=w)
    sim.set_global(FLAGS['endgameStarted'], 1, 1)
    sim.set_global(FLAGS['hasBag'], 1, 1)
    sim.spawns = _PollLimit(polls)
    try:
        sim.run_event(ENDGAME, TOPUP_OFFSET, av.objid, max_steps=200000)
    except SimError as e:
        check('run stopped on the poll limit, not a runaway',
              'poll limit' in str(e), f'{e}')
    return sim


def in_bag(w, bag, frame):
    return [it for it in w.items.values()
            if it.shape == TYPE_REAGENT and it.frame == frame
            and it.parent == bag.objid]


print()
print('P11: requirement 1 -- a partial drag inside the bag refills 5 per '
      'poll, capped at 25')
for polls, want in ((1, 18), (2, 23), (3, 25), (4, 25)):
    w, av = topup_world()
    bag = w.add(TYPE_BAG, quality=1)
    w.put_in_container(bag, av)
    remainder = w.add(TYPE_REAGENT, frame=0, quantity=13)  # 25 split by 12
    w.put_in_container(remainder, bag)
    ground_split = w.add(TYPE_REAGENT, frame=0, quantity=12)
    run_topup(w, av, polls=polls)
    check(f'after {polls} poll(s) the in-bag remainder is {want} '
          f'(13 -> 18 -> 23 -> 25)',
          remainder.quantity == want, f'{remainder.quantity}')
    check(f'after {polls} poll(s) the dropped half is unaffected',
          ground_split.quantity == 12, f'{ground_split.quantity}')

print()
print('P11b: a split dropped on the bag\'s own floor is a second stack in '
      'the bag; the cap is on the frame\'s total, so it mints nothing')
# docs/playtest-2026-10-03-batch-merge.md finding 1: with a per-stack cap,
# 25 split 13 + 12 inside the bag refilled both, and frame 9 went 25 -> 50.
for (a, b), polls, want in (((13, 12), 3, 25), ((10, 5), 1, 20),
                            ((10, 12), 1, 25), ((10, 5), 3, 25)):
    w, av = topup_world()
    bag = w.add(TYPE_BAG, quality=1)
    w.put_in_container(bag, av)
    s1 = w.add(TYPE_REAGENT, frame=9, quantity=a)
    w.put_in_container(s1, bag)
    s2 = w.add(TYPE_REAGENT, frame=9, quantity=b)
    w.put_in_container(s2, bag)
    run_topup(w, av, polls=polls)
    total = sum(it.quantity for it in in_bag(w, bag, 9))
    check(f'{a} + {b} in the bag, {polls} poll(s): the frame totals {want}',
          total == want, f'{total} ({s1.quantity} + {s2.quantity})')
    check(f'{a} + {b}: no third stack appears', len(in_bag(w, bag, 9)) == 2,
          f'{len(in_bag(w, bag, 9))}')

print()
print('P12: requirement 2 -- nothing outside the tagged bag is EVER '
      'refilled')
w, av = topup_world()
bag = w.add(TYPE_BAG, quality=1)
w.put_in_container(bag, av)
other_bag = w.add(TYPE_BAG, quality=0)      # Ragnar/Hrodny-shaped, untagged
w.put_in_container(other_bag, av)
in_other_bag = w.add(TYPE_REAGENT, frame=14, quantity=2)
w.put_in_container(in_other_bag, other_bag)
loose_on_avatar = w.add(TYPE_REAGENT, frame=6, quantity=1)  # not in any bag
w.put_in_container(loose_on_avatar, av)
sim = run_topup(w, av, polls=3)
check('a low stack inside an UNTAGGED TypeBag/637 is left alone',
      in_other_bag.quantity == 2, f'{in_other_bag.quantity}')
check('a low stack carried loose on the Avatar (no bag) is left alone',
      loose_on_avatar.quantity == 1, f'{loose_on_avatar.quantity}')

print()
print('P13: requirement 3 -- dragging a whole stack out does not mint a '
      'free one while the player still has it')
w, av = topup_world()
bag = w.add(TYPE_BAG, quality=1)
w.put_in_container(bag, av)
# Frame 10 has NOTHING left in the bag, but the whole dragged-out stack
# is still on the Avatar (here, loose; Ragnar/Hrodny's untagged bag would
# read the same way). The farming move -- drag the whole stack, let the
# bag "restock" -- must not pay out while he is still holding it.
carried_elsewhere = w.add(TYPE_REAGENT, frame=10, quantity=25)
w.put_in_container(carried_elsewhere, av)
sim = run_topup(w, av, polls=3)
check('still carrying the whole stack elsewhere: the bag gets no fresh one',
      len(in_bag(w, bag, 10)) == 0, f'{in_bag(w, bag, 10)}')
check('the carried stack itself is untouched',
      carried_elsewhere.quantity == 25, f'{carried_elsewhere.quantity}')

print()
print('P14: requirement 3, the permitted case -- truly out of a kind '
      'restocks it at 5, and a full stack is left alone')
w, av = topup_world()
bag = w.add(TYPE_BAG, quality=1)
w.put_in_container(bag, av)
control = w.add(TYPE_REAGENT, frame=6, quantity=25)
w.put_in_container(control, bag)
emptied = w.add(TYPE_REAGENT, frame=8, quantity=0)  # the whole stack spent
w.put_in_container(emptied, bag)
# Frame 9 has no stack anywhere -- not in the bag, not anywhere else on
# the Avatar. This is "truly out": the one case that may restock.
#
# Frame 14's whole stack was dragged out and dropped on the ground: it
# has no parent, so `within container Avatar` cannot see it either, and
# it reads as "truly out" the same as frame 9 above. This is a named,
# accepted residual: the dropped stack itself is a real, spent
# withdrawal, never refilled, same as any ground item; the bag simply
# has no way to tell "gone from the world" apart from "still on him,
# just not in the bag," so it restocks here too. The slow refill bounds
# it: 5 per poll per frame, where 333fdd1 paid 25.
dropped_on_ground = w.add(TYPE_REAGENT, frame=14, quantity=25)
sim = run_topup(w, av, polls=1)
check('an untouched full stack is unaffected',
      control.quantity == 25, f'{control.quantity}')
check('a stack emptied to zero (still in the bag) gains 5, not 25',
      emptied.quantity == 5, f'{emptied.quantity}')
fresh = in_bag(w, bag, 9)
check('a frame missing from the bag AND the rest of the Avatar is '
      'recreated at 5',
      len(fresh) == 1 and fresh[0].quantity == 5, f'{fresh}')
check('the dropped-on-ground stack itself is unaffected either way',
      dropped_on_ground.quantity == 25, f'{dropped_on_ground.quantity}')
fresh14 = in_bag(w, bag, 14)
check('a whole stack dropped on the ground restocks at 5 (accepted '
      'residual: ground is invisible to this check)',
      len(fresh14) == 1 and fresh14[0].quantity == 5, f'{fresh14}')
sim = run_topup(w, av, polls=3)
check('the recreated stack climbs 5 per poll (5, then 3 more polls: 20)',
      in_bag(w, bag, 9) and in_bag(w, bag, 9)[0].quantity == 20,
      f'{in_bag(w, bag, 9)}')

print()
print(f'OK: {passed} passed, {failed} failed' if failed == 0
      else f'FAILED: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

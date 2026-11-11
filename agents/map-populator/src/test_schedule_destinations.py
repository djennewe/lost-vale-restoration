#!/usr/bin/env python3
"""
test_schedule_destinations.py — every place a scheduled Lost Vale NPC is
put on Map 10 is a place an NPC body can stand and walk from: its
schedule() destinations, its map start, and the Sacred Circle and
Passage Test scenes' teleports (the Avatar's too, for the second).

WHY (2026-10-08). The eight Lost Vale schedules (ATLI, EZREKAL, RAGNAR,
TYORVI, THORDIS, HRODNY and INGYALD in lv-patched/, SIGRID in lv-new/) end
in retail METHOD `safeTeleport` (class 0x57C offset 133F). Retail checks
only that the Avatar is over 700 units from the NPC and from the
destination, then calls Npc::teleport(x, y, z, map) with the literals as
written: nothing snaps the point to a floor or out of a wall. Their 1994
destinations were coordinates of a Map 10 that no longer exists (void,
lake, bare ground at z 64 over z-0 ground; docs/playtest-2026-10-07-
wave1.md), so the call was held back until they were retargeted to the
rebuilt villages. The same audit found three of these NPCs STARTING inside
solids (Thordis in the Hoskuld keep's corner, Ragnar in Hut 3's wall,
Ingjald in a chest) and EggShades sending Thordis home into the same keep
corner. The regression this catches is the next one: a map edit that drops
a hut, a fence or the lake onto one of these points, or a usecode or
builder edit that types a point nobody checked.

WHAT IT READS — the bytes that ship, not anyone's intent:
  * shared/build/EUSECODE.FLX: each class's schedule() (event 8) is
    disassembled; every `spawn 07h 02h 057Ch 133Fh/143Ah` must push map
    10, and every x/y/z literal stored into the WorldPoint it pushes is a
    destination. EggShades (lv-patched/SHADES.UNK) is disassembled whole
    and every `push map; push z; push y; push x; push NPC; calli 0Ch 009Eh`
    (Npc::teleport) to map 10 is a point too — the three teleport-ins at
    the Sacred Circle and the three send-homes. EggPlantTest and
    TypePoisonPlant (lv-patched/PLNTST.UNK) are read the same way for the
    Passage Test's three teleports (the Avatar, Atli, Thordis), whose map
    is `Avatar.getMap()`, not a literal;
  * shared/build/FIXED.DAT + TYPEFLAG.DAT, Map 10, globs expanded, through
    exact_reach (the engine's own getPositionInfo/Box::overlaps rules).
    The NPC records (npcNum 100-116) are left out of the geometry: they are
    the movers. The eight scheduled NPCs' records are themselves checked as
    points (their map starts).

EACH POINT MUST BE
  1. standable at EXACTLY its z for a 64x64x40 body (every one of the
     eight NPC shapes is footpad 2x2x5): no SOLID/DAMAGING box overlaps it,
     a surface tops out at z, land within 8 below — exact_reach at a
     1-unit lattice around the point, since the engine puts the actor
     there to the unit;
  2. not over the lake: no SI_SEA item under the body's footprint (the
     lake tiles, shape 347, are SOLID|SEA with a top at 0, so the
     standability rule alone would accept them);
  3. reachable on foot from the Map 10 arrival pad, with every lattice
     position within 64 units also reached at the same z — off any
     plateau edge, with room for the loiter that enterFastArea starts.
     The flood runs on a 16-unit lattice (as test_route_reach does for
     Map 10); a point off it (map records sit on multiples of 32) must
     also have every 1-unit position between it and its nearest lattice
     position standable at z. A point in a door gap, where a body meets a
     solid jamb within 128 on both sides across the door, need only have
     the positions within 64 ALONG the doorway reached (into the hut and out
     to the yard): Atli's (19231,6943,0), screen19's 1994 elder in his
     doorway (2026-10-17). Every other point keeps the full box.
  4. drawn in the open: at most 10% of the NPC's body sprite (its map
     record's shape and frame, the body the engine draws it with on
     arrival; frame 0 for every NPC but Atli, whose record faces SE out of
     his door at 888's frame 60 since 2026-10-25) is painted over by map
     items the engine draws after it — item_sorter.ItemSorter.overdrawn,
     a port of SortItem::below/overlap with the sprites' real pixels, and
     with GameMapGump's roof cut for a camera on the point, so an NPC
     inside a hut is judged from inside it. A covered pixel can be neither
     seen nor clicked. Standability says nothing about this: Tyorvi's first
     Gunnar stash point (22335,7647,0) was standable, reachable and
     dry, and the south-east cliff (104 tall from x 22528, sorted in
     front of everything within about 380 units west of its foot) drew
     over him whole (docs/playtest-2026-10-09-schedules.md finding 2).

A MAP START MUST ALSO BE
  5. one of the NPC's own schedule() points, to within 1 unit per axis
     (map records sit on multiples of 32, the literals one below). Every
     Map 10 entry snaps the LV actors (100-116) back to their FIXED
     starts (fork map.cpp) and the entry's schedule() call then moves
     only the far ones, so a start that is no schedule point is where
     the NPC reappears after any map hop (docs/playtest-2026-10-09-
     schedules.md finding 4).

Prove-it (2026-10-08): against an EUSECODE.FLX whose eight schedule
classes were compiled from the pre-retarget sources with the call enabled,
all 16 points fail check 1 (z 64 is no standing level at any of them; two
are void), the three lake points (Ragnar's field, Tyorvi's stash,
Sigrid's hunt) also fail check 2, and every one fails check 3: 35 FAIL.
Against the f872e99 build (schedules retargeted, Thordis/Ragnar/Ingjald
starts and the EggShades send-homes not yet moved), the three starts and
Thordis's send-home (6144,6656) fail checks 1 and 3: 8 FAIL. Against the
c2f2e15 build (Tyorvi's stash still at (22335,7647)), check 4 fails on
that point alone, at 100% covered; every other point reads 0%. Against
the d7d9b15 build, check 5 fails on Atli's start (19200,6400, inside his
hut) and Sigrid's (7680,6400): 2 FAIL. Against FIXED 22cada6f, the
Passage Test points fail check 4 (the Avatar's 100% covered by the
plateau's south rim, the witness's 83% by its east rim and crest) and
the Avatar's fails check 3 (a dressing spire 33 units off it): 8 FAIL.

    python3 agents/map-populator/src/test_schedule_destinations.py [FLX [FIXED]]

Plain script: exit 0 on pass, 1 on fail. ~15 s.
"""

import json
import os
import struct
import sys

import numpy as np

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'agents', 'usecode-compiler', 'src'))
sys.path.insert(0, os.path.join(BASE_DIR, 'agents', 'usecode-disasm', 'src'))

from exact_reach import (ExactReach, load_map, AVATAR_BODY,   # noqa: E402
                         SI_SOLID, SI_DAMAGING, SI_SEA, FLG_FLIPPED)
from item_sorter import ItemSorter, SHAPES                   # noqa: E402
from map_preview import GlobReader, expand_globs             # noqa: E402
from u8_flex import UsecodeFlexArchive                       # noqa: E402
from u8_usecode_disasm import UsecodeDisassembler            # noqa: E402
from u8c_symbols import LV_NPC_SHAPES, METHOD_CLASS_ID, METHOD_ROUTINES  # noqa: E402

FLX = (sys.argv[1] if len(sys.argv) > 1 else
       os.path.join(BASE_DIR, 'shared', 'build', 'EUSECODE.FLX'))
FIXED = (sys.argv[2] if len(sys.argv) > 2 else
         os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT'))
MANIFEST = os.path.join(BASE_DIR, 'shared', 'build', 'lv_manifest.json')
NPC_TELEPORT = 0x9E                # calli 0Ch 009Eh: Npc::teleport
OBJ_SEG = 0x8002                   # push dword 8002xxxxh: objid xxxx
MAP = 10
ARRIVAL = (12800, 2560, 0)        # test_route_reach.py's Map 10 seed
CLEARANCE = 64
START_SLACK = 1                    # check 5: start within 1 unit per axis
OVERDRAWN_MAX = 0.10               # check 4: share of the NPC sprite covered
SCHEDULE_EVENT = 8
SCHEDULED = ('ATLI', 'EZREKAL', 'RAGNAR', 'TYORVI', 'THORDIS', 'HRODNY',
             'INGJALD', 'SIGRID')
SAFE_TELEPORT = METHOD_ROUTINES['safeTeleport'][0]
CAN_SAFE_TELEPORT = METHOD_ROUTINES['canSafeTeleport'][0]

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def sbyte(v):
    return v - 256 if v > 127 else v


def schedule_body(flx, classid):
    """Instructions of the class's schedule() only, bounded by the next
    event entry (disassemble_bytecode would run on to the class end)."""
    blob = flx.get_class_data(classid)[12:]
    offs = sorted({struct.unpack_from('<I', blob, e * 4)[0]
                   for e in range(32)} - {0})
    start = struct.unpack_from('<I', blob, SCHEDULE_EVENT * 4)[0]
    if not start:
        return []
    end = next((o for o in offs if o > start), len(blob))
    return [ins for ins in UsecodeDisassembler().disassemble_bytecode(
        blob, start_offset=start) if ins.offset < end]


def literal(ins):
    """Value of a push-literal instruction, else None."""
    if ins.opcode == 0x0A:                    # push byte (sign-extended)
        return ins.operands[0][1]
    if ins.opcode == 0x0B:                    # push word
        return ins.operands[0][1]
    return None


def destinations(body):
    """(calls, points): calls = [(routine offset, map value or None)] for
    every METHOD safeTeleport/canSafeTeleport spawn; points = every
    (x, y, z) literal triple stored into the WorldPoint those calls push."""
    calls, point_bp = [], set()
    local_writes = {}                         # bp -> [literal values]
    for k, ins in enumerate(body):
        if ins.opcode == 0x01 and k and literal(body[k - 1]) is not None:
            bp = sbyte(ins.operands[0][1])
            local_writes.setdefault(bp, []).append(literal(body[k - 1]))
        if ins.opcode != 0x57:
            continue
        _a, _t, cls, off = (o[1] for o in ins.operands)
        if cls != METHOD_CLASS_ID or off not in (SAFE_TELEPORT,
                                                 CAN_SAFE_TELEPORT):
            continue
        # push <map>; push huge [BP+p] 05h; push dword [BP+06h]; spawn
        huge, mp = body[k - 2], body[k - 3]
        assert huge.opcode == 0x45 and huge.operands[1][1] == 5, huge
        point_bp.add(sbyte(huge.operands[0][1]))
        if literal(mp) is not None:
            calls.append((off, [literal(mp)]))
        elif mp.opcode == 0x3F:               # push [BP+m]: a MapNum local
            calls.append((off, ('local', sbyte(mp.operands[0][1]))))
        else:
            calls.append((off, None))
    calls = [(off, local_writes.get(m[1], []) if isinstance(m, tuple) else m)
             for off, m in calls]
    points = []
    for p in point_bp:
        x = y = None
        for k, ins in enumerate(body):
            if not k or ins.opcode not in (0x00, 0x01) \
                    or literal(body[k - 1]) is None:
                continue
            v = literal(body[k - 1])
            bp = sbyte(ins.operands[0][1])
            if ins.opcode == 0x01 and bp == p:
                x = v
            elif ins.opcode == 0x01 and bp == p + 2:
                y = v
            elif ins.opcode == 0x00 and bp == p + 4 and x is not None:
                points.append((x, y, v))
                x = y = None
    return calls, points


def npc_teleports(flx, classid):
    """[(npc objid, x, y, z, map)] for every Npc::teleport to a literal
    point in the class: push map; push z; push y; push x; push dword
    8002<objid>h; calli 0Ch 009Eh. `map` is None where it is computed
    (PLNTST's `Avatar.getMap()`: push retval) rather than a literal."""
    blob = flx.get_class_data(classid)[12:]
    start = min({struct.unpack_from('<I', blob, e * 4)[0]
                 for e in range(32)} - {0})
    body = UsecodeDisassembler().disassemble_bytecode(blob, start_offset=start)
    out = []
    for k, ins in enumerate(body):
        if ins.opcode != 0x0F or ins.operands[1][1] != NPC_TELEPORT:
            continue
        obj, x, y, z, m = body[k - 1], body[k - 2], body[k - 3], body[k - 4], \
            body[k - 5]
        if obj.opcode != 0x0C or obj.operands[0][1] >> 16 != OBJ_SEG:
            continue
        vals = [literal(i) for i in (x, y, z)]
        if None in vals:
            continue
        out.append((obj.operands[0][1] & 0xFFFF, *vals, literal(m)))
    return out


def sea_boxes(items):
    """XY boxes (x, y, xd, yd) of every SI_SEA item, globs expanded."""
    gr, out = GlobReader(), []
    for it in items:
        parts = (gr.glob_to_items(it.quality, it.x, it.y, it.z & 0xFF)
                 if it.is_glob_egg else [it])
        for p in parts:
            if 0 <= p.shape < len(shapes) and shapes[p.shape].flags0 & SI_SEA:
                si = shapes[p.shape]
                xd, yd = si.footpad_x * 32, si.footpad_y * 32
                if p.flags & FLG_FLIPPED:
                    xd, yd = yd, xd
                out.append((p.x, p.y, xd, yd))
    return out


def doorway(i, j, z, k):
    """The open axis ('x' or 'y') if lattice point (i, j) stands in a door
    gap: across the door, a body meets a solid jamb within 2 x CLEARANCE
    on BOTH sides (a gap no wider than a hut's 128-unit door plus the
    body), and every position within CLEARANCE along the other axis, into
    the hut and out into the yard, is reached at z. Else None. A doorway
    is a fair place to stand — screen19's 1994 elder, Atli, stands in his
    (ATLI.UNK S1 (19231,6943,0)) — but no such gap leaves the full box
    clear; everywhere else the box check stands."""
    if z not in reach:
        return None
    blk, r = world.blocked(z), reach[z]
    nx, ny = r.shape

    def jamb(di, dj):
        for n in range(1, 2 * k + 1):
            p, q = i + di * n, j + dj * n
            if not (0 <= p < nx and 0 <= q < ny):
                return False
            if blk[p, q]:
                return True
        return False

    for axis, (di, dj) in (('y', (1, 0)), ('x', (0, 1))):
        if not (jamb(di, dj) and jamb(-di, -dj)):
            continue
        line = (r[i, max(j - k, 0):j + k + 1] if axis == 'y'
                else r[max(i - k, 0):i + k + 1, j])
        if line.size == 2 * k + 1 and line.all():
            return axis
    return None


def check_point(tag, x, y, z, body):
    """Checks 1-4 of the module docstring for one point; `body` is the
    NPC's map-record (shape, frame), its body sprite for check 4."""
    local = ExactReach(geometry, shapes, (x - 24, y - 24, x + 24, y + 24),
                       step=1, mover_flags=SI_SOLID | SI_DAMAGING)
    i, j = local.index_of(x, y)
    stand = z in local.levels and bool(local.mask(z)[i, j])
    check(f'{tag}: a 64x64x40 body stands at exactly z {z}', stand,
          f'standing levels here: {local.standable_levels(x, y)}')
    wet = [s for s in sea if s[0] - s[2] < x and x - bxd < s[0]
           and s[1] - s[3] < y and y - byd < s[1]]
    check(f'{tag}: not over the lake (no SI_SEA under the body)',
          not wet, wet[:2])
    i, j = world.index_of(x, y)
    lx, ly = world.x_of(i), world.y_of(j)
    a, b = local.index_of(min(x, lx), min(y, ly))
    c, d = local.index_of(max(x, lx), max(y, ly))
    linked = (z in local.levels and
              bool(local.mask(z)[a:c + 1, b:d + 1].all()))
    k = CLEARANCE // world.step
    box = (z in reach and
           bool(np.all(reach[z][max(i - k, 0):i + k + 1,
                                max(j - k, 0):j + k + 1])))
    door = doorway(i, j, z, k) if linked and not box else None
    ok = linked and (box or door is not None)
    check(f'{tag}: reached on foot from the arrival pad, '
          f'+/-{CLEARANCE} around it all at z {z}'
          + (f' (a doorway: through it along {door})' if door else ''), ok,
          'not joined to the lattice' if not linked
          else 'unreached or on an edge')
    shape, frame = body
    share, over = sorter.overdrawn(drawn, shape, frame, x, y, z)
    check(f'{tag}: drawn in the open (map items cover '
          f'{share:.0%} of shape {shape} frame {frame}, at most '
          f'{OVERDRAWN_MAX:.0%})',
          share <= OVERDRAWN_MAX,
          sorted(over, key=lambda c: -c[-1])[:3])


print('=' * 70)
print('Scheduled NPCs on Map 10 — schedule points, map starts, EggShades')

if not (os.path.exists(FLX) and os.path.exists(SHAPES)
        and load_map(MAP, FIXED)[0]):
    print('  built EUSECODE.FLX / U8SHAPES.FLX / FIXED.DAT absent — '
          'run tools/build_artifacts.sh')
    sys.exit(1)

flx = UsecodeFlexArchive(FLX)
items, shapes = load_map(MAP, FIXED)
movers = [it for it in items
          if 100 <= it.npcnum <= 116 and not it.is_glob_egg
          and it.shape not in (73, 500)]          # UNK_EGG, MONSTER_EGG
geometry = [it for it in items if it not in movers]
bxd, byd, _ = AVATAR_BODY
sea = sea_boxes(geometry)
sorter = ItemSorter(shapes=SHAPES)
drawn = expand_globs(geometry, GlobReader())
body_of = {it.npcnum: (it.shape, it.frame) for it in movers}

xs = [i.x for i in geometry if i.x >= 64]
ys = [i.y for i in geometry if i.y >= 64]
roi = (min(xs) - 64, min(ys) - 64, max(xs) + 64, max(ys) + 64)
world = ExactReach(geometry, shapes, roi, step=16,
                   mover_flags=SI_SOLID | SI_DAMAGING)
reach, seeded = world.flood([ARRIVAL])
check(f'the Map 10 arrival pad {ARRIVAL} is standable', bool(seeded))

print()
print('-- schedule() destinations')
sched_points = {}
for name in SCHEDULED:
    cid = LV_NPC_SHAPES[name]
    body = schedule_body(flx, cid)
    calls, points = destinations(body)
    sched_points[name] = points
    print(f'  {name} (class 0x{cid:04X}): {len(points)} destination(s)')
    check(f'{name}: schedule() calls retail METHOD safeTeleport '
          f'(spawn 057Ch {SAFE_TELEPORT:04X}h)',
          any(off == SAFE_TELEPORT for off, _ in calls), calls)
    check(f'{name}: every (can)safeTeleport goes to map {MAP}',
          calls and all(m and set(m) == {MAP} for _, m in calls), calls)
    check(f'{name}: at least one destination literal was read',
          bool(points), body and body[0].offset)
    for (x, y, z) in points:
        check_point(f'{name} ({x},{y},{z})', x, y, z, body_of[cid - 0x400])

print()
print('-- map starts (FIXED.DAT records, npcNum = class - 0x400)')
for name in SCHEDULED:
    npcnum = LV_NPC_SHAPES[name] - 0x400
    recs = [it for it in movers if it.npcnum == npcnum]
    check(f'{name}: exactly one map-{MAP} record for npcNum {npcnum}',
          len(recs) == 1, [(r.x, r.y, r.z) for r in recs])
    for r in recs:
        check_point(f'{name} start ({r.x},{r.y},{r.z})', r.x, r.y, r.z,
                    (r.shape, r.frame))
        near = [p for p in sched_points[name]
                if abs(p[0] - r.x) <= START_SLACK
                and abs(p[1] - r.y) <= START_SLACK and p[2] == r.z]
        check(f'{name} start ({r.x},{r.y},{r.z}) is one of its schedule() '
              f'points (within {START_SLACK} unit per axis)', bool(near),
              f'points: {sched_points[name]}')
# Every LV actor in the promotion window (100-116) must keep its one start
# record. A vignette stamp drops an unpinned record inside its region, and
# derive_map_pins then re-derives the pins without it: on 2026-10-25 npc 111
# (the blond spear child, 890) vanished from Map 10 that way, and no
# test noticed (docs/playtest-2026-10-25-phaseD-verify.md defect 1).
missing = [n for n in range(100, 117)
           if sum(1 for it in movers if it.npcnum == n) != 1]
check('every LV actor npcNum 100-116 has exactly one map-10 start record',
      not missing, f'npcNum without exactly one record: {missing}')

print()
print('-- EggShades (lv-patched/SHADES.UNK) Npc::teleport literals')
with open(MANIFEST) as fh:
    manifest_classes = json.load(fh)['classes']
shades_cid = manifest_classes['EGGSHADES']
tps = npc_teleports(flx, shades_cid)
who = {LV_NPC_SHAPES[n] - 0x400: n for n in SCHEDULED}
check('EggShades: six NPC teleports read (three in, three home)',
      len(tps) == 6, tps)
for (obj, x, y, z, m) in tps:
    tag = f'EggShades {who.get(obj, obj)} ({x},{y},{z})'
    check(f'{tag}: map {MAP}', m == MAP, m)
    check_point(tag, x, y, z, body_of[obj])

# The Passage Test (quest step 8) ends with the Avatar and the witness
# teleported onto the test-grounds plateau, and the step-9 talk is a
# double-click on the witness there. Both classes that run the scene carry
# the same three teleports, to `Avatar.getMap()` (map 10: the egg and the
# plant are on it). Until 2026-10-10 the plateau's south and east rim
# painted over 100% of the Avatar's point and 83% of the witness's
# (playtest-2026-10-10-full-run-part5 finding 3).
AVATAR_OBJ, AVATAR_SHAPE = 1, 1
print()
print('-- the Passage Test (lv-patched/PLNTST.UNK) Npc::teleport literals')
for cname in ('EGGPLANTTEST', 'TYPEPOISONPLANT'):
    tps = npc_teleports(flx, manifest_classes[cname])
    check(f'{cname}: three teleports read (the Avatar, Atli, Thordis)',
          sorted(t[0] for t in tps) == sorted(
              [AVATAR_OBJ, LV_NPC_SHAPES['ATLI'] - 0x400,
               LV_NPC_SHAPES['THORDIS'] - 0x400]), tps)
    for (obj, x, y, z, m) in tps:
        name = 'AVATAR' if obj == AVATAR_OBJ else who.get(obj, obj)
        tag = f'{cname} {name} ({x},{y},{z})'
        check(f"{tag}: to the Avatar's own map", m is None, m)
        check_point(tag, x, y, z, (AVATAR_SHAPE, 0) if obj == AVATAR_OBJ
                    else body_of[obj])

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

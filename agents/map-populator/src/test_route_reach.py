#!/usr/bin/env python3
"""
test_route_reach.py — CAN THE AVATAR ACTUALLY WALK THE QUEST ROUTE?

Every map in the expansion is entered at a teleport arrival pad and left at
an onward trigger, and quest items sit somewhere in between. This asks the
only question that matters about the geometry: starting from the arrival
pad, with the engine's own 64x64x40 Avatar box, can he get there?

It is deliberately NOT the cell-raster check. `map_walkability.WalkGrid`
quantises to 32-unit cells and judges a cell by its centre, which is right
for "roughly, does this region connect" and wrong at body width in BOTH
directions — it shipped the Tiny Tar crack sealed (b95de7a) and it also
reports 64-wide corridors impassable when they are not aligned to its grid.
`exact_reach.py` reimplements CurrentMap::getPositionInfo and Box::overlaps
instead. See its docstring for the model and its limits (FIXED.DAT only:
NPCs and NONFIXED doors are invisible to it).

WHAT THIS CAUGHT WHEN IT WAS WRITTEN (2026-07-31), both invisible to every
check that existed:

  * MAP 17 — the whole northern half (God's Halls, Scroll Chamber and the
    Memorial Hall with BOTH SHIELD HALVES, quest steps 13-15) was severed
    from the arrival plaza by a 512-unit strip with no floor in it.
  * MAP 13 — the climb to Cloud City was six separate ribbons with 9-unit
    risers between them, plus a 512-unit hole. Walking refuses a riser
    over 8 (scanForValidPosition scans +/-8), and no jump crosses 512.

SCOPE OF A VERDICT HERE (from the same-day self-audit — exact_reach.py's
"deliberate deviations" section is the full statement). REACHED is solid:
the model is strictly no more permissive than the engine. UNREACHED means
no WALKING route over REAL geometry — the engine itself would walk a
floorless void at z=0 (so pre-fix map 17 was likely traversable as a
black-void walk, ugly but passable), and the jump button auto-climbs up
to 72 units, which this model does not simulate. The two "designed
barrier" assertions below are therefore *walking* seals; whether a jump
climbs the map 18 crack wall (40 tall, bare top) or the map 11 boulders
(40 tall, bare top) is an OPEN QUESTION needing one in-engine jump test.

Runtime ~40s: the floods ~12s (maps 10 and 11 on a 16-unit lattice, same
verdicts as 8, four times faster; the rest on 8), the mover replays the rest.
"""

import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC_DIR)

from exact_reach import ExactReach, load_map, TINY_BODY   # noqa: E402
from exact_reach import AVATAR_BODY, HURT_SHAPES_U8      # noqa: E402
from exact_reach import FLG_CONTAINED, FLG_EQUIPPED, FLG_FLIPPED  # noqa: E402
from map_preview import GlobReader, expand_globs          # noqa: E402
from build_map_13 import (climb_tiles, CLIMB_Z_TOP,      # noqa: E402
                         CLIMB_Z_STEP)
from exact_reach import Z_SEARCH_OFFSETS_U8              # noqa: E402
from exact_reach import SI_SOLID, SI_DAMAGING            # noqa: E402

SEALING_BOULDER_QUALITY = 299     # build_map_11: the four-pillar puzzle's plug

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def flood(mapnum, seed, step=8, body=None, drop=None, mover_flags=None,
          hurt_margin=None):
    """Flood a map from an arrival pad. `drop`: predicate to remove items
    (used for the sealing-boulder counterfactual). `mover_flags`: which
    item flags block the mover — SI_SOLID alone by default; add
    SI_DAMAGING to walk as the Avatar does, refused by lava and flame.
    `hurt_margin`: also refuse every position within that many units of a
    usecode-burning shape (HURT_SHAPES_U8, the CLRLAVA lava), contact
    included."""
    items, shapes = load_map(mapnum)
    if not items:
        return None, None
    if drop is not None:
        items = [it for it in items if not drop(it)]
    xs = [i.x for i in items if i.x >= 64]
    ys = [i.y for i in items if i.y >= 64]
    roi = (min(xs) - 64, min(ys) - 64, max(xs) + 64, max(ys) + 64)
    kw = {'step': step}
    if body is not None:
        kw['body'] = body
    if mover_flags is not None:
        kw['mover_flags'] = mover_flags
    if hurt_margin is not None:
        kw['hurt_shapes'] = HURT_SHAPES_U8
        kw['hurt_margin'] = hurt_margin
    er = ExactReach(items, shapes, roi, **kw)
    reach, seeded = er.flood([seed])
    if not seeded:
        return er, None
    return er, reach


def route(mapnum, label, seed, targets, step=8, body=None, drop=None,
          mover_flags=None, hurt_margin=None):
    er, reach = flood(mapnum, seed, step=step, body=body, drop=drop,
                      mover_flags=mover_flags, hurt_margin=hurt_margin)
    if er is None:
        check(f'map {mapnum}: present in FIXED.DAT', False)
        return
    if reach is None:
        check(f'map {mapnum} {label}: the arrival pad {seed} is standable',
              False, 'the player drops into a void on arrival')
        return
    tot, walk = er.summary(reach)
    print(f'  map {mapnum} ({label}): reached {tot} of {walk} standable '
          f'positions ({100.0 * tot / max(walk, 1):.1f}%)')
    for (want, desc, x, y, z) in targets:
        hit = er.reached_near(reach, x, y, z, ring=96)
        check(f'map {mapnum}: {desc}', bool(hit) == want,
              f'{"unreachable" if want else "reachable when it must not be"}'
              f' from {seed}')


print('=' * 70)
print('Quest route reachability — engine box arithmetic, arrival pad to goal')

# --- Gateway geometry: pins + the bounce audit ------------------------
# THE TELEPORT-INVERSION BOUNCE CLASS (found in-engine 2026-07-31, report
# C1; then found SYSTEMIC by static audit — 8 of 11 gateways had it). The
# 2026-07-25 relocation comments were written under the pre-771d5c7
# inverted helper names, so the ACTIVE trigger of most gateways was built
# on the natural walking line while the passive pad sat on the marked
# out-of-the-way slab. Walking off the arrival pad bounced you straight
# back. Trigger hatch boxes are INVISIBLE to every flood (eggs are not
# blockers), so only this audit sees them.

# Crossings that are the INTENDED onward trigger for that egress:
# (map, pad, trigger). (13,206/207 -> 209): the northbound egress IS the
# climb, and the summit trigger at its top is where it is meant to end.
GATEWAY_INTENDED = {(9, 201, 203), (9, 202, 200), (13, 206, 209),
                    (13, 207, 209)}


def gateway_audit():
    from u8_map import MapArchive
    from build_all_maps import TELEPORT_TABLE, gated_teleporters
    fixed = os.path.join(os.path.dirname(SRC_DIR.rstrip('/')).rsplit('agents', 1)[0],
                         'shared', 'build', 'FIXED.DAT')
    arch = MapArchive(fixed)
    # Gated triggers are usecode eggs (shape 73, class = quality + 0x47F),
    # so their quality is not their teleport id: tid_of() maps them back.
    gated = {(m, tid): it for tid, rows in gated_teleporters(arch).items()
             for m, it in rows}
    gated_id = {id(it): tid for (m, tid), it in gated.items()}

    def tid_of(it):
        return gated_id.get(id(it), it.quality & 0xFF)

    # The full LV gateway table as fixed on 2026-07-31 (Map 8's 201 and two
    # pads, Map 9's pad 201 and Map 10's 204 and 213 moved 2026-10-10 for
    # the arrival corridors below; Map 8's pads and 212, Map 11's pad 204
    # and Map 13's 206 moved again that day when the corridors went onto
    # the engine's mover model, and Map 8's 212 once more, out of the dark
    # and off its riser, for deliberate_use). Savegames do not
    # pin these (they are FIXED.DAT plumbing), but the cross-map dials do:
    # a trigger with id K delivers to the pad with id K on its dest map.
    # Map 8's 212 is 'gated' since 2026-10-11: EggValeReturn, which sends
    # him to Map 10's pad 212 only once allColumnsDestroyed is set
    # (first_visit_approach below; test_uc_vale_return.py runs the class).
    # (kind, id, x, y, z[, dest_map])
    TABLE = {
        8:  [('pad', 200, 20111, 3175, 8), ('trig', 201, 20415, 2783, 1, 9),
             ('pad', 213, 20143, 3175, 8), ('gated', 212, 20575, 3903, 0, 10)],
        9:  [('trig', 200, 13759, 12031, 0, 8), ('pad', 201, 13696, 14208, 0),
             ('pad', 202, 14336, 16128, 0), ('trig', 203, 14336, 16760, 0, 11)],
        10: [('trig', 204, 11904, 2048, 1, 11), ('pad', 205, 12800, 2560, 0),
             ('pad', 212, 13824, 2560, 0), ('trig', 213, 12800, 1792, 1, 8),
             ('pad', 206, 7168, 23296, 8), ('trig', 207, 7168, 24064, 8, 13),
             ('pad', 210, 18432, 22719, 112),   # screen17 shelf, 2026-10-17
             ('trig', 211, 18432, 23552, 0, 18)],
        11: [('trig', 202, 9728, 1152, 1, 9), ('pad', 203, 9728, 1792, 0),
             ('pad', 204, 8291, 22639, 0), ('trig', 205, 8960, 23296, 1, 10)],
        13: [('pad', 207, 4096, 11776, 0), ('trig', 206, 3328, 11520, 0, 10),
             ('pad', 208, 5119, 2303, 120), ('trig', 209, 4351, 2303, 120, 17)],
        17: [('trig', 208, 4608, 11008, 0, 13), ('pad', 209, 4608, 9984, 0)],
        18: [('trig', 210, 3072, 1408, 0, 10), ('pad', 211, 3072, 1792, 0)],
    }
    # Quest egress: the direction(s) the route leaves each pad by.
    EGRESS = {(8, 200): 'S', (8, 213): 'S', (9, 201): 'S', (9, 202): 'N',
              (10, 205): 'S', (10, 212): 'S', (10, 206): 'N', (10, 210): 'N',
              (11, 203): 'S', (11, 204): 'E', (13, 206): 'E,N',
              (13, 207): 'E,N', (13, 208): 'S', (17, 209): 'N', (18, 211): 'S'}
    INTENDED = GATEWAY_INTENDED

    for m, rows in TABLE.items():
        items = arch.get_map_items(m)
        eggs = {(('trig' if it.is_teleporter else 'pad'), it.quality & 0xFF): it
                for it in items if it.is_teleport_egg and (it.quality & 0xFF) >= 200}
        eggs.update({('gated', tid): it for (gm, tid), it in gated.items()
                     if gm == m})
        ok = True
        for row in rows:
            kind, tid, x, y, z = row[:5]
            it = eggs.get((kind, tid))
            if it is None or (it.x, it.y, it.z & 0xFF) != (x, y, z) or \
               (kind == 'trig' and it.mapnum != row[5]) or \
               (kind == 'gated' and TELEPORT_TABLE[tid]['to_map'] != row[5]):
                ok = False
                got = (f'({it.x},{it.y},{it.z & 0xFF})' if it is not None
                       else 'MISSING')
                check(f'map {m} gateway {kind} {tid} at ({x},{y},{z})',
                      False, f'got {got}')
        if ok:
            check(f'map {m}: gateway table matches ({len(rows)} eggs)', True)

        pads = [it for it in items if it.is_teleport_target
                and (it.quality & 0xFF) >= 200]
        trigs = [it for it in items if it.is_teleporter
                 and (it.quality & 0xFF) >= 200] + \
            [it for (gm, _t), it in gated.items() if gm == m]
        bad = []
        for p in pads:
            for t in trigs:
                xr, yr = (t.npcnum >> 4) * 32, (t.npcnum & 0xF) * 32
                x0, x1 = t.x - xr, t.x + xr
                y0, y1 = t.y - yr, t.y + yr
                if x0 - 64 <= p.x <= x1 + 64 and y0 - 64 <= p.y <= y1 + 64:
                    bad.append(f'pad {p.quality & 0xFF} within 64 of trigger '
                               f'{tid_of(t)} box')
                for d in EGRESS.get((m, p.quality & 0xFF), '').split(','):
                    if not d:
                        continue
                    hit = ((d == 'N' and x0 - 32 <= p.x <= x1 + 32 and y1 < p.y) or
                           (d == 'S' and x0 - 32 <= p.x <= x1 + 32 and y0 > p.y) or
                           (d == 'W' and y0 - 32 <= p.y <= y1 + 32 and x1 < p.x) or
                           (d == 'E' and y0 - 32 <= p.y <= y1 + 32 and x0 > p.x))
                    if hit and (m, p.quality & 0xFF, tid_of(t)) not in INTENDED:
                        bad.append(f'pad {p.quality & 0xFF} egress {d} crosses '
                                   f'trigger {tid_of(t)} hatch box')
        check(f'map {m}: no quest-egress line crosses a trigger hatch box',
              not bad, '; '.join(bad))

        # Quest ITEMS must sit clear of trigger boxes too: the Map 8 key
        # chest used to sit 16 units inside trigger 212's box, so walking
        # up to it from the south teleported you to Map 10 (retest,
        # 2026-07-31). Keys (82), chests (78/618) and the shield halves
        # (878 since 2026-10-17; 870, now retired, and 539 before
        # 2026-10-11) are the walk-up-and-use set.
        USE_SHAPES = {78, 82, 878, 618}
        clutter = []
        for it in items:
            if it.shape not in USE_SHAPES or it.x < 64:
                continue
            for t in trigs:
                xr, yr = (t.npcnum >> 4) * 32, (t.npcnum & 0xF) * 32
                if t.x - xr - 32 <= it.x <= t.x + xr + 32 and \
                   t.y - yr - 32 <= it.y <= t.y + yr + 32:
                    clutter.append(f'shape {it.shape} at ({it.x},{it.y}) '
                                   f'inside/beside trigger '
                                   f'{tid_of(t)} box')
        check(f'map {m}: no quest item sits in a trigger hatch box',
              not clutter, '; '.join(clutter))

    quest_order(arch, gated)


# --- Quest order: no trigger a player can walk onto skips ahead ----------
# Playtest 2026-10-11 replay leg 2 finding 1: Map 8's 212 (Map 8 -> Map 10,
# the RETURN to the Vale) was an engine TeleportEgg, whose hatch is
# unconditional, on the first-visit way to the doors. A fresh player who
# walked over it reached the Vale with steps 3 and 4 skipped. The maps in
# the order a first playthrough reaches them, and the one designed onward
# link out of each (Map 10 has two: the cliffs and the temple, each with its
# own gate in the Vale). An ungated trigger must be one of those links or
# go BACK to a map reached earlier: a return. Anything else carries a
# player ahead of his quest, and must be a gated usecode egg (build_all_
# maps.TELEPORT_TABLE "gated"), whose class the usecode tests run with its
# flag unset and set.
QUEST_MAP_ORDER = (8, 9, 11, 10, 13, 17, 18)
QUEST_FORWARD = {(8, 9), (9, 11), (11, 10), (10, 13), (13, 17), (10, 18)}


def quest_order(arch, gated):
    from build_all_maps import TELEPORT_TABLE
    rank = {m: i for i, m in enumerate(QUEST_MAP_ORDER)}
    for m in QUEST_MAP_ORDER:
        for it in arch.get_map_items(m):
            if not it.is_teleporter or (it.quality & 0xFF) < 200:
                continue
            tid, dst = it.quality & 0xFF, it.mapnum
            if (m, dst) in QUEST_FORWARD:
                kind = 'the route onward'
            elif rank.get(dst, len(rank)) < rank[m]:
                kind = 'a return'
            else:
                kind = None
            check(f'trigger {tid} (map {m} -> {dst}, an engine TeleportEgg) '
                  f'is {kind or "a return or the route onward"}',
                  kind is not None,
                  f'map {dst} comes after map {m} and is not its onward '
                  f'link: walking onto it skips the quest steps between; '
                  f'gate it (a usecode egg on its quest flag)')
    for (m, tid), it in sorted(gated.items()):
        dst = TELEPORT_TABLE[tid]['to_map']
        check(f'trigger {tid} (map {m} -> {dst}) is a gated usecode egg '
              f'at ({it.x},{it.y},{it.z & 0xFF})', True)


gateway_audit()

# --- Arrival corridors: a held input carries the Avatar THROUGH a gateway -
# The bounce class the audit above does not see (playtest 2026-10-10-mover,
# finding 2). A teleport keeps the Avatar's heading, and a held key or
# mouse button keeps him walking on the new map. Walked N into Map 8's
# trigger 212 with the key held 2 s, he arrived on Map 10's pad 212, walked
# on N, and crossed trigger 213's hatch box 228 units ahead: back to Map 8.
#
# The first version of this check (d665e3c) walked straight lines from each
# pad and ended a line at the first refused step. The engine does not stop
# there (playtest 2026-10-10-gateways): U8AvatarMoverProcess::step retries
# a refused step 45 degrees right, then left, and a keyboard hold then FACES
# the way he slid, so it wall-follows. Pad 213's north line "stopped" on
# Map 8's west jamb pillar; the engine slid him NE into the open doorway
# and on to Map 9, 9 holds of 9. So each hold is now replayed by
# avatar_mover.py, the mover verbatim (its docstring has the model and the
# 10-10 rows it reproduces to the unit).
#
#   heading   the engine's 8-way quantiser (avatar_mover.world_dir:
#             Direction_GetWorldDir, direction_util.h; the mouse path
#             Direction_Get(2*dy, dx) in screen space is the same sectors
#             rotated) of the vector from
#             each place a player sets off from to the trigger's marked
#             spot: every arrival pad within ARRIVAL_CLUSTER of it, plus the
#             route's own entry points (APPROACH below). Plus the route's
#             walking direction where it crosses the box.
#   hold      every input (mouse or keyboard, walk or run, either step of
#             the two-step cycle) from the pad itself — the teleport puts
#             him on the egg exactly (MainActor::teleport) — for
#             ARRIVAL_SECONDS. Map 8 is run with its double doors open and
#             closed; they are NONFIXED leaves the model adds.
#   hatch     EggHatcherProcess::run verbatim at every position he passes,
#             with the justTeleported rule (avatar_mover.hold).
#   bound     4 s: the 10-10 report's longest timed hold, about 3,200 units
#             of running. The model's clock runs faster than the engine's
#             on a wall-follow (201's keyboard run below meets 203 at 6.0 s
#             in the model, 7.25-7.92 s in-engine), so the bound errs long.
#
# A trigger the route is MEANT to reach next (GATEWAY_INTENDED) ends a hold
# without failing it. Falls are reported, not modelled past the landing.
ARRIVAL_CLUSTER = 2500
ARRIVAL_SECONDS = 4.0
# trigger id -> (route entry points, route headings through the box)
APPROACH = {
    201: ([(20415, 4000)], ['N']),   # Map 8: up the chamber, through the doors
    212: ([(20415, 4000)], ['E']),   # Map 8: east onto the bone field's slab
    200: ([], ['N']),                # Map 9: back up the throat
    203: ([], ['S']),                # Map 9: on down the hall
    204: ([(13311, 2975)], []),      # Map 10: in off the track, between
    213: ([(13311, 2975)], ['N', 'NE']),  # the court's two columns (NE:
                                     # the 10-10 brief asks for N/NE/NW)
    207: ([], ['S']),                # Map 10: south through the key gate
    211: ([], ['S']),                # Map 10: south down screen17's stair
    202: ([], ['N']),                # Map 11: back up the hall
    205: ([(8640, 22624)], ['S']),   # Map 11: in at the north doorway
    206: ([(4003, 10708)], []),      # Map 13: down from the climb's gap
    209: ([], ['S']),                # Map 13: across the summit plateau
                                     # from its north-east corner (2026-10-17)
    208: ([], ['S']),                # Map 17: back from the city
    210: ([], ['N']),                # Map 18: back from the sanctum
}
COMPASS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
# The Cloud Cliffs <-> Cloud City pair (trigger 209 lands on Map 17's pad,
# 208 on Map 13's) is held harder: every heading, every mode, moving and
# from a standstill, for FULL_HOLD_SECONDS. Verifier 2026-10-17 finding 6:
# from Map 13's pad 208 a keyboard hold NE (not an arrival heading: he
# lands facing S) wall-followed N up the north leg, W along the summit leg
# and S into trigger 209 at 3.5 s run / 5.5-6.1 s walk, back to Map 17;
# the S/W holds at 4 s this check made did not see it. The north leg's
# dead end (build_map_13.CLIMB_STUB) stops that hold.
FULL_HOLD = (208, 209)
FULL_HOLD_SECONDS = 8.0


class Gateways:
    """The LV teleport eggs off the built FIXED.DAT, and one mover World
    per (map, door state), built once and shared by the checks below.
    A gated trigger (build_all_maps.TELEPORT_TABLE "gated": Map 8's 212,
    a usecode egg that teleports only once its quest flag is set) is a
    trigger here like any other: the checks below model a player who may
    hold that flag. first_visit_approach drops it (`gated`)."""

    def __init__(self):
        import avatar_mover as am
        from u8_map import MapArchive
        from exact_reach import DEFAULT_FIXED
        from build_all_maps import TELEPORT_TABLE, gated_teleporters
        self.am = am
        self.shapes, self.anims = am.load_shapes(), am.load_anims()
        arch = MapArchive(DEFAULT_FIXED)
        self.pads, self.trigs, self.tele, self.dest = {}, {}, {}, {}
        for m in (8, 9, 10, 11, 13, 17, 18):
            for it in arch.get_map_items(m):
                if not it.is_teleport_egg:
                    continue
                q = it.quality & 0xFF
                if it.is_teleporter:
                    self.tele.setdefault(m, {})[q] = it
                    self.dest[(m, q)] = it.mapnum
                if q in range(200, 214):
                    (self.trigs if it.is_teleporter else self.pads)[q] = \
                        (m, it)
        self.gated = set()
        for tid, rows in gated_teleporters(arch).items():
            for m, it in rows:
                self.tele.setdefault(m, {})[tid] = it
                self.dest[(m, tid)] = TELEPORT_TABLE[tid]['to_map']
                self.trigs[tid] = (m, it)
                self.gated.add(tid)
        self._items, self._worlds = {}, {}

    def world(self, m, doors=None):
        """Items within 4,500 of the map's LV gateway eggs: a 4 s hold
        covers about 3,200 (Map 8 is a retail map 32,000 across); 8,000 on
        a map with a FULL_HOLD pad, whose 8 s holds cover about 6,400."""
        key = (m, doors)
        if key not in self._worlds:
            if m not in self._items:
                self._items[m] = self.am.map_items(m)
            items = self._items[m]
            if doors:
                items = self.am.with_doors(items, doors)
            eggs = [e for (qm, e) in list(self.pads.values()) +
                    list(self.trigs.values()) if qm == m]
            r = 8000 if any(self.pads[t][0] == m for t in FULL_HOLD
                            if t in self.pads) else 4500
            self._worlds[key] = self.am.World(
                items, self.shapes,
                (min(e.x for e in eggs) - r, min(e.y for e in eggs) - r,
                 max(e.x for e in eggs) + r, max(e.y for e in eggs) + r))
        return self._worlds[key]

    def door_states(self, m):
        return ('open', 'closed') if m == 8 else (None,)

    def boxes(self, m):
        return {k: self.am.hatch_box(e) for k, e in self.tele[m].items()}

    def headings(self, tid):
        src, t = self.trigs[tid]
        entries, route = APPROACH[tid]
        origins = [(q.x, q.y) for (qm, q) in self.pads.values()
                   if qm == src and abs(q.x - t.x) < ARRIVAL_CLUSTER and
                   abs(q.y - t.y) < ARRIVAL_CLUSTER] + list(entries)
        heads = set(route) | {self.am.world_dir(t.y - oy, t.x - ox)
                              for (ox, oy) in origins}
        return [h for h in COMPASS if h in heads]

    def rest_level(self, w, x, y, zmax=64):
        tops = sorted({b[2] + b[5] for b in w.near(x - 64, y - 64, x, y)
                       if b[2] + b[5] <= zmax} | {0}, reverse=True)
        return next((z for z in tops if w.resting(x, y, z)), None)


GW = Gateways()


def arrival_corridors():
    am = GW.am
    for tid in sorted(GW.trigs):
        src, t = GW.trigs[tid]
        if tid not in GW.pads or tid not in APPROACH:
            check(f'gateway {tid}: has an arrival pad and an APPROACH row',
                  False)
            continue
        dst, p = GW.pads[tid]
        start = (p.x, p.y, p.z & 0xFF)
        full = tid in FULL_HOLD
        heads = COMPASS if full else GW.headings(tid)
        bound = FULL_HOLD_SECONDS if full else ARRIVAL_SECONDS
        boxes = GW.boxes(dst)
        intended = {k for k in boxes if (dst, tid, k) in GATEWAY_INTENDED}
        bad, tally = [], {}
        for doors in GW.door_states(dst):
            w = GW.world(dst, doors)
            for h in heads:
                for mode in am.MODES:
                    for standing in ((False, True) if full else (False,)):
                        out, k, pos, secs, _ = am.hold(
                            w, GW.anims, start, h, *mode, boxes, bound,
                            standing=standing)
                        if out == 'trigger' and k in intended:
                            out = f'on to {k}'
                        tally[out] = tally.get(out, 0) + 1
                        if out in ('trigger', 'falls', 'teeters'):
                            what = (f'trigger {k} -> map {GW.dest[(dst, k)]}'
                                    if out == 'trigger' else out)
                            bad.append(f'{h} {am.mode_name(*mode)}'
                                       f'{" standing" if standing else ""}'
                                       f'{" doors " + doors if doors else ""}'
                                       f': {what} at {pos} after {secs:.2f} s')
        summary = ', '.join(f'{v} {k}' for k, v in sorted(tally.items()))
        check(f'gateway {tid} (map {src} -> {dst}): held {"/".join(heads)}'
              f'{", moving and standing," if full else ""} '
              f'from ({p.x},{p.y},{p.z & 0xFF}) for {bound:g} s '
              f'reaches no trigger [{summary}]', not bad,
              f'{len(bad)} holds: ' + '; '.join(bad[:4]))


def arrival_footing():
    """Playtest 2026-10-10-gateways finding 2: Map 8's pad 213 sat at z 0
    inside retail bone piles (tops 8 and 16). The start-box rule let him
    walk off it, NW into a pocket of piles, and there he refused all 8
    headings. Every pad must rest on a real top clear of solids, and his
    first three animations off it in each of the 8 headings must too.
    A first step that runs off an edge to a lethal drop is printed as a
    NOTE: that is the summit-edge hazard (10-10 finding 4), not a wedge."""
    am = GW.am
    for tid in sorted(GW.pads):
        m, p = GW.pads[tid]
        pos = (p.x, p.y, p.z & 0xFF)
        probs, falls = [], []
        for doors in GW.door_states(m):
            w, f = am.footing(GW.world(m, doors), GW.anims, pos)
            probs += w
            falls += f
        check(f'pad {tid} (map {m}) at {pos}: rests clear of solids and '
              f'every first step off it does too', not probs,
              f'{len(probs)}: ' + '; '.join(probs[:3]))
        if falls:
            print(f'  NOTE  pad {tid}: {len(falls)} first steps fall to their '
                  f'death, e.g. {falls[0]}')


# Map 8's double doors, approached the way the route does: north, from
# anywhere across the doorway. Before 2026-10-10 trigger 212's box reached
# x 20484, and a push at x 20450..20464 slid NE along the leaves into it,
# to Map 10, doors open or closed (playtest 10-10-gateways finding 3).
DOOR_APPROACH_X = range(20255, 20480, 16)    # body max x across x(20223,20479]
DOOR_APPROACH_Y = (3199, 3263)


def door_approach():
    am = GW.am
    boxes = GW.boxes(8)
    for doors in ('open', 'closed'):
        w = GW.world(8, doors)
        allowed = {201} if doors == 'open' else set()
        bad, n = [], 0
        for y in DOOR_APPROACH_Y:
            for x in DOOR_APPROACH_X:
                z = GW.rest_level(w, x, y)
                if z is None:
                    continue
                for mode in am.MODES:
                    n += 1
                    out, k, pos, secs, _ = am.hold(
                        w, GW.anims, (x, y, z), 'N', *mode, boxes,
                        ARRIVAL_SECONDS)
                    if out == 'trigger' and k not in allowed:
                        bad.append(f'({x},{y}) {am.mode_name(*mode)}: '
                                   f'trigger {k} at {pos} after {secs:.2f} s')
        check(f'map 8: pushing north at the {doors} double doors ({n} holds '
              f'across the doorway) reaches no trigger but '
              f'{"201 through them" if allowed else "none"}', not bad,
              f'{len(bad)}: ' + '; '.join(bad[:3]))


# The FIRST visit to the doors chamber (playtest 2026-10-11 replay leg 2
# finding 1). The player comes up the spitter corridor to its safe pocket
# (18164,5020) and then heads for the doors: a run E along the corridor,
# then N, NE or NW into the chamber. From the pocket, a mouse run E 3.54 s
# then N 2.5 s crossed trigger 212's slab in-engine and landed him on Map
# 10 with the doors locked, the key in the chest and Map 11 undone. The
# model's run is faster than the engine's (arrival_corridors' note), so
# the turn north is not taken at a time but at every point of the run's
# line: each start 32 apart across the corridor's line, y 5020, and the
# chamber's south half, y 4480, every input, held 4 s, doors closed (they
# are locked on a first visit). Plus the E run itself from the pocket.
#   crossed  with every trigger live (the Vale open), the lines DO cross
#            212's box: the slab is on the way in, so no move of it is
#            proven safe here, and the gate is what protects the visit.
#            (It also keeps this check honest: lines that never reached a
#            box would pass the next one vacuously.)
#   first    with the gated triggers inert (their flag unset, as on every
#            first visit), no hold reaches any trigger at all.
FIRST_VISIT_POCKET = (18164, 5020, 0)
FIRST_VISIT_ROWS = (5020, 4480)
FIRST_VISIT_XS = range(19600, 21400, 32)
FIRST_VISIT_HEADINGS = ('N', 'NE', 'NW')


def first_visit_approach():
    am = GW.am
    w = GW.world(8, 'closed')
    every = GW.boxes(8)
    first = {k: b for k, b in every.items() if k not in GW.gated}
    crossed, bad, n = [], [], 0

    def judge(start, h, mode, standing=False):
        out, k, pos, secs, _ = am.hold(w, GW.anims, start, h, *mode, every,
                                       ARRIVAL_SECONDS, standing=standing)
        what = f'{start} {h} {am.mode_name(*mode)}: '
        if out != 'trigger':
            return
        crossed.append(what + f'{k} at {pos} after {secs:.2f} s')
        if k in GW.gated:
            out, k, pos, secs, _ = am.hold(w, GW.anims, start, h, *mode,
                                           first, ARRIVAL_SECONDS,
                                           standing=standing)
        if out == 'trigger':
            bad.append(what + f'trigger {k} -> map {GW.dest[(8, k)]}'
                       f'{" (gated)" if k in GW.gated else ""} at {pos} '
                       f'after {secs:.2f} s')

    for mode in am.MODES:
        n += 1
        judge(FIRST_VISIT_POCKET, 'E', mode, standing=True)
    for y in FIRST_VISIT_ROWS:
        for x in FIRST_VISIT_XS:
            z = GW.rest_level(w, x, y)
            if z is None:
                continue
            for h in FIRST_VISIT_HEADINGS:
                for mode in am.MODES:
                    n += 1
                    judge((x, y, z), h, mode)
    check(f'map 8 first visit: the way in from the spitter corridor crosses '
          f'a trigger box that is live once the Vale is open ({len(crossed)} '
          f'of {n} holds; the slab is on the way in, so a gate must hold)',
          bool(crossed), 'no hold crosses one: the approach lines no '
          'longer reach the slab, so the next check proves nothing')
    if crossed:
        print(f'  NOTE  e.g. {crossed[0]}')
    check(f'map 8 first visit: {n} holds E from the pocket and N/NE/NW from '
          f'the corridor and the chamber\'s south half, doors locked and '
          f'gated triggers inert ({sorted(GW.gated)}), reach no trigger',
          not bad, f'{len(bad)}: ' + '; '.join(bad[:3]))



# The moved triggers are still there to be used, and to be SEEN: a player
# walks at the marked slab, by mouse or keyboard, and it fires
# (playtest 2026-10-10-maps3 G4, findings 3, 4 and 6). For each trigger:
#   rows     every row across the marker (perpendicular to `heading`, 8
#            apart) from DELIBERATE_BACK outside the hatch box, every input
#            in am.MODES from a standstill, facing `heading` (a keyboard
#            hold walks his facing): it must fire this trigger within 6 s,
#            with no fall on the way. A fall there is a riser: Map 8's slab
#            stood at z=1, zero height, and the engine's scan has no +1
#            offset, so every walk onto it ended unsupported at z 4 and he
#            got on only by dropping 3 (avatar_mover's `falls`).
#   seen     the marker itself, the Avatar at every start and where he
#            fires are at most OVERDRAWN_MAX painted over
#            (item_sorter.overdrawn, as test_schedule_destinations check 4),
#            and the marker's centre is on the 320x200 screen from each
#            start, the camera on the Avatar. Map 8's strip was behind
#            glob 938's wall and roof (100% covered): the Avatar vanished.
#            Map 13's slab was a 301 under the SI_OCCL glob floor (100%).
# On FIXED 332bdeb2 (212's slab (301,3) at (21247,3455,1), 206's at
# (3328,11520,0)) both markers read 100% covered, 128 of 128 holds into 212
# fire only after the 3-unit fall, every start for 212 has the Avatar 100%
# covered, and from 4 of 206's 16 starts its marker is 2-8 px off screen.
# (map, marker (shape, frame, x, y, z), heading, doors)
DELIBERATE = {
    212: (8, (71, 9, 20639, 3967, 0), 'E', 'open'),    # across the chamber
    206: (13, (71, 0, 3775, 11776, 0), 'W', None),     # west off pad 207
}
DELIBERATE_BACK = 128
OVERDRAWN_MAX = 0.10
SCREEN_320x200 = (160, 100)      # half the view, camera on the Avatar


def _screen_offset(frm, to):
    """Screen pixels from the point `frm` to `to` (x, y, z): sx = (x-y)/4,
    sy = (x+y)/8 - z, as item_sorter projects."""
    dx, dy, dz = (to[i] - frm[i] for i in range(3))
    return (dx - dy) / 4, (dx + dy) / 8 - dz


def deliberate_use():
    from item_sorter import ItemSorter
    am = GW.am
    sorter = ItemSorter()
    for tid, (m, mk, h, doors) in sorted(DELIBERATE.items()):
        shape, frame, mx, my, mz = mk
        w, boxes = GW.world(m, doors), GW.boxes(m)
        box = boxes[tid]
        items = GW._items[m]
        if doors:
            items = am.with_doors(items, doors)
        near = [it for it in expand_globs(items, GlobReader())
                if abs(it.x - mx) < 2000 and abs(it.y - my) < 2000]
        marker = [it for it in near if (it.shape, it.frame, it.x, it.y,
                                        it.z & 0xFF) == mk]
        check(f'trigger {tid} (map {m}): its marker, shape {shape} frame '
              f'{frame}, is at ({mx},{my},{mz})', bool(marker))
        drawn = [it for it in near if it not in marker]
        share, over = sorter.overdrawn(drawn, shape, frame, mx, my, mz)
        check(f'trigger {tid} (map {m}): its marker is drawn (map items '
              f'cover {share:.0%} of it)', share <= OVERDRAWN_MAX,
              sorted(over, key=lambda c: -c[-1])[:3])
        mxd, myd = sorter.info(shape)['xd'], sorter.info(shape)['yd']
        centre = (mx - mxd // 2, my - myd // 2, mz)
        d = am.DIRS[h]
        if am.xf(d) and not am.yf(d):
            px = box[0] - DELIBERATE_BACK if am.xf(d) > 0 \
                else box[1] + DELIBERATE_BACK
            starts = [(px, py) for py in range(my - myd + 33, my + 33, 8)]
        else:
            py = box[2] - DELIBERATE_BACK if am.yf(d) > 0 \
                else box[3] + DELIBERATE_BACK
            starts = [(px, py) for px in range(mx - mxd + 33, mx + 33, 8)]
        seen = {}

        def covered(x, y, z):
            if (x, y, z) not in seen:
                seen[(x, y, z)] = sorter.overdrawn(drawn, 1, 0, x, y, z)[0]
            return seen[(x, y, z)]

        bad, hidden, n = [], [], 0
        for (x, y) in starts:
            z = GW.rest_level(w, x, y)
            if z is None:
                bad.append(f'({x},{y}) is no standing spot')
                continue
            sx, sy = _screen_offset((x - 32, y - 32, z + 20), centre)
            if covered(x, y, z) > OVERDRAWN_MAX or \
               abs(sx) > SCREEN_320x200[0] or abs(sy) > SCREEN_320x200[1]:
                hidden.append(f'from ({x},{y},{z}) the Avatar is '
                              f'{covered(x, y, z):.0%} covered, the marker '
                              f'at screen ({sx:+.0f},{sy:+.0f})')
            for mode in am.MODES:
                n += 1
                falls = []
                out, k, pos, secs, _ = am.hold(
                    w, GW.anims, (x, y, z), h, *mode, boxes, 6.0,
                    standing=True, falls=falls)
                what = f'({x},{y},{z}) {am.mode_name(*mode)}: '
                if out != 'trigger' or k != tid:
                    bad.append(what + f'{out} {k or ""} at {pos}')
                elif falls:
                    bad.append(what + f'fires only after falling from '
                               f'{falls[0][0]} to z {falls[0][1]}')
                elif covered(*pos) > OVERDRAWN_MAX:
                    hidden.append(what + f'fires at {pos}, '
                                  f'{covered(*pos):.0%} covered')
        check(f'trigger {tid} (map {m}) fires on purpose: {n} holds {h} '
              f'across its marker, mouse and keyboard, from a standstill, '
              f'no riser', not bad, f'{len(bad)}: ' + '; '.join(bad[:3]))
        check(f'trigger {tid} (map {m}): the Avatar is drawn on the way '
              f'and where it fires, the marker on the 320x200 screen',
              not hidden, f'{len(hidden)}: ' + '; '.join(hidden[:3]))


# Playtest 2026-10-11 build 7 finding 2: holding S off Map 13's pad 207
# ended against the valley's south rim at (4096,12272), and the Avatar was
# not drawn (F-m13-rim-avatar-hidden): the rim's two courses, 96 tall and
# in front of him from the south-east camera, covered 100% of him. The
# east rim did the same along the whole valley floor. Every hold E, SE,
# S or SW off the pad that comes to rest must leave him drawn, and so must
# every standing spot against the valley's south and east edges
# (item_sorter.overdrawn, at most OVERDRAWN_MAX covered). A hold still
# moving at the bound is not judged: walking behind a boulder hides him
# for a step, as it should.
MAP13_SOUTH_EDGE_Y = 12288           # the last terrain row, chunk row 23
MAP13_EAST_EDGE_X = 6656             # the last terrain column, chunk 12


def map13_rim_drawn():
    from item_sorter import ItemSorter
    am = GW.am
    sorter = ItemSorter()
    w, boxes = GW.world(13), GW.boxes(13)
    _, pad = GW.pads[207]
    flat = list(expand_globs(GW._items[13], GlobReader()))

    def covered(x, y, z):
        near = [it for it in flat
                if abs(it.x - x) < 1500 and abs(it.y - y) < 1500]
        return sorter.overdrawn(near, 1, 0, x, y, z)[0]

    hidden, n = [], 0
    for h in ('E', 'SE', 'S', 'SW'):
        for mode in am.MODES:
            for standing in (False, True):
                out, k, pos, secs, _ = am.hold(
                    w, GW.anims, (pad.x, pad.y, pad.z & 0xFF), h, *mode,
                    boxes, 4.0, standing=standing)
                if out != 'stops':
                    continue
                n += 1
                c = covered(*pos)
                if c > OVERDRAWN_MAX:
                    hidden.append(f'{h} {am.mode_name(*mode)}'
                                  f'{" standing" if standing else ""}: '
                                  f'stops at {pos}, {c:.0%} covered')
    check(f'map 13: the {n} holds E/SE/S/SW off pad 207 that stop leave '
          f'the Avatar drawn (at most {OVERDRAWN_MAX:.0%} covered)',
          n > 0 and not hidden, f'{len(hidden)}: ' + '; '.join(hidden[:3]))
    spots = [(x, MAP13_SOUTH_EDGE_Y) for x in range(1600, 6657, 64)] + \
            [(MAP13_EAST_EDGE_X, y) for y in range(640, 12289, 128)]
    hidden, n = [], 0
    for (x, y) in spots:
        if not w.resting(x, y, 0):
            continue
        n += 1
        c = covered(x, y, 0)
        if c > OVERDRAWN_MAX:
            hidden.append(f'({x},{y}) {c:.0%}')
    check(f'map 13: the Avatar is drawn at all {n} standing spots against '
          f'the valley\'s south and east edges', n > 0 and not hidden,
          f'{len(hidden)}: ' + ', '.join(hidden[:6]))


def chain_201_keyboard_run():
    """Playtest finding: Shift+Up held on from Map 8 through 201 wall-follows
    Map 9's hall into 203 and on to Map 11 at 7.25-7.92 s. 203 is the
    route's next gateway (GATEWAY_INTENDED (9, 201, 203)), and the hold is
    nearly twice the bound, so it is reported, not failed."""
    am = GW.am
    m, p = GW.pads[201]
    w, boxes = GW.world(m), GW.boxes(m)
    for f in (False, True):
        out, k, pos, secs, _ = am.hold(w, GW.anims, (p.x, p.y, p.z & 0xFF),
                                       'N', False, True, f, boxes, 12.0)
        print(f'  NOTE  201 keyboard run held N{"" if f else " /2"}: {out}'
              f'{" " + str(k) if k else ""} at {pos} after {secs:.2f} s '
              f'(bound {ARRIVAL_SECONDS:g} s)')


# Playtest 2026-10-10 part 5 finding 8, two "wedges" on Map 10.
#  * The fork east track, (17399..17407, 7959..8223): the outer face of
#    Gunnar's west palisade, x(17407,17439], south of the gate post. Every
#    hold N or NE from there slides up the fence into the gate, and the
#    footing check below finds no position he cannot leave; a hold E is a
#    push into a straight fence, which stops in U8 as it should. Not LV
#    geometry to fix: the run's waypoint lay east, through the fence.
#  * Ezrekal's east door, x 13983, y (12415, 12671]: the desk stood 127
#    units inside it, and runs in through the door stopped on it. The desk
#    moved (build_map_10); a mouse hold W across the doorway must carry
#    him at least EZREKAL_DOOR_CLEAR into the stockade.
#    Build 7 (playtest-2026-10-11-build7 D1) ran W at y 12600-12620 from
#    x 14004-14407, standing after a teleport, and 3 of 4 stopped outside.
#    The rows now run to the south jamb, y 12671, from that whole x span,
#    under way and from a standstill: the doorway's last 31 units south,
#    y (12640, 12671], were on the line of the two typed potions (pinned,
#    159 units in), and a hold at y 12671 stopped 88 units inside.
FORK_EAST_WEDGE = [(17399, 7959), (17407, 7959), (17407, 8095),
                   (17407, 8223)]
EZREKAL_DOOR_X = 13983
EZREKAL_DOOR_CLEAR = 250
EZREKAL_DOOR_YS = range(12479, 12672, 16)    # body (y-64, y] in the door
EZREKAL_DOOR_STARTS = (EZREKAL_DOOR_X + 21, EZREKAL_DOOR_X + 80,
                       EZREKAL_DOOR_X + 208, EZREKAL_DOOR_X + 424)

# Playtest 2026-10-11 part 6 finding 6: walking up the WEST side of
# Hrodny's chest (618, 96x64x16) toward the north-east, the Avatar wedged
# at (21049,8857), 7 units off its west face. The hut prefab's rubble chip
# (526, 64x64x16) sat 32 units north-west of the chest, diagonally
# against it, so N was the rubble, E the chest and NE both, and the
# mover's side retries were exactly those. Mouse holds NE and N from
# along the west face (body x 1, 7 and 16 units off it, every y the face
# meets) must each carry him CHEST_WEST_CLEAR or more.
CHEST_WEST_GAPS = (1, 7, 16)
CHEST_WEST_CLEAR = 128


def chest_west_side(w):
    am = GW.am
    chests = [i for i in GW._items[10] if i.shape == 618 and i.quality == 20]
    check("map 10: exactly one Hrodny's chest (618, lock 20)",
          len(chests) == 1, f'{len(chests)}')
    if len(chests) != 1:
        return
    c = chests[0]
    cx0, cy0, cy1 = c.x - 96, c.y - 64, c.y       # x (cx0, c.x], y (cy0, cy1]
    bad, n = [], 0
    for gap in CHEST_WEST_GAPS:
        for y in range(cy0 + 1, cy1 + 64, 8):      # body (y-64, y] meets it
            start = (cx0 - gap, y, 0)
            for h in ('NE', 'N'):
                for mode in am.MODES:
                    if not mode[0]:
                        continue       # the mouse: the heading stays put
                    n += 1
                    out, _, pos, secs, _ = am.hold(w, GW.anims, start, h,
                                                   *mode, {}, 2.0)
                    moved = max(abs(pos[0] - start[0]),
                                abs(pos[1] - start[1]))
                    if moved < CHEST_WEST_CLEAR:
                        bad.append(f'{start} {h} {am.mode_name(*mode)}: '
                                   f'{out} at {pos} after {secs:.2f} s')
    check(f"map 10 Hrodny's chest at ({c.x},{c.y}): {n} mouse holds NE/N "
          f'from along its west face all carry him {CHEST_WEST_CLEAR}+',
          not bad, f'{len(bad)}: ' + '; '.join(bad[:3]))



def map10_wedges():
    am = GW.am
    w = GW.world(10)
    probs = []
    for (x, y) in FORK_EAST_WEDGE:
        probs += am.footing(w, GW.anims, (x, y, 0))[0]
    check(f'map 10 fork east track: the 10-10 wedge points by Gunnar\'s west '
          f'palisade {FORK_EAST_WEDGE} rest clear and every heading leaves '
          f'them', not probs, f'{len(probs)}: ' + '; '.join(probs[:3]))
    bad, n = [], 0
    for y in EZREKAL_DOOR_YS:
        for x in EZREKAL_DOOR_STARTS:
            for mode in am.MODES:
                if not mode[0]:
                    continue           # the mouse: the heading stays W
                for standing in (False, True):
                    n += 1
                    out, _, pos, secs, _ = am.hold(w, GW.anims, (x, y, 0),
                                                   'W', *mode, {}, 2.0,
                                                   standing=standing)
                    if out == 'stops' and \
                            pos[0] > EZREKAL_DOOR_X - EZREKAL_DOOR_CLEAR:
                        bad.append(f'({x},{y}) {am.mode_name(*mode)}'
                                   f'{" standing" if standing else ""}: '
                                   f'stops at {pos} after {secs:.2f} s')
    check(f"map 10 Ezrekal's east door: {n} mouse holds W across the "
          f'doorway all carry him {EZREKAL_DOOR_CLEAR}+ inside', not bad,
          f'{len(bad)}: ' + '; '.join(bad[:3]))
    chest_west_side(w)


# Playtest 2026-10-17 replay leg 6 finding 3. Pad 210, the return from Map
# 18, is on the temple shelf at the head of screen17's stair, and the stair
# goes down into the pit trigger 211 stands in. 211's box was +/-416 across
# (npcNum 0xD3) and spanned the pit's whole mouth but its east 160 units,
# so a walk off the stair's foot toward the villages went back to Map 18:
# held SW, 306 of 336 holds from the landing. It is +/-96 now
# (build_map_10.TRIGGER_211_RANGE), the strip a walk S off the stair comes
# down. Both sides of that, from the z 0 landing under the stair (every
# TEMPLE_FOOT_XS x TEMPLE_FOOT_YS position he rests at there):
#   leaving   a hold W, SW or NW (to the villages), every input, from a
#             standstill, for ARRIVAL_SECONDS, reaches no trigger; and every
#             mouse hold SW walks out of the pit past 211's box, west of it.
#             (E, NE and N are not asked: the shot's z 112 cell under the
#             stair's foot turns a keyboard hold into that strip.)
#   walking   a mouse hold S from the stair's bottom step either stops
#   in        against that cell (the step's east half, a wedge that is the
#             shot's) or fires 211, and some fire; a hold N from the
#             forecourt, across the box from DELIBERATE_BACK south of it,
#             fires it every time; and so does a hold NW from the forecourt
#             point leg 6 walked in from. A keyboard hold S down the stair
#             is turned SW at the foot like the leaving holds, and leaves.
TEMPLE_FOOT_XS = range(18335, 18536, 16)
TEMPLE_FOOT_YS = range(23263, 23352, 16)
TEMPLE_LEAVE = ('W', 'SW', 'NW')
TEMPLE_STEP = ((23231, 23247), range(18399, 18528, 16), 8)  # ys, xs, top
TEMPLE_LEG6 = (18720, 23808)


def temple_stair_foot():
    am = GW.am
    w, boxes = GW.world(10), GW.boxes(10)
    box = boxes[211]
    foot = [(x, y, 0) for y in TEMPLE_FOOT_YS for x in TEMPLE_FOOT_XS
            if GW.rest_level(w, x, y, zmax=8) == 0]
    check(f'map 10: the temple stair\'s landing has {len(foot)} rest '
          f'positions at z 0', len(foot) >= 30, f'{len(foot)}')
    bad, stuck, n = [], [], 0
    for s in foot:
        for h in TEMPLE_LEAVE:
            for mode in am.MODES:
                n += 1
                out, k, pos, secs, _ = am.hold(w, GW.anims, s, h, *mode,
                                               boxes, ARRIVAL_SECONDS,
                                               standing=True)
                if out == 'trigger':
                    bad.append(f'{s} {h} {am.mode_name(*mode)}: trigger {k} '
                               f'at {pos} after {secs:.2f} s')
                elif h == 'SW' and mode[0] and not (
                        pos[1] >= box[3] and pos[0] < box[0]):
                    stuck.append(f'{s} {am.mode_name(*mode)}: {out} at {pos}')
    check(f'map 10 temple stair foot: {n} holds {"/".join(TEMPLE_LEAVE)} '
          f'from the landing reach no trigger', not bad,
          f'{len(bad)}: ' + '; '.join(bad[:3]))
    check(f'map 10 temple stair foot: every mouse hold SW walks out of the '
          f'pit past trigger 211\'s box (y >= {box[3]}), west of it '
          f'(x < {box[0]})', not stuck, f'{len(stuck)}: ' + '; '.join(stuck[:3]))

    ys, xs, top = TEMPLE_STEP
    fired, wrong, n = 0, [], 0
    for y in ys:
        for x in xs:
            if GW.rest_level(w, x, y, zmax=top) != top:
                continue
            for mode in am.MODES:
                if not mode[0]:
                    continue           # the mouse: the heading stays S
                n += 1
                out, k, pos, secs, _ = am.hold(w, GW.anims, (x, y, top), 'S',
                                               *mode, boxes, ARRIVAL_SECONDS,
                                               standing=True)
                if out == 'trigger' and k == 211:
                    fired += 1
                elif out != 'stops' or pos[1] > 23263:
                    wrong.append(f'({x},{y},{top}) {am.mode_name(*mode)}: '
                                 f'{out} {k or ""} at {pos}')
    check(f'map 10 temple stair: {n} mouse holds S off the bottom step fire '
          f'211 or stop against the cell under it ({fired} fire)',
          fired and not wrong, f'{len(wrong)}: ' + '; '.join(wrong[:3]))
    starts = [(x, box[3] + DELIBERATE_BACK, 'N')
              for x in range(box[0] + 7, box[1], 16)] + [(*TEMPLE_LEG6, 'NW')]
    missed, n = [], 0
    for (x, y, h) in starts:
        z = GW.rest_level(w, x, y)
        for mode in am.MODES:
            n += 1
            out, k, pos, secs, _ = am.hold(w, GW.anims, (x, y, z), h, *mode,
                                           boxes, ARRIVAL_SECONDS,
                                           standing=True)
            if (out, k) != ('trigger', 211):
                missed.append(f'({x},{y},{z}) {h} {am.mode_name(*mode)}: '
                              f'{out} {k or ""} at {pos}')
    check(f'map 10: {n} holds into trigger 211 from the forecourt (N across '
          f'its box, NW from {TEMPLE_LEG6}) all fire it', not missed,
          f'{len(missed)}: ' + '; '.join(missed[:3]))


arrival_corridors()
arrival_footing()
door_approach()
first_visit_approach()
deliberate_use()
map13_rim_drawn()
chain_201_keyboard_run()
map10_wedges()
temple_stair_foot()

# --- Gate walls: tall enough that the jump button cannot climb them ----
# The engine auto-tries climb72..climb16 on jump. Both designed barriers
# were ONE course (40/48 tall) with bare standable tops, and the 2026-07-31
# playtest climbed straight over (tests A and B). The fix is stacked
# courses: every gate line must present a CONTINUOUS solid stack from the
# floor to above 72 — no ledge in between for a chained climb to stand on.

def gate_coverage(mapnum, label, lines):
    """lines: (name, axis, fixed_coord, lo, hi, req_lo, req_hi, exceptions)
    where exceptions maps a coordinate span to a different required
    z-interval (the crack aperture, the boulder doorway)."""
    items, shapes = load_map(mapnum)
    from exact_reach import ExactReach
    xs = [i.x for i in items if i.x >= 64]
    ys = [i.y for i in items if i.y >= 64]
    roi = (min(xs) - 64, min(ys) - 64, max(xs) + 64, max(ys) + 64)
    er = ExactReach(items, shapes, roi)   # for the glob-expanded solids
    solids = er.blockers
    for (name, axis, fc, lo, hi, req, exceptions) in lines:
        worst = None
        for c in range(lo, hi, 32):
            x, y = (c, fc) if axis == 'x' else (fc, c)
            need = req
            for (elo, ehi, ereq) in exceptions:
                if elo <= c <= ehi:
                    need = ereq
            ivs = sorted((bz, bz + bzd) for (bx, by, bz, bxd, byd, bzd)
                         in solids
                         if bx - bxd < x <= bx and by - byd < y <= by)
            cover = need[0]
            for (a, b) in ivs:
                if a <= cover:
                    cover = max(cover, b)
            if cover < need[1]:
                worst = (x, y, cover, need)
                break
        check(f'map {mapnum} {label}: {name} is a continuous stack',
              worst is None,
              worst and f'at ({worst[0]},{worst[1]}) coverage stops at '
                        f'z={worst[2]}, need {worst[3]}')


gate_coverage(18, 'sanctum perimeter (anti-climb, 120 tall)', [
    # The exception spans the whole glob doorway the crack lives in
    # (2751..2879 incl. the body-impossible 2-unit slit west of the fill
    # stub): below z=40 that layer is owned by test_crack_geometry's
    # body-box math; here we only demand the anti-climb courses above.
    ('north/crack line y=6143', 'x', 6143, 2080, 4064, (0, 120),
     [(2751 - 32, 2879, (40, 120))]),
    # Since 2026-10-17 the sanctum is screen04's cave, closed by its own
    # shell; the old rectangle's outline (shoulders, west, east and the
    # south line, moved to y=9343 with the cave's floor) is retail's
    # invisible wall, three 48-unit courses (build_map_18.sanctum_outline).
    ('west shoulder y=6175', 'x', 6175, 1056, 2016, (0, 120), []),
    ('east shoulder y=6175', 'x', 6175, 4128, 5088, (0, 120), []),
    ('west line x=1024', 'y', 1040, 6208, 9312, (0, 120), []),
    ('east line x=5119', 'y', 5119, 6208, 9312, (0, 120), []),
    ('south line y=9343', 'x', 9343, 1056, 5088, (0, 120), []),
    ('hall west wall x=2048', 'y', 2048, 4768, 6112, (0, 120), []),
    ('hall east wall x=4095', 'y', 4095, 4768, 6112, (0, 120), []),
])

# 120 since 2026-09-15: the gate is three courses of the 40-tall stone
# piece (was three of the 48-tall cave piece, 144) — the same stack the
# Map 18 sanctum gate uses. climb72 from the floor still reaches nothing
# on a continuous 120 stack, and no standable in either room tops 40.
gate_coverage(11, 'teleporter-pad room (anti-climb, 120 tall)', [
    ('chamber south band y=22527', 'x', 22527, 6176, 10208, (0, 120),
     [(8449 - 32, 8704, (40, 120))]),   # doorway: boulders below, lintel above
    ('pad north band y=22528', 'x', 22528, 8224, 9184, (0, 120),
     [(8449 - 32, 8704, (40, 120))]),
    ('pad south y=23551', 'x', 23551, 8224, 9184, (0, 120), []),
    ('pad west x=8192', 'y', 8192, 22560, 23520, (0, 120), []),
    ('pad east x=9215', 'y', 9215, 22560, 23520, (0, 120), []),
])

# The reach rule (2026-09-24, art track contract 5). The gate lines above
# prove the wall is a continuous 120 stack; this proves nothing NEAR it
# hands the Avatar a way up. The engine climbs at most 72 in one move, so
# a breach needs a standable top of 48 or more (48 + 72 = 120) that the
# Avatar can reach, and reaching it is a chain of climbs of 72 or less,
# each onto something ADJACENT (the climb anims step forward one body
# width; a ledge across the room is no help). So: within two tiles of a
# gate line, take every EXPOSED top (the continuous stack coverage at each
# solid's footprint: a course inside a wall is not exposed, the wall's top
# is), mark reachable every top the floor reaches (72 or less), then chain
# through adjacency, and fail if any reachable top is 48 or higher. Today
# the chamber's sealing boulders top 40 and the lintel over them is 120:
# 40 + 72 = 112 falls short, which is the designed margin. The pillars top
# 80 since custom art 865 (footpad z=10); they stand 1023 units from the
# line, outside this rule's reach, and nothing beside them tops 8.
def gate_reach(mapnum, label, lines, reach=256, climb=72, danger=48, step=64):
    items, shapes = load_map(mapnum)
    from exact_reach import ExactReach
    xs = [i.x for i in items if i.x >= 64]
    ys = [i.y for i in items if i.y >= 64]
    roi = (min(xs) - 64, min(ys) - 64, max(xs) + 64, max(ys) + 64)
    solids = ExactReach(items, shapes, roi).blockers

    def stack_top(x, y):
        ivs = sorted((bz, bz + bzd) for (bx, by, bz, bxd, byd, bzd) in solids
                     if bx - bxd < x <= bx and by - byd < y <= by)
        cover = 0
        for (a, b) in ivs:
            if a <= cover:
                cover = max(cover, b)
        return cover

    def adjacent(a, b):
        # a's xy box grown by one body width overlaps b's xy box
        (ax, ay, axd, ayd), (bx, by, bxd, byd) = a, b
        return not (ax + step <= bx - bxd or bx <= ax - axd - step
                    or ay + step <= by - byd or by <= ay - ayd - step)

    for (name, axis, fc, lo, hi, _req, _exc) in lines:
        near = []                                   # (top, xy box)
        for (bx, by, bz, bxd, byd, bzd) in solids:
            if axis == 'x':      # the line runs along x at y = fc
                ok = (by - byd <= fc + reach and by >= fc - reach
                      and bx >= lo and bx - bxd <= hi)
            else:
                ok = (bx - bxd <= fc + reach and bx >= fc - reach
                      and by >= lo and by - byd <= hi)
            if ok:
                near.append((stack_top(bx - bxd // 2, by - byd // 2),
                             (bx, by, bxd, byd)))
        reachable = [n for n in near if n[0] <= climb]
        grew = True
        while grew:
            grew = False
            for n in near:
                if n in reachable:
                    continue
                if any(n[0] <= r[0] + climb and adjacent(r[1], n[1])
                       for r in reachable):
                    reachable.append(n)
                    grew = True
        bad = sorted((t, b[:2]) for (t, b) in reachable if t >= danger)
        check(f'map {mapnum} {label}: no reachable top of {danger}+ within '
              f'{reach} of {name} (exposed tops '
              f'{sorted({t for t, _ in near})}, reachable '
              f'{sorted({t for t, _ in reachable})})',
              not bad, f'{bad[:4]}')


gate_reach(11, 'teleporter-pad room (reach rule)', [
    ('chamber south band y=22527', 'x', 22527, 6176, 10208, (0, 120), []),
    ('pad north band y=22528', 'x', 22528, 8224, 9184, (0, 120), []),
    ('pad south y=23551', 'x', 23551, 8224, 9184, (0, 120), []),
    ('pad west x=8192', 'y', 8192, 22560, 23520, (0, 120), []),
    ('pad east x=9215', 'y', 9215, 22560, 23520, (0, 120), []),
])

# ...and the doorway is still plugged: exactly two quality-299 boulders.
_items11, _ = load_map(11)
_boulders = [i for i in _items11 if i.quality == SEALING_BOULDER_QUALITY
             and i.shape == 66]
check('map 11: the two sealing boulders plug the doorway',
      sorted((b.x, b.y) for b in _boulders) == [(8576, 22528), (8704, 22528)],
      f'found {[(b.x, b.y) for b in _boulders]}')

# --- Map 13: the climb ------------------------------------------------
# Structural first: the generator is the fix, so pin what makes it correct.
tiles = climb_tiles()
risers = [b[2] - a[2] for a, b in zip(tiles, tiles[1:])]
steps = [max(abs(b[0] - a[0]), abs(b[1] - a[1]))
         for a, b in zip(tiles, tiles[1:])]
# The riser rule is an ENUMERATED SET, not a bound. scanForValidPosition
# probes SEARCH_OFFSETS_U8 = {0, -4, 4, -8, 8} and nothing else, so a
# 1-unit riser is refused exactly as a 9-unit one is. The predecessor of
# this check asserted only `max(riser) <= 8`, which the 2026-07-31 rebuild
# satisfied with risers of 1 and 2 — and the climb was unwalkable in
# ScummVM (F10). Assert membership, not magnitude.
_legal = {d for d in Z_SEARCH_OFFSETS_U8 if d >= 0}
_illegal = sorted({r for r in risers if r not in _legal})
check("map 13 climb: every riser is one the engine can actually step",
      risers and not _illegal,
      f'risers outside {sorted(_legal)}: {_illegal}')
check('map 13 climb: monotonic — no step back down the cliff',
      all(r >= 0 for r in risers))
check('map 13 climb: contiguous — one tile per 128-unit step',
      steps and max(steps) == 128, f'max gap {max(steps) if steps else 0}')
check('map 13 climb: tops out on the summit plateau surface',
      tiles[-1][2] == CLIMB_Z_TOP, f'ends at z={tiles[-1][2]}')
check('map 13 climb: the summit plateau is itself on the z lattice',
      CLIMB_Z_TOP % CLIMB_Z_STEP == 0,
      f'CLIMB_Z_TOP={CLIMB_Z_TOP} is not a multiple of {CLIMB_Z_STEP}')

route(13, 'Cloud Cliffs', (4096, 11776, 0), [
    (True, 'the summit is walkable from the Lost Vale arrival pad',
     4351, 1919, 120),
    (True, 'TRIGGER 209 to Cloud City is reachable', 4351, 2303, 120),
])

# --- Map 17: the shield halves ---------------------------------------
# Rebuilt 2026-10-17 as the open 1994 city: the halves stand where the
# shots show them (screen11 beside the obelisk, screen12 in the throne
# nook), the arrival pad is on the gold landing and trigger 208 on the
# pier south of the void channel, reached round its east end.
route(17, 'Cloud City', (4608, 9984, 0), [
    (True, 'shield half 1 (the sun, beside the obelisk) is reachable',
     4259, 7199, 0),
    (True, 'shield half 2 (the eye, in the throne nook) is reachable',
     3559, 3311, 0),
    (True, 'the scroll court is reachable', 3328, 1536, 0),
    (True, 'the walkway is reachable, on its top', 2303, 3103, 8),
    (True, 'the east court is reachable', 6271, 5823, 0),
    (True, 'the return TRIGGER 208 is reachable', 4608, 11008, 0),
])
# The way back crosses the bridge between its two gem pillars. At x 5823
# and 5951 they left a 64-unit body one 32-unit band of x, and a mouse walk
# could not thread it (verifier 2026-10-17 finding 5); a body twice the
# Avatar's, 128 square, could not cross at all. Against the bridge's curbs
# they leave 192, so the 128 body crosses and the Avatar has 128 of x.
route(17, 'Cloud City, a 128-square body', (4608, 9984, 0), [
    (True, 'the return TRIGGER 208 is reachable across the bridge',
     4608, 11008, 0),
], body=(128, 128, 40))

# --- Map 18: the Tiny Tar gate, proved by reachability ----------------
# Not a hand-picked wall line this time (test_crack_geometry does that):
# an unassisted flood from the arrival pad has to STOP at the crack for
# the full-size Avatar and get through it for the shrunken one.
route(18, 'Ancient Temple, full size', (3072, 1792, 0), [
    (True, 'the return TRIGGER 210 is reachable', 3072, 1408, 0),
    (False, 'the Inner Sanctum is SEALED to the full-size Avatar',
     2864, 6504, 0),
])
route(18, 'Ancient Temple, shrunken', (3072, 1792, 0), [
    (True, 'the Inner Sanctum opens to the shrunken Avatar (DD-005)',
     2864, 6504, 0),
    # screen04's shrine (2026-10-17): round the rock at the shot's top to
    # the altar, where the shot stands the Avatar, and to the skull.
    (True, "the altar is reachable, at screen04's Avatar spot",
     3256, 8152, 0),
    (True, 'the priestess\'s skull (331) is reachable', 2496, 8512, 0),
], body=TINY_BODY)

# --- Map 11: the sealing boulders are the only thing in the way -------
# The four talismans and the Four Pillars chamber are goals here since
# 2026-09-15 (cleanup plan, Map 11 boundary): the sections get dressed —
# terraces, causeways, pools — and every one of those changes traversal.
# The engine's Avatar (shape 1: SI_SOLID|SI_OCCL, no SI_DAMAGING, so
# current_map.cpp:784's blockflagmask is SOLID alone) walks onto lava and
# burns. This flood adds SI_DAMAGING to the mover flags, so it is STRICTER
# than the engine: REACHED means a walking route exists that never has to
# stand on a damaging tile. That is the cleanup plan's acceptance for the
# dressed sections. The talismans' own coordinates are pins
# (map_pins.json) and do not move.
#
# SI_DAMAGING is not the whole of it. The Fire section's lava lakes (glob
# 802, 16x shape 409) are LAND|SOLID, and they burn through their class,
# CLRLAVA's gotHit (exact_reach.HURT_SHAPES_U8): a 2026-10-10 run walked
# from the Fire talisman toward the doorway and died, hp 30 -> 0, with
# nothing else near (playtest-2026-10-10-full-run-part5 finding 1). Every
# flood here therefore also keeps LAVA_MARGIN clear of every lava tile,
# and the pad flood reaching the talismans, the chamber and (boulders
# removed) the exit means each talisman joins both by such a route.
LAVA_MARGIN = 128          # two body widths of daylight
route(11, 'Elemental Dungeon, as the Avatar walks', (9728, 1792, 0), [
    (True, 'the Talisman of Earth is reachable', 2047, 5631, 4),
    (True, 'the Talisman of Air is reachable', 17152, 5120, 0),
    (True, 'the Talisman of Fire is reachable, no lava on the way',
     5631, 18943, 4),
    (True, 'the Talisman of Water is reachable', 12799, 18943, 4),
    (True, 'the Four Pillars chamber (centre) is reachable', 8192, 20992, 0),
    (False, 'the exit to the Vale is plugged by the sealing boulders',
     8960, 23296, 0),
], step=16, mover_flags=SI_SOLID | SI_DAMAGING, hurt_margin=LAVA_MARGIN)
route(11, 'Elemental Dungeon, boulders removed', (9728, 1792, 0), [
    (True, 'and opens once the four-pillar puzzle destroys them',
     8960, 23296, 0),
], step=16, drop=lambda it: it.quality == SEALING_BOULDER_QUALITY,
      mover_flags=SI_SOLID | SI_DAMAGING, hurt_margin=LAVA_MARGIN)


# A route existing is not enough: the 10-10 run had one (the causeways)
# and died on the line a player actually walks — straight from the Fire
# talisman to the only doorway out. The lines a player takes from the
# talisman must keep LAVA_MARGIN from every hazard: the lava lakes and
# the SI_DAMAGING pools and flame tiles alike. Points are the Avatar's
# max corner at z 0 (the causeway is 8 up, so z 0 is the stricter test).
#
# The three lines that run on north to the north wall were added after
# build 7 (playtest-2026-10-11-build7 L1): a walk held north from the
# talisman's column crossed the doorway's latitude and touched FIREPIT
# 12231 (318) at (5632,16384), 2 hp. Past the pit stood lake chunk (8,2),
# a second pit and a flame tile, all in the column.
FIRE_TALISMAN_STAND = (5584, 18864)   # where the 10-10 run took it from
FIRE_DOOR = (6080, 16767)             # the east doorway, y (16384, 16896]
FIRE_NORTH_WALL_Y = 14464             # the Avatar against the north wall
FIRE_LINES = {
    'straight to the doorway': [FIRE_TALISMAN_STAND, FIRE_DOOR],
    'north along the talisman, then east':
        [FIRE_TALISMAN_STAND, (5584, 16767), FIRE_DOOR],
    "north at x 5456, the 10-10 run's fatal line":
        [(5456, 18864), (5456, 16767), FIRE_DOOR],
    "straight north from the talisman to the north wall, build 7's line":
        [FIRE_TALISMAN_STAND, (5584, FIRE_NORTH_WALL_Y)],
    'north at x 5456 to the north wall':
        [(5456, 18864), (5456, FIRE_NORTH_WALL_Y)],
    'north-east to the east wall, then north along it':
        [FIRE_TALISMAN_STAND, (6080, 18368), (6080, FIRE_NORTH_WALL_Y)],
    'the causeways: the branch west, the spine north, then east':
        [FIRE_TALISMAN_STAND, (5375, 18783), (3551, 18783), (3551, 16863),
         (6080, 16863)],
    'on through the Water section to the Four Pillars chamber':
        [FIRE_DOOR, (8576, 16767), (8576, 19519), (8192, 20992)],
}


def hazard_boxes(mapnum):
    """(x, y, z, xd, yd, zd, shape) of every item that hurts on contact:
    SI_DAMAGING, or a HURT_SHAPES_U8 shape. Globs expanded."""
    items, shapes = load_map(mapnum)
    out = []
    for it in expand_globs(items, GlobReader()):
        if it.flags & (FLG_CONTAINED | FLG_EQUIPPED) or \
                not 0 <= it.shape < len(shapes):
            continue
        si = shapes[it.shape]
        if it.shape in HURT_SHAPES_U8 or si.flags0 & SI_DAMAGING:
            xd, yd = si.footpad_x * 32, si.footpad_y * 32
            if it.flags & FLG_FLIPPED:
                xd, yd = yd, xd
            out.append((it.x, it.y, it.z & 0xFF, xd, yd, si.footpad_z * 8,
                        it.shape))
    return out


def line_clearance(boxes, pts, z=0, step=8):
    """The least daylight, in world units, between the Avatar's box walked
    along the polyline `pts` and any box in `boxes` at a height it would
    touch: (clearance, where, (shape, x, y)). Boxes are closed, as
    sweepTest's are, so 0 is contact and a negative value is overlap."""
    bxd, byd, bzd = AVATAR_BODY
    worst = (1 << 30, None, None)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, max(abs(x1 - x0), abs(y1 - y0)) // step)
        for k in range(n + 1):
            x, y = x0 + (x1 - x0) * k // n, y0 + (y1 - y0) * k // n
            for (hx, hy, hz, hxd, hyd, hzd, sh) in boxes:
                if hz > z + bzd or hz + hzd < z:
                    continue
                c = max(hx - hxd - x, x - bxd - hx, hy - hyd - y, y - byd - hy)
                if c < worst[0]:
                    worst = (c, (x, y), (sh, hx, hy))
    return worst


_hazards11 = hazard_boxes(11)
for _name, _pts in FIRE_LINES.items():
    _c, _at, _what = line_clearance(_hazards11, _pts)
    check(f'map 11 Fire talisman, {_name}: at least {LAVA_MARGIN} clear of '
          f'lava and flame (least {_c})', _c >= LAVA_MARGIN,
          f'shape {_what[0]} at ({_what[1]},{_what[2]}) from the Avatar at '
          f'{_at}' if _what else '')


# HURT_SHAPES_U8 must name every shape placed on an LV map whose class's
# gotHit (event 6, which the engine runs on every move that touches the
# item, item.cpp collideMove) reaches Item::receiveHit, directly or
# through the routines it calls and spawns. Build 7 lost 2 hp to FIREPIT
# (318) on Map 11 while the list held only the lava, 409.
LV_MAPS = (8, 9, 10, 11, 13, 17, 18, 39)
# CLRWATER's gotHit drowns only a hitter that is ON the water (056E:00A2
# Item::isOn, else return), and the water is SOLID|SEA without LAND, so no
# walker stands on it: touching it does not hurt.
HURT_EXEMPT = {347: 'CLRWATER drowns only what stands on it'}


def gothit_hurts():
    """{shape: class name} of the shapes placed on LV maps whose gotHit
    reaches Item::receiveHit (calls and spawns followed six deep)."""
    import re
    sys.path.insert(0, os.path.join(SRC_DIR, '..', '..', 'usecode-disasm',
                                    'src'))
    from u8_flex import UsecodeFlexArchive
    from u8_usecode_disasm import UsecodeClass, UsecodeDisassembler
    arc = UsecodeFlexArchive(os.path.join(SRC_DIR, '..', '..', '..',
                                          'shared', 'build', 'EUSECODE.FLX'))
    dis, listing = UsecodeDisassembler(), {}

    def lines(cid):
        if cid not in listing:
            data = arc.get_class_data(cid) if arc.class_exists(cid) else b''
            listing[cid] = dis.disassemble_class(data, cid).splitlines() \
                if data else []
        return listing[cid]

    def reaches(cid, off, seen, depth=0):
        if (cid, off) in seen or depth > 6:
            return False
        seen.add((cid, off))
        body = lines(cid)
        start = next((k for k, s in enumerate(body)
                      if re.match(r'\s+%04X:' % off, s)), None)
        if start is None:
            return False
        for s in body[start:]:
            if 'Item::receiveHit' in s:
                return True
            m = re.search(r'\b(?:call|spawn)\b.*; class ([0-9A-F]{4}) '
                          r'offset ([0-9A-F]{4})', s)
            if m and reaches(int(m.group(1), 16), int(m.group(2), 16),
                             seen, depth + 1):
                return True
            if re.search(r'\s79\s+end\s*$', s):
                return False
        return False

    placed = set()
    for mapnum in LV_MAPS:
        items, _ = load_map(mapnum)
        placed.update(it.shape for it in expand_globs(items, GlobReader())
                      if not it.flags & (FLG_CONTAINED | FLG_EQUIPPED))
    out = {}
    for shape in sorted(placed):
        data = arc.get_class_data(shape) if arc.class_exists(shape) else b''
        if not data:
            continue
        events = UsecodeClass(shape, None, data).events
        if 6 in events and reaches(shape, events[6], set()):
            out[shape] = arc.get_class_name(shape)
    return out


_hurts = gothit_hurts()
check('the LV maps place shapes whose gotHit hurts (the survey is live)',
      409 in _hurts and 318 in _hurts, f'{_hurts}')
for _shape, _name in sorted(_hurts.items()):
    if _shape in HURT_EXEMPT:
        continue
    check(f'shape {_shape} ({_name}) hurts on contact: in HURT_SHAPES_U8',
          _shape in HURT_SHAPES_U8, f'HURT_SHAPES_U8 = {HURT_SHAPES_U8}')

# --- Map 9 and Map 10: the long walks --------------------------------
route(9, 'Galjeron Chamber', (13696, 14208, 0), [
    (True, 'TRIGGER 203 to the Elemental Dungeon is reachable',
     14336, 16760, 0),
    (True, 'TRIGGER 200 back to Pagan is reachable', 13759, 12031, 0),
    # screen10's dais (2026-10-17): the top the shot stands the Avatar on,
    # up the stair its invisible treads make climbable.
    (True, 'the guardian dais top (screen10) is reachable up its stair',
     14360, 12792, 56),
])
route(10, 'Lost Vale', (12800, 2560, 0), [
    (True, 'the Sacred Circle is reachable (steps 14-15)', 20480, 16896, 0),
    (True, "Ezrekal's dwelling: the ground outside the stockade's west wall",
     12288, 12288, 0),
    (True, "Ezrekal is reachable inside her stockade (steps 9-10)",
     12800, 12544, 0),
    (True, 'TRIGGER 207 to the Cloud Cliffs is reachable', 7168, 24064, 8),
    (True, 'TRIGGER 211 to the Ancient Temple is reachable',
     18432, 23552, 0),
    (True, 'TRIGGER 213 back to Pagan is reachable', 12800, 1792, 0),
    (True, 'TRIGGER 204 back to the Elemental Dungeon is reachable',
     11904, 2048, 0),
    # Added 2026-09-15 ahead of the landscape pass (cleanup plan section 3:
    # goals go in BEFORE the map is dressed). The villages, the lake
    # causeway, the Passage Test grounds and Ragnar's cache were never
    # goals; the last two are the ones a 4-unit-lattice mover can refuse
    # while map_walkability (STEP_Z=24) still passes them.
    (True, "Hoskuld village: the gathering slab is reachable", 5120, 7168, 0),
    (True, "Gunnar village: the well is reachable", 18688, 7680, 0),
    (True, "Gunnar village: Hrodny's chest is reachable (step 16)",
     21104, 8768, 0),
    (True, 'the lake causeway is reachable (step 7)', 13824, 19456, 8),
    (True, 'the Passage Test plant is reachable on foot (step 8)',
     12800, 29300, 64),
    (True, "Ragnar's cache: the boulder crown is reachable (step 7 bag)",
     16447, 25727, 56),
], step=16)

# Ezrekal is in her garden, south of the stockade, in firstebb and
# lastebb (EZREKAL.UNK schedule; test_schedule_destinations checks the
# point itself), and step 12 hands her the root there. A 10-10 run could
# not find the way from the house (playtest part 5 finding 5): it stood
# at (12779,12155), outside the north wall and west of its gap, x (12799,
# 12927]. The ways out are the east door and the south wall's fallen
# panel, x (13055, 13183]; this pins the walk from inside the house to
# her two garden points and out to the track.
route(10, "Ezrekal's house", (12640, 12704, 0), [
    (True, "the garden, where the 10-10 run saw her", 12580, 13124, 0),
    (True, "the garden, her firstebb/lastebb schedule point",
     12895, 13439, 0),
    (True, 'the track south from the fork, past her east door',
     14207, 12543, 0),
], step=16)

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

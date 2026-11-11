#!/usr/bin/env python3
"""
lv_monster_eggs.py — one LV monster group: its eggs and the MONEGG trigger
that hatches them.

HOW U8 HATCHES A MONSTER (2026-10-11, playtest-2026-10-11-monsters finding 1).
A monster egg (shape 500) is a MonsterEgg, which derives from Item, not Egg,
so the EggHatcherProcess never sees it and walking onto it does nothing.
Retail hatches them from a MONEGG trigger: an UnkEgg (shape 73) of quality
2, class 0x481. MONEGG::hatch (EUSECODE 0481:0080):

  * returns at once if bit 0x80 of its own mapNum is set; sets it at the
    end, and its leaveFastArea (0481:011D) clears it — one hatch per stay
    in the fast area;
  * area-searches 112*32 = 3584 units round itself (x and y, any z;
    CurrentMap::areaSearch) for shape 500;
  * hatches every egg whose mapNum >> 3 equals its own mapNum & 0x1F;
  * destroys a hatched egg whose frame is not 0 (a one-shot egg). Frame 0
    eggs hatch again on every return, as 395 of retail's 418 do. Retail's
    eggs are NONFIXED, so a destroyed one is gone for good; ours are FIXED,
    which World::loadMap reloads on every map change, so a one-shot LV egg
    hatches once per visit to its map. It destroys the egg whether or not
    a monster came of it.

EVERY LV EGG IS ONE-SHOT (2026-10-11, playtest-2026-10-11-monsters2
finding 3). A frame-0 group hatched again on each return through its
trigger while the last hatch's monsters still stood there: golems 125 and
129 at one spot, four more on every pass. A monster that leaves the fast
area is destroyed (FLG_FAST_ONLY), so one-shot costs nothing a player
could miss: a group he has left behind is gone either way, and comes back
with the map. No LV group needs respawn for its gameplay.

MonsterEgg::hatch (world/monster_egg.cpp) creates the actor FAST_ONLY and
DISPOSABLE at the egg's own position, loads its stats from u8monsters.ini
and sets the activity in the egg's mapNum & 7: 0 loiter, 1 combat, 2 stand.
Its `canExistAt` test never refuses: Item::canExistAt passes shapeflags 0
to CurrentMap::getPositionInfo, whose blocker test ANDs them, so a monster
hatches even inside a solid (the placement checks are ours, in
test_monster_eggs.py). Retail: 292 of 418 eggs combat, 120 loiter, 6
stand. A loitering monster never attacks until it is hit (finding 4), so
every LV egg is combat: CombatProcess::seekTarget then takes the first
enemy within 768 units, and the Avatar (NPCDATA alignment 0x1A, align bits
0xA) is an enemy of every LV monster.

A COMBAT MONSTER MUST HATCH INSIDE THE FAST AREA (playtest-2026-10-11-
monsters2 finding 1). MonsterEgg::hatch moves the actor and then sets its
activity. Inside the fast area the move calls Item::enterFastArea first,
so combat sticks. Outside, the actor keeps the combat flag but
CombatProcess::run returns while it is not FLG_FASTAREA, and when the
Avatar comes near, Item::enterFastArea (fork item.cpp:1913-1917) clears
combat and stands it: golems at flags 0x800 went to 0 and stood beside him.
CurrentMap::updateFastArea makes fast the 512-unit chunks whose screen box
meets the game screen grown by half a chunk (`fast_chunks`). At 320x200,
with the camera on the Avatar, that reaches about three chunks (1,536-
2,047 units) north, south, east and west, three to five along the screen's
vertical (north-west and south-east) and one along its horizontal
(north-east, south-west). And a monster that does not see the Avatar at
once loiters round its egg (CombatProcess::waitForTarget, LoiterProcess:
+/- 320), and is destroyed when it walks out of the fast area, so its
loiter square must be fast as well (`hatch_fast_problem`). That is what
killed one lane harpie of two (finding 4) [INFERENCE: no log of it].
Retail does not keep to this. Of its 136 (combat egg, trigger) pairs
(pristine FIXED.DAT plus U8SAVE.000's NONFIXED.DAT), 55 hatch outside the
fast area from some position in the box and 53 more could loiter out of
it; 28 meet the rule. So in ScummVM retail monsters hatch passive too
[INFERENCE: whether the 1994 engine kept their combat is not known; the
engine-side alternative, keeping combat on fast-area entry for a
hatched monster, is the fork's to decide]. A combat LV group therefore
either hatches round a trigger on the way, near enough, or, where its
monsters stand off the way, from a trigger off the way beside them: then
every position in the box is in each monster's seek square
(`wakes_at_once`) and a player who wanders in meets it fighting.

The trigger's box is the EggHatcherProcess's: x +/- 32*(npcNum >> 4),
y +/- 32*(npcNum & 0xF), the Avatar's z within 48 of the egg's.

A hatched combat monster wakes when the Avatar's reference point is inside
its seek square, CurrentMap::areaSearch round the monster with range 768:
x in (mx - xd - 769, mx + 768], the same on y (`seek_square`).

RETAIL'S LAYOUT, surveyed from U8SAVE.000's NONFIXED.DAT (130 triggers,
127 of them with eggs of their group in reach): the nearest hatched egg
sits a median 861 units (Chebyshev) from its trigger, 10th-90th percentile
561-1,504, the farthest 3,441, so a group hatches out of sight ahead of
the player. Boxes are either a square (+/-64 to +/-448) or a strip across
the way in (480 x 32, 32 x 480), and in 98 of the 127 the eggs sit on the
trigger's own z.
"""

from u8_map import MapItem

# Engine/usecode constants, mirrored for the test (test_monster_eggs.py).
MONEGG_RANGE = MapItem.MONEGG_RANGE        # 0481:00AD push 112 * 32
HATCH_Z = 48                               # EggHatcherProcess z_range
SEEK_RANGE = 768                           # CombatProcess::seekTarget
ACTIVITY_COMBAT = 1                        # Actor::setActivityU8 case 1
LOITER_RANGE = 320                         # LoiterProcess::run: anchor +/- 32*10
MAP_CHUNK = 512                            # CurrentMap::_mapChunkSize, U8
CAMERA_Z = 20                              # CameraProcess: avatar z + 20
FAST_DIMS = (320, 200)                     # the smallest game screen


def fast_chunks(cam_x, cam_y, cam_z, dims=FAST_DIMS):
    """The map chunks CurrentMap::updateFastArea makes fast with the camera
    at (cam_x, cam_y, cam_z) (from == to), on a dims-sized game screen:
    a coarse square of xy_limit chunks round the camera's chunk, cut to
    the chunks whose screen box (ChunkOnScreen) meets the screen grown by
    half a chunk."""
    w, h, ch = dims[0], dims[1], MAP_CHUNK
    sx = int((cam_x - cam_y) / 4)          # C++ division truncates
    sleft = sx - (w // 2 + ch // 4)
    sright = sx + (w // 2 + ch // 4)
    stop = (cam_x + cam_y) // 8 - cam_z - (h // 2 + ch // 8)
    sbot = (cam_x + cam_y) // 8 - cam_z + (h // 2 + ch // 8)
    xy_limit = ((w // (ch // 2) + 3) + (h // (ch // 4) + 7)) // 2
    out = set()
    for cy in range(cam_y // ch - xy_limit, cam_y // ch + xy_limit + 1):
        for cx in range(cam_x // ch - xy_limit, cam_x // ch + xy_limit + 1):
            scx, scy = (cx - cy) * ch // 4, (cx + cy) * ch // 8
            if not (scx + ch // 4 <= sleft or scx - ch // 4 >= sright or
                    scy - ch // 2 >= sbot or scy + ch // 4 <= stop):
                out.add((cx, cy))
    return out


def loiter_chunks(x, y):
    """The chunks a monster hatched at (x, y) may be in while it waits for
    a target: CombatProcess::waitForTarget loiters it, and each
    LoiterProcess step walks it to its anchor (the egg) +/- LOITER_RANGE.
    An item is in the chunk of its reference point (its max corner), so
    the body's size does not enter."""
    return {(cx, cy)
            for cx in range((x - LOITER_RANGE) // MAP_CHUNK,
                            (x + LOITER_RANGE) // MAP_CHUNK + 1)
            for cy in range((y - LOITER_RANGE) // MAP_CHUNK,
                            (y + LOITER_RANGE) // MAP_CHUNK + 1)}


def box_positions(trigger, xrange, yrange, body=(64, 64)):
    """The corners of the Avatar reference points that fire a trigger at
    (x, y): EggHatcherProcess::run, x1 <= px and px - xd < x2 on x (and
    the same on y), so px in [tx - 32*xr, tx + 32*xr + xd - 1]."""
    tx, ty = trigger
    return [(x, y) for x in (tx - 32 * xrange, tx + 32 * xrange + body[0] - 1)
            for y in (ty - 32 * yrange, ty + 32 * yrange + body[1] - 1)]


def hatch_cameras(trigger, xrange, yrange, zs):
    """Camera points for every Avatar position that fires a trigger at
    `trigger` (x, y): the corners of its box, at each standing z in `zs`.
    A chunk's fast-area test is a set of half-planes and intervals in the
    camera's x, y and z, so a chunk fast from every corner is fast from
    everywhere between."""
    return [(x, y, z + CAMERA_Z)
            for x, y in box_positions(trigger, xrange, yrange) for z in zs]


def seek_square(x, y, shape_footpad):
    """(x_lo_excl, x_hi, y_lo_excl, y_hi): where an Avatar's reference point
    wakes a combat monster standing at (x, y) with footpad (xd, yd, _)."""
    xd, yd = shape_footpad[0], shape_footpad[1]
    return (x - xd - SEEK_RANGE - 1, x + SEEK_RANGE,
            y - yd - SEEK_RANGE - 1, y + SEEK_RANGE)


def wakes_at_once(trigger, xrange, yrange, egg, shape_footpad):
    """Is every Avatar position that fires the trigger inside the seek
    square of a monster on `egg`? Then CombatProcess::seekTarget finds him
    on its first run and the monster never loiters at its hatch."""
    x0, x1, y0, y1 = seek_square(egg[0], egg[1], shape_footpad)
    return all(x0 < px <= x1 and y0 < py <= y1
               for px, py in box_positions(trigger, xrange, yrange))


def hatch_fast_problem(trigger, xrange, yrange, zs, egg, shape_footpad,
                       dims=FAST_DIMS):
    """'' if a monster hatched from `egg` (x, y) is inside the fast area
    whichever position in the box fires the trigger, at each standing z in
    `zs`, else why not.

    Inside, it is fast: Item::move calls enterFastArea, which clears
    combat (item.cpp, Item::enterFastArea) BEFORE MonsterEgg::hatch sets
    the egg's activity, so the combat activity sticks. Outside, it keeps
    the combat flag but CombatProcess::run returns while it is not
    FLG_FASTAREA, and when the Avatar comes near, enterFastArea clears it:
    it stands there passive (playtest-2026-10-11-monsters2 finding 1).
    A monster that does not see the Avatar at once loiters round its egg,
    and one that walks out of the fast area is destroyed (FLG_FAST_ONLY,
    Item::leaveFastArea), so then its whole loiter square must be fast."""
    fast = set.intersection(*[fast_chunks(*c, dims=dims) for c in
                              hatch_cameras(trigger, xrange, yrange, zs)])
    own = (egg[0] // MAP_CHUNK, egg[1] // MAP_CHUNK)
    if own not in fast:
        return f'its chunk {own} is outside the fast area'
    if wakes_at_once(trigger, xrange, yrange, egg, shape_footpad):
        return ''
    out = sorted(loiter_chunks(egg[0], egg[1]) - fast)
    return (f'it does not see the Avatar at once, and its loiter square '
            f'reaches chunks {out} outside the fast area') if out else ''


def monster_group(group, trigger, box, eggs, activity=ACTIVITY_COMBAT):
    """Items for one hatch group, its eggs one-shot (frame 1: destroyed as
    they hatch, so once per visit; see the module note).

    group    1..31, unique among the groups whose eggs a trigger can reach
    trigger  (x, y, z) of the MONEGG egg
    box      (xrange, yrange) in 32-unit steps, 1..15 each
    eggs     [(x, y, z, monster_shape)], every one within MONEGG_RANGE of
             the trigger on both axes
    """
    tx, ty, tz = trigger
    out = [MapItem.monster_trigger(x=tx, y=ty, z=tz, group=group,
                                   xrange=box[0], yrange=box[1])]
    for (x, y, z, shape) in eggs:
        if abs(x - tx) > MONEGG_RANGE or abs(y - ty) > MONEGG_RANGE:
            raise ValueError(f"group {group}: egg ({x},{y}) is outside the "
                             f"trigger's {MONEGG_RANGE}-unit search from "
                             f"({tx},{ty})")
        out.append(MapItem.monster_egg(x=x, y=y, z=z, monster_shape=shape,
                                       count=1, activity=activity,
                                       group=group, one_shot=True))
    return out

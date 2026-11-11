#!/usr/bin/env python3
"""
build_map_13.py — Map 13: Cloud Cliffs

REBUILT 2026-10-17 AROUND THE 1994 SHOTS (screenshot reconstruction phase B,
docs/research/2026-10-16-screenshot-reconstruction/phaseB/map13/REPORT.md).
Five published 1994 shots are of this map, and the build places each one
verbatim at its vignette origin (vignettes/screenNN.json):

  screen01  the summit edge over the sea of cloud      origin (2176,0,56)
  screen14  the skull ring under the north face         origin (-1024,256,0)
  screen15  the stepping stones across the lake         origin (-1024,2688,-8)
  screen16  the causeway's landing under the big face   origin (-1152,1536,-8)
  screen13  the city edge: earth level with the summit  origin (3456,-384,120)
            under floating cloud and the gold street's corner

Everything else is extrapolated around them in their own material and
idiom (lv_map13_tiers): 301 rock floors on the 127-mod-128 lattice, raised
in tiers whose rims are 125 crests by role over 26/32 faces stacked 48
apart, black frames only on the faces the camera never sees, the lake's
navy water, and the cloud sea at z 57 that the summit drops into.

Layout, south to north (the camera looks from the south-east, so every
tier's south and east faces are the ones drawn):

  y 10240-12288  the valley (z 0): arrival pad 207, return trigger 206,
                 EggCloudCliffs, the ruined wall at the climb's foot.
  y 7936-10240   the lower climb, x 4095, rising 0 -> 64 against the
                 terraced massif on its west; the valley's floor east.
  y 5631-7679    the lake (screen15, screen16's west) north of the climb's
                 east leg, its causeway of stepping stones running north to
                 screen16's pillar under the big face.
  y 3840-5375    the skull ring path (screen14) at z 80, joined to the
                 climb's north leg at its east end.
  y 1279-7935    the north leg, x 5119, rising 68 -> 120 with the massif
                 standing on its west and the cloud sea (north of y 5247)
                 or a shelf at z 56 (south of it) below it on the east; it
                 runs one row on past its turn west to a dead end
                 (CLIMB_STUB).
  y 0-1663       the summit (screen01) at z 120: pads 208/209, the crag,
                 and cloud on every side the shot shows it.
  x 5247-6783    screen13's earth at z 120, east of the turn, open to it
  y 1151-2687    across the turn's east lane: an island over the cloud
                 sea, which the field carries east to x 8191 (CX_EAST).
                 Its cloud patches and gold corner float at 216 (FLOATING),
                 and the island's ground under them stays walkable.

The walkable route is the climb (CLIMB_WAYPOINTS): every 1994 view is a
side scene off it or its goal, and none of the four depends on the 1994
jump-climb (56-unit ledges), which the engine does unreliably.
"""

import json
import os
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(__file__))

from u8_map import MapItem, generate_terrain_grid, wall_run_x
from lv_monster_eggs import monster_group
from lv_furnish import void_floor, WALL_EW, WALL_PLAIN
from lv_landscape import rim
import lv_map13_tiers as T
import vignette_place as VP
from lv_shapes import (
    SHAPE_ROCK_SPIRE_CLUSTER,
    SHAPE_BOULDER_PILE,
    SHAPE_SLAB_PALE,
    SHAPE_BOULDER_LARGE,
    SHAPE_MON_HARPIE,
    SHAPE_PLACEHOLDER_INVISIBLE_EGG,
    SHAPE_CLOUD_1994,
    SHAPE_GOLD_BRICK_1994,
    SHAPE_CLOUD_RIM_1994,
    SHAPE_GOLD_EDGE_1994,
    SHAPE_TREE_STUMP_GREY,
    SHAPE_BONES_A,
    SHAPE_SKELETON_SPRAWLED,
)

HERE = os.path.dirname(os.path.abspath(__file__))

# Retail's cave floor, 16 tiles of 301 f0-6 (the 1994 shots' grey rock).
# The valley's chunks are this glob; every other floor is a loose tile so
# its frame and height can change cell by cell.
GLOB_ROCK = 397

# ===========================================================================
# THE 1994 SHOTS
# ===========================================================================
VIGNETTES = ('screen01', 'screen14', 'screen15', 'screen16', 'screen13')
# The 1994 floors (art_registry 2000 cloud, 2004 gold brick) are built as
# shapes 874 and 876 with the shots' own frames. Their hotspots sit one
# pixel lower than the 1994 frames' (phaseC-art.md, the z rule: z - 1), so
# each is laid one unit below the shot's own z and draws exactly there:
# screen01's cloud plane at z 56. Since 2026-10-25 (phase D) screen13's
# floor tiles are its own cut tiles, 2015 -> 886 (each with the lobed rim
# the shot shows), and the gold corner is 2008 f2 -> 884 f2, the edge tile
# screen12 shows too.
ART_STANDIN = {2000: SHAPE_CLOUD_1994, 2004: SHAPE_GOLD_BRICK_1994,
               2015: SHAPE_CLOUD_RIM_1994, 2008: SHAPE_GOLD_EDGE_1994}
STANDIN_DZ = {SHAPE_CLOUD_1994: T.CLOUD_DZ, SHAPE_GOLD_BRICK_1994: T.CLOUD_DZ,
              SHAPE_CLOUD_RIM_1994: T.CLOUD_DZ, SHAPE_GOLD_EDGE_1994: T.CLOUD_DZ}
# A shot whose ground is not the cliffs' rock: its HALO and hidden cells are
# floored in its own material (lv_map13_tiers.Cell.floor), so the ground
# runs on past its frame. screen13 is retail earth, 4 f30-33.
SHOT_FLOORS = {'screen13': (4, (30, 31, 32, 33))}
# A shot's floors that float over its ground (vignette_layer `floating`):
# laid, but no cell's ground. screen13's cloud patches and gold corner
# (Douglas, 2026-10-30): in 1994 they draw over the tree's crown (74 f0,
# local 40-80), the mushroom behind it and the spires' feet, while the
# Avatar's legs draw over the lower patch. So he stands on the cloud, and
# the props stand on earth below it. The vignette lays the cloud and gold
# (and the Avatar) at local 97, 12 view-ray steps (+384, +384, +96) up from
# where they lay on the earth: every pixel is the same, 16 clear of the
# crown. The earth island stays the summit's walkable ground at 120; the
# floating layer, at 216, is out of reach.
FLOATING = {'screen13': frozenset({2015, 2004, 2008})}
# Shot items moved along the view ray (lv_map13_tiers.vignette_layer
# `slides`): k steps of (8, 8, 2) draw exactly the same pixels, so the
# shots are unchanged, and only the boxes they meet move. A
# reconstruction fixes x, y, z only up to that ray, and these three were
# solved inside their neighbours, which closed the two paint cycles the
# engine logged 254,668 times in one session (verifier 2026-10-17 finding
# 7, test_paint_cycles section 6):
#   * screen01: the spire 66:9 stood 8 deep in the plateau's crest and
#     floor, the spire 66:7 beside it on the ledge west of that crest:
#     125 -> 66 -> 66 -> 125. 66:9 now stands on the crest (k 4), 66:7
#     16 over its ledge (k 8), clear of the crest's box;
#   * screen14's 26 -> 564 -> 566 -> 26 ran through the black plate 564:6
#     and the black face 26:8, which draw nothing in the window (they are
#     dropped below, SHOT_CUTS).
RAY_SLIDES = {
    ('screen01', 66, 9, 2143, 2495, 56): 4,
    ('screen01', 66, 7, 2047, 2623, 48): 8,
}
# Shot items laid as the smaller pieces of them that draw in the window
# (vignette_layer `cuts`). screen14's black plate 564:3 at z 137 is 256
# across, and three quarters of it lie outside the window, where it drew a
# black diamond over the ground round the skull ring's path (verifier
# 2026-10-17 finding 3). It is laid as the two quarters that reach the
# window, each the black cell tile 35:10 (lv_cave_vignette's), at the
# offsets that draw the plate's own pixels there (screen14's score is
# unchanged); the cells the other two quarters covered become the shot's
# HIDDEN cells, floored round it.
SHOT_CUTS = {
    ('screen14', 564, 3, 5399, 4079, 137): ((35, 10), [(-8, -12, 0),
                                                       (-136, -12, 0)]),
    # The black plate and face behind the skull ring's north face draw no
    # pixel of the window (every one is under the shot's own pieces) and
    # drew black slabs above it: no pieces.
    ('screen14', 564, 6, 5231, 3943, 104): ((564, 6), []),
    ('screen14', 26, 8, 5184, 3916, 96): ((26, 8), []),
}

# Pieces of a 1994 frame the reconstruction left out whose box lies outside
# the shot's region, laid as completions (window_fills; a gap inside the
# region goes into the vignette's own items, as screen01's corner post 29:7
# did). Each is checked palette-exact against the shot and placed on its view
# ray where its box meets no solid (window_fills refuses one that meets).
#   * screen01's left edge, window (0..6, 115..122): a crest top, 125:0, 32
#     of 32 px exact, where Map 13's generated north face 26:7 at
#     (3711,2335,56) drew black through the hole (verify3 4b's wedge). On
#     the ray at (3711,2431,72) it would stand inside that face; four steps
#     up, at (3743,2463,80), it meets nothing. It changes no other window
#     pixel; west of the window it covers 281 more px of the same black
#     face with rock.
WINDOW_FILLS = [
    (125, 0, 3743, 2463, 80),
]

# ===========================================================================
# THE CLIMB
# ===========================================================================
# ONE polyline, walked in 128-unit tile steps (2026-07-31), its z quantized
# to the engine's step (2026-08-18): when a walk step lands unsupported,
# AnimationTracker::step falls back to CurrentMap::scanForValidPosition,
# whose U8 table is {0, -4, 4, -8, 8} — the ONLY z changes a walking actor
# can make. A 1- or 2-unit riser is as impassable as a 9-unit one (F10,
# playtest 2026-08-17), so every riser is a multiple of CLIMB_Z_STEP and
# test_route_reach / test_climb_risers hold it there.
#
# Since 2026-10-17 the tiles sit on the floor lattice (x, y = 127 mod 128)
# with the 1994 views, and the line goes round them: the old x 4096 line
# ran through the four shots' cells. It climbs the lower massif on x 4095,
# turns east along the lake's south shore, goes north on x 5119 past the
# skull ring's path, on north out over the cloud sea, and turns west to end
# on (34,12), north of the summit plateau's north-east corner (34,13),
# which its south lane steps onto. The summit cannot be entered from the
# south: screen01 shows the ground south and east of its plateau lower
# (crest lips on (33,19) and (34,18)), and a tile at 120 on (34,19) or
# (33,20) drew over the shot's bone pillar below the rim (344 of the
# window's pixels). Cells at 120 with y <= 1663 and x > 4351 project
# outside the window.
TILE = 128
CLIMB_Z_STEP = 4
CLIMB_Z_TOP = 120          # the summit (screen01's mid plateau)

# (x, y, z): the polyline's corners, and z there; z is interpolated in
# CLIMB_Z_STEP risers between them. (5119, 4735) and (5119, 2687) are no
# corners: they pin the path at 80 where screen14's path joins it and at
# 120 from there on.
CLIMB_POINTS = [
    (4095, 10239, 0),     # the foot, on the valley floor
    (4095, 7935, 64),     # up the lower massif to the lake's south shore
    (5119, 7935, 68),     # east along it
    (5119, 4735, 80),     # north: the skull ring's path joins here
    (5119, 2687, 120),    # on north to the summit's height
    (5119, 1663, 120),    # out over the cloud sea
    (4479, 1663, 120),    # west onto the summit's north-east corner
]
CLIMB_WAYPOINTS = [(x, y) for (x, y, _) in CLIMB_POINTS]

# Where the path is more than one tile wide, as (y_lo, y_hi, extra lanes
# each side): all of it but the foot tile. One tile is 128 units for a
# 64-unit body, and a walking Avatar dropped off it six times in one climb
# (docs/playtest-2026-10-11-full-run-part6.md finding 2): every slide the
# mover makes off a refused step moves him sideways. test_climb_width.py
# holds every input along every leg and counts falls.
CLIMB_WIDE = (
    (1663, 10111, 1),
)

# Lane cells the climb does without, because they draw into a 1994 window
# (lv_map13_views.py --fit reports the climb's own cells): (31, 60), the
# lower bend square's north lane, over screen15's lake bank (246 pixels).
# Never a path tile.
CLIMB_CUTS = frozenset({(31, 60)})

# The cells where screen14's path meets the north leg's west lane, both at
# z 80: the climb's one side opening. They are climb cells (no curb across
# them, and the holds may cross them).
CLIMB_SPURS = {(37, 35): 80, (37, 36): 80}

# The north leg's dead end: its three lanes run one row on north past the
# turn west, at the summit's z, and stop over the cloud (curbed round).
# Verifier 2026-10-17 finding 6: from pad 208 a keyboard hold NE slid N up
# the east lane, and where the leg ended at the turn's north row the
# refused step's slides (NE, then NW) turned him W along the summit leg,
# SW onto the plateau and S into trigger 209 at 3.5 s run / 5.5-6.1 s
# walk: back to Map 17. Past the turn a hold up the leg still has north to
# go, so it runs on into this row and stops at its end; every hold from
# the pad, 8 headings x every mode, moving and standing, now stops or goes
# back down the climb (test_route_reach's arrival corridors, 8 s; in the
# mover none reaches a trigger in 16 s). These cells draw into no window
# (z 120 north of y 1663 and east of x 4351 projects outside screen01's).
CLIMB_STUB = {(38, 10): CLIMB_Z_TOP, (39, 10): CLIMB_Z_TOP,
              (40, 10): CLIMB_Z_TOP}


def climb_tiles():
    """Every path tile from base to summit, as (x, y, z), in order."""
    pts, zs = [], []
    for (ax, ay, az), (bx, by, bz) in zip(CLIMB_POINTS, CLIMB_POINTS[1:]):
        dx = (bx > ax) - (bx < ax)
        dy = (by > ay) - (by < ay)
        if (dx == 0) == (dy == 0):
            raise ValueError(f"climb leg ({ax},{ay})->({bx},{by}) is not "
                             f"axis-aligned")
        if (az - bz) % CLIMB_Z_STEP or bz < az:
            raise ValueError(f'climb z {az} -> {bz} is not a rise in '
                             f'{CLIMB_Z_STEP}s')
        n = (abs(bx - ax) + abs(by - ay)) // TILE
        steps = (bz - az) // CLIMB_Z_STEP
        for k in range(n):
            pts.append((ax + dx * k * TILE, ay + dy * k * TILE))
            # Quantized: interpolate in STEPS, not in world units.
            zs.append(az + CLIMB_Z_STEP * ((steps * k + n // 2) // n))
    x, y, z = CLIMB_POINTS[-1]
    pts.append((x, y))
    zs.append(z)
    return [(x, y, z) for (x, y), z in zip(pts, zs)]


def climb_z(y):
    """The path's z where it crosses this y on a north-south leg."""
    for (x, ty, z) in climb_tiles():
        if ty == y:
            return z
    return None


def lanes_at(y):
    return max((lanes for (lo, hi, lanes) in CLIMB_WIDE if lo <= y <= hi),
               default=0)


def climb_cells():
    """Every walkable cell of the climb as {(x, y): z}, (x, y) the tile's
    max corner: the path tiles, then `lanes_at(y)` lanes each side of each
    tile across its leg (a corner tile both ways and its diagonals, so a
    bend is a full square) but CLIMB_CUTS, then CLIMB_SPURS and CLIMB_STUB.
    The first z laid on a cell wins, path tiles first.

    On a north-south leg the lanes' risers are staggered (2026-10-17): the
    east lane takes the z of the path tile a row south, the west lane the
    one a row north, so across a row z never rises eastward. Level lanes
    closed a paint cycle at every riser (verifier 2026-10-17 pass 2, 3d:
    `1 -> 125 -> ... -> 1`, a mouse run down the north leg). Stepping down
    a riser the Avatar's drawn position is lerped between two ticks and
    floored (Item::doLerp, `>> 8`), so for the last quarter of the step he
    is drawn at the lower z while his box still reaches into the higher
    row. The sorter then puts him below the east lane's higher crest (x
    first: his box ends where it begins), above that lane's lower crest in
    front (z), and the higher crest is below the lower one (y): a knot.
    With the east lane already down on the higher row, nothing east of him
    there stands above him (test_paint_cycles section 7)."""
    tiles = climb_tiles()
    cells = {(x, y): z for (x, y, z) in tiles}
    cut = {(T.corner(cx), T.corner(cy)) for (cx, cy) in CLIMB_CUTS}
    if cut & set(cells):
        raise ValueError('CLIMB_CUTS takes a path tile')
    for k, (x, y, z) in enumerate(tiles):
        lanes = lanes_at(y)
        if not lanes:
            continue
        legs = [(tx - x, ty - y) for (tx, ty, _) in
                tiles[max(k - 1, 0):k] + tiles[k + 1:k + 2]]
        across_x = any(dy for (_, dy) in legs)        # a north-south leg
        across_y = any(dx for (dx, _) in legs)        # an east-west leg
        stagger = across_x and not across_y           # not a bend square
        if stagger and not (0 < k < len(tiles) - 1 and
                            tiles[k - 1][1] > y > tiles[k + 1][1]):
            raise ValueError(f'climb tile ({x},{y}): the lane stagger needs '
                             f'its north-south leg to climb north')
        rx = range(-lanes, lanes + 1) if across_x else (0,)
        ry = range(-lanes, lanes + 1) if across_y else (0,)
        for i in rx:
            for j in ry:
                c = (x + i * TILE, y + j * TILE)
                if c not in cut:
                    cells.setdefault(c, tiles[k - i][2] if stagger else z)
    for (cx, cy), z in {**CLIMB_SPURS, **CLIMB_STUB}.items():
        cells.setdefault((T.corner(cx), T.corner(cy)), z)
    return cells


def summit_cells(field=None, vcells=None):
    """{cell: z}: the summit plateau, screen01's ground walked to from the
    climb's last tile and its lanes on the shot's cells (test_climb_width:
    the raised climb ends here)."""
    if field is None:
        field, _, (_, _, vcells) = build_field()
    x, y, z = climb_tiles()[-1]
    ex, ey = T.cell_of(x), T.cell_of(y)
    seeds = {(ex, ey): z}
    seeds.update({c: cz for c, cz in _climb_index().items()
                  if c in vcells and abs(c[0] - ex) <= 1
                  and abs(c[1] - ey) <= 1})
    return {**seeds, **walk_cells(field, vcells, seeds)}


def shot_region(shot):
    """The cells of a shot's ground: its items' cells, the FLOATING ones'
    not (vignette_layer's region for that shot)."""
    vig = VP.load(shot)
    afloat = FLOATING.get(shot, frozenset())
    return VP.region(dict(vig, items=[it for it in vig['items']
                                      if it['shape'] not in afloat]),
                     ART_STANDIN)


def city_edge_cells(field=None, vcells=None):
    """{cell: z}: screen13's island (the city edge), its ground walked to
    from the climb cells beside the shot's region (the turn's east lane).
    The cells under its floating cloud are walked too: the cloud draws over
    an Avatar there (UNDER THE FLOATING CLOUD below)."""
    if field is None:
        field, _, (_, _, vcells) = build_field()
    region = shot_region('screen13')
    seeds = {c: z for c, z in _climb_index().items()
             if any((c[0] + dx, c[1] + dy) in region
                    for dx, dy in T.SIDES.values())}
    return walk_cells(field, vcells, seeds)


def foot_apron():
    """The foot's apron: the foot tile's row, across the lanes of the first
    raised row above it, as cells (the foot tile's own excluded). It is
    valley floor, so the ruined wall's gap opens onto the climb with no
    massif corner in it, and it is no side to curb (build_curbs): a
    keyboard run N off pad 207 slid off that corner, or off a curb along
    the raised row's south side, and ran east along it for good
    (test_climb_width FOOT)."""
    tiles = climb_tiles()
    lanes = lanes_at(tiles[1][1])
    fx, fy = T.cell_of(tiles[0][0]), T.cell_of(tiles[0][1])
    return {(fx + i, fy) for i in range(-lanes, lanes + 1) if i}


# ===========================================================================
# THE HARPIES
# ===========================================================================
# Four one-shot waves of ONE harpie each (Douglas, 2026-10-11: one-shot
# pairs; 2026-10-24: the climb's harpies one at a time; 2026-10-30: the
# summit's too) on the climb's north leg and the summit, with a rest
# between the lanes and the summit (test_monster_eggs.py). Each egg stands
# on the path or the plateau at its own z with 32 units of it on every
# side. The lane pair hatched together killed an ARMED new-game Avatar in
# 5 of 10 fights (docs/playtest-2026-10-18-armed-harpie-pair.md): the two
# reached him within seconds of each other, and four blows kill him. So
# the climb meets them one by one, each wave's trigger wholly past the
# last wave's monster.
#   Group 3, the first lane harpie: a trigger across the three lanes at
#   y 6143, on the long level stretch at z 76, hatches one 512 ahead
#   (HARPIE_FIRST), on that same level ground. The fight is on the flat,
#   and the next trigger's box begins 1,024 north of that harpie's egg.
#   Group 1, the second: a trigger across the three lanes at y 4479,
#   where screen14's path joins, hatches one on the lanes 512 ahead of him
#   (HARPIE_LANE), in the seek square of every position that fires it
#   (lv_monster_eggs.wakes_at_once). The lanes' risers are staggered
#   (2026-10-17, climb_cells), so it stands at (5183, 3967), the nearest
#   spot still level 32 round the body at 96 (the pair's west egg stood at
#   (5023, 3999)).
#   Group 4, the third: a trigger across the three lanes at y 2687, where
#   the leg reaches the summit's z, hatches one 512 ahead (HARPIE_TOP) on
#   the leg's level top, north-east of pad 208. The trigger's box lies
#   south of the pad (an arrival from Map 17 stands outside it).
#   Group 2, the fourth: a trigger across the summit leg over the cloud
#   (y 1663, three lanes), its box wholly north of HARPIE_TOP's body,
#   hatches one on the plateau (HARPIE_SUMMIT), 576 west of him.
# HARPIE_REST, on the north leg between the lane and the summit, lies
# outside every egg's seek square (768 round the egg,
# lv_monster_eggs.seek_square) and every trigger's box: a player who has
# beaten the lane harpies can stand there and heal. The seek squares of
# the lane harpie and the summit's two leave his reference point y
# 3008-3070 between them on the leg (both summit squares end at 2943, his
# box 64 deep; the lane harpie's begins past 3070), and group 4's box ends
# at 2814.
# A dead harpie stays where it fell, solid at 128 x 128 x 32, as a retail
# torax does (Actor::dieU8 leaves the actor in place). One body never
# closes the three lanes (test_harpie_corpses.py). One summit harpie's body
# in the neck between screen01's boulder 66:8 (x 4127-4255) and the
# plateau's east edge (x 4479), or in the column below it, can close the
# walk to teleporter 209 until it leaves the fast area: walking back down
# the climb (about two chunks) clears it. Accepted by Douglas 2026-10-30:
# any ground that widens the neck draws over screen01's window.
HARPIE_FIRST = (5183, 5631)
HARPIE_FIRST_Z = 76
HARPIE_LANE = (5183, 3967)
HARPIE_LANE_Z = 96
HARPIE_TOP = (5183, 2175)
HARPIE_SUMMIT = (4287, 2175)
HARPIE_TRIGGER_FIRST = (5119, 6143)
HARPIE_TRIGGER_LANE = (5119, 4479)
HARPIE_TRIGGER_TOP = (5119, 2687)
HARPIE_TRIGGER_SUMMIT = (4863, 1663)
HARPIE_REST = (5087, 3039, None)        # z filled in below


def _harpie_rest():
    x, y, _ = HARPIE_REST
    return (x, y, climb_z(T.corner(y // TILE)))


HARPIE_REST = _harpie_rest()


def build_harpies():
    tx, ty = HARPIE_TRIGGER_FIRST
    items = monster_group(
        3, trigger=(tx, ty, climb_z(ty)), box=(6, 2),
        eggs=[(*HARPIE_FIRST, HARPIE_FIRST_Z, SHAPE_MON_HARPIE)])
    tx, ty = HARPIE_TRIGGER_LANE
    items += monster_group(
        1, trigger=(tx, ty, climb_z(ty)), box=(6, 2),
        eggs=[(*HARPIE_LANE, HARPIE_LANE_Z, SHAPE_MON_HARPIE)])
    tx, ty = HARPIE_TRIGGER_TOP
    items += monster_group(
        4, trigger=(tx, ty, climb_z(ty)), box=(6, 2),
        eggs=[(*HARPIE_TOP, CLIMB_Z_TOP, SHAPE_MON_HARPIE)])
    tx, ty = HARPIE_TRIGGER_SUMMIT
    items += monster_group(
        2, trigger=(tx, ty, CLIMB_Z_TOP), box=(1, 6),
        eggs=[(*HARPIE_SUMMIT, CLIMB_Z_TOP, SHAPE_MON_HARPIE)])
    return items


# ===========================================================================
# THE TERRAIN FIELD
# ===========================================================================
# One cell per 128 units over the map's rectangle, x (1535, 6655], y (-1,
# 12287]. The design below gives each cell a kind and a level; the
# vignettes' cells are locked to the shots; a halo two cells deep carries
# each shot's ground out past its frame so the shot's tiers continue
# instead of ending in the air (the phase A "island"); the climb's cells
# are laid over it; and FIT (map13_window_fit.json) lowers the cells whose
# items would have drawn into a shot's window — in this projection a point
# hidden in one window is hidden in every window, so what each shot's
# frame shows is what any camera shows there, and only the world beyond
# the frames is ours to extrapolate.
CX0, CX1 = 12, 51          # x (1535, 6655]
CY0, CY1 = 0, 95           # y (-1, 12287]
# Past CX1 only the cloud sea goes on, to CX_EAST, north of CY_EAST:
# screen13's island and its halo reach x 7039, and a 640 x 400 view from
# its gold street's corner reaches x 8100 and y 3200 (the field's edge drew
# black there). Further south the field keeps its edge: a cloud tile east
# of the valley's east edge drew over an Avatar standing against it
# (test_route_reach map13_rim_drawn), and the valley's rim, built on CX1's
# chunks, is unchanged.
CX_EAST = 63               # x (6655, 8191], cloud only
CY_EAST = 31               # y <= 4095
HALO = 2
FIT_FILE = os.path.join(HERE, 'map13_window_fit.json')


def _walk(n, salt, lo=-2, hi=2, p=55):
    """A deterministic random walk of cell offsets: the 128-unit jog a tier
    boundary takes as it runs (retail's cliff runs: median 128-192 units,
    60-75% of them two tiles or shorter)."""
    off, v = [], 0
    for i in range(n):
        r = T.hsh(i, salt, 5) % 100
        if r < p // 2:
            v -= 1
        elif r < p:
            v += 1
        v = max(lo, min(hi, v))
        off.append(v)
    return off


_JOG = {k: _walk(100, k) for k in range(40)}


def _yb(cy0, k, cx):
    """An east-west tier boundary near row cy0, jogging along x."""
    return cy0 + _JOG[k][cx]


def _xb(cx0, k, cy):
    """A north-south tier boundary near column cx0, jogging along y."""
    return cx0 + _JOG[20 + k][cy]


VALLEY = 'valley'          # z 0 rock under the valley's glob floor


def design(cx, cy):
    """The macro layout: (kind, level) of a cell before the shots are laid
    in. Levels are retail tiers (a 48 course plus an 8 crest: 56, 112,
    168, 224) except where a shot fixes another (104 and 80 under screen16
    and the lake's banks, 40 east of the lake)."""
    if cy >= 80:
        return VALLEY, 0                               # the valley
    if cx <= _xb(18, 3, cy):                           # the west ridge
        if cy <= _yb(30, 4, cx):
            return T.ROCK, 224
        if cy <= _yb(52, 5, cx):
            return T.ROCK, 168
        if cy <= _yb(70, 6, cx):
            return T.ROCK, 112
        return T.ROCK, 56
    if cy <= _yb(13, 0, cx):                           # the cloud sea, north
        return T.CLOUD, T.CLOUD_Z
    if cx >= 41:                                       # east of the climb
        if cy <= _yb(40, 1, cx):
            return T.CLOUD, T.CLOUD_Z
        if cy <= _yb(62, 2, cx):
            return T.ROCK, 56
        return VALLEY, 0
    if cy <= _yb(20, 7, cx):                           # the summit's west
        if cx >= 35:
            return T.CLOUD, T.CLOUD_Z
        return T.ROCK, 56 if cx >= _xb(22, 8, cy) else 112
    if cy <= _yb(24, 9, cx):                           # below the summit
        if cx >= _xb(31, 10, cy):
            return T.CLOUD, T.CLOUD_Z
        return T.ROCK, 112
    if cy <= _yb(29, 11, cx):                          # the high massif
        return T.ROCK, 168 if cx <= _xb(34, 12, cy) else 112
    if cy <= _yb(41, 13, cx):                          # screen14's tier
        return T.ROCK, 112
    if cy <= _yb(48, 14, cx):                          # screen16's tier
        return T.ROCK, 104
    if cy <= _yb(59, 15, cx):                          # the lake's banks
        return (T.ROCK, 40) if cx >= _xb(35, 16, cy) else (T.ROCK, 80)
    if cx <= _xb(29, 17, cy):                          # the lower massif
        return T.ROCK, 112 if cy <= _yb(71, 18, cx) else 56
    return VALLEY, 0


def _load_fit():
    if not os.path.exists(FIT_FILE):
        return {}
    with open(FIT_FILE) as fh:
        data = json.load(fh)
    return {tuple(int(v) for v in k.split(',')): (kind, z)
            for k, (kind, z) in data['cells'].items()}


# A fit entry (UNFACED, keys) names the completion pieces (shot_faces) of a
# shot's (LOCK) cell that the fit found drawing into a window, each by its
# lv_map13_tiers.piece_key (side and z; CLOUD_KEY for the cloud filler): a
# shot cell cannot be lowered, so those pieces go without.
UNFACED = 'unfaced'


# Completion pieces refused by hand, where the fit cannot see the loss: it
# protects only the pixels a shot's vignette matches alone, and these draw
# over pixels the generated map matches. Cell (31,14), screen01's blood
# cliff: its north face's top course N120, black, laid where the 1994 corner
# post 29:7 stands and slid four steps down the view ray, drew 37 px of
# black over the cloud sea beside the post in the window (verify3 4b).
UNFACED_BY_HAND = {
    (31, 14): frozenset({'N120'}),
}

# Generated strips below screen01's crop. Their black ends
# remain visible from m13-29 through m13-34 and m13-42. A post in each strip
# closes the end without changing its collision union or any window pixel.
SUMMIT_FACE_ENDS = frozenset({
    (26, 4351, 1695, 16), (26, 4351, 1695, 64),
    (31, 3615, 2303, 24),
})


def summit_face_caps(faces, keys=None):
    """Close three exposed strip ends with coincident 29 posts."""
    out = []
    for it in faces:
        old = (it.shape, it.x, it.y, it.z)
        if old not in SUMMIT_FACE_ENDS:
            out.append(it)
            continue
        post = MapItem.placed_item(it.x, it.y, it.z, T.SHAPE_POST, 0)
        if it.shape == 26:
            it.shape, it.x = 27, it.x - 32
        else:
            it.shape, it.y = 30, it.y - 32
        it.frame = 0
        out.extend((it, post))
        if keys is not None and old in keys:
            name = keys.pop(old)
            for piece in (it, post):
                keys[piece.shape, piece.x, piece.y, piece.z] = name
    return out


def unfaced(fit=None):
    out = {c: frozenset(keys) for c, (kind, keys)
           in (_load_fit() if fit is None else fit).items()
           if kind == UNFACED}
    for c, keys in UNFACED_BY_HAND.items():
        out[c] = out.get(c, frozenset()) | keys
    return out


def build_field(fit=None):
    """(field, valley cells, vignette layer) — see THE TERRAIN FIELD.
    `fit`: {cell: (kind, level)} instead of map13_window_fit.json (the fit
    tool, lv_map13_views.py, passes its trial)."""
    vitems, region, vcells = T.vignette_layer(VIGNETTES, 13, ART_STANDIN,
                                              STANDIN_DZ, RAY_SLIDES,
                                              SHOT_CUTS, FLOATING)
    field, valley = {}, set()
    for cx in range(CX0, CX_EAST + 1):
        for cy in range(CY0, CY1 + 1):
            kind, z = design(cx, cy)
            if cx > CX1 and (kind != T.CLOUD or cy > CY_EAST):
                continue
            if kind == VALLEY:
                valley.add((cx, cy))
                kind = T.ROCK
            field[(cx, cy)] = T.Cell(kind, z)
    # The cells of each shot whose ground has its own material.
    own = {c: floor for shot, floor in SHOT_FLOORS.items()
           for c in shot_region(shot)}
    # The shots' cells, locked to what the shots show. A cell the shot
    # shows no ground in (behind a face, under a prop, the black of a
    # drop) is HIDDEN: it is floored below like a halo cell, floor only, so
    # nothing it gets can meet a piece of the shot's own, and FIT may lower
    # it like any other generated cell.
    locked = {c for c in region if vcells[c]['top'] is not None}
    hidden = region - locked
    for c in locked:
        field[c] = T.Cell(T.LOCK, vcells[c]['top'])
        valley.discard(c)
    # The halo: each shot's ground carried HALO cells out past its frame.
    # A cell beside a shot takes, from the shot's cells next to it: water
    # or cloud if that is what they show; else the foot of the face they
    # drop by on its side (the lowest course's base) if they have one;
    # else, if their crest's lip says they drop that way, the design's
    # lower level there (a tier lower if the design has none); else their
    # ground. Water beats cloud beats a drop (the lowest) beats ground
    # (the highest).
    ring, ring_floor = {}, {}
    for c in sorted(locked):
        v = vcells[c]
        for side, (dx, dy) in T.SIDES.items():
            n = (c[0] + dx, c[1] + dy)
            if n not in field or n in locked:
                continue
            if v['water']:
                cand = (3, T.WATER, v['top'])
            elif v['cloud']:
                cand = (2, T.CLOUD, T.CLOUD_Z)
            elif side in v['edge']:
                cand = (1, T.ROCK, -v['edge'][side])
            elif side in v['lips']:
                kind, z = design(*n)
                if kind == T.CLOUD:
                    cand = (2, T.CLOUD, T.CLOUD_Z)
                else:
                    cand = (1, T.ROCK, -(z if z < v['top'] else
                                         max(v['top'] - 56, 0)))
            else:
                cand = (0, T.ROCK, v['top'])
            if n not in ring or cand > ring[n]:
                ring[n], ring_floor[n] = cand, own.get(c)
    halo = {n: (kind, abs(z)) for n, (_, kind, z) in ring.items()}
    floors = dict(ring_floor)
    queue = deque(sorted(n for n in halo if n not in hidden))
    dist = {n: 1 for n in halo}
    while queue:
        c = queue.popleft()
        if dist[c] >= HALO:
            continue
        for dx, dy in T.SIDES.values():
            n = (c[0] + dx, c[1] + dy)
            if n not in field or n in dist or n in region:
                continue
            dist[n] = dist[c] + 1
            halo[n] = halo[c]
            floors[n] = floors[c]
            queue.append(n)
    for n, (kind, z) in sorted(halo.items()):
        if n in hidden and kind == T.ROCK:
            kind = T.HIDDEN
        field[n] = T.Cell(kind, z, floor=floors[n])
        valley.discard(n)
    for c in hidden - set(halo):
        field[c] = T.Cell(T.VOID, 0)
        valley.discard(c)
    # The climb, over everything but the shots.
    for (x, y), z in climb_cells().items():
        c = (T.cell_of(x), T.cell_of(y))
        if c in region:
            continue
        field[c] = T.Cell(T.ROCK, z)
        valley.discard(c)
    for c in foot_apron():
        if c not in region:
            field[c] = T.Cell(T.ROCK, 0)
            valley.add(c)
    for c, (kind, z) in (_load_fit() if fit is None else fit).items():
        if c in locked or c not in field:
            continue
        if c in hidden and kind == T.ROCK:
            kind = T.HIDDEN
        field[c] = T.Cell(kind, z, floor=field[c].floor)
        valley.discard(c)
    return field, valley, (vitems, locked, vcells)


def field_level(field):
    def level(c, side):
        cell = field.get(c)
        return 0 if cell is None else cell.level(side)
    return level


# ===========================================================================
# THE VALLEY (the base: the arrival from Lost Vale)
# ===========================================================================
VALLEY_X0, VALLEY_Y0 = 1536, 10240


# Earth fans meet the grey approach at two broad, hand-drawn seams.
VALLEY_EARTH_WEST = (23, 24, 25, 25, 24, 23, 24, 25, 26, 26, 25, 24,
                     23, 24, 25, 25, 24)
VALLEY_EARTH_EAST = (42, 41, 40, 39, 39, 40, 41, 42, 42, 41, 40, 39,
                     38, 39, 40, 41, 42)


def build_valley(valley):
    """Two dry earth fans leave a grey approach between them."""
    from lv_vale_terrain import EDGE_FRAMES
    earth = {(x, y) for y in range(80, 97) for x in range(12, 53)
             if x <= VALLEY_EARTH_WEST[y - 80] - 2
             or x >= VALLEY_EARTH_EAST[y - 80] + 2}
    # An earth streak bends through the approach, with blended edges.
    earth.update({(34, 91), (34, 92), (33, 93), (34, 93), (33, 94)})
    tiles = {}
    for cx, cy in sorted(valley):
        pattern = ''.join('1' if c in earth else '0' for c in
                          ((cx, cy), (cx + 1, cy),
                           (cx + 1, cy + 1), (cx, cy + 1)))
        if pattern == '1111':
            shape, frames = 4, (30, 31, 32, 33)
        elif pattern == '0000':
            shape, frames = 301, T.FLOOR_FRAMES
        else:
            shape, frames = 386, EDGE_FRAMES[pattern]
        tiles[cx, cy] = (shape, T.pick(frames, cx, cy, 4013))
    chunks = {}
    for c in valley:
        chunks.setdefault((c[0] // 4, c[1] // 4), []).append(c)
    out = []
    for (kx, ky), cells in sorted(chunks.items()):
        if len(cells) == 16 and all(tiles[c][0] == 301 for c in cells):
            out.append(MapItem.glob_egg(kx * 512 + 511, ky * 512 + 511,
                                        0, GLOB_ROCK))
        else:
            out.extend(MapItem.placed_item(T.corner(cx), T.corner(cy), 0,
                                           *tiles[cx, cy])
                       for cx, cy in sorted(cells))
    return out


def build_base_zone():
    """The valley's pins and props: the base pair, EggCloudCliffs, the
    ruined wall at the climb's foot."""
    items = []
    x0, y0 = VALLEY_X0, VALLEY_Y0
    # ── The base-zone teleport pair. READ THE NAMES CAREFULLY. ──────────
    # `teleporter()` (frame 0) is the ACTIVE TRIGGER — step on it and you
    # LEAVE for Map 10. `teleport_target()` (frame 1) is the passive
    # ARRIVAL pad Map 10's trigger 207 delivers to. The 2026-07-31 swap put
    # the pad on the route at (4096,11776) and the trigger off it, so
    # returning to the Vale is a deliberate act.
    items.append(MapItem.teleport_target(
        x=x0 + 2560, y=y0 + 1536, z=0,
        teleport_id=207
    ))
    # Return TRIGGER (ID 206) → Map 10. Its box (npcNum 0xCE: x +/-384,
    # y +/-448) is x 2944..3775, y 11104..11999 (2026-10-10): the south
    # rim's slide line (y 12244 on) passes 240 south of it, the climb line
    # 320 east, and a walk west off the pad still crosses it
    # (test_route_reach.deliberate_use). Its marker is a pale slab (71,
    # neither SI_DRAW nor SI_OCCL, so it draws over the 301 floor) where a
    # walk west off the pad enters the box.
    items.append(MapItem.placed_item(
        x=x0 + 2239, y=y0 + 1536, z=0,
        shape=SHAPE_SLAB_PALE, frame=0, quality=0
    ))
    items.append(MapItem.teleporter(
        x=x0 + 1792, y=y0 + 1280, z=0,
        teleport_id=206, dest_npc=206, dest_map=10
    ))
    # A RUINED wall at the climb's foot: two stone stubs either side of the
    # climb's three lanes, x (3839,4223] (2026-10-11: a one-tile gap beside
    # the pad's line wedged a run N; test_climb_width.py's FOOT holds). No
    # gate: the key check lives in CLCLIMB's handholds
    # (docs/reviews/2026-09-25-keyless-gates.md).
    for z in (0, 40):
        # The upper course covers three quest-band cells beside the gap.
        # Its coincident invisible wall retains the ruined stub's barrier.
        shape = WALL_EW if z == 0 else 497
        frame = WALL_PLAIN if z == 0 else 0
        items.extend(wall_run_x(x0 + 2047, x0 + 2303, y0 + 512, WALL_EW,
                                frame=WALL_PLAIN, z=z))
        items.extend(wall_run_x(x0 + 2687, x0 + 2943, y0 + 512, shape,
                                frame=frame, z=z))
    # EGGCLOUDCLIFFS trigger (quest step 13, the climb to Cloud City).
    # UnkEgg dispatch: class = quality + 0x47F, so quality 297 -> class
    # 1448 EggCloudCliffs (lv-new/CLCLIMB.UNK, manifest-pinned); npcNum
    # 0x88 = a +/-256 box. On the walking line between the pad and the
    # wall, so the hint fires before the climb. `climbedCliffs` is read by
    # TYORVI, HRODNY, THORDIS, INGYALD and EZREKAL.
    items.append(MapItem(
        x=x0 + 2560, y=y0 + 1024, z=0,
        shape=SHAPE_PLACEHOLDER_INVISIBLE_EGG, frame=0,
        quality=297, npcnum=0x88  # EggCloudCliffs 1448
    ))
    for rx, ry, fr in [(x0+383, y0+767, 1), (x0+4735, y0+1279, 5)]:
        items.append(MapItem.placed_item(x=rx, y=ry, z=0,
                                         shape=SHAPE_BOULDER_PILE, frame=fr))
    return items


def build_valley_rim(valley):
    """Close the valley's outline with cliffs (2026-09-18: the map had no
    edge; the engine supports any position at z <= 0, so an unbuilt cell
    at ground level is walkable forever). lv_landscape.rim over the
    valley's chunks, two courses and a crest, except the south and east
    edges, which face the camera: a 96-high course there covered the
    Avatar against it (playtest-2026-10-11-build7 finding 2), so they are
    flush — no course above the ground, two of retail's invisible wall on
    it. The massif's chunks are passed too so no rim stands between the
    valley and the massif; the massif's own outline is the field's faces."""
    chunks = {(kx, ky): 0 for kx in range(CX0 // 4, CX1 // 4 + 1)
              for ky in range(CY0 // 4, CY1 // 4 + 1)}
    flush = {(kx, ky, side) for (kx, ky) in chunks
             for side, nb in (('south', (kx, ky + 1)), ('east', (kx + 1, ky)))
             if nb not in chunks}
    out = []
    for it in rim(chunks, courses=2, crest=True, flush=flush):
        # Only where the valley (z 0) meets the map's outline: the field
        # cell the piece stands beside, or one either side of it along the
        # edge, is valley. The rest of the outline is the massif's, the
        # cloud's and the terrace's own faces.
        cx = min(max(T.cell_of(it.x - 16), CX0), CX1)
        cy = min(max(T.cell_of(it.y - 16), CY0), CY1)
        if any((cx + i, cy + j) in valley
               for i in (-1, 0, 1) for j in (-1, 0, 1)):
            out.append(it)
    return out


def valley_water_skirt():
    """Four chunks of navy water beyond the valley's existing barriers.

    Retail glob 262 is sixteen 347:16 tiles. Glob 55 includes four bright
    bank tiles that would repeat as stripes across the open water.
    """
    chunks = {(kx, ky) for kx in range(0, 17) for ky in range(16, 28)
              if kx < CX0 // 4 or kx > CX1 // 4 or ky > CY1 // 4}
    chunks |= {(kx, ky) for kx in range(13, 17) for ky in range(12, 16)}
    return [MapItem.glob_egg(kx * 512 + 511, ky * 512 + 511, 0, 262)
            for kx, ky in sorted(chunks)]


def lake_shore_halo(field, valley, vcells, window):
    """Carry the water one cell into unwalked banks outside the windows."""
    busy = set(_climb_index()) | set(walk_cells(field, vcells, _climb_index()))
    busy |= valley
    halo = {}
    for (cx, cy), cell in sorted(field.items()):
        if cell.kind != T.WATER:
            continue
        for dx, dy in T.SIDES.values():
            n = (cx + dx, cy + dy)
            bank = field.get(n)
            if n in busy or bank is None or bank.kind != T.ROCK:
                continue
            if window(T.corner(n[0]), T.corner(n[1]), max(bank.z, cell.z),
                      TILE, TILE, 64):
                continue
            halo[n] = T.Cell(T.WATER, cell.z)
    field.update(halo)


def close_cloud_inlet(field, window):
    """Cap the cloud inlet inside the massif with rock at the same plane.

    The white patches at m13-29/31/42 are generated CLOUD cells west of
    the north leg. Rock tops at 56 preserve their former standing height;
    the summit's protected cloud and the eastern sea retain their art.
    """
    for (cx, cy), cell in field.items():
        if cell.kind != T.CLOUD or not (31 <= cx <= 37 and 17 <= cy <= 30):
            continue
        if not window(T.corner(cx), T.corner(cy), 48, TILE, TILE, 8):
            field[(cx, cy)] = T.Cell(T.ROCK, 56)


def lake_banks(terrain, field, window):
    """Keep cliff caps and texture a few water cells that touch rock."""
    import random
    frames = {'N': (0, 1), 'S': (4, 5), 'E': (6, 7), 'W': (2, 3)}
    bank_frames = {frozenset('N'): 4, frozenset('W'): 8,
                   frozenset('NW'): 14, frozenset('SW'): 15}
    for it in terrain:
        if it.shape != T.SHAPE_CREST:
            continue
        cx, cy = T.cell_of(it.x), T.cell_of(it.y)
        cell = field.get((cx, cy))
        if cell is None or cell.kind != T.ROCK or it.z != cell.z - 8:
            continue
        water = frozenset(side for side, (dx, dy) in T.SIDES.items()
                          if (nb := field.get((cx + dx, cy + dy)))
                          and nb.kind == T.WATER and 0 < cell.z - nb.z <= 16)
        if water in bank_frames and not window(it.x, it.y, it.z, TILE, TILE, 8):
            it.shape, it.frame = 128, bank_frames[water]
    for it in terrain:
        if it.shape != 347 or it.frame != 16:
            continue
        cx, cy = T.cell_of(it.x), T.cell_of(it.y)
        sides = [side for side, (dx, dy) in T.SIDES.items()
                 if (n := field.get((cx + dx, cy + dy)))
                 and n.kind in (T.ROCK, T.LOCK)]
        rng = random.Random(f'4013:lake:{cx}:{cy}')
        if sides and rng.random() < .18 and not window(
                it.x, it.y, it.z, TILE, TILE, 8):
            it.frame = rng.choice(frames[sides[0]])


# The approved south-coast profile, expressed as its last land cell per column.
SHORE_PROFILE = {
    12:96, 13:96, 14:97, 15:97, 16:96, 17:95, 18:95, 19:95,
    20:95, 21:96, 22:97, 23:99, 24:99, 25:98, 26:96, 27:95,
    28:95, 29:95, 30:96, 31:96, 32:97, 33:97, 34:96, 35:95,
    36:95, 37:96, 38:96, 39:97, 40:97, 41:98, 42:97, 43:96,
    44:95, 45:95, 46:96, 47:97, 48:97, 49:96, 50:96, 51:95,
}


EAST_SHORE_PROFILE = {
    64:52, 65:53, 66:53, 67:52, 68:51, 69:51, 70:52, 71:53,
    72:53, 73:52, 74:52, 75:51, 76:51, 77:52, 78:52, 79:53,
    80:54, 81:54, 82:53, 83:52, 84:51, 85:51, 86:52, 87:53,
    88:53, 89:52, 90:51, 91:51, 92:52, 93:53, 94:53, 95:52,
}


def cliff_coast():
    """A low coast outside the retained barriers, with one broken headland."""
    south = {(x, y) for x, end in SHORE_PROFILE.items()
             for y in range(96, end + 1)}
    east = {(x, y) for y, end in EAST_SHORE_PROFILE.items()
            for x in range(52, end + 1)}
    land = south | east
    # The headland sits one cell seaward to keep its faces clear of the Avatar.
    bluff = {(23, 98): 56, (23, 99): 56, (24, 98): 56,
             (24, 99): 56, (25, 98): 56}
    out = []
    for x, y in sorted(land - set(bluff)):
        drops = {side for side, (dx, dy) in T.SIDES.items()
                 if (x + dx, y + dy) not in land
                 and not (side == 'N' and (x, y) in south)
                 and not (side == 'W' and (x, y) in east)}
        if drops:
            out.append(MapItem.placed_item(T.corner(x), T.corner(y), 0,
                                           125, T.crest_frame(x, y, drops)))
        else:
            out.append(MapItem.placed_item(T.corner(x), T.corner(y), 8,
                                           301, T.pick((0, 1, 2, 3, 4, 5), x, y, 413)))
    out.extend(T.emit({c: T.Cell(T.ROCK, z) for c, z in bluff.items()}))
    # Screen16's jagged pillar breaks into two unequal teeth and a low lump.
    # Their separate silhouettes leave water between the eroded remnants.
    out.extend([MapItem.placed_item(2943, 13055, 0, 193, 0),
                MapItem.placed_item(3103, 13151, -12, 193, 0),
                MapItem.placed_item(2911, 13247, 0, 125, 21)])
    # The smaller remnant has rounded native rocks, with an eight-unit tail.
    out.extend([MapItem.placed_item(3455, 13183, 0, 72, 1),
                MapItem.placed_item(3583, 13183, 0, 72, 0),
                MapItem.placed_item(3583, 13311, 0, 125, 19),
                MapItem.placed_item(3775, 13087, 0, 125, 15),
                MapItem.placed_item(3903, 13247, 0, 125, 20),
                MapItem.placed_item(4031, 13055, 0, 125, 22)])
    # Sparse waterline accents, all on cells touching the profile.
    accents = ((14, 98, 347, 17), (21, 97, 347, 4),
               (26, 98, 347, 2), (31, 97, 347, 8),
               (38, 97, 347, 1), (43, 97, 347, 5),
               (48, 98, 347, 6),
               (54, 66, 347, 7), (53, 70, 347, 2),
               (55, 80, 347, 6), (54, 88, 347, 3),
               (54, 65, 128, 6), (53, 78, 128, 7),
               (54, 94, 128, 5),
               (15, 98, 128, 4), (22, 98, 128, 14),
               (32, 98, 128, 8), (42, 98, 128, 15))
    out.extend(MapItem.placed_item(T.corner(x), T.corner(y),
                                   1 if shape == 347 else 0, shape, frame)
               for x, y, shape, frame in accents)
    out.extend([MapItem.placed_item(2815, 12863, 0, 70, 0),
                MapItem.placed_item(3839, 12735, 0, 72, 0),
                MapItem.placed_item(7103, 11007, 0, 72, 1),
                MapItem.placed_item(7167, 9151, 0, 70, 1)])
    # Move along the view ray past the retained barrier's box and margin.
    # The projected silhouette stays identical; the geometry is wholly outside.
    for it in out:
        # Flush caps and bank stones keep their tops on the valley plane.
        if (it.shape in (125, 128) and it.z == 0) or (it.shape == 301 and it.z == 8):
            it.z -= 8
        it.x += 96
        it.y += 96
        it.z += 24
    return out


RETAINED_LEDGE_GROUPS = (
    (66, 5, 1791, 3679, 224),
    (66, 0, 1855, 3455, 224),
    (138, 0, 1855, 4671, 168),
    (152, 0, 1855, 4639, 168),
    (152, 2, 1887, 6175, 168),
    (138, 1, 1791, 6143, 168),
    (138, 0, 1791, 6047, 168),
    (152, 0, 1887, 6047, 168),
    (152, 0, 1823, 7103, 112),
    (152, 1, 1727, 7295, 112),
    (66, 2, 1791, 8543, 112),
    (152, 0, 1855, 511, 224),
    (66, 0, 1951, 415, 224),
    (152, 2, 1791, 319, 224),
    (66, 5, 2015, 2111, 224),
    (66, 1, 1823, 1983, 224),
    (152, 2, 1855, 2303, 224),
    (66, 3, 1951, 5247, 168),
    (66, 1, 2175, 5087, 168),
    (152, 0, 2079, 5151, 168),
    (66, 1, 2047, 6559, 168),
    (66, 3, 2079, 6751, 168),
    (66, 3, 1855, 6719, 168),
    (66, 3, 1823, 6559, 168),
    (66, 2, 2047, 7455, 112),
    (66, 3, 2079, 7263, 112),
    (152, 1, 1855, 7359, 112),
    (152, 1, 2015, 7519, 112),
    (66, 1, 2303, 9151, 56),
    (66, 1, 2239, 9279, 56),
    (66, 4, 2431, 607, 224),
    (138, 1, 2431, 703, 224),
    (66, 3, 2239, 831, 224),
    (138, 0, 2719, 2463, 112),
    (66, 1, 2655, 2623, 112),
    (66, 5, 2463, 2591, 112),
    (152, 2, 2527, 2719, 112),
    (152, 0, 2815, 2815, 112),
    (66, 4, 2687, 9215, 112),
    (66, 1, 2815, 9119, 112),
    (152, 1, 2815, 9311, 112),
    (138, 1, 2911, 6911, 80),
    (66, 1, 2751, 7007, 80),
    (152, 0, 2751, 7167, 80),
    (66, 1, 2751, 6879, 80),
    (66, 1, 2943, 7039, 80),
    (138, 1, 3039, 2911, 112),
    (152, 0, 3167, 3167, 112),
    (66, 2, 2911, 3007, 112),
    (152, 0, 3007, 3455, 168),
    (152, 1, 3039, 3519, 168),
    (66, 0, 3327, 3583, 168),
    (152, 2, 5471, 7871, 56),
    (66, 0, 5887, 6623, 56),
    (66, 0, 5823, 6495, 56),
    (66, 5, 5599, 6495, 56),
    (66, 2, 6015, 7903, 56),
    (66, 4, 6047, 7775, 56),
    (152, 0, 6111, 7711, 56),
    (152, 2, 6271, 7423, 56),
    (66, 1, 5951, 7359, 56),
    (152, 0, 6015, 7167, 56),
    (66, 1, 6303, 6655, 56),
    (66, 2, 6271, 6303, 56),
    (66, 1, 6143, 6527, 56),
    (332, 2, 3071, 4991, 112),
    (219, 0, 3423, 8159, 112),
    (219, 0, 3423, 8447, 112),
    (358, 0, 4607, 7551, 40),
    (332, 0, 4703, 7391, 40),
    (332, 1, 5503, 7519, 56),
    (235, 0, 5631, 6879, 56),
    (358, 0, 6527, 7679, 56),
    (235, 1, 5631, 8319, 0),
    (332, 0, 6527, 8287, 0),
)


VALLEY_GROUPS = (
    ('west windfall', ((66, 2, 1887, 11743), (322, 1, 2015, 11807), (321, 3, 1951, 11711))),
    ('east scree', ((66, 0, 5471, 11007), (322, 4, 5599, 11103), (321, 0, 5695, 11071))),
    ('tidal spur', ((66, 5, 6143, 11839), (322, 2, 6303, 11903), (321, 1, 6367, 11935))),
    ('split outcrop', ((66, 1, 5055, 11615), (322, 0, 5119, 11679), (321, 2, 5151, 11583))),
    ('dry hollow', ((66, 4, 2463, 11999), (322, 3, 2623, 12031), (321, 4, 2527, 11935))),
    ('upper fan', ((66, 3, 5983, 10495), (322, 2, 6111, 10559), (321, 1, 6175, 10527))),
)


def phase4_dressing(items):
    """Authored landmarks first, then seam- and cliff-foot clusters."""
    import json
    import lv_dressing as D
    import lv_globs as G
    from dressing_metrics import item_class
    from parse_typeflag import load_typeflag
    shapes = load_typeflag(os.path.join(HERE, '../../../shared/build/TYPEFLAG.DAT'))
    site = D.Site(13, items, shapes, seed=4027)
    landmarks = {
        'split spur': ((66, 3, 2143, 10687, 0),
                       (66, 1, 2303, 10559, 0),
                       (152, 2, 2399, 10719, 0),
                       (465, 6, 2271, 10783, 0),
                       (465, 11, 2303, 10815, 0),
                       (322, 3, 2463, 10783, 0)),
        'wind-scoured perch': ((66, 4, 5855, 6047, 56),
                              (152, 1, 5983, 6143, 56),
                              (465, 4, 5839, 6175, 56),
                              (465, 12, 5887, 6207, 56),
                              (322, 2, 6015, 6239, 56),
                              (465, 7, 5759, 6271, 56),
                              (465, 2, 5807, 6319, 56),
                              (465, 13, 5887, 6351, 56),
                              (465, 0, 5759, 6135, 56),
                              (465, 5, 5807, 6095, 56),
                              (465, 10, 5871, 6087, 56),
                              (465, 14, 5919, 6175, 56),
                              (465, 8, 5983, 6207, 56),
                              (465, 1, 6047, 6175, 56),
                              (465, 11, 6031, 6303, 56),
                              (465, 6, 5967, 6335, 56),
                              (465, 3, 5791, 6359, 56),
                              (465, 15, 5855, 6407, 56),
                              (465, 12, 6063, 6271, 56)),
        'lake seep': ((65, 0, 3039, 6239, 80),
                      (65, 0, 3007, 6351, 80),
                      (65, 0, 3071, 6463, 80)),
        'city fall': ((875, 0, 4319, 511, 56),
                      (875, 1, 4511, 607, 56),
                      (876, 1, 4703, 735, 60),
                      (465, 3, 4607, 831, 56),
                      (465, 9, 4671, 863, 56)),
    }
    for name, rows in landmarks.items():
        site.set_piece(name, [MapItem.placed_item(x, y, z, shape, frame)
                              for shape, frame, x, y, z in rows])
    site.swap_chunks(plain=397, family=D.ROCK_FUNGUS, share=.5,
                     where=(1536, 10240, 6656, 12288))
    site.swap_chunks(plain=397, family=D.ROCK_DRESSED, share=.5,
                     where=(1536, 1664, 6656, 10240))
    # Broken groups punctuate the two earth fans, leaving the grey lane clear.
    for name, rows in VALLEY_GROUPS:
        site.set_piece(name, [MapItem.placed_item(x, y, 0, shape, frame)
                              for shape, frame, x, y in rows])
    # Keep the existing bones and use the kit's small debris on bare ledges.
    site.clusters(kit=tuple(row for row in D.KIT_BONES if row[0] in (465, 322)),
                  per100=12,
                  where=(1536, 1664, 6656, 10240),
                  floors={301}, anchor='wall')
    # Pebble spills occupy existing floors beside the inherited ledge groups.
    # Per-prop checks retain safe members in these already occupied chunks.
    for number, x, y, z in ((956, 6143, 8191, 0),
                             (957, 6143, 7167, 56),
                             (956, 5631, 9727, 0),
                             (957, 2047, 9727, 56)):
        site.place_prefab(number, x=x, y=y, z=z,
                          where=(1536, 1664, 6656, 10240))
    # Debris trails away from the city fragment across the cloud edge.
    site.place_prefab(956, x=4607, y=1023, z=56,
                      where=(1536, 0, 8191, 1663))
    site.beyond('stars', where=(0, 0, 16383, 2047), z=0)
    site.beyond('stars', where=(8192, 0, 16383, 6143), z=0)
    packed = site.pack()
    # Keep recurring pre-existing ground strips loose. Identical packed
    # strips would violate the three-chunk run contract.
    eggs = {(i.x // 512, i.y // 512): i for i in packed if i.is_glob_egg}
    loose = set()
    for (x, y), egg in eggs.items():
        if egg.quality < 3072:
            continue
        pieces = site.globs.glob_to_items(egg.quality, egg.x, egg.y, egg.z)
        if any(item_class(site.sorter.info(p.shape), p.shape, p.frame) != 'ground'
               for p in pieces):
            continue
        for dx, dy in ((1, 0), (0, 1)):
            row = [eggs.get((x + k * dx, y + k * dy)) for k in range(3)]
            if all(i is not None and i.quality == egg.quality for i in row):
                loose.add(egg.quality)
    result, expanded, removed = [], [], set()
    for it in packed:
        if it.is_glob_egg and it.quality in loose:
            pieces = site.globs.glob_to_items(it.quality, it.x, it.y, it.z)
            result.extend(pieces)
            expanded.extend(p.to_bytes().hex() for p in pieces)
            removed.add(it.to_bytes().hex())
        else:
            result.append(it)
    from build_all_maps import RECORD_BUDGET
    if len(result) > min(D.RAW_CEILING[13], RECORD_BUDGET[13]):
        raise ValueError('Map 13 final raw record ceiling exceeded')
    # Expansion preserves expanded geometry and its already checked budget.
    # Persist the final records so the structural audit sees exactly FIXED.
    doc = G.registry()
    provenance = doc['dressing']['13']
    provenance['eggs'] = [key for key in provenance['eggs'] if key not in removed]
    provenance['records'].extend(expanded)
    provenance['ledger'].append(dict(operation='unpack_ground_runs',
                                     eggs=len(removed), records=len(expanded)))
    G.MANIFEST.write_text(json.dumps(doc, indent=2) + '\n')
    return result



# ===========================================================================
# THE SUMMIT (screen01)
# ===========================================================================
def build_summit():
    """The teleport pair to Cloud City (z 120). The 1994 summit's north is
    cloud, so the pair moved from (4096,512)/(4096,128), which are cloud
    now (and screen01 sits 1024 further south than its reconstruction
    placed it, so the black beyond the map's north edge stays out of a
    summit view). The climb arrives at the plateau's north-east corner, so
    the trigger 209's box (+/-416 x 32) lies across the plateau's south,
    where the walk from the climb ends, and the pad (Map 17's trigger 208
    lands on it) stands on the climb's north leg at y 2303, east of that
    box's x span and due east of the trigger: an arrival held south or a
    walk back down the climb crosses no trigger (on the plateau, any way
    back north crossed it), and pad to trigger is a walk west, not the
    south-west that carried an arrival on Map 17 into its trigger 208."""
    return [
        MapItem.teleport_target(x=5119, y=2303, z=CLIMB_Z_TOP,
                                teleport_id=208),
        MapItem.teleporter(x=4351, y=2303, z=CLIMB_Z_TOP,
                           teleport_id=209, dest_npc=209, dest_map=17),
    ]


# ===========================================================================
# CURBS
# ===========================================================================
# Retail's invisible wall (497/498, never drawn, still solid). Two kinds:
#
#  * the climb's: beyond every side of every climb cell above the valley
#    floor (the foot, at z 0, stays open to the valley) that is not climb
#    and not higher ground (whose face already stops him), at every
#    height. A running Avatar drifts right of his heading on every uphill
#    leg (docs/playtest-2026-10-11-fix7.md finding 1); a keyboard run
#    turns its slide into its heading (fix9 C1); a hold carried past a
#    bend runs straight off the bend square. Walled both sides, the slide
#    is refused and the run turns back along the lane. test_climb_width
#    holds cover all three.
#  * everywhere else he can walk to (the cells the climb reaches at
#    steps of 8 or less): beyond every side that drops CURB_DROP or more —
#    the summit's edge over the cloud and the crag's 120-unit west face,
#    the skull ring path's drop into the black.
CURB_DROP = 32


def _climb_index():
    return {(T.cell_of(x), T.cell_of(y)): z
            for (x, y), z in climb_cells().items()}


def walk_cells(field, vcells, seeds):
    """{cell: standing z} for every non-climb cell walked to from `seeds`
    ({cell: z}) at steps of 8 or less, cell by cell (the field's levels,
    a shot cell's top; water and cloud are not stood on)."""
    climb = _climb_index()

    def stand(c):
        cell = field.get(c)
        if cell is None or c in climb:
            return None
        if cell.kind == T.LOCK:
            return vcells[c]['top'] if not vcells[c]['water'] else None
        return cell.z if cell.kind in (T.ROCK, T.HIDDEN) else None
    walkers, queue = {}, deque(seeds)
    seen = set(seeds)
    while queue:
        c = queue.popleft()
        z = seeds.get(c, walkers.get(c))
        for dx, dy in T.SIDES.values():
            n = (c[0] + dx, c[1] + dy)
            if n in seen:
                continue
            zn = stand(n)
            if zn is None or abs(zn - z) > 8:
                continue
            seen.add(n)
            walkers[n] = zn
            queue.append(n)
    return walkers


def spur_ground(field=None, vcells=None):
    """{cell: z}: the shot ground the climb opens onto through CLIMB_SPURS
    (screen14's skull ring path), walked to from the spur cells."""
    if field is None:
        field, _, (_, _, vcells) = build_field()
    return walk_cells(field, vcells,
                      {c: z for c, z in CLIMB_SPURS.items()})


def build_curbs(field, region, vcells):
    cells = _climb_index()
    level = field_level(field)
    apron = foot_apron()
    out = []
    # The climb's own: every side not climb and not a face above his step
    # (more than 8 higher: a ledge 8 up, the lake's stepping stones beside
    # the east leg, is stepped onto), except toward the foot's apron (the
    # valley's way on) and where it walks onto a shot's ground at its own
    # level (the summit's south rim, screen14's path at the spur).
    for (cx, cy), z in sorted(cells.items()):
        if z <= 0:
            continue
        X, Y = T.corner(cx), T.corner(cy)
        for side, (dx, dy) in T.SIDES.items():
            nb = (cx + dx, cy + dy)
            if nb in cells or nb in apron:
                continue
            if level(nb, T.OPPOSITE[side]) > z + 8:
                continue
            if nb in vcells \
                    and not vcells[nb]['water'] and vcells[nb]['top'] == z:
                continue
            shape, x, y = T.CURB_AT[side](X, Y)
            out.append(MapItem.placed_item(x, y, z, shape, 0))
    # Everything walked to from the climb at steps of 8 or less.
    walkers = walk_cells(field, vcells, cells)
    out += T.edge_curbs(level, walkers, CURB_DROP)
    return out


# ===========================================================================
# UNDER THE FLOATING CLOUD
# ===========================================================================
# screen13's floating layer (FLOATING) draws over everything below it, an
# Avatar walking the island under it included: SortItem::below orders a
# flat and an actor by z first, and the layer carries no SI_ROOF, so the
# camera's roof cut (CameraProcess::findRoof) never lifts it off him. The
# island stays open under it all the same (Douglas 2026-10-30, round-2
# card 1b): he can walk under the cloud and is hidden while he does. Phase
# E had curbed off the 73 cells where it would draw over him.


# ===========================================================================
# DRESSING
# ===========================================================================
# Sprite bounds preserve the five 1994 camera windows and their margin.
WINDOW_MARGIN = 16
VALLEY_CLEAR = (2687, 10111, 4735, 11135)


def window_rects():
    """Each 1994 shot's window on the map as (sx0, sy0, w, h) in the
    painter's screen frame (vignette_replay.world_camera, camera.crop)."""
    out = []
    for shot in VIGNETTES:
        vig = VP.load(shot)
        ox, oy, oz = vig['placement']['origin_world']
        cam = vig['camera']
        w, h = cam['crop']
        out.append((cam['sx0'] + ox // 4 - oy // 4,
                    cam['sy0'] + ox // 8 + oy // 8 - oz, w, h))
    return out


def in_a_window(rects, x, y, z, xd, yd, zd):
    """Could a piece with max corner (x, y, z) and box xd x yd x zd draw
    into a window? Its box's eight corners projected (screen x = x/4 -
    y/4, y = x/8 + y/8 - z), widened by WINDOW_MARGIN."""
    sxa, sxb = (x - xd) // 4 - y // 4, x // 4 - (y - yd) // 4
    sya = (x - xd) // 8 + (y - yd) // 8 - (z + zd)
    syb = x // 8 + y // 8 - z
    m = WINDOW_MARGIN
    return any(sxa - m < rx + w and sxb + m > rx and
               sya - m < ry + h and syb + m > ry
               for (rx, ry, w, h) in rects)


# ===========================================================================
# THE MAP
# ===========================================================================
def globbed_chunks(field, valley, smooth):
    """{chunk: z} for the massif's chunks that are one flat tier: all 16
    cells rock at one level, none of them the climb or a shot, and none
    with a face the camera sees (a glob floor sits at the level itself, a
    crest 8 lower, so a seen face would show the 8-unit gap). Their floor
    is glob 397 at that z — the cave floor of the shots — and the cells
    keep only their hidden faces."""
    by_chunk = {}
    for (cx, cy), c in field.items():
        by_chunk.setdefault((cx // 4, cy // 4), []).append(((cx, cy), c))
    out = {}
    for k, cells in sorted(by_chunk.items()):
        if len(cells) != 16:
            continue
        zs = {c.z for _, c in cells if c.kind == T.ROCK}
        if len(zs) != 1 or any(c.kind != T.ROCK or c.floor or cc in valley
                               or cc in smooth for cc, c in cells):
            continue
        if any(set(T.drops_of(field, *cc, smooth=smooth)[0]) & {'S', 'E'}
               for cc, _ in cells):
            continue
        out[k] = zs.pop()
    return out


def window_fills(items):
    """WINDOW_FILLS as items, each refused if its box meets a solid's."""
    import vignette_place as VP
    flags = VP._flags()
    solids = [T._box_of(flags, it) for it in items
              if not it.is_glob_egg and (flags.get(it.shape) or {}).get('solid')]
    out = []
    for shape, frame, x, y, z in WINDOW_FILLS:
        it = MapItem.placed_item(x, y, z, shape, frame)
        if T._meets_any(T._box_of(flags, it), [b for b in solids if b]):
            raise ValueError(f'window fill {(shape, frame, x, y, z)} meets a '
                             'solid: slide it along the view ray to a free spot')
        out.append(it)
    return out


def north_frame_backdrop():
    """Clear the beyond-world wedge visible above the north cloud edge.

    FIXED positions are unsigned. Moving a virtual negative-y plate by
    (1008, 1008, 252) preserves its projection and gives it valid coordinates.
    Black is the void-floor fallback here: star shape 351 currently counts
    as ground in shared dressing metrics, so a raised star plane would mask
    the summit's real ground measurements. That shared change is requested
    in the slice report.
    """
    return [MapItem.placed_item(x + 1008, y + 1008, 252, 564, 2)
            for x in range(2303, 10240, 256)
            for y in (-769, -513, -257, -1)]


def build_map_13(fit=None, keys=None):
    """Build complete Map 13 item list (`fit`: see build_field; `keys`: see
    lv_map13_tiers.shot_faces)."""
    field, valley, (vitems, region, vcells) = build_field(fit)
    smooth = {(T.cell_of(x), T.cell_of(y)) for (x, y) in climb_cells()}
    rects = window_rects()

    def window(*box):
        return in_a_window(rects, *box)
    close_cloud_inlet(field, window)
    lake_shore_halo(field, valley, vcells, window)
    globbed = globbed_chunks(field, valley, smooth)
    items = []
    items.extend(build_valley(valley))
    items.extend(MapItem.glob_egg(kx * 512 + 511, ky * 512 + 511, z,
                                  GLOB_ROCK)
                 for (kx, ky), z in sorted(globbed.items()))
    items.extend(build_base_zone())
    terrain = T.emit({c: v for c, v in field.items() if c not in valley},
                     smooth=smooth,
                     globbed={(cx, cy) for (cx, cy) in field
                              if (cx // 4, cy // 4) in globbed},
                     window=window)
    terrain = summit_face_caps(terrain)
    lake_banks(terrain, field, window)
    items.extend(terrain)
    items.extend(vitems)
    items.extend(summit_face_caps(
        T.shot_faces(field, vcells, vitems, unfaced(fit),
                     window=window, around=terrain, keys=keys), keys))
    items.extend(T.cloud_fill(field, vcells, unfaced(fit)))
    items.extend(window_fills(items))
    items.extend(build_summit())
    items.extend(build_harpies())
    items.extend(build_curbs(field, region, vcells))
    items.extend(build_valley_rim(valley))
    items.extend(valley_water_skirt())
    items.extend(cliff_coast())
    for cx, cy in sorted(foot_apron()):
        if not window(T.corner(cx), T.corner(cy), 0, TILE, TILE, 8):
            items.append(MapItem.placed_item(
                T.corner(cx), T.corner(cy), 0, 70, 0))
    # The void floor (2026-09-16): black plates under every void cell
    # within view of a floor — the engine never clears the frame without
    # `usehighres` (.claude/rules/map-geometry.md, last section). Last, so
    # it sees every ledge; it overlaps floors harmlessly.
    items.extend(MapItem.placed_item(x, y, z, shape, frame)
                 for shape, frame, x, y, z in RETAINED_LEDGE_GROUPS)
    items = phase4_dressing(items)
    north = north_frame_backdrop()
    # Derive the physical void cover before adding the virtual north plane.
    # Its ray-shifted boxes must leave the original floor coverage intact.
    fill = void_floor(items)
    items.extend(north)
    items.extend(fill)
    from lv_dressing import RAW_CEILING
    if len(items) > RAW_CEILING[13]:
        raise ValueError('Map 13 final raw record ceiling exceeded after void fill')
    return items


if __name__ == '__main__':
    items = build_map_13()
    globs = sum(1 for i in items if i.is_glob_egg)
    teles = sum(1 for i in items if i.is_teleport_egg)
    mons = sum(1 for i in items if i.is_monster_egg)
    print(f"Map 13: {len(items)} items")
    print(f"  Glob eggs: {globs}")
    print(f"  Teleport eggs: {teles}")
    print(f"  Monster eggs: {mons}")
    print(f"  Other items: {len(items) - globs - teles - mons}")

#!/usr/bin/env python3
"""
build_map_17.py — Map 17: Cloud City, the open 1994 city.

REBUILT 2026-10-17 (phase C of the 1994 screenshot reconstruction,
docs/research/2026-10-16-screenshot-reconstruction.md and its phaseC/map17/
REPORT.md). The two published 1994 shots of Cloud City are stamped into
the map verbatim (vignette_place.stamp) and the rest of the city is
extrapolated around them in their own vocabulary:

  screen11  the obelisk plaza: cloud floor to every frame edge, the
            obelisk as retail pieces (12 f14-f17, cap 545, skull 814) on
            four banded drums, a ring of gem pillars (the white column
            875 f0 under a retail gem 596), the skeletons and the sun
            Shield half, the Avatar's spot. Origin (1280, 4736, 0).
  screen12  the raised marble walkway (877) and the throne nook between
            its two strips: banded posts, the throne 223, rubble, bones,
            the eye Shield half; gold brick (876) beyond. Origin
            (1024, 1024, 0).

Around them (one 128-unit cell = one floor tile, all at z=0):

  * an open cloud landscape (874 f0-f2) whose outline is the features
    grown by five to seven cells with a lobed edge, void only beyond it,
    and retail's invisible curb (497/498) on every walkable side that
    faces the void;
  * gold brick (876) streets and plazas: the scroll court in the north,
    the forecourt below the walkway, the processional street from the
    walkway to the obelisk plaza, the south street, the arrival landing,
    and the east court;
  * the walkway's two strips run on east and west of the shot, and a third
    strip crosses to the east court, every strip with a banded-post
    colonnade on both sides at 192 units (screen12's rhythm), posts on the
    slab's front edge standing on it (z 8);
  * gem pillars along the processional street and in the courts, and
    screen11's outer square of plain columns carried round the plaza;
  * the plaques on white two-drum supports at their original anchors;
  * nothing generated that would paint into either shot's window
    (window_clear), so the stamped shots stay exactly the vignettes.

No stone rooms, tapestries, lamps or ceilings: the 1994 shots show none.

The arrival (2026-10-17, coordinated with the Map 13 rebuild, where the
player now crosses trigger 209 heading south): pad 209 lies on the gold
landing; trigger 208 back to the Cloud Cliffs lies on a cloud pier south
of a void channel, reached only round the channel's east end. A hold in
any one direction from the pad either stops at a curb or slides past the
channel's end and on away from the trigger, never into it
(test_route_reach's arrival corridors).

Pins (map_pins.json): the two teleport eggs and EggReapply, the Shield
halves (878, the 1994 art since 2026-10-17, TypeAOFrizbee; npcnum 236
dispatches class 1260), the Message Scroll (a route-test goal), the four
gold plaques (614, npcnum 235 -> class 1259). The obelisk is no shape of
its own: custom art 861 is retired, and the retail composite's front drum
carries QUALITY_OBELISK for the deferred MAGNET wiring (derive_map_pins
DECORATIVE/DEFERRED).
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from u8_map import MapItem                                  # noqa: E402
from lv_furnish import void_floor                          # noqa: E402
from lv_shapes import (                                     # noqa: E402
    SHAPE_MESSAGE_SCROLL, SHAPE_SHIELD_HALVES, NPCNUM_SHIELD_HALVES,
    SHAPE_PLAQUE_ON_Y_WALL, NPCNUM_GOLD_PLAQUE, SHAPE_BLOCKER_X,
    SHAPE_BLOCKER_Y, SHAPE_CLOUD_1994, SHAPE_WHITE_COLUMN_1994,
    SHAPE_GOLD_BRICK_1994, SHAPE_MARBLE_WALKWAY_1994, SHAPE_TALISMAN_GEM,
    SHAPE_GEM_CAP_1994, SHAPE_WALKWAY_END_1994,
    SHAPE_NOOK_DAIS_1994,
    SHAPE_BONES_A, SHAPE_BONES_B,
)
import vignette_place as VP                                 # noqa: E402
# EggReapply on the arrival pad (209, the only way in), 2026-10-11. The
# Shield halves are fixed records, and World::switchMap re-reads every fixed
# record on each entry, so a picked-up pair lay here again at the next visit
# and after the ceremony (docs/playtest-2026-10-11-static-art.md finding 2).
# The egg (lv-new/REAPPLY.UNK) destroys each half once shieldFixed is set or
# the Avatar already carries that half, and hatches as the player lands.
from build_map_11 import reapply_egg                        # noqa: E402

CELL = 128
VIGNETTES = ('screen11', 'screen12')

SHAPE_CLOUD = SHAPE_CLOUD_1994          # 874, 1994 cloud floor
CLOUD_FRAMES = (0, 1, 2)                # 3/4 are 0/2 mirrored: the shots'
                                        # edge cells only
SHAPE_GOLD = SHAPE_GOLD_BRICK_1994      # 876
GOLD_FRAMES = (0, 1)
SHAPE_WALKWAY = SHAPE_MARBLE_WALKWAY_1994   # 877, 128x128x8, top at z 8
WALKWAY_TOP = 8
SHAPE_COLUMN = SHAPE_WHITE_COLUMN_1994  # 875: frame 0 plain, 1 banded
COLUMN_PLAIN, COLUMN_BANDED = 0, 1
COLUMN_HEIGHT = 40
SHAPE_GEM = SHAPE_GEM_CAP_1994          # 880: retail 596's frames, FIXED. The
                                        # shots' 596 is TypeTalisman, which a
                                        # player could lift off a pillar and
                                        # feed to a Map 11 receptacle
ART_MAP = {SHAPE_TALISMAN_GEM: SHAPE_GEM}   # the vignettes' 596 -> 880, frames kept
GEM_FRAMES = (2, 3, 4, 5, 6, 7)         # screen11's six
SHAPE_BOTTLE = 471                      # screen11/12's bottles and vases
POST_RHYTHM = 192                       # screen12's colonnade, both sides

# Quest items. The Message Scroll's position is pinned by test_route_reach
# (derive_map_pins.route_cite greps it for the literal "3328, 1536,"), so
# it may not move by a unit; it lies on a marble plinth whose top is z 8.
QUALITY_MSG_SCROLL = 80
SCROLL_POS = (3328, 1536, 8)
SCROLL_PLINTH = (3327, 1535, 0)
# Shield halves: 878 since 2026-10-17, the 1994 art (sun half frame 0,
# eye half frame 1), placed where screen11 and screen12 show them. TYPEFLAG
# is 828's row: carryable, not an equip-slot item.
# TYPE_SHAPES['TypeAOFrizbee'] MUST equal it: SHADES.UNK's `foreach ...
# where type = TypeAOFrizbee` within the backpack finds the halves.
#
# FRAME IS LOAD-BEARING: SHADES.UNK identifies the two halves by
# getFrame() = 0 (half 1) and getFrame() = 1 (half 2). Quality (81/82) is
# cosmetic identity only; the usecode does not read it. The halves dispatch
# TypeAOFrizbee (ZEALSHLD.UNK) through npcnum 236 -> class 1260 (the engine's
# npcnum + 1024 patch), per placement, so no other shield gets the class.
QUALITY_SHIELD_HALF_1 = 81
QUALITY_SHIELD_HALF_2 = 82
# The obelisk is the retail composite in screen11. QUALITY_OBELISK rides on
# its front drum (the 875 f1 nearest the camera), where the vignette's
# pin_moves put the MAGNET egg if it is ever placed.
QUALITY_OBELISK = 90
OBELISK_FRONT_DRUM = (4127, 7199, 0)

# The MAGNET egg stays unplaced (derive_map_pins DEFERRED): EggMagnet and
# EggCandleTrick are per-tick monitors that need H1's process semantics,
# nothing can light a candle (TypeMagicCandle resolves to the 295 wall
# relief and no candle art is unlit at frame 0 with a lit frame 1), and
# MAGNET.UNK pops the Avatar's magic items to a hard-coded (15615, 19839,
# 120) that must be retargeted to this obelisk in an lv-patched copy first.
# The two CANTRK revisions reach the same solution (candles 2 and 6 lit).

# Teleports (2026-10-17). Pad 209 on the arrival landing; trigger 208 on
# the pier south of the void channel, its +/-416 hatch box well inside the
# channel's 1152-unit half-length either side of the pad's x.
PAD_209 = (4608, 9984, 0)
TRIGGER_208 = (4608, 11008, 0)


# ── The layout, in 128-unit cells ─────────────────────────────────────────
# Rectangles are world (x0, y0, x1, y1), half-open, on cell boundaries.

GOLD_AREAS = [
    (2688, 1024, 3968, 2048),     # the scroll court
    (2688, 3584, 4480, 4480),     # the forecourt below the walkway (screen12
                                  # shows its gold at the bottom left)
    (1664, 3072, 3200, 3456),     # the aisle between the strips, west of
    (4224, 3072, 6656, 3456),     # the nook and east of it (screen12's gold
                                  # at x 2943-3071 and 4351)
    (3712, 4480, 4480, 6144),     # the processional street to the plaza
    (4224, 7936, 4992, 9472),     # the south street from the plaza
    (3200, 9472, 6016, 10496),    # the arrival landing
    (5632, 4864, 6912, 6272),     # the east court
]
CLOUD_AREAS = [
    (1664, 2560, 6784, 4096),     # the walkway's field (screen12)
    (2944, 6016, 5248, 8064),     # the obelisk plaza (screen11, all cloud)
]
# The walkway strips: slab rows at y (max corner), x from..to (max corners).
# screen12 ends both of its strips at x 4095 (phase D, 2026-10-25): the last
# slab is the 883 east-end cut behind a two-drum post at x 4127, and the shot
# shows cloud past it, so A and B run west only. (y, x0, x1, east end piece)
STRIPS = [
    (3103, 1663, 3967, True),     # strip A (screen12's upper strip)
    (3583, 1663, 3967, True),     # strip B (its lower strip)
    (5759, 4479, 6911, False),    # strip C, the street to the east court
]
# The arrival: everything south of the landing is void but the pier and
# the bridge round the channel's east end.
SOUTH_CUT = 10496
PIER = (3584, 10752, 6016, 11264)
BRIDGE = (5760, 10496, 6016, 10752)
OUTLINE_GROW = 8                  # cells of cloud round every feature, +0..2:
                                  # no void within ~1000 of a walk (Fable)


def _cells_of(rect):
    x0, y0, x1, y1 = rect
    return {(cx, cy) for cx in range(x0 // CELL, (x1 - 1) // CELL + 1)
            for cy in range(y0 // CELL, (y1 - 1) // CELL + 1)}


def _hash(cx, cy, salt=0):
    return ((cx * 73856093) ^ (cy * 19349663) ^ (salt * 83492791)) & 0xFFFF


def layout():
    """{cell: 'cloud' | 'gold'}: every walkable floor cell. Walkway slabs
    stand on cloud cells (the floor under them never shows)."""
    feature = set()
    gold = set()
    for r in GOLD_AREAS:
        cells = _cells_of(r)
        # Ragged edges, not rectangles (screen12/13's gold meets the cloud
        # in lobes, never a hard line): on a coarse two-cell grid, a quarter
        # of each area's border goes back to cloud and a quarter of the ring
        # outside it turns gold; then no gold cell is left with fewer than
        # two gold sides.
        ring = {(cx + dx, cy + dy) for cx, cy in cells
                for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - cells
        border = {c for c in cells
                  if any((c[0] + dx, c[1] + dy) in ring
                         for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        lump = (lambda c: _hash(c[0] // 2, c[1] // 2, 11) % 4)
        gold |= {c for c in cells if c not in border or lump(c) != 0}
        gold |= {c for c in ring if lump(c) == 1}
    for _ in range(2):
        gold = {c for c in gold
                if sum((c[0] + dx, c[1] + dy) in gold
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 2}
    # Material bays stay within the original cloud envelope. Its growth
    # and every curb continue to use the original feature footprint.
    city_gold = set(gold)
    for cy, left, right in ((35,24,28), (36,23,28), (37,22,28),
                            (38,22,28), (39,22,28), (40,22,28),
                            (41,22,28), (42,22,28), (43,23,28),
                            (44,24,28), (45,25,28),
                            (37,35,40), (38,35,41), (39,35,42),
                            (40,35,43), (41,35,43), (42,35,43),
                            (43,35,43), (44,35,42), (45,35,41),
                            (46,35,40)):
        gold.update((cx, cy) for cx in range(left, right + 1))
    gold |= _cells_of((5120, 8448, 5888, 9216))
    gold |= _cells_of((5248, 7296, 6016, 8064))
    gold.add((21, 39))
    feature |= city_gold
    for r in CLOUD_AREAS:
        feature |= _cells_of(r)
    for y, x0, x1, _end in STRIPS:
        feature |= _cells_of((x0 - 127, y - 127, x1 + 1, y + 1))
    feature |= _cells_of(PIER) | _cells_of(BRIDGE)
    # Grow by OUTLINE_GROW..+2 cells (a lobed rim), a multi-source BFS in
    # Chebyshev steps so the rim is a cloud bank, not a stair.
    dist = {c: 0 for c in feature}
    frontier = list(feature)
    reach = OUTLINE_GROW + 2
    for d in range(1, reach + 1):
        nxt = []
        for cx, cy in frontier:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (cx + dx, cy + dy)
                    if n not in dist:
                        dist[n] = d
                        nxt.append(n)
        frontier = nxt

    def lobe(c):
        # Lobes 2-3 cells across: the noise is taken on a coarse 2-cell
        # grid, so neighbouring rim cells agree.
        return OUTLINE_GROW + _hash(c[0] // 2, c[1] // 2, 7) % 3

    out = {}
    for c, d in dist.items():
        if d <= lobe(c) and c[0] >= 1 and c[1] >= 1:
            out[c] = 'gold' if c in gold else 'cloud'
    # Smooth the rim twice: a void cell walled by five or more cloud cells
    # is filled, a rim cell with two or fewer walkable neighbours dropped,
    # so no one-cell pocket or spur needs its own ring of curbs.
    nb8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
    for _ in range(2):
        cand = {(cx + dx, cy + dy) for cx, cy in out for dx, dy in nb8} | set(out)
        nxt = dict(out)
        for c in cand:
            n = sum((c[0] + dx, c[1] + dy) in out for dx, dy in nb8)
            if c not in out and n >= 5 and c[0] >= 1 and c[1] >= 1:
                nxt[c] = 'cloud'
            elif c in out and c not in feature and n <= 2:
                del nxt[c]
        out = nxt
    pier, bridge = _cells_of(PIER), _cells_of(BRIDGE)
    for c in list(out):
        if c[1] >= SOUTH_CUT // CELL and c not in pier and c not in bridge:
            del out[c]
    return out


def _gold_frame(cx, cy):
    # Frame one has eight transparent edge pixels. Isolated accents keep
    # neighbouring full tiles beneath those cuts and break the old checker.
    value = random.Random(f'17:gold:{cx}:{cy}').random()
    neighbours = ((cx+1,cy), (cx-1,cy), (cx,cy+1), (cx,cy-1))
    return int(value < .45 and all(
        value < random.Random(f'17:gold:{x}:{y}').random()
        for x, y in neighbours))


# Distinct foundations give the ruined bays their former court footprints.
DRESSING_GOLD_COURTS = {
    'north observatory': {(44,13), (45,13), (46,13),
                         (43,14), (44,14), (45,14), (46,14), (47,14),
                         (43,15), (44,15), (45,15), (46,15), (47,15),
                         (44,16), (45,16), (46,16)},
    'western votive court': {(16,43), (17,43), (15,44), (16,44), (17,44),
                            (18,44), (16,45), (17,45), (18,45), (17,46), (18,46)},
    'western broken court': {(18,58), (17,59), (18,59), (19,59),
                            (17,60), (18,60), (19,60), (20,60),
                            (17,61), (18,61), (19,61), (17,62), (18,62)},
    'western urn court': {(16,66), (16,67), (17,67), (17,68), (18,68),
                         (17,69), (18,69), (19,69), (18,70), (19,70)},
}
FOCAL_GOLD = set().union(*DRESSING_GOLD_COURTS.values())


def floors(cells):
    out = []
    for (cx, cy), mat in sorted(cells.items()):
        if (cx, cy) in FOCAL_GOLD:
            mat = 'gold'
        h = _hash(cx, cy)
        if mat == 'gold':
            shape = SHAPE_GOLD
            frame = (GOLD_FRAMES[h % 2] if 23 <= cx < 41 and 47 <= cy < 63
                     else _gold_frame(cx, cy))
        else:
            shape, frame = SHAPE_CLOUD, CLOUD_FRAMES[h % 3]
        out.append(MapItem.placed_item(cx * CELL + CELL - 1, cy * CELL + CELL - 1,
                                       0, shape, frame))
    return out


def cloud_sea(cells):
    """Paint lobes two to five cells beyond the retained playable outline."""
    # Retained collision follows layout(); these outer lobes are paint only.
    sea = set()
    for cx, cy in cells:
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                x, y = cx + dx, cy + dy
                radius = 2 + _hash(x // 3, y // 3, 81) % 4
                if x >= 1 and y >= 1 and dx * dx + dy * dy <= radius * radius:
                    sea.add((x, y))
    sea.update(cells)
    # Update in place so adjacent singleton flips cannot oscillate. Each
    # singleton flip shortens the perimeter; filling a corner join keeps
    # it unchanged. Repeating preserves the broad lobes and bays.
    neighbours = ((-1, 0), (1, 0), (0, -1), (0, 1))
    x0, x1 = min(x for x, y in sea) - 1, max(x for x, y in sea) + 1
    y0, y1 = min(y for x, y in sea) - 1, max(y for x, y in sea) + 1
    changed = True
    while changed:
        changed = False
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                c = (x, y)
                adjacent = sum((x + dx, y + dy) in sea
                               for dx, dy in neighbours)
                if c in sea and adjacent == 0:
                    assert c not in cells, ('isolated playable cell', c)
                    sea.remove(c)
                    changed = True
                elif c not in sea and adjacent == 4:
                    sea.add(c)
                    changed = True
        for x in range(x0, x1):
            for y in range(y0, y1):
                block = ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1))
                pattern = tuple(corner in sea for corner in block)
                if pattern in ((True, False, False, True),
                               (False, True, True, False)):
                    sea.add(next(corner for corner in block if corner not in sea))
                    changed = True
        # A continuous coastline also excludes enclosed star pockets with
        # several cells. Flood the outer sky, retaining every open bay.
        sky = {(x, y) for x in range(x0, x1 + 1)
               for y in range(y0, y1 + 1)} - sea
        outside, pending = set(), [(x0, y0)]
        while pending:
            c = pending.pop()
            if c not in sky or c in outside:
                continue
            outside.add(c)
            pending.extend((c[0] + dx, c[1] + dy) for dx, dy in neighbours)
        pockets = sky - outside
        if pockets:
            sea.update(pockets)
            changed = True
    assert not pockets, ('enclosed star pocket', sorted(pockets))
    connected, pending = set(), [next(iter(cells))]
    while pending:
        c = pending.pop()
        if c not in sea or c in connected:
            continue
        connected.add(c)
        pending.extend((c[0] + dx, c[1] + dy) for dx, dy in neighbours)
    assert connected == sea, 'disconnected cloud coastline'
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            adjacent = sum((x + dx, y + dy) in sea for dx, dy in neighbours)
            assert adjacent != (0 if (x, y) in sea else 4), (
                'isolated cloud or star cell', (x, y))
            pattern = tuple(corner in sea for corner in
                            ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)))
            assert pattern not in ((True, False, False, True),
                                   (False, True, True, False)), (
                'diagonal-only cloud or star join', (x, y))
    return floors({c: 'cloud' for c in sea - cells.keys()})


def curbs(cells):
    """Retail's invisible wall beyond every walkable side that faces the
    void (build_map_13's CURB_SIDES): the engine supports any position at
    z <= 0, so without them the cloud could be walked off forever."""
    out = []
    for (cx, cy) in sorted(cells):
        mx, my = cx * CELL + CELL - 1, cy * CELL + CELL - 1
        for (dx, dy), (shape, x, y) in (
                ((1, 0), (SHAPE_BLOCKER_Y, mx + 32, my)),
                ((-1, 0), (SHAPE_BLOCKER_Y, mx - CELL, my)),
                ((0, 1), (SHAPE_BLOCKER_X, mx, my + 32)),
                ((0, -1), (SHAPE_BLOCKER_X, mx, my - CELL))):
            if (cx + dx, cy + dy) not in cells:
                out.append(MapItem.placed_item(x, y, 0, shape, 0))
    return out


def column(x, y, z=0, frame=COLUMN_BANDED, drums=1):
    return [MapItem.placed_item(x, y, z + k * COLUMN_HEIGHT, SHAPE_COLUMN, frame)
            for k in range(drums)]


def gem_pillar(x, y, z=0):
    """screen11's gem pillar: the plain white column, a retail gem on top."""
    return column(x, y, z, COLUMN_PLAIN) + [MapItem.placed_item(
        x, y, z + COLUMN_HEIGHT, SHAPE_GEM, GEM_FRAMES[_hash(x, y, 3) % 6])]


def walkways():
    """The strips, and a banded-post colonnade down both long sides: posts
    on the cloud behind the slab's back rim (screen12's 2943 against strip
    A at 3103), and on the slab's front edge standing on it; every fourth
    back post two drums tall, as the shot's gate posts are. A back post is
    laid one step along the view ray, (x+32, y-128, z 8) for (x, y-160, 0):
    the same pixels, but its box clears the slab's back edge and sorts over
    the rim the slab draws 12 px high, as screen12 shows its back posts."""
    out = []
    for y, x0, x1, end in STRIPS:
        for x in range(x0, x1 + 1, CELL):
            out.append(MapItem.placed_item(x, y, 0, SHAPE_WALKWAY, 0))
        if end:
            out.append(MapItem.placed_item(x1 + CELL, y, 0, SHAPE_WALKWAY_END_1994, 0))
        for k, x in enumerate(range(x0 + 64, x1 - 63, POST_RHYTHM)):
            out += column(x + 32, y - 128, WALKWAY_TOP,
                          drums=2 if k % 4 == 0 else 1)
            out += column(x, y, WALKWAY_TOP)
    return out


def gold_plaque(x, y, quality):
    """A gold plaque on the south face of a stele, read through class 1259.

    Shape 614 has zero depth in y, so it hangs at the stele's y + 1, at
    z=16 as retail hangs its plaques. NPCNUM_GOLD_PLAQUE sends every event
    to TYPENSGOLDPLAQUE, whose readPlaque() picks the text by quality;
    qualities 55 and 68-70 are lv-patched/PLAQUENS.UNK's (docs/art-track.md
    contract 6). Without the npcnum, retail class 614 barks "plaque"."""
    return MapItem(x=x, y=y, z=16, shape=SHAPE_PLAQUE_ON_Y_WALL, frame=0,
                   quality=quality, npcnum=NPCNUM_GOLD_PLAQUE)


def stele(x, y, quality):
    """Two white drums carry the original plaque at its pinned anchor."""
    return column(x - 32, y, drums=2) + [gold_plaque(x - 32, y + 1, quality)]


def build_scroll_court():
    """The scroll court, north of the walkway: the Message Scroll on a
    marble plinth, four banded drums and two gem pillars round it."""
    px, py, _ = SCROLL_PLINTH
    # Keep the original support and its z 8 top. The throne nook's marble
    # end pieces close a square pedestal around it, with the pinned scroll
    # at its centre and a gold-trimmed face on each southern side.
    items = [MapItem.placed_item(*SCROLL_PLINTH, SHAPE_WALKWAY, 0)]
    items += [MapItem.placed_item(px + dx, py + dy, 0,
                                  SHAPE_NOOK_DAIS_1994, frame)
              for dx, dy, frame in ((128, 0, 2), (0, 128, 1), (128, 128, 1))]
    items.append(MapItem.placed_item(*SCROLL_POS, SHAPE_MESSAGE_SCROLL, 0,
                                     QUALITY_MSG_SCROLL))
    for dx in (-256, 256):
        for dy in (-256, 256):
            # The south-east post's upper drum clipped the scroll from
            # both southern tour views. One cell east clears its sprite.
            x = px + dx + (CELL if dx == dy == 256 else 0)
            items += column(x, py + dy, drums=2)
    for dx in (-448, 448):
        items += gem_pillar(px + dx, py)
    return items


def build_processional():
    """Gem pillars down both sides of the processional street (walkway to
    plaza) and of the south street (plaza to the arrival), every 256; the
    plaques of the two trios (EZREKAL.UNK:1536-1538) flank the street's
    head, "*ADMIRE*BUT*TOUCH NOT" (55) stands south of the plaza."""
    items = []
    for y in range(4735, 6144, 256):
        row = (y - 4735) // 256
        wx, wy = ((-32,-32), (-32,-64), (0,-32),
                  (-32,-64), (0,-64), (-32,0))[row]
        if y in (4991, 5759):
            items += column(3775 + wx, y + wy, drums=2)
        else:
            items += gem_pillar(3775 + wx, y + wy)
        dx, dy = ((32,-32), (32,-64), (32,-32),
                  (32,-64), (32,0), (32,-64))[row]
        if y == 6015:
            items += column(4447 + dx, y + dy, frame=COLUMN_PLAIN)
        else:
            items += gem_pillar(4447 + dx, y + dy)
    for y in range(8191, 9472, 256):
        items += gem_pillar(4287, y)
        dx, dy = {8191: (32, 64), 8447: (64, -32), 8703: (32, 32),
                  8959: (64, -64), 9215: (32, 64), 9471: (64, -32)}[y]
        items += gem_pillar(4959 + dx, y + dy)
    items += stele(3647, 4543, 69) + stele(4703, 4543, 70)
    items += stele(4159, 8255, 55)
    # Intact memorial columns use the established capped-pillar composition.
    items += gem_pillar(5311, 8511) + gem_pillar(5631, 9183)
    return items


def build_plaza_ring():
    """screen11's outer square of plain white columns (its rows at x 3359
    and y 6431) carried round the plaza at 160 units; the shot's own
    columns are in the vignette and window_clear drops the rest that
    would show in its frame."""
    items = []
    x0, y0, x1, y1 = 3359, 6431, 4863, 7935
    for x in range(x0, x1 + 1, 160):
        items += column(x, y0, frame=COLUMN_PLAIN)
        items += column(x, y1, frame=COLUMN_PLAIN)
    for y in range(y0 + 160, y1, 160):
        dx = (32,64,32,64,0,32,64,32,64)[(y-y0)//160-1]
        items += column(x0, y, frame=COLUMN_PLAIN)
        items += column(x1+dx, y, frame=COLUMN_PLAIN)
    return items


def build_east_court():
    """Five gem pillars turn a ruined corner beside two bare shafts.

    Six pieces of non-standing rubble complete the collapsed side in
    SET_PIECES. Bottles and bones share the north-east corner.
    """
    items = []
    # Five upright pillars turn the corner of the ruined court. The western
    # foot retains its existing invisible recess at (5887,6143).
    for x, y in ((5887,5055), (6240,5087), (6655,5055),
                 (5887,5439), (5887,6143)):
        items += gem_pillar(x, y)
    for x, y in ((6303,6111), (6719,5471)):
        items += column(x, y, frame=COLUMN_PLAIN)
    # Carryables share a corner, with separate clear floor footprints.
    for x, y, f in ((6719,5247,1), (6815,5279,6), (6591,5279,7)):
        items.append(MapItem.placed_item(x,y,0,SHAPE_BOTTLE,f))
    items.append(MapItem.placed_item(6815,5407,0,SHAPE_BONES_A,0))
    return items


def build_arrival():
    """The arrival landing and the pier. Pad 209 and EggReapply on the
    landing; trigger 208 on the pier, south of the channel. A plaque left
    of the way north: "Forbidden to mortals" (THORDIS.UNK:1594)."""
    items = [
        MapItem.teleport_target(*PAD_209, teleport_id=209),
        reapply_egg(*PAD_209),
        MapItem.teleporter(*TRIGGER_208, teleport_id=208, dest_npc=208,
                           dest_map=13),
    ]
    items += stele(4159, 9599, 68)
    # The drum colonnade marching up-screen from the landing (Fable's
    # first view) and two gem pillars at the bridge, one against each of
    # its curbs. They stood at x 5823 and 5951 until 2026-10-17, 96 apart,
    # which left a 64-unit body one 32-unit band of x to cross in (verifier
    # 2026-10-17 finding 5: a mouse walk could not thread it); at the
    # edges the way between them is 192 (test_route_reach: a 128 body
    # crosses).
    for x in (3455, 5759):
        for y in (9599, 9855, 10111, 10367):
            items += column(x, y, drums=2)
    items += (gem_pillar(BRIDGE[0] + 31, 10623)
              + gem_pillar(BRIDGE[2] - 1, 10623))
    for x, y, f in ((3967, 10303, 6), (5311, 9727, 7)):
        items.append(MapItem.placed_item(x, y, 0, SHAPE_BOTTLE, f))
    items.append(MapItem.placed_item(5183, 11135, 0, SHAPE_BONES_B, 1))
    return items


def build_walkway_field():
    """Round the throne nook, outside the shot: scattered remains."""
    return [MapItem.placed_item(2367, 3359, 0, SHAPE_BONES_A, 1),
            MapItem.placed_item(5311, 3327, 0, SHAPE_BONES_B, 0),
            MapItem.placed_item(5503, 3391, 0, SHAPE_BOTTLE, 6),
            MapItem.placed_item(1983, 3327, 0, SHAPE_BOTTLE, 7)]


# ── The shots' windows ───────────────────────────────────────────────────
_PAINTER = None


def _painter():
    global _PAINTER
    if _PAINTER is None:
        from vignette_paint import Painter
        from vignette_paint import BUILD
        _PAINTER = Painter.built(BUILD)
    return _PAINTER


def windows():
    """[(shot, camera x, camera y, W, H)] in world screen space."""
    from vignette_replay import world_camera, shot_size
    out = []
    for shot in VIGNETTES:
        vig = VP.load(shot)
        out.append((shot, *world_camera(vig), *shot_size(vig)))
    return out


def sprite_rect(it, cam_x, cam_y):
    fr = _painter().frame(it.shape, it.frame)
    if fr is None:
        return None
    hx = it.x // 4 - it.y // 4 - cam_x
    hy = it.x // 8 + it.y // 8 - it.z - cam_y
    left, top = hx - fr['xoff'], hy - fr['yoff']
    return left, top, left + fr['width'], top + fr['height']


def window_clear(items):
    """Drop every generated item that would paint into a shot's window.
    Eggs draw nothing and floors tessellate with the vignette's own (the
    window's every pixel is a vignette floor's), so both stay; a pinned
    item here is a layout error and raises."""
    wins = windows()
    keep = []
    for it in items:
        if it.is_glob_egg or it.is_teleport_egg or it.shape == MapItem.SHAPE_STANDARD_EGG \
                or it.shape in (SHAPE_CLOUD, SHAPE_GOLD):
            keep.append(it)
            continue
        hit = None
        for shot, cx, cy, w, h in wins:
            r = sprite_rect(it, cx, cy)
            if r and r[0] < w and r[2] > 0 and r[1] < h and r[3] > 0:
                hit = shot
                break
        if hit is None:
            keep.append(it)
        elif it.quality or it.npcnum:
            raise ValueError(f'quest/typed item shape {it.shape} at '
                             f'({it.x},{it.y},{it.z}) paints into {hit}')
    return keep


def fill_gaps(items, cells):
    """Cloud for every layout cell whose centre lacks a ground-level flat
    after the stamp. A shot's walkway slab straddles two cell rows (its y is 31 mod
    128), so vignette_place.hidden_ground counts the row it only grazes as
    floored, and the generated tile there went with the stamp."""
    covered = set()
    for it in items:
        info = VP._flags().get(it.shape)
        # Raised slabs cover only part of a cell. Keep cloud beneath them
        # so their uncovered strip cannot acquire a black void plate.
        if not info or not info['land'] or info['zfoot'] != 0 or it.z != 0:
            continue
        w, d = info['xfoot'] * 32, info['yfoot'] * 32
        for cx in range((it.x - w + 1) // CELL, it.x // CELL + 1):
            for cy in range((it.y - d + 1) // CELL, it.y // CELL + 1):
                mx, my = cx * CELL + CELL // 2, cy * CELL + CELL // 2
                if it.x - w < mx <= it.x and it.y - d < my <= it.y:
                    covered.add((cx, cy))
    return floors({c: 'cloud' for c in cells if c not in covered})


def quest_halves(items):
    """The vignettes' shield halves become the quest items: frame 0 (the
    sun, screen11) is half 1, frame 1 (the eye, screen12) half 2."""
    out = []
    n = 0
    for it in items:
        if it.shape == SHAPE_SHIELD_HALVES:
            it = MapItem(x=it.x, y=it.y, z=it.z, shape=it.shape, frame=it.frame,
                         quality=(QUALITY_SHIELD_HALF_1, QUALITY_SHIELD_HALF_2)[it.frame],
                         npcnum=NPCNUM_SHIELD_HALVES)
            n += 1
        elif (it.shape, it.frame, it.x, it.y, it.z) == \
                (SHAPE_COLUMN, COLUMN_BANDED, *OBELISK_FRONT_DRUM):
            it = MapItem.placed_item(it.x, it.y, it.z, it.shape, it.frame,
                                     QUALITY_OBELISK)
        out.append(it)
    if n != 2:
        raise ValueError(f'expected the two Shield halves in the vignettes, got {n}')
    return out


def column_recesses():
    """Keep the quest bands on the clear side of the colonnades.

    A single 40-unit drum hides more than half of a neighbouring Avatar.
    Preserve the columns and both 1994 windows, and recess their shadow
    sides with solid editor walls. Four courses close each column recess
    to 192; the original perimeter curbs and all pinned items stay in place.
    Bounds are half-open footprints, before the Avatar's 64-unit body.
    """
    posts = [
        # West ends of the two marble strips, including the next tall post.
        (2335, 2975), (2303, 3103), (2335, 3455), (2303, 3583),
        # Scroll court, throne nook, and the plaza's column ring.
        (2879, 1535), (3359, 6431), (3423, 3423), (3871, 7167),
        # Eight units east of the (3679, 3423) post clears the eye half.
        (4159, 7935), (3687, 3423), (3743, 6431), (3775, 6815),
        (4319, 7935), (3871, 6431), (4095, 6943), (4255, 7039),
        (4287, 7327), (3839, 3423), (3999, 3423), (4479, 7935),
        (4031, 6431), (4159, 6431), (4319, 6431), (3231, 3423),
        # The east court's western gem pillar.
        (5887, 6143),
    ]
    posts += [(4287, y) for y in range(8191, 9472, 256)]
    posts += [(3775, y) for y in range(4735, 6144, 256)]
    boxes = [(x - 128, y - 128, x, y) for x, y in posts]
    boxes += [
        # Two-drum shadows need a deeper recess. The scroll court retains
        # its eastern approach beside the drum at (3071, 1791).
        (2271, 3199, 2527, 3455),
        (2815, 1535, 3039, 1791),
        # The alternate leg passes the taller posts beside the shot.
        (3871, 3327, 4127, 3583),
        (3967, 3327, 4223, 3583),
        (3967, 3071, 4223, 3327),
        (3871, 2847, 4127, 3103),
        (2927, 3119, 3183, 3375),
        # The obelisk's cap stands at 120. Its whole north-west shadow
        # stays behind this recess; the sun half remains reachable east.
        (3647, 6687, 4159, 7199),
    ]
    positions = set()
    for x0, y0, x1, y1 in boxes:
        # The obelisk cap and the 88-unit posts offer no climb72 step
        # onto the invisible tops at 240 and 192, respectively.
        top = 240 if (x0, y0, x1, y1) == (3647, 6687, 4159, 7199) else 192
        # The final overlapping strip closes a width shorter than 128.
        for x in sorted(set(range(x0 + 128, x1 + 1, 128)) | {x1}):
            for y in range(y0 + 32, y1 + 1, 32):
                for z in range(0, top, 48):
                    positions.add((x, y, z))
    # The front ground strip leaves the skull and its drum clear of solids.
    positions.discard((4159, 7199, 0))
    # The movable bone containers need eight units clear below these
    # strips. The shifted course overlaps z48, so its top is blocked.
    for x, y in ((2335, 3359), (2399, 3263), (2399, 3295),
                 (2399, 3327), (2399, 3359), (3423, 3327)):
        positions.remove((x, y, 0))
        positions.add((x, y, 8))
    return [MapItem.placed_item(x, y, z, SHAPE_BLOCKER_X, 0)
            for x, y, z in sorted(positions)]


# Explicit scene records, separate from the immutable shot compositions.
# Each scene is accepted atomically and reserved by the shared API.
SET_PIECES = {
    'shrine offering crescent': (
        (2911,1279,0,909,0), (3615,1247,0,875,1),
        (3167,1215,0,909,0), (3391,1183,0,909,0),
        (3263,1215,0,909,0), (3455,1247,0,909,0)),
    'walkway broken terminus': (
        (5567,2943,0,875,1), (5855,3135,0,875,0),
        (5727,3071,0,905,0), (5983,3199,0,905,0),
        (6047,3263,0,910,7), (5791,3199,0,910,6),
        (6111,3103,0,910,8)),
    'processional votive bay': (
        (3455,4895,0,875,0), (3487,5343,0,875,1),
        (3039,5311,0,875,1), (3423,4799,0,875,1),
        (3199,5087,0,909,0), (3263,5151,0,909,0),
        (3871,5023,0,909,0),
        (3103,5023,0,909,0), (3295,4991,0,909,0),
        (3263,5471,0,905,0), (3359,5535,0,910,8)),
    'plaza empty council': (
        (5247,7455,0,223,0), (5567,7519,0,223,0),
        (5631,7903,0,223,1), (5535,8063,0,223,1),
        (5247,7967,0,223,3),
        (5055,7583,0,875,0), (5631,8255,0,875,1),
        (5183,7807,0,909,0), (5663,7935,0,909,0),
        (5215,7583,0,909,0), (5055,7935,0,909,0)),
    'south street memorial': (
        (5535,8768,0,614,0),
        (5407,8831,0,909,0), (5599,8927,0,909,0),
        (5503,8863,0,909,0), (5695,8831,0,909,0),
        (5439,8991,0,909,0)),
    'east court collapse': (
        (6687,5983,0,905,0), (6495,6207,0,905,0),
        (6847,6015,0,910,6), (6751,6079,0,910,7),
        (6879,6111,0,899,3), (6783,5919,0,910,8),
        (6431,6239,0,910,6), (6559,6271,0,910,6)),
    'landing watch': (
        (3807,9631,0,223,0),
        (3615,9855,0,875,0),
        (3615,10111,0,875,1),
        (3839,9855,0,909,0), (3807,10015,0,909,0),
        (3935,9727,0,909,0)),
    'north observatory ruins': (
        (5023,1855,0,875,1), (5023,2111,0,905,0),
        (5119,2143,0,910,6), (5311,1919,0,905,0),
        (5471,2015,0,910,8), (5567,1823,0,875,0),
        (5887,1951,0,909,0), (5983,2079,0,909,0),
        (6079,1919,0,909,0), (6239,2175,0,905,0),
        (6463,2303,0,875,1), (6367,2239,0,910,7),
        (6591,1951,0,905,0), (6655,2047,0,910,6)),
    'western fallen arcade': (
        (2079,1759,0,875,1), (1919,1887,0,905,0),
        (2175,2015,0,910,7), (2399,1791,0,909,0),
        (2079,4703,0,875,0), (2303,4831,0,905,0),
        (2239,4927,0,910,8), (2143,5087,0,909,0),
        (2239,5663,0,875,1), (2047,5727,0,905,0),
        (2175,5823,0,910,6), (2367,5951,0,905,0),
        (2111,6655,0,905,0), (2335,6815,0,875,0),
        (2399,6943,0,910,8), (2207,6975,0,909,0),
        (2335,7583,0,875,1), (2559,7807,0,905,0),
        (2495,7903,0,910,7), (2239,8031,0,905,0),
        (2111,8671,0,905,0), (2399,8863,0,875,0),
        (2495,8927,0,909,0), (2335,9055,0,910,6),
        (2175,9727,0,875,1), (2303,9823,0,905,0),
        (2527,10015,0,910,8), (2655,10271,0,905,0)),
    'fallen plaza approach': (
        (5503,6527,0,905,0), (5311,6591,0,905,0),
        (5407,6655,0,910,6), (5567,6655,0,875,0),
        (5535,6751,0,910,8)),
    'eastern fallen portico': (
        (6559,7871,0,875,1), (6655,8159,0,905,0),
        (6495,8255,0,910,7), (6623,8767,0,905,0),
        (6431,8863,0,909,0), (6559,9023,0,910,8)),

}

# Marble outlines, courts, and the arrival descent have explicit anchors.
MARBLE_SCENES = {
    'shrine offering crescent': (
        (2815,1151), (2943,1151), (3071,1151), (3199,1151),
        (3327,1151), (3455,1151), (3583,1151), (3711,1151),
        (3839,1151), (3967,1151), (3455,2175), (3583,2175),
        (2943,2175), (3071,2175), (3711,2175), (3839,2175),
        (3967,1279), (3967,1407), (3967,1535), (3967,1663),
        (3967,1791), (3967,1919)),
    'plaza empty council': ((5503,7807), (5631,7807), (5503,7679), (5631,7679)),
    'south street memorial': ((5503,8767), (5631,8767), (5503,8639), (5631,8639)),
    'landing watch': ((3839,10143), (3967,10143)),
    'arrival marble descent': ((5503,10111), (5631,10111),
                               (5503,10239), (5631,10239)),
}


def dress_city(items):
    from parse_typeflag import load_typeflag
    import lv_dressing
    shapes = load_typeflag(os.path.join(os.path.dirname(__file__),
                                       '../../../shared/build/TYPEFLAG.DAT'))
    site = lv_dressing.Site(17, items, shapes, seed=1704)
    # Stars stay loose before the cloud lobes and the retained scene records.
    site.beyond('stars', where=(0, 0, 16383, 16383), partial=True, north=True)
    site.swap_loose_chunks(floors={874, 876},
        family=lv_dressing.prefab_family('cloud_gold_'), share=.5,
        where=(3072, 4608, 6143, 6143))
    site.protected_raw.update(id(i) for i in site.items)
    for name, anchors in MARBLE_SCENES.items():
        site.walkable_set_piece(name, [
            MapItem.placed_item(x, y, 0, 877, 0) for x, y in anchors])
    # The complete ruined court shares its reservation with the fallen drums.
    site.reserve('east court collapse', (5632, 4864, 6912, 6272))
    site.reserve('south street memorial', (5279, 8479, 5631, 9183))
    for name, rows in SET_PIECES.items():
        site.set_piece(name, [MapItem.placed_item(*row) for row in rows])
    # Pack at most 150 complete floor chunks (chosen when the engine capped
    # FLEX archives at 4,095 entries; the fork now allows 65,536, and
    # test_dressing checks the built GLOB.FLX fits). Kept at 150 so the
    # reviewed Map 17 output does not change.
    # Overlapping land retains its FIXED order; transitions stay loose.
    from collections import defaultdict
    candidates = defaultdict(list)
    for it in site.items:
        if (it.shape not in (874, 876) or it.x % 128 != 127 or it.y % 128 != 127
                or id(it) in site.floor_order
                or lv_dressing.paints_window(it, site.sorter, site.windows)):
            continue
        bounds = lv_dressing.box(it, site.sorter)
        peers = [other for other in site._near(bounds)
                 if other is not it and other.z == it.z
                 and site.sorter.info(other.shape)['land']
                 and lv_dressing.xy_overlap(bounds, lv_dressing.box(other, site.sorter))]
        if not peers:
            candidates[it.x // 512, it.y // 512, it.z].append(it)
    complete = [(key, rows) for key, rows in sorted(candidates.items()) if len(rows) == 16]
    for _, rows in complete[:150]:
        site.protected_raw.difference_update(id(it) for it in rows)
    return site.pack()


def build_map_17():
    """Build complete Map 17 item list."""
    cells = layout()
    items = floors(cells) + cloud_sea(cells) + curbs(cells)
    items += walkways()
    items += build_scroll_court()
    items += build_processional()
    items += build_plaza_ring()
    items += build_east_court()
    items += build_arrival()
    items += build_walkway_field()
    items = window_clear(items)
    for shot in VIGNETTES:
        items = VP.stamp(items, shot, 17, art_map=ART_MAP,
                         fill=(SHAPE_CLOUD, CLOUD_FRAMES))
    items = quest_halves(items) + fill_gaps(items, cells)
    # Editor walls draw nothing, so they bypass the sprite-window filter.
    recesses = column_recesses()
    # Retained curbs close the cloud; stars repaint the remaining view rays.
    retained = items + recesses
    items = dress_city(retained + void_floor(retained))
    return items


if __name__ == '__main__':
    items = build_map_17()
    globs = sum(1 for i in items if i.is_glob_egg)
    teles = sum(1 for i in items if i.is_teleport_egg)
    mons = sum(1 for i in items if i.is_monster_egg)
    print(f"Map 17: {len(items)} items")
    print(f"  Glob eggs: {globs}")
    print(f"  Teleport eggs: {teles}")
    print(f"  Monster eggs: {mons}")
    print(f"  Other items: {len(items) - globs - teles - mons}")

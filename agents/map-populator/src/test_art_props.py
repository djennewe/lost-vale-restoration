#!/usr/bin/env python3
"""
test_art_props.py — the art track's static props, checked in the BUILT
artifacts with the engine's own box arithmetic.

WHY THIS FILE EXISTS (2026-09-15). Landing the Magnetic Obelisk (shape 861,
docs/art-track.md contract 1; retired 2026-10-17) changed three artifacts at
once — a new shape in U8SHAPES.FLX, a new TYPEFLAG entry with a footpad
twice the chimney's, and a moved, re-shaped item on Map 17 — and nothing in
the estate looked at any of it:

  - `test_route_reach.py` is FIXED.DAT-only by its own docstring; a footpad
    that grew from 64 to 128 units is invisible to it.
  - `map_walkability.py` has no Map 17 run.
  - `test_map_hygiene.py` counts placeholders; a custom shape is not one.

So this file is to lv_art_props.py what test_sanctum_clearance.py is to the
gods: it reads what ships and asserts each row's contract. The first two
sections run over every row of PROPS (the shape decodes with the right frame
count and anchor rule; the TYPEFLAG entry carries the donor's flags and the
table's footpad). The sections after them are per-prop map geometry. Map 17
since 2026-10-17 is the open 1994 city (build_map_17): the obelisk is
screen11's retail composite, the floor is the 1994 cloud 874, the Shield
halves are the 1994 art 878, and the gem pillars' caps are 880, retail 596's
frames on a fixed row. The custom art those replaced, 861 and 862, is
retired, and the last section asserts its slots stay empty and unused;
870, the old halves, is 878's legacy alias (a copy of its frames and row,
so a pre-2026-10-17 save's halves open in the pack), and is never placed.

Same instrument as test_crack_geometry / test_sanctum_clearance:
`Box::overlaps` verbatim over the BUILT FIXED.DAT with globs expanded.
"""

import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'tools'))

from u8_map import MapArchive                      # noqa: E402
sys.path.insert(0, os.path.join(BASE_DIR, 'agents', 'usecode-compiler', 'src'))
from map_preview import GlobReader, expand_globs   # noqa: E402
from parse_typeflag import load_typeflag           # noqa: E402
from shape_viewer import (read_flx_entry, parse_shape_frames,  # noqa: E402
                          load_palette, PALETTE_FILE)
from lv_art_props import (PROPS, indexed_sources,   # noqa: E402
                          load_registry, patch_sources, patch_frame, crop_copy, turn_copy, rock_skin_copy)
from png2shape import indexed_pixels               # noqa: E402
from lv_shapes import (RETIRED_SHAPE_IDS,                            # noqa: E402
                       SHAPE_SACRED_ROCK, SHAPE_ROCK_SPIRE_CLUSTER,
                       SHAPE_MESSAGE_SCROLL, SHAPE_STOOL,
                       SHAPE_ELEMENTAL_PILLAR, SHAPE_PILLAR_RECEPTACLE,
                       SHAPE_CHEST_ORNATE,
                       SHAPE_STANDING_STONE,
                       SHAPE_PLACEHOLDER_GENERIC_PILLAR, SHAPE_PLATFORM_FLAGSTONE,
                       SHAPE_ELIXIR, SHAPE_SPECIAL_ROOT, SHAPE_SHIELD_HALVES,
                       SHAPE_TALISMAN_GEM,
                       SHAPE_TEST_PLANT, SHAPE_CLOUD_1994,
                       SHAPE_WHITE_COLUMN_1994, SHAPE_GOLD_BRICK_1994,
                       SHAPE_MARBLE_WALKWAY_1994, SHAPE_SHIELD_HALVES_1994,
                       SHAPE_SACRED_SHIELD_1994, SHAPE_GEM_CAP_1994,
                       SHAPE_STRIPED_PROP_1994, SHAPE_SHIELD_HALVES_LEGACY)
from png2shape import footpad_screen_size          # noqa: E402
from PIL import Image                              # noqa: E402

BUILD = os.path.join(BASE_DIR, 'shared', 'build')
FIXED = os.path.join(BUILD, 'FIXED.DAT')
TYPEFLAG = os.path.join(BUILD, 'TYPEFLAG.DAT')
SHAPES = os.path.join(BUILD, 'U8SHAPES.FLX')

SI_FIXED = 0x01
SI_SOLID = 0x02
SI_DAMAGING = 0x40     # parse_typeflag FLAGS_BYTE0 order: fixed, solid, sea,
                       # land, occl, bag, damaging, noisy
SI_NOISY = 0x80

MAP = 17
QUALITY_OBELISK = 90
# The obelisk, screen11's 1994 composite at the vignette's world position
# (origin (1280, 4736, 0), phase C z=0 encoding): (shape, frame, x, y, z).
OBELISK_PIECES = [
    (875, 1, 4063, 7135, 0), (875, 1, 4063, 7199, 0), (875, 1, 4127, 7135, 0),
    (875, 1, 4127, 7199, 0), (12, 14, 4127, 7167, 80), (12, 15, 4095, 7199, 80),
    (12, 16, 4127, 7167, 40), (12, 17, 4095, 7199, 40), (545, 0, 4127, 7199, 120),
    (814, 0, 4127, 7199, 40)]
OBELISK_FRONT_DRUM = (4127, 7199, 0)

# The Sacred Rock (contract 3) is on map 10, so that map is loaded too.
MAP_VALE = 10
QUALITY_SACRED_ROCK = 100
SACRED_ROCK_POS = (20415, 16831, 0)
# map_walkability.MAP10_ROOT_SEED. The stone's box must clear an Avatar
# standing here, and it does so by exactly one world unit on each axis, so
# the position and the (4,4) footpad are both frozen.
ROOT_SEED = (20480, 16896, 0)
AVATAR_BODY = (64, 64, 40)
# SHADES.UNK teleports the three elders onto this span; the stone must not
# stand in it.
ELDER_SPAN = (20224, 17216, 20672, 17472)

# The Message Scroll (contract 4) on Map 17's scroll-court plinth. The
# position is frozen twice over: route 17 floods to it, and
# derive_map_pins.route_cite finds that line by grepping test_route_reach.py
# for the literal string below, so a move of one unit drops the pin row with
# no complaint.
MSG_SCROLL_POS = (3328, 1536, 8)
QUALITY_MSG_SCROLL = 80
SCROLL_PLINTH = (3327, 1535, 0)      # a marble slab, 877, footpad (4,4,1)
SCROLL_DONOR = 159                   # the game's own scroll: SI_SOLID, SF_QUALITY
LV_MAPS = (9, 10, 11, 13, 17, 18)

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


def overlaps(a, b):
    """ultima8/misc/box.h Box::overlaps, verbatim. Half-open boxes (x-xd, x];
    every comparison is <=, so an exact fit is a MISS."""
    ax, ay, az, axd, ayd, azd = a
    bx, by, bz, bxd, byd, bzd = b
    if ax <= bx - bxd or bx <= ax - axd:
        return False
    if ay <= by - byd or by <= ay - ayd:
        return False
    if az + azd <= bz or bz + bzd <= az:
        return False
    return True


print('=' * 70)
print('Art-track static props, as built')

for p in (FIXED, TYPEFLAG, SHAPES):
    if not os.path.exists(p):
        print(f'  {p} absent — run tools/build_artifacts.sh')
        sys.exit(1)

shapes = load_typeflag(TYPEFLAG)
flx = open(SHAPES, 'rb').read()
REG = load_registry()
items = expand_globs(MapArchive(FIXED).get_map_items(MAP), GlobReader())

# ── 1. Every row: the shape is in the FLX and follows its anchor rule ────
print('\n-- 1. U8SHAPES.FLX, every PROPS row --')
for prop in PROPS:
    sid, name = prop['shape'], prop['name']
    data = read_flx_entry(flx, sid)
    check(f'{name}: shape {sid} has data', data is not None)
    frames = parse_shape_frames(data) if data else []
    nframes = (len(prop['frames']) if 'frames' in prop
               else len(prop['indexed']) if 'indexed' in prop
               else prop['copy'][1] + len(prop.get('copy_clips', ())) if 'copy' in prop
               else len(patch_sources(prop, REG)) if 'patch' in prop
               else 1)
    check(f'{name}: {nframes} frame(s)',
          len(frames) == nframes, f'got {len(frames)}')
    if not frames:
        continue
    f = frames[0]
    check(f'{name}: frame 0 has opaque pixels',
          any(px != 255 for px in f['pixels']))
    if 'indexed' in prop:
        want = indexed_sources(prop, REG)[0]['anchor']
        check(f'{name}: frame 0 anchored at its registry hotspot + shift '
              f'{want}', (f['xoff'], f['yoff']) == tuple(want),
              f"got {f['xoff']},{f['yoff']}")
    elif 'recolour' in prop:
        rs, rf, _remap = prop['recolour']
        d = parse_shape_frames(read_flx_entry(flx, rs))[rf]
        check(f'{name}: frame 0 keeps base {rs} frame {rf}\'s size and anchor '
              f'({d["width"]}x{d["height"]} @ {d["xoff"]},{d["yoff"]})',
              (f['width'], f['height'], f['xoff'], f['yoff']) ==
              (d['width'], d['height'], d['xoff'], d['yoff']),
              f"got {f['width']}x{f['height']} @ {f['xoff']},{f['yoff']}")
    elif 'patch' in prop:
        # each frame is its registry patch over its retail base, rebuilt
        # here with the builder's own composer (the retail base frames are
        # the same in the built FLX)
        _bad = []
        for _n, (_g, _src) in enumerate(zip(frames, patch_sources(prop, REG))):
            _b = parse_shape_frames(read_flx_entry(flx, _src['base'][0]))
            _px, _w, _h, _ = indexed_pixels(os.path.join(BASE_DIR, _src['png']),
                                            load_palette(PALETTE_FILE))
            _want = patch_frame(_b[_src['base'][1]], _px, _w, _h,
                                _src['hotspot'])
            if (_g['pixels'], _g['width'], _g['height'], _g['xoff'],
                    _g['yoff']) != _want:
                _bad.append(_n)
        check(f'{name}: every frame is its registry patch over its retail '
              f'base frame', not _bad, f'frames {_bad}')
    elif 'copy' in prop:
        cs, cn = prop['copy']
        all_src = parse_shape_frames(read_flx_entry(flx, cs))
        src = [dict(all_src[i]) for i in prop.get('copy_frames', range(cn))]
        if prop.get('copy_turn'):
            src = [turn_copy(f) for f in src]
        if 'copy_texture' in prop:
            ts,tf = prop['copy_texture']
            texture = parse_shape_frames(read_flx_entry(flx,ts))[tf]
            src = [rock_skin_copy(f,texture) for f in src]
        for n, source in enumerate(src):
            if 'copy_crops' in prop:
                source['pixels'] = crop_copy(source, prop['copy_crops'][n])
        for source, (dx, dy) in zip(src, prop.get('copy_shifts', ((0, 0),) * cn)):
            source['xoff'] += dx
            source['yoff'] += dy
        check(f'{name}: copied frames retain base {cs} pixels and declared anchors', [(g['width'], g['height'], g['xoff'], g['yoff'],
                             g['pixels']) for g in frames[:cn]] ==
              [(g['width'], g['height'], g['xoff'], g['yoff'], g['pixels'])
               for g in src])
        for clip_index, clip in enumerate(prop.get('copy_clips', ()), cn):
            clipped, original = frames[clip_index], all_src[clip['frame']]
            check(f'{name}: clipped frame {clip_index} keeps source geometry',
                  all(clipped[k] == original[k]
                      for k in ('width', 'height', 'xoff', 'yoff')))
            check(f'{name}: clipped frame {clip_index} only removes pixels',
                  any(px != 255 for px in clipped['pixels'])
                  and any(px == 255 and old != 255
                          for px, old in zip(clipped['pixels'], original['pixels']))
                  and all(px == 255 or px == old
                          for px, old in zip(clipped['pixels'], original['pixels'])))
    elif isinstance(prop['frames'][0], dict):
        # a 1994 frame inside a drawn row (865 since 2026-10-30, all four)
        want = indexed_sources({**prop, 'indexed': [prop['frames'][0]['indexed']]},
                               REG)[0]['anchor']
        check(f'{name}: frame 0 anchored at its registry hotspot {want}',
              (f['xoff'], f['yoff']) == tuple(want),
              f"got {f['xoff']},{f['yoff']}")
    else:
        check(f'{name}: frame 0 is anchored bottom-centre (xoff=w/2, yoff=h)',
              f['xoff'] == f['width'] // 2 and f['yoff'] == f['height'],
              f"{f['width']}x{f['height']} @ {f['xoff']},{f['yoff']}")
    bw, bh = footpad_screen_size(*prop['footpad'])
    if prop.get('oversize'):
        # the overhang may be any frame's: 865's is frame 2 (the 1994
        # Pillar of Fire), 886's the frames whose lobes spill past the cell
        _big = max(frames, key=lambda g: max(g['width'] / bw, g['height'] / bh))
        check(f'{name}: a frame ({_big["width"]}x{_big["height"]}) is over '
              f'the footpad\'s screen box ({bw}x{bh}) by design: '
              f'{prop["oversize"]}',
              _big['width'] > bw * 1.25 or _big['height'] > bh * 1.25)
    else:
        check(f'{name}: frame 0 ({f["width"]}x{f["height"]}) fits the '
              f'footpad\'s screen box ({bw}x{bh}) within png2shape\'s 1.25 '
              f'slack', f['width'] <= bw * 1.25 and f['height'] <= bh * 1.25)

# ── 2. Every row: TYPEFLAG carries the donor's flags, the table's footpad ─
print('\n-- 2. TYPEFLAG.DAT, every PROPS row --')
for prop in PROPS:
    sid, name = prop['shape'], prop['name']
    si = shapes[sid]
    donor = shapes[prop['donor']]
    # SI_FIXED follows the donor. Every prop was fixed scenery until the
    # Message Scroll (contract 4), which takes donor 159 precisely so the
    # Avatar can pick it up, so this check asserts the donor's flag.
    check(f'{name}: SI_FIXED matches donor {prop["donor"]} '
          f'({"fixed scenery" if donor.flags0 & SI_FIXED else "carryable"})',
          bool(si.flags0 & SI_FIXED) == bool(donor.flags0 & SI_FIXED))
    # Decorative backdrops inherit donor 202's absence of collision.
    check(f'{name}: SI_SOLID matches donor {prop["donor"]}',
          bool(si.flags0 & SI_SOLID) == bool(donor.flags0 & SI_SOLID))
    check(f'{name}: not SI_DAMAGING (the fire-field mistake, never again)',
          not (si.flags0 & SI_DAMAGING))
    check(f'{name}: footpad is the table\'s {prop["footpad"]}',
          (si.footpad_x, si.footpad_y, si.footpad_z) == tuple(prop['footpad']),
          f'got {(si.footpad_x, si.footpad_y, si.footpad_z)}')
    check(f'{name}: flags byte 0 otherwise equal the donor {prop["donor"]}\'s',
          (si.flags0 & ~(SI_FIXED | SI_SOLID)) ==
          (donor.flags0 & ~(SI_FIXED | SI_SOLID)))

# ── 3. The obelisk: screen11's retail composite ─────────────────────────
print('\n-- 3. FIXED.DAT map 17: the obelisk --')
check('no 721 chimney on Map 17',
      not any(i.shape == SHAPE_PLACEHOLDER_GENERIC_PILLAR for i in items))
_have = {(i.shape, i.frame, i.x, i.y, i.z) for i in items}
_miss = [p for p in OBELISK_PIECES if p not in _have]
check(f'the {len(OBELISK_PIECES)} pieces of screen11\'s obelisk stand at the '
      f'shot\'s positions (12 f14-f17, 545, 814 on four 875 f1 drums)',
      not _miss, f'missing {_miss}')
_drum = [i for i in items if (i.shape, i.frame, i.x, i.y, i.z) ==
         (SHAPE_WHITE_COLUMN_1994, 1, *OBELISK_FRONT_DRUM)]
check(f'the front drum carries quality {QUALITY_OBELISK} for the future '
      f'MAGNET wiring, and only it does',
      len(_drum) == 1 and _drum[0].quality == QUALITY_OBELISK and
      sum(1 for i in items if i.quality == QUALITY_OBELISK) == 1,
      str([(i.shape, i.x, i.y, i.quality) for i in items
           if i.quality == QUALITY_OBELISK]))

# ── 4. The floor: the 1994 cloud everywhere ─────────────────────────────
print('\n-- 4. FIXED.DAT map 17: the cloud floor --')
cloud = [i for i in items if i.shape == SHAPE_CLOUD_1994]
check('the 1994 cloud (874) floors Map 17 (over a thousand tiles)',
      len(cloud) > 1000, f'got {len(cloud)}')
check('no flagstone platform (113) is left on Map 17',
      not any(i.shape == SHAPE_PLATFORM_FLAGSTONE for i in items))
check('every cloud and gold tile lies at z 0 (phase C\'s z=0 encoding)',
      all(i.z == 0 for i in items
          if i.shape in (SHAPE_CLOUD_1994, SHAPE_GOLD_BRICK_1994)),
      str(sorted({i.z for i in items
                  if i.shape in (SHAPE_CLOUD_1994, SHAPE_GOLD_BRICK_1994)})))
check('every cloud and gold tile is on the floor grid (x, y ≡ 127 mod 128)',
      all(i.x % 128 == 127 and i.y % 128 == 127 for i in items
          if i.shape in (SHAPE_CLOUD_1994, SHAPE_GOLD_BRICK_1994)))
check('no walkway slab is stacked on another (every 877 at z 0)',
      all(i.z == 0 for i in items if i.shape == SHAPE_MARBLE_WALKWAY_1994))

# ── 5. The Sacred Rock: the ninth stone, and the seed cell it must miss ─
print('\n-- 5. FIXED.DAT map 10: the Sacred Rock --')
vale = expand_globs(MapArchive(FIXED).get_map_items(MAP_VALE), GlobReader())
prop = next(p for p in PROPS if p['shape'] == SHAPE_SACRED_ROCK)
rocks = [i for i in vale if i.shape == SHAPE_SACRED_ROCK]
check('exactly one Sacred Rock on Map 10', len(rocks) == 1, f'got {len(rocks)}')
check('no shape-66 item on Map 10 carries quality 100 any more '
      '(the placeholder is gone, not doubled)',
      not any(i.shape == SHAPE_ROCK_SPIRE_CLUSTER and i.quality == 100
              for i in vale))
check('shape 66 still stands on Map 10 as ambient rubble, so the swap did '
      'not disturb TypeSealingBoulder',
      sum(1 for i in vale if i.shape == SHAPE_ROCK_SPIRE_CLUSTER) > 0)
# Shape 38 frames 2-3 are the plain monoliths; frames 0-1 are gargoyle
# busts, which the 1994 shots place on Map 10 (screen18 one, screen17 two:
# vignettes, 2026-10-16), so only the monolith frames are the ring's.
_ring = [i for i in vale if i.shape == SHAPE_STANDING_STONE and i.frame in (2, 3)]
check('the eight ring monoliths are untouched', len(_ring) == 8, str(len(_ring)))
si = shapes[SHAPE_SACRED_ROCK]
check('Sacred Rock TYPEFLAG footpad is the row\'s (4,4,8)',
      (si.footpad_x, si.footpad_y, si.footpad_z) == prop['footpad'],
      f'{(si.footpad_x, si.footpad_y, si.footpad_z)}')
# The rescale targets 96 and the trim to the opaque bounding box may take
# a row back, so 95 or 96; either is half again the ring stones' 59.
_rh = parse_shape_frames(read_flx_entry(flx, SHAPE_SACRED_ROCK))[0]['height']
_ringh = parse_shape_frames(read_flx_entry(flx, SHAPE_STANDING_STONE))[2]['height']
check(f'Sacred Rock sprite is 96 px tall (95 after the trim), against the '
      f'ring stones\' {_ringh}', _rh in (95, 96), f'{_rh} px')
check('and it stands at least half again the ring stones\' height',
      _rh >= _ringh * 3 // 2, f'{_rh} vs {_ringh}')
if len(rocks) == 1:
    r = rocks[0]
    fx, fy, fz = prop['footpad']
    check(f'Sacred Rock at {SACRED_ROCK_POS}, the frozen position',
          (r.x, r.y, r.z) == SACRED_ROCK_POS, f'{(r.x, r.y, r.z)}')
    check(f'quality {QUALITY_SACRED_ROCK} kept for a future wiring',
          r.quality == QUALITY_SACRED_ROCK, f'quality={r.quality}')
    box = (r.x, r.y, r.z, fx * 32, fy * 32, fz * 8)
    seed = (ROOT_SEED[0], ROOT_SEED[1], ROOT_SEED[2]) + AVATAR_BODY
    check('Sacred Rock box clears an Avatar on MAP10_ROOT_SEED '
          f'{ROOT_SEED[:2]}', not overlaps(box, seed),
          f'box x {r.x - fx * 32}..{r.x}, y {r.y - fy * 32}..{r.y}')
    # Box::contains is px > x - xd && px <= x, so an Avatar on the seed
    # occupies 20417..20480 and the stone's box ends at 20415: one free
    # world unit, 20416, lies between them on each axis.
    free_x = (ROOT_SEED[0] - AVATAR_BODY[0] + 1) - r.x - 1
    free_y = (ROOT_SEED[1] - AVATAR_BODY[1] + 1) - r.y - 1
    check('exactly one free world unit separates them on each axis, so '
          'neither the position nor the (4,4) footpad may move',
          (free_x, free_y) == (1, 1), f'free x {free_x}, y {free_y}')
    x0, y0, x1, y1 = ELDER_SPAN
    check('Sacred Rock stands clear of the span SHADES teleports the '
          'elders onto',
          r.x - fx * 32 > x1 or r.x < x0 or r.y - fy * 32 > y1 or r.y < y0,
          f'box x {r.x - fx * 32}..{r.x}, y {r.y - fy * 32}..{r.y}')

# ── 6. The Message Scroll: carryable, on its plinth, and the stool gone ─
print('\n-- 6. FIXED.DAT map 17: the Message Scroll --')
prop = next(p for p in PROPS if p['shape'] == SHAPE_MESSAGE_SCROLL)
scrolls = [i for i in items if i.shape == SHAPE_MESSAGE_SCROLL]
check('exactly one Message Scroll on Map 17', len(scrolls) == 1,
      f'got {len(scrolls)}')
stools = {m: sum(1 for i in expand_globs(MapArchive(FIXED).get_map_items(m),
                                         GlobReader())
                 if i.shape == SHAPE_STOOL) for m in LV_MAPS}
check('shape 158, the stool, is gone from every LV map '
      '(test_map_hygiene counts it as a placeholder)',
      sum(stools.values()) == 0, str(stools))
si, d = shapes[SHAPE_MESSAGE_SCROLL], shapes[SCROLL_DONOR]
check(f'Message Scroll TYPEFLAG flags and footpad equal {SCROLL_DONOR}\'s '
      f'exactly',
      (si.flags0, si.family, si.footpad_x, si.footpad_y, si.footpad_z) ==
      (d.flags0, d.family, d.footpad_x, d.footpad_y, d.footpad_z),
      f'{(si.flags0, si.family, si.footpad_x, si.footpad_y, si.footpad_z)} '
      f'vs {(d.flags0, d.family, d.footpad_x, d.footpad_y, d.footpad_z)}')
check('it is NOT SI_FIXED, so the Avatar can pick it up and carry it to '
      'Ezrekal (Plot v1.2 beat 14)', not si.flags0 & SI_FIXED,
      f'flags0={si.flags0:#04x}')
check('its family is SF_QUALITY (1), the one family Item::I_getQuality '
      'answers for, so quality 80 is readable', si.family == 1,
      f'family={si.family}')
_sf = parse_shape_frames(read_flx_entry(flx, SHAPE_MESSAGE_SCROLL))[0]
_bw, _bh = footpad_screen_size(*prop['footpad'])
check(f'the {_sf["width"]}x{_sf["height"]} sprite fits the footpad\'s '
      f'{_bw}x{_bh} screen box', _sf['width'] <= _bw and _sf['height'] <= _bh)
_base = parse_shape_frames(read_flx_entry(flx, SCROLL_DONOR))[0]
check(f'and it is larger than the base game\'s scroll '
      f'({_base["width"]}x{_base["height"]}), so it reads as the chamber\'s '
      f'object', _sf['width'] * _sf['height'] > _base['width'] * _base['height'])
if len(scrolls) == 1:
    r = scrolls[0]
    fx, fy, fz = prop['footpad']
    check(f'Message Scroll at {MSG_SCROLL_POS}, the frozen position',
          (r.x, r.y, r.z) == MSG_SCROLL_POS, f'{(r.x, r.y, r.z)}')
    check(f'quality {QUALITY_MSG_SCROLL} kept', r.quality == QUALITY_MSG_SCROLL,
          f'quality={r.quality}')
    plinths = [i for i in items
               if i.shape == SHAPE_MARBLE_WALKWAY_1994
               and (i.x, i.y, i.z) == SCROLL_PLINTH]
    check(f'the marble plinth (877) is at {SCROLL_PLINTH}, its top at '
          f'z=8 under the scroll', len(plinths) == 1, f'got {len(plinths)}')
    if plinths:
        pl = plinths[0]
        pbox = (pl.x, pl.y, pl.z, 4 * 32, 4 * 32, 1 * 8)
        sbox = (r.x, r.y, r.z, fx * 32, fy * 32, fz * 8)
        check('scroll box stacks on top of the plinth box, clear of it',
              not overlaps(sbox, pbox))
        check('and its footprint lies over the plinth tile',
              r.x - fx * 32 >= pl.x - 4 * 32 and r.y - fy * 32 >= pl.y - 4 * 32,
              f'scroll x {r.x - fx * 32}..{r.x}, plinth x {pl.x - 128}..{pl.x}')
    goal = open(os.path.join(SRC_DIR, 'test_route_reach.py')).read()
    check('route 17 still names the literal "%d, %d," that '
          'derive_map_pins.route_cite greps for' % (r.x, r.y),
          f'{r.x}, {r.y},' in goal)

# ── 7. The elemental pillars: four frames, four items, and the re-point ─
print('\n-- 7. FIXED.DAT map 11: the elemental pillars --')
from u8c_symbols import TYPE_SHAPES                  # noqa: E402
from build_map_11 import RECEPTACLE_NPCNUM, FIRE_RECEPTACLE  # noqa: E402
items11 = expand_globs(MapArchive(FIXED).get_map_items(11), GlobReader())
prop = next(p for p in PROPS if p['shape'] == SHAPE_ELEMENTAL_PILLAR)
check('TYPE_SHAPES[TypeElementalColumn] is SHAPE_ELEMENTAL_PILLAR: the number '
      'COLPUZZL.UNK:139 compiles into the search that destroys a pillar is '
      'the number on the map',
      TYPE_SHAPES['TypeElementalColumn'] == SHAPE_ELEMENTAL_PILLAR,
      f"{TYPE_SHAPES['TypeElementalColumn']} vs {SHAPE_ELEMENTAL_PILLAR}")
pillars = sorted((i for i in items11 if i.shape == SHAPE_ELEMENTAL_PILLAR),
                 key=lambda i: i.quality)
check('exactly four pillars on Map 11', len(pillars) == 4, f'got {len(pillars)}')
# frame = element = quality - 201, in the map's order (build_map_11.py)
EXPECTED = {201: (0, 7680, 20480), 202: (1, 8704, 20480),
            203: (2, 7680, 21504), 204: (3, 8704, 21504)}
for q, (fr, x, y) in EXPECTED.items():
    hit = [i for i in pillars if i.quality == q]
    check(f'pillar q{q} is frame {fr} at ({x}, {y}, 0), unchanged from the chimney',
          len(hit) == 1 and (hit[0].frame, hit[0].x, hit[0].y, hit[0].z)
          == (fr, x, y, 0),
          f'{[(i.frame, i.x, i.y, i.z) for i in hit]}')
chimneys = {m: sum(1 for i in expand_globs(MapArchive(FIXED).get_map_items(m),
                                           GlobReader())
                   if i.shape == SHAPE_PLACEHOLDER_GENERIC_PILLAR)
            for m in LV_MAPS}
check('shape 721, the chimney, is gone from every LV map',
      sum(chimneys.values()) == 0, str(chimneys))
si, d = shapes[SHAPE_ELEMENTAL_PILLAR], shapes[38]
check('pillar TYPEFLAG flags and family equal donor 38\'s (the ring stone), '
      'not the chimney\'s SI_NOISY',
      (si.flags0, si.family) == (d.flags0, d.family) and not si.flags0 & SI_NOISY,
      f'{(si.flags0, si.family)} vs {(d.flags0, d.family)}')
check('pillar footpad is the row\'s (2,2,10): 80 units of collision',
      (si.footpad_x, si.footpad_y, si.footpad_z) == prop['footpad'] == (2, 2, 10),
      f'{(si.footpad_x, si.footpad_y, si.footpad_z)}')
_pf = parse_shape_frames(read_flx_entry(flx, SHAPE_ELEMENTAL_PILLAR))
_bw, _bh = footpad_screen_size(*prop['footpad'])
_f2 = _pf[2]
for k, f in enumerate(_pf):
    # the 1994 Pillar of Fire (registry 2023, 2026-10-25) and, since
    # 2026-10-30, its column redrawn for the other three (2024-2026): the
    # flames and foot pool spread past the box; the column stands 90+ px.
    # All four share frame 2's canvas and anchor, so they stand alike.
    check(f'pillar frame {k} ({f["width"]}x{f["height"]}) is at least 90 px '
          f'tall, over the box by design, on frame 2\'s canvas and anchor',
          f['height'] >= 90 and f['width'] > _bw and bool(prop.get('oversize'))
          and (f['width'], f['height'], f['xoff'], f['yoff']) ==
          (_f2['width'], _f2['height'], _f2['xoff'], _f2['yoff']))
_ring = parse_shape_frames(read_flx_entry(flx, 38))[2]
check(f'a pillar overtops the ring stone ({_ring["height"]} px) by half again',
      all(f['height'] >= _ring['height'] * 1.5 for f in _pf))
# the receptacle's search box must hold its own pillar's origin and no other:
# CurrentMap::areaSearch grows the SEARCHER's footpad by the range and matches
# candidates on their origin (contract 5, "the range math")
rprop = next(p for p in PROPS if p['shape'] == SHAPE_PILLAR_RECEPTACLE)
rfx, rfy, _ = rprop['footpad']
recs = [i for i in items11 if i.shape == SHAPE_PILLAR_RECEPTACLE]
for r in recs:
    inside = [p for p in pillars
              if r.x - 32 * rfx - 300 <= p.x <= r.x + 300
              and r.y - 32 * rfy - 300 <= p.y <= r.y + 300]
    check(f'receptacle q{r.quality}\'s "within 300" box holds exactly its own '
          f'pillar', len(inside) == 1 and inside[0].quality == r.quality,
          f'{[p.quality for p in inside]}')

# ── 8. The receptacles: one frame, npcnum dispatch, and the chest gone ──
print('\n-- 8. FIXED.DAT map 11: the receptacles --')
check('exactly four receptacles on Map 11', len(recs) == 4, f'got {len(recs)}')
check(f'every receptacle carries npcnum {RECEPTACLE_NPCNUM}, which is the whole '
      f'dispatch (class 1144 off the engine patch; the shape is cosmetic)',
      all(r.npcnum == RECEPTACLE_NPCNUM for r in recs),
      f'{[r.npcnum for r in recs]}')
# Earth, Air and Water stand 256 south of their pillars; Fire moved off the
# 1994 screen07 frame on 2026-10-17 (build_map_11.FIRE_RECEPTACLE, 255 east
# and 255 south). The "within 300" check above is what the puzzle needs.
check('each receptacle stands 256 units south of its pillar, the Fire one '
      'at FIRE_RECEPTACLE, south-east of its pillar and off the screen07 frame',
      all(any(p.quality == r.quality and
              ((r.x, r.y) == FIRE_RECEPTACLE if r.quality == 203
               else (p.x, p.y + 256) == (r.x, r.y))
              for p in pillars) for r in recs),
      f'{[(r.quality, r.x, r.y) for r in recs]}')
check('shape 307, the chest, is gone from Map 11 and stays on Map 10 as '
      'SHAPE_CRATE (five house chests, an honest use)',
      not any(i.shape == SHAPE_CHEST_ORNATE for i in items11)
      and sum(1 for i in expand_globs(MapArchive(FIXED).get_map_items(10),
                                      GlobReader())
              if i.shape == SHAPE_CHEST_ORNATE) == 5)
si, d = shapes[SHAPE_PILLAR_RECEPTACLE], shapes[443]
check('receptacle TYPEFLAG flags, family and footpad equal donor 443\'s exactly '
      '(SF_GENERIC: it stops claiming to be a container)',
      (si.flags0, si.family, si.footpad_x, si.footpad_y, si.footpad_z) ==
      (d.flags0, d.family, d.footpad_x, d.footpad_y, d.footpad_z),
      f'{(si.flags0, si.family, si.footpad_x, si.footpad_y, si.footpad_z)}')
_rf = parse_shape_frames(read_flx_entry(flx, SHAPE_PILLAR_RECEPTACLE))
_bw, _bh = footpad_screen_size(*rprop['footpad'])
check(f'receptacle is one frame of {_rf[0]["width"]}x{_rf[0]["height"]} inside '
      f'the {_bw}x{_bh} box',
      len(_rf) == 1 and _rf[0]['width'] <= _bw and _rf[0]['height'] <= _bh)
for r in recs:
    p = next(p for p in pillars if p.quality == r.quality)
    rbox = (r.x, r.y, r.z, rfx * 32, rfy * 32, rprop['footpad'][2] * 8)
    pbox = (p.x, p.y, p.z, 2 * 32, 2 * 32, 10 * 8)
    check(f'receptacle q{r.quality} box and its pillar box do not overlap',
          not overlaps(rbox, pbox))

# ── 9. Tyorvi's elixir: its own vial, not a reagent, and a class that names it
print('\n-- 9. Tyorvi\'s elixir (868): recolour, TYPEFLAG, class --')
import json                                          # noqa: E402
from u8_flex import UsecodeFlexArchive               # noqa: E402
SF_QUANTITY, SF_REAGENT = 2, 9
BLOOD, POTION = 395, 766
prop = next(p for p in PROPS if p['shape'] == SHAPE_ELIXIR)
check('TYPE_SHAPES[TypeBottle] is SHAPE_ELIXIR: the number EZREKAL creates '
      'and TYORVI\'s two drink filters destroy is this shape',
      TYPE_SHAPES['TypeBottle'] == SHAPE_ELIXIR,
      f"{TYPE_SHAPES['TypeBottle']} vs {SHAPE_ELIXIR}")
si, d = shapes[SHAPE_ELIXIR], shapes[prop['donor']]
check(f'elixir TYPEFLAG equals donor {prop["donor"]}\'s (the engine\'s bottle) '
      f'in flags, family, footpad, weight and volume',
      (si.flags0, si.flags1, si.family, si.footpad_x, si.footpad_y,
       si.footpad_z, si.weight, si.volume) ==
      (d.flags0, d.flags1, d.family, d.footpad_x, d.footpad_y,
       d.footpad_z, d.weight, d.volume))
check('elixir is carryable (not SI_FIXED)', not si.flags0 & SI_FIXED,
      f'flags0={si.flags0:#04x}')
check('elixir family is neither SF_QUANTITY nor SF_REAGENT, so '
      'Item::canMergeWith never stacks it (and it is no blood)',
      si.family not in (SF_QUANTITY, SF_REAGENT), f'family={si.family}')
check(f'and its footprint and weight are the blood vial {BLOOD}\'s',
      (si.footpad_x, si.footpad_y, si.footpad_z, si.weight) ==
      (shapes[BLOOD].footpad_x, shapes[BLOOD].footpad_y,
       shapes[BLOOD].footpad_z, shapes[BLOOD].weight))
_rs, _rf, _remap = prop['recolour']
_edata = read_flx_entry(flx, SHAPE_ELIXIR)
_ef = parse_shape_frames(_edata)[0] if _edata else {'pixels': []}
_vf = parse_shape_frames(read_flx_entry(flx, _rs))[_rf]
check(f'elixir pixels are base {_rs} frame {_rf}\'s with only the liquid '
      f'remapped (glass, cork, outline and mask untouched)',
      _ef['pixels'] == [_remap.get(px, px) for px in _vf['pixels']])
check(f'no red liquid tone ({sorted(_remap)}) survives in the elixir',
      not set(_ef['pixels']) & set(_remap))
_others = {px for s in (BLOOD, POTION)
           for f in parse_shape_frames(read_flx_entry(flx, s))
           for px in f['pixels']}
check(f'its liquid colours ({sorted(set(_remap.values()))}) appear in no '
      f'frame of the vial {BLOOD} or the potion {POTION}',
      not set(_remap.values()) & _others)
_placed = {m: sum(1 for i in expand_globs(MapArchive(FIXED).get_map_items(m),
                                          GlobReader())
                  if i.shape == SHAPE_ELIXIR) for m in LV_MAPS}
check('the elixir is placed on no LV map (EZREKAL creates it at runtime)',
      sum(_placed.values()) == 0, str(_placed))
_man = json.load(open(os.path.join(BUILD, 'lv_manifest.json')))
check('TYPEELIXIR is pinned to the shape number (the engine dispatches look() '
      'to class = shape, item.cpp:1516)',
      _man['classes'].get('TYPEELIXIR') == SHAPE_ELIXIR,
      str(_man['classes'].get('TYPEELIXIR')))
_cls = UsecodeFlexArchive(os.path.join(BUILD, 'EUSECODE.FLX')).get_class_data(
    SHAPE_ELIXIR)
check(f'EUSECODE class {SHAPE_ELIXIR} is compiled and its look() barks '
      f'"Tyorvi\'s elixir"', bool(_cls) and b"Tyorvi's elixir" in _cls)


def same_row(a, b):
    return ((a.flags0, a.flags1, a.family, a.equiptype, a.weight, a.volume)
            == (b.flags0, b.flags1, b.family, b.equiptype, b.weight, b.volume))


def placed(shape, mapnum):
    return [i for i in expand_globs(MapArchive(FIXED).get_map_items(mapnum),
                                    GlobReader()) if i.shape == shape]


def barks(shape, text):
    cls = UsecodeFlexArchive(os.path.join(BUILD, 'EUSECODE.FLX')
                             ).get_class_data(shape)
    return bool(cls) and text.encode() in cls


# ── 10. The Shield halves: the 1994 art (878), quest items, not wearable ─
print('\n-- 10. Shield halves (878) --')
check('TYPE_SHAPES[TypeAOFrizbee] is SHAPE_SHIELD_HALVES (SHADES.UNK:138 '
      'finds the halves by it), the 1994 art 878, no longer 870 or 539',
      TYPE_SHAPES['TypeAOFrizbee'] == SHAPE_SHIELD_HALVES ==
      SHAPE_SHIELD_HALVES_1994, str(TYPE_SHAPES['TypeAOFrizbee']))
_hf = parse_shape_frames(read_flx_entry(flx, SHAPE_SHIELD_HALVES))
check('878 has exactly two frames (SHADES reads 0 and 1; its frame-4 '
      'anchor relies on a missing frame)', len(_hf) == 2, str(len(_hf)))
si, d = shapes[SHAPE_SHIELD_HALVES], shapes[828]
check('halves TYPEFLAG is donor 828\'s row (flags, family, equip, weight)',
      same_row(si, d))
check('halves are carryable and NOT an equip-slot item (the paperdoll draws '
      'frame + 1)', not si.flags0 & SI_FIXED and si.equiptype == 0,
      f'flags0={si.flags0:#04x} equip={si.equiptype}')
_halves = placed(SHAPE_SHIELD_HALVES, 17)
check('Map 17 places half 1 frame 0 q81 (screen11, by the obelisk) and half '
      '2 frame 1 q82 (screen12, the throne nook), npcnum 236',
      sorted((i.frame, i.quality, i.npcnum, i.x, i.y, i.z) for i in _halves) ==
      [(0, 81, 236, 4259, 7199, 0), (1, 82, 236, 3559, 3311, 0)],
      str([(i.frame, i.quality, i.npcnum, i.x, i.y, i.z) for i in _halves]))
check('no 539 on any LV map', not any(placed(539, m) for m in LV_MAPS))

# ── 10b. The gem pillar cap (880): 596's look, never a talisman ──────────
print('\n-- 10b. Gem pillar cap (880): fixed copy of 596 --')
si = shapes[SHAPE_GEM_CAP_1994]
check('880 is SI_FIXED (cannot be picked up) and 596 is not (TypeTalisman)',
      si.flags0 & SI_FIXED and not shapes[SHAPE_TALISMAN_GEM].flags0 & SI_FIXED)
check('880 has 596\'s footpad', (si.footpad_x, si.footpad_y, si.footpad_z) ==
      (shapes[SHAPE_TALISMAN_GEM].footpad_x, shapes[SHAPE_TALISMAN_GEM].footpad_y,
       shapes[SHAPE_TALISMAN_GEM].footpad_z))
check('Map 17 places no 596 (a talisman taken off a pillar would open a '
      'Map 11 receptacle)', not placed(SHAPE_TALISMAN_GEM, 17))
_caps = placed(SHAPE_GEM_CAP_1994, 17)
_cols = {(i.x, i.y, i.z + 40) for i in placed(SHAPE_WHITE_COLUMN_1994, 17)
         if i.frame == 0}
check('Map 17 caps its gem pillars with 880, every cap on a plain white '
      'column\'s top', _caps and all((i.x, i.y, i.z) in _cols for i in _caps),
      str([(i.x, i.y, i.z) for i in _caps if (i.x, i.y, i.z) not in _cols]))

# ── 10c. The striped prop (881): screen04's, on Felicitar's plinth ───────
print('\n-- 10c. Striped prop (881): fixed, on Felicitar\'s plinth --')
si = shapes[SHAPE_STRIPED_PROP_1994]
check('881 is SI_FIXED (scenery, cannot be picked up)', si.flags0 & SI_FIXED)
check('Map 18 places exactly one 881, at screen04\'s spot on Felicitar\'s '
      'plinth (2815,8031,16)',
      [(i.x, i.y, i.z) for i in placed(SHAPE_STRIPED_PROP_1994, 18)] ==
      [(2815, 8031, 16)],
      str([(i.x, i.y, i.z) for i in placed(SHAPE_STRIPED_PROP_1994, 18)]))
check('Map 18 places no Shield on the altar (879 arrives with the ceremony, '
      'AOSCENE shield.pop)', not placed(SHAPE_SACRED_SHIELD_1994, 18))

# ── 11. The special root: its own shape, frame 0, a class that names it ─
print('\n-- 11. Special root (869): TYPEFLAG, placement, class --')
prop = next(p for p in PROPS if p['shape'] == SHAPE_SPECIAL_ROOT)
check('TYPE_SHAPES[TypeWeedz] is SHAPE_SPECIAL_ROOT (Ezrekal\'s two '
      'filters, frame 0)', TYPE_SHAPES['TypeWeedz'] == SHAPE_SPECIAL_ROOT,
      str(TYPE_SHAPES['TypeWeedz']))
si = shapes[SHAPE_SPECIAL_ROOT]
check('root TYPEFLAG is donor 180\'s row: carryable, SF_GENERIC, not '
      'SI_NOISY or translucent like 399', same_row(si, shapes[180])
      and not si.flags0 & (SI_FIXED | SI_NOISY))
_roots = placed(SHAPE_SPECIAL_ROOT, MAP_VALE)
check('Map 10 places one root, frame 0, at (21376, 16640, 0)',
      [(i.frame, i.x, i.y, i.z) for i in _roots] == [(0, 21376, 16640, 0)],
      str([(i.frame, i.x, i.y, i.z) for i in _roots]))
check('no 399 left on Map 10', not placed(399, MAP_VALE))
check('TYPESPECIALROOT is pinned to the shape number',
      _man['classes'].get('TYPESPECIALROOT') == SHAPE_SPECIAL_ROOT,
      str(_man['classes'].get('TYPESPECIALROOT')))
check('EUSECODE class 869 barks "special root"',
      barks(SHAPE_SPECIAL_ROOT, 'special root'))

# ── 12. The Passage Test plant: solid, fixed, re-pointed, 126 gone ──────
print('\n-- 12. Passage Test plant (871): TYPEFLAG, placement, class --')
check('TYPE_SHAPES[TypeShortmushroom] and [TypePoisonPlant] are '
      'SHAPE_TEST_PLANT (PLNTST destroy/creates, REAPPLY q10)',
      TYPE_SHAPES['TypeShortmushroom'] == TYPE_SHAPES['TypePoisonPlant']
      == SHAPE_TEST_PLANT)
si = shapes[SHAPE_TEST_PLANT]
check('plant TYPEFLAG is donor 65\'s row: SI_FIXED|SI_SOLID, no SI_LAND',
      same_row(si, shapes[65]) and si.flags0 & SI_FIXED
      and si.flags0 & SI_SOLID and not si.has_flag('SI_LAND'))
_tp = placed(SHAPE_TEST_PLANT, MAP_VALE)
check('Map 10 places one Test Plant, frame 0 q10 at (12800, 29408, 64)',
      [(i.frame, i.quality, i.x, i.y, i.z) for i in _tp] ==
      [(0, 10, 12800, 29408, 64)], str([(i.frame, i.quality, i.x, i.y, i.z)
                                        for i in _tp]))
# The 1994 shots are placed verbatim (vignettes, 2026-10-16), and screen21
# lays a retail 126 walkable tile (frame 13) on the knoll: no usecode reads
# 126 since TypeShortmushroom moved to 871, so only the Test Plant's own
# 126 had to go.
import vignette_place as _VP                          # noqa: E402
_shot126 = set()
for _f in sorted(os.listdir(_VP.VIGNETTE_DIR)):
    if _f.startswith('screen') and _f.endswith('.json'):
        _v = _VP.load(_f[:-5])
        _o = _VP.origin(_v)
        _shot126 |= {(it['frame'], it['x'] + _o[0], it['y'] + _o[1],
                      it['z'] + _o[2]) for it in _v['items'] if it['shape'] == 126}
check('no 126 left on Map 10 but the 1994 shots\' own (the other LV maps '
      'never had one)',
      not any((i.frame, i.x, i.y, i.z) not in _shot126
              for m in LV_MAPS for i in placed(126, m)),
      str([(m, i.frame, i.x, i.y, i.z) for m in LV_MAPS
           for i in placed(126, m)]))
_fp = (si.footpad_x * 32, si.footpad_y * 32)
_pops = [(12767, 29791), (12863, 29727), (12735, 29663), (12639, 29695),
         (12767, 29567), (12800, 29408)]
_clash = [(a, b) for n, a in enumerate(_pops) for b in _pops[n + 1:]
          if overlaps((*a, 64, *_fp, 32), (*b, 64, *_fp, 32))]
check('the placed plant and PLNTST\'s five pops never overlap',
      not _clash, str(_clash))
check('TYPETESTPLANT is pinned to the shape number',
      _man['classes'].get('TYPETESTPLANT') == SHAPE_TEST_PLANT,
      str(_man['classes'].get('TYPETESTPLANT')))
check('EUSECODE class 871 barks the 1994 "Strange plant"',
      barks(SHAPE_TEST_PLANT, 'Strange plant'))

# ── 13. The 1994 art: the cut screenshot pixels, verbatim, on safe rows ──
print('\n-- 13. The 1994 art (874-879): built frames equal the cut PNGs --')
_tf = open(TYPEFLAG, 'rb').read()


def tf_row(shape):
    return _tf[shape * 8:shape * 8 + 8]


SI_LAND, SI_OCCL, SI_DRAW = 0x08, 0x10, 0x01      # byte 0, 0, byte 1
_rows94 = [p for p in PROPS if 'indexed' in p]
check('the 1994 rows are exactly shapes 874-879, 881 and phase D\'s 882-886 '
      '(880 is a copy row)',
      [p['shape'] for p in _rows94] == list(range(874, 880)) + [881] +
      list(range(882, 887)))
for prop in _rows94:
    _frames = parse_shape_frames(read_flx_entry(flx, prop['shape']))
    for i, (f, src) in enumerate(zip(_frames, indexed_sources(prop, REG))):
        im = Image.open(os.path.join(BASE_DIR, src['png']))
        check(f'{prop["name"]} frame {i} is registry {src["ref"]}\'s PNG '
              f'index for index ({im.size[0]}x{im.size[1]}, {src["grade"]})',
              im.mode == 'P' and (f['width'], f['height']) == im.size
              and f['pixels'] == list(im.getdata()))
        check(f'{prop["name"]} frame {i} anchored at {src["anchor"]}',
              (f['xoff'], f['yoff']) == tuple(src['anchor']),
              f"got ({f['xoff']},{f['yoff']})")
    check(f'{prop["name"]}: no grade outside cross-shot-validated / '
          f'single-shot reaches the build',
          all(s['grade'] in ('cross-shot-validated', 'single-shot')
              for s in indexed_sources(prop, REG)))
# Floors draw one pixel higher than the registry hotspot (z=0, not z=1);
# objects keep it.
for sid, reg_id, shift in ((SHAPE_CLOUD_1994, 2000, 1),
                           (SHAPE_GOLD_BRICK_1994, 2004, 1),
                           (SHAPE_MARBLE_WALKWAY_1994, 2003, 1),
                           (SHAPE_WHITE_COLUMN_1994, 2001, 0),
                           (SHAPE_SACRED_SHIELD_1994, 2013, 0)):
    _f0 = parse_shape_frames(read_flx_entry(flx, sid))[0]
    _hx, _hy = REG['shapes'][str(reg_id)]['frames'][0]['hotspot']
    check(f'{sid}: anchor is registry {reg_id}\'s ({_hx},{_hy}) with yoff '
          f'+{shift}', (_f0['xoff'], _f0['yoff']) == (_hx, _hy + shift),
          f"got ({_f0['xoff']},{_f0['yoff']})")
# The two halves at one position reassemble the altar Shield (879).
_h = parse_shape_frames(read_flx_entry(flx, SHAPE_SHIELD_HALVES_1994))
_w = parse_shape_frames(read_flx_entry(flx, SHAPE_SACRED_SHIELD_1994))[0]
_canvas = {}
for _f in _h:
    for _n, _px in enumerate(_f['pixels']):
        if _px != 255:
            _canvas[(_n % _f['width'] - _f['xoff'],
                     _n // _f['width'] - _f['yoff'])] = _px
_whole = {(_n % _w['width'] - _w['xoff'], _n // _w['width'] - _w['yoff']): _px
          for _n, _px in enumerate(_w['pixels']) if _px != 255}
_agree = sum(1 for k, v in _whole.items() if _canvas.get(k) == v)
check(f'878 frames 0+1 at one position reproduce 879 (screen04\'s altar '
      f'Shield) at >= 600 of its {len(_whole)} px', _agree >= 600,
      f'{_agree}/{len(_whole)}')
for sid in (SHAPE_CLOUD_1994, SHAPE_GOLD_BRICK_1994):
    r = tf_row(sid)
    check(f'{sid}: a flat SI_LAND|SI_SOLID|SI_OCCL floor without SI_DRAW (a '
          f'SI_DRAW flat sorts under every floor at its z; SI_OCCL sorts '
          f'under the flat props lying on it)',
          shapes[sid].footpad_z == 0 and r[0] & SI_LAND and r[0] & SI_SOLID
          and r[0] & SI_OCCL and not r[1] & SI_DRAW, r.hex())
_r301 = bytearray(tf_row(301))
_r301[1] &= ~SI_DRAW
_r301[0] |= SI_OCCL
check('874\'s TYPEFLAG row is 301\'s with SI_DRAW swapped for SI_OCCL, '
      'byte for byte (retail 163\'s row)',
      tf_row(SHAPE_CLOUD_1994) == bytes(_r301) == tf_row(163),
      f'{tf_row(SHAPE_CLOUD_1994).hex()} vs {bytes(_r301).hex()}')
# 879 is the one exception (2026-10-17): it is the restored Shield the
# ceremony creates, so its look() is class 879, lv-new/SACSHLD.UNK
# (class = shape, item.cpp:1516), pinned TYPESACREDSHIELD like TYPEELIXIR.
_eus = UsecodeFlexArchive(os.path.join(BUILD, 'EUSECODE.FLX'))
check('no other 1994-art shape carries a usecode class (EUSECODE 874-878 '
      'empty)', not any(_eus.get_class_data(s) for s in range(874, 879)))
check('no manifest class is pinned at 874-879 but TYPESACREDSHIELD',
      sorted(k for k, v in _man['classes'].items() if 874 <= v <= 879)
      == ['TYPESACREDSHIELD'],
      str({k: v for k, v in _man['classes'].items() if 874 <= v <= 879}))
check('TYPESACREDSHIELD is pinned to the shape number (the engine dispatches '
      'look() to class = shape, item.cpp:1516)',
      _man['classes'].get('TYPESACREDSHIELD') == SHAPE_SACRED_SHIELD_1994,
      str(_man['classes'].get('TYPESACREDSHIELD')))
_cls = _eus.get_class_data(SHAPE_SACRED_SHIELD_1994)
check(f'EUSECODE class {SHAPE_SACRED_SHIELD_1994} is compiled and its look() '
      f'barks "Ceremonial Shield of the Ancients Ones"',
      bool(_cls) and b'Ceremonial Shield of the Ancients Ones' in _cls)

# ── 14. The retired ids: unbuilt, unplaced, never reused; 870 an alias ───
# 861 (the Magnetic Obelisk) and 862 (the cloud floor tile) were replaced by
# the 1994 art on 2026-10-17 — screen11's retail obelisk composite and 874 —
# and dropped from the build. Their slots stay the base game's, so a save or
# a record that names one finds nothing else there. 870 (the Shield halves
# cut from 828) was replaced by 878 the same day, but a 2026-10-11..17 save
# can carry it in the pack, where an empty slot aborts ScummVM
# (ContainerGump::run, `Assertion sh`; verify3 claim 2): it is built as a
# copy of 878, frames and TYPEFLAG row, and nothing places or names it.
print('\n-- 14. Retired ids %s: unbuilt, unplaced, unused; 870 = 878 --'
      % '/'.join(map(str, RETIRED_SHAPE_IDS)))
from base_input import pristine_base                 # noqa: E402
_base_tf = open(pristine_base(os.path.join(
    BASE_DIR, 'shared', 'data', 'u8-install', 'STATIC', 'TYPEFLAG.DAT'),
    None, 'base TYPEFLAG.DAT'), 'rb').read()
check('the retired ids are exactly 861 and 862 (870 is an alias, not '
      'retired)', tuple(RETIRED_SHAPE_IDS) == (861, 862),
      str(RETIRED_SHAPE_IDS))
check('no PROPS row builds a retired id',
      not any(p['shape'] in RETIRED_SHAPE_IDS for p in PROPS),
      str([p['shape'] for p in PROPS if p['shape'] in RETIRED_SHAPE_IDS]))
_built_maps = (8, 39) + LV_MAPS
_on_maps = {m: {i.shape for i in expand_globs(
    MapArchive(FIXED).get_map_items(m), GlobReader())} for m in _built_maps}
for sid in RETIRED_SHAPE_IDS:
    check(f'{sid}: no data in U8SHAPES.FLX (the base game\'s empty slot)',
          read_flx_entry(flx, sid) is None)
    check(f'{sid}: TYPEFLAG row is the base game\'s',
          tf_row(sid) == _base_tf[sid * 8:sid * 8 + 8],
          f'{tf_row(sid).hex()} vs {_base_tf[sid * 8:sid * 8 + 8].hex()}')
for sid in RETIRED_SHAPE_IDS + (SHAPE_SHIELD_HALVES_LEGACY,):
    check(f'{sid}: placed on no map the build writes {_built_maps}',
          not any(sid in _on_maps[m] for m in _built_maps),
          str([m for m in _built_maps if sid in _on_maps[m]]))
    check(f'{sid}: no EUSECODE class', not _eus.get_class_data(sid))
_unnamed = RETIRED_SHAPE_IDS + (SHAPE_SHIELD_HALVES_LEGACY,)
check('no TYPE_SHAPES entry resolves to a retired id or to 870 (SHADES and '
      'REAPPLY name 870 by literal)',
      not any(v in _unnamed for v in TYPE_SHAPES.values()),
      str({k: v for k, v in TYPE_SHAPES.items() if v in _unnamed}))
check('no manifest class is pinned at a retired id or at 870',
      not any(v in _unnamed for v in _man['classes'].values()),
      str({k: v for k, v in _man['classes'].items() if v in _unnamed}))
_ld = read_flx_entry(flx, SHAPE_SHIELD_HALVES_LEGACY)
_legacy = parse_shape_frames(_ld) if _ld else []
_halves = parse_shape_frames(read_flx_entry(flx, SHAPE_SHIELD_HALVES_1994))
check('870 is built: 878\'s two frames, pixels, size and anchor verbatim '
      '(an old half in the pack draws as the 1994 half)',
      len(_legacy) == 2 and
      [(g['width'], g['height'], g['xoff'], g['yoff'], g['pixels'])
       for g in _legacy] ==
      [(g['width'], g['height'], g['xoff'], g['yoff'], g['pixels'])
       for g in _halves], f'{len(_legacy)} frame(s)')
check('870\'s TYPEFLAG row is 878\'s byte for byte (carryable, 828\'s family, '
      'no equip slot)', tf_row(SHAPE_SHIELD_HALVES_LEGACY) ==
      tf_row(SHAPE_SHIELD_HALVES_1994),
      f'{tf_row(SHAPE_SHIELD_HALVES_LEGACY).hex()} vs '
      f'{tf_row(SHAPE_SHIELD_HALVES_1994).hex()}')

# Decorative art must keep the existing gameplay surfaces and named witness.
print('\n-- 15. Decorative water and west sanctum passage --')
for sid in (896, 897):
    check(f'{sid}: decorative flags exclude sea, solid, land, and occlusion',
          shapes[sid].flags0 == shapes[202].flags0
          and shapes[sid].flags1 == shapes[202].flags1)
check('897: original 566 box dimensions',
      (shapes[897].footpad_x, shapes[897].footpad_y, shapes[897].footpad_z)
      == (shapes[566].footpad_x, shapes[566].footpad_y, shapes[566].footpad_z))
from void_audit import Scene
from avatar_visibility import Poses, visibility
water_items = expand_globs(MapArchive(FIXED).get_map_items(11), GlobReader())
water_paint = [it for it in water_items if it.shape == 896]
water_section_paint = [it for it in water_paint
                       if 6144 <= it.x < 14336 and 14336 <= it.y < 19456]
check('Water section: 112 navy tiles surround the four dry islands',
      len(water_section_paint) == 112 and all(it.frame == 0 and it.z == 0
                                    for it in water_paint))
dry_support = {(it.x, it.y) for it in water_items
               if it.shape == 35 and it.z == 0}
check('every decorative water tile keeps its original dry flagstone support',
      all((it.x, it.y) in dry_support for it in water_paint))
from lv_art_props import CAVE_BACKDROP_CLIPS
editor_support = {(it.shape, it.x, it.y, it.z) for it in water_items}
protected_support = {(clip['support_shape'], *clip['at'], 0)
                     for clip in CAVE_BACKDROP_CLIPS
                     if clip['map'] == 11 and clip.get('kind') != 'window'}
check('clipped tails retain every original support box as an editor plate',
      protected_support <= editor_support,
      str(sorted(protected_support - editor_support)))
sanctum = Scene(18)
tiny_poses = Poses(sanctum.painter, sanctum.anim, shape=867)
minimum = visibility(sanctum, tiny_poses, (2591, 7295, 0))['min_visible']
check('m18-19: Tiny Tar visible in every walk and stand pose',
      minimum >= .9, str(minimum))
# Follow the connected westward jog around the protected rock face.
passage = [(2671, y, 0) for y in range(7199, 7296, 16)]
passage += [(x, 7295, 0) for x in range(2655, 2526, -16)]
passage += [(2527, y, 0) for y in range(7311, 7552, 16)]
route_minimum = min(visibility(sanctum, tiny_poses, spot)['min_visible']
                    for spot in passage)
check('west passage through y 7551: every pose on the connected jog >= 80%',
      route_minimum >= .8, str(route_minimum))
from vignette_built_window import window
import hashlib
screen04_pixels = window('screen04', actors=True)[0]
check('screen04: every palette pixel retains its pre-art-pass value',
      hashlib.sha256(screen04_pixels.astype('<i2').tobytes()).hexdigest()
      == 'b115b101ec8667df794f555f79562c8ae3ff73bed9a6494a99b0862d92931f69')
for name, floor, allowance in (('screen05', 94.30, 0), ('screen07', 97.02, 6)):
    pixels, reference_rgb, _, score = window(name, actors=True)
    check(f'{name}: clipped backdrops retain the screenshot floor', score >= floor,
          str(score))
    holes = int(((pixels < 0) & (reference_rgb.sum(-1) > 12)).sum())
    check(f'{name}: clipped backdrops retain the unpainted allowance',
          holes <= allowance, str(holes))
# Animated objects and destroyed pillars must uncover painted background.
import lv_cave_vignette as cave_background
import build_map_11 as elemental_map
background_scene = Scene(11)
background_painter = background_scene.painter
background_items = [it for it in background_scene.items
                    if background_painter.info(it['shape'])['fixed']
                    and not background_painter.info(it['shape'])['anim']
                    and background_painter.info(it['shape'])['zd'] == 0
                    and (background_painter.info(it['shape'])['land']
                         or background_painter.info(it['shape'])['solid']
                         or it['shape'] in (894, 895))]
reference_background = [it for it in background_items
                        if it['shape'] != 895 or it['frame'] < 7]
reference_background += [dict(shape=35 if clip['support_shape'] == 763 else 564,
                             frame=10 if clip['support_shape'] == 763 else 2,
                             x=clip['at'][0], y=clip['at'][1], z=0)
                         for clip in CAVE_BACKDROP_CLIPS
                         if clip['map'] == 11 and clip.get('kind') != 'window']
fire_art = {2023: (elemental_map.SHAPE_PILLAR, 2)}
fire_art.update({key: (782, 0) for key in elemental_map.SCREEN07_LEFT_OUT})
for name in ('screen05', 'screen07'):
    shot = (cave_background.Shot(name, art_map=fire_art)
            if name == 'screen07' else cave_background.Shot(name))
    before_background = background_painter.paint(
        reference_background, shot.csx, shot.csy, shot.W, shot.H)[0]
    after_background = background_painter.paint(
        background_items, shot.csx, shot.csy, shot.W, shot.H)[0]
    holes = int(((before_background >= 0) & (after_background < 0)).sum())
    check(f'{name}: background stays painted beneath animated and removable objects',
          holes == 0, str(holes))

print('=' * 70)
print(f'{passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

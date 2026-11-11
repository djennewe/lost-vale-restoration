#!/usr/bin/env python3
"""
vignette_place.py — put a reconstructed 1994 screenshot into a map, verbatim.

Each published 1994 Lost Vale screenshot is reconstructed as a vignette
(vignettes/screenNN.json, docs/research/2026-10-16-screenshot-reconstruction.md):
items in local coordinates, x/y the footprint's max corner as everywhere in
U8, plus `placement.origin_world`. World position = origin + local.

`stamp(items, shot, map_num)` makes the map show that shot:

  1. every glob egg whose chunk meets the vignette is replaced by the items
     it would expand to (GlobEgg::enterFastArea's transform, via
     GlobReader.glob_to_items), so the generated ground can be cut tile by
     tile instead of a whole 512 chunk at a time;
  2. every item whose XY box meets the vignette's region is removed — the
     region is the union of the 128-unit cells that any vignette item's
     footprint touches — so nothing generated survives inside the shot;
  3. the vignette's items are added at origin + local.

`slides` ({(shape, frame, local x, y, z): k}) moves a shot item k steps of
(8, 8, 2) along the view ray: screen x = x/4 - y/4 and y = x/8 + y/8 - z
are exact over a step, so the item draws the same pixels and only the
boxes it meets move. A reconstruction fixes a position only up to that
ray, and a piece solved inside its neighbours can close a paint cycle
(build_map_13.RAY_SLIDES does the same through lv_map13_tiers; Map 10's
are build_map_10.RAY_SLIDES). A slide naming no item of the shot raises.

An item listed in map_pins.json is never removed silently: if one falls in
the region the call raises, naming it, because a pin move is a decision
(the vignette's `placement.pin_moves` records the ones already made).
Eggs of any kind are kept: they draw nothing and are positioned by the
Only real shape ids are placed: a retail shape, or an id the art track
built (860+, e.g. the 1994 art at 874-879), goes in directly. A synthetic
1994-art id from vignettes/art_registry.json (>= 2000) is refused unless
`art_map` maps it to a built shape. Footprints come from the BUILT
shared/build/TYPEFLAG.DAT (it carries the art track's rows), falling back to
the install copy only if the build is missing.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from glob_catalog import GlobReader, ShapeFlags  # noqa: E402
from u8_map import MapItem  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
VIGNETTE_DIR = os.path.join(HERE, "vignettes")
PINS = os.path.join(HERE, "map_pins.json")
CELL = 128
CHUNK = 512
FIRST_SYNTHETIC_ID = 2000     # vignettes/art_registry.json ids start here
BUILT_TYPEFLAG = os.path.join(HERE, "..", "..", "..", "shared", "build",
                              "TYPEFLAG.DAT")

_SF = None
_GLOBS = None


def _flags():
    global _SF
    if _SF is None:
        _SF = (ShapeFlags(BUILT_TYPEFLAG) if os.path.exists(BUILT_TYPEFLAG)
               else ShapeFlags())
    return _SF


def _globs():
    global _GLOBS
    if _GLOBS is None:
        _GLOBS = GlobReader()
    return _GLOBS


def load(shot):
    with open(os.path.join(VIGNETTE_DIR, f"{shot}.json")) as f:
        return json.load(f)


def origin(vig):
    return tuple(vig["placement"]["origin_world"])


def _box(shape, x, y):
    """XY box of an item: [x0, x1) x [y0, y1) in world units (x, y = max corner)."""
    info = _flags().get(shape)
    w = (info["xfoot"] if info else 0) * 32
    d = (info["yfoot"] if info else 0) * 32
    return x - w + 1, x + 1, y - d + 1, y + 1


def _cells(box):
    x0, x1, y0, y1 = box
    return {(cx, cy)
            for cx in range(x0 // CELL, (x1 - 1) // CELL + 1)
            for cy in range(y0 // CELL, (y1 - 1) // CELL + 1)}


def world_items(vig, art_map=None, slides=None):
    """The vignette's items as MapItems at origin + local.

    1994-only art the art track has not built carries a synthetic id from
    vignettes/art_registry.json (>= 2000). `art_map` maps such an id to the
    shape the art track built for it — an int shape (the item keeps its
    frame) or a (shape, frame) tuple — or to a stand-in until it does; an
    unmapped synthetic id raises. Real shape ids (< 2000, built art
    included) place directly. `slides`: see the module docstring."""
    ox, oy, oz = origin(vig)
    art_map = art_map or {}
    slides = dict(slides or {})
    out = []
    for it in vig["items"]:
        shape, frame = it["shape"], it["frame"]
        k = slides.pop((shape, frame, it["x"], it["y"], it["z"]), 0)
        if shape in art_map:
            to = art_map[shape]
            shape, frame = (to, frame) if isinstance(to, int) else to
        elif not isinstance(shape, int) or shape >= FIRST_SYNTHETIC_ID:
            raise ValueError(
                f"{vig['shot']}: item {it} is 1994-only art; map it to a shape "
                "(art_map) before placing it")
        out.append(MapItem.placed_item(ox + it["x"] + 8 * k,
                                       oy + it["y"] + 8 * k,
                                       oz + it["z"] + 2 * k, shape, frame))
    if slides:
        raise ValueError(f"{vig['shot']}: slides name no item of the shot: "
                         f"{sorted(slides)}")
    return out


def region(vig, art_map=None, slides=None):
    """Union of the 128-unit cells any vignette item's footprint touches."""
    cells = set()
    for it in world_items(vig, art_map, slides):
        cells |= _cells(_box(it.shape, it.x, it.y))
    return cells


def _is_ground(shape):
    info = _flags().get(shape)
    return bool(info and (info["land"] or info["sea"]) and info["zfoot"] <= 1)


def hidden_ground(vig, shape=301, frames=range(7), art_map=None, slides=None):
    """Floor for the region cells the shot never shows a floor in.

    A cell behind a cliff face or under a building has no ground item in
    the reconstruction (nothing of it reached the screen), but it is open
    floor from every other camera position. It gets the shot's base
    material at the vignette's base z, on the shot's 128k+127 lattice, the
    frame chosen by a hash of the cell so the fill is deterministic."""
    ox, oy, oz = origin(vig)
    items = world_items(vig, art_map, slides)
    shown = set()
    cells = set()
    for it in items:
        box = _cells(_box(it.shape, it.x, it.y))
        cells |= box
        if _is_ground(it.shape):
            shown |= box
    frames = list(frames)
    out = []
    for cx, cy in sorted(cells - shown):
        h = (cx * 73856093 ^ cy * 19349663) & 0xFFFF
        out.append(MapItem.placed_item(cx * CELL + CELL - 1, cy * CELL + CELL - 1,
                                       oz, shape, frames[h % len(frames)]))
    return out


def _pinned(map_num):
    with open(PINS) as f:
        pins = json.load(f)["maps"].get(str(map_num), [])
    return {(p["shape"], p["x"], p["y"], p["z"]) for p in pins
            if p.get("kind") != "quest_item" or p["x"] >= 0}


def _is_egg(item):
    return item.is_glob_egg or item.is_teleport_egg or item.is_monster_egg \
        or item.shape == MapItem.SHAPE_STANDARD_EGG


def stamp(items, shot, map_num, art_map=None, fill=(301, range(7)),
          slides=None):
    """Return `items` with the vignette for `shot` placed verbatim.

    `art_map`: synthetic 1994-art id -> (shape, frame), see world_items.
    `fill`: (shape, frames) for hidden_ground, or None for no fill (water,
    void, or a builder that floors the cells itself). `slides`: view-ray
    moves of the shot's own items (module docstring)."""
    vig = load(shot)
    if vig["placement"]["map"] != map_num:
        raise ValueError(f"{shot} belongs to map {vig['placement']['map']}, not {map_num}")
    cells = region(vig, art_map, slides)
    chunks = {(cx * CELL // CHUNK, cy * CELL // CHUNK) for cx, cy in cells}

    expanded = []
    for it in items:
        if it.is_glob_egg and (it.x // CHUNK, it.y // CHUNK) in chunks:
            expanded.extend(_globs().glob_to_items(it.quality, it.x, it.y, it.z))
        else:
            expanded.append(it)

    pins = _pinned(map_num)
    kept = []
    for it in expanded:
        if _is_egg(it) or not (_cells(_box(it.shape, it.x, it.y)) & cells):
            kept.append(it)
            continue
        if (it.shape, it.x, it.y, it.z) in pins:
            raise ValueError(
                f"{shot}: pinned item shape {it.shape} at ({it.x},{it.y},{it.z}) "
                "is inside the vignette; move the pin (placement.pin_moves) first")
    floor = hidden_ground(vig, fill[0], fill[1], art_map, slides) if fill else []
    return kept + world_items(vig, art_map, slides) + floor

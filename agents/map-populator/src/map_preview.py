#!/usr/bin/env python3
"""
map_preview.py — Render whole Lost Vale maps to PNG for review without
launching ScummVM.

This is a QA tool, not a data pipeline: it imports each map's builder module
directly (build_map_09.build_map_09(), etc.) rather than reading FIXED.DAT, so
it always reflects uncommitted source changes. Glob eggs are expanded to their
concrete items (via glob_catalog.GlobReader) so buildings are actually visible,
and invisible logic items (monster eggs, teleporters/targets) are drawn as
small labeled markers since they have no sprite.

Reuses iso_render.IsoRenderer for all shape decoding / compositing — this
module only resolves item lists and drives the renderer.

Usage:
    python3 map_preview.py 9 11 13 17 18 [--out DIR] [--scale N]

Default output dir: shared/build/map_previews/, one PNG per map (map_09.png).
"""

import os
import sys
import argparse
import importlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image

from iso_render import IsoRenderer, PALETTE_FILE
from glob_catalog import GlobReader

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))  # .../lost-vale

# Custom LV shapes (856-858, wood walls etc) only exist in the build copy of
# U8SHAPES.FLX. Prefer it when present, fall back to the base game copy.
BUILD_SHAPES_FLX = os.path.join(BASE_DIR, "shared", "build", "U8SHAPES.FLX")
BASE_SHAPES_FLX = os.path.join(
    BASE_DIR, "shared", "data", "u8-install", "STATIC", "U8SHAPES.FLX")

DEFAULT_OUT_DIR = os.path.join(BASE_DIR, "shared", "build", "map_previews")

# Cap output image dimensions (Map 10 in particular is large).
MAX_DIM = 4000

# Map -> (module name, entry-point function name). Map 8 only ever modifies
# the base game map (adds a door/key/teleports near the entry) — its builder
# returns *additions only*, not a full map, so the preview is necessarily
# partial for that one map.
MAP_BUILDERS = {
    8: ("build_map_08", "build_map_08_additions"),
    9: ("build_map_09", "build_map_09"),
    10: ("build_map_10", "build_map_10"),
    11: ("build_map_11", "build_map_11"),
    13: ("build_map_13", "build_map_13"),
    17: ("build_map_17", "build_map_17"),
    18: ("build_map_18", "build_map_18"),
}

MARKER_COLORS = {
    "monster": (220, 40, 40),        # red
    "tele_target": (40, 200, 240),  # cyan
    "teleporter": (240, 200, 40),     # yellow
}


def shapes_flx_path():
    """Prefer the build copy (custom injected shapes) if it exists."""
    return BUILD_SHAPES_FLX if os.path.exists(BUILD_SHAPES_FLX) else BASE_SHAPES_FLX


def get_map_items(mapnum):
    """Import the build_map_XX module for mapnum and call its entry-point
    build function, returning the raw (unexpanded) MapItem list."""
    if mapnum not in MAP_BUILDERS:
        raise ValueError(
            f"No known builder for map {mapnum} "
            f"(handled maps: {sorted(MAP_BUILDERS)})")
    mod_name, fn_name = MAP_BUILDERS[mapnum]
    mod = importlib.import_module(mod_name)
    fn = getattr(mod, fn_name)
    return fn()


def expand_globs(items, glob_reader):
    """Replace each glob egg with its concrete expanded items (so buildings
    are visible); pass every other item through unchanged."""
    out = []
    for it in items:
        if it.is_glob_egg:
            expanded = glob_reader.glob_to_items(it.quality, it.x, it.y, it.z)
            if expanded:
                out.extend(expanded)
            else:
                out.append(it)  # empty/invalid glob index — keep the egg marker
        else:
            out.append(it)
    return out


def build_markers(items):
    """Labeled QA markers for items with no sprite: monster eggs and
    teleporters/targets (IsoRenderer skips shape 500/508 by default)."""
    marks = []
    for it in items:
        if it.is_monster_egg:
            marks.append({
                "x": it.x, "y": it.y, "z": it.z, "r": 4,
                "color": MARKER_COLORS["monster"],
                "label": f"M{it.quality}",
            })
        elif it.is_teleport_target:
            marks.append({
                "x": it.x, "y": it.y, "z": it.z, "r": 4,
                "color": MARKER_COLORS["tele_target"],
                "label": f"T{it.quality}>",
            })
        elif it.is_teleporter:
            marks.append({
                "x": it.x, "y": it.y, "z": it.z, "r": 4,
                "color": MARKER_COLORS["teleporter"],
                "label": f"<T{it.quality - 256}",
            })
    return marks


def render_map(mapnum, out_path, expand_globs_flag=True, scale=2):
    """Render one LV map to a PNG.

    Returns (out_path, width, height, n_rendered_items, n_raw_items).
    """
    raw_items = get_map_items(mapnum)

    renderer = IsoRenderer(shapes_flx=shapes_flx_path(), palette_file=PALETTE_FILE)

    if expand_globs_flag:
        glob_reader = GlobReader()
        items = expand_globs(raw_items, glob_reader)
    else:
        items = raw_items

    marks = build_markers(items)

    img = renderer.render(items, scale=scale, marks=marks)

    if img.width > MAX_DIM or img.height > MAX_DIM:
        ratio = min(MAX_DIM / img.width, MAX_DIM / img.height)
        new_size = (max(1, int(img.width * ratio)), max(1, int(img.height * ratio)))
        img = img.resize(new_size, Image.LANCZOS)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    img.save(out_path)
    return out_path, img.width, img.height, len(items), len(raw_items)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _main():
    ap = argparse.ArgumentParser(
        description="Render whole Lost Vale maps to PNG for review without ScummVM.")
    ap.add_argument('maps', type=int, nargs='+',
                     help="Map numbers to render, e.g. 9 11 13 17 18")
    ap.add_argument('--out', default=DEFAULT_OUT_DIR, help="Output directory")
    ap.add_argument('--scale', type=int, default=2, help="Pixel scale (nearest-neighbor)")
    ap.add_argument('--no-glob-expand', action='store_true',
                     help="Render raw glob eggs instead of expanding them to buildings")
    args = ap.parse_args()

    print(f"Shapes source: {shapes_flx_path()}")
    os.makedirs(args.out, exist_ok=True)

    for mapnum in args.maps:
        out_path = os.path.join(args.out, f"map_{mapnum:02d}.png")
        try:
            path, w, h, n_rendered, n_raw = render_map(
                mapnum, out_path,
                expand_globs_flag=not args.no_glob_expand,
                scale=args.scale)
            note = ""
            if mapnum == 8:
                note = "  [Map 8 builder returns ADDITIONS ONLY, not the full base map]"
            print(f"Map {mapnum:2d}: {n_raw} raw items -> {n_rendered} rendered "
                  f"-> {path} ({w}x{h}){note}")
        except Exception as exc:
            print(f"Map {mapnum:2d}: ERROR: {exc}")


if __name__ == '__main__':
    _main()

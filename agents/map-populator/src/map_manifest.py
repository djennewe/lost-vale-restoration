#!/usr/bin/env python3
"""
map_manifest.py — Emit a greppable JSON manifest of every placed item in
the Lost Vale maps, so humans can answer "where is X on map Y" without
hand-deriving x0+offset coordinates.

Usage:
    from map_manifest import build_manifest
    manifest = build_manifest(archive, map_nums)

CLI:
    python3 map_manifest.py [--fixed path/to/FIXED.DAT] [--maps 8,9,10,11,13,17,18]
                             [--out shared/build/map_manifest.json]
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from u8_map import MapArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

DEFAULT_FIXED = os.path.join(BASE_DIR, "shared", "build", "FIXED.DAT")
DEFAULT_OUT = os.path.join(BASE_DIR, "shared", "build", "map_manifest.json")
DEFAULT_LV_MAPS = [8, 9, 10, 11, 13, 17, 18]


def _build_shape_name_lookup():
    """Best-effort reverse lookup: shape id -> human name, sourced from
    lv_shapes.py if it exists in this directory. That module is being
    developed in parallel, so its exact layout is unknown — try a few
    reasonable shapes for it and fall back to an empty dict (callers
    then fall back to str(shape)) on any failure."""
    lookup = {}
    try:
        import lv_shapes
    except ImportError:
        return lookup

    try:
        # Strategy 1: an explicit id -> name dict (keys are ints).
        for attr_name in dir(lv_shapes):
            if attr_name.startswith("_"):
                continue
            val = getattr(lv_shapes, attr_name)
            if isinstance(val, dict) and val:
                sample_key = next(iter(val))
                sample_val = val[sample_key]
                if isinstance(sample_key, int) and isinstance(sample_val, str):
                    for k, v in val.items():
                        if isinstance(k, int) and isinstance(v, str):
                            lookup.setdefault(k, v)
                elif isinstance(sample_key, str) and isinstance(sample_val, int):
                    # name -> id dict; reverse it.
                    for k, v in val.items():
                        if isinstance(k, str) and isinstance(v, int):
                            lookup.setdefault(v, k)

        # Strategy 2: top-level UPPER_CASE int constants, e.g.
        # SHAPE_WELL = 855  =>  855 -> "WELL" (SHAPE_ prefix stripped).
        for attr_name in dir(lv_shapes):
            if attr_name.startswith("_") or not attr_name.isupper():
                continue
            val = getattr(lv_shapes, attr_name)
            if isinstance(val, int):
                name = attr_name
                if name.startswith("SHAPE_"):
                    name = name[len("SHAPE_"):]
                lookup.setdefault(val, name)
    except Exception:
        # Never let a shape of lv_shapes.py we didn't anticipate break
        # manifest generation — worst case we fall back to str(shape).
        pass

    return lookup


def _classify_kind(item):
    if item.is_glob_egg:
        return "glob_egg"
    if item.is_teleport_target:
        return "teleport_target"
    if item.is_teleporter:
        return "teleporter"
    if item.is_monster_egg:
        return "monster_egg"
    return "item"


def build_manifest(archive, map_nums, shape_names=None):
    """Build the manifest dict: {mapnum_str: [entry, ...], ...}

    Each entry: {shape, shape_name, engine_name, frame, x, y, z, kind}

    engine_name is the name the GAME prints on single-click (from the
    base-game usecode name table, see shape_names.py) — the authoritative
    identity. When it disagrees with our shape_name constant, trust it.
    """
    if shape_names is None:
        shape_names = _build_shape_name_lookup()

    try:
        from shape_names import all_names
        engine_names = all_names()
    except Exception:
        engine_names = {}

    manifest = {}
    for mapnum in map_nums:
        items = archive.get_map_items(mapnum)
        entries = []
        for item in items:
            entries.append({
                "shape": item.shape,
                "shape_name": shape_names.get(item.shape, str(item.shape)),
                "engine_name": engine_names.get(item.shape),
                "frame": item.frame,
                "x": item.x,
                "y": item.y,
                "z": item.z,
                "kind": _classify_kind(item),
            })
        manifest[str(mapnum)] = entries

    return manifest


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Emit a JSON placement manifest for Lost Vale maps")
    parser.add_argument("--fixed", default=DEFAULT_FIXED,
                        help=f"Path to FIXED.DAT (default: {DEFAULT_FIXED})")
    parser.add_argument("--maps", default=None,
                        help="Comma-separated map numbers "
                             f"(default: {','.join(str(m) for m in DEFAULT_LV_MAPS)})")
    parser.add_argument("--out", default=DEFAULT_OUT,
                        help=f"Output JSON path (default: {DEFAULT_OUT})")
    args = parser.parse_args()

    if not os.path.exists(args.fixed):
        print(f"ERROR: FIXED.DAT not found at {args.fixed}")
        sys.exit(1)

    if args.maps:
        map_nums = [int(m.strip()) for m in args.maps.split(",") if m.strip()]
    else:
        map_nums = DEFAULT_LV_MAPS

    shape_names = _build_shape_name_lookup()
    if shape_names:
        print(f"Loaded {len(shape_names)} shape name(s) from lv_shapes.py")
    else:
        print("lv_shapes.py not found (or unusable) — falling back to str(shape)")

    archive = MapArchive(args.fixed)
    manifest = build_manifest(archive, map_nums, shape_names)

    total = sum(len(v) for v in manifest.values())
    print(f"Built manifest: {len(manifest)} map(s), {total} item(s) total")

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.out, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()

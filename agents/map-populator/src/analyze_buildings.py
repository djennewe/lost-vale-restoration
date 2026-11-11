#!/usr/bin/env python3
"""
analyze_buildings.py — Extract building compositions from base game maps.

Analyzes Maps 39 and 41 (Tenebrae — a working town) to understand how the
base game constructs buildings from individual shape items.

Outputs:
  1. Per-map shape usage by category (walls, roofs, doors, terrain, etc.)
  2. Spatial clusters of structural items (= individual buildings)
  3. Per-cluster z-layer breakdown showing the layered composition pattern
  4. Summary of all structural shapes used in Tenebrae
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from u8_map import MapArchive
from parse_typeflag import load_typeflag

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
BASE_FIXED = os.path.join(
    BASE_DIR, "shared", "data", "u8-install", "STATIC", "FIXED.DAT")


# --- Helpers ---

def _categorize(si):
    """Return a category string for a ShapeInfo object."""
    if si.shape_id == 2:
        return 'globs'
    if si.shape_id == 508:
        return 'teleports'
    if si.has_flag('SI_ROOF'):
        return 'roofs'
    if si.family == 1:
        return 'doors'
    if si.family == 6:
        return 'containers'
    if si.has_flag('SI_LAND'):
        return 'terrain'
    if (si.has_flag('SI_SOLID') and si.has_flag('SI_DRAW')
            and not si.has_flag('SI_LAND')):
        return 'walls'
    return 'other'


def _is_structural(si):
    """True for shapes that form part of a building (wall/roof/door)."""
    cat = _categorize(si)
    return cat in ('walls', 'roofs', 'doors')


# --- Analysis functions ---

def analyze_map_shapes(archive, map_num, shapes):
    """Print shape-usage breakdown by category for one map."""
    items = archive.get_map_items(map_num)
    if not items:
        print(f"Map {map_num}: empty")
        return

    print(f"\n{'=' * 70}")
    print(f"Map {map_num}: {len(items)} items")
    print(f"{'=' * 70}")

    # Count by shape
    shape_counts = {}
    for item in items:
        shape_counts[item.shape] = shape_counts.get(item.shape, 0) + 1

    # Bucket into categories
    categories = {}
    for sid, count in sorted(shape_counts.items(), key=lambda x: -x[1]):
        if sid >= 2048:
            continue
        si = shapes[sid]
        cat = _categorize(si)
        categories.setdefault(cat, []).append((sid, count, si))

    CAT_ORDER = ['walls', 'roofs', 'doors', 'terrain', 'containers',
                 'globs', 'teleports', 'other']
    for cat in CAT_ORDER:
        entries = categories.get(cat, [])
        if not entries:
            continue
        total = sum(c for _, c, _ in entries)
        print(f"\n--- {cat.upper()} ({total} items, {len(entries)} shapes) ---")
        for sid, count, si in entries[:25]:
            flags_str = ",".join(si.flag_names) or "none"
            print(f"  shape {sid:4d} x{count:4d}  "
                  f"fp=({si.footpad_x},{si.footpad_y},{si.footpad_z})  "
                  f"fam={si.family_name:15s}  [{flags_str}]")
        if len(entries) > 25:
            print(f"  ... ({len(entries) - 25} more)")


def cluster_buildings(archive, map_num, shapes, cluster_radius=1024):
    """Find spatial clusters of structural items and print their composition."""
    items = archive.get_map_items(map_num)

    structural = []
    for item in items:
        if item.shape >= 2048:
            continue
        si = shapes[item.shape]
        if _is_structural(si):
            structural.append(item)

    if not structural:
        return []

    # Greedy spatial clustering
    clusters = []
    assigned = set()

    for i, item in enumerate(structural):
        if i in assigned:
            continue
        cluster = [item]
        assigned.add(i)
        frontier = [item]

        while frontier:
            cur = frontier.pop()
            for j, other in enumerate(structural):
                if j in assigned:
                    continue
                if (abs(cur.x - other.x) < cluster_radius
                        and abs(cur.y - other.y) < cluster_radius):
                    cluster.append(other)
                    assigned.add(j)
                    frontier.append(other)

        if len(cluster) >= 3:
            clusters.append(cluster)

    print(f"\n{'=' * 70}")
    print(f"Building Clusters on Map {map_num} ({len(clusters)} found)")
    print(f"{'=' * 70}")

    for ci, cluster in enumerate(clusters[:20]):
        min_x = min(i.x for i in cluster)
        max_x = max(i.x for i in cluster)
        min_y = min(i.y for i in cluster)
        max_y = max(i.y for i in cluster)
        min_z = min(i.z for i in cluster)
        max_z = max(i.z for i in cluster)

        n_walls = sum(1 for it in cluster
                      if _categorize(shapes[it.shape]) == 'walls')
        n_roofs = sum(1 for it in cluster
                      if _categorize(shapes[it.shape]) == 'roofs')
        n_doors = sum(1 for it in cluster
                      if _categorize(shapes[it.shape]) == 'doors')

        print(f"\n--- Cluster {ci + 1}: {len(cluster)} items  "
              f"bbox=({min_x},{min_y},{min_z})–({max_x},{max_y},{max_z}) ---")
        print(f"  Walls: {n_walls}  Roofs: {n_roofs}  Doors: {n_doors}")

        # Z-layer breakdown
        z_layers = {}
        for it in cluster:
            z_layers.setdefault(it.z, []).append(it)

        print(f"  Z layers: {sorted(z_layers.keys())}")
        for z in sorted(z_layers.keys()):
            layer = z_layers[z]
            summary = {}
            for it in layer:
                si = shapes[it.shape]
                key = (it.shape, si.footpad_x, si.footpad_y, si.footpad_z)
                summary[key] = summary.get(key, 0) + 1
            parts = []
            for (sid, fx, fy, fz), cnt in sorted(summary.items()):
                parts.append(f"shape {sid}({fx}x{fy}x{fz}) x{cnt}")
            print(f"    z={z:3d}: {len(layer)} items — {', '.join(parts)}")

        # Full item list for small clusters
        if len(cluster) <= 25:
            print(f"  Items:")
            for it in sorted(cluster, key=lambda i: (i.z, i.y, i.x)):
                si = shapes[it.shape]
                cat = _categorize(si)
                print(f"    shape={it.shape:4d} f={it.frame} "
                      f"pos=({it.x:5d},{it.y:5d},{it.z:3d}) "
                      f"fp=({si.footpad_x},{si.footpad_y},{si.footpad_z}) "
                      f"[{cat}]")

    return clusters


def print_shape_reference(archive, shapes, map_nums):
    """Print summary of all structural shapes used across analyzed maps."""
    building_shapes = set()
    for mn in map_nums:
        for item in archive.get_map_items(mn):
            if item.shape < 2048 and item.shape != 2:
                si = shapes[item.shape]
                if _is_structural(si):
                    building_shapes.add(item.shape)

    print(f"\n{'=' * 70}")
    print(f"STRUCTURAL SHAPE REFERENCE  "
          f"({len(building_shapes)} shapes from maps {map_nums})")
    print(f"{'=' * 70}")

    for sid in sorted(building_shapes):
        si = shapes[sid]
        flags_str = ",".join(si.flag_names)
        print(f"  shape {sid:4d}: fp=({si.footpad_x},{si.footpad_y},"
              f"{si.footpad_z})  fam={si.family_name:15s}  [{flags_str}]")


# --- Entrypoint ---

def main():
    if not os.path.exists(BASE_FIXED):
        print(f"ERROR: FIXED.DAT not found at {BASE_FIXED}")
        sys.exit(1)

    shapes = load_typeflag()
    archive = MapArchive(BASE_FIXED)

    target_maps = [39, 41]

    for mn in target_maps:
        analyze_map_shapes(archive, mn, shapes)
        cluster_buildings(archive, mn, shapes)

    print_shape_reference(archive, shapes, target_maps)


if __name__ == '__main__':
    main()

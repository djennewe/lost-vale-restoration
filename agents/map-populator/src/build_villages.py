#!/usr/bin/env python3
"""
build_villages.py — FULLY-AUTOMATED Lost Vale village construction.

Integrates the three new approaches so a village is generated end-to-end with no
tile placed by hand:

  Approach 1  building_prefab.REGISTRY      — real base-game buildings (Stampable)
  Approach 2  glob_catalog.GlobPrefab       — engine-native building globs
  Approach 3  village_layout.generate_village — procedural placement + paths + ground

All three meet at the shared "Stampable" contract (.name/.footprint/.tags/
.origin_z/.stamp), so the layout engine treats a hand-extracted prefab and a
GLOB.FLX building identically.

Targets the two Zealan clan villages on Map 10 (Hoskuld, Gunnar). The aesthetic
reference is shared/data/lv-screenshots/screen19.gif: red ribbed clay-tile roofs
+ wood-plank walls on grey rock — which is exactly what the Map-39 prefabs and
the red-roof building globs look like.

Run (preview only — writes PNGs to /tmp, touches nothing):
    cd agents/map-populator/src && python3 build_villages.py

Run (inject the generated villages into Map 10 + rebuild FIXED.DAT):
    python3 build_villages.py --write
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from u8_map import MapArchive, MapItem
from iso_render import IsoRenderer
from building_prefab import REGISTRY, get_prefabs
from village_layout import VillageSpec, generate_village, plan_layout, check_overlaps
from glob_catalog import GlobReader, GlobPrefab

# ---------------------------------------------------------------------------
# Building pools  (decision: glob-native houses + prefab accents)
# ---------------------------------------------------------------------------
_BY_NAME = {p.name: p for p in REGISTRY}

# Homes = engine-native red clay-roof Tenebrae-house globs (Approach 2).
HOUSE_GLOBS = [573, 575, 538, 537, 1007, 1011]

# Prefab accents (Approach 1): a civic centerpiece + an animal pen + a fence.
HALL_NAME = "great_hall_grey"
PEN_NAME = "stone_yard"
FENCE_NAME = "stone_wall_ruin"

# Ground: glob 40 = grass with natural rock/scrub variation (the Lost Vale is a
# lush valley; screen19's bare rock is the cliff entrance, not the village floor).
GROUND_GLOB = 40


def make_house_prefabs(reader, indices=HOUSE_GLOBS):
    """Wrap each building-glob index as a Stampable, skipping any that are empty."""
    out = []
    for idx in indices:
        gp = GlobPrefab(reader, idx, tags=["norse", "house", "red-roof"],
                        name=f"glob_house_{idx}")
        if gp.footprint != (0, 0):
            out.append(gp)
    return out


# ---------------------------------------------------------------------------
# Glob expansion for preview rendering
# ---------------------------------------------------------------------------

def expand_for_preview(items, reader):
    """Replace glob eggs (shape 2) with their expanded item lists so the
    isometric renderer can actually draw them. The saved map keeps the eggs;
    only previews are expanded."""
    out = []
    for it in items:
        if it.shape == MapItem.SHAPE_GLOB_EGG:
            out.extend(reader.glob_to_items(it.quality, it.x, it.y, it.z))
        else:
            out.append(it)
    return out


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def generate_clan_village(name, center, seed, reader,
                          target_houses=6, bounds=(1920, 1920),
                          ring_radius=1280, with_hall=True):
    """Glob-native homes ringed around an optional prefab clan-hall centerpiece,
    with animal-pen / fence prefab accents, on grass. Fully automated."""
    houses = make_house_prefabs(reader)
    pens = [_BY_NAME[n] for n in (PEN_NAME,) if n in _BY_NAME]

    spec = VillageSpec(
        center=center, bounds=bounds, target_buildings=target_houses,
        style="cluster", ground_glob=GROUND_GLOB, seed=seed,
        ring_radius=ring_radius, min_gap=64,
        path_shape=None,   # flat z=0 paths don't read against grass in preview;
                           # the hall + ringed houses + pens carry the layout
        grid_snap=512,   # glob eggs snap to their 512 chunk; place on that grid
    )
    items = generate_village(spec, houses, props=pens)

    # Prefab centerpiece: the clan hall sits on the plaza the houses ring.
    if with_hall and HALL_NAME in _BY_NAME:
        hall = _BY_NAME[HALL_NAME]
        hw, hh = hall.footprint
        items.extend(hall.stamp(center[0] - hw // 2, center[1] - hh // 2,
                                hall.origin_z))

    placements, shortfall = plan_layout(spec, houses)
    n_eggs = sum(1 for it in items if it.shape == MapItem.SHAPE_GLOB_EGG)
    print(f"[{name}] {len(placements)}/{target_houses} glob houses"
          f"{' + hall' if with_hall else ''}, {n_eggs} eggs, {len(items)} items"
          f" (shortfall {shortfall})")
    return items


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render(items, reader, out, scale=2, expand_ground=True):
    renderer = IsoRenderer()
    preview = expand_for_preview(items, reader) if expand_ground else \
        [it for it in items if it.shape != MapItem.SHAPE_GLOB_EGG]
    img = renderer.render(preview, scale=scale)
    img.save(out)
    print(f"  rendered {out} ({img.width}x{img.height}, {len(preview)} sprites)")
    return out


# ---------------------------------------------------------------------------
# Map 10 injection (optional)
# ---------------------------------------------------------------------------

def write_into_map10(villages):
    """Append the generated villages to Map 10 of the build FIXED.DAT.

    This does NOT rebuild from scratch — it loads the current build artifact and
    adds the village items. Run build_all_maps.py separately for a clean rebuild.
    """
    build_fixed = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))),
        "shared", "build", "FIXED.DAT")
    arch = MapArchive(build_fixed)
    before = arch.get_map_count(10)
    for items in villages:
        arch.add_items(10, items)
    arch.save(build_fixed)
    after = arch.get_map_count(10)
    print(f"Map 10: {before} -> {after} items (+{after - before}); "
          f"wrote {build_fixed}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="inject villages into shared/build/FIXED.DAT Map 10")
    args = ap.parse_args()

    reader = GlobReader()

    print("Generating villages (fully automated)...")
    # Hoskuld = larger clan with a central hall; Gunnar = smaller, no hall.
    hoskuld = generate_clan_village("hoskuld", (5376, 6912), 0x405CA1, reader,
                                    target_houses=6, bounds=(2304, 2304),
                                    ring_radius=1792, with_hall=True)
    gunnar = generate_clan_village("gunnar", (12800, 6912), 0x6A77A2, reader,
                                   target_houses=5, bounds=(1792, 1792),
                                   ring_radius=1280, with_hall=False)

    print("\nRendering previews...")
    render(hoskuld, reader, "/tmp/lv_hoskuld.png")
    render(gunnar, reader, "/tmp/lv_gunnar.png")

    if args.write:
        print("\nWriting into Map 10...")
        write_into_map10([hoskuld, gunnar])
    else:
        print("\n(preview only — rerun with --write to inject into Map 10)")


if __name__ == "__main__":
    main()

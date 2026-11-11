#!/usr/bin/env python3
"""
building_prefab.py — APPROACH 1: PREFAB LIBRARY.

Stamp REAL base-game buildings into Lost Vale maps instead of hand-placing
tiles. Each prefab is a rectangular region lifted out of a base-game map
(Tenebrae and the surrounding settlements), normalized so its NW corner sits
at the origin, and cached. Stamping it returns a fresh list of MapItems
translated to a destination — pure and repeatable, so the same prefab can be
dropped many times across a village.

SHARED INTERFACE CONTRACT ("Stampable"):
    name: str                # e.g. "tenebrae_longhouse_red"
    footprint: (w, h)        # world-unit bbox after normalization
    tags: list[str]          # ["longhouse","red-roof","norse",...]
    origin_z: int            # base z the structure expects (0 = ground level)
    def stamp(self, dest_x, dest_y, z_base=0) -> list[MapItem]

Z is preserved exactly during normalization: Tenebrae walls live at negative z
(they sink into the ground), floors at z=0, roofs at z>0. So origin_z is 0 for
every prefab here (the floor/ground reference plane), and stamp() shifts the
whole structure by z_base for destination terrain that is not at world-z 0.

Run it:
    cd agents/map-populator/src && python3 building_prefab.py
produces /tmp/prefab_catalog.png (contact sheet) + /tmp/prefab_<name>.png.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageFont

from u8_map import MapArchive, MapItem
from iso_render import IsoRenderer

# ---------------------------------------------------------------------------
# Paths + shared base archive (loaded once, lazily)
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
BASE_FIXED = os.path.join(
    BASE_DIR, "shared", "data", "u8-install", "STATIC", "FIXED.DAT")

# Special "shapes" that are gameplay eggs, not sprites — never copy these into
# a prefab (a stray teleport/monster egg would fire in the new map).
#   2 = glob egg, 73 = standard egg, 500 = monster egg, 508 = teleport egg
SKIP_SHAPES = frozenset({2, 73, 500, 508})

_ARCHIVE = None


def base_archive():
    """Return the shared base-game MapArchive, loading it on first use."""
    global _ARCHIVE
    if _ARCHIVE is None:
        if not os.path.exists(BASE_FIXED):
            raise FileNotFoundError(
                f"base FIXED.DAT not found at {BASE_FIXED} — provide the "
                f"extracted Ultima 8 game data (see CLAUDE.md).")
        _ARCHIVE = MapArchive(BASE_FIXED)
    return _ARCHIVE


# ---------------------------------------------------------------------------
# Region extraction + normalization (promoted from build_shape_gallery.py)
# ---------------------------------------------------------------------------

def extract_region(archive, map_num, rx, ry, rw, rh, skip_special=True):
    """Extract all items whose anchor falls inside a rectangle of a map.

    Promotes build_shape_gallery._extract_region. ``skip_special`` drops glob
    and gameplay-egg shapes so a prefab is pure scenery.
    """
    region = []
    for it in archive.get_map_items(map_num):
        if skip_special and it.shape in SKIP_SHAPES:
            continue
        if rx <= it.x < rx + rw and ry <= it.y < ry + rh:
            region.append(it)
    return region


def normalize(region):
    """Shift a region so min(x)=0 and min(y)=0; preserve z exactly.

    Returns ``(items, footprint)`` where footprint = (max_x, max_y) measured on
    the normalized anchor positions (world units).
    """
    if not region:
        return [], (0, 0)

    src_x = min(it.x for it in region)
    src_y = min(it.y for it in region)

    items = [MapItem(x=it.x - src_x, y=it.y - src_y, z=it.z,
                     shape=it.shape, frame=it.frame,
                     quality=it.quality, flags=it.flags)
             for it in region]

    max_x = max(it.x for it in items)
    max_y = max(it.y for it in items)
    return items, (max_x, max_y)


def relocate(items, dest_x, dest_y, z_base=0):
    """Promotes build_shape_gallery._relocate: copy items, add offsets.

    Pure — never mutates the inputs, so a cached prefab can be stamped repeatedly.
    """
    return [MapItem(x=it.x + dest_x, y=it.y + dest_y, z=it.z + z_base,
                    shape=it.shape, frame=it.frame,
                    quality=it.quality, flags=it.flags)
            for it in items]


# ---------------------------------------------------------------------------
# BuildingPrefab — the Stampable
# ---------------------------------------------------------------------------

class BuildingPrefab:
    """A normalized, cached region of a base-game map, ready to stamp."""

    def __init__(self, name, source_map, bbox, tags=None, origin_z=0,
                 keep_shapes=None):
        self.name = name
        self.source_map = source_map
        self.bbox = tuple(bbox)            # (x, y, w, h) in the source map
        self.tags = list(tags or [])
        self.origin_z = origin_z
        # keep_shapes: optional structural-shape whitelist. A rectangular bbox
        # sweeps in a building's neighbours/ground clutter and clips its roof;
        # use a generous bbox to capture the WHOLE roof, then whitelist only the
        # building's wall+roof shapes to drop loose furniture, editor markers,
        # terrain, and stray props (the "furniture outside / roof gap" defects).
        self.keep_shapes = frozenset(keep_shapes) if keep_shapes else None

        region = extract_region(base_archive(), source_map, *self.bbox)
        if self.keep_shapes is not None:
            region = [it for it in region if it.shape in self.keep_shapes]
        self._items, self.footprint = normalize(region)
        self.item_count = len(self._items)

    def stamp(self, dest_x, dest_y, z_base=0, shape_remap=None):
        """Return copies positioned with the NW corner at (dest_x, dest_y).

        Items are normalized to z_base by subtracting origin_z (the source
        terrain z-level) so that z_base=0 always means "sit on the ground".
        Source maps with elevated terrain (e.g. Map 37 at z=64) need
        origin_z set to their terrain level so items don't float.

        shape_remap: optional dict {old_shape_id: new_shape_id}.
        """
        items = relocate(self._items, dest_x, dest_y, z_base - self.origin_z)
        if shape_remap:
            items = [MapItem(x=it.x, y=it.y, z=it.z,
                             shape=shape_remap.get(it.shape, it.shape),
                             frame=it.frame,
                             quality=it.quality, flags=it.flags)
                     for it in items]
        return items

    def __repr__(self):
        return (f"BuildingPrefab({self.name!r}, map={self.source_map}, "
                f"n={self.item_count}, footprint={self.footprint})")


# ---------------------------------------------------------------------------
# REGISTRY — curated rustic-Norse-village prefabs, each visually QA'd
# ---------------------------------------------------------------------------
# Source maps surveyed: 39 (Tenebrae core — richest), 41 (Tenebrae), 40
# (Tenebrae hub), 37 (large outdoor settlement). Maps 40/37 mostly use dark
# flat roofs that read poorly; map 39 holds the brown/red clay-roofed buildings
# that match the LV target aesthetic (screen19 Zealan village).

REGISTRY = [
    # --- Seeds reused from build_shape_gallery (verified extractions) ---
    BuildingPrefab(
        "stone_ruin_corner", 39, (16700, 18700, 1200, 1200),
        tags=["stone", "ruin", "wall", "medium", "norse"]),
    BuildingPrefab(
        "red_hall_manor", 41, (18752, 12096, 2048, 2048),
        tags=["hall", "manor", "red-roof", "large", "norse"]),

    # --- Roofed buildings (the clay-roof Norse aesthetic) ---
    BuildingPrefab(
        "longhouse_red", 39, (15487, 9343, 960, 1470),
        tags=["longhouse", "cottage", "red-roof", "large", "norse"],
        # 412/410=clay roof, 118/148/647/648=timber frame, 145=door frame
        # Excludes shape 203 (chest) and 752 (tiny prop) — keep structure only.
        keep_shapes={412, 410, 118, 148, 145, 647, 648}),
    BuildingPrefab(
        "longhouse_forge", 39, (16511, 15999, 1470, 1470),
        tags=["longhouse", "workshop", "red-roof", "large", "norse"]),
    BuildingPrefab(
        "great_hall_grey", 39, (17023, 2687, 1470, 960),
        tags=["hall", "civic", "grey-roof", "large", "cupola"]),
    BuildingPrefab(
        "hut_small_red", 37, (14600, 2030, 620, 660),
        tags=["hut", "cottage", "red-roof", "small", "norse"],
        # Map 37 terrain sits at z=64; origin_z normalises items to ground-level
        # (z=0) when stamped with z_base=0 on maps with flat z=0 terrain.
        origin_z=64,
        # generous bbox captures the full roof (incl. north eaves); whitelist
        # keeps only wall(556)+roof(412/410/426/427/24/20/526/118/255), dropping
        # editor pillars, terrain, mushrooms and loose urns around it.
        keep_shapes={556, 412, 410, 426, 427, 24, 20, 526, 118, 255}),

    # --- Open / detail structures ---
    BuildingPrefab(
        "stone_yard", 41, (19967, 14847, 620, 620),
        tags=["enclosure", "yard", "pen", "fence", "stone", "small"]),
    BuildingPrefab(
        "stone_house", 39, (14879, 7711, 920, 560),
        tags=["house", "stone", "furnished", "medium"]),
    BuildingPrefab(
        "market_stall", 40, (11820, 6800, 290, 420),
        tags=["stall", "market", "detail", "small"]),
    BuildingPrefab(
        "stone_wall_ruin", 37, (7951, 3167, 235, 650),
        tags=["wall", "fence", "gateway", "ruin", "stone", "detail"]),

]


def get_prefabs(tag=None):
    """Return REGISTRY, optionally filtered to prefabs carrying ``tag``."""
    if tag is None:
        return list(REGISTRY)
    return [p for p in REGISTRY if tag in p.tags]


# ---------------------------------------------------------------------------
# Visual QA: per-prefab PNGs + a labeled contact sheet
# ---------------------------------------------------------------------------

def _font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:           # very old Pillow
        return ImageFont.load_default()


def render_prefab(prefab, renderer=None, scale=2):
    """Render one prefab (stamped at the origin) to a PIL RGB image."""
    renderer = renderer or IsoRenderer()
    return renderer.render(prefab.stamp(0, 0), scale=scale)


def build_contact_sheet(prefabs, path, cols=4, thumb=(300, 240)):
    """Render every prefab and tile them into one labeled grid PNG."""
    renderer = IsoRenderer()
    tw, th = thumb
    cellw, cellh = tw + 16, th + 46
    rows = (len(prefabs) + cols - 1) // cols

    sheet = Image.new("RGB", (cols * cellw, rows * cellh), (18, 18, 26))
    draw = ImageDraw.Draw(sheet)
    name_font = _font(15)
    meta_font = _font(12)

    for i, p in enumerate(prefabs):
        img = renderer.render(p.stamp(0, 0), scale=1)
        s = min(tw / img.width, th / img.height, 1.0)
        if s < 1.0:
            img = img.resize((max(1, int(img.width * s)),
                              max(1, int(img.height * s))), Image.NEAREST)
        r, c = divmod(i, cols)
        cx, cy = c * cellw + 8, r * cellh + 6
        sheet.paste(img, (cx + (tw - img.width) // 2,
                          cy + (th - img.height) // 2))
        draw.text((cx, cy + th + 4), p.name, fill=(255, 235, 130),
                  font=name_font)
        meta = (f"M{p.source_map}  n={p.item_count}  "
                f"fp={p.footprint[0]}x{p.footprint[1]}")
        draw.text((cx, cy + th + 24), meta, fill=(160, 170, 200),
                  font=meta_font)

    sheet.save(path)
    return path


# ---------------------------------------------------------------------------
# CLI / self-test
# ---------------------------------------------------------------------------

def _print_table():
    print(f"{'name':<18} {'map':>3} {'bbox (x,y,w,h)':<24} "
          f"{'items':>5} {'footprint':>11}  tags")
    print("-" * 100)
    for p in REGISTRY:
        bbox = f"{p.bbox[0]},{p.bbox[1]},{p.bbox[2]},{p.bbox[3]}"
        fp = f"{p.footprint[0]}x{p.footprint[1]}"
        print(f"{p.name:<18} {p.source_map:>3} {bbox:<24} "
              f"{p.item_count:>5} {fp:>11}  {','.join(p.tags)}")
    print("-" * 100)
    print(f"{len(REGISTRY)} prefabs, "
          f"{sum(p.item_count for p in REGISTRY)} items total")


def main():
    out_dir = "/tmp"
    _print_table()

    renderer = IsoRenderer()
    print("\nWriting per-prefab PNGs...")
    for p in REGISTRY:
        img = renderer.render(p.stamp(0, 0), scale=2)
        path = os.path.join(out_dir, f"prefab_{p.name}.png")
        img.save(path)
        print(f"  {path}  ({img.width}x{img.height})")

    catalog = os.path.join(out_dir, "prefab_catalog.png")
    build_contact_sheet(REGISTRY, catalog)
    print(f"\nContact sheet: {catalog}")


if __name__ == "__main__":
    main()

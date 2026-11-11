#!/usr/bin/env python3
"""
glob_catalog.py — Discover which GLOB.FLX prefabs are BUILDINGS.

APPROACH 2 (GLOB-NATIVE) of the Lost Vale map-populator. The U8 engine's native
building block is the GLOB: a prefab cluster of items stored in GLOB.FLX. A
"glob egg" (shape 2) in FIXED.DAT tells the engine to stamp the whole cluster at
runtime. We already use globs for ground terrain; this module finds the globs
that are *structures* (walls + roofs at height) so we can place whole buildings
with a single egg.

What this module provides
-------------------------
- GlobReader     : parse GLOB.FLX; expand a glob into world-space MapItems.
- GlobPrefab     : a Stampable wrapper around one glob index.
- classify_globs : feature-extract + label every non-empty glob.
- build_catalog  : write /tmp/glob_catalog.json + a /tmp/glob_buildings.png
                   contact sheet of the top building candidates.

Coordinate scale (VERIFIED, not assumed)
----------------------------------------
From the engine itself — GlobEgg::enterFastArea() in
scummvm-lv/engines/ultima/ultima8/world/glob_egg.cpp (the U8, non-Crusader
branch: coordmask=~0x1FF, coordshift=1, offset=1):

    itemx = (_x & ~0x1FF) + (globitem.x << 1) + 1
    itemy = (_y & ~0x1FF) + (globitem.y << 1) + 1
    itemz =  _z          +  globitem.z

So x/y offsets are scaled by 2 (then +1), but z is added DIRECTLY (scale 1) —
a NON-uniform scale that a "uniform 1/2/4" guess would get wrong. The egg's x/y
is masked to its 512-unit chunk, so a glob fills exactly one chunk (max offset
255 -> 255*2+1 = 511). Visual calibration (glob 1454 rendered at x/y scales
1/2/4 with z fixed) confirms it: scale 2 yields a coherent multi-story stone
building; scale 1 overlaps the floor tiles, scale 4 blows them apart with gaps.

Glob record format (VERIFIED against all 2129 non-empty entries; matches
map-format.md and MapGlob::read): uint16 itemcount, then itemcount * 6 bytes of
{x:u8, y:u8, z:u8, shape:u16le, frame:u8}. Entry size == 2 + itemcount*6.
Of the 2129 non-empty FLX entries, 616 are zero-item placeholders (size 2), so
1513 globs actually contain items.

Shape semantics come from STATIC/TYPEFLAG.DAT (SI_LAND/SI_SEA = ground,
SI_ROOF = roof, solid + tall z-footpad = wall/pillar) augmented by the hand-
identified shape sets in shape_viewer.py. Roof-flagged tiles (e.g. 9, 220, 412)
double as floor tiles, so a tile only counts as a "roof" when its item sits
above ground level (z > ROOF_Z_MIN).
"""

import os
import sys
import json
import struct
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from u8_flex import FlexArchive
from u8_map import MapItem
from iso_render import IsoRenderer
from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))  # .../lost-vale
STATIC_DIR = os.path.join(BASE_DIR, "shared", "data", "u8-install", "STATIC")
GLOB_FLX = os.path.join(STATIC_DIR, "GLOB.FLX")
TYPEFLAG_DAT = os.path.join(STATIC_DIR, "TYPEFLAG.DAT")

CATALOG_JSON = "/tmp/glob_catalog.json"
CONTACT_SHEET = "/tmp/glob_buildings.png"

# ---------------------------------------------------------------------------
# Engine-verified coordinate transform (see module docstring)
# ---------------------------------------------------------------------------
XY_SHIFT = 1          # globitem.x/y << 1  (== * 2)
XY_OFFSET = 1         # ... + 1
CHUNK_MASK = ~0x1FF   # egg x/y snapped to its 512-unit chunk
# z is added directly: world_z = egg_z + globitem.z  (scale 1)

# ---------------------------------------------------------------------------
# Hand-identified shape sets (from shape_viewer.py SHAPE_GROUPS); these augment
# the TYPEFLAG.DAT-derived classification.
# ---------------------------------------------------------------------------
ROOF_SHAPES = {412, 162, 164, 271}
WALL_SHAPES = {622, 690, 691}
PILLAR_SHAPES = {148, 155, 301, 302, 303, 304, 305}
DOOR_SHAPES = {174, 68, 69, 114, 505, 288}
GROUND_SHAPES = {9, 220}

# A roof-flagged tile only counts as a roof when lifted above ground level
# (world z; z scale is 1, so this is in world units).
ROOF_Z_MIN = 8
# Minimum world z-spread for a wall/roof cluster to read as a real structure.
BUILDING_Z_SPREAD = 16


# ===========================================================================
# TYPEFLAG.DAT — per-shape physics/role flags
# ===========================================================================
class ShapeFlags:
    """Reader for STATIC/TYPEFLAG.DAT (2048 shapes x 8 bytes, no header).

    Robust to a missing file: get() then returns None and callers fall back to
    the hand-identified shape sets above.
    """

    def __init__(self, path=TYPEFLAG_DAT):
        self._data = b""
        if os.path.exists(path):
            with open(path, "rb") as f:
                self._data = f.read()

    def get(self, shape):
        o = shape * 8
        if o + 8 > len(self._data):
            return None
        b = self._data[o:o + 8]
        return {
            "land": bool(b[0] & 0x08),
            "sea": bool(b[0] & 0x04),
            "solid": bool(b[0] & 0x02),
            "occl": bool(b[0] & 0x10),
            "roof": bool(b[1] & 0x04),
            "family": b[1] >> 4,
            "xfoot": b[2] >> 4,
            "yfoot": b[3] & 0x0F,
            "zfoot": b[3] >> 4,
        }


def shape_role(shape, z, sf):
    """Classify one glob item into a structural role.

    z is the item's world z (== glob z offset, scale 1). Priority order matters:
    doors first, then elevated roofs, then vertical structure (walls/pillars),
    then flat ground, else 'other'.
    """
    info = sf.get(shape)

    if shape in DOOR_SHAPES:
        return "door"

    is_roof_shape = shape in ROOF_SHAPES or (info and info["roof"])
    if is_roof_shape and z > ROOF_Z_MIN:
        return "roof"

    if shape in WALL_SHAPES or shape in PILLAR_SHAPES:
        return "wall"
    if info and info["solid"] and info["zfoot"] >= 3 \
            and not info["land"] and not info["roof"]:
        return "wall"

    if shape in GROUND_SHAPES or (info and (info["land"] or info["sea"])
                                  and info["zfoot"] <= 1):
        return "ground"

    return "other"


# ===========================================================================
# GLOB.FLX reader
# ===========================================================================
class GlobReader:
    """Parse GLOB.FLX and expand globs into world-space MapItems."""

    def __init__(self, glob_flx_path=None):
        if glob_flx_path is None:
            built = os.path.join(BASE_DIR, 'shared', 'build', 'GLOB.FLX')
            glob_flx_path = built if os.path.exists(built) else GLOB_FLX
        self.flx = FlexArchive(glob_flx_path)
        self.count = self.flx.count

    def get_glob(self, index):
        """Return the glob's items as dicts {x,y,z,shape,frame} (raw offsets).

        Empty / zero-item / out-of-range entries return []."""
        try:
            data = self.flx.get_object(index)
        except IndexError:
            return []
        if not data or len(data) < 2:
            return []
        itemcount = struct.unpack_from("<H", data, 0)[0]
        if 2 + itemcount * 6 > len(data):
            itemcount = (len(data) - 2) // 6
        items = []
        for k in range(itemcount):
            o = 2 + k * 6
            items.append({
                "x": data[o],
                "y": data[o + 1],
                "z": data[o + 2],
                "shape": struct.unpack_from("<H", data, o + 3)[0],
                "frame": data[o + 5],
            })
        return items

    def glob_to_items(self, index, dest_x, dest_y, z_base=0):
        """Expand a glob into placed MapItems, faithfully replicating the engine
        transform from GlobEgg::enterFastArea() (x/y *2 +1 within the dest's
        512-chunk; z added directly)."""
        base_x = dest_x & CHUNK_MASK
        base_y = dest_y & CHUNK_MASK
        items = []
        for g in self.get_glob(index):
            ix = base_x + (g["x"] << XY_SHIFT) + XY_OFFSET
            iy = base_y + (g["y"] << XY_SHIFT) + XY_OFFSET
            iz = z_base + g["z"]
            items.append(MapItem.placed_item(ix, iy, iz, g["shape"], g["frame"]))
        return items

    def non_empty_indices(self):
        """Indices of globs that actually contain at least one item."""
        return [i for i in range(self.count) if self.get_glob(i)]


# ===========================================================================
# GlobPrefab — Stampable wrapper around one glob index
# ===========================================================================
class GlobPrefab:
    """Stampable adapter for a single glob.

    Conforms to the shared 'Stampable' contract: .name, .footprint (w,h world
    units), .tags, .origin_z, .stamp(dx,dy,z_base) -> [MapItem].

    .stamp() returns a single glob egg (the engine expands the cluster at
    runtime). .expand() returns the full item list for PREVIEW rendering.
    Because the engine masks the egg to its 512-chunk, footprint is at most one
    chunk (~512 world units) on each axis.
    """

    def __init__(self, reader, index, tags=None, name=None):
        self.reader = reader
        self.index = index
        self.tags = list(tags) if tags else []
        self.name = name or f"glob_{index}"
        glob = reader.get_glob(index)
        if glob:
            maxx = max(g["x"] for g in glob)
            maxy = max(g["y"] for g in glob)
            self.footprint = ((maxx << XY_SHIFT) + XY_OFFSET,
                              (maxy << XY_SHIFT) + XY_OFFSET)
            self.min_item_z = min(g["z"] for g in glob)
        else:
            self.footprint = (0, 0)
            self.min_item_z = 0

        # H7. origin_z is the Stampable contract's "terrain level this
        # structure expects", and for a glob that is ALWAYS 0: the engine
        # renders each item at `egg.z + item.z`, so a glob's internal z
        # values are authored relative to the egg, and the egg's z IS the
        # destination terrain datum. The base game demonstrates both halves —
        # it places globs 49/51 at egg z=48 and glob 65 at 8/48/56, varying
        # the egg with the ground under it, while placing all six house globs
        # (573/575/538/537/1007/1011) at egg z=0.
        #
        # This used to be `min(item z)`, which is a different quantity: the
        # lowest item in the cluster. For the two-storey house globs that is
        # 40 — their ground-floor plate (shape 286, an 8x8 SI_LAND slab) —
        # and it is a DESIGNED raised floor, not a grounding offset. Verified
        # against the base game: glob 573 sits on Tenebrae terrain whose
        # LAND items are at z=0/8, with its own plate at 40. Treating 40 as
        # the datum made `generate_village` (which passes each prefab's
        # origin_z as z_base) stamp the egg at 40, so those four houses
        # rendered 40 units higher than the identical glob does in Tenebrae,
        # while 1007/1011 (min_item_z 0) were unaffected — hence the
        # inconsistent village heights.
        self.origin_z = 0

    def _egg_z(self, z_base):
        """The z the egg must carry to sit on terrain at z_base.

        `z_base - origin_z`, exactly mirroring BuildingPrefab's relocation —
        and since a glob's origin_z is 0 (see __init__), that is z_base
        itself. Written as the subtraction anyway so both Stampables read the
        same and the contract is one rule, not two special cases.
        """
        egg_z = z_base - self.origin_z
        if not (0 <= egg_z <= 255):
            raise ValueError(
                f"glob {self.index}: terrain z_base {z_base} gives an egg z "
                f"of {egg_z}, outside the 0..255 the engine can read (the "
                f"egg's z is an UNSIGNED byte, so a negative would wrap to "
                f"{egg_z & 0xFF} and hoist the structure toward the ceiling)")
        return egg_z

    def stamp(self, dest_x, dest_y, z_base=0):
        """Return the placement marker; the engine stamps the cluster.

        Per the Stampable contract, z_base is the TERRAIN level the structure
        is being placed on — the same meaning BuildingPrefab.stamp() gives
        it. Note this is not the same as the height of the structure's lowest
        item: a glob may carry a designed raised floor (see min_item_z).
        """
        return [MapItem.glob_egg(dest_x, dest_y, self._egg_z(z_base),
                                 self.index)]

    def expand(self, dest_x, dest_y, z_base=0):
        """Return the full expanded item list (for preview rendering).

        Uses the same egg z as stamp(), so a preview shows what the engine
        will actually draw for the equivalent stamp().
        """
        return self.reader.glob_to_items(self.index, dest_x, dest_y,
                                         self._egg_z(z_base))

    def __repr__(self):
        return (f"GlobPrefab(#{self.index}, footprint={self.footprint}, "
                f"tags={self.tags})")


# ===========================================================================
# Classification
# ===========================================================================
def classify_globs(reader, sf=None):
    """Feature-extract and label every non-empty glob.

    Returns a list of records (dicts) sorted by descending building score.
    Each record: index, label, score, itemcount, zspread, distinct_shapes,
    roofs, walls, doors, ground, shapes, tags.
    """
    sf = sf or ShapeFlags()
    records = []

    for idx in range(reader.count):
        glob = reader.get_glob(idx)
        if not glob:
            continue

        n = len(glob)
        zs = [g["z"] for g in glob]
        zspread = max(zs) - min(zs)  # world units (z scale == 1)

        roles = Counter(shape_role(g["shape"], g["z"], sf) for g in glob)
        n_roof = roles["roof"]
        n_wall = roles["wall"]
        n_door = roles["door"]
        n_ground = roles["ground"]
        n_struct = n_roof + n_wall + n_door
        shapes = sorted({g["shape"] for g in glob})

        # Building-likelihood score (interpretable, monotone; arbitrary scale).
        score = n_door * 10 + n_wall * 5 + n_roof * 4 + min(zspread, 160) * 0.5
        if n_struct == 0:
            score -= n_ground  # ground-only clusters drift toward 0
        score = round(max(0.0, score), 1)

        ground_frac = n_ground / n

        # Label.
        if (((n_wall + n_roof) > 0 and zspread >= BUILDING_Z_SPREAD)
                or n_wall >= 6
                or (n_door > 0 and n_struct > 1)):
            label = "building"
        elif ground_frac >= 0.6 and zspread < BUILDING_Z_SPREAD and n_struct == 0:
            label = "terrain"
        else:
            label = "prop/other"

        tags = [label]
        if n_roof:
            tags.append("roof")
        if n_wall:
            tags.append("wall")
        if n_door:
            tags.append("door")
        if label != "building" and n_ground:
            tags.append("ground")

        records.append({
            "index": idx,
            "label": label,
            "score": score,
            "itemcount": n,
            "zspread": zspread,
            "distinct_shapes": len(shapes),
            "roofs": n_roof,
            "walls": n_wall,
            "doors": n_door,
            "ground": n_ground,
            "shapes": shapes,
            "tags": tags,
        })

    records.sort(key=lambda r: r["score"], reverse=True)
    return records


def make_prefab(reader, record):
    """Build a GlobPrefab from a classification record (carries its tags)."""
    return GlobPrefab(reader, record["index"], tags=record["tags"])


# ===========================================================================
# Contact sheet
# ===========================================================================
def build_contact_sheet(reader, records, out_path=CONTACT_SHEET,
                        top_n=40, cols=5, cell=(232, 248), label_h=20):
    """Render the top building candidates into a labeled grid PNG for review."""
    buildings = [r for r in records if r["label"] == "building"][:top_n]
    if not buildings:
        Image.new("RGB", (400, 80), (20, 20, 28)).save(out_path)
        return out_path, 0

    rend = IsoRenderer()
    cw, ch = cell
    rows = (len(buildings) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw, rows * (ch + label_h)), (18, 18, 26))
    draw = ImageDraw.Draw(sheet)

    for i, r in enumerate(buildings):
        cx = (i % cols) * cw
        cy = (i // cols) * (ch + label_h)
        try:
            items = reader.glob_to_items(r["index"], 0, 0, 0)
            img = rend.render(items, scale=1)
            img.thumbnail((cw - 8, ch - 8), Image.NEAREST)
            ox = cx + (cw - img.width) // 2
            oy = cy + (ch - img.height) // 2
            sheet.paste(img, (ox, oy))
        except Exception as exc:  # never let one bad glob kill the sheet
            draw.text((cx + 6, cy + ch // 2), f"render err\n{exc}",
                      fill=(200, 90, 90))
        draw.text(
            (cx + 4, cy + ch + 4),
            f"#{r['index']}  s={r['score']:.0f}  z={r['zspread']} "
            f"w{r['walls']} r{r['roofs']} d{r['doors']} n{r['itemcount']}",
            fill=(232, 210, 120),
        )

    sheet.save(out_path)
    return out_path, len(buildings)


# ===========================================================================
# Catalog driver
# ===========================================================================
def build_catalog(reader=None, sf=None,
                  json_path=CATALOG_JSON, png_path=CONTACT_SHEET):
    """Classify all globs, write the JSON catalog and the building contact
    sheet. Returns (records, json_path, png_path)."""
    reader = reader or GlobReader()
    sf = sf or ShapeFlags()
    records = classify_globs(reader, sf)

    catalog = [{
        "index": r["index"],
        "label": r["label"],
        "score": r["score"],
        "itemcount": r["itemcount"],
        "zspread": r["zspread"],
        "roofs": r["roofs"],
        "walls": r["walls"],
        "doors": r["doors"],
        "ground": r["ground"],
        "shapes": r["shapes"],
    } for r in records]
    with open(json_path, "w") as f:
        json.dump(catalog, f, indent=1)

    png_path, n_rendered = build_contact_sheet(reader, records, png_path)
    return records, json_path, png_path


# ===========================================================================
# CLI
# ===========================================================================
def main():
    reader = GlobReader()
    sf = ShapeFlags()
    records, json_path, png_path = build_catalog(reader, sf)

    counts = Counter(r["label"] for r in records)
    buildings = [r for r in records if r["label"] == "building"]

    print(f"GLOB.FLX: {GLOB_FLX}")
    print(f"  FLX entries: {reader.count}  |  non-empty (with items): {len(records)}")
    print(f"  catalog JSON : {json_path}")
    print(f"  contact sheet: {png_path}")
    print()
    print("Labels:")
    for label in ("building", "terrain", "prop/other"):
        print(f"  {label:11s}: {counts.get(label, 0)}")
    print()
    print(f"Top 25 BUILDING candidates (index : score  z-spread  walls/roofs/doors  items):")
    for r in buildings[:25]:
        print(f"  glob {r['index']:4d} : {r['score']:6.1f}   "
              f"z={r['zspread']:3d}   "
              f"w{r['walls']:<2d} r{r['roofs']:<2d} d{r['doors']:<2d}   "
              f"n={r['itemcount']}")


if __name__ == "__main__":
    main()

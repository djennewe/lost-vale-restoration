#!/usr/bin/env python3
"""
map_validate.py — Sanity checks for placed MapItems in a built FIXED.DAT.

Catches the class of bugs that produce garbage rendering or broken
collision/depth-sort in ScummVM: bad frame indices, shapes with no FLX
entry, all-zero TYPEFLAG metadata, and monster-egg encoding (M12).

Usage:
    from map_validate import validate_items, validate_map_module
    issues = validate_items(items, mapnum=10)

CLI:
    python3 map_validate.py [--fixed path/to/FIXED.DAT] [--maps 8,9,10,11,13,17,18]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from u8_flex import FlexArchive
from u8_map import MapArchive
from shape_viewer import parse_shape_frames
from parse_typeflag import load_typeflag

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

# Effective U8SHAPES.FLX: prefer the shared build (has custom injected
# shapes 856-858), fall back to the base game copy.
SHAPES_FLX_BUILD = os.path.join(BASE_DIR, "shared", "build", "U8SHAPES.FLX")
SHAPES_FLX_BASE = os.path.join(BASE_DIR, "shared", "data", "u8-install", "STATIC", "U8SHAPES.FLX")

DEFAULT_FIXED = os.path.join(BASE_DIR, "shared", "build", "FIXED.DAT")
DEFAULT_LV_MAPS = [8, 9, 10, 11, 13, 17, 18]

Z_WARN_THRESHOLD = 200


def effective_shapes_path():
    """Return the effective U8SHAPES.FLX path: prefer the build copy."""
    if os.path.exists(SHAPES_FLX_BUILD):
        return SHAPES_FLX_BUILD
    return SHAPES_FLX_BASE


# Effective TYPEFLAG.DAT, the same rule. Until 2026-10-11 the TYPEFLAG side
# always read the install copy, which is the PREVIOUS install's artifact (or
# the base), never this build's: a new actor shape (872, the Water Zombie)
# then read as family 0 and every egg hatching it warned.
TYPEFLAG_BUILD = os.path.join(BASE_DIR, "shared", "build", "TYPEFLAG.DAT")


def effective_typeflag_path():
    """Return the effective TYPEFLAG.DAT path: prefer the build copy."""
    if os.path.exists(TYPEFLAG_BUILD):
        return TYPEFLAG_BUILD
    return None        # load_typeflag's own default, the install copy



class ShapeCache:
    """Lazily parses U8SHAPES.FLX ONCE and caches frame counts per shape."""

    def __init__(self, shapes_path=None):
        self.shapes_path = shapes_path or effective_shapes_path()
        self._flx = FlexArchive(self.shapes_path)
        self._frame_counts = {}  # shape_id -> frame count (cached)

    def exists(self, shape_id):
        """True if the shape has a non-empty FLX entry."""
        if shape_id < 0 or shape_id >= self._flx.count:
            return False
        return self._flx.exists(shape_id)

    def frame_count(self, shape_id):
        """Number of frames for shape_id, or 0 if the shape doesn't exist
        or fails to parse."""
        if shape_id in self._frame_counts:
            return self._frame_counts[shape_id]
        count = 0
        if self.exists(shape_id):
            data = self._flx.get_object(shape_id)
            if data:
                frames = parse_shape_frames(data)
                count = len(frames)
        self._frame_counts[shape_id] = count
        return count


class TypeflagCache:
    """Lazily loads TYPEFLAG.DAT ONCE and answers is_empty queries."""

    def __init__(self, path=None):
        self._shapes = load_typeflag(path or effective_typeflag_path())

    def is_empty(self, shape_id):
        if shape_id < 0 or shape_id >= len(self._shapes):
            return True
        return self._shapes[shape_id].is_empty

    def family(self, shape_id):
        """TYPEFLAG family nibble (6 = monster/actor), or None if OOR."""
        if shape_id < 0 or shape_id >= len(self._shapes):
            return None
        return self._shapes[shape_id].family


# Module-level singletons, built lazily on first use so importing this
# module doesn't require the data files to exist unless validation runs.
_shape_cache = None
_typeflag_cache = None


def _get_shape_cache():
    global _shape_cache
    if _shape_cache is None:
        _shape_cache = ShapeCache()
    return _shape_cache


def _get_typeflag_cache():
    global _typeflag_cache
    if _typeflag_cache is None:
        _typeflag_cache = TypeflagCache()
    return _typeflag_cache


def _is_egg(item):
    """Eggs encode data (glob index, teleport id, monster quality, etc.)
    in the shape/frame/quality fields — they must be exempt from
    shape/frame validity checks."""
    return (item.is_glob_egg or item.is_teleport_egg or item.is_monster_egg
            or item.is_teleport_target or item.is_teleporter)


def _issue(level, mapnum, item, msg):
    return {
        "level": level,
        "mapnum": mapnum,
        "shape": item.shape,
        "frame": item.frame,
        "x": item.x,
        "y": item.y,
        "z": item.z,
        "msg": msg,
    }


# ---------------------------------------------------------------------------
# Placement checks: floor support + the "avatar surrounded by blackness"
# rule (2026-07-02, from in-game QA on Map 8).
#
# Two real failure modes these catch:
#  - items / teleport points with NO floor under them (the LV door ensemble
#    was once placed on a wall RIDGE at z=48: the avatar stood on the wall,
#    stuck, and nothing was reachable);
#  - teleport destinations / loot placed on floor that renders PURE BLACK
#    (base-game "shadow floor" plates like shape 564): mechanically fine,
#    but on screen everything there floats in a void.
# ---------------------------------------------------------------------------

# LV teleport IDs are 200-213 (base game uses 0-105); dest eggs store 256+id.
_LV_TELE_IDS = set(range(200, 214))

_black_shape_cache = {}


def _shape_renders_black(shape_id, frame=0):
    """True if the shape's art for THIS frame is essentially pure black
    (mean brightness of opaque pixels < 26/255). Frame-aware: e.g. shadow
    plate 564 has a dark-gray frame 0 but pure-black frames 2-6, and maps
    place the black ones. Cached per (shape, frame)."""
    key = (shape_id, frame)
    if key in _black_shape_cache:
        return _black_shape_cache[key]
    result = False
    try:
        from iso_render import frame_to_rgba
        from shape_viewer import load_palette, PALETTE_FILE
        cache = _get_shape_cache()
        data = cache._flx.get_object(shape_id) if cache.exists(shape_id) else None
        frames = parse_shape_frames(data) if data else []
        if frames:
            f = frames[frame] if frame < len(frames) else frames[0]
            palette = load_palette(PALETTE_FILE)
            img, _xoff, _yoff = frame_to_rgba(f, palette)
            total = n = 0
            if img is not None:
                for px in img.getdata():
                    if px[3] > 0:
                        total += px[0] + px[1] + px[2]
                        n += 1
            result = n > 0 and (total / (3.0 * n)) < 26
    except Exception:
        result = False
    _black_shape_cache[key] = result
    return result


def _is_lv_teleport(item):
    if item.is_teleport_target:
        return item.quality in _LV_TELE_IDS
    if item.is_teleporter:
        return (item.quality - 256) in _LV_TELE_IDS
    return False


def _build_floor_index(items, typeflag_cache):
    """LAND-flagged items (globs expanded) as (x, y, z, half_x, half_y,
    shape) tuples. Footprint half-extent = footpad_cells * 16 world units
    (one footpad cell = 32 units, origin at the item center)."""
    expanded = items
    try:
        from glob_catalog import GlobReader
        gr = GlobReader()
        out = []
        for it in items:
            if it.is_glob_egg:
                out.extend(gr.glob_to_items(it.quality, it.x, it.y, it.z))
            else:
                out.append(it)
        expanded = out
    except Exception:
        pass

    shapes = typeflag_cache._shapes
    floor = []
    for it in expanded:
        if it.shape < 0 or it.shape >= len(shapes):
            continue
        si = shapes[it.shape]
        # LAND = walkable ground; SEA = water surface (props on water are
        # visible, if questionable — that's a design call, not blackness)
        if si.has_flag('SI_LAND') or si.has_flag('SI_SEA'):
            floor.append((it.x, it.y, it.z,
                          max(16, si.footpad_x * 16),
                          max(16, si.footpad_y * 16),
                          it.shape, it.frame))
    return floor


def _support_under(floor, x, y, z):
    """Topmost LAND/SEA item covering (x, y) at or below z, or None.
    Ties at equal z go to the LATER item in the list: items appended later
    (e.g. LV paving slabs over base shadow plates) draw on top in-engine."""
    best = None
    for fx, fy, fz, hx, hy, fshape, fframe in floor:
        if fz <= z and abs(x - fx) <= hx and abs(y - fy) <= hy:
            if best is None or fz >= best[0]:
                best = (fz, fshape, fframe)
    return best


def validate_placement(items, mapnum, typeflag_cache=None):
    """Floor-support and blackness checks for gameplay-critical placements:
    LV teleport eggs (ids 200-213) and SF_QUALITY / SF_CONTAINER items.

    WARN: nothing walkable under the placement (floating in a void or on
          missing terrain — e.g. the tracked Map 17 cloud-glob gap). Kept
          at WARN, not ERROR, while known terrain deficiencies exist;
          escalate to ERROR once Map 17/13 terrain is complete.
    WARN: the supporting floor renders pure black (shadow plates): works
          mechanically but reads as a void on screen. Pave it (rock slabs,
          shape 301) or move the placement.

    Items in the off-map staging margin (x or y < 64) are skipped — the
    base game parks usecode-spawned stock there.
    """
    if typeflag_cache is None:
        typeflag_cache = _get_typeflag_cache()

    shapes = typeflag_cache._shapes
    check = []
    for it in items:
        if it.x < 64 or it.y < 64:
            continue  # off-map staging
        if _is_lv_teleport(it):
            check.append((it, 'LV teleport'))
        elif not _is_egg(it) and 0 <= it.shape < len(shapes):
            info = shapes[it.shape]
            fam = info.family_name
            # A wall-hung fixture (zero footpad in x or y, above the floor:
            # the gold plaques 599/614 on Map 17) needs no floor under it,
            # and at a room's edge the anchor-as-centre box below reaches
            # the void plate beyond the wall. Nothing stands on it and
            # nothing picks it up, so there is no support to check.
            if (it.z > 0 and 'SI_FIXED' in info.flag_names
                    and (info.footpad_x == 0 or info.footpad_y == 0)):
                continue
            # A fixed LAND piece is ground, not a placement on it: retail's
            # 735 (family SF_QUALITY, SI_FIXED|SI_SOLID|SI_LAND, a 320x320
            # dark slab, map 5) is its own floor, and the support search
            # found the piece itself (screen14's 1994 skull ring floor,
            # Map 13, 2026-10-17).
            if ('SI_FIXED' in info.flag_names
                    and 'SI_LAND' in info.flag_names):
                continue
            if fam in ('SF_QUALITY', 'SF_CONTAINER'):
                check.append((it, fam))
    if not check:
        return []

    floor = _build_floor_index(items, typeflag_cache)
    issues = []
    for it, why in check:
        sup = _support_under(floor, it.x, it.y, it.z)
        if sup is None:
            iss = _issue(
                "WARN", mapnum, it,
                f"no floor support under {why} placement — floating in a "
                f"void or on missing terrain; avatar/loot may be "
                f"unreachable or invisible")
            # Stable machine-readable tag (M10). An LV teleport endpoint with
            # no floor is the progression-breaking case (you arrive falling
            # into a void), so build_all_maps ratchets on the COUNT of these
            # rather than matching on message text.
            if why == 'LV teleport':
                iss["code"] = "LV_TELEPORT_NO_FLOOR"
            issues.append(iss)
        elif _shape_renders_black(sup[1], sup[2]):
            issues.append(_issue(
                "WARN", mapnum, it,
                f"{why} placement sits on pure-black floor (shape "
                f"{sup[1]} frame {sup[2]}) — reads as a void on screen; "
                f"pave with rock slabs (301) or relocate"))
    return issues


def validate_items(items, mapnum, shape_cache=None, typeflag_cache=None):
    """Validate a list of MapItems belonging to a single map.

    Returns a list of issue dicts:
        {level: 'ERROR'|'WARN', mapnum, shape, frame, x, y, z, msg}

    Checks, in priority order:
      1. ERROR: frame index >= actual frame count for the shape
      2. ERROR: shape id has no FLX entry at all
      3. WARN: shape's TYPEFLAG entry is all-zero

    Egg items (glob/teleport/monster eggs) are exempt from the
    shape/frame checks (1 & 2) since they encode data, not visuals, in
    those fields — but are still checked for z-ceiling issues.
    """
    if shape_cache is None:
        shape_cache = _get_shape_cache()
    if typeflag_cache is None:
        typeflag_cache = _get_typeflag_cache()

    issues = []

    for item in items:
        is_egg = _is_egg(item)

        if not is_egg:
            if not shape_cache.exists(item.shape):
                issues.append(_issue(
                    "ERROR", mapnum, item,
                    f"shape {item.shape} has no U8SHAPES.FLX entry"))
            else:
                frame_count = shape_cache.frame_count(item.shape)
                if item.frame >= frame_count:
                    issues.append(_issue(
                        "ERROR", mapnum, item,
                        f"frame {item.frame} out of range for shape "
                        f"{item.shape} ({frame_count} frames)"))

                if typeflag_cache.is_empty(item.shape):
                    issues.append(_issue(
                        "WARN", mapnum, item,
                        f"shape {item.shape} has an all-zero TYPEFLAG entry "
                        f"(depth-sort/collision may misbehave)"))

        # M12: a monster egg (shape 500) packs (prob<<11)|monster_shape into
        # quality. If the low 11 bits don't name a monster-family (6) actor,
        # or prob is 0, the egg spawns garbage/terrain or never hatches — the
        # exact silent breakage that left the harpie zone and elemental
        # sections empty. WARN (not ERROR): the base game itself ships a few
        # intentional prob=0 / shape=0 dormant eggs, so this must not gate.
        if item.is_monster_egg:
            mon_shape = item.quality & 0x7FF
            prob = (item.quality >> 11) & 0x1F
            fam = typeflag_cache.family(mon_shape)
            if mon_shape != 0 and fam != 6:
                issues.append(_issue(
                    "WARN", mapnum, item,
                    f"monster egg spawns shape {mon_shape} (TYPEFLAG family "
                    f"{fam}, not monster family 6) — likely terrain/garbage, "
                    f"nothing meaningful hatches"))
            if prob == 0 and mon_shape != 0:
                issues.append(_issue(
                    "WARN", mapnum, item,
                    f"monster egg has prob=0 (quality 0x{item.quality:04X}) — "
                    f"it will never hatch"))

        # NOTE (H4): there is deliberately no "z near the unsigned ceiling"
        # WARN here. z is unsigned to the engine, but the base game
        # legitimately places 6,229 items (552 on Map 8 alone) at z > 200,
        # so a post-serialization z threshold cannot tell an LV grounding
        # bug from ordinary base data — it only floods. The genuine LV
        # signal is a builder passing NEGATIVE z (which serializes to a
        # ceiling byte); that is caught pre-serialization in
        # build_all_maps.py, where base items (already unsigned) can't be
        # confused for it.

    # 5+6. Floor-support (WARN) and blackness (WARN) checks for
    # gameplay-critical placements — see validate_placement().
    issues.extend(validate_placement(items, mapnum, typeflag_cache))

    return issues


def validate_map_module(items, mapnum):
    """Convenience wrapper for use by build_all_maps.py or similar
    in-process callers: validates one map's items using the shared
    module-level caches (parsed once, reused across calls)."""
    return validate_items(items, mapnum)


def format_report(all_issues):
    """Format a list of issue dicts (from one or more maps) into a
    readable multi-line report string."""
    lines = []
    if not all_issues:
        lines.append("No issues found.")
        return "\n".join(lines)

    by_map = {}
    for issue in all_issues:
        by_map.setdefault(issue["mapnum"], []).append(issue)

    error_count = sum(1 for i in all_issues if i["level"] == "ERROR")
    warn_count = sum(1 for i in all_issues if i["level"] == "WARN")

    for mapnum in sorted(by_map):
        map_issues = by_map[mapnum]
        lines.append(f"Map {mapnum}: {len(map_issues)} issue(s)")
        for issue in map_issues:
            lines.append(
                f"  [{issue['level']}] shape={issue['shape']} "
                f"frame={issue['frame']} pos=({issue['x']},{issue['y']},"
                f"{issue['z']}) — {issue['msg']}")

    lines.append("")
    lines.append(f"Total: {error_count} ERROR(s), {warn_count} WARN(s)")
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate placed items in a built FIXED.DAT")
    parser.add_argument("--fixed", default=DEFAULT_FIXED,
                        help=f"Path to FIXED.DAT (default: {DEFAULT_FIXED})")
    parser.add_argument("--maps", default=None,
                        help="Comma-separated map numbers to validate "
                             f"(default: {','.join(str(m) for m in DEFAULT_LV_MAPS)})")
    args = parser.parse_args()

    if not os.path.exists(args.fixed):
        print(f"ERROR: FIXED.DAT not found at {args.fixed}")
        sys.exit(1)

    if args.maps:
        map_nums = [int(m.strip()) for m in args.maps.split(",") if m.strip()]
    else:
        map_nums = DEFAULT_LV_MAPS

    shapes_path = effective_shapes_path()
    print(f"Using shapes: {shapes_path}")
    print(f"Validating FIXED.DAT: {args.fixed}")
    print(f"Maps: {map_nums}")
    print()

    archive = MapArchive(args.fixed)
    shape_cache = ShapeCache(shapes_path)
    typeflag_cache = TypeflagCache()

    all_issues = []
    for mapnum in map_nums:
        items = archive.get_map_items(mapnum)
        if not items:
            print(f"Map {mapnum}: no items (empty or missing)")
            continue
        issues = validate_items(items, mapnum, shape_cache, typeflag_cache)
        all_issues.extend(issues)

    print(format_report(all_issues))

    error_count = sum(1 for i in all_issues if i["level"] == "ERROR")
    sys.exit(1 if error_count else 0)


if __name__ == "__main__":
    main()

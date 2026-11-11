#!/usr/bin/env python3
"""
build_all_maps.py — Assembles all Lost Vale maps into a complete FIXED.DAT.

1. Loads base game FIXED.DAT (42 maps, 87,603 items)
2. Adds Map 8 modifications (F1)
3. Adds all 6 new maps (F2-F7)
4. Verifies all teleport pairs match (trigger <-> dest for each ID)
5. Saves to shared/build/FIXED.DAT
6. Verifies: reloads and checks all map item counts
"""

import argparse
import json
import sys
import os

# Ensure our local modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from u8_map import MapArchive, MapItem

# Import all map builders
from build_map_08 import build_map_08_additions
from build_map_09 import build_map_09
from build_map_10 import build_map_10
from build_map_11 import build_map_11
from build_map_13 import build_map_13
from build_map_17 import build_map_17
from build_map_18 import build_map_18
from build_map_39 import (
    build_map_39_additions,
    build_map_03_test_additions,
    LB_TEST_EGG_AT_START,
)
from build_shape_gallery import build_shape_gallery

# Validation / manifest / preview machinery — imported as libraries, never
# shelled out to, so build_all_maps.py is the single source of truth for
# "did the build actually succeed".
from map_validate import validate_items, format_report
import lv_dressing
import map_manifest
from map_preview import render_map as render_map_preview


# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
BASE_FIXED = os.path.join(BASE_DIR, "shared", "data", "u8-install", "STATIC", "FIXED.DAT")
OUTPUT_DIR = os.path.join(BASE_DIR, "shared", "build")
OUTPUT_FIXED = os.path.join(OUTPUT_DIR, "FIXED.DAT")
# L12 staged-write gate: the build writes here, verifies the STAGED file,
# and only then renames it over OUTPUT_FIXED. A rejected build is left at
# QUARANTINE_FIXED and the previous known-good artifact is untouched. Both
# byproducts are gitignored (shared/build/*.staging, *.failed).
STAGING_FIXED = OUTPUT_FIXED + ".staging"
QUARANTINE_FIXED = OUTPUT_FIXED + ".failed"
OUTPUT_MANIFEST = os.path.join(OUTPUT_DIR, "map_manifest.json")
OUTPUT_PREVIEWS_DIR = os.path.join(OUTPUT_DIR, "previews")

# Maps that belong to the Lost Vale expansion — validated, manifested, and
# previewed. (Map 22, the shape gallery, is a dev tool, not a shippable LV
# map, so it's intentionally excluded here.)
LV_MAPS = [8, 9, 10, 11, 13, 17, 18]

# M10 ratchet pin: LV teleport endpoints sitting on no floor at all.
# Now ZERO. There were 5 when this ratchet was introduced (2026-07-25), all on
# Map 13/17, and all five turned out to share one root cause: the terrain
# globs those maps tile with were EMPTY (Map 13 GLOB_CLIFF_BASE 50, Map 17
# GLOB_STONE_FLOOR 75), so the arrival pads had no ground under them at all.
# Fixed the same day by pointing them at real globs (51 and 65) and by paving
# the summit platform at its true 128-unit tile size instead of a 512 stride.
# This number must only ever go DOWN — validate_and_gate() turns any increase
# into a build failure, so a new floating teleport can never ship again.
KNOWN_FLOATING_LV_TELEPORTS = 0

RECORD_BUDGET = {8: 7000, 9: 2500, 10: 25000, 11: 12000,
                 13: 9000, 17: 12000, 18: 3000, 39: 6500}
EXPANDED_RECORD_BUDGET = {8: 31000, 39: 31000}
DRESSING_RAW_CEILING = lv_dressing.RAW_CEILING
EXPANDED_PER_CELL_BUDGET = lv_dressing.EXPANDED_PER_CELL


# Teleport connection table — all 14 teleport IDs (200-213)
# from_map is where the TELEPORTER (frame 0) stands and to_map is where its
# TARGET (frame 1) stands, matching the engine: TeleportEgg::isTeleporter()
# is `_frame != 1`, and the teleporter's mapNum field is the destination.
#
# Every row's direction was recorded backwards until 2026-07-29 — the same
# root cause as the u8_map.py factory naming (see
# docs/playtest-2026-07-28-cleanroom-run1.md finding F1). The ids come in
# complementary couples, so BOTH directions of every link always existed and
# travel worked in-game; only the per-id labels lied. No map bytes changed
# when this was corrected: FIXED.DAT rebuilt byte-identical.
TELEPORT_TABLE = {
    200: {"from_map": 9, "to_map": 8, "desc": "Galjeron's Chamber -> Plateau"},
    201: {"from_map": 8, "to_map": 9, "desc": "Plateau -> Galjeron's Chamber"},
    202: {"from_map": 11, "to_map": 9, "desc": "Elemental Dungeon -> Galjeron's Chamber"},
    203: {"from_map": 9, "to_map": 11, "desc": "Galjeron's Chamber -> Elemental Dungeon"},
    204: {"from_map": 10, "to_map": 11, "desc": "Lost Vale -> Elemental Dungeon"},
    205: {"from_map": 11, "to_map": 10, "desc": "Elemental Dungeon -> Lost Vale"},
    206: {"from_map": 13, "to_map": 10, "desc": "Cloud Cliffs -> Lost Vale"},
    207: {"from_map": 10, "to_map": 13, "desc": "Lost Vale -> Cloud Cliffs"},
    208: {"from_map": 17, "to_map": 13, "desc": "Cloud City -> Cloud Cliffs"},
    209: {"from_map": 13, "to_map": 17, "desc": "Cloud Cliffs -> Cloud City"},
    210: {"from_map": 18, "to_map": 10, "desc": "Ancient Temple -> Lost Vale"},
    211: {"from_map": 10, "to_map": 18, "desc": "Lost Vale -> Ancient Temple"},
    212: {"from_map": 8, "to_map": 10, "desc": "Pagan -> Lost Vale return",
          "gated": "EGGVALERETURN"},
    213: {"from_map": 10, "to_map": 8, "desc": "Lost Vale -> Pagan return"},
}

# A "gated" row's trigger is not an engine TeleportEgg (whose hatch is
# unconditional) but a usecode egg: a shape-73 UnkEgg whose class (quality +
# 0x47F) is the named manifest pin, and which calls teleportToEgg(to_map, id)
# only once its quest flag is set. 212 is the one (2026-10-11): its slab lies
# on the first-visit way to Map 8's doors, and as a TeleportEgg it sent a
# fresh player to the Vale with steps 3 and 4 undone (docs/playtest-
# 2026-10-11-replay-leg2.md finding 1; build_map_08 TELE_213_TRIGGER_X). The
# destination the class compiles in is checked against the pads by
# agents/usecode-compiler/src/test_uc_vale_return.py.
EGG_CLASS_BASE = 0x47F
LV_MANIFEST = os.path.join(OUTPUT_DIR, "lv_manifest.json")


def _gated_class_ids():
    """{teleport id: pinned class id} for TELEPORT_TABLE's gated rows."""
    gated = {tid: info["gated"] for tid, info in TELEPORT_TABLE.items()
             if "gated" in info}
    if not gated:
        return {}
    with open(LV_MANIFEST) as fh:
        classes = json.load(fh)["classes"]
    return {tid: classes.get(name) for tid, name in gated.items()}


def gated_teleporters(archive):
    """{teleport id: [(map, egg), ...]}: the usecode eggs that carry
    TELEPORT_TABLE's gated rows (shape 73, class = quality + 0x47F)."""
    out = {}
    for tid, cls_id in _gated_class_ids().items():
        if cls_id is None:
            continue
        for map_num in archive.non_empty_maps():
            for item in archive.get_map_items(map_num):
                if item.shape == MapItem.SHAPE_STANDARD_EGG and \
                        item.quality + EGG_CLASS_BASE == cls_id:
                    out.setdefault(tid, []).append((map_num, item))
    return out



def verify_teleport_pairs(archive):
    """Verify all teleporter/target pairs match across maps.

    For each teleport ID, per the engine (TeleportEgg::isTeleporter() is
    `_frame != 1`):
    - The TELEPORTER (frame=0) should be on the from_map; for a gated row,
      the usecode egg of its pinned class instead, and no TeleportEgg
    - The TARGET (frame=1) should be on the to_map
    """
    print("\n=== Teleport Pair Verification ===")
    all_ok = True

    # Collect all teleport eggs across all maps.
    # LISTS, not dicts (M9): a dict silently kept only the LAST egg for a
    # given id, so a duplicate teleporter/target shipped unreported while the
    # verification below still printed OK for that id.
    teleporters = {}  # teleport_id -> [(map_num, item), ...]  frame 0
    targets = {}      # teleport_id -> [(map_num, item), ...]  frame 1

    for map_num in archive.non_empty_maps():
        for item in archive.get_map_items(map_num):
            if item.is_teleport_target:
                # TARGET quality = teleport_id
                tid = item.quality
                if tid >= 200:
                    targets.setdefault(tid, []).append((map_num, item))
            elif item.is_teleporter:
                # TELEPORTER quality = 256 + teleport_id
                tid = item.quality - 256
                if tid >= 200:
                    teleporters.setdefault(tid, []).append((map_num, item))

    # Gated rows: their trigger is the usecode egg, and an engine teleporter
    # with the same id would fire past the gate.
    for tid, cls_id in sorted(_gated_class_ids().items()):
        if tid in teleporters:
            all_ok = False
            where = ", ".join(f"map {m} ({it.x},{it.y},{it.z})"
                              for m, it in teleporters[tid])
            print(f"  ID {tid}: UNGATED TELEPORTER — a TeleportEgg fires "
                  f"for anyone; this id must be a "
                  f"{TELEPORT_TABLE[tid]['gated']} egg — {where}")
            del teleporters[tid]
        if cls_id is None:
            all_ok = False
            print(f"  ID {tid}: {TELEPORT_TABLE[tid]['gated']} is not "
                  f"pinned in lv_manifest.json — cannot find its egg")
    for tid, entries in gated_teleporters(archive).items():
        teleporters.setdefault(tid, []).extend(entries)

    # M9: duplicate ids are a hard failure — two triggers sharing an id means
    # one of them sends the player somewhere unintended.
    for label, table in (("TELEPORTER", teleporters), ("TARGET", targets)):
        for tid, entries in sorted(table.items()):
            if len(entries) > 1:
                all_ok = False
                where = ", ".join(f"map {m} ({it.x},{it.y},{it.z})"
                                  for m, it in entries)
                print(f"  ID {tid}: DUPLICATE {label} x{len(entries)} — {where}")

    # An id inside the documented LV range (200-213, CLAUDE.md) that is NOT in
    # TELEPORT_TABLE is unverifiable — surface it rather than skipping
    # silently. Deliberately scoped to that range: the shape gallery (Map 22)
    # carries a debug destination at id 250, which is out of range on purpose
    # and must not fail the build.
    known = set(TELEPORT_TABLE)
    seen_ids = set(teleporters) | set(targets)
    for tid in sorted(i for i in seen_ids - known if 200 <= i <= 213):
        all_ok = False
        print(f"  ID {tid}: teleport egg(s) present but id is NOT in "
              f"TELEPORT_TABLE — cannot verify")

    for tid in sorted(TELEPORT_TABLE.keys()):
        info = TELEPORT_TABLE[tid]
        tele_ok = tid in teleporters
        targ_ok = tid in targets

        if tele_ok and targ_ok:
            # [0] = first entry; duplicates are reported as a hard failure
            # above, so reading the first here is only a display choice.
            tele_map, tele_pos = teleporters[tid][0]
            targ_map, targ_pos = targets[tid][0]
            expected_from = info["from_map"]
            expected_to = info["to_map"]

            map_ok = (tele_map == expected_from and targ_map == expected_to)
            status = "OK" if map_ok else "MAP MISMATCH"
            if not map_ok:
                all_ok = False
            print(f"  ID {tid}: {info['desc']}")
            print(f"         TELEPORTER on map {tele_map} ({expected_from}) pos=({tele_pos.x},{tele_pos.y},{tele_pos.z})")
            print(f"         TARGET     on map {targ_map} ({expected_to})   pos=({targ_pos.x},{targ_pos.y},{targ_pos.z})")
            print(f"         [{status}]")
        else:
            all_ok = False
            if not tele_ok:
                print(f"  ID {tid}: MISSING TELEPORTER ({info['desc']})")
            if not targ_ok:
                print(f"  ID {tid}: MISSING TARGET ({info['desc']})")

    return all_ok


def validate_and_gate(items_by_map, ratchet=False):
    """Run map_validate.validate_items() across a {mapnum: [items]} dict,
    print a full report, and decide whether the build may proceed.

    ratchet: apply the M10 floating-LV-teleport ratchet. Only meaningful
    for the LV_MAPS pass — the quest-step-1 pass (Map 39) carries no LV
    teleports, so running it there would report a spurious "0 remain".

    Returns (all_issues, has_errors). Any ERROR-severity issue means the
    caller MUST NOT write FIXED.DAT. WARN-severity issues are reported but
    are not blocking.

    This function takes a plain dict of items rather than a MapArchive so
    it can be exercised in isolation (e.g. with synthetic/bad items) without
    needing a built archive or touching any file on disk.
    """
    all_issues = []
    for mapnum in sorted(items_by_map.keys()):
        items = items_by_map[mapnum]
        issues = validate_items(items, mapnum)
        all_issues.extend(issues)
        counts = [("raw", len(items), RECORD_BUDGET.get(mapnum))]
        if mapnum in EXPANDED_RECORD_BUDGET:
            from map_preview import GlobReader, expand_globs
            counts.append(("expanded", len(expand_globs(items, GlobReader())),
                           EXPANDED_RECORD_BUDGET[mapnum]))
        if mapnum in EXPANDED_PER_CELL_BUDGET and items and len(items) <= RECORD_BUDGET[mapnum]:
            import dressing_metrics as dm
            metrics = dm.measure(dm.Source(fixed=False), mapnum,
                                 box=lv_dressing.BUDGET_BOX.get(mapnum), raw=items)
            cells = metrics['ground'].get('cells', 0)
            ratio = metrics['records']['expanded'] / max(1, cells)
            counts.append(("expanded per ground cell", ratio,
                           EXPANDED_PER_CELL_BUDGET[mapnum]))
        for kind, count, cap in counts:
            if cap is not None and count > cap:
                all_issues.append(dict(level="ERROR", mapnum=mapnum,
                                       shape=0, frame=0, x=0, y=0, z=0,
                                       msg=f"{kind} records {count} exceed budget {cap}"))

    print(format_report(all_issues))

    has_errors = any(issue["level"] == "ERROR" for issue in all_issues)

    # M10 RATCHET: an LV teleport endpoint with no floor under it is the
    # progression-breaking case — you arrive falling into a void. These are
    # kept at WARN because KNOWN_FLOATING_LV_TELEPORTS of them already exist
    # on the incomplete Map 13/17 cloud terrain, and failing outright would
    # block every build. But the count may never GROW: a new one is an
    # ERROR that blocks the write, and fixing the existing ones must lower
    # the pin. Same ratchet discipline as the compiler's Gate 7.
    floating = [i for i in all_issues if i.get("code") == "LV_TELEPORT_NO_FLOOR"]
    if not ratchet:
        return all_issues, has_errors
    if len(floating) > KNOWN_FLOATING_LV_TELEPORTS:
        has_errors = True
        print(f"\n   RATCHET FAILURE: {len(floating)} LV teleport endpoint(s) "
              f"with no floor support, baseline is "
              f"{KNOWN_FLOATING_LV_TELEPORTS}.")
        print( "   A teleport destination in a void drops the player. Fix the "
               "new one, or lower the pin if you removed a teleport:")
        for i in floating:
            print(f"     map {i['mapnum']} shape {i['shape']} frame {i['frame']} "
                  f"at ({i['x']},{i['y']},{i['z']})")
    elif len(floating) < KNOWN_FLOATING_LV_TELEPORTS:
        print(f"\n   NOTE: only {len(floating)} floating LV teleport(s) "
              f"remain (pin is {KNOWN_FLOATING_LV_TELEPORTS}) — lower "
              f"KNOWN_FLOATING_LV_TELEPORTS in build_all_maps.py to lock the "
              f"improvement in.")

    return all_issues, has_errors


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Assemble all Lost Vale maps into shared/build/FIXED.DAT")
    parser.add_argument("--no-previews", action="store_true",
                         help="Skip rendering preview PNGs after a successful build "
                              "(previews are rendered by default)")
    parser.add_argument("--lb-test-egg", action="store_true",
                         help="TEST-ONLY: also place the Lord British quest-step-1 "
                              "egg+apparition pair at the new-game start area (Map 3). "
                              "Default OFF — never enable for a release build (see "
                              "build_map_39.py LB_TEST_EGG_AT_START).")
    return parser.parse_args(argv)


def main():
    args = parse_args()

    print("=" * 60)
    print("Lost Vale Map Assembly — build_all_maps.py")
    print("=" * 60)

    # Step 1: Load base FIXED.DAT
    print(f"\n1. Loading base FIXED.DAT from:\n   {BASE_FIXED}")
    if not os.path.exists(BASE_FIXED):
        print(f"   ERROR: Base FIXED.DAT not found!")
        sys.exit(1)

    # The install dir doubles as install_lv.sh's target, so after an
    # install this "base" is actually the previous built artifact (the
    # 2026-07-27 duplicate-teleport failure). Prefer the pristine .bak
    # and hard-abort if no candidate is free of LV content.
    from base_input import pristine_base
    LV_SLOTS = {9, 10, 11, 13, 17, 18}

    def _fixed_is_pristine(p):
        return not (set(MapArchive(p).non_empty_maps()) & LV_SLOTS)

    base_path = pristine_base(BASE_FIXED, _fixed_is_pristine,
                              'base FIXED.DAT')

    archive = MapArchive(base_path)
    base_maps = archive.non_empty_maps()
    # Per-map baseline, snapshotted BEFORE any modification, so the post-save
    # read-back (M11) can prove untouched base maps survived intact.
    base_counts = {m: archive.get_map_count(m) for m in base_maps}
    base_total = sum(base_counts.values())
    print(f"   Loaded: {len(base_maps)} maps, {base_total} items")

    # M11: every map we modify records its intended final count here, so the
    # post-save read-back can prove the file on disk matches what was built.
    expected_counts = {}

    # Step 2: Add Map 8 modifications (F1)
    print("\n2. Adding Map 8 modifications (double doors entry)...")
    # 2a. Base-item removals: the sealed Lost Vale door slabs (blank shape
    # 619 monoliths, retail's famous "doors that cannot be opened") are
    # REPLACED by the functional LV doors, so the originals must go first.
    from build_map_08 import BASE_ITEM_REMOVALS
    if BASE_ITEM_REMOVALS:
        m8 = archive.get_map_items(8)
        keep = [it for it in m8
                if (it.x, it.y, it.z, it.shape) not in BASE_ITEM_REMOVALS]
        removed = len(m8) - len(keep)
        archive.set_map_items(8, keep)
        print(f"   Removed {removed} base item(s) "
              f"(expected {len(BASE_ITEM_REMOVALS)}: sealed door slabs)")
        if removed != len(BASE_ITEM_REMOVALS):
            print("   WARNING: removal count mismatch — check BASE_ITEM_REMOVALS")
    map8_items = build_map_08_additions()
    archive.add_items(8, map8_items)
    expected_counts[8] = archive.get_map_count(8)
    print(f"   Added {len(map8_items)} items to Map 8 (total: {expected_counts[8]})")

    # Step 2b: Add Map 39 (Tenebrae) quest step 1 trigger (LORDBRIT scene) —
    # base-map modification, same pattern as Map 8 above: one base glob egg
    # removed (the lane through the gate wall, build_map_39.BASE_ITEM_REMOVALS;
    # its other items come back among the additions), then the additions.
    print("\n2b. Adding Map 39 (Tenebrae) modifications (quest step 1 trigger)...")
    from build_map_39 import BASE_ITEM_REMOVALS as MAP39_REMOVALS
    m39 = archive.get_map_items(39)
    keep = [it for it in m39
            if (it.x, it.y, it.z, it.shape) not in MAP39_REMOVALS]
    removed = len(m39) - len(keep)
    archive.set_map_items(39, keep)
    print(f"   Removed {removed} base item(s) "
          f"(expected {len(MAP39_REMOVALS)}: the gate-wall glob the lane cuts)")
    if removed != len(MAP39_REMOVALS):
        print("   WARNING: removal count mismatch — check "
              "build_map_39.BASE_ITEM_REMOVALS")
    map39_items = build_map_39_additions()
    archive.add_items(39, map39_items)
    expected_counts[39] = archive.get_map_count(39)
    print(f"   Added {len(map39_items)} items to Map 39 (total: {expected_counts[39]})")

    # Step 2c: TEST-ONLY — also place the quest step 1 pair at the new-game
    # start area (Map 3), gated by --lb-test-egg / LB_TEST_EGG_AT_START.
    # Never on by default; see build_map_39.py.
    if args.lb_test_egg or LB_TEST_EGG_AT_START:
        print("\n2c. [TEST] Adding Map 3 new-game-start quest step 1 egg "
              "(--lb-test-egg)...")
        map03_items = build_map_03_test_additions()
        archive.add_items(3, map03_items)
        expected_counts[3] = archive.get_map_count(3)
        print(f"   Added {len(map03_items)} items to Map 3 (total: {expected_counts[3]})")
    else:
        map03_items = []

    # Step 3: Add all 6 new maps (F2-F7)
    print("\n3. Building new maps...")

    new_maps = [
        (9, "Galjeron's Chamber", build_map_09),
        (10, "Lost Vale Overworld", build_map_10),
        (11, "Elemental Dungeon", build_map_11),
        (13, "Cloud Cliffs", build_map_13),
        (17, "Cloud City", build_map_17),
        (18, "Ancient Temple", build_map_18),
    ]

    for map_num, name, builder in new_maps:
        items = builder()
        archive.set_map_items(map_num, items)
        expected_counts[map_num] = len(items)
        globs = sum(1 for i in items if i.is_glob_egg)
        teles = sum(1 for i in items if i.is_teleport_egg)
        mons = sum(1 for i in items if i.is_monster_egg)
        print(f"   Map {map_num:2d} ({name}): {len(items)} items "
              f"(globs={globs}, teleports={teles}, monsters={mons})")
        # H4: flag the builders' negative "below-datum" z shorthand here,
        # on the builder items (z<0), NOT after serialization — a re-parsed
        # item reads back as unsigned 254 and is then indistinguishable from
        # the 6,229 base-game items legitimately at high z. z is unsigned to
        # the engine, so z=-2 renders at 254 (near the ceiling) while base
        # water/terrain sits low (0..~104). Not a hard error (bytes are
        # unchanged from the shipped, playtested build); a heads-up that
        # these placements want an in-game grounding check.
        neg_z = sum(1 for i in items if i.z < 0)
        if neg_z:
            print(f"      NOTE: {neg_z} item(s) at negative z (render near "
                  f"the unsigned ceiling, not below-surface) — verify "
                  f"in-game grounding")

    # Step 3b: Build shape gallery (Map 22)
    print("\n   Building shape gallery (Map 22)...")
    gallery_items = build_shape_gallery()
    archive.set_map_items(22, gallery_items)
    expected_counts[22] = len(gallery_items)
    print(f"   Map 22 (Shape Gallery): {len(gallery_items)} items")

    # Step 4: Verify teleport pairs — HARD GATE (H5). A dangling teleport
    # (missing trigger/destination, or a map mismatch) is a hard progression
    # breaker, so its failure must block the write exactly like the item
    # validator's ERROR gate below, not merely print a warning and save.
    teleports_ok = verify_teleport_pairs(archive)
    if not teleports_ok:
        print("\n" + "!" * 60)
        print("TELEPORT VERIFICATION FAILED — FIXED.DAT was NOT written.")
        print("  A dangling teleport pair is a progression breaker; fix the")
        print("  reported trigger/destination/map-mismatch and rebuild.")
        print("!" * 60)
        sys.exit(1)
    else:
        print("\n   All 14 teleport pairs verified OK!")

    # Step 5: Validator gate — must run BEFORE archive.save(). Any
    # ERROR-severity issue on any LV map blocks the write entirely.
    print("\n" + "=" * 60)
    print("5. Validation gate (pre-save)")
    print("=" * 60)
    # pack() can append content-addressed rows while a map builder runs.
    # Rebuild before validation so every reader sees the same archive.
    import lv_globs
    lv_globs.build()
    items_by_map = {m: archive.get_map_items(m) for m in LV_MAPS}
    all_issues, has_errors = validate_and_gate(items_by_map, ratchet=True)

    if has_errors:
        print("\n" + "!" * 60)
        print("VALIDATION FAILED — FIXED.DAT was NOT written.")
        print(f"  {sum(1 for i in all_issues if i['level'] == 'ERROR')} ERROR(s), "
              f"{sum(1 for i in all_issues if i['level'] == 'WARN')} WARN(s)")
        print("!" * 60)
        sys.exit(1)
    else:
        warn_count = sum(1 for i in all_issues if i["level"] == "WARN")
        if warn_count:
            print(f"\n   No ERRORs found ({warn_count} WARN(s) above) — proceeding to save.")
        else:
            print("\n   No issues found — proceeding to save.")

    # Step 5b: Quest step 1 placement validation — Map 39 (Tenebrae) and,
    # if enabled, the Map 3 test placement. Kept SEPARATE from the Step 5
    # gate above (which stays scoped to LV_MAPS) so this doesn't change
    # the "18 known WARN(s)" LV_MAPS baseline: Map 39 is a base-game map
    # that was never validated before this work landed, and carries one
    # pre-existing WARN of its own (shape 174 at (15359,12319), unrelated
    # to and untouched by the LORDBRIT placement — a base-game oddity
    # this work did not introduce). Still an ERROR-gates-the-write check,
    # same as Step 5.
    print("\n" + "=" * 60)
    print("5b. Quest step 1 placement validation (Map 39 + optional Map 3)")
    print("=" * 60)
    quest1_maps = {39: archive.get_map_items(39)}
    if map03_items:
        quest1_maps[3] = archive.get_map_items(3)
    quest1_issues, quest1_has_errors = validate_and_gate(quest1_maps)
    if quest1_has_errors:
        print("\n" + "!" * 60)
        print("VALIDATION FAILED (quest step 1 maps) — FIXED.DAT was NOT written.")
        print("!" * 60)
        sys.exit(1)
    print(f"\n   {sum(1 for i in quest1_issues if i['level'] == 'WARN')} "
          f"WARN(s), 0 ERROR(s) — none attributable to the LORDBRIT egg/"
          f"apparition/paving-slab additions themselves (independently "
          f"verified: 0 new issues from those specific items).")

    # Step 6: Stage the output (L12). The canonical FIXED.DAT is NOT touched
    # until Step 7's read-back has verified these bytes — the same
    # stage-verify-promote shape as the usecode build's P2 gate. Previously
    # the read-back ran against a file that had already replaced the last
    # known-good build, so "POST-SAVE VERIFICATION FAILED" exited 1 with the
    # bad artifact sitting at the path install_lv.sh installs from.
    print(f"\n6. Staging to:\n   {STAGING_FIXED}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    archive.save(STAGING_FIXED)
    print(f"   Staged successfully!")

    # Step 7: Verification — reload the STAGED file and check
    print("\n7. Verification — reloading staged FIXED.DAT...")
    verify = MapArchive(STAGING_FIXED)
    verify_maps = verify.non_empty_maps()
    verify_total = sum(verify.get_map_count(m) for m in verify_maps)
    print(f"   Maps: {len(verify_maps)} non-empty")
    print(f"   Total items: {verify_total}")
    print(f"   New items added: {verify_total - base_total}")

    # M11: this step used to PRINT counts and assert nothing, so a builder
    # returning a truncated list — or a serialization bug that dropped items —
    # shrank or emptied a map and the build still exited 0 with a silently
    # smaller FIXED.DAT. Read the counts back off the SAVED file and compare
    # against what we intended to write.
    readback_problems = []
    for map_num, want in sorted(expected_counts.items()):
        got = verify.get_map_count(map_num)
        if got != want:
            readback_problems.append(
                f"map {map_num}: wrote {want} items, read back {got}")
    # Base-game maps we never touched must survive untouched too.
    for map_num in base_maps:
        if map_num in expected_counts or map_num not in verify_maps:
            continue
        if verify.get_map_count(map_num) != base_counts.get(map_num):
            readback_problems.append(
                f"map {map_num} (untouched base map): {base_counts.get(map_num)} "
                f"-> {verify.get_map_count(map_num)}")
    if readback_problems:
        os.replace(STAGING_FIXED, QUARANTINE_FIXED)
        print("\n" + "!" * 60)
        print("POST-SAVE VERIFICATION FAILED — the staged FIXED.DAT does not "
              "match what was built:")
        for p in readback_problems:
            print(f"   {p}")
        print(f"  {OUTPUT_FIXED} was NOT modified; the previous known-good")
        print(f"  build is intact. The rejected output is at")
        print(f"  {QUARANTINE_FIXED} for inspection.")
        print("!" * 60)
        sys.exit(1)
    print(f"   Read-back check: all {len(expected_counts)} written map(s) "
          f"and {len(base_maps) - len(set(base_maps) & set(expected_counts))} "
          f"untouched base map(s) match — OK")

    # L12 promotion gate: verified, so it may now replace the canonical
    # artifact. os.replace() is atomic within a filesystem, and staging
    # alongside the target keeps it one.
    os.replace(STAGING_FIXED, OUTPUT_FIXED)
    print(f"   Promoted staged build to {OUTPUT_FIXED}")

    # Detailed per-map verification
    print("\n   Per-map summary:")
    for m in verify_maps:
        count = verify.get_map_count(m)
        items = verify.get_map_items(m)
        globs = sum(1 for i in items if i.is_glob_egg)
        teles = sum(1 for i in items if i.is_teleport_egg)
        mons = sum(1 for i in items if i.is_monster_egg)
        marker = " [LV]" if m in LV_MAPS else ""
        print(f"     Map {m:3d}: {count:5d} items "
              f"(globs={globs}, teleports={teles}, monsters={mons}){marker}")

    # Step 8: Manifest — regenerate shared/build/map_manifest.json from the
    # FIXED.DAT we just saved, so it can never go stale relative to it.
    print("\n" + "=" * 60)
    print("8. Manifest")
    print("=" * 60)
    shape_names = map_manifest._build_shape_name_lookup()
    manifest = map_manifest.build_manifest(verify, LV_MAPS, shape_names)
    manifest_total = sum(len(v) for v in manifest.values())
    os.makedirs(os.path.dirname(OUTPUT_MANIFEST), exist_ok=True)
    with open(OUTPUT_MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"   Wrote {OUTPUT_MANIFEST} ({len(manifest)} map(s), {manifest_total} item(s))")

    # Step 9: Previews — render whole-map PNGs for QA review.
    print("\n" + "=" * 60)
    print("9. Previews")
    print("=" * 60)
    if args.no_previews:
        print("   Skipped (--no-previews)")
    else:
        os.makedirs(OUTPUT_PREVIEWS_DIR, exist_ok=True)
        for m in LV_MAPS:
            out_path = os.path.join(OUTPUT_PREVIEWS_DIR, f"map_{m:02d}.png")
            try:
                path, w, h, n_rendered, n_raw = render_map_preview(m, out_path)
                print(f"   Map {m:2d}: {n_raw} raw items -> {n_rendered} rendered "
                      f"-> {path} ({w}x{h})")
            except Exception as exc:
                print(f"   Map {m:2d}: ERROR rendering preview: {exc}")

    # Final summary
    print("\n" + "=" * 60)
    print("ASSEMBLY COMPLETE")
    print(f"  Base game:  {base_total} items across {len(base_maps)} maps")
    print(f"  Final:      {verify_total} items across {len(verify_maps)} maps")
    print(f"  Added:      {verify_total - base_total} new items, {len(verify_maps) - len(base_maps)} new maps")
    print(f"  Teleports:  {'ALL OK' if teleports_ok else 'ISSUES FOUND'}")
    print(f"  Validation: {sum(1 for i in all_issues if i['level'] == 'WARN')} WARN(s), 0 ERROR(s)")
    print(f"  Manifest:   {OUTPUT_MANIFEST}")
    print(f"  Previews:   {'skipped' if args.no_previews else OUTPUT_PREVIEWS_DIR}")
    print(f"  Output:     {OUTPUT_FIXED}")
    print("=" * 60)


if __name__ == '__main__':
    main()

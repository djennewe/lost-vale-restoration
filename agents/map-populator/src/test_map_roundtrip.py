#!/usr/bin/env python3
"""test_map_roundtrip.py — the map pipeline's first automated coverage.

Guards adversarial-review finding H9: zero test files existed anywhere under
map-populator, so `MapItem.to_bytes/from_bytes`, the FIXED.DAT writer, the
validator's rules, and the teleport gate were all proven only by "the build
printed OK". This is the pipeline that already shipped 12 wrong shape
constants and a z-signedness defect.

Coverage:
  1. Item serialization: from_bytes(to_bytes(item)) is byte- and field-
     identical across EVERY record in the base game FIXED.DAT (~87k items),
     plus the signed x/y, unsigned z (H4), and out-of-range edges.
  2. Egg encoders: teleporter/target quality convention, monster-egg
     (prob<<11)|shape packing and its range guards (M12).
  3. Archive round trip: base FIXED.DAT -> save -> reload is item-identical,
     the written file's index table is structurally sound, and save() is
     atomic (L12) — a failed write leaves the previous artifact intact.
  4. Validator rules, driven by deliberately known-bad synthetic items:
     missing shape, out-of-range frame, egg exemption, monster-egg family
     and prob=0 warnings, and the LV_TELEPORT_NO_FLOOR placement check with
     a paved positive control.
  5. Teleport-pair completeness on the SHIPPED FIXED.DAT, plus negative
     controls (missing teleporter, duplicate target, wrong map, id outside
     TELEPORT_TABLE) and the deliberate out-of-range Map 22 gallery id.
  6. The M10 floating-teleport ratchet actually fails a build.

Plain script, no pytest dependency: exit 0 on pass, exit 1 on fail.

    python3 agents/map-populator/src/test_map_roundtrip.py
"""

import contextlib
import io
import os
import struct
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from u8_flex import FlexArchive
from u8_map import MapArchive, MapItem
import map_validate
import build_all_maps as ba

REPO = os.path.abspath(os.path.join(_HERE, '..', '..', '..'))
BASE_FIXED = os.path.join(REPO, 'shared', 'data', 'u8-install',
                          'STATIC', 'FIXED.DAT')
BUILT_FIXED = os.path.join(REPO, 'shared', 'build', 'FIXED.DAT')

REC = MapItem.RECORD_SIZE

# Fixtures, asserted to still have these properties before they are used, so
# a changed U8SHAPES.FLX / TYPEFLAG.DAT turns into a clear failure rather
# than a test that quietly stops testing anything.
SHAPE_MISSING = 2047        # no U8SHAPES.FLX entry
SHAPE_SLAB = 301            # rock slab: exists, SI_LAND, many frames
SHAPE_GHOUL = 142           # TYPEFLAG family 6 (monster) — lv_shapes SHAPE_MON_ZOMBIE

# Ratchet pin (2026-07-25): validator WARNs across LV_MAPS in the shipped
# FIXED.DAT. Currently zero — the Map 13/17 terrain work and the shape
# constant audit cleared the last of them. May only go DOWN.
MAX_KNOWN_WARNS = 0

FIELDS = ('x', 'y', 'z', 'shape', 'frame', 'flags', 'quality',
          'npcnum', 'mapnum', 'next_ptr')


def fields(item):
    return tuple(getattr(item, f) for f in FIELDS)


def _capture(fn, *a, **kw):
    """Run fn with stdout captured; return (result, output)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = fn(*a, **kw)
    return result, buf.getvalue()


# ---------------------------------------------------------------------------
# 1. Item serialization
# ---------------------------------------------------------------------------

def test_item_roundtrip_base_fixed():
    """Every 16-byte record in the base game FIXED.DAT survives
    from_bytes -> to_bytes byte-identically, and re-parses to the same
    fields. This is the whole corpus, not a sample."""
    assert os.path.exists(BASE_FIXED), (
        f"base game FIXED.DAT missing: {BASE_FIXED} — see CLAUDE.md "
        f"(shared/data/u8-install must be populated)")

    flx = FlexArchive(BASE_FIXED)
    total = 0
    ragged = []
    for i, off, size in flx.entries():
        if not size:
            continue
        blob = flx.get_object(i)
        if len(blob) % REC:
            ragged.append((i, len(blob)))
        for pos in range(0, len(blob) - REC + 1, REC):
            want = blob[pos:pos + REC]
            item = MapItem.from_bytes(blob, pos)
            got = item.to_bytes()
            assert got == want, (
                f"map {i} record {pos // REC}: re-serialized to {got.hex()}, "
                f"original {want.hex()}")
            assert fields(MapItem.from_bytes(got)) == fields(item), (
                f"map {i} record {pos // REC}: fields changed on re-parse")
            total += 1

    assert not ragged, (
        f"map blob(s) not a whole number of 16-byte records: {ragged}")
    assert total > 80000, (
        f"only {total} records checked; the base game has ~87.6k — is "
        f"FIXED.DAT truncated?")
    print(f"  PASS  item round trip: {total} base-game records across "
          f"{len(flx)} map slots, all byte- and field-identical")


def test_item_field_edges():
    """Signed x/y, unsigned z (H4), and the serializable-range guard."""
    cases = [
        # (kwargs, expected re-parsed z)
        (dict(x=-32768, y=32767, z=0, shape=65535, frame=255,
              flags=65535, quality=65535, npcnum=255, mapnum=255,
              next_ptr=65535), 0),
        (dict(x=0, y=0, z=255, shape=1), 255),
        (dict(x=1, y=2, z=128, shape=1), 128),
        # The builders' "below datum" shorthand: -2 must land on 254, the
        # byte the shipped, playtested build already contains.
        (dict(x=1, y=2, z=-2, shape=1), 254),
        (dict(x=1, y=2, z=-128, shape=1), 128),
    ]
    for kw, want_z in cases:
        item = MapItem(**kw)
        raw = item.to_bytes()
        assert len(raw) == REC, f"record is {len(raw)} bytes, expected {REC}"
        back = MapItem.from_bytes(raw)
        assert back.z == want_z, (
            f"z={kw['z']} serialized/reparsed as {back.z}, expected {want_z}")
        for f in FIELDS:
            if f == 'z':
                continue
            assert getattr(back, f) == kw.get(f, 0), (
                f"{f} changed: {kw.get(f, 0)} -> {getattr(back, f)}")

    # A z outside [-128, 255] is a computation bug, not either idiom
    for bad_z in (-129, 256, 100000):
        try:
            MapItem(x=100, y=100, z=bad_z, shape=1).to_bytes()
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"z={bad_z} serialized silently instead of raising; it would "
                f"wrap to a ceiling-height byte")

    print("  PASS  field edges: signed x/y at their limits, z unsigned "
          "0..255 with the negative below-datum shorthand intact, "
          "|z| out of range raises")


# ---------------------------------------------------------------------------
# 2. Egg encoders
# ---------------------------------------------------------------------------

def test_egg_encoders():
    """The egg constructors encode what the engine decodes."""
    trig = MapItem.teleport_target(x=100, y=200, z=8, teleport_id=207)
    assert trig.shape == MapItem.SHAPE_TELEPORT_EGG and trig.frame == 1
    assert trig.quality == 207, f"target quality {trig.quality}, expected 207"
    assert trig.is_teleport_target and not trig.is_teleporter

    dest = MapItem.teleporter(x=100, y=200, z=8, teleport_id=207,
                                 dest_npc=100, dest_map=10)
    assert dest.frame == 0 and dest.quality == 256 + 207, (
        f"teleporter quality {dest.quality}, expected {256 + 207}")
    assert dest.npcnum == 100 and dest.mapnum == 10
    assert dest.is_teleporter and not dest.is_teleport_target

    # Both survive serialization as the same kind of egg
    for egg in (trig, dest):
        back = MapItem.from_bytes(egg.to_bytes())
        assert fields(back) == fields(egg), "teleport egg did not round trip"

    # M12: quality is (prob<<11)|monster_shape, mapnum carries the activity
    egg = MapItem.monster_egg(x=1, y=2, z=3, monster_shape=SHAPE_GHOUL,
                              prob=6, count=3, activity=2)
    assert egg.quality & 0x7FF == SHAPE_GHOUL, (
        f"monster shape decoded as {egg.quality & 0x7FF}")
    assert (egg.quality >> 11) & 0x1F == 6, (
        f"prob decoded as {(egg.quality >> 11) & 0x1F}")
    assert egg.npcnum == 3 and egg.mapnum == 2
    # mapNum is (group<<3)|activity: MonsterEgg::getActivity = mapNum & 7,
    # I_getMonId = mapNum >> 3, the group a MONEGG trigger hatches.
    egg = MapItem.monster_egg(x=1, y=2, z=3, monster_shape=SHAPE_GHOUL,
                              activity=1, group=13)
    assert egg.mapnum & 0x07 == 1 and egg.mapnum >> 3 == 13, egg.mapnum
    assert egg.frame == 0, "a monster egg re-hatches (frame 0) by default"
    # One-shot: MONEGG destroys a hatched egg whose frame is not 0.
    assert MapItem.monster_egg(x=1, y=2, monster_shape=SHAPE_GHOUL,
                               one_shot=True).frame == 1
    trig = MapItem.monster_trigger(x=1, y=2, z=3, group=13,
                                   xrange=6, yrange=2)
    assert (trig.shape, trig.quality) == (73, 2), "MONEGG is UnkEgg q2"
    assert trig.mapnum & 0x1F == 13 and trig.npcnum == 0x62, (
        trig.mapnum, trig.npcnum)
    back = MapItem.from_bytes(trig.to_bytes())
    assert fields(back) == fields(trig), "MONEGG trigger did not round trip"

    for kw in (dict(monster_shape=2048, prob=6),
               dict(monster_shape=-1, prob=6),
               dict(monster_shape=SHAPE_GHOUL, prob=32),
               dict(monster_shape=SHAPE_GHOUL, prob=-1),
               dict(monster_shape=SHAPE_GHOUL, activity=8),
               dict(monster_shape=SHAPE_GHOUL, group=32)):
        try:
            MapItem.monster_egg(x=1, y=1, **kw)
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"monster_egg({kw}) accepted an out-of-range value; it would "
                f"silently corrupt the neighbouring bitfield")
    for kw in (dict(group=0, xrange=1, yrange=1),
               dict(group=32, xrange=1, yrange=1),
               dict(group=1, xrange=0, yrange=1),
               dict(group=1, xrange=1, yrange=16)):
        try:
            MapItem.monster_trigger(x=1, y=1, **kw)
        except ValueError:
            pass
        else:
            raise AssertionError(f"monster_trigger({kw}) accepted an "
                                 f"out-of-range value")

    glob = MapItem.glob_egg(x=511, y=511, z=0, glob_index=1757)
    assert glob.is_glob_egg and glob.quality == 1757

    print("  PASS  egg encoders: teleporter/target quality convention, "
          "monster (prob<<11)|shape and (group<<3)|activity packing with "
          "their range guards, the MONEGG trigger, glob egg")


# ---------------------------------------------------------------------------
# 3. Archive round trip
# ---------------------------------------------------------------------------

def check_flex_structure(path, label):
    """Assert the written FIXED.DAT's index table is sane: entries inside
    the file, past the index table, non-overlapping, gapless."""
    data = open(path, 'rb').read()
    count = struct.unpack_from('<I', data, 0x54)[0]
    index_end = 0x80 + count * 8
    spans = []
    for i in range(count):
        off, size = struct.unpack_from('<II', data, 0x80 + i * 8)
        if not size:
            assert off == 0, f"{label}: empty map {i} has offset {off}"
            continue
        assert off >= index_end, (
            f"{label}: map {i} at {off} overlaps the index table")
        assert off + size <= len(data), (
            f"{label}: map {i} runs to {off + size}, past EOF {len(data)}")
        assert size % REC == 0, (
            f"{label}: map {i} is {size} bytes, not a whole number of "
            f"{REC}-byte records")
        spans.append((off, size, i))
    spans.sort()
    prev_end = index_end
    for off, size, i in spans:
        assert off == prev_end, (
            f"{label}: map {i} at {off}, expected {prev_end} "
            f"({off - prev_end} byte gap or overlap)")
        prev_end = off + size
    assert prev_end == len(data), (
        f"{label}: {len(data) - prev_end} trailing byte(s)")
    return count


def test_archive_roundtrip():
    """MapArchive(base) -> save -> reload preserves every item on every map,
    and the file it wrote is structurally sound."""
    archive = MapArchive(BASE_FIXED)
    maps = archive.non_empty_maps()
    total = sum(archive.get_map_count(m) for m in maps)

    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, 'FIXED.DAT')
        archive.save(out)
        count = check_flex_structure(out, "saved base")
        reloaded = MapArchive(out)

    assert count == MapArchive.MAP_COUNT, (
        f"saved archive declares {count} map slots, expected "
        f"{MapArchive.MAP_COUNT}")
    assert reloaded.non_empty_maps() == maps, (
        f"map set changed: {set(maps) ^ set(reloaded.non_empty_maps())}")
    for m in maps:
        before = [fields(i) for i in archive.get_map_items(m)]
        after = [fields(i) for i in reloaded.get_map_items(m)]
        assert before == after, (
            f"map {m}: {sum(1 for a, b in zip(before, after) if a != b)} "
            f"item(s) differ after save/reload "
            f"({len(before)} -> {len(after)} items)")

    print(f"  PASS  archive round trip: {total} items across {len(maps)} maps "
          f"saved and reloaded identically, index table gapless")


def test_archive_mutation():
    """set_map_items / add_items land exactly as given, including on a new
    map slot, and empty lists remove a map rather than writing a 0-byte
    entry."""
    archive = MapArchive()
    items = [MapItem.placed_item(x=100 + i, y=200, z=i, shape=SHAPE_SLAB,
                                 frame=i % 4)
             for i in range(5)]
    archive.set_map_items(9, items)
    archive.add_items(9, [MapItem.teleport_target(x=1, y=2, teleport_id=201)])
    archive.set_map_items(10, [])

    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, 'FIXED.DAT')
        archive.save(out)
        check_flex_structure(out, "synthetic")
        reloaded = MapArchive(out)

    assert reloaded.non_empty_maps() == [9], (
        f"expected only map 9, got {reloaded.non_empty_maps()}")
    assert reloaded.get_map_count(9) == 6, (
        f"map 9 has {reloaded.get_map_count(9)} items, expected 6")
    assert [fields(i) for i in reloaded.get_map_items(9)] == \
           [fields(i) for i in archive.get_map_items(9)], \
        "map 9 items changed through save/reload"
    print("  PASS  archive mutation: set/add land verbatim, an empty list "
          "removes the map slot entirely")


def test_save_is_atomic():
    """L12: save() stages and renames, so a failed write leaves the previous
    artifact byte-identical and no temp file behind."""
    archive = MapArchive()
    archive.set_map_items(9, [MapItem.placed_item(x=100, y=100,
                                                  shape=SHAPE_SLAB)])

    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, 'FIXED.DAT')
        previous = b'PREVIOUS KNOWN-GOOD BUILD' * 100
        open(target, 'wb').write(previous)

        # A write that blows up at the rename: the target must be untouched
        # and the staging file must not survive.
        import u8_map
        real_replace = u8_map.os.replace

        def boom(src, dst):
            raise OSError(28, "No space left on device")

        u8_map.os.replace = boom
        try:
            archive.save(target)
        except OSError:
            pass
        else:
            raise AssertionError("save() swallowed the failed rename")
        finally:
            u8_map.os.replace = real_replace

        assert open(target, 'rb').read() == previous, (
            "a failed save() clobbered the previous artifact")
        leftovers = [f for f in os.listdir(tmp) if f != 'FIXED.DAT']
        assert not leftovers, f"staging file(s) left behind: {leftovers}"

        # And the ordinary path still replaces the file and cleans up
        archive.save(target)
        assert open(target, 'rb').read() != previous, "save() did not write"
        assert os.listdir(tmp) == ['FIXED.DAT'], (
            f"unexpected files after a good save: {os.listdir(tmp)}")
        assert MapArchive(target).get_map_count(9) == 1

    print("  PASS  atomic save: a failed rename leaves the previous "
          "FIXED.DAT byte-identical with no staging file left behind")


# ---------------------------------------------------------------------------
# 4. Validator rules
# ---------------------------------------------------------------------------

def _check_fixtures():
    sc = map_validate._get_shape_cache()
    tc = map_validate._get_typeflag_cache()
    assert not sc.exists(SHAPE_MISSING), (
        f"fixture broken: shape {SHAPE_MISSING} now HAS a U8SHAPES.FLX entry")
    assert sc.exists(SHAPE_SLAB) and sc.frame_count(SHAPE_SLAB) > 1, (
        f"fixture broken: shape {SHAPE_SLAB} missing or single-framed")
    assert tc._shapes[SHAPE_SLAB].has_flag('SI_LAND'), (
        f"fixture broken: shape {SHAPE_SLAB} is no longer SI_LAND")
    assert tc.family(SHAPE_GHOUL) == 6, (
        f"fixture broken: shape {SHAPE_GHOUL} is family "
        f"{tc.family(SHAPE_GHOUL)}, not monster family 6")
    return sc, tc


def _msgs(issues, level=None):
    return [i["msg"] for i in issues if level is None or i["level"] == level]


def test_validator_shape_rules():
    """Known-bad shapes and frames must be reported; eggs stay exempt."""
    sc, _tc = _check_fixtures()
    frames = sc.frame_count(SHAPE_SLAB)

    bad = MapItem.placed_item(x=1000, y=1000, shape=SHAPE_MISSING)
    issues = map_validate.validate_items([bad], 99)
    assert any('no U8SHAPES.FLX entry' in m for m in _msgs(issues, 'ERROR')), (
        f"a shape with no art did not ERROR: {issues}")

    over = MapItem.placed_item(x=1000, y=1000, shape=SHAPE_SLAB,
                               frame=frames + 3)
    issues = map_validate.validate_items([over], 99)
    assert any('out of range for shape' in m for m in _msgs(issues, 'ERROR')), (
        f"an out-of-range frame did not ERROR: {issues}")

    ok = MapItem.placed_item(x=1000, y=1000, shape=SHAPE_SLAB,
                             frame=frames - 1)
    issues = map_validate.validate_items([ok], 99)
    assert not _msgs(issues, 'ERROR'), (
        f"a valid slab was reported: {issues}")

    # Eggs encode data in shape/frame/quality — they must not be art-checked
    eggs = [MapItem.glob_egg(x=1000, y=1000, glob_index=9999),
            MapItem.teleport_target(x=1000, y=1000, teleport_id=200)]
    issues = map_validate.validate_items(eggs, 99)
    assert not _msgs(issues, 'ERROR'), (
        f"an egg was art-checked: {issues}")

    print(f"  PASS  validator shape rules: missing shape and frame >= "
          f"{frames} both ERROR, a valid frame does not, eggs exempt")


def test_validator_monster_egg_rules():
    """M12: the encoding that left the harpie zone and elemental sections
    silently empty must warn."""
    _check_fixtures()

    # The pre-2026-07-24 bug: a raw small number as the whole quality —
    # prob 0, and the low bits name a terrain shape.
    bug = MapItem(x=1000, y=1000, shape=MapItem.SHAPE_MONSTER_EGG,
                  quality=SHAPE_SLAB)
    issues = map_validate.validate_items([bug], 99)
    warns = _msgs(issues, 'WARN')
    assert any('not monster family 6' in m for m in warns), (
        f"a terrain-shape monster egg did not warn: {issues}")
    assert any('never hatch' in m for m in warns), (
        f"a prob=0 monster egg did not warn: {issues}")

    good = MapItem.monster_egg(x=1000, y=1000, monster_shape=SHAPE_GHOUL,
                               prob=6, count=2)
    issues = map_validate.validate_items([good], 99)
    warns = _msgs(issues, 'WARN')
    assert not any('monster egg' in m for m in warns), (
        f"a correctly encoded monster egg warned: {issues}")

    print("  PASS  validator monster eggs: terrain shape and prob=0 both "
          "warn, a real (prob<<11)|shape egg does not")


def test_validator_floor_support():
    """LV teleport endpoints with nothing under them get the ratchetable
    LV_TELEPORT_NO_FLOOR code; a paved one does not."""
    _check_fixtures()

    floating = MapItem.teleporter(x=5000, y=5000, z=16, teleport_id=209,
                                     dest_npc=100, dest_map=13)
    issues = map_validate.validate_items([floating], 17)
    codes = [i.get("code") for i in issues]
    assert "LV_TELEPORT_NO_FLOOR" in codes, (
        f"a teleport destination in a void was not flagged: {issues}")

    paved = [MapItem.placed_item(x=5000, y=5000, z=0, shape=SHAPE_SLAB),
             MapItem.teleporter(x=5000, y=5000, z=0, teleport_id=209,
                                   dest_npc=100, dest_map=13)]
    issues = map_validate.validate_items(paved, 17)
    codes = [i.get("code") for i in issues]
    assert "LV_TELEPORT_NO_FLOOR" not in codes, (
        f"a teleport destination standing on a rock slab was flagged: "
        f"{issues}")

    print("  PASS  validator floor support: an LV teleport in a void is "
          "coded LV_TELEPORT_NO_FLOOR, the same egg on a slab is clean")


def test_validator_on_shipped_build():
    """The FIXED.DAT actually in shared/build must still be clean. Pins the
    current state so a regression cannot ride in unnoticed."""
    assert os.path.exists(BUILT_FIXED), (
        f"built FIXED.DAT missing: {BUILT_FIXED} — run "
        f"build_all_maps.py first")
    archive = MapArchive(BUILT_FIXED)
    issues = []
    for m in ba.LV_MAPS:
        items = archive.get_map_items(m)
        assert items, f"map {m} is empty in the shipped FIXED.DAT"
        issues.extend(map_validate.validate_items(items, m))

    errors = [i for i in issues if i["level"] == "ERROR"]
    warns = [i for i in issues if i["level"] == "WARN"]
    assert not errors, (
        f"{len(errors)} validator ERROR(s) in the shipped FIXED.DAT:\n"
        + map_validate.format_report(errors))
    assert len(warns) <= MAX_KNOWN_WARNS, (
        f"{len(warns)} validator WARN(s), baseline is {MAX_KNOWN_WARNS}:\n"
        + map_validate.format_report(warns))
    if len(warns) < MAX_KNOWN_WARNS:
        print(f"  NOTE  only {len(warns)} WARN(s) remain (pin is "
              f"{MAX_KNOWN_WARNS}) — lower MAX_KNOWN_WARNS to lock it in")

    total = sum(archive.get_map_count(m) for m in ba.LV_MAPS)
    print(f"  PASS  shipped FIXED.DAT: {total} items across "
          f"{len(ba.LV_MAPS)} LV maps, 0 ERROR(s), {len(warns)} WARN(s) "
          f"(pin {MAX_KNOWN_WARNS})")


def test_glob_grounding():
    """H7: a stamped structure must ground on the terrain it is placed on,
    and a glob must land where the BASE GAME puts the identical glob.

    The base-game comparison is the anchor: it reads the real placements out
    of the shipped FIXED.DAT rather than hardcoding an expectation, so if the
    grounding rule ever drifts the test says so in the engine's own terms.
    """
    from glob_catalog import GlobReader, GlobPrefab
    from village_layout import VillageSpec, generate_village
    from build_villages import HOUSE_GLOBS

    gr = GlobReader()

    # What egg z does the base game itself use for these globs?
    base = MapArchive(BASE_FIXED)
    base_egg_z = {}
    for m in base.non_empty_maps():
        for it in base.get_map_items(m):
            if it.is_glob_egg and it.quality in HOUSE_GLOBS:
                base_egg_z.setdefault(it.quality, set()).add(it.z)
    assert base_egg_z, "no base-game placements of the house globs to anchor on"

    for gi in HOUSE_GLOBS:
        p = GlobPrefab(gr, gi)
        assert p.origin_z == 0, (
            f"glob {gi}: origin_z is {p.origin_z}; a glob's items are authored "
            f"relative to the egg, so its expected terrain datum is always 0 "
            f"(min_item_z={p.min_item_z} is a different quantity)")

        egg = p.stamp(5000, 5000, 0)[0]
        if gi in base_egg_z and base_egg_z[gi] == {0}:
            assert egg.z == 0, (
                f"glob {gi} stamped at egg z={egg.z} on z=0 terrain, but the "
                f"base game places it at egg z=0 — it would render "
                f"{egg.z} units off")

        # Following the ground: +48 of terrain must move everything +48
        low0 = min(i.z for i in p.expand(5000, 5000, 0))
        low48 = min(i.z for i in p.expand(5000, 5000, 48))
        assert low48 - low0 == 48, (
            f"glob {gi}: raising terrain by 48 moved the structure by "
            f"{low48 - low0}")

        # Preview must equal what the engine will draw for that same stamp
        via_stamp = gr.glob_to_items(egg.quality, egg.x, egg.y, egg.z)
        assert ([(i.x, i.y, i.z, i.shape) for i in via_stamp] ==
                [(i.x, i.y, i.z, i.shape) for i in p.expand(5000, 5000, 0)]), (
            f"glob {gi}: expand() disagrees with the engine transform applied "
            f"to stamp()'s egg — previews would lie")

    # An egg z the engine cannot represent must raise, not wrap: egg z is an
    # unsigned byte, so a negative would hoist the structure to the ceiling.
    try:
        GlobPrefab(gr, HOUSE_GLOBS[0])._egg_z(-8)
    except ValueError:
        pass
    else:
        raise AssertionError("a negative egg z was accepted; it would wrap")

    # A whole village must sit on one datum
    spec = VillageSpec(center=(5120, 7168), target_buildings=5, seed=7)
    items = generate_village(spec, [GlobPrefab(gr, gi) for gi in HOUSE_GLOBS])
    egg_zs = {i.z for i in items if i.is_glob_egg}
    assert egg_zs == {spec.ground_z}, (
        f"village glob eggs sit at {sorted(egg_zs)}, expected all at the "
        f"village datum {spec.ground_z}")

    print(f"  PASS  H7 grounding: {len(HOUSE_GLOBS)} house globs stamp at the "
          f"base game's own egg z, follow raised terrain 1:1, preview matches "
          f"the engine, and a village lands on one datum")


# ---------------------------------------------------------------------------
# 5. Teleport-pair gate
# ---------------------------------------------------------------------------

def _valid_teleport_archive():
    """A synthetic archive carrying exactly one correct teleporter/target
    pair for every id in TELEPORT_TABLE.

    Engine convention: the TELEPORTER (frame 0) stands on from_map and
    carries the destination in its mapNum; the TARGET (frame 1) stands on
    to_map. A gated row's trigger is the usecode egg of its pinned class
    (shape 73, quality = class - 0x47F) instead.
    """
    archive = MapArchive()
    gated = ba._gated_class_ids()
    for tid, info in ba.TELEPORT_TABLE.items():
        if tid in gated:
            trig = MapItem(x=2000 + tid, y=2000, z=0,
                           shape=MapItem.SHAPE_STANDARD_EGG,
                           quality=gated[tid] - ba.EGG_CLASS_BASE,
                           npcnum=0x11)
        else:
            trig = MapItem.teleporter(x=2000 + tid, y=2000, z=0,
                                      teleport_id=tid, dest_npc=100,
                                      dest_map=info["to_map"])
        archive.add_items(info["from_map"], [trig])
        archive.add_items(info["to_map"], [
            MapItem.teleport_target(x=1000 + tid, y=1000, z=0,
                                    teleport_id=tid)])
    return archive


def _drop(archive, mapnum, predicate):
    archive.set_map_items(
        mapnum, [i for i in archive.get_map_items(mapnum) if not predicate(i)])


def test_teleport_gate_shipped():
    """The shipped FIXED.DAT's 14 pairs must all verify."""
    assert os.path.exists(BUILT_FIXED), (
        f"built FIXED.DAT missing: {BUILT_FIXED} — run build_all_maps.py")
    ok, out = _capture(ba.verify_teleport_pairs, MapArchive(BUILT_FIXED))
    assert ok, f"the shipped FIXED.DAT fails teleport verification:\n{out}"
    assert out.count("[OK]") == len(ba.TELEPORT_TABLE), (
        f"{out.count('[OK]')} pairs reported OK, expected "
        f"{len(ba.TELEPORT_TABLE)}")
    print(f"  PASS  teleport gate: all {len(ba.TELEPORT_TABLE)} pairs "
          f"verified on the shipped FIXED.DAT")


def test_teleport_gate_negatives():
    """Each way a teleport table can be wrong must fail the gate."""
    ok, out = _capture(ba.verify_teleport_pairs, _valid_teleport_archive())
    assert ok, f"the synthetic control archive failed:\n{out}"

    # a) missing teleporter (the frame-0 trigger, on from_map)
    arch = _valid_teleport_archive()
    _drop(arch, ba.TELEPORT_TABLE[207]["from_map"],
          lambda i: i.is_teleporter and i.quality == 256 + 207)
    ok, out = _capture(ba.verify_teleport_pairs, arch)
    assert not ok and "MISSING TELEPORTER" in out, (
        f"a dangling teleport passed the gate:\n{out}")

    # b) duplicate target for one id (M9)
    arch = _valid_teleport_archive()
    arch.add_items(ba.TELEPORT_TABLE[200]["to_map"],
                   [MapItem.teleport_target(x=9000, y=9000, teleport_id=200)])
    ok, out = _capture(ba.verify_teleport_pairs, arch)
    assert not ok and "DUPLICATE TARGET" in out, (
        f"a duplicated target passed the gate:\n{out}")

    # c) target on the wrong map
    arch = _valid_teleport_archive()
    _drop(arch, ba.TELEPORT_TABLE[200]["to_map"],
          lambda i: i.is_teleport_target and i.quality == 200)
    arch.add_items(99, [MapItem.teleport_target(x=1200, y=1000,
                                                teleport_id=200)])
    ok, out = _capture(ba.verify_teleport_pairs, arch)
    assert not ok and "MAP MISMATCH" in out, (
        f"a target on the wrong map passed the gate:\n{out}")

    # d) an LV-range id that is not in TELEPORT_TABLE at all
    arch = _valid_teleport_archive()
    trimmed = {k: v for k, v in ba.TELEPORT_TABLE.items() if k != 213}
    saved = ba.TELEPORT_TABLE
    try:
        ba.TELEPORT_TABLE = trimmed
        ok, out = _capture(ba.verify_teleport_pairs, arch)
    finally:
        ba.TELEPORT_TABLE = saved
    assert not ok and "NOT in TELEPORT_TABLE" in out, (
        f"an unverifiable LV teleport id passed the gate:\n{out}")

    # e) the deliberate out-of-range debug id on the Map 22 shape gallery
    #    must NOT fail the build
    arch = _valid_teleport_archive()
    arch.add_items(22, [
        MapItem.teleport_target(x=1000, y=1000, teleport_id=250),
        MapItem.teleporter(x=2000, y=2000, teleport_id=250, dest_map=22)])
    ok, out = _capture(ba.verify_teleport_pairs, arch)
    assert ok, (
        f"the Map 22 gallery's out-of-range debug id 250 failed the "
        f"gate:\n{out}")

    # f) a gated id (212, the return to the Vale) carried by an engine
    #    TeleportEgg: it fires for anyone, quest state or not (playtest
    #    2026-10-11 replay leg 2 finding 1). Both with the usecode egg
    #    still present and with the TeleportEgg in its place.
    gated = sorted(ba._gated_class_ids())
    assert gated == [212], f"gated teleport ids {gated}, expected [212]"
    for keep_egg in (True, False):
        arch = _valid_teleport_archive()
        info = ba.TELEPORT_TABLE[212]
        if not keep_egg:
            _drop(arch, info["from_map"],
                  lambda i: i.shape == MapItem.SHAPE_STANDARD_EGG)
        arch.add_items(info["from_map"], [
            MapItem.teleporter(x=3000, y=2000, z=0, teleport_id=212,
                               dest_npc=0x11, dest_map=info["to_map"])])
        ok, out = _capture(ba.verify_teleport_pairs, arch)
        assert not ok and "UNGATED TELEPORTER" in out, (
            f"an ungated teleporter for gated id 212 passed the gate:\n{out}")

    # g) a gated id whose usecode egg is missing
    arch = _valid_teleport_archive()
    _drop(arch, ba.TELEPORT_TABLE[212]["from_map"],
          lambda i: i.shape == MapItem.SHAPE_STANDARD_EGG)
    ok, out = _capture(ba.verify_teleport_pairs, arch)
    assert not ok and "MISSING TELEPORTER" in out, (
        f"a gated id with no usecode egg passed the gate:\n{out}")

    print("  PASS  teleport gate negatives: missing dest, duplicate trigger, "
          "wrong map, an id outside TELEPORT_TABLE, and the gated 212 as a "
          "TeleportEgg or with no egg all fail; the Map 22 debug id 250 "
          "does not")


# ---------------------------------------------------------------------------
# 6. The M10 ratchet
# ---------------------------------------------------------------------------

def test_floating_teleport_ratchet():
    """One more floating LV teleport than the pin must block the write."""
    n = ba.KNOWN_FLOATING_LV_TELEPORTS + 1
    items = [MapItem.teleporter(x=6000 + 200 * k, y=6000, z=16,
                                   teleport_id=209, dest_npc=100, dest_map=13)
             for k in range(n)]

    (_issues, has_errors), out = _capture(ba.validate_and_gate, {17: items},
                                          ratchet=True)
    assert has_errors, (
        f"{n} floating LV teleport(s) did not trip the ratchet (pin "
        f"{ba.KNOWN_FLOATING_LV_TELEPORTS}):\n{out}")
    assert "RATCHET FAILURE" in out, f"no ratchet message printed:\n{out}"

    # Without the ratchet these are WARNs only — the quest-step-1 pass relies
    # on that, so prove the flag is what makes the difference.
    (issues, has_errors), _out = _capture(ba.validate_and_gate, {17: items},
                                          ratchet=False)
    assert not has_errors, (
        "floating teleports became ERRORs without the ratchet flag")
    assert sum(1 for i in issues
               if i.get("code") == "LV_TELEPORT_NO_FLOOR") == n, (
        f"expected {n} LV_TELEPORT_NO_FLOOR issue(s): {issues}")

    print(f"  PASS  M10 ratchet: {n} floating LV teleport(s) (pin "
          f"{ba.KNOWN_FLOATING_LV_TELEPORTS}) block the build; the same "
          f"items are WARN-only without ratchet=True")


# ---------------------------------------------------------------------------

def main():
    print("Map pipeline tests (H9)")
    print(f"  base  FIXED.DAT: {BASE_FIXED}")
    print(f"  built FIXED.DAT: {BUILT_FIXED}")
    print(f"  shapes:          {map_validate.effective_shapes_path()}")
    print()

    tests = [
        test_item_roundtrip_base_fixed,
        test_item_field_edges,
        test_egg_encoders,
        test_archive_roundtrip,
        test_archive_mutation,
        test_save_is_atomic,
        test_validator_shape_rules,
        test_validator_monster_egg_rules,
        test_validator_floor_support,
        test_glob_grounding,
        test_validator_on_shipped_build,
        test_teleport_gate_shipped,
        test_teleport_gate_negatives,
        test_floating_teleport_ratchet,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {test.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"  ERROR {test.__name__}: {type(e).__name__}: {e}")

    print()
    print('=' * 60)
    if failed:
        print(f"FAILED: {failed}/{len(tests)} tests failed")
        print('=' * 60)
        return 1
    print(f"OK: {len(tests)}/{len(tests)} tests passed")
    print('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())

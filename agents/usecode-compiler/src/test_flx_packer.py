#!/usr/bin/env python3
"""test_flx_packer.py — prove the FLX packer's layout math is CORRECT, not
merely repeatable.

Guards adversarial-review finding H8. Before this file, no test imported
u8_flx_packer at all: `FlxWriter.build()`'s offset-table arithmetic and the
retired reclaim-before-place allocator were exercised only by full builds,
and test_manifest's md5 comparison proves determinism — two identically
wrong builds still match each other.

Everything here packs, then re-reads through the INDEPENDENT reader
(u8_flex.FlexArchive / UsecodeFlexArchive) and compares against what went
in, plus a structural sweep of the index table (offsets inside the file,
past the index table, non-overlapping, no trailing slack).

Coverage:
  1. Synthetic multi-entry pack: reread byte-identity, offset monotonicity,
     entry count, empty-slot encoding (offset=0/size=0), determinism.
  2. Original-offset ordering: entries are laid out in the source file's
     data order, not index order, and both still reread correctly.
  3. UsecodeFlxPacker name table: class data and names survive a pack/reread
     at the 4-byte header + 13-byte record layout.
  4. The real base EUSECODE.FLX: from_existing -> build is byte-identical,
     and the two mutations the real build performs — replacing a class with
     a LARGER one (shifts every later entry) and adding a new class past the
     original count (grows the index table AND the name table, shifting the
     whole data area) — leave every other class byte-identical.
  5. The retired stealth path (DD-006b): an oversized replacement drives the
     reclaim-before-place allocator into silently corrupting a neighbouring
     entry, and a new entry past 610 is silently dropped. These assert the
     BROKEN behaviour on purpose, so the retirement stays justified and
     nobody un-retires --stealth without tripping this file. The CLI gate is
     checked too.

Plain script, no pytest dependency: exit 0 on pass, exit 1 on fail.
"""

import contextlib
import io
import os
import struct
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from u8_flex import FlexArchive, UsecodeFlexArchive
from u8_flx_packer import FlxPacker, UsecodeFlxPacker

REPO = os.path.abspath(os.path.join(_HERE, '..', '..', '..'))
BASE_FLX = os.path.join(REPO, 'shared', 'data', 'u8-install',
                        'USECODE', 'EUSECODE.FLX')

COUNT_OFFSET = 0x54
INDEX_OFFSET = 0x80
ENTRY_SIZE = 8

# First byte past the md5 window stock ScummVM hashes for detection. The
# stealth path existed entirely to keep bytes 0..4999 untouched; with a
# 620-entry archive the index table alone runs to 0x80 + 620*8 = 5088, which
# is why entry 610 (index slot at 0x80 + 610*8 = 5008) was the cutoff.
MD5_WINDOW = 5000
STEALTH_FIRST_FREE_ENTRY = 610


def read_index(data):
    """Return [(index, offset, size)] straight off the raw index table."""
    count = struct.unpack_from('<I', data, COUNT_OFFSET)[0]
    out = []
    for i in range(count):
        off, size = struct.unpack_from('<II', data, INDEX_OFFSET + i * ENTRY_SIZE)
        out.append((i, off, size))
    return out


def check_structure(data, label, contiguous=True):
    """Assert the index table describes a sane archive.

    contiguous=True additionally requires the data area to be gapless and to
    end exactly at EOF — true of anything build() produces, and the property
    that catches an offset-arithmetic slip that happens to stay consistent
    with itself.
    """
    entries = read_index(data)
    count = len(entries)
    index_end = INDEX_OFFSET + count * ENTRY_SIZE
    assert len(data) >= index_end, (
        f"{label}: file is {len(data)} bytes, shorter than its own "
        f"{count}-entry index table ({index_end} bytes)")

    spans = []
    for i, off, size in entries:
        if size == 0:
            assert off == 0, (
                f"{label}: empty entry {i} has offset {off}, expected 0")
            continue
        assert off >= index_end, (
            f"{label}: entry {i} offset {off} overlaps the index table "
            f"(ends at {index_end})")
        assert off + size <= len(data), (
            f"{label}: entry {i} runs to {off + size}, past EOF {len(data)}")
        spans.append((off, size, i))

    spans.sort()
    prev_end, prev_i = index_end, None
    for off, size, i in spans:
        assert off >= prev_end, (
            f"{label}: entry {i} at {off} overlaps entry {prev_i} "
            f"(ends at {prev_end})")
        if contiguous:
            assert off == prev_end, (
                f"{label}: {off - prev_end} byte gap before entry {i} "
                f"at {off}")
        prev_end, prev_i = off + size, i
    if contiguous:
        assert prev_end == len(data), (
            f"{label}: {len(data) - prev_end} trailing byte(s) after the "
            f"last entry")
    return entries


def check_reread(data, expected, label):
    """Reread `data` with the independent reader and compare every entry
    against `expected` ({index: bytes}); indices not present must be empty."""
    flx = FlexArchive(data)
    for i in range(flx.count):
        got = flx.get_object(i)
        want = expected.get(i)
        if want:
            assert got == want, (
                f"{label}: entry {i} reread as {len(got) if got else None} "
                f"bytes, expected {len(want)}"
                + ("" if got is None or len(got) != len(want)
                   else " (same length, different content)"))
        else:
            assert got is None, (
                f"{label}: entry {i} should be empty, reread "
                f"{len(got)} bytes")
    return flx


# ---------------------------------------------------------------------------
# 1. Synthetic multi-entry pack
# ---------------------------------------------------------------------------

def test_synthetic_pack():
    """Pack varied-size entries with a gap; reread every one; check the
    index table's offsets, sizes, count, and monotonicity."""
    payload = {
        0: b'\x00',
        1: bytes(range(256)),
        2: b'A' * 1,
        # 3 deliberately absent — an interior empty slot
        4: b'\xff' * 4097,          # odd size, straddles no alignment
        5: b'entry five',
    }
    packer = FlxPacker(title="Synthetic Test FLX")
    for i, d in payload.items():
        packer.set_entry(i, d)

    built = packer.build()
    entries = check_structure(built, "synthetic")
    flx = check_reread(built, payload, "synthetic")

    assert flx.count == 6, f"count is {flx.count}, expected 6 (max index + 1)"
    assert flx.title == "Synthetic Test FLX", f"title reread as {flx.title!r}"

    # Sizes come from the index table, not from the reader's slicing
    for i, off, size in entries:
        assert size == len(payload.get(i, b'')), (
            f"entry {i}: index size {size}, payload {len(payload.get(i, b''))}")

    # Fresh pack (no original offsets): data must be laid out in index order,
    # starting immediately after the index table.
    nonempty = [(i, off) for i, off, size in entries if size]
    assert nonempty[0][1] == INDEX_OFFSET + 6 * ENTRY_SIZE, (
        f"first entry at {nonempty[0][1]}, expected right after the index "
        f"table at {INDEX_OFFSET + 6 * ENTRY_SIZE}")
    offs = [off for _i, off in nonempty]
    assert offs == sorted(offs), f"offsets not monotonic in index order: {offs}"

    # Deterministic
    assert packer.build() == built, "build() is not deterministic"

    print(f"  PASS  synthetic pack: {flx.count} entries "
          f"({len(payload)} with data, 1 empty slot), {len(built)} bytes, "
          f"all reread byte-identical")


def test_empty_and_clear():
    """count follows the highest index; set_entry(None)/b'' clears a slot."""
    packer = FlxPacker()
    packer.set_entry(0, b'zero')
    packer.set_entry(7, b'seven')
    assert packer.count == 8, f"count {packer.count}, expected 8"

    packer.set_entry(7, None)
    assert packer.count == 1, f"count after clear {packer.count}, expected 1"
    packer.set_entry(0, b'')
    assert packer.count == 0, f"count after clearing all {packer.count}"

    # An all-empty archive is still a structurally valid, readable FLX
    packer.set_entry(3, b'only')
    built = packer.build()
    check_structure(built, "clear")
    check_reread(built, {3: b'only'}, "clear")
    print("  PASS  empty slots: count tracks the highest index, clearing "
          "works, interior gaps encode as offset=0/size=0")


def test_original_offset_ordering():
    """Entries are written in ORIGINAL data order, not index order — the
    property that lets a rebuild of a real FLX stay byte-identical."""
    packer = FlxPacker()
    packer.set_entry(1, b'first-by-index')
    packer.set_entry(2, b'first-in-file')
    # Pretend entry 2 came earlier in the source file than entry 1
    packer._original_offsets = {1: 9999, 2: 1000}

    built = packer.build()
    check_structure(built, "ordering")
    check_reread(built, {1: b'first-by-index', 2: b'first-in-file'}, "ordering")

    idx = {i: off for i, off, size in read_index(built) if size}
    assert idx[2] < idx[1], (
        f"original data order not preserved: entry 2 at {idx[2]}, "
        f"entry 1 at {idx[1]}")
    print("  PASS  ordering: entries laid out by original file offset, "
          "index table still resolves both correctly")


# ---------------------------------------------------------------------------
# 2. Usecode layout (name table)
# ---------------------------------------------------------------------------

def test_usecode_name_table():
    """Class data and names survive a synthetic pack/reread."""
    packer = UsecodeFlxPacker()
    classes = {
        0: (b'\x01\x02\x03\x04', 'FIRST'),
        1: (b'\xaa' * 100, 'SECOND'),
        3: (b'\xbb' * 7, 'TOOLONGNAME'),   # truncated to 8 chars
    }
    for cid, (data, name) in classes.items():
        packer.add_new_class(cid, data, name)

    built = packer.build()
    check_structure(built, "usecode")
    flx = UsecodeFlexArchive(built)

    for cid, (data, name) in classes.items():
        assert flx.get_class_data(cid) == data, (
            f"class {cid} data did not survive the round trip")
        assert flx.get_class_name(cid) == name[:8], (
            f"class {cid} name reread as {flx.get_class_name(cid)!r}, "
            f"expected {name[:8]!r}")

    assert flx.get_class_data(2) is None, "class 2 should be empty"
    assert flx.get_class_name(2) is None, "class 2 should have no name"

    # Name table geometry: 4-byte header + 13 bytes per class slot
    name_table = flx.get_object(UsecodeFlxPacker.NAME_TABLE_INDEX)
    expected_len = 4 + packer.class_count * 13
    assert len(name_table) == expected_len, (
        f"name table is {len(name_table)} bytes, expected {expected_len} "
        f"(4 + {packer.class_count} * 13)")
    assert packer.class_count == 4, (
        f"class_count {packer.class_count}, expected 4 (highest id 3 + 1)")

    print(f"  PASS  usecode layout: {len(classes)} classes + names reread "
          f"correctly, name table {len(name_table)} bytes "
          f"(4 + {packer.class_count} * 13)")


# ---------------------------------------------------------------------------
# 3. The real base EUSECODE.FLX
# ---------------------------------------------------------------------------

def _base_reader():
    assert os.path.exists(BASE_FLX), (
        f"base game EUSECODE.FLX missing: {BASE_FLX} — see CLAUDE.md "
        f"(shared/data/u8-install must be populated)")
    return UsecodeFlexArchive(BASE_FLX)


def test_base_flx_roundtrip():
    """from_existing -> build reproduces the base archive byte for byte."""
    reader = _base_reader()
    original = open(BASE_FLX, 'rb').read()
    rebuilt = UsecodeFlxPacker.from_existing(reader).build()

    assert len(rebuilt) == len(original), (
        f"rebuilt is {len(rebuilt)} bytes, original {len(original)}")
    if rebuilt != original:
        for i in range(len(original)):
            if rebuilt[i] != original[i]:
                raise AssertionError(
                    f"first byte difference at 0x{i:06X}: "
                    f"orig=0x{original[i]:02X} rebuilt=0x{rebuilt[i]:02X}")

    check_structure(rebuilt, "base rebuild")
    print(f"  PASS  base FLX round trip: {len(original)} bytes byte-identical "
          f"({reader.count} entries, {reader.class_count} classes)")


def _all_class_data(reader):
    return {cid: reader.get_class_data(cid)
            for cid in range(reader.class_count)
            if reader.class_exists(cid)}


def test_base_flx_oversized_replacement():
    """Replacing a class with a LARGER one shifts every later entry. Every
    other class must still reread byte-identically."""
    reader = _base_reader()
    before = _all_class_data(reader)

    # A mid-archive class, so plenty of entries shift behind it
    victim = sorted(before)[len(before) // 2]
    new_data = before[victim] + b'\x00' * 4096

    packer = UsecodeFlxPacker.from_existing(reader)
    packer.replace_class(victim, new_data)
    built = packer.build()

    check_structure(built, "oversized replace")
    after = UsecodeFlexArchive(built)
    assert after.count == reader.count, (
        f"entry count changed: {reader.count} -> {after.count}")
    assert after.get_class_data(victim) == new_data, (
        f"class 0x{victim:04X} did not reread as the replacement data")

    bad = [cid for cid, data in before.items()
           if cid != victim and after.get_class_data(cid) != data]
    assert not bad, (
        f"{len(bad)} class(es) corrupted by the replacement, first: "
        f"0x{bad[0]:04X}")

    print(f"  PASS  oversized replacement: class 0x{victim:04X} grown by "
          f"4096 bytes, remaining {len(before) - 1} classes all still "
          f"byte-identical")


def _check_added_class(reader, before, names_before, new_id, label):
    """add_new_class(new_id) then assert the new class reads back and every
    pre-existing class and name is untouched. Returns the rebuilt reader."""
    new_data = b'LVCLASS!' * 64
    packer = UsecodeFlxPacker.from_existing(reader)
    packer.add_new_class(new_id, new_data, 'LVTEST')
    built = packer.build()

    check_structure(built, label)
    after = UsecodeFlexArchive(built)

    assert after.get_class_data(new_id) == new_data, (
        f"{label}: the new class did not reread")
    assert after.get_class_name(new_id) == 'LVTEST', (
        f"{label}: new class name reread as {after.get_class_name(new_id)!r}")

    bad = [cid for cid, data in before.items()
           if after.get_class_data(cid) != data]
    assert not bad, (
        f"{label}: {len(bad)} pre-existing class(es) lost or corrupted, "
        f"first 0x{bad[0]:04X}")

    # The name table is rebuilt from scratch once any name is modified;
    # every original name must survive that rebuild.
    bad_names = {cid: (n, after.get_class_name(cid))
                 for cid, n in names_before.items()
                 if after.get_class_name(cid) != n}
    assert not bad_names, (
        f"{label}: {len(bad_names)} class name(s) changed, e.g. "
        f"{list(bad_names.items())[:3]}")
    return after


def test_base_flx_new_class_append():
    """The two ways the real build adds an LV class.

    a) Into an EMPTY INTERIOR SLOT (0x0204, the documented first LV id): the
       entry count is unchanged, but the name table grows to cover the new
       id, which moves the whole data area behind it.
    b) PAST the original count (id 1431): the index table itself grows by one
       8-byte slot, moving the data area again.
    Either way nothing already in the archive may shift out from under its
    index entry.
    """
    reader = _base_reader()
    before = _all_class_data(reader)
    names_before = {cid: reader.get_class_name(cid)
                    for cid in range(reader.class_count)
                    if reader.get_class_name(cid)}

    interior_id = 0x0204     # first LV class id (CLAUDE.md)
    assert not reader.class_exists(interior_id), (
        f"class 0x{interior_id:04X} is not an empty slot in the base archive")
    after_a = _check_added_class(reader, before, names_before,
                                 interior_id, "interior slot")
    assert after_a.count == reader.count, (
        f"interior slot: entry count changed {reader.count} -> "
        f"{after_a.count}; 0x{interior_id:04X} is inside the existing table")

    past_end_id = reader.class_count      # first id past the last slot
    after_b = _check_added_class(reader, before, names_before,
                                 past_end_id, "past end")
    assert after_b.count == past_end_id + UsecodeFlxPacker.CLASS_BASE_INDEX + 1, (
        f"past end: entry count {after_b.count}, expected "
        f"{past_end_id + 3}")
    assert after_b.count == reader.count + 1, (
        f"past end: archive grew by {after_b.count - reader.count} entries, "
        f"expected 1")

    print(f"  PASS  new class append: 0x{interior_id:04X} into an empty "
          f"interior slot (count stays {after_a.count}) and 0x{past_end_id:04X} "
          f"past the end (count {reader.count} -> {after_b.count}); all "
          f"{len(before)} existing classes and {len(names_before)} names "
          f"intact both times")


# ---------------------------------------------------------------------------
# 4. The retired stealth path — assert it is still broken
# ---------------------------------------------------------------------------

def _synthetic_stealth_original(path, n_entries=620, size=32):
    """Write a synthetic FLX big enough that entry 610's index slot sits past
    the 5000-byte md5 window, mirroring the real EUSECODE.FLX geometry.

    Entry 0 and entry 618 are left empty (618 is the 'new class' slot).
    """
    packer = FlxPacker(title="Stealth Fixture")
    payload = {}
    for i in range(1, n_entries):
        if i == 618:
            continue
        payload[i] = bytes([i & 0xFF]) * size
        packer.set_entry(i, payload[i])
    data = packer.build()
    assert INDEX_OFFSET + STEALTH_FIRST_FREE_ENTRY * ENTRY_SIZE > MD5_WINDOW, (
        "fixture geometry wrong: entry 610's index slot is inside the md5 "
        "window")
    open(path, 'wb').write(data)
    return payload


def test_stealth_reclaim_corrupts():
    """DD-006b: with two adjacent modified entries, the reclaim-before-place
    allocator gives the FIRST one all the merged space and then cannot place
    the SECOND — whose index still points into the region it just overwrote.
    The result reads back as neither the old nor the new data.

    This asserts the CORRUPTION on purpose. If someone repairs the allocator
    this test fails loudly, which is the moment to reconsider the retirement
    rather than the moment to discover a wrecked FLX in-game.
    """
    with tempfile.TemporaryDirectory() as tmp:
        orig_path = os.path.join(tmp, 'orig.flx')
        out_path = os.path.join(tmp, 'stealth.flx')
        payload = _synthetic_stealth_original(orig_path)
        original = open(orig_path, 'rb').read()

        packer = FlxPacker()
        reader = FlexArchive(orig_path)
        for i, off, size in reader.entries():
            if size:
                packer.set_entry(i, reader.get_object(i))
                packer._original_offsets[i] = off

        # Two adjacent oversized replacements + one brand new entry
        packer.set_entry(610, b'A' * 64)
        packer.set_entry(611, b'B' * 64)
        packer.set_entry(618, b'N' * 32)

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            written = packer.write_stealth(out_path, orig_path)
        stderr = err.getvalue()

        out = open(out_path, 'rb').read()
        after = FlexArchive(out_path)

    assert written == len(original), (
        f"stealth output is {written} bytes, original {len(original)} — the "
        f"whole point of the mode was an unchanged file size")
    assert out[:MD5_WINDOW] == original[:MD5_WINDOW], (
        "the md5 detection window changed; stealth mode's only premise is "
        "that it does not")

    # Entry 610 got the entire merged region
    assert after.get_object(610) == b'A' * 64, (
        f"entry 610 reread as {after.get_object(610)!r:.40}, expected 64 'A's")

    # Entry 611 was NOT placed, and its untouched index now points into
    # entry 610's freshly written data: silent corruption.
    got_611 = after.get_object(611)
    assert got_611 != b'B' * 64, (
        "entry 611 was placed after all — the reclaim allocator changed "
        "behaviour; re-evaluate the DD-006b retirement")
    assert got_611 != payload[611], (
        "entry 611 kept its original data — the reclaim allocator changed "
        "behaviour; re-evaluate the DD-006b retirement")
    assert got_611 == b'A' * 32, (
        f"entry 611 reread as {got_611!r:.40}; expected the tail of entry "
        f"610's overwrite (32 'A's)")
    assert 'Could not fit modified entry 611' in stderr, (
        f"no warning printed for the unplaceable entry:\n{stderr}")

    # A brand new entry past 610 is silently dropped — there is no space to
    # grow into, which is exactly why the expansion cannot ship this way.
    assert after.get_object(618) is None, (
        "the new entry 618 was written; stealth mode cannot grow the file")
    assert '1 new LV classes skipped' in stderr, (
        f"no skipped-new note printed:\n{stderr}")

    print("  PASS  stealth reclaim path is still broken as documented: "
          "entry 611 silently reads back as entry 610's overflow, new entry "
          "618 dropped, file size and md5 window preserved")


def test_stealth_cli_retired():
    """`build_eusecode.py --stealth` must refuse and exit nonzero without
    building anything."""
    script = os.path.join(_HERE, 'build_eusecode.py')
    proc = subprocess.run([sys.executable, script, '--stealth'],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode != 0, (
        "--stealth exited 0; the retirement gate is gone")
    assert 'retired' in proc.stdout.lower() + proc.stderr.lower(), (
        f"--stealth did not print a retirement notice:\n{proc.stdout}\n"
        f"{proc.stderr}")
    print(f"  PASS  --stealth CLI gate: exit {proc.returncode} with a "
          f"retirement notice, nothing built")


# ---------------------------------------------------------------------------

def main():
    print("FLX packer tests (H8)")
    print(f"  base FLX: {BASE_FLX}")
    print()

    tests = [
        test_synthetic_pack,
        test_empty_and_clear,
        test_original_offset_ordering,
        test_usecode_name_table,
        test_base_flx_roundtrip,
        test_base_flx_oversized_replacement,
        test_base_flx_new_class_append,
        test_stealth_reclaim_corrupts,
        test_stealth_cli_retired,
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

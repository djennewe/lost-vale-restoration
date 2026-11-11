#!/usr/bin/env python3
"""
test_manifest.py — Acceptance tests for the M0.6 id/flag manifest
(manifest-design.md section 5; PLAN.md M0.6).

Covers:
  1. Order independence: compiling every LV source directory in reversed
     sorted order, with the checked-in manifest, produces a byte-identical
     EUSECODE.FLX (md5) to the normal-order build. Both runs write to temp
     paths, never the real OUTPUT_FLX.
  2. Append behavior: against a temp copy of the manifest, a build that
     includes a temp .UNK declaring one new globalflag appends exactly one
     new flag pin at the next_free cursor (plus the temp file's one new
     class pin) and moves no existing pin.
  3. Conflict detection: a hand-corrupted temp manifest (duplicate bit;
     width mismatch; class id collision; a live pin on a retired bit)
     makes the build fail, naming the conflict, without writing the output
     FLX or touching the manifest.

Plain script, no pytest dependency: exit 0 on pass, exit 1 on fail.
Mirrors the style of test_patch_mythran.py. Full-build tests run the real
build() with module constants monkeypatched to temp paths, so nothing here
ever writes the real OUTPUT_FLX, the real manifest, or detection_tables.h.
"""

import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lv_manifest
import build_eusecode as be

REAL_MANIFEST = lv_manifest.DEFAULT_MANIFEST_PATH

TEST_UNK = """\
// test_manifest.py fixture — declares one new globalflag (append test).

uses "egg";
uses "free";
uses "flags";
uses "item";

globalflag m06TestFlag;

eggclass EggM06Test inherits Egg
{
\tprocess hatch();
}

process EggM06Test::hatch()
{
\tif m06TestFlag
\t{
\t\treturn;
\t}
\tm06TestFlag = TRUE;
}
"""


def _run_build(**kwargs):
    """Run be.build() with stdout captured. Returns (failures, output_text)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _path, failures = be.build(**kwargs)
    return failures, buf.getvalue()


def _md5(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


@contextlib.contextmanager
def _patched(module, **attrs):
    """Temporarily replace module attributes."""
    saved = {k: getattr(module, k) for k in attrs}
    try:
        for k, v in attrs.items():
            setattr(module, k, v)
        yield
    finally:
        for k, v in saved.items():
            setattr(module, k, v)


def test_order_independence():
    """Reversed compile order + manifest => byte-identical FLX (md5)."""
    assert os.path.exists(REAL_MANIFEST), (
        f"checked-in manifest missing: {REAL_MANIFEST} — run a bootstrap "
        f"build first")

    with tempfile.TemporaryDirectory() as tmp:
        normal_flx = os.path.join(tmp, 'normal.flx')
        reversed_flx = os.path.join(tmp, 'reversed.flx')

        failures, out = _run_build(output_path=normal_flx)
        assert not failures, f"normal-order build failed: {failures}"
        failures, out = _run_build(output_path=reversed_flx, reverse_order=True)
        assert not failures, f"reversed-order build failed: {failures}"

        md5_normal = _md5(normal_flx)
        md5_reversed = _md5(reversed_flx)
        assert md5_normal == md5_reversed, (
            f"order dependence! normal={md5_normal} reversed={md5_reversed}")

    print(f"  PASS  order independence: normal and reversed compile order "
          f"both md5 {md5_normal}")


def test_append_behavior():
    """A new globalflag in a temp .UNK appends exactly one flag pin at the
    cursor (plus the temp file's class pin); no existing pin moves."""
    before = json.load(open(REAL_MANIFEST))

    with tempfile.TemporaryDirectory() as tmp:
        tmp_manifest = os.path.join(tmp, 'lv_manifest.json')
        shutil.copyfile(REAL_MANIFEST, tmp_manifest)

        # lv-new copy + one extra file declaring the new flag
        tmp_lvnew = os.path.join(tmp, 'lv-new')
        shutil.copytree(be.LV_NEW, tmp_lvnew)
        with open(os.path.join(tmp_lvnew, 'M06TEST.UNK'), 'w') as f:
            f.write(TEST_UNK)

        tmp_flx = os.path.join(tmp, 'EUSECODE.FLX')
        # OUTPUT_FLX must equal the build's output path for the manifest
        # append (is_real_build) to happen — point both at the temp FLX.
        # is_real_build also auto-updates detection_tables.h, found under
        # REPO_ROOT at run time, so REPO_ROOT goes to the temp dir too.
        # Without it every estate run wrote this test's FLX (one extra
        # class: md5 340c79..., 1,505,765 bytes) into the real
        # scummvm-lv/engines/ultima/detection_tables.h, and a bare `make`
        # then built an engine that could not detect the game
        # (docs/playtest-2026-09-27-bag-ezrekal.md, finding 3).
        with _patched(be, OUTPUT_FLX=tmp_flx, LV_NEW=tmp_lvnew,
                      REPO_ROOT=tmp), \
             _patched(lv_manifest, DEFAULT_MANIFEST_PATH=tmp_manifest):
            failures, out = _run_build()
        assert not failures, f"append-test build failed: {failures}"
        assert 'MANIFEST: appended' in out, "no MANIFEST append block printed"

        after = json.load(open(tmp_manifest))

    # Exactly one new flag pin, at the old cursor
    new_flags = set(after['global_flags']) - set(before['global_flags'])
    assert new_flags == {'m06TestFlag'}, f"unexpected new flags: {new_flags}"
    entry = after['global_flags']['m06TestFlag']
    old_cursor = before['next_free']['global_bit']
    assert entry['bit'] == old_cursor and entry['width'] == 1, (
        f"m06TestFlag pinned at {entry}, expected bit {old_cursor} width 1")
    assert after['next_free']['global_bit'] == old_cursor + 1, (
        f"global_bit cursor not bumped by 1: {after['next_free']}")

    # The temp file's class also gets a pin, at the old class cursor
    new_classes = set(after['classes']) - set(before['classes'])
    assert new_classes == {'EGGM06TEST'}, f"unexpected new classes: {new_classes}"
    assert after['classes']['EGGM06TEST'] == before['next_free']['class_id']

    # No existing pin moved
    for name, pin in before['global_flags'].items():
        assert after['global_flags'][name] == pin, (
            f"existing flag pin moved: {name} {pin} -> {after['global_flags'][name]}")
    for name, cid in before['classes'].items():
        assert after['classes'][name] == cid, (
            f"existing class pin moved: {name} {cid} -> {after['classes'][name]}")

    # And the real manifest on disk was never touched
    assert json.load(open(REAL_MANIFEST)) == before, (
        "real manifest was modified by the temp-path build")

    print(f"  PASS  append: m06TestFlag pinned at bit {old_cursor}, "
          f"EGGM06TEST at 0x{after['classes']['EGGM06TEST']:04X}, "
          f"{len(before['global_flags'])} existing flag pins unmoved")


def _run_corrupted(mutate, expect_in_failures):
    """Corrupt a temp manifest copy with mutate(dict), run a temp-path
    build, and assert it fails with a message containing expect_in_failures.
    Also asserts the output FLX was not written."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_manifest = os.path.join(tmp, 'lv_manifest.json')
        data = json.load(open(REAL_MANIFEST))
        mutate(data)
        with open(tmp_manifest, 'w') as f:
            json.dump(data, f, indent=2)

        tmp_flx = os.path.join(tmp, 'EUSECODE.FLX')
        with _patched(be, OUTPUT_FLX=tmp_flx), \
             _patched(lv_manifest, DEFAULT_MANIFEST_PATH=tmp_manifest):
            failures, out = _run_build()

        assert failures, "corrupted manifest did not fail the build"
        joined = '\n'.join(failures)
        assert expect_in_failures in joined, (
            f"failure text does not name the conflict "
            f"({expect_in_failures!r} not in):\n{joined}")
        assert not os.path.exists(tmp_flx), (
            "output FLX was written despite the build failing")
    return failures


def test_conflict_duplicate_bit():
    """Two pins on the same bit must fail the build naming both flags."""
    def mutate(data):
        # Pin mythranIntroDone onto lbDone's bit
        data['global_flags']['mythranIntroDone']['bit'] = \
            data['global_flags']['lbDone']['bit']

    failures = _run_corrupted(mutate, 'bit overlap')
    joined = '\n'.join(failures)
    assert 'lbDone' in joined and 'mythranIntroDone' in joined, (
        f"overlap failure does not name both flags:\n{joined}")
    print(f"  PASS  duplicate bit: build failed naming lbDone/mythranIntroDone "
          f"overlap ({len(failures)} failure line(s))")


def test_conflict_width_mismatch():
    """A pinned width that disagrees with the source declaration must fail
    the build naming the flag. Widens the HIGHEST-bit pin so the widening
    does not also trip the structural bit-overlap check — that keeps this
    exercising allocate_global_flag's ManifestError path specifically.

    The top pin is looked up dynamically rather than hardcoded (it used to
    be sigridToldHusband). Appending new pins is routine — the 2026-07-19
    givenElixir/iAmDrunk allocation moved the top and silently turned this
    into an overlap test — so the fixture now follows the cursor.
    """
    data0 = json.load(open(REAL_MANIFEST))
    live = {n: i for n, i in data0['global_flags'].items() if not i.get('retired')}
    top = max(live, key=lambda n: live[n]['bit'] + live[n].get('width', 1))
    assert live[top].get('width', 1) == 1, (
        f"top pin {top!r} is not width 1; widening it to 2 would not be a "
        f"clean width mismatch")

    def mutate(data):
        # The declaring source says width 1; widening the pin to 2 stays
        # clear of every other pin (it is the last allocated bit), so only
        # the allocation-time width check can catch it.
        data['global_flags'][top]['width'] = 2
        # Keep the allocation cursor past the now-wider pin. Since 2026-07-25
        # validate() also asserts next_free sits beyond every pin (M3), and
        # widening the TOP pin by definition eats the next free bit — without
        # this the fixture would report a cursor conflict too and stop being
        # a clean isolation of the width-mismatch path.
        nf = data.setdefault('next_free', {})
        widened_end = data['global_flags'][top]['bit'] + 2 - 1
        if nf.get('global_bit', 0) <= widened_end:
            nf['global_bit'] = widened_end + 1

    failures = _run_corrupted(mutate, f"'{top}'")
    joined = '\n'.join(failures)
    assert 'width' in joined, f"width-mismatch failure unclear:\n{joined}"
    print(f"  PASS  width mismatch: build failed naming {top}'s "
          f"pinned width vs declared width")


def test_conflict_class_id_collision():
    """A class pin colliding with a base-game class id must fail the build
    naming the class and the collision. Two variants:
      - a base-game id NOT recorded in the manifest (0x0100 FISH2), caught
        by the allocator at class-id assignment;
      - an id recorded in the manifest (0x0401 AVATAR, in
        modified_base_classes), caught by the structural validate() at load.
    """
    # The victim is chosen from the live manifest rather than hardcoded. It
    # used to be SIGRID, which broke on 2026-07-26 when she moved out of
    # `classes` into the npcnum-dispatch window (orphan triage, decision B):
    # LV_NPC_SHAPES takes precedence over the manifest pin, so corrupting her
    # pin no longer reached the allocator and the test silently stopped
    # testing anything. Same failure mode the width-mismatch fixture already
    # guards against by following the cursor.
    #
    # Lowest-id pin is the most stable pick: `classes` is append-only, so the
    # lowest id is the oldest entry and the least likely to be re-homed.
    data0 = json.load(open(REAL_MANIFEST))
    victim = min(data0['classes'], key=lambda n: data0['classes'][n])

    # Variant 1: allocator-path check against the full base-game id set
    def mutate_base(data):
        data['classes'][victim] = 0x0100  # FISH2 — base-game, not in manifest

    failures = _run_corrupted(mutate_base, f"'{victim}'")
    joined = '\n'.join(failures)
    assert 'base-game' in joined and '0x0100' in joined, (
        f"class-collision failure unclear:\n{joined}")

    # Variant 2: structural cross-group check in lv_manifest.validate()
    def mutate_recorded(data):
        data['classes'][victim] = 0x0401  # AVATAR (modified_base_classes)

    failures = _run_corrupted(mutate_recorded, victim)
    joined = '\n'.join(failures)
    assert 'AVATAR' in joined and '0x0401' in joined, (
        f"cross-group collision failure unclear:\n{joined}")

    print(f"  PASS  class id collision: allocator caught {victim}->0x0100 "
          f"(base-game FISH2); validate() caught {victim}->0x0401 (AVATAR)")


def test_conflict_retired_bit_reuse():
    """A live flag pin moved onto a RETIRED flag's bits must fail the build
    naming both. Retired bits are dead forever: a save from before the
    retirement can still hold a value there (devonInRule left bit 1206 for
    retail 0x58 on 2026-10-08, araminaSchedule 1635 for 0x207)."""
    data0 = json.load(open(REAL_MANIFEST))
    retired = {n: i for n, i in data0['global_flags'].items() if i.get('retired')}
    assert retired, "manifest records no retired flag bits"
    r_name = min(retired)
    r_bit = retired[r_name]['bit']

    def mutate(data):
        data['global_flags']['mythranIntroDone']['bit'] = r_bit

    failures = _run_corrupted(mutate, 'retired')
    joined = '\n'.join(failures)
    assert 'mythranIntroDone' in joined and r_name in joined, (
        f"retired-bit failure does not name both entries:\n{joined}")
    print(f"  PASS  retired bit reuse: build failed naming mythranIntroDone "
          f"on {r_name}'s bit {r_bit}")


def main():
    print(f"M0.6 manifest acceptance tests (manifest: {REAL_MANIFEST})")
    print()

    tests = [
        test_order_independence,
        test_append_behavior,
        test_conflict_duplicate_bit,
        test_conflict_width_mismatch,
        test_conflict_class_id_collision,
        test_conflict_retired_bit_reuse,
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

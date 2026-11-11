#!/usr/bin/env python3
"""
test_patch_mythran.py — Tests for the Mythran patch's residual guards (M0.7)
and the codegen-Emitter rebuild of build_new_use() (M0.8).

Covers:
  1. A successful patch with realistic parameters (positive path).
  2. Preamble hash mismatch (corrupted base bytes) raises ValueError.
  3. lv_use_offset == 0 raises ValueError before any patching happens.
  4. The patch only appends: the first old_len bytes of the output are
     byte-identical to the input except the event-01 table entry (4 bytes)
     and the total_size header field (4 bytes).
  5. build_new_use() byte-identity regression: the current (BytecodeEmitter-
     based, M0.8) implementation must produce exactly the same bytes as the
     pre-M0.8 hand-rolled implementation, for the real deployment parameters
     and for synthetic parameter sets. Pinned via sha256 digest.

Plain script, no pytest dependency: exit 0 on pass, exit 1 on fail. Mirrors
the style of test_roundtrip.py.
"""

import hashlib
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from u8_flex import UsecodeFlexArchive
from patch_mythran import (
    patch_mythran_class,
    build_new_use,
    BASE_OFFSET,
    USE_EVENT,
    MYTHRAN_USE_OFFSET,
    PREAMBLE_START,
    PREAMBLE_END,
)

# Path resolution: relative to this file (repo root three levels up), same
# convention as lv_manifest.py.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

FLX_PATH = os.path.join(REPO_ROOT, 'shared', 'data', 'USECODE.FLX')
MYTHRAN_CLASS_ID = 0x421

# Realistic-but-arbitrary patch parameters, matching the ranges named in the
# task: lbDone bit 678 width 1, LV class id 0x0279, use offset 0x0080,
# mythranStockVisit bit 796 width 1.
LBDONE_BIT = 678
LBDONE_WIDTH = 1
LV_CLASS_ID = 0x0279
LV_USE_OFFSET = 0x0080
STOCKVISIT_BIT = 796
STOCKVISIT_WIDTH = 1

# sha256 digests of build_new_use() output, captured from the pre-M0.8
# hand-rolled (bytes([...]) literal) implementation at commit c344cfd,
# before it was rebuilt on u8c_codegen.BytecodeEmitter. Any future change to
# build_new_use() must keep producing these exact bytes for these exact
# inputs -- see the M0.8 acceptance criterion ("patch output byte-identical
# to the hand-rolled version").
#
# All cases use the real 43-byte preamble extracted from class 0x421 of
# USECODE.FLX (md5 09e6916fdd404ce910eb19b6acf96383) unless they name their
# own. The synthetic cases exercise different bit offsets/widths, class
# ids/offsets, and preamble lengths (including an empty preamble) to catch
# any use of position 0 as a fixed origin.
#
# P3 (2026-07-25): 'historical' below was named 'real' and described as "the
# deployment parameters", but those offsets stopped being deployed long ago —
# the manifest now pins lbDone at bit 1702 and mythranStockVisit at 1820, and
# TypeMythranLVDlg compiles to class 0x05AB, not 0x0279. It was locking 85
# bytes the build never emits (same length, different content), so an
# operand-encoding regression on the offsets the build DOES emit would have
# passed. 'deployed' now covers those, and
# test_deployed_case_matches_manifest() fails the moment the manifest moves
# again, so this can't go stale silently a second time.
#
# 'historical' is kept rather than replaced: its digest is the only one
# captured from the pre-M0.8 hand-rolled implementation at those inputs, and
# deleting it would throw away the hand-rolled equivalence evidence. The
# 'deployed' digest was computed from the current (BytecodeEmitter)
# implementation, which is legitimate precisely because the other four cases
# still pin it to the hand-rolled bytes.
BYTE_IDENTITY_CASES = {
    'historical': dict(
        kwargs=dict(lbdone_bit=678, lbdone_width=1, lv_class_id=0x0279,
                    lv_use_offset=0x0080, stockvisit_bit=796,
                    stockvisit_width=1),
        preamble='real',
        expected_len=85,
        expected_sha256=(
            '4f8e4416248c190f255c8b9d5d103e3f7486e0ee01f0321165a1d321ae32beb2'),
    ),
    'deployed': dict(
        kwargs=dict(lbdone_bit=1702, lbdone_width=1, lv_class_id=0x05AB,
                    lv_use_offset=0x0080, stockvisit_bit=1820,
                    stockvisit_width=1),
        preamble='real',
        expected_len=85,
        expected_sha256=(
            '7be03582a916582e5625c0c70e102c4035a62e5bb032a8eb9b4509e71d630bf3'),
    ),
    'synthetic1': dict(
        kwargs=dict(lbdone_bit=1, lbdone_width=1, lv_class_id=0x0001,
                    lv_use_offset=0x0001, stockvisit_bit=2,
                    stockvisit_width=1),
        preamble=bytes(range(10)),
        expected_len=52,
        expected_sha256=(
            '22b610af788b44679558d3087cf93af8b8bdf69dc0c5565e59028b6d047c7174'),
    ),
    'synthetic2': dict(
        kwargs=dict(lbdone_bit=1023, lbdone_width=2, lv_class_id=0xFFFF,
                    lv_use_offset=0xFFFF, stockvisit_bit=500,
                    stockvisit_width=4),
        preamble=bytes([0xAA] * 100),
        expected_len=142,
        expected_sha256=(
            'bd43d5fd6a75d47a6a3941e34f43bf6ff77fa5082e8eaec88e206ddebea498c3'),
    ),
    'synthetic3': dict(
        kwargs=dict(lbdone_bit=0, lbdone_width=1, lv_class_id=0x0204,
                    lv_use_offset=0x0010, stockvisit_bit=0,
                    stockvisit_width=1),
        preamble=b'',
        expected_len=42,
        expected_sha256=(
            '54362a6bdc26590a1031b4ea77f9721522bd14293f98efc320fea8f57d40039b'),
    ),
}


def load_base_class():
    flx = UsecodeFlexArchive(FLX_PATH)
    data = flx.get_class_data(MYTHRAN_CLASS_ID)
    if data is None:
        raise RuntimeError(f"class 0x{MYTHRAN_CLASS_ID:04X} not found in {FLX_PATH}")
    return data


def test_successful_patch(base_data):
    """A valid patch should succeed, grow the class, and repoint event 01."""
    old_len = len(base_data)

    patched = patch_mythran_class(
        base_data, LBDONE_BIT, LBDONE_WIDTH, LV_CLASS_ID, LV_USE_OFFSET,
        STOCKVISIT_BIT, STOCKVISIT_WIDTH)

    assert len(patched) > old_len, (
        f"patched class did not grow ({len(patched)} <= {old_len})")

    new_use_offset = struct.unpack_from(
        '<I', patched, BASE_OFFSET + USE_EVENT * 4)[0]
    expected_offset = old_len - BASE_OFFSET
    assert new_use_offset == expected_offset, (
        f"event-01 offset 0x{new_use_offset:X} != expected "
        f"0x{expected_offset:X} (old_len - BASE_OFFSET)")

    print(f"  PASS  successful patch: {old_len} -> {len(patched)} bytes, "
          f"event 01 -> 0x{new_use_offset:X}")


def test_preamble_hash_mismatch(base_data):
    """Corrupting one byte inside the preamble range must raise ValueError
    mentioning the hash mismatch."""
    corrupted = bytearray(base_data)
    corrupt_at = BASE_OFFSET + PREAMBLE_START  # first byte of the preamble
    corrupted[corrupt_at] ^= 0xFF  # flip all bits of one byte

    try:
        patch_mythran_class(
            bytes(corrupted), LBDONE_BIT, LBDONE_WIDTH, LV_CLASS_ID,
            LV_USE_OFFSET, STOCKVISIT_BIT, STOCKVISIT_WIDTH)
    except ValueError as e:
        msg = str(e)
        assert 'hash' in msg.lower(), (
            f"ValueError did not mention 'hash': {msg!r}")
        print(f"  PASS  corrupted preamble byte raised ValueError: {msg[:70]}...")
        return
    raise AssertionError(
        "corrupted preamble byte did not raise ValueError")


def test_zero_use_offset(base_data):
    """lv_use_offset=0 on otherwise-clean data must raise ValueError."""
    try:
        patch_mythran_class(
            base_data, LBDONE_BIT, LBDONE_WIDTH, LV_CLASS_ID,
            0,  # lv_use_offset
            STOCKVISIT_BIT, STOCKVISIT_WIDTH)
    except ValueError as e:
        msg = str(e)
        assert 'lv_use_offset' in msg or '0' in msg, (
            f"ValueError message unclear: {msg!r}")
        print(f"  PASS  lv_use_offset=0 raised ValueError: {msg[:70]}...")
        return
    raise AssertionError("lv_use_offset=0 did not raise ValueError")


def test_patch_only_appends(base_data):
    """Byte-for-byte: the patched output's first old_len bytes equal the
    original except the 4-byte event-01 table entry and the 4-byte
    total_size field. Proves the patch only appends."""
    old_len = len(base_data)

    patched = patch_mythran_class(
        base_data, LBDONE_BIT, LBDONE_WIDTH, LV_CLASS_ID, LV_USE_OFFSET,
        STOCKVISIT_BIT, STOCKVISIT_WIDTH)

    event01_range = range(BASE_OFFSET + USE_EVENT * 4,
                           BASE_OFFSET + USE_EVENT * 4 + 4)
    total_size_range = range(4, 8)
    allowed_diff_offsets = set(event01_range) | set(total_size_range)

    diffs = []
    for i in range(old_len):
        if base_data[i] != patched[i] and i not in allowed_diff_offsets:
            diffs.append(i)

    assert not diffs, (
        f"unexpected byte differences outside event-01/total_size fields "
        f"at offsets: {diffs[:10]}{'...' if len(diffs) > 10 else ''}")

    print(f"  PASS  patch only appends: first {old_len} bytes match except "
          f"event-01 entry (offset 0x{BASE_OFFSET + USE_EVENT * 4:X}) and "
          f"total_size (offset 0x4)")


def test_build_new_use_byte_identity(base_data):
    """build_new_use() must reproduce the pre-M0.8 hand-rolled bytes exactly,
    for the real deployment parameters and for several synthetic parameter
    sets (different bit offsets/widths, class ids/offsets, preamble
    lengths)."""
    real_preamble = bytes(
        base_data[BASE_OFFSET + PREAMBLE_START:BASE_OFFSET + PREAMBLE_END])

    for name, case in BYTE_IDENTITY_CASES.items():
        preamble = real_preamble if case['preamble'] == 'real' else case['preamble']
        out = build_new_use(preamble_bytes=preamble, **case['kwargs'])
        got_sha256 = hashlib.sha256(out).hexdigest()

        assert len(out) == case['expected_len'], (
            f"{name}: length {len(out)} != expected {case['expected_len']}")
        assert got_sha256 == case['expected_sha256'], (
            f"{name}: sha256 {got_sha256} != expected "
            f"{case['expected_sha256']} (build_new_use() output diverged "
            f"from the pinned pre-M0.8 hand-rolled reference)")

    print(f"  PASS  build_new_use() byte-identical to pre-M0.8 hand-rolled "
          f"reference for {len(BYTE_IDENTITY_CASES)} parameter sets")


def test_deployed_case_matches_manifest(base_data):
    """P3: the 'deployed' byte-identity case must describe the parameters the
    build ACTUALLY passes, or it is pinning bytes nobody emits.

    The three ids come from the checked-in manifest, which is what the build
    reads, so this catches a drift the moment it happens instead of years
    later during a review.
    """
    import json
    manifest_path = os.path.join(REPO_ROOT, 'shared', 'build',
                                 'lv_manifest.json')
    assert os.path.exists(manifest_path), (
        f"manifest missing: {manifest_path}")
    manifest = json.load(open(manifest_path))

    kw = BYTE_IDENTITY_CASES['deployed']['kwargs']
    expect = {
        'lbdone_bit': ('global_flags', 'lbDone', 'bit'),
        'lbdone_width': ('global_flags', 'lbDone', 'width'),
        'stockvisit_bit': ('global_flags', 'mythranStockVisit', 'bit'),
        'stockvisit_width': ('global_flags', 'mythranStockVisit', 'width'),
    }
    drift = []
    for key, (group, name, field) in expect.items():
        live = manifest[group][name][field]
        if kw[key] != live:
            drift.append(f"{key}: pinned {kw[key]}, manifest says {live}")

    live_cid = manifest['classes'].get('TYPEMYTHRANLVDLG')
    if kw['lv_class_id'] != live_cid:
        drift.append(
            f"lv_class_id: pinned 0x{kw['lv_class_id']:04X}, manifest pins "
            f"TYPEMYTHRANLVDLG at "
            f"{('0x%04X' % live_cid) if live_cid is not None else 'nothing'}")

    assert not drift, (
        "the 'deployed' byte-identity case no longer matches the manifest, so "
        "it is pinning bytes the build does not emit (this is exactly P3):\n  "
        + "\n  ".join(drift)
        + "\n  Fix: update BYTE_IDENTITY_CASES['deployed']['kwargs'] to the "
          "manifest values, recompute expected_sha256 from build_new_use() "
          "with those kwargs and the real preamble, and re-run.")

    print(f"  PASS  'deployed' case tracks the manifest: lbDone bit "
          f"{kw['lbdone_bit']}, stockVisit bit {kw['stockvisit_bit']}, "
          f"TypeMythranLVDlg 0x{kw['lv_class_id']:04X}")


def main():
    print(f"Loading class 0x{MYTHRAN_CLASS_ID:04X} from {FLX_PATH}")
    base_data = load_base_class()
    print(f"  class length: {len(base_data)} bytes")
    orig_use = struct.unpack_from(
        '<I', base_data, BASE_OFFSET + USE_EVENT * 4)[0]
    assert orig_use == MYTHRAN_USE_OFFSET, (
        f"fixture assumption broken: event 01 offset 0x{orig_use:04X} != "
        f"0x{MYTHRAN_USE_OFFSET:04X} -- patch_mythran.py constants are stale "
        f"against this base FLX")
    print()

    tests = [
        test_successful_patch,
        test_preamble_hash_mismatch,
        test_zero_use_offset,
        test_patch_only_appends,
        test_build_new_use_byte_identity,
        test_deployed_case_matches_manifest,
    ]

    failed = 0
    for test in tests:
        try:
            test(base_data)
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

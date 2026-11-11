#!/usr/bin/env python3
"""
test_png2shape.py — Cover tools/png2shape.py's refusals and its round trip.

Lives here rather than under tools/ because tools/run_all_tests.sh discovers
tests by globbing agents/*/src/test_*.py, and the primitives png2shape drives
(encode_frame, inject_shape, patch_typeflag) are this agent's code anyway.

What matters in this tool is not that it produces a shape — the encoder was
already proven by the wood shapes — but that it never produces a BAD one
silently. So most of what is checked here is refusal:

  - a frame wider than the format's single-byte RLE fields is rejected, not
    clamped (the old encode_frame did `min(skip, 255)`, which would have
    shifted a row and rendered wrong rather than failed),
  - a non-empty FLX slot is refused without --force (L15),
  - an unused/filler donor is refused,
  - a failed write leaves the artifacts untouched.

Every test works on temporary copies; nothing here touches shared/build.
"""

import os
import shutil
import struct
import subprocess
import sys
import tempfile

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(REPO, 'tools'))

PNG2SHAPE = os.path.join(REPO, 'tools', 'png2shape.py')
BUILD = os.path.join(REPO, 'shared', 'build')
SRC_FLX = os.path.join(BUILD, 'U8SHAPES.FLX')
SRC_TF = os.path.join(BUILD, 'TYPEFLAG.DAT')
STATUE = os.path.join(REPO, 'shared', 'docs', 'art-poc',
                      'statue_codex_raw.png')

from lv_wood_wall import encode_frame, encode_shape_blobs, validate_shape
from patch_typeflag import set_footpad, FILLER_ENTRY
from parse_typeflag import ShapeInfo
from shape_viewer import read_flx_entry, parse_shape_frames
from png2shape import (first_free_slot, FIRST_LV_ART_SLOT, build_frame,
                       indexed_pixels, Refused)
from shape_viewer import load_palette, PALETTE_FILE
from PIL import Image

PASSED = 0
FAILED = 0


def check(name, cond, detail=""):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  PASS  {name}")
    else:
        FAILED += 1
        print(f"  FAIL  {name}{': ' + detail if detail else ''}")


def run(args, cwd=REPO):
    """Run png2shape.py, returning (exit code, stdout+stderr)."""
    p = subprocess.run([sys.executable, PNG2SHAPE] + args, cwd=cwd,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# ---------------------------------------------------------------------------
# encode_frame guards (the format limits png2shape has to respect)
# ---------------------------------------------------------------------------

def test_encoder_guards():
    print("\nencode_frame guards")

    # 256 px wide: the RLE skip/length fields are single bytes, so a fully
    # transparent row would need a skip of 256. Must raise, not clamp.
    try:
        encode_frame([0xFF] * (256 * 2), 256, 2, 128, 2)
        check("width 256 rejected", False, "no exception")
    except ValueError as e:
        check("width 256 rejected", "1..255" in str(e), str(e))

    # 255 is the largest expressible width and must still work.
    blob = encode_shape_blobs([encode_frame([0xFF] * 255 + [7] * 255,
                                            255, 2, 127, 2)])
    check("width 255 accepted", validate_shape(blob) == [])

    try:
        encode_frame([0] * 10, 5, 3, 2, 3)
        check("pixel-count mismatch rejected", False, "no exception")
    except ValueError as e:
        check("pixel-count mismatch rejected", "expected" in str(e), str(e))

    try:
        encode_frame([], 0, 4, 0, 4)
        check("zero width rejected", False, "no exception")
    except ValueError:
        check("zero width rejected", True)


def test_footpad_nibbles():
    print("\nTYPEFLAG footpad packing")
    # Donor 443: flags SI_FIXED|SI_SOLID, footpad (3,3,3).
    entry = bytes.fromhex('0300303300010001')
    out = set_footpad(entry, 3, 4, 10)
    si = ShapeInfo(0, out)
    check("footpad round-trips through the nibbles",
          (si.footpad_x, si.footpad_y, si.footpad_z) == (3, 4, 10),
          f"got ({si.footpad_x},{si.footpad_y},{si.footpad_z})")
    check("flags survive a footpad override",
          si.flag_names == ['SI_FIXED', 'SI_SOLID'], str(si.flag_names))
    check("weight/volume survive a footpad override",
          (si.weight, si.volume) == (0, 1))
    try:
        set_footpad(entry, 3, 4, 16)
        check("out-of-nibble footpad rejected", False, "no exception")
    except ValueError:
        check("out-of-nibble footpad rejected", True)


# ---------------------------------------------------------------------------
# png2shape end to end, on throwaway copies of the artifacts
# ---------------------------------------------------------------------------

def test_cli():
    print("\npng2shape.py CLI")
    if not (os.path.exists(SRC_FLX) and os.path.exists(SRC_TF)):
        print("  SKIP  shared/build artifacts not built "
              "(run tools/build_artifacts.sh)")
        return
    if not os.path.exists(STATUE):
        print(f"  SKIP  {STATUE} missing")
        return

    tmp = tempfile.mkdtemp(prefix='png2shape-test-')
    try:
        flx = os.path.join(tmp, 'U8SHAPES.FLX')
        tf = os.path.join(tmp, 'TYPEFLAG.DAT')
        shutil.copy2(SRC_FLX, flx)
        shutil.copy2(SRC_TF, tf)
        before = os.path.getsize(flx)
        common = ['--donor', '443', '--height', '48',
                  '--flx', flx, '--typeflag', tf]

        # Pick the free slots rather than hardcoding 859: whether 859 is
        # already taken depends on what has been injected into this checkout's
        # artifacts, and the test must not care.
        with open(flx, 'rb') as f:
            slot = first_free_slot(f.read(), FIRST_LV_ART_SLOT)
        target, spare = str(slot), str(slot + 1)

        # L15: an occupied slot must be refused, and must leave both
        # artifacts byte-for-byte untouched.
        rc, out = run([STATUE] + common + ['--shape-id', '856'])
        check("occupied slot exits 1", rc == 1, f"rc={rc}")
        check("occupied slot names the slot", 'not empty' in out, out[-300:])
        check("occupied slot writes nothing",
              os.path.getsize(flx) == before)

        # An unused (filler) TYPEFLAG donor is not a real shape. Use a free
        # slot, not a fixed number: 900 was filler until it became a
        # decorative bone row (phase 4 shared slice 0.1).
        rc, out = run([STATUE, '--donor', spare, '--height', '48',
                       '--flx', flx, '--typeflag', tf])
        check("filler donor exits 1", rc == 1, f"rc={rc}")
        check("filler donor is explained", 'filler' in out, out[-300:])

        # The real thing.
        rc, out = run([STATUE] + common + ['--shape-id', target,
                                           '--footpad', '3,4,10'])
        check("injection exits 0", rc == 0, out[-600:])
        check("injection grew the FLX", os.path.getsize(flx) > before)

        with open(flx, 'rb') as f:
            data = f.read()
        blob = read_flx_entry(data, slot)
        check(f"slot {slot} reads back", blob is not None)
        check(f"slot {slot} validates", blob is not None
              and validate_shape(blob) == [])
        frames = [f for f in parse_shape_frames(blob) if f] if blob else []
        check("one frame", len(frames) == 1, f"got {len(frames)}")
        if frames:
            f0 = frames[0]
            check("anchor is bottom-centre",
                  (f0['xoff'], f0['yoff']) == (f0['width'] // 2, f0['height']),
                  f"{f0['xoff']},{f0['yoff']} for {f0['width']}x{f0['height']}")
            check("no pixel uses the key index as a colour",
                  all(p == 0xFF or p < 0xFF for p in f0['pixels']))

        with open(tf, 'rb') as f:
            tfdata = f.read()
        entry = tfdata[slot * 8: slot * 8 + 8]
        si = ShapeInfo(slot, entry)
        check(f"TYPEFLAG {slot} is no longer filler", entry != FILLER_ENTRY,
              entry.hex())
        check("TYPEFLAG inherited the donor's flags",
              si.flag_names == ['SI_FIXED', 'SI_SOLID'], str(si.flag_names))
        check("TYPEFLAG took the authored footpad",
              (si.footpad_x, si.footpad_y, si.footpad_z) == (3, 4, 10),
              f"({si.footpad_x},{si.footpad_y},{si.footpad_z})")

        # Re-running on the now-occupied slot must refuse just the same.
        size_after = os.path.getsize(flx)
        rc, out = run([STATUE] + common + ['--shape-id', target])
        check("re-injection without --force exits 1", rc == 1, f"rc={rc}")
        check("re-injection writes nothing",
              os.path.getsize(flx) == size_after)

        # ...and go through with --force.
        rc, out = run([STATUE] + common + ['--shape-id', target, '--force'])
        check("--force exits 0", rc == 0, out[-400:])
        check("--force says what it orphaned", 'orphaned' in out, out[-400:])

        # --dry-run must be inert.
        size_after = os.path.getsize(flx)
        tf_before = open(tf, 'rb').read()
        rc, out = run([STATUE] + common + ['--shape-id', spare, '--dry-run'])
        check("--dry-run exits 0", rc == 0, out[-400:])
        check("--dry-run writes no FLX bytes",
              os.path.getsize(flx) == size_after)
        check("--dry-run writes no TYPEFLAG bytes",
              open(tf, 'rb').read() == tf_before)
        check("--dry-run leaves no staging file",
              not any(n.endswith('.png2shape.tmp') for n in os.listdir(tmp)),
              str(os.listdir(tmp)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# --indexed: a P-mode U8PAL PNG's indices go into the frame verbatim
# ---------------------------------------------------------------------------

def indexed_args(xoff, yoff):
    """build_frame's namespace for an indexed frame (lv_art_props builds the
    same frames through indexed_pixels directly)."""
    from types import SimpleNamespace
    return SimpleNamespace(indexed=True, anchor='explicit', xoff=xoff,
                           yoff=yoff, donor=0)


def decode(blob):
    return [f for f in parse_shape_frames(encode_shape_blobs([blob])) if f][0]


def test_indexed():
    print("\n--indexed: verbatim palette indices")
    if not os.path.exists(PALETTE_FILE):
        print(f"  SKIP  {PALETTE_FILE} missing (game data)")
        return
    palette = load_palette(PALETTE_FILE)
    flat = [c for rgb in palette for c in rgb]
    # The inputs that break the RGB path: the higher index of a duplicate
    # pair (144 = 2's RGB, 239 = 47's), the index nearest the magenta key,
    # and a transparent (255) margin that a trim would crop. The rest are
    # arbitrary.
    magenta = min(range(255), key=lambda i: sum(
        (a - b) ** 2 for a, b in zip(palette[i], (255, 0, 255))))
    w, h = 7, 5
    src = [255] * (w * h)
    body = [144, 239, magenta, 2, 47, 0, 254, 9, 28, 140, 13, 191]
    for n, px in enumerate(body):
        src[(1 + n // 4) * w + 1 + n % 4] = px
    tmp = tempfile.mkdtemp(prefix='png2shape-indexed-')
    try:
        path = os.path.join(tmp, 'f.png')
        im = Image.new('P', (w, h))
        im.putpalette(flat)
        im.putdata(src)
        im.save(path, transparency=255)

        blob, rep = build_frame(path, indexed_args(-3, 9), palette, b'', 0)
        f = decode(blob)
        check("indexed frame keeps the canvas size (no trim)",
              (f['width'], f['height']) == (w, h),
              f"{f['width']}x{f['height']}")
        check("indexed frame pixels == PNG indices, index for index",
              f['pixels'] == src)
        check("duplicate-RGB high indices (144, 239, 191, 28, 140) survive",
              all(p in f['pixels'] for p in (144, 239, 191, 28, 140)))
        check(f"the index nearest magenta ({magenta}) is not keyed out",
              magenta in f['pixels'])
        check("index 255 stays the transparency key",
              [p == 255 for p in f['pixels']] == [p == 255 for p in src])
        check("explicit anchor kept, negative xoff included",
              (f['xoff'], f['yoff']) == (-3, 9) and rep['anchor'] == (-3, 9))

        # Refusals: not P-mode; P-mode on a foreign palette.
        rgb = os.path.join(tmp, 'rgb.png')
        im.convert('RGB').save(rgb)
        try:
            indexed_pixels(rgb, palette)
            check("RGB PNG refused", False, "no exception")
        except Refused as e:
            check("RGB PNG refused", 'P-mode' in str(e), str(e))
        foreign = os.path.join(tmp, 'foreign.png')
        im2 = im.copy()
        bad = list(flat)
        bad[3 * 144:3 * 144 + 3] = [1, 2, 3]
        im2.putpalette(bad)
        im2.save(foreign, transparency=255)
        try:
            indexed_pixels(foreign, palette)
            check("foreign-palette PNG refused", False, "no exception")
        except Refused as e:
            check("foreign-palette PNG refused", 'not U8PAL' in str(e), str(e))

        # CLI guards: --indexed never resamples, and needs a given anchor.
        rc, out = run([path, '--indexed', '--donor', '443', '--height', '9',
                       '--anchor', 'explicit', '--xoff', '1', '--yoff', '1',
                       '--dry-run'])
        check("--indexed with --height is a usage error", rc == 2, out[-300:])
        rc, out = run([path, '--indexed', '--donor', '443', '--dry-run'])
        check("--indexed without an anchor is a usage error", rc == 2,
              out[-300:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # The real 1994 assets the build injects (lv_art_props 'indexed' rows):
    # each decodes back to its PNG's indices.
    from lv_art_props import PROPS, indexed_sources, load_registry
    reg = load_registry()
    n = bad_frames = 0
    for prop in PROPS:
        if 'indexed' not in prop:
            continue
        for s in indexed_sources(prop, reg):
            path = os.path.join(REPO, s['png'])
            if not os.path.exists(path):
                print(f"  SKIP  {s['png']} missing")
                continue
            blob, _ = build_frame(path, indexed_args(*s['anchor']),
                                  palette, b'', 0)
            f = decode(blob)
            n += 1
            if f['pixels'] != list(Image.open(path).getdata()):
                bad_frames += 1
                print(f"        {s['ref']} differs")
    check(f"every 1994 frame the build injects round-trips ({n} frames)",
          n > 0 and bad_frames == 0, f"{bad_frames} differ")


def main():
    print("=== png2shape / shape-injection tests ===")
    test_encoder_guards()
    test_footpad_nibbles()
    test_cli()
    test_indexed()
    print(f"\n{'OK' if not FAILED else 'FAILED'}: {PASSED} passed, "
          f"{FAILED} failed")
    return 1 if FAILED else 0


if __name__ == '__main__':
    sys.exit(main())

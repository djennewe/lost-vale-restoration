#!/usr/bin/env python3
"""
lv_tiny_tar.py — generate and inject the Tiny Tar potion shape (DD-005).

WHY THIS EXISTS
---------------
`POTION.UNK::use()` — the 1994 potion class, compiled as TYPEPOTION (1253)
and dispatched by npcNum 229 — branches on the item's FRAME:

    0 empty   1 heal   2 mana   3 heal-variant   4 damage
    5 protection   6 (spawns an item)   7 invisibility   8 TINY TAR

Frame 8 spawns `makeAvatarTiny()`, waits 2000 ticks (~33 s at 60/s) and
spawns `makeAvatarBig()`, which kills the Avatar if a full-size body cannot
fit where it re-grows. That is the shrink, and per DD-005 it is how the
player enters the Ancient Temple: through a 32-unit crack in the Inner
Sanctum wall that admits a 32x32 body and refuses a 64x64 one.

The problem: the base game's potion, shape **766**, has only **8 frames
(0-7)**. The expansion needed a ninth and it did not survive — no frame-8
potion can render or be placed, so nothing in the game can shrink the
Avatar and the sealed temple is unreachable by any means.

WHAT THIS BUILDS
----------------
Shape **859** (the first LV custom-art slot; 855 unallocated, 856-858 are
the wood-plank walls): a 9-frame copy of 766. Frames 0-7 are byte-faithful
re-encodes of the originals; frame 8 is frame 1 (the red potion) with only
its LIQUID recoloured to tar.

The liquid is isolated exactly rather than guessed: every frame of 766
shares one geometry (9x14 at offset 5,13), so the liquid is precisely the
36 pixels where frame 1 differs from frame 0 (the empty vial). Those use a
four-tone red ramp, remapped tone-for-tone onto the palette's warm dark
ramp so the glass, cork and highlights are untouched and the shading
survives:

    44 (97,0,0)      -> 223 (16,4,0)    darkest
    41 (154,4,4)     -> 220 (44,16,0)
    36 (223,81,81)   -> 217 (73,36,12)
    33 (247,195,195) -> 214 (105,60,32) highlight

This follows lv_wood_wall.py exactly — derive a new shape from base-game
art, inject it, patch TYPEFLAG — and like that module it is a step in
tools/build_artifacts.sh, so the injection survives an artifact rebuild
instead of being silently dropped.

Usage:
    python3 lv_tiny_tar.py [--out PATH] [--src PATH] [--preview]
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shape_viewer import read_flx_entry, parse_shape_frames, load_palette, \
    PALETTE_FILE, SHAPES_FLX                                    # noqa: E402
from lv_wood_wall import encode_frame, encode_shape_blobs, inject_shape, \
    validate_shape, num_frames                                  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    '..', '..', '..', 'shared')
OUT_SHAPES = os.path.join(ROOT, 'build', 'U8SHAPES.FLX')

DONOR_SHAPE = 766          # engine name "potion"; 8 frames, all 9x14
TINY_TAR_ID = 859          # first LV custom-art slot (see CLAUDE.md)
TINY_TAR_FRAME = 8         # the frame POTION.UNK branches on

# Red liquid tone -> tar tone. Keys are the four palette indices the donor's
# liquid actually uses; values walk the palette's warm dark ramp (212-223)
# so the four-step shading is preserved rather than flattened to black.
TAR_REMAP = {
    44: 223,   # (97,0,0)      -> (16,4,0)
    41: 220,   # (154,4,4)     -> (44,16,0)
    36: 217,   # (223,81,81)   -> (73,36,12)
    33: 214,   # (247,195,195) -> (105,60,32)
}


def build_tiny_tar_frames(shape_data):
    """Return [frame_blob, ...] for a 9-frame Tiny Tar potion.

    Frames 0-7 re-encode the donor unchanged. Frame 8 is frame 1 with the
    liquid — the pixels that differ from the empty frame 0 — remapped.
    """
    frames = parse_shape_frames(shape_data)
    if len(frames) < 2:
        raise SystemExit(f"donor shape {DONOR_SHAPE} has {len(frames)} frames; "
                         f"need at least 2 (empty + a filled one)")
    f0, f1 = frames[0], frames[1]
    geo = ('width', 'height', 'xoff', 'yoff')
    if any(f0[k] != f1[k] for k in geo):
        raise SystemExit("donor frames 0 and 1 differ in geometry; the "
                         "liquid-by-difference trick is not valid here")

    blobs = [encode_frame(f['pixels'], f['width'], f['height'],
                          f['xoff'], f['yoff']) for f in frames]

    tar = list(f1['pixels'])
    liquid = [i for i, (a, b) in enumerate(zip(f0['pixels'], f1['pixels']))
              if a != b]
    if not liquid:
        raise SystemExit("frames 0 and 1 are identical; cannot locate the "
                         "liquid to recolour")
    unmapped = set()
    for i in liquid:
        src = tar[i]
        if src in TAR_REMAP:
            tar[i] = TAR_REMAP[src]
        else:
            unmapped.add(src)
    if unmapped:
        raise SystemExit(
            f"donor liquid uses palette indices {sorted(unmapped)} that "
            f"TAR_REMAP does not cover — the base art changed; update the "
            f"remap rather than letting a red potion ship as Tiny Tar")

    blobs.append(encode_frame(tar, f1['width'], f1['height'],
                              f1['xoff'], f1['yoff']))
    return blobs, len(liquid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=OUT_SHAPES)
    ap.add_argument('--src', default=None,
                    help='source U8SHAPES.FLX (default: the pristine base)')
    ap.add_argument('--preview', action='store_true',
                    help='write a PNG of every frame instead of injecting')
    args = ap.parse_args()

    src = args.src
    if src is None:
        # Same guard the other artifact builders use: install_lv.sh writes
        # into the base-input directory, so prefer the pristine .bak.
        from base_input import pristine_base
        src = pristine_base(SHAPES_FLX, None, 'base U8SHAPES.FLX')

    print("=== LV Tiny Tar Potion (DD-005) ===")
    # The donor must come from whatever we are injecting INTO, so that a
    # rebuild on top of an already-patched file still reads a real 766.
    base = open(src, 'rb').read()
    donor = read_flx_entry(base, DONOR_SHAPE)
    if not donor:
        raise SystemExit(f"donor shape {DONOR_SHAPE} missing from {src}")

    blobs, n_liquid = build_tiny_tar_frames(donor)
    blob = encode_shape_blobs(blobs)
    print(f"  donor shape {DONOR_SHAPE}: {num_frames(donor)} frames")
    print(f"  recoloured {n_liquid} liquid pixels for frame {TINY_TAR_FRAME}")
    print(f"  new shape {TINY_TAR_ID}: {len(blobs)} frames, {len(blob)} bytes")

    # validate_shape returns a LIST OF ERRORS; empty means safe to load.
    errs = validate_shape(blob)
    if errs:
        raise SystemExit("generated shape failed validation:\n  " +
                         "\n  ".join(errs))
    print("  validate_shape: clean (engine pointer walk simulated)")

    if args.preview:
        from lv_wood_wall import preview
        dst = '/tmp/U8SHAPES_tinytar.FLX'
        inject_shape(blob, TINY_TAR_ID, src, dst)
        preview(TINY_TAR_ID, load_palette(PALETTE_FILE), shapes_flx=dst,
                out='/tmp/tinytar.png', nframes=9)
        print("  preview -> /tmp/tinytar.png")
        return

    inject_shape(blob, TINY_TAR_ID, args.out if os.path.exists(args.out)
                 else src, args.out)
    print(f"  injected into {args.out}")

    # TYPEFLAG: copy the donor's entry so the new shape inherits "carryable
    # potion" wholesale — weight, volume, family SF_QUALITY, not SI_FIXED.
    from patch_typeflag import patch_entry_in_file
    tf = os.path.join(ROOT, 'build', 'TYPEFLAG.DAT')
    old, new = patch_entry_in_file(tf, TINY_TAR_ID, DONOR_SHAPE)
    print(f"  TYPEFLAG slot {TINY_TAR_ID} <- {DONOR_SHAPE}: "
          f"{old.hex()} -> {new.hex()}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
lv_god_statues.py — inject the three Zealan gods as shape 860 (42 frames).

WHY THIS EXISTS
---------------
Map 18's Inner Sanctum stages the three imprisoned gods. Base-game stand-ins
came first (shape 400 `fire field`, which burned the player on the ceremony
triangle; then 443 `statue`), then our own amber art (2026-09-13). Since
2026-10-17 the sealed gods are the 1994 team's own: screenshot screen04
shows all three in amber on their plinths, and the reconstruction cut them
out pixel for pixel (vignettes/art_registry.json 2010-2012,
docs/research/2026-10-16-screenshot-reconstruction.md).

THE FRAME TABLE, AND WHY THE ORDER MATTERS
------------------------------------------
    0 1 2     SEALED   Felicitar, Doloras, Timyra: the 1994 pixels
    3 4 5     FREED    the same three standing, at rest
    6..41     RUNS     three 12-frame runs, 6 shatter + 6 wake, one per god

build_map_18.py places frames 0/1/2 and test_sanctum_clearance.py asserts
them; AOSCENE.UNK kicks god E into run 6 + 12*E; GODANIM.UNK (usecode class
860) steps a run and ends it on frame E + 3; TEMPLENT.UNK maps a god caught
mid-run back onto her rest frame. test_god_animation.py holds the four
together.

EVERY FRAME IS IMPORTED INDEXED (png2shape.indexed_pixels): the P-mode
PNG's U8PAL indices go in verbatim at an explicit hotspot.
  - Frames 0-2 are the registry PNGs at the registry hotspots (Felicitar
    carries 42 inferred pixels at her right foot, hidden in the shot behind
    the striped prop on her plinth).
  - Frames 3-41 are lv_god_frames.py's output, redrawn from the 2026 art at
    the 1994 scale and on the 1994 statues' palette, with each run starting
    on the 1994 statue itself; `run/anchors.json` carries their hotspots.

Like lv_wood_wall.py and lv_tiny_tar.py this is a step in
tools/build_artifacts.sh, so the injection survives an artifact rebuild
instead of being silently dropped (.claude/rules/shape-ids.md).

Usage:
    python3 lv_god_statues.py [--out PATH] [--src PATH] [--preview]
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.join(HERE, '..', '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'tools'))

from shape_viewer import load_palette, PALETTE_FILE, SHAPES_FLX   # noqa: E402
from lv_wood_wall import (encode_frame, encode_shape_blobs,      # noqa: E402
                          inject_shape, validate_shape)
from png2shape import indexed_pixels, Refused                    # noqa: E402

SHARED = os.path.join(ROOT, 'shared')
OUT_SHAPES = os.path.join(SHARED, 'build', 'U8SHAPES.FLX')
ART = os.path.join(SHARED, 'docs', 'art-poc', 'gods')
RUN = os.path.join(ART, 'run')
REGISTRY = os.path.join(HERE, 'vignettes', 'art_registry.json')

GODS_SHAPE_ID = 860        # 859 is the Tiny Tar; custom art starts at 859
DONOR_SHAPE = 443          # "statue": SI_FIXED|SI_SOLID, the flags we want

# THE FOOTPAD IS 64x64x56 (2, 2, 7). The reconstruction solved each 1994
# god on a 64x64 base, standing on its plinth at z 16 (registry footprints
# 64x64x40, 64x64x24 and 64x64x56). TYPEFLAG holds one footpad per shape,
# and the three share shape 860 because the usecode class is the shape
# number (item.cpp:1516), so the box is the tallest of the three: Timyra's
# 56, which also holds a freed god (~59 px over a 16 px base diamond is
# 7 z-units). It was (6, 6, 8), 192x192x64, for the 2026 art's 96-px blocks.
FOOTPAD = (2, 2, 7)

# (animType, animData, animSpeed). Type 5 is "call the item's usecode anim()",
# and the engine takes that class from the SHAPE NUMBER, so it lands in class
# 860 — lv-new/GODANIM.UNK, pinned in lv_manifest.json. animData is unused by
# type 5.
#
# animSpeed is a DIVISOR on the game tick (`gametick % animSpeed == 0`) and
# must not be 0. It is the only pacing control the run has: at 1 the twelve
# frames would be gone in twelve ticks. 6 is what retail DRIPS uses on the
# same mechanism, and puts a god's shatter-and-wake at 72 ticks.
ANIM = (5, 0, 6)

GOD_NAMES = ('felicitar', 'doloras', 'timyra')
STATUES = (2010, 2011, 2012)          # registry ids, in frame order 0/1/2

RUN_BASE = 6
RUN_LEN = 12
SHATTER_LEN = 6


def _frames():
    """[(repo-relative PNG, (xoff, yoff)), ...] for all 42 frames."""
    with open(REGISTRY) as f:
        reg = json.load(f)['shapes']
    with open(os.path.join(RUN, 'anchors.json')) as f:
        anchors = json.load(f)['gods']
    rel = lambda p: os.path.relpath(p, ROOT)                     # noqa: E731
    out = []
    for sid in STATUES:
        fr = reg[str(sid)]['frames'][0]
        if fr['grade'] in ('reference-only', 'residual'):
            raise SystemExit(f'registry {sid} is graded {fr["grade"]}')
        out.append((fr['png'], tuple(fr['hotspot'])))
    for name in GOD_NAMES:
        out.append((rel(os.path.join(RUN, f'{name}_rest.png')),
                    tuple(anchors[name]['rest'])))
    for name in GOD_NAMES:
        for k in range(RUN_LEN):
            out.append((rel(os.path.join(RUN, f'{name}_{k:02d}.png')),
                        tuple(anchors[name]['run'])))
    return out


FRAMES = _frames()
NAMES = ([f'{g.capitalize()} sealed (1994)' for g in GOD_NAMES] +
         [f'{g.capitalize()} standing' for g in GOD_NAMES] +
         [f'{g.capitalize()} {"shatter" if k < SHATTER_LEN else "wake"} '
          f'{k if k < SHATTER_LEN else k - SHATTER_LEN}'
          for g in GOD_NAMES for k in range(RUN_LEN)])

assert len(FRAMES) == RUN_BASE + 3 * RUN_LEN == 42, len(FRAMES)
assert len(NAMES) == len(FRAMES)


def build_frames(palette):
    blobs, reports = [], []
    for rel, (xoff, yoff) in FRAMES:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            raise SystemExit(f"missing god art: {path}")
        try:
            pixels, w, h, used = indexed_pixels(path, palette)
        except Refused as exc:
            raise SystemExit(f"god art {rel}: {exc}")
        blobs.append(encode_frame(pixels, w, h, xoff, yoff))
        reports.append({'path': rel, 'size': (w, h), 'colors': len(used),
                        'anchor': (xoff, yoff), 'bytes': len(blobs[-1])})
    return blobs, reports


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=OUT_SHAPES)
    ap.add_argument('--src', default=None,
                    help='source U8SHAPES.FLX (default: the pristine base)')
    ap.add_argument('--preview', action='store_true',
                    help='inject into a temp FLX and render every frame')
    args = ap.parse_args()

    src = args.src
    if src is None:
        from base_input import pristine_base
        src = pristine_base(SHAPES_FLX, None, 'base U8SHAPES.FLX')

    print("=== LV Zealan gods (shape 860, 42 frames) ===")
    palette = load_palette(PALETTE_FILE)

    blobs, reports = build_frames(palette)
    for i, (name, r) in enumerate(zip(NAMES, reports)):
        w, h = r['size']
        print(f"  frame {i:>2}  {name:<24} {w:>3}x{h:<3} @{r['anchor']}  "
              f"{r['colors']:>3} colours  {r['bytes']:>6} B")

    blob = encode_shape_blobs(blobs)
    print(f"  shape {GODS_SHAPE_ID}: {len(blobs)} frames, {len(blob)} bytes")

    # validate_shape returns a LIST of errors; empty means safe to load.
    errs = validate_shape(blob)
    if errs:
        raise SystemExit("generated shape failed validation:\n  " +
                         "\n  ".join(errs))
    print("  validate_shape: clean (engine pointer walk simulated)")

    if args.preview:
        from lv_wood_wall import preview
        dst = '/tmp/U8SHAPES_gods.FLX'
        inject_shape(blob, GODS_SHAPE_ID, src, dst)
        preview(GODS_SHAPE_ID, palette, shapes_flx=dst,
                out='/tmp/gods.png', nframes=len(blobs))
        print("  preview -> /tmp/gods.png")
        return

    inject_shape(blob, GODS_SHAPE_ID,
                 args.out if os.path.exists(args.out) else src, args.out)
    print(f"  injected into {args.out}")

    # TYPEFLAG: the donor's flags (SI_FIXED|SI_SOLID) are right for something
    # the player walks around and cannot pick up; its footpad is not.
    from patch_typeflag import patch_entry_in_file
    tf = os.path.join(SHARED, 'build', 'TYPEFLAG.DAT')
    old, new = patch_entry_in_file(tf, GODS_SHAPE_ID, DONOR_SHAPE,
                                   footpad=FOOTPAD, anim=ANIM)
    print(f"  TYPEFLAG slot {GODS_SHAPE_ID} <- {DONOR_SHAPE} "
          f"footpad {FOOTPAD} anim {ANIM}: {old.hex()} -> {new.hex()}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
shape_render.py — Render arbitrary U8SHAPES.FLX shape IDs to contact-sheet
                  PNGs, for visual identification/audit of shape constants.

Usage:
    python3 shape_render.py 205 307 721 --out /tmp/audit
        Writes one <shape_id>.png contact sheet (first 6 frames) per shape
        into --out.

    python3 shape_render.py --range 800 850 --out /tmp/audit
        Renders every shape ID in [800, 850).

Reuses the FLX/shape parsing from shape_viewer.py so both tools stay in
sync with the same U8 shape-format decoder.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shape_viewer import (read_flx_entry, load_palette, parse_shape_frames,
                           frame_to_image, SHAPES_FLX, PALETTE_FILE)
from PIL import Image, ImageDraw

try:
    from PIL import ImageFont
    FONT = ImageFont.load_default()
except Exception:
    FONT = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
BUILD_SHAPES_FLX = os.path.join(BASE_DIR, "shared", "build", "U8SHAPES.FLX")


def effective_shapes_flx():
    """Prefer the patched build copy so custom LV shapes render too."""
    if os.path.exists(BUILD_SHAPES_FLX):
        return BUILD_SHAPES_FLX
    return SHAPES_FLX


def render_shape(shape_id, flx_data, palette, out_dir, label=""):
    shape_data = read_flx_entry(flx_data, shape_id)
    if shape_data is None:
        print(f"{shape_id:5d}  NO DATA (bad shape id)")
        return None
    frames = parse_shape_frames(shape_data)
    valid = [fr for fr in frames if fr is not None]
    if not valid:
        print(f"{shape_id:5d}  NO VALID FRAMES")
        return None

    sample = valid[:6]
    imgs = [frame_to_image(fr, palette, scale=3) for fr in sample]
    imgs = [im for im in imgs if im is not None]
    if not imgs:
        print(f"{shape_id:5d}  RENDER FAILED")
        return None

    pad = 6
    label_h = 16
    w = sum(im.width for im in imgs) + pad * (len(imgs) + 1)
    h = max(im.height for im in imgs) + pad * 2 + label_h
    sheet = Image.new('RGB', (w, h), (30, 30, 30))
    draw = ImageDraw.Draw(sheet)
    x = pad
    for im in imgs:
        sheet.paste(im, (x, pad + label_h))
        x += im.width + pad
    title = f"shape {shape_id} ({len(valid)} frames)"
    if label:
        title += f" -- {label}"
    draw.text((pad, 2), title, fill=(255, 255, 0), font=FONT)

    out_path = os.path.join(out_dir, f"{shape_id:04d}.png")
    sheet.save(out_path)
    print(f"{shape_id:5d}  {len(valid)} frames OK  -> {out_path}")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ids', nargs='*', type=int, help='Shape IDs to render')
    ap.add_argument('--range', nargs=2, type=int, metavar=('START', 'END'),
                     help='Render every shape ID in [START, END)')
    ap.add_argument('--out', required=True, help='Output directory')
    ap.add_argument('--label', default='', help='Optional label suffix on each sheet')
    args = ap.parse_args()

    ids = list(args.ids)
    if args.range:
        ids.extend(range(args.range[0], args.range[1]))
    if not ids:
        ap.error("Provide shape IDs and/or --range START END")

    os.makedirs(args.out, exist_ok=True)

    palette = load_palette(PALETTE_FILE)
    shapes_path = effective_shapes_flx()
    print(f"Shapes source: {shapes_path}")
    with open(shapes_path, 'rb') as f:
        flx_data = f.read()

    for shape_id in ids:
        render_shape(shape_id, flx_data, palette, args.out, label=args.label)


if __name__ == '__main__':
    main()

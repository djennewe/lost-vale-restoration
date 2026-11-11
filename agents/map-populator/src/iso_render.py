#!/usr/bin/env python3
"""
iso_render.py — Composite a list of U8 MapItems into a single isometric PNG.

This is the shared "eyes" for the village-construction toolchain. Any building
source (hand-placed items, an extracted base-game region, or a GLOB.FLX cluster)
ultimately resolves to a list of MapItems; this module renders that list the way
the engine roughly draws it, so a building / village / glob can be previewed as
one image for visual QA and vision-model comparison against LV screenshots.

Reuses the shape-decoding core from shape_viewer.py (do not duplicate it).

World -> screen projection (U8 / Pentagram isometric convention):
    sx = (x - y) // XY_DIV
    sy = (x + y) // XYSUM_DIV - z * Z_SCALE
Each shape frame is pasted with its hotspot (xoff, yoff) subtracted, so the
frame's origin lands on the projected point. Items are drawn back-to-front
(painter's algorithm) keyed on (x + y, z, original-index).

Usage (library):
    from iso_render import IsoRenderer
    r = IsoRenderer()
    img = r.render(list_of_map_items, scale=2)
    img.save("preview.png")

Usage (CLI calibration — render a region of a base-game map):
    python3 iso_render.py --map 39 --x 16100 --y 18100 --w 1400 --h 1400 \
        --out /tmp/bldg.png --scale 3
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw

from shape_viewer import (
    read_flx_entry, load_palette, parse_shape_frames,
    SHAPES_FLX, PALETTE_FILE,
)

# ---------------------------------------------------------------------------
# Projection constants (U8 isometric). Calibrated visually against a known
# Tenebrae building — see __main__. Override per-call via render(z_scale=...).
# ---------------------------------------------------------------------------
XY_DIV = 4        # screen-x = (x - y) / XY_DIV
XYSUM_DIV = 8     # screen-y depth = (x + y) / XYSUM_DIV   (2:1 isometric)
Z_SCALE = 1.0     # screen-y lift per z unit


def frame_to_rgba(frame, palette):
    """Parsed shape frame -> (RGBA Image, xoff, yoff). None-safe.

    Unlike shape_viewer.frame_to_image, this keeps a transparent background so
    frames can be alpha-composited on top of each other.
    """
    if frame is None:
        return None, 0, 0
    w, h = frame['width'], frame['height']
    pixels = frame['pixels']
    out = bytearray(w * h * 4)
    for i, idx in enumerate(pixels):
        if idx != 0xFF:
            r, g, b = palette[idx]
            o = i * 4
            out[o] = r
            out[o + 1] = g
            out[o + 2] = b
            out[o + 3] = 255
    img = Image.frombytes('RGBA', (w, h), bytes(out))
    return img, frame['xoff'], frame['yoff']


class IsoRenderer:
    """Loads U8SHAPES.FLX + palette once; renders MapItem lists to PNGs.

    Frame decode results are cached per (shape, frame), so a village with
    hundreds of repeated wall/roof tiles renders quickly.
    """

    def __init__(self, shapes_flx=SHAPES_FLX, palette_file=PALETTE_FILE):
        with open(shapes_flx, 'rb') as f:
            self.flx = f.read()
        self.palette = load_palette(palette_file)
        self._frames_cache = {}   # shape_id -> parsed frame list
        self._img_cache = {}      # (shape_id, frame_idx) -> (RGBA|None, xoff, yoff)

    def _frames(self, shape_id):
        fl = self._frames_cache.get(shape_id)
        if fl is None:
            data = read_flx_entry(self.flx, shape_id)
            fl = parse_shape_frames(data) if data else []
            self._frames_cache[shape_id] = fl
        return fl

    def _img(self, shape_id, frame_idx):
        key = (shape_id, frame_idx)
        cached = self._img_cache.get(key)
        if cached is None:
            frames = self._frames(shape_id)
            frame = frames[frame_idx] if 0 <= frame_idx < len(frames) else None
            cached = frame_to_rgba(frame, self.palette)
            self._img_cache[key] = cached
        return cached

    def project(self, x, y, z, z_scale=Z_SCALE):
        sx = (x - y) // XY_DIV
        sy = (x + y) // XYSUM_DIV - int(round(z * z_scale))
        return sx, sy

    def render(self, items, scale=1, bg=(28, 28, 38), pad=8, z_scale=Z_SCALE,
               skip_shapes=(2, 73, 500, 508), marks=None):
        """Render MapItems to a PIL RGB Image.

        skip_shapes: special/egg shapes that have no sprite (glob egg, eggs,
        monster/teleport eggs) are skipped by default. To preview a glob,
        expand it to real items first.

        marks: optional list of dicts {x, y, z, color, label} drawn as labeled
        QA dots at the projected position (e.g. to flag NPC locations).
        """
        # Resolve each renderable item to (screen_x, screen_y, image), and the
        # canvas bounds.
        placements = []
        minx = miny = 10 ** 9
        maxx = maxy = -10 ** 9

        order = sorted(
            range(len(items)),
            key=lambda i: (items[i].x + items[i].y, items[i].z, i),
        )
        for i in order:
            it = items[i]
            if it.shape in skip_shapes:
                continue
            img, xoff, yoff = self._img(it.shape, it.frame)
            if img is None:
                continue
            sx, sy = self.project(it.x, it.y, it.z, z_scale)
            # Frame origin (hotspot) sits at (sx, sy); top-left = origin - hotspot
            px = sx - xoff
            py = sy - yoff
            placements.append((px, py, img))
            minx = min(minx, px)
            miny = min(miny, py)
            maxx = max(maxx, px + img.width)
            maxy = max(maxy, py + img.height)

        if not placements:
            return Image.new('RGB', (32, 32), bg)

        w = (maxx - minx) + 2 * pad
        h = (maxy - miny) + 2 * pad
        canvas = Image.new('RGBA', (w, h), bg + (255,))
        ox, oy = pad - minx, pad - miny
        for px, py, img in placements:
            canvas.alpha_composite(img, (px + ox, py + oy))

        out = canvas.convert('RGB')
        if scale != 1:
            out = out.resize((w * scale, h * scale), Image.NEAREST)

        if marks:
            draw = ImageDraw.Draw(out)
            for m in marks:
                sx, sy = self.project(m['x'], m['y'], m.get('z', 0), z_scale)
                px = (sx + ox) * scale
                py = (sy + oy) * scale
                col = m.get('color', (255, 0, 255))
                r = m.get('r', 5)
                draw.ellipse([px - r, py - r, px + r, py + r],
                             fill=col, outline=(255, 255, 255), width=2)
                if m.get('label'):
                    draw.text((px + r + 2, py - r), str(m['label']),
                              fill=(255, 255, 255))
        return out


def render_items_to_png(items, path, scale=2, **kw):
    """Convenience: render and save."""
    img = IsoRenderer().render(items, scale=scale, **kw)
    img.save(path)
    return path


# ---------------------------------------------------------------------------
# CLI — calibration / spot rendering of base-game map regions
# ---------------------------------------------------------------------------

def _main():
    import argparse
    from u8_map import MapArchive

    base_fixed = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))),
        "shared", "data", "u8-install", "STATIC", "FIXED.DAT")

    ap = argparse.ArgumentParser()
    ap.add_argument('--fixed', default=base_fixed)
    ap.add_argument('--map', type=int, required=True)
    ap.add_argument('--x', type=int, required=True)
    ap.add_argument('--y', type=int, required=True)
    ap.add_argument('--w', type=int, default=1200)
    ap.add_argument('--h', type=int, default=1200)
    ap.add_argument('--out', default='/tmp/iso_render.png')
    ap.add_argument('--scale', type=int, default=3)
    ap.add_argument('--zscale', type=float, default=Z_SCALE)
    args = ap.parse_args()

    arch = MapArchive(args.fixed)
    items = [it for it in arch.get_map_items(args.map)
             if args.x <= it.x < args.x + args.w
             and args.y <= it.y < args.y + args.h]
    print(f"Map {args.map}: {len(items)} items in region "
          f"({args.x},{args.y}) {args.w}x{args.h}")
    shapes = sorted({it.shape for it in items if it.shape not in (2, 73, 500, 508)})
    print(f"  distinct sprite shapes: {shapes}")
    img = IsoRenderer().render(items, scale=args.scale, z_scale=args.zscale)
    img.save(args.out)
    print(f"  wrote {args.out} ({img.width}x{img.height})")


if __name__ == '__main__':
    _main()

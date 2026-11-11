#!/usr/bin/env python3
"""
resin_encase.py — seal a generated statue in amber resin, locally.

WHY THIS EXISTS
---------------
The 1994 Art List asks for the three Zealan gods in TWO states: "Zealan God
1/2/3, encased in resin" and "Zealan God 1/2/3, speaking". Carrying both as
frames of one shape is what lets AOSCENE stage the freeing later
(`setFrame(n + 3)`) instead of narrating it as it does today.

A frame swap only reads as *the resin breaking* if the statue underneath is
the same statue. Re-prompting an image model for "the same idol, now encased"
re-rolls the idol; compositing the shell onto the chosen art cannot. So the
encasement is built here, from the picked render, and is reproducible from it.

IT WORKS AT GAME SCALE, ON PURPOSE
----------------------------------
The tool resizes to the final sprite height FIRST and composites after, for
one reason: the resin margin is a 50% checkerboard of amber and transparent —
the 1994 way to paint translucency in a palette with no alpha, and what makes
the shell read as glass instead of a painted outline. A checkerboard built at
the source's ~14x resolution averages back into flat fill under png2shape's
Lanczos downscale. Built here, at 1px granularity, it survives into the sprite.

So pass the result to png2shape at the SAME height it was built for:

    tools/resin_encase.py shared/docs/art-poc/gods/felicitar_B_raw.png \
        --out /tmp/resin --height 110
    tools/png2shape.py /tmp/resin/felicitar_B_resin.png --donor 443 \
        --height 110 --no-key --shape-id 860 --flx /tmp/scratch.flx \
        --no-typeflag --force --preview /tmp/felicitar_B_resin_x3.png

Quantization to U8PAL still happens in png2shape, not here.

The shell hugs the silhouette rather than boxing it. A slab would be closer to
the Dune shields the design doc cites, but the gods stand at the points of the
Map 18 ceremony triangle with props at +/-128 units, and the widest pick is
already 100px; a slab spends clearance the sanctum does not have.
"""

import argparse
import os
import sys

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
except ImportError:
    sys.exit("resin_encase.py needs Pillow (pip install pillow)")


def parse_hex(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def key_to_alpha(im, key, tolerance):
    """Magenta -> transparent, for sources that came back without alpha."""
    im = im.convert("RGB")
    kr, kg, kb = key
    px = im.load()
    alpha = Image.new("L", im.size, 255)
    ap = alpha.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            if (r - kr) ** 2 + (g - kg) ** 2 + (b - kb) ** 2 <= tolerance ** 2:
                ap[x, y] = 0
    im.putalpha(alpha)
    return im


def to_game_scale(im, height, key, tolerance):
    """Key, trim, and resize to the height the sprite will ship at."""
    if im.mode in ("RGBA", "LA") and im.getchannel("A").getextrema()[0] < 250:
        im = im.convert("RGBA")
    else:
        im = key_to_alpha(im, key, tolerance)

    box = im.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()
    if box:
        im = im.crop(box)

    w = max(1, round(im.width * height / im.height))
    im = im.resize((w, height), Image.LANCZOS)
    # Lanczos bleeds the edges; re-harden alpha so the silhouette stays crisp.
    im.putalpha(im.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    return im


def grow(mask, px):
    out = mask
    for _ in range(px):
        out = out.filter(ImageFilter.MaxFilter(3))
    return out


def shrink(mask, px):
    out = mask
    for _ in range(px):
        out = out.filter(ImageFilter.MinFilter(3))
    return out


def checker(size, phase=0):
    """1px checkerboard: the palette-era way to paint half-transparency."""
    w, h = size
    m = Image.new("L", (w, h), 0)
    mp = m.load()
    for y in range(h):
        for x in range(w):
            if (x + y) % 2 == phase:
                mp[x, y] = 255
    return m


def vertical_gradient(size, top, bottom):
    w, h = size
    g = Image.new("RGB", (1, h))
    gp = g.load()
    for y in range(h):
        t = y / max(1, h - 1)
        gp[0, y] = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return g.resize((w, h), Image.NEAREST)



def shade(rgb, gain):
    return tuple(max(0, min(255, round(c * gain))) for c in rgb)



def encase_gem(src, band, cut, taper, opacity, tint_top, tint_bottom,
               rim_gain, spec):
    """The figure sealed in a rough-cut amber crystal, as the box cover shows.

    NOT a box. The cover's blocks have no right angles: the sides taper, the
    top is sliced off at a steep diagonal with a bright triangular facet, and
    what reads as the amber is a thick band around a darker window where the
    figure shows through — the facets seen edge-on. A rectilinear crate was the
    first attempt here and it read as packaging.

    The hull is built from the figure's own bounding box, so a standing figure
    still yields a tall shard and a kneeling one a squat gem.
    """
    pad = band + 3
    w = src.width + pad * 2
    h = src.height + pad * 2
    fx, fy = pad, pad

    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    figure = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    figure.paste(src, (fx, fy))
    body = figure.getchannel("A").point(lambda v: 255 if v >= 128 else 0)

    L, R, T, B = 1, w - 2, 1, h - 2
    tw = max(1, int((R - L) * taper))          # how far the sides lean in
    cw = max(2, int((R - L) * cut))            # width of the sliced top corner
    ch_ = max(2, int((B - T) * cut * 0.55))    # its height

    # Outer hull: leans left at the top, right at the foot, top-left corner
    # sliced off. Deliberately asymmetric — a symmetrical gem reads as a box
    # with the corners filed.
    hull = [(L + tw, T + ch_), (L + tw + cw, T), (R, T + ch_ // 2),
            (R - tw // 2, B - ch_ // 3), (L + tw // 3, B)]
    inner = [(L + tw + band, T + ch_ + band),
             (L + tw + cw + band, T + band + 2),
             (R - band, T + ch_ // 2 + band),
             (R - tw // 2 - band, B - ch_ // 3 - band),
             (L + tw // 3 + band, B - band)]

    def mask_of(poly):
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        return m

    hull_m, inner_m = mask_of(hull), mask_of(inner)
    band_m = ImageChops.subtract(hull_m, inner_m)

    amber = vertical_gradient((w, h), tint_top, tint_bottom)
    window = vertical_gradient((w, h), shade(tint_top, 0.40), shade(tint_bottom, 0.40))
    facet = vertical_gradient((w, h), shade(tint_top, 0.95), shade(tint_bottom, 0.80))
    dark = vertical_gradient((w, h), shade(tint_top, 0.55), shade(tint_bottom, 0.45))

    # The window: darker, dithered, the figure suspended in it.
    canvas.paste(window, (0, 0),
                 ImageChops.multiply(ImageChops.subtract(inner_m, body),
                                     checker((w, h))))

    # The band is the crystal seen edge-on, and it is the solid part. Split it
    # at the hull's midline so one side catches the light and the other does
    # not, which is what gives the facets their read.
    lit = Image.new("L", (w, h), 0)
    lp = lit.load()
    for y in range(h):
        for x in range(w):
            lp[x, y] = 255 if (x / w) + (y / h) * 0.35 < 0.55 else 0
    canvas.paste(facet, (0, 0), ImageChops.multiply(band_m, lit))
    canvas.paste(dark, (0, 0),
                 ImageChops.multiply(band_m, ImageChops.invert(lit)))

    # The sliced corner is one bright triangle, the brightest thing on the
    # crystal — it is the first thing the eye finds on the cover.
    tri = mask_of([(L + tw, T + ch_), (L + tw + cw, T), (R, T + ch_ // 2)])
    tri = ImageChops.subtract(tri, inner_m)
    canvas.paste(vertical_gradient((w, h), shade(tint_top, rim_gain + 0.3),
                                   shade(tint_top, rim_gain)), (0, 0), tri)

    # The figure inside, tinted by what it is seen through.
    seen = Image.blend(figure.convert("RGB"), amber, opacity)
    canvas.paste(seen, (0, 0), body)

    # Hull and seam edges, one pixel.
    edges = Image.new("L", (w, h), 0)
    ed = ImageDraw.Draw(edges)
    ed.line(hull + [hull[0]], fill=255, width=1)
    ed.line(inner + [inner[0]], fill=255, width=1)
    canvas.paste(vertical_gradient((w, h), shade(tint_top, rim_gain),
                                   shade(tint_bottom, rim_gain)), (0, 0), edges)

    if spec > 0:
        hl = Image.new("L", (w, h), 0)
        hp = hl.load()
        for y in range(h):
            for x in range(w):
                d = abs(x / w - 0.3) * 2.4 + abs(y / h - 0.45) * 0.7
                if d < 0.10:
                    hp[x, y] = int(255 * (1 - d / 0.10) * spec)
        canvas.paste(Image.new("RGB", (w, h), (255, 246, 220)), (0, 0),
                     ImageChops.multiply(hl, ImageChops.multiply(inner_m,
                                                                 checker((w, h), 1))))

    alpha = canvas.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    canvas.putalpha(alpha)
    return canvas.crop(alpha.getbbox() or (0, 0, w, h))


def encase_block(src, margin, depth, opacity, tint_top, tint_bottom,
                 rim_gain, spec, bevel):
    """The figure sealed in a faceted amber block, as the box cover shows it.

    The block is sized to the figure's own bounding box, which is why no
    per-god shape parameter exists: a standing figure yields a tall prism, a
    kneeling one a cube, a narrow one a slab — the three blocks on the cover.

    Drawn in U8's fixed dimetric view: a front face, one side facet receding
    up and to the right, and a top facet. The top facet is the lit one on the
    cover, so it is the only solid fill; everything else is dithered.
    """
    # The block stands off the figure by `margin` on every side, so the front
    # face is the figure's box grown by 2*margin.
    L, T = 1, depth // 2 + 1
    R, B = L + src.width + margin * 2, T + src.height + margin * 2
    w, h = R + depth + 1, B + 1
    dy = depth // 2

    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    figure = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    figure.paste(src, (L + margin, T + margin))
    body = figure.getchannel("A").point(lambda v: 255 if v >= 128 else 0)

    # The FACES are dark. Resin at full tint reads as bright yellow mesh once
    # it is dithered, and the figure vanishes into it — the brightest thing in
    # the sprite has to be the god, not the block.
    amber = vertical_gradient((w, h), tint_top, tint_bottom)
    face = vertical_gradient((w, h), shade(tint_top, 0.46), shade(tint_bottom, 0.46))
    side = vertical_gradient((w, h), shade(tint_top, 0.32), shade(tint_bottom, 0.32))
    top = vertical_gradient((w, h), shade(tint_top, 0.78), shade(tint_bottom, 0.78))

    # Bevel slices the front face's top corner off, the way the cover's left
    # block is cut. Without it every block is a plain box.
    cut = int(src.width * bevel)
    front_poly = [(L, B), (L, T + cut), (L + cut, T), (R, T), (R, B)]
    side_poly = [(R, T), (R + depth, T - dy), (R + depth, B - dy), (R, B)]
    top_poly = [(L, T + cut), (L + cut, T), (R, T), (R + depth, T - dy),
                (L + depth, T - dy)] if cut else \
               [(L, T), (R, T), (R + depth, T - dy), (L + depth, T - dy)]

    def mask_of(poly):
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        return m

    front, sidem, topm = mask_of(front_poly), mask_of(side_poly), mask_of(top_poly)

    # Faces. Dithered where the floor should show through; the lit top facet
    # solid, because on the cover it is the one face that reads as bright.
    canvas.paste(side, (0, 0), ImageChops.multiply(sidem, checker((w, h))))
    canvas.paste(face, (0, 0),
                 ImageChops.multiply(ImageChops.subtract(front, body),
                                     checker((w, h))))
    canvas.paste(top, (0, 0), ImageChops.multiply(topm, checker((w, h), 1)))

    # The figure, seen through the front face: tinted toward amber and nothing
    # more. An amber scatter ON TOP of the body shreds a 24px-wide figure.
    seen = Image.blend(figure.convert("RGB"), amber, opacity)
    canvas.paste(seen, (0, 0), body)

    # Edges: every seam of the block, one pixel, lifted. These are what make
    # it read as a solid object rather than a wash of colour.
    edges = Image.new("L", (w, h), 0)
    ed = ImageDraw.Draw(edges)
    for poly in (front_poly, side_poly, top_poly):
        ed.line(poly + [poly[0]], fill=255, width=1)
    rim = vertical_gradient((w, h), shade(tint_top, rim_gain),
                            shade(tint_bottom, rim_gain))
    canvas.paste(rim, (0, 0), edges)

    # One specular streak down the lit side of the front face.
    if spec > 0:
        hl = Image.new("L", (w, h), 0)
        hp = hl.load()
        for y in range(h):
            for x in range(w):
                d = abs(x / w - 0.2) * 2.2 + abs(y / h - 0.3) * 0.8
                if d < 0.12:
                    hp[x, y] = int(255 * (1 - d / 0.12) * spec)
        canvas.paste(Image.new("RGB", (w, h), (255, 244, 214)), (0, 0),
                     ImageChops.multiply(hl, ImageChops.multiply(front, checker((w, h), 1))))

    alpha = canvas.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    canvas.putalpha(alpha)
    return canvas.crop(alpha.getbbox() or (0, 0, w, h))


def encase(src, shell_px, opacity, tint_top, tint_bottom, rim_gain, spec, solid):
    """Statue seen through an amber shell. src is already at game scale."""
    pad = shell_px + 2
    w, h = src.width + pad * 2, src.height + pad
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    base.paste(src, (pad, 0))

    body = base.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    shell = grow(body, shell_px)
    margin = ImageChops.subtract(shell, body)

    amber = vertical_gradient((w, h), tint_top, tint_bottom)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    # The margin is dithered, not solid: half its pixels stay transparent, so
    # the sanctum floor shows through and the shell reads as glass. An opaque
    # margin reads as a yellow outline stuck on the sprite.
    if solid:
        out.paste(amber, (0, 0), margin)
    else:
        out.paste(amber, (0, 0), ImageChops.multiply(margin, checker((w, h))))

    # The statue sits inside the resin, so it is seen THROUGH the tint.
    seen = Image.blend(base.convert("RGB"), amber, opacity)
    out.paste(seen, (0, 0), body)

    # One thin lit edge, top-left only. An even band all the way round was the
    # first version of this and read as a sticker outline.
    ring = ImageChops.subtract(shell, shrink(shell, 1))
    lit = Image.new("L", (w, h), 0)
    lp = lit.load()
    for y in range(h):
        for x in range(w):
            lp[x, y] = max(0, min(255, int(255 * (1.05 - (x / w) - (y / h) * 0.5))))
    rim = vertical_gradient(
        (w, h),
        tuple(min(255, round(c * rim_gain)) for c in tint_top),
        tuple(min(255, round(c * rim_gain)) for c in tint_bottom))
    out.paste(rim, (0, 0), ImageChops.multiply(ring, lit))

    # Specular: a short streak down the upper left, the light direction the
    # statue art was generated with.
    if spec > 0:
        hl = Image.new("L", (w, h), 0)
        hp = hl.load()
        for y in range(h):
            for x in range(w):
                d = abs(x / w - 0.24) * 1.8 + abs(y / h - 0.28)
                if d < 0.12:
                    hp[x, y] = int(255 * (1 - d / 0.12) * spec)
        hl = ImageChops.multiply(hl, ImageChops.multiply(shell, checker((w, h), 1)))
        out.paste(Image.new("RGB", (w, h), (255, 244, 214)), (0, 0), hl)

    alpha = out.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    out.putalpha(alpha)
    return out.crop(alpha.getbbox() or (0, 0, w, h))


def main():
    ap = argparse.ArgumentParser(
        description="Seal a statue PNG in an amber resin shell (Lost Vale).")
    ap.add_argument("images", metavar="IMAGE", nargs="+")
    ap.add_argument("--out", required=True, metavar="DIR")
    ap.add_argument("--height", type=int, default=110, metavar="PX",
                    help="game-scale sprite height to build at (default 110). "
                         "Pass png2shape the SAME height.")
    ap.add_argument("--mode", choices=("gem", "block", "contour"), default="gem",
                    help="gem: a rough-cut amber crystal, as the box cover "
                         "shows (default). block: a rectilinear box — reads as "
                         "packaging, kept only for comparison. contour: a "
                         "shell hugging the silhouette.")
    ap.add_argument("--band", type=int, default=5, metavar="PX",
                    help="gem mode: thickness of the amber seen edge-on around "
                         "the window (default 5)")
    ap.add_argument("--cut", type=float, default=0.30, metavar="FRAC",
                    help="gem mode: how much of the top is sliced off for the "
                         "bright facet (default 0.30)")
    ap.add_argument("--taper", type=float, default=0.12, metavar="FRAC",
                    help="gem mode: how far the sides lean in; 0 gives "
                         "vertical sides and a boxier crystal (default 0.12)")
    ap.add_argument("--margin", type=int, default=4, metavar="PX",
                    help="block mode: amber between the figure and the front "
                         "face, in game pixels (default 4)")
    ap.add_argument("--depth", type=int, default=6, metavar="PX",
                    help="block mode: how far the side facet recedes "
                         "(default 6)")
    ap.add_argument("--bevel", type=float, default=0.0, metavar="FRAC",
                    help="block mode: slice this fraction of the width off the "
                         "top-left corner, as on the cover's left block "
                         "(default 0, try 0.35)")
    ap.add_argument("--shell", type=int, default=3, metavar="PX",
                    help="how far the resin stands off the silhouette, in game "
                         "pixels (default 3; every px costs sanctum clearance)")
    ap.add_argument("--opacity", type=float, default=0.30,
                    help="how much amber the statue is seen through, 0-1 "
                         "(default 0.30; higher reads as carved amber rather "
                         "than stone under resin)")
    ap.add_argument("--tint", default="d9a03c", metavar="RRGGBB")
    ap.add_argument("--tint-bottom", default="8a5a16", metavar="RRGGBB")
    ap.add_argument("--rim", type=float, default=1.2, metavar="GAIN",
                    help="brightness of the lit edge (default 1.2)")
    ap.add_argument("--spec", type=float, default=0.5,
                    help="strength of the upper-left highlight, 0-1 (0 to omit)")
    ap.add_argument("--solid", action="store_true",
                    help="fill the margin solid instead of dithering it — "
                         "reads as amber-cast rather than encased")
    ap.add_argument("--key", default="ff00ff", metavar="RRGGBB")
    ap.add_argument("--key-tolerance", type=int, default=60)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    key = parse_hex(args.key)

    for path in args.images:
        src = to_game_scale(Image.open(path), args.height, key, args.key_tolerance)
        if args.mode == "gem":
            out = encase_gem(src, args.band, args.cut, args.taper, args.opacity,
                             parse_hex(args.tint), parse_hex(args.tint_bottom),
                             args.rim, args.spec)
        elif args.mode == "block":
            out = encase_block(src, args.margin, args.depth, args.opacity,
                               parse_hex(args.tint), parse_hex(args.tint_bottom),
                               args.rim, args.spec, args.bevel)
        else:
            out = encase(src, args.shell, args.opacity, parse_hex(args.tint),
                         parse_hex(args.tint_bottom), args.rim, args.spec,
                         args.solid)

        name = os.path.basename(path)
        for suffix in ("_raw.png", ".png"):
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
        dest = os.path.join(args.out, f"{name}_resin.png")
        out.save(dest)
        detail = {"gem": f"+ {args.band}px band, {args.cut} cut",
                  "block": f"+ {args.margin}px margin, {args.depth}px depth",
                  "contour": f"+ {args.shell}px shell"}[args.mode]
        print(f"  {dest}  {out.width}x{out.height}  "
              f"(figure {src.width}x{src.height} {detail})")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
png2shape.py — PNG in, injected U8 shape out, in one command.

WHY THIS EXISTS
The art pipeline was proven end to end on 2026-07-19 (see
docs/research/2026-07-19-ai-art-generation.md Part 3) but every stage after
"generate the image" was a throwaway scratchpad script. Three assets were
quantized, encoded and validated, and then nothing could be done with them:
nothing in the repo would put a PNG into U8SHAPES.FLX. This is that missing
driver, and it is deliberately the ONLY new code in the chain — quantization
aside, every step below calls a primitive that the wood-plank shapes 856-858
already proved against the real engine:

    lv_wood_wall.encode_frame        one frame → engine-exact RLE blob
    lv_wood_wall.encode_shape_blobs  frames    → shape blob
    lv_wood_wall.validate_shape      the SIGBUS guard (a port of ScummVM's
                                     own reader; a shape that fails this
                                     crashes the engine mid-paint)
    lv_wood_wall.inject_shape        shape blob → a free U8SHAPES.FLX slot
    patch_typeflag.copy_entry        donor's 3D bounding box → the new slot

WHAT IT DOES, IN ORDER
  1. Chroma-key the source PNG (default flat magenta, the convention the
     generators are prompted with), trim to the alpha bounding box, resize to
     game scale, then re-key: Lanczos resampling bleeds the key colour into
     the edge pixels, so keying once is not enough.
  2. Quantize every opaque pixel to its nearest U8PAL.PAL entry over indices
     0..254 by Euclidean RGB distance. Index 255 is the shape format's
     transparency key and must never be emitted as a colour; transparent
     pixels become 0xFF.
  3. Anchor the frame. U8 pastes a frame with (xoff, yoff) subtracted, so the
     anchor is the pixel that lands on the item's world position. Props want
     bottom-centre (xoff=w/2, yoff=h); terrain wants whatever its donor uses,
     because a ground tile's anchor is what makes it tessellate.
  4. Encode, validate, and refuse to write if validation fails.
  5. Inject into an EMPTY U8SHAPES.FLX slot (859+ by default; the wood shapes
     hold 856-858 and 855 is unallocated — see lv_wood_wall.py).
  6. Copy the donor's TYPEFLAG.DAT entry to the new slot. This step is not
     optional cosmetics: every one of the 2048 stock TYPEFLAG entries is
     populated, and the 1189 unused ones all carry SI_SOLID | SI_OCCL with a
     (1,1,0) footpad, so an unpatched new shape is a solid, view-blocking
     zero-height box rather than an unconfigured one. The donor's 3D footpad
     is then checked against the art's actual pixel size, and can be
     overridden with --footpad when no base-game shape has both the right
     behaviour and the right volume (see suggest_footpad).

INDEXED SOURCES (--indexed)
  Art cut pixel-exact from a 1994 screenshot (shared/data/lv-1994-art/, P-mode
  PNGs on U8PAL, index 255 transparent) is already a frame: the palette
  indices ARE the art. Steps 1-2 above would damage it four ways — the magenta
  key deletes purple/pink pixels, the trim moves the hotspot, any rescale
  resamples, and the RGB round trip maps the higher index of U8PAL's seven
  duplicate-RGB pairs (2/144, 9/28, 10/51, 11/15, 13/140, 46/191, 47/239) to
  the lower one. --indexed bypasses all of it: the PNG's indices go into the
  frame verbatim, 255 stays the transparency key, the canvas keeps its size,
  and the anchor is given (--anchor explicit / donor). It refuses a PNG that
  is not P-mode or whose palette is not U8PAL at every index it uses, since
  verbatim indices on a foreign palette would recolour silently. One limit
  is the format's, not the tool's: U8PAL 255 is also a real teal
  (24,125,125), and no frame can carry it.

USAGE
    tools/png2shape.py IMAGE.png --donor 443
    tools/png2shape.py IMAGE.png --donor 443 --shape-id 859 --height 110
    tools/png2shape.py enc.png freed.png --donor 443    # 2 frames, one shape
    tools/png2shape.py tile.png --donor 301 --anchor donor   # terrain
    tools/png2shape.py IMAGE.png --donor 443 --footpad 4,4,10
    tools/png2shape.py IMAGE.png --donor 443 --dry-run --preview /tmp/p.png
    tools/png2shape.py f0.png f1.png --donor 163 --indexed \
        --anchor explicit --xoff 31 --yoff 32       # 1994 art, verbatim

The FLX and TYPEFLAG.DAT it patches are the BUILT artifacts under
shared/build/, not the read-only game install. Note that they are rebuilt
from scratch by tools/build_artifacts.sh, which does not know about this
tool: an injection made here is lost on the next artifact rebuild until the
asset is given a builder of its own. Deliberate, not an oversight — wiring a
one-off injection into the build changes the canonical artifact hashes.

EXIT CODES
    0  injected (or dry run completed) and validated
    1  refused: bad input, occupied slot, failed validation, no free slot
    2  usage error
"""

import argparse
import os
import struct
import sys

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_SRC = os.path.join(REPO_DIR, 'agents', 'map-populator', 'src')
sys.path.insert(0, MAP_SRC)

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("ERROR: Pillow required. Install with: pip3 install Pillow",
          file=sys.stderr)
    sys.exit(1)

from lv_wood_wall import (encode_frame, encode_shape_blobs, validate_shape,
                          inject_shape)
from patch_typeflag import patch_entry_in_file, FILLER_ENTRY
from parse_typeflag import ShapeInfo
from shape_viewer import (load_palette, read_flx_entry, parse_shape_frames,
                          frame_to_image, PALETTE_FILE)

BUILD_DIR = os.path.join(REPO_DIR, 'shared', 'build')
DEFAULT_FLX = os.path.join(BUILD_DIR, 'U8SHAPES.FLX')
DEFAULT_TYPEFLAG = os.path.join(BUILD_DIR, 'TYPEFLAG.DAT')

# Slots 0-854 are base game, 855 is unallocated (adversarial-review L14) and
# 856-858 are the wood-plank shapes. New art starts here, per improvement
# plan section 6.1.
FIRST_LV_ART_SLOT = 859

# The shape format's transparency key. Also the reason quantization is capped
# at 254: emitting index 255 as a colour would punch a hole in the sprite.
KEYCOLOR = 0xFF

DEFAULT_KEY_RGB = (255, 0, 255)   # flat magenta, what the generators are told
DEFAULT_KEY_TOLERANCE = 60        # generous: catches anti-aliased fringing


class Refused(Exception):
    """A condition the operator has to resolve — reported, never worked around."""


# ---------------------------------------------------------------------------
# 1. Key, trim, scale
# ---------------------------------------------------------------------------

def key_out(img, key_rgb, tolerance):
    """Return an RGBA copy with pixels near key_rgb made fully transparent.

    Squared-distance threshold rather than an exact match: generators emit
    anti-aliased edges against the key colour, and a strict match leaves a
    magenta halo that then quantizes to whatever palette entry is closest to
    magenta — a bright pink outline around the sprite.
    """
    img = img.convert('RGBA')
    px = img.load()
    kr, kg, kb = key_rgb
    limit = tolerance * tolerance
    keyed = 0
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if (r - kr) ** 2 + (g - kg) ** 2 + (b - kb) ** 2 <= limit:
                px[x, y] = (0, 0, 0, 0)
                keyed += 1
    return img, keyed


def despill_edge(img, key_rgb, margin, passes=2):
    """Strip key-coloured bleed off the silhouette edge, AT GAME SCALE.

    `key_out` runs on the source PNG, where the generator's anti-aliased edge
    is one or two pixels wide. The Lanczos downscale that follows is ~9x, so
    whatever survived the tolerance gets averaged across the new edge pixel
    and comes out as a solid one-pixel halo — which then quantizes to the
    nearest palette entry to the key. On a magenta key that is a purple
    outline, invisible on a dark preview plate and unmistakable over a lit
    floor (found in-engine 2026-09-13, on the freed gods).

    Raising the tolerance does not fix it: at a distance that catches the
    blend it also catches the figure. So this discriminates by HUE instead.
    A pixel is bleed when every channel the key is bright in exceeds every
    channel it is dark in, by `margin` — for magenta (255,0,255) that is
    `r > g + margin and b > g + margin`, which bronze skin never satisfies
    because its blue is its lowest channel.

    Two thresholds. Above `2 * margin` the reading is unambiguous and the
    pixel goes regardless of where it sits — that is what clears an INTERIOR
    seam, like the one-pixel gap between a figure's legs, which fills solid
    at game scale and so has no transparent neighbour to erode from. Between
    `margin` and `2 * margin` the pixel must TOUCH transparency, and only
    `passes` rings of them are taken; without that limit the weak rule alone
    would eat ~3% of a bronze figure's interior, wherever a cool shadow sits
    above the margin. Checked by flagging both sets on the game-scale sprite
    (2026-09-13): every pixel either rule marks lies on the silhouette or in
    a seam, none inside the body.
    """
    hi = [i for i in range(3) if key_rgb[i] >= 128]
    lo = [i for i in range(3) if key_rgb[i] < 128]
    if not hi or not lo:
        return img, 0          # a key with no contrast has no spill signature
    img = img.convert('RGBA')
    w, h = img.size
    px = img.load()
    def spill(c):
        return min(c[i] for i in hi) - max(c[i] for i in lo)

    removed = 0
    # Unambiguous spill first, anywhere in the frame. Doing this before the
    # edge passes also SEEDS them: a seam cleared here becomes transparency
    # the erosion below can work outward from.
    strong = [(x, y) for y in range(h) for x in range(w)
              if px[x, y][3] and spill(px[x, y]) > 2 * margin]
    for x, y in strong:
        px[x, y] = (0, 0, 0, 0)
    removed += len(strong)

    for _ in range(passes):
        doomed = []
        for y in range(h):
            for x in range(w):
                if px[x, y][3] == 0:
                    continue
                if spill(px[x, y]) <= margin:
                    continue
                if any(x + dx < 0 or y + dy < 0 or x + dx >= w or y + dy >= h
                       or px[x + dx, y + dy][3] == 0
                       for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    doomed.append((x, y))
        if not doomed:
            break
        for x, y in doomed:
            px[x, y] = (0, 0, 0, 0)
        removed += len(doomed)
    return img, removed


def trim_to_alpha(img):
    """Crop to the opaque bounding box. Anchoring is defined relative to the
    sprite, so leftover empty margin would silently shift the anchor."""
    bbox = img.getbbox()          # alpha-aware for RGBA
    if bbox is None:
        raise Refused("image is fully transparent after keying — wrong key "
                      "colour, or too large a --key-tolerance")
    return img.crop(bbox)


def scale_to(img, target_h=None, target_w=None):
    """Resize to a game-scale size, preserving aspect ratio."""
    if target_h is None and target_w is None:
        return img
    w, h = img.size
    if target_h is not None and target_w is not None:
        new_w, new_h = target_w, target_h
    elif target_h is not None:
        new_h = target_h
        new_w = max(1, round(w * target_h / h))
    else:
        new_w = target_w
        new_h = max(1, round(h * target_w / w))
    return img.resize((new_w, new_h), Image.LANCZOS)


def rekey_alpha(img, alpha_threshold):
    """Force alpha to 0 or 255. The shape format has no partial transparency:
    a pixel is a palette index or it is the key colour. Doing this AFTER the
    resize is what stops Lanczos' soft edges from becoming a fringe of
    half-keyed pixels that quantize to arbitrary colours."""
    img = img.convert('RGBA')
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= alpha_threshold else (0, 0, 0, 0)
    return img


# ---------------------------------------------------------------------------
# 2. Quantize against U8PAL.PAL
# ---------------------------------------------------------------------------

def quantize(img, palette):
    """RGBA image → (pixel index list, set of indices used).

    Brute-force nearest neighbour in RGB over indices 0..254. PIL's own
    quantize() is not usable here: it ignores alpha and will happily pick
    index 255, which the engine reads as transparent.
    """
    px = img.load()
    candidates = list(enumerate(palette[:KEYCOLOR]))
    cache = {}
    pixels = []
    used = set()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a == 0:
                pixels.append(KEYCOLOR)
                continue
            rgb = (r, g, b)
            idx = cache.get(rgb)
            if idx is None:
                best, best_d = 0, None
                for i, (pr, pg, pb) in candidates:
                    d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
                    if best_d is None or d < best_d:
                        best, best_d = i, d
                        if d == 0:
                            break
                idx = cache[rgb] = best
            pixels.append(idx)
            used.add(idx)
    return pixels, used


def indexed_pixels(path, palette):
    """A P-mode PNG on U8PAL → (pixel index list, width, height, set of
    indices used), its indices verbatim: --indexed's whole job.

    Index 255 is the transparency key in both the 1994-art PNGs and the
    shape format, so it passes through as-is. Every other index used must
    carry exactly U8PAL's RGB in the PNG's own palette: a verbatim copy of
    indices drawn on any other palette would recolour the art silently,
    which is the one failure this mode exists to rule out.
    """
    img = Image.open(path)
    if img.mode != 'P':
        raise Refused(f"--indexed: {path} is a {img.mode} image; indexed "
                      f"import needs a P-mode PNG on U8PAL")
    w, h = img.size
    pixels = list(img.getdata())
    used = set(pixels) - {KEYCOLOR}
    if not used:
        raise Refused(f"--indexed: {path} is fully transparent (index 255)")
    pal = img.getpalette() or []
    foreign = sorted(i for i in used
                     if tuple(pal[3 * i:3 * i + 3]) != tuple(palette[i]))
    if foreign:
        i = foreign[0]
        raise Refused(
            f"--indexed: {path} palette is not U8PAL at {len(foreign)} used "
            f"index(es), e.g. {i}: {tuple(pal[3 * i:3 * i + 3])} vs U8PAL "
            f"{tuple(palette[i])}")
    return pixels, w, h, used



# ---------------------------------------------------------------------------
# 3. Anchor
# ---------------------------------------------------------------------------

def donor_offsets(flx_bytes, donor_id, frame_index):
    """(xoff, yoff) of a donor shape's frame, for terrain that must line up
    with the tiles around it."""
    data = read_flx_entry(flx_bytes, donor_id)
    if data is None:
        raise Refused(f"--anchor donor: shape {donor_id} has no data in the FLX")
    frames = parse_shape_frames(data)
    # Frame n of the new shape takes frame n of the donor where it exists;
    # a donor with fewer frames falls back to frame 0, which is reported by
    # the caller rather than assumed.
    usable = frame_index if frame_index < len(frames) else 0
    frame = frames[usable] if frames else None
    if frame is None:
        raise Refused(f"--anchor donor: shape {donor_id} frame {usable} "
                      f"did not parse")
    return frame['xoff'], frame['yoff'], frame['width'], frame['height'], usable


# ---------------------------------------------------------------------------
# 4. Footpad fit
# ---------------------------------------------------------------------------

def suggest_footpad(w, h):
    """The TYPEFLAG footpad that would project to a w×h sprite.

    Not a heuristic — it inverts the engine's own two constants. A footpad
    unit is (32, 32, 8) world units (map_walkability.py:143, which is how the
    walkability model reads the same file), and the isometric projection is
    sx = (x - y) / 4, sy = (x + y) / 8 - z (iso_render.py). So a footpad
    (fx, fy, fz) occupies 8*(fx+fy) pixels across and 8*fz + 4*(fx+fy)
    pixels tall on screen. Solving that for the art's pixel size gives the
    box that actually contains the sprite.

    Assumes a square-ish base, i.e. a prop rather than a wall.
    """
    span = max(2, min(30, round(w / 8)))          # fx + fy
    fx = max(1, min(15, span // 2))
    fy = max(1, min(15, span - fx))
    fz = max(0, min(15, round((h - 4 * (fx + fy)) / 8)))
    return fx, fy, fz


def footpad_screen_size(fx, fy, fz):
    """Inverse of suggest_footpad: the on-screen box a footpad covers."""
    return 8 * (fx + fy), 8 * fz + 4 * (fx + fy)


# ---------------------------------------------------------------------------
# 5. Slot allocation
# ---------------------------------------------------------------------------

def flx_entry(flx_bytes, index):
    off, size = struct.unpack_from('<II', flx_bytes, 0x80 + index * 8)
    return off, size


def flx_entry_count(flx_bytes):
    return struct.unpack_from('<I', flx_bytes, 0x54)[0]


def first_free_slot(flx_bytes, start):
    count = flx_entry_count(flx_bytes)
    for i in range(start, count):
        off, size = flx_entry(flx_bytes, i)
        if off == 0 and size == 0:
            return i
    raise Refused(f"no empty shape slot at or after {start} (FLX holds "
                  f"{count} entries)")


# ---------------------------------------------------------------------------
# 6. Preview
# ---------------------------------------------------------------------------

def render_preview(flx_bytes, shape_id, palette, out_path, scale=3):
    """Contact sheet of the shape AS READ BACK from the FLX, with the anchor
    marked. Reading it back rather than reusing the in-memory pixels is the
    point: it exercises the decoder against what actually got written."""
    data = read_flx_entry(flx_bytes, shape_id)
    if data is None:
        raise Refused(f"preview: shape {shape_id} is not in the FLX")
    frames = [f for f in parse_shape_frames(data) if f is not None]
    if not frames:
        raise Refused(f"preview: shape {shape_id} has no parseable frames")

    imgs = [frame_to_image(f, palette, scale=scale, bg_color=(24, 24, 32))
            for f in frames]
    pad, label_h = 8, 14
    # ASCII only in drawn text: PIL's built-in bitmap font has no glyph for
    # an em dash and draws a tofu box instead.
    title = (f"shape {shape_id}: {len(frames)} frame(s), "
             f"read back from the FLX")
    # Widen the sheet if the title is longer than the frames, so the caption
    # is never clipped — a preview whose label is cut off is a preview that
    # cannot be checked against.
    sheet_w = max(sum(i.width for i in imgs) + pad * (len(imgs) + 1),
                  len(title) * 6 + pad * 2)
    sheet_h = max(i.height for i in imgs) + pad * 3 + label_h * 2
    sheet = Image.new('RGB', (sheet_w, sheet_h), (16, 16, 22))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 2), title, fill=(230, 184, 0))

    x = pad
    for f, im in zip(frames, imgs):
        top = pad + label_h
        sheet.paste(im, (x, top))
        # Crosshair on the anchor: the pixel the engine puts on the item's
        # world position. Eyeballing this is how an anchor mistake gets
        # caught before the sprite floats or sinks in-game.
        ax, ay = x + f['xoff'] * scale, top + f['yoff'] * scale
        draw.line([(ax - 5, ay), (ax + 5, ay)], fill=(255, 64, 64))
        draw.line([(ax, ay - 5), (ax, ay + 5)], fill=(255, 64, 64))
        draw.text((x, top + im.height + 2),
                  f"{f['width']}x{f['height']} @({f['xoff']},{f['yoff']})",
                  fill=(150, 150, 170))
        x += im.width + pad

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    sheet.save(out_path)
    return out_path, sheet.size


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def build_frame(path, args, palette, flx_bytes, frame_index):
    """One PNG → (encoded frame blob, report dict). With args.indexed the
    PNG's palette indices go in verbatim (indexed_pixels); otherwise it is
    keyed, trimmed, scaled and quantized."""
    keyed = despilled = 0
    if getattr(args, 'indexed', False):
        pixels, w, h, used = indexed_pixels(path, palette)
        original = (w, h)
    else:
        src = Image.open(path)
        original = src.size

        if args.no_key:
            img = src.convert('RGBA')
        else:
            img, keyed = key_out(src, args.key_rgb, args.key_tolerance)

        if not args.no_trim:
            img = trim_to_alpha(img)
        img = scale_to(img, args.height, args.width)
        img = rekey_alpha(img, args.alpha_threshold)
        if getattr(args, 'key_despill', 0) and not args.no_key:
            img, despilled = despill_edge(img, args.key_rgb, args.key_despill)
        # Trim again after the resize: re-keying can empty edge rows that
        # only survived the first trim as partly transparent resample bleed.
        if not args.no_trim:
            img = trim_to_alpha(img)

        w, h = img.size
        pixels, used = quantize(img, palette)

    if args.anchor == 'donor':
        xoff, yoff, dw, dh, used_frame = donor_offsets(flx_bytes, args.donor,
                                                       frame_index)
        anchor_note = (f"donor shape {args.donor} frame {used_frame} "
                       f"({dw}x{dh} @ {xoff},{yoff})")
        if (dw, dh) != (w, h):
            anchor_note += "  [WARNING: donor frame is a different size]"
    elif args.anchor == 'explicit':
        xoff, yoff = args.xoff, args.yoff
        anchor_note = "explicit --xoff/--yoff"
    else:
        xoff, yoff = w // 2, h
        anchor_note = "bottom-centre (xoff=w/2, yoff=h)"

    blob = encode_frame(pixels, w, h, xoff, yoff)
    return blob, {
        'path': path, 'original': original, 'size': (w, h),
        'keyed': keyed, 'despilled': despilled,
        'colors': len(used), 'anchor': (xoff, yoff),
        'anchor_note': anchor_note, 'bytes': len(blob),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog='png2shape.py',
        description='Quantize a PNG to U8PAL, encode it as a U8 shape, and '
                    'inject it into shared/build/U8SHAPES.FLX + TYPEFLAG.DAT.',
        epilog='One PNG per frame; multiple PNGs become one multi-frame shape.')
    ap.add_argument('images', nargs='+', metavar='IMAGE',
                    help='source PNG(s), one per frame')
    ap.add_argument('--donor', type=int, required=True, metavar='ID',
                    help='base-game shape whose TYPEFLAG entry (flags, '
                         'footpad, weight) the new shape inherits — pick one '
                         'whose footpad matches the new art')
    ap.add_argument('--shape-id', type=int, metavar='ID',
                    help=f'target FLX slot (default: first empty slot at or '
                         f'after {FIRST_LV_ART_SLOT})')
    ap.add_argument('--height', type=int, metavar='PX',
                    help='resize to this game-scale height (aspect preserved)')
    ap.add_argument('--width', type=int, metavar='PX',
                    help='resize to this game-scale width (aspect preserved '
                         'unless --height is also given)')
    ap.add_argument('--anchor', choices=('bottom-center', 'donor', 'explicit'),
                    default='bottom-center',
                    help='bottom-center: xoff=w/2, yoff=h (props, default). '
                         'donor: copy --donor\'s frame offsets (terrain). '
                         'explicit: use --xoff/--yoff.')
    ap.add_argument('--xoff', type=int, default=0, help='with --anchor explicit')
    ap.add_argument('--yoff', type=int, default=0, help='with --anchor explicit')
    ap.add_argument('--key', default='ff00ff', metavar='RRGGBB',
                    help='chroma key colour (default ff00ff, flat magenta)')
    ap.add_argument('--key-despill', type=int, default=0, metavar='MARGIN',
                    help="strip key-coloured bleed off the silhouette edge "
                         "AFTER the downscale, by hue rather than distance. "
                         "16 is a good starting margin; 0 (default) is off. "
                         "Use it when the sprite reads clean on a dark plate "
                         "and carries a coloured outline over a lit floor.")
    ap.add_argument('--key-tolerance', type=int, default=DEFAULT_KEY_TOLERANCE,
                    metavar='N', help='RGB distance treated as key colour '
                                      f'(default {DEFAULT_KEY_TOLERANCE})')
    ap.add_argument('--no-key', action='store_true',
                    help='source already has an alpha channel; skip keying')
    ap.add_argument('--no-trim', action='store_true',
                    help='keep the source margins instead of cropping to the '
                         'opaque bounding box')
    ap.add_argument('--alpha-threshold', type=int, default=128, metavar='N',
                    help='alpha at or above N is opaque (default 128)')
    ap.add_argument('--indexed', action='store_true',
                    help='the PNG is P-mode on U8PAL (1994 screenshot art): '
                         'copy its palette indices verbatim, 255 = '
                         'transparent — no key, trim, scale or quantize. '
                         'Needs --anchor explicit or donor')
    ap.add_argument('--flx', default=DEFAULT_FLX,
                    help='U8SHAPES.FLX to patch (default: shared/build copy)')
    ap.add_argument('--out', help='write the patched FLX here instead of '
                                  'back over --flx')
    ap.add_argument('--typeflag', default=DEFAULT_TYPEFLAG,
                    help='TYPEFLAG.DAT to patch (default: shared/build copy)')
    ap.add_argument('--footpad', metavar='X,Y,Z',
                    help='override the donor\'s 3D footpad (0-15 each) while '
                         'keeping its flags, family and weight — for art with '
                         'no volume-matched donor in the base game')
    ap.add_argument('--no-typeflag', action='store_true',
                    help='skip the TYPEFLAG patch — leaves the shape with the '
                         'stock filler box (SI_SOLID|SI_OCCL, footpad 1,1,0)')
    ap.add_argument('--force', action='store_true',
                    help='allow overwriting a slot that already holds a shape')
    ap.add_argument('--preview', metavar='PATH',
                    help='render a contact sheet of the injected shape here '
                         '(to re-render one later, use shape_render.py)')
    ap.add_argument('--dry-run', action='store_true',
                    help='do everything except write the artifacts')
    args = ap.parse_args(argv)

    try:
        args.key_rgb = tuple(int(args.key.lstrip('#')[i:i + 2], 16)
                             for i in (0, 2, 4))
    except (ValueError, IndexError):
        ap.error(f"--key must be RRGGBB hex, got {args.key!r}")
    if args.anchor == 'explicit' and args.xoff == 0 and args.yoff == 0:
        ap.error("--anchor explicit needs --xoff/--yoff")
    if args.indexed:
        if args.height or args.width or args.key_despill:
            ap.error("--indexed copies the PNG's indices verbatim; "
                     "--height/--width/--key-despill would resample or "
                     "recolour it")
        if args.anchor == 'bottom-center':
            ap.error("--indexed needs --anchor explicit (the art's hotspot) "
                     "or --anchor donor; a cut sprite's canvas is not "
                     "bottom-centred")
    if args.footpad:
        try:
            args.footpad = tuple(int(v) for v in args.footpad.split(','))
            if len(args.footpad) != 3 or not all(0 <= v <= 15
                                                 for v in args.footpad):
                raise ValueError
        except ValueError:
            ap.error(f"--footpad wants three 0-15 values as X,Y,Z, got "
                     f"{args.footpad!r}")
    if args.footpad and args.no_typeflag:
        ap.error("--footpad has nothing to write with --no-typeflag")

    for p in args.images:
        if not os.path.exists(p):
            ap.error(f"no such image: {p}")
    if not os.path.exists(args.flx):
        ap.error(f"no such FLX: {args.flx}\n"
                 f"       Build the artifacts first: tools/build_artifacts.sh")
    if not args.no_typeflag and not os.path.exists(args.typeflag):
        ap.error(f"no such TYPEFLAG.DAT: {args.typeflag}\n"
                 f"       Build the artifacts first: tools/build_artifacts.sh")

    palette = load_palette(PALETTE_FILE)
    with open(args.flx, 'rb') as f:
        flx_bytes = f.read()

    print("=== png2shape ===")
    print(f"  FLX:       {args.flx}")
    print(f"  TYPEFLAG:  {args.typeflag if not args.no_typeflag else '(skipped)'}")
    print(f"  palette:   {PALETTE_FILE}")

    # --- Slot ------------------------------------------------------------
    if args.shape_id is None:
        shape_id = first_free_slot(flx_bytes, FIRST_LV_ART_SLOT)
        print(f"  slot:      {shape_id} (first free at or after "
              f"{FIRST_LV_ART_SLOT})")
    else:
        shape_id = args.shape_id
        off, size = flx_entry(flx_bytes, shape_id)
        state = 'EMPTY' if (off == 0 and size == 0) else f'OCCUPIED ({size} bytes)'
        print(f"  slot:      {shape_id} ({state})")

    # --- Donor -----------------------------------------------------------
    with open(args.typeflag, 'rb') as f:
        tf_bytes = f.read()
    donor_entry = tf_bytes[args.donor * 8: args.donor * 8 + 8]
    donor_info = ShapeInfo(args.donor, donor_entry)
    if donor_entry == FILLER_ENTRY:
        raise Refused(
            f"donor shape {args.donor} carries the stock filler TYPEFLAG "
            f"entry ({FILLER_ENTRY.hex()}), i.e. it is an unused slot with no "
            f"real bounding box. Pick a donor that exists in the base game.")
    print(f"  donor:     {donor_info}")

    # --- Frames ----------------------------------------------------------
    print("\n-- 1/4  key, scale, quantize, encode --")
    frame_blobs = []
    reports = []
    for i, path in enumerate(args.images):
        blob, rep = build_frame(path, args, palette, flx_bytes, i)
        frame_blobs.append(blob)
        reports.append(rep)
        print(f"  frame {i}: {os.path.basename(rep['path'])}  "
              f"{rep['original'][0]}x{rep['original'][1]} -> "
              f"{rep['size'][0]}x{rep['size'][1]}, "
              f"{rep['colors']} U8PAL colours, {rep['bytes']} bytes")
        print(f"           anchor {rep['anchor']} — {rep['anchor_note']}")

    shape_blob = encode_shape_blobs(frame_blobs)
    print(f"  shape blob: {len(frame_blobs)} frame(s), {len(shape_blob)} bytes")

    # --- Validate BEFORE writing anything --------------------------------
    print("\n-- 2/4  validate against the ScummVM shape reader --")
    errs = validate_shape(shape_blob)
    if errs:
        for e in errs:
            print(f"  FAIL {e}", file=sys.stderr)
        raise Refused("encoded shape would crash the engine — nothing written")
    print("  OK  (0 errors — safe to load)")

    # --- Footpad fit -----------------------------------------------------
    # The donor supplies a 3D box; if it does not contain the new sprite, the
    # engine depth-sorts and collides against the wrong volume — the Avatar
    # walks through the top of a monument, or stands in front of what should
    # occlude him. Check it rather than hope.
    nw = max(r['size'][0] for r in reports)
    nh = max(r['size'][1] for r in reports)
    want = suggest_footpad(nw, nh)
    have = (donor_info.footpad_x, donor_info.footpad_y, donor_info.footpad_z)
    hav_w, hav_h = footpad_screen_size(*have)
    print(f"\n-- footpad fit --")
    print(f"  art {nw}x{nh}px wants footpad {want}; donor {args.donor} has "
          f"{have} (covers {hav_w}x{hav_h}px)")
    if args.footpad:
        fit_w, fit_h = footpad_screen_size(*args.footpad)
        print(f"  --footpad {args.footpad} overrides it (covers "
              f"{fit_w}x{fit_h}px); donor flags/family/weight still apply")
    elif hav_h * 1.25 < nh or hav_w * 1.25 < nw:
        print(f"  NOTE: the donor box is smaller than the art. Depth sort and "
              f"collision will use the smaller box. Pass "
              f"--footpad {want[0]},{want[1]},{want[2]} to author the right "
              f"one, or pick a bulkier donor.")

    if args.dry_run:
        print("\n-- 3/4  inject --\n  SKIPPED (--dry-run)")
        print("-- 4/4  TYPEFLAG --\n  SKIPPED (--dry-run)")
        if args.preview:
            print("\n  preview needs the injected FLX; re-run without "
                  "--dry-run", file=sys.stderr)
        print("\nDry run OK — nothing written.")
        return 0

    # --- Inject ----------------------------------------------------------
    # Stage into a temp file and rename over the target only once the shape
    # has been read back and re-validated, so a bad write can never leave a
    # corrupt artifact where the build expects a good one.
    print("\n-- 3/4  inject --")
    dst = args.out or args.flx
    staged = dst + '.png2shape.tmp'
    try:
        inject_shape(shape_blob, shape_id, args.flx, staged, force=args.force)

        with open(staged, 'rb') as f:
            staged_bytes = f.read()
        reread = read_flx_entry(staged_bytes, shape_id)
        if reread is None:
            raise Refused(f"slot {shape_id} reads back empty after injection")
        if reread != shape_blob:
            raise Refused(f"slot {shape_id} reads back {len(reread)} bytes, "
                          f"not the {len(shape_blob)} written")
        errs = validate_shape(reread)
        if errs:
            raise Refused(f"shape read back from the FLX fails validation: "
                          f"{errs}")
        frames = [f for f in parse_shape_frames(reread) if f is not None]
        dims = ', '.join(f"{f['width']}x{f['height']}@({f['xoff']},{f['yoff']})"
                         for f in frames)
        print(f"  re-read OK: {len(frames)} frame(s) — {dims}")

        os.replace(staged, dst)
    finally:
        if os.path.exists(staged):
            os.remove(staged)
    print(f"  {dst} now {os.path.getsize(dst)} bytes")

    # --- TYPEFLAG --------------------------------------------------------
    print("\n-- 4/4  TYPEFLAG --")
    if args.no_typeflag:
        print(f"  SKIPPED (--no-typeflag): shape {shape_id} keeps the stock "
              f"filler box {FILLER_ENTRY.hex()} — SI_SOLID|SI_OCCL, "
              f"footpad (1,1,0)")
    else:
        old, new = patch_entry_in_file(args.typeflag, shape_id, args.donor,
                                       footpad=args.footpad)
        was = "stock filler" if old == FILLER_ENTRY else "PRE-EXISTING ENTRY"
        print(f"  slot {shape_id} ← donor {args.donor}: "
              f"{old.hex()} ({was}) -> {new.hex()}")
        print(f"  {ShapeInfo(shape_id, new)}")

    print(f"\nDone. Shape {shape_id} is in {dst}.")
    print(f"  Place it with a SHAPE_ constant in "
          f"agents/map-populator/src/lv_shapes.py, then a map builder.")
    print(f"  NOTE: tools/build_artifacts.sh rebuilds U8SHAPES.FLX from the "
          f"base game and will drop this shape.")

    # --- Preview ---------------------------------------------------------
    if args.preview:
        with open(dst, 'rb') as f:
            final_bytes = f.read()
        path, size = render_preview(final_bytes, shape_id, palette,
                                    args.preview)
        print(f"  Preview: {path} ({size[0]}x{size[1]})")

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Refused as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, OSError) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)

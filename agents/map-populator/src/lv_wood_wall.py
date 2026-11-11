#!/usr/bin/env python3
"""
lv_wood_wall.py — Build the wood-plank hut shapes the base game does not have,
and inject them into a patched copy of U8SHAPES.FLX.

Ultima 8 ships no wood-plank wall sprite, but the Lost Vale screenshots show
the clan village built from planks. Rather than draw new art, each wood shape
is a STRUCTURAL COPY of a real base-game stone shape — same per-frame
silhouette, same frame count, same offsets — with the stone pixels repainted
as vertical planks in U8 palette browns 164-174. Copying the silhouette is
what makes this safe: the frame layout is one the engine already parses, and
every frame index a prefab might reference still resolves to real pixels.

    856 ← 24   SE-facing wall panel
    857 ← 20   SW-facing wall panel
    858 ← 255  corner post

This module is also the home of the shape primitives these three proved —
encode_frame, encode_shape_blobs, validate_shape, inject_shape — which
tools/png2shape.py reuses to inject arbitrary PNG art. Change them with care:
validate_shape is a port of ScummVM's own reader, and a frame that fails it
SIGBUSes the engine mid-paint rather than merely failing to load.

Usage:
    python3 lv_wood_wall.py [--out PATH]  # default: shared/build/U8SHAPES.FLX
    python3 lv_wood_wall.py --preview     # inject to /tmp instead, then render
"""

import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image
from shape_viewer import load_palette, SHAPES_FLX, PALETTE_FILE

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    '..', '..', '..', 'shared')
BUILD_DIR = os.path.join(ROOT, 'build')
OUT_SHAPES = os.path.join(BUILD_DIR, 'U8SHAPES.FLX')

# Injected shape ids. 855 is deliberately absent (adversarial-review L14):
# it was reserved for a matching wood-plank FLOOR tile to replace shape 556,
# but build_map_10.py's WOOD_WALL_REMAP dropped the 556 entry on purpose —
# 556's placed items reference frames 27-29, and a 4-frame custom tile left
# them pointing at frames that do not exist. With its only consumer gone the
# tile was never generated, never injected and never TYPEFLAG-patched, so the
# id is now simply unallocated. Do not "restore" it without first building a
# floor tile that carries all 30 of shape 556's frames.
SE_WALL_ID     = 856  # 39×60 SE-facing wood-plank wall (replaces shape 24)
SW_WALL_ID     = 857  # 40×61 SW-facing wood-plank wall (replaces shape 20)
CORNER_POST_ID = 858  # 16×48 wooden corner post (replaces shape 255 frames 0-3)


# ---------------------------------------------------------------------------
# Wall sprite generator — replaces shapes 24 (SE) and 20 (SW)
# ---------------------------------------------------------------------------

def make_wall_pixels(template_shape_data, template_frame=0, plank_width=7, seed=42):
    """
    Replace the stone texture with wood planks, keeping the exact pixel
    silhouette of the template shape (shapes 24 / 20 are isometric parallelograms
    with transparent corners).  Returns (pixels, width, height, xoff, yoff).

    Uses U8 brown palette indices 164-174 (sampled from screen19 wood building).
    """
    import random
    from shape_viewer import parse_shape_frames
    rng = random.Random(seed)

    frames = parse_shape_frames(template_shape_data)
    f = frames[template_frame]
    w, h = f['width'], f['height']
    xoff, yoff = f['xoff'], f['yoff']
    template_px = f['pixels']

    GAP  = 174
    EDGE = 172
    BODY = [171, 170, 169, 168, 167, 166]
    LITE = [165, 164]

    pixels = []
    for y in range(h):
        for x in range(w):
            if template_px[y * w + x] == 0xFF:
                pixels.append(0xFF)
            else:
                col = x % plank_width
                if col == 0:
                    pixels.append(GAP)
                elif col == 1:
                    pixels.append(EDGE)
                elif col == plank_width - 1:
                    pixels.append(LITE[rng.randint(0, 1)])
                else:
                    pixels.append(BODY[rng.randint(0, len(BODY) - 1)])
    return pixels, w, h, xoff, yoff


# ---------------------------------------------------------------------------
# Encode as a U8 shape frame (uncompressed)
#
# Quantization lives in tools/png2shape.py, not here: this file's shapes are
# authored directly in palette indices, and the only quantizer that is any use
# for real art must be transparency-aware (alpha → index 0xFF) and must avoid
# emitting index 255 as a colour. PIL's quantize() is neither, so the old
# build_palette_image()/quantize_to_u8() pair here was both dead and a trap.
# ---------------------------------------------------------------------------

def encode_frame(pixels, width, height, xoff, yoff):
    """
    Build a U8 shape frame blob (uncompressed, compressed-flag=0).

    Frame layout (all little-endian):
      [0..7]   : 8 bytes of padding / unknown (zeroed)
      [8]      : compressed flag (0 = uncompressed)
      [9]      : padding byte
      [10..11] : width  (int16)
      [12..13] : height (int16)
      [14..15] : xoff   (int16)
      [16..17] : yoff   (int16)
      [18 .. 18+height*2-1] : line-offset table (uint16 per row, relative)
      [18+height*2 ..]      : RLE data (uncompressed runs)

    In uncompressed mode each run chunk is:
      skip (uint8) — transparent pixels to skip
      dlen_byte    — (pixel_count << 1) | 0  (is_rle=0)
      pixel bytes  — palette indices

    The line-offset table stores absolute offsets from the START of the
    line-offset table itself (i.e. raw offset from byte 18 of the frame),
    with each entry further adjusted by +((height - row) * 2) per the
    parser's formula:  raw = line_offsets[y] + (height - y) * 2

    Raises ValueError on input the format cannot express — see the width
    guard below. The wood shapes never approach these limits; arbitrary art
    coming in through tools/png2shape.py can, and a clamp or a truncation
    here would produce a shape that loads and renders WRONG rather than one
    that fails loudly.
    """
    # Both the skip count and the run length are single bytes, and each is
    # bounded by the row width, so width <= 255 is exactly the condition that
    # makes every run encodable. Above it, `min(skip, 255)` below would
    # silently shift a row and a >255 run would blow up inside bytes().
    if not 0 < width <= 255:
        raise ValueError(
            f"frame width {width} out of range: the U8 RLE skip and length "
            f"fields are single bytes, so a frame must be 1..255 px wide "
            f"(slice wider art into multiple shapes)")
    if not 0 < height <= 32767:
        raise ValueError(f"frame height {height} out of range (1..32767)")
    if len(pixels) != width * height:
        raise ValueError(f"pixel buffer is {len(pixels)}, expected "
                         f"{width * height} for {width}x{height}")

    # Build RLE data row by row
    rle_rows = []
    for y in range(height):
        row_px = pixels[y * width: y * width + width]
        chunks = b''
        x = 0
        while x < width:
            # Count transparent pixels
            skip = 0
            while x + skip < width and row_px[x + skip] == 0xFF:
                skip += 1
            x += skip
            if x >= width:
                if skip or not chunks:
                    chunks += bytes([min(skip, 255)])
                break
            # Count opaque run
            run = []
            while x + len(run) < width and row_px[x + len(run)] != 0xFF:
                run.append(row_px[x + len(run)])
            # Emit: skip + length_byte + pixel data.
            # CRITICAL: for UNCOMPRESSED frames (_compression=0) ScummVM's
            # ShapeFrame::load uses dlen RAW — it only does `dlen >>= 1` when
            # _compressed is set. So the length byte is the literal pixel count,
            # NOT (count<<1). Writing (count<<1) makes the engine read twice as
            # many pixel bytes as exist → buffer overrun → SIGBUS.
            dlen_byte = len(run)
            chunks += bytes([min(skip, 255), dlen_byte]) + bytes(run)
            x += len(run)
        rle_rows.append(chunks)

    # Build line-offset table.
    # Decoder: line_ptr = rle_start + (raw - (height - y) * 2)
    # We want line_ptr = rle_start + cur_offset_to_row_y
    # So: raw = cur_offset + (height - y) * 2
    table = b''
    rle_blob = b''
    cur = 0
    for y, row_data in enumerate(rle_rows):
        raw = cur + (height - y) * 2
        # The table entry is a uint16. Masking an overflow would point a row
        # at the wrong RLE bytes — a rendering corruption the engine cannot
        # detect — so refuse instead. Reachable only for a frame whose RLE
        # payload exceeds 64 KB, i.e. very large and mostly opaque.
        if raw > 0xFFFF:
            raise ValueError(
                f"row {y} line-offset {raw} exceeds the uint16 table entry; "
                f"frame RLE payload is too large ({cur} bytes so far)")
        table += struct.pack('<H', raw)
        rle_blob += row_data
        cur += len(row_data)

    # Assemble frame header — U8ShapeFormat _len_frameheader2 = 18 bytes:
    #   8 bytes frame_unknown
    #   2 bytes frame_compression (uint16!)  — 0 = uncompressed
    #   2 bytes frame_width  (sint16)
    #   2 bytes frame_height (sint16)
    #   2 bytes frame_xoff   (sint16)
    #   2 bytes frame_yoff   (sint16)
    header = (
        b'\x00' * 8 +
        struct.pack('<H', 0) +              # compression = 0 (2-byte field)
        struct.pack('<h', width) +
        struct.pack('<h', height) +
        struct.pack('<h', xoff) +
        struct.pack('<h', yoff)
    )
    return header + table + rle_blob


def _frame_table_entry(offset, size):
    """One U8 frame-table entry — _len_frameheader = 6 bytes:
        3 bytes frame_offset (uint24 LE)
        1 byte  frameheader_unk
        2 bytes frame_length (uint16)
    """
    return struct.pack('<I', offset)[:3] + b'\x00' + struct.pack('<H', size)


def encode_shape_blobs(frame_blobs):
    """Assemble a U8 shape from already-encoded frame blobs (which may differ
    in dimensions). Shape header _len_header = 6 bytes: 4 unk + 2 num_frames."""
    n = len(frame_blobs)
    table_end = 6 + n * 6
    frame_table = b''
    cur = table_end
    for blob in frame_blobs:
        frame_table += _frame_table_entry(cur, len(blob))
        cur += len(blob)
    header = b'\x00' * 4 + struct.pack('<H', n)
    return header + frame_table + b''.join(frame_blobs)


def encode_shape(frames_pixels, width, height, xoff, yoff):
    """Build a U8 shape blob for multiple frames sharing one geometry."""
    blobs = [encode_frame(px, width, height, xoff, yoff) for px in frames_pixels]
    return encode_shape_blobs(blobs)


def num_frames(shape_data):
    """num_frames field of a U8 shape blob (uint16 at offset 4)."""
    return struct.unpack_from('<H', shape_data, 4)[0]


# ---------------------------------------------------------------------------
# Validator — a faithful port of ScummVM's U8 shape reader + renderer.
# This is the round-trip check done against the REAL engine format, so a
# malformed frame is caught here instead of as a SIGBUS during paint.
# Mirrors ConvertShapeFrame::Read and ShapeFrame::load in scummvm-lv.
# ---------------------------------------------------------------------------

def validate_shape(shape_data):
    """Return a list of error strings; empty list means the shape is safe to
    load. Simulates the engine's exact pointer walk and flags any read that
    would run off the RLE buffer (the SIGBUS) or off the pixel surface."""
    errs = []
    try:
        n = struct.unpack_from('<H', shape_data, 4)[0]
    except struct.error:
        return ["shape header truncated"]

    LEN_HEADER, LEN_FRAMEHDR, LEN_FRAMEHDR2, LINE_OFF = 6, 6, 18, 2

    for f in range(n):
        ent = LEN_HEADER + LEN_FRAMEHDR * f
        if ent + 6 > len(shape_data):
            errs.append(f"frame {f}: table entry out of range")
            continue
        frame_off = struct.unpack_from('<I', shape_data, ent)[0] & 0xFFFFFF
        frame_len = struct.unpack_from('<H', shape_data, ent + 4)[0]

        if frame_off + LEN_FRAMEHDR2 > len(shape_data):
            errs.append(f"frame {f}: header beyond blob")
            continue
        comp = struct.unpack_from('<H', shape_data, frame_off + 8)[0]
        h    = struct.unpack_from('<h', shape_data, frame_off + 12)[0]
        w    = struct.unpack_from('<h', shape_data, frame_off + 10)[0]
        if comp not in (0, 1):
            errs.append(f"frame {f}: bad compression={comp}")
            continue

        # Line-offset table → offsets into rle_data (engine's fudge applied)
        line_offs = []
        for i in range(h):
            off_pos = frame_off + LEN_FRAMEHDR2 + i * LINE_OFF
            raw = struct.unpack_from('<H', shape_data, off_pos)[0]
            line_offs.append(raw - (h - i) * LINE_OFF)   # _line_offset_absolute=0

        bytes_rle = frame_len - (LEN_FRAMEHDR2 + h * LINE_OFF)
        if bytes_rle < 0:
            errs.append(f"frame {f}: negative rle length")
            continue
        rle_start = frame_off + LEN_FRAMEHDR2 + h * LINE_OFF
        rle = shape_data[rle_start: rle_start + bytes_rle]

        # Walk each row exactly like ShapeFrame::load
        for y in range(h):
            p = line_offs[y]
            if p < 0 or p > len(rle):
                errs.append(f"frame {f} row {y}: line_offset {p} out of [0,{len(rle)}]")
                break
            xpos = 0
            guard = 0
            while True:
                guard += 1
                if guard > w + 4:
                    errs.append(f"frame {f} row {y}: row did not terminate")
                    break
                if p >= len(rle):
                    errs.append(f"frame {f} row {y}: skip read overruns rle ({p}>={len(rle)})")
                    break
                xpos += rle[p]; p += 1                      # skip byte
                if xpos >= w:
                    break
                if p >= len(rle):
                    errs.append(f"frame {f} row {y}: dlen read overruns rle")
                    break
                dlen = rle[p]; p += 1                        # dlen byte
                typ = 0
                if comp:
                    typ = dlen & 1; dlen >>= 1
                if xpos + dlen > w:
                    errs.append(f"frame {f} row {y}: run overflows width "
                                f"(xpos={xpos} dlen={dlen} w={w})")
                    break
                if typ:
                    if p >= len(rle):
                        errs.append(f"frame {f} row {y}: compressed pixel overruns rle")
                        break
                    p += 1                                   # single repeated pixel
                else:
                    if p + dlen > len(rle):
                        errs.append(f"frame {f} row {y}: {dlen} pixels overrun rle "
                                    f"({p}+{dlen}>{len(rle)})")
                        break
                    p += dlen                                # dlen literal pixels
                xpos += dlen
                if xpos >= w:
                    break
            if errs and errs[-1].startswith(f"frame {f} row {y}"):
                break
    return errs


# ---------------------------------------------------------------------------
# Step 4 — Inject into U8SHAPES.FLX
# ---------------------------------------------------------------------------

def inject_shape(shape_blob, shape_id, src_path, dst_path, force=False):
    """
    Append shape_blob to a copy of src_path, updating slot shape_id's index.

    Refuses a slot that already holds data unless force=True (adversarial-
    review L15). Overwriting an occupied slot orphans the old blob's bytes
    (they stay in the file, unreferenced) and, far worse, silently replaces a
    base-game sprite that hundreds of placed map items may point at. That is
    a legitimate operation — it is how a base shape would be re-skinned — but
    it must be asked for, not warned about after the fact.
    """
    with open(src_path, 'rb') as f:
        flx = bytearray(f.read())

    entry_count = struct.unpack_from('<I', flx, 0x54)[0]
    if not 0 <= shape_id < entry_count:
        raise ValueError(f"shape id {shape_id} outside the FLX index "
                         f"(0..{entry_count - 1})")

    entry_off = 0x80 + shape_id * 8
    existing_offset = struct.unpack_from('<I', flx, entry_off)[0]
    existing_size   = struct.unpack_from('<I', flx, entry_off + 4)[0]
    if existing_offset != 0 or existing_size != 0:
        if not force:
            raise ValueError(
                f"slot {shape_id} is not empty (offset={existing_offset:#x} "
                f"size={existing_size}) — refusing to overwrite an existing "
                f"shape. Pass force=True (CLI: --force) if replacing it is "
                f"what you mean to do.")
        print(f"  FORCED overwrite of non-empty slot {shape_id} "
              f"(was offset={existing_offset:#x} size={existing_size}; "
              f"those bytes are now orphaned in the file)")

    # Append data and record new position
    new_offset = len(flx)
    flx.extend(shape_blob)

    # Update index entry
    struct.pack_into('<I', flx, entry_off,     new_offset)
    struct.pack_into('<I', flx, entry_off + 4, len(shape_blob))

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, 'wb') as f:
        f.write(flx)

    print(f"Injected shape {shape_id}: {len(shape_blob)} bytes at offset {new_offset:#010x}")
    print(f"Wrote {dst_path} ({len(flx)} bytes)")


# ---------------------------------------------------------------------------
# Step 5 — Preview via iso_render
# ---------------------------------------------------------------------------

def preview(shape_id, palette, shapes_flx=None, out=None, nframes=4):
    """Render the first nframes of shape_id through the isometric renderer,
    side by side, as a single PNG. This is the engine-side check: it reads the
    shape back out of the FLX rather than trusting the pixels we encoded."""
    from iso_render import IsoRenderer
    from u8_map import MapItem

    r = IsoRenderer(
        shapes_flx=shapes_flx or OUT_SHAPES,
        palette_file=PALETTE_FILE,
    )

    frames_imgs = []
    for frame_idx in range(nframes):
        items = [MapItem(x=0, y=0, z=0, shape=shape_id, frame=frame_idx)]
        img = r.render(items, scale=4)
        frames_imgs.append(img)

    total_w = sum(i.width for i in frames_imgs) + 10 * (len(frames_imgs) - 1)
    max_h = max(i.height for i in frames_imgs)
    sheet = Image.new('RGB', (total_w, max_h), (20, 20, 30))
    x = 0
    for img in frames_imgs:
        sheet.paste(img, (x, (max_h - img.height) // 2))
        x += img.width + 10

    out = out or f'/tmp/lv_shape_{shape_id}_preview.png'
    sheet.save(out)
    print(f"Preview: {out}  ({sheet.width}x{sheet.height})")
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=OUT_SHAPES)
    ap.add_argument('--preview', action='store_true',
                    help='inject into /tmp instead of the real artifact, then '
                         'render each shape to a PNG (leaves shared/build alone)')
    ap.add_argument('--src', default=SHAPES_FLX,
                    help='source SHAPES.FLX to patch (default: game install)')
    args = ap.parse_args()

    if args.src == SHAPES_FLX:
        # The install dir doubles as install_lv.sh's target; after an
        # install the default "base" here is the previously built artifact
        # (already carrying 856-858 and any hand-run 859+ injections).
        from base_input import pristine_base

        def _shapes_pristine(p):
            raw_ = open(p, 'rb').read()
            from shape_viewer import read_flx_entry as _rfe
            return all(not _rfe(raw_, sid)
                       for sid in (SE_WALL_ID, SW_WALL_ID, CORNER_POST_ID))

        args.src = pristine_base(SHAPES_FLX, _shapes_pristine,
                                 'base U8SHAPES.FLX')

    from shape_viewer import read_flx_entry

    palette = load_palette(PALETTE_FILE)

    print("=== LV Wood Wall Sprite Tool ===")

    dst = args.out if not args.preview else '/tmp/U8SHAPES_patched.FLX'
    raw = open(args.src, 'rb').read()

    # Each wood shape is a structural copy of a real base-game shape with the
    # pixels repainted as vertical planks: identical silhouette per frame, and
    # — critically — a frame layout that matches ScummVM's U8ShapeFormat parser
    # exactly (see encode_frame). We mirror each source shape's full frame count
    # so any frame the prefab references resolves to a real wood frame.
    #   856 ← 24  (SE wall),  857 ← 20  (SW wall),  858 ← 255 (corner post)
    jobs = [
        (SE_WALL_ID,    24,  6, "SE wall"),
        (SW_WALL_ID,    20,  6, "SW wall"),
        (CORNER_POST_ID, 255, 4, "corner post"),
    ]

    first = True
    for new_id, src_id, plank_w, label in jobs:
        src_data = read_flx_entry(raw, src_id)
        nframes = num_frames(src_data)
        frame_blobs = []
        for fi in range(nframes):
            px, w, h, xo, yo = make_wall_pixels(src_data, template_frame=fi,
                                                plank_width=plank_w, seed=44 + fi)
            frame_blobs.append(encode_frame(px, w, h, xo, yo))
        blob = encode_shape_blobs(frame_blobs)
        # First injection reads from the pristine source; the rest chain on dst.
        inject_shape(blob, new_id, args.src if first else dst, dst)
        first = False
        print(f"  {label} shape {new_id} ← {src_id}: {nframes} frames, {len(blob)} bytes")

    # --- Validate against a faithful port of ScummVM's parser ---
    print("\nValidating encoded shapes against ScummVM U8ShapeFormat parser...")
    out_raw = open(dst, 'rb').read()
    ok = True
    for new_id, src_id, _, label in jobs:
        errs = validate_shape(read_flx_entry(out_raw, new_id))
        if errs:
            ok = False
            print(f"  FAIL shape {new_id} ({label}): {errs}")
        else:
            print(f"  OK   shape {new_id} ({label})")
    if not ok:
        raise SystemExit("Validation failed — NOT safe to load in ScummVM.")

    # --preview used to only redirect the output file and never render
    # anything, which made its own help text false. Render for real.
    if args.preview:
        for new_id, _, _, label in jobs:
            preview(new_id, palette, shapes_flx=dst)

    print("\nDone.")
    print(f"  SE wall shape:    {SE_WALL_ID}  (replaces shape 24)")
    print(f"  SW wall shape:    {SW_WALL_ID}  (replaces shape 20)")
    print(f"  Corner post:      {CORNER_POST_ID}  (replaces shape 255)")
    print(f"  WOOD_WALL_REMAP: {{24:{SE_WALL_ID}, 20:{SW_WALL_ID}, 255:{CORNER_POST_ID}}}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
shape_viewer.py — Render U8 shapes from U8SHAPES.FLX and display alongside
                  Lost Vale screenshots for visual matching.

Outputs HTML to shared/build/shape_viewer.html with:
  - LV screenshots annotated with what shapes are needed
  - All frames for candidate shapes rendered at 2x scale
  - Organized by purpose: roofs, walls, floors, pillars, etc.

Usage:
    python3 agents/map-populator/src/shape_viewer.py
    open shared/build/shape_viewer.html
"""

import os
import sys
import struct
import base64
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow required. Install with: pip3 install Pillow")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
SHAPES_FLX = os.path.join(BASE_DIR, "shared", "data", "u8-install", "STATIC", "U8SHAPES.FLX")
PALETTE_FILE = os.path.join(BASE_DIR, "shared", "data", "u8-install", "STATIC", "U8PAL.PAL")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "shared", "data", "lv-screenshots")
OUTPUT_HTML = os.path.join(BASE_DIR, "shared", "build", "shape_viewer.html")


# ---------------------------------------------------------------------------
# FLX reader (minimal, standalone)
# ---------------------------------------------------------------------------

def read_flx_entry(data, index):
    """Read a single entry from a FLX archive."""
    count = struct.unpack_from('<I', data, 0x54)[0]
    if index >= count:
        return None
    entry_off = 0x80 + index * 8
    offset = struct.unpack_from('<I', data, entry_off)[0]
    size = struct.unpack_from('<I', data, entry_off + 4)[0]
    if offset == 0 or size == 0:
        return None
    return data[offset:offset + size]


# ---------------------------------------------------------------------------
# Palette loader
# ---------------------------------------------------------------------------

def load_palette(path):
    """Load U8 palette (6-bit RGB) and return as list of (r,g,b) tuples."""
    with open(path, 'rb') as f:
        data = f.read()
    # 4-byte header, then 256 * 3 bytes of 6-bit RGB
    palette = []
    for i in range(256):
        off = 4 + i * 3
        r6 = data[off]
        g6 = data[off + 1]
        b6 = data[off + 2]
        # 6-bit to 8-bit: (x << 2) | (x >> 4)
        r = (r6 << 2) | (r6 >> 4)
        g = (g6 << 2) | (g6 >> 4)
        b = (b6 << 2) | (b6 >> 4)
        palette.append((r, g, b))
    return palette


# ---------------------------------------------------------------------------
# U8 Shape parser
# ---------------------------------------------------------------------------

def parse_shape_frames(shape_data):
    """Parse a U8 shape entry into list of frame dicts.

    Each frame dict: {width, height, xoff, yoff, compressed, pixels}
    where pixels is a width*height list of palette indices (0xFF = transparent).
    """
    if len(shape_data) < 6:
        return []

    num_frames = struct.unpack_from('<H', shape_data, 4)[0]
    if num_frames == 0 or num_frames > 500:
        return []

    frames = []
    for i in range(num_frames):
        idx_off = 6 + i * 6
        if idx_off + 6 > len(shape_data):
            break
        frame_off = struct.unpack_from('<I', shape_data, idx_off)[0] & 0xFFFFFF
        frame_size = struct.unpack_from('<H', shape_data, idx_off + 4)[0]

        if frame_off + 18 > len(shape_data):
            frames.append(None)
            continue

        frame = _parse_one_frame(shape_data, frame_off, frame_size)
        frames.append(frame)

    return frames


def _parse_one_frame(data, offset, size):
    """Parse a single U8 shape frame at the given offset."""
    # Frame data starts at data[offset], but the U8 format reader
    # skips 8 bytes of "unknown" at the start and treats the frame
    # data as starting 8 bytes BEFORE the offset.
    # Actually: loadU8Format passes (data + frameoffset) to RawShapeFrame,
    # then loadU8Format skips 8 bytes. So the frame header is at offset+8.
    # But wait - the stream is created with (data, size+8) and skip(8),
    # meaning it reads from data[8] onward. The data pointer is (shape_data + frame_off).
    # So compression is at frame_off + 8, width at frame_off + 10, etc.

    fh_off = offset + 8
    if fh_off + 10 > len(data):
        return None

    compressed = data[fh_off]  # just the low byte
    width = struct.unpack_from('<h', data, fh_off + 2)[0]
    height = struct.unpack_from('<h', data, fh_off + 4)[0]
    xoff = struct.unpack_from('<h', data, fh_off + 6)[0]
    yoff = struct.unpack_from('<h', data, fh_off + 8)[0]

    if width <= 0 or height <= 0 or width > 1024 or height > 1024:
        return None

    # Line offsets table: height * uint16, relative
    lo_start = fh_off + 10
    if lo_start + height * 2 > len(data):
        return None

    line_offsets = []
    for i in range(height):
        raw = struct.unpack_from('<H', data, lo_start + i * 2)[0]
        line_offsets.append(raw - (height - i) * 2)

    rle_start = lo_start + height * 2

    # Decode RLE
    keycolor = 0xFF
    pixels = [keycolor] * (width * height)

    for y in range(height):
        if line_offsets[y] < 0:
            continue
        line_ptr = rle_start + line_offsets[y]
        xpos = 0

        safety = 0
        while xpos < width and safety < 1000:
            safety += 1
            if line_ptr >= len(data):
                break

            skip = data[line_ptr]
            line_ptr += 1
            xpos += skip

            if xpos >= width:
                break

            if line_ptr >= len(data):
                break

            dlen_byte = data[line_ptr]
            line_ptr += 1

            if compressed:
                is_rle = dlen_byte & 1
                dlen = dlen_byte >> 1
            else:
                # Uncompressed: dlen is the RAW literal pixel count. ScummVM's
                # ShapeFrame::load only applies `dlen >>= 1` when _compressed
                # is set; for uncompressed frames the byte is used as-is.
                is_rle = 0
                dlen = dlen_byte

            if dlen <= 0:
                continue

            for d in range(dlen):
                if line_ptr >= len(data):
                    break
                px = xpos + d
                if 0 <= px < width:
                    pixels[y * width + px] = data[line_ptr]
                if not is_rle:
                    line_ptr += 1

            xpos += dlen
            if is_rle:
                line_ptr += 1

    return {
        'width': width,
        'height': height,
        'xoff': xoff,
        'yoff': yoff,
        'compressed': compressed,
        'pixels': pixels,
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def frame_to_image(frame, palette, scale=2, bg_color=(40, 40, 40)):
    """Convert a parsed frame to a PIL Image."""
    if frame is None:
        # Return a small placeholder
        img = Image.new('RGB', (16 * scale, 16 * scale), (80, 0, 0))
        return img

    w, h = frame['width'], frame['height']
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))

    for y in range(h):
        for x in range(w):
            idx = frame['pixels'][y * w + x]
            if idx != 0xFF:
                r, g, b = palette[idx]
                img.putpixel((x, y), (r, g, b, 255))

    if scale != 1:
        img = img.resize((w * scale, h * scale), Image.NEAREST)

    # Composite onto background
    bg = Image.new('RGB', img.size, bg_color)
    bg.paste(img, mask=img.split()[3])
    return bg


def image_to_data_uri(img, fmt='PNG'):
    """Convert a PIL Image to a data: URI for embedding in HTML."""
    buf = BytesIO()
    img.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    mime = 'image/png' if fmt == 'PNG' else 'image/jpeg'
    return f"data:{mime};base64,{b64}"


def file_to_data_uri(path):
    """Read a file and return as data: URI."""
    ext = os.path.splitext(path)[1].lower()
    mime = {'gif': 'image/gif', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.png': 'image/png', '.gif': 'image/gif'}
    with open(path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('ascii')
    return f"data:{mime.get(ext, 'image/gif')};base64,{b64}"


# ---------------------------------------------------------------------------
# Shape groups for the viewer
# ---------------------------------------------------------------------------

SHAPE_GROUPS = [
    {
        'title': 'Tenebrae Roof Template — shape 412, extracted from Map 4 building (z=96)',
        'screenshots': [
            ('screen19.gif', 'Zealan village building — brown clay tile roof with ribbed pattern'),
            ('screen22.gif', 'Fenced area — brown roof visible at bottom-right corner'),
        ],
        'note': (
            'Frame layout from a real 4x4 Tenebrae building roof:\n'
            '       W edge  ridge   E body  E body\n'
            '  N      29     48      33      33\n'
            '         29     43      33      33\n'
            '         26     32      34      33\n'
            '  S      25     32      32      34\n'
            'Frame roles: 32=main S-facing body, 33=main E-facing body, 34=SE corner/ridge, '
            '29=W edge, 25/26=SW corners, 43/48=ridge accents, 47=additional ridge.'
        ),
        'shapes': [
            (412, 'Brown ribbed clay roof — frames 25-49 are roof tiles at z=96'),
        ],
    },
    {
        'title': 'Other roof candidates (compare against Tenebrae template above)',
        'screenshots': [],
        'shapes': [
            (271, 'Flat roof/awning (2 frames)'),
            (220, 'Floor/roof tile (55 frames) — many frame variants'),
            (9, 'Floor tile (27 frames)'),
            (162, 'Peaked roof A (7 frames)'),
            (164, 'Peaked roof B (4 frames)'),
        ],
    },
    {
        'title': 'Wall Panels — wooden plank walls for Zealan buildings',
        'screenshots': [
            ('screen19.gif', 'Zealan village — horizontal wooden plank walls'),
        ],
        'shapes': [
            (690, 'Wood wall N-S (2x5 footpad, 5 frames)'),
            (691, 'Wood wall E-W (5x2 footpad, 5 frames)'),
            (622, 'Stone block wall (7 frames) — for temples/foundations'),
            (565, 'Stone platform (unknown frames)'),
            (75, 'Fence/rail A'),
            (199, 'Fence/rail B'),
            (704, 'Wooden fence A'),
            (705, 'Wooden fence B'),
        ],
    },
    {
        'title': 'Cloud City — white marble + gold palette',
        'screenshots': [
            ('screen11.gif', 'Cloud City — white pillars, dark central column'),
            ('screen12.gif', 'Cloud City walkway — gold railings, white marble floor'),
            ('screen13.gif', 'Cloud terrain edge — white/snowy surface, gold tiles at bottom'),
        ],
        'shapes': [
            (148, 'Pillar/post'),
            (155, 'Column'),
            (301, 'Pillar variant A'),
            (302, 'Pillar variant B'),
            (303, 'Pillar variant C'),
            (304, 'Pillar variant D'),
            (305, 'Pillar variant E'),
            (353, 'Rail/edge piece A'),
            (354, 'Rail/edge piece B'),
            (355, 'Rail/edge piece C'),
            (356, 'Rail/edge piece D'),
        ],
    },
    {
        'title': 'Roof Edges & Trim — eaves, gutters, ridgelines',
        'screenshots': [
            ('screen19.gif', 'Building has defined roof edge/eave line'),
        ],
        'shapes': [
            (647, 'Roof edge A'),
            (648, 'Roof edge B'),
            (45, 'Trim piece A'),
            (84, 'Trim piece B'),
            (211, 'Edge piece A'),
            (212, 'Edge piece B'),
        ],
    },
    {
        'title': 'Doors — for village buildings',
        'screenshots': [],
        'shapes': [
            (68, 'Door A'),
            (69, 'Door B'),
            (114, 'Door C'),
            (174, 'Door D (Tenebrae uses this)'),
            (505, 'Door E'),
            (288, 'Door F'),
        ],
    },
]


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def generate_html(flx_data, palette, groups):
    """Generate the complete HTML viewer."""
    lines = ["""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Lost Vale Shape Viewer</title>
<style>
body { background: #1a1a2e; color: #e0e0e0; font-family: 'Courier New', monospace;
       margin: 20px; }
h1 { color: #e6b800; border-bottom: 2px solid #e6b800; padding-bottom: 10px; }
h2 { color: #cc9900; margin-top: 40px; }
.group { background: #16213e; border: 1px solid #333; border-radius: 8px;
         padding: 20px; margin: 20px 0; }
.screenshots { display: flex; flex-wrap: wrap; gap: 20px; margin: 15px 0; }
.screenshot { max-width: 400px; }
.screenshot img { max-width: 100%; border: 2px solid #555; }
.screenshot .caption { font-size: 12px; color: #aaa; margin-top: 4px; }
.shape-section { margin: 15px 0; }
.shape-name { color: #66ccff; font-size: 14px; font-weight: bold; margin: 10px 0 5px; }
.frames { display: flex; flex-wrap: wrap; gap: 6px; align-items: flex-end; }
.frame { text-align: center; background: #0a0a1a; border: 1px solid #333;
         border-radius: 4px; padding: 4px; }
.frame img { display: block; margin: 0 auto; }
.frame .label { font-size: 10px; color: #888; margin-top: 2px; }
.frame:hover { border-color: #e6b800; background: #1a1a3e; }
.note { color: #aaa; font-style: italic; font-size: 13px; margin: 5px 0; }
</style>
</head>
<body>
<h1>Lost Vale Shape Viewer</h1>
<p class="note">Shapes rendered from U8SHAPES.FLX with game palette.
Click/hover frames to highlight. Compare with screenshots to identify correct shapes.</p>
"""]

    for group in groups:
        lines.append(f'<div class="group">')
        lines.append(f'<h2>{group["title"]}</h2>')

        if group.get('note'):
            note_html = group['note'].replace('\n', '<br>')
            lines.append(f'<pre class="note" style="background:#0a0a1a;padding:10px;'
                         f'border-left:3px solid #e6b800;white-space:pre;color:#cce;">'
                         f'{note_html}</pre>')

        # Screenshots
        if group['screenshots']:
            lines.append('<div class="screenshots">')
            for fname, caption in group['screenshots']:
                fpath = os.path.join(SCREENSHOTS_DIR, fname)
                if os.path.exists(fpath):
                    uri = file_to_data_uri(fpath)
                    lines.append(f'<div class="screenshot">')
                    lines.append(f'<img src="{uri}" alt="{fname}">')
                    lines.append(f'<div class="caption"><b>{fname}</b>: {caption}</div>')
                    lines.append(f'</div>')
            lines.append('</div>')

        # Shapes
        for shape_id, desc in group['shapes']:
            shape_data = read_flx_entry(flx_data, shape_id)
            if not shape_data:
                lines.append(f'<div class="shape-name">Shape {shape_id}: {desc} — NOT FOUND</div>')
                continue

            frame_list = parse_shape_frames(shape_data)
            n = len(frame_list)
            lines.append(f'<div class="shape-section">')
            lines.append(f'<div class="shape-name">Shape {shape_id} ({n} frames): {desc}</div>')
            lines.append(f'<div class="frames">')

            for fi, frame in enumerate(frame_list):
                if frame is None:
                    lines.append(f'<div class="frame">'
                                 f'<div style="width:32px;height:32px;background:#300;"></div>'
                                 f'<div class="label">f{fi} (err)</div></div>')
                    continue

                img = frame_to_image(frame, palette, scale=2)
                uri = image_to_data_uri(img)
                w, h = frame['width'], frame['height']
                lines.append(f'<div class="frame">'
                             f'<img src="{uri}" title="Shape {shape_id} frame {fi} ({w}x{h})">'
                             f'<div class="label">f{fi} ({w}x{h})</div></div>')

            lines.append('</div>')  # frames
            lines.append('</div>')  # shape-section

        lines.append('</div>')  # group

    lines.append("""
<h2>Teleport Commands (for in-game comparison)</h2>
<pre>
Cheat::toggle
MainActor::teleport 22 4096 12288 0   — Section D: Roof frame sweep
MainActor::teleport 22 4096 17408 0   — Section E: Cloud City shapes
MainActor::teleport 10 4352  6912  0  — Map 10: Lost Vale village
MainActor::teleport 17 5376 11520  0  — Map 17: Cloud City
</pre>
</body></html>""")

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not os.path.exists(SHAPES_FLX):
        print(f"ERROR: U8SHAPES.FLX not found at {SHAPES_FLX}")
        sys.exit(1)
    if not os.path.exists(PALETTE_FILE):
        print(f"ERROR: U8PAL.PAL not found at {PALETTE_FILE}")
        sys.exit(1)

    print("Loading palette...")
    palette = load_palette(PALETTE_FILE)

    print("Loading U8SHAPES.FLX...")
    with open(SHAPES_FLX, 'rb') as f:
        flx_data = f.read()

    print(f"Generating shape viewer...")
    print(f"  Shape groups: {len(SHAPE_GROUPS)}")
    total_shapes = sum(len(g['shapes']) for g in SHAPE_GROUPS)
    print(f"  Total shapes to render: {total_shapes}")

    html = generate_html(flx_data, palette, SHAPE_GROUPS)

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, 'w') as f:
        f.write(html)

    size_kb = os.path.getsize(OUTPUT_HTML) / 1024
    print(f"\nWrote {OUTPUT_HTML} ({size_kb:.0f} KB)")
    print(f"Open with: open {OUTPUT_HTML}")


if __name__ == '__main__':
    main()

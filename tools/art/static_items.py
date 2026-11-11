#!/usr/bin/env python3
"""
static_items.py: references and game-scale plates for art-track contracts
12 and 13 (docs/art-track.md):

    special-root   shape 869, the special root (Map 10, the Sacred Circle)
    test-plant     shape 871, the Passage Test plant (Map 10, test grounds)

"Judge a candidate at game scale, never at 1024" is the track's recorded
lesson, so every candidate goes through the build's own frame pipeline
(png2shape.build_frame: key, trim, resize, re-key, despill, quantize to
U8PAL, anchor, encode), is DECODED BACK from the encoded blob as the engine
would read it, and only then rendered: at 1x and 4x beside the placeholder
it replaces and its neighbours, and composited into its real site from
FIXED.DAT (globs expanded) as a before/after pair.

Subcommands:

    refs                write the generator references
                        (special-root/reference-reagents.png,
                         test-plant/reference-plants.png)
    plates ITEM CAND..  the plates for one item's candidates
    flatten SRC DST     composite a transparent-background generation onto
                        flat magenta, the input the build recipe expects

All reads are of shared/data/u8-install (shape_viewer.SHAPES_FLX, the
installed U8SHAPES.FLX, whose 0-854 are the base game's) and its FIXED.DAT;
nothing is injected or written to shared/build.

Usage:
    python3 tools/art/static_items.py refs
    python3 tools/art/static_items.py plates special-root A B C
    python3 tools/art/static_items.py plates test-plant A B C
"""

import json
import os
import struct
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))   # tools/png2shape.py
sys.path.insert(0, os.path.join(ROOT, 'agents', 'map-populator', 'src'))

from PIL import Image, ImageDraw                                  # noqa: E402
from png2shape import (build_frame, footpad_screen_size,          # noqa: E402
                       suggest_footpad)
from lv_wood_wall import encode_shape_blobs, validate_shape       # noqa: E402
from shape_viewer import (read_flx_entry, load_palette,           # noqa: E402
                          parse_shape_frames, _parse_one_frame,
                          SHAPES_FLX, PALETTE_FILE)
from iso_render import IsoRenderer, frame_to_rgba                 # noqa: E402
from u8_map import MapArchive, MapItem                            # noqa: E402
from glob_catalog import GlobReader                               # noqa: E402
from map_preview import expand_globs                              # noqa: E402
from parse_typeflag import load_typeflag                         # noqa: E402

ART = os.path.join(ROOT, 'shared', 'docs', 'art-poc')
FIXED = os.path.join(ROOT, 'shared', 'data', 'u8-install', 'STATIC',
                     'FIXED.DAT')
MAGENTA = (255, 0, 255)
BG = (24, 24, 28)
INK = (210, 210, 215)

# ── the contracts, engine side (docs/art-track.md) ──────────────────────
# donor/footpad are the contract's; `height`/`max_w` the game-scale size the
# candidate is judged at; `site` the real placement it is composited into.
ITEMS = {
    'special-root': {
        'shape': 869, 'donor': 180, 'footpad': (2, 2, 1),
        'height': 16, 'max_w': 26,
        'before': [(399, 9)],
        'refs': [('399.9 now', 399, 9), ('395.20 wood', 395, 20),
                 ('38.2 ring stone', 38, 2), ('863 Sacred Rock', 863, 0),
                 ('Avatar', 1, 0)],
        'site': {'map': 10, 'at': (399, 9, 21376, 16640),
                 'box': (20700, 16000, 21900, 17150),
                 'avatar': (21376 - 96, 16640 + 64, 0)},
    },
    'test-plant': {
        'shape': 871, 'donor': 65, 'footpad': (3, 3, 4),
        'height': 48, 'max_w': 48,
        'before': [(126, 0)],
        'refs': [('126.0 now', 126, 0), ('65.0 mushroom', 65, 0),
                 ('66.0 rock spire', 66, 0), ('235.0 bones', 235, 0),
                 ('Avatar', 1, 0)],
        'site': {'map': 10, 'at': (126, 0, 12800, 29408),
                 'box': (12400, 29000, 13300, 29900),
                 'avatar': (12800 + 32, 29408 + 160, 64)},
    },
}


class Shapes:
    """The installed U8SHAPES.FLX, with shape 1 (1550 frames, past
    shape_viewer's 500-frame cap) read frame by frame."""

    def __init__(self):
        self.flx = open(SHAPES_FLX, 'rb').read()
        self.pal = load_palette(PALETTE_FILE)

    def frame(self, shape, i):
        data = read_flx_entry(self.flx, shape)
        if shape == 1:
            o = 6 + i * 6
            off = struct.unpack_from('<I', data, o)[0] & 0xFFFFFF
            size = struct.unpack_from('<H', data, o + 4)[0]
            return _parse_one_frame(data, off, size)
        return parse_shape_frames(data)[i]


def frame_rgba(frame, pal, scale=1, bg=None):
    img, _, _ = frame_to_rgba(frame, pal)
    if bg is not None:
        base = Image.new('RGBA', img.size, bg + (255,))
        base.alpha_composite(img)
        img = base
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale),
                         Image.NEAREST)
    return img


def strip(entries, pal, scale, pad=10, label_h=13, bottom=True):
    """[(label, frame)] -> one row, sprites standing on a common baseline
    (bottom) the way they stand on the floor."""
    imgs = [frame_rgba(f, pal, scale, BG) for _, f in entries]
    w = sum(i.width for i in imgs) + pad * (len(imgs) + 1)
    h = max(i.height for i in imgs) + pad * 2 + (label_h if scale > 1 else 0)
    sh = Image.new('RGB', (w, h), BG)
    dr = ImageDraw.Draw(sh)
    x = pad
    top = pad + (label_h if scale > 1 else 0)
    inner = h - top - pad
    for (label, _), im in zip(entries, imgs):
        y = top + (inner - im.height if bottom else 0)
        sh.paste(im.convert('RGB'), (x, y))
        if scale > 1:
            dr.text((x, 2), label, fill=INK)
        x += im.width + pad
    return sh


def stack(plates, pad=10, title=None):
    th = 16 if title else 0
    w = max(p.width for p in plates)
    h = sum(p.height for p in plates) + pad * (len(plates) - 1) + th
    out = Image.new('RGB', (w, h), BG)
    if title:
        ImageDraw.Draw(out).text((6, 2), title, fill=INK)
    y = th
    for p in plates:
        out.paste(p, (0, y))
        y += p.height + pad
    return out


def side(plates, pad=10):
    w = sum(p.width for p in plates) + pad * (len(plates) - 1)
    h = max(p.height for p in plates)
    out = Image.new('RGB', (w, h), BG)
    x = 0
    for p in plates:
        out.paste(p, (x, 0))
        x += p.width + pad
    return out


def on_magenta(entries, sh, scale, pad=16):
    """Generator reference: base sprites, nearest-scaled, on flat magenta."""
    imgs = [frame_rgba(sh.frame(s, i), sh.pal, scale, MAGENTA)
            for s, i in entries]
    w = sum(i.width for i in imgs) + pad * (len(imgs) + 1)
    h = max(i.height for i in imgs) + pad * 2
    out = Image.new('RGB', (w, h), MAGENTA)
    x = pad
    for im in imgs:
        out.paste(im.convert('RGB'), (x, h - pad - im.height))
        x += im.width + pad
    return out


# ── refs ─────────────────────────────────────────────────────────────────

def cmd_refs():
    sh = Shapes()
    jobs = [
        ('special-root/reference-reagents.png',
         [(395, 16), (395, 19), (395, 20), (399, 4), (399, 7), (399, 9)], 8),
        ('test-plant/reference-plants.png',
         [(65, 0), (65, 2), (65, 6), (625, 0), (753, 0)], 4),
    ]
    for rel, entries, scale in jobs:
        path = os.path.join(ART, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        on_magenta(entries, sh, scale).save(path)
        print('wrote', path)


# ── plates ───────────────────────────────────────────────────────────────

def frame_args(height, width, donor, despill=16):
    """The build's recipe (lv_art_props.frame_args): flat-magenta key at
    tolerance 130, despill 16, bottom-centre anchor."""
    return SimpleNamespace(
        no_key=False, key_rgb=MAGENTA, key_tolerance=130,
        key_despill=despill, no_trim=False, height=height,
        width=width, alpha_threshold=128, anchor='bottom-center',
        donor=donor, xoff=None, yoff=None)


# The despill strips key-coloured bleed BY HUE at game scale, and violet is
# magenta's neighbour: at margin 16 it ate 102 of the purple root's pixels
# (B, 18x16 -> 13x11) and 11 of C's purple leaves (measured 2026-10-11). A
# purple candidate therefore takes margin 0, which an lv_art_props row can
# carry (the fifth element of its frame tuple). The plant's spines are
# purple-black at the tips by design, and margin 16 stripped them from all
# three candidates (A 121 px, B 971, C 141), the very spines that make it
# menacing; margin 0 shows no magenta fringe on any of them at 4x.
DESPILL = {'special-root': {'B': 0, 'C': 0},
           'test-plant': {'A': 0, 'B': 0, 'C': 0}}


def build(paths, spec, flx, pal, despill=16):
    """Candidate PNG(s) -> encoded shape -> decoded frames, plus a report."""
    blobs, rows = [], []
    for i, p in enumerate(paths):
        # Size by height; a candidate drawn wider than the box is sized by
        # width instead, aspect kept either way.
        h, w = spec['height'], None
        _, probe = build_frame(p, frame_args(h, None, spec['donor'], despill),
                               pal, flx, i)
        if spec['max_w'] and probe['size'][0] > spec['max_w']:
            h, w = None, spec['max_w']
        blob, rep = build_frame(p, frame_args(h, w, spec['donor'], despill),
                                pal, flx, i)
        rep['despill_margin'] = despill
        blobs.append(blob)
        rows.append(rep)
    shape = encode_shape_blobs(blobs)
    errors = validate_shape(shape)      # [] means the engine can read it
    if errors:
        raise SystemExit(f'{paths}: shape fails validation: {errors}')
    frames = parse_shape_frames(shape)
    return frames, rows, not errors


def site_render(spec, sh, subs):
    """The real site from FIXED.DAT, globs expanded, with `subs`
    [(old_shape, old_frame, x, y) -> new (shape, frame)] swapped in and an
    Avatar standing beside it for scale."""
    site = spec['site']
    arch = MapArchive(FIXED)
    items = expand_globs(list(arch.get_map_items(site['map'])), GlobReader())
    x0, y0, x1, y1 = site['box']
    items = [it for it in items if x0 <= it.x < x1 and y0 <= it.y < y1]
    for (os_, of, ox, oy), (ns, nf) in subs:
        for it in items:
            if (it.shape, it.frame, it.x, it.y) == (os_, of, ox, oy):
                it.shape, it.frame = ns, nf
    ax, ay, az = site['avatar']
    items.append(MapItem.placed_item(x=ax, y=ay, z=az, shape=1, frame=0))
    return items


_TYPEFLAG = None


def is_floor(shape):
    """A flat walkable tile (SI_LAND, footpad z 0 or 1): painted first.
    IsoRenderer sorts everything on (x+y, z), which draws a floor tile whose
    anchor corner lies nearer the camera OVER a prop standing on the tile
    behind it, so a 48-px plant lost its lower half to the plateau floor."""
    global _TYPEFLAG
    if _TYPEFLAG is None:
        _TYPEFLAG = load_typeflag(os.path.join(
            ROOT, 'shared', 'data', 'u8-install', 'STATIC', 'TYPEFLAG.DAT'))
    si = _TYPEFLAG[shape] if shape < len(_TYPEFLAG) else None
    return bool(si and si.has_flag('SI_LAND') and si.footpad_z <= 1)


def render_scene(items, injected, sh, scale):
    """IsoRenderer's projection and hotspots, with a two-layer order:
    floors by (z, x+y), then everything else by (x+y, z). Still a
    composite, not the engine's sorter."""
    r = IsoRenderer()
    r._img_cache[(1, 0)] = frame_to_rgba(sh.frame(1, 0), sh.pal)
    for key, frame in injected.items():
        r._img_cache[key] = frame_to_rgba(frame, sh.pal)
    skip = (2, 73, 500, 508)
    keyed = []
    for i, it in enumerate(items):
        if it.shape in skip:
            continue
        if is_floor(it.shape):
            keyed.append(((0, it.z, it.x + it.y, i), it))
        else:
            keyed.append(((1, it.x + it.y, it.z, i), it))
    placed = []
    for _, it in sorted(keyed, key=lambda k: k[0]):
        img, xoff, yoff = r._img(it.shape, it.frame)
        if img is None:
            continue
        sx, sy = r.project(it.x, it.y, it.z)
        placed.append((sx - xoff, sy - yoff, img))
    minx = min(p[0] for p in placed)
    miny = min(p[1] for p in placed)
    w = max(p[0] + p[2].width for p in placed) - minx + 16
    h = max(p[1] + p[2].height for p in placed) - miny + 16
    canvas = Image.new('RGBA', (w, h), BG + (255,))
    for px, py, img in placed:
        canvas.alpha_composite(img, (px - minx + 8, py - miny + 8))
    out = canvas.convert('RGB')
    if scale != 1:
        out = out.resize((w * scale, h * scale), Image.NEAREST)
    return out


def crop_scene(img, frac=0.62):
    """Centre crop: the composites are a whole region; the plate wants the
    site and its immediate setting."""
    w, h = img.size
    cw, ch = int(w * frac), int(h * frac)
    return img.crop(((w - cw) // 2, (h - ch) // 2,
                     (w + cw) // 2, (h + ch) // 2))


def cmd_plates(item, cands):
    spec = ITEMS[item]
    sh = Shapes()
    out = os.path.join(ART, item)
    refs = [(lab, sh.frame(s, f)) for lab, s, f in spec['refs']]
    box = footpad_screen_size(*spec['footpad'])
    report = {}
    built = {}
    for c in cands:
        paths = [os.path.join(out, f'{c}_raw.png')]
        missing = [p for p in paths if not os.path.exists(p)]
        if missing:
            print(f'{c}: missing {missing}')
            continue
        frames, rows, ok = build(paths, spec, sh.flx, sh.pal,
                                 DESPILL.get(item, {}).get(c, 16))
        built[c] = frames
        report[c] = {
            'valid': bool(ok), 'footpad': spec['footpad'], 'box': box,
            'frames': [{'size': r['size'], 'anchor': r['anchor'],
                        'colors': r['colors'],
                        'despill_margin': r['despill_margin'],
                        'fits_box': r['size'][0] <= box[0]
                        and r['size'][1] <= box[1],
                        'suggest_footpad': suggest_footpad(*r['size'])}
                       for r in rows]}
        print(f'{item} {c}: valid={bool(ok)} '
              + ', '.join(f"f{i} {r['size'][0]}x{r['size'][1]}"
                          f"{'' if r['size'][0] <= box[0] and r['size'][1] <= box[1] else ' OVER ' + str(box)}"
                          for i, r in enumerate(rows)))
    if not built:
        return

    # 1x and 4x: placeholder and neighbours first, then each candidate.
    cand_entries = [(f'{c} f{i}', f) for c, fs in built.items()
                    for i, f in enumerate(fs)]
    one = strip(refs + cand_entries, sh.pal, 1)
    four = strip(refs[:len(spec['before'])] + cand_entries, sh.pal, 4)
    sheet = stack([one, four],
                  title=f'{item}: shape {spec["shape"]}, donor '
                        f'{spec["donor"]}, footpad {spec["footpad"]} '
                        f'(box {box[0]}x{box[1]} px). Row 1 at 1x: '
                        f'placeholder, neighbours, candidates.')
    sheet.save(os.path.join(out, 'compare.png'))
    print('wrote', os.path.join(out, 'compare.png'))

    # In the site: before, then each candidate, at 1x and 2x.
    at = spec['site']['at']
    before = crop_scene(render_scene(site_render(spec, sh, []), {}, sh, 1))
    scenes = [before]
    for c, fs in built.items():
        subs = [(at, (spec['shape'], 0))]
        inj = {(spec['shape'], i): fr for i, fr in enumerate(fs)}
        scenes.append(crop_scene(render_scene(site_render(spec, sh, subs),
                                              inj, sh, 1)))
    labels = ['before'] + list(built)
    lab = []
    for name, im in zip(labels, scenes):
        tile = Image.new('RGB', (im.width, im.height + 14), BG)
        tile.paste(im, (0, 14))
        ImageDraw.Draw(tile).text((4, 1), name, fill=INK)
        lab.append(tile)
    grid = stack([side(lab[:2]), side(lab[2:])]) if len(lab) > 2 else side(lab)
    grid.save(os.path.join(out, 'site-1x.png'))
    grid.resize((grid.width * 2, grid.height * 2), Image.NEAREST).save(
        os.path.join(out, 'site-2x.png'))
    print('wrote', os.path.join(out, 'site-1x.png'), grid.size)
    rp = os.path.join(out, 'preview_report.json')
    json.dump(report, open(rp, 'w'), indent=1)
    print('report ->', rp)


def cmd_flatten(src, dst):
    """A generator that ignored the magenta instruction and returned soft
    alpha (Codex gpt-image-2 does): composite it onto flat magenta, the
    input the build recipe is tuned for. Fed to build_frame as it is, its
    faint near-transparent pixels widen the first trim's box and are then
    dropped by the re-key, so the sprite lands short of its target height
    (test-plant C: 38x40 for a 48 target)."""
    img = Image.open(src).convert('RGBA')
    flat = Image.new('RGBA', img.size, MAGENTA + (255,))
    flat.alpha_composite(img)
    flat.convert('RGB').save(dst)
    print('wrote', dst)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == 'refs':
        cmd_refs()
    elif argv[0] == 'flatten' and len(argv) == 3:
        cmd_flatten(argv[1], argv[2])
    elif argv[0] == 'plates' and len(argv) > 2 and argv[1] in ITEMS:
        cmd_plates(argv[1], argv[2:])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

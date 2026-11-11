#!/usr/bin/env python3
"""
tiny_avatar_plates.py: the candidate plates for art-track contract 8, the
Tiny Tar body (shape 867, docs/art-track.md).

Every candidate is derived by code from the Avatar's own sprites (shape 1,
1550 frames) with agents/map-populator/src/lv_tiny_avatar_art.py, and goes
through the real pipeline before anything is drawn from it:

    build_frames -> encode_frame / encode_shape_blobs -> validate_shape
    -> inject_shape into a scratch copy of the base U8SHAPES.FLX at 867
    -> read the slot back and decode it
    -> avatar_anim_table into a scratch copy of the base ANIM.DAT
    -> decode 867's action table back out

and every plate below is rendered from those read-back bytes: the stand and
walk frames are the ones 867's own ANIM.DAT entry names, not the ones the
generator meant to write. No image model is involved, so there is no agy
log to read and no PIL-substitution risk (gen_sacred_rock.sh's warning).

Douglas picked O60 with the glow ramp and a scaled stride on 2026-10-11;
that is lv_tiny_avatar_art's SCALE/METHOD/GLOW/STRIDE, and build step 6
(lv_tiny_avatar.py) builds exactly the O60-glow body drawn here. The
"before" rows are 867 as it was until then, a copy of the child 708.

Writes shared/docs/art-poc/tiny-avatar/:

    compare-4x.png, compare-1x.png   stand, 8 directions: shape 1, 867
                                     before (the child 708), each candidate
    walk-<ID>-3x.png                 walk, 8 directions x 8 frames, beside
                                     shape 1's walk at full size
    walk-<ID>.gif                    the same, animated, 8 directions
    ramp-3x.png, ramp-1x.png         frames 60-69 of each candidate and of
                                     the glow variant, between shape 1
                                     frame 3 and the tiny stand, under
                                     708's 60-69 (what the shrink showed)
    ramp-O60.gif, ramp-O60-glow.gif  the shrink at FREE.UNK's pace
    crack-1x.png                     Map 18's crack, before and per candidate
    crack-<ID>-2x.png                the same scene at 2x

Needs only the game install (shared/data/u8-install); the built artifacts
are not read, and nothing under shared/build is written.

Usage:
    python3 tools/art/tiny_avatar_plates.py
"""

import os
import shutil
import struct
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'agents', 'map-populator', 'src')
sys.path.insert(0, SRC)

from PIL import Image, ImageDraw                                  # noqa: E402

from shape_viewer import read_flx_entry, load_palette, PALETTE_FILE  # noqa: E402
from lv_wood_wall import validate_shape, inject_shape             # noqa: E402
import lv_tiny_avatar_art as T                                    # noqa: E402
from base_input import pristine_base                              # noqa: E402

STATIC = os.path.join(ROOT, 'shared', 'data', 'u8-install', 'STATIC')
# install_lv.sh installs the built artifacts over these, keeping .bak
# copies; main() resolves both to the pristine file (base_input.py).
BASE_FLX = os.path.join(STATIC, 'U8SHAPES.FLX')
BASE_ANIM = os.path.join(STATIC, 'ANIM.DAT')
OUT = os.path.join(ROOT, 'shared', 'docs', 'art-poc', 'tiny-avatar')

CHILD = 708
CANDIDATES = [
    # id, method, scale. Stride scale = scale (the feet stay planted).
    ('N60', 'nearest', 0.6),
    ('A60', 'area', 0.6),
    ('O60', 'outline', 0.6),
    ('O50', 'outline', 0.5),
    ('O70', 'outline', 0.7),
]
GLOW = T.GLOW               # the picked ramp's peak tint (R2)
BG = (40, 40, 48)
INK = (215, 215, 220)
WALK, STAND = 0, 2
AFF_FLIPPED = 0x20


def through_pipeline(frames, relocate, stride, base_anim, scratch, tag):
    """encode, validate, inject at 867, read back; anim table, read back.
    Returns (read-back frames, 867's decoded actions)."""
    blob = T.encode(frames)
    errs = validate_shape(blob)
    if errs:
        raise SystemExit(f'{tag}: validate_shape refused it:\n  '
                         + '\n  '.join(errs[:10]))
    flx_path = os.path.join(scratch, f'U8SHAPES-{tag}.FLX')
    inject_shape(blob, T.TINY_SHAPE, BASE_FLX, flx_path)
    back = read_flx_entry(open(flx_path, 'rb').read(), T.TINY_SHAPE)
    if back != blob:
        raise SystemExit(f'{tag}: slot 867 read back different bytes')
    anim = T.avatar_anim_table(base_anim, relocate, stride)
    with open(os.path.join(scratch, f'ANIM-{tag}.DAT'), 'wb') as f:
        f.write(anim)
    acts = T.decode_anim(anim, T.TINY_SHAPE)
    print(f'  {tag}: {len(frames)} frames, {len(blob)} bytes, validate '
          f'clean, read back equal; ANIM.DAT {len(base_anim)} -> {len(anim)}')
    return T.decode_frames(back), acts, flx_path


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def rgba(frame, pal, flip=False):
    w, h = frame['width'], frame['height']
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = img.load()
    for i, c in enumerate(frame['pixels']):
        if c != T.TRANSPARENT:
            px[i % w, i // w] = pal[c] + (255,)
    xoff = frame['xoff']
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        xoff = w - 1 - xoff
    return img, xoff, frame['yoff']


def strip(cells, pal, scale, cell_w, top, bottom, label=None, label_w=0):
    """One row of frames, every frame's anchor on the same baseline at the
    centre of its cell, so sizes compare honestly."""
    w = label_w + cell_w * len(cells)
    img = Image.new('RGBA', (w * scale, (top + bottom) * scale), BG + (255,))
    for k, (frame, flip) in enumerate(cells):
        if frame is None:
            continue
        im, xo, yo = rgba(frame, pal, flip)
        cx = label_w + k * cell_w + cell_w // 2
        sub = Image.new('RGBA', (w, top + bottom), (0, 0, 0, 0))
        sub.alpha_composite(im, (cx - xo, top - yo))
        if scale != 1:
            sub = sub.resize((sub.width * scale, sub.height * scale),
                             Image.NEAREST)
        img.alpha_composite(sub)
    if label:
        ImageDraw.Draw(img).text((3, 3), label, fill=INK)
    return img.convert('RGB')


def stack(rows, pad=4):
    w = max(r.width for r in rows)
    h = sum(r.height for r in rows) + pad * (len(rows) - 1)
    img = Image.new('RGB', (w, h), BG)
    y = 0
    for r in rows:
        img.paste(r, (0, y))
        y += r.height + pad
    return img


def side(imgs, pad=8):
    w = sum(i.width for i in imgs) + pad * (len(imgs) - 1)
    h = max(i.height for i in imgs)
    img = Image.new('RGB', (w, h), BG)
    x = 0
    for i in imgs:
        img.paste(i, (x, 0))
        x += i.width + pad
    return img


def action_cells(frames, acts, action, step=0):
    """Frame `step` of `action` in each of the 8 directions, as the
    engine would pick them: frame number and flip flag from the table."""
    _size, _fl, _rep, dirs = acts[action]
    out = []
    for d in range(8):
        fnum, _dz, _sfx, _dd, ff = dirs[d][step]
        out.append((frames[fnum], bool(ff & AFF_FLIPPED)))
    return out


# ---------------------------------------------------------------------------
# Map 18
# ---------------------------------------------------------------------------

def crack_items():
    """The crack's neighbourhood from build_map_18's own builders (the
    hall and the sanctum; void_floor needs a built TYPEFLAG and is only
    the black skirt, so it is left out), globs expanded."""
    import build_map_18
    import glob_catalog
    import map_preview
    items = (build_map_18.build_transition_hall()
             + build_map_18.build_inner_sanctum())
    items = map_preview.expand_globs(items, glob_catalog.GlobReader())
    return [it for it in items
            if 2560 <= it.x <= 3200 and 5760 <= it.y <= 6600]


def crack_scene(renderer, items, actors, scale):
    """Floors first, then everything else back to front with the actors
    among them; iso_render's single x+y sort lets floor tiles nearer the
    viewer paint over an actor standing on the tile behind."""
    from u8_map import MapItem
    ext = [MapItem.placed_item(x=x, y=y, z=z, shape=s, frame=f)
           for (x, y, z, s, f) in actors]
    floors = [it for it in items if it.shape == 35]
    rest = [it for it in items if it.shape != 35] + ext
    rest.sort(key=lambda it: (it.x + it.y, it.z))
    placements = []
    for it in floors + rest:
        if it.shape in (2, 73, 500, 508):
            continue
        img, xo, yo = renderer._img(it.shape, it.frame)
        if img is None:
            continue
        sx, sy = renderer.project(it.x, it.y, it.z)
        placements.append((sx - xo, sy - yo, img))
    minx = min(p[0] for p in placements)
    miny = min(p[1] for p in placements)
    maxx = max(p[0] + p[2].width for p in placements)
    maxy = max(p[1] + p[2].height for p in placements)
    canvas = Image.new('RGBA', (maxx - minx + 16, maxy - miny + 16),
                       (28, 28, 38, 255))
    for px, py, img in placements:
        canvas.alpha_composite(img, (px - minx + 8, py - miny + 8))
    out = canvas.convert('RGB')
    if scale != 1:
        out = out.resize((out.width * scale, out.height * scale),
                         Image.NEAREST)
    return out


# The sanctum side of the wall line y 6143 is the side facing the viewer;
# anything on the hall side is behind 40 units of wall. The tiny body
# stands in the crack at x 2852, the position
# docs/playtest-2026-10-09-crack-aramina.md C1 walked through, between the
# full-size Avatar and the child on the sanctum floor.
AVATAR_AT = (2740, 6250, 0)
TINY_AT = (2852, 6143, 0)
CHILD_AT = (2980, 6250, 0)


def _slot_empty(path, read):
    with open(path, 'rb') as f:
        return not read(f.read())


def main():
    global BASE_FLX, BASE_ANIM
    BASE_FLX = pristine_base(BASE_FLX, lambda p: _slot_empty(
        p, lambda d: read_flx_entry(d, T.TINY_SHAPE)), 'base U8SHAPES.FLX')
    BASE_ANIM = pristine_base(BASE_ANIM, lambda p: _slot_empty(
        p, lambda d: T.anim_offset(d, T.TINY_SHAPE)), 'base ANIM.DAT')
    os.makedirs(OUT, exist_ok=True)
    pal = load_palette(PALETTE_FILE)
    flx = open(BASE_FLX, 'rb').read()
    base_anim = open(BASE_ANIM, 'rb').read()
    avatar = T.decode_frames(read_flx_entry(flx, T.AVATAR_SHAPE))
    child = T.decode_frames(read_flx_entry(flx, CHILD))
    acts1 = T.decode_anim(base_anim, T.AVATAR_SHAPE)
    acts708 = T.decode_anim(base_anim, CHILD)
    quant = T.Quantizer(pal, T.used_indices(avatar))
    glow_quant = T.Quantizer(pal, range(255))

    scratch = tempfile.mkdtemp(prefix='tiny-avatar-')
    results = {}
    try:
        for cid, method, s in CANDIDATES:
            frames, relocate = T.build_frames(avatar, s, method, quant,
                                              base_anim)
            results[cid] = through_pipeline(frames, relocate, s, base_anim,
                                            scratch, cid) + (s,)
        frames, relocate = T.build_frames(avatar, T.SCALE, T.METHOD, quant,
                                          base_anim, glow=GLOW,
                                          glow_quant=glow_quant)
        glow_rb = through_pipeline(frames, relocate, T.STRIDE, base_anim,
                                   scratch, 'O60-glow')
        # 867 before 2026-10-11, for the "before" rows: 708's blob and table.
        today_flx = os.path.join(scratch, 'U8SHAPES-today.FLX')
        inject_shape(read_flx_entry(flx, CHILD), T.TINY_SHAPE, BASE_FLX,
                     today_flx)

        # -- stand, 8 directions ------------------------------------------
        for scale, name in ((4, 'compare-4x.png'), (1, 'compare-1x.png')):
            lw = 34 if scale == 1 else 18
            rows = [strip(action_cells(avatar, acts1, STAND), pal, scale, 36,
                          60, 6, 'shape 1' if scale > 1 else '1', lw),
                    strip(action_cells(child, acts708, STAND), pal, scale,
                          36, 60, 6, '867 before (708)' if scale > 1
                          else 'was', lw)]
            for cid, (fr, acts, _p, _s) in results.items():
                rows.append(strip(action_cells(fr, acts, STAND), pal, scale,
                                  36, 60, 6, cid, lw))
            stack(rows).save(os.path.join(OUT, name))

        # -- walk, 8 directions x 8 frames -------------------------------
        for cid, (fr, acts, _p, _s) in results.items():
            left = stack([strip([action_cells(avatar, acts1, WALK, j)[d]
                                 for j in range(1, 9)], pal, 3, 48, 60, 6)
                          for d in range(8)])
            right = stack([strip([action_cells(fr, acts, WALK, j)[d]
                                  for j in range(1, 9)], pal, 3, 48, 60, 6)
                           for d in range(8)])
            side([left, right], 24).save(
                os.path.join(OUT, f'walk-{cid}-3x.png'))
            gif = []
            for j in range(1, 9):
                top = strip(action_cells(avatar, acts1, WALK, j), pal, 3, 48,
                            60, 6)
                bot = strip(action_cells(fr, acts, WALK, j), pal, 3, 48,
                            60, 6)
                gif.append(stack([top, bot]))
            gif[0].save(os.path.join(OUT, f'walk-{cid}.gif'), save_all=True,
                        append_images=gif[1:], duration=100, loop=0)

        # -- ramp ---------------------------------------------------------
        def ramp_cells(fr, acts):
            stand = action_cells(fr, acts, STAND)[3][0]
            return ([(avatar[T.RAMP_SOURCE_FRAME], False)]
                    + [(fr[k], False) for k in range(T.RAMP_FIRST,
                                                     T.RAMP_LAST + 1)]
                    + [(stand, False)])
        # 867 before: what FREE's setFrame(60..69) showed on 708's frames
        # (its die action, contract 8 finding 2), with no bookends.
        today_ramp = ([(None, False)]
                      + [(child[k], False) for k in range(T.RAMP_FIRST,
                                                          T.RAMP_LAST + 1)]
                      + [(None, False)])
        for scale, name in ((3, 'ramp-3x.png'), (1, 'ramp-1x.png')):
            lw = 34 if scale == 1 else 26
            rows = [strip(today_ramp, pal, scale, 44, 60, 6,
                          'was' if scale == 1 else 'before', lw)]
            rows += [strip(ramp_cells(fr, acts), pal, scale, 44, 60, 6,
                           cid, lw)
                     for cid, (fr, acts, _p, _s) in results.items()]
            rows.append(strip(ramp_cells(glow_rb[0], glow_rb[1]), pal, scale,
                              44, 60, 6, 'glow' if scale == 1
                              else 'O60 glow', lw))
            stack(rows).save(os.path.join(OUT, name))
        for tag, (fr, acts) in (('ramp-O60.gif', results['O60'][:2]),
                                ('ramp-O60-glow.gif', glow_rb[:2])):
            seq = [(avatar[T.RAMP_SOURCE_FRAME], 1000)]
            seq += [(fr[k], 333) for k in range(T.RAMP_FIRST, T.RAMP_LAST + 1)]
            seq += [(action_cells(fr, acts, STAND)[3][0], 1500)]
            ims = [strip([(f, False)], pal, 4, 40, 60, 6) for f, _ in seq]
            ims[0].save(os.path.join(OUT, tag), save_all=True,
                        append_images=ims[1:],
                        duration=[d for _, d in seq], loop=0)

        # -- Map 18 crack -------------------------------------------------
        import iso_render
        items = crack_items()
        panels = []
        for cid, flx_path, fr in [('today', today_flx, child)] + [
                (c, results[c][2], results[c][0]) for c in results]:
            r = iso_render.IsoRenderer(shapes_flx=flx_path)
            # iso_render's parse_shape_frames stops at 500 frames; shape 1
            # and the candidates have 1550+. Hand it the full decodes (867's
            # is the read-back of flx_path's own slot).
            r._frames_cache[T.AVATAR_SHAPE] = avatar
            r._frames_cache[T.TINY_SHAPE] = fr
            actors = [AVATAR_AT + (1, 3), TINY_AT + (T.TINY_SHAPE,
                                                    4 if cid == 'today'
                                                    else 3),
                      CHILD_AT + (CHILD, 4)]
            one = crack_scene(r, items, actors, 1)
            lab = one.copy()
            ImageDraw.Draw(lab).text((6, 6), cid if cid != 'today'
                                     else '867 before (708)', fill=INK)
            panels.append(lab)
            if cid != 'today':
                crack_scene(r, items, actors, 2).save(
                    os.path.join(OUT, f'crack-{cid}-2x.png'))
        grid = stack([side(panels[:3]), side(panels[3:])])
        grid.save(os.path.join(OUT, 'crack-1x.png'))
    finally:
        shutil.rmtree(scratch)
    for n in sorted(os.listdir(OUT)):
        print(f'  wrote {os.path.relpath(os.path.join(OUT, n), ROOT)}')


if __name__ == '__main__':
    main()

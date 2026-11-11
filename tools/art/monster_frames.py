#!/usr/bin/env python3
"""
monster_frames.py — the Water Zombie (872) and the Harpie (873): reference
strips, sheet splitting, the derived walk samples, and the plates.

Art-track item 9, docs/art-track.md contract 9. Douglas, 2026-10-11:
"generate key poses, derive the rest". tools/art/gen_monsters.sh generates;
this derives and plates. Phase 1 only: nothing here touches a build
artifact. Every frame shown on a plate has been through the real pipeline
(quantize -> lv_wood_wall.encode_frame -> encode_shape_blobs ->
validate_shape -> inject_shape into a SCRATCH copy of U8SHAPES.FLX at the
contract's slot -> parse_shape_frames read-back), so a plate is what the
engine would be handed.

THE TWO DERIVATIONS, AND WHY THEY DIFFER

Water Zombie: RAMP TRANSFER onto the donor's own frames. The ghoul (142)
is already a shambling undead with 162 drawn frames of hand-made Origin
animation. The candidate's colours are read off its key poses by anatomy
(head, torso and legs are flesh, the hip band is the rags, the most
saturated tenth is the accent: weed, slime, tide stain), and each donor
material (the palette's own hue groups: skin and its shading greys, the
brown rags, the red wounds, the green tint) is quantile-matched by
luminance to the matching candidate colours, so each donor index gets one
target index: a 256-entry lookup table. Applying one table to every frame
is coherent by construction: the donor's dithering, its shading and its
motion are kept pixel for pixel, nothing can flicker, and the whole
451-frame set derives in seconds. The cost is that the silhouette stays
the ghoul's: whatever the candidate adds outside the ghoul's outline
(trailing weed, a bloated belly) does not transfer. Pixel registration of
each key pose onto the donor frame of the same pose was tried first and
dropped: the generated poses are upright and the ghoul's are hunched, so
the pairs mixed skin with background outline and the table came out dark.
Per-frame img2img was rejected: it repaints each frame independently, so
details swim from frame to frame, and 162 generations is about 40 times
the quota one session got (2026-10-11: Nano Banana walled after 4 images,
codex after 4 more).

Harpie: SHEET SEQUENCING. The torax (120) is a crawling quadruped, so its
silhouette is useless as a guide for a winged biped; what it gives is the
frame LAYOUT (which ANIM.DAT indexes, so the anim entry can be cloned) and
the timing. Each drawn direction gets one generated sheet of four wing
phases of the same body (gen_monsters.sh walk); the four come out of one
image, so they are one creature. They are scaled with ONE factor per
sheet (never per figure, which would make the body pulse), aligned on the
body, and sequenced into the donor's 7-frame cycle with a one-pixel body
bob, so 4 drawings make 7 frames.

Usage (from the repo root):
    tools/art/monster_frames.py refs
    tools/art/monster_frames.py split
    tools/art/monster_frames.py keys
    tools/art/monster_frames.py zombie A
    tools/art/monster_frames.py harpie A
"""

import collections
import colorsys
import contextlib
import io
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, 'agents', 'map-populator', 'src')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
sys.path.insert(0, HERE)
sys.path.insert(0, SRC)

from PIL import Image, ImageDraw                                   # noqa: E402

from shape_viewer import read_flx_entry, parse_shape_frames, load_palette  # noqa: E402
from lv_wood_wall import (encode_frame, encode_shape_blobs,         # noqa: E402
                          validate_shape, inject_shape)
from base_input import pristine_base                               # noqa: E402
from png2shape import key_out, rekey_alpha, despill_edge, quantize  # noqa: E402

STATIC = os.path.join(ROOT, 'shared', 'data', 'u8-install', 'STATIC')
BASE_SHAPES = os.path.join(STATIC, 'U8SHAPES.FLX')
BASE_ANIM = os.path.join(STATIC, 'ANIM.DAT')
PALETTE = os.path.join(STATIC, 'U8PAL.PAL')
BUILT_SHAPES = os.path.join(ROOT, 'shared', 'build', 'U8SHAPES.FLX')
POC = os.path.join(ROOT, 'shared', 'docs', 'art-poc')
ZDIR = os.path.join(POC, 'water-zombie')
HDIR = os.path.join(POC, 'harpie')
SCRATCH = os.environ.get('LV_SCRATCH', '/tmp/lv-monsters')

WATER_ZOMBIE, HARPIE = 872, 873
GHOUL, TORAX, AVATAR = 142, 120, 1
MAGENTA = (255, 0, 255)
KEY_TOL = 130            # split_sheet's tolerance, the recipe the track settled on
POSES = ('idle', 'walk', 'attack', 'dead')
PHASES = ('up', 'downstroke', 'down', 'upstroke')
ATTACK_PHASES = ('ready', 'rear', 'lunge', 'strike', 'recover')
DIE_PHASES = ('struck', 'falling', 'dropping', 'landing', 'dead')

# The donor frame of each key pose, all facing the viewer (direction 3,
# unflipped in both donors' ANIM.DAT entries).
ZOMBIE_KEY_FRAMES = {'idle': 40, 'walk': 44, 'attack': 122, 'dead': 219}
TORAX_KEY_FRAMES = {'idle': 40, 'walk': 43, 'attack': 122, 'dead': 238}

# ANIM.DAT walk (action 0): drawn direction -> first frame, and the three
# mirrored directions, read from the donors' entries (contract 9 table).
GHOUL_WALK = {7: 0, 3: 40, 4: 50, 5: 60, 6: 70}     # 8 frames each
TORAX_WALK = {7: 0, 3: 40, 4: 50, 5: 60, 6: 70}     # 7 frames each
MIRROR = {0: 6, 1: 5, 2: 4}                          # flipped dir -> drawn dir

# Palette indices 1-14 are rewritten every tick by CycleProcess
# (gfx/cycle_process.cpp: 1-7 rotate, 8-14 cycle), so a derived pixel must
# never land on one. 255 is the shape format's transparency.
CYCLING = set(range(1, 15))

# Harpie game scale: the wings-up WALK key pose, the tallest the creature
# ever gets, is this many pixels. The idle pose is no use as the measure:
# its height is mostly how level the generator drew the wings, so it scaled
# the codex candidates (wings flat) half again larger than A. 64 leaves the
# body a little smaller than the Avatar (shape 1 frame 0 is 24x50) under a
# wingspan wider than him, near the torax's own 35-40 px.
HARPIE_UP_H = 64
HARPIE_HOVER = 6         # px between the talons and the donor's ground line
# The donor's 7-frame walk from 4 drawn phases: (phase, body bob in px, up
# is negative). The downstroke lifts the body, the upstroke lets it sink.
HARPIE_CYCLE = ((0, 0), (1, -1), (2, -2), (2, -1), (3, 0), (3, 1), (0, 1))


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

_cache = {}


def base_flx():
    if 'flx' not in _cache:
        with contextlib.redirect_stdout(io.StringIO()):
            path = pristine_base(BASE_SHAPES, None, 'base U8SHAPES.FLX')
        _cache['flx'] = open(path, 'rb').read()
    return _cache['flx']


def palette():
    if 'pal' not in _cache:
        _cache['pal'] = load_palette(PALETTE)
    return _cache['pal']


def quant_palette():
    """The palette as png2shape.quantize sees it, with the cycling indices
    pushed out of reach so the nearest-colour search can never pick one."""
    return [(10 ** 4,) * 3 if i in CYCLING else c
            for i, c in enumerate(palette())]


def frames_of(shape, flx=None):
    return parse_shape_frames(read_flx_entry(flx or base_flx(), shape))


def frame_rgba(fr):
    w, h = fr['width'], fr['height']
    pal = palette()
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = img.load()
    for i, p in enumerate(fr['pixels']):
        if p != 255:
            r, g, b = pal[p]
            px[i % w, i // w] = (r, g, b, 255)
    return img


def anim_walk(shape):
    """ANIM.DAT action 0 for a shape: {dir: [(frame, flipped)...]}."""
    with contextlib.redirect_stdout(io.StringIO()):
        data = open(pristine_base(BASE_ANIM, None, 'base ANIM.DAT'), 'rb').read()
    off = struct.unpack_from('<I', data, 4 * shape)[0]
    ao = struct.unpack_from('<I', data, off)[0]
    size, rep = data[ao], data[ao + 2]
    p, out = ao + 4, {}
    for d in range(8):
        seq = []
        for _ in range(size):
            b = data[p:p + 6]
            p += 6
            seq.append((b[0] + ((b[1] & 7) << 8), bool(b[5] & 0x20)))
        out[d] = seq
    return out, rep


# ---------------------------------------------------------------------------
# The real pipeline: pixels -> encoded shape -> scratch FLX -> read back
# ---------------------------------------------------------------------------

def rgba_to_frame(img, xoff, yoff):
    """Quantize an RGBA image (alpha already 0/255) to a frame dict."""
    pixels, _ = quantize(img, quant_palette())
    bad = CYCLING.intersection(pixels)
    assert not bad, f'cycling indices emitted: {sorted(bad)}'
    return dict(width=img.width, height=img.height, xoff=xoff, yoff=yoff,
                pixels=pixels)


def through_pipeline(shape_id, frames, label):
    """Encode `frames` (list of frame dicts; None = copy nothing, a 1x1
    blank) as one shape, validate it, inject it at `shape_id` into a scratch
    copy of the built U8SHAPES.FLX, and return the frames READ BACK."""
    blobs = []
    for fr in frames:
        if fr is None:
            fr = dict(width=1, height=1, xoff=0, yoff=0, pixels=[255])
        blobs.append(encode_frame(list(fr['pixels']), fr['width'],
                                  fr['height'], fr['xoff'], fr['yoff']))
    blob = encode_shape_blobs(blobs)
    errs = validate_shape(blob)
    if errs:
        raise SystemExit(f'{label}: validate_shape refused:\n  ' +
                         '\n  '.join(errs[:10]))
    os.makedirs(SCRATCH, exist_ok=True)
    src = BUILT_SHAPES if os.path.exists(BUILT_SHAPES) else BASE_SHAPES
    dst = os.path.join(SCRATCH, f'U8SHAPES-{label}.FLX')
    with contextlib.redirect_stdout(io.StringIO()):
        inject_shape(blob, shape_id, src, dst)
    flx = open(dst, 'rb').read()
    back = parse_shape_frames(read_flx_entry(flx, shape_id))
    assert len(back) == len(frames), (len(back), len(frames))
    print(f'  {label}: {len(frames)} frames, {len(blob)} bytes, validate_shape '
          f'clean, injected at {shape_id} in {dst}, read back')
    return back, dst


# ---------------------------------------------------------------------------
# Sheets -> game-scale figures
# ---------------------------------------------------------------------------

def keyed(path):
    """A sheet or piece with its background removed. Nano Banana returns
    flat magenta, which is keyed; gpt-image-2 (the codex route) ignores the
    magenta request and returns real transparency, with a haze of alpha-1
    and alpha-2 pixels over the empty canvas, so alpha is also cut at 128."""
    img, _ = key_out(Image.open(path), MAGENTA, KEY_TOL)
    a = img.split()[3].point(lambda v: 255 if v >= 128 else 0)
    img.putalpha(a)
    return img


def to_game(img, factor):
    """Lanczos to game scale with one factor, then the shape format's
    binary alpha and the magenta despill png2shape uses."""
    w, h = img.size
    small = img.resize((max(1, round(w * factor)), max(1, round(h * factor))),
                       Image.LANCZOS)
    small = rekey_alpha(small, 128)
    small, _ = despill_edge(small, MAGENTA, 40)
    return small


def piece_paths(stem, names):
    return [f'{stem}_f{i}_{n}_raw.png' for i, n in enumerate(names)]


def split_figures(path, names, cell=4):
    """Cut a sheet into its figures by 2-D connected components, not by
    columns: split_sheet.py's column bands fail when one pose's reach
    overlaps the next pose's columns (an attacking arm over a corpse) though
    the two never touch. The keyed mask is reduced to `cell`-px cells and
    dilated one cell, so drips and feather tips a few pixels off the body
    join it; the len(names) largest components are the figures, ordered left
    to right, and any other component is either a crumb (under 3% of the
    smallest figure, given to the nearest figure) or a refusal. Each figure
    is written at the sheet's full height so a sheet's shared ground line
    survives the cut."""
    img = keyed(path)
    w, h = img.size
    a = img.split()[3].load()
    gw, gh = (w + cell - 1) // cell, (h + cell - 1) // cell
    occ = [[False] * gw for _ in range(gh)]
    for y in range(h):
        for x in range(w):
            if a[x, y]:
                occ[y // cell][x // cell] = True
    dil = [[any(occ[j][i] for j in range(max(0, y - 1), min(gh, y + 2))
                for i in range(max(0, x - 1), min(gw, x + 2)))
            for x in range(gw)] for y in range(gh)]
    label = [[-1] * gw for _ in range(gh)]
    comps = []
    for y in range(gh):
        for x in range(gw):
            if dil[y][x] and label[y][x] < 0:
                n = len(comps)
                stack, cells = [(x, y)], []
                label[y][x] = n
                while stack:
                    cx, cy = stack.pop()
                    cells.append((cx, cy))
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = cx + dx, cy + dy
                            if (0 <= nx < gw and 0 <= ny < gh and dil[ny][nx]
                                    and label[ny][nx] < 0):
                                label[ny][nx] = n
                                stack.append((nx, ny))
                comps.append(cells)
    real = [sum(occ[cy][cx] for cx, cy in c) for c in comps]
    order = sorted(range(len(comps)), key=lambda k: -real[k])
    if len(order) < len(names):
        raise SystemExit(f'MISS {os.path.basename(path)}: {len(order)} '
                         f'figure(s), need {len(names)}')
    figs = order[:len(names)]
    floor = min(real[k] for k in figs)
    owner = {k: k for k in figs}
    for k in order[len(names):]:
        if real[k] > 0.03 * floor:
            raise SystemExit(f'MISS {os.path.basename(path)}: a fifth mass '
                             f'of {real[k]} cells (figures: '
                             f'{[real[f] for f in figs]}); refusing to guess')
        cx = sum(x for x, _ in comps[k]) / len(comps[k])
        cy = sum(y for _, y in comps[k]) / len(comps[k])
        owner[k] = min(figs, key=lambda f: min((x - cx) ** 2 + (y - cy) ** 2
                                               for x, y in comps[f]))
    figs.sort(key=lambda f: sum(x for x, _ in comps[f]) / len(comps[f]))
    stem = os.path.splitext(path)[0]
    stem = stem[:-4] if stem.endswith('_raw') else stem
    src = img.load()
    out = []
    for i, (f, name) in enumerate(zip(figs, names)):
        mine = {k for k, o in owner.items() if o == f}
        xs = [cx for k in mine for cx, _ in comps[k]]
        x0, x1 = max(0, (min(xs) - 1) * cell), min(w, (max(xs) + 2) * cell)
        piece = Image.new('RGB', (x1 - x0, h), MAGENTA)
        pp = piece.load()
        for y in range(h):
            for x in range(x0, x1):
                if src[x, y][3] and label[y // cell][x // cell] in mine:
                    pp[x - x0, y] = src[x, y][:3]
        dest = f'{stem}_f{i}_{name}_raw.png'
        piece.save(dest)
        out.append(dest)
        print(f'  f{i} {name:10s} columns {x0}..{x1}, {real[f]} cells '
              f'+ {len(mine) - 1} crumb(s) -> {os.path.basename(dest)}')
    return out


def split_all():
    for d in (ZDIR, HDIR):
        for c in 'ABC':
            p = os.path.join(d, f'keys_{c}_raw.png')
            if os.path.exists(p):
                print(f'== {os.path.relpath(p, ROOT)}')
                split_figures(p, POSES)
    for f in sorted(os.listdir(HDIR)):
        for kind, names in (('walk', PHASES), ('attack', ATTACK_PHASES),
                            ('die', DIE_PHASES)):
            if (f.startswith(kind + '_') and f.endswith('_raw.png')
                    and '_f' not in f):
                print(f'== {f}')
                split_figures(os.path.join(HDIR, f), names)


# ---------------------------------------------------------------------------
# Water Zombie: ramp transfer
# ---------------------------------------------------------------------------

def material(idx):
    """Donor palette index -> material class, by the palette's own hue. The
    ghoul's indices fall into these groups (contract 9 lists them)."""
    r, g, b = palette()[idx]
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    h *= 360
    if l < 0.07:
        return 'outline'           # 0, 31, 79, 222, 223 ...: kept as drawn
    if 90 <= h <= 150:
        # the ghoul's green: the tint on its face and, in the death frames,
        # the rising motes; the bright end is the eyes and the motes' cores
        return 'spark' if l >= 0.4 else 'glow'
    if s < 0.05 or 200 <= h <= 260:
        return 'flesh'             # 18-29 and 250-253: the shading greys
    if h < 14 or h > 340:
        return 'blood'             # 44-47, 186-190: the wounds
    if 14 <= h < 45:
        return 'rags'              # 167-174, 209-223: the brown loincloth
    return 'flesh'                 # 195-199, the olive-grey skin itself


def lum(c):
    r, g, b = c
    return 0.299 * r + 0.587 * g + 0.114 * b


def zombie_factor(cand):
    """One scale for every image of a candidate: the upright idle pose
    becomes as tall as the ghoul's own upright idle (frames 380-420, 55 px)."""
    idle = keyed(piece_paths(os.path.join(ZDIR, f'keys_{cand}'), POSES)[0])
    bb = idle.getbbox()
    return 55 / (bb[3] - bb[1])


def key_samples(cand):
    """The candidate's colours by material, read off its key poses at twice
    game scale. No pixel registration: a generated upright pose does not
    overlay the ghoul's hunch, so the materials are read by ANATOMY on the
    upright poses (idle, walk): the head-and-torso band and the legs are
    flesh, the hip band is the rags. The accent is the most saturated tenth
    of all four poses (the weed, the slime, the tide stain). The outline and
    anything darker than L 45 is left out: the donor keeps its own."""
    f = zombie_factor(cand) * 2
    flesh, rags, everything = [], [], []
    paths = piece_paths(os.path.join(ZDIR, f'keys_{cand}'), POSES)
    for pose, path in zip(POSES, paths):
        s = to_game(keyed(path), f)
        bb = s.getbbox()
        px = s.load()
        H = bb[3] - bb[1]
        for y in range(bb[1], bb[3]):
            t = (y - bb[1]) / H
            for x in range(bb[0], bb[2]):
                c = px[x, y]
                if not c[3] or lum(c[:3]) < 45:
                    continue
                everything.append(c[:3])
                if pose not in ('idle', 'walk'):
                    continue
                if 0.12 <= t < 0.45 or 0.70 <= t < 0.97:
                    flesh.append(c[:3])
                elif 0.50 <= t < 0.66:
                    rags.append(c[:3])

    def sat(c):
        return colorsys.rgb_to_hsv(*(v / 255 for v in c))[1]
    accent = sorted(everything, key=sat)[-max(1, len(everything) // 10):]
    return {'flesh': flesh, 'rags': rags, 'accent': accent}


def quantile_target(donor_l, samples):
    """Map a donor luminance to the candidate colour at the same quantile:
    donor_l is the class's donor pixel luminances (with repeats, so the
    quantile is by pixel count), samples the candidate's colours."""
    d_l = sorted(donor_l)
    r_s = sorted(samples, key=lum)
    n, m = len(d_l), len(r_s)

    def target(l):
        lo = sum(1 for x in d_l if x < l)
        hi = sum(1 for x in d_l if x <= l)
        q = (lo + hi) / 2 / n
        a = max(0, int((q - 0.06) * m))
        b = min(m, max(a + 1, int((q + 0.06) * m)))
        win = r_s[a:b]
        # per-channel median: a window mixing two materials (skin and the
        # weed lying on it) takes the dominant one, not a murky average
        return tuple(sorted(c[k] for c in win)[len(win) // 2] for k in range(3))
    return target


def build_lut(cand):
    """The 256-entry donor-index -> target-index table for one candidate.
    Each donor material is quantile-matched by luminance to the candidate's
    colours for it: flesh to flesh, rags to rags, the wounds and the green
    tint to the accent, and the eyes and the death motes' bright cores to a
    fixed pale-water ramp (they are a handful of pixels no key pose shows
    at a usable size). The outline is kept."""
    samples = key_samples(cand)
    pal = palette()
    qpal = quant_palette()
    used = collections.Counter()
    for fr in frames_of(GHOUL):
        if fr:
            used.update(p for p in fr['pixels'] if p != 255)
    by_class = collections.defaultdict(list)
    for i, n in used.items():
        by_class[material(i)].append(i)
    source = {'flesh': 'flesh', 'rags': 'rags', 'blood': 'accent',
              'glow': 'accent'}
    lut = list(range(256))
    report = {}
    for cls, idxs in by_class.items():
        if cls == 'outline':
            continue
        if cls == 'spark':
            target = water_ramp
            report[cls] = 'fixed water ramp'
        else:
            donor_l = [lum(pal[i]) for i in idxs for _ in range(used[i])]
            target = quantile_target(donor_l, samples[source[cls]])
            report[cls] = f'{len(samples[source[cls]])} {source[cls]} samples'
        for i in idxs:
            rgb = target(lum(pal[i]))
            lut[i] = min((j for j in range(255) if j not in CYCLING),
                         key=lambda j: sum((qpal[j][k] - rgb[k]) ** 2
                                           for k in range(3)))
    return lut, report


def water_ramp(l):
    """Pale blue-green water, darker for darker donor pixels."""
    t = max(0.0, min(1.0, l / 255))
    return (90 + 140 * t, 140 + 110 * t, 150 + 105 * t)


def apply_lut(fr, lut):
    if not fr:
        return fr
    return dict(fr, pixels=[p if p == 255 else lut[p] for p in fr['pixels']])


# ---------------------------------------------------------------------------
# Harpie: sheet sequencing
# ---------------------------------------------------------------------------

def body_centre_x(img):
    """x of the alpha centroid over the figure's middle rows, where the
    torso is and the wingtips mostly are not."""
    bb = img.getbbox()
    a = img.split()[3].load()
    y0 = bb[1] + (bb[3] - bb[1]) * 35 // 100
    y1 = bb[1] + (bb[3] - bb[1]) * 80 // 100
    xs = [x for y in range(y0, y1) for x in range(bb[0], bb[2]) if a[x, y]]
    return sum(xs) / len(xs) if xs else (bb[0] + bb[2]) / 2


def harpie_factor(cand):
    """One scale for every harpie image of a candidate: the wings-up WALK
    key pose becomes HARPIE_UP_H tall."""
    up = keyed(piece_paths(os.path.join(HDIR, f'keys_{cand}'), POSES)[1])
    bb = up.getbbox()
    return HARPIE_UP_H / (bb[3] - bb[1])


def harpie_walk_frames(cand, d, donor_frs):
    """The 7 walk frames of one drawn direction, as frame dicts."""
    return harpie_sheet_frames(cand, 'walk', d, PHASES, HARPIE_CYCLE,
                               donor_frs[TORAX_WALK[d]])


def harpie_sheet_frames(cand, kind, d, names, seq, donor, hovers=None):
    """One generated sheet -> the donor action's frames for direction d.
    `seq` is [(phase, body bob in px, up negative)], one per frame; `hovers`
    the talons' height off the ground per phase (default HARPIE_HOVER)."""
    stem = os.path.join(HDIR, f'{kind}_{cand}_d{d}')
    pieces = [keyed(p) for p in piece_paths(stem, names)]
    # One factor per sheet, never per figure (that would make the body pulse
    # through the cycle): the sheet's tallest figure, the wings-up phase,
    # is scaled to HARPIE_UP_H like the key sheet's wings-up WALK pose.
    tallest = max(p.getbbox()[3] - p.getbbox()[1] for p in pieces)
    factor = HARPIE_UP_H / tallest
    smalls = [to_game(p, factor) for p in pieces]
    # Common frame of reference: the sheet's rows are shared (split keeps
    # the full height), so the ground line is the lowest talon of any phase.
    ground = max(s.getbbox()[3] for s in smalls)
    # The donor's anchor relative to its body: feet below it, and its column
    # against the body's centre (an actor's anchor is a footpad corner, not
    # the middle of the sprite).
    dfeet = donor['height'] - donor['yoff']
    dcol = donor['xoff'] - body_centre_x(frame_rgba(donor))
    hovers = hovers or [HARPIE_HOVER] * len(names)
    out = []
    for phase, bob in seq:
        s = smalls[phase]
        bb = s.getbbox()
        fig = s.crop(bb)
        cx = body_centre_x(s) - bb[0]
        # the sheet's ground hovers[phase] px below the talons; a negative
        # bob lifts the body, i.e. moves the figure's top further from the
        # anchor. Each figure keeps its own height above the sheet's ground.
        xoff = round(cx + dcol)
        yoff = (ground - bb[1]) - dfeet + hovers[phase] - bob
        out.append(rgba_to_frame(fig, xoff, yoff))
    return out


# The torax's attack (action 7, 7 frames, hit window 3-5) and death (action
# 14, 8 frames) from five generated phases each (gen_monsters.sh). The
# strike, phase 3, is drawn on frames 3 and 4, the peak of the hit window.
TORAX_ATTACK = {7: 80, 3: 120, 4: 130, 5: 140, 6: 150}
ATTACK_SEQ = ((0, 0), (1, -1), (2, 0), (3, 0), (3, 0), (2, 0), (4, 0))
# Death: two views, 211-218 drawn for direction 3 and 231-238 for 7 (the
# donor's own split; ANIM.DAT mirrors and reuses them for the rest). The
# harpie falls: the talons start at the hover height and reach the ground
# by the landing. standUp plays these backwards.
TORAX_DIE = {3: 211, 7: 231}
DIE_SEQ = ((0, 0), (1, 0), (1, 0), (2, 0), (2, 0), (3, 0), (4, 0), (4, 0))
DIE_HOVER = (HARPIE_HOVER, 4, 2, 0, 0)


def harpie_frames(cand):
    """The harpie's whole torax-layout frame list (240; None = undrawn)."""
    tx = frames_of(TORAX)
    frames = [None] * len(tx)
    for d, f0 in TORAX_WALK.items():
        for k, fr in enumerate(harpie_walk_frames(cand, d, tx)):
            frames[f0 + k] = fr
    for d, f0 in TORAX_ATTACK.items():
        for k, fr in enumerate(harpie_sheet_frames(
                cand, 'attack', d, ATTACK_PHASES, ATTACK_SEQ, tx[f0])):
            frames[f0 + k] = fr
    for d, f0 in TORAX_DIE.items():
        for k, fr in enumerate(harpie_sheet_frames(
                cand, 'die', d, DIE_PHASES, DIE_SEQ, tx[f0], DIE_HOVER)):
            frames[f0 + k] = fr
    return frames


def harpie_key_frames(cand):
    f = harpie_factor(cand)
    out = []
    for path in piece_paths(os.path.join(HDIR, f'keys_{cand}'), POSES):
        s = to_game(keyed(path), f)
        fig = s.crop(s.getbbox())
        out.append(rgba_to_frame(fig, fig.width // 2, fig.height))
    return out


def zombie_key_frames(cand):
    f = zombie_factor(cand)
    out = []
    for path in piece_paths(os.path.join(ZDIR, f'keys_{cand}'), POSES):
        s = to_game(keyed(path), f)
        fig = s.crop(s.getbbox())
        out.append(rgba_to_frame(fig, fig.width // 2, fig.height))
    return out


# ---------------------------------------------------------------------------
# Plates
# ---------------------------------------------------------------------------

BG = (52, 60, 52)


def paste_frame(canvas, fr, ax, ay, flip=False):
    img = frame_rgba(fr)
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        canvas.paste(img, (ax - (fr['width'] - 1 - fr['xoff']), ay - fr['yoff']),
                     img)
    else:
        canvas.paste(img, (ax - fr['xoff'], ay - fr['yoff']), img)


def row_plate(rows, scale, title, gap=10, label_w=150):
    """rows: [(label, [frame dicts])]. Frames bottom-aligned on their
    anchors in fixed cells."""
    cw = max(max(f['width'] for f in fs) for _, fs in rows) + gap
    ch = max(max(f['height'] for f in fs) for _, fs in rows) + gap
    ncol = max(len(fs) for _, fs in rows)
    W, H = label_w + ncol * cw, 18 + len(rows) * (ch + 12)
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((4, 2), title, fill=(240, 220, 120))
    for r, (label, fs) in enumerate(rows):
        y = 18 + r * (ch + 12)
        d.text((4, y + ch // 2), label, fill=(230, 230, 230))
        for c, fr in enumerate(fs):
            ax = label_w + c * cw + cw // 2
            paste_frame(im, fr, ax - (fr['width'] // 2 - fr['xoff']),
                        y + ch - 4 - (fr['height'] - fr['yoff']))
    return im.resize((W * scale, H * scale), Image.NEAREST) if scale != 1 else im


def stack(images, pad=8, bg=(24, 24, 30)):
    W = max(i.width for i in images)
    H = sum(i.height for i in images) + pad * (len(images) + 1)
    out = Image.new('RGB', (W + 2 * pad, H), bg)
    y = pad
    for i in images:
        out.paste(i, (pad, y))
        y += i.height + pad
    return out


def ring_positions(cell):
    """Screen layout of the 8 directions, as the camera sees them: dir 7
    (NW) faces up the screen, 3 (SE) faces the viewer."""
    return {7: (1, 0), 0: (2, 0), 1: (2, 1), 2: (2, 2), 3: (1, 2),
            4: (0, 2), 5: (0, 1), 6: (0, 0)}


def walk_ring(dir_frames, t, cell, flips):
    """One animation tick: all 8 directions in a 3x3 ring."""
    im = Image.new('RGB', (cell * 3, cell * 3), BG)
    for d, (cx, cy) in ring_positions(cell).items():
        fs = dir_frames[d]
        fr = fs[t % len(fs)]
        paste_frame(im, fr, cx * cell + cell // 2, cy * cell + cell - 10,
                    flip=flips[d])
    return im


def walk_gif(path, panels, ticks, delay_ms, scale):
    """panels: [(label, dir_frames, flips)] side by side, looping."""
    frames = []
    for t in range(ticks):
        imgs = [walk_ring(df, t, 96, fl) for _, df, fl in panels]
        W = sum(i.width for i in imgs) + 8 * (len(imgs) - 1)
        im = Image.new('RGB', (W, imgs[0].height + 14), (24, 24, 30))
        x = 0
        for (label, _, _), i in zip(panels, imgs):
            im.paste(i, (x, 14))
            ImageDraw.Draw(im).text((x + 4, 1), label, fill=(240, 220, 120))
            x += i.width + 8
        frames.append(im.resize((im.width * scale, im.height * scale),
                                Image.NEAREST))
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=delay_ms, loop=0, optimize=False)
    # the first tick as a still, for viewers that do not animate
    frames[0].save(path.replace('.gif', '-still.png'))


def scene(mapnum, centre, radius, figures, flx_path, scale):
    """Render a window of the LV map with `figures` (MapItems) added, from
    the scratch FLX. The renderer is iso_render's painter (depth sort by
    x+y, z); water draws in its static palette (no cycling)."""
    from map_preview import GlobReader, expand_globs
    from iso_render import IsoRenderer
    from item_sorter import _FrameTable
    import importlib
    key = f'map{mapnum}'
    if key not in _cache:
        mod = importlib.import_module(f'build_map_{mapnum:02d}')
        with contextlib.redirect_stdout(io.StringIO()):
            _cache[key] = expand_globs(
                getattr(mod, f'build_map_{mapnum:02d}')(), GlobReader())
    items = _cache[key]
    cx, cy = centre
    win = [i for i in items if abs(i.x - cx) <= radius and abs(i.y - cy) <= radius]
    r = IsoRenderer(flx_path)
    # parse_shape_frames refuses >500 frames; the Avatar has 1,550
    r._frames_cache[AVATAR] = _FrameTable(read_flx_entry(r.flx, AVATAR))
    return r.render(win + figures, scale=scale)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def magenta_strip(shape, idxs, gap=24, scale=8):
    """Donor frames in a row on flat magenta, anchors on one line, at 8x:
    the form every reference on the track is handed to the generator in."""
    frs = frames_of(shape)
    sel = [frs[i] for i in idxs]
    L = max(f['xoff'] for f in sel)
    R = max(f['width'] - f['xoff'] for f in sel)
    T = max(f['yoff'] for f in sel)
    B = max(f['height'] - f['yoff'] for f in sel)
    cw = L + R + gap
    im = Image.new('RGB', (cw * len(sel) + gap, T + B + 2 * gap), MAGENTA)
    for k, f in enumerate(sel):
        paste_frame(im, f, gap + k * cw + L, gap + T)
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


def cmd_refs(dest=None):
    """The generator's references: the ghoul's four key poses facing the
    viewer, and one ghoul walk frame per drawn direction (the harpie's
    facing cue for each walk sheet)."""
    zd, hd = (dest, dest) if dest else (ZDIR, HDIR)
    os.makedirs(zd, exist_ok=True)
    os.makedirs(hd, exist_ok=True)
    out = os.path.join(zd, 'reference-ghoul-dir3.png')
    magenta_strip(GHOUL, [ZOMBIE_KEY_FRAMES[p] for p in POSES]).save(out)
    print(f'wrote {out}')
    for d, f0 in GHOUL_WALK.items():
        out = os.path.join(hd, f'reference-facing-d{d}.png')
        magenta_strip(GHOUL, [f0]).save(out)
        print(f'wrote {out}')


def avatar_frame():
    from item_sorter import _FrameTable
    flx = open(BUILT_SHAPES if os.path.exists(BUILT_SHAPES) else BASE_SHAPES,
               'rb').read()
    return _FrameTable(read_flx_entry(flx, AVATAR))[0]


def cmd_keys():
    av = avatar_frame()
    gh = frames_of(GHOUL)
    tx = frames_of(TORAX)
    for what, d, donor, keyfr, make in (
            ('water-zombie', ZDIR, gh, ZOMBIE_KEY_FRAMES, zombie_key_frames),
            ('harpie', HDIR, tx, TORAX_KEY_FRAMES, harpie_key_frames)):
        rows = [('placeholder ' + ('142 ghoul' if donor is gh else '120 torax'),
                 [donor[keyfr[p]] for p in POSES] + [av])]
        for c in 'ABC':
            if not os.path.exists(piece_paths(os.path.join(d, f'keys_{c}'),
                                              POSES)[0]):
                continue
            fs = make(c)
            sid = WATER_ZOMBIE if d == ZDIR else HARPIE
            back, _ = through_pipeline(sid, fs, f'{what}-keys-{c}')
            rows.append((f'candidate {c}', list(back) + [av]))
        if what == 'water-zombie':
            # what the ramp transfer makes of the donor's own key frames
            for c in 'ABC':
                if os.path.exists(piece_paths(os.path.join(d, f'keys_{c}'),
                                              POSES)[0]):
                    lut, _ = build_lut(c)
                    rows.append((f'{c} derived (LUT)',
                                 [apply_lut(gh[keyfr[p]], lut) for p in POSES]
                                 + [av]))
        title = (f'{what}: key poses idle/walk/attack/dead + the Avatar, '
                 f'read back from the FLX at {WATER_ZOMBIE if d == ZDIR else HARPIE}')
        for s in (1, 4):
            out = os.path.join(d, f'keys-plate-{s}x.png')
            row_plate(rows, s, title).save(out)
            print(f'wrote {os.path.relpath(out, ROOT)}')


def cmd_zombie(cand):
    lut, report = build_lut(cand)
    print(f'  LUT for candidate {cand}: {report}')
    gh = frames_of(GHOUL)
    walk, rep = anim_walk(GHOUL)
    derived = [apply_lut(f, lut) for f in gh]
    # The sample: the walk's 40 drawn frames recoloured, every other frame
    # left blank, so the read-back shape has the donor's 451-frame layout.
    sample = [None] * len(gh)
    for d, f0 in GHOUL_WALK.items():
        for k in range(8):
            sample[f0 + k] = derived[f0 + k]
    back, flx_path = through_pipeline(WATER_ZOMBIE, sample,
                                      f'water-zombie-walk-{cand}')
    dir_new = {d: [back[f] for f, _ in walk[d][:-1]] for d in range(8)}
    dir_old = {d: [gh[f] for f, _ in walk[d][:-1]] for d in range(8)}
    flips = {d: walk[d][0][1] for d in range(8)}
    rows = []
    for d in range(8):
        f = mirror if flips[d] else (lambda x: x)
        rows.append((f'dir {d} ghoul' + (' (flip)' if flips[d] else ''),
                     [f(x) for x in dir_old[d]]))
        rows.append((f'dir {d} water zombie {cand}', [f(x) for x in dir_new[d]]))
    for s in (1, 3):
        out = os.path.join(ZDIR, f'walk-{cand}-{s}x.png')
        row_plate(rows, s, f'water zombie {cand}: walk, 8 directions, '
                  f'read back from shape {WATER_ZOMBIE} (5 drawn + 3 mirrored)'
                  ).save(out)
        print(f'wrote {os.path.relpath(out, ROOT)}')
    gif = os.path.join(ZDIR, f'walk-{cand}.gif')
    walk_gif(gif, [('placeholder 142', dir_old, flips),
                   (f'water zombie {cand}', dir_new, flips)],
             8, round(rep * 1000 / 30), 3)
    print(f'wrote {os.path.relpath(gif, ROOT)}')
    # The whole set costs nothing more, so it is shown too: every drawn
    # frame of the ghoul through the same table, read back from 872.
    full, _ = through_pipeline(WATER_ZOMBIE, derived, f'water-zombie-all-{cand}')
    drawn = [i for i, f in enumerate(gh)
             if f and any(p != 255 for p in f['pixels'])]
    rows = [(f'frames {drawn[k]}-{drawn[min(k + 14, len(drawn)) - 1]}',
             [full[i] for i in drawn[k:k + 14]])
            for k in range(0, len(drawn), 14)]
    out = os.path.join(ZDIR, f'allframes-{cand}-2x.png')
    row_plate(rows, 2, f'water zombie {cand}: all {len(drawn)} drawn frames '
              f'of the ghoul through the table, read back from {WATER_ZOMBIE}'
              ).save(out)
    print(f'wrote {os.path.relpath(out, ROOT)}')
    from u8_map import MapItem
    # Map 10, the pier between the zombie eggs at (12800,19456) and
    # (14592,19200): the placeholder, the new one and the Avatar, 1x.
    figs = [MapItem(x=13900, y=18950, z=8, shape=GHOUL, frame=40),
            MapItem(x=13900, y=19250, z=8, shape=WATER_ZOMBIE, frame=40),
            MapItem(x=13770, y=19500, z=8, shape=AVATAR, frame=0)]
    for s in (1, 2):
        out = os.path.join(ZDIR, f'scene-map10-{cand}-{s}x.png')
        scene(10, (13850, 19150), 700, figs, flx_path, s).save(out)
        print(f'wrote {os.path.relpath(out, ROOT)} (placeholder, new, Avatar)')


def mirror(fr):
    w = fr['width']
    px = fr['pixels']
    rows = [px[y * w:(y + 1) * w][::-1] for y in range(fr['height'])]
    return dict(fr, pixels=[p for r in rows for p in r], xoff=w - 1 - fr['xoff'])


def cmd_harpie(cand):
    """The whole harpie: every ANIM.DAT-referenced torax frame drawn, read
    back from 873, plated per action beside the torax, and written as the
    build input (indexed PNGs + anchors) lv_monsters.py injects."""
    tx = frames_of(TORAX)
    frames = harpie_frames(cand)
    back, flx_path = through_pipeline(HARPIE, frames, f'harpie-{cand}')
    write_build_input(cand, back, frames)
    for action, label in ((0, 'walk (flap)'), (7, 'attack'), (14, 'die')):
        seqs, rep = anim_action(TORAX, action)
        dir_new = {d: [back[f] for f, _ in seqs[d]] for d in range(8)}
        dir_old = {d: [tx[f] for f, _ in seqs[d]] for d in range(8)}
        flips = {d: seqs[d][0][1] for d in range(8)}
        rows = []
        for d in range(8):
            f = mirror if flips[d] else (lambda x: x)
            rows.append((f'dir {d} torax' + (' (flip)' if flips[d] else ''),
                         [f(x) for x in dir_old[d]]))
            rows.append((f'dir {d} harpie {cand}', [f(x) for x in dir_new[d]]))
        name = label.split()[0]
        for s in (1, 3):
            out = os.path.join(HDIR, f'{name}-{cand}-{s}x.png')
            row_plate(rows, s, f'harpie {cand}: {label}, 8 directions, read '
                      f'back from shape {HARPIE}').save(out)
            print(f'wrote {os.path.relpath(out, ROOT)}')
        gif = os.path.join(HDIR, f'{name}-{cand}.gif')
        walk_gif(gif, [(f'placeholder 120', dir_old, flips),
                       (f'harpie {cand}', dir_new, flips)],
                 len(seqs[3]), round(max(rep, 1) * 1000 / 30), 3)
        print(f'wrote {os.path.relpath(gif, ROOT)}')
    from u8_map import MapItem
    # Map 13, the climb path through the harpie zone, between the eggs
    # (build_map_13.py:595-601) and the summit: placeholder, new, Avatar.
    figs = [MapItem(x=3990, y=1400, z=116, shape=TORAX, frame=40),
            MapItem(x=3990, y=1600, z=116, shape=HARPIE, frame=40),
            MapItem(x=3990, y=1800, z=112, shape=AVATAR, frame=0)]
    for s in (1, 2):
        out = os.path.join(HDIR, f'scene-map13-{cand}-{s}x.png')
        scene(13, (3968, 1560), 420, figs, flx_path, s).save(out)
        print(f'wrote {os.path.relpath(out, ROOT)} (placeholder, new, Avatar)')


def anim_action(shape, action):
    """ANIM.DAT `action` for a shape: ({dir: [(frame, flipped)...]}, repeat),
    the action's last frame dropped when it repeats the first (a loop)."""
    with contextlib.redirect_stdout(io.StringIO()):
        data = open(pristine_base(BASE_ANIM, None, 'base ANIM.DAT'), 'rb').read()
    off = struct.unpack_from('<I', data, 4 * shape)[0]
    ao = struct.unpack_from('<I', data, off + 4 * action)[0]
    size, rep = data[ao], data[ao + 2]
    p, out = ao + 4, {}
    for d in range(8):
        seq = []
        for _ in range(size):
            b = data[p:p + 6]
            p += 6
            seq.append((b[0] + ((b[1] & 7) << 8), bool(b[5] & 0x20)))
        if len(seq) > 1 and seq[-1][0] == seq[0][0]:
            seq = seq[:-1]
        out[d] = seq
    return out, rep


def build_dir(cand):
    return os.path.join(HDIR, f'frames-{cand}')


def write_build_input(cand, back, frames):
    """The harpie's build input: one palette-indexed PNG per drawn frame
    (pixel = U8PAL index, 255 transparent, so nothing is re-quantized at
    build time) and anchors.json {frame: [xoff, yoff]}. These are the
    frames READ BACK from the scratch FLX, so the builder injects exactly
    what the plates show."""
    import json
    d = build_dir(cand)
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    flat = [c for rgb in palette() for c in rgb]
    anchors = {}
    for i, fr in enumerate(frames):
        if fr is None:
            continue
        b = back[i]
        im = Image.frombytes('P', (b['width'], b['height']), bytes(b['pixels']))
        im.putpalette(flat)
        im.save(os.path.join(d, f'{i:03d}.png'), transparency=255)
        anchors[str(i)] = [b['xoff'], b['yoff']]
    with open(os.path.join(d, 'anchors.json'), 'w') as f:
        json.dump({'shape': HARPIE, 'frames': len(frames), 'anchors': anchors},
                  f, indent=0, sort_keys=True)
    print(f'wrote {os.path.relpath(d, ROOT)}/: {len(anchors)} frames + '
          f'anchors.json')


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    cmd = argv[0]
    if cmd == 'refs':
        cmd_refs(argv[1] if len(argv) > 1 else None)
    elif cmd == 'split':
        split_all()
    elif cmd == 'keys':
        cmd_keys()
    elif cmd == 'zombie':
        cmd_zombie(argv[1])
    elif cmd == 'harpie':
        cmd_harpie(argv[1])
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])

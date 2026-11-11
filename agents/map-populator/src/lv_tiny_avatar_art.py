#!/usr/bin/env python3
"""
lv_tiny_avatar_art.py — derive the Tiny Tar body (shape 867) from the Avatar.

Art-track item 8, contract 8 in docs/art-track.md. Douglas, 2026-10-11: the
shrunken Avatar is the Avatar scaled down, made by code from shape 1's own
sprites and driven by shape 1's own animation table, plus a generated shrink
ramp. This module is the derivation; lv_tiny_avatar.py (build step 6/8) is
the step that injects it, and tools/art/tiny_avatar_plates.py renders the
candidates for review.

THE LAYOUT IS SHAPE 1's, WITH ONE COLLISION MOVED
-------------------------------------------------
867 carries all 1550 frames of shape 1, each scaled by the same factor, so
every action the full-size Avatar has (walk, run, jump, climb, combat,
casting, kneel, look, get-up, edge-balance, die ...) has its tiny frames at
the same numbers. Frames 60-69 are the exception. FREE.UNK's makeAvatarTiny()
and makeAvatarBig() (lv-patched/FREE.UNK:1397-1489) drive the shrink by
setFrame(60..69) on shape 867, and in shape 1's layout 60-67 are walk
direction 5 (south-west). So:

  frames 60-69     the shrink ramp (60 = full size, 69 = tiny), SE-facing
  frames 1550-1557 shape 1's frames 60-67 scaled, i.e. tiny SW walk
  ANIM.DAT         867 gets its OWN action table, appended: a copy of
                   shape 1's with frame references 60-67 rewritten to
                   1550-1557 and every frame's deltaDir scaled by the stride
                   factor (cumulatively rounded per direction, so a cycle's
                   total travel scales exactly and the feet stay planted).

Shape 1's frames 68 and 69 are referenced by no action (the table only
reaches 60-67 in this range), so nothing else moves. The usecode is
unchanged: frame 60 is shape 1 frame 3 verbatim, so the setType(TypeTinytar)
swap is seamless, and frame 69 is exactly the tiny body's frame 3 (stand,
SE), which is what AS_STAND southeast shows next.

THE PICK (Douglas, 2026-10-11, from shared/docs/art-poc/tiny-avatar/)
---------------------------------------------------------------------
O60 (the outline method at 0.6), the R2 ramp (the pale-blue glow), and a
stride that scales with the body. SCALE, METHOD, GLOW and STRIDE below;
build_tiny_avatar() is what build step 6/8 (lv_tiny_avatar.py) injects.

Usage (library):
    from lv_tiny_avatar_art import build_tiny_avatar
"""

import math
import struct

import numpy as np

from shape_viewer import _parse_one_frame
from lv_wood_wall import encode_frame, encode_shape_blobs

AVATAR_SHAPE = 1
TINY_SHAPE = 867
RAMP_FIRST, RAMP_LAST = 60, 69          # FREE.UNK makeAvatarTiny / makeAvatarBig
RAMP_LEN = RAMP_LAST - RAMP_FIRST + 1
# The frame the ramp is made of. makeAvatarTiny turns the Avatar to face
# southeast before setFrame(60); makeAvatarBig ends on shape 1 setFrame(3).
# Shape 1's stand action (2) is frame 0+dir, so 3 is stand, south-east.
RAMP_SOURCE_FRAME = 3
OUTLINE_INDEX = 0                       # every edge pixel of shape 1 frame 3
TRANSPARENT = 0xFF
FRAME_KEYS = ('width', 'height', 'xoff', 'yoff', 'pixels')

METHODS = ('nearest', 'area', 'outline')

SCALE = 0.6             # the child's height over the Avatar's (contract 8)
METHOD = 'outline'
GLOW = 0.4              # R2: the ramp's peak tint toward GLOW_RGB
STRIDE = SCALE          # deltaDir scale: the feet stay planted

# ANIM.DAT (AnimDat::load, gfx/anim_dat.cpp:149-280, U8 branch).
ANIM_SHAPES = 2048
ANIM_ACTIONS = 64
ANIM_DIRS = 8
ANIM_FRAME_BYTES = 6


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def decode_frame(blob, i):
    """Frame i of a shape blob, as a frame dict with FRAME_KEYS (the
    shape_viewer dict without its 'compressed' flag)."""
    ent = 6 + 6 * i
    off = struct.unpack_from('<I', blob, ent)[0] & 0xFFFFFF
    size = struct.unpack_from('<H', blob, ent + 4)[0]
    f = _parse_one_frame(blob, off, size)
    if f is None:
        raise ValueError(f"frame {i} does not decode")
    return {k: f[k] for k in FRAME_KEYS}


def decode_frames(blob):
    """Every frame of a shape blob. Unlike shape_viewer.parse_shape_frames
    this has no 500-frame cap: shape 1 has 1550."""
    return [decode_frame(blob, i)
            for i in range(struct.unpack_from('<H', blob, 4)[0])]


def _arr(frame):
    return np.array(frame['pixels'], dtype=np.uint8).reshape(
        frame['height'], frame['width'])


def _frame(a, xoff, yoff):
    """numpy index array + anchor -> frame dict, trimmed to its opaque
    bounding box. An empty frame is 1x1 transparent at (0, 0), as shape 1's
    own empty frames are."""
    rows = np.where((a != TRANSPARENT).any(axis=1))[0]
    cols = np.where((a != TRANSPARENT).any(axis=0))[0]
    if not len(rows):
        return {'width': 1, 'height': 1, 'xoff': 0, 'yoff': 0,
                'pixels': [TRANSPARENT]}
    r0, r1, c0, c1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
    a = a[r0:r1, c0:c1]
    return {'width': int(a.shape[1]), 'height': int(a.shape[0]),
            'xoff': int(xoff - c0), 'yoff': int(yoff - r0),
            'pixels': a.flatten().tolist()}


# The blending methods run in fixed point so the build is the same bytes on
# every machine. A float matmul goes to BLAS, whose summation order depends
# on the CPU's kernel (AVX2 vs AVX-512), and the canonical hash of
# U8SHAPES.FLX cannot depend on that. Weights are integers in units of
# 1/WFIX and linear-light colour in units of 1/LFIX, so every sum is an
# exact int64 (at most ~2^44 here) whatever order it is taken in. Only the
# final division, the tint blend and the sRGB conversion are float, all
# elementwise.
WFIX = 1 << 12
LFIX = 1 << 16


def _axis(n, off, s):
    """Anchor-aligned resampling along one axis. Source pixel i covers
    [i - off, i - off + 1) in anchor coordinates (the engine pastes a frame
    with its offset subtracted); output pixel U covers [U/s, (U+1)/s).
    Returns (first U, int64 weights[out, in], each the fraction of output
    pixel U that source pixel i covers, in units of 1/WFIX; nearest source
    index per output pixel or -1)."""
    u0 = math.floor(-off * s)
    u1 = math.ceil((n - off) * s)
    m = u1 - u0
    w = np.zeros((m, n), dtype=np.int64)
    near = np.full(m, -1)
    for k in range(m):
        lo, hi = (u0 + k) / s, (u0 + k + 1) / s
        i0, i1 = max(0, math.floor(lo + off)), min(n, math.ceil(hi + off))
        for i in range(i0, i1):
            ov = min(hi, i - off + 1) - max(lo, i - off)
            if ov > 0:
                w[k, i] = round(ov * s * WFIX)
        c = math.floor((u0 + k + 0.5) / s + off)
        if 0 <= c < n:
            near[k] = c
    return u0, w, near


def _to_lin(rgb):
    c = rgb / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _to_srgb(lin):
    c = np.clip(lin, 0, 1)
    return 255.0 * np.where(c <= 0.0031308, c * 12.92,
                            1.055 * c ** (1 / 2.4) - 0.055)


class Quantizer:
    """Nearest palette entry (Euclidean sRGB, png2shape's metric) over a
    fixed set of indices: by default the indices shape 1 itself uses, so a
    downscale can only produce colours the Avatar already wears. lin is
    the whole palette in linear light, as integers in units of 1/LFIX."""

    def __init__(self, palette, indices):
        self.idx = np.array(sorted(indices), dtype=np.int64)
        if not len(self.idx) or (self.idx == TRANSPARENT).any():
            raise ValueError("quantizer needs indices excluding 0xFF")
        self.rgb = np.array([palette[i] for i in self.idx], dtype=np.float64)
        self.lin = np.rint(_to_lin(np.array(palette, dtype=np.float64))
                           * LFIX).astype(np.int64)

    def __call__(self, srgb):
        # Spelled out rather than .sum(axis=-1), so the three-term sum has
        # one order.
        d = srgb[..., None, :] - self.rgb
        d = d[..., 0] * d[..., 0] + d[..., 1] * d[..., 1] + d[..., 2] * d[..., 2]
        return self.idx[d.argmin(axis=-1)]


def used_indices(frames):
    s = set()
    for f in frames:
        s.update(f['pixels'])
    s.discard(TRANSPARENT)
    return s


def scale_frame(frame, s, method, quant, tint=None):
    """Scale one frame by s about its anchor.

    nearest  point-sample the source index per output pixel. Exact palette,
             no blending; thin features (the 1 px outline, fingers, the
             sword-belt) drop in and out between frames.
    area     box-filter coverage and linear-light colour, opaque where
             coverage >= 0.5, colour re-quantized to the Avatar's own
             indices. Smooth, but the black outline averages into the edge
             colours and the figure loses its edge.
    outline  area, with the black outline treated as line work and not
             colour: colour averages only the non-outline pixels, a pixel
             that is mostly black source stays black (interior lines), and
             the new silhouette's edge is redrawn as index 0, one pixel, as
             every edge pixel of shape 1 is.

    tint (rgb, amount) blends the colour toward rgb before quantizing (the
    ramp's glow); it needs a quantizer that can reach that colour.
    """
    if method not in METHODS:
        raise ValueError(f"method {method!r} not in {METHODS}")
    a = _arr(frame)
    h, w = a.shape
    ux, wx, nx = _axis(w, frame['xoff'], s)
    uy, wy, ny = _axis(h, frame['yoff'], s)
    xoff, yoff = -ux, -uy

    if method == 'nearest':
        out = np.full((len(ny), len(nx)), TRANSPARENT, dtype=np.uint8)
        for r, sy in enumerate(ny):
            if sy < 0:
                continue
            for c, sx in enumerate(nx):
                if sx >= 0:
                    out[r, c] = a[sy, sx]
        if tint is not None:
            raise ValueError("tint needs a blending method")
        return _frame(out, xoff, yoff)

    opaque = (a != TRANSPARENT).astype(np.int64)
    lin = quant.lin[np.where(a == TRANSPARENT, 0, a)]
    if method == 'outline':
        colour = opaque * (a != OUTLINE_INDEX)
    else:
        colour = opaque
    wxt = np.ascontiguousarray(wx.T)
    cov = wy @ opaque @ wxt                 # units of 1/WFIX^2
    ccov = wy @ colour @ wxt
    acc = np.stack([wy @ (colour * lin[..., ch]) @ wxt for ch in range(3)],
                   axis=-1)
    with np.errstate(invalid='ignore', divide='ignore'):
        col = acc / (ccov[..., None] * float(LFIX))
    if tint is not None:
        rgb, amount = tint
        col = (1 - amount) * col + amount * _to_lin(np.array(rgb, float))
    solid = 2 * cov >= WFIX * WFIX
    idx = np.full(cov.shape, TRANSPARENT, dtype=np.uint8)
    have = solid & (ccov > 0)
    if have.any():
        idx[have] = quant(_to_srgb(col[have])).astype(np.uint8)
    if method == 'outline':
        idx[solid & (2 * ccov < cov)] = OUTLINE_INDEX
        pad = np.pad(solid, 1)
        inner = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
        idx[solid & ~inner] = OUTLINE_INDEX
    return _frame(idx, xoff, yoff)


# ---------------------------------------------------------------------------
# The shrink ramp and the whole shape
# ---------------------------------------------------------------------------

GLOW_RGB = (210, 235, 255)


def ramp_scales(s, n=RAMP_LEN):
    """Geometric: each step shrinks by the same ratio, so the shrink reads
    as a steady rate. ramp_scales(s)[0] == 1, [-1] == s."""
    return [s ** (k / (n - 1)) for k in range(n)]


def make_ramp(src, s, method, quant, glow=None, glow_quant=None):
    """Ten frames of the Avatar's own frame, full size down to s.

    Frame 0 is the source verbatim (the setType swap from shape 1 frame 3
    is pixel-identical) and the last is exactly scale_frame(src, s, method),
    the tiny body's own stand frame, so AS_STAND after the loop is
    seamless too. glow=peak amount tints the middle frames toward GLOW_RGB
    on a sine envelope (zero at both ends); it needs glow_quant, a
    quantizer over the whole palette, because the Avatar wears no pale
    blue."""
    scales = ramp_scales(s)
    out = [{k: src[k] for k in FRAME_KEYS}]
    for k in range(1, RAMP_LEN):
        amt = glow * math.sin(math.pi * k / (RAMP_LEN - 1)) if glow else 0
        if amt > 1e-9:
            m = 'area' if method == 'nearest' else method
            out.append(scale_frame(src, scales[k], m, glow_quant,
                                   tint=(GLOW_RGB, amt)))
        else:
            out.append(scale_frame(src, scales[k], method, quant))
    return out


def relocated_frames(anim):
    """Shape 1 frames inside 60-69 that its action table references, in
    order: the frames the ramp displaces, which build_frames appends past
    the end of the shape (1550 onward)."""
    return sorted({f for f in anim_frame_refs(anim, AVATAR_SHAPE)
                   if RAMP_FIRST <= f <= RAMP_LAST})


def build_frames(avatar_frames, s, method, quant, anim, glow=None,
                 glow_quant=None):
    """Shape 867's frame list: shape 1's frames scaled by s, the ramp at
    60-69, and the displaced frames appended. Returns (frames, relocate)
    with relocate = {old frame: new frame}."""
    frames = [scale_frame(f, s, method, quant) for f in avatar_frames]
    moved = relocated_frames(anim)
    relocate = {old: len(avatar_frames) + i for i, old in enumerate(moved)}
    frames.extend(frames[old] for old in moved)
    ramp = make_ramp(avatar_frames[RAMP_SOURCE_FRAME], s, method, quant,
                     glow=glow, glow_quant=glow_quant)
    frames[RAMP_FIRST:RAMP_LAST + 1] = ramp
    return frames, relocate


def encode(frames):
    """Frame dicts -> a U8 shape blob (lv_wood_wall's engine-exact
    encoder)."""
    return encode_shape_blobs([encode_frame(f['pixels'], f['width'],
                                            f['height'], f['xoff'],
                                            f['yoff']) for f in frames])


def build_tiny_avatar(avatar_blob, anim, palette):
    """The shipped body: shape 1's blob and the pristine ANIM.DAT in;
    (867's shape blob, its frame list, relocate, ANIM.DAT with 867's own
    table) out, at the pick (SCALE, METHOD, GLOW, STRIDE)."""
    avatar = decode_frames(avatar_blob)
    frames, relocate = build_frames(
        avatar, SCALE, METHOD, Quantizer(palette, used_indices(avatar)), anim,
        glow=GLOW, glow_quant=Quantizer(palette, range(TRANSPARENT)))
    return (encode(frames), frames, relocate,
            avatar_anim_table(anim, relocate, STRIDE))


# ---------------------------------------------------------------------------
# ANIM.DAT: 867's own action table
# ---------------------------------------------------------------------------

def anim_offset(data, shape):
    """Shape's entry in the 2048-entry offset table; 0 = no animation."""
    if not 0 <= shape < ANIM_SHAPES:
        raise ValueError(f"shape {shape} outside ANIM.DAT (0..{ANIM_SHAPES - 1})")
    return struct.unpack_from('<I', data, 4 * shape)[0]


def _actions(data, shape):
    """[(action, offset, size)] for each non-empty action of shape."""
    base = anim_offset(data, shape)
    if not base:
        raise ValueError(f"ANIM.DAT shape {shape} has no entry")
    out = []
    for a in range(ANIM_ACTIONS):
        ao = struct.unpack_from('<I', data, base + 4 * a)[0]
        if ao:
            out.append((a, ao, data[ao]))
    return out


def _frame_num(b0, b1):
    return b0 + ((b1 & 0x7) << 8)


def anim_frame_refs(data, shape):
    refs = []
    for _a, ao, size in _actions(data, shape):
        p = ao + 4
        for _ in range(ANIM_DIRS * size):
            refs.append(_frame_num(data[p], data[p + 1]))
            p += ANIM_FRAME_BYTES
    return refs


def _scaled_run(deltas, scale):
    """Cumulative rounding: the running total is rounded, not each step, so
    the sum of a direction's deltas is round(sum * scale) and no step
    changes sign."""
    out, acc, prev = [], 0, 0
    for d in deltas:
        acc += d
        r = int(math.floor(acc * scale + 0.5))
        out.append(r - prev)
        prev = r
    return out


def avatar_anim_table(data, relocate, stride_scale, src=AVATAR_SHAPE,
                      dst=TINY_SHAPE):
    """Return ANIM.DAT with shape dst given its own action table, appended
    at the end of the file: src's 64 actions with frame numbers remapped
    through relocate and deltaDir scaled by stride_scale. Headers (size,
    flags, frame repeat), deltaZ, sfx and frame flags are src's. Refuses an
    occupied dst."""
    if anim_offset(data, dst):
        raise ValueError(f"ANIM.DAT shape {dst} already has an entry")
    acts = _actions(data, src)
    table_at = len(data)
    table = bytearray(4 * ANIM_ACTIONS)
    blocks = bytearray()
    cursor = table_at + len(table)
    for a, ao, size in acts:
        block = bytearray(data[ao:ao + 4 + ANIM_DIRS * size * ANIM_FRAME_BYTES])
        for d in range(ANIM_DIRS):
            base = 4 + d * size * ANIM_FRAME_BYTES
            deltas = [struct.unpack_from('b', block, base + j * ANIM_FRAME_BYTES + 4)[0]
                      for j in range(size)]
            scaled = _scaled_run(deltas, stride_scale)
            for j in range(size):
                p = base + j * ANIM_FRAME_BYTES
                fr = _frame_num(block[p], block[p + 1])
                fr = relocate.get(fr, fr)
                if not 0 <= fr < 0x800:
                    raise ValueError(f"frame {fr} does not fit 11 bits")
                block[p] = fr & 0xFF
                block[p + 1] = (block[p + 1] & 0xF8) | (fr >> 8)
                if not -128 <= scaled[j] <= 127:
                    raise ValueError(f"deltaDir {scaled[j]} out of int8")
                struct.pack_into('b', block, p + 4, scaled[j])
        struct.pack_into('<I', table, 4 * a, cursor + len(blocks))
        blocks += block
    out = bytearray(data) + table + blocks
    struct.pack_into('<I', out, 4 * dst, table_at)
    return bytes(out)


def decode_anim(data, shape):
    """{action: (size, flags, repeat, [[(frame, dz, sfx, ddir, fflags)]*8])}
    decoded the way AnimDat::load does for U8."""
    out = {}
    for a, ao, size in _actions(data, shape):
        flags = data[ao + 1] | (data[ao + 3] << 8)
        rep = data[ao + 2]
        p, dirs = ao + 4, []
        for _d in range(ANIM_DIRS):
            fr = []
            for _j in range(size):
                b = data[p:p + ANIM_FRAME_BYTES]
                p += ANIM_FRAME_BYTES
                fr.append((_frame_num(b[0], b[1]),
                           struct.unpack('b', b[2:3])[0], b[3],
                           struct.unpack('b', b[4:5])[0],
                           b[5] + ((b[1] & 0xF8) << 8)))
            dirs.append(fr)
        out[a] = (size, flags, rep, dirs)
    return out

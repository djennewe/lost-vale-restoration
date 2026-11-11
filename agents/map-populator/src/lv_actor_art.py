#!/usr/bin/env python3
"""
lv_actor_art.py — the 1994 screenshots' actors, as whole frame sets.

WHY THIS EXISTS
---------------
Four published 1994 shots show actors no retail shape draws: the white-haired
Zealan elder in screen19's doorway and at screen20's campfire, the two
spear-carrying children beside him in screen20, and the Water Zombies of
screen02 and screen09 (docs/research/2026-10-16-screenshot-reconstruction.md;
the cut-outs are vignettes/art_registry.json 2041, 2042 and 2050). Douglas,
2026-10-25: draw them all, the shot's pose exact at the frame the shot shows,
the rest of the animation set drawn in the shots' style. Each is an actor
clone (lv_monsters.py builds it): the donor's TYPEFLAG row and ANIM.DAT
table, and these frames in the donor's frame layout, so every action the
table names draws.

NOTHING HERE IS COMMITTED ORIGIN ART. Every frame is derived at build time
from the pristine base shapes (base_input.pristine_base) plus the committed
1994 crops under shared/data/lv-1994-art/ and the rules below, the way
lv_monsters.py builds 872 and lv_tiny_tar.py 859.

THE ELDER (888, Atli): donor 190, Mythran. The 1994 elder IS Mythran's body
— the screen20 pose overlaps Mythran's stand/talk frames at IoU 0.83, the
screen19 pose his walk at 0.80, against 0.72 for any frame of 707, the
peasant Atli wore — with long white hair over a bald head, no belt and a
short cane. So: Mythran's 350 frames, his staff cut back to that cane
(ELDER_STAFF, _cane: nothing above the hand, the knob gone), his blue-grey
belt recoloured into the robe's own browns (ELDER_RECOLOUR), the bald crown
and long locks painted per drawn direction (_paint_hair; the front view
stamps screen20's own hair, aligned on each frame's head), and the two shot
poses in place: screen20's at frame 60 (stand facing SE, also the first
frame of that walk) and screen19's at 71, the middle of the SE talk
gesture 70-72 (talk_gesture: the cane hand held out, its cane drawn on
below the hand where the shot's Avatar hid it; 70 and 72 turn that forearm
about the elbow). Mythran's table names 35 frames his shape leaves blank;
they get drawn here so nothing vanishes: combatStand
(110/136/160/185/209) is that direction's stand, die and standUp
(108/133/158/183/208) the peasant 707's last death frame for the same
direction with its hair whitened, and the climb frames 90-102 (an NPC never
climbs) the east stand.

THE CHILDREN (889 dark-haired, 890 blond): donor 708, the child. The 1994
children wear a grey tunic over a black cloak and carry a spear; 708 wears
a brown dress. So: 708's 100 frames with the dress mapped onto the
screenshots' grey/black ramp by luminance (CHILD_DRESS) — light grey above
the waist, black below — the hair kept black or mapped onto the blond ramp
(CHILD_BLOND), no black outline (_unoutline), and a spear in the right hand
on every upright frame (_paint_spear: the grip at the hand found per frame,
the shot's 3-D angle projected per facing, each end in front of the body or
behind it as the facing puts it); the death frames drop it. The shot pose
is frame 1 (stand facing N, drawn mirrored for W: the shot's children face
up-left), each child's own.

THE WATER ZOMBIE (872): donor 142, the ghoul. The 1994 zombie is teal with
bright green slime and a dark green kilt; candidate A's remap made it
blue-grey. So: ZOMBIE_REMAP, each ghoul material (skin, loincloth, wounds,
shadows) quantile-matched by luminance onto the same material in the three
1994 poses, one table over all 451 frames (coherent by construction: the
ghoul's dithering and motion survive pixel for pixel); and the three poses
at their frames: screen02's front view at 40 (stand facing SE), screen02's
raised club at 81 (the NW attack's raise), screen09's lunge at 112 (the E
attack's first hit frame).

THE SHOT POSES are the registry PNG's palette indices verbatim, except that
an index the engine colour-cycles (1-14, gfx/cycle_process.cpp) becomes the
non-cycling entry of the same RGB (9 -> 28, 2 -> 144): the crops were cut
as nearest palette entry, and both are the shot's colour. Holes the cut
left inside a figure where the figure's colour happened to equal the ground
behind it are filled from the shot (POSE_HOLES).
"""

import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
REGISTRY = os.path.join(HERE, 'vignettes', 'art_registry.json')

from shape_viewer import load_palette, PALETTE_FILE     # noqa: E402

PAL = np.array(load_palette(PALETTE_FILE), dtype=int)
TRANSPARENT = 255
CYCLING = frozenset(range(1, 15))
NOT_A_SPRITE = ('reference-only', 'residual')


def _lum(i):
    r, g, b = PAL[i]
    return 0.299 * r + 0.587 * g + 0.114 * b


def cycling_twin(i):
    """The non-cycling palette entry with the same RGB as cycling index i."""
    for j in range(256):
        if j not in CYCLING and j != TRANSPARENT and (PAL[j] == PAL[i]).all():
            return j
    raise SystemExit(f"palette index {i} cycles and has no same-colour twin")


CYCLE_TWINS = {i: cycling_twin(i) for i in (2, 9)}


# ---------------------------------------------------------------------------
# frames as arrays
# ---------------------------------------------------------------------------

def arr(f):
    """A parse_shape_frames frame -> HxW uint8 array (255 transparent)."""
    if f['width'] * f['height'] == 0:
        return np.full((1, 1), TRANSPARENT, np.uint8)
    return np.array(f['pixels'], np.uint8).reshape(f['height'], f['width'])


def frame(a, xoff, yoff):
    """Array + anchor -> frame dict (the encode_frame/parse_shape_frames
    shape), trimmed to its opaque box with the anchor kept."""
    op = a != TRANSPARENT
    if not op.any():
        return dict(width=1, height=1, xoff=0, yoff=0, pixels=[TRANSPARENT])
    ys, xs = np.nonzero(op)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    a = a[y0:y1, x0:x1]
    return dict(width=int(a.shape[1]), height=int(a.shape[0]),
                xoff=int(xoff - x0), yoff=int(yoff - y0),
                pixels=[int(p) for p in a.flatten()])


def blank(f):
    return f['width'] * f['height'] <= 1 and all(
        p == TRANSPARENT for p in f['pixels'])


def recoloured(f, lut):
    return dict(f, pixels=[lut.get(p, p) for p in f['pixels']])


def mirrored(f):
    a = arr(f)[:, ::-1]
    return frame(a, f['width'] - 1 - f['xoff'], f['yoff'])


def paste(f, stamp, sx, sy):
    """Paint stamp's opaque pixels onto frame f with the stamp's (0,0) at
    frame coordinates (sx, sy), growing the canvas when the stamp reaches
    past it. Returns the new frame (anchor kept)."""
    a = arr(f)
    h, w = stamp.shape
    x0, y0 = min(0, sx), min(0, sy)
    x1, y1 = max(a.shape[1], sx + w), max(a.shape[0], sy + h)
    canvas = np.full((y1 - y0, x1 - x0), TRANSPARENT, np.uint8)
    canvas[-y0:-y0 + a.shape[0], -x0:-x0 + a.shape[1]] = a
    sub = canvas[sy - y0:sy - y0 + h, sx - x0:sx - x0 + w]
    op = stamp != TRANSPARENT
    sub[op] = stamp[op]
    return frame(canvas, f['xoff'] - x0, f['yoff'] - y0)


# ---------------------------------------------------------------------------
# the shot poses
# ---------------------------------------------------------------------------

def load_registry(path=REGISTRY):
    with open(path) as f:
        return json.load(f)


# Holes the registry cut left inside a figure, filled from the shot: (registry
# id, frame) -> {(x, y): palette index}. Each is a single pixel enclosed by
# the figure where the 1994 figure's colour equals the ground the replay
# paints behind it, so the difference cut could not see it (2026-10-25).
POSE_HOLES = {
    (2041, 1): {(15, 16): 211, (16, 17): 214, (22, 17): 217, (2, 18): 211,
                (6, 19): 174, (20, 19): 215},
    (2042, 0): {(11, 3): 214, (10, 16): 217, (11, 20): 218},
    (2042, 1): {(16, 6): 219, (7, 8): 174, (8, 8): 174, (12, 20): 215},
}


def shot_pose(registry, sid, fno):
    """(array, registry frame) of a 1994 cut-out: its U8PAL indices verbatim,
    cycling indices swapped for their same-colour twin, POSE_HOLES filled."""
    fr = registry['shapes'][str(sid)]['frames'][fno]
    if fr['grade'] in NOT_A_SPRITE:
        raise SystemExit(f"registry {sid}:{fno} is graded {fr['grade']}, "
                         f"not a sprite — never build it")
    im = Image.open(os.path.join(ROOT, fr['png']))
    if im.mode != 'P':
        raise SystemExit(f"{fr['png']} is {im.mode}, not palette-indexed")
    pal = im.getpalette()[:768]
    a = np.array(im, np.uint8)
    for i in set(np.unique(a).tolist()) - {TRANSPARENT}:
        if tuple(pal[3 * i:3 * i + 3]) != tuple(PAL[i]):
            raise SystemExit(f"{fr['png']}: index {i} is not U8PAL's colour")
    for i, j in CYCLE_TWINS.items():
        a[a == i] = j
    for (x, y), idx in POSE_HOLES.get((sid, fno), {}).items():
        if a[y, x] != TRANSPARENT:
            raise SystemExit(f"registry {sid}:{fno} ({x},{y}) is not a hole")
        a[y, x] = idx
    return a, fr


def pose_frame(registry, sid, fno, anchor, mirror=False):
    """A shot pose as a frame anchored at `anchor` (in the cut-out's own
    coordinates, before any mirroring)."""
    a, _ = shot_pose(registry, sid, fno)
    xoff, yoff = anchor
    if mirror:
        a = a[:, ::-1]
        xoff = a.shape[1] - 1 - xoff
    # frame() trims; a cut-out is already its opaque box.
    return frame(a, xoff, yoff)


# ---------------------------------------------------------------------------
# which direction each frame is drawn for
# ---------------------------------------------------------------------------

MIRROR_DIR = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0, 7: 7}


def drawn_directions(table, nframes):
    """{frame: the direction it is drawn facing} from a decoded ANIM.DAT table
    (lv_tiny_avatar_art.decode_anim): the direction that shows it unflipped,
    or the mirror of the one that shows it flipped."""
    seen = {}
    for _a, (_size, _flags, _rep, dirs) in table.items():
        for d, seq in enumerate(dirs):
            for fr, _dz, _sfx, _dd, fflags in seq:
                if fr < nframes:
                    seen.setdefault(fr, []).append(
                        MIRROR_DIR[d] if fflags & 0x20 else d)
    return {fr: max(set(ds), key=ds.count) for fr, ds in seen.items()}


def referenced(table):
    return sorted({fr for _a, (_s, _f, _r, dirs) in table.items()
                   for seq in dirs for fr, *_ in seq})


# ---------------------------------------------------------------------------
# the elder: Mythran (190) restyled
# ---------------------------------------------------------------------------

ELDER_DONOR = 190
ELDER_CORPSE_DONOR = 707

# Mythran's blue-grey belt, sash and staff head (240-253) and his blues
# (144-152) -> the robe's browns at the nearest luminance among those the
# two 1994 elder poses use (none of these indices is in either pose).
ELDER_RECOLOUR = {
    240: 178, 241: 178, 242: 179, 243: 205, 244: 206, 245: 207, 246: 209,
    247: 210, 248: 212, 249: 213, 250: 215, 251: 217, 252: 219, 253: 174,
    144: 178, 145: 178, 146: 179, 147: 180, 149: 210, 150: 211, 151: 213,
    152: 215,
}

# The skin and white of a head (Mythran's bald scalp, face and fringe).
HEAD_SKIN = frozenset({176, 200, 201, 202, 203, 204, 224, 225, 160, 32})
HEAD_WHITE = frozenset({48, 16, 17, 18, 19, 192, 193})


def _components(mask):
    H, W = mask.shape
    seen = np.zeros((H, W), bool)
    out = []
    for y in range(H):
        for x in range(W):
            if mask[y, x] and not seen[y, x]:
                seen[y, x] = True
                stack, pts = [(y, x)], []
                while stack:
                    cy, cx = stack.pop()
                    pts.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] \
                                    and not seen[ny, nx]:
                                seen[ny, nx] = True
                                stack.append((ny, nx))
                out.append(pts)
    return out


def head_box(a, frac=0.45):
    """(x0, y0, x1, y1) inclusive of the head: the largest connected patch of
    skin/white in the top `frac` of the figure (the staff and the hands are
    smaller or lower)."""
    op = a != TRANSPARENT
    rows = np.nonzero(op.any(1))[0]
    if not len(rows):
        return None
    lim = rows[0] + int((rows[-1] - rows[0]) * frac) + 1
    m = np.isin(a, list(HEAD_SKIN | HEAD_WHITE))
    m[lim:] = False
    cs = _components(m)
    if not cs:
        return None
    pts = max(cs, key=len)
    ys = [p[0] for p in pts]
    xs = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


# The white ramp down a lock: (core, edge) by how far down it is.
def _lock_colour(t, edge):
    if t < 0.5:
        return 17 if edge else 48
    if t < 0.8:
        return 20 if edge else 17
    return 22 if edge else 19


LOCK_LENGTH = {7: 11, 0: 10, 1: 10, 2: 10}


def _paint_hair(a, d):
    """Mythran's bald head under long white hair, facing d (7, 0, 1, 2; the
    front view 3 takes screen20's own hair, _front_hair). The crown: the top
    half of the head's skin turns white. The locks: from under the head's
    lowest white/skin pixel in each hair column, down over the robe —
    the whole head width behind (7, 0), the back three columns in profile
    (1, 2: they face right, so the back is on the left)."""
    a = a.copy()
    hb = head_box(a)
    if hb is None:
        return a
    x0, y0, x1, y1 = hb
    H, W = a.shape
    top = y0 + max(1, (y1 - y0 + 2) // 2)
    for y in range(y0, top):
        for x in range(x0, x1 + 1):
            if a[y, x] in HEAD_SKIN:
                a[y, x] = 48 if (x - x0) % 3 else 17
    cols = list(range(x0, x1 + 1)) if d in (7, 0) else list(range(x0, x0 + 3))
    n = len(cols)
    for k, x in enumerate(cols):
        head_px = [y for y in range(y0, y1 + 1)
                   if a[y, x] in HEAD_WHITE | HEAD_SKIN]
        start = (max(head_px) + 1) if head_px else y1 + 1
        length = LOCK_LENGTH[d] - (abs(k - n // 2) if d in (7, 0) else 0)
        for j in range(length):
            y = start + j
            if y >= H or a[y, x] == TRANSPARENT:
                break
            a[y, x] = _lock_colour(j / max(1, length), k in (0, n - 1))
    return a


# screen20's hair and face, the front view's stamp: the cut-out's rows 0-14,
# columns 9-20 (the head and both locks), only its hair greys/whites, face
# and the outline over the crown (rows 0-2) — the robe and Mythran's beard
# between the locks stay the frame's own. It is placed on each SE frame by
# its head's top centre against frame 60's, where the pose's own pixels sit
# at (+1, -2) of the cut-out (best mask overlap with Mythran's 60, IoU 0.83).
FRONT_STAMP_BOX = (9, 0, 21, 15)        # x0, y0, x1, y1 (exclusive)
FRONT_STAMP_KEEP = frozenset({48, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                              27, 28, 32, 192, 193}) | HEAD_SKIN
FRONT_POSE_AT_60 = (1, -2)


def front_stamp(pose):
    x0, y0, x1, y1 = FRONT_STAMP_BOX
    st = pose[y0:y1, x0:x1]
    keep = np.isin(st, list(FRONT_STAMP_KEEP))
    keep[:3] |= np.isin(st[:3], [0, 29, 30, 31])
    return np.where(keep, st, TRANSPARENT).astype(np.uint8)


def _front_hair(f, stamp, ref_head):
    a = arr(f)
    hb = head_box(a)
    if hb is None:
        return f
    cx = (hb[0] + hb[2]) // 2 - (ref_head[0] + ref_head[2]) // 2
    cy = hb[1] - ref_head[1]
    sx = FRONT_STAMP_BOX[0] + FRONT_POSE_AT_60[0] + cx
    sy = FRONT_STAMP_BOX[1] + FRONT_POSE_AT_60[1] + cy
    return paste(f, stamp, sx, sy)


def _corpse_hair(f):
    """707's corpse with its dark hair white: the largest patch of dark
    pixels inside the silhouette (not on its edge) is the head's hair."""
    a = arr(f)
    op = a != TRANSPARENT
    inner = np.zeros_like(op)
    inner[1:-1, 1:-1] = (op[1:-1, 1:-1] & op[:-2, 1:-1] & op[2:, 1:-1]
                         & op[1:-1, :-2] & op[1:-1, 2:])
    dark = np.isin(a, [0, 29, 30, 31, 253, 252, 9, 27, 26]) & inner
    cs = _components(dark)
    if cs:
        for y, x in max(cs, key=len):
            a[y, x] = 48 if (x + y) % 3 else 17
    return frame(a, f['xoff'], f['yoff'])


# Blank frames of Mythran's table, drawn: {frame: ('stand' | 'corpse', dir)}.
ELDER_COMBAT_STAND = {110: 7, 136: 0, 160: 1, 185: 2, 209: 3}
ELDER_DIE = {108: 7, 133: 0, 158: 1, 183: 2, 208: 3}
ELDER_STAND = {7: 0, 0: 15, 1: 30, 2: 45, 3: 60}
CORPSE_707 = {7: 52, 0: 60, 1: 68, 2: 76, 3: 84}     # 707's last die frame

# The shot poses: (registry id, frame, target frame, anchor in the cut-out).
# Anchors put each pose where Mythran's frame it replaces draws its body
# (best mask overlap), so the feet stay put when the frame changes. The
# screen19 pose's best overlap is at x 14 (IoU 0.768 against 71); it sits
# one pixel left, at 13 (0.758), because from x 14 no world position at
# z 0 lands the pose on the shot's pixels (the C division per term leaves
# half the screen points of a z unreachable): at 13 the doorway's
# (19196,6944,0) does, exactly (vignettes/screen19.json).
ELDER_POSES = [
    (2041, 1, 60, (15, 42)),             # screen20, stand SE: 60 at (-1, +2)
    (2041, 0, 71, (13, 45)),             # screen19, SE talk (see above)
]

# The SE talk (Douglas, 2026-10-30, art review card 6: "give the SE talk
# some movement"). Mythran's talk table plays 70,71,72,70,71,70,71,72,71,70;
# all three were the screen19 pose, so he stood frozen. Now 71 is that pose
# and 70/72 are the same figure with his right forearm turned about the
# elbow: {frame: degrees, + raises the hand away from the body}. 70 draws
# the hand in a little, 72 lifts it and points the cane.
#
# The cane stays in that hand: screen20 holds it in the same right hand, and
# under screen19's hand the Avatar stands in front of him, so the shot
# shows nowhere it could be except behind the Avatar. ELDER_TALK_CANE draws
# it there: from just under the hand down and out to the ground, leaning
# away from the body as the outstretched arm puts it, two pixels wide in
# screen20's cane ramp (light core, dark outer edge), (x, y, index) in the
# cut-out's coordinates. Every one of its pixels is one the shot's Avatar
# (shape 1 frame 11, hotspot (130,124); the cut-out sits at (140,60))
# covers: the cane cannot pass under the hand itself, where the shot shows
# ground at (0..2, 28..30) and at the foot (rows 37-40, x 1-2), which is why
# it starts one pixel out from the hand and leans. So 71 keeps every
# cut-out pixel at the shot's index and adds only pixels the shot cannot
# see (vignette_replay screen19 --built: unchanged).
ELDER_TALK_SE = {70: -6, 71: 0, 72: 18}
ELDER_TALK_CANE = [
    (-1, 29, 216), (-2, 29, 31), (-1, 30, 216), (-2, 30, 31), (-2, 31, 216),
    (-3, 31, 175), (-2, 32, 217), (-3, 32, 175), (-3, 33, 218), (-4, 33, 174),
    (-3, 34, 219), (-4, 34, 174), (-4, 35, 219), (-5, 35, 175), (-5, 36, 219),
    (-6, 36, 174), (-5, 37, 217), (-6, 37, 174), (-6, 38, 217), (-7, 38, 175),
    (-6, 39, 175), (-7, 39, 174), (-7, 40, 175), (-8, 40, 31), (-7, 41, 174),
    (-8, 41, 31),
]
# What turns with the forearm ({row: (x0, x1)} of the forearm, hand and the
# hand's lowest pixels, in the cut-out; the cane turns too), the elbow it
# turns about (x, y), and the robe's left outline column the turned arm
# bares, per row (the robe edge runs from the elbow down to row 29's
# outline at x 4): bared pixels right of it take the robe two pixels
# further in, the column itself the outline, left of it transparent.
ELDER_FOREARM = {19: (3, 6), 20: (2, 6), 21: (2, 6), 22: (1, 6), 23: (1, 6),
                 24: (0, 5), 25: (0, 4), 26: (0, 4), 27: (0, 4), 28: (1, 3),
                 29: (1, 1), 31: (1, 3)}
ELDER_ELBOW = (6.5, 19.5)
ELDER_ROBE_EDGE = {19: 7, 20: 7, 21: 7, 22: 6, 23: 6, 24: 5, 25: 5, 26: 5,
                   27: 5, 28: 4, 29: 4, 30: 4, 31: 4}
TALK_PAD = 12


def talk_gesture(pose, anchor, degrees):
    """A frame of the SE talk: the screen19 cut-out with its cane, the
    forearm turned `degrees` about the elbow, anchored as the pose is."""
    p = TALK_PAD
    H, W = pose.shape
    c = np.full((H + p, W + p), TRANSPARENT, np.uint8)
    c[p:, p:] = pose
    turn = np.zeros(c.shape, bool)
    for y, (x0, x1) in ELDER_FOREARM.items():
        turn[y + p, x0 + p:x1 + p + 1] = pose[y, x0:x1 + 1] != TRANSPARENT
    for x, y, idx in ELDER_TALK_CANE:
        if c[y + p, x + p] != TRANSPARENT:
            raise SystemExit(f"ELDER_TALK_CANE ({x},{y}) is on the cut-out")
        c[y + p, x + p] = idx
        turn[y + p, x + p] = True
    out = c
    if degrees:
        out = c.copy()
        for y, x in zip(*np.nonzero(turn)):
            edge = ELDER_ROBE_EDGE.get(y - p)
            if edge is None or x - p < edge:
                out[y, x] = TRANSPARENT
            elif x - p == edge:
                out[y, x] = 29
            else:
                out[y, x] = c[y, x + 2] if not turn[y, x + 2] else c[y, x + 3]
        th = np.radians(degrees)
        cs, sn = np.cos(th), np.sin(th)
        px, py = ELDER_ELBOW[0] + p, ELDER_ELBOW[1] + p
        for y in range(c.shape[0]):
            for x in range(c.shape[1]):
                sx = int(round(cs * (x - px) + sn * (y - py) + px))
                sy = int(round(-sn * (x - px) + cs * (y - py) + py))
                if 0 <= sy < c.shape[0] and 0 <= sx < c.shape[1] \
                        and turn[sy, sx]:
                    out[y, x] = c[sy, sx]
    return frame(out, anchor[0] + p, anchor[1] + p)


# ---------------------------------------------------------------------------
# the elder's cane: Mythran's staff cut back to the 1994 short cane
# ---------------------------------------------------------------------------

# Douglas, 2026-10-30 (art review card 6): the 1994 elder carries a short
# cane that ends at his hand (screen20's cut-out, rows 22-40: from the hand
# down to the ground, 19 px, nothing above the hand), not Mythran's tall
# knobbed staff, which popped in whenever he left the screen20 pose. Every
# Mythran frame the table names is cut back by the same rule. The staff is a
# line from its knob end K through the grip G (the hand on it) to its other
# end F, given as (Kx, Ky, Gx, Gy, Fx, Fy, keep) in the donor frame's own
# pixels:
#   'F'  walk, stand, talk, cast: the staff from the hand up, knob and all,
#        goes; the cane is the staff from the hand down to the ground;
#   'K'  the attacks whose striking end is the knob end (the thrusts): the
#        part behind the hand goes; the cane is the staff from the hand
#        forward, the knob dropped.
# A walk's cane runs from the hand to the ground, 19-34 px (the screen20
# cane: 21); in the attacks (ELDER_ATTACK, Mythran's 50-px staff swung)
# it stops CANE_LEN px from the hand. The points were found (2026-10-30)
# by a line fit through each frame's thin protruding pixels and its knob
# (palette 240-253, 144-152), the grip at the skin pixels on that line,
# the attacks keeping whichever side shows more staff; 52, 53, 66, 67, 247
# and 253 were placed by hand. The frames are the donor's own: re-derive
# the table if the base art changes (test_lv_monsters checks the knob is
# gone).
CANE_LEN = 25
ELDER_ATTACK = range(230, 301)
STAFF_KNOB = frozenset(range(240, 254)) | frozenset(range(144, 153))
STAFF_HAND = frozenset({160, 33, 176, 177, 195, 196, 197, 200, 201, 202, 203,
                        204, 205, 224, 225})
OUTLINE = frozenset({0, 28, 29, 30, 31})
ELDER_STAFF = {
    0: (27,-1,28,14,29,38, 'F'), 1: (29,-1,28,15,27,40, 'F'),
    2: (29,-1,29,15,28,39, 'F'), 3: (29,-1,29,15,28,40, 'F'),
    4: (28,-1,28,16,28,40, 'F'), 5: (24,-1,25,15,28,41, 'F'),
    6: (22,-1,23,7,27,41, 'F'), 7: (20,-1,22,10,27,41, 'F'),
    8: (19,-1,22,13,26,35, 'F'), 9: (23,-1,24,12,27,34, 'F'),
    10: (26,-1,26,13,26,37, 'F'), 11: (27,-1,27,13,27,37, 'F'),
    15: (42,0,42,16,41,40, 'F'), 16: (44,-1,40,15,34,39, 'F'),
    17: (43,-1,41,15,38,39, 'F'), 18: (46,-1,43,14,39,38, 'F'),
    19: (43,-1,39,15,34,39, 'F'), 20: (38,-1,35,16,29,41, 'F'),
    21: (36,0,32,16,26,41, 'F'), 22: (35,-1,30,16,23,41, 'F'),
    23: (31,-1,33,14,38,38, 'F'), 24: (31,-1,35,14,40,37, 'F'),
    25: (38,0,38,15,37,40, 'F'), 26: (38,0,38,15,37,40, 'F'),
    27: (38,0,38,15,37,40, 'F'), 30: (34,5,32,20,30,43, 'F'),
    31: (36,3,32,18,25,40, 'F'), 32: (37,3,34,18,31,41, 'F'),
    33: (41,2,38,18,33,40, 'F'), 34: (39,2,34,18,26,40, 'F'),
    35: (35,3,29,18,18,41, 'F'), 36: (35,3,27,17,14,40, 'F'),
    37: (37,3,26,16,24,19, 'F'), 38: (29,0,30,15,33,40, 'F'),
    39: (28,-1,31,15,36,39, 'F'), 40: (34,5,32,20,30,40, 'F'),
    41: (34,5,32,20,30,40, 'F'), 42: (34,4,32,19,30,39, 'F'),
    45: (19,7,18,21,16,44, 'F'), 46: (20,6,18,19,14,40, 'F'),
    47: (20,6,19,19,16,42, 'F'), 48: (23,6,21,19,19,41, 'F'),
    49: (22,6,18,18,13,40, 'F'), 50: (24,7,20,15,9,39, 'F'),
    51: (23,6,16,18,5,37, 'F'), 52: (21,6,27,17,28,19, 'F'),
    53: (18,0,18,16,17,40, 'F'), 54: (18,0,18,15,19,41, 'F'),
    55: (20,8,19,16,16,44, 'F'), 56: (20,8,19,16,16,44, 'F'),
    57: (20,7,19,20,16,43, 'F'), 61: (3,4,4,18,5,37, 'F'),
    62: (2,3,2,17,3,39, 'F'), 63: (3,3,3,17,4,38, 'F'),
    64: (3,5,3,16,3,37, 'F'), 65: (4,6,3,17,1,35, 'F'),
    66: (7,7,4,17,1,32, 'F'), 67: (7,6,5,13,1,29, 'F'),
    68: (8,0,5,15,1,39, 'F'), 69: (5,0,4,15,1,40, 'F'),
    230: (13,-1,28,22,38,36, 'F'), 231: (-1,1,19,9,48,21, 'F'),
    232: (-1,8,27,9,55,9, 'F'), 233: (-1,7,34,8,52,9, 'F'),
    234: (-1,8,30,8,43,8, 'K'), 235: (-1,9,32,8,55,8, 'K'),
    236: (-1,8,40,8,55,8, 'F'), 237: (-1,10,15,10,54,8, 'K'),
    238: (-1,6,20,7,38,8, 'K'), 239: (16,-1,21,15,33,56, 'K'),
    245: (31,-1,37,20,42,42, 'F'), 246: (19,0,35,17,50,32, 'F'),
    247: (12,3,33,13,52,19, 'F'), 248: (9,1,37,13,50,19, 'F'),
    249: (4,0,35,12,48,16, 'F'), 250: (0,1,24,9,46,15, 'F'),
    251: (-1,1,22,8,47,16, 'F'), 252: (-1,1,37,11,48,14, 'F'),
    253: (10,1,10,4,10,5, 'F'), 254: (59,0,33,15,8,29, 'K'),
    260: (39,0,34,20,29,43, 'F'), 261: (36,-1,34,20,33,37, 'F'),
    262: (33,4,34,17,34,27, 'F'), 263: (34,0,35,17,35,26, 'F'),
    264: (34,-1,37,16,38,24, 'F'), 265: (32,-1,39,17,41,23, 'F'),
    266: (29,-1,40,20,43,25, 'F'), 267: (28,0,39,20,41,24, 'F'),
    268: (52,0,43,10,35,18, 'K'), 269: (67,10,42,10,10,10, 'K'),
    275: (34,4,22,22,9,42, 'F'), 276: (43,4,25,20,8,36, 'K'),
    277: (48,10,36,15,1,30, 'K'), 278: (51,7,38,13,0,32, 'K'),
    279: (54,7,41,13,1,33, 'K'), 280: (56,6,44,12,2,34, 'K'),
    281: (54,4,44,11,7,36, 'K'), 282: (53,3,44,9,7,36, 'K'),
    283: (71,13,33,18,7,21, 'K'), 284: (72,24,39,16,10,10, 'K'),
    290: (3,6,2,21,1,42, 'F'), 291: (27,9,14,22,0,36, 'F'),
    292: (49,11,23,20,0,29, 'F'), 293: (58,18,23,19,0,19, 'F'),
    294: (49,18,20,20,0,21, 'F'), 295: (58,17,16,20,0,20, 'F'),
    296: (57,17,37,19,0,21, 'K'), 297: (56,14,38,17,0,22, 'K'),
    298: (56,14,39,16,0,21, 'K'), 299: (56,26,14,19,0,17, 'K'),
    310: (40,1,38,16,36,39, 'F'), 311: (42,0,40,15,36,38, 'F'),
    312: (43,1,39,17,34,39, 'F'), 313: (44,1,40,17,34,39, 'F'),
    314: (44,1,40,17,34,39, 'F'), 315: (42,0,39,15,35,38, 'F'),
    316: (38,0,38,15,37,39, 'F'), 330: (19,8,18,21,17,43, 'F'),
    331: (17,7,17,20,16,41, 'F'), 334: (40,12,37,15,14,39, 'F'),
    335: (18,7,18,21,17,42, 'F'), 336: (20,8,19,21,16,44, 'F'),
}


def _dilate(m, r=1):
    """Square dilation of a bool mask by r pixels (numpy only)."""
    H, W = m.shape
    p = np.pad(m, r)
    o = np.zeros_like(m)
    for dy in range(2 * r + 1):
        for dx in range(2 * r + 1):
            o |= p[dy:dy + H, dx:dx + W]
    return o


def _staff_band(a, staff, cap=None, width=1.6, knob_r=3.5, hand_t=2.0):
    """{(y, x): unit normal} of the staff pixels the cane loses: from the
    grip toward the end that goes, the knob, and past `cap` px toward the
    tip when capped."""
    kx, ky, gx, gy, fx, fy, keep = staff
    K, G, F = (np.array(p, float) for p in ((ky, kx), (gy, gx), (fy, fx)))
    out, near = (K, F) if keep == 'F' else (F, K)
    du = out - G                    # toward the end that goes
    lu = np.hypot(*du)
    du = du / lu if lu else du
    nu = np.array([-du[1], du[0]])
    dk = near - G                   # toward the cane's tip
    lk = np.hypot(*dk)
    dk = dk / lk if lk else -du
    nk = np.array([-dk[1], dk[0]])
    band = {}
    for y, x in zip(*np.nonzero(a != TRANSPARENT)):
        p = int(a[y, x])
        v = np.array([y, x], float) - G
        tu, su = v @ du, abs(v @ nu)
        tk, sk = v @ dk, abs(v @ nk)
        knob_disc = np.hypot(y - K[0], x - K[1]) <= knob_r + 0.6
        if lu and 0.5 < tu <= lu + 1 and su <= width \
                and not (tu <= hand_t and p in STAFF_HAND):
            band[(y, x)] = nu
        elif cap and tk > cap and sk <= width:
            band[(y, x)] = nk
        elif knob_disc and (p in STAFF_KNOB or p in OUTLINE):
            band[(y, x)] = nu
    return band


def _despur(out, zone, iters=4):
    """Drop the staff's leftover outline: inside `zone`, pixels hanging on
    by one side, and outline pixels touching no coloured pixel."""
    H, W = out.shape
    for _ in range(iters):
        op = out != TRANSPARENT
        changed = False
        for y, x in zip(*np.nonzero(op & zone)):
            n4 = sum(op[yy, xx] for yy, xx in ((y - 1, x), (y + 1, x),
                                                (y, x - 1), (y, x + 1))
                     if 0 <= yy < H and 0 <= xx < W)
            body8 = sum(1 for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1)
                        if (yy, xx) != (y, x) and 0 <= yy < H and 0 <= xx < W
                        and op[yy, xx] and out[yy, xx] not in OUTLINE)
            if n4 <= 1 or (out[y, x] in OUTLINE and body8 == 0):
                out[y, x] = TRANSPARENT
                changed = True
        if not changed:
            break
    return out


def _cane(a, staff, cap=None):
    """Frame array a with its staff cut back to the cane. A lost staff pixel
    with the body on both sides (2-4 px across the line) takes the body's
    pixel beside it; any other turns transparent, and the body pixels it
    bared take the outline."""
    band = _staff_band(a, staff, cap)
    H, W = a.shape
    op = a != TRANSPARENT
    out = a.copy()
    for (y, x), n in band.items():
        sides = []
        for sg in (1, -1):
            v = None
            for k in (2, 3, 4):
                yy, xx = int(round(y + sg * n[0] * k)), int(round(x + sg * n[1] * k))
                if not (0 <= yy < H and 0 <= xx < W) or not op[yy, xx]:
                    break
                if (yy, xx) not in band:
                    v = a[yy, xx]
                    break
            sides.append(v)
        if sides[0] is not None and sides[1] is not None:
            out[y, x] = sides[0] if sides[0] not in OUTLINE else sides[1]
        else:
            out[y, x] = TRANSPARENT
    bared = op & (out == TRANSPARENT)
    for y, x in zip(*np.nonzero((out != TRANSPARENT) & _dilate(bared))):
        if out[y, x] not in OUTLINE and any(
                0 <= yy < H and 0 <= xx < W and bared[yy, xx]
                for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))):
            out[y, x] = 0
    zone = _dilate(bared, 2) | _dilate((out != a) & (out != TRANSPARENT))
    out = _despur(out, zone)
    parts = _components(out != TRANSPARENT)
    body = max(parts, key=len)
    for c in parts:
        if c is not body and len(c) < 40 and any(zone[y, x] for y, x in c):
            for y, x in c:
                out[y, x] = TRANSPARENT
    return out


def build_elder(donor_frames, corpse_frames, table, registry):
    """Mythran's 350 frames restyled as the 1994 elder."""
    n = len(donor_frames)
    dirs = drawn_directions(table, n)
    refs = set(referenced(table))
    stamp_a, _ = shot_pose(registry, 2041, 1)
    stamp = front_stamp(stamp_a)
    ref_head = head_box(arr(donor_frames[60]))
    out = []
    for i, f in enumerate(donor_frames):
        if blank(f):
            out.append(f)
            continue
        if i in ELDER_STAFF:
            f = frame(_cane(arr(f), ELDER_STAFF[i],
                            CANE_LEN if i in ELDER_ATTACK else None),
                      f['xoff'], f['yoff'])
        f = recoloured(f, ELDER_RECOLOUR)
        d = dirs.get(i)
        if d is None:                    # drawn, never shown: nearest kin
            d = dirs[min((k for k in dirs if not blank(donor_frames[k])),
                         key=lambda k: abs(k - i))]
        if d == 3:
            f = _front_hair(f, stamp, ref_head)
        else:
            f = frame(_paint_hair(arr(f), d), f['xoff'], f['yoff'])
        out.append(f)
    for sid, fno, target, anchor in ELDER_POSES:
        out[target] = pose_frame(registry, sid, fno, anchor)
    # The SE talk: 71 becomes the screen19 pose with its cane, 70 and 72
    # the same with the forearm turned.
    s19 = shot_pose(registry, *ELDER_POSES[1][:2])[0]
    for t, degrees in ELDER_TALK_SE.items():
        out[t] = talk_gesture(s19, ELDER_POSES[1][3], degrees)
    for target, d in ELDER_COMBAT_STAND.items():
        out[target] = out[ELDER_STAND[d]]
    for target, d in ELDER_DIE.items():
        out[target] = _corpse_hair(corpse_frames[CORPSE_707[d]])
    for target in refs:
        if target < n and blank(out[target]):
            out[target] = out[ELDER_STAND[2]]
    return out


# ---------------------------------------------------------------------------
# the spear children: the child (708) restyled
# ---------------------------------------------------------------------------

CHILD_DONOR = 708
CHILD_SCALE = 0.8        # the 1994 children stand 24 px, 708 stands 30
CHILD_DEATH = range(45, 75)           # 708's kneel/die frames: no spear

# 708's dress browns -> the 1994 children's grey tunic (above the waist) and
# black cloak (below), each by luminance rank against the indices the two
# screen20 children wear for it.
CHILD_DRESS = frozenset({221, 174, 220, 219, 173, 218, 172, 216, 187, 171, 215,
                         186, 170, 214, 213, 185, 169, 63, 212, 184, 62, 168,
                         211, 210, 167, 183})
CHILD_TUNIC = (27, 26, 25, 24, 23, 22)                 # dark -> light
CHILD_CLOAK = (31, 30, 29, 253, 252, 251, 250, 27)
# Bare legs and feet below the waist (olive greys and skin) go under the
# cloak too: the 1994 children's legs are black strands.
CHILD_LEGS = frozenset({199, 198, 197, 196, 195, 194, 29, 9, 27, 26, 25,
                        162, 163, 164, 165, 166, 178, 179, 180, 181, 182,
                        204, 205, 206, 207, 208, 209})
CHILD_WAIST = 0.42       # of the figure's height, from the top
# The blond child's hair: 708's black hair (the dark pixels inside the head,
# the top 30% of the figure) onto the blond ramp screen20 shows (53-55).
CHILD_HAIR_DARK = frozenset({0, 31, 30, 29, 253, 252, 9})
CHILD_BLOND = {0: 55, 31: 55, 30: 54, 29: 54, 253: 55, 252: 54, 9: 53,
               199: 53}
CHILD_HEAD = 0.30


def _rank_map(src, targets):
    s = sorted(src, key=_lum)
    t = sorted(targets, key=_lum)
    return {i: t[min(len(t) - 1, k * len(t) // len(s))] for k, i in enumerate(s)}


TUNIC_MAP = _rank_map(CHILD_DRESS, CHILD_TUNIC)
CLOAK_MAP = _rank_map(CHILD_DRESS, CHILD_CLOAK)


def _inner(op):
    p = np.pad(op, 1)
    return op & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]


def _child_colours(a, upright, blond):
    a = a.copy()
    op = a != TRANSPARENT
    rows = np.nonzero(op.any(1))[0]
    top, h = rows[0], rows[-1] - rows[0] + 1
    waist = top + int(h * CHILD_WAIST) if upright else a.shape[0]
    head = top + int(h * CHILD_HEAD)
    inner = _inner(op)
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            p = a[y, x]
            if p == TRANSPARENT:
                continue
            if blond and upright and y < head and inner[y, x] \
                    and p in CHILD_BLOND:
                a[y, x] = CHILD_BLOND[p]
            elif p in CHILD_DRESS:
                a[y, x] = (TUNIC_MAP if y < waist else CLOAK_MAP)[p]
            elif upright and y >= waist and p in CHILD_LEGS:
                a[y, x] = CLOAK_MAP[min(CHILD_DRESS, key=lambda d: abs(
                    _lum(d) - _lum(p)))]
    return a


# No outline (Douglas, 2026-10-30, art review card 7): the 1994 children
# have none, so every silhouette-edge pixel the 'outline' scale draws as
# index 0 takes the commonest colour among its inner neighbours (the edge
# ones when it has no inner one); a strand only one pixel thick has no
# coloured neighbour and stays black, as the shot's cloak strands are.
def _unoutline(a):
    H, W = a.shape
    op = a != TRANSPARENT
    edge = op & ~_inner(op)
    out = a.copy()
    for y, x in zip(*np.nonzero(edge & (a == 0))):
        near = [(yy, xx) for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1)
                if (yy, xx) != (y, x) and 0 <= yy < H and 0 <= xx < W
                and a[yy, xx] not in (0, TRANSPARENT)]
        inner = [a[p] for p in near if not edge[p]] or [a[p] for p in near]
        if inner:
            vals, counts = np.unique(inner, return_counts=True)
            out[y, x] = vals[np.argmax(counts)]
    return out


# The spear, held (Douglas, 2026-10-30, card 7: "put the shaft in the
# child's hand"). The grip is the child's right hand, found per frame: the
# outermost silhouette pixel on that hand's side between 36% and 56% of the
# figure's height (the arms hang to the waist; the hand is the sleeve's
# end), one pixel further out so the shaft clears the body's edge, with the
# hand (the shot's hand colour, 173) painted over the shaft there. Which
# side: N (0) and NW (7) the screen right, NE (1) the front (also right),
# E (2) and SE (3) the screen left; the flipped directions mirror these.
CHILD_HAND_SIDE = {7: 1, 0: 1, 1: 1, 2: -1, 3: -1}
CHILD_HAND_BAND = (0.36, 0.56)
CHILD_HAND = 173
# The spear's direction is one 3-D direction relative to the child, read off
# screen20's pose (facing W: tip 8 left and 5 up of the hand, butt 15 right
# and 11 down): the tip SPEAR_FWD[0] world-pixels forward and SPEAR_UP[0] up,
# the butt SPEAR_FWD[1] back and SPEAR_UP[1] down; per drawn direction the
# facing's screen vector per unit (the iso projection: N is up-right, NE
# right, E down-right, SE down at half length, NW up) turns it into the
# screen offsets of tip and butt from the hand. So the N frames repeat the
# shot's angle mirrored, NE holds it level, and SE / NW (toward and away
# from the camera) foreshorten it to an upright stick at the side.
SPEAR_FACING = {0: (0.707, -0.354), 1: (1.0, 0.0), 2: (0.707, 0.354),
                3: (0.0, 0.5), 7: (0.0, -0.5)}
SPEAR_FWD, SPEAR_UP = (11.3, 21.2), (1.0, 3.5)
# Which of (tip, butt) passes in front of the body: the end toward the
# camera (E and SE the tip, NW the butt); N keeps the shot's (both behind:
# the butt crosses behind the body), NE the same. Behind, the shaft shows
# only where the frame is transparent.
SPEAR_FRONT = {0: (False, False), 1: (False, False), 2: (True, False),
               3: (True, False), 7: (False, True)}
SPEAR_TIP, SPEAR_SHAFT = (20, 22), (25, 26)


def spear_offsets(d):
    """(tip, butt) screen offsets from the hand, facing drawn direction d."""
    fx, fy = SPEAR_FACING[d]
    return ((round(SPEAR_FWD[0] * fx), round(SPEAR_FWD[0] * fy - SPEAR_UP[0])),
            (round(-SPEAR_FWD[1] * fx), round(-SPEAR_FWD[1] * fy + SPEAR_UP[1])))


def child_grip(a, d):
    """(x, y) of the spear hand in frame array a, facing drawn direction d."""
    op = a != TRANSPARENT
    rows = np.nonzero(op.any(1))[0]
    top, h = rows[0], rows[-1] - rows[0] + 1
    side = CHILD_HAND_SIDE[d]
    best = None
    for y in range(int(top + CHILD_HAND_BAND[0] * h),
                   int(top + CHILD_HAND_BAND[1] * h) + 1):
        xs = np.nonzero(op[y])[0]
        if len(xs):
            x = xs.max() if side > 0 else xs.min()
            if best is None or side * x >= side * best[0]:
                best = (x, y)
    return best[0] + side, best[1]


def _line(x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0))
    return [(round(x0 + (x1 - x0) * k / n), round(y0 + (y1 - y0) * k / n))
            for k in range(n + 1)]


def _paint_spear(f, d):
    """The spear in the child's hand (child_grip), along spear_offsets(d),
    each end in front of the body or behind it (SPEAR_FRONT), the hand
    painted over the shaft. Returns the new frame (the canvas grows)."""
    a = arr(f)
    gx, gy = child_grip(a, d)
    tip, butt = spear_offsets(d)
    ends = [(_line(gx, gy, gx + tip[0], gy + tip[1]), SPEAR_FRONT[d][0], True),
            (_line(gx, gy, gx + butt[0], gy + butt[1]), SPEAR_FRONT[d][1],
             False)]
    pts = [p for seg, _f, _t in ends for p in seg]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    ox, oy = min(0, min(xs)), min(0, min(ys))
    W = max(a.shape[1], max(xs) + 1) - ox
    H = max(a.shape[0], max(ys) + 1) - oy
    canvas = np.full((H, W), TRANSPARENT, np.uint8)
    canvas[-oy:-oy + a.shape[0], -ox:-ox + a.shape[1]] = a
    for seg, front, is_tip in ends:
        for k, (x, y) in enumerate(seg[1:], 1):
            if front or canvas[y - oy, x - ox] == TRANSPARENT:
                canvas[y - oy, x - ox] = (
                    SPEAR_TIP[k % 2] if is_tip and k >= len(seg) - 3
                    else SPEAR_SHAFT[k % 2])
    canvas[gy - oy, gx - ox] = CHILD_HAND
    return frame(canvas, f['xoff'] - ox, f['yoff'] - oy)


# The shot pose: (registry id, frame) per child, at frame 1 (stand N, which
# the table draws mirrored for W, the shot's facing), anchored at its feet
# two pixels under the sole as 708's own stand frames are.
CHILD_POSE_FRAME = 1
CHILD_POSE_ANCHOR = (12, 25)
CHILD_POSES = {'dark': (2042, 0), 'blond': (2042, 1)}


def build_child(donor_frames, table, registry, hair):
    """708's 100 frames restyled as a 1994 spear child, hair 'dark' or
    'blond'."""
    from lv_tiny_avatar_art import Quantizer, scale_frame
    blond = hair == 'blond'
    dirs = drawn_directions(table, len(donor_frames))
    coloured = []
    for i, f in enumerate(donor_frames):
        if blank(f):
            coloured.append(f)
            continue
        coloured.append(frame(_child_colours(arr(f), i not in CHILD_DEATH,
                                             blond), f['xoff'], f['yoff']))
    used = set()
    for f in coloured:
        used.update(f['pixels'])
    used.discard(TRANSPARENT)
    quant = Quantizer([tuple(p) for p in PAL.tolist()], used)
    out = []
    for i, f in enumerate(coloured):
        if blank(f):
            out.append(f)
            continue
        f = scale_frame(f, CHILD_SCALE, 'outline', quant)
        f = frame(_unoutline(arr(f)), f['xoff'], f['yoff'])
        d = dirs.get(i)
        if i not in CHILD_DEATH and d in SPEAR_FACING:
            f = _paint_spear(f, d)
        out.append(f)
    sid, fno = CHILD_POSES[hair]
    out[CHILD_POSE_FRAME] = pose_frame(registry, sid, fno, CHILD_POSE_ANCHOR,
                                       mirror=True)
    return out


# ---------------------------------------------------------------------------
# the Water Zombie: the ghoul (142) recoloured, the three 1994 poses in place
# ---------------------------------------------------------------------------

ZOMBIE_DONOR = 142

# The ghoul's palette -> the 1994 Water Zombie's (2026-10-25). Each ghoul
# material, read by the palette's own hue, is matched by luminance quantile
# (weighted by how often each index is drawn over the 284 frames the ghoul's
# ANIM.DAT table names) onto the same material in the three 1994 poses:
# the olive-grey skin onto the teal skin (86-95, 132-135), its blue-grey
# shadows onto the darkest teals, the brown loincloth onto the dark green
# kilt (71-77), the red wounds onto the bright green slime (115, 70). Kept:
# the outline (0, 30, 31, 78, 79, 222, 223) and the ghoul's own greens (the
# eyes and the death's rising motes, already slime).
ZOMBIE_REMAP = {
    9: 93, 18: 132, 19: 132, 20: 132, 21: 132, 22: 133, 23: 133, 24: 134,
    25: 89, 26: 89, 27: 91, 29: 94, 44: 115, 45: 115, 46: 115, 47: 70,
    103: 93, 167: 71, 168: 71, 169: 71, 170: 73, 171: 74, 172: 75, 173: 76,
    174: 77, 186: 115, 187: 115, 188: 115, 189: 115, 190: 115, 195: 133,
    196: 134, 197: 88, 198: 90, 199: 92, 209: 71, 210: 71, 211: 71, 212: 71,
    213: 71, 214: 71, 215: 74, 216: 75, 218: 75, 219: 76, 220: 77, 221: 77,
    224: 132, 250: 91, 251: 92, 252: 93, 253: 94,
}

# The poses: (registry id, frame, target frame, anchor in the cut-out). The
# front view and the raised club take the anchor that lays them over the
# ghoul frame they replace (best mask overlap: 40 at (-6, +7), 81 at
# (-2, +9)), so a walk or a swing through them does not jump; the lunge,
# whose overlap with 112 is weak (IoU 0.42), stands on its lead foot as
# 112 does (anchor one pixel over the sole).
ZOMBIE_POSES = [
    (2050, 0, 40, (15, 56)),             # screen02 front: stand/walk SE
    (2050, 1, 81, (19, 61)),             # screen02 raised club: NW attack
    (2050, 2, 112, (14, 46)),            # screen09 lunge: E attack, hit 1
]


def build_zombie(donor_frames, registry):
    """The ghoul's 451 frames through ZOMBIE_REMAP, the three poses in."""
    out = [recoloured(f, ZOMBIE_REMAP) for f in donor_frames]
    for sid, fno, target, anchor in ZOMBIE_POSES:
        out[target] = pose_frame(registry, sid, fno, anchor)
    return out


# ---------------------------------------------------------------------------
# the entry point lv_monsters.py builds from
# ---------------------------------------------------------------------------

# {art key: donor shape}. lv_monsters.py's rows name a key; the donor's
# TYPEFLAG row and ANIM.DAT table become the new shape's.
ACTOR_ART = {
    'elder': ELDER_DONOR,
    'child-dark': CHILD_DONOR,
    'child-blond': CHILD_DONOR,
    'zombie': ZOMBIE_DONOR,
}


def actor_frames(kind, base_shapes, anim, registry=None):
    """The frames of one actor (`kind` a key of ACTOR_ART), derived from the
    pristine base U8SHAPES bytes and an ANIM.DAT holding the donor's table
    (the table decides which direction each frame is drawn for)."""
    from shape_viewer import read_flx_entry, parse_shape_frames
    from lv_tiny_avatar_art import decode_anim
    donor = ACTOR_ART[kind]
    registry = registry or load_registry()
    frames = parse_shape_frames(read_flx_entry(base_shapes, donor))
    if kind == 'zombie':
        out = build_zombie(frames, registry)
    else:
        table = decode_anim(anim, donor)
        if kind == 'elder':
            corpse = parse_shape_frames(read_flx_entry(base_shapes,
                                                       ELDER_CORPSE_DONOR))
            out = build_elder(frames, corpse, table, registry)
        else:
            out = build_child(frames, table, registry, kind.split('-')[1])
    # The donors' own art draws index 9, which the engine colour-cycles (the
    # peasant 707 81 pixels, the child 708 33): the derived frames take its
    # static same-colour twin, as the shot poses do.
    out = [recoloured(f, CYCLE_TWINS) for f in out]
    cyc = sorted({p for f in out for p in f['pixels'] if p in CYCLING})
    if cyc:
        raise SystemExit(f"{kind}: frames use cycling palette indices {cyc}")
    return out

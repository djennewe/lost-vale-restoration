#!/usr/bin/env python3
"""
avatar_mover.py — the Avatar's held-input movement, step for step.

WHY THIS EXISTS (2026-10-10). `test_route_reach.arrival_corridors` walked
straight lines from each arrival pad and ended a line at the first refused
step. The engine does not stop there. In-engine
(docs/playtest-2026-10-10-gateways.md) a northbound hold from Map 8's pad
213 met the double doors' west jamb, slid north-east into the open doorway
and fired trigger 201 to Map 9, 9 runs of 9; a keyboard run held on Map 9
wall-followed the hall into trigger 203. The line model called both safe.

So this module replays the decision the engine makes every time the
Avatar's previous animation ends, verbatim from the fork
(scummvm-lv-console/engines/ultima/ultima8):

  mover   U8AvatarMoverProcess::handleNormalMode / step
          (world/actors/u8_avatar_mover_process.cpp:331-731). Run is chosen
          only after a walk or a run. A refused step (tryAnim FAILURE, or
          END_OFF_LAND for the small `step` action) is retried one heading
          clockwise (Direction_OneRight), then one anticlockwise
          (Direction_OneLeft); if both are refused a run falls back to a
          walk and a walk to a step, each again with both side headings;
          a step refused all three ways becomes `stand`.
          checkTurn (avatar_mover_process.cpp:121) lets a walk or run change
          heading by 45 degrees without a turn animation, and doAnim leaves
          the Avatar FACING the heading he actually stepped in.
  input   MOUSE (right button held): the heading is the mouse's, fixed, so
          each step tries it first. KEYBOARD (Up = MOVE_FORWARD,
          metaengine.cpp:50): the heading is the Avatar's own facing
          (`direction = avatar->getDir()`), so one slide turns him for good
          and a held key wall-follows.
  anim    Actor::tryAnim + AnimationTracker::step, shape 1's actions walk
          (0), run (1) and step (12) decoded from the built ANIM.DAT the
          way AnimDat::load does: per frame 4 * deltaDir world units along
          Direction_X/YFactor, two-step ranges from AnimAction::getAnimRange.
          A frame that lands invalid or unsupported goes to
          CurrentMap::scanForValidPosition (z offsets 0,-4,4,-8,8 and
          SIDEWAYS offsets 0,-4,4 perpendicular to the heading), so a
          frame can creep 4 units round a corner; a frame of 56 or more
          is swept (sampled every 4 units) as the tracker's sweepTest does.
  boxes   CurrentMap::getPositionInfo / Box::overlaps verbatim, including
          the rule that an item already overlapping the animation's START
          box does not block it.
  eggs    EggHatcherProcess::run, checked at every position the anim
          process moves the Avatar through (the interpolated sub-frame
          positions too, ActorAnimProcess::run), with MainActor's
          justTeleported rule.
  time    in anim frame periods: a frame lasts frameRepeat + 1 of them.
          Walk and run are 4 frames x 2 periods; the 10-10 playtest's 205
          rows measure 4.43 (mouse run, 1560 units between the 2 s and 4 s
          holds at 176 per run) and 4.64 (keyboard walk, 928 at ~100 per
          walk) of those animations a second, so PERIODS_PER_SECOND = 36.
          A turn on the spot is costed 3 periods per 45 degrees.
  falls   an anim that ends unsupported above z 0 drops him onto the
          highest top under him (GravityProcess, simplified: no slide, no
          bounce); a drop of 104 or more is lethal and ends the hold, and
          every other drop goes on Mover.falls. That list is how a RISER
          shows: the scan has no +/-1..3 offsets, so a walk frame onto a
          surface 1 above the floor (Map 8's z=1 slab, zero height) is
          lifted to z+4, unsupported; the walk ends END_OFF_LAND, the step
          that replaces it plays to that frame, and he only gets onto the
          surface by falling the 3 units back down (in the engine a hurl,
          GravityProcess and the `land` animation).
  start   a teleport arrival is mid-stride; a player who sets off is not
          (hold(standing=True)): the first animation is then a walk even
          with run held, and a keyboard hold walks his FACING.

WHAT IT REPRODUCES. Replayed on FIXED 29abf906, the build the 10-10
gateways playtest ran (positions per step parity where they differ):
  Map 8 pad 213 north, doors open    every mode -> 201 at 0.44-0.67 s
                                     (engine: 9 of 9 -> 201, Map 9)
  Map 8 pad 213 north, doors closed  mouse run stops at (20312,3148,0) /
                                     (20316,3144,0) (engine: (20312,3148,0))
  Map 8 pad 213 north-west           stops at (20140,3280,0), inside bone
                                     piles (engine: wedged there, 2 of 2)
  Map 8 pad 200 north                mouse run (20156,3140,8) /
                                     (20156,3148,8), key walk (20100,3160,8)
                                     / (20104,3136,8) (engine: (20156,3140,8),
                                     (20156,3148,8), (20100,3160,8))
  Map 9 pad 201 north                mouse run (13820,13380)/(13816,13384),
                                     key walk (13696,13376) (engine: same)
  Map 9 pad 201 north-east           mouse run stops (14812,12708)
                                     (engine: (14812,12708))
  Map 9 pad 201 Shift+Up             -> 203 at 6.0 s (engine: 7.25-7.92 s)
The last row is the clock: on a long wall-follow the model runs ahead of
the engine, so a time bound applied to it errs long.
And on FIXED 22cada6f, the maps3 playtest's build (its Map 8 is item for
item the 332bdeb2 one), from a standstill (docs/playtest-2026-10-10-maps3.md
G4 and finding 3; its results.json and lv_run.log):
  Map 8 key walk /2 from              facing SE: stops at (20211,5747,0), out
  (20967,3431,0)                      of the chamber (engine: the same spot;
                                     he stood on frame 3, the SE stand
                                     frame, when Up went down [INFERENCE:
                                     frames 0-7 track his heading there])
  Map 8 the 16 E rows that loaded    all fire 212, each only by falling onto
  Map 10 (x 20894..21007)            the z=1 slab from z 4 (the riser)
The run that stood at (21094,3394,0) is NOT reproduced: the model fires
212 from every E start. The log there shows frame 501 (shakeHead/
lookRight, idle animations the mover plays only with no movement input),
so the key was probably not held [INFERENCE].

WHAT IT DOES NOT MODEL: jumping, combat, NPCs and monsters (the
wandering ghost at Map 8's doors included), and the mouse being moved
during a hold. The items it sees are what the caller passes: FIXED.DAT
(globs expanded) plus, for a base-game map, the new-game NONFIXED.DAT,
with Map 8's door leaves in the state asked for.
"""

import os
import struct
import sys
import tempfile

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)

from u8_map import MapArchive, MapItem              # noqa: E402
from map_preview import GlobReader                   # noqa: E402
from parse_typeflag import load_typeflag             # noqa: E402

DEFAULT_FIXED = os.path.join(BASE_DIR, 'shared', 'build', 'FIXED.DAT')
DEFAULT_TYPEFLAG = os.path.join(BASE_DIR, 'shared', 'build', 'TYPEFLAG.DAT')
DEFAULT_ANIM = os.path.join(BASE_DIR, 'shared', 'build', 'ANIM.DAT')
U8SAVE = os.path.join(BASE_DIR, 'shared', 'data', 'u8-install', 'SAVEGAME',
                      'U8SAVE.000')

SI_SOLID, SI_LAND, SI_DAMAGING = 0x02, 0x08, 0x40
ROOF = 0x100                     # our own bit: TYPEFLAG flags1 & 0x04
FLG_FLIPPED = 0x0020
BODY = (64, 64, 40)              # shape 1's footpad (2,2,5)

WALK, RUN, STAND, STEP = 0, 1, 2, 12      # Animation::Sequence (animation.h)
TWOSTEP, LOOPING, LOOPING2_U8 = 0x01, 0x04, 0x10
AFF_ONGROUND = 0x02

# Direction (misc/direction.h): 16-way, the 8 U8 headings are the even ones.
DIRS = {'N': 0, 'NE': 2, 'E': 4, 'SE': 6, 'S': 8, 'SW': 10, 'W': 12,
        'NW': 14}
NAMES = {v: k for k, v in DIRS.items()}
_XF = (0, 1, 1, 1, 0, -1, -1, -1)
_YF = (-1, -1, 0, 1, 1, 1, 0, -1)
PERIODS_PER_SECOND = 36
SCAN = 8                          # scanForValidPosition's U8 scansize
SEARCH = (0, -4, 4, -8, 8)        # SEARCH_OFFSETS_U8; first 3 are sideways


def xf(d):
    return _XF[d // 2]


def yf(d):
    return _YF[d // 2]


def one_right(d):
    return (d + 2) % 16


def one_left(d):
    return (d + 14) % 16


# --------------------------------------------------------------------------
# ANIM.DAT (gfx/anim_dat.cpp AnimDat::load, U8 branch)

class AnimAction:
    def __init__(self, size, flags, repeat, frames):
        self.size, self.flags, self.repeat = size, flags, repeat
        self.frames = frames           # [dir8][frame] = (deltaDir, dz, flags)

    def anim_range(self, lastanim, lastdir, firststep, action, d):
        """AnimAction::getAnimRange."""
        start, end = 0, self.size
        if self.flags & TWOSTEP:
            looping = bool(self.flags & LOOPING)
            if firststep:
                start = self.size - 1 if looping else 0
                end = self.size // 2
            else:
                start = self.size // 2
                if looping:
                    end = self.size - 1
        elif lastanim == action and lastdir == d and self.size > 1:
            start = 1
        return start, end

    def next_frame(self, f, end):
        """AnimationTracker::getNextFrame."""
        f += 1
        if f == end:
            return end
        if f >= self.size:
            f = 1 if self.flags & LOOPING else 0
        return f


def load_anims(path=DEFAULT_ANIM, shape=1, actions=(WALK, RUN, STAND, STEP)):
    data = open(path, 'rb').read()
    off = struct.unpack_from('<I', data, 4 * shape)[0]
    out = {}
    for act in actions:
        ao = struct.unpack_from('<I', data, off + 4 * act)[0]
        size, lo, rep, hi = data[ao], data[ao + 1], data[ao + 2], data[ao + 3]
        raw = lo | (hi << 8)
        flags = raw & (TWOSTEP | LOOPING)
        if raw & LOOPING2_U8:         # loadAnimActionFlags: handled as LOOPING
            flags |= LOOPING
        p, frames = ao + 4, []
        for _ in range(8):
            row = []
            for _ in range(size):
                b = data[p:p + 6]
                p += 6
                dz = struct.unpack('b', b[2:3])[0]
                dd = struct.unpack('b', b[4:5])[0]
                row.append((dd, dz, b[5] + ((b[1] & 0xF8) << 8)))
            frames.append(row)
        out[act] = AnimAction(size, flags, rep & 0xF, frames)
    return out


AFF_FLIPPED = 0x0020


def sprite_frames(action, d, path=DEFAULT_ANIM, shape=1):
    """The shape frames an action draws heading `d` (a DIRS value), as
    (frame, flipped) per anim frame: AnimDat::load's U8 `_frame` (byte 0
    plus the low 3 bits of byte 1) and AFF_FLIPPED. The mover needs only
    the movement; a paint check needs the sprite."""
    data = open(path, 'rb').read()
    off = struct.unpack_from('<I', data, 4 * shape)[0]
    ao = struct.unpack_from('<I', data, off + 4 * action)[0]
    size = data[ao]
    p = ao + 4 + (d // 2) * size * 6
    out = []
    for k in range(size):
        b = data[p + 6 * k:p + 6 * k + 6]
        flags = b[5] + ((b[1] & 0xF8) << 8)
        out.append((b[0] | ((b[1] & 0x7) << 8), bool(flags & AFF_FLIPPED)))
    return out


# --------------------------------------------------------------------------
# The items, bucketed so a box query touches a few cells.

CELL = 128


class World:
    def __init__(self, items, shapes, roi):
        """items: MapItems (glob eggs expanded here), roi (x0, y0, x1, y1):
        only items within reach of it are kept."""
        x0, y0, x1, y1 = roi
        gr = None
        boxes = []
        for it in items:
            if it.is_glob_egg:
                gr = gr or GlobReader()
                boxes.extend(self._box(sub, shapes) for sub in
                             gr.glob_to_items(it.quality, it.x, it.y,
                                              it.z & 0xFF))
            else:
                boxes.append(self._box(it, shapes))
        self.cells = {}
        for b in boxes:
            if b is None:
                continue
            bx, by, bz, bxd, byd, bzd, fl = b
            if bx <= x0 - 128 or bx - bxd >= x1 + 128 or \
               by <= y0 - 128 or by - byd >= y1 + 128:
                continue
            for cx in range((bx - bxd) // CELL, bx // CELL + 1):
                for cy in range((by - byd) // CELL, by // CELL + 1):
                    self.cells.setdefault((cx, cy), []).append(b)
        self._near, self._pi, self._track = {}, {}, {}

    @staticmethod
    def _box(it, shapes):
        if it.x < 64 or it.y < 64 or not 0 <= it.shape < len(shapes):
            return None
        si = shapes[it.shape]
        fl = si.flags0 & (SI_SOLID | SI_LAND | SI_DAMAGING)
        if si.flags1 & 0x04:
            fl |= ROOF
        if not fl:
            return None
        xd, yd = si.footpad_x * 32, si.footpad_y * 32
        if it.flags & FLG_FLIPPED:
            xd, yd = yd, xd
        return (it.x, it.y, it.z & 0xFF, xd, yd, si.footpad_z * 8, fl)

    def near(self, xlo, ylo, xhi, yhi):
        key = (xlo // CELL, ylo // CELL, xhi // CELL, yhi // CELL)
        hit = self._near.get(key)
        if hit is None:
            hit, seen = [], set()
            for cx in range(key[0], key[2] + 1):
                for cy in range(key[1], key[3] + 1):
                    for b in self.cells.get((cx, cy), ()):
                        if id(b) not in seen:
                            seen.add(id(b))
                            hit.append(b)
            self._near[key] = hit
        return hit

    # CurrentMap::getPositionInfo(target, start, avatar flags). The Avatar's
    # flags (0x22) carry SI_SOLID and not SI_DAMAGING, so only SOLID blocks.
    def position_info(self, x, y, z, start=None, real_surface=False):
        """(valid, supported). real_surface drops the engine's `z <= 0 is
        supported` rule, as exact_reach.py does (its deviation 1): a body
        must stand on an actual item."""
        key = (x, y, z, start, real_surface)
        hit = self._pi.get(key)
        if hit is not None:
            return hit
        xd, yd, zd = BODY
        midx, midy = x - xd // 2, y - yd // 2
        supportz = landz = -10 ** 9
        valid = True
        for (bx, by, bz, bxd, byd, bzd, fl) in self.near(x - xd, y - yd, x, y):
            xy = not (x <= bx - bxd or bx <= x - xd or
                      y <= by - byd or by <= y - yd)
            if fl & SI_SOLID and valid and xy and \
               not (z + zd <= bz or bz + bzd <= z):
                if start is None or not _overlaps(start, (bx, by, bz, bxd,
                                                          byd, bzd)):
                    valid = False
            top = bz + bzd
            if xy and fl & (SI_SOLID | SI_LAND | ROOF) and supportz < top <= z:
                supportz = top
            if bx - bxd < midx <= bx and by - byd < midy <= by and \
               z >= top and fl & (SI_LAND | ROOF) and top > landz:
                landz = top
        supported = (supportz == z and landz + 8 >= z) or \
            (z <= 0 and not real_surface)
        self._pi[key] = (valid, supported)
        return valid, supported

    # CurrentMap::scanForValidPosition(x, y, z, avatar, movedir, true, ...)
    def scan(self, x, y, z, movedir):
        xd, yd, zd = BODY
        searchdir = (movedir + 4) % 8
        xdir, ydir = xf(searchdir) != 0, yf(searchdir) != 0
        stype = searchdir // 2
        valid = [[True] * (2 * SCAN + 1) for _ in range(2 * SCAN + 1)]
        support = [[False] * (2 * SCAN + 1) for _ in range(2 * SCAN + 1)]
        for (bx, by, bz, ixd, iyd, izd, fl) in self.near(
                x - xd - SCAN, y - yd - SCAN, x + SCAN, y + SCAN):
            if not fl & SI_SOLID:
                continue
            minv = max(bz - z - zd + 1, -SCAN)
            maxv = min(bz + izd - z - 1, SCAN)
            sminx, smaxx = bx - ixd + 1 - x, bx + xd - 1 - x
            sminy, smaxy = by - iyd + 1 - y, by + yd - 1 - y
            minh, maxh = -100, 100
            if not xdir and (sminx > 0 or smaxx < 0):
                continue
            if not ydir and (sminy > 0 or smaxy < 0):
                continue
            if xdir:
                minh, maxh = max(minh, sminx), min(maxh, smaxx)
            if ydir and stype != 1:
                minh, maxh = max(minh, sminy), min(maxh, smaxy)
            if stype == 1:
                minh, maxh = max(minh, -smaxy), min(maxh, -sminy)
            minh, maxh = max(minh, -SCAN), min(maxh, SCAN)
            for j in range(minv, maxv + 1):
                for i in range(minh, maxh + 1):
                    valid[j + SCAN][i + SCAN] = False
            top = bz + izd
            if z - SCAN <= top <= z + SCAN:
                for i in range(minh, maxh + 1):
                    support[top - z + SCAN][i + SCAN] = True
        found, out = False, None
        for horiz in SEARCH[:3]:
            for vert in SEARCH:
                if not valid[vert + SCAN][horiz + SCAN]:
                    continue
                sup = support[vert + SCAN][horiz + SCAN]
                if not found or sup:
                    tx = x + (horiz if stype != 0 else 0)
                    ty = y - horiz if stype == 1 else \
                        y if stype == 2 else y + horiz
                    out = (tx, ty, z + vert)
                if sup:
                    return out
                found = True
        return out

    def landing(self, x, y, z):
        """Where a body dropped at (x, y, z) comes to rest: the highest
        top at or below z of anything under it that supports, else 0."""
        xd, yd, _ = BODY
        best = 0
        for (bx, by, bz, bxd, byd, bzd, fl) in self.near(x - xd, y - yd, x, y):
            if fl & (SI_SOLID | SI_LAND | ROOF) and best < bz + bzd <= z and \
               not (x <= bx - bxd or bx <= x - xd or
                    y <= by - byd or by <= y - yd):
                best = bz + bzd
        return best

    def resting(self, x, y, z):
        """The body overlaps no solid and rests on a real top at exactly z
        (getPositionInfo's supportz == z, without the z <= 0 freebie). The
        land rule is not asked: on the lip of a bone pile the engine calls
        him unsupported, yet he stands there and walks off. A body inside
        a solid is what wedged him on Map 8 (playtest 10-10 finding 2)."""
        xd, yd, zd = BODY
        rest = False
        for (bx, by, bz, bxd, byd, bzd, fl) in self.near(x - xd, y - yd, x, y):
            if x <= bx - bxd or bx <= x - xd or y <= by - byd or by <= y - yd:
                continue
            if fl & SI_SOLID and not (z + zd <= bz or bz + bzd <= z):
                return False
            if fl & (SI_SOLID | SI_LAND | ROOF) and bz + bzd == z:
                rest = True
        return rest


def _overlaps(a, b):
    ax, ay, az, axd, ayd, azd = a
    bx, by, bz, bxd, byd, bzd = b
    return not (ax <= bx - bxd or bx <= ax - axd or ay <= by - byd or
                by <= ay - ayd or az + azd <= bz or bz + bzd <= az)


def _swept_blocked(world, cur, end):
    """AnimationTracker's sweepTest for a large step, sampled every 4 units:
    a SOLID box the body enters on the way and did not overlap at the
    frame's start blocks it."""
    xd, yd, zd = BODY
    n = max(abs(end[0] - cur[0]), abs(end[1] - cur[1]), abs(end[2] - cur[2]))
    n = max(1, n // 4)
    sb = (cur[0], cur[1], cur[2], xd, yd, zd)
    xlo = min(cur[0], end[0]) - xd
    ylo = min(cur[1], end[1]) - yd
    cands = [b for b in world.near(xlo, ylo, max(cur[0], end[0]),
                                   max(cur[1], end[1]))
             if b[6] & SI_SOLID and not _overlaps(sb, b[:6])]
    for k in range(1, n):
        p = tuple(cur[i] + (end[i] - cur[i]) * k // n for i in range(3))
        pb = (p[0], p[1], p[2], xd, yd, zd)
        if any(_overlaps(pb, b[:6]) for b in cands):
            return True
    return False


SUCCESS, END_OFF_LAND, FAILURE = 'ok', 'off', 'fail'


def track(world, anims, pos, action, d, st):
    """Actor::tryAnim / AnimationTracker. st = (lastanim, facing, firststep).
    Returns (result, [positions after each frame], frame count). Memoised
    per world: the same anim from the same spot is replayed constantly."""
    a = anims[action]
    lastanim, facing, firststep = st
    start, end = a.anim_range(lastanim, facing, firststep, action, d)
    key = (pos, action, d, start, end)
    hit = world._track.get(key)
    if hit is None:
        hit = world._track[key] = _track(world, a, pos, d, start, end)
    return hit


def _track(world, a, pos, d, start, end):
    rows = a.frames[d // 2]
    curr, path = pos, []
    blocked = unsupported = False
    f, first = start, True
    while True:
        if not first:
            f = a.next_frame(f, end)
        if f == end:
            break
        first = False
        dd, dz, ff = rows[f]
        dx, dy = 4 * xf(d) * dd, 4 * yf(d) * dd
        t = (curr[0] + dx, curr[1] + dy, curr[2] + dz)
        onground = bool(ff & AFF_ONGROUND)
        if (abs(dx) >= BODY[0] - 8 or abs(dy) >= BODY[1] - 8 or
                abs(dz) >= BODY[2] - 8) and _swept_blocked(world, curr, t):
            blocked = True
            break
        sbox = (pos[0], pos[1], pos[2]) + BODY
        valid, sup = world.position_info(*t, start=sbox)
        if not valid or (onground and not sup):
            if onground:
                t = world.scan(*t, d)
                if t is None:
                    blocked = True
                    break
            elif not valid:
                blocked = True
                break
        curr = t
        path.append(curr)
        if onground and not world.position_info(*curr, start=sbox)[1]:
            unsupported = True
            break
    if blocked:
        return FAILURE, path, len(path)
    if unsupported:
        return END_OFF_LAND, path, len(path)
    sbox = (pos[0], pos[1], pos[2]) + BODY
    if not world.position_info(*curr, start=sbox)[1]:
        return END_OFF_LAND, path, len(path)
    return SUCCESS, path, len(path)


class Avatar:
    def __init__(self, pos, facing, lastanim, firststep):
        self.pos, self.facing = pos, facing
        self.lastanim, self.firststep = lastanim, firststep
        self.periods = 0

    def st(self):
        return (self.lastanim, self.facing, self.firststep)


class Mover:
    """U8AvatarMoverProcess, held input only. Each decide() runs one
    animation (or a turn); every position the Avatar passes through is
    appended to `trail`, sub-frame interpolation included, for the caller's
    egg check. Every fall that does not kill is appended to `falls` as
    ((x, y, z) where the anim ended unsupported, z he lands at)."""

    def __init__(self, world, anims, avatar, mouse, run, mousedir=None):
        self.w, self.anims, self.av = world, anims, avatar
        self.mouse, self.run, self.mousedir = mouse, run, mousedir
        self.event = None
        self.trail = []
        self.falls = []

    def decide(self):
        av = self.av
        if self.run and av.lastanim in (RUN, WALK):
            nextanim = RUN
        else:
            nextanim = WALK
        d = self.mousedir if self.mouse else av.facing
        self.step(nextanim, d, False)

    def _try(self, action, d):
        return track(self.w, self.anims, self.av.pos, action, d,
                     self.av.st())[0]

    def step(self, action, direction, adjusted):
        av = self.av
        res = self._try(action, direction)
        stepdir = direction

        def refused(r):
            return r == FAILURE or (action == STEP and r == END_OFF_LAND)

        if refused(res):
            alt1, alt2 = one_right(stepdir), one_left(stepdir)
            res = self._try(action, alt1)
            if refused(res):
                res = self._try(action, alt2)
                if refused(res):
                    if action == WALK:
                        return self.step(STEP, direction, True)
                    if action == RUN:
                        return self.step(WALK, direction, True)
                else:
                    stepdir = alt2
            else:
                stepdir = alt1
        if action == STEP and res == END_OFF_LAND and not adjusted \
                and av.pos[2] > 0:
            if self.check_turn(stepdir, False):
                return
            self.event = ('teeters', av.pos)    # keepBalance: an edge
            return
        if action == STEP and res == FAILURE:
            action = STAND
        if action == WALK and res == END_OFF_LAND:
            action = STEP
        if action == RUN and res == END_OFF_LAND:
            action = WALK
        moving = action in (RUN, WALK)
        if self.check_turn(stepdir, moving):
            return
        self.do_anim(action, stepdir)

    def check_turn(self, d, moving):
        """AvatarMoverProcess::checkTurn."""
        av = self.av
        cur = av.facing
        if d == cur:
            return False
        if moving:
            if av.lastanim in (WALK, RUN) and (abs(d - cur) + 2) % 16 <= 4:
                return False
            if av.lastanim == RUN:
                self.do_anim(WALK, cur)
                return True
        av.facing = d              # turnTowardDir: look anims, no movement
        av.lastanim = STAND
        av.periods += 3 * ((min((d - cur) % 16, (cur - d) % 16)) // 2)
        return True

    def do_anim(self, action, d):
        av = self.av
        a = self.anims[action]
        res, path, nframes = track(self.w, self.anims, av.pos, action, d,
                                   av.st())
        prev = av.pos
        for p in path:
            for k in range(1, a.repeat + 2):
                # getInterpolatedPosition: C division truncates
                self.trail.append(tuple(
                    prev[i] + int((p[i] - prev[i]) * k / (a.repeat + 1))
                    for i in range(3)))
            prev = p
        av.facing = d
        av.lastanim = action
        av.periods += max(nframes, 1) * (a.repeat + 1)
        if path:
            av.pos = path[-1]
        if a.flags & TWOSTEP and res != FAILURE:
            av.firststep = not av.firststep
        if res == END_OFF_LAND and av.pos[2] > 0:
            # The anim stopped on the unsupported frame and gravity takes
            # over: he drops straight down onto the highest top under him.
            # A drop of 104 or more kills (gravity_process.cpp:322-331).
            x, y, z = av.pos
            land = self.w.landing(x, y, z)
            if z - land >= 104:
                self.event = ('falls', (x, y, land))
            else:
                self.falls.append(((x, y, z), land))
            av.pos = (x, y, land)
            av.lastanim = STAND
            self.trail.append(av.pos)
        return res


# --------------------------------------------------------------------------
# Eggs (EggHatcherProcess::run, world/egg_hatcher_process.cpp)

def hatch_box(egg):
    """The Avatar positions (his max corner) a teleporter fires for:
    x1 <= px < x2 + 64, the same in y, egg z - 48 < pz <= egg z + 48, where
    x1, x2 = egg x -/+ 32 * (npcNum >> 4) and y uses npcNum & 0xF."""
    xr, yr = (egg.npcnum >> 4) * 32, (egg.npcnum & 0xF) * 32
    return (egg.x - xr, egg.x + xr + BODY[0], egg.y - yr,
            egg.y + yr + BODY[1], egg.z & 0xFF)


def in_box(b, p):
    return b[0] <= p[0] < b[1] and b[2] <= p[1] < b[3] and \
        b[4] - 48 < p[2] <= b[4] + 48


def hold(world, anims, start, heading, mouse, run, firststep, boxes,
         seconds, standing=False, falls=None):
    """Hold one input from `start`, the Avatar facing `heading` (a teleport
    keeps his facing) with walk or run already under way — or, with
    `standing`, from a standstill, as a player sets off: the first
    animation is then a walk even when running is held, because
    handleNormalMode picks run only after a walk or a run. A keyboard hold
    walks the Avatar's FACING, so `heading` is the way he faces when the
    key goes down, whatever the player meant. `boxes`: {id: hatch_box} of
    every teleporter on the map. A box he starts inside does not fire
    until he has been outside all of them once (MainActor::_justTeleported).
    `falls`, a list, collects every fall he survives (Mover.falls).

    Returns (outcome, trigger id or None, position, seconds, trail), the
    outcome one of 'trigger', 'stops' (no movement left), 'clear' (still
    moving at the bound), 'falls' (a lethal drop) or 'teeters'."""
    d = DIRS[heading]
    av = Avatar(start, d, STAND if standing else (RUN if run else WALK),
                firststep)
    mv = Mover(world, anims, av, mouse, run, d)
    if falls is not None:
        mv.falls = falls
    armed = not any(in_box(b, start) for b in boxes.values())
    limit = seconds * PERIODS_PER_SECOND
    still = 0
    while av.periods < limit:
        before = (av.pos, av.facing, av.lastanim)
        n0 = len(mv.trail)
        mv.decide()
        for p in mv.trail[n0:]:
            inb = [k for k, b in boxes.items() if in_box(b, p)]
            if armed and inb:
                return ('trigger', inb[0], p,
                        av.periods / PERIODS_PER_SECOND, mv.trail)
            armed = armed or not inb
        if mv.event:
            return (mv.event[0], None, av.pos,
                    av.periods / PERIODS_PER_SECOND, mv.trail)
        if (av.pos, av.facing, av.lastanim) == before:
            still += 1
            if still >= 3:
                return ('stops', None, av.pos,
                        av.periods / PERIODS_PER_SECOND, mv.trail)
        else:
            still = 0
    return ('clear', None, av.pos, av.periods / PERIODS_PER_SECOND,
            mv.trail)


def world_dir(dy, dx):
    """Direction_GetWorldDir(deltay, deltax, dirmode_8dirs), C division: the
    8-way heading of (dx, dy). A keyboard player turns in 45-degree steps,
    so this is the facing he takes to walk at a point; the mouse path
    (Direction_Get(2*dy, dx) in screen space) is the same sectors rotated."""
    if dx == 0:
        return 'NE' if dy == 0 else ('S' if dy > 0 else 'N')
    q = abs(1024 * dy) // abs(dx)
    dydx = q if (dy >= 0) == (dx > 0) or dy == 0 else -q
    if dydx >= 0:
        if dx > 0:
            return 'E' if dydx <= 424 else 'SE' if dydx <= 2472 else 'S'
        return 'W' if dydx <= 424 else 'NW' if dydx <= 2472 else 'N'
    if dx > 0:
        return 'E' if dydx >= -424 else 'NE' if dydx >= -2472 else 'N'
    return 'W' if dydx >= -424 else 'SW' if dydx >= -2472 else 'S'


# Every way to hold an input: (mouse?, run?, first step of the two-step
# walk/run cycle?). The parity is whatever the Avatar's last step left.
MODES = [(m, r, f) for m in (True, False) for r in (False, True)
         for f in (False, True)]


def mode_name(mouse, run, firststep):
    return (f'{"mouse" if mouse else "key"} {"run" if run else "walk"}'
            f'{"" if firststep else "/2"}')


def movable(world, anims, pos, st=(WALK, 0, False)):
    """Some heading lets him walk or step on (tryAnim is not FAILURE)."""
    return any(track(world, anims, pos, act, d, st)[0] != FAILURE
               for d in range(0, 16, 2) for act in (WALK, STEP))


def footing(world, anims, pos, nanims=3):
    """The arrival-pad wedge check: the pad itself rests on a real top
    clear of every solid and he can move off it; then, held in each of the
    8 headings in every mode, each of his first `nanims` animations ends
    the same way. Returns (wedges, falls): the problems found, and the
    first steps that walk off an edge to a lethal drop."""
    if not world.resting(*pos):
        return [f'the pad {pos} is not resting on a top clear of solids'], []
    if not movable(world, anims, pos):
        return [f'the pad {pos} refuses every heading'], []
    wedges, falls = [], []
    for h in DIRS:
        for (m, r, f) in MODES:
            d = DIRS[h]
            av = Avatar(pos, d, RUN if r else WALK, f)
            mv = Mover(world, anims, av, m, r, d)
            for _ in range(nanims):
                mv.decide()
                if mv.event:
                    falls.append(f'{h} {mode_name(m, r, f)} {mv.event[0]} '
                                 f'at {mv.event[1]}')
                    break
                if not world.resting(*av.pos) or \
                        not movable(world, anims, av.pos, av.st()):
                    wedges.append(f'{h} {mode_name(m, r, f)} ends at '
                                  f'{av.pos}, inside a solid, on nothing '
                                  f'or refused every way')
                    break
    return wedges, falls


def map_items(mapnum, fixed=DEFAULT_FIXED, nonfixed=True):
    """FIXED.DAT's items for a map plus, for a base-game map, the new-game
    NONFIXED.DAT's (x <= 2 there is a container depth, not a position)."""
    items = list(MapArchive(fixed).get_map_items(mapnum))
    if nonfixed and os.path.exists(U8SAVE):
        from scan_npc_slots import read_u8save
        with tempfile.TemporaryDirectory() as tmp:
            nf = os.path.join(tmp, 'NONFIXED.DAT')
            with open(nf, 'wb') as fh:
                fh.write(read_u8save(U8SAVE)['NONFIXED.DAT'])
            items += [i for i in MapArchive(nf).get_map_items(mapnum)
                      if i.x > 2]
    return items


# Map 8's double-door leaves are NONFIXED items (U8SAVE.000): shape 342
# closed at (20351,3071) and (20479,3071); opened, each becomes 340 (32 x
# 128) against its jamb, (20255,3071) and (20479,3071) — read back live,
# docs/playtest-2026-07-31-doors-investigation.md "Observed open geometry".
DOOR_SHAPES = (340, 342)
DOOR_CLOSED = ((342, 20351, 3071), (342, 20479, 3071))
DOOR_OPEN = ((340, 20255, 3071), (340, 20479, 3071))


def with_doors(items, state):
    """Map 8 items with the double doors 'open' or 'closed'."""
    out = [i for i in items if not (i.shape in DOOR_SHAPES and
                                    (i.x, i.y) in {(20351, 3071),
                                                   (20479, 3071),
                                                   (20255, 3071)})]
    for (shape, x, y) in (DOOR_OPEN if state == 'open' else DOOR_CLOSED):
        out.append(MapItem(x=x, y=y, z=0, shape=shape))
    return out


def load_shapes(path=DEFAULT_TYPEFLAG):
    return load_typeflag(path)

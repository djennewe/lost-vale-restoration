#!/usr/bin/env python3
"""
lv_tiny_avatar.py — give the shrunken Avatar its own body, shape 867.

WHY THIS EXISTS
---------------
`makeAvatarTiny()` (lv-patched/FREE.UNK) does `Avatar.setType(TypeTinytar)`,
and usecode setType reassigns the Avatar's own shape. Until 2026-10-08
TypeTinytar was 708, the base game's child actor, picked for its (1,1,4)
footpad and 100 frames. But an Actor is a Container, and the engine reads
the Avatar's own weight and capacity from whatever shape it currently is
(Container::getTotalWeight/getCapacity, container.cpp:219-245): shrunk to
708 the pack read weight 520 against capacity 200, against 30/250 at full
size, and every pickup or equip ran against those numbers
(docs/reviews/2026-09-30-four-anomalies.md §1). 708 is also two village
children on Map 10, so its row could not be edited in place without
changing them too. Douglas, 2026-10-08: a slot of its own.

From 2026-10-08 to 2026-10-11 the slot held a copy of 708. Douglas,
2026-10-11 (art-track contract 8): the Avatar himself, scaled down, on the
Avatar's own animation table, with a shrink ramp. The picked candidate is
O60 with the R2 glow ramp and a scaled stride; lv_tiny_avatar_art.py holds
the derivation and the pick.

WHAT THIS BUILDS — one shape needs three files
----------------------------------------------
An actor shape is more than a sprite. ScummVM keys actor animation by shape
number in STATIC/ANIM.DAT (AnimDat::load, gfx/anim_dat.cpp), and
AnimationTracker refuses to move an actor whose shape has no entry. So 867
is written in all three places the engine looks:

  U8SHAPES.FLX  slot 867 = 1558 frames derived from shape 1 at build time
                (lv_tiny_avatar_art.build_tiny_avatar): shape 1's 1550
                frames scaled to 0.6 about their anchors, frames 60-69 the
                shrink ramp FREE.UNK steps through (60 = shape 1 frame 3,
                69 = the tiny stand south-east), and 1550-1557 shape 1's
                walk-SW frames 60-67, which the ramp displaces.
  TYPEFLAG.DAT  row 867 = 708's row (flags, family SF_CONTAINER, footpad
                (1,1,4) = 32x32x32 — the body the Map 18 crack admits —
                equip type, anim fields) with bytes 6-7, weight and volume,
                taken from shape 1, the Avatar: the disguise changes
                nothing about what the player carries. Unchanged by the
                2026-10-11 art.
  ANIM.DAT      867's OWN action table, appended to the file: shape 1's 53
                actions with frames 60-67 renumbered 1550-1557 and deltaDir
                scaled by 0.6 (lv_tiny_avatar_art.avatar_anim_table). The
                format is not a FLX: 2048 uint32 offsets (one per shape,
                0 = no anim), each to a 64-entry action table, each action
                a 4-byte header and 8 directions x size 6-byte frames.

clone_anim_entry() below is not used by this step any more; it is the
"keep the donor's layout" binding the Actor contract in docs/art-track.md
names for item 9 (Water Zombie, Harpie), whose art keeps its donor's frame
numbers.

ANIM.DAT becomes the fifth built artifact. It is built from the pristine
base every run, so re-running this step alone is safe for ANIM.DAT;
U8SHAPES and TYPEFLAG are the shared/build copies the earlier steps of
tools/build_artifacts.sh produced, and slot 867 must be empty there (run
the whole build, not this step twice).

All three outputs are written to `<artifact>.staging`, verified there, and
only then promoted with os.replace() (.claude/rules/build-artifacts.md). A
rejected build is quarantined as `<artifact>.failed` and the previous good
artifacts are left untouched.

Usage:
    python3 lv_tiny_avatar.py
"""

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shape_viewer import (read_flx_entry, load_palette,          # noqa: E402
                          SHAPES_FLX, PALETTE_FILE)
from lv_wood_wall import inject_shape, validate_shape, num_frames  # noqa: E402
from patch_typeflag import patch_entry_in_file, ENTRY_SIZE     # noqa: E402
from base_input import pristine_base                           # noqa: E402
import lv_tiny_avatar_art as art                               # noqa: E402
from lv_tiny_avatar_art import (anim_offset, anim_frame_refs,  # noqa: E402
                                ANIM_ACTIONS, ANIM_DIRS,
                                ANIM_FRAME_BYTES)

SHARED = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      '..', '..', '..', 'shared')
BUILD = os.path.join(SHARED, 'build')
OUT_SHAPES = os.path.join(BUILD, 'U8SHAPES.FLX')
OUT_TYPEFLAG = os.path.join(BUILD, 'TYPEFLAG.DAT')
OUT_ANIM = os.path.join(BUILD, 'ANIM.DAT')
BASE_ANIM = os.path.join(SHARED, 'data', 'u8-install', 'STATIC', 'ANIM.DAT')

TINY_AVATAR_ID = 867       # u8c_symbols TypeTinytar / TypeTinyAvatar
TYPEFLAG_DONOR = 708       # base child actor: its row, footpad (1,1,4)
AVATAR_SHAPE = 1           # the art, the animation table, weight/volume
TINY_FRAMES = 1558         # shape 1's 1550 + the 8 frames the ramp displaces


def actor_anim(data, shape):
    """Decode one shape's ActorAnim the way AnimDat::load does for U8.

    Returns None for a shape with no entry, else a 64-tuple holding, per
    action, None or the action's raw bytes (4-byte header plus 8 directions
    of `size` 6-byte frames). Two shapes whose tuples are equal animate
    identically. Raises where the engine would error(): a frame-repeat byte
    with its high nibble set."""
    off = anim_offset(data, shape)
    if off == 0:
        return None
    actions = []
    for action in range(ANIM_ACTIONS):
        aoff = struct.unpack_from('<I', data, off + 4 * action)[0]
        if aoff == 0:
            actions.append(None)
            continue
        size = data[aoff]
        if data[aoff + 2] & 0xF0:
            raise ValueError(f"shape {shape} action {action}: frame repeat "
                             f"byte {data[aoff + 2]:#x} > 0xf (engine error)")
        end = aoff + 4 + ANIM_DIRS * size * ANIM_FRAME_BYTES
        if end > len(data):
            raise ValueError(f"shape {shape} action {action} runs off the "
                             f"end of ANIM.DAT ({end} > {len(data)})")
        actions.append(bytes(data[aoff:end]))
    return tuple(actions)


def clone_anim_entry(data, new_id, src_id):
    """Return a copy of ANIM.DAT with shape new_id pointing at src_id's
    action table. Refuses an occupied new_id or an empty src_id."""
    if anim_offset(data, new_id):
        raise ValueError(f"ANIM.DAT shape {new_id} already has an entry")
    src = anim_offset(data, src_id)
    if not src:
        raise ValueError(f"ANIM.DAT donor shape {src_id} has no entry")
    out = bytearray(data)
    struct.pack_into('<I', out, 4 * new_id, src)
    return bytes(out)


def _anim_867_empty(path):
    with open(path, 'rb') as f:
        return anim_offset(f.read(), TINY_AVATAR_ID) == 0


def _verify(shapes_in, shapes_out, body_blob, tf_in, tf_out, tf_row,
            anim_in, anim_out, relocate):
    """Return a list of errors in the staged outputs; empty means promote."""
    errs = []

    # U8SHAPES: slot 867 is the derived body; nothing else moved.
    got = read_flx_entry(shapes_out, TINY_AVATAR_ID)
    if got != body_blob:
        errs.append(f"U8SHAPES slot {TINY_AVATAR_ID} is not the derived body")
    elif num_frames(got) != TINY_FRAMES:
        errs.append(f"U8SHAPES slot {TINY_AVATAR_ID} has {num_frames(got)} "
                    f"frames, expected {TINY_FRAMES}")
    count = struct.unpack_from('<I', shapes_in, 0x54)[0]
    if struct.unpack_from('<I', shapes_out, 0x54)[0] != count:
        errs.append("U8SHAPES entry count changed")
    slot = 0x80 + TINY_AVATAR_ID * 8
    if (shapes_out[:slot] != shapes_in[:slot]
            or shapes_out[slot + 8:len(shapes_in)] != shapes_in[slot + 8:]):
        errs.append("U8SHAPES bytes outside slot 867 changed")

    # TYPEFLAG: row 867 is exactly what was asked for; nothing else moved.
    lo, hi = TINY_AVATAR_ID * ENTRY_SIZE, (TINY_AVATAR_ID + 1) * ENTRY_SIZE
    if tf_out[lo:hi] != tf_row:
        errs.append(f"TYPEFLAG row {TINY_AVATAR_ID} is {tf_out[lo:hi].hex()}, "
                    f"expected {tf_row.hex()}")
    if tf_out[:lo] != tf_in[:lo] or tf_out[hi:] != tf_in[hi:]:
        errs.append("TYPEFLAG rows other than 867 changed")

    # ANIM.DAT: 867 has its own table, appended; the base bytes are intact.
    try:
        a_new = actor_anim(anim_out, TINY_AVATAR_ID)
        a_src = actor_anim(anim_out, AVATAR_SHAPE)
    except ValueError as e:
        errs.append(f"ANIM.DAT does not decode: {e}")
    else:
        if a_new is None or [a is None for a in a_new] != \
                [a is None for a in a_src]:
            errs.append(f"ANIM.DAT entry {TINY_AVATAR_ID} does not have "
                        f"shape {AVATAR_SHAPE}'s action set")
        refs = anim_frame_refs(anim_out, TINY_AVATAR_ID)
        if max(refs) >= TINY_FRAMES:
            errs.append(f"ANIM.DAT entry {TINY_AVATAR_ID} names frame "
                        f"{max(refs)}, past the body's {TINY_FRAMES}")
        ramp = sorted({r for r in refs
                       if art.RAMP_FIRST <= r <= art.RAMP_LAST})
        if ramp:
            errs.append(f"ANIM.DAT entry {TINY_AVATAR_ID} shows ramp frames "
                        f"{ramp} in an action")
    if relocate != {60 + i: 1550 + i for i in range(8)}:
        errs.append(f"the ramp displaced {sorted(relocate)}, expected "
                    f"shape 1's walk-SW frames 60-67")
    if anim_offset(anim_out, TINY_AVATAR_ID) != len(anim_in):
        errs.append("ANIM.DAT entry 867 does not point at the appended table")
    a = 4 * TINY_AVATAR_ID
    if (anim_out[:a] != anim_in[:a]
            or anim_out[a + 4:len(anim_in)] != anim_in[a + 4:]):
        errs.append("ANIM.DAT base bytes outside entry 867 changed")
    return errs


def main():
    print(f"=== LV Tiny Tar body (shape {TINY_AVATAR_ID} <- shape "
          f"{AVATAR_SHAPE} x {art.SCALE}, {art.METHOD}, glow {art.GLOW}) ===")
    for path in (OUT_SHAPES, OUT_TYPEFLAG):
        if not os.path.exists(path):
            raise SystemExit(f"{path} is missing — this step patches the "
                             f"artifact earlier build_artifacts.sh steps "
                             f"produce; run tools/build_artifacts.sh")

    # The source comes from the pristine base, as in lv_tiny_tar.py: shape
    # 1 is a base shape no LV step touches, so this is the same bytes
    # either way.
    base_shapes = open(pristine_base(SHAPES_FLX, None, 'base U8SHAPES.FLX'),
                       'rb').read()
    avatar_blob = read_flx_entry(base_shapes, AVATAR_SHAPE)
    if not avatar_blob or num_frames(avatar_blob) != 1550:
        raise SystemExit(f"shape {AVATAR_SHAPE} missing from the base or not "
                         f"1550 frames")
    anim_src = pristine_base(BASE_ANIM, _anim_867_empty, 'base ANIM.DAT')
    anim_in = open(anim_src, 'rb').read()

    body_blob, _frames, relocate, anim_out = art.build_tiny_avatar(
        avatar_blob, anim_in, load_palette(PALETTE_FILE))
    errs = validate_shape(body_blob)
    if errs:
        raise SystemExit(f"derived shape {TINY_AVATAR_ID} failed validation:"
                         f"\n  " + "\n  ".join(errs[:20]))
    print(f"  derived {num_frames(body_blob)} frames, {len(body_blob)} bytes, "
          f"validate_shape clean; ramp displaced {sorted(relocate)} -> "
          f"{sorted(relocate.values())}")

    shapes_in = open(OUT_SHAPES, 'rb').read()
    tf_in = open(OUT_TYPEFLAG, 'rb').read()

    av = tf_in[AVATAR_SHAPE * ENTRY_SIZE:(AVATAR_SHAPE + 1) * ENTRY_SIZE]
    weight, volume = av[6], av[7]

    staged = {p: p + '.staging' for p in (OUT_SHAPES, OUT_TYPEFLAG, OUT_ANIM)}
    for p in staged.values():
        if os.path.exists(p):
            os.remove(p)

    inject_shape(body_blob, TINY_AVATAR_ID, OUT_SHAPES, staged[OUT_SHAPES])

    with open(staged[OUT_TYPEFLAG], 'wb') as f:
        f.write(tf_in)
    _old, tf_row = patch_entry_in_file(staged[OUT_TYPEFLAG], TINY_AVATAR_ID,
                                       TYPEFLAG_DONOR,
                                       weight_volume=(weight, volume))
    print(f"  TYPEFLAG slot {TINY_AVATAR_ID} <- {TYPEFLAG_DONOR}, weight/volume "
          f"<- shape {AVATAR_SHAPE} ({weight}, {volume}): {tf_row.hex()}")

    with open(staged[OUT_ANIM], 'wb') as f:
        f.write(anim_out)
    print(f"  ANIM.DAT entry {TINY_AVATAR_ID}: own table at "
          f"{anim_offset(anim_out, TINY_AVATAR_ID):#x}, shape {AVATAR_SHAPE}'s "
          f"actions, stride x {art.STRIDE} ({len(anim_in)} -> {len(anim_out)} "
          f"bytes)")

    errs = _verify(shapes_in, open(staged[OUT_SHAPES], 'rb').read(),
                   body_blob, tf_in, open(staged[OUT_TYPEFLAG], 'rb').read(),
                   tf_row, anim_in, open(staged[OUT_ANIM], 'rb').read(),
                   relocate)
    if errs:
        for p, s in staged.items():
            if os.path.exists(s):
                os.replace(s, p + '.failed')
        raise SystemExit("staged outputs REJECTED (quarantined as .failed; "
                         "the previous artifacts are untouched):\n  "
                         + "\n  ".join(errs))
    print("  verified: 867 is the derived body with its own action table, "
          "TYPEFLAG row as intended, nothing else moved")

    for p, s in staged.items():
        os.replace(s, p)
        print(f"  promoted {os.path.relpath(p, SHARED)}")


if __name__ == '__main__':
    main()

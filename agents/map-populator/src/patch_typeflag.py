#!/usr/bin/env python3
"""
patch_typeflag.py — Patch TYPEFLAG.DAT for custom LV shape slots.

Each new shape slot must have a TYPEFLAG.DAT entry matching the shape it
stands in for, so the engine uses the correct 3D bounding box for depth-sort
and collision. Without this, new shapes sort incorrectly (the Avatar appears
behind walls it should stand in front of).

Skipping the patch is NOT the same as leaving a shape unconfigured. Every one
of the 2048 entries in the stock TYPEFLAG.DAT is populated: the 1189 slots
with no shape behind them all carry the identical filler entry
`12 00 10 01 10 01 01 00` — SI_SOLID | SI_OCCL with a (1,1,0) footpad. An
injected shape that never gets a TYPEFLAG entry therefore inherits a solid,
view-occluding, zero-height box rather than nothing at all.

TYPEFLAG.DAT: 2048 × 8 bytes, indexed by shape id. See parse_typeflag.py for
the field decode.

Remap (new slot ← copy from):
    856  ← 24    (SE wall panel)
    857  ← 20    (SW wall panel)
    858  ← 255   (corner post)

Slot 855 was once reserved here for a wood-plank floor tile (← 556); that
shape was never built and the id is unallocated — see lv_wood_wall.py.

Entries for art injected by tools/png2shape.py are written by that tool
through copy_entry() below, not listed in REMAP: png2shape patches the built
TYPEFLAG.DAT in place so a one-off injection does not need an edit here.
"""

import os, shutil

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    '..', '..', '..', 'shared')
SRC  = os.path.join(ROOT, 'data', 'u8-install', 'STATIC', 'TYPEFLAG.DAT')
DST  = os.path.join(ROOT, 'build', 'TYPEFLAG.DAT')

# new_shape_id → copy_from_shape_id
REMAP = {
    856: 24,    # wood SE wall             ← stone SE wall
    857: 20,    # wood SW wall             ← stone SW wall
    858: 255,   # wood corner post         ← stone corner post
}

ENTRY_SIZE = 8
NUM_ENTRIES = 2048

# The entry every unused slot carries in the stock file (see module docstring).
# Not a constant of the format — it is what this game data happens to contain —
# so it is used only to *report* whether a slot looked untouched, never to
# decide whether writing is safe.
FILLER_ENTRY = bytes.fromhex('1200100110010100')


def copy_entry(data, new_id, src_id):
    """Copy shape src_id's 8-byte entry over shape new_id's, in a bytearray.

    Returns (old_bytes, new_bytes) so the caller can report what it replaced —
    every unused slot already holds the filler entry, so "before" is never
    zeros and a silent overwrite would hide a mistake.
    """
    for sid in (new_id, src_id):
        if not 0 <= sid < NUM_ENTRIES:
            raise ValueError(f"shape id {sid} outside TYPEFLAG.DAT "
                             f"(0..{NUM_ENTRIES - 1})")
    src_off = src_id * ENTRY_SIZE
    dst_off = new_id * ENTRY_SIZE
    src_entry = bytes(data[src_off: src_off + ENTRY_SIZE])
    old_entry = bytes(data[dst_off: dst_off + ENTRY_SIZE])
    data[dst_off: dst_off + ENTRY_SIZE] = src_entry
    return old_entry, src_entry


def set_footpad(entry, fx, fy, fz):
    """Return entry with its 3D footpad replaced. The three sizes are packed
    as nibbles across bytes 2 and 3 (see ShapeInfo in parse_typeflag.py):
    byte2 = footpad_x << 4 | equiptype, byte3 = footpad_z << 4 | footpad_y.
    Everything else — flags, family, equip type, weight, volume — is left as
    it was, which is the point: a donor supplies the behaviour and only the
    box gets resized to the new art."""
    for name, v in (('x', fx), ('y', fy), ('z', fz)):
        if not 0 <= v <= 15:
            raise ValueError(f"footpad {name}={v} outside the 0..15 nibble")
    e = bytearray(entry)
    e[2] = (fx << 4) | (e[2] & 0x0F)
    e[3] = (fz << 4) | fy
    return bytes(e)


def set_anim(entry, anim_type, anim_data, anim_speed):
    """Return entry with its animation fields replaced.

    Byte 4 packs animData << 4 | animType; byte 5's low nibble is animSpeed,
    and its HIGH nibble carries four independent flags (SI_EDITOR,
    SI_U8_EXPLODE and two unknowns) which are preserved.

    ANIM SPEED IS A DIVISOR AND MUST NOT BE ZERO. The engine runs
    `if (animType && (gametick % animSpeed) == 0) animateItem()`
    (item.cpp:1778) — animType non-zero with animSpeed 0 divides by zero on
    the first frame the item is drawn. Shape 443, the gods' TYPEFLAG donor,
    happens to carry animSpeed 1 already, but nothing guarantees that for the
    next donor, so this refuses 0 rather than trusting it.

    animType 5 means "call the item's usecode anim() event", and the usecode
    class the engine calls is THE SHAPE NUMBER (item.cpp:1516,
    `uint32 class_id = _shape`). Seven retail shapes use it — HOURGLAS 227,
    DRIPS 348, FIREITEM 397, FIREFELD 400, CLRLAVA 409, BUBLAST 483,
    DRIPS2 653 — and every one has a usecode class at its own shape number.
    """
    for name, v, hi in (('anim_type', anim_type, 15),
                        ('anim_data', anim_data, 15),
                        ('anim_speed', anim_speed, 15)):
        if not 0 <= v <= hi:
            raise ValueError(f"{name}={v} outside the 0..{hi} nibble")
    if anim_type and not anim_speed:
        raise ValueError("anim_speed 0 with a non-zero anim_type divides by "
                         "zero in Item::setupLerp — use 1 for every tick")
    e = bytearray(entry)
    e[4] = (anim_data << 4) | anim_type
    e[5] = (e[5] & 0xF0) | anim_speed
    return bytes(e)


def set_weight_volume(entry, weight, volume):
    """Return entry with its weight (byte 6) and volume (byte 7) replaced.

    For an ACTOR shape these two bytes are not about picking the thing up:
    an Actor is a Container, and Container::getTotalWeight() and
    getCapacity() (container.cpp:219-245) start from the actor's OWN shape
    row. A body swapped in by usecode setType() therefore changes what the
    Avatar's pack weighs and holds — which is why the Tiny Tar body (867, a
    copy of 708) takes shape 1's pair (lv_tiny_avatar.py)."""
    for name, v in (('weight', weight), ('volume', volume)):
        if not 0 <= v <= 255:
            raise ValueError(f"{name}={v} outside the 0..255 byte")
    e = bytearray(entry)
    e[6] = weight
    e[7] = volume
    return bytes(e)


def patch_entry_in_file(path, new_id, src_id, footpad=None, anim=None,
                        weight_volume=None):
    """Apply copy_entry to an existing TYPEFLAG.DAT in place, optionally
    overriding the copied footpad, animation and weight/volume fields. Used
    by tools/png2shape.py, which patches one slot at a time rather than
    regenerating the whole file from the base game copy.

    `anim` is (anim_type, anim_data, anim_speed); see set_anim.
    `weight_volume` is (weight, volume); see set_weight_volume."""
    with open(path, 'rb') as f:
        data = bytearray(f.read())
    if len(data) != NUM_ENTRIES * ENTRY_SIZE:
        raise ValueError(f"{path} is {len(data)} bytes, expected "
                         f"{NUM_ENTRIES * ENTRY_SIZE}")
    old_entry, new_entry = copy_entry(data, new_id, src_id)
    if footpad is not None:
        new_entry = set_footpad(new_entry, *footpad)
    if anim is not None:
        new_entry = set_anim(new_entry, *anim)
    if weight_volume is not None:
        new_entry = set_weight_volume(new_entry, *weight_volume)
    data[new_id * ENTRY_SIZE: new_id * ENTRY_SIZE + ENTRY_SIZE] = new_entry
    with open(path, 'wb') as f:
        f.write(data)
    return old_entry, new_entry


def patch_typeflag(src=SRC, dst=DST):
    if src == SRC:
        # The install dir doubles as install_lv.sh's target; after an
        # install the "base" here is the previously built artifact. The
        # patch is idempotent for slots 856-858, but a hand-run injection
        # (png2shape) in the install dir would silently become canonical.
        from base_input import pristine_base
        src = pristine_base(SRC, None, 'base TYPEFLAG.DAT')
    shutil.copy2(src, dst)
    data = bytearray(open(dst, 'rb').read())

    for new_id, src_id in REMAP.items():
        _old, src_entry = copy_entry(data, new_id, src_id)
        print(f"  slot {new_id:4d} ← shape {src_id:4d}:  {src_entry.hex()}")

    with open(dst, 'wb') as f:
        f.write(data)
    print(f"Wrote {dst} ({len(data)} bytes)")


if __name__ == '__main__':
    print("=== Patching TYPEFLAG.DAT ===")
    patch_typeflag()
    print("Done.")

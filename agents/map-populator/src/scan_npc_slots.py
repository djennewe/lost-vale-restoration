#!/usr/bin/env python3
"""
scan_npc_slots.py — Scan U8SAVE.000/ITEMCACH.DAT for empty NPC slots.

U8SAVE.000 format (from ScummVM u8_save_file.cpp):
  - Bytes 0-22: "Ultima 8 SaveGame File." magic
  - Offset 0x18: uint16 LE file count
  - Then for each file:
      uint32 LE name_length
      char[name_length] name
      uint32 LE data_size
      byte[data_size] data

ITEMCACH.DAT inside U8SAVE.000 is a FLX archive. Object 0 contains
the NPC item cache. Shape for NPC slot i is at offset 0x0B400 + i*2
(uint16 LE). Slots with shape==0 are empty/unused.
"""

import struct
import sys
from pathlib import Path

# Add the usecode-disasm src for FlexArchive
sys.path.insert(0, str(Path(__file__).resolve().parent / "../../usecode-disasm/src"))
from u8_flex import FlexArchive


def read_u8save(path):
    """Parse U8SAVE.000 and return dict of {name: bytes}."""
    data = Path(path).read_bytes()

    magic = data[:23]
    assert magic == b"Ultima 8 SaveGame File.", f"Bad magic: {magic!r}"

    count = struct.unpack_from('<H', data, 0x18)[0]
    pos = 0x1A  # right after the count

    files = {}
    for _ in range(count):
        name_len = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        name = data[pos:pos + name_len].decode('ascii', errors='replace').rstrip('\x00')
        pos += name_len
        size = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        files[name] = data[pos:pos + size]
        pos += size

    return files


def main():
    save_path = Path(__file__).resolve().parent / "../../../shared/data/u8-install/SAVEGAME/U8SAVE.000"
    if not save_path.exists():
        print(f"ERROR: {save_path} not found")
        sys.exit(1)

    print(f"Reading {save_path}")
    files = read_u8save(save_path)

    print(f"Files in U8SAVE.000: {list(files.keys())}")

    itemcach_data = files.get("ITEMCACH.DAT")
    if itemcach_data is None:
        # Try case variations
        for k in files:
            if k.upper() == "ITEMCACH.DAT":
                itemcach_data = files[k]
                break
    if itemcach_data is None:
        print("ERROR: ITEMCACH.DAT not found in U8SAVE.000")
        sys.exit(1)

    print(f"ITEMCACH.DAT size: {len(itemcach_data)} bytes")

    # Parse as FLX
    flx = FlexArchive(itemcach_data)
    print(f"FLX entries: {flx.count}")
    obj0 = flx.get_object(0)
    print(f"Object 0 size: {len(obj0)} bytes")

    # Read all 255 NPC slots
    print(f"\n{'Slot':>4}  {'Shape':>6}  {'Frame':>5}  {'X':>6}  {'Y':>6}  {'Z':>3}  {'Map':>3}  {'Flags':>5}  Status")
    print("-" * 70)

    empty_slots = []
    occupied_slots = []

    for i in range(1, 256):
        shape_off = 0x0B400 + i * 2
        shape = struct.unpack_from('<H', obj0, shape_off)[0]

        if shape == 0:
            empty_slots.append(i)
        else:
            # Read additional info for occupied slots
            x = struct.unpack_from('<H', obj0, 0x00000 + i * 2)[0]
            y = struct.unpack_from('<H', obj0, 0x04800 + i * 2)[0]
            z = obj0[0x09000 + i]
            frame = obj0[0x0FC00 + i]
            flags = struct.unpack_from('<H', obj0, 0x12000 + i * 2)[0]
            mapnum = obj0[0x1D400 + i]
            occupied_slots.append((i, shape, frame, x, y, z, mapnum, flags))

    # Print occupied slots
    print("\n=== OCCUPIED NPC SLOTS ===")
    print(f"{'Slot':>4}  {'Shape':>6}  {'Frame':>5}  {'X':>6}  {'Y':>6}  {'Z':>3}  {'Map':>3}  {'Flags':>5}")
    print("-" * 55)
    for slot, shape, frame, x, y, z, mapnum, flags in occupied_slots:
        print(f"{slot:4d}  {shape:6d}  {frame:5d}  {x:6d}  {y:6d}  {z:3d}  {mapnum:3d}  0x{flags:04X}")

    # Print empty slots
    print(f"\n=== EMPTY NPC SLOTS (shape==0) ===")
    print(f"Total empty: {len(empty_slots)} out of 255")
    print(f"Empty slots: {empty_slots}")

    # Find contiguous ranges
    print(f"\n=== CONTIGUOUS EMPTY RANGES ===")
    ranges = []
    start = None
    for i, slot in enumerate(empty_slots):
        if start is None:
            start = slot
            end = slot
        elif slot == end + 1:
            end = slot
        else:
            ranges.append((start, end))
            start = slot
            end = slot
    if start is not None:
        ranges.append((start, end))

    for start, end in ranges:
        count = end - start + 1
        marker = " <-- GOOD for LV" if count >= 17 else ""
        print(f"  Slots {start:3d}-{end:3d}  ({count:2d} slots){marker}")

    # Specifically check slots 50-70 (current LV range)
    print(f"\n=== CURRENT LV RANGE (50-70) ===")
    for i in range(50, 71):
        status = "EMPTY" if i in empty_slots else "OCCUPIED"
        if i not in empty_slots:
            for slot, shape, frame, x, y, z, mapnum, flags in occupied_slots:
                if slot == i:
                    print(f"  Slot {i:3d}: {status} (shape={shape}, map={mapnum})")
                    break
        else:
            print(f"  Slot {i:3d}: {status}")

    # Suggest best range
    print(f"\n=== RECOMMENDATION ===")
    best = None
    for start, end in ranges:
        count = end - start + 1
        if count >= 17:
            if best is None or start >= 100:
                best = (start, end, count)
                if start >= 100:
                    break

    if best:
        start, end, count = best
        print(f"Best range: slots {start}-{start+16} ({17} slots from {count} available in {start}-{end})")
        print(f"This range is {'above' if start >= 100 else 'below'} slot 100.")
    else:
        print("No contiguous range of 17+ empty slots found!")
        print("May need to use non-contiguous slots.")


if __name__ == "__main__":
    main()

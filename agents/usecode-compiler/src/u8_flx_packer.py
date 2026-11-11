#!/usr/bin/env python3
"""
u8_flx_packer.py — Writer for Ultima 8 .FLX archive files.

Creates new or modifies existing EUSECODE.FLX archives. Companion to
u8_flex.py (reader) from the usecode-disasm agent.

FLX format:
  - 0x00-0x51: Title text + 0x1A padding
  - 0x52-0x53: Padding
  - 0x54-0x57: Entry count (uint32 LE)
  - 0x58-0x7F: Reserved (40 bytes)
  - 0x80+:     Index table (N * 8 bytes: offset + size per entry)
  - After index: Data area

USECODE.FLX layout:
  - Entry 0: unused (empty)
  - Entry 1: name table
  - Entry 2+: class bytecode (classid = entry - 2)

Name table format:
  - 4-byte header
  - N * 13-byte records: 9 bytes null-padded name + 4 bytes padding
"""

import struct
from pathlib import Path


class FlxPacker:
    """Build or modify a .FLX archive file."""

    HEADER_SIZE = 0x80
    TITLE_AREA = 0x52
    COUNT_OFFSET = 0x54
    RESERVED_SIZE = 0x28
    INDEX_OFFSET = 0x80
    ENTRY_SIZE = 8

    def __init__(self, title="Ultima 8 Usecode"):
        """Create a new FLX packer.

        Args:
            title: ASCII title string for the FLX header (max 80 chars)
        """
        self.title = title
        self.entries = {}  # index -> bytes (data for each entry)
        self._raw_header = None  # preserved raw header for round-trip
        self._original_offsets = {}  # index -> original file offset (for ordering)

    def set_entry(self, index, data):
        """Set the data for a given entry index.

        Args:
            index: FLX entry index (0-based)
            data: bytes or None (None = empty entry)
        """
        if data is None or len(data) == 0:
            if index in self.entries:
                del self.entries[index]
        else:
            self.entries[index] = bytes(data)

    def get_entry(self, index):
        """Get data for a given entry index, or None."""
        return self.entries.get(index)

    @property
    def count(self):
        """Number of entries (including empty slots)."""
        if not self.entries:
            return 0
        return max(self.entries.keys()) + 1

    def build(self):
        """Build the complete FLX archive as bytes.

        Returns:
            bytes: the complete FLX file
        """
        n_entries = self.count
        if n_entries == 0:
            # Empty FLX
            n_entries = 0

        # Build header
        if self._raw_header:
            # Use preserved raw header for round-trip fidelity
            header = bytearray(self._raw_header)
            # Update entry count (may have changed)
            struct.pack_into('<I', header, self.COUNT_OFFSET, n_entries)
        else:
            header = bytearray(self.HEADER_SIZE)

            # Title area (0x00-0x51): ASCII text + 0x1A padding
            title_bytes = self.title.encode('ascii', errors='replace')
            title_bytes = title_bytes[:self.TITLE_AREA - 1]  # leave room for 0x1A
            header[:len(title_bytes)] = title_bytes
            # Pad rest of title area with 0x1A
            for i in range(len(title_bytes), self.TITLE_AREA):
                header[i] = 0x1A

            # Entry count at 0x54
            struct.pack_into('<I', header, self.COUNT_OFFSET, n_entries)

            # Reserved area 0x58-0x7F is already zeroed

        # Build index table
        index_table = bytearray(n_entries * self.ENTRY_SIZE)

        # Calculate data area start
        data_start = self.HEADER_SIZE + len(index_table)

        # Determine entry write order: use original offsets for ordering
        # when available, otherwise append new entries at the end
        entries_with_data = []
        for i in range(n_entries):
            entry_data = self.entries.get(i)
            if entry_data and len(entry_data) > 0:
                orig_off = self._original_offsets.get(i, float('inf'))
                entries_with_data.append((orig_off, i, entry_data))

        # Sort by original offset (preserves original data layout)
        entries_with_data.sort(key=lambda x: x[0])

        # Build data area and fill index
        data_buf = bytearray()
        for _, i, entry_data in entries_with_data:
            offset = data_start + len(data_buf)
            size = len(entry_data)
            struct.pack_into('<II', index_table, i * self.ENTRY_SIZE,
                           offset, size)
            data_buf.extend(entry_data)

        # Empty entries stay as offset=0, size=0 (already zeroed)

        return bytes(header) + bytes(index_table) + bytes(data_buf)

    def write(self, path):
        """Write the FLX archive to a file.

        Args:
            path: output file path
        """
        data = self.build()
        Path(path).write_bytes(data)
        return len(data)

    def write_stealth(self, path, original_path):
        """Write FLX archive that passes ScummVM detection unchanged.

        ScummVM validates by md5-5000 AND file size. This method:
        1. Starts from an exact copy of the original file
        2. Keeps the first 5000 bytes byte-identical (entries 0-609 unchanged)
        3. Overwrites data space of entries 610+ with our modified/new class data
        4. Keeps the file at EXACTLY the original size

        Entries 0-609 retain their original data and index offsets.
        Entries 610+ get new data packed into the same data region,
        with their index entries updated (these are past byte 5000).

        Requires:
        - Entry count is unchanged
        - Modified/new entries all have index >= 610
        - Total new data fits in the space used by entries 610+ in the original

        Args:
            path: output file path
            original_path: path to original FLX file
        """
        original = Path(original_path).read_bytes()
        orig_count = struct.unpack_from('<I', original, self.COUNT_OFFSET)[0]
        orig_size = len(original)

        # Parse original index table
        orig_index = []
        for i in range(orig_count):
            off = self.INDEX_OFFSET + i * self.ENTRY_SIZE
            entry_off, entry_size = struct.unpack_from('<II', original, off)
            orig_index.append((entry_off, entry_size))

        # Build output: exact copy of original (all base game data intact)
        output = bytearray(original)

        # For entries 610+ that have MODIFIED data (existing entry with
        # different content), replace in-place using a free-space allocator.
        # For entries 610+ that are NEW (were empty in original), skip them
        # — there's no space without growing the file.
        #
        # Collect reclaimable space from entries we're replacing.
        modified_610 = {}
        skipped_new = []
        for i in range(610, orig_count):
            new_data = self.entries.get(i)
            if new_data is None or len(new_data) == 0:
                continue
            e_off, e_size = orig_index[i]
            if e_off > 0 and e_size > 0:
                # Existing entry — check if data changed
                orig_data = original[e_off:e_off + e_size]
                if new_data != orig_data:
                    modified_610[i] = new_data
            else:
                # New entry (was empty in original) — no space available
                skipped_new.append(i)

        if skipped_new:
            import sys
            print(f"  NOTE: {len(skipped_new)} new LV classes skipped "
                  f"(no space in stealth FLX). Entry range: "
                  f"{min(skipped_new)}-{max(skipped_new)}", file=sys.stderr)

        # Reclaimable space from modified entries
        reclaimable = []
        for i in modified_610:
            e_off, e_size = orig_index[i]
            reclaimable.append((e_off, e_size))
        reclaimable.sort()

        # Merge adjacent reclaimable regions
        merged = []
        for r_off, r_cap in reclaimable:
            if merged and merged[-1][0] + merged[-1][1] == r_off:
                merged[-1] = (merged[-1][0], merged[-1][1] + r_cap)
            else:
                merged.append((r_off, r_cap))

        # Place modified entries into reclaimable space
        for i in sorted(modified_610.keys()):
            data = modified_610[i]
            placed = False
            for r_idx, (r_off, r_cap) in enumerate(merged):
                if len(data) <= r_cap:
                    output[r_off:r_off + len(data)] = data
                    idx_off = self.INDEX_OFFSET + i * self.ENTRY_SIZE
                    struct.pack_into('<II', output, idx_off, r_off, len(data))
                    new_off = r_off + len(data)
                    new_cap = r_cap - len(data)
                    if new_cap > 0:
                        merged[r_idx] = (new_off, new_cap)
                    else:
                        merged.pop(r_idx)
                    placed = True
                    break
            if not placed:
                import sys
                print(f"  WARNING: Could not fit modified entry {i} "
                      f"({len(data)} bytes) into reclaimable space",
                      file=sys.stderr)

        assert len(output) == orig_size, \
            f"Output size {len(output)} != original {orig_size}"

        Path(path).write_bytes(output)
        return len(output)


class UsecodeFlxPacker(FlxPacker):
    """Specialized FLX packer for USECODE.FLX files.

    Handles the usecode-specific layout:
    - Entry 0: unused
    - Entry 1: name table
    - Entry 2+: class bytecode (classid = entry - 2)
    """

    CLASS_BASE_INDEX = 2
    NAME_TABLE_INDEX = 1
    NAME_RECORD_SIZE = 13
    NAME_HEADER_SIZE = 4
    NAME_LENGTH = 9

    def __init__(self, title="Ultima VIII - Usecode"):
        super().__init__(title)
        self._class_names = {}  # classid -> name string
        self._name_table_header = b'\x00\x00\x00\x00'  # default 4-byte header
        self._raw_name_table = None  # preserved for round-trip
        self._names_modified = False  # track if names changed

    def set_class_data(self, classid, data):
        """Set compiled bytecode for a usecode class.

        Args:
            classid: class ID (0x0000+)
            data: compiled class bytecode, or None to clear
        """
        self.set_entry(classid + self.CLASS_BASE_INDEX, data)

    def get_class_data(self, classid):
        """Get bytecode for a class, or None."""
        return self.get_entry(classid + self.CLASS_BASE_INDEX)

    def set_class_name(self, classid, name):
        """Set the name for a usecode class.

        Args:
            classid: class ID
            name: class name string (max 8 chars, will be truncated)
        """
        if name:
            self._class_names[classid] = name[:8]  # 8 chars + null = 9 bytes
        elif classid in self._class_names:
            del self._class_names[classid]
        self._names_modified = True

    def set_name_table_header(self, header_bytes):
        """Set the 4-byte header of the name table.

        Args:
            header_bytes: 4 bytes of header data
        """
        if len(header_bytes) != 4:
            raise ValueError("Name table header must be exactly 4 bytes")
        self._name_table_header = bytes(header_bytes)

    @property
    def class_count(self):
        """Number of class slots (may include empty)."""
        max_class = -1
        for idx in self.entries:
            if idx >= self.CLASS_BASE_INDEX:
                classid = idx - self.CLASS_BASE_INDEX
                if classid > max_class:
                    max_class = classid
        for classid in self._class_names:
            if classid > max_class:
                max_class = classid
        return max_class + 1 if max_class >= 0 else 0

    def _build_name_table(self):
        """Build the name table entry data.

        If names haven't been modified and we have the raw table, return it as-is.
        Otherwise builds from scratch:
        Format: 4-byte header + N * 13-byte records
        Each record: 9 bytes null-padded name + 4 bytes zero padding
        """
        # Use raw name table for exact round-trip when not modified
        if not self._names_modified and self._raw_name_table:
            return self._raw_name_table

        n_classes = self.class_count
        if n_classes == 0:
            return self._name_table_header

        buf = bytearray(self._name_table_header)
        for classid in range(n_classes):
            record = bytearray(self.NAME_RECORD_SIZE)
            name = self._class_names.get(classid, '')
            if name:
                name_bytes = name.encode('ascii', errors='replace')[:self.NAME_LENGTH - 1]
                record[:len(name_bytes)] = name_bytes
                # Rest is zero-padded (already zeroed)
            buf.extend(record)

        return bytes(buf)

    def build(self):
        """Build the complete USECODE.FLX archive.

        Automatically builds the name table from registered class names.
        """
        # Build name table and set as entry 1
        name_table = self._build_name_table()
        self.set_entry(self.NAME_TABLE_INDEX, name_table)

        # Ensure entry 0 exists (even if empty)
        if 0 not in self.entries:
            self.entries[0] = b''

        return super().build()

    @classmethod
    def from_existing(cls, flx_reader):
        """Create a packer from an existing UsecodeFlexArchive reader.

        Args:
            flx_reader: UsecodeFlexArchive instance (from u8_flex.py)

        Returns:
            UsecodeFlxPacker with all data copied from the reader
        """
        packer = cls(title=flx_reader.title)

        # Preserve the raw header (including reserved area) for round-trip
        packer._raw_header = bytes(flx_reader._data[:cls.INDEX_OFFSET])

        # Copy all entries and track original offsets
        for i, offset, size in flx_reader.entries():
            if size > 0:
                data = flx_reader.get_object(i)
                if data:
                    packer.set_entry(i, data)
                    packer._original_offsets[i] = offset

        # Store the raw name table for exact round-trip
        name_data = flx_reader.get_object(cls.NAME_TABLE_INDEX)
        if name_data:
            packer._raw_name_table = bytes(name_data)
        else:
            packer._raw_name_table = None

        # Also parse class names for modification purposes
        if name_data and len(name_data) >= cls.NAME_HEADER_SIZE:
            packer._name_table_header = bytes(name_data[:cls.NAME_HEADER_SIZE])
            offset = cls.NAME_HEADER_SIZE
            classid = 0
            # NAME_LENGTH, not NAME_RECORD_SIZE: the base game's table ends
            # in a TRUNCATED record — 18603 bytes = 4 + 1430*13 + 9, i.e. the
            # last class (1430, AIRSPEL) carries its 9 name bytes with the 4
            # trailing pad bytes omitted. The reader tolerates that
            # (u8_flex.get_class_name only needs the 9), so requiring a full
            # 13-byte record here silently dropped that one name, and every
            # build that touches any class name rebuilt the table without it.
            while offset + cls.NAME_LENGTH <= len(name_data):
                name_bytes = name_data[offset:offset + cls.NAME_LENGTH]
                null_pos = name_bytes.find(0)
                if null_pos >= 0:
                    name_bytes = name_bytes[:null_pos]
                name = name_bytes.decode('ascii', errors='replace').strip()
                if name:
                    packer._class_names[classid] = name
                offset += cls.NAME_RECORD_SIZE
                classid += 1

        packer._names_modified = False
        return packer

    def replace_class(self, classid, new_data, name=None):
        """Replace a class's bytecode (and optionally name).

        Args:
            classid: class ID to replace
            new_data: new compiled bytecode
            name: optional new class name
        """
        self.set_class_data(classid, new_data)
        if name is not None:
            self.set_class_name(classid, name)

    def add_new_class(self, classid, data, name):
        """Add a new class at a specific ID.

        Args:
            classid: class ID for the new class
            data: compiled bytecode
            name: class name
        """
        self.set_class_data(classid, data)
        self.set_class_name(classid, name)


def roundtrip_test_flx(input_path, output_path=None):
    """Test: read a FLX, rebuild it, compare.

    This validates the packer against the reader.
    """
    import os
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from u8_flex import UsecodeFlexArchive

    reader = UsecodeFlexArchive(input_path)
    packer = UsecodeFlxPacker.from_existing(reader)

    rebuilt = packer.build()
    original = Path(input_path).read_bytes()

    if rebuilt == original:
        print(f"FLX round-trip: PASS ({len(original)} bytes)")
        return True
    else:
        print(f"FLX round-trip: FAIL")
        print(f"  Original: {len(original)} bytes")
        print(f"  Rebuilt:  {len(rebuilt)} bytes")

        # Find first difference
        min_len = min(len(original), len(rebuilt))
        for i in range(min_len):
            if original[i] != rebuilt[i]:
                print(f"  First diff at offset 0x{i:04X}: "
                      f"orig=0x{original[i]:02X} rebuilt=0x{rebuilt[i]:02X}")
                # Show context
                start = max(0, i - 8)
                end = min(min_len, i + 8)
                print(f"  Orig [{start:04X}]: {' '.join(f'{original[j]:02X}' for j in range(start, end))}")
                print(f"  Rebt [{start:04X}]: {' '.join(f'{rebuilt[j]:02X}' for j in range(start, end))}")
                break
        if len(original) != len(rebuilt):
            print(f"  Size difference: {len(rebuilt) - len(original):+d} bytes")

        if output_path:
            Path(output_path).write_bytes(rebuilt)
            print(f"  Wrote rebuilt to {output_path}")

        return False


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: u8_flx_packer.py <command> [args...]")
        print("Commands:")
        print("  test <input.flx>         Round-trip test")
        print("  info <input.flx>         Show FLX info")
        print("  rebuild <in.flx> <out.flx>  Rebuild FLX (for testing)")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'test':
        roundtrip_test_flx(sys.argv[2])
    elif cmd == 'info':
        from u8_flex import UsecodeFlexArchive
        flx = UsecodeFlexArchive(sys.argv[2])
        print(f"FLX: {flx}")
        print(f"Entries: {flx.count}")
        non_empty = sum(1 for i, o, s in flx.entries() if s > 0)
        print(f"Non-empty: {non_empty}")
    elif cmd == 'rebuild':
        from u8_flex import UsecodeFlexArchive
        reader = UsecodeFlexArchive(sys.argv[2])
        packer = UsecodeFlxPacker.from_existing(reader)
        size = packer.write(sys.argv[3])
        print(f"Wrote {size} bytes to {sys.argv[3]}")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

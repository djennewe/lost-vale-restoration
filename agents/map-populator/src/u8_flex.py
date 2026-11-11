#!/usr/bin/env python3
"""
u8_flex.py — Reader for Ultima 8 .FLX archive files.

FLX is the container format used by all U8 data files, including USECODE.FLX.
Format documented in agents/usecode-disasm/docs/usecode-format.md.

Usage:
    from u8_flex import FlexArchive
    flx = FlexArchive("USECODE.FLX")
    data = flx.get_object(index)
    for i, (offset, size) in flx.entries():
        ...
"""

import struct
from pathlib import Path


class FlexArchive:
    """Read-only access to a .FLX archive file."""

    HEADER_SIZE = 0x80  # fixed header before index table
    TITLE_END = 0x52    # title area is bytes 0x00–0x51
    COUNT_OFFSET = 0x54
    INDEX_OFFSET = 0x80
    ENTRY_SIZE = 8      # each index entry: uint32 offset + uint32 size

    def __init__(self, path):
        """Open a FLX archive from a file path or bytes."""
        if isinstance(path, (str, Path)):
            self._data = Path(path).read_bytes()
        elif isinstance(path, (bytes, bytearray, memoryview)):
            self._data = bytes(path)
        else:
            raise TypeError(f"Expected path or bytes, got {type(path)}")

        if not self.is_valid_flex(self._data):
            raise ValueError("Not a valid FLX file")

        self._count = struct.unpack_from('<I', self._data, self.COUNT_OFFSET)[0]

    @classmethod
    def write(cls, path, objects, header=None):
        """Write sequential objects, preserving a supplied archive header."""
        objects = list(objects)
        if header is None:
            header = b'Lost Vale' + b'\x1a' * (0x52 - 9) + bytes(0x80 - 0x52)
        if len(header) != cls.HEADER_SIZE or not cls.is_valid_flex(header):
            raise ValueError('invalid FLX header')
        data = bytearray(header)
        struct.pack_into('<I', data, cls.COUNT_OFFSET, len(objects))
        data.extend(bytes(cls.ENTRY_SIZE * len(objects)))
        for i, obj in enumerate(objects):
            if obj:
                struct.pack_into('<II', data, cls.INDEX_OFFSET + i * cls.ENTRY_SIZE,
                                 len(data), len(obj))
                data.extend(obj)
        Path(path).write_bytes(data)

    @staticmethod
    def is_valid_flex(data):
        """Check if data begins with a valid FLX header."""
        if len(data) < 0x80:
            return False
        # Title area: find first 0x1A, then all remaining bytes must be 0x1A
        found_marker = False
        for i in range(0x52):
            if data[i] == 0x1A:
                found_marker = True
            elif found_marker:
                return False  # non-0x1A byte after first 0x1A
        return found_marker

    @property
    def count(self):
        """Number of entries in the archive."""
        return self._count

    @property
    def title(self):
        """Title string from the FLX header."""
        end = self._data.index(0x1A) if 0x1A in self._data[:0x52] else 0x52
        return self._data[:end].decode('ascii', errors='replace').rstrip()

    def _get_entry(self, index):
        """Return (offset, size) for the given index."""
        if index < 0 or index >= self._count:
            raise IndexError(f"Index {index} out of range (0–{self._count-1})")
        base = self.INDEX_OFFSET + self.ENTRY_SIZE * index
        offset, size = struct.unpack_from('<II', self._data, base)
        return offset, size

    def get_size(self, index):
        """Return the size of object at index, or 0 if empty."""
        offset, size = self._get_entry(index)
        return size

    def get_object(self, index):
        """Return the raw bytes of the object at index, or None if empty."""
        offset, size = self._get_entry(index)
        if size == 0:
            return None
        return self._data[offset:offset + size]

    def exists(self, index):
        """Check if an entry exists (has non-zero size)."""
        try:
            return self.get_size(index) > 0
        except IndexError:
            return False

    def entries(self):
        """Yield (index, offset, size) for all entries."""
        for i in range(self._count):
            offset, size = self._get_entry(i)
            yield i, offset, size

    def __len__(self):
        return self._count

    def __getitem__(self, index):
        return self.get_object(index)

    def __repr__(self):
        return f"FlexArchive(count={self._count}, title={self.title!r})"


class UsecodeFlexArchive(FlexArchive):
    """Specialized FLX reader for USECODE.FLX files.

    Knows about the U8 usecode layout:
    - Entry 0: unused
    - Entry 1: name table
    - Entries 2+: usecode classes (classid = entry - 2)
    """

    NAME_TABLE_INDEX = 1
    CLASS_BASE_INDEX = 2
    NAME_RECORD_SIZE = 13  # bytes per name record
    NAME_HEADER_SIZE = 4   # bytes before first name record
    NAME_LENGTH = 9        # max name string length

    @property
    def class_count(self):
        """Number of usecode classes (may include empty slots)."""
        return max(0, self.count - self.CLASS_BASE_INDEX)

    def get_class_data(self, classid):
        """Return raw bytecode for a usecode class, or None if empty."""
        return self.get_object(classid + self.CLASS_BASE_INDEX)

    def get_class_size(self, classid):
        """Return the size of a usecode class entry."""
        return self.get_size(classid + self.CLASS_BASE_INDEX)

    def class_exists(self, classid):
        """Check if a usecode class has data."""
        return self.exists(classid + self.CLASS_BASE_INDEX)

    def get_class_name(self, classid):
        """Return the name of a usecode class from the name table."""
        name_data = self.get_object(self.NAME_TABLE_INDEX)
        if name_data is None:
            return None

        offset = self.NAME_HEADER_SIZE + classid * self.NAME_RECORD_SIZE
        if offset + self.NAME_LENGTH > len(name_data):
            return None

        name_bytes = name_data[offset:offset + self.NAME_LENGTH]
        # Null-terminated string
        null_pos = name_bytes.find(0)
        if null_pos >= 0:
            name_bytes = name_bytes[:null_pos]
        name = name_bytes.decode('ascii', errors='replace').strip()
        return name if name else None

    def all_class_names(self):
        """Yield (classid, name) for all classes that have names."""
        for classid in range(self.class_count):
            name = self.get_class_name(classid)
            if name:
                yield classid, name

    def all_classes(self):
        """Yield (classid, name, data) for all non-empty classes."""
        for classid in range(self.class_count):
            if self.class_exists(classid):
                name = self.get_class_name(classid)
                data = self.get_class_data(classid)
                yield classid, name, data


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: u8_flex.py <file.flx> [--names] [--dump INDEX]")
        sys.exit(1)

    path = sys.argv[1]
    flx = FlexArchive(path)
    print(f"FLX: {flx}")

    if '--names' in sys.argv and isinstance(flx, UsecodeFlexArchive):
        for classid, name in flx.all_class_names():
            print(f"  {classid:04X}: {name}")
    elif '--dump' in sys.argv:
        idx = int(sys.argv[sys.argv.index('--dump') + 1])
        data = flx.get_object(idx)
        if data:
            print(f"Entry {idx}: {len(data)} bytes")
            # hex dump first 256 bytes
            for off in range(0, min(256, len(data)), 16):
                hexb = ' '.join(f'{b:02X}' for b in data[off:off+16])
                ascii_repr = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[off:off+16])
                print(f"  {off:04X}: {hexb:<48s} {ascii_repr}")
        else:
            print(f"Entry {idx}: empty")
    else:
        print(f"Entries: {flx.count}")
        non_empty = sum(1 for i, o, s in flx.entries() if s > 0)
        print(f"Non-empty: {non_empty}")
        total_size = sum(s for i, o, s in flx.entries())
        print(f"Total data: {total_size} bytes")

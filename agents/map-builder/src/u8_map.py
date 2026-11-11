#!/usr/bin/env python3
"""
u8_map.py — Reader/writer for Ultima 8 FIXED.DAT map files.

Extends the FLX reader to parse and manipulate map item records.
See docs/map-format.md for the format specification.

Usage:
    from u8_map import MapArchive, MapItem
    archive = MapArchive("FIXED.DAT")

    # Read a map
    items = archive.get_map_items(8)
    for item in items:
        print(f"shape={item.shape} pos=({item.x},{item.y},{item.z})")

    # Write a new map
    items = [
        MapItem(x=511, y=511, z=0, shape=2, frame=0, quality=1757),  # glob egg
        MapItem.teleport_target(x=1024, y=1024, z=0, teleport_id=200),
        MapItem.teleporter(x=1024, y=2048, z=0, teleport_id=200,
                              dest_npc=100, dest_map=9),
    ]
    archive.set_map_items(10, items)
    archive.save("FIXED_MODIFIED.DAT")
"""

import struct
from pathlib import Path
from u8_flex import FlexArchive


class MapItem:
    """A single item record from a U8 map (16 bytes)."""

    RECORD_SIZE = 16

    # Special shape numbers
    SHAPE_GLOB_EGG = 2
    SHAPE_STANDARD_EGG = 73
    SHAPE_MONSTER_EGG = 500
    SHAPE_TELEPORT_EGG = 508

    def __init__(self, x=0, y=0, z=0, shape=0, frame=0,
                 flags=0, quality=0, npcnum=0, mapnum=0, next_ptr=0):
        self.x = x
        self.y = y
        self.z = z
        self.shape = shape
        self.frame = frame
        self.flags = flags
        self.quality = quality
        self.npcnum = npcnum
        self.mapnum = mapnum
        self.next_ptr = next_ptr

    @classmethod
    def from_bytes(cls, data, offset=0):
        """Parse a 16-byte item record."""
        x = struct.unpack_from('<h', data, offset)[0]
        y = struct.unpack_from('<h', data, offset + 2)[0]
        z = struct.unpack_from('<b', data, offset + 4)[0]
        shape = struct.unpack_from('<H', data, offset + 5)[0]
        frame = data[offset + 7]
        flags = struct.unpack_from('<H', data, offset + 8)[0]
        quality = struct.unpack_from('<H', data, offset + 10)[0]
        npcnum = data[offset + 12]
        mapnum = data[offset + 13]
        next_ptr = struct.unpack_from('<H', data, offset + 14)[0]
        return cls(x, y, z, shape, frame, flags, quality, npcnum, mapnum, next_ptr)

    def to_bytes(self):
        """Serialize to a 16-byte record."""
        return struct.pack('<hhbHBHHBBH',
                           self.x, self.y, self.z,
                           self.shape, self.frame,
                           self.flags, self.quality,
                           self.npcnum, self.mapnum,
                           self.next_ptr)

    @classmethod
    def glob_egg(cls, x, y, z=0, glob_index=0):
        """Create a glob egg item."""
        return cls(x=x, y=y, z=z, shape=cls.SHAPE_GLOB_EGG,
                   frame=0, quality=glob_index)

    @classmethod
    def teleport_target(cls, x, y, z=0, teleport_id=0):
        """Create a teleport trigger egg (frame=1)."""
        return cls(x=x, y=y, z=z, shape=cls.SHAPE_TELEPORT_EGG,
                   frame=1, quality=teleport_id)

    @classmethod
    def teleporter(cls, x, y, z=0, teleport_id=0,
                      dest_npc=0, dest_map=0):
        """Create a teleport destination egg (frame=0)."""
        return cls(x=x, y=y, z=z, shape=cls.SHAPE_TELEPORT_EGG,
                   frame=0, quality=256 + teleport_id,
                   npcnum=dest_npc, mapnum=dest_map)

    @classmethod
    def monster_egg(cls, x, y, z=0, monster_quality=0,
                    count=1, activity_map=0):
        """Create a monster spawn egg."""
        return cls(x=x, y=y, z=z, shape=cls.SHAPE_MONSTER_EGG,
                   frame=0, quality=monster_quality,
                   npcnum=count, mapnum=activity_map)

    @classmethod
    def placed_item(cls, x, y, z=0, shape=0, frame=0, quality=0):
        """Create a generic placed item."""
        return cls(x=x, y=y, z=z, shape=shape, frame=frame, quality=quality)

    @property
    def is_glob_egg(self):
        return self.shape == self.SHAPE_GLOB_EGG

    @property
    def is_teleport_egg(self):
        return self.shape == self.SHAPE_TELEPORT_EGG

    @property
    def is_monster_egg(self):
        return self.shape == self.SHAPE_MONSTER_EGG

    @property
    def is_teleport_target(self):
        return self.is_teleport_egg and self.frame == 1

    @property
    def is_teleporter(self):
        return self.is_teleport_egg and self.frame == 0

    def __repr__(self):
        if self.is_glob_egg:
            return f"MapItem(glob={self.quality}, pos=({self.x},{self.y},{self.z}))"
        elif self.is_teleport_target:
            return f"MapItem(tele_trigger={self.quality}, pos=({self.x},{self.y},{self.z}))"
        elif self.is_teleporter:
            return f"MapItem(tele_dest npc={self.npcnum} map={self.mapnum}, pos=({self.x},{self.y},{self.z}))"
        elif self.is_monster_egg:
            return f"MapItem(monster q={self.quality}, pos=({self.x},{self.y},{self.z}))"
        else:
            return f"MapItem(shape={self.shape} f={self.frame}, pos=({self.x},{self.y},{self.z}), q={self.quality})"


class MapArchive:
    """Read/write access to a FIXED.DAT map archive."""

    MAP_COUNT = 256

    def __init__(self, path=None):
        """Open an existing FIXED.DAT or create a new empty archive."""
        self._maps = {}  # map_num -> list of MapItem

        if path is not None:
            path = Path(path)
            if path.exists():
                self._load(path)

    def _load(self, path):
        """Load all maps from a FIXED.DAT file."""
        flx = FlexArchive(path)
        for i in range(min(flx.count, self.MAP_COUNT)):
            data = flx.get_object(i)
            if data and len(data) >= MapItem.RECORD_SIZE:
                items = []
                for offset in range(0, len(data), MapItem.RECORD_SIZE):
                    if offset + MapItem.RECORD_SIZE <= len(data):
                        items.append(MapItem.from_bytes(data, offset))
                if items:
                    self._maps[i] = items

    def get_map_items(self, map_num):
        """Return list of MapItems for a map, or empty list."""
        return list(self._maps.get(map_num, []))

    def set_map_items(self, map_num, items):
        """Set the items for a map."""
        if items:
            self._maps[map_num] = list(items)
        elif map_num in self._maps:
            del self._maps[map_num]

    def add_items(self, map_num, items):
        """Append items to an existing map."""
        existing = self._maps.get(map_num, [])
        existing.extend(items)
        self._maps[map_num] = existing

    def get_map_count(self, map_num):
        """Return number of items in a map."""
        return len(self._maps.get(map_num, []))

    def non_empty_maps(self):
        """Return sorted list of map numbers that have items."""
        return sorted(self._maps.keys())

    def save(self, path):
        """Write the archive to a new FIXED.DAT file."""
        path = Path(path)

        # Build map data blobs
        map_blobs = {}
        for map_num, items in self._maps.items():
            if items:
                map_blobs[map_num] = b''.join(item.to_bytes() for item in items)

        # Calculate layout
        title = b'Ultima 8 Map Data\x1a'
        title = title.ljust(0x52, b'\x1a')

        header = bytearray(0x80)
        header[:len(title)] = title
        struct.pack_into('<I', header, 0x54, self.MAP_COUNT)

        # Index table
        index_size = self.MAP_COUNT * 8
        data_start = 0x80 + index_size

        index_table = bytearray(index_size)
        data_parts = []
        current_offset = data_start

        for i in range(self.MAP_COUNT):
            blob = map_blobs.get(i, b'')
            if blob:
                struct.pack_into('<II', index_table, i * 8,
                                 current_offset, len(blob))
                data_parts.append(blob)
                current_offset += len(blob)

        # Write file
        with open(path, 'wb') as f:
            f.write(header)
            f.write(index_table)
            for part in data_parts:
                f.write(part)

    def summary(self):
        """Print a summary of the archive."""
        maps = self.non_empty_maps()
        total = sum(self.get_map_count(m) for m in maps)
        print(f"Maps: {len(maps)} non-empty out of {self.MAP_COUNT}")
        print(f"Total items: {total}")
        for m in maps:
            count = self.get_map_count(m)
            items = self.get_map_items(m)
            globs = sum(1 for i in items if i.is_glob_egg)
            teles = sum(1 for i in items if i.is_teleport_egg)
            mons = sum(1 for i in items if i.is_monster_egg)
            print(f"  Map {m:3d}: {count:5d} items "
                  f"(globs={globs}, teleports={teles}, monsters={mons})")


def generate_terrain_grid(x_start, y_start, x_chunks, y_chunks,
                          glob_index, chunk_size=512):
    """Generate a grid of glob eggs to tile terrain.

    Args:
        x_start, y_start: starting coordinates (world units)
        x_chunks, y_chunks: number of chunks in each direction
        glob_index: which glob from GLOB.FLX to use
        chunk_size: size of each chunk (default 512)

    Returns:
        list of MapItem glob eggs
    """
    items = []
    for cx in range(x_chunks):
        for cy in range(y_chunks):
            x = x_start + cx * chunk_size + (chunk_size - 1)
            y = y_start + cy * chunk_size + (chunk_size - 1)
            items.append(MapItem.glob_egg(x, y, 0, glob_index))
    return items


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: u8_map.py <FIXED.DAT> [--summary] [--map N]")
        sys.exit(1)

    path = sys.argv[1]
    archive = MapArchive(path)

    if '--summary' in sys.argv:
        archive.summary()
    elif '--map' in sys.argv:
        idx = sys.argv.index('--map')
        map_num = int(sys.argv[idx + 1])
        items = archive.get_map_items(map_num)
        print(f"Map {map_num}: {len(items)} items")
        for i, item in enumerate(items[:50]):
            print(f"  {i:4d}: {item}")
        if len(items) > 50:
            print(f"  ... ({len(items) - 50} more)")
    else:
        archive.summary()

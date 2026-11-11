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

import os
import struct
import tempfile
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

    # Item flag bits (engine: world/item.h)
    FLG_CONTAINED = 0x0008

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
        # z is UNSIGNED on disk (H4). The engine reads it as a uint8
        # (0..255); 6,229 base-game items carry raw z > 127. Reading it
        # signed ('<b') mis-parsed those as negative and made the validator's
        # z-ceiling check dead code. Read unsigned to match the engine.
        z = struct.unpack_from('<B', data, offset + 4)[0]
        shape = struct.unpack_from('<H', data, offset + 5)[0]
        frame = data[offset + 7]
        flags = struct.unpack_from('<H', data, offset + 8)[0]
        quality = struct.unpack_from('<H', data, offset + 10)[0]
        npcnum = data[offset + 12]
        mapnum = data[offset + 13]
        next_ptr = struct.unpack_from('<H', data, offset + 14)[0]
        return cls(x, y, z, shape, frame, flags, quality, npcnum, mapnum, next_ptr)

    def to_bytes(self):
        """Serialize to a 16-byte record.

        z is written as an UNSIGNED byte (H4), matching the engine. Two
        idioms both land correctly through the mask: a direct 0..255 value,
        and the builders' negative "below-datum" shorthand (z=-2 -> 254),
        which the old signed pack happened to produce and which stays
        byte-identical here. A z outside [-128, 255] is a computation bug,
        not either idiom, so it raises rather than silently wrapping to a
        ceiling-height byte.
        """
        if not (-128 <= self.z <= 255):
            raise ValueError(
                f"z={self.z} out of serializable range [-128, 255] "
                f"(shape {self.shape} at {self.x},{self.y})")
        return struct.pack('<hhBHBHHBBH',
                           self.x, self.y, self.z & 0xFF,
                           self.shape, self.frame,
                           self.flags, self.quality,
                           self.npcnum, self.mapnum,
                           self.next_ptr)

    @classmethod
    def glob_egg(cls, x, y, z=0, glob_index=0):
        """Create a glob egg item."""
        return cls(x=x, y=y, z=z, shape=cls.SHAPE_GLOB_EGG,
                   frame=0, quality=glob_index)

    # Teleport eggs come in two halves, and the engine decides which is
    # which by FRAME (ultima8/world/teleport_egg.h):
    #
    #     bool isTeleporter() const { return _frame != 1; }
    #
    # so frame 0 is the TELEPORTER (the trigger the Avatar walks into) and
    # frame 1 is the TARGET (the arrival pad). TeleportEgg::hatch() reads
    # the *teleporter's* _mapNum as the destination map and _quality & 0xFF
    # as the teleport id; the target is matched by id on that map.
    #
    # These two factories were named the other way round until 2026-07-28
    # (`teleport_trigger` made the frame-1 pad, `teleport_dest` made the
    # frame-0 trigger). The emitted bytes were always correct — only the
    # names lied — so the rename changed no map data. See
    # docs/playtest-2026-07-28-cleanroom-run1.md finding F1.

    @classmethod
    def teleport_target(cls, x, y, z=0, teleport_id=0):
        """Create a teleport TARGET egg (frame=1) — the arrival pad.

        Matched by `teleport_id` (quality & 0xFF) on the map it sits on.
        """
        return cls(x=x, y=y, z=z, shape=cls.SHAPE_TELEPORT_EGG,
                   frame=1, quality=teleport_id)

    @classmethod
    def teleporter(cls, x, y, z=0, teleport_id=0,
                   dest_npc=0, dest_map=0):
        """Create a TELEPORTER egg (frame=0) — the trigger.

        `dest_map` lands in the mapNum field (the destination map) and
        `teleport_id` in the quality low byte (which target to arrive at).
        `dest_npc` lands in the npcNum field, which for an egg is NOT an NPC
        number but its hatch range: x range = (npcNum >> 4) * 32, y range =
        (npcNum & 0xF) * 32 (Egg::getXRange/getYRange).
        """
        return cls(x=x, y=y, z=z, shape=cls.SHAPE_TELEPORT_EGG,
                   frame=0, quality=256 + teleport_id,
                   npcnum=dest_npc, mapnum=dest_map)

    @classmethod
    def monster_egg(cls, x, y, z=0, monster_shape=0, prob=6,
                    count=1, activity=0, group=0, one_shot=False):
        """Create a monster spawn egg (shape 500).

        The engine (ScummVM MonsterEgg) decodes the quality word as
        (prob<<11)|monster_shape:
            getMonsterShape() = quality & 0x7FF   -> the U8 actor shape
            getProb()         = (quality>>11) & 0x1F  -> spawn chance 0..31
        and the mapNum byte as (group<<3)|activity:
            getActivity()     = mapNum & 0x07  (0 loiter, 1 combat, 2 stand)
            getMonId()        = mapNum >> 3    (the hatch group)

        A shape-500 egg never hatches on its own: MonsterEgg is not an Egg,
        so the EggHatcherProcess never sees it. A MONEGG trigger
        (`monster_trigger`) hatches every egg of its `group` within its
        area search. Neither the engine nor MONEGG reads `prob`.

        `one_shot` sets frame 1: MONEGG destroys a hatched egg whose frame
        is not 0 (0481:00EC-00FB), so it hatches once per visit. A FIXED
        egg comes back when the map is next loaded (World::loadMap reloads
        FIXED), as every FIXED item does; frame 0 hatches again each time
        its trigger re-enters the fast area.

        Passing a raw small number as the whole quality (the pre-2026-07-24
        bug, M12) set prob=0 (egg never hatches) and named a terrain shape,
        so the harpie zone / lair / elemental sections spawned nothing.
        Pass a real monster shape (see lv_shapes.SHAPE_MON_*) and a nonzero
        prob instead.
        """
        if not (0 <= monster_shape <= 0x7FF):
            raise ValueError(
                f"monster_shape {monster_shape} out of range 0..2047 "
                f"(only the low 11 bits of the egg quality)")
        if not (0 <= prob <= 0x1F):
            raise ValueError(f"prob {prob} out of range 0..31")
        if not (0 <= activity <= 0x07):
            raise ValueError(f"activity {activity} out of range 0..7")
        if not (0 <= group <= 0x1F):
            raise ValueError(f"group {group} out of range 0..31")
        quality = (prob << 11) | (monster_shape & 0x7FF)
        return cls(x=x, y=y, z=z, shape=cls.SHAPE_MONSTER_EGG,
                   frame=1 if one_shot else 0, quality=quality,
                   npcnum=count, mapnum=(group << 3) | activity)

    # MONEGG, retail class 0x481: an UnkEgg (shape 73) of quality 2. Its
    # hatch() area-searches 112*32 = 3584 units round itself for shape 500
    # and calls MonsterEgg::hatch on every egg whose mapNum >> 3 equals its
    # own mapNum & 0x1F, once per stay in the fast area (bit 0x80 of its
    # mapNum, cleared by its leaveFastArea). Retail lays all 130 of its own
    # in U8SAVE.000's NONFIXED.DAT, frame 2 in 126 of them.
    MONEGG_QUALITY = 2
    MONEGG_FRAME = 2
    MONEGG_RANGE = 3584

    @classmethod
    def monster_trigger(cls, x, y, z=0, group=0, xrange=0, yrange=0):
        """Create a MONEGG trigger: hatches monster-egg `group` when the
        Avatar walks into its box, x +/- 32*xrange, y +/- 32*yrange, z
        within 48 (EggHatcherProcess::run)."""
        if not (1 <= group <= 0x1F):
            raise ValueError(f"group {group} out of range 1..31")
        if not (0 < xrange <= 0xF and 0 < yrange <= 0xF):
            raise ValueError(f"ranges ({xrange},{yrange}) out of range 1..15")
        return cls(x=x, y=y, z=z, shape=cls.SHAPE_STANDARD_EGG,
                   frame=cls.MONEGG_FRAME, quality=cls.MONEGG_QUALITY,
                   npcnum=(xrange << 4) | yrange, mapnum=group)

    @classmethod
    def placed_item(cls, x, y, z=0, shape=0, frame=0, quality=0):
        """Create a generic placed item."""
        return cls(x=x, y=y, z=z, shape=shape, frame=frame, quality=quality)

    @classmethod
    def contained_item(cls, shape, frame=0, quality=0, npcnum=0, depth=1):
        """Create an item that lives INSIDE the container written just
        before it.

        The FIXED format has no explicit parent link. Map::loadFixedFormat-
        Objects keeps a stack of open containers and reads a record's x as
        its CONTAINER DEPTH: x=1 means "inside the most recent top-level
        container", x=2 "inside the container inside that", and an x that
        does not match the open depth pops the stack. So a contained item
        must directly follow its container (or its container's earlier
        contents) in the item list — MapArchive.save() preserves list
        order, and nothing in the build sorts it.

        y is the item's position in the container's gump, packed
        (gx | gy << 8). -1 packs as 0xFFFF, which ContainerGump::InitGump
        reads as "unplaced" and randomises on first open
        (Item::randomGumpLocation). z is unused for a contained item.

        flags MUST carry FLG_CONTAINED (0x0008). ItemFactory::createItem
        copies the record's flags straight onto the item, and
        Item::moveToContainer only unlinks an item from its old container
        inside `if (_flags & (FLG_CONTAINED | FLG_EQUIPPED))`. The loader
        attaches contained records with Container::addItem(), which pushes
        to _contents WITHOUT setting that flag — so without it here, the
        first time the player takes the item out it is added to the new
        container while STILL listed in the old one. Two owners, one item:
        the container keeps reporting the old count, and the next map
        change frees it under the holder. That crashed ScummVM on
        2026-09-04 (segfault leaving map 10 carrying a Tiny Tar).

        Both map_validate and exact_reach already skip records with
        x < 64 or y < 64, so a contained item is invisible to the
        placement checks — which is right, it has no world position.
        Retail FIXED.DAT never uses this (0 records); the base game only
        exercises the path through NONFIXED. Verified in-engine 2026-09-03
        on Hrodny's chest (build_map_10.py).
        """
        return cls(x=depth, y=-1, z=0, shape=shape, frame=frame,
                   flags=cls.FLG_CONTAINED,
                   quality=quality, npcnum=npcnum)

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
        """Frame 1: the arrival pad. Engine: NOT a teleporter."""
        return self.is_teleport_egg and self.frame == 1

    @property
    def is_teleporter(self):
        """Frame 0: the trigger. Engine: isTeleporter() == (_frame != 1)."""
        return self.is_teleport_egg and self.frame == 0

    def __repr__(self):
        if self.is_glob_egg:
            return f"MapItem(glob={self.quality}, pos=({self.x},{self.y},{self.z}))"
        elif self.is_teleport_target:
            return f"MapItem(tele_target id={self.quality & 0xFF}, pos=({self.x},{self.y},{self.z}))"
        elif self.is_teleporter:
            return f"MapItem(teleporter id={self.quality & 0xFF} -> map={self.mapnum} range={self.npcnum}, pos=({self.x},{self.y},{self.z}))"
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
        """Write the archive to a FIXED.DAT file — atomically (L12).

        The bytes go to a uniquely named `.staging` file in the SAME
        directory and are renamed into place with os.replace(), which is
        atomic on a single filesystem. Writing straight to `path` truncated
        the previous artifact the instant the write began, so a Ctrl-C, a
        crash, or a full disk part-way through 1.6 MB of map data left a
        TRUNCATED FIXED.DAT at exactly the path install_lv.sh copies into
        the game — and a reader that happened to open it mid-write saw a
        short file rather than an error. Same discipline as the P2 staged
        write; `shared/build/*.staging` is gitignored, and the temp file is
        removed if anything goes wrong.

        Note this is write-atomicity only. Deciding whether the new archive
        deserves to REPLACE the canonical one is a separate gate, and lives
        in build_all_maps.py: it stages, verifies the staged file, then
        promotes or quarantines it.
        """
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

        # Write to a staging file in the same directory, then rename over
        # the target. mkstemp gives a unique name, so two builds writing to
        # the same output can never share a temp file.
        fd, tmp_name = tempfile.mkstemp(dir=str(path.parent) or '.',
                                        prefix=path.name + '.',
                                        suffix='.staging')
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(header)
                f.write(index_table)
                for part in data_parts:
                    f.write(part)
            os.replace(tmp_name, path)
        except BaseException:
            # Includes KeyboardInterrupt: a Ctrl-C mid-write must not leave
            # the staging file behind either.
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise

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


# ---------------------------------------------------------------------------
# Solid wall runs (2026-07-27)
# ---------------------------------------------------------------------------
# THE PICKET-FENCE BUG, fixed properly. Every LV map builds walls by placing
# a wall shape every 256 units, but the wall shapes are only 128 long (and
# only along ONE axis), so each "wall" is a row of posts with 128-unit holes
# between them — wide open to a 64-unit-wide Avatar. map_walkability first
# reported it on Map 11 in 2026-07-04 (457 gap joints) and it is present on
# 09/10/13/17/18 as well.
#
# There are TWO mistakes, and fixing only the stride fixes only one:
#
#   1. STRIDE. A wall segment must be placed every FOOTPAD-LENGTH units
#      along its run, not every 256. The base game agrees: measuring its own
#      placements of shapes 489 and 492 across all 42 retail maps, the
#      spacing along the long axis is 128 units 28/34 and 36/44 times
#      respectively (the handful of wider gaps are doorways).
#
#   2. ORIENTATION. Wall shapes are directional and come in complementary
#      pairs. Shape 489 is 32x128 — long in Y, so it builds walls running
#      NORTH-SOUTH. Its partner 492 is 128x32 — long in X, for walls running
#      EAST-WEST. Map 18 used 489 for its east-west walls, so each segment
#      covered 32 of every 256 units: 87% hole. Using the right shape matters
#      more than the stride.
#
# Item positions are the MAX corner (world/item.cpp), so a 128x32 item at
# (x, y) occupies [x-128, x] x [y-32, y]. These helpers do that arithmetic so
# callers can think in terms of the interval they want covered.

def wall_run_x(x0, x1, y, shape, frame=0, z=0, seg_len=128, gaps=()):
    """Solid east-west wall covering x in [x0, x1] at constant y.

    `shape` must be long in X (footpad_x * 32 == seg_len), e.g. 492 or 26.
    `gaps`: iterable of (gap_x0, gap_x1) intervals to leave OPEN — doorways,
    or the Tiny Tar crack. A gap is left open if the segment it would occupy
    overlaps the interval at all, so gaps are conservative (never partially
    walled).
    """
    items = []
    x = x0 + seg_len
    while x <= x1:
        seg = (x - seg_len, x)
        if not any(seg[0] < g1 and g0 < seg[1] for g0, g1 in gaps):
            items.append(MapItem.placed_item(x=x, y=y, z=z,
                                             shape=shape, frame=frame))
        x += seg_len
    return items


def wall_run_y(y0, y1, x, shape, frame=0, z=0, seg_len=128, gaps=()):
    """Solid north-south wall covering y in [y0, y1] at constant x.

    `shape` must be long in Y (footpad_y * 32 == seg_len), e.g. 489 or 32.
    `gaps`: iterable of (gap_y0, gap_y1) intervals to leave OPEN.
    """
    items = []
    y = y0 + seg_len
    while y <= y1:
        seg = (y - seg_len, y)
        if not any(seg[0] < g1 and g0 < seg[1] for g0, g1 in gaps):
            items.append(MapItem.placed_item(x=x, y=y, z=z,
                                             shape=shape, frame=frame))
        y += seg_len
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

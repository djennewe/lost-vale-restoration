#!/usr/bin/env python3
"""
parse_typeflag.py — Read and decode TYPEFLAG.DAT shape metadata.

Usage:
    parse_typeflag.py 145 148 155 220         # Dump specific shapes
    parse_typeflag.py --find roof              # Find shapes with SI_ROOF
    parse_typeflag.py --find solid,roof        # Multiple flags (AND)
    parse_typeflag.py --footpad 4,4            # Find by footpad X,Y
    parse_typeflag.py --footpad 4,4,5          # Find by footpad X,Y,Z
    parse_typeflag.py --all                    # Full dump (non-empty only)
"""

import struct
import sys
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
TYPEFLAG_PATH = os.path.join(
    BASE_DIR, "shared", "data", "u8-install", "STATIC", "TYPEFLAG.DAT")

# --- Flag tables ---

FLAGS_BYTE0 = [
    (0x01, "SI_FIXED"),
    (0x02, "SI_SOLID"),
    (0x04, "SI_SEA"),
    (0x08, "SI_LAND"),
    (0x10, "SI_OCCL"),
    (0x20, "SI_BAG"),
    (0x40, "SI_DAMAGING"),
    (0x80, "SI_NOISY"),
]

FLAGS_BYTE1_LO = [
    (0x01, "SI_DRAW"),
    (0x02, "SI_IGNORE"),
    (0x04, "SI_ROOF"),
    (0x08, "SI_TRANSL"),
]

FLAGS_BYTE5_HI = [
    (0x10, "SI_EDITOR"),
    (0x20, "SI_EXPLODE"),
    (0x40, "SI_UNK46"),
    (0x80, "SI_UNK47"),
]

FAMILY_NAMES = {
    0: "SF_GENERIC",
    1: "SF_QUALITY",
    2: "SF_QUANTITY",
    3: "SF_GLOBEGG",
    4: "SF_UNKEGG",
    5: "SF_BREAKABLE",
    6: "SF_CONTAINER",
    7: "SF_MONSTEREGG",
    8: "SF_TELEPORTEGG",
    9: "SF_REAGENT",
    15: "SF_15",
}

EQUIP_NAMES = {
    0: "none", 1: "shield", 2: "arm", 3: "head",
    4: "body", 5: "legs", 6: "weapon",
}


class ShapeInfo:
    """Decoded TYPEFLAG.DAT entry for one shape."""

    def __init__(self, shape_id, data):
        self.shape_id = shape_id
        b0, b1, b2, b3, b4, b5, self.weight, self.volume = struct.unpack(
            'BBBBBBBB', data)

        # Byte 0 — physics flags
        self.flags0 = b0

        # Byte 1 — low nibble = more flags, high nibble = family
        self.flags1 = b1 & 0x0F
        self.family = (b1 >> 4) & 0x0F

        # Byte 2 — low nibble = equip type, high nibble = X footpad
        self.equiptype = b2 & 0x0F
        self.footpad_x = (b2 >> 4) & 0x0F

        # Byte 3 — low nibble = Y footpad, high nibble = Z footpad
        self.footpad_y = b3 & 0x0F
        self.footpad_z = (b3 >> 4) & 0x0F

        # Byte 4 — low nibble = animtype, high nibble = animdata
        self.animtype = b4 & 0x0F
        self.animdata = (b4 >> 4) & 0x0F

        # Byte 5 — low nibble = unknown, high nibble = extra flags
        self.unknown5 = b5 & 0x0F
        self.flags5 = b5 & 0xF0

    # --- Properties ---

    @property
    def flag_names(self):
        names = []
        for mask, name in FLAGS_BYTE0:
            if self.flags0 & mask:
                names.append(name)
        for mask, name in FLAGS_BYTE1_LO:
            if self.flags1 & mask:
                names.append(name)
        for mask, name in FLAGS_BYTE5_HI:
            if self.flags5 & mask:
                names.append(name)
        return names

    @property
    def family_name(self):
        return FAMILY_NAMES.get(self.family, f"SF_UNK{self.family}")

    @property
    def equip_name(self):
        return EQUIP_NAMES.get(self.equiptype, f"equip_{self.equiptype}")

    @property
    def is_empty(self):
        """True when all bytes are zero (unused shape slot)."""
        return (self.flags0 == 0 and self.flags1 == 0 and self.family == 0
                and self.footpad_x == 0 and self.footpad_y == 0
                and self.footpad_z == 0 and self.weight == 0
                and self.volume == 0)

    def has_flag(self, flag_name):
        upper = flag_name.upper()
        return upper in [f.upper() for f in self.flag_names]

    def __str__(self):
        flags = ", ".join(self.flag_names) if self.flag_names else "(none)"
        parts = [
            f"Shape {self.shape_id:4d}:",
            f"flags=[{flags}]",
            f"family={self.family_name}",
            f"footpad=({self.footpad_x},{self.footpad_y},{self.footpad_z})",
        ]
        if self.equiptype:
            parts.append(f"equip={self.equip_name}")
        if self.animtype:
            parts.append(f"anim={self.animtype}/{self.animdata}")
        parts.append(f"wt={self.weight} vol={self.volume}")
        return "  ".join(parts)


# --- Loader ---

def load_typeflag(path=None):
    """Load all 2048 shape entries from TYPEFLAG.DAT."""
    if path is None:
        path = TYPEFLAG_PATH
    with open(path, 'rb') as f:
        data = f.read()
    if len(data) != 2048 * 8:
        print(f"WARNING: Expected 16384 bytes, got {len(data)}")
    shapes = []
    for i in range(min(len(data) // 8, 2048)):
        shapes.append(ShapeInfo(i, data[i * 8:(i + 1) * 8]))
    return shapes


# --- Query helpers ---

def find_shapes(shapes, query):
    """Find shapes matching a comma-separated flag/keyword query (AND logic)."""
    terms = [t.strip().upper() for t in query.split(",")]
    results = []
    for si in shapes:
        if si.is_empty:
            continue
        match = True
        for term in terms:
            # Family shortcuts
            if term == "CONTAINER":
                if si.family != 6:
                    match = False
            elif term == "QUALITY":
                if si.family != 1:
                    match = False
            elif term.startswith("FAMILY="):
                if si.family != int(term.split("=")[1]):
                    match = False
            # Flag shortcuts (with or without SI_ prefix)
            else:
                flag = term if term.startswith("SI_") else f"SI_{term}"
                if not si.has_flag(flag):
                    match = False
        if match:
            results.append(si)
    return results


def find_by_footpad(shapes, x, y, z=None):
    """Find shapes with matching footpad dimensions."""
    results = []
    for si in shapes:
        if si.is_empty:
            continue
        if si.footpad_x == x and si.footpad_y == y:
            if z is None or si.footpad_z == z:
                results.append(si)
    return results


# --- CLI ---

def main():
    if not os.path.exists(TYPEFLAG_PATH):
        print(f"ERROR: TYPEFLAG.DAT not found at {TYPEFLAG_PATH}")
        sys.exit(1)

    shapes = load_typeflag()
    non_empty = sum(1 for s in shapes if not s.is_empty)
    print(f"Loaded {len(shapes)} entries ({non_empty} non-empty) "
          f"from TYPEFLAG.DAT\n")

    if len(sys.argv) < 2:
        print("Usage:")
        print("  parse_typeflag.py 145 148 155 220     # Dump specific shapes")
        print("  parse_typeflag.py --find roof          # Find by flag")
        print("  parse_typeflag.py --find solid,roof    # Multiple flags (AND)")
        print("  parse_typeflag.py --footpad 4,4        # Find by footpad")
        print("  parse_typeflag.py --all                # Full dump")
        sys.exit(0)

    if sys.argv[1] == '--all':
        for si in shapes:
            if not si.is_empty:
                print(si)

    elif sys.argv[1] == '--find':
        query = sys.argv[2] if len(sys.argv) > 2 else "roof"
        results = find_shapes(shapes, query)
        print(f"Shapes matching '{query}': {len(results)}\n")
        for si in results:
            print(si)

    elif sys.argv[1] == '--footpad':
        parts = sys.argv[2].split(',')
        x, y = int(parts[0]), int(parts[1])
        z = int(parts[2]) if len(parts) > 2 else None
        results = find_by_footpad(shapes, x, y, z)
        z_str = f",{z}" if z is not None else ""
        print(f"Shapes with footpad ({x},{y}{z_str}): {len(results)}\n")
        for si in results:
            print(si)

    else:
        # Positional args → shape IDs
        for arg in sys.argv[1:]:
            try:
                sid = int(arg)
                if 0 <= sid < len(shapes):
                    print(shapes[sid])
                else:
                    print(f"Shape {sid}: out of range (0–{len(shapes)-1})")
            except ValueError:
                print(f"Invalid shape ID: {arg}")


if __name__ == '__main__':
    main()

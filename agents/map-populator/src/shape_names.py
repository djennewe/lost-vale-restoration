#!/usr/bin/env python3
"""
shape_names.py — the ENGINE's own shape->display-name table.

When the player single-clicks an item in U8, the engine prints a name that
comes from the item's usecode class strings. The mapping is:

    usecode class ID = shape ID + 2

(confirmed empirically 2026-07-02 on four anchors: shape 505 prints "switch"
= class 507; shape 307 prints "Wardrobe" = class 309; shape 289 renders as a
stone throne = class 291 "Stone throne"; shape 68 is our door = class 70
"Locked Door").

This is the AUTHORITATIVE identity source for base-game shapes — stronger
than visual inspection of renders, which misidentified 505 (a switch) as a
key and 307 (a wardrobe) as an ornate chest. Always check engine_name()
before assigning a semantic SHAPE_* constant.

Usage:
    from shape_names import engine_name, all_names
    engine_name(505)   # -> 'switch'
    engine_name(82)    # -> 'key blank'
    engine_name(66)    # -> None (no usecode class; scenery)

The table is extracted from the BASE game's EUSECODE.FLX (not the LV build,
whose extra classes would pollute the offsets) and cached as JSON in
shared/corpus/shape_names.json. Delete the cache to force re-extraction.
"""

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, '..', '..', '..'))
CACHE_PATH = os.path.join(_ROOT, 'shared', 'corpus', 'shape_names.json')
BASE_EUSECODE = os.path.join(_ROOT, 'shared', 'data', 'u8-install',
                             'USECODE', 'EUSECODE.FLX')

CLASS_SHAPE_OFFSET = 2  # usecode class ID = shape ID + 2

# strings that appear in bytecode but are not item names
_NOISE = {'wxY', 'SPyZ', 'wxJ', 'PyZ', 'etD'}


def _looks_like_name(t):
    if t in _NOISE:
        return False
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z \-']{2,35}", t))


def _extract(eusecode_path):
    sys.path.insert(0, os.path.join(_ROOT, 'agents', 'usecode-disasm', 'src'))
    from u8_flex import UsecodeFlexArchive
    arc = UsecodeFlexArchive(eusecode_path)
    names = {}
    for cid in range(CLASS_SHAPE_OFFSET, arc.count):
        try:
            data = arc.get_object(cid)
        except Exception:
            continue
        if not data:
            continue
        for s in re.findall(rb'[ -~]{3,40}', data):
            t = s.decode().strip()
            if _looks_like_name(t):
                names[cid - CLASS_SHAPE_OFFSET] = t
                break
    return names


_names_cache = None


def all_names():
    """Return {shape_id(int): name(str)} for every shape with a usecode name."""
    global _names_cache
    if _names_cache is not None:
        return _names_cache
    if os.path.exists(CACHE_PATH):
        raw = json.load(open(CACHE_PATH))
        _names_cache = {int(k): v for k, v in raw.items()}
        return _names_cache
    names = _extract(BASE_EUSECODE)
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    json.dump({str(k): v for k, v in sorted(names.items())},
              open(CACHE_PATH, 'w'), indent=0)
    _names_cache = names
    return names


def engine_name(shape_id):
    """The name the game prints when the player clicks this shape (or None)."""
    return all_names().get(shape_id)


if __name__ == '__main__':
    names = all_names()
    if len(sys.argv) > 1:
        for a in sys.argv[1:]:
            s = int(a)
            print(f"{s}: {names.get(s, '(no usecode class)')}")
    else:
        for s, n in sorted(names.items()):
            print(f"{s:5d}  {n}")

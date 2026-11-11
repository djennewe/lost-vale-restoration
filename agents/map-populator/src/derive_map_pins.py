#!/usr/bin/env python3
"""Derive the Lost Vale map pin inventory (map_pins.json).

Phase 0 of docs/reviews/2026-09-14-map-cleanup-plan.md section 2: "Pins are an
inventory, derived, not a list from memory."  Run this, commit the JSON, and
let test_map_hygiene.py read it:

    python3 agents/map-populator/src/derive_map_pins.py

Nothing here is a remembered list of coordinates.  Every row's shape, frame,
quality, npcnum and position is read out of the built FIXED.DAT (or, for the
two base-game slots 08 and 39, out of the builders' *_additions() functions,
because those maps are mostly Origin's bytes).  Every ACTIVE row carries a
`reads` citation that was produced by scanning a file at run time:

  * the compiled usecode type filters are found by scanning
    agents/usecode-compiler/src/lv-patched/*.UNK and lv-new/*.UNK for
    `foreach ... type = TypeX`, `item.getType() = TypeX` and
    `typeclass TypeX`, then resolving TypeX through TYPE_SHAPES in
    u8c_symbols.py.  (Those two directories are the authoritative compiled
    tier per CLAUDE.md; the recovered 1994 snapshot under shared/data/ is
    read-only evidence and its LOST VALE/ copies are outranked by
    lv-patched/ for every basename that exists in both.)
  * egg dispatch (shape 73) is resolved as class = quality + 0x47F against
    shared/build/lv_manifest.json, the same arithmetic map_walkability's
    run_event_eggs table uses.
  * npcnum dispatch is resolved as class = npcnum + 1024 against the same
    manifest (the engine patch in Item::callUsecodeEvent).
  * teleport pairs are decoded with the encoding documented on
    u8_map.MapItem.teleporter / .teleport_target.
  * a handful of rows are pinned by a TEST rather than by usecode; those
    citations are found by grepping test_route_reach.py for the coordinate.

A world-scanning filter (`within N of referent`) only pins the items that are
actually in range of a real anchor on the map, so the 48 loose shape-295 wall
reliefs on Map 11 and the 36 loose shape-721 chimneys on Map 17 do NOT become
pins just because some TypeX resolves to their shape.  They are defects for
the hygiene test to catch, and leaving them out is the point.

Classes (plan section 2):
  active      — something compiled reads it today.
  decorative  — placed with a quality/npcnum for a possible future wiring,
                but nothing compiled reads it.  Free to move; the quality is
                recorded so a later wiring can find it.
  deferred    — a trigger removed on purpose.  The row says where it WOULD
                go so nobody restores it to satisfy a pin.
"""

import datetime
import hashlib
import json
import os
import re
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, '..', '..', '..'))
sys.path.insert(0, _THIS_DIR)
sys.path.insert(0, os.path.join(REPO_ROOT, 'agents', 'usecode-compiler', 'src'))

from u8_map import MapArchive, MapItem              # noqa: E402
from map_preview import GlobReader, expand_globs    # noqa: E402
from u8c_symbols import TYPE_SHAPES                 # noqa: E402
import build_map_08                                 # noqa: E402
import build_map_39                                 # noqa: E402

FIXED = os.path.join(REPO_ROOT, 'shared', 'build', 'FIXED.DAT')
MANIFEST = os.path.join(REPO_ROOT, 'shared', 'build', 'lv_manifest.json')
LV_PATCHED = os.path.join(REPO_ROOT, 'agents', 'usecode-compiler', 'src',
                          'lv-patched')
LV_NEW = os.path.join(REPO_ROOT, 'agents', 'usecode-compiler', 'src', 'lv-new')
OUT = os.path.join(_THIS_DIR, 'map_pins.json')

# FIXED.DAT map slots the expansion builds itself...
LV_MAPS = (9, 10, 11, 13, 17, 18)
# ...and the two base-game slots it only adds to.
BASE_SLOTS = {8: build_map_08.build_map_08_additions,
              39: build_map_39.build_map_39_additions}

EGG_SHAPE = MapItem.SHAPE_GLOB_EGG          # 2 — glob eggs, expanded away
UNK_EGG = 73
MONSTER_EGG = MapItem.SHAPE_MONSTER_EGG     # 500
TELEPORT_EGG = MapItem.SHAPE_TELEPORT_EGG   # 508
EGG_CLASS_BASE = 0x47F                      # class = quality + 0x47F
NPCNUM_CLASS_BASE = 1024                    # class = npcnum + 1024
ACTOR_WINDOW = range(100, 117)              # npcnum 100-116 = Actor promotion


# ---------------------------------------------------------------- sources --

def sha_prefix(path, n=16):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()[:n]


def load_manifest():
    with open(MANIFEST) as fh:
        m = json.load(fh)
    by_id = {v: k for k, v in m['classes'].items()}
    npc_by_id = {v: k for k, v in m['npc_classes'].items()}
    return m, by_id, npc_by_id


def load_maps(source='fixed'):
    """{mapnum: [MapItem]} with globs expanded.

    source='fixed' reads the LV slots out of the built FIXED.DAT, the
    shipped bytes. source='builders' runs the six map builders in memory
    instead, so a builder edit shows up before anyone rebuilds; each record
    goes through to_bytes()/from_bytes() first, so it carries exactly what
    build_all_maps.py would write (unsigned z, packed fields). The two base
    slots always come from their builders' *_additions()."""
    if source == 'fixed':
        archive = MapArchive(FIXED)
        raw = {n: archive.get_map_items(n) for n in LV_MAPS}
    elif source == 'builders':
        import contextlib
        import io
        raw = {}
        for n in LV_MAPS:
            mod = __import__(f'build_map_{n:02d}')
            with contextlib.redirect_stdout(io.StringIO()):
                built = getattr(mod, f'build_map_{n:02d}')()
            raw[n] = [MapItem.from_bytes(it.to_bytes()) for it in built]
    else:
        raise ValueError(f'unknown source {source!r}')
    gr = GlobReader()
    maps = {n: expand_globs(items, gr) for n, items in raw.items()}
    for n, fn in BASE_SLOTS.items():
        maps[n] = list(fn())
    return maps


# ------------------------------------------------------- the usecode scan --

# The recovered 1994 files carry high-bit German characters, so grep calls
# them binary and every reader has to say latin-1 explicitly.  The patched
# copies inherit those bytes.
ENC = 'latin-1'

RE_FOREACH = re.compile(r'foreach\b[^{]*?\btype\s*=\s*(Type\w+)')
RE_GETTYPE = re.compile(r'\bgetType\s*\(\s*\)\s*=\s*(Type\w+)')
RE_TYPECLASS = re.compile(r'^\s*(?:typeclass|eggclass)\s+(\w+)')
RE_FRAME = re.compile(r'\bframe\s*=\s*(\d+)')
RE_GETFRAME = re.compile(r'\bgetFrame\s*\(\s*\)\s*=\s*(\w+)')
RE_CONTAINER = re.compile(r'within\s+container\b')
RE_RANGE = re.compile(r'within\s+(\d+)\s+(cells\s+of|of)\b')


def scan_filters():
    """Every compiled type filter in lv-patched/ + lv-new/.

    Returns a list of dicts: {file, line, type, shape, scope, range, frame}.
    `scope` is 'inventory' (within container ...) or 'world'.
    """
    out = []
    for d in (LV_PATCHED, LV_NEW):
        for name in sorted(os.listdir(d)):
            if not name.endswith('.UNK'):
                continue
            path = os.path.join(d, name)
            lines = read_lines(path)
            for i, line in enumerate(lines):
                if line.lstrip().startswith('//'):
                    continue
                # A foreach's qualifiers often wrap onto the next lines.
                window = ' '.join(lines[i:i + 3])
                for rx, kind in ((RE_FOREACH, 'foreach'),
                                 (RE_GETTYPE, 'getType')):
                    m = rx.search(line)
                    if not m:
                        continue
                    tname = m.group(1)
                    shape = TYPE_SHAPES.get(tname)
                    scope = ('inventory' if RE_CONTAINER.search(window)
                             else 'world')
                    rm = RE_RANGE.search(window)
                    rng = None
                    raw_range = None
                    if rm:
                        # Quote the source's own words in the citation; the
                        # numeric radius below assumes a 32-unit cell only
                        # so the in-range test has something to use.
                        raw_range = ' '.join(rm.group(0).split())
                        rng = int(rm.group(1)) * (32 if 'cells' in rm.group(2)
                                                  else 1)
                    fm = RE_FRAME.search(window) or RE_GETFRAME.search(window)
                    frame = None
                    if fm and fm.group(1).isdigit():
                        frame = int(fm.group(1))
                    out.append({
                        'file': os.path.relpath(path, REPO_ROOT),
                        'line': i + 1, 'kind': kind, 'type': tname,
                        'shape': shape, 'scope': scope, 'range': rng,
                        'raw_range': raw_range, 'frame': frame,
                    })
    return out


def cite(f):
    return f"{f['file']}:{f['line']} ({f['type']} -> shape {f['shape']})"


def find_filter(filters, filename, typename):
    """The one filter row for a (file, type) pair — fails loudly if absent,
    so a rename in the usecode breaks this script instead of silently
    dropping a pin."""
    hits = [f for f in filters
            if os.path.basename(f['file']) == filename and
            f['type'] == typename]
    if not hits:
        raise SystemExit(
            f"derive_map_pins: no `type = {typename}` filter left in "
            f"{filename} — the pin table is stale, re-derive it by hand")
    return hits[0]


def read_lines(path):
    """Lines exactly as grep counts them.

    The recovered 1994 sources carry lone CR bytes inside dialogue strings
    (3,292 of them in ATLI.UNK alone).  Python's universal newlines turn
    every one of those into a line break, which would push every citation
    below it out of step with `grep -n` — the tool everyone else in this
    repo checks a citation with.  So: read bytes, split on \n only, and
    decode latin-1 (the files are binary to grep because of the high-bit
    German characters).
    """
    with open(path, 'rb') as fh:
        raw = fh.read()
    return [ln.decode(ENC) for ln in raw.split(b'\n')]


def grep_line(path, needle):
    """First 1-based line number in `path` containing `needle`, or None."""
    for i, line in enumerate(read_lines(path), 1):
        if needle in line:
            return i
    return None


def route_cite(x, y):
    """test_route_reach.py's goal line for a coordinate, if it has one."""
    path = os.path.join(_THIS_DIR, 'test_route_reach.py')
    n = grep_line(path, f'{x}, {y},')
    return f"agents/map-populator/src/test_route_reach.py:{n}" if n else None


# ----------------------------------------------------------- the pin rules --

def row(item, cls, kind, why, reads):
    return {'shape': item.shape, 'frame': item.frame, 'quality': item.quality,
            'npcnum': item.npcnum, 'x': item.x, 'y': item.y, 'z': item.z,
            'class': cls, 'kind': kind, 'why': why, 'reads': list(reads)}


def synthetic_row(shape, frame, quality, npcnum, x, y, z, cls, kind, why,
                  reads):
    return {'shape': shape, 'frame': frame, 'quality': quality,
            'npcnum': npcnum, 'x': x, 'y': y, 'z': z, 'class': cls,
            'kind': kind, 'why': why, 'reads': list(reads)}


def dist(a, b):
    return max(abs(a.x - b.x), abs(a.y - b.y))


# World-scanning filters: which anchor each one searches from.  `anchor` is
# resolved against the real map, so a filter whose anchor was never placed
# produces no pins (and gets reported as dangling).
WORLD_SCANS = [
    # (usecode file, type, anchor spec, quality guard, note)
    {'file': 'AOSCENE.UNK', 'type': 'TypeZealanGod',
     'anchor': ('egg', 296),
     'note': 'the Sacred Shield ceremony animates the three gods'},
    {'file': 'TEMPLENT.UNK', 'type': 'TypeZealanGod',
     'anchor': ('egg', 305),
     'note': 'the temple-entry scene wakes the three gods'},
    {'file': 'COLPUZZL.UNK', 'type': 'TypeElementalColumn',
     'anchor': ('npcnum', 120),
     'note': 'TypeReceptacle::use() destroys the pillar beside it'},
    {'file': 'COLPUZZL.UNK', 'type': 'TypeSealingBoulder',
     'anchor': ('npcnum', 120), 'quality': 299,
     'note': 'the doorway plug the four-pillar puzzle removes'},
    {'file': 'LBSCENE.UNK', 'type': 'TypeLordBritish',
     'anchor': ('egg', 304),
     'note': 'the quest step 1 apparition the egg animates'},
    {'file': 'PLNTST.UNK', 'type': 'TypeShortmushroom',
     'anchor': ('egg', 283),
     'note': 'the Test Plant EggPlantTest::hatch() bursts'},
    {'file': 'CANTRK.UNK', 'type': 'TypeMagicCandle',
     'anchor': ('egg', 280),
     'note': 'the candle trick — EggCandleTrick (q280) is unplaced'},
]

# Inventory-scanning filters pin the map-placed instances the player picks up.
INVENTORY_SCANS = [
    {'file': 'PLNTST.UNK', 'type': 'TypeBushKey', 'kind': 'quest_item',
     'note': 'the Passage stone EggPlantTest::hatch() consumes'},
    # 'quality': the filter's getQ() guard. Tyorvi creates his key at
    # runtime (lv-patched/TYORVI.UNK T7), so no placed key matches it.
    {'file': 'CLCLIMB.UNK', 'type': 'TypeCliffKey', 'kind': 'quest_item',
     'quality': 170,
     'note': "EggCloudCliffs gates the climb on Tyorvi's quality-170 key"},
    {'file': 'SHADES.UNK', 'type': 'TypeAOFrizbee', 'kind': 'quest_item',
     'note': 'the Sacred Shield halves the ceremony fuses'},
    {'file': 'CRACKHNT.UNK', 'type': 'TypePotion', 'kind': 'quest_item',
     'note': 'the Tiny Tar potions the crack hint looks for'},
    {'file': 'EZREKAL.UNK', 'type': 'TypeWeedz', 'kind': 'quest_item',
     'note': "the special root for Tyorvi's nightmare elixir"},
    {'file': 'COLPUZZL.UNK', 'type': 'TypeTalisman', 'kind': 'quest_item',
     'note': 'the four elemental talismans the receptacles consume'},
    {'file': 'ENDGAME.UNK', 'type': 'TypeReagent', 'kind': 'quest_item',
     'note': 'the endgame reagents (created at runtime, never map-placed)'},
    {'file': 'TYORVI.UNK', 'type': 'TypeBottle', 'kind': 'quest_item',
     'note': 'the elixir bottle (created at runtime, never map-placed)'},
]

# Rows nothing compiled reads, kept because the plan says to keep them.  Each
# is located by a (map, shape, quality) lookup on the real map data, never by
# a remembered coordinate.
DECORATIVE = [
    {'map': 10, 'shape': 863, 'quality': 100, 'kind': 'custom_art',
     'symbol': 'agents/map-populator/src/build_map_10.py '
               'build_sacred_circle (SHAPE_SACRED_ROCK, quality=100)',
     'why': "The Sacred Circle's central stone, custom art since "
            "2026-09-20 (docs/art-track.md contract 3: a ninth standing "
            "stone kin to the eight shape-38 monoliths on the ring; was a "
            "66 rubble lump, and a 721 chimney before that). Nothing reads "
            "it. TypeSealingBoulder resolves to 66 and COLPUZZL.UNK:175 "
            "reads it, but guarded by getQ() = 299 within 2200 of a Map 11 "
            "referent, so the swap to 863 left that filter's targets alone. "
            "Decoration until a wiring claims quality 100. The POSITION is "
            "frozen: the box clears map_walkability's MAP10_ROOT_SEED "
            "(20480, 16896) by one world unit on each axis."},
    {'map': 17, 'shape': 875, 'quality': 90, 'kind': 'custom_art',
     'symbol': 'agents/map-populator/src/build_map_17.py:QUALITY_OBELISK',
     'why': "The magnetic obelisk's front drum. Since 2026-10-17 the "
            "obelisk is screen11's 1994 composite, retail pieces (12 "
            "f14-f17, cap 545, skull 814) on four banded white columns "
            "(875 f1), and custom art 861 is retired; the "
            "drum nearest the camera carries QUALITY_OBELISK where the "
            "vignette's pin_moves put the MAGNET egg. Its MAGNET egg is "
            "deliberately absent (build_map_17.py's MAGNET note), so nothing "
            "reads it today. The position is the shot's."},
    {'map': 18, 'shape': 550, 'quality': 310, 'kind': 'placeholder',
     'symbol': 'agents/map-populator/src/build_map_18.py:QUALITY_ALTAR',
     'why': "The Inner Sanctum altar. No TypeX resolves to shape 550 and "
            "no egg or npcnum dispatches it; quality 310 is map-side "
            "bookkeeping kept for a future wiring."},
    {'map': 9, 'shape': 613, 'quality': 1, 'kind': 'quest_item',
     'symbol': "agents/map-populator/src/build_map_09.py Galjeron's Journal "
               "(SHAPE_BOOK_CLOSED, quality=1)",
     'why': "Galjeron's journal. The builder comment says 'quality triggers "
            "usecode read', but TypeBook/TypeScroll/TypeNSGoldPlaque all "
            "resolve to 158, not 613, and no compiled LV filter names shape "
            "613. It is not inert, though: the engine dispatches a shape's "
            "use()/look() from the class whose number equals the shape "
            "(item.cpp:1516) and EUSECODE.FLX entry 615 (= class 613) is "
            "7,482 bytes of Origin's own book handler, so double-clicking "
            "it runs base-game Pagan code with quality 1. Decorative until "
            "an LV class is compiled at 613 — a manifest decision, not a "
            "two-file edit."},
]

# Triggers removed on purpose.  Never restore one to satisfy a pin.
DEFERRED = [
    {'map': 17, 'quality': 281, 'class_name': 'EGGMAGNET',
     'at': ('item', 875, 90),      # the obelisk's front drum (screen11)
     'why': "The MAGNET egg that used to sit on the obelisk (it carried "
            "quality 3, which dispatched the base game's BARENTRY). Removed "
            "2026-07-26 and still deferred on four blockers listed in "
            "build_map_17.py: H1 process semantics, MAGNET.UNK's hard-coded "
            "pop target (15615,19839,120) which is nowhere near this "
            "obelisk, the six ritual candles, and the ankh arrangement. "
            "Coordinates are the obelisk's, where it would go.",
     'reads': ['agents/map-populator/src/build_map_17.py (the MAGNET note '
               'after OBELISK_FRONT_DRUM)',
               'shared/data/lv-usecode/LOST VALE/MAGNET.UNK']},
    {'map': 17, 'quality': 280, 'class_name': 'EGGCANDLETRICK',
     'at': ('nowhere',),
     'why': "The candle trick. EGGCANDLETRICK (class 1431, quality 280) is "
            "compiled and unplaced, and no builder comment names a "
            "coordinate for it, so this row records only that it is "
            "deliberately absent: x/y/z are -1. CANTRK.UNK reads "
            "candle.getFrame() but nothing writes it, TypeMagicCandle "
            "resolves to shape 295 (a stone wall relief, SI_FIXED), and no "
            "base-game shape is unlit at frame 0 with a lit frame 1. Do not "
            "place shape-295 items to satisfy this.",
     'reads': ['agents/map-populator/src/build_map_17.py (blockers 2 and 3 '
               'of the deferred-MAGNET note)',
               'shared/data/lv-usecode/LOST VALE/CANTRK.UNK']},
]


def build(source='fixed'):
    manifest, class_by_id, npc_by_id = load_manifest()
    maps = load_maps(source)
    filters = scan_filters()
    notes = {'dangling': [], 'surprises': [], 'unresolved': [],
             'no_such_shape': []}

    pins = {n: [] for n in sorted(maps)}
    claimed = {}   # (map, id(item)) -> the row, so nothing is pinned twice

    def add(mapnum, item, cls, kind, why, reads):
        """Pin an item once. A second rule that also reads the same item
        (a shield half is both a TypeAOFrizbee and an npcNum-236 dispatch)
        contributes its citation to the row that already exists rather
        than making a duplicate."""
        key = (mapnum, id(item))
        if key in claimed:
            r = claimed[key]
            for c in reads:
                if c not in r['reads']:
                    r['reads'].append(c)
            return
        r = row(item, cls, kind, why, reads)
        claimed[key] = r
        pins[mapnum].append(r)

    # --- teleport pairs (shape 508) ------------------------------------
    tele_cite = ['agents/map-populator/src/u8_map.py MapItem.teleporter / '
                 'MapItem.teleport_target (frame 0 = trigger, quality = '
                 '256 + id, mapNum = destination map; frame 1 = arrival '
                 'pad, quality = id)',
                 'agents/map-populator/src/build_all_maps.py '
                 'verify_teleport_pairs']
    for mapnum, items in maps.items():
        for it in items:
            if it.shape != TELEPORT_EGG:
                continue
            if it.frame == 0:
                tid = it.quality & 0xFF
                why = (f"Teleport TRIGGER {tid} -> map {it.mapnum}. Hatch "
                       f"box +/-{(it.npcnum >> 4) * 32}x{(it.npcnum & 0xF) * 32} "
                       f"(npcNum 0x{it.npcnum:02X}). Frozen: the quest spine "
                       f"walks through it.")
            else:
                tid = it.quality & 0xFF
                why = (f"Teleport ARRIVAL PAD {tid} — the destination every "
                       f"trigger with quality {256 + tid} lands on. Frozen: "
                       f"moving it moves the player's arrival point.")
            add(mapnum, it, 'active', 'teleport', why, tele_cite)

    # --- UnkEggs (shape 73): class = quality + 0x47F -------------------
    for mapnum, items in maps.items():
        for it in items:
            if it.shape != UNK_EGG:
                continue
            cid = it.quality + EGG_CLASS_BASE
            if it.quality == MapItem.MONEGG_QUALITY:
                # Retail's MONEGG (0x481), not an LV class: it hatches the
                # monster eggs of its group (lv_monster_eggs.py).
                why = (f"MONEGG trigger (UnkEgg q2 -> retail class {cid}): "
                       f"hatches monster-egg group {it.mapnum & 0x1F} within "
                       f"{MapItem.MONEGG_RANGE} units. Hatch box "
                       f"+/-{(it.npcnum >> 4) * 32}x{(it.npcnum & 0xF) * 32}"
                       f" (npcNum 0x{it.npcnum:02X}).")
                add(mapnum, it, 'active', 'monster_trigger', why,
                    ['agents/map-populator/src/lv_monster_eggs.py',
                     'agents/map-populator/src/test_monster_eggs.py'])
                continue
            name = class_by_id.get(cid)
            if name is None:
                notes['surprises'].append(
                    f"map {mapnum} ({it.x},{it.y},{it.z}): shape-73 egg "
                    f"quality {it.quality} dispatches class {cid}, which is "
                    f"NOT pinned in lv_manifest.json")
                continue
            why = (f"UnkEgg -> class {cid} {name} (class = quality + 0x47F). "
                   f"Hatch box +/-{(it.npcnum >> 4) * 32}x"
                   f"{(it.npcnum & 0xF) * 32} (npcNum 0x{it.npcnum:02X}); "
                   f"npcNum 0 would mean zero range and the egg could never "
                   f"be walked into.")
            add(mapnum, it, 'active', 'egg', why,
                ['shared/build/lv_manifest.json classes.' + name,
                 'agents/map-populator/src/map_walkability.py '
                 'run_event_eggs'])

    # --- monster eggs (shape 500) --------------------------------------
    for mapnum, items in maps.items():
        for it in items:
            if it.shape != MONSTER_EGG:
                continue
            mshape = it.quality & 0x7FF
            prob = (it.quality >> 11) & 0x1F
            why = (f"Monster egg: spawns actor shape {mshape}, activity "
                   f"{it.mapnum & 0x07}, when a MONEGG trigger of group "
                   f"{it.mapnum >> 3} hatches it (prob {prob}/31, count "
                   f"{it.npcnum}: neither is read).")
            add(mapnum, it, 'active', 'monster_egg', why,
                ['agents/map-populator/src/u8_map.py MapItem.monster_egg '
                 '(quality = (prob << 11) | monster_shape)'])

    # --- world-scanning type filters -----------------------------------
    for spec in WORLD_SCANS:
        try:
            f = find_filter(filters, spec['file'], spec['type'])
        except SystemExit:
            if spec['file'] in ('CANTRK.UNK',):
                # CANTRK lives in the read-only 1994 tier, not lv-patched/
                # or lv-new/, so the authoritative scan never sees it.  It
                # still compiles, so record it as a dangling filter.
                f = {'file': 'shared/data/lv-usecode/LOST VALE/CANTRK.UNK',
                     'line': grep_line(os.path.join(
                         REPO_ROOT, 'shared', 'data', 'lv-usecode',
                         'LOST VALE', 'CANTRK.UNK'), 'TypeMagicCandle') or 0,
                     'type': spec['type'],
                     'shape': TYPE_SHAPES.get(spec['type']),
                     'range': 50 * 32, 'raw_range': 'within 50 cells of',
                     'frame': None}
            else:
                raise
        shape = f['shape']
        rng = f['range']
        kind, val = spec['anchor']
        placed = 0
        for mapnum, items in maps.items():
            if kind == 'egg':
                anchors = [i for i in items
                           if i.shape == UNK_EGG and i.quality == val]
            else:
                anchors = [i for i in items if i.npcnum == val]
            if not anchors:
                continue
            for it in items:
                if it.shape != shape:
                    continue
                if f['frame'] is not None and it.frame != f['frame']:
                    continue
                if 'quality' in spec and it.quality != spec['quality']:
                    continue
                if rng is not None and not any(dist(it, a) <= rng
                                               for a in anchors):
                    continue
                placed += 1
                why = (f"{spec['note']}: matched by the compiled filter at "
                       f"{f['file']}:{f['line']} "
                       f"(`type = {f['type']}` -> shape {shape}"
                       + (f", frame {f['frame']}" if f['frame'] is not None
                          else '')
                       + (f", {f['raw_range']}" if f.get('raw_range')
                          else '') + ').')
                add(mapnum, it, 'active', 'typed_item', why,
                    [f"{f['file']}:{f['line']} ({f['type']} -> shape "
                     f"{shape})"])
        if placed == 0:
            notes['dangling'].append(
                f"{f['file']}:{f['line']} `type = {f['type']}` -> shape "
                f"{shape}: no item on any LV map is in range of an anchor "
                f"({kind} {val}) — dangling filter")

    # --- inventory-scanning type filters -------------------------------
    for spec in INVENTORY_SCANS:
        f = find_filter(filters, spec['file'], spec['type'])
        shape = f['shape']
        placed = 0
        for mapnum, items in maps.items():
            for it in items:
                if it.shape != shape:
                    continue
                if f['frame'] is not None and it.frame != f['frame']:
                    continue
                if 'quality' in spec and it.quality != spec['quality']:
                    continue
                placed += 1
                contained = it.x <= 1 or it.y < 0
                why = (f"{spec['note']}. Picked up and then matched by "
                       f"{f['file']}:{f['line']} (`type = {f['type']}` -> "
                       f"shape {shape}"
                       + (f", frame {f['frame']}" if f['frame'] is not None
                          else '')
                       + (f", quality {spec['quality']}" if 'quality' in spec
                          else '') + ' within the Avatar\'s container)'
                       + ('; CONTAINED item — x/y are the container slot, '
                          'not a world position' if contained else ''))
                add(mapnum, it, 'active', spec['kind'], why,
                    [f"{f['file']}:{f['line']} ({f['type']} -> shape "
                     f"{shape})"])
        if placed == 0:
            notes['dangling'].append(
                f"{f['file']}:{f['line']} `type = {f['type']}` -> shape "
                f"{shape}: no item of that shape is placed on any LV map "
                f"— dangling filter (created at runtime, or unplaced)")

    # --- npcnum dispatch ------------------------------------------------
    for mapnum, items in maps.items():
        for it in items:
            if not it.npcnum or it.shape in (UNK_EGG, MONSTER_EGG,
                                             TELEPORT_EGG):
                continue
            if it.npcnum in ACTOR_WINDOW:
                cid = it.npcnum + NPCNUM_CLASS_BASE
                name = npc_by_id.get(cid) or class_by_id.get(cid)
                who = (f"dispatches class {cid} {name}" if name else
                       "no compiled class at "
                       f"{cid} — Actor promotion only")
                reads = ['shared/build/lv_manifest.json npc_classes'
                         if name else
                         'docs/reviews/2026-09-14-map-cleanup-plan.md '
                         'section 3 (every NPC start position is pinned)']
                add(mapnum, it, 'active', 'npc',
                    f"NPC start position, npcNum {it.npcnum} ({who}). The "
                    f"Actor-promotion window is npcNum 100-116; the start "
                    f"position and its loiter leash are frozen.", reads)
                continue
            cid = it.npcnum + NPCNUM_CLASS_BASE
            name = class_by_id.get(cid)
            if name is None:
                notes['surprises'].append(
                    f"map {mapnum} ({it.x},{it.y},{it.z}) shape {it.shape}: "
                    f"npcNum {it.npcnum} dispatches class {cid}, not pinned "
                    f"in lv_manifest.json")
                continue
            contained = it.x <= 1 or it.y < 0
            add(mapnum, it, 'active', 'typed_item',
                f"npcNum dispatch: class = npcNum + 1024 = {cid} {name} "
                f"(the engine patch in Item::callUsecodeEvent)."
                + ('; CONTAINED item — x/y are the container slot'
                   if contained else ''),
                ['shared/build/lv_manifest.json classes.' + name,
                 'agents/map-populator/src/lv_shapes.py NPCNUM_BANDS'])

    # --- locks and their keys (engine-side, not usecode) ----------------
    LOCKS = {
        170: ("Key to the Clouds gate, quality 170 (build_map_10.py "
              "CLIFF_KEY_ID), the number Tyorvi's key carries "
              "(lv-patched/TYORVI.UNK T7). Shape 114 has no door "
              "behaviour, so no key opens it; open lanes pass it "
              "(docs/reviews/2026-09-25-keyless-gates.md)."),
        180: ("Temple gate, lock id 180 (build_map_10.py / build_map_18.py "
              "`quality=180  # temple gate`). Engine-side lock, on the "
              "quest spine to the Ancient Temple."),
        20: ("Hrodny's locked chest, lock id 20 (build_map_10.py "
             "HRODNY_KEY_ID). It holds the three Tiny Tar potions, so it "
             "is on the quest spine for step 16."),
    }
    for mapnum, items in maps.items():
        for it in items:
            if it.shape in (114, 618) and it.quality in LOCKS:
                add(mapnum, it, 'active', 'quest_item', LOCKS[it.quality],
                    ['agents/map-populator/src/build_map_10.py '
                     'CLIFF_KEY_ID / build_map_10.py HRODNY_KEY_ID / '
                     'build_map_08.py DOOR_LOCK_ID'])
    # The keys that fit them. Retail KEY/KEYRING (class 0x4F, 0119) opens a
    # lock whose id equals the key's whole quality, so a key is the lock's
    # other half.
    # Hrodny's q20 key is not here: no map places one since 2026-10-11, the
    # usecode errand hands it out (test_chest_locks SCRIPT_KEYS).
    KEYS = {
        99: ("The Map 8 door key, quality 99 (build_map_08.py "
             "DOOR_LOCK_ID): KEYRING opens the retail double doors (lock "
             "99, U8SAVE.000 NONFIXED) on the way to the Vale with it"),
    }
    for mapnum, items in maps.items():
        for it in items:
            if it.shape == 82 and it.quality in KEYS:
                contained = it.x <= 1 or it.y < 0
                add(mapnum, it, 'active', 'quest_item',
                    KEYS[it.quality]
                    + ('; CONTAINED item — x/y are the container slot, '
                       'not a world position' if contained else '.'),
                    ['agents/map-populator/src/build_map_10.py '
                     'HRODNY_KEY_ID / build_map_08.py DOOR_LOCK_ID'])

    # --- rows a test pins rather than usecode ---------------------------
    for mapnum, items in maps.items():
        for it in items:
            if (mapnum, it.shape) != (17, 864) or it.quality != 80:
                continue
            c = route_cite(it.x, it.y)
            if c:
                add(mapnum, it, 'active', 'quest_item',
                    "The Cloud City message scroll (QUALITY_MSG_SCROLL 80), "
                    "custom art 864 since 2026-09-21 (art track item 4; it "
                    "was the 158 stool). Nothing compiled finds it by type: "
                    "MAGNET.UNK's two TypeMagicScroll foreach are 'within "
                    "container Avatar' and EZREKAL.UNK filters TypeWeedz and "
                    "TypeShields. Route 17 in test_route_reach.py floods to "
                    "its coordinate, so the position is pinned by a test, and "
                    "route_cite finds that line by grepping for the literal "
                    "'3328, 1536,', so a move of one unit drops this row with "
                    "no complaint. Its quality is live now that donor 159 "
                    "makes the shape SF_QUALITY (item.cpp:2841), and class "
                    "864 (lv-new/MSGSCRL.UNK, pinned TYPEMESSAGESCROLL) "
                    "dispatches its look() and use() off the shape number, "
                    "so the shape may not be renumbered either.", [c])

    # --- decorative-with-quality ----------------------------------------
    for spec in DECORATIVE:
        hits = [i for i in maps[spec['map']]
                if i.shape == spec['shape'] and i.quality == spec['quality']]
        if not hits:
            notes['surprises'].append(
                f"map {spec['map']}: expected a decorative shape "
                f"{spec['shape']} quality {spec['quality']} and found none")
        for it in hits:
            add(spec['map'], it, 'decorative', spec['kind'], spec['why'],
                [spec['symbol']])

    # --- the Sacred Circle ring: the plan's claim, corrected -------------
    ring = [i for i in maps[10] if i.shape == 65
            and 19000 < i.x < 22000 and 15500 < i.y < 18300]
    for it in sorted(ring, key=lambda i: (i.x, i.y)):
        add(10, it, 'decorative', 'placeholder',
            "Sacred Circle ring stone. The cleanup plan section 2 calls "
            "these eight 'the active ring' because lv-patched/PLNTST.UNK:72 "
            "filters TypeShortmushroom — but they are shape 65 "
            "(SHAPE_MUSHROOM_CLUSTER) and TypeShortmushroom resolves to 871, "
            "and they sit ~15,000 units from the only EggPlantTest, whose "
            "search radius is 100 cells. Nothing reads them: decoration, "
            "free to move.",
            ['agents/map-populator/src/build_map_10.py build_sacred_circle '
             '(SHAPE_MUSHROOM_CLUSTER = 65)',
             'agents/usecode-compiler/src/lv-patched/PLNTST.UNK:72 '
             '(TypeShortmushroom -> shape 871, not 65)'])

    # --- deferred triggers -----------------------------------------------
    for spec in DEFERRED:
        cid = spec['quality'] + EGG_CLASS_BASE
        if spec['at'][0] == 'item':
            _, shape, quality = spec['at']
            hits = [i for i in maps[spec['map']]
                    if i.shape == shape and i.quality == quality]
            x, y, z = ((hits[0].x, hits[0].y, hits[0].z) if hits
                       else (-1, -1, -1))
        else:
            x, y, z = -1, -1, -1
        pins[spec['map']].append(synthetic_row(
            UNK_EGG, 0, spec['quality'], 0, x, y, z, 'deferred', 'egg',
            f"NOT PLACED. Would dispatch class {cid} "
            f"{class_by_id.get(cid, '?')}. " + spec['why'], spec['reads']))

    # --- dangling: compiled classes that were never placed ---------------
    placed_egg_qualities = {
        it.quality for items in maps.values() for it in items
        if it.shape == UNK_EGG}
    deferred_q = {s['quality'] for s in DEFERRED}
    for name, cid in sorted(manifest['classes'].items(), key=lambda kv: kv[1]):
        if not name.startswith('EGG'):
            continue
        q = cid - EGG_CLASS_BASE
        if q in placed_egg_qualities or q in deferred_q:
            continue
        notes['dangling'].append(
            f"{name} (class {cid}, egg quality {q}) is compiled but no "
            f"shape-73 egg on any LV map carries that quality")

    # --- extra citations for rows a test also pins ----------------------
    # Each needle is grepped out of the test at run time, so a renamed
    # constant or a moved assertion shows up as a missing citation rather
    # than as a stale line number.
    RR = os.path.join(_THIS_DIR, 'test_route_reach.py')
    rr_rel = 'agents/map-populator/src/test_route_reach.py'
    extra = [
        (11, lambda r: r['shape'] == 66 and r['quality'] == 299,
         'SEALING_BOULDER_QUALITY = 299',
         ' Route 11 in test_route_reach.py proves BOTH states — plugged '
         'with them, open without — so the pair is frozen at these exact '
         'coordinates.'),
    ]
    for mapnum, pred, needle, tail in extra:
        n = grep_line(RR, needle)
        if n is None:
            notes['surprises'].append(
                f"test_route_reach.py no longer contains {needle!r} — the "
                f"map {mapnum} citation for it is stale")
            continue
        for r in pins[mapnum]:
            if pred(r):
                c = f'{rr_rel}:{n}'
                if c not in r['reads']:
                    r['reads'].append(c)
                if tail:
                    r['why'] += tail
    for r in pins[11]:
        if r['shape'] == 596:
            r['why'] += (' Placed at z=4 on purpose '
                         '(docs/playtest-2026-09-06-step4-talismans.md); '
                         'do not lower them.')
            r['reads'].append(
                'docs/playtest-2026-09-06-step4-talismans.md')

    # --- every scanned filter whose shape is on no LV map at all --------
    on_maps = {it.shape for items in maps.values() for it in items}
    seen = set()
    for f in sorted(filters, key=lambda f: (f['file'], f['line'])):
        if f['type'] in seen:
            continue
        seen.add(f['type'])
        if f['shape'] is None:
            notes['unresolved'].append(
                f"{f['file']}:{f['line']} `{f['type']}` does not resolve "
                f"through TYPE_SHAPES at all")
        elif f['shape'] not in on_maps:
            notes['no_such_shape'].append(
                f"{f['file']}:{f['line']} `{f['type']}` -> shape "
                f"{f['shape']}: that shape is on NO LV map")

    for lst in pins.values():
        lst.sort(key=lambda r: (r['x'], r['y'], r['z'], r['shape'],
                                r['quality']))

    doc = {
        'generated': datetime.date.today().isoformat(),
        'fixed_sha256_prefix': sha_prefix(FIXED),
        'maps': {str(n): pins[n] for n in sorted(pins)},
    }
    return doc, notes


def main():
    doc, notes = build()
    with open(OUT, 'w') as fh:
        json.dump(doc, fh, indent=1, sort_keys=False)
        fh.write('\n')

    print(f"map_pins.json  ({OUT})")
    print(f"  FIXED.DAT sha256 prefix {doc['fixed_sha256_prefix']}")
    total = 0
    for n, rows in doc['maps'].items():
        total += len(rows)
        by_class = {}
        by_kind = {}
        for r in rows:
            by_class[r['class']] = by_class.get(r['class'], 0) + 1
            by_kind[r['kind']] = by_kind.get(r['kind'], 0) + 1
        cls = ', '.join(f"{k} {v}" for k, v in sorted(by_class.items()))
        knd = ', '.join(f"{k} {v}" for k, v in sorted(by_kind.items()))
        print(f"  map {n:>2}: {len(rows):>3} rows  [{cls}]")
        print(f"            {knd}")
    print(f"  total: {total} rows")

    if notes['dangling']:
        print("\n  dangling (a compiled filter or class with nothing to "
              "read):")
        for d in notes['dangling']:
            print(f"    - {d}")
    if notes['no_such_shape']:
        print("\n  filters whose shape is on no LV map (base-game "
              "inventory checks are expected here):")
        for d in notes['no_such_shape']:
            print(f"    - {d}")
    if notes['unresolved']:
        print("\n  types that do not resolve through TYPE_SHAPES:")
        for d in notes['unresolved']:
            print(f"    - {d}")
    if notes['surprises']:
        print("\n  surprises:")
        for s in notes['surprises']:
            print(f"    - {s}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""test_map_constants.py — regression tests for Map* constant resolution
(Fix 2a, 2026-07-27).

Before this fix every Map* name was an unknown identifier compiled as
`push 0`: the LB vision's on-Docks suppression was lost (the guard
compared getMap() against 0 twice) and SHADES.UNK:682 teleported Atli to
map 0 instead of the vale. Values are PINNED against retail bytecode —
storms-chain, coordinate needles, AIRSPEL case-suffix — see MAP_CONSTANTS
in u8c_symbols.py. Unpinned names must keep warning, not guess.

Exits nonzero on any failure.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from u8c_parser import parse_file
from u8c_codegen import CodeGenerator
from u8c_symbols import create_symbol_table, MAP_CONSTANTS


def compile_body(body):
    src = ("class TypeTest inherits Item;\n"
           "process TypeTest::t()\n{\n" + body + "\n}\n")
    f = tempfile.NamedTemporaryFile('w', suffix='.UNK', delete=False,
                                    encoding='latin-1')
    f.write(src)
    f.close()
    ast = parse_file(f.name)
    cg = CodeGenerator(create_symbol_table())
    data = cg.generate_class(ast)
    os.unlink(f.name)
    return bytes(data), cg


PASS = 0
FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"FAIL: {name}")


def push_byte(v):
    return bytes([0x0A, v])


# ── Pinned names emit their pinned value, warning-free ─────────────────
# One representative per evidence class, plus both both-zero disambiguation
# cases (MapLBBlackness=0 must NOT warn; an unknown name pushes 0 AND warns).

for name, val in [('MapDocks', 3),               # needle
                  ('MapLostVale', 10),           # context pin
                  ('MapDaemonsCrag', 12),        # needle x2
                  ('MapEastTenebrae', 41),       # airspel-suffix
                  ('MapPlaneOfEarth47', 47),     # storms; self-naming
                  ('MapGhostRoom', 63)]:         # storms tail
    data, cg = compile_body(f"x : Number;\nx = {name};")
    check(f"{name} -> push byte {val}", push_byte(val) in data)
    check(f"{name} does not warn",
          not any('unknown identifier' in w for w in cg.warnings))

data, cg = compile_body("x : Number;\nx = MapLBBlackness;")
check("MapLBBlackness -> push byte 0 WITHOUT a warning",
      push_byte(0) in data
      and not any('unknown identifier' in w for w in cg.warnings))

# ── The table matches the evidence set exactly ──────────────────────────

check("31 pinned names", len(MAP_CONSTANTS) == 31)
check("ambiguous names are NOT pinned",
      all(n not in MAP_CONSTANTS for n in
          ('MapFishermansReef', 'MapShepherdValley', 'MapEastRoad',
           'MapProgPlayland', 'MapNameHere')))
check("all values are valid byte-size map numbers",
      all(0 <= v <= 63 for v in MAP_CONSTANTS.values()))
check("no duplicate map numbers",
      len(set(MAP_CONSTANTS.values())) == len(MAP_CONSTANTS))

# ── Unpinned Map* names keep the loud fallback ──────────────────────────

for name in ('MapFishermansReef', 'MapNameHere', 'MapTypoVille'):
    data, cg = compile_body(f"x : Number;\nx = {name};")
    check(f"unpinned {name} still warns unknown-identifier",
          any(f"unknown identifier '{name}'" in w for w in cg.warnings))
    check(f"unpinned {name} still pushes 0", push_byte(0) in data)

# ── The AVATAR guard shape: compare against 3 and 0, not 0 and 0 ────────

data, cg = compile_body(
    "if (Avatar.getMap() != MapDocks) and (Avatar.getMap() != MapLBBlackness)"
    " {\n\tx : Number;\n\tx = 1;\n}")
check("guard compares against MapDocks=3", push_byte(3) in data)
check("guard emits no unknown-identifier warnings",
      not any('unknown identifier' in w for w in cg.warnings))

print(f"map-constants: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)

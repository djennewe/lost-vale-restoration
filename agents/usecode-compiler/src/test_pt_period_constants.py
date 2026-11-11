#!/usr/bin/env python3
"""test_pt_period_constants.py — PT_* and day-period constant resolution
(2026-08-12).

Before this fix, all 28 corpus `resetRef(referent, PT_*)` sites compiled
their type argument to `push 0` — and killProcesses(objid, 0, ...) matches
nothing, so every one was a silent no-op (`I_resetRef item=106 type=0x0000`
in playtest logs). Likewise every day-period name compiled to 0 =
bloodwatch, so `if (getPeriod() = daytide)` never fired and Atli's schedule
kept his destination at (0,0,0).

Values are PINNED against retail bytecode and engine source — see
PT_CONSTANTS and DAY_PERIOD_CONSTANTS in u8c_symbols.py for the evidence
(33 retail 4-in-a-row resetRef runs; the class 0x00E3 clock whose period
compares are each labeled by the period's own display string). Unpinned
PT_* names (PT_FX, PT_USE, PT_LOOK, ...) must keep warning, not guess.

Exits nonzero on any failure.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from u8c_parser import parse_file
from u8c_codegen import CodeGenerator
from u8c_symbols import (create_symbol_table, PT_CONSTANTS,
                         DAY_PERIOD_CONSTANTS)

PASS = 0
FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")


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


def push_word(v):
    return bytes([0x0B, v & 0xFF, v >> 8])


def push_byte(v):
    return bytes([0x0A, v & 0xFF])


# ── pinned values are exactly the evidence set ─────────────────────────────
check("PT table pins exactly the five evidenced names",
      PT_CONSTANTS == {'PT_DEFAULT': 0x001, 'PT_ANIM': 0x0F0,
                       'PT_BARK': 0x200, 'PT_PATHFIND': 0x204,
                       'PT_ACTIVITY': 0x205})
check("period table pins the six retail clock values",
      DAY_PERIOD_CONSTANTS == {'bloodwatch': 0, 'firstebb': 1, 'daytide': 2,
                               'threemoons': 3, 'lastebb': 4, 'eventide': 5})

# ── PT_* in expression position emits the retail word push ─────────────────
for name, val in PT_CONSTANTS.items():
    data, cg = compile_body(f"resetRef(referent, {name});")
    check(f"{name} -> push word {val:#06x}", push_word(val) in data)
    check(f"{name} compiles without unknown-identifier warning",
          not any(name in w for w in getattr(cg, 'warnings', [])))

# The canonical 4-call kill block emits the retail sequence of immediates.
data, _ = compile_body(
    "resetRef(referent, PT_ACTIVITY);\n"
    "resetRef(referent, PT_PATHFIND);\n"
    "resetRef(referent, PT_ANIM);\n"
    "resetRef(referent, PT_BARK);")
i205 = data.find(push_word(0x205))
i204 = data.find(push_word(0x204))
i0f0 = data.find(push_word(0x0F0))
i200 = data.find(push_word(0x200))
check("kill block emits 0205, 0204, 00F0, 0200 in retail order",
      -1 < i205 < i204 < i0f0 < i200)

# ── day periods emit the retail byte literal ───────────────────────────────
for name, val in DAY_PERIOD_CONSTANTS.items():
    data, cg = compile_body(f"x:Integer;\nx = {name};")
    check(f"{name} -> push byte {val}", push_byte(val) in data)

# ── unpinned PT_* names still warn, still push 0 ───────────────────────────
data, cg = compile_body("resetRef(referent, PT_FX);")
warned = any('PT_FX' in w for w in getattr(cg, 'warnings', []))
check("PT_FX (unpinned) still raises the unknown-identifier warning", warned)

print(f"\n{'OK' if FAIL == 0 else 'FAILED'}: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)

#!/usr/bin/env python3
"""test_multivalue_case.py — multi-value `case "A", "B"` dispatch codegen.

Guards the 2026-08-12 fix for the confirmed in-game defect: ATLI's
`case "Tell me more of the test.", "Tell me again of the Rite of Passage."`
never dispatched — the pick looped silently back to the ask list.

The old emission OR-branched per value with not(0x30) + jne-to-body, a shape
that appears NOWHERE in the retail FLX. The retail idiom, verified at three
independent base-game sites (0x02C4:04B6, 0x0405:2C6E, 0x0408:413C), is:

    push answer / push "A" / strcmp        (0x26)
    push answer / push "B" / strcmp
    or                                     (0x34, one per extra value)
    jne next_case                          (0x51)

These tests assert (1) the emitted byte shape matches retail, (2) the old
not-based shape is gone, and (3) the construct executes correctly in the
simulator for every value and for a mismatch.

Exits nonzero on any failure.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from u8c_parser import parse_file
from u8c_codegen import CodeGenerator
from u8c_symbols import create_symbol_table
from u8c_sim import UCSim, SimWorld

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


def compile_src(src):
    f = tempfile.NamedTemporaryFile('w', suffix='.UNK', delete=False,
                                    encoding='latin-1')
    f.write(src)
    f.close()
    ast = parse_file(f.name)
    cg = CodeGenerator(create_symbol_table())
    data = cg.generate_class(ast)
    os.unlink(f.name)
    return data


def op_string(text):
    """The 0D push-string encoding for `text`: u16le length (excluding the
    terminator), latin-1 bytes, NUL — as seen in every retail listing."""
    b = text.encode('latin-1')
    return bytes([0x0D, len(b) & 0xFF, len(b) >> 8]) + b + b'\x00'


TWO_SRC = """class TypeTest inherits Item;
process TypeTest::use()
{
    answer:String;
    answer = "B";
    switch answer
    {
        case "A", "B"
        {
            bark("hit");
        }
        case "C"
        {
            bark("other");
        }
    }
}
"""

data = compile_src(TWO_SRC)

# ── 1. Byte shape: strcmp, <push answer, push "B">, strcmp, or, jne ────────
pa = data.find(op_string("A"))
pb = data.find(op_string("B"), data.find(op_string("B")) + 1)  # 2nd "B": the case value
pc = data.find(op_string("C"))
check("all three case strings present", pa > 0 and pb > 0 and pc > 0)

after_a = data[pa + len(op_string("A")):]
check("strcmp follows value A", after_a[:1] == b'\x26')

after_b = data[pb + len(op_string("B")):]
check("strcmp/or follow value B", after_b[:2] == b'\x26\x34')
check("jne follows the or", after_b[2:3] == b'\x51')

# The old shape put not(0x30) directly after a strcmp. It must be gone.
check("no strcmp+not anywhere (old OR-branch shape)",
      data.find(b'\x26\x30') == -1)

# Single-value case "C" keeps the plain shape: strcmp, jne — no or.
after_c = data[pc + len(op_string("C")):]
check("single-value case unchanged (strcmp, jne)",
      after_c[:1] == b'\x26' and after_c[1:2] == b'\x51')


# ── 2. Execution: each value dispatches; a mismatch falls through ──────────
class _OneClassFlx:
    """Duck-typed FlexArchive holding a single compiled class blob at
    class id 0 (FLX entry 2 — the sim reads entry class_id + 2)."""
    def __init__(self, blob):
        self._blob = blob

    def get_object(self, entry):
        return self._blob if entry == 2 else b''


THREE_SRC_TMPL = """class TypeTest inherits Item;
process TypeTest::use()
{{
    answer:String;
    answer = "{pick}";
    switch answer
    {{
        case "A", "B", "C"
        {{
            bark("multi");
        }}
        case "D"
        {{
            bark("single");
        }}
    }}
}}
"""


def run_pick(pick):
    blob = compile_src(THREE_SRC_TMPL.format(pick=pick))
    world = SimWorld()
    item = world.add(1, objid=1)
    # Mirror UCSim.__init__ exactly, minus the disk FlexArchive read —
    # every field below exists there; a new field added to __init__ will
    # surface here as an AttributeError, which is the correct failure.
    sim = UCSim.__new__(UCSim)
    sim.flx = _OneClassFlx(blob)
    sim.world = world
    sim.globals = bytearray(0x1000)
    sim.trace = False
    sim.trace_log = []
    sim.pid = 0x0123
    sim.barks = []
    sim.spawns = []
    sim.calls = []
    sim.intrinsic_log = []
    sim.warnings = []
    sim.created = []
    sim.teleports = []
    sim.strings = {}
    sim._next_string = 1
    sim._next_pid = 0x200
    sim.answer_script = []
    sim.asks = []
    sim.call_returns = {}
    sim.process_result = 0
    sim.lists = {}
    sim._next_list_id = 0x40
    sim.follow_spawns = False
    sim._intrinsics = sim._load_intrinsic_names()
    sim.run_event(0, 0, item.objid, event=1)
    return [t for (_o, t) in sim.barks]


for pick, want in (("A", ["multi"]), ("B", ["multi"]), ("C", ["multi"]),
                   ("D", ["single"]), ("E", [])):
    try:
        barks = run_pick(pick)
        check(f"pick {pick!r} -> barks {want}", barks == want)
    except Exception as exc:
        check(f"pick {pick!r} (sim error: {exc})", False)

print(f"\n{'OK' if FAIL == 0 else 'FAILED'}: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)

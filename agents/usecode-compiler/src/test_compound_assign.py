#!/usr/bin/env python3
"""test_compound_assign.py — regression tests for compound assignment codegen.

Guards adversarial-review finding C1 (2026-07-19): compound `+=` / `-=` on
numeric and String locals (and globals) silently miscompiled to plain
assignment, emitting NO arithmetic. `x += 16` became `x = 16`; `s += "?"`
freed s and stored only "?". Shipped LOST VALE/FREE.UNK relies on
`quan-=666`, `charge+=mana/5`, `x+=16`, etc.

Asserts the correct opcodes and operand order, matching the base game
(uc_machine.cpp: sub 0x1C pushes `first_pushed - second_pushed`; concat 0x16
extends the first-pushed string). Exits nonzero on any failure.
"""
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from u8c_parser import parse_file
from u8c_codegen import CodeGenerator
from u8c_symbols import create_symbol_table


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
    return data, cg


def find_sub(hay, needle):
    """Return the index of the byte-subsequence `needle` in `hay`, or -1."""
    for i in range(len(hay) - len(needle) + 1):
        if hay[i:i + len(needle)] == needle:
            return i
    return -1


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


# ── numeric += : push var; push k; add(0x14); pop var ────────────────────────
# locals here land at BP-02 (first local). push [BP+off] = 3F off;
# push byte k = 0A kk; add = 14; pop [BP+off] = 01 off.
data, _ = compile_body("x : Number;\n  x = 5;\n  x += 16;\n  x -= 3;")
plus = bytes([0x3F, 0xFE, 0x0A, 0x10, 0x14, 0x01, 0xFE])   # push x;push 16;add;pop x
minus = bytes([0x3F, 0xFE, 0x0A, 0x03, 0x1C, 0x01, 0xFE])  # push x;push 3;sub;pop x
check("numeric += emits push-var/push-rhs/add/pop-var", find_sub(data, plus) >= 0)
check("numeric -= emits push-var/push-rhs/sub/pop-var", find_sub(data, minus) >= 0)

# The C1 bug shape: `x += 16` == push 16; pop x with NO arithmetic. Assert that
# the miscompiled sequence (push byte 16; pop [BP-02]) does NOT appear standalone
# as the whole statement — i.e. an add opcode sits between the pushes and pop.
check("numeric += is NOT bare assignment (add opcode present)", 0x14 in data)
check("numeric -= is NOT bare assignment (sub opcode present)", 0x1C in data)

# ── string += : push string; push string; concat(0x16); free; pop ────────────
data, _ = compile_body('s : String;\n  s = "hi";\n  s += "?";')
check("string += emits concat 0x16", 0x16 in data)
# base-game append idiom ends: concat(0x16); free string [off](0x62 off);
# pop [off](0x01 off) — with the SAME local offset byte. Search offset-
# agnostically since a String local's BP slot is not fixed.
def has_concat_free_pop_idiom(hay):
    for i in range(len(hay) - 4):
        if (hay[i] == 0x16 and hay[i + 1] == 0x62 and
                hay[i + 3] == 0x01 and hay[i + 2] == hay[i + 4]):
            return True
    return False
check("string += uses concat/free-string/pop idiom", has_concat_free_pop_idiom(data))

# ── ^= on a numeric has no meaning: warn, emit nothing (no silent miscompile) ─
data, cg = compile_body("x : Number;\n  x = 5;\n  x ^= 1;")
check("numeric ^= records a warning", any("^=" in w for w in cg.warnings))

# ── a plain '=' still works (no regression) ──────────────────────────────────
data, _ = compile_body("x : Number;\n  x = 7;")
check("plain assignment still emits push-const/pop", find_sub(data, bytes([0x0A, 0x07, 0x01, 0xFE])) >= 0)


print()
print("=" * 50)
print(f"compound-assign: {PASS} passed, {FAIL} failed")
print("=" * 50)
sys.exit(1 if FAIL else 0)

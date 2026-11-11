#!/usr/bin/env python3
"""test_pragma.py — regression tests for statement-form process-type
pragma codegen (`[[PT_DEFAULT, NULL_REF]];` et al. -> `set info`).

Guards the 2026-07-26 first-map-change collapse: these pragmas compiled
to NOTHING, so AVATAR::schedule()'s Lord British vision kept its event
identity (itemNum 1, type 0x210) and was killed by the engine's
map-change sweep (world.cpp switchMap -> killProcessesNotOfType(0, 1))
inside its own Npc::teleport() call — the teleport-back was never
reached and the Avatar was stranded on map 0.

The emitted encodings are pinned against retail bytecode by exact
per-class site counts (see the PRAGMA_TYPES comment in u8c_codegen.py).
Only PT_DEFAULT (= 1) is pinned; all other PT_* types must keep
compiling to nothing, loudly, until pinned the same way.

Exits nonzero on any failure.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from u8c_parser import parse_file
from u8c_codegen import CodeGenerator
from u8c_symbols import create_symbol_table


def compile_proc(body, proc='t'):
    """Compile a one-process class; proc='use' makes it an event process."""
    src = ("class TypeTest inherits Item;\n"
           f"process TypeTest::{proc}()\n{{\n{body}\n}}\n")
    f = tempfile.NamedTemporaryFile('w', suffix='.UNK', delete=False,
                                    encoding='latin-1')
    f.write(src)
    f.close()
    ast = parse_file(f.name)
    cg = CodeGenerator(create_symbol_table())
    data = cg.generate_class(ast)
    os.unlink(f.name)
    return bytes(data), cg


# Pinned encodings (type pushed first; engine's 0x77 pops itemNum, then type)
SETINFO_NULL = bytes([0x0A, 0x01, 0x0A, 0x00, 0x77])
SETINFO_REFERENT = bytes([0x0A, 0x01, 0x40, 0x06, 0x4C, 0x02, 0x77])
SETINFO_AVATAR = bytes([0x0A, 0x01, 0x0A, 0x01, 0x77])
# Event-preamble tail: set info; process exclude
PREAMBLE_TAIL = bytes([0x77, 0x78])

PASS = 0
FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"FAIL: {name}")


def count_sub(hay, needle):
    n = i = 0
    while True:
        i = hay.find(needle, i)
        if i < 0:
            return n
        n += 1
        i += 1


# ── Accepted forms emit the pinned bytes ────────────────────────────────

for spelling in ("[[PT_DEFAULT, NULL_REF]];",
                 "[[PT_DEFAULT,NULL_REF]];",
                 "[[PT_DEFAULT,NUL_REF]];",      # TESTPLAN.UNK:245 typo
                 "[[PT_DEFAULT,0]];"):           # ZEALSHLD.UNK:32
    data, cg = compile_proc(spelling)
    check(f"null form {spelling!r} emits 0A 01 0A 00 77",
          count_sub(data, SETINFO_NULL) == 1)
    check(f"null form {spelling!r} warns nothing",
          not any('DROPPED PRAGMA' in w for w in cg.warnings))

for spelling in ("[[PT_DEFAULT, referent]];",
                 "[[PT_DEFAULT, referent:Referent]];"):
    data, cg = compile_proc(spelling)
    check(f"referent form {spelling!r} emits 0A 01 40 06 4C 02 77",
          count_sub(data, SETINFO_REFERENT) == 1)

data, cg = compile_proc("[[PT_DEFAULT, Avatar:Referent]];")
check("Avatar:Referent emits 0A 01 0A 01 77",
      count_sub(data, SETINFO_AVATAR) == 1)

# ── Position: in an event process the pragma lands AFTER the preamble ──

data, cg = compile_proc("[[PT_DEFAULT, NULL_REF]];", proc='use')
pre = data.find(PREAMBLE_TAIL)
prag = data.find(SETINFO_NULL)
check("event process keeps its preamble set info", pre >= 0)
check("pragma set info present in event process", prag >= 0)
check("pragma re-brand comes after the preamble brand", prag > pre)

# ── PT_ACTIVITY (pinned 2026-10-02): retail pushes 0x205 as a word ──
# Count-matched against retail in 11 NPC classes (u8c_codegen.py,
# PRAGMA_TYPES). Before the pin it was dropped, and ARAMINA's spawned
# atHome() ran as item 0, type 0, which nothing kills.

SETINFO_ACTIVITY_REF = bytes.fromhex('0B050240064C0277')
data, cg = compile_proc("[[PT_ACTIVITY, referent]];")
check("PT_ACTIVITY referent emits 0B 05 02 40 06 4C 02 77",
      count_sub(data, SETINFO_ACTIVITY_REF) == 1)
check("PT_ACTIVITY referent warns nothing",
      not any('DROPPED PRAGMA' in w for w in cg.warnings))

# ── Deferred forms: byte-identical to no pragma at all, plus a warning ──

for spelling in ("[[PT_BARK, Avatar:Referent]];",
                 "[[PT_FX, NULL_REF]];",
                 "[[PT_DEFAULT, ball.referent]];",  # expression referent
                 "[[PT_ANIM_UNK,0]];"):
    with_pragma, cg = compile_proc(spelling + "\n\tbark(\"x\");")
    without, _ = compile_proc("bark(\"x\");")
    check(f"deferred {spelling!r} emits nothing", with_pragma == without)
    check(f"deferred {spelling!r} warns loudly",
          any('DROPPED PRAGMA' in w for w in cg.warnings))

print(f"pragma set-info: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)

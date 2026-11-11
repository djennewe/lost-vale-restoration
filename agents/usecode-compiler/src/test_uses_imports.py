#!/usr/bin/env python3
"""
test_uses_imports.py — Acceptance tests for `uses`-import cross-class
calls (shared/docs/wiring.md "Blocking discovery: uses imports are not
implemented").

Compiles a tiny synthetic provider + consumer pair from in-memory source
(never touches the real corpus) and asserts the exact emitted bytecode for:
  1. A plain function call resolving to a cross-class `0x11 call` (word
     retval, since the provider declares `:Number`).
  2. Argument passing (2 bytes per arg) and `add sp` cleanup.
  3. Arity-based overload resolution — a 2-arg and a 3-arg process sharing
     a name (mirrors FREE.UNK's safePlaySFX(2 args) vs safePlaySFX(3
     args)) resolve to two DIFFERENT provider offsets.
  4. The spawn form (`spawn f(...) -> return;`) emitting `0x57 spawn` with
     the provider's class id : offset and this_size=0x00 (bare routines
     take no implicit `this` — confirmed against base-game MYTHRAN calling
     FREE's give()/getPeriod(), which push only their declared args).
  5. Same-class resolution (no `uses` needed): a consumer calling its own
     earlier-defined routine emits a same-class `0x11 call` against its
     own class id — this is the FREE.UNK getHour()/getPeriod() pattern.
  6. A still-unresolved call (no provider, no same-class match) keeps
     warning exactly as before — the "no worse than before" guarantee.
  7. The class_name_override flow (how build_eusecode.py really compiles
     FREE.UNK — as the NEW manifest-pinned class LVFREE, because retail
     FREE/0x581 has 190 retail caller classes at hardcoded offsets and
     must ship byte-identical; see UNSAFE_TO_REPLACE there): the provider
     compiles under an override name registered at a pinned id, every
     provider symbol and consumer call targets THAT pinned id (never the
     basename's retail class id), while the provider registry key stays
     the file's basename so consumers' `uses "..."` directives work
     unchanged.

Plain script, no pytest dependency: exit 0 on pass, exit 1 on fail.
Mirrors the style of test_patch_mythran.py / test_manifest.py.
"""

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from u8c_parser import parse_source
from u8c_codegen import CodeGenerator
from u8c_symbols import create_symbol_table

_disasm_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            '..', '..', 'usecode-disasm', 'src')
sys.path.insert(0, _disasm_dir)
from u8_usecode_disasm import UsecodeDisassembler

PASS_COUNT = 0
FAIL_COUNT = 0


def check(label, cond, detail=''):
    global PASS_COUNT, FAIL_COUNT
    if cond:
        PASS_COUNT += 1
        print(f"  PASS  {label}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL  {label}  {detail}")


# ─── Fixture sources ─────────────────────────────────────────────────────

# Provider — mirrors FREE.UNK's shape: bare routine/process defs, no
# `class` header, an arity-overloaded process (safePlaySFX(2) vs (3)), and
# one routine (addTwo) whose second param exercises the multi-arg
# BP-offset stride.
PROVIDER_SRC = """\
routine getValue():Number {
\treturn 42;
}

routine addTwo(a:Number, b:Number):Number {
\treturn a + b;
}

process fireAlarm(level:Number) {
\treturn;
}

process playFX(soundNum:Number, priority:Number) {
\treturn;
}

process playFX(soundNum:Number, priority:Number, volume:Number) {
\treturn;
}
"""

# Consumer — `uses` the provider above (basename "testprov"), plus one
# same-class call (helper() defined before use(), same pattern as FREE's
# own getPeriod() calling getHour()) and one genuinely unresolved call.
CONSUMER_SRC = """\
uses "testprov";

typeclass TypeTestConsumer inherits Item {
\troutine helper();
\tprocess use();
}

routine TypeTestConsumer::helper() {
\treturn;
}

process TypeTestConsumer::use() {
\tx : Number = getValue();
\ty : Number = addTwo(3,4);
\tspawn playFX(100,200) -> return;
\tspawn playFX(100,200,50) -> return;
\tspawn fireAlarm(9) -> return;
\thelper();
\tfireAlarm(3);
\ttotallyUnknownRoutine(1,2);
}
"""

# Forward same-class spawn — mirrors LORDBRIT.UNK exactly: use() (defined
# FIRST) spawns puppet() (defined SECOND, i.e. AFTER use() in source
# order), and puppet() also calls a plain function (helper2, likewise
# defined after it) to prove forward resolution works for both the spawn
# form AND a bare same-class call, not just spawn.
FORWARD_SRC = """\
typeclass TypeForwardTest inherits Item {
\tprocess use();
\tprocess puppet(lb:Item);
\troutine helper2();
}

process TypeForwardTest::use() {
\tlb : Item;
\tspawn puppet(lb) -> return;
\treturn;
}

process TypeForwardTest::puppet(lb:Item) {
\thelper2();
\treturn;
}

routine TypeForwardTest::helper2() {
\treturn;
}
"""


def find_all(haystack, needle):
    out = []
    start = 0
    while True:
        i = haystack.find(needle, start)
        if i < 0:
            return out
        out.append(i)
        start = i + 1


# The provider's PINNED class id under its override name — mirrors
# build_eusecode.py compiling FREE.UNK as LVFREE at a manifest-pinned id.
# Deliberately NOT a retail base-game class id.
PROVIDER_PINNED_ID = 0x0700
RETAIL_FREE_ID = 0x0581



# ─── `uses` selects an overloaded intrinsic (2026-09-21) ─────────────────
# Book::read (0x6E), Scroll::read (0x6F), Grave::read (0x70) and
# Plaque::read (0x71) take the same shape of call, so a bare read() cannot
# be told apart by name or by arity and the first-registered slot wins.
# The 1994 sources choose with the include file's name: SGBOOK.UNK says
# `uses "books"`, PLAQUENS.UNK says `uses "plaque"`. Before this landed,
# PLAQUENS compiled 70 calls to Grave::read.
READER_SRC = """\
uses "item";
uses "%s";

typeclass TypeTestReader inherits Item {
\tprocess use();
}

process TypeTestReader::use() {
\t%s
}
"""


def _calli_ids(data):
    ids, i = [], 0
    while i < len(data) - 3:
        if data[i] == 0x0F:
            ids.append(data[i + 2] | (data[i + 3] << 8))
            i += 4
        else:
            i += 1
    return ids


def check_uses_picks_intrinsic():
    for used, call, want, name in (('scroll', 'read("TEXT");', 0x6F, 'Scroll::read'),
                                   ('books', 'read("TEXT");', 0x6E, 'Book::read'),
                                   ('plaque', 'read(16,"TEXT");', 0x71, 'Plaque::read'),
                                   ('grave', 'read(16,"TEXT");', 0x70, 'Grave::read')):
        ast = parse_source(READER_SRC % (used, call), filename='READER.UNK')
        data = CodeGenerator(create_symbol_table()).generate_class(ast)
        ids = _calli_ids(data)
        check(f'uses "{used}" makes a bare read() compile to {name} '
              f'(0x{want:02X})', want in ids, f'calli ids {[hex(i) for i in ids]}')

    # No matching `uses` line: resolution is exactly what it was, the
    # first-registered same-arity slot.
    ast = parse_source(READER_SRC % ('flags', 'read("TEXT");'),
                       filename='READER.UNK')
    data = CodeGenerator(create_symbol_table()).generate_class(ast)
    ids = _calli_ids(data)
    check('a file with no reader `uses` line still resolves as before '
          '(Book::read, 0x6E)', 0x6E in ids,
          f'calli ids {[hex(i) for i in ids]}')


def main():
    symbols = create_symbol_table()

    # Compile the provider FIRST (matches build_eusecode.py's provider
    # pre-pass ordering requirement) so its function offsets are
    # registered into `symbols` before the consumer compiles. Uses the
    # class_name_override flow exactly the way build_eusecode.py does for
    # FREE.UNK -> LVFREE: register the override name at its pinned id,
    # then compile the headerless provider file under that override.
    symbols.register_class('LVTESTPROV', PROVIDER_PINNED_ID)
    provider_ast = parse_source(PROVIDER_SRC, filename='TESTPROV.UNK')
    provider_cg = CodeGenerator(symbols, filename='TESTPROV.UNK',
                                class_name_override='LVTESTPROV')
    provider_bytecode = provider_cg.generate_class(provider_ast)
    check("provider compiles with zero warnings",
          provider_cg.warnings == [], provider_cg.warnings)

    provider_class_id = provider_cg._classid
    check("provider compiled under the override's PINNED id "
          f"(0x{PROVIDER_PINNED_ID:04X}), not the basename's id",
          provider_class_id == PROVIDER_PINNED_ID,
          hex(provider_class_id))
    check("provider class id is NOT retail FREE (0x0581) — the "
          "UNSAFE_TO_REPLACE guarantee",
          provider_class_id != RETAIL_FREE_ID)
    check("provider registry key is still the file BASENAME ('testprov'), "
          "so `uses \"testprov\"` resolves",
          'testprov' in symbols.providers
          and symbols.providers['testprov']['class_id'] == PROVIDER_PINNED_ID,
          list(symbols.providers.keys()))
    getvalue_entries = provider_cg._function_table.get('getvalue', {})
    addtwo_entries = provider_cg._function_table.get('addtwo', {})
    playfx_entries = provider_cg._function_table.get('playfx', {})
    firealarm_entries = provider_cg._function_table.get('firealarm', {})

    check("getValue() registered with arity 0, word return",
          getvalue_entries.get(0, (None, None))[1] == 'word',
          getvalue_entries)
    check("addTwo(a,b) registered with arity 2, word return",
          addtwo_entries.get(2, (None, None))[1] == 'word',
          addtwo_entries)
    check("playFX overload set has BOTH arity 2 and arity 3",
          set(playfx_entries.keys()) >= {2, 3}, playfx_entries)
    check("playFX(2) and playFX(3) overloads have DIFFERENT offsets",
          playfx_entries.get(2, (None,))[0] != playfx_entries.get(3, (None,))[0],
          playfx_entries)
    check("fireAlarm(level) registered with arity 1 as a process "
          "(spawned, never called)",
          firealarm_entries.get(1, (None, None))[1] == 'process',
          firealarm_entries)

    # Register the consumer's own class id (build_eusecode.py does this
    # via manifest pins / LV_NPC_SHAPES; here it's a direct registration —
    # exercises the SAME get_class_id() path codegen consults).
    symbols.register_class('TypeTestConsumer', 0x0600)

    consumer_ast = parse_source(CONSUMER_SRC, filename='TESTCONS.UNK')
    consumer_cg = CodeGenerator(symbols, filename='TESTCONS.UNK')
    consumer_bytecode = consumer_cg.generate_class(consumer_ast)

    warnings = consumer_cg.warnings
    check("consumer has exactly one warning (totallyUnknownRoutine)",
          len(warnings) == 1 and 'totallyUnknownRoutine' in warnings[0],
          warnings)

    # ─── 1/2. Plain call: getValue() — 0 args, word retval ──────────────
    getvalue_off = getvalue_entries[0][0]
    call_getvalue = struct.pack('<BHH', 0x11, provider_class_id, getvalue_off)
    hits = find_all(consumer_bytecode, call_getvalue)
    check("getValue() call site: `11 <class> <offset>` present exactly once",
          len(hits) == 1, hits)
    if hits:
        after = consumer_bytecode[hits[0] + 5:hits[0] + 6]
        check("getValue() call has NO `add sp` (0 args) — next byte is "
              "push retval (0x5E)", after == b'\x5E', after.hex())

    # ─── 2. addTwo(3,4) — 2 args (2 bytes each), add sp -4, word retval ──
    addtwo_off = addtwo_entries[2][0]
    call_addtwo = struct.pack('<BHH', 0x11, provider_class_id, addtwo_off)
    hits = find_all(consumer_bytecode, call_addtwo)
    check("addTwo(3,4) call site present exactly once", len(hits) == 1, hits)
    if hits:
        # Args push RIGHT-TO-LEFT (push byte 4, then push byte 3) so the
        # callee's first declared param lands at BP+06 = last word pushed.
        # Retail proof: STRATOS create(TypeMagicSparkle,11) emits
        # `push byte 11; push 024Bh` (frame then shape), and a retail
        # Camera::move_to call site pushes speed/z/y/x — the engine reads
        # the FIRST declared arg from the top of the stack (args+0).
        before = consumer_bytecode[hits[0] - 4:hits[0]]
        check("addTwo(3,4) pushes args right-to-left (push 4, then push 3) "
              "right before the call", before == bytes([0x0A, 4, 0x0A, 3]),
              before.hex())
        cleanup = consumer_bytecode[hits[0] + 5:hits[0] + 8]
        check("addTwo(3,4) cleanup: add sp -4 (0xFC), then push retval (word)",
              cleanup == bytes([0x6E, 0xFC, 0x5E]), cleanup.hex())

    # ─── 3. Overload resolution: playFX(2 args) vs playFX(3 args) ───────
    off2 = playfx_entries[2][0]
    off3 = playfx_entries[3][0]
    spawn2 = struct.pack('<BBBHH', 0x57, 4, 0x00, provider_class_id, off2)
    spawn3 = struct.pack('<BBBHH', 0x57, 6, 0x00, provider_class_id, off3)
    check("spawn playFX(100,200) resolves to the 2-arg overload's offset "
          "(this_size=0x00, arg_bytes=4)", spawn2 in consumer_bytecode)
    check("spawn playFX(100,200,50) resolves to the 3-arg overload's "
          "offset (this_size=0x00, arg_bytes=6) — DIFFERENT call site "
          "than the 2-arg spawn above",
          spawn3 in consumer_bytecode and spawn2 != spawn3)

    # ─── 4. Spawn form for a single-arg provider process ─────────────────
    fa_off = firealarm_entries[1][0]
    spawn_fa = struct.pack('<BBBHH', 0x57, 2, 0x00, provider_class_id, fa_off)
    check("spawn fireAlarm(9) emits `57 <arg_bytes=2> <this_size=0> "
          "<class> <offset>`", spawn_fa in consumer_bytecode)
    # Retail `spawn f(..) -> return;` (FREE 0x581 37EF flameBlast(p)):
    # args / 0C 00000000 / 57 / 6E / 5E / 12 — no push pid, the caller
    # does not wait. The null this dword is load-bearing: opcode 0x57
    # pop4's a this pointer even with this_size=0.
    fa_hits = find_all(consumer_bytecode, spawn_fa)
    if fa_hits:
        pre = consumer_bytecode[fa_hits[0] - 7:fa_hits[0]]
        check("spawn fireAlarm(9) prelude: push byte 9, push dword 0 null "
              "this (0C 00000000) right before the spawn, no push pid",
              pre == bytes([0x0A, 9, 0x0C, 0, 0, 0, 0])
              and consumer_bytecode[fa_hits[0] - 8] != 0x59, pre.hex())
        post = consumer_bytecode[fa_hits[0] + 7:fa_hits[0] + 11]
        check("spawn fireAlarm(9) postlude: add sp -2, push retval, "
              "pop temp",
              post == bytes([0x6E, 0xFE, 0x5E, 0x12]), post.hex())

    # ─── 5. Same-class resolution: use() calling its own helper() ───────
    helper_entries = consumer_cg._function_table.get('helper', {})
    check("helper() registered in the CONSUMER's own function table "
          "(same-class resolution, no `uses` needed)",
          0 in helper_entries, helper_entries)
    if 0 in helper_entries:
        helper_off = helper_entries[0][0]
        consumer_class_id = consumer_cg._classid
        check("same-class call targets the CONSUMER's own class id, not "
              "the provider's", consumer_class_id == 0x0600)
        call_helper = struct.pack('<BHH', 0x11, consumer_class_id, helper_off)
        check("helper() call site: same-class `11 <own class> <offset>` "
              "present", call_helper in consumer_bytecode)

    # A plain `fireAlarm(3);` names a PROCESS: retail spawns and waits on
    # it (FREE 0x581 scrollBack 1CB9-1CD8 runs `scrollTo(...)` that way),
    # never `call`s it.
    if 1 in firealarm_entries:
        fa3 = (bytes([0x59, 0x0A, 3, 0x0C, 0, 0, 0, 0]) +
               struct.pack('<BBBHH', 0x57, 2, 0x00, provider_class_id,
                           firealarm_entries[1][0]) +
               bytes([0x6E, 0xFE, 0x5E, 0x54, 1, 1, 0x12, 0x53]))
        check("plain fireAlarm(3) call to a process: push pid; arg; null "
              "this; spawn; add sp; push retval; implies; pop temp; suspend",
              fa3 in consumer_bytecode, consumer_bytecode.hex())
        check("no `call` (0x11) into the process fireAlarm",
              struct.pack('<BHH', 0x11, provider_class_id,
                          firealarm_entries[1][0]) not in consumer_bytecode)

    # ─── 6. Still-unresolved call keeps warning, emits no bytecode ───────
    # totallyUnknownRoutine(1,2) must not have produced ANY 0x11/0x57
    # opcode, and — matching the PRE-EXISTING (unchanged by this work)
    # "unknown function" fallback — its args are never pushed either, so
    # `push byte 1 / push byte 2` (0A 01 0A 02) must NOT appear anywhere
    # in the compiled class (that exact byte pair also can't arise
    # elsewhere in this fixture, since no other call passes literals 1,2).
    check("unresolved call: args not pushed, no call opcode emitted "
          "(only the warning above is a trace of it) — behavior "
          "unchanged from before this work",
          bytes([0x0A, 1, 0x0A, 2]) not in consumer_bytecode)

    # ─── Sanity: the whole consumer class disassembles cleanly ──────────
    d = UsecodeDisassembler()
    code_blob = consumer_bytecode[0x0C:]
    instrs = d.disassemble_bytecode(code_blob, start_offset=0x80)
    bad = [i for i in instrs if i.mnemonic == 'db']
    check("consumer class disassembles with no unknown-opcode ('db') "
          "fallback instructions (Gate 6 shape)", not bad, bad)

    # ─── 7. Forward same-class spawn (uses-imports work item 4) ─────────
    # LORDBRIT.UNK's exact shape: use() (compiled FIRST) spawns puppet()
    # (compiled SECOND) — before this work, _resolve_function had no way
    # to know puppet existed yet, so the spawn silently emitted nothing.
    symbols.register_class('TypeForwardTest', 0x0650)
    forward_ast = parse_source(FORWARD_SRC, filename='FORWARD.UNK')
    forward_cg = CodeGenerator(symbols, filename='FORWARD.UNK')
    forward_bytecode = forward_cg.generate_class(forward_ast)

    check("forward-spawn fixture compiles with zero warnings (puppet() "
          "resolves even though it's defined AFTER use())",
          forward_cg.warnings == [], forward_cg.warnings)

    puppet_entries = forward_cg._function_table.get('puppet', {})
    helper2_entries = forward_cg._function_table.get('helper2', {})
    check("puppet(lb) registered with arity 1 once compiled",
          1 in puppet_entries, puppet_entries)
    check("helper2() registered with arity 0 once compiled",
          0 in helper2_entries, helper2_entries)

    if 1 in puppet_entries:
        puppet_off = puppet_entries[1][0]
        forward_class_id = forward_cg._classid
        check("forward-spawn fixture compiled under its registered class id",
              forward_class_id == 0x0650, hex(forward_class_id))
        # spawn arg_bytes=2 (lb, 1 word), this_size=0x02 (puppet is a
        # `TypeForwardTest::` method, so it gets retail's method frame and
        # the caller's `this`, since 2026-09-25; retail PLAQUENS 00B5 is
        # the same shape), own class id, puppet's REAL (not
        # placeholder-zero) offset.
        spawn_puppet = struct.pack('<BBBHH', 0x57, 2, 0x02,
                                    forward_class_id, puppet_off)
        check("spawn puppet(lb) resolves to puppet's ACTUAL offset "
              "(not a placeholder/zero) even though puppet() is defined "
              "AFTER use() in source order",
              spawn_puppet in forward_bytecode,
              f"expected offset 0x{puppet_off:04X}")
        # The placeholder-zero form must NOT appear anywhere — proves the
        # fixup actually patched the word rather than leaving it at 0.
        spawn_puppet_zero = struct.pack('<BBBHH', 0x57, 2, 0x02,
                                         forward_class_id, 0)
        check("spawn puppet(lb) does NOT leave the unpatched zero-offset "
              "placeholder in the compiled class",
              spawn_puppet_zero not in forward_bytecode or puppet_off == 0)

    if 0 in helper2_entries:
        helper2_off = helper2_entries[0][0]
        forward_class_id = forward_cg._classid
        call_helper2 = struct.pack('<BHH', 0x11, forward_class_id, helper2_off)
        check("puppet() calling helper2() (forward call, not spawn) also "
              "resolves to helper2's actual offset",
              call_helper2 in forward_bytecode)
        # Method frame (2026-09-25): helper2 is a `TypeForwardTest::`
        # method, so puppet() pushes its own `this` above the (zero) args
        # and pops it after, as retail 057C does at 169A:
        # push dword [BP+06h]; call; add sp -4.
        check("a same-class method call pushes this and pops it after "
              "(40 06 / 11 cls off / 6E FC)",
              b'\x40\x06' + call_helper2 + b'\x6E\xFC' in forward_bytecode)

    d2 = UsecodeDisassembler()
    instrs2 = d2.disassemble_bytecode(forward_bytecode[0x0C:], start_offset=0x80)
    bad2 = [i for i in instrs2 if i.mnemonic == 'db']
    check("forward-spawn fixture disassembles with no unknown-opcode "
          "fallback instructions (Gate 6 shape)", not bad2, bad2)

    check_uses_picks_intrinsic()

    print()
    print("=" * 60)
    if FAIL_COUNT:
        print(f"FAILED: {PASS_COUNT} passed, {FAIL_COUNT} failed")
        print("=" * 60)
        return 1
    print(f"OK: {PASS_COUNT}/{PASS_COUNT} tests passed")
    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())

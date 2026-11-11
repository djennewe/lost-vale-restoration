#!/usr/bin/env python3
"""test_trampoline.py — event-table integrity across trampoline relays.

Guards adversarial-review findings M2 (and the M19 boundary case).

U8 jump offsets are sint16, so a class over ~32KB cannot encode a jump from
one end to the other. `_resolve_with_trampolines()` splices 6-byte relay
blocks into the instruction stream to chain shorter hops. Every splice moves
all code after it 6 bytes later, and labels / string ranges / instruction
starts / fixups are all shifted to match.

The EVENT TABLE was not. Event offsets are captured during codegen and handed
to `build_class()` after resolution, so a relay landing above a later handler
left that handler's table entry pointing 6 bytes short of its real start —
dispatching the event INTO THE MIDDLE OF AN INSTRUCTION, where the VM reads
operand bytes as opcodes. ATLI is the only class large enough to trampoline
today and survives only because its overflow sits in the final function.
Gate 6 cannot catch it: the bytes stay structurally valid, they are simply
entered at the wrong point.

This test builds a class big enough to force relays, with several event
handlers AFTER the overflow, and asserts every event entry still lands
exactly on an instruction boundary.

Exits nonzero on failure.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from u8c_codegen import BytecodeEmitter

PASS = 0
FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}{(' — ' + detail) if detail else ''}")


def build_oversized_class(n_events=4, pad_bytes=40000):
    """Emit a class > 32KB containing ONE jump that spans the whole body, so
    it overflows sint16 and forces relay insertion, with several event
    handlers positioned INSIDE that span (i.e. after the relay lands)."""
    em = BytecodeEmitter()
    events = {}

    # Event 0 at the very start, jumping clear to the end of the class.
    events[0] = em.offset
    em.define_label(em.event_label(0))
    em.emit_jmp_label('__far_end')

    # One contiguous run of padding, with the remaining event handlers
    # sprinkled through it.
    #
    # The padding uses FOUR-byte instructions (0x0F calli, format Bw) on
    # purpose. A relay block is 6 bytes, and 6 % 4 != 0, so an uncorrected
    # event offset lands strictly INSIDE a padding instruction — which is
    # what makes the "lands on an instruction start" assertion meaningful.
    # With 1-byte padding every offset is trivially a boundary and that
    # check passes even with the bug present (verified).
    per_event = pad_bytes // (n_events - 1) // 4
    for i in range(1, n_events):
        for _ in range(per_event):
            em._mark_instr()
            em.emit_byte(0x0F)
            em.emit_byte(0x00)
            em.emit_byte(0x00)
            em.emit_byte(0x00)
        events[i] = em.offset
        em.define_label(em.event_label(i))
        em._mark_instr()
        em.emit_byte(0x50)          # ret — this handler's body

    em.define_label('__far_end')
    em._mark_instr()
    em.emit_byte(0x50)

    data = em.build_class(0, 0, events)
    return em, events, data


def main():
    print("Building an oversized class to force trampoline relays...")
    em, events, data = build_oversized_class()

    relays = len(em._insertions)
    print(f"  class size: {len(data)} bytes, relay blocks inserted: {relays}")
    check("the fixture actually forced trampolines", relays > 0,
          "no relays inserted — the test would prove nothing")

    # Event table is the first 128 bytes after the 12-byte header.
    import struct
    table = data[12:12 + 128]
    instr_starts = set(em._instr_starts)

    all_on_boundary = True
    for eid in sorted(events):
        stored = struct.unpack_from('<I', table, eid * 4)[0]
        code_pos = stored - 0x80
        on_boundary = code_pos in instr_starts
        if not on_boundary:
            all_on_boundary = False
            print(f"       event {eid}: table says 0x{stored:04X} "
                  f"(code +{code_pos}), which is NOT an instruction start")
    check("every event entry lands on an instruction start", all_on_boundary,
          "an event would dispatch mid-instruction (M2)")

    # The first handler sits at the very start, before any relay, so its
    # offset must be untouched; later handlers must have MOVED.
    first = struct.unpack_from('<I', table, 0)[0]
    check("first handler offset unchanged", first == events[0],
          f"expected 0x{events[0]:04X}, got 0x{first:04X}")

    moved = 0
    for eid in sorted(events):
        if eid == 0:
            continue
        stored = struct.unpack_from('<I', table, eid * 4)[0]
        if stored > events[eid]:
            moved += 1
    check("later handlers shifted past the inserted relays", moved > 0,
          "no later handler moved — the correction is not being applied")

    # Sanity: shifting must be a no-op when nothing was inserted.
    em2 = BytecodeEmitter()
    ev2 = {0: em2.offset}
    em2.emit_byte(0x50)
    out = em2.shift_event_offsets(ev2)
    check("no-trampoline case passes offsets through unchanged", out == ev2)

    print()
    print("=" * 52)
    print(f"trampoline event-table: {PASS} passed, {FAIL} failed")
    print("=" * 52)
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())

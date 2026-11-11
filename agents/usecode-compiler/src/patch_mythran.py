#!/usr/bin/env python3
"""
patch_mythran.py — Wire the Lost Vale intro dialogue into the base Mythran NPC.

Mythran (base class 0x421) is a ~41 KB usecode class with no recovered high-level
source, so it cannot be recompiled from a .UNK. Instead we surgically append a
replacement use() handler at the end of the class and repoint event 01 to it,
leaving every existing instruction (and therefore every internal jump offset)
untouched.

The appended handler is:

    new_use:
        init 08
        push global lbDone
        jne .stock                 ; LB message not delivered -> stock Mythran
        <copied face-setup preamble>   ; verbatim bytes from the original use()
        push dword [BP+06]          ; this (the engine pushed it for new_use)
        call TypeMythranLVDlg::use  ; absolute call -> LV dialogue (this = Mythran)
        add sp -4
        push global mythranStockVisit
        jne .done                  ; LV dialogue did not request stock handoff
        push byte 0
        pop global mythranStockVisit   ; consume the handoff request
    .stock:
        push dword [BP+06]          ; this
        call MYTHRAN::use@0x208C    ; absolute call -> original conversation, intact
        add sp -4
    .done:
        ret
        end

Routing (DD-005a with stock passthrough):
  * lbDone clear -> stock Mythran, untouched.
  * lbDone set   -> TypeMythranLVDlg::use() always runs. It plays the full LV
    intro until mythranIntroDone is set, then a short follow-up menu (doors
    location, key hint) on later visits — so the key hint stays reachable.
  * If the LV dialogue set mythranStockVisit ("Let us speak of other matters."),
    the wrapper clears the flag and chains straight into the stock conversation,
    so the full base-game Mythran remains available forever.

Calling convention (verified against base-game bytecode, e.g. class 0x0044
call sites): caller pushes `this` as a dword from [BP+06], and pops the 4
argument bytes with `add sp -4` after the call returns.

Implementation (M0.8): `build_new_use()` emits the handler above through
`u8c_codegen.BytecodeEmitter` (emit_init/emit_push_global/emit_jne_label/
emit_push_dword_bp/emit_call/emit_add_sp/emit_push_byte/emit_pop_global/
emit_ret/emit_end, with the two `jne`s resolved via the emitter's
label/fixup machinery) rather than hand-rolled opcode/operand byte literals.
The copied face-setup preamble is still appended verbatim (there is nothing
to encode -- it is opaque bytes from the original class). This is the
successor to an earlier hand-rolled version that shipped the M0.1 `this`-push
bug; the emitter path is verified byte-identical to that version's corrected
(post-M0.1) output for both the real deployment parameters and synthetic
parameter sets (see test_patch_mythran.py's byte-identity regression test).

Why this is safe:
  * Only *appended* bytes + the event-01 table entry + the header total_size
    change. No existing instruction moves, so no relative jump breaks.
  * The only control transfers are two short forward `jne`s (in range) and two
    `call class:offset` ops (absolute offsets, no ±32 KB range limit) — the
    41 KB class exceeds the relative-jump range, so absolute calls are required.
  * ScummVM bounds a U8 class by its FLX index size (set by the packer from the
    data length) and uses a hardcoded 0x0C base offset; it ignores the header
    total_size/unknown fields. We update total_size anyway for tool consistency
    (the disassembler uses it to bound the bytecode).

All variable operands (lbDone's global bit, the LV class id, the LV use() offset)
are read from the live symbol table / compiled bytecode at build time, so the
patch always matches the flag numbering LORDBRIT and the LV class were compiled
with.
"""

import hashlib
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(__file__))
from u8c_codegen import BytecodeEmitter

BASE_OFFSET = 0x0C          # U8 class header size; event table follows
USE_EVENT = 1               # event id for use()
MYTHRAN_USE_OFFSET = 0x208C  # original use() entry (event-table relative)

# Range of the original use() preamble to copy into the LV path, expressed as
# event-table-relative offsets. Starts *after* the `init 08` (0x208C..0x208E)
# because new_use emits its own init; ends just before the stock greeting at
# 0x20B9. This span (push 0207 ... pop global 024A) sets the conversation info
# and spawns Mythran's face portrait, and contains no relative jumps, so it is
# safe to relocate verbatim.
PREAMBLE_START = 0x208E
PREAMBLE_END = 0x20B9

# sha256 of the 43 verbatim preamble bytes
# (base_data[BASE_OFFSET+PREAMBLE_START:BASE_OFFSET+PREAMBLE_END]), pinned
# against ~/projects/lost-vale/shared/data/USECODE.FLX,
# md5 09e6916fdd404ce910eb19b6acf96383 (base game USECODE.FLX as of
# 2026-07-03, class 0x421 length 41265 bytes). If a different base
# EUSECODE.FLX is ever substituted, the copied preamble bytes could differ
# (different disc pressing, patch level, or bytecode revision) and the
# wrapper would splice garbage instructions into Mythran's face-setup path,
# which would misbehave or crash at runtime rather than fail at build time.
PREAMBLE_SHA256 = "ec3032c2528c5920c43c5a336a461f15ad1f30d5e3f6370db492a3c02d576f26"


def _event_offset(class_data, event_id):
    """Read a class's event-table entry (offset relative to BASE_OFFSET)."""
    return struct.unpack_from('<I', class_data, BASE_OFFSET + event_id * 4)[0]


def build_new_use(lbdone_bit, lbdone_width, lv_class_id, lv_use_offset,
                  preamble_bytes, stockvisit_bit, stockvisit_width):
    """Assemble the appended replacement use() handler.

    Returns the raw bytecode for new_use. Callers append this to the class and
    point the event-01 table entry at its start.

    Built on the codegen BytecodeEmitter (see u8c_codegen.py) rather than
    hand-rolled opcode/operand byte literals -- the M0.1 `this`-push bug was
    introduced by a hand-typed byte sequence, so this path now shares the
    same emit_* helpers the compiler itself uses. The two forward `jne`s use
    the emitter's label/fixup machinery (emit_jne_label/define_label +
    resolve_fixups); the emitter's `offset` property is always
    `0x80 + len(code)`, and that constant cancels out in the relative-offset
    subtraction, so it produces byte-identical operands to manual backpatch
    against position 0 even though this buffer is later appended at a
    nonzero offset in the real class. The only bytes not emitted via an
    emit_* call are the copied face-setup preamble itself, appended verbatim
    to `emitter.code` as designed (see the module docstring).
    """
    emitter = BytecodeEmitter()

    # init 08  (allocate 8 local bytes, matching the original use frame)
    emitter.emit_init(0x08)

    # push global lbDone; jne .stock (LB message not delivered -> stock Mythran)
    emitter.emit_push_global(lbdone_bit, lbdone_width)
    emitter.emit_jne_label('stock')

    # --- LV path ---
    emitter.code.extend(preamble_bytes)         # copied face-setup preamble
    emitter.emit_push_dword_bp(0x06)            # push dword [BP+06]  (this)
    emitter.emit_call(lv_class_id, lv_use_offset)  # TypeMythranLVDlg::use
    emitter.emit_add_sp(0xFC)                   # add sp -4 (pop the this arg)

    # push global mythranStockVisit; jne .done (no stock handoff requested)
    emitter.emit_push_global(stockvisit_bit, stockvisit_width)
    emitter.emit_jne_label('done')

    # Handoff requested: clear the flag, then fall through to the stock call.
    emitter.emit_push_byte(0)
    emitter.emit_pop_global(stockvisit_bit, stockvisit_width)

    # --- stock path ---
    emitter.define_label('stock')
    emitter.emit_push_dword_bp(0x06)            # push dword [BP+06]  (this)
    emitter.emit_call(0x421, MYTHRAN_USE_OFFSET)  # MYTHRAN::use@0x208C
    emitter.emit_add_sp(0xFC)                   # add sp -4 (pop the this arg)

    emitter.define_label('done')
    emitter.emit_ret()
    emitter.emit_end()

    emitter.resolve_fixups()

    return bytes(emitter.code)


def patch_mythran_class(base_data, lbdone_bit, lbdone_width,
                        lv_class_id, lv_use_offset,
                        stockvisit_bit, stockvisit_width):
    """Return a patched copy of Mythran's class data (0x421).

    Args:
        base_data: original class 0x421 bytes (12-byte header + event table + code).
        lbdone_bit, lbdone_width: global-flag address of `lbDone`.
        lv_class_id: compiled class id of TypeMythranLVDlg.
        lv_use_offset: use() event offset within the LV class (event-table rel).
        stockvisit_bit, stockvisit_width: global-flag address of
            `mythranStockVisit` (set by the LV dialogue to request handoff to
            the stock conversation; cleared by the wrapper).
    """
    # Guard: a zero use() offset means the compiled LV dialogue class has no
    # use() event (TypeMythranLVDlg::use was never emitted, or the symbol
    # table lookup silently defaulted). Calling class:0000 would jump into
    # that class's header/event table as if it were code -- garbage
    # execution in-game. Fail here, at build time, instead.
    if lv_use_offset == 0:
        raise ValueError(
            "lv_use_offset is 0: TypeMythranLVDlg has no use() event to "
            "call. Refusing to patch Mythran with a call into offset 0000 "
            "(that would execute the class header as bytecode in-game).")

    data = bytearray(base_data)
    old_len = len(data)

    # Sanity: event 01 must still be the stock use() we are wrapping.
    orig_use = _event_offset(data, USE_EVENT)
    if orig_use != MYTHRAN_USE_OFFSET:
        raise ValueError(
            f"Mythran use() event moved (0x{orig_use:04X} != "
            f"0x{MYTHRAN_USE_OFFSET:04X}); patch offsets are stale.")

    preamble = bytes(data[BASE_OFFSET + PREAMBLE_START:
                          BASE_OFFSET + PREAMBLE_END])

    # Guard: the preamble is copied verbatim into the wrapper with no
    # decoding, so if it came from a different base EUSECODE.FLX (different
    # disc pressing, patch level, or bytecode revision) it could be handled
    # by the game silently and wrongly at runtime rather than fail to build.
    # Pin it against the known-good hash computed above.
    preamble_hash = hashlib.sha256(preamble).hexdigest()
    if preamble_hash != PREAMBLE_SHA256:
        raise ValueError(
            "Mythran use() preamble does not match the pinned hash "
            f"(expected {PREAMBLE_SHA256}, got {preamble_hash}). This base "
            "EUSECODE.FLX's class 0x421 differs from the file the patch was "
            "verified against -- copying these bytes verbatim would splice "
            "unverified/garbage instructions into the LV Mythran path. "
            "Re-verify the preamble range and re-pin PREAMBLE_SHA256 before "
            "patching against this file.")

    new_use = build_new_use(lbdone_bit, lbdone_width, lv_class_id,
                            lv_use_offset, preamble,
                            stockvisit_bit, stockvisit_width)

    # new_use lives at the end; its event-table-relative offset is (old_len - base).
    new_use_offset = old_len - BASE_OFFSET
    if new_use_offset > 0xFFFF:
        raise ValueError(
            f"Mythran class too large: use() offset 0x{new_use_offset:X} "
            f"exceeds the 16-bit event/call operand range.")

    data += new_use

    # Repoint event 01 (use) to new_use.
    struct.pack_into('<I', data, BASE_OFFSET + USE_EVENT * 4, new_use_offset)

    # Keep total_size consistent with the new length (disassembler relies on it).
    struct.pack_into('<I', data, 4, len(data))

    return bytes(data)

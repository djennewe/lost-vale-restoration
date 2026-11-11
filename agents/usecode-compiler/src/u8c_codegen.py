#!/usr/bin/env python3
"""
u8c_codegen.py — Code generator for the U8 usecode compiler.

Takes an AST (from u8c_parser.py) and emits binary bytecode for each
usecode class. Generates the 12-byte header, 128-byte event table,
and instruction stream.

Architecture:
- Each class generates one bytecode blob
- Process functions map to event handlers in the event table
- bark() generates calli to intrinsic 0x0049
- ask() generates calli to intrinsic 0x004A
- Method calls on items/npcs generate calli to the appropriate intrinsic
"""

import bisect
import os
import struct
import sys
from typing import Dict, List, Optional, Tuple
from u8c_ast import *
from u8c_symbols import SymbolTable, create_symbol_table, METHOD_CLASS_ID

# NPC usecode classes are 0x400 + npcNum. An NPC class name used as an
# item is that NPC's object number, which only holds inside the real NPC
# window: retail NPCs run npcNum 1-61 (AVATAR 0x401 .. GUARD10 0x43D) and
# the Lost Vale NPCs 100-116 (SIGRID 0x466 .. EZREKAL 0x474, the map.cpp
# Actor promotion window). Above it sit classes that are not actors:
# TYPERECE 0x478 (npcNum-dispatched pillar receptacles) and the egg
# classes from MAPTELE 0x480, where `push byte` would also sign-extend
# (0x4AA -> 0A AA -> 0xFFAA). Playtest 2026-10-03 finding 4.
NPC_CLASS_FIRST = 0x0401
NPC_CLASS_LAST = 0x0474

# The process type an event handler's preamble gives itself (`push word
# T; push this; set info; process exclude`). Retail's per-event value,
# counted over every event entry in shared/data/USECODE.FLX (2026-10-07):
# look 0x208 x360, use 0x207 x158, anim 0x20A x8, cachein 0x213 x2, hit
# 0x20B x19, gotHit 0x20C x60, hatch 0x210 x48, schedule 0x215 x35, release
# 0x20D x10, combine 0x214 x1, enterFastArea 0x21B x87, leaveFastArea 0x21C
# x79, cast 0x21D x34, justMoved 0x22D x1, AvatarStoleSomething 0x22E x19.
# The old `0x208 + event` matched look and anim only, so e.g. retail METHOD
# 0x57C 0BE5's resetRef(0x207) on a dead NPC missed our use() (then 0x209).
# Events retail never compiles keep 0x208 + id, and so does event 0x15,
# whose single retail handler takes PT_BARK's 0x200.
RETAIL_EVENT_TYPES = {
    0x00: 0x208, 0x01: 0x207, 0x02: 0x20A, 0x04: 0x213, 0x05: 0x20B,
    0x06: 0x20C, 0x07: 0x210, 0x08: 0x215, 0x09: 0x20D, 0x0C: 0x214,
    0x0F: 0x21B, 0x10: 0x21C, 0x11: 0x21D, 0x12: 0x22D, 0x13: 0x22E,
}


def npc_num_of_class(classid):
    """npcNum for an NPC class id, or None outside the NPC window."""
    if classid is not None and NPC_CLASS_FIRST <= classid <= NPC_CLASS_LAST:
        return classid - 0x0400
    return None


def _contains_node(node, cls):
    """True if `node` is, or holds anywhere below it, an AST node of `cls`."""
    if isinstance(node, cls):
        return True
    if isinstance(node, (list, tuple)):
        return any(_contains_node(n, cls) for n in node)
    if isinstance(node, ASTNode):
        return any(_contains_node(v, cls) for v in vars(node).values()
                   if isinstance(v, (ASTNode, list, tuple)))
    return False


class CodeGenError(Exception):
    def __init__(self, message, node=None):
        if node and hasattr(node, 'line'):
            message = f"L{node.line}: {message}"
        super().__init__(message)


class BytecodeEmitter:
    """Low-level bytecode emission."""

    def __init__(self):
        self.code = bytearray()
        self._labels = {}  # label_name -> offset
        self._fixups = []  # (offset, label_name, fixup_type)
        # (start, end) code-relative byte ranges of every emitted string
        # literal, recorded at emission time (ground truth — see
        # _find_safe_insertion). Kept in sync with code-position shifts
        # inserted by _resolve_with_trampolines(), same as _labels.
        self._string_ranges = []
        # code-relative offsets where an instruction begins, recorded at
        # emission time by _mark_instr() (ground truth, exactly like
        # _string_ranges). Kept sorted and shifted in sync with
        # code-position changes made by _resolve_with_trampolines(), so
        # _find_safe_insertion() never splices a relay block mid-instruction.
        self._instr_starts = []
        # (code_position, size) for every relay block spliced in by
        # _resolve_with_trampolines(). Labels/strings/instr-starts/fixups are
        # shifted in place as each relay lands, but the EVENT TABLE is built
        # from a dict handed to build_class() after resolution, so it cannot
        # be shifted in place — it is corrected from this log instead (M2).
        # Without it, a relay inserted above a later event handler left that
        # handler's table entry pointing 6 bytes short of its real start, so
        # the event would dispatch INTO THE MIDDLE OF AN INSTRUCTION.
        self._insertions = []

    @property
    def offset(self):
        """Current bytecode offset (relative to event table start, so +0x80)."""
        return 0x80 + len(self.code)

    def emit_byte(self, b):
        self.code.append(b & 0xFF)

    def emit_word(self, w):
        self.code.extend(struct.pack('<H', w & 0xFFFF))

    def emit_dword(self, d):
        self.code.extend(struct.pack('<I', d & 0xFFFFFFFF))

    def emit_signed_word(self, w):
        self.code.extend(struct.pack('<h', w))

    def _mark_instr(self):
        """Record that an instruction begins at the current code offset.

        Called at the top of every instruction-emitting method, before any
        bytes for that instruction are appended — ground truth for
        instruction boundaries, exactly like _string_ranges is ground truth
        for string data. _find_safe_insertion() uses this set so a relay
        block can never be spliced mid-instruction.
        """
        bisect.insort(self._instr_starts, len(self.code))

    def emit_op(self, opcode):
        """Emit a raw single-byte opcode as a new instruction start.

        For opcodes with no dedicated emit_* wrapper (e.g. strcmp, cmp/ne/
        lt/gt, and, or, not, add, sub, loopscr, loop, loopnext, create
        list). Any operand bytes that follow MUST be emitted via plain
        emit_byte (not emit_op / not marked) so they are never mistaken
        for instruction starts.
        """
        self._mark_instr()
        self.emit_byte(opcode)

    def emit_string(self, s):
        """Emit a push string instruction: 0x0D + uint16_len + data + 0x00."""
        self._mark_instr()
        if isinstance(s, str):
            s_bytes = s.encode('ascii', errors='replace')
        else:
            s_bytes = s
        start = len(self.code)
        self.emit_byte(0x0D)
        self.emit_word(len(s_bytes))
        self.code.extend(s_bytes)
        self.emit_byte(0x00)
        self._string_ranges.append((start, len(self.code)))

    def emit_push_byte(self, val):
        """Push signed byte literal."""
        self._mark_instr()
        self.emit_byte(0x0A)
        if val < 0:
            val = val & 0xFF
        self.emit_byte(val)

    def emit_push_word(self, val):
        """Push 16-bit literal."""
        self._mark_instr()
        self.emit_byte(0x0B)
        self.emit_word(val)

    def emit_push_dword(self, val):
        """Push 32-bit literal."""
        self._mark_instr()
        self.emit_byte(0x0C)
        self.emit_dword(val)

    def emit_push_bp(self, bp_offset):
        """Push word from [BP+xx]."""
        self._mark_instr()
        self.emit_byte(0x3F)
        self.emit_byte(bp_offset & 0xFF)

    def emit_push_dword_bp(self, bp_offset):
        """Push dword from [BP+xx]."""
        self._mark_instr()
        self.emit_byte(0x40)
        self.emit_byte(bp_offset & 0xFF)

    def emit_pop_bp(self, bp_offset):
        """Pop word to [BP+xx]."""
        self._mark_instr()
        self.emit_byte(0x01)
        self.emit_byte(bp_offset & 0xFF)

    def emit_pop_byte_bp(self, bp_offset):
        """Pop byte to [BP+xx] (0x00) — WorldPoint .z writes."""
        self._mark_instr()
        self.emit_byte(0x00)
        self.emit_byte(bp_offset & 0xFF)

    def emit_push_byte_bp(self, bp_offset):
        """Push sign-extended byte from [BP+xx] (0x3E) — WorldPoint .z
        reads. Sign-extension makes z >= 128 read as a negative word; every
        consumer in the corpus either passes it straight to an ARG_UINT8
        (only the low byte survives) or compares against small values, so
        this matches how retail reads byte locals (0x3E is retail's only
        byte-local push)."""
        self._mark_instr()
        self.emit_byte(0x3E)
        self.emit_byte(bp_offset & 0xFF)

    def emit_push_string_bp(self, bp_offset):
        """Push string from [BP+xx]."""
        self._mark_instr()
        self.emit_byte(0x41)
        self.emit_byte(bp_offset & 0xFF)

    def emit_push_addr_bp(self, bp_offset):
        """Push address of [BP+xx]."""
        self._mark_instr()
        self.emit_byte(0x4B)
        self.emit_byte(bp_offset & 0xFF)

    def emit_push_indirect(self, size):
        """Deref pointer, push size bytes."""
        self._mark_instr()
        self.emit_byte(0x4C)
        self.emit_byte(size)

    def emit_calli(self, arg_bytes, intrinsic_id):
        """Emit intrinsic call."""
        self._mark_instr()
        self.emit_byte(0x0F)
        self.emit_byte(arg_bytes)
        self.emit_word(intrinsic_id)

    def emit_call(self, classid, offset):
        """Emit cross-class call."""
        self._mark_instr()
        self.emit_byte(0x11)
        self.emit_word(classid)
        self.emit_word(offset)

    def emit_call_label(self, classid, label):
        """Same as emit_call, but the target offset is a same-class
        function not yet compiled (forward reference — e.g. a function
        calling one defined LATER in source order). The offset word is a
        placeholder patched by resolve_fixups() once the target
        function's _generate_function() defines `label` (see
        emit_spawn_label's docstring for the full mechanism)."""
        self._mark_instr()
        self.emit_byte(0x11)
        self.emit_word(classid)
        self._fixups.append((len(self.code), label, 'funcoffset'))
        self.emit_word(0)  # placeholder

    def emit_init(self, local_bytes):
        """Emit init (allocate local variables)."""
        self._mark_instr()
        self.emit_byte(0x5A)
        self.emit_byte(local_bytes)

    def emit_ret(self):
        self._mark_instr()
        self.emit_byte(0x50)

    def emit_end(self):
        self._mark_instr()
        self.emit_byte(0x79)

    def emit_suspend(self):
        self._mark_instr()
        self.emit_byte(0x53)

    def emit_set_info(self):
        self._mark_instr()
        self.emit_byte(0x77)

    def emit_process_exclude(self):
        self._mark_instr()
        self.emit_byte(0x78)

    def emit_push_pid(self):
        self._mark_instr()
        self.emit_byte(0x59)

    def emit_str_to_ptr(self):
        self._mark_instr()
        self.emit_byte(0x6B)

    def emit_free_string_sp(self, sp_offset):
        self._mark_instr()
        self.emit_byte(0x65)
        self.emit_byte(sp_offset & 0xFF)

    def emit_free_slist_sp(self, sp_offset):
        """Free string list at [SP+xx] (opcode 0x67)."""
        self._mark_instr()
        self.emit_byte(0x67)
        self.emit_byte(sp_offset & 0xFF)

    def emit_add_sp(self, val):
        """Adjust stack pointer. A zero adjustment emits nothing: retail
        never has `6E 00` — its 399 zero-argument calli sites go straight
        on (FREE 0x581 1BE6 `calli 00h 00D2h; push long retval`), as do
        its zero-argument spawns (PENT 0x7C 1204 `spawn; push retval`)."""
        if val & 0xFF == 0:
            return
        self._mark_instr()
        self.emit_byte(0x6E)
        self.emit_byte(val & 0xFF)

    def emit_push_retval(self):
        self._mark_instr()
        self.emit_byte(0x5E)

    def emit_push_byte_retval(self):
        self._mark_instr()
        self.emit_byte(0x5D)

    def emit_pop_temp(self):
        self._mark_instr()
        self.emit_byte(0x12)

    def emit_implies(self, a=1, b=1):
        self._mark_instr()
        self.emit_byte(0x54)
        self.emit_byte(a)
        self.emit_byte(b)

    def emit_jne(self, offset):
        """Jump if false. offset is relative to after this instruction."""
        self._mark_instr()
        self.emit_byte(0x51)
        self.emit_signed_word(offset)

    def emit_jmp(self, offset):
        """Unconditional jump."""
        self._mark_instr()
        self.emit_byte(0x52)
        self.emit_signed_word(offset)

    def emit_concat(self):
        self._mark_instr()
        self.emit_byte(0x16)

    def emit_push_slist(self, bp_offset):
        """Push string list from [BP+xx]."""
        self._mark_instr()
        self.emit_byte(0x43)
        self.emit_byte(bp_offset & 0xFF)

    def emit_free_slist(self, bp_offset):
        """Free string list at [BP+xx]."""
        self._mark_instr()
        self.emit_byte(0x63)
        self.emit_byte(bp_offset & 0xFF)

    def emit_push_list(self, bp_offset, elem_size=0x02):
        """Push a copy of the list at [BP+xx] (0x42 xx size)."""
        self._mark_instr()
        self.emit_byte(0x42)
        self.emit_byte(bp_offset & 0xFF)
        self.emit_byte(elem_size)

    def emit_free_list(self, bp_offset):
        """Free list at [BP+xx] (0x64)."""
        self._mark_instr()
        self.emit_byte(0x64)
        self.emit_byte(bp_offset & 0xFF)

    def emit_foreach_list_label(self, opcode, var_bp, label, elem_size=0x02):
        """`for each` over a pushed list (0x75) or string list (0x76):
        75|76 var size rel16, rel16 relative to the end of the instruction
        (retail FREE 0x581 1FD5 `75 FE 02 0B 00` -> 1FE5), a forward jump
        to the loop end, so it rides the ordinary 'jmp' fixup."""
        self._mark_instr()
        self.emit_byte(opcode)
        self.emit_byte(var_bp & 0xFF)
        self.emit_byte(elem_size)
        self._fixups.append((len(self.code), label, 'jmp'))
        self.emit_word(0)  # placeholder

    def emit_spawn_inline_label(self, classid, func_label, body_label,
                                this_size):
        """`spawn inline` (0x58 class func delta this_size 00): start an
        inline process at func_label + delta = body_label. Retail AVATAR
        0x401 2FE4 `58 01 04 B2 00 59 2F 02 00` (00B2 + 2F59 = 300B). Both
        words are absolute values patched at resolution ('funcoffset' and
        ('delta', func_label) fixups), never jump displacements."""
        self._mark_instr()
        self.emit_byte(0x58)
        self.emit_word(classid)
        self._fixups.append((len(self.code), func_label, 'funcoffset'))
        self.emit_word(0)
        self._fixups.append((len(self.code), body_label, ('delta', func_label)))
        self.emit_word(0)
        self.emit_byte(this_size)
        self.emit_byte(0x00)

    def emit_append(self):
        """Append two lists on stack."""
        self._mark_instr()
        self.emit_byte(0x17)

    def emit_union_slist(self, elem_size=0x02):
        """Union string lists (prepend semantics)."""
        self._mark_instr()
        self.emit_byte(0x19)
        self.emit_byte(elem_size)

    def emit_subtract_slist(self, elem_size=0x02):
        """Subtract string list elements."""
        self._mark_instr()
        self.emit_byte(0x1A)
        self.emit_byte(elem_size)

    def emit_spawn(self, arg_bytes, this_size, classid, offset):
        self._mark_instr()
        self.emit_byte(0x57)
        self.emit_byte(arg_bytes)
        self.emit_byte(this_size)
        self.emit_word(classid)
        self.emit_word(offset)

    def emit_spawn_label(self, arg_bytes, this_size, classid, label):
        """Same-class forward-reference spawn (uses-imports work item 4,
        shared/docs/wiring.md): `spawn puppet(lb) -> return;` inside
        LORDBRIT's use(), where puppet() is defined LATER in the same
        file. classid is known immediately (it's always this class for a
        same-class spawn), but the target function's own byte offset
        isn't known until _generate_function() actually emits it — so
        this defers the offset word exactly the way emit_jne_label/
        emit_jmp_label defer a forward jump target: write a placeholder
        and record a ('funcoffset', label) fixup. resolve_fixups() (see
        its 'funcoffset' branch) patches it with the label's final
        offset — an absolute word, never a relative jump displacement, so
        it is exempt from the sint16-overflow/trampoline logic that
        branch also handles."""
        self._mark_instr()
        self.emit_byte(0x57)
        self.emit_byte(arg_bytes)
        self.emit_byte(this_size)
        self.emit_word(classid)
        self._fixups.append((len(self.code), label, 'funcoffset'))
        self.emit_word(0)  # placeholder

    def emit_push_global(self, bit_offset, bits):
        self._mark_instr()
        self.emit_byte(0x4E)
        self.emit_word(bit_offset)
        self.emit_byte(bits)

    def emit_pop_global(self, bit_offset, bits):
        self._mark_instr()
        self.emit_byte(0x4F)
        self.emit_word(bit_offset)
        self.emit_byte(bits)

    # Labels and fixups for forward jumps
    def define_label(self, name):
        self._labels[name] = self.offset

    def emit_jne_label(self, label):
        """Emit jne with a forward reference to be fixed up later."""
        self._mark_instr()
        self._fixups.append((len(self.code) + 1, label, 'jne'))
        self.emit_byte(0x51)
        self.emit_word(0)  # placeholder

    def emit_jmp_label(self, label):
        """Emit jmp with a forward reference."""
        self._mark_instr()
        self._fixups.append((len(self.code) + 1, label, 'jmp'))
        self.emit_byte(0x52)
        self.emit_word(0)  # placeholder

    def _find_safe_insertion(self, target_pos):
        """Find the nearest position at or after target_pos that is both
        (a) not inside string literal data, and (b) an actual instruction
        boundary, so a relay block never corrupts a string AND never
        splices itself into the middle of an instruction/operand.

        Uses self._string_ranges and self._instr_starts — ground truth
        recorded at emission time by emit_string()/_mark_instr() and kept
        position-shifted in sync by _resolve_with_trampolines() — exactly
        the same pattern for both.

        CORRECTED 2026-07-03 (found during M0.6): this used to rescan the
        raw bytecode treating every 0x0D byte as a string opcode. A 0x0D
        appearing as ordinary operand data (e.g. the low byte of a
        16-bit global-flag bit offset — any flag pinned at bit 1037,
        1293, 1549, ... in the manifest window) made the scan misread the
        next two bytes as a huge bogus string length, so the relay block
        got planned tens of KB past where the resolver needed it and
        large classes (ATLI, 36 KB once the manifest killed its silent
        push-0 fallbacks) failed with "Failed to resolve jumps after 10
        trampoline passes" while making zero progress per pass. The old
        scanner was always unsound (any operand or string byte equal to
        0x0D desynced it); the manifest's bit-1024+ window just made it
        fire deterministically.

        CORRECTED AGAIN 2026-07-03 (M0.6 follow-up): even after the fix
        above, this only avoided string ranges — it did not require the
        returned position to be an instruction boundary at all, so a
        relay could still land mid-instruction (e.g. 2 bytes into a
        `push global` in ATLI, corrupting the stack at runtime). Now
        returns the nearest *recorded instruction start* at or after
        target_pos, skipping past string ranges first exactly as before.
        """
        # First, if target_pos lands inside an emitted string literal,
        # jump past it — a relay block must never split string data.
        for start, end in self._string_ranges:
            if start < target_pos < end:
                target_pos = min(end, len(self.code))
                break

        # Now find the nearest instruction boundary at or after
        # target_pos. _instr_starts is kept sorted.
        idx = bisect.bisect_left(self._instr_starts, target_pos)
        while idx < len(self._instr_starts):
            candidate = self._instr_starts[idx]
            # Defensive: an instruction start should never fall inside a
            # string range, but re-check in case a boundary and a string
            # range coincide oddly after repeated shifting.
            inside_string = any(s < candidate < e for s, e in self._string_ranges)
            if not inside_string:
                return candidate
            idx += 1

        # No safe instruction boundary before end-of-code — appending at
        # the very end is always safe (nothing after it to split).
        return len(self.code)

    def _absolute_value(self, label, fixup_type):
        """Value of an ABSOLUTE fixup, or None for a relative jump one.
        'funcoffset' is the label's own offset; ('delta', base) is the
        distance from label `base` (spawn inline's offset+delta pair)."""
        if fixup_type == 'funcoffset':
            return self._labels[label]
        if isinstance(fixup_type, tuple) and fixup_type[0] == 'delta':
            return (self._labels[label] - self._labels[fixup_type[1]]) & 0xFFFF
        return None

    def resolve_fixups(self):
        """Resolve all jump references, inserting trampolines for overflows.

        When a jump offset exceeds sint16 range (-32768..32767), we insert
        skip-protected relay blocks to chain shorter jumps. Each relay is
        6 bytes: [jmp +3][jmp placeholder] — the first jmp acts as a guard
        so normal execution skips the relay; the relay jmp is only reached
        via intentional jumps targeting it.

        For jne overflows, we first convert:
            jne far_target
        into:
            jne +3          ; if FALSE, jump to trampoline
            jmp +3          ; if TRUE, skip trampoline
            jmp far_target  ; trampoline (now a jmp overflow to handle)
        """
        # Phase 1: try direct resolution
        has_overflow = False
        for code_offset, label, fixup_type in self._fixups:
            if label not in self._labels:
                raise CodeGenError(f"Undefined label: {label}")
            if self._absolute_value(label, fixup_type) is not None:
                # Absolute same-class function offset (forward-reference
                # spawn/call — see emit_spawn_label/emit_call_label), not
                # a relative jump displacement. Never overflows (it's a
                # plain uint16 byte offset into this class' own code) and
                # is patched below/in _resolve_with_trampolines, not here.
                continue
            target = self._labels[label]
            after_instr = 0x80 + code_offset + 2
            rel = target - after_instr
            if not (-32768 <= rel <= 32767):
                has_overflow = True
                break

        if not has_overflow:
            # Simple path: all fit in sint16
            for code_offset, label, fixup_type in self._fixups:
                target = self._labels[label]
                value = self._absolute_value(label, fixup_type)
                if value is not None:
                    struct.pack_into('<H', self.code, code_offset, value)
                    continue
                after_instr = 0x80 + code_offset + 2
                rel = target - after_instr
                struct.pack_into('<h', self.code, code_offset, rel)
            return

        # Phase 2: handle overflows with trampolines
        self._resolve_with_trampolines()

    def _resolve_with_trampolines(self):
        """Insert trampoline relay chains for jump overflows."""
        MAX_RELAY_DISTANCE = 30000  # Close to sint16 max (32767)
        MAX_ITERATIONS = 10

        for iteration in range(MAX_ITERATIONS):
            # Step A: Convert jne overflows to jne+3/jmp+3/jmp pattern
            # This turns conditional overflows into unconditional overflows.
            # Process from end to start so byte insertions don't shift
            # already-processed positions.
            jne_overflows = []
            for i, (code_offset, label, fixup_type) in enumerate(self._fixups):
                target = self._labels[label]
                after_instr = 0x80 + code_offset + 2
                rel = target - after_instr
                if not (-32768 <= rel <= 32767) and fixup_type == 'jne':
                    jne_overflows.append((i, code_offset, label))

            # Process jne conversions from end to start
            for fixup_idx, code_offset, label in sorted(
                    jne_overflows, key=lambda x: x[1], reverse=True):
                insert_at = code_offset + 2  # After the jne operand
                # Insert: jmp +3 (skip guard) + jmp placeholder (trampoline)
                new_bytes = bytearray([0x52, 0x03, 0x00, 0x52, 0x00, 0x00])
                self.code[insert_at:insert_at] = new_bytes

                # Set jne operand to +3 (jump to trampoline at insert_at+3)
                struct.pack_into('<h', self.code, code_offset, 3)

                # Trampoline jmp operand is at code_offset + 6 in self.code
                trampoline_operand = code_offset + 6

                # Shift all labels at or after insert_at
                for name in self._labels:
                    if self._labels[name] - 0x80 >= insert_at:
                        self._labels[name] += 6

                # Shift string-literal ranges at or after insert_at
                # (insertions never land inside a string: insert_at is an
                # instruction boundary right after a jne operand)
                self._string_ranges = [
                    (s + 6, e + 6) if s >= insert_at else (s, e)
                    for s, e in self._string_ranges]

                # Shift instruction-start offsets at or after insert_at,
                # then record the two new instruction starts the relay
                # block itself introduces (the +3 skip guard jmp at
                # insert_at, and the trampoline jmp at insert_at+3).
                self._instr_starts = [
                    s + 6 if s >= insert_at else s
                    for s in self._instr_starts]
                bisect.insort(self._instr_starts, insert_at)
                bisect.insort(self._instr_starts, insert_at + 3)

                # M2: log the splice so build_class() can correct the event
                # table, which is not shiftable in place from here.
                self._insertions.append((insert_at, 6))

                # Shift all fixup code_offsets at or after insert_at
                new_fixups = []
                for j, (co, lb, ft) in enumerate(self._fixups):
                    if co >= insert_at:
                        new_fixups.append((co + 6, lb, ft))
                    else:
                        new_fixups.append((co, lb, ft))
                # Replace the jne fixup with a jmp fixup at the trampoline
                new_fixups[fixup_idx] = (trampoline_operand, label, 'jmp')
                self._fixups = new_fixups

            # Step B: Resolve all fixups that fit; collect remaining overflows
            jmp_overflows = []
            for i, (code_offset, label, fixup_type) in enumerate(self._fixups):
                target = self._labels[label]
                value = self._absolute_value(label, fixup_type)
                if value is not None:
                    # Absolute offset, not a jump displacement — always
                    # resolvable directly, and re-patched on every pass so
                    # the LAST write (after all label shifts settle) has
                    # the correct final value. See resolve_fixups().
                    struct.pack_into('<H', self.code, code_offset, value)
                    continue
                after_instr = 0x80 + code_offset + 2
                rel = target - after_instr
                if -32768 <= rel <= 32767:
                    struct.pack_into('<h', self.code, code_offset, rel)
                else:
                    jmp_overflows.append((i, code_offset, label, rel))

            if not jmp_overflows:
                return  # All resolved!

            # Step C: For each jmp overflow, insert ONE relay block midway.
            # Pre-compute ALL relay positions, then insert from end to start
            # with cumulative shift tracking to avoid cascade issues.
            jmp_overflows.sort(key=lambda x: x[1], reverse=True)

            # Pre-compute relay positions (before any insertions)
            relay_plans = []  # (fixup_idx, code_offset, label, relay_code)
            for fixup_idx, code_offset, label, rel in jmp_overflows:
                target = self._labels[label]
                target_code = target - 0x80
                source_code = code_offset
                if rel > 0:
                    relay_code = min(source_code + MAX_RELAY_DISTANCE,
                                     target_code - 6)
                else:
                    relay_code = max(source_code - MAX_RELAY_DISTANCE,
                                     target_code + 6)
                relay_code = max(0, min(len(self.code), relay_code))
                relay_code = self._find_safe_insertion(relay_code)
                relay_plans.append((fixup_idx, code_offset, label, relay_code))

            # Sort by relay_code descending so end-to-start insertions
            # don't shift earlier relay positions
            relay_plans.sort(key=lambda x: x[3], reverse=True)

            for fixup_idx, code_offset, label, relay_code in relay_plans:
                relay_bytes = bytearray([0x52, 0x03, 0x00, 0x52, 0x00, 0x00])
                self.code[relay_code:relay_code] = relay_bytes

                relay_operand = relay_code + 4
                relay_entry_addr = 0x80 + relay_code + 3

                for name in self._labels:
                    if self._labels[name] - 0x80 >= relay_code:
                        self._labels[name] += 6

                # Shift string-literal ranges at or after relay_code
                # (relay_code was routed through _find_safe_insertion, so
                # it is never strictly inside a string range)
                self._string_ranges = [
                    (s + 6, e + 6) if s >= relay_code else (s, e)
                    for s, e in self._string_ranges]

                # Shift instruction-start offsets at or after relay_code,
                # then record the two new instruction starts the relay
                # block itself introduces (the +3 skip guard jmp at
                # relay_code, and the trampoline jmp at relay_code+3).
                self._instr_starts = [
                    s + 6 if s >= relay_code else s
                    for s in self._instr_starts]
                bisect.insort(self._instr_starts, relay_code)
                bisect.insort(self._instr_starts, relay_code + 3)

                # M2: log the splice (see _insertions).
                self._insertions.append((relay_code, 6))

                relay_label = f'__relay_{iteration}_{fixup_idx}'
                self._labels[relay_label] = relay_entry_addr

                new_fixups = []
                for j, (co, lb, ft) in enumerate(self._fixups):
                    if co >= relay_code:
                        new_fixups.append((co + 6, lb, ft))
                    else:
                        new_fixups.append((co, lb, ft))

                orig = new_fixups[fixup_idx]
                new_fixups[fixup_idx] = (orig[0], relay_label, orig[2])
                new_fixups.append((relay_operand, label, 'jmp'))
                self._fixups = new_fixups

            # Loop back to try resolving again (relays may need further relays)

        raise CodeGenError(
            f"Failed to resolve jumps after {MAX_ITERATIONS} trampoline passes. "
            f"Remaining overflows: {len(jmp_overflows)}"
        )

    @staticmethod
    def event_label(event_id):
        """Label name marking an event handler's first instruction (M2)."""
        return f'__event_{event_id}'

    def shift_event_offsets(self, events):
        """Correct event-table offsets for trampoline relay insertions (M2).

        Rather than replaying the insertion log, this reads each event's
        position back out of `_labels`. Labels are shifted IN PLACE as every
        relay lands, so they are always in current coordinates — whereas the
        raw insertion positions are not directly comparable to each other
        (relays are spliced end-to-start, so a later, lower-positioned splice
        also moves an earlier-logged one). Reusing the label machinery avoids
        that coordinate-space problem entirely.

        Falls back to the caller's offset for any event with no label, and is
        a no-op when nothing was inserted.
        """
        if not self._insertions:
            return events
        shifted = {}
        for eid, offset in events.items():
            label = self.event_label(eid)
            shifted[eid] = self._labels.get(label, offset)
        return shifted

    def build_class(self, unknown1, unknown2, events):
        """Build the complete class binary.

        Args:
            unknown1: first header uint32
            unknown2: third header uint32
            events: dict of event_id -> bytecode_offset (relative to base 0x0C)

        Returns:
            bytes: complete class data
        """
        self.resolve_fixups()

        # M2: correct event offsets for any trampoline relay blocks spliced
        # in by resolve_fixups(). Event offsets are captured during codegen
        # (0x80 + len(code) at each function's first instruction) and handed
        # in here AFTER resolution, so unlike labels they cannot be shifted
        # in place — each relay inserted at or before an event's position
        # pushes that function 6 bytes later than the table records.
        #
        # Left uncorrected, a >32KB class whose relay lands above a later
        # handler dispatches that event 6 bytes early PER RELAY, landing
        # mid-instruction so the VM reads operand bytes as opcodes. ATLI is
        # the only class large enough to trampoline today and survives only
        # because its overflow sits in the final function, with no later
        # event to shift — pure luck of layout. Gate 6 cannot see it either:
        # the bytes stay structurally valid, they are just entered at the
        # wrong point.
        events = self.shift_event_offsets(events)

        # Event table (128 bytes = 32 x uint32)
        event_table = bytearray(128)
        for eid, offset in events.items():
            struct.pack_into('<I', event_table, eid * 4, offset)

        bytecode = bytes(event_table) + bytes(self.code)
        total_size = 0x0C + len(bytecode)

        header = struct.pack('<III', unknown1, total_size, unknown2)
        return header + bytecode


class CodeGenerator:
    """Generate bytecode from AST."""

    def __init__(self, symbols=None, filename='<unknown>',
                 class_name_override=None):
        """Args:
            symbols: SymbolTable (or None for a fresh default one).
            filename: source basename — used for warnings, the provider
                registry key, and (absent a `class` header) class-id
                resolution.
            class_name_override: optional class NAME to compile a
                headerless (no `class` declaration) file under, instead
                of its own basename. Used by build_eusecode.py to compile
                FREE.UNK as 'LVFREE' (a NEW manifest-pinned class) rather
                than as base class FREE/0x581 — retail 0x581 is called by
                190 other retail classes at hardcoded offsets, so it must
                ship byte-identical (see UNSAFE_TO_REPLACE in
                build_eusecode.py). The override changes the class id
                that same-class calls target and that the provider
                registry records; the provider KEY stays the file's
                basename ('free'), matching consumers' `uses "free";`
                directives. Ignored for files that declare a class header.
        """
        self.symbols = symbols or create_symbol_table()
        self.filename = filename or '<unknown>'
        self.class_name_override = class_name_override
        self.emitter = None
        self.events = {}  # event_id -> offset
        self._local_vars = {}  # name -> bp_offset
        self._next_bp = 0  # next BP offset for locals (negative)
        self._label_counter = 0
        self._class_name = ''
        self._classid = 0
        self.warnings = []  # list of formatted "WARN <file>:<line>: ..." strings

        # `uses`-import support (uses-imports-as-cross-class-calls work).
        # _function_table records every bare (event_id is None) top-level
        # routine/process compiled SO FAR in THIS class:
        #   name.lower() -> {arity: (offset, return_kind)}
        # Populated incrementally as generate_class walks program.functions
        # in source order, so a BACKWARD call (to an already-compiled,
        # earlier-defined function) resolves directly against a real byte
        # offset — matching the base game's own FREE class (getPeriod
        # calls getHour, defined earlier, via a same-class 0x11 call).
        self._function_table = {}
        # FORWARD same-class references (uses-imports work item 4,
        # shared/docs/wiring.md): a same-class spawn/call whose target is
        # defined LATER in source order — e.g. LORDBRIT.UNK's `spawn
        # puppet(lb) -> return;` inside use(), where puppet() is the next
        # function in the file. Pre-scanned by generate_class() BEFORE any
        # function is compiled, so _resolve_function can already tell such
        # a target EXISTS (name.lower() -> {arity: return_kind}) even
        # though its offset isn't known yet. Resolution hands back a
        # LABEL string instead of an int offset in that case; emit_spawn/
        # emit_call callers must check for that (see emit_spawn_label/
        # emit_call_label) and resolve_fixups() patches the label's real
        # offset once _generate_function() defines it — the exact same
        # forward-reference mechanism as a forward jne/jmp, just an
        # absolute word instead of a relative displacement (see
        # BytecodeEmitter.resolve_fixups()'s 'funcoffset' fixup type).
        self._forward_functions = {}
        # Lowercased `uses "x";` strings declared by the file currently
        # being compiled — set once per generate_class() call. A bare
        # function/spawn call resolves against providers in this list (in
        # declaration order) after same-class resolution fails.
        self._used_providers = []

    def _warn(self, node, message):
        """Record + emit a structured codegen warning.

        Does NOT affect emitted bytecode — this is diagnostics only, for
        silent fallback paths (unknown identifier/function/type/etc.) that
        would otherwise compile to a placeholder or a no-op without a trace.
        """
        line = getattr(node, 'line', None) or '?'
        text = f"WARN {self.filename}:{line}: {message}"
        print(text, file=sys.stderr)
        self.warnings.append(text)

    def _new_label(self, prefix='L'):
        self._label_counter += 1
        return f"{prefix}_{self._label_counter}"

    def _alloc_local(self, name, size=2):
        """Allocate a local variable and return its BP offset."""
        self._next_bp += size
        bp_offset = (-self._next_bp) & 0xFF
        self._local_vars[name] = bp_offset
        return bp_offset

    def _get_local(self, name):
        """Get the BP offset for a local variable."""
        return self._local_vars.get(name)

    @staticmethod
    def _classify_return_kind(return_type, kind='routine'):
        """Classify a function by how a caller collects its result:
        'process', 'word', 'byte' or 'none'.

        A `process` hands its result over in the process-result register
        (`60 int to long; 08 pop result`, retail FREE 0x581 askYesNo
        1B1A-1B1D), so a caller must SPAWN it and wait: `push pid; args;
        push dword 0; spawn; push retval; implies; pop temp; suspend`, then
        `push process result; long to int` when it wants the value (retail
        PENT 0x7C 11FE-1212 `if askYesNo()`). Retail never `call`s a
        process: of the 17 retail functions that end a `return <expr>` in
        `60 08`, every caller spawns them; the 52 that end it in `12 pop
        temp` are all reached by `call` (0x11).

        A `routine` returns through the temp register (`12 pop temp`), read
        back with `push retval` (0x5E) or, for a Boolean, `push byte retval`
        (0x5D): base game MYTHRAN calling FREE's give(...):Boolean uses
        `push byte retval`; calling getPeriod():Number uses `push retval`.
        Routines with no declared return type ('none') are only ever called
        as statements in the corpus, so 'none' is never actually pushed.
        """
        if (kind or '').lower() == 'process':
            return 'process'
        if not return_type:
            return 'none'
        return 'byte' if return_type.strip().lower() in ('boolean', 'bool') else 'word'

    @staticmethod
    def _forward_label(key, arity):
        """Label name for a same-class function not yet compiled (forward
        reference). Keyed by (lowercased name, arity) — same
        disambiguation _function_table itself uses for overloads."""
        return f'__func_{key}_{arity}'

    def _resolve_function(self, name, arity):
        """Resolve a bare function/process name used as a plain call or a
        spawn target (uses-imports-as-cross-class-calls work).

        Resolution order:
          1. A function already compiled earlier in THIS class (same-class
             0x11/0x57 call — e.g. FREE's own getPeriod() calling
             getHour()) — offset is a real, already-known int.
          2. A function defined LATER in this class (forward reference —
             e.g. LORDBRIT's `spawn puppet(lb)`, where puppet() comes
             after use() in source order) — offset is a label string;
             see _forward_functions' docstring in __init__ for the full
             mechanism. Only bare (event_id is None) functions are ever
             pre-scanned into _forward_functions, matching what
             _function_table itself tracks.
          3. A routine/process exposed by a provider this file `uses`.
        All three are matched by (name, arity) — arity disambiguates
        overloads like FREE's safePlaySFX(2 args) vs safePlaySFX(3 args).

        Returns (class_id, offset_or_label, return_kind) or None. Callers
        (_gen_spawn, _gen_function_call) must check `isinstance(offset,
        str)` and route to emit_spawn_label/emit_call_label instead of
        emit_spawn/emit_call when it's a label.
        """
        key = name.lower()
        overloads = self._function_table.get(key)
        if overloads and arity in overloads:
            offset, return_kind = overloads[arity]
            return (self._classid, offset, return_kind)
        forward = self._forward_functions.get(key)
        if forward and arity in forward:
            return_kind = forward[arity]
            return (self._classid, self._forward_label(key, arity), return_kind)
        for provider in self._used_providers:
            found = self.symbols.find_provider_function(provider, name, arity)
            if found:
                return found
        return None

    def _resolve_same_class(self, name, arity):
        """Same-class (this file) resolution ONLY — steps 1 and 2 of
        _resolve_function, without the provider fallback. Used to give a
        class's own routines precedence over INTRINSIC names: FREE.UNK
        defines `routine combine(i:Item)` and calls `combine(item)`, and
        the old intrinsic-first order silently bound those calls to the
        engine's Item::combine instead of the 1994 routine (found
        2026-07-28 by the calli arity lint — the intrinsic call carried
        an argument the signature doesn't have). Local definitions win,
        which is ordinary scoping and what the 1994 compiler must have
        done for this source to have worked. Providers deliberately do
        NOT win over intrinsics: event-handler names (look/use/schedule/
        cast...) exist in every provider class and would shadow the real
        intrinsics wholesale."""
        key = name.lower()
        overloads = self._function_table.get(key)
        if overloads and arity in overloads:
            offset, return_kind = overloads[arity]
            return (self._classid, offset, return_kind)
        forward = self._forward_functions.get(key)
        if forward and arity in forward:
            return_kind = forward[arity]
            return (self._classid, self._forward_label(key, arity), return_kind)
        return None

    def _intrinsic_from_uses(self, name, arg_count):
        """Pick an overloaded bare intrinsic through this file's `uses` lines.

        The 1994 sources select among same-shaped intrinsic slots this way,
        and the include file's name IS the choice: SGBOOK.UNK says
        `uses "books"` and calls read(), PLAQUENS.UNK says `uses "plaque"`
        and calls read(16, ...). Book::read (0x6E), Scroll::read (0x6F),
        Grave::read (0x70) and Plaque::read (0x71) are four slots that a
        bare name plus an arity cannot tell apart, so without this the
        first-registered slot wins and a plaque is read as a grave
        (measured 2026-09-21: PLAQUENS compiled 70 calls to 0x70).

        Consulted ONLY when the plain lookup is still ambiguous, so a file
        with no matching `uses` line resolves exactly as it did before.
        Returns IntrinsicInfo or None.
        """
        cands = self.symbols.intrinsic_by_name.get(name.lower(), [])
        if arg_count is not None:
            same_arity = [c for c in cands if c.arg_count == arg_count]
            if same_arity:
                cands = same_arity
        if len(cands) < 2:
            return None
        for used in self._used_providers:
            base = used[:-1] if used.endswith('s') else used
            for c in cands:
                if c.class_name and c.class_name.lower() == base:
                    return c
        return None

    def generate_class(self, program):
        """Generate bytecode for a complete class.

        Args:
            program: Program AST node

        Returns:
            bytes: the compiled class data
        """
        self.emitter = BytecodeEmitter()
        self.events = {}
        self._function_table = {}
        self._forward_functions = {}

        # Get class info
        if program.class_decl:
            self._class_name = program.class_decl.name
            self._classid = self.symbols.get_class_id(self._class_name) or 0
        else:
            # No `class` header — routine-library files (FREE.UNK,
            # METHOD.UNK, FLAGS.UNK, AIRSPEL.UNK: see build_eusecode.py's
            # MODIFIED_BASE_CLASSES basename-identity handling). Resolve
            # the class id under class_name_override if the caller gave
            # one (FREE.UNK compiles as the NEW pinned class LVFREE — see
            # __init__ docstring), else the file's own basename, so
            # same-class 0x11 calls (e.g. FREE's getPeriod() calling its
            # own getHour()) and provider self-registration (below) target
            # the right class even with no declared name to read.
            self._class_name = ''
            lookup_name = (self.class_name_override
                           or os.path.splitext(self.filename)[0])
            self._classid = self.symbols.get_class_id(lookup_name) or 0

        # `uses "x";` directives this file declares — consulted by
        # unresolved FunctionCall/SpawnStmt resolution (_resolve_function).
        self._used_providers = [u.filename.lower() for u in program.uses]

        # Register global flags from this file
        for gf in program.globalflags:
            self.symbols.allocate_global_flag(gf.name, gf.bits)

        # Pre-scan bare (non-event) functions for FORWARD same-class
        # reference resolution (uses-imports work item 4): a spawn/call
        # may target a function defined LATER in this same file (source
        # order), e.g. LORDBRIT's `spawn puppet(lb) -> return;` inside
        # use(), where puppet() is the next function down. We only need
        # name/arity/return-kind here — the byte offset itself isn't
        # known until that function's own _generate_function() runs;
        # _resolve_function hands back a label in that case, and
        # resolve_fixups() patches the real offset once every function in
        # the class has been emitted (see _forward_functions' docstring
        # in __init__). Mirrors exactly what the main generation loop
        # below records into _function_table for BACKWARD references,
        # just ahead of time and offset-less.
        for func_def in program.functions:
            if self._event_id_of(func_def) is None:
                key = func_def.func_name.lower()
                self._forward_functions.setdefault(key, {})[len(func_def.params)] = \
                    self._classify_return_kind(func_def.return_type,
                                               func_def.kind)

        # Non-event `Class::method(...)`s get retail's method frame: the
        # caller pushes its args, then `this`, so the callee finds `this` at
        # BP+06 and its params from BP+0A (retail 057C: `call 057Ch 0113h`
        # after `push byte 16; push addr [BP-02h]`, and 0113 reads the
        # param at BP+0A). A bare `process name(...)` keeps the routine
        # frame, params from BP+06 and no `this`. Before 2026-09-25 every
        # non-event function got the routine frame, so a method that read
        # its implicit `this` (PLAQUENS's readPlaque() -> getQuality())
        # ran on item 0.
        self._methods = {(f.func_name.lower(), len(f.params))
                         for f in program.functions
                         if f.class_name
                         and self.symbols.get_event_id(f.func_name) is None}

        # The events this class handles: a bare zero-argument call of one
        # inside the class spawns our own handler (see _gen_own_event_call).
        self._class_events = {self._event_id_of(f) for f in program.functions
                              if not f.params} - {None}

        # Generate each function
        for func_def in program.functions:
            self._generate_function(func_def)

        # End marker
        self.emitter.emit_end()

        # Self-register this file's bare routines/processes as a `uses`
        # provider, keyed by its own basename lowercased (e.g. 'free' for
        # FREE.UNK — matches every `uses "free";` in the corpus, including
        # FREE.UNK's own self-referential `uses "free";`). Harmless for
        # files nobody `uses` — find_provider_function() is only ever
        # consulted for names a consumer actually declared in its own
        # `uses` list.
        provider_key = os.path.splitext(self.filename)[0].lower()
        for func_name, overloads in self._function_table.items():
            for arity, (offset, return_kind) in overloads.items():
                self.symbols.register_provider_function(
                    provider_key, func_name, arity, self._classid,
                    offset, return_kind)

        # Build class with header
        # Calculate unknown1 and unknown2 (seems to follow patterns from the base game)
        # For now, use simple placeholders
        total_size_placeholder = 0x0C + 128 + len(self.emitter.code)
        unknown1 = total_size_placeholder + 0x100  # approximation
        unknown2 = total_size_placeholder + 0x50   # approximation

        return self.emitter.build_class(unknown1, unknown2, self.events)

    def _event_id_of(self, func_def):
        """Event slot of a function definition, or None.

        Only a `Class::name` definition is an event handler. A bare
        `routine combine(i:Item)` (FREE.UNK, the only bare function in the
        corpus whose name is also an event, combine = 12) is an ordinary
        routine: retail FREE 0x581 give() calls it as one, `push [BP-02h];
        call 0581h 2767h` at 200D. Taking it as event 12 left it out of the
        function table, so `combine(item)` bound the 0-arg intrinsic
        Item::combine (0x65) on a garbage `this` instead.
        """
        if not func_def.class_name:
            return None
        return self.symbols.get_event_id(func_def.func_name)

    def _is_same_class_method(self, classid, call):
        """True if `call` resolved into this class and names one of its
        non-event `Class::method`s (see _methods in generate_class)."""
        return (classid == self._classid and
                (call.name.lower(), len(call.args)) in
                getattr(self, '_methods', ()))

    def _push_this_or_null(self):
        """Push the caller's `this` for a method call, or a null dword when
        the caller is a bare routine with no `this` of its own."""
        if getattr(self, '_func_has_this', False):
            self.emitter.emit_push_dword_bp(0x06)
        else:
            self.emitter.emit_push_dword(0)

    def _generate_function(self, func_def):
        """Generate bytecode for a function definition."""
        # Reset local state
        self._local_vars = {}
        self._slist_locals = set()   # track String List variables
        self._list_locals = set()    # track Item/Number List variables
        self._string_locals = set()  # track String variables
        self._worldpoint_locals = set()  # track WorldPoint variables
        self._has_enter_convo = False  # track if enterConvo() was used
        self._next_bp = 0
        # (free opcode, BP offset) of every String / String List / List
        # local, in declaration order: the function's exit frees them.
        self._freeable_locals = []

        # Determine event ID
        event_id = self._event_id_of(func_def)
        # An event handler or a method holds `this` at BP+06; a bare
        # routine holds its first param there.
        is_method = (func_def.func_name.lower(), len(func_def.params)) in \
            getattr(self, '_methods', ())
        self._func_has_this = event_id is not None or is_method
        # `return <expr>` hands its value over by function kind (see
        # _gen_return), and every `return` jumps to this function's single
        # exit, the epilogue label defined just before its `ret`.
        self._func_is_process = (func_def.kind or '').lower() == 'process'
        self._epilogue_label = self._new_label('epilogue')

        # Record event table entry, and (for bare, non-event functions)
        # this function's offset for same-class / `uses`-provider
        # resolution — capture BEFORE emit_init, same point event offsets
        # are captured, so the recorded offset is this function's very
        # first instruction (what a cross-class 0x11/0x57 call must land
        # on).
        func_offset = self.emitter.offset
        # Every function's first instruction, as a label: the base the
        # 0x58 `spawn inline` offset+delta pair is measured from.
        self._func_start_label = self._new_label('funcstart')
        self.emitter.define_label(self._func_start_label)
        if event_id is not None:
            self.events[event_id] = func_offset
            # Also mark this position with a label (M2). Labels are shifted
            # in place by every trampoline relay insertion, so build_class()
            # can read the handler's TRUE final offset back out instead of
            # writing the pre-relay value into the event table.
            self.emitter.define_label(self.emitter.event_label(event_id))
        else:
            # Define this bare function's forward-reference label NOW, at
            # its very first instruction — the same offset _function_table
            # will record a few lines down. Any earlier-compiled function
            # in this class that referenced this name via a forward spawn/
            # call (emit_spawn_label/emit_call_label) already has a
            # 'funcoffset' fixup pointing at this exact label; harmless to
            # define even when nothing ever references it.
            self.emitter.define_label(
                self._forward_label(func_def.func_name.lower(), len(func_def.params)))

        # Prologue: allocate locals
        # We'll emit init with 0 first, then patch it later
        init_pos = len(self.emitter.code)
        self.emitter.emit_init(0)

        # Standard process preamble: set info + process exclude
        if event_id is not None:
            # Push process type ID: retail's per-event type, not 0x208+id
            # (that held only for look and anim). See RETAIL_EVENT_TYPES.
            self.emitter.emit_push_word(
                RETAIL_EVENT_TYPES.get(event_id or 0, 0x0208 + (event_id or 0)))
            # Push this pointer
            self.emitter.emit_push_dword_bp(0x06)
            self.emitter.emit_push_indirect(0x02)
            self.emitter.emit_set_info()
            self.emitter.emit_process_exclude()

        # Register parameters as locals.
        #
        # Event-dispatched functions (event_id is not None: look/use/hatch/
        # schedule/cast/...) keep the ORIGINAL (negative BP offset, "local
        # variable" style) allocation below unconditionally — that is
        # existing, shipped, and validated behavior (11 NPC files declare
        # params on schedule()/cast()) and this work does not touch it.
        #
        # Bare functions (event_id is None: `uses`-provider routines like
        # FREE's getPeriod/killProcess/scrollBack, and same-class
        # processes like LORDBRIT's puppet) get NO preamble above, so the
        # VM's calling convention places the caller's pushed arguments at
        # POSITIVE BP offsets starting at BP+06, one word (2 bytes) per
        # argument regardless of declared type — confirmed against base
        # game bytecode (MYTHRAN calling FREE's give(r,t,f,qual,quan):
        # `push [BP+06h]` reads the first param; 5 args pushed as 5 words,
        # `add sp -10` cleanup). Before this fix these names were silently
        # allocated as uninitialized NEGATIVE-offset locals instead — dead
        # code, since nothing could call a bare function until this work
        # added the resolution/emission side, so there is no prior
        # behavior to preserve here.
        if event_id is None:
            bp = 0x0A if is_method else 0x06
            for param in func_def.params:
                self._local_vars[param.name] = bp
                if param.type_name in ('String', 'String Reference'):
                    self._string_locals.add(param.name)
                elif param.type_name == 'String List':
                    self._slist_locals.add(param.name)
                elif param.type_name.endswith(' List'):
                    self._list_locals.add(param.name)
                bp += 2
            key = func_def.func_name.lower()
            self._function_table.setdefault(key, {})[len(func_def.params)] = (
                func_offset, self._classify_return_kind(func_def.return_type,
                                                        func_def.kind))
        else:
            for param in func_def.params:
                self._alloc_local(param.name)

        # Generate body
        if func_def.body:
            self._generate_block(func_def.body)

        # Epilogue: a body that falls off its end after enterConvo() runs
        # exitConvo() for it, unless every way to the end already passes
        # one: a top-level bare exitConvo() after the last top-level
        # statement holding an enterConvo() (ARAMINA's use() ends
        # `exitConvo(); }`, ZCHILD's `exitConvo(); cSetActivity(..); }`),
        # or a final `return`. A second exitConvo would scroll the camera
        # and restart the NPC's activity again.
        if self._has_enter_convo:
            body = getattr(func_def.body, 'stmts', None) or []
            last_enter = max(i for i, s in enumerate(body)
                             if _contains_node(s, EnterConvoStmt))
            exited = any(isinstance(s, ExitConvoStmt) and s.target is None
                         for s in body[last_enter + 1:])
            if not (exited or isinstance(body[-1], ReturnStmt)):
                self._gen_exit_convo(None)
        # The shared exit every `return` jumps to. It sits after the
        # enterConvo cleanup above, so a `return` skips that cleanup exactly
        # as the bare `ret` it replaces did.
        self.emitter.define_label(self._epilogue_label)
        # Free every heap-owning local, in declaration order, then return:
        # retail FREE 0x581 askYesNo 1B43 `62 FE; 63 FC; 50` (key:String,
        # keyList:String List), give() 20B4 `64 F8; 50` (its Item List),
        # METHOD 0x57C ask 010D `63 FE; 62 FC; 50`. Parameters are the
        # caller's and are never freed here (FREE listTop 3670 frees only
        # its local, not its String List param). Without this every
        # give()/take() call leaked an item list and every conversation
        # leaked its option list and answer string.
        for free_op, bp_off in self._freeable_locals:
            self.emitter.emit_op(free_op)
            self.emitter.emit_byte(bp_off & 0xFF)
        self.emitter.emit_ret()
        self.emitter.emit_end()

        # Patch init with actual local bytes
        self.emitter.code[init_pos + 1] = self._next_bp & 0xFF

    def _generate_block(self, block):
        """Generate bytecode for a block of statements."""
        for stmt in block.stmts:
            self._generate_statement(stmt)

    def _gen_process_block(self, block):
        """Generate a bare `process { ... }` block (kind='process') as an
        unconditional loop: a label at the top, a `suspend`, the block's
        own statements, then a backward `jmp` to that label.

        Found 2026-10-01, verified against retail class 0x2FE
        (TypePotion::protection()/invisible(), offsets 0x059B/0x0687):
        each compiles its `process { ... }` section to exactly this
        shape, reached only by falling off the end of the block without
        an explicit `return`. `return` anywhere inside (even nested in an
        `if`) jumps to the function's epilogue (_gen_return) and exits
        before the backward jmp is ever reached, so no extra
        exit handling is needed here. Before this, every `process { }`
        in the corpus (base-game-style files like POTION.UNK, METHOD.UNK,
        AIRSPEL.UNK, FREE.UNK, and LORDBRIT.UNK's puppet()) compiled as a
        single straight-through pass -- the LORDBRIT animation bug this
        closes, and, unfixed, a latent Avatar-stays-immortal-forever bug
        in POTION.UNK's protection().
        """
        # THE SUSPEND AT THE LOOP HEAD (2026-10-02). Retail's backward jmp
        # lands on a `suspend` (0x53), so every lap yields to the scheduler
        # whatever the body does: TypePotion 0x0634, GUARD1 0x103D, and 184
        # backward jumps across retail land the same way. Without it a body
        # whose only yields sit inside a branch or a search that finds
        # nothing spins inside one engine tick, and the engine's "stuck in
        # process loop" guard counts runs, not instructions, so it never
        # fires: ARAMINA's atHome() hard-froze ScummVM on Map 41
        # (docs/playtest-2026-10-01-process-loops.md). The shape is the one
        # docs/reviews/2026-07-23-h1-process-block-semantics.md specified:
        # `.loop: suspend; body; jmp .loop`.
        loop_label = self._new_label('procloop')
        self.emitter.define_label(loop_label)
        self.emitter.emit_suspend()
        for stmt in block.stmts:
            self._generate_statement(stmt)
        self.emitter.emit_jmp_label(loop_label)

    def _gen_return(self, stmt):
        """`return [expr];`: hand the value over, then jump to the epilogue.

        A routine returns through the temp register, which its caller reads
        with `push retval`/`push byte retval`: retail FREE 0x581 abs()
        1C5C-1C5F `push [BP+06h]; pop temp; jmp`. A process returns through
        the process-result register, which a spawning caller reads with
        `push process result`: FREE askYesNo 1B1A-1B1E `push byte 1; int to
        long; pop result; jmp`. Every `return` (bare ones too, METHOD 0x57C
        boom 06F2) jumps to the single exit before `ret`, even when that is
        the next instruction (`jmp +0`, FREE 1C68). Until 2026-10-07 this
        was a bare `ret` that dropped the value, so `if give(...)` read
        whatever the temp register last held.
        """
        if stmt.expr is not None:
            self._gen_expression(stmt.expr)
            if self._func_is_process:
                self.emitter.emit_op(0x60)  # int to long
                self.emitter.emit_op(0x08)  # pop result
            else:
                self.emitter.emit_pop_temp()
        self.emitter.emit_jmp_label(self._epilogue_label)

    def _generate_statement(self, stmt):
        """Generate bytecode for a statement."""
        if isinstance(stmt, VarDecl):
            self._gen_var_decl(stmt)
        elif isinstance(stmt, ExprStmt):
            self._gen_expr_stmt(stmt)
        elif isinstance(stmt, Assignment):
            self._gen_assignment(stmt)
        elif isinstance(stmt, IfStmt):
            self._gen_if(stmt)
        elif isinstance(stmt, WhileStmt):
            self._gen_while(stmt)
        elif isinstance(stmt, ForStmt):
            self._gen_for(stmt)
        elif isinstance(stmt, ForEachStmt):
            self._gen_foreach(stmt)
        elif isinstance(stmt, ReturnStmt):
            self._gen_return(stmt)
        elif isinstance(stmt, BarkStmt):
            self._gen_bark(stmt)
        elif isinstance(stmt, WaitStmt):
            self._gen_wait(stmt)
        elif isinstance(stmt, SpawnStmt):
            self._gen_spawn(stmt)
        elif isinstance(stmt, SwitchStmt):
            self._gen_switch(stmt)
        elif isinstance(stmt, PostfixOp):
            self._gen_postfix(stmt)
        elif isinstance(stmt, Block):
            if getattr(stmt, 'kind', '') == 'process':
                self._gen_process_block(stmt)
            else:
                self._generate_block(stmt)
        elif isinstance(stmt, BreakStmt):
            pass  # handled by parent switch/loop
        elif isinstance(stmt, EnterConvoStmt):
            # enterConvo(): spawn retail METHOD Npc::enterConvo (0x57C
            # 0BCF) on the NPC and wait, byte for byte as all 49 retail
            # sites do (u8c_symbols METHOD_ROUTINES). It kills the NPC's
            # 0x205/0x200/0xF0/0x204 processes on `referent` itself, so no
            # resetRef is emitted here, and never one on
            # Npc::getNpcSlot() (intrinsic 0x9A allocates a free slot and
            # returns 0, and resetRef(0, type) kills that type for EVERY
            # item: docs/playtest-2026-10-02-pt-activity.md finding 2).
            # `npc.enterConvo()` (FREE's `agent.enterConvo()`, agent a
            # local Npc) spawns it on that NPC, as retail 0x4B5 0301 does
            # through `push addr [BP-02h]`. Only the bare form arms the
            # end-of-function exitConvo epilogue: that resumes [BP+06],
            # which is the talked-to NPC only when it is `referent`.
            if stmt.target is None:
                self._has_enter_convo = True
            self._emit_usecode_method(self._convo_routine('enterConvo'),
                                      [], stmt.target, False, 'wait')
        elif isinstance(stmt, ExitConvoStmt):
            self._gen_exit_convo(stmt.target)
        elif isinstance(stmt, PreprocIf):
            # #if English/French/German { ... } — compile English only
            if stmt.language.upper() == 'ENGLISH':
                self._generate_block(stmt.body)

    # Heap-owning local types and the opcode that frees one at [BP+xx]
    # (any other `... List` is a word/Item list, 0x64). See
    # _emit_epilogue_frees.
    _FREE_OPS = {'String': 0x62, 'String List': 0x63}

    def _gen_var_decl(self, decl):
        """Generate variable declaration."""
        for name in decl.names:
            size = 2  # default word
            if decl.type_name == 'WorldPoint':
                # The engine's WorldPoint is a 5-BYTE buffer (world_point.h
                # _buf[5]: x/y little-endian uint16 at +0/+2, z byte at +4),
                # and Item::I_getPoint writes all 5 through assignPointer.
                # 4 bytes (the old size) meant every getPoint overflowed the
                # neighboring local by one byte. 6 keeps BP offsets even.
                size = 6
                self._worldpoint_locals.add(name)
            elif decl.type_name in ('Item', 'Npc', 'Referent'):
                size = 4  # dword for object refs
            elif decl.type_name == 'String':
                size = 4  # string pointer
                self._string_locals.add(name)
            elif decl.type_name == 'String List':
                size = 4
                self._slist_locals.add(name)
            elif decl.type_name.endswith(' List'):
                # `Item List` / `Number List` (FREE.UNK give/take/combine/
                # createNear): a 2-byte list handle, as retail FREE 0x581
                # give() keeps its itemList at [BP-08h] beside 2-byte locals.
                self._list_locals.add(name)
            elif decl.type_name == 'Long':
                size = 4
            self._alloc_local(name, size)
            free_op = self._FREE_OPS.get(decl.type_name)
            if free_op is None and decl.type_name.endswith(' List'):
                free_op = 0x64
            if free_op is not None:
                self._freeable_locals.append((free_op, self._get_local(name)))

        if decl.initializer:
            self._gen_expression(decl.initializer)
            bp_off = self._get_local(decl.names[0])
            if bp_off is not None:
                self.emitter.emit_pop_bp(bp_off)

    # Statement-form process-type pragmas: `[[<PT_*>, <ref>]];`
    #
    # These are NOT inert (2026-07-26, the first-map-change collapse): the
    # 1994 compiler emitted `set info` (opcode 0x77) for the statement
    # form, re-branding the running process's (itemNum, processType). On
    # every U8 map change the engine kills all processes with itemNum != 0
    # AND type != 1 (ScummVM world.cpp switchMap ->
    # killProcessesNotOfType(0, 1)), so a scene that teleports across maps
    # must re-brand itself first or it is killed inside its own teleport
    # intrinsic and its return trip never runs. AVATAR::schedule()'s Lord
    # British vision died exactly there, stranding the Avatar on map 0.
    #
    # Only PT_DEFAULT's value is pinned (= 1, protective via the type==1
    # test). Each accepted <ref> spelling is pinned by exact per-class
    # site-count matches between the 1994 sources and retail bytecode:
    #
    #   NULL_REF / NUL_REF / 0    0A 01 0A 00 77
    #       POTION 3/3, TORWIN 2/2, DARION 1/1, FREE 5/5
    #   referent[:Referent]       0A 01 40 06 4C 02 77
    #       METHOD 9/9, JENNA 2/2, MORDEA 1/1, DARION 1/1, STRATOS 2/2
    #   Avatar:Referent           0A 01 0A 01 77   (Avatar objid == 1)
    #       FREE 2/2, STRATOS 1/1
    #
    # Anything else — every other PT_* type and expression referents like
    # `ball.referent` (AIRSPEL) — still compiles to nothing, but now warns
    # loudly. Pin a new PT_* value against retail bytecode (the count
    # method above) before adding it here; do not guess.
    #
    # PT_ACTIVITY = 0x205, pinned 2026-10-02 by the same count method:
    # `0B 05 02 40 06 4C 02 77` (push word 0x205, push this, set info)
    # appears in retail USECODE.FLX exactly as often as
    # `[[PT_ACTIVITY, referent]]` appears in the 1994 source, in all 11 NPC
    # classes with a source in lv-usecode/U8/: ARAMINA 7/7, BENTIC 2/2,
    # CYRRUS 7/7, DARION 6/6, JENNA 4/4, KILANDRA 2/2, MORDEA 7/7,
    # SALKIND 4/4, STELLOS 4/4, TORWIN 4/4, XAVIER 7/7. (METHOD reads 1
    # against retail's 5; our METHOD.UNK is the dev-tier copy.) Dropping it
    # left ARAMINA's spawned atHome() as item 0, type 0, which neither her
    # leaveFastArea nor a map switch kills: once process blocks looped it
    # ran forever and stacked a copy per visit to Map 41
    # (docs/playtest-2026-10-02-process-loops-suspend.md).
    PRAGMA_TYPES = {'PT_DEFAULT': 1, 'PT_ACTIVITY': 0x205}

    # Compound assignment -> arithmetic opcode (operands: target, then RHS).
    COMPOUND_OPS = {'+=': 0x14, '-=': 0x1C, '/=': 0x20}
    PRAGMA_NULL_REFS = frozenset({'NULL_REF', 'NUL_REF', '0'})

    def _push_pragma_type(self, ptype):
        """Push a process type the way retail does: a byte (0A) for a
        value that fits, a word (0B) otherwise, as PT_ACTIVITY's 0B 05 02."""
        if ptype <= 0xFF:
            self.emitter.emit_push_byte(ptype)
        else:
            self.emitter.emit_push_word(ptype)

    def _gen_pragma_stmt(self, expr):
        """Emit `set info` for a statement-form [[PT_*, ref]] pragma.

        Stack order matches the engine's 0x77 handler, which pops itemNum
        first, then type — so the type is pushed first.
        """
        body = expr.name[2:-2]
        parts = [p.strip() for p in body.split(',')]
        ptype = self.PRAGMA_TYPES.get(parts[0]) if len(parts) == 2 else None
        if ptype is not None:
            ref = parts[1]
            if ref in self.PRAGMA_NULL_REFS:
                self._push_pragma_type(ptype)
                self.emitter.emit_push_byte(0)   # itemNum 0: never killed
                self.emitter.emit_set_info()
                return
            if ref in ('referent', 'referent:Referent'):
                self._push_pragma_type(ptype)
                self.emitter.emit_push_dword_bp(0x06)  # this item, same
                self.emitter.emit_push_indirect(0x02)  # idiom as preamble
                self.emitter.emit_set_info()
                return
            if ref == 'Avatar:Referent':
                self._push_pragma_type(ptype)
                self.emitter.emit_push_byte(1)
                self.emitter.emit_set_info()
                return
        self._warn(expr, f"DROPPED PRAGMA [[{body}]] — no set info emitted; "
                   "the process keeps its event identity and WILL be killed "
                   "by the next map change (unpinned PT_* value or referent "
                   "form; pin it against retail bytecode before emitting)")

    def _gen_expr_stmt(self, stmt):
        """Generate an expression statement (for side effects)."""
        if isinstance(stmt.expr, Identifier) and stmt.expr.name.startswith('[['):
            # A `[[PT_DEFAULT, referent]];` process-type-annotation pragma
            # used as a STATEMENT (LORDBRIT.UNK:16, distinct from the same
            # annotation on a member/function declaration header, which
            # the parser already stores in .annotations and codegen never
            # consults). The lexer hands this whole bracketed pragma back
            # as one IDENT token.
            self._gen_pragma_stmt(stmt.expr)
            return
        if (isinstance(stmt.expr, Identifier) and stmt.expr.name == 'suspend'
                and self._get_local('suspend') is None):
            # `suspend;` (lv-patched/MAGNET.UNK:274, AIRSPEL.UNK:1149/1208):
            # the VM's yield, opcode 0x53, which the 1994 compiler also
            # emits at the head of every process-block lap (TypePotion
            # 0x2FE 0634). It parsed as an unknown identifier and compiled
            # to a stray `push 0`.
            self.emitter.emit_suspend()
            return
        if isinstance(stmt.expr, BarkStmt):
            self._gen_bark(stmt.expr)
        elif isinstance(stmt.expr, MethodCall):
            self._gen_method_call(stmt.expr)
        elif isinstance(stmt.expr, FunctionCall):
            self._gen_function_call(stmt.expr)
        elif isinstance(stmt.expr, BinaryOp) and stmt.expr.op == '=':
            # Assignment expression like lbStarted = 1
            self._gen_assignment(Assignment(target=stmt.expr.left,
                                           op='=', value=stmt.expr.right))
        else:
            self._gen_expression(stmt.expr)

    def _gen_assignment(self, asn):
        """Generate assignment."""
        if isinstance(asn.target, Identifier):
            name = asn.target.name
            # Check if it's a global flag
            flag = self.symbols.get_global_flag(name)
            if flag:
                bit_offset, bits = flag
                # Compound ops on a (multi-bit) global need read-modify-write;
                # the plain path below ignores asn.op and would turn
                # `g += x` into `g = x`. Same operand order as the numeric
                # local case (sub = first_pushed - second_pushed, 0x1C).
                if asn.op in self.COMPOUND_OPS:
                    self.emitter.emit_push_global(bit_offset, bits)
                    self._gen_expression(asn.value)
                    self.emitter.emit_op(self.COMPOUND_OPS[asn.op])
                    self.emitter.emit_pop_global(bit_offset, bits)
                    return
                if asn.op == '^=':
                    self._warn(asn.target, f"compound '^=' on global '{name}' "
                               "has no defined semantics (union is String-List "
                               "only); no bytecode emitted")
                    return
                self._gen_expression(asn.value)
                self.emitter.emit_pop_global(bit_offset, bits)
                return
            # Local variable
            bp_off = self._get_local(name)
            if bp_off is not None:
                # Item/Number List locals (FREE.UNK give/take/combine/
                # createNear). Retail FREE 0x581 give():
                #   L = <<item>>   1F61  push [item]; 0E 02 01; 64 F8; 01 F8
                #   L += <<item>>  1FBF  42 F8 02; push [item]; 0E 02 01;
                #                        17; 64 F8; 01 F8
                # i.e. `push list` (0x42, a copy), the new one-element list,
                # append, then free the old handle and store the new one.
                if name in self._list_locals:
                    if asn.op == '+=':
                        self.emitter.emit_push_list(bp_off)
                        self._gen_expression(asn.value)
                        self.emitter.emit_append()
                    elif asn.op == '=':
                        self._gen_expression(asn.value)
                    else:
                        self._warn(asn.target, f"compound '{asn.op}' on list "
                                   f"'{name}' has no retail form; no bytecode "
                                   "emitted")
                        return
                    self.emitter.emit_free_list(bp_off)
                    self.emitter.emit_pop_bp(bp_off)
                    return
                # String list compound operations: +=, -=, ^=
                if name in self._slist_locals and asn.op in ('+=', '-=', '^='):
                    if asn.op == '+=':
                        # append: push existing, push new, append
                        self.emitter.emit_push_slist(bp_off)
                        self._gen_expression(asn.value)
                        self.emitter.emit_append()
                    elif asn.op == '-=':
                        # subtract: push existing, push elements to remove, subtract
                        self.emitter.emit_push_slist(bp_off)
                        self._gen_expression(asn.value)
                        self.emitter.emit_subtract_slist(0x02)
                    elif asn.op == '^=':
                        # prepend/union: push new FIRST, push existing SECOND
                        self._gen_expression(asn.value)
                        self.emitter.emit_push_slist(bp_off)
                        self.emitter.emit_union_slist(0x02)
                    self.emitter.emit_free_slist(bp_off)
                    self.emitter.emit_pop_bp(bp_off)
                    return
                # Numeric / String compound ops: += and -= (^= is meaningful
                # only for String Lists, handled above). Before this, a
                # non-slist compound op fell through to the plain-assignment
                # path below, which ignores asn.op: `x += 16` emitted
                # `push 16; pop x` (x = 16) with no arithmetic, and
                # `s += "?"` freed s and stored only "?". Shipped
                # LOST VALE/FREE.UNK relies on quan-=666, charge+=mana/5,
                # x+=16, y-=16, remainder-=quan, ran+=a (adversarial review
                # C1, 2026-07-19).
                if asn.op in ('+=', '-=', '/=', '^='):
                    if name in self._string_locals:
                        # s += x  ==  s = s + x. Emitted as the base game's
                        # string-append idiom: push s, push x, concat (0x16),
                        # free the old s handle, pop the extended handle back.
                        # concat extends the FIRST-pushed string in place and
                        # frees the second (uc_machine.cpp 0x16), so s is
                        # pushed first; byte-matches retail (e.g. the
                        # " obsidian coin" append in the base FLX).
                        if asn.op != '+=':
                            self._warn(asn.target, f"compound '{asn.op}' on "
                                       f"String '{name}' — only += (concat) is "
                                       "defined; no bytecode emitted")
                            return
                        self.emitter.emit_push_string_bp(bp_off)
                        self._gen_expression(asn.value)
                        self.emitter.emit_concat()
                        self.emitter.emit_op(0x62)   # free string [BP+off]
                        self.emitter.emit_byte(bp_off & 0xFF)
                        self.emitter.emit_pop_bp(bp_off)
                        return
                    if asn.op == '^=':
                        self._warn(asn.target, f"compound '^=' on numeric "
                                   f"'{name}' has no defined semantics (union "
                                   "is String-List only); no bytecode emitted")
                        return
                    # numeric += / -= / /= : read-modify-write. sub/div are
                    # (first_pushed OP second_pushed) per uc_machine.cpp
                    # 0x1C/0x20, so push the variable FIRST then the RHS —
                    # matching the base game (DOOR_NS `pos += delta`: push
                    # pos, push delta, add/sub, pop pos; FREE 0x581 getPeriod
                    # `getHour() / 4`: push retval, push byte 4, div).
                    self.emitter.emit_push_bp(bp_off)
                    self._gen_expression(asn.value)
                    self.emitter.emit_op(self.COMPOUND_OPS[asn.op])
                    self.emitter.emit_pop_bp(bp_off)
                    return
                # Plain assignment — free old value AFTER evaluating the
                # new expression, matching the base game pattern.  This is
                # safer: (a) the old handle stays valid during expression
                # evaluation so self-referencing expressions (str = str + x)
                # work, and (b) there is no dangling-handle window between
                # the free and the pop that stores the new value.
                self._gen_expression(asn.value)
                if name in self._slist_locals:
                    self.emitter.emit_free_slist(bp_off)
                elif name in self._string_locals:
                    self.emitter.emit_op(0x62)  # free string [BP+xx]
                    self.emitter.emit_byte(bp_off & 0xFF)
                self.emitter.emit_pop_bp(bp_off)
            else:
                self._warn(asn.target, f"assignment to unknown identifier "
                           f"'{name}' — no bytecode emitted")

        elif (isinstance(asn.target, MemberAccess)
              and isinstance(asn.target.obj, Identifier)
              and asn.target.obj.name in self._worldpoint_locals
              and asn.target.member in ('x', 'y', 'z')):
            # WorldPoint member write: word at +0 (.x) / +2 (.y), byte at
            # +4 (.z) — the engine buffer layout (world_point.h). Before
            # this branch existed, `point.x = N` fell through the whole
            # elif chain and emitted NOTHING, silently: every schedule
            # destination and scene coordinate written this way was a
            # no-op, and the buffers stayed zeroed.
            bp_off = self._get_local(asn.target.obj.name)
            self._gen_expression(asn.value)
            if asn.target.member == 'x':
                self.emitter.emit_pop_bp(bp_off)
            elif asn.target.member == 'y':
                self.emitter.emit_pop_bp((bp_off + 2) & 0xFF)
            else:
                self.emitter.emit_pop_byte_bp((bp_off + 4) & 0xFF)

        elif isinstance(asn.target, MemberAccess) and asn.target.member == 'referent':
            # `X.referent = Y` — `.referent` on an Item-typed local is a
            # transparent accessor: the RVALUE side already treats it that
            # way (_gen_expression's MemberAccess case just pushes
            # expr.obj, ignoring the member name entirely), so the
            # assignment side must be identical to a plain `X = Y`.
            # Before this fix, `_gen_assignment` had NO branch at all for
            # a non-Identifier target, so every one of this idiom's 30+
            # occurrences across the corpus (FREE.UNK, ZEALSHLD.UNK,
            # SHADES.UNK, LORDBRIT.UNK's own `lb.referent =
            # item.referent`) silently compiled to ZERO bytes — not even
            # a warning. Delegate onto the underlying variable so it goes
            # through the exact same local-variable / global-flag logic
            # above.
            self._gen_assignment(Assignment(line=asn.line, col=asn.col,
                                             target=asn.target.obj,
                                             op=asn.op, value=asn.value))

    def _gen_if(self, stmt):
        """Generate if/else."""
        self._gen_expression(stmt.condition)
        else_label = self._new_label('else')
        end_label = self._new_label('endif')

        if stmt.else_block:
            self.emitter.emit_jne_label(else_label)
            self._generate_block(stmt.then_block)
            self.emitter.emit_jmp_label(end_label)
            self.emitter.define_label(else_label)
            if isinstance(stmt.else_block, Block):
                self._generate_block(stmt.else_block)
            elif isinstance(stmt.else_block, IfStmt):
                self._gen_if(stmt.else_block)
            self.emitter.define_label(end_label)
        else:
            self.emitter.emit_jne_label(end_label)
            self._generate_block(stmt.then_block)
            self.emitter.define_label(end_label)

    def _gen_while(self, stmt):
        """Generate while loop."""
        loop_label = self._new_label('while')
        end_label = self._new_label('endwhile')
        self.emitter.define_label(loop_label)
        self._gen_expression(stmt.condition)
        self.emitter.emit_jne_label(end_label)
        self._generate_block(stmt.body)
        self.emitter.emit_jmp_label(loop_label)
        self.emitter.define_label(end_label)

    def _gen_for(self, stmt):
        """Generate for loop."""
        # Initialize counter
        bp_off = self._get_local(stmt.var_name)
        if bp_off is None:
            bp_off = self._alloc_local(stmt.var_name)

        self._gen_expression(stmt.start)
        self.emitter.emit_pop_bp(bp_off)

        loop_label = self._new_label('for')
        end_label = self._new_label('endfor')

        self.emitter.define_label(loop_label)
        # Check condition: var <= end
        self.emitter.emit_push_bp(bp_off)
        self._gen_expression(stmt.end)
        self.emitter.emit_op(0x2A)  # le
        self.emitter.emit_jne_label(end_label)

        self._generate_block(stmt.body)

        # Increment
        self.emitter.emit_push_byte(1)
        self.emitter.emit_push_bp(bp_off)
        self.emitter.emit_op(0x14)  # add
        self.emitter.emit_pop_bp(bp_off)

        self.emitter.emit_jmp_label(loop_label)
        self.emitter.define_label(end_label)

    def _gen_foreach_list(self, stmt, var_bp):
        """`foreach x in L { body }` over a list local or parameter.

        Retail FREE 0x581 give() 1FCF-1FE5 (`foreach item in itemList {
        item.destroy(); }`):
            42 F8 02        push list [BP-08h] 02h   (a copy of L)
            0B FF FF        push FFFFh               (loop index)
          .top:
            75 FE 02 rel16  for each [BP-02h] 02h -> .end
            <body>
            52 rel16        jmp .top
          .end:
        A String List uses `push slist` (0x43) and `for each str` (0x76):
        FREE 0x581 29BA-29CB (countStrList, the list a parameter at
        [BP+06h]). No cleanup follows: 0x75/0x76 free the copy and pop
        both words when the iteration ends (uc_machine.cpp case 0x75).
        """
        lst = stmt.container_expr
        name = lst.name if isinstance(lst, Identifier) else None
        bp = self._get_local(name) if name else None
        if bp is not None and name in self._list_locals:
            self.emitter.emit_push_list(bp)
            opcode = 0x75
        elif bp is not None and name in self._slist_locals:
            self.emitter.emit_push_slist(bp)
            opcode = 0x76
        else:
            self._warn(stmt, f"foreach over '{name or type(lst).__name__}', "
                       "not a list local — loop dropped")
            return
        self.emitter.emit_push_word(0xFFFF)
        top = self._new_label('forlist')
        end = self._new_label('endforlist')
        self.emitter.define_label(top)
        self.emitter.emit_foreach_list_label(opcode, var_bp, end)
        if stmt.body:
            self._generate_block(stmt.body)
        self.emitter.emit_jmp_label(top)
        self.emitter.define_label(end)

    def _gen_foreach(self, stmt):
        """Generate foreach loop using loop/loopscr/loopnext opcodes.

        foreach [recursive] var where (conditions) within N cells of referent { body }
        foreach [recursive] var where (conditions) within container X { body }

        Base game bytecode pattern:
          loopscr ...                ; filter script bytes FIRST
          push container/referent    ; what to search around/in
          [push FFFFh]               ; for container searches
          loop bp_var script_size search_type  ; init search + first iteration
          check_label:
          jne end_loop               ; if done, exit
          [body]
          loopnext                   ; advance to next item
          jmp check_label            ; back to jne check
          end_loop:
        """
        # Allocate loop variable
        bp_off = self._get_local(stmt.var_name)
        if bp_off is None:
            bp_off = self._alloc_local(stmt.var_name, 2)

        if stmt.search_type == 'list':
            self._gen_foreach_list(stmt, bp_off)
            return

        # Determine search type
        if stmt.search_type == 'container':
            search_type = 5 if stmt.recursive else 4
        else:  # 'cells' / area search
            search_type = 3 if stmt.recursive else 2

        # Build the loop filter script
        script = self._build_loop_script(stmt.conditions)
        script_size = sum(2 if isinstance(b, ASTNode) else 1 for b in script)

        # Emit loop script bytes FIRST via loopscr (0x74) — before loop init.
        # In REVERSE: each 0x74 push1's its byte onto the downward-growing
        # UC stack, and opcode 0x70 pops the script off with a forward
        # memcpy from the stack top — so the interpreter sees the bytes in
        # reverse push order. Retail bytecode confirms: base-game loopscr
        # runs emit '$' (24) FIRST and the script body backwards. Emitting
        # forward handed checkLoopScript '$' as its first token, which
        # returns the default TRUE for every item — the LB scene's foreach
        # matched a random grass tile instead of the shape-411 apparition
        # (bark/sparkles/destroy on empty grass, hole left in the ground).
        # A runtime operand (an expression node) is pushed as a word in
        # its slot: its low byte lands first in the script, where the
        # preceding '%' reads it (see _build_loop_script).
        for b in reversed(script):
            if isinstance(b, ASTNode):
                self._gen_expression(b)
            else:
                self.emitter.emit_op(0x74)
                self.emitter.emit_byte(b & 0xFF)

        # Operand order is dictated by opcode 0x70's pops (uc_machine.cpp):
        # ui16a = pop2 (LAST pushed), ui16b = pop2 (pushed first).
        #   area search (2/3):      ui16a = center ITEM, ui16b = range
        #   container search (4/5): ui16a = FFFF marker, ui16b = container
        # So area searches push range FIRST, center item LAST — getting
        # this backwards made the engine search "within 1 of item 1024"
        # for LORDBRIT's `within 1024 of Avatar`, matching nothing (the
        # in-game "skipping bark ... because item invalid" failure).
        # Container searches were already pushing container-then-FFFF,
        # which is why the verified dialogue foreach worked all along.
        if stmt.search_type != 'container':
            if stmt.range_expr:
                self._gen_expression(stmt.range_expr)
                if stmt.cells:
                    # `N cells` is N * 32 world units. Retail compiles
                    # the range as `push N; push byte 32; mul` (ARAMINA
                    # 0x40D atHome: push 10, push 32, mul; every retail
                    # NPC class with an area search agrees). We pushed
                    # the bare N, so a "within 50 cells" search covered
                    # 50 units.
                    self.emitter.emit_push_byte(32)
                    self.emitter.emit_op(0x1E)  # mul
            else:
                # The engine pops a range word unconditionally — omitting
                # it would misalign the stack. No LV source hits this
                # (every area foreach says `within N`), but fail safe.
                self._warn(stmt, "area foreach without 'within N' range — "
                           "defaulting range to 0x400")
                self.emitter.emit_push_word(0x400)

        # Push the search reference (referent or container)
        if stmt.container_expr:
            self._gen_expression(stmt.container_expr)
        else:
            # Push this (referent = current object)
            self.emitter.emit_push_dword_bp(0x06)
            self.emitter.emit_push_indirect(0x02)

        # Container searches: FFFF marker goes on top
        if stmt.search_type == 'container':
            self.emitter.emit_push_word(0xFFFF)

        # Emit loop init: 0x70 bp_var script_size search_type
        self.emitter.emit_op(0x70)
        self.emitter.emit_byte(bp_off & 0xFF)
        self.emitter.emit_byte(script_size & 0xFF)
        self.emitter.emit_byte(search_type & 0xFF)

        # Loop check point (loop init does first iteration, loopnext does rest)
        check_label = self._new_label('foreach_check')
        end_label = self._new_label('endforeach')

        self.emitter.define_label(check_label)
        self.emitter.emit_jne_label(end_label)  # if no more items, exit

        # Generate body
        if stmt.body:
            self._generate_block(stmt.body)

        # Advance to next item and jump back to check
        self.emitter.emit_op(0x73)  # loopnext
        self.emitter.emit_jmp_label(check_label)
        self.emitter.define_label(end_label)

        # Free the loop state the search machinery left on the stack.
        # Opcode 0x70 pushes exactly `stacksize` bytes (filler + script +
        # scriptsize + bpoff + index + listid; uc_machine.cpp case 0x70),
        # and the exit-path jne consumes loopnext's 0 flag — retail
        # cleans up with `add sp -stacksize` after the loop (TOMB 0x485:
        # add sp -52 after its area search). We leaked it until
        # 2026-07-05: benign at shallow nesting, stack exhaustion in long
        # conversation loops. U8 stacksizes per search type: area 0x34,
        # container 0x28, recursive container 0x2A.
        stacksize = {2: 0x34, 3: 0x34, 4: 0x28, 5: 0x2A}[search_type]
        self.emitter.emit_add_sp((256 - stacksize) & 0xFF)

    def _build_loop_script(self, conditions):
        """Build the loop filter script for foreach conditions.

        Returns a list in script (read) order. Each element is a byte
        (int) or an expression node standing for a 2-byte operand that
        _gen_foreach pushes at run time.

        Each condition is typically: (type = TypeXXX) and (frame = N)
        Loopscript format (from ScummVM loop_script.h):
          Optimized single-value checks (compile-time constants):
            0x41 'A' + uint16_le — shape equals value (pushes 1/0)
            0x61 'a' + uint16_le — frame equals value (pushes 1/0)
          General comparison (run-time values):
            '%' <word> '@' '='  — shape equals word
            '%' <word> '`' '='  — frame equals word
          Operators:
            0x26 '&' — AND top two stack values
            0x24 '$' — end script, return top of stack

        A value known only at run time (a local, a parameter, a call)
        uses the general form with the word pushed by ordinary code, as
        retail does: ARAMINA 0x40D atHome's `(frame = counter)` is
        `loopscr '=' '`'; push [BP-04h]; loopscr '%'` (04A5-04AB in
        shared/data/USECODE.FLX), FREE 0x581 findNearest's `(type=t) and
        (frame=f)` pushes [BP+08h]/[BP+0Ah] the same way (1E98-1EA6), and
        FREE 0x581 27A8-27B7 pushes `ref.getType()`'s retval. We compiled
        each of these as a constant 0 (a frame-0 or shape-0 filter).
        """
        import struct as _struct
        script = []
        num_conditions = 0

        def runtime(prop_token, value):
            # Read order '%' lo hi <prop> '='; the node fills lo hi.
            script.extend((0x25, value, prop_token, 0x3D))

        for cond in conditions:
            if isinstance(cond, BinaryOp) and cond.op == '=':
                if isinstance(cond.left, Identifier):
                    prop = cond.left.name.lower()
                    right = cond.right
                    is_local = (isinstance(right, Identifier)
                                and self._get_local(right.name) is not None)
                    if prop == 'type':
                        if isinstance(right, NumberLit):
                            shape = right.value
                        elif isinstance(right, Identifier) and not is_local:
                            shape = self.symbols.get_type_shape(right.name)
                            if shape is None:
                                self._warn(cond, f"unknown type '{right.name}' "
                                           "in foreach condition compiled as shape 0")
                                shape = 0
                        else:
                            shape = None
                        if shape is None:
                            runtime(0x40, right)  # '@' shape
                        else:
                            # Optimized: 'A' + uint16 = single shape check
                            script.append(0x41)
                            script.extend(_struct.pack('<H', shape))
                        num_conditions += 1
                    elif prop == 'frame':
                        if isinstance(right, NumberLit):
                            # Optimized: 'a' + uint16 = single frame check
                            script.append(0x61)
                            script.extend(_struct.pack('<H', right.value))
                        else:
                            runtime(0x60, right)  # '`' frame
                        num_conditions += 1
                    else:
                        self._warn(cond, f"unsupported foreach condition on "
                                   f"'{cond.left.name}' ignored (dropped from filter script)")
                else:
                    self._warn(cond, "unsupported foreach condition ignored "
                               "(dropped from filter script)")
            else:
                self._warn(cond, "unsupported foreach condition ignored "
                           "(dropped from filter script)")

        # AND conditions together
        for _ in range(num_conditions - 1):
            script.append(0x26)  # & AND

        # End marker
        script.append(0x24)  # $ end script

        return script

    def _gen_switch(self, stmt):
        """Generate switch statement.

        Multi-value cases (case "A", "B") generate OR-branched comparisons:
        for each value except the last, match jumps to the case body;
        the last value's mismatch jumps to the next case.
        """
        end_label = self._new_label('endswitch')

        for case in stmt.cases:
            next_label = self._new_label('nextcase')

            if isinstance(case.value, StringList) and len(case.value.elements) > 1:
                # Multi-value case (case "A", "B"): retail idiom, verified
                # against three independent base-game sites (0x02C4:04B6,
                # 0x0405:2C6E, 0x0408:413C — all exactly this shape):
                #   push answer / push "A" / strcmp
                #   push answer / push "B" / strcmp
                #   or                          (0x34, one per extra value)
                #   jne next_case
                # The previous emission here OR-branched with not(0x30) +
                # jne-to-body per value, a pattern that appears NOWHERE in
                # the 1433-entry retail FLX and did not dispatch in-engine
                # (ATLI's "Tell me more of the test." pick looped silently).
                values = case.value.elements
                for i, val in enumerate(values):
                    self._gen_expression(stmt.expr)
                    self._gen_expression(val)
                    self.emitter.emit_op(0x26)  # strcmp
                    if i > 0:
                        self.emitter.emit_op(0x34)  # or
                self.emitter.emit_jne_label(next_label)
            else:
                # Single-value case
                self._gen_expression(stmt.expr)
                self._gen_expression(case.value)
                self.emitter.emit_op(0x26)  # strcmp
                self.emitter.emit_jne_label(next_label)

            self._generate_block(case.body)
            self.emitter.emit_jmp_label(end_label)
            self.emitter.define_label(next_label)

        # `default { }`: the fall-through after the last case's test, as
        # retail MORDEA 0x407 18AD-18E9 lays out U8/MORDEA.UNK:798's
        # default (urandom/bark) straight after the last case's jne target.
        if stmt.default is not None:
            self._generate_block(stmt.default)
        self.emitter.define_label(end_label)

    def _gen_bark(self, stmt, mode='wait'):
        """Generate bark() call; `mode` as _spawn_tail (a spawned bark
        with `-> return` is 'discard': retail DARION 0x405 1C7C-1C9D)."""
        # bark generates: push pid, push string, str_to_ptr, push this, calli
        self._spawn_pid(mode)

        if isinstance(stmt.text, StringLit):
            self.emitter.emit_string(stmt.text.value)
        elif isinstance(stmt.text, BinaryOp) and stmt.text.op == '+':
            # String concatenation
            self._gen_expression(stmt.text)
        else:
            self._gen_expression(stmt.text)

        self.emitter.emit_str_to_ptr()

        # Push this pointer as 4-byte UC pointer
        # (bark intrinsic expects ARG_ITEM_FROM_PTR = 4 bytes)
        if stmt.target:
            self._gen_item_ptr(stmt.target)
        else:
            self.emitter.emit_push_dword_bp(0x06)

        self.emitter.emit_calli(0x08, 0x0049)  # Item::bark

        # Cleanup: free string, adjust stack
        self.emitter.emit_free_string_sp(0x04)
        self.emitter.emit_add_sp(0xF8)  # -8
        self._spawn_tail(mode)

    def _gen_wait(self, stmt):
        """Generate wait() call."""
        self.emitter.emit_push_pid()
        self._gen_expression(stmt.ticks)
        self.emitter.emit_push_dword(0)  # null process
        # Spawn the wait process (FREE class wait function)
        free_class = self.symbols.get_class_id('FREE') or 0x0581
        self.emitter.emit_spawn(0x02, 0x00, free_class, 0x1C19)
        self.emitter.emit_add_sp(0xFE)  # -2
        self.emitter.emit_push_retval()
        self.emitter.emit_implies()
        self.emitter.emit_pop_temp()
        self.emitter.emit_suspend()

    # How a spawn's caller treats the new process, from retail USECODE.FLX:
    #   'wait'    a plain call of a process (rule a): push pid; ...; push
    #             retval; implies; pop temp; suspend (FREE 0x581 1CB9,
    #             ARAMINA 0x40D 0C1F).
    #   'inline'  the call an inline process waits on: the 0x58 already
    #             pushed the pid `implies` pairs; no suspend (AVATAR 0x401
    #             2FE4-3008).
    #   'discard' `spawn x -> return;` (rule c): no pid, the caller runs
    #             on; push retval; pop temp after the spawn (ARAMINA 0x40D
    #             021F/0239/0251 own processes, DARION 0x405 1C7C bark,
    #             FREE 0x581 372E item.use(), 37EF flameBlast(p)).
    #   'detach'  arrowless `spawn f();` (rule b, LORDBRIT's puppet; no
    #             retail site): nothing before or after.
    #   'head'/'link'  `spawn a -> spawn b -> return;` (rule d): a leaves
    #             its pid (push retval); each later call pushes its own and
    #             implies, so the pid below waits on it (uc_machine 0x54:
    #             the lower popped pid waitFor()s the upper); the chain's
    #             last pid is then popped. The caller does not wait
    #             (ARAMINA 0x40D 0D55-0D90).
    def _spawn_pid(self, mode):
        if mode == 'wait':
            self.emitter.emit_push_pid()

    def _spawn_tail(self, mode):
        """Everything after a spawn/calli and its stack cleanup."""
        if mode == 'detach':
            return
        self.emitter.emit_push_retval()
        if mode in ('wait', 'inline', 'link'):
            self.emitter.emit_implies()
        if mode in ('wait', 'inline', 'discard'):
            self.emitter.emit_pop_temp()
        if mode == 'wait':
            self.emitter.emit_suspend()

    def _gen_spawn_inline(self, stmt):
        """`spawn call -> [[PT_*, ref]] { body } -> return;`
        (lv-patched/AVATAR.UNK:1047-1050, "Call Guards" in the cheat menu).

        Retail AVATAR 0x401 look() 2FE4-301B compiles exactly this source:
            58 01 04 B2 00 59 2F 02 00   spawn inline 0401:00B2+2F59 (=300B)
            <args, this>; 57 04 02 7C 05 E7 15  spawn caster.realDoAnim
            6E FC; 5E; 54 01 01; 12      the inline pid implies on it
            52 11 00                     jmp over the inline body
          300B: 5A 00; 0A 01 0A 00 77    init 0; [[PT_DEFAULT,NULL_REF]]
                53                       suspend (its first run stops here)
                <body>; 50               caster.setDead(); ret
        The spawn is the ordinary `-> return` spawn with 0x58 standing in
        for `push pid` and no trailing suspend: the caller runs on, the
        inline process waits for the spawned call, then runs the body.
        """
        body = self._new_label('inline')
        after = self._new_label('endinline')
        self.emitter.emit_spawn_inline_label(
            self._classid, self._func_start_label, body,
            0x02 if self._func_has_this else 0x00)
        start = len(self.emitter.code)
        self._gen_spawn_call(stmt.call, 'inline')
        if len(self.emitter.code) == start:
            # The awaited call did not resolve (already warned): nothing
            # to wait on, so drop the inline pid; the body runs next tick.
            self._warn(stmt, "inline spawn's awaited call emitted no code; "
                       "the inline body runs without waiting")
            self.emitter.emit_pop_temp()
        self.emitter.emit_jmp_label(after)
        self.emitter.define_label(body)
        self.emitter.emit_init(0)
        if stmt.inline_pragma:
            self._gen_pragma_stmt(Identifier(name=stmt.inline_pragma))
        self.emitter.emit_suspend()
        # The inline body is its own process with its own frame: a `return`
        # inside it exits the body (process-result register, its own `ret`),
        # never the enclosing function.
        outer = (self._epilogue_label, self._func_is_process)
        self._epilogue_label = self._new_label('inline_epilogue')
        self._func_is_process = True
        try:
            self._generate_block(stmt.inline_body)
            self.emitter.define_label(self._epilogue_label)
            self.emitter.emit_ret()
        finally:
            self._epilogue_label, self._func_is_process = outer
        self.emitter.define_label(after)

    def _gen_spawn(self, stmt):
        """Generate a spawn statement; how the caller treats the new
        process (rule b/c/d) is the `mode` documented at _spawn_tail.
        """
        if stmt.inline_body is not None:
            self._gen_spawn_inline(stmt)
            return
        if stmt.chain:
            linked = False
            for call in [stmt.call, *stmt.chain]:
                start = len(self.emitter.code)
                self._gen_spawn_call(call, 'link' if linked else 'head')
                linked = linked or len(self.emitter.code) != start
            if linked:
                self.emitter.emit_pop_temp()  # the chain's last pid
            return
        self._gen_spawn_call(stmt.call,
                             'discard' if stmt.has_arrow_return else 'detach')

    def _gen_spawn_call(self, call, mode):
        """One spawned call: [push pid], args, [this], spawn or calli,
        cleanup, then _spawn_tail(mode).

        Rule (b), an arrowless spawn, has no retail site: a function or
        METHOD spawn detaches (LORDBRIT's looping puppet must not be
        waited on), while the bark, intrinsic and class-instantiation
        branches keep the full wait an arrowless spawn always had there
        (`legacy`). No shipped source spawns those without an arrow.
        """
        legacy = 'wait' if mode == 'detach' else mode

        if isinstance(call, BarkStmt):
            # spawn bark("text") -> return — common pattern
            # Emit bark as a subprocess
            self._gen_bark(call, legacy)
            return

        if isinstance(call, MethodCall):
            # spawn obj.bark("...") -> return: route through _gen_bark.
            # The generic intrinsic branch below counts every arg as a
            # 2-byte word, but Item::bark takes a char* — the string id
            # must go through `str to ptr` (0x6B) and count 4 bytes.
            # Without this, spawned barks compiled to `calli 06h 0049h`
            # (raw string id where the engine reads a 4-byte pointer):
            # 14 sites across 4 classes, while retail bytecode has 0
            # 6-byte bark calls against 4,533 8-byte ones (found
            # 2026-07-27 when the EGGSHADES ceremony sim crashed on
            # SHADES.UNK:372). _gen_bark emits the proven 8-byte form.
            if call.method == 'bark' and len(call.args) == 1:
                self._gen_bark(BarkStmt(target=call.obj, text=call.args[0]),
                               legacy)
                return
            # spawn obj.method(args) -> return
            # Check if it's an intrinsic method (e.g., doAnim, pathfind).
            # arg_count: overload resolution by arity, same as
            # _gen_method_call (no overloaded name is spawned in the
            # corpus today, so this is consistency, not a change).
            intrinsic = self.symbols.find_intrinsic(call.method,
                                                    arg_count=len(call.args))
            if intrinsic:
                # push pid FIRST when the caller waits — implies at the end
                # pops (spawned pid, our pid) to pair them; every proven
                # wait-shaped sequence (_gen_bark, _gen_wait, retail
                # STRATOS) leads with 0x59. Without it, implies pops a
                # garbage word as a pid and the stack is off by 2.
                self._spawn_pid(legacy)
                # Push args right-to-left (last source arg first), the U8
                # calling convention: the callee/intrinsic reads args from
                # the top of the stack down, so the FIRST declared arg must
                # be the LAST one pushed. Proven from retail bytecode
                # twice: STRATOS's create(TypeMagicSparkle, 11) compiles
                # to `push byte 11; push 024Bh; push addr; calli create`,
                # and a retail Camera::move_to(x,y,z,speed) call site
                # pushes speed/z/y/x. I_create/I_moveTo in ScummVM read
                # (ptr,) shape/x first from args+0 = top of stack.
                arg_bytes = self._push_intrinsic_args(call.args, intrinsic)
                # Push this (4-byte item pointer)
                if call.obj:
                    self._gen_item_ptr(call.obj)
                else:
                    self.emitter.emit_push_dword_bp(0x06)
                total_args = arg_bytes + 4  # args + this
                self.emitter.emit_calli(total_args, intrinsic.id)
                self._free_intrinsic_arg_temps(total_args)
                self.emitter.emit_add_sp(256 - total_args)
                self._spawn_tail(legacy)
                return
            target = self._usecode_method(call.method, len(call.args), call)
            if target:
                self._emit_usecode_method(target, call.args, call.obj, False,
                                          mode)
                return
            self._warn(call, f"unknown method '{call.method}' in spawn "
                       "— no call bytecode emitted")
            return

        if isinstance(call, FunctionCall):
            # spawn funcName(args) -> return
            # Resolution happens BEFORE any pushes: a waiting branch leads
            # with push pid (paired with its trailing implies), and
            # emitting that pid for a call that then fails to resolve would
            # orphan a word on the stack. Args push right-to-left — see the
            # MethodCall branch above.
            arg_bytes = len(call.args) * 2

            def _push_pid_and_args():
                self._spawn_pid(legacy)
                for arg in reversed(call.args):
                    self._gen_expression(arg)

            # Check if it's an intrinsic
            same, intrinsic = self._lookup_call(call)
            if intrinsic:
                self._spawn_pid(legacy)
                pushed = self._push_intrinsic_args(call.args, intrinsic)
                if intrinsic.class_name and intrinsic.class_name not in ('Kernel', 'Camera'):
                    # Method intrinsic — push this (skip static Kernel/Camera intrinsics)
                    self.emitter.emit_push_dword_bp(0x06)
                    total_args = pushed + 4
                else:
                    total_args = pushed
                self.emitter.emit_calli(total_args, intrinsic.id)
                self._free_intrinsic_arg_temps(total_args)
                self.emitter.emit_add_sp(256 - total_args)
                self._spawn_tail(legacy)
                return

            # Same-class routine/process, or a routine/process exposed by
            # a provider this file `uses` (uses-imports work) — e.g.
            # `spawn safePlaySFX(sfx,100) -> return;` (FREE, cross-class)
            # or LORDBRIT's `spawn puppet(lb) -> return;` (same class).
            # Tried before the class-instantiation fallback below, which
            # is for a DIFFERENT spawn form (`spawn TypeXXX() -> return`,
            # spawning a new object instance's use() handler) that this
            # must not disturb.
            resolved = (None if call.scope
                        else self._resolve_function(call.name, len(call.args)))
            if resolved:
                classid, offset, _return_kind = resolved
                self._emit_function_spawn(call, classid, offset, mode)
                return
            # A bare METHOD process on our own `this` (_usecode_method).
            target = (None if call.scope else
                      self._usecode_method(call.name, len(call.args), call))
            if target:
                self._emit_usecode_method(target, call.args, None, False,
                                          mode)
                return

            # Non-intrinsic function — resolve to class:offset via symbol table
            classid = self.symbols.get_class_id(call.name)
            if classid is not None:
                # Spawn into the class's default event (use = event 1,
                # offset 0x80). `this` here is OUR this (the spawned use()
                # runs on the same item — e.g. EggLBScene::hatch() spawning
                # TypeLordBritish() hands the scene the egg as its item),
                # consumed by spawn's unconditional pop4.
                _push_pid_and_args()
                self.emitter.emit_push_dword_bp(0x06)  # push this
                self.emitter.emit_spawn(arg_bytes, 0x04, classid, 0x0080)
                if arg_bytes:
                    self.emitter.emit_add_sp((256 - arg_bytes) & 0xFF)
                self._spawn_tail(legacy)
                return
            else:
                self._warn(call, f"unknown function '{call.name}' in spawn "
                           "— no call bytecode emitted")

    def _emit_function_spawn(self, call, classid, offset, mode):
        """Spawn a resolved same-class/`uses` function as a new process;
        `mode` as _spawn_tail.

        Only 'wait' (a plain call of a process) makes the CALLER wait:
        push_pid pairs with the trailing push_retval/implies/suspend, and
        implies and suspend together block this process until the spawned
        one returns. uc_machine.cpp case 0x57 already runs a freshly
        spawned process once immediately and resumes the caller on its
        own, so `spawn f() -> return;` ('discard', retail ARAMINA 0x40D
        021F) only drops the new pid, and bare `spawn puppet(lb);`
        ('detach', found 2026-09-30, LORDBRIT finding 1) does nothing
        after the spawn: a looping puppet whose exit condition the caller
        itself sets must not be waited on, or the caller deadlocks.
        """
        arg_bytes = len(call.args) * 2
        self._spawn_pid(mode)
        for arg in reversed(call.args):
            self._gen_expression(arg)
        # The spawn opcode (0x57) unconditionally pop4's a this pointer
        # even when this_size is 0 (uc_machine.cpp: "only remove the this
        # pointer from stack"), so a null dword MUST sit on top — that's the
        # `push dword 0` in the retail wait pattern this whole sequence
        # mirrors (59 / args / 0C 00000000 / 57 / 6E / 5E / 54 / 12 / 53).
        # Omitting it made spawn eat the args plus 2 stray bytes, and the
        # missing leading push pid left implies popping garbage pids — the
        # in-game "Process caused an error at 05A3:0277, killing process"
        # failure on spawn puppet(lb).
        this_size = 0x00
        if self._is_same_class_method(classid, call):
            # A method: pass our `this` (see _methods), as retail does
            # (PLAQUENS 00B5: `push dword [BP+06h]; spawn 00h 02h`). A
            # caller with no `this` passes a null one.
            self._push_this_or_null()
            this_size = 0x02
        else:
            self.emitter.emit_push_dword(0)
        if isinstance(offset, str):
            # Forward same-class reference (target defined LATER in this
            # file, e.g. LORDBRIT's puppet()) — offset isn't known yet,
            # patched via label by resolve_fixups().
            self.emitter.emit_spawn_label(arg_bytes, this_size, classid, offset)
        else:
            self.emitter.emit_spawn(arg_bytes, this_size, classid, offset)
        if arg_bytes:
            self.emitter.emit_add_sp((256 - arg_bytes) & 0xFF)
        self._spawn_tail(mode)

    def _gen_postfix(self, stmt):
        """Generate postfix ++ or --.

        sub (0x1C) is first-pushed minus second-pushed (uc_machine.cpp),
        so `x--` pushes x FIRST: retail FREE 0x581 give() 2019-201E
        (`quan--`) is `push [BP+0Eh]; push byte 1; sub; pop [BP+0Eh]`.
        Until 2026-10-07 we pushed 1 first, compiling `x--` as x = 1 - x,
        so `while n { n--; }` never ended unless n was 1. `x++` keeps
        retail's 1-first order (FREE 0x581 countStrList 29C4: push byte 1;
        push [BP-04h]; add).
        """
        if isinstance(stmt.operand, Identifier):
            bp_off = self._get_local(stmt.operand.name)
            if bp_off is not None:
                if stmt.op == '++':
                    self.emitter.emit_push_byte(1)
                    self.emitter.emit_push_bp(bp_off)
                    self.emitter.emit_op(0x14)  # add
                else:
                    self.emitter.emit_push_bp(bp_off)
                    self.emitter.emit_push_byte(1)
                    self.emitter.emit_op(0x1C)  # sub
                self.emitter.emit_pop_bp(bp_off)
            else:
                self._warn(stmt.operand, f"postfix '{stmt.op}' on unknown "
                           f"identifier '{stmt.operand.name}' — no bytecode emitted")

    @staticmethod
    def _intrinsic_arg_tokens(intrinsic):
        """Declared arg type tokens from the signature, left to right."""
        import re as _re
        m = _re.search(r'\(([^)]*)\)', intrinsic.signature)
        if not m or not m.group(1).strip():
            return []
        return [t.strip().split()[0] for t in m.group(1).split(',')]

    def _push_intrinsic_args(self, args, intrinsic=None):
        """Push intrinsic-call arguments right-to-left; return total bytes.

        WorldPoint locals are passed BY POINTER — `push addr` (0x4B), 4
        bytes — because the engine reads them with ARG_UC_PTR and (for out
        params like Item::I_getPoint) writes back through assignPointer.
        The old path pushed the buffer's first WORD as a value: the callee
        then read 2 bytes of coordinate + 2 bytes of neighboring stack as
        its "pointer", so every getPoint wrote nowhere and the reforged
        shield of SHADES.UNK vanished at (-60,-30,0). Found 2026-07-28 by
        comparing our calli byte counts against the engine's ARG_ macros
        (ours said B=6 where I_getPoint reads 8).

        Everything else keeps the existing 2-bytes-per-arg convention.
        """
        total = 0
        self._pending_string_frees = 0
        self._pending_slist_frees = []
        tokens = (self._intrinsic_arg_tokens(intrinsic)
                  if intrinsic is not None else [])
        if intrinsic is not None and len(args) > intrinsic.arg_count:
            # 1994 source sometimes passes more arguments than the
            # intrinsic declares — playSFX(sfx, volume) against
            # playSFX(word) is 22 sites. Retail bytecode shows the 1994
            # compiler DROPPED the extras (every retail playSFX is B=2),
            # so do the same, keeping the leading args the engine reads.
            self._warn(args[intrinsic.arg_count],
                       f"intrinsic '{intrinsic.name}' takes "
                       f"{intrinsic.arg_count} arg(s), call passes "
                       f"{len(args)} — extras dropped (retail convention)")
            args = args[:intrinsic.arg_count]
        for i in range(len(args) - 1, -1, -1):
            arg = args[i]
            tok = tokens[i] if i < len(tokens) else None
            if intrinsic is not None and self._intrinsic_param_is_slist(
                    intrinsic, i):
                # A String List argument is pushed as a COPY (push slist,
                # 0x43) that the caller frees after the calli: retail FREE
                # 0x581 1AF3-1AFB `push slist [BP-04h]; push addr; calli
                # 06h 004Ah; free slist [SP+04h]`, the form the AskExpr
                # path already emits.
                self._gen_expression(arg)
                total += 2
                self._pending_slist_frees.append(total)
                continue
            if (isinstance(arg, Identifier)
                    and arg.name in self._worldpoint_locals):
                bp_off = self._get_local(arg.name)
                self.emitter.emit_push_addr_bp(bp_off)
                total += 4
            elif tok == 'char*':
                # String argument by POINTER: emit the string, then
                # `str to ptr` (0x6B) — 4 bytes on the stack, retail's
                # Book::read idiom. The old path pushed the 2-byte string
                # id: the engine read id+garbage as a pointer, so all 70
                # plaque texts (TYPENSGOLDPLAQUE) dereferenced junk. The
                # string must be freed AFTER the calli — callers emit
                # emit_free_string_sp(4) per pending free (works for the
                # corpus shape: one string arg pushed last-but-receiver).
                self._gen_expression(arg)
                self.emitter.emit_str_to_ptr()
                self._pending_string_frees += 1
                total += 4
            elif tok in ('long', 'ulong') and isinstance(arg, NumberLit):
                self.emitter.emit_push_dword(arg.value & 0xFFFFFFFF)
                total += 4
            else:
                if tok in ('long', 'ulong'):
                    self._warn(arg, f"long-typed intrinsic arg pushed as "
                               f"2-byte value — engine reads 2 garbage "
                               f"bytes ('{intrinsic.name}')")
                self._gen_expression(arg)
                total += 2
        return total

    @staticmethod
    def _intrinsic_param_is_slist(intrinsic, index):
        """Whether the intrinsic's declared parameter `index` is named
        `slist` (`strptr process Item::ask(uword slist)`)."""
        import re as _re
        m = _re.search(r'\(([^)]*)\)', intrinsic.signature)
        params = m.group(1).split(',') if m and m.group(1).strip() else []
        return index < len(params) and params[index].split()[-1] == 'slist'

    def _free_intrinsic_arg_temps(self, arg_bytes):
        """After a calli, free the temporaries _push_intrinsic_args left
        under the call's `arg_bytes` (args + receiver): one `free string
        [SP+04h]` per char* arg, then one `free slist [SP+n]` per String
        List copy, n being the bytes pushed above it."""
        for _ in range(self._pending_string_frees):
            self.emitter.emit_free_string_sp(0x04)
        for pushed in self._pending_slist_frees:
            self.emitter.emit_free_slist_sp(arg_bytes - pushed)
        self._pending_string_frees = 0
        self._pending_slist_frees = []

    def _convo_routine(self, name):
        """_emit_usecode_method target for retail METHOD enterConvo/
        exitConvo (u8c_symbols METHOD_ROUTINES)."""
        offset, _kind, has_this, params, ret = \
            self.symbols.get_method_routine(name)
        return METHOD_CLASS_ID, offset, ret, has_this, params

    def _gen_exit_convo(self, target):
        """exitConvo() / npc.exitConvo(): spawn retail METHOD
        Npc::exitConvo (0x57C 1090) on the NPC and wait, byte for byte as
        all 256 retail sites do, and nothing more.

        Retail exitConvo restarts the NPC itself: 109A calls
        Item::enterFastArea() (intrinsic 0x67) on it, which in U8.EXE
        (10d8:2577) fires the NPC's own enterFastArea event even though
        a talked-to NPC is already in the fast area (route, loiter, bark,
        or nothing in a scene). ScummVM's intrinsic skipped it for such an
        NPC until the fork's `Item::I_enterFastArea` fix (2026-10-09), so
        from 7cc1051 to then we spawned the class's own handler after the
        exitConvo spawn; with the fixed intrinsic that started a second
        activity, and the invisible-Avatar abort (METHOD 0D7C-0DB8, which
        ends the conversation before our spawn) still left the NPC frozen
        (docs/playtest-2026-10-09-convo.md finding 1).

        No cSetActivity(0) follows either. Retail's compiler adds nothing
        after exitConvo: in the three retail NPC classes with no
        enterFastArea handler (THURGIST 0x10D, PESANT1 0x2C3, CHILD 0x2C4)
        all 19 exitConvo sites are followed by a cSetActivity their SOURCE
        wrote, as ZCHILD's 1994 source writes one after each of its own
        (`exitConvo(); cSetActivity(ACT_LOITER);`), and the scene classes
        (SORCERER 0x575, DAEMSCEN 0x58A, SORCHAT 0x4B5, BERENHCH 0x4A7)
        have none. Adding one stacked a second LoiterProcess on ZCHILD's
        (setActivityU8(0) adds one without killing the last) and on the
        one Mythran's 0x421 handler starts after MYTHRDLG's exitConvo.
        """
        self._emit_usecode_method(self._convo_routine('exitConvo'),
                                  [], target, False, 'wait')

    def _wait_for_process(self, as_value):
        """Block on the process an intrinsic just started; push its result
        when the call is a value.

        A `process` intrinsic returns the new process's pid, not its
        answer, and retail always waits on that pid: the call is `push pid`
        (before the args) ... `calli; add sp; push retval; implies 01 01;
        pop temp; suspend`, plus `push process result; long to int` as a
        value — ARAMINA 0x40D 04C4-04D8 (`if pathfind(pathEgg.referent,
        20)`), and all 31 retail pathfind and 44 target() value sites.
        Testing the pid made Aramina launch a pathfinder per matching egg
        per lap (playtest 2026-10-03 finding 1).

        A STATEMENT waits the same way, minus the result: ARAMINA 0x40D
        0C1F `pathfind(...)`, FREE 0x581 1C74 `Camera::scrollTo(...)`.
        Retail has no process-intrinsic call that neither waits nor
        discards its pid (`5E 12`, the `spawn x -> return` form), and the
        statement sites wait for every process intrinsic the corpus uses:
        doAnim 48/48, the 239 Book/Scroll/Grave/Plaque::read sites, the
        fades and LightningBolt (111 of 116), teleportToEgg 9/9, pathfind
        31/31, and cSetActivity 34 of 35. cSetActivity is safe to wait on:
        for activity 0 it returns a 1-tick DelayProcess, not the endless
        LoiterProcess it also starts (actor.cpp setActivityU8), and 0 (no
        wait, `implies` just warns) for activity 1. We waited only for
        values until 2026-10-07, so a scene ran on while its fade, anim or
        pathfind was still playing. The caller emits the leading `push
        pid`.
        """
        self.emitter.emit_push_retval()
        self.emitter.emit_implies()
        self.emitter.emit_pop_temp()
        self.emitter.emit_suspend()
        if as_value:
            self.emitter.emit_op(0x6D)  # push process result
            self.emitter.emit_op(0x61)  # long to int

    def _gen_method_call(self, call, as_value=False):
        """Generate a method call on an object.

        Returns 'process' when `as_value` and the call was a process
        (intrinsic or usecode): its awaited result is already on the
        stack, so the caller must not `push retval` again; a routine's
        return kind ('word'/'byte'/'none') for a usecode routine call;
        otherwise None.
        """
        # bark() needs full suspension pattern — route to _gen_bark
        if call.method == 'bark' and call.args:
            bark_stmt = BarkStmt(target=call.obj, text=call.args[0])
            self._gen_bark(bark_stmt)
            return

        # arg_count resolves overloaded intrinsic names by arity (see
        # find_intrinsic): RAGNAR/HRODNY's `key.pop(bag.referent)` must
        # emit Item::pop(uword)/0x37 popToContainer, not 0x36 popToCoords.
        intrinsic = self.symbols.find_intrinsic(call.method,
                                                arg_count=len(call.args))
        if intrinsic:
            wait = intrinsic.is_process
            if wait:
                self.emitter.emit_push_pid()
            # Push args right-to-left (see _gen_spawn's MethodCall branch
            # for the retail-bytecode proof), then the itemptr on top.
            pushed = self._push_intrinsic_args(call.args, intrinsic)
            # Push this (4-byte item pointer)
            if call.obj:
                self._gen_item_ptr(call.obj)
            else:
                self.emitter.emit_push_dword_bp(0x06)  # push this
            arg_bytes = pushed + 4  # args + this ptr
            self.emitter.emit_calli(arg_bytes, intrinsic.id)
            self._free_intrinsic_arg_temps(arg_bytes)
            self.emitter.emit_add_sp(256 - arg_bytes)  # negative adjust
            if wait:
                self._wait_for_process(as_value)
                return 'process'
            return None
        target = self._usecode_method(call.method, len(call.args), call)
        if target:
            return self._emit_usecode_method(target, call.args, call.obj,
                                             as_value, 'wait')
        self._warn(call, f"unknown method '{call.method}' "
                   "— call compiled as no-op (0 bytes emitted)")
        return 'unresolved'

    def _usecode_method(self, name, arity, node=None):
        """A usecode method a `x.name(...)` / bare `name(...)` call can
        reach when no intrinsic matched: this class's own non-event
        `Class::method` (FREE's `timer.isDone()`, retail FREE 0x581 1C2C
        `push addr [BP-08h]; call 0581h 1BF1h`), else a retail METHOD
        (0x57C) routine (u8c_symbols.METHOD_ROUTINES). Returns
        (classid, offset, kind, has_this, param kinds) or None; a METHOD
        name called with the wrong arity is warned about and not called.
        """
        same = self._resolve_same_class(name, arity)
        if same and (name.lower(), arity) in getattr(self, '_methods', ()):
            classid, offset, kind = same
            return classid, offset, kind, True, ('word',) * arity
        entry = self.symbols.get_method_routine(name)
        if entry is None:
            return None
        offset, _routine, has_this, params, kind = entry
        if len(params) != arity:
            self._warn(node, f"METHOD {name} takes {len(params)} arg(s), "
                       f"call passes {arity} — not called")
            return None
        return METHOD_CLASS_ID, offset, kind, has_this, params

    def _emit_usecode_method(self, target, args, obj, as_value, mode):
        """Call or spawn a usecode method on `obj` (None: our own `this`).

        A routine is `call`ed with its args (right to left) and the
        receiver pointer on top, all popped after: retail TypePotion 0x2FE
        06C6 `Avatar.toggleStatus(OWNED)` = push byte 4; push addr; call
        057Ch 0113h; add sp. A process is spawned with this_size 2 and
        treated per `mode` (_spawn_tail): 'wait' for every retail statement
        or value call of a process (_classify_return_kind): FREE 0x581 376F
        `Malchir.realDoAnim(..)` = push pid; args; this; spawn 04h 02h
        057Ch 15E7h; add sp; push retval; implies; pop temp; suspend.
        Param kinds: a String is passed as a pointer (str to ptr) and freed
        after the spawn (retail 0x6D 1D7D timedBark: spawn; free string
        [SP+02h]); a WorldPoint by value, `push huge [BP+xx] 05` (retail
        0x402 024B safeTeleport). The receiver is the usual item pointer
        (_gen_item_ptr): retail puts an NPC/Avatar objid in a stack temp
        and pushes its address, a SEG_OBJ pointer reads back the same
        objid (uc_machine.cpp dereferencePointer).
        """
        classid, offset, kind, has_this, params = target
        for arg, pk in zip(args, params):
            if pk == 'worldpoint' and not (
                    isinstance(arg, Identifier)
                    and arg.name in self._worldpoint_locals):
                self._warn(arg, "WorldPoint argument is not a WorldPoint "
                           "local — call compiled as no-op")
                return 'unresolved'
        is_proc = kind == 'process'
        if is_proc:
            self._spawn_pid(mode)
        sizes = []  # push order
        for arg, pk in reversed(list(zip(args, params))):
            if pk == 'worldpoint':
                self.emitter.emit_op(0x45)  # push huge [BP+xx] 05
                self.emitter.emit_byte(self._get_local(arg.name) & 0xFF)
                self.emitter.emit_byte(0x05)
                sizes.append((pk, 5))
            elif pk == 'string':
                self._gen_expression(arg)
                self.emitter.emit_str_to_ptr()
                sizes.append((pk, 4))
            else:
                self._gen_expression(arg)
                sizes.append((pk, 2))
        arg_bytes = sum(n for _, n in sizes)
        if has_this:
            if obj is None:
                self._push_this_or_null()
            else:
                self._gen_item_ptr(obj)
        elif is_proc:
            self.emitter.emit_push_dword(0)
        if is_proc:
            this_size = 0x02 if has_this else 0x00
            if isinstance(offset, str):
                self.emitter.emit_spawn_label(arg_bytes, this_size, classid,
                                              offset)
            else:
                self.emitter.emit_spawn(arg_bytes, this_size, classid, offset)
        elif isinstance(offset, str):
            self.emitter.emit_call_label(classid, offset)
        else:
            self.emitter.emit_call(classid, offset)
        for k, (pk, _n) in enumerate(sizes):
            if pk == 'string':
                above = sum(n for _, n in sizes[k + 1:])
                if not is_proc and has_this:
                    above += 4
                self.emitter.emit_free_string_sp(above)
        self.emitter.emit_add_sp((256 - arg_bytes
                                  - (4 if has_this and not is_proc else 0))
                                 & 0xFF)
        if not is_proc:
            return kind
        self._spawn_tail(mode)
        if mode == 'wait' and as_value:
            self.emitter.emit_op(0x6D)  # push process result
            self.emitter.emit_op(0x61)  # long to int
            return 'process'
        return None

    def _lookup_call(self, call):
        """Resolve a FunctionCall's target: (same_class, intrinsic).

        A bare name prefers this class's own function, then the `uses`
        choice among overloaded intrinsics, then the intrinsic table by
        arity, then by name. A scoped `Camera::getX()` (call.scope) names
        an intrinsic of that class and nothing else: FREE.UNK's own
        `process scrollTo` body calls `Camera::scrollTo(...)`, which must
        bind intrinsic 0xB5 (retail FREE 0x581 1C7D `calli 08h 00B5h`),
        not recurse into itself.
        """
        if call.scope:
            intrinsic = self.symbols.find_intrinsic(
                call.name, class_name=call.scope, arg_count=len(call.args))
            if intrinsic is None or (intrinsic.class_name or '').lower() \
                    != call.scope.lower():
                self._warn(call, f"no intrinsic {call.scope}::{call.name} — "
                           "call compiled as no-op (0 bytes emitted)")
                return None, None
            return None, intrinsic
        same = self._resolve_same_class(call.name, len(call.args))
        if same:
            return same, None
        intrinsic = self._intrinsic_from_uses(call.name, len(call.args))
        if intrinsic is None:
            intrinsic = self.symbols.find_intrinsic(
                call.name, arg_count=len(call.args))
        if intrinsic is None:
            intrinsic = self.symbols.find_intrinsic(call.name)
        return None, intrinsic

    def _gen_own_event_call(self, call, as_value):
        """A bare zero-argument call of an event this class handles, made
        where there is a `this`: spawn our own handler on `this` and wait,
        as retail compiles all 17 of its bare `enterFastArea();` calls in a
        class with that handler (ARAMINA 0x40D 0379 `push pid; push dword
        [BP+06h]; spawn 00h 02h 040Dh 01D6h; push retval; implies; pop
        temp; suspend`), where we called intrinsic 0x67 on `this`. Retail
        calls 0x67 only on another item or in a class without the
        handler (METHOD 0x57C, DAEMSCEN 0x58A, DARION's `5.` NPC).
        Returns True when it emitted the call."""
        if call.scope or call.args or not self._func_has_this:
            return False
        event_id = self.symbols.get_event_id(call.name)
        if event_id not in getattr(self, '_class_events', ()):
            return False
        self.emitter.emit_push_pid()
        self.emitter.emit_push_dword_bp(0x06)
        self.emitter.emit_spawn_label(0x00, 0x02, self._classid,
                                      self.emitter.event_label(event_id))
        self._spawn_tail('wait')
        if as_value:
            self.emitter.emit_op(0x6D)  # push process result
            self.emitter.emit_op(0x61)  # long to int
        return True

    def _gen_function_call(self, call, as_value=False):
        """Generate a function call.

        Returns the resolved return-kind ('word'/'byte') for a same-class
        or `uses`-provider routine this method itself resolved (uses-imports
        work), so expression-context callers can push the right retval
        variant; 'process' when `as_value` and the call was a process
        intrinsic or a process function, whose awaited result is already
        pushed (see _wait_for_process). Returns None for other
        intrinsics and unresolved calls.
        """
        if self._gen_own_event_call(call, as_value):
            return 'process'
        # A function THIS class defines wins over an intrinsic of the same
        # name (see _resolve_same_class — FREE's `combine`).
        same, intrinsic = self._lookup_call(call)
        if intrinsic:
            wait = intrinsic.is_process
            if wait:
                self.emitter.emit_push_pid()
            # Right-to-left, per the U8 calling convention (retail proof in
            # _gen_spawn's MethodCall branch). This is what puts scrollTo's
            # speed at the bottom and x on top where I_scrollTo reads it.
            arg_bytes = self._push_intrinsic_args(call.args, intrinsic)
            if intrinsic.class_name and intrinsic.class_name not in ('Kernel', 'Camera'):
                # Method intrinsic called as bare function — push this
                # Skip for Kernel/Camera intrinsics which are static, not methods
                self.emitter.emit_push_dword_bp(0x06)
                arg_bytes += 4
            self.emitter.emit_calli(arg_bytes, intrinsic.id)
            self._free_intrinsic_arg_temps(arg_bytes)
            self.emitter.emit_add_sp(256 - arg_bytes)
            if wait:
                self._wait_for_process(as_value)
                return 'process'
            return None

        resolved = (None if call.scope
                    else self._resolve_function(call.name, len(call.args)))
        if resolved:
            classid, offset, return_kind = resolved
            if return_kind == 'process':
                # A process is spawned and waited on, never `call`ed (see
                # _classify_return_kind): retail FREE 0x581 scrollBack
                # 1CB9-1CD8 runs `scrollTo(x,y,z+20,vel);` as push pid;
                # args; push dword 0; spawn; add sp; push retval; implies;
                # pop temp; suspend, and PENT 0x7C 11FE-1212 reads `if
                # askYesNo()` back with push process result; long to int.
                # A `call` ran the process body inside the caller, so its
                # `pop result` landed in the caller's own result register
                # and the caller read the stale temp register instead.
                self._emit_function_spawn(call, classid, offset, 'wait')
                if as_value:
                    self.emitter.emit_op(0x6D)  # push process result
                    self.emitter.emit_op(0x61)  # long to int
                return 'process'
            # Right-to-left: the callee reads its first declared param at
            # BP+06, which is the LAST word pushed before the call frame —
            # matches retail (MYTHRAN→FREE give(r,t,f,qual,quan) call
            # sites) and _generate_function's bare-function param layout.
            for arg in reversed(call.args):
                self._gen_expression(arg)
            arg_bytes = len(call.args) * 2
            if self._is_same_class_method(classid, call):
                # A method frame: `this` above the args (retail 057C 169A),
                # popped with them.
                self._push_this_or_null()
                arg_bytes += 4
            if isinstance(offset, str):
                # Forward same-class reference — see _gen_spawn's
                # matching branch / emit_call_label's docstring.
                self.emitter.emit_call_label(classid, offset)
            else:
                self.emitter.emit_call(classid, offset)
            if arg_bytes:
                self.emitter.emit_add_sp((256 - arg_bytes) & 0xFF)
            return return_kind

        # A bare METHOD name inside an NPC/item class runs on our own
        # `this`: retail ARAMINA 0x40D 0331 `turnToFace(..)` = args; push
        # dword [BP+06h]; spawn 06h 02h 057Ch 091Ch.
        target = (None if call.scope
                  else self._usecode_method(call.name, len(call.args), call))
        if target:
            return self._emit_usecode_method(target, call.args, None,
                                             as_value, 'wait')

        self._warn(call, f"unknown function '{call.name}' "
                   "— call compiled as no-op (0 bytes emitted)")
        return 'unresolved'

    def _gen_item_ptr(self, expr):
        """Push an expression as a 4-byte UC item pointer.

        Bark and other intrinsics expect ARG_ITEM_FROM_PTR (4 bytes).
        For well-known objects like Avatar (objid 1), emit a dword
        with the U8 pointer format: (SEG_OBJ << 16) | objid.

        Local Item variables (and bare-function Item params) are 2-byte
        objid SLOTS, so the itemptr is `push addr [BP+xx]` (0x4B) — a
        BP-relative pointer to the slot. That is the retail convention
        (STRATOS create/pop both emit 4B), and it is load-bearing:
        Item::I_create WRITES the new objid back through this pointer
        (UCMachine::assignPointer), and every reader dereferences it via
        ptrToObject. Pushing the slot's VALUE as a dword (the old 0x40
        emission) hands the engine 2 bytes of objid + 2 bytes of
        neighboring stack as a "pointer" — create's write-back lands
        nowhere and all later method calls on the local no-op on garbage.
        `this` (no explicit receiver) stays push dword [BP+06]: there the
        caller passed a real 4-byte pointer value.
        """
        SEG_OBJ = 0x8002
        if isinstance(expr, Identifier):
            if expr.name == 'Avatar':
                self.emitter.emit_push_dword((SEG_OBJ << 16) | 1)
                return
            bp_off = self._get_local(expr.name)
            if bp_off is not None:
                self.emitter.emit_push_addr_bp(bp_off)
                return
            # NPC class name → UC object pointer (SEG_OBJ << 16 | npcnum),
            # inside the NPC window only (see NPC_CLASS_FIRST).
            npc_num = npc_num_of_class(self.symbols.get_class_id(expr.name))
            if npc_num is not None:
                self.emitter.emit_push_dword((SEG_OBJ << 16) | npc_num)
                return
        # Fallback: evaluate expression (2 bytes) and widen to pointer
        self._gen_expression(expr)
        # Convert 16-bit objid to 32-bit UC pointer by pushing SEG_OBJ
        # and combining: push word SEG_OBJ, then the VM needs manual widening.
        # For safety, just push as dword constant if it's a number literal.
        if isinstance(expr, NumberLit):
            # Already pushed 2 bytes, but we need 4. This is a codegen
            # limitation — for now, well-known objects cover all LV cases.
            pass

    # ─── Expression generation ─────────────────────────────────────────────

    def _is_string_expr(self, expr):
        """True for a string-valued operand of `+`: a literal, a String
        local, or a `+` chain that contains one (`"a" + getName() + "b"`
        is `("a" + getName()) + "b"`)."""
        if isinstance(expr, StringLit):
            return True
        if isinstance(expr, Identifier):
            return expr.name in self._string_locals
        if isinstance(expr, BinaryOp) and expr.op == '+':
            return (self._is_string_expr(expr.left)
                    or self._is_string_expr(expr.right))
        return False

    def _gen_expression(self, expr):
        """Generate code to push an expression's value onto the stack."""
        if isinstance(expr, NumberLit):
            if -128 <= expr.value <= 127:
                self.emitter.emit_push_byte(expr.value)
            elif 0 <= expr.value <= 0xFFFF:
                self.emitter.emit_push_word(expr.value)
            else:
                self.emitter.emit_push_dword(expr.value)

        elif isinstance(expr, StringLit):
            self.emitter.emit_string(expr.value)

        elif isinstance(expr, BoolLit):
            self.emitter.emit_push_byte(1 if expr.value else 0)

        elif isinstance(expr, Identifier):
            name = expr.name
            # Check local variable
            bp_off = self._get_local(name)
            if bp_off is not None:
                if name in self._slist_locals:
                    self.emitter.emit_push_slist(bp_off)
                elif name in self._string_locals:
                    self.emitter.emit_push_string_bp(bp_off)
                else:
                    self.emitter.emit_push_bp(bp_off)
                return
            # Check global flag
            flag = self.symbols.get_global_flag(name)
            if flag:
                bit_offset, bits = flag
                self.emitter.emit_push_global(bit_offset, bits)
                return
            # Check type-to-shape mapping (TypeXXX → shape ID)
            shape = self.symbols.get_type_shape(name)
            if shape is not None:
                self.emitter.emit_push_word(shape)
                return
            # Check snddefs SFX constants (LTNING1A, QUAKE3, ... — the 1994
            # sound header recovered from SOUND.FLX entry 0, 2026-07-04).
            # Exact all-caps match only, so locals can never collide.
            # Check EQ_* equip-slot constants (EQ_SHIELD, EQ_BACKPACK, ...).
            # Must precede nothing in particular — the names can't collide
            # with SND_CONSTANTS or TYPE_SHAPES — but note EQ_SHIELD is 0,
            # so before this hook existed the whole family fell through to
            # the `push 0` fallback and aliased onto the shield slot.
            eq = self.symbols.get_eq_constant(name)
            if eq is not None:
                self.emitter.emit_push_byte(eq)
                return
            snd = self.symbols.get_snd_constant(name)
            if snd is not None:
                if snd <= 127:
                    self.emitter.emit_push_byte(snd)
                else:
                    self.emitter.emit_push_word(snd)
                return
            # Map-number constants (Fix 2a, 2026-07-27). Values pinned
            # against retail bytecode — see MAP_CONSTANTS in u8c_symbols.
            # push byte keeps this the same size as the old push-0
            # fallback, so the fix is size-neutral in every class.
            # Before this hook, every Map* name compiled to push 0: the
            # LB vision lost its on-Docks suppression and SHADES.UNK:682
            # teleported Atli to map 0 instead of the vale.
            mapno = self.symbols.get_map_constant(name)
            if mapno is not None:
                self.emitter.emit_push_byte(mapno)
                return
            # Process-type constants (2026-08-12). Retail pushes these as
            # words (push 0205h etc. before every resetRef), so emit the
            # same. Before this hook, resetRef(referent, PT_BARK) compiled
            # its type to push 0 — and killProcesses(objid, 0, ...) matches
            # nothing, so all 28 corpus resetRef sites were silent no-ops
            # (the `I_resetRef item=106 type=0x0000` lines in playtest
            # logs). See PT_CONSTANTS in u8c_symbols for the evidence.
            # Shape-family constants (2026-09-02). getFamily() returns the
            # ShapeInfo::SF_* number and retail compares against byte
            # literals, so emit push byte. Before this hook every *_FAMILY
            # name compiled to push 0, which made FREE::give's first guard
            # `getFamily() != 0` — true for every container — so give() and
            # take() returned at their first instruction and three quest
            # hand-overs silently delivered nothing. See FAMILY_CONSTANTS
            # in u8c_symbols for the disassembly evidence.
            fam = self.symbols.get_family_constant(name)
            if fam is not None:
                self.emitter.emit_push_byte(fam)
                return
            pt = self.symbols.get_pt_constant(name)
            if pt is not None:
                self.emitter.emit_push_word(pt)
                return
            # Day-period constants (2026-08-12). Retail compares
            # FREE::getPeriod against byte literals 0-5; emit push byte to
            # match. Before this, `if (getPeriod() = daytide)` was always
            # comparing against 0 = bloodwatch, so both of Atli::schedule's
            # period branches missed and his destination stayed (0,0,0).
            # See DAY_PERIOD_CONSTANTS in u8c_symbols for the evidence.
            period = self.symbols.get_period_constant(name)
            if period is not None:
                self.emitter.emit_push_byte(period)
                return
            # Schedule constants (at_home, on_throne, chow_down...).
            # Retail pushes byte literals (CYRRUS 0x416 enterFastArea
            # `4E B6 01 02 0A 01`); see SCHEDULE_CONSTANTS in u8c_symbols.
            sched = self.symbols.get_schedule_constant(name)
            if sched is not None:
                self.emitter.emit_push_byte(sched)
                return
            # DMG_* damage-type constants. Retail pushes a WORD (MORDEA
            # 0x407 @2736 `0B 80 00` for DMG_FULL); see u8c_symbols.
            dmg = self.symbols.get_dmg_constant(name)
            if dmg is not None:
                self.emitter.emit_push_word(dmg)
                return
            # Status flags (OWNED, INVISIBLE, CONTAINER_GUMP_OPEN). Retail
            # pushes byte literals before bit_and (ARAMINA 0x40D @05C1 `5E
            # 0A 10 39`, TypePotion 0x2FE @06BC `5E 0A 04 39`) and a word
            # past 0xFF (AVATAR 0x401 @0093 `5E 0B 00 01 39`); see
            # STATUS_CONSTANTS.
            st = self.symbols.get_status_constant(name)
            if st is not None:
                if st > 0xFF:
                    self.emitter.emit_push_word(st)
                else:
                    self.emitter.emit_push_byte(st)
                return
            # Animation sequences (AS_*), compass directions / RANDOM /
            # LEFT (the realDoAnim / turnToFace arguments) and the
            # single-value header constants (differentMap -1, NULL_REF,
            # ACT_LOITER). Retail pushes bytes (FREE 0x581 377D `0A 1B`
            # AS_ENTER_CAST, AVATAR 0x401 0CCB `0A 00` north, FREE 1D98
            # `0A FF` differentMap); see ANIM_CONSTANTS / DIR_CONSTANTS /
            # LITERAL_CONSTANTS.
            for lookup in (self.symbols.get_anim_constant,
                           self.symbols.get_dir_constant,
                           self.symbols.get_literal_constant):
                value = lookup(name)
                if value is not None:
                    self.emitter.emit_push_byte(value)
                    return
            # Well-known game objects
            if name == 'Avatar':
                self.emitter.emit_push_byte(1)  # Avatar is always objid 1
                return
            # Bare `referent` — the current process's own item, as a word
            # value. Matches the codegen's existing `within N cells of
            # referent` foreach convention (this same push-this-then-deref
            # pair, a few dozen lines up in _gen_foreach): push the 4-byte
            # this-pointer at [BP+06], then dereference 2 bytes to get the
            # plain item objid an intrinsic like Item::getDirToItem(uword)
            # expects (LORDBRIT.UNK:47's
            # `Avatar.getDirToItem(referent)`). Never a local variable —
            # `referent` is a reserved lexer token (TokenType.REFERENT),
            # not an IDENT, so it can never collide with a real declared
            # local's name.
            if name == 'referent':
                self.emitter.emit_push_dword_bp(0x06)
                self.emitter.emit_push_indirect(0x02)
                return
            # Check class ID (for NPC/class references used as item refs)
            classid = self.symbols.get_class_id(name)
            if classid is not None:
                npc_num = npc_num_of_class(classid)
                if npc_num is not None:
                    # NPC class name as an item reference is the NPC's
                    # object number (classid - 0x400), pushed as a byte,
                    # never the class id. Retail ARAMINA 0x40D's atHome
                    # searches around `push byte +13` (npcnum 13); we
                    # pushed 040Dh, so every `within N cells of Aramina`
                    # logged "Invalid item 1037 passed to area search!"
                    # and matched nothing. Retail CYRRUS/XAVIER/DARION/
                    # MORDEA/SALKIND/STELLOS/TORWIN agree
                    # (test_killprocess_npc_ref_cells.py). Only the NPC
                    # window qualifies (NPC_CLASS_FIRST..NPC_CLASS_LAST).
                    self.emitter.emit_push_byte(npc_num)
                    return
                self.emitter.emit_push_word(classid)
                return
            # Unknown identifier — push 0 as placeholder.  Warn: this is how
            # a typo'd or undeclared global flag becomes a silent wrong-
            # branch bug (bytecode is unchanged, diagnostics only).
            self._warn(expr, f"unknown identifier '{name}' compiled as push 0")
            self.emitter.emit_push_byte(0)

        elif isinstance(expr, BinaryOp):
            self._gen_expression(expr.left)
            self._gen_expression(expr.right)

            # Use strcmp for string comparisons (= and !=) instead of
            # integer cmp/ne which compares handles, not content.
            is_string_op = False
            if expr.op in ('=', '!='):
                is_string_op = (
                    isinstance(expr.left, StringLit) or
                    isinstance(expr.right, StringLit) or
                    (isinstance(expr.left, Identifier) and
                     expr.left.name in self._string_locals) or
                    (isinstance(expr.right, Identifier) and
                     expr.right.name in self._string_locals))

            if is_string_op:
                self.emitter.emit_op(0x26)  # strcmp (compares content, frees both)
                if expr.op == '!=':
                    self.emitter.emit_op(0x30)  # not (invert: strcmp returns 1 on match)
            elif expr.op == '+' and (self._is_string_expr(expr.left)
                                     or self._is_string_expr(expr.right)):
                # String `+` is concat (0x16), never add: retail ARAMINA
                # 0x40D 1146-115F compiles `"Yes, I am "+getName()+"."` to
                # `push string; calli getName; push retval; concat; push
                # string "."; concat`. `add` summed the two string
                # handles, so every such bark showed a wrong string.
                self.emitter.emit_concat()
            else:
                op_map = {
                    '+': 0x14,   # add
                    '&': 0x39,   # bit_and: retail ARAMINA 0x40D 05C1-05C4
                                 # `push retval; push byte 10h; bit_and`
                                 # for `Avatar.getStatus() & INVISIBLE`
                    '-': 0x1C,   # sub
                    '*': 0x1E,   # mul
                    '/': 0x20,   # div
                    'modulo': 0x22,  # mod: retail FREE 0x581 getHour 28E7-
                                 # 28EE `TimeInGameHours() modulo 24` =
                                 # calli D8; push retval; push byte 18h; mod
                    '|': 0x3A,   # bit_or: retail METHOD 0x57C boom 084E-
                                 # 0852 `DMG_FIRE|DMG_BLUNT` = push byte 8;
                                 # push byte 4; bit_or
                    '=': 0x24,   # cmp
                    '!=': 0x36,  # ne
                    '<': 0x28,   # lt
                    '>': 0x2C,   # gt
                    '<=': 0x2A,  # le
                    '>=': 0x2E,  # ge
                    'and': 0x32, # and
                    'or': 0x34,  # or
                }
                opcode = op_map.get(expr.op)
                if opcode:
                    self.emitter.emit_op(opcode)

        elif isinstance(expr, UnaryOp):
            if expr.op == 'not':
                self._gen_expression(expr.operand)
                self.emitter.emit_op(0x30)  # not
            elif expr.op == '-':
                if (isinstance(expr.operand, NumberLit)
                        and expr.operand.value <= 128):
                    # A negative literal is one sign-extended push byte:
                    # retail AVATAR 0x401 39CE/3A22/3AB2/3B15 `x = -1..-4`
                    # = `0A FF`..`0A FC`, TORWIN 0x41A 339E hurl(15,-30,..)
                    # `0A E2`, FREE 0x581 1C62 `-1 * x` = `0A FF 3F 06 1E`
                    # and getDistance's differentMap (-1) 1D98 `0A FF`.
                    # No retail literal below -128 exists to pin a word
                    # form, so those keep the general (0 - operand).
                    self.emitter.emit_push_byte(-expr.operand.value)
                    return
                # Negate: emit (0 - operand)
                self.emitter.emit_push_byte(0)
                self._gen_expression(expr.operand)
                self.emitter.emit_op(0x1C)  # sub

        elif isinstance(expr, MethodCall):
            kind = self._gen_method_call(expr, as_value=True)
            if kind == 'unresolved':
                # Nothing was called, so `push retval` would read whatever
                # the last real call left in the temp register: HRODNY's
                # `if canSafeTeleport(...)` took its branch at random.
                # A deterministic 0, like an unknown identifier.
                self.emitter.emit_push_byte(0)
            elif kind == 'byte':
                self.emitter.emit_push_byte_retval()  # FREE 1C35
            elif kind != 'process':
                self.emitter.emit_push_retval()

        elif isinstance(expr, FunctionCall):
            return_kind = self._gen_function_call(expr, as_value=True)
            # 'byte' only for a same-class/`uses`-provider call resolved
            # to a Boolean-returning routine (e.g. FREE's give(), inView(),
            # unkCloseAllGumps()) — matches the base game's `push byte
            # retval` at those call sites. 'process': a process intrinsic
            # already pushed its awaited result. 'unresolved': nothing was
            # called, push a deterministic 0 (see the MethodCall branch).
            # Every other case (intrinsics, 'word'/'none' provider returns)
            # keeps the unconditional `push retval`.
            if return_kind == 'unresolved':
                self.emitter.emit_push_byte(0)
            elif return_kind == 'byte':
                self.emitter.emit_push_byte_retval()
            elif return_kind != 'process':
                self.emitter.emit_push_retval()

        elif isinstance(expr, MemberAccess):
            # WorldPoint member read: word at +0/+2, byte at +4 (see the
            # assignment branch). Before this, `p.y` and `p.z` pushed the
            # same first word `p.x` did — the member name was ignored.
            if (isinstance(expr.obj, Identifier)
                    and expr.obj.name in self._worldpoint_locals
                    and expr.member in ('x', 'y', 'z')):
                bp_off = self._get_local(expr.obj.name)
                if expr.member == 'x':
                    self.emitter.emit_push_bp(bp_off)
                elif expr.member == 'y':
                    self.emitter.emit_push_bp((bp_off + 2) & 0xFF)
                else:
                    self.emitter.emit_push_byte_bp((bp_off + 4) & 0xFF)
                return
            # obj.member — might be referent access or property
            self._gen_expression(expr.obj)

        elif isinstance(expr, BarkStmt):
            # bark as expression
            self._gen_bark(expr)

        elif isinstance(expr, AskExpr):
            # ask(slist) — base game pattern from MYTHRAN disassembly:
            #   push pid
            #   push slist [BP-xx]
            #   push dword [BP+06]   (this)
            #   calli 06h 004Ah      (Item::ask)
            #   free slist [SP+04h]
            #   add sp -6
            #   push retval
            #   implies 01 01
            #   pop temp
            #   suspend
            #   push process result  (the player's answer string)
            self.emitter.emit_push_pid()
            self._gen_expression(expr.list_expr)
            self.emitter.emit_push_dword_bp(0x06)  # push this
            self.emitter.emit_calli(0x06, 0x004A)  # Item::ask(uword slist)
            # Free the slist COPY pushed by push_slist (opcode 0x43).
            # push_slist duplicates the list and its strings, so this frees
            # the copy, not the original variable.  Base game always emits
            # this after calli ask().
            self.emitter.emit_free_slist_sp(0x04)
            self.emitter.emit_add_sp(0xFA)  # -6
            self.emitter.emit_push_retval()
            self.emitter.emit_implies()
            self.emitter.emit_pop_temp()
            self.emitter.emit_suspend()
            self.emitter.emit_op(0x6D)  # push process result
            self.emitter.emit_op(0x61)  # long to int

        elif isinstance(expr, StringList):
            # <<"str1", "str2">>
            for elem in expr.elements:
                self._gen_expression(elem)
            # Create list
            self.emitter.emit_op(0x0E)  # create list
            self.emitter.emit_byte(0x02)  # elem size
            self.emitter.emit_byte(len(expr.elements))

        elif isinstance(expr, IndexExpr):
            # L[i] — retail FREE 0x581 take() 22E8-22EC
            # (`item = itemList[element]`): push [BP-04h] (the list handle
            # itself, not a copy), push [BP-08h] (the 1-based index),
            # `44 02 00` push element (word elements, not a string list).
            obj = expr.obj
            name = obj.name if isinstance(obj, Identifier) else None
            bp_off = self._get_local(name) if name else None
            if bp_off is None or name not in self._list_locals:
                self._warn(expr, f"index into '{name or type(obj).__name__}', "
                           "not an Item/Number List local — compiled as push 0")
                self.emitter.emit_push_byte(0)
                return
            self.emitter.emit_push_bp(bp_off)
            self._gen_expression(expr.index)
            self.emitter.emit_op(0x44)
            self.emitter.emit_byte(0x02)
            self.emitter.emit_byte(0x00)


def compile_monskul_test():
    """Compile MONSKUL.UNK as a test."""
    import os
    from u8c_parser import parse_file

    # Path resolution: relative to this file (repo root three levels up),
    # same convention as lv_manifest.py.
    repo_root = os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
    path = os.path.join(repo_root, 'shared', 'data', 'lv-usecode',
                         'LOST VALE', 'MONSKUL.UNK')
    ast = parse_file(path)

    symbols = create_symbol_table()
    codegen = CodeGenerator(symbols)
    class_data = codegen.generate_class(ast)

    print(f"Compiled MONSKUL: {len(class_data)} bytes")
    # Hex dump first 256 bytes
    for off in range(0, min(256, len(class_data)), 16):
        hexb = ' '.join(f'{class_data[i]:02X}' for i in range(off, min(off + 16, len(class_data))))
        print(f"  {off:04X}: {hexb}")

    return class_data


if __name__ == '__main__':
    compile_monskul_test()

#!/usr/bin/env python3
"""
u8_assembler.py — Assembler for Ultima 8 usecode bytecode.

Parses disassembly listings produced by u8_usecode_disasm.py and emits
binary bytecode. Designed for perfect round-trip: disassemble -> assemble
should produce byte-identical output.

The assembler works at the class level: it reads a complete disassembly
listing (including header comments and event table) and produces the
raw binary class data suitable for embedding in EUSECODE.FLX.
"""

import struct
import re
from io import BytesIO


# ─── Opcode table (mnemonic -> opcode, operand_format) ─────────────────────
# This is the reverse mapping of the disassembler's OPCODES dict.
# Some mnemonics map to multiple opcodes based on operand format.
# Format chars: b=BP_offset, p=SP_offset, v=signed_literal, B=uint8,
#               w=uint16, W=sint16_jump, d=uint32, s=string

# Opcode definitions keyed by (mnemonic, operand_format)
# We need to handle ambiguous mnemonics (e.g., "push byte" with 'v' vs 'b')
# by checking the operand types.

OPCODES_BY_MNEMONIC = {}

OPCODE_TABLE = {
    0x00: ("pop byte",      "b"),
    0x01: ("pop",           "b"),
    0x02: ("pop dword",     "b"),
    0x03: ("pop huge",      "bB"),
    0x08: ("pop result",    ""),
    0x09: ("assign elem",   "bBB"),
    0x0A: ("push byte",     "v"),
    0x0B: ("push",          "w"),
    0x0C: ("push dword",    "d"),
    0x0D: ("push string",   "s"),
    0x0E: ("create list",   "BB"),
    0x0F: ("calli",         "Bw"),
    0x11: ("call",          "ww"),
    0x12: ("pop temp",      ""),
    0x13: ("pop long temp", ""),
    0x14: ("add",           ""),
    0x15: ("add long",      ""),
    0x16: ("concat",        ""),
    0x17: ("append",        ""),
    0x19: ("union slist",   "B"),
    0x1A: ("subtract slist","B"),
    0x1B: ("subtract list", "B"),
    0x1C: ("sub",           ""),
    0x1D: ("sub long",      ""),
    0x1E: ("mul",           ""),
    0x1F: ("mul long",      ""),
    0x20: ("div",           ""),
    0x21: ("div long",      ""),
    0x22: ("mod",           ""),
    0x23: ("mod long",      ""),
    0x24: ("cmp",           ""),
    0x25: ("cmp long",      ""),
    0x26: ("strcmp",         ""),
    0x28: ("lt",            ""),
    0x29: ("lt long",       ""),
    0x2A: ("le",            ""),
    0x2B: ("le long",       ""),
    0x2C: ("gt",            ""),
    0x2D: ("gt long",       ""),
    0x2E: ("ge",            ""),
    0x2F: ("ge long",       ""),
    0x30: ("not",           ""),
    0x31: ("not long",      ""),
    0x32: ("and",           ""),
    0x33: ("and long",      ""),
    0x34: ("or",            ""),
    0x35: ("or long",       ""),
    0x36: ("ne",            ""),
    0x37: ("ne long",       ""),
    0x38: ("in list",       "BB"),
    0x39: ("bit_and",       ""),
    0x3A: ("bit_or",        ""),
    0x3B: ("bit_not",       ""),
    0x3C: ("lsh",           ""),
    0x3D: ("rsh",           ""),
    0x3E: ("push byte",     "b"),   # same mnemonic as 0x0A but different operand type
    0x3F: ("push",          "b"),   # same mnemonic as 0x0B but different operand type
    0x40: ("push dword",    "b"),   # same mnemonic as 0x0C but different operand type
    0x41: ("push string",   "b"),
    0x42: ("push list",     "bB"),
    0x43: ("push slist",    "b"),
    0x44: ("push element",  "BB"),
    0x45: ("push huge",     "bB"),
    0x4B: ("push addr",     "b"),
    0x4C: ("push indirect", "B"),
    0x4D: ("pop indirect",  "B"),
    0x4E: ("push global",   "wB"),
    0x4F: ("pop global",    "wB"),
    0x50: ("ret",           ""),
    0x51: ("jne",           "W"),
    0x52: ("jmp",           "W"),
    0x53: ("suspend",       ""),
    0x54: ("implies",       "BB"),
    0x57: ("spawn",         "BBww"),
    0x58: ("spawn inline",  "wwwBB"),
    0x59: ("push pid",      ""),
    0x5A: ("init",          "B"),
    0x5B: ("line",          "w"),
    0x5C: ("symbol",        "w"),    # special handling needed
    0x5D: ("push byte retval",""),
    0x5E: ("push retval",   ""),
    0x5F: ("push long retval",""),
    0x60: ("int to long",   ""),
    0x61: ("long to int",   ""),
    0x62: ("free string",   "b"),
    0x63: ("free slist",    "b"),
    0x64: ("free list",     "b"),
    0x65: ("free string",   "p"),
    0x66: ("free list",     "p"),
    0x67: ("free slist",    "p"),
    0x69: ("str to ptr",    "b"),
    0x6B: ("str to ptr",    ""),
    0x6C: ("param pid chg", "bB"),
    0x6D: ("push process result",""),
    0x6E: ("add sp",        "v"),
    0x6F: ("push addr",     "p"),
    0x70: ("loop",          "bBB"),
    0x73: ("loopnext",      ""),
    0x74: ("loopscr",       "B"),
    0x75: ("for each",      "bBW"),
    0x76: ("for each str",  "bBW"),
    0x77: ("set info",      ""),
    0x78: ("process exclude",""),
    0x79: ("end",           ""),
    0x7A: ("end",           ""),
}


def _build_mnemonic_table():
    """Build reverse lookup: mnemonic -> list of (opcode, fmt)."""
    table = {}
    for opcode, (mnemonic, fmt) in OPCODE_TABLE.items():
        key = mnemonic.lower().strip()
        if key not in table:
            table[key] = []
        table[key].append((opcode, fmt))
    return table


MNEMONIC_LOOKUP = _build_mnemonic_table()


class AssemblerError(Exception):
    def __init__(self, message, line_num=None, line_text=None):
        self.line_num = line_num
        self.line_text = line_text
        if line_num is not None:
            message = f"Line {line_num}: {message}"
        super().__init__(message)


class ParsedInstruction:
    """A parsed instruction from the disassembly listing."""
    __slots__ = ('offset', 'mnemonic', 'operand_strs', 'raw_hex',
                 'comment', 'line_num', 'is_symbol_op')

    def __init__(self, offset, mnemonic, operand_strs, raw_hex='',
                 comment='', line_num=0, is_symbol_op=False):
        self.offset = offset
        self.mnemonic = mnemonic
        self.operand_strs = operand_strs
        self.raw_hex = raw_hex
        self.comment = comment
        self.line_num = line_num
        self.is_symbol_op = is_symbol_op


def _parse_bp_offset(s):
    """Parse [BP+xxh] or [BP-xxh] -> uint8 value."""
    s = s.strip()
    m = re.match(r'\[BP([+-])([0-9A-Fa-f]+)h\]', s)
    if not m:
        raise ValueError(f"Invalid BP offset: {s}")
    sign = m.group(1)
    val = int(m.group(2), 16)
    if sign == '-':
        val = (-val) & 0xFF
    return val


def _parse_sp_offset(s):
    """Parse [SP+xxh] or [SP-xxh] -> uint8 value."""
    s = s.strip()
    m = re.match(r'\[SP([+-])([0-9A-Fa-f]+)h\]', s)
    if not m:
        raise ValueError(f"Invalid SP offset: {s}")
    sign = m.group(1)
    val = int(m.group(2), 16)
    if sign == '-':
        val = (-val) & 0xFF
    return val


def _parse_hex_byte(s):
    """Parse xxh -> uint8."""
    s = s.strip()
    m = re.match(r'([0-9A-Fa-f]+)h', s)
    if not m:
        raise ValueError(f"Invalid hex byte: {s}")
    return int(m.group(1), 16) & 0xFF


def _parse_hex_word(s):
    """Parse xxxxh -> uint16."""
    s = s.strip()
    m = re.match(r'([0-9A-Fa-f]+)h', s)
    if not m:
        raise ValueError(f"Invalid hex word: {s}")
    return int(m.group(1), 16) & 0xFFFF


def _parse_hex_dword(s):
    """Parse xxxxxxxxh -> uint32."""
    s = s.strip()
    m = re.match(r'([0-9A-Fa-f]+)h', s)
    if not m:
        raise ValueError(f"Invalid hex dword: {s}")
    return int(m.group(1), 16) & 0xFFFFFFFF


def _parse_signed_literal(s):
    """Parse '+42 (2Ah)' or '-8 (F8h)' -> uint8."""
    s = s.strip()
    m = re.match(r'[+-]?\d+\s*\(([0-9A-Fa-f]+)h\)', s)
    if not m:
        raise ValueError(f"Invalid signed literal: {s}")
    return int(m.group(1), 16) & 0xFF


def _parse_jump_offset(s):
    """Parse '+001Fh (-> 00B1h)' or '-0056h (-> 014Fh)' -> sint16."""
    s = s.strip()
    m = re.match(r'([+-])([0-9A-Fa-f]+)h\s*\(->\s*[0-9A-Fa-f]+h\)', s)
    if not m:
        raise ValueError(f"Invalid jump offset: {s}")
    sign = m.group(1)
    val = int(m.group(2), 16)
    if sign == '-':
        val = -val
    # Convert to sint16 encoded as uint16
    return val & 0xFFFF


def _parse_string(s):
    """Parse '"Hello, world!"' -> string bytes (no length prefix, no null terminator)."""
    s = s.strip()
    if not s.startswith('"') or not s.endswith('"'):
        raise ValueError(f"Invalid string: {s}")
    content = s[1:-1]
    # latin-1 maps code points 0x00-0xFF straight back to the same byte, so a
    # listing that DOES carry real high bytes (CP437 text: umlauts, accents,
    # the German ß) re-encodes losslessly. Was 'ascii', which turned every
    # such character into '?' (0x3F).
    #
    # KNOWN LIMIT, not fixable here: the disassembler decodes strings with
    # `ascii, errors='replace'` (u8_usecode_disasm.py:610), so by the time a
    # listing exists those bytes are ALREADY U+FFFD and the original value is
    # unrecoverable from text. errors='replace' below keeps that case working
    # (it degrades to '?') rather than raising. Round-trip stays byte-perfect
    # for these strings only because assemble_bytecode* falls back to the
    # authoritative raw hex — which is exactly why that fallback is now
    # recorded in `encoder_mismatches` instead of hidden. The disassembler is
    # do-not-modify by project rule, so this is a property of the listing
    # format, not a bug to fix in the assembler.
    return content.encode('latin-1', errors='replace')


class UsecodeAssembler:
    """Assemble disassembly listings back into bytecode.

    This reassembles the exact output format produced by u8_usecode_disasm.py.

    Usage:
        asm = UsecodeAssembler()
        class_data = asm.assemble_class(listing_text)
    """

    def __init__(self):
        # Diagnostics, reset per assemble_* call. Both exist because the
        # assembler used to hide its own failures:
        #   encoder_mismatches — _encode_operands produced bytes that disagree
        #     with the authoritative raw hex. The code still falls back to raw
        #     hex (so round-trip stays byte-perfect), but the disagreement is
        #     now RECORDED instead of silently swallowed (review L8), which is
        #     what makes the encoder testable at all (review H2).
        #   parse_drops — lines that look like instructions ("XXXX: ..") but
        #     failed the instruction regex. These used to `continue` silently,
        #     so a standalone assemble wrote a TRUNCATED class and still
        #     reported success (review M8).
        self.encoder_mismatches = []
        self.parse_drops = []

    def _parse_listing(self, text):
        """Parse a disassembly listing into structured data.

        Returns:
            (header_info, event_table_entries, instructions)
        """
        lines = text.split('\n')
        header_info = {}
        event_table = {}  # event_id -> offset
        instructions = []

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue

            # Header: unknown1, total_size, unknown2
            m = re.match(
                r';\s*Header:\s*unknown1=([0-9A-Fa-f]+)\s+'
                r'total_size=([0-9A-Fa-f]+)\s+'
                r'unknown2=([0-9A-Fa-f]+)',
                stripped)
            if m:
                header_info['unknown1'] = int(m.group(1), 16)
                header_info['total_size'] = int(m.group(2), 16)
                header_info['unknown2'] = int(m.group(3), 16)
                continue

            # Event table entry: ;   Event XX (name()): offset YYYY
            # Note: event names like "look()" have nested parens, so we
            # match everything up to the LAST ): before "offset"
            m = re.match(
                r';\s*Event\s+([0-9A-Fa-f]+)\s*\(.*\):\s*offset\s+([0-9A-Fa-f]+)',
                stripped)
            if m:
                event_id = int(m.group(1), 16)
                offset = int(m.group(2), 16)
                event_table[event_id] = offset
                continue

            # Jump target label: .LXXXX:
            if re.match(r'\.L[0-9A-Fa-f]+:', stripped):
                continue  # Labels are informational, we use offsets

            # Event separator: ; ─── Event XX: name() ───
            if re.match(r';\s*─', stripped):
                continue

            # Other comments
            if stripped.startswith(';'):
                continue

            # Data byte: skip lines where mnemonic is literally "db"
            # (unknown opcode placeholder from the disassembler)
            # Must NOT use 'db' in stripped — hex bytes like "64 62" match "db"

            # Instruction line:
            # Format: "  XXXX: HH HH HH ...          mnemonic\toperands\t; comment"
            m = re.match(
                r'([0-9A-Fa-f]{4}):\s+'    # offset
                r'((?:[0-9A-Fa-f]{2}\s?)+)'  # hex bytes
                r'\s+'                       # padding
                r'(.+)',                     # rest (mnemonic + operands + comment)
                stripped)
            if not m:
                # M8: only skip lines that are genuinely NOT instructions
                # (comments, labels, blanks). A line that STARTS like an
                # instruction ("01A4: ...") but fails the full regex is a
                # real parse failure — dropping it silently truncates the
                # assembled class while still reporting success.
                if re.match(r'[0-9A-Fa-f]{4}:', stripped):
                    self.parse_drops.append((line_num, stripped))
                continue

            offset = int(m.group(1), 16)
            raw_hex = m.group(2).strip()
            rest = m.group(3)

            # Split rest into mnemonic, operands, comment
            # Comment starts with "; " that isn't inside a string
            comment = ''
            # Find comment - look for tab-separated ;
            # The format is: mnemonic\toperands\t; comment
            # or: mnemonic\t; comment  (no operands)
            # or: mnemonic  (no operands, no comment)

            # Parse the rest by splitting on tabs
            parts = rest.split('\t')
            mnemonic = parts[0].strip()

            operand_strs = []
            for i in range(1, len(parts)):
                part = parts[i].strip()
                if part.startswith('; ') or part.startswith(';'):
                    comment = part.lstrip('; ').strip()
                    break
                elif part:
                    operand_strs.append(part)

            # Check if this is a symbol opcode (0x5C) - special handling
            is_symbol = (mnemonic == 'symbol')

            instr = ParsedInstruction(
                offset=offset,
                mnemonic=mnemonic,
                operand_strs=operand_strs,
                raw_hex=raw_hex,
                comment=comment,
                line_num=line_num,
                is_symbol_op=is_symbol,
            )
            instructions.append(instr)

        return header_info, event_table, instructions

    def _resolve_opcode(self, mnemonic, operand_strs, raw_hex):
        """Determine the correct opcode for an ambiguous mnemonic.

        Uses the raw hex bytes from the listing as the authoritative source.
        This handles cases like 'push byte' (0x0A vs 0x3E), 'push' (0x0B vs 0x3F),
        'push dword' (0x0C vs 0x40), 'free string' (0x62 vs 0x65), etc.
        """
        # The raw hex bytes always start with the opcode byte
        hex_parts = raw_hex.split()
        if hex_parts:
            opcode = int(hex_parts[0], 16)
            if opcode in OPCODE_TABLE:
                return opcode, OPCODE_TABLE[opcode][1]

        # Fallback: look up by mnemonic
        key = mnemonic.lower().strip()
        candidates = MNEMONIC_LOOKUP.get(key, [])
        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) == 0:
            raise AssemblerError(f"Unknown mnemonic: {mnemonic}")

        # Multiple candidates - disambiguate by operand types
        for opcode, fmt in candidates:
            if self._operands_match_format(operand_strs, fmt):
                return opcode, fmt

        raise AssemblerError(
            f"Ambiguous mnemonic '{mnemonic}' with operands {operand_strs}")

    def _operands_match_format(self, operand_strs, fmt):
        """Check if operand strings match a given format."""
        if not fmt and not operand_strs:
            return True
        if not operand_strs and fmt:
            return False

        # Count expected operands
        expected = len(fmt)
        if expected != len(operand_strs):
            return False

        for i, (f, s) in enumerate(zip(fmt, operand_strs)):
            s = s.strip()
            if f == 'b' and not re.match(r'\[BP[+-]', s):
                return False
            if f == 'p' and not re.match(r'\[SP[+-]', s):
                return False
            if f == 'v' and not re.match(r'[+-]\d+\s*\(', s):
                return False
            if f == 'W' and not re.match(r'[+-]', s):
                return False
            if f == 's' and not s.startswith('"'):
                return False
        return True

    def _encode_operands(self, opcode, fmt, operand_strs, raw_hex_bytes):
        """Encode operand strings into bytes according to the format.

        For the symbol opcode (0x5C), we use the raw hex bytes directly
        since the format is special (uint16 + 9-byte name).
        """
        buf = bytearray()

        if opcode == 0x5C:
            # Symbol opcode: use raw hex bytes directly (skip opcode byte)
            return bytes(raw_hex_bytes[1:])

        op_idx = 0
        for f in fmt:
            if op_idx >= len(operand_strs):
                raise AssemblerError(
                    f"Not enough operands for opcode {opcode:02X}: "
                    f"expected format '{fmt}', got {operand_strs}")

            s = operand_strs[op_idx].strip()

            if f == 'b':
                val = _parse_bp_offset(s)
                buf.append(val)
            elif f == 'p':
                val = _parse_sp_offset(s)
                buf.append(val)
            elif f == 'v':
                val = _parse_signed_literal(s)
                buf.append(val)
            elif f == 'B':
                val = _parse_hex_byte(s)
                buf.append(val)
            elif f == 'w':
                val = _parse_hex_word(s)
                buf.extend(struct.pack('<H', val))
            elif f == 'W':
                val = _parse_jump_offset(s)
                buf.extend(struct.pack('<H', val))
            elif f == 'd':
                val = _parse_hex_dword(s)
                buf.extend(struct.pack('<I', val))
            elif f == 's':
                string_bytes = _parse_string(s)
                # Format: uint16 length + string data + 0x00 terminator
                buf.extend(struct.pack('<H', len(string_bytes)))
                buf.extend(string_bytes)
                buf.append(0x00)  # null terminator
            else:
                raise AssemblerError(f"Unknown format char '{f}'")

            op_idx += 1

        return bytes(buf)

    def _build_event_table(self, event_table):
        """Build the 128-byte event table from event_id -> offset mapping."""
        event_table_bytes = bytearray(128)
        for event_id, offset in event_table.items():
            struct.pack_into('<I', event_table_bytes, event_id * 4, offset)
        return bytes(event_table_bytes)

    def assemble_bytecode(self, instructions, event_table):
        """Assemble parsed instructions into bytecode.

        Uses raw hex bytes from the listing as the primary encoding.
        Falls back to operand-based encoding only when raw hex is unavailable.

        Returns the complete bytecode area including the 128-byte event table.
        """
        event_table_bytes = self._build_event_table(event_table)

        # Build bytecode from raw hex bytes (most reliable for round-trip)
        bytecode_buf = bytearray()
        for instr in instructions:
            if instr.raw_hex:
                raw_hex_bytes = bytes(
                    int(h, 16) for h in instr.raw_hex.split())
                bytecode_buf.extend(raw_hex_bytes)
            else:
                # No raw hex available — encode from operands
                opcode, fmt = self._resolve_opcode(
                    instr.mnemonic, instr.operand_strs, instr.raw_hex)
                encoded = bytearray()
                encoded.append(opcode)
                encoded.extend(
                    self._encode_operands(opcode, fmt, instr.operand_strs, b''))
                bytecode_buf.extend(encoded)

        return bytes(event_table_bytes) + bytes(bytecode_buf)

    def assemble_bytecode_from_operands(self, instructions, event_table):
        """Assemble instructions by parsing operands (not raw hex).

        This is the true assembler path used when generating code from scratch
        (Track B compiler). Validates encoding against raw hex when available.
        """
        event_table_bytes = self._build_event_table(event_table)
        bytecode_buf = bytearray()

        for instr in instructions:
            opcode, fmt = self._resolve_opcode(
                instr.mnemonic, instr.operand_strs, instr.raw_hex)

            encoded = bytearray()
            encoded.append(opcode)

            if instr.raw_hex:
                raw_hex_bytes = bytes(
                    int(h, 16) for h in instr.raw_hex.split())
            else:
                raw_hex_bytes = b''

            encoded.extend(
                self._encode_operands(opcode, fmt, instr.operand_strs, raw_hex_bytes))

            # Verify against raw hex if available. The raw hex from the
            # disassembler is authoritative, so we still fall back to it to
            # keep round-trip byte-perfect — but RECORD the disagreement
            # (L8/H2). Silently substituting meant an operand-encoding bug
            # (sign, endianness, width) could never be observed: the encoder
            # "passed" by being overwritten.
            if raw_hex_bytes and bytes(encoded) != raw_hex_bytes:
                self.encoder_mismatches.append({
                    'offset': instr.offset,
                    'mnemonic': instr.mnemonic,
                    'operands': list(instr.operand_strs),
                    'encoded': bytes(encoded).hex(),
                    'expected': raw_hex_bytes.hex(),
                })
                encoded = bytearray(raw_hex_bytes)

            bytecode_buf.extend(encoded)

        return bytes(event_table_bytes) + bytes(bytecode_buf)

    def assemble_class(self, listing_text):
        """Assemble a complete class listing into binary class data.

        Uses raw hex bytes from the disassembly listing for perfect round-trip.
        This is the primary method for reassembling disassembler output.

        Args:
            listing_text: text output from disassemble_class()

        Returns:
            bytes: the complete binary class data (header + event table + bytecode)
        """
        self.encoder_mismatches = []
        self.parse_drops = []
        header_info, event_table, instructions = self._parse_listing(listing_text)

        if not header_info:
            raise AssemblerError("No header found in listing")

        # Build bytecode (event table + instructions)
        bytecode = self.assemble_bytecode(instructions, event_table)

        # Build 12-byte header
        header = struct.pack('<III',
                           header_info['unknown1'],
                           header_info['total_size'],
                           header_info['unknown2'])

        return header + bytecode

    def assemble_class_encoded(self, listing_text):
        """Assemble a listing by ENCODING operands, not copying raw hex.

        This is the path that actually exercises `_encode_operands`, and it
        exists because `assemble_class()` copies `raw_hex` verbatim whenever
        it is present — which it always is in disassembler output. That made
        round-trip Phase 2 byte-identical to Phase 1's raw copy, so the
        "516/516 round-trip" result proved the listing could be re-copied,
        not that the assembler can encode anything (review H2).

        Byte-for-byte output is still identical to assemble_class(), because
        any encoder disagreement falls back to the authoritative raw hex.
        The difference is that disagreements now land in
        `self.encoder_mismatches`, so a caller can assert on them.
        """
        self.encoder_mismatches = []
        self.parse_drops = []
        header_info, event_table, instructions = self._parse_listing(listing_text)

        if not header_info:
            raise AssemblerError("No header found in listing")

        bytecode = self.assemble_bytecode_from_operands(instructions, event_table)
        header = struct.pack('<III',
                             header_info['unknown1'],
                             header_info['total_size'],
                             header_info['unknown2'])
        return header + bytecode

    def assemble_class_raw_fallback(self, listing_text):
        """Assemble by using raw hex bytes directly from the listing.

        This is the most reliable method for round-trip validation since
        it uses the exact bytes shown in the disassembly output.
        """
        header_info, event_table, instructions = self._parse_listing(listing_text)

        if not header_info:
            raise AssemblerError("No header found in listing")

        # Build event table
        event_table_bytes = bytearray(128)
        for event_id, offset in event_table.items():
            struct.pack_into('<I', event_table_bytes, event_id * 4, offset)

        # Build bytecode from raw hex
        bytecode_buf = bytearray()
        for instr in instructions:
            raw_bytes = bytes(
                int(h, 16) for h in instr.raw_hex.split())
            bytecode_buf.extend(raw_bytes)

        # Build header
        header = struct.pack('<III',
                           header_info['unknown1'],
                           header_info['total_size'],
                           header_info['unknown2'])

        return header + bytes(event_table_bytes) + bytes(bytecode_buf)


def assemble_from_listing(listing_text):
    """Convenience function to assemble a listing string."""
    asm = UsecodeAssembler()
    return asm.assemble_class(listing_text)


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: u8_assembler.py <listing.txt> [output.bin]")
        print("  Assembles a disassembly listing back into binary bytecode.")
        print("  If output is '-', prints hex dump to stdout.")
        sys.exit(1)

    listing_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    with open(listing_path, 'r') as f:
        listing = f.read()

    asm = UsecodeAssembler()
    data = asm.assemble_class(listing)

    if output_path == '-':
        # Hex dump
        for off in range(0, len(data), 16):
            hexb = ' '.join(f'{b:02X}' for b in data[off:off+16])
            print(f"  {off:04X}: {hexb}")
    elif output_path:
        with open(output_path, 'wb') as f:
            f.write(data)
        print(f"Wrote {len(data)} bytes to {output_path}")
    else:
        print(f"Assembled {len(data)} bytes")

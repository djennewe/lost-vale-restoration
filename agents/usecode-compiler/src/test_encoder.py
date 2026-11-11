#!/usr/bin/env python3
"""test_encoder.py — prove the assembler's OPERAND ENCODER actually works.

Guards adversarial-review finding H2. `assemble_class()` copies `raw_hex`
verbatim whenever it is present, and the disassembler emits raw hex on every
line — so `_encode_operands` and every operand parser were dead code on the
validation path, and round-trip Phase 2 was byte-identical to Phase 1's raw
copy. "516/516 round-trip" proved hex could be re-copied, not that the
assembler can encode anything: any sign, endian, or width bug passed silently.

This test drives `assemble_class_encoded()`, which runs the real encoder, and
asserts:
  1. Output is still byte-identical to the original class data.
  2. Every instruction the encoder disagreed with is a KNOWN, EXPLAINED case.
     Any NEW kind of disagreement fails.

The only accepted disagreement is `push string` carrying non-ASCII text: the
disassembler decodes strings with `ascii, errors='replace'`
(u8_usecode_disasm.py:610), so CP437 high bytes (umlauts, accents, ß) are
already destroyed in the listing and cannot be recovered from text. Round-trip
survives via the raw-hex fallback. The disassembler is do-not-modify by
project rule, so this is a property of the listing format.

Exits nonzero on failure.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, '..', '..', 'usecode-disasm', 'src'))

from u8_flex import UsecodeFlexArchive
from u8_usecode_disasm import UsecodeDisassembler
from u8_assembler import UsecodeAssembler

REPO = os.path.abspath(os.path.join(_HERE, '..', '..', '..'))
BASE_FLX = os.path.join(REPO, 'shared', 'data', 'u8-install',
                        'USECODE', 'EUSECODE.FLX')

# Pinned baseline (2026-07-25, base game EUSECODE.FLX): 7 instructions across
# 3 classes (SALKIND, DARION, MYTHRAN) — all German/French strings. This may
# only go DOWN.
MAX_KNOWN_STRING_MISMATCHES = 7

# Classes the encoder path cannot assemble FROM TEXT at all (2026-07-25, base
# game): 17 of 516. Two documented listing-format limits, neither an encoder
# bug and neither fixable here (the disassembler is do-not-modify by rule):
#   16x  a string operand containing a newline. The disassembler prints it
#        verbatim, so the quoted operand spans multiple physical lines and the
#        line-based listing parser sees an unterminated string.
#    1x  ORLOK: a jump offset outside the range the listing text can express.
# The raw-hex path (assemble_class) handles all 516 — that is what the build
# and test_roundtrip use. This pin measures how far the REAL encoder reaches
# and may only go DOWN.
MAX_ENCODER_UNPARSEABLE = 17


def is_known_lossy_string(m):
    """True if this mismatch is the documented non-ASCII string case."""
    if not m['mnemonic'].startswith('push string'):
        return False
    # The encoder emits 0x3F ('?') where the original had a high byte; the
    # two must otherwise be the same length.
    enc = bytes.fromhex(m['encoded'])
    exp = bytes.fromhex(m['expected'])
    if len(enc) != len(exp):
        return False
    for a, b in zip(enc, exp):
        if a != b and not (a == 0x3F and b > 0x7F):
            return False
    return True


def main():
    if not os.path.exists(BASE_FLX):
        print(f"SKIP: base EUSECODE.FLX not found at {BASE_FLX}")
        return 0

    flx = UsecodeFlexArchive(BASE_FLX)
    disasm = UsecodeDisassembler()
    asm = UsecodeAssembler()

    total = identical = 0
    unparseable = []
    failed_classes = []
    known_mismatches = 0
    unknown = []
    parse_drops = []

    for classid, name, data in flx.all_classes():
        try:
            listing = disasm.disassemble_class(data, classid, name)
        except Exception:
            continue          # disassembly failures are test_roundtrip's job
        try:
            out = asm.assemble_class_encoded(listing)
        except Exception as e:
            # Listing-format limits (see MAX_ENCODER_UNPARSEABLE), not
            # wrong bytes. Counted and ratcheted, not treated as silence.
            unparseable.append(f"{name} (0x{classid:04X}): {e}".split('\n')[0][:110])
            total += 1
            continue

        total += 1
        if out == data:
            identical += 1
        else:
            failed_classes.append(
                f"{name} (0x{classid:04X}): assembled output differs from original")

        for m in asm.encoder_mismatches:
            if is_known_lossy_string(m):
                known_mismatches += 1
            else:
                unknown.append((name, m))
        for ln, text in asm.parse_drops:
            parse_drops.append(f"{name}: line {ln}: {text[:70]}")

    print("=" * 62)
    print(f"Encoder path: {total} classes seen, {identical} byte-identical, "
          f"{len(unparseable)} unparseable from text (pin {MAX_ENCODER_UNPARSEABLE})")
    print(f"Known lossy-string mismatches: {known_mismatches} "
          f"(pin {MAX_KNOWN_STRING_MISMATCHES})")
    print(f"Unexplained encoder mismatches: {len(unknown)}")
    print(f"Instruction-shaped lines dropped by the parser: {len(parse_drops)}")
    print("=" * 62)

    ok = True
    if failed_classes:
        ok = False
        print("\nFAIL: classes that did not reassemble byte-identically:")
        for f in failed_classes[:20]:
            print(f"   {f}")
    if unknown:
        ok = False
        print("\nFAIL: encoder produced bytes that disagree with retail for a "
              "reason other than the documented non-ASCII string case.")
        print("      This is the class of bug H2 existed to expose "
              "(sign / endian / width):")
        for name, m in unknown[:20]:
            print(f"   {name}: {m['mnemonic']!r} ops={m['operands']}")
            print(f"      encoded={m['encoded']}")
            print(f"      expected={m['expected']}")
    if len(unparseable) > MAX_ENCODER_UNPARSEABLE:
        ok = False
        print(f"\nFAIL: encoder-unparseable classes grew "
              f"({len(unparseable)} > {MAX_ENCODER_UNPARSEABLE}):")
        for u in unparseable[:20]:
            print(f"   {u}")
    elif len(unparseable) < MAX_ENCODER_UNPARSEABLE:
        print(f"\nNOTE: encoder-unparseable dropped to {len(unparseable)}; "
              f"lower MAX_ENCODER_UNPARSEABLE to lock it in.")

    if known_mismatches > MAX_KNOWN_STRING_MISMATCHES:
        ok = False
        print(f"\nFAIL: lossy-string mismatches grew "
              f"({known_mismatches} > {MAX_KNOWN_STRING_MISMATCHES}).")
    elif known_mismatches < MAX_KNOWN_STRING_MISMATCHES:
        print(f"\nNOTE: lossy-string mismatches dropped to {known_mismatches}; "
              f"lower MAX_KNOWN_STRING_MISMATCHES to lock it in.")
    if parse_drops:
        ok = False
        print("\nFAIL: the listing parser silently dropped instruction-shaped "
              "lines (M8) — the assembled class would be truncated:")
        for d in parse_drops[:20]:
            print(f"   {d}")

    if ok:
        print("\nOK: the operand encoder is exercised and correct "
              "(only the documented listing-format string loss remains).")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

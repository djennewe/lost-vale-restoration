#!/usr/bin/env python3
"""
test_roundtrip.py — Round-trip validation for the assembler.

For each class in EUSECODE.FLX:
  1. Disassemble the class data to text
  2. Reassemble the text back to binary
  3. Byte-compare original vs reassembled

Target: ZERO byte differences on ALL 516 base game classes.
"""

import sys
import os

# Add both src directories to path
sys.path.insert(0, os.path.dirname(__file__))
disasm_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'usecode-disasm', 'src')
sys.path.insert(0, disasm_dir)

from u8_flex import UsecodeFlexArchive
from u8_usecode_disasm import UsecodeDisassembler
from u8_assembler import UsecodeAssembler


def run_roundtrip(flx_path, verbose=False, max_classes=None, stop_on_error=False):
    """Run round-trip test on all classes in EUSECODE.FLX."""
    flx = UsecodeFlexArchive(flx_path)
    disasm = UsecodeDisassembler()
    asm = UsecodeAssembler()

    total = 0
    passed = 0
    failed = 0
    errors = []
    skipped = 0

    for classid, name, data in flx.all_classes():
        if max_classes and total >= max_classes:
            break

        total += 1

        try:
            # Step 1: Disassemble
            listing = disasm.disassemble_class(data, classid, name)

            # Step 2: Reassemble
            reassembled = asm.assemble_class(listing)

            # Step 3: Compare
            if reassembled == data:
                passed += 1
                if verbose:
                    print(f"  PASS  {classid:04X} {name:>10s}  ({len(data)} bytes)")
            else:
                failed += 1
                # Find first difference
                min_len = min(len(data), len(reassembled))
                diff_offset = None
                for i in range(min_len):
                    if data[i] != reassembled[i]:
                        diff_offset = i
                        break
                if diff_offset is None and len(data) != len(reassembled):
                    diff_offset = min_len

                err_msg = (
                    f"  FAIL  {classid:04X} {name:>10s}  "
                    f"orig={len(data)} reasm={len(reassembled)} "
                    f"first_diff=0x{diff_offset:04X}"
                )
                errors.append(err_msg)
                print(err_msg)

                if verbose and diff_offset is not None:
                    # Show context around the first difference
                    start = max(0, diff_offset - 4)
                    end = min(min_len, diff_offset + 8)
                    orig_hex = ' '.join(f'{data[i]:02X}' for i in range(start, end))
                    rasm_hex = ' '.join(f'{reassembled[i]:02X}'
                                       for i in range(start, min(len(reassembled), end)))
                    print(f"         orig [{start:04X}]: {orig_hex}")
                    print(f"         rasm [{start:04X}]: {rasm_hex}")

                if stop_on_error:
                    print("\nStopping on first error.")
                    break

        except Exception as e:
            failed += 1
            err_msg = f"  ERROR {classid:04X} {name:>10s}  {e}"
            errors.append(err_msg)
            print(err_msg)
            if stop_on_error:
                import traceback
                traceback.print_exc()
                break

    print(f"\n{'='*60}")
    print(f"Round-trip results: {passed}/{total} passed, "
          f"{failed} failed, {skipped} skipped")
    if errors:
        print(f"\nFailures:")
        for e in errors[:20]:
            print(e)
        if len(errors) > 20:
            print(f"  ... and {len(errors)-20} more")
    print(f"{'='*60}")

    return passed, total, failed, errors


def run_roundtrip_raw(flx_path, verbose=False, max_classes=None):
    """Run round-trip using raw hex bytes (baseline test)."""
    flx = UsecodeFlexArchive(flx_path)
    disasm = UsecodeDisassembler()
    asm = UsecodeAssembler()

    total = 0
    passed = 0
    failed = 0

    for classid, name, data in flx.all_classes():
        if max_classes and total >= max_classes:
            break
        total += 1

        try:
            listing = disasm.disassemble_class(data, classid, name)
            reassembled = asm.assemble_class_raw_fallback(listing)

            if reassembled == data:
                passed += 1
            else:
                failed += 1
                min_len = min(len(data), len(reassembled))
                diff_offset = None
                for i in range(min_len):
                    if data[i] != reassembled[i]:
                        diff_offset = i
                        break
                if diff_offset is None:
                    diff_offset = min_len
                print(f"  FAIL (raw) {classid:04X} {name:>10s}  "
                      f"orig={len(data)} reasm={len(reassembled)} "
                      f"first_diff=0x{diff_offset:04X}")
        except Exception as e:
            failed += 1
            print(f"  ERROR (raw) {classid:04X} {name:>10s}  {e}")

    print(f"\nRaw fallback: {passed}/{total} passed, {failed} failed")
    return passed, total, failed


if __name__ == '__main__':
    # Default path — relative to this file (repo root three levels up),
    # same convention as lv_manifest.py.
    _repo_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
    flx_path = os.path.join(_repo_root, 'shared', 'data', 'USECODE.FLX')

    if len(sys.argv) > 1:
        flx_path = sys.argv[1]

    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    stop_on_error = '--stop' in sys.argv or '-s' in sys.argv
    raw_only = '--raw' in sys.argv
    max_classes = None
    for arg in sys.argv:
        if arg.startswith('--max='):
            max_classes = int(arg.split('=')[1])

    if raw_only:
        print("Running raw hex fallback round-trip test...")
        run_roundtrip_raw(flx_path, verbose=verbose, max_classes=max_classes)
    else:
        print("Running assembler round-trip test...")
        print(f"FLX: {flx_path}")
        print()

        # First, run raw fallback to validate the parsing pipeline
        print("Phase 1: Raw hex fallback (validates parsing)")
        raw_passed, raw_total, raw_failed = run_roundtrip_raw(
            flx_path, verbose=verbose, max_classes=max_classes)

        if raw_failed > 0:
            print("\nWARNING: Raw fallback failed! Parsing pipeline has bugs.")
            print("Fix parsing before testing full assembly.\n")

        # Then run full assembly
        print("\nPhase 2: Full assembly (validates encoding)")
        passed, total, failed, _errors = run_roundtrip(
            flx_path, verbose=verbose, max_classes=max_classes,
            stop_on_error=stop_on_error)

        # M5: this used to always exit 0, so a failing round-trip still
        # looked like a passing test run. The round-trip is the assembler's
        # integrity backbone — a failure here must be loud.
        # NOTE: Phase 2 shares Phase 1's raw-hex path (see review H2); the
        # test that actually exercises the operand encoder is test_encoder.py.
        if raw_failed or failed:
            print(f"\nFAILED: raw phase {raw_failed} failure(s), "
                  f"assembly phase {failed} failure(s)")
            sys.exit(1)

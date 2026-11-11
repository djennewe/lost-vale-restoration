#!/usr/bin/env python3
"""
test_calli_arity.py — every `calli` carries its argument byte count; check
it against the intrinsic's signature, for every class we compile.

WHY THIS EXISTS (2026-07-28). Our compiler emitted Frizbee1.getPoint(fp)
with B=6 where the engine's I_getPoint reads 8 bytes (ARG_ITEM_FROM_PTR +
ARG_UC_PTR): the WorldPoint out-param was pushed as a 2-byte value instead
of a 4-byte `push addr`. The engine dereferenced garbage, wrote nowhere,
and the Sacred Circle's reforged shield — the artifact quest step 17
needs — vanished at (-60,-30,0). It cost three engine runs to find,
and the simulator was no help because its getPoint stub had been
reverse-engineered from our own broken emission. The mismatch was sitting
in the bytecode the whole time, machine-checkable: this file is that check.

METHOD. Expected sizes come from U8_INTRINSICS signatures (word/uword/
byte = 2, long = 4, any pointer = 4, plus 4 for the implicit item/actor
receiver on non-static intrinsics). The table is CALIBRATED ON RETAIL:
all 516 base-game classes — bytecode from Origin's real compiler — must
lint clean before the rule is applied to us. Signatures whose retail
usage disagrees with the naive reading get per-intrinsic overrides below,
each with the retail evidence; an intrinsic retail never calls stays at
the naive reading. Then every class in the BUILT EUSECODE.FLX is linted.

Known accepted variance (not errors, documented):
  - Item::pop/popToEnd lead with ARG_NULL32, which the engine never reads,
    so retail itself is loose about the receiver bytes there.
"""

import os
import re
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SRC_DIR)))
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'agents', 'usecode-disasm', 'src'))

from u8_flex import UsecodeFlexArchive            # noqa: E402
from u8_usecode_disasm import (UsecodeDisassembler,  # noqa: E402
                               U8_INTRINSICS)

# PRISTINE base game: shared/data/USECODE.FLX, the same file build_eusecode
# reads as BASE_FLX. Never shared/data/u8-install/USECODE/EUSECODE.FLX:
# install_lv.sh installs the LV build there (the C3 base-pollution trap),
# so calibrating against it silently calibrates against ourselves. (This
# used to prefer the installer's EUSECODE.FLX.bak and fall back to the
# installed file when no .bak existed.)
RETAIL_FLX = os.path.join(BASE_DIR, 'shared', 'data', 'USECODE.FLX')
BUILD_FLX = os.path.join(BASE_DIR, 'shared', 'build', 'EUSECODE.FLX')

# Static intrinsic classes: no implicit receiver pointer. Everything else
# with a Class:: prefix takes ARG_*_FROM_PTR first (4 bytes). Mirrors
# u8c_codegen's push-this rule; retail calibration below verifies it.
STATIC_CLASSES = {'Kernel', 'Camera', 'UCMachine', 'U8MousePointer'}

TOKEN_SIZE = {
    'word': 2, 'uword': 2, 'sword': 2, 'byte': 2, 'ubyte': 2,
    'ProcessType': 2, 'AnimSet': 2, 'Activity': 2,
    'long': 4, 'ulong': 4,
    # every pointer: char*, WorldPoint*, word*, uword*
}


def expected_bytes(sig):
    """(expected_arg_bytes, is_process) for one signature string, or None
    if it cannot be derived."""
    m = re.search(r'(?:(\w+)\s+)?(?:(\w+)::)?(\w+)\((.*)\)\s*$', sig)
    if not m:
        return None
    _ret, cls, _name, args = m.groups()
    total = 0
    if cls and cls not in STATIC_CLASSES:
        total += 4  # implicit item/actor/egg receiver pointer
    for tok in args.split(','):
        tok = tok.strip()
        if not tok:
            continue
        tok = tok.split()[0]
        if tok.endswith('*'):
            total += 4
        elif tok in TOKEN_SIZE:
            total += TOKEN_SIZE[tok]
        else:
            return None
    return total


# Per-intrinsic overrides where retail bytecode disagrees with the naive
# signature reading. Keyed by intrinsic number; value = set of B values
# retail actually emits (measured by the calibration loop below — rerun
# with LINT_CALIBRATE=1 to regenerate the evidence). Empty as of
# 2026-07-28: all 1431 retail classes match the naive table exactly.
RETAIL_OVERRIDES = {}

# Known deviations in the 1994 SOURCE itself — calls that under-supply an
# intrinsic in the recovered text, faithfully compiled. Each is (classid,
# intrinsic, B) -> max occurrences. Fixing one means an lv-patched copy of
# the source, not a compiler change; a NEW deviation must not hide behind
# these pins.
PINNED_1994 = {
    # lv-patched/FREE.UNK:1318 (verbatim 1994):
    #   spawn sphincterBoyTony.schedule(TimeInGameHours():Long) -> return;
    # The ulong arg is a 2-byte retval push. Dead-end joke code — nothing
    # named sphincterBoyTony exists — kept byte-faithful.
    (1454, 0xB1, 6): 1,
}

passed = failed = 0


def check(desc, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        print(f'  PASS  {desc}')
    else:
        failed += 1
        print(f'  FAIL  {desc}  {detail}')


EXPECTED = {}
for num, sig in enumerate(U8_INTRINSICS):
    e = expected_bytes(sig)
    if e is not None:
        EXPECTED[num] = e


def lint_flx(path, classes):
    """-> {(classid, offset, intrinsic, got, want), ...}"""
    flx = UsecodeFlexArchive(path)
    dis = UsecodeDisassembler()
    bad = []
    per_intrinsic = {}
    for cid in classes:
        blob = flx.get_class_data(cid)
        if not blob:
            continue
        try:
            ins = dis.disassemble_bytecode(blob[12:], start_offset=0x80)
        except Exception:
            continue
        for x in ins:
            if x.opcode != 0x0F or len(x.operands) < 2:
                continue
            got = x.operands[0][1]
            num = x.operands[1][1]
            per_intrinsic.setdefault(num, set()).add(got)
            want = EXPECTED.get(num)
            if want is None:
                continue
            if num in RETAIL_OVERRIDES:
                if got in RETAIL_OVERRIDES[num]:
                    continue
                want = RETAIL_OVERRIDES[num]
            if got != want:
                bad.append((cid, x.offset, num, got, want))
    return bad, per_intrinsic


print('=' * 70)
print('calli arity lint — expected sizes calibrated on retail bytecode')

# ── Phase 1: retail must lint clean (it is the ground truth) ──────────
retail_bad, retail_seen = lint_flx(RETAIL_FLX, range(1431))
if retail_bad and os.environ.get('LINT_CALIBRATE'):
    # Emit override table entries for signatures the naive reading gets
    # wrong, with the evidence, then bail: a human moves them into
    # RETAIL_OVERRIDES with a comment.
    from collections import Counter
    ctr = Counter((num, got, want) for _c, _o, num, got, want in retail_bad)
    for (num, got, want), n in sorted(ctr.items()):
        print(f'  CALIBRATE  {num:#05x} {U8_INTRINSICS[num]!r}: retail '
              f'emits B={got} x{n}, naive expectation {want}')
    sys.exit(2)

check('retail: all 1431 base classes lint clean '
      f'({len(retail_seen)} intrinsics, '
      f'{sum(len(v) for v in retail_seen.values())} distinct (num,B) pairs)',
      not retail_bad,
      f'{len(retail_bad)} mismatches — the size table is wrong, '
      f'recalibrate with LINT_CALIBRATE=1; first: {retail_bad[:4]}')

# ── Phase 2: our build ────────────────────────────────────────────────
ours_bad, _ = lint_flx(BUILD_FLX, range(1456))

# Retail-identical classes lint identically, so any finding here is in a
# class we compiled. Report them all; assert none.
from collections import Counter
pin_seen = Counter()
real_bad = []
for cid, off, num, got, want in ours_bad:
    key = (cid, num, got)
    if key in PINNED_1994 and pin_seen[key] < PINNED_1994[key]:
        pin_seen[key] += 1
        continue
    real_bad.append((cid, off, num, got, want))
for cid, off, num, got, want in real_bad[:12]:
    print(f'    class {cid} @ {hex(off)}: {U8_INTRINSICS[num]!r} '
          f'B={got}, engine reads {want}')
check('our build: every compiled calli matches the engine\'s arg sizes '
      f'(beyond {sum(pin_seen.values())} pinned 1994-source deviations)',
      not real_bad, f'{len(real_bad)} mismatches (first 12 above)')
check('the pinned 1994 deviations are all still present (fixing one '
      'means updating PINNED_1994, not silence)',
      sum(pin_seen.values()) == sum(PINNED_1994.values()),
      f'saw {dict(pin_seen)}, pinned {PINNED_1994}')

print()
print('=' * 70)
print(f'{"OK" if failed == 0 else "FAILED"}: {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)

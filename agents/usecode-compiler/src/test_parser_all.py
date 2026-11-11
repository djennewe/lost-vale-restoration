#!/usr/bin/env python3
"""Test parser on all UNK files in the project."""
import sys
import os
import glob

sys.path.insert(0, os.path.dirname(__file__))
from u8c_parser import parse_file

# Path resolution: relative to this file (repo root three levels up), same
# convention as lv_manifest.py.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

base = os.path.join(REPO_ROOT, 'shared', 'data', 'lv-usecode')
patterns = [
    os.path.join(base, 'LOST VALE', '*.UNK'),
    os.path.join(base, 'UNK files', 'UNK', '*.UNK'),
    os.path.join(base, 'U8', '*.UNK'),
]

total = 0
ok = 0
errs = 0
seen_names = set()   # basenames of files that produced a warning/error

for pattern in patterns:
    for path in sorted(glob.glob(pattern)):
        total += 1
        name = os.path.basename(path)
        try:
            # Redirect stderr to capture parse errors
            import io
            old_stderr = sys.stderr
            sys.stderr = io.StringIO()
            ast = parse_file(path)
            errors = sys.stderr.getvalue()
            sys.stderr = old_stderr
            if errors.strip():
                errs += 1
                seen_names.add(name)
                print(f"  WARN  {name:20s}  {errors.strip()[:120]}")
            else:
                ok += 1
                n_funcs = len(ast.functions)
                print(f"  OK    {name:20s}  {n_funcs} functions")
        except Exception as e:
            errs += 1
            seen_names.add(name)
            sys.stderr = old_stderr
            print(f"  FAIL  {name:20s}  {e}")

print(f"\nTotal: {total} files, {ok} OK, {errs} warnings/errors")

# M7: this script had no asserts and always exited 0 — including when the
# gitignored recovered corpus was absent entirely, in which case it
# "passed" having parsed nothing at all. Both are now hard failures.
#
# RATCHET (M7). This sweep parses the ENTIRE recovered 1994 corpus, including
# base-game /U8/ sources that the Lost Vale build never compiles, so demanding
# zero warnings would be demanding fixes to files nobody ships. Instead the
# count is pinned and may only go DOWN — a NEW parse regression fails the
# build, a fix prompts you to lower the pin.
#
# Baseline 2026-07-25: 23 warnings/errors across 65 files, spread over
# /U8 (9, base-game sources — out of scope), /UNK files/UNK (9, dev tier) and
# /LOST VALE (2), plus 3 hard FAILs of which two are the documented
# known-unparseable 1994 files (EALOGO.UNK truncated block comment,
# TJORVI.UNK unterminated string — an early draft of TYORVI, which compiles
# fine and is what the build actually uses).
#
# Per-file ratcheting for the files that DO ship is build_eusecode.py Gate 7;
# this is the wider net.
#
# Lowered 2026-10-07 to 5: every compiled tier now parses clean. Left:
# EALOGO/TJORVI (the two hard FAILs above), U8/DARION.UNK (unterminated
# string at 2741), U8/CYRRUS.UNK:1975 (`foreach ... where (a) or (b)`, a
# loop-script OR) and U8/XAVIER.UNK:2027 (`"0" in askedList`, list
# membership). The last three are retail-only sources nothing compiles.
MAX_PARSE_ISSUES = 5

if total == 0:
    print("\nFAILED: no source files found — the recovered corpus "
          "(shared/data/lv-usecode/, gitignored) is missing, so this test "
          "verified nothing. Provide the corpus or skip this test "
          "explicitly.")
    sys.exit(1)

if errs > MAX_PARSE_ISSUES:
    print(f"\nFAILED: parse warnings/errors grew to {errs} "
          f"(pin {MAX_PARSE_ISSUES}). New regressions:")
    print(f"   files affected: {sorted(seen_names)}")
    sys.exit(1)
if errs < MAX_PARSE_ISSUES:
    print(f"\nNOTE: parse issues dropped to {errs} (pin {MAX_PARSE_ISSUES}) — "
          f"lower MAX_PARSE_ISSUES in test_parser_all.py to lock it in.")
print(f"\nOK: {errs} parse issue(s), at or below the pinned baseline "
      f"of {MAX_PARSE_ISSUES}.")

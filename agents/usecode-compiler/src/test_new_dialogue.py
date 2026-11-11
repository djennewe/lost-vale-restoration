#!/usr/bin/env python3
"""Test compilation of all new dialogue files."""
import sys
import os
import glob

sys.path.insert(0, os.path.dirname(__file__))
from u8c_driver import Driver

driver = Driver()
new_dir = os.path.join(os.path.dirname(__file__), 'lv-new')

total = 0
ok = 0
for path in sorted(glob.glob(os.path.join(new_dir, '*.UNK'))):
    total += 1
    result = driver.compile_file(path, verbose=True)
    if result.success:
        ok += 1

print(f"\nNew dialogue: {ok}/{total} compiled successfully")
driver.print_report()

# M6: used to exit 0 even when files failed to compile, so a broken new
# dialogue file passed CI//cleanroom silently.
if total == 0:
    print(f"FAILED: no .UNK files found in {new_dir}")
    sys.exit(1)
if ok != total:
    print(f"FAILED: {total - ok} of {total} new dialogue file(s) did not compile")
    sys.exit(1)

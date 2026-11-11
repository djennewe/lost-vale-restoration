#!/usr/bin/env python3
"""Debug the parsing of problematic lines."""
import sys
import re
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'usecode-disasm', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from u8_flex import UsecodeFlexArchive
from u8_usecode_disasm import UsecodeDisassembler
from u8_assembler import UsecodeAssembler

# Path resolution: relative to this file (repo root three levels up), same
# convention as lv_manifest.py.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

flx = UsecodeFlexArchive(os.path.join(REPO_ROOT, 'shared', 'data', 'USECODE.FLX'))
disasm = UsecodeDisassembler()
asm = UsecodeAssembler()
data = flx.get_class_data(0x50)
listing = disasm.disassemble_class(data, 0x50, 'HYDROS')

# Check: does `_parse_listing` actually skip the 00F3 line?
lines = listing.split('\n')
header_info = {}
event_table = {}
instructions = []

for line_num, line in enumerate(lines, 1):
    stripped = line.strip()
    if not stripped:
        continue

    # Check if this is one of our target offsets
    is_target = stripped.startswith('00F3:')

    # Reproduce the exact logic from _parse_listing
    m_header = re.match(
        r';\s*Header:\s*unknown1=([0-9A-Fa-f]+)\s+'
        r'total_size=([0-9A-Fa-f]+)\s+'
        r'unknown2=([0-9A-Fa-f]+)',
        stripped)
    if m_header:
        if is_target: print(f'  -> matched as header')
        continue

    m_event = re.match(
        r';\s*Event\s+([0-9A-Fa-f]+)\s*\(.*\):\s*offset\s+([0-9A-Fa-f]+)',
        stripped)
    if m_event:
        if is_target: print(f'  -> matched as event')
        continue

    if re.match(r'\.L[0-9A-Fa-f]+:', stripped):
        if is_target: print(f'  -> matched as label')
        continue

    if re.match(r';\s*─', stripped):
        if is_target: print(f'  -> matched as event separator')
        continue

    if stripped.startswith(';'):
        if is_target: print(f'  -> matched as comment')
        continue

    if 'db' in stripped:
        if is_target: print(f'  -> matched as db')
        continue

    m_instr = re.match(
        r'([0-9A-Fa-f]{4}):\s+'
        r'((?:[0-9A-Fa-f]{2}\s?)+)'
        r'\s+'
        r'(.+)',
        stripped)
    if not m_instr:
        if is_target:
            print(f'  -> DID NOT match instruction regex')
            print(f'     line: {repr(stripped[:100])}')
        continue

    if is_target:
        print(f'  -> matched as instruction: offset=0x{m_instr.group(1)}, hex=[{m_instr.group(2).strip()[:40]}]')
        instructions.append(True)

# Actually, let me check if the issue is the `if 'db' in stripped` check
# The string "Goodbye. " doesn't contain "db", so that shouldn't be the issue
# Let me check what `stripped` looks like for a line containing hex bytes with "db" in them

# Actually, wait: `'db' in stripped` is True for many lines!
# E.g., "0D 09 00 47 6F 6F 64 62 79 65 2E 20 00 push string..."
# has "64 62" = "db" in the hex bytes!

print("\n\nChecking 'db' substring issue:")
count_db = 0
for line in listing.split('\n'):
    stripped = line.strip()
    if not stripped or stripped.startswith(';') or stripped.startswith('.L'):
        continue
    if re.match(r'[0-9A-Fa-f]{4}:', stripped) and 'db' in stripped:
        count_db += 1
        if count_db <= 5:
            print(f'  "db" found in: {stripped[:100]}')

print(f'\nTotal instruction lines with "db": {count_db}')

# usecode-disasm — Development Log

## Session 1 — 2026-03-20: Format Research + Disassembler Build

### Task A1: Research U8 usecode bytecode format ✓

Fetched and analyzed the complete Pentagram engine source for usecode handling.
Key files examined:

- `usecode/UCMachine.cpp` — Complete VM interpreter with all ~80 opcodes
- `usecode/UCMachine.h` — VM class definition, pointer segment types
- `usecode/UCProcess.cpp` — Process model (stack frame layout, call/ret)
- `usecode/UCStack.h` — Little-endian stack implementation
- `usecode/Usecode.cpp` — Class event lookup (U8 vs Crusader differences)
- `usecode/UsecodeFlex.cpp` — FLX-based usecode loading, name table access
- `filesys/FlexFile.cpp` — FLX archive format (header validation, index)
- `convert/u8/ConvertUsecodeU8.h` — Complete intrinsic table (258 entries), event names, class header parsing
- `convert/Convert.h` — Opcode reader with operand sizes, debug symbol parsing
- `tools/fold/Folder.cpp` — Decompiler/folder (not needed for disassembly, but informative)
- `tools/disasm/DisasmProcess.cpp` — Pentagram's own disassembler harness

Key findings:
- FLX format: 0x80-byte header, then 8-byte index entries (offset+size)
- USECODE.FLX: entry 0 unused, entry 1 = name table, entries 2+ = classes
- U8 class header: 12 bytes (3×uint32), then 32×uint32 event table, then bytecode
- Base offset for U8 is always 0x0C
- 32 events per class (look, use, anim, setActivity, cachein, hit, gotHit, ...)
- Stack-based VM with little-endian data stack, BP/IP, temp/result registers
- Global state is a 0x1000-byte bit-field addressed by bit offset
- ~80 opcodes covering stack manipulation, arithmetic, control flow, process management
- 258 intrinsic functions for game engine interaction

Output: `agents/usecode-disasm/docs/usecode-format.md` — comprehensive format spec.

### Task A2: Build FLX reader ✓

Built `src/u8_flex.py`:
- `FlexArchive` — general FLX reader with header validation
- `UsecodeFlexArchive` — subclass knowing about USECODE.FLX layout
  - Name table parsing (13-byte records, 9-byte names)
  - Class ID → FLX index mapping (classid + 2)
  - Iterators for all classes and names

### Task A3: Build core disassembler ✓

Built `src/u8_usecode_disasm.py`:
- Complete opcode table with operand formats for all ~80 U8 opcodes
- Full U8 intrinsic table (258 entries) for symbolic names
- `UsecodeClass` — parses class header, event table, extracts bytecode
- `UsecodeDisassembler` — core disassembly engine:
  - Reads opcode + operands from bytecode stream
  - Generates `Instruction` objects with offset, mnemonic, operands, comments
  - Handles special cases: string literals, debug symbols, jump target resolution
  - `disassemble_class()` — full formatted listing with event labels
  - `disassemble_class_summary()` — extracts intrinsic calls, cross-references, strings
- CLI interface for single class, all classes, or summary mode

### Task A4: Validate against base game USECODE.FLX ✓

USECODE.FLX was already available (populated by corpus-builder). Full validation:
- 516 non-empty classes, 238,357 instructions disassembled
- **Zero errors, zero unknown opcodes**
- Cross-validated DOOR_NS (complex door logic), HYDROS (major NPC), KEY (lock mechanism)
- All opcode operand sizes correct, event tables parsed properly
Output: `agents/usecode-disasm/docs/validation-notes.md`

### Task A5: Build base game symbol table ✓

Generated `shared/corpus/usecode-index/base-game-symbols.yaml`:
- All 516 classes with names, events, intrinsic calls, cross-references
- 182 unique intrinsics used (of 258 defined)
- 445 unique global bit-fields accessed
- All strings extracted per class

### Task B1: Check LV usecode availability ✓

`shared/data/lv-usecode.zip` was already present (539 KB).

### Task B2: Catalog LV usecode snapshot ✓

**CRITICAL DISCOVERY:** The .UNK files are **original U8 usecode SOURCE CODE**
from Origin Systems — not compiled bytecode! 67 files, ~60K lines of developer
source code including full dialogue, variable names, developer comments, and
localization markers.

Three directory versions:
- `LOST VALE/` (11 files) — LV-specific new classes
- `U8/` (23 files) — modified base game classes
- `UNK files/UNK/` (33 files) — merged/complete working set

Output: `agents/usecode-disasm/docs/lv-snapshot-inventory.md`

### Task B3: Disassemble LV usecode — N/A

Not applicable — the files are source code, not compiled bytecode.
The disassembler is validated and ready if compiled bytecode is ever found.

### Task B4: Cross-reference LV vs base game ✓

Generated `shared/corpus/usecode-index/lv-cross-reference.yaml`:
- 23 LV-only classes (new content)
- 10 modified base game classes
- 631 global flags defined
- 106 Type* references identified
- 17 "uses" library references

### Task B5: Final analysis ✓

Generated `shared/corpus/usecode-index/lv-analysis-final.md`:
- Complete character catalog (9 new NPCs, 11 modified base NPCs)
- Item inventory (Shield of the Ancients, Bush Key, potions, etc.)
- Quest structure from 631 global flags
- Puzzle mechanics (Passage Test, Moot/Shade scene, Candle Trick, Magnetic puzzle)
- Lord British message scene (full dialogue)
- Air magic system (AIRSPEL.UNK, 10 spell functions)
- Localization evidence (German/French translation markers)
- Developer comments and internal naming conventions

## Status: ALL TASKS COMPLETE

All Track A and Track B tasks are finished. The usecode-disasm agent has:
1. Built a validated disassembler (0 errors on 238K instructions)
2. Produced a complete base game symbol table
3. Discovered that the LV snapshot is SOURCE CODE (not bytecode)
4. Produced comprehensive analysis of the LV content
5. Generated cross-references between LV and base game

# Usecode Compiler Development Log

## Session 1 — Track A: Assembler + Round-Trip

### A1: Assembler Core (`u8_assembler.py`)
Built a complete assembler that parses disassembly listings produced by `u8_usecode_disasm.py`.

Key design decisions:
- Two assembly modes: raw-hex (round-trip) and operand-based (codegen)
- Regex-based listing parser extracts header, event table, and instructions
- Event table regex uses `\(.*\)` not `\([^)]*\)` for nested parens like `look()`
- Opcode disambiguation uses raw hex byte as authoritative source
- String encoding handles uint16 length + data + null terminator

### A2: Round-Trip Validation
**Result: 516/516 classes pass (ZERO byte differences)**

Bugs found and fixed:
1. Event table regex `\([^)]*\)` failed on `look()` — nested parens. Fixed with `\(.*\)`.
2. `if 'db' in stripped` check accidentally matched hex bytes `64 62` in strings
   like "Goodbye" (`47 6F 6F 64 62 79 65`). Removed the check entirely.

### A3: FLX Packer (`u8_flx_packer.py`)
Built tool to create/modify EUSECODE.FLX archives.

### A4: Name Table Tool
Integrated into FLX packer — can create/extend name tables for LV classes.

### Round-Trip Results Document
See `docs/roundtrip-results.md` for the full validation report.

## Session 2 — Track B: Compiler

### B1: Lexer (`u8c_lexer.py`)
Full tokenizer handling all UNK language constructs:
- Keywords, operators, delimiters, string literals, numbers
- Multi-line strings with `\f` and `\g` language markers
- `#if English/French/German` preprocessor directives
- `[[PT_DEFAULT, referent]]` process type annotations
- Tested on all 65 UNK files successfully

### B2: Parser + AST (`u8c_parser.py`, `u8c_ast.py`)
Recursive descent parser producing 35+ AST node types:
- Class declarations (npcclass/eggclass/typeclass inherits)
- Process/routine definitions with startup/process blocks
- foreach, switch/case, for, while, if/else
- Bare routines (no class qualifier)
- 39/65 UNK files parse cleanly; all primary LV files parse

### B3: Symbol Table (`u8c_symbols.py`)
- 258 intrinsic functions loaded from the disassembler
- 516 base game class IDs loaded from EUSECODE.FLX
- 32 event IDs (look, use, hatch, schedule, etc.)
- Global flag allocation system
- Intrinsic lookup by name and class context

### B4: Code Generator (`u8c_codegen.py`)
AST -> bytecode generation:
- bark(): push pid, push string, str_to_ptr, push this, calli 0x0049
- wait(): spawn FREE class wait process
- if/else: jne + jmp with label fixups
- while/for: loop labels + condition + body + jmp
- switch/case: strcmp chains
- Variable allocation with BP offsets
- Standard process preamble (init + set info + process exclude)

### B6: Driver (`u8c_driver.py`)
Full compilation pipeline:
- Parse -> symbol resolution -> codegen -> bytecode
- Compile all files in a directory
- Build EUSECODE.FLX from compiled classes

### B7-B9: Compilation Results
- **36/44** LV source files compile successfully
- **133KB** of bytecode generated
- MONSKUL (28 lines), PLNTST (68 lines), LORDBRIT (130 lines): all compile
- RAGNAR (944 lines, MVP gate): compiles (21KB bytecode)
- THORDIS (1500+ lines): compiles (35KB bytecode)
- Remaining failures: jump overflow on largest files, source file issues

## Session — M0.6: savegame-visible id/flag manifest (2026-07-03)

Implemented the manifest design (docs/manifest-design.md) as signed off.

### What landed
- `lv_manifest.py`: load/save/validate of `shared/build/lv_manifest.json`
  (schema per design doc section 3; deterministic sorted-key serialization).
- `u8c_symbols.py`: `SymbolTable.load_manifest()`, pin-aware
  `allocate_global_flag()` (pinned name returns the pin, raises
  `ManifestError` on width mismatch; unpinned allocates at the cursor and
  records into `new_allocations`), `check_new_allocations()` invariant.
- `build_eusecode.py`: loads the manifest at start (missing manifest =
  bootstrap mode), consults class-id pins, appends new pins on a successful
  real build with a `MANIFEST: appended N new pins` block, fails loudly
  (M0.4 mechanism) on any pin conflict. Temp-path builds never write the
  manifest or detection_tables.h.
- `test_manifest.py`: 5/5 — order independence (reversed compile order,
  byte-identical FLX), append-at-cursor with no pin movement, duplicate
  bit, width mismatch, class id collision (allocator path and structural
  validate() path).

### SAVEGAME RESET
Bootstrap rebased every LV global flag into the reserved window at bit
1024+ (design doc section 2): lbDone moved 678 -> 1702 (0x6A6),
mythranIntroDone -> 1819 (0x71B), mythranStockVisit -> 1820 (0x71C).
All pre-M0.6 savegames are stale. This is the one planned reset, done
while savegames are still throwaway. 645 flag pins (583 marked
retail_shared pending the M1 flag-graph recovery), 22 class pins,
next_free = bit 1827 / class 1453.

### Three latent defects found and fixed on the way
1. **NEW_CLASS_START = 0x0260 overwrote live base classes.** The base FLX
   is a dense class table out to id 1430; 0x0260 (608) is DEMNSTAT, and
   every prior --full build silently clobbered it and ~27 neighbors with
   new LV classes. New classes now start at 1431 (0x0597), one past the
   base game's highest used id.
2. **Dev-dir dedup compared class names to file basenames.** CANTRK,
   MONSKUL, PLNTST, and TESTPLAN exist in both LOST VALE/ and
   UNK files/UNK/ and were compiled twice, each copy getting its own class
   id under the same name. Dedup is now by source basename.
3. **`_find_safe_insertion()` in u8c_codegen.py misparsed 0x0D operand
   bytes as string opcodes.** Any 16-bit operand containing 0x0D (e.g. a
   manifest-window flag bit offset like 1293 = 0x50D) desynced the scan,
   relay blocks got planned tens of KB off target, and ATLI (36 KB once
   the manifest killed its push-0 fallbacks) failed with "Failed to
   resolve jumps after 10 trampoline passes". The emitter now records
   string-literal ranges at emission time and keeps them shifted in sync
   during trampoline insertion.

### Verification
- Bootstrap build and subsequent manifest builds byte-identical
  (md5 018cb27834f2ae6ca5da4e84f12da591); build exits 0.
- md5-5000 d1287b302cb16d28a55dc94a49d62f21, size 1,420,514 — new
  detection entry applied to scummvm-lv/detection_tables.h (relink
  scummvm-lv before the next in-game run or detection fails).
- test_roundtrip.py 516/516; test_patch_mythran.py 4/4;
  test_parser_all.py unchanged.

## Session — M1 shared-flag migration, first two flags (2026-10-08)

Douglas approved breaking saves for these two bits.

### What moved
- `araminaSchedule` (2 bits) 1635 (0x663) → 519 (0x207). Retail MORDEA
  0x0407 writes 0207h at 0270/0420/05C6 (at_home/on_throne/chow_down), and
  retail ARAMINA 0x040D reads it. Our ARAMINA read 0x663, which nothing in
  normal play writes, so she idled.
- `devonInRule` 1206 (0x4B6) → 88 (0x58). Retail LOGBOOK4 0x057E writes it
  at 1032 (next to toranDead 0x57), retail AVATAR's afterEarth cheat at
  33F5, and 24 retail classes read it. Our ARAMINA's three reads and our
  AVATAR's cheat write were on 0x4B6.
- The old pins stay as `araminaSchedule_1635` and `devonInRule_1206` with
  `"retired": true`. `lv_manifest.validate()` now fails the build on a live
  pin that overlaps a retired range, and the `next_free.global_bit` check
  covers retired ranges too. Before this change validate() skipped retired
  entries entirely, so nothing stopped a hand-edit reusing one.

### SAVEGAME BREAK (these two bits only)
A save written before this build keeps any value it set at 0x663/0x4B6,
where nothing reads it now. It reads 0x207/0x58 from what retail code
wrote there.

### Verification
- Only ARAMINA 0x040D (20 bytes, 10 operands) and AVATAR 0x0401 (2 bytes,
  1 operand) changed. No global operand on 0x663/0x4B6 remains in the
  built FLX. MORDEA, LOCKDOOR and LOGBOOK4 are still byte-identical to
  retail.
- EUSECODE.FLX sha256 1ca0e93b… → 6d523e07… (md5 0e56f23d…, size
  unchanged 1,524,731). The other three artifacts are unchanged.
- test_symbol_retail_pins.py and test_manifest.py
  (test_conflict_retired_bit_reuse) both fail on the pre-change manifest.

## Session — M1 shared-flag migration, the rest of ARAMINA (2026-10-09)

Douglas: migrate ARAMINA's retail-shared flags only.

### How the set was found
Disassembled our built ARAMINA 0x040D and retail's (EUSECODE.FLX.bak).
Both have exactly 39 push/pop global operands, in the same order: the
class compiles from the same 1994 source (`U8/ARAMINA.UNK` is a Word
copy of `UNK files/UNK/ARAMINA.UNK`). Zipping them gives one retail bit
per name, with no conflicts. Besides the two moved on 2026-10-08, eleven
names were still on LV bits:

| name | old | retail | w | retail ARAMINA | other retail users |
|---|---|---|---|---|---|
| araminaMet | 0x65F | 0x203 | 1 | W 1633, R 0600/06A1/0727/081F/133B/144F | ORLOK R 962C ("Tell me of Aramina.") |
| araminaName | 0x660 | 0x204 | 1 | W 16C6, R 00C2/00FA/1637 | none |
| araminaJob | 0x661 | 0x205 | 1 | W 174A, R 00C6/0124 | none |
| somebodyTalking | 0x46D | 0x0F | 1 | R 04FD | METHOD W 0E49/108A (1) 10F1 (0); 23 classes |
| hearTruthActive | 0x485 | 0x27 | 1 | R 1B82/1C6D/2188/23D4 | AIRSPEL W 2E7E/2E9D; ORLOK, CYRRUS, XAVIER R |
| hydrosFree | 0x494 | 0x36 | 2 | R 1556 | HYDROS W 152C, ERTHSPEL W 0BEF; 24 readers |
| hasHeart | 0x49A | 0x3C | 1 | R 1164 | 18 readers, no writer anywhere |
| lothianDead | 0x51D | 0xBF | 1 | R 1524/1590 | VIVIDOS W 0F57 ("…the Necromancer… I am he"), AVATAR W 33FB |
| toldDagger | 0x534 | 0xD6 | 1 | R 1520/158C | VIVIDOS W 49E4 ("Mordea keeps the dagger…") |
| mordeaDead | 0x576 | 0x11A | 1 | R 3916 | GWILLIM, KILANDRA, VIVIDOS, TORWIN R; no writer anywhere |
| toldOfTreasure | 0x5A3 | 0x147 | 1 | R 1418/14EC/16F2 | ORLOK W 4560 ("Tell me about lost treasures.") |

Name checks beyond ARAMINA: compiling the recovered `U8/TORWIN.UNK`,
`U8/MORDEA.UNK` and `U8/SALKIND.UNK` against the manifest gives global
sequences that zip one-for-one with retail TORWIN/MORDEA/SALKIND, and put
mordeaDead on 0x11A, hydrosFree on 0x36 and somebodyTalking on 0x0F. The
other writers are labelled by their own dialogue strings (column above).
The 2026-10-08 batch-B report paired mordeaDead with 0x147 and hasHeart
with 0x0F. Those pairings came from operand order, and they are wrong:
0x147 is toldOfTreasure and 0x0F is somebodyTalking.

No live or retired pin overlaps any of the eleven retail ranges. In the
built FLX the only classes besides ARAMINA that touch those ranges are
retail bytes and the patched MYTHRAN, whose operands there match retail.
The only other LV class on an old bit was AVATAR: the afterEarth cheat's
`lothianDead = 1` (`lv-patched/AVATAR.UNK:1136`, 310E). It now writes
0xBF, the bit retail AVATAR's cheat writes at 33FB.

### SAVEGAME BREAK (these eleven bits)
Values at the old bits are ignored, and the retail bits are read. None
of the 110 saves in `~/lv-checkpoints` has any of the old bits set.
Retail code had been writing the retail bits all along, so an old save
gets correct state. The exception is araminaMet/Name/Job (0x203-0x205),
which only ARAMINA writes: a player who met her on an older build is
greeted as a stranger once.

### Verification
- Only ARAMINA 0x040D (29 operands) and AVATAR 0x0401 (1 operand)
  changed. Class lengths and disassembly line counts are unchanged, and
  no other line changed. Our ARAMINA's 39 global operands now equal
  retail's. No global operand on any retired bit remains in the built
  FLX.
- EUSECODE.FLX sha256 29fb0c29… → 91ce0871…. Size is unchanged at
  1,525,384, and md5-of-first-5000 is unchanged at cd847392…, so
  build_scummvm.sh's detection values still hold. The other four
  artifacts are unchanged.
- test_symbol_retail_pins.py: 279/279. Against the pre-change manifest
  it fails 45 checks, including the new check that compiles
  ARAMINA.UNK and compares its global operands with retail 0x040D.

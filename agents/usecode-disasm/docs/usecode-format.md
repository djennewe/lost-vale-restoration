# Ultima 8 Usecode Bytecode Format Specification

Reconstructed from the Pentagram engine source (pentagram-u8/pentagram).
Primary sources: `usecode/UCMachine.cpp`, `usecode/UsecodeFlex.cpp`,
`convert/u8/ConvertUsecodeU8.h`, `convert/Convert.h`, `filesys/FlexFile.cpp`.

## FLX Container Format

All U8 data files (including USECODE.FLX) use the FLX archive format.

### FLX Header

| Offset | Size | Description |
|--------|------|-------------|
| 0x00 | 0x52 | Title/comment text, terminated and padded with 0x1A bytes |
| 0x52 | 2 | (padding) |
| 0x54 | 4 | Entry count (uint32 LE) |
| 0x58 | 0x28 | Reserved/padding |
| 0x80 | 8×N | Index table: N entries of (uint32 offset, uint32 size) |

### FLX Validation

A valid FLX file has the title area (bytes 0x00–0x51) containing ASCII text
terminated by 0x1A, with all remaining bytes through 0x51 also being 0x1A.

### Index Table

Each entry is 8 bytes at `0x80 + 8*index`:
- **Offset** (uint32 LE at `0x80 + 8*i`): byte offset of the object data
- **Size** (uint32 LE at `0x84 + 8*i`): byte size of the object data

An entry with size 0 is empty/unused.

## USECODE.FLX Structure

The USECODE.FLX file is a FLX archive with the following layout:

| FLX Index | Content |
|-----------|---------|
| 0 | (unused/unknown) |
| 1 | **Name table** — class names for all usecode classes |
| 2 | Class 0x0000 bytecode |
| 3 | Class 0x0001 bytecode |
| ... | ... |
| N+2 | Class N bytecode |

**Class ID to FLX index:** `flx_index = classid + 2`

### Name Table (FLX index 1)

| Offset | Size | Description |
|--------|------|-------------|
| 0 | 4 | Header (unknown purpose) |
| 4 | 13×N | N name records, one per class |

Each name record is 13 bytes:
- Up to 9 bytes of null-terminated ASCII class name
- 4 bytes of additional data (purpose unknown, possibly padding)

The name at `offset 4 + classid * 13` is the class name for the given class ID.

## Usecode Class Format (U8-specific)

Each class entry in USECODE.FLX contains a self-contained bytecode module.

### Class Header (12 bytes)

| Offset | Size | Description |
|--------|------|-------------|
| 0x00 | 4 | Unknown uint32 |
| 0x04 | 4 | Total data size including header (actual bytecode size = this − 0x0C) |
| 0x08 | 4 | Unknown uint32 |

### Event Table (128 bytes, starting at offset 0x0C)

The **base offset** for U8 classes is always `0x0C`.

Starting at offset 0x0C, there are exactly **32 event entries**, each a uint32 LE
offset. These offsets are relative to the base offset (0x0C).

| Event | Name | Used? |
|-------|------|-------|
| 0x00 | look() | Yes |
| 0x01 | use() | Yes |
| 0x02 | anim() | Rare |
| 0x03 | setActivity() | Yes |
| 0x04 | cachein() | Yes |
| 0x05 | hit(uword, word) | Yes |
| 0x06 | gotHit(uword, word) | Yes |
| 0x07 | hatch() | Yes |
| 0x08 | schedule() | Rare |
| 0x09 | release() | Rare |
| 0x0A | equip() | Rare |
| 0x0B | unequip() | Rare |
| 0x0C | combine() | Rare |
| 0x0D | func0D | Unknown |
| 0x0E | calledFromAnim() | Rare |
| 0x0F | enterFastArea() | Yes |
| 0x10 | leaveFastArea() | Rare |
| 0x11 | cast(uword) | Rare |
| 0x12 | justMoved() | Rare |
| 0x13 | AvatarStoleSomething(uword) | Rare |
| 0x14 | animGetHit() | Rare |
| 0x15 | guardianBark(word) | Yes |
| 0x16–0x1F | (undefined/reserved) | No |

An event offset of 0 means the event handler is not defined for this class.

Event offsets point to positions within the bytecode area (relative to base
offset 0x0C). Since the event table itself occupies bytes 0x00–0x7F relative
to base offset, meaningful event offsets are >= 0x80.

### Bytecode Area

Bytecode starts at the end of the event table (base_offset + 0x80 = raw offset
0x8C in the class data). Each function/event handler consists of a sequence of
opcodes terminated by `ret` (0x50).

The class itself ends with opcode 0x79 (U8 end-of-function marker).

## VM Architecture

The U8 usecode VM is a **stack-based virtual machine** with:

- **Data stack**: Little-endian, grows downward. Default size 0x1000 bytes.
- **BP (Base Pointer)**: Points to the current stack frame base.
- **IP (Instruction Pointer)**: Offset within current class bytecode.
- **Temp register** (`temp32`): 32-bit register for return values and intrinsic results.
- **Result register** (`result`): 32-bit register for process results.
- **Global bit-field**: 0x1000-byte (32768-bit) shared global state, addressed by bit offset.

### Stack Frame Layout

When a function is called via opcode 0x11 (call):
```
[BP+06] = this pointer (if present, 4 bytes)
[BP+04] = previous classid (uint16)
[BP+02] = previous IP (uint16)
[BP+00] = previous BP (uint16)
[BP-01...] = local variables (allocated by opcode 0x5A init)
```

Arguments are pushed before the call; the this pointer (if any) is pushed last.

### Pointer Types (32-bit segmented pointers)

| Segment | Meaning |
|---------|---------|
| 0x0000 | NULL |
| 0x0001–0x7FFE | Stack segment (segment = process ID) |
| 0x8000 | String heap |
| 0x8001 | List heap |
| 0x8002 | Object reference |
| 0x8003 | Global variable area |

Format: `(segment << 16) | offset`

## Opcode Reference

All multi-byte values are **little-endian**. Operand abbreviations:
- `bp(xx)` = signed 8-bit offset from BP: `[BP + (sint8)xx]`
- `sp(xx)` = signed 8-bit offset from SP: `[SP + (sint8)xx]`

### Pop/Store Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 00 | xx | pop byte [BP+xx] | Pop 16-bit, store low 8 bits at [BP+xx] |
| 01 | xx | pop [BP+xx] | Pop 16-bit into [BP+xx] |
| 02 | xx | pop dword [BP+xx] | Pop 32-bit into [BP+xx] |
| 03 | xx yy | pop huge [BP+xx] yy | Pop yy bytes into [BP+xx] |
| 08 | — | pop result | Pop 32-bit into process result register |
| 09 | xx yy zz | assign elem [BP+xx] yy zz | Pop yy bytes into list element; zz=slist flag |

### Push Constant Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 0A | xx | push byte xx | Push sign-extended 8-bit value as 16-bit |
| 0B | xxxx | push xxxx | Push 16-bit value |
| 0C | xxxxxxxx | push dword xxxxxxxx | Push 32-bit value |
| 0D | xxxx str 00 | push string "str" | Push string of length xxxx, null-terminated |
| 0E | xx yy | create list xx yy | Pop yy values of size xx, push as list |

### Call Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 0F | xx yyyy | calli xx yyyy | Intrinsic call; xx=arg bytes, yyyy=intrinsic ID |
| 11 | xxxx yyyy | call xxxx:yyyy | Call class xxxx at offset yyyy |
| 12 | — | pop temp | Pop 16-bit into temp register |
| 13 | — | pop long temp | Pop 32-bit into temp register |

### Arithmetic Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 14 | — | add | 16-bit add |
| 15 | — | add long | 32-bit add |
| 16 | — | concat | Concatenate two strings |
| 17 | — | append | Append two lists |
| 19 | xx | union slist | Union two string lists (xx=elem size) |
| 1A | xx | subtract slist | Subtract string list (xx=elem size) |
| 1B | xx | subtract list | Subtract list (xx=elem size) |
| 1C | — | sub | 16-bit subtract |
| 1D | — | sub long | 32-bit subtract |
| 1E | — | mul | 16-bit multiply |
| 1F | — | mul long | 32-bit multiply |
| 20 | — | div | 16-bit divide |
| 21 | — | div long | 32-bit divide |
| 22 | — | mod | 16-bit modulo |
| 23 | — | mod long | 32-bit modulo |

### Comparison Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 24 | — | cmp | 16-bit equals |
| 25 | — | cmp long | 32-bit equals |
| 26 | — | strcmp | String compare (frees both strings) |
| 28 | — | lt | 16-bit less than |
| 29 | — | lt long | 32-bit less than |
| 2A | — | le | 16-bit less or equal |
| 2B | — | le long | 32-bit less or equal |
| 2C | — | gt | 16-bit greater than |
| 2D | — | gt long | 32-bit greater than |
| 2E | — | ge | 16-bit greater or equal |
| 2F | — | ge long | 32-bit greater or equal |

### Boolean Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 30 | — | not | 16-bit boolean NOT |
| 31 | — | not long | 32-bit boolean NOT |
| 32 | — | and | 16-bit boolean AND |
| 33 | — | and long | 32-bit boolean AND |
| 34 | — | or | 16-bit boolean OR |
| 35 | — | or long | 32-bit boolean OR |
| 36 | — | ne | 16-bit not-equal |
| 37 | — | ne long | 32-bit not-equal |

### List Test Opcode

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 38 | xx yy | in list xx yy | Test if element (size xx) is in list; yy=slist flag |

### Bitwise Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 39 | — | bit_and | 16-bit bitwise AND |
| 3A | — | bit_or | 16-bit bitwise OR |
| 3B | — | bit_not | 16-bit bitwise NOT |
| 3C | — | lsh | 16-bit left shift |
| 3D | — | rsh | 16-bit right shift |

### Push Variable Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 3E | xx | push byte [BP+xx] | Push byte var as 16-bit |
| 3F | xx | push [BP+xx] | Push 16-bit var |
| 40 | xx | push dword [BP+xx] | Push 32-bit var |
| 41 | xx | push string [BP+xx] | Push string var (duplicates string) |
| 42 | xx yy | push list [BP+xx] yy | Push list with yy-size elements (duplicates) |
| 43 | xx | push slist [BP+xx] | Push string list var (duplicates) |
| 44 | xx yy | push element xx yy | Push indexed element from list; yy=slist flag |
| 45 | xx yy | push huge [BP+xx] yy | Push yy bytes from [BP+xx] |

### Pointer Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 4B | xx | push addr [BP+xx] | Push 32-bit pointer to [BP+xx] |
| 4C | xx | push indirect xx | Deref pointer, push xx bytes |
| 4D | xx | pop indirect xx | Deref pointer, pop xx bytes into location |

### Global Variable Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 4E | xxxx yy | push global [xxxx] yy | Push global bit-field at offset xxxx, yy bits |
| 4F | xxxx yy | pop global [xxxx] yy | Pop into global bit-field at offset xxxx, yy bits |

### Control Flow Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 50 | — | ret | Return from function (or terminate process) |
| 51 | xxxx | jne xxxx | Relative jump if top-of-stack is false (0) |
| 52 | xxxx | jmp xxxx | Unconditional relative jump |
| 53 | — | suspend | Yield execution (cede timeslice) |
| 54 | xx yy | implies xx yy | Link two processes (always 01 01) |

### Process Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 57 | aa tt xxxx yyyy | spawn aa tt xxxx:yyyy | Spawn process; aa=arg bytes, tt=this size |
| 58 | xxxx yyyy zzzz tt uu | spawn inline | Spawn inline process at class:offset+delta |
| 59 | — | push pid | Push current process ID |

### Function Init

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 5A | xx | init xx | Allocate xx bytes of local variables (zeroed) |

### Debug Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 5B | xxxx | line xxxx | Source line number |
| 5C | xxxx str 00 | symbol xxxx "name" | Debug symbol info; xxxx=offset to debug data |

### Return Value Push

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 5D | — | push byte retval | Push low 8 bits of temp as 16-bit |
| 5E | — | push retval | Push low 16 bits of temp |
| 5F | — | push long retval | Push full 32-bit temp |

### Type Conversion

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 60 | — | int to long | Sign-extend 16-bit to 32-bit |
| 61 | — | long to int | Truncate 32-bit to 16-bit |

### Memory Management

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 62 | xx | free string [BP+xx] | Free string at [BP+xx] |
| 63 | xx | free slist [BP+xx] | Free string list at [BP+xx] |
| 64 | xx | free list [BP+xx] | Free list at [BP+xx] |
| 65 | xx | free string [SP+xx] | Free string at [SP+xx] |
| 66 | xx | free list [SP+xx] | Free list at [SP+xx] |
| 67 | xx | free slist [SP+xx] | Free string list at [SP+xx] |

### String/Pointer Conversion

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 69 | xx | str to ptr [BP+xx] | Push string at [BP+xx] as 32-bit pointer |
| 6B | — | str to ptr | Pop string ref, push as 32-bit pointer |
| 6C | xx yy | param pid chg xx yy | Copy string/list for spawned process; yy=type |

### Result and Stack Manipulation

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 6D | — | push process result | Push 32-bit process result register |
| 6E | xx | add sp xx | Adjust stack pointer by -(sint8)xx bytes |
| 6F | xx | push addr [SP-xx] | Push 32-bit pointer to [SP - (sint8)xx] |

### Loop Opcodes

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 70 | xx yy zz | loop xx yy zz | Init object search loop; xx=var, yy=script size, zz=type |
| 73 | — | loopnext | Advance to next loop item; push false if done |
| 74 | xx | loopscr xx | Append byte to loop script |
| 75 | xx yy zzzz | for each xx yy zzzz | Iterate list; xx=var, yy=elem size, zzzz=end offset |
| 76 | xx yy zzzz | for each str xx yy zzzz | Same as 75 but for string lists |

### Loop Search Types (opcode 0x70 parameter zz)

| Type | Description |
|------|-------------|
| 2 | Area search around object |
| 3 | Area search, recursive into containers |
| 4 | Container search |
| 5 | Container search, recursive |
| 6 | Surface search |

### Info/Exclude

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 77 | — | set info | Pop item number and process type from stack |
| 78 | — | process exclude | Terminate if another process has same (item, type) |

### End of Function

| Op | Operands | Mnemonic | Description |
|----|----------|----------|-------------|
| 79 | — | end | End of function (U8 only; equivalent to 0x7A) |
| 7A | — | end | End of function (Crusader; also used internally for U8) |

## Intrinsics Table (U8)

There are 0x102 intrinsic functions (IDs 0x0000–0x0101). The full list is
defined in `ConvertUsecodeU8::_intrinsics[]` in `convert/u8/ConvertUsecodeU8.h`.
Selected key intrinsics:

| ID | Signature |
|----|-----------|
| 0x0000 | process target() |
| 0x000D | uword Item::getType() |
| 0x000F | uword Item::getFrame() |
| 0x0010 | void Item::setFrame(uword frame) |
| 0x0011 | uword Item::getQuality() |
| 0x0025 | Item::overlaps(uword) |
| 0x0031 | Item::legal_create(uword, uword, uword, uword, uword) |
| 0x0032 | Item::create(uword, uword) |
| 0x003A | Item::destroy() |
| 0x0042 | Item::isNpc() |
| 0x0049 | process Item::bark(char* str) |
| 0x004A | strptr process Item::ask(uword slist) |
| 0x005C | process Item::look() — calls event 0x0 |
| 0x005D | process Item::use() — calls event 0x1 |
| 0x008C | Npc::isDead() |
| 0x009C | Npc::getDir() |
| 0x009F | process Npc::doAnim(AnimSet, word, word, ubyte) |
| 0x00A1 | process Npc::pathfind(uword, uword, uword, uword) |
| 0x00A2 | process Npc::pathfind(uword, uword) |
| 0x00AE | process Npc::cSetActivity(Activity) |
| 0x00B5 | process Camera::scrollTo(uword, uword, ubyte, word) |
| 0x00B6 | urandom(word) |
| 0x00B9 | numToStr(uword) |
| 0x00BB | playMusic(byte) |
| 0x00BC | getName() — returns Avatar's name |
| 0x00CC | process teleportToEgg(word, word, ubyte) |
| 0x00DE | process FadeToBlack() |
| 0x00DF | process FadeFromBlack() |
| 0x00EC | playSFX(word) |

(Full table: 258 entries. See `ConvertUsecodeU8::_intrinsics[]` in source.)

## Debug Symbol Format

Some classes include debug symbol information (from the original compiler).

- Opcode 0x5C stores the offset to the debug data and the class name (9 bytes).
- At the debug offset, there is a debug symbol table:
  - uint8 count
  - For each symbol:
    - uint8 unknown1
    - uint8 type
    - uint8 unknown2 (BP offset for the variable)
    - uint8 unknown3
    - null-terminated string (variable name)
- Opcode 0x7A (end) follows the debug data.

## References

- Pentagram source: https://github.com/pentagram-u8/pentagram
- DominusExult fork: https://github.com/DominusExult/pentagram
- ScummVM (current home): https://github.com/scummvm/scummvm (engines/ultima/ultima8/)

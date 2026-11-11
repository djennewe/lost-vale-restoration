# Pentagram docs vs the live ScummVM engine

Cross-check run **2026-07-25** against the ScummVM checkout at
`scummvm-lv/engines/ultima/ultima8/`.

**Rule for this project: ScummVM wins.** Pentagram's documents are historical
notes from 1996 to 2005, written before a working engine existed. Where they
disagree with the engine that actually runs our build, the engine is correct
by definition, because it is the thing executing our bytes.

Line references are `file:line`. ScummVM paths are relative to
`scummvm-lv/engines/ultima/ultima8/`. Our paths are relative to the repo root.
Line numbers cited for pinned Pentagram source files (`convert-Convert.h.txt`
and friends) are **upstream** line numbers; add 7 to locate them in the pinned
copy, which carries a 7-line provenance header.

Every row is marked **VERIFIED** (checked against source or against real game
data in this session) or **CLAIMED** (asserted by a document, not independently
confirmed).

---

## Summary of what was checked

| Area | Result |
|---|---|
| Opcode set, engine vs our disassembler | **105 opcodes each, exact match, zero difference** (VERIFIED) |
| Opcode operand sizes | Match on all opcodes we exercise, with **one exception: `0x79`** (VERIFIED) |
| Intrinsic table size | ScummVM 258, ours 258, Pentagram 257 (VERIFIED) |
| Intrinsic index alignment | **Zero misalignment**; 28 cosmetic name differences; 60 unimplemented in ScummVM (VERIFIED) |
| Map item record | Doc, engine, and our tool all agree on the 16-byte layout (VERIFIED) |
| Glob placement formula | Doc is **missing a `+1` term** the engine applies (VERIFIED) |
| TYPEFLAG.DAT bitfields | Doc marks 20 bits "Unknown" that the engine names; our tool already follows the engine (VERIFIED) |
| Savegame container | Doc describes Pentagram's format; ScummVM replaced it (VERIFIED) |

---

## D1. Opcode `0x79`: end-of-function vs push-global-address

**The one genuine opcode-level disagreement, and it is ScummVM that is wrong.**

| | Reading |
|---|---|
| **Pentagram doc** | `u8usecode.txt` says nothing. It has no opcode table. |
| **Pentagram source** | `convert/Convert.h:779-800` makes `0x79` **game-conditional**: "end of function ... `79 xx xx` global_address ... `if (crusader)` it's not eof for crusader". `0x7A` is commented "end of function (79 = u8, 7a = crusader)". So in U8, `0x79` is end-of-function with **zero** operand bytes. |
| **ScummVM** | `usecode/uc_machine.cpp:1969-1976`, `case 0x79`, is **not** game-conditional. It unconditionally does `ui16a = cs->readUint16LE(); ui32a = globalToPtr(ui16a); p->_stack.push4(ui32a);`. The only nod to U8 is a comment, "push address of global (Crusader only)". `case 0x7A` at `:1978-1985` is the end-of-function handler, and it sets `error = true`. |
| **Our disassembler** | `agents/usecode-disasm/src/u8_usecode_disasm.py:460-461`: `0x79: ("end", "")`, `0x7A: ("end", "")`. Zero operands. Matches Pentagram's U8 branch. |
| **Our assembler / codegen** | `agents/usecode-compiler/src/u8_assembler.py:135-136` mirrors that. `u8c_codegen.py:208-210` `emit_end()` emits a bare `0x79`. |
| **Real game data** | **VERIFIED empirically.** Scanning the retail `EUSECODE.FLX`: of 518 non-empty entries, **516 classes end with byte `0x79` and zero end with `0x7A`.** |

**Which we follow:** our own tools, which agree with Pentagram's U8 branch and
with the retail data. This is the one place in this document where the
"ScummVM wins" rule is deliberately **not** applied, because the retail bytes
settle it and ScummVM's handler is missing a `GAME_IS_U8` guard.

**Impact on our toolchain: low, but not zero.** `emit_end()` is called once per
class, after every function has been generated (`u8c_codegen.py:938` and
`:1067`), and each function already terminates with `ret` (`0x50`). So the
`0x79` is a trailing class terminator that is never reached, exactly as in the
retail data. The latent risk is the failure mode if it ever *is* reached: a
function that falls through without a `ret` would, under ScummVM, read two
bytes past the end of the class and push a bogus global pointer, then keep
executing garbage, instead of stopping. Under `0x7A` semantics it would have
raised a clean error and terminated the process. In other words, our
class terminator degrades a crisp engine error into silent corruption.

---

## D2. `u8usecode.txt` has no opcode table

**VERIFIED.** The document (2171 bytes, pinned in full) covers only the
EUSECODE.FLX container, the 12-byte class header, and the 32-entry event table.
It documents no opcodes whatsoever.

The task brief assumed an opcode table lived here. It does not, and no other
file in Pentagram's `docs/` has one either. Pentagram's opcode knowledge is in
`convert/Convert.h` (`readOpGeneric()`, the operand-size switch) and
`tools/disasm/Disasm.cpp` (the mnemonic print layer). Both are pinned here for
that reason.

**Impact:** none, beyond correcting the expectation. Our disassembler's opcode
table was never derived from this document.

---

## D3. Opcode set and operand sizes otherwise agree exactly

**VERIFIED by script.** Every `case 0xNN:` in
`usecode/uc_machine.cpp`'s `execProcess` switch was extracted and compared
against `OPCODES` in `u8_usecode_disasm.py`:

```
engine cases: 105   disasm: 105
in disasm not engine: []
in engine not disasm: []
```

Operand sizes were then read by hand for every opcode that takes operands.
They agree, including the fiddly ones:

| Opcode | ScummVM | Ours | Agree |
|---|---|---|---|
| `0x0F` calli | `readByte` argbytes, `readUint16LE` func (`:355-356`) | `"Bw"` | yes |
| `0x11` call | two `readUint16LE` (`:425-426`) | `"ww"` | yes |
| `0x51` jne | `readUint16LE` as `int16`, target = `cs->pos() + si16a` (`:1273-1277`) | `"W"`, target = `offset + len(raw) + val` | yes |
| `0x54` implies | `cs->readUint16LE()` to skip `01 01` (`:1322`) | `"BB"` | yes, same 2 bytes |
| `0x57` spawn | byte, byte, u16, u16 (`:1365-1368`) | `"BBww"` | yes |
| `0x58` spawn inline | u16, u16, u16, byte, byte (`:1401-1405`) | `"wwwBB"` | yes |
| `0x5C` symbol | `readUint16LE` then 9 raw bytes (`:1467-1472`) | special case, `read(2)` then `read(9)` (`:690-704`) | yes |
| `0x70` loop | sbyte, byte, byte (`:1685-1687`) | `"bBB"` | yes |
| `0x75`/`0x76` for each | byte, byte, `readUint16LE` (`:1890-1892`) | `"bBW"` | yes |

Cosmetic mnemonic differences only, no semantic gap: ours says `add sp` for
`0x6E` where ScummVM's comment says "subtract xx from stack pointer"
(`:1652-1658`); ours says `cmp` for `0x24` where ScummVM computes equality.

**Impact:** none. This is the reassuring result. The round-trip test's
foundation is sound.

---

## D4. Intrinsics: counts and alignment

**VERIFIED by script**, comparing three tables index by index.

| Source | Entries |
|---|---|
| ScummVM `usecode/u8_intrinsics.h:56-332`, `U8Intrinsics[]` | **258** |
| Our `u8_usecode_disasm.py`, `U8_INTRINSICS` | **258** |
| Pentagram `convert/u8/ConvertUsecodeU8.h`, `_intrinsics[]` | **257** |

**Our 258-entry table matches `u8_intrinsics.h` in size and in index
alignment, with zero semantic gaps.** Specifically:

- **0** indices where ScummVM has a real implementation but our table calls the
  slot unused. There is no case where the engine knows a function we cannot
  name.
- **28** indices where both name something and the spellings differ. All 28 are
  naming-convention differences for the same function, not misalignment. For
  example `0x00D` ours `Item::getType()` vs ScummVM `Item::I_getShape`;
  `0x031` ours `Item::legal_create(...)` vs ScummVM `Item::I_legalCreateAtCoords`;
  `0x0FE` ours `isGameRunning()` vs ScummVM `UCMachine::I_true`.
- **2** trivial differences against Pentagram: at `0x0FF` and `0x100` Pentagram
  says `"unused"` where we say `"unused_00FF"` / `"unused_0100"`. Pentagram
  simply lacks the final entry `0x101`.

**Impact:** none on naming. Our table is trustworthy. But see D5.

---

## D5. Sixty intrinsics are unimplemented in ScummVM, and we call four of them

**VERIFIED.** `u8_intrinsics.h` has 63 slots set to literal `0`. Sixty of those
are slots our table gives a real Pentagram name to. When usecode calls one,
`uc_machine.cpp:361-363` takes the `_intrinsics[func] == 0` branch, sets
**`p->_temp32 = 0`**, and emits `warning("Unhandled intrinsic %u '%s'? (%s) called")`.
So the call silently yields **0**.

Compiling every LV source file in memory and scanning the emitted `calli`
operands with the real disassembler, **four** of those sixty are actually
reached by our compiler:

| Intrinsic | Name | ScummVM | Where we emit it |
|---|---|---|---|
| `0x043` | `Item::isInNpc()` | `0` | `MAGNET.UNK` |
| `0x065` | `process Item::combine()` | `0` | `FREE.UNK` |
| `0x098` | `Npc::freeEquip(uword)` | `0` | `ZEALSHLD.UNK` |
| `0x09A` | `Npc::getNpcSlot()` | `0` at `u8_intrinsics.h:221` | **synthesised by codegen into every `enterConvo()`**, reaching 19 source files |

The 19 files reaching `0x09A` are every NPC conversation in the expansion:
`ARAMINA`, `ATLI`, `CYRRUS`, `EZREKAL`, `HRODNY`, `INGYALD`, `JENNA`,
`KILANDRA`, `MORDEA`, `MYTHRDLG`, `RAGNAR`, `SALKIND`, `SIGRID`, `STELLOS`,
`THORDIS`, `TORWIN`, `TYORVI`, `XAVIER`, `ZCHILD`. Counted over the compile
sweep described above, which covered 77 candidate sources from
`shared/data/lv-usecode`, `lv-new`, and `lv-patched` and compiled 74 of them.

None of these four is called anywhere in the retail game: scanning all 518
non-empty base classes of the retail `EUSECODE.FLX` with our disassembler
found **0 call sites** for each. That is exactly why ScummVM never implemented
them. The recovered 1994 Lost Vale code paths reach places retail U8 never did.

### D5a. The `getNpcSlot()` case is a real bug, not a cosmetic one

This is the most consequential finding in this document. The chain is fully
verified at every link:

1. `u8c_codegen.py:1118-1128`: for each of three process types (`0x0205`
   Loiter, `0x00F0` Anim, `0x0204` Pathfind) `enterConvo()` emits
   `push this` then `calli 0x04, 0x009A` (`Npc::getNpcSlot()`) then
   `push retval` then `calli 0x04, 0x00CB` (`Kernel::resetRef`).
   **VERIFIED** by disassembling compiled `ATLI.UNK`: three `calli 009A` sites
   at offsets `0334`, `0346`, `0358`.
2. `u8_intrinsics.h:221`: slot `0x09A` is `0, //U`. ScummVM's own
   `convert/u8/convert_usecode_u8.h:205` even labels it `"Npc::getNpcSlot()" // Unused`.
   **VERIFIED.**
3. `uc_machine.cpp:363`: the unhandled path sets `p->_temp32 = 0`, so
   `push retval` pushes **0**. **VERIFIED.**
4. `kernel.cpp:482-492`: `I_resetRef` reads `ARG_OBJID(item)` and calls
   `killProcesses(item, type, true)`. **VERIFIED.**
5. `kernel.cpp:311`: the guard is
   `p->_itemNum != 0 && (objid == 0 || objid == p->_itemNum) && ...`.
   **An `objid` of 0 is a wildcard meaning every object.** **VERIFIED.**

**Consequence (INFERRED from the five verified links, not yet observed in a
running game):** every `enterConvo()` in our compiled dialogue calls
`resetRef(0, type)` three times, and therefore fails **all** Loiter, Anim, and
Pathfind processes for **every** NPC in the world, not just the NPC being
talked to. Starting any conversation plausibly freezes the ambient behaviour of
every actor on the map.

The project's `CLAUDE.md` already flags `enterConvo()` codegen as incomplete,
but it describes the gap as missing `turnToFace` and the invisible check. The
gap recorded here is different and larger: the slot lookup does not merely fall
short, it returns 0, and 0 is the "all objects" wildcard. **Recommend treating
this as a distinct defect from the documented `enterConvo()` limitation.** Two
directions exist: derive the slot without `getNpcSlot()`, or implement the
intrinsic in the patched engine, which already carries LV-specific changes at
`kernel.cpp:489` and `world/map.cpp:251-286`.

---

## D6. Map item record: doc, engine, and our tool agree

**VERIFIED.** `u8mapfmt.txt` describes a 16-byte record. `world/map.cpp:203`
computes `itemcount = size / 16`, and `:208-222` reads exactly the documented
field order and widths:

| Offset | Doc | ScummVM `map.cpp` | Our `u8_map.py` |
|---|---|---|---|
| 0 | Map X, 2 | `readUint16LE()` `:210` | `'<h'` `:62` |
| 2 | Map Y, 2 | `readUint16LE()` `:211` | `'<h'` `:63` |
| 4 | Map Z, 1 | `readByte()` `:212` | `'<B'` `:68` |
| 5 | Type number, 2 | `readUint16LE()` as `shape` `:216` | `'<H'` `:69` |
| 7 | Frame, 1 | `readByte()` `:217` | byte |
| 8 | Flags, 2 | `readUint16LE()` `:218` | `'<H'` `:71` |
| 10 | Glob number / Quality, 2 | `readUint16LE()` `:219` | `'<H'` `:72` |
| 12 | NPC number, 1 | `readByte()` `:220` | byte |
| 13 | Map number, 1 | `readByte()` `:221` | byte |
| 14 | Next object id, 2 | `readUint16LE()` `:222` | `'<H'` `:75` |

One nuance worth recording. `map.cpp:209` carries the comment
**"These are ALL unsigned on disk"**, and reads X and Y with `readUint16LE()`.
Our `u8_map.py:62-63` unpacks them as **signed** `'<h'`, and packs with
`'<hhBHBHHBBH'` at `:93`.

**Which we follow:** ScummVM. In practice this is currently harmless, and that
was checked rather than assumed: across the retail `FIXED.DAT`, 87,603 items,
the maximum X and the maximum Y are both exactly **32767**, and **zero** items
have X or Y at or above 32768. The U8 world is 0x8000 units across, so valid
coordinates always fit in a signed 16-bit value. The failure mode is also
loud rather than silent: `struct.pack('<h', 32768)` raises `struct.error`, so a
builder that ever computed an out-of-range coordinate would crash the build
rather than write a corrupt map. **Low priority, but `'<H'` would be the
strictly correct format.**

---

## D7. Glob placement: the doc is missing a `+1`

**VERIFIED, and this one is a substantive doc error.**

| | Formula |
|---|---|
| **Pentagram doc** | `u8mapfmt.txt` gives `MapX = MapX * 2 + OriginalMapX`, `MapY = MapY * 2 + OriginalMapY`, `MapZ = MapZ + OriginalMapZ`, with the note "DON'T use the 9 lowest bits of OriginalMapX and OriginalMapY (`&= ~0x1FF`)". |
| **ScummVM** | `world/glob_egg.cpp:41-70`: `coordmask = ~0x1FFU; coordshift = 1; offset = 1;` then `itemx = (_x & coordmask) + (globitem.x << coordshift) + offset;` and likewise for Y. Z is `_z + globitem.z`, no offset. |

The mask and the doubling match. **The engine adds `+1` to X and to Y; the doc
does not mention it.** (For Crusader the engine uses `~0x3FF`, shift 2, offset
2, which the doc does not cover at all.)

**Which we follow:** ScummVM. Anything computing absolute positions of
glob contents from the doc's formula lands 1 unit short on both axes.

**Impact on our toolchain: none today.** `u8_map.py` writes glob **eggs**
(`is_glob_egg`, `glob_egg()` at `:101-104`, shape 2 with the glob index in
`quality`) and lets the engine expand them at runtime. It never computes
expanded glob member coordinates itself, so it never uses the formula. This
matters only if a future tool tries to predict where glob contents land, for
example a walkability or collision pre-pass.

---

## D8. TYPEFLAG.DAT: the doc marks 20 bits "Unknown" that the engine names

**VERIFIED.** `u8typeflag.txt` is the weakest document in the set. ScummVM
resolves nearly everything it gives up on. Engine reference:
`gfx/type_flags.cpp:50-102` (the `GAME_IS_U8` branch).

| Byte | Pentagram doc | ScummVM `type_flags.cpp` | Follow |
|---|---|---|---|
| 0, bits 0-7 | "Unknown" | Eight named flags: `SI_FIXED` 0x01, `SI_SOLID` 0x02, `SI_SEA` 0x04, `SI_LAND` 0x08, `SI_OCCL` 0x10, `SI_BAG` 0x20, `SI_DAMAGING` 0x40, `SI_NOISY` 0x80 (`:71-78`) | ScummVM |
| 1, bits 0-2 | "Unknown" | `SI_DRAW` 0x01, `SI_IGNORE` 0x02, `SI_ROOF` 0x04 (`:80-82`) | ScummVM |
| 1, bit 3 | "Translucency" | `SI_TRANSL` (`:83`) | agree |
| 1, bits 4-7 | "1 = has quality, 2 = has quantity, 6 = container" | `si._family = data[1] >> 4` (`:84`) | ScummVM. The doc describes particular family values as if they were the field's meaning. |
| 2, bits 0-3 | "Unknown" | `si._equipType` (`:86`) | ScummVM |
| 2, bits 4-7 | "X Dim of Shape" | `si._x` (`:87`) | agree |
| 3 | "Y Dim / Z Dim" | `si._y`, `si._z` (`:89-90`) | agree |
| 4 | "Anim type / Anim Data" | `si._animType`, `si._animData` (`:92-93`) | agree |
| 5, bits 0-3 | "Unknown" | `si._animSpeed` (`:94`) | ScummVM |
| 5, bit 4 | "editor shape" | `SI_EDITOR` (`:96`) | agree |
| 5, bit 5 | "only set on flaming oils" | `SI_U8_EXPLODE` (`:97`) | ScummVM, which explains the observation |
| 5, bits 6-7 | "non-blocking?" / "only on blue field passage gem" | `SI_UNKNOWN46`, `SI_UNKNOWN47` (`:98-99`) | neither knows |
| 6 | "Unknown" | `si._weight` (`:101`) | ScummVM |
| 7 | "Unknown" | `si._volume` (`:102`) | ScummVM |

Also: the doc asserts the file "has 8 bytes of info for all 2048 shapes".
ScummVM derives the count instead: `count = size / blocksize` with
`blocksize = 8` for U8 and 9 for Crusader (`:51-57`). It imposes no 2048 limit,
which is what lets our patched TYPEFLAG.DAT carry LV shapes.

**Impact on our toolchain: none. Our tooling already follows ScummVM, not the
doc.** `agents/map-populator/src/parse_typeflag.py:27-48` defines exactly
ScummVM's flag names and bit values, and `:74-100` splits the nibbles the same
way. The one gap is cosmetic: `:99` labels byte 5's low nibble `unknown5`
where the engine calls it `_animSpeed`.

The doc's animation-type semantics (types 0 through 5, and "Type 5: Animated by
Usecode Event 0x2") are **CLAIMED**, not checked in this pass.

---

## D9. `savegame.txt` documents Pentagram's container, not ScummVM's

**VERIFIED.** The document specifies a container beginning
`char id[17] "PentagramSavegame"` followed by a `uint32` file count.

ScummVM does not use it. `filesys/savegame.cpp:29` defines
`#define SAVEGAME_IDENT MKTAG('V','M','U','8')`, written at `:189` and checked
at `:110`. The container is ScummVM's standard save format.

The **section names survive**: `VERSION`, `GAME`, `INFO`, `KERNEL`, `OBJECTS`,
`WORLD`, `MAPS`, `CURRENTMAP`, `UCSTRINGS` and the rest are still the member
names ScummVM looks up, for example `_archive->getMember("VERSION")` at
`savegame.cpp:143`. So the document remains useful for **what is inside** a
save, and is wrong about **how the file is wrapped**.

**Which we follow:** ScummVM. **Impact:** none today, since we do not read or
write saves. It matters for the save-compatibility guarantee in
`shared/build/lv_manifest.json`: class ids and global flag bits are what
persist, and the container is ScummVM's problem, not ours.

---

## D10. Note on the LV engine patch surface

**VERIFIED, recorded as context for D5a.** The patched engine at `scummvm-lv/`
carries very few LV-specific changes. Searching for the `LV:` marker finds
only four sites: three debug lines and the NPC-actor promotion block in
`world/map.cpp:241-286`, plus one debug line at `kernel/kernel.cpp:489`.

The intrinsic table is **not** patched. `u8_intrinsics.h:221` is still `0`, so
nothing in our engine fork currently supplies `Npc::getNpcSlot()`.

---

## Items explicitly not verified

Stated plainly so nothing here is mistaken for a checked result:

- `u8gfxfmt.txt` (shape and palette format) was **not** cross-checked against
  `gfx/shape.cpp` or `convert/u8/convert_shape_u8.cpp`. Pinned, unchecked.
- `shapes.cmp.txt` was **not** cross-checked. Pinned, unchecked.
- `u8anim.txt` was **not** cross-checked against `world/actors/anim_dat.cpp`.
  Pinned, unchecked.
- `u8encoding.txt` was **not** cross-checked against ScummVM's font rendering.
- The animation-type semantics in `u8typeflag.txt` (D8, final paragraph) were
  not checked against the engine's animation dispatch.
- D5a's world-wide process-kill consequence is inferred from five verified
  code facts. It has **not** been observed in a running game. Confirming it
  needs a play test with `debuglevel 1`, watching for the
  `LV: I_resetRef item=0 type=0x...` line that `kernel.cpp:489` already prints.

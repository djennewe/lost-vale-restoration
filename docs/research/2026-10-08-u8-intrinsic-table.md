# The retail U8 intrinsic table, decompiled (2026-10-08)

The retail engine `shared/data/u8-install/U8.EXE` was decompiled (935,440
bytes, sha256 `1b1f4708…`, a 16-bit NE executable under the Phar Lap 286
DOS extender). The goal was to stop guessing what the usecode intrinsics
that ScummVM leaves empty actually do, and to check the guesses the fork
had already made.

**Outcome.**
- The table is a data file, `USECODE/UNKCOFF.DAT`, and every one of its 256
  slots has its own retail routine.
- Fork `10d59e56` (Camera getX/Y/Z) matches retail.
- Fork `9be627c0` (`isGameRunning` = false) does not: it let every locked
  chest open without its key and disarmed every chest trap. It was reverted
  in fork `f50c1d45` (comments corrected in `ed924d30`), which also binds
  `isInNpc` (0x43) and `freeEquip` (0x98) to their retail behaviour.
- Verifying that revert showed Hrodny's chest had no real lock: any key
  opened it. Retail locks a chest with a TRAP item inside it, not with the
  chest's quality. `build_map_10.py` now puts that TRAP in the chest
  (FIXED.DAT `6dc98430`).
- `getNpcSlot` (0x9A) turned out to be a slot allocator, which confirms the
  compiler's 2026-10-04 workaround.
- ScummVM never fires the equip/unequip usecode events for U8. Retail does.
- Verification: `docs/playtest-2026-10-08-intrinsics.md` (the fork) and
  `docs/playtest-2026-10-08-chest-lock.md` (the lock).

## How it was found

The method is recorded because the dead ends are cheaper to read than to
repeat.

1. **The usecode side first.** All of retail `EUSECODE.FLX.bak` was
   disassembled with `agents/usecode-disasm/src/u8_usecode_disasm.py`: 516
   classes, 0 errors. The intrinsic numbers each class calls in retail were
   compared with those in our `shared/build/EUSECODE.FLX`, and both were
   crossed with the null entries of the fork's `u8_intrinsics.h` (58 of the
   256 U8 slots). Only three null slots are called by anything compiled:
   `0x43` (EGGMAGNE), `0x98` (TYPEAOFR) and `0xCE` (FREE, retail too).
2. **Opening the EXE.** `file` says `NE for MS-DOS, Phar Lap DOS extender`.
   REA (github.com/morluto/rea, a CLI/MCP front end to Ghidra) refused NE
   outright. Plain Ghidra's NE loader imports it as
   `x86:LE:16:Protected Mode`, so REA was extended to admit NE (local branch
   `feat/ghidra-ne` in `~/src/rea`; `TODO.md` §7 holds the unsent upstream
   PR). Ghidra puts NE segment *N* at selector `0x1000 + 8·(N−1)`, so
   `0x13e00043` is `13e0:0043`, segment 125. The data segment (DS) is
   segment 148, selector `0x1498`, file offset `0xd0200`. One persistent MCP
   session was kept open, because each fresh import re-analyses the whole
   EXE in about three minutes.
3. **Dead end: hunting the table in relocations.** A 256-entry table of far
   pointers should show up as 256 relocations 4 bytes apart. The longest such
   runs (659 and 220 entries in DS) are C++-style dispatch tables with a
   repeating 13-entry pattern and string-pointer tables, not the intrinsics.
   The table is not in the image at all.
4. **Strings lead to the interpreter.** The data segment keeps the assert
   file names: `INTER.C`, `UPROCESS.C`, "No Usecode! (press any key)". A scan
   of the code segments for `push 0x88c8` (the offset of `INTER.C`) found
   only segment 125. Ghidra does not turn a 16-bit `push imm16` of a DS
   offset into a reference, so string xrefs come back empty and a byte scan
   (`68 lo hi`) is the reliable search. The decompile of
   `FUN_13e0_01f1`, a 2,600-line interpreter with a `switch` on the opcode,
   shows `case 0xf` reading the argument size and the intrinsic number and
   calling `FUN_13e0_0043(n)` for the function pointer.
5. **The lookup leads to the loader.** `FUN_13e0_0043` asserts
   `n < [DS:b684]` and returns `[DS:b680] + n*4`. Those two words are filled
   at run time. A byte scan for writes to `b680`/`b684` found only
   `FUN_13e8_0477` in `UPROCESS.C`, whose strings are `unkcoff` `.dat`,
   `unkcsym` `.map`, "Publics by Name", "Unresolved c symbol %s" and
   "Continue anyway?". `USECODE/UNKCOFF.DAT` is exactly 1,024 bytes.
6. **Calibration.** Decoding `UNKCOFF.DAT` as `(offset, segment)` pairs
   with segment *s* at selector `0x1000 + 8·(s−1)` puts 248 of the 256
   entries exactly on a Ghidra function start. Shifting the segment by
   anything from −6 to +6 gives at most 6, so the stored segment is the NE
   segment number.
7. **Decompiling the slots** with REA's `analyze_function`. Helpers were
   followed as needed: `FUN_10d8_0dce` (item flags), `FUN_10d8_0bdd`
   (parent), `FUN_1408_1149` (Kernel find process), `FUN_1418_019e` (set a
   process's item), `FUN_13e8_0bf7` (call a usecode event).
8. **Checking a constant really is constant.** For `isGameRunning`'s byte
   `[DS:59fa]`, three checks were combined. Ghidra's xrefs give two reads and
   no writes. A byte scan of all code for the operand `fa 59` turns up the
   same two reads. The debug menu's toggle list (`FUN_13b8_0374`), whose
   items hold pointers to the flags they flip, has no `59fa`. And the
   initialised value in the file is `01`.
9. **Engine events.** `procedure_callers` on `FUN_13e8_0bf7` returned 23
   wrappers, one per usecode event. Each pushes its event number and mask
   (`0x0A`/`0x400` is equip, `0x0B`/`0x800` is unequip). Their callers show
   where the original engine fires each event.
10. **The engine run corrected the reading.** The fork change went to the
    project verifier, which played it in ScummVM
    (`docs/playtest-2026-10-08-intrinsics.md`). Two things the static
    reading had wrong surfaced there:
    - The `loop` that `isGameRunning` guards in CHEST was read as "the
      containers inside". The listing's `search type: container` names the
      search scope (the items inside a container). The item filter is the
      pushed shape `02F4h`, so the loop iterates TRAP items, and an opened
      trapped chest exploded.
    - Using a key blank on Hrodny's chest unlocked it, which led to
      KEYRING's TRAP-based lock check.

    Read a loop's pushed filter values for what it iterates.

## 1. Where the table lives: `USECODE/UNKCOFF.DAT`

The table is not compiled into the EXE. It is the 1,024-byte file beside
`EUSECODE.FLX`:

- The interpreter (`INTER.C`, segment 125) handles opcode `0x0F calli` by
  calling `FUN_13e0_0043(n)`, which asserts `n < [DS:b684]` and returns the
  far pointer at `[DS:b680] + n*4`.
- `FUN_13e8_0477` (`UPROCESS.C`, segment 126) fills both words. Its shipping
  path reads `unkcoff.dat`, sets the count to `size / 4`, and turns each
  stored segment number into a protected-mode selector:
  `((seg + 0x20b − last_entry_seg) * 8) | 7`. Its other path [INFERENCE:
  the developers' build] reads 74-byte name records from `unkcsym` and
  resolves each against the linker `.map`'s "Publics by Name". So
  intrinsics were bound by C function name at link time, and the shipped
  game carries the resolved table. An expansion that added an intrinsic
  would have shipped a new EXE and a new `UNKCOFF.DAT` together.

```python
import struct
uk = open('shared/data/u8-install/USECODE/UNKCOFF.DAT', 'rb').read()
table = [struct.unpack_from('<HH', uk, i * 4) for i in range(256)]  # (offset, NE segment)
```

The 8 entries not on a Ghidra function start are `0x79 0xb9 0xd2 0xd9 0xda
0xdd 0xde 0xe5`. Three of them (`0x79`, `0xb9`, `0xd2`) are at offset 0 of
a segment; Ghidra just did not create functions there.

**No two slots share a target.** So the 58 slots ScummVM leaves null are not
stubs in the original. ScummVM never needed them because retail usecode
never calls them. The one exception, `0xCE setRef`, has a single retail
caller, FREE's wrapper at `0581:2A64`, and no class calls that wrapper.

## 2. The slots that matter here

| Slot | Name (ScummVM) | Retail target | What retail does | Fork after `f50c1d45` | Called by |
|---|---|---|---|---|---|
| `0xC3` | `Camera::getX()` | `1288:2bf1` | `return [DS:b26a]` | `I_getCameraX` (`10d59e56`) | LVFREE |
| `0xC4` | `Camera::getY()` | `1288:2bf9` | `return [DS:b26c]` | `I_getCameraY` | LVFREE |
| `0xC5` | `Camera::getZ()` | `1288:2c01` | `return (byte)[DS:b26e]` | `I_getCameraZ` | LVFREE |
| `0xFE` | `isGameRunning()` | `1298:1873` | `return (byte)[DS:59fa]`, constantly **1** | `UCMachine::I_true` (was `I_false`) | retail CHEST_EW/NS, LCHST_EW/NS |
| `0x9A` | `Npc::getNpcSlot()` | `10f8:1c8a` | allocates a free NPC slot | null, by design | nothing compiled |
| `0x43` | `Item::isInNpc()` | `10d8:1ed8` | 1 if a container above the item is an NPC | `Item::I_isInNpc` (new binding) | EGGMAGNE |
| `0x98` | `Npc::freeEquip(uword)` | `10f8:2696` | clears the item from the NPC's equipment slots | `Actor::I_freeEquip` (new) | TYPEAOFR |
| `0xCE` | `setRef(uword, uword, uword)` | `13e8:152d` | retargets a running process to another item | null | FREE `0581:2A64`, uncalled |
| `0x65` | `process Item::combine()` | `10d8:2519` | runs usecode event `0x0C`, returns its pid | null | none since wave 2 (`c89bf07`) |

### Camera::getX/Y/Z: the fork binding is right

`Camera::move_to` (`0xBF`, `1288:0e1a`) starts by storing
`[b26a] = x; [b26c] = y; [b26e] = z`, and `Camera::move_rel` (`0xC0`) is
`move_to(b26a + dx, b26c + dy, b26e + dz, 0)`. The getters return the last
camera target, which is what fork `10d59e56` binds them to.

### isGameRunning: retail returns 1

`[DS:59fa]` starts at `01` (file offset `0xd0200 + 0x59fa`) and nothing
writes it (method step 8). Its only other reader is the mouse hit-test in
`FUN_1298_155f`: `if ([59fa] && typeflag bit) return 0`; [INFERENCE] this
skips editor-only items. So the byte is [INFERENCE] the "game running, not
the editor" flag. That decides the four callers, all retail classes that are
byte-identical in our build:

- `LCHST_EW` 026A / `LCHST_NS` 02A1 `use()`: `if isGameRunning() spawn
  look()` (the "locked chest " bark) `else playSFX; openGump(7)`. **In retail
  a locked chest cannot be opened by double-clicking.** Its key turns shape
  618 into shape 78 (`CHEST_EW`); the open branch is the editor's.
- `CHEST_EW` 004E / `CHEST_NS` 0075 `use()`: both branches open the gump. The
  `isGameRunning` branch first calls `use()` on every TRAP (shape 756, class
  `TRAP` 0x2F4) inside the chest. TRAP `use()` does nothing when
  `quality/256 == 1`. When `quality/256 == 0` it spawns an explosion
  (FIRESPEL `0583:233D`) and barks "Ouch! -That- must have hurt, Avatar!".
  That is how retail booby-traps a chest.

The 2026-09-03 fork change came from `docs/playtest-2026-09-02-quest-chain.md`
Z-c, written about Hrodny's chest while it was still locked (item 3515,
shape 618). That section read the bark as a defect and concluded "no chest
in the game could be opened". The very next section (Z-d) shows the key path
working: the quality-20 key turns 618 into 78 and the chest opens. With
`I_false`, every locked chest in Pagan opened without its key and no chest
trap ever fired. Upstream's `I_true` had been right. It logs
`Unhandled intrinsic 254` on each call (`uc_machine.cpp:391`, a warning for
every `I_true` slot); that line is expected.

### How a chest is locked: a TRAP inside it

Found while verifying the revert (`docs/playtest-2026-10-08-intrinsics.md`
C4 and finding 1). The key class `KEYRING` (0x4F, byte-identical to retail)
handles a key used on a locked chest at `004F:0445`:

1. Scan the chest for shape 756 with `quality/256 == 1`.
2. If there is none, unlock: **any key opens it**.
3. Otherwise unlock only if `trap.quality & 0xFF` equals the key's quality
   (a keyring checks each key inside it, `04ED`).
4. Unlocking turns LCHST_EW into shape 78 and LCHST_NS into 117.

So the lock id lives in a contained TRAP record with quality `0x100 | keyid`,
not in the chest's own quality. Retail's starting state (NONFIXED, inside
`SAVEGAME/U8SAVE.000`) holds 38 TRAP records:
- 11 lock traps (`quality/256 == 1`; `0x11E`, `0x13A`, `0x150` and others);
- 26 booby traps (quality 0);
- one with `quality/256 == 57`.

All but one carry flags `0x2008`; the `0x2000` (fast area) bit is run-time
state.
Hrodny's chest (`build_map_10.py`) had quality 20 on the chest and no trap,
so the Cliff Key and even a key blank opened it, contrary to the 2026-09-02
Z-d note. Since 2026-10-08 the builder places
`contained_item(SHAPE_TRAP, quality=0x100 | 20)` directly after the chest.
`SHAPE_TRAP = 756` is in `lv_shapes.py` with this rule.

### getNpcSlot allocates a slot; it does not identify the NPC

```c
int getNpcSlot(void) {             /* 10f8:1c8a, no arguments */
  for (slot = 1; slot < 0x100; slot++)
    if (!(npc_table[slot * 0x31 + 0x2f] & 1)) {   /* 49-byte NPC records */
      npc_table[slot * 0x31 + 0x2f] |= 1;
      return slot;
    }
  return 0;
}
```

It hands out the first free NPC number (1-255) and marks it used. The 1994
`enterConvo()` passes it to `resetRef`. With a faithful binding, that would
leak a slot on every conversation and kill nothing. The compiler's
2026-10-04 replacement (kill the talked-to NPC's own process types on
`referent`, as retail METHOD does) stands. Never bind 0x9A as "this NPC's
slot".

### isInNpc

```c
bool isInNpc(item) {                 /* 10d8:1ed8 */
  for (i = item; i != 0; ) {
    if (!(flags[i] & 8)) return 0;   /* FLG_CONTAINED */
    i = parent[i];
    if (1 <= i && i <= 255) return 1; /* item numbers 1-255 are NPCs */
  }
  return 0;
}
```

It returns 1 if the item is anywhere in an NPC's inventory, nested bags
included. In retail, equipped items carry `FLG_CONTAINED` as well:
`FUN_1348_01db` tests equipped (`0x200`) only inside `flags & 8`. ScummVM's
`Actor::setEquip` clears `FLG_CONTAINED`, so a literal port of the flag test
would answer 0 for an equipped item where retail answers 1. ScummVM's
existing `Item::I_isInNpc`, written for Crusader, walks
`getParentAsContainer()` and stops at the first `Actor`. Actor object ids are
1-255 (`object_manager.cpp:75`), so it gives retail's answer for both
contained and equipped items. Fork `f50c1d45` binds it unchanged.

### freeEquip

```c
void freeEquip(npc, item) {          /* 10f8:2696 */
  short *eq = &npc_table[npc * 0x31 + 0x1d];   /* 8 equipment words */
  for (k = 0; k < 8; k++) if (eq[k] == item) eq[k] = 0;
}
```

It clears the NPC's equipment record and leaves the item where it is. In
ScummVM, being equipped is `FLG_EQUIPPED` on an item whose parent is the
actor, so the new `Actor::I_freeEquip` clears `FLG_EQUIPPED` and sets
`FLG_CONTAINED` when the item is equipped on that actor, and does nothing
otherwise. The retail engine calls the same routine itself when an equipped
item is cached out (`FUN_10e0_24e4`).

### setRef and combine (left unbound)

- `setRef(item, type, newItem)`: Kernel finds the first live process
  matching (item, type) (`FUN_1408_1149`; item 0 = any, type 6 = any,
  terminated processes skipped) and calls the process's set-item routine
  (`FUN_1418_019e`). Nothing reachable calls it.
- `combine()`: `return callUsecodeEvent(item, 0x0C)`'s pid, or 0. Event
  `0x0C` is `combine` in ScummVM's event table. Nothing calls it.

## 3. Engine events: retail fires equip and unequip, ScummVM does not

Retail's usecode-event wrappers (callers of `FUN_13e8_0bf7`) cover every
event from `0x00` to `0x15` except `0x0D`. Two of them, equip (`0x0A`) and
unequip (`0x0B`), are fired by the engine itself, not only by usecode. The
roles below are read from the decompiles: [INFERENCE] beyond the call
itself, since these gump routines carry no names.

| Event | Wrapper | Fired by retail engine code | Also intrinsic |
|---|---|---|---|
| `0x0A` equip | `10d8:2484` | `FUN_1340_0e87` (a drop into the Avatar's gump: set the equip slot from the shape's equip type, then fire), `FUN_1340_03cd` (`CONTGUMP.C`; creates and equips a backpack when there is none), `1080:00ee` (game start) and a Code120 debugger routine | `0x63 process Item::equip()` |
| `0x0B` unequip | `10d8:24b3` | `FUN_10e0_24e4` (`ITEMCACH.C`: an equipped item leaving the cache; freeEquip, fire, clear `0x200`), `FUN_1348_01db` and `FUN_1348_08bf` (gump drag code) | `0x64 process Item::unequip()` |

ScummVM's `callUsecodeEvent_equip`/`_unequip` run only from the usecode
intrinsics, which are null for U8. So no U8 equip or unequip handler ever
runs. Retail has none to run. Of our classes, only `TYPEAOFR`
(`TypeAOFrizbee`, 0x04EC) has one (equip). Its body acts only at frame 3,
which nothing creates (`agents/usecode-compiler/docs/lv-patched-inventory.md`,
`ZEALSHLD.UNK`). If it ran as written, it would undo itself: it treats any
item in the shield slot, the Defender included, as forbidden armour. So
dispatching the event would change nothing a player can reach today. It was
left out of `f50c1d45` and recorded in `TODO.md`.

## 4. The other null slots

Of the 58 null slots, the compiled game calls only the three above. A few
more, for the record:
- `0x09`/`0x0A`/`0x0B` get and set an item's gump position (byte X ≤ 127,
  byte Y ≤ 255).
- `0x17`/`0x18` get and set a glob egg's glob number, and `0x1C` sets an
  egg's type. Each is gated on the typeflag family (3 glob egg, 4 egg,
  6 container).
- `0x24`/`0x28`/`0x29`/`0x2A` are the bounding-box tests `touches`,
  `isCompletelyOn`, `isAbove` and `isUnder`.

## Reproducing

1. Build REA from `feat/ghidra-ne` (`npm ci && npm run build:cached`) and
   run `node scripts/rea.mjs mcp` with `GHIDRA_INSTALL_DIR` set to Ghidra
   12.1.4.
2. Call `open_binary` on `U8.EXE` with `provider_id: "ghidra"`. The first
   analysis takes about three minutes.
3. Call `analyze_function` with `procedure: "0x<selector><offset>"` for any
   slot from the table decode above. `procedure_callers`,
   `resolve_containing_procedure`, `xrefs` and `search_strings` cover the
   rest.
4. Raise the stdio client's `maxBufferSize` before any whole-image call, and
   give each call a long timeout: a request that times out cancels and tears
   down the Ghidra session.

The usecode listings come from `agents/usecode-disasm/src/u8_usecode_disasm.py`
on `USECODE/EUSECODE.FLX.bak`. Nothing derived from `U8.EXE` is committed
here beyond addresses and paraphrased pseudocode.

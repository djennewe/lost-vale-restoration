# M0.6 — lv_manifest.json design

> Pins every savegame-visible number the build allocates dynamically, so that
> adding, removing, or reordering source files can never silently renumber a
> flag or class that a savegame (or the shipped FIXED.DAT) depends on.
> PLAN.md M0.6 is the requirement; this document is the design.

## 1. What is currently allocation-order dependent (the hazard)

Verified against the code on 2026-07-03:

- **Global flag bits** — `SymbolTable.allocate_global_flag()` hands out
  `_next_global_bit` starting at **0**, in first-declaration/first-reference
  order across the whole compile. Compile order is `sorted()` per directory,
  directories in the order `LOST VALE/` → `UNK files/UNK/` → `lv-new/`
  (`build_eusecode.py` steps 3-5). Adding one flag to an early file shifts
  every bit after it. `lbDone` landing at bit 678 in the current build is
  pure compile-order accident.
- **New class ids** — `build_eusecode.py` step 6 iterates `driver.results`
  (insertion order = compile order) and assigns `NEW_CLASS_START = 0x0260`
  upward. Renaming a file reorders the walk and renumbers classes. Class ids
  are savegame-visible (running process state) and FIXED.DAT-visible where a
  trigger encodes one (future UnkEgg quality dispatch = `class - 0x47F`).
- **Not** order-dependent (already pinned in code, manifest records them for
  completeness/conflict-checking only): LV NPC classes via `LV_NPC_SHAPES`
  (npcnum+1024), modified base classes (keep their base ids), teleport ids
  (map builders), global flag *widths* (declared in source).

## 2. Bootstrap decision — experiment results (2026-07-03)

`UNK files/UNK/FLAGS.UNK` ("ULTIMA 8 FLAGS.UNK", 582 declarations, ~673
bits) is the 1994 master flag include — but with the **Lost Vale flags
prepended at the top**, shifting every retail flag. Two experiments against
the retail bytecode (extracting `push/pop global` bit offsets from the
compiled classes) settled the bootstrap question:

1. **FLAGS.UNK declaration order from bit 0: refuted.** 0/36 of AVATAR's
   predicted bits appear in retail AVATAR bytecode (0/2 METHOD, 0/4 AIRSPEL,
   0/1 FREE).
2. **Retail-section-only renumbering (skip the LV block): refuted.** Only
   4/35 hits — the 1994 file also reordered sections relative to whatever
   produced the retail build. Declaration-order recovery is not viable.

Implication: the 1994 team planned a **full recompile of every class** (all
bytecode consistently renumbered), which an expansion install could do.
We cannot — we recompile only 5 base classes; the other 511 keep retail bits.

Two distinct problems fall out, and the manifest solves the first:

- **Collision (fixed by this design):** the current allocator assigns LV
  flags from bit 0 upward, directly on top of retail's densely used range
  (525 distinct bits, dense below ~600; capacity is 4096 bits —
  `UCMachine` creates `BitSet(0x1000)`). Any LV flag under ~600 can corrupt
  retail quest state and vice versa. (Today's verified Mythran flags — 678,
  794, 796 — happen to be collision-free, so the 2026-07-03 verification
  stands.)
- **Shared-flag mismatch (deferred to M1):** flags that our 5 recompiled
  base classes share with untouched retail bytecode (e.g. `avatarEndure`,
  `somebodyTalking`, `levitateAvatar`) currently live at our bits while
  retail classes use theirs. Recovering the true retail name→bit mapping
  needs bytecode alignment (compile our source, align the k-th flag op
  against retail's k-th flag op) — that is the M1 flag-graph tool's job.
  Until then these flags are marked `"retail_shared": true` in the manifest;
  they occupy LV-window bits (mismatch unchanged from today, but no longer
  *colliding*). When M1 recovers the retail bits, those pins get corrected
  in one deliberate, devlog-noted, savegame-breaking migration — which must
  happen before any public release freezes the manifest for good.

  **First migration, 2026-10-08** (Douglas approved the save break for these
  two bits): `araminaSchedule` 1635 (0x663) → 519 (0x207) and `devonInRule`
  1206 (0x4B6) → 88 (0x58), the bits retail MORDEA, LOGBOOK4 and ARAMINA use
  (evidence: `test_symbol_retail_pins.py`). The old pins stay in the manifest
  as `araminaSchedule_1635` / `devonInRule_1206` with `"retired": true`.

  **Second migration, 2026-10-09** (Douglas: ARAMINA's flags only): the
  other eleven globals ARAMINA reads or writes, found by zipping her
  compiled global operands against retail ARAMINA 0x040D's (39 each, same
  source). `araminaMet` 0x65F → 0x203, `araminaName` 0x660 → 0x204,
  `araminaJob` 0x661 → 0x205, `somebodyTalking` 0x46D → 0x0F,
  `hearTruthActive` 0x485 → 0x27, `hydrosFree` (2 bits) 0x494 → 0x36,
  `hasHeart` 0x49A → 0x3C, `lothianDead` 0x51D → 0xBF, `toldDagger` 0x534
  → 0xD6, `mordeaDead` 0x576 → 0x11A, `toldOfTreasure` 0x5A3 → 0x147, each
  old range retired as `<name>_<oldbit>`. Every other retail_shared pin is
  unmigrated.

**Adopted bootstrap:** rebase the *entire* LV flag set into a reserved
window starting at **bit 1024** (clear of retail's dense range and below the
sparse outliers at 2560+; 1536+ bits of headroom for ~700 bits of current LV
usage), preserving the current build's relative order. One savegame reset,
done while savegames are still throwaway.

## 3. Manifest schema

Checked-in at `shared/build/lv_manifest.json` (per PLAN; note it is a pinned
*source of truth* unlike its regenerated neighbors — header comment field
says so):

```json
{
  "version": 1,
  "comment": "Savegame-visible id/flag pins. Append-only. Never renumber.",
  "global_flags": {
    "avatarPoisoned": {"bit": 0, "width": 1},
    "lbSpoke":        {"bit": 1, "width": 2},
    "lbDone":         {"bit": 656, "width": 1}
  },
  "classes": {
    "TYPEMYTHRANLVDLG": 633,
    "SIGRID": 634
  },
  "npc_classes": {"RAGNAR": 1079},
  "modified_base_classes": {"AVATAR": 1},
  "next_free": {"global_bit": 700, "class_id": 635}
}
```

- `global_flags` / `classes`: the pins. Decimal in JSON; tools print hex too.
- `npc_classes` / `modified_base_classes`: recorded for conflict detection
  (a new pin colliding with an NPC id or base id must fail the build), not
  consulted for allocation — code stays the source for those.
- `next_free`: append cursors. Monotonic; never reused even if a pin is
  retired (retirement = keep the entry, add `"retired": true`; the bit/id is
  dead forever — matches the PLAN risk-register rule). A flag that moves
  keeps its live name, and its old range stays as `<name>_<oldbit>` with
  `"retired": true`. `validate()` fails the build on a live pin that overlaps
  a retired range, or a `next_free.global_bit` that is not past one.

## 4. Allocator changes

- `SymbolTable` gains `load_manifest(manifest)` — pre-populates
  `global_flags` from pins and sets `_next_global_bit` from `next_free`.
  `allocate_global_flag(name, bits)`:
  - pinned name: return the pin; **fail** if the declared width differs.
  - unpinned name: allocate at cursor, record in a `new_allocations` list.
  - Post-pass invariant check: no two pins overlap bit ranges; no unpinned
    allocation landed inside a pinned range.
- `build_eusecode.py` class assignment: consult `classes` pins; unpinned new
  class gets `next_free.class_id`; fail if a pinned id collides with an NPC
  id, base id, or another pin.
- End of build: if `new_allocations` is non-empty, append them to the
  manifest file, bump `next_free`, and print a clearly visible
  `MANIFEST: appended N new pins (...)` block. The updated manifest must be
  committed — the build prints a reminder when the file changed.
- **Fail the build** (M0.4 mechanism) if honoring a pin is impossible or if
  an existing pin's value would change. There is no "re-pin" code path; that
  requires a human editing the JSON with a written justification.

## 5. Acceptance (from PLAN M0.6)

1. Compiling the sources in a shuffled order produces a byte-identical
   EUSECODE.FLX (test: monkeypatch `compile_directory` to reverse its sorted
   order, rebuild, md5-compare).
2. Adding a `globalflag` to any source appends exactly one manifest entry at
   the cursor and reports it; no existing pin moves (test: temp flag in a
   temp file, diff the manifest).
3. Hand-editing a pin to conflict (duplicate bit, width mismatch, class id
   collision) makes the build exit nonzero naming the conflict.

## 6. Sequencing

Implementation waits for the M0.3/M0.4 build-guardrail branch to land (same
file, `build_eusecode.py`). Order: run the section-2 experiment → Douglas
signs off on bootstrap (a) vs (b) → generate the initial manifest → wire the
allocators → acceptance tests. One savegame reset accompanies bootstrap (b);
note it in the devlog.

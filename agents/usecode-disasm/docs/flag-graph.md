# flag-graph.md — u8_flag_graph.py

M1 tool implementing PLAN.md 2.1 ("Reachability audit") and 2.3 ("Flag-graph
tool"). Read-only consumer of `u8_usecode_disasm.py` (never modifies it, per
CLAUDE.md's hard rule); local copies of `u8_map.py` (FIXED.DAT reader) and
`parse_typeflag.py` (TYPEFLAG.DAT reader) from `agents/map-populator/src/`,
per the project's per-agent-copy convention (`u8_flex.py` is the precedent).

## What it does

1. Disassembles every non-empty class in a built `EUSECODE.FLX`, using the
   disassembler's own instruction iterator (`disassemble_class_summary`,
   built on `disassemble_bytecode`) — never a raw byte scan, so instruction
   offsets, operand widths, and string/opcode boundaries are exact.
2. Joins every observed `push global` (0x4E) / `pop global` (0x4F) bit
   offset against `shared/build/lv_manifest.json`'s `global_flags` pins.
   Bits below 1024 are retail's own range (summarized, not itemized — see
   "Why bit 1024 is the line" below). Bits at or above 1024 are the LV
   window; unpinned bits in that range print as `bit_NNNN`.
3. Computes an inbound-reference count per class using the four engine
   dispatch mechanisms below, and reports every class pinned in the
   manifest's `classes` + `npc_classes` sections with zero inbound
   references as an **orphan**: compiled and shipped, but nothing in the
   game invokes it.
4. Cross-checks a bit >= 4096 anomaly (see "Anomalies" below) — a
   structural sanity check that turned up a real bytecode defect the first
   time this tool ran (see devlog / commit for the ATLI finding).
5. Writes `shared/docs/wiring-data.md`, deterministic modulo the generated
   timestamp line.

## Running it

```bash
python3 agents/usecode-disasm/src/u8_flag_graph.py shared/build/EUSECODE.FLX
```

All four inputs default to the checked-in build artifacts and can be
overridden:

```bash
python3 agents/usecode-disasm/src/u8_flag_graph.py shared/build/EUSECODE.FLX \
    --manifest shared/build/lv_manifest.json \
    --fixed    shared/build/FIXED.DAT \
    --typeflag shared/build/TYPEFLAG.DAT \
    --out      shared/docs/wiring-data.md
```

`--typeflag` defaults to `shared/build/TYPEFLAG.DAT` (the patched copy
`patch_typeflag.py` produces for the new wood-wall shape slots), not the raw
`shared/data/u8-install/STATIC/TYPEFLAG.DAT` — the built copy is what the
actual `shared/build/FIXED.DAT` was placed against, and the two differ (shape
slots 856-858, unrelated to SF_UNKEGG classification, but use the matching
pair by default regardless). Runtime on the current build: under half a
second (545 classes, ~92k map items).

Exit status is currently always 0 — this tool reports, it does not gate the
build. PLAN 2.3 says it should run inside the build gate once M1's wiring
work (2.2) is far enough along that a quest-critical orphan is always a
regression rather than expected pre-wiring state; wiring `build_eusecode.py`
to call it is explicitly **not** done by this tool (that file belongs to the
usecode-compiler agent, working in parallel — see CLAUDE.md's coordination
protocol). When that integration lands, the natural gate is: fail the build
if any class in the manifest's `classes` ∪ `npc_classes` has zero inbound
references.

## The dispatch model (PLAN.md section 0)

Four ways a class actually gets invoked, verified against scummvm-lv's
`world/item.cpp` `callUsecodeEvent`:

| Mechanism | Rule | Source data this tool reads |
|---|---|---|
| (a) default item dispatch | `class_id = shape` | every placed item's `shape` field, all maps in FIXED.DAT |
| (b) LV npcNum patch | `class_id = npcNum + 1024`, any item with `npcNum != 0` | every placed item's `npcnum` field |
| (c) UnkEgg quality dispatch | `class_id = quality + 0x47F` (1151), item's shape has the `SF_UNKEGG` typeflag family (family 4) | TYPEFLAG.DAT family byte + placed items' `shape`/`quality` |
| (d) usecode-internal | any `0x11 call` or `0x57 spawn` instruction naming the class | disassembled `class_calls` / `spawns` from every class |

A class with a nonzero count from *any* mechanism is reachable; a pinned LV
class with zero across all four is an orphan.

### Discovered quirk: mechanism (b) reads a reused field

`u8_map.py` (the map-populator agent's authoring API, copied here read-only)
stores three semantically different things in the same 16-bit item field
that the engine treats as `npcNum`:

- an authored NPC actor's number (`MapItem(..., npcnum=105, ...)` for Ragnar)
- a teleport egg's *destination* npc slot (`MapItem.teleport_dest(...,
  dest_npc=N, ...)` → stored in `.npcnum`)
- a monster egg's *spawn count* (`MapItem.monster_egg(..., count=N, ...)` →
  also stored in `.npcnum`)

PLAN.md's engine fact is literal: *any* item with `npcNum != 0` dispatches
`npcNum + 1024` when a class exists there. The tool follows that literally
and reports both kinds of hit, but separates them in the report as
`npcnum:N` (item shape is not one of the four egg/glob family shapes: 2, 73,
500, 508 — an authored actor placement) versus `npcnum(field-reuse):N` (a
teleport/monster egg's incidental field value). None of the field-reuse hits
observed in the current build land on a manifest-pinned LV class id — but if
a future monster egg's spawn count or teleport's dest_npc value happens to
equal one of ours, that class would fire unintentionally when the egg
resolves. Worth checking when placing new eggs in the 1-450ish count/npc
range.

## Known blind spot: the savegame

The engine's *other* permanent-NPC dispatch path — `objId < 256` with
`EXT_PERMANENT_NPC` set → `class_id = objId + 1024` — is a **runtime**
object id assigned when a savegame's item hierarchy is built, not something
stored in FIXED.DAT. This tool has no savegame to read (and wouldn't want to
depend on one — the manifest's M0.6 note calls out that "one savegame reset"
already accompanied the bit-1024 rebase; that's a real, changing artifact,
not a build input). A base-game class that is reachable *only* via this path
will show as a false orphan in the count-only base-class summary. This does
not affect the LV orphan list, which is why PLAN 2.1 and this tool both
scope the audited claim to "reachable by the mechanisms below" rather than
"reachable, full stop."

## Anomalies: flag bits beyond engine capacity

`UCMachine` allocates its global flag state as `BitSet(0x1000)` — 4096 bits.
A `push global` / `pop global` referencing a bit at or past 4096 cannot be a
real flag access. The tool treats this as a structural sanity check
independent of the manifest and reports it separately from the ordinary
flag table.

The first run against the current build (2026-07-03) found exactly one: bit
21064 in **ATLI** (class 1131), bytecode offset `0x853B`. Manually
inspecting the raw class bytes around that offset shows the disassembler
decoded a real, addressable `push global 5248h 03h` (0x4E) followed by a
`pop byte` and then two bytes (0xF2, 0xFC) that do not exist in the opcode
table at all — a `db` (unknown opcode) fallback in the listing. Comparing
against a byte-identical sibling idiom elsewhere in the same class (the
"subtract an already-asked option from the ask list" pattern, used for both
"Kill her?" and "More to stop her?" in ATLI's dialogue tree) shows the
sibling ends its idiom with a 3-byte `jmp`, while this occurrence's `01 FC`
(`pop [BP-04h]`) is followed directly by these 15 bytes before recovering
into a clearly valid `push string "But Ragnar is a Hoskuld!"` at `0x854A`.
That is consistent with 15 stray bytes spliced into otherwise-correct
bytecode — a suspected usecode-compiler codegen defect (the same class of
bug as the already-fixed `_find_safe_insertion()` string-operand misparse
noted in M0.6's devlog), **not** a flag-graph tool bug: the anomalous bit
value (21064, an order of magnitude past the 4096-bit capacity) is the
tell, and it is derived from the disassembler's own precise instruction
walk, not a heuristic.

This tool does not fix it — ATLI's source lives under the usecode-compiler
agent's directory, out of scope here (CLAUDE.md's agent-directory boundary,
and another agent is working there in parallel). It is reported so the
compiler team can decide whether to re-run codegen on ATLI or patch the
byte range directly. Because ATLI is one of the seven already-"verified"
NPC dialogues (PLAN.md section 0), this is a live, in-game-reachable
defect, not theoretical: the "Kill her?" ask option is real dialogue.

## Re-running after future builds

The tool takes no manifest edits and makes none — it is purely a reader. Any
rebuild of `EUSECODE.FLX` (and, less often, `FIXED.DAT` or `TYPEFLAG.DAT`)
should be followed by a re-run to keep `shared/docs/wiring-data.md` current;
nothing currently does this automatically (see "Running it" above re: build
gate integration).

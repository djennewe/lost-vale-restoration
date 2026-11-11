# Adversarial Code Review, 2026-07-19

Multi-agent hostile audit of the entire Lost Vale toolchain at working-tree state
`cdc7b28` plus the uncommitted 2026-07-19 changeset. Method: 16 module finders
(one per subsystem or cross-cutting lens), deterministic dedup, then two
independent skeptics per finding with a third tie-break vote on splits. 92
agents total. Findings below are only those that survived verification;
2 findings were refuted by skeptics and are listed at the end, since both
refutations carry useful information.

**Totals: 35 confirmed (3 critical, 10 high, 22 medium), 23 low-severity
reported unverified by design, 2 refuted.** One finder (packer-build:
`u8_flx_packer.py`, `build_eusecode.py`, `patch_mythran.py`) returned a
malformed stub and was re-run separately; its results are in the addendum at
the bottom.

A deliberate scope note: facts already documented in CLAUDE.md, PLAN.md, or the
known-limitations list were not treated as findings. Drift between those
documents and the code was.

---

## Progress log (living)

Updated 2026-07-24. This section tracks work against the findings below; the
findings text itself is preserved as the point-in-time audit record, with
inline `**Status:**` notes on individual items where they have moved.

**Resolved**
- **C2** — shield half 2 restored to `frame=1` (commit `9acf0e6`). Rebuilt
  FIXED.DAT verified: halves at frame 0 / frame 1, matching SHADES.UNK.
- **M13** — the contradictory shield comment block collapsed to one correct
  block (`9acf0e6`).
- **L22** — the `givenElixir` vial-dupe is closed, not merely reverted:
  `givenElixir`/`iAmDrunk` are now real manifest-pinned flags (bits
  1827/1828) via `lv-patched/FLAGS.UNK`, with a dialogue-harness assertion
  and negative control (`9acf0e6`).

**Investigated, held as a written finding (not yet fixed)**
- **H1** — confirmed real and the exact `startup{}/process{}` semantics were
  reverse-engineered from base-game bytecode. Fix specified but NOT applied
  (VM-contract change needing in-game timing verification). See
  `docs/reviews/2026-07-23-h1-process-block-semantics.md`.

**Also landed alongside** (not numbered findings): the Shield SI_FIXED
unblock (580→539), the EQ_* equip constants (which also fixed EQ_BACKPACK in
FREE/MAGNET), Map 17/18 shape-400 "fire field" swaps, a `build_eusecode.py`
unknown-arg guard, and the Zealans/Gunnars spelling sweep. All in `9acf0e6`;
this review and the research/plan docs are committed in `e248d39`.

- **C1** — compound-assignment miscompile fixed (`_gen_assignment` now emits
  add/sub/concat/read-modify-write; regression test 8/8; LVFREE re-emits real
  arithmetic). See its inline Status below.

- **C3** — ScummVM engine patches now tracked in `tools/scummvm-patches/` and
  applied by a SHA-pinned clone that fails loudly on drift; `--clean` is safe.
  Also closes M17. See its inline Status below.

- **H4/H5/M12** — map pipeline hardening done: z serialization is
  engine-faithful (unsigned) and byte-safe with negative-z placements
  surfaced for in-game grounding; a dangling teleport now fails the build;
  monster eggs spawn real creatures. See inline Status notes.

- **M9/M10/M11** — map build gates closed: duplicate teleport ids fail the
  build, floating LV teleport endpoints are ratcheted (pin 5, any new one is
  an ERROR), and a post-save read-back proves the file on disk matches what
  was built. See inline Status notes.

- **H6 + Map 13/17 terrain** — both maps tiled their floors with EMPTY globs,
  so Cloud Cliffs and Cloud City had no ground at all and every arrival pad
  floated. Fixed (globs 49 / 65, summit paved at true tile size), and the
  Map 13 return trigger moved off the corridor to the gate. LV-map validator
  went 11 WARN -> **0 WARN, 0 ERROR**; the M10 pin is now 0.

- **H2/M3/M5/M6/M7/M8** — compiler + test-estate hardening: the operand
  encoder is genuinely exercised (499/516 byte-identical) with its
  disagreements asserted rather than hidden, the manifest cursors are
  guarded, and the three always-green tests now exit nonzero on failure.

- **M2** — trampoline relay insertion now corrects the event table, with a
  synthesized >32KB regression test. Closes the compiler binary-layer tier.

- **P1/P2** — the packer addendum is closed: the build stages and verifies
  before promoting (a failed build can no longer destroy the last good
  artifact), and Gate 7 now covers the highest-precedence source tier.

**Top still-open, by current priority:** H8/H9 test coverage (the FLX packer
and the entire map pipeline are both at zero), M18 a single test runner, then
M22 (tracked Origin binaries) and the docs reconciliation (H10/M20/M21)
before any repo-visibility change. P3/P4 (Mythran test pin, guard traceback)
remain as low-value cleanups. Also open and quest-relevant: **H6** (Map
13 return trigger sits on the forced climb path) and the two arrival DESTs
flagged by the M10 ratchet, which both want real Map 13/17 terrain.

---

## Critical

### C1. Compound assignment silently miscompiles to plain assignment
`agents/usecode-compiler/src/u8c_codegen.py:1147` (found by codegen-lang)

**Status (2026-07-24): RESOLVED in `cea91f1`.** `_gen_assignment` now
handles compound ops on numeric locals (`push var; push rhs; add/sub; pop
var`), String locals (`+=` -> the base-game concat idiom), and globals
(read-modify-write); `^=` on a non-slist target warns instead of
miscompiling. Operand order verified against uc_machine.cpp (sub 0x1C =
first-second) and base-game DOOR_NS. Regression test
`test_compound_assign.py` (8/8). Rebuilt FLX grew +189 bytes of restored
arithmetic; LVFREE (0x05AE) now emits real add/sub at quan-=666 etc.

In `_gen_assignment` the compound-op branch is gated on `name in
self._slist_locals`. A numeric or String local using `+=`, `-=`, or `^=` skips
it and falls into the plain-assignment path, which never inspects `asn.op`: it
evaluates the RHS and `pop_bp`s it, emitting no add or subtract. So `x += 16`
becomes `x = 16`, and `sentence += "?"` frees the old string and stores only
`"?"`. The global-flag path (line 1138) ignores `asn.op` the same way. No
warning is emitted.

Verified by compiling `x:Number=5; x+=16; x-=3;` which yields `0a10 01fe / 0a03
01fe` (push 16, pop; push 3, pop) with no arithmetic opcode. The shipped `LOST
VALE/FREE.UNK` does `quan-=666`, `x+=16`, `y-=16`, `remainder-=quan`, `ran+=a`,
`charge+=mana/5`: quantities, coordinates, and accumulators are overwritten
instead of adjusted, corrupting `give()`, spell charge, and movement math
in-game.

Fix sketch: in the local branch handle non-slist `+=`/`-=` (push `[BP+off]`,
eval RHS, emit `0x14`/`0x1C`, `pop_bp`); String `+=` emits concat `0x16`;
read-modify-write for globals; at minimum `_warn` on any unhandled compound op.

### C2. Shield half 2 placed at frame=2, which the reforge usecode cannot see
`agents/map-populator/src/build_map_17.py:459` (found by maps-b, in the uncommitted changeset)

**Status (2026-07-24): RESOLVED in `9acf0e6`.** Verified against source:
SHADES.UNK:47/52 match on `getFrame()=0`/`=1`. Half 2 restored to `frame=1`;
rebuilt FIXED.DAT confirms the two halves at frame 0 (q81) and frame 1 (q82).

The edit changed Memorial Hall shield half 2 from frame=1 to frame=2 for visual
distinctness, reasoning that quality carries identity. But the quest keys on
frame: `SHADES.UNK:44-56` finds halves via `type=TypeAOFrizbee` then
`getFrame()=0` for Frizbee1 and `getFrame()=1` for Frizbee2. A frame-2 item
matches neither, `found2` stays false, and the reforge ceremony calls
`Frizbee2.destroy()` on an unset referent, never consuming the real half.
`shieldFixed` is still set true, and `ZEALSHLD.UNK::look()` labels the frame-2
broken half with the restored shield's name. Half 1 (frame=0) is fine. The
placement validator only checks frame < framecount (539 has 4 frames), so this
is invisible to it.

Fix sketch: restore frame=1 for half 2; do not encode identity in the frame
field for visual reasons. (Note: the companion comment at lines 78-87 is also
wrong; see M-13.)

### C3. build_scummvm.sh reapplies only the detection table; the engine patches exist nowhere else
`build_scummvm.sh:80` (found by infra-scummvm)

**Status (2026-07-24): RESOLVED.** The engine work (npcNum dispatch in
item.cpp, NPC Actor promotion in map.cpp, a resetRef debug line in
kernel.cpp) is now a tracked patch `tools/scummvm-patches/0001-lost-vale-engine.patch`
(+78 lines, detection-table hunks excluded since the script regenerates
those). `build_scummvm.sh` pins the clone to the base SHA `01bd8879`, applies
the patch after clone, and `exit 1`s if any hunk fails to apply. `--clean` is
now safe: a rebuild re-fetches and re-applies. Validated end-to-end against a
fresh GitHub fetch of the pinned SHA. Also addresses **M17** (clone pinned to
a tested SHA).

The script's sole patch target is `detection_tables.h`. The engine changes that
make the expansion function at all, `item.cpp` (+23, npcNum+1024 dispatch with
egg-family exclusion) and `map.cpp` (+54, NPC Actor promotion), live only as 7
commits inside the gitignored `scummvm-lv/` checkout. No .patch or .diff file
in the tracked tree backs them up. A fresh clone patched only for detection
builds an engine that detects and launches Lost Vale but has no NPC dispatch:
every LV NPC is silently mute. Worse, `--clean` (line 29) is `rm -rf
scummvm-lv`, which deletes the only copy of those commits; a subsequent rebuild
clones stock master and the engine work is gone.

Fix sketch: `git format-patch` the 7 commits into a tracked
`tools/scummvm-patches/` series; have `build_scummvm.sh` apply them after
clone and fail loudly if any hunk does not apply.

---

## High

### H1. The uncommitted process-block change likely runs puppet processes once, not per tick
`agents/usecode-compiler/src/u8c_parser.py:380` (parser-front, uncommitted changeset)

**Status (2026-07-24): CONFIRMED, held as a written finding.** Proven from
base-game bytecode (puppet has no back-edge; 634 suspend-loops, 97
bare-suspend per-tick monitors, DOOR_NS/LITZAPEW). `startup{}/process{}` =
loop once per tick with an implicit `suspend`. Fix specified but NOT applied
(would hang shieldMonitor/candle/magnet monitors if done naively; needs
in-game timing verification). Full writeup:
`docs/reviews/2026-07-23-h1-process-block-semantics.md`.

The 2026-07-19 diff flattens `startup {}` / `process {}` bodies into the
function body as ordinary blocks, and codegen emits them linearly with ret at
the end and no loop-back. LORDBRIT's `process {}` is an animation stepper
(`fram++`, `wait(5)`, `setFrame(fram)`) with an `if lbDone=1 { return }` exit
that only makes sense inside a loop. As compiled, the ghost sets one frame,
waits once, and the process dies. The diff's "byte-for-byte known-good" claim
rests on a source form no prior build actually compiled. Needs a disassembled
base-game puppet comparison plus in-game verification per PLAN's
definition of done.

### H2. Round-trip "full assembly" short-circuits to raw hex; the encoder is never tested
`agents/usecode-compiler/src/u8_assembler.py:518` (assembler-roundtrip)

**Status (2026-07-25): RESOLVED.** New `assemble_class_encoded()` runs the real
encoder, and `test_encoder.py` drives it over the whole base FLX: **499/516
classes reassemble BYTE-IDENTICAL through `_encode_operands`**. Encoder
disagreements are no longer silently overwritten by raw hex (that was L8) —
they are recorded in `encoder_mismatches` and asserted on, so a sign/endian/
width bug now fails the test. Two limits are pinned and ratcheted, both
properties of the text listing rather than encoder bugs: 7 instructions whose
non-ASCII string bytes the disassembler already destroyed with
`ascii, errors='replace'` (u8_usecode_disasm.py:610, do-not-modify by rule),
and 17 classes unparseable from text (16 multi-line strings, 1 out-of-range
jump offset). `test_roundtrip.py` now states plainly that its Phase 2 shares
the raw-hex path and points at test_encoder for real encoder coverage.

`assemble_bytecode` copies `instr.raw_hex` byte-for-byte whenever present, and
the disassembler emits raw hex on every line, so `_encode_operands` and every
operand parser are dead code on the validation path. Phase 2 of
`test_roundtrip.py` is behaviorally identical to Phase 1's raw copy. The
"516/516 round-trip" cited in PLAN.md proves hex can be re-copied, not that the
assembler can encode anything. Any sign, endian, or length bug in the encoder
passes silently.

### H3. Orphan detection drops all 0x58 spawn-inline call edges
`agents/usecode-disasm/src/u8_usecode_disasm.py:827` (copies-drift)

`disassemble_class_summary` tallies call edges from `0x11` (call) and `0x57`
(spawn) but has no branch for `0x58` (spawn inline). `u8_flag_graph.py` builds
its inbound-reference counts purely from that summary, so a class invoked only
via spawn-inline scores zero inbound and is reported orphaned. The base FLX
contains 20 real 0x58 edges across 8 classes. This poisons exactly the
reachability audit PLAN 2.1/2.3 depends on to prevent the project's worst
defect class. (The disassembler is do-not-modify by rule; the fix belongs in
the summary layer or a downstream shim, or as a deliberate rule exception.)

### H4. Map item z is packed signed while the engine reads it unsigned
`agents/map-populator/src/u8_map.py:62` (map-core)

**Status (2026-07-25): FULLY RESOLVED.** The 49 stray placements are now
DELETED (44 on Map 10, 5 on Map 17) after an isometric render decomposed the
layers and proved them redundant AND visibly wrong: they rendered as debris
floating ~253 units above the lake. The real lake body is glob-based (1,026
SEA tiles at z=0) and all 21 stray water items were already covered by it, so
nothing was lost; Map 17's five were "fall damage" tiles that at z=252 had
never been functional. FIXED.DAT 96,948 -> 96,899 items, walkability 90/90,
zero items at z>=250 on either map.

Serialization half (2026-07-24):
`from_bytes` now reads z unsigned (`<B`) and `to_bytes` writes unsigned with
a `[-128,255]` range guard; 4,258 high-z base items round-trip cleanly and
FIXED.DAT is byte-identical (no placement moved). The `z>200` validator WARN
was NOT re-aimed as the plan suggested — the base game legitimately places
6,229 items (552 on Map 8) at z>200, so a post-serialization threshold only
floods. Instead the genuine LV signal (a builder passing negative z, which
serializes to a ceiling byte) is flagged pre-serialization in build_all_maps
as a NOTE: 44 items on Map 10, 5 on Map 17 want an in-game grounding check —
base water sits at low z, so these likely render near the ceiling.

`from_bytes` uses `<b` and `to_bytes` packs `z` signed (-128..127), but the
engine treats z as an unsigned byte: 6,229 base-game items carry raw z > 127,
and the map_11 devlog itself records z=-2 rendering as z=254. Consequences:
negative z from a builder serializes to a ceiling-height byte and renders in
the void; the z>200 ceiling WARN in `map_validate.py:332` is unreachable dead
code (loaded values are capped at 127 or negative); and any legitimate high z
in 128..255 crashes `to_bytes` with struct.error. Fix: pack `<B` both ways,
reject z<0 at build time, re-aim the validator at raw unsigned range.

### H5. Teleport-pair verification failure does not gate the build
`agents/map-populator/src/build_all_maps.py:262` (map-core)

**Status (2026-07-24): RESOLVED.** `verify_teleport_pairs` failure now
`sys.exit(1)`s before `archive.save()`, mirroring the item-validator gate — a
dangling teleport can no longer ship.

`verify_teleport_pairs` detects missing triggers, missing destinations, and map
mismatches, but `main()` prints one WARNING line and proceeds to save FIXED.DAT
and exit 0. A dangling teleport is a hard progression breaker and deserves the
same fatal gate the item validator already has.

### H6. Map 13 return teleport sits on the forced climb path
`agents/map-populator/src/build_map_13.py:94` (maps-a)

**Status (2026-07-25): RESOLVED.** TRIGGER 207 moved 1024 units WEST, level
with the arrival pad, at (3072,11776). Arrival DEST 206 (4096,11776) and the
locked gate (4096,10752) share x=4096, so the route north to the objective no
longer crosses the return trigger; going back to the Vale is now a deliberate
walk to the side. Separation from DEST 206 is 1024, well over the 384 minimum.

Arrival from Lost Vale lands at DEST 206 (4096,11776); the only objective (the
locked gate, then the climb) is due north at decreasing y. Return TRIGGER 207
is at (4096,11264), directly between them at the same x. Walking north fires
it and bounces the player back to Map 10, making Cloud City unreachable. Maps
8, 9, and 11 all received explicit 2026-07-04 clearance relocations; this pair
did not.

### H7. GlobPrefab.stamp adds origin_z instead of subtracting it, floating glob houses
`agents/map-populator/src/glob_catalog.py:250` (villages)

The Stampable contract grounds a structure by subtracting `origin_z`
(BuildingPrefab does `z_base - origin_z`). GlobPrefab places the egg at
`z_base` verbatim while `generate_village` passes `origin_z` as `z_base`, so
the engine renders glob items at `origin_z + g.z`. HOUSE_GLOBS 573/575/538/537
have min z=40 and float roughly 80 units above the terrain grid; globs
1007/1011 (min z=0) sit correctly, making village heights inconsistent.

### H8. FLX packer has zero automated coverage
`agents/usecode-compiler/src/u8_flx_packer.py:358` (test-gaps)

No test imports the packer. `FlxWriter.build()` offset-table math and the
retired reclaim-before-place allocator are exercised only by full builds, and
`test_manifest`'s md5 comparison proves determinism, not correctness: two
identically wrong builds still pass. A synthetic pack-reread-compare test plus
an oversized-replacement case would close it.

### H9. The entire FIXED.DAT pipeline is untested
`agents/map-populator/src/build_all_maps.py:175` (test-gaps)

Zero test files exist under map-populator or map-builder: no
`MapItem.to_bytes/from_bytes` round-trip, no validator rule regression, no
teleport-pair test, no shape-injection test. Given the project already shipped
12 wrong shape constants and the z-signedness defect above, this is the
highest-value test gap in the repo.

### H10. CLAUDE.md orders agents to maintain a dashboard that does not exist
`CLAUDE.md:118` (docs-drift)

CLAUDE.md and PLAN.md both direct agents to update a root MEMORY.md at each
milestone; commit 5cec802 (2026-03-28) moved it to `docs/MEMORY.md`, which
still self-describes as the root file and is frozen at 2026-03-21 (4 agents, 32
LV classes, phase 4c pending). The live dashboard duty devolved to TODO.md
without any doc saying so. A fresh coordinator following the documented
protocol reconstructs a three-month-old project.

---

## Medium

Grouped by area. Each is confirmed by two skeptics.

**Compiler and simulator**

- **M1. switch/case subject parsed with `_parse_primary` leaks postfix tokens**
  (`u8c_parser.py:664`, parser-front). `switch obj.field {` leaves `.field` in
  the stream; recovery then discards the entire switch. Same truncation class
  commit 7e6a19c fixed for casts and foreach, unfixed for switch. Latent (no
  current LV source triggers it).
- **M2. Trampoline relay insertion never shifts event-table offsets**
  (`u8c_codegen.py:588`, codegen-binary). Relays shift labels, string ranges,
  instr starts, and fixups, but not `self.events` (nor literal same-class
  call/spawn offsets). Any >32KB class whose relay lands below a later event
  handler dispatches that event 6 bytes early per relay. ATLI survives only
  because its overflow sits in the final function. Gate 6 cannot see it.
  **Status (2026-07-25): RESOLVED.** Each event handler's start is now also
  marked with an `__event_N` label, and `build_class()` reads the corrected
  offset back out of `_labels` before writing the table. Labels are shifted
  in place at every splice, so this reuses machinery already proven correct —
  deliberately NOT a replay of the insertion log, whose recorded positions are
  not mutually comparable (relays are spliced end-to-start, so a later,
  lower-positioned splice also moves an earlier-logged one). New
  `test_trampoline.py` (5/5) synthesizes a >32KB class with handlers after the
  overflow and asserts every event entry lands on an instruction start; its
  padding uses 4-byte instructions on purpose, since 6 % 4 != 0 makes an
  uncorrected offset land strictly mid-instruction (with 1-byte padding the
  assertion passes even with the bug — verified). Negative control: reverting
  the fix fails both the boundary and the shift assertions.
  The review's diagnosis was confirmed exactly: ATLI inserts **12 relays**,
  the earliest at code +1677, while all 6 of its handlers sit at +128..+651 —
  so the correction is a no-op today and EUSECODE.FLX is byte-identical. Pure
  luck of layout, now guarded.
  (The "literal same-class call/spawn offsets" half was already safe: those go
  through `funcoffset` fixups, which Step B re-patches on every pass.)
- **M3. Class-id allocation lacks the pin guard the flag path has**
  (`u8c_symbols.py:844`, symbols-manifest). A corrupted or hand-edited
  `next_free.class_id` can silently reuse a reserved-but-uncompiled pinned id
  (e.g. EGGCOLUMNPUZZLE=1449). `check_new_allocations` covers flags only;
  `validate()` never inspects cursors. **Status (2026-07-25): RESOLVED.**
  `lv_manifest.validate()` now asserts BOTH cursors sit past every pin
  (class_id and global_bit) and that the class cursor is not itself pinned.
  Negative control: a cursor rolled back to the top pin is detected on all
  three counts. One existing fixture needed updating — widening the top flag
  pin also has to advance the cursor to stay structurally consistent.
- **M4. Simulator `_run_child` resolves the spawned `this` against the zeroed child stack**
  (`u8c_sim.py:455`, sim-fidelity). On followed spawns the stack is swapped
  before `ptr_to_object(thisptr)` runs, so the common `push dword [BP+06]`
  pattern yields objid 0 with no warning: children run with null `this` in the
  sim but a real item in-game. One more way sim-green can diverge from
  game-green.

**Exit-code discipline (the "build cannot fail" class, still alive in the test layer)**

- **M5. `test_roundtrip.py` exits 0 even when classes fail** (line 192).
  **Status (2026-07-25): RESOLVED** — exits 1 if either phase reports failures.
- **M6. `test_new_dialogue.py` exits 0 on compile failures** (line 22).
  **Status (2026-07-25): RESOLVED** — exits 1 on any compile failure, and on
  finding no .UNK files at all.
- **M7. `test_parser_all.py` has no asserts, always exits 0, and vacuously
  passes when the gitignored corpus is absent** (line 49).
  **Status (2026-07-25): RESOLVED** — a missing corpus is now a hard failure
  (it "passed" having parsed nothing), and parse issues are ratcheted at the
  2026-07-25 baseline of 23. Zero was not demanded: the sweep covers the whole
  recovered corpus including base-game /U8/ sources the build never compiles.
  Per-file ratcheting for shipped files remains build Gate 7.
- **M8. `u8_assembler.py _parse_listing` silently drops instruction lines that
  fail its regex** (line 343): standalone assembly writes a truncated class
  with a success message. **Status (2026-07-25): RESOLVED.** A line that
  starts like an instruction (`XXXX:`) but fails the full regex is recorded in
  `parse_drops` instead of skipped; `test_encoder.py` fails on any drop.
  Currently 0 across the base FLX.

**Maps and world**

- **M9. Duplicate teleport ids are masked by dict overwrite**
  (`build_all_maps.py:98`): two triggers with the same id and only the last is
  verified; duplicates ship unreported. **Status (2026-07-25): RESOLVED.**
  Collection uses lists per id and a duplicate fails the build (via the H5
  gate). Also added: an id inside the documented LV range 200-213 that is
  missing from TELEPORT_TABLE now fails rather than being skipped silently —
  scoped to that range, since the Map 22 shape gallery carries a debug dest at
  id 250 that must not break the build. Negative control: an injected
  duplicate id 201 is caught.
- **M10. Floor-support under LV teleports is WARN but a comment claims ERROR**
  (`map_validate.py:273` vs 338): a floating teleport destination has no hard
  gate at all. **Status (2026-07-25): RESOLVED.** The misleading "(ERROR)"
  comment is corrected and a RATCHET gates it: floating LV teleport endpoints
  are tagged `LV_TELEPORT_NO_FLOOR` and pinned at
  `KNOWN_FLOATING_LV_TELEPORTS`; any increase is a build-blocking ERROR, a
  decrease prints a reminder to lower the pin. **The pin is now 0** — the same
  day, all 5 were traced to EMPTY terrain globs (Map 13 GLOB_CLIFF_BASE 50,
  Map 17 GLOB_STONE_FLOOR 75) and fixed, so a floating teleport can never
  ship again. Straight escalation was NOT
  possible — 5 real violations already exist on the incomplete Map 13/17 cloud
  terrain, and two are arrival DESTs (id 206 from Lost Vale, id 208 into Cloud
  City) that drop the player into a void. Those want real terrain when Maps
  13/17 are finished.
- **M11. Post-save verification prints counts but asserts nothing**
  (`build_all_maps.py:323`): a builder returning a truncated list shrinks or
  deletes a map and the build still exits 0 with a silently smaller FIXED.DAT.
  **Status (2026-07-25): RESOLVED.** Every modified map records its intended
  count; after save the file is re-read and each count compared, plus a
  per-map baseline check that untouched base maps survived intact. A mismatch
  prints the offending maps and exits 1. Confirmed live: it fired the moment
  maps 8/39 were misclassified as untouched.
- **M12. LV monster eggs pass raw small qualities, not the packed
  `(prob<<11)|monster_shape` format** (`build_map_13.py:323`, also maps 09 and
  11). Quality 40 decodes to monster shape 40, a terrain shape, with spawn
  bits 0. Harpie zone, Galjeron's lair, and every elemental section spawn
  nothing or garbage actors instead of the intended creatures. **Status
  (2026-07-24): RESOLVED.** `MapItem.monster_egg` now takes `monster_shape` +
  `prob` and packs `(prob<<11)|shape`; all 12 sites pass real family-6 base
  creatures at prob 6 (lv_shapes.SHAPE_MON_*: troll/ghoul/kith/spider/golem/
  seeker/daemon/skellot — v1 stand-ins, harpie needs art). Validator rule
  added (family-6 + nonzero prob) and confirmed to catch a broken egg.
  **Follow-up (2026-07-25):** rendering every pick caught a bad one before any
  playtest — shape 76 "kith" is a large SPIDER, not winged, so it was wrong as
  the Cloud Cliffs harpie stand-in; swapped to 120 "torax" (a winged insect).
  A sweep of all 43 named family-6 shapes found NO winged/bird creature in U8,
  confirming a real harpie needs new art. Also noted: frame 0 is often not a
  standing pose (golem 214 frame 0 is rubble), so judge picks on a frame
  spread, not frame 0.
- **M13. The new Map 17 shield comment contradicts the fix it accompanies**
  (`build_map_17.py:78-87`, uncommitted): claims the halves are still
  unpickable on shape 580 and prescribes moving to 828, all false against the
  same diff's SHAPE_SHIELD=539 and the current TYPE_SHAPES. A maintainer
  acting on it would re-break the quest. **Status (2026-07-24): RESOLVED in
  `9acf0e6`** — the two stacked comments collapsed into one correct block.
- **M14. `build_villages.py --write` appends villages to FIXED.DAT every run**
  (line 154): non-idempotent, duplicates entire villages on a second run, and
  mutates the artifact build_all_maps owns.

**Infrastructure and docs**

- **M15. Retired --stealth is still advertised by install_lv.sh and play.sh**
  (install_lv.sh:264 and play.sh): both steer users to a build mode that now
  exits nonzero by design.
- **M16. `install_lv.sh --clean` can restore EUSECODE but fail on FIXED.DAT's
  missing .bak** (line 90), leaving vanilla usecode over LV maps.
- **M17. ScummVM built from unpinned master via depth-50 clone**
  (`build_scummvm.sh:73`): the detection-insert markers and engine ABI can
  drift; the build is not reproducible across dates.
- **M18. No CI and no single runner: the real-assert quest tests run only if a
  human remembers** (`tools/cleanroom_test.sh:247` runs 3 of 9 test files).
- **M19. sint16 boundary and trampoline insertion have no targeted test, and
  the built EUSECODE.FLX is never round-tripped** (`u8c_codegen.py:323`).
- **M20. CLAUDE.md artifact stats are wrong** (line 46): claims 48 maps and
  92,954 items and 1431+34 classes; the tree holds 49 maps, 96,948 items, 1458
  FLX entries. Four documents carry four different superseded counts.
- **M21. HANDOFF.md (2026-04-04) contradicts TODO/PLAN on Map 8 doors, NPC
  status, and artifact sizes** (line 57): every one of its Next Steps is
  already done; following it would undo verified work.
- **M22. The four merged game-data artifacts in shared/build are git-tracked**
  (.gitignore:24): EUSECODE.FLX, FIXED.DAT, TYPEFLAG.DAT, U8SHAPES.FLX (~18 MB
  of Origin-derived bytes) violate PLAN 4.3's pre-visibility requirement; a
  history purge is needed before any release or repo visibility change.

---

## Low severity (reported without skeptic verification, by design)

| # | File:line | Title |
|---|-----------|-------|
| L1 | u8c_parser.py:879 | Malformed numeric literal raises uncaught ValueError, aborting the file compile |
| L2 | u8c_parser.py:767 | Non-associative comparison drops a trailing operator into recovery |
| L3 | u8c_codegen.py:1043 | `break` inside while/for/foreach compiles to nothing |
| L4 | u8c_codegen.py:1837 | Integer literal below -128 pushed as dword, misaligning the 16-bit stack |
| L5 | u8c_codegen.py:451 | Phase-1 undefined-label check degrades later errors to bare KeyError |
| L6 | lv_manifest.json:940 | retail_shared tags computed from stale source dirs, not lv-patched |
| L7 | u8c_symbols.py:50 | TYPE_SHAPES audit note cites a non-existent entry and wrong count |
| L8 | u8_assembler.py:560 | Encoder silently substitutes raw hex when its own encoding disagrees |
| L9 | parse_typeflag.py:129 | is_empty ignores byte2/4/5, treating nonzero shapes as empty |
| L10 | u8_usecode_disasm.py:693 | 0x5C symbol decode fixed 9-byte name never validated by round-trip |
| L11 | test_uc_plntst.py:144 | "no Mark item" check is a tautology (TypeZealMark absent from TYPE_SHAPES) |
| L12 | u8_map.py:234 | save() writes FIXED.DAT non-atomically over the previous good build |
| L13 | build_map_09.py:103 | teleport_dest writes the source map into mapnum, contradicting map-format.md |
| L14 | lv_wood_wall.py:32 | Shape 855 exported but never injected or TYPEFLAG-patched |
| L15 | lv_wood_wall.py:448 | inject_shape only warns on a non-empty target slot, then overwrites |
| L16 | cleanroom_test.sh:35 | Hardcoded absolute user path for game data |
| L17 | install_lv.sh:140 | No pre-install hash check before overwriting game files |
| L18 | agents/map-populator/MEMORY.md:47 | Agent MEMORY.md files describe a different codebase |
| L19 | CLAUDE.md:31 | Omits the load-bearing lv-patched/ dir; Ragnar limitation stale |
| L20 | lv-patched/PLNTST.UNK:24 | Comment "compiler drops startup/process blocks" falsified by this changeset |
| L21 | lv_manifest.py:172 | Stored indent=1 vs save() indent=2: next programmatic append reformats ~3220 lines |
| L22 | lv-patched/EZREKAL.UNK:3322 | givenElixir guard revert re-opens the vial dupe for mid-window saves |

(A 23rd low entry was stub output from the failed packer-build finder and was
discarded.)

## Refuted findings (verification working as intended)

1. **"Round-trip never validates LV classes, so a malformed class ships"**
   (assembler-roundtrip): refuted because `build_eusecode.py` Gate 6b
   disassembles every added, replaced, and manifest-pinned class in the written
   FLX and blocks the detection-table update on any failure. The narrower
   observation (the assembler encoder is dead code) survived as H2.
2. **"iAmDrunk newly live activates ~30 untested branches and can stall step
   11-12"** (worktree-diff): refuted; the elixir-handover entries sit outside
   the drunk gate, the drunk chain itself reaches the key handover, and
   `leaveFastArea()` resets the flag. The coverage-gap observation is real but
   the claimed stall cannot occur.

## Module health summaries

| Module | Verdict (compressed) |
|--------|----------------------|
| parser-front | Sound; truncation-class hardening real. One open question: the uncommitted process-block change (H1) needs in-game proof. |
| codegen-lang | Lowering, ask dispatch, spawn conventions, loopscripts all match uc_machine.cpp. Compound assignment (C1) is the exception. |
| codegen-binary | Trampoline machinery careful; _find_safe_insertion fix genuine. Event-table shift (M2) is the latent hole. |
| symbols-manifest | Pin manifest internally consistent; flag side hardened; class-id side lacks the same guard (M3). |
| assembler-roundtrip | Header and event-table reconstruction faithful, but the encoder half is dead code (H2) and the CLI drops bad lines (M8). |
| packer-build | Finder failed with stub output; re-run separately (see addendum). |
| copies-drift | All duplicated modules byte-identical to canonical. Disassembler untouched since the rule. 0x58 gap (H3) is in the summary layer. |
| sim-fidelity | Faithful port overall; followed-spawn `this` bug (M4); two tests cannot fail (M6, M7 family). |
| map-core | Byte-level round-trip correct except signed z (H4); gates porous (H5, M9, M10, M11). |
| maps-a | Single-sourcing discipline holds; egg recipe matches manifest. Map 13 teleport bounce (H6) and egg quality encoding (M12) are the real problems. |
| maps-b | The 17/18 art swaps are sound and quest-coherent except shield half 2 frame (C2) and the contradicting comment (M13). |
| villages | Well-instrumented; z-semantics disagreement floats half the glob pool (H7); injector non-idempotent (M14). |
| infra-scummvm | set -euo pipefail discipline present, but the patch-survival trap (C3) plus stealth advertising, unpinned clone, and non-atomic restore. |
| test-gaps | Compiler manifest/patch logic well covered; packer and map pipeline at zero; several tests cannot fail; no runner or CI. |
| docs-drift | TODO.md current; CLAUDE.md, HANDOFF.md, docs/MEMORY.md, agent MEMORYs frozen months behind with contradicting numbers. |
| worktree-diff | Changeset safe to commit on savegame invariants (manifest append-only, detection hash unchanged, flags consistent) once C2/H1/M13 are addressed. |

## Addendum: packer-build re-run

The original packer-build finder failed with stub output and was re-run as a
single high-effort agent. Its findings did NOT pass through the two-skeptic
verification the rest of this report had, but the agent verified each claim
read-only against the tree (including hash comparisons against the real base
archive), so treat these as high-confidence single-source.

**Module health:** the load-bearing machinery is sound. FLX header, offset,
and count math is correct against the real 1433-entry base archive; the
quest-critical gate is double-covered (compile-time Gate 4 plus post-write
disassembly Gate 6); the compile-failure allowlist is exactly EALOGO and
TJORVI; the Mythran use-offset and preamble-hash guards are correctly
calibrated (pinned sha256 and md5 both verified against
shared/data/USECODE.FLX); and the retired reclaim-before-place
`write_stealth()` allocator is confirmed unreachable from `--full` (no
callers).

- **P1 (medium)** `build_eusecode.py:666`: Gate 7, the statement-drop ratchet
  built after EZREKAL once shipped with its conversation silently dropped,
  iterates every source tier EXCEPT `lv_patched_results` (and double-counts
  provider_results). The `LOST VALE/` copies of patched basenames are skipped
  from compilation, so recovered parse errors in a patched source are
  unbounded. Dormant today (all four patched files parse clean), but a
  hand-edit slip in lv-patched/EZREKAL.UNK would drop statements and ship
  with exit 0: the exact recurrence the ratchet exists to prevent.
  **Status (2026-07-25): RESOLVED.** `lv_patched_results` added to the Gate 7
  sweep and the duplicated `provider_results` term dropped (line ~567 already
  does `lv_final_results = list(provider_results)`; harmless since the tally
  takes a max per basename, but misleading). Negative control: a temporary
  lv-patched file with a recovered parse error is now caught and fails the
  build. Census unchanged, FLX byte-identical.
- **P2 (medium)** `u8_flx_packer.py:146`: `write()` truncates the canonical
  shared/build/EUSECODE.FLX in place, and the build calls it BEFORE Gate 6
  disassembly verification. A Gate-6 failure or an interrupted write leaves
  corrupt bytes at the canonical path, destroying the last verified build.
  Fix: build to a temp file, verify, then `os.replace()` on success.
  **Status (2026-07-25): RESOLVED.** The build now writes
  `EUSECODE.FLX.staging`, runs Gate 6 against THAT file, and only
  `os.replace()`s it over the canonical artifact once verification passes.
  A rejected build is quarantined as `EUSECODE.FLX.failed` for inspection and
  the previous good artifact is left byte-for-byte untouched; both byproducts
  are gitignored so a corrupt FLX can never be committed. Negative control:
  a forced Gate-6 rejection exits 1, prints "was NOT modified", leaves the
  canonical md5 unchanged, and skips the detection-table/manifest updates.
- **P3 (low)** `test_patch_mythran.py:71`: the 'real' byte-identity case pins
  flag bits 678/796, but the shipped manifest deploys 1702/1820; the pinned
  hash locks bytes the build never emits, so operand-encoding regressions on
  the deployed offsets would pass.
- **P4 (low)** `build_eusecode.py:838`: the Mythran guards raise ValueError
  with a raw traceback instead of the documented one-line "BUILD FAILED"
  summary (exit stays nonzero; diagnostic consistency only).

# ID Legend

Every `C*`, `H*`, `M*`, `L*`, `P*`, and `DD-*` code used across `CLAUDE.md`,
`PLAN.md`, `TODO.md`, `HANDOFF.md`, the review docs, and source comments.

Created 2026-08-11 because the codes are used in ~350 places and defined in
none of the files that reference them most. **This file is an index, not an
owner** — each code's authoritative text lives in the "defined in" file named
for its family, and the one-line titles below are copied from there. If a
title here disagrees with the source, the source wins.

---

## Read this first: three collisions

The codes were minted independently by different documents and were never
reconciled. Three of them are genuinely ambiguous and must be read from
context.

### 1. `DD-005` means two unrelated things

| Where | Meaning |
|---|---|
| `TODO.md` § Design Decisions | **The temple is entered by SHRINKING**, not by an explosive or a guardian |
| `PLAN.md` §5 | **Mythran graft mechanism** — how LV dialogue grafts onto stock Mythran |

This is the most-referenced code in the repo (~57 uses). All five uses in
`CLAUDE.md` mean the **TODO.md** one (shrinking: the Tiny Tar potion 859,
`FREE.UNK`'s `makeAvatarBig`, `HRODNY.UNK`'s chest key). `patch_mythran.py`
and `dialogue-mythran.md` mean the **PLAN.md** one.

### 2. `DD-*` is two disjoint registries in two files

- **`DD-001`–`DD-005`** — *story and design* decisions, defined in `TODO.md`
  § Design Decisions (an older, shorter copy of 001–003 also sits in the
  archived `docs/MEMORY.md:262-280`)
- **`DD-005`–`DD-011`** — *engineering* decisions, defined in the `PLAN.md` §5 table

They overlap at 005 and nowhere else, so a code ≥ 006 is unambiguously
engineering and a code ≤ 004 is unambiguously story.

### 3. Bare `M1`–`M4` mean Medium finding *or* Milestone

| Context | `M2` means |
|---|---|
| `docs/reviews/2026-07-19-adversarial-review.md`, `TODO.md` finding lists | **Medium finding 2** — trampoline relay insertion never shifts event-table offsets |
| `PLAN.md`, sequencing tables, milestone status | **Milestone 2** — "It looks and plays like 1994 intended" |

Only `M1`–`M4` collide. `M5`–`M22` are always findings; `M0.1`–`M0.8` are
always milestone sub-items.

---

## `DD-*` — decisions

### Story and design · defined in `TODO.md` § Design Decisions

| ID | Decision |
|---|---|
| DD-001 | Tjorvi = Tyorvi (same character) |
| DD-002 | Ancient Temple = Shrine of the Ancient Ones |
| DD-003 | Plot v1.2 wins for trust-gaining mechanism |
| DD-004 | Romeo & Juliet subplot → CUT |
| DD-005 | The temple is entered by SHRINKING, not by an explosive or a guardian |

### Engineering · defined in `PLAN.md` §5 ("Open design decisions")

| ID | Decision | Resolved to |
|---|---|---|
| DD-005 | Mythran graft mechanism | (a) — see `DD-005a` below |
| DD-006 | Stealth mode fate | (b) — see `DD-006b` |
| DD-007 | Event-script dispatch | (a) for event eggs, (b) for SIGRID — see `DD-007a` |
| DD-008 | RAGNAR dead-end fix | (a) — implemented 2026-07-04, `lv-patched/RAGNAR.UNK` change 8 |
| DD-009 | Encounter difficulty | recommended (a), base-game mid-game |
| DD-010 | v1 audio scope | recommended (a), base-track mapping only |
| DD-011 | Release form | recommended (a), build-from-owned-copy installer |

### The letter suffix

A trailing letter names **which option the decision resolved to**, matching
the option labels in the `PLAN.md` section 5 table. This convention is used
in three places and written down in none of them; it is inferred here, and it
holds for all three uses:

| Suffix code | Expands to | Used in |
|---|---|---|
| `DD-005a` | DD-005 option (a) — wrapper routes on `lbDone AND NOT mythranIntroDone`, intro plays once | `patch_mythran.py:33`, `dialogue-mythran.md:31`, `TODO.md:742` |
| `DD-006b` | DD-006 option (b) — keep `--stealth` as an error stub rather than deleting it | `CLAUDE.md:122` |
| `DD-007a` | DD-007 option (a) — UnkEgg quality dispatch (`quality = class − 0x47F`), no engine change | `lv_shapes.py:562,580`, archived TODO (PLNTST egg placement) |

---

## `C*` / `H*` / `M*` / `L*` — adversarial review findings

All defined in **`docs/reviews/2026-07-19-adversarial-review.md`**. Severity
is the letter; the number is position within that severity. Current status is
tracked in that file's "Progress log (living)" section (§23) and in
`docs/reviews/2026-07-19-improvement-plan.md`, **not** here.

### Critical (§97)

| ID | Finding |
|---|---|
| C1 | Compound assignment silently miscompiles to plain assignment |
| C2 | Shield half 2 placed at frame=2, which the reforge usecode cannot see |
| C3 | `build_scummvm.sh` reapplies only the detection table; the engine patches exist nowhere else |

### High (§181)

| ID | Finding |
|---|---|
| H1 | The uncommitted process-block change likely runs puppet processes once, not per tick |
| H2 | Round-trip "full assembly" short-circuits to raw hex; the encoder is never tested |
| H3 | Orphan detection drops all `0x58` spawn-inline call edges |
| H4 | Map item z is packed signed while the engine reads it unsigned |
| H5 | Teleport-pair verification failure does not gate the build |
| H6 | Map 13 return teleport sits on the forced climb path |
| H7 | `GlobPrefab.stamp` adds `origin_z` instead of subtracting it, floating glob houses |
| H8 | FLX packer has zero automated coverage |
| H9 | The entire FIXED.DAT pipeline is untested |
| H10 | CLAUDE.md orders agents to maintain a dashboard that does not exist |

### Medium (§340)

*Compiler and simulator*

| ID | Finding |
|---|---|
| M1 | switch/case subject parsed with `_parse_primary` leaks postfix tokens |
| M2 | Trampoline relay insertion never shifts event-table offsets |
| M3 | Class-id allocation lacks the pin guard the flag path has |
| M4 | Simulator `_run_child` resolves the spawned `this` against the zeroed child stack |

*Exit-code discipline (the "build cannot fail" class)*

| ID | Finding |
|---|---|
| M5 | `test_roundtrip.py` exits 0 even when classes fail |
| M6 | `test_new_dialogue.py` exits 0 on compile failures |
| M7 | `test_parser_all.py` has no asserts and always exits 0 |
| M8 | `u8_assembler.py _parse_listing` silently drops instruction lines |

*Maps and world*

| ID | Finding |
|---|---|
| M9 | Duplicate teleport ids are masked by dict overwrite |
| M10 | Floor-support under LV teleports is WARN but a comment claims ERROR |
| M11 | Post-save verification prints counts but asserts nothing |
| M12 | LV monster eggs pass raw small qualities, not the packed form |
| M13 | The new Map 17 shield comment contradicts the fix it accompanies |
| M14 | `build_villages.py --write` appends villages to FIXED.DAT every run |

*Infrastructure and docs*

| ID | Finding |
|---|---|
| M15 | Retired `--stealth` is still advertised by `install_lv.sh` and `play.sh` |
| M16 | `install_lv.sh --clean` can restore EUSECODE but fail on FIXED.DAT |
| M17 | ScummVM built from unpinned master via depth-50 clone |
| M18 | No CI and no single runner for the real-assert quest tests |
| M19 | sint16 boundary and trampoline insertion have no targeted test |
| M20 | CLAUDE.md artifact stats are wrong (claims 48 maps) |
| M21 | HANDOFF.md contradicts TODO/PLAN on Map 8 doors and NPCs |
| M22 | The four merged game-data artifacts in `shared/build` are git-tracked |

### Low (§501)

Reported without skeptic verification, by design. Full table with file:line is
in the source doc; titles abridged here.

| ID | File | Finding |
|---|---|---|
| L1 | `u8c_parser.py:879` | Malformed numeric literal raises uncaught ValueError |
| L2 | `u8c_parser.py:767` | Non-associative comparison drops a trailing operator |
| L3 | `u8c_codegen.py:1043` | `break` inside while/for/foreach compiles to nothing |
| L4 | `u8c_codegen.py:1837` | Integer literal below −128 pushed as dword, misaligning the stack |
| L5 | `u8c_codegen.py:451` | Undefined-label check degrades later errors to bare KeyError |
| L6 | `lv_manifest.json:940` | `retail_shared` tags computed from stale source dirs |
| L7 | `u8c_symbols.py:50` | TYPE_SHAPES audit note cites a non-existent entry and wrong count |
| L8 | `u8_assembler.py:560` | Encoder silently substitutes raw hex on disagreement |
| L9 | `parse_typeflag.py:129` | `is_empty` ignores byte2/4/5 |
| L10 | `u8_usecode_disasm.py:693` | `0x5C` symbol decode never validated by round-trip |
| L11 | `test_uc_plntst.py:144` | "no Mark item" check is a tautology |
| L12 | `u8_map.py:234` | `save()` writes FIXED.DAT non-atomically |
| L13 | `build_map_09.py:103` | `teleport_dest` writes the source map into mapnum |
| L14 | `lv_wood_wall.py:32` | Shape 855 exported but never injected or TYPEFLAG-patched |
| L15 | `lv_wood_wall.py:448` | `inject_shape` only warns on a non-empty target slot |
| L16 | `cleanroom_test.sh:35` | Hardcoded absolute user path for game data |
| L17 | `install_lv.sh:140` | No pre-install hash check before overwriting game files |
| L18 | `agents/map-populator/MEMORY.md:47` | Agent MEMORY.md files describe a different codebase |
| L19 | `CLAUDE.md:31` | Omits the load-bearing `lv-patched/` dir; Ragnar limitation stale |
| L20 | `lv-patched/PLNTST.UNK:24` | Comment falsified by this changeset |
| L21 | `lv_manifest.py:172` | Stored `indent=1` vs `save()` `indent=2` reformats ~3220 lines |
| L22 | `lv-patched/EZREKAL.UNK:3322` | `givenElixir` guard revert re-opens the vial dupe |

---

## `M0.*` – `M3` — PLAN.md milestones

Defined in **`PLAN.md`**. See collision 3 above: bare `M1`–`M4` are ambiguous.

| ID | Milestone | PLAN §|
|---|---|---|
| M0 | Repair and guardrails | §1 |
| M1 | Playable spine | §2 |
| M2 | It looks and plays like 1994 intended | §3 |
| M3 | Release engineering | §4 |

### M0 sub-items · `PLAN.md:87-94`

| ID | Task |
|---|---|
| M0.1 | Fix the `this` pointer bug in `patch_mythran.py build_new_use()` |
| M0.2 | Ungate stock Mythran (implements DD-005 *engineering*) |
| M0.3 | Retire stealth mode (implements DD-006) |
| M0.4 | Build fails loudly — nonzero exit on compile failure, skipped Mythran patch, or missing quest-critical class |
| M0.5 | Kill silent codegen fallbacks |
| M0.6 | Pin ids in a manifest (`shared/build/lv_manifest.json`) |
| M0.7 | Harden the Mythran patch |
| M0.8 | (Optional) Rebuild `build_new_use` on the codegen Emitter |

`M1.x`–`M3.x` sub-numbering follows the PLAN section headings (e.g. M1's
subsections are PLAN §2.1–2.6, M3's are §4.1–4.4); those are cited as section
numbers rather than as `M1.1`-style codes.

**"The M1 shared-flag migration"** (TODO.md, `u8c_symbols.py`) is the
milestone, not finding M1. It is the savegame-breaking repin that
`agents/usecode-compiler/docs/manifest-design.md` §2 deferred to M1: a flag
our recompiled classes share with untouched retail bytecode moves from its
bit-1024-window pin onto the retail bit, and the old bit is kept in
`lv_manifest.json` as a `<name>_<oldbit>` entry with `"retired": true`. The
build refuses a live pin on a retired bit. Done so far: `araminaSchedule`
0x663 → 0x207 and `devonInRule` 0x4B6 → 0x58 (2026-10-08), then the other
eleven flags ARAMINA uses (2026-10-09: `araminaMet`/`Name`/`Job` → 0x203-
0x205, `somebodyTalking` → 0x0F, `hearTruthActive` → 0x27, `hydrosFree` →
0x36, `hasHeart` → 0x3C, `lothianDead` → 0xBF, `toldDagger` → 0xD6,
`mordeaDead` → 0x11A, `toldOfTreasure` → 0x147). Every other
`retail_shared` pin still sits in the LV window.

---

## `P1`–`P4` — packer-build addendum findings

Defined in **`docs/reviews/2026-07-19-adversarial-review.md:565`** ("Addendum:
packer-build re-run"). These did **not** go through the two-skeptic
verification the rest of the report had; treat as high-confidence
single-source.

| ID | Severity | Finding | Status |
|---|---|---|---|
| P1 | medium | `build_eusecode.py:666` — Gate 7's statement-drop ratchet skips `lv_patched_results` | RESOLVED 2026-07-25 |
| P2 | medium | `u8_flx_packer.py:146` — `write()` truncates the canonical EUSECODE.FLX before Gate 6 verifies it | RESOLVED 2026-07-25 (stage → verify → promote) |
| P3 | low | `test_patch_mythran.py` — byte-identity case pinned retired flag bits | RESOLVED 2026-07-25 (repinned as 'deployed' + manifest-drift guard) |
| P4 | low | `build_eusecode.py` — Mythran guards raised raw ValueError instead of the BUILD FAILED summary | RESOLVED (caught and routed through `failures`) |

**Not this namespace:** `P5`–`P10` appear in `test_uc_eggs.py`,
`test_uc_shades.py`, and `build_map_10.py` as local test-phase and waypoint
labels. They are unrelated to the review's `P` findings and are not indexed
here.

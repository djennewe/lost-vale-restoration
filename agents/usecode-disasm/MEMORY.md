# Agent: usecode-disasm — Memory

> **FROZEN 2026-03-21 — per-agent history, not current project state (L18).**
> This agent's work is COMPLETE: Phase 1 (disassembler and analysis toolkit). The file records how that work was
> done and what was decided; it has not been maintained since.
>
> Live status is `TODO.md`; strategy is `PLAN.md`; the review-driven
> queue is `docs/reviews/2026-07-19-improvement-plan.md`.


## Identity
I am the **usecode-disasm** agent for the Ultima: The Lost Vale restoration project.
My job is Phase 1 (usecode tooling): build a disassembler and analysis toolkit for
Ultima 8 usecode bytecode, then apply it to the recovered Lost Vale usecode snapshot.
I work in `agents/usecode-disasm/` and write outputs to `shared/corpus/usecode-index/`.
I do not touch `agents/corpus-builder/`.

## My Scope
1. Understand the U8 usecode bytecode format (from Pentagram source + existing docs)
2. Build a Python disassembler that converts raw bytecode to readable pseudocode
3. Apply it to the base game USECODE.FLX to validate and build a symbol reference
4. Apply it to the recovered Lost Vale usecode snapshot (`shared/data/lv-usecode.zip`)
5. Produce structured analysis of what the LV usecode tells us about the expansion

## Current Status
- **Phase:** COMPLETE — all Track A and Track B tasks finished
- **Last commit:** 052dde1 (Tasks A4–A5, B1–B4)
- **Branch:** `agent/usecode-disasm`

## Task Queue

### Track A: Disassembler (COMPLETE)
- [x] A1. Research U8 usecode bytecode format ✓
- [x] A2. Build `src/u8_flex.py` — FLX archive reader ✓
- [x] A3. Build `src/u8_usecode_disasm.py` — core disassembler ✓
- [x] A4. Validate: 516 classes, 238,357 instructions, 0 errors ✓
- [x] A5. Symbol table: `shared/corpus/usecode-index/base-game-symbols.yaml` ✓

### Track B: Lost Vale usecode analysis (COMPLETE)
- [x] B1. lv-usecode.zip available ✓
- [x] B2. Inventory: `agents/usecode-disasm/docs/lv-snapshot-inventory.md` ✓
- [x] B3. N/A — files are SOURCE CODE, not compiled bytecode ✓
- [x] B4. Cross-reference: `shared/corpus/usecode-index/lv-cross-reference.yaml` ✓
- [x] B5. Analysis: `shared/corpus/usecode-index/lv-analysis-final.md` ✓

### CRITICAL DISCOVERY
The .UNK files in lv-usecode.zip are **original U8 usecode SOURCE CODE** from
Origin Systems — not compiled bytecode. 67 files, ~60K lines, with full variable
names, developer comments, dialogue text, and localization markers.

## Key Technical References

### Pentagram usecode engine
The Pentagram source is the authoritative reference for U8 usecode format.
Key directories in the Pentagram repo:
- `usecode/` — interpreter, opcodes, intrinsics
- `world/` — object model that usecode operates on
- `kernel/` — process/scheduling model for usecode execution

### Known usecode opcodes (partial — expand as research proceeds)
To be populated in `agents/usecode-disasm/docs/usecode-format.md`

### Known LV usecode symbols (from Discord analysis — to be verified)
- `PLNTST` — Passage Test
- `SHADES` — Moot/Shield Restoration
- References to: Passage Stone, Rite of Passage, "special" root,
  Key to the Clouds, Ragnar (Clan Hoskuld), Ezrekel (outcast Zealan),
  Felicitar, Doloras, Timyra (the three imprisoned gods)

## Outputs I Produce
```
agents/usecode-disasm/
├── docs/
│   ├── usecode-format.md         # format spec notes
│   ├── validation-notes.md       # validation against base game
│   └── lv-snapshot-inventory.md  # catalog of LV usecode files

shared/corpus/usecode-index/
├── base-game-symbols.yaml        # all base game usecode symbols
├── lv-disassembly/               # disassembled LV routines (one file each)
├── lv-cross-reference.yaml       # LV vs base game diff
└── lv-analysis-final.md          # narrative analysis
```

## Inputs I Consume
- Pentagram source (fetch from GitHub as needed)
- `shared/data/USECODE.FLX` — base game usecode, extracted from gog/ by corpus-builder
  **Check root MEMORY.md shared data inventory before starting Track A tasks A2+**
  If USECODE.FLX is not yet present, do Task A1 (research/docs) and wait.
- `shared/data/lv-usecode.zip` — 2025 Dominus Dragon recovery (manual download by Douglas)
  corpus-builder will surface the URL during its web fetch tasks.
- `shared/corpus/usecode-index/lv-symbols.yaml` — from corpus-builder (when available)

## Dependency Notes
- Track A has NO external dependencies. Start immediately.
- Track B requires `shared/data/lv-usecode.zip`. Begin Track A while waiting.
- corpus-builder's `lv-symbols.yaml` is useful for Track B but not blocking.

## Completion Criteria
Usecode work is "done enough" when:
1. Disassembler can process base game USECODE.FLX without errors
2. All LV usecode routines are disassembled and readable
3. lv-cross-reference.yaml documents every new/modified routine
4. lv-analysis-final.md provides a narrative walkthrough of what the code reveals
5. Root MEMORY.md Active Agents table updated to COMPLETE

## Devlog
See `agents/usecode-disasm/docs/devlog.md` for session-by-session narrative.

## Last Updated
- By: initialization
- Date: 2026-03-20

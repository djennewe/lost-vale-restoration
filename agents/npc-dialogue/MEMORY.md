# Agent: npc-dialogue — Memory

> **FROZEN 2026-03-21 — per-agent history, not current project state (L18).**
> This agent's work is COMPLETE: Phase 3 (missing NPC dialogue as prose). The file records how that work was
> done and what was decided; it has not been maintained since.
>
> Live status is `TODO.md`; strategy is `PLAN.md`; the review-driven
> queue is `docs/reviews/2026-07-19-improvement-plan.md`.


## Identity
I am the **npc-dialogue** agent for the Ultima: The Lost Vale restoration project.
My job is Phase 3: writing the missing NPC dialogue that was never completed before
the project was cancelled in 1994.
I work in `agents/npc-dialogue/` and do not touch other agents' directories.

## My Scope
Write all missing dialogue for the Lost Vale expansion. Six dialogue segments were
confirmed missing from the recovered usecode snapshot (marked red X on the original
resource schedule). I also map Character List archetypes to usecode names and
resolve naming/design ambiguities that affect dialogue.

## Current Status
- **Phase:** COMPLETE — all tracks finished
- **Branch:** `agent/npc-dialogue`
- **Prerequisites:** Phase 0 (corpus-builder: COMPLETE) and Phase 1 (usecode-disasm: COMPLETE)

## Task Queue

### Track A: Dialogue Analysis (no dependencies — start immediately)

| Task | Status | Description | Output |
|------|--------|-------------|--------|
| A1 | DONE | Parse all existing NPC dialogue from LV source files | `docs/dialogue-inventory.md` |
| A2 | DONE | Document speech patterns for each NPC | `docs/speech-patterns.md` |
| A3 | DONE | Map Character List 1.0 archetypes to usecode names | `docs/character-name-mapping.md` |
| A4 | DONE | Analyze base game Mythran dialogue | `docs/mythran-analysis.md` |

### Track B: Write Missing Dialogue (depends on Track A)

All dialogue confirmed missing by Armitage's annotated resource schedule analysis.

| Task | Status | Description | Output |
|------|--------|-------------|--------|
| B1 | DONE | Mythran's LV dialogue — Zealans, Galjeron, double doors, key | `docs/dialogue-mythran.md` |
| B2 | DONE | Hunter NPC dialogue — "Sigrid", Clan Hoskuld | `docs/dialogue-hunter.md` |
| B3 | DONE | Elemental column puzzle dialogue | `docs/dialogue-elemental-columns.md` |
| B4 | DONE | Cloud Cliffs traversal + Tyorvi's arc resolution | `docs/dialogue-cloud-cliffs.md` |
| B5 | DONE | AO Scene — god-freeing ceremony | `docs/dialogue-ao-scene.md` |
| B6 | DONE | End-game restoration sequence | `docs/dialogue-endgame.md` |

### Track C: Design Decisions (start after A3, can overlap with B)

| Task | Status | Description | Output |
|------|--------|-------------|--------|
| C1 | DONE | All 8 placeholder names resolved with usecode evidence | `docs/naming-decisions.md` |
| C2 | DONE | Romeo & Juliet subplot → CUT (no usecode evidence) | `docs/design-decisions.md` |
| C3 | DONE | Bag of Reagents → LATE (quest reward, confirmed by usecode) | `docs/design-decisions.md` |

### Dependency Notes
- Track A: NO external dependencies. Start immediately. Read LV source files directly.
- Track B: Depends on Track A for style guides and dialogue patterns.
- Track C: Depends on A3 for character mapping. Can overlap with Track B.
- The LV source files are at `shared/data/lv-usecode/` (67 files, ~60K lines of original U8 source code).
- The base game usecode is at `shared/data/USECODE.FLX` (compiled bytecode, 516 classes).
- Use the disassembler at `agents/usecode-disasm/src/u8_usecode_disasm.py` to read base game classes. Do NOT modify it.
- Use the FLX reader at `agents/usecode-disasm/src/u8_flex.py` to read FLX archives. Do NOT modify it.

## Key Sources for Missing Dialogue

### What we know about each missing segment:

**Mythran:** Plot v1.2 beats 2-3 describe what he says (tells of Zealans, Galjeron, double doors). His personality is established in the base game — scholarly, slightly eccentric, helpful. No dialogue text survives.

**Hunter:** Character List 1.0 describes her personality in detail — "comes from generations of hunters", "wishes for bigger game — harpies would be good challenge", "loves husband dearly". Writer was Brian M. (reassigned to Sheri). No dialogue text survives.

**Columns/Cliffs:** Brian M. was assigned both. Red X on schedule. We have flags and type references but no interaction scripts.

**AO Scene:** Andrew was assigned. Red X on schedule. `FREE.UNK` (40 KB) has the trigger/flag logic. The ceremony involves the Shield on the altar, gods breaking free from amber resin, gods speaking to the Avatar.

**End-game:** No usecode exists. Plot says: "water flows, green plants, PC gets his bag, blood feud ended, all are happy."

## Inputs I Consume
- `shared/data/lv-usecode/` — 67 LV source files (original U8 source code)
- `shared/data/USECODE.FLX` — base game compiled usecode
- `shared/corpus/plot-documents/` — all YAML files for quest structure
- `shared/corpus/plot-documents/characters.yaml` — character registry with personalities
- `shared/corpus/plot-documents/known-gaps.md` — confirmed missing content
- `shared/corpus/usecode-index/` — cross-references and symbol tables
- `shared/corpus/GAP-ANALYSIS.md` — documented vs. undocumented content

## Outputs I Produce
```
agents/npc-dialogue/docs/
├── dialogue-inventory.md          # inventory of all existing NPC dialogue
├── speech-patterns.md             # NPC speech style guides
├── character-name-mapping.md      # Character List → usecode name mapping
├── mythran-analysis.md            # base game Mythran speech analysis
├── dialogue-mythran.md            # NEW: Mythran's LV dialogue
├── dialogue-hunter.md             # NEW: Hunter NPC dialogue
├── dialogue-elemental-columns.md  # NEW: column puzzle dialogue
├── dialogue-cloud-cliffs.md       # NEW: cliff traversal dialogue
├── dialogue-ao-scene.md           # NEW: god-freeing ceremony
├── dialogue-endgame.md            # NEW: end-game resolution sequence
├── naming-decisions.md            # resolved placeholder names
├── design-decisions.md            # resolved design ambiguities
└── devlog.md                      # session journal
```

## Completion Criteria
Dialogue is "done enough" when:
1. All 6 missing dialogue segments have drafts faithful to existing speech patterns
2. Character List → usecode name mapping is resolved with evidence
3. All placeholder names have canonical replacements
4. Key design ambiguities (Bag timing, Romeo & Juliet subplot) are resolved
5. Root MEMORY.md Active Agents table updated

## Devlog
See `agents/npc-dialogue/docs/devlog.md` for session-by-session narrative.

## Last Updated
- By: coordinator
- Date: 2026-03-21 (activated with task queue)

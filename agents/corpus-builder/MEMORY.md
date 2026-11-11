# Agent: corpus-builder — Memory

> **FROZEN 2026-03-20 — per-agent history, not current project state (L18).**
> This agent's work is COMPLETE: Phase 0 (research and corpus assembly). The file records how that work was
> done and what was decided; it has not been maintained since.
>
> Live status is `TODO.md`; strategy is `PLAN.md`; the review-driven
> queue is `docs/reviews/2026-07-19-improvement-plan.md`.


## Identity
I am the **corpus-builder** agent for the Ultima: The Lost Vale restoration project.
My job is Phase 0: Research & Corpus Assembly.
I work in `agents/corpus-builder/` and write outputs to `shared/corpus/`.
I do not touch `agents/usecode-disasm/`.

## My Scope
Build a clean, structured, machine-readable corpus from all publicly available
Lost Vale source material. This corpus will be consumed by other agents (especially
usecode-disasm) and by future content-creation phases.

## Current Status
- **Phase:** COMPLETE — all immediate tasks done
- **Last commit:** Step 3 complete (structured corpus documents)
- **Branch:** `agent/corpus-builder`

## Task Queue

### Immediate (do these first, in order)

#### Step 1: Unpack and sort everything in gog/
- [x] 1a. Unzip all GOG extras — DONE (13 LV design PDFs + 5 base game PDFs)
- [x] 1b. Extract DOS game data — DONE (EUSECODE.FLX → USECODE.FLX, full install copied)
      Also found & extracted Sheri-U8-LV.zip from discord/ → shared/data/lv-usecode/
- [x] 1c. Inventory — DONE → `shared/data/INVENTORY.md`

#### Step 2: Web sources
- [x] 2. Usecode analysis article — DONE → `shared/corpus/usecode-index/lv-usecode-analysis.md`
      Note: ultimacodex.com article JS-heavy, used web search + Discord screenshots instead.
      Discord screenshots provided Armitage's full analysis (clan names, symbol meanings, annotated schedule).
      lv-usecode.zip already present locally (from discord/Sheri-U8-LV.zip).
- [x] 3. Codex wiki summary — DONE → `shared/corpus/plot-documents/codex-wiki-summary.md`
- [x] 4. Dino's Guide omissions — DONE → `shared/corpus/plot-documents/dinos-guide-omissions.md`
      Also fetched dedicated Lost Vale page (u8tlv.php).
- [x] 5. Sheri Graner Ray interviews — DONE → `shared/corpus/interviews/sheri-graner-ray.md`
      Sources: personal blog (2014), GameBanshee interview (2013).

#### Step 3: Structured corpus documents
- [x] 6. story-beats.yaml — DONE. 21 beats (18 main + 3 proposed) with full source citations.
      Read Plot v1.1, v1.2, Walk Through, Synopsis with Notes, Pitch Doc, Elean Speak, Art List.
- [x] 7. characters.yaml — DONE. 25+ characters with factions, roles, writer assignments.
      Cross-referenced Character List 1.0, usecode symbols, Discord analysis.
- [x] 8. locations.yaml — DONE. 15 locations with connections and art notes.
- [x] 9. items.yaml — DONE. 30+ items including quest items, rewards, obstacles, Easter eggs.
- [x] 10. lv-symbols.yaml — DONE. 28 LV-related symbols + 13 base game symbols + 6 confirmed missing.
       This is the file usecode-disasm is waiting on.
- [x] 11. GAP-ANALYSIS.md — DONE. Documented vs undocumented vs conflicts/ambiguities.

### Upcoming (after immediate tasks)
- [ ] Screenshot inventory (when screenshots are added to shared/data/)
- [ ] Box art description document
- [ ] Cross-reference: which story beats appear in usecode vs. only in plot docs

## Outputs I Produce
All outputs go to `shared/corpus/`. Do not write anywhere else except my own
`agents/corpus-builder/` directories.

```
shared/corpus/
├── plot-documents/
│   ├── codex-wiki-summary.md
│   ├── dinos-guide-omissions.md
│   ├── story-beats.yaml
│   ├── characters.yaml
│   ├── locations.yaml
│   └── items.yaml
├── interviews/
│   └── sheri-graner-ray.md
├── usecode-index/
│   ├── lv-usecode-analysis.md
│   └── lv-symbols.yaml
└── GAP-ANALYSIS.md
```

## Inputs I Consume
- Public web sources (fetch directly)
- `shared/data/lv-usecode.zip` when available (notify in MEMORY.md when processed)
- `shared/data/plot-docs/` image files when available

## Dependency Notes
- usecode-disasm is waiting on `shared/corpus/usecode-index/lv-symbols.yaml`
  Prioritize task 9 after tasks 1-4 are done.

## Completion Criteria
Corpus is "done enough" when:
1. All known public text sources are saved and structured
2. story-beats.yaml, characters.yaml, locations.yaml, items.yaml all have entries
3. lv-symbols.yaml lists all known usecode symbols from the recovered snapshot
4. GAP-ANALYSIS.md exists and is populated
5. Root MEMORY.md Active Agents table updated to COMPLETE

## Devlog
See `agents/corpus-builder/docs/devlog.md` for session-by-session narrative.

## Last Updated
- By: corpus-builder
- Date: 2026-03-20 (session 1, all immediate tasks complete)

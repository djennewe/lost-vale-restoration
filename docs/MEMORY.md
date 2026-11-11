# Ultima: The Lost Vale — Global Project Memory (ARCHIVED)

> **ARCHIVED SNAPSHOT — do not treat as current state (H10).**
> Frozen at 2026-03-21, covering Phases 0-3 (4 agents, 32 LV classes, Phase 4c
> pending). It was the root `MEMORY.md` dashboard until commit 5cec802
> (2026-03-28) moved it here, after which it stopped being maintained while the
> project ran on for four more months.
>
> Everything below describes March 2026. Where it conflicts with the live docs,
> the live docs win:
>
> | For | Read |
> |---|---|
> | Current status / what's next | `TODO.md` |
> | Strategy and milestones | `PLAN.md` |
> | Review-driven work queue | `docs/reviews/2026-07-19-improvement-plan.md` |
> | Repo conventions and commands | `CLAUDE.md` |
> | Session pickup | `HANDOFF.md` |
>
> Kept because its Phase 0-3 record — the corpus survey, the format
> reverse-engineering, the early design decisions — is not written down
> anywhere else.

## Project Goal
Fan restoration of *Ultima 8: The Lost Vale* — the cancelled 1994 expansion to Ultima 8: Pagan.
Target runtime: ScummVM (which absorbed the Pentagram U8 engine in April 2020).
Legal basis: Fan restoration of content the owner has legal copies of. Similar standing to Exult/Pentagram.

## Repository Structure
```
ultima-lost-vale/
├── MEMORY.md                        # ← this file: global state
├── README.md
├── PROMPTS.md                       # Claude Code agent initialization prompts
├── gog/                             # READ-ONLY: raw GOG downloads (place zips here)
│   ├── ultima__8_gold_edition_enUS_gog_3x_34378.pkg
│   ├── ultima_8_lost_vale_design_documents.zip
│   ├── ultima_8_cluebook.zip
│   ├── ultima_8_manual.zip
│   ├── ultima_8_chronicle.zip
│   ├── ultima_8_map.zip
│   └── ultima_8_reference_card.zip
├── agents/
│   ├── corpus-builder/
│   │   ├── MEMORY.md                # corpus-builder agent state
│   │   ├── docs/devlog.md           # human-readable journal
│   │   └── src/                     # corpus-builder code
│   ├── usecode-disasm/
│   │   ├── MEMORY.md                # usecode-disasm agent state
│   │   ├── docs/devlog.md           # human-readable journal
│   │   └── src/                     # usecode-disasm code
│   ├── map-builder/
│   │   ├── MEMORY.md                # map-builder agent state (Phase 2)
│   │   └── docs/                    # map design docs (when active)
│   └── npc-dialogue/
│       ├── MEMORY.md                # npc-dialogue agent state (Phase 3)
│       └── docs/                    # dialogue drafts and analysis
├── shared/
│   ├── docs/                        # shared reference documents
│   ├── data/                        # unpacked working files (populated by agents)
│   │   ├── u8-install/              # extracted DOS game data from .pkg
│   │   ├── USECODE.FLX              # working copy for agents
│   │   ├── lv-usecode.zip           # 2025 Dominus Dragon recovery (manual download)
│   │   └── extracted/               # unzipped GOG extras
│   └── corpus/                      # structured output from corpus-builder
│       ├── plot-documents/          # parsed plot docs in structured form
│       ├── interviews/              # parsed interview content
│       ├── screenshots/             # screenshot inventory
│       └── usecode-index/           # index of recovered LV usecode symbols
└── README.md
```

## Active Agents

### corpus-builder
- **Status:** COMPLETE — Phase 0 corpus ready
- **Branch:** `agent/corpus-builder`
- **Current task:** All immediate tasks done (Steps 1-3)
- **Last commit:** Step 3 — structured corpus documents
- **Blocker:** None
- **Outputs ready:**
  - `shared/corpus/plot-documents/story-beats.yaml` (21 beats + Discord 21-step questline)
  - `shared/corpus/plot-documents/characters.yaml` (25+ characters, enriched)
  - `shared/corpus/plot-documents/locations.yaml` (17 locations incl. The Lake, Ancient Temple)
  - `shared/corpus/plot-documents/items.yaml` (32+ items incl. Key to the Clouds)
  - `shared/corpus/plot-documents/production-schedule.yaml` (team, assignments, red-X gaps)
  - `shared/corpus/plot-documents/known-gaps.md` (confirmed missing usecode, implications)
  - `shared/corpus/usecode-index/lv-symbols.yaml` (28 LV symbols + missing list)
  - `shared/corpus/usecode-index/lv-usecode-analysis.md`
  - `shared/corpus/plot-documents/codex-wiki-summary.md`
  - `shared/corpus/plot-documents/dinos-guide-omissions.md`
  - `shared/corpus/interviews/sheri-graner-ray.md`
  - `shared/corpus/GAP-ANALYSIS.md`
  - `shared/data/INVENTORY.md`
- **Note:** Corpus seeded by coordinator (6dda3ef) with Discord primary source data

### usecode-disasm
- **Status:** COMPLETE — All Track A and Track B tasks finished
- **Branch:** `agent/usecode-disasm`
- **Current task:** All tasks complete
- **Last commit:** 052dde1 (Tasks A4–A5, B1–B4)
- **Blocker:** None
- **Key discovery:** LV usecode snapshot contains ORIGINAL SOURCE CODE (not bytecode)
- **Outputs ready:**
  - `agents/usecode-disasm/docs/usecode-format.md` (complete U8 bytecode format spec)
  - `agents/usecode-disasm/docs/validation-notes.md` (0 errors on 238K instructions)
  - `agents/usecode-disasm/docs/lv-snapshot-inventory.md` (67 source files, 60K lines)
  - `agents/usecode-disasm/src/u8_flex.py` (FLX archive reader)
  - `agents/usecode-disasm/src/u8_usecode_disasm.py` (validated disassembler)
  - `shared/corpus/usecode-index/base-game-symbols.yaml` (516 classes, 182 intrinsics)
  - `shared/corpus/usecode-index/lv-cross-reference.yaml` (23 new + 10 modified classes)
  - `shared/corpus/usecode-index/lv-analysis-final.md` (comprehensive LV analysis)

### map-builder (Phase 2)
- **Status:** COMPLETE — All tracks (A, B, C) finished
- **Branch:** `agent/map-builder`
- **Current task:** All tasks complete
- **Blocker:** None
- **Outputs ready:**
  - `agents/map-builder/docs/map-format.md` (U8 map format specification)
  - `agents/map-builder/docs/base-game-maps.md` (42-map catalog + connectivity graph)
  - `agents/map-builder/docs/shape-catalog.md` (2,048 shapes + 2,129 globs documented)
  - `agents/map-builder/docs/asset-reuse-plan.md` (Art List v2.5 cross-reference)
  - `agents/map-builder/docs/map-design-overview.md` (slot assignments, 14 transitions)
  - `agents/map-builder/docs/map-08-plateau-entry.md` (double doors modification)
  - `agents/map-builder/docs/map-09-galjeron-chamber.md` (Map 9 design)
  - `agents/map-builder/docs/map-10-lost-vale.md` (Map 10 overworld, 10 sub-zones)
  - `agents/map-builder/docs/map-11-elemental-dungeon.md` (Map 11, 4 sections)
  - `agents/map-builder/docs/map-13-17-cloud-areas.md` (Maps 13+17 cloud areas)
  - `agents/map-builder/docs/map-18-ancient-temple.md` (Map 18, god-freeing)
  - `agents/map-builder/src/u8_map.py` (FIXED.DAT reader/writer tool)
  - `shared/maps/FIXED_TEST.DAT` (test map with Map 10 prototype)
- **Memory:** `agents/map-builder/MEMORY.md`

### npc-dialogue (Phase 3)
- **Status:** COMPLETE — all tracks finished
- **Branch:** `agent/npc-dialogue`
- **Last commit:** Track B+C complete (all 6 dialogue segments, naming, design decisions)
- **Blocker:** None
- **Completed:**
  1. Mythran — LV introduction dialogue (`docs/dialogue-mythran.md`)
  2. Hunter — "Sigrid", Clan Hoskuld (`docs/dialogue-hunter.md`)
  3. Elemental columns — pillar puzzle dialogue (`docs/dialogue-elemental-columns.md`)
  4. Cloud Cliffs — climbing traversal + Tyorvi arc (`docs/dialogue-cloud-cliffs.md`)
  5. AO Scene — god-freeing ceremony (`docs/dialogue-ao-scene.md`)
  6. End-game — restoration sequence (`docs/dialogue-endgame.md`)
- **Also completed:** Character name mapping, all 8 placeholder names resolved,
  Romeo & Juliet subplot → CUT, Bag of Reagents → LATE (quest reward)
- **Outputs ready:**
  - `agents/npc-dialogue/docs/dialogue-inventory.md` (complete bark/ask/flag extraction)
  - `agents/npc-dialogue/docs/speech-patterns.md` (Elean Speak rules + per-NPC guides)
  - `agents/npc-dialogue/docs/character-name-mapping.md` (6 confirmed, 3 missing, 1 cut)
  - `agents/npc-dialogue/docs/mythran-analysis.md` (base game Mythran: 499 strings)
  - `agents/npc-dialogue/docs/dialogue-mythran.md` (NEW: ~1100 words)
  - `agents/npc-dialogue/docs/dialogue-hunter.md` (NEW: "Sigrid", Clan Hoskuld)
  - `agents/npc-dialogue/docs/dialogue-elemental-columns.md` (NEW: 4 pillar sequences)
  - `agents/npc-dialogue/docs/dialogue-cloud-cliffs.md` (NEW: climb + Tyorvi)
  - `agents/npc-dialogue/docs/dialogue-ao-scene.md` (NEW: gods speak)
  - `agents/npc-dialogue/docs/dialogue-endgame.md` (NEW: all NPC reactions)
  - `agents/npc-dialogue/docs/naming-decisions.md` (8 placeholders resolved)
  - `agents/npc-dialogue/docs/design-decisions.md` (5 design decisions)
- **Memory:** `agents/npc-dialogue/MEMORY.md`

### usecode-compiler (Phase 4a)
- **Status:** COMPLETE — assembler + compiler + FLX packer
- **Outputs ready:**
  - `agents/usecode-compiler/src/u8_assembler.py` (assembler, 516/516 round-trip)
  - `agents/usecode-compiler/src/u8_flx_packer.py` (FLX archive writer)
  - `agents/usecode-compiler/src/u8c_*.py` (lexer, parser, AST, codegen, symbols, driver)
  - `agents/usecode-compiler/src/lv-new/*.UNK` (6 new dialogue source files)
  - `agents/usecode-compiler/src/build_eusecode.py` (EUSECODE.FLX builder)
  - `shared/build/EUSECODE.FLX` (1.36 MB, 516 base + 32 new LV classes)
- **Compilation stats:** 42/49 LV files compile (143 KB bytecode). RAGNAR.UNK (MVP gate) passes.
- **Known limitations:** 5 largest files hit sint16 jump overflow; 2 files have source-level issues

### map-populator (Phase 4b)
- **Status:** COMPLETE — all maps built + FIXED.DAT assembled
- **Outputs ready:**
  - `agents/map-populator/src/build_*.py` (7 map builders + orchestrator)
  - `shared/build/FIXED.DAT` (1.5 MB, 48 maps, 92,954 items)
- **Maps:** 8 (mod), 9, 10, 11, 13, 17, 18 — all 14 teleport pairs verified

## Source Data

### `gog/` — Raw GOG downloads (READ-ONLY, do not modify)
| File | Description | Status |
|------|-------------|--------|
| `ultima__8_gold_edition_enUS_gog_3x_34378.pkg` | GOG Mac installer (69.9 MB) | PRESENT |
| `ultima_8_lost_vale_design_documents.zip` | GOG-bundled LV design docs (16.6 MB) | PRESENT |
| `ultima_8_cluebook.zip` | Official cluebook (12.9 MB) | PRESENT |
| `ultima_8_manual.zip` | Game manual (192 KB) | PRESENT |
| `ultima_8_chronicle.zip` | Chronicle of Pagan (12 MB) | PRESENT |
| `ultima_8_map.zip` | Pagan world map (745 KB) | PRESENT |
| `ultima_8_reference_card.zip` | Reference card (190 KB) | PRESENT |

### `shared/data/` — Unpacked working files (populated by agents)
| File/Dir | Description | Populated by | Status |
|----------|-------------|--------------|--------|
| `u8-install/` | Extracted DOS game data from .pkg | corpus-builder | PRESENT |
| `USECODE.FLX` | Base game usecode (EUSECODE.FLX, 1.3 MB) | corpus-builder | PRESENT |
| `lv-usecode.zip` | 2025 Dominus Dragon usecode recovery | corpus-builder (from discord/) | PRESENT |
| `lv-usecode/` | Extracted LV usecode (71 files, 3 dirs) | corpus-builder | PRESENT |
| `extracted/` | Unzipped GOG extras | corpus-builder | PRESENT |

**Note on lv-usecode.zip:** This is the February 2025 usecode snapshot recovered from
Sheri Graner Ray's diskette, published by Dominus Dragon on the Ultima Dragons Discord
and hosted at ultimacodex.com. It is SEPARATE from the GOG design documents.
corpus-builder will surface the download URL; Douglas may need to download it manually.

## Key Sources
- Usecode analysis: https://ultimacodex.com/2025/02/a-look-at-the-usecode-for-ultima-8-the-lost-vale/
- Plot documents: https://gallery.ultimacodex.com/the-lost-vale-plot-documents/
- Ultima Codex wiki: https://wiki.ultimacodex.com/wiki/Ultima_VIII:_The_Lost_Vale
- Dino's Guide omissions: https://gigi.nullneuron.net/ultima/u8/omission.php
- Pentagram engine (now in ScummVM): https://github.com/pentagram-u8/pentagram
- DominusExult fork: https://github.com/DominusExult/pentagram

## Known Story Beats (from recovered sources)
1. Receive message from Lord British
2. Talk to Mythran — learn of Lost Vale, how to open double doors
3. Find key; enter Elemental Dungeon
4. Collect 4 tokens, open way to Lost Vale
5. Meet the Zealans — must pass Rite of Passage to be recognized
6. Neither clan has Passage Stone; each blames the other
7. Ragnar (Clan Hoskuld) tells of young woman killed at the lake; gives bag
8. Find Passage Stone at the lake (water zombies); take Passage Test; get poisoned
9. Thordis and Atli give Zealan mark; seek Ezrekal
10. Ezrekal tells history; gods can cure poison but need to reach Cloud City
11. Tjorvi has Key to the Clouds; won't give it up (nightmares)
12. Get special root for Ezrekal; she brews nightmare potion; cure Tjorvi; get key
13. Climb Cloud Cliffs to Cloud City; find broken Shield halves, no gods
14. Return to Ezrekal; she calls meeting at Sacred Circle
15. Shield restoration ceremony; shades reveal truth; clans reconciled
16. Gods are at Ancient Temple; Hrodny has Tiny Tar but lost chest key
17. Get potions; enter Temple; place Shield on altar; talk to gods
18. Receive Bag of Reagents. END.

**Full 21-step Discord questline**: see `shared/corpus/plot-documents/story-beats.yaml`

## Phase Status

| Phase | Agent | Status | Key Output |
|-------|-------|--------|------------|
| 0: Research & Corpus | corpus-builder | COMPLETE | `shared/corpus/` — all YAMLs, analysis, gaps |
| 1: Usecode Tooling | usecode-disasm | COMPLETE | Disassembler, 67 source files analyzed, 631 flags |
| — Corpus Seed | coordinator | COMPLETE | Discord primary source enrichment (6dda3ef) |
| 2: Map Design | map-builder | COMPLETE | 7 map designs, format spec, prototype tools, test map |
| 3: NPC Dialogue | npc-dialogue | COMPLETE | 6 dialogue segments, naming, design decisions — all written |
| 4a: Usecode Compiler | usecode-compiler | COMPLETE | Assembler (516/516 round-trip), compiler (42/49 files), 6 new dialogue .UNK, EUSECODE.FLX |
| 4b: Map Population | map-populator | COMPLETE | 6 new maps + Map 8 mod, 92,954 items, 14 teleport pairs, FIXED.DAT |
| 4c: Integration | coordinator | ACTIVE | Build artifacts in shared/build/, verification pending |

## Coordination Protocol
- Each agent updates its own `MEMORY.md` after every commit
- Each agent updates the **Active Agents** table in this root `MEMORY.md` after every commit
- Neither agent modifies the other agent's `MEMORY.md` or `src/`
- Shared outputs go to `shared/corpus/` or `shared/data/` only
- Conflicts on this root file: last-writer wins, content is additive

## Design Decisions (Coordinator)

### DD-001: Tjorvi = Tyorvi (same character)
- **Decision:** TJORVI.UNK (14 KB, 1994-06-20) and TYORVI.UNK (71 KB, 1994-09-13)
  are the same character at different development stages.
- **Evidence:** Same Norse name with spelling variation; coordinator prompt treats
  them as one; file size progression consistent with development.
- **Implication:** Use "Tyorvi" as canonical name (final version). Key to the Clouds
  subplot and nightmares are this character's quest arc.

### DD-002: Ancient Temple vs. Shrine of the Ancient Ones
- **Decision:** Treat as the same location (or closely connected locations in the
  same map area). The design docs say "Shrine of the Wheaties" / "Shrine of the
  Ancient Ones" and the Discord analysis calls it "Ancient Temple."
- **Evidence:** Both refer to where the gods are imprisoned. Usecode flags
  `templeOpen` and `ezToTemple` reference "temple" consistently.
- **Implication:** Map-builder should design this as one map area with the
  "Temple" as the outer structure and the "Shrine" as the inner sanctum where
  the gods are imprisoned.

### DD-003: Plot v1.2 wins over Synopsis for trust-gaining mechanism
- **Decision:** Use the Passage Test (PLNTST) mechanism from Plot v1.2, not the
  two-quest mechanism from the Synopsis.
- **Evidence:** PLNTST.UNK exists in the usecode snapshot. Usecode flags
  `completedTest`, `zealanMark`, `avatarPoisoned` confirm this flow.
- **Implication:** The Synopsis's alternate quest structure (kill monster for Group 1,
  recover stolen item for Group 2) was not implemented.

## Last Updated
- By: coordinator
- Date: 2026-03-21

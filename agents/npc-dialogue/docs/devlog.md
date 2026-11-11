# NPC Dialogue Agent — Devlog

## Session 1 — 2026-03-21 — Track A Complete

### What I did
Completed all four Track A tasks (dialogue analysis) in a single session:

**A1: Dialogue Inventory** (`dialogue-inventory.md`)
- Read all 67 LV source files (~60K lines of original U8 source code)
- Extracted every bark() string, ask() option list, and conversation flag
- Organized by NPC (8 Zealan NPCs), Items (6), Puzzles (6 mechanisms), and
  U8 Modified NPCs (12)
- Documented all 631+ global flags and version differences between LOST VALE/
  and UNK files/ directories

**A2: Speech Patterns** (`speech-patterns.md`)
- Documented "Elean Speak" — the inverted syntax used by all Zealan NPCs
- Codified 6 core inversion rules with examples
- Individual style guides for all 8 Zealan NPCs, Lord British, and Mythran
- Tyorvi's drunk speech rules (consonant shifts, -hic- placement, -sob-)
- Shade speech patterns (grave, dignified, truth-telling register)
- Writing guidelines for missing dialogue

**A3: Character Name Mapping** (`character-name-mapping.md`)
- Mapped all Character List 1.0 archetypes to usecode NPC names
- 6 CONFIRMED mappings (Thordis, Tyorvi, Atli, Hrodny, Ingyald, ZealanChild1)
- 3 MISSING characters (Female Hunter, Male Farmer, Female Farmer)
- 1 CUT character (Female Child of Elder — struck through in Character List)
- 1 additional NPC not in Character List (Ragnar — added during development)
- Spatial analysis of NPC schedule coordinates confirms clan territories

**A4: Mythran Analysis** (`mythran-analysis.md`)
- Analyzed all 499 dialogue strings from base game USECODE.FLX class 0x0421
- Documented his speech pattern: formal modern English, "Ah" opener, "my friend"
  address, dashes for emphasis, long complex sentences
- Identified his 3-stage quest-giving pattern: Acknowledge → Theorize → Direct
- Personality profile: scholarly, eclectic, generous-but-pragmatic, dry humor
- Key for LV: he contextualizes before directing, admits uncertainty, frames
  quests as logical deductions

### Key Discoveries
1. **All Zealan NPCs use "Elean Speak"** — a consistent inverted syntax pattern
   (~70-80% of declaratives). This is the dominant style guide for all missing
   dialogue.
2. **Tyorvi's drunk speech** has specific phonetic rules (s→sh, -hic- insertion)
   that are mechanically consistent across all his dialogue.
3. **The Monster Skull message names all six Ancient Ones:** Felicitas, Timyra,
   Odion, Apathas, Amoras, and the unnamed author (Doloras by elimination).
4. **Ragnar is NOT the Female Hunter** from Character List — he's a separate male
   hunter added during development. The Female Hunter was never implemented.
5. **Clan territories on Map 10** are spatially separated: Hoskuld x≈11000-14000,
   Gunnar x≈17000-20000, Ezrekal in the south at y≈29000.
6. **Mythran uses standard English** (not Elean Speak) — his LV dialogue must
   match his established scholarly tone, not the Zealan pattern.

### Next Steps
- Track B: Write all 6 missing dialogue segments (B1-B6)
- Track C: Resolve placeholder names (C1) and design decisions (C2, C3)
- Track C can start now that A3 is complete

---

## Session 1 (continued) — Track B + Track C Complete

### What I did
Completed all 6 missing dialogue segments and all 3 design decisions:

**B1: Mythran's LV Dialogue** (`dialogue-mythran.md`)
- Full conversation tree: Zealans, Galjeron, double doors, key/puzzle
- Follows his base-game quest-giving pattern (Acknowledge → Theorize → Direct)
- Includes late-game return reactions (finding Vale, freeing gods)
- ~1100 words of new Mythran dialogue

**B2: Hunter NPC** (`dialogue-hunter.md`)
- Named "Sigrid" (Norse, fitting naming convention)
- Full personality: practical, independent, loves hunting and family
- Dialogue about hunting, harpies, husband, the feud, the Vale
- Post-reconciliation reaction (wants to hunt harpies)

**B3: Elemental Columns** (`dialogue-elemental-columns.md`)
- Four pillar destruction sequences with correct elemental oppositions
- Avatar barks, environmental barks, wrong-element damage
- Galjeron's journal hint for the puzzle solution
- Dungeon ambient barks for all four sections

**B4: Cloud Cliffs** (`dialogue-cloud-cliffs.md`)
- Tyorvi accompanies Avatar up the cliffs (his PTSD arc resolves)
- Environmental barks keyed to climb altitude
- Harpy combat barks
- Tyorvi's farewell at Cloud City — emotional payoff
- NPC reactions post-climb

**B5: AO Scene** (`dialogue-ao-scene.md`)
- Three gods speak: Felicitar (Joy), Doloras (Sorrow), Timyra (Courage)
- Gods use the "purest" Elean Speak — more formal than any NPC
- Avatar healed of poison. Wisdom given (but no specific Titan instructions)
- Ezrekal enters, reunites with her gods
- Reframed Timyra from "Fear/Apathy" to "Courage" (mastery of fear)

**B6: End-Game** (`dialogue-endgame.md`)
- Every surviving NPC reacts to the restoration
- Character-consistent reactions (Tyorvi vows sobriety, Atli admits he was wrong,
  child asks "what called are green things?")
- Ezrekal's farewell (longest NPC speech — recaps the heroic arc)
- Bag of Reagents and Defender Shield as rewards

**C1: Naming Decisions** (`naming-decisions.md`)
- Shrine of the Wheaties → Shrine of the Ancient Ones
- Sacred Smallish Unusual-Colored Rock → Sacred Circle (from usecode)
- Test of Rutabaga → Rite of Passage (from Atli's dialogue)
- Love/Hate/Apathy → Felicitar/Doloras/Timyra (base game canon)
- Two boys: Hoskuld and Gunnar (from SHADES usecode)
- All 8 placeholder names resolved with evidence

**C2: Romeo & Juliet** (`design-decisions.md`)
- Decision: CUT. No usecode evidence. Walk Through suggestion never developed.

**C3: Bag of Reagents** (`design-decisions.md`)
- Decision: LATE (quest reward from Ezrekal after gods freed).
  Confirmed by usecode: her existing bark is gated behind `godsFree`.

### Status
All Track A, B, and C tasks complete. The npc-dialogue agent has fulfilled
its scope:
- 6 missing dialogue segments drafted
- Character List → usecode name mapping resolved
- All placeholder names resolved
- All design ambiguities resolved

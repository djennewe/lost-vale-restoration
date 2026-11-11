# corpus-builder devlog

## 2026-03-20 — Session 1: Initial data extraction

### Step 1: Unpack and sort everything

**1a — GOG extras extracted:**
- All 6 GOG extra zips extracted to `shared/data/extracted/`
- 13 Lost Vale design PDFs found — these are the primary source documents:
  - Plot v1.1, Plot v1.2, Plot Synopsis with Notes, Walk Through
  - Character List 1.0, Art List v2.5, Art List Draft
  - Art Needs Email, Bug Report, Elean Speak Exerpt
  - Misc. Draft, Pitch Doc, Resource Schedules
- 5 base game reference PDFs (cluebook, manual, chronicle, map, reference card)

**1b — DOS game data extracted from GOG .pkg:**
- Used `pkgutil --expand-full` on the macOS .pkg installer
- Found English, French, German game data
- Copied English install to `shared/data/u8-install/`
- Copied `EUSECODE.FLX` (1.3 MB) to `shared/data/USECODE.FLX`

**Discovery: LV usecode already present!**
- Found `Sheri-U8-LV.zip` (539 KB) in `shared/data/discord/`
- This is the Dominus Dragon recovery from Sheri Graner Ray's diskette
- Copied to `shared/data/lv-usecode.zip` and extracted to `shared/data/lv-usecode/`
- Contains 3 directories, 71 files total:
  - `LOST VALE/` (11 files) — final LV usecode, dates Sep 7-13, 1994
  - `U8/` (23 files) — base game usecode from Sheri's work disk, mostly Jul 1994
  - `UNK files/UNK/` (33 files) — development snapshot, mixed dates Mar 1993 - Aug 1994
- Key LV characters found: Atli, Ezrekal, Tyorvi, Hrodny, Thordis, Ragnar, Ingyald, Changtar
- Key LV systems: FREE (free gods), ZEALSHLD (Zealan Shield), SHADES, AIRSPEL, FLAGS
- Key LV items: MAGNET, POTION, MONSKUL, PLAQUENS, BULLWHIP, FEDORA, BEDROLL
- NPC Lord British present (LORDBRIT.UNK) — confirms story beat #1

**1c — Inventory written:** `shared/data/INVENTORY.md`

### Step 2: Web sources

**Task 2 — Usecode analysis article:**
- ultimacodex.com article too JS-heavy to fetch directly
- Used web search and Discord screenshots instead
- Discord screenshots (preview.webp through preview-4.webp) are incredibly valuable:
  - Dominus Dragon's original post (1/28/25): "a small little bomb from the Origin Museum"
  - Armitage's analysis (2/1/25): identified clan names, usecode symbol meanings
  - Armitage's walkthrough reconstruction from the usecode
  - Annotated resource schedule showing what's found (✓) vs missing (✗)
- Output: `shared/corpus/usecode-index/lv-usecode-analysis.md`

**Task 3 — Codex wiki:** Fetched successfully. Full plot summary, characters, production history.
Output: `shared/corpus/plot-documents/codex-wiki-summary.md`

**Task 4 — Dino's Guide:** Fetched omissions page + dedicated Lost Vale page.
Key detail: entrance is at Bonecrusher's cave on the Plateau.
Output: `shared/corpus/plot-documents/dinos-guide-omissions.md`

**Task 5 — Sheri Graner Ray interviews:** Found and fetched two sources:
- Personal blog post "Looking Back on 20 years" (2014)
- GameBanshee interview (March 2013)
Key revelations: "Yoda-speak" dialogue, PTSD veteran, magnetic obelisk, TinyTar joke,
candlestick puzzle self-critique, cancellation night before submission.
Output: `shared/corpus/interviews/sheri-graner-ray.md`

### Step 3: Structured corpus documents

**PDF reading session — read all key design documents:**
- Plot v1.2 (3 pages): Complete 19-beat plot from LB message to god liberation
- Plot v1.1 (3 pages): Earlier version with different names (Draesh/Ikanikar → Snori/Hoskuld)
- Character List 1.0 (2 pages): Full NPC roster with personalities and writer assignments
- Walk Through (3 pages): Annotated walkthrough with handwritten notes
- Plot Synopsis with Notes (6 pages): Expanded version with 5 design recommendation notes
- Art List v2.5 (1 page): Complete asset list — meshes, terrain, items with time estimates
- Pitch Doc (2 pages): Business pitch dated 06/07/94, technical specs, schedule
- Elean Speak Exerpt (1 page): Actual usecode source code showing Ezrekal's dialogue

**Key discoveries from design docs:**
- "Magic Frisbee" was the working name for Shield of the Ancients
- "Shrine of the Wheaties" and "Sacred Smallish Unusual-Colored Rock" are placeholder names
- "Apathy, Love, and Hate" are working names for Felicitar, Doloras, Timyra
- Character List has NO proper names for NPCs — just archetypes ("Female elder", "Male Veteran")
- The two boys were originally "Draesh and Ikanikar" (v1.1) → "Snori and Hoskuld" (v1.2) → "Flossie and Snori" (Art List)
- Synopsis suggests a Titan-placed agent NPC, Bonecrusher hammer, and Birthplace of Moriens
- Walk Through has a Romeo & Juliet subplot not in other versions
- Art List shows: 3 gods speaking + 3 gods in resin, Harpy, Water Zombie, cloud architecture
- Elean Speak shows actual bark() and askList code — Ezrekal says "Sorry I am, acted so rudely before I did"

**YAML files written:**
- `story-beats.yaml`: 21 beats across 5 acts with full source citations
- `characters.yaml`: 25+ characters with factions, roles, writers, usecode files
- `locations.yaml`: 15 locations with connections and art notes
- `items.yaml`: 30+ items including quest items, rewards, obstacles
- `lv-symbols.yaml`: 28 LV symbols + 13 base game + 6 confirmed missing
- `GAP-ANALYSIS.md`: Comprehensive analysis of documented vs undocumented content

### Status: ALL IMMEDIATE TASKS COMPLETE

The corpus is ready for consumption by other agents. Key remaining work:
- usecode-disasm should analyze the actual .UNK files to extract dialogue and logic
- Remaining design PDFs (Misc. Draft, Bug Report, Resource Schedules) could yield more detail
- Creative design decisions needed for undocumented content (see GAP-ANALYSIS.md)

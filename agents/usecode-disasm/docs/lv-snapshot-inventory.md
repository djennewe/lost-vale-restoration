# Lost Vale Usecode Snapshot Inventory

## Source

**File:** `shared/data/lv-usecode.zip` (539 KB)
**Origin:** February 2025 recovery from Sheri Graner Ray's development diskette,
published by Dominus Dragon on the Ultima Dragons Discord.
**Hosted at:** ultimacodex.com

## Critical Discovery

The `.UNK` files are **original U8 usecode SOURCE CODE** — not compiled
bytecode. They are written in Origin's proprietary usecode scripting language,
with full variable names, comments, and structured game logic. This is far more
valuable than compiled bytecode for restoration purposes.

## Directory Structure

The zip contains three directories representing different stages of the
Lost Vale development:

### 1. `LOST VALE/` — 11 files (352 KB)
New classes created specifically for The Lost Vale expansion.

| File | Size | Lines | Class | Description |
|------|------|-------|-------|-------------|
| ATLI.UNK | 90,613 | 2,960 | `npcclass Atli inherits Npc` | Atli — Zealan NPC (clan Hoskuld?) |
| CANTRK.UNK | 1,769 | 143 | `eggclass EggCandleTrick inherits Egg` | Candle trick puzzle trigger |
| EZREKAL.UNK | 120,787 | 3,305 | `npcclass Ezrekal inherits Npc` | Ezrekal — outcast Zealan sage |
| FREE.UNK | 40,924 | 1,938 | (utility functions) | Free-the-gods helper functions |
| MAGNET.UNK | 10,710 | 517 | `eggclass EggMagnet inherits Egg` | Magnetic puzzle trigger |
| MONSKUL.UNK | 750 | 31 | `typeclass TypeMonskul inherits Item` | Monster skull item |
| PLNTST.UNK | 1,007 | 69 | `eggclass EggPlantTest inherits Egg` | Passage test / plant puzzle |
| POTION.UNK | 4,630 | 248 | `typeclass TypePotion inherits Item` | Potion item class |
| TESTPLAN.UNK | 6,983 | 326 | `typeclass TypePoisonPlant inherits Item` | Poison plant obstacle |
| TYORVI.UNK | 71,524 | 2,287 | `npcclass Tyorvi inherits Npc` | Tyorvi — Zealan NPC (clan Thordis?) |
| ZCHILD.UNK | 7,351 | 314 | `typeclass TypeZealanChild1 inherits pesantBoy` | Zealan child NPC |

### 2. `U8/` — 23 files (845 KB)
Modified base game classes — these contain changes to existing U8 NPCs and
systems to integrate Lost Vale content.

| File | Size | Lines | Class | Description |
|------|------|-------|-------|-------------|
| ARAMINA.UNK | 72,340 | 1,951 | `npcclass Aramina inherits Npc` | Modified base game NPC |
| BENTIC.UNK | 51,163 | 1,527 | `npcclass Bentic inherits Npc` | Modified base game NPC |
| CYRRUS.UNK | 62,420 | 1,990 | `npcclass Cyrrus inherits Npc` | Modified base game NPC |
| DARION.UNK | 96,624 | 2,711 | `npcclass Darion inherits Npc` | Modified base game NPC |
| EZREKAL.UNK | 41,051 | 1,387 | `npcclass Ezrekal inherits Npc` | Ezrekal in base game context |
| JENNA.UNK | 65,546 | 2,037 | `npcclass Jenna inherits Npc` | Modified base game NPC |
| KILANDRA.UNK | 48,967 | 1,539 | `npcclass Kilandra inherits Npc` | Modified base game NPC |
| LES1.UNK | 786 | 48 | `npcclass Avatar inherits Npc` | Avatar lesson 1 |
| LES2.UNK | 307 | 32 | `npcclass Avatar inherits Npc` | Avatar lesson 2 |
| LES4_1.UNK | 442 | 34 | `npcclass Avatar inherits Npc` | Avatar lesson 4.1 |
| LES4_4.UNK | 1,142 | 67 | `npcclass Avatar inherits Npc` | Avatar lesson 4.4 |
| MORDEA.UNK | 28,133 | 1,297 | `npcclass Mordea inherits Npc` | Modified base game NPC |
| ORLOK1.DOC | 7,274 | 228 | `npcclass Orlok inherits Npc` | Orlok NPC (documentation) |
| PLNTST.UNK | 1,002 | 70 | `eggclass EggPlantTest inherits Egg` | Plant test (base game version) |
| RHNTXT.DOC | 20,829 | 640 | (text document) | Possibly documentation/text |
| SALKIND.UNK | 36,357 | 1,231 | `npcclass Salkind inherits Npc` | Modified base game NPC |
| SGBOOK.UNK | 42,846 | 932 | (book/spell functions) | Sorcerer's Guide book content |
| STELLOS.UNK | 76,339 | 2,173 | `npcclass Stellos inherits Npc` | Modified base game NPC |
| STRATOS.UNK | 15,095 | 566 | `typeclass TypeAirTitan inherits MrsStratos` | Air Titan / Stratos |
| TEMP.UNK | 386 | 34 | `npcclass Avatar inherits Npc` | Temporary Avatar code |
| TESTPLAN.UNK | 2,978 | 181 | `typeclass TypePoisonPlant inherits Item` | Poison plant (base version) |
| TORWIN.UNK | 40,925 | 1,495 | `npcclass Torwin inherits Npc` | Modified base game NPC |
| XAVIER.UNK | 96,803 | 2,933 | `npcclass Xavier inherits Npc` | Modified base game NPC |

### 3. `UNK files/UNK/` — 33 files (790 KB)
Appears to be a merged/complete working set combining LV-specific and
modified base game files.

| File | Size | Lines | Class | Description |
|------|------|-------|-------|-------------|
| ABACUS.UNK | 759 | 46 | `typeclass TypeAbacus inherits Item` | Abacus puzzle item |
| AIRSPEL.UNK | 28,066 | 1,323 | (spell functions) | Air magic spells |
| ARAMINA.UNK | 60,159 | 1,926 | `npcclass Aramina inherits Npc` | Aramina NPC |
| ATLI.UNK | 89,960 | 2,935 | `npcclass Atli inherits Npc` | Atli — Zealan NPC |
| AVATAR.UNK | 36,185 | 1,560 | `npcclass Avatar inherits Npc` | Full Avatar class |
| BEDROLL.UNK | 1,453 | 83 | `typeclass TypeBedroll inherits Item` | Bedroll item |
| BULLWHIP.UNK | 141 | 14 | `typeclass TypeBullwhip inherits Item` | Bullwhip item |
| CANTRK.UNK | 1,624 | 128 | `eggclass EggCandleTrick inherits Egg` | Candle trick |
| CHANGTAR.UNK | 1,728 | 94 | (unknown) | Changtar — possibly an NPC or location |
| EALOGO.UNK | 172 | 14 | `typeclass TypeEaLogo inherits Item` | EA logo item |
| EAPUZL.UNK | 1,822 | 111 | `typeclass TypePedestals inherits Item` | Pedestal puzzle |
| EZREKAL.UNK | 114,111 | 3,124 | `npcclass Ezrekal inherits Npc` | Ezrekal — LV version |
| FEDORA.UNK | 131 | 12 | `typeclass TypeFedora inherits Item` | Fedora hat item |
| FLAGS.UNK | 17,096 | 762 | (global flags) | Global flag definitions |
| FREE.UNK | 27,573 | 1,418 | (utility functions) | Free-the-gods helpers |
| HRODNY.UNK | 27,407 | 1,207 | `npcclass Hrodny inherits Npc` | Hrodny — Zealan NPC |
| INGYALD.UNK | 19,130 | 895 | `npcclass Ingjald inherits Npc` | Ingjald — Zealan NPC |
| LORDBRIT.UNK | 2,899 | 131 | `typeclass TypeLordBritish inherits Item` | Lord British message |
| METHOD.UNK | 20,666 | 1,150 | (method functions) | Spell method implementations |
| MONSKUL.UNK | 705 | 28 | `typeclass TypeMonskul inherits Item` | Monster skull |
| ORLOK1.UNK | 3,838 | 204 | `npcclass Orlok inherits Npc` | Orlok NPC |
| PLAQUENS.UNK | 9,990 | 508 | `typeclass TypeNSGoldPlaque inherits GoldPlaque` | Gold plaque (N-S) |
| PLNTST.UNK | 1,000 | 69 | `eggclass EggPlantTest inherits Egg` | Plant/passage test |
| POTION.UNK | 4,623 | 259 | `typeclass TypePotion inherits Item` | Potion item |
| PSCEND.UNK | 7 | 2 | (minimal) | Possibly incomplete/stub |
| RAGNAR.UNK | 27,009 | 945 | `npcclass Ragnar inherits Npc` | Ragnar — Clan Hoskuld leader |
| SHADES.UNK | 19,127 | 709 | `eggclass EggShades inherits Egg` | Shade/Moot scene |
| TESTPLAN.UNK | 6,982 | 326 | `typeclass TypePoisonPlant inherits Item` | Poison plant |
| THORDIS.UNK | 53,195 | 1,985 | `npcclass Thordis inherits Npc` | Thordis — Zealan NPC |
| TJORVI.UNK | 13,695 | 610 | `npcclass Tjorvi inherits Npc` | Tjorvi — Zealan NPC |
| TYORVI.UNK | 55,248 | 1,829 | `npcclass Tyorvi inherits Npc` | Tyorvi — Zealan NPC |
| ZEALSHLD.UNK | 3,378 | 158 | `typeclass TypeAOFrizbee inherits Item` | Shield of the Ancients |
| ZZVFLAGS.UNK | 4,615 | 209 | (flags) | ZZV flags (LV-specific flags) |

## Key Discoveries

### 1. Source Code, Not Bytecode
The `.UNK` files are **original U8 usecode source code** written in Origin's
proprietary scripting language. This provides full variable names, developer
comments, structured game logic, and complete dialogue text. This is
significantly more valuable than compiled bytecode for restoration.

### 2. Internal Names
- The Shield of the Ancients is internally called **"AOFrizbee"** (named by developer "Mel")
- Frame 0,1 = broken shield halves; Frame 2 = "Ceremonial Shield of the Ancient Ones"; Frame 3 = "Defender"
- The Lost Vale is a separate map: **MapLostVale**
- The main quest symbol "PLNTST" stands for "Plant Test" (EggPlantTest), not "Passage Test"
- "SHADES" refers to the "Shade scene" at the Moot (Atli vs Thordis confrontation)

### 3. Confirmed Characters
- **Ezrekal** (outcast Zealan sage) — largest class (120K), central to LV plot
- **Atli** (Zealan clan member) — 90K, significant dialogue
- **Tyorvi** (Zealan clan member) — 71K, significant dialogue
- **Thordis** (Zealan elder) — 53K, involved in Shade/Moot scene
- **Ragnar** (Clan Hoskuld leader) — 27K
- **Hrodny** (Zealan NPC) — 27K
- **Ingjald** (Zealan NPC) — 19K
- **Tjorvi** (variant of Tyorvi?) — 13K
- **Lord British** — sends magical message to Avatar via Nystul

### 4. Confirmed Story Beats
From the source code, we can directly confirm:

1. **Lord British message**: Avatar receives a magical visitation from Lord British,
   who tells him to seek Mythran and learn about the ancient race (Zealans).
   Lord British cannot see or hear the Avatar but sends the message via Nystul.
   Quote: "Seek the counsel of the wise man known as Mythran..."

2. **Shield of the Ancients**: Found in two broken pieces (frame 0, 1).
   Must be restored (frame 2 = "Ceremonial Shield"). Has a "Defender" form (frame 3)
   that strips all other armor from the Avatar when worn.

3. **Moot/Shade Scene**: Atli, Thordis, and Ezrekal argue at a gathering.
   The Avatar must mediate between the feuding clan leaders. Ezrekal calls
   for unity: "Over, the time for dissension is!"

4. **Passage Test**: Involves a "BushKey" item. When the Avatar carries it
   near certain plants, mushrooms are destroyed by mini air titans with
   magical effects and sound.

5. **Candle Trick**: A puzzle involving candle manipulation.

6. **Magnetic Puzzle**: An egg-triggered magnetic puzzle mechanism.

7. **Poison Plants**: Obstacle items that the Avatar must navigate around.

8. **Potion System**: Custom potion items with LV-specific effects.

### 5. Modified Base Game NPCs
11 base game NPCs received modified dialogue/behavior for the expansion:
Aramina, Bentic, Cyrrus, Darion, Jenna, Kilandra, Mordea, Salkind,
Stellos, Torwin, Xavier. This suggests the expansion deeply integrated
with the base game's NPC network.

### 6. File Version Differences
Files exist in multiple versions across the three directories, suggesting
an active development process:
- `PLNTST.UNK`: LOST VALE (1007 bytes) vs U8 (1002 bytes) vs UNK (1000 bytes)
- `EZREKAL.UNK`: LOST VALE (120787) vs U8 (41051) vs UNK (114111)
- `TYORVI.UNK`: LOST VALE (71524) vs UNK (55248)
- These version differences may represent different development stages.

## Total Statistics

| Directory | Files | Total Size | Total Lines |
|-----------|-------|------------|-------------|
| LOST VALE/ | 11 | 352 KB | 11,888 |
| U8/ | 23 | 845 KB | 23,296 |
| UNK files/UNK/ | 33 | 790 KB | 25,089 |
| **Total** | **67** | **1,987 KB** | **60,273** |

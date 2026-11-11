# Lost Vale Usecode Analysis — Final Report

## Executive Summary

The recovered Lost Vale usecode snapshot contains **original U8 usecode source
code** from Origin Systems' development of The Lost Vale expansion (1994). This
is not compiled bytecode but the actual scripting language source, providing
complete game logic, dialogue text, variable names, and developer comments.

**67 source files** totaling ~60,000 lines of code define the expansion's
characters, items, puzzles, and quest logic. Combined with the base game's 516
compiled usecode classes (fully disassembled and cross-referenced), this gives us
a comprehensive understanding of both the base game's scripting architecture and
the expansion's intended content.

## Source Code Language

The files use Origin's proprietary U8 usecode scripting language with:
- C-like syntax with `process` functions (concurrent execution model)
- Class inheritance: `npcclass Foo inherits Npc`, `typeclass Bar inherits Item`,
  `eggclass Baz inherits Egg`
- Event-driven handlers: `look()`, `use()`, `hatch()`, `schedule()`, etc.
- Global flag system: `globalflag flagName` with optional bit-width specifiers
- Process management: `spawn`, `wait()`, `suspend`
- Localization support: German and French translation comments (`//@@@Translate`)
- NPC dialogue via `bark()` with multi-line string literals

## Characters

### New Lost Vale NPCs

| Character | Class | Size | Role |
|-----------|-------|------|------|
| **Ezrekal** | `npcclass Ezrekal` | 120K | Outcast Zealan sage; central quest-giver who speaks in inverted Yoda-like syntax ("Over, the time for dissension is!") |
| **Atli** | `npcclass Atli` | 90K | Zealan clan member; involved in Moot/Shade scene dispute |
| **Tyorvi** | `npcclass Tyorvi` | 71K | Zealan clan member; has schedule-based behavior |
| **Thordis** | `npcclass Thordis` | 53K | Zealan elder; feuds with Atli at the Moot |
| **Ragnar** | `npcclass Ragnar` | 27K | Clan Hoskuld hunter; distinctive inverted speech pattern ("Hard to understand you are"); schedules between home and fields on map 10 |
| **Hrodny** | `npcclass Hrodny` | 27K | Zealan NPC with conversation trees |
| **Ingjald** | `npcclass Ingjald` | 19K | Zealan NPC (spelling variant: Ingyald) |
| **Tjorvi** | `npcclass Tjorvi` | 13K | Zealan NPC (variant of Tyorvi?) |
| **Zealan Child** | `typeclass TypeZealanChild1 inherits pesantBoy` | 7K | Zealan child NPC |

### Modified Base Game NPCs

11 existing U8 NPCs received dialogue modifications to integrate LV content:
Aramina, Bentic, Cyrrus, Darion, Jenna, Kilandra, Mordea, Salkind, Stellos,
Torwin, Xavier. This deep integration suggests the expansion would have felt
like a natural extension of the base game rather than a bolt-on addition.

### Lord British

A special item class (`TypeLordBritish`) triggers a magical visitation scene:
- Lord British appears with colored magic sparkles (blue, yellow, red)
- He barks: "Avatar, I have found a portal through which I can speak..."
- Message delivered via Nystul, who pierced the Guardian's dark veil
- Instructs the Avatar to seek Mythran and learn about the ancient race (Zealans)
- Includes a puppet animation sequence
- Tracked by flags: `lbStarted`, `lbDone`

## Items and Objects

| Item | Internal Name | Description |
|------|--------------|-------------|
| **Shield of the Ancients** | `TypeAOFrizbee` | Found broken in two pieces (frames 0,1). Restored as "Ceremonial Shield of the Ancient Ones" (frame 2). "Defender" form (frame 3) strips all other armor. Named "AOFrizbee" by developer "Mel". |
| **Bush Key** | `TypeBushKey` | Key item for the Passage Test |
| **Poison Plant** | `TypePoisonPlant` | Obstacle item in the Lost Vale |
| **Potion** | `TypePotion` | Custom potion with LV-specific effects |
| **Monster Skull** | `TypeMonskul` | Item found in the Lost Vale |
| **Bedroll** | `TypeBedroll` | Camping item |
| **Bullwhip** | `TypeBullwhip` | Weapon/tool item |
| **Fedora** | `TypeFedora` | Hat item (Indiana Jones reference?) |
| **EA Logo** | `TypeEaLogo` | Easter egg item |
| **Gold Plaque (N-S)** | `TypeNSGoldPlaque inherits GoldPlaque` | Inscribed plaque with text |
| **Pedestal** | `TypePedestals` | Puzzle element |
| **Abacus** | `TypeAbacus` | Puzzle item |

## Puzzles and Mechanics

### Passage Test (PLNTST)
- Triggered by `EggPlantTest::hatch()`
- Tests if Avatar carries `TypeBushKey` (frame 0) in their inventory
- If key is present: destroys mushrooms (`TypeShortmushroom`) within 100 cells
  by spawning mini air titans (`TypeMiniAirTitan`) that animate and play
  `MAGIC1` sound effect
- Stasis is set during the sequence

### Moot/Shade Scene (SHADES)
- Triggered by `EggShades::hatch()`
- Teleports Atli, Thordis, and Ezrekal to specific coordinates on MapLostVale
- Checks for Shield of the Ancients (`TypeAOFrizbee`) in Avatar's backpack
- If shield not present, Ezrekal says: "Bring the sacred shield, you must!"
- Scene involves: Avatar pathfinding to position, camera scrolling to Ezrekal,
  Ezrekal casting animations, a squabble between NPCs, Avatar mediating
- Avatar gets dialogue choices: "Can't you two get along!?", "Let's be reasonable..."
- Tracked by flags: `doneShades`, `inShadeScene`

### Candle Trick (CANTRK)
- `EggCandleTrick::hatch()` — a candle-based puzzle mechanism

### Magnetic Puzzle (MAGNET)
- `EggMagnet::hatch()` — magnetic-themed puzzle with 5 functions

### Elemental Columns
- Four elemental columns that must be destroyed:
  - `WaterColumnDestroyed`, `FireColumnDestroyed`
  - `EarthColumnDestroyed`, `AirColumnDestroyed`
  - `allColumnsDestroyed` flag tracks completion

## Quest Structure (from flags and logic)

### Global Flags (from FLAGS.UNK and ZZVFLAGS.UNK)

631 global flags define the expansion's state machine. Key categories:

**Quest Progress:**
- `lbStarted`, `lbDone` — Lord British message sequence
- `doneShades`, `inShadeScene` — Moot confrontation
- `WaterColumnDestroyed`, `FireColumnDestroyed`, `EarthColumnDestroyed`,
  `AirColumnDestroyed`, `allColumnsDestroyed` — Elemental column puzzle
- `godsSpoke` — The imprisoned gods have spoken
- `stormsOn` — Weather/storm state

**NPC Conversation Tracking:**
Each major NPC has conversation state flags:
- Ezrekal: `metEzrekal`, `spokeEzrekal`, etc.
- Thordis: `toldSelf`, `toldTyorvi`, `toldRagnar`, `toldAtli`, `toldHrodny`, `toldIngyald`
- Ragnar, Atli, Hrodny, Ingyald: similar per-NPC tracking
- `beganConvo` — Generic conversation-in-progress flag

**Avatar State:**
- `avX`, `avY`, `avZ`, `avMap` — 16-bit position storage (for teleportation/restoration)
- `avatarPoisoned` — Poison status
- `cliffClimbing` — Climbing state

**World State:**
- `limitTornado:3` — Tornado limiter (3-bit value)
- `thordisSchedule:2` — Thordis schedule state (2-bit value)
- `spokeOfThordis`, `likeThordis` — NPC opinion tracking

### Map Reference
The Lost Vale exists as a separate game map: **MapLostVale** (referenced in
teleport calls and map checks). The map number appears to be 10 (based on
Ragnar's schedule code which references map 10).

## Localization

The source code includes localization markers:
- `// @@@ ready to translate french` (EZREKAL.UNK)
- `//@@@Tranlate g f` (LORDBRIT.UNK — note the typo)
- `//@@@ TRANSLATE FG` (ZEALSHLD.UNK)
- The `askYesNo()` function in FREE.UNK has German ("Ja"/"Nein") and French
  ("Oui"/"Non") string alternatives

This confirms the expansion was being prepared for international release at the
time of cancellation.

## Air Magic System (AIRSPEL.UNK)

A 28K file containing 10 spell functions — the air magic system for the
Lost Vale. This likely represents new spells available in the expansion,
possibly including the "Shrink" spell mentioned in design documents.

## Development Notes

### Developer Comments in Source
- `"Named by Mel, thank you"` — regarding the `AOFrizbee` shield name
- `"a nightmarish hack to get this file to link"` — in ZZVFLAGS.UNK
- `"//********LEAVE THIS IN*************"` — coordinate hardcoding in SHADES.UNK
- `"//@@@Translate"` markers throughout — localization was in progress

### Code Quality Observations
- Well-structured object-oriented design using class inheritance
- Consistent use of the process/spawn model for concurrent behavior
- NPC dialogue trees use `ask()` with string lists for player choices
- Schedule system for NPC daily routines (eventide/morning/afternoon)
- Extensive use of `wait()` for timing and animation sequencing

### File Version Analysis
Multiple versions of some files across directories suggest active development:
- EZREKAL.UNK: LV version (120K) is 3x the U8 version (41K) — extensive expansion
- TYORVI.UNK: LV version (71K) vs UNK version (55K) — ongoing refinement
- These differences could represent different development snapshots or branches

## Implications for Restoration

### What We Have
1. **Complete game logic** for all LV-specific content (NPCs, items, puzzles)
2. **Full dialogue text** for all characters including localization notes
3. **Quest state machine** with 631 global flags defining every state transition
4. **Modified base game code** showing exactly how LV integrated with U8
5. **Air magic system** with new spell implementations
6. **Internal naming conventions** and developer notes

### What We Still Need
1. **Shape/sprite data** — The code references shape types (TypeBushKey,
   TypeMiniAirTitan, etc.) but the actual graphics are not in this snapshot
2. **Map data** — MapLostVale is referenced but the map file itself isn't here
3. **Sound/music** — Sound effect names (MAGIC1, etc.) are referenced
4. **The "uses" libraries** — Some includes (egg, free, flags, npc, item, snddefs)
   are U8 standard libraries, but the expansion may have modified them

### Restoration Path
The source code can be:
1. Compiled using a reconstructed U8 usecode compiler (or transpiled to C++)
2. Integrated into ScummVM's Ultima 8 engine
3. Combined with reconstructed shape/map data from other corpus sources
4. The 631 flags can be mapped to the base game's global bit-field addresses

This source code represents the most complete and authoritative record of The
Lost Vale's intended gameplay. Combined with the design documents, cluebook
references, and interview material, it provides a solid foundation for faithful
restoration of the cancelled expansion.

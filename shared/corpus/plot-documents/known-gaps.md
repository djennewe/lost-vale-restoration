# Known Gaps in the Recovered Lost Vale Material

Source: Armitage analysis, Ultima Dragons Discord (#ultima-8-exult), 2025-01/02.
Cross-referenced with `GAP-ANALYSIS.md` and the production schedule annotations.

---

## Confirmed Missing from Usecode Snapshot

These items were marked with **red X** on the annotated resource schedule,
indicating they were never completed before the project was cancelled.

### Missing Dialogue / Usecode

| Content | Assigned To | Evidence |
|---------|-------------|----------|
| **Mythran dialogue** | Andrew | Red X on schedule; confirmed missing by Armitage |
| **Usecode: Columns** | Brian M. | Red X; elemental dungeon pillars/columns |
| **Usecode: Cliffs** | Brian M. | Red X; Cloud Cliffs game logic |
| **Usecode: AO scene** | Andrew | Red X; Ancient Ones freeing set piece |
| **Usecode: Bag o' Reagents** | Andrew | Red X; final reward item implementation |
| **Convos: Hunter** | Brian M. | Red X; Hunter NPC from Clan Hoskuld |

### Missing End-Game Events (Steps 17–21)

The usecode snapshot contains flags and references for the end-game but NOT
the full implementation. Specifically missing:

- The complete Ancient Temple interior sequence
- The god-freeing ceremony dialogue and animations
- The "water flows, plants return" restoration cutscene
- The Bag of Reagents reward delivery
- The Shield-on-altar interaction
- Any U9 teaser dialogue from the gods

**What we DO have for end-game:**
- `FREE.UNK` (40 KB) — trigger/flag logic for freeing the gods
- Flags: `godsFree`, `godsSpoke`, `templeOpen`, `ezToTemple`, `getPowerAO`
- `TypeBagOReagents` type reference in the cross-reference

---

## Implications for Restoration

### Content that must be written from scratch:

1. **Mythran's LV dialogue** — We know from the plot docs that Mythran tells
   the Avatar about the Zealans, Galjeron, and the double doors. But no
   dialogue text survives. Must be written to match Mythran's existing
   base-game speech patterns.

2. **Elemental dungeon column mechanics** — We know there are four elemental
   columns destroyed with opposite elements (`WaterColumnDestroyed`, etc.)
   but the actual puzzle/combat mechanics are missing.

3. **Cloud Cliffs traversal** — The `climbedCliffs` and `attemptedCliffs`
   flags exist, as does `agreeToClimb`, but the climbing gameplay sequence
   is missing.

4. **AO scene (god-freeing ceremony)** — The dramatic set piece where the
   gods are freed from their amber prison. `FREE.UNK` has the trigger logic
   but not the full cinematic/dialogue.

5. **Bag of Reagents item** — The reward item needs implementation. We know
   from the design docs it "eliminates reagent hunting" and from the flags
   that `TypeBagOReagents`, `haveReagents`, `haveReagentsDone` track its state.

6. **Hunter NPC dialogue** — The Female Hunter from Clan Hoskuld (Character
   List) has no surviving dialogue. Brian M. was assigned but did not complete.

### Content that can be reconstructed from surviving usecode:

Everything NOT listed above has surviving source code. In particular:
- All NPC conversations (Ezrekal, Atli, Tyorvi, Thordis, Ragnar, Hrodny, Ingyald)
- Passage Test mechanics (PLNTST)
- Moot/Shade scene (SHADES)
- Candle puzzle (CANTRK)
- Magnetic puzzle (MAGNET)
- Shield of the Ancients item logic (ZEALSHLD)
- Lord British message sequence (LORDBRIT)
- Air spell system (AIRSPEL)
- All 631 global flags defining quest state

### Speculative elements (from Armitage, flagged as uncertain):

- **Step 8:** "Bag contains some sort of key" — the exact mechanism for
  recovering the Passage Stone from the lake is inferred, not confirmed
- **Step 13:** "Avatar finds the root, gets the potion" — the root's
  specific location is not stated
- **Step 19:** "Avatar finds the key, opens the chest" — Hrodny's lost
  key location is not specified

These speculative elements are plausible inferences from the usecode flags
(`hasRoot`, `givenRoot`, `gotTheKey`, `hasTea`, `givenTea`) but the exact
gameplay flow would need design decisions during restoration.

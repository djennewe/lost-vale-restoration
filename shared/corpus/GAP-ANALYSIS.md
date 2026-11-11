# Gap Analysis: What We Know vs. What We Need

## Summary

The corpus has strong coverage of the **overall story arc**, **character concepts**, and
**NPC dialogue** for the Lost Vale content. The primary gaps are in **dungeon design**,
**mechanical specifics**, **map layouts**, and **end-game events**.

---

## DOCUMENTED (high confidence)

### Story
- Complete 19-beat plot arc from Lord British's message through god liberation (Plot v1.2)
- Alternate/expanded plot notes with design suggestions (Plot Synopsis with Notes)
- Backstory: Great Council attack, Shield breaking, clan feud origin
- Resolution: Shield restoration ceremony, shades reveal truth, gods freed
- Character motivations and relationships (Character List 1.0)

### Characters
- All named NPCs with roles and personality descriptions
- Writer assignments (who wrote which NPC's dialogue)
- Ezrekal's dialogue style ("Elean Speak" — inverted syntax, actual code sample)
- Character dynamics within each clan (the veteran's PTSD, the inventor's atheism, etc.)
- Clan names: Hoskuld and Gunnar (from Discord analysis)

### Items
- Complete art asset list (Art List v2.5) with all items, terrain, and character meshes
- Shield of the Ancients (half/whole), four elemental talismans, pillars
- Bag of Reagents, Tiny Tar potion, Passage Test plant
- Development time estimates for each art asset (handwritten annotations)

### Usecode
- 11 final LV usecode files + 17 development-stage files with descriptions
- Key symbol meanings confirmed: PLNTST, SHADES, FREE, MAGNET, CANTRK, POTION
- Actual dialogue code sample (Elean Speak Exerpt)
- What's confirmed missing from the archive

### Development History
- Complete development timeline (April 15 – August 15, 1994)
- Team roster and individual assignments per month
- Cancellation circumstances (interviews)
- Business context (Pitch Doc dated June 7, 1994)

---

## PARTIALLY DOCUMENTED (some info, needs design decisions)

### The Elemental Dungeon
- **Known:** Four sections (Earth, Air, Fire, Water), each contains a talisman/gemstone
- **Known:** Four elemental pillars at exit, destroyed with opposite element
- **Known:** Synopsis suggests a "multi-elemental agent" NPC as recurring antagonist
- **Unknown:** Specific puzzle designs, room layouts, monsters per section, map geography
- **Unknown:** Whether separate maps or one continuous dungeon
- **Decision needed:** Design all dungeon content from scratch within the established framework

### The Passage Test / Rite of Passage
- **Known:** Involves a "nasty plant" with fruit guarded by poisonous spines
- **Known:** Avatar always fails and gets poisoned (this is plot-critical)
- **Known:** PLNTST.UNK exists (1 KB) — very small, may just be a trigger
- **Unknown:** Exact mechanics of the test, whether it's a combat or puzzle sequence
- **Decision needed:** Mechanical design of the test encounter

### Cloud World Layout
- **Known:** Architecture is "Bob's red stone architecture turned white and gold"
- **Known:** Cloud-like terrain, collapsing ground, magnetic obelisk
- **Known:** Contains the scroll from the gods and the Shield halves + skeletons
- **Unknown:** Map layout, room count, specific puzzle sequences
- **Decision needed:** Full Cloud World map design

### The Shrine / Temple
- **Known:** Gods encased in amber-like resin ("like Dune shields")
- **Known:** Must break through a wall or defeat a guardian to enter
- **Known:** Tiny Tar potion needed to enter (shrink to fit through entrance?)
- **Unknown:** Interior layout, the god-freeing ceremony mechanics
- **Decision needed:** Shrine interior design and ceremony implementation

### NPC Final Names
- **Known:** Character archetypes and personalities (Character List 1.0)
- **Known:** Some proper names from usecode (Atli, Tyorvi, Thordis, Hrodny, Ragnar, Ingyald, Changtar)
- **Unknown:** Which Character List archetype maps to which usecode name
- **Partially known:** Ragnar → Clan Hoskuld (confirmed by Armitage)
- **Decision needed:** Assign proper names to all unnamed Character List archetypes

### Placeholder Name Replacements
- **Known placeholders:**
  - "Shrine of the Wheaties" → probably "Shrine of the Ancient Ones"
  - "Sacred Smallish Unusual-Colored Rock" → needs a proper name
  - "Test of Rutabaga" → "Rite of Passage" / "Passage Test" (likely final)
  - "Apathy, Love, and Hate" → Felicitar, Doloras, Timyra (from base game)
- **Decision needed:** Confirm final names for all placeholders

---

## UNDOCUMENTED (needs design from scratch)

### Missing Usecode Content
The following content was confirmed missing from the recovered archive and has no
design documentation beyond the plot outline:

1. **Mythran's dialogue** — How exactly does Mythran introduce the Lost Vale? What
   puzzle does he describe? What does he know about Galjeron?

2. **Elemental dungeon usecode** — "Columns" and "Cliffs" sections (marked ✗ on
   Armitage's annotated schedule)

3. **AO Scene** — "Ancient Ones scene" — the set piece for freeing the gods. We have
   FREE.UNK (the flag/trigger) but not the cinematic/dialogue content.

4. **Bag of Reagents** usecode — The reward item implementation

5. **End-game events** — What happens after the gods are freed? The plot says "water
   flows, green plants, PC gets his bag, blood feud ended, all are happy" but no
   usecode exists for this sequence.

### Map/Level Design
- No map layouts survive for any LV area
- Pitch Doc says "approximately five new maps" but no specifics
- Art List terrain pieces and architecture notes are the only guidance
- All maps must be designed from scratch for ScummVM/Pentagram engine

### Combat and Encounter Design
- Harpie behavior/stats
- Water Zombie behavior/stats
- Multi-elemental agent (if used) behavior/stats
- Any other encounters in the dungeon or cliffs

### Technical Integration
- How does the expansion hook into the base game? (double doors trigger)
- Teleporter pad at dungeon exit (Synopsis suggestion)
- Travel between Pagan and Lost Vale (Synopsis recommendation)
- Save game compatibility
- ScummVM engine capabilities and limitations

### Sound and Music
- No sound design documentation exists
- No music specifications
- Original U8 audio is available for reference

---

## CONFLICTS AND AMBIGUITIES

### Plot v1.2 vs. Plot Synopsis — Different Trust-Gaining Mechanisms
- **Plot v1.2:** Avatar takes "Test of Rutabaga" (plant test), fails, gets poisoned
- **Synopsis:** Avatar must complete two quests — kill monster for Group 1, recover
  stolen item for Group 2 — before being allowed to visit Ezrekal
- **Resolution needed:** Which version to implement? The usecode (PLNTST) supports v1.2.

### Bag of Reagents Timing
- **Plot v1.2:** Given at the very end as a reward
- **Synopsis:** Recommends Mythran give it early (beat 2)
- **Walk Through annotation:** "Pay off Weapon → Bag of reagents"
- **Resolution needed:** Choose timing. Early gift makes the expansion more generous;
  late gift maintains it as a quest reward.

### God Names
- **Design docs:** "Love, Hate, and Apathy"
- **Base game canon:** Felicitar, Doloras, Timyra
- **Resolution:** Use base game names. Design doc names were working placeholders.

### Two Boys' Names
- **Plot v1.1:** Draesh and Ikanikar
- **Plot v1.2:** Snori and Hoskuld
- **Art List:** Flossie and Snori
- **Resolution needed:** The Art List is dated June 28 (later than both plot docs from
  May 9), so "Flossie and Snori" may be the intended final names. But Armitage's
  analysis uses "Clan Hoskuld" and "Clan Gunnar" from the usecode.

### Young Couple Romeo & Juliet Subplot
- **Walk Through (beat XIII):** "There is a young couple, one from each side of the feud,
  who are in love. The Avatar uses them to reunite the two factions."
- **Plot v1.2:** Does not mention this subplot
- **Resolution needed:** Was this cut or added later? No usecode evidence either way.

---

## PRIORITY RECOMMENDATIONS

1. **Highest priority:** Have usecode-disasm agent analyze the actual .UNK files to
   extract dialogue text and game logic. This will resolve many unknowns.

2. **Second priority:** Read all remaining design PDFs (Misc. Draft, Bug Report,
   Resource Schedules) for additional details.

3. **Third priority:** Design decisions for the undocumented content (dungeon layouts,
   Cloud World map, encounter design) — these require creative decisions informed by
   the corpus but cannot be derived from it.

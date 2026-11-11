# Asset Reuse Plan — Lost Vale Map Design

Cross-reference of Art List v2.5 requirements, corpus items, and available
U8 shapes from TYPEFLAG.DAT / U8SHAPES.FLX / GLOB.FLX.

## Methodology

The base game has 2,048 shapes and 2,129 non-empty globs. The Lost Vale design
documents specify terrain types, items, and creatures needed for the expansion.
This plan identifies what can be reused directly, what needs new art, and what
can be approximated with existing assets.

---

## 1. Terrain and Tile Assets

### Lost Vale Overworld (Map 10)

**Art notes:** "barren is sometimes boring — cool fallen ruins" (Synopsis)

| Need | Reusable Shapes | Notes |
|------|-----------------|-------|
| Barren ground | Shapes 3, 6, 11, 128, 242, 409 (206 LND shapes) | Extensive ground tile library |
| Rocky terrain | Shapes 65, 92, 94, 126 and many more | Solid terrain decorations |
| Cliff walls | Shapes 26–32, 125, 301, 334 (89 DRW shapes) | Full directional set |
| Water (lake) | Shapes 347, 669, 710, 738 (14 SEA shapes) | Lake area and springs |
| Ruins/rubble | Shapes in decorations category (1,466 shapes) | Abundant options |
| Vegetation (sparse) | Various decoration shapes | Limited — LV is barren |
| Roofs/overhangs | Shapes 9, 34, 36, 37, 77 (36 ROF shapes) | For cave/dwelling roofs |

**Glob reuse:** 532 terrain-only globs available. Standard 16-item ground tiles
can compose the entire overworld floor.

**Assessment:** Fully achievable with existing assets. The "barren valley" theme
works well with existing rocky terrain shapes.

### Elemental Dungeon

| Need | Reusable Shapes | Notes |
|------|-----------------|-------|
| Dungeon walls | Shapes 489–499, 678–680 (stone walls) | Base game dungeon tileset |
| Dungeon floors | Existing ground shapes with cave textures | Multiple options |
| Lava/fire tiles | Shapes 318, 385, 435–438, 636 (25 DMG shapes) | For Fire section |
| Water tiles | Shapes 57, 63, 72, 129, 347 | For Water section |
| Earth elements | Standard terrain shapes | For Earth section |
| Air elements | Translucent shapes (SI_TRANSL flag) | Limited — may need new art |

**Assessment:** Earth, Fire, and Water sections well-served. Air section may need
creative use of existing shapes or new cloud/wind tiles.

### Cloud Cliffs

**Art notes:** Vertical climb, bones of dead Zealans

| Need | Reusable Shapes | Notes |
|------|-----------------|-------|
| Cliff faces | Shapes 26–32 (directional walls, z-height 6) | Core climbing surfaces |
| Narrow paths | Ground shapes with small footpads | Existing narrow terrain |
| Bones/remains | Decoration shapes | Human remains shapes exist |
| Heights | Z-axis variation (-128 to +127) | Engine supports full range |

**Assessment:** Fully achievable. Cliff shapes with high z-footpads provide
the vertical feel.

### Cloud City

**Art notes:** "Bob's red stone architecture turned white and gold," cloud-like
terrain, collapsing ground, Avatar dying in cloud terrain

| Need | Reusable Shapes | Notes |
|------|-----------------|-------|
| Stone architecture | Shapes from walls/cliffs (89 shapes) | Recolor white/gold |
| Cloud terrain | **NEW ART NEEDED** | No cloud ground tiles exist |
| Collapsing ground | Existing ground + DMG shapes | Gameplay: ground disappears |
| Building interiors | Shapes from base game buildings | Extensive options |
| Floating platforms | Existing platform/ground shapes | Placed at high z |

**Assessment:** Partial reuse. Stone architecture shapes can be recolored.
Cloud terrain is the main gap — needs new shapes or creative use of existing
translucent/sea shapes.

### Ancient Temple / Shrine

**Art notes:** Gods encased in resin "like Dune shields," altar, Tiny Tar entry

| Need | Reusable Shapes | Notes |
|------|-----------------|-------|
| Temple walls | Stone wall shapes | Dungeon/cave tileset |
| Altar | Decoration shapes | Several large prop shapes exist |
| Shrine interior | Base game interior assets | Good coverage |
| God statues | **NEW ART NEEDED** | Encased god figures |
| Tiny entry | Standard door shapes with special trigger | Gameplay mechanic |

**Assessment:** Structure reusable, but god statue figures need new art.

---

## 2. Item Assets

### Quest-Critical Items — Shape Mapping

| Item | Existing Shape? | Strategy |
|------|----------------|----------|
| Key to Double Doors | Yes — SF_QUALITY shapes (60 types) | Use existing key shape |
| Galjeron's Journal | Yes — book/scroll shapes exist | Reuse TypeBook shape |
| Talisman of Fire | Partial — gem/crystal shapes exist | May need unique art |
| Talisman of Earth | Same as above | May need unique art |
| Talisman of Water | Same as above | May need unique art |
| Talisman of Air | Same as above | May need unique art |
| Passage Stone | Yes — stone/rock shapes | Reuse decorative stone |
| Key to the Clouds | Yes — TypeKey shape | Reuse existing key |
| Shield halves | **NEW ART NEEDED** | TypeAOFrizbee / TypeZealanShield |
| Shield restored | **NEW ART NEEDED** | TypeAOFrizbee whole |
| Message Scroll | Yes — scroll/book shapes | Reuse existing |
| Tiny Tar Potion | Yes — bottle/potion shapes | TypeBottle shape |
| Special Root | Yes — plant/reagent shapes | Reuse existing |
| Bag of Reagents | Partial — TypeBag shape exists | TypeBagOReagents — may need unique gump |
| Magnetic Obelisk | Partial — large stone shapes | TypeMagnet — may need unique art |

### Usecode Type References → Base Game Shapes

Many Type* references in LV usecode map to existing base game shapes:

| LV Type Reference | Base Game Shape | Notes |
|-------------------|----------------|-------|
| TypeKey | Shape with SF_QUALITY family | Standard key model |
| TypeDoorEW | Shape 68 (1,4,5 footpad) | East-west door |
| TypeDoorNS | Shape 69 (4,1,5 footpad) | North-south door |
| TypeBook | Existing book shape | Reusable |
| TypeBottle | Existing bottle shape | For potions |
| TypeBag | Existing bag container | SF_CONTAINER family |
| TypeBackPack | Existing backpack | SF_CONTAINER family |
| TypeBarrel | Existing barrel shape | SF_CONTAINER family |
| TypeFood | Existing food shapes | Reusable |
| TypeArmour | Existing armour shapes (12) | Reusable |
| TypeHelmets | Existing helmet shape | equip=3 (SE_HEAD) |
| TypeLeggings | Existing legging shape | equip=5 (SE_LEGS) |
| TypeArmGuards | Existing arm guard shape | equip=2 (SE_ARM) |

---

## 3. Creature/NPC Assets

### Required Creatures

| Creature | Art List Notes | Reusable? |
|----------|---------------|-----------|
| Water Zombie | "Import Dicko's art" | **NEW ART** — Art List says to import external art |
| Harpie | Listed in Art List | **NEW ART** — No base game equivalent |
| Multi-Elemental Agent | Synopsis suggestion | **NEW ART** — Could use existing monster shapes as placeholder |
| Guardian (Galjeron's chamber) | Synopsis: creature killed Galjeron | Can reuse existing monster shapes |
| Shades (Flossie & Snori) | "2 days work" in Art List | **NEW ART** — Ghost/apparition effect |

### Reusable NPC Elements

| NPC Type | Base Game Shapes | Notes |
|----------|-----------------|-------|
| Zealan villagers | Existing peasant/villager shapes | Reclothable via frame changes |
| Ezrekal | Existing NPC shape | Unique dialogue, standard model |
| Clan elders | Existing NPC shapes | Different frames for appearance |

**Assessment:** NPCs can largely reuse existing human shapes with different frames.
Creatures (Water Zombie, Harpie) are the main new art requirements.

---

## 4. Environmental Mechanics

### Eggs and Triggers (No New Art Needed)

| Mechanism | Implementation | Shape |
|-----------|---------------|-------|
| Double doors unlock | Teleport egg + key quality check | Shape 508 |
| Map transitions | Teleport egg pairs | Shape 508 |
| Monster spawns | Monster eggs | Shape 500 |
| Passage Test trigger | Standard egg + PLNTST usecode | Shape 73 |
| Elemental pillar interaction | Quality items + usecode | SF_QUALITY shapes |
| Collapsing cloud ground | Damaging shapes + trigger | Shapes 435–438 + egg |

### Existing Puzzle Shapes

| Mechanism | Available Assets |
|-----------|-----------------|
| Candlestick rack (CANTRK) | Candle/torch shapes in decorations |
| Door locks/keys | Full SF_QUALITY system with 60 shapes |
| Container puzzles | 73 container shapes with lock quality |

---

## 5. Summary: New Art Requirements

### Must-Have (blocking map creation)

1. **Shield of the Ancients** — half (x2) and whole variants (3 shapes)
2. **Zealan gods encased in resin** — 3 god figures (3 shapes + speaking variants)

### Should-Have (significant gameplay)

3. **Water Zombie** — Art List says "import Dicko's art" (1 shape + animation)
4. **Harpie** — new monster for Cloud Cliffs (1 shape + animation)
5. **Elemental talismans** — 4 distinct gem/token shapes (could be frames of one shape)
6. **Shades apparition** — ghost effect for Flossie & Snori (1 shape)

### Nice-to-Have (polish)

7. **Cloud terrain tiles** — for Cloud City distinctive look (2-4 shapes)
8. **Magnetic Obelisk** — distinctive prop for Cloud City puzzle (1 shape)
9. **Passage Test plant** — "nasty plant with delectable fruit" (1 shape)
10. **Bottomless Bag gump** — UI element for Bag of Reagents (gump graphic)

### Can Skip (reuse existing)

- All terrain for Lost Vale overworld, Elemental Dungeon, Cliffs, Temple
- All doors, keys, containers, books, scrolls, potions
- All NPC base models
- All map transition eggs
- All standard UI elements

---

## 6. Glob Creation Strategy

For creating new map terrain, we can:

1. **Reuse existing globs:** 2,129 terrain patterns available. Many are general
   rocky ground suitable for the "barren valley" aesthetic.

2. **Create minimal new globs** for areas needing distinctive terrain:
   - Cloud City platforms (if cloud tile shapes are created)
   - Elemental dungeon section-specific floor patterns
   - Ancient Temple interior floor

3. **Available glob slots:** 943 empty entries in GLOB.FLX (indices 0–3071)

4. **Recommended approach:** Start with existing globs, identify gaps during
   map layout design, create new globs only when existing ones don't fit.

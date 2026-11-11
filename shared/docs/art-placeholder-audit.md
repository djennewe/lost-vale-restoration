# Art Placeholder Audit — The Lost Vale (SUPERSEDED, 2026-07-01 pass)

> **SUPERSEDED — read the newer audit first.**
> The authoritative placeholder audit is
> `agents/map-populator/docs/art-placeholder-audit-2026-07-19.md`. This
> 2026-07-01 pass is kept for two reasons: its **1500-1700 new-shape id
> allocation still stands** and is not restated in the newer document, and
> several call-outs here (shape 158 is a stool, 338 a green sparkle VFX, 400 a
> fire VFX, 205 a desk) are cited by the TYPE_SHAPES audit note in
> `u8c_symbols.py` and remain correct.
>
> Where the two disagree on what a placeholder should become, or on priority,
> the 2026-07-19 document wins. Several items here were fixed after this pass
> (the SI_FIXED trap sweep, the Shield 580→539 correction, the Map 17/18
> shape-400 swaps), so treat any "current shape" value below as a snapshot of
> 2026-07-01, not of the build.

All new LV concepts currently use base game placeholder shapes. This audit
catalogs every placeholder, its current shape, what it should look like, and
priority for replacement.

## Summary

| Priority | Count | Items |
|----------|-------|-------|
| BLOCKING | 8 | Shades, Water Zombie, Harpie, Shield (2 forms), 3 Gods |
| HIGH | 3 | Zealan NPCs, Elemental Columns, Magnetic Obelisk |
| MEDIUM | 6 | Lord British, Passage Stone, Gold Plaques, Cloud Terrain, Zealan Child, Monster Skull |
| LOW | 5 | Abacus, Bedroll, EA Logo, Special Root, Vision Whirlwind |

## BLOCKING — Will look wrong or break gameplay

### 1. Shades (Hoskuld & Gunnar ghosts)
- **Current:** Shape 73 (egg/marker — invisible in-game!)
- **Should be:** Translucent ghost/spirit figures
- **Where:** Map 10 Sacred Circle ceremony (`build_map_10.py:674`), `SHADES.UNK`
- **Why blocking:** Egg shape is invisible. Ceremony scene depends on visible spirits speaking dialogue.

### 2. Water Zombie
- **Current:** Shape 400 (generic human NPC)
- **Should be:** Aquatic undead creature ("Import Dicko's art" per Art List v2.5)
- **Where:** Map 10 lake, 5 monster eggs (`build_map_10.py:608-614`)
- **Why blocking:** Indistinguishable from Zealan villagers.

### 3. Harpie
- **Current:** Shape 400 (generic human NPC)
- **Should be:** Flying predator with wings, distinctive silhouette
- **Where:** Map 13 Cloud Cliffs, 3-4 monster eggs at z=80-112 (`build_map_13.py`)
- **Why blocking:** Signature creature for the cliffs sequence. Must be visually distinct.

### 4–5. Shield of the Ancients (TypeAOFrizbee / TypeAOArtifact)
- **Current:** Shape 580 (generic talisman/gem) for both halves and whole
- **Should be:** 3 shapes — left half, right half, restored whole shield
- **Where:** Map 17 memorial hall halves (`build_map_17.py:399,410`), Map 18 altar ceremony
- **Why blocking:** Central quest item. Talisman gem looks nothing like a shield. Players can't recognize it.

### 6–8. Three Zealan Gods (Felicitar, Doloras, Timyra)
- **Current:** Shape 400 (generic human NPC) with quality IDs 301-303
- **Should be:** Distinctive divine figures, each visually unique; "encased in resin" variant + "freed/speaking" variant = 6 shapes minimum
- **Where:** Map 18 Inner Sanctum (`build_map_18.py:283-311`), `FREE.UNK`, `AOSCENE.UNK`
- **Why blocking:** End-game climax. Gods identical to villagers ruins the ceremony. Art List describes them as "like the shields in the movie Dune."

## HIGH — Noticeable gameplay impact

### 9. Zealan NPCs (16 total)
- **Current:** Shape 400 frames 0-7 for all villagers
- **Should be:** Zealan-specific human figures with cultural dress (Norse-inspired)
- **Where:** Map 10 — 7 Clan Hoskuld, 9 Clan Gunnar, 1 Ezrekal (`build_map_10.py:232-490`)
- **Impact:** Dialogue emphasizes cultural identity. All NPCs look like base game Pagans.

### 10. Elemental Columns (4 variants)
- **Current:** Shape 721 (generic stone pillar) for all four
- **Should be:** 4 distinct pillars — Earth (brown/stone), Fire (red/flame), Water (blue/liquid), Air (white/translucent)
- **Where:** Map 11 Elemental Dungeon, `COLPUZZL.UNK` puzzle script
- **Impact:** Puzzle requires knowing which element each pillar represents.

### 11. Magnetic Obelisk
- **Current:** Shape 721 (generic stone pillar)
- **Should be:** Tall exotic obelisk with metallic/magnetic visual
- **Where:** Map 17 Cloud City main plaza (`build_map_17.py:168`), `MAGNET.UNK`
- **Impact:** Puzzle centerpiece. Players need to identify it as the source of equipment sealing.

## MEDIUM — Atmospheric / recognition impact

### 12. Lord British (Vision NPC)
- **Current:** Shape 400 (generic NPC)
- **Should be:** Royal figure distinct from Zealan NPCs
- **Where:** Intro sequence, `LORDBRIT.UNK`

### 13. Passage Stone
- **Current:** Shape 580 (generic talisman)
- **Should be:** Stone token with Zealan iconography
- **Where:** Map 10 lake island (`build_map_10.py:598`)

### 14. Gold Plaques (TypeNSGoldPlaque)
- **Current:** Shape 158 (book)
- **Should be:** Wall-mounted gold inscription plaque
- **Where:** Map 17 Cloud City halls (`build_map_17.py:251,363`), `PLAQUENS.UNK`

### 15. Cloud Terrain
- **Current:** Existing base game globs (creative reuse of translucent/stone shapes)
- **Should be:** Distinctive cloud-like ground tiles
- **Where:** Map 17 Cloud City throughout (`build_map_17.py` glob 78)

### 16. Zealan Child (TypeZealanChild1)
- **Current:** Shape 400 (adult NPC)
- **Should be:** Child-sized figure
- **Where:** Map 10, `ZCHILD.UNK`

### 17. Monster Skull (TypeMonskul)
- **Current:** Shape 189 — **wrong category, not bones.** Rendering (2026-07-01 audit)
  shows shape 189 is a full robed humanoid NPC sprite (322 animation frames), not a
  bone decoration. The correct base-game bone/skeleton pile props are shapes 235 and
  237 (2 frames each).
- **Should be:** Ornate skull with magical glow; if no custom art is made, shape 235
  or 237 is a far closer stand-in than 189.
- **Priority raised from LOW to MEDIUM:** the previous "thematically acceptable"
  assessment was wrong — an NPC sprite standing in for a skull prop is a visible
  category mismatch, not a cosmetic near-miss.

## LOW — Cosmetic / minor props

### 18. Abacus (TypeAbacus)
- **Current:** Shape 158 (book) — completely wrong
- **Should be:** Counting frame/abacus prop

### 19. Bedroll (TypeBedroll)
- **Current:** Shape 225 (backpack)
- **Should be:** Rolled sleeping mat

### 20. EA Logo (TypeEaLogo)
- **Current:** Shape 158 (book). Source file doesn't compile (truncated).
- **Likely cut content.** Lowest priority.

### 21. Special Root (TypeWeedz)
- **Current:** Shape 399 — engine name "eye of newt" (a snake-skin/root sprite).
- **Should be:** A distinctive nightmare-elixir root prop.
- **Where:** Map 10 Sacred Circle (`build_map_10.py` special-root placement, frame 9),
  quest steps 9-10 poison-cure arc (`EZREKAL.UNK` hint, `TYORVI.UNK`).
- **Note:** No better existing shape; "eye of newt" reads as a plausible root
  stand-in, so it is intentionally kept. Confirmed still-a-placeholder 2026-07-05.

### 22. Vision Whirlwind (Passage Test VFX)
- **Current:** Shape 400 — a fire/explosion VFX placeholder (same shape reused for
  several NPC placeholders elsewhere; see items 12/16 etc.).
- **Should be:** A swirling wind/vortex effect for the vision-quest scene.
- **Where:** Map 10 Passage Test vision (spawned by `PLNTST.UNK`; the five
  whirlwind+plant pop pairs referenced in `build_map_10.py` build_test_grounds).
- **Note:** No better existing shape; intentionally kept. Confirmed still-a-
  placeholder 2026-07-05.

## Shape ID Allocation Plan

If new shapes are created, they should use IDs in the range 1500-1700 (well above
base game's used range of 0-1100, below the 2048 max). TYPEFLAG.DAT will need 8-byte
entries for each new shape.

| New Shape | Proposed ID | TYPEFLAG Flags |
|-----------|-------------|----------------|
| Water Zombie | 1500 | SI_FIXED, monster family |
| Harpie | 1501 | SI_FIXED, monster family |
| Shield Half Left | 1510 | SF_QUALITY |
| Shield Half Right | 1511 | SF_QUALITY |
| Shield Whole | 1512 | SF_QUALITY |
| God Felicitar (encased) | 1520 | SI_FIXED |
| God Felicitar (freed) | 1521 | SI_FIXED |
| God Doloras (encased) | 1522 | SI_FIXED |
| God Doloras (freed) | 1523 | SI_FIXED |
| God Timyra (encased) | 1524 | SI_FIXED |
| God Timyra (freed) | 1525 | SI_FIXED |
| Shade ghost | 1530 | SI_FIXED, SI_TRANSL |
| Earth Column | 1540 | SI_FIXED, SI_SOLID |
| Fire Column | 1541 | SI_FIXED, SI_SOLID |
| Water Column | 1542 | SI_FIXED, SI_SOLID |
| Air Column | 1543 | SI_FIXED, SI_SOLID |
| Magnetic Obelisk | 1550 | SI_FIXED, SI_SOLID |
| Zealan Adult M | 1560 | NPC family |
| Zealan Adult F | 1561 | NPC family |
| Zealan Child | 1562 | NPC family |
| Cloud terrain tile | 1570 | SI_FIXED, SI_SOLID, SI_LAND |
| Gold Plaque | 1580 | SI_FIXED |

When shapes are created, update `TYPE_SHAPES` in `u8c_symbols.py` and the
corresponding `SHAPE_*` constants in the map builder scripts, then rebuild both
EUSECODE.FLX and FIXED.DAT.

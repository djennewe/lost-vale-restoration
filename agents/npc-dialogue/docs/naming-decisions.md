# Naming Decisions — Resolved Placeholder Names

All placeholder names from the design documents, with canonical replacements
derived from usecode evidence and base-game lore.

---

## Resolved Names

### 1. "Shrine of the Wheaties" → **Shrine of the Ancient Ones**

| Source | Name Used |
|--------|-----------|
| Plot v1.2 | `"Shrine of the Wheaties"` (placeholder) |
| Plot v1.2 | `"shrine of Kumash Ghor"` (another placeholder?) |
| Walk Through | `"Shrine"` |
| Usecode flags | `templeOpen`, `ezToTemple`, `spokeTemple` |
| Coordinator DD-002 | `"Ancient Temple"` / `"Shrine of the Ancient Ones"` |

**Decision:** "Shrine of the Ancient Ones" — with "Ancient Temple" as the
outer structure and the Shrine as the inner sanctum where the gods are
imprisoned. The usecode consistently uses "temple" in flag names.

**Rationale:** "Wheaties" is obviously a placeholder (cereal brand humor).
"Kumash Ghor" appears once and was likely another working name. The base game
refers to the Zealan gods as "Ancient Ones," so "Shrine of the Ancient Ones"
is the natural canonical form.

---

### 2. "Sacred Smallish Unusual-Colored Rock" → **Sacred Circle**

| Source | Name Used |
|--------|-----------|
| Plot v1.2 | `"Sacred Smallish Unusual-Colored Rock"` (placeholder) |
| Usecode (Ezrekal ask) | `"Where is the Sacred Circle?"` |
| Usecode (SHADES.UNK) | Specific coordinates for the ceremony location |

**Decision:** "Sacred Circle" — this is the name used in the actual usecode
dialogue. Ezrekal has an ask option referencing it by this name.

**Rationale:** The placeholder was humorously long and nonsensical. The usecode
proves the team settled on "Sacred Circle" as the final name. The location is
where the Shield Restoration Ceremony (SHADES) takes place.

---

### 3. "Test of Rutabaga" → **Rite of Passage**

| Source | Name Used |
|--------|-----------|
| Plot v1.2 | `"Test of Rutabaga"` (placeholder) |
| Walk Through | `"Test"` |
| Usecode (Atli) | `"Called the Rite of Passage it is."` |
| Usecode symbol | `PLNTST` (Passage Test) |
| Usecode flags | `completedTest`, `zealanMark` |

**Decision:** "Rite of Passage" — the name Atli uses in dialogue. The usecode
file is named PLNTST (Passage Test / Plant Test), confirming the plant-based
test mechanism.

**Rationale:** "Rutabaga" is a vegetable placeholder. Atli explicitly names
the test in his dialogue. "Rite of Passage" is more appropriate for a
coming-of-age ritual.

---

### 4. "Love, Hate, Apathy" → **Felicitar, Doloras, Timyra**

| Source | Name Used |
|--------|-----------|
| Plot v1.2 | Love, Hate, Apathy (working names) |
| Base game U8 lore | Felicitar, Doloras, Timyra |
| Monster Skull message | Felicitas, Timyra (plus Odion, Apathas, Amoras) |

**Decision:** Use base-game canonical names: **Felicitar**, **Doloras**,
**Timyra**. The design doc names were working placeholders for the emotions
each god represents.

**Note (counts verified 2026-07-26):** both spellings are real, and the split
is not wiki-versus-source as previously assumed.

- The **shipped base game** says `Felicitar`: EUSECODE.FLX carries "Felicitar
  controlled joy, Doloras ruled grief, and Timyra was the patron of fear", and
  contains `Felicitas` nowhere.
- The **recovered LV drafts use both**: `Felicitas` appears in MONSKUL.UNK and
  twice in EZREKAL.UNK, while `Felicitar` also appears in EZREKAL.UNK. The
  1994 team was inconsistent with itself inside a single file.

Use **Felicitar** for anything we write, because it is what the shipped game
says and it is the spelling a player can actually encounter. Leave the
recovered source alone: it is read-only evidence, and its inconsistency is
itself a fact about the snapshot.

---

### 5. "Magic Frisbee" → **Shield of the Ancients**

| Source | Name Used |
|--------|-----------|
| Plot v1.1 | `"Magic Frisbee"` |
| Walk Through | `"Magic Frisbee"` (still used) |
| Plot v1.2 | `"Shield of the Ancients"` |
| Usecode class | `TypeAOFrizbee` (internal name preserves "Frisbee" joke) |
| Usecode look bark | `"Ceremonial Shield of the Ancients Ones"` |
| Dev comment | `"Named by Mel, thank you"` |

**Decision:** "Shield of the Ancients" — already resolved in Plot v1.2.
The internal class name `TypeAOFrizbee` is a developer joke that was never
player-facing. The look bark uses "Ceremonial Shield of the Ancient Ones"
(note: "Ancients Ones" in source is likely a typo for "Ancient Ones").

---

### 6. Two Boys — **Hoskuld and Gunnar**

| Source | Names Used |
|--------|-----------|
| Plot v1.1 | Draesh and Ikanikar |
| Plot v1.2 | Snori and Hoskuld |
| Art List v2.5 | Flossie and Snori |
| Usecode (SHADES) | Hoskuld and Gunnar |

**Decision:** **Hoskuld and Gunnar** — these are the names used in the
actual Shade dialogue, which is the final implemented version:

- `"The shade of Hoskuld, I am."`
- `"In life, Gunnar, was I named. And fast friend to Hoskuld, I was."`

The clans are named after these boys:
- Clan Hoskuld → descended from the boy Hoskuld's family
- Clan Gunnar → descended from the boy Gunnar's family

**Evolution:** Draesh/Ikanikar (v1.1) → Snori/Hoskuld (v1.2) → Hoskuld/Gunnar
(final usecode). The name "Flossie" from the Art List may have been a temporary
nickname or was replaced during development. The Character List's reference to
"Flossie's family" (for the Female Elder/Thordis) predates the final usecode
naming.

---

### 7. "Cliffs of Insanity" → **Cloud Cliffs**

| Source | Name Used |
|--------|-----------|
| Plot v1.2 | `"Cliffs of Insanity"` |
| Usecode flags | `climbedCliffs`, `attemptedCliffs`, `agreeToClimb` |
| Discord analysis | `"Cloud Cliffs"` |

**Decision:** Both names are valid. "Cloud Cliffs" is the functional name
from usecode context. "Cliffs of Insanity" is the narrative name from the
design docs (possibly a *Princess Bride* reference). Use "Cloud Cliffs" as
the primary name in game text; "Cliffs of Insanity" can be used by NPCs
informally.

---

### 8. Additional Six Ancient Ones

From the Monster Skull message, six Ancient Ones are named:

| Name | Source | Role |
|------|--------|------|
| **Felicitas** | Monster Skull | God of Joy/Love (= Felicitar in wiki) |
| **Timyra** | Monster Skull, base game | God of Fear/Emotion |
| **Doloras** | Base game wiki (unnamed in skull) | God of Sorrow — author of the skull message |
| **Odion** | Monster Skull | Brother god (not in base game) |
| **Apathas** | Monster Skull | Brother god (not in base game) |
| **Amoras** | Monster Skull, Ezrekal's stories | Sister god, associated with love/flight |

The skull message says: `"To my brothers, Odion and Apathas, and my sister,
Amoras... Felicitas, Timyra and I will go now to the Temple..."` The unnamed
author who stays with Felicitas and Timyra is **Doloras** (by elimination).

---

## Summary Table

| Placeholder | Canonical Name | Source |
|-------------|---------------|--------|
| Shrine of the Wheaties | Shrine of the Ancient Ones | DD-002 + usecode |
| Sacred Smallish Unusual-Colored Rock | Sacred Circle | Usecode (Ezrekal ask) |
| Test of Rutabaga | Rite of Passage | Usecode (Atli dialogue) |
| Love, Hate, Apathy | Felicitar, Doloras, Timyra | Base game lore |
| Magic Frisbee | Shield of the Ancients | Plot v1.2 |
| Draesh/Ikanikar, Snori/Hoskuld | Hoskuld and Gunnar | Usecode (SHADES) |
| Cliffs of Insanity | Cloud Cliffs | Usecode flags |

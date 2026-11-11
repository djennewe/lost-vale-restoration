# Design Decisions — Resolved Ambiguities

---

## DD-NPC-01: Romeo & Juliet Subplot — CUT

**Question:** Walk Through beat XIII mentions `"a young couple, one from each
side of the feud, who are in love"` who help reunite the factions. Should this
be included?

**Decision: CUT.** Do not include the Romeo & Juliet subplot.

**Evidence:**

1. **Plot v1.2 does not mention it.** The Shield Restoration Ceremony (beat 16)
   involves Ezrekal, the two clan leaders (Atli and Thordis), and the Avatar.
   No lovers are referenced.

2. **Usecode has no evidence.** The SHADES.UNK ceremony scene includes only
   Ezrekal, Atli, Thordis, the Avatar, and the two Shades (Hoskuld and Gunnar).
   No additional NPCs are teleported or referenced.

3. **No usecode flags exist** for a romantic subplot. No flags like
   `loversReunited`, `metLover`, or similar appear in FLAGS.UNK or ZZVFLAGS.UNK.

4. **Character List 1.0 has no lovers.** The ~12 character archetypes include
   a married couple (Hunter + Farmer) but they're in the SAME clan (Hoskuld),
   not cross-clan lovers.

5. **The Female Child of Elder (Gunnar)** — `"Mother died climbing the cliffs.
   Never far from daddy"` — is the only candidate for a young female character
   in Clan Gunnar, and she was **struck through** (cut) in the Character List.

**Conclusion:** The subplot was a Walk Through suggestion that was never
developed. The existing reconciliation mechanism (Shield ceremony + Shade
revelation) is complete and satisfying without it. Adding unimplemented content
would risk contradicting the usecode evidence.

**Note:** The Walk Through is a less authoritative source than Plot v1.2 and
the usecode. It contains suggestions and annotations ("Build obstacles!",
"Cool Scenes") rather than final designs.

---

## DD-NPC-02: Bag of Reagents Timing — LATE (Quest Reward)

**Question:** Is the Bag of Reagents given early by Mythran (Synopsis beat 2)
or late as a quest reward (Plot v1.2 beat 19)?

**Decision: LATE.** The Bag of Reagents is given by Ezrekal after the gods
are freed, as a reward for completing the expansion's main quest.

**Evidence:**

1. **Usecode confirms late delivery.** Ezrekal's dialogue (EZREKAL.UNK)
   includes the line:
   ```
   "What a wonderful time this is! Once again be able to fulfill my duties as
   High Priestess I will! Nothing there is I can give you to repay you for your
   trouble, but this I can give you there is. A magical bag it is."
   ```
   This line is gated behind `godsFree = true` or `templeOpen = true`.

2. **Plot v1.2 beat 19** places the Bag as a resolution reward:
   `"The Avatar receives the Bag of Reagents (eliminates reagent hunting for
   remainder of base game)."`

3. **Usecode flags confirm late state:** `hasBag` is only checked in
   Ezrekal's late-game dialogue branches, alongside `godsFree` and
   `templeOpen`. It never appears in early-game dialogue.

4. **The Synopsis suggestion** (`"Mythran give 'bag of endless reagents' here"`)
   was a design note, not an implemented decision. It conflicts with the
   usecode evidence.

5. **Narrative logic:** The Bag as a quest reward provides motivation to
   complete the expansion. Giving it early would reduce the player's incentive
   to continue. It also makes more thematic sense as a gift from the Zealans
   (whose gods are connected to the elements/reagents) rather than from Mythran
   (who already sells reagents for profit).

**Implementation:** The `TypeBagOReagents` class should be spawned by Ezrekal
during her post-`godsFree` dialogue branch. The `hasBag` and
`haveReagentsDone` flags track its state.

---

## DD-NPC-03: Titan Agent Subplot — NOT INCLUDED

**Question:** Synopsis Note 1 proposes a Titan agent NPC who lives apart from
both factions and tries to prevent reunification. Should this be included?

**Decision: NOT INCLUDED** in dialogue. This is a map-builder / gameplay
design decision, not a dialogue question. No usecode evidence supports this
NPC existing.

**Note for map-builder agent:** If the Titan agent is implemented as a
combat encounter, the npc-dialogue agent can write his dialogue upon request.

---

## DD-NPC-04: Six Ancient Ones — Three Free, Three Absent

**Question:** The Monster Skull message names six Ancient Ones. Only three
(Felicitas/Felicitar, Timyra, and Doloras) are freed in the game. What
happened to the other three (Odion, Apathas, Amoras)?

**Decision:** The skull message says `"Felicitas, Timyra and I will go now
to the Temple and attempt to hold them off until you arrive."` The three
who went to the Temple (Felicitas, Timyra, Doloras) were captured and
encased in amber. The three who were away (Odion, Apathas, Amoras) escaped
capture but are missing — their fate is unknown.

This is consistent with the design docs, which only mention three gods being
freed: `"Love, Hate, and Apathy"` (Plot v1.2) / `"three gods"` (Walk Through).

The missing three gods can be referenced in dialogue as a mystery but should
NOT be resolved — this is an open thread, possibly intended for future content.

---

## DD-NPC-05: "Flossie" Identity

**Question:** The Art List references `"Shades (Flossie & Snori)"` and the
Character List says the Female Elder is `"Descendant of Flossie's family."`
Who is Flossie?

**Decision:** "Flossie" is an earlier development name for one of the two
boys (either Hoskuld or Gunnar). In the final usecode, the Shade dialogue
uses only "Hoskuld" and "Gunnar." Since the Female Elder (Thordis) leads
Clan Hoskuld, and she's described as `"Descendant of Flossie's family"`,
Flossie likely = Hoskuld (the boy whose family became Clan Hoskuld).

This is not gameplay-relevant since "Flossie" never appears in the final
dialogue. The name was replaced during development.

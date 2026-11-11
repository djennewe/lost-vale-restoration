# End-Game — Restoration Sequence

Missing dialogue segment #6. No writer assigned; never written.
Plot beat 18: "water flows, green plants, PC gets his bag, blood feud ended."

---

## Context

After the gods are freed (AO Scene), the Vale begins to heal. This is the
resolution sequence — a series of environmental and NPC reactions showing
the world transformed by the restoration of the Ancient Ones.

No usecode exists for this sequence. This document provides the full
dialogue script for the end-game events.

---

## Scene Flow

### 1. Immediate Aftermath — The Vale Transforms

*As the Avatar exits the Ancient Temple, the sky brightens. Water begins
to flow from springs that had been dry. Green shoots appear in the barren
soil. The environmental mood shifts from desolation to renewal.*

**Environmental barks (sequential, timed):**
```
"Water... it is flowing again!"
"The ground... it's changing. Green shoots are pushing through!"
"The air feels different. Cleaner. Warmer."
```

---

### 2. Clan Reactions — Hoskuld Village

The Avatar passes through Clan Hoskuld territory.

**Thordis:**
```
"Look! Look upon this! Green, the fields are turning! Water from
the spring, flowing it is! Dreamed of this I have, but believe
it I dared not.

What done you have, stranger... no. Friend. What done you have,
friend, repay it we never can. Saved us all you have. Saved the
Vale."
```

**Tyorvi (sober):**
```
"See this do you? Water. Real water, not from a jug. Running
through the valley it is, like in the old stories. And the
dreams... gone, they are. Truly gone.

Owe you everything I do. Everything. A new man, I am. Drink
again I will not. Sworn it I have."
```

**Ragnar:**
```
"Smell that? The air. Different it is. Fresher. And look —
tracks in the mud. New tracks! Return the game will, I think.
The Vale lives again.

A great hunter you are, Avatar. The greatest hunt of all,
completed you have."
```

**Sigrid (Hunter):**
```
"Growing! The plants are growing! My husband — beside himself
he will be! And my boy — run through green fields he will,
as in grandfather's stories!

Thank you. Simple words they are, but mean them with all my
heart I do."
```

**Zealan Child:**
```
"Look! Look! Water! Real water! And green things! What called
are green things? Mama says 'plants' they are. Pretty, they
are! Can eat them we?"
```

---

### 3. Clan Reactions — Gunnar Village

**Atli:**
```
"Astounding. Never in my lifetime expected to see this I did.
Flowing, the springs are. Greening, the soil is.

Wrong I was. About the Hoskulds. About Ezrekal. About
everything. Stubborn old fool I am. But perhaps... not too
old to learn.

Welcome here always you are, Avatar. A Zealan in spirit, you
are. The best of us."
```

**Hrodny:**
```
"The water! Flowing again it is! Do you know what this means?
My irrigation channels — work now they will! Feed everyone I
can! No more rationing, no more hunger!

Told them I did! Told them my inventions would save us! Well...
perhaps the gods helped too. A little."
```

**Ingyald:**
```
"Water for brewing! Real, clean water! Not that brackish swill
from the bottom of the well. A proper batch, make I will!

Celebrate this we must. The greatest day in the history of the
Vale, this is. Drinks on me!"
```

---

### 4. Ezrekal — Final Conversation

**Ezrekal (at her dwelling, after the restoration):**

```
"Avatar. Felt the change I have, deep in my bones. Flowing again
the power of the Ancient Ones is. Through me, to the people,
speak they can once more. High Priestess I am again, truly.

What done you have... no words sufficient there are. From
outside our world you came, a stranger to our ways. Mocked you
the people did, and poisoned you were. Yet persevered you did.
Climbed the cliffs you did. Faced the harpies you did. Reunited
the clans you did. And freed our gods you did.

A debt to you, all of the Vale owes. For as long as remembered
the Zealans are, remembered you will be."
```

**Ask option:** `"What will happen now?"`

**Ezrekal:**
```
"Heal, the Vale will. Slowly at first, but heal it will. Green
the fields will become again. Flow the rivers will. Return the
game will. And united, the people will stay.

Through the Shield, speak to the people the Ancient Ones will,
as in the days of old. Guide them, counsel them, love them.
Never again abandoned, the Zealans will feel.

And I... fulfill my purpose at last, I shall. The High Priestess
I was born to be, the High Priestess I shall be. Until the end
of my days."
```

**Ask option:** `"Thank you, Ezrekal."`

**Ezrekal:**
```
"Thank me? Thank you, I should! Without you, in that amber
prison forever the Ancient Ones would have remained. And in my
exile, forever I would have stayed.

Given me back my life, you have. Given us all back our lives.

Go well, Avatar. And if ever need our help you do, know that a
home in the Vale you have. Always."
```

**Ask option:** `"I must return to Pagan now."`

**Ezrekal:**
```
"Yes. A great task ahead of you there is, I know. The Titans
still rule your world above. But remember what learned here you
have: that faith and unity can overcome even the darkest power.

Take the Shield with you if you wish. The Defender, strong it
is, and protect you it will. Crafted by the Ancient Ones
themselves, it was.

Farewell, Avatar. Forget you, the Zealans never will."
```

> **Note:** The "Defender" is the Shield of the Ancients in frame 3
> (`TypeAOFrizbee`). The look bark says `"Defender"`. According to the
> Synopsis, it "maxes out the PC's armor rating."

---

### 5. Return to Mythran (optional late-game)

Already handled in `dialogue-mythran.md`:
- `"I freed the Zealan gods."` → Mythran's astonished reaction

---

## Bag of Reagents — Implementation Note

The `TypeBagOReagents` is spawned by Ezrekal during the AO Scene
(see `dialogue-ao-scene.md`). Her bark about the magical bag is already
in the usecode:

```
"Nothing there is I can give you to repay you for your trouble,
but this I can give you there is. A magical bag it is."
```

### Bag Look Bark
```
"Bag of Reagents"
```

### Bag Use Bark
```
"This magical bag will provide whatever reagents I need for my
spells."
```

Sets `hasBag = true`, `haveReagentsDone = true`.

---

## Design Notes

1. **Every surviving NPC gets a reaction.** This is the payoff for the
   entire expansion — seeing each character respond to the restoration.
   Each reaction reflects their personality established in the dialogue
   inventory.

2. **Character consistency:**
   - Thordis: shifts from despair to gratitude
   - Tyorvi: vows sobriety — his arc is complete
   - Ragnar: thinks about hunting (practical)
   - Sigrid: thinks about her family and green fields
   - Atli: admits he was wrong (the proudest character humbled)
   - Hrodny: excited her inventions will work (practical atheist)
   - Ingyald: celebrates with brew (opportunist to the end)
   - Ezrekal: full emotional catharsis — her life's purpose fulfilled

3. **The child's reaction** (`"What called are green things?"`) is the
   most affecting — a child who has never seen green plants.

4. **Ezrekal's farewell** is the longest NPC speech in the expansion.
   It recaps the Avatar's journey through the Vale as a heroic arc,
   providing narrative closure.

5. **The Defender shield** is offered as a practical reward alongside
   the Bag of Reagents. The Synopsis says it "maxes out the PC's armor
   rating" — a powerful item for the base game's remaining content.

6. **No U9 teaser dialogue** is included. The design docs mention the
   gods might hint at Britannia/U9, but this is too speculative. The
   gods' dialogue in the AO Scene already suggests the Avatar may
   "return to your Britannia."

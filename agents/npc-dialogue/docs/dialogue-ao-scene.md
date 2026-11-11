# AO Scene — God-Freeing Ceremony

Missing dialogue segment #5. Writer: Andrew (never completed).
The dramatic set piece at the Ancient Temple / Shrine of the Ancient Ones
where the Shield is placed on the altar and the three gods are freed.

---

## Context

After the Shield Restoration Ceremony (SHADES), the Avatar learns the gods
are imprisoned in the Ancient Temple (Shrine of the Ancient Ones). Hrodny
has Tiny Tar potions to enter the Temple. Inside, the Avatar places the
restored Shield on the altar and the three gods — Felicitar, Doloras, and
Timyra — are freed from their amber prison.

FREE.UNK has the trigger/flag logic but not the cinematic dialogue.

## Flags

```
globalflag templeOpen           // Avatar has accessed the Temple
globalflag godsFree             // gods have been freed
globalflag godsSpoke            // gods have spoken to the Avatar
globalflag getPowerAO           // Avatar receives power from the gods
globalflag ezToTemple           // Ezrekal has been told about the Temple
```

---

## Scene Structure

### 1. Approaching the Altar

The Avatar enters the inner shrine and sees three large figures encased
in amber-like resin (described in design docs as "looking like the shields
in the movie Dune").

**Avatar bark:**
```
"By the Virtues... they are here. The Ancient Ones — trapped in
amber. They look as if they have been here for ages."
```

**Look barks for encased gods:**
```
"Ancient One, encased in amber"    (all three, before freed)
```

### 2. Placing the Shield

When the Avatar uses the restored Shield (`TypeAOArtifact`, shape 828 at
quality 83 since 2026-10-08; it was `TypeAOFrizbee` frame 2) on the
altar:

**Avatar bark:**
```
"The Shield... it is glowing!"
```

*The Shield floats from the Avatar's hands and settles onto the altar.
Light pulses outward from it. The amber around the three figures begins
to crack. Camera shakes. SFX: crystalline shattering.*

**Environmental bark:**
```
"The amber is cracking!"
```

*The amber shatters. The three gods step forward, radiant with light.
Stasis is set. Cinematic mode.*

### 3. The Gods Speak

The gods speak in a MORE formal version of Elean Speak — they are the
source of the language (see `speech-patterns.md`).

**Felicitar** (god of Joy/Love):

```
"Free. Free at last, we are.

Long have we slumbered in this prison of amber, while above us
our children suffered and our Vale withered. Felt their pain, we
did, but act we could not.

Mortal, who are you that freed us has? Not a Zealan, you are.
Not a Pagan. Something... other."
```

**Ask option:** `"I am the Avatar, from Britannia."`

**Felicitar:**
```
"The Avatar. Heard of you, the whispers of the world have told
us. Even in our prison, hear the world we could. Sent to us
by our children, you were. And by the faith of our reunited
people, broken free we have been.

Grateful, beyond measure, we are."
```

**Doloras** (god of Sorrow):

```
"Long have I mourned. Mourned for our children who believed
abandoned them we had. Mourned for the Vale that once green
and beautiful was. Mourned for Odion, Apathas, and Amoras,
our siblings who to this place never came.

But now, a new sorrow replaces the old. The sorrow of time
lost. Of generations who lived and died believing forsaken
they were."
```

**Ask option:** `"Your people never lost faith — not entirely."`

**Doloras:**
```
"Speak you of Ezrekal? Yes. Felt her prayers we did, faint
through the amber. The only voice that reached us, hers was.
Sustained us, her faith did, when all else failed.

Remember her devotion, we shall. Always."
```

**Timyra** (god of Fear/Emotion):

```
"Afraid, you are. Yes, sense it I can. Fear not the fear, mortal.
Natural it is. To feel fear and act despite it — that is courage.
And courage in abundance, you have shown.

The Titans imprisoned us here when attacked the Great Council
they did. Sealed this shrine with their combined power, they did.
But broken that seal, the faith of our people has. And placed the
Shield upon the altar, you have."
```

### 4. The Avatar's Poison

**Felicitar:**
```
"But wounded, you are. Poisoned by the sacred plant. Sense it we
can. Hold still."
```

*Light flows from all three gods toward the Avatar. The poison
is purged. HP and stats fully restored.*

**Avatar bark:**
```
"I feel... whole again. The poison is gone!"
```

**Felicitar:**
```
"Healed, you are. Fully. The strength stolen from you, restored
it has been. A gift from us, this is, for what done you have."
```

### 5. The Gods' Wisdom

**Timyra:**
```
"Listen well, Avatar. The Titans who imprisoned us — the same
Titans who rule your world above. Powerful they are, but not
invincible. Weakened them, their long war against each other has.

If master their powers you can, then perhaps free this world
you may. Perhaps even return to your Britannia you could."
```

**Ask option:** `"How can I defeat the Titans?"`

**Doloras:**
```
"That answer, give you we cannot. Beyond our domain, the Titans
are. But this I will say: united they are not. Against each other
they scheme, as always they have. In their division, your
opportunity lies."
```

**Ask option:** `"What will happen to the Vale now?"`

**Felicitar:**
```
"Restored, the Vale shall be. Already feel it I can — the water
returning, the soil awakening. A slow healing it will be, but
heal it shall.

Our children will know green fields again. Grow again, the
plants shall. Flow again, the waters shall. And guide them, once
more we shall — through the Shield, as in the days of old."
```

### 6. The Gift

**Felicitar:**
```
"One more gift, we have for you. A token of our gratitude, and
a tool for your journey ahead."
```

*Ezrekal enters the shrine (if `ezToTemple = true`).*

**Ezrekal:**
```
"Felt it I did! Known something had happened I have! The Ancient
Ones... free they are! Oh, tears of joy these are! Dreamed of
this day I have, all my life!"
```

**Ezrekal (kneels):**
```
"Ancient Ones, your humble servant I am. Failed you I did not.
Kept the faith I have, even when all others doubted."
```

**Felicitar (to Ezrekal):**
```
"Rise, faithful one. Failed us, you never did. Through the
darkest years, your voice reached us. The only light in our
prison, your prayers were. High Priestess you are, and High
Priestess you shall remain."
```

*Ezrekal rises, weeping.*

**Ezrekal (to Avatar):**
```
"What a wonderful time this is! Once again be able to fulfill
my duties as High Priestess I will! Nothing there is I can give
you to repay you for your trouble, but this I can give you there
is. A magical bag it is."
```

> **Note:** This bark already exists in EZREKAL.UNK. It is gated behind
> `godsFree = true`. The `TypeBagOReagents` item is spawned here.

### 7. Farewell

**Timyra:**
```
"Go now, Avatar. Much yet to do, you have. But know this: alone,
you are not. Watched over, you shall be. And when the time comes
to face the Titans... remember that beyond their power, forces
exist. We are proof of that."
```

**Doloras:**
```
"Carry our blessing with you, mortal. And when sorrow weighs
upon you, remember: to feel sorrow is to know that something
mattered. Lose not that knowledge."
```

**Felicitar:**
```
"Joy go with you, Avatar. And when to your Britannia you return,
tell them of us. Tell them that even in the darkest places, hope
endures."
```

*The gods return to the shrine's inner sanctum. The Shield
remains on the altar, glowing. Sets `godsFree = true`,
`godsSpoke = true`, `getPowerAO = true`.*

---

## Look Barks — Gods (after freed)

```
"Felicitar, Ancient One of Joy"
"Doloras, Ancient One of Sorrow"
"Timyra, Ancient One of Courage"
```

> **Note:** Timyra's domain is listed as "Fear" in some sources and "Apathy"
> in others. In dialogue, I've reframed it as "Courage" (mastery of fear) —
> Timyra says `"To feel fear and act despite it — that is courage."` This is
> consistent with the Zealan philosophy of embracing emotions rather than
> suppressing them.

---

## Design Notes

1. **The gods speak the "purest" Elean Speak.** Their syntax is more
   consistently inverted than any NPC, befitting beings who created the
   language. Every declarative is inverted.

2. **Each god has a distinct emotional domain:**
   - Felicitar: warm, generous, hopeful (Joy/Love)
   - Doloras: melancholy, reflective, deeply empathetic (Sorrow)
   - Timyra: perceptive, commanding, philosophical (Fear→Courage)

3. **Ezrekal's existing dialogue** is reused where possible. Her bark
   about the magical bag (`"What a wonderful time this is!"`) is already
   in the usecode and should play here.

4. **The gods do not give specific instructions** about defeating the Titans.
   This preserves the base game's quest structure — the Avatar still needs
   to figure out the Titan-defeating path on their own.

5. **The "other three gods" mystery** (Odion, Apathas, Amoras) is referenced
   by Doloras but not resolved. This is an intentional open thread.

6. **Timyra's domain reframing:** The design docs call her "Apathy" or "Fear."
   Since the Zealans revere emotions (not suppress them), "Fear" is reframed
   as "Courage" — the mastery of fear. This is more fitting for a benevolent
   deity and matches Timyra's dialogue about facing fear.

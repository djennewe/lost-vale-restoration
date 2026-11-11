# Mythran — Base Game Dialogue Analysis

Style guide for writing Mythran's missing Lost Vale dialogue.
All data extracted from USECODE.FLX class 0x0421 (41,265 bytes, 499 strings).

---

## 1. Speech Pattern Summary

### Register
Formal, scholarly English with light archaic coloring. He is the most articulate
NPC in U8 — his sentences are long, complex, and precise. He never uses Elean
Speak (inverted syntax). He speaks standard English.

### Signature Words and Phrases

| Pattern | Frequency | Examples |
|---------|-----------|---------|
| `"Ah"` opener | Very high | `"Ah, good."` `"Ah, yes."` `"Ah, interesting question."` `"Ah, greetings, traveler."` `"Ah, Tenebrae."` `"Ah, I see."` `"Ah, very well."` |
| `"my friend"` | 15+ times | Main form of address once rapport is built. Replaces "stranger" / "young one" from first meeting. |
| `"Indeed"` | Moderate | `"Indeed, no"` / `"Indeed, I do"` — scholarly affirmation |
| `"Perhaps"` | Very high | `"Perhaps you wish"` / `"Perhaps in the future"` / `"Perhaps another time"` — hedging |
| `"Very well"` | 10+ times | Transition/dismissal: `"Very well, then"` |
| `"Excellent"` | Moderate | Positive outcomes: `"Excellent. Use this well."` `"Excellent. We can now begin."` |
| `"I am sorry"` | Moderate | Polite deflection: `"I am sorry that I cannot help you then."` |
| Dashes for emphasis | Consistent | `-have-`, `-you-`, `-can-`, `-all-` — italics substitute in the engine |

### Sentence Structure

- **Long and complex.** Information-delivery sentences average 30–50 words with
  multiple subordinate clauses.
- **Parenthetical asides** with dashes: `"-- or should I say misuse --"`,
  `"-- nay, loathed --"`
- **Rhetorical questions:** `"Do you truly wish a means off this world? Or are you
  simply testing the limits of my knowledge?"`
- **Conditional hedging:** `"Perhaps, with a little more time"`, `"I cannot say,
  for I do not know whether"`

### How He Addresses the Avatar

The form of address evolves as the relationship develops:

| Stage | Term |
|-------|------|
| First meeting | `"stranger"`, `"young one"`, `"stranger to this land"` |
| After name exchange | `"[NAME]"` (uses the Avatar's actual name) |
| Established rapport | `"my friend"` (dominant form thereafter) |
| Late game | `"traveler"` (occasionally) |

### Archaic Vocabulary

Uses sparingly, never enough to feel forced:
`"'tis"`, `"nay"`, `"aye"`, `"thou canst"`, `"thee"`, `"fare well"`,
`"lest"`, `"boon"`, `"bade"`

> **Note:** He uses `thee/thou` only when quoting Lord British or speaking in
> extremely formal contexts. His normal speech is modern-formal English.

---

## 2. Personality Profile

### Core Traits

1. **Scholarly / Intellectual** — Primary motivation is knowledge. `"I suppose I
   spend most of my time studying and exploring the mind."` Has written at least
   three books. Lives alone studying.

2. **Eclectic / Independent** — Lives in an extra-dimensional house on the Plateau.
   Practices Thaumaturgy, which `"borrows bits and pieces from any form of magic."`
   Not aligned with any school or Titan.

3. **Generous but Pragmatic** — Gives recall disk and healing potions freely, but
   charges for scrolls and spells with apologetic explanations: `"I must confess
   that the eternal pursuit of knowledge, despite the solitude I afford myself on
   this dreary island, is costly."`

4. **Patient with Limits** — Tolerates repeated questions. But: `"I do not like to
   be tested."` If the player picks wrong options twice, he ends the conversation.

5. **Cryptically Knowledgeable** — Knows far more than he reveals, especially about
   the Guardian: `"I know that -you- know of him as well."` Deflects deep
   questions: `"Ask of it no more for now, please."`

6. **Warmly Paternal** — Genuinely cares about the Avatar. Time-of-day sensitive
   farewells. Worries about consequences of the Avatar's actions.

7. **Dry Humor** — `"Unusual? I do not see anything unusual about my living quarters.
   It does not differ from any other extra-dimensional abode."`

8. **Morally Nuanced** — Judges factions fairly: `"if you will permit me a judgement
   of ethics."` Notes consequences without lecturing.

### How Others See Him
- Bentic: `"has been known to dabble in the various magical arts and is a scholar"`
- Gwillim: `"an old hermit... just an eccentric old man"`
- Jenna: `"Some call him a sage, but I think he wields magic"`
- Shaana: `"His wisdom is great"`

---

## 3. Quest-Giving Pattern

This is the critical pattern for writing Mythran's LV dialogue.

### The "Leaving Pagan" Quest Hook (his major quest delivery)

1. **Acknowledge the question's significance:** `"I have never had anyone ask such
   a question."`
2. **Test the asker's sincerity:** `"Do you truly wish a means off this world? Or
   are you simply testing the limits of my knowledge?"`
3. **Establish personal investment:** `"I, myself, have given considerable thought
   to finding ways to cross into what you would call 'other worlds.'"`
4. **Admit limits of his knowledge:** `"I have not yet uncovered a solution."`
5. **Present theoretical framework:** `"However, I -have- come to the conclusion
   that it is the power of the Titans..."`
6. **Derive logical conclusion:** `"Therefore, it is reasonable to assume that to
   depart from Pagan, one must master the powers of all four of the Titans."`
7. **Give practical first step:** `"I suppose the best place to begin is with one
   of the schools of magic."`
8. **Direct to specific NPC:** `"Speak with Vividos about becoming his apprentice."`
9. **Acknowledge difficulty:** `"I realize the thought of dealing with the rituals
   of death may seem distasteful, but I expect it is something to which you must
   become accustomed."`

### Teaching Pattern (spell delivery)

1. **State readiness:** `"You are ready for your [Nth] lesson."`
2. **Apologize for cost:** `"I must confess... I am afraid I must charge you..."`
3. **State price:** `"I must ask [N] in obsidian chits."`
4. **Deliver knowledge:** `"Here is the book. Study it well."`
5. **Remind of practical needs:** `"Do not forget that you will need reagents."`

### Blackrock / Endgame Pattern

1. **Examine and speculate:** `"That piece of black stone?"` / `"I wonder if it
   could be..."`
2. **Connect to history:** `"It is possible you have found one of the Fragments..."`
3. **Direct to written source:** `"Somewhere I have a book that might delve into
   greater detail."`
4. **Wait for player to research**
5. **Reveal the path:** `"You must cast the Ethereal Travel spell."`
6. **Acknowledge uncertainty:** `"I do not know where the spell will send you."`
7. **Inspire confidence:** `"Good luck..."`

---

## 4. Key Principles for LV Dialogue

Based on the pattern analysis above, Mythran's LV dialogue should:

1. **Contextualize before directing.** He explains WHY before telling WHAT to do.
   Never gives bare instructions.

2. **Frame quests as logical deductions:** `"Therefore, it is reasonable to
   assume..."` — not commands.

3. **Admit uncertainty openly:** `"I cannot say"`, `"I do not know whether"`,
   `"I have not yet uncovered"` — he's honest about his limits.

4. **Give practical hooks alongside theory.** Always: go talk to X, find object Y,
   look in location Z.

5. **React to world state.** His dialogue changes based on what the Avatar has
   already done. He's aware of events.

6. **Express concern for consequences.** He notes ramifications without lecturing.

7. **Use "Ah" opener and "my friend" address.** These are his most consistent
   verbal markers.

8. **Use dashes for emphasis** on key words: `-have-`, `-you-`, `-can-`, `-all-`.

9. **Soften bad news** with `"Of course, I realize"` and `"Please accept my
   humble apologies."`.

10. **Keep greetings time-aware:** `"Good evening"` / `"Good morning"` / `"Good day"`.

---

## 5. What He Knows About the Zealans (pre-LV)

From his existing base game dialogue, Mythran already knows:

- The Zealans existed: Lord British's message says `"the race that once thrived
  upon the land that is now your prison"`
- The Zealans lost to the Pagans: `"the Zealans fell to their enemies"`
- The Zealans worshipped the Ancient Ones (Zealan gods)
- The Great Cataclysm happened when the Titans fought the Destroyer
- He references the "haunted grove" (circle of dead trees on the Plateau)

This is the baseline knowledge he has when Lord British's message asks the Avatar
to learn about the "ancient race" from Mythran. His LV dialogue needs to expand on
this — revealing what he knows about the Zealans' survival in the Vale, about
Galjeron's exploration, and about the double doors.

---

## 6. Sample Dialogue Lines (from base game, for tone reference)

### Scholarly exposition
> `"There are four of what I call 'schools' of magic on Pagan -- one for each of
> the Titans."`

### Gentle guidance
> `"I suggest you begin with the Necromancers, then."`

### Dry humor
> `"Unusual? I do not see anything unusual about my living quarters. It does not
> differ from any other extra-dimensional abode."`

### Moral nuance
> `"I hope you realize the effect of taking the Breath of Wind. The citizens have
> little in the way of healing now."`

### Acknowledging limits
> `"To be honest, I know little about the people."`

### Warm farewell
> `"Good evening, my friend, and farewell."`

### Combat reluctance
> `"I do not wish to do this."`
> `"A pity..."`

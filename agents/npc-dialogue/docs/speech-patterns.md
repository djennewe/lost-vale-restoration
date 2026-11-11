# NPC Speech Patterns — Style Guide

Reference for writing missing dialogue. Each NPC's patterns are derived from
their surviving usecode dialogue (see `dialogue-inventory.md` for verbatim lines).

---

## 1. "Elean Speak" — Universal Zealan Speech Pattern

All Zealan NPCs (Ezrekal, Atli, Thordis, Tyorvi, Ragnar, Hrodny, Ingyald, the
Child) use inverted syntax. The pattern is sometimes called "Yoda-speak" but has
its own specific rules.

> **Two notes added 2026-07-26.**
>
> **"Elean Speak" is our own coinage**, not a 1994 term. There is no Elean
> clan: the word survives only in the filename of a 2014 gallery scan. The
> two clans are **Gunnar** and **Hoskuld**. The label is kept because it is
> already used throughout these docs and in SIGRID.UNK, but nobody should
> infer a people from it.
>
> **This page's "all Zealan NPCs" claim is now measured, and it holds.**
> Against a control of 13 base-game Pagan conversations at 2.3 inversions per
> 100 sentences, Clan Gunnar runs 32-38 and Clan Hoskuld 30-42: statistically
> indistinguishable from each other, and roughly fifteen times the base-game
> rate. About 2,450 inverted clauses across ~9,000 sentences in 10 files.
> This retires the "one clan speaks in inverted syntax" premise that the
> improvement plan carried from a 2009 memoir. See
> `docs/research/2026-07-25-design-fidelity.md`.

### Core Rules

1. **Verb-final in declaratives.** The main verb moves to the end of the clause:
   - Standard: `"I am called Atli."` → Elean: `"Called Atli I am."`
   - Standard: `"I am sorry."` → Elean: `"Sorry I am."`
   - Standard: `"The shield was stolen."` → Elean: `"Stolen the shield was."`

2. **Object/complement fronts.** The object or complement moves before the subject:
   - Standard: `"I can not tolerate this."` → Elean: `"Tolerate this I shall not!"`
   - Standard: `"I do not have it."` → Elean: `"Have it I do not."`

3. **Adjective/adverb fronting.** Descriptive words move to the front:
   - Standard: `"She is very difficult to understand."` → Elean: `"Very difficult to understand you are."`
   - Standard: `"It is obvious from your dress."` → Elean: `"Obvious it is from your dress."`

4. **Questions use "do" inversion but keep Elean word order:**
   - `"Where come from do you?"`
   - `"What called are you?"`
   - `"Need what, do you?"`

5. **Exclamations and emotional outbursts can break the pattern:**
   - `"NO!"`, `"BEGONE!"`, `"LEAVE!"`, `"Help!"` — these are standard English.
   - The pattern breaks under extreme emotion, then reasserts.

6. **Complex sentences apply inversion per clause:**
   - `"If give me a kiss you will, become a handsome man I will."`
   - `"In the days before the Great Cataclysm, given to teach our youngsters about their own mortality this test was."`

### Common Elean Constructions

| Pattern | Example |
|---------|---------|
| `[Complement] I am` | `"Ezrekal my name is."` / `"The High Priestess I am."` |
| `[Object] [Subject] did/does` | `"Fouls my home your evil presence does!"` |
| `[Adjective] it is` | `"Very sacred the special days were."` |
| `[Verb-inf] you must` | `"Bring the sacred shield, you must!"` |
| `Said it is that...` | `"Said it is that lit the skies for many hours each day the great ball of fire did."` |
| `[Past participle] [Subject] was/were` | `"Claimed my best friend those cliffs did."` |
| `Have [object] I do not` | `"Have it I do not."` |

### Frequency of Inversion

Not every sentence is inverted. Short exclamations, questions starting with
standard interrogatives, and emotional outbursts use normal English. The pattern
applies ~70-80% of the time in regular speech. In rapid dialogue or arguments,
the percentage drops.

---

## 2. Ezrekal — High Priestess

### Pattern Notes
- **Strictest** Elean Speak practitioner. Nearly every declarative is inverted.
- Long, flowing sentences with multiple inverted clauses.
- Uses `"Hmmmm"` and `"Oh"` as discourse markers.
- Rarely breaks the pattern except in shouted outbursts (`"BEGONE!"`, `"AWAY!"`).

### Vocabulary
- Formal/priestly register. `"Ancient Ones"`, `"High Priestess"`, `"special days"`,
  `"the Great Cataclysm"`, `"the Sacred Circle"`, `"Cloud City"`
- Terms of abuse for Pagans: `"filth"`, `"wretch"`, `"slime"`, `"foul creature of
  the dark"`
- Emotional range: fierce anger → scholarly exposition → gentle storytelling →
  maternal concern → commanding authority

### Distinctive Features
- Tells Vale stories/legends as extended narratives
- Uses `"Wounded I am"` (emotional) and `"Sorry I am"` (apology) — verb-final
  pattern applied to emotional states
- When commanding: `"Bring the sacred shield, you must!"` / `"Silent before me,
  you will be!"`
- Her funeral offer is both comic and touching: `"A nice funeral it will be."`

### Emotional States

| State | Example | Notes |
|-------|---------|-------|
| Fury | `"EEEEEEEHHH!!! A PAGAN!!"` | Pattern breaks, all caps |
| Apology | `"Sorry I am, acted so rudely before I did."` | Pattern maintained |
| Scholarly | `"Control all emotions, the Ancients do."` | Strict inversion |
| Gentle | `"A nice young man you seemed, too."` | Tender tone |
| Commanding | `"Silent before me, you will be!"` | Emphatic inversion |
| Hopeful | `"Yes! Yes! Knew, done it could be, I did!"` | Pattern with excitement |
| Sad | `"Oh, sad this is. Wounded I am."` | Short, clipped |

---

## 3. Atli — Elder of Clan Gunnar

### Pattern Notes
- Strong Elean Speak, similar to Ezrekal but more aggressive.
- His inversions carry contempt: the syntax amplifies his insults.
- Uses more modern/colloquial insults despite the inverted structure.

### Vocabulary
- Clan pride: `"Gunnar the martyr"`, `"the all-giving martyr"`
- Insults for Hoskulds: `"dung-eating peasants"`, `"mouth-breathing, nose-picking
  idiots"`, `"murdering, theiving worthless animals"`, `"scum-sucking torax whelp"`
- Accusatory: `"A spy you are"`, `"Prove it!"`

### Distinctive Features
- More willing to break pattern for emphasis: `"Prove it!"`
- Uses longer insult chains that stay in Elean syntax:
  `"Lying, mud eating, filth!"`
- Suspicious nature comes through in rapid-fire challenges:
  `"Pagan you mean? Believe you I do not..."`

### Contrast with Thordis
Both are clan elders, but:
- Atli is aggressive, accusatory, confrontational
- Thordis is despairing, weary, resigned
- In the Shade scene squabble, Atli attacks, Thordis defends

---

## 4. Thordis — Elder of Clan Hoskuld

### Pattern Notes
- Strict Elean Speak. Her inversions carry weariness and despair.
- Short sentences predominate — she's exhausted.
- Random barks are the most revealing: isolated thoughts of a desperate leader.

### Vocabulary
- Despair: `"Failed, I have."`, `"Lost, lost, we are..."`, `"Lay down and die, I
  should."`, `"No hope, there is..."`
- Loneliness: `"Lonely, I am..."`, `"The last Elder, shall I be."`
- Farming struggle: `"Withering, the poor crops are."`, `"Poor, our soil is..."`
- Religious doubt: `"Why Ancient Ones, forsaken us, have you?"`

### Distinctive Features
- Most emotionally fragile NPC. Her barks read like internal monologue.
- Blames herself: `"Failed, I have."` / `"Do something for my poeple, I must!"`
- Field barks are practical and desperate — she's farming to survive.
- Her reconciliation dialogue shows humility: `"Unworthy am I, upon you to look."`

---

## 5. Tyorvi — The Elder's Brother (Veteran)

### Pattern Notes
- Elean Speak **modified by drunkenness**. When drunk, consonants shift:
  `s → sh`, words slur, `-hic-` interrupts the syntax.
- When sober, his inversions are clean and articulate.
- The drunk/sober contrast reveals his intelligence underneath the addiction.

### Drunk Speech Rules
1. `s` → `sh` in many words: `"shomething"`, `"dresshes"`, `"talksh"`, `"likesh"`,
   `"Mishter"`, `"thash's"`, `"shtop"`, `"cliffsh"`, `"monthsh"`, `"alwaysh"`
2. `-hic-` inserted between phrases (not mid-word)
3. `-sob-` for emotional breaks
4. Ellipses `...` for trailing off
5. Repeated words: `"Well, well, well"`, `"Look good? Look good?"`

### Sober Speech
Clean Elean Speak without the slurring:
- `"Yes, have it I do. Want it do you?"`
- `"No, allow this I can not. Come upon you the curse will."`

### Vocabulary
- Self-medication: `"Drink enough to shtop the dreams I cannot."`
- PTSD imagery: `"Dropped my ax I have and reaching for it he does..."`, `"falling
  he is"`, `"screaming he is"`, `"blood everywhere there was"`
- Bravado masking pain: `"Kind of like that I do."` / `"In vain our deaths will not be."`
- Contempt for Avatar: `"Mishter Pagan, your kind likesh Torax better than women"`

### Distinctive Features
- Most complex NPC psychologically. His alcoholism is both comic and tragic.
- Nightmares are described in vivid present tense within the Elean structure
- The `-hic-` and slurring are the most immediately recognizable speech markers
  in the game

---

## 6. Ragnar — Hunter, Clan Hoskuld

### Pattern Notes
- Standard Elean Speak. Less elaborate than Ezrekal or Atli.
- Shorter sentences — he's a practical man, not a talker.
- His inversions are simple and direct.

### Vocabulary
- Hunting/nature: `"Dry this land is...and barren."`, `"Little game to hunt there
  is."`, `"Wild torax, mainly."`
- Old stories: `"Remember stories I do about the old days."`, `"Bigger than a torax
  they were."`
- Philosophy: `"Not a vengful man I am."`, `"Be peaceful with all a man cannot be."`

### Distinctive Features
- Armitage identified his speech as similar to Ezrekal's pattern but simpler
- Matter-of-fact observations: `"What to tell there is? A barren, dry place it is."`
- Blunt honesty: `"Then a fool you are. No disrespect do I mean."`
- Only male hunter in Hoskuld territory (the Female Hunter was never implemented)

---

## 7. Hrodny — The Inventor, Clan Gunnar

### Pattern Notes
- Elean Speak in short, frustrated bursts.
- Her random barks are truncated thoughts — she thinks faster than she speaks.

### Vocabulary
- Frustration with others: `"Fools, they are!"`, `"If only listen, they would!"`
- Work focus: `"Work, it should..."`, `"Understand it, I do not!"`
- Practical concern: `"Hungry, I am."`, `"Starve, we need not!"`

### Distinctive Features
- Shortest dialogue of any major NPC — suggests her full conversation tree was
  either incomplete or her character conveyed more through actions than words
- Her atheism (`"Can't sit and wait for gods that never existed"` per Character List)
  doesn't appear in her surviving dialogue but is referenced by Thordis

---

## 8. Ingyald — The Brewer, Clan Gunnar

### Pattern Notes
- Standard Elean Speak. Friendly/mercantile tone.
- His speech is the most approachable of any Zealan NPC.

### Vocabulary
- Commerce: `"A drink, do you wish?"`, `"To buy my brew, come, you have?"`
- Social awareness: `"Hmmmm. Seen Tyorvi today, I have not."` — tracks his customer
- Daily life: `"Ask Atli for more wood, tomorrow, I must."`

### Distinctive Features
- Warm and welcoming despite being the source of cross-clan tension
- His bark `"Hrodny brings food soon, I hope"` shows he depends on Hrodny (same clan)
- Aware of the water crisis: `"Gone down again, the water has..."`

---

## 9. Zealan Child

### Pattern Notes
- Elean Speak in child register — simpler inversions, shorter sentences.
- Uses `"yeah"` as a childish affirmation.

### Vocabulary
- Child-appropriate: `"Mama"`, `"strangers"`, `"funny clothes"`
- Torax joke: `"Why big and brown are toraxes?"` → `"Because then kith they would be."`

### Distinctive Features
- The child's refusal to talk to strangers (`"Told me never to talk to strangers my
  mama did"`) uses perfect Elean Speak in a childlike context
- His question chain (What called are you? Where come from do you? etc.) mirrors
  the adult NPCs' question patterns but with innocent curiosity instead of suspicion

---

## 10. Lord British

### Pattern Notes
- **Formal archaic English.** Uses thee/thou consistently.
- NOT Elean Speak — standard English word order.
- This is the one non-Zealan LV NPC.

### Vocabulary
- Royal register: `"Avatar"`, `"magician"`, `"trusted friend"`, `"dark veil"`,
  `"tether"`, `"counsel"`, `"the wise man"`, `"the ancient race"`
- U7-era: `"thou canst"`, `"thy"`, `"thee"`

### Distinctive Features
- His message is an item bark, not NPC dialogue — it plays when the item activates
- Urgency: `"my time here is short"`, `"journey with great haste"`, `"please hurry"`
- Names Mythran explicitly: `"the wise man known as Mythran"`
- Names the Zealans implicitly: `"the race that once thrived upon the land"`

---

## 11. Mythran

### Pattern Notes
- **Formal modern English with light archaic coloring.** Standard word order.
- NOT Elean Speak. He is Pagan, not Zealan.
- See `mythran-analysis.md` for his complete style guide.

### Key Markers (quick reference)
- Opens with `"Ah"` frequently
- Addresses Avatar as `"my friend"` (after first meeting)
- Uses dashes for emphasis: `-have-`, `-you-`
- Long, complex sentences with subordinate clauses
- Admits uncertainty openly
- Dry humor
- Contextualizes before directing

---

## 12. Shades (Hoskuld and Gunnar)

### Pattern Notes
- Elean Speak in grave, formal register. Short, solemn declarations.
- These are ghosts speaking truth — their speech is the most dignified in the game.

### Vocabulary
- Heroic register: `"the realm of the gods, we sought"`, `"our sacred shield"`,
  `"our clans to reunite"`, `"by foul monsters, slain we were"`
- Grief: `"But now grieved, I am."`, `"What we sought, only worsened we did."`

### Distinctive Features
- No insults, no anger — pure sorrow and truth-telling
- Their revelation is the dramatic climax: both boys went TOGETHER to find the gods,
  not as thieves. The feud is based on a lie.
- End with a command: `"Free them, you must!"`

---

## 13. Writing Guidelines for Missing Dialogue

### For any Zealan NPC (Hunter, Column/Cliff mechanics, AO Scene)
1. Use Elean Speak consistently (~70-80% of declaratives)
2. Short exclamations and emotional outbursts can be standard English
3. Match the emotional register to the character (see individual sections)
4. NPC combat barks invoke `"Shades"` or `"Ancient Ones"` for protection

### For Mythran
1. Use standard formal English
2. Open new topics with `"Ah"`
3. Address the Avatar as `"my friend"`
4. Contextualize before directing — explain WHY first
5. Admit uncertainty where appropriate
6. Include dry humor where it fits naturally
7. Use dashes for emphasis on key words
8. See `mythran-analysis.md` for the full quest-giving pattern

### For the AO Scene Gods
1. The gods (Felicitar, Doloras, Timyra) are never heard in surviving dialogue
2. They should speak in a MORE formal version of Elean Speak — they are the
   source of the language
3. The Monster Skull message names all six Ancient Ones and establishes a warm,
   familial tone among siblings: `"To my brothers, Odion and Apathas, and my
   sister, Amoras"`
4. The unnamed author of the message is Doloras (by elimination from the six)

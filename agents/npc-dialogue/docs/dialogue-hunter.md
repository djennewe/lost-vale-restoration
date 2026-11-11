# Hunter NPC — Female Hunter, Clan Hoskuld

Missing dialogue segment #2. Writer: Brian M. → Sheri (never completed).
Character List 1.0 archetype: "Female Hunter (Clan Hoskuld)."

All dialogue written in Elean Speak (see `speech-patterns.md`).

---

## Character Profile

From Character List 1.0:
- Comes from generations of hunters
- Remembers stories her grandfather told about bigger game
- Wishes for bigger game — harpies would be good challenge
- Loves husband dearly but can't understand why he is happy mucking about in the mud
- Married to the Male Farmer; has a son (the Male Child)

**Usecode name:** Not implemented — this NPC needs a new usecode class.
**Suggested name:** Sigrid (Norse female name, fitting the naming convention:
Thordis, Tyorvi, Hrodny, Ragnar, Ingyald, Atli).

---

## Flags

```
globalflag sigridMet            // has Avatar met the Hunter?
globalflag sigridName           // has Avatar learned her name?
globalflag sigridJob            // has Avatar asked about her job?
globalflag sigridToldHunting    // has she talked about hunting?
globalflag sigridToldHarpies    // has she mentioned harpies?
globalflag sigridToldHusband    // has she talked about her husband?
```

---

## Class Definition

```
npcclass Sigrid inherits Npc
```

**Schedule (Map 10, Clan Hoskuld territory):**
- Hunting grounds (daytide/firstebb) at ~13500,16000,64
- Home (eventide/bloodwatch/threemoons/lastebb) at ~12000,13500,64

---

## Look Barks

| Condition | Text |
|-----------|------|
| Dead | `"hunter's lifeless body"` |
| Name+Job | `"Sigrid the hunter"` |
| Name only | `"Sigrid"` |
| Job only | `"hunter"` |
| Unknown | `"woman"` |

**Combat bark:** `"Fight, I will! Shades, give me strength!"`

---

## Random Barks — Hunting Grounds

```
"Quiet! Scare the game, you will!"
"Tracks here, there were... Gone now, they are."
"A torax passed this way. Small, but feed us it will."
"Remember when plentiful the game was, I do not. But told so, grandfather did."
"Bigger prey, wish for, I do. Something to truly test my skill."
"Withered, even the hunting grounds have."
```

## Random Barks — At Home

```
"Tired, I am. But feed my family, I must."
"Mud on his boots again, my husband has. Surprise, that is not."
"Where gone has that boy? Everywhere, he goes!"
"Sharpen my spear, I should."
"Brought home two torax today, I did. Not enough, it is."
"In my grandfather's day, magnificent creatures roamed the Vale, they did."
```

---

## Dialogue Tree

### First Meeting

**Proximity bark (no mark):**
```
"Stop! A Pagan, are you? Stay back! Come closer and regret it, you will!"
```

**Proximity bark (with mark):**
```
"Hmm? The mark, you bear. Strange, you look, but a Zealan you must be."
```

### Name

**Ask option:** `"What is your name?"`

**Sigrid (sets `sigridName`):**
```
"Sigrid called I am. The hunter of Clan Hoskuld I am.
Strange you look. Strange you dress. Not from the Vale, you are."
```

### Job

**Ask option:** `"What do you do?"`

**Sigrid (sets `sigridJob`):**
```
"Hunt I do. Every day into the grounds I go. Whatever game find
I can, back to the clan I bring. Feed my family and my people,
I must.

A hunter my mother was, and her mother before her, and her mother
before her. In my blood, the hunt is."
```

### Hunting / Old Days

**Ask option:** `"What do you hunt?"`

**Sigrid (sets `sigridToldHunting`):**
```
"Torax, mostly. Small, stupid creatures they are. But little
else remains. Dried up, the Vale has. Withered, the plants have.
Fled or died, most of the game has.

Stories my grandfather told me of the old days, when the Vale
green was and great beasts roamed the hills. Horned creatures,
twice the size of a man. Challenge a hunter, they would. A
worthy kill, they were."
```

**Ask option:** `"You wish for bigger game?"`

**Sigrid (sets `sigridToldHarpies`):**
```
"Wish? Dream of it, I do! Heard of the harpies have you?
Terrible winged creatures, upon the cliffs they nest.
Dangerous, certainly. But what a challenge they would be!

To hunt a harpy... test every skill I have, it would. Sharpen
my spear I would and climb those cliffs and face them I would,
if allow it Thordis did. But foolish she calls me. 'Die you
will,' she says. Perhaps right she is.

But what a hunt it would be!"
```

### Husband

**Ask option:** `"Tell me about your family."`

**Sigrid (sets `sigridToldHusband`):**
```
"A husband I have. A good man he is, but understand him sometimes
I cannot. Happy he is to spend his days in the mud, coaxing
plants from this cursed soil. 'From the ground, life I bring,'
he says. Proud of his dirt he is!

Love him I do, though. Dearly. Proud of him I am, truly, even
if understand his love of mud I do not. Strong he is, and kind,
and devoted to our son.

And our boy! Everywhere that child goes. Hold still he cannot.
The wanderlust of his mother, that one has."
```

### The Vale

**Ask option:** `"What is this place like?"`

**Sigrid:**
```
"Dying, it is. Slowly, but dying. Less water each year there is.
Less game. Less food. Know it everyone does, but speak of it no
one will.

In my grandmother's time, a river ran through the center of the
Vale. Imagine! A river! Now barely a trickle remains, and fight
over even that the clans do.

Something must change, or last much longer we will not."
```

### The Feud

**Ask option:** `"Why do the clans fight?"`

**Sigrid:**
```
"Old wounds that will not heal. Stolen the shield was, killed
someone was, and blamed each other the clans have ever since.
Ask Thordis if the full story you want. Tired of it I am.

Hunt I do. Feed my people I do. Leave the politics to Thordis
and the arguing to the men."
```

### Post-Reconciliation (after `doneShades = true`)

**Sigrid:**
```
"Changed, everything has! Friends the two clans are now? Believe
it I can scarcely. But if mean it does more water and more
game... then welcome this peace is.

Perhaps now, hunt the harpies I can. With both clans united,
who to stop me there would be? Ha!"
```

---

## Design Notes

1. **Name choice:** "Sigrid" follows the Norse naming pattern of the existing
   NPCs (Thordis, Tyorvi, Ragnar, Hrodny, Ingyald, Atli). It means
   "beautiful victory" — fitting for a hunter.

2. **Personality:** Practical, independent, slightly impatient with politics.
   Her love of hunting and her family grounds her as the most "normal" NPC in
   the Vale — she's not consumed by the feud like the elders.

3. **Relationship to Ragnar:** Both are hunters in Clan Hoskuld. Ragnar hunts
   in the field (schedule x≈13695); Sigrid hunts at different coordinates.
   They can reference each other without overlap. Ragnar is more philosophical;
   Sigrid is more action-oriented.

4. **The husband** (Male Farmer archetype) is referenced but does not need his
   own usecode file. He appears only through Sigrid's dialogue.

5. **Post-reconciliation** dialogue shows her character — she immediately
   thinks about hunting harpies now that restrictions may be lifted.

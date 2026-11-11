# Mythran — Lost Vale Introduction Dialogue

Missing dialogue segment #1. Writer: Andrew (never completed).
Plot beats 2-3. This is Mythran's conversation about the Zealans, Galjeron,
the double doors, and the key/puzzle.

All dialogue written to match Mythran's base-game speech patterns
(see `mythran-analysis.md`).

---

## Context

After installing the expansion, the Avatar receives Lord British's message
(LORDBRIT.UNK) directing them to `"Seek the counsel of the wise man known as
Mythran"` and ask about `"the race that once thrived upon the land."` The Avatar
goes to Mythran's house and raises the topic.

## Flags

```
globalflag mythranToldZealans       // has Mythran explained the Zealans?
globalflag mythranToldGaljeron      // has Mythran told of Galjeron?
globalflag mythranToldDoors         // has Mythran described the double doors?
globalflag mythranToldKey           // has Mythran told where to find the key?
globalflag lbDone                   // Lord British message already delivered
globalflag mythranIntroDone         // intro completed (key heard + Farewell)
globalflag mythranStockVisit        // LV dialogue requests stock-Mythran handoff
```

## Wiring (DD-005a, implemented 2026-07-03)

`patch_mythran.py` appends a wrapper use() to the base Mythran class (0x421)
and repoints event 01 at it:

- `lbDone` clear: stock Mythran, untouched.
- `lbDone` set: TypeMythranLVDlg::use() always runs.
  - Intro not yet done (`mythranIntroDone` clear): the full intro conversation.
    The flag is set only when the player has heard the key hint
    (`mythranToldKey`) and chosen Farewell, so bailing out early replays the
    intro with the progressive ask list intact.
  - Intro done: a short follow-up menu — doors location recap, key hint recap.
- Both menus offer "Let us speak of other matters." That sets
  `mythranStockVisit` and ends the LV conversation; the wrapper sees the flag,
  clears it, and chains into the stock use() at 0x208C. The full base-game
  Mythran conversation therefore stays reachable forever, and the key hint
  stays reachable on repeat visits — the two DD-005 acceptance requirements.

---

## Dialogue Tree

### Entry — Avatar Asks About the Ancient Race

**Ask option** (appears after `lbDone = true`):
```
"Lord British sent me. He said to ask you about an ancient race."
```

**Mythran:**
```
"Ah. So the message has arrived at last. I confess, my friend,
I have been expecting you -- or someone very much like you.

Some time ago, I received a vision. In it, I saw a stranger
from another world who would come seeking knowledge of an
ancient people -- a people long thought destroyed. I did not
understand the vision at the time. But now, looking at you,
I believe I do."
```

### Ask — The Ancient Race

**Ask option:**
```
"Tell me of this ancient race."
```

**Mythran:**
```
"They were called the Zealans. Before the Pagans, before the
Titans claimed dominion over this world, there existed a people
who worshipped a different set of gods -- the Ancient Ones.
The Zealans were devout, peaceful, and by all accounts rather
more civilized than the Pagans who came after them.

When the Titans arose and the Destroyer threatened the world,
the Zealans were caught in the middle. Their gods were
overwhelmed, and the Zealans themselves were thought to have
perished in the Great Cataclysm that followed."
```

**Ask option:**
```
"Thought to have perished? You mean they survived?"
```

**Mythran:**
```
"That is the question, is it not? Most scholars -- and I use the
term loosely, as scholarship on Pagan leaves much to be desired --
believe the Zealans were wiped out entirely. I, however, have
never been entirely convinced.

You see, there are references in very old texts to a hidden valley
-- a place sealed away from the rest of Pagan during the great
upheaval. A place the Zealans called the Vale. Whether any Zealans
survived there, I cannot say with certainty. But I -can- say that
the possibility has occupied my thoughts for some years."
```

### Ask — What Lord British Wants

**Ask option:**
```
"Lord British says they can help me."
```

**Mythran:**
```
"Does he? Hmm. That is an intriguing notion. If the Zealans yet
live, and if their gods yet possess any measure of their former
power, then yes -- I can see how they might offer assistance that
no Pagan could provide. The Titans have no claim over Zealan magic.
It would be, so to speak, outside their jurisdiction.

Very well. If you are determined to pursue this, I can tell you
of a man who sought the Zealans before you."
```

### Ask — Galjeron

**Ask option:**
```
"Who searched for the Zealans?"
```

**Mythran (sets `mythranToldGaljeron`):**
```
"His name was Galjeron. An explorer -- perhaps the only true
explorer Pagan has produced since the Cataclysm. He was driven
by a conviction that the Zealans had not perished, and that their
hidden valley could still be reached.

I assisted him with what knowledge I could provide, and he set off
with great enthusiasm. That was a very long time ago, my friend.
He never returned."
```

**Ask option:**
```
"What happened to him?"
```

**Mythran:**
```
"I do not know. I feared the worst, of course, but I had no means
to follow him. He told me he had discovered a passage -- a set of
enormous double doors deep within a cavern on the Plateau. He
believed those doors led to the path the Zealans had used to reach
their hidden valley.

Whether he succeeded in opening them, I cannot say. But if you
wish to follow in his footsteps, that is where you must begin."
```

### Ask — The Double Doors

**Ask option:**
```
"Where are these double doors?"
```

**Mythran (sets `mythranToldDoors`):**
```
"Galjeron described the location as a cavern in the Plateau, not
far from where we stand. I believe you may know it -- it is the
same cave system where the creature called Bonecrusher once made
its lair. Deep within that cave, Galjeron found a massive set of
double doors carved from stone older than anything the Pagans
have built.

The doors are sealed, of course. I would not expect the Zealans
to leave their sanctuary unguarded."
```

### Ask — The Key

**Ask option:**
```
"How do I open the doors?"
```

**Mythran (sets `mythranToldKey`):**
```
"Galjeron spoke of a key, and on this matter he was less cryptic
than usual. He told me that when at last he stood before the great
doors, he found the chamber about them strewn with bones -- the
remains, I should think, of beasts, or perhaps of others who sought
the Vale and were not so fortunate. And there, amid the bones,
stood a chest. He was certain the key lay within it.

The Zealans, it seems, did not hide their key across half of Pagan
after all -- they set it before the very doors it opens, trusting
that any who reached so far had earned the right to pass. So search
the bone-strewn ground near the doors, my friend, and look to the
chest you find there. The key should be yours for the taking."
```

### Ask — What Lies Beyond

**Ask option:**
```
"What will I find beyond the doors?"
```

**Mythran:**
```
"If Galjeron's theories were correct, the doors lead to a passage
that eventually reaches the Vale itself. However, I suspect the
path will not be straightforward. The Zealans revered the four
elements -- earth, air, fire, and water -- in ways that differed
greatly from the Pagan understanding of the Titans.

I would advise you to be prepared for challenges that test your
mastery of the elemental forces. Beyond that, I can only speculate."
```

### Ask — Concern / Warning

**Ask option:**
```
"Is it dangerous?"
```

**Mythran:**
```
"My friend, everything on Pagan is dangerous. The question is
whether the danger is worth the reward. In this case, I believe
it may well be. If the Zealans survive, and if their gods retain
even a fraction of their former power, you may find allies unlike
any you have encountered on this world.

But I must be honest with you. Galjeron was a capable man, and
he did not return. Whatever lies beyond those doors, do not take
it lightly."
```

### Ask — Farewell

**Ask option:**
```
"Thank you, Mythran."
```

**Mythran:**
```
"You are welcome, my friend. I confess, I am curious to learn
what you discover. If the Zealans yet live, it would be the most
remarkable thing to happen on Pagan since -- well, since you
arrived.

Ah, one more thing. You are welcome to return here at any time.
If you find yourself in need of supplies or counsel, my door is
always open. Good luck, [NAME]."
```

### Late-Game Return — After Finding the Vale

**Ask option** (appears after `haveMark = true`):
```
"I found the Zealans, Mythran."
```

**Mythran:**
```
"You found them? They -live-? My friend, that is extraordinary.
In all my years of study, I dared only to hope. Tell me -- what
are they like? Are they as the old texts describe?"
```

**Ask option:**
```
"They speak strangely, but they are good people."
```

**Mythran:**
```
"Ah, yes. The Zealans had their own manner of speech, as I recall
from the fragments I have read. Inverted, was it not? Subject and
verb reversed? How delightful that such a tradition has survived.

I hope you can help them, [NAME]. If their gods can truly assist
you against the Titans, then this journey may prove to be the
most important thing either of us has ever undertaken."
```

### Late-Game Return — After Freeing the Gods

**Ask option** (appears after `godsFree = true`):
```
"I freed the Zealan gods."
```

**Mythran:**
```
"You have freed -gods-? My friend, I am at a loss for words, and
that, as you know, is a rare occurrence.

The implications of what you have done are staggering. If the
Zealan gods are free, then the Titans' hold over this world is
not as complete as they would have us believe. Perhaps there is
hope for Pagan after all -- hope that extends beyond your quest
to leave us.

I shall have to revise several chapters of my history. Ah, the
burdens of scholarship."
```

---

## Design Notes

1. **Mythran's knowledge is limited.** He knows of the Zealans from old texts
   and from helping Galjeron, but he has never been to the Vale himself. This
   matches his base-game pattern of knowing things theoretically but not from
   direct experience.

2. **The vision** serves two purposes: it explains why Mythran is willing to
   share dangerous knowledge, and it provides a narrative link between Lord
   British's message and the quest.

3. **Galjeron is described but never met alive.** Mythran's account establishes
   Galjeron as a historical figure the Avatar will find dead beyond the doors
   (Plot beat 4).

4. **The key hint points to the actual placement.** Mythran relays Galjeron's
   account that the key sits in a chest amid the bones near the doors — which
   matches what is placed in-game: shape 78 chest in the outer Bonecrusher-cave
   bone chamber with the quality-99 key (shape 82) as a containment record
   inside it (see `build_map_08.py`). He's still relaying secondhand
   information, so he hedges ("He was certain the key lay within it"), but the
   direction he gives is correct and leads the Avatar straight to the loot.

5. **Late-game reactions** show Mythran's scholarly delight at the discovery
   and his characteristic dry humor ("the burdens of scholarship").

6. **Word count:** ~1100 words of Mythran dialogue. His base-game class has
   ~5000 words of dialogue across 499 strings, so this addition represents
   a proportionate expansion for a major plot hook.

# Cloud Cliffs — Climbing Traversal Dialogue

Missing dialogue segment #4. Writer: Brian M. (never completed).
The climbing sequence, NPC reactions, and environmental barks for
the Cloud Cliffs (Cliffs of Insanity).

---

## Context

After getting the Key to the Clouds from Tyorvi, the Avatar climbs
the Cloud Cliffs to reach Cloud City (Plot beat 12-13). The cliffs are
dangerous — Tyorvi's best friend died here, and Tyorvi himself fell and
survived. Harpies nest on the cliffs.

## Flags

```
globalflag attemptedCliffs      // Avatar has started the climb
globalflag climbedCliffs        // Avatar has reached the top
globalflag agreeToClimb         // Avatar agreed to attempt the cliffs
globalflag cliffClimbing        // Avatar is currently on the cliffs
```

---

## Pre-Climb — Tyorvi Agrees to Accompany

When `agreeToClimb = true` and `givenTea = true` (Tyorvi is sober):

**Tyorvi:**
```
"Ready are you? Then go we shall. Promised to accompany you I
did, and a man of my word I am.

But warn you I must. Dangerous the cliffs are, more dangerous
than imagine you can. Pitons you will need, and rope, and
courage. Died up there my friend did, and nearly died I did.
Careful you must be."
```

**Ask option:** `"Are you sure you want to come?"`

**Tyorvi:**
```
"Sure? No. But owe this to my friend I do. In vain his death
should not be. If reach the top we can, then meaning his
sacrifice will have. Come. Waste more time we should not."
```

---

## The Climb — Environmental Barks

These fire as the Avatar ascends, keyed to position/altitude.

### Early Climb
```
"The wind is picking up."
"The handholds here are solid, at least."
"I can still see the Vale below."
```

### Mid-Climb
```
"Don't look down."
"The stone is crumbling here!"
"This must be where Tyorvi fell."
"I can hear something shrieking above — harpies?"
```

### Tyorvi Barks (mid-climb)
```
"Careful! Loose the rock is there!"
"Hold on! Blowing harder the wind is!"
"Here it was... here fell my friend... Keep going, we must."
"Above us, hear that do you? The harpies. Near their nests, we are."
```

### Late Climb (near the top)
```
"Almost there!"
"The clouds are so close I can touch them."
"I've never been this high before."
```

### Tyorvi Bark (at the top)
```
"Made it, we have! Believe it I can scarcely. The last time here
I was... No. Think of that I will not. Forward, only forward."
```

---

## Harpy Encounters

Harpies attack during the climb. Combat barks:

**Harpy (shriek):**
```
"SKREEEE!"
```

**Avatar (during harpy combat on cliffs):**
```
"I can barely fight on this ledge!"
"Keep your balance!"
```

**Tyorvi (during harpy combat):**
```
"The creatures! Tear us from the cliffs, they would!"
"Fight them off! Fall we must not!"
"Hate these things, I do!"
```

---

## Arrival at Cloud City

When the Avatar reaches the top (`climbedCliffs = true`):

**Avatar:**
```
"By the Virtues... what is this place?"
```

**Tyorvi:**
```
"The Cloud City... Real it is. Always thought a legend it was.
White as the clouds the walls are, just as Ezrekal said.

Here I leave you, I think. Belong here I do not. But grateful
to you I am. Freed me from my nightmares you did, and now see
this I have. Worth it, the climb was. Worth everything."
```

**Ask option:** `"Will you be alright going back down?"`

**Tyorvi:**
```
"Down? Ha! Easier than up, going down is. Provided fall I do
not. No, fine I will be. Changed, something inside me has.
The dreams... feel them I do not. Perhaps at peace my friend
finally is.

Go. Find what seek you do. And when return you do... tell me
of it."
```

---

## Failed Climb (if implemented)

If the Avatar falls during the climb (`attemptedCliffs` but not
`climbedCliffs`):

**Avatar:**
```
"Ugh... I survived, but barely."
```

**Tyorvi (if present):**
```
"Told you I did! Dangerous the cliffs are! Try again will you?
A fool you are, but brave. Like that I do."
```

---

## NPC Reactions — Post-Climb

### Ezrekal (after `climbedCliffs = true`)

Already handled in existing dialogue:
```
"I climbed the cliffs!" → triggers Cloud City / healing branch
```

### Thordis (after `climbedCliffs = true`)

```
"Climbed the cliffs have you? Survived? Remarkable. Perhaps
underestimated you we have."
```

### Ragnar (after `climbedCliffs = true`)

```
"The cliffs you climbed? And lived? A brave hunter you would
make. Respect, you have earned."
```

---

## Design Notes

1. **Tyorvi's arc completes here.** His PTSD subplot resolves through the
   climb — facing the place where his friend died. His farewell at the top
   is the emotional payoff for the nightmare/elixir questline.

2. **Tyorvi does NOT enter Cloud City.** He escorts the Avatar up the
   cliffs but stays behind. This keeps Cloud City as a solo exploration
   area and gives Tyorvi a clean exit.

3. **The climb is the only place harpies appear** — they nest on the
   cliffs, as established by the Hunter's dialogue about wanting to hunt
   them.

4. **Environmental barks** are in standard English (Avatar). Tyorvi's
   barks are in Elean Speak, maintaining his sober speech pattern (he has
   the tea cure by this point).

5. **The "don't look down" moment** and the reference to where Tyorvi
   fell create a connection to his nightmare descriptions: `"Dropped my
   ax I have and reaching for it he does..."`.

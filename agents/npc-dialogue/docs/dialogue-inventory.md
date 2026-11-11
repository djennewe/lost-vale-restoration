# Dialogue Inventory — Lost Vale Usecode

All dialogue extracted from the 67 LV source files in `shared/data/lv-usecode/`.
Organized by NPC, then Items/Objects, then Puzzles/Mechanics, then U8 Modified NPCs.

> **Notation:** `bark()` = spoken line. `ask()` = player choice menu.
> All strings verbatim from source. `~` in source = line break in-game.

---

## I. Zealan NPCs

---

### 1. Ezrekal — High Priestess of the Ancient Ones

**Files:** `LOST VALE/EZREKAL.UNK` (primary, ~2600 lines), `UNK files/UNK/EZREKAL.UNK` (earlier)
**Class:** `npcclass Ezrekal inherits Npc`
**Writer:** SHERI
**Schedule (Map 10):** Inside (daytide/eventide/bloodwatch/threemoons) at 19327,29439,64.
Outside (firstebb/lastebb) at 18431,29311,64.

#### Look Barks
| Condition | Text |
|-----------|------|
| Dead | `"Ezrekal's lifeless body"` |
| Name+Job known | `"Ezrekal the High Priestess"` |
| Name only | `"Ezrekal"` |
| Job only | `"High Priestess"` |
| Unknown | `"old woman"` |

**Combat bark:** `"Help! Help!"`

#### Dialogue — Pre-Mark Encounter (Avatar is a Pagan)

Five random barks when Avatar approaches without Zealan Mark:

1. `"Eh? What? A Pagan! A Pagan here? NO! Get gone, you foul creature of the dark! Leave me or call upon the Ancient Ones I will and blast you from my sight they will!"`
2. `"A Pagan? In my home? Begone, you filth! Fouls my home your evil presence does! BEGONE!"`
3. `"EEEEEEEHHH!!! A PAGAN!! Come to finish what your grandfathers started have you? Tolerate this I will not! Leave my sight, or call the powers of the Ancient Ones to destroy you I shall!"`
4. `"What is this? Why a horrid Pagan I believe it is! NO! Tolerate it I shall not! Leave me, you vile wretch! LEAVE!"`
5. `"Believe what I see, I can not! A PAGAN it is! Filth! Wretch! Slime! Away with you! Darken not my door! AWAY!"`

#### Dialogue — First Meeting (with Zealan Mark)

- Greeting: `"Hello"`
- Name (with prior yelling): `"Ezrekal my name is. Sorry I am, acted so rudely before I did. See the mark of the Zeleans upon you I did not. Funny, not like a Zelean you look. Different you look, different you speak. If not a Pagan you are, what are you?"`
- Name (without yelling): `"Ezrekal my name is. The mark of the Zeleans upon you I see. Funny, not like a Zelean you look. Different you look, different you speak. If not a Pagan you are, what are you?"`

#### Dialogue — Job / Role

- `"The High Priestess I am...or I was."`
- `"Of what you ask? Why of the Ancient Ones!"`
- `"Hmmmm, obvious it is from your dress and your speech that not from here you are. The mouth piece of the Ancient Ones the High Priestess is. On special days through me to their followers they speak."`

#### Dialogue — Zealan History and Lore

**Special Days / Ball of Fire:**
- `"Very sacred the special days were. Ruled by the great ball of fire in the sky they were..."`
- `"Said it is that lit the skies for many hours each day the great ball of fire did. So great its power was, kept the great mushrooms from growing the heat did. Great plants with brilliant colors grew and blue the sky was!"`

**Britannia / Outside:**
- `"Britannia?....No place in the Vale called 'Britannia' there is. From 'outside' the barrier are you?"`
- `"Oh, my! And not a Pagan you are? Well, of course not, the Mark you bear! Well, an interesting day this has become, met someone from outside I have."`
- `"That much guess I can by the way you act and certainly by the way you speak. Very difficult to understand you are. In your Britannia as well, the Titans are?"`

**Ancient Ones:**
- `"The Ancient Ones, who are? Sunk so far has it the names of the Ancients the young do not know? Oh, sad this is. Wounded I am, but tell you of them I will. Control all emotions, the Ancients do. Rich in power they are. Power to heal the world they have... and power to destroy it. Worshipped by all of Pagan they were until arrived the Titans did. A great battle it was. Ended in the Great Cataclysm it did."`

**Shield of the Ancients:**
- `"a great powerful artifact the Shield is. Used it to communicate with us the Ancients did. So powerful their magic is, sear the flesh from the High Priestess it would. So constructed a shield was to protect her when receiving their presence she was. But lost many years ago the shield was."`
- `"The shame of the High Priestess it is. After the Great Cataclysm terribly depressed the High Priestess became... One night, disappeared from her house the Shield did. At the same time, disappeared from the villages two young boys did... Neither boy nor the shield was ever found. Fighting ever since the families have been."`

**Exile:**
- `"Goes back to the Great Cataclysm it does. When occured that did, rush to the High Priestess the people did. Demand an answer from the Ancient Ones they did. But answer the High Priestess the Ancients would not. Accused the High Priestess of lying the people did. Ran her out of their village they did... Many, many years ago that was. Allow me back, the people of the village will not. Crazy, me they call. A fake I am they say. But watch for the return of the Ancients someone must."`

#### Dialogue — Poison / Funeral

- `"Sorry I am. A nice young man you seemed, too. A little hard to understand you are, but nice. Well, prepare a nice funeral for you I shall."`
- `"A nice funeral it will be. Burn the finest incense I will and sing some of the old songs I will. Invoke the Ancient Ones of Love and Joy I will and perform the ritual to chase away Sorrow I will."`
- `"This I cannot do. But begin preparations for your funeral right away I will. Have to gather the appropriate mushrooms I will."`

#### Dialogue — Cloud City / Healing

- `"The home of the Ancient Ones the Cloud City is. Atop those very tall cliffs you see off to the Northwest it is. Hmmmm, now that about it I think. A possible way for you to be healed there may be."`
- `"Well, not a very good chance it is, but better than no chance, any chance is. Before the Cataclysm, heal those poisoned in the Trial the High Priestess would... Said by some it is that the not gone the Ancient Ones are, but merely sleeping in their Cloud City. Perhaps go you could and awaken them."`
- `"Hmmmm, your only chance it may be. For if still there the Ancient Ones are, able to wake them and ask them to heal you, you may. If the Key to the Clouds I had, gladly give it to you I would. But have it I do not. Given it to Tyorvi I have."`

#### Dialogue — Eternal Peace / Undead

- `"Oh, live with the Ancient Ones you will and in their wonderful Cloud City serve them you will."`
- `"Certainly? Where else live would the Ancient Ones? Said it is that beautiful the city is. White as the clouds the walls are and bright as gold the streets are."`
- `"Oh, believe it is so I do not! Remnants of that horrid water Titan I believe they are. Believe the undead Zealans go to the Cloud City I do, the return of the Ancients to await."`

#### Dialogue — Healing

- `"I thought change your mind you might. Certainly heal you I will."`
- `"Hmmm, it seems heal you no more I can. Sapped your strength has been. Repair that damage only the Ancient Ones can."`

#### Dialogue — Temple / Gods Freed

- `"Opened the temple have you?! Something had happened I knew. I sensed it! How managed it did you?"`
- `"What a wonderful time this is! Once again be able to fulfill my duties as High Priestess I will! Nothing there is I can give you to repay you for your trouble, but this I can give you there is. A magical bag it is."`

#### Dialogue — Vale Stories

**Casera the fish:**
- `"Once a lush, green place the Vale was... Up from the water a fish jumped. 'Hello,' to her it said... 'If give me a kiss you will, become a handsome man I will and abide with you forever I will.' ...Picked up the fish from the stream High Priestess Casera did... 'Careless to get caught by a mage you were. Want to live with someone so careless I do not.' and fried fish for dinner that night she had!"`

**Felicitas creates Zealans:**
- `"Before the Titans, before the Pagans and even before the Zealans, here the Ancient Ones were... Their favorite place the Vale was... Felicitas... one day a bit of the ground she picked up and a bit of the clouds she mixed in and a small figure she formed. Gently into the figure's mouth she blew and to life it came... How the Zealans came to live in the Vale that is."`

**Gudbrand's Heart:**
- `"Once in the sky a great orange ball of fire hung... Called the Heart of Gudbrand this was... came to the Vale Amoras did. Here Gudbrand, leader of the Zealans, saw her and instantly in love he fell... slipped he did. Down the cliff he fell, to his death. When heard this Amoras did, fly to him she did, but too late she was. So touched she was by his love that his heart she took and placed it into the sky she did. That way provide light for all the world his love would."`

#### Dialogue — Tyorvi Subplot

- `"I would speak to you of Tyorvi."` (ask option when `tyorviDreams = true`)
- `"Is Tyorvi's elixir ready?"` / `"Have you made the elixir?"` (ask options for root/tea)

#### Ask Options (complete)

```
"May I know your name?"
"What do you do?"
"High Priestess of what?"
"What does the High Priestess do?"
"How do they speak through you?"
"When are the special days?"
"Ball of fire in the sky?"
"What happened to the ball of fire?"
"Why are there no more special days?"
"I am from Britannia."
"Yes, I am from outside."
"No, I am not from outside."
"Who are the Ancient Ones?"
"The Titans are still in control."
"I have heard from the Ancient Ones."
"I have not heard from the Ancient Ones."
"They did mention you."
"They did not mention you."
"Shield of the Ancients?"
"I was in their temple."
"Can you help me?"
"I have been poisoned."
"But I'm dying!"
"Atli sent me to you."
"Thordis sent me to you."
"Prepare my funeral?!"
"I want to be healed!"
"I don't want a funeral!"
"You said the Ancient Ones were gone!"
"What kind of eternal peace?"
"A city in the clouds?"
"Where will I be until then?"
"When will they return?"
"I don't want to be an undead!"
"Those cannot be Zealans!"
"Cloud City?"
"Remnants of the Water Titan?"
"How?! How can I be healed?"
"Tell me of the Shield."
"Tell me again of the Shield."
"How was it lost?"
"When did this happen?"
"Can you make another shield?"
"Where is the Cloud City?"
"Tell me more of the Cloud City."
"Are the Ancient Ones still there?"
"Has anyone ever been there?"
"Perhaps I will try the Cliffs."
"Key to the Clouds?"
"Where is the Sacred Circle?"
"How can I awaken the Ancients?"
"I have the Ancient Shield."
"I found it in the Temple in Pagan."
"I climbed the cliffs!"
"Please heal me."
"Tell me of the Vale."
"Tell me more of the Cataclysm."
"I have opened your temple!"
"I have freed your gods!"
"I found the Ancient Ones!"
"They are encased in amber."
"I have found the root."
"Is Tyorvi's elixir ready?"
"Have you made the elixir?"
"I would speak to you of Tyorvi."
"bye"
```

#### Key Flags

`ezrekalMet`, `ezrekalName`, `ezrekalJob`, `yelledAtAvatar`, `haveMark`,
`avatarPoisoned`, `spokeOfCataclysm`, `askedAboutAncients`, `spokeOfClouds`,
`mentionShield`, `toldOfShield`, `sentToTyorvi`, `climbedCliffs`, `spokeOfAwaken`,
`shieldFixed`, `spokeOfOpenTemple`, `templeOpen`, `godsFree`, `hasBag`, `ezToTemple`,
`toldValeOne`, `toldValeTwo`, `toldValeThree`, `tyorviDreams`, `hasRoot`, `givenRoot`,
`justGotRoot`, `givenTea`, `hasTea`, `toldAboutAddiction`

---

### 2. Atli — Elder of Clan Gunnar

**Files:** `LOST VALE/ATLI.UNK` (primary, ~1550 lines), `UNK files/UNK/ATLI.UNK` (earlier)
**Class:** `npcclass Atli inherits Npc`
**Writer:** SHERI
**Schedule (Map 10):** Eating (daytide/eventide/threemoons) at 18943,19711,64.
Lab (firstebb/lastebb/bloodwatch) at 18175,20095,64.

#### Look Barks
| Condition | Text |
|-----------|------|
| Dead | `"Atli's body"` / `"dead body"` |
| Name+Job | `"Atli, Elder of Clan Gunnar"` |
| Name only | `"Atli"` |
| Job only | `"Elder of Clan Gunnar"` |
| Unknown | `"man"` |

**Combat bark:** `"Help! Help!"`

#### Dialogue — First Meeting

- `"What? Who are you? Strange you dress! stranger you talk! A Pagan are you? No, surely not!"`
- `"Called Atli I am."`
- `"The Elder of Clan Gunnar I am."`
- `"Related to Gunnar the martyr, we are."`

#### Dialogue — Clan History

- `"Heard of him surely you have! The all-giving martyr he was. Gave his life he did to save our clan."`
- `"The Shield of the Ancients it was. Stolen by that father of all evil Hoskuld, it was. After Hoskuld Gunnar went. Tried to bring the shield back he did. Killed by Hoskuld he was."`

#### Dialogue — Suspicion / Hostility

- `"Pagan you mean? Believe you I do not... I think from the Hoskulds you are. I think a spy you are..."`
- `"Those dung-eating peasants who live on the other side of the Vale, they are."` (about Hoskulds)
- `"Prove it!"`
- `"A Zealan you are not. Welcome here you are not. Little enough food to support us there is."`

#### Dialogue — Rite of Passage

- `"Only stay if one of us you were. If a Zealan you would become."`
- `"Right you are, man enough to pass our test you are not!"`
- `"Called the Rite of Passage it is."`
- `"To do this, take the Passage Stone you must to the southwest corner of the vale. There made open to you the way will be. Then approach the Passage Plant you must. Reach into its very center you must. Pluck you must the fruit which grows there and here bring it you must."`

#### Dialogue — Missing Girl / Passage Stone

- `"Ah, now a mystery that is. The last person to attempt the test it seems, disappered she did... Found her body half-submerged in the shallow lake to the east of here we did. Missing the Passage Stone was. The Hoskulds killed her I believe, and the Stone they took."`
- `"Crushed almost beyond recognition her head was. Set upon her they must have when for a drink she stopped. Beat her with stones they did. Those lowly, cowards!"`
- `"Of course, tell who can why do anything such mouth-breathing, nose-picking idiots like the Hoskulds would?"`
- `"Well, watch your back. Murdering, theiving worthless animals they are."`

#### Dialogue — Poison Scene (from TESTPLAN.UNK)

- `"Oh my. Look good he does not. Try to take the test did he? Certainly not! Oh my, I think waking up he is."`
- `"Heard Thordis sent you here, I had. That scum-sucking torax whelp! Tell you the test was poisonous did she?"`
- `"No, of course not. A Hoskuld she is and the worst of them at that! Lying, mud eating, filth!"`
- `"No. In the days before the Great Cataclysm, given to teach our youngsters about their own mortality this test was. From the Ancient Ones the only antidote was. Now that reach the Ancient Ones the High Priestess cannot, afraid you are doomed I am."`
- `"Sad to say it I am. But give you the Zealan Mark I will. With it recognized as a full Zealan you will be, for the short time you have."`
- `"Well, speak to Ezrekal you can, but afraid I am no good it will do."`

#### Key Flags

`atliMet`, `atliName`, `atliJob`, `atliToldTest`, `testFromAtli`,
`gunnarSpokeStone`, `hoskuldSpokeStone`

---

### 3. Tyorvi — The Elder's Brother (Alcoholic Veteran)

**Files:** `LOST VALE/TYORVI.UNK` (primary, ~1550+ lines), `UNK files/UNK/TJORVI.UNK` (earlier, note spelling)
**Class:** `npcclass Tyorvi inherits Npc`
**Writer:** SHERI
**Schedule (Map 10):** Home (daytide/eventide/bloodwatch) at 11519,14079,64.
Stash (threemoons/firstebb/lastebb) at 13695,15743,64.

#### Look Barks
| Condition | Text |
|-----------|------|
| Dead | `"Tyorvi's mortal remains"` |
| Name+Job | `"Tyorvi, the Elder's brother"` |
| Name only | `"Tyorvi"` |
| Job only | `"Elder's brother"` |
| Unknown | `"man"` |

#### Dialogue — First Meeting (always drunk)

`"What? Talking to me are you? -hic- Tyorvi I am and... well. Well, well, well, what here we have? Now shomething, you are. Kinda funny he dresshes. Sure he does. Funny he talksh too. -hic- What are you, boy? A Pagan? Why bet I would thash's what you are. A Pagan. So, Mishter Pagan, your kind likesh Torax better than women, true it is? Ha, ha, ha, ha You know shomething, Pagan, take you out right now, where you stand, I oughta, shure I should, and...and I will...jusht as shoon as another drink I have."`

#### Dialogue — Hostile / Sends to Thordis

- `"Listen, Pagan, like to kill you where you stand, I would. But ordered any strangers be sent to her, Thordi has... Go and see Thordis you must."`
- `"Thordis? The Elder of Clan Hoskuld she is. Also my sister she is."`
- `"OUT! A Pagan you are!"`

#### Dialogue — Cliffs / PTSD

- `"A foolish man you are. Kind of like that I do. So try them you will. Perhaps accompany you I will. At least in vain our deaths will not be."`
- `"Too dangerous? Ha! How well that I know. Claimed my best friend it did and claimed me as well it should have."`
- `"In vain no one's death should be. No one's. Claimed my best friend those cliffs did when claimed me they should have...now, give them one more chance I can."`

#### Dialogue — Nightmares (drunk)

- `"Feeling alright? Corsh feeling alright I am. -hic- Only....hmmmmm, only -hic-..well, only a little to drink I have had. Drink enough I cannot, though. Drink enough to shtop the dreams I cannot. Every night they come. -hic-... alwaysh the same thing it is. The cliff....my pal.....oh, -sob- oh, I can't, I can't, too horrible it is."`
- `"Look good? Look good? -hic- How -hic- look good could I? Slept in -hic- monthsh I have not... Dropped my ax I have and reaching for it he does...then... loose from the wall his pin pulls, and oh Ancients, falling he is. Falling he is and reach him I can not! Screaming he is and screaming and screaming, Stop it won't!"`
- `"Have you been drinking again? ... Yes, drinking again I have been! ... So sleep without the dreams I can. alwaysh the same dream it is. Back on the cliffsh I am and trying to help me my friend is. -hic- Then, suddenly falling he is! Falling and screaming he is! Screaming my name he is and reach him I can not... then the screaming stopped...it just stopped. By the time down there I got, blood everywhere there was."`

#### Dialogue — Key to the Clouds

- (drunk) `"The talish....uh, telish...-hic-... the thing to get to the cliffs you mean? Why...-hic- why want that would you? Climb the cliffs would you? -hic- No, you should not, I think. -hic- Because if climb the cliffsh you do, then have the nightmaresh you will!"`
- (sober) `"Yes, have it I do. Want it do you? Why? Try to climb the cliffs will you? No, allow this I can not. Come upon you the curse will. The curse of the nightmares it is."`

#### Dialogue — Ezrekal

- `"Sure! A healer there ish! Ezrekal her name ish. in the southern part of the Vale she livesh. Fix anything she can...as soon as the Ancients return! Ha, ha, ha!"`

#### Key Flags

`tyorviMet`, `tyorviName`, `tyorviJob`, `tyorviDrunk`, `tyorviPissed`,
`iAmDrunk`, `toldOfDreams`, `tyorviDreams`, `agreeToClimb`, `spokeOnce`,
`toldOfPoison`, `sentToTyorvi`, `givenTea`

---

### 4. Thordis — Elder of Clan Hoskuld

**File:** `UNK files/UNK/THORDIS.UNK` (only version)
**Class:** `npcclass Thordis inherits Npc`
**Writer:** LISA
**Schedule (MapLostVale):** Field (daytide) at 12904,13976,64.
Home (other) at 11052,12724,64.

#### Random Barks — At Home (ambient)

```
"Curse Ingyald, the Ancient Ones should!"
"With Tyorvi, do what, can I?"
"Lonely, I am... The last Elder, shall I be."
"Why Ancient Ones, forsaken us, have you?"
"Do something for my poeple, I must!"
"No comfort, the shades offer. No answer, they have."
"Failed, I have. Lost, lost, we are..."
```

#### Random Barks — In Field

```
"Upon the plants, step not!"
"Withering, the poor crops are. More water, need, they do."
"Poor, our soil is..."
"Feed us for long, this will not."
"At these leaves, look!" / "Eating better than us, the insects are!"
"Ancient Ones, need more food, we do!"
"To haul water, need Tyorvi, I do."
"Find game soon, I hope Ragnar does." / "Last long, these crops will not."
"Every year, worse, the crops get."
"Lay down and die, I should. No hope, there is..."
```

#### Proximity Barks

```
"Hello?"
"Need what, do you?"
"Resting, I am. Away, go."
"Speak to anyone, wish, I do not!"
```

**Combat bark:** `"Help! Help! Shades, me, protect!"`

#### Dialogue — Poison Scene (from TESTPLAN.UNK)

- `"Oh my, terrible this is. Send you here Atli did?"`
- `"So cruel those Gunnar's are! Tell you did he poisonous the plant is and no antidote there is?"`
- `"As much I thought. In the days before the Great Cataclysm, given to teach our youngsters about their own mortality this test was. From the Ancient Ones the only antidote was."`
- `"Sad to say it I am. But give you the Zealan Mark I will."`
- `"Well, speak to Ezrekal you can, but afraid I am no good it will do."`

#### Key Ask Options

```
"How are you called?"
"What is it you do?"
"What is this place?"
"Tell me about the other people."
"Can you direct me to the Test?"
"Where is the Passage Stone?"
"The Gunnar's say you have the Stone."
"Why will no one speak to me?"
"How may I be accepted?"
```

#### Key Flags

`thordisMet`, `thordisName`, `thordisJob`, `thordisToldTest`, `toldMyTribe`,
`toldOthers`, `toldSelf`, `toldTyorvi`, `toldRagnar`, `toldAtli`, `toldHrodny`,
`toldIngyald`, `toldEzrekal`, `saidGrandmother`, `saidWomen`, `thordisSchedule`

---

### 5. Ragnar — Hunter, Clan Hoskuld

**File:** `UNK files/UNK/RAGNAR.UNK` (only version)
**Class:** `npcclass Ragnar inherits Npc`
**Writer:** not in Character List (added during development)
**Schedule (Map 10):** Home (eventide) at 14207,13055,64.
Field (all other periods) at 13695,19071,64.

#### Look Barks
- `"Ragnar"` or `"Man"`

#### Dialogue — Introduction

- `"Ragnar called I am. Never seen one such as you have I. Where come from do you?"`
- `"Do here? Hard to understand you are. Strangly you speak. But try to answer your question I will. A hunter I am. Bring back food for the clan I do. When find it I can."`

#### Dialogue — Hunting / Old Days

- `"Not easy it is. Dry this land is...and barren. Little game to hunt there is. Wild torax, mainly. Remember stories I do about the old days."`
- `"Bigger than a torax they were. Out of their head two horns grew. Spread as wide as your arms, the horns did. Tined the horns were, and as sharp as knives. Kill you as quick as look at you, they would."`

#### Dialogue — The Vale / Clan Conflict

- `"What to tell there is? A barren, dry place it is. Little game to hunt there is."`
- `"Well, not a vengful man I am. Forgiven all is."`
- `"Peacful you are, but peaceful with Gunnar clan? If peaceful with Gunnar clan you are, then at war with Huskold clan you are."`
- `"Then a fool you are. No disrespect do I mean, but be peaceful with all a man cannot be."`
- `"How naive you are. The body of a grown man you have but in it the mind of a child there is."`

#### Key Flags

`ragnarMet`, `ragnarName`, `ragnarPissed`, `sentToRagnar`, `ragnarToldStone`

---

### 6. Hrodny — The Inventor (Clan Gunnar)

**File:** `UNK files/UNK/HRODNY.UNK` (only version)
**Class:** `npcclass Hrodny inherits Npc`
**Writer:** LISA
**Schedule (MapLostVale):** Work (daytide) at 17506,22354,64.
Home (other) at 17686,21806,64.

#### Look Barks
- `"Hrodny, the Inventor"`, `"Hrodny"`, `"Inventor"`, `"woman"`

#### Random Barks — At Home

```
"Hello?"
"Why here, are you?"
"Hungry, I am."
"Fools, they are! Help them, I could!"
"Work, it should..."
"Understand it, I do not!"
"If only listen, they would!"
"Starve, we need not!"
```

**Combat bark:** `"Shades, you, I summon! Help!"`

#### Key Flags

`hrodnyMet`, `hrodnyName`, `hrodnyJob`, `hrodnySchedule`

---

### 7. Ingyald — The Brewer (Clan Gunnar)

**File:** `UNK files/UNK/INGYALD.UNK` (only version)
**Class:** `npcclass Ingjald inherits Npc` (note: class spelled "Ingjald", flags say "ingyald")
**Writer:** LISA
**Schedule (MapLostVale):** Still (daytide) at 19935,19775,64.
Home (other) at 18175,20639,64.

#### Random Barks — At Home

```
"A drink, do you wish?"
"Hrodny brings food soon, I hope."
"Ask Atli for more wood, tomorrow, I must."
"Hmmmm. Seen Tyorvi today, I have not."
"Tired, I am. To sleep early, go, I should."
"Gone down again, the water has..."
"Cruel, the gods are. Left us to starve, they have."
```

#### Random Barks — At Still

```
"Hello?"
"To buy my brew, come, you have?"
"A new batch, this! Come taste!"
```

**Combat bark:** `"Help! Help! Shades, protect me!"`

#### Key Flags

`ingyaldMet`, `ingyaldName`, `ingyaldJob`, `ingyaldSchedule`

---

### 8. Zealan Child

**File:** `LOST VALE/ZCHILD.UNK`
**Class:** `typeclass TypeZealanChild1 inherits pesantBoy`

#### Look Barks
- Dead: `"dead child"` | Alive: `"child"`

#### Combat Barks
- `"Mama!"` | `"Ahhh! Don't hurt me!"`

#### Conversation — Full Dialogue Tree

Child may refuse: `"Know you I do not. Told me never to talk to strangers my mama did. A stranger you are. Talk to you I can not."`

If willing, a charming question chain:

| Child asks | Avatar choices |
|------------|---------------|
| `"What called are you?"` | name / `"Avatar"` |
| `"Where come from do you?"` | another world / a town |
| `"What do there did you?"` | fought monsters / helped people / baked bread |
| `"Why so tall are you?"` | born this way / troll stretched me |
| `"How get here did you?"` | walked / boat / big red hand dropped me |
| `"Wear those funny clothes always do you?"` | various answers |
| `"Why big and brown are toraxes?"` | → punchline: `"Because then kith they would be."` |

---

## II. Key Items and Objects

---

### 9. Lord British — Message Object

**File:** `UNK files/UNK/LORDBRIT.UNK`
**Class:** `typeclass TypeLordBritish inherits Item`
**Writer:** ANDREW

#### Full Message (bark)

`"Avatar, I have found a portal through which I can speak, yet I can neither see nor hear thee. Nystul, my magiciain and trusted friend, has managed to pierce the Guardian's dark veil to locate thee and send this message. Yet the tether that binds to this world grows threadbare and I fear my time here is short. Seek the counsel of the wise man known as Mythran. I feel that he is near thee and can offer much help. Ask him of the race that once thrived upon the land that is now your prison. Through him thou canst find the ancient race and earn their help, for Pagan is now their prison too. Journey with great haste to Mythran. Only with his aid canst thou escape. Farewell, Avatar and please hurry. Britannia is in great need of thee..."`

**Flags:** `lbStarted`, `lbDone`

---

### 10. Monster Skull — Message Artifact

**File:** `LOST VALE/MONSKUL.UNK`
**Class:** `typeclass TypeMonskul inherits Item`
**Look bark:** `"Strange skull"`

#### Message Text

`"To my brothers, Odion and Apathas, and my sister, Amoras, A great emergency has occured in our Vale. As our beloved Priestess prepares herself for the ceremonies, the Titans draw near. I fear they plan to attack! You must return to us quickly as only united can we hope to stop them. Even now I can feel the very ground trembling. Felicitas, Timyra and I will go now to the Temple and attempt to hold them off until you arrive. Hurry, my siblings, our time is short!"`

> **Note:** Names the six Ancient Ones: Felicitas, Timyra, Odion, Apathas, Amoras,
> and the unnamed author (Doloras, by elimination).

---

### 11. Shield of the Ancients (AOFrizbee)

**File:** `UNK files/UNK/ZEALSHLD.UNK`
**Class:** `typeclass TypeAOFrizbee inherits Item`

#### Look Barks
| Frame | Text |
|-------|------|
| 2 (restored) | `"Ceremonial Shield of the Ancients Ones"` |
| 3 (defender) | `"Defender"` |
| Other (broken) | `"broken shield"` |

**Dev comment:** `"Named by Mel, thank you"`

---

### 12. Potions

**File:** `LOST VALE/POTION.UNK`
**Class:** `typeclass TypePotion inherits Item`

| Frame | Effect | Bark |
|-------|--------|------|
| 0 | Empty | `"it's empty..."` |
| 1 | Health (overdose) | `"Augh!"` |
| 1 | Health (healed) | `"I feel much better!"` |
| 2 | Mana | `"I have regained power!"` / `"Yummm..."` |
| 3 | Minor health | `"I feel better!"` |
| 5 | Protection | `"I feel like fighting!"` |
| 6 | Sleep | `"Zzzzz..."` |

---

### 13. Simple Items

| File | Class | Look | Notes |
|------|-------|------|-------|
| ABACUS.UNK | TypeAbacus | `"abacus"` | Counts obsidian coins |
| BEDROLL.UNK | TypeBedroll | `"bedroll"` | `"Rest for how many periods of time?"` / `"This is no time to rest!"` |
| FEDORA.UNK | TypeFedora | `"Fedora"` | Easter egg (Indiana Jones) |
| BULLWHIP.UNK | TypeBullwhip | `"Bullwhip"` | Easter egg (Indiana Jones) |
| EALOGO.UNK | TypeEaLogo | `"earthen shape"` | Easter egg (EA branding) |

---

## III. Puzzles and Mechanics

---

### 14. Passage Test (PLNTST)

**File:** `LOST VALE/PLNTST.UNK`
**Class:** `eggclass EggPlantTest inherits Egg`
**No dialogue.** Checks for `TypeBushKey`; destroys mushrooms with air titan effects.

---

### 15. Poison Plant / Rite of Passage (TESTPLAN)

**File:** `LOST VALE/TESTPLAN.UNK`
**Class:** `typeclass TypePoisonPlant inherits Item`
**Look bark:** `"Strange plant"`

#### Poison Barks (ongoing, rotating)

```
"I haven't felt this bad since Lydia poisoned me!"
"I think I'm feverish!"
"I don't feel good."
"Oh, my stomach!"
"My head really hurts."
"I feel terrible!"
"All my joints hurt!"
"I feel so weak!"
"I've never felt so bad!"
"I feel sick."
```

Sets `haveMark = true`, `avatarPoisoned = true`, `firstPoisoned = true`.
Poison does 1 damage every 10000 ticks; every 3 hits reduces STR and DEX by 1.

---

### 16. Candle Trick (CANTRK)

**File:** `LOST VALE/CANTRK.UNK`
**Class:** `eggclass EggCandleTrick inherits Egg`
**No dialogue.** Solution: candles 1=off, 2=on, 3=off, 4=off, 5=off, 6=on.
**Flags:** `candleOne`-`candleSix`, `candlesCorrect`, `monolithSucks`

---

### 17. Magnetic Puzzle (MAGNET)

**File:** `LOST VALE/MAGNET.UNK`
**Class:** `eggclass EggMagnet inherits Egg`
**No dialogue.** When candles incorrect, confiscates ALL magic items from Avatar.
Items deposited at 15615,19839,120.

---

### 18. Shield Restoration / Shade Ceremony (SHADES)

**File:** `UNK files/UNK/SHADES.UNK`
**Class:** `eggclass EggShades inherits Egg`

This is the climactic reunification scene. Teleports Atli, Thordis, and Ezrekal
to specific coordinates. Requires Shield of the Ancients in Avatar's backpack.

#### Ezrekal's Dialogue

```
"At fault who is, I care not! Over, the time for dissension is!"
"Our offering of faith, the gods await. To me, heed you must! Old grievances, set aside, you must!"
"The hero, I am not. Listen to me, they will not. Persuade them, you must."
"Without the faith of my people, do nothing, I can! With respect, to them, speak. Remember... Upon this, your life depends."
"Bring the sacred shield, you must! Without it, return not! You only hope, it is!"
"Supplicant, who healed wishes to be, the shield, bring forth!"
"The combined faith of all our people, I must have..."
"Silence!"
"Of breaking tradition, each other, you accuse. This, tradition is!"
"Silent before me, you will be! High Priestess, I am! Your respect, will I have!"
"Ancient Ones, hear me! Sundered, our people have been. To their own gods, blind. To end our quarrels, resolved we are!"
"Now, reunited, we are. To fulfill our destiny, ready we are! Our hearts and souls, made whole be!"
"Yes! Yes! Knew, done it could be, I did!"
"At my feet, grovel you should not. Wisdom late learned, wisdom still is."
"Rise! And into their new future, lead your people."
"Then healed, you shall be! Passed your test, your have."
"Sorry, I am. The poison, rid I can. Restore your lost health, only the gods can. To them could you go, if open, the temple was."
```

#### Atli / Thordis Squabble

```
Atli:    "With Hoskuld's clan, all the trouble lies!"
Thordis: "Liar! Gunnar's clan, tradition broke!"
Atli:    "Hoskuld, the shield stole! Upon your head, the blood of Gunnar is!"
Thordis: "Gunnar, the shield stole! Upon your clan, the blame lies!"
Atli:    "Hoskuld, the thief was! Murdered innocent Gunnar, he did!"
Thordis: "Gunnar, the murderer was! The stolen shield, Hoskuld did seek!"
Atli:    "Control your own brother, you cannot! Yet of my place, tell me you would!"
Thordis: "If not for Ingyald, control him, I would not have to! Encourage Ingyald in this, you do!"
Thordis: "Because blasphemy Hrodny speaks, disfavor us the gods do!"
Atli:    "To the gods, one woman's opinion is what?! Beneath their feet, dust she is!"
Thordis: "No wonder, disfavored are you! Dishonor women, you do!"
```

#### Shade of Hoskuld

```
"The shade of Hoskuld, I am."
"Together, Gunnar and I, the realm of the gods, we sought."
"The power to restore our sacred shield, we sought, our clans to reunite. By foul monsters, slain we were."
"Long from the vale, lost have I been. Our story to tell, denied have I been."
```

#### Shade of Gunnar

```
"In life, Gunnar, was I named. And fast friend to Hoskuld, I was."
"But now grieved, I am. What we sought, only worsened we did."
"Felled, we were. And with us, our news did die."
"Trapped by the Pagan Titans, have our gods been. Deny us, they did not."
"Sealed, I fear they are, within our temple. Free them, you must!"
```

#### Post-Ceremony — Reconciliation

```
Thordis: "Wise Priestess, wrong we were, to doubt you. In paying you proper homage, failed we have. Unworthy am I, upon you to look."
Atli:    "You we blamed, for the loss of the gods' favor. But our rivalry and scorn, the cause truly was."
Atli:    "Whole, it is! Forgiven us, the gods have!" / "Grow again, our crops shall!"
Thordis: "Now redeemed, shall we be! Fertile once more, shall our land be!" / "Flow again, the water will!"
```

#### Avatar Ask Options (this scene)

```
"Can't you two get along!?" / "Let's be reasonable!"
"Please cooperate..." / "You two are insufferable!"
"Yes, Priestess." / "No, it is mine now."
"I'm sorry. Please heal me." / "Fine!"
"Please, High Priestess." / "No, thanks anyway."
"Here are both pieces, Priestess." / "I feel better... But I'm still so weak!"
```

**Flags:** `doneShades`, `inShadeScene`

---

### 19. FREE.UNK — God-Freeing Trigger Logic

**File:** `LOST VALE/FREE.UNK` (primary), `UNK files/UNK/FREE.UNK`
Contains `askYesNo()` utility (with German "Ja"/"Nein", French "Oui"/"Non")
and trigger/flag logic for the Ancient Temple sequence.
**Flags:** `godsFree`, `godsSpoke`, `templeOpen`, `ezToTemple`, `getPowerAO`

> **Note:** Has the trigger LOGIC but NOT the cinematic dialogue for the god-freeing
> ceremony. This is one of the confirmed MISSING segments.

---

### 20. Air Spell System (AIRSPEL)

**File:** `UNK files/UNK/AIRSPEL.UNK` (~28K, 10 spell functions)
New air magic for the expansion. No dialogue.

---

### 21. Changtar (Shrink/Grow)

**File:** `UNK files/UNK/CHANGTAR.UNK`
Processes `makeAvatarTiny()` and `makeAvatarBig()`. No dialogue.

---

## IV. U8 Modified Base Game NPCs

11 existing NPCs received modifications to integrate LV hooks:

| NPC | File | Nature of Modification |
|-----|------|----------------------|
| Aramina | U8/ARAMINA.UNK | LV flag checks added to dialogue tree |
| Bentic | U8/BENTIC.UNK | LV flag checks added |
| Cyrrus | U8/CYRRUS.UNK | LV flag checks added |
| Darion | U8/DARION.UNK | LV flag checks added |
| Jenna | U8/JENNA.UNK | LV flag checks added |
| Kilandra | U8/KILANDRA.UNK | LV flag checks added |
| Mordea | U8/MORDEA.UNK | LV flag checks added |
| Salkind | U8/SALKIND.UNK | LV flag checks added |
| Stellos | U8/STELLOS.UNK | LV flag checks added |
| Stratos | U8/STRATOS.UNK | LV flag checks added |
| Torwin | U8/TORWIN.UNK | LV flag checks added |
| Xavier | U8/XAVIER.UNK | LV flag checks added |

Additional U8 files:
- `SGBOOK.UNK` — In-game books (Saga of Bone Crusher, Enemies of Tenebrae, "What the Fish Tell Me")
- `TEMP.UNK` — Test/development file
- `LES1.UNK` — Easter egg: `"Are you sure? The Yugo is a heck of a deal!"`
- `LES4_1.UNK`, `LES4_4.UNK` — Lesson/tutorial scripts
- `ORLOK1.DOC`, `RHNTXT.DOC` — Design notes

---

## V. Global Flags Summary

### From FLAGS.UNK (47 LV-specific flags)

**Main Plot:** `avatarPoisoned`, `climbedCliffs`, `ezToTemple`, `shieldFixed`,
`firstPoisoned`, `zealanMark`, `hasBag`, `godsFree`, `attemptedCliffs`,
`haveMark`, `templeOpen`, `sentToTyorvi`, `plantScene`, `endOfPlantScene`, `lbSpoke`

**Puzzle:** `candlesCorrect`, `monolithSucks`, `candleOne`-`candleSix`,
`ActivateAirPuzzle`, `limitTornado:3`

**Tyorvi subplot:** `toldOfDreams`, `tyorviDreams`, `givenTea`, `hasTea`,
`givenRoot`, `justGotRoot`, `hasRoot`, `toldAboutAddiction`

### From ZZVFLAGS.UNK (additional)

**Position storage:** `avX:16`, `avY:16`, `avZ:16`, `avMap:16`
**World state:** `beganConvo`, `godsSpoke`, `stormsOn`, `allColumnsDestroyed`
**NPC tracking:** `spokeOfThordis`, `likeThordis`, `toldSelf`, `toldTyorvi`,
`toldRagnar`, `toldAtli`, `toldHrodny`, `toldIngyald`, `toldEzrekal`,
`saidGrandmother`, `saidWomen`
**Elemental columns:** `WaterColumnDestroyed`, `FireColumnDestroyed`,
`EarthColumnDestroyed`, `AirColumnDestroyed`
**Items:** `bagHas*` (reagent bag flags), `tokens`
**Puzzles:** `pedZeroDone`, `pedOneDone`, `pedTwoDone`, `doneOne`-`doneFinal`

---

## VI. Version Differences (LOST VALE/ vs UNK files/)

| File | Difference |
|------|-----------|
| EZREKAL | LV version adds German translations, Tyorvi dream/elixir subplot, expanded Shield explanation |
| TESTPLAN | LV version has complete poison scene with Atli/Thordis branching; U8 version simpler |
| TYORVI/TJORVI | Spelling change; TYORVI (LV) is 71KB vs TJORVI (UNK) 14KB — major expansion |
| THORDIS | Only exists in UNK files/ — either final version or still in revision |
| MONSKUL | LV version marked "READY TO TRANSLATE F & G 8-11-94" |

---

## VII. Confirmed MISSING Dialogue (Red X on schedule)

| Segment | Writer | What we know | What we have |
|---------|--------|-------------|-------------|
| **Mythran LV dialogue** | Andrew | Tells of Zealans, Galjeron, double doors | Lord British message mentions Mythran; no Mythran usecode |
| **Hunter NPC** | Brian M. → Sheri | Female Hunter, Clan Hoskuld, personality from Character List | Nothing — no usecode file |
| **Elemental columns** | Brian M. | 4 pillar destruction sequences | Flags only: `WaterColumnDestroyed`, etc. |
| **Cloud Cliffs** | Brian M. | Climbing traversal, NPC reactions | Flags only: `climbedCliffs`, `attemptedCliffs`, `agreeToClimb` |
| **AO Scene** | Andrew | God-freeing ceremony | `FREE.UNK` has trigger logic, no cinematic dialogue |
| **End-game** | none | Water flows, plants return, Bag of Reagents | No usecode exists |

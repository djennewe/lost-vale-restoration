# Playtest 2026-09-02 — the quest chain from Ragnar's referral to Ezrekal's door

Continuation of the exit test begun on 2026-09-01. One continuous run, cheats
off, no `MainActor::teleport`: the debugger was used only to *read* state
(`objectInfo`, `UCMachine::getGlobal`) and to detach. Every metre was walked
or climbed.

Start: `cp7c-ragnar-referral.sav` (Ragnar's village, map 10).
End: `cp29-spare-key-at-chest.sav` — the chest is unlocked and open, and
empty: the Tiny Tar was never placed in the world.

## Verdicts

| id | test | verdict |
|---|---|---|
| E | Ragnar's referral tree reaches the Passage Stone | **PASS** |
| E-a | the `No, I don't.` label collision closes the Stone thread | **CONFIRMED DEFECT** (known quirk, now seen live) |
| E-b | `Her body was eaten?!` is a dead option | **CONFIRMED DEFECT** (known quirk, now seen live) |
| F | the router plots courses through water | **HARNESS DEFECT — FIXED** (two deaths) |
| G | Ragnar's bag spawns at the 1994 coordinate and can be taken | **PASS** |
| G-a | the bag is takeable from ground level | **FAIL** — needs the dais climb |
| H | the Passage Test grants the Mark and the poison | **PASS** |
| H-a | the test-grounds terraces are walkable | **FAIL** — each riser needs a climb |
| I | Ezrekal accepts a marked Avatar | **PASS** |
| I-a | Ezrekal can cure the poison | **correctly refuses** (cure is the Sacred Circle) |
| J | Tyorvi and Ingyald talk, and Tyorvi tracks what Ezrekal said | **PASS** |
| K | `ingyaldMet` / `ingyaldJob` / `tyorviMet` set | **PASS** |
| L | Ezrekal delivers the cliffs and the Key to the Clouds | **PASS** |
| M | Tyorvi's Key option opens on `sentToTyorvi` + `haveMark`, and he refuses | **PASS** |
| N | the Passage Test returns its witness NPC home | **FAIL — new defect** |
| N-a | the stranded witness still talks correctly where she stands | **PASS** |
| O | Ezrekal's root errand runs and sets `givenRoot` / `hasTea` | **PASS** |
| P | Tyorvi takes the elixir and speaks the Key handover | **PASS** |
| P-a | the Key to the Clouds reaches the player (old build) | **FAIL — root cause found** |
| Q | with `CONTAINER_FAMILY` pinned, the Key lands in the pack | **PASS** |
| R | the Cloud Cliffs key-gate actually gates the path | **FAIL — bypassable** |
| S | the cliff climb accepts the Key and sets `climbedCliffs` | **PASS** |
| T | base → summit → Cloud City, on foot | **PASS** |
| U | both shield halves taken in Cloud City | **PASS** |
| V | the Sacred Circle ceremony restores the shield and cures the poison | **PASS** |
| W | the ceremony leaves the camera off the Avatar; he freezes | **DEFECT — recoverable** |
| X | the Ancient Temple's inner sanctum is reachable at full size | **correctly refuses** — the crack needs Hrodny's Tiny Tar |
| Y | Hrodny opens her temple thread after the ceremony and spawns the chest key | **PASS** |
| Y-a | the key bag lands on the ground, not 64 units above it | **PASS** — the lv-patched height fix works |
| Z | the key reaches the player | **PASS** |
| Z-a | Hrodny's locked chest can be clicked | **FAIL — buried; FIXED and verified in-engine** |
| Z-b | `trek.py` stops when a teleport changes the map | **HARNESS DEFECT — FIXED** (it killed the Avatar once) |
| Z-c | any chest in the game can be opened | **ENGINE DEFECT — FIXED** (intrinsic 254 stubbed to `I_true`) |
| Z-d | the key unlocks Hrodny's chest | **PASS** |
| Z-e | the Tiny Tar is in the chest | **FAIL — it is nowhere in the world** |

## E — Ragnar to the Passage Stone (PASS)

The referral tree, navigated organically:

    Atli sent me to you. → Atli admires you. → I believe that he is sincere.
      → He spoke of you and Hrodny. → He said you could help me.
      → Do you know of the Passage Stone? → Yes, I do.
      → Why do you not go there? / Tell me of the legends.

`Why do you not go there?` is the quest-critical leaf: it sets
`ragnarToldStone` and pops the bag. `Tell me of the legends.` opens the
Gunnar-murder lore (`Why did the Gunnars kill her?`, `How was she killed?`).

### E-a — the `No, I don't.` collision (CONFIRMED DEFECT)

Answering **No** to `Do you know of the Passage Stone?` produces the *Hrodny*
rebuke and ends the conversation:

> Blind are you? Stupid? Wonderful she is. Beautiful and wise she is!
> Appreciate this you can not, then waste my time with you I will not!

Two cases share the label `No, I don't.` — `lv-patched/RAGNAR.UNK:663` (the
Thordis-crush pair) and `:962` (the Stone pair) — and the first shadows the
second. The `:962` case is doubly dead: its label is `No, I don't` with the
period missing, so it could never match the option the askList adds. The file
header already lists this under "Known 1994 quirks deliberately NOT fixed";
this is the first time it has been seen in the engine.

Player-visible consequence: the wrong answer to a Stone question gets a
non-sequitur about a woman and closes the thread. Recoverable — re-open the
conversation and the askList resets — but a first-time player has no way to
know that. Screenshot `E11-passagestone-no.png`.

Note the question is genuinely ambiguous in the UI: Ragnar's bark is
*"Yes, seek it do you?"*, so **Yes, I do.** answers *his* question, not the
menu line above it.

### E-b — `Her body was eaten?!` is dead (CONFIRMED DEFECT)

The askList adds `Her body was eaten?!`; the case is `Her body was eaten?`
without the `!`. Clicking it produces no bark, consumes nothing, and the
option stays on the menu for the rest of the conversation. Also already
listed as a known quirk. Screenshot `E10-passagestone-ask.png` shows the
menu carrying it after the click.

## F — the router drowned the Avatar twice (HARNESS DEFECT, FIXED)

`pathfind.py` routed a 16,000-unit walk straight across the vale's lake.
`exact_reach` records an `SI_SEA` tile as *support* (it is `SI_SOLID`), and at
level ≤ 0 a support alone makes a cell standable — the engine agrees the
Avatar can step there, and then he drowns. Both deaths were hp 30 → 0 inside
one poll interval:

| death | at | cause |
|---|---|---|
| 1 | (15392, 14788) | route crossed 60 sea tiles at x≈15400 |
| 2 | (13672, 20556) | route hugged the shore at y=20543; the walker's burst drifted the 77 units into water at y≤20479 |

Screenshot `F-drowned-lake.png` — the ripple where he sank.

Fixed in `tools/playtest-linux/pathfind.py`:

- **`DryMixin`** subtracts every `SI_SEA` top from the standability mask.
  On by default; `--allow-water` restores the old behaviour.
- **`--water-margin` (default 128)** widens each sea box by a body width
  before subtracting, so a route cannot hug a shoreline. Death 2 needed
  this; the sea-only fix was not enough.
- **`--step-z`** exposes the model's per-step z limit (was hard-coded 8).

With the margin the router picked a corridor 128 units further inland and the
same leg walked at hp 30 throughout.

## G — Ragnar's bag (PASS, with a caveat)

The bag exists exactly where 1994 puts it:

    Item 1754 (class Container, shape 637) (uc: BAG), (16447, 25727, 64)
    Container vol: 2/32, total weight: 20, items: 1

`build_ragnar_cache_ruins()`'s dais holds it visibly (`G1-ruins-arrival.png`).

### G-a — not takeable from the ground (FAIL against the builder's comment)

`build_map_10.py` says "the Avatar can walk right onto the crown to take it".
He cannot walk onto it, and from ground level the drag is refused — the item
snaps back (log shows `Dragging item 1754` → `Dropping object 1754`, no
`Dropped item in backpack`, and `objectInfo 1754` still reads (16447, 25727, 64)).

`exact_reach` agrees: the drop cell has **no standable level at any z**. The
dais reads as

| x band (y 25692-25756) | level |
|---|---|
| 16684-16748 | 24 |
| 16556-16620 | 48 |
| 16492 | 56 (the crown) |

Each 24-unit riser needs a climb; the engine's `scanForValidPosition` only
searches ±8 in z. From z=48 the drag succeeded — `Dropped item in backpack`,
Avatar total weight 20 → 40. Screenshot `G2-bag-taken.png`.

## H — the Passage Test (PASS)

The corridor south from Moriens Ruins to the test grounds rises z=0 → 24 → 48
→ 64. `build_test_grounds()` calls this "an on-foot link… so the whole climb
stays within the STEP_Z=24 the walkability model enforces". **It is not an
on-foot link.** Each riser leaves a 32-unit band where nothing is standable
(measured at x=12800: z=0 ends at y=28160, z=24 begins at y=28200), and U8
auto-steps only ±8. Three held-SPACE climbs took them.

The third climb ended at **(13055, 30079, 64)** — `MAP10_SCENE_COORDS[0]`, the
scene's own avatar-teleport coordinate. The PLNTST egg hatched on approach,
the whirlwind and plant pops played (`H1-passage-test.png`,
`H2-test-after.png`), and afterwards:

| flag | bit | value |
|---|---|---|
| `ragnarToldStone` | 1098 | 1 |
| `haveMark` | 1041 | 1 |
| `avatarPoisoned` | 1028 | 1 |
| `firstPoisoned` | 1034 | 1 |

The Passage Stone was consumed: the carried bag went from `vol 2/32, weight
20, items 1` to `vol 0/32, weight 10, items 0`. That matches
`test_uc_plntst.py`'s "haveMark NOT set without the stone" — the stone is the
price of the test.

No Mark *item* appears in the pack (Avatar weight 30 = own 20 + empty bag 10).
`PLNTST.UNK` guards the grant with `if give(Avatar:Referent,TypeZealMark,…)`
and then sets `haveMark` unconditionally, so the flag is the quest-visible
grant either way — and every gate downstream reads the flag.

## I — Ezrekal accepts the marked Avatar (PASS)

On 2026-09-01 an unmarked Avatar got *"A PAGAN it is! Filth! Wretch! Slime!
Away with you!"*. With the Mark she opens a conversation (`I1-ezrekal-marked.png`):

> Ezrekal my name is. The mark of th' Zealans upon you I see. Funny, not like
> a Zealan you look. Different you look, different you speak. If not a Pagan
> you are.

and, after `I am from Britannia.` → `Yes, I am from outside.`:

> Oh, my! And not a Pagan you are? Well, of course not, the Mark you bear!

That is the step-9 → step-10 gate demonstrated in both directions.
Screenshots `I2-ezrekal-sees-mark.png`, `I3-mark-you-bear.png`.

Her thread then opens the Ancient Ones / Great Cataclysm history, and
`Can you help me?` narrows to a single option — **`I have been poisoned.`**
(`I4-poisoned-option.png`) — which is the poison arc surfacing exactly where
the source says it should.

### I-a — she correctly cannot cure it

> That I cannot do. But begin preparations for your funeral right away I will.

The cure is `SHADES.UNK:429`, at the shield-restoration ceremony. Her refusal
is the design, not a defect.

## J — Tyorvi and Ingyald (PASS)

Tyorvi (NPC 115) opens in character and drunk:

> What? Talking to me are you? -hic- Tyorvi I c... and... well. Well, well,
> well, what here we have? Now shomething, you are. Kinda funny he dresshes.

and states his lever — *"another drink I have. Another drink, What I need
that is."* (`J2-tyorvi-drunk.png`).

Ingyald (NPC 112) is at (20996, 6644) and his `What do you do?` — *"A brewer,
I am. Make potions for sweet dreams, I do."* — sets both flags the quest
reads: `ingyaldMet` (bit 1126) and `ingyaldJob` (1128) both read 1 afterwards,
alongside `tyorviMet` (1083). Screenshot `K1-ingyald.png`.

Returning to Tyorvi, his menu had grown **"I have spoken to Ezrekal."**
(`J3-ezrekal-referral.png`) — cross-NPC state again, as with Ragnar's
"Atli sent me to you." His reply, *"So, still alive you are. Hmmm. Stronger
than I thought you were, you are"*, branches on what she said, and the two
options offered matched exactly what she had actually told me (poison,
funeral) — the cliffs option was correctly absent, because at that point she
had not mentioned them.

## L — Ezrekal to the cliffs and the Key (PASS)

The Cloud City is not reachable from her obvious threads. The path is:

    Can you help me? → I have been poisoned. → But I'm dying!
      → Prepare my funeral?! → I don't want a funeral!
      → You said the Ancient Ones were gone!
      → I don't want to be an undead!        ← this is what opens it
      → Cloud City? → How?! How can I be healed?
      → Where is the Cloud City? / Tell me of the Shield.
        / How can I awaken the Ancients? → Key to the Clouds? / How was it lost?

`I don't want to be an undead!` is the branch that adds the pair
`Cloud City?` + `Remnants of the Water Titan?` (`L1-cloud-city-opens.png`).
Nothing signposts it: the two obvious options (`I want to be healed!` and
`Those cannot be Zealans!`) both loop back to the funeral speech.

Then:

> See the great cliffs to the Northwest of our vale can you? At the top of
> those cliffs the fabled Cloud City lies. (`L2-cliffs-northwest.png`)

> [The Key] allows the bearer to be transfered safely across the lava it
> does. Built it was with what little magic the High Priestess has left.
> (`L3-key-to-clouds.png`)

She also delivers the Shield's loss — the two families, the boy sent to
retrieve it who never returned, and the feud that followed — which is the
shield-halves arc's own origin, and the Casero story of the first High
Priestess carried to the Cloud City.

## M — the Key gate on Tyorvi (PASS)

`sentToTyorvi` (bit 1047) read 1 straight after Ezrekal's cliffs thread, and
on the next visit Tyorvi's menu carried **"Do you have the Key to the
Clouds?"** (`M1-key-option.png`) — the guard is
`if (sentToTyorvi = true) and (haveMark = true)`, and both were set.

He admits to it and refuses (`M2-key-refused.png`):

> Yes, have it I do. Want it do you? Why? Try to climb the cliffs will you?
> No, allow this I can not. Come upon you the curse will. The curse of the
> nightmares it is.

`Tell me of these nightmares.` then plays his whole trauma — the friend who
fell from the cliffs, the screaming that stopped, the blood he could not
stop, and the drinking that has lately stopped working (`M3-nightmares.png`).
It ends in `exitConvo()`.

The handover itself (`May I have the Key to the Clouds?`, TYORVI.UNK:2142)
sits behind a second gate, `hasTea` (bit 1062, currently 0) — Thordis's
remedy for the nightmares. **That is the next leg**: Thordis is NPC 106 at
(6144, 6656), the far west of the vale.

## N — the Passage Test strands Thordis 20,000 units from home (NEW DEFECT)

`PLNTST.UNK`'s hatch teleports a witness to the test grounds:

    if thordisToldTest = true
        Atli.teleport(12927,29823,64, …)
    else
        Thordis.teleport(12927,29823,64, …)

and **nothing teleports the witness back.** The scene's own header note says
only that the *Avatar* is not sent home.

Because this run found the test on its own (Thordis never told me about it,
so `thordisToldTest` was 0), the else-branch fired and Thordis was moved.
Hours later `objectInfo 106` reads

    Item 106 (class Actor, shape 707) (uc: PESANT1), (13047, 30213, 64)

— still on the SW plateau, wandering near where the scene dropped her, about
20,000 units from her village spot at (6144, 6656).

She talks there quite normally — walking back up onto the plateau and
striking her got her reacting to the test she had just watched: *"So cruel
those Gunnar's are! Tell you did he poisonous the plant is and no antidote
there is?"* (`N1-thordis-stranded.png`). So the displacement is silent: no
dialogue anywhere acknowledges that she is 20,000 units from home.

Only `SHADES.UNK` (the Sacred Circle ceremony, quest steps 14-15) ever
teleports her home, and that is many steps later. Any step in between that
expects Thordis in her village is looking in the wrong place.

(I first read her as blocking the Key — she is not. `hasTea` is written in
`EZREKAL.UNK:3367`, at the end of an errand for a root. The stranding is
still real; it is just not on the Key's critical path.)

Fix candidates: send the witness home at the end of the hatch, or place the
witness with `createNear` instead of moving the real NPC. Either is a
one-line change in `lv-patched/PLNTST.UNK`; which one is Douglas's call,
since the real NPC is what makes the scene mean anything.

## O — Ezrekal's root errand (PASS)

    Ezrekal: I would speak to you of Tyorvi. → He needs help.
             → He has another problem. → He has nightmares.
      (her grandmother's bitter tea; the root grows "by the standing stones")
    the root: item 7611, shape 399 (uc: ETHEREAG), at (21376, 16640, 0)
      — exactly `MAP10_ROOT_XY`; dragged into the pack, log
      `Dragging item 7611` → `Dropped item in backpack`
    Ezrekal: I have found the root. → "Ah, good that is. Take it I will
             and brew the tea I will."  → givenRoot
    (close and re-open — the elixir option is added at conversation entry)
    Ezrekal: Have you made the elixir? → hasTea (bit 1062) reads 1

Two documented repairs are confirmed live here. The **period fix** at
`EZREKAL.UNK:3161` (`I have found the root!` → `.`) dispatches — the 1994
option could never have matched. And the **E2 gate change** (keying the
elixir option on `givenRoot` alone rather than `justGotRoot`) offers it after
a conversation restart, which is exactly the state the old gate lost
(`O2-elixir-option.png`).

The offered `I have found the root.` is *not* removed after it dispatches, so
it sits on the menu afterwards — one more of this file's removal-side
mismatches, cosmetic here.

## P — the Key handover speaks, but the Key never arrives

`sentToTyorvi` + `haveMark` put "Do you have the Key to the Clouds?" on
Tyorvi's menu, and `hasTea` adds "I have something for you from Ezrekal."
The persuasion runs:

    I have something for you from Ezrekal. → It is an elixir.
      → It will heal your dreams. → Just try it, please.
      → May I have the Key to the Clouds?

and he says it (`P3-key-handed-over.png`):

> Well, treacherous it is, but brave you are. Deserve a chance you do.
> Here, here the Key to the Clouds is.

`givenTea` (bit 1061) reads 1 afterwards, so the case ran to its end.

### P-a — no Key in the pack, and none found on the ground (BLOCKER)

The backpack afterwards holds one item, the (now empty) bag
(`P4-pack-after-key.png`); the Avatar's total weight is unchanged at 30
across the whole handover. Opening the bag shows it empty. A 20-point probe
sweep of the ground turned up floor, a mushroom and the Avatar — no shape 82.

**This matters because `CLCLIMB.UNK:30` gates the cliff climb on the item,
not a flag**: `foreach recursive item where (type = TypeCliffKey) within
container Avatar`. Without the item in inventory the Cloud City cannot be
entered, and the poison cure is behind it.

The same silence attended two earlier hand-overs in this run: the Zealan Mark
(`PLNTST.UNK`, no item, weight unchanged) and Ezrekal's elixir bottle
(no bottle in the pack, though Tyorvi's `foreach … TypeBottle … destroy()`
ran happily over an empty match and continued). All three use the same
idiom — `if give(Avatar:Referent, …) {} else if createNear(myMan, …) {}`.

(One confound worth recording for the next sweep: **single left-clicks on the
ground make the Avatar walk**, so the probe sweep moved him ~800 units off
the drop site before it finished.)

## Q — root cause: `CONTAINER_FAMILY` compiled to 0 (FIXED)

Disassembling the shipped `EUSECODE.FLX`, class `05AE` (FREE) offset `03B3`
— the head of `give` — showed the guard as

    03BB: calli  Item::getFamily()
    03C1: push retval
    03C2: 0A 00        push byte +0        ← CONTAINER_FAMILY
    03C4: 36           ne
    03C5: 51 01 00     jne  -> 03C9
    03C8: 50           ret                 ← every container lands here

`CONTAINER_FAMILY`, `QUAL_FAMILY`, `QUAN_FAMILY` and `REAGENT_FAMILY` are
never declared — not in `FREE.UNK`, not in any recovered header — so the
compiler's unresolved-identifier fallback emitted `push 0` for each, and the
build said so out loud: twelve `unknown identifier '…_FAMILY' compiled as
push 0` warnings from `FREE.UNK` alone.

The Avatar is `SF_CONTAINER` = 6, so `getFamily() != 0` was true for him and
**`give()` returned at its first instruction, for every caller, always**.
`take()` (`FREE.UNK:363`) carries the identical guard and was equally dead.
That is why the Zealan Mark, Ezrekal's elixir and the Key all vanished: the
`else if createNear(...)` fallback never ran either, because `give` returning
0 is exactly the branch that *does* run createNear — and createNear's own
quantity handling reads `QUAN_FAMILY`/`REAGENT_FAMILY`, both also zero.

**Fix**: `FAMILY_CONSTANTS` in `u8c_symbols.py`, pinned against
`ShapeInfo::SF_*` in `scummvm-lv-console/.../gfx/shape_info.h`, with a
`get_family_constant` hook in `u8c_codegen.py` beside the EQ_/Map*/PT_ ones.
`push byte 0` → `push byte 6` is size-neutral, so no class reflowed.

Verified three ways:

1. the twelve `_FAMILY` warnings are gone from the build;
2. the rebuilt `EUSECODE.FLX` disassembles at the same offset as
   `03C2: 0A 06  push byte +6`;
3. **in-engine**: reloading the pre-handover checkpoint and replaying the
   scene, the Avatar's total weight goes 30 → 50 and the Key sprite is
   sitting in the backpack (`Q1-key-delivered.png`).

Estate 26/26 after the change; `ARTIFACTS.sha256` re-recorded. Detection is
unaffected — the md5-5000 and the file size are unchanged, so no ScummVM
rebuild is needed.

One more thing this exposed about Tyorvi: his drunkenness is a **per-
conversation dice roll** (`ran = urandom(100); if (ran < 75) or (givenTea)`),
and `Just try it, please.` refuses outright on the drunk branch. A run that
tries once and believes the refusal will conclude the elixir is broken. Close
the conversation and re-open until the sober branch comes up.

## R — the Cloud Cliffs gate does not gate anything (FAIL)

`build_cloud_approach()` puts a key-locked gate (shape 114, quality 170 =
`CLIFF_KEY_ID`) at (7168, 23552, 8), described as standing "between the vale
and the active trigger, so Tyorvi's key gates the cliffs again". It does not:

- **it is inert.** Double-clicking it fires no usecode on the item at all
  (only the Avatar's own `event 18`); shape 114 has no door handler here.
  Probed as `Item 6297 (class Item, shape 114), (7168, 23552, 8) q: 170`.
- **it is 128 units wide on an eight-chunk-wide path.** `exact_reach` shows
  x=7040 and x=7296 open at the gate's own y band, and a route around it is
  three waypoints long. I walked round it and stepped straight onto the
  map-13 trigger at (7168, 24064).

Also worth noting: the key Tyorvi gives is created with quality 0
(`give(Avatar:Referent, TypeCliffKey, 0, 0, 1)` — the compiled call pushes
`qual 0`), while the gate's lock id is 170, so even a working door would not
have matched. Screenshot `R1-cliff-gate.png`.

## S — the cliff climb (PASS)

Walked in through the map-10 trigger — `Unloading map 10` /
`Loading Fixed items in map 13`, no debug teleport — and then north to the
`EggCloudCliffs` egg at (4096, 11264). Afterwards:

    climbedCliffs   (bit 1031) = 1
    attemptedCliffs (bit 1039) = 1

`CLCLIMB.UNK`'s hatch takes the has-key branch only when
`foreach recursive item where (type = TypeCliffKey) within container Avatar`
matches — so this is the `give()` fix proven end to end: the Key that could
not exist yesterday is the Key the climb just found. `climbedCliffs` had no
writer reachable before today, and it is read by TYORVI, HRODNY, THORDIS,
INGYALD and EZREKAL, so five NPCs' post-climb dialogue tiers just became
reachable. Checkpoint `cp20-cliffs-climbed.sav`.

One map note for the next session: the map-10 trigger delivers to
(4360, 19880) on map 13, roughly 8,000 units south of the arrival pad at
(4096, 11776), on ground `exact_reach` calls unstandable — the engine's
`z <= 0` freebie is what carries the Avatar there. `pathfind --engine-void`
routes out of it; a player without that would be standing in blackness.

## T — the summit and Cloud City (PASS)

Map 13 carries **a second inert key-gate** (`Item 4780, shape 114,
(4096, 10752, 4), q: 170`), and this one sits squarely across the climb's
foot: the Avatar walked into it and wedged. It behaves exactly like map 10's
— a double-click fires no usecode on the item — and it is equally bypassable,
four waypoints round it via x=3967.

Past it, `scratchpad/climb13d.py` (the 2026-09-01 pursuit driver) took the
whole climb in one run: `SUMMIT reached at (4068, 1068, 120)`. Walking three
tiles further north onto the trigger at (4096, 128, 120) gave
`Unloading map 13` / `Loading Fixed items in map 17` — **Cloud City**, white
stone and carved heads, matching Ezrekal's *"White as the clouds the walls
are"* (`T1-cloud-city.png`). Checkpoint `cp21-cloud-city.sav`.

Worth keeping: `walkto.py` cannot drive this climb and neither can `nav.goto`
— the 2026-09-01 report says so and this run re-confirmed it twice, losing
the Avatar off the narrow ledge at (4148, 5804) and off the east switchback
corner at (5016, 5312), both times to a run-gait overshoot. Densifying the
waypoints made it worse, not better: at hops under 320 units `walkto` drops
to a 56-unit tolerance and exhausts its budget short of the aim. Use
`climb13d.py` for map 13.

## U — the shield halves (PASS)

Cloud City's Memorial Hall holds them beside two sprawled skeletons:

    Item 2632 (class Item, shape 539) (uc: SHIELD), frame 0, (6208, 1568, 0)
    Item 7936 (class Item, shape 539) (uc: SHIELD), frame 1, (7232, 1568, 0)

Both dragged into the backpack (`Dropped item in backpack` for each); the
Avatar's total weight went 50 → 320. One of those 190 is a skeleton I picked
up by mistake — `BONES3` is a container lying *on top of* the second half, so
the first grab takes the bones and only then is the shield exposed. Worth
knowing before the next run wonders why the shield is still on the floor.

## V — the Sacred Circle ceremony (PASS)

Walking back to (20480, 17152) hatched it on approach:

    Item: 1440 (shape 73) calling usecode event 7 @ 05A5:0080
    Item: 107 (shape 707) calling usecode event 15   ← Atli
    Item: 106 (shape 707) calling usecode event 15   ← Thordis
    Item: 116 (shape 200) calling usecode event 15   ← Ezrekal

The clan leaders arrive quarrelling (*"Son of swine! Speak to me like this,
you shall not!"*), the mediation options land, and the Priestess sets her
price — *"If the shield of the Ancient Ones, he does have, listen, I will."*
Answering `Yes, Priestess.` puts both halves on the ground, and they merge
into one round shield (`U2-shield-restored.png`) while the Shades speak:
*"The power to restore our sacred shield, we sought, our clans to reunite.
By foul monsters, slain we were."*

Then `Please, High Priestess.` → **"I feel better... But I'm still so weak!"**
(`U3-cure.png`), and afterwards:

    avatarPoisoned (bit 1028) = 0     ← cured
    shieldFixed    (bit 1033) = 1

So the poison arc opened at the Passage Test closes at the Sacred Circle,
exactly as `SHADES.UNK` designs it — and the whole span from Ragnar's
referral to here ran in one continuous session, on foot, cheats off.
Checkpoint `cp23-ceremony-done.sav`.

## W — the ceremony leaves the camera behind (DEFECT, recoverable)

After `EggShades` finishes, the camera stops following the Avatar. He walks
normally for a while, leaves the fast area, and then stops moving entirely —
`objectInfo 1` shows his flags drop from `f: 0x2041` to `f: 0x41` (the
in-fast-area bit gone). The world is not paused and he is not wedged.

**A save taken in that state carries it**: reloading `cp23` put him straight
back to `f: 0x41`.

The recovery is `CameraProcess::moveToAvatar` — a camera command, not a
cheat; it changes no game state. `scratchpad/trek.py` wraps it, calling it
whenever progress stops, and the walk to the temple went through on that.

Root cause not established. `SHADES.UNK:546` ends `scrollBack(20);
setAvatarInStasis(false);` and **both resolve in the real build** — an
isolated single-file compile reports `scrollBack` unresolved, but that is the
provider table being empty outside `build_eusecode.py`, and the full build
log carries no such warning. So this is not another push-0.

## X — the Ancient Temple wall holds, and that is the design

The map-10 temple trigger works: `Unloading Fixed items from map 10` /
`Loading Fixed items in map 18`, arriving at (4040, 2008). The entry zone is
a warren of stone walls with narrow gaps (`W2-temple-entry.png`) — the
harness wedges in it repeatedly and needs a walkto-style eight-direction
sweep to get through.

Past it the Inner Sanctum boundary stops a full-size Avatar dead. Flooding
`exact_reach` from the arrival pad reaches 142,166 cells spanning
x 1607..4575, **y 583..6111**; the quest content is beyond it
(`EggTempleEntry` q305 at (2864, 6240), the altar at (3072, 8192),
`EggAOCeremony` q296 at (3072, 8320)). The break reads as

    y=6110   ground at z=0 across x 2608..3584
    y=6142   nothing standable
    y=6174   standable only at z=120   ← wall top
    y=6206   ground at z=0 again

and a 16-unit scan across x 600..6400 finds no ground-level opening in it.
**In-engine, walked in**: the Avatar reached (2928, 6108) and five sustained
southward bursts moved him zero units (`X1-sealed-wall.png`).

**This is correct behaviour, not a defect.** `build_sanctum_gate_hardening()`
raised that boundary to a 120-tall continuous stack on purpose, to close the
climb and void-walk bypasses the 2026-07-31 playtest proved. The way in is
the crack, and the builder states its terms exactly: *"its clear span is
x 2817..2879 at z 0..40, and the courses above it start at z=40, which the
32-tall shrunken Avatar passes under with 8 units of headroom"*.

So the gate is **Hrodny's Tiny Tar** (DD-005) — shrink, then creep through
the crack. My first reading of this, that the temple was mis-sealed and
wanted a doorway cut, was wrong: a 64x64x40 body finds no opening because
there is deliberately none at that height. The flood and the scan were both
measuring the wrong Avatar.

Next: fetch the Tiny Tar from Hrodny (NPC 113, map 10), return, drink, and
take the crack at (2817..2879, 6143).

## Y — Hrodny and the stolen chest key (PASS)

She is at (21760, 8448) in the Gunnar village, and her first-tier menu is
just name / job / bye — *"Unless with my inventions, here to help me, you
are, leave, you should."* The post-ceremony tier is what matters, and it was
there on the next conversation:

    I have been healed!
    The Shield of the Ancients is restored!

`I have been healed!` → *"See, so I do! For you, good! Perhaps something to
these god stories, there is. So now, open the temple, will you?"* → and that
adds **"How can I open the temple?"** (`Y1-hrodny.png`), which answers with
the Tiny Tar potions — *"Potions, I have, from generation to generation
passed on, they have been. For the moment of miracles, they are"* — and ends
by spawning the bag holding her chest key at **(19588, 23284, 0)**, in the
Temple Approach. Checkpoint `cp25-hrodny-key.sav`.

The remaining chain is therefore fully mapped: fetch that bag, unlock her
chest, take the Tiny Tar, carry it to the temple, drink at the crack
(x 2817..2879, y 6143), then `EggTempleEntry` → the altar → `EggAOCeremony`,
and `EggEndgame` back on map 10.

### The strike pixel needs the camera on the Avatar

`chase2.pixel()` — and `chase.py`'s — computes the sprite position as an
offset from the **window centre**, which is only the Avatar's position while
the camera is tracking him. After the ceremony it is not, and every strike
lands on bare ground: Hrodny took six failed strikes at ranges of 150-310
units before the cause was clear. `scratchpad/chase2.py` now calls
`CameraProcess::moveToAvatar` immediately before it re-reads and aims, and
the very next strike opened her.

## Z — the chest key, and where it stops (PARTIAL)

The bag Hrodny's case spawns is exactly where `lv-patched/HRODNY.UNK`'s
first repair puts it — **on the ground at (19588, 23284), not 64 units above
it** (`Y2-key-bag.png`). That repair is confirmed live: the 1994 `bag.pop(…,
64)` would have left it hanging in the air over this map's z=0 terrain.
Dragged into the backpack, `Dropped item in backpack`, item 6159.

### Z-a — the chest is buried in the hut wall (FAIL, blocker)

`build_gunnar_village()` puts `SHAPE_CHEST_LOCKED` (shape 618, quality 20) at
`x0+3584, y0+3584` = **(20992, 8704, 0)**. That coordinate is the hut's west
**wall column**, and the chest shares it with a wall piece:

    (20992, 8512, 0) shape 857     ← wall
    (20992, 8544, 0) shape 858     ← wall
    (20992, 8672, 0) shape 857     ← wall
    (20992, 8704, 0) shape 858     ← wall
    (20992, 8704, 0) shape 618  q 20   ← the chest, same cell

In-engine the wall wins the hit test. Standing inside the hut at
(21033, 8770) — reached via the y=8839 road, since the model calls the
interior floor level 40 from outside — a 16-point probe sweep across the
chest's whole predicted sprite area returned the wall piece, the floor and
the Avatar, and **never shape 618**. The chest cannot be clicked, so it
cannot be unlocked, so the Tiny Tar cannot be taken, so the temple cannot be
entered.

**Fixed in two moves, because the first one was not enough.**

Move 1 put the chest at `x0+3744, y0+3520` = (21152, 8640, 0) — same hut,
empty cell, on floor `exact_reach` calls standable. **Still unclickable.**
The hut's south wall run at y=8704 is 40 tall and sorts *in front of*
anything north of it, so the chest sat inside the wall's sprite. A 20-point
probe sweep on a fresh map-10 load returned the wall pieces at
(21120/21280, 8704), the post at (21152, 8704) and the floor at
(21119, 8575) — never shape 618. Same failure as the wall column, one tile
further in.

Move 2 put it on the open ground outside her door: `x0+3744, y0+3712` =
**(21152, 8832, 0)** — a single standable level 0, no occupants, the village
road just south at y=8839, and nothing tall between it and the camera.

**Verified in-engine**, on a fresh map-10 load (`Loading Fixed items in
map 10` after walking out of map 18, since a map-10 save carries the old
placement):

    Item 3515 (class Container, shape 618) (uc: LCHST_EW), (21152, 8832, 0)

three probes, three hits (`Z1-chest-moved.png`). `build_all_maps.py` rebuilt
cleanly (validation 0 WARN / 0 ERROR), estate 26/26, `ARTIFACTS.sha256`
re-recorded, and the new `FIXED.DAT` is installed under
`shared/u8-lv-patched/`. Checkpoint `cp27-chest-visible.sav`.

**The lesson generalises**: on this map an item is clickable only if nothing
tall lies south of it. Two "empty standable cell" placements in a row failed
for that reason, and neither the map validator nor `exact_reach` can see it —
they model standing, not drawing.

### Z-b — `trek.py` had no map-change guard, and it killed the Avatar

`nav.goto` has carried one since 2026-08-12, when continuing past a teleport
"dragged him 2100 units north into something lethal". `trek.py`, written
today, shipped without it: on the map 18 → map 10 return it kept driving at
(3071, 1420) — a map-18 coordinate that on map 10 is half the vale away —
and the Avatar was dead within the leg, `objectInfo 1` reading (0, 0, 0) with
the death book up. The arrival pad itself is fine: (18432, 22784) is
standable ground at z=0 across its whole neighbourhood.

Fixed: `trek.py` now records the map on its first reading and stops the
moment it changes. `trek.py`, `chase2.py`, `climbto.py` and `lv.sh` are
promoted out of the scratchpad into `tools/playtest-linux/`.

Checkpoint `cp26-chest-key.sav` — the key is in the pack, ready for the
chest as soon as it is reachable.

### The villages are the harness's worst terrain

Worth stating plainly for whoever picks this up. Between Hrodny and the key
the Avatar: climbed **onto a hut roof** at (21064, 8400) and had to be pushed
off; got shut **inside a hut** at (21056, 8288), where `exact_reach` reads
the only standable level as 40 (the roof) and a route out is unplottable;
and oscillated for 30 iterations in a north-south slot between huts because
the village exit loops **east** before it goes west. Both `walkto.py` and
`trek.py` time out there. What works is an explicit escape loop that tries
eight directions and keeps whichever one reduces the distance — the same
shape as `walkto`'s stall probe, but driven per-step instead of only on a
stall.

## Z-c — no chest in the game could be opened (ENGINE DEFECT, FIXED)

> **Corrected 2026-10-08:** this diagnosis was wrong. The retail engine's
> `isGameRunning()` returns 1 in the shipped game, so a *locked* chest that
> barks instead of opening is the retail design. Its key (Z-d below) is the
> way in. Plain chests open on either branch. The `I_false` fix described
> here let every locked chest open without its key, and was reverted in fork
> `f50c1d45`. Evidence: `docs/research/2026-10-08-u8-intrinsic-table.md`.

With the chest finally clickable, `use()` fired and nothing happened. The
log said

    Item: 3515 (shape 618) calling usecode event 1 @ 026A:00B0
    WARNING: Unhandled intrinsic 254 'isGameRunning()'? called!

Disassembling `026A` (LCHST_EW) shows why:

    00BB: calli 00FEh          ; intrinsic 254
    00BF: push byte retval
    00C0: jne -> 00D6          ; jne jumps when the value is ZERO
    00C3: spawn look() ...     ; taken when TRUE
    .L00D6: playSFX; openGump(7)

**The container opens on FALSE.** ScummVM's `U8Intrinsics[254]` is
`UCMachine::I_true` — a stub, and the engine even warns about it — so the
branch always took `look()`. Every one of the four callers in `EUSECODE` is a
chest (`CHEST_EW 004E`, `CHEST_NS 0075`, `LCHST_EW 026A`, `LCHST_NS 02A1`),
each compiling the same idiom, so **no chest in the game could be opened**.

Fixed in the fork (`engines/ultima/ultima8/usecode/u8_intrinsics.h`) by
mapping 254 to `UCMachine::I_false`, and the tracked patch
`tools/scummvm-patches/0001-lost-vale-engine.patch` was regenerated from the
fork — it was 21 lines out of date besides. Rebuilt, and the warning is gone.

Two traps worth recording for the next rebuild:

- **`build_scummvm.sh` applies the engine patch only when it clones.** An
  existing `scummvm-lv/` tree is just recompiled, so a fork edit does not
  reach the binary; either edit `scummvm-lv/` too or `--clean`.
- **`scummvm-lv-console/scummvm` is a stale August binary.** Launching the
  playtest with `LV_SCUMMVM=$PWD/scummvm-lv-console/scummvm` — which
  `HANDOFF.md` has been recommending — runs that, not what
  `build_scummvm.sh` produces in `scummvm-lv/`. Drop the override.
- After the rebuild the debugger stopped consuming `commands.txt`; the
  on-screen console takes **keystrokes** instead. `scratchpad/dbg.sh` drives
  it that way.

## Z-d — the key unlocks the chest (PASS)

Double-clicking the quality-20 key in the pack and then clicking the chest
turns it from `shape 618 (LCHST_EW)` into `shape 78 (CHEST_EW)`, and the next
double-click opens its gump (`Z2-chest-open.png`). The Cliff Key (quality 0)
targets the chest but does not unlock it, which is the lock ids working.

> **Corrected 2026-10-08:** the chest had no lock when this was written:
> KEYRING reads a TRAP inside the chest, not the chest's quality, and there
> was none, so any key opened it (`docs/playtest-2026-10-08-intrinsics.md`
> C4). Whatever made the Cliff Key fail here, it was not the lock id. The
> builder now places the TRAP, and the refusal is real
> (`docs/playtest-2026-10-08-chest-lock.md` L4).

## Z-e — the Tiny Tar does not exist (FAIL, terminal)

**The chest is empty.** `build_gunnar_village()` places
`SHAPE_CHEST_LOCKED` with no contents, the builder has no containment
support at all, and nothing else supplies the potions:

- `HRODNY.UNK`'s `How can I open the temple?` has exactly two branches. The
  first visit tells the key-theft story and spawns the key bag; every later
  visit says *"Give you the potions, I would. But gone, the key to the
  chest, is… Help you, I cannot."* **There is no branch for the player
  having found the key**, so she never hands them over.
- `POTION.UNK:145` is the shrink: `if fram = 8 … spawn makeAvatarTiny()`.
  Class `02FE POTION` is in the build (1958 bytes).
- **No potion item of any shape or frame is placed anywhere on map 10.**

So DD-005's Tiny Tar is wired but never instantiated, and the Ancient
Temple's crack — the only way in — cannot be used. Steps 16-18 are
unreachable until something puts a frame-8 potion in the player's hands.

**Decision wanted**, because this is quest design rather than a defect:

1. **Give the builder containment** and put two frame-8 potions inside the
   chest. Truest to DD-005 and keeps the key meaningful, but the map writer
   has no contained-item support today.
2. **Place the potions on the ground beside the chest.** One line, works
   now, but makes the key decorative.
3. **Add a branch to `HRODNY.UNK`** that gives the potions when the key is
   carried. Keeps the key meaningful and needs no map format work, but edits
   recovered dialogue past the minimal mandate the `lv-patched` tier keeps.

## Findings not on the plan

0. **AskGump clicks miss more often than they hit at some camera positions.**
   A click on the visible text of an option is not reliably inside its
   button: `Do you like her?` and `Cloud City?` both refused repeated clicks
   at their text centres and then took one a few pixels away. When an option
   does not respond, sweep a few (x, y) around it rather than concluding the
   option is dead — and re-screenshot after every selection, because the
   AskGump's vertical position moves with the camera, so a fixed row offset
   goes stale within one exchange.
1. **`nav.ask()` goes silent on back-to-back queries** mid-session, which made
   `chase.py` bail with "no strike landed" and no round output at all (its
   `continue` on a failed read prints nothing). `scratchpad/chase2.py` is
   `chase.py` with every read routed through `lv.sh q` (one command per
   attach) and it worked first time. Worth folding into `chase.py`.
1b. **`chase.py`'s triple double-click dismisses the gump it opens.** Tyorvi
   registered `event 1` five times and showed no conversation; a single
   double-click opened it. `scratchpad/chase2.py` now sends one.
2. **A climb push needs ≥ 1.4 s**, and ~2.2 s against a riser the Avatar is
   already standing against. 0.9 s moved him zero units — the turn animation
   eats a short burst, the same trap `walkto.py` documents.
3. **`climbto.py` must detach before pushing.** `nav.pos()` leaves the
   debugger attached, and attached means paused: two climbs "failed" silently
   before the detach was added.
4. **Poison does not tick during walking.** ~28,000 units of walking while
   `avatarPoisoned = 1` left hp at 30 throughout. The traps note about
   `Cheat::heal` did not apply on this run.

## Harness anomalies

- `session.sh`'s window search (`xdotool search --name ScummVM`) finds
  nothing; the window is named `Ultima VIII: Pagan (Gold Edition + Lost
  Vale/DOS/English)`. `nav.win()`'s `--class scummvm` works.
- There is no window manager on `:77`, so `windowactivate` errors. Clicks
  still land, because there is only one window.

## Disk changes

- `tools/playtest-linux/pathfind.py` — `DryMixin`/`DryReach`, `--allow-water`,
  `--water-margin`, `--step-z`.
- New checkpoints: `cp8-ragnar-stone`, `cp9-south-vale`, `cp10-passage-stone`,
  `cp11-zealan-mark`, `cp12-ezrekal-accepts`, `cp13-tyorvi-met`,
  `cp14-ingyald-met`, `cp15-cliffs-lead`, `cp16-tyorvi-nightmares`
  (slots 24-32).
- This report and `docs/playtest-2026-09-02-quest-chain/`.
- No game data was rebuilt; `ARTIFACTS.sha256` is untouched.

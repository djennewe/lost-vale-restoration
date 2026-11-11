# The full 1→18 playthrough, completed (2026-09-07)

Steps 1 through 18 run end to end in one continuous save chain. Every row
below is read from the engine's own globals, and the final state has been
**reloaded and re-read** before being believed.

| step | what it is | evidence |
|---|---|---|
| 1 | Lord British's message | `lbSpoke = 1` |
| 2-3 | Mythran; key; Elemental Dungeon | inherited from `run-s3-galjeron.sav` |
| 4 | four tokens, way opened | `Earth/Air/Fire/WaterColumnDestroyed = 1` |
| 5 | met the Zealans, Rite granted | `testFromAtli = 1` |
| 6 | each clan blames the other | `ragnarMet = 1` |
| 7 | Ragnar's tale and the bag | `ragnarToldStone = 1` |
| 8 | Passage Stone, test, poison | `haveMark = 1`, `avatarPoisoned = 1` |
| 9 | the Zealan Mark | `endOfPlantScene = 1` |
| 10 | Ezrekal's history | `ezrekalMet = 1` |
| 11 | Tyorvi and the Key | `sentToTyorvi = 1`, `tyorviDreams = 1` |
| 12 | root, elixir, Key handed over | `givenRoot`, `givenTea = 1`; Key (shape 82, q99) in the pack |
| 13 | cliffs climbed, Shield halves | `climbedCliffs = 1`; both halves taken |
| 14-15 | ceremony, shades, cure | `shieldFixed = 1`, `avatarPoisoned = 0`, `inShadeScene = 0` |
| 16 | gods at the Temple; Tiny Tar | `hrodnyMet`, `spokeTemple = 1`; three potions taken |
| 17 | Temple entered, Shield on the altar | `templeOpen = 1`, **`godsFree = 1`** |
| 18 | the Bag of Reagents | **`endgameStarted = 1`**; bag (shape 637) in the pack holding six reagent stacks of 25 |

Final state banked as `~/lv-checkpoints/run-s18-complete.sav`. Reloading it
gives Map 10, every flag above still set, the bag still carried and its six
reagents still in it.

Travel between areas used `MainActor::teleport`. The quest actions — the
answers, the pickups, the altar — are the real ones.

## Two defects that stop the run, both fixed or worked around

**`ragnarPissed` was a one-way door (fixed).** The top of `Ragnar::use()`
does `askList=<<"Ragnar?">>` — an assignment, not an append — so once the
flag was set every later conversation collapsed to that one option. The
apology barks "Forgiven all is" and never cleared it. Anger him once and
the Passage Stone thread, and step 7's bag with it, was gone for the rest
of the game. `lv-patched/RAGNAR.UNK` now clears it (LV-RESTORE change 12).

**The Sacred Circle leaves an item that crashes the engine.**
`SHADES.UNK:407` creates `invisShield` as `create(TypeAOFrizbee, 4)` and
pops it into the circle. Shape 539 has four frames, 0 to 3; there is no
frame 4. The item is only read for a position, and the file's own comment
already notes that read is dead — but the item stays lying on the grass,
and picking it up and opening the backpack kills the process outright:

    container_gump.cpp:101: ContainerGump::run(): Assertion `fr' failed.

That is the "altar-ceremony segfault" this project has been carrying. It is
not the altar: it is a frame-4 item in the pack, and any container gump
drawing it asserts. The run was completed by taking only the frame-2
`wholeShield`.

**Fixed** (LV-RESTORE change 13): `invisShield.destroy()` immediately after
the `getPoint` that is the only thing reading it. Verified by replaying the
ceremony from `run-s13-shield-halves.sav` on the rebuilt EUSECODE: it now
leaves exactly one shape-539 item in the circle, the frame-2 restored
Shield, where before it left two.

## Also worth keeping

**The restored Shield is dropped on the grass, not handed over.**
`SHADES.UNK:456` pops `wholeShield` at the ceremony site. The altar scene
(`AOSCENE.UNK`) searches the Avatar's *container* for it, so the player has
to notice it on the ground and pick it up, and an item on another map does
not exist to `findShape` at all — which is why the first altar attempt
looked like "no Shield anywhere".

**Step 9 sets no mark flag, deliberately.** Thordis's block says "give you
the Zealan Mark I will" and writes none: `haveMark`, from the Passage Test
hatch, is what the quest reads. `endOfPlantScene` is the one-shot the two
elders share and is the honest marker for the step. Her block is bark-only
— no question opens, so a "did a conversation start?" check reports failure
on success — and it only fires with the Avatar standing next to her.

## What made it finishable

Five console commands in the fork took the mouse out of the quest loop:
`ObjectManager::findShape`, `AskGump::ask`, `Actor::hold`, `Actor::talk`,
`Item::grab`. The last two matter most: they replace "get the pointer onto
a sprite" — which fails whenever the camera is parked where the last
conversation ended — with an object id.

`AskGump::ask` also reports how many conversation processes are live.
Without that a caller cannot tell an NPC mid-bark from a finished
conversation, and has to guess with a timeout; the pessimistic guess cost
twenty seconds on every turn of every tree.

Three traps are worth remembering:

- **An open console pauses the world.** Polling a cutscene to see whether
  it has finished is what stops it finishing. One ceremony sat on the same
  instruction pointer for five minutes of "waiting".
- **Long barks must be clicked through**, not waited out: the usecode after
  them — including the flag writes — does not run until they are dismissed.
- **A save can fail silently.** `Kernel::canSave()` refuses while a
  conversation process is suspended. `scratchpad/bank.py` saves, checks the
  slot's mtime moved, reloads it and reads the flags back before keeping
  the file; it rejected three bad saves during this run.

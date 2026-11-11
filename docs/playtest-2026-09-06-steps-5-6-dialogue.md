# Step 5 reached, and dialogue stops being a pixel problem (2026-09-06)

## What the run reached

Continuing the run banked as `run-s4-columns-done.sav`:

| step | state | evidence |
|---|---|---|
| 1 | done | `lbSpoke = 1` |
| 2-3 | done | inherited from `run-s3-galjeron.sav` |
| 4 | done | `EarthColumnDestroyed`/`Air`/`Fire`/`Water` all `= 1` |
| 5 | done | `atliMet = 1`, **`testFromAtli = 1`** — Atli granted the Rite of Passage |
| 6 | done | both clans blame the other; `ragnarMet = 1` |
| 7 | done | **`ragnarToldStone = 1`** — Ragnar's tale of the lake, and the bag |
| 8-18 | not reached | |

Banked and **verified by reloading**: `~/lv-checkpoints/run-s5-rite-granted.sav`
comes back at Map 10 with all of the above still set.

Step 4's completion is now confirmed in usecode, not just visually: the
four column flags read 1.

## Reading quest state

`shared/build/lv_manifest.json` holds the pinned `global_flags` allocation
the shipped EUSECODE was built with. That is the only trustworthy map of
flag to bit. Re-deriving an offset by parsing `FLAGS.UNK` alone gives the
wrong bit — the compiler allocates by walking every source tier — and the
wrong bit reads 0, which is indistinguishable from a quest step that never
fired. That mistake cost a full round of false negatives here: all four
column flags read 0 from a locally-derived offset while the pillars were
demonstrably gone.

`scratchpad/flags.py` reads any flag by name through the manifest.

## Dialogue by console

Two commands were added to the fork:

- **`AskGump::ask`** — no argument lists the open question's options with
  their indices; one argument answers by index.
- **`Actor::hold <objid> [dx dy]`** — stops an NPC wandering, parks her
  beside the Avatar, and reports the pixel she is drawn at.

Clicking dialogue rows meant locating variable-width text whose position
depends on the answer strings, and a mis-hit was indistinguishable from a
mis-read tree. With `ask`, a conversation is a loop of console calls, and
the option text is readable — so the tree can be walked, logged and
asserted on.

`Actor::hold` exists because killing a villager's LoiterProcess is not
enough on its own: `SchedulerProcess` hands her a fresh activity within
seconds, so a probe grid that takes twenty seconds to run arrives where
she used to be. Atli moved ~500 units between one teleport and the probe.

## Two defects seen while walking Ragnar

**Options accumulate on re-entry.** Leaving and re-entering Ragnar's
conversation adds another copy of the same option: `When you can find
game?` appeared once, then twice, then three times in successive
conversations, and `I am peaceful with all.` doubled. The met-branch menu
appends without checking for a duplicate. Not fatal, but it makes the menu
grow without bound across a real playthrough.

**`Atli sent me to you.` never appeared — and that was the harness, not
the game.** The walker's goodbye pattern did not match `Farewell.` (the
trailing period), so it never ended a conversation with Ragnar. His
`use()` process stayed suspended, every later `Actor::talk` resumed it
mid-loop instead of re-running the header, and the header is where
`RAGNAR.UNK:242` adds the option. The same thing explains the duplicate
options above: the askList is a local of that one long-lived process, so
it accumulated instead of being rebuilt.

With the pattern fixed, a genuinely fresh conversation opens on exactly
`['Atli sent me to you.', 'Farewell.']`, and walking it through
`Do you know of the Passage Stone?` -> `Yes, I do.` sets
**`ragnarToldStone = 1`**. Steps 6 and 7 are done. Also confirmed in
passing: the DD-008 restoration ships, `I have no fight with you.` is in
his menu.

**`ragnarPissed` is a one-way door, and that one is real.** The top menu
does `askList=<<"Ragnar?">>` — an assignment, not an append — so once the
flag is set every later conversation collapses to that single option. The
apology case barks "Forgiven all is" and never clears the flag, so the
collapse is permanent: anger him once and the Passage Stone thread, and
step 7's bag with it, is gone for the rest of the game. `lv-patched/
RAGNAR.UNK` now clears `ragnarPissed` in that case (LV-RESTORE change 12).

## The harness limit

The remaining cost is not dialogue any more, it is getting the pointer to
the right place at all. The camera repeatedly stayed parked where the last
conversation ended; `CameraProcess::moveToAvatar` only takes effect on a
world tick and an open console pauses the world, so a pixel measured right
after it is measured against the old camera. Re-teleporting the Avatar
each attempt re-centres the view, but the console is a stateless toggle
and a command typed while it happens to be shut goes to the game instead
(where `c` toggles combat, which silently swallows every left click).

The fix worth building next is a console command that starts a
conversation with an NPC by object id, with no pointer involved at all.
Everything downstream of that already works.

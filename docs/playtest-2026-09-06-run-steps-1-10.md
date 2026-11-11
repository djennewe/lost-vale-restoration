# The run reaches step 10, and the quest loop stops needing a pointer

## Where the run stands

Every row below is read from the engine, not inferred, and every
checkpoint named here has been **reloaded and re-read** before being
believed.

| step | flag evidence | checkpoint |
|---|---|---|
| 1 | `lbSpoke = 1` | |
| 2-3 | inherited from `run-s3-galjeron.sav` | |
| 4 | `Earth/Air/Fire/WaterColumnDestroyed = 1` | `run-s4-columns-done.sav` |
| 5 | `testFromAtli = 1` | `run-s5-rite-granted.sav` |
| 6 | `ragnarMet = 1` (both clans blame the other) | |
| 7 | `ragnarToldStone = 1` | `run-s7-ragnar-stone.sav` |
| 8 | `haveMark = 1`, `avatarPoisoned = 1` | `run-s8-mark-poisoned.sav` |
| 9 | `endOfPlantScene = 1` | `run-s9-mark-given.sav` |
| 10 | `ezrekalMet = 1` | `run-s10-ezrekal.sav` |
| 11-18 | not reached | |

Travel between areas uses `MainActor::teleport`. The quest actions —
answering, taking, using — are the real ones.

## A checkpoint that lied

`run-s9-mark-given.sav` was banked once and was **wrong**: it reloaded
with `haveMark = 0`. `Kernel::canSave()` refuses while a conversation
process is suspended, `cmdSaveGame` says so on a path a log match does not
reliably catch, and copying the slot afterwards then preserves whatever
older state was in it. The file was deleted and the step redone.

`scratchpad/bank.py` now saves, checks the slot's mtime actually moved,
reloads the slot, and reads the flags back out before copying anything
into `~/lv-checkpoints`. It refused two bad saves during this session.

## Reading quest state

`shared/build/lv_manifest.json` holds the pinned `global_flags`
allocation the shipped EUSECODE was built with. That is the only
trustworthy flag-to-bit map: re-deriving an offset from `FLAGS.UNK` alone
gives the wrong bit, and a wrong bit reads 0, which is indistinguishable
from a step that never fired. All four column flags read 0 that way while
the pillars were demonstrably gone.

## Five console commands, and why each exists

| command | replaces | why the pointer failed |
|---|---|---|
| `ObjectManager::findShape <shape>` | hunting an item by clicking | "never created", "not in the fast area" and "behind something" all read as silence |
| `AskGump::ask [n]` | clicking a dialogue row | rows are variable-width and move; a mis-hit reads like a mis-read tree |
| `Actor::hold <id> [dx dy]` | chasing a walking NPC | SchedulerProcess re-issues loitering seconds after the walk is killed |
| `Actor::talk <id>` | double-clicking an NPC | the camera parks where the last conversation ended, so the reported pixel is off screen |
| `Item::grab <id>` | dragging an item onto the Avatar | a 5x4 gem on a floor tile falls through any probe grid |

With `talk`, `ask` and `grab`, none of steps 5-10 needed the mouse.

## Two harness bugs that looked like game defects

**"`Atli sent me to you.` never appears."** Wrong. The walker's goodbye
pattern did not match `Farewell.` — the trailing period — so it never
ended a conversation with Ragnar. His `use()` process stayed suspended,
every later `Actor::talk` resumed it mid-loop instead of re-running the
header, and the header is where the option is added. The same cause
explains the duplicate options: the askList is a local of that one
long-lived process, so it accumulated instead of being rebuilt.

**Deep options "unreachable".** They are only reachable inside a single
continuous conversation. Saying goodbye between rounds throws the position
away and the next round restarts at the top menu.

## One real game defect, fixed

`ragnarPissed` was a one-way door. The top of `Ragnar::use()` does
`askList=<<"Ragnar?">>` — an assignment, not an append — so once the flag
was set every later conversation collapsed to that single option. The
apology case barks "Forgiven all is" and never cleared it, so the collapse
was permanent: anger him once and the Passage Stone thread, and step 7's
bag with it, was gone for the rest of the game. `lv-patched/RAGNAR.UNK`
now clears the flag there (LV-RESTORE change 12).

## Step 9 has no mark flag, and that is deliberate

Thordis's post-test block says "give you the Zealan Mark I will" and sets
no `zealanMark`. `ATLI.UNK`'s header explains why: `haveMark`, granted by
the Passage Test hatch, is the flag the quest reads; `zealanMark` is a
discriminator for a different branch. `endOfPlantScene` is the one-shot
latch the two elders share — exact complementary guards, so only one of
them ever delivers the beat. It is the honest marker for step 9.

Two things follow for anyone driving this: the block is bark-only (no
question opens, so a "did a conversation start?" check reports failure
even on success), and it only fires with the Avatar standing next to her —
300 units away is too far.

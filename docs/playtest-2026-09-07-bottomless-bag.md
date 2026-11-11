# `hasBag`, and a bag that is actually bottomless (2026-09-07)

## What changed

`ENDGAME.UNK` now does three things at the hand-over instead of one:

1. creates the bag and its six reagent stacks (as before),
2. sets **`hasBag = true`**, and
3. spawns **`topUpReagents`**, which keeps the stacks full.

## The flag

`hasBag` had no writer. `EZREKAL.UNK:2066` gates her reply to "I have freed
your gods!" on it — "I know not enough to repay you the bag I gave you is"
— so the Avatar could finish the game and she would never acknowledge the
bag. One line, and it uses the existing pin (bit 1037); nothing new was
allocated.

## Why a process and not usecode on the bag

A U8 item's usecode class comes from its **shape**, and this bag is shape
637 — the same `TypeBag` RAGNAR pops for the Passage-stone bag and HRODNY
for the stolen-key bag. Attaching behaviour to 637 gives it to those too.

Replacing retail class `027D BAG` is *dispatch*-safe. Scanning every retail
class for `call`/`spawn` operands finds **zero** callers of 027D — the same
test that clears AVATAR, against FREE's 133. But it is not *expressible*:
retail `use()` is `closeGump()` if `status & 0100h` else `openGump(3)`, and
this dialect has no bitwise and. A version that could only ever open the
gump would change how both quest bags behave.

The fork's `npcnum + 1024` dispatch would sidestep the shape entirely —
it keys on `_npcNum` for any item, runtime-created included — but
`I_setNpcNum` is not in the U8 intrinsic table, so a bag created in usecode
cannot be given an npcnum.

Hence a process: it owns no shape and collides with nothing.

## Why topping up and not a bigger number

Reagent weight scales at about 1 per unit against the Avatar's 600
capacity. `FREE::give()`'s 666-per-stack ceiling took him to 4296 and he
could not pick anything up again. "Endless" has to come from refilling.

The loop waits 200 ticks, then tops every `TypeReagent` in the Avatar's
container (recursively, so it reaches inside the bag) back to 25 — guarded
by `< 25`, so a larger stack found elsewhere is left alone rather than
trimmed.

## The regression this nearly shipped with

`spawn X -> return` emits the spawn **and an `implies`**, so the spawning
process waits on the spawned one. Placed mid-scene, `topUpReagents` — which
never returns — froze `EggEndgame::hatch` where it stood: no fades, no
closing bark, and the Avatar left permanently in stasis because
`setAvatarInStasis(false)` was never reached. The game could not be saved
again.

Caught because `bank.py` refused the save. The spawn is now the **last**
statement in `hatch`, after everything else has run.

## Verified in ScummVM

Replayed from `run-s16-tinytar.sav` through the altar and the endgame:

- `godsFree = 1`, `endgameStarted = 1`, **`hasBag = 1`**.
- Save now succeeds, and reloading gives all three back.
- **Refill, before a reload**: stacks drained to 0, 3 and 7 were all 25
  again within 45 s.
- **Refill, after a save and reload**: stacks drained to 0, 2 and 5 were all
  25 again within 50 s — so the process is saved with the game and resumes.

Banked as `~/lv-checkpoints/run-s18-bottomless.sav`. The full test estate
passes, 26/26 files.

## Still open

The six stacks share gump slot (0,0) and draw on top of each other.
`moveToContainer` zeroes the gump position, no intrinsic exposes it to
usecode, and only the literal (255,255) triggers `ContainerGump`'s
randomiser — inherent U8 behaviour for usecode-created contents, and it
affects the refill exactly as it affected the shipped pouch.

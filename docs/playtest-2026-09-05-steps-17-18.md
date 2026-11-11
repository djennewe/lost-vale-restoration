# Playtest 2026-09-05 — steps 17-18 COMPLETE: the altar, the gods, the endgame

## Verdicts

| # | Test | Result |
|---|------|--------|
| A | `templeOpen` is written when the Avatar enters the Inner Sanctum | **PASS** |
| B | The restored Zealan Shield exists and can be carried | **PASS** |
| C | `EggAOCeremony` fires at the altar | **PASS** |
| D | AOSCENE's guards bail correctly when a precondition is missing | **PASS** |
| E | **Step 17** — the ceremony completes and sets `godsFree` | **PASS** |
| F | **Step 18** — `EggEndgame` runs the restoration sequence | **PASS** |
| G | **Bag of Reagents handed over by the freed gods** | **PASS (implemented this session)** |

Final flag state:

    shieldFixed     (0x409) = 1
    templeOpen      (0x412) = 1
    godsFree        (0x40E) = 1
    endgameStarted  (0x716) = 1

Checkpoint: `~/lv-checkpoints/cp32-endgame-done.sav`.

## The mistake that cost most of this session

**There was never a bug in AOSCENE.** The scene is ~450 ticks of `wait()` plus
four barks, and `godsFree` is set only at the very *end* (offset 0x389). Every
time I checked a global I attached the debugger — **and attaching pauses the
world**, freezing the scene mid-run. Reading `godsFree` therefore always
observed 0, and I read that as "the scene bailed".

It also explains the Avatar "wedging": `AOSCENE::hatch` opens with
`setAvatarInStasis(true)`, so a paused-mid-ceremony Avatar refuses to walk in
all four directions — indistinguishable from the documented teleport wedge,
and `Cheat::hackMover` cannot fix it because it is not a terrain problem.

The one **segfault** seen earlier did **not** recur: the full chain ran
afterwards under `gdb -batch` with no backtrace produced (`BACKTRACE` count 0).
Treat it as an unreproduced one-off, not a blocker.

**The rule that falls out:** let a cutscene run untouched. Close the console,
wait out the scene, and only then query. Frame-diffing is not enough either —
the sanctum is static enough that two frames match while the scene plays.

## A — `templeOpen` gets its writer (PASS)

Squeezing through the Tiny Tar crack drops the Avatar onto `EggTempleEntry`
(quality 305 -> class 1456):

    Item: 1950 (shape 73) calling usecode event 7 @ 05B0:0080
    templeOpen (0x412)  0 -> 1

The flag *"read in 11 places across the 1994 corpus and written in ZERO"* is
now written in-engine. Teleporting straight into the sanctum skips this egg,
which is an easy way to make the altar look broken.

## B — the restored Shield, and where it actually was (PASS, with a finding)

**cp29's Avatar was not carrying the shield.** He was carrying a skeleton:

    Item 1135 (class Container, shape 332) (uc: BONES3)
      Container vol: 0/20, total weight: 190, items: 0

That is the `traps.md` hazard — `BONES3` lies on top of the shield halves in
Cloud City and wins the click. The restored shield was still lying where the
Sacred Circle ceremony left it:

    Item 2676 (class Item, shape 539) (uc: SHIELD), frame 2, (20480, 17148, 0)

`SHADES.UNK:456` does `wholeShield.pop(firePoint1.x - 60, firePoint1.y - 30,
firePoint1.z)` — it **drops the shield on the grass** and never hands it over.
Picked up normally it stows (weight 250 -> 290, so the shield weighs 40).

**Design call wanted:** an endgame artifact that silently falls at the end of a
cutscene is very easy to walk away from, and the 2026-09-02 run did exactly
that.

## C/D — the egg and its guards (PASS)

`EggAOCeremony` (quality 296 -> class 1447) fired on approach *and* on
teleport-arrival into its +/-192 box:

    Item: 4958 (shape 73) calling usecode event 7 @ 05A7:0080

Both guard paths were observed returning cleanly, which is what makes E mean
something: with `templeOpen` 0 it returns at the second guard, and with no
shape-539 item in the Avatar's container it returns at `if not hasArtifact`.
Neither crashes; `godsFree` stays 0.

Also verified by inspection, because the artifact search looked suspect at
first: the `foreach recursive item where (type = TypeAOArtifact) within
container Avatar` loopscript is built on the stack, so it reads back as
`'A', 0x1B, 0x02, '$'` — "match 1 shape, little-endian 0x021B = 539", then
END. The container-search operands are pushed `1` (Avatar) then `0xFFFF`, and
`uc_machine.cpp:1689` pops `ui16a = 0xFFFF`, `ui16b = container`. Both correct.

## E — step 17, the ceremony completes (PASS)

With `godsFree` 0, `templeOpen` 1, `shieldFixed` 1 and shape 539 in the pack
(`Item 6530 ... f: 0xc`), the hatch ran the full scene: `setAvatarInStasis`,
the SFX spawns, `FadeToWhite` (visible as a white band across the sanctum),
the four barks, `FadeFromWhite`, and finally

    godsFree (0x40E)  0 -> 1

## F — step 18, the endgame (PASS)

`EggEndgame` (quality 299 -> class 1450) at (18432, 22016) on map 10, +/-256
box:

    Item: 7688 (shape 73) calling usecode event 7 @ 05AA:0080
    endgameStarted (0x716)  0 -> 1

The restoration sequence played — fade to black, the Vale-healing barks, and
the closing line about the path to Britannia opening — then `FadeFromBlack`
restored the view and stasis was released (`C2-vale-after-endgame.png`).

## G — the Bag of Reagents, now implemented (PASS)

Step 18's reward was not code: `ENDGAME.UNK` ended on `// playEndgame();` and
nothing handed the player anything. `items.yaml` records the "Bottomless Bag"
as *"given by the freed gods"*, so the hand-over went into the endgame itself
rather than a later Ezrekal branch — nothing makes the player walk back to her
once the Vale is restored, so that reward would simply never be collected.

The elder's beat now creates a `TypeBag` (637, SF_CONTAINER — the same quest
bag RAGNAR and HRODNY already pop), fills it with six `TypeReagent` (395,
SF_REAGENT) stacks at frames 0, 6, 8, 9, 10 and 14, and pops it into the
Avatar's backpack, with `popToEnd(Avatar)` as the fallback for a backpack-less
Avatar (the same fallback `FREE::give()` uses). A closing bark covers it.

**Deliberately NOT `TypeBagOReagents` (225):** that entry is SF_GENERIC and
still carries the old dining-table id, so it can hold nothing. The six frames
are the set ScummVM's own `Cheat::items` builds, so they are known-good
reagent frames rather than a guess. New symbol `TypeReagent: 395` was added
for readability; 395 was already present as `TypeBottle` (the elixir at
frame 13).

**Quantity was tuned against the engine, not guessed.** At `FREE::give()`'s
666-per-stack ceiling the Avatar went **290 → 4296** in-engine — permanently
overloaded against a 600 capacity, unable to pick anything up again. At 25
apiece he goes **290 → 450**, which leaves him mobile.

Verified in-engine on a fresh run of the whole chain:

    weight 290 -> 450   (bag + 6 x 25 reagents)
    endgameStarted (0x716)  0 -> 1
    dragging one stack out of the bag: weight 450 -> 425, exactly one stack

Screenshot `D1-bag-of-reagents.png` shows the pouch open in the pack.

**Two caveats worth knowing.** The bag is a generous pouch, not the literally
endless one Plot v1.2 describes — a true bottomless bag cannot be a stack at
all; it needs usecode that tops itself back up on use, which is a feature
rather than a hand-over, and is left as a design call. And the six stacks all
land at gump slot (0,0) and draw on top of each other: `moveToContainer` zeroes
`_x`/`_y`, no intrinsic exposes gump position to usecode, and only the literal
(255,255) triggers `ContainerGump`'s randomiser — so this is inherent U8
behaviour for usecode-created container contents, not something introduced
here.

## Harness notes worth keeping

- **Let cutscenes run.** Attaching the debugger pauses the world; a scene whose
  flag is set at the end will always read as "bailed" if you poll it.
- **Stasis looks exactly like a teleport wedge.** Zero displacement in all four
  directions during a scene is `setAvatarInStasis(true)`, not terrain.
- **`close_verified()`** (`scratchpad/drv.py`): the console is a toggle with no
  readable state and `exit` typed at a closed console leaks its letters to the
  game (`i` opens the pack, `m` the minimap, Escape the Pagan menu). Probe with
  `help` — if the log grows it was open. Do not detect it by green pixels;
  grass matches.
- **Scene eggs hatch on teleport-arrival**, far more reliable than walking into
  the box. But an egg hatches **once per map instance and the savegame stores
  that** — only leaving the map and returning re-arms it.
- **Clicks are window-relative**: window at (405,196), so screenshot pixel maps
  to `(px-405, py-196)`.
- Drop pickups on the **Avatar's sprite**, approaching **from the north-west**;
  beyond ~150 units the drop silently bounces.
- **Cheats ON turn a click into the retail dev menu** (`Blow up!`/`Kill me` are
  live). `Cheat::items` grants no key.

## Disk changes

- **`cp33-bag-of-reagents.sav`** (endgame done, bag in the pack; one stack
  was pulled out during verification).
- `~/lv-checkpoints/cp30-altar-ready.sav` (shield carried, AO egg unhatched;
  its saved position is a teleport wedge), `cp31-altar-armed.sav`,
  **`cp32-endgame-done.sav`** (all four flags set — the finished state).
- Save slot 1 overwritten; pre-session slot 1 archived as
  `slot1-before-2026-09-03.sav`.
- `scratchpad/drv.py`, `scratchpad/gdbrun.sh`.
- `agents/usecode-compiler/src/lv-new/ENDGAME.UNK` — the hand-over.
- `agents/usecode-compiler/src/u8c_symbols.py` — new `TypeReagent: 395`.
- `EUSECODE.FLX` rebuilt (`70eea382... -> 9fbca0be...`); `ARTIFACTS.sha256`
  re-recorded. **Detection followed**: EUSECODE grew 1502367 -> 1502809, so
  `LV_SIZE` in `build_scummvm.sh` was updated and ScummVM rebuilt
  (`detection_tables.h` is auto-updated by `build_eusecode.py`). The md5-5000
  window is unchanged. `FIXED.DAT` unchanged at `278a48c3...`.
- Note `scummvm-lv-console/` still carries the old detection size; it is the
  stale August binary the baton already says not to use.

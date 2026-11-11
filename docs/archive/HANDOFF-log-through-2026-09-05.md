# HANDOFF log, archived through 2026-09-05

(Archived 2026-09-13 when HANDOFF.md was cut back to a baton. Durable content
from this file lives in `.claude/skills/playtest/traps.md`, `TODO.md` and the
dated `docs/playtest-*.md` records.)

The baton between sessions. Keep it short — if something is still true next
month, it belongs in `TODO.md`, a rule, a skill, or a doc, not here.

> Last updated: 2026-09-05 (session close)

## Next action

**Continue the step 1-18 continuous run. Step 1 is DONE; step 2 is where it
stops.** Start from `~/lv-checkpoints/run-s1-lbdone.sav` (`lbDone` = 1,
map 8).

**The blocker is NPC conversation, and it is the same blocker for all 17
remaining steps.** Mythran is objId 33, shape 190, on the z=48 shelf. He
wanders faster than a probe sweep runs, and from most angles a large scenery
item (5534, shape 149, at (2367,2559,48)) sorts in front of him. Talking to
him needs a double-click on his sprite, and the harness cannot hold the two
halves together: every console read reopens the console, which pauses the
world, and every mouse probe needs it shut.

**Build the strike tool before grinding further.** `scratchpad/drv.py` now has
the pieces — `ready()` (proves the world is interactive by a click that
returns a dump), `look_fast()` (~0.3 s per probe instead of ~1.3 s, fast
enough to out-run a walking NPC) and `find_actor()` (mouse-only sweep, no
console calls mid-sweep). What is missing is the loop that ties them
together: read the NPC once, close the console, sweep, strike, and confirm by
`Item: <id> ... calling usecode event 1` in the log. **Occlusion is
world-determined, not camera-determined** — U8's view angle is fixed, so
moving the Avatar does not uncover an NPC; you have to catch him when he is
not behind the scenery.

**Three structural facts found while starting the run — do not rediscover
them:**

1. **Map 8 has at least two large disconnected z=0 regions.**
   `cp4-mythran-approach` sits in a 5840-cell pocket that does **not** contain
   Mythran; his region is a separate 11552-cell one. The save name misleads.
   `exact_reach --map 8` reproduces both.
2. **The map-8 LORDBRIT backstop egg is not walk-reachable.** No standable
   cell inside its +/-128 box is reachable from the approach region, and its
   own cell reports `levels here: []`. The scene fires correctly once you are
   in the box, so this is placement, not wiring. The *primary* step-1 trigger
   is on map 39 at (17150, 19700, 48), and **no checkpoint exists on map 39**
   (the earliest two are both map 40).
3. **August checkpoints cannot be trusted for quest state.**
   `cp4b-lb-done.sav` reads `lbDone = 0` under today's flag numbering.

**What the run has banked:** `run-s1-lbdone.sav` — step 1 complete, the Lord
British scene played in full, Avatar stable at (2200, 2300, 8).

**Decisions wanted:**

1. **The Bag of Reagents is a generous pouch, not a bottomless one.** Six
   reagent stacks of 25. Worth building the real thing, or is a pouch enough?
   The refill mechanic is **specced but deliberately unbuilt** — see the
   filed item in `TODO.md` §6, which carries the three candidate approaches
   (refill-on-open, a top-up process, or just making reagents weightless),
   the shape-637 class-collision blocker that has to be solved first, and the
   engine constraints so they are not rediscovered.
2. **The restored Zealan Shield is dropped on the grass** by `SHADES.UNK:456`
   (`wholeShield.pop(firePoint1 - (60,30))`) and never handed over. The
   2026-09-02 run left it at (20480, 17148) and walked off with a shape-332
   `BONES3` skeleton instead. Easy to miss; the endgame bag now shows the
   pattern for handing something over properly.

**Steps 17-18 COMPLETE (2026-09-05)**, checkpoint `cp32-endgame-done.sav`:

    shieldFixed (0x409) = 1   templeOpen (0x412) = 1
    godsFree    (0x40E) = 1   endgameStarted (0x716) = 1

`EggAOCeremony` (q296 -> 1447) played the full scene and freed the gods;
`EggEndgame` (q299 -> 1450) at (18432, 22016) ran the restoration sequence.
Record: `docs/playtest-2026-09-05-steps-17-18.md`.

**Also wanted from Douglas — a design call.** The restored Zealan Shield is
**dropped on the grass** by `SHADES.UNK:456` (`wholeShield.pop(firePoint1 -
(60,30))`) and never handed over. The 2026-09-02 run left it at
(20480, 17148) and walked off carrying a shape-332 `BONES3` skeleton instead
(the Cloud City hazard in `traps.md`). Easy to miss; worth changing.

**THE HARNESS RULE THAT COST THIS SESSION: let a cutscene run untouched.**
Attaching the debugger **pauses the world**. AOSCENE sets `godsFree` only at
the END of ~450 ticks of waits and barks, so polling the flag froze the scene
and always read 0 — which I misdiagnosed as a crash. The same pause makes the
Avatar refuse to move in all four directions (`setAvatarInStasis(true)` opens
the scene), which is indistinguishable from a teleport wedge and which
`Cheat::hackMover` cannot fix. Close the console, wait the scene out, *then*
query. Frame-diffing does not help; a static sanctum gives identical frames.

**Other harness facts** — `scratchpad/drv.py` encodes them:

- **`close_verified()`**: the console is a toggle with no readable state, and
  `exit` typed at a closed console leaks its letters to the game (`i` opens
  the pack, `m` the minimap, Escape the Pagan menu). Probe with `help` — if
  the log grows it was open. Do NOT detect it by green pixels; grass matches.
- **Scene eggs hatch on teleport-arrival**, which is far more reliable than
  walking into the box. But an egg hatches **once per map instance and the
  savegame stores that** — only leaving the map and returning re-arms it.
- **Clicks are window-relative**: window at (405,196), so a screenshot pixel
  maps to `(px-405, py-196)`.
- Drop pickups on the **Avatar's sprite**, approaching **from the north-west**;
  beyond ~150 units the drop silently bounces.
- **Cheats ON turn a click into the retail dev menu** (`Blow up!`/`Kill me`
  are live). `Cheat::items` grants no key.

**Proven 2026-09-04** (`docs/playtest-2026-09-04-steps-16-17.md`): key ->
unlock chest (618->78) -> three Tiny Tar potions inside -> one into the pack ->
survives a map change -> full-size Avatar BLOCKED at the crack (four pushes,
zero units) -> drink frame 8 -> `shape 708 (uc: CHILD)` -> the same pushes
carry him through to (2804, 6664) -> re-grows alive -> `templeOpen` 0 -> 1.

**A crash was found and fixed 2026-09-04.** Contained `FIXED.DAT` records
loaded without `FLG_CONTAINED` (the loader's `Container::addItem` never sets
it), so `Item::moveToContainer` did not unlink a taken item from its old
container: one item in two containers, freed under the pack on the next map
change. Fixed data-side in `MapItem.contained_item()` (`flags = 0x0008`). If
you add contained items anywhere else, that flag is mandatory.

**The exit test now runs steps 6-15 unbroken and reaches the door of 16-17.**
One continuous session, cheats off, everything walked or climbed: Ragnar's
referral → the Passage Stone → the Passage Test → Ezrekal → Tyorvi and
Ingyald → the root errand → the Key to the Clouds → the Cloud Cliffs → Cloud
City → both shield halves → the Sacred Circle ceremony (shield restored,
**poison cured**) → the temple → Hrodny → her key → her chest, unlocked and
open. Full record: `docs/playtest-2026-09-02-quest-chain.md`.

**Three defects fixed on the way, each of which blocked everything after it:**

1. **`give()` never delivered an item.** `CONTAINER_FAMILY`, `QUAL_FAMILY`,
   `QUAN_FAMILY` and `REAGENT_FAMILY` were declared nowhere, so the compiler
   emitted `push 0`; `FREE::give`'s first guard read `getFamily() != 0`, the
   Avatar is `SF_CONTAINER` = 6, and give returned at its first instruction
   for every caller — `take()` with it. The Zealan Mark, Ezrekal's elixir and
   the Key to the Clouds had all been handed over in dialogue and delivered
   nothing. Fixed by `FAMILY_CONSTANTS` in `u8c_symbols.py`.
2. **No chest in the game could be opened.** All four chest classes compile
   `if (intrinsic 254) { look() } else { openGump() }`, and ScummVM stubs
   254 to `I_true`. Fixed in the fork to `I_false`; the tracked engine patch
   was regenerated (it was 21 lines stale).
3. **Hrodny's chest was unclickable**, first buried in the hut's west wall
   column and then, after a first move, still behind the hut's 40-tall south
   wall. It now sits on the open ground outside her door at (21152, 8832, 0).

**Rebuild traps, both of which cost time today:**

- `build_scummvm.sh` applies the engine patch **only when it clones**; an
  existing `scummvm-lv/` tree is just recompiled. Edit that tree too, or
  `--clean`.
- **`scummvm-lv-console/scummvm` is a stale August binary.** Do not pass
  `LV_SCUMMVM=$PWD/scummvm-lv-console/scummvm`; the default
  `scummvm-lv/scummvm` is what `build_scummvm.sh` produces.
- After a rebuild the debugger stopped consuming `commands.txt` — the
  on-screen console takes keystrokes. `tools/playtest-linux/dbg.sh` drives it.

**Harness lessons worth keeping:**

- **The villages defeat short-step drivers.** `walkto.py`, `trek.py` and
  `hike.py` all pin in the Gunnar village; what gets through is a **2.5 s
  burst at mag 240 with a diagonal**. The Avatar also climbed onto a hut roof
  and got shut inside a hut where `exact_reach` reads the only standable
  level as the roof.
- **After the ceremony the camera stops following the Avatar**, which both
  freezes him once he leaves the fast area and breaks every NPC strike (the
  sprite pixel is measured from the window centre). `CameraProcess::moveToAvatar`
  recovers both; `trek.py` and `chase2.py` now call it.
- **An item is clickable only if nothing tall stands south of it** — neither
  the map validator nor `exact_reach` can see that.
- `scratchpad/climb13d.py` is still the only thing that climbs map 13.

## Current state

- Branch **`main`**, clean. Estate 26/26; all four artifacts match
  `ARTIFACTS.sha256`. `FIXED.DAT` is now **`278a48c3…`** — it moved twice on
  2026-09-03/04 (potions into the chest, then the `FLG_CONTAINED` fix).
  Detection unaffected (FIXED.DAT is outside the md5-5000 window) — no ScummVM
  rebuild has been needed for any of it.
- Nothing half-built. The playtest session on `:77` can be stopped freely.
- **`scummvm.ini` is now genuinely stock** — the four
  `keymap_ultima8_MOVE_*` lines the 2026-08-19 session believed it had
  reverted were still on disk and are now removed. Leave them removed;
  the ascent does not need them.
- Saves: slots 24-44 are the 2026-09-02/03 exit-test run, **44 "key
  respawned fresh map"** the forward one, archived as `cp8`-`cp28` in
  `~/lv-checkpoints/`. Slots 24-42 predate the FIXED.DAT chest fix and carry
  the old, unclickable placement in their baked map 10.
  Older: slot 4 `cp3-plateau`, slot 5 `cp3h-west-strip`, slot 6 "cave
  ascended 24001", slot 7 "through gate 11210", **slot 8 "plateau west
  12854"** (the forward one). Slots 1-3 untouched. Archived in
  `~/lv-checkpoints/` as `cp3k-*`, `cp3l-*`, `cp3m-*`. A savegame carries its own instantiated map, so verify map
  fixes on a fresh world, not from a checkpoint.
- **`EUSECODE.FLX` changed 2026-09-02** (the `_FAMILY` constants) and
  `ARTIFACTS.sha256` was re-recorded; the installed copy under
  `shared/u8-lv-patched/USECODE/` was refreshed too. Detection is
  unaffected — same md5-5000 and size — so no ScummVM rebuild. `FIXED.DAT`
  changed 2026-09-01 (two cave seam doorways).
- Both climbs are closed: the cave ascent works on stock keybindings 5/5,
  and the Cloud Cliffs walk base→summit unbroken. **New tools**:
  `tools/playtest-linux/pathfind.py` (BFS waypoints; `--engine-void` for
  routes across a floorless void, `--erode 1` to reject the one-lattice-row
  seams the engine refuses; `--water-margin`/`--allow-water` since
  2026-09-02, and `--step-z`), `walkto.py` (run gait by default — `nav.py`
  warned that walkers die to chasers and it was written at the walk gait,
  which cost two deaths) and `fight.py`. Record:
  `docs/playtest-2026-09-01-stock-bindings-climb.md`.

## Open questions

- **The four dialogue repairs are still PROVISIONAL and need Douglas:**
  E5/E6 (EZREKAL), T1 (TYORVI), T2 (THORDIS). Built into the deployed
  EUSECODE and verified in-engine, but unreviewed. See TODO "Decisions
  wanted".
- **Map 8's south route is thousands of units of floorless void.** The
  gate is reachable from `cp3h` at z=0 with no climb at all — the engine's
  `z <= 0` freebie support carries him over nothing, rendering as
  blackness. That is the project's own broken-design rule, on the critical
  path, in retail geometry. Decision wanted on whether it gets floored.
- **Is the cave ascent worth keeping as-is?** It works, but the launch
  window is 17 units wide with no landmark, and it is now known NOT to be
  required — it leads to a pocket. Leave it, mark it, or drop it.
- **`agent/village-pipeline` still exists on the remote**, identical to
  `main`. Delete when sure: `git push origin --delete agent/village-pipeline`.
- Undiagnosed and intermittent: a savegame load can trip the kernel's
  65534-run guard. The crash it caused is fixed; the runaway is not.
- Unexplained, seen once: left standing in the trench void with no input,
  the Avatar was found on **map 0** at (15967, 19711, 0) and back on map 8
  a moment later. No teleport egg is anywhere near. Not reproduced.

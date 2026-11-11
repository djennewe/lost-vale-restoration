# Playtest results, 2026-07-26

Driven from a Claude Code session with `tools/playtest/` (see its README).
Build under test: `EUSECODE.FLX` 1,498,680 bytes, md5-5000
`ce5098a57c9cf761f2ec9ecd87ae2dc3`. All four artifacts verified against
`ARTIFACTS.sha256` before launch, and again after a full rebuild partway
through, which reproduced all four byte-for-byte. Detection entry confirmed
live: the window titles itself "Ultima VIII: Pagan (Gold Edition + Lost
Vale/DOS/English)".

> **Correction.** The first version of this document reported that LV class
> ids had drifted two slots from the manifest. That was wrong, and the error
> was in the analysis, not the build. It indexed `EUSECODE.FLX` with the raw
> `FlexArchive`, but usecode class ids are offset from FLX entries by two:
> `u8_flex.py` `UsecodeFlexArchive` states `classid = entry - 2`
> (`CLASS_BASE_INDEX = 2`). Re-run with `get_class_data()`, **zero**
> manifest-pinned ids are empty and every class is exactly where the manifest
> and the map builders expect it. The id-drift section has been removed. What
> follows is what actually held up.

---

## Class ids are correct

Confirmed two independent ways.

The build's own assignment log pins each class where the manifest says:

```
NPC     0x0466 SIGRID          PIN     0x04E4 TYPEMONSKUL
NPC     0x0469 RAGNAR          PIN     0x04E5 TYPEPOTION
NPC     0x046A THORDIS         PIN     0x04E6 TYPEABACUS
NPC     0x046B ATLI            PIN     0x04E7 TYPEBEDROLL
NPC     0x0470 INGJALD         PIN     0x04E8 TYPEBULLWHIP
NPC     0x0471 HRODNY          PIN     0x04EA TYPEFEDORA
NPC     0x0473 TYORVI          PIN     0x04EC TYPEAOFRIZBEE
NPC     0x0474 EZREKAL
```

And reading the FLX by class id confirms the content matches:

| Class | npcNum | Content |
|---|---|---|
| 1126 | 102 | `Sigrid the hunter` |
| 1252 | 228 | `Strange skull` + the lore letter |
| 1253 | 229 | `potion` |
| 1254 | 230 | `abacus` |
| 1255 | 231 | `bedroll` |
| 1258 | 234 | `Fedora` |
| 1260 | 236 | `Ceremonial Shield of the Ancients Ones` |

So the dispatch tables are sound. **The defects below happen despite the right
class being present at the right id**, which makes them runtime problems, not
wiring problems.

---

## Per-test results

### 1. Conversation-freeze theory: not reproduced as stated

No `I_resetRef item=0` in any call logged. The specific prediction (intrinsic
`0x9A` returning 0, `kernel.cpp:311` treating objid 0 as a wildcard) did not
fire.

A different null-reference failure did, and it turned out not to need a click
at all. See "Map 10 first-load collapse" below, which supersedes the
click-based account originally written here.

The failure chain, for reference:

```
LV: I_resetRef item=106 type=0x0000
WARNING: Trying to access segment 0000!
WARNING: skipping bark of 'Resting, I am. Away, go.' because item invalid.!
WARNING: Non-existent process PID (0) in implies.!
Unloading map 10
Loading Fixed items in map 0
```

The zero is in `type`, not `item`. The bark is real LV content in inverted
Zealan order, so Thordis's class ran and reached her bark, then failed on an
invalid item reference.

This is worth taking seriously as a relative of the freeze theory rather than a
refutation of it: an invalid `this` item reaching a bark is the same family of
defect as a null objid reaching `resetRef`, and `Non-existent process PID (0)`
says a pid-0 wildcard really is in play somewhere on this path.

---

## First map change of a new game collapses to map 0 (quest-critical)

**Scope corrected, 2026-07-26.** This was written up as a map 10 defect. It is
not. Isolated with two controls on clean launches:

- **Idle 70s on the starting map 3, no teleport: no collapse.** So it is not a
  free-running `schedule()` timer.
- **Teleport to map 11 instead of map 10: collapses identically.**
  `Loading Fixed items in map 11` then straight to `Unloading map 11` /
  `Loading Fixed items in map 0`.

So the trigger is **the first map transition of a new game**, whichever map
that is, and the village has nothing to do with it. The one-shot `0405h` latch
is what makes it look like a property of whichever map you happened to visit
first. Anyone reaching any new map for the first time is dropped to map 0 and
frozen there.

That makes this the most serious thing found this session by a wide margin: it
is not a bug in one area, it is a bug on the way into the expansion.

**Method warning.** The first attempt at the idle control was invalid: two
ScummVM instances were running because an earlier `pkill` had not taken, so
`pgrep` returned two pids and the keystrokes went to the stale process while
the log being read belonged to the fresh one. Check `pgrep -f
scummvm-lv/scummvm` returns exactly one pid before trusting any observation.

### Original write-up (map 10 wording kept for the log excerpts)

**The first time a map is loaded, the game drops to map 0 and goes black.**

Reproduced on a clean launch with no interaction whatsoever: skip the intro,
start a game, open the debugger, `MainActor::teleport 10 7936 6656 0`. The
screen goes black with only the Avatar drawn. The only input was the teleport.

The trigger is the actor-creation path, and the log distinguishes the two cases
exactly. First load:

```
LV: Created actor npc 106 shape 707 mapNum 10 at (6144,6656,0)
...
LV: I_resetRef item=106 type=0x0000
WARNING: Trying to access segment 0000!
WARNING: skipping bark of 'Resting, I am. Away, go.' because item invalid.!
WARNING: Non-existent process PID (0) in implies.!
Unloading map 10
Loading Fixed items in map 0
```

Teleport to the same place again and it is clean, with no `item=106` line and
no collapse, because the actors now already exist:

```
LV: Slot 106 already has actor shape 707 mapNum 10 , updating pos to (6144,6656,0)
```

**Root cause found: `AVATAR::schedule()` runs a one-shot cutscene that never
comes back.**

With `UCMachine::traceAll` on across a fresh first load, the line immediately
before `Unloading map 10` is:

```
tick 452 running process 84, item 1, type 528, class 1025, offset 6288
```

Class 1025 is AVATAR (one of our three modified base classes), item 1 is the
Avatar, and offset 6288 = 0x1890 sits inside `Event 08: schedule()`.
Disassembling it shows the standard U8 cutscene pattern: save the Avatar's
position, freeze him, teleport to a hidden staging map, play something,
teleport back.

```
1867: push global 0405h 02h        ; 2-bit latch, "has this played yet"
186F: jne  -> 1979h                ; skip the whole scene if already set
1874: pop global 0405h 02h         ; set the latch
1881: spawn 0581h 1C19h            ; wait(), _gen_wait()'s retail target
188B: implies 01h 01h              ; <- "Non-existent process PID (0)"
188F: suspend
1890: ... getX / getY / getZ / Npc::getMap   ; save where we are
18CA: setAvatarInStasis(1)
18D0: push 0    push 0    push 4CFFh   push 3E5Fh
18DF: Npc::teleport(uword, uword, ubyte, ubyte)
```

Arguments go right-to-left, so that call is
`teleport(x=0x3E5F, y=0x4CFF, z=0, map=0)`. **The map-0 jump is a deliberate
teleport to a cutscene stage, not a crash.** What is broken is the return trip:
the scene's `wait()` is codegen'd as `spawn 0581:1C19` followed by `implies` on
the returned pid, and the log shows that `implies` receiving **pid 0**, so the
spawn failed. The process suspends on a wait that will never complete, the
Avatar is left in stasis on map 0, and the teleport-back at the end of the
routine is never reached.

**This also corrects the "first load only" explanation given above.** The
one-shot behaviour comes from the 2-bit global latch at `0405h`, which the
routine sets before it teleports, not from the `Created actor` versus `Slot
already has actor` difference. The second teleport is clean because the latch
is already set and the scene is skipped, which is why the collapse looks
load-dependent when it is really latch-dependent.

**Confirmed in-game 2026-07-26**, using the `--enable-text-console` build and
`tools/playtest/session.sh cmd`, which drives the debugger over stdin so
responses land in the log instead of an unreadable overlay:

```
debug> UCMachine::getGlobal 0x405 2
[0405 02] = 0          <- fresh game, before any map change
debug> MainActor::teleport 11 9728 1536 0
debug> UCMachine::getGlobal 0x405 2
[0405 02] = 1          <- after the first map change
```

with the transitions in the same log reading `map 3` -> `map 11` -> `map 0`.
The latch is real, it is set by the first map change, and it is what makes the
collapse one-shot. This was disassembly-only until the text-console build
existed.

npc 106 is Thordis (106 + 1024 = class 1130), the Hoskuld clan elder. Her
`I_resetRef item=106 type=0x0000` and failed bark happen ~385 log lines before
the map change and are a **separate** problem, not the trigger.

This matters more than anything else found this session: a player reaching the
Lost Vale village for the first time, by any route, gets dumped to map 0. It is
on the critical path and it is deterministic. It was originally written up here
as being caused by double-clicking her, which was wrong; the click was
incidental and the log lines were merely adjacent.

### 2. Sigrid: FAIL, with a control this time

Re-run with `tools/playtest/talk_to.py`, which captures, locates her sprite and
clicks in one invocation so she cannot walk out from under the coordinates.

With `UCMachine::traceAll` live, double-clicking her produces **only**:

```
tick ... running process ..., item 0, type 0, class 1025, offset 6121
```

Class 1025 is AVATAR, offset 6121 is his walk process. No class 1126, and no
other class at all. She turns to face the Avatar, which is engine-side Actor
behaviour and not usecode, and nothing else happens: no conversation, no bark.

The `traceAll` output is the control that makes this meaningful. Tracing is
demonstrably live at the moment of the click, so the absence of 1126 is a real
absence rather than a disabled trace. **Double-clicking Sigrid dispatches no
usecode.**

Her class is not dead, though: it ran during the first map load
(`running process 1723, item 0, type 0, class 1126, offset 397`). So the
question is specifically why `use` does not reach it.

### Superseded: the earlier "inconclusive" note

Class 1126 is present and holds her dialogue, and `UCMachine::traceClass 1126`
proves it runs:

```
tick 126268 running process 1723, item 0, type 0, class 1126, offset 397
```

An earlier draft of this document called her inert. **That claim is withdrawn.**
She has a wandering schedule, and every follow-up click was aimed at
coordinates read from an older screenshot, so it landed on empty ground.
Teleporting the Avatar does not reset her position, which is what made the
stale coordinates look reproducible. Only the very first click, taken while she
was still at her spawn, actually reached her, and that one produced a
turn-to-face and nothing else, with no tracing enabled at the time.

So the state of test 2 is: not yet properly run.

**Method note for the next attempt.** NPC positions must be re-read
immediately before each click, and even then a round trip is long enough for
her to move. `Kernel::toggleFrameByFrame` plus `Kernel::advanceFrame` is
probably the way to get a stable target, at the cost of having to step the
conversation forward by hand.

### 5. Item classes: bedroll produced no response

Double-clicking a bedroll at (12672,12800) gave nothing visible and no log
output. Class 1255 is present and is the bedroll. This one is a static object
so the stale-coordinate problem does not apply, but it was a single attempt
with no tracing and should be redone before it counts as anything.

### 3, 4, 6, 7, 8: not reached

---

## The `item 0` pattern

Worth recording because it shows up on every traced process, not just the ones
that misbehave:

```
tick 126268 running process 1723, item 0, type 0, class 1126, offset 397
tick 132786 running process 2902, item 0, type 0, class 1130, offset 793
tick 138310 running process 2738, item 0, type 0, class 1025, offset 6121
```

Class 1025 is AVATAR, so `item 0` on a class-level process is not by itself
abnormal. What is worth checking is whether the NPC schedule processes (1126,
1130) *should* be carrying their own objid there, given that Thordis's bark
fails with "item invalid" and `I_resetRef item=106 type=0x0000` repeats
steadily in the background. `item=106` looks like an npcNum arriving where an
objid belongs.

---

## What the session did establish

`tools/playtest/` drives ScummVM with the game in the background, so this
procedure can be run from a session without holding the machine. That part is
solid and is documented in its README.

## Next

1. **Fix the map 10 first-load collapse.** It is deterministic, it is on the
   critical path, and the two log variants (`Created actor` versus `Slot
   already has actor`) point straight at the actor-creation path in the engine
   patch. `I_resetRef item=106 type=0x0000` passing an npcNum where an objid
   belongs is the first thing to check.
2. **Sigrid's `use` never dispatches.** Her class exists, is correctly pinned,
   and runs on map load, so this is about how `use` reaches an npcNum-promoted
   Actor, not about wiring.
3. Re-run tests 3 to 8 once the collapse is fixed, since every one of them
   needs a stable map 10.

## Audio

Muting needs **both** config sections. `[scummvm] mute=true` alone is
overridden by `[ultima8] mute=false`. Also, ScummVM writes its config back on
exit, so edit the file with the game stopped or the running instance will
clobber the change.

## Method warnings for whoever runs this next

- **Class ids are offset by two from FLX entries.** Use
  `UsecodeFlexArchive.get_class_data(classid)`, never raw `FlexArchive[i]`.
  Getting this wrong produces a very convincing fake "everything drifted by
  two" result.
- **LV village NPCs wander.** Re-read positions immediately before clicking,
  and do not assume a teleport resets them.
- **Confirm the debugger actually closed** before clicking. If the console is
  up, clicks go to it and the game looks unresponsive.
- **Cheats start enabled** in this build. `Cheat::toggle` once turns them
  *off*, and `MainActor::teleport` then answers "Cheats are disabled".

---

## What the map 0 scene actually is

Disassembling on past the teleport, the scene body is:

```
18ED: spawn 0581h 1C19h          ; wait()
18FC: push 9   push 019Bh        ; frame 9, shape 411
1903: Item::create(uword, uword) ; -> [BP-0Eh]
1909: getZ +40 / getY -120 / getX ; position it near the Avatar
1938: Item::pop(uword, uword, ubyte)
1940: process Item::use()
194E: spawn 0581h 1C19h          ; wait()
195F: setAvatarInStasis(0)
1972: Npc::teleport(...)          ; back to the saved position
```

Shape 411 is the Shades apparition, and class 411 exists in the build (181
bytes, string `ghost`). So this is the LV intro vision: stage the Avatar on map
0, conjure an apparition beside him, play it, then restore him.

**Structurally the scene is intact.** Class 0x581 is present and demonstrably
runs, too: the trace shows `class 1409, offset 7229` (0x581, just past
0x1C19) executing repeatedly as a type-1 process, so `wait()` is not
universally broken.

**Not established:** whether the scene is hung or waiting for something. It was
observed not returning within about 25 seconds, and the screen showed only the
Avatar with no visible apparition, but "hung" is an inference. The apparition is
placed at `getY() - 120`, which may simply be off-camera. Before touching
`_gen_wait()`, the thing to determine is whether process 84 is still alive and
suspended: `Kernel::listProcesses` and `Kernel::processInfo` will say directly,
and that distinguishes a failed wait from a scene waiting on the
apparition's own usecode.

---

## RESOLVED, 2026-07-27: the collapse is fixed and verified in-game

The question the section above left open — hung or waiting — had a third
answer: **dead**. `Kernel::listProcesses` on map 0 showed no UCProcess at all
and nothing suspended. The process was killed, and the killer was the engine's
own map-change sweep.

### Root cause

`World::switchMap` fails every process with `itemNum != 0 && type != 1` on
every map change (`kernel.cpp` `killProcessesNotOfType(0, 1)` — retail U8
semantics, documented in the ScummVM source). The 1994 sources guard scenes
against exactly this with a statement-form pragma as the scene's first line:

```
[[PT_DEFAULT, NULL_REF]];    // AVATAR.UNK:1282
```

which their compiler compiled to `set info` (opcode 0x77), re-branding the
running process to itemNum 0, type 1 — unkillable on both criteria. **Our
codegen compiled the statement to nothing** (`u8c_codegen.py`, "pragma
statements carry no runtime meaning"), so `AVATAR::schedule()`'s scene kept
its event identity (item 1, type 0x210) and was failed *inside its own
`Npc::teleport()` call*. The VM loop exits on termination; the teleport-back
at `0x1972` was unreachable. The `0405h` latch had already been set, making
it one-shot.

Corrections to the analysis above, all verified:

- **The scene is the Lord British vision, not Shades.** `Item::create` gets
  `TypeLordBritish` (shape 411 is the ghost/apparition art, frame 9); the
  latch global is `lbSpoke`; map 0 is `MapLBBlackness` (`AVATAR.UNK:1277-1312`).
- **The `implies`/pid-0 theory is conclusively dead**: the collapse reproduces
  with zero `implies` warnings in the log, and the wait() completed in 242
  ticks (240 requested). `_gen_wait()` was never the problem.
- **The Avatar was stranded, not frozen**: map 0 renders fully, and
  `avatarInStasis` reads false afterward (a foreign `AVATAR::cachein`, see
  below, clears it).
- **Offset 6121 was `justMoved()`**, not "his walk process".
- **`I_resetRef item=106 type=0x0000`: the item was never the anomaly**
  (actor objids *are* npcNums; 106 is well-formed Thordis). The `type=0` is:
  `PT_*` constants in expression position are unknown identifiers compiled as
  `push 0` — 28 `resetRef(referent, PT_BARK/PT_PATHFIND/PT_ANIM/PT_ACTIVITY)`
  sites corpus-wide are silent no-ops (`PROC_TYPE_ALL` is 6, so type 0 is not
  a wildcard; it just matches nothing). Same defect family, still open.
- **The "`item 0` pattern" is benign**: trace lines print at process start,
  before the preamble's `set info` runs.

### The fix

`u8c_codegen.py` now emits `set info` for statement-form `[[PT_DEFAULT, …]]`.
Three referent forms, each pinned by exact per-class site-count matches
between 1994 source and retail bytecode (never guessed):

| Form | Bytes | Count evidence |
|---|---|---|
| `NULL_REF` / `NUL_REF` / `0` | `0A 01 0A 00 77` | POTION 3/3, TORWIN 2/2, DARION 1/1, FREE 5/5 |
| `referent[:Referent]` | `0A 01 40 06 4C 02 77` | METHOD 9/9, JENNA 2/2, MORDEA 1/1, DARION 1/1, STRATOS 2/2 |
| `Avatar:Referent` | `0A 01 0A 01 77` | FREE 2/2, STRATOS 1/1 |

All other `PT_*` types (values unpinned) still compile to nothing but now
warn loudly — 23 such sites in a full build, a ready-made work queue for
pinning `PT_ACTIVITY`/`PT_BARK`/`PT_ANIM`/`PT_PATHFIND`/`PT_FX` later.
`test_pragma.py` (24 asserts) guards the encodings and the deferrals.

Audit: the rebuild grew EUSECODE.FLX by exactly 194 bytes = the sum of
per-site insertions across 12 classes (AVATAR +22 = 3 null + 1 referent
site, LVFREE +65 = 11 null + 2 Avatar, MAGNET +21 = 3 referent, EAPUZL→
TYPEPEDESTALS +10, …). AVATAR's mnemonic-histogram delta is exactly the 13
inserted instructions; the ten byte-changed-size-unchanged classes are
LVFREE call-operand shifts only. Estate 16/16.

### In-game verification (fresh game, traceClass 1025)

```
tick 326 (still) running process 81, item 0, type 1, class 1025, offset 6295   <- re-brand live
tick 568 running process 81, item 0, type 1, class 1025, offset 6310           <- wait(240) done
Unloading map 11
Loading Fixed items in map 0
tick 568 (still) running process 81, item 0, type 1, class 1025, offset 6403   <- SURVIVES the switch
...
Loading Fixed items in map 11                                                   <- the return trip
```

Map sequence `3 → 11 → 0 → 11`; Avatar restored to the exact saved position
`(9728, 1536) m:11`; `[0405 02] = 1`; stasis false; no AVATAR process left
suspended. **A player entering the expansion now arrives.**

### Still open, found or confirmed during the fix

- **The vision is currently invisible and mute.** Mid-scene screenshot shows
  no apparition (shape 411 frame 9 draws nothing visible), and `lb.use()`
  dispatches shape 411 → class 0x19B GHOST, whose event table has *only*
  `look()` — there is no use() to run. The return trip is timer-driven
  (`wait 60/120`), so the blocker fix is unaffected; the player gets a ~6 s
  empty pause on the stage. Wiring candidate: the LBSCENE pattern (spawn the
  manifest-pinned TYPELORDBRITISH 1443 and puppet the created item), via a
  future `lv-patched/AVATAR.UNK`.
- **The foreign cachein is real and still unexplained**: `AVATAR::cachein`
  runs with `item 6359` on every map-0 load. Map 0 has **zero fixed items**
  (scanned), so 6359 is a NonFixed item — and the 494-npcNum audit covered
  fixed items only. `ObjectManager::objectInfo` on it next live session.
- **GUARD1 (0404) schedule active on map 11** via item 6346 — base-NPC class
  reached from an LV map item; unexamined.
- `install_lv.sh` died silently on Linux (`grep` under `set -euo pipefail`
  inside `$()` when scummvm.ini has no `[ultima8]` path) — fixed.
- Console-tree detection repatched: md5-5000 `56ae39ad746e58faf45e65f0bacad2ff`,
  size 1,498,874 — **interim values**; `ARTIFACTS.sha256` re-record is
  deliberately deferred until the map-constant fix (2a) lands, so there is
  one canonical record. Until then `sha256sum -c` fails on EUSECODE.FLX by
  design — do not "fix" it by rebuilding.

### Addendum, 2026-07-27: Fix 2a and the canonical re-record

The Map* constants landed the same night (31 names pinned in
`MAP_CONSTANTS`, `u8c_symbols.py` — evidence table in its comment). The
rebuild was size-neutral as designed: 33 bytes changed across 5 classes,
every one an old `push 0` operand becoming the pinned map number, so the
detection values (`56ae39ad…` / 1,498,874) did not move. The AVATAR guard
now compares `getMap()` against 3 and 0 — the vision is suppressed on the
Docks again — and all six EGGSHADES vale-teleports target map 10.

`ARTIFACTS.sha256` re-recorded (EUSECODE.FLX line only; FIXED.DAT
reproduced byte-identical, sha unchanged — the map pipeline is
deterministic). Both ScummVM trees rebuilt on the new detection entry;
`build_scummvm.sh` defaults updated to match. The vision round-trip was
re-verified in-game on the canonical build: map 3 → 11 → 0 → 11, Avatar
restored to (9728, 1536) m:11, latch 1, estate 17/17.

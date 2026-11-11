# Clean-room playthrough, attempt 1 — 2026-07-28

The milestone-1 exit test (PLAN.md 2.6): *one continuous no-cheat playthrough
from a fresh game through "Receive Bag of Reagents. END."* This is the record
of the first attempt.

**Result: incomplete.** The run reached **map 40 (Tenebrae interior)** without
a single `setGlobal`, teleport or cheat, which is further than any previous
session has walked. It stopped on **navigation**, not on a defect in the
restoration — see "Where it stopped" and "What this attempt actually
establishes".

Build under test (all four artifacts verified against `ARTIFACTS.sha256`
before launch, 4/4 OK, and the harness copy at `shared/u8-lv-patched/` is
byte-identical to all four):

| Artifact | sha256 (first 16) |
|---|---|
| EUSECODE.FLX | `1a41dda192575a25` |
| FIXED.DAT | `8e5d27ec3e816db1` |
| TYPEFLAG.DAT | `6360e6b3cbdd87a9` |
| U8SHAPES.FLX | `762ca62d473cadc3` |

Harness: `tools/playtest-linux/session.sh` on Xvfb `:77`, console build
`scummvm-lv-console/scummvm`.

## Rules observed

- **No `setGlobal`, no `MainActor::teleport`, no `Cheat::*`, no savegame.**
- `ObjectManager::objectInfo 1` and `UCMachine::getGlobal` were used as
  **read-only instrumentation** to record position and flag state. Reading
  pauses the engine but does not alter game state. Every state change below
  was produced by walking and clicking.

## What was played

| # | Beat | Evidence |
|---|---|---|
| 1 | Fresh game boots on the LV build; map 3, Avatar (14527, 5887, 8), HP 30/30 | `objectInfo 1` |
| 2 | Devon conversation on the shore, played to "Farewell, friend Avatar" | shots 01-04 |
| 3 | Walked inland and north to the Tenebrae gate | shots 05-17 |
| 4 | Gate guard conversation; "Open the gate!" → refused | shots 18-25 |
| 5 | Gate confirmed physically shut (portcullis) | shot 32 |
| 6 | Toran execution cutscene played in full — Mordea, the executioner, the beheading | shots 39-41 |
| 7 | `executionDone` (global `0x5B`) **0 → 1** | `getGlobal 0x5B 1` → `[005B 01] = 1` |
| 8 | Post-execution guard conversation ("You may go about your business.") | shots 43-52 |
| 9 | **Walked through the now-open gate: map 3 → map 40** | `m: 3` → `m: 40` |
| 10 | Crossed the map-40 pier north into the Tenebrae palace | shots 56-59 |

Nothing crashed. The base game is fully intact under the merged LV
artifacts — the opening, the conversation system, the scripted execution
cutscene and the map transition all behave normally.

## Where it stopped

Inside Mordea's great hall on map 40, around (13318, 8514, 48), unable to
find the lane north to either onward teleporter. Both onward transitions are
known and confirmed walkable in isolation:

- **map 40 → 39** (Tenebrae core, the LORDBRIT primary egg) — teleporter at
  (10456, 3296, 48)
- **map 40 → 7 → 8** (Mythran plateau + the LORDBRIT backstop egg at
  map 8 (2200, 2230, 8)) — teleporters at (13054, 2322, 48) and
  (9498, 19702, 8)
- and onward **map 8 → 9 → 11**, the Elemental Dungeon (quest steps 3-4)

This is a harness limitation (see "Navigation" below), not a progression
dead end. No LV content was reached, so **no quest step 1-18 was verified or
falsified by this attempt.**

## Findings

### F1 — `u8_map.py`'s teleport predicates and factory names are inverted

The engine is unambiguous (`teleport_egg.h`):

```cpp
bool isTeleporter() const { return _frame != 1; }
```

so **frame 0 is the teleporter (the trigger) and frame 1 is the target
(the arrival pad)**. `TeleportEgg::hatch()` reads the *trigger's* `_mapNum`
as the destination map and `_quality & 0xFF` as the teleport id.

`agents/map-populator/src/u8_map.py` has this exactly backwards:

- `is_teleport_trigger` → `frame == 1` (that is the **target**)
- `is_teleport_dest` → `frame == 0` (that is the **trigger**)
- `MapItem.teleport_trigger()` emits `frame=1` — an arrival pad
- `MapItem.teleport_dest()` emits `frame=0`, `quality=256+id`, `mapnum=dest`
  — a trigger

**The emitted bytes are correct.** `teleport_dest()` produces exactly the
record shape the base game uses for a trigger (verified against map 3's own
base-game egg at (11516, 1660, 48): frame 0, `mapnum=40`, `npcnum=134` as the
hatch range). That is why the 14 shipped LV teleport pairs work in-game and
why nothing needs rebuilding. Only the **names and predicates** lie.

This is not cosmetic: it cost this session a wasted leg. Reading the map-3
egg list through these predicates said the exit to Tenebrae was at
(11778, 4878) — which is the *arrival pad* for traffic coming the other way.
The real exit was at (11516, 1660). Anyone reasoning about connectivity from
these helpers reads the graph backwards.

**FIXED 2026-07-29.** Renamed to engine-matching names across all three
copies of `u8_map.py` and every call site — a pure rename, no semantic edit:

| was | now | frame |
|---|---|---|
| `teleport_trigger()` | `teleport_target()` | 1 — the arrival pad |
| `teleport_dest()` | `teleporter()` | 0 — the trigger |
| `is_teleport_trigger` | `is_teleport_target` | 1 |
| `is_teleport_dest` | `is_teleporter` | 0 |

`MapItem.__repr__` now prints the decoded id, destination map and hatch
range instead of the two mislabelled forms. **FIXED.DAT rebuilt
byte-identical** (`8e5d27ec…`), all four artifacts still match
`ARTIFACTS.sha256`, estate 23/23.

### F1b — `TELEPORT_TABLE`'s direction was backwards for all 14 LV ids

Found while fixing F1, same root cause. `build_all_maps.TELEPORT_TABLE`
recorded each id's `from_map`/`to_map` — and its `desc` — the wrong way
round. Checked against the built data, id 200's frame-0 teleporter sits on
map 9 pointing at map 8, i.e. it runs *Galjeron's Chamber → Plateau*, while
the table called it *Plateau → Galjeron's Chamber*.

**The shipped map data was never wrong.** The ids are allocated in
complementary couples (200/201, 202/203, …), so both directions of every
link have always existed and travel worked in-game — which is exactly why
14 pairs "verified" for months. Each row simply carried its partner's
description.

`verify_teleport_pairs()` had the matching inversion baked into its
expectation (it required the frame-1 target on `from_map`), so the two
errors cancelled and the gate passed. Both are now corrected together: the
table states the true direction, and the gate requires the **teleporter
(frame 0) on `from_map`** and the **target (frame 1) on `to_map`**, per
`TeleportEgg::isTeleporter()`. The synthetic archive and the three negative
controls in `test_map_roundtrip.py` were updated to build pairs the
engine's way round.

That the shipped FIXED.DAT still passes the gate *after* the expectation was
corrected is the real proof the data was always right.

### F2 — the Toran execution egg lives in NONFIXED.DAT, not FIXED.DAT

The Tenebrae gate is gated on global `0x5B`, which is written by **exactly
one** class in the whole FLX — 1155 `EXCUTION` — and read by classes 607,
1026, 1027, 1028, 1029, 1031, 1032, 1042, 1043 (the gate guards).

Class 1155 is dispatched as an UnkEgg (`quality + 0x47F`, so quality 4), and
**there is no quality-4 egg anywhere in FIXED.DAT** — base or built. It is in
`SAVEGAME/U8SAVE.000 → NONFIXED.DAT`, map 3, at **(11732, 5844, 48)**, hatch
range `npcnum=187` → ±352 units.

Consequence for this project's tooling: every scan that has been run against
`FIXED.DAT` alone has a blind spot. `map_walkability.run_event_eggs()` guards
LV eggs against label-not-a-class-id errors, but it cannot see base-game
dynamic eggs, so it cannot detect an LV item that *collides* with one.

### F3 — the 32-unit walkability raster is too optimistic for routing

`WalkGrid.flood()` over map 40 returns a clean 268-cell corridor from the
palace to the map-7 teleporter. The engine refuses it: the Avatar oscillates
against walls that the raster reports free. This is the same limitation
HANDOFF.md already records for the Tiny Tar crack ("a one-body-width aperture
cannot be adjudicated by the cell raster") showing up in a second place — the
raster marks a cell blocked only when a blocker covers the cell **centre**, so
furniture and thin walls in Tenebrae's interiors vanish. It is fine as a
connectivity check and unfit as a pathfinder.

### F4 — harness notes

- `session.sh dbg` intermittently fails to attach and reports "no response
  after attach+retry" while the command *has* in fact queued; a manual
  ctrl+alt+d then drains the whole backlog at once.
- **ScummVM appends command output to the same line as the `debug>` prompt.**
  A reader that slices the log from "lines present before I sent" loses the
  reply. Start one line earlier.
- `dbg` leaves the console **attached, and attached means paused** — clicks
  and drags sent in that state are silently discarded. One "the door will not
  open" dead end this session was just this.

## What this attempt actually establishes

The honest scope finding, which is the main output of the attempt:

**The clean-room exit test requires playing essentially all of Ultima 8 Pagan
before any Lost Vale content is reachable.** Quest step 1's primary trigger is
at the Tenebrae gate on map 39 and its backstop is on the Mythran plateau
(map 8); map 8 sits behind the base game's whole Tenebrae arc. Every previous
in-engine verification of LV content reached it by `MainActor::teleport`,
which is exactly what this test forbids.

That is not an argument against the test — it is the test doing its job on the
first run: it has already surfaced three real tooling defects (F1-F3) that the
teleport-driven sessions could not, because they never traversed the base game
by foot.

## Attempt 2 (2026-07-30) — prologue replayed hands-off; checkpoints exist

A second run, driven entirely by the agent, replayed the whole prologue
without a single cheat and left durable checkpoints:

- Fresh game → Devon → the plateau ramp → **the Toran execution cutscene
  (fired by walking into its box at map 3 (11732, 5844, 48))** → the
  post-execution guard conversation → the gate-guard conversation → **through
  the city gate onto map 40**. `executionDone` verified 1 in-engine.
- **Checkpoint saves** (ScummVM quicksave slot 1, copied aside to
  `~/lv-checkpoints/`): `cp1-map40.sav` — map 40 south end (13038, 14546, 48),
  clean, before the palace; `cp2-palace.sav` — inside the palace west wing
  (~12254, 7270, 48), two interior doors already opened. Load with
  `Ultima8Engine::loadGame 1` after copying the `.sav` back over
  `~/.local/share/scummvm/saves/ultima8.001`, or via the in-game diary.
- Neither save has been near any LORDBRIT egg (map 39 was never entered; map
  8 not reached), so `lbDone` is untouched by construction. **Verify it reads
  0 on load anyway before using a save as the clean-room base.**

What the attempt established about the palace leg:

- **U8 doors live in NONFIXED.DAT and are invisible to `WalkGrid`** — both as
  blockers (closed doors on "free" cells) and as passages (locked q=512
  doors on cells the flood routes through). Map 40's palace has shape-69/68
  doors where quality 0 = openable, **512 = locked**. Two q=0 doors were
  opened by double-click at point-blank range (interaction range is short;
  clicks from ≳150 units silently do nothing).
- **One first-time death**: the Avatar drowned near the execution dock when a
  blind stuck-recovery walk backed him into the Lurker's water. The game-over
  menu cannot be closed (`MenuGump::OnKeyDown` refuses Close when
  `ACT_DEAD`), which is what an unclosable Pagan diary means.
- The remaining blocker is not geometry but **live NPCs**: a patrolling
  guard body-blocks the west-wing rooms, and NPC positions are in
  NPCDATA/ITEMCACH — invisible to every static tool. Screenshot-driven
  micro-navigation converges too slowly against a moving blocker.

**Handoff: the remaining human leg is ~2 minutes.** From `cp2-palace.sav`:
walk north/east through the palace west wing to the pier, north to the
teleporter at **(13054, 2322)** → map 7 arrival (15071, 26239); walk to
**(9498, 19702)** → map 8 arrival (31583, 19135). **Stop there.** Do not
approach Mythran's house or (2200, 2230) — the LORDBRIT backstop egg. F5-save
(e.g. `plateau-cleanroom-base`). Everything after that save is agent work
again.

## Recommended next steps

1. ~~**Fix F1**~~ **DONE 2026-07-29** — F1 and F1b both corrected, FIXED.DAT
   byte-identical, estate 23/23.
2. **Starting line — DECIDED 2026-07-29 (Douglas): a base-game save at the
   Mythran plateau.** Pagan's prologue is played by hand once and snapshotted;
   the exit test is then **steps 1-18 continuous from that save**, still with
   no `setGlobal`, no debug teleport and no cheats. Rationale: the Pagan
   prologue is not the thing under test, and re-walking it on every attempt is
   pure overhead that has already consumed one full session.

   The snapshot must be taken **before** anything LV-specific has fired —
   in particular with `lbDone` (`0x6A6`) still 0 — so quest step 1 is still
   live from the save. Record the four artifact hashes it was made against;
   a savegame is only valid for the class-id/flag-bit layout it was made on
   (`shared/build/lv_manifest.json` pins those, and CLAUDE.md warns never to
   renumber a retired bit).
3. **If foot navigation stays in scope**, the raster is not enough. The
   engine's own `CurrentMap::isValidPosition` is the only authority; a
   pathfinder would have to reimplement `Box::overlaps` at full resolution the
   way `test_crack_geometry.py` already does for the crack.

## Artifacts from this run

- **Screenshots:** `docs/playtest-2026-07-28/` (63 frames, cropped to the
  640x480 game surface). See that directory's `README.md` for the beat-by-beat
  index; `39-exec.png` is the execution cutscene and `32-gate.png` the closed
  portcullis.
- **Navigator:** `tools/playtest-linux/nav.py` — waypoint driver with the
  isometric screen-direction mapping and stuck detection. The two non-obvious
  parts are that mapping (`screen_x = wx - wy`, `screen_y = (wx + wy) / 2`)
  and the log-reading fix from F4: ScummVM appends a command's reply to the
  same line as the `debug>` prompt, so a reader must start one line earlier
  than "lines present before I sent". It handles open ground fine and
  oscillates against interior walls (F3).

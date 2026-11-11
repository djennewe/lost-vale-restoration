# In-engine test, 2026-08-18 — F10: the Cloud Cliffs climb, walked

Session: `scummvm-lv-console` on `:77`, save slot 1 (`cp24-zealanmark`),
cheats ON (teleports need them). Artifacts rebuilt and re-recorded the same
day; `shared/u8-lv-patched/` synced to `shared/build/` before the run (see
Harness anomalies — it is not synced automatically).

## What this session set out to do

Two Tier-1 items from `HANDOFF.md`:

- **F10** — the Cloud Cliffs climb was unwalkable as shipped, so every
  playtest since 2026-08-17 reached the summit (and therefore Cloud City,
  and therefore quest steps 13-15) only by teleport.
- **F11** — the Tiny Tar potion would not stash into the backpack, which
  blocks carrying it to the temple and so blocks the organic DD-005 shrink
  entry.

## Verdicts

| Test | Question | Verdict |
|---|---|---|
| **A** | Was F10's diagnosis (`zd=0` footpads starve the mover of support) correct? | **NO — REFUTED at the source.** Support is read off an item's TOP face, so a `zd=0` tile does support standing at its own z. The prescribed fix (bump `zd` 0→1) would have made every path tile a blocker. |
| **B** | What actually made the climb unwalkable? | **The riser granularity.** `scanForValidPosition` probes an enumerated table, `SEARCH_OFFSETS_U8 = {0, -4, 4, -8, 8}`. The 2026-07-31 rebuild interpolated z linearly and produced risers of 1 and 2 — refused exactly as a 9-unit riser is. |
| **C** | Does the climb walk after quantizing the ramp to the 4-unit lattice? | **PASS on the risers, PARTIAL on the full ascent.** z rises continuously on foot on both legs driven (north 0→48, east switchback 48→56). The unbroken base→summit walk was NOT completed — the harness overshoots the one-tile switchback corners. |
| **D** | F11 — why does the Tiny Tar potion refuse to stash? | **PASS — FIXED AND VERIFIED IN-ENGINE.** The three potions were **interpenetrating solid geometry** (buried in the locked chest and the furniture beside it, both z [0,16), potions at z=4). Moved to clear floor; the potion now stows: `"Dropped item in backpack"`, Avatar weight 20 → 30, item flags `0xc` (contained). |

---

## TEST A/B — the diagnosis was wrong, and the fix would have made it worse

F10 was recorded as: *"A zero-height half-open box contains no z, so the
mover finds no support on it… FIX: bump zd 0->1 for the flat tiles in the
TYPEFLAG patch step."*

That is not what the engine does. `CurrentMap::getPositionInfo`
(`current_map.cpp:742`) computes support from the item's **top face**:

```cpp
if (si->_flags & supportmask && ib._z + ib._zd > supportz && ib._z + ib._zd <= target._z)
    supportz = ib._z + ib._zd;
...
if (supportz == target._z && (landz + 8 >= target._z || GAME_IS_CRUSADER))
    info.supported = true;
```

A tile at z=48 with `zd=0` has top 48, so it supports standing at z=48. It
is also incapable of blocking, because `Box::overlaps` needs
`_z + _zd > o._z` and a zero-height box never satisfies it.

**Bumping `zd` to 1 would have broken the map.** An 8-unit-tall tile at
z=48 spans [48,56), which *does* overlap the Avatar's body box [48,88) —
so every path tile would have become a blocker, and the surface you could
stand on would have moved 8 units up. The footpad was never the defect.

A faithful port of `getPositionInfo` run against the shipped `FIXED.DAT`
confirms it: **all 89 climb tiles were already standable**. The static
model saw nothing wrong because nothing was wrong *statically*.

### What was actually wrong

When a walk step lands unsupported, `AnimationTracker::step` falls back to
`CurrentMap::scanForValidPosition`, which does not scan a range. It probes
a fixed table:

```cpp
static const int SEARCH_OFFSETS_U8[] = {0, -4, 4, -8, 8};
static const int SEARCH_OFFSETS_CRU[] = {0, -1, 1, -2, 2, -3, 3, ...};
```

U8's table has no ±1, ±2 or ±3 — Crusader's does, with a comment
explaining that Crusader has floor pieces at 1-pixel offsets. **A walking
actor in U8 can change z by 0, ±4 or ±8 and by nothing else.**

The 2026-07-31 rebuild read the limit as "at most 8 units" — the builder
comment said so in as many words — and interpolated z linearly over 89
tiles for 118 units, giving 58 risers of 1 and 30 of 2. Not one of them is
in the table. 67 of the 89 tile tops were not even multiples of 4.

There is a second, compounding wrinkle: the two collision routines
disagree about `zd=0`. `getPositionInfo` uses `Box::overlaps` (a
zero-height box never blocks), while `scanForValidPosition` computes its
invalid span arithmetically as `[pt.z - z - zd + 1, pt.z + izd - z - 1]`,
which for `izd=0` still clears the mask at `vert=0`. So a flat tile one
unit above you invalidates standing where you are, while offering support
only at an offset the scanner never probes.

### The fix

`build_map_13.py` now interpolates in **steps**, not world units:

```python
CLIMB_Z_STEP = 4
CLIMB_Z_TOP  = 120          # was 118 — not a multiple of the step
steps = CLIMB_Z_TOP // CLIMB_Z_STEP
z = CLIMB_Z_STEP * ((steps * k + last // 2) // last)
```

88 intervals carrying 120 units in 4-unit steps: **30 risers of +4 and 58
flats**, every one in the engine's table, and every tile top on the
lattice. The summit plateau's four hardcoded `z=118` sites now follow
`CLIMB_Z_TOP`.

Two tools were carrying the same wrong reading and were corrected with it:

- `exact_reach.py` allowed any `|dz| <= step_z`. It now offers only the
  table's entries clipped by `step_z`. **This is what makes the model able
  to catch the defect at all**: re-run against the shipped `FIXED.DAT` it
  now reports the summit and TRIGGER 209 as unreachable — the first static
  reproduction of F10. Against the rebuilt map both pass, and map 13
  reachability goes 91.6% → 97.7%.
- `test_route_reach.py` asserted `max(riser) <= 8`, which risers of 1 and 2
  satisfy. That assertion is why this shipped. It now asserts **membership
  in the table**, not magnitude, plus that `CLIMB_Z_TOP` is on the lattice.

## TEST C — the climb, walked — **PASS on the risers, PARTIAL on the full ascent**

Repositioned to the ramp foot at (4096, 10240, 0) and held the walk north.
No teleports during the ascent; z is the engine's own reading of the
Avatar's position after each 2-second burst.

| burst | position | z |
|---|---|---|
| foot | (4096, 10240, 0) | 0 |
| 1 | (4096, 9736, 4) | 4 |
| 2 | (4096, 9040, 12) | 12 |
| 3 | (4096, 8440, 20) | 20 |
| 4 | (4096, 7736, 28) | 28 |
| 5 | (4096, 7136, 32) | 32 |
| 6 | (4096, 6536, 40) | 40 |
| 7 | (4096, 5840, 48) | 48 |

Every z matches the quantized ramp for that y, and x stays pinned to the
one-tile path line at 4096. Screenshot: `A2-climbing-midway.png` (the
Avatar mid-ramp in the warning zone, terraced bands visible).

The east switchback leg climbs too, driven from the corner at
(4096, 5760, 48):

| burst | position | z |
|---|---|---|
| 1 | (4304, 5760, 52) | 52 |
| 2 | (4616, 5760, 56) | 56 |
| 3 | (4928, 5760, 56) | 56 |

### What this test does NOT show

**The continuous base→summit walk was not completed.** Twice the Avatar
overshot a switchback corner and fell to z=0: walking north past the
corner at (4096, 5760) leaves the ramp entirely (the path turns east
there), and a 1-second east burst carried him from x=4928 to x=5312,
past the (5120, 5760) corner and off the edge. Both are the harness's
coarse bursts missing a **one-tile-wide** turn, not the map refusing —
and the corrected `exact_reach` flood reports the summit and TRIGGER 209
reachable over the same geometry.

It is still worth flagging for the exit test: **the switchback corners
are one tile wide and easy to walk off.** A human with fine mouse control
will do better than 1-second bursts, but this is the part of the climb
most likely to frustrate.

Before this change the same walk left z at 0 — the Avatar simply walked
off the ramp onto the base terrain, which is why the 2026-08-17 session
recorded "walking wedges".

## Findings not in the plan

- **F14 — 43 surface tops on map 13 are still off the 4-unit lattice**, and
  they are dressing, not path: `build_narrow_ledge` places cliff-face detail
  at `z = 80 + i*2` (→ 82, 86, 90, 94), and other zones place rocks at
  z=105/106/110/114. These are `SI_LAND|SI_SOLID` with `zd=8`, so each is a
  phantom standing level the walk scanner cannot reach — the same family as
  the bones that were moved off the ledge on 2026-07-31. They do not block
  the route (the corrected flood passes), so they were left alone rather
  than churned mid-verification. Worth a sweep: quantize decorative z the
  same way. Maps 10/11/17/18 have 6/43/2/2 such tops respectively.
- **F15 — `ARTIFACTS.sha256` had been stale for EUSECODE.FLX since
  2026-08-17.** Commit `8af416d` (the T2 THORDIS re-gate) asserted "Same
  token length — no offset shift, detection hash and saves unchanged" and
  did not re-record. The token lengths match but the *flag numbers* differ,
  so the bytecode does. `build_scummvm.sh`'s `LV_MD5`/`LV_SIZE` had been
  stale since 2026-07-28 for the same reason (E5/E6/T1/T2 each moved the
  bytes). Both are now corrected; the build is reproducible (two
  consecutive builds match). The compiled console binary already carried
  the current md5, so detection was never actually broken — but it was one
  ScummVM rebuild away from being.
- **F16 — the drag telemetry does not mean what F13 claimed.**
  `"Dragging item %u"` is printed in `mouse.cpp` *before*
  `StartDraggingItem` runs its `canDrag`/`canReach` checks, so the line
  appears even when the drag is immediately refused. F13 (2026-08-17)
  recommended log-verifying pickups on that line. It is not sufficient
  evidence of a successful grab; `total weight` from
  `ObjectManager::objectInfo 1` still is.

## TEST D — F11, the Tiny Tar stash — **PASS**

Not solved, but the search space is now much smaller, and the previous
leading hypothesis is dead.

The refusal is silent because `GameMapGump::DraggingItem` returns
`backpack->CanAddItem(item, true)` *while dragging*; a false there sets
`DRAG_INVALID` and the release does nothing at all. So "nothing happens"
is the expected symptom of a `CanAddItem` false — which is why the
container check was the natural suspect.

`CanAddItem` can only return false for five reasons. Four are now ruled
out with evidence:

| branch | verdict |
|---|---|
| `item->getObjId() < 256` (actors don't fit) | **Ruled out.** npcNum 229 is outside the 100-116 window `Map::loadFixedFormatObjects` promotes to Actors, so the potion loads as a plain Item with an objId ≥ 256. |
| snake-eating container check | **Ruled out.** Shape 859 is `SF_GENERIC`, not a container. |
| `volume + item->getVolume() > capacity` | **Ruled out.** The backpack holds **three items** — a sword, a shield and the quality-20 key — against capacity 175, and the potion's volume is 1. Screenshot: `D1-backpack-nearly-empty.png`. |
| `getTotalWeight() + item->getTotalWeight() > 40 * str` | **Ruled out.** `ObjectManager::objectInfo 1` reads `total weight: 110`, `str: 15` → 110 + 10 against a limit of **600**. |

Shape 859's TYPEFLAG entry is also byte-identical to its donor (766,
"potion"): `SI_SOLID`, `SF_GENERIC`, footpad (1,1,1), wt 1, vol 1 — so
`canDrag()` passes (not fixed, non-zero weight) as well.

**So `CanAddItem` should be returning true, and the refusal is probably
not in the container path at all.** The remaining candidate upstream is
the drop target itself: if `TraceCoordinates` does not return
`kMainActorId`, the "dropping on self" branch never runs, and `DropItem`
falls through to the reach/throw path — which puts the potion back on the
ground near where it started. That is indistinguishable, on screen, from
"the stash was refused".

The three potions sit **on top of Hrodny's chest**, which is a large
`SF_CONTAINER` sprite, and the trace is taken at the cursor pixel offset
by `dox/doy` (where the item was grabbed). The 2026-08-17 session verified
the *drop* pixel was on the Avatar, but the trace point is not the cursor
point.

### The cause: the potions were buried inside solid boxes

Checking the potions' boxes against every solid on map 10 found the
defect, and it is geometry, not engine behaviour:

| item | occupies |
|---|---|
| locked chest, shape 618 at (20992, 8704, 0) | x 20897..20992, y 8641..8704, **z [0,16)** |
| furniture, shape 526 at (21024, 8768, 0) | x 20961..21024, y 8705..8768, **z [0,16)** |
| potion 1, at (20968, 8710, **4**) | x 20937..20968, y 8679..8710, z [4,12) |
| potion 2, at (21008, 8710, **4**) | x 20977..21008, y 8679..8710, z [4,12) |
| potion 3, at (21048, 8710, **4**) | x 21017..21048, y 8679..8710, z [4,12) |

All three overlap shape 526; two also overlap the chest itself. The
builder comment said they "sit ON the locked chest's cell so they read as
its contents" — but z=4 is not on top of a 16-unit-tall box, it is 12
units **inside** it, and the x pitch had drifted them off the chest and
into the neighbouring furniture as well.

An item interpenetrating a solid is precisely the state that defeats
drag-and-drop: `avatar->canReach()` sweeps a line of sight that the
enclosing box blocks, and `GameMapGump`'s trace resolves to the solid
rather than to the Avatar. It also explains why the *other* two shape-859
potions — Ezrekal's shelf stock, same shape, same npcNum, overlapping
nothing — were never reported as unstashable.

**Fix applied** in `build_map_10.py`: the three potions now sit on clear
floor beside the chest, each overlapping no solid and with no tall
neighbour to sort against. Verified statically after the rebuild: **0
solid overlaps, all three `valid=True supported=True`**. Screenshot of
the new placement: `D3-potions-on-clear-floor.png`.

### Verified in-engine

Retested on a **fresh world** rather than from `cp24`, and that detail
matters: a savegame carries its own instantiated map, so loading cp24
restored the OLD potion positions and the paint-cycle spam came straight
back. **A FIXED.DAT placement change is invisible to any save whose map
was already instantiated.** Worth remembering before "verifying" a map fix
from a checkpoint.

On a new game, cheats on, `debugflag_enable Object`, Avatar teleported
beside the potions at (20860, 8770, 0):

| step | observation |
|---|---|
| probe the potion pixel | `Item 2954 (class Item, shape 859)` |
| Avatar before | `Container vol: 175/250, total weight: 20, items: 1` |
| drag onto the Avatar | `Dragging item 2954` → `Dropping object 2954` → **`Dropped item in backpack`** |
| Avatar after | `total weight: 30` — exactly the potion's weight (TYPEFLAG wt 1 × 10) |
| the potion itself | `Item 2954 … (255, 255) … f: 0xc` — contained, position replaced by a gump slot |
| the pack | one Tiny Tar vial inside (`D2-potion-stashed.png`) |

Paint-dependency cycles on the new build: **0**.

### One rejected fix worth recording

The first correction put the potions on the shape-526 furniture **top** at
z=16 — geometrically clean (0 overlaps) and properly supported, since 526
is `SI_LAND` while the chest is `SI_SOLID` without `SI_LAND` and would
leave them unsupported. It was still wrong: resting a small box exactly on
a tall neighbour's top face with overlapping XY makes the renderer's depth
sort unresolvable, and the engine logged
`Cycle in paint dependency graph 859 -> 526` **10,956 times in a few
seconds**. The shipped placement is floor level, clear of both boxes and
of anything tall enough to sort against.

## Harness anomalies

- **`shared/u8-lv-patched/` is not synced by anything.** `install_lv.sh`
  installs into `shared/data/u8-install/`, but the playtest harness runs
  out of `shared/u8-lv-patched/`, which is maintained by hand. Its
  `FIXED.DAT` was from 2026-07-31 and its `EUSECODE.FLX` from 2026-08-17.
  A playtest can therefore silently run against stale artifacts. All four
  were copied in by hand before this run. **This deserves a sync step or a
  guard** — it is the kind of thing that invalidates a whole session's
  verdicts without any visible symptom.
- **Batching with `cmd` blocks `dbg` for as long as the backlog takes.**
  Queuing 600 `objectInfo` lines made every subsequent `dbg` report "no
  response after attach+retry" for several minutes while the backlog
  drained; the commands themselves all executed correctly, just late. The
  existing warning covers ordering, not this. Keep batches to ~50.
- `nav.py` drifts off a one-tile-wide path: driving to (4096, 10240) left
  the Avatar at (4528, 9264) — 432 units east of the ramp, on base terrain
  at z=0, which reads exactly like "the climb does not work". Controlled
  `walk` bursts along a known bearing were needed instead.
- The session comes up in the opening Devon conversation, whose AskGump is
  modal and makes the debugger answer nothing. Click "Goodbye." and click
  through the farewell bark before anything else.

## Disk changes

- `agents/map-populator/src/build_map_13.py` — climb quantized; `CLIMB_Z_STEP`
  added, `CLIMB_Z_TOP` 118 → 120; summit literals follow the constant.
- `agents/map-populator/src/exact_reach.py` — vertical model corrected to the
  engine's offset table; `Z_SEARCH_OFFSETS_U8` exported.
- `agents/map-populator/src/test_route_reach.py` — riser assertion now tests
  table membership; lattice assertion added.
- `build_scummvm.sh` — `LV_MD5`/`LV_SIZE` updated to the current EUSECODE.
- `agents/map-populator/src/build_map_10.py` — the three Tiny Tar potions
  moved out of the chest/furniture solids onto the shape-526 top at z=16.
- `shared/build/ARTIFACTS.sha256` — re-recorded twice (EUSECODE catch-up +
  FIXED for the climb, then FIXED again for the potion placement).
- `shared/u8-lv-patched/{STATIC,USECODE}/*` — synced to `shared/build/`.
- `docs/playtest-2026-08-18-f10-climb/` — screenshots.

Test estate: **26/26 PASS**. Route/reach suite: **59/59 PASS**.

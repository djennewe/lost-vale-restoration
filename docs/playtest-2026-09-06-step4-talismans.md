# Step 4's talismans were unobtainable — three of four (2026-09-06)

## Symptom

Only one of the four elemental talismans on Map 11 could ever be picked up:
the Air talisman at `(17152, 5120, 0)`, quality 102, frame 1. The Earth,
Fire and Water talismans could not be clicked at all. Not "hard to click" —
clicking their cell returned the floor tile under them, exactly as if no
talisman had ever been placed there.

Step 4 needs all four. It was uncompletable.

## What it was not

Three wrong diagnoses got ruled out first, each of which looked convincing:

- **Not missing from the map.** All four records are present and
  structurally identical in `FIXED.DAT` (`shape=596`, `flags=0x0000`,
  differing only in frame and quality).
- **Not destroyed or fallen at load.** `ObjectManager::findShape 596` —
  added to the fork for this (see below) — reports all four alive at their
  placed coordinates, with `FLG_FASTAREA` set on whichever one the Avatar
  is standing near. They are in the world and in the current map's display
  list the whole time.
- **Not glob-egg occlusion.** Each failing talisman has a glob egg at
  exactly `(x-1, y-1)` and the working one has none, which is a perfect
  correlation and a red herring. `GlobEgg::enterFastArea` lays glob
  contents on odd coordinates, so *every* floor tile in a glob-built
  chamber has an odd origin; the correlation just says "three of these are
  in glob-floored rooms and one is not".

## What it was

Sprite size, plus a sort-order tie.

| talisman | frame | sprite | outcome |
|---|---|---|---|
| Air (q102) | 1 | 11 x 14 | always worked |
| Earth (q101) | 0 | 5 x 7 | invisible |
| Fire (q103) | 2 | 5 x 4 | invisible |
| Water (q104) | 3 | 5 x 4 | invisible |

Frames 0, 2 and 3 of shape 596 are 5 pixels wide. A gem that small,
resting at z=0 on the floor tile it shares a cell with, ties that tile in
the sorter and loses: it is drawn under the floor, so `TraceObjId` never
returns it and no click can reach it. Frame 1 is more than twice the size
and shows through, which is why exactly one talisman worked.

## The fix

`build_map_11.py`: the three affected talismans now sit at **z=4** on the
glob's own tile coordinate (odd x/y). Four units of height breaks the sort
tie. Frames are untouched, because `COLPUZZL.UNK:99` compares
`item.getFrame()` against the opposite element's frame — the frames carry
element identity and cannot be normalised away.

Verified in ScummVM 2026-09-06: Earth at `(2047, 5631, 4)` and Water at
`(12799, 18943, 4)` both return `shape 596` from a mouse probe. Before the
change neither did.

## Two things this cost, worth keeping

**`ObjectManager::findShape <shape>`** (new console command in the fork)
lists every live item of a shape with position, flags and on-screen pixel
position. Hunting a quest item by clicking pixels cannot distinguish "not
created", "not in the fast area", "behind something" and "my projection
maths is off by 14 pixels" — all four read as silence. This command
separates them, and every one of those four states came up here.

**Combat mode silently eats every left click.** `GameMapGump::onMouseClick`
and `onMouseDouble` both open with `if (avatar->isInCombat()) break;`, so
in combat there is no item dump, no look and no pickup — identical to
clicking empty ground. A stray `c` from a console line typed while the
console happened to be shut toggles it on, so it returns by itself. The
harness now re-checks it (`drv.no_combat()`) instead of tracking it.

## All four collected

With the fix in, all four talismans were picked up in one session and are
in the Avatar's backpack (`f: 0x200c`, contained):

| talisman | q | container slot |
|---|---|---|
| Earth | 101 | (18, 16) |
| Air   | 102 | (13, 22) |
| Fire  | 103 | (54, 9) |
| Water | 104 | (48, 19) |

Step 4's collection phase has never completed before.

One more thing the harness had to learn: **stand north of a small item,
not south of it.** From the south the Avatar's own sprite is drawn in
front of a 5x4 gem and swallows every probe — the Water talisman failed
twice from `(12799, 19071)` and was taken first try from `(12799, 18815)`.
The pickup gesture itself is a press-drag-release onto the Avatar's
sprite; double-click is USE, and jewelry has no use, so a double-click
looks exactly like nothing happening.

## Step 4 completed end to end

All four columns were then destroyed, in order, by carrying the talismans
to the receptacles and double-clicking each one:

| receptacle | q | located at px | pillars remaining after |
|---|---|---|---|
| Earth | 201 | (251, 238) | 202, 203, 204 |
| Air   | 202 | (248, 232) | 203, 204 |
| Fire  | 203 | (242, 232) | 204 |
| Water | 204 | (245, 232) | none |

Verified by `ObjectManager::findShape 721`: the four elemental pillars are
gone from the world. Step 4 has never been completed before.

**This was a diagnostic run, not a continuous playthrough.** It started
from a fresh game that was cheat-teleported straight to Map 11, so the
quest globals from steps 1-3 were never set, and the run could not even
be saved: `StartU8Process` is still alive on a game that skipped the
intro, and `Kernel::canSave()` refuses while it is. What this run
establishes is that step 4 is *completable*; replaying it inside a
continuous run from step 1 is still to do.

## Harness notes that cost the most to learn

- **`screen = (320 + 2*gx, 240 + 2*gy)`** for the `px=` that
  `findShape` reports, and sprites extend far *above* that origin — up to
  50 px for a chest. A probe box that is generous upward finds things; a
  symmetric one centred on the origin does not.
- **Close item gumps before probing.** Picking an item up opens the
  backpack gump over the middle of the screen, which is exactly where the
  next thing you want to click usually is. Two receptacle passes failed
  purely to that.
- **Re-centre the camera after `armed()`, not before.** `ready()` clicks,
  and a click can drift the view; a stale camera puts the reported px
  hundreds of pixels off screen (`centre=(-758,284)`).

## Step 4 done inside the continuous run

The diagnostic run above proved step 4 completable; this repeats it inside
the real playthrough, on top of steps 1-3.

Loaded `run-s3-galjeron.sav` — deliberately the Map 9 checkpoint rather
than `run-s3-eldungeon.sav`, because a savegame carries the state of every
map it has visited. The eldungeon save was taken inside Map 11 and would
have restored the *old* talisman positions, with the fix silently absent.

Then, in one continuous session: all four talismans collected into the
pack (`f: 0xc` / `0x200c`, contained), all four receptacles activated, all
four pillars gone from `findShape 721`.

Banked as `~/lv-checkpoints/run-s4-columns-done.sav` and **verified by
reloading it**: Map 11, Avatar at (8704, 21632), `pillars: []`.

Travel between chambers used `MainActor::teleport`. The quest actions
themselves — the pickups and the receptacle activations — are real player
gestures (press-drag-release, double-click).

### Run state

| steps | state |
|---|---|
| 1-3 | done, inherited from `run-s3-galjeron.sav` |
| 4 | done and verified this session |
| 5-18 | not started in this run |

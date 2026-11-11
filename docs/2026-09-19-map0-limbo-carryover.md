# Map 0's limbo items ride into the next map (2026-09-19)

Chasing finding 1 of `docs/playtest-2026-09-18-map10-walk.md`: two robed,
staff-carrying figures stand on Map 10's lake island and pier, and a
look-click on one resolved an object whose map is 12. That report called it
"an actor whose map is 12 renders on Map 10". **That was wrong about the
object and wrong about the cause.** The mechanism below is reproduced from a
new game in four commands.

## What it actually is

Every map switch in the session routes through map 0 once, and map 0's
contents are never unloaded, so they land on the destination map.

1. **Map 0 is U8's limbo**, and its `NONFIXED.DAT` entry inside
   `SAVEGAME/U8SAVE.000` holds 63 sixteen-byte records, each describing a
   base-game NPC: shape, frame, npc number, and the map that NPC belongs to.
   Records 3, 4, 6 and 7 are the four ghouls (shape 142, npc 41-44, map 31);
   seven more carry shape 200, npc 52-60, maps 12 and 14.

2. **The engine loads them as ordinary items.** `Map::loadNonFixed` passes
   extended flags of 0 (`map.cpp:63`), and NPC shapes are container-family,
   so `ItemFactory::createItem` returns a `Container` for each. They are
   plain map furniture that happens to look like a person, which is why the
   figures have an NPC's sprite but no `FLG_IN_NPC_LIST`.

3. **Leaving map 0 skips the cleanup.** `World::switchMap` guards the
   writeback and the fixed-item unload with `if (oldmap != 0)`
   (`world.cpp:158`), and `CurrentMap::getNum()` returns 0 both when no map
   is loaded yet and when the current map really is map 0
   (`current_map.cpp`). `CurrentMap::loadMap` never clears `_items[][]` on
   its own — it relies entirely on `writeback()` having emptied them. So
   switching away from a genuinely loaded map 0 leaves all 63 limbo items in
   the current map's chunk lists, and the destination map's own items are
   loaded on top of them.

4. **They then become permanent.** At the next map switch `writeback()` runs
   normally, and every one of those items lacks `FLG_IN_NPC_LIST` and
   `EXT_FIXED`, so it is pushed into the destination map's `_dynamicItems`
   and recreated on every later load of that map, for the rest of the
   session.

The items keep the world coordinates stored in their limbo records, so they
land wherever those coordinates fall on the new map. On Map 10 the shape-200
records at (14495, 19039, 56) and (14047, 18751, 56) fall on the lake, which
is why two of them stand on the island deck and the causeway.

## Reproduction, from a new game

```
session.sh start                        # new game, Avatar on map 3
ObjectManager::findShape 200            # 7 found, 0 Container
Cheat::toggle
MainActor::teleport 10 13895 18700 8
ObjectManager::findShape 200            # 16 found, 7 Container
ObjectManager::findShape 142            # 8 found, 4 Container
```

With the Actor debug channel on, that single teleport logs three teleports
and three map loads:

```
Loading Fixed items in map 10
Actor::teleport: 1 to 10 (13895, 18700, 8)
Unloading map 10
Loading Fixed items in map 0
Actor::teleport: 1 to 0 (15967, 19711, 0)
Loading Fixed items in map 10
Actor::teleport: 1 to 10 (13895, 18700, 8)
```

Note what is missing between the map-10 unload and the second map-10 load:
there is no `Unloading map 0` line, because that debug line sits inside the
same `oldmap != 0` guard. The hop happens on the **first** map switch of a
session only; later teleports log a single map load and add no items. What
causes it is answered below.

## Scope

- **Not LV map data.** Map 10's `FIXED.DAT` entry holds exactly two shape-200
  records, npc 114 and npc 116, at (20224, 7680) and (12800, 12544) — the
  Gunnar villager and Ezrekal. Map 10's `NONFIXED` entry is empty. The
  phantoms are in neither.
- **Not the LV engine patch.** The `oldmap != 0` guard and the missing clear
  in `loadMap` are both stock ScummVM. The fork's only change in this area is
  the npc 100-116 promotion in `Map::loadFixedFormatObjects`, which the
  phantoms do not go through (their npc numbers are 41-60).
- **Every LV plate taken after a debug teleport contains them.** They are
  furniture a player would not see if the map-0 hop did not happen, so any
  screenshot of an LV map from any past session may show base-game NPC
  sprites that are not placed content. This retro-explains the two figures in
  `R4-lake-pier-island.png` and `R4b-island-figures-3x.png`.
- **Whether normal play hits it is untested.** With no commands at all, a new
  game loads only map 3 and stays there for at least 90 seconds. The hop was
  observed only as part of the first `MainActor::teleport`. What calls
  `MainActor::teleport(0, ...)` is not identified; the third teleport in the
  trace restores the Avatar to the exact coordinates the first one asked for,
  which is the signature of a save-position/hop/restore path.

## The fix — applied 2026-09-19

One guard in `World::switchMap` (`world.cpp:158`). The test wants to be "is a
map actually loaded", which is the `Map *` pointer inside `CurrentMap`, not
the map number, so `CurrentMap` gained a `hasMap()` accessor beside
`getNum()`:

```cpp
uint32 oldmap = _currentMap->getNum();
if (_currentMap->hasMap()) {        // was: if (oldmap != 0)
```

Everything inside the branch is unchanged. `Map::unloadFixed()` on map 0 is
safe, since `FIXED.DAT` entry 0 is empty, and map 0 now gets the same
writeback every other map gets.

Fork commit `e0d6084d` on `lost-vale`;
`tools/scummvm-patches/0001-lost-vale-engine.patch` regenerated and now
carries 18 files (was 16 — `world.cpp` and `current_map.h` are new). The
regenerated patch was checked against a throwaway worktree of the pinned base
`01bd8879` and applies cleanly. The rest of the patch is byte-identical: the
regeneration is 43 insertions and no deletions.

### Acceptance — PASS

New game, cheats on, one teleport to Map 10:

```
              before          after
findShape 200  16 found,      9 found,
               7 Container    0 Container
findShape 142   8 found,      4 found,
               4 Container    0 Container
```

Nine is right: seven base-game actors plus npc 114 and npc 116, Map 10's own
stand-ins. Four is right: the ghoul actors with no twins.

The map trace now carries the line that proves the branch is taken, because
that `debug()` call sits inside the guard:

```
Loading Fixed items in map 10
Actor::teleport: 1 to 10 (13895, 18700, 8)
Unloading map 10
Loading Fixed items in map 0
Actor::teleport: 1 to 0 (15967, 19711, 0)
Unloading map 0                      <-- absent before the fix
Loading Fixed items in map 10
Actor::teleport: 1 to 10 (13895, 18700, 8)
```

`R4d-lake-pier-after-the-fix.png` in
`docs/playtest-2026-09-18-map10-walk/` is the island deck with the Avatar
alone on it. `R4c-map0-phantoms-on-the-lake.png` is the same spot before.

### Regression checks

| Check | Result |
|---|---|
| Map 18's three Zealan gods, `findShape 860` | 3 found |
| Map 17's obelisk, `findShape 861` | 1 found |
| Map 17's cloud floor, `findShape 862` | 78 found |

No artifact was rebuilt, so `ARTIFACTS.sha256` is untouched and
`tools/run_all_tests.sh` has no bearing on this change: the test estate never
runs the engine.

### What causes the map-0 hop — answered 2026-09-19

It is the Guardian's first appearance, and it is original 1994 usecode.

A full usecode trace (`UCMachine::traceAll`) puts class **1025** (0x0401,
`AVATAR`) on the instruction immediately before the switch:

```
tick 2746 running process 60, item 0, type 1, class 1025, offset 6496
Unloading map 10
Loading Fixed items in map 0
Actor::teleport: 1 to 0 (15967, 19711, 0)
```

Disassembling `AVATAR` gives the whole routine, which begins at 0x1908:

```
1913  Npc::getMap() != 3
1922  Npc::getMap() != 0
1932  global 0405 (2 bits) == 0
193A  jne -> 1A49                  ; all three must hold
1944  global 0405 = 1              ; one-shot
1951  spawn 0581:1C19 (wait 0xF0)  ; a timer class
195F  suspend
1960  save X, Y, Z and map into locals
1998  setAvatarInStasis(1)
19A4  push 4CFFh (19711), 3E5Fh (15967), 0, 0
19AF  Npc::teleport(x, y, z, map)  ; -> map 0 at (15967, 19711, 0)
19BD  spawn 0581:1C19 (wait 60); suspend
19D3  Item::create(019Bh = shape 411, frame 9)
1A08  Item::pop(x+40, y-120, z+40)
1A10  Item::use()                  ; the apparition speaks
1A1E  spawn 0581:1C19 (wait 120); suspend
1A2F  setAvatarInStasis(0)
1A42  Npc::teleport(saved x, y, z, map)   ; back exactly where he was
```

That accounts for every line of the trace, including the puzzle of the third
teleport landing on the coordinates the first one asked for: 0x1A35-0x1A42
pushes the saved locals back. Shape 411 is the apparition sprite this project
already names `SHAPE_LB_APPARITION`. The one-shot global at bit offset 0405
is why the hop happens on the first map switch of a session and never again.

Two corrections to what is written above. (15967, 19711, 0) is **not** the
Avatar's limbo record — `ITEMCACH` slot 1 is map 3 at (14527, 5887, 8) — it
is a coordinate hard-coded in this routine. And the condition is not "the
first map switch" as such: it is "the Avatar is on a map that is neither 3
nor 0, and the flag is unset". The first switch out of the starting map is
simply when that first becomes true.

**So a real player does trigger this, once, early.** The cutscene fires the
first time the Avatar leaves Tenebrae's starting map, whatever map they walk
into. Before the fix, that walk deposited all 63 limbo items on that map
permanently. The fix was live, not defensive; the earlier draft of this
document said otherwise and was wrong.

The hop itself is correct game behaviour and is left alone. Staging a
cutscene in limbo is what map 0 is for; the bug was only that limbo was
never cleaned up on the way out.

### A build trap this ran into

A bare `make` in `scummvm-lv/` produced a binary that could not identify the
game: `WARNING: Couldn't identify game 'ultima8' for the engine 'ultima'`.
The checkout's `engines/ultima/detection_tables.h` carried
`b5daa83289f403b3195fc60c1d5c43a8`/1503838 for `eusecode.flx`, while the
built one is `a9861861951900c80968b3449be55454`/1503649. The old binary had
been linked before that header went stale, so the staleness was invisible
until something forced a recompile of `detection.o`. **Rebuild with
`./build_scummvm.sh`**, which rewrites the entry from the actual FLX first.

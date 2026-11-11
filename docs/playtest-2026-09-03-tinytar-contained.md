# Playtest 2026-09-03 — Tiny Tar potions moved into Hrodny's chest (DD-005)

## Verdict

| Test | Result |
|------|--------|
| A. Hrodny's chest holds the three Tiny Tar potions in a freshly-built world | **PASS** |
| B. No duplicate Tiny Tar potions remain on the ground | **PASS** |
| C. Shape 618 loads as a Container so contained records attach | **PASS (engine source + runtime)** |

## Context

`git log` handoff and the 2026-09-02 exit test (`docs/playtest-2026-09-02-quest-chain.md`,
test Z-e) ended on one terminal blocker: the Tiny Tar potions — DD-005's only way into
the Ancient Temple — were nowhere in the world. Three frame-8 potions were placed at the
chest's ORIGINAL cell (`x0+3488..3536`), which is the hut's west wall column, the same
spot that had made the chest itself unclickable, so the exit test never saw them and the
chest was placed empty.

Decision taken: **Option 1 (containment)**. It is truest to DD-005, keeps both keys
meaningful, and Hrodny's shipped dialogue ("locked in a chest") already assumes it. The
FIXED map format supports containment natively; the map writer just had no helper for it.

## What changed

- **`agents/map-populator/src/u8_map.py`** — new `MapItem.contained_item()`. The FIXED
  format has no parent pointer: `Map::loadFixedFormatObjects` keeps a stack of open
  containers and reads a record's **x as its container depth**, popping the stack when x
  drops. So a contained item is any record with `x = depth` (1 = "inside the previous
  top-level container") placed directly after its container. y packs the gump slot
  (`0xFFFF` = unplaced, randomised on first open); z is unused.
- **`agents/map-populator/src/build_map_10.py`** — the three `SHAPE_POTION_REAL` (859)
  frame-8 potions now follow the chest record as `contained_item(depth=1)` instead of
  sitting on the floor. They carry `npcnum 229` so the engine patch dispatches TYPEPOTION.
- Artifact rehash: only `FIXED.DAT` moved.
  `ca93f4ce… → 2327ca70…`. `ARTIFACTS.sha256` re-recorded; two builds reproduce the hash.
  Estate 26/26. Detection unaffected (FIXED.DAT is not in the md5-5000 window).

## A — the chest holds three items (PASS)

Fresh world built from the new `FIXED.DAT` (a save carries its own baked map, so this was
verified on a `MainActor::teleport 10` into a newly-loaded map, never from a checkpoint).
Single-click (LOOK) on the chest with `debugflag_enable Object`:

```
Item 2636 (class Container, shape 618) (uc: LCHST_EW), 0, (21152, 8832, 0)
  q: 20, m: 0, n: 0, f: 0x2000, ef: 0x3 shapeinfo f: 2, fam: 6, et: 0);
  Container vol: 3/200, total weight: 230, items: 3
```

`class Container`, shape 618 (locked chest), at exactly the placed position (21152, 8832,
0), lock quality 20, **items: 3** — up from 0 in the 2026-09-02 build. Screenshot
`A1-chest-items3.png`.

The three contained records are shape 859 frame 8, npcnum 229 (dumped from the built
`FIXED.DAT`), each with `x=1, y=-1` — the container-depth encoding, not a world position.

## B — no ground duplicates (PASS)

Built-`FIXED.DAT` scan of map 10: exactly three shape-859 frame-8 records exist, all three
with `x=1, y=-1` (contained), **zero on the ground**. The old floor placements are gone,
so there is no double supply and nothing loose beside the chest.

## C — 618 is a Container (PASS, source + runtime)

`ItemFactory::createItem` builds a `new Container()` for family `SF_CONTAINER`
(`item_factory.cpp:50`). TYPEFLAG gives shape 618 family 6 = SF_CONTAINER, so the loader's
`dynamic_cast<Container *>(item)` succeeds, it pushes the chest onto the container stack,
and each following `x==contdepth` record is `cont.top()->addItem(item)` with
`checkwghtvol=false` (`map.cpp:230-270`). The runtime dump in test A is that path
executing: a Container carrying its three records.

## Not re-verified here (already PASS in prior sessions)

- Key (quality 20) unlocks the chest → shape 618 becomes 78, gump opens
  (`docs/playtest-2026-09-02-quest-chain.md`, Z-d).
- Tiny Tar potion stows in the pack (F11, `docs/playtest-2026-08-18-f10-climb.md`).
- Frame-8 `POTION.UNK::use()` shrinks the Avatar, re-grow kill check (DD-005).

Opening the chest for a visual potion count was not repeated this session: `Cheat::items`
grants no key, and the whole unlock→open→count chain was already a PASS on 2026-09-02.
The container item count is the new fact, and it is conclusive.

## Harness notes

- **This build's on-screen console takes keystrokes, not `commands.txt`.** `lv.sh q`
  (stdin pipe) returned "ATTACH FAILED"; driving with `xdotool type` into the attached
  console works.
- **Typing `exit` to detach leaks its `i` to the game** whenever the console has already
  closed, opening the backpack gump. Close it with `i`, not Escape — Escape opens the
  Pagan menu book.
- **Click coordinates are window-relative.** The window sits at (405,196) on the
  1450×873 Xvfb root, so a screenshot pixel maps to `(px-405, py-196)`. Passing raw
  screenshot pixels clamps every click to the same edge tile.
- **The playtest game dir is `shared/u8-lv-patched/`, which `install_lv.sh` does not
  touch** (it targets `shared/data/u8-install`). Copy the new `FIXED.DAT` into
  `shared/u8-lv-patched/STATIC/` by hand before starting a session, or the session runs
  the old map.
- A persistent green-bordered gump appeared and did not block the test; not diagnosed.

## Disk changes

- `agents/map-populator/src/u8_map.py`, `build_map_10.py` — source edits above.
- `shared/build/FIXED.DAT` (rebuilt), `shared/build/ARTIFACTS.sha256` (re-recorded),
  `shared/build/map_manifest.json`. Installed copy refreshed under
  `shared/u8-lv-patched/STATIC/FIXED.DAT` and `shared/u8-lv-patched/FIXED.DAT`.
- `~/lv-checkpoints/slot1-before-2026-09-03.sav` — backup of save slot 1 taken before the
  session (slot untouched otherwise).
- Screenshot: `docs/playtest-2026-09-03-tinytar-contained/A1-chest-items3.png`.

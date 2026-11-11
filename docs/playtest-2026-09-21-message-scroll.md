# Playtest 2026-09-21: the Message Scroll (shape 864) in Cloud City

Art track item 4 (`docs/art-track.md` contract 4), verified in ScummVM on a
fresh world built from the artifacts recorded the same day
(`FIXED.DAT 8fe8a9a0…`, `U8SHAPES.FLX c7827792…`, `TYPEFLAG.DAT d505d491…`;
`EUSECODE.FLX` unmoved at `a71868ae…`, so the engine binary is untouched).

## Verdicts

| ID | Test | Verdict |
|----|------|---------|
| A1 | The plinth carries a scroll, at 640x400 | **PASS** |
| A2 | It rests on the plinth top at z=8 on a fresh world | **PASS** |
| A3 | A click prints nothing | **PASS** |
| B1 | `findShape 864` reports the contract's identity | **PASS** |
| B2 | The Avatar can pick it up and carry it | **PASS** |
| B3 | Dropped, it lands on the floor beside the plinth | **PASS** |

## A1, the plinth carries a scroll: PASS

`A1-plinth-640x400.png`, the Scroll Chamber with the cursor parked off the
item. The plinth holds a pale parchment with two rolled ends and a band of
dark strokes, between the two candlesticks, under the wall lamp. A wooden
plank bench stood here until today. `A4-scroll-4x.png` is the same sprite at
4x: 30x22 px, the writing legible as strokes at 1x against the chamber's
dark slate floor.

`A2-avatar-beside-the-plinth-640x400.png` is the scale shot: the Avatar a
short way south of the plinth, the scroll about the width of his torso.

## A2, it rests at z=8: PASS

The item is not `SI_FIXED` any more (that is the point of donor 159), so
the question is whether it stays where the map puts it. On a fresh world,
before anything touched it:

```
] ObjectManager::findShape 864
Item 8275 (class Item, shape 864), 0, (3328, 1536, 8) q: 80, m: 0, n: 0,
  f: 0x2000, ef: 0x3 shapeinfo f: 2, fam: 1, et: 0) px=(0,-4)
findShape 864: 1 found
```

z=8, the plinth's top (donor 113, footpad z 1, placed at z=0). Nothing
fell.

## A3, a click prints nothing: PASS

`A3-click-no-bark.png`, shot 0.35 s after a single left click with the
cursor visibly on the sheet. No bark, no name, no gump. Structural
confirmation: FLX entry 866 (= class 864) is empty, so the engine's
shape-number dispatch (`item.cpp:1516`) has nothing to call. The stool
printed nothing either; making the scroll *readable* is the contract's open
question and needs text.

## B1, the engine's own description: PASS

From the A2 line: quality **80** kept (`QUALITY_MSG_SCROLL`),
`shapeinfo f: 2` = `SI_SOLID` alone, no `SI_FIXED`, and `fam: 1` =
`SF_QUALITY`. That is donor 159's entry copied whole, and it is what makes
`Item::I_getQuality` answer 80 for this item. On an `SF_GENERIC` shape
that call returns 0 whatever the quality field holds (`item.cpp:2841`).

## B2, the Avatar carries it: PASS

Walked the documented pickup: cursor on the sheet, `mousedown`, 0.9 s, then
8 px increments, released on the Avatar's sprite, with him standing south of
the plinth as `A2-avatar-beside-the-plinth-640x400.png` shows. His exact
coordinate at the moment of the grab is not in the record, for the
stale-log-line reason under harness anomalies.

```
Item 8387 (class Item, shape 864), 0, (57, 29) q: 80, ... f: 0x200c
Item 1 (class MainActor, shape 1), ... total weight: 30, items: 1
```

The coordinates are container-relative and the flags carry the in-container
bit, so it is in the pack; total weight went **20 → 30**, which is TYPEFLAG
weight 1 x 10. `B2-scroll-in-the-pack.png` shows it inside the open gump.
This is the behaviour Plot v1.2 beat 14 asks for (the Avatar shows the
scroll to Ezrekal) and the 158 stool could not give: `SI_FIXED` scenery is
unpickable.

## B3, dropped, it lands: PASS

Dragged back out of the pack onto the floor: (3448, 1360, 0), flags
`0x2004`, resting on the chamber's floor at z=0. A loose item behaves as a
loose item.

## Findings outside the plan

1. **The sprite sits on the near half of the plinth tile.**
   Its centre would be the tile's centre; its box is 64x64 on a
   128x128 tile and the anchor is bottom-centre, so the sprite's foot lands
   on the tile's near vertex instead.
   Contract 1 re-centred the obelisk for exactly this reason; the scroll
   cannot be re-centred without moving it, and its position is frozen by
   `derive_map_pins.route_cite`, which finds its pin row by grepping
   `test_route_reach.py` for the literal `3328, 1536,`. It reads acceptably
   off-centre (A4). Centring it means moving the route goal, the pin row and
   `MSG_SCROLL_POS` together, in one commit.

2. **`TYPE_SHAPES` points every paper type at the stool.** `TypeBook`,
   `TypeScroll`, `TypeMagicScroll` and `TypeGrimoire` all resolve to 158,
   while the engine's scroll is 159 (class 0x9F `BASESCRL`) and its book is
   288. `FREE.UNK:1338`'s debug grant therefore creates a bench and calls it
   a scroll. Not fixed here: the blast radius is `EUSECODE.FLX`, a rehash and
   a ScummVM rebuild, and it has nothing to do with this item's art. Recorded
   in contract 4.

## Harness anomalies

- **`Cheat::toggle` sent within a second of `session.sh start` does not
  land**, and the only symptom is `Cheats are disabled` on the next
  teleport. Send it, read the log for `Cheats = true`, then teleport.
- **A query's reply must be read as new log lines, or it is the previous
  query's.** Two `MainActor::teleport` calls looked like they had failed,
  and one `objectInfo` reported a position the Avatar had already left, all
  because `tail | grep` found the last matching line, which was the
  previous query's. That is why B2 carries no coordinate. Count the log's lines before
  the command and read only what is new (`tail -n +$((N+1))`).
- **The backpack gump reopens after a teleport**, not only after a fresh
  start. Double-click its own frame before every plate.

## Disk changes

- `docs/playtest-2026-09-21-message-scroll/`, five plates.
- `shared/u8-lv-patched/`, the four artifacts re-synced from
  `shared/build/` before the session (`session.sh start` also does this).
- No savegame was written; the session was stopped.

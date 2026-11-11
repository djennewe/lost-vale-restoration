# Playtest 2026-09-21: reading the Message Scroll (class 864)

The second session of the day. The scroll's art landed this morning
(`docs/playtest-2026-09-21-message-scroll.md`); this is the usecode class
behind it, compiled at 864 so the engine's shape dispatch finds it
(`item.cpp:1516`). Artifacts: `EUSECODE.FLX 40ec62f4…` (moved),
`TYPEFLAG d505d491…`, `U8SHAPES c7827792…`, `FIXED 8fe8a9a0…` (unmoved).
ScummVM rebuilt, since `LV_SIZE` in `build_scummvm.sh` had to follow.

**Detection was exercised through the harness, and `install_lv.sh --run`
was not run.** `scummvm-lv/scummvm` is built from the regenerated
`detection_tables.h` and it loaded the expansion's map 17 with the new
class bound, which is the thing a stale entry would break; the installer
path stays unexercised.

## Verdicts

| ID | Test | Verdict |
|----|------|---------|
| A1 | The engine binds class 864 to shape 864 | **PASS** |
| A2 | The scroll can be picked up and carried | **PASS** |
| B1 | Double-clicking it opens the scroll gump with Odion's letter | **PASS** |
| B2 | The text pages through to its end | **PASS** |
| C1 | `look()` barks "message scroll" on a single click | **NOT DEMONSTRATED** |

## A1, the engine binds the class: PASS

`ObjectManager::findShape 864` now prints a usecode name beside the item
that was not there this morning:

```
Item 8275 (class Item, shape 864) (uc: TYPEMESS), 0, (3328, 1536, 8) q: 80,
  ... shapeinfo f: 2, fam: 1
```

`TYPEMESS` is the FLX name-table entry for TYPEMESSAGESCROLL, pinned to
0x0360 in `lv_manifest.json`. The engine read class 864 off the shape
number by itself.

## A2, carried: PASS

Dragged off the plinth onto the Avatar with the documented pickup recipe.
`A1-plinth-after-the-pickup.png` shows the plinth bare;
`A2-scroll-in-the-pack.png` shows the sheet inside the open pack gump.

## B1 and B2, the letter reads: PASS

Double-clicked in the pack. `ScrollGump` opens over the world with the
game's own scroll art and font, three pages long, paging on a click:

- `B1-page1.png`: the address and the first two paragraphs.
- `B2-page2.png`: the rest of the letter.
- `B3-page3-signature.png`: "Odion" alone.

The bytecode is retail `SCROLL2`'s shape: push the string, push this,
`calli 0x6F` (`Scroll::read`). That slot is what the `uses "scroll"`
line in `MSGSCRL.UNK` buys; drop the line and the same source compiles
to `Book::read` (0x6E) and the two-page book gump.
`test_uses_imports.py` now pins all four reader slots.

## C1, the look bark: NOT DEMONSTRATED

A single click on the scroll printed nothing on screen, and so did a
single click on the Avatar, which is the control: this harness is not
delivering the look bark for any item today. The 2026-09-15 trap note
("clicks did not log") is the same failure. The bark is in the compiled
class (`calli 0x49`, `Item::bark("message scroll")`, asserted by the
estate). The click path is what went untested here.

The control was a click on the Avatar, which assumes MainActor barks on a
look; a candlestick or a column would have separated "the harness eats
look feedback" from "look() never fired". One consequence for this
morning's report: its A3 ("a click prints nothing") now rests entirely on
the structural fact it already cites, FLX entry 866 being empty, because
the click path is shown to print nothing for anything.

## Findings outside the plan

1. **The signature sits alone on page 3.** Page 2 ends on "...for that
   door." with room below it, and the paragraph break plus "Odion" tips
   into a third page. **Douglas kept it on 2026-09-21**, so the third
   page is the shipped look and the note in `MSGSCRL.UNK`'s header says
   so; the alternative was a one-character change (`~~Odion` to
   `~Odion`).
2. **`PLAQUENS.UNK` was compiling its plaque text as a grave.** Making
   `uses` select the reader intrinsic changed one other shipping class:
   TYPENSGOLDPLAQUE (0x4EB) moved from 70 calls to `Grave::read` (0x70)
   to `Plaque::read` (0x71). Both open a `ReadableGump`; the difference
   is the line count the gump is built with (11 against 10,
   `readable_gump.cpp:97`). Nothing places a gold plaque on an LV map
   yet, so this shows up the day art track item 6 lands.
3. **`startSelection` opens the backpack.** The debugger's
   `ItemSelectionProcess::startSelection` was tried as a way around the
   dead click path and it selects the Avatar's own pack, which reopens
   the gump over the view. Not useful for reaching a world item.

## Harness anomalies

- **Clicks deliver `use` but not `look` feedback.** Double-clicks work
  (the pickup, the gump, the pack), and single clicks produce nothing
  visible for any item. Unchanged from 2026-09-15.
- **A double-click at the pack gump's frame toggles it**, so a "close the
  pack" reflex can reopen it. Verify with a pixel sample before assuming
  the view is clear.
- **`MainActor::teleport` repeated within one map sometimes does not
  land**, and the stale-log-line trap hides it. `walkto.py --walk` is the
  reliable short move.

## Disk changes

- `docs/playtest-2026-09-21-scroll-class/`, five plates.
- The session's world had the scroll in the Avatar's pack when it was
  stopped. No savegame was written.

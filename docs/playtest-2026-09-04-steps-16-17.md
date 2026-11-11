# Playtest 2026-09-04 — steps 16-17: the Tiny Tar route into the Inner Sanctum

## Verdicts

| # | Test | Result |
|---|------|--------|
| A1 | Pre-placed q20 key found and stowed | **PASS** |
| A2 | Key unlocks Hrodny's chest (618 → 78) | **PASS** |
| A3 | Chest opens; three Tiny Tar potions inside | **PASS** |
| A4 | A potion transfers from chest to backpack | **PASS** |
| A5 | Chest count decrements when the potion is taken | **PASS (after the fix below)** |
| A6 | Carrying the potion across a map change | **PASS (after the fix below)** |
| B1 | Full-size Avatar is BLOCKED at the crack (negative control) | **PASS** |
| B2 | Drinking frame 8 dispatches TYPEPOTION and shrinks the Avatar | **PASS** |
| B3 | Shrunken Avatar passes THROUGH the crack | **PASS** |
| B4 | Re-grow inside the sanctum does not kill him | **PASS** |
| C  | Shield on altar → gods → Bag of Reagents (rest of 17, and 18) | **NOT DEMONSTRATED** |

Everything ran on a world built fresh from the new `FIXED.DAT`, never from a
checkpoint (a save carries its own baked map).

## The defect this run found, and the fix

Taking the first potion out of the chest put it in **two containers at once**,
and the next map change then freed it under the backpack: **ScummVM segfaulted**
leaving map 10 while carrying a Tiny Tar.

Cause, in engine source. `Item::moveToContainer` unlinks an item from its old
container only inside

```cpp
if (_flags & (FLG_CONTAINED | FLG_EQUIPPED)) { ... p->removeItem(this); }
```

but the loader attaches contained records with `Container::addItem()`, which
pushes onto `_contents` and **never sets `FLG_CONTAINED`**. Items loaded
contained from `FIXED.DAT` therefore came up without that flag (dumped as
`f: 0x2000`, i.e. fast-area only), so moving one added it to the backpack while
leaving it listed in the chest. The chest kept reporting `items: 3` after a take
while its gump drew 2 — the visible symptom.

Fix is data-side, no engine change: `MapItem.contained_item()` now writes
`flags = FLG_CONTAINED (0x0008)` into the record. `ItemFactory::createItem`
copies record flags straight onto the item, so the item is correctly flagged
from the moment of load. Retail never exercised this path — retail `FIXED.DAT`
has **zero** contained records — which is why it went unnoticed.

After the fix, the same take reads `Container vol: 2/200, total weight: 220,
items: 2`, and the map change that crashed now completes with the potion intact
(`f: 0xc` = CONTAINED|OWNED).

`FIXED.DAT` rehashed `2327ca70… → 278a48c3…`; only that artifact moved.

## A — obtaining the Tiny Tar (PASS)

The pre-placed quality-20 key means this whole leg needs no quest flags.

- **A1.** `Item 2952 (shape 82) (uc: KEY), (22016, 6144, 0) q: 20` dragged onto
  the Avatar: `Dragging item 2952` → `Dropped item in backpack`, weight 20 → 30.
- **A2.** Double-click key → click chest gives
  `Target result: Item 3020 (class Container, shape 618) (uc: LCHST_EW)`, and
  the chest then reads **shape 78 (CHEST_EW)** — unlocked. The lock ids work.
- **A3.** Double-click opens the gump: three potions inside
  (`A1-chest-open-potions.png`).
- **A4/A5.** One dragged onto the Avatar's sprite: weight 30 → 40, chest drops
  to `items: 2`.
- **A6.** Teleport map 10 → 18 with the potion carried: no crash, potion intact.

Release must land on the **Avatar's sprite**; dropping into the open pack
interior is refused silently (`Dropping object N` with no
`Dropped item in backpack`), exactly as `traps.md` says.

## B — the crack (PASS, with its negative control)

- **B1 (negative control).** Full-size Avatar at **(2848, 6100, 0)**, four
  sustained south pushes (1.2 s at mag 230): final position **(2848, 6100, 0)** —
  **zero displacement**. `build_sanctum_gate_hardening()` holds.
- **B2.** Drinking frame 8 logs
  `Item: 2955 (shape 859) calling usecode event 1 @ 04E5:00A9` — class 0x04E5 =
  1253 TYPEPOTION, dispatched through npcnum 229 by the engine patch. The Avatar
  becomes **`shape 708 (uc: CHILD)`** (`B1-shrunken-inside-sanctum.png`).
- **B3.** Three south pushes from the same spot that refused him at full size
  carried him to **(2804, 6664, 0)** — past the crack at y 6143 and into the
  Inner Sanctum. Same position, same input, opposite outcome: the shrink is what
  changed.
- **B4.** After the timer, `makeAvatarBig()` returned him to **shape 1** at the
  same position, **alive, hp 31** (`B2-regrown-alive.png`). The sanctum floor
  has room for the re-grow, so the lethal branch does not fire on arrival.

DD-005 is therefore demonstrated end to end for the first time: the crack is
impassable at full size, the potion is the only thing that changes that, and the
potion is now obtainable where the design says it is.

## C — the rest of 17, and 18 (NOT DEMONSTRATED)

Placing the Shield on the altar, the gods, and the Bag of Reagents were not
attempted. They need the **restored Zealan shield**, which only exists after the
Sacred Circle ceremony (step 15); this run started from a fresh world to get the
new map, so no quest state existed. Those scenes last executed in-engine on
2026-07-31. Closing them properly is the one-continuous-playthrough tier, not a
fresh-world spot check.

## Harness notes

- **The console takes keystrokes, not `commands.txt`**, and it is a TOGGLE with
  no readable state. A command typed while it is closed goes to the GAME: `i`
  opens the pack, `m` toggles the minimap (the mystery green box in the
  2026-09-03 shots), Escape opens the Pagan menu book. Typing `exit` leaks its
  own `i` for exactly this reason. `scratchpad/drv.py` verifies every command by
  waiting for a marker in the log and re-chords only on a miss.
- **Clicks are window-relative.** The window sits at (405,196) on the 1450×873
  root; screenshot pixel → window pixel is `(px-405, py-196)`. Passing raw
  screenshot pixels clamps every click to the same edge tile and looks exactly
  like "the item is not clickable".
- **`CameraProcess::moveToAvatar` is required before projecting** any world
  position to a pixel; the camera silently stops tracking after teleports.
- **`Cheat::items` grants no key** (money, skull, recall, weapons, bags,
  reagents only), so the chest needs the real q20 key.
- The playtest game dir `shared/u8-lv-patched/` is still synced by nothing —
  `install_lv.sh` targets `shared/data/u8-install`. Copy `FIXED.DAT` in by hand.

## Disk changes

- `agents/map-populator/src/u8_map.py` — `contained_item()` now sets
  `FLG_CONTAINED`; new `MapItem.FLG_CONTAINED` constant.
- `shared/build/FIXED.DAT` rebuilt (`278a48c3…`), `ARTIFACTS.sha256` re-recorded,
  installed copies refreshed under `shared/u8-lv-patched/`.
- Screenshots in `docs/playtest-2026-09-04-steps-16-17/`.
- Save slots untouched. `~/lv-checkpoints/slot1-before-2026-09-03.sav` still holds
  the pre-session slot-1 backup.

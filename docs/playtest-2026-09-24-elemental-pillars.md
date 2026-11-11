# The elemental pillars in the engine (2026-09-24)

Art track item 5 landed: shape 865 (four pillars, custom art, class 865
behind it) and shape 866 (the receptacles) on Map 11, with
`TypeElementalColumn` re-pointed 721 → 865 in `COLPUZZL`'s compiled search.
This session is the contract's in-engine verification: the shapes draw, the
engine binds the class to the shape, the receptacle still dispatches off its
npcnum on the new shape, and one pillar was destroyed through the
re-pointed `areaSearch` with a real talisman.

Fresh world each start (`tools/playtest-linux/session.sh start`,
`scummvm-lv/scummvm` rebuilt 2026-09-24 07:30 with the current detection
entry), `Cheat::toggle`, `debugflag_enable Object`, travel by
`MainActor::teleport`. The quest actions themselves (the pickup, the
receptacle activations) are player input. Plates are in
`docs/playtest-2026-09-24-elemental-pillars/`, cropped to nothing: the
1450×873 Xvfb screen with the 640×400 game window at (565, 336).

## Verdicts

| ID | Test | Verdict |
|---|---|---|
| A1 | `findShape 865` lists four pillars, frames 0-3, q201-204, `(uc: TYPEELEM)` | **PASS** |
| A2 | `findShape 866` lists four receptacles carrying `n: 120`, no class of their own | **PASS** |
| B1 | The four pillars and four receptacles draw in the chamber | **PASS** |
| C1 | Double-click a receptacle empty-handed: `use()` runs in class 1144 and barks the repel line | **PASS** |
| C2 | Double-click the Earth receptacle with the Air talisman: talisman consumed, bark, Earth pillar destroyed | **PASS** |
| D1 | Single-click a pillar barks its element (class 865 `look()`) | **NOT DEMONSTRATED** |

## A1, A2: the engine's own binding, PASS

`ObjectManager::findShape 865`:

    Item 14385 (class Item, shape 865) (uc: TYPEELEM), 0, (7680, 20480, 0) q: 201 ... shapeinfo f: 3
    Item 14396 (class Item, shape 865) (uc: TYPEELEM), 1, (8704, 20480, 0) q: 202 ...
    Item 14407 (class Item, shape 865) (uc: TYPEELEM), 2, (7680, 21504, 0) q: 203 ...
    Item 14418 (class Item, shape 865) (uc: TYPEELEM), 3, (8704, 21504, 0) q: 204 ...
    findShape 865: 4 found

`(uc: TYPEELEM)` is the engine naming the usecode class it resolves for the
shape, the same tell that proved class 864 on 2026-09-21. Frame equals
element equals quality minus 201, at the chimney's four coordinates.
`shapeinfo f: 3` is `SI_FIXED | SI_SOLID`, donor 38's flags.

`ObjectManager::findShape 866` lists the four receptacles at the pillars'
x and 256 south, `n: 120`, `fam: 0`, and no `(uc: …)`: the shape number
carries no class, as the contract says, and the dispatch is the npcnum.

**A trap on the way** (finding 1): the first `findShape 865`, sent right
after the teleport, printed `0 found`, because Map 11's fixed items were
still loading (`Loading Fixed items in map 11` landed in the log after it).
The receptacles were already there. Wait for the load line before
counting.

## B1: the art in the chamber, PASS

`B1-north-pair-earth-air.png`, `B1-south-pair-fire-water.png`,
`B1-earth-pillar-and-receptacle.png`: the rock spire (Earth), the twister
(Air), the flame (Fire) and the water column (Water), each on its plinth on
its paved square, a stone socket beside each. They sort correctly against
the Avatar (the Earth pillar draws in front of him when he stands behind
it) and read as four different things from across the room. The 2×2 grid is
1024 units on a side, so no single 640×400 view holds all four; the two
pair plates together do. Measured on `B1-north-pair-earth-air.png`, where
the window renders 640×400 at 1:1: the Earth column spans 93 screen rows
from spire tip to plinth foot (rows 397 to 489), the 95-row frame minus
its clear rows, so the contract's 96 px is the height the player sees.

## C1: `use()` still dispatches on the new receptacle shape, PASS

With `UCMachine::traceClass 1144` armed, a double-click on the Earth
receptacle from beside it logged

    tick 20066 running process 1020, item 14386, type 1, class 1144, offset 128

item 14386 being the q201 receptacle, type 1 the `use` event, class 1144
`TYPERECEPTACLE`. The Avatar carried nothing, so the class took its
"no talisman" branch and barked **"The column flares with energy and
repels you!"** (`C1-repel-bark.png`). That is the contract's central
claim shown live: the npcnum override reaches class 1144 whatever the
shape is.

**Negative control** (finding 5): the same double-clicks from 181 units
away (the Avatar at (7808, 20608), the receptacle at (7680, 20736))
dispatched nothing and logged nothing three times running. The engine's
double-click needs the item within reach; from 64 units it worked first
time.

## C2: the re-pointed search destroys a shape-865 pillar, PASS

This was a diagnostic run in the sense of the 2026-09-06 step 4 report: a
fresh game cheat-teleported straight to Map 11, the quest globals from
steps 1-3 never set, the talisman taken by drag and by the debugger. It
proves the receptacle finds and destroys the new shape; it says nothing
about a continuous run from step 1.

The Air talisman (shape 596 frame 1, q102, the opposite of Earth) was
picked up at (17152, 5120, 0) by the drag recipe in
`.claude/skills/playtest/traps.md`: `total weight` 20 → 30, and
`findShape 596` then lists item 13096 at container slot (32, 18) with
`f: 0xc` (`C2-talisman-lifting.png`, `C2-talisman-taken.png`). Back
beside the Earth receptacle, pack closed (`C2-before-activation.png`), a
double-click on the socket's top face logged

    tick 43064 running process 934, item 14386, type 1, class 1144, offset 128
    tick 43064 (still) running process 934, item 14386, type 1, class 1144, offset 536
    tick 43342 running process 934, item 14386, type 1, class 1144, offset 551

and then, in order: `findShape 596: 3 found` (the Air talisman consumed),
the bark **"The air talisman howls with fury!"** (`C2-air-talisman-howls.png`),
and

    findShape 865: 3 found

with q202, q203 and q204 listed and **q201 gone**. `COLPUZZL`'s `foreach
pillar where type = TypeElementalColumn within 300 of referent`, compiled
with 865 since this morning's re-point, found the shape-865 pillar through
the real `CurrentMap::areaSearch` and destroyed it. `test_uc_sim` proved
the bytecode against a mock world; this is the engine.

## D1: the look bark, NOT DEMONSTRATED

Class 865's `look()` is compiled and the engine binds it (A1), and it was
not observed, for the reason the 2026-09-21 scroll session recorded:
single clicks deliver no `look` feedback through this harness for any
item. Not retried. The structural fact stands in, and the barks' text is
asserted by the estate.

## Findings outside the plan

1. **`findShape` right after a teleport counts the previous map.** The
   fixed items of the destination load a beat later; a `0 found` on a
   shape you know is placed means "not loaded yet", and the log's
   `Loading Fixed items in map N` line is the thing to wait for.
2. **The two sheets' plinths disagree.** Earth and Air (from sheet C2)
   stand on violet plinths; Fire and Water (from C3) on the ring stone's
   blue-grey. Visible in the pair plates. The pillars were chosen by
   element, so the family reads across the four columns and breaks at the
   plinth. A fix is one of: re-quantize the C2 plinths toward the C3
   palette, paste C3's plinth under the C2 columns before `build_frame`,
   or accept it. Left as is that day; **fixed 2026-09-25** by the second
   route (`tools/art/pillar_plinth.py`,
   `docs/playtest-2026-09-25-pillar-plinths.md`).
3. **`Item::grab <objid>` exists.** The fork's debugger can put an item in
   the Avatar's pack without a pointer (`debugger.cpp`, "the same
   destination a drag onto the Avatar reaches"). Three drag attempts
   failed here before the fourth took (finding 4); the command would have
   replaced all of them. `traps.md` should name it beside the drag recipe.
4. **A drop that lands as a click on the Avatar does two things.** When
   the drag has not lifted the item, releasing on the Avatar is a click on
   him: once it opened the backpack gump over the view, and once it opened
   the LV debug menu ("Blow up!", "EndGame", "Done"), which is
   `AVATAR.UNK`'s `use()`. Both had to be dismissed before the next
   attempt. The drag lifted only when the pack was closed first and the
   Avatar stood within reach; from 256 units it drew the red-X refusal
   cursor (`F4-drag-refused-red-x.png`).
5. **Receptacle reach.** See C1: double-clicks from 181 units away dispatch
   nothing. The 2026-09-06 run stood beside each one and never saw this.

## Harness anomalies

- Clicks do not log `dumpInfo()` (the 2026-09-15 trap holds); the usecode
  trace (`UCMachine::traceClass 1144`) is what showed a click had landed.
- `dbg.sh` replies land out of order: an `objectInfo` reply appeared in the
  log after the following `findShape`'s lines. Read the log by content,
  never by "the last line is the latest command".
- **No plate of the emptied plinth.** The session was stopped after the
  counts were read and before a last plate; the destroy is evidenced by
  `findShape 865: 3 found` with q201 absent and by the consumed talisman.
  A rerun would take the plate at +8 s or later; at +5.5 s the bark was up
  and the pillar still drawn.

## Disk changes

- `shared/data/u8-install/STATIC/` and `USECODE/`: the four artifacts of
  this morning's build, installed by `install_lv.sh`; `session.sh start`
  then logged `synced USECODE/EUSECODE.FLX <- shared/build/EUSECODE.FLX`.
  No savegame written.
- Nothing else. The scratchpad crops were temporary.

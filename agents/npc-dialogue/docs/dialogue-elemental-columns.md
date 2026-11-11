# Elemental Columns — Pillar Puzzle Dialogue

Missing dialogue segment #3. Writer: Brian M. (never completed).
The four elemental pillar destruction sequences at the exit of the
Elemental Dungeon.

---

## Context

At the end of the Elemental Dungeon, four elemental pillars block the
path to the Lost Vale (Plot beat 6). Each pillar must be destroyed by
applying its opposite element:

| Pillar | Destroyed By | Flag |
|--------|-------------|------|
| Water Pillar | Fire talisman | `WaterColumnDestroyed` |
| Fire Pillar | Water talisman | `FireColumnDestroyed` |
| Earth Pillar | Air talisman | `EarthColumnDestroyed` |
| Air Pillar | Earth talisman | `AirColumnDestroyed` |

When all four are destroyed: `allColumnsDestroyed = true`.

---

## Class Definition

```
typeclass TypeElementalColumn inherits Item
```

Each pillar is a separate instance distinguished by frame number
(UPDATED 2026-07-04 to match the shipped FIXED.DAT placements — the map's
mapping won by decision; build_map_11.py is the source of truth, with
receptacle quality 201-204 and talisman quality 101-104 in the same order):
- Frame 0: Earth Column
- Frame 1: Air Column
- Frame 2: Fire Column
- Frame 3: Water Column

---

## Pillar Look Barks

REMAPPED 2026-09-22 to the frame order the Class Definition above has carried
since 2026-07-04. This block still listed the pre-remap order (frame 0 water,
1 flame, 2 stone, 3 wind) for two and a half months, so anyone who wired the
barks off it would have named every pillar wrong. The element is what the
bark must follow; the frame is only where the map put it.

```
Frame 0 (Earth): "column of solid stone"
Frame 1 (Air):   "column of swirling wind"
Frame 2 (Fire):  "column of roaring flame"
Frame 3 (Water): "column of shimmering water"
```

If destroyed:
```
"shattered remains of a column"
```

That last bark is unreachable as the puzzle is built: `COLPUZZL.UNK:139-141`
calls `destroy()` on the pillar, so no item survives to be looked at. It
would need the pillar reframed to a rubble frame, leaving the item alive.
That is a design decision for whoever wants the bark.

These barks are compiled: `lv-new/ELMCOLMN.UNK` (class 865, pinned
`TYPEELEMENTALCOLUMN`, 2026-09-24) carries them in `look()` by frame. It is
dead until custom shape 865 is injected and placed; the pillars are shape
721 today, whose class is the base game's `CHIMNEY`, so a click still says
"chimney". `docs/art-track.md` contract 5 has the rest.

---

## Interaction — Wrong Element

When the Avatar uses the wrong talisman on a column, or uses an item that
is not a talisman:

```
"The column flares with energy and repels you!"
```

The Avatar takes 5 damage and is pushed back.

---

## Interaction — Correct Element

### Water Column + Fire Talisman

**Avatar bark:**
```
"The fire talisman blazes in my hand!"
```

*The talisman ignites. The water column hisses and evaporates
in a burst of steam. Screen flash. SFX: steam burst.*

**Environmental bark:**
```
"The water column has been destroyed."
```

Sets `WaterColumnDestroyed = true`.

### Fire Column + Water Talisman

**Avatar bark:**
```
"The water talisman glows with a cold light!"
```

*Water surges from the talisman. The fire column sputters and
dies with a roar. Screen flash. SFX: extinguishing flame.*

**Environmental bark:**
```
"The fire column has been destroyed."
```

Sets `FireColumnDestroyed = true`.

### Earth Column + Air Talisman

**Avatar bark:**
```
"The air talisman howls with fury!"
```

*A violent wind erupts from the talisman. The earth column cracks
and crumbles into dust. Screen shake. SFX: stone shattering.*

**Environmental bark:**
```
"The earth column has been destroyed."
```

Sets `EarthColumnDestroyed = true`.

### Air Column + Earth Talisman

**Avatar bark:**
```
"The earth talisman grows heavy with power!"
```

*The talisman's weight seems to anchor the very air. The wind
column collapses inward and disperses. SFX: wind dying.*

**Environmental bark:**
```
"The air column has been destroyed."
```

Sets `AirColumnDestroyed = true`.

---

## All Columns Destroyed

When the fourth column falls:

*The ground trembles. A passage opens in the wall beyond where
the columns stood. Light — natural light — streams through.*

**Environmental bark:**
```
"The way to the Lost Vale is open!"
```

Sets `allColumnsDestroyed = true`.

---

## Galjeron's Journal Hint

Before the columns, the Avatar should have read Galjeron's journal.
Relevant passage for the column puzzle:

```
"The way is barred by pillars of elemental force. Fire opposes
water, earth opposes air — the ancient principle of balance.
Each pillar can only be overcome by its natural contrary. I have
gathered the tokens needed, but dare not face the pillars alone.
If you read this, know that the key lies in opposition."
```

---

## Environmental Barks — Dungeon Ambient

Random barks as the Avatar explores the Elemental Dungeon:

### Earth Section
```
"The walls are carved from living rock."
"The ground here feels unstable."
"I can hear something moving deep underground."
```

### Air Section
```
"The wind here is relentless!"
"I can barely keep my footing in this gale."
"The air itself seems to be alive."
```

### Fire Section
```
"The heat in here is unbearable!"
"Pools of magma block the path."
"I need to find a way around these flames."
```

### Water Section
```
"The floor is ankle-deep in water."
"I can hear rushing water somewhere ahead."
"This place smells of the sea."
```

---

## Design Notes

1. **Elemental opposition** (fire↔water, earth↔air) is the core mechanic.
   This matches the Plot v1.2 description and the Art List entries for
   "Pillars of Fire, Earth, Water, Air."

2. **Talismans are consumed** when used on their matching pillar. This prevents
   re-use and emphasizes that each talisman has one purpose.

3. **Wrong-element damage** (5 HP) punishes trial-and-error without being
   lethal. Players who read Galjeron's journal will know the correct pairings.

4. **Avatar barks** are in standard English (Avatar is not Zealan). They're
   short, action-oriented, and describe what the player sees happening.

5. **The opening sequence** when all columns fall is the dramatic transition
   from the dungeon to the Vale — natural light streaming in signals the
   shift from hostile dungeon to open world.

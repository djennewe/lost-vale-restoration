# Map 8 Modification — Plateau Double Doors Entry

Design for modifying Map 8 (Plateau) to enable the Lost Vale entry through
Bonecrusher's Cave.

## Background

The double doors in Bonecrusher's Cave already exist in the base game as visual
elements but are non-functional — the player cannot open or interact with them.
The Lost Vale expansion makes these doors the gateway to the new content.

**Story context:** Beat 3 — Mythran tells the Avatar about Galjeron and the double
doors. The Avatar must find the key and enter.

## Current Map 8 State

- **Total items:** 4,306 (1,414 glob eggs, 2,892 placed items)
- **Unique shapes:** 152
- **Bounding box:** X=[1023, 32735] Y=[1055, 31775] Z=[-128, 120]
- **Existing teleports:** 15 eggs (connects to Map 7 and internal transitions)
- **Existing containers:** 3 (shapes 205, 208, 307)

### Bonecrusher's Cave Area

The cave area in the Plateau corresponds to a building/cave cluster at
coordinates approximately (1000–4000, 1000–2500). This area contains:

- Building structure shapes (145–165, walls and pillars)
- Roof shapes (220, 335, 441, 451)
- Stacked wall columns (shape 721 at multiple z levels)
- Containers (shapes 205, 208, 307)
- Teleport eggs for transitions within the Plateau

**OPEN ITEM:** The exact pixel coordinates of the double doors within the
cave area need to be identified by:
1. Running the game in ScummVM and navigating to Bonecrusher's Cave
2. Using ScummVM's debugger to query item positions near the doors
3. Or inspecting the shape graphics for door-like decorative shapes

The doors are likely generic solid shapes (not SF_QUALITY) placed as
decorative wall elements in the cave interior.

## Modification Plan

### Items to Add

| Item | Shape | Frame | Position | Quality | Notes |
|------|-------|-------|----------|---------|-------|
| LV Door (functional) | 114 or 69 | 0 | Near double doors | Lock ID | SF_QUALITY door replacing decorative doors |
| Key to Double Doors | TypeKey shape | 0 | Puzzle location TBD | Lock ID | Matching quality for door lock |
| Teleport TRIGGER | 508 | 1 | Behind doors | 200 | Triggers transition to Map 9 |
| Teleport DEST | 508 | 0 | Cave entry area | 200+ | Return destination from Map 9 |

### Implementation Steps

1. **Locate the double doors** — Identify the existing decorative door shapes in
   the cave area. Note their coordinates and z-level.

2. **Replace or augment doors** — Either:
   - Replace the decorative shapes with a functional SF_QUALITY door (shape 114
     for a large gate, or shapes 68/69 for standard doors)
   - Keep the decorative shapes and add a trigger egg in front of them

3. **Add teleport eggs** — Place a TRIGGER egg (shape 508, frame=1, quality=200)
   at the door location. Place a corresponding DEST egg (shape 508, frame=0) for
   the return trip from Map 9.

4. **Add key mechanism** — The key's `quality` value must match the door's
   `quality` value. The engine checks this when the player tries to open the door.

5. **Place the key** — Plot v1.2 says "Mythran tells the Avatar where the key is.
   The Avatar must solve a puzzle to get the key." The key location is a design
   decision — it could be:
   - Hidden in the cave itself (requiring a puzzle)
   - Obtained from Mythran directly
   - Found in a nearby chest (requires solving a lock puzzle)

### Teleport Egg Placement

**Trigger (Map 8 side):**
```
shape=508, frame=1, quality=200
position: immediately behind the double doors
```
When the Avatar walks past the opened doors, this egg triggers the transition.

**Destination (Map 8 side, for returns):**
```
shape=508, frame=0, quality=(200 | 0x100)=456, npcnum=<return_id>, mapnum=8
position: just outside the double doors
```
This is where the Avatar appears when returning from Map 9.

### Optional: Return Path from Lost Vale

Per Synopsis Note 3, a permanent return path should exist. Options:

**Option A:** Reuse the double doors — walking through from Map 9 side
transitions back to Map 8. Simple and intuitive.

**Option B:** Add a separate teleporter in the Lost Vale overworld (Map 10)
that goes directly to Map 8, bypassing Map 9 and the dungeon. More convenient
for the player after first traversal.

**Recommendation:** Both. The double doors serve as the initial entry/return
path. After reaching the Lost Vale, a permanent teleporter (IDs 212/213) allows
quick travel between Map 10 and Map 8.

## Items to Modify (Existing)

No existing items need to be removed or modified. All changes are additive:
- 1 door item (SF_QUALITY)
- 1 key item (if placed on this map)
- 2 teleport eggs
- Total additions: ~4 items

## Testing Plan

1. Navigate to Bonecrusher's Cave in ScummVM
2. Verify the door is interactable and requires the key
3. Obtain the key (from wherever it's placed)
4. Open the door and verify transition to Map 9
5. Return from Map 9 and verify arrival at the correct position
6. Save/load game and verify the door state persists

## Dependencies

- Map 9 must exist with a corresponding DEST egg for the initial transition
- Key placement design decision (currently unresolved — depends on Mythran's
  dialogue, which is MISSING from the usecode snapshot)

## Risks

- **Door identification:** The exact double door shapes and positions are
  unknown without in-game inspection. This is the primary blocker for
  implementation.
- **Key puzzle design:** Mythran's dialogue (which would describe where the
  key is) was never completed. The key puzzle needs to be designed from scratch.

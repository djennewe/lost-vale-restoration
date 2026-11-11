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

### Bonecrusher's Cave Area — THE SEALED DOORS (solved 2026-07-02)

The famous "doors that cannot be opened" are **dynamic items seeded from
`SAVEGAME/U8SAVE.000`** (named-section container; its NONFIXED.DAT parses
with `u8_map.MapArchive`) — they exist in no static file, which is why
FIXED.DAT/GLOB.FLX scans never find them:

```text
shape 342 ("TDOOR_EW") frame 0, quality 0x663, at (20351, 3071, 0)  west leaf
shape 342 ("TDOOR_EW") frame 1, quality 0x463, at (20479, 3071, 0)  east leaf
```

Door-quality encoding (decoded from retail keyring usecode, class 0x4F —
@0119 is a code offset *inside* that class, not an FLX entry; corrected
2026-07-31): low byte = lock ID (0x63 = 99), bit 0x400 = LOCKED, bit
0x100 = open. Retail ships **no quality-99 key** — that is the entire
seal. The shipped keyring code whitelists door shapes 68/69/340/342,
ready for the expansion that never came.

The restoration adds only 7 items (see build_map_08.py): key shape 82
q=99 + chest 78 in the bone field, teleport trigger 200 → Map 9 behind
the doors, dests 201/212, direct-travel trigger 213 (+1 paving slab).
Doors opened in-game 2026-07-02 — first time since 1994 — and
re-verified end to end 2026-07-31.

## HOW TO OPEN THE DOORS (the most load-bearing undocumented fact in the
project until 2026-07-31 — a missing record here turned a wandering
ghost into a five-hour "blocking regression")

1. Get the key into the pack: open the chest beside the bone field,
   drag the key out and release it **on the Avatar's sprite** (weight
   +10 confirms).
2. **Double-click the KEY in the inventory.** A target cursor rises.
3. Click the door leaf. The lock matches quality low-byte 99 and the
   leaf unlocks; repeat for the other leaf if needed.
4. Double-click the (now unlocked) door to swing it open, walk through;
   trigger 201 behind the doors delivers you to Map 9.

What does NOT work, and what it looks like: double-clicking or
single-clicking a **locked** door barks `Locked Door` — but barks are
transient and render at the very top edge of the viewport for an item
this tall, so it is easy to conclude "the door answers nothing".
(`Mouse::getMouseFrame()` computes the cursor from pointer direction
alone, never from the item under it, so "the cursor stayed a walk
arrow" proves nothing either — 2026-07-31 investigation.)

**Known intermittent hazard, retail-correct behavior:** a wandering
base-game GHOST (shape 411, `SI_SOLID`, 96x96x48) can park in the
doorway. The door's open path (`FREE::2411` → `Item::legal_create`)
refuses while any solid overlaps the open box and the partner leaf
barks `blocked`. Kill the ghost or wait for it to drift off. It is a
runtime spawn — no shape-411 record exists in map 8's NONFIXED — so it
cannot be engineered away from FIXED.DAT.

Debug teleport: `MainActor::teleport 8 20430 3250 0`

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

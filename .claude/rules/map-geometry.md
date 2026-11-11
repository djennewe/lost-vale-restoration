---
paths:
  - "agents/map-populator/**"
  - "agents/map-builder/**"
---

# U8 item boxes are HALF-OPEN. Never size an aperture with the cell flood.

Two mistakes here sealed the entire DD-005 entry route and shipped it, and the
"proof" that it worked was itself invalid. Both are cheap to avoid and
expensive to find in-engine.

## The half-open box

`Box::contains` is `px > _x - _xd && px <= _x`.

So a 96-wide filler placed at `x=2848` occupies **2753..2848 inclusive** — the
high edge is *in* the box. With the glob piece east of it occupying
2880..2943, the clear span is 2849..2879 = **31 units**. A body needing 32 has
**zero** valid positions. `Box::overlaps` is strict.

Off by one world unit, and the entire route was impassable.

## The cell flood cannot see this

`map_walkability` quantises to 32-unit cells and marks a cell blocked only
when a blocker covers the cell **centre**. The filler's last unit — 2848, the
first unit of cell 89 — vanished in that rounding. The cell read as fully
free, and a body-width flood walked through a gap the engine refuses.

**The cell raster is the right instrument for "can you get from A to B" and
the wrong one for a one-body-width aperture.** It reported 11,441 / 21,923
reachable cells as evidence for an aperture that did not exist.

## What to use instead

`test_crack_geometry.py` reimplements `Box::overlaps` verbatim and runs it
over the **built** `FIXED.DAT` with globs expanded — so it tests what ships,
not what the builder intended. Size single-body apertures with that, and add a
case there when you add one.

`map_walkability`'s aperture assertions were rewritten to stop claiming they
prove the mechanic. Don't re-add that claim.

## Test the built artifact, not the builder's intent

The generalisation behind both bugs: a builder can be correct and the shipped
map still wrong, because globs expand and rounding happens between the two.
Geometry assertions belong against expanded `FIXED.DAT`.

## A walking actor changes z by 0, ±4 or ±8 — and by nothing else

This one shipped an unclimbable mountain twice (2026-07-31 and again after
the "fix"; found in-engine 2026-08-18, filed as F10).

When a walk step lands unsupported, `AnimationTracker::step` falls back to
`CurrentMap::scanForValidPosition`, which does **not** scan a range. It
probes an enumerated table:

```cpp
static const int SEARCH_OFFSETS_U8[]  = {0, -4, 4, -8, 8};
static const int SEARCH_OFFSETS_CRU[] = {0, -1, 1, -2, 2, -3, 3, ...};
```

U8's table has no ±1, ±2 or ±3. **A 1-unit riser is refused exactly as a
9-unit riser is.** Read as "at most 8 units" — which the builder comment,
`exact_reach.py` and `test_route_reach.py` all did — it looks like a
bound, and a linear z interpolation sails through every check while the
engine refuses to walk it.

So: **every walkable surface must have its top on the 4-unit lattice**,
and every riser between adjacent surfaces must be 0, 4 or 8. Interpolate
in *steps*, never in world units:

```python
CLIMB_Z_STEP = 4
steps = CLIMB_Z_TOP // CLIMB_Z_STEP        # CLIMB_Z_TOP must be a multiple
z = CLIMB_Z_STEP * ((steps * k + last // 2) // last)
```

Decorative `SI_LAND|SI_SOLID` items at off-lattice z are not harmless
either: each is a phantom standing level the scanner cannot reach.

### Do NOT "fix" this by changing footpad z

The F10 write-up blamed `zd=0` footpads — "a zero-height box contains no
z, so the mover finds no support" — and prescribed bumping `zd` 0→1.
**That is wrong and would have made it worse.** `getPositionInfo` computes
support from an item's TOP face (`ib._z + ib._zd`), so a `zd=0` tile at
z=48 *does* support standing at z=48; and `Box::overlaps` needs
`_z + _zd > o._z`, so a zero-height box can never block. Give that tile
`zd=1` and it gains an 8-unit box spanning [48,56) which **overlaps the
Avatar's body box** [48,88) — every floor tile becomes a blocker.

(The two routines genuinely do disagree about `zd=0`: `getPositionInfo`
uses `Box::overlaps`, while `scanForValidPosition` computes its invalid
span as `[pt.z - z - zd + 1, pt.z + izd - z - 1]`, which for `izd=0`
still clears the mask at `vert=0`. That is a real asymmetry — it is just
not fixable from TYPEFLAG.)

## Never bury an item inside a solid, and never rest one on a solid's top face

Two placement mistakes, both found on 2026-08-18, both silent until you
try to interact with the item.

**Buried in a solid.** The three Tiny Tar potions sat at z=4 "on the
locked chest's cell". The chest (618) occupies z [0,16) and the furniture
beside it (526) occupies z [0,16); a 32x32x8 potion box at z=4 was
INSIDE them. An item interpenetrating a solid cannot be picked up or
stashed — `canReach()` sweeps a line of sight the enclosing box blocks,
and the drop trace resolves to the solid rather than to the Avatar. That
was F11, and it looked for weeks like an engine defect in the container
code. (It is not: every branch of `Container::CanAddItem` was ruled out
with in-engine data first.)

**Resting exactly on a solid's top face.** The obvious correction — put
them on the furniture top at z=16, which is clean geometry and properly
supported — makes the renderer's depth sort unresolvable when the small
box's XY overlaps the tall one. In-engine that logged
`Cycle in paint dependency graph 859 -> 526` about **11,000 times in a
few seconds**.

So place small carryables on **clear floor**, overlapping no solid and
with no tall neighbour to sort against. Check both, not just overlap:

```python
b = Box(x, y, z, 32, 32, 8)
assert not any(b.overlaps(ob) for ob in solids)          # not buried
assert not any(near_in_xy(o, x, y, 80) and o.zd >= 8     # nothing tall
               for o in solids)                          # to sort against
```

Note the support asymmetry if you do need a surface: `SI_SOLID` alone
gives support without land, and `getPositionInfo`'s
`landz + 8 >= target.z` test then fails — an item left there is
unsupported. The item needs an `SI_LAND` surface under it.

## Verify a map fix on a FRESH world, never from a checkpoint

A savegame carries its own instantiated map. Load a checkpoint and you
get the item positions that were baked in when that map was first
entered, **not** the ones in the FIXED.DAT you just rebuilt. The F11
retest initially "failed" for exactly this reason: cp24 restored the old
buried potions, paint-cycle spam and all. Start a new game and teleport
to the site instead.

## Related, same era

The engine was promoting eggs into Actors, which silently killed two event
eggs (`cb7fa78`). If an egg never hatches and the usecode looks right, check
what class the engine actually instantiated it as.

## A flat tile laid over a floor is sorted by its FLAGS, never its position

Found on Map 10 (2026-09-15): a court of 301 slabs and 589 tiles of 386
track laid on the glob floor's own grid were simply not there in-engine.
`SortItem::below` (`sort_item.cpp:145-181`) handles two zero-height items
at the same z with a fixed list of flag rules before any x/y comparison:
an `SI_DRAW` flat "always gets drawn first", then an `SI_OCCL` one. The
glob floors (242, 3) are `SI_OCCL`; 301, 386, 299 and 4 are `SI_DRAW`. So
an `SI_DRAW` overlay goes UNDER the floor, and shifting it a unit changes
nothing. An overlay must be a flat with neither flag — 6, 71, 425, 783
(`lv_shapes.py`) — or have height (299, 113 at 8 tall are sorted by z
range and draw fine, but then they are a step, and the pinned pads and
scene coordinates at z=0 sit inside them).

## The frame is never cleared: every void cell a player can see needs a floor

Found 2026-09-15 on Map 17's cloud islands, which stand in void "in the
dark". `Ultima8Engine::paint()` fills the frame black only when `_highRes`
is set (`ultima8.cpp:711`, the `usehighres` config key). Without it —
every player's default — wherever no item paints, the previous frame's
pixels stay. A retail map covers the screen wherever the camera can go;
an LV map is zones standing in void, and from any wall the view reaches
1,280 units past it on x−y and 1,600 on x+y (the 640×400 canvas; half at
320×200). So a player at the Arrival Plaza's wall saw the plaza's own
earlier frames beyond it, and the islands' "dark" was never dark.

Plates in the harness showed the same thing as "teleport residue" —
three teleports, one identical background — and it was not: the engine
had no wall or floor item there at all.

The floor is `lv_furnish.void_floor(items)`: a pure-black 256-unit plate
(shape 564 frame 2, `SHAPE_SHADOW_PLATE`) under every 128-cell that is
void and within view of a floor cell, computed from the builder's own
item list. Call it LAST in a map builder so it sees every floor. The
plate is `SI_DRAW`, which the rule above sorts UNDER every real floor at
the same z, so blocks may overlap floors freely and show only where
nothing else paints. `test_map_hygiene.py`'s `void_in_view` class counts
what is left per map and ratchets it: every LV map is 0 since 2026-09-17.
Water counts as cover (it paints; the lake is glob 55, sixteen `SI_SEA`
tiles) but not as a place to stand; the builder expands globs for real
before counting, because a chunk is not always sixteen floor tiles.

For plates of anything at a map's edge, set `usehighres=true` in
`scummvm.ini` (the harness has it) — but that is the harness's
convenience, not the fix, because players do not have it.

## A south or east rim paints over whatever stands behind it

Found 2026-10-10 on Map 10's Passage Test plateau (full-run part 5,
finding 3). The camera looks from the south-east, so a cliff on a zone's
south or east edge is sorted in FRONT of the ground it closes, and a face
standing h above that ground covers everything within about 8h of it in
x+y. The plateau's rim stood 128 over its floor: it covered 100% of the
Avatar where the scene teleports him (129 units from the south edge) and
83% of the witness, and the step-9 talk could not be clicked. A scripted
point near such an edge needs `item_sorter.overdrawn` (the
`test_schedule_destinations` check 4) — and the fix is
`lv_landscape.rim(flush=...)`: the visible courses end at the ground and
two courses of retail's invisible wall (497/498, `SI_EDITOR`: never drawn,
still solid) stop the walk and the jump off the edge.

## Some floors burn without SI_DAMAGING

The retail lava, shape 409 (glob 802), is LAND|SOLID, and its class
CLRLAVA's gotHit burns whatever touches it: 2-4 hp a contact, and its
frame-33 tiles kill. TYPEFLAG cannot see it, so a flood with SI_DAMAGING
in its mover flags walks straight across. Map 11's "harmless" lava lakes
killed a 10-10 run on the line from the Fire talisman to the doorway.
Model it with `ExactReach(hurt_shapes=HURT_SHAPES_U8, hurt_margin=...)`,
and keep it off the lines a player walks (`test_route_reach`'s
`FIRE_LINES`), not just off some route.

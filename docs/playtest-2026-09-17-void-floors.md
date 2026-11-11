# Playtest — the void floor on maps 9, 10, 11, 13 and 18 (2026-09-17)

The follow-up to `docs/playtest-2026-09-15-cloud-tiles.md` §V: the same
black floor Map 17 got on 2026-09-16, laid under the other five Lost Vale
maps. The engine never clears the frame without `usehighres`
(`ultima8.cpp:711`), so a player at a map's edge saw the previous frame in
the void beyond it. `.claude/rules/map-geometry.md`, last section, is the
rule; `lv_furnish.void_floor` is the fix; `test_map_hygiene.py`'s
`void_in_view` class is the ratchet.

Fresh world, the canonical build (`FIXED.DAT e9f6cc60…`; the other three
artifacts unchanged), the 640×400 canvas, plates cropped at `+565+336`,
**`usehighres=false`** throughout — the player's default, the configuration
the defect lives in. The key was set back to `true` afterwards.

## Verdicts

| ID | Test | Verdict |
|---|---|---|
| H1 | `void_in_view` is 0 on all six maps | **PASS** (60/60) |
| H2 | Only `FIXED.DAT` moved; a second build reproduces it; the estate passes | **PASS** |
| W09 | Map 9, Galjeron's chamber: black beyond the cave walls | **PASS** |
| W10 | Map 10, the vale's edge by the lake: black beyond the terrain | **PASS** |
| W11 | Map 11, the dungeon's edge: black beyond the section's wall | **PASS** |
| W13 | Map 13, the cliffs' edge: black beyond the cave wall | **PASS** |
| W18 | Map 18, the temple's edge: black beyond the outer walls | **PASS** |

## H1 — the ratchet

```
map 9  … void_in_view=0      (was 1,404 on 2026-09-16)
map 10 … void_in_view=0      (was 10,599)
map 11 … void_in_view=0      (was 9,941)
map 13 … void_in_view=0      (was 3,004)
map 17 … void_in_view=0      (2026-09-16)
map 18 … void_in_view=0      (was 2,206)
OK: 60 passed, 0 failed
```

Plates laid: 366 / 2,477 / 2,522 / 758 / 999 / 568. Each builder ends with
`items.extend(void_floor(items))`.

Two corrections to the counting landed with this, both found by the
ratchet refusing to reach zero:

1. **Water is cover.** Map 10 stayed at 1,230 after its floor: every one
   of those cells lay in a chunk tiled with glob 55, the lake — sixteen
   shape-347 tiles carrying `SI_SEA`, not `SI_LAND`. Water paints, so it
   covers; it is not a place to stand, so it does not seed the view. The
   test and the builder both use `floor_cells(..., painted=True)` for the
   cover and the LAND-only set for the seed.
2. **The builder expands globs for real.** The first version treated a
   glob egg as sixteen floor cells; the lake glob showed why that is not
   safe in general. `void_floor` now runs the builder's list through
   `expand_globs` before counting, so its count is the ratchet's count.
   The plate counts did not change on any map, and the artifacts did not
   move for it.

## W09–W18 — the plates

Each map was entered by a debug hop (an in-map hop first, then the
target), then a walk step to force the repaint, then the plate. The target
on each map is the z=0 floor cell that sees the most void within half a
canvas, chosen from the built `FIXED.DAT`, so each plate is the map's
worst case, not its kindest.

- `W09-galjeron-edge.png` — Map 9 at (14336, 12544, 0) (the second hop to
  the worst cell did not land; this is the entry point, whose walls face
  the void): the cave's rock walls, black beyond them on every side.
- `W10-vale-edge.png` — Map 10 at the lake's north shore by the pier's
  end: the lake's own dark water tiles (an opaque frame, their look),
  the shore terrain, and black where the vale ends. The rim cliff is at
  the top left.
- `W11-dungeon-edge.png` — Map 11 at (1151, 19423, 0), the fire section's
  south-west corner: the section's raised floor and its wall, black
  beyond, a sliver of the neighbouring floor top left.
- `W13-cliffs-edge.png` — Map 13 at (1659, 12283, 0), the base zone's
  west wall: the cave wall, the mossy path, black beyond the wall.
- `W18-temple-edge.png` — Map 18 at (4063, 607, 0), the temple exterior's
  north wall: the walls, lamps and doors, black beyond.

No plate shows any earlier frame. Before this change each of these spots
showed whatever the player had last looked at.

## Findings that were not part of the plan

1. **The second hop did not land on Map 9** (`objectInfo 1` reported the
   entry point). The plate still faces void, so it stands; the
   "in-map hop first" rule from the cloud-tiles report is not a
   guarantee.
2. **A wait loop of mine went runaway** (an `until grep` watching the
   newest task file, which was its own) and had to be stopped with
   TaskStop. Nothing of the game's; noted so the pattern is not reused.

## Disk changes

- `shared/u8-lv-patched/FIXED.DAT` (both copies) replaced with `e9f6cc60…`.
- `~/.config/scummvm/scummvm.ini`: `usehighres` switched to `false` for the
  plates and back to `true` after.
- The playtest session was stopped at the end.

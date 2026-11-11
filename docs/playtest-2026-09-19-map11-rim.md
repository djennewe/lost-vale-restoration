# Playtest 2026-09-19: Map 11 has an edge now

The same defect as Map 13, found by running Map 13's containment check over
the rest of the LV maps. Map 11, the Elemental Dungeon, let the Avatar walk
off it in every direction.

Build: `FIXED.DAT eabbc016…`, `EUSECODE.FLX a71868ae…` (unmoved). Fresh
world, cheats on for positioning only, `usehighres=false` for every plate
(restored to `true` afterwards).

## Verdicts

| ID | Test | Verdict |
|---|---|---|
| B1 | Pushing north-west from inside the earth section stops at the rim corner | **PASS** |
| B2 | Pushing east across the air section stops inside the map | **PASS** |
| B3 | The flood is bounded to the footprint on all four sides | **PASS (model)** |
| B4 | Maps 9, 17 and 18 are contained without a change | **PASS (model)** |

## B1: the north-west corner holds (PASS)

Teleported to (1400, 1400, 0), the far corner of the earth section, then
twelve north-west bursts at the walking gait (`session.sh walk 0 -130`,
1.4 to 1.5 s each):

    after eight bursts   (1088, 1088, 0)
    after four more      (1088, 1088, 0)

**y=1088 and x=1088** is exactly the predicted stop. The rim's west run for
chunk column 2 stands at x=1024 with a 32-wide box spanning 993..1024, the
north run for chunk row 2 likewise at y=1024, and the Avatar's own 64-wide
body box at 1088 spans 1025..1088. One unit closer and it overlaps.

`B1-nw-corner-stop.png`: the Avatar against two rock runs meeting in a
corner, the dungeon's mossy floor inside, black beyond.

## B2: the east edge holds (PASS)

Teleported to (19200, 5000, 0) in the air section, then ten east bursts.
He stopped at **x=19408** and stayed there across the last four. The rim's
box on that edge begins at 19457, so what held him is the section's own
stone wall. He is inside the map, where before he was not.

`B2-east-edge.png`, shot from (19000, 5000, 0): the stone floor, the rim's
rock along the south-east edge, black beyond it.

## B3: the flood is bounded (PASS, model)

`exact_reach` seeded at both of Map 11's arrival pads, (9728, 1792, 0) and
(8448, 23040, 0), over a fixed ROI of 0,0 to 22455,26551 (the footprint
plus 3,000 units), 32-unit lattice, 8-unit z steps:

    before   reached 309,402 of 314,131   bbox x 31..21023   y 31..25119
    after    reached 146,920 of 336,717   bbox x 1119..19423 y 1119..23519

The footprint is x 1024..19455, y 1024..23551. Before the rim the flood
filled the ROI in every direction; after it, the reached bbox sits inside
the footprint on all four sides.

## B4: the other maps (PASS, model)

The same check, seeded at each map's own teleport targets with a 3,000-unit
margin, before any change:

| Map | Footprint | Reached bbox | Verdict |
|---|---|---|---|
| 9 | x 12800..14847, y 12288..16895 | x 12895..14815, y 12383..16863 | contained |
| 11 | x 1024..19455, y 1024..23551 | x 31..21023, y 31..25119 | **leaked** |
| 17 | x 1024..8191, y 512..11775 | x 1119..8159, y 607..11743 | contained |
| 18 | x 1024..5119, y 512..8703 | x 1631..4575, y 607..6111 | contained |

Map 10 already carries `build_rim()` from the 2026-09-15 landscape pass and
Map 13 gained one earlier today, so 11 was the last LV map with no edge.

## The fix

`build_map_11.build_rim()`, the same shape as Map 13's: `lv_landscape.rim`
over the chunk set read back off the glob eggs the section builders emit,
two courses and a crest, placed in the void just beyond each chunk edge so
no floor is lost. It adds 3,207 items.

The rim's shapes, 26 and 32, are the cave walls this builder already uses
for its own walls, so the dungeon reads as rooms carved into rock. Every
glob on the map sits at z=0, so the rim is a uniform 96 tall, the height of
the two-course stone the rooms are walled with.

The voids between the sections lie outside the outline. None is a hole
inside it, so `rim` walls both faces of each and they stay black.

## Findings that were not part of the plan

None. 33 items sit outside the glob footprint on this map and all 33 are
wall pieces (shapes 10 and 15) at a room's boundary, which is structural.
Map 13's stranded-dressing class does not appear here.

## Harness anomalies

1. **The backpack and minimap gumps reopen after a teleport**, as on the
   Map 13 run. Four plates were retaken for it.

## Disk changes

- `docs/playtest-2026-09-19-map11-rim.md` and its plate directory.
- `shared/build/*` rebuilt and re-recorded (`FIXED.DAT eabbc016…`).
- `~/.config/scummvm/scummvm.ini`: `usehighres` false during the session,
  **restored to true**.
- No savegames written.

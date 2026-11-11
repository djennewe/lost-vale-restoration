# Playtest 2026-09-25: one plinth under the four pillars

Follow-up to `docs/playtest-2026-09-24-elemental-pillars.md`, finding 2:
the Earth and Air pillars (sheet C2) stood on violet plinths and the Fire
and Water pillars (sheet C3) on the ring stone's blue-grey. Douglas's call:
"fix it now, C3 plinth under all four." `tools/art/pillar_plinth.py`
rebuilt the two C2 frames on C3's plinth (`C2_f0_earth_c3plinth_raw.png`,
`C2_f1_air_c3plinth_raw.png`), `lv_art_props.py` row 865 points at them,
and only `U8SHAPES.FLX` moved (`0db9dbe9…` → `a611e9be…`; TYPEFLAG,
EUSECODE, and FIXED unchanged, so the detection entry and the ScummVM
binary stayed). This session checks the result in the engine.

Harness: `tools/playtest-linux/session.sh` on `:77`, the 640×400 window
at (565, 336) of the 1450×873 screen, rendered 1:1. A fresh world,
cheat-teleported to Map 11; a diagnostic run in the sense of the
2026-09-06 step 4 report.

## Verdicts

| ID | Test | Verdict |
|----|------|---------|
| B1 | All four pillars stand on the same blue-grey plinth | **PASS** |
| A1 | The four shape-865 items still bind class 865 after the U8SHAPES move | **PASS** |

## B1: one plinth, PASS

`B1-north-pair-earth-air.png` (Avatar at (8192, 20480, 0), between the
north pair) and `B1-south-pair-fire-water.png` (at (8192, 21504, 0)): the
rock spire and the twister now stand on the same grey block as the flame
and the water column. `B1-all-four-from-the-earth-pillar.png` (Avatar at
(7936, 20608, 0)) holds all four in one frame: Earth top centre, Fire
left, Air right, Water at the bottom edge, four grey plinths.

Measured on the built frames, the same pipeline the build runs
(`png2shape.build_frame` at 96 px, donor 38, then decoded), mean plinth
colour per frame, Earth, Air, Fire, Water:

    before  (55, 55, 101)  (51, 51, 93)  (59, 59, 75)  (58, 58, 73)
    after   (66, 66, 83)   (60, 60, 76)  (59, 59, 75)  (58, 58, 73)

Blue over red went from 46 and 42 on the C2 pair against 16 and 15 on
the C3 pair, to 17 and 16 against 16 and 15. Frame sizes are unchanged
(24x95, 24x96, 23x95, 23x96), so nothing about the footpad or the
collision box moved.

One difference between the sheets stays: C2 drew its plinth taller than
C3 did (full width at row 840 of 1024 against 866), and at 96 px the
Earth block is 18 rows to the Fire block's 17 (grey rows on
`C23_h96_1x.png`). Same stone, one row taller. Not fixed.

## A1: the binding survives the U8SHAPES move, PASS

`ObjectManager::findShape 865` after the teleport:

    Item 14449 (class Item, shape 865) (uc: TYPEELEM), 0, (7680, 20480, 0) q: 201 ... shapeinfo f: 3
    Item 14460 (class Item, shape 865) (uc: TYPEELEM), 1, (8704, 20480, 0) q: 202 ...
    Item 14471 (class Item, shape 865) (uc: TYPEELEM), 2, (7680, 21504, 0) q: 203 ...
    Item 14482 (class Item, shape 865) (uc: TYPEELEM), 3, (8704, 21504, 0) q: 204 ...
    findShape 865: 4 found

Same four items, same frames, same coordinates, same `(uc: TYPEELEM)` as
on 2026-09-24. The frame swap changed pixels and nothing the engine binds
on.

## Harness anomalies

- **The first plate after the map switch was black but for the Avatar and
  a monster sprite**, taken 2 s after `Loading Fixed items in map 11`
  reached the log. Retaken 6 s after the teleport it was drawn. Waiting
  for the load line is not enough; give the first draw a few more seconds.
- **The pack gump came back after a `dbg.sh` teleport.** A fresh start
  opens it (known trap); a double-click on the gump's left frame edge,
  window (278, 150), closed it; after the next `dbg.sh "MainActor::teleport
  …"` it was open again, and after the one after that, closed. The south
  retake probed the flap's brown at window (320, 120) before its plate
  and would have closed the gump had it found it.
- **Two of seven `dbg.sh` teleports in the first session did not land**
  (the sixth and seventh; each plate repeated the previous position, and
  the seventh overwrote the south pair plate with the all-four view).
  The south pair was retaken in a second session whose first teleport
  landed, checked by probing for the flame's orange where the Fire
  pillar projects (window x 180-205, y 50-135: 750 px found) before the
  plate. Probe the landing.

## Disk changes

- `shared/u8-lv-patched/STATIC/U8SHAPES.FLX`: synced by `session.sh start`
  from `shared/build/U8SHAPES.FLX` (`synced STATIC/U8SHAPES.FLX <-
  shared/build/U8SHAPES.FLX`). `shared/data/u8-install/` re-installed by
  `install_lv.sh`. No savegame written.

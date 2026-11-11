# Playtest 2026-09-19: Map 13 has an edge now

Verifying the rim added to `build_map_13` against
`docs/playtest-2026-09-18-map10-walk.md` finding 2, where the Avatar walked
off Map 13's south side and kept going 3,300 units through unpainted black.

Build: `FIXED.DAT 7c141b84…`, `EUSECODE.FLX a71868ae…` (unmoved). Fresh
world each time, cheats on for positioning only, `usehighres=false` for
every plate (restored to `true` afterwards).

## Verdicts

| ID | Test | Verdict |
|---|---|---|
| A1 | Walking south from the arrival pad stops at the south rim | **PASS** |
| A2 | The rim reads as a cliff, with black and no floor beyond it | **PASS** |
| A3 | The other three edges hold | **PASS (model only, not walked)** |
| A4 | The three props that stood outside the terrain are on it now | **PARTIAL**: the urn is shot, the two boulders are not |

## A1: the walk south stops (PASS)

Teleported to (3888, 11900, 0), 388 units north of the terrain's last row,
waited out the Guardian one-shot, confirmed `m: 13`. Then ten south bursts
at the walking gait (`session.sh walk -130 65`, 1.4 to 1.5 s each):

    after six bursts   (3868, 12288, 0)
    after four more    (3868, 12288, 0)

He advanced 388 units and then moved zero across four further bursts. The
stop is at **y=12288**, the last row of base-zone terrain. The rim's south
run stands at y=12320 with a 32-deep box spanning 12289..12320, and the
Avatar's own 64-wide body box at y=12288 spans 12225..12288, so 12288 is
the last position that does not overlap the wall. That is exactly where he
stopped.

The prior observation, on 2026-09-18 and on the pre-rim build, was the same
heading carrying him to (4368, 17152, 0).

## A2: the rim reads as a cliff (PASS)

`A1-south-rim.png`: the Avatar on the valley floor with the rim's rock face
and grey crest running across the frame in front of him, and pure black
beyond it. No floor, no stale frame, no item past the wall.

Two courses of 26/32 rock (96 tall) with a 125 crest one course above,
placed in the void beyond each chunk edge. That is `lv_landscape.rim`, the
same call Map 10's `build_rim()` makes.

## A3: the other three edges (PASS, model only)

Not walked. `exact_reach` over the whole map plus a void margin
(ROI 256,0 to 8700,14500, 16-unit lattice, 8-unit z steps, seeded at the
arrival pad) floods the engine's own box arithmetic and reports:

    reached 237,128 of 455,361 standable lattice positions
    reached bbox  x 1615 .. 6655   y 15 .. 12287

The terrain footprint is x 1536..6655, y 0..12287. The flood stops inside
it on every side.

**The controlled comparison** is the same flood over one ROI, run on both
builds. Over the base zone (ROI 512,9216 to 8192,16384) the pre-rim
`FIXED.DAT` reached **130,913 of 131,961** standable positions, which is the
whole plane, void included; the rim build reaches **58,722**, the footprint
alone.

The model sees `FIXED.DAT` only and checks positions rather than the swept
volume between them, so it is evidence about the geometry. The walk in A1
is what ties it to the engine.

## A4: the three stranded props (PARTIAL)

Found while shooting the rim: three items had always stood outside Map 13's
terrain, invisible while everything beyond the edge was void, conspicuous
once a cliff closed it.

| Shape | Was | Now | Why it was wrong |
|---|---|---|---|
| 796 boulder | (1792, 12544, 0) | (1792, 12032, 0) | 257 units south of the base zone's last row |
| 796 boulder | (6400, 12288, 0) | (6400, 12160, 0) | 1 unit south of it |
| 229 urn | (5376, 256, 120) | (4480, 256, 120) | 769 units east of the plateau's last paving tile, hanging at z=120 over nothing |

`A2-summit-urn.png` shows the urn on the paving at the plateau's east end,
beside the column, mirroring the rock at the west end. The two boulders were
not shot. The builder check that found all three now returns zero items
outside the glob footprint.

## Findings that were not part of the plan

1. **Standing against the south rim hides the Avatar.** At (3888, 12280) he
   is behind the wall: a 96-tall run one row south of him draws in front of
   his sprite, and the frame shows rock where he is standing. This is how
   any south-facing cliff in U8 behaves, and it is why A1's plate was taken
   from 388 units back. Worth knowing before someone reports a vanished
   Avatar at a map edge.

## Harness anomalies

1. **The backpack and minimap gumps reopen after a teleport.** Three plates
   were spoiled by one or both. `i` and `m` toggle them; a double-click on
   the pack's frame reopened it instead of closing it, because that is
   `use` on the owner.
2. **`walkto.py` never printed under a 110 s timeout.** Each `nav.pos()`
   goes through `dbg.sh`, which costs about 5 s, so a leg is minutes of
   wall clock. Direct `session.sh walk` bursts with a position read at the
   end did the same job in a fraction of the time, and that is what A1
   used.
3. **The first `dbg.sh` after `session.sh start` can be swallowed.** One
   teleport left the Avatar on map 3 with no error. Read the position back
   every time.
4. **The blue arrow in the void on three plates is the mouse cursor.** It
   was chased with a click probe and a pixel zoom before that was clear.

## Disk changes

- `docs/playtest-2026-09-19-map13-rim.md` and its plate directory.
- `shared/build/*` rebuilt and re-recorded (`FIXED.DAT 7c141b84…`).
- `~/.config/scummvm/scummvm.ini`: `usehighres` false during the session,
  **restored to true**.
- No savegames written.

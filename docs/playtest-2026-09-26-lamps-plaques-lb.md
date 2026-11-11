# The moved lamps, two new plaques and the Lord British scene in the engine (2026-09-26)

Verification of commit 2f27d51 (EUSECODE `7b916203`, FIXED `6c518f4f`).
`session.sh start` synced FIXED.DAT (both copies) and EUSECODE.FLX into
`shared/u8-lv-patched/`, and all four harness artifacts matched
`shared/build/ARTIFACTS.sha256` before play. `scummvm-lv/scummvm`, one pid,
640×400 canvas, crop `+565+336`. Two fresh worlds (new game, Devon's
conversation closed with **Goodbye.**), so every map was entered fresh and no
checkpoint was loaded. Travel by `MainActor::teleport` with cheats on; the
egg walk-in, the walk after the scene and every click are player input.
Plates are in `docs/playtest-2026-09-26-lamps-plaques-lb/`.

## Verdicts

| ID | Test | Observed | Verdict | Plates |
|---|---|---|---|---|
| L1 | Hall A lamp out of the Scroll Chamber doorway | `findShape 314`: item 7995 at (2432, 2080, 16); no shape-314 lamp spans x 2560..2815 on that wall; the Avatar walked from (2688, 2250) through the doorway to (2688, 1850) | **PASS** | `L1-lamp-west-of-doorway.png`, `L1-avatar-in-doorway.png`, `L1-through-into-scroll-chamber.png` |
| L2 | Main Plaza lamp out of the Hall B doorway | item 7750 at (5824, 5152, 16), spanning 5728..5824; plaque 70 at x 5055 and tapestry 7746 at 5920..6016 are clear of it; the Avatar walked from (5450, 5400) through the doorway to (5450, 5000) | **PASS** | `L2-doorway-plaque-lamp.png`, `L2-avatar-at-doorway.png`, `L2-through-into-corridor.png`, `L2-lamp-east-wall-section.png` |
| P8 | Stele and plaque q55 by the obelisk | plaque item 7740 at (4127, 7552, 16) q 55, `n: 235`; double-click logs `event 1 @ 04EB:00A9`; gump reads **ADMIRE / BUT / TOUCH NOT**; pid unchanged, 0 `Assertion`/`segment 0000` lines | **PASS** | `P8-before-double-click.png`, `P8-plaque-gump.png`, `P8-plaque-gump-zoom.png` |
| P8-look | The stele next to the dais | legible, but it reads as a block on the dais's south-west skirt more than a freestanding stele | **PARTIAL** | `P8-stele-with-obelisk.png`, `P8-stele-zoom.png` |
| P9 | Moriens stub and plaque q66 | plaque item 9667 at (12255, 22208, 16) q 66; double-click logs `event 1 @ 04EB:00A9`; gump reads **BIRTHPLACE / OF / MORIENS**; no crash | **PASS** | `P9-moriens-ruin.png`, `P9-before-double-click.png`, `P9-plaque-gump.png`, `P9-plaque-gump-zoom.png` |
| LB1 | Scene fires and speaks | egg 8104 (q 304) `hatched=0` → walk-in → `event 7 @ 05AF:0080`; "Avatar...", sparkles, the full message, sparkles, apparition gone | **PASS** | `LB0-lane-apparition-placed.png`, `LB1-message-bark-start.png`, `LB2-message-bark-end.png`, `LB4-run2-opening-sequence.png` |
| LB2 | Flags | `[06A5 01]` lbStarted 0 → 1, `[06A6 01]` lbDone 0 → 1; `findShape 411` 1 → 0; egg `hatched=1` | **PASS** | (log values) |
| LB3 | Camera re-attaches | `objectInfo 1` `ef:` 0x122 before, **0x102** during the scene, 0x122 after | **PASS** | `LB3-camera-back-on-avatar.png` |
| LB4 | View follows a 1,500-unit walk | (17114, 19694) to (17530, 21246), 1,607 units straight, 1,968 walked; Avatar centred in every plate | **PASS** | `LB6-walk-before.png`, `LB6-walk-1152-south.png`, `LB6-walk-after-1607.png` |
| LB5 | The apparition animates (`puppet(lb)`, the method this commit changed) | frame 0 → 1 once when the message starts, then frame 1 for the whole bark; frame 9 never shows; the compiled `puppet` has no backward jump | **FAIL** (not in the requested checks; Finding 1) | `LB4-apparition-static-during-bark.png`, `LB5-shape411-frames-0-9.png` |

## L1: Hall A's lamp, PASS

`findShape 314` on Map 17 listed ten wall lamps. The two on Hall A's north
wall are 7994 at (1792, 2080, 16) and 7995 at (2432, 2080, 16). A lamp spans
96 units west of its x, so 7995 covers 2336..2432, 128 units short of the
doorway's west jamb at 2560. None of the ten covers any of x 2560..2815.

The doorway is a gap in the ground course under a continuous upper course,
so from the south it reads as a lintel. Walking settles it: from
(2688, 2250) north, `objectInfo 1` read (2688, 2050) with the Avatar
standing in the opening and the lamp well to his west
(`L1-avatar-in-doorway.png`), then (2688, 1850) inside the Scroll Chamber
with the view still centred on him (`L1-through-into-scroll-chamber.png`).
`L1-lamp-west-of-doorway.png` is the approach plate.

## L2: the Main Plaza's east lamp, PASS

Item 7750 is at (5824, 5152, 16), covering 5728..5824. The Hall B doorway is
5120..5631, so the lamp starts 97 units east of the east jamb. Plaque 70
(item 7653, x 5055) is west of the doorway, 673 units from the lamp.
Tapestry 7746 (shape 329, frame 5, x 6016) covers 5920..6016, a 96-unit gap
east of the lamp.

`L2-doorway-plaque-lamp.png` and `L2-avatar-at-doorway.png` show the gold
plaque left of the doorway, the open floor under the lintel, and the lamp on
the wall section to the right. From (5450, 5400) north, the Avatar read
(5450, 5200), then (5450, 5000) in the corridor, behind the wall
(`L2-through-into-corridor.png`). The one other lamp in view is 3216, a
shape-317 lamp on the corridor's west wall at (5151, 4864, 16).

The tapestry did not show in `L2-lamp-east-wall-section.png`; see Finding 2.

## P8: the stele by the obelisk, PASS (reads), PARTIAL (looks)

Plaque item 7740 sits at (4127, 7552, 16), q 55, `n: 235`, 385 units south of
the obelisk (item 7736, shape 861, (4095, 7167, 16)).
`P8-stele-with-obelisk.png` has both in frame.

From (3900, 7650), about 250 units off, a double-click logged only the look
line, twice. From (4082, 7665), 45 units west and 113 south of the plaque
(`px=(39,-5)`), the double-click at window (351, 183) logged

    Item 7740 (class Item, shape 614) (uc: PLAQUEEW), 0, (4127, 7552, 16) q: 55, m: 0, n: 235, ...
    Item: 7740 (shape 614) calling usecode event 1 @ 04EB:00A9

and the gold plaque gump came up reading ADMIRE / BUT / TOUCH NOT
(`P8-plaque-gump.png`, `P8-plaque-gump-zoom.png`). The ScummVM pid was
unchanged and `grep -c 'Assertion\|segment 0000\|stuck in process'` on the
session log read 0. A single click on the gump closed it.

**Look.** The stele is one 128-unit wall piece, one course high, set against
the dais's south-west corner (`P8-stele-zoom.png`). Its top sits a little
above the lowest tier, and from the default view it merges with the dais
skirt: the plaque reads as mounted on the dais, and the stele does not read
as its own standing stone. It is legible and nothing about it is wrong in
engine terms. By the map dressing standard it is borderline. Two options:
set it 64 to 128 units further south so floor shows between stele and dais,
or leave it as a dais-mounted plaque, which is what it reads as now.

## P9: the Moriens plaque, PASS

`P9-moriens-ruin.png` is the ruin from (12255, 22500): the two tall columns,
the one-course stub between them, and the plaque on its south face at head
height. It sits well. From (12210, 22321) (`px=(39,-5)`) the double-click
logged item 9667, `event 1 @ 04EB:00A9`, and the gump read BIRTHPLACE / OF /
MORIENS (`P9-plaque-gump.png`, `P9-plaque-gump-zoom.png`). No crash, 0
`Assertion` lines.

## LB: the Lord British scene, PASS on every requested check

**Run 1** (fresh world; the first teleport of the session had gone to Map 17,
followed by a 25 s wait for the Guardian cutscene, per `traps.md`). Before: `[06A5 01] = 0`, `[06A6 01] = 0`, `findShape 411`
one item, 8105 (`uc: GHOST`) at (17150, 19850, 48), frame 0; egg 8104 at
(17150, 19700, 48), q 304, range 4×4, `hatched=0`
(`LB0-lane-apparition-placed.png`). Teleported to (17070, 20050, 48), outside
the egg's box, and walked north. The first walk stopped at (17010, 19694),
12 units west of the box's x edge, and nothing hatched. A 0.6 s step east to
(17114, 19694) crossed into it, and the log showed

    Item: 8104 (shape 73) calling usecode event 7 @ 05AF:0080

with the "Avatar..." bark on the next plate. A position read taken that
instant gave `ef: 0x102`: the scene's `scrollTo` had detached the camera.
The console then stayed closed for the rest of the scene. The full message
played over roughly 100 s (`LB1-message-bark-start.png` through
`LB2-message-bark-end.png`, ending "...Britannia is in great need of
thee..."), then the view snapped back to the Avatar at the window centre
(`LB3-camera-back-on-avatar.png`). The log carried no `WARNING`, `Assertion`
or `stuck in process loop` line from the walk-in to the end.

After: `[06A5 01] = 1`, `[06A6 01] = 1`, `findShape 411: 0 found`, egg
`hatched=1`, `objectInfo 1` `ef: 0x122`.

**The walk.** From (17114, 19694, 48), south in running bursts:
(17114, 20846, 0), then east to (17530, 20846, 0), then south to
(17530, 21246, 0). That is 1,607 units in a straight line from the start.
`f: 0x2041` at every read, `ef: 0x122` at every read, and the Avatar is at
the window centre in `LB6-walk-before.png`, `LB6-walk-1152-south.png` and
`LB6-walk-after-1607.png`. The first burst ran him off the lane's south edge
and down 48 units (Finding 3), which is why the later plates are mostly void;
the grass edge moves across them while he stays centred.

**Run 2** (second fresh world, for a fast capture): teleported to
(17200, 20000, 48), waited out the Guardian cutscene, walked north into the
box, and captured 200 frames over 29.8 s with the console closed. The same
scene played, and afterwards lbDone read 1, `findShape 411` read 0 and `ef`
read 0x122. The capture is the evidence for LB5.

## Findings

1. **The apparition does not animate.** `LORDBRIT.UNK`'s `puppet(lb)` sets
   frame 0, then cycles frames 1..8 every `wait(5)`, holds frame 2 for
   `wait(120)` every fourth cycle, and switches to frame 9 once lbDone is
   set. Shape 411 has ten distinct frames: 0-6 an arms-raising cycle, 7-9 a
   dark, translucent fade (`LB5-shape411-frames-0-9.png`). In run 2 the
   apparition holds frame 0 through the sparkles, changes once to an
   arms-raised pose as the message starts (`LB4-run2-opening-sequence.png`,
   f063 to f066), and then keeps that pose: a pixel signature of the body
   is identical across 137 consecutive frames, 0.15 s apart, about 20 s
   (`LB4-apparition-static-during-bark.png`). Run 1 shows the same pose from
   the first bark to the snap-back, and frame 9 never appears
   (`LB2-message-bark-end.png`). The compiled class explains it. In
   `EUSECODE.FLX` class 05A3, `puppet` (offset 06B1..0760) runs straight
   through: `setFrame(0)`, the lbDone test, the `count = 4` branch, the
   `getFrame() = 8` test, `fram` to 1, `wait(5)`, `setFrame(1)`, `ret`. It
   has no backward jump, so the `process { ... }` block compiles as one
   pass. The frame it lands on, 1, is the arms-raised pose on screen.
   `this` does reach it: every `setFrame` pushes `addr [BP+0Ah]`, and the
   frame change lands on the apparition.

   **A fix has to change the spawn too.** `use()` spawns the puppet at 0279
   as `spawn 05A3:06B1` followed by `implies` and `suspend`, so `use()`
   waits for the puppet to return before the message bark. The bark plays
   today only because the puppet returns after one pass. A puppet that
   loops as written would hold `use()` at that line until lbDone is set,
   and lbDone is set only after the bark, so the scene would stall with
   the Avatar in stasis (`traps.md`, "A process spawned from `hatch` must
   be the LAST statement", is the same mechanism).
2. **Tapestry 7746 at (6016, 5121, 0) did not show** in the Main Plaza plates
   (`L2-lamp-east-wall-section.png`); only a small dark mark near the north
   wall's east corner is visible where it should hang. The 2026-09-25 plate
   of the same wall (`F2-lamp-in-doorway-5568-5152.png`) does not show it
   either, though the corner sits near that plate's edge, so it probably
   predates this commit. Not investigated. It does
   not touch the lamp either way.
3. **The Map 39 grass lane ends in a 48-unit drop.** Running south from the
   egg, the Avatar left the z-48 lane near y 20100 and landed at z 0 in the
   black void south of it, where he can still walk. The lane's builder note
   covers only the moat to the north. A player walking the lane south would
   find the same edge.
4. **Plaque double-clicks need to be close.** At about 250 units the
   double-click on q55 logged the look line and nothing else; at about 120
   units it opened the gump. Most likely retail behavior, and the reason
   both P tests were run from 45 west and 113 south of the plaque.

## Harness anomalies

- **The first `noexit` chord after a `dbg.sh` call failed four times.** Each
  time the teleport or `toggleCombat` letters went to the world: the Avatar
  came out in combat mode (`flags: 800`), and once the minimap opened. A
  helper that verified the position, retried the teleport, and sent
  `toggleCombat` when it saw `flags: 800` recovered every case. The second
  attempt always landed.
- A `shot.sh` left in the scratchpad by an earlier session (a
  teleport-and-plate script with map 8 hard-coded) ran once in place of a
  plain capture. Cheats were off, so it printed `Cheats are disabled` and
  moved nothing.
- One `dbg.sh "Kernel::listProcesses 13841"` during run 2 did not reach the
  console; its `exit` opened and closed the pack (two `event 1` on item 512).
- The walk verb at offset (140, -70) drifted west enough to stop 12 units
  outside the egg's box on the first try.

## Disk changes

- `shared/u8-lv-patched/`: FIXED.DAT (both copies) and EUSECODE.FLX synced
  from `shared/build/` by `session.sh start`.
- `~/.local/share/scummvm/saves/ultima8.000` was rewritten on quit (the
  autosave slot) and restored from the pre-session backup; all eight
  `ultima8.00*` files and `timestamps` match their pre-session md5.
  `scummvm-history.txt` (the console history) was also rewritten and was
  restored from the same backup; it is byte-identical again.
- `~/.config/scummvm/scummvm.ini` is byte-identical to the pre-session copy.
- Session stopped; no ScummVM or Xvfb left running.
- `TODO.md` not updated.

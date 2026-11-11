# Playtest 2026-09-25: the two walk-path gates are gone

Verification of commit f5fe0b7 (FIXED `00925049`; TYPEFLAG, U8SHAPES and
EUSECODE unchanged). `session.sh start` synced FIXED.DAT (both copies) into
`shared/u8-lv-patched/`; all four `shared/build/` artifacts matched
`ARTIFACTS.sha256`. `scummvm-lv/scummvm`, 640x400 canvas, crop `+565+336`,
`usehighres=true`. A fresh world, cheat-teleported to each site; every
crossing is a player walk (`walkto.py --walk`, right-button bursts, no
teleport). Plates are in `docs/playtest-2026-09-25-gates-removed/`.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| G1 | Map 13 climb foot, gate at (4096, 10752, 4) gone, Avatar walks through | `findShape 114`: 0 found on Map 13. Walk (4096, 11100) to (4036, 10944), then one burst to (4036, 10544) and on to (4036, 10448), through the 128-unit gap (3967..4095] | **PASS** |
| G2 | Map 10 processional, gate at (18432, 23040, 0) gone, Avatar walks through | `findShape 114`: 1 found on Map 10, item 9342 at (7168, 23552, 8) q 170, the cloud-terrace gate the commit keeps. Walk (18432, 22800) to (18432, 23032), standing in the gap, then to (18432, 23392) and back to (18432, 23296) | **PASS** |

## G1: Map 13, PASS

`G1-approach-south-of-stubs.png` (Avatar at (4096, 11100, 0)): two plain
stone slabs on y=10752 with open floor between them, no gate sprite.
`G1-through-north-of-stubs.png` (Avatar at (4036, 10448, 0)): the Avatar
north of the line, the stubs behind him. The crossing burst went from
y=10944 to y=10544 with no stall at the wall line. One stall read at
(4096, 11004), south of the stubs and 250 units short of them, is the
walker's burst timing; the next burst moved.

The stubs are two full courses of `WALL_PLAIN` (z 0 and 40), squared off.
In the plate they read as an intact wall with a doorway in it more than a
ruin; nothing about the gap reads as broken. Left as observed.

## G2: Map 10, PASS

`G2-approach-north-of-stubs.png` (Avatar at (18432, 22700, 0)): the pale
middle lane runs between the two stubs with no gate; columns flank the way.
`G2-in-the-gap.png` (Avatar at (18432, 23032, 0)): the Avatar standing
between the west and east stubs. `G2-through-south-of-stubs.png` (Avatar at
(18432, 23296, 0)): the Avatar on the forecourt south of the line, the
stubs behind him.

## Findings

1. **A walk burst past y about 23450 on the middle lane lands on Map 18.**
   The first G2 attempt targeted (18432, 23350) from (18432, 22932) in one
   leg; the burst overshot and the next read was Map 18 at (4056, 2464, 0)
   (`F1-overshoot-lands-on-map-18.png`). That is the teleporter egg 211 at
   (18432, 23552), hatch range npcnum 211 = 0xD3, so plus or minus 416 in x
   and 96 in y, firing on a walked arrival, as built. The Avatar also stood
   and walked across (18432, 22784), the teleport-target egg labelled
   "Teleport TRIGGER (ID 210)" in `build_map_10.py`, with no map change; the
   label names the pad, and the trigger is the `teleporter` call after it.
   The retake used two short legs and stayed south of the stubs at 23296.

## Harness anomalies

- **The first `Cheat::toggle` of the first session did not land.** Its
  reply never reached the log, and the chord, command, Return teleport that
  followed printed `Cheats are disabled`, leaving the console open. The next
  `dbg.sh` chord closed it and typed its command into the world; the
  minimap came up. Restarted the session; the second start's toggle printed
  `Cheats = true` on the first try, and every teleport after that was sent
  as chord, command, Return with no `exit` and landed.
- **No pack gump appeared** in either session, before or after teleports.

## Disk changes

- `shared/u8-lv-patched/FIXED.DAT` and `STATIC/FIXED.DAT` synced to
  `00925049` by `session.sh start`.
- `~/.local/share/scummvm/saves/ultima8.000` (the autosave) was rewritten
  by the session and restored from a copy taken before it; `timestamps` and
  `scummvm.ini` came out byte-identical. `scummvm-history.txt` (the console
  history) now carries this session's commands.

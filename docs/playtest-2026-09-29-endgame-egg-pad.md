# The endgame egg on the arrival pad, verified in engine (2026-09-29)

Change under test: the uncommitted work on HEAD `4f981fe`, on top of the bag
change verified on 2026-09-27. `build_map_10.py` moves EggEndgame (quality
299, class 1450) from (18432, 22016) npcnum 0x88 to (18432, 22784) npcnum
0x86, the location of Map 10's arrival pad for returns from Map 18 (the
frame-1 target, teleport id 210). `test_manifest.py` patches
`build_eusecode.REPO_ROOT` in its append test. EZREKAL.UNK and
`lv-patched-inventory.md` gain comments.

Artifacts: a full `tools/build_artifacts.sh` exited 0 and matched all four
canonical hashes (FIXED.DAT `f92973ee...`, EUSECODE.FLX `7f885f5e...`).
`./install_lv.sh` ran first; `session.sh start` synced both FIXED.DAT
copies into `shared/u8-lv-patched/`; the engine logged `usecode/eusecode.flx:
aae44805..., 1505576 bytes` and `Running Ultima VIII: Pagan (Gold Edition +
Lost Vale/DOS/English)`. Binary `scummvm-lv/scummvm` linked 2026-09-27
15:19, after fork tip `e0d6084d` (2026-09-19). One ScummVM process ran every
test; 0 `Segmentation` or `Assertion` lines, 0 `Cheats =` lines, 0
`setGlobal`, 0 `MainActor::teleport`. Plates are in
`docs/playtest-2026-09-29-endgame-egg-pad/`, named by test ID, 640x400.

## Verdicts

| ID | Test | Observed | Verdict |
|---|---|---|---|
| S1 | Test estate | `run_all_tests.sh` 31/31 PASS, exit 0; `test_uc_eggs.py` 49 passed; round-trip 516/516 | **PASS** |
| S2 | Build and hashes | full build exit 0, all four artifacts OK against `ARTIFACTS.sha256` | **PASS** |
| S3 | Compilation Report | 48 files, 46 succeed; `EALOGO.UNK` and `TJORVI.UNK`, the allowlist pair | **PASS** |
| S4 | ScummVM fork | no fork commit; patch-equality diff silent | **PASS** |
| S5 | Shapes | no shape ID touched | **not triggered** |
| S6 | `exact_reach.py` | no aperture, gap, or route changed: an egg moved on existing paving; the 09-27 bypass route was walked in engine in B instead | **not triggered** |
| S7 | New usecode class | none; EggEndgame is existing class 1450, dispatched in engine at `05AA`; EUSECODE bytes unchanged, so the EZREKAL edit is comment-only | **not triggered** |
| A | Arrival from Map 18 hatches the egg with no step | Map 10 loaded 0.713 s into the walk, button up 8 ms later; egg 12052 `event 7 @ 05AA` 60 log lines after the load; all six barks; `endgameStarted` 0 to 1, `hasBag` 0; Avatar at (18432, 22784) exactly after the scene, then walked 200 units; processes 1406 and 422 alive | **PASS** |
| B | West off the pad to Ezrekal, bag, refill | bag 4865 with six q 25 stacks; split 12 off stack 15433: q 13 at 5.0 s, q 25 at about 25 s; ground stacks held at q 12 | **PASS** |
| C | Before `godsFree`, arrival plays nothing | cp34 (Map 18, `godsFree` 0): egg 16369 hatched on arrival and returned; no bark, no fade, no EGGENDGA process, `endgameStarted` 0; walked 200 units | **PASS** |
| D | Estate leaves `detection_tables.h` alone | entry `aae44805...`, 1505576 and mtime 22:05:26 identical before and after the estate and after the build ("already up to date") | **PASS** |
| E | Box overlap on Map 10 | the new box (x 18176..18688, y 22592..22976) meets only its own frame-1 pad; trigger 211's box starts 480 units south; no other scene or monster egg within 4000 units overlaps | **PASS** |
| R | Replay and round trip (added) | Map 10 to Map 18 and back after the scene: egg hatched both ways, no replay, no stasis; the top-up still refilled 13 to 25 | **PASS** |

## Method

Saves (48 files) and `scummvm.ini` were copied to the scratchpad first and
restored at the end. `godsfree-map18-2026-09-27.sav` (current map 18,
`godsFree` 1, `endgameStarted` 0, `hasBag` 0) was copied over `ultima8.001`
and loaded with `Ultima8Engine::loadGame 1`. That save holds Map 18 with the
pre-breach wall, so the way out was the same as on 09-27: a Tiny Tar at the
crack (x 2864, the clear span is x 2817..2879 by `build_map_18.py:401`), north
to (3076, 1624), then the exit trigger (Map 18 teleporter id 210 at
(3072, 1408), box y 1344..1535). The first potion wore off while the walker
thrashed along the wall, and a second one (8983) got through
(`A0-drink-tiny-tar-at-crack.png`).

Every crossing used one script: move the cursor, hold the right button,
poll the log every 10 ms for `Loading Fixed items in map N`, and release
within 10 ms of it. Then frames every 0.85 s with the console closed.

## A: arrival hatches the egg, PASS

Crossing: `load seen at 0.713 s, mouseup at 0.721 s`. In the log, 60 lines
after `Loading Fixed items in map 10` (the NPC slot updates and event 8s of
the map load): `Item: 12052 (shape 73) calling usecode event 7 @ 05AA:0080`.

Film (139 frames, 120 s), segmented by the red bark mask:

| Frames | Screen |
|---|---|
| 0 | Map 18, first draw after the switch (`A1-map18-before-crossing.png`) |
| 1-2 | opening fade |
| 3-16 | "With the Ancient Ones freed, their power flows through the land. The Vale begins to change." (`A2-endgame-bark1-on-arrival.png`) |
| 24-38 | "Green returns to the withered earth. Water flows where dust once lay. The vale is healing." |
| 45-59 | "The Zealans gather around me. Their faces show something I have not seen here before -- hope." |
| 62-82 | "An elder steps forward... They are thanking me. The Vale is restored." (`A2-endgame-bark4-elder.png`) |
| 86-102 | "And with the power of the Ancient Ones now restored, I feel the path to Britannia opening before me at last." (`A2-endgame-bark5-closing.png`) |
| 103-110 | "The Guardian's prison weakens. It is time to go home." (`A2-endgame-bark6-time-to-go-home.png`) |
| 114 | black (`A2-endgame-fade-black.png`) |
| 115 on | world (`A2-after-scene-world.png`) |

All six texts, zoomed: `A2-endgame-six-barks-zoom.png`. No bark mentions a
bag.

Reads after: Avatar at **(18432, 22784, 0)**, the DEST egg's own location
(`MainActor::teleport` places him on `egg->getLocation()`,
`main_actor.cpp:389-429`), so he took no step between arrival and the
end of the scene. `endgameStarted` **1**, `hasBag` **0**, `godsFree` 1;
`findShape 637` 2 (1754, 14387), `findShape 395` 0. `Kernel::listProcesses`:
process 1406 (`EGGENDGA`, item 12052, `05AA:04C0`) and process 422
(`05AA:04E6`, notify 1406), the hatch waiting on the top-up. A 1.2 s walk
west moved him from (18432, 22784) to (18232, 22784)
(`A3-walked-west-off-pad.png`).

**Negative control:** the scene created no bag and no reagent and left
`hasBag` 0.

## B: west off the pad to Ezrekal, PASS

Route: (18232, 22480), (17232, 22480), (17232, 14648), (14128, 14648),
(14128, 12672), into the stockade: the 09-27 bypass route, which never
crossed the old egg. Ezrekal wandered; the fourth standstill strike logged
`Item: 116 (shape 200) calling usecode event 1 @ 0474:031C` and showed
**I have freed your gods!**, **I would speak to you of Tyorvi.**, **bye**
(`B1-ezrekal-menu-after-endgame.png`). Clicking the first row: page 1 "What
a wonderful time this is! ... but", page 2 "this I can give you there is. A
magical bag it is. Provide you it will with any magical reagents you need.
Take it, with our heartfelt thanks!" (`B2-ezrekal-bag-bark-page1.png`,
`-page2.png`, `-zoom.png`).

Reads after: `hasBag` **1**; new bag **4865** (shape 637) at pack position
(0, 0); six shape-395 stacks, frames 0, 6, 8, 9, 10, 14, each **q 25**;
weight 330 to 490. Processes 1406 and 422 unchanged.

Double-clicking the bag logged `Item: 4865 (shape 637) calling usecode event
1 @ 027D:00A7` (`B3-bag-opened.png`). Dragging stack 15433 to the ground
brought up the slider (`B4-split-slider.png`), set to 12
(`B4-split-slider-set-12.png`); **OK** logged `SplitItemProcess splitting:
12: 13-12`.

| Split | Read after **OK** | Stack 15433 in the bag | Ground stack |
|---|---|---|---|
| 1 | 9.5 s | q 25 (already refilled) | 14732 q 12 |
| 2 | 5.0 s | q **13** | 2414 q 12 |
| 2 | about 25 s | q **25** (`B6-after-refill.png`) | 2414 q 12, 14732 q 12 |

The first read came too late to see the low value, so the split was
repeated with an immediate read. The ground stacks staying at 12 is the
`within container Avatar` scope holding.

## C: before `godsFree`, arrival plays nothing, PASS

`~/lv-checkpoints/cp34-altar-ready-head-20260926.sav` over `ultima8.001`:
Map 18 at (3400, 7696), `godsFree` 0, `endgameStarted` 0, `hasBag` 0,
`templeOpen` 1 (`C1-cp34-loaded.png`). The route stayed clear of the altar
egg (quality 296, box x 2880..3264, y 8128..8512); `godsFree` read 0 again
at (3060, 1604) before the crossing.

Crossing: `load seen at 0.697 s, mouseup at 0.702 s`; `Item: 16369 (shape
73) calling usecode event 7 @ 05AA:0080`. So the egg did hatch, and
`hatch()` returned at `if not godsFree`. Film, 46 frames over 40 s: frame 0
black (the first-draw lag after a map switch, traps.md 2026-09-25), frames
1-45 world with no bark and no fade (`C2-pre-altar-arrival-no-scene.png`,
`C2-pre-altar-arrival-35s.png`). Reads: Avatar at (18432, 22784),
`endgameStarted` **0**, `hasBag` 0, `godsFree` 0; `Kernel::listProcesses`
8 processes, **none** `EGGENDGA`; `findShape 637` 2, `findShape 395` 0. A
1.0 s walk west moved him 200 units (`C3-pre-altar-walked-west.png`).

## D: the estate leaves the detection entry alone, PASS

Before the estate: line 297 of `scummvm-lv/engines/ultima/detection_tables.h`
read `"aae44805b36691dd54bd6cc9ff6b0520", 1505576`, mtime 22:05:26.844. After
`tools/run_all_tests.sh` (31/31) and again after the full build (which
printed `detection_tables.h already up to date`) and after the session:
the same line, the same mtime.

The patch does not hollow the append test. `REPO_ROOT` is read at run time
only for the detection path (`build_eusecode.py:1015`); `BASE_FLX`,
`LV_FINAL`, and `LV_DEV` were bound from it at import (`:100-106`), so the
temp build still compiles the real sources, and the test still asserts
`MANIFEST: appended` and the one new pin.

## E: box overlap on Map 10, PASS

Read from the built `shared/build/FIXED.DAT` with `u8_map.MapArchive`. Map
10 has 9730 items, 1685 of them eggs (1664 glob, 10 monster, 8 teleport, 3
shape 73). Within 4000 units of the new egg:

| Egg | Location | Box | Overlaps the new box |
|---|---|---|---|
| EggEndgame q 299, 0x86 | (18432, 22784, 0) | x 18176..18688, y 22592..22976 | itself |
| teleport target id 210 (frame 1) | (18432, 22784, 0) | a point | yes, harmless: `TeleportEgg::hatch` returns for a non-teleporter |
| teleporter q 467 (id 211 to map 18), 0xd3 | (18432, 23552, 0) | x 18016..18848, y 23456..23648 | no, 480 units south |
| two monster eggs | (14592, 19200), (15104, 20224) | npcnum 1 | no |

Glob eggs are expanded at load and are not hatcher eggs. The other two shape
73 eggs on Map 10 are far away.

## R: replay and round trip, added, PASS

From Ezrekal back to (18440, 22468), then south across the box into trigger
211: `Item: 12052 (shape 73) calling usecode event 7 @ 05AA:0080`, then
`Loading Fixed items in map 18` 3.0 s into the same held walk. The replay
guard returned at once: the Avatar was never frozen and arrived at (3072,
1792). North again into the exit trigger: egg **10870** (a new object id,
the map was reloaded) hatched, 27 frames over 25 s showed no bark
(`R1-return-no-replay.png`), `endgameStarted` stayed 1.

`Kernel::listProcesses` then showed **only process 422** (the top-up, item
0); process 1406, the hatch that owned item 12052, was gone with the Map 10
unload. A third split (`R2-slider-after-round-trip.png`) read q 13 at 5.0 s
and q 25 at 27.9 s, so the top-up survives leaving the map. The two ground
stacks from test B were still there at q 12, and the new one at (18697,
22686) read q 12.

## Findings outside the plan

1. **The comments beside the egg name the two teleport eggs backwards.**
   `build_map_10.py:1388` heads the frame-1 target (`teleport_target`, id
   210, y 22784) "Teleport TRIGGER (ID 210) -> Map 18", and `:1400` heads the
   frame-0 teleporter (id 211 to map 18, y 23552) "Teleport DEST (ID 211)
   for returns from Map 18". The built map and `u8_map.py:109-146` say the
   opposite. The new EggEndgame comment calls y 22784 "DEST 210", which is
   right and contradicts the heading 20 lines above it. The 2026-07-31 swap
   note explains the history, but a future edit that trusts the headings
   would move the egg onto the trigger. Confidence high.
2. **Nothing in the estate pins the egg to the pad.** `test_uc_eggs.py`
   covers the class, not the placement; no map test asserts that
   EggEndgame's box contains the Map 10 target id 210. The 09-27 defect was
   a placement defect, and a check of that shape would have caught it. A
   possible check: read the built Map 10, find quality 299 and the frame-1
   id-210 egg, assert the target's point lies in the half-open box.
3. **The comment's "measured (18432, 22680)" is not the arrival point.**
   The engine lands the Avatar on the target's location, (18432, 22784),
   read three times this session. 22680 (and 09-27's 22480) are readings
   taken after a held walk carried on past the crossing. The conclusion (the
   box contains the arrival) holds either way.
4. **Reagent duplication is now shown in engine** (09-27 finding 5, then
   only read from the code). Three splits of 12 left three ground stacks
   of q 12 and the bag stack back at 25 each time: 36 reagents made from
   nothing in about a minute, and a player can pick them up and repeat.
5. **A save taken on Map 10 before this change keeps the old egg** until
   the player leaves Map 10 and returns (traps.md, "An old save does not
   see new fixed items"). Such a player can still walk around the old egg
   at (18432, 22016) and get a bag with no top-up. It affects development
   saves only.
6. **The hatch process dies with its egg on a map unload, the top-up does
   not.** Harmless as built, because the top-up is item 0 and loops on its
   own. It would matter if anything were ever made to wait on the hatch
   process after the player leaves Map 10.
7. **`map_pins.json` was not re-derived.** Its header reads
   `fixed_sha256_prefix: bf233644...` (2026-09-25), and its EggEndgame row
   still says (18432, 22016) npcnum 136. `derive_map_pins.py` run into the
   scratchpad against today's FIXED.DAT (`f92973ee...`) differs in three
   rows: EggEndgame now (18432, 22784) npcnum 134, and two Map 18 eggs from
   the previous commit (quality 305 npcnum 68 to 132 at (2864, 6240), and a
   new quality 306 at (3072, 4800) npcnum 136). No test compares the pins
   with the build, so the estate stays green. Confidence high.

## Harness anomalies

- **The 09-27 driver wrote a plate into the 09-27 folder.** Its default
  plate directory was 09-27's, and the first `shot()` ran without
  `LV_PLATES`, overwriting `docs/playtest-2026-09-27-bag-ezrekal/A0-drink-
  tiny-tar-at-crack.png`. There was no other copy. It now holds this
  session's plate of the same action (Tiny Tar at the crack, "Something
  strange is happening to me"), taken 2026-09-29 22:16; the same image is
  this report's `A0-drink-tiny-tar-at-crack.png`. The driver's default now
  points here.
- `Ultima8Engine::saveGame` with no argument opens the save chooser; a
  click on slot 1 and **OK** saved it.
- The goto walker thrashes inside a 24-unit tolerance and let the first
  Tiny Tar wear off against the wall; a direct north burst at x 2852..2864
  passes the crack.
- Ezrekal wanders; the fourth strike landed.

## Disk changes

- This report and `docs/playtest-2026-09-29-endgame-egg-pad/` (26 plates).
- `docs/playtest-2026-09-27-bag-ezrekal/A0-drink-tiny-tar-at-crack.png`
  replaced with a 2026-09-29 capture of the same action (above).
- `shared/build/` rewritten by `tools/build_artifacts.sh` with the canonical
  bytes (new mtimes); `ARTIFACTS.sha256` untouched.
- `shared/data/u8-install/` rewritten by `./install_lv.sh` (same hashes).
- `shared/u8-lv-patched/FIXED.DAT` and `STATIC/FIXED.DAT` synced by
  `session.sh start`.
- `scummvm-lv/engines/ultima/detection_tables.h` not modified (mtime
  22:05:26, before this session).
- `~/.local/share/scummvm/saves/` (48 files) and `~/.config/scummvm/scummvm.ini`
  restored from the copies taken first; `ultima8.001` md5 `083de199...`,
  `scummvm.ini` `a143fa3b...`, as before.
- Scratchpad: `v0929-tests.log`, `v0929-build.log`, `v0929-install.log`,
  `endgame-egg-pad-session.log`, frame folders `fA/`, `fB/`, `fC/`, `fR/`,
  `cross.py`, `go_until.py`, `map_pins.derived.json` (finding 7), the
  `drv.py` plate-directory edit, and one new
  checkpoint, `godsfree-at-exit-map18-2026-09-29.sav` (Map 18 at (3072,
  1624), `godsFree` 1, `endgameStarted` 0, 89 units south of the exit
  trigger).
- No source edited, nothing committed, `TODO.md` not edited. Session
  stopped (ScummVM and Xvfb killed).

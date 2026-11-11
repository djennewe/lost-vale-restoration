# Playtest 2026-10-25: npc 111 (890) back on Map 10

Rechecks phaseD finding F1 (`docs/playtest-2026-10-25-phaseD-verify.md`). In FIXED `995f4395`, npc 111 had no start record on Map 10. The map pin has been restored, and the build is now FIXED `9e666935`.

## Verdicts

| ID | Claim | Verdict |
|----|-------|---------|
| C1 | Old save → map hop → Map 10: 111 reads shape 890 at its record | **PASS.** Before the hop: `shape 708 (uc: CHILD), (19712, 6656, 0)`. After hopping Map 10 → 13 → 10: `shape 890, (19712, 6656, 0)`. The loader logged `LV: Slot 111 already has actor shape 708 … updating pos to (19712,6656,0)`. Controls: 104 708 → **889**, 107 707 → **888** |
| C2 | The record creates 111 when Map 10 loads fresh | **PASS (new game).** In a new game on Map 3, `objectInfo 111` gives `No such object: 111` and `findShape 890` finds 0. After entering Map 10 the log shows `LV: Created actor npc 111 shape 890 mapNum 10 at (19712,6656,0)`, `objectInfo 111` reads `shape 890, (19712, 6656, 0)`, and `findShape 890` finds 1. The suggested Map 11 save (`replay1011-s03c-m11-arrival.sav`) had already been on Map 10 (111 was 708 in it), so it exercises C1's update path again: 708 → 890 |
| — | 111 drawn on screen as the blond spear child | **PASS, using `Actor::hold`.** At its record spot the child stands behind a cliff from the default camera, and only its hair and spear tip show past the rock edge (C1-e, C2-c). `Actor::hold 111 128 -64` moved it onto open floor for the clear plates (C1-c/d, C2-d/e) |

Both C2 Map 10 entries were debug teleports (`Cheat::toggle` on, teleport, off), not walk-ins. No egg-triggered behaviour was under test, so the teleport doesn't weaken these claims.

## Build under test

Pinned copy in `/tmp/claude-1000/npc111/` (display :95). Hashes are in `pinned-start.sha256`, and every artifact matched `shared/build/ARTIFACTS.sha256`:

- FIXED.DAT, top level and `STATIC/`: `9e666935…`
- EUSECODE `2e3b71c2…`, U8SHAPES `f64cbfd8…`, TYPEFLAG `7faaaf23…`, ANIM `97ae5fc9…`
- binary: `scummvm-lv-console/scummvm` `d371f7ce…` (the text-console build)

The game was run with `--save-slot=1` or as a new game, using `py/lv.py` copied from the phaseD driver.

## C1: old save, map hop (PASS)

Save: `~/lv-checkpoints/replay1017-s18c-m10-reagent-bag-hp30.sav`. It was made before phase D, and on load the Avatar is on Map 10 at (12676,13263,0) with hp 30 (C1-a).

**Before the hop** (straight from the save):
```
Item 111 (class Actor, shape 708) (uc: CHILD), 1, (19712, 6656, 0) q: 0, m: 10, n: 111, f: 0x40, ef: 0x103 … flags: 0, activity: 0
Item 104 (class Actor, shape 708) (uc: CHILD), 0, (5376, 7424, 0) …
Item 107 (class Actor, shape 707) (uc: PESANT1), 19, (19231, 6943, 0) …
```

**The hop:**
- `MainActor::teleport 13 4479 1791 120`. The log shows `Unloading map 10` → `Loading Fixed items in map 13`.
- On Map 13, 111 still read 708 (as expected: actors live in the save until a Map 10 load).
- `MainActor::teleport 10 19800 6800 0`. The log shows `Unloading map 13` → `Loading Fixed items in map 10`, and then:
```
LV: Slot 104 already has actor shape 708 mapNum 10 — updating pos to (5376,7424,0)
LV: Slot 107 already has actor shape 707 mapNum 10 — updating pos to (19231,6943,0)
LV: Slot 111 already has actor shape 708 mapNum 10 — updating pos to (19712,6656,0)
```
(This line prints the shape held *before* the loader's `setShape`, at `map.cpp:271-273`.)

**After the hop:**
```
Item 111 (class Actor, shape 890), 1, (19712, 6656, 0) q: 0, m: 10, n: 111, f: 0x2040, ef: 0x103 … ac: 0 … flags: 0, activity: 0
findShape 890: 1 found
Item 104 (class Actor, shape 889), 0, (5376, 7424, 0) …           findShape 889: 1 found
Item 107 (class Actor, shape 888), 30, (19283, 6995, 8) …          findShape 888: 1 found
```
- 111 sits exactly on its record.
- 107 had already walked off its record, which is normal: Atli loiters.

**Plates:**
- C1-b: just after the hop. Both the Avatar (19800,6800) and 111 are hidden behind the rock band, so the frame shows neither.
- C1-c/C1-d (`Actor::hold 111 128 -64`, moving it to (20008,6656,0)): the small blond child with a spear, next to the Avatar on open floor.
- C1-e: with 111 held back onto its record (19712,6656,0), its blond hair and spear tip show past the cliff edge, NW of the Avatar.
- C1-f/C1-g: the controls, both held into view. Atli 888 is the white-haired robed elder with a staff, and child 104 889 is the dark-haired spear child.

## C2: fresh map load (PASS, new game)

**New game** (no save; started with the session's intro skip and name entry). It comes up on Map 3 inside Devon's opening conversation (C2-a):
```
Item 1 (class MainActor, shape 1), 5, (14527, 5887, 8) … m: 3 …
No such object: 111
No such object: 104
No such object: 107
findShape 890: 0 found
```

`MainActor::teleport 10 19880 6720 0` gave:
```
Unloading map 3
Loading Fixed items in map 10
LV: Created actor npc 104 shape 889 mapNum 10 at (5376,7424,0)
LV: Created actor npc 107 shape 888 mapNum 10 at (19231,6943,0)
LV: Created actor npc 111 shape 890 mapNum 10 at (19712,6656,0)
```
- All 17 slots 100-116 were created, one line each.
- The engine then hopped to map 0 and back to 10 by itself (H1). The second load printed `Slot 111 already has actor shape 890`.

Afterwards:
```
Item 111 (class Actor, shape 890), 1, (19712, 6656, 0) q: 0, m: 10, n: 111, f: 0x2040, ef: 0x103 … activity: 0
findShape 890: 1 found
Item 104 (class Actor, shape 889), 0, (5376, 7424, 0) …    findShape 889: 1 found
Item 107 (class Actor, shape 888), 15, (19551, 6895, 0) …  findShape 888: 1 found
```

**Plates:**
- C2-b/C2-c: arrival, with the child's hair and spear past the cliff edge at its record.
- C2-d/C2-e: `Actor::hold 111 128 -64`, the child on open floor.

**The Map 11 save** `~/lv-checkpoints/replay1011-s03c-m11-arrival.sav` (the suggested `replay1017-s03c*` doesn't exist):
- On load the Avatar is on Map 11 at (9728,2664,0). The save already holds 111 as `shape 708 (uc: CHILD), (19712, 6656, 0)`, 104 as 708 and 107 as 707, so this save had been on Map 10 before.
- After `MainActor::teleport 10 19880 6720 0`: 111 → `shape 890, (19712, 6656, 0)`, 104 → 889, 107 → 888 (at (18931,7171,0), loitering). Plate C2-f.
- This repeats C1 from another map and another save. It isn't a never-visited save.

## Findings not in the plan

**N1. 111's record spot is hidden behind a cliff from the default camera.**
- At (19712,6656,0), only the child's hair and spear tip show past the rock edge, from both (19880,6720) and (19800,6800).
- An Avatar teleported to (19800,6800) is fully hidden by the same rock (C1-b).
- A player will barely see the child unless they come round the rock. Whether (19712,6656) is open floor or inside the cliff's footprint was not checked `[INFERENCE: probably the spot screen19's 1994 framing shows; not compared]`.

**N2. 111 stood still** (`activity: 0`) on every read, as the retail 708 CHILD did in phaseD. That matches phaseD's note on 104.

**N3. The `uc:` tag changed.** Under 708, objectInfo printed `(uc: CHILD)`. Under 890 it prints no `uc:` tag. The same is true of 104 under 889 and 107 under 888. Talking to 111 was not tested.

## Harness anomalies

- **H1.** In the new-game run, the debug teleport out of Devon's opening conversation was followed by an engine-driven `Unloading map 10` → `Loading Fixed items in map 0` → back to `map 10`. Two `I_resetRef item=25662` lines and three `Non-existent process PID (0) in implies` came with it (phaseD F7 saw the same warning in a new game). Most likely the Map 3 start script was still running `[INFERENCE]`. It did not affect the result: 111 was created on the first load and kept on the second.
- **H2.** `Actor::hold`'s reply gives `px=` from before the move, so it is stale. Placement was judged from the plate, not from that field.
- **H3.** One eval cell timed out on a 30 s wrapper limit mid-probe. The probe was re-run.

Log hygiene, across `lv_C1.log`, `lv_C2new.log` and `lv_C2s03c.log`: 0 `stuck in process loop`, 0 Segmentation, 0 Assertion, 0 `Unhandled intrinsic`, 0 ERROR, 0 `Cycle in paint`. The only warnings were the 3 `Non-existent process PID (0) in implies`, all in the new-game log (H1).

## Console commands used

- **Reads:** `ObjectManager::objectInfo` (1, 104, 107, 111) and `ObjectManager::findShape` (888, 889, 890).
- **`Cheat::toggle`:** on and off around each teleport, each time verified by the echoed `Cheats = true/false`.
- **`MainActor::teleport`:**
  - 13 (4479,1791,120)
  - 10 (19800,6800,0)
  - 10 (19880,6720,0) ×2
- **`Actor::hold`:**
  - 111 with (96,96), (128,−64), (−168,−64): the last put it back on its record
  - 104 (128,−64)
  - 107 (−32,−160)
- **Not used:** heal, invincibility, item cheats, `setGlobal`, `saveGame`, `loadGame` (reloads were restarts with `--save-slot`).

## Disk changes

- **Wrote:** this report and `docs/playtest-2026-10-25-npc111-check/` (13 plates).
- **Scratch only, in `/tmp/claude-1000/npc111/`:** game, binary and engine-data copies with `pinned-start.sha256`, `py/lv.py`, the three logs, and `sp/` raw captures. `saves/ultima8.001` was overwritten by checkpoint copies.
- **Not changed:** `~/lv-checkpoints`, `shared/`, source, TODO and HANDOFF.
- ScummVM and Xvfb :95 are stopped.

# Phase E, slice pillars11: screen07 and the four pillars (2026-10-30)

Branch `wt/pillars11`, worktree `lv-wt-pillars11`. This covers Douglas's
review cards 3 and 4. The builds went into the worktree's own
`shared/build` (`tools/build_artifacts.sh --record`). EUSECODE did not change
(`b47c324c…`), so the detection md5 stays the same.

Contact sheet: `phaseE-pillars11-contact.png`.
- Top row: 1994 | phase-D build | this build (the built window with the
  Avatar painted, x3).
- Bottom row: the four 865 frames, then the three AI-drawn frames they
  replace.

## Scores (screen07)

| | built window `--actors` | replay `--built` | in-engine class |
|---|---|---|---|
| phase D (main `ac193c0`) | 91.20 | 86.63 | 89.93 (SCORES-2026-10-25) |
| this build (FIXED `42bd676e`) | **97.28** | 86.67 | **94.92** |

- **The in-engine capture.** It is `screen07_ingame.png` beside this file.
  - It was taken with `vignette_capture.py` on a pinned copy of main's
    `u8-lv-patched` (`/tmp/claude-1000/pillars11/game`), which this build's
    artifacts were synced into.
  - The binary was `scummvm-lv-console/scummvm`, on display :97.
  - It ran from a private copy of `session.sh` whose `stop` kills only its
    own `tail`.
- **The in-engine number is 2.4 points under the built one.** Two
  differences between the capture and the built window account for all of
  it:
  - The Avatar keeps his start facing (about 700 px).
  - A transient: a dark monster drifted over the back wall above the
    pillar during the capture (about 600 px at (170-200, 5-70)).
  - Neither is map content.
- **screen05 is unchanged**: built 94.55, in-engine 86.82.
- **The replay barely moves.** It paints the vignette's retail pieces, not
  the built ones (as in phase D).
- **Test floor.** `test_vignettes`' floor for screen07 is raised from 91.20
  to 97.27.

## What the 8.8% left after phase D was

I decomposed the built window's 5,238 missed pixels by the item that owns
each one:

| residual | px | fix |
|---|---|---|
| floor showing above the right cliff where 1994 is black (the notch north of the rock band) | 553 | three mask cells became rock (`SCREEN07_MASK` rows 160-162). The Earth socket keeps its north and east sides open |
| the right cliff's front course stops short of the frame edge | 210 | a retail 26 f2 at (8191,21503,0) (`SCREEN07_STANDINS`). It was the best of every 26-32 frame at x 8191-8319, y 21375-21631 |
| the spears in the cliffs, the right cliff's course seam, the back wall's pointed east end | ~1,640 | **891**, see below |
| the lava pit round the pillar's foot (its glow and lip), the floor bits | ~1,350 | **892**, see below |
| the pillar's left flame and the lava by the candle post, which the phase-D cut stopped short of | 41 + 24 | added to 2023 from the shot |
| remaining: spears on the 32/27/29 pieces (left and back-left walls), the black caps at z 96, 125's floor bits at the bottom, the mouse pointer, the status text, the Avatar's pose | ~1,620 | see "Left" |

Searches that found nothing to gain:
- moving the right cliff's courses together or singly (every frame, x/y
  ±64, z −48..+24);
- stacking an upper course;
- moving the back row over the front;
- every 26-32/98-112/125/564/334/393/138 frame, template-matched over the
  misses and then placed in the rock cells.

The seam and the spears are 1994 art on retail-shaped pieces, not a
placement problem.

## New art

- **891 (registry 2043, 8 frames)**: the screen07 cave walls (26 family).
  - Each frame is one window piece's retail 26 frame with the shot's
    pixels the piece owns laid over it: the spears, the course seam, and
    the back wall's tip (pixels the black void tile owned, given to the
    nearest wall).
  - It is a `patch` row, a new `lv_art_props` row kind: the PNG holds only
    the shot's pixels and the composition happens at build time, so no
    Origin pixel is committed.
  - It uses donor 26 and 26's footpad, so every piece sorts and collides as
    before.
  - `build_map_11.screen07_faces` swaps each piece for its frame by its
    exact (shape, frame, position) and asserts that each piece is found
    once.
- **892 (registry 2027, 17 frames)**: the floor tiles round the pillar, on
  the same patch method with donor 301 and footpad (4,4,0).
- **865 frame 2 (registry 2023)**: +41 flame/lava pixels from the shot, and
  24 pixels re-cut (the candle post's outline down column 30).
  - Its 88 index-9 greys became 28, the same colour outside the cycling
    range.
  - Its `inferred_px` list is recomputed in frame coordinates. Phase D's
    list had x −121..−112, which is not a frame coordinate.
- **`tools/art/screen07_cuts.py`** regenerates all of the above from the
  map. It is deterministic; rerun it after any change to Map 11's screen07
  window.

All of these frames are single-use and need Douglas's sign-off. The
patches draw exactly what the shot shows, so a spear or the pit lip looks
painted onto the rock or floor wherever that piece is seen. The camera
angle never changes, so the piece looks the same from every position.

## Card 4: the Earth, Air and Water pillars

Registry entries 2024-2026 hold the new art, made by
`tools/art/pillar_1994_style.py`, with grade `derived` (a new grade, added
to the registry `_doc`).

- **What each frame is.** It is 2023's column pixel for pixel, on 2023's
  46x106 canvas with hotspot (18,104), so the footprint (2,2,10), height
  and anchor are frame 2's. The shaft's lower-left, which screen07 hides,
  is drawn from the rows above.
- **The recolouring.** The red gem, the flames and the lava are recoloured
  by luminance onto one ramp per element:
  - Earth: ochre 163-173, a brown stone cap, flying earth, a heap at the
    foot.
  - Air: pale greys 240-249, a white cap, wisps, a dust swirl.
  - Water: blues 136-155, a blue cap, spray, a pool.
- **Mottling.** The column's rust mottling goes grey for Air and slate for
  Water.
- **No cycling indices.** No pixel uses indices 1-14, and the script
  asserts it.
- **Placement.** The pillars stand on Map 11 where they stood (865 f0
  (7680,20480), f1 (8704,20480), f2 (7680,21504), f3 (8704,21504); the
  receptacles are untouched). In-engine plates:
  - `ingame_plate_all4.png`: all four in the chamber; Earth's top is cut by
    the viewport.
  - `ingame_plate_fire.png`: Fire and Water.
  - Both drew with no sort glitch.
- **Puzzle.** `ELMCOLMN.UNK`/`COLPUZZL` were not touched, and
  `TYPE_SHAPES['TypeElementalColumn']` is still 865. `test_art_props`
  (the receptacle search boxes, the pillar TYPEFLAG) is green, as are the
  usecode simulation tests in the estate.
- **Not run:** no receptacle was used in-engine.

## Tests (worktree build)

`tools/run_all_tests.sh`: 52 of 54 files passed on the first run.
- `test_map_pins_fresh` failed on the FIXED hash, as any rebuild does.
  `map_pins.json` has been regenerated, and the test now passes 3/3.
- `test_integration_state` fails on the install target, which is main's
  `u8-install`; the parent's `tools/integrate.sh` updates it.

`test_art_props` (484 passed) gained:
- a `patch`-row check: each frame equals its patch over its retail base;
- a frame-0 anchor check for indexed entries in drawn rows;
- a check that all four pillars share frame 2's canvas and anchor.

`test_vignettes`: 39 passed.

## Left, and for Douglas

1. **Sign-off on 891/892, 2023's additions and the three redrawn
   pillars.** Earth's flare is brown flame shapes, which may read as fire
   rather than earth. If it does, redraw the flare and keep the column.
2. **Spears on the left and back-left walls (~500 px).** They sit on
   32/27/29 pieces, which have other footprints, so they would need more
   shape IDs. 891 placed FLIPPED would take 32's box, but the engine draws
   a mirrored sprite 1 px right of where `vignette_paint` puts it
   (`render_surface.cpp` paintLogic: `right = x + xoff + 1`; the painter
   uses the sorter's `x + xoff - width`). I stopped there, and the offline
   painter still carries that 1-px difference for every flipped sprite.
3. **The capture tool cannot face the Avatar** (no console command for
   it), so the shot's pose costs about 1.2 points in-engine on every shot
   with an Avatar.
4. **Integration.** U8SHAPES, TYPEFLAG and FIXED changed. Run
   `tools/integrate.sh --record` after merging.
